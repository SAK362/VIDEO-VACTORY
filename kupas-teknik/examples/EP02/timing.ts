import timeline from "./timeline.json";
import subs from "./subs.json";

export const FPS = 30;
export const END_CARD_DUR = 2.5;
const lastWordEnd = timeline.shots[timeline.shots.length - 1].end;
export const END_CARD_START = lastWordEnd + 0.15;
export const TOTAL_SEC = END_CARD_START + END_CARD_DUR;
export const TOTAL_FRAMES = Math.ceil(TOTAL_SEC * FPS);

export type ShotId = "S01" | "S02" | "S03" | "S04" | "S05" | "S06" | "S07" | "S08";
export type Span = { id: ShotId; t0: number; t1: number };

// visual shot spans: each shot starts mid-gap before its VO and runs to the next shot's start
export const SHOTS: Span[] = timeline.shots.map((s, i) => {
  const prevEnd = i === 0 ? 0 : timeline.shots[i - 1].end;
  const t0 = i === 0 ? 0 : (prevEnd + s.start) / 2;
  const next = timeline.shots[i + 1];
  const t1 = next ? (s.end + next.start) / 2 : TOTAL_SEC;
  return { id: s.id as ShotId, t0, t1 };
});

export function shotAt(t: number): Span & { u: number; lt: number } {
  const s = SHOTS.find((x) => t >= x.t0 && t < x.t1) ?? SHOTS[SHOTS.length - 1];
  return { ...s, u: Math.min(1, Math.max(0, (t - s.t0) / (s.t1 - s.t0))), lt: t - s.t0 };
}

export type SubWord = { t: string; s: number; e: number };
export type SubChunk = { start: number; end: number; shot: string; lines: SubWord[][] };
export const SUBS = subs as SubChunk[];

// time (seconds) when a phrase is first spoken in the subtitles (used to sync animation beats)
export function phraseTime(needle: string, fallback: number): number {
  for (const c of SUBS) for (const l of c.lines) for (const w of l) if (w.t.toLowerCase().includes(needle.toLowerCase())) return w.s;
  return fallback;
}

export const smooth = (x: number) => { const c = Math.min(1, Math.max(0, x)); return c * c * (3 - 2 * c); };
export const ramp = (t: number, a: number, b: number) => smooth((t - a) / (b - a));
export const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
