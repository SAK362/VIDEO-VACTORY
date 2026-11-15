#!/usr/bin/env python3
"""Sistem multi-titik Focaloop. Bola keluar dari 1-5 titik awal, kena dinding, KEMBALI KE TITIK ITU SERENTAK pada Tret.
Kecepatan v tetap. Jenis sistem:
  radial   : 1 titik (pusat). Dinding = busur lingkaran (radius bisa beda per sektor, jeda berangkat menyamakan waktu). Bola tegak lurus dinding.
  ellipse  : 2 titik (kedua fokus). Bola dari satu fokus lewat dinding ke fokus lain (tukar posisi) lalu pulang. Bisa berlapis (a/ganjil).
  reuleaux : 3 atau 5 titik (puncak segi-n Reuleaux). Busur di seberang tiap puncak berpusat di puncak itu -> bola tegak lurus, pulang.
Gabungan beberapa sistem (lapisan) dipakai untuk 3-5 titik: bola tiap sistem hanya memantul di dinding sistemnya sendiri."""
import math, random
import numpy as np
import cv2
from bounce3 import CX, CY, hsv_bgr

RMAX = 335.0


def roots(cx, cy, A, B, phi, px, py, vx, vy):
    cs, sn = math.cos(phi), math.sin(phi)
    x, y = (px - cx) * cs + (py - cy) * sn, -(px - cx) * sn + (py - cy) * cs
    ux, uy = vx * cs + vy * sn, -vx * sn + vy * cs
    a2, b2 = A * A, B * B
    Aq = ux * ux / a2 + uy * uy / b2; Bq = 2 * (x * ux / a2 + y * uy / b2); Cq = x * x / a2 + y * y / b2 - 1
    D = Bq * Bq - 4 * Aq * Cq
    if D < 0: return []
    s = math.sqrt(D); out = []
    for t in ((-Bq - s) / (2 * Aq), (-Bq + s) / (2 * Aq)):
        if t > 1e-7:
            hx, hy = x + ux * t, y + uy * t
            nx, ny = hx / a2, hy / b2; n = math.hypot(nx, ny); nx, ny = nx / n, ny / n
            out.append((t, cx + hx * cs - hy * sn, cy + hx * sn + hy * cs, nx * cs - ny * sn, nx * sn + ny * cs))
    return out


# ---------------- pembuat sistem ----------------
def radial_radii(r):
    kind = r.choice(["circle", "circle", "sunburst", "sunburst", "spiral", "wavy"])
    if kind == "circle": return kind, [1.0]
    ns = r.choice([3, 4, 5, 6, 8, 10, 12, 16, 24, 36]); lo = r.uniform(0.38, 0.85)
    if kind == "sunburst":
        ch = [1.0, lo, (1 + lo) / 2]
        if r.random() < 0.5 and ns % 2 == 0:
            a, b = r.sample(ch, 2); rad = [a if i % 2 == 0 else b for i in range(ns)]
        else: rad = [r.choice([lo, (1 + lo) / 2, 1.0, 1.0]) for _ in range(ns)]
    elif kind == "spiral":
        ns = max(ns, 8); rad = [lo + (1 - lo) * s / (ns - 1) for s in range(ns)]
        if r.random() < .5: rad = rad[::-1]
    else:
        ns = max(ns, 12); ph = r.uniform(0, 6.28); k = r.choice([1, 2, 3, 4, 5])
        rad = [lo + (1 - lo) * (0.5 + 0.5 * math.sin(ph + 2 * math.pi * k * s / ns)) for s in range(ns)]
    m = max(rad); return kind, [x / m for x in rad]


def place(r, extent, multi):
    if not multi: return (CX, CY)
    room = max(RMAX - extent, 0.0); ang = r.uniform(0, 2 * math.pi); d = r.uniform(0.3, 1.0) * room
    return (CX + d * math.cos(ang), CY + d * math.sin(ang))


def make_radial(r, multi):
    u = r.uniform(0.5, 0.85) if multi else r.uniform(0.75, 1.0)
    R = RMAX * u; kind, rel = radial_radii(r)
    return dict(type="radial", name=kind, c=place(r, R, multi), radii=[R * x for x in rel], sources=1, Lmax=2 * R, phase=r.uniform(0, 6.28))


