"""Perencana adegan AI: naskah (timing.js) -> spec.json -> spec.js.
  python webgl/plan_scenes.py [--title "Judul"] [--out webgl/spec.js]
Butuh env GEMINI_API_KEY (gratis, diutamakan) atau ANTHROPIC_API_KEY (secret repo). Tanpa kunci / gagal 3x -> spec cadangan generik (tetap bisa dirender).
Bila work/props.json sudah punya "spec" -> dipakai langsung, tanpa AI."""
import json, os, re, sys, urllib.request, urllib.error
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from validate_spec import check, comps

MODEL = os.environ.get('PLANNER_MODEL', 'claude-sonnet-5-5')


def load_sents():
    tm = json.loads(re.search(r'=(.*);\s*$', open(os.path.join(HERE, 'timing.js'), encoding='utf-8').read(), re.S).group(1))
    words = tm['words']; n = len(tm['sent_spans']); S = [[] for _ in range(n)]
    for w in words: S[w['si']].append(w['w'])
    return [' '.join(x) for x in S]


def comp_doc():
    import glob
    src = '\n'.join(open(f, encoding='utf-8').read() for f in sorted(glob.glob(os.path.join(HERE, 'engine', 'lib*.js'))))
    return '\n'.join('- `%s`: %s' % (a, b) for a, b in re.findall(r"^reg\('([a-z_]+)', '([^']*)'", src, re.M))


def fix_cover(d, n):
    """paksa adegan berurut & menutup semua kalimat 0..n-1"""
    sc = d['scenes']; cur = 0
    for i, s in enumerate(sc):
        se = s.get('sent'); a, b = (se, se) if isinstance(se, int) else se
        a = cur; b = max(a, min(b, n - 1)) if i < len(sc) - 1 else n - 1
        s['sent'] = [a, b]; cur = b + 1
        if cur >= n and i < len(sc) - 1: del sc[i + 1:]; sc[-1]['sent'][1] = n - 1; break
    return d


