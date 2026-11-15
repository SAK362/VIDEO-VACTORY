#!/usr/bin/env python3
"""v2: tiap video unik dari seed. Pakai: python3 bounce2.py SEED out.mp4  (juga menulis out.json)"""
import sys, json, math, subprocess, colorsys, os, random, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 720, 1280, 30
CX, CY = 360, 700
SR = 44100
FONT_B = os.environ.get("FONT_B", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Poppins-Bold.ttf"))
WATERMARK = os.environ.get("WATERMARK", "Focaloop")

QUESTIONS = ["Do they all meet at one point?", "Will they all meet again?", "Where will they all meet?",
             "Do they come back together?", "Do they all end up at one point?"]
SCALES = {"pentatonic": [0, 2, 4, 7, 9], "major": [0, 2, 4, 5, 7, 9, 11], "minor": [0, 2, 3, 5, 7, 8, 10],
          "dorian": [0, 2, 3, 5, 7, 9, 10], "hirajoshi": [0, 2, 3, 7, 8]}
# (rasio, amplitudo, peluruhan) per partial
INSTR = {
    "bell":    dict(p=[(1, 1, 3.0), (2.76, .5, 4.5), (5.4, .3, 7), (8.93, .15, 10)], dur=1.4, att=.003),
    "marimba": dict(p=[(1, 1, 7.0), (4, .35, 16), (10, .1, 30)], dur=.6, att=.002),
    "pluck":   dict(p=[(1, 1, 9.0), (2, .5, 12), (3, .33, 15), (4, .2, 18), (5, .12, 22)], dur=.5, att=.001),
    "synth":   dict(p=[(1, 1, 4.0), (2, .5, 5), (3, .33, 6), (4, .25, 7)], dur=.7, att=.012),
    "glass":   dict(p=[(1, 1, 2.2), (3, .25, 3.5), (5, .08, 5)], dur=1.5, att=.006),
}


def gen_params(seed):
    r = random.Random(seed)
    ecc_mode = r.random()
    e = 0.0 if ecc_mode < 0.08 else r.uniform(0.35, 0.93)
    A = r.uniform(300, 420)
    B = A * math.sqrt(1 - e * e)
    phi = math.radians(r.choice([r.uniform(0, 180), r.uniform(75, 105), r.uniform(-20, 20)]))
    # muat di layar
    hx = math.sqrt((A * math.cos(phi)) ** 2 + (B * math.sin(phi)) ** 2)
    hy = math.sqrt((A * math.sin(phi)) ** 2 + (B * math.cos(phi)) ** 2)
    k = min(1.0, 335 / hx, 430 / hy)
    A, B = A * k, B * k
    c = math.sqrt(max(A * A - B * B, 0))
    tmeet = r.uniform(1.2, 2.0)
    launch = "focus"
    lp = [r.choice([-c, c]), 0.0]   # selalu dari salah satu fokus -> semua bola bertemu di fokus lain
    sector = r.choice([360, 360, 360, r.uniform(120, 300)])
    start = r.choice([1, 1, 2, 4]); fac = r.choice([2, 4, 4, 8])
    nst = r.randint(4, 6)
    counts, n = [], start
    for _ in range(nst):
        counts.append(min(n, 2048)); n *= fac
    counts = sorted(set(counts))
    hue0 = r.random(); span = r.uniform(0.35, 1.0)
    return dict(seed=seed, A=A, B=B, phi=phi, c=c, tmeet=tmeet, launch=launch, lp=lp, sector=sector,
                sector_rot=r.uniform(0, 2 * math.pi), counts=counts, hue0=hue0, span=span,
                question=r.choice(QUESTIONS), scale=r.choice(list(SCALES)), root=r.randint(48, 60),
                instr=r.choice(list(INSTR)), mapping=r.choice(["x", "angle", "walk"]),
                glow=r.uniform(0.9, 1.3), **gen_styles(seed))


def gen_styles(seed):
    r = random.Random(seed * 7919 + 13)
    return dict(wall_style=r.choice(["single", "thick", "thin", "double", "dashed", "dots"]),
                ball_style=r.choice(["dot", "square", "cross", "comet"]),
                line_style=r.choice(["thin", "bright", "fade", "thin"]),
                bg_style=r.choice(["vignette", "gradient", "stars", "grid", "particles"]),
                palette=r.choice(["rainbow", "mono", "duo"]),
                wall_hue_shift=r.choice([0.5, 0.0, 0.33]))


def pal(p, i, n):
    t = i / max(n, 1)
    if p["palette"] == "mono": return hsv_bgr(p["hue0"] + 0.06 * t, 0.35 + 0.6 * t, 1.0)
    if p["palette"] == "duo": return hsv_bgr(p["hue0"] + (0.5 if int(t * 8) % 2 else 0.0), 0.85, 1.0)
    return hsv_bgr(p["hue0"] + p["span"] * t, 0.85, 1.0)


def make_hit(p):
    A, B, phi = p["A"], p["B"], p["phi"]
    cs, sn = math.cos(phi), math.sin(phi)
    def to_local(x, y): dx, dy = x - CX, y - CY; return dx * cs + dy * sn, -dx * sn + dy * cs
    def to_world(x, y): return CX + x * cs - y * sn, CY + x * sn + y * cs
    def hit(px, py, vx, vy):
        x, y = to_local(px, py); ux, uy = vx * cs + vy * sn, -vx * sn + vy * cs
        a2, b2 = A * A, B * B
        Aq = ux * ux / a2 + uy * uy / b2; Bq = 2 * (x * ux / a2 + y * uy / b2); Cq = x * x / a2 + y * y / b2 - 1
        D = max(Bq * Bq - 4 * Aq * Cq, 0)
        t = (-Bq + math.sqrt(D)) / (2 * Aq)
        hx, hy = x + ux * t, y + uy * t
        nx, ny = hx / a2, hy / b2; n = math.hypot(nx, ny); nx, ny = nx / n, ny / n
        wx, wy = to_world(hx, hy)
        return t, wx, wy, nx * cs - ny * sn, nx * sn + ny * cs
    return hit, to_world


def simulate(hit, start, n, speed, T, sector, rot):
    paths, hits = [], []
    for i in range(n):
        ang = rot + (math.radians(sector) * (i + 0.5) / n)
        vx, vy = speed * math.cos(ang), speed * math.sin(ang)
        px, py = start; t = 0.0; pts = [(0.0, px, py)]; g = 0
        while t < T and g < 40:
            dt, hx, hy, nx, ny = hit(px, py, vx, vy)
            t += dt; pts.append((t, hx, hy)); hits.append((t, hx, hy))
            d = vx * nx + vy * ny; vx, vy = vx - 2 * d * nx, vy - 2 * d * ny
            px, py = hx - nx * 1e-3, hy - ny * 1e-3; g += 1
        pts.append((t + 10, px + vx * 10, py + vy * 10)); paths.append(np.array(pts))
    return paths, hits


def pos_at(path, t):
    ts = path[:, 0]; k = min(max(int(np.searchsorted(ts, t, side="right")) - 1, 0), len(ts) - 2)
    f = (t - ts[k]) / max(ts[k + 1] - ts[k], 1e-9)
    return path[k, 1] + (path[k + 1, 1] - path[k, 1]) * f, path[k, 2] + (path[k + 1, 2] - path[k, 2]) * f, k


def hsv_bgr(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v); return (int(b * 255), int(g * 255), int(r * 255))


def build_base(p):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - CX) / 520.0) ** 2 + ((yy - CY) / 760.0) ** 2)
    v = np.clip(16 - 12 * d, 4, 16)
    tint = np.array(hsv_bgr(p["hue0"] + 0.5, 0.6, 1.0), np.float32) / 255.0
    base = (v[:, :, None] * (0.6 + 0.8 * tint[None, None, :])).clip(0, 255).astype(np.uint8)
    rg = random.Random(p["seed"] + 99)
    if p["bg_style"] == "gradient":
        top = np.array(hsv_bgr(p["hue0"] + 0.55, 0.7, 0.20), np.float32); bot = np.array(hsv_bgr(p["hue0"] + 0.7, 0.7, 0.03), np.float32)
        gy = np.linspace(0, 1, H)[:, None, None]; base = (top * (1 - gy) + bot * gy).repeat(W, 1).astype(np.uint8)
    elif p["bg_style"] == "stars":
        for _ in range(220): cv2.circle(base, (rg.randrange(W), rg.randrange(H)), 1, (rg.randint(40, 110),) * 3, -1)
    elif p["bg_style"] == "grid":
        for x in range(0, W, 80): cv2.line(base, (x, 0), (x, H), (26, 26, 26), 1)
        for y in range(0, H, 80): cv2.line(base, (0, y), (W, y), (26, 26, 26), 1)
    wall = np.zeros((H, W, 3), np.uint8)
    col = hsv_bgr(p["hue0"] + p["wall_hue_shift"], 0.75, 1.0)
    A, B, ph = int(p["A"]), int(p["B"]), math.degrees(p["phi"]); ws = p["wall_style"]; gs = 7
    if ws == "thick": cv2.ellipse(wall, (CX, CY), (A, B), ph, 0, 360, col, 7, cv2.LINE_AA); gs = 11
    elif ws == "thin": cv2.ellipse(wall, (CX, CY), (A, B), ph, 0, 360, col, 1, cv2.LINE_AA); gs = 4
    elif ws == "double":
        cv2.ellipse(wall, (CX, CY), (A, B), ph, 0, 360, col, 2, cv2.LINE_AA)
        cv2.ellipse(wall, (CX, CY), (A - 12, max(B - 12, 4)), ph, 0, 360, col, 2, cv2.LINE_AA)
    elif ws == "dashed":
        for a in range(0, 360, 12): cv2.ellipse(wall, (CX, CY), (A, B), ph, a, a + 7, col, 4, cv2.LINE_AA)
    elif ws == "dots":
        cs_, sn_ = math.cos(p["phi"]), math.sin(p["phi"])
        for k in range(150):
            th = 2 * math.pi * k / 150; x, y = p["A"] * math.cos(th), p["B"] * math.sin(th)
            cv2.circle(wall, (int(CX + x * cs_ - y * sn_), int(CY + x * sn_ + y * cs_)), 3, col, -1, cv2.LINE_AA)
    else: cv2.ellipse(wall, (CX, CY), (A, B), ph, 0, 360, col, 3, cv2.LINE_AA)
    glow = cv2.GaussianBlur(wall, (0, 0), gs)
    return cv2.add(base, cv2.add(wall, (glow * 1.2).clip(0, 255).astype(np.uint8)))


