#!/usr/bin/env python3
"""Focaloop v6. Bola keluar dari 1-5 titik awal -> kena dinding -> kembali ke titik itu serentak -> jeda -> tahap baru
dengan jumlah bola lebih banyak (SELALU dari sedikit ke banyak). Kecepatan bola tetap sepanjang video. Durasi 30-90 dtk.
Pakai: python3 bounce6.py SEED out.mp4  (env DURATION untuk uji)"""
import sys, json, math, subprocess, os, random, wave
import numpy as np, cv2
import bounce3 as b3
import bounce4 as b4
import bounce5 as b5
import multi as M
from bounce3 import W, H, FPS, CX, CY, SR, SCALES, INSTR, hsv_bgr, pos_at, draw_ball, text_layer, pal

HOLD = 0.7


def gen_params(seed):
    base = b3.gen_params(int(seed))
    p = {k: base[k] for k in ("seed", "hue0", "span", "question", "scale", "root", "instr", "mapping", "glow",
                              "ball_style", "line_style", "bg_style", "palette", "wall_hue_shift")}
    r = random.Random(seed * 2654435761 % (2 ** 32))
    dur = float(os.environ.get("DURATION", 0)) or round(r.uniform(30, 90), 1)
    dur = min(max(dur, 30.0), 90.0) if not os.environ.get("DURATION") else dur
    k0 = r.randint(1, 5); vary = r.random() < 0.3; morph = vary or r.random() < 0.5
    tavg = r.uniform(1.6, 3.4)
    nst = max(3, int(round(dur / (tavg + HOLD))))
    maxtot = r.choice([8, 12, 16, 24, 32, 48, 64, 100, 160, 256, 400, 640, 1000, 1500])
    lg = math.log(maxtot); rate = r.choice([1.0, 1.0, 1.3, 1.7])
    stages = []; fixed = M.gen_systems(random.Random(seed * 7 + 1), k0); prev = 0
    for s in range(nst):
        f = s / max(nst - 1, 1)
        if morph or vary:
            rs = random.Random(seed * 131 + s); k = rs.randint(1, 5) if vary else k0
            systems = M.gen_systems(rs, k)
        else: systems = fixed
        k = sum(sy["sources"] for sy in systems)
        target = 1.0 if s == 0 else math.exp(lg * min(1.0, f * rate))
        nper = max(1, int(round(target / k)))
        if nper * k < prev: nper = int(math.ceil(prev / k))
        prev = nper * k
        Lmax = max(sy["Lmax"] for sy in systems)
        stages.append(dict(nper=nper, k=k, n=nper * k, systems=systems, Lmax=Lmax, hue=0.012 * s))
    v = sum(st["Lmax"] for st in stages) / max(dur - nst * HOLD, 1.0)
    off = 0.0
    for st in stages:
        st["Tret"] = st["Lmax"] / v; st["T"] = st["Tret"] + HOLD; st["off"] = off; off += st["T"]
    p.update(dur=dur, nst=nst, v=v, stages=stages, total=off, morph=morph, vary=vary, k0=k0, maxtot=maxtot,
             counts=[st["n"] for st in stages], kinds=sorted({sy["name"] for st in stages for sy in st["systems"]}),
             chords=r.choice([[0, 4, 5, 3], [0, 5, 3, 4], [5, 3, 0, 4], [0, 3, 4, 3], [0, 2, 5, 4]]),
             wall_th=r.choice([2, 3, 3, 5]), A=M.RMAX)
    p["wall_hue"] = p["hue0"] + p["wall_hue_shift"]
    return p


def build_stage(p, st):
    paths, meets, worst = M.stage_paths(st["systems"], st["nper"], p["v"], st["Lmax"], st["Tret"])
    return paths, meets, worst


def hits_of(paths, Tmax):
    out = []
    for pa in paths:
        for j in range(2, len(pa) - 2):
            t, x, y = pa[j]
            if t <= Tmax: out.append((t, x, y))
    return out


