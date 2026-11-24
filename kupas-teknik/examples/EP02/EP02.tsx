import React, { useEffect, useMemo, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { HDRLoader } from "three/examples/jsm/loaders/HDRLoader.js";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { GTAOPass } from "three/examples/jsm/postprocessing/GTAOPass.js";
import { BokehPass } from "three/examples/jsm/postprocessing/BokehPass.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { SMAAPass } from "three/examples/jsm/postprocessing/SMAAPass.js";
import { buildWorld, texturesReady, World } from "./world";
import { AZ, FENCE_X, HERO_POST, SLICE_Y, sandY, camera as camAt, DECK_TOP, GATE_Z, HERO, JOINT_Y, LANES, P_RIN, P_RS, PILE_R, windKmh } from "./layout";
import { END_CARD_START, FPS, SUBS, ramp, shotAt } from "./timing";

// ------------------------------------------------------------------ 3D
type Assets = { env: THREE.Texture; world: World };
function useAssets(): Assets | null {
  const [a, setA] = useState<Assets | null>(null);
  const [h] = useState(() => delayRender("ep02 assets", { timeoutInMilliseconds: 600000 }));
  useEffect(() => {
    (async () => {
      const tl = new THREE.TextureLoader();
      const [env, emblem, wmark] = await Promise.all([
        new HDRLoader().loadAsync(staticFile("scene/sky_2k.hdr")),
        tl.loadAsync(staticFile("ep02/emblem_kupas_teknik_transparent.png")),
        tl.loadAsync(staticFile("ep02/watermark_kupas_teknik_landscape_transparent.png")),
      ]);
      env.mapping = THREE.EquirectangularReflectionMapping;
      emblem.colorSpace = wmark.colorSpace = THREE.SRGBColorSpace; emblem.anisotropy = wmark.anisotropy = 8;
      const world = buildWorld(emblem, wmark);
      await texturesReady();
      setA({ env, world });
    })().catch((e) => { console.error(e); throw e; });
  }, []);
  useEffect(() => { if (a) continueRender(h); }, [a, h]);
  return a;
}

const SUN = new THREE.Vector3(0.2835, 0.5592, 0.779).normalize();
const Rig: React.FC<{ a: Assets }> = ({ a }) => {
  const { camera, gl, scene, size } = useThree();
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const light = useMemo(() => {
    const l = new THREE.DirectionalLight(new THREE.Color(1.0, 0.95, 0.88), 4.8);
    l.castShadow = true; l.shadow.mapSize.set(4096, 4096);
    const c = l.shadow.camera as THREE.OrthographicCamera; c.near = 1; c.far = 600;
    l.shadow.bias = -0.0002; l.shadow.normalBias = 0.02; l.shadow.radius = 3; return l;
  }, []);
  const hemi = useMemo(() => new THREE.HemisphereLight(new THREE.Color(0.75, 0.85, 1.0), new THREE.Color(0.35, 0.55, 0.5), 1.1), []);
  const fx = useMemo(() => {
    const w = size.width, h = size.height;
    const composer = new EffectComposer(gl, new THREE.WebGLRenderTarget(w, h, { type: THREE.HalfFloatType, samples: 4 }));
    composer.setPixelRatio(1); composer.setSize(w, h);
    composer.addPass(new RenderPass(scene, camera));
    const ao = new GTAOPass(scene, camera, w, h); ao.updateGtaoMaterial({ radius: 0.6, distanceExponent: 1.2, thickness: 1.0, scale: 1.0, samples: 16 }); ao.blendIntensity = 0.85;
    composer.addPass(ao);
    const bokeh = new BokehPass(scene, camera, { focus: 10, aperture: 0.0005, maxblur: 0.008 });
    composer.addPass(bokeh);
    composer.addPass(new OutputPass());
    composer.addPass(new SMAAPass());
    return { composer, bokeh, ao };
  }, [gl, scene, camera, size.width, size.height]);
  const c = camAt(t);
  const pc = camera as THREE.PerspectiveCamera;
  pc.fov = c.fov; pc.near = c.near ?? 0.1; pc.far = 4000; pc.position.copy(c.pos); pc.lookAt(c.target); pc.updateProjectionMatrix();
  const dist = c.pos.distanceTo(c.target);
  // shadow box is FIXED per shot (no per-frame resize -> no shimmering), centre snapped to whole shadow texels
  const sh = shotAt(t); const cm = camAt((sh.t0 + sh.t1) / 2);
  const half = Math.min(220, Math.max(4, cm.pos.distanceTo(cm.target) * 1.8));
  const sc = light.shadow.camera as THREE.OrthographicCamera;
  if (sc.right !== half) { sc.left = -half; sc.right = half; sc.top = half; sc.bottom = -half; sc.updateProjectionMatrix(); }
  const texel = (2 * half) / light.shadow.mapSize.x;
  const lz = SUN.clone().negate(); const lx = new THREE.Vector3(0, 1, 0).cross(lz).normalize(); const ly = lz.clone().cross(lx).normalize();
  const tc = c.target.clone();
  const px = Math.round(tc.dot(lx) / texel) * texel, py = Math.round(tc.dot(ly) / texel) * texel, pz = tc.dot(lz);
  const snapped = lx.clone().multiplyScalar(px).add(ly.clone().multiplyScalar(py)).add(lz.clone().multiplyScalar(pz));
  light.position.copy(snapped).add(SUN.clone().multiplyScalar(300)); light.target.position.copy(snapped); light.target.updateMatrixWorld();
  a.world.update(t);
  gl.toneMapping = THREE.AgXToneMapping; gl.toneMappingExposure = 0.74;
  gl.shadowMap.enabled = true; gl.shadowMap.type = THREE.PCFSoftShadowMap;
  scene.environment = a.env; scene.background = a.env;
  scene.environmentRotation.y = 3.7658 + Math.PI; scene.backgroundRotation.y = 3.7658 + Math.PI;
  scene.environmentIntensity = 1.15; scene.backgroundIntensity = 1.1;
  if (!scene.fog) scene.fog = new THREE.FogExp2(new THREE.Color(0.78, 0.83, 0.85), 0.0011);
  const bu = fx.bokeh.uniforms as Record<string, THREE.IUniform>;
  bu["focus"].value = dist; bu["aperture"].value = c.aperture; bu["maxblur"].value = c.aperture > 0.002 ? 0.012 : 0.006;
  useEffect(() => {
    const hd = delayRender(`draw ${frame}`);
    fx.composer.render(); (gl.getContext() as WebGL2RenderingContext).finish();
    requestAnimationFrame(() => continueRender(hd));
  }, [frame, gl, fx]);
  return (<><primitive object={light} /><primitive object={light.target} /><primitive object={hemi} /><primitive object={a.world.scene} /></>);
};

// ------------------------------------------------------------------ overlay
const ORANGE = "#ff9a1f";
type Header = { kicker: string; title: [string, boolean][][]; tag?: string };
const HEADERS: Record<string, Header> = {
  S01: { kicker: "BAB 01 · KARAT DI PINGGIR PANTAI", title: [[["Besi di pantai", false]], [["cepat ", false], ["keropos", true]]], tag: "ILUSTRASI" },
  S02: { kicker: "BAB 02 · TOL DI ATAS LAUT", title: [[["12,7 km", true], [" berdiri", false]], [["di atas Teluk Benoa", false]]], tag: "ILUSTRASI 3D · SKALA DISEDERHANAKAN" },
  S03: { kicker: "BAB 03 · ANATOMI TIANG", title: [[["Dibelah: ", false], ["spun pile", true]], [["beton berongga + baja", false]]], tag: "BEDAH TIANG · ILUSTRASI" },
  S04: { kicker: "BAB 04 · MUSUH UTAMA", title: [[["Bukan ombak,", false]], [["tapi ", false], ["garam", true]]], tag: "BEDAH TIANG · DIPERCEPAT" },
  S05: { kicker: "BAB 05 · DUA TITIK LEMAH", title: [[["Pasang surut", false]], [["& ", false], ["sambungan las", true]]], tag: "ILUSTRASI · DIPERCEPAT" },
  S06: { kicker: "BAB 06 · PERISAI TIANG", title: [[["Dibungkus", false]], [["jaket HDPE", true]]], tag: "ILUSTRASI" },
  S07: { kicker: "BAB 07 · JALUR MOTOR", title: [[["Angin ", false], ["40 km/jam", true]], [["jalur motor ditutup", false]]], tag: "SIMULASI · ANEMOMETER" },
  S08: { kicker: "PENUTUP", title: [[["Beton vs", false]], [["garam laut", true]]] },
};
const shadow = "0 2px 10px rgba(0,0,0,0.55), 0 1px 2px rgba(0,0,0,0.6)";

const TopHeader: React.FC<{ t: number }> = ({ t }) => {
  const s = shotAt(t); const h = HEADERS[s.id]; if (!h || t >= END_CARD_START) return null;
  const inK = ramp(s.lt, 0.1, 0.55); const y = (1 - inK) * 10;
  return (
    <div style={{ position: "absolute", left: 64, top: 96 + y, opacity: inK, width: 960 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <div style={{ width: 6, height: 30, background: ORANGE }} />
        <div style={{ fontFamily: "Consolas, monospace", fontWeight: 700, fontSize: 30, color: "#fff", letterSpacing: 1, textShadow: shadow }}>{h.kicker}</div>
      </div>
      <div style={{ marginTop: 14 }}>
        {h.title.map((line, i) => (
          <div key={i} style={{ fontFamily: "Bahnschrift, 'Segoe UI', sans-serif", fontWeight: 700, fontSize: 78, lineHeight: "92px", color: "#fff", textShadow: shadow, whiteSpace: "nowrap" }}>
            {line.map(([txt, hl], j) => (
              <span key={j} style={{ position: "relative", display: "inline-block", whiteSpace: "pre" }}>
                {hl ? <span style={{ position: "absolute", left: -4, right: -4, bottom: 6, height: 13, background: ORANGE, opacity: 0.85, transformOrigin: "left", transform: `scaleX(${ramp(s.lt, 0.4, 0.9)})` }} /> : null}
                <span style={{ position: "relative" }}>{txt}</span>
              </span>
            ))}
          </div>
        ))}
      </div>
      {h.tag ? (
        <div style={{ marginTop: 18, display: "inline-flex", alignItems: "center", background: "rgba(10,12,16,0.47)", borderLeft: `4px solid ${ORANGE}`, padding: "7px 16px" }}>
          <span style={{ fontFamily: "Consolas, monospace", fontWeight: 700, fontSize: 24, color: "#ebebeb" }}>{h.tag}</span>
        </div>
      ) : null}
    </div>
  );
};

const Subtitles: React.FC<{ t: number }> = ({ t }) => {
  if (t >= END_CARD_START) return null;
  // bridge gaps shorter than 0.35 s so the pill never blinks off for 1–2 frames
  let c = SUBS.find((x) => t >= x.start - 0.03 && t <= x.end);
  if (!c) { const i = SUBS.findIndex((x) => x.start > t); if (i > 0 && SUBS[i].start - SUBS[i - 1].end < 0.35) c = SUBS[i - 1]; }
  if (!c) return null;
  const flat = c.lines.flat(); let activeIdx = -1; flat.forEach((w, k) => { if (t >= w.s - 0.02) activeIdx = k; });
  if (activeIdx >= 0 && t > flat[activeIdx].e + 0.25 && activeIdx === flat.length - 1) activeIdx = -1;
  const LINE_H = 82, GAP = 8;
  const n = c.lines.length; const top = 1618 - n * LINE_H - (n - 1) * GAP;
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top, display: "flex", flexDirection: "column", alignItems: "center", gap: GAP }}>
      {c.lines.map((l, i) => (
        <div key={i} style={{ height: LINE_H, display: "flex", alignItems: "center", padding: "0 24px", borderRadius: 14, background: "rgba(10,12,16,0.72)" }}>
          {l.map((w, j) => {
            const active = flat.indexOf(w) === activeIdx;
            return (
              <span key={j} style={{ position: "relative", fontFamily: "'Segoe UI', sans-serif", fontWeight: 700, fontSize: 58, color: "#fff", marginRight: j < l.length - 1 ? 15 : 0, whiteSpace: "nowrap" }}>
                {w.t}
                {active ? <span style={{ position: "absolute", left: 0, right: 0, bottom: 2, height: 4, borderRadius: 2, background: ORANGE }} /> : null}
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
};

type P3 = [number, number, number];
type Callout = { shot: string; label: string; p: P3; u0: number; u1: number; dx: number; dy: number; p2?: P3 };
const PH0 = AZ + Math.PI / 4, PH1 = PH0 + Math.PI * 1.5;
const hp = (a: number, r: number, y: number): P3 => [HERO.x + Math.sin(a) * r, y, HERO.z + Math.cos(a) * r];
const CALLOUTS: Callout[] = [
  { shot: "S01", label: "cat mengelupas", p: [FENCE_X - 0.047, sandY(FENCE_X) + 1.47, HERO_POST.z - 0.02], u0: 0.12, u1: 0.42, dx: 190, dy: -170 },
  { shot: "S02", label: "tiang beton", p: [-14.2, 1.2, -192], u0: 0.55, u1: 0.98, dx: -40, dy: 150 },
  { shot: "S02", label: "jalur motor", p: [LANES.motorW, DECK_TOP + 0.3, -214], u0: 0.62, u1: 0.98, dx: 140, dy: -160 },
  { shot: "S03", label: "rongga tengah", p: [HERO.x, SLICE_Y, HERO.z], u0: 0.5, u1: 0.98, dx: -200, dy: -150 },
  { shot: "S03", label: "baja prategang", p: hp(PH0 + Math.PI * 1.5 * 0.6, P_RS, SLICE_Y), u0: 0.58, u1: 0.98, dx: 200, dy: -170 },
  { shot: "S03", label: "kawat spiral", p: hp(AZ, P_RS + 0.012, SLICE_Y - 0.3), u0: 0.66, u1: 0.98, dx: -210, dy: 140 },
  { shot: "S03", label: "selimut beton", p: hp(PH0 + Math.PI * 1.5 * 0.3, PILE_R, SLICE_Y), u0: 0.78, u1: 0.98, dx: 210, dy: 130, p2: hp(PH0 + Math.PI * 1.5 * 0.3, P_RS + 0.009, SLICE_Y) },
  { shot: "S04", label: "ion klorida (Cl⁻)", p: hp(PH0 + Math.PI * 1.5 * 0.45, PILE_R - 0.015, SLICE_Y), u0: 0.08, u1: 0.5, dx: 210, dy: -150 },
  { shot: "S04", label: "baja berkarat", p: hp(PH0 + Math.PI * 1.5 * 0.3, P_RS, SLICE_Y), u0: 0.45, u1: 0.98, dx: 210, dy: -140 },
  { shot: "S04", label: "beton terkelupas", p: hp(PH0 + 0.25, PILE_R, SLICE_Y - 0.2), u0: 0.8, u1: 0.98, dx: -220, dy: 150 },
  { shot: "S05", label: "zona pasang surut", p: hp(AZ - 0.6, PILE_R, 0.3), u0: 0.06, u1: 0.4, dx: 220, dy: -150 },
  { shot: "S05", label: "sambungan las", p: hp(AZ - 0.25, PILE_R + 0.006, JOINT_Y), u0: 0.6, u1: 0.98, dx: -230, dy: -150 },
  { shot: "S05", label: "pelat baja (tanpa selimut)", p: hp(PH0 + 0.004, (P_RIN + PILE_R) / 2, JOINT_Y), u0: 0.7, u1: 0.98, dx: 120, dy: 170 },
  { shot: "S06", label: "jaket HDPE", p: hp(AZ, PILE_R + 0.035, JOINT_Y + 0.3), u0: 0.2, u1: 0.98, dx: 220, dy: -120 },
  { shot: "S06", label: "coating pelindung", p: hp(AZ + 0.3, PILE_R, 2.8), u0: 0.62, u1: 0.98, dx: 200, dy: -120 },
  { shot: "S07", label: "anemometer", p: [-14.5, DECK_TOP + 10.1, GATE_Z + 4], u0: 0.05, u1: 0.98, dx: 160, dy: 90 },
  { shot: "S07", label: "jalur motor", p: [LANES.motorW, DECK_TOP + 0.6, GATE_Z + 14], u0: 0.35, u1: 0.98, dx: 170, dy: -60 },
];
const projCam = new THREE.PerspectiveCamera(50, 1080 / 1920, 0.03, 5000);
function project(p: P3) { const v = new THREE.Vector3(...p).project(projCam); return { x: (v.x * 0.5 + 0.5) * 1080, y: (-v.y * 0.5 + 0.5) * 1920, ok: v.z < 1 }; }
const Callouts: React.FC<{ t: number }> = ({ t }) => {
  const s = shotAt(t); if (t >= END_CARD_START) return null;
  const c = camAt(t); projCam.fov = c.fov; projCam.position.copy(c.pos); projCam.lookAt(c.target); projCam.updateProjectionMatrix(); projCam.updateMatrixWorld();
  return (
    <>
      {CALLOUTS.filter((k) => k.shot === s.id && s.u >= k.u0 && s.u <= k.u1).map((k, i) => {
        // S01 post callout follows the hero post on the sand
        const p: P3 = k.p;
        const q = project(p); if (!q.ok) return null;
        const a = Math.min(ramp(s.u, k.u0, k.u0 + 0.05), 1 - ramp(s.u, k.u1 - 0.04, k.u1));
        const wLab = k.label.length * 17 + 34;
        let lx = q.x + k.dx; const ly = Math.max(430, Math.min(1380, q.y + k.dy));
        lx = k.dx < 0 ? Math.max(40 + wLab, Math.min(1040, lx)) : Math.max(40, Math.min(1040 - wLab, lx));
        const q2 = k.p2 ? project(k.p2) : null;
        return (
          <svg key={i} width={1080} height={1920} style={{ position: "absolute", left: 0, top: 0, opacity: a }}>
            {q2 ? (
              <g>
                <line x1={q.x} y1={q.y} x2={q2.x} y2={q2.y} stroke={ORANGE} strokeWidth={6} />
                {[q, q2].map((e, j) => { const ang = Math.atan2(q2.y - q.y, q2.x - q.x) + Math.PI / 2; return <line key={j} x1={e.x - Math.cos(ang) * 14} y1={e.y - Math.sin(ang) * 14} x2={e.x + Math.cos(ang) * 14} y2={e.y + Math.sin(ang) * 14} stroke={ORANGE} strokeWidth={6} />; })}
              </g>
            ) : null}
            <line x1={q.x} y1={q.y} x2={lx} y2={ly} stroke="rgba(255,255,255,0.55)" strokeWidth={5} />
            <line x1={q.x} y1={q.y} x2={lx} y2={ly} stroke="#fff" strokeWidth={2.2} />
            {q2 ? null : <><circle cx={q.x} cy={q.y} r={10} fill="none" stroke={ORANGE} strokeWidth={3.5} /><circle cx={q.x} cy={q.y} r={3.5} fill={ORANGE} /></>}
            <foreignObject x={lx - (k.dx < 0 ? 380 : 0)} y={ly - 26} width={380} height={60}>
              <div style={{ display: "flex", justifyContent: k.dx < 0 ? "flex-end" : "flex-start" }}>
                <div style={{ background: "rgba(10,12,16,0.72)", border: `2px solid ${ORANGE}`, borderRadius: 8, padding: "6px 14px", fontFamily: "'Segoe UI', sans-serif", fontWeight: 700, fontSize: 30, color: "#fff", whiteSpace: "nowrap" }}>{k.label}</div>
              </div>
            </foreignObject>
          </svg>
        );
      })}
    </>
  );
};

// "dicetak sambil diputar" — curved arrows circling the pile top during S03 anatomy
const SpinArrows: React.FC<{ t: number }> = ({ t }) => {
  const s = shotAt(t); if (s.id !== "S03") return null;
  const a = Math.min(ramp(s.u, 0.3, 0.36), 1 - ramp(s.u, 0.52, 0.58)); if (a <= 0) return null;
  const c = camAt(t); projCam.fov = c.fov; projCam.position.copy(c.pos); projCam.lookAt(c.target); projCam.updateProjectionMatrix(); projCam.updateMatrixWorld();
  const pts = Array.from({ length: 40 }, (_, i) => { const ang = s.lt * 4 + (i / 40) * Math.PI * 1.6; return project([HERO.x + Math.sin(ang) * 0.42, SLICE_Y + 1.4, HERO.z + Math.cos(ang) * 0.42]); });
  const d = pts.map((p, i) => `${i ? "L" : "M"}${p.x},${p.y}`).join(" ");
  const last = pts[pts.length - 1], prev = pts[pts.length - 3];
  const ang = Math.atan2(last.y - prev.y, last.x - prev.x);
  return (
    <svg width={1080} height={1920} style={{ position: "absolute", left: 0, top: 0, opacity: a }}>
      <path d={d} fill="none" stroke={ORANGE} strokeWidth={7} strokeLinecap="round" />
      <polygon points={`${last.x + Math.cos(ang) * 22},${last.y + Math.sin(ang) * 22} ${last.x + Math.cos(ang + 2.4) * 18},${last.y + Math.sin(ang + 2.4) * 18} ${last.x + Math.cos(ang - 2.4) * 18},${last.y + Math.sin(ang - 2.4) * 18}`} fill={ORANGE} />
      <foreignObject x={Math.min(700, last.x + 30)} y={last.y - 40} width={360} height={60}>
        <div style={{ background: "rgba(10,12,16,0.72)", border: `2px solid ${ORANGE}`, borderRadius: 8, padding: "6px 14px", fontFamily: "'Segoe UI', sans-serif", fontWeight: 700, fontSize: 28, color: "#fff", whiteSpace: "nowrap", display: "inline-block" }}>dicetak sambil diputar</div>
      </foreignObject>
    </svg>
  );
};

const WindHud: React.FC<{ t: number }> = ({ t }) => {
  const s = shotAt(t); if (s.id !== "S07") return null;
  const w = windKmh(t); const red = w >= 40;
  const a = Math.min(ramp(s.u, 0.04, 0.1), 1 - ramp(s.u, 0.96, 1));
  return (
    <div style={{ position: "absolute", left: 64, top: 470, opacity: a, background: "rgba(10,12,16,0.62)", borderLeft: `4px solid ${red ? "#ff3b30" : ORANGE}`, padding: "14px 20px", width: 330 }}>
      <div style={{ fontFamily: "Consolas, monospace", fontWeight: 700, fontSize: 22, color: "#cfd3d8", letterSpacing: 1 }}>KECEPATAN ANGIN</div>
      <div style={{ fontFamily: "Bahnschrift, sans-serif", fontWeight: 700, fontSize: 66, color: red ? "#ff4d42" : "#fff" }}>{Math.round(w)}<span style={{ fontSize: 30 }}> km/jam</span></div>
      <div style={{ height: 8, background: "rgba(255,255,255,0.18)", borderRadius: 4, marginTop: 4 }}>
        <div style={{ height: 8, width: `${Math.min(100, (w / 90) * 100)}%`, background: red ? "#ff3b30" : ORANGE, borderRadius: 4 }} />
      </div>
      <div style={{ fontFamily: "'Segoe UI', sans-serif", fontWeight: 700, fontSize: 24, color: red ? "#ff8a80" : "#9fe3b0", marginTop: 8 }}>
        {w >= 80 ? "JALUR MOTOR & MOBIL DITUTUP" : w >= 40 ? "JALUR MOTOR DITUTUP" : "SEMUA JALUR DIBUKA"}
      </div>
    </div>
  );
};

const EndCard: React.FC<{ t: number }> = ({ t }) => {
  if (t < END_CARD_START) return null;
  const k = ramp(t, END_CARD_START, END_CARD_START + 0.6);
  return (
    <AbsoluteFill style={{ background: `rgba(8,10,14,${0.72 * k})`, alignItems: "center", justifyContent: "center", flexDirection: "column" }}>
      <Img src={staticFile("ep02/watermark_kupas_teknik_landscape_transparent.png")} style={{ width: 760, opacity: k, transform: `translateY(${(1 - k) * 20}px)` }} />
      <div style={{ marginTop: 34, fontFamily: "'Segoe UI', sans-serif", fontWeight: 700, fontSize: 40, color: "#fff", opacity: ramp(t, END_CARD_START + 0.4, END_CARD_START + 1.0) }}>Ikuti untuk bedah teknik berikutnya</div>
    </AbsoluteFill>
  );
};

export const EP02: React.FC = () => {
  const { width, height } = useVideoConfig();
  const frame = useCurrentFrame(); const t = frame / FPS;
  const a = useAssets();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <ThreeCanvas width={width} height={height} gl={{ antialias: false, preserveDrawingBuffer: true }} shadows>
        {a ? <Rig a={a} /> : null}
      </ThreeCanvas>
      <Callouts t={t} />
      <SpinArrows t={t} />
      <WindHud t={t} />
      <TopHeader t={t} />
      <Subtitles t={t} />
      <EndCard t={t} />
    </AbsoluteFill>
  );
};
