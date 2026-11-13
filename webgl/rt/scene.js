import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { strataTexture, boreTexture, concreteTexture, makeNoise } from './tex.js';
export const W = 1080, H = 1920;

export const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('gl'), antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H); renderer.setPixelRatio(1);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.15;
renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.localClippingEnabled = true;

export const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b0907);
scene.fog = new THREE.FogExp2(0x15110d, 0.012);
const pm = new THREE.PMREMGenerator(renderer);
scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.55;
export const cam = new THREE.PerspectiveCamera(36, W / H, 0.1, 250);

// ---------- konstanta ----------
const R = 3.2, SH_IN = 3.0, RO = 2.9, RI = 2.3, FACE_X = 1.6, TAIL_X = -6.3, FRONT_X = 0.05;
const clip = [new THREE.Plane(new THREE.Vector3(0, 0, -1), 0)];
const N = makeNoise(5);

// ---------- bahan ----------
const strata = strataTexture({ seed: 11, w: 2048, h: 2048 });
for (const x of [strata.map, strata.normalMap]) x.wrapS = x.wrapT = THREE.MirroredRepeatWrapping;
const bore = boreTexture(4), conc = concreteTexture(2);
for (const t of [bore.map, bore.normalMap]) t.repeat.set(10, 3);
for (const t of [conc.map, conc.normalMap]) t.repeat.set(2, 1);
const std = (o) => new THREE.MeshStandardMaterial(o);
const M = {
  rockFace: std({ map: strata.map, normalMap: strata.normalMap, normalScale: new THREE.Vector2(1.6, 1.6), roughness: 0.93 }),
  bore: std({ map: bore.map, normalMap: bore.normalMap, normalScale: new THREE.Vector2(1.8, 1.8), roughness: 1, side: THREE.DoubleSide }),
  face: std({ map: bore.map, normalMap: bore.normalMap, normalScale: new THREE.Vector2(2.2, 2.2), roughness: 1, side: THREE.DoubleSide, clippingPlanes: clip }),
  steel: std({ color: 0x8a9096, metalness: 0.92, roughness: 0.32, side: THREE.DoubleSide, clippingPlanes: clip }),
  steelS: std({ color: 0x8a9096, metalness: 0.92, roughness: 0.32 }),
  dark: std({ color: 0x2b2f34, metalness: 0.85, roughness: 0.46, side: THREE.DoubleSide, clippingPlanes: clip }),
  darkS: std({ color: 0x2b2f34, metalness: 0.85, roughness: 0.46 }),
  paint: std({ color: 0xe0661a, metalness: 0.3, roughness: 0.4, side: THREE.DoubleSide, clippingPlanes: clip }),
  paintS: std({ color: 0xe0661a, metalness: 0.3, roughness: 0.4 }),
  blue: std({ color: 0x1d5ea6, metalness: 0.35, roughness: 0.4, side: THREE.DoubleSide, clippingPlanes: clip }),
  blueS: std({ color: 0x1d5ea6, metalness: 0.35, roughness: 0.4 }),
  yellowS: std({ color: 0xe8b617, metalness: 0.25, roughness: 0.45 }),
  conc: std({ map: conc.map, normalMap: conc.normalMap, roughness: 0.93, side: THREE.DoubleSide, clippingPlanes: clip }),
  concS: std({ map: conc.map, normalMap: conc.normalMap, roughness: 0.93 }),
  grout: std({ color: 0x77786a, roughness: 1 }),
  rubber: std({ color: 0x141414, roughness: 0.85 }),
  rail: std({ color: 0x5a5f66, metalness: 0.85, roughness: 0.45 }),
  chip: std({ map: strata.map, normalMap: strata.normalMap, roughness: 0.96, color: 0xb9ab98 }),
  lamp: std({ color: 0xfff1d0, emissive: 0xffe2a8, emissiveIntensity: 4 }),
  vest: std({ color: 0xff6a00, roughness: 0.7 }),
  helm: std({ color: 0xf2c200, roughness: 0.4 }),
  cloth: std({ color: 0x2c3a4f, roughness: 0.9 }),
  skin: std({ color: 0xb98a68, roughness: 0.8 }),
  duct: std({ color: 0xd9741c, roughness: 0.85 }),
  brush: std({ color: 0x3a3022, roughness: 1, clippingPlanes: clip, side: THREE.DoubleSide }),
};
M.rockFace.clippingPlanes = null;

