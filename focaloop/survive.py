"""Tema SURVIVE (tali): tiap bola mulai 10 tali; tali TETAP (arahnya tidak mengikuti bola); memantul di dinding = +1 tali;
bola yang menyentuh tali lawan memotongnya: pemotong dapat tali sebanyak yang terpotong, lawan kehilangannya.
Tali habis = gugur. Batas waktu T: tali terbanyak menang. Semua parameter dari seed."""
import random
from fx import *

CX, CY = 360, 650
BR = 17
START_ROPES = 10
COL = {"RED": (255, 61, 110), "GREEN": (46, 230, 166), "BLUE": (74, 163, 255), "PURPLE": (150, 100, 250),
       "ORANGE": (255, 166, 61), "YELLOW": (255, 225, 74), "PINK": (255, 122, 217), "CYAN": (61, 230, 255)}
SHAPES = [("circle", 0, 300, 30), ("square", 4, 396, 16), ("hexagon", 6, 330, 16), ("triangle", 3, 380, 10),
          ("ellipse", -1, 0, 12), ("octagon", 8, 320, 10), ("pentagon", 5, 330, 6)]
SUB = ["Bounce = +1 rope. Cut = steal.", "Cut their ropes to win.", "Ropes are your lives.", "Steal ropes. Survive."]


def arena_poly(sh, sides, circ):
    if sh == "circle":
        a = np.linspace(0, 2 * np.pi, 160, endpoint=False)
        return np.stack([300 * np.cos(a), 300 * np.sin(a)], 1)
    if sh == "ellipse":
        a = np.linspace(0, 2 * np.pi, 200, endpoint=False)
        return np.stack([255 * np.cos(a), 345 * np.sin(a)], 1)
    if sh == "square":
        return regular_polygon(4, circ, -math.pi / 4)
    return regular_polygon(sides, circ)


def gen_params(seed):
    r = random.Random(seed * 999983 + 5)
    sh = r.choices(SHAPES, [s[3] for s in SHAPES])[0]
    N = r.choices([2, 3, 4, 5], [50, 25, 15, 10])[0]
    colors = r.sample(list(COL), N)
    titles = ["WHICH COLOR WINS?", "LAST ONE STANDING", "CUT THE ROPES. SURVIVE.", "WHO KEEPS THE MOST ROPES?"]
    if N == 2:
        titles += ["ROPE DUEL: WHO WINS?", f"{colors[0]} VS {colors[1]}"]
    else:
        titles += [f"{N} COLORS. 1 WINNER.", f"{N} BALLS. ONLY 1 SURVIVES."]
    return dict(seed=seed, shape=sh[0], sides=sh[1], circ=sh[2], N=N, colors=colors, speed=r.uniform(140, 195) - (N - 2) * 10,
                T=r.choice([26, 28, 30, 32, 34, 36]), title=r.choice(titles), sub=r.choice(SUB),
                base=r.choice([246.94, 261.63, 277.18, 293.66, 329.63]), pad=r.choice([[110, 165, 220.5], [98, 147, 196]]))


def cast(p, angs, n, d):
    dirs = np.stack([np.cos(angs), np.sin(angs)], 1)
    nd = dirs @ n.T
    num = d - n @ p
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where(nd > 1e-9, num[None, :] / nd, np.inf)
    return dirs, t.min(1)


def add_rope(angs, rng):
    if len(angs) == 0:
        return [rng.uniform(0, 2 * np.pi)]
    a = np.sort(np.array(angs) % (2 * np.pi))
    gaps = np.diff(np.append(a, a[0] + 2 * np.pi))
    i = int(np.argmax(gaps))
    return list(angs) + [a[i] + gaps[i] / 2]


