"""Selaraskan kata naskah dengan suara memakai jeda bicara sebagai jangkar (tanpa model pengenal ucapan).
Membaca work/props.json (satu adegan = satu kalimat) + public/voiceover.wav (sudah dirapikan),
menulis webgl/timing.js. Gagal -> keluar dengan kode 1 (workflow memakai make_timing.py)."""
import re, json, subprocess, sys, os
import numpy as np

CLEAN = os.environ.get('WAV_FILE', 'public/voiceover.wav')
PROPS = os.environ.get('PROPS_FILE', 'work/props.json')
OUT = os.environ.get('TIMING_OUT', 'webgl/timing.js')
SR = 24000


def readwav(p):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.int16).astype(np.float32) / 32768


def rms_env(x, win_ms=10):
    n = int(SR * win_ms / 1000); m = len(x) // n
    r = np.sqrt((x[:m * n].reshape(m, n) ** 2).mean(axis=1) + 1e-12)
    return r, win_ms / 1000


def silences(x, thr_db=-35, min_d=0.18):
    r, dt = rms_env(x); thr = 10 ** (thr_db / 20); sil = r < thr; out = []; i = 0
    while i < len(sil):
        if sil[i]:
            j = i
            while j < len(sil) and sil[j]: j += 1
            if (j - i) * dt >= min_d: out.append([i * dt, j * dt])
            i = j
        else:
            i += 1
    return out

# ---- 2. word timing ----
y = readwav(CLEAN)
dur = len(y) / SR
sil = silences(y, -35, 0.18)
lead = 0.0
if sil and sil[0][0] < 0.05: lead = sil[0][1]; sil = sil[1:]
trail = dur
if sil and sil[-1][1] > dur - 0.05: trail = sil[-1][0]; sil = sil[:-1]
print('speech', round(lead, 2), round(trail, 2), 'pauses', len(sil))

props = json.load(open(PROPS, encoding='utf-8'))
sents = [str(s.get('narration', '')).replace('*', '').strip() for s in props['scenes']]
words = []
for si, s in enumerate(sents):
    for w in s.split():
        words.append({'w': w, 'si': si})


def syl(w):
    w2 = re.sub(r'[^A-Za-z\-]', '', w).lower()
    if w2 in ('cc',): return 2
    n = 0
    for part in w2.split('-'):
        if part == 'v': n += 1; continue
        n += max(1, len(re.findall(r'[aeiou]+', part)))
    return n

for w in words: w['syl'] = syl(w['w']) + 0.35
N = len(words)
cum = np.concatenate([[0], np.cumsum([w['syl'] for w in words])])
total = cum[-1]


def spt(t):  # speech-time (silences >=0.18 removed)
    r = 0.0; cur = lead
    for a, b in sil:
        if t <= a: return r + (t - cur)
        r += a - cur; cur = b
        if t < b: return r
    return r + (t - cur)

Ts = spt(trail)
M = len(sil)
INF = 1e9
sig = 2.2
isend = [False] * (N + 1)
iscomma = [False] * (N + 1)
for k in range(1, N + 1):
    w = words[k - 1]['w']
    isend[k] = bool(re.search(r'[.!?]$', w)); iscomma[k] = bool(re.search(r'[,:;]$', w))
sc = np.concatenate([[0], np.cumsum([1 if isend[k] else 0 for k in range(1, N + 1)])])  # sentence ends among first k words
def typecost(k, d):
    if isend[k]: return 0.0 if d >= 0.42 else 1.2
    if iscomma[k]: return 0.7 if d < 0.55 else 1.4
    return 3.2
f = [[INF] * (N + 1) for _ in range(M + 1)]
bp = [[None] * (N + 1) for _ in range(M + 1)]
f[0][0] = 0
for j in range(1, M + 1):
    pj = spt(sil[j - 1][0]); d = sil[j - 1][1] - sil[j - 1][0]
    skipc = 1.2 if d < 0.3 else 4.5
    for k in range(0, N + 1):
        if f[j - 1][k] < INF and f[j - 1][k] + skipc < f[j][k]:
            f[j][k] = f[j - 1][k] + skipc; bp[j][k] = (k, 'skip')
    # assign: from k' < k, penalty for unassigned sentence ends strictly between
    for k in range(1, N + 1):
        base = ((pj - cum[k] / total * Ts) / sig) ** 2 + typecost(k, d)
        bestc = INF; bestk = 0
        for k2 in range(0, k):
            if f[j - 1][k2] >= INF: continue
            miss = sc[k - 1] - sc[k2]
            c = f[j - 1][k2] + 2.5 * miss
            if c < bestc: bestc = c; bestk = k2
        if bestc < INF and bestc + base < f[j][k]:
            f[j][k] = bestc + base; bp[j][k] = (bestk, 'assign')
kend = int(np.argmin([f[M][k] + 2.5 * (sc[N] - sc[k]) for k in range(N + 1)]))
assign = {}
j, k = M, kend
while j > 0:
    pk, kind = bp[j][k]
    if kind == 'assign': assign[j - 1] = k
    k = pk; j -= 1
bounds = sorted(assign.items())  # (pause idx, boundary word count)
print('assigned', len(bounds), 'of', M)
for pi,k in bounds: print('  pause %.2f-%.2f after word %d (%s)' % (sil[pi][0], sil[pi][1], k, words[k-1]['w']))

