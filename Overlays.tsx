import React from 'react';
import {interpolate, spring} from 'remotion';
import {C, FONT, FPS} from './theme';
import {tokenize} from './timing';
import type {Callout, DataCard, Phrase, Token} from './types';

const Tokens: React.FC<{tokens: Token[]; color?: string; hiColor?: string}> = ({tokens, color = C.ivory, hiColor = C.gold}) => (
  <>
    {tokens.map((tk, i) => (
      <span key={i} style={{color: tk.hi ? hiColor : color}}>
        {tk.text}
        {i < tokens.length - 1 ? ' ' : ''}
      </span>
    ))}
  </>
);

export const LabelBlock: React.FC<{label?: string; heading?: string; localFrame: number}> = ({label, heading, localFrame}) => {
  if (!label && !heading) return null;
  const k = spring({frame: localFrame, fps: FPS, config: {damping: 200}});
  return (
    <div
      style={{
        position: 'absolute',
        left: 60,
        right: 60,
        top: 170,
        opacity: k,
        transform: `translateY(${interpolate(k, [0, 1], [30, 0])}px)`,
        fontFamily: FONT,
      }}
    >
      {label ? (
        <div style={{color: C.cyan, fontSize: 26, fontWeight: 800, letterSpacing: '0.18em', textTransform: 'uppercase', textShadow: '0 3px 12px rgba(11,31,58,0.9)'}}>
          {label}
        </div>
      ) : null}
      {heading ? (
        <div style={{color: C.ivory, fontSize: 54, fontWeight: 800, lineHeight: 1.1, marginTop: 6, textShadow: '0 4px 0 rgba(11,31,58,0.9), 0 0 24px rgba(11,31,58,0.9)'}}>
          <Tokens tokens={tokenize(heading)} />
        </div>
      ) : null}
    </div>
  );
};

export const Callouts: React.FC<{callouts?: Callout[]; localFrame: number}> = ({callouts, localFrame}) => {
  if (!callouts || callouts.length === 0) return null;
  return (
    <>
      {callouts.slice(0, 3).map((c, i) => {
        const k = spring({frame: localFrame - (12 + i * 9), fps: FPS, config: {damping: 16}});
        const left = i % 2 === 0;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: 470 + i * 150,
              [left ? 'left' : 'right']: 40,
              maxWidth: 400,
              padding: '10px 20px',
              borderRadius: 20,
              background: 'rgba(11,31,58,0.86)',
              border: `2px solid ${C.cyan}`,
              boxShadow: `0 0 16px rgba(34,195,240,0.4)`,
              color: C.ivory,
              fontFamily: FONT,
              fontWeight: 800,
              fontSize: 28,
              opacity: k,
              transform: `translateX(${interpolate(k, [0, 1], [left ? -60 : 60, 0])}px) scale(${interpolate(k, [0, 1], [0.9, 1])})`,
            }}
          >
            <span style={{color: C.gold}}>● </span>
            {c.text}
            <svg width="100" height="14" style={{position: 'absolute', top: '50%', [left ? 'left' : 'right']: '100%', marginTop: -7, overflow: 'visible'}}>
              <line x1={left ? 0 : 100} y1="7" x2={left ? 100 * k : 100 - 100 * k} y2="7" stroke={C.cyan} strokeWidth="4" strokeLinecap="round" />
              <circle cx={left ? 100 * k : 100 - 100 * k} cy="7" r="7" fill={C.gold} stroke={C.navy} strokeWidth="3" />
            </svg>
          </div>
        );
      })}
    </>
  );
};

export const DataCardView: React.FC<{card?: DataCard; localFrame: number}> = ({card, localFrame}) => {
  if (!card) return null;
  const k = spring({frame: localFrame - 6, fps: FPS, config: {damping: 14}});
  return (
    <div
      style={{
        position: 'absolute',
        left: 200,
        right: 200,
        top: 470,
        padding: '22px 22px',
        borderRadius: 28,
        background: 'rgba(11,31,58,0.9)',
        border: `4px solid ${C.cyan}`,
        boxShadow: '0 0 50px rgba(34,195,240,0.5)',
        textAlign: 'center',
        fontFamily: FONT,
        opacity: Math.min(1, k * 1.5),
        transform: `scale(${interpolate(k, [0, 1], [0.7, 1])})`,
      }}
    >
      <div style={{color: C.gold, fontSize: 92, fontWeight: 800, lineHeight: 1}}>{card.value}</div>
      <div style={{color: C.ivory, fontSize: 30, fontWeight: 700, marginTop: 10}}>{card.caption}</div>
    </div>
  );
};