const root = new THREE.Group(); scene.add(root);
let rockMesh = null;
const put = (m, x = 0, y = 0, z = 0, par = root, shadow = true) => { m.position.set(x, y, z); m.castShadow = shadow; m.receiveShadow = true; par.add(m); return m; };
const cylX = (r1, r2, len, mat, seg = 48, open = false) => { const g = new THREE.CylinderGeometry(r1, r2, len, seg, 1, open); g.rotateZ(Math.PI / 2); return new THREE.Mesh(g, mat); };
const box = (w, h, d, mat) => new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
const cyl = (r, h, mat, seg = 20) => new THREE.Mesh(new THREE.CylinderGeometry(r, r, h, seg), mat);

// ---------- batuan ----------
{
  const LxL = 40, LxR = 30, Hh = 16;
  const sh = new THREE.Shape();
  const pts = [[-LxL, -Hh], [LxR, -Hh], [LxR, Hh], [-LxL, Hh], [-LxL, R], [FACE_X, R], [FACE_X, -R], [-LxL, -R]];
  pts.forEach((p, i) => i ? sh.lineTo(p[0], p[1]) : sh.moveTo(p[0], p[1])); sh.closePath();
  const g = new THREE.ShapeGeometry(sh, 8); const uv = g.attributes.uv, pos = g.attributes.position;
  for (let i = 0; i < uv.count; i++) uv.setXY(i, pos.getX(i) / 16, pos.getY(i) / 14);
  const f = new THREE.Mesh(g, M.rockFace); f.receiveShadow = true; root.add(f); rockMesh = f;
  const cg = new THREE.CylinderGeometry(R, R, LxL + FACE_X, 120, 1, true, Math.PI / 2, Math.PI); cg.rotateZ(Math.PI / 2); cg.translate((FACE_X - LxL) / 2, 0, 0);
  put(new THREE.Mesh(cg, M.bore), 0, 0, 0, root, false);
  const back = new THREE.Mesh(new THREE.PlaneGeometry(90, 40), std({ color: 0x120e0a, roughness: 1 })); back.position.set(-5, 0, -R - 0.4); root.add(back);
}
// muka galian: kasar, bergaris, cekung
let faceDisc;
{
  const g = new THREE.RingGeometry(0.02, R - 0.02, 160, 56); g.rotateY(Math.PI / 2);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const y = p.getY(i), z = p.getZ(i), r = Math.hypot(y, z);
    const dx = N.fbm(y * 1.7, z * 1.7, 4) * 0.28 + N.noise(y * 9, z * 9) * 0.05 + Math.sin(r * 34) * 0.035 - (r / R) * (r / R) * 0.12;
    p.setX(i, FACE_X + 0.25 + dx);
  }
  g.computeVertexNormals();
  const uvs = g.attributes.uv; for (let i = 0; i < uvs.count; i++) uvs.setXY(i, p.getY(i) * 0.7, p.getZ(i) * 0.7);
  faceDisc = put(new THREE.Mesh(g, M.face), 0, 0, 0, root, false);
}

// ---------- kepala pemotong ----------
const head = new THREE.Group(); head.position.set(0.5, 0, 0); root.add(head);
{
  put(cylX(R - 0.05, R - 0.05, 0.9, M.paint, 96), 0, 0, 0, head);
  put(cylX(0.95, 0.95, 1.5, M.dark, 48), 0.3, 0, 0, head);
  put(cylX(0.62, 0.62, 0.35, M.steel, 48), 1.15, 0, 0, head);
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2, b = cylX(0.06, 0.06, 0.1, M.dark, 8); put(b, 1.3, Math.sin(a) * 0.5, Math.cos(a) * 0.5, head); }
  for (let i = 0; i < 8; i++) {
    const a = i / 8 * Math.PI * 2, arm = new THREE.Group(); arm.rotation.x = a; head.add(arm);
    put(box(0.5, R - 0.45, 0.62, M.paint), 0.2, (R - 0.45) / 2 + 0.7, 0, arm);
    put(box(0.34, R - 0.45, 0.4, M.dark), 0.55, (R - 0.45) / 2 + 0.7, 0, arm);
    // pelat aus
    put(box(0.1, R - 0.6, 0.66, M.dark), 0.42, (R - 0.45) / 2 + 0.7, 0, arm);
    for (let r = 1.05, k = 0; r < R - 0.2; r += 0.4, k++) {
      put(cylX(0.27, 0.27, 0.22, M.dark, 28), 0.72, r, 0, arm);
      put(cylX(0.22, 0.31, 0.13, M.steel, 36), 0.9, r, 0, arm);
      put(cylX(0.32, 0.32, 0.045, M.steel, 36), 0.96, r, 0, arm);
      put(cylX(0.08, 0.08, 0.08, M.dark, 12), 1.0, r, 0, arm);
      
    }
    // gigi pengeruk di tepi + ember buang
    put(box(0.5, 0.34, 0.85, M.dark), 0.25, R - 0.3, 0, arm);
    put(box(0.28, 0.18, 0.5, M.dark), 0.62, R - 0.1, 0.0, arm);
  }
  // ring bagian dalam kepala
  put(cylX(R - 0.55, R - 0.55, 0.12, M.steel, 96, true), 0.6, 0, 0, head);
}