def sim(p, seed):
    rng = np.random.default_rng(seed)
    P = arena_poly(p["shape"], p["sides"], p["circ"])
    n, d = poly_edges(P)
    N = p["N"]
    a0 = rng.uniform(0, 2 * np.pi)
    pos = np.array([[130 * math.cos(a0 + 2 * math.pi * i / N), 130 * math.sin(a0 + 2 * math.pi * i / N)] for i in range(N)])
    va = rng.uniform(0, 2 * np.pi, N)
    vel = np.stack([np.cos(va), np.sin(va)], 1) * p["speed"]
    ropes = [list(rng.uniform(0, 2 * np.pi) + 2 * np.pi * np.arange(START_ROPES) / START_ROPES) for _ in range(N)]
    alive = np.ones(N, bool)
    dt = 1 / FPS
    frames, events = [], []
    death_t = [None] * N
    t, over_t = 0.0, None
    while True:
        gain = {}
        if over_t is None:
            for _ in range(4):
                h = dt / 4
                pos += vel * h
                for i in range(N):
                    if not alive[i]:
                        continue
                    for _ in range(2):
                        dist = d - n @ pos[i]
                        k = int(np.argmin(dist))
                        if dist[k] < BR:
                            pos[i] -= n[k] * (BR - dist[k])
                            if vel[i] @ n[k] > 0:
                                vel[i] -= 2 * (vel[i] @ n[k]) * n[k]
                                ropes[i] = add_rope(ropes[i], rng)
                                events.append((t, "bounce", i, len(ropes[i])))
                for i in range(N):
                    for j in range(i + 1, N):
                        if alive[i] and alive[j]:
                            dv = pos[j] - pos[i]
                            dd = np.linalg.norm(dv)
                            if 0 < dd < 2 * BR:
                                nn = dv / dd
                                ov = 2 * BR - dd
                                pos[i] -= nn * ov / 2
                                pos[j] += nn * ov / 2
                                rel = (vel[i] - vel[j]) @ nn
                                if rel > 0:
                                    vel[i] -= rel * nn
                                    vel[j] += rel * nn
                for o in range(N):
                    if not alive[o]:
                        continue
                    for e in range(N):
                        if e == o or not alive[e] or not ropes[o]:
                            continue
                        angs = np.array(ropes[o])
                        dirs, tt = cast(pos[o], angs, n, d)
                        pr = np.clip((pos[e] - pos[o]) @ dirs.T, 0, tt)
                        cp = pos[o] + dirs * pr[:, None]
                        hit = np.linalg.norm(pos[e] - cp, axis=1) < BR + 1
                        if hit.any():
                            k = int(hit.sum())
                            first = cp[np.argmax(hit)]
                            ropes[o] = [a for a, hh in zip(ropes[o], hit) if not hh]
                            for _ in range(k):
                                ropes[e] = add_rope(ropes[e], rng)
                            events.append((t, "cut", o, e, k, first[0], first[1]))
                            g = gain.setdefault(e, [0, first[0], first[1]])
                            g[0] += k
                            if not ropes[o]:
                                alive[o] = False
                                death_t[o] = t
                                events.append((t, "death", o))
                if alive.sum() <= 1:
                    over_t = t
                    if alive.sum() == 1:
                        events.append((t, "win", int(np.where(alive)[0][0])))
                    break
        if over_t is None and t >= p["T"]:
            cn = np.array([len(r_) if alive[i] else -1 for i, r_ in enumerate(ropes)])
            top = np.where(cn == cn.max())[0]
            if len(top) == 1:
                over_t = t
                w = int(top[0])
                events.append((t, "timeup", w))
                for i in range(N):
                    if alive[i] and i != w:
                        alive[i] = False
                        death_t[i] = t
                        events.append((t, "death", i))
                events.append((t, "win", w))
        ends = [None] * N
        for i in range(N):
            if alive[i] and ropes[i]:
                dirs, tt = cast(pos[i], np.array(ropes[i]), n, d)
                ends[i] = pos[i] + dirs * tt[:, None]
        frames.append(dict(t=t, pos=pos.copy(), cnt=[len(r_) for r_ in ropes], alive=alive.copy(), ends=ends, gain=dict(gain)))
        t += dt
        if over_t is not None and t > over_t + 2.8:
            break
        if t > p["T"] + 60:
            return None
    if alive.sum() != 1:
        return None
    return dict(frames=frames, events=events, death_t=death_t, over_t=over_t, winner=int(np.where(alive)[0][0]), P=P)


