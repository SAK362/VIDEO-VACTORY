import React from 'react';
import {interpolate, spring} from 'remotion';
import {C, FPS} from './theme';

// Maskot Curio: insinyur mini dengan helm emas dan kacamata lensa pembesar x-ray.
export const Curio: React.FC<{pose?: string | null; frame: number; localFrame: number; width?: number}> = ({
  pose,
  frame,
  localFrame,
  width = 280,
}) => {
  const t = frame / FPS;
  const pop = spring({frame: localFrame, fps: FPS, config: {damping: 14, stiffness: 120}});
  const p = pose || 'nod';

  const goggleUp = p === 'hook_confused' || p === 'goggles_up_wave' || p === 'point_left' || p === 'point_right' || p === 'thumbs_up' || p === 'nod';
  const tilt = p === 'hook_confused' ? -8 + Math.sin(t * 3) * 3 : 0;
  const bob = p === 'nod' ? Math.sin(t * 6) * 4 : Math.sin(t * 2) * 2;
  const surprised = p === 'surprised';

  // lengan kanan/kiri: titik ujung
  let rightEnd: [number, number] = [164, 192];
  let leftEnd: [number, number] = [36, 192];
  if (p === 'point_right') rightEnd = [196, 150];
  if (p === 'point_left') leftEnd = [4, 150];
  if (p === 'thumbs_up') rightEnd = [170, 116];
  if (p === 'goggles_up_wave') rightEnd = [166, 112 + Math.sin(t * 9) * 14];
  if (p === 'surprised') {
    rightEnd = [176, 130];
    leftEnd = [24, 130];
  }

  const bubble = p === 'hook_confused' ? '?' : surprised ? '!' : null;
  const height = (width * 260) / 200;

  return (
    <svg
      viewBox="0 0 200 260"
      width={width}
      height={height}
      style={{
        transform: `scale(${interpolate(pop, [0, 1], [0.6, 1])}) translateY(${interpolate(pop, [0, 1], [40, 0])}px)`,
        transformOrigin: '50% 100%',
        opacity: Math.min(1, pop * 1.5),
        overflow: 'visible',
      }}
    >
      <ellipse cx="100" cy="252" rx="54" ry="7" fill="#000" opacity="0.25" />
      {/* kaki */}
      <rect x="72" y="205" width="22" height="40" rx="8" fill={C.navy2} />
      <rect x="106" y="205" width="22" height="40" rx="8" fill={C.navy2} />
      <rect x="66" y="238" width="32" height="12" rx="6" fill="#0A1626" />
      <rect x="102" y="238" width="32" height="12" rx="6" fill="#0A1626" />
      {/* lengan */}
      <line x1="62" y1="152" x2={leftEnd[0]} y2={leftEnd[1]} stroke={C.ivory} strokeWidth="15" strokeLinecap="round" />
      <line x1="138" y1="152" x2={rightEnd[0]} y2={rightEnd[1]} stroke={C.ivory} strokeWidth="15" strokeLinecap="round" />
      <circle cx={leftEnd[0]} cy={leftEnd[1]} r="9" fill="#F2C9A0" />
      <circle cx={rightEnd[0]} cy={rightEnd[1]} r="9" fill="#F2C9A0" />
      {p === 'thumbs_up' ? <rect x={rightEnd[0] - 3} y={rightEnd[1] - 22} width="8" height="16" rx="4" fill="#F2C9A0" /> : null}
      {/* badan */}
      <rect x="64" y="126" width="72" height="40" rx="14" fill={C.ivory} />
      <rect x="62" y="146" width="76" height="68" rx="16" fill={C.navy2} />
      <rect x="86" y="158" width="28" height="22" rx="6" fill={C.cyan} opacity="0.85" />
      <circle cx="100" cy="169" r="5" fill={C.navy} />
      {/* kepala */}
      <g transform={`translate(0 ${bob}) rotate(${tilt} 100 100)`}>
        <circle cx="60" cy="98" r="8" fill="#F2C9A0" />
        <circle cx="140" cy="98" r="8" fill="#F2C9A0" />
        <circle cx="100" cy="96" r="42" fill="#F2C9A0" />
        {/* helm */}
        <path d="M54 84 Q100 22 146 84 Z" fill={C.gold} />
        <rect x="94" y="40" width="12" height="44" fill="#FFD25A" />
        <rect x="48" y="80" width="104" height="11" rx="5" fill="#E0A010" />
        {/* mata */}
        <circle cx="85" cy="104" r={surprised ? 6.5 : 4.5} fill={C.navy} />
        <circle cx="115" cy="104" r={surprised ? 6.5 : 4.5} fill={C.navy} />
        {/* mulut */}
        {surprised ? (
          <ellipse cx="100" cy="127" rx="6" ry="8" fill={C.navy} />
        ) : p === 'hook_confused' ? (
          <path d="M88 126 Q94 120 100 126 T112 126" stroke={C.navy} strokeWidth="3.5" fill="none" strokeLinecap="round" />
        ) : (
          <path d="M87 122 Q100 134 113 122" stroke={C.navy} strokeWidth="3.5" fill="none" strokeLinecap="round" />
        )}
        {/* kacamata x-ray */}
        {goggleUp ? (
          <g transform="translate(0 -40)">
            <rect x="52" y="86" width="96" height="9" rx="4" fill="#0A1626" opacity="0.8" />
            <circle cx="82" cy="104" r="15" fill={C.cyan} opacity="0.55" stroke={C.gold} strokeWidth="5" />
            <circle cx="118" cy="104" r="15" fill={C.cyan} opacity="0.55" stroke={C.gold} strokeWidth="5" />
            <line x1="97" y1="104" x2="103" y2="104" stroke={C.gold} strokeWidth="5" />
          </g>
        ) : (
          <g>
            <circle cx="85" cy="104" r="21" fill={C.cyan} opacity="0.22" />
            <circle cx="115" cy="104" r="21" fill={C.cyan} opacity="0.22" />
            <circle cx="85" cy="104" r="16" fill={C.glow} opacity="0.5" stroke={C.gold} strokeWidth="5" />
            <circle cx="115" cy="104" r="16" fill={C.glow} opacity="0.5" stroke={C.gold} strokeWidth="5" />
            <line x1="101" y1="104" x2="99" y2="104" stroke={C.gold} strokeWidth="5" />
            <line x1="56" y1="102" x2="69" y2="102" stroke={C.gold} strokeWidth="5" />
            <line x1="131" y1="102" x2="144" y2="102" stroke={C.gold} strokeWidth="5" />
          </g>
        )}
      </g>
      {bubble ? (
        <text x="160" y="52" fontSize="56" fontWeight="800" fill={C.gold} fontFamily="'Plus Jakarta Sans', Arial, sans-serif" textAnchor="middle">
          {bubble}
        </text>
      ) : null}
    </svg>
  );
};