def ask(system, user):
    if os.environ.get('GEMINI_API_KEY'):
        model = os.environ.get('GEMINI_MODEL') or 'gemini-3.5-flash-lite'
        body = json.dumps({'systemInstruction': {'parts': [{'text': system}]}, 'contents': [{'role': 'user', 'parts': [{'text': user}]}],
                           'generationConfig': {'temperature': 0.4, 'responseMimeType': 'application/json', 'maxOutputTokens': 16000}}).encode()
        rq = urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent' % model, body,
                                    {'x-goog-api-key': os.environ['GEMINI_API_KEY'], 'content-type': 'application/json'})
        with urllib.request.urlopen(rq, timeout=300) as r: out = json.load(r)
        return ''.join(pt.get('text', '') for pt in out['candidates'][0]['content']['parts'])
    key = os.environ['ANTHROPIC_API_KEY']
    body = json.dumps({'model': MODEL, 'max_tokens': 16000, 'system': system, 'messages': [{'role': 'user', 'content': user}]}).encode()
    rq = urllib.request.Request('https://api.anthropic.com/v1/messages', body, {'x-api-key': key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
    with urllib.request.urlopen(rq, timeout=300) as r: out = json.load(r)
    return ''.join(b.get('text', '') for b in out['content'])


def parse(txt):
    m = re.search(r'\{.*\}', txt, re.S)
    return json.loads(m.group(0))


def fallback(sents, title):
    """spec generik: tiap ~3 kalimat satu adegan, objek berputar bergantian. Selalu valid."""
    cyc = [[{'t': 'gear', 'p': [-1.6, 2, 0], 'n': 12, 'rad': 1.5, 'w': 1.5, 'col': '#d97a1c'}, {'t': 'gear', 'p': [1.15, 2, 0], 'n': 10, 'rad': 1.25, 'w': -1.8, 'col': '#2f8fbf'}],
           [{'t': 'motor', 'p': [0, 1.6, 0]}, {'t': 'fan', 'p': [3, 1.6, 0], 'rad': 1}],
           [{'t': 'pump', 'p': [0, 1.2, 0]}, {'t': 'tank', 'p': [4, 1.5, 0], 'size': [2, 3, 2], 'lvlAnim': [0.3, 0.9, 6]}],
           [{'t': 'atom', 'p': [0, 2.5, 0], 'e': 3}, {'t': 'molecule', 'p': [4, 2, 0], 'atoms': [{'p': [0, 0, 0], 'r': 0.5, 'c': '#e8403a'}, {'p': [0.9, 0.5, 0], 'r': 0.35, 'c': '#ffffff'}, {'p': [-0.9, 0.5, 0], 'r': 0.35, 'c': '#ffffff'}]}]]
    n = len(sents); k = max(1, round(n / 3)); sc = []
    for i in range(k):
        a = i * n // k; b = (i + 1) * n // k - 1
        words = re.sub(r'[.,!?]', '', sents[a]).split()[:4]
        s = {'sent': [a, b], 'env': 'stage' if i % 2 else 'studio', 'kicker': (title or 'FAKTA UNIK').upper()[:22] if i == 0 else 'LANGKAH %d' % i,
             'heading': ' '.join(words), 'objs': cyc[i % len(cyc)], 'tag': 'ILUSTRASI DISEDERHANAKAN'}
        sc.append(s)
    sc[-1]['kicker'] = 'JADI...'; sc[-1]['ajak'] = 'Follow & tulis topik berikutnya di komentar'
    return {'title': title or 'FAKTA UNIK', 'scenes': sc}


def main():
    title = sys.argv[sys.argv.index('--title') + 1] if '--title' in sys.argv else ''
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else os.path.join(HERE, 'spec.js')
    for pj in ('work/props.json', os.path.join(HERE, '..', 'work', 'props.json')):
        if os.path.exists(pj):
            p = json.load(open(pj, encoding='utf-8')); title = title or p.get('title', '')
            if p.get('engine') == 'diesel':
                open(os.path.join(HERE, 'engine.txt'), 'w').write('engine_diesel.html'); print('mesin lama (diesel) dipakai'); return
            if p.get('spec'): d = p['spec']; print('spec dari props.json'); return emit(d, out)
            break
    sents = load_sents(); n = len(sents); d = None
    if os.environ.get('GEMINI_API_KEY') or os.environ.get('ANTHROPIC_API_KEY'):
        system = open(os.path.join(HERE, 'SPEC.md'), encoding='utf-8').read().replace('@@COMP@@', comp_doc())
        user = 'Judul: %s\nJumlah kalimat: %d\nNaskah:\n%s\n\nBuat spec JSON.' % (title, n, '\n'.join('%d: %s' % (i, s) for i, s in enumerate(sents)))
        for attempt in range(3):
            try:
                d = parse(ask(system, user)); d = fix_cover(d, n); e, w = check(d, n)
                for x in w: print('PERINGATAN', x)
                if not e: print('perencana AI OK (percobaan %d)' % (attempt + 1)); break
                print('::warning::spec AI galat:', e[:6]); user += '\n\nPercobaan sebelumnya galat, perbaiki: ' + '; '.join(e[:10]); d = None
            except Exception as ex:
                print('::warning::perencana AI gagal:', ex); d = None
    else:
        print('::warning::GEMINI_API_KEY/ANTHROPIC_API_KEY tidak ada -> spec cadangan generik')
    if d is None: print('::warning::memakai spec cadangan generik'); d = fallback(sents, title)
    emit(d, out)


def emit(d, out):
    json.dump(d, open(os.path.join(HERE, 'spec.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(out, 'w', encoding='utf-8').write('window.SPEC=' + json.dumps(d, ensure_ascii=False) + ';\n'); print('spec ->', out, len(d['scenes']), 'adegan')


if __name__ == '__main__': main()