export const DangerOverlay: React.FC<{frame: number}> = ({frame}) => (
  <div
    style={{
      position: 'absolute',
      inset: 0,
      background: 'radial-gradient(ellipse at center, rgba(229,72,77,0) 45%, rgba(229,72,77,0.5) 100%)',
      opacity: 0.55 + 0.35 * Math.sin((frame / FPS) * 8),
    }}
  />
);

const HATCH = `repeating-linear-gradient(135deg, ${C.gold} 0px, ${C.gold} 7px, #C98A00 7px, #C98A00 10px)`;

// Subtitle: kata yang sedang diucapkan diberi blok emas berarsir; kata yang sudah lewat putih, yang belum redup.
export const Subtitles: React.FC<{phrases: Phrase[]; frame: number}> = ({phrases, frame}) => {
  const ph = phrases.find((x) => frame >= x.from && frame < x.to + 2);
  if (!ph) return null;
  const k = spring({frame: frame - ph.from, fps: FPS, config: {damping: 18, stiffness: 220}});
  let cur = 0;
  for (let i = 0; i < ph.wordFrames.length; i++) if (frame >= ph.wordFrames[i]) cur = i;
  return (
    <div style={{position: 'absolute', left: 70, right: 70, top: 1380, height: 170, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
      <div
        style={{
          padding: '10px 18px',
          borderRadius: 24,
          background: 'rgba(8,24,46,0.72)',
          border: '2px solid rgba(34,195,240,0.35)',
          fontFamily: FONT,
          fontWeight: 800,
          fontSize: 46,
          lineHeight: 1.2,
          textAlign: 'center',
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: '2px 6px',
          transform: `scale(${interpolate(k, [0, 1], [0.93, 1])})`,
        }}
      >
        {ph.tokens.map((tk, i) => {
          const active = i === cur;
          const past = i < cur;
          return (
            <span
              key={i}
              style={{
                padding: '0 10px',
                borderRadius: 10,
                background: active ? HATCH : 'transparent',
                color: active ? C.navy : past ? (tk.hi ? C.gold : C.ivory) : tk.hi ? 'rgba(245,182,35,0.55)' : 'rgba(247,243,234,0.5)',
                textShadow: active ? 'none' : '0 3px 0 rgba(8,24,46,0.9)',
                boxShadow: active ? '0 0 0 2px #7A4E00, 0 4px 0 rgba(0,0,0,0.35)' : 'none',
                transform: active ? 'scale(1.06)' : 'none',
              }}
            >
              {tk.text}
            </span>
          );
        })}
      </div>
    </div>
  );
};

export const Watermark: React.FC = () => (
  <div
    style={{
      position: 'absolute',
      right: 40,
      top: 1760,
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      opacity: 0.8,
      fontFamily: FONT,
      fontWeight: 800,
      fontSize: 24,
      color: C.ivory,
    }}
  >
    <svg width="30" height="30" viewBox="0 0 44 44">
      <circle cx="20" cy="20" r="14" fill="none" stroke={C.cyan} strokeWidth="4" />
      <path d="M6 20 H34 M20 6 Q28 20 20 34 Q12 20 20 6" fill="none" stroke={C.cyan} strokeWidth="2.5" />
      <line x1="30" y1="30" x2="40" y2="40" stroke={C.gold} strokeWidth="5" strokeLinecap="round" />
    </svg>
    CurioSphere
  </div>
);

export const SceneFade: React.FC<{localFrame: number; first: boolean}> = ({localFrame, first}) => {
  if (first) return null;
  const o = interpolate(localFrame, [0, 7], [0.75, 0], {extrapolateRight: 'clamp'});
  return <div style={{position: 'absolute', inset: 0, background: C.navy, opacity: o}} />;
};
