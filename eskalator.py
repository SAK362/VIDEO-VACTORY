"""Kit dunia: eskalator di mal (rantai anak tangga, roda gigi penggerak, dua rel, pelat sisir, pegangan)."""
import math
import numpy as np
from .. import core
from ..core import Scene, PI, RZ90

RISE = 3.5; X0 = -3.0; X1 = 3.0; M = RISE / (X1 - X0); XB = -4.6; XT = 4.6; D = 0.42; WD = 1.0; K = 3.5
sp = lambda t: math.log1p(math.exp(K * t)) / K
sg = lambda t: 1 / (1 + math.exp(-K * t))
def Y(x): return M * (sp(x - X0) - sp(x - X1))
def slope(x): return M * (sg(x - X0) - sg(x - X1))


def steps(S, t, cut):
    off = (t * 0.45) % D
    n = int((XT - XB) / D)
    for i in range(n):
        x = XB + i * D + off
        if x > XT - D * 0.5:
            continue
        y0 = Y(x); y1 = Y(x + D); r = max(0.0, y1 - y0)
        S.box([x + D / 2, y0 - 0.035, 0], [D * 0.97, 0.07, WD], '#C9CDD2')
        for g in range(5):
            S.box([x + D / 2, y0 + 0.002, -0.4 + g * 0.2], [D * 0.9, 0.01, 0.05], '#9AA1A9')
        S.box([x + D / 2, y0 - 0.035, 0.5], [D * 0.97, 0.072, 0.03], '#F2C230')
        if r > 0.02:
            S.box([x + D - 0.01, y0 + r / 2, 0], [0.03, r, WD], '#B6BCC3')
        body = 0.18 + r
        S.box([x + D / 2, y0 - 0.07 - body / 2, 0], [D * 0.8, body, WD * 0.9], '#8E969F')
        if cut:
            for z in (-0.52, 0.52):
                S.cyl([x + D * 0.85, y0 - 0.2, z], 0.07, 0.07, 0.06, '#2E3A46', RZ90, 10)
                S.cyl([x + D * 0.15, y0 - 0.2 - 0.3 * min(1, slope(x) / M), z], 0.07, 0.07, 0.06, '#2E3A46', RZ90, 10)
    for i in range(n):
        x = XT - (i * D + off)
        if x < XB + D * 0.5:
            continue
        y = Y(x) - 1.05
        S.box([x - D / 2, y, 0], [D * 0.97, 0.07, WD], '#9EA5AD')
        S.box([x - D / 2, y + 0.16, 0], [D * 0.8, 0.22, WD * 0.9], '#7F8790')


def rails(S, cut):
    if not cut:
        return
    xs = np.linspace(XB, XT, 26)
    for a, b in zip(xs[:-1], xs[1:]):
        for z in (-0.6, 0.6):
            S.seg([a, Y(a) - 0.29, z], [b, Y(b) - 0.29, z], 0.03, '#E67E22')
            S.seg([a, Y(a) - 0.29 - 0.3 * min(1, slope(a) / M), z], [b, Y(b) - 0.29 - 0.3 * min(1, slope(b) / M), z], 0.03, '#2E9E6B')
        S.seg([a, Y(a) - 0.32, 0], [b, Y(b) - 0.32, 0], 0.025, '#3B3F45')
        S.seg([a, Y(a) - 0.85, 0], [b, Y(b) - 0.85, 0], 0.025, '#3B3F45')


def gears(S, t):
    for (cx, cy, rr, col) in [(XT + 0.25, RISE - 0.55, 0.5, '#F5B623'), (XB - 0.25, -0.55, 0.5, '#D9DDE2')]:
        S.cyl([cx, cy, 0], rr, rr, 0.25, col, RZ90, 18)
        for k in range(12):
            a = k / 12 * 2 * PI - t * 1.0
            S.box([cx + math.cos(a) * (rr + 0.06), cy + math.sin(a) * (rr + 0.06), 0], [0.12, 0.12, 0.24], col)
        S.cyl([cx, cy, 0], 0.08, 0.08, 1.3, '#5E6978', RZ90, 10)


