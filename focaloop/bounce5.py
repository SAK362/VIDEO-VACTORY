#!/usr/bin/env python3
"""Focaloop v5. Tiap video = 1 jenis pola dinding (acak) + urutan jumlah bola acak, durasi acak 30-90 dtk.
Aturan tetap: kecepatan bola TETAP, semua bola bertemu di satu titik pada satu waktu (Tm), fisika pantulan asli.
Pakai: python3 bounce5.py SEED out.mp4   (env DURATION untuk menimpa durasi saat uji)"""
import sys, json, math, subprocess, os, random, wave
import numpy as np, cv2
import bounce3 as b3
import bounce4 as b4
import patterns as P
from bounce3 import W, H, FPS, CX, CY, SR, SCALES, INSTR, hsv_bgr, pos_at, draw_ball, text_layer, pal

HOLD = 0.9
KINDS = [("ellipse", .22), ("circle", .06), ("sunburst", .20), ("spiral", .10), ("drop", .14), ("nested", .14), ("wavy", .14)]
RMAX = 335.0


def pick(r, pairs):
    x = r.random() * sum(w for _, w in pairs)
    for k, w in pairs:
        x -= w
        if x <= 0: return k
    return pairs[-1][0]


def gen_counts(r, nst):
    maxn = r.choice([4, 8, 16, 32, 64, 128, 256, 512, 512, 1024, 1024, 2048])
    mode = r.choice(["up", "updown", "wave", "jump", "steady", "plateau", "downup"])
    lg = math.log(maxn)
    def at(f): return max(1, int(round(math.exp(lg * min(max(f, 0), 1)))))
    cs = []
    for i in range(nst):
        f = i / max(nst - 1, 1)
        if mode == "up": c = at(f)
        elif mode == "updown": c = at(1 - abs(2 * f - 1))
        elif mode == "downup": c = at(abs(2 * f - 1))
        elif mode == "wave": c = at(0.5 + 0.5 * math.sin(2 * math.pi * f * r.choice([1, 2, 3]) - math.pi / 2))
        elif mode == "jump": c = at(r.random())
        elif mode == "steady": c = at(0.9) if i == 0 else cs[0]
        else: c = at(min(f * 3, 1))
        cs.append(c)
    return cs, mode, maxn


def gen_params(seed):
    base = b3.gen_params(int(seed))  # dipakai hanya untuk gaya visual/musik (hue, skala, alat musik, dll)
    p = {k: base[k] for k in ("seed", "hue0", "span", "question", "scale", "root", "instr", "mapping", "glow",
                              "wall_style", "ball_style", "line_style", "bg_style", "palette", "wall_hue_shift")}
    r = random.Random(seed * 2654435761 % (2 ** 32))
    dur = float(os.environ.get("DURATION", 0)) or round(r.uniform(30, 90), 1)
    kind = pick(r, KINDS)
    radial = kind in ("circle", "sunburst", "spiral", "wavy")
    Tm0 = r.uniform(1.15, 2.0)
    T0 = (Tm0 + HOLD) if radial else 2 * Tm0
    nst = max(3, int(round(dur / T0)))
    if radial: Tm = max(dur / nst - HOLD, 0.8)
    else: Tm = dur / nst / 2
    T = (Tm + HOLD) if radial else 2 * Tm
    counts, cmode, maxn = gen_counts(r, nst)
    morph = r.random() < 0.55 and kind != "circle"
    p.update(kind=kind, radial=radial, dur=dur, nst=nst, tmeet=Tm, T=T, counts=counts, count_mode=cmode, maxn=maxn,
             morph=morph, A=RMAX, chords=r.choice([[0, 4, 5, 3], [0, 5, 3, 4], [5, 3, 0, 4], [0, 3, 4, 3], [0, 2, 5, 4]]),
             wall_th=r.choice([2, 3, 3, 5]), sector=360.0)
    p["wall_hue"] = p["hue0"] + p["wall_hue_shift"]
    wr = random.Random(seed * 7 + 1)
    p["shape"] = gen_shape(kind, wr)
    p["stages"] = []
    for s in range(nst):
        shp = gen_shape(kind, random.Random(seed * 131 + s)) if morph else p["shape"]
        sec = 360.0
        if kind in ("ellipse", "nested") and wr.random() < 0.25: sec = wr.uniform(140, 300)
        p["stages"].append(dict(n=counts[s], hue=0.012 * s + wr.uniform(-.03, .03), shape=shp, sector=sec,
                                rot=wr.uniform(0, 2 * math.pi)))
    if kind in ("ellipse", "nested"): p["sector"] = p["stages"][0]["sector"]
    return p


