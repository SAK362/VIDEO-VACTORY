"""Kit dunia: lift traksi (kabin, tali baja, roda puli, motor, pemberat, rel pemandu, governor, rem pengaman)."""
import math
import numpy as np
from .. import core
from ..core import Scene, PI, RZ90

FH = 1.5; NF = 5; TOP = FH * NF
SHX0, SHX1, SHZ0 = -0.85, 0.8, -0.75
SHEAVE = np.array([0.15, 8.15, 0.0]); SR = 0.4
_state = {'car': 3.0, 'cw': 3.1, 'wedge': 0}


def car_state(sh, now, p):
    carY = 3.0 + 2.4 * math.sin(now * 0.22)
    wedge = 0
    if sh.get('fall'):
        k = min(1, p * 1.7)
        carY = 4.2 - 2.9 * (k * k)
        wedge = 1 if p > 0.6 else 0
    _state.update(car=carY, cw=6.1 - carY, wedge=wedge)
    return carY, 6.1 - carY, wedge


def resolve(v):
    if isinstance(v, str):
        base = {'MID': (_state['car'] + 0.7 + _state['cw'] + 0.5) / 2, 'CAR': _state['car'] + 0.7, 'CW': _state['cw'] + 0.5, 'GOV': 8.0}
        for k, b in base.items():
            if v.startswith(k):
                return b + (float(v[len(k):]) if len(v) > len(k) else 0.0)
    return v


def resolve_point(pt, now, p):
    return [resolve(x) for x in pt]


