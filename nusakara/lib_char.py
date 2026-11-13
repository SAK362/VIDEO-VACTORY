"""Karakter stickman: tokoh cerita (pustaka) dan Pak Nusa (maskot). Semua dalam koordinat dunia 1080x1920."""
import math
from draw import INK, SKIN, mix

SAD = {"sedih", "menangis", "hancur", "rindu", "haru", "lelah", "berharap", "penuh_harap"}
HAPPY = {"senang", "bahagia", "bangga", "tenang", "anggun", "kagum", "bertekad", "fokus"}
ANGRY = {"marah", "dingin", "jijik", "angkuh", "malu", "patuh"}
SHOCK = {"kaget", "heboh", "panik"}

# (sudut lengan atas kiri, bawah kiri, atas kanan, bawah kanan) derajat: 0=ke bawah, 90=mendatar keluar, 180=ke atas
POSES = {
    "berdiri": (14, 8, 14, 8), "berjalan": (20, 10, -20, -10), "berlari": (60, 100, -50, -90),
    "menjemur_ikan": (110, 140, 40, 20), "membantu": (45, 80, 30, 14), "menatap_laut": (14, 8, 125, 160),
    "duduk": (30, 60, 30, 60), "menunjuk": (14, 8, 92, 94), "menunjuk_ke_laut": (14, 8, 92, 94),
    "memohon": (100, 150, 100, 150), "mengusap_air_mata": (14, 8, 150, 205), "melambai": (14, 8, 150, 170),
    "naik_kapal": (20, 10, -20, -10), "berdiri_angkuh": (74, -38, 74, -38), "berkacak_pinggang": (74, -38, 74, -38),
    "memeluk_kaki": (60, 20, 60, 20), "menepis_tangan": (14, 8, 80, 50), "terhuyung": (70, 50, 80, 60),
    "menengadah_berdoa": (150, 175, 150, 175), "berteriak_minta_ampun": (140, 170, 150, 180),
    "menarik_jangkar": (50, 20, 50, 20), "menunduk": (14, 8, 14, 8), "menoleh": (14, 8, 14, 8),
    "menengadah": (20, 10, 20, 10), "berdiri_menatap_laut": (14, 8, 14, 8), "berdagang": (80, 120, 60, 20),
    "memeluk": (60, 20, 60, 20), "berbisik": (14, 8, 135, 170), "membuang_muka": (30, 20, 30, 20),
}

OUTFIT = {
    "mande_rubayah": dict(h=0.93, top=(236, 200, 120), bot=(168, 62, 56), head="kerudung", hc=(120, 40, 60), stick=True, hunch=0.05, skirt=True, gold=True),
    "malin_kecil": dict(h=0.55, top=(196, 150, 96), bot=(110, 80, 56), head="rambut", hc=INK, skirt=False),
    "malin_remaja": dict(h=0.86, top=(120, 150, 170), bot=(120, 84, 56), head="rambut", hc=INK, skirt=False),
    "malin_dewasa": dict(h=1.0, top=(84, 130, 90), bot=(98, 70, 50), head="destar", hc=(150, 60, 50), skirt=False, vest=True),
    "malin_kaya": dict(h=1.02, top=(60, 120, 160), bot=(50, 70, 110), head="destar", hc=(180, 40, 40), skirt=False, gold=True, sash=True),
    "istri_malin": dict(h=0.95, top=(214, 96, 122), bot=(214, 96, 122), head="sanggul", hc=INK, skirt=True, gold=True),
    "warga": dict(h=0.9, top=(120, 160, 120), bot=(130, 96, 64), head="caping", hc=(222, 184, 96), skirt=False),
    "awak_kapal": dict(h=0.92, top=(244, 244, 250), bot=(60, 84, 130), head="topi", hc=(60, 84, 130), skirt=False, stripe=True),
}
VAR = [((120, 160, 120), (222, 184, 96)), ((190, 120, 80), (150, 100, 60)), ((100, 130, 190), (222, 184, 96)), ((170, 90, 120), (120, 40, 60))]


def vec(a, side, L): r = math.radians(a); return (side * math.sin(r) * L, math.cos(r) * L)


def expr(name):
    return "sad" if name in SAD else "happy" if name in HAPPY else "angry" if name in ANGRY else "shock" if name in SHOCK else "neutral"