// ---------- perisai ----------
// kulit, rusuk, sambungan artikulasi, bulkhead, motor penggerak
put(cylX(R - 0.05, R - 0.05, 6.35, M.blue, 120, true), (TAIL_X + 0.05) / 2, 0, 0, root, false);
put(cylX(SH_IN, SH_IN, 6.35, M.dark, 120, true), (TAIL_X + 0.05) / 2, 0, 0, root, false);
for (const x of [-0.2, -1.4, -2.6, -3.8, -5.0]) { const t = new THREE.Mesh(new THREE.TorusGeometry(SH_IN - 0.05, 0.07, 8, 96), M.steel); t.rotation.y = Math.PI / 2; t.position.x = x; root.add(t); }
{ // sambungan artikulasi (ring gelap)
  const t = new THREE.Mesh(new THREE.TorusGeometry(R - 0.02, 0.1, 10, 120), M.dark); t.rotation.y = Math.PI / 2; t.position.x = -3.3; t.castShadow = true; root.add(t);
}
put(cylX(R - 0.1, R - 0.1, 0.4, M.steel, 96), -0.2, 0, 0);
put(cylX(R - 0.5, R - 0.5, 0.15, M.dark, 96), -0.45, 0, 0);
// motor penggerak kepala (di belakang bulkhead)
for (let i = 0; i < 8; i++) {
  const a = i / 8 * Math.PI * 2 + 0.2, y = Math.sin(a) * 2.1, z = Math.cos(a) * 2.1; if (z > 0.2) continue;
  put(cylX(0.34, 0.34, 1.3, i % 2 ? M.paint : M.blue, 24), -1.2, y, z);
  put(cylX(0.22, 0.22, 0.5, M.dark, 20), -2.0, y, z);
  put(cylX(0.42, 0.42, 0.12, M.steel, 24), -0.62, y, z);
}
// dongkrak dorong
const rods = [];
for (let i = 0; i < 20; i++) {
  const a = i / 20 * Math.PI * 2, rr = R - 0.55, y = Math.sin(a) * rr, z = Math.cos(a) * rr; if (z > 0.2) continue;
  put(cylX(0.18, 0.18, 2.4, M.steel, 20), -1.8, y, z);
  put(cylX(0.14, 0.14, 0.2, M.dark, 20), -3.05, y, z);
  const rod = cylX(0.1, 0.1, 1.85, M.steel, 14); put(rod, -4.0, y, z); rods.push(rod);
  put(box(0.14, 0.5, 0.7, M.dark), -4.95, y, z);   // bantalan menekan cincin
  put(cylX(0.22, 0.22, 0.2, M.paint, 20), -0.7, y, z);
}
// sikat kawat ekor perisai
put(cylX(2.98, 2.98, 0.35, M.brush, 96, true), -6.1, 0, 0, root, false);
put(cylX(2.9, 2.9, 0.35, M.brush, 96, true), -6.1, 0, 0, root, false);

