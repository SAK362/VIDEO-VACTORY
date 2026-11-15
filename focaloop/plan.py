"""Rencana implisit: nomor video -> seed. Deterministik, tidak perlu tabel seed."""
import bounce3 as b

START = 1000


def valid(p, seen):
    if max(p["counts"]) < 64 or len(p["counts"]) < 4: return None
    if p["sector"] < 150 and max(p["counts"]) < 256: return None
    key = (p["wall_style"], p["ball_style"], p["line_style"], p["bg_style"], p["palette"], p["scale"], p["instr"],
           p["mapping"], tuple(p["counts"]), round(p["sector"] / 60), round(p["c"] / p["A"], 1))
    return None if key in seen else key


def seed_for(no):
    seen, n, seed = set(), 0, START
    while True:
        seed += 1
        p = b.gen_params(seed)
        key = valid(p, seen)
        if key is None: continue
        seen.add(key); n += 1
        if n == no: return seed
