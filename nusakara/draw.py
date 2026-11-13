"""Pen: kuas vektor Pillow dengan supersampling dan kamera (zoom + pusat). Koordinat dunia 1080x1920."""
from PIL import Image, ImageDraw
INK = (46, 30, 38)
SKIN = (255, 246, 232)
W, H = 1080, 1920


class Pen:
    def __init__(s, im, ss=2, z=1.0, cx=540.0, cy=960.0):
        s.im = im; s.d = ImageDraw.Draw(im); s.ss = ss; s.z = z; s.cx = cx; s.cy = cy
        s.k = ss * z

    def X(s, x): return ((x - s.cx) * s.z + W / 2) * s.ss
    def Y(s, y): return ((y - s.cy) * s.z + H / 2) * s.ss

    def _p(s, pts):
        out = []
        for i in range(0, len(pts), 2):
            out.append(s.X(pts[i])); out.append(s.Y(pts[i + 1]))
        return out

    def _w(s, w): return max(1, int(round(w * s.k)))

    def line(s, pts, fill, w):
        s.d.line(s._p(pts), fill=fill, width=s._w(w), joint="curve")
        r = s._w(w) / 2.0  # ujung membulat
        p = s._p(pts)
        for i in (0, len(p) - 2):
            s.d.ellipse([p[i] - r, p[i + 1] - r, p[i] + r, p[i + 1] + r], fill=fill)

    def ell(s, b, fill=None, out=None, w=0):
        p = s._p(b); s.d.ellipse(p, fill=fill, outline=out, width=s._w(w) if w else 0)

    def poly(s, pts, fill=None, out=None, w=0):
        p = s._p(pts)
        if fill is not None: s.d.polygon(p, fill=fill)
        if out: s.d.line(p + p[:2], fill=out, width=s._w(w), joint="curve")

    def rect(s, b, fill=None, out=None, w=0, r=0):
        p = s._p(b)
        if r: s.d.rounded_rectangle(p, radius=r * s.k, fill=fill, outline=out, width=s._w(w) if w else 0)
        else: s.d.rectangle(p, fill=fill, outline=out, width=s._w(w) if w else 0)

    def arc(s, b, a0, a1, fill, w): s.d.arc(s._p(b), a0, a1, fill=fill, width=s._w(w))
    def pie(s, b, a0, a1, fill): s.d.pieslice(s._p(b), a0, a1, fill=fill)


def layer(ss=2):
    return Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))


def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