def face(p, hc, r, kind, f, mouth=0.0, blink=False, look=0.0):
    ex = r * .42
    for sx in (-1, 1):
        x = hc[0] + sx * ex + look
        if blink: p.line([x - 5, hc[1] + 2, x + 5, hc[1] + 2], INK, 2.5)
        else: p.ell([x - 4, hc[1] - 3, x + 4, hc[1] + 8], fill=INK)
    by = hc[1] - 10
    if kind == "sad":
        for sx in (-1, 1): p.line([hc[0] + sx * ex - 8, by - (3 if sx < 0 else -3) * -1, hc[0] + sx * ex + 8, by - (-3 if sx < 0 else 3) * -1], INK, 2.5)
        p.arc([hc[0] - r * .4, hc[1] + r * .38, hc[0] + r * .4, hc[1] + r * .85], 200, 340, INK, 3)
    elif kind == "happy":
        p.arc([hc[0] - r * .45, hc[1] + r * .08, hc[0] + r * .45, hc[1] + r * .66], 20, 160, INK, 3)
    elif kind == "angry":
        for sx in (-1, 1): p.line([hc[0] + sx * ex - 9 * sx * -1, by + (4 if sx < 0 else -4) * 0 - 4, hc[0] + sx * ex + 9 * sx * -1, by + 5], INK, 3)
        p.line([hc[0] - r * .3, hc[1] + r * .55, hc[0] + r * .3, hc[1] + r * .55], INK, 3)
    elif kind == "shock":
        p.ell([hc[0] - 6, hc[1] + r * .42, hc[0] + 6, hc[1] + r * .42 + 14], fill=(120, 30, 40), out=INK, w=2)
    else:
        p.line([hc[0] - r * .28, hc[1] + r * .5, hc[0] + r * .28, hc[1] + r * .5], INK, 2.5)


def head_gear(p, o, hc, r, f):
    k = o["head"]; c = o["hc"]
    if k == "rambut":
        p.pie([hc[0] - r * 1.05, hc[1] - r * 1.1, hc[0] + r * 1.05, hc[1] + r * .9], 180, 360, c)
    elif k == "destar":
        p.rect([hc[0] - r * 1.05, hc[1] - r * 1.05, hc[0] + r * 1.05, hc[1] - r * .4], fill=c, out=INK, w=2.5, r=4)
        p.poly([hc[0] - r * .4, hc[1] - r * 1.05, hc[0], hc[1] - r * 1.7, hc[0] + r * .4, hc[1] - r * 1.05], fill=c, out=INK, w=2.5)
    elif k == "kerudung":
        p.pie([hc[0] - r * 1.25, hc[1] - r * 1.3, hc[0] + r * 1.25, hc[1] + r * 1.3], 150, 390, c)
        p.poly([hc[0] - f * r * 1.2, hc[1] - r * .1, hc[0] - f * r * 1.45, hc[1] + r * 1.9, hc[0] - f * r * .1, hc[1] + r * 1.1], fill=c, out=INK, w=2)
    elif k == "sanggul":
        p.pie([hc[0] - r * 1.05, hc[1] - r * 1.1, hc[0] + r * 1.05, hc[1] + r * .9], 180, 360, c)
        p.ell([hc[0] - r * .4, hc[1] - r * 1.65, hc[0] + r * .4, hc[1] - r * .85], fill=c)
        p.line([hc[0] - r * .35, hc[1] - r * 1.15, hc[0] + r * .35, hc[1] - r * 1.15], (244, 208, 120), 3)
    elif k == "caping":
        p.poly([hc[0] - r * 1.8, hc[1] - r * .4, hc[0], hc[1] - r * 2.0, hc[0] + r * 1.8, hc[1] - r * .4], fill=c, out=INK, w=2.5)
    elif k == "topi":
        p.rect([hc[0] - r * 1.0, hc[1] - r * 1.1, hc[0] + r * 1.0, hc[1] - r * .45], fill=c, out=INK, w=2.5, r=5)
        p.rect([hc[0] - r * 1.0, hc[1] - r * .55, hc[0] + r * 1.0, hc[1] - r * .4], fill=(250, 250, 250))


