"""Properti, efek, dan perakit latar. Semua kunci dari spec harus ada di PROPS / FX / LATAR; kunci tak dikenal dicatat WARN (tidak membuat render gagal)."""
import math, random, os
from PIL import Image, ImageDraw, ImageFont
from draw import Pen, INK, W, H, mix, layer
import lib_bg as B

HERE = os.path.dirname(os.path.abspath(__file__))
def font(sz, mono=False):
    return ImageFont.truetype(os.path.join(HERE, "fonts", "DejaVuSansMono.ttf" if mono else "DejaVuSans-Bold.ttf"), int(sz))


def text(p, x, y, s, size, fill, anchor="mm", mono=False):
    f = font(size * p.k, mono)
    p.d.text((p.X(x), p.Y(y)), s, font=f, fill=fill, anchor=anchor)


def ship(p, x, y, w, t=0.0, gold=False, rock=0.0, parts=0.0):
    u = w / 400.0; by = math.sin(t * 1.6) * 5 * u; y = y + by
    hull = (150, 60, 48) if not gold else (132, 46, 44)
    p.poly([x - 20 * u, y + 10 * u, x + w + 20 * u, y + 10 * u, x + w - 30 * u, y + 90 * u, x + 30 * u, y + 90 * u], fill=hull, out=INK, w=3 * u)
    p.rect([x + 30 * u, y + 10 * u, x + w - 30 * u, y + 24 * u], fill=(232, 178, 62), out=INK, w=2 * u)
    for i in range(6): p.ell([x + 60 * u + i * 52 * u, y + 46 * u, x + 78 * u + i * 52 * u, y + 64 * u], fill=(244, 208, 120), out=INK, w=2 * u)
    p.poly([x + w - 10 * u, y + 10 * u, x + w + 40 * u, y - 26 * u, x + w + 20 * u, y + 10 * u], fill=hull, out=INK, w=3 * u)
    for mx, sh in ((x + 130 * u, 230 * u), (x + 260 * u, 260 * u)):
        p.line([mx, y + 10 * u, mx, y - sh], (90, 58, 40), 7 * u)
        fl = math.sin(t * 3 + mx) * 6 * u
        p.poly([mx + 4 * u, y - sh + 10 * u, mx + 90 * u + fl, y - sh * .55, mx + 4 * u, y - 30 * u], fill=(250, 242, 224), out=INK, w=3 * u)
        p.poly([mx - 4 * u, y - sh + 30 * u, mx - 70 * u - fl, y - sh * .55, mx - 4 * u, y - 50 * u], fill=(240, 228, 200), out=INK, w=3 * u)
        p.poly([mx, y - sh, mx + 36 * u + fl, y - sh + 14 * u, mx, y - sh + 28 * u], fill=(196, 48, 48), out=INK, w=2 * u)
    return y


# --------------- PROPS (p, t, c) ---------------
def batu(p, t, c):
    cx, y, k = 700, 1150, 1.3
    X = lambda v: cx + (v - 430) * k
    Y = lambda v: y + (v - 1150) * k
    gray = (130, 128, 136)
    P = lambda pts: [q for i in range(0, len(pts), 2) for q in (X(pts[i]), Y(pts[i + 1]))]
    p.ell([X(190), Y(1150 - 12), X(670), Y(1150 + 26)], fill=(0, 0, 0, 40))
    p.poly(P([240, 1150, 260, 1080, 340, 1030, 410, 960, 490, 950, 540, 1000, 520, 1060, 590, 1090, 630, 1150]), fill=gray, out=INK, w=4)
    p.ell([X(450), Y(888), X(540), Y(970)], fill=(144, 142, 150), out=INK, w=4)
    p.poly(P([410, 960, 470, 1000, 550, 1000, 520, 1050]), fill=(112, 110, 120))
    p.line([X(280), Y(1090), X(370), Y(1050)], (160, 158, 166), 5); p.line([X(470), Y(960), X(528), Y(990)], (160, 158, 166), 5)