// ---------- potongan (penutup irisan) ----------
const capMat = (mat) => { const m = mat.clone(); m.clippingPlanes = null; m.side = THREE.FrontSide; return m; };
const strip = (x0, x1, y0, y1, mat, z = 0.001) => {
  for (const s of [1, -1]) { const g = new THREE.PlaneGeometry(Math.abs(x1 - x0), y1 - y0); const m = new THREE.Mesh(g, mat); m.position.set((x0 + x1) / 2, s * (y0 + y1) / 2, z); m.receiveShadow = true; root.add(m); }
};
strip(TAIL_X, 0.05, SH_IN, R - 0.05, capMat(M.blue));
strip(-0.5, 0.0, 0, R - 0.1, capMat(M.steel), 0.002);   // bulkhead
// kepala pemotong irisan: pelat dasar
// ---------- segmen beton ----------
function segGeom(a0, a1, thick, ro = RO, ri = RI) {
  const sh = new THREE.Shape(), n = 28;
  for (let k = 0; k <= n; k++) { const a = a0 + (a1 - a0) * k / n; const p = [Math.cos(a) * ro, Math.sin(a) * ro]; k ? sh.lineTo(...p) : sh.moveTo(...p); }
  for (let k = n; k >= 0; k--) { const a = a0 + (a1 - a0) * k / n; sh.lineTo(Math.cos(a) * ri, Math.sin(a) * ri); }
  const g = new THREE.ExtrudeGeometry(sh, { depth: thick, bevelEnabled: true, bevelSize: 0.025, bevelThickness: 0.025, bevelSegments: 1, curveSegments: 1 });
  g.rotateY(Math.PI / 2); return g;       // y = sin a*r, z = -cos a*r, sumbu x
}
const ALPHA = Math.PI * 2 / 7;
const segAngles = (k) => { const c = -Math.PI / 2 + (k - 3) * ALPHA; return [c - ALPHA / 2 + 0.012, c + ALPHA / 2 - 0.012]; };
const ringTints = [0xffffff, 0xf2eee4, 0xe8e6e0, 0xfafafa];
function ring(x0, thick = 1.46, missing = [], tintIdx = 0) {
  const g = new THREE.Group(); g.position.x = x0; root.add(g);
  for (let k = 0; k < 7; k++) {
    if (missing.includes(k)) continue;
    const [a0, a1] = segAngles(k);
    const m = new THREE.Mesh(segGeom(a0, a1, thick), M.conc); m.castShadow = true; m.receiveShadow = true; g.add(m);
    m.material = M.conc.clone(); m.material.color.setHex(ringTints[(tintIdx + k) % 4]);
    for (const dx of [0.28, thick - 0.28]) { // kantong baut
      const am = a0 - 0.0;
      const b = box(0.12, 0.1, 0.1, M.darkS); const ang = a0 + 0.0; b.position.set(dx, Math.sin(ang) * (RI + 0.02), -Math.cos(ang) * (RI + 0.02)); b.rotation.x = ang + Math.PI / 2; g.add(b);
    }
  }
  return g;
}
const rings = [];
const NR = 13;
for (let i = 0; i < NR; i++) rings.push(ring(-7.8 - i * 1.5, 1.46, [], i));
// cincin yang sedang dipasang (di dalam ekor perisai), ada celah di atas
const buildRing = ring(-6.28, 1.46, [6, 0], 7);
// penutup irisan cincin & grout
for (let i = 0; i < NR; i++) strip(-7.8 - i * 1.5, -7.8 - i * 1.5 + 1.46, RI, RO, capMat(M.conc));
strip(-7.8 - NR * 1.5, -7.8, RO, R, capMat(M.grout));
strip(TAIL_X, -4.8, RI, RO, capMat(M.conc));
// grout terlihat sebagai kulit tipis
{ const gm = M.grout.clone(); gm.side = THREE.DoubleSide; gm.clippingPlanes = clip; put(cylX(R - 0.02, R - 0.02, NR * 1.5, gm, 96, true), -7.8 - NR * 0.75, 0, 0, root, false); }

