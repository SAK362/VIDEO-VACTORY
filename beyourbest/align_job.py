"""Whisper: catat waktu tiap kata dari semua wav di beyourbest/align yang belum punya *_heard.json."""
import glob, json, os
from faster_whisper import WhisperModel
model = WhisperModel("medium", device="cpu", compute_type="int8")
for wav in sorted(glob.glob("beyourbest/align/*.wav")):
    out = wav[:-4] + "_heard.json"
    if os.path.exists(out):
        continue
    txt = wav[:-4] + "_narasi.txt"
    prompt = open(txt, encoding="utf-8").read() if os.path.exists(txt) else None
    segs, info = model.transcribe(wav, language="id", word_timestamps=True, beam_size=5,
                                  initial_prompt=prompt, vad_filter=False, condition_on_previous_text=False)
    heard = []
    for s in segs:
        for w in (s.words or []):
            if w.word.strip():
                heard.append([w.word.strip(), round(float(w.start), 3), round(float(w.end), 3)])
    json.dump({"duration": info.duration, "words": heard}, open(out, "w", encoding="utf-8"), ensure_ascii=False)
    print(wav, "kata:", len(heard), "durasi:", info.duration)
