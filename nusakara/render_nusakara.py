"""NUSAKARA: render 1080x1920@30 (Pillow + ffmpeg), tanpa Chrome.
  python nusakara/render_nusakara.py meta                 -> jumlah frame
  python nusakara/render_nusakara.py chunk i n OUT.mp4    -> render potongan ke-i dari n (video saja)
  python nusakara/render_nusakara.py still T [T...]       -> frame uji ke stills/f_T.jpg (T = detik)
Masukan: work/props.json (spec adegan) + nusakara/timing.js (dari webgl/make_timing.py, TIMING_OUT=nusakara/timing.js).
Zona aman (semua platform): atas 220, bawah 480, kanan 180, kiri 50 px. Panggung aksi y 480-1200."""
import json, math, os, re, subprocess, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import Pen, layer, W, H, INK, mix
import lib_char as C
import lib_props as P

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
PROPS = os.environ.get("PROPS_FILE", "work/props.json")
SPOS = {"kiri": 250, "tengah": 440, "kanan": 620, "bawah": 330, "atas": 600}
CAM = {"tutup": 1.32, "sedang": 1.14, "lebar": 1.0}
TEAL = (31, 122, 99); MINT = (150, 226, 196)


def load():
    props = json.load(open(PROPS, encoding="utf-8"))
    t = json.loads(re.search(r"=(.*);\s*$", open(os.path.join(HERE, "timing.js"), encoding="utf-8").read(), re.S).group(1))
    return props, t


def total_frames(t): return int(round((t["dur"] + 0.8) * FPS))