// ---------- erector ----------
const erector = new THREE.Group(); erector.position.set(-5.5, 0, 0); root.add(erector);
{
  put(cylX(2.45, 2.45, 0.5, M.paint, 72, true), 0, 0, 0, erector);
  put(cylX(0.5, 0.5, 0.9, M.dark, 24), 0, 0, 0, erector);
  put(cylX(2.52, 2.52, 0.1, M.steel, 72, true), 0.26, 0, 0, erector);
  put(cylX(2.52, 2.52, 0.1, M.steel, 72, true), -0.26, 0, 0, erector);
}
const arm = new THREE.Group(); arm.position.set(-5.5, 0, 0); root.add(arm);
{ // lengan radial + penjepit vakum memegang segmen k=6
  const hold = new THREE.Group(); arm.add(hold);
  put(box(0.28, 2.3, 0.28, M.paintS), 0.0, 1.2, 0, hold);
  put(cylX(0.18, 0.18, 0.6, M.darkS, 16), 0, 0.2, 0, hold);
  const [a0, a1] = segAngles(6), g = segGeom(a0, a1, 1.46), m = new THREE.Mesh(g, M.concS.clone()); m.position.set(-0.73, 0, 0); m.castShadow = true; hold.add(m);
  put(box(1.46, 0.12, 0.7, M.darkS), 0, 0, 0, hold).visible = false;
  hold.userData.seg = m;
}
// ---------- lantai, rel, bantalan ----------
const FLOOR_Y = -RI + 0.38;
{ // balok invert beton
  put(box(39.3, 0.4, 3.0, M.concS), -20.35, -RI + 0.2, -1.5);
  const cap = new THREE.Mesh(new THREE.PlaneGeometry(39.3, 0.4), capMat(M.conc)); cap.position.set(-20.35, -RI + 0.2, 0.001); root.add(cap);
  for (let i = 0; i < 44; i++) put(box(0.12, 0.08, 1.5, M.darkS), -1.2 - i * 0.9, FLOOR_Y + 0.04, -0.75);
  for (const z of [-0.2, -1.3]) put(box(39.3, 0.12, 0.09, M.rail), -20.35, FLOOR_Y + 0.14, z);
}
// ---------- screw conveyor ----------
const screw = new THREE.Group(); root.add(screw);
{
  const ang = 0.42;     // naik ke belakang
  const hou = cylX(0.55, 0.55, 5.4, M.dark, 32, true); put(hou, 0, 0, 0, screw);
  const core = cylX(0.16, 0.16, 5.4, M.steel, 14); put(core, 0, 0, 0, screw);
  const fl = new THREE.Group(); screw.add(fl); screw.userData.fl = fl;
  for (let i = 0; i < 22; i++) { const d = cylX(0.5, 0.5, 0.05, M.steelS, 24); d.position.set(-2.6 + i * 0.24, 0, 0); d.rotation.z = Math.PI / 2; d.rotation.y = i * 0.45; fl.add(d); d.castShadow = true; }
  screw.rotation.z = -ang * 0 + Math.PI * 0; screw.rotation.z = 0.0;
  // bidang miring: memutar seluruh grup mengelilingi sumbu z
  screw.rotation.z = ang; screw.position.set(-2.2, -2.15 + 0.0, -0.9);
  // karter motor di ujung
  put(box(0.7, 0.8, 0.9, M.paintS), -4.7, -1.35, -0.9);
}
// ---------- ban berjalan ----------
const BELT_Y = 0.3, BELT_Z = -1.35;
{
  put(box(30, 0.1, 1.0, M.rubber), -22.5, BELT_Y, BELT_Z);
  for (const s of [-0.55, 0.55]) put(box(30, 0.2, 0.06, M.steelS), -22.5, BELT_Y + 0.12, BELT_Z + s);
  for (let i = 0; i < 38; i++) { const x = -6 - i * 0.8; put(cyl(0.07, 1.0, M.steelS, 12), x, BELT_Y - 0.1, BELT_Z).rotation.x = Math.PI / 2; if (i % 4 === 0) { put(box(0.1, 2.1, 0.1, M.steelS), x, BELT_Y - 1.1, BELT_Z - 0.5); put(box(0.1, 2.1, 0.1, M.steelS), x, BELT_Y - 1.1, BELT_Z + 0.5); } }
}
// ---------- pipa, duct, kabel, lampu ----------
{
  const tube = (x0, x1, y, z, r, mat) => put(cylX(r, r, x1 - x0, mat, 20), (x0 + x1) / 2, y, z);
  tube(-6.6, -34, 1.65, -0.9, 0.5, M.duct);                    // duct ventilasi
  for (let i = 0; i < 40; i++) { const t = new THREE.Mesh(new THREE.TorusGeometry(0.5, 0.025, 6, 24), M.darkS); t.rotation.y = Math.PI / 2; t.position.set(-7 - i * 0.7, 1.65, -0.9); root.add(t); }
  tube(-5.6, -34, 1.2, -1.75, 0.13, M.blueS);                  // air
  tube(-5.6, -34, 0.95, -1.9, 0.07, M.darkS);                  // grout
  put(box(30, 0.06, 0.35, M.darkS), -20, 0.6, -2.0);            // baki kabel
  for (let i = 0; i < 5; i++) put(cylX(0.04, 0.04, 30, M.rubber, 8), -20, 0.65 + i * 0.01, -2.0 + (i - 2) * 0.06);
  for (let i = 0; i < 12; i++) { put(box(0.4, 0.06, 0.1, M.lamp), -8 - i * 2.4, 1.0, -2.0, root, false); put(box(0.05, 0.3, 0.05, M.darkS), -8 - i * 2.4, 0.82, -2.0, root, false); }
}
// ---------- kereta (lokomotif + gerbong segmen) ----------
const train = new THREE.Group(); root.add(train);
{
  const y0 = FLOOR_Y + 0.14;
  put(box(2.6, 0.9, 1.4, M.yellowS), -11.0, y0 + 0.65, -0.75, train);
  put(box(1.2, 0.8, 1.3, M.yellowS), -11.4, y0 + 1.45, -0.75, train);
  put(box(0.08, 0.5, 1.1, std({ color: 0x9ec7e0, metalness: 0.1, roughness: 0.15, transparent: true, opacity: 0.55 })), -10.78, y0 + 1.5, -0.75, train);
  put(box(0.2, 0.2, 0.2, M.lamp), -9.65, y0 + 0.9, -0.4, train, false);
  put(box(0.2, 0.2, 0.2, M.lamp), -9.65, y0 + 0.9, -1.1, train, false);
  for (const x of [-12.0, -10.2]) for (const z of [-0.2, -1.3]) put(cylX(0.2, 0.2, 0.1, M.darkS, 20), x, y0 + 0.25, z, train);
  // gerbong pembawa segmen
  put(box(3.2, 0.2, 1.5, M.darkS), -14.4, y0 + 0.4, -0.75, train);
  for (const x of [-15.6, -13.2]) for (const z of [-0.2, -1.3]) put(cylX(0.2, 0.2, 0.1, M.darkS, 20), x, y0 + 0.25, z, train);
  for (let s = 0; s < 3; s++) {
    const sh = new THREE.Shape(); const rr = 3.2, n = 16, a = 0.62;
    for (let k = 0; k <= n; k++) { const t = -a / 2 + a * k / n; const p = [rr * Math.sin(t), rr * Math.cos(t) - rr + 0.0]; k ? sh.lineTo(...p) : sh.moveTo(...p); }
    for (let k = n; k >= 0; k--) { const t = -a / 2 + a * k / n; sh.lineTo((rr - 0.6) * Math.sin(t), (rr - 0.6) * Math.cos(t) - rr); }
    const g = new THREE.ExtrudeGeometry(sh, { depth: 1.3, bevelEnabled: false }); g.translate(0, 0, -0.65);
    const m = new THREE.Mesh(g, M.concS); put(m, -14.4, y0 + 0.5 + s * 0.62 + 0.55, -0.75, train);
  }
}
// ---------- gantry (rangka penopang) ----------
{
  for (const gx of [-9.4, -17.2, -25.0]) {
    const y0 = FLOOR_Y;
    for (const z of [-0.15, -2.05]) { put(box(0.14, 3.6, 0.14, M.paintS), gx, y0 + 1.8, z); put(box(0.14, 3.6, 0.14, M.paintS), gx + 3.4, y0 + 1.8, z); }
    put(box(3.6, 0.14, 2.1, M.paintS), gx + 1.7, y0 + 2.45, -1.1);       // lantai tingkat
    put(box(3.6, 0.1, 0.1, M.steelS), gx + 1.7, y0 + 3.05, -0.15);       // pagar
    put(box(0.1, 0.1, 2.1, M.steelS), gx, y0 + 3.0, -1.1);
    put(box(0.5, 0.9, 0.7, M.yellowS), gx + 1.0, y0 + 2.97, -1.4);       // peralatan
    put(cyl(0.45, 1.0, M.blueS, 24), gx + 2.4, y0 + 3.02, -1.4);          // tangki grout
  }
}
// ---------- pekerja ----------
function worker(x, y, z, face = 1, pose = 0) {
  const g = new THREE.Group();
  const leg = (s) => { const l = cyl(0.09, 0.85, M.cloth, 10); l.position.set(0, 0.45, s * 0.11); g.add(l); const b = box(0.28, 0.12, 0.14, M.darkS); b.position.set(0.05, 0.06, s * 0.11); g.add(b); };
  leg(1); leg(-1);
  const t = box(0.3, 0.55, 0.42, M.vest); t.position.set(0, 1.12, 0); g.add(t);
  const t2 = box(0.31, 0.06, 0.43, M.steelS); t2.position.set(0, 1.07, 0); g.add(t2);
  const hd = new THREE.Mesh(new THREE.SphereGeometry(0.13, 16, 12), M.skin); hd.position.set(0, 1.55, 0); g.add(hd);
  const he = new THREE.Mesh(new THREE.SphereGeometry(0.15, 16, 10, 0, Math.PI * 2, 0, Math.PI / 2), M.helm); he.position.set(0, 1.57, 0); g.add(he);
  for (const s of [1, -1]) { const a = cyl(0.06, 0.55, M.vest, 8); a.position.set(0.05 * face, 1.2, s * 0.26); a.rotation.z = pose ? 0.9 * face : 0.1; g.add(a); }
  g.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  g.position.set(x, y, z); g.rotation.y = face > 0 ? 0 : Math.PI; g.scale.setScalar(1.05); root.add(g); return g;
}
worker(-9.0, FLOOR_Y + 0.14, -1.0, -1, 1);
worker(-6.9, FLOOR_Y + 0.14, -0.9, 1, 1);
worker(-12.4, FLOOR_Y + 0.14, -1.7, -1, 0);