def building(S, carY, cwY, ang, wedge, now, people=True):
    S.box([-0.3, -0.6, -0.4], [7.2, 1.2, 3.4], '#B98B66'); S.box([0, -0.05, 0], [1.6, 0.1, 1.5], '#8E969F')
    for x in (-0.25, 0.55):
        S.cyl([x, 0.22, 0], 0.12, 0.14, 0.45, '#E8B547', seg=10)
    for k in range(NF + 1):
        y = k * FH
        S.box([(-3.2 + SHX0) / 2, y - 0.06, -0.4], [SHX0 + 3.2, 0.12, 2.8], '#E9E4DA')
        S.box([(SHX1 + 2.6) / 2, y - 0.06, -0.4], [2.6 - SHX1, 0.12, 2.8], '#E9E4DA')
        S.box([(SHX0 + SHX1) / 2, y - 0.06, (-1.8 + SHZ0) / 2], [SHX1 - SHX0, 0.12, SHZ0 + 1.8], '#E9E4DA')
    S.box([-0.3, TOP / 2, -1.8], [5.8, TOP + 1.5, 0.12], '#EFE6D6')
    S.box([-3.2, TOP / 2, -0.4], [0.12, TOP, 2.8], '#E8DCC8'); S.box([2.6, TOP / 2, -0.4], [0.12, TOP, 2.8], '#E8DCC8')
    S.box([(SHX0 + SHX1) / 2, TOP / 2, SHZ0], [SHX1 - SHX0, TOP + 1.3, 0.06], '#C9CED4')
    S.box([SHX1, TOP / 2, 0], [0.06, TOP, 1.5], '#C9CED4')
    for k in range(NF):
        y = k * FH
        S.box([SHX0, y + FH * 0.5 + 0.62, 0], [0.06, FH * 0.5 - 0.1, 1.5], '#C9CED4')
        S.box([SHX0, y + 0.55, 0.6], [0.06, 1.1, 0.3], '#C9CED4'); S.box([SHX0, y + 0.55, -0.6], [0.06, 1.1, 0.3], '#C9CED4')
        S.box([SHX0 - 0.03, y + 0.55, -0.22], [0.03, 1.1, 0.42], '#AEB8C2'); S.box([SHX0 - 0.03, y + 0.55, 0.22], [0.03, 1.1, 0.42], '#B8C2CC')
        S.box([SHX0 - 0.04, y + 1.25, 0.0], [0.02, 0.12, 0.3], '#2E3A46')
        S.box([1.7, y + 0.4, -1.0], [1.0, 0.06, 0.6], '#B07A4A'); S.box([1.7, y + 0.2, -1.0], [0.9, 0.4, 0.5], '#9C6A3E')
        S.box([-2.6, y + 0.25, -1.2], [0.8, 0.1, 0.4], '#5BA7D6')
        S.sph([2.25, y + 0.45, 0.2], 0.25, '#3E9E58', 8, 5)
    S.box([-0.3, TOP + 0.03, -0.5], [2.4, 0.06, 2.4], '#DDD6C9'); S.box([-0.3, TOP + 1.4, -0.5], [2.4, 0.08, 2.4], '#D3CBBE')
    S.box([-0.3, TOP + 0.7, -1.7], [2.4, 1.4, 0.08], '#E4DCCD')
    for x in (-0.8, 0.3):
        S.box([x, TOP / 2, 0], [0.05, TOP, 0.08], '#7A838D')
    for x in (0.4, 0.7):
        S.box([x, TOP / 2, -0.25], [0.04, TOP, 0.06], '#7A838D')
    cy = carY
    S.box([-0.25, cy + 0.04, 0], [1.0, 0.08, 1.2], '#8E969F'); S.box([-0.25, cy + 1.32, 0], [1.0, 0.06, 1.2], '#8E969F')
    S.box([-0.25, cy + 0.68, -0.58], [1.0, 1.3, 0.04], '#D9CBB0'); S.box([0.24, cy + 0.68, 0], [0.04, 1.3, 1.2], '#CDBFA4')
    S.box([-0.74, cy + 0.68, -0.4], [0.04, 1.3, 0.4], '#CDBFA4'); S.box([-0.74, cy + 0.68, 0.4], [0.04, 1.3, 0.4], '#CDBFA4')
    S.box([-0.25, cy + 1.27, 0], [0.4, 0.03, 0.3], '#FFF2C2')
    S.box([-0.25, cy + 1.45, 0], [0.9, 0.08, 0.3], '#5E6978')
    for x in (-0.8, 0.3):
        S.box([x, cy + 0.1, 0], [0.16, 0.2, 0.2], '#F5B623' if wedge else '#C9A24A')
    S.box([0.55, cwY + 0.5, -0.25], [0.26, 1.0, 0.5], '#5E6978')
    for k in range(6):
        S.box([0.55, cwY + 0.1 + k * 0.16, -0.25], [0.27, 0.02, 0.51], '#4A5563')
    for dz in (-0.05, 0.05):
        S.seg([-0.25, cy + 1.49, dz], [-0.25, SHEAVE[1], dz], 0.015, '#2E3A46')
        S.seg([0.55, cwY + 1.0, dz - 0.25], [0.55, SHEAVE[1], dz], 0.015, '#2E3A46')
    S.cyl(SHEAVE, SR, SR, 0.22, '#F5B623', RZ90, 20)
    for k in range(8):
        a = k / 8 * 2 * PI - ang
        S.box(SHEAVE, [0.06, SR * 1.6, 0.24], '#C98A00', core.rz(a))
    S.cyl(SHEAVE + [0, 0, -0.55], 0.3, 0.3, 0.6, '#3E6FA8', RZ90, 16)
    for k in range(4):
        S.cyl(SHEAVE + [0, 0, -0.35 - k * 0.13], 0.33, 0.33, 0.04, '#5A86B8', RZ90, 16)
    S.cyl(SHEAVE + [0, 0, -0.9], 0.2, 0.2, 0.08, '#E5484D', RZ90, 14)
    S.box([SHEAVE[0], TOP + 0.2, -0.4], [0.9, 0.35, 0.9], '#4A5563')
    G = np.array([0.72, 8.0, 0.5])
    S.cyl(G, 0.15, 0.15, 0.08, '#2E9E6B', RZ90, 14)
    S.seg(G + [0.15, 0, 0], [0.87, 0.3, 0.5], 0.01, '#2E3A46')
    S.seg([0.3, cy + 0.2, 0], [0.87, cy + 0.2, 0.5], 0.012, '#2E3A46')
    if people:
        S.person(-0.45, cy + 0.08, 0.15, '#3B6EA5', h=0.95, hair='#1F1A17'); S.person(0.0, cy + 0.08, -0.2, '#E8835A', h=0.9, hair='#7A4A2A')
        S.person(-1.5, FH * 2, 0.3, '#2E9E6B', hair='#2B1D14'); S.person(-2.1, FH * 2, -0.4, '#F5B623', h=0.95, hair='#C98F4A')
        S.person(1.9, FH * 4, 0.2, '#8E5BA8', t=now, walk=True, hair='#1F1A17')


