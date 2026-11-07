"""Merender video CurioSphere dari work/props.json.

Pemakaian:
  python -m studio.render meta  PROPS                 -> cetak jumlah frame
  python -m studio.render chunk PROPS i n OUT.mp4     -> render potongan ke-i dari n (video saja)
  python -m studio.render stills PROPS OUTDIR         -> satu gambar per adegan (uji cepat)
"""
import importlib
import json
import math
import os
import subprocess
import sys

from . import core

FPS = int(os.environ.get('STUDIO_FPS', '15'))
TAIL = 1.2


def tokenize(text):
    return [w for w in str(text or '').split() if w.strip('*')]


def clean(w):
    return w.replace('*', '')


class Timeline:
    def __init__(self, props):
        self.scenes = props.get('scenes') or []
        toks = []
        self.scene_tok = []
        for sc in self.scenes:
            t = tokenize(sc.get('narration') or sc.get('narration_ref') or '')
            self.scene_tok.append((len(toks), len(toks) + len(t)))
            toks += t
        self.toks = toks
        audio = float(props.get('audioSeconds') or 0) or max(5.0, len(toks) / 2.5)
        self.audio = audio
        wt = props.get('wordTimes')
        if isinstance(wt, list) and len(wt) == len(toks) and toks:
            self.start = [float(w[0]) for w in wt]
            self.mode = 'suara'
        else:
            lens = [len(clean(w)) + 1.5 for w in toks] or [1]
            tot = sum(lens)
            t = 0.25
            self.start = []
            for L in lens:
                self.start.append(t)
                t += (audio - 0.5) * L / tot
            self.mode = 'perkiraan'
        n = len(self.scenes)
        self.sstart = []
        for i, (a, b) in enumerate(self.scene_tok):
            if i == 0:
                self.sstart.append(0.0)
            elif a < len(self.start):
                self.sstart.append(max(self.sstart[-1] + 0.8, self.start[a] - 0.15))
            else:
                self.sstart.append(self.sstart[-1] + 3.0)
        self.total = max(audio, (self.sstart[-1] if n else 0) + 2.0) + TAIL
        self.phrases = []
        for i, (a, b) in enumerate(self.scene_tok):
            ph = []
            cur = []
            for j in range(a, b):
                cur.append(j)
                w = clean(toks[j])
                if len(cur) >= 5 or (w.endswith(('.', ',', '?', '!', ':', ';')) and len(cur) >= 2):
                    ph.append(cur)
                    cur = []
            if cur:
                if len(cur) < 2 and ph:
                    ph[-1] += cur
                else:
                    ph.append(cur)
            self.phrases.append(ph)

    def scene_at(self, now):
        i = 0
        for k, st in enumerate(self.sstart):
            if now >= st:
                i = k
        end = self.sstart[i + 1] if i + 1 < len(self.sstart) else self.total
        p = min(1.0, max(0.0, (now - self.sstart[i]) / max(0.1, end - self.sstart[i])))
        return i, p

    def subtitle_at(self, i, now):
        cur = None
        for ph in self.phrases[i]:
            if now >= self.start[ph[0]] - 0.12:
                cur = ph
        if cur is None:
            return [], -1, -1
        act = cur[0]
        for j in cur:
            if self.start[j] - 0.06 <= now:
                act = j
        words = [clean(self.toks[j]) for j in cur]
        return words, cur.index(act), cur.index(act)


def load_kit(name):
    name = (name or '').strip().lower()
    return importlib.import_module('studio.kits.' + name)


def draw_frame(kit, props, tl, now):
    lang = 'id' if str(props.get('lang', 'en')).lower().startswith('id') else 'en'
    i, p = tl.scene_at(now)
    sc = tl.scenes[i]
    shot = sc.get('shot')
    if shot not in kit.SHOTS:
        shot = kit.DEFAULT_SHOT
    sh = kit.SHOTS[shot]
    e = core.ease(p)
    if hasattr(kit, 'camera'):
        pos, look = kit.camera(shot, sh, now, p)
    else:
        a0, l0 = sh['cam']
        a1, l1 = sh.get('cam2', sh['cam'])
        pos = [a0[k] + (a1[k] - a0[k]) * e for k in range(3)]
        look = [l0[k] + (l1[k] - l0[k]) * e for k in range(3)]
    cb = core.cam_basis(pos, look)
    scene = kit.build(shot, sh, now, p)
    sky = sh.get('sky') or getattr(kit, 'SKY', ((196, 224, 242), (244, 240, 232)))
    img = core.render3d(scene, cb, sky[0], sky[1])
    if hasattr(kit, 'post'):
        kit.post(img, shot, sh, now, p, cb)
    labels = []
    for lab in (sh.get('labels') or {}).get(lang, []):
        txt, pt, side, col = lab
        pt = kit.resolve_point(pt, now, p) if hasattr(kit, 'resolve_point') else pt
        labels.append((txt, pt, side, core.ORANGE if col == 'o' else core.GREEN))
    tag = (sh.get('tag') or {}).get(lang)
    card = sc.get('card') if (sh.get('card') or sc.get('card')) else None
    if card and not isinstance(card, dict):
        card = None
    keys = sc.get('keywords') or [w.strip('*') for w in str(sc.get('heading', '')).split() if w.startswith('*')]
    core.overlay(img, sc.get('kicker') or sc.get('label') or '', sc.get('heading', ''), keys, labels, tag, card, cb)
    words, act, done = tl.subtitle_at(i, now)
    core.subtitle(img, words, act, done)
    core.brand(img, now)
    return img


def main():
    mode = sys.argv[1]
    props = json.load(open(sys.argv[2], encoding='utf-8'))
    width = int(os.environ.get('STUDIO_WIDTH', '720'))
    core.init(width)
    kit = load_kit(props.get('kit') or (props.get('world') or {}).get('archetype') or '')
    tl = Timeline(props)
    nframes = int(math.ceil(tl.total * FPS))
    if mode == 'meta':
        print(json.dumps({'frames': nframes, 'seconds': round(tl.total, 2), 'timing': tl.mode, 'scenes': len(tl.scenes), 'kit': kit.__name__}))
        return
    if mode == 'stills':
        out = sys.argv[3]
        os.makedirs(out, exist_ok=True)
        for i, st in enumerate(tl.sstart):
            end = tl.sstart[i + 1] if i + 1 < len(tl.sstart) else tl.total
            draw_frame(kit, props, tl, st + (end - st) * 0.6).save(os.path.join(out, 'adegan_%02d.png' % (i + 1)))
        print('timing', tl.mode)
        return
    ci, cn, outp = int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    a = nframes * ci // cn
    b = nframes * (ci + 1) // cn
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (core.W, core.H),
                           '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
                           '-pix_fmt', 'yuv420p', '-r', str(FPS), outp], stdin=subprocess.PIPE)
    for f in range(a, b):
        img = draw_frame(kit, props, tl, f / FPS)
        ff.stdin.write(img.convert('RGB').tobytes())
        if (f - a) % 30 == 0:
            print('frame %d/%d (potongan %d: %d-%d)' % (f, nframes, ci, a, b), flush=True)
    ff.stdin.close()
    if ff.wait() != 0:
        raise SystemExit('ffmpeg gagal')


if __name__ == '__main__':
    main()
