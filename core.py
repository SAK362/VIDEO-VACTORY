"""Mesin gambar CurioSphere: geometri 3D sederhana, z-buffer, dan lapisan teks (gaya "cerita teknik").

Semua koordinat tata letak teks ditulis untuk kanvas acuan 540x960 lalu dikalikan K,
sehingga video bisa dirender di 540, 720, atau 1080 lebar tanpa mengubah tata letak.
"""
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PI = math.pi
HERE = os.path.dirname(os.path.abspath(__file__))
ASSET = lambda *p: os.path.join(HERE, 'assets', *p)
DATA = lambda *p: os.path.join(HERE, 'data', *p)

# ---------------------------------------------------------------- ukuran
W, H, K = 540, 960, 1.0


def init(width=720):
    global W, H, K
    W = int(width)
    H = int(round(width * 16 / 9))
    K = W / 540.0


def s(v):
    return int(round(v * K))


_fonts = {}


def font(kind, size):
    key = (kind, size, K)
    if key not in _fonts:
        path = ASSET('DejaVuSansMono.ttf' if kind == 'mono' else 'DejaVuSans-Bold.ttf')
        _fonts[key] = ImageFont.truetype(path, max(6, s(size)))
    return _fonts[key]


# ---------------------------------------------------------------- geometri
def rx(a):
    c, n = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -n], [0, n, c]])


def ry(a):
    c, n = math.cos(a), math.sin(a)
    return np.array([[c, 0, n], [0, 1, 0], [-n, 0, c]])


def rz(a):
    c, n = math.cos(a), math.sin(a)
    return np.array([[c, -n, 0], [n, c, 0], [0, 0, 1]])


def eul(r):
    return rx(r[0]) @ ry(r[1]) @ rz(r[2])


RZ90 = rx(PI / 2)  # silinder dengan sumbu z


def cylm(rt, rb, h, seg=16, open_=False):
    P = []
    T = [np.array([rt * math.cos(2 * PI * i / seg), h / 2, rt * math.sin(2 * PI * i / seg)]) for i in range(seg)]
    B = [np.array([rb * math.cos(2 * PI * i / seg), -h / 2, rb * math.sin(2 * PI * i / seg)]) for i in range(seg)]
    for i in range(seg):
        j = (i + 1) % seg
        P.append([B[i], B[j], T[j], T[i]])
    if not open_:
        P.append(T[::-1])
        P.append(B)
    return P


def boxm(x, y, z):
    v = lambda a, b, c: np.array([a * x / 2, b * y / 2, c * z / 2])
    F = [[(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)], [(1, -1, -1), (-1, -1, -1), (-1, 1, -1), (1, 1, -1)],
         [(-1, 1, 1), (1, 1, 1), (1, 1, -1), (-1, 1, -1)], [(-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)],
         [(1, -1, 1), (1, -1, -1), (1, 1, -1), (1, 1, 1)], [(-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1)]]
    return [[v(*p) for p in f] for f in F]


def usphere(r, seg=10, ring=7):
    V = [[np.array([r * math.sin(PI * i / ring) * math.cos(2 * PI * j / seg), r * math.cos(PI * i / ring),
                    r * math.sin(PI * i / ring) * math.sin(2 * PI * j / seg)]) for j in range(seg)] for i in range(ring + 1)]
    P = []
    for i in range(ring):
        for j in range(seg):
            k = (j + 1) % seg
            P.append([V[i][j], V[i + 1][j], V[i + 1][k], V[i][k]])
    return P


def mesh(p):
    k = p['kind']
    sz = p['size']
    if k == 'box':
        return boxm(*sz)
    if k == 'cyl':
        return cylm(sz[0], sz[1], sz[2])
    if k == 'sphere':
        return usphere(sz[0], 10, 6)
    return cylm(0.01, sz[0], sz[1], int(sz[2]) if len(sz) > 2 else 10)


def tr(pl, t, R=None):
    R = np.eye(3) if R is None else R
    t = np.array(t, float)
    return [[R @ v + t for v in q] for q in pl]


def _align(u):
    up = np.array([0, 1.0, 0])
    v = np.cross(up, u)
    if np.linalg.norm(v) < 1e-6:
        return np.eye(3) if u[1] > 0 else rx(PI)
    v /= np.linalg.norm(v)
    ang = math.acos(np.clip(np.dot(up, u), -1, 1))
    Kx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + math.sin(ang) * Kx + (1 - math.cos(ang)) * Kx @ Kx


def segpolys(a, b, r, open_=False, seg=12):
    a = np.array(a, float)
    b = np.array(b, float)
    d = b - a
    L = np.linalg.norm(d)
    if L < 1e-6:
        return []
    R = _align(d / L)
    return tr(cylm(r, r, L, seg, open_), (a + b) / 2, R)


