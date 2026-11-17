"""Buat webgl/timing.js dari work/props.json (wordTimes hasil Whisper) + public/voiceover.wav.
Satu adegan = satu kalimat (indeks 'si'). Tanpa wordTimes, waktu diperkirakan sebanding panjang kata."""
import json, os, subprocess
import numpy as np

PROPS = os.environ.get('PROPS_FILE', 'work/props.json')
WAV = os.environ.get('WAV_FILE', 'public/voiceover.wav')
OUT = os.environ.get('TIMING_OUT', 'webgl/timing.js')
SR = 24000; FPS = 30


def main():
    props = json.load(open(PROPS, encoding='utf-8'))
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', WAV, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    y = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    dur = len(y) / SR
    sents = [str(s.get('narration', '')).replace('*', '').strip() for s in props['scenes']]
    words = []
    for si, s in enumerate(sents):
        for w in s.split(): words.append({'w': w, 'si': si})
    wt = props.get('wordTimes')
    if isinstance(wt, list) and len(wt) == len(words):
        for i, w in enumerate(words):
            w['start'] = float(wt[i][0]); w['end'] = float(wt[i][1])
        # Whisper sering meregangkan kata ke dalam jeda: geser awal kata ke akhir jeda, akhir kata ke awal jeda.
        n10 = int(SR * 0.01); m10 = len(y) // n10
        r10 = np.sqrt((y[:m10 * n10].reshape(m10, n10) ** 2).mean(axis=1) + 1e-12); sil = r10 < 10 ** (-35 / 20)
        def silence_at(t):
            i = int(t / 0.01)
            if i < 0 or i >= m10 or not sil[i]: return None
            a = i
            while a > 0 and sil[a - 1]: a -= 1
            b = i
            while b < m10 and sil[b]: b += 1
            return (a * 0.01, b * 0.01) if (b - a) >= 12 else None
        for w in words:
            sg = silence_at(w['start'])
            if sg and sg[1] < w['end'] - 0.05: w['start'] = sg[1]
            sg = silence_at(w['end'])
            if sg and sg[0] > w['start'] + 0.05: w['end'] = sg[0]
        for i in range(len(words) - 1):  # akhir kata tidak melewati awal kata berikut
            words[i]['end'] = max(words[i]['start'] + 0.04, min(words[i]['end'], words[i + 1]['start'] - 0.01))
        mode = 'suara'
    else:
        lens = [len(w['w']) + 1.5 for w in words]; tot = sum(lens); t = 0.25
        for w, L in zip(words, lens):
            w['start'] = t; t += (dur - 0.5) * L / tot; w['end'] = t - 0.02
        mode = 'perkiraan'
    spans = []
    for si in range(len(sents)):
        ws = [w for w in words if w['si'] == si]
        spans.append([ws[0]['start'], ws[-1]['end']] if ws else [0, 0])
    nf = int((dur + 0.8) * FPS); env = []; win = int(SR * 0.04)
    for i in range(nf):
        c = int(i / FPS * SR); seg = y[max(0, c - win):c + win]
        env.append(float(np.sqrt((seg ** 2).mean())) if len(seg) else 0.0)
    env = np.array(env)
    p95 = np.percentile(env[env > 0.004], 92) if (env > 0.004).any() else 1
    o = np.clip(env / p95, 0, 1.2) ** 0.7; o[env < 0.006] = 0
    mouth = []; cur = 0
    for v in o:
        cur = cur + (v - cur) * (0.65 if v > cur else 0.35); mouth.append(round(min(1.0, cur), 3))
    d = {'dur': dur, 'fps': FPS, 'words': words, 'sents': sents, 'sent_spans': spans, 'mouth': mouth}
    os.makedirs(os.path.dirname(OUT) or '.', exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write('window.TIMING=' + json.dumps(d, ensure_ascii=False) + ';')
    print('timing.js ditulis: %d kata, %d kalimat, %.2f dtk, mode %s' % (len(words), len(sents), dur, mode))


if __name__ == '__main__':
    main()
