"""Tema ESCAPE: satu bola lurus-memantul di dalam lapisan berputar (cincin/poligon) yang punya celah; celah berputar, bola
lolos satu lapisan demi satu lapisan. Pola lapisan (labirin) diacak dari seed: bentuk per lapisan, jumlah lapisan/celah,
lebar celah, arah+kecepatan putar, warna, kecepatan bola. Pilih seed yang durasinya pas (18-45 dtk)."""
import random
from fx import *

CX, CY = 360, 640
BRB = 12
R_OUT = 320
SHAPE_NAME = {0: "RINGS", 3: "TRIANGLES", 4: "SQUARES", 5: "PENTAGONS", 6: "HEXAGONS", 8: "OCTAGONS"}
SUBS = ["Watch the last second.", "Don't blink.", "Wait for it.", "Almost there...", "Can it make it out?", "Watch the gap."]
BALLS = [(255, 200, 40), (90, 255, 235), (255, 120, 200), (170, 255, 80), (235, 225, 255), (255, 140, 60)]


def gen_params(seed):
    r = random.Random(seed * 1000033 + 3)
    N = r.choice([3, 4, 4, 5, 5, 6, 7])
    layout = r.choice(["rings", "rings", "poly", "alt", "grow", "mix"])
    poly_n = r.choice([3, 4, 5, 6, 6, 8])
    sides = []
    for k in range(N):
        if layout == "rings":
            sides.append(0)
        elif layout == "poly":
            sides.append(poly_n)
        elif layout == "alt":
            sides.append(0 if k % 2 == 0 else poly_n)
        elif layout == "grow":
            sides.append(min(3 + k, 8))
        else:
            sides.append(r.choice([0, 0, 3, 4, 5, 6, 8]))
    rmin = r.choice([60, 75, 90])
    for _try in range(2):
        radii = []
        for k in range(N):
            lin = rmin + (R_OUT - rmin) * k / max(1, N - 1)
            c_ = math.cos(math.pi / sides[k]) if sides[k] else 1.0
            if k == 0:
                radii.append(max(lin, 50 / c_))
            else:
                radii.append(max(lin, radii[-1] / c_ * 1.1))
        if radii[-1] <= R_OUT * 1.12:
            break
        sides = [8 if s_ else 0 for s_ in sides]  # terlalu sempit: pakai bentuk lebih bulat
    sc_ = min(1.0, R_OUT / radii[-1])
    radii = [x * sc_ for x in radii]
    gaps = []
    for k in range(N):
        g = 1 if radii[k] < 150 else r.choice([1, 1, 2, 3])
        total = r.uniform(1.0, 1.5) if g == 1 else r.uniform(1.4, 2.0)
        w = total / g
        g0 = r.uniform(0, 2 * np.pi)
        gaps.append([(g0 + 2 * np.pi * j / g, w) for j in range(g)])
    spin0 = r.uniform(0.25, 0.6)
    om = [(1 if (k + r.randrange(2)) % 2 == 0 else -1) * (spin0 + r.uniform(0, 0.15) * k) for k in range(N)]
    h0 = r.random()
    mode = r.choice(["rainbow", "duo", "duo", "warm", "cool"])
    if mode == "rainbow":
        hues = [h0 + 0.8 * k / max(1, N - 1) for k in range(N)]
    elif mode == "duo":
        hues = [h0 + 0.3 * k / max(1, N - 1) for k in range(N)]
    elif mode == "warm":
        hues = [0.9 + 0.2 * k / max(1, N - 1) for k in range(N)]
    else:
        hues = [0.45 + 0.35 * k / max(1, N - 1) for k in range(N)]
    pal = [hsv_rgb(h, 0.55, 1.0) for h in hues]
    shape_word = SHAPE_NAME.get(poly_n if layout in ("poly",) else 0, "RINGS")
    if layout == "rings":
        titles = [f"ESCAPE ALL {N} RINGS?", f"CAN IT ESCAPE {N} RINGS?", f"{N} RINGS. 1 BALL.", "CAN THE BALL ESCAPE?"]
    elif layout == "poly":
        titles = [f"ESCAPE THE {N} {shape_word}?", f"CAN IT ESCAPE THE {shape_word}?", f"{N} LAYERS. 1 BALL."]
    else:
        titles = [f"ESCAPE ALL {N} LAYERS?", "CAN IT ESCAPE THE MAZE?", f"{N} LAYERS. 1 BALL.", "ESCAPE THE MAZE?"]
    ph0 = [r.uniform(0, 2 * np.pi) for _ in range(N)]
    return dict(seed=seed, N=N, layout=layout, sides=sides, radii=radii, gaps=gaps, om=om, ph0=ph0, pal=pal,
                speed=r.uniform(250, 370), ball=r.choice(BALLS), title=r.choice(titles), sub=r.choice(SUBS),
                bg=(hsv_rgb(h0 + 0.05, 0.6, 0.1), hsv_rgb(h0 + 0.1, 0.6, 0.045)), base=r.choice([246.94, 261.63, 277.18, 293.66, 329.63]),
                pad=r.choice([[98, 147, 196.5], [110, 165, 220.5], [130, 195, 260]]), word="LAYERS" if layout not in ("rings",) else "RINGS")


def rwrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def in_gap(p, k, ang):
    for (g0, w) in p["gaps"][k]:
        if abs(rwrap(ang - g0)) < w / 2 - BRB / p["radii"][k] * 1.1:
            return True
    return False


def sim(p, sseed):
    rng = np.random.default_rng(sseed)
    N = p["N"]
    a0 = rng.uniform(0, 2 * np.pi)
    pos_ = np.array([math.cos(a0), math.sin(a0)]) * 6.0
    va = rng.uniform(0, 2 * np.pi)
    v = np.array([math.cos(va), math.sin(va)]) * p["speed"]
    h = 1 / 240
    k, t, step = 0, 0.0, 0
    esc, bounces, pts = [None] * N, [], []
    end_t = None
    while True:
        pos_ = pos_ + v * h
        t += h
        if k < N:
            Rk, sd = p["radii"][k], p["sides"][k]
            phi = p["ph0"][k] + p["om"][k] * t
            c, s_ = math.cos(-phi), math.sin(-phi)
            q = np.array([c * pos_[0] - s_ * pos_[1], s_ * pos_[0] + c * pos_[1]])
            if sd == 0:
                dist = np.linalg.norm(q)
                nq = q / max(dist, 1e-9)
                lim = Rk - BRB
            else:
                ap = Rk * math.cos(math.pi / sd)
                ang_n = (np.arange(sd) + .5) * 2 * np.pi / sd
                norms = np.stack([np.cos(ang_n), np.sin(ang_n)], 1)
                proj = norms @ q
                ii = int(np.argmax(proj))
                nq, dist, lim = norms[ii], proj[ii], ap - BRB
            if dist >= lim:
                ang = math.atan2(q[1], q[0])
                if in_gap(p, k, ang):
                    esc[k] = t
                    k += 1
                    if k == N:
                        end_t = t
                else:
                    cb, sb = math.cos(phi), math.sin(phi)
                    vq = np.array([c * v[0] - s_ * v[1], s_ * v[0] + c * v[1]])
                    if vq @ nq > 0:
                        vq = vq - 2 * (vq @ nq) * nq
                        j = rng.uniform(-0.02, 0.02)
                        cj, sj = math.cos(j), math.sin(j)
                        vq = np.array([cj * vq[0] - sj * vq[1], sj * vq[0] + cj * vq[1]])
                        v = np.array([cb * vq[0] - sb * vq[1], sb * vq[0] + cb * vq[1]])
                        q = q - nq * (dist - lim + 0.5)
                        pos_ = np.array([cb * q[0] - sb * q[1], sb * q[0] + cb * q[1]])
                        bounces.append((t, k, pos_[0], pos_[1], len(bounces)))
        step += 1
        if step % 8 == 0:
            pts.append(pos_.copy())
        if end_t is not None and t > end_t + 1.8:
            break
        if t > 70:
            return None
    return dict(pos=pts, esc=esc, bounces=bounces, end_t=end_t)