class Scene:
    """Penampung poligon: (titik-titik, warna hex)."""

    def __init__(self):
        self.P = []

    def add(self, polys, col):
        self.P.extend((q, col) for q in polys)

    def box(self, c, sz, col, R=None):
        self.add(tr(boxm(*sz), c, R), col)

    def cyl(self, c, r0, r1, h, col, R=None, seg=14):
        self.add(tr(cylm(r0, r1, h, seg), c, R), col)

    def sph(self, c, r, col, seg=10, ring=6):
        self.add(tr(usphere(r, seg, ring), c), col)

    def seg(self, a, b, r, col):
        self.add(segpolys(a, b, r), col)

    def limb(self, a, b, r0, r1, col):
        a = np.array(a, float)
        b = np.array(b, float)
        d = b - a
        L = np.linalg.norm(d)
        if L < 1e-6:
            return
        self.add(tr(cylm(r1, r0, L, 10), (a + b) / 2, _align(d / L)), col)
        self.add(tr(usphere(r1 * 1.02, 8, 5), b), col)

    def person(self, x, y, z, shirt, h=1.0, t=0.0, walk=False, hair='#3B2A20', pants='#3E4A5A', skin='#F0C9A0'):
        sc = h
        sw = math.sin(t * 4) * 0.25 if walk else 0.0
        hip = np.array([x, y + 0.5 * sc, z])
        sh = np.array([x, y + 0.92 * sc, z])
        for side, ph in ((-1, sw), (1, -sw)):
            hp = hip + [0, 0, side * 0.07 * sc]
            ft = hp + [math.sin(ph) * 0.18 * sc, -0.46 * sc, 0]
            self.limb(hp, ft, 0.06 * sc, 0.05 * sc, pants)
            self.box(ft + [0.04 * sc, -0.02 * sc, 0], [0.16 * sc, 0.06 * sc, 0.09 * sc], '#2B2B2B')
        self.cyl([x, y + 0.72 * sc, z], 0.12 * sc, 0.1 * sc, 0.46 * sc, shirt, seg=12)
        self.sph([x, y + 0.93 * sc, z], 0.125 * sc, shirt, 10, 5)
        for side, ph in ((-1, -sw), (1, sw)):
            a = sh + [0, 0, side * 0.15 * sc]
            hand = a + [math.sin(ph) * 0.14 * sc, -0.4 * sc, side * 0.03 * sc]
            self.limb(a, hand, 0.045 * sc, 0.04 * sc, shirt)
            self.sph(hand, 0.045 * sc, skin, 8, 4)
        self.cyl([x, y + 1.04 * sc, z], 0.045 * sc, 0.05 * sc, 0.08 * sc, skin, seg=8)
        head = np.array([x, y + 1.17 * sc, z])
        self.sph(head, 0.12 * sc, skin, 12, 8)
        hairp = [q for q in tr(usphere(0.127 * sc, 12, 8), head + [-0.012 * sc, 0.025 * sc, 0])
                 if np.mean(q, axis=0)[1] > head[1] + 0.01 * sc or np.mean(q, axis=0)[0] < head[0] - 0.05 * sc]
        self.add(hairp, hair)

    def prim(self, p, color=None, M=None, t=None):
        """Primitif dari JSON (kind/pos/rot/size/color) dengan transformasi tambahan M,t."""
        R = eul(p.get('rot') or [0, 0, 0])
        pos = np.array(p['pos'], float)
        polys = [[R @ v + pos for v in q] for q in mesh(p)]
        if M is not None:
            polys = [[M @ v + t for v in q] for q in polys]
        self.add(polys, color or p['color'])


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


_hexcache = {}


def hexcc(h):
    if h not in _hexcache:
        _hexcache[h] = hexc(h)
    return _hexcache[h]


# ---------------------------------------------------------------- kamera & z-buffer
FOV = 50.0
NEAR = 0.12


def cam_basis(pos, look):
    pos = np.array(pos, float)
    look = np.array(look, float)
    f = look - pos
    f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1, 0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return pos, f, r, u


def project(p, cb):
    pos, f, r, u = cb
    d = np.array(p, float) - pos
    z = np.dot(d, f)
    fy = 1 / math.tan(math.radians(FOV / 2))
    asp = W / H
    if z < 1e-3:
        z = 1e-3
    return (W / 2 + np.dot(d, r) / z * fy / asp * W / 2, H / 2 - np.dot(d, u) / z * fy * H / 2), z


