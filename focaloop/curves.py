"""Tema CURVES: banyak bola, tiap bola HANYA bergerak lurus bolak-balik di sumbunya; fase diatur sehingga gabungan bola
membentuk lingkaran / bunga / cincin. Semua parameter diturunkan dari seed (bentuk arena, jumlah bola, warna, urutan pola,
teks). Pakai: make(seed, base) -> meta (menulis base.mp4)."""
import random
from fx import *

CX, CY = 360, 700
SHAPES = [("circle", 0, 300, 38), ("hexagon", 6, 310, 14), ("square", 4, 372, 14), ("octagon", 8, 310, 10),
          ("pentagon", 5, 320, 12), ("triangle", 3, 360, 12)]
TOP = [
    ("{n} balls. only straight lines", "where do flowers come from?", True),
    ("no ball moves in a curve", "not even one", False),
    ("straight lines only", "so why does it curve?", True),
    ("{n} balls, zero curves", "or is it?", False),
    ("every ball goes straight", "so where do curves come from?", True),
    ("nothing here moves in a circle", "watch closely", True),
    ("{n} straight lines", "one hidden shape", False),
    ("it looks curved", "but nothing is curved", True),
]
BOTTOM = [
    ("every ball moves straight", "but together they curve"), ("{n} straight lines", "one hidden pattern"),
    ("watch the pattern change", ""), ("no curve was drawn", "only straight paths"),
    ("the curve is an illusion", "the lines are real"), ("{n} balls, zero curves", "watch the pattern change"),
]


def gen_params(seed):
    r = random.Random(seed * 1000003 + 11)
    sh = r.choices(SHAPES, [s[3] for s in SHAPES])[0]
    N = r.randrange(25, 66) | 1  # ganjil agar bola tidak menumpuk persis
    k = r.choice([4, 5, 5, 6, 6])
    vals = r.sample([1, 2, 3, 4, 5, 6, 7], k - 1)
    vals.append(0)  # selalu berakhir sebagai cincin penuh
    ramp = r.uniform(2.6, 3.6)
    hold = r.uniform(4.2, 6.2)
    build = r.uniform(5.5, 8.0)
    t = 3.0 + build + hold
    ramps = []
    for v in vals[1:]:
        ramps.append((t, t + ramp, v))
        t += ramp + hold
    T = round(t + 1.5, 1)
    mode = r.choice(["rainbow", "rainbow", "duo", "duo", "warm", "cool"])
    h0 = r.random()
    if mode == "rainbow":
        hue = (h0, h0 + 1.0)
    elif mode == "duo":
        hue = (h0, h0 + r.choice([0.3, 0.4, -0.3, -0.4]))
    elif mode == "warm":
        hue = (0.88, 1.16)
    else:
        hue = (0.45, 0.78)
    top, tq, eyes = r.choice(TOP)
    b1, b2 = r.choice(BOTTOM)
    return dict(seed=seed, shape=sh[0], sides=sh[1], circ=sh[2], N=N, build=build, T=T, m0=vals[0], ramps=ramps, mode=mode,
                hue=hue, sat=r.uniform(0.7, 0.9), br=r.choice([5, 6, 6, 7]), omega=2 * np.pi / r.uniform(2.7, 4.2),
                rot=r.choice([0, 0, 0.03, -0.03]), phi0=np.pi / 2, base=r.choice([220.0, 246.94, 261.63, 277.18, 293.66, 329.63]),
                top=[top.format(n=N), tq.format(n=N)], eyes=eyes, bottom=[x.format(n=N) for x in (b1, b2) if x],
                cap_t=3.0 + build + 1.0, bg_h=h0, pad=r.choice([[110, 165, 220.5], [98, 147, 196], [130, 195, 260]]),
                tone=r.choice([(1, .25), (1, .35, .12), (1, .5, .2)]), vals=vals)


def arena_pts(p):
    return regular_polygon(p["sides"], p["circ"], -math.pi / 4 if p["sides"] == 4 else -math.pi / 2)


