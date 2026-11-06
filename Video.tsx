import React, {useEffect, useMemo, useState} from 'react';
import {AbsoluteFill, Audio, continueRender, delayRender, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {Stage3D} from './Stage3D';
import {Curio} from './Curio';
import {Callouts, DangerOverlay, DataCardView, LabelBlock, ScanOverlay, SceneFade, Subtitles, Watermark} from './Overlays';
import {buildTiming} from './timing';
import {C, FONT} from './theme';
import type {Scene, VideoProps} from './types';

const FALLBACK_SCENE: Scene = {type: 'establish', set: 'generic', camera: 'dolly_in'};

// Memuat font Plus Jakarta Sans (bila gagal, pakai font cadangan) sebelum frame pertama dirender.
function useFont() {
  const [handle] = useState(() => delayRender('font'));
  useEffect(() => {
    const id = 'curio-font-style';
    if (!document.getElementById(id)) {
      const style = document.createElement('style');
      style.id = id;
      style.textContent = "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&display=block');";
      document.head.appendChild(style);
    }
    const done = () => continueRender(handle);
    const timer = setTimeout(done, 8000);
    Promise.resolve((document as any).fonts?.load("800 40px 'Plus Jakarta Sans'"))
      .catch(() => undefined)
      .then(() => {
        clearTimeout(timer);
        done();
      });
    return () => clearTimeout(timer);
  }, [handle]);
}

export const Video: React.FC<VideoProps> = (props) => {
  useFont();
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();

  const scenes = props.scenes && props.scenes.length ? props.scenes : [FALLBACK_SCENE];
  const {timed, phrases} = useMemo(() => buildTiming(props.narration, scenes, props.audioSeconds), [props.narration, props.scenes, props.audioSeconds]);

  let idx = timed.findIndex((s) => frame >= s.from && frame < s.from + s.dur);
  if (idx < 0) idx = frame < timed[0].from ? 0 : timed.length - 1;
  const scene = timed[idx];
  const localFrame = Math.max(0, frame - scene.from);
  const p = Math.min(1, localFrame / Math.max(1, scene.dur));

  const scanIdx = timed.findIndex((s) => s.type === 'xray_scan');
  let xray = 0;
  if (scanIdx >= 0) {
    if (idx > scanIdx) xray = 1;
    else if (idx === scanIdx) xray = interpolate(p, [0.35, 0.8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  }

  return (
    <AbsoluteFill style={{backgroundColor: C.navy, fontFamily: FONT}}>
      <Audio src={staticFile(props.audioFile || 'voiceover.wav')} />

      <ThreeCanvas width={width} height={height} camera={{fov: 38, position: [0, 1.7, 6.6]}} style={{position: 'absolute', inset: 0}}>
        <Stage3D scene={scene} frame={frame} localFrame={localFrame} xray={xray} />
      </ThreeCanvas>

      {scene.type === 'danger' ? <DangerOverlay frame={frame} /> : null}
      {scene.type === 'xray_scan' ? <ScanOverlay p={p} lang={props.lang} /> : null}

      <LabelBlock label={scene.label} heading={scene.heading} localFrame={localFrame} />
      <Callouts callouts={scene.callouts} localFrame={localFrame} />
      {scene.type === 'data_card' || scene.data_card ? <DataCardView card={scene.data_card} localFrame={localFrame} /> : null}

      {scene.curio ? (
        <div style={{position: 'absolute', left: 40, top: 1370}}>
          <Curio pose={scene.curio} frame={frame} localFrame={localFrame} width={260} />
        </div>
      ) : null}

      <Subtitles phrases={phrases} frame={frame} />
      <Watermark />
      <SceneFade localFrame={localFrame} first={idx === 0} />
    </AbsoluteFill>
  );
};