def _clip_near(P):
    out = []
    n = len(P)
    for i in range(n):
        a = P[i]
        b = P[(i + 1) % n]
        ia = a[2] >= NEAR
        ib = b[2] >= NEAR
        if ia:
            out.append(a)
        if ia != ib:
            t = (NEAR - a[2]) / (b[2] - a[2])
            out.append(a + (b - a) * t)
    return out


def render3d(scene, cb, sky_top=(196, 224, 242), sky_bot=(244, 240, 232), ss=2):
    pos, f, r, u = cb
    Wp, Hp = W * ss, H * ss
    fy = 1 / math.tan(math.radians(FOV / 2))
    asp = W / H
    top = np.array(sky_top, float)
    bot = np.array(sky_bot, float)
    yy = np.clip(np.arange(Hp) / (Hp * 0.8), 0, 1)[:, None]
    img = np.repeat((top + (bot - top) * yy)[:, None, :], Wp, axis=1)
    zb = np.zeros((Hp, Wp))
    Lg = np.array([3, 8, 5.0])
    Lg /= np.linalg.norm(Lg)
    M = np.stack([r, u, f])
    for q, col in scene.P:
        Q = np.asarray(q, float)
        n = np.cross(Q[1] - Q[0], Q[2] - Q[0])
        nn = np.linalg.norm(n)
        if nn < 1e-12:
            continue
        n /= nn
        if np.dot(n, Q.mean(axis=0) - pos) > 0:
            n = -n
        C = (Q - pos) @ M.T
        if (C[:, 2] < NEAR).all():
            continue
        if (C[:, 2] < NEAR).any():
            C = np.array(_clip_near(list(C)))
            if len(C) < 3:
                continue
        sx = Wp / 2 + C[:, 0] / C[:, 2] * fy / asp * Wp / 2
        sy = Hp / 2 - C[:, 1] / C[:, 2] * fy * Hp / 2
        if sx.max() < 0 or sx.min() > Wp or sy.max() < 0 or sy.min() > Hp:
            continue
        iz = 1 / C[:, 2]
        k = max(0, np.dot(n, Lg))
        sk = max(0, n[1]) * 0.12
        cc = np.clip(hexcc(col) * (0.62 + 0.38 * k + sk) + np.array([6, 8, 14]), 0, 255)
        for j in range(1, len(C) - 1):
            x0, y0, x1, y1, x2, y2 = sx[0], sy[0], sx[j], sy[j], sx[j + 1], sy[j + 1]
            area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
            if abs(area) < 1e-9:
                continue
            bx0 = max(int(math.floor(min(x0, x1, x2))), 0)
            bx1 = min(int(math.ceil(max(x0, x1, x2))), Wp - 1)
            by0 = max(int(math.floor(min(y0, y1, y2))), 0)
            by1 = min(int(math.ceil(max(y0, y1, y2))), Hp - 1)
            if bx0 > bx1 or by0 > by1:
                continue
            X, Y = np.meshgrid(np.arange(bx0, bx1 + 1) + 0.5, np.arange(by0, by1 + 1) + 0.5)
            w0 = ((x1 - X) * (y2 - Y) - (x2 - X) * (y1 - Y)) / area
            w1 = ((x2 - X) * (y0 - Y) - (x0 - X) * (y2 - Y)) / area
            w2 = 1 - w0 - w1
            m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not m.any():
                continue
            z = w0 * iz[0] + w1 * iz[j] + w2 * iz[j + 1]
            sub = zb[by0:by1 + 1, bx0:bx1 + 1]
            m &= z > sub
            sub[m] = z[m]
            img[by0:by1 + 1, bx0:bx1 + 1][m] = cc
    im = Image.fromarray(img.astype(np.uint8))
    if ss > 1:
        im = im.resize((W, H), Image.LANCZOS)
    return im


# ---------------------------------------------------------------- lapisan teks
ORANGE = (232, 120, 40)
GREEN = (46, 150, 110)
NAVY = (11, 31, 58)
IVORY = (247, 243, 234)


def hatch(img, box):
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = max(1, x1 - x0), max(1, y1 - y0)
    tile = Image.new('RGB', (w, h), (245, 182, 35))
    td = ImageDraw.Draw(tile)
    step = max(4, s(9))
    for x in range(-h, w, step):
        td.line([(x, h), (x + h, 0)], fill=(201, 138, 0), width=max(1, s(3)))
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], s(8), fill=255)
    img.paste(tile, (x0, y0), m)


