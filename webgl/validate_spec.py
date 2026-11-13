"""Validasi spec.json. python webgl/validate_spec.py spec.json [--n-sent N]  -> exit 1 bila galat; mencetak peringatan."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PRIM = {'box', 'cyl', 'sph', 'link', 'path', 'flow', 'group'}
ENVS = {'outdoor', 'rail', 'road', 'room', 'stage', 'studio', 'sea', 'space', 'night', 'underground', 'kampung', 'candi', 'hsr'}


def comps():
    import glob
    return set(n for f in glob.glob(os.path.join(HERE, 'engine', 'lib*.js')) for n in re.findall(r"^reg\('([a-z_]+)'", open(f, encoding='utf-8').read(), re.M))


def check(d, nsent=None):
    err, warn = [], []; C = comps() | PRIM
    sc = d.get('scenes')
    if not isinstance(sc, list) or not sc: return ['tidak ada scenes'], warn
    prev = -1
    for i, s in enumerate(sc):
        w = lambda m: err.append('adegan %d: %s' % (i, m))
        se = s.get('sent'); se = [se, se] if isinstance(se, int) else se
        if not (isinstance(se, list) and len(se) == 2 and all(isinstance(x, int) for x in se) and se[0] <= se[1]): w('sent harus [a,b]'); continue
        if se[0] <= prev: w('sent tumpang tindih / tidak berurut')
        prev = se[1]
        if nsent and se[1] >= nsent: w('sent melebihi jumlah kalimat %d' % nsent)
        if s.get('env', 'outdoor') not in ENVS: w('env tidak dikenal: %s' % s.get('env'))
        if not s.get('heading'): warn.append('adegan %d: heading kosong' % i)
        ids = set()
        objs = s.get('objs') or []
        if not objs: w('objs kosong')
        for j, o in enumerate(objs):
            t = o.get('t')
            if t not in C: w('objek %d jenis tidak dikenal: %s' % (j, t)); continue
            if o.get('id'): ids.add(o['id'])
            p = o.get('p')
            if p is not None and not (isinstance(p, list) and len(p) == 3 and all(isinstance(x, (int, float)) for x in p)): w('objek %d: p harus [x,y,z]' % j)
            if t in ('link',) and not (o.get('a') and o.get('b')): w('link butuh a & b')
            if t in ('path', 'flow') and len(o.get('pts') or []) < 2: w('%s butuh pts >=2' % t)
            if t == 'group':
                for k in o.get('kids') or []:
                    if k.get('id'): ids.add(k['id'])
        for l in s.get('labels') or []:
            a = str(l.get('at', '')).split('.')[0]
            if isinstance(l.get('at'), str) and a not in ids: warn.append('adegan %d: label at=%s tidak ada id' % (i, l.get('at')))
    if nsent and sc[-1]['sent'][-1] if isinstance(sc[-1].get('sent'), list) else False:
        pass
    if not sc[-1].get('ajak'): warn.append('adegan terakhir tanpa ajak')
    return err, warn


if __name__ == '__main__':
    d = json.load(open(sys.argv[1], encoding='utf-8')); n = int(sys.argv[sys.argv.index('--n-sent') + 1]) if '--n-sent' in sys.argv else None
    e, w = check(d, n)
    for x in w: print('PERINGATAN', x)
    for x in e: print('GALAT', x)
    print('OK' if not e else 'GAGAL'); sys.exit(1 if e else 0)
