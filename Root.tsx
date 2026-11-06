import React from 'react';
import {Composition} from 'remotion';
import {Video} from './Video';
import {totalFrames} from './timing';
import {FPS} from './theme';
import type {VideoProps} from './types';

// Contoh props untuk pratinjau di Remotion Studio. Saat render, props asli datang dari work/props.json.
const defaultProps: VideoProps = {
  title: 'Contoh',
  lang: 'en',
  audioSeconds: 20,
  audioFile: 'voiceover.wav',
  narration:
    'You press the tap and water just *comes out*. But how? Turns out, a hidden *impeller* is spinning fast. It throws water outward, and pressure pushes it up the pipe.',
  scenes: [
    {type: 'establish', label: 'EVERYDAY MYSTERY', heading: 'How does a *water pump* work?', set: 'pump', camera: 'dolly_in', curio: 'hook_confused'},
    {type: 'xray_scan', label: 'X-RAY', heading: 'Let us *look inside*', set: 'pump', camera: 'orbit_slow', curio: 'goggles_down'},
    {type: 'step', label: 'STEP 1', heading: 'The *impeller* spins', set: 'pump', focus: 'impeller', camera: 'orbit_close', flow: 'water', callouts: [{text: 'Impeller'}]},
    {type: 'outro_loop', label: 'YOUR TURN', heading: 'What should we *x-ray* next?', set: 'pump', camera: 'dolly_out', curio: 'goggles_up_wave'},
  ],
};

export const Root: React.FC = () => (
  <Composition
    id="CurioVideo"
    component={Video}
    width={1080}
    height={1920}
    fps={FPS}
    durationInFrames={totalFrames(defaultProps.audioSeconds)}
    defaultProps={defaultProps}
    calculateMetadata={({props}) => ({durationInFrames: totalFrames((props as VideoProps).audioSeconds)})}
  />
);
