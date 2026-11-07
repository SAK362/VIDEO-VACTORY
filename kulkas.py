"""Kit dunia: kulkas (siklus cairan pendingin: kompresor -> kondensor -> kapiler -> evaporator)."""
import math
import numpy as np
from .. import core
from ..core import Scene

FR = np.array([1.2, 0.0, -1.4])


def L3(p):
    return FR + np.array(p, float)


def serp(x0, x1, y0, y1, z, n):
    pts = []
    for i in range(n + 1):
        y = y0 + (y1 - y0) * i / n
        a, b = (x0, x1) if i % 2 == 0 else (x1, x0)
        pts += [[a, y, z], [b, y, z]]
    return pts


COND = serp(0.3, -0.3, 0.35, 1.65, -0.41, 7)
EVAP = serp(-0.3, 0.3, 1.42, 1.72, -0.27, 3)
LOOP = ([[0.2, 0.18, -0.5], [0.3, 0.3, -0.45]] + COND + [[-0.42, 1.65, -0.41], [-0.42, 1.55, -0.27], [-0.3, 1.42, -0.27]] + EVAP[1:]
        + [[0.36, 1.72, -0.27], [0.36, 1.72, -0.45], [0.36, 0.3, -0.5], [0.2, 0.18, -0.5]])
LOOPW = [L3(p) for p in LOOP]
SEGL = [float(np.linalg.norm(LOOPW[i + 1] - LOOPW[i])) for i in range(len(LOOPW) - 1)]
TOT = sum(SEGL)
N_COND_END = 2 + len(COND)
N_EVAP_START = N_COND_END + 3
N_EVAP_END = N_EVAP_START + len(EVAP) - 1
SKY = ((236, 232, 224), (244, 240, 232))


