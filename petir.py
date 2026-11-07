"""Kit dunia: penangkal petir (batang di atap, kabel turun, batang tanah; badai)."""
import json, math, random
import numpy as np
from .. import core
from ..core import Scene, PI

D = json.load(open(core.DATA('petir_world.json')))
SEGS = D['segs']
LENS = [float(np.linalg.norm(np.array(s['b']) - np.array(s['a']))) for s in SEGS]
TOT = sum(LENS)
RECOL = {'grass': '#9CCB86', 'topsoil': '#B98B66', 'clay': '#C99B78', 'sand': '#E2CDA3', 'house': '#F2EBDD', 'roof': '#D98A6A',
         'ground_rod': '#D9853B', 'lamp': '#5E6978'}
STORM = ((118, 134, 152), (196, 201, 206))


def _col(p):
    c = p['color']
    if p['id'] == 'house' and c in ('#9FD8F5', '#8A5A3B', '#C46A3A', '#3E9E58', '#4F7CC2', '#B07A4A'):
        return c
    if p['id'] == 'yard':
        return {'#3E9E58': '#7DB36A', '#4FB86A': '#93C67E', '#7A4E2D': '#8B6A4E'}.get(c, '#C8A27A')
    return RECOL.get(p['id'], c)


def point_at(d):
    for s, L in zip(SEGS, LENS):
        if d <= L:
            a = np.array(s['a']); b = np.array(s['b'])
            return a + (b - a) * (d / L)
        d -= L
    return np.array(SEGS[-1]['b'])


def jag(a, b, n, seed, amp=0.35):
    rnd = random.Random(seed)
    pts = [np.array(a, float)]
    for k in range(1, n):
        q = np.array(a) + (np.array(b) - np.array(a)) * k / n
        pts.append(q + np.array([rnd.uniform(-amp, amp), 0, rnd.uniform(-0.1, 0.1)]))
    pts.append(np.array(b, float))
    return pts


def world(S, fill, now, rod=True, strike=False, people=False, burn=False):
    for p in D['env']:
        if p['id'] == 'source' or (not rod and p['id'] == 'ground_rod'):
            continue
        S.prim(p, _col(p))
    for i, (dx, dy, r) in enumerate([(-1.6, 0, 0.9), (-0.5, 0.35, 1.1), (0.7, 0.1, 0.95), (1.6, -0.1, 0.8), (-2.6, -0.2, 0.7)]):
        S.sph([-2.6 + dx, 7.2 + dy, -2.2], r, '#6E7C8C' if i % 2 else '#7F8C9A', 10, 6)
    if rod:
        P = np.array(D['pos']); sc = D['scale']
        for part in D['parts']:
            for p in part['prims']:
                S.prim(p, p['color'], M=np.eye(3) * sc, t=P)
        for s in SEGS:
            if s['kind'] == 'wire':
                S.seg(s['a'], s['b'], 0.045, '#2E3A46')
        left = fill * TOT
        for s, Ln in zip(SEGS, LENS):
            if left <= 0:
                break
            k = min(1, left / Ln)
            a = np.array(s['a']); b = a + (np.array(s['b']) - a) * k
            if s['kind'] == 'bolt':
                pts = jag(s['a'], b, 7, int(now * 7))
                for u, v in zip(pts[:-1], pts[1:]):
                    S.seg(u, v, 0.07, '#FFF6C2')
            else:
                S.seg(a, b, 0.06, '#FFD84A')
            left -= Ln
        if fill >= 0.9:
            for i in range(16):
                k = (now * 1.4 + i / 16) % 1
                a = i / 16 * 2 * PI
                S.sph([-1.5 + math.cos(a) * 1.5 * k, -2.5 + math.sin(a) * 1.0 * k, 0.86], 0.07, '#FFF0A0', 6, 4)
    if strike and not rod:
        pts = jag([-2.85, 6.6, -1.5], [-2.85, 3.45, -0.9], 7, int(now * 7))
        for u, v in zip(pts[:-1], pts[1:]):
            S.seg(u, v, 0.08, '#FFF6C2')
    if burn:
        for i in range(10):
            k = (now * 1.6 + i / 10) % 1
            S.sph([-2.85 + math.sin(i * 2.3) * 0.5, 3.4 + k * 0.9, -0.9 + math.cos(i * 1.7) * 0.4], 0.1 + 0.1 * (1 - k), '#FF8A3D' if i % 2 else '#FFC24A', 6, 4)
    if people:
        S.person(-3.3, 0.12, -1.2, '#3B6EA5', hair='#1F1A17'); S.person(-2.6, 0.12, -1.6, '#E8835A', h=0.7, hair='#7A4A2A')


