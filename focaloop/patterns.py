#!/usr/bin/env python3
"""Pola dinding lanjutan Focaloop. Semua: kecepatan bola TETAP, semua bola bertemu di satu titik pada satu waktu (Tm).
Teknik yang menjaga aturan itu:
  ellipse   : bola dari fokus F1 -> semua di F2 pada Tm, kembali di F1 pada 2Tm
  circle    : bola dari pusat, tegak lurus dinding -> kembali di pusat pada Tm
  sunburst  : dinding = busur lingkaran beda radius per sektor; bola di sektor kecil berangkat lebih lambat (jeda), semua kembali di pusat pada Tm
  petal     : dinding = busur elips confocal (fokus sama) beda 'a' per sektor; jeda berangkat menyamakan waktu tiba di F2
  nested    : elips confocal berlapis a, a/3, a/5; tiap grup bola memantul di lapisannya sendiri, semua di F2 pada Tm
"""
import math, random, os, sys
import numpy as np, cv2
import bounce3 as b3
from bounce3 import W, H, CX, CY, hsv_bgr, pos_at, text_layer

TM = 1.6


def ell_roots(A, B, phi, px, py, vx, vy):
    cs, sn = math.cos(phi), math.sin(phi)
    x, y = (px - CX) * cs + (py - CY) * sn, -(px - CX) * sn + (py - CY) * cs
    ux, uy = vx * cs + vy * sn, -vx * sn + vy * cs
    a2, b2 = A * A, B * B
    Aq = ux * ux / a2 + uy * uy / b2; Bq = 2 * (x * ux / a2 + y * uy / b2); Cq = x * x / a2 + y * y / b2 - 1
    D = Bq * Bq - 4 * Aq * Cq
    if D < 0: return []
    s = math.sqrt(D)
    out = []
    for t in ((-Bq - s) / (2 * Aq), (-Bq + s) / (2 * Aq)):
        if t > 1e-7:
            hx, hy = x + ux * t, y + uy * t
            nx, ny = hx / a2, hy / b2; n = math.hypot(nx, ny); nx, ny = nx / n, ny / n
            out.append((t, CX + hx * cs - hy * sn, CY + hx * sn + hy * cs, nx * cs - ny * sn, nx * sn + ny * cs))
    return out


def reflect(vx, vy, nx, ny):
    d = vx * nx + vy * ny
    if d < 0: nx, ny, d = -nx, -ny, -d
    return vx - 2 * d * nx, vy - 2 * d * ny, nx, ny


# ---------------- generator jalur ----------------
def paths_ellipse(A, phi, e, n, v, Tend, sector=360.0, rot=0.0, groups=None):
    """groups: daftar (a_k) -> bola i memakai elips confocal a_k (i % len). Fokus sama."""
    c = A * e
    cs, sn = math.cos(phi), math.sin(phi)
    f1 = (CX + c * cs, CY + c * sn)
    out = []
    ellipses = [(a, math.sqrt(a * a - c * c)) for a in (groups or [A])]
    for i in range(n):
        a, b = ellipses[i % len(ellipses)]
        ang = rot + 0.1234 + math.radians(sector) * (i + 0.5) / n
        vx, vy = v * math.cos(ang), v * math.sin(ang)
        px, py = f1; t = 0.0; pts = [(0.0, px, py)]; g = 0
        while t < Tend and g < 200:
            r = ell_roots(a, b, phi, px, py, vx, vy)
            if not r: break
            dt, hx, hy, nx, ny = max(r, key=lambda q: q[0]) if len(r) == 1 else max(r, key=lambda q: q[0])
            t += dt; pts.append((t, hx, hy))
            vx, vy, nx, ny = reflect(vx, vy, nx, ny)
            px, py = hx, hy; g += 1
        pts.append((t + 10, px + vx * 10, py + vy * 10)); out.append(np.array(pts))
    return out, f1


