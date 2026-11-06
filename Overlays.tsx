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
        left: 70,
        right: 70,
        top: 210,
        opacity: k,
        transform: `translateY(${interpolate(k, [0, 1], [30, 0])}px)`,
        fontFamily: FONT,
      }}
    >
      {label ? (
        <div style={{color: C.cyan, fontSize: 36, fontWeight: 800, letterSpacing: '0.18em', textTransform: 'uppercase', textShadow: '0 3px 12px rgba(11,31,58,0.9)'}}>
          {label}
        </div>
      ) : null}
      {heading ? (
        <div style={{color: C.ivory, fontSize: 80, fontWeight: 800, lineHeight: 1.08, marginTop: 10, textShadow: '0 4px 0 rgba(11,31,58,0.9), 0 0 24px rgba(11,31,58,0.9)'}}>
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
              top: 600 + i * 190,
              [left ? 'left' : 'right']: 50,
              maxWidth: 520,
              padding: '16px 28px',
              borderRadius: 26,
              background: 'rgba(11,31,58,0.86)',
              border: `3px solid ${C.cyan}`,
              boxShadow: `0 0 24px rgba(34,195,240,0.45)`,
              color: C.ivory,
              fontFamily: FONT,
              fontWeight: 800,
              fontSize: 42,
              opacity: k,
              transform: `translateX(${interpolate(k, [0, 1], [left ? -60 : 60, 0])}px) scale(${interpolate(k, [0, 1], [0.9, 1])})`,
            }}
          >
            <span style={{color: C.gold}}>● </span>
            {c.text}
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
        left: 130,
        right: 130,
        top: 640,
        padding: '36px 30px',
        borderRadius: 40,
        background: 'rgba(11,31,58,0.9)',
        border: `4px solid ${C.cyan}`,
        boxShadow: '0 0 50px rgba(34,195,240,0.5)',
        textAlign: 'center',
        fontFamily: FONT,
        opacity: Math.min(1, k * 1.5),
        transform: `scale(${interpolate(k, [0, 1], [0.7, 1])})`,
      }}
    >
      <div style={{color: C.gold, fontSize: 150, fontWeight: 800, lineHeight: 1}}>{card.value}</div>
      <div style={{color: C.ivory, fontSize: 48, fontWeight: 700, marginTop: 14}}>{card.caption}</div>
    </div>
  );
};

export const ScanOverlay: React.FC<{p: number; lang: string}> = ({p, lang}) => {
  const y = interpolate(p, [0.1, 0.8], [330, 1180], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const pct = Math.round(interpolate(p, [0.1, 0.8], [0, 100], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const flash = interpolate(p, [0.8, 0.86, 0.96], [0, 0.55, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <>
      <div style={{position: 'absolute', left: 0, right: 0, top: y, height: 8, background: C.glow, boxShadow: `0 0 40px 14px ${C.cyan}`}} />
      <div style={{position: 'absolute', left: 0, right: 0, top: y - 160, height: 160, background: `linear-gradient(to bottom, rgba(34,195,240,0), rgba(34,195,240,0.28))`}} />
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: 1180,
          textAlign: 'center',
          color: C.glow,
          fontFamily: FONT,
          fontWeight: 800,
          fontSize: 44,
          letterSpacing: '0.2em',
          textShadow: '0 0 18px rgba(34,195,240,0.9)',
        }}
      >
        {lang === 'id' ? 'PINDAI X-RAY' : 'X-RAY SCAN'} {pct}%
      </div>
      <div style={{position: 'absolute', inset: 0, background: '#fff', opacity: flash}} />
    </>
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

export const Subtitles: React.FC<{phrases: Phrase[]; frame: number}> = ({phrases, frame}) => {
  const ph = phrases.find((x) => frame >= x.from && frame < x.to + 2);
  if (!ph) return null;
  const k = spring({frame: frame - ph.from, fps: FPS, config: {damping: 18, stiffness: 220}});
  return (
    <div style={{position: 'absolute', left: 50, right: 50, top: 1140, height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
      <div
        style={{
          padding: '14px 30px',
          borderRadius: 30,
          background: 'rgba(11,31,58,0.62)',
          fontFamily: FONT,
          fontWeight: 800,
          fontSize: 68,
          lineHeight: 1.12,
          textAlign: 'center',
          textShadow: '0 4px 0 rgba(11,31,58,0.95), 0 0 16px rgba(11,31,58,0.95)',
          transform: `scale(${interpolate(k, [0, 1], [0.92, 1])})`,
        }}
      >
        <Tokens tokens={ph.tokens} />
      </div>
    </div>
  );
};

export const Watermark: React.FC = () => (
  <div
    style={{
      position: 'absolute',
      right: 50,
      top: 1700,
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      opacity: 0.8,
      fontFamily: FONT,
      fontWeight: 800,
      fontSize: 34,
      color: C.ivory,
    }}
  >
    <svg width="44" height="44" viewBox="0 0 44 44">
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