def seesaw(S, ang):
    S.box([0, -0.05, 0], [4, 0.1, 2.4], '#9CCB86')
    S.cyl([0, 0.25, 0], 0.05, 0.35, 0.5, '#E5484D', seg=4)
    S.box([0, 0.52, 0], [3.0, 0.08, 0.35], '#F5B623', core.rz(ang))
    for sx, c in ((-1.3, '#3B6EA5'), (1.3, '#E8835A')):
        S.person(sx * math.cos(ang), 0.56 + math.sin(ang) * sx, 0, c, h=0.6, hair='#1F1A17')


def L(id_, en): return {'id': id_, 'en': en}
CUT = L('ILUSTRASI · GEDUNG DIBELAH', 'ILLUSTRATION · BUILDING CUT OPEN')
SHOTS = {
    'building_wide': dict(desc='establishing: 5-floor building cut open, people waiting and riding the lift', cam=([-6.0, 5.2, 10.8], [-0.2, 3.8, -0.3]), cam2=([-4.6, 5.0, 11.2], [-0.2, 3.8, -0.3])),
    'shaft_reveal': dict(desc='building cut open: machine room on the roof and the car in the shaft', tag=CUT,
                         labels={'id': [('ruang mesin', [0.15, 8.2, -0.6], 'l', 'o'), ('kabin lift', [-0.25, 'CAR', 0.6], 'r', 'o')],
                                 'en': [('machine room', [0.15, 8.2, -0.6], 'l', 'o'), ('lift car', [-0.25, 'CAR', 0.6], 'r', 'o')]},
                         cam=([3.6, 5.6, 10.0], [0.0, 4.0, -0.3]), cam2=([2.6, 5.2, 9.4], [0.0, 4.0, -0.3])),
    'ropes_sheave': dict(desc='the car hangs on steel ropes that wrap over the sheave (pulley) on the roof', tag=CUT,
                         labels={'id': [('tali baja', [-0.25, 7.1, 0.05], 'l', 'o'), ('roda puli', [0.15, 8.55, 0.12], 'r', 'o')],
                                 'en': [('steel ropes', [-0.25, 7.1, 0.05], 'l', 'o'), ('sheave', [0.15, 8.55, 0.12], 'r', 'o')]},
                         cam=([2.8, 9.7, 3.8], [0.1, 7.6, 0]), cam2=([2.4, 9.4, 3.4], [0.1, 7.8, 0])),
    'motor_room': dict(desc='machine room opened: electric motor turns the sheave, with a brake disc', tag=L('ILUSTRASI · RUANG MESIN DIBUKA', 'ILLUSTRATION · MACHINE ROOM OPEN'),
                       labels={'id': [('motor listrik', [0.15, 8.15, -0.75], 'l', 'o'), ('rem', [0.15, 8.15, -0.95], 'r', 'g')],
                               'en': [('electric motor', [0.15, 8.15, -0.75], 'l', 'o'), ('brake', [0.15, 8.15, -0.95], 'r', 'g')]},
                       cam=([2.4, 9.2, 2.6], [0.2, 8.1, -0.3]), cam2=([2.0, 9.0, 2.2], [0.2, 8.1, -0.4])),
    'counterweight': dict(desc='counterweight on the other end of the ropes: car goes up, counterweight goes down', tag=CUT,
                          labels={'id': [('pemberat', [0.55, 'CW', 0.0], 'r', 'o'), ('kabin', [-0.74, 'CAR', 0.4], 'l', 'o')],
                                  'en': [('counterweight', [0.55, 'CW', 0.0], 'r', 'o'), ('car', [-0.74, 'CAR', 0.4], 'l', 'o')]},
                          cam=([3.2, 'MID+1.2', 8.6], [0.15, 'MID', -0.1]), cam2=([2.6, 'MID+1.0', 8.0], [0.15, 'MID', -0.1])),
    'seesaw_analogy': dict(desc='analogy: a seesaw with two equally heavy kids (separate set)', seesaw=True, tag=L('PERUMPAMAAN', 'ANALOGY'),
                           cam=([0.8, 2.6, 7.4], [0, 0.7, 0]), cam2=([0.3, 2.4, 6.8], [0, 0.7, 0])),
    'guide_rails': dict(desc='car and counterweight slide on guide rails so they do not sway', tag=CUT,
                        labels={'id': [('rel pemandu', [-0.8, 'CAR+0.9', 0.05], 'l', 'o')], 'en': [('guide rail', [-0.8, 'CAR+0.9', 0.05], 'l', 'o')]},
                        cam=([-2.6, 'CAR+0.9', 3.2], [-0.4, 'CAR-0.1', 0]), cam2=([-2.2, 'CAR+0.7', 2.8], [-0.4, 'CAR-0.1', 0])),
    'safety_danger': dict(desc='danger: car moves too fast, governor trips the safety brakes that clamp the rails (red tint)', danger=True, fall=True,
                          tag=L('ILUSTRASI · DISEDERHANAKAN', 'ILLUSTRATION · SIMPLIFIED'),
                          labels={'id': [('governor', [0.72, 'GOV', 0.5], 'r', 'g'), ('rem pengaman', [0.3, 'CAR-0.6', 0.1], 'l', 'o')],
                                  'en': [('governor', [0.72, 'GOV', 0.5], 'r', 'g'), ('safety brake', [0.3, 'CAR-0.6', 0.1], 'l', 'o')]},
                          cam=([2.6, 2.8, 4.4], [-0.2, 1.8, 0]), cam2=([2.4, 2.4, 4.0], [-0.2, 1.5, 0])),
    'data_card': dict(desc='wide view with the number card (card required)', card=True, cam=([-5.4, 5.0, 11.2], [-0.2, 3.8, -0.3]), cam2=([-6.0, 5.2, 11.6], [-0.2, 3.8, -0.3])),
    'outro_wide': dict(desc='ending wide shot of the building and lift', cam=([-4.6, 5.0, 11.2], [-0.2, 3.8, -0.3]), cam2=([-6.0, 5.2, 10.8], [-0.2, 3.8, -0.3])),
}
DEFAULT_SHOT = 'building_wide'


def camera(shot, sh, now, p):
    car_state(sh, now, p)
    e = core.ease(p)
    a0, l0 = [[resolve(v) for v in x] for x in sh['cam']]
    a1, l1 = [[resolve(v) for v in x] for x in sh.get('cam2', sh['cam'])]
    return [a0[k] + (a1[k] - a0[k]) * e for k in range(3)], [l0[k] + (l1[k] - l0[k]) * e for k in range(3)]


def build(shot, sh, now, p):
    S = Scene()
    if sh.get('seesaw'):
        seesaw(S, 0.12 * math.sin(now * 1.5))
        return S
    carY, cwY, wedge = _state['car'], _state['cw'], _state['wedge']
    building(S, carY, cwY, carY / SR, wedge, now)
    return S


def post(img, shot, sh, now, p, cb):
    if sh.get('danger'):
        core.tint(img, (229, 72, 77, int(14 + 10 * math.sin(now * 6))))