class Show:
    def __init__(s):
        s.props, s.T = load(); s.sc = s.props["scenes"]; s.spans = s.T["sent_spans"]; s.words = s.T["words"]; s.mouth = s.T["mouth"]
        n = len(s.sc); s.t0 = [0.0] + [max(0.0, s.spans[i][0] - 0.06) for i in range(1, n)]; s.t1 = s.t0[1:] + [s.T["dur"] + 0.9]
        s.bgc = {}; s.heading = []; h = ""
        for sc in s.sc:
            h = sc.get("judul") or h; s.heading.append(h)
        s.label = s.props.get("label_judul", "CERITA RAKYAT")
        s.warned = set(); s.phr = [s.phrases(i) for i in range(n)]

    def scene_at(s, T):
        for i in range(len(s.sc)):
            if T < s.t1[i]: return i
        return len(s.sc) - 1

    def phrases(s, si):
        ws = [w for w in s.words if w["si"] == si]; out = []; cur = []
        for w in ws:
            cur.append(w)
            if (len(cur) >= 6) or (len(cur) >= 2 and re.search(r"[,.!?;:]$", w["w"])) :
                out.append(cur); cur = []
        if cur:
            if out and len(cur) == 1: out[-1] += cur
            else: out.append(cur)
        return out

    def warn(s, kind, k):
        if (kind, k) not in s.warned: s.warned.add((kind, k)); print("WARN %s tak dikenal: %s" % (kind, k), flush=True)

    # ---------- kamera ----------
    def camera(s, sc, tl, dur):
        z0 = CAM.get(sc.get("kamera", "sedang"), 1.14); g = sc.get("gerak", "diam_merayap"); k = min(1.0, tl / max(dur, 0.5))
        k = k * k * (3 - 2 * k); cx, cy = 540.0, 840.0
        if g == "dorong_masuk": z = z0 * (1 + 0.12 * k)
        elif g == "geser_kanan": z = z0 * 1.05; cx = 540 + (-30 + 60 * k) * (1 if z0 > 1.02 else 0.4)
        else: z = z0 * (1 + 0.03 * k)
        z = max(1.0, z); hw = W / 2.0 / z; hh = H / 2.0 / z
        cx = min(max(cx, hw), W - hw); cy = min(max(cy, hh), H - hh)
        return z, cx, cy

    def bg(s, i, sc):
        key = (i)
        if key not in s.bgc:
            s.bgc.clear(); s.bgc[key] = P.build_bg(sc.get("latar", "pantai_air_manis_siang"), sc.get("waktu", "siang"))
        return s.bgc[key]

    # ---------- frame ----------
    def frame(s, f):
        T = f / float(FPS); i = s.scene_at(T); sc = s.sc[i]; tl = T - s.t0[i]; dur = s.t1[i] - s.t0[i]
        z, cx, cy = s.camera(sc, tl, dur)
        bg = s.bg(i, sc)
        box = (int((cx - W / 2.0 / z) * 2), int((cy - H / 2.0 / z) * 2), int((cx + W / 2.0 / z) * 2), int((cy + H / 2.0 / z) * 2))
        base = bg.crop(box).resize((W, H), Image.BILINEAR).convert("RGBA")
        L = layer(2); p = Pen(L, 2, z, cx, cy); ctx = dict(dur=dur, heads=[], feet=[])
        for k in sc.get("properti", []):
            fn = P.PROPS.get(k)
            if fn is None: s.warn("properti", k); continue
            fn(p, tl, ctx)
        toks = sc.get("tokoh", []); n = len(toks)
        for j, tk in enumerate(toks):
            pos = tk.get("posisi", "tengah"); x = SPOS.get(pos, 540); fy = 1130; bh = 330; pose = tk.get("pose", "berdiri")
            if pos == "bawah": bh = 370; fy = 1190
            if pos == "atas": bh = 290; fy = 1010
            fc = 1 if x < 440 else -1
            if n == 1 and pos == "tengah": fc = 1
            if pose in ("berjalan", "naik_kapal"): x += -90 + min(tl, 4) * 45
            if pose == "berlari": x += -150 + min(tl, 3) * 120; fc = 1
            if tk.get("kunci") not in C.OUTFIT: s.warn("tokoh", tk.get("kunci"))
            info = C.person(p, x, fy, tk.get("kunci"), pose, tk.get("ekspresi", "tenang"), tl, fc, bh, seed=j + i)
            ctx["heads"].append((info["head"][0] + (6 if fc > 0 else -6), info["head"][1])); ctx["feet"].append((x, fy))
        ov = None
        for k in sc.get("efek", []):
            fn = P.FX.get(k)
            if fn is None: s.warn("efek", k); continue
            if k in ("awan_gelap", "petir", "kabut_pagi"):
                if ov is None: ov = layer(2)
            fn(p, tl, ctx, ov)
        base = Image.alpha_composite(base, L.resize((W, H), Image.LANCZOS))
        if ov is not None: base = Image.alpha_composite(base, ov.resize((W, H), Image.LANCZOS))
        # Pak Nusa (maskot): tanpa kamera
        U = layer(2); pu = Pen(U, 2)
        mi = min(f, len(s.mouth) - 1); mv = s.mouth[mi] if s.mouth else 0.0
        C.pak_nusa(pu, 790, 1425, 290, mouth=mv, t=T, wave=(T < 3.0 or i == len(s.sc) - 1), shock=("sting_tegang" in sc.get("sfx", [])), point=True)
        base = Image.alpha_composite(base, U.resize((W, H), Image.LANCZOS))
        im = base.convert("RGB"); s.ui(im, i, T, sc)
        # transisi
        tr = sc.get("transisi", "potong"); fr = f - int(round(s.t0[i] * FPS))
        if tr == "kilat_putih" and 0 <= fr < 6: im = Image.blend(im, Image.new("RGB", im.size, (255, 255, 255)), 1 - fr / 6.0)
        if tr == "pudar" and 0 <= fr < 10: im = Image.blend(im, Image.new("RGB", im.size, (30, 36, 34)), 1 - fr / 10.0)
        return im

    # ---------- UI 2D ----------
    def ui(s, im, i, T, sc):
        d = ImageDraw.Draw(im, "RGBA")
        # panel judul krem (di bawah y=190 aman), memudar
        pan = Image.new("RGBA", (W, 380), (0, 0, 0, 0)); pd = ImageDraw.Draw(pan)
        for y in range(380): pd.line([(0, y), (W, y)], fill=(237, 235, 221, int(228 * (1 - (y / 380.0) ** 2.0))))
        im.paste(pan, (0, 190), pan); d = ImageDraw.Draw(im, "RGBA")
        # watermark
        f = P.font(32); a, b = "NUSA", "KARA"; wa = d.textlength(a, font=f); wb = d.textlength(b, font=f)
        tw = wa + wb + 34; x0 = (W - tw - 44) / 2 - 20; y0 = 232
        d.rounded_rectangle([x0, y0, x0 + tw + 44, y0 + 60], radius=30, fill=(30, 38, 36)); d.text((x0 + 22, y0 + 8), a, font=f, fill=(255, 255, 255))
        d.rounded_rectangle([x0 + 22 + wa + 6, y0 + 8, x0 + 22 + wa + 6 + wb + 16, y0 + 52], radius=10, fill=MINT); d.text((x0 + 22 + wa + 14, y0 + 8), b, font=f, fill=(24, 52, 44))
        # label + judul
        lab = " ".join(s.label.upper().replace("·", " · ")) if False else "   ".join(" ".join(w) for w in s.label.upper().split(" "))
        d.text((60, 318), lab, font=P.font(21, True), fill=(84, 92, 86))
        s.heading_draw(d, s.heading[i])
        # subtitle
        s.subtitle(im, i, T)

    def heading_draw(s, d, text):
        if not text: return
        ft = P.font(58); toks = re.findall(r"\*[^*]+\*|[^\s*]+", text); lines = [[]]; wcur = 0
        for tk in toks:
            clean = tk.strip("*"); w = d.textlength(clean + " ", font=ft)
            if wcur + w > 840 and lines[-1]: lines.append([]); wcur = 0
            lines[-1].append(tk); wcur += w
        for li, ln in enumerate(lines[:2]):
            x = 60
            for tk in ln:
                kw = tk.startswith("*"); clean = tk.strip("*")
                if re.fullmatch(r"[^\w]+", clean): x -= d.textlength(" ", font=ft)
                d.text((x, 352 + li * 68), clean, font=ft, fill=TEAL if kw else (36, 44, 42)); x += d.textlength(clean + " ", font=ft)

    def subtitle(s, im, i, T):
        phr = s.phr[i]
        if not phr: return
        cur = None
        for k, ph in enumerate(phr):
            nxt = phr[k + 1][0]["start"] if k + 1 < len(phr) else 1e9
            if ph[0]["start"] - 0.05 <= T < min(nxt - 0.03, ph[-1]["end"] + 0.7) or (ph[0]["start"] - 0.05 <= T and nxt > T and T < ph[-1]["end"] + 0.7): cur = ph
        if cur is None: return
        f = P.font(44); d = ImageDraw.Draw(im, "RGBA"); sp = 12; maxw = 520
        lines = [[]]; wc = 0
        for w in cur:
            ww = d.textlength(w["w"], font=f)
            if wc + ww > maxw and lines[-1]: lines.append([]); wc = 0
            lines[-1].append(w); wc += ww + sp
        lines = lines[:2]; cxs = 350
        wid = [sum(d.textlength(w["w"], font=f) for w in ln) + sp * (len(ln) - 1) for ln in lines]
        bw = max(wid) + 60; hh = 70 * len(lines) + 20; by0 = 1422 - hh
        cap = Image.new("RGBA", im.size, (0, 0, 0, 0)); cd = ImageDraw.Draw(cap)
        cd.rounded_rectangle([cxs - bw / 2, by0, cxs + bw / 2, by0 + hh], radius=28, fill=(30, 58, 52, 230)); im.paste(cap, (0, 0), cap)
        d = ImageDraw.Draw(im, "RGBA")
        active = None
        for w in cur:
            if w["start"] - 0.06 <= T: active = w
        for li, ln in enumerate(lines):
            x = cxs - wid[li] / 2.0; y = by0 + 12 + li * 70
            for w in ln:
                ww = d.textlength(w["w"], font=f)
                if w is active: s.batik(im, x - 8, y + 4, ww + 16, 56)
                d = ImageDraw.Draw(im, "RGBA"); d.text((x, y), w["w"], font=f, fill=(255, 255, 255)); x += ww + sp

    def batik(s, im, x, y, w, h):
        w = int(w); h = int(h); tile = Image.new("RGBA", (w, h), (0, 0, 0, 0)); td = ImageDraw.Draw(tile)
        td.rounded_rectangle([0, 0, w - 1, h - 1], radius=12, fill=MINT + (70,)); c = 14
        for ci in range(-1, w // c + 2):
            for ri in range(-1, 5):
                px = ci * c + (c / 2 if ri % 2 else 0); py = ri * c * 0.9 + 4
                for ex, ey in ((-4, 0), (4, 0), (0, -4), (0, 4)): td.ellipse([px + ex - 5, py + ey - 5, px + ex + 5, py + ey + 5], outline=MINT + (170,), width=1)
        mask = Image.new("L", (w, h), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=12, fill=255)
        alpha = Image.composite(tile.split()[3], Image.new("L", (w, h), 0), mask); tile.putalpha(alpha)
        im.paste(tile, (int(x), int(y)), tile)


def main():
    mode = sys.argv[1]; sh = Show(); n = total_frames(sh.T)
    if mode == "meta": print(json.dumps({"frames": n, "seconds": round(n / FPS, 2)})); return
    if mode == "still":
        os.makedirs("stills", exist_ok=True)
        for t in sys.argv[2:]:
            sh.frame(int(float(t) * FPS)).save("stills/f_%s.jpg" % t, quality=92)
        return
    ci, cn, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    a, z = n * ci // cn, n * (ci + 1) // cn
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    import io
    for f in range(a, z):
        buf = io.BytesIO(); sh.frame(f).save(buf, "JPEG", quality=94); ff.stdin.write(buf.getvalue())
        if (f - a) % 30 == 0: print("frame %d/%d (potongan %d: %d-%d)" % (f, n, ci, a, z), flush=True)
    ff.stdin.close()
    if ff.wait() != 0: raise SystemExit("ffmpeg gagal")


if __name__ == "__main__":
    main()
