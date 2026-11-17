"""Whisper: catat waktu tiap kata suara proyek FIKSI -> <proyek>/heard.json (format sama dengan beyourbest).

Pakai: python fiksi/align_job.py fiksi/topik01
"""
import json
import os
import sys

from faster_whisper import WhisperModel

proj = sys.argv[1]
out = os.path.join(proj, "heard.json")
if os.path.exists(out):
    print("heard.json sudah ada, dilewati")
    sys.exit(0)
spec = json.load(open(os.path.join(proj, "spec.json"), encoding="utf-8"))
wav = os.path.join(proj, spec["audio"])
prompt = " ".join(s["text"] for s in spec["scenes"])
model = WhisperModel("medium", device="cpu", compute_type="int8")
segs, info = model.transcribe(wav, language="id", word_timestamps=True, beam_size=5,
                              initial_prompt=prompt, vad_filter=False, condition_on_previous_text=False)
heard = []
for s in segs:
    for w in (s.words or []):
        if w.word.strip():
            heard.append([w.word.strip(), round(float(w.start), 3), round(float(w.end), 3)])
json.dump({"duration": info.duration, "words": heard}, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print(wav, "kata:", len(heard), "durasi:", info.duration)
