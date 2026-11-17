#!/usr/bin/env python3
"""python render.py NO OUTDIR -> OUTDIR/focaloop_NNNN.mp4, .png, meta.json  (tema dipilih dari nomor: plan.theme_for)"""
import sys, os, json, subprocess
import plan

no = int(sys.argv[1]); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
seed = plan.seed_for(no)
theme = os.environ.get("THEME") or plan.theme_for(no)
base = os.path.join(out, f"focaloop_{no:04d}")
if theme == "bounce":
    import bounce6 as b
    b.main(str(seed), base + ".mp4")
    p = json.load(open(base + ".json"))
    st = p["stages"]
    bi = max(range(len(st)), key=lambda i: (st[i]["n"], -i))
    t = st[bi]["off"] + st[bi]["Tret"] * 0.5
    cs = p["counts"]; pts = sorted({s["k"] for s in st})
    meta = {k: p[k] for k in ("seed", "question", "ball_style", "line_style", "bg_style", "palette", "scale", "instr", "mapping")}
    meta.update(no=no, duration=round(p["total"], 1), file=os.path.basename(base), counts=cs,
                kind=p["kinds"][0], points=pts, kinds=p["kinds"],
                counts_text=f"{min(cs)}-{max(cs)} balls, few to many, {len(cs)} stages, {pts[0]}-{pts[-1]} launch points", count_mode="few-to-many")
else:
    mod = __import__(theme)
    meta = mod.make(seed, base)
    t = meta.pop("thumb_t")
    meta.update(no=no, seed=seed, file=os.path.basename(base), theme=theme)
    meta.setdefault("count_mode", "n/a")
    for k in ("line_style",):
        meta.setdefault(k, "none")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", base + ".mp4", "-frames:v", "1", base + ".png"], check=True)
meta["theme"] = theme
json.dump(meta, open(os.path.join(out, "meta.json"), "w"))
print(json.dumps(meta))
