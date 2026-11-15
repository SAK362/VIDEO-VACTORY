"""Rencana implisit: nomor video -> seed. Deterministik, tanpa tabel. 3 tahun = 5475 video (5/hari)."""
START = 1000
TOTAL = 5475


def seed_for(no):
    return START + int(no)
