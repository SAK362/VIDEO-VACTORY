#!/usr/bin/env python3
"""Render video FIKSI (gambar adegan + voice + subtitle) dengan numpy + Pillow + ffmpeg.

Pakai:
  python fiksi/render_fiksi.py fiksi/topik01 --out hasil/            # video penuh + thumbnail + narasi
  python fiksi/render_fiksi.py fiksi/topik01 --stills hasil/         # hanya beberapa frame contoh (cek visual)

Folder proyek berisi:
  spec.json            naskah, emosi, gambar tiap adegan
  voice/*.wav          suara (nama di spec["audio"])
  img/*.png            gambar adegan
  heard.json           (opsional) waktu kata dari Whisper; tanpa ini waktu diperkirakan
Env: FIKSI_W, FIKSI_H, FIKSI_FPS (default 1080, 1920, 30).
"""
import argparse
import difflib
import json
import math
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W = int(os.environ.get("FIKSI_W", 1080))
H = int(os.environ.get("FIKSI_H", 1920))
FPS = int(os.environ.get("FIKSI_FPS", 30))
HOLD = 1.0      # detik tahan setelah suara selesai
XFADE = 0.40    # lama transisi antar adegan (detik)
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_BOLD = os.path.join(os.path.dirname(HERE), "DejaVuSans-Bold.ttf")

# Preset per emosi: zoom awal/akhir, geser (-1..1 dari ruang geser), getar (px), warna, saturasi, terang, vignette
PRESET = {
    "netral":       dict(z0=1.00, z1=1.08, p0=(0.0, 0.0),   p1=(0.0, 0.0),   shake=0.0, tone=(1.00, 1.00, 1.00), sat=1.00, bright=1.00, vig=0.15, flash=0.0, punch=0.0, flicker=0.0),
    "berpikir":     dict(z0=1.00, z1=1.10, p0=(-0.3, 0.0),  p1=(0.3, 0.0),   shake=0.0, tone=(1.00, 1.00, 1.00), sat=1.00, bright=1.00, vig=0.20, flash=0.0, punch=0.0, flicker=0.0),
    "takut ringan": dict(z0=1.06, z1=1.16, p0=(0.0, 0.2),   p1=(0.0, -0.2),  shake=1.2, tone=(0.93, 0.98, 1.08), sat=0.90, bright=0.96, vig=0.35, flash=0.0, punch=0.0, flicker=0.0),
    "takut":        dict(z0=1.08, z1=1.22, p0=(0.0, 0.3),   p1=(0.0, -0.3),  shake=3.0, tone=(0.90, 0.97, 1.12), sat=0.82, bright=0.94, vig=0.50, flash=0.0, punch=0.0, flicker=0.07),
    "kaget":        dict(z0=1.05, z1=1.14, p0=(0.0, 0.0),   p1=(0.0, 0.0),   shake=4.0, tone=(0.96, 0.98, 1.06), sat=0.92, bright=0.98, vig=0.40, flash=0.55, punch=0.10, flicker=0.0),
    "sedih":        dict(z0=1.12, z1=1.00, p0=(0.0, -0.3),  p1=(0.0, 0.3),   shake=0.0, tone=(0.96, 0.99, 1.06), sat=0.72, bright=0.94, vig=0.35, flash=0.0, punch=0.0, flicker=0.0),
    "hangat":       dict(z0=1.10, z1=1.00, p0=(0.0, 0.0),   p1=(0.0, 0.0),   shake=0.0, tone=(1.06, 1.02, 0.92), sat=1.05, bright=1.05, vig=0.12, flash=0.0, punch=0.0, flicker=0.0),
}


def clamp(x, a, b):
    return a if x < a else b if x > b else x