def gen_shape(kind, r):
    A = RMAX
    if kind == "ellipse":
        e = 0.0 if r.random() < .06 else r.uniform(0.12, 0.93)
        return dict(e=e, phi=r.uniform(0, math.pi))
    if kind == "circle": return dict()
    if kind in ("sunburst", "spiral", "wavy"):
        ns = r.choice([3, 4, 5, 6, 8, 10, 12, 16, 24, 36])
        lo = r.uniform(0.38, 0.85)
        if kind == "sunburst":
            if r.random() < 0.5:
                a, b = r.sample([1.0, lo, (1 + lo) / 2], 2); rad = [a if i % 2 == 0 else b for i in range(ns - ns % 2 or ns)]
                if ns % 2: rad = [r.choice([1.0, lo, (1 + lo) / 2]) for _ in range(ns)]
            else: rad = [r.choice([lo, (1 + lo) / 2, 1.0, 1.0]) for _ in range(ns)]
        elif kind == "spiral":
            ns = max(ns, 8); rad = [lo + (1 - lo) * s / (ns - 1) for s in range(ns)]
            if r.random() < .5: rad = rad[::-1]
        else:
            ns = max(ns, 12); ph = r.uniform(0, 6.28); k = r.choice([1, 2, 3, 4, 5])
            rad = [lo + (1 - lo) * (0.5 + 0.5 * math.sin(ph + 2 * math.pi * k * s / ns)) for s in range(ns)]
        m = max(rad); rad = [x / m * RMAX for x in rad]
        return dict(radii=rad)
    if kind == "drop":
        u = r.uniform(0.5, 0.9); e = r.uniform(0.15, 0.9 * u)
        return dict(e=e, phi=r.uniform(0, 2 * math.pi), u=u)
    if kind == "nested":
        odds = r.choice([[1, 3], [1, 3], [1, 3, 5], [1, 5]])
        emax = 0.9 / max(odds) * 0.96
        return dict(odds=odds, e=r.uniform(0.04, emax), phi=r.uniform(0, math.pi))
    raise ValueError(kind)


def bg_only(p):
    q = dict(p); q["wall_style"] = "none"
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
    return base


def drop_wall(ak, bk, sec, steps, phi, col, th):
    def fn(img):
        cs, sn = math.cos(phi), math.sin(phi)
        for k in range(len(ak)):
            pts = []
            for q in range(2400):
                t = 2 * math.pi * q / 2400; x, y = ak[k] * math.cos(t), bk[k] * math.sin(t)
                wx, wy = CX + x * cs - y * sn, CY + x * sn + y * cs
                if sec(wx, wy) == k: pts.append((wx, wy))
                else:
                    if len(pts) > 1: P.draw_poly(img, pts, col, th)
                    pts = []
            if len(pts) > 1: P.draw_poly(img, pts, col, th)
        for (x0, y0), (x1, y1) in steps: cv2.line(img, (int(x0), int(y0)), (int(x1), int(y1)), col, th, cv2.LINE_AA)
    return fn


