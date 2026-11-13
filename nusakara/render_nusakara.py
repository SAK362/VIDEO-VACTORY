"""NUSAKARA: render 1080x1920@30 (Pillow + ffmpeg), tanpa Chrome.
  python nusakara/render_nusakara.py meta                 -> jumlah frame
  python nusakara/render_nusakara.py chunk i n OUT.mp4    -> render potongan ke-i dari n (video saja)
  python nusakara/render_nusakara.py still T [T...]       -> frame uji ke stills/f_T.jpg (T = detik)
Masukan: work/props.json (spec adegan) + nusakara/timing.js (dari webgl/make_timing.py, TIMING_OUT=nusakara/timing.js).
Zona aman (semua platform): atas 220, bawah 480, kanan 180, kiri 50 px. Panggung aksi y 480-1200."""
import json, math, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import Pen, layer, W, H, INK, mix
import lib_char as C
import lib_props as P

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
PROPS = os.environ.get("PROPS_FILE", "work/props.json")
SPOS = {"kiri": 250, "tengah": 540, "kanan": 830, "bawah": 440, "atas": 640}
STYLE = os.environ.get("NUSAKARA_STYLE", "3d")   # 3d | 25d
PARALLAX = 0.55   # 0 = lapisan jauh diam, 1 = ikut kamera penuh
CAM = {"tutup": 1.45, "sedang": 1.28, "lebar": 1.12}
TEAL = (31, 122, 99); MINT = (150, 226, 196)


def load():
    props = json.load(open(PROPS, encoding="utf-8"))
    t = json.loads(re.search(r"=(.*);\s*$", open(os.path.join(HERE, "timing.js"), encoding="utf-8").read(), re.S).group(1))
    return props, t


def total_frames(t): return int(round((t["dur"] + 0.8) * FPS))