def gutter(S, now):
    S.box([0, -0.05, 0], [5, 0.1, 3], '#9CCB86')
    S.box([-0.6, 1.0, -0.3], [2.4, 2.0, 1.6], '#F2EBDD')
    S.box([-0.6, 2.25, -0.3], [3.0, 0.12, 2.0], '#D98A6A', core.rz(-0.18))
    S.seg([0.85, 1.95, -1.3], [0.85, 1.95, 0.7], 0.08, '#B8C2CC')
    S.seg([0.85, 1.95, 0.7], [0.85, 0.05, 0.7], 0.08, '#B8C2CC')
    for i in range(8):
        k = (now * 1.5 + i / 8) % 1
        S.sph([0.85, 1.95 - 1.9 * k, 0.75], 0.05, '#3FA9E8', 6, 4)


def L(id_, en): return {'id': id_, 'en': en}
SHOTS = {
    'storm_wide': dict(desc='establishing: house in a thunderstorm, family inside', storm=True, people=True, fill=0,
                       cam=([-7.6, 4.4, 10.4], [-2.2, 1.8, -0.8]), cam2=([-6.4, 4.2, 10.8], [-2.2, 1.8, -0.8])),
    'rod_close': dict(desc='close on the rod at the top of the roof (good for the myth "it attracts lightning")', storm=True, fill=0,
                      labels={'id': [('penangkal petir', [-2.85, 5.1, -1.25], 'r', 'o')], 'en': [('lightning rod', [-2.85, 5.1, -1.25], 'r', 'o')]},
                      cam=([-3.0, 5.6, 6.0], [-2.85, 4.3, -1.25]), cam2=([-2.2, 5.4, 5.4], [-2.85, 4.3, -1.25])),
    'system_cut': dict(desc='house and ground cut open: rod on the roof, down conductor cable, ground rod', storm=True, fill=0,
                       tag=L('ILUSTRASI · RUMAH & TANAH DIBELAH', 'ILLUSTRATION · HOUSE & GROUND CUT OPEN'),
                       labels={'id': [('batang di atap', [-2.85, 5.0, -1.25], 'l', 'o'), ('kabel turun', [-1.5, 1.4, 0.25], 'r', 'o'), ('batang tanah', [-1.5, -1.8, 0.86], 'r', 'g')],
                               'en': [('air terminal', [-2.85, 5.0, -1.25], 'l', 'o'), ('down conductor', [-1.5, 1.4, 0.25], 'r', 'o'), ('ground rod', [-1.5, -1.8, 0.86], 'r', 'g')]},
                       cam=([2.6, 2.8, 9.6], [-2.0, 0.6, -0.2]), cam2=([2.0, 2.4, 9.0], [-2.0, 0.4, -0.2])),
    'strike': dict(desc='lightning strikes the tip of the rod (white flash)', storm=True, fillfrom=0.0, fillto=0.33, flash=True,
                   tag=L('ILUSTRASI · DISEDERHANAKAN', 'ILLUSTRATION · SIMPLIFIED'),
                   labels={'id': [('ujung batang', [-2.85, 5.25, -1.25], 'r', 'o')], 'en': [('rod tip', [-2.85, 5.25, -1.25], 'r', 'o')]},
                   cam=([-1.2, 6.0, 3.6], [-2.85, 5.0, -1.25]), cam2=([-1.0, 5.8, 3.2], [-2.85, 4.8, -1.25])),
    'current_down': dict(desc='the current flows down the thick cable on the outside wall (camera follows it)', storm=True, fillfrom=0.33, fillto=0.8, follow=True,
                         tag=L('ILUSTRASI · DISEDERHANAKAN', 'ILLUSTRATION · SIMPLIFIED'),
                         labels={'id': [('kabel turun', [-1.5, 1.2, 0.25], 'r', 'o')], 'en': [('down conductor', [-1.5, 1.2, 0.25], 'r', 'o')]},
                         cam=([0, 0, 0], [0, 0, 1])),
    'ground_spread': dict(desc='the current enters the ground rod and spreads into the earth', fillfrom=0.8, fillto=1.0,
                          tag=L('ILUSTRASI · TANAH DIBELAH', 'ILLUSTRATION · GROUND CUT OPEN'),
                          labels={'id': [('batang tanah', [-1.5, -1.0, 0.86], 'l', 'o'), ('arus menyebar', [-0.3, -2.6, 0.86], 'r', 'g')],
                                  'en': [('ground rod', [-1.5, -1.0, 0.86], 'l', 'o'), ('current spreads', [-0.3, -2.6, 0.86], 'r', 'g')]},
                          cam=([1.6, 0.6, 7.8], [-1.4, -1.5, 0.8]), cam2=([1.2, 0.3, 7.2], [-1.4, -1.7, 0.8])),
    'gutter_analogy': dict(desc='analogy: a rain gutter guides water down a pipe instead of the wall (separate set)', gutter=True, tag=L('PERUMPAMAAN', 'ANALOGY'),
                           labels={'id': [('jalur aman', [0.85, 1.0, 0.78], 'r', 'g')], 'en': [('safe path', [0.85, 1.0, 0.78], 'r', 'g')]},
                           cam=([3.2, 2.6, 5.6], [0, 1.1, 0]), cam2=([2.8, 2.4, 5.0], [0.2, 1.1, 0])),
    'no_rod_danger': dict(desc='danger: a house without the system is struck and the roof starts burning (red tint)', storm=True, danger=True, norod=True,
                          cam=([-6.6, 4.6, 8.2], [-2.6, 2.8, -1.0]), cam2=([-6.0, 4.4, 7.6], [-2.6, 2.8, -1.0])),
    'data_card': dict(desc='wide view with the number card (card required)', storm=True, fill=1, card=True,
                      cam=([-6.8, 4.4, 10.4], [-2.2, 1.6, -0.8]), cam2=([-7.4, 4.4, 10.8], [-2.2, 1.6, -0.8])),
    'outro_wide': dict(desc='ending: calm weather, family safe', people=True, fill=0, cam=([-6.4, 4.2, 10.8], [-2.2, 1.8, -0.8]), cam2=([-7.6, 4.4, 10.4], [-2.2, 1.8, -0.8])),
}
for _s in SHOTS.values():
    if _s.get('storm') or _s.get('gutter'):
        _s['sky'] = STORM if _s.get('storm') else None
    if _s.get('sky') is None:
        _s.pop('sky', None)
