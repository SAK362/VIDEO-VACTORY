import {FPS} from './theme';
import type {Phrase, Scene, TimedScene, Token} from './types';

// Pecah teks menjadi kata; kata di antara tanda *bintang* ditandai sebagai penekanan.
// Tanda baca yang menempel langsung setelah kata bertanda (mis. "*Ternyata*,") ikut ke kata itu,
// bukan menjadi "kata" sendiri.
export function tokenize(raw: string): Token[] {
  const out: Token[] = [];
  let hi = false;
  let lastEndedWs = true;
  for (const part of String(raw || '').split(/(\*)/)) {
    if (part === '*') {
      hi = !hi;
      continue;
    }
    if (part.length === 0) continue;
    const pieces = part.split(/\s+/).filter(Boolean);
    if (pieces.length && out.length && !/^\s/.test(part) && !lastEndedWs) {
      out[out.length - 1].text += pieces.shift() as string;
    }
    for (const w of pieces) out.push({text: w, hi});
    lastEndedWs = /\s$/.test(part);
  }
  return out;
}

export const TAIL_SECONDS = 1.2;

export function totalFrames(audioSeconds: number): number {
  return Math.max(60, Math.round((Math.max(5, audioSeconds) + TAIL_SECONDS) * FPS));
}

function words(s: string): string[] {
  return String(s || '')
    .toLowerCase()
    .replace(/\*/g, '')
    .replace(/[^\p{L}\p{N}\s]/gu, ' ')
    .split(/\s+/)
    .filter(Boolean);
}

type Chunk = {tokens: Token[]; g0: number; sentence: number};

