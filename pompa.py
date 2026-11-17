"""Kit dunia: pompa air sumur (pompa sentrifugal permukaan + pipa hisap + katup kaki)."""
import json, math
import numpy as np
from .. import core
from ..core import Scene, PI

D = json.load(open(core.DATA('pump_world.json')))
PATH = [np.array(p, float) for p in D['path']]
SEGL = [float(np.linalg.norm(PATH[i + 1] - PATH[i])) for i in range(len(PATH) - 1)]
TOT = sum(SEGL)
RECOLOR = {'grass': '#9CCB86', 'topsoil': '#B98B66', 'clay': '#C99B78', 'sand': '#E2CDA3', 'aquifer': '#8CC8E6',
           'bedrock': '#A3ABB5', 'house': '#F2EBDD', 'roof': '#D98A6A', 'well': '#C9CED4', 'water_table': '#D8F1FF',
           'sink': '#F7F5F0', 'tap': '#C9D3DC', 'pump': '#C3C9CF', 'foot_valve': '#E8B547'}
PUMPCOL = {'#3B6EA5': '#5A86B8', '#2A4A73': '#46688F', '#1B3A63': '#5C6F86', '#16365F': '#56687E', '#3F6A9C': '#6890BD', '#5B8FC7': '#7FA7D1'}


def _col(p):
    c = p['color']
    if p['id'] == 'house' and c in ('#9FD8F5', '#8A5A3B', '#FFE08A', '#C46A3A', '#3E9E58', '#FFFFFF'):
        return c
    if p['id'] == 'yard':
        return {'#3E9E58': '#7DB36A', '#4FB86A': '#93C67E', '#7A4E2D': '#8B6A4E'}.get(c, '#C8A27A')
    return RECOLOR.get(p['id'], c)


def point_at(d):
    for i, L in enumerate(SEGL):
        if d <= L:
            return PATH[i] + (PATH[i + 1] - PATH[i]) * (d / L)
        d -= L
    return PATH[-1]


def world(S, fill, cut, spin, now):
    for p in D['env']:
        S.prim(p, _col(p))
    for sg in D['segs']:
        a, b = PATH[sg['i']], PATH[sg['i'] + 1]
        polys = core.segpolys(a, b, sg['r'], bool(sg.get('half')))
        if sg.get('half') == 'z':
            polys = [q for q in polys if np.mean(q, axis=0)[2] <= a[2] + 1e-6]
        elif sg.get('half') == 'y':
            polys = [q for q in polys if np.mean(q, axis=0)[1] <= a[1] + 1e-6]
        S.add(polys, '#9DB8D6' if sg['r'] > 0.1 else '#C9D3DC')
    for i in (1, 2, 5, 6, 7):
        S.seg(PATH[i] - [0, 0.12, 0], PATH[i] + [0, 0.12, 0], 0.15, '#9DB8D6')
    left = fill * TOT
    for i in range(len(PATH) - 1):
        if left <= 0:
            break
        k = min(1, left / SEGL[i])
        S.seg(PATH[i], PATH[i] + (PATH[i + 1] - PATH[i]) * k, 0.125 if i < 5 else 0.085, '#3FA9E8')
        left -= SEGL[i]
    if fill > 0.05:
        for j in range(16):
            d = (now * 1.6 + j / 16 * TOT) % TOT
            if d < fill * TOT:
                S.sph(point_at(d) + [0, 0, 0.05], 0.04, '#D8F1FF', 6, 4)
    wb = core.tr(core.boxm(0.88, 1.0, 0.43), [0.9, -4.5, 0.575])
    S.add([q for q in wb if np.mean(q, axis=0)[1] > -4.05 or np.mean(q, axis=0)[2] < 0.4], '#A8DBF3')
    P = np.array(D['pumpPos'])
    RY = core.ry(PI / 2)
    sc = 0.55
    cz = 3 + (P[2] + 0.02 - 3) * cut
    for part in D['pump']:
        if cut == 0 and part['id'] in ('impeller', 'rotor', 'shaft'):
            continue
        RS = core.rz(spin * (1.4 if part['id'] == 'fan' else 1.0)) if part['id'] in ('impeller', 'rotor', 'shaft', 'fan') else np.eye(3)
        for p in part['prims']:
            R = core.eul(p.get('rot') or [0, 0, 0])
            t = np.array(p['pos'])
            polys = [[RY @ (sc * (RS @ (R @ v + t))) + P for v in q] for q in core.mesh(p)]
            if part['shell'] and cut > 0:
                polys = [q for q in polys if np.mean(q, axis=0)[2] <= cz]
            S.add(polys, PUMPCOL.get(p['color'], p['color']))


