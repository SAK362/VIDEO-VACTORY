// World layout (three.js units = metres, Y up). Road runs along -Z.
import * as THREE from "three";
import { lerp, phraseTime, ramp, shotAt, smooth } from "./timing";

export const DECK_TOP = 6.5;
export const DECK_T = 0.8;
export const CAP_H = 0.9;
export const PILE_TOP = DECK_TOP - DECK_T - CAP_H;  // 4.8
export const BENT_STEP = 12;
export const PILE_X = [-14.2, -10.4, -6.2, -2.0, 2.0, 6.2, 10.4, 14.2];
export const PILE_R = 0.3;      // spun pile Ø600
export const P_RIN = 0.2;       // hollow core radius
export const P_RS = 0.245;      // prestressing strand circle radius
export const JOINT_Y = 0.35;    // welded segment joint sits in the tidal zone
export const SLICE_Y = 2.2;     // horizontal cross-section plane (lid lifts off here)
export const HERO = { x: -14.2, z: -240 };
export const GATE_Z = -900;
export const BEACH = { x: -112, z: -300 };
export const SHORE_X = BEACH.x + 6;
export const sandY = (x: number) => Math.max(-1.5, Math.min(1.1, (SHORE_X - x) * 0.12));
export const FENCE_X = BEACH.x - 4.4;
export const HERO_POST = { x: FENCE_X, z: BEACH.z + 1.8 };

// lanes (x centres) — left-hand traffic; west half drives -Z, east half +Z
export const LANES = { motorW: -13.3, carW: [-9.4, -6.0, -2.6], carE: [2.6, 6.0, 9.4], motorE: 13.3 };

export const AZ = Math.atan2(-2.2, 1.8);   // azimuth of the removed cutaway wedge (faces the camera side)
export const T40 = phraseTime("40", 130);
export const T80 = phraseTime("80", 135);

export type Cam = { pos: THREE.Vector3; target: THREE.Vector3; fov: number; aperture: number; near?: number };
const V = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);
const L = (a: THREE.Vector3, b: THREE.Vector3, k: number) => a.clone().lerp(b, k);
function shake(t: number, amp: number) {
  return V(Math.sin(t * 1.3) * 0.6 + Math.sin(t * 2.9) * 0.4, Math.sin(t * 1.7 + 1) * 0.5 + Math.sin(t * 3.7) * 0.3, Math.sin(t * 1.1 + 2) * 0.5).multiplyScalar(amp);
}
const orbit = (a: number, r: number, y: number) => V(HERO.x + Math.sin(a) * r, y, HERO.z + Math.cos(a) * r);