DEFAULT_SHOT = 'storm_wide'


def _fill(sh, p):
    if 'fillfrom' in sh:
        return sh['fillfrom'] + (sh['fillto'] - sh['fillfrom']) * min(1, p * 1.2)
    return sh.get('fill', 0)


def camera(shot, sh, now, p):
    if sh.get('follow'):
        fr = point_at(_fill(sh, p) * TOT)
        return list(fr + [2.6, 0.8, 5.4]), list(fr)
    e = core.ease(p)
    a0, l0 = sh['cam']; a1, l1 = sh.get('cam2', sh['cam'])
    return [a0[k] + (a1[k] - a0[k]) * e for k in range(3)], [l0[k] + (l1[k] - l0[k]) * e for k in range(3)]


def build(shot, sh, now, p):
    S = Scene()
    if sh.get('gutter'):
        gutter(S, now)
    elif sh.get('norod'):
        world(S, 0, now, rod=False, strike=p > 0.25, burn=p > 0.4)
    else:
        world(S, _fill(sh, p), now, people=sh.get('people', False))
    return S


def post(img, shot, sh, now, p, cb):
    if sh.get('storm') or sh.get('gutter'):
        core.rain(img, now)
    f = _fill(sh, p)
    if (sh.get('flash') and 0.3 < f < 0.36) or (sh.get('norod') and 0.25 < p < 0.3):
        core.tint(img, (255, 255, 255, 120))
    if sh.get('danger'):
        core.tint(img, (229, 72, 77, int(14 + 10 * math.sin(now * 6))))