def make_ellipse(r, multi, nested_ok=True):
    u = r.uniform(0.55, 0.9) if multi else r.uniform(0.8, 1.0)
    A = RMAX * u
    odds = [1]
    if nested_ok and r.random() < 0.3: odds = r.choice([[1, 3], [1, 3], [1, 3, 5], [1, 5]])
    emax = 0.93 if len(odds) == 1 else 0.9 / max(odds) * 0.96
    e = 0.0 if (len(odds) == 1 and r.random() < .05) else r.uniform(0.12 if len(odds) == 1 else 0.04, emax)
    return dict(type="ellipse", name="nested" if len(odds) > 1 else "ellipse", c=place(r, A, multi), A=A, e=e, phi=r.uniform(0, math.pi),
                odds=odds, sources=2, Lmax=4 * A, phase=r.uniform(0, 6.28))


def make_reuleaux(r, n, multi):
    R = (r.uniform(0.45, 0.75) if multi else r.uniform(0.8, 1.0)) * 558.0
    rho = R / (2 * math.cos(math.pi / (2 * n)))
    return dict(type="reuleaux", name=f"reuleaux{n}", c=place(r, 0.6 * R, multi), R=R, n=n, rot=r.uniform(0, 2 * math.pi), rho=rho,
                sources=n, Lmax=2 * R, phase=0.0)


def gen_systems(r, k):
    # 1 dinding saja per tahap
    opts = {1: [("R",)], 2: [("E",)], 3: [("U3",)], 5: [("U5",)]}[k]
    plan = r.choice(opts); multi = len(plan) > 1; out = []
    for t in plan:
        if t == "R": out.append(make_radial(r, multi))
        elif t == "E": out.append(make_ellipse(r, multi, False))
        elif t == "U3": out.append(make_reuleaux(r, 3, multi))
        else: out.append(make_reuleaux(r, 5, multi))
    return out


def sources_of(sy):
    cx, cy = sy["c"]
    if sy["type"] == "radial": return [(cx, cy)]
    if sy["type"] == "ellipse":
        c = sy["A"] * sy["e"]; cs, sn = math.cos(sy["phi"]), math.sin(sy["phi"])
        return [(cx + c * cs, cy + c * sn), (cx - c * cs, cy - c * sn)]
    n = sy["n"]
    return [(cx + sy["rho"] * math.cos(sy["rot"] + 2 * math.pi * i / n), cy + sy["rho"] * math.sin(sy["rot"] + 2 * math.pi * i / n)) for i in range(n)]


# ---------------- gambar dinding ----------------
def draw_system(sy, img, col, th):
    cx, cy = sy["c"]; t = sy["type"]
    if t == "radial":
        radii = sy["radii"]; ns = len(radii)
        if ns == 1:
            cv2.circle(img, (int(cx), int(cy)), int(radii[0]), col, th, cv2.LINE_AA)
            cv2.circle(img, (int(cx), int(cy)), int(radii[0]) - 12, col, max(th - 1, 1), cv2.LINE_AA)
        else:
            for s, rr in enumerate(radii):
                a0 = 360.0 * s / ns; a1 = 360.0 * (s + 1) / ns
                cv2.ellipse(img, (int(cx), int(cy)), (int(rr), int(rr)), 0, a0, a1, col, th, cv2.LINE_AA)
                r2 = radii[(s + 1) % ns]; a = math.radians(a1)
                cv2.line(img, (int(cx + rr * math.cos(a)), int(cy + rr * math.sin(a))), (int(cx + r2 * math.cos(a)), int(cy + r2 * math.sin(a))), col, th, cv2.LINE_AA)
    elif t == "ellipse":
        c = sy["A"] * sy["e"]
        for o in sy["odds"]:
            a = sy["A"] / o; b = math.sqrt(max(a * a - c * c, 1.0))
            cv2.ellipse(img, (int(cx), int(cy)), (int(a), int(b)), math.degrees(sy["phi"]), 0, 360, col, th, cv2.LINE_AA)
    else:
        V = sources_of(sy); n = sy["n"]; m = (n - 1) // 2
        for i in range(n):
            a1, a2 = reu_angles(V, i, n, m)
            lo, hi = (a1, a2) if a2 > a1 else (a2, a1)
            cv2.ellipse(img, (int(V[i][0]), int(V[i][1])), (int(sy["R"]), int(sy["R"])), 0, math.degrees(min(a1, a1 + (a2 - a1))), math.degrees(max(a1, a1 + (a2 - a1))), col, th, cv2.LINE_AA)


