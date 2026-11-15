#!/usr/bin/env python3
"""python render.py NO OUTDIR -> OUTDIR/focaloop_NNNN.mp4, .png, meta.json"""
import sys, os, json, subprocess
import plan, bounce3 as b

no = int(sys.argv[1]); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
seed = plan.seed_for(no)
base = os.path.join(out, f"focaloop_{no:04d}")
b.main(str(seed), base + ".mp4")
p = json.load(open(base + ".json"))
T = 2 * p["tmeet"]; total = T * len(p["counts"])
t = max(total - T * 0.45, 0.5)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", base + ".mp4", "-frames:v", "1", base + ".png"], check=True)
meta = {k: p[k] for k in ("seed", "question", "counts", "wall_style", "ball_style", "line_style", "bg_style", "palette", "scale", "instr", "mapping", "sector")}
meta.update(no=no, duration=round(total, 1), file=os.path.basename(base))
json.dump(meta, open(os.path.join(out, "meta.json"), "w"))
print(json.dumps(meta))
