"""Layered voice-over QC.
Usage: python -I qc_vo_layers.py <episode_dir> <master.mp4> <subs.json>
L1 content     : Whisper-medium transcript vs script (normalised WER), key terms present, no extra sentences
L2 pronunciation: low-confidence words (prob < 0.45) with timestamps
L3 signal      : clipping, DC offset, clicks/pops, dead air inside a clip, clean clip edges
L4 consistency : per-clip loudness spread, speaking rate (wpm)
L5 final mix   : integrated LUFS, true peak, LRA (from the master file)
L6 A/V sync    : master audio re-transcribed; subtitle word starts vs heard word starts
Writes 07_qc/QC-VO_layers.json and prints PASS/FAIL per layer."""
import json, re, subprocess, sys, wave, difflib
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel

D = Path(sys.argv[1]); MASTER = sys.argv[2]; SUBS = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
shots = json.loads((D / "shots.json").read_text(encoding="utf-8"))
EP = json.loads((D / "episode.json").read_text(encoding="utf-8")) if (D / "episode.json").exists() else {}
model = WhisperModel("medium", device="cpu", compute_type="int8")
KEY_TERMS = EP.get("key_terms", {})
NUM = {k: v for k, v in EP.get("digits_to_spoken", {}).items() if len(k) > 1}
def norm(s):
    s = s.lower().replace("-", " ")
    for k, v in NUM.items(): s = re.sub(rf"\b{re.escape(k)}\b", v, s)
    s = re.sub(r"[^\w\s]", " ", s)
    s = s.replace("nggak", "ga").replace("enggak", "ga").replace("gak", "ga").replace("coklat", "cokelat").replace("kropos", "keropos")
    return s.split()
def load(p):
    with wave.open(str(p)) as w: sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a, sr
