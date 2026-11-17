#!/usr/bin/env python3
"""Focaloop v4: video panjang (maks 90 dtk), lapisan kecepatan (odd multiples), riak di titik temu,
kilatan dinding, cincin confocal dekoratif, musik berlapis (pad akord, arpeggio, bass, riser, reverb, stereo).
Fisika tetap elips murni -> semua bola selalu bertemu di fokus lain pada t=tmeet (kelipatan ganjil) dan kembali di fokus awal pada t=2*tmeet.
Pakai: python3 bounce4.py SEED out.mp4"""
import sys, json, math, subprocess, os, random, wave
import numpy as np, cv2
import bounce3 as b3
from bounce3 import (W, H, FPS, CX, CY, SR, SCALES, INSTR, make_hit, pos_at, hsv_bgr, build_base,
                     draw_ball, text_layer, pal)

MAX_DUR = 90.0


def gen_params(seed):
    p = b3.gen_params(int(seed))
    r = random.Random(seed * 104729 + 7)
    dur = min(float(os.environ.get("DURATION", MAX_DUR)), MAX_DUR)
    nst = max(8, round(dur / (2 * p["tmeet"])))
    p["tmeet"] = dur / nst / 2          # total = persis dur
    maxn = r.choice([256, 512, 512, 1024])
    fac = 2 if nst >= 20 else 4
    up, n = [], 1
    while n < maxn: up.append(n); n *= fac
    up.append(maxn)
    down = up[-2::-1]
    mid_len = max(nst - len(up) - len(down), 0)
    top = [c for c in up if c >= maxn // 4] or [maxn]
    counts = list(up)
    for _ in range(mid_len): counts.append(r.choice(top))
    counts += down
    counts = counts[:nst] if len(counts) > nst else counts + [1] * (nst - len(counts))
    stages = []
    for i, n in enumerate(counts):
        v = "plain"
        if n >= 8:
            v = r.choice(["plain", "multi", "multi", "sector", "multi_sector"])
        mults = [1]
        if "multi" in v: mults = r.choice([[1, 3], [1, 3, 5], [1, 3, 3, 5], [1, 5]])
        sector = 360.0
        if "sector" in v: sector = r.uniform(140, 300)
        stages.append(dict(n=n, variant=v, mults=mults, sector=sector, rot=r.uniform(0, 2 * math.pi),
                           hue=r.uniform(-0.05, 0.05) + 0.015 * i))
    p["stages"] = stages
    p["counts"] = [s["n"] for s in stages]
    p["rings"] = r.choice([0, 1, 2, 3])
    p["chords"] = r.choice([[0, 4, 5, 3], [0, 5, 3, 4], [5, 3, 0, 4], [0, 3, 4, 3], [0, 2, 5, 4]])
    p["duration"] = dur
    return p


def simulate(hit, start, n, speed, T, sector, rot, mults):
    paths, hits = [], []
    for i in range(n):
        ang = rot + (math.radians(sector) * (i + 0.5) / n)
        sp = speed * mults[i % len(mults)]
        vx, vy = sp * math.cos(ang), sp * math.sin(ang)
        px, py = start; t = 0.0; pts = [(0.0, px, py)]; g = 0
        while t < T and g < 200:
            dt, hx, hy, nx, ny = hit(px, py, vx, vy)
            t += dt; pts.append((t, hx, hy)); hits.append((t, hx, hy))
            d = vx * nx + vy * ny; vx, vy = vx - 2 * d * nx, vy - 2 * d * ny
            px, py = hx - nx * 1e-3, hy - ny * 1e-3; g += 1
        pts.append((t + 10, px + vx * 10, py + vy * 10)); paths.append(np.array(pts))
    return paths, hits


def ring_layer(p, to_world):
    lay = np.zeros((H, W, 3), np.uint8)
    A, c, ph = p["A"], p["c"], math.degrees(p["phi"])
    for j in range(1, p["rings"] + 1):
        a2 = A * (1 - 0.13 * j)
        if a2 <= c * 1.12: break
        b2 = math.sqrt(a2 * a2 - c * c)
        col = hsv_bgr(p["hue0"] + p["wall_hue_shift"] + 0.08 * j, 0.6, 0.55)
        cv2.ellipse(lay, (CX, CY), (int(a2), int(b2)), ph, 0, 360, col, 1, cv2.LINE_AA)
    return cv2.add(lay, cv2.GaussianBlur(lay, (0, 0), 4)) if p["rings"] else lay


# ---------- audio ----------
def tone(L, R, t0, freq, amp, ins, pan):
    i0 = int(t0 * SR)
    if i0 >= len(L) or i0 < 0: return
    n = min(int(ins["dur"] * SR), len(L) - i0); t = np.arange(n) / SR
    w = sum(a * np.exp(-t * dc) * np.sin(2 * math.pi * freq * r * t) for r, a, dc in ins["p"] if freq * r < 9000)
    w = amp * np.minimum(t / ins["att"], 1.0) * w
    gl, gr = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    L[i0:i0 + n] += (w * gl).astype(np.float32); R[i0:i0 + n] += (w * gr).astype(np.float32)


def reverb(x, seed, secs=1.8, wet=0.24):
    rg = np.random.RandomState(seed)
    n = int(secs * SR); t = np.arange(n) / SR
    ir = rg.randn(n) * np.exp(-t * 3.2); ir = np.convolve(ir, np.ones(8) / 8, mode="same")
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    m = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[:len(x)]
    return x + wet * y.astype(np.float32)


def build_audio(stage_hits, T, p, total):
    N = int(total * SR) + SR
    L = np.zeros(N, np.float32); R = np.zeros(N, np.float32)
    ins = INSTR[p["instr"]]; sc = SCALES[p["scale"]]; nl = len(sc)
    rng = random.Random(p["seed"] + 7); tm = p["tmeet"]
    def freq(idx):
        o, dg = divmod(idx, nl); return 440.0 * 2 ** ((p["root"] + 12 * o + sc[dg] - 69) / 12)
    grid = tm / 24; walk = 7
    for s, hits in enumerate(stage_hits):
        off = s * T
        cdeg = p["chords"][s % len(p["chords"])] % nl
        chord = [cdeg, cdeg + 2, cdeg + 4]
        # pad (akord panjang, halus)
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
        # not per pantulan, dikuantisasi
        buckets = {}
        for th, x, y in hits:
            if th <= T: buckets.setdefault(int(th / grid), []).append((x, y))
        cands = [c + nl * o for c in chord for o in range(0, 3)]
        for k in sorted(buckets):
            pts = buckets[k]; mx = np.mean([q[0] for q in pts]); my = np.mean([q[1] for q in pts])
            if p["mapping"] == "x": idx = int(np.clip((mx - (CX - p["A"])) / (2 * p["A"]), 0, .999) * 2 * nl)
            elif p["mapping"] == "angle": idx = int(((math.atan2(my - CY, mx - CX) + math.pi) / (2 * math.pi)) * 2 * nl)
            else:
                walk = int(np.clip(walk + rng.choice([-2, -1, -1, 1, 1, 2]), 0, 2 * nl)); idx = walk
            if rng.random() < 0.55: idx = min(cands, key=lambda c: abs(c - idx))
            n = len(pts); amp = 0.28 / math.sqrt(n) * min(1.0, 0.5 + 0.1 * math.sqrt(n))
            pan = float(np.clip((mx - CX) / max(p["A"], 1), -1, 1)) * 0.8
            tone(L, R, off + k * grid, freq(idx), amp, ins, pan)
            if n > 12: tone(L, R, off + k * grid, freq(idx) / 2, amp * 0.5, ins, pan * 0.5)
        # momen temu: riser + boom + kilau akord
        for mi in (1, 2):
            tt = off + mi * tm
            rl = int(min(0.8, tm * 0.9) * SR); tr = np.arange(rl) / SR; d = rl / SR
            ph = 2 * math.pi * (350 * tr + (1050 / (2 * d)) * tr ** 2)
            w = 0.10 * (tr / d) ** 2 * np.sin(ph); i0 = int((tt - d) * SR)
            if i0 >= 0 and i0 + rl <= N:
                L[i0:i0 + rl] += w.astype(np.float32); R[i0:i0 + rl] += w.astype(np.float32)
            bl = int(0.9 * SR); tb = np.arange(bl) / SR
            ph = 2 * math.pi * (45 * tb + 80 * (1 - np.exp(-14 * tb)) / 14)
            w = 0.5 * np.exp(-tb * 5) * np.sin(ph); i0 = int(tt * SR); seg = min(bl, N - i0)
            if seg > 0:
                L[i0:i0 + seg] += w[:seg].astype(np.float32); R[i0:i0 + seg] += w[:seg].astype(np.float32)
            for ci, idx in enumerate(chord):
                tone(L, R, tt, freq(idx + nl), 0.16, INSTR["bell"], (-0.6, 0.0, 0.6)[ci])
    L = reverb(L, p["seed"] + 1); R = reverb(R, p["seed"] + 2)
    st = np.stack([L, R], 1)
    st = np.tanh(1.4 * st) / math.tanh(1.4)
    st /= (np.max(np.abs(st)) or 1); st *= 0.9
    nn = int(total * SR); st = st[:nn]
    fo = int(0.4 * SR); st[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return st


def main(seed, out_path):
    p = gen_params(int(seed)); hit, to_world = make_hit(p)
    f1 = to_world(*p["lp"]); f2 = to_world(-p["lp"][0], 0.0)
    start = f1; speed = 2 * p["A"] / p["tmeet"]; T = 2 * p["tmeet"]; tm = p["tmeet"]
    base = build_base(p); nst = len(p["stages"]); total = T * nst; fpp = int(round(T * FPS))
    rings = ring_layer(p, to_world); beat = tm / 4
    wallcol = hsv_bgr(p["hue0"] + p["wall_hue_shift"], 0.75, 1.0)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    tv, ta = out_path + ".v.mp4", out_path + ".a.wav"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", tv], stdin=subprocess.PIPE)
    stage_hits = []
    for s, st in enumerate(p["stages"]):
        n = st["n"]
        paths, hits = simulate(hit, start, n, speed, T + 0.2, st["sector"], st["rot"], st["mults"]); stage_hits.append(hits)
        hits_a = np.array(sorted(hits)) if hits else np.zeros((0, 3))
        ps = dict(p); ps["hue0"] = p["hue0"] + st["hue"]
        cols = [pal(ps, i, n) for i in range(n)]
        lab = f"{n:,} ball" + ("s" if n > 1 else "")
        tcol, talpha = text_layer(p["question"], lab)
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
            # kilatan dinding saat bola memantul
            if len(hits_a):
                a, b = np.searchsorted(hits_a[:, 0], [t - 0.12, t + 1e-9])
                if b > a:
                    sel = hits_a[a:b]
                    if len(sel) > 260: sel = sel[::len(sel) // 260 + 1]
                    for th, hx, hy in sel:
                        k_ = 1 - (t - th) / 0.12
                        cv2.circle(heads, (int(hx), int(hy)), 3, tuple(int(v * k_) for v in wallcol), -1, cv2.LINE_AA)
            # riak di titik temu
            for tmt, (fx, fy) in ((tm, f2), (2 * tm, f1)):
                dtm = t - tmt
                if 0 <= dtm < 0.9:
                    k_ = 1 - dtm / 0.9
                    cv2.circle(heads, (int(fx), int(fy)), int(8 + dtm * 260), tuple(int(v * k_ * 0.9) for v in (255, 255, 255)), 2, cv2.LINE_AA)
                    cv2.circle(heads, (int(fx), int(fy)), int(6 + dtm * 120), tuple(int(v * k_) for v in cols[0]), 2, cv2.LINE_AA)
            g1 = cv2.GaussianBlur(heads, (0, 0), 6); g2 = cv2.GaussianBlur(heads, (0, 0), 2)
            f = cv2.add(cv2.add(b3.bg_frame(base, p, s * T + t), lines), heads)
            if p["rings"]:
                pulse = 0.35 + 0.65 * math.exp(-((t % beat) / 0.12))
                f = cv2.add(f, (rings * pulse).astype(np.uint8))
            f = cv2.add(f, (g1 * 1.8 * p["glow"]).clip(0, 255).astype(np.uint8)); f = cv2.add(f, (g2 * .8).clip(0, 255).astype(np.uint8))
            f[:230] = (f[:230].astype(np.float32) * (1 - talpha) + tcol * talpha).clip(0, 255).astype(np.uint8)
            ff.stdin.write(f.tobytes())
        print("stage", s + 1, "/", nst, n, st["variant"], flush=True)
    ff.stdin.close(); ff.wait()
    au = build_audio(stage_hits, T, p, total)
    with wave.open(ta, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((au * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tv, "-i", ta, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_path], check=True)
    os.remove(tv); os.remove(ta); json.dump(p, open(out_path.rsplit(".", 1)[0] + ".json", "w"), indent=1)
    print("OK", out_path, p["duration"], p["counts"][:12])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
