"""Rapikan voiceover: jeda dalam > 0,7 dtk dipendekkan jadi ~0,55 dtk, lalu normalisasi -14 LUFS.
Membaca public/voiceover.wav, menulis ulang file itu (asli disimpan sebagai voiceover_raw.wav)
dan memperbarui audioSeconds di work/props.json. Bila gagal, file asli dipakai apa adanya."""
import json, os, shutil, subprocess, sys, wave
import numpy as np

WAV = os.environ.get('WAV_FILE', 'public/voiceover.wav')
PROPS = os.environ.get('PROPS_FILE', 'work/props.json')
SR = 24000


def read(p):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.int16).astype(np.float32) / 32768


def silences(x, thr_db=-38, min_d=0.7):
    n = int(SR * 0.01); m = len(x) // n
    r = np.sqrt((x[:m * n].reshape(m, n) ** 2).mean(axis=1) + 1e-12)
    sil = r < 10 ** (thr_db / 20); out = []; i = 0
    while i < len(sil):
        if sil[i]:
            j = i
            while j < len(sil) and sil[j]: j += 1
            if (j - i) * 0.01 >= min_d: out.append((i * 0.01, j * 0.01))
            i = j
        else: i += 1
    return out


def main():
    x = read(WAV); dur = len(x) / SR
    keep = np.ones(len(x), bool)
    for a, b in silences(x):
        if a < 0.3 or b > dur - 0.3: continue
        ex = (b - a) - 0.55; mid = (a + b) / 2
        keep[int((mid - ex / 2) * SR):int((mid + ex / 2) * SR)] = False
    y = x[keep]
    tmp = 'public/_tmp.wav'
    with wave.open(tmp, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    shutil.copy(WAV, 'public/voiceover_raw.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '44100', '-ac', '1', WAV], check=True)
    os.remove(tmp)
    new = len(read(WAV)) / SR
    props = json.load(open(PROPS, encoding='utf-8')); props['audioSeconds'] = round(new, 2)
    json.dump(props, open(PROPS, 'w', encoding='utf-8'), ensure_ascii=False)
    print('suara dirapikan: %.2f -> %.2f dtk' % (dur, new))


if __name__ == '__main__':
    try: main()
    except Exception as e: print('pembersihan suara dilewati:', repr(e))
