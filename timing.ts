import {FPS} from './theme';
import type {Phrase, Scene, TimedScene, Token} from './types';

// Pecah teks menjadi kata; kata di antara tanda *bintang* ditandai sebagai penekanan.
export function tokenize(raw: string): Token[] {
  const out: Token[] = [];
  let hi = false;
  for (const part of String(raw || '').split(/(\*)/)) {
    if (part === '*') {
      hi = !hi;
      continue;
    }
    for (const w of part.split(/\s+/).filter(Boolean)) out.push({text: w, hi});
  }
  return out;
}

export const TAIL_SECONDS = 1.2;

export function totalFrames(audioSeconds: number): number {
  return Math.max(60, Math.round((Math.max(5, audioSeconds) + TAIL_SECONDS) * FPS));
}

// Tanpa timestamp kata dari TTS, waktu dibagi sebanding jumlah kata per kalimat.
export function buildTiming(narration: string, scenes: Scene[], audioSeconds: number) {
  const total = Math.max(5, audioSeconds);
  const lead = 0.2;
  const span = total - lead;

  const sentences = String(narration || '')
    .replace(/\s+/g, ' ')
    .split(/(?<=[.!?…])\s+/)
    .filter((s) => s.trim().length > 0);
  if (sentences.length === 0) sentences.push(String(narration || ' '));

  const weights = sentences.map((s) => Math.max(1, tokenize(s).length) + 0.6);
  const wsum = weights.reduce((a, b) => a + b, 0);
  const sStart: number[] = [];
  const sEnd: number[] = [];
  let t = lead;
  for (const w of weights) {
    sStart.push(t);
    t += (span * w) / wsum;
    sEnd.push(t);
  }

  // Frasa subtitle: maksimal 5 kata, memecah di koma bila sudah 2+ kata.
  const phrases: Phrase[] = [];
  sentences.forEach((s, i) => {
    const toks = tokenize(s);
    const chunks: Token[][] = [];
    let cur: Token[] = [];
    for (const tk of toks) {
      cur.push(tk);
      const endsClause = /[,;:]$/.test(tk.text);
      if (cur.length >= 5 || (endsClause && cur.length >= 2)) {
        chunks.push(cur);
        cur = [];
      }
    }
    if (cur.length) {
      if (cur.length < 2 && chunks.length) chunks[chunks.length - 1].push(...cur);
      else chunks.push(cur);
    }
    if (chunks.length === 0) return;
    const lens = chunks.map((c) => c.reduce((a, k) => a + k.text.length + 1, 0));
    const lsum = lens.reduce((a, b) => a + b, 0);
    const dur = (sEnd[i] - sStart[i]) * 0.94;
    let tt = sStart[i];
    chunks.forEach((c, k) => {
      const d = (dur * lens[k]) / lsum;
      // Waktu tiap kata dibagi sebanding panjang hurufnya (kata panjang = lebih lama diucapkan).
      const wl = c.map((x) => x.text.length + 1.5);
      const wsum2 = wl.reduce((a, b) => a + b, 0);
      const wordFrames: number[] = [];
      let wt = tt;
      for (let q = 0; q < c.length; q++) {
        wordFrames.push(Math.round(wt * FPS));
        wt += (d * wl[q]) / wsum2;
      }
      phrases.push({tokens: c, from: Math.round(tt * FPS), to: Math.round((tt + d) * FPS), wordFrames});
      tt += d;
    });
  });

  // Batas adegan: dekatkan ke awal kalimat bila selisihnya kecil, selain itu bagi rata.
  const n = scenes.length;
  const bounds: number[] = [0];
  for (let i = 1; i < n; i++) {
    const target = lead + (span * i) / n;
    let best = target;
    let bd = Infinity;
    for (const ss of sStart) {
      const d = Math.abs(ss - target);
      if (d < bd) {
        bd = d;
        best = ss;
      }
    }
    if (bd > (span / n) * 0.45) best = target;
    const prev = bounds[i - 1];
    const maxAllowed = total - (n - i) * 1.0;
    if (best < prev + 1.8) best = Math.min(prev + 1.8, maxAllowed);
    bounds.push(best);
  }
  bounds.push(total + TAIL_SECONDS);

  const timed: TimedScene[] = scenes.map((sc, i) => {
    const from = Math.round(bounds[i] * FPS);
    const to = Math.round(bounds[i + 1] * FPS);
    return {...sc, from, dur: Math.max(15, to - from)};
  });

  return {timed, phrases};
}