def smooth(x):
    x = clamp(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- waktu

def norm(w):
    return re.sub(r"[^0-9a-z]+", "", w.lower())


def script_words(spec):
    out = []
    for si, sc in enumerate(spec["scenes"]):
        for w in sc["text"].split():
            out.append({"scene": si, "w": w, "n": norm(w)})
    return [x for x in out if x["n"]]


def audio_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def estimate_times(words, dur):
    """Perkiraan waktu kata tanpa Whisper: proporsional panjang huruf + jeda tanda baca."""
    lead, tail = 0.30, 0.35
    span = max(1.0, dur - lead - tail)
    weights = []
    for x in words:
        wt = len(x["n"]) + 2.0
        if x["w"].endswith((".", "?", "!")):
            wt += 9
        elif x["w"].endswith(","):
            wt += 4
        weights.append(wt)
    total = sum(weights)
    t = lead
    res = []
    for wt in weights:
        d = span * wt / total
        res.append((t, t + d * 0.8))
        t += d
    return res


def whisper_times(words, heard):
    """Cocokkan kata naskah ke kata Whisper; kata yang tak cocok diinterpolasi."""
    a = [x["n"] for x in words]
    b = [norm(h["w"]) for h in heard]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    times = [None] * len(a)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal" or (tag == "replace" and (i2 - i1) == (j2 - j1)):
            for k in range(i2 - i1):
                times[i1 + k] = (heard[j1 + k]["s"], heard[j1 + k]["e"])
    known = [i for i, t in enumerate(times) if t]
    if not known:
        return None
    ratio = len(known) / len(a)
    for i in range(len(a)):
        if times[i]:
            continue
        lo = max([k for k in known if k < i], default=None)
        hi = min([k for k in known if k > i], default=None)
        if lo is not None and hi is not None:
            f = (i - lo) / (hi - lo)
            s = times[lo][1] + (times[hi][0] - times[lo][1]) * f
            times[i] = (s, s + 0.25)
        elif lo is not None:
            s = times[lo][1] + 0.3 * (i - lo)
            times[i] = (s, s + 0.25)
        else:
            s = max(0.0, times[hi][0] - 0.3 * (hi - i))
            times[i] = (s, s + 0.25)
    return times, ratio


def build_timing(spec, proj, dur):
    words = script_words(spec)
    heard_path = os.path.join(proj, "heard.json")
    mode = "perkiraan"
    times = None
    if os.path.exists(heard_path):
        heard = json.load(open(heard_path))
        heard = heard["words"] if isinstance(heard, dict) else heard
        heard = [{"w": h[0], "s": h[1], "e": h[2]} if isinstance(h, list) else h for h in heard]
        r = whisper_times(words, heard)
        if r and r[1] >= 0.6:
            times, ratio = r
            mode = "whisper (%.0f%% kata cocok)" % (ratio * 100)
        else:
            print("PERINGATAN: heard.json kurang cocok dengan naskah, pakai perkiraan", file=sys.stderr)
    if times is None:
        times = estimate_times(words, dur)
    first = {}
    for x, t in zip(words, times):
        first.setdefault(x["scene"], t[0])
    n = len(spec["scenes"])
    starts = [0.0]
    for i in range(1, n):
        starts.append(max(starts[-1] + 1.0, first.get(i, starts[-1] + 5.0) - 0.25))
    return words, times, starts, mode


# ---------------------------------------------------------------- subtitle

def ass_time(t):
    t = max(0.0, t)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return "%d:%02d:%05.2f" % (h, m, s)


def make_chunks(words, times):
    chunks, cur = [], []
    for x, t in zip(words, times):
        cur.append((x, t))
        bare = x["w"].rstrip('"”’\'')
        end = bare.endswith((".", "?", "!"))
        comma = bare.endswith(",")
        if len(cur) >= 5 or end or (comma and len(cur) >= 3):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def write_ass(path, words, times, total):
    chunks = make_chunks(words, times)
    lines = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 0", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Default,DejaVu Sans,68,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,7,2,2,90,90,470,1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for i, ch in enumerate(chunks):
        s = ch[0][1][0] - 0.04
        e_last = ch[-1][1][1]
        nxt = chunks[i + 1][0][1][0] - 0.03 if i + 1 < len(chunks) else total
        e = min(max(e_last + 0.30, s + 0.6), nxt)
        text = " ".join(x["w"] for x, _ in ch).replace("{", "(").replace("}", ")")
        lines.append("Dialogue: 0,%s,%s,Default,,0,0,0,,{\\fad(70,50)}%s" % (ass_time(s), ass_time(e), text))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return len(chunks)


# ---------------------------------------------------------------- frame

class Scene:
    def __init__(self, sc, proj, start, end):
        self.emotion = sc.get("emotion", "netral")
        self.p = PRESET.get(self.emotion, PRESET["netral"])
        self.start, self.end = start, end
        self.dur = max(0.5, end - start)
        im = Image.open(os.path.join(proj, sc["img"])).convert("RGB")
        self.im = im
        self.sw, self.sh = im.size
        self.s0 = max(W / self.sw, H / self.sh)

    def render(self, t):
        """Frame float32 (H, W, 3) 0..255 pada waktu global t."""
        p = self.p
        lt = t - self.start
        u = clamp(lt / self.dur, 0.0, 1.0)
        ltc = max(0.0, lt)
        z = p["z0"] + (p["z1"] - p["z0"]) * u
        if p["punch"]:
            z += p["punch"] * math.exp(-ltc / 0.25)
        s = self.s0 * z
        vw, vh = W / s, H / s
        slack_x = max(0.0, (self.sw - vw) / 2)
        slack_y = max(0.0, (self.sh - vh) / 2)
        px = p["p0"][0] + (p["p1"][0] - p["p0"][0]) * u
        py = p["p0"][1] + (p["p1"][1] - p["p0"][1]) * u
        cx = self.sw / 2 + px * slack_x
        cy = self.sh / 2 + py * slack_y
        if p["shake"]:
            amp = p["shake"] * (math.exp(-ltc / 0.7) if p["flash"] else 1.0)
            cx += amp * (math.sin(ltc * 13.1) + 0.6 * math.sin(ltc * 27.7 + 1.0)) / s
            cy += amp * (math.sin(ltc * 11.3 + 2.0) + 0.6 * math.sin(ltc * 23.9)) / s
        cx = clamp(cx, vw / 2, self.sw - vw / 2) if vw < self.sw else self.sw / 2
        cy = clamp(cy, vh / 2, self.sh - vh / 2) if vh < self.sh else self.sh / 2
        coef = (1 / s, 0, cx - W / (2 * s), 0, 1 / s, cy - H / (2 * s))
        img = self.im.transform((W, H), Image.AFFINE, coef, resample=Image.BICUBIC)
        arr = np.asarray(img, dtype=np.float32)
        if p["sat"] != 1.0:
            gray = (arr[..., 0] * 0.299 + arr[..., 1] * 0.587 + arr[..., 2] * 0.114)[..., None]
            arr = gray + (arr - gray) * p["sat"]
        bright = p["bright"]
        if p["flicker"]:
            bright *= 1.0 - p["flicker"] * max(0.0, math.sin(ltc * 17.0) * math.sin(ltc * 5.3 + 1.0))
        mul = np.array(p["tone"], dtype=np.float32) * bright
        arr = arr * mul
        arr = arr * vignette(p["vig"])
        if p["flash"]:
            a = p["flash"] * math.exp(-ltc / 0.10)
            if a > 0.01:
                arr = arr * (1 - a) + 255.0 * a
        return arr


_VIG = {}


def vignette(strength):
    if strength not in _VIG:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 1.414
        _VIG[strength] = (1.0 - strength * (r ** 2))[..., None].astype(np.float32)
    return _VIG[strength]


def frame_at(scenes, t, total):
    n = len(scenes)
    idx = n - 1
    for i in range(n):
        if t < scenes[i].end:
            idx = i
            break
    a = scenes[idx].render(t)
    half = XFADE / 2
    if idx + 1 < n and t > scenes[idx].end - half:
        k = smooth((t - (scenes[idx].end - half)) / XFADE)
        a = a * (1 - k) + scenes[idx + 1].render(t) * k
    elif idx > 0 and t < scenes[idx].start + half:
        k = smooth((t - (scenes[idx].start - half)) / XFADE)
        a = scenes[idx - 1].render(t) * (1 - k) + a * k
    if t < 0.5:
        a = a * smooth(t / 0.5)
    if t > total - 0.9:
        a = a * smooth((total - t) / 0.9)
    return np.clip(a, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- keluaran

def make_thumbnail(spec, proj, path):
    im = Image.open(os.path.join(proj, spec["cover"])).convert("RGB")
    s = max(1080 / im.width, 1920 / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    l, t = (im.width - 1080) // 2, (im.height - 1920) // 2
    im = im.crop((l, t, l + 1080, t + 1920))
    over = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    for y in range(0, 760):
        d.line([(0, y), (1080, y)], fill=(0, 0, 0, int(215 * (1 - y / 760) ** 1.5)))
    im = Image.alpha_composite(im.convert("RGBA"), over)
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT_BOLD, 118)
    words = spec["judul"].upper().split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if d.textlength(test, font=font) > 940 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    lines.append(cur)
    y = 150
    for ln in lines:
        x = (1080 - d.textlength(ln, font=font)) / 2
        d.text((x, y), ln, font=font, fill=(255, 255, 255), stroke_width=8, stroke_fill=(0, 0, 0))
        y += 140
    im.convert("RGB").save(path)


def build_scenes(spec, proj, starts, total):
    scenes = []
    for i, sc in enumerate(spec["scenes"]):
        end = starts[i + 1] if i + 1 < len(starts) else total
        scenes.append(Scene(sc, proj, starts[i], end))
    return scenes


def slug(s):
    return re.sub(r"[^A-Z0-9]+", "_", s.upper()).strip("_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proj")
    ap.add_argument("--out", default="hasil")
    ap.add_argument("--stills", default="")
    ap.add_argument("--musik", default="")
    a = ap.parse_args()
    proj = a.proj
    spec = json.load(open(os.path.join(proj, "spec.json"), encoding="utf-8"))
    audio = os.path.join(proj, spec["audio"])
    dur = audio_duration(audio)
    total = dur + HOLD
    words, times, starts, mode = build_timing(spec, proj, dur)
    print("Audio %.1f dtk | waktu: %s | %dx%d @%dfps" % (dur, mode, W, H, FPS))
    for i, st in enumerate(starts):
        print("  adegan %02d  mulai %6.2f  [%s]" % (i + 1, st, spec["scenes"][i].get("emotion")))
    scenes = build_scenes(spec, proj, starts, total)

    if a.stills:
        os.makedirs(a.stills, exist_ok=True)
        for i, sc in enumerate(scenes):
            t = sc.start + min(1.0, sc.dur * 0.4)
            Image.fromarray(frame_at(scenes, t, total)).save(os.path.join(a.stills, "adegan_%02d.png" % (i + 1)))
        print("frame contoh ->", a.stills)
        return

    os.makedirs(a.out, exist_ok=True)
    base = "%s_%s" % (spec["nomor"], slug(spec["judul"]))
    ass = os.path.join(a.out, base + ".ass")
    nch = write_ass(ass, words, times, total)
    print("subtitle: %d potongan" % nch)
    mp4 = os.path.join(a.out, base + ".mp4")
    fontsdir = os.path.dirname(FONT_BOLD)
    vf = "ass=%s:fontsdir=%s" % (os.path.abspath(ass).replace("\\", "/").replace(":", "\\:"), fontsdir.replace(":", "\\:"))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-", "-i", audio]
    af = "apad,afade=t=out:st=%.2f:d=0.9" % (total - 0.9)
    if a.musik and os.path.exists(a.musik):
        cmd += ["-stream_loop", "-1", "-i", a.musik]
        fc = "[1:a]apad[v];[2:a]volume=0.10[m];[v][m]amix=inputs=2:duration=first:normalize=0,afade=t=out:st=%.2f:d=0.9[aout]" % (total - 0.9)
        cmd += ["-filter_complex", fc, "-map", "0:v", "-map", "[aout]"]
    else:
        cmd += ["-af", af, "-map", "0:v", "-map", "1:a"]
    cmd += ["-vf", vf, "-t", "%.2f" % total, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", mp4]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nframes = int(total * FPS)
    for n in range(nframes):
        proc.stdin.write(frame_at(scenes, n / FPS, total).tobytes())
        if n % (FPS * 10) == 0:
            print("  frame %d/%d" % (n, nframes), flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg gagal")
    make_thumbnail(spec, proj, os.path.join(a.out, base + "_thumbnail.png"))
    with open(os.path.join(a.out, base + "_narasi.txt"), "w", encoding="utf-8") as f:
        f.write("%s\n\n%s\n\n%s\n\n---\n%s\n" % (spec["judul"], spec.get("deskripsi", ""), spec.get("hashtag", ""),
                                                   "\n\n".join(s["text"] for s in spec["scenes"])))
    print("selesai:", mp4, "%.1f MB" % (os.path.getsize(mp4) / 1e6))


if __name__ == "__main__":
    main()
