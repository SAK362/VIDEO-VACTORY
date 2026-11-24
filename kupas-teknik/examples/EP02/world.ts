import * as THREE from "three";
import { Water } from "three/examples/jsm/objects/Water.js";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import { staticFile } from "remotion";
import {
  AZ, SLICE_Y, SHORE_X, BEACH, BENT_STEP, CAP_H, DECK_T, DECK_TOP, FENCE_X, GATE_Z, HERO, HERO_POST, JOINT_Y, LANES, P_RIN, P_RS,
  PILE_R, PILE_TOP, PILE_X, carClosed, motorClosed, sandY, tide, windKmh,
} from "./layout";
import { lerp, ramp, shotAt } from "./timing";

// ---------- deterministic random ----------
let seed = 7;
const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };

// ---------- textures ----------
const tl = new THREE.TextureLoader();
const texCache: Record<string, THREE.Texture> = {};
const pending: Promise<void>[] = [];
export const texturesReady = () => Promise.all(pending).then(() => undefined);
function tex(file: string, rx: number, ry: number, srgb: boolean) {
  const k = `${file}|${rx}|${ry}`;
  if (!texCache[k]) {
    let done: () => void = () => {};
    pending.push(new Promise<void>((res) => { done = res; }));
    const t = tl.load(staticFile(file), () => done(), undefined, () => done());
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rx, ry); t.anisotropy = 8;
    t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
    texCache[k] = t;
  }
  return texCache[k];
}
function photo(prefix: string, rx: number, ry: number, color = new THREE.Color(1, 1, 1), extra: Partial<THREE.MeshStandardMaterialParameters> = {}) {
  const matte = prefix.includes("concrete");
  return new THREE.MeshStandardMaterial({
    map: tex(`tex/${prefix}_diff_2k.jpg`, rx, ry, true), normalMap: tex(`tex/${prefix}_nor_gl_2k.jpg`, rx, ry, false),
    roughnessMap: matte ? null : tex(`tex/${prefix}_rough_2k.jpg`, rx, ry, false), roughness: matte ? 0.92 : 1, color, ...extra,
  });
}
function canvasTex(w: number, h: number, draw: (g: CanvasRenderingContext2D) => void, srgb = true, rx = 1, ry = rx) {
  const c = document.createElement("canvas"); c.width = w; c.height = h; draw(c.getContext("2d")!);
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rx, ry);
  t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace; t.anisotropy = 8; return t;
}
function waterNormals() {
  const N = 512; const c = document.createElement("canvas"); c.width = c.height = N; const g = c.getContext("2d")!;
  const img = g.createImageData(N, N); const H = new Float32Array(N * N);
  const waves: [number, number, number, number][] = [];
  for (let i = 0; i < 34; i++) waves.push([1 + Math.floor(rnd() * 11), Math.floor(rnd() * 11) - 5, rnd() * 6.28, 1 / (1 + i * 0.3)]);
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    let h = 0; for (const [kx, ky, ph, a] of waves) h += a * Math.sin(((kx * x + ky * y) / N) * Math.PI * 2 + ph);
    H[y * N + x] = h;
  }
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    const dx = H[y * N + ((x + 1) % N)] - H[y * N + ((x - 1 + N) % N)];
    const dy = H[((y + 1) % N) * N + x] - H[((y - 1 + N) % N) * N + x];
    const n = new THREE.Vector3(-dx * 0.6, -dy * 0.6, 1).normalize();
    const i = (y * N + x) * 4; img.data[i] = (n.x * 0.5 + 0.5) * 255; img.data[i + 1] = (n.y * 0.5 + 0.5) * 255; img.data[i + 2] = (n.z * 0.5 + 0.5) * 255; img.data[i + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.NoColorSpace; return t;
}
const sandTex = () => canvasTex(512, 512, (g) => {
  g.fillStyle = "#cdbb94"; g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 60000; i++) { const v = 150 + rnd() * 80; g.fillStyle = `rgba(${v},${v - 18},${v - 50},${0.25 + rnd() * 0.4})`; g.fillRect(rnd() * 512, rnd() * 512, 1 + rnd() * 1.5, 1 + rnd() * 1.5); }
  for (let i = 0; i < 40; i++) { g.strokeStyle = `rgba(120,100,70,${0.05 + rnd() * 0.08})`; g.lineWidth = 2 + rnd() * 5; g.beginPath(); const y = rnd() * 512; g.moveTo(0, y); g.bezierCurveTo(170, y + rnd() * 30 - 15, 340, y + rnd() * 30 - 15, 512, y); g.stroke(); }
}, true, 12);
const rustTex = () => canvasTex(256, 512, (g) => {
  g.fillStyle = "#6b3416"; g.fillRect(0, 0, 256, 512);
  for (let i = 0; i < 900; i++) { const r = 2 + rnd() * 18; const c = rnd(); g.fillStyle = c < 0.45 ? `rgba(168,82,30,${0.25 + rnd() * 0.4})` : c < 0.8 ? `rgba(70,32,14,${0.25 + rnd() * 0.4})` : `rgba(196,120,60,${0.2 + rnd() * 0.3})`; g.beginPath(); g.ellipse(rnd() * 256, rnd() * 512, r, r * (0.5 + rnd()), rnd() * 3, 0, 6.3); g.fill(); }
  for (let i = 0; i < 3000; i++) { g.fillStyle = `rgba(30,14,6,${0.3 + rnd() * 0.5})`; g.fillRect(rnd() * 256, rnd() * 512, 1 + rnd() * 2, 1 + rnd() * 2); }
});
// macro post: weathered blue-grey paint peeling to rust — fractal-noise masks (irregular, not blobs)
function peelTex(): { map: THREE.Texture; bump: THREE.Texture } {
  const Wd = 256, Hd = 1024;
  const grid = (s: number) => { const n = Math.ceil(Wd / s) + 2, m = Math.ceil(Hd / s) + 2; return { n, m, v: Array.from({ length: n * m }, () => rnd()) }; };
  const octs = [96, 48, 24, 12, 6, 3].map((s) => ({ s, g: grid(s) }));
  const sm = (x: number) => x * x * (3 - 2 * x);
  const vnoise = (o: { s: number; g: { n: number; m: number; v: number[] } }, x: number, y: number) => {
    const fx = x / o.s, fy = y / o.s, ix = Math.floor(fx), iy = Math.floor(fy), tx = sm(fx - ix), ty = sm(fy - iy);
    const at = (i: number, j: number) => o.g.v[(j % o.g.m) * o.g.n + (i % o.g.n)];
    return (at(ix, iy) * (1 - tx) + at(ix + 1, iy) * tx) * (1 - ty) + (at(ix, iy + 1) * (1 - tx) + at(ix + 1, iy + 1) * tx) * ty;
  };
  const fbm = (x: number, y: number) => { let v = 0, a = 0.5, n = 0; for (const o of octs) { v += vnoise(o, x, y) * a; n += a; a *= 0.55; } return v / n; };
  const N = new Float32Array(Wd * Hd), N2 = new Float32Array(Wd * Hd);
  for (let y = 0; y < Hd; y++) for (let x = 0; x < Wd; x++) { N[y * Wd + x] = fbm(x, y); N2[y * Wd + x] = fbm(x + 500, y + 300); }
  const mk = (fn: (i: number, x: number, y: number) => [number, number, number]) => {
    const c = document.createElement("canvas"); c.width = Wd; c.height = Hd; const g = c.getContext("2d")!; const img = g.createImageData(Wd, Hd);
    for (let y = 0; y < Hd; y++) for (let x = 0; x < Wd; x++) { const i = y * Wd + x; const [r, gg, b] = fn(i, x, y); img.data[i * 4] = r; img.data[i * 4 + 1] = gg; img.data[i * 4 + 2] = b; img.data[i * 4 + 3] = 255; }
    g.putImageData(img, 0, 0); return c;
  };
  // rust grows where noise is high, more toward the bottom (splash) of the post
  const thr = (y: number) => 0.56 - (y / Hd) * 0.12;
  const pits: number[] = []; for (let i = 0; i < 1400; i++) pits.push(Math.floor(rnd() * Wd * Hd));
  const pitSet = new Set(pits);
  const colC = mk((i, x, y) => {
    const n = N[i], t = thr(y), d = n - t;
    const grime = 0.85 + N2[i] * 0.25;
    if (d < -0.012) { // intact paint (weathered)
      const r = 92 * grime, g = 114 * grime, b = 126 * grime;
      return [r, g, b];
    }
    if (d < 0.0) return [205, 200, 188]; // lifted paint edge
    const k = Math.min(1, d / 0.06), v = N2[i], m = N[(i * 7) % N.length];
    let r = 128 - k * 62 + v * 46 - m * 20, g = 58 - k * 30 + v * 22 - m * 10, b = 22 - k * 10 + v * 8;
    if (pitSet.has(i) || pitSet.has(i + 1) || pitSet.has(i + Wd)) { r *= 0.35; g *= 0.3; b *= 0.3; }
    return [r, g, b];
  });
  // rust streaks running down from rust patches
  const g2 = colC.getContext("2d")!;
  for (let i = 0; i < 70; i++) { const x = rnd() * Wd, y = rnd() * Hd * 0.85; const gr = g2.createLinearGradient(x, y, x, y + 60 + rnd() * 140); gr.addColorStop(0, "rgba(130,58,22,0.35)"); gr.addColorStop(1, "rgba(130,58,22,0)"); g2.fillStyle = gr; g2.fillRect(x - 1.5 - rnd() * 2, y, 3 + rnd() * 4, 200); }
  const bumpC = mk((i, x, y) => { const d = N[i] - thr(y); const v = d < -0.012 ? 170 : d < 0 ? 215 : 90 - Math.min(1, d / 0.08) * 40 + N2[i] * 30; const p = pitSet.has(i) ? 20 : v; return [p, p, p]; });
  const map = new THREE.CanvasTexture(colC); map.colorSpace = THREE.SRGBColorSpace; map.anisotropy = 8;
  const bump = new THREE.CanvasTexture(bumpC); bump.colorSpace = THREE.NoColorSpace;
  for (const t of [map, bump]) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(1, 3.5); } // post face is 0.09 x 1.25 m -> keep texels square
  return { map, bump };
}
const foamTex = () => canvasTex(256, 256, (g) => {
  const c = 128;
  for (let i = 0; i < 2600; i++) {
    const a = rnd() * 6.283; const r = 30 + Math.pow(rnd(), 1.8) * 95; const s = 1 + rnd() * 4;
    g.fillStyle = `rgba(255,255,255,${(1 - (r - 30) / 95) * (0.25 + rnd() * 0.5)})`; g.beginPath(); g.arc(c + Math.cos(a) * r, c + Math.sin(a) * r, s, 0, 6.3); g.fill();
  }
});
const hazardTex = () => canvasTex(256, 64, (g) => { for (let i = -2; i < 10; i++) { g.fillStyle = i % 2 ? "#141414" : "#f2c200"; g.beginPath(); g.moveTo(i * 32, 64); g.lineTo(i * 32 + 32, 64); g.lineTo(i * 32 + 64, 0); g.lineTo(i * 32 + 32, 0); g.fill(); } }, true, 4, 1);
const signTex = (txt: string, sub: string) => canvasTex(1024, 128, (g) => {
  g.fillStyle = "#0d4f8c"; g.fillRect(0, 0, 1024, 128); g.fillStyle = "#ffffff";
  g.font = "bold 64px Bahnschrift, 'Segoe UI', sans-serif"; g.textBaseline = "middle"; g.fillText(txt, 40, 64);
  g.font = "bold 40px 'Segoe UI', sans-serif"; g.textAlign = "right"; g.fillText(sub, 990, 64);
});