def amp_fn(p):
    if p["sides"] == 0:
        return lambda th: np.full_like(th, 300.0)
    P = arena_pts(p)
    n, d = poly_edges(P)

    def f(th):
        dirs = np.stack([np.cos(th), np.sin(th)], 1)
        nd = dirs @ n.T
        with np.errstate(divide="ignore", invalid="ignore"):
            t = np.where(nd > 1e-9, d[None, :] / nd, np.inf)
        return t.min(1) - p["br"]
    return f


def mval(p, t):
    m = p["m0"]
    for (a, b, tgt) in p["ramps"]:
        if t <= a:
            return m
        if t < b:
            x = (t - a) / (b - a)
            return m + (tgt - m) * x * x * (3 - 2 * x)
        m = tgt
    return m


def setup(p):
    N = p["N"]
    th0 = 2 * np.pi * np.arange(N) / N
    st = max(1, int(round(N * 0.618)))
    while math.gcd(st, N) != 1:
        st += 1
    appear = np.zeros(N)
    for j in range(N):
        appear[(j * st) % N] = 0 if j == 0 else 3.0 + (j - 1) * p["build"] / (N - 1)
    h0, h1 = p["hue"]
    cols = [hsv_rgb(h0 + (h1 - h0) * k / N, p["sat"], 1.0) for k in range(N)]
    return dict(th0=th0, appear=appear, cols=cols, A=amp_fn(p))


def positions(p, S, t):
    th = S["th0"] + p["rot"] * t
    A = S["A"](th)
    s = A * np.cos(p["omega"] * t + mval(p, t) * S["th0"] + p["phi0"])
    return np.stack([s * np.cos(th), s * np.sin(th)], 1), th, A