def build_stage(p, st, n, Tend):
    """-> paths, wall_fn(col,th), meets[(t,(x,y))], start(x,y). Semua jenis menjaga: kecepatan tetap v, bertemu di satu titik."""
    A = p["A"]; Tm = p["tmeet"]; v = 2 * A / Tm; kind = p["kind"]; shp = st["shape"]
    col = hsv_bgr(p["wall_hue"] + st["hue"], 0.75, 1.0); th = p["wall_th"]
    if kind == "ellipse":
        e, phi = shp["e"], shp["phi"]; c = A * e; B = math.sqrt(A * A - c * c)
        paths, f1 = P.paths_ellipse(A, phi, e, n, v, Tend, st["sector"], st["rot"])
        f2 = (2 * CX - f1[0], 2 * CY - f1[1])
        return paths, P.wall_ellipses([(A, B, phi)], col, th), [(Tm, f2), (2 * Tm, f1)], f1
    if kind == "nested":
        e, phi, odds = shp["e"], shp["phi"], shp["odds"]; c = A * e
        ag = [A / o for o in odds]
        paths, f1 = P.paths_ellipse(A, phi, e, n, v, Tend, st["sector"], st["rot"], groups=ag)
        f2 = (2 * CX - f1[0], 2 * CY - f1[1])
        items = [(a, math.sqrt(a * a - c * c), phi) for a in ag]
        return paths, P.wall_ellipses(items, col, th), [(Tm, f2), (2 * Tm, f1)], f1
    if kind == "drop":
        e, phi, u = shp["e"], shp["phi"], shp["u"]
        paths, f1, ak, bk, steps, sec, c, amax = P.paths_petal(A, phi, e, [1, u], 2, phi, n, v, Tend)
        f2 = (2 * CX - f1[0], 2 * CY - f1[1])
        return paths, drop_wall(ak, bk, sec, steps, phi, col, th), [(Tm, f2)], f1
    # radial
    if kind == "circle": radii = [A]
    else: radii = shp["radii"]
    ns = len(radii); rmax = max(radii)
    def rad(a): return radii[int(((a % (2 * math.pi)) / (2 * math.pi)) * ns) % ns]
    paths = P.paths_radial(rad, n, v * rmax / A if False else 2 * rmax / Tm, Tend, lambda t_: 2 * (rmax - rad(t_)) / (2 * rmax / Tm))
    wf = P.wall_ellipses([(A, A, 0.0), (A - 14, A - 14, 0.0)], col, th) if kind == "circle" else P.wall_sectors(radii, col, th)
    return paths, wf, [(Tm, (CX, CY))], (CX, CY)


def hits_of(paths, start, Tend):
    out = []
    sx, sy = start
    for pa in paths:
        for j in range(1, len(pa) - 1):
            t, x, y = pa[j]
            if t <= Tend and (x - sx) ** 2 + (y - sy) ** 2 > 25: out.append((t, x, y))
    return out