export function camera(t: number): Cam {
  const s = shotAt(t); const u = s.u; const e = smooth(u);
  switch (s.id) {
    case "S01": { // macro from the LAND side (sea + toll road blurred behind the post) -> slow pull-back + rack focus
      const k = smooth(ramp(u, 0.42, 1.0));
      const py = sandY(HERO_POST.x) + 0.95;
      const postPt = V(HERO_POST.x, py - 0.02, HERO_POST.z);
      const macroPos = V(HERO_POST.x - 0.46, py + 0.04, HERO_POST.z - 0.12).add(V(0, lerp(0.06, -0.04, ramp(u, 0, 0.42)), 0));
      const endPos = V(HERO_POST.x - 2.6, py + 0.8, HERO_POST.z - 0.9);
      const pos = L(macroPos, endPos, k);
      const d0 = postPt.clone().sub(macroPos).normalize();
      const d1 = V(0, 7, -360).sub(endPos).normalize();
      const dir = d0.clone().applyQuaternion(new THREE.Quaternion().slerp(new THREE.Quaternion().setFromUnitVectors(d0, d1), k));
      const focusDist = lerp(postPt.distanceTo(macroPos), 115, smooth(ramp(k, 0.15, 0.85)));
      const p2 = pos.add(shake(t, 0.003));
      return { pos: p2, target: p2.clone().add(dir.multiplyScalar(focusDist)), fov: lerp(30, 36, k), aperture: lerp(0.012, 0.0005, smooth(ramp(k, 0.1, 0.8))), near: lerp(0.03, 0.5, smooth(ramp(k, 0.0, 0.45))) };
    }
    case "S02": {
      const pos = L(V(-95, 46, 60), V(-36, 12, -188), e);
      const tgt = L(V(0, 4, -150), V(-6, 4.5, -262), e);
      return { pos: pos.add(shake(t, 0.12)), target: tgt, fov: 50, aperture: 0.000015 };
    }
    case "S03": { // approach the pile, then look down into the lifted cross-section (anatomy)
      const k = ramp(u, 0, 0.28);
      const far = V(HERO.x - 9, 3.2, HERO.z + 10);
      const nk = ramp(u, 0.28, 1);
      const near = orbit(lerp(AZ + 0.4, AZ + 0.12, nk), lerp(1.75, 1.45, nk), lerp(SLICE_Y + 1.15, SLICE_Y + 0.95, nk));
      return { pos: L(far, near, k).add(shake(t, 0.004)), target: L(V(HERO.x, 1.6, HERO.z), V(HERO.x, SLICE_Y + 0.12, HERO.z), k), fov: 42, aperture: lerp(0.0006, 0.0028, k) };
    }
    case "S04": { // chloride ingress / rust / spall on the section
      const a = lerp(AZ + 0.22, AZ - 0.08, e);
      return { pos: orbit(a, lerp(1.3, 1.1, e), lerp(SLICE_Y + 0.9, SLICE_Y + 0.72, e)).add(shake(t, 0.003)), target: V(HERO.x, SLICE_Y - 0.05, HERO.z), fov: 40, aperture: 0.003 };
    }
    case "S05": { // tidal zone (wide) -> welded joint close-up
      const k = ramp(u, 0.42, 0.62);
      const wide = orbit(lerp(AZ + 0.2, AZ - 0.1, e), 4.6, 1.4);
      const joint = orbit(AZ - 0.25, 1.3, 0.75);
      return { pos: L(wide, joint, k).add(shake(t, 0.006)), target: L(V(HERO.x, 0.3, HERO.z), V(HERO.x, 0.4, HERO.z), k), fov: 42, aperture: lerp(0.0012, 0.003, k) };
    }
    case "S06": { // HDPE clamshell closes on the joint, then coating
      const a = lerp(AZ - 0.25, AZ + 0.45, e);
      return { pos: orbit(a, lerp(2.5, 3.8, ramp(u, 0.5, 1)), lerp(1.0, 2.0, ramp(u, 0.5, 1))).add(shake(t, 0.005)), target: V(HERO.x, lerp(0.4, 1.4, ramp(u, 0.5, 1)), HERO.z), fov: 42, aperture: 0.0022 };
    }
    case "S07": {
      const pos = L(V(-19.5, DECK_TOP + 5.2, GATE_Z + 44), V(-18.5, DECK_TOP + 4.4, GATE_Z + 27), e);
      return { pos: pos.add(shake(t, 0.03)), target: V(-10.5, DECK_TOP + 2.2, GATE_Z - 2), fov: 50, aperture: 0.00006 };
    }
    default: { // S08 + end card
      const pos = L(V(-58, 26, -430), V(-150, 96, -320), e);
      return { pos, target: L(V(0, 5, -600), V(0, 0, -700), e), fov: 50, aperture: 0.00001 };
    }
  }
}

// --- animation beats shared by scene + overlay ---
export function windKmh(t: number) {
  const s = shotAt(t);
  if (s.id !== "S07") return 0;
  if (t < T40) return lerp(18, 40, smooth((t - s.t0) / (T40 - s.t0)));
  if (t < T80) return lerp(40, 80, smooth((t - T40) / (T80 - T40)));
  return 80 + (t - T80) * 0.8;
}
export const motorClosed = (t: number) => ramp(t, T40, T40 + 1.4);
export const carClosed = (t: number) => ramp(t, T80, T80 + 1.4);
export const tide = (t: number) => {
  const s = shotAt(t);
  return s.id === "S05" ? 0.55 * Math.sin((s.lt / 3.6) * Math.PI * 2) * (1 - ramp(s.u, 0.42, 0.6)) : 0;
};
