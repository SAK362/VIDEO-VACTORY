"""Build subtitle chunks: display text from the script (correct spelling, digits), timing from Whisper words.
Atomic units (number+unit, names) never split across lines/chunks. Max 2 lines, ~26 chars/line.
Usage: python -I make_subs.py <episode_dir> <out_json> <out_srt>"""
import json, re, sys, difflib
from pathlib import Path

D = Path(sys.argv[1])
shots = json.loads((D / "shots.json").read_text(encoding="utf-8"))
words = json.loads((D / "05_audio" / "words.json").read_text(encoding="utf-8"))
EP = json.loads((D / "episode.json").read_text(encoding="utf-8")) if (D / "episode.json").exists() else {}

DISPLAY = EP.get("subtitle_display", {})  # spoken form -> display form
ATOMIC = EP.get("subtitle_atomic", [])
SPOKEN_NUM = {k: v for k, v in EP.get("digits_to_spoken", {}).items() if len(k.split()) == 1}

def n(w): return re.sub(r"[^\w]", "", w.lower())

out_chunks = []
for s in shots:
    sw = [w for w in words if w["shot"] == s["id"]]
    # expand whisper digits back to spoken tokens so they align with the spoken script
    wt = []
    for w in sw:
        toks = re.findall(r"[\w]+", w["word"])
        exp = []
        for t in toks: exp += SPOKEN_NUM.get(t.lower(), t).split()
        if not exp: continue
        d = (w["end"] - w["start"]) / len(exp)
        for i, e in enumerate(exp): wt.append((n(e), w["start"] + i * d, w["start"] + (i + 1) * d))
    spoken = s["vo"].split()
    sp_n = [n(x) for x in spoken]
    sm = difflib.SequenceMatcher(None, sp_n, [x[0] for x in wt], autojunk=False)
    times = [None] * len(spoken)
    for a, b, size in sm.get_matching_blocks():
        for k in range(size): times[a + k] = (wt[b + k][1], wt[b + k][2])
    # interpolate unmatched
    known = [i for i, t in enumerate(times) if t]
    for i in range(len(times)):
        if times[i]: continue
        prev = max([k for k in known if k < i], default=None); nxt = min([k for k in known if k > i], default=None)
        t0 = times[prev][1] if prev is not None else (sw[0]["start"] if sw else 0)
        t1 = times[nxt][0] if nxt is not None else (sw[-1]["end"] if sw else t0 + 0.3)
        span = (nxt if nxt is not None else len(times)) - (prev if prev is not None else -1)
        pos = i - (prev if prev is not None else -1)
        a_ = t0 + (t1 - t0) * (pos - 1) / max(1, span - 1 + 1e-9); b_ = t0 + (t1 - t0) * pos / max(1, span - 1 + 1e-9)
        times[i] = (a_, max(a_ + 0.05, b_))
    # build display tokens (merge spoken phrases into display phrases)
    disp, i = [], 0
    while i < len(spoken):
        hit = None
        for sp, dv in DISPLAY.items():
            k = len(sp.split())
            if [n(x) for x in spoken[i:i + k]] == [n(x) for x in sp.split()]:
                tail = re.sub(r"^[\w]+", "", spoken[i + k - 1])  # keep trailing punctuation
                hit = (dv + tail, k); break
        if hit:
            disp.append({"t": hit[0], "s": times[i][0], "e": times[i + hit[1] - 1][1], "unit": True}); i += hit[1]
        else:
            disp.append({"t": spoken[i], "s": times[i][0], "e": times[i][1], "unit": False}); i += 1
    # lock atomic multi-word phrases
    units, i = [], 0
    atom = sorted([a.split() for a in ATOMIC], key=len, reverse=True)
    while i < len(disp):
        for a in atom:
            k = len(a)
            if [n(x["t"]) for x in disp[i:i + k]] == [n(x) for x in a]:
                units.append(disp[i:i + k]); i += k; break
        else:
            units.append([disp[i]]); i += 1
    # chunking: max 2 lines x 26 chars, break on sentence end / comma / long pause
    MAXL = 26
    def txt(us): return " ".join(w["t"] for u in us for w in u)
    def lines_of(us):
        if len(txt(us)) <= MAXL: return [us]
        best = None
        for k in range(1, len(us)):
            a, b = txt(us[:k]), txt(us[k:])
            if len(a) <= MAXL and len(b) <= MAXL:
                sc = abs(len(a) - len(b))
                if best is None or sc < best[0]: best = (sc, [us[:k], us[k:]])
        return best[1] if best else None
    cur = []
    def flush():
        if not cur: return
        ls = lines_of(cur)
        out_chunks.append({"start": round(cur[0][0]["s"], 3), "end": round(cur[-1][-1]["e"], 3), "shot": s["id"],
                           "lines": [[{"t": w["t"], "s": round(w["s"], 3), "e": round(w["e"], 3)} for u in l for w in u] for l in ls]})
    for u in units:
        cand = cur + [u]
        gap = u[0]["s"] - cur[-1][-1]["e"] if cur else 0
        prev_end = cur[-1][-1]["t"] if cur else ""
        if cur and (lines_of(cand) is None or gap > 0.45 or re.search(r"[.?!:]$", prev_end) or (re.search(r",$", prev_end) and len(txt(cur)) > 18)):
            flush(); cur = [u]
        else:
            cur = cand
    flush()

# keep chunks on screen until next chunk (but max +0.6 s)
for a, b in zip(out_chunks, out_chunks[1:]):
    a["end"] = round(min(b["start"] - 0.02, a["end"] + 0.6), 3)
out_chunks[-1]["end"] = round(out_chunks[-1]["end"] + 0.6, 3)
Path(sys.argv[2]).write_text(json.dumps(out_chunks, ensure_ascii=False), encoding="utf-8")

def ts(x):
    h, r = divmod(x, 3600); m, s_ = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s_):02d},{int((s_ - int(s_)) * 1000):03d}"
srt = []
for i, c in enumerate(out_chunks, 1):
    srt.append(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n" + "\n".join(" ".join(w["t"] for w in l) for l in c["lines"]) + "\n")
Path(sys.argv[3]).write_text("\n".join(srt), encoding="utf-8")
bad = [c for c in out_chunks if len(c["lines"]) > 2 or any(len(" ".join(w["t"] for w in l)) > 30 for l in c["lines"])]
print(len(out_chunks), "chunks; violations:", len(bad))
for c in out_chunks[:6]: print(c["start"], "|", " / ".join(" ".join(w["t"] for w in l) for l in c["lines"]))