def machine(S, t):
    S.cyl([5.6, 2.55, 0], 0.42, 0.42, 0.9, '#3E6FA8', RZ90, 16)
    for k in range(5):
        S.cyl([5.6, 2.55, -0.35 + k * 0.17], 0.46, 0.46, 0.04, '#5A86B8', RZ90, 16)
    S.box([5.6, 2.12, 0], [1.2, 0.12, 0.9], '#4A5563')
    S.cyl([5.15, 2.55, 0], 0.17, 0.17, 0.12, '#F5B623', RZ90, 12)
    S.seg([5.15, 2.72, 0.12], [XT + 0.25, RISE - 0.05, 0.12], 0.03, '#2E3A46')
    S.seg([5.15, 2.38, 0.12], [XT + 0.25, RISE - 1.05, 0.12], 0.03, '#2E3A46')
    S.box([6.3, 2.6, -0.2], [0.3, 0.6, 0.4], '#2E9E5B')


def handrail(S):
    xs = np.linspace(XB - 0.4, XT + 0.4, 28)
    for z in (-0.62, 0.62):
        for a, b in zip(xs[:-1], xs[1:]):
            S.seg([a, Y(a) + 1.0, z], [b, Y(b) + 1.0, z], 0.05, '#1E2328')
    for a, b in zip(xs[:-1], xs[1:]):
        S.add([[np.array([a, Y(a) + 0.05, -0.6]), np.array([b, Y(b) + 0.05, -0.6]), np.array([b, Y(b) + 0.95, -0.6]), np.array([a, Y(a) + 0.95, -0.6])]], '#D7E7EE')


def cladding(S, cut):
    if cut:
        return
    xs = np.linspace(XB - 0.5, XT + 0.5, 30)
    for a, b in zip(xs[:-1], xs[1:]):
        S.add([[np.array([a, Y(a) - 1.5, 0.64]), np.array([b, Y(b) - 1.5, 0.64]), np.array([b, Y(b) + 0.04, 0.64]), np.array([a, Y(a) + 0.04, 0.64])]], '#C3CAD2')


def comb(S):
    for (x, y, sgn) in [(XT - 0.05, RISE, 1), (XB + 0.05, 0.0, -1)]:
        S.box([x + sgn * 0.25, y + 0.02, 0], [0.5, 0.04, WD + 0.1], '#D9DDE2')
        S.box([x, y + 0.03, 0], [0.08, 0.05, WD + 0.1], '#F2C230')
        for g in range(9):
            S.box([x - sgn * 0.07, y + 0.02, -0.45 + g * 0.11], [0.12, 0.03, 0.04], '#F2C230')


def mall(S, cut, opentop=False):
    S.box([0, -0.25, -1.5], [16, 0.5, 9], '#E7E1D6')
    if opentop:
        S.box([6.4, RISE - 0.25, -3.4], [3.6, 0.5, 5.2], '#E9E4DA')
        S.box([6.4, RISE - 0.25, -0.79], [3.6, 0.5, 0.02], '#C9C2B4')
    else:
        S.box([6.4, RISE - 0.25, -1.5], [3.6, 0.5, 9], '#E9E4DA')
    if not cut:
        S.box([6.0, 2.4, 0.0], [2.0, 1.8, 1.6], '#D7D2C8')
    S.box([5.0, 1.6, -2.4], [0.4, 3.2, 0.4], '#D9D3C7')
    S.box([0, 4.2, -6.0], [16, 8.4, 0.3], '#F1ECE2')
    for x, c in [(-5.2, '#E8835A'), (-2.0, '#5BA7D6'), (1.2, '#7DBB72')]:
        S.box([x, 1.3, -5.8], [2.6, 2.2, 0.12], '#FBF8F2'); S.box([x, 2.6, -5.78], [2.6, 0.4, 0.12], c)
    for x, c in [(5.4, '#C77DBA'), (7.6, '#F0B44A')]:
        S.box([x, RISE + 1.3, -5.8], [2.0, 2.0, 0.12], '#FBF8F2'); S.box([x, RISE + 2.5, -5.78], [2.0, 0.4, 0.12], c)
    for x in np.linspace(4.7, 8.1, 6):
        S.seg([x, RISE, 0.8], [x, RISE + 1.0, 0.8], 0.02, '#B8C2CC')
    S.seg([4.7, RISE + 1.0, 0.8], [8.1, RISE + 1.0, 0.8], 0.04, '#9AA4AE')


