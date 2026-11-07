import React, {useMemo} from 'react';
import {useThree} from '@react-three/fiber';
import * as THREE from 'three';
import {C, FPS} from './theme';
import type {VideoProps} from './types';
import type {TimedScene} from './types';

type Vec = [number, number, number];
type Prim = {
  kind: 'box' | 'cyl' | 'sphere' | 'cone';
  pos: Vec;
  rot?: Vec;
  size: number[]; // box: [x,y,z] | cyl: [rTop,rBottom,height] | sphere: [r] | cone: [r,height,segments]
  color: string;
};
type Part = {
  id: string;
  prims: Prim[];
  shell: boolean; // bagian casing luar yang ikut terpotong pada adegan bedah
  ex: Vec; // arah geser saat "exploded"
  origin?: Vec;
  spin?: number;
  spinAxis?: 'x' | 'y' | 'z';
  bob?: number;
  phase?: number;
};
type Model = {parts: Part[]; path: Vec[]};

const PI = Math.PI;

function hashString(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return Math.abs(h);
}

function pumpModel(): Model {
  const fins: Prim[] = [];
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * PI * 2;
    fins.push({kind: 'box', pos: [Math.cos(a) * 0.55, Math.sin(a) * 0.55, 0], rot: [0, 0, a], size: [0.7, 0.12, 0.5], color: '#FFCF5A'});
  }
  return {
    parts: [
      {id: 'housing', shell: true, ex: [0, 0.8, 0], prims: [{kind: 'cyl', pos: [0, 0, 0], rot: [PI / 2, 0, 0], size: [1.25, 1.25, 0.9], color: '#3B6EA5'}]},
      {
        id: 'impeller',
        shell: false,
        ex: [0, 0, 0.9],
        spin: 6,
        spinAxis: 'z',
        prims: [{kind: 'cyl', pos: [0, 0, 0], rot: [PI / 2, 0, 0], size: [0.28, 0.28, 0.55], color: C.gold}, ...fins],
      },
      {id: 'inlet', shell: true, ex: [0, 0, 1.2], prims: [{kind: 'cyl', pos: [0, 0, 1.5], rot: [PI / 2, 0, 0], size: [0.38, 0.38, 1.6], color: '#5B8FC7'}]},
      {id: 'outlet', shell: true, ex: [0, 1.0, 0], prims: [{kind: 'cyl', pos: [0, 1.75, 0], size: [0.38, 0.38, 1.5], color: '#5B8FC7'}]},
      {id: 'motor', shell: true, ex: [0, 0, -1.3], prims: [{kind: 'cyl', pos: [0, 0, -1.5], rot: [PI / 2, 0, 0], size: [0.75, 0.75, 1.5], color: '#2A4A73'}]},
      {id: 'shaft', shell: false, ex: [0, 0, -0.7], prims: [{kind: 'cyl', pos: [0, 0, -0.7], rot: [PI / 2, 0, 0], size: [0.12, 0.12, 1.2], color: '#C0D4E8'}]},
      {id: 'base', shell: false, ex: [0, -0.6, 0], prims: [{kind: 'box', pos: [0, -1.35, 0], size: [3.2, 0.2, 3.8], color: '#1B3A63'}]},
    ],
    path: [[0, 0, 3.0], [0, 0, 0.4], [0, 0.2, 0], [0, 1.2, 0], [0, 3.0, 0]],
  };
}