export type World = { scene: THREE.Group; water: Water; update: (t: number) => void };

export function buildWorld(emblem: THREE.Texture, wmark: THREE.Texture): World {
  seed = 7;
  const root = new THREE.Group();
  const M = {
    pile: photo("brushed_concrete", 1, 2, new THREE.Color(1.35, 1.33, 1.27)),
    deck: photo("concrete_wall_008", 4, 4, new THREE.Color(1.1, 1.08, 1.03)),
    cap: photo("brushed_concrete", 4, 1, new THREE.Color(1.15, 1.13, 1.08)),
    asphalt: photo("asphalt_02", 6, 6, new THREE.Color(1.55, 1.55, 1.55)),
    paint: new THREE.MeshStandardMaterial({ color: new THREE.Color(0.85, 0.85, 0.8), roughness: 0.7 }),
    yellow: new THREE.MeshStandardMaterial({ color: new THREE.Color(0.8, 0.6, 0.1), roughness: 0.7 }),
    barrier: photo("concrete_pavement", 2, 1, new THREE.Color(1.25, 1.24, 1.2)),
    rail: new THREE.MeshStandardMaterial({ color: new THREE.Color(0.62, 0.63, 0.65), metalness: 1, roughness: 0.35 }),
    rust: new THREE.MeshStandardMaterial({ map: rustTex(), normalMap: tex("tex/rusty_metal_02_nor_gl_2k.jpg", 0.5, 2, false), roughness: 0.9, metalness: 0.05 }),
    sand: new THREE.MeshStandardMaterial({ map: sandTex(), roughness: 0.95 }),
    glass: new THREE.MeshPhysicalMaterial({ color: new THREE.Color(0.02, 0.03, 0.035), metalness: 0.2, roughness: 0.04, clearcoat: 1, clearcoatRoughness: 0.03 }),
    tire: new THREE.MeshStandardMaterial({ color: new THREE.Color(0.035, 0.035, 0.035), roughness: 0.82 }),
    rim: new THREE.MeshStandardMaterial({ color: new THREE.Color(0.7, 0.71, 0.73), metalness: 1, roughness: 0.28 }),
    green: new THREE.MeshStandardMaterial({ color: new THREE.Color(0.09, 0.17, 0.07), roughness: 0.95 }),
    algae: new THREE.MeshStandardMaterial({ color: new THREE.Color(0.17, 0.21, 0.12), roughness: 0.9, transparent: true, opacity: 0.8 }),
    head: new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xfff6e0, emissiveIntensity: 1.2, roughness: 0.1 }),
    tail: new THREE.MeshStandardMaterial({ color: 0x8a0000, emissive: 0xff1010, emissiveIntensity: 0.8, roughness: 0.2 }),
    steel: new THREE.MeshStandardMaterial({ color: new THREE.Color(0.5, 0.51, 0.53), metalness: 0.95, roughness: 0.38 }),
  };
  const shadowAll = (o: THREE.Object3D) => o.traverse((m) => { if ((m as THREE.Mesh).isMesh) { m.castShadow = true; m.receiveShadow = true; } });
  const tmp = new THREE.Object3D();

  // ---------- sea (Teluk Benoa: calm, green-teal) ----------
  const water = new Water(new THREE.PlaneGeometry(6000, 6000), {
    textureWidth: 1024, textureHeight: 1024, waterNormals: waterNormals(),
    sunDirection: new THREE.Vector3(0.2835, 0.5592, 0.779).normalize(), sunColor: 0xfff2dc, waterColor: 0x0e6a5e, distortionScale: 0.9, fog: true,
  });
  water.rotation.x = -Math.PI / 2; water.material.uniforms["size"].value = 1.6;
  root.add(water);

  // ---------- viaduct ----------
  const Z0 = 120, Z1 = -1500, LEN = Z0 - Z1, ZC = (Z0 + Z1) / 2;
  const deck = new THREE.Mesh(new THREE.BoxGeometry(31, DECK_T, LEN), M.deck); deck.position.set(0, DECK_TOP - DECK_T / 2 - 0.08, ZC);
  const road = new THREE.Mesh(new THREE.BoxGeometry(30.4, 0.08, LEN), M.asphalt); road.position.set(0, DECK_TOP - 0.04, ZC);
  for (const k of ["map", "normalMap"] as const) (M.asphalt[k] as THREE.Texture).repeat.set(30.4 / 4, LEN / 4);
  root.add(deck, road);
  for (const x of [-15.35, -11.65, -0.35, 0.35, 11.65, 15.35]) { const b = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.95, LEN), M.barrier); b.position.set(x, DECK_TOP + 0.47, ZC); root.add(b); }
  for (const x of [-15.35, 15.35]) { const r = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.08, LEN), M.rail); r.position.set(x, DECK_TOP + 1.3, ZC); root.add(r); }
  const nd = Math.floor(LEN / 9); const dashXs = [-7.7, -4.3, 4.3, 7.7];
  const dashes = new THREE.InstancedMesh(new THREE.BoxGeometry(0.15, 0.02, 3), M.paint, dashXs.length * nd); let di = 0;
  for (const x of dashXs) for (let i = 0; i < nd; i++) { tmp.position.set(x, DECK_TOP + 0.01, Z0 - i * 9); tmp.rotation.set(0, 0, 0); tmp.scale.set(1, 1, 1); tmp.updateMatrix(); dashes.setMatrixAt(di++, tmp.matrix); }
  root.add(dashes);
  for (const x of [-11.1, -0.9, 0.9, 11.1]) { const e = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.02, LEN), Math.abs(x) < 2 ? M.yellow : M.paint); e.position.set(x, DECK_TOP + 0.01, ZC); root.add(e); }
  const nb = Math.floor(LEN / BENT_STEP);
  const caps = new THREE.InstancedMesh(new THREE.BoxGeometry(31, CAP_H, 1.2), M.cap, nb);
  const pileGeo = new THREE.CylinderGeometry(PILE_R, PILE_R, PILE_TOP + 6, 24); pileGeo.translate(0, (PILE_TOP - 6) / 2, 0);
  const piles = new THREE.InstancedMesh(pileGeo, M.pile, nb * PILE_X.length);
  const algae = new THREE.InstancedMesh(new THREE.CylinderGeometry(PILE_R + 0.008, PILE_R + 0.008, 1.1, 24, 1, true), M.algae, nb * PILE_X.length);
  const bandGeo = new THREE.CylinderGeometry(PILE_R + 0.003, PILE_R + 0.003, 0.1, 24, 1, true);
  const joints = new THREE.InstancedMesh(bandGeo, M.steel, nb * PILE_X.length);
  const foamMat = new THREE.MeshBasicMaterial({ map: foamTex(), transparent: true, depthWrite: false, opacity: 0.85 });
  const foam = new THREE.InstancedMesh(new THREE.RingGeometry(PILE_R + 0.005, 0.78, 40, 2).rotateX(-Math.PI / 2), foamMat, nb * PILE_X.length);
  let pi = 0;
  for (let i = 0; i < nb; i++) {
    const z = Z0 - i * BENT_STEP;
    tmp.position.set(0, PILE_TOP + CAP_H / 2, z); tmp.rotation.set(0, 0, 0); tmp.scale.set(1, 1, 1); tmp.updateMatrix(); caps.setMatrixAt(i, tmp.matrix);
    for (const x of PILE_X) {
      const isHero = Math.abs(x - HERO.x) < 0.01 && Math.abs(z - HERO.z) < 0.01;
      const s = isHero ? 0.0001 : 1;
      tmp.position.set(x, 0, z); tmp.scale.setScalar(s); tmp.rotation.set(0, rnd() * 6.28, 0); tmp.updateMatrix(); piles.setMatrixAt(pi, tmp.matrix);
      tmp.position.set(x, -0.05, z); tmp.updateMatrix(); algae.setMatrixAt(pi, tmp.matrix);
      tmp.position.set(x, JOINT_Y + (rnd() - 0.5) * 0.4, z); tmp.updateMatrix(); joints.setMatrixAt(pi, tmp.matrix);
      tmp.position.set(x, 0.015, z); tmp.scale.set(0.8 + rnd() * 0.5, 1, 0.8 + rnd() * 0.5); tmp.rotation.set(0, rnd() * 6.28, 0); tmp.updateMatrix(); foam.setMatrixAt(pi, tmp.matrix);
      pi++;
    }
  }
  root.add(caps, piles, algae, joints, foam);
  foam.renderOrder = 2; foamMat.polygonOffset = true; foamMat.polygonOffsetFactor = -2;
  const waterBefore = water.onBeforeRender.bind(water);
  water.onBeforeRender = (...args: Parameters<typeof water.onBeforeRender>) => { const v = foam.visible; foam.visible = false; waterBefore(...args); foam.visible = v; };
  const lampGeo = new THREE.CylinderGeometry(0.08, 0.1, 9, 10); const armGeo = new THREE.BoxGeometry(1.6, 0.1, 0.12);
  const lampHead = new THREE.BoxGeometry(0.7, 0.14, 0.3);
  for (let z = Z0; z > Z1; z -= 40) for (const s of [-1, 1]) {
    if (Math.abs(z - GATE_Z) < 70) continue;
    const p = new THREE.Mesh(lampGeo, M.rail); p.position.set(s * 15.6, DECK_TOP + 4.5, z); root.add(p);
    const a = new THREE.Mesh(armGeo, M.rail); a.position.set(s * 14.9, DECK_TOP + 8.95, z); root.add(a);
    const h = new THREE.Mesh(lampHead, M.rail); h.position.set(s * 14.2, DECK_TOP + 8.86, z); root.add(h);
  }
  // distant coast (mangrove / Nusa Dua)
  for (let i = 0; i < 26; i++) {
    const x = (rnd() < 0.5 ? -1 : 1) * (500 + rnd() * 900), z = -200 - rnd() * 1600;
    const w = 80 + rnd() * 220, h = 4 + rnd() * 14;
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, 40 + rnd() * 120), M.green); m.position.set(x, h / 2 - 1, z); root.add(m);
    if (rnd() < 0.5) { const bh = 10 + rnd() * 30; const b = new THREE.Mesh(new THREE.BoxGeometry(20 + rnd() * 30, bh, 20 + rnd() * 30), new THREE.MeshStandardMaterial({ color: new THREE.Color(0.8, 0.79, 0.76), roughness: 0.8 })); b.position.set(x + rnd() * 40, bh / 2, z + rnd() * 30); root.add(b); }
  }

  // ---------- beach set (S01) ----------
  const beach = new THREE.Group();
  const sandGeo = new THREE.PlaneGeometry(220, 160, 110, 80); sandGeo.rotateX(-Math.PI / 2);
  const sp = sandGeo.attributes.position as THREE.BufferAttribute;
  for (let i = 0; i < sp.count; i++) { const x = sp.getX(i) + BEACH.x - 100; sp.setY(i, sandY(x) + Math.sin(sp.getZ(i) * 0.15) * 0.04); }
  sandGeo.computeVertexNormals();
  const sand = new THREE.Mesh(sandGeo, M.sand); sand.position.set(BEACH.x - 100, 0, BEACH.z); beach.add(sand);
  const shoreTex = canvasTex(64, 512, (g) => { const gr = g.createLinearGradient(0, 0, 64, 0); gr.addColorStop(0, "rgba(120,104,80,0)"); gr.addColorStop(0.45, "rgba(110,95,72,0.55)"); gr.addColorStop(0.7, "rgba(240,245,245,0.85)"); gr.addColorStop(1, "rgba(240,245,245,0)"); g.fillStyle = gr; g.fillRect(0, 0, 64, 512); for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(255,255,255,${rnd() * 0.5})`; g.fillRect(36 + rnd() * 26, rnd() * 512, 2, 2); } }, true, 1, 8);
  const shore = new THREE.Mesh(new THREE.PlaneGeometry(6, 160).rotateX(-Math.PI / 2), new THREE.MeshStandardMaterial({ map: shoreTex, transparent: true, depthWrite: false, roughness: 0.6, polygonOffset: true, polygonOffsetFactor: -2 }));
  shore.position.set(SHORE_X - 0.6, 0.03, BEACH.z); beach.add(shore);
  const fence = new THREE.Group();
  for (let i = 0; i < 11; i++) {
    const z = BEACH.z + 3 - i * 1.2; if (Math.abs(z - HERO_POST.z) < 0.3) continue;
    const post = new THREE.Mesh(new THREE.BoxGeometry(0.09, 1.25, 0.09), M.rust);
    post.position.set(FENCE_X + Math.sin(i) * 0.03, sandY(FENCE_X) + 0.55, z); post.rotation.z = (rnd() - 0.5) * 0.06; fence.add(post);
  }
  for (const y of [0.55, 1.25]) { const r = new THREE.Mesh(new THREE.BoxGeometry(0.045, 0.045, 13), M.rust); r.position.set(FENCE_X + 0.05, sandY(FENCE_X) + y - 0.05, BEACH.z - 3.4); fence.add(r); }
  // hero macro post: displaced paint + rust, curled paint flakes
  const pt = peelTex();
  const heroPostMat = new THREE.MeshStandardMaterial({ map: pt.map, bumpMap: pt.bump, bumpScale: 5.0, displacementMap: pt.bump, displacementScale: 0.0025, displacementBias: -0.0015, roughness: 0.8, metalness: 0.08 });
  const heroPost = new THREE.Mesh(new THREE.BoxGeometry(0.09, 1.25, 0.09, 24, 320, 24), heroPostMat);
  heroPost.position.set(HERO_POST.x, sandY(HERO_POST.x) + 0.55, HERO_POST.z); fence.add(heroPost);
  const flakeMat = new THREE.MeshStandardMaterial({ color: 0x5c707c, roughness: 0.7, side: THREE.DoubleSide });
  for (let i = 0; i < 12; i++) {
    const g = new THREE.PlaneGeometry(0.006 + rnd() * 0.01, 0.005 + rnd() * 0.01, 4, 4);
    const ps = g.attributes.position as THREE.BufferAttribute;
    for (let k = 0; k < ps.count; k++) ps.setZ(k, Math.pow(ps.getX(k) * 60, 2) * 0.004 + rnd() * 0.0008);
    const f = new THREE.Mesh(g, flakeMat);
    const side = rnd() < 0.6 ? 1 : 0;
    f.position.set(HERO_POST.x + (side ? -0.0465 : (rnd() - 0.5) * 0.08), heroPost.position.y + (rnd() - 0.2) * 0.5, HERO_POST.z + (side ? (rnd() - 0.5) * 0.08 : -0.0465));
    f.rotation.set((rnd() - 0.5) * 0.6, side ? Math.PI / 2 : 0, (rnd() - 0.5) * 0.8); fence.add(f);
  }
  beach.add(fence);
  for (let i = 0; i < 14; i++) { // rocks
    const g = new THREE.IcosahedronGeometry(0.15 + rnd() * 0.35, 2); const ps = g.attributes.position as THREE.BufferAttribute;
    for (let k = 0; k < ps.count; k++) ps.setXYZ(k, ps.getX(k) * (0.8 + rnd() * 0.4), ps.getY(k) * (0.5 + rnd() * 0.3), ps.getZ(k) * (0.8 + rnd() * 0.4));
    g.computeVertexNormals();
    const r = new THREE.Mesh(g, photo("concrete_pavement", 0.3, 0.3, new THREE.Color(0.75, 0.7, 0.62)));
    const x = FENCE_X + 2 + rnd() * 9; r.position.set(x, sandY(x) + 0.02, BEACH.z - 6 + rnd() * 14); beach.add(r);
  }
  root.add(beach);

  // ---------- hero pile: detailed spun-pile cutaway (S03–S06) ----------
  // vertical 90° wedge cut (faces camera side) + horizontal section at SLICE_Y where the "lid" lifts off
  const hero = new THREE.Group(); hero.position.set(HERO.x, 0, HERO.z);
  const R0 = P_RIN, R1 = PILE_R, Y0 = -3, Y1 = PILE_TOP, PT = 0.018, SY = SLICE_Y;
  const ph0 = AZ + Math.PI / 4, phL = Math.PI * 1.5, ph1 = ph0 + phL;
  const lathe = (r0: number, r1: number, y0: number, y1: number, a0: number, aL: number, seg = 64) =>
    new THREE.LatheGeometry([new THREE.Vector2(r0, y0), new THREE.Vector2(r1, y0), new THREE.Vector2(r1, y1), new THREE.Vector2(r0, y1), new THREE.Vector2(r0, y0)], seg, a0, aL);
  const heroMat = photo("brushed_concrete", 1, 3, new THREE.Color(1.35, 1.33, 1.27), { side: THREE.DoubleSide });
  const sectMat = new THREE.MeshStandardMaterial({ map: tex("tex/concrete_pavement_diff_2k.jpg", 0.35, 0.35, true), color: new THREE.Color(1.3, 1.26, 1.18), roughness: 0.95, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: 1 });
  const faceMat = new THREE.MeshStandardMaterial({ map: tex("tex/concrete_pavement_diff_2k.jpg", 0.25, 1.5, true), color: new THREE.Color(1.22, 1.18, 1.1), roughness: 0.95, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: 1 });
  const capFace = (ph: number, r0: number, r1: number, y0: number, y1: number, mat: THREE.Material) => {
    const g = new THREE.PlaneGeometry(r1 - r0, y1 - y0); g.translate((r0 + r1) / 2, (y0 + y1) / 2, 0);
    const m = new THREE.Mesh(g, mat); m.rotation.y = ph - Math.PI / 2; return m;
  };
  const ring = (r0: number, r1: number, y: number, a0: number, aL: number, mat: THREE.Material) => {
    const g = new THREE.RingGeometry(r0, r1, 64, 1, a0 - Math.PI / 2, aL); g.rotateX(-Math.PI / 2); g.translate(0, y, 0); return new THREE.Mesh(g, mat);
  };
  const CH_A = 0.5, CY0 = SY - 0.42, RC = P_RS + 0.014;
  // lower segment (below welded joint)
  hero.add(new THREE.Mesh(lathe(R0, R1, Y0, JOINT_Y - PT, ph0, phL), heroMat));
  hero.add(capFace(ph0, R0, R1, Y0, JOINT_Y - PT, faceMat), capFace(ph1, R0, R1, Y0, JOINT_Y - PT, faceMat));
  // upper segment up to the section plane, with a removable spall chunk at its top edge
  hero.add(new THREE.Mesh(lathe(R0, R1, JOINT_Y + PT, SY, ph0 + CH_A, phL - CH_A), heroMat));
  hero.add(new THREE.Mesh(lathe(R0, R1, JOINT_Y + PT, CY0, ph0, CH_A, 16), heroMat));
  hero.add(new THREE.Mesh(lathe(R0, RC, CY0, SY, ph0, CH_A, 16), heroMat));
  hero.add(capFace(ph1, R0, R1, JOINT_Y + PT, SY, faceMat), capFace(ph0, R0, R1, JOINT_Y + PT, CY0, faceMat), capFace(ph0, R0, RC, CY0, SY, faceMat));
  hero.add(ring(R0, R1, SY, ph0 + CH_A, phL - CH_A, sectMat), ring(R0, RC, SY, ph0, CH_A, sectMat));
  const chunk = new THREE.Group();
  chunk.add(new THREE.Mesh(lathe(RC, R1, CY0, SY, ph0, CH_A, 16), heroMat));
  chunk.add(capFace(ph0, RC, R1, CY0, SY, faceMat), capFace(ph0 + CH_A, RC, R1, CY0, SY, faceMat), ring(RC, R1, SY, ph0, CH_A, sectMat));
  hero.add(chunk);
  // lid (above section plane) lifts off to reveal the cross-section
  const lid = new THREE.Group(); hero.add(lid);
  lid.add(new THREE.Mesh(lathe(R0, R1, SY, Y1, ph0, phL), heroMat));
  lid.add(capFace(ph0, R0, R1, SY, Y1, faceMat), capFace(ph1, R0, R1, SY, Y1, faceMat), ring(R0, R1, SY, ph0, phL, sectMat));
  // welded steel end plates + outer steel band + weld bead
  const plateMat = new THREE.MeshStandardMaterial({ color: new THREE.Color(0.45, 0.46, 0.48), metalness: 0.9, roughness: 0.42, side: THREE.DoubleSide });
  hero.add(new THREE.Mesh(lathe(R0, R1 + 0.002, JOINT_Y - PT, JOINT_Y + PT, ph0, phL), plateMat));
  hero.add(new THREE.Mesh(new THREE.CylinderGeometry(R1 + 0.003, R1 + 0.003, 0.12, 64, 1, true, ph0, phL), plateMat));
  const beadPts: THREE.Vector3[] = []; for (let i = 0; i <= 96; i++) { const a = ph0 + (phL * i) / 96; beadPts.push(new THREE.Vector3(Math.sin(a) * (R1 + 0.006), JOINT_Y, Math.cos(a) * (R1 + 0.006))); }
  hero.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(beadPts), 192, 0.007, 8, false), new THREE.MeshStandardMaterial({ color: 0x3a3632, metalness: 0.7, roughness: 0.6 })));
  // prestressing strands: lower part to the section plane, upper part rides with the lid
  const strandMat = new THREE.MeshStandardMaterial({ color: new THREE.Color(0.62, 0.63, 0.65), metalness: 0.95, roughness: 0.28 });
  const strandAngles = [ph0 + 0.0001, ph1 - 0.0001]; for (let i = 1; i < 10; i++) strandAngles.push(ph0 + (phL * i) / 10);
  const strands: THREE.Mesh[] = [];
  for (const a of strandAngles) {
    const lo = new THREE.Mesh(new THREE.CylinderGeometry(0.0085, 0.0085, SY - Y0, 12), strandMat); lo.position.set(Math.sin(a) * P_RS, (Y0 + SY) / 2, Math.cos(a) * P_RS); hero.add(lo); strands.push(lo);
    const hi = new THREE.Mesh(new THREE.CylinderGeometry(0.0085, 0.0085, Y1 - SY, 12), strandMat); hi.position.set(Math.sin(a) * P_RS, (SY + Y1) / 2, Math.cos(a) * P_RS); lid.add(hi); strands.push(hi);
  }
  const spiralMat = new THREE.MeshStandardMaterial({ color: new THREE.Color(0.55, 0.55, 0.57), metalness: 0.9, roughness: 0.38 });
  const helix = (yA: number, yB: number) => {
    const pts: THREE.Vector3[] = []; const n = Math.floor(((yB - yA) / 0.07) * 40);
    for (let i = 0; i <= n; i++) { const y = yA + ((yB - yA) * i) / n; const a = (y / 0.07) * Math.PI * 2; pts.push(new THREE.Vector3(Math.sin(a) * (P_RS + 0.012), y, Math.cos(a) * (P_RS + 0.012))); }
    return new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), n, 0.003, 6, false), spiralMat);
  };
  hero.add(helix(-1.2, SY)); lid.add(helix(SY, 3.6));
  // chloride ingress on the section (blue ring creeping inward) + ions + rust blooms + radial cracks
  const chlMat = new THREE.MeshBasicMaterial({ color: 0x2f9bff, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -3 });
  const chl = ring(R1 - 0.001, R1, SY + 0.002, ph0 + CH_A, phL - CH_A, chlMat); hero.add(chl);
  const NI = 140; const ions = new THREE.InstancedMesh(new THREE.SphereGeometry(0.0042, 8, 6), new THREE.MeshStandardMaterial({ color: 0x55c2ff, emissive: 0x1677c9, emissiveIntensity: 1.3, roughness: 0.3 }), NI);
  const ionSeed = Array.from({ length: NI }, () => [ph0 + CH_A + rnd() * (phL - CH_A), rnd(), rnd()]);
  hero.add(ions);
  const rustDiscMat = new THREE.MeshStandardMaterial({ map: rustTex(), color: new THREE.Color(1, 0.8, 0.7), roughness: 0.95, transparent: true, opacity: 0, polygonOffset: true, polygonOffsetFactor: -4, side: THREE.DoubleSide });
  const crackMat = new THREE.MeshBasicMaterial({ color: 0x1a1816, transparent: true, opacity: 0, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -5 });
  const rustDiscs: THREE.Mesh[] = [];
  for (const a of strandAngles) {
    const d = new THREE.Mesh(new THREE.CircleGeometry(1, 24).rotateX(-Math.PI / 2), rustDiscMat); d.position.set(Math.sin(a) * P_RS, SY + 0.003, Math.cos(a) * P_RS); hero.add(d); rustDiscs.push(d);
    const len = R1 - P_RS; const c = new THREE.Mesh(new THREE.BoxGeometry(0.0035, 0.002, len), crackMat);
    const aa = a + (rnd() - 0.5) * 0.12; c.position.set(Math.sin(aa) * (P_RS + len / 2), SY + 0.004, Math.cos(aa) * (P_RS + len / 2)); c.rotation.y = aa; hero.add(c);
  }
  // tide-zone highlight
  const band = new THREE.Mesh(new THREE.CylinderGeometry(R1 + 0.012, R1 + 0.012, 1.2, 64, 1, true, ph0, phL), new THREE.MeshBasicMaterial({ color: 0xff9a1f, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide }));
  hero.add(band);
  // HDPE clamshell jacket (two halves, hinged) + stainless straps
  const hdpe = new THREE.MeshPhysicalMaterial({ color: new THREE.Color(0.05, 0.05, 0.055), roughness: 0.34, clearcoat: 0.5, clearcoatRoughness: 0.35, side: THREE.DoubleSide });
  const JH = 1.7, JR0 = R1 + 0.012, JR1 = R1 + 0.032;
  const halfBack = new THREE.Mesh(lathe(JR0, JR1, JOINT_Y - JH / 2, JOINT_Y + JH / 2, AZ + Math.PI / 2, Math.PI, 48), hdpe);
  const hingeA = AZ - Math.PI / 2; const hinge = new THREE.Group(); hinge.position.set(Math.sin(hingeA) * JR1, 0, Math.cos(hingeA) * JR1);
  const halfFront = new THREE.Mesh(lathe(JR0, JR1, JOINT_Y - JH / 2, JOINT_Y + JH / 2, AZ - Math.PI / 2, Math.PI, 48), hdpe);
  halfFront.position.set(-hinge.position.x, 0, -hinge.position.z); hinge.add(halfFront);
  const jacket = new THREE.Group(); jacket.add(halfBack, hinge); hero.add(jacket);
  const straps: THREE.Mesh[] = [];
  for (const dy of [-0.62, 0, 0.62]) { const s = new THREE.Mesh(new THREE.TorusGeometry(JR1 + 0.004, 0.006, 6, 64), new THREE.MeshStandardMaterial({ color: 0xc9ccd0, metalness: 1, roughness: 0.25 })); s.rotation.x = Math.PI / 2; s.position.y = JOINT_Y + dy; jacket.add(s); straps.push(s); }
  const coatMat = new THREE.MeshPhysicalMaterial({ color: new THREE.Color(0.38, 0.5, 0.6), roughness: 0.12, clearcoat: 1, clearcoatRoughness: 0.08, transparent: true, opacity: 0.55, side: THREE.DoubleSide });
  const coatTop = JOINT_Y + JH / 2 + 0.02;
  const coat = new THREE.Mesh(new THREE.CylinderGeometry(R1 + 0.004, R1 + 0.004, 1, 64, 1, true, ph0, phL), coatMat); hero.add(coat);
  shadowAll(hero);
  [chl, band].forEach((m) => { m.castShadow = false; });
  root.add(hero);

  // ---------- vehicles ----------
  const carCols = [0xa31212, 0xe8e8e6, 0x101114, 0x3e4852, 0x9da2a8, 0x1c3d78, 0x5b5f63];
  const wheel = (r: number, w: number) => {
    const g = new THREE.Group();
    const t = new THREE.Mesh(new THREE.TorusGeometry(r - 0.07, 0.07, 10, 24), M.tire); t.rotation.y = Math.PI / 2; g.add(t);
    const rim = new THREE.Mesh(new THREE.CylinderGeometry(r - 0.09, r - 0.09, w, 18), M.rim); rim.rotation.z = Math.PI / 2; g.add(rim);
    return g;
  };
  function car(col: number) {
    const g = new THREE.Group();
    const paint = new THREE.MeshPhysicalMaterial({ color: col, metalness: 0.55, roughness: 0.38, clearcoat: 1, clearcoatRoughness: 0.05 });
    const body = new THREE.Shape();
    body.moveTo(-2.2, 0.3); body.lineTo(-2.22, 0.62); body.quadraticCurveTo(-2.18, 0.82, -1.85, 0.86); body.lineTo(-0.72, 0.95); body.lineTo(1.9, 0.99);
    body.quadraticCurveTo(2.2, 0.98, 2.22, 0.7); body.lineTo(2.2, 0.32); body.lineTo(1.75, 0.3); body.absarc(1.4, 0.3, 0.38, 0, Math.PI, false);
    body.lineTo(-0.95, 0.3); body.absarc(-1.3, 0.3, 0.38, 0, Math.PI, false); body.lineTo(-2.2, 0.3);
    const bg = new THREE.ExtrudeGeometry(body, { depth: 1.56, bevelEnabled: true, bevelThickness: 0.09, bevelSize: 0.06, bevelSegments: 4, curveSegments: 14 });
    bg.translate(0, 0, -0.78); bg.rotateY(-Math.PI / 2);
    g.add(new THREE.Mesh(bg, paint));
    const cab = new THREE.Shape(); cab.moveTo(-0.72, 0.95); cab.lineTo(-0.08, 1.37); cab.lineTo(1.02, 1.39); cab.lineTo(1.86, 0.99); cab.lineTo(-0.72, 0.95);
    const cg = new THREE.ExtrudeGeometry(cab, { depth: 1.42, bevelEnabled: true, bevelThickness: 0.04, bevelSize: 0.03, bevelSegments: 2 }); cg.translate(0, 0, -0.71); cg.rotateY(-Math.PI / 2);
    g.add(new THREE.Mesh(cg, M.glass));
    const roof = new THREE.Mesh(new RoundedBoxGeometry(1.42, 0.05, 1.12, 2, 0.02), paint); roof.position.set(0, 1.4, 0.47); g.add(roof);
    for (const z of [-0.45, 0.45 + 0.02]) { const pil = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.42, 0.06), paint); pil.position.set(0, 1.17, z * 0); void pil; }
    for (const x of [-0.84, 0.84]) for (const z of [-1.3, 1.4]) { const w = wheel(0.34, 0.2); w.position.set(x, 0.34, z); g.add(w); }
    for (const x of [-0.62, 0.62]) { const h = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.08, 0.04), M.head); h.position.set(x, 0.72, -2.25); g.add(h); const t = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.08, 0.04), M.tail); t.position.set(x, 0.82, 2.25); g.add(t); }
    for (const x of [-0.98, 0.98]) { const m = new THREE.Mesh(new RoundedBoxGeometry(0.1, 0.1, 0.18, 2, 0.03), paint); m.position.set(x, 1.0, -0.6); g.add(m); }
    shadowAll(g); return g;
  }
  function bike() {
    const g = new THREE.Group();
    const col = [0x111111, 0xb30f0f, 0xdddddd, 0x1a3f8a][Math.floor(rnd() * 4)];
    const paint = new THREE.MeshPhysicalMaterial({ color: col, metalness: 0.3, roughness: 0.35, clearcoat: 1, clearcoatRoughness: 0.08 });
    for (const z of [-0.66, 0.66]) { const w = wheel(0.3, 0.07); w.position.set(0, 0.3, z); g.add(w); }
    const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.17, 0.95, 6, 12), paint); body.rotation.x = Math.PI / 2 - 0.12; body.position.set(0, 0.62, 0.05); g.add(body);
    const seat = new THREE.Mesh(new RoundedBoxGeometry(0.26, 0.08, 0.6, 2, 0.04), M.tire); seat.position.set(0, 0.84, 0.25); g.add(seat);
    const shield = new THREE.Mesh(new RoundedBoxGeometry(0.42, 0.55, 0.12, 2, 0.05), paint); shield.position.set(0, 0.85, -0.5); shield.rotation.x = 0.25; g.add(shield);
    const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.62, 8), M.rim); bar.rotation.z = Math.PI / 2; bar.position.set(0, 1.12, -0.42); g.add(bar);
    const shirt = new THREE.MeshStandardMaterial({ color: [0x2b3440, 0x6b4b2a, 0x1f5f3f, 0x444444, 0x8b1a1a][Math.floor(rnd() * 5)], roughness: 0.85 });
    const pants = new THREE.MeshStandardMaterial({ color: 0x1b2230, roughness: 0.9 });
    const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.16, 0.42, 4, 10), shirt); torso.position.set(0, 1.32, 0.18); torso.rotation.x = -0.28; g.add(torso);
    for (const s of [-1, 1]) {
      const arm = new THREE.Mesh(new THREE.CapsuleGeometry(0.05, 0.42, 4, 8), shirt); arm.position.set(s * 0.2, 1.3, -0.12); arm.rotation.set(-1.0, 0, s * 0.18); g.add(arm);
      const thigh = new THREE.Mesh(new THREE.CapsuleGeometry(0.075, 0.36, 4, 8), pants); thigh.position.set(s * 0.15, 0.98, 0.0); thigh.rotation.x = 1.25; g.add(thigh);
      const shin = new THREE.Mesh(new THREE.CapsuleGeometry(0.06, 0.34, 4, 8), pants); shin.position.set(s * 0.17, 0.7, -0.2); shin.rotation.x = 0.2; g.add(shin);
    }
    const helmet = new THREE.Mesh(new THREE.SphereGeometry(0.16, 16, 12), new THREE.MeshPhysicalMaterial({ color: [0xffffff, 0x111111, 0xd8b100][Math.floor(rnd() * 3)], roughness: 0.2, clearcoat: 1 }));
    helmet.position.set(0, 1.78, 0.02); g.add(helmet);
    const visor = new THREE.Mesh(new THREE.SphereGeometry(0.162, 16, 8, -0.9, 1.8, 1.2, 0.6), M.glass); visor.position.copy(helmet.position); visor.rotation.y = Math.PI; g.add(visor);
    for (const [z, m] of [[-0.95, M.head], [0.95, M.tail]] as [number, THREE.Material][]) { const l = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.06, 0.03), m); l.position.set(0, z < 0 ? 0.95 : 0.8, z * 0.75); g.add(l); }
    shadowAll(g); return g;
  }
  type Mover = { o: THREE.Object3D; x: number; z0: number; v: number; dir: number; kind: "car" | "bike" };
  const movers: Mover[] = [];
  const traffic = new THREE.Group(); root.add(traffic);
  for (const [lanes, dir] of [[LANES.carW, -1], [LANES.carE, 1]] as [number[], number][]) for (const x of lanes) for (let i = 0; i < 9; i++) {
    const o = car(carCols[Math.floor(rnd() * carCols.length)]); traffic.add(o); movers.push({ o, x, z0: 100 - rnd() * 1300, v: 14 + rnd() * 8, dir, kind: "car" });
  }
  for (const [x, dir] of [[LANES.motorW, -1], [LANES.motorE, 1]] as [number, number][]) for (let i = 0; i < 26; i++) {
    const o = bike(); traffic.add(o); movers.push({ o, x: x + (rnd() - 0.5) * 1.2, z0: 100 - rnd() * 1300, v: 9 + rnd() * 4, dir, kind: "bike" });
  }
  // hero truck with watermark livery (S02)
  const truck = new THREE.Group();
  const boxMat = new THREE.MeshStandardMaterial({ color: new THREE.Color(0.86, 0.86, 0.84), roughness: 0.4, metalness: 0.15 });
  const box = new THREE.Mesh(new RoundedBoxGeometry(2.5, 2.9, 9.2, 2, 0.05), boxMat); box.position.set(0, 2.5, 1.8); truck.add(box);
  for (let i = 0; i < 44; i++) for (const s of [-1, 1]) { const r = new THREE.Mesh(new THREE.BoxGeometry(0.03, 2.6, 0.06), boxMat); r.position.set(s * 1.26, 2.5, -2.5 + i * 0.2); truck.add(r); }
  const cabShape = new THREE.Shape(); cabShape.moveTo(0, 0.55); cabShape.lineTo(2.3, 0.55); cabShape.lineTo(2.3, 3.0); cabShape.lineTo(0.55, 3.0); cabShape.lineTo(0.05, 1.7); cabShape.lineTo(0, 0.55);
  const cabG = new THREE.ExtrudeGeometry(cabShape, { depth: 2.3, bevelEnabled: true, bevelThickness: 0.08, bevelSize: 0.08, bevelSegments: 3 }); cabG.translate(0, 0, -1.15); cabG.rotateY(-Math.PI / 2);
  const cabMesh = new THREE.Mesh(cabG, new THREE.MeshPhysicalMaterial({ color: 0x15428f, metalness: 0.4, roughness: 0.3, clearcoat: 1, clearcoatRoughness: 0.06 })); cabMesh.position.set(0, 0, -5.4); truck.add(cabMesh);
  const ws = new THREE.Mesh(new THREE.PlaneGeometry(2.05, 1.25), M.glass); ws.position.set(0, 2.38, -5.08); ws.rotation.set(-0.37, Math.PI, 0); truck.add(ws);
  for (const x of [-0.82, 0.82]) { const h = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.14, 0.05), M.head); h.position.set(x, 0.95, -5.43); truck.add(h); }
  const bumper = new THREE.Mesh(new RoundedBoxGeometry(2.5, 0.35, 0.3, 2, 0.06), new THREE.MeshStandardMaterial({ color: 0x222326, roughness: 0.5 })); bumper.position.set(0, 0.6, -5.4); truck.add(bumper);
  for (const z of [-4.4, 2.6, 4.0]) for (const x of [-1.05, 1.05]) { const w = wheel(0.5, 0.3); w.position.set(x, 0.5, z); truck.add(w); }
  const livery = new THREE.Mesh(new THREE.PlaneGeometry(4.6, 1.98), new THREE.MeshStandardMaterial({ map: wmark, transparent: true, opacity: 0.82, roughness: 0.55, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -4 }));
  livery.position.set(-1.3, 2.55, 1.8); livery.rotation.y = -Math.PI / 2; truck.add(livery);
  shadowAll(truck); livery.castShadow = false; root.add(truck);

  // ---------- toll gate (S07) ----------
  const gate = new THREE.Group(); gate.position.set(0, DECK_TOP, GATE_Z);
  const steelW = new THREE.MeshStandardMaterial({ color: 0xe9e9e6, roughness: 0.45, metalness: 0.25 });
  const roof = new THREE.Mesh(new THREE.BoxGeometry(32, 0.7, 14), steelW); roof.position.y = 6.5; gate.add(roof);
  const under = new THREE.Mesh(new THREE.PlaneGeometry(31.6, 13.6), new THREE.MeshStandardMaterial({ color: 0xbfc3c6, roughness: 0.7, side: THREE.DoubleSide })); under.rotation.x = Math.PI / 2; under.position.y = 6.14; gate.add(under);
  for (let i = 0; i < 8; i++) for (let j = 0; j < 3; j++) { const l = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 0.3), new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xffffff, emissiveIntensity: 1.5, side: THREE.DoubleSide })); l.rotation.x = Math.PI / 2; l.position.set(-14 + i * 4, 6.13, -4 + j * 4); gate.add(l); }
  const fascia = new THREE.Mesh(new THREE.BoxGeometry(32.2, 1.3, 0.3), new THREE.MeshStandardMaterial({ map: signTex("GERBANG TOL", "JALUR 1 – 8"), roughness: 0.5 })); fascia.position.set(0, 6.5, 7.05); gate.add(fascia);
  const boothXs = [-11.6, -7.7, -4.3, -0.6, 0.6, 4.3, 7.7, 11.6];
  const boothMat = new THREE.MeshStandardMaterial({ color: 0xd9dcdf, roughness: 0.4, metalness: 0.2 });
  const island = new THREE.MeshStandardMaterial({ map: hazardTex(), roughness: 0.7 });
  for (const x of boothXs) {
    const isl = new THREE.Mesh(new THREE.BoxGeometry(1.3, 0.25, 9), island); isl.position.set(x, 0.12, 0); gate.add(isl);
    const nose = new THREE.Mesh(new THREE.CylinderGeometry(0.65, 0.65, 0.9, 20, 1, false, 0, Math.PI), island); nose.position.set(x, 0.45, 4.5); gate.add(nose);
    const b = new THREE.Mesh(new RoundedBoxGeometry(1.4, 2.4, 3.0, 2, 0.1), boothMat); b.position.set(x, 1.45, 0); gate.add(b);
    const win = new THREE.Mesh(new THREE.BoxGeometry(1.42, 1.0, 2.2), M.glass); win.position.set(x, 1.85, 0); gate.add(win);
    const p = new THREE.Mesh(new THREE.BoxGeometry(0.35, 5.9, 0.35), steelW); p.position.set(x, 3.2, -3.0); gate.add(p);
    const cab = new THREE.Mesh(new RoundedBoxGeometry(0.4, 1.0, 0.4, 2, 0.05), new THREE.MeshStandardMaterial({ color: 0xf2c200, roughness: 0.5 })); cab.position.set(x + (x < 0 ? -0.6 : 0.6), 0.75, 2.4); gate.add(cab);
  }
  const sticker = new THREE.Mesh(new THREE.PlaneGeometry(0.95, 0.88), new THREE.MeshStandardMaterial({ map: emblem, transparent: true, opacity: 0.6, roughness: 0.6, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -4 }));
  sticker.position.set(-11.6, 1.45, 1.52); gate.add(sticker);
  const booms: { arm: THREE.Group; kind: "motor" | "car" }[] = [];
  const boomMat = new THREE.MeshStandardMaterial({ color: 0xf2f2f2, roughness: 0.4 }); const boomRed = new THREE.MeshStandardMaterial({ color: 0xd11a1a, roughness: 0.4 });
  const addBoom = (x: number, len: number, kind: "motor" | "car") => {
    const arm = new THREE.Group(); arm.position.set(x, 1.15, 2.4);
    for (let i = 0; i < 6; i++) { const seg = new THREE.Mesh(new THREE.BoxGeometry(Math.abs(len) / 6, 0.09, 0.09), i % 2 ? boomRed : boomMat); seg.position.x = (i + 0.5) * (len / 6); arm.add(seg); }
    gate.add(arm); booms.push({ arm, kind });
  };
  addBoom(-12.2, -3.1, "motor"); addBoom(-11.0, 9.8, "car"); addBoom(12.2, 3.1, "motor"); addBoom(11.0, -9.8, "car");
  const sigs: { m: THREE.MeshStandardMaterial; kind: "motor" | "car" }[] = [];
  for (const [x, kind] of [[-13.3, "motor"], [-9.4, "car"], [-6.0, "car"], [-2.6, "car"]] as [number, "motor" | "car"][]) {
    const m = new THREE.MeshStandardMaterial({ color: 0x0f3, emissive: 0x00ff44, emissiveIntensity: 2.5 });
    const s = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.45, 0.12), m); s.position.set(x, 5.4, 7.25); gate.add(s); sigs.push({ m, kind });
  }
  const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.06, 3.2, 10), M.rail); mast.position.set(-14.5, 8.45, 4); gate.add(mast);
  const cups = new THREE.Group(); cups.position.set(-14.5, 10.1, 4);
  for (let i = 0; i < 3; i++) {
    const a = (i / 3) * Math.PI * 2; const arm = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.025, 0.025), M.rail); arm.position.set(Math.cos(a) * 0.27, 0, Math.sin(a) * 0.27); arm.rotation.y = -a; cups.add(arm);
    const cup = new THREE.Mesh(new THREE.SphereGeometry(0.09, 12, 8, 0, Math.PI), new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.4, side: THREE.DoubleSide })); cup.position.set(Math.cos(a) * 0.55, 0, Math.sin(a) * 0.55); cup.rotation.y = -a + Math.PI / 2; cups.add(cup);
  }
  gate.add(cups);
  const cctv = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.08, 4, 8), M.rail); cctv.position.set(-15.2, 2, 9); gate.add(cctv);
  const camBox = new THREE.Mesh(new RoundedBoxGeometry(0.2, 0.18, 0.45, 2, 0.04), new THREE.MeshStandardMaterial({ color: 0xf0f0f0, roughness: 0.4 })); camBox.position.set(-15.0, 4.0, 8.8); gate.add(camBox);
  const sockPole = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.05, 3, 8), M.rail); sockPole.position.set(14.5, 8.35, 4); gate.add(sockPole);
  const sock = new THREE.Group(); sock.position.set(14.5, 9.7, 4);
  const sockTex = canvasTex(256, 64, (g) => { for (let i = 0; i < 5; i++) { g.fillStyle = i % 2 ? "#ffffff" : "#ff5a00"; g.fillRect(i * 51.2, 0, 51.2, 64); } });
  const sockMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.12, 2.0, 18, 1, true), new THREE.MeshStandardMaterial({ map: sockTex, side: THREE.DoubleSide, roughness: 0.8 }));
  sockMesh.rotation.z = Math.PI / 2; sockMesh.position.x = -1.0; sock.add(sockMesh); gate.add(sock);
  shadowAll(gate); sticker.castShadow = false; root.add(gate);

  shadowAll(beach);
  for (const x of root.children) if ((x as THREE.Mesh).isMesh && x !== water) { x.castShadow = true; x.receiveShadow = true; }
  [caps, piles, deck, road].forEach((m) => { m.castShadow = true; m.receiveShadow = true; });
  foam.castShadow = false; foam.receiveShadow = false;

  // ---------- per-frame update ----------
  const update = (t: number) => {
    const s = shotAt(t);
    water.material.uniforms["time"].value = t * 0.55;
    water.position.y = tide(t);
    foam.position.y = tide(t) + 0.02;
    foamMat.opacity = 0.78; (foamMat.map as THREE.Texture).rotation = t * 0.03; (foamMat.map as THREE.Texture).center.set(0.5, 0.5);
    const heroShot = s.id === "S03" || s.id === "S04" || s.id === "S05" || s.id === "S06";
    hero.visible = heroShot;
    // lid lifts in S03, stays up in S04, comes back down at the start of S05
    const lift = s.id === "S03" ? ramp(s.u, 0.3, 0.48) : s.id === "S04" ? 1 : s.id === "S05" ? 1 - ramp(s.u, 0.0, 0.12) : 0;
    lid.position.y = lift * 0.8;
    // S04: chloride creeps through the cover, strands rust, section cracks, cover spalls off
    const u4 = s.id === "S04" ? s.u : 0;
    const front = s.id === "S04" ? ramp(u4, 0.05, 0.4) : 0;
    const rustK = s.id === "S04" ? ramp(u4, 0.38, 0.62) : s.id === "S05" ? 1 : 0;
    const crackK = s.id === "S04" ? ramp(u4, 0.6, 0.75) : s.id === "S05" ? 1 : 0;
    const spallK = s.id === "S04" ? ramp(u4, 0.76, 0.95) : s.id === "S05" ? 1 : 0;
    const healthy = s.id === "S03" || s.id === "S06";
    const r0 = lerp(R1, P_RS - 0.012, front);
    chl.geometry.dispose(); chl.geometry = new THREE.RingGeometry(Math.min(r0, R1 - 0.0005), R1, 64, 1, ph0 + CH_A - Math.PI / 2, phL - CH_A).rotateX(-Math.PI / 2).translate(0, SY + 0.002, 0);
    chlMat.opacity = s.id === "S04" ? 0.38 * Math.min(1, front * 4) * (1 - ramp(u4, 0.72, 0.86)) : 0;
    ions.visible = s.id === "S04";
    ionSeed.forEach(([a, k, k2], i) => {
      const prog = Math.min(1, front * (0.7 + k * 0.45));
      const r = lerp(R1 - 0.004, P_RS + 0.006, prog) + (k2 - 0.5) * 0.01;
      tmp.position.set(Math.sin(a) * r, SY + 0.006, Math.cos(a) * r); tmp.scale.setScalar(front > 0.01 ? 1 : 0.0001); tmp.rotation.set(0, 0, 0); tmp.updateMatrix(); ions.setMatrixAt(i, tmp.matrix);
    });
    ions.instanceMatrix.needsUpdate = true;
    const rk = healthy ? 0 : rustK;
    strandMat.color.setRGB(lerp(0.62, 0.5, rk), lerp(0.63, 0.24, rk), lerp(0.65, 0.08, rk)); strandMat.metalness = lerp(0.95, 0.2, rk); strandMat.roughness = lerp(0.28, 0.95, rk);
    spiralMat.color.copy(strandMat.color); spiralMat.metalness = strandMat.metalness; spiralMat.roughness = strandMat.roughness;
    strands.forEach((m) => m.scale.set(1 + rk * 0.9, 1, 1 + rk * 0.9));
    rustDiscMat.opacity = healthy ? 0 : rustK * 0.95; rustDiscs.forEach((d) => d.scale.setScalar(0.009 + rk * 0.02));
    crackMat.opacity = healthy ? 0 : crackK;
    const fall = healthy ? 0 : spallK;
    chunk.position.set(Math.sin(ph0 + CH_A / 2) * fall * 0.25, -fall * fall * 2.6, Math.cos(ph0 + CH_A / 2) * fall * 0.25);
    chunk.rotation.set(fall * 0.9, 0, fall * 0.4);
    chunk.visible = !(s.id === "S05" || (s.id === "S04" && fall > 0.98));
    // S05: tidal band + rusting joint plate
    (band.material as THREE.MeshBasicMaterial).opacity = s.id === "S05" ? 0.26 * ramp(s.u, 0.05, 0.15) * (1 - ramp(s.u, 0.38, 0.46)) : 0;
    const plateRust = s.id === "S05" ? ramp(s.u, 0.62, 0.85) : 0;
    plateMat.color.setRGB(lerp(0.45, 0.5, plateRust), lerp(0.46, 0.25, plateRust), lerp(0.48, 0.1, plateRust)); plateMat.roughness = lerp(0.42, 0.9, plateRust); plateMat.metalness = lerp(0.9, 0.25, plateRust);
    // S06: clamshell closes, straps appear, coating wipes down
    const u6 = s.id === "S06" ? s.u : 0;
    jacket.visible = s.id === "S06";
    const close = ramp(u6, 0.04, 0.3);
    hinge.rotation.y = lerp(-1.9, 0, close);
    jacket.position.y = lerp(0.25, 0, ramp(u6, 0.0, 0.12));
    straps.forEach((st, i) => { st.visible = u6 > 0.3 + i * 0.04; });
    const c = ramp(u6, 0.5, 0.82);
    coat.visible = s.id === "S06" && c > 0.01;
    const len = Math.max(0.001, c * (Y1 - coatTop)); coat.scale.y = len; coat.position.y = Y1 - len / 2;
    // traffic
    const span = 1400;
    movers.forEach((m, i) => {
      let z = m.z0 + m.dir * m.v * t;
      z = ((z - 100) % span + span) % span - span + 100;
      if (s.id === "S07" && m.dir < 0) {
        const stop = m.kind === "bike" ? motorClosed(t) > 0.5 : carClosed(t) > 0.5;
        const queueZ = GATE_Z + 5 + (i % 7) * (m.kind === "bike" ? 2.4 : 6.5);
        if (stop && z < queueZ && z > GATE_Z - 30) z = queueZ;
      }
      m.o.position.set(m.x, DECK_TOP, z); m.o.rotation.y = m.dir < 0 ? 0 : Math.PI;
    });
    traffic.visible = !heroShot && s.id !== "S01";
    truck.visible = s.id === "S02";
    if (truck.visible) truck.position.set(LANES.carW[0], DECK_TOP, lerp(-20, -236, s.u));
    gate.visible = s.id === "S07" || s.id === "S08";
    const w = windKmh(t);
    cups.rotation.y = -t * (w / 6);
    const droop = 1 - Math.min(1, w / 45);
    sock.rotation.z = -droop * 1.1 + Math.sin(t * (2 + w / 12)) * 0.06 * (1 - droop * 0.5);
    sock.rotation.y = Math.sin(t * 0.7) * 0.15;
    booms.forEach((b) => {
      const k = b.kind === "motor" ? motorClosed(t) : carClosed(t);
      const up = (b.arm.children[0].position.x < 0 ? -1 : 1) * Math.PI * 0.47;
      b.arm.rotation.z = lerp(up, 0, s.id === "S07" ? k : 0);
    });
    sigs.forEach((g) => {
      const closed = (g.kind === "motor" ? motorClosed(t) : carClosed(t)) > 0.5 && s.id === "S07";
      g.m.color.set(closed ? 0xff1a1a : 0x00ff44); g.m.emissive.set(closed ? 0xff1a1a : 0x00ff44);
    });
    beach.visible = s.id === "S01";
  };
  return { scene: root, water, update };
}
