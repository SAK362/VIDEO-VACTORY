"""Layered automatic glitch QC for a rendered video.
Usage: python -I qc_video_glitch.py <video.mp4> <timeline.json> <out_dir>
Layers (per frame, grayscale 270x480):
  L1 spike   : frame-to-frame change far above its local median, not at a shot cut
  L2 pop     : frame i differs from i-1 AND i+1 while i-1 ~= i+1 (one-frame glitch)
  L3 flicker : 8x8-block pops (local flashes / z-fighting / shadow shimmer), counted per zone
Zones: header (y<26%), scene (26–72%), subtitle (72–86%), bottom (>86%).
Writes qc_glitch.json + strip images (i-1, i, i+1) for every flagged frame."""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image

VID, TL, OUT = sys.argv[1], sys.argv[2], Path(sys.argv[3]); OUT.mkdir(parents=True, exist_ok=True)
W, H, FPS = 270, 480, 30
import os
CUT_WIN = int(os.environ.get("KT_CUT_WIN", "3"))  # master has 3-frame tmix motion blur
tl = json.loads(Path(TL).read_text())
shots = tl["shots"]
# visual shot boundaries = midpoints of the gaps between VO shots (same rule as timing.ts)
cuts = [round(((shots[i - 1]["end"] + shots[i]["start"]) / 2) * FPS) for i in range(1, len(shots))]
end_card = round((shots[-1]["end"] + 0.15) * FPS)
cuts.append(end_card)
def shot_of(f):
    t = f / FPS
    for i, s in enumerate(shots):
        t1 = (s["end"] + shots[i + 1]["start"]) / 2 if i + 1 < len(shots) else 1e9
        if t < t1: return s["id"]
    return shots[-1]["id"]
ZONES = {"header": (0, int(H * 0.26)), "scene": (int(H * 0.26), int(H * 0.72)), "subtitle": (int(H * 0.72), int(H * 0.86)), "bottom": (int(H * 0.86), H)}

p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", VID, "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
frames = []  # keep a small ring buffer only
d_prev, d_skip, pops_blk = [], [], []
idx = 0; prev2 = prev1 = None
keep = {}  # frame -> array (only around flagged frames, filled in second pass)
diffs = []
blockpops = []
while True:
    buf = p.stdout.read(W * H)
    if len(buf) < W * H: break
    f = np.frombuffer(buf, np.uint8).astype(np.int16).reshape(H, W)
    if prev1 is not None:
        d = np.abs(f - prev1)
        diffs.append({z: float(d[a:b].mean()) for z, (a, b) in ZONES.items()})
    else:
        diffs.append({z: 0.0 for z in ZONES})
    if prev2 is not None:
        # evaluate frame idx-1 (= prev1) as the middle frame
        a, b, c = prev2, prev1, f
        ab, bc, ac = np.abs(b - a), np.abs(c - b), np.abs(c - a)
        # 8x8 block means
        def blk(x): return x[: H // 8 * 8, : W // 8 * 8].reshape(H // 8, 8, W // 8, 8).mean(axis=(1, 3))
        AB, BC, AC = blk(ab), blk(bc), blk(ac)
        pop = (AB > 14) & (BC > 14) & (AC < 5)
        rows = {z: int(pop[a_ // 8:b_ // 8].sum()) for z, (a_, b_) in ZONES.items()}
        blockpops.append((idx - 1, rows, float(ab.mean()), float(bc.mean()), float(ac.mean())))
    prev2, prev1 = prev1, f
    idx += 1
p.wait()
N = idx
flags = []
scene = np.array([d["scene"] for d in diffs])
for i in range(2, N - 2):
    if any(abs(i - c) <= CUT_WIN for c in cuts): continue
    lo, hi = max(0, i - 15), min(N, i + 16)
    med = float(np.median(scene[lo:hi])) + 0.4
    if scene[i] > max(6.0, 4.5 * med):
        flags.append({"frame": i, "t": round(i / FPS, 2), "shot": shot_of(i), "layer": "L1 spike", "zone": "scene", "value": round(scene[i], 2), "local_median": round(med, 2)})
for (i, rows, ab, bc, ac) in blockpops:
    if any(abs(i - c) <= CUT_WIN for c in cuts): continue
    if ab > 3.0 and bc > 3.0 and ac < 0.45 * min(ab, bc):
        flags.append({"frame": i, "t": round(i / FPS, 2), "shot": shot_of(i), "layer": "L2 pop", "zone": "full", "value": round(min(ab, bc), 2), "ac": round(ac, 2)})
    for z, n in rows.items():
        if n >= 3:
            flags.append({"frame": i, "t": round(i / FPS, 2), "shot": shot_of(i), "layer": "L3 flicker", "zone": z, "value": n})
# summarise flicker clusters
summary = {}
for fl in flags:
    k = (fl["shot"], fl["layer"], fl["zone"]); summary[k] = summary.get(k, 0) + 1
(OUT / "qc_glitch.json").write_text(json.dumps({"frames": N, "cuts": cuts, "flags": flags, "summary": {f"{a}|{b}|{c}": n for (a, b, c), n in summary.items()}}, indent=1))
print("frames", N, "flags", len(flags))
for k, n in sorted(summary.items(), key=lambda x: -x[1]): print(f"  {k[0]} {k[1]:11s} {k[2]:9s} x{n}")
# strips for the strongest flags (one per cluster region in time)
picked, last = [], -99
for fl in sorted(flags, key=lambda x: x["frame"]):
    if fl["frame"] - last > 20: picked.append(fl); last = fl["frame"]
want = sorted({f for fl in picked[:40] for f in (fl["frame"] - 1, fl["frame"], fl["frame"] + 1)})
if want:
    wset = set(want); got = {}
    q = subprocess.Popen(["ffmpeg", "-v", "error", "-i", VID, "-vf", "scale=360:640", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = 0
    while n <= max(want):
        buf = q.stdout.read(360 * 640 * 3)
        if len(buf) < 360 * 640 * 3: break
        if n in wset: got[n] = Image.frombytes("RGB", (360, 640), buf)
        n += 1
    q.kill()
    for fl in picked[:40]:
        trip = [got.get(fl["frame"] + k) for k in (-1, 0, 1)]
        if not all(trip): continue
        st = Image.new("RGB", (360 * 3, 640)); [st.paste(x, (k * 360, 0)) for k, x in enumerate(trip)]
        st.save(OUT / f"strip_{fl['frame']:05d}_{fl['layer'].split()[0]}_{fl['zone']}.jpg", quality=80)
print("picked", len(picked))