function engineModel(): Model {
  const pistons: Part[] = [];
  for (let i = 0; i < 4; i++) {
    pistons.push({
      id: 'piston' + (i + 1),
      shell: false,
      ex: [0, 0.9, 0],
      bob: 0.28,
      phase: (i * PI) / 2,
      origin: [-0.8 + i * 0.53, 0.1, 0],
      prims: [{kind: 'cyl', pos: [0, 0, 0], size: [0.22, 0.22, 0.5], color: '#FFCF5A'}],
    });
  }
  return {
    parts: [
      {id: 'block', shell: true, ex: [0, 0, 0], prims: [{kind: 'box', pos: [0, 0, 0], size: [2.4, 1.4, 1.4], color: '#3B6EA5'}]},
      {id: 'head', shell: true, ex: [0, 1.2, 0], prims: [{kind: 'box', pos: [0, 0.9, 0], size: [2.4, 0.35, 1.4], color: '#2A4A73'}]},
      ...pistons,
      {id: 'crankshaft', shell: false, ex: [0, -0.9, 0], spin: 5, spinAxis: 'x', prims: [{kind: 'cyl', pos: [0, -0.45, 0], rot: [0, 0, PI / 2], size: [0.12, 0.12, 2.2], color: C.gold}]},
      {id: 'exhaust', shell: true, ex: [1.2, 0.4, 0], prims: [{kind: 'cyl', pos: [1.6, 0.4, 0], rot: [0, 0, PI / 2], size: [0.2, 0.2, 1.0], color: '#5B8FC7'}]},
      {id: 'intake', shell: true, ex: [-1.2, 0.4, 0], prims: [{kind: 'cyl', pos: [-1.6, 0.4, 0], rot: [0, 0, PI / 2], size: [0.2, 0.2, 1.0], color: '#5B8FC7'}]},
      {id: 'base', shell: false, ex: [0, -0.6, 0], prims: [{kind: 'box', pos: [0, -1.1, 0], size: [3.2, 0.2, 2.2], color: '#1B3A63'}]},
    ],
    path: [[-2.4, 0.4, 0], [-1.0, 0.4, 0], [0.2, 0.2, 0], [1.2, 0.4, 0], [2.6, 0.4, 0]],
  };
}

function rodModel(): Model {
  const cloud: Prim[] = [];
  const cx = [-0.9, -0.3, 0.4, 1.0];
  for (let i = 0; i < 4; i++) cloud.push({kind: 'sphere', pos: [cx[i], 3.7 + (i % 2) * 0.2, 0], size: [0.6 + (i % 2) * 0.15], color: '#5C7A99'});
  return {
    parts: [
      {id: 'rod', shell: true, ex: [0, 1.0, 0], prims: [{kind: 'cyl', pos: [0, 1.1, 0], size: [0.07, 0.11, 3.4], color: '#9FB4C8'}, {kind: 'cone', pos: [0, 3.05, 0], size: [0.14, 0.5, 8], color: C.gold}]},
      {id: 'house', shell: true, ex: [0, 0, 0], prims: [{kind: 'box', pos: [0, -0.7, 0], size: [2.4, 1.2, 1.8], color: '#3B6EA5'}, {kind: 'cone', pos: [0, 0.35, 0], rot: [0, PI / 4, 0], size: [1.9, 0.9, 4], color: '#7A4E2D'}]},
      {id: 'cable', shell: false, ex: [0.9, 0, 0], prims: [{kind: 'cyl', pos: [1.0, 0.0, 0], size: [0.04, 0.04, 2.6], color: C.gold}]},
      {id: 'ground', shell: false, ex: [0.6, -0.9, 0], prims: [{kind: 'cyl', pos: [1.0, -1.7, 0], size: [0.07, 0.03, 0.9], color: '#C0D4E8'}]},
      {id: 'cloud', shell: false, ex: [0, 0.8, 0], prims: cloud},
      {id: 'base', shell: false, ex: [0, -0.5, 0], prims: [{kind: 'box', pos: [0, -1.4, 0], size: [3.4, 0.2, 2.6], color: '#1B3A63'}]},
    ],
    path: [[0, 3.5, 0], [0, 1.6, 0], [1.0, 0.8, 0], [1.0, -1.7, 0]],
  };
}

function genericModel(seed: string): Model {
  const h = hashString(seed || 'x');
  const hues = ['#3B6EA5', '#2F7F8F', '#6A5BA8', '#3F8A5E'];
  const body = hues[h % hues.length];
  const teeth: Prim[] = [];
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * PI * 2;
    teeth.push({kind: 'box', pos: [Math.cos(a) * 0.62, 0, Math.sin(a) * 0.62], rot: [0, -a, 0], size: [0.22, 0.4, 0.14], color: '#FFCF5A'});
  }
  return {
    parts: [
      {id: 'body', shell: true, ex: [0, 0.9, 0], prims: [{kind: 'cyl', pos: [0, 0, 0], size: [1.2, 1.2, 1.7], color: body}]},
      {id: 'gear', shell: false, ex: [0, 0, 0], spin: 3, spinAxis: 'y', prims: [{kind: 'cyl', pos: [0, 0, 0], size: [0.5, 0.5, 0.4], color: C.gold}, ...teeth]},
      {id: 'pipe_in', shell: true, ex: [-1.2, 0, 0], prims: [{kind: 'cyl', pos: [-1.6, 0, 0], rot: [0, 0, PI / 2], size: [0.3, 0.3, 1.4], color: '#5B8FC7'}]},
      {id: 'pipe_out', shell: true, ex: [1.2, 0, 0], prims: [{kind: 'cyl', pos: [1.6, 0, 0], rot: [0, 0, PI / 2], size: [0.3, 0.3, 1.4], color: '#5B8FC7'}]},
      {id: 'cap', shell: true, ex: [0, 1.4, 0], prims: [{kind: 'cyl', pos: [0, 1.0, 0], size: [0.9, 1.0, 0.3], color: '#2A4A73'}]},
      {id: 'base', shell: false, ex: [0, -0.6, 0], prims: [{kind: 'box', pos: [0, -1.1, 0], size: [3.4, 0.2, 2.6], color: '#1B3A63'}]},
    ],
    path: [[-2.6, 0, 0], [-0.9, 0, 0], [0, 0.2, 0], [0.9, 0, 0], [2.6, 0, 0]],
  };
}