def render_frame(p, S, fi, bg):
    t = fi / FPS
    N = p["N"]
    img = bg.copy()
    glow = np.zeros_like(img)
    P, th, A = positions(p, S, t)
    vis = np.clip((t - S["appear"]) / 0.45, 0, 1)
    off = np.array([CX, CY])
    arena = hsv_rgb(p["hue"][0] + 0.05, 0.45, 1.0)
    if p["sides"] == 0:
        cv2.circle(img, (CX, CY), 300, arena, 2, cv2.LINE_AA)
        cv2.circle(glow, (CX, CY), 300, scale(arena, 0.3), 5, cv2.LINE_AA)
    else:
        Pp = (arena_pts(p) + off).astype(np.int32)
        cv2.polylines(img, [Pp], True, arena, 2, cv2.LINE_AA)
        cv2.polylines(glow, [Pp], True, scale(arena, 0.3), 5, cv2.LINE_AA)
    prev = [positions(p, S, t - 0.022 * j)[0] for j in range(1, 9)]
    for k in range(N):
        v = vis[k]
        if v <= 0:
            continue
        c = bgr(S["cols"][k])
        d_ = np.array([math.cos(th[k]), math.sin(th[k])])
        e1, e0 = off + A[k] * d_, off - A[k] * d_
        cv2.line(img, (int(e0[0] * 8), int(e0[1] * 8)), (int(e1[0] * 8), int(e1[1] * 8)), scale(c, 0.16 * v), 1, cv2.LINE_AA, 3)
        for j, pj in enumerate(prev):
            q = pj[k] + off
            cv2.circle(glow, (int(q[0]), int(q[1])), max(1, int(p["br"] * (1 - (j + 1) / 11))),
                       scale(c, (1 - (j + 1) / 9) * v * 0.7), -1, cv2.LINE_AA)
        pc = (int(P[k][0] + CX), int(P[k][1] + CY))
        cv2.circle(glow, pc, int(p["br"] * 2.2), scale(c, 0.55 * v), -1, cv2.LINE_AA)
        cv2.circle(img, pc, p["br"], scale(c, v), -1, cv2.LINE_AA)
        cv2.circle(img, pc, max(1, p["br"] // 2), scale((255, 255, 255), v), -1, cv2.LINE_AA)
    return overlay(p, bloom(img, glow, 1.0), t)


def overlay(p, out, t):
    pil = Image.fromarray(out[:, :, ::-1])
    d = ImageDraw.Draw(pil)
    a = min(1, t / 0.6)
    pill = hsv_rgb(p["hue"][0] + 0.02, 0.62, 0.78)
    y = 120
    for i, ln in enumerate(p["top"]):
        extra = 46 if (p["eyes"] and i == len(p["top"]) - 1) else 0
        sz = 34
        while d.textlength(ln, font=font(sz)) + extra > 600:
            sz -= 2
        tw = d.textlength(ln, font=font(sz))
        w = tw + extra
        x0 = 360 - w / 2
        d.rounded_rectangle([x0 - 16, y - 27, x0 + w + 16, y + 27], radius=14, fill=scale(pill, a))
        d.text((x0 + tw / 2, y), ln, font=font(sz), fill=scale((255, 255, 255), a), anchor="mm")
        if extra:
            ex = x0 + tw + 12
            for q in range(2):
                bx = ex + q * 18
                d.ellipse([bx, y - 13, bx + 15, y + 13], fill=scale((250, 250, 250), a))
                d.ellipse([bx + 5, y - 3, bx + 12, y + 9], fill=scale((15, 15, 25), a))
        y += 58
    if t >= p["cap_t"]:
        b = min(1, (t - p["cap_t"]) / 0.6)
        for i, ln in enumerate(p["bottom"]):
            d.text((360, 1040 + i * 44), ln, font=font(28), fill=scale((245, 245, 250), b), anchor="mm")
    d.text((360, 46), WATERMARK, font=font(22), fill=(140, 140, 165), anchor="mm")
    return np.asarray(pil)[:, :, ::-1].copy()


def audio(p, S):
    T = p["T"]
    buf = np.zeros(int(T * SR) + SR // 2)
    add_pad(buf, p["pad"], 0.05)
    N = p["N"]
    ts = np.arange(0, T, 1 / 240)
    s_all = np.zeros((len(ts), N))
    for i, t in enumerate(ts):
        P, th, A = positions(p, S, t)
        s_all[i] = np.cos(th) * P[:, 0] + np.sin(th) * P[:, 1]
    ds = np.diff(s_all, axis=0)
    turn = ((ds[:-1] > 0) & (ds[1:] <= 0)) | ((ds[:-1] < 0) & (ds[1:] >= 0))
    amp = 0.55 / math.sqrt(N)
    for i in range(turn.shape[0]):
        t = ts[i + 1]
        for k in np.where(turn[i])[0]:
            if t >= S["appear"][k]:
                add_tone(buf, t, pnote(int(k / N * 14), p["base"]), 0.35, amp, 0.09, harm=p["tone"])
    for (a, b, tgt) in p["ramps"]:
        add_tone(buf, a, p["base"] / 2, b - a, 0.07, 3.0, harm=(1, .3), glide=2.0)
        add_tone(buf, b, pnote(7, p["base"]), 1.6, 0.12, 0.7)
    return buf


def make(seed, base):
    p = gen_params(seed)
    S = setup(p)
    bg = gradient_bg(hsv_rgb(p["bg_h"], 0.5, 0.11), hsv_rgb(p["bg_h"] + 0.05, 0.5, 0.045))
    out = base + ".mp4"
    w = Writer(out)
    n = int(p["T"] * FPS)
    for fi in range(n):
        w.write(render_frame(p, S, fi, bg))
    w.close()
    finish(w, audio(p, S), out)
    t_thumb = p["ramps"][0][0] - 0.6 if len(p["ramps"]) > 1 else p["T"] / 2
    pv = p["ramps"][1][0] - 0.6 if len(p["ramps"]) > 1 else t_thumb
    return dict(kind="curves", question=" ".join(p["top"]), palette=p["mode"], scale="pentatonic", instr="soft pluck",
                mapping=f"{p['N']} straight-line balls", ball_style="glow dots", bg_style="gradient", counts=[p["N"]],
                counts_text=f"{p['N']} balls moving only in straight lines, forming curves", duration=p["T"],
                shape=p["shape"], pattern_order=p["vals"], thumb_t=round(pv, 2), points=[], kinds=["curves"])