def people(S, t):
    off = (t * 0.45) % D
    for k, c, hr, pn in [(4, '#E5484D', '#3B2A20', '#2F3B4C'), (9, '#3B6EA5', '#1F1A17', '#6B5B4B'), (13, '#2E9E6B', '#7A4A2A', '#3E4A5A')]:
        x = XB + k * D + off + 0.2
        S.person(x, Y(x - 0.2), 0.1, c, hair=hr, pants=pn)
    wx = -5.6 + ((t * 0.35) % 2.0)
    S.person(wx, 0, 1.3, '#F5B623', t=t, walk=True, hair='#2B1D14', pants='#4A5A6A')
    S.person(-6.6, 0, -1.6, '#8E5BA8', hair='#C98F4A', pants='#2F3B4C')
    S.person(7.2, RISE, -1.0, '#E8835A', hair='#1F1A17', pants='#3E4A5A')


def wheel_closeup(S, t):
    S.box([0, 0.5, 0], [1.2, 0.1, 1.6], '#C9CDD2')
    for g in range(7):
        S.box([0, 0.555, -0.6 + g * 0.2], [1.1, 0.012, 0.06], '#9AA1A9')
    S.box([0, 0.2, 0], [0.9, 0.5, 1.4], '#8E969F'); S.box([0.58, 0.05, 0], [0.04, 0.8, 1.6], '#B6BCC3')
    a = t * 3
    for z in (-0.82, 0.82):
        for (x, y) in ((0.45, -0.12), (-0.45, -0.42)):
            S.cyl([x, y, z], 0.14, 0.14, 0.1, '#2E3A46', RZ90, 14)
            S.box([x + math.cos(a) * 0.08, y + math.sin(a) * 0.08, z + 0.06 * np.sign(z)], [0.05, 0.05, 0.02], '#C9CDD2')
        S.seg([-1.8, -0.28, z], [1.8, -0.28, z], 0.04, '#E67E22')
        S.seg([-1.8, -0.58, z], [1.8, -0.58, z], 0.04, '#2E9E6B')
    S.seg([-1.8, -0.05, 0], [1.8, -0.05, 0], 0.035, '#3B3F45')


def L(id_, en): return {'id': id_, 'en': en}