export function modelFor(set?: string): Model {
  const s = String(set || '').toLowerCase();
  if (/pump|impeller|water|well|pompa/.test(s)) return pumpModel();
  if (/engine|motor|piston|mesin/.test(s)) return engineModel();
  if (/rod|lightning|petir|thunder|penangkal/.test(s)) return rodModel();
  return genericModel(s);
}

const FLOW_COLORS: Record<string, string> = {water: '#5CC8FF', electricity: '#FFD84A', air: '#E8F4FF', heat: '#FF7A3D'};

function onPath(path: Vec[], s: number): Vec {
  const segs = path.length - 1;
  const f = Math.min(0.9999, Math.max(0, s)) * segs;
  const i = Math.floor(f);
  const k = f - i;
  const a = path[i];
  const b = path[i + 1];
  return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k];
}


type StyleName = NonNullable<VideoProps['style']>;
const OUTLINE = '#06142A';

const Geo: React.FC<{p: Prim; style: StyleName}> = ({p, style}) => {
  const seg = style === 'real' ? 40 : 20;
  switch (p.kind) {
    case 'box':
      return <boxGeometry args={[p.size[0], p.size[1], p.size[2]]} />;
    case 'cyl':
      return <cylinderGeometry args={[p.size[0], p.size[1], p.size[2], seg]} />;
    case 'sphere':
      return <icosahedronGeometry args={[p.size[0], style === 'real' ? 3 : 1]} />;
    default:
      return <coneGeometry args={[p.size[0], p.size[1], p.size[2] || 8]} />;
  }
};

// Gradien 3 tingkat untuk bayangan ala kartun.
function makeToonGradient(): THREE.DataTexture {
  const data = new Uint8Array([70, 70, 70, 255, 165, 165, 165, 255, 255, 255, 255, 255]);
  const tex = new THREE.DataTexture(data, 3, 1, THREE.RGBAFormat);
  tex.minFilter = THREE.NearestFilter;
  tex.magFilter = THREE.NearestFilter;
  tex.needsUpdate = true;
  return tex;
}

const CameraRig: React.FC<{cam: string; p: number; t: number}> = ({cam, p, t}) => {
  const {camera} = useThree();
  let x = 0;
  let y = 1.7;
  let z = 6.6;
  switch (cam) {
    case 'dolly_in':
      z = 8.6 - 3.4 * p;
      x = Math.sin(p * 1.2) * 1.2;
      break;
    case 'dolly_out':
      z = 5.2 + 3.2 * p;
      break;
    case 'orbit_slow': {
      const a = -0.55 + 1.1 * p;
      x = Math.sin(a) * 6.8;
      z = Math.cos(a) * 6.8;
      y = 1.9;
      break;
    }
    case 'orbit_close': {
      const a = -0.9 + 1.8 * p;
      x = Math.sin(a) * 4.8;
      z = Math.cos(a) * 4.8;
      y = 1.3;
      break;
    }
    case 'cutaway_orbit': {
      const a = 0.35 + 0.75 * p; // kamera di sisi +x agar bagian dalam yang terbuka terlihat
      x = Math.sin(a) * 5.6;
      z = Math.cos(a) * 5.6;
      y = 1.6 - 0.3 * p;
      break;
    }
    case 'pan_down':
      y = 3.4 - 2.1 * p;
      z = 6.2;
      break;
    case 'pan_up':
      y = 0.5 + 2.2 * p;
      z = 6.2;
      break;
    case 'top_down':
      y = 6.8;
      z = 2.4 + 0.8 * p;
      break;
    default:
      x = Math.sin(t * 0.6) * 0.5;
      y = 1.7 + Math.sin(t * 0.5) * 0.15;
      z = 6.6;
  }
  camera.position.set(x, y, z);
  camera.lookAt(0, 0.3, 0);
  camera.updateProjectionMatrix();
  return null;
};