def person(p, cx, fy, key, pose="berdiri", ekspresi="tenang", t=0.0, f=1, base_h=330, mouth=0.0, seed=0, bob=True):
    """f=+1 menghadap kanan, -1 kiri. t detik adegan: napas, kedip, ayun langkah."""
    o = dict(OUTFIT.get(key, OUTFIT["warga"]))
    if key == "warga":
        o["top"], o["hc"] = VAR[seed % len(VAR)]
    h = base_h * o["h"]
    a = POSES.get(pose, POSES["berdiri"])
    walk = pose in ("berjalan", "berlari", "naik_kapal")
    sw = math.sin(t * (9 if pose == "berlari" else 5.5)) if walk else 0.0
    br = math.sin(t * 2.2 + seed) * 2.0 if bob else 0.0
    p.ell([cx - h * .3, fy - 8, cx + h * .3, fy + 8], fill=(0, 0, 0, 0) if False else (90, 70, 56))
    sit = pose == "duduk"
    bend = {"memeluk_kaki": 0.22, "menunduk": 0.06, "terhuyung": -0.08, "berlari": 0.08, "memohon": 0.05, "menengadah_berdoa": -0.05, "berteriak_minta_ampun": -0.03}.get(pose, 0) + o.get("hunch", 0)
    hipy = fy - h * (0.30 if not sit else 0.14); hip = (cx, hipy)
    # kaki
    col = INK
    if sit:
        p.line([cx, hipy, cx + f * h * .30, hipy + 4, cx + f * h * .34, fy], col, 7)
    else:
        for sgn in (-1, 1):
            ph = sw * sgn
            p.line([cx, hipy, cx + sgn * h * .07 + ph * h * .16, fy - 2], col, 7)
            p.rect([cx + sgn * h * .07 + ph * h * .16 - 12, fy - 5, cx + sgn * h * .07 + ph * h * .16 + 12 * f, fy + 3], fill=(110, 72, 44), out=INK, w=1.6, r=3)
    # rok / celana
    if o.get("skirt"):
        wb = h * .17; wt = h * .12
        p.poly([cx - wt, hipy - h * .02, cx + wt, hipy - h * .02, cx + wb, fy - h * .06 if not sit else hipy + h * .16, cx - wb, fy - h * .06 if not sit else hipy + h * .16], fill=o["bot"], out=INK, w=2.5)
        if o.get("gold"): p.line([cx - wb * .95, fy - h * .12, cx + wb * .95, fy - h * .12], (244, 208, 120), 2.5)
    else:
        p.rect([cx - h * .09, hipy - h * .05, cx + h * .09, hipy + h * .09], fill=o["bot"], out=INK, w=2)
    # badan
    shy = hipy - h * .32 + br
    sx0 = cx + f * bend * h
    p.line([cx, hipy, sx0, shy], INK, 7)
    p.ell([sx0 - h * .12, shy - 2, sx0 + h * .12, hipy + 4], fill=o["top"], out=INK, w=2.5)
    if o.get("vest"): p.line([sx0, shy + 6, sx0, hipy], (60, 100, 70), 3)
    if o.get("sash"): p.rect([sx0 - h * .12, hipy - h * .04, sx0 + h * .12, hipy + h * .02], fill=(220, 168, 56), out=INK, w=1.8, r=3)
    if o.get("stripe"):
        for i in range(4): p.line([sx0 - h * .11, shy + 8 + i * 10, sx0 + h * .11, shy + 8 + i * 10], o["bot"], 2.5)
    # lengan
    wv = math.sin(t * 9) * 14 if pose == "melambai" else 0
    for side, (a1, a2) in ((-1, (a[0], a[1])), (1, (a[2], a[3] + wv))):
        s_ = side * f if False else side
        shp = (sx0 + side * h * .10, shy + 6)
        e = vec(a1, side, h * .20); el = (shp[0] + e[0], shp[1] + e[1])
        w_ = vec(a2, side, h * .19); hd = (el[0] + w_[0], el[1] + w_[1])
        p.line([*shp, *el], o["top"], 7); p.line([*el, *hd], SKIN, 5.5)
        p.ell([hd[0] - 4.5, hd[1] - 4.5, hd[0] + 4.5, hd[1] + 4.5], fill=SKIN, out=INK, w=1.6)
        if o.get("stick") and side == 1: p.line([hd[0], hd[1] - 20, hd[0] + 3, fy], (110, 72, 40), 4.5)
    # kepala
    r = h * .13; hc = (sx0 + f * h * .015, shy - r * 1.05 - (4 if pose == "menengadah_berdoa" else 0))
    p.ell([hc[0] - r, hc[1] - r, hc[0] + r, hc[1] + r], fill=SKIN, out=INK, w=2.8)
    head_gear(p, o, hc, r, f)
    blink = (t % 3.2) < 0.12
    face(p, hc, r, expr(ekspresi), f, blink=blink, look=f * 2)
    return dict(head=hc, hand=hd, shoulder=(sx0, shy), foot=fy, h=h)