_VIG = None
def vignette():
    """Gelap tipis di tepi bingkai: memberi kedalaman."""
    global _VIG
    if _VIG is None:
        m = Image.radial_gradient("L").resize((W, H), Image.BILINEAR).point(lambda v: max(0, v - 90) * 100 // 165)
        _VIG = Image.new("RGBA", (W, H), (18, 22, 44, 0)); _VIG.putalpha(m)
    return _VIG


def volume(Lr):
    """Efek 2.5D pada lapisan tokoh/properti: cahaya di tepi atas-kiri, bayangan di tepi bawah-kanan, bayangan jatuh lembut."""
    a = Lr.getchannel("A")
    lit = ImageChops.subtract(a, ImageChops.offset(a, 5, 5)).filter(ImageFilter.GaussianBlur(1.6))
    shd = ImageChops.subtract(a, ImageChops.offset(a, -6, -6)).filter(ImageFilter.GaussianBlur(2.2))
    hi = Image.new("RGBA", Lr.size, (255, 250, 236, 0)); hi.putalpha(ImageChops.multiply(lit.point(lambda v: min(255, v * 2) * 60 // 100), a))
    lo = Image.new("RGBA", Lr.size, (30, 24, 60, 0)); lo.putalpha(ImageChops.multiply(shd.point(lambda v: min(255, v * 2) * 40 // 100), a))
    out = Image.alpha_composite(Lr, lo); out = Image.alpha_composite(out, hi)
    return out


def drop_shadow(Lr, hor):
    """Bayangan jatuh lembut ke arah kanan-bawah, hanya di bawah kaki langit (di tanah/dek/laut)."""
    a = Lr.getchannel("A").filter(ImageFilter.GaussianBlur(9)); a = ImageChops.offset(a, 16, 20)
    a = a.point(lambda v: v * 60 // 255)
    if hor > 0: a.paste(0, (0, 0, W, min(H, hor)))
    sh = Image.new("RGBA", Lr.size, (24, 20, 44, 0)); sh.putalpha(a); return sh


def volume3d(Lr):
    """3D semu: peta tinggi dari alpha dibulatkan -> normal -> cahaya difus, kilap spekular, cahaya tepi, hangat di sisi gelap."""
    arr = np.asarray(Lr).astype(np.float32); a = arr[..., 3] / 255.0
    h = (np.asarray(Lr.getchannel("A").filter(ImageFilter.GaussianBlur(8))).astype(np.float32) * 0.6
         + np.asarray(Lr.getchannel("A").filter(ImageFilter.GaussianBlur(20))).astype(np.float32) * 0.4) / 255.0
    gy, gx = np.gradient(h); k = 16.0
    nx, ny, nz = -gx * k, -gy * k, np.ones_like(h); n = np.sqrt(nx * nx + ny * ny + nz * nz); nx /= n; ny /= n; nz /= n
    Lx, Ly, Lz = -0.5, -0.62, 0.6; ln = (Lx * Lx + Ly * Ly + Lz * Lz) ** .5; Lx /= ln; Ly /= ln; Lz /= ln
    dif = np.clip(nx * Lx + ny * Ly + nz * Lz, 0, 1)
    hx, hy, hz = Lx, Ly, Lz + 1.0; hn = (hx * hx + hy * hy + hz * hz) ** .5
    spec = np.clip((nx * hx + ny * hy + nz * hz) / hn, 0, 1) ** 28 * 0.34
    lum = (0.70 + 0.46 * dif)[..., None]
    rgb = arr[..., :3] * lum
    shade = np.clip(1 - dif, 0, 1)[..., None]
    rgb = rgb + shade * np.array([22, 8, 30], np.float32) * 0.0 - shade * (rgb * 0.0)      # (tetap netral)
    rgb = rgb * (1 - 0.10 * shade) + np.array([60, 30, 70], np.float32) * 0.10 * shade      # pantulan hangat-ungu di sisi gelap
    rgb = rgb + spec[..., None] * 255.0 * a[..., None]
    out = np.concatenate([np.clip(rgb, 0, 255), arr[..., 3:4]], axis=-1).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


class Show:
    def __init__(s):
        s.props, s.T = load(); s.sc = s.props["scenes"]; s.spans = s.T["sent_spans"]; s.words = s.T["words"]; s.mouth = s.T["mouth"]
        n = len(s.sc); s.t0 = [0.0] + [max(0.0, s.spans[i][0] - 0.06) for i in range(1, n)]; s.t1 = s.t0[1:] + [s.T["dur"] + 0.9]
        s.bgc = {}; s.heading = []; h = ""
        for sc in s.sc:
            h = sc.get("judul") or h; s.heading.append(h)
        s.label = s.props.get("label_judul", "CERITA RAKYAT")
        s.warned = set(); s.phr = [s.phrases(i) for i in range(n)]

    def scene_at(s, T):
        for i in range(len(s.sc)):
            if T < s.t1[i]: return i
        return len(s.sc) - 1

    def phrases(s, si):
        ws = [w for w in s.words if w["si"] == si]; out = []; cur = []
        for w in ws:
            cur.append(w)
            if (len(cur) >= 6) or (len(cur) >= 2 and re.search(r"[,.!?;:]$", w["w"])) :
                out.append(cur); cur = []
        if cur:
            if out and len(cur) == 1: out[-1] += cur
            else: out.append(cur)
        return out

    def warn(s, kind, k):
        if (kind, k) not in s.warned: s.warned.add((kind, k)); print("WARN %s tak dikenal: %s" % (kind, k), flush=True)

    # ---------- kamera ----------
    def camera(s, sc, tl, dur):
        z0 = CAM.get(sc.get("kamera", "sedang"), 1.14); g = sc.get("gerak", "diam_merayap"); k = min(1.0, tl / max(dur, 0.5))
        k = k * k * (3 - 2 * k); cx = 540.0; cy = 840.0 + 65.0 / z0
        if g == "dorong_masuk": z = z0 * (1 + 0.12 * k)
        elif g == "geser_kanan": z = z0 * 1.05; cx = 540 + (-30 + 60 * k) * (1 if z0 > 1.02 else 0.4)
        else: z = z0 * (1 + 0.03 * k)
        z = max(1.0, z); hw = W / 2.0 / z; hh = H / 2.0 / z
        cx = min(max(cx, hw), W - hw); cy = min(max(cy, hh), H - hh)
        return z, cx, cy

    def bg(s, i, sc):
        key = (i)
        if key not in s.bgc:
            s.bgc.clear(); s.bgc[key] = P.build_bg2(sc.get("latar", "pantai_air_manis_siang"), sc.get("waktu", "siang"))
        return s.bgc[key]

    # ---------- frame ----------
    def frame(s, f):
        T = f / float(FPS); i = s.scene_at(T); sc = s.sc[i]; tl = T - s.t0[i]; dur = s.t1[i] - s.t0[i]
        z, cx, cy = s.camera(sc, tl, dur)
        far, near = s.bg(i, sc)
        box = (int((cx - W / 2.0 / z) * 2), int((cy - H / 2.0 / z) * 2), int((cx + W / 2.0 / z) * 2), int((cy + H / 2.0 / z) * 2))
        # paralaks 2.5D: lapisan jauh bergerak/zoom lebih lambat, kaki langit tetap sejajar
        zf = 1 + (z - 1) * PARALLAX; hwf = W / 2.0 / zf; cxf = min(max(540 + (cx - 540) * PARALLAX, hwf), W - hwf)
        cyf = 720 - (720 - cy) * z / zf; hhf = H / 2.0 / zf; cyf = min(max(cyf, hhf), H - hhf)
        fbox = (int((cxf - hwf) * 2), int((cyf - hhf) * 2), int((cxf + hwf) * 2), int((cyf + hhf) * 2))
        base = far.crop(fbox).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.8)).convert("RGBA")
        base.alpha_composite(near.crop(box).resize((W, H), Image.BILINEAR))
        L = layer(2); p = Pen(L, 2, z, cx, cy); ctx = dict(dur=dur, heads=[], feet=[])
        for k in sc.get("properti", []):
            fn = P.PROPS.get(k)
            if fn is None: s.warn("properti", k); continue
            fn(p, tl, ctx)
        toks = sc.get("tokoh", []); n = len(toks)
        for j, tk in enumerate(toks):
            pos = tk.get("posisi", "tengah"); x = SPOS.get(pos, 540); fy = 1130; bh = 330; pose = tk.get("pose", "berdiri")
            if pos == "bawah": bh = 370; fy = 1190
            if pos == "atas": bh = 290; fy = 1010
            fc = 1 if x < 540 else -1
            if n == 1 and pos == "tengah": fc = 1
            if pose in ("berjalan", "naik_kapal"): x += -90 + min(tl, 4) * 45
            if pose == "berlari": x += -150 + min(tl, 3) * 120; fc = 1
            if tk.get("kunci") not in C.OUTFIT: s.warn("tokoh", tk.get("kunci"))
            info = C.person(p, x, fy, tk.get("kunci"), pose, tk.get("ekspresi", "tenang"), tl, fc, bh, seed=j + i)
            ctx["heads"].append((info["head"][0] + (6 if fc > 0 else -6), info["head"][1])); ctx["feet"].append((x, fy))
        Lr = L.resize((W, H), Image.LANCZOS)
        if STYLE == "3d":
            hor = int((720 - cy) * z + H / 2)
            base.alpha_composite(drop_shadow(Lr, hor)); Lr = volume3d(Lr)
        else: Lr = volume(Lr)
        base.alpha_composite(Lr)
        L = layer(2); p = Pen(L, 2, z, cx, cy)
        ov = None
        for k in sc.get("efek", []):
            fn = P.FX.get(k)
            if fn is None: s.warn("efek", k); continue
            if k in ("awan_gelap", "petir", "kabut_pagi"):
                if ov is None: ov = layer(2)
            fn(p, tl, ctx, ov)
        base = Image.alpha_composite(base, L.resize((W, H), Image.LANCZOS))
        if ov is not None: base = Image.alpha_composite(base, ov.resize((W, H), Image.LANCZOS))
        base = Image.alpha_composite(base, vignette())
        if STYLE == "3d":
            rgb = base.convert("RGB"); rgb = ImageEnhance.Color(rgb).enhance(1.14); rgb = ImageEnhance.Contrast(rgb).enhance(1.05)
            bl = rgb.point(lambda v: max(0, v - 200) * 4).filter(ImageFilter.GaussianBlur(26))   # bloom lembut
            base = Image.blend(rgb, ImageChops.screen(rgb, bl), 0.55).convert("RGBA")
        # Pak Nusa (maskot): tanpa kamera
        U = layer(2); pu = Pen(U, 2)
        mi = min(f, len(s.mouth) - 1); mv = s.mouth[mi] if s.mouth else 0.0
        C.pak_nusa(pu, 128, 1896, 290, mouth=mv, t=T, wave=(T < 3.0 or i == len(s.sc) - 1), shock=("sting_tegang" in sc.get("sfx", [])), point=True)
        Ur = U.resize((W, H), Image.LANCZOS)
        if STYLE == "3d": base.alpha_composite(drop_shadow(Ur, 0)); Ur = volume3d(Ur)
        base = Image.alpha_composite(base, Ur)
        im = base.convert("RGB"); s.ui(im, i, T, sc)
        # transisi
        tr = sc.get("transisi", "potong"); fr = f - int(round(s.t0[i] * FPS))
        if tr == "kilat_putih" and 0 <= fr < 6: im = Image.blend(im, Image.new("RGB", im.size, (255, 255, 255)), 1 - fr / 6.0)
        if tr == "pudar" and 0 <= fr < 10: im = Image.blend(im, Image.new("RGB", im.size, (30, 36, 34)), 1 - fr / 10.0)
        return im

    # ---------- UI 2D ----------
    def ui(s, im, i, T, sc):
        # layout mengikuti FAKTA UNIK: panel judul atas, watermark kanan bawah, subtitle tengah-bawah, maskot kiri bawah
        pan = Image.new("RGBA", (W, 340), (0, 0, 0, 0)); pd = ImageDraw.Draw(pan)
        for y in range(340):
            t = y / 340.0; al = 247 - (247 - 217) * (t / 0.72) if t < 0.72 else 217 * (1 - (t - 0.72) / 0.28)
            pd.line([(0, y), (W, y)], fill=(237, 235, 221, int(max(0, al))))
        im.paste(pan, (0, 0), pan); d = ImageDraw.Draw(im, "RGBA")
        lab = "  ".join(" ".join(w) for w in s.label.upper().split(" "))
        d.text((W / 2, 140), lab, font=P.font(25, True), fill=(86, 101, 94), anchor="ms")
        s.heading_draw(d, s.heading[i])
        # watermark NUSAKARA tengah atas
        f = P.font(36); a, b = "NUSA", "KARA"; wa = d.textlength(a, font=f); wb = d.textlength(b, font=f)
        ph = 76; pw = wa + wb + 80; x0 = (W - pw) / 2; y0 = 22
        d.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], radius=38, fill=(21, 34, 31, 240))
        d.text((x0 + 28, y0 + ph / 2 + 2), a, font=f, fill=(255, 255, 255), anchor="lm")
        d.rounded_rectangle([x0 + 28 + wa - 6 + 6, y0 + 12, x0 + 28 + wa + 6 + wb + 18, y0 + ph - 12], radius=11, fill=(127, 224, 194))
        d.text((x0 + 28 + wa + 15, y0 + ph / 2 + 2), b, font=f, fill=(21, 34, 31), anchor="lm")
        s.subtitle(im, i, T)

    def heading_draw(s, d, text):
        if not text: return
        ft = P.font(58); toks = re.findall(r"\*[^*]+\*|[^\s*]+", text); sp = d.textlength(" ", font=ft); lines = [[]]; wcur = 0
        for tk in toks:
            clean = tk.strip("*"); w = d.textlength(clean, font=ft); add = (0 if (re.fullmatch(r"[^\w]+", clean) and lines[-1]) else (sp if lines[-1] else 0)) + w
            if wcur + add > 940 and lines[-1]: lines.append([tk]); wcur = w
            else: lines[-1].append(tk); wcur += add
        lines = lines[:2]; y = 222 if len(lines) == 1 else 212
        for ln in lines:
            ws = [d.textlength(t.strip("*"), font=ft) for t in ln]; pn = [1 if (k and re.fullmatch(r"[^\w]+", t.strip("*"))) else 0 for k, t in enumerate(ln)]; tw = sum(ws) + sp * (len(ln) - 1 - sum(pn)); x = W / 2 - tw / 2
            for t, w, q in zip(ln, ws, pn):
                clean = t.strip("*"); kw = t.startswith("*")
                if q: x -= sp
                d.text((x, y), clean, font=ft, fill=TEAL if kw else (20, 24, 27), anchor="ls"); x += w + sp
            y += 74

    def subtitle(s, im, i, T):
        phr = s.phr[i]
        if not phr: return
        cur = None
        for k, ph in enumerate(phr):
            nxt = phr[k + 1][0]["start"] if k + 1 < len(phr) else 1e9
            if ph[0]["start"] - 0.05 <= T < min(nxt - 0.03, ph[-1]["end"] + 0.7) or (ph[0]["start"] - 0.05 <= T and nxt > T and T < ph[-1]["end"] + 0.7): cur = ph
        if cur is None: return
        f = P.font(50); d = ImageDraw.Draw(im, "RGBA"); sp = d.textlength(" ", font=f); maxw = 800
        lines = [[]]; wc = 0
        for w in cur:
            ww = d.textlength(w["w"], font=f); add = (sp if lines[-1] else 0) + ww
            if wc + add > maxw and lines[-1]: lines.append([w]); wc = ww
            else: lines[-1].append(w); wc += add
        lines = lines[:2]
        wid = [sum(d.textlength(w["w"], font=f) for w in ln) + sp * (len(ln) - 1) for ln in lines]
        LH = 72; bw = max(wid) + 70; bh = len(lines) * LH + 30; cxs = W / 2; cys = 1522; by0 = cys - bh / 2
        cap = Image.new("RGBA", im.size, (0, 0, 0, 0)); cd = ImageDraw.Draw(cap)
        cd.rounded_rectangle([cxs - bw / 2, by0, cxs + bw / 2, by0 + bh], radius=30, fill=(30, 58, 52, 237)); im.paste(cap, (0, 0), cap)
        active = None
        for w in cur:
            if w["start"] - 0.06 <= T: active = w
        for li, ln in enumerate(lines):
            x = cxs - wid[li] / 2.0; yc = by0 + 15 + li * LH + LH / 2
            for w in ln:
                ww = d.textlength(w["w"], font=f)
                if w is active: s.batik(im, x - 10, yc - 36, ww + 20, 70)
                d = ImageDraw.Draw(im, "RGBA"); d.text((x, yc), w["w"], font=f, fill=(255, 255, 255), anchor="lm"); x += ww + sp

    def batik(s, im, x, y, w, h):
        w = int(w); h = int(h); tile = Image.new("RGBA", (w, h), (0, 0, 0, 0)); td = ImageDraw.Draw(tile)
        td.rounded_rectangle([0, 0, w - 1, h - 1], radius=12, fill=MINT + (70,)); c = 14
        for ci in range(-1, w // c + 2):
            for ri in range(-1, 7):
                px = ci * c + (c / 2 if ri % 2 else 0); py = ri * c * 0.9 + 4
                for ex, ey in ((-4, 0), (4, 0), (0, -4), (0, 4)): td.ellipse([px + ex - 5, py + ey - 5, px + ex + 5, py + ey + 5], outline=MINT + (170,), width=1)
        mask = Image.new("L", (w, h), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=12, fill=255)
        alpha = Image.composite(tile.split()[3], Image.new("L", (w, h), 0), mask); tile.putalpha(alpha)
        im.paste(tile, (int(x), int(y)), tile)


def main():
    mode = sys.argv[1]; sh = Show(); n = total_frames(sh.T)
    if mode == "meta": print(json.dumps({"frames": n, "seconds": round(n / FPS, 2)})); return
    if mode == "still":
        os.makedirs("stills", exist_ok=True)
        for t in sys.argv[2:]:
            sh.frame(int(float(t) * FPS)).save("stills/f_%s.jpg" % t, quality=92)
        return
    ci, cn, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    a, z = n * ci // cn, n * (ci + 1) // cn
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    import io
    for f in range(a, z):
        buf = io.BytesIO(); sh.frame(f).save(buf, "JPEG", quality=94); ff.stdin.write(buf.getvalue())
        if (f - a) % 30 == 0: print("frame %d/%d (potongan %d: %d-%d)" % (f, n, ci, a, z), flush=True)
    ff.stdin.close()
    if ff.wait() != 0: raise SystemExit("ffmpeg gagal")


if __name__ == "__main__":
    main()
