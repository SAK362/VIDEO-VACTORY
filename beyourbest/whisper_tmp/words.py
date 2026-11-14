"""BeYourBest: waktu kata dari suara asli (faster-whisper). Cetak JSON di log antara penanda."""
import json, sys, os
from faster_whisper import WhisperModel

d = sys.argv[1]
wav = os.path.join(d, "voiceover.wav")
prompt = open(os.path.join(d, "narasi.txt"), encoding="utf-8").read().replace("\n\n", " ").strip()
m = WhisperModel("medium", device="cpu", compute_type="int8")
segs, info = m.transcribe(wav, language="id", word_timestamps=True, initial_prompt=prompt[-600:],
                          condition_on_previous_text=False, vad_filter=False, beam_size=5)
words = []
for s in segs:
    for w in (s.words or []):
        words.append([w.word.strip(), round(w.start, 3), round(w.end, 3)])
print("durasi", info.duration, "jumlah kata", len(words))
print("WORDS_JSON_BEGIN")
print(json.dumps(words, ensure_ascii=False))
print("WORDS_JSON_END")
os.makedirs("out", exist_ok=True)
json.dump(words, open("out/words.json", "w", encoding="utf-8"), ensure_ascii=False)