def paths_radial(radfun, n, v, Tend, delayfun):
    out = []
    for i in range(n):
        th = 2 * math.pi * (i + 0.5) / n + 0.1234
        ang = th; t = delayfun(th); pts = [(0.0, CX, CY), (t, CX, CY)]
        while t < Tend:
            r = radfun(ang); t += r / v
            pts.append((t, CX + r * math.cos(ang), CY + r * math.sin(ang))); t += r / v
            pts.append((t, CX, CY)); ang += math.pi
        pts.append((t + 10, CX, CY)); out.append(np.array(pts))
    return out


def paths_petal(A, phi, e, ua, nsec, rot, n, v, Tend):
    """busur elips confocal per sektor (sudut di sekitar F1), dengan dinding radial (langkah) yang juga memantul."""
    c = A * e; cs, sn = math.cos(phi), math.sin(phi)
    f1 = (CX + c * cs, CY + c * sn)
    ak = [A * u for u in ua]; bk = [math.sqrt(a * a - c * c) for a in ak]
    amax = max(ak)
    def sec(px, py):
        th = math.atan2(py - f1[1], px - f1[0])
        return int(((th - rot) % (2 * math.pi)) / (2 * math.pi / nsec)) % nsec
    def point_on(k, th):  # titik elips k pada sudut th di sekitar F1 (garis dari F1)
        lo, hi = 0.0, 2 * A
        dx, dy = math.cos(th), math.sin(th)
        r = ell_roots(ak[k], bk[k], phi, f1[0], f1[1], dx, dy)
        t = max(q[0] for q in r)
        return f1[0] + dx * t, f1[1] + dy * t
    # segmen langkah
    steps = []
    for j in range(nsec):
        k0, k1 = ua[j - 1], ua[j]
        if abs(k0 - k1) < 1e-9: continue
        th = rot + j * 2 * math.pi / nsec
        p0 = point_on(j - 1, th); p1 = point_on(j, th); steps.append((p0, p1))
    def cast(px, py, vx, vy):
        best = None
        for k in range(nsec):
            for q in ell_roots(ak[k], bk[k], phi, px, py, vx, vy):
                if sec(q[1], q[2]) == k and (best is None or q[0] < best[0]): best = q
        for (x0, y0), (x1, y1) in steps:
            sx, sy = x1 - x0, y1 - y0; den = vx * sy - vy * sx
            if abs(den) < 1e-9: continue
            t = ((x0 - px) * sy - (y0 - py) * sx) / den; u = ((x0 - px) * vy - (y0 - py) * vx) / den
            if t > 1e-7 and 0 <= u <= 1 and (best is None or t < best[0]):
                m = math.hypot(sx, sy); best = (t, px + vx * t, py + vy * t, -sy / m, sx / m)
        return best
    out = []
    for i in range(n):
        th = rot + 0.1234 + 2 * math.pi * (i + 0.5) / n
        s = sec(f1[0] + math.cos(th), f1[1] + math.sin(th))
        d = 2 * (amax - ak[s]) / v
        vx, vy = v * math.cos(th), v * math.sin(th); px, py = f1; t = d; pts = [(0.0, px, py), (d, px, py)]; g = 0
        while t < Tend and g < 120:
            r = cast(px, py, vx, vy)
            if r is None: break
            dt, hx, hy, nx, ny = r; t += dt; pts.append((t, hx, hy))
            vx, vy, nx, ny = reflect(vx, vy, nx, ny); px, py = hx, hy; g += 1
        pts.append((t + 10, px + vx * 10, py + vy * 10)); out.append(np.array(pts))
    return out, f1, ak, bk, steps, sec, c, amax


# ---------------- gambar ----------------
def hsv(h, s=0.85, v=1.0): return hsv_bgr(h, s, v)


def draw_poly(img, pts, col, th=2):
    cv2.polylines(img, [np.array(pts, np.int32).reshape(-1, 1, 2)], False, col, th, cv2.LINE_AA)