type ModelViewProps = {
  model: Model;
  style: StyleName;
  ts: number; // waktu (detik) untuk animasi
  t: number;
  focus: string;
  explode: number;
  plane: THREE.Plane;
  ghost?: boolean;
  gradient: THREE.DataTexture;
};

const ModelView: React.FC<ModelViewProps> = ({model, style, ts, t, focus, explode, plane, ghost, gradient}) => {
  const pulse = 0.5 + 0.5 * Math.sin(t * 7);
  return (
    <>
      {model.parts.map((part) => {
        const origin = part.origin || [0, 0, 0];
        const pos: Vec = [
          origin[0] + part.ex[0] * explode,
          origin[1] + part.ex[1] * explode + (part.bob ? Math.sin(ts * 6 + (part.phase || 0)) * part.bob : 0),
          origin[2] + part.ex[2] * explode,
        ];
        const rot: Vec = [0, 0, 0];
        if (part.spin) rot[part.spinAxis === 'x' ? 0 : part.spinAxis === 'y' ? 1 : 2] = ts * part.spin;
        const isFocus = focus.length > 0 && part.id.toLowerCase().includes(focus);
        const clip = part.shell ? [plane] : null;
        const emissive = isFocus ? C.gold : '#000000';
        const emissiveIntensity = isFocus ? 0.35 + 0.45 * pulse : 0;
        return (
          <group key={part.id} position={pos} rotation={rot}>
            {part.prims.map((pr, i) => {
              const p3: Vec = [pr.pos[0] - origin[0], pr.pos[1] - origin[1], pr.pos[2] - origin[2]];
              return (
                <React.Fragment key={i}>
                  <mesh position={p3} rotation={pr.rot || [0, 0, 0]}>
                    <Geo p={pr} style={style} />
                    {style === 'toon' ? (
                      <meshToonMaterial
                        color={pr.color}
                        gradientMap={gradient}
                        side={THREE.DoubleSide}
                        clippingPlanes={clip as any}
                        emissive={emissive}
                        emissiveIntensity={emissiveIntensity}
                      />
                    ) : (
                      <meshStandardMaterial
                        color={pr.color}
                        metalness={0.45}
                        roughness={0.28}
                        side={THREE.DoubleSide}
                        clippingPlanes={clip as any}
                        emissive={emissive}
                        emissiveIntensity={emissiveIntensity}
                        transparent={!!ghost}
                        opacity={ghost ? 0.22 : 1}
                      />
                    )}
                  </mesh>
                  {style === 'toon' ? (
                    <mesh position={p3} rotation={pr.rot || [0, 0, 0]} scale={[1.055, 1.055, 1.055]}>
                      <Geo p={pr} style={style} />
                      <meshBasicMaterial color={OUTLINE} side={THREE.BackSide} clippingPlanes={clip as any} />
                    </mesh>
                  ) : null}
                </React.Fragment>
              );
            })}
          </group>
        );
      })}
    </>
  );
};

type StageProps = {
  scene: TimedScene;
  frame: number; // frame global
  localFrame: number; // frame di dalam adegan
  style: StyleName;
  cut: number; // 0..1 seberapa terbuka adegan bedah
};

const easeInOut = (x: number) => (x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2);

