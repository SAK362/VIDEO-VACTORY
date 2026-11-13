"""Periksa spec NUSAKARA (work/props.json). Melengkapi 'narration' dari 'teks' bila kosong. Keluar 1 hanya pada kesalahan struktur;
kunci komponen tak dikenal hanya WARN (adegan tetap dirender dengan komponen pengganti/dilewati)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_char as C
import lib_props as P

path = sys.argv[1] if len(sys.argv) > 1 else "work/props.json"
s = json.load(open(path, encoding="utf-8")); err = []; warn = []
sc = s.get("scenes")
if not isinstance(sc, list) or not sc: err.append("scenes kosong")
else:
    for i, x in enumerate(sc, 1):
        if not (x.get("narration") or x.get("teks")): err.append("scene %d tanpa teks/narration" % i)
        x["narration"] = x.get("narration") or x.get("teks")
        if x.get("id") != i: warn.append("scene %d: id tidak berurutan (%r)" % (i, x.get("id")))
        if x.get("latar") not in P.LATAR: warn.append("scene %d: latar '%s' tak dikenal" % (i, x.get("latar")))
        for k in x.get("properti", []):
            if k not in P.PROPS: warn.append("scene %d: properti '%s' tak dikenal" % (i, k))
        for k in x.get("efek", []):
            if k not in P.FX: warn.append("scene %d: efek '%s' tak dikenal" % (i, k))
        for t in x.get("tokoh", []):
            if t.get("kunci") not in C.OUTFIT: warn.append("scene %d: tokoh '%s' tak dikenal" % (i, t.get("kunci")))
            if t.get("pose") not in C.POSES: warn.append("scene %d: pose '%s' tak dikenal (pakai 'berdiri')" % (i, t.get("pose")))
    words = sum(len(x["narration"].split()) for x in sc)
    print("scene: %d, kata: %d (target 380-420 untuk 2 menit)" % (len(sc), words))
    if len(sc) > 40: err.append("terlalu banyak scene (>40)")
for w in warn: print("WARN", w)
for e in err: print("ERROR", e)
if err: sys.exit(1)
json.dump(s, open(path, "w", encoding="utf-8"), ensure_ascii=False)
print("spec OK")