def render(name, out, paths, wall_fn, t, label, hue0=0.55, span=0.7, gain=0.4, hr=3, bgv=14, tag=""):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - CX) / 520.0) ** 2 + ((yy - CY) / 760.0) ** 2)
    v = np.clip(bgv - 10 * d, 3, bgv)
    base = np.dstack([v * 1.3, v * 1.0, v * 0.9]).astype(np.uint8)
    wall = np.zeros((H, W, 3), np.uint8); wall_fn(wall)
    gl = cv2.GaussianBlur(wall, (0, 0), 7)
    img = cv2.add(base, cv2.add(wall, (gl * 1.3).clip(0, 255).astype(np.uint8)))
    lines = np.zeros((H, W, 3), np.uint8); heads = np.zeros((H, W, 3), np.uint8)
    n = len(paths)
    for i, pa in enumerate(paths):
        col = hsv(hue0 + span * i / n)
        c = tuple(int(q * gain) for q in col)
        ts = pa[:, 0]; k = min(max(int(np.searchsorted(ts, t, side="right")) - 1, 0), len(ts) - 2)
        pts = [(int(pa[j, 1]), int(pa[j, 2])) for j in range(k + 1)]
        x, y, _ = pos_at(pa, t); pts.append((int(x), int(y)))
        for j in range(len(pts) - 1): cv2.line(lines, pts[j], pts[j + 1], c, 1, cv2.LINE_AA)
        cv2.circle(heads, (int(x), int(y)), hr, col, -1, cv2.LINE_AA)
    g1 = cv2.GaussianBlur(heads, (0, 0), 6); g2 = cv2.GaussianBlur(heads, (0, 0), 2)
    f = cv2.add(cv2.add(img, lines), heads)
    f = cv2.add(f, (g1 * 1.8).clip(0, 255).astype(np.uint8)); f = cv2.add(f, (g2 * .8).clip(0, 255).astype(np.uint8))
    tcol, talpha = text_layer("Will they all meet again?", label)
    f[:230] = (f[:230].astype(np.float32) * (1 - talpha) + tcol * talpha).clip(0, 255).astype(np.uint8)
    cv2.putText(f, tag, (30, 1245), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (255, 255, 255), 3, cv2.LINE_AA)
    cv2.imwrite(out, f)


def wall_ellipses(items, col, th=3):
    def fn(img):
        for A, B, phi in items: cv2.ellipse(img, (CX, CY), (int(A), int(B)), math.degrees(phi), 0, 360, col, th, cv2.LINE_AA)
    return fn


def wall_sectors(radii, col, th=3):
    nsec = len(radii)
    def fn(img):
        for s, r in enumerate(radii):
            a0 = 360.0 * s / nsec; a1 = 360.0 * (s + 1) / nsec
            cv2.ellipse(img, (CX, CY), (int(r), int(r)), 0, a0, a1, col, th, cv2.LINE_AA)
            r2 = radii[(s + 1) % nsec]; a = math.radians(a1)
            cv2.line(img, (int(CX + r * math.cos(a)), int(CY + r * math.sin(a))), (int(CX + r2 * math.cos(a)), int(CY + r2 * math.sin(a))), col, th, cv2.LINE_AA)
    return fn


