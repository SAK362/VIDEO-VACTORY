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
MODEL = os.environ.get("WHISPER_MODEL", "small")


def script_tokens(narration):
    # Sama dengan tokenize() di timing.ts: tanda * dibuang tanpa menambah spasi, lalu dipecah per spasi.
    return str(narration or "").replace("*", "").split()


def norm(s):
    return re.sub(r"[\W_]+", "", s.lower(), flags=re.UNICODE)


def align_tokens(tokens, heard, total):
    """tokens: kata naskah. heard: [(kata, mulai, selesai)] dari pengenal ucapan.
    Mengembalikan (waktu, rasio_cocok) dengan waktu = [[mulai, selesai], ...] sepanjang tokens."""
    a = [norm(t) for t in tokens]
    b = [norm(h[0]) for h in heard]
    times = [None] * len(tokens)
    exact = 0
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                times[i1 + k] = [heard[j1 + k][1], heard[j1 + k][2]]
                exact += 1
        elif tag == "replace":
            if j2 > j1:
                lo, hi = heard[j1][1], heard[j2 - 1][2]
                if (i2 - i1) == (j2 - j1):
                    for k in range(i2 - i1):
                        times[i1 + k] = [heard[j1 + k][1], heard[j1 + k][2]]
                else:
                    wl = [len(tokens[i]) + 1.5 for i in range(i1, i2)]
                    ws = sum(wl)
                    t = lo
                    for k, i in enumerate(range(i1, i2)):
                        d = (hi - lo) * wl[k] / ws
                        times[i] = [t, t + d]
                        t += d
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
    return times, (exact / n if n else 0.0)


def main():
    with open(PROPS, "r", encoding="utf-8") as f:
        props = json.load(f)
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
        beam_size=1,
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
    print("Kata yang cocok persis: %.0f%%" % (ratio * 100))
    if ratio < 0.4:
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