// wordTimes: [mulai, selesai] dalam detik untuk setiap kata naskah, berurutan (dari align.py).
// Bila tidak ada atau jumlahnya tidak cocok, waktu diperkirakan dari panjang kata (cara lama).
export function buildTiming(narration: string, scenes: Scene[], audioSeconds: number, wordTimes?: number[][]) {
  const total = Math.max(5, audioSeconds);
  const lead = 0.2;
  const span = total - lead;

  const sentences = String(narration || '')
    .replace(/\s+/g, ' ')
    .split(/(?<=[.!?…])\s+/)
    .filter((s) => s.trim().length > 0);
  if (sentences.length === 0) sentences.push(String(narration || ' '));

  const sentTokens = sentences.map((s) => tokenize(s));
  const offsets: number[] = [];
  let totalTokens = 0;
  for (const t of sentTokens) {
    offsets.push(totalTokens);
    totalTokens += t.length;
  }

  const real =
    Array.isArray(wordTimes) &&
    wordTimes.length === totalTokens &&
    totalTokens > 0 &&
    wordTimes.every((w) => Array.isArray(w) && Number.isFinite(w[0]) && Number.isFinite(w[1]));

  // Awal dan akhir tiap kalimat (detik).
  const sStart: number[] = [];
  const sEnd: number[] = [];
  if (real) {
    sentTokens.forEach((t, i) => {
      if (t.length === 0) {
        const prev = i > 0 ? sEnd[i - 1] : lead;
        sStart.push(prev);
        sEnd.push(prev);
        return;
      }
      sStart.push((wordTimes as number[][])[offsets[i]][0]);
      sEnd.push((wordTimes as number[][])[offsets[i] + t.length - 1][1]);
    });
  } else {
    const weights = sentTokens.map((t) => Math.max(1, t.length) + 0.6);
    const wsum = weights.reduce((a, b) => a + b, 0);
    let t = lead;
    for (const w of weights) {
      sStart.push(t);
      t += (span * w) / wsum;
      sEnd.push(t);
    }
  }

  // Frasa subtitle: maksimal 5 kata, memecah di koma bila sudah 2+ kata.
  const chunks: Chunk[] = [];
  sentTokens.forEach((toks, i) => {
    const parts: Token[][] = [];
    let cur: Token[] = [];
    for (const tk of toks) {
      cur.push(tk);
      const endsClause = /[,;:]$/.test(tk.text);
      if (cur.length >= 5 || (endsClause && cur.length >= 2)) {
        parts.push(cur);
        cur = [];
      }
    }
    if (cur.length) {
      if (cur.length < 2 && parts.length) parts[parts.length - 1].push(...cur);
      else parts.push(cur);
    }
    let g = offsets[i];
    for (const c of parts) {
      chunks.push({tokens: c, g0: g, sentence: i});
      g += c.length;
    }
  });

  const phrases: Phrase[] = [];
  if (real) {
    const wt = wordTimes as number[][];
    chunks.forEach((c, k) => {
      const first = wt[c.g0][0];
      const last = wt[c.g0 + c.tokens.length - 1][1];
      const nextStart = k + 1 < chunks.length ? wt[chunks[k + 1].g0][0] : Infinity;
      const endAt = Math.max(first + 0.2, Math.min(last + 0.35, nextStart));
      phrases.push({
        tokens: c.tokens,
        from: Math.round(first * FPS),
        to: Math.round(endAt * FPS),
        wordFrames: c.tokens.map((_, q) => Math.round(wt[c.g0 + q][0] * FPS)),
      });
    });
  } else {
    // Perkiraan: waktu kalimat dibagi per frasa sebanding panjang huruf, lalu per kata.
    const bySentence = new Map<number, Chunk[]>();
    for (const c of chunks) {
      const arr = bySentence.get(c.sentence) || [];
      arr.push(c);
      bySentence.set(c.sentence, arr);
    }
    bySentence.forEach((list, i) => {
      const lens = list.map((c) => c.tokens.reduce((a, k) => a + k.text.length + 1, 0));
      const lsum = lens.reduce((a, b) => a + b, 0);
      const dur = (sEnd[i] - sStart[i]) * 0.94;
      let tt = sStart[i];
      list.forEach((c, k) => {
        const d = (dur * lens[k]) / lsum;
        const wl = c.tokens.map((x) => x.text.length + 1.5);
        const wsum2 = wl.reduce((a, b) => a + b, 0);
        const wordFrames: number[] = [];
        let w = tt;
        for (let q = 0; q < c.tokens.length; q++) {
          wordFrames.push(Math.round(w * FPS));
          w += (d * wl[q]) / wsum2;
        }
        phrases.push({tokens: c.tokens, from: Math.round(tt * FPS), to: Math.round((tt + d) * FPS), wordFrames});
        tt += d;
      });
    });
  }

  // Batas adegan. Utama: tiap adegan mulai saat kalimat yang dirujuk narration_ref mulai diucapkan.
  const n = scenes.length;
  const sentWords = sentences.map((s) => new Set(words(s)));
  const matched: number[] = [];
  let ok = n > 0;
  let prevIdx = -1;
  for (let i = 0; i < n && ok; i++) {
    const ref = words(scenes[i].narration_ref || '');
    if (i === 0) {
      matched.push(0);
      prevIdx = 0;
      continue;
    }
    if (ref.length === 0) {
      ok = false;
      break;
    }
    let best = -1;
    let bestScore = 0;
    for (let s = Math.max(0, prevIdx + 1); s < sentences.length; s++) {
      let hit = 0;
      for (const w of ref) if (sentWords[s].has(w)) hit++;
      const score = hit / ref.length;
      if (score > bestScore + 1e-9) {
        bestScore = score;
        best = s;
      }
    }
    if (best < 0 || bestScore < 0.5) {
      ok = false;
      break;
    }
    matched.push(best);
    prevIdx = best;
  }

  const bounds: number[] = [0];
  let usedSentenceBounds = false;
  if (ok && n > 1) {
    const cand: number[] = [0];
    for (let i = 1; i < n; i++) cand.push(Math.max(0, sStart[matched[i]] - 0.12));
    let good = true;
    for (let i = 1; i < n; i++) if (cand[i] - cand[i - 1] < 1.2) good = false;
    if (cand[n - 1] > total - 0.8) good = false;
    if (good) {
      bounds.length = 0;
      bounds.push(...cand);
      usedSentenceBounds = true;
    }
  }
  if (!usedSentenceBounds) {
    // Cadangan: bagi rata, dekatkan ke awal kalimat bila selisihnya kecil.
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
  }
  bounds.push(total + TAIL_SECONDS);

  const timed: TimedScene[] = scenes.map((sc, i) => {
    const from = Math.round(bounds[i] * FPS);
    const to = Math.round(bounds[i + 1] * FPS);
    return {...sc, from, dur: Math.max(15, to - from)};
  });

  return {timed, phrases, mode: real ? 'suara' : 'perkiraan', sceneMode: usedSentenceBounds ? 'kalimat' : 'rata'};
}