def build_all(outdir):
    os.makedirs(outdir, exist_ok=True)
    R = random.Random(2026); specs = []
    # 1 elips tipis, 2 elips gemuk
    for idx, (A, e, phi_deg, hue) in enumerate([(370, 0.9, -65, 0.5), (330, 0.45, 20, 0.08)], 1):
        phi = math.radians(phi_deg); c = A * e; B = math.sqrt(A * A - c * c); v = 2 * A / TM
        n = 110
        paths, f1 = paths_ellipse(A, phi, e, n, v, 2.2 * TM)
        specs.append((f"p{idx:02d}_elips", paths, wall_ellipses([(A, B, phi)], hsv(hue + 0.5, .8)), 1.5 * TM, f"{n} balls", hue, idx))
    # 3 lingkaran dari pusat
    Rc = 330; v = 2 * Rc / TM; n = 72
    paths = paths_radial(lambda a: Rc, n, v, 2.4 * TM, lambda th: 0.0)
    specs.append(("p03_lingkaran_pusat", paths, wall_ellipses([(Rc, Rc, 0.0), (Rc - 14, Rc - 14, 0.0)], hsv(0.9, .7)), 1.0 * TM + 0.35, f"{n} balls", 0.9, 3))
    # 4-6 sunburst
    def sun(radii, name, idx, hue, n):
        ns = len(radii); rmax = max(radii); v = 2 * rmax / TM
        def rad(a): return radii[int(((a % (2 * math.pi)) / (2 * math.pi)) * ns) % ns]
        paths = paths_radial(rad, n, v, 2.0 * TM, lambda th: 2 * (rmax - rad(th)) / v)
        specs.append((name, paths, wall_sectors(radii, hsv(hue + 0.5, .75)), TM + 0.3, f"{n} balls", hue, idx))
    sun([330, 190] * 3, "p04_sunburst_gear", 4, 0.12, 96)
    sun([R.choice([200, 240, 280, 330]) for _ in range(10)], "p05_sunburst_acak", 5, 0.3, 120)
    sun([150 + 180 * s / 15 for s in range(16)], "p06_spiral_siput", 6, 0.75, 128)
    # 7,10 petal elips confocal
    for idx, (ua, ns, e, phi_deg, hue, n) in enumerate([([1, .72], 2, .5, -70, 0.0, 120), ([1, .6], 2, .45, 20, 0.45, 150)], 0):
        A = 335; phi = math.radians(phi_deg); v = 2 * A / TM
        rot = phi
        paths, f1, ak, bk, steps, sec, c, amax = paths_petal(A, phi, e, ua, ns, rot, n, v, 2.0 * TM)
        def wf(img, ak=ak, bk=bk, sec=sec, steps=steps, phi=phi, hue=hue):
            col = hsv(hue + 0.5, .75); cs, sn = math.cos(phi), math.sin(phi)
            for k in range(len(ak)):
                pts = []
                for q in range(2400):
                    th = 2 * math.pi * q / 2400; x, y = ak[k] * math.cos(th), bk[k] * math.sin(th)
                    wx, wy = CX + x * cs - y * sn, CY + x * sn + y * cs
                    if sec(wx, wy) == k: pts.append((wx, wy))
                    else:
                        if len(pts) > 1: draw_poly(img, pts, col, 3)
                        pts = []
                if len(pts) > 1: draw_poly(img, pts, col, 3)
            for (x0, y0), (x1, y1) in steps: cv2.line(img, (int(x0), int(y0)), (int(x1), int(y1)), col, 3, cv2.LINE_AA)
        specs.append((f"p{7 if idx == 0 else 10:02d}_tetesan_{idx + 1}", paths, wf, TM + 0.3, f"{n} balls", hue, 7 if idx == 0 else 10))
    # 8,9 elips berlapis confocal
    for idx, (A, e, phi_deg, groups, hue, n) in enumerate([(340, 0.15, -50, [1, 1 / 3, 1 / 5], 0.6, 120), (340, 0.3, 30, [1, 1 / 3], 0.18, 100)]):
        phi = math.radians(phi_deg); c = A * e; v = 2 * A / TM
        ag = [A * g for g in groups]
        paths, f1 = paths_ellipse(A, phi, e, n, v, 2.0 * TM, groups=ag)
        items = [(a, math.sqrt(a * a - c * c), phi) for a in ag]
        specs.append((f"p{8 + idx:02d}_elips_berlapis_{len(groups)}", paths, wall_ellipses(items, hsv(hue + 0.5, .75)), TM + 0.25, f"{n} balls", hue, 8 + idx))
    specs.sort(key=lambda s: s[6])
    for name, paths, wf, t, label, hue, idx in specs:
        render(name, os.path.join(outdir, name + ".png"), paths, wf, t, label, hue0=hue, tag=f"#{idx}")
        print(name)


if __name__ == "__main__":
    build_all(sys.argv[1])