def pin(p, t, c):
    x, y = 300, 800 + math.sin(t * 4) * 12
    p.ell([x - 40, 868, x + 40, 886], fill=(110, 90, 70))
    p.poly([x - 36, y - 40, x + 36, y - 40, x, y + 66], fill=(210, 50, 50), out=INK, w=4)
    p.ell([x - 48, y - 100, x + 48, y - 4], fill=(210, 50, 50), out=INK, w=4)
    p.ell([x - 18, y - 70, x + 18, y - 34], fill=(255, 244, 230))
    text(p, 420, y - 20, "PADANG", 36, (60, 30, 30), "lm")


def rumah_gubuk(p, t, c): pass
def perahu(p, t, c):
    u = 1.7; x, y = 60, 955 + math.sin(t * 1.4) * 4
    p.poly([x, y, x + 240 * u, y, x + 200 * u, y + 50 * u, x + 40 * u, y + 50 * u], fill=(150, 100, 60), out=INK, w=3)
    p.line([x + 120 * u, y, x + 120 * u, y - 130 * u], (90, 58, 40), 6)
    p.poly([x + 124 * u, y - 126 * u, x + 200 * u, y - 30 * u, x + 124 * u, y - 20 * u], fill=(250, 240, 220), out=INK, w=3)
    p.ell([x - 10, y + 50 * u - 8, x + 240 * u + 10, y + 50 * u + 14], fill=(255, 255, 255, 70))


def jala(p, t, c):
    for i in range(8): p.line([700 + i * 36, 900, 690 + i * 38, 1070], (90, 90, 80), 2)
    for j in range(6): p.line([690, 910 + j * 28, 1000, 910 + j * 28], (90, 90, 80), 2)
    p.line([690, 890, 1000, 890], (110, 74, 44), 7); p.line([690, 890, 690, 1085], (110, 74, 44), 7); p.line([1000, 890, 1000, 1085], (110, 74, 44), 7)


def ikan_jemur(p, t, c):
    p.line([60, 930, 470, 930], (110, 74, 44), 9); p.line([70, 930, 70, 1110], (110, 74, 44), 9); p.line([460, 930, 460, 1110], (110, 74, 44), 9)
    for i in range(6):
        x = 120 + i * 62
        p.poly([x, 940, x + 20, 985, x, 1040, x - 20, 985], fill=(170, 180, 190), out=INK, w=2.5)


def ember(p, t, c):
    p.poly([620, 1160, 700, 1160, 690, 1225, 630, 1225], fill=(120, 140, 160), out=INK, w=3); p.arc([620, 1120, 700, 1200], 180, 360, INK, 3)


def kapal_horizon(p, t, c):
    x = 700 + math.sin(t * 0.4) * 4; y = 706
    p.poly([x, y, x + 70, y, x + 58, y + 14, x + 12, y + 14], fill=(150, 60, 48), out=INK, w=2)
    p.line([x + 36, y, x + 36, y - 34], (90, 58, 40), 3); p.poly([x + 38, y - 32, x + 60, y - 4, x + 38, y - 2], fill=(250, 240, 220), out=INK, w=2)


def kapal_besar(p, t, c): ship(p, 280, 880, 800, t)
def kapal_megah(p, t, c): ship(p, 160, 900, 760, t, gold=True)
def kapal_menjauh(p, t, c):
    x = 560 + t * 70; ship(p, x, 860, 260 - t * 6, t)
def peti(p, t, c):
    for i, (x, y, w) in enumerate(((60, 1130, 150), (230, 1130, 130), (140, 1040, 130))):
        p.rect([x, y, x + w, y + 90], fill=(170, 116, 70), out=INK, w=3); p.line([x, y + 45, x + w, y + 45], (110, 70, 44), 4); p.line([x + w / 2, y, x + w / 2, y + 90], (110, 70, 44), 4)