def build_audio(stage_hits, stage_meets, p, total):
    N = int(total * SR) + SR
    L = np.zeros(N, np.float32); R = np.zeros(N, np.float32)
    ins = INSTR[p["instr"]]; sc = SCALES[p["scale"]]; nl = len(sc)
    rng = random.Random(p["seed"] + 7); A = M.RMAX
    def freq(idx):
        o, dg = divmod(idx, nl); return 440.0 * 2 ** ((p["root"] + 12 * o + sc[dg] - 69) / 12)
    grid = 0.06; walk = 7
    for s, hits in enumerate(stage_hits):
        st = p["stages"][s]; off = st["off"]; T = st["T"]
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
        for tmt in stage_meets[s][-2:]:
            tt = off + tmt
            rl = int(min(0.8, max(tmt * 0.9, 0.2)) * SR); tr = np.arange(rl) / SR; d = rl / SR
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
    st_ = np.stack([L, R], 1)
    st_ = np.tanh(1.4 * st_) / math.tanh(1.4)
    st_ /= (np.max(np.abs(st_)) or 1); st_ *= 0.9
    nn = int(total * SR); st_ = st_[:nn]
    fo = int(0.5 * SR); st_[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return st_


def main(seed, out_path):
    p = gen_params(int(seed)); nst = p["nst"]; total = p["total"]; bg = b5.bg_only(p)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    tv, ta = out_path + ".v.mp4", out_path + ".a.wav"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", tv], stdin=subprocess.PIPE)
    stage_hits, stage_meets = [], []; worst_all = 0.0; gs = {5: 11, 2: 4}.get(p["wall_th"], 7)
    for s, st in enumerate(p["stages"]):
        T = st["T"]; fpp = int(round(T * FPS)); n = st["n"]
        paths, meets, worst = build_stage(p, st); worst_all = max(worst_all, worst)
        if worst > 2.0: raise RuntimeError(f"aturan titik kembali dilanggar: stage {s} selisih {worst:.2f}px")
        hits = hits_of(paths, T); stage_hits.append(hits); stage_meets.append([m[0] for m in meets])
        hits_a = np.array(sorted(hits)) if hits else np.zeros((0, 3))
        wall = np.zeros((H, W, 3), np.uint8)
        for si, sy in enumerate(st["systems"]):
            M.draw_system(sy, wall, hsv_bgr(p["wall_hue"] + st["hue"] + 0.11 * si, 0.75, 1.0), p["wall_th"])
        gl = cv2.GaussianBlur(wall, (0, 0), gs)
        sbase = cv2.add(bg, cv2.add(wall, (gl * 1.2).clip(0, 255).astype(np.uint8)))
        ps = dict(p); ps["hue0"] = p["hue0"] + st["hue"]
        cols = [pal(ps, i, n) for i in range(n)]
        tcol, talpha = text_layer(p["question"], f"{n:,} ball" + ("s" if n > 1 else "") + (f" · {st['k']} points" if st["k"] > 1 else " · 1 point"))
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
            for tmt, pts_ in meets:
                dtm = t - tmt
                if 0 <= dtm < 0.9:
                    k_ = 1 - dtm / 0.9
                    for (fx, fy) in pts_:
                        cv2.circle(heads, (int(fx), int(fy)), int(8 + dtm * 220), tuple(int(q * k_ * 0.9) for q in (255, 255, 255)), 2, cv2.LINE_AA)
                        cv2.circle(heads, (int(fx), int(fy)), int(6 + dtm * 110), tuple(int(q * k_) for q in cols[0]), 2, cv2.LINE_AA)
            g1 = cv2.GaussianBlur(heads, (0, 0), 6); g2 = cv2.GaussianBlur(heads, (0, 0), 2)
            f = cv2.add(cv2.add(b3.bg_frame(sbase, p, st["off"] + t), lines), heads)
            f = cv2.add(f, (g1 * 1.8 * p["glow"]).clip(0, 255).astype(np.uint8)); f = cv2.add(f, (g2 * .8).clip(0, 255).astype(np.uint8))
            f[:230] = (f[:230].astype(np.float32) * (1 - talpha) + tcol * talpha).clip(0, 255).astype(np.uint8)
            ff.stdin.write(f.tobytes())
        print("stage", s + 1, "/", nst, n, f"k={st['k']} dev={worst:.2f}", flush=True)
    ff.stdin.close(); ff.wait()
    au = build_audio(stage_hits, stage_meets, p, total)
    with wave.open(ta, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((au * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tv, "-i", ta, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_path], check=True)
    os.remove(tv); os.remove(ta)
    p["worst_dev"] = worst_all
    json.dump(p, open(out_path.rsplit(".", 1)[0] + ".json", "w"), indent=1, default=lambda o: list(o) if isinstance(o, (set, tuple)) else str(o))
    print("OK", out_path, round(total, 1), "k0", p["k0"], p["kinds"], f"worst={worst_all:.3f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
