"""QC-2 VO: transcribe each shot (faster-whisper, local), compare with script, measure edges/peaks,
then clean (trim to speech, fades, limiter), assemble with fixed gaps, and export word timings.
Usage: python -I qc_vo.py <episode_dir>"""
import json, re, subprocess, sys, difflib
from pathlib import Path
import numpy as np, wave
class sf:
    @staticmethod
    def read(p, dtype="float32"):
        with wave.open(str(p), "rb") as w:
            n, ch, sw, sr = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
            raw = w.readframes(n)
        assert sw == 2, f"unsupported sample width {sw}"
        a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
        return (a.reshape(-1, ch) if ch > 1 else a), sr
    @staticmethod
    def write(p, a, sr):
        a = np.clip(np.asarray(a, np.float32), -1, 1)
        with wave.open(str(p), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a * 32767).astype(np.int16).tobytes())
from faster_whisper import WhisperModel

D = Path(sys.argv[1]); RAW = D / "05_audio" / "raw"; CLEAN = D / "05_audio" / "clean"; CLEAN.mkdir(parents=True, exist_ok=True)
shots = json.loads((D / "shots.json").read_text(encoding="utf-8"))
EP = json.loads((D / "episode.json").read_text(encoding="utf-8")) if (D / "episode.json").exists() else {}
model = WhisperModel("medium", device="cpu", compute_type="int8")

NUMS = EP.get("spoken_to_digits", {})
def norm(s):
    s = s.lower()
    for k, v in NUMS.items(): s = s.replace(k, v)
    s = re.sub(r"[^\w\s,]", " ", s).replace(",", " ")
    return s.split()

def db(x): return 20 * np.log10(max(1e-9, float(np.sqrt(np.mean(np.square(x)))))) if len(x) else -120.0

import os
GAP = float(os.environ.get('KT_GAP', str(EP.get('gap_s', 0.30)))); SR = 48000; TEMPO_G = float(os.environ.get('KT_TEMPO', str(EP.get('tempo', 1.0))))
TEMPO_SHOT = json.loads(os.environ.get('KT_TEMPO_SHOT', json.dumps(EP.get('tempo_per_shot', {}))))  # per-shot override, e.g. {"S08": 0.95}
CLIP_LUFS = float(os.environ.get('KT_CLIP_LUFS', str(EP.get('clip_lufs', -17))))
report, words_all, t_cursor, timeline = [], [], 0.0, []
pieces = []
for s in shots:
    wav, sr = sf.read(RAW / f"{s['id']}.wav", dtype="float32")
    if wav.ndim > 1: wav = wav.mean(1)
    a16 = np.interp(np.linspace(0, len(wav) - 1, int(len(wav) * 16000 / sr)), np.arange(len(wav)), wav).astype(np.float32)
    segs, _ = model.transcribe(a16, language="id", word_timestamps=True, vad_filter=False, beam_size=5)
    ws = [w for seg in segs for w in seg.words]
    hyp = " ".join(w.word.strip() for w in ws)
    a, b = norm(s["vo"]), norm(hyp)
    sim = difflib.SequenceMatcher(None, a, b).ratio()
    extra = len(b) - len(a)
    t0 = max(0.0, ws[0].start - 0.06) if ws else 0.0
    t1 = min(len(wav) / sr, ws[-1].end + 0.18) if ws else len(wav) / sr
    seg = wav[int(t0 * sr):int(t1 * sr)].copy()
    fi, fo = int(0.04 * sr), int(0.12 * sr)
    seg[:fi] *= np.linspace(0, 1, fi); seg[-fo:] *= np.linspace(1, 0, fo)
    peak = 20 * np.log10(max(1e-9, float(np.abs(seg).max())))
    if peak > -1.0: seg *= 10 ** ((-1.0 - peak) / 20); peak = -1.0
    sf.write(CLEAN / f"{s['id']}.wav", seg, sr)
    TEMPO = TEMPO_SHOT.get(s['id'], TEMPO_G)
    if True:  # tempo (pitch preserved) + per-clip loudness match (pitch preserved), then reload the clip
        tmpf = CLEAN / f"{s['id']}_t.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(CLEAN / f"{s['id']}.wav"), "-filter:a", f"atempo={TEMPO},loudnorm=I={CLIP_LUFS}:TP=-2:LRA=7:linear=false,aresample={sr}", "-ar", str(sr), "-ac", "1", str(tmpf)], check=True)
        tmpf.replace(CLEAN / f"{s['id']}.wav"); seg, sr = sf.read(CLEAN / f"{s['id']}.wav")
    start_db, end_db = db(seg[:int(0.02 * sr)]), db(seg[-int(0.02 * sr):])
    dur = len(seg) / sr
    report.append({"id": s["id"], "dur": round(dur, 2), "similarity": round(sim, 3), "word_diff": extra,
                   "start_db": round(start_db, 1), "end_db": round(end_db, 1), "peak_db": round(peak, 1), "hyp": hyp})
    for w in ws:
        words_all.append({"word": w.word.strip(), "start": round(t_cursor + (w.start - t0) / TEMPO_SHOT.get(s["id"], TEMPO_G), 3), "end": round(t_cursor + (w.end - t0) / TEMPO_SHOT.get(s["id"], TEMPO_G), 3), "shot": s["id"]})
    timeline.append({"id": s["id"], "start": round(t_cursor, 3), "end": round(t_cursor + dur, 3)})
    pieces.append((seg, sr))
    t_cursor += dur + GAP

# assemble mono VO at 48 kHz with fixed gaps (0 overlap by construction)
lead = 0.35
out = [np.zeros(int(lead * SR), np.float32)]
for seg, sr in pieces:
    if sr != SR:
        n = int(len(seg) * SR / sr); seg = np.interp(np.linspace(0, len(seg) - 1, n), np.arange(len(seg)), seg).astype(np.float32)
    out += [seg, np.zeros(int(GAP * SR), np.float32)]
out.append(np.zeros(int(1.6 * SR), np.float32))  # tail for end card
vo = np.concatenate(out); sf.write(D / "05_audio" / "vo_full.wav", vo, SR)
for w in words_all: w["start"] += lead; w["end"] += lead
for t in timeline: t["start"] += lead; t["end"] += lead
(D / "05_audio" / "words.json").write_text(json.dumps(words_all, ensure_ascii=False, indent=0), encoding="utf-8")
(D / "05_audio" / "timeline.json").write_text(json.dumps({"total": round(len(vo) / SR, 3), "shots": timeline}, indent=1), encoding="utf-8")
(D / "07_qc").mkdir(exist_ok=True)
(D / "07_qc" / "QC-2_vo_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
for r in report:
    flag = "PASS" if r["similarity"] >= 0.88 and abs(r["word_diff"]) <= 3 and r["start_db"] < -45 and r["end_db"] < -45 and r["peak_db"] <= -1.0 else "CHECK"
    print(f"{r['id']} {flag} dur={r['dur']}s sim={r['similarity']} wdiff={r['word_diff']} start={r['start_db']}dB end={r['end_db']}dB peak={r['peak_db']}dB")
print("TOTAL", round(len(vo) / SR, 2), "s;", len(words_all), "words")