def check_meet(paths, meets, tol=1.5):
    worst = 0.0
    for tm, (fx, fy) in meets:
        for pa in paths[:: max(1, len(paths) // 40)]:
            x, y, _ = pos_at(pa, tm); worst = max(worst, math.hypot(x - fx, y - fy))
    return worst


def build_audio(stage_hits, stage_meets, p, total):
    T = p["T"]; tm = p["tmeet"]
    N = int(total * SR) + SR
    L = np.zeros(N, np.float32); R = np.zeros(N, np.float32)
    ins = INSTR[p["instr"]]; sc = SCALES[p["scale"]]; nl = len(sc)
    rng = random.Random(p["seed"] + 7)
    def freq(idx):
        o, dg = divmod(idx, nl); return 440.0 * 2 ** ((p["root"] + 12 * o + sc[dg] - 69) / 12)
    grid = tm / 24; walk = 7; A = p["A"]
    for s, hits in enumerate(stage_hits):
        off = s * T
        cdeg = p["chords"][s % len(p["chords"])] % nl
        chord = [cdeg, cdeg + 2, cdeg + 4]
        pl = int((T + 0.4) * SR); t = np.arange(pl) / SR
        env = np.minimum(t / 0.6, 1.0) * np.minimum((T + 0.4 - t) / 0.6, 1.0)
        for ci, idx in enumerate(chord):
            f = freq(idx - nl)
            w = (np.sin(2 * math.pi * f * t) + np.sin(2 * math.pi * f * 1.004 * t + 1.3)) * 0.5 * env * 0.07
            i0 = int(off * SR); seg = min(pl, N - i0)
            if seg <= 0: continue
            pan = (-0.5, 0.0, 0.5)[ci]
            gl, gr = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
            L[i0:i0 + seg] += (w[:seg] * gl).astype(np.float32); R[i0:i0 + seg] += (w[:seg] * gr).astype(np.float32)
        buckets = {}
        for th, x, y in hits:
            if th <= T: buckets.setdefault(int(th / grid), []).append((x, y))
        cands = [c + nl * o for c in chord for o in range(0, 3)]
        for k in sorted(buckets):
            pts = buckets[k]; mx = np.mean([q[0] for q in pts]); my = np.mean([q[1] for q in pts])
            if p["mapping"] == "x": idx = int(np.clip((mx - (CX - A)) / (2 * A), 0, .999) * 2 * nl)
            elif p["mapping"] == "angle": idx = int(((math.atan2(my - CY, mx - CX) + math.pi) / (2 * math.pi)) * 2 * nl)
            else:
                walk = int(np.clip(walk + rng.choice([-2, -1, -1, 1, 1, 2]), 0, 2 * nl)); idx = walk
            if rng.random() < 0.55: idx = min(cands, key=lambda c: abs(c - idx))
            n = len(pts); amp = 0.26 / math.sqrt(n) * min(1.0, 0.5 + 0.1 * math.sqrt(n))
            pan = float(np.clip((mx - CX) / A, -1, 1)) * 0.8
            b4.tone(L, R, off + k * grid, freq(idx), amp, ins, pan)
            if n > 12: b4.tone(L, R, off + k * grid, freq(idx) / 2, amp * 0.5, ins, pan * 0.5)
        for tmt in stage_meets[s]:
            tt = off + tmt
            rl = int(min(0.8, tm * 0.9) * SR); tr = np.arange(rl) / SR; d = rl / SR
            ph = 2 * math.pi * (350 * tr + (1050 / (2 * d)) * tr ** 2)
            w = 0.10 * (tr / d) ** 2 * np.sin(ph); i0 = int((tt - d) * SR)
            if i0 >= 0 and i0 + rl <= N:
                L[i0:i0 + rl] += w.astype(np.float32); R[i0:i0 + rl] += w.astype(np.float32)
            bl = int(0.9 * SR); tb = np.arange(bl) / SR
            ph = 2 * math.pi * (45 * tb + 80 * (1 - np.exp(-14 * tb)) / 14)
            w = 0.45 * np.exp(-tb * 5) * np.sin(ph); i0 = int(tt * SR); seg = min(bl, N - i0)
            if seg > 0:
                L[i0:i0 + seg] += w[:seg].astype(np.float32); R[i0:i0 + seg] += w[:seg].astype(np.float32)
            for ci, idx in enumerate(chord):
                b4.tone(L, R, tt, freq(idx + nl), 0.16, INSTR["bell"], (-0.6, 0.0, 0.6)[ci])
    L = b4.reverb(L, p["seed"] + 1, 2.2, 0.28); R = b4.reverb(R, p["seed"] + 2, 2.2, 0.28)
    st = np.stack([L, R], 1)
    st = np.tanh(1.4 * st) / math.tanh(1.4)
    st /= (np.max(np.abs(st)) or 1); st *= 0.9
    nn = int(total * SR); st = st[:nn]
    fo = int(0.5 * SR); st[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return st


def main(seed, out_path):
    p = gen_params(int(seed)); T = p["T"]; Tm = p["tmeet"]; nst = p["nst"]; total = T * nst
    fpp = int(round(T * FPS)); bg = bg_only(p)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    tv, ta = out_path + ".v.mp4", out_path + ".a.wav"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", tv], stdin=subprocess.PIPE)
    stage_hits, stage_meets = [], []; worst_all = 0.0
    for s, st in enumerate(p["stages"]):
        n = st["n"]
        paths, wall_fn, meets, start = build_stage(p, st, n, T + 0.25)
        worst = check_meet(paths, meets); worst_all = max(worst_all, worst)
        if worst > 2.0: raise RuntimeError(f"aturan titik temu dilanggar: stage {s} selisih {worst:.2f}px kind={p['kind']}")
        hits = hits_of(paths, start, T + 0.25); stage_hits.append(hits); stage_meets.append([m[0] for m in meets])
        hits_a = np.array(sorted(hits)) if hits else np.zeros((0, 3))
        wall = np.zeros((H, W, 3), np.uint8); wall_fn(wall)
        gs = {5: 11, 2: 4}.get(p["wall_th"], 7)
        gl = cv2.GaussianBlur(wall, (0, 0), gs)
        sbase = cv2.add(bg, cv2.add(wall, (gl * 1.2).clip(0, 255).astype(np.uint8)))
        ps = dict(p); ps["hue0"] = p["hue0"] + st["hue"]
        cols = [pal(ps, i, n) for i in range(n)]
        tcol, talpha = text_layer(p["question"], f"{n:,} ball" + ("s" if n > 1 else ""))
        lines = np.zeros((H, W, 3), np.uint8)
        gain = 0.55 if n < 100 else (0.22 if n < 800 else 0.10); hr = 4 if n < 100 else (3 if n < 800 else 2)
        ls = p["line_style"]; gain = min(gain * (1.8 if ls == "bright" else (2.2 if ls == "fade" else 1.0)), 0.85)
        wallcol = hsv_bgr(p["wall_hue"] + st["hue"], 0.75, 1.0)
        last = [(pa[0, 1], pa[0, 2], 0) for pa in paths]
        for fr in range(fpp):
            t = fr / FPS; heads = np.zeros((H, W, 3), np.uint8)
            if ls == "fade": lines = cv2.convertScaleAbs(lines, alpha=0.95)
            for i, pa in enumerate(paths):
                x, y, k = pos_at(pa, t); lx, ly, lk = last[i]; c = tuple(int(q * gain) for q in cols[i]); qx, qy = lx, ly
                for kk in range(lk + 1, k + 1):
                    cv2.line(lines, (int(qx), int(qy)), (int(pa[kk, 1]), int(pa[kk, 2])), c, 1, cv2.LINE_AA); qx, qy = pa[kk, 1], pa[kk, 2]
                cv2.line(lines, (int(qx), int(qy)), (int(x), int(y)), c, 1, cv2.LINE_AA)
                last[i] = (x, y, k); draw_ball(heads, x, y, hr, cols[i], p, pa, t, n)
            if len(hits_a):
                a, b = np.searchsorted(hits_a[:, 0], [t - 0.12, t + 1e-9])
                if b > a:
                    sel = hits_a[a:b]
                    if len(sel) > 260: sel = sel[::len(sel) // 260 + 1]
                    for th_, hx, hy in sel:
                        k_ = 1 - (t - th_) / 0.12
                        cv2.circle(heads, (int(hx), int(hy)), 3, tuple(int(q * k_) for q in wallcol), -1, cv2.LINE_AA)
            for tmt, (fx, fy) in meets:
                dtm = t - tmt
                if 0 <= dtm < 0.9:
                    k_ = 1 - dtm / 0.9
                    cv2.circle(heads, (int(fx), int(fy)), int(8 + dtm * 260), tuple(int(q * k_ * 0.9) for q in (255, 255, 255)), 2, cv2.LINE_AA)
                    cv2.circle(heads, (int(fx), int(fy)), int(6 + dtm * 120), tuple(int(q * k_) for q in cols[0]), 2, cv2.LINE_AA)
            g1 = cv2.GaussianBlur(heads, (0, 0), 6); g2 = cv2.GaussianBlur(heads, (0, 0), 2)
            f = cv2.add(cv2.add(b3.bg_frame(sbase, p, s * T + t), lines), heads)
            f = cv2.add(f, (g1 * 1.8 * p["glow"]).clip(0, 255).astype(np.uint8)); f = cv2.add(f, (g2 * .8).clip(0, 255).astype(np.uint8))
            f[:230] = (f[:230].astype(np.float32) * (1 - talpha) + tcol * talpha).clip(0, 255).astype(np.uint8)
            ff.stdin.write(f.tobytes())
        print("stage", s + 1, "/", nst, n, f"dev={worst:.2f}", flush=True)
    ff.stdin.close(); ff.wait()
    au = build_audio(stage_hits, stage_meets, p, total)
    with wave.open(ta, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((au * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tv, "-i", ta, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_path], check=True)
    os.remove(tv); os.remove(ta)
    p["total"] = total; p["worst_dev"] = worst_all
    json.dump(p, open(out_path.rsplit(".", 1)[0] + ".json", "w"), indent=1)
    print("OK", out_path, p["kind"], round(total, 1), p["count_mode"], p["maxn"], f"worst={worst_all:.3f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