def seg_color(i):
    if i < 2:
        return '#E5484D'
    if i < N_COND_END - 1:
        return ['#E5484D', '#F07A3A', '#F5A04A'][min(2, (i - 2) * 3 // len(COND))]
    if i < N_EVAP_START:
        return '#E8B547'
    if i < N_EVAP_END:
        return '#3FA9E8'
    return '#8FD0F0'


def pos_on(d):
    for i, Ls in enumerate(SEGL):
        if d <= Ls:
            return LOOPW[i] + (LOOPW[i + 1] - LOOPW[i]) * (d / Ls)
        d -= Ls
    return LOOPW[-1]


def kitchen(S, backwall=True):
    S.box([0, -0.05, -0.5], [7, 0.1, 5], '#E7DCCB')
    for i in range(7):
        for j in range(5):
            if (i + j) % 2:
                S.box([-2.5 + i * 1.0, 0.002, -2.0 + j * 1.0], [0.98, 0.004, 0.98], '#DCCFBB')
    if backwall:
        S.box([0, 1.5, -2.55], [7, 3, 0.1], '#F2EBDD')
    S.box([-3.05, 1.5, -0.5], [0.1, 3, 5], '#EADFCB')
    S.box([-1.7, 0.45, -2.15], [2.2, 0.9, 0.6], '#B07A4A')
    S.box([-1.7, 0.92, -2.15], [2.3, 0.05, 0.65], '#E8E2D8')
    S.box([-1.7, 1.9, -2.48], [1.2, 0.8, 0.03], '#9FD8F5')
    S.box([-1.7, 1.9, -2.47], [0.04, 0.8, 0.03], '#FFFFFF')
    S.cyl([-2.5, 1.06, -2.2], 0.12, 0.09, 0.22, '#C46A3A', seg=10)
    S.sph([-2.5, 1.3, -2.2], 0.18, '#3E9E58', 8, 5)


def fridge(S, cut=False, run=True, flow=1.0, now=0.0, doors=True):
    body = '#F3F5F7'
    S.box(L3([0, 0.04, 0]), [0.8, 0.08, 0.7], '#D4D9DE')
    S.box(L3([0, 1.78, 0]), [0.8, 0.04, 0.7], body)
    S.box(L3([-0.38, 0.9, 0]), [0.04, 1.8, 0.7], body)
    S.box(L3([0.38, 0.9, 0]), [0.04, 1.8, 0.7], body)
    S.box(L3([0, 0.9, -0.33]), [0.8, 1.8, 0.04], '#E6EAEE')
    S.box(L3([0, 1.3, 0]), [0.72, 0.05, 0.64], '#E6EAEE')
    if not cut and doors:
        S.box(L3([0, 1.55, 0.37]), [0.8, 0.48, 0.05], body)
        S.box(L3([0, 0.66, 0.37]), [0.8, 1.26, 0.05], body)
        S.box(L3([0.3, 1.45, 0.41]), [0.04, 0.2, 0.04], '#9FB4C8')
        S.box(L3([0.3, 0.95, 0.41]), [0.04, 0.3, 0.04], '#9FB4C8')
    else:
        for y in (0.5, 0.9):
            S.box(L3([0, y, 0.02]), [0.72, 0.02, 0.6], '#DCEAF3')
        S.box(L3([-0.15, 0.62, 0.05]), [0.18, 0.2, 0.16], '#E5484D')
        S.cyl(L3([0.15, 0.65, 0.1]), 0.05, 0.05, 0.25, '#3E9E58', seg=10)
        S.sph(L3([0.0, 0.98, 0.12]), 0.07, '#F5B623', 8, 5)
        S.sph(L3([0.14, 0.98, 0.05]), 0.07, '#F5B623', 8, 5)
        S.box(L3([-0.15, 1.02, 0.08]), [0.2, 0.18, 0.18], '#5BA7D6')
        a = now * 8 if run else 0
        for k in range(4):
            S.box(L3([0.25, 1.55, -0.22]) + np.array([math.cos(a + k * 1.57) * 0.05, math.sin(a + k * 1.57) * 0.05, 0]),
                  [0.09, 0.03, 0.01], '#C9D3DC', core.rz(a + k * 1.57))
    vib = math.sin(now * 60) * 0.004 if run else 0
    S.cyl(L3([0.2 + vib, 0.12, -0.5]), 0.14, 0.15, 0.2, '#2B2F35')
    S.sph(L3([0.2 + vib, 0.22, -0.5]), 0.14, '#2B2F35', 10, 6)
    for i in range(len(LOOPW) - 1):
        S.seg(LOOPW[i], LOOPW[i + 1], 0.014, '#3B3F45')
    for x in np.linspace(-0.32, 0.32, 9):
        S.seg(L3([x, 0.33, -0.42]), L3([x, 1.67, -0.42]), 0.005, '#22262B')
    left = flow * TOT
    for i, Ls in enumerate(SEGL):
        if left <= 0:
            break
        k = min(1, left / Ls)
        S.seg(LOOPW[i], LOOPW[i] + (LOOPW[i + 1] - LOOPW[i]) * k, 0.022, seg_color(i))
        left -= Ls
    if run and flow > 0.05:
        for j in range(18):
            d = (now * 0.9 + j / 18 * TOT) % TOT
            if d <= flow * TOT:
                S.sph(pos_on(d), 0.02, '#FFFFFF', 6, 4)


def heat_out(S, now, n=12, spread=1.0, rise=1.3):
    for j in range(n):
        k = (now * 0.5 + j / n) % 1
        S.sph(L3([-0.3 + 0.6 * ((j * 0.37) % 1), 0.4 + rise * k, -0.5 - 0.5 * k * spread]), 0.035 + 0.02 * k, '#FF8A3D' if j % 2 else '#FFB24A', 6, 4)


def heat_in(S, now):
    for j in range(8):
        k = (now * 0.5 + j / 8) % 1
        a = L3([-0.15 + 0.3 * ((j * 0.53) % 1), 0.7 + 0.3 * ((j * 0.31) % 1), 0.1])
        b = L3([0, 1.55, -0.26])
        S.sph(a + (b - a) * k, 0.025, '#FFB24A' if k < 0.6 else '#8FD0F0', 6, 4)


def sponge(S, now):
    S.box([0, -0.05, 0], [4, 0.1, 2.4], '#E7DCCB')
    S.box([-0.9, 0.1, 0], [1.2, 0.2, 1.0], '#5BA7D6')
    S.box([0.9, 0.1, 0], [1.2, 0.2, 1.0], '#B8C2CC')
    sq = 0.5 + 0.5 * math.sin(now * 2)
    S.box([-0.9, 0.35, 0], [0.6, 0.3, 0.4], '#F5D04A')
    S.box([0.9, 0.4 - 0.1 * sq, 0], [0.6, 0.3 * (1 - 0.4 * sq), 0.4], '#F5D04A')
    for j in range(5):
        k = (now * 1.2 + j / 5) % 1
        S.sph([0.75 + 0.08 * j, 0.3 - 0.25 * k, 0.1], 0.04, '#FF8A3D', 6, 4)


def L(id_, en): return {'id': id_, 'en': en}
CUT = L('ILUSTRASI · KULKAS DIBELAH', 'ILLUSTRATION · FRIDGE CUT OPEN')
WALL = L('ILUSTRASI · TEMBOK DIBUKA', 'ILLUSTRATION · WALL REMOVED')
SHOTS = {
    'kitchen_wide': dict(desc='establishing: kitchen, a person opens the fridge', people=True, open=True,
                         cam=([-2.0, 1.9, 3.8], [0.6, 1.0, -1.2]), cam2=([-1.4, 1.8, 3.4], [0.8, 1.0, -1.3])),
    'heat_moves': dict(desc='key idea: heat goes from inside to the back of the fridge (orange particles)', heat=True, hin=True, open=True,
                       labels={'id': [('panas dibuang', [1.2, 1.4, -2.0], 'r', 'o')], 'en': [('heat released', [1.2, 1.4, -2.0], 'r', 'o')]},
                       cam=([3.6, 1.8, 1.6], [1.2, 1.0, -1.5]), cam2=([3.4, 1.9, 1.0], [1.2, 1.0, -1.6])),
    'fridge_cut': dict(desc='cutaway: fridge cut open, refrigerant pipe loop visible', cut=True, tag=CUT,
                       labels={'id': [('pipa evaporator', [1.2, 1.6, -1.67], 'r', 'g'), ('rak makanan', [1.0, 0.9, -1.3], 'l', 'o')],
                               'en': [('evaporator pipe', [1.2, 1.6, -1.67], 'r', 'g'), ('food shelf', [1.0, 0.9, -1.3], 'l', 'o')]},
                       cam=([2.4, 1.7, 1.4], [1.2, 0.95, -1.45]), cam2=([2.1, 1.6, 1.1], [1.2, 0.95, -1.5])),
    'compressor': dict(desc='step: compressor at the lower back squeezes the gas until hot (red)', noback=True, tag=WALL, flowfrom=0.0, flowto=0.15,
                       labels={'id': [('kompresor', [1.4, 0.2, -1.9], 'r', 'o')], 'en': [('compressor', [1.4, 0.2, -1.9], 'r', 'o')]},
                       cam=([3.0, 1.0, -3.9], [1.3, 0.35, -1.85]), cam2=([2.6, 0.9, -3.6], [1.35, 0.35, -1.85])),
    'condenser': dict(desc='step: hot gas in the coils at the back releases heat into the room', noback=True, heat=True, tag=WALL, flowfrom=0.15, flowto=0.6,
                      labels={'id': [('kisi kondensor', [1.2, 1.2, -1.81], 'r', 'o')], 'en': [('condenser coils', [1.2, 1.2, -1.81], 'r', 'o')]},
                      cam=([2.4, 1.7, -4.4], [1.2, 1.0, -1.8]), cam2=([2.0, 1.6, -4.0], [1.2, 1.0, -1.8])),
    'capillary': dict(desc='step: narrow capillary tube, pressure drops and it turns very cold', noback=True, tag=WALL, flowfrom=0.6, flowto=0.72,
                      labels={'id': [('pipa kapiler', [0.78, 1.6, -1.73], 'l', 'o')], 'en': [('capillary tube', [0.78, 1.6, -1.73], 'l', 'o')]},
                      cam=([3.2, 1.9, -2.8], [1.0, 1.55, -1.75]), cam2=([2.9, 1.8, -2.5], [0.9, 1.55, -1.7])),
    'evaporator': dict(desc='step: cold pipe inside absorbs heat from the food, gas returns to compressor', cut=True, hin=True, tag=CUT, flowfrom=0.72, flowto=1.0,
                       labels={'id': [('evaporator', [1.2, 1.58, -1.67], 'r', 'g')], 'en': [('evaporator', [1.2, 1.58, -1.67], 'r', 'g')]},
                       cam=([1.9, 1.6, 0.3], [1.2, 1.3, -1.6]), cam2=([1.8, 1.7, 0.1], [1.2, 1.45, -1.65])),
    'sponge_analogy': dict(desc='analogy: a sponge soaks up inside and is squeezed outside (separate set)', sponge=True, tag=L('PERUMPAMAAN', 'ANALOGY'),
                           labels={'id': [('serap di dalam', [-0.9, 0.5, 0.2], 'l', 'g'), ('peras di luar', [0.9, 0.5, 0.2], 'r', 'o')],
                                   'en': [('soak inside', [-0.9, 0.5, 0.2], 'l', 'g'), ('squeeze outside', [0.9, 0.5, 0.2], 'r', 'o')]},
                           cam=([0.2, 2.8, 6.2], [0, 0.35, 0]), cam2=([0.1, 2.6, 5.6], [0, 0.35, 0])),
    'wall_danger': dict(desc='danger: coils blocked by a wall or dust, heat cannot escape, compressor overworks (red tint)', danger=True, noback=True, heat=True,
                        tag=L('ILUSTRASI · DISEDERHANAKAN', 'ILLUSTRATION · SIMPLIFIED'),
                        labels={'id': [('mepet tembok', [1.2, 1.3, -1.85], 'r', 'o')], 'en': [('too close to wall', [1.2, 1.3, -1.85], 'r', 'o')]},
                        cam=([2.8, 3.4, 0.9], [1.2, 0.9, -1.85]), cam2=([2.6, 3.2, 0.6], [1.2, 0.9, -1.85])),
    'data_card': dict(desc='wide view with the number card (card required)', card=True,
                      cam=([-2.4, 2.4, 4.8], [0.2, 1.0, -1.2]), cam2=([-2.8, 2.4, 5.2], [0.2, 1.0, -1.2])),
    'outro_wide': dict(desc='ending: kitchen wide with the person', people=True,
                       cam=([-1.4, 1.8, 3.4], [0.8, 1.0, -1.3]), cam2=([-2.0, 1.9, 3.8], [0.6, 1.0, -1.2])),
}
DEFAULT_SHOT = 'kitchen_wide'


def build(shot, sh, now, p):
    S = Scene()
    if sh.get('sponge'):
        sponge(S, now)
        return S
    kitchen(S, backwall=not sh.get('noback'))
    flow = sh.get('flow', 1.0)
    if 'flowfrom' in sh:
        flow = sh['flowfrom'] + (sh['flowto'] - sh['flowfrom']) * min(1, p * 1.2)
    fridge(S, cut=sh.get('cut', False), flow=flow, now=now, doors=not sh.get('open'))
    if sh.get('heat'):
        dg = sh.get('danger')
        heat_out(S, now, n=24 if dg else 12, spread=0.1 if dg else 1.0, rise=2.4 if dg else 1.3)
    if sh.get('hin'):
        heat_in(S, now)
    if sh.get('danger'):
        S.box([1.2, 1.5, -1.98], [1.8, 3.0, 0.06], '#E4DCCD')
    if sh.get('people'):
        S.person(0.2, 0, -0.6, '#3B6EA5', hair='#1F1A17')
    return S


def post(img, shot, sh, now, p, cb):
    if sh.get('danger'):
        core.tint(img, (229, 72, 77, int(14 + 10 * math.sin(now * 6))))