def overlay(img, kicker, heading, keys, labels=(), tag=None, card=None, cb=None):
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([0, 0, W, s(118)], fill=(246, 243, 236, 235))
    d.text((s(22), s(24)), (kicker or '').upper(), font=font('b', 12), fill=(120, 128, 138))
    x = s(22)
    keyset = {k.strip('*,.?!').lower() for k in (keys or [])}
    fh = font('b', 25)
    words = (heading or '').replace('*', '').split(' ')
    y = s(44)
    for w in words:
        ww = d.textlength(w + ' ', font=fh)
        if x + ww > W - s(18):
            x = s(22)
            y += s(30)
        c = GREEN if w.strip(',.?!').lower() in keyset else NAVY
        d.text((x, y), w, font=fh, fill=c)
        x += ww
    if tag:
        ft = font('mono', 11)
        tw = d.textlength(tag, font=ft)
        d.rectangle([s(22), s(300), s(30) + tw + s(8), s(318)], fill=(255, 255, 255, 235), outline=(40, 40, 40))
        d.text((s(30), s(303)), tag, font=ft, fill=(30, 30, 30))
    fl = font('b', 14)
    for text, pt3, side, colr in labels:
        if cb is None:
            continue
        (px, py), z = project(pt3, cb)
        if z <= 0.05 or not (-W * 0.2 < px < W * 1.2 and -H * 0.2 < py < H * 1.2):
            continue
        tw = d.textlength(text, font=fl)
        lx = s(26) if side == 'l' else W - s(26) - tw - s(20)
        ly = py - s(70) if py > s(200) else py + s(50)
        ly = min(max(ly, s(128)), s(640))
        d.line([(lx + (tw + s(20) if side == 'l' else 0), ly + s(13)), (px, py)], fill=(40, 40, 40), width=max(1, s(2)))
        d.ellipse([px - s(4), py - s(4), px + s(4), py + s(4)], fill=(40, 40, 40))
        d.rounded_rectangle([lx, ly, lx + tw + s(20), ly + s(26)], s(6), fill=colr)
        d.text((lx + s(10), ly + s(5)), text, font=fl, fill=(255, 255, 255))
    if card:
        d.rounded_rectangle([s(60), s(150), W - s(60), s(250)], s(14), fill=(255, 255, 255, 240), outline=(30, 30, 30), width=max(1, s(2)))
        d.text((s(80), s(160)), str(card.get('label', '')).upper()[:48], font=font('mono', 11), fill=(90, 90, 90))
        d.text((s(80), s(178)), str(card.get('value', ''))[:22], font=font('b', 40), fill=NAVY)
        d.text((s(80), s(228)), ('Sumber: ' + str(card.get('source', '')))[:70], font=font('mono', 10), fill=(110, 110, 110))
    return img


def subtitle(img, words, active, done_upto):
    """words: daftar kata frasa; active: indeks kata yang sedang diucapkan."""
    if not words:
        return
    d = ImageDraw.Draw(img, 'RGBA')
    size = 21
    fs = font('b', size)
    tw = sum(d.textlength(w + ' ', font=fs) for w in words)
    while tw > W - s(56) and size > 13:
        size -= 1
        fs = font('b', size)
        tw = sum(d.textlength(w + ' ', font=fs) for w in words)
    d.rounded_rectangle([W / 2 - tw / 2 - s(14), s(694), W / 2 + tw / 2 + s(10), s(734)], s(11), fill=(20, 34, 44, 225))
    x = W / 2 - tw / 2
    for j, w in enumerate(words):
        ww = d.textlength(w, font=fs)
        if j == active:
            hatch(img, (x - s(3), s(699), x + ww + s(3), s(729)))
            d = ImageDraw.Draw(img, 'RGBA')
            d.text((x, s(701)), w, font=fs, fill=NAVY)
        else:
            d.text((x, s(701)), w, font=fs, fill=IVORY if j <= done_upto else (180, 190, 200))
        x += d.textlength(w + ' ', font=fs)


_curio = None


def brand(img, now):
    global _curio
    if _curio is None:
        c = Image.open(ASSET('curio.png')).convert('RGBA')
        hh = s(170)
        _curio = c.resize((int(c.width * hh / c.height), hh), Image.LANCZOS)
    bob = int(s(3) * math.sin(now * 3))
    img.paste(_curio, (s(16), s(752) + bob), _curio)
    d = ImageDraw.Draw(img, 'RGBA')
    d.rounded_rectangle([W - s(142), s(918), W - s(14), s(944)], s(13), fill=(11, 31, 58, 215))
    d.text((W - s(128), s(924)), 'CurioSphere', font=font('b', 13), fill=IVORY)


def tint(img, rgba):
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([0, 0, W, H], fill=rgba)


def rain(img, now, n=70):
    import random
    rnd = random.Random(int(now * 12))
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(n):
        x = rnd.uniform(0, W)
        y = rnd.uniform(s(110), H)
        d.line([(x, y), (x - s(6), y + s(22))], fill=(220, 230, 240, 120), width=max(1, s(1)))


def ease(p):
    return p * p * (3 - 2 * p)
