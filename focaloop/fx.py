"""Utilitas bersama untuk tema Focaloop tambahan (curves, survive, escape): video, teks, bloom, audio."""
import os, math, wave, subprocess, colorsys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SR = 720, 1280, 30, 44100
WATERMARK = os.environ.get("WATERMARK", "Focaloop")
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Poppins-Bold.ttf")
_fc = {}


def font(sz):
    sz = int(sz)
    if sz not in _fc:
        _fc[sz] = ImageFont.truetype(FONT, sz)
    return _fc[sz]


def bgr(c):
    return (int(c[2]), int(c[1]), int(c[0]))


def scale(c, k):
    return tuple(int(max(0, min(255, v * k))) for v in c)


def hsv_rgb(h, s=0.8, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def fit(d, text, size, maxw):
    s = size
    while s > 12 and d.textlength(text, font=font(s)) > maxw:
        s -= 2
    return s


def draw_text(img, items):
    """items: (text, cx, cy, size, rgb, maxw) -> BGR array"""
    pil = Image.fromarray(img[:, :, ::-1])
    d = ImageDraw.Draw(pil)
    for text, cx, cy, sz, col, maxw in items:
        s = fit(d, text, sz, maxw)
        d.text((cx, cy), text, font=font(s), fill=tuple(int(v) for v in col), anchor="mm")
    return np.asarray(pil)[:, :, ::-1].copy()


def bloom(img, glow, k=1.0, down=4, blur=9):
    small = cv2.resize(glow, (W // down, H // down), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), blur / 2)
    big = cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR)
    out = cv2.add(img, glow)
    return cv2.add(out, (big * 1.6 * k).clip(0, 255).astype(np.uint8))


def gradient_bg(top, bot):
    f = np.linspace(0, 1, H)[:, None]
    col = (np.array(top, float) * (1 - f) + np.array(bot, float) * f)[:, ::-1]
    return np.repeat(col[:, None, :], W, axis=1).astype(np.uint8)


# ---------------- audio ----------------
def add_tone(buf, t0, freq, dur, amp, tau, harm=(1, .35, .12), attack=.004, glide=None):
    i0 = int(t0 * SR)
    if i0 < 0 or i0 >= len(buf):
        return
    n = min(int(dur * SR), len(buf) - i0)
    tt = np.arange(n) / SR
    f = freq * np.ones(n) if glide is None else freq * (1 + (glide - 1) * tt / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = sum(a * np.sin((k + 1) * ph) for k, a in enumerate(harm))
    buf[i0:i0 + n] += amp * sig * np.exp(-tt / tau) * np.minimum(1, tt / attack)


def add_noise(buf, t0, dur, amp, tau, seed=0, lp=0.15):
    i0 = int(t0 * SR)
    if i0 >= len(buf):
        return
    n = min(int(dur * SR), len(buf) - i0)
    r = np.random.default_rng(seed).standard_normal(n)
    # one-pole low pass, vectorised with lfilter-like recursion in blocks
    y = np.empty(n)
    a = 0.0
    for i in range(n):
        a += lp * (r[i] - a)
        y[i] = a
    tt = np.arange(n) / SR
    buf[i0:i0 + n] += amp * y * np.exp(-tt / tau) * 6


def add_pad(buf, freqs, amp, lfo=0.15):
    tt = np.arange(len(buf)) / SR
    sig = sum(np.sin(2 * np.pi * f * tt + i) for i, f in enumerate(freqs)) / len(freqs)
    fi = np.minimum(1, tt / 1.0)
    fo = np.minimum(1, (len(buf) / SR - tt) / 1.0)
    buf += amp * sig * (0.75 + 0.25 * np.sin(2 * np.pi * lfo * tt)) * fi * fo


PENTA = [0, 2, 4, 7, 9]


def pnote(i, base=261.63):
    octv, k = divmod(int(i), 5)
    return base * 2 ** ((PENTA[k] + 12 * octv) / 12)


def write_wav(path, buf):
    peak = np.abs(buf).max()
    if peak > 0:
        buf = buf / peak * 0.88
    fo = int(0.35 * SR)
    buf[-fo:] *= np.linspace(1, 0, fo)
    pcm = (np.repeat(buf[:, None], 2, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# ---------------- video io ----------------
class Writer:
    def __init__(self, path):
        self.path = path
        self.tmp = path + ".v.mp4"
        self.p = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
             "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", self.tmp],
            stdin=subprocess.PIPE)

    def write(self, frame):
        self.p.stdin.write(frame.tobytes())

    def close(self):
        self.p.stdin.close()
        if self.p.wait() != 0:
            raise RuntimeError("ffmpeg encode failed")


def finish(writer, buf, out):
    wav = out + ".wav"
    write_wav(wav, buf)
    tmp = out + ".mux.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", writer.tmp, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", tmp], check=True)
    os.replace(tmp, out)
    os.remove(writer.tmp)
    os.remove(wav)


def regular_polygon(n, circ, rot=-math.pi / 2):
    a = rot + 2 * np.pi * np.arange(n) / n
    return np.stack([circ * np.cos(a), circ * np.sin(a)], 1)


def poly_edges(P):
    E = np.roll(P, -1, 0) - P
    n = np.stack([E[:, 1], -E[:, 0]], 1)
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    mid = (P + np.roll(P, -1, 0)) / 2
    n *= np.sign(((mid - P.mean(0)) * n).sum(1))[:, None]
    return n, (n * P).sum(1)


def watermark_item():
    return (WATERMARK, W / 2, 46, 22, (140, 140, 165), 400)