# ---------------- Pak Nusa (maskot) ----------------
def batik_trapezoid(p, cx, fy, u):
    p.poly([cx - 70 * u, fy - 168 * u, cx + 70 * u, fy - 168 * u, cx + 58 * u, fy - 40 * u, cx - 58 * u, fy - 40 * u], fill=(132, 78, 44), out=INK, w=3 * u)
    st = 22 * u
    for r_ in range(5):
        yy = fy - 150 * u + r_ * st * .75
        wid = 70 * u - (yy - (fy - 168 * u)) * (12 / 128.0)
        n = int((2 * wid) / st); x0 = cx - n * st / 2 + (st / 2 if r_ % 2 else 0)
        for k in range(n):
            xx = x0 + k * st + st / 2
            if abs(xx - cx) < wid - 6 * u:
                p.poly([xx, yy - 8 * u, xx + 8 * u, yy, xx, yy + 8 * u, xx - 8 * u, yy], out=(244, 208, 120), w=1.5 * u)
    p.line([cx - 58 * u, fy - 40 * u, cx + 58 * u, fy - 40 * u], (244, 208, 120), 3 * u)


def pak_nusa(p, cx, fy, h, mouth=0.5, t=0.0, wave=False, shock=False, point=True):
    u = h / 340.0
    br = math.sin(t * 2.0) * 2.2 * u   # napas
    p.ell([cx - 90 * u, fy - 9 * u, cx + 90 * u, fy + 9 * u], fill=(70, 50, 40))
    for sx in (-1, 1):
        p.line([cx + sx * 26 * u, fy - 100 * u, cx + sx * 30 * u, fy - 6 * u], INK, 8 * u)
        p.rect([cx + sx * 30 * u - 22 * u, fy - 8 * u, cx + sx * 30 * u + 22 * u, fy + 2 * u], fill=(120, 72, 44), out=INK, w=2 * u, r=4 * u)
    batik_trapezoid(p, cx, fy, u)
    p.line([cx + 62 * u, fy - 190 * u, cx + 92 * u, fy - 262 * u], (90, 58, 40), 8 * u)
    p.line([cx + 92 * u, fy - 262 * u, cx + 104 * u, fy - 290 * u], (190, 190, 200), 4 * u)
    sh_l = (cx - 62 * u, fy - 245 * u + br); sh_r = (cx + 62 * u, fy - 245 * u + br)
    el = (cx - 104 * u, fy - 196 * u); hl = (cx - 112 * u, fy - 232 * u + math.sin(t * 2.4) * 3 * u)
    p.line([*sh_l, *el, *hl], (30, 48, 92), 9 * u); p.ell([hl[0] - 8 * u, hl[1] - 8 * u, hl[0] + 8 * u, hl[1] + 8 * u], fill=SKIN, out=INK, w=2 * u)
    p.line([hl[0], hl[1] + 10 * u, hl[0], hl[1] - 70 * u], (120, 80, 48), 4 * u)
    k = [hl[0], hl[1] - 150 * u, hl[0] + 28 * u, hl[1] - 112 * u, hl[0] + 34 * u, hl[1] - 70 * u, hl[0] + 16 * u, hl[1] - 40 * u, hl[0] - 16 * u, hl[1] - 40 * u, hl[0] - 34 * u, hl[1] - 70 * u, hl[0] - 28 * u, hl[1] - 112 * u]
    p.poly(k, fill=(232, 178, 62), out=INK, w=2.5 * u)
    p.poly([hl[0], hl[1] - 130 * u, hl[0] + 14 * u, hl[1] - 100 * u, hl[0] + 14 * u, hl[1] - 66 * u, hl[0], hl[1] - 52 * u, hl[0] - 14 * u, hl[1] - 66 * u, hl[0] - 14 * u, hl[1] - 100 * u], fill=(176, 40, 40), out=INK, w=2 * u)
    p.line([hl[0], hl[1] - 120 * u, hl[0], hl[1] - 60 * u], (244, 208, 120), 2 * u)
    if wave:
        ang = 150 + math.sin(t * 9) * 16
        r_ = math.radians(ang); e2 = (sh_r[0] + math.sin(r_) * 56 * u + 30 * u, sh_r[1] + math.cos(r_) * 40 * u); hr = (e2[0] + 10 * u, e2[1] - 50 * u)
        er = (cx + 112 * u, fy - 262 * u)
    else:
        er = (cx + 100 * u, fy - 268 * u); hr = (cx + 112 * u, fy - 316 * u) if point else (cx + 104 * u, fy - 196 * u)
        if shock: er = (cx + 110 * u, fy - 290 * u); hr = (cx + 100 * u, fy - 340 * u)
    p.line([*sh_r, *er, *hr], (30, 48, 92), 9 * u); p.ell([hr[0] - 8 * u, hr[1] - 8 * u, hr[0] + 8 * u, hr[1] + 8 * u], fill=SKIN, out=INK, w=2 * u)
    p.ell([cx - 70 * u, fy - 268 * u + br, cx + 70 * u, fy - 132 * u], fill=(30, 48, 92), out=INK, w=3.5 * u)
    p.rect([cx - 66 * u, fy - 176 * u, cx + 66 * u, fy - 160 * u], fill=(220, 168, 56), out=INK, w=2 * u, r=6 * u)
    for i in range(5): p.ell([cx - 3.5 * u, fy - 250 * u + i * 17 * u + br, cx + 3.5 * u, fy - 243 * u + i * 17 * u + br], fill=(244, 208, 120))
    p.poly([cx - 18 * u, fy - 262 * u + br, cx + 18 * u, fy - 262 * u + br, cx, fy - 238 * u + br], fill=SKIN, out=INK, w=2 * u)
    p.rect([cx - 9 * u, fy - 282 * u + br, cx + 9 * u, fy - 262 * u + br], fill=SKIN, out=INK, w=2 * u)
    hc = (cx, fy - 306 * u + br); r = 36 * u
    p.ell([hc[0] - r, hc[1] - r, hc[0] + r, hc[1] + r], fill=SKIN, out=INK, w=3.5 * u)
    for sx in (-1, 1): p.ell([hc[0] + sx * r - 6 * u, hc[1] - 6 * u, hc[0] + sx * r + 6 * u, hc[1] + 10 * u], fill=SKIN, out=INK, w=2 * u)
    p.pie([hc[0] - r * 1.04, hc[1] - r * 1.25, hc[0] + r * 1.04, hc[1] + r * .75], 180, 360, (112, 64, 34))
    p.arc([hc[0] - r * 1.04, hc[1] - r * 1.25, hc[0] + r * 1.04, hc[1] + r * .75], 180, 360, INK, 3 * u)
    p.line([hc[0] - r * 1.02, hc[1] - r * .26, hc[0] + r * 1.02, hc[1] - r * .26], INK, 3 * u)
    p.ell([hc[0] + r * .55, hc[1] - r * 1.2, hc[0] + r * 1.2, hc[1] - r * .62], fill=(112, 64, 34), out=INK, w=2.5 * u)
    for i in range(4): p.line([hc[0] - r * .7 + i * r * .45, hc[1] - r * 1.1, hc[0] - r * .7 + i * r * .45, hc[1] - r * .3], (244, 208, 120), 1.6 * u)
    ex = r * .42; blink = (t % 3.0) < 0.13
    for sx in (-1, 1):
        if blink: p.line([hc[0] + sx * ex - 4.5 * u, hc[1] + r * .08, hc[0] + sx * ex + 4.5 * u, hc[1] + r * .08], INK, 2.5 * u)
        else: p.ell([hc[0] + sx * ex - 4.5 * u, hc[1] + r * .02, hc[0] + sx * ex + 4.5 * u, hc[1] + r * .02 + 11 * u], fill=INK)
        p.line([hc[0] + sx * ex - 9 * u, hc[1] - 8 * u + (2 * u * sx), hc[0] + sx * ex + 9 * u, hc[1] - 10 * u - (2 * u * sx)], INK, 3 * u)
    for sx in (-1, 1): p.ell([hc[0] + sx * r * .62 - 7 * u, hc[1] + r * .28, hc[0] + sx * r * .62 + 7 * u, hc[1] + r * .28 + 8 * u], fill=(255, 190, 170))
    p.arc([hc[0] - r * .55, hc[1] + r * .2, hc[0] + r * .02, hc[1] + r * .62], 190, 350, INK, 4 * u)
    p.arc([hc[0] - r * .02, hc[1] + r * .2, hc[0] + r * .55, hc[1] + r * .62], 190, 350, INK, 4 * u)
    mh = (4 + 17 * mouth) * u
    p.ell([hc[0] - 10 * u, hc[1] + r * .5, hc[0] + 10 * u, hc[1] + r * .5 + mh], fill=(130, 34, 44), out=INK, w=2.5 * u)