def straw(S, now, k):
    S.box([0, 0, 0], [3.0, 0.15, 2.0], '#C9A27A')
    S.cyl([0, 0.85, 0], 0.42, 0.36, 1.5, '#E3EEF4', seg=20)
    S.cyl([0, 0.6, 0], 0.39, 0.35, 0.95, '#6FB7E0', seg=20)
    R = core.rz(0.25)
    S.add(core.tr(core.cylm(0.05, 0.05, 2.0, 12), [0.1, 1.25, 0], R), '#E5484D')
    L = 0.3 + 1.4 * k
    S.add(core.tr(core.cylm(0.035, 0.035, L, 10), [0.1 - math.sin(0.25) * (1.0 - L / 2), 1.25 - math.cos(0.25) * (1.0 - L / 2), 0], R), '#3FA9E8')


def arrows(S, now):
    for x in (0.65, 0.9, 1.15):
        y = -3.35 + 0.12 * math.sin(now * 4 + x * 5)
        S.seg([x, y + 0.45, 0.72], [x, y + 0.12, 0.72], 0.025, '#FFFFFF')
        S.add(core.tr(core.cylm(0.0, 0.07, 0.16, 8), [x, y + 0.04, 0.72]), '#FFFFFF')


def L(id_, en):
    return {'id': id_, 'en': en}


SHOTS = {
    'house_wide': dict(desc='establishing: house, kitchen, yard, pump and the ground cut open down to the water layer', people=True, fill=0,
                       cam=([-5.6, 2.6, 12.6], [-1.0, -1.2, -0.6]), cam2=([-3.6, 2.2, 12.8], [-0.9, -1.2, -0.6])),
    'ground_cut': dict(desc='the ground is cut open: suction pipe going down into the water layer', fill=0,
                       tag=L('ILUSTRASI · TANAH DIBELAH', 'ILLUSTRATION · GROUND CUT OPEN'),
                       labels={'id': [('pipa hisap', [0.9, -2.2, 0.58], 'l', 'o'), ('lapisan air', [1.7, -4.6, 0.82], 'r', 'g')],
                               'en': [('suction pipe', [0.9, -2.2, 0.58], 'l', 'o'), ('water layer', [1.7, -4.6, 0.82], 'r', 'g')]},
                       cam=([3.0, -0.4, 9.6], [0.2, -2.6, 0]), cam2=([3.4, -1.0, 8.6], [0.5, -3.0, 0])),
    'foot_valve': dict(desc='close-up of the one-way foot valve at the bottom of the suction pipe in the well', fill=0.12,
                       tag=L('ILUSTRASI · SUMUR DIBELAH', 'ILLUSTRATION · WELL CUT OPEN'),
                       labels={'id': [('katup kaki', [0.9, -4.67, 0.82], 'r', 'o')], 'en': [('foot valve', [0.9, -4.67, 0.82], 'r', 'o')]},
                       cam=([2.4, -3.2, 4.4], [0.9, -4.3, 0.58]), cam2=([2.0, -3.5, 3.8], [0.9, -4.4, 0.58])),
    'pump_close': dict(desc='close-up of the pump next to the house (priming, outside view)', fill=0,
                       tag=L('ILUSTRASI · DISEDERHANAKAN', 'ILLUSTRATION · SIMPLIFIED'),
                       labels={'id': [('pompa air', [-0.2, 1.6, -0.6], 'r', 'o')], 'en': [('water pump', [-0.2, 1.6, -0.6], 'r', 'o')]},
                       cam=([2.8, 2.7, 4.4], [-0.35, 1.1, -0.6]), cam2=([1.8, 2.5, 4.8], [-0.35, 1.1, -0.6])),
    'pump_cutaway': dict(desc='the pump is cut open: motor spins the impeller, water is flung outward', fill=0.35, cut=1, run=True,
                         tag=L('ILUSTRASI · POMPA DIBELAH', 'ILLUSTRATION · PUMP CUT OPEN'),
                         labels={'id': [('impeler', [-0.2, 1.15, -0.6], 'r', 'o'), ('motor listrik', [-1.0, 0.95, -0.6], 'l', 'o')],
                                 'en': [('impeller', [-0.2, 1.15, -0.6], 'r', 'o'), ('electric motor', [-1.0, 0.95, -0.6], 'l', 'o')]},
                         cam=([1.5, 1.9, 3.9], [-0.3, 1.0, -0.6]), cam2=([0.9, 1.8, 3.6], [-0.3, 1.0, -0.6])),
    'impeller_eye': dict(desc='very close on the impeller centre where pressure becomes low', fill=0.4, cut=1, run=True,
                         tag=L('ILUSTRASI · POMPA DIBELAH', 'ILLUSTRATION · PUMP CUT OPEN'),
                         labels={'id': [('tekanan rendah', [0.0, 0.9, -0.55], 'r', 'g')], 'en': [('low pressure', [0.0, 0.9, -0.55], 'r', 'g')]},
                         cam=([1.0, 1.5, 2.6], [-0.1, 0.9, -0.6]), cam2=([0.8, 1.35, 2.3], [-0.1, 0.9, -0.6])),
    'water_rises': dict(desc='camera follows water rising up the cut-open suction pipe; air pressure arrows push on the well water', fillfrom=0.05, fillto=0.55, run=True, follow=True, arrows=True,
                        tag=L('ILUSTRASI · PIPA DIBELAH', 'ILLUSTRATION · PIPE CUT OPEN'),
                        labels={'id': [('tekanan udara', [0.9, -3.2, 0.72], 'l', 'g')], 'en': [('air pressure', [0.9, -3.2, 0.72], 'l', 'g')]},
                        cam=([0, 0, 0], [0, 0, 1])),
    'straw_analogy': dict(desc='analogy: drinking with a straw (separate small set with a glass and straw)', straw=True,
                          tag=L('PERUMPAMAAN', 'ANALOGY'),
                          labels={'id': [('sedotan = pipa hisap', [0.25, 1.8, 0], 'r', 'o')], 'en': [('straw = suction pipe', [0.25, 1.8, 0], 'r', 'o')]},
                          cam=([1.6, 2.5, 4.8], [0, 0.9, 0]), cam2=([1.2, 2.3, 4.2], [0, 1.0, 0])),
    'leak_danger': dict(desc='danger: the foot valve leaks and water drains back down the pipe (red tint)', fillfrom=0.55, fillto=0.08, danger=True,
                        tag=L('ILUSTRASI · SUMUR DIBELAH', 'ILLUSTRATION · WELL CUT OPEN'),
                        labels={'id': [('air turun lagi', [0.9, -1.6, 0.58], 'r', 'o')], 'en': [('water drains back', [0.9, -1.6, 0.58], 'r', 'o')]},
                        cam=([3.0, -1.2, 7.2], [0.6, -2.6, 0]), cam2=([2.8, -1.6, 6.6], [0.7, -3.0, 0])),
    'data_card': dict(desc='wide view with the number card (card required)', fill=1, run=True, card=True,
                      cam=([-5.0, 2.4, 12.6], [-0.9, -1.4, -0.6]), cam2=([-5.6, 2.6, 13.0], [-0.9, -1.4, -0.6])),
    'tap_outro': dict(desc='water comes out of the tap in the kitchen; ending', fill=1, run=True, people=True, stream=True,
                      labels={'id': [('keran', [-2.8, 1.55, -0.35], 'r', 'g')], 'en': [('tap', [-2.8, 1.55, -0.35], 'r', 'g')]},
                      cam=([-1.2, 2.4, 4.6], [-2.8, 1.3, -0.5]), cam2=([-0.6, 2.6, 6.0], [-2.4, 1.1, -0.5])),
}
DEFAULT_SHOT = 'house_wide'