def best_sim(p, lo=18, hi=45, bmin=10, bmax=60):
    cand = None
    for i in range(120):
        S = sim(p, p["seed"] * 101 + i)
        if not S:
            continue
        nb = len(S["bounces"])
        if lo <= S["end_t"] <= hi and bmin <= nb <= bmax:
            return S
        if cand is None or abs(S["end_t"] - 28) < abs(cand["end_t"] - 28):
            cand = S
    if cand is None:
        raise RuntimeError("escape: no sim")
    return cand


def ring_pts(p, k, t, sc=1.0):
    Rk = p["radii"][k] * sc
    sd = p["sides"][k]
    phi = p["ph0"][k] + p["om"][k] * t
    gaps = sorted(p["gaps"][k], key=lambda g: g[0] % (2 * np.pi))
    segs = []
    n_g = len(gaps)
    for j in range(n_g):
        g0, w = gaps[j]
        g1, w1 = gaps[(j + 1) % n_g]
        u0 = g0 + w / 2
        u1 = g1 - w1 / 2
        while u1 <= u0:
            u1 += 2 * np.pi
        segs.append(np.linspace(u0, u1, 160))
    out, ends = [], []
    for u in segs:
        r = np.full_like(u, Rk) if sd == 0 else (Rk * math.cos(math.pi / sd)) / np.cos((u % (2 * np.pi)) - (np.floor((u % (2 * np.pi)) / (2 * np.pi / sd)) + .5) * 2 * np.pi / sd)
        out.append(np.stack([r * np.cos(u + phi) + CX, r * np.sin(u + phi) + CY], 1))
        for uu, rr in ((u[0], r[0]), (u[-1], r[-1])):
            ends.append((rr * math.cos(uu + phi) + CX, rr * math.sin(uu + phi) + CY))
    return out, ends


def make_bg(p):
    rng = np.random.default_rng(7)
    bg = gradient_bg(p["bg"][0], p["bg"][1])
    for _ in range(170):
        x, y = rng.integers(0, W), rng.integers(0, H)
        b = int(rng.integers(60, 170))
        cv2.circle(bg, (int(x), int(y)), int(rng.choice([0, 0, 1])), (b, b, b), -1, cv2.LINE_AA)
    return bg