def reu_angles(V, i, n, m):
    j1, j2 = (i + m) % n, (i + m + 1) % n
    a1 = math.atan2(V[j1][1] - V[i][1], V[j1][0] - V[i][0]); a2 = math.atan2(V[j2][1] - V[i][1], V[j2][0] - V[i][0])
    d = ((a2 - a1 + math.pi) % (2 * math.pi)) - math.pi
    return a1, a1 + d


# ---------------- jalur bola ----------------
def stage_paths(systems, n_per, v, Lmax, Tret):
    """-> paths, meets[(t,[pts])], worst. Tiap bola: tunggu (jeda) -> keluar -> dinding -> kembali ke titik awal tepat pada Tret."""
    paths = []; meets = {}; worst = 0.0
    for sy in systems:
        srcs = sources_of(sy); cx, cy = sy["c"]
        for si, o in enumerate(srcs):
            for j in range(n_per):
                if sy["type"] == "radial":
                    radii = sy["radii"]; ns = len(radii)
                    th = 2 * math.pi * (j + 0.5) / n_per + 0.1234 + sy["phase"]
                    rr = radii[int(((th % (2 * math.pi)) / (2 * math.pi)) * ns) % ns]
                    d = (Lmax - 2 * rr) / v
                    w = (o[0] + rr * math.cos(th), o[1] + rr * math.sin(th))
                    pts = [(0.0, o[0], o[1]), (d, o[0], o[1]), (d + rr / v, w[0], w[1]), (Tret, o[0], o[1]), (Tret + 10, o[0], o[1])]
                    paths.append(np.array(pts)); continue
                if sy["type"] == "reuleaux":
                    n = sy["n"]; m = (n - 1) // 2; a1, a2 = reu_angles(srcs, si, n, m)
                    th = a1 + (a2 - a1) * (j + 0.5) / n_per; R = sy["R"]
                    d = (Lmax - 2 * R) / v
                    w = (o[0] + R * math.cos(th), o[1] + R * math.sin(th))
                    pts = [(0.0, o[0], o[1]), (d, o[0], o[1]), (d + R / v, w[0], w[1]), (Tret, o[0], o[1]), (Tret + 10, o[0], o[1])]
                    paths.append(np.array(pts)); continue
                # ellipse (bisa berlapis)
                odds = sy["odds"]; grp = j % len(odds); a = sy["A"] / odds[grp]; c = sy["A"] * sy["e"]; b = math.sqrt(max(a * a - c * c, 1e-9))
                th = 2 * math.pi * (j + 0.5) / n_per + 0.1234 + sy["phase"] + si * 0.7
                d = (Lmax - 4 * sy["A"]) / v
                vx, vy = v * math.cos(th), v * math.sin(th); px, py = o; t = d
                pts = [(0.0, px, py), (d, px, py)]; g = 0
                while t < Tret + 0.05 and g < 220:
                    r_ = roots(cx, cy, a, b, sy["phi"], px, py, vx, vy)
                    if not r_: break
                    dt, hx, hy, nx, ny = max(r_, key=lambda q: q[0])
                    t += dt; pts.append((t, hx, hy)); dd = vx * nx + vy * ny
                    vx, vy = vx - 2 * dd * nx, vy - 2 * dd * ny; px, py = hx, hy; g += 1
                pts.append((t + 10, px + vx * 10, py + vy * 10)); pa = np.array(pts)
                from bounce3 import pos_at
                x, y, _ = pos_at(pa, Tret); worst = max(worst, math.hypot(x - o[0], y - o[1]))
                mid = d + 2 * sy["A"] / v
                x, y, _ = pos_at(pa, mid); other = srcs[1 - si]; worst = max(worst, math.hypot(x - other[0], y - other[1]))
                keep = pa[pa[:, 0] < Tret - 1e-6]
                paths.append(np.vstack([keep, [[Tret, o[0], o[1]], [Tret + 10, o[0], o[1]]]]))
                meets.setdefault(round(d + 2 * sy["A"] / v, 3), set()).update(srcs)
    meets[round(Tret, 3)] = set(p for sy in systems for p in sources_of(sy))
    ml = [(t, sorted(pts)) for t, pts in sorted(meets.items())]
    return paths, ml, worst
