"""Rencana implisit: nomor video -> seed + tema. Deterministik, tanpa tabel. 5 tahun = 9125 video (5/hari).
Tema diacak per hari (tiap hari minimal 3 tema berbeda, tidak ada dua tema sama berurutan, termasuk antar-hari)."""
import random
START = 1000
PER_DAY = 5
YEARS = 5
TOTAL = 365 * YEARS * PER_DAY + 0   # 9125
THEMES = ["bounce", "curves", "escape"]
WEIGHTS = {"bounce": 0.40, "curves": 0.30, "escape": 0.30}  # ubah bobot di sini untuk atur proporsi tema


def seed_for(no):
    return START + int(no)


def _build():
    out, prev_last = [], None
    for day in range(TOTAL // PER_DAY + 1):
        r = random.Random(day * 7919 + 20261116)
        for _ in range(500):
            bag = r.choices(THEMES, [WEIGHTS[t] for t in THEMES], k=PER_DAY)
            if len(set(bag)) < 3 or max(bag.count(t) for t in THEMES) > 2:
                continue
            ok = all(bag[i] != bag[i + 1] for i in range(PER_DAY - 1)) and bag[0] != prev_last
            if ok:
                break
        out.extend(bag)
        prev_last = bag[-1]
    return out


_SCHEDULE = _build()


def theme_for(no):
    return _SCHEDULE[int(no) - 1]