// ---------- batu pecah (muck) ----------
const chips = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(0.09, 0), M.chip, 160); chips.castShadow = true; root.add(chips);
const chipSeed = [...Array(160)].map(() => ({ a: Math.random() * 6.28, rr: 0.4 + Math.random() * (R - 0.9), ph: Math.random(), s: 0.7 + Math.random() * 1.6 }));
const pile = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(0.16, 0), M.chip, 180); pile.castShadow = true; pile.receiveShadow = true; root.add(pile);
{
  const d = new THREE.Object3D();
  for (let i = 0; i < 180; i++) {
    const x = 0.2 + Math.random() * 1.1, zz = -(Math.random() * 2.4), base = -R + 0.15;
    const hgt = Math.max(0, 0.9 - (Math.abs(x - 0.7) * 0.9 + Math.abs(zz + 1.1) * 0.35));
    d.position.set(x, base + Math.random() * hgt, zz); d.scale.setScalar(0.7 + Math.random() * 1.7); d.rotation.set(Math.random() * 6, Math.random() * 6, 0); d.updateMatrix(); pile.setMatrixAt(i, d.matrix);
  }
}
const load = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(0.1, 0), M.chip, 120); load.castShadow = true; root.add(load);
const loadSeed = [...Array(120)].map(() => ({ x: Math.random() * 28, z: BELT_Z + (Math.random() - 0.5) * 0.6, s: 0.6 + Math.random() * 1.1, r: Math.random() * 6 }));
const scrChips = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(0.08, 0), M.chip, 40); root.add(scrChips);
const scrSeed = [...Array(40)].map(() => ({ ph: Math.random(), s: 0.7 + Math.random() }));