export const Stage3D: React.FC<StageProps> = ({scene, frame, localFrame, style, cut}) => {
  const {gl} = useThree();
  gl.localClippingEnabled = true;

  const model = useMemo(() => modelFor(scene.set), [scene.set]);
  const gradient = useMemo(() => makeToonGradient(), []);
  const t = frame / FPS;
  const p = Math.min(1, Math.max(0, localFrame / Math.max(1, scene.dur)));
  const slow = scene.type === 'slowmo' ? 0.3 : 1;
  const ts = t * slow;
  const popIn = 0.88 + 0.12 * Math.min(1, localFrame / 10);
  const focus = String(scene.focus || '').toLowerCase();
  const flow = scene.flow && FLOW_COLORS[scene.flow] ? scene.flow : null;
  const danger = scene.type === 'danger';

  // Bidang potong: makin besar cut, makin banyak bagian casing (sisi +x) yang terpotong hingga separuh.
  const plane = useMemo(() => new THREE.Plane(new THREE.Vector3(-1, 0, 0), 99), []);
  plane.constant = 3 - 3.05 * easeInOut(cut);
  const explode = 0.35 * easeInOut(cut); // casing bergeser sedikit saat dibedah

  const ground = style === 'toon';
  const layers: {y: number; h: number; c: string}[] = [
    {y: -1.525, h: 0.15, c: '#63C467'},
    {y: -1.775, h: 0.35, c: '#8F5E3F'},
    {y: -2.1, h: 0.3, c: '#2FA9DA'},
    {y: -2.4, h: 0.3, c: '#5E6978'},
  ];

  return (
    <>
      <fog attach="fog" args={[style === 'real' ? '#050E1C' : '#0F3B63', 12, 26]} />
      <CameraRig cam={scene.camera || 'static_drift'} p={p} t={ts} />
      <ambientLight intensity={style === 'real' ? 0.5 : 0.85} color="#CFE8FF" />
      <directionalLight position={[4, 6, 5]} intensity={style === 'real' ? 1.6 : 1.2} />
      <pointLight position={[-3, 2, 3]} intensity={1.4} color={C.cyan} />
      <pointLight position={[3, 3, -2]} intensity={0.9} color={C.gold} />
      {danger ? <pointLight position={[0, 2, 3]} intensity={2.2 * (0.6 + 0.4 * Math.sin(t * 10))} color={C.red} /> : null}

      {ground ? (
        <group>
          {layers.map((l, i) => (
            <group key={i}>
              <mesh position={[0, l.y, 0]}>
                <boxGeometry args={[7.4, l.h, 6.4]} />
                <meshToonMaterial color={l.c} gradientMap={gradient} />
              </mesh>
              <mesh position={[0, l.y, 0]} scale={[1.01, 1.02, 1.01]}>
                <boxGeometry args={[7.4, l.h, 6.4]} />
                <meshBasicMaterial color={OUTLINE} side={THREE.BackSide} />
              </mesh>
            </group>
          ))}
        </group>
      ) : (
        <group>
          <mesh position={[0, -1.5, 0]}>
            <cylinderGeometry args={[3.6, 3.6, 0.1, 64]} />
            <meshStandardMaterial color="#0A1A2E" metalness={0.6} roughness={0.25} transparent opacity={0.82} />
          </mesh>
          <mesh position={[0, -1.43, 0]} rotation={[Math.PI / 2, 0, 0]}>
            <torusGeometry args={[3.5, 0.04, 8, 96]} />
            <meshBasicMaterial color={C.glow} />
          </mesh>
          <group position={[0, -3.0, 0]} scale={[popIn, -popIn, popIn]}>
            <ModelView model={model} style={style} ts={ts} t={t} focus={focus} explode={explode} plane={plane} ghost gradient={gradient} />
          </group>
        </group>
      )}

      <group scale={[popIn, popIn, popIn]} rotation={[0, Math.sin(ts * 0.4) * 0.25, 0]}>
        <ModelView model={model} style={style} ts={ts} t={t} focus={focus} explode={explode} plane={plane} gradient={gradient} />

        {flow
          ? Array.from({length: 16}).map((_, i) => {
              const s = (ts * 0.32 + i / 16) % 1;
              const [x, y, z] = onPath(model.path, s);
              const jitter = flow === 'electricity' ? Math.sin(ts * 40 + i * 3) * 0.06 : 0;
              return (
                <mesh key={i} position={[x + jitter, y, z]}>
                  <icosahedronGeometry args={[0.11, 0]} />
                  <meshBasicMaterial color={FLOW_COLORS[flow as string]} />
                </mesh>
              );
            })
          : null}
      </group>

      {/* partikel melayang agar adegan terasa hidup */}
      {Array.from({length: 18}).map((_, i) => {
        const sx = ((hashString('s' + i) % 1000) / 1000 - 0.5) * 8;
        const sz = ((hashString('z' + i) % 1000) / 1000 - 0.5) * 5 - 0.5;
        const y = -1.2 + (((ts * 0.25 + (hashString('y' + i) % 1000) / 1000) % 1) * 5);
        return (
          <mesh key={i} position={[sx + Math.sin(ts + i) * 0.15, y, sz]}>
            <icosahedronGeometry args={[0.04 + (i % 3) * 0.02, 0]} />
            <meshBasicMaterial color={i % 4 === 0 ? C.gold : C.glow} transparent opacity={0.7} />
          </mesh>
        );
      })}
    </>
  );
};
