#!/usr/bin/env python3
"""python render.py NO OUTDIR -> OUTDIR/focaloop_NNNN.mp4, .png, meta.json"""
import sys, os, json, subprocess
import plan, bounce5 as b

no = int(sys.argv[1]); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
seed = plan.seed_for(no)
base = os.path.join(out, f"focaloop_{no:04d}")
b.main(str(seed), base + ".mp4")
p = json.load(open(base + ".json"))
T = p["T"]; st = p["stages"]
bi = max(range(len(st)), key=lambda i: (st[i]["n"], -i))
t = bi * T + p["tmeet"] + 0.3
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", base + ".mp4", "-frames:v", "1", base + ".png"], check=True)
cs = p["counts"]
meta = {k: p[k] for k in ("seed", "question", "kind", "count_mode", "morph", "wall_style", "ball_style", "line_style", "bg_style",
                          "palette", "scale", "instr", "mapping")}
meta.update(no=no, duration=round(p["total"], 1), file=os.path.basename(base), counts=cs,
            counts_text=f"{min(cs)}-{max(cs)} balls, {p['count_mode']}, {len(cs)} stages")
json.dump(meta, open(os.path.join(out, "meta.json"), "w"))
print(json.dumps(meta))