def koin(p, t, c):
    for i in range(9):
        x = 640 + (i % 5) * 34 + (i // 5) * 17; y = 1170 - (i // 5) * 18
        p.ell([x, y, x + 34, y + 16], fill=(244, 196, 60), out=INK, w=2)
def jangkar(p, t, c):
    y = 1060 - min(1.0, t / 2.0) * 120; x = 200
    p.line([x, y - 60, x, y + 70], INK, 9); p.line([x - 40, y - 30, x + 40, y - 30], INK, 8)
    p.arc([x - 60, y + 10, x + 60, y + 100], 0, 180, INK, 9); p.ell([x - 12, y - 84, x + 12, y - 60], out=INK, w=6)
    p.line([x, y - 80, x, 760], (120, 90, 60), 4)
def awan_badai(p, t, c):
    for i in range(7):
        x = i * 190 - 60 + math.sin(t * 0.5 + i) * 18
        p.ell([x, 250 + (i % 2) * 40, x + 300, 520 + (i % 3) * 30], fill=(54, 58, 78))
def petir_prop(p, t, c):
    k = int(t * 2.2)
    if (t * 2.2 - k) < 0.35:
        x = 300 + (k * 197) % 520
        p.poly([x, 330, x - 40, 560, x + 6, 560, x - 56, 840, x + 70, 520, x + 14, 520, x + 50, 330], fill=(255, 250, 200), out=(255, 255, 255), w=4)
def kapal_hancur(p, t, c):
    k = min(1.0, t / 1.8)
    ship(p, 250 - 30 * k, 1040 + 20 * k, 520, t, rock=k)
    p.poly([800 + 40 * k, 1070 + 80 * k, 960 + 50 * k, 1080 + 100 * k, 920 + 50 * k, 1140 + 110 * k, 820 + 40 * k, 1140 + 100 * k], fill=(150, 60, 48), out=INK, w=3)
def serpihan(p, t, c):
    for i, (x, y) in enumerate(((220, 1120), (520, 1160), (820, 1110), (380, 1190))):
        yy = y + math.sin(t * 2 + i) * 6; a = math.sin(t + i) * 12
        p.poly([x - 50, yy - 8 + a, x + 50, yy - 8 - a, x + 50, yy + 8 - a, x - 50, yy + 8 + a], fill=(140, 92, 60), out=INK, w=2.5)
def kapal_batu(p, t, c):
    o = 60
    p.poly([700 + o, 1170, 720 + o, 1110, 800 + o, 1080, 880 + o, 1100, 960 + o, 1060, 1010 + o, 1120, 1000 + o, 1170], fill=(120, 118, 126), out=INK, w=4)
    p.poly([760 + o, 1080, 780 + o, 980, 800 + o, 1080], fill=(110, 108, 116), out=INK, w=3)
def plakat(p, t, c):
    p.rect([300, 1000, 340, 1190], fill=(110, 72, 46), out=INK, w=3); p.rect([130, 850, 510, 1010], fill=(236, 214, 160), out=INK, w=4, r=10)
    text(p, 320, 902, "LEGENDA", 40, (84, 50, 34)); text(p, 320, 962, "CERITA RAKYAT", 28, (84, 50, 34))
def pin_tanya(p, t, c):
    for i, (x, y) in enumerate(((330, 820), (700, 900), (840, 640), (260, 1130))):
        s = 1 + 0.12 * math.sin(t * 4 + i)
        p.ell([x - 34 * s, y - 34 * s, x + 34 * s, y + 34 * s], fill=(210, 50, 50), out=INK, w=3)
        text(p, x, y + 2, "?", 38, (255, 255, 255))
def noop(p, t, c): pass

PROPS = {"batu_malin_bersujud": batu, "pin_lokasi_padang": pin, "rumah_gubuk": rumah_gubuk, "perahu_kecil": perahu, "jala": jala,
         "ikan_jemur": ikan_jemur, "ember": ember, "kapal_jauh_di_horizon": kapal_horizon, "kapal_dagang_besar": kapal_besar,
         "layar_putih": noop, "kapal_menjauh": kapal_menjauh, "tongkat": noop, "laut_kosong": noop, "peti_dagangan": peti, "koin_emas": koin,
         "kapal_megah": kapal_megah, "awak_kapal": noop, "pakaian_sutra": noop, "jangkar": jangkar, "awan_badai": awan_badai, "petir": petir_prop,
         "kapal_hancur": kapal_hancur, "serpihan_kayu": serpihan, "serpihan_kapal_membatu": kapal_batu,
         "plakat_legenda_cerita_rakyat": plakat, "peta_nusantara": noop, "pin_pertanyaan": pin_tanya}


# --------------- FX (p, t, c, ov) --- ov = lapisan RGBA layar penuh untuk efek layar ---------------
def fx_ombak(p, t, c, ov):
    for i in range(9):
        x = (i * 150 + t * 40) % 1300 - 100; y = 1180 + (i % 3) * 12 - 20
        p.arc([x, y - 16, x + 120, y + 16], 190, 350, (255, 255, 255), 5)
def fx_camar(p, t, c, ov):
    for i in range(3):
        x = (t * 90 + i * 330) % 1300 - 100; y = 520 + i * 60 + math.sin(t * 3 + i) * 12; f = math.sin(t * 9 + i) * 10
        p.line([x - 26, y - f, x, y, x + 26, y - f], (250, 250, 250), 5)
def fx_air_mata(p, t, c, ov):
    for hd in c.get("heads", []):
        for i in range(2):
            ph = (t * 1.3 + i * .5) % 1.0
            x = hd[0] + (-14 if i else 14); y = hd[1] + 14 + ph * 70
            p.ell([x - 5, y - 8, x + 5, y + 8], fill=(150, 210, 250), out=INK, w=1.5)
def fx_kalender(p, t, c, ov):
    n = 1 + int(min(t / max(c["dur"], 1) * 5.0, 4.99))
    p.rect([70, 560, 330, 760], fill=(250, 246, 236), out=INK, w=4, r=14); p.rect([70, 560, 330, 620], fill=(190, 50, 50), out=INK, w=4, r=14)
    text(p, 200, 592, "TAHUN", 34, (255, 255, 255)); text(p, 200, 694, str(n), 96, (60, 40, 40))
def fx_koin(p, t, c, ov):
    for i in range(6):
        ph = (t * 1.6 + i * .17) % 1.0; x = 650 + i * 52; y = 1100 - ph * 60; r = 10 * (1 - ph)
        p.line([x - r * 1.5, y, x + r * 1.5, y], (255, 244, 170), 3); p.line([x, y - r * 1.5, x, y + r * 1.5], (255, 244, 170), 3)
def fx_debu(p, t, c, ov):
    for fy_ in c.get("feet", []):
        for i in range(5):
            ph = (t * 2 + i * .2) % 1.0; x = fy_[0] - 40 - ph * 90 + i * 8; y = fy_[1] - ph * 30
            p.ell([x - 10 - ph * 10, y - 10 - ph * 8, x + 10 + ph * 10, y + 10 + ph * 8], fill=(214, 190, 150))
def fx_awan_gelap(p, t, c, ov):
    k = min(1.0, t / max(c["dur"], 1) * 1.2); ImageDraw.Draw(ov).rectangle([0, 0, ov.size[0], ov.size[1]], fill=(20, 24, 50, int(130 * k)))
def fx_hujan(p, t, c, ov):
    rnd = random.Random(11)
    for i in range(110):
        x = (rnd.random() * 1300 + t * 260) % 1300 - 100; y = (rnd.random() * 2100 + t * 1500 + i * 13) % 2000 - 40
        p.line([x, y, x - 22, y + 70], (190, 210, 235), 3)
def fx_petir(p, t, c, ov):
    k = int(t * 2.2)
    if (t * 2.2 - k) < 0.12: ImageDraw.Draw(ov).rectangle([0, 0, ov.size[0], ov.size[1]], fill=(255, 255, 255, 170))
def fx_ombak_besar(p, t, c, ov):
    for i in range(5):
        x0 = -200 + i * 300 + math.sin(t * 2 + i) * 40; hgt = 90 + 25 * math.sin(t * 2.6 + i)
        p.poly([x0, 1200, x0 + 90, 1200 - hgt, x0 + 200, 1200 - hgt * .4, x0 + 330, 1200, x0 + 330, 1300, x0, 1300], fill=(48, 86, 126), out=(220, 236, 246), w=4)
def fx_kabut(p, t, c, ov):
    d = ImageDraw.Draw(ov)
    for i in range(4):
        y = 780 + i * 90 + math.sin(t + i) * 12; d.rectangle([0, y * 2 if False else int(y * 2), ov.size[0], int((y + 70) * 2)], fill=(255, 255, 255, 40))
def fx_sunset(p, t, c, ov):
    k = min(1.0, t / max(c["dur"], 1)); x = 780; y = 640 + k * 150
    p.ell([x - 110, y - 110, x + 110, y + 110], fill=(255, 200, 130)); p.ell([x - 70, y - 70, x + 70, y + 70], fill=(255, 226, 150))
def fx_ajak(p, t, c, ov):
    k = min(1.0, t / 0.5); s = 0.85 + 0.15 * k
    p.rect([90, 940, 890, 1100], fill=(255, 252, 244), out=(31, 122, 99), w=5, r=40)
    text(p, 490, 988, "Follow NUSAKARA &", 46, (36, 44, 42)); text(p, 490, 1052, "tulis cerita daerah berikutnya di komentar", 31, (31, 122, 99))
def fx_noop(p, t, c, ov): pass

FX = {"ombak_pecah": fx_ombak, "ombak": fx_ombak, "burung_camar": fx_camar, "air_mata": fx_air_mata, "kalender_berganti": fx_kalender,
      "bintang": fx_noop, "koin_berkilau": fx_koin, "debu": fx_debu, "awan_gelap": fx_awan_gelap, "hujan": fx_hujan, "petir": fx_petir,
      "ombak_besar": fx_ombak_besar, "retakan_kapal": fx_noop, "kabut_pagi": fx_kabut, "matahari_terbenam": fx_sunset,
      "kartu_ajakan_follow_komentar": fx_ajak}


# --------------- LATAR ---------------
LATAR = {}
def latar(name):
    def deco(fn): LATAR[name] = fn; return fn
    return deco

def _base(d, p, pal, sea_=True, ground=True, house=True, palms=True, sunon=True, cl=3, horizon_hills=True):
    B.sky(d, pal)
    if pal["dark"] > 0.3: B.stars(d)
    if sunon: B.sun(p, pal)
    B.clouds(p, pal, cl)
    if horizon_hills: B.hills(p, pal)
    if sea_: B.sea(d, pal)
    if ground: B.beach(d, pal)
    if house: B.gonjong(p, -150, 1100, 500)
    if palms: B.palm(p, 980, 1280, 380, -30); B.palm(p, 470, 1300, 300, 24)

@latar("pantai_air_manis_senja")
def _a(d, p, pal, w): _base(d, p, pal, sunon=False)
for _n in ("pantai_air_manis_pagi", "pantai_air_manis_siang"): LATAR[_n] = lambda d, p, pal, w: _base(d, p, pal)
LATAR["pantai_air_manis_senja"] = lambda d, p, pal, w: _base(d, p, pal)
LATAR["tepi_pantai_siang"] = lambda d, p, pal, w: _base(d, p, pal, house=False, palms=False)
LATAR["pantai_senja_ibu"] = lambda d, p, pal, w: _base(d, p, pal, house=True)
def _laut(d, p, pal, w):
    _base(d, p, pal, ground=False, house=False, palms=False)
    if B.near_ok(): d.rectangle([0, 1099, W, H], fill=pal["sea2"])
    B.palm(p, 920, 760, 120, -10)
LATAR["laut_menuju_pantai"] = _laut
LATAR["kampung_nelayan_pagi"] = lambda d, p, pal, w: (_base(d, p, pal, house=False), B.hut(p, 380, 1045, 260), B.hut(p, -60, 1095, 420), B.hut(p, 700, 1085, 380))
def _halaman(d, p, pal, w):
    B.sky(d, pal); B.sun(p, pal); B.clouds(p, pal, 2); B.hills(p, pal)
    if B.near_ok(): d.polygon([(0, 722), (W, 722), (W, H), (0, H)], fill=mix(pal["gr"], (110, 150, 80), .45))
    B.palm(p, 90, 1000, 420, 24); B.palm(p, 1000, 1010, 340, -28)
    B.hut(p, 470, 985, 360)
    if B.near_ok():
        for x in range(0, 1100, 70): p.line([x, 1020, x, 1120], (110, 72, 46), 9)
        p.line([0, 1050, W, 1050], (110, 72, 46), 9); p.line([0, 1095, W, 1095], (110, 72, 46), 9)
LATAR["rumah_gubuk_halaman"] = _halaman
def _town(p):
    if not B.far_ok(): return
    for x in range(-30, 1100, 140):
        top = 540 + (x * 37) % 120; c = mix((150, 120, 100), (190, 160, 130), (x % 3) / 3.0)
        p.rect([x, top, x + 130, 745], fill=c, out=INK, w=3)
        p.poly([x - 8, top, x + 65, top - 40, x + 138, top], fill=mix(c, (150, 70, 52), .6), out=INK, w=3)
        for r in range(int((745 - top - 20) // 56)):
            for q in range(3): p.rect([x + 16 + q * 38, top + 20 + r * 56, x + 40 + q * 38, top + 50 + r * 56], fill=(250, 226, 150), out=INK, w=2)
def _pier(d, p, pal, w):
    B.sky(d, pal); (B.stars(d) if pal["dark"] > .3 else None); B.sun(p, pal); B.clouds(p, pal, 2); B.hills(p, pal); B.sea(d, pal, 720, 1095); B.pier(p, pal)
for _n in ("dermaga_siang", "dermaga_senja", "dermaga_kampung", "dermaga_kampung_ramai"): LATAR[_n] = _pier
def _dari_geladak(d, p, pal, w):
    B.sky(d, pal); (B.stars(d) if pal["dark"] > .3 else None); B.sun(p, pal); B.clouds(p, pal, 2); B.hills(p, pal); B.sea(d, pal, 720, 930)
    B.planks(p, 930, 1085, col=(124, 82, 54))
    if B.near_ok():
        p.rect([-20, 850, 1100, 872], fill=(96, 62, 42))
        for x in range(30, 1100, 140): p.rect([x, 872, x + 16, 940], fill=(96, 62, 42))
    B.pier(p, pal, 1100)
LATAR["dermaga_dari_geladak"] = _dari_geladak
LATAR["pelabuhan_kota_seberang"] = lambda d, p, pal, w: (_base(d, p, pal, ground=False, house=False, palms=False), _town(p), B.sea(d, pal, 740, 1095), B.pier(p, pal))
def _deck(d, p, pal, w):
    B.sky(d, pal); (B.stars(d) if pal["dark"] > .3 else None); B.sun(p, pal); B.clouds(p, pal, 2); B.sea(d, pal, 700, 1070); B.deck(p, pal)
LATAR["geladak_kapal_megah"] = _deck
def _storm(d, p, pal, w):
    if not B.near_ok(): return
    st = (30, 34, 56); sb = (70, 76, 108)
    for y in range(0, 760): d.line([(0, y), (W, y)], fill=mix(st, sb, (y / 760.0) ** 1.4))
    for y in range(720, 1400): d.line([(0, y), (W, y)], fill=mix((24, 44, 72), (14, 28, 50), (y - 720) / 680.0))
    rnd = random.Random(2)
    for i in range(70):
        y = 740 + i * 9; x = rnd.randint(-40, 1040); d.line([(x, y), (x + 70, y - 4)], fill=(120, 150, 180), width=3)
    d.rectangle([0, 1380, W, H], fill=(14, 28, 50))
LATAR["laut_badai"] = _storm
LATAR["peta_sumbar_pin"] = lambda d, p, pal, w: B.map_bg(d, p, "sumbar")
LATAR["peta_nusantara_penutup"] = lambda d, p, pal, w: B.map_bg(d, p, "nusantara")


def _render_bg(name, waktu, ss, mode, rgba):
    B.MODE = mode
    try:
        pal = B.PAL.get(waktu, B.PAL["siang"])
        im = Image.new("RGBA" if rgba else "RGB", (W * ss, H * ss), (0, 0, 0, 0) if rgba else (0, 0, 0))
        d = _ScaledDraw(ImageDraw.Draw(im), ss); p = Pen(im, ss)
        fn = LATAR.get(name)
        if fn is None: print("WARN latar tak dikenal:", name); fn = LATAR["pantai_air_manis_siang"]
        fn(d, p, pal, waktu)
    finally:
        B.MODE = "all"
    return im, pal


def build_bg2(name, waktu, ss=2):
    """Dua lapisan untuk paralaks 2.5D: far (RGB) dan near (RGBA transparan di atas horizon)."""
    far, pal = _render_bg(name, waktu, ss, "far", False)
    near, _ = _render_bg(name, waktu, ss, "near", True)
    # kabut udara di kaki langit (lapisan jauh)
    hz = 720 * ss; band = 200 * ss
    g = Image.linear_gradient("L").resize((far.width, band)).point(lambda v: int(v * 0.5))
    haze = Image.new("RGBA", (far.width, band), tuple(mix(pal["sb"], (255, 250, 240), .5)) + (0,)); haze.putalpha(g)
    far = far.convert("RGBA"); far.alpha_composite(haze, (0, hz - band)); far = far.convert("RGB")
    if pal["dark"]:
        a = int(255 * pal["dark"])
        far = Image.alpha_composite(far.convert("RGBA"), Image.new("RGBA", far.size, (10, 20, 60, a))).convert("RGB")
        ov = Image.new("RGBA", near.size, (10, 20, 60, 255)); ov.putalpha(near.getchannel("A").point(lambda v: int(v * pal["dark"])))
        near = Image.alpha_composite(near, ov)
    return far, near


def build_bg(name, waktu, ss=2):
    pal = B.PAL.get(waktu, B.PAL["siang"])
    im = Image.new("RGB", (W * ss, H * ss), (0, 0, 0))
    big = ImageDraw.Draw(im); d = _ScaledDraw(big, ss)
    p = Pen(im, ss)
    fn = LATAR.get(name)
    if fn is None:
        print("WARN latar tak dikenal:", name); fn = LATAR["pantai_air_manis_siang"]
    fn(d, p, pal, waktu)
    if pal["dark"]: 
        ov = Image.new("RGBA", im.size, (10, 20, 60, int(255 * pal["dark"]))); im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    return im


class _ScaledDraw:
    """ImageDraw yang mengalikan koordinat dunia dengan ss (untuk gradien/garis langsung)."""
    def __init__(s, d, ss): s.d = d; s.ss = ss
    def _s(s, v):
        if isinstance(v[0], (tuple, list)): return [(a * s.ss, b * s.ss) for a, b in v]
        return [x * s.ss for x in v]
    def line(s, xy, fill=None, width=1): s.d.line(s._s(xy), fill=fill, width=max(1, int(width * s.ss)))
    def polygon(s, xy, fill=None, outline=None): s.d.polygon(s._s(xy), fill=fill, outline=outline)
    def ellipse(s, xy, fill=None, outline=None, width=1): s.d.ellipse(s._s(xy), fill=fill, outline=outline, width=int(width * s.ss))
    def rectangle(s, xy, fill=None, outline=None, width=1): s.d.rectangle(s._s(xy), fill=fill, outline=outline, width=int(width * s.ss))