// ---------- debu ----------
const dustN = 260, dg = new THREE.BufferGeometry(), dp = new Float32Array(dustN * 3);
for (let i = 0; i < dustN; i++) { dp[i * 3] = -14 + Math.random() * 16; dp[i * 3 + 1] = -2.4 + Math.random() * 4.8; dp[i * 3 + 2] = -2 - Math.random() * 0.2 + Math.random() * 2.8 - 1; }
dg.setAttribute('position', new THREE.BufferAttribute(dp, 3));
const dust = new THREE.Points(dg, new THREE.PointsMaterial({ color: 0xffe6c0, size: 0.018, transparent: true, opacity: 0.5, depthWrite: false, sizeAttenuation: true }));
root.add(dust);

// ---------- lampu ----------
const key = new THREE.DirectionalLight(0xffe9cc, 1.5); key.position.set(-4, 10, 18); key.castShadow = true;
Object.assign(key.shadow.camera, { left: -22, right: 22, top: 14, bottom: -14, near: 1, far: 70 }); key.shadow.mapSize.set(4096, 4096); key.shadow.bias = -0.0003; key.shadow.normalBias = 0.02; key.shadow.radius = 3;
scene.add(key); key.target.position.set(-8, 0, 0); scene.add(key.target);
const fill = new THREE.DirectionalLight(0x6f98cc, 0.4); fill.position.set(14, 4, 12); scene.add(fill);
const SPOTS = [[-3, 2.2, -0.5, 1.6, -0.2, -1.2], [-10, 1.6, 0.8, -9, -1.5, -1.0], [-16, 1.6, 0.8, -15, -1.5, -1.0]];
for (const s of SPOTS) { const L = new THREE.SpotLight(0xffd9a0, 260, 30, 1.0, 0.8, 1.3); L.position.set(s[0], s[1], s[2]); L.target.position.set(s[3], s[4], s[5]); scene.add(L, L.target); }
const faceLight = new THREE.PointLight(0xffb868, 90, 16, 1.5); faceLight.position.set(2.4, 0.4, 0.8); scene.add(faceLight);
for (let i = 0; i < 8; i++) { const p = new THREE.PointLight(0xffe0aa, 22, 12, 1.7); p.position.set(-6 - i * 4, 1.2, -1.2); scene.add(p); }