def bg_frame(base, p, t):
    if p["bg_style"] != "particles": return base
    f = base.copy(); rg = random.Random(p["seed"] + 5)
    for _ in range(60):
        x0, y0, sp, ph = rg.uniform(0, W), rg.uniform(0, H), rg.uniform(8, 30), rg.uniform(0, 6.28)
        cv2.circle(f, (int((x0 + 20 * math.sin(t * .5 + ph)) % W), int((y0 - sp * t) % H)), 2, (70, 70, 70), -1, cv2.LINE_AA)
    return f


def draw_ball(img, x, y, hr, c, p, pa, t, n):
    bs = p["ball_style"]
    if bs == "square": cv2.rectangle(img, (int(x) - hr, int(y) - hr), (int(x) + hr, int(y) + hr), c, -1)
    elif bs == "cross":
        cv2.line(img, (int(x) - hr * 2, int(y)), (int(x) + hr * 2, int(y)), c, 1, cv2.LINE_AA)
        cv2.line(img, (int(x), int(y) - hr * 2), (int(x), int(y) + hr * 2), c, 1, cv2.LINE_AA)
        cv2.circle(img, (int(x), int(y)), max(hr - 1, 1), c, -1, cv2.LINE_AA)
    elif bs == "comet" and n <= 512:
        px_, py_ = x, y
        for j in range(1, 7):
            qx, qy, _ = pos_at(pa, max(t - j * 0.03, 0)); k = 1 - j / 7
            cv2.line(img, (int(px_), int(py_)), (int(qx), int(qy)), tuple(int(v * k) for v in c), max(hr - j // 2, 1), cv2.LINE_AA); px_, py_ = qx, qy
        cv2.circle(img, (int(x), int(y)), hr, c, -1, cv2.LINE_AA)
    else: cv2.circle(img, (int(x), int(y)), hr, c, -1, cv2.LINE_AA)


def text_layer(question, label):
    img = Image.new("RGBA", (W, 230), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f1 = ImageFont.truetype(FONT_B, 34); f2 = ImageFont.truetype(FONT_B, 44)
    f3 = ImageFont.truetype(FONT_B, 24)
    for txt, f, y, col in ((question, f1, 70, (255, 255, 255, 255)), (label, f2, 125, (255, 214, 90, 255)),
                           (WATERMARK, f3, 188, (255, 255, 255, 130))):
        d.text(((W - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill=col)
    a = np.array(img); return a[:, :, :3][:, :, ::-1].astype(np.float32), (a[:, :, 3:] / 255.0).astype(np.float32)


def add_tone(buf, t0, freq, amp, ins):
    i0 = int(t0 * SR)
    if i0 >= len(buf): return
    n = min(int(ins["dur"] * SR), len(buf) - i0); t = np.arange(n) / SR
    wave_ = sum(a * np.exp(-t * dc) * np.sin(2 * math.pi * freq * r * t) for r, a, dc in ins["p"] if freq * r < 9000)
    buf[i0:i0 + n] += (amp * np.minimum(t / ins["att"], 1.0) * wave_).astype(np.float32)


def build_audio(stage_hits, T, p, total):
    buf = np.zeros(int(total * SR) + SR, np.float32)
    ins = INSTR[p["instr"]]; sc = SCALES[p["scale"]]; L = len(sc)
    rng = random.Random(p["seed"] + 7)
    def freq(idx):
        o, dg = divmod(idx, L); return 440.0 * 2 ** ((p["root"] + 12 * o + sc[dg] - 69) / 12)
    walk = 7
    for s, hits in enumerate(stage_hits):
        off = s * T; buckets = {}
        for t, x, y in hits:
            if t <= T: buckets.setdefault(int(t / 0.04), []).append((x, y))
        for k in sorted(buckets):
            pts = buckets[k]; mx = np.mean([q[0] for q in pts]); my = np.mean([q[1] for q in pts])
            if p["mapping"] == "x": idx = int(np.clip((mx - (CX - p["A"])) / (2 * p["A"]), 0, .999) * 2 * L)
            elif p["mapping"] == "angle": idx = int(((math.atan2(my - CY, mx - CX) + math.pi) / (2 * math.pi)) * 2 * L)
            else:
                walk = int(np.clip(walk + rng.choice([-2, -1, -1, 1, 1, 2]), 0, 2 * L)); idx = walk
            n = len(pts); amp = 0.30 / math.sqrt(n) * min(1.0, 0.5 + 0.1 * math.sqrt(n))
            add_tone(buf, off + k * 0.04, freq(idx), amp, ins)
            if n > 12: add_tone(buf, off + k * 0.04, freq(idx) / 2, amp * 0.5, ins)
        if p["launch"] == "focus":
            for kk in (1, 2): add_tone(buf, off + kk * p["tmeet"] - 0.01, freq(0) / 2, 0.45, ins)
    pk = np.max(np.abs(buf)) or 1; return buf / pk * 0.85


def main(seed, out_path):
    p = gen_params(int(seed)); hit, to_world = make_hit(p)
    start = to_world(*p["lp"]); speed = 2 * p["A"] / p["tmeet"]; T = 2 * p["tmeet"]
    base = build_base(p); nst = len(p["counts"]); total = T * nst; fpp = int(round(T * FPS))
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    tv, ta = out_path + ".v.mp4", out_path + ".a.wav"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tv], stdin=subprocess.PIPE)
    stage_hits = []
    for s, n in enumerate(p["counts"]):
        paths, hits = simulate(hit, start, n, speed, T + 0.2, p["sector"], p["sector_rot"]); stage_hits.append(hits)
        cols = [pal(p, i, n) for i in range(n)]
        tcol, talpha = text_layer(p["question"], f"{n:,} ball" + ("s" if n > 1 else ""))
        lines = np.zeros((H, W, 3), np.uint8)
        gain = 0.55 if n < 100 else (0.22 if n < 800 else 0.10); hr = 4 if n < 100 else (3 if n < 800 else 2)
        ls = p["line_style"]; gain = min(gain * (1.8 if ls == "bright" else (2.2 if ls == "fade" else 1.0)), 0.85)
        last = [(pa[0, 1], pa[0, 2], 0) for pa in paths]
        for fr in range(fpp):
            t = fr / FPS; heads = np.zeros((H, W, 3), np.uint8)
            if ls == "fade": lines = cv2.convertScaleAbs(lines, alpha=0.95)
            for i, pa in enumerate(paths):
                x, y, k = pos_at(pa, t); lx, ly, lk = last[i]; c = tuple(int(v * gain) for v in cols[i]); qx, qy = lx, ly
                for kk in range(lk + 1, k + 1):
                    cv2.line(lines, (int(qx), int(qy)), (int(pa[kk, 1]), int(pa[kk, 2])), c, 1, cv2.LINE_AA); qx, qy = pa[kk, 1], pa[kk, 2]
                cv2.line(lines, (int(qx), int(qy)), (int(x), int(y)), c, 1, cv2.LINE_AA)
                last[i] = (x, y, k); draw_ball(heads, x, y, hr, cols[i], p, pa, t, n)
            g1 = cv2.GaussianBlur(heads, (0, 0), 6); g2 = cv2.GaussianBlur(heads, (0, 0), 2)
            f = cv2.add(cv2.add(bg_frame(base, p, s * T + t), lines), heads)
            f = cv2.add(f, (g1 * 1.8 * p["glow"]).clip(0, 255).astype(np.uint8)); f = cv2.add(f, (g2 * .8).clip(0, 255).astype(np.uint8))
            f[:230] = (f[:230].astype(np.float32) * (1 - talpha) + tcol * talpha).clip(0, 255).astype(np.uint8)
            ff.stdin.write(f.tobytes())
    ff.stdin.close(); ff.wait()
    au = build_audio(stage_hits, T, p, total)
    with wave.open(ta, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((au[:int(total * SR)] * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tv, "-i", ta, "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", out_path], check=True)
    os.remove(tv); os.remove(ta); json.dump(p, open(out_path.rsplit(".", 1)[0] + ".json", "w"), indent=1)
    print("OK", out_path, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in p.items() if k in ("sector", "counts", "scale", "instr", "mapping", "wall_style", "ball_style", "line_style", "bg_style", "palette")})

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