def _fill(sh, p):
    if 'fillfrom' in sh:
        return sh['fillfrom'] + (sh['fillto'] - sh['fillfrom']) * min(1, p * 1.15)
    return sh.get('fill', 0)


def camera(shot, sh, now, p):
    if sh.get('follow'):
        fr = point_at(_fill(sh, p) * TOT)
        return list(fr + [1.6, 0.8, 5.6]), list(fr + [-0.2, 0, 0])
    e = core.ease(p)
    a0, l0 = sh['cam']
    a1, l1 = sh.get('cam2', sh['cam'])
    return [a0[k] + (a1[k] - a0[k]) * e for k in range(3)], [l0[k] + (l1[k] - l0[k]) * e for k in range(3)]


def build(shot, sh, now, p):
    S = Scene()
    if sh.get('straw'):
        straw(S, now, min(1, p * 1.3))
        return S
    spin = now * 3.0 if (sh.get('run') or sh.get('cut')) else 0.0
    world(S, _fill(sh, p), sh.get('cut', 0), spin, now)
    if sh.get('people'):
        S.person(-2.8, 0.12, 0.15, '#E8835A', hair='#1F1A17', pants='#3E4A5A')
    if sh.get('arrows'):
        arrows(S, now)
    if sh.get('stream'):
        S.seg([-2.8, 1.5, -0.35], [-2.8, 1.03, -0.35], 0.03, '#3FA9E8')
    return S


def post(img, shot, sh, now, p, cb):
    if sh.get('danger'):
        core.tint(img, (229, 72, 77, int(14 + 10 * math.sin(now * 6))))
