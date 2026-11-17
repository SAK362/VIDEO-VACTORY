"""Latar statis (di-cache per adegan). Panggung aksi: y 480-1200. Horizon y=720. Tanah/pasir mulai y~1180."""
import math, random
from PIL import Image, ImageDraw
from draw import Pen, INK, W, H, mix

PAL = {
    "fajar": dict(st=(244, 168, 150), sb=(255, 232, 196), sea=(110, 160, 186), sea2=(58, 108, 148), gr=(236, 214, 170), hill=(150, 140, 160), sun=(255, 214, 160), sunxy=(300, 700), dark=0.0),
    "siang": dict(st=(88, 170, 214), sb=(250, 236, 200), sea=(64, 150, 196), sea2=(34, 100, 150), gr=(238, 214, 160), hill=(104, 140, 150), sun=(255, 240, 190), sunxy=(800, 560), dark=0.0),
    "senja": dict(st=(104, 112, 170), sb=(252, 178, 112), sea=(70, 96, 140), sea2=(34, 52, 88), gr=(222, 190, 140), hill=(110, 92, 120), sun=(255, 206, 130), sunxy=(780, 700), dark=0.08),
    "malam": dict(st=(12, 20, 50), sb=(46, 58, 104), sea=(26, 44, 78), sea2=(12, 24, 50), gr=(120, 104, 100), hill=(30, 40, 70), sun=(236, 236, 214), sunxy=(800, 420), dark=0.35),
}


def sky(d, pal):
    for y in range(0, 760):
        t = (y / 760.0) ** 1.3
        d.line([(0, y), (W, y)], fill=mix(pal["st"], pal["sb"], t))


def sea(d, pal, y0=720, y1=1100, seed=7):
    for y in range(y0, y1):
        t = (y - y0) / float(y1 - y0)
        d.line([(0, y), (W, y)], fill=mix(pal["sea2"], pal["sea"], 1 - t if False else t * 0.0 + (1 - t)))
    rnd = random.Random(seed)
    for i in range(46):
        y = y0 + 14 + i * (y1 - y0 - 20) / 46.0; x = rnd.randint(-40, 1040)
        d.line([(x, y), (x + 40 + i * 1.4, y - 2)], fill=mix(pal["sea"], (240, 250, 252), 0.7), width=3)


def hills(p, pal):
    c = pal["hill"]
    p.poly([0, 720, 0, 640, 140, 600, 260, 650, 380, 590, 520, 660, 640, 620, 760, 660, 900, 610, 1080, 650, 1080, 720], fill=c)
    p.poly([380, 590, 340, 640, 380, 626, 420, 650, 450, 620], fill=mix(c, (255, 244, 236), 0.6))


def beach(d, pal, y0=1060):
    d.polygon([(0, y0), (W, y0 - 40), (W, H), (0, H)], fill=pal["gr"])
    d.polygon([(0, y0), (W, y0 - 40), (W, y0 - 10), (0, y0 + 30)], fill=mix(pal["gr"], (255, 252, 240), 0.7))
    rnd = random.Random(3)
    for i in range(80):
        x = rnd.randint(0, 1070); y = rnd.randint(y0 + 60, H - 10)
        d.ellipse([x, y, x + rnd.randint(8, 26), y + 5], fill=mix(pal["gr"], (150, 110, 70), 0.25))


def clouds(p, pal, n=3):
    c = mix((255, 252, 244), pal["sb"], 0.25 + pal["dark"])
    for cx, cy, s in ((220, 420, 1.0), (760, 360, 1.3), (520, 560, 0.8))[:n]:
        for dx, dy, r in ((0, 0, 50), (55, -12, 62), (120, 4, 48), (60, 20, 56)):
            p.ell([cx + dx * s - r * s, cy + dy * s - r * .6 * s, cx + dx * s + r * s, cy + dy * s + r * .6 * s], fill=c)


def sun(p, pal):
    x, y = pal["sunxy"]
    p.ell([x - 70, y - 70, x + 70, y + 70], fill=mix(pal["sun"], pal["sb"], .5))
    p.ell([x - 46, y - 46, x + 46, y + 46], fill=pal["sun"])


def stars(d, seed=5):
    rnd = random.Random(seed)
    for i in range(70):
        x = rnd.randint(0, W); y = rnd.randint(30, 700); r = rnd.choice([2, 2, 3])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 250, 230))


def palm(p, x, y, h, lean):
    tx = x + lean
    p.line([x, y, x + lean * .4, y - h * .5, tx, y - h], (94, 60, 40), 12)
    for a in (-160, -125, -90, -55, -20):
        r = math.radians(a)
        ex = tx + math.cos(r) * 130; ey = y - h + math.sin(r) * 70 + 50
        p.line([tx, y - h, (tx + ex) / 2, (y - h + ey) / 2 - 30, ex, ey], (40, 110, 64), 11)
    p.ell([tx - 10, y - h - 6, tx + 10, y - h + 14], fill=(110, 70, 40))