def render_frame(p, S, fi, bg):
    t = fi / FPS
    N = p["N"]
    img = bg.copy()
    glow = np.zeros_like(img)
    esc_n = sum(1 for e in S["esc"] if e is not None and e <= t)
    bn = sum(1 for b in S["bounces"] if b[0] <= t)
    pb = bgr(p["ball"])
    for k in range(N):
        e = S["esc"][k]
        sc, br = 1.0, 1.0
        if e is not None and t >= e:
            tau = t - e
            if tau > 0.5:
                continue
            sc, br = 1 + 0.12 * tau / 0.5, 1 - tau / 0.5
        last = [b[0] for b in S["bounces"] if b[1] == k and b[0] <= t]
        if last:
            br *= 1 + 0.9 * max(0, 1 - (t - last[-1]) / 0.22)
        c = bgr(p["pal"][k])
        segs, ends = ring_pts(p, k, t, sc)
        for sg in segs:
            pi = (sg * 16).astype(np.int32)
            cv2.polylines(img, [pi], False, scale(c, min(1.0, br)), 3, cv2.LINE_AA, 4)
            cv2.polylines(glow, [pi], False, scale(c, min(1.0, br) * 0.35), 7, cv2.LINE_AA, 4)
        for ex, ey in ends:
            cv2.circle(img, (int(ex), int(ey)), 4, scale((235, 245, 255), min(1, br)), -1, cv2.LINE_AA)
    for b in S["bounces"]:
        tau = t - b[0]
        if 0 <= tau < 0.35:
            f = 1 - tau / 0.35
            for q in range(7):
                a = q * 2 * np.pi / 7 + b[4]
                r = 26 * tau / 0.35 + 3
                cv2.circle(glow, (int(b[2] + CX + r * math.cos(a)), int(b[3] + CY + r * math.sin(a))), 2, scale(pb, f), -1, cv2.LINE_AA)
    i = min(fi, len(S["pos"]) - 1)
    fade = 1.0
    if t > S["end_t"] + 0.9:
        fade = max(0, 1 - (t - S["end_t"] - 0.9) / 0.9)
    for q in range(1, 14):
        pp = S["pos"][max(0, i - q)]
        cv2.circle(glow, (int(pp[0] + CX), int(pp[1] + CY)), max(1, int(BRB * (1 - q / 18))), scale(pb, (1 - q / 14) * 0.6 * fade), -1, cv2.LINE_AA)
    pp = S["pos"][i]
    cv2.circle(glow, (int(pp[0] + CX), int(pp[1] + CY)), BRB + 5, scale(pb, 0.55 * fade), -1, cv2.LINE_AA)
    cv2.circle(img, (int(pp[0] + CX), int(pp[1] + CY)), BRB, scale(pb, fade), -1, cv2.LINE_AA)
    cv2.circle(img, (int(pp[0] + CX - 3), int(pp[1] + CY - 3)), 4, scale((255, 255, 255), fade), -1, cv2.LINE_AA)
    if 0 <= t - S["end_t"] < 1.0:
        tau = t - S["end_t"]
        cv2.circle(glow, (CX, CY), int(R_OUT * (0.5 + tau * 1.2)), scale(pb, (1 - tau) * 0.8), 5, cv2.LINE_AA)
    out = bloom(img, glow, 0.9)
    txt = [watermark_item(), (p["title"], 360, 120, 46, (255, 255, 255), 670),
           (f"{p['word']} {esc_n}/{N}   BOUNCES {bn}", 360, 178, 28, (255, 255, 255), 600)]
    if t >= S["end_t"]:
        txt.append(("ESCAPED!", 360, 232, 34, scale(p["ball"], 0.3 + 0.7 * min(1, (t - S["end_t"]) / 0.4)), 600))
    else:
        txt.append((p["sub"], 360, 232, 26, (205, 205, 215), 600))
    return draw_text(out, txt)


def audio(p, S, n):
    buf = np.zeros(int(n / FPS * SR) + SR // 2)
    add_pad(buf, p["pad"], 0.05)
    base = p["base"]
    for (t, k, x, y, idx) in S["bounces"]:
        add_tone(buf, t, pnote(idx % 8 + 2 * k, base), 0.7, 0.26, 0.2)
    for k, e in enumerate(S["esc"]):
        if e is None:
            continue
        last = k == p["N"] - 1
        for q, dg in enumerate([0, 2, 4, 7, 9, 12, 14] if last else [0, 2, 4, 7]):
            add_tone(buf, e + 0.07 * q, pnote(dg + 5 + k, base), 1.0, 0.24 if last else 0.18, 0.9 if last else 0.4)
        add_noise(buf, e, 0.3, 0.12, 0.08, seed=k, lp=0.4)
    return buf


def make(seed, base):
    p = gen_params(seed)
    S = best_sim(p)
    bg = make_bg(p)
    n = len(S["pos"])
    out = base + ".mp4"
    w = Writer(out)
    for fi in range(n):
        w.write(render_frame(p, S, fi, bg))
    w.close()
    finish(w, audio(p, S, n), out)
    return dict(kind="escape", question=p["title"].capitalize(), palette="layers", scale="pentatonic", instr="soft pluck",
                mapping=f"{p['N']} {p['layout']} layers", ball_style="comet", bg_style="stars", counts=[1],
                counts_text=f"1 ball escaping {p['N']} rotating layers ({p['layout']}) in {len(S['bounces'])} bounces",
                duration=round(n / FPS, 1), layout=p["layout"], thumb_t=round(S["end_t"] * 0.55, 2), points=[], kinds=["escape"])