def best_sim(p, tries=8):
    best = None
    for i in range(tries):
        s = p["seed"] * 31 + i
        S = sim(p, s)
        if not S:
            continue
        fi = min(len(S["frames"]) - 1, int(S["over_t"] * FPS))
        c = sorted(S["frames"][fi]["cnt"] if S["frames"][fi]["alive"].sum() > 1 else [S["frames"][fi - 1]["cnt"][S["winner"]], 0])
        c2 = sorted(S["frames"][max(0, fi - 1)]["cnt"])
        gap = c2[-1] - c2[-2]
        lead = [int(np.argmax(f["cnt"])) for f in S["frames"][::15]]
        flips = sum(1 for a, b in zip(lead, lead[1:]) if a != b)
        score = min(gap, 8) + min(flips, 4) * 1.5
        if best is None or score > best[0]:
            best = (score, S)
    if best is None:
        raise RuntimeError("survive: no valid sim")
    return best[1]


def render_frame(p, S, fi):
    fr = S["frames"][fi]
    t = fr["t"]
    N = p["N"]
    cols = [COL[c] for c in p["colors"]]
    img = np.empty((H, W, 3), np.uint8)
    img[:] = (8, 5, 5)
    glow = np.zeros_like(img)
    off = np.array([CX, CY])
    Pp = (S["P"] + off).astype(np.int32)
    over = t >= S["over_t"]
    for i in range(N):
        if fr["ends"][i] is None or len(fr["ends"][i]) == 0:
            continue
        c = bgr(cols[i])
        pc = fr["pos"][i] + off
        for q in fr["ends"][i] + off:
            a = (int(pc[0] * 16), int(pc[1] * 16))
            b = (int(q[0] * 16), int(q[1] * 16))
            cv2.line(glow, a, b, scale(c, 0.45), 3, cv2.LINE_AA, 4)
            cv2.line(img, a, b, scale(c, 0.85), 1, cv2.LINE_AA, 4)
            cv2.circle(img, (int(q[0]), int(q[1])), 2, c, -1, cv2.LINE_AA)
    cv2.polylines(img, [Pp], True, (225, 225, 235), 2, cv2.LINE_AA)
    cv2.polylines(glow, [Pp], True, (60, 60, 70), 4, cv2.LINE_AA)
    for ev in S["events"]:
        tau = t - ev[0]
        if ev[1] == "cut" and 0 <= tau < 0.4:
            f = 1 - tau / 0.4
            c = bgr(cols[ev[3]])
            for q in range(8):
                a = q * 2 * np.pi / 8 + ev[2]
                r = 6 + 34 * tau / 0.4
                cv2.circle(glow, (int(ev[5] + CX + r * math.cos(a)), int(ev[6] + CY + r * math.sin(a))), 3, scale(c, f), -1, cv2.LINE_AA)
        elif ev[1] == "death" and 0 <= tau < 0.7:
            f = 1 - tau / 0.7
            c = bgr(cols[ev[2]])
            p0 = S["frames"][min(len(S["frames"]) - 1, int(ev[0] * FPS))]["pos"][ev[2]] + off
            for k in range(16):
                a = 2 * np.pi * k / 16 + ev[2]
                r_ = 70 * (1 - math.exp(-5 * tau))
                cv2.circle(glow, (int(p0[0] + r_ * math.cos(a)), int(p0[1] + r_ * math.sin(a))), max(1, int(5 * f)), scale(c, f), -1, cv2.LINE_AA)
    items = []
    for i in range(N):
        if not fr["alive"][i]:
            continue
        c = bgr(cols[i])
        pc = fr["pos"][i] + off
        r = BR + (int(10 * min(1, (t - S["over_t"]) / 0.6)) if over and i == S["winner"] else 0)
        cv2.circle(glow, (int(pc[0]), int(pc[1])), r + 4, scale(c, 0.6), -1, cv2.LINE_AA)
        cv2.circle(img, (int(pc[0]), int(pc[1])), r, c, -1, cv2.LINE_AA)
        cv2.circle(img, (int(pc[0]), int(pc[1])), r, (255, 255, 255), 1, cv2.LINE_AA)
        items.append((str(fr["cnt"][i]), pc[0], pc[1] + 1, 19 if r == BR else 26, (20, 14, 20), 60))
    for j in range(max(0, fi - 18), fi + 1):
        for e, (k, x, y) in S["frames"][j]["gain"].items():
            tau = (fi - j) / FPS
            if tau < 0.6 and fr["alive"][e]:
                f = 1 - tau / 0.6
                pe = fr["pos"][e] + off
                items.append((f"+{k}", pe[0], pe[1] - 34 - 30 * tau, 24, scale(cols[e], 0.4 + 0.6 * f), 80))
    out = bloom(img, glow)
    txt = [watermark_item(), (p["title"], 360, 120, 38, (255, 255, 255), 660), (p["sub"], 360, 172, 24, (170, 170, 185), 660)]
    if not over:
        rem = max(0, math.ceil(p["T"] - t))
        txt.append((f"0:{rem:02d}", 360, 228, 34, (255, 255, 255) if rem > 5 else (255, 120, 120), 200))
    else:
        ko = S["events"] and any(e[1] == "timeup" for e in S["events"])
        txt.append(("TIME'S UP" if ko else "KNOCKOUT", 360, 228, 34, (255, 220, 120), 300))
    for i in range(N):
        x = 360 + (i - (N - 1) / 2) * (640 / max(N, 2) if N > 2 else 260)
        txt.append((f"{p['colors'][i]} {fr['cnt'][i]}", x, 1010, 28, cols[i] if fr["alive"][i] else (70, 70, 80), 110 if N > 3 else 200))
    if over:
        k = min(1, (t - S["over_t"]) / 0.5)
        txt.append((p["colors"][S["winner"]] + " WINS!", 360, 1075, 54, scale(cols[S["winner"]], 0.25 + 0.75 * k), 660))
    return draw_text(out, txt + items)