def to16k(a, sr): return np.interp(np.linspace(0, len(a) - 1, int(len(a) * 16000 / sr)), np.arange(len(a)), a).astype(np.float32)
def lufs(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    summ = out[out.rfind("Summary:"):]
    g = lambda k: float(re.search(rf"{k}:\s+(-?[\d.]+)", summ).group(1)) if re.search(rf"{k}:\s+(-?[\d.]+)", summ) else None
    return {"I": g("I"), "LRA": g("LRA"), "TP": g("Peak")}

rep = {"clips": [], "layers": {}}
fails = {k: [] for k in ("L1", "L2", "L3", "L4", "L5", "L6")}
for s in shots:
    p = D / "05_audio" / "clean" / f"{s['id']}.wav"
    a, sr = load(p)
    segs, _ = model.transcribe(to16k(a, sr), language="id", beam_size=5, word_timestamps=True,
                               initial_prompt=EP.get("whisper_prompt", "Kupas Teknik"))
    words = [w for sg in segs for w in sg.words]
    hyp = " ".join(w.word.strip() for w in words)
    A, B = norm(s["vo"]), norm(hyp)
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    errs = [(" ".join(A[i1:i2]), " ".join(B[j1:j2])) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]
    wer = sum(max(i2 - i1, j2 - j1) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal") / max(1, len(A))
    missing = [k for k in KEY_TERMS.get(s["id"], []) if k.lower() not in hyp.lower()]
    extra = len(B) - len(A)
    lowconf = [(w.word.strip(), round(float(w.start), 2), round(float(w.probability), 2)) for w in words if w.probability < 0.45]
    # L3 signal
    peak = float(np.abs(a).max()); clip_n = int((np.abs(a) > 0.995).sum()); dc = float(a.mean())
    d = np.abs(np.diff(a)); rms_local = np.convolve(np.abs(a), np.ones(480) / 480, mode="same")[1:] + 1e-4
    clicks = int(((d > 0.35) & (d > 12 * rms_local)).sum())
    env = np.convolve(a ** 2, np.ones(int(sr * 0.05)) / int(sr * 0.05), mode="same")
    silent = env < 10 ** (-50 / 10)
    longest, run = 0, 0
    for v in silent[int(sr * 0.2):-int(sr * 0.2)]: run = run + 1 if v else 0; longest = max(longest, run)
    dead = longest / sr
    edge = (20 * np.log10(np.sqrt(np.mean(a[:int(sr * 0.02)] ** 2)) + 1e-9), 20 * np.log10(np.sqrt(np.mean(a[-int(sr * 0.02):] ** 2)) + 1e-9))
    L = lufs(p); wpm = len(A) / (len(a) / sr) * 60
    c = {"id": s["id"], "wer": round(wer, 3), "errors": errs[:8], "missing_terms": missing, "extra_words": extra, "low_conf": lowconf, "peak_db": round(20 * np.log10(peak + 1e-9), 2),
         "clipped_samples": clip_n, "dc": round(dc, 5), "clicks": clicks, "dead_air_s": round(dead, 2), "edge_db": [round(x, 1) for x in edge], "lufs": L["I"], "wpm": round(wpm)}
    rep["clips"].append(c)
    if wer > 0.12 or missing or extra > 3: fails["L1"].append(s["id"])
    if len(lowconf) > 2: fails["L2"].append(s["id"])
    if clip_n or abs(dc) > 0.005 or clicks or dead > 1.2 or max(edge) > -45: fails["L3"].append(s["id"])
lu = [c["lufs"] for c in rep["clips"] if c["lufs"] is not None]
if max(lu) - min(lu) > 2.0: fails["L4"].append(f"loudness spread {max(lu) - min(lu):.1f} LU")
for c in rep["clips"]:
    if not 105 <= c["wpm"] <= 175: fails["L4"].append(f"{c['id']} {c['wpm']} wpm")
M = lufs(MASTER); rep["master"] = M
if M["I"] is None or not (-15.0 <= M["I"] <= -13.0) or (M["TP"] is not None and M["TP"] > -1.4): fails["L5"].append(str(M))
# L6 sync: transcribe master audio, compare subtitle word starts to heard word starts (matched words only)
wav = D / "07_qc" / "_master_audio.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", MASTER, "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
ma, msr = load(wav)
segs, _ = model.transcribe(ma, language="id", beam_size=5, word_timestamps=True)
heard = [(re.sub(r"[^\w]", "", w.word.lower()), w.start) for sg in segs for w in sg.words]
subw = [(re.sub(r"[^\w]", "", w["t"].lower()), w["s"]) for ch in SUBS for l in ch["lines"] for w in l]
sm = difflib.SequenceMatcher(None, [x[0] for x in subw], [x[0] for x in heard], autojunk=False)
offs = []
for i, j, n in sm.get_matching_blocks():
    for k in range(n): offs.append(float(subw[i + k][1]) - float(heard[j + k][1]))
offs = np.array(offs) if offs else np.array([0.0])
rep["sync"] = {"matched_words": int(len(offs)), "median_offset_s": round(float(np.median(offs)), 3), "p95_abs_s": round(float(np.percentile(np.abs(offs), 95)), 3), "worst_s": round(float(np.abs(offs).max()), 3)}
if abs(rep["sync"]["median_offset_s"]) > 0.08 or rep["sync"]["p95_abs_s"] > 0.25: fails["L6"].append(rep["sync"])
wav.unlink()
rep["layers"] = {k: ("PASS" if not v else {"FAIL": v}) for k, v in fails.items()}
(D / "07_qc" / "QC-VO_layers.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
names = {"L1": "isi & naskah", "L2": "pelafalan", "L3": "sinyal (klik/clip/dead air)", "L4": "konsistensi", "L5": "mix final", "L6": "sinkron A/V"}
for k, v in rep["layers"].items(): print(k, names[k], "->", v if v == "PASS" else json.dumps(v, ensure_ascii=False)[:300])
for c in rep["clips"]: print(c["id"], "wer", c["wer"], "wpm", c["wpm"], "lufs", c["lufs"], "lowconf", c["low_conf"][:4], "errs", c["errors"][:3])
print("master", M, "sync", rep["sync"])