# segments in time
segs = []  # (t0, t1, w0, w1)
t0 = lead; w0 = 0
for pi, k in bounds:
    segs.append((t0, sil[pi][0], w0, k)); t0 = sil[pi][1]; w0 = k
segs.append((t0, trail, w0, N))


def inv_spt(s):  # speech time -> real time
    r = 0.0; cur = lead
    for a, b in sil:
        if s <= r + (a - cur): return cur + (s - r)
        r += a - cur; cur = b
    return cur + (s - r)

from scipy.signal import butter, sosfilt, find_peaks
sos = butter(4, [250, 3500], btype='band', fs=SR, output='sos')
yb = sosfilt(sos, y)
e10, dt10 = rms_env(yb, 10)
edb = 20 * np.log10(e10 + 1e-6)
edb = np.convolve(edb, np.ones(3) / 3, mode='same')
isyl = lambda w: max(1, int(round(w['syl'] - 0.35)))
def align_seg(a, b, w0, w1):
    syls = []  # (word idx)
    for k in range(w0, w1): syls += [k] * isyl(words[k])
    S = len(syls)
    i0, i1 = int(a / dt10), int(b / dt10)
    seg = edb[i0:i1]
    pk, _ = find_peaks(seg, prominence=3.0, distance=5)
    tp = [(i0 + p) * dt10 for p in pk]
    P = len(tp)
    texp = [a + (i + 0.5) / S * (b - a) for i in range(S)]
    INFc = 1e9; un = 3.0; skip = 0.6
    dp = [[INFc] * (P + 1) for _ in range(S + 1)]; bk = [[None] * (P + 1) for _ in range(S + 1)]
    dp[0][0] = 0  # index j = number of peaks consumed
    for i in range(S):
        for j in range(P + 1):
            if dp[i][j] >= INFc: continue
            c = dp[i][j] + un
            if c < dp[i + 1][j]: dp[i + 1][j] = c; bk[i + 1][j] = (j, None)
            for j2 in range(j, P):
                c = dp[i][j] + skip * (j2 - j) + ((tp[j2] - texp[i]) / 0.15) ** 2
                if c < dp[i + 1][j2 + 1]: dp[i + 1][j2 + 1] = c; bk[i + 1][j2 + 1] = (j, j2)
    j = int(np.argmin([dp[S][x] + skip * (P - x) for x in range(P + 1)]))
    st = [None] * S; i = S
    while i > 0:
        pj, pm = bk[i][j]
        if pm is not None: st[i - 1] = tp[pm]
        j = pj; i -= 1
    # interpolate unmatched
    known = [(-1, a)] + [(i, t) for i, t in enumerate(st) if t is not None] + [(S, b)]
    for x in range(len(known) - 1):
        (ia, ta), (ib, tb) = known[x], known[x + 1]
        for i in range(ia + 1, ib): st[i] = ta + (tb - ta) * (i - ia) / (ib - ia)
    return syls, st

for (a, b, w0, w1) in segs:
    syls, st = align_seg(a, b, w0, w1)
    first = {}; last = {}
    for i, k in enumerate(syls): first.setdefault(k, i); last[k] = i
    starts = {}
    for k in range(w0, w1):
        if k == w0: starts[k] = a; continue
        t1, t2 = st[last[k - 1]], st[first[k]]
        i1, i2 = int(t1 / dt10), max(int(t1 / dt10) + 1, int(t2 / dt10))
        v = i1 + int(np.argmin(edb[i1:i2 + 1])) if i2 > i1 else i1
        starts[k] = min(max(v * dt10 - 0.03, t1 + 0.02), t2 - 0.01) if t2 - t1 > 0.05 else (t1 + t2) / 2
    for k in range(w0, w1):
        words[k]['start'] = round(starts[k], 3)
        words[k]['end'] = round((starts[k + 1] - 0.01) if k < w1 - 1 else b, 3)

# sentence spans
sent_spans = []
for si in range(len(sents)):
    ws = [w for w in words if w['si'] == si]
    sent_spans.append([ws[0]['start'], ws[-1]['end']])
    print(si + 1, round(ws[0]['start'], 2), round(ws[-1]['end'], 2), sents[si][:46])

# ---- 3. mouth envelope at 30 fps ----
FPS = 30
nf = int((dur + 0.8) * FPS)
env = []
win = int(SR * 0.04)
for i in range(nf):
    c = int(i / FPS * SR)
    seg = y[max(0, c - win):c + win]
    env.append(float(np.sqrt((seg ** 2).mean())) if len(seg) else 0.0)
env = np.array(env)
p95 = np.percentile(env[env > 0.004], 92) if (env > 0.004).any() else 1
o = np.clip(env / p95, 0, 1.2) ** 0.7
o[env < 0.006] = 0
sm = []; cur = 0
for v in o:
    cur = cur + (v - cur) * (0.65 if v > cur else 0.35)
    sm.append(cur)
mouth = [round(min(1.0, v), 3) for v in sm]

os.makedirs(os.path.dirname(OUT) or '.', exist_ok=True)
open(OUT, 'w', encoding='utf-8').write('window.TIMING=' + json.dumps({'dur': dur, 'fps': FPS, 'words': words, 'sents': sents, 'sent_spans': sent_spans, 'mouth': mouth}, ensure_ascii=False) + ';')
print('frames', nf)