// ---------- animasi ----------
const dummy = new THREE.Object3D();
const SHOTS = {
  wide: { p: [9.0, 3.0, 15.5], l: [-2.6, -0.3, 0], f: 44 },
  mid: { p: [8.5, 2.6, 15.5], l: [-2.2, -0.2, -0.5], f: 44 },
  head: { p: [6.8, 1.8, 12.5], l: [0.2, -0.1, -1.0], f: 40 },
  erector: { p: [-1.0, 2.6, 11.5], l: [-6.2, -0.2, -1.0], f: 40 },
  rear: { p: [-5.0, 0.8, 12.5], l: [-12.5, -0.5, -1.0], f: 40 },
  front: { p: [9.5, 2.0, 7.5], l: [0.6, -0.2, -1.0], f: 44 },
  front2: { p: [6.0, 3.2, 3.2], l: [0.6, 0.0, -1.2], f: 52 },
  muck: { p: [3.2, -1.4, 9.0], l: [-2.0, -1.8, -1.0], f: 40 },
};
export const SHOT_DEFS = SHOTS;
export function renderScene(t, S) {
  head.rotation.x = -t * 0.9;
  screw.userData.fl.children.forEach((d, i) => { d.rotation.y = i * 0.45 + t * 3; });
  arm.rotation.x = 0;  // pegangan segmen menuju celah di atas kanan
  const hold = arm.children[0]; const ph = Math.min(1, (Math.sin(t * 0.5) * 0.5 + 0.5));
  const target = Math.PI * 2 - (ph * 0.35); hold.rotation.x = -(Math.PI / 2 - 1.1) * 0 + (-ph * 0.4);
  hold.position.set(0, 0, 0); hold.rotation.x = -(Math.PI * 2) * 0 - (Math.PI / 2) + (Math.PI / 2) + (ph * 0.25) - 0.12 + (-0.0);
  // segmen yang dipegang: letakkan di sudut k=6 lalu geser keluar sedikit dari celah
  const seg = hold.userData.seg; seg.position.set(-0.73, 0.35 * (1 - ph), 0); seg.position.z = 0;
  for (let i = 0; i < chipSeed.length; i++) {
    const c = chipSeed[i], p = (t * 0.6 + c.ph) % 1;
    const x = 1.5 - p * 0.9, y = Math.sin(c.a) * c.rr - p * p * 2.2, z = -Math.abs(Math.cos(c.a) * c.rr) * 0.8 - 0.15;
    dummy.position.set(x, Math.max(y, -R + 0.15), z); dummy.scale.setScalar(c.s * (1 - p * 0.3)); dummy.rotation.set(p * 9 * c.s, p * 7, 0); dummy.updateMatrix(); chips.setMatrixAt(i, dummy.matrix);
  }
  chips.instanceMatrix.needsUpdate = true;
  for (let i = 0; i < loadSeed.length; i++) {
    const c = loadSeed[i], x = -4.8 - ((c.x + t * 1.2) % 28);
    dummy.position.set(x, BELT_Y + 0.1, c.z); dummy.scale.setScalar(c.s); dummy.rotation.set(c.r, c.r * 2, 0); dummy.updateMatrix(); load.setMatrixAt(i, dummy.matrix);
  }
  load.instanceMatrix.needsUpdate = true;
  for (let i = 0; i < scrSeed.length; i++) {
    const c = scrSeed[i], p = (t * 0.35 + c.ph) % 1;
    const x = -2.2 - 2.4 * Math.cos(0.42) * (p * 2 - 1) * -1 * 0 + (-2.2 + 2.4 * (1 - p * 2) * 0.0) - p * 2.4, y = -2.15 + (-p * 2.4) * -Math.tan(0.42) * 1 + 0.0 + 0;
    dummy.position.set(-2.2 + 2.4 - p * 4.8, -2.15 + (p * 4.8 - 2.4) * -0.0 + (2.4 - p * 4.8) * -Math.tan(0.42), -0.9); dummy.scale.setScalar(c.s); dummy.updateMatrix(); scrChips.setMatrixAt(i, dummy.matrix);
  }
  scrChips.instanceMatrix.needsUpdate = true;
  const p = dust.geometry.attributes.position;
  for (let i = 0; i < dustN; i++) { p.setY(i, ((p.getY(i) + 2.4 + 0.0006 * (1 + (i % 5))) % 4.8) - 2.4); }
  p.needsUpdate = true;
  const front = !!S.front;
  faceDisc.visible = !front;
  const want = front ? [new THREE.Plane(new THREE.Vector3(-1, 0, 0), FACE_X)] : null;
  if ((rockMesh.material.clippingPlanes ? 1 : 0) !== (want ? 1 : 0)) { rockMesh.material.clippingPlanes = want; rockMesh.material.needsUpdate = true; }
  cam.position.set(S.p[0] + Math.sin(t * 0.25) * 0.25, S.p[1], S.p[2]); cam.lookAt(S.l[0], S.l[1], S.l[2]); cam.fov = S.f; cam.updateProjectionMatrix(); cam.updateMatrixWorld();
  renderer.render(scene, cam);
}
const _v = new THREE.Vector3();
export function proj(p) { _v.set(p[0], p[1], p[2]).project(cam); return [(_v.x * 0.5 + 0.5) * W, (-_v.y * 0.5 + 0.5) * H]; }
// titik jangkar label (koordinat dunia terowongan)
export const ANCH = {
  disc: [FACE_X + 0.2, 1.4, 0.3], rim: [FACE_X, 2.7, 1.0], motor: [-1.6, 2.4, 0.2], jack: [-0.9, -0.9, 0.9],
  arm: [-5.4, 1.6, 0.6], belt: [-7.5, -1.7, 0.5], seg: [-6.8, 2.5, 0.4], grout: [-6.0, -2.4, 0.6], face: [FACE_X, 0.2, 0.2],
  screw: [-2.2, -1.2, 0.5], shield: [-0.8, 3.0, 0.5], ring: [-8.5, 2.6, 0.8],
};