CUT_TAG = L('ILUSTRASI · RANGKA DIBELAH', 'ILLUSTRATION · TRUSS CUT OPEN')
SHOTS = {
    'mall_wide': dict(desc='establishing: two-floor mall, people riding the escalator', cam=([-7.0, 5.8, 11.5], [0.8, 1.8, 0]), cam2=([-5.0, 5.2, 10.5], [0.8, 1.8, 0])),
    'truss_cut': dict(desc='side panel removed: steps loop around, upper run and return run underneath', cut=True, tag=CUT_TAG,
                      labels={'id': [('jalur naik', [0.0, Y(0.0) + 0.1, 0.5], 'l', 'o'), ('jalur balik di bawah', [1.0, Y(1.0) - 1.0, 0.5], 'r', 'g')],
                              'en': [('upper run', [0.0, Y(0.0) + 0.1, 0.5], 'l', 'o'), ('return run below', [1.0, Y(1.0) - 1.0, 0.5], 'r', 'g')]},
                      cam=([-3.8, 3.4, 8.8], [0.6, 1.0, 0]), cam2=([-1.8, 3.2, 8.2], [0.8, 1.2, 0])),
    'motor_room': dict(desc='machine space under the top landing: electric motor turns the big drive gear', cut=True, opentop=True,
                       tag=L('ILUSTRASI · RUANG MESIN DIBUKA', 'ILLUSTRATION · MACHINE SPACE OPEN'),
                       labels={'id': [('motor listrik', [5.6, 2.55, 0.45], 'r', 'o'), ('roda gigi penggerak', [XT + 0.25, RISE - 0.55, 0.13], 'l', 'o')],
                               'en': [('electric motor', [5.6, 2.55, 0.45], 'r', 'o'), ('drive gear', [XT + 0.25, RISE - 0.55, 0.13], 'l', 'o')]},
                       cam=([8.4, 4.6, 5.6], [4.9, 2.7, 0]), cam2=([7.6, 4.2, 4.8], [4.9, 2.7, 0])),
    'step_chain': dict(desc='the step chain pulls every step up; rails and wheels visible', cut=True, tag=CUT_TAG,
                       labels={'id': [('rantai anak tangga', [0.6, Y(0.6) - 0.32, 0.1], 'r', 'o')], 'en': [('step chain', [0.6, Y(0.6) - 0.32, 0.1], 'r', 'o')]},
                       cam=([-1.6, 2.6, 5.6], [0.2, 0.8, 0]), cam2=([0.4, 3.0, 5.2], [1.2, 1.4, 0])),
    'wheels_two_rails': dict(desc='one step enlarged: two pairs of wheels on two different rails', wheel=True,
                             tag=L('ILUSTRASI · SATU ANAK TANGGA', 'ILLUSTRATION · ONE STEP'),
                             labels={'id': [('rel roda depan', [1.2, -0.28, 0.82], 'r', 'o'), ('rel roda belakang', [-1.2, -0.58, 0.82], 'l', 'g')],
                                     'en': [('front wheel rail', [1.2, -0.28, 0.82], 'r', 'o'), ('rear wheel rail', [-1.2, -0.58, 0.82], 'l', 'g')]},
                             cam=([2.6, 1.6, 3.8], [0, 0.0, 0]), cam2=([3.0, 1.3, 3.2], [0, 0.0, 0])),
    'steps_flatten': dict(desc='at the top the two rails come together so the steps become flat', cut=True, tag=CUT_TAG,
                          labels={'id': [('dua rel menyatu', [3.9, RISE - 0.3, 0.6], 'l', 'g')], 'en': [('rails come together', [3.9, RISE - 0.3, 0.6], 'l', 'g')]},
                          cam=([6.0, 4.8, 3.8], [3.6, 3.0, 0]), cam2=([5.4, 4.5, 3.3], [3.8, 3.1, 0])),
    'comb_danger': dict(desc='danger: the gap at the end, comb plate teeth mesh into the step grooves (red tint)', danger=True,
                        tag=L('ILUSTRASI · DISEDERHANAKAN', 'ILLUSTRATION · SIMPLIFIED'),
                        labels={'id': [('pelat sisir', [XT - 0.05, RISE + 0.05, 0.4], 'r', 'o')], 'en': [('comb plate', [XT - 0.05, RISE + 0.05, 0.4], 'r', 'o')]},
                        cam=([6.0, 4.6, 2.6], [4.4, 3.5, 0]), cam2=([5.7, 4.4, 2.2], [4.5, 3.5, 0])),
    'handrail': dict(desc='the handrail is driven by the same gear and moves with the steps',
                     labels={'id': [('pegangan tangan', [-0.6, Y(-0.6) + 1.0, 0.62], 'r', 'o')], 'en': [('handrail', [-0.6, Y(-0.6) + 1.0, 0.62], 'r', 'o')]},
                     cam=([-2.6, 3.6, 6.0], [-0.4, 2.6, 0.6]), cam2=([-1.2, 3.8, 5.4], [0.4, 3.0, 0.6])),
    'data_card': dict(desc='wide view with the number card (card required)', card=True, cam=([-6.0, 5.6, 11.0], [0.8, 1.8, 0]), cam2=([-6.6, 5.8, 11.6], [0.8, 1.8, 0])),
    'outro_wide': dict(desc='ending wide shot of the mall escalator', cam=([-5.0, 5.2, 10.5], [0.8, 1.8, 0]), cam2=([-7.0, 5.8, 11.5], [0.8, 1.8, 0])),
}
DEFAULT_SHOT = 'mall_wide'


def build(shot, sh, now, p):
    S = Scene()
    if sh.get('wheel'):
        wheel_closeup(S, now)
        return S
    cut = sh.get('cut', False)
    mall(S, cut, sh.get('opentop', False)); steps(S, now, cut); rails(S, cut); gears(S, now); machine(S, now); handrail(S); cladding(S, cut); comb(S); people(S, now)
    return S


def post(img, shot, sh, now, p, cb):
    if sh.get('danger'):
        core.tint(img, (229, 72, 77, int(14 + 10 * math.sin(now * 6))))
