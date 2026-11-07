"""Selaraskan kata naskah dengan suara asli (voiceover.wav) memakai faster-whisper.

Membaca work/props.json, menambahkan "wordTimes" (daftar [mulai, selesai] detik, satu per kata naskah)
lalu menulis ulang file itu. Bila apa pun gagal atau hasilnya meragukan, props.json TIDAK diubah
dan video memakai perkiraan waktu seperti sebelumnya.
"""
import difflib
import json
import os
import re
import sys

PROPS = os.environ.get("PROPS_FILE", "work/props.json")
WAV = os.environ.get("WAV_FILE", "public/voiceover.wav")
# "medium" lebih tepat untuk bahasa Indonesia daripada "small" (unduhan pertama sekitar 1,5 GB).
MODEL = os.environ.get("WHISPER_MODEL_OVERRIDE", "medium")


def script_tokens(narration):
    # Sama dengan tokenize() di timing.ts: tanda * dibuang tanpa menambah spasi, lalu dipecah per spasi.
    return str(narration or "").replace("*", "").split()


def norm(s):
    return re.sub(r"[\W_]+", "", s.lower(), flags=re.UNICODE)


def align_tokens(tokens, heard, total):
    """Pencocokan per HURUF (bukan per kata), supaya kata yang dipecah/digabung pengenal ucapan
    (mis. "nggak" vs "enggak", "sembilan puluh" vs "90") tidak menggeser kata-kata sesudahnya.
    tokens: kata naskah. heard: [(kata, mulai, selesai)].
    Mengembalikan (waktu, rasio_huruf_cocok) dengan waktu = [[mulai, selesai], ...] sepanjang tokens."""
    # Aliran huruf naskah + rentang huruf tiap kata.
    s_chars = []
    spans = []
    for t in tokens:
        n = norm(t)
        a = len(s_chars)
        s_chars.extend(n)
        spans.append((a, len(s_chars)))
    # Aliran huruf yang terdengar + waktu tiap huruf (dibagi rata di dalam kata).
    h_chars = []
    h_time = []
    for w, st, en in heard:
        n = norm(w)
        if not n:
            continue
        dur = max(0.0, en - st)
        for k, ch in enumerate(n):
            h_chars.append(ch)
            h_time.append(st + dur * (k + 0.5) / len(n))
    s_str = "".join(s_chars)
    h_str = "".join(h_chars)
    match = [None] * len(s_str)
    sm = difflib.SequenceMatcher(None, s_str, h_str, autojunk=False)
    for blk in sm.get_matching_blocks():
        if blk.size < 2:  # huruf tunggal yang kebetulan sama diabaikan
            continue
        for k in range(blk.size):
            match[blk.a + k] = blk.b + k
    matched = sum(1 for m in match if m is not None)

    times = [None] * len(tokens)
    for i, (a, b) in enumerate(spans):
        idx = [match[c] for c in range(a, b) if match[c] is not None]
        if b > a and len(idx) >= max(1, (b - a) // 3):
            st = h_time[idx[0]] - 0.03
            en = h_time[idx[-1]] + 0.03
            times[i] = [st, max(en, st + 0.05)]
    # Isi kata yang tidak terdengar: bagi waktu di antara dua jangkar sebanding panjang huruf.
    n = len(tokens)
    i = 0
    while i < n:
        if times[i] is not None:
            i += 1
            continue
        j = i
        while j < n and times[j] is None:
            j += 1
        left = times[i - 1][1] if i > 0 else 0.15
        right = times[j][0] if j < n else max(left + 0.2, total - 0.1)
        if right < left:
            right = left
        wl = [len(tokens[k]) + 1.5 for k in range(i, j)]
        ws = sum(wl)
        t = left
        for q, k in enumerate(range(i, j)):
            d = (right - left) * wl[q] / ws
            times[k] = [t, t + d]
            t += d
        i = j
    # Pastikan urut dan tidak mundur.
    prev = 0.0
    for k in range(n):
        s, e = times[k]
        s = max(s, prev)
        e = max(e, s + 0.04)
        times[k] = [round(min(s, total), 3), round(min(e, total + 0.5), 3)]
        prev = s
    return times, (matched / len(s_str) if s_str else 0.0)


def main():
    with open(PROPS, "r", encoding="utf-8") as f:
        props = json.load(f)
    sc = props.get("scenes") or []
    if sc and all(isinstance(x, dict) and x.get("narration") for x in sc):
        props["narration"] = " ".join(str(x["narration"]) for x in sc)
    tokens = script_tokens(props.get("narration"))
    if len(tokens) < 10:
        print("Naskah terlalu pendek, lewati penyelarasan.")
        return 0
    total = float(props.get("audioSeconds") or 0) or 60.0
    lang = "id" if str(props.get("lang", "en")).lower().startswith("id") else "en"

    from faster_whisper import WhisperModel

    model = WhisperModel(MODEL, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(
        WAV,
        language=lang,
        word_timestamps=True,
        beam_size=3,
        vad_filter=False,
        condition_on_previous_text=False,
    )
    heard = []
    for seg in segments:
        for w in seg.words or []:
            word = (w.word or "").strip()
            if word:
                heard.append((word, float(w.start), float(w.end)))
    print("Kata terdengar: %d, kata naskah: %d" % (len(heard), len(tokens)))
    if len(heard) < len(tokens) * 0.5:
        print("Hasil pengenalan terlalu sedikit, memakai perkiraan waktu.")
        return 0

    times, ratio = align_tokens(tokens, heard, total)
    print("Huruf yang cocok: %.0f%%" % (ratio * 100))
    if ratio < 0.5:
        print("Kecocokan terlalu rendah, memakai perkiraan waktu.")
        return 0

    props["wordTimes"] = times
    tmp = PROPS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False)
    os.replace(tmp, PROPS)
    print("wordTimes ditulis untuk %d kata." % len(times))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # jangan sampai render gagal karena penyelarasan
        print("Penyelarasan dilewati: %r" % (e,))
        sys.exit(0)