def audio(p, S):
    dur = S["frames"][-1]["t"] + 1 / FPS
    buf = np.zeros(int(dur * SR) + SR // 2)
    add_pad(buf, p["pad"], 0.05)
    base = p["base"]
    for ev in S["events"]:
        t = ev[0]
        if ev[1] == "bounce":
            add_tone(buf, t, pnote(ev[2] * 2 + (ev[3] % 5), base / 2), 0.5, 0.16, 0.15)
        elif ev[1] == "cut":
            for q in range(min(ev[4], 3)):
                add_tone(buf, t + 0.05 * q, pnote(5 + 2 * ev[3] + q * 2, base), 0.8, 0.22, 0.3)
        elif ev[1] == "death":
            add_tone(buf, t, 520, 0.7, 0.28, 0.25, glide=0.35)
            add_noise(buf, t, 0.5, 0.25, 0.12, seed=int(t * 1000) % 99)
        elif ev[1] == "win":
            for k, dg in enumerate([0, 2, 4, 7, 9, 12]):
                add_tone(buf, t + 0.18 * k, pnote(dg + 5, base), 1.4, 0.2, 0.55)
            add_tone(buf, t, base / 2, 2.4, 0.22, 0.9)
    return buf


def make(seed, base):
    p = gen_params(seed)
    S = best_sim(p)
    out = base + ".mp4"
    w = Writer(out)
    for fi in range(len(S["frames"])):
        w.write(render_frame(p, S, fi))
    w.close()
    finish(w, audio(p, S), out)
    q = p["title"] if p["title"].endswith("?") else "Which color wins?"
    return dict(kind="survive", question=q.capitalize() if q.isupper() else q, palette="/".join(p["colors"]), scale="pentatonic",
                instr="soft pluck", mapping="rope duel", ball_style="glow ball", bg_style="black", counts=[p["N"]],
                counts_text=f"{p['N']} colored balls fighting over ropes, winner: {p['colors'][S['winner']]}",
                duration=round(S["frames"][-1]["t"], 1), shape=p["shape"], thumb_t=round(max(1.0, S["over_t"] * 0.62), 2),
                points=[], kinds=["survive"])