def gonjong(p, x, y, w):
    u = w / 380.0; wh = 165
    p.rect([x + 20 * u, y - wh * u, x + w - 20 * u, y], fill=(138, 84, 56), out=INK, w=4 * u)
    for i in range(1, 8): p.line([x + 20 * u + i * (w - 40 * u) / 8, y - wh * u, x + 20 * u + i * (w - 40 * u) / 8, y], (100, 60, 40), 3 * u)
    for i in range(5): p.line([x + 40 * u + i * (w - 80 * u) / 4, y, x + 40 * u + i * (w - 80 * u) / 4, y + 24 * u], (90, 58, 40), 8 * u)
    d = wh - 120
    pts = [x - 10 * u, y - (120 + d) * u, x + 30 * u, y - (210 + d) * u, x + 70 * u, y - (290 + d) * u, x + 110 * u, y - (230 + d) * u, x + 170 * u, y - (170 + d) * u, x + 210 * u, y - (230 + d) * u, x + 250 * u, y - (290 + d) * u, x + 290 * u, y - (210 + d) * u, x + w + 10 * u, y - (120 + d) * u]
    p.poly(pts, fill=(60, 56, 64), out=INK, w=4 * u)
    p.rect([x + w / 2 - 30 * u, y - 125 * u, x + w / 2 + 30 * u, y], fill=(60, 36, 30), out=INK, w=3 * u)
    for i in range(3): p.rect([x + 50 * u + i * 70 * u, y - 135 * u, x + 84 * u + i * 70 * u, y - 90 * u], fill=(244, 208, 120), out=INK, w=2 * u)


def hut(p, x, y, w, col=(150, 100, 66)):
    wh = w * .55
    p.rect([x, y - wh, x + w, y], fill=col, out=INK, w=3)
    for i in range(1, 6): p.line([x + i * w / 6, y - wh, x + i * w / 6, y], mix(col, INK, .3), 2)
    p.poly([x - w * .05, y - wh, x + w / 2, y - w * 1.05, x + w * 1.05, y - wh], fill=(190, 150, 80), out=INK, w=3)
    p.rect([x + w * .4, y - w * .42, x + w * .6, y], fill=(70, 44, 34), out=INK, w=2)
    p.rect([x + w * .1, y - w * .42, x + w * .26, y - w * .26], fill=(244, 208, 120), out=INK, w=2)
    for i in range(3): p.line([x + 6 + i * w * .35, y, x + 6 + i * w * .35, y + w * .08], (90, 58, 40), 6)


def planks(p, y0, y1, col=(150, 100, 66), x0=-100, x1=1180):
    p.rect([x0, y0, x1, y1], fill=col)
    n = 8
    for i in range(n + 1):
        y = y0 + (y1 - y0) * i / n
        p.line([x0, y, x1, y], mix(col, INK, .55), 3)
    for i in range(14):
        x = x0 + (x1 - x0) * i / 14.0 + (30 if i % 2 else 0)
        yy = y0 + (y1 - y0) * (i % n) / n
        p.line([x, yy, x, yy + (y1 - y0) / n], mix(col, INK, .4), 2)


def pier(p, pal, y=1090):
    planks(p, y, y + 820)
    p.rect([-100, y - 8, 1180, y + 6], fill=(110, 70, 44), out=INK, w=3)
    for x in (80, 330, 580, 830, 1060):
        p.rect([x, y - 140, x + 22, y], fill=(110, 72, 46), out=INK, w=3)
    p.line([60, y - 110, 1100, y - 110], (130, 88, 56), 8)


def deck(p, pal):
    planks(p, 1060, 1920, col=(160, 108, 70))
    p.rect([-20, 920, 1100, 944], fill=(126, 82, 52), out=INK, w=3)
    for x in range(30, 1100, 140): p.rect([x, 944, x + 16, 1066], fill=(126, 82, 52), out=INK, w=3)
    p.rect([840, 220, 880, 1080], fill=(104, 66, 44), out=INK, w=4)
    p.poly([880, 250, 1100, 560, 880, 820], fill=(246, 238, 218), out=INK, w=4)
    p.line([-20, 940, 1100, 940], (90, 60, 40), 7)


def blob(p, pts, c): p.poly(pts, fill=c, out=mix(c, INK, .45), w=3)


def map_bg(d, p, kind):
    d.rectangle([0, 0, W, H], fill=(232, 214, 170))
    for y in range(0, H, 6): d.line([(0, y), (W, y)], fill=(226, 206, 160)) if (y // 6) % 3 == 0 else None
    p.rect([-20, -20, 1100, 1940], out=(150, 100, 60), w=16)
    for gx in range(0, 1080, 120): p.line([gx, 0, gx, H], (210, 188, 140), 2)
    for gy in range(0, H, 120): p.line([0, gy, W, gy], (210, 188, 140), 2)
    land = (122, 168, 104); sea_c = (176, 206, 206)
    p.rect([40, 40, 1040, 1880], fill=sea_c, out=(150, 100, 60), w=6)
    if kind == "sumbar":
        blob(p, [160, 300, 420, 400, 640, 560, 860, 760, 1000, 940, 1010, 1120, 760, 1240, 500, 1100, 300, 900, 200, 640, 140, 440], land)
        blob(p, [140, 1000, 200, 1060, 190, 1120, 130, 1080], land)  # pulau kecil
    else:
        for pts in ([100, 420, 330, 380, 520, 520, 420, 700, 200, 680], [420, 760, 760, 700, 900, 820, 700, 1000, 480, 960],
                    [180, 860, 330, 880, 300, 1040, 160, 1000], [640, 380, 900, 360, 980, 520, 760, 560],
                    [260, 1180, 520, 1160, 560, 1280, 330, 1320], [700, 1120, 960, 1100, 1000, 1240, 760, 1260]):
            blob(p, pts, land)


# ---- mode lapisan (2.5D): "all" = satu gambar, "far" = langit/bukit/matahari/awan, "near" = laut/darat/rumah/dermaga ----
MODE = "all"
def _wrap(name, modes):
    fn = globals()[name]
    def w(*a, **k):
        if MODE in modes: return fn(*a, **k)
    w.__name__ = name; globals()[name] = w
for _n in ("sky", "stars", "sun", "clouds", "hills"): _wrap(_n, ("all", "far"))
for _n in ("sea", "beach", "palm", "gonjong", "hut", "pier", "deck", "planks", "map_bg"): _wrap(_n, ("all", "near"))
def near_ok(): return MODE != "far"
def far_ok(): return MODE != "near"
