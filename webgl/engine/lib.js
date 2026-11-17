// ---------- Pustaka komponen generik (semua topik) ----------
// Konvensi: y ke atas, satuan meter, titik acuan = pusat dasar. Waktu global TT (detik), waktu adegan TS.
let TT = 0, TS = 0, CURID = '';
const ANCH = {};
const anc = (name, p) => { ANCH[CURID + '.' + name] = wpt(p); };
const fr = x => ((x % 1) + 1) % 1;
const AX = {x: [1, 0, 0], y: [0, 1, 0], z: [0, 0, 1]};
const Rax = (ax, a) => ax === 'x' ? RX(a) : ax === 'z' ? RZ(a) : RY(a);
const COMP = {}, COMP_DOC = {};
function reg(name, doc, fn) { COMP[name] = fn; COMP_DOC[name] = doc; }

// ----- komponen -----
reg('engine', 'mesin torak: n silinder per sisi, v=true untuk susunan V; piston naik-turun, nyala bergantian, poros engkol & roda gila berputar. param: n(4), v(true), rev(1.15)', (o) => {
  const n = o.n || 4, V = o.v !== false, banks = V ? [-1, 1] : [1], d = V ? 22.5 * Math.PI / 180 : 0, Cy = 2.6, r = 0.55, L = 2.0, rev = o.rev || 1.15, th0s = [0, Math.PI, Math.PI / 2, 3 * Math.PI / 2], cr = TT * 2 * Math.PI * rev;
  const len = n * 1.5, x0 = -len / 2 - 0.2;
  box(0, 0.85, 0, len + 1.2, 1.1, 2.6, '#3f4c55'); box(0, 2.45, 0, len + 1.2, 1.9, 2.6, '#7e909c', {glass: true});
  link([x0 - 0.5, Cy, 0], [len / 2 + 1.7, Cy, 0], 0.22, '#b7c0c6', {seg: 16});
  for (let i = 0; i < n; i++) {
    const xi = (i - (n - 1) / 2) * 1.5, th = cr + th0s[i % 4], dy = r * Math.cos(th), dz = r * Math.sin(th);
    for (const sx of [-0.55, 0.55]) { link([xi + sx, Cy, 0], [xi + sx + 0.12, Cy, 0], 0.55, '#c7ced2', {seg: 18, ns: 1}); link([xi + sx, Cy - dy * 0.6, -dz * 0.6], [xi + sx + (sx > 0 ? 0.14 : -0.14), Cy - dy * 0.6, -dz * 0.6], 0.34, '#f08a1c', {seg: 12, ns: 1}); }
    link([xi - 0.55, Cy + dy, dz], [xi + 0.55, Cy + dy, dz], 0.19, '#e8edf0', {seg: 12});
    for (const sg of banks) {
      const u = [Math.cos(d), sg * Math.sin(d)], dv = [dy, dz], a = dv[0] * u[0] + dv[1] * u[1], sp = a + Math.sqrt(L * L - (r * r - a * a)), xc = xi + (V ? sg * 0.3 : 0);
      const P3 = (s, x = xc) => [x, Cy + s * u[0], s * u[1]], thc = th + (sg > 0 ? 0 : Math.PI * 2), par = ((Math.floor(thc / (2 * Math.PI)) % 2) + 2) % 2 === 0, fl = par ? Math.max(0, (Math.cos(th - 0.25) - 0.5) / 0.5) : 0;
      link([xc, Cy + dy, dz], P3(sp), 0.1, '#e3e8ea', {seg: 8}); link(P3(sp), P3(sp + 0.62), 0.46, '#c9d1d6', {seg: 18});
      for (const q of [0.42, 0.52, 0.6]) link(P3(sp + q), P3(sp + q + 0.05), 0.49, '#4a5259', {seg: 18});
      link(P3(0.8), P3(3.4), 0.58, '#9fd0e6', {seg: 20, glass: true});
      link(P3(3.4), P3(4.3), 0.64, fl > 0.02 ? mixc(P.head, '#ff9a3a', fl) : P.head, {seg: 14, e: fl * 0.8}); link(P3(4.3), P3(4.6), 0.42, P.cap, {seg: 12});
      if (fl > 0.02) { const p = P3(3.0); sph(...p, 0.22 + 0.4 * fl, '#ff8a2a', {e: 1, ns: 1}); sph(...p, 0.12 + 0.22 * fl, '#fff0a0', {e: 1, ns: 1}); }
      if (i === 1 && sg === banks[banks.length - 1]) { anc('head', P3(4.0)); anc('piston', P3(2.2)); }
    }
  }
  anc('crank', [x0 - 0.3, Cy, 0]); anc('flywheel', [len / 2 + 1.0, Cy, 0]); anc('block', [0, 0.85, 1.3]);
  link([len / 2 + 0.7, Cy, 0], [len / 2 + 1.05, Cy, 0], 1.0, '#8d9aa4', {seg: 24});
  for (let p = 0; p < 3; p++) { const a = cr + p * 2.094; box(len / 2 + 1.1, Cy + 0.72 * Math.cos(a), 0.72 * Math.sin(a), 0.07, 0.22, 0.22, '#ff9a2e', {ns: 1}); }
});

reg('motor', 'motor/generator listrik tembus pandang: rotor + kutub berputar, kumparan tembaga. param: w(rad/dtk 12), col, len(2.4), rad(1.2), axis(x)', (o) => {
  const Lm = o.len || 2.4, R = o.rad || 1.2, col = o.col || P.alt, w = o.w == null ? 12 : o.w, a0 = TT * w;
  box(0, -R * 0.55, 0, Lm * 0.9, R * 0.5, R * 1.6, '#3f4c55');
  link([-Lm / 2, 0, 0], [Lm / 2, 0, 0], R, col, {seg: 28, glass: true}); link([-Lm / 2 - 0.06, 0, 0], [-Lm / 2 + 0.1, 0, 0], R * 1.06, P.altD, {seg: 28}); link([Lm / 2 - 0.1, 0, 0], [Lm / 2 + 0.06, 0, 0], R * 1.06, P.altD, {seg: 28});
  link([-Lm / 2 - 0.9, 0, 0], [Lm / 2 + 0.9, 0, 0], 0.16, '#c9ced2', {seg: 12}); link([-Lm / 2 + 0.1, 0, 0], [Lm / 2 - 0.1, 0, 0], R * 0.36, '#c9ced2', {seg: 16});
  for (let p = 0; p < 4; p++) { const a = a0 + p * Math.PI / 2; box(0, R * 0.55 * Math.cos(a), R * 0.55 * Math.sin(a), Lm * 0.8, R * 0.25, R * 0.25, p % 2 ? '#e8403a' : '#8fb4ff', {ns: 1}); }
  for (const k of [-0.28, -0.08, 0.12, 0.32]) link([k * Lm, 0, 0], [k * Lm + 0.14, 0, 0], R * 0.8, P.copper, {seg: 24, glass: true});
  anc('rotor', [0, R * 0.55, 0]); anc('stator', [0, R, 0]); anc('shaft', [Lm / 2 + 0.9, 0, 0]);
});

reg('gear', 'roda gigi berputar. param: n(12) jumlah gigi, rad(1), w(rad/dtk 1.5), th(0.35 tebal), col. Pasangan gigi: dua gear dengan w berlawanan tanda & jarak rad1+rad2', (o) => {
  const n = o.n || 12, R = o.rad || 1, w = o.w == null ? 1.5 : o.w, th = o.th || 0.35, col = o.col || '#c9d1d6', a0 = TT * w + (o.ph || 0);
  cyl(0, 0, 0, R * 0.86, th, col, {rx: Math.PI / 2, seg: 28}); cyl(0, 0, 0, R * 0.25, th * 1.5, '#7b838e', {rx: Math.PI / 2, seg: 14});
  for (let i = 0; i < n; i++) { const a = a0 + i * 2 * Math.PI / n; box(Math.cos(a) * R * 0.95, Math.sin(a) * R * 0.95, 0, R * 0.26, R * 0.2, th, col, {rz: a}); }
  anc('hub', [0, 0, th]);
});

reg('fan', 'kipas/baling-baling berputar. param: n(4) bilah, rad(1), w(8), ax(y|x|z)', (o) => {
  const n = o.n || 4, R = o.rad || 1, w = o.w == null ? 8 : o.w, ax = o.ax || 'y', a0 = TT * w;
  pushM(ax === 'x' ? RZ(-Math.PI / 2) : ax === 'z' ? RX(Math.PI / 2) : IDM);
  cyl(0, 0, 0, R * 0.16, R * 0.3, '#444b51', {seg: 14});
  for (let i = 0; i < n; i++) box(0, 0, 0, R * 1.9, R * 0.03, R * 0.36, '#c7ced4', {ry: a0 + i * 2 * Math.PI / n});
  popM(); anc('hub', [0, R * 0.2, 0]);
});

reg('tank', 'tangki/gelas tembus pandang berisi cairan. param: size[w,h,d], lvl(0-1) atau lvlAnim[a,b,periode], col cairan, round(true)', (o) => {
  const [w, h, d] = o.size || [2, 3, 2]; let lv = o.lvl == null ? 0.6 : o.lvl; if (o.lvlAnim) { const [a, b, T0] = o.lvlAnim; lv = a + (b - a) * (0.5 - 0.5 * Math.cos(TT * 2 * Math.PI / (T0 || 8))); }
  const lc = o.col || '#3d9bd6';
  if (o.round === false) { box(0, h / 2, 0, w, h, d, '#cfe3ea', {glass: true}); if (lv > 0.01) box(0, h * lv / 2, 0, w * 0.96, h * lv, d * 0.96, lc, {glass: true}); }
  else { cyl(0, h / 2, 0, w / 2, h, '#cfe3ea', {glass: true, seg: 28}); if (lv > 0.01) cyl(0, h * lv / 2, 0, w / 2 * 0.95, h * lv, lc, {glass: true, seg: 28}); }
  cyl(0, 0.04, 0, w / 2 * 1.05, 0.08, '#5d6a72', {seg: 28});
  if (o.bubbles) for (let i = 0; i < 6; i++) { const t = fr(TT * 0.4 + i / 6); sph((i % 3 - 1) * w * 0.18, t * h * lv, ((i * 7) % 3 - 1) * d * 0.18, 0.07 + 0.05 * (i % 2), '#e8f6ff', {e: 0.6, ns: 1}); }
  anc('top', [0, h, 0]); anc('liquid', [0, h * lv, 0]);
});

reg('pump', 'pompa sentrifugal: impeller berputar di rumah pompa, pipa masuk/keluar dengan aliran. param: w(14)', (o) => {
  const w = o.w == null ? 14 : o.w, a0 = TT * w;
  box(0, 0.25, 0, 2.6, 0.5, 2.0, '#3f4c55');
  link([0, 1.1, -0.25], [0, 1.1, 0.25], 1.15, '#9fd0e6', {seg: 28, glass: true}); link([0, 1.1, -0.28], [0, 1.1, -0.18], 1.22, '#5d6a72', {seg: 28});
  for (let i = 0; i < 6; i++) { const a = a0 + i * Math.PI / 3; box(Math.cos(a) * 0.5, 1.1 + Math.sin(a) * 0.5, 0, 1.0, 0.1, 0.34, '#f08a1c', {rz: a, ns: 1}); }
  link([0, 1.1, 0.25], [0, 1.1, 1.3], 0.2, '#c9ced2'); box(0, 1.1, 1.5, 1.2, 1.2, 0.5, '#d94b3d');
  link([-3, 1.1, 0], [-1.1, 1.1, 0], 0.32, '#8fb4c9', {seg: 16}); link([0, 2.25, 0], [0, 3.6, 0], 0.32, '#8fb4c9', {seg: 16}); link([0, 3.6, 0], [2.6, 3.6, 0], 0.32, '#8fb4c9', {seg: 16});
  for (let i = 0; i < 5; i++) sph(-3 + fr(i / 5 + TT * 0.5) * 1.9, 1.1, 0, 0.17, '#bfe6ff', {e: 0.9, ns: 1});
  for (let i = 0; i < 5; i++) { const pts = [[0, 2.25, 0], [0, 3.6, 0], [2.6, 3.6, 0]], p = along(pts, fr(i / 5 + TT * 0.5)); sph(...p, 0.17, '#bfe6ff', {e: 0.9, ns: 1}); }
  anc('impeller', [0, 1.1, 0.3]); anc('inlet', [-3, 1.1, 0]); anc('outlet', [2.6, 3.6, 0]);
});

reg('wheel', 'roda dengan ban & jari-jari berputar. param: rad(0.55), w(rad/dtk), ax(z)', (o) => {
  const R = o.rad || 0.55, a0 = TT * (o.w == null ? 6 : o.w);
  pushM(o.ax === 'x' ? RY(Math.PI / 2) : IDM);
  link([0, 0, -0.12], [0, 0, 0.12], R, '#2b2f34', {seg: 28}); link([0, 0, -0.14], [0, 0, 0.14], R * 0.62, '#c9ced2', {seg: 24});
  for (let k = 0; k < 3; k++) box(0, 0, 0.14, R * 1.15, R * 0.12, 0.05, k === 0 ? '#ff9a2e' : '#7b838e', {rz: a0 + k * Math.PI / 3, ns: 1});
  popM();
});

reg('vehicle', 'mobil/bus/truk balok: body, kabin, kaca, 4 roda berputar. param: len(4), kind(car|bus|truck), col, wheels w', (o) => {
  const k = o.kind || 'car', Ln = o.len || (k === 'car' ? 4 : k === 'bus' ? 8 : 6), col = o.col || (k === 'bus' ? '#e8a31c' : k === 'truck' ? '#d94b3d' : '#2f66c9'), w = o.w == null ? 8 : o.w, h = k === 'car' ? 1.0 : 2.2;
  box(0, 0.45 + h / 2, 0, Ln, h, 2.0, col);
  if (k === 'car') { box(-0.2, 1.95, 0, Ln * 0.5, 0.9, 1.8, col); box(-0.2, 1.95, 0, Ln * 0.5 + 0.02, 0.6, 1.84, P.glass, {glass: true}); }
  else if (k === 'truck') { box(Ln * 0.3, 2.2, 0, Ln * 0.3, 1.6, 2.0, '#eef0ee'); box(-Ln * 0.12, 2.2, 0, Ln * 0.62, 2.0, 2.0, '#cfd6da'); box(Ln * 0.46, 2.4, 0, 0.05, 0.7, 1.6, P.glass, {glass: true}); }
  else box(0, 1.7, 1.01, Ln * 0.9, 0.7, 0.05, P.glass, {glass: true});
  box(Ln / 2 + 0.01, 0.9, 0.6, 0.05, 0.3, 0.4, '#fff3b0', {e: 1}); box(Ln / 2 + 0.01, 0.9, -0.6, 0.05, 0.3, 0.4, '#fff3b0', {e: 1});
  for (const x of [-Ln * 0.32, Ln * 0.32]) for (const z of [-1.0, 1.0]) { pushM(T(x, 0.5, z)); COMP.wheel({rad: 0.5, w: -w}); popM(); }
  anc('front', [Ln / 2, 1, 0]); anc('roof', [0, 0.45 + h, 0]);
});

reg('battery', 'baterai: sel-sel silinder dalam rumah tembus pandang dengan kutub +/-, indikator. param: n(3), lvl', (o) => {
  const n = o.n || 3; box(0, 0.7, 0, n * 0.9 + 0.3, 1.4, 1.2, '#cfe3ea', {glass: true});
  for (let i = 0; i < n; i++) { const x = (i - (n - 1) / 2) * 0.9; cyl(x, 0.65, 0, 0.36, 1.2, '#f2c21c', {seg: 18}); cyl(x, 1.38, 0, 0.14, 0.12, '#c9ced2', {seg: 10}); }
  box(0, 1.45, 0, n * 0.9 + 0.4, 0.1, 1.3, '#3f4c55'); const lv = o.lvl == null ? 0.5 + 0.5 * Math.sin(TT) : o.lvl;
  for (let i = 0; i < 4; i++) box(-0.6 + i * 0.4, 1.55, 0.62, 0.3, 0.1, 0.05, i / 4 < lv ? '#59d97a' : '#555a60', {e: i / 4 < lv ? 0.8 : 0});
  anc('plus', [-(n * 0.45), 1.5, 0]); anc('minus', [n * 0.45, 1.5, 0]);
});

reg('bulb', 'lampu pijar/LED: menyala bila on=true atau berkedip. param: on(true), col', (o) => {
  const on = o.on !== false, k = on ? 0.6 + 0.4 * Math.sin(TT * 5) * 0 + 0.4 : 0;
  cyl(0, 0.3, 0, 0.3, 0.6, '#9aa2ab', {seg: 12}); sph(0, 1.0, 0, 0.6, on ? (o.col || '#fff3a0') : '#dfe9ee', {e: on ? 0.9 : 0, glass: !on, seg: 20});
  if (on) { sph(0, 1.0, 0, 0.95, '#fff3a0', {glass: true, e: 0.6, seg: 14}); } link([-0.15, 0.6, 0], [0.15, 1.0, 0], 0.03, '#ffb53a', {e: 1}); anc('glass', [0, 1.0, 0.6]);
});

reg('atom', 'atom: inti + elektron mengorbit. param: e(3) elektron, rad(2)', (o) => {
  const e = o.e || 3, R = o.rad || 2;
  for (let i = 0; i < 4; i++) { const a = i * 2.1; sph(Math.cos(a) * 0.15, Math.sin(a) * 0.15, Math.cos(a * 2) * 0.15, 0.24, i % 2 ? '#e8403a' : '#8fb4ff', {seg: 12}); }
  for (let k = 0; k < e; k++) {
    const tilt = k * Math.PI / e; pushM(mm(RX(tilt), RZ(0.4 * k)));
    for (let s = 0; s < 40; s++) { const a = s / 40 * 2 * Math.PI; sph(Math.cos(a) * R, 0, Math.sin(a) * R, 0.025, '#b8c4cc', {ns: 1, seg: 6}); }
    const a = TT * (1.6 - k * 0.3) + k * 2; sph(Math.cos(a) * R, 0, Math.sin(a) * R, 0.2, '#ffe07a', {e: 0.8, ns: 1, seg: 12}); popM();
  }
  anc('nucleus', [0, 0, 0.3]);
});

reg('molecule', 'molekul: atoms=[{p,r,c}], ikatan otomatis antar atom berdekatan; berputar pelan. param: atoms, w(0.6)', (o) => {
  const at = o.atoms || [{p: [0, 0, 0], r: 0.6, c: '#e8403a'}, {p: [1.1, 0.7, 0], r: 0.38, c: '#eef0ee'}, {p: [-1.1, 0.7, 0], r: 0.38, c: '#eef0ee'}];
  pushM(RY(TT * (o.w == null ? 0.6 : o.w)));
  for (const a of at) sph(...a.p, a.r, a.c, {seg: 18});
  for (let i = 0; i < at.length; i++) for (let j = i + 1; j < at.length; j++) if (Math.hypot(...sub(at[i].p, at[j].p)) < (at[i].r + at[j].r) * 2.4) link(at[i].p, at[j].p, 0.09, '#9aa2ab', {seg: 8});
  popM();
});

reg('cell', 'sel biologi: membran tembus pandang, inti, organel bergerak. param: rad(2)', (o) => {
  const R = o.rad || 2; sph(0, 0, 0, R, '#9fe0b8', {glass: true, seg: 26}); sph(0.2, 0.1, 0, R * 0.32, '#7a5cc9', {seg: 18}); sph(0.2, 0.1, 0.2, R * 0.12, '#4d3a96', {seg: 10});
  for (let i = 0; i < 9; i++) { const a = i * 2.4 + TT * 0.3, rr_ = R * (0.45 + 0.3 * ((i * 37) % 10) / 10); sph(Math.cos(a) * rr_, Math.sin(a * 1.3) * rr_ * 0.6, Math.sin(a) * rr_ * 0.7, 0.12 + 0.08 * (i % 3), ['#f08a1c', '#e8403a', '#f2c21c'][i % 3], {seg: 10, ns: 1}); }
  anc('nucleus', [0.2, 0.1, R * 0.32]); anc('membrane', [R, 0, 0]);
});

reg('house', 'rumah balok dengan atap & jendela. param: size[w,h,d], col, open(0-1 atau [t0,t1] waktu adegan: dinding depan digulung)', (o) => {
  const [w, h, d] = o.size || [6, 3, 5], col = o.col || '#efe6d6'; let op = 0; if (Array.isArray(o.open)) op = sm((TS - o.open[0]) / Math.max(0.3, o.open[1] - o.open[0])); else if (o.open) op = o.open;
  box(0, 0.1, 0, w + 0.3, 0.2, d + 0.3, '#8b8a84'); box(0, h / 2, -d / 2, w, h, 0.2, col); box(-w / 2, h / 2, 0, 0.2, h, d, col); box(w / 2, h / 2, 0, 0.2, h, d, col);
  const hh = h * (1 - op) + 0.02; if (op < 0.98) { box(0, h - hh / 2, d / 2, w, hh, 0.2, col); if (op < 0.5) { box(-w * 0.2, h * 0.5 + op * h, d / 2 + 0.12, 1.0, 1.1, 0.06, P.glass, {glass: true}); box(w * 0.25, h * 0.4 + op * h, d / 2 + 0.12, 0.9, 1.7, 0.06, '#7a5a3a'); } }
  box(0, h + 0.1 + op * 5, 0, w + 0.6, 0.2, d + 0.6, '#cfd3d6'); cyl(0, h + 0.9 + op * 5, 0, Math.max(w, d) * 0.78, 1.5, '#c8553a', {seg: 4, rt: 0.1, rb: 1, ry: Math.PI / 4});
  anc('inside', [0, h * 0.4, 0]); anc('roof', [0, h + 1.2, 0]);
});

reg('tree', 'pohon low-poly. param: h(5)', (o) => { const h = o.h || 5; cyl(0, 0.9, 0, 0.18 * h / 4, 1.8, '#6b4c33', {seg: 6}); cyl(0, 0.8 + h / 2 + 0.7, 0, h * 0.35, h, o.col || '#4f8a45', {rt: 0.02, rb: 1, seg: 9}); });

reg('person', 'orang low-poly yang berjalan (anggota badan berayun). param: col baju, walk(true)', (o) => {
  const sw = o.walk === false ? 0 : Math.sin(TT * 6) * 0.5, col = o.col || '#2f66c9';
  for (const s of [-1, 1]) { pushM(T(0, 1.0, s * 0.18)); pushM(RZ(sw * s)); box(0, -0.45, 0, 0.2, 0.9, 0.2, '#2b3a55'); popM(); popM(); pushM(T(0, 1.9, s * 0.42)); pushM(RZ(-sw * s)); box(0, -0.4, 0, 0.16, 0.8, 0.16, col); popM(); popM(); }
  box(0, 1.55, 0, 0.4, 0.95, 0.6, col); sph(0, 2.3, 0, 0.26, '#f2c9a0', {seg: 12}); cyl(0, 2.5, 0, 0.27, 0.12, '#ffd23a', {seg: 12});
});

reg('solar', 'panel surya miring dengan sel dan sinar matahari mengalir. param: n(3) panel, sun(true)', (o) => {
  const n = o.n || 3; pushM(RX(-0.7));
  for (let i = 0; i < n; i++) { const x = (i - (n - 1) / 2) * 2.1; box(x, 1.6, 0, 2.0, 0.08, 3.0, '#1d3f86'); for (let a = 1; a < 4; a++) box(x, 1.66, -1.5 + a * 0.75, 2.0, 0.03, 0.04, '#cfe0f5', {ns: 1}); for (let b = -1; b <= 1; b += 1) box(x + b * 0.65, 1.66, 0, 0.04, 0.03, 3.0, '#cfe0f5', {ns: 1}); }
  popM(); box(0, 0.6, 1.2, 0.2, 1.2, 0.2, '#8c8f94');
  if (o.sun !== false) { sph(-6, 9, -4, 1.1, '#ffd23a', {e: 1, ns: 1}); for (let i = 0; i < 6; i++) { const p = along([[-6, 9, -4], [0, 2.5, 0.8]], fr(i / 6 + TT * 0.4)); sph(...p, 0.18, '#fff3a0', {e: 1, ns: 1}); } }
  anc('panel', [0, 2.2, 0.8]);
});

reg('shell', 'selubung/ casing yang DIBUKA (dibedah): dinding depan digulung ke atas, atap terangkat, isi terlihat. param: size[w,h,d], col, open=[t0,t1] waktu adegan', (o) => {
  const [w, h, d] = o.size || [6, 3, 3], col = o.col || '#1d3f86'; let op = 0; if (Array.isArray(o.open)) op = sm((TS - o.open[0]) / Math.max(0.3, o.open[1] - o.open[0])); else if (o.open != null) op = o.open;
  box(0, 0.1, 0, w, 0.2, d, '#4e535b'); box(0, h / 2, -d / 2, w, h, 0.12, col); box(-w / 2, h / 2, 0, 0.12, h, d, col); box(w / 2, h / 2, 0, 0.12, h, d, col);
  const hh = h * (1 - op) + 0.02; if (op < 0.98) box(0, h - hh / 2, d / 2, w, hh, 0.12, col);
  box(0, h + 0.07 + op * 6, 0, w + 0.1, 0.14, d + 0.1, '#eef0ee'); anc('inside', [0, h * 0.45, 0]); anc('top', [0, h, 0]);
});

reg('radiator', 'penukar panas/radiator/evaporator bersirip dengan aliran fluida. param: size[w,h], hot(true)', (o) => {
  const [w, h] = o.size || [2.6, 2.4], hot = o.hot !== false; box(0, h / 2, 0, w, h, 0.3, '#7ec3e6');
  for (let i = 0; i < 12; i++) box(-w / 2 + (i + 0.5) * w / 12, h / 2, 0.17, 0.05, h * 0.95, 0.05, '#4a97bd');
  const pts = []; for (let r = 0; r < 4; r++) { const y = 0.3 + r * (h - 0.6) / 3; pts.push([-w / 2 + 0.2, y, 0.3], [w / 2 - 0.2, y, 0.3]); }
  path(pts, 0.05, hot ? '#d94b3d' : '#2f8fbf'); for (let i = 0; i < 10; i++) sph(...along(pts, fr(i / 10 + TT * 0.25)), 0.11, hot ? '#ffb199' : '#bfe6ff', {e: 0.9, ns: 1}); anc('core', [0, h / 2, 0.35]);
});

reg('compressor', 'kompresor/silinder penekan: piston bolak-balik di dalam silinder tembus pandang. param: w(6)', (o) => {
  const w = o.w == null ? 6 : o.w, x = 0.55 * Math.sin(TT * w);
  cyl(0, 0.5, 0, 0.9, 1.0, '#3f4c55', {seg: 22}); link([-1.9, 1.15, 0], [1.9, 1.15, 0], 0.7, '#9fd0e6', {seg: 22, glass: true}); link([1.9, 1.15, 0], [2.3, 1.15, 0], 0.55, '#6f7e88', {seg: 18});
  link([x - 0.9, 1.15, 0], [x - 0.2, 1.15, 0], 0.66, '#c9d1d6', {seg: 22}); link([x - 1.8, 1.15, 0], [x - 0.9, 1.15, 0], 0.1, '#e3e8ea', {seg: 8}); sph(x - 1.85, 1.15, 0, 0.18, '#ff9a2e', {ns: 1});
  const comp = 0.5 + 0.5 * Math.sin(TT * w); sph(1.0, 1.15, 0, 0.25 + 0.35 * comp, comp > 0.6 ? '#ff8a2a' : '#bfe6ff', {e: 0.7, ns: 1}); anc('piston', [x - 0.5, 1.5, 0]); anc('outlet', [2.3, 1.15, 0]);
});

reg('pipe', 'pipa/kabel dengan aliran pulsa. param: pts[[x,y,z]...], r(0.1), c pipa, fc warna pulsa, n(8), w(0.5)', (o) => {
  const pts = o.pts || [[0, 0, 0], [2, 0, 0]]; path(pts, o.r || 0.1, o.c || '#ff8b1f', {e: 0.45});
  for (let i = 0; i < (o.n || 8); i++) sph(...along(pts, fr(i / (o.n || 8) + TT * (o.w == null ? 0.5 : o.w))), (o.r || 0.1) * 1.6, o.fc || '#ffe07a', {e: 1, ns: 1});
});

reg('sun', 'matahari bercahaya. param: rad(1.2)', (o) => { sph(0, 0, 0, o.rad || 1.2, '#ffd23a', {e: 1, ns: 1, seg: 20}); sph(0, 0, 0, (o.rad || 1.2) * 1.5, '#fff3a0', {glass: true, e: 0.6, seg: 14}); });
reg('cloud', 'awan; hujan bila rain=true. param: rain', (o) => { for (const [x, y, r] of [[0, 0, 1.1], [1.1, -0.1, 0.9], [-1.1, -0.1, 0.9], [0.4, 0.5, 0.8]]) sph(x, y, 0, r, '#f4f8fb', {seg: 12, ns: 1}); if (o.rain) for (let i = 0; i < 14; i++) { const t = fr(TT * 0.9 + i * 0.137); sph(-1.6 + (i % 7) * 0.55, -0.9 - t * 6, ((i * 3) % 5) * 0.2 - 0.4, 0.07, '#8fc4ff', {e: 0.8, ns: 1, seg: 6}); } });
reg('planet', 'planet/bola berputar dengan cincin opsional. param: rad(1.5), col, ring', (o) => { pushM(RY(TT * 0.4)); sph(0, 0, 0, o.rad || 1.5, o.col || '#4f8aa6', {seg: 24}); box(0.6, 0.4, 0.5, 0.9, 0.9, 0.9, '#8fb08a', {ns: 1}); popM(); if (o.ring) cyl(0, 0, 0, (o.rad || 1.5) * 1.8, 0.04, '#d9c9a0', {seg: 40, ns: 1}); });
reg('spring', 'pegas bergetar naik-turun. param: h(2), coils(7)', (o) => { const h = (o.h || 2) * (0.85 + 0.15 * Math.sin(TT * 5)), n = o.coils || 7; for (let i = 0; i < n * 8; i++) { const a = i / 8 * 2 * Math.PI, b = (i + 1) / 8 * 2 * Math.PI; link([Math.cos(a) * 0.5, i / (n * 8) * h, Math.sin(a) * 0.5], [Math.cos(b) * 0.5, (i + 1) / (n * 8) * h, Math.sin(b) * 0.5], 0.06, '#c9d1d6', {seg: 6}); } box(0, h + 0.1, 0, 1.3, 0.14, 1.3, '#7b838e'); box(0, -0.05, 0, 1.3, 0.14, 1.3, '#7b838e'); });
reg('heart', 'organ berdenyut sederhana (jantung/paru-paru/lambung) bentuk bulat + pembuluh; param: col, beat(1.2)', (o) => { const s = 1 + 0.08 * Math.max(0, Math.sin(TT * 2 * Math.PI * (o.beat || 1.2))) * 2; sph(-0.3, 0, 0, 0.9 * s, o.col || '#d94b3d', {seg: 18}); sph(0.5, 0.1, 0, 0.75 * s, o.col || '#c23b3b', {seg: 18}); link([0, 0.7, 0], [0, 1.7, 0], 0.22 * s, '#b83232'); link([0.4, 0.7, 0], [0.9, 1.6, 0], 0.18 * s, '#3d6fc9'); const pts = [[0, 1.7, 0], [0, 2.4, 0.3]]; for (let i = 0; i < 4; i++) sph(...along(pts, fr(i / 4 + TT * 0.6)), 0.1, '#ffb199', {e: 0.9, ns: 1}); });

// ----- animasi & primitif -----
function animM(an, c) {
  let M = IDM; if (!an) return M;
  if (an.osc) { const a = an.osc, v = (a.amp || 1) * Math.sin(TT * (a.w || 2) + (a.ph || 0)), e = AX[a.ax || 'y']; M = mm(T(e[0] * v, e[1] * v, e[2] * v), M); }
  if (an.orbit) { const a = an.orbit, ang = TT * (a.w || 1) + (a.ph || 0), r = a.r || 2; const off = (a.ax || 'y') === 'y' ? [Math.cos(ang) * r, 0, Math.sin(ang) * r] : (a.ax === 'x' ? [0, Math.cos(ang) * r, Math.sin(ang) * r] : [Math.cos(ang) * r, Math.sin(ang) * r, 0]); M = mm(T(...off), M); }
  if (an.rot) { const a = an.rot, p = a.c || c || [0, 0, 0]; M = mm(M, mm(T(p[0], p[1], p[2]), mm(Rax(a.ax || 'y', TT * (a.w || 1) + (a.ph || 0)), T(-p[0], -p[1], -p[2])))); }
  return M;
}
function buildObj(o, i) {
  CURID = o.id || ('o' + i); const an = o.anim || {};
  if (an.show && (TS < an.show[0] || TS > an.show[1])) return;
  const t = o.t || o.k, ph = Array.isArray(o.p) ? o.p : [0, 0, 0], cid = CURID;
  const needLocal = ['comp', 'group'].includes(t) || (COMP[t] && !['box', 'cyl', 'sph', 'link', 'path', 'flow'].includes(t));
  let M = animM(an, ph);
  if (needLocal) { M = T(ph[0], ph[1], ph[2]); if (o.ry || o.rx || o.rz) M = mm(M, mm(RY(o.ry || 0), mm(RX(o.rx || 0), RZ(o.rz || 0)))); if (o.s) M = mm(M, Array.isArray(o.s) ? S(...o.s) : S(o.s, o.s, o.s)); M = mm(M, animM(an, [0, 0, 0])); }
  pushM(M);
  const c = o.c || '#8d9aa4', e = o.e || 0, f = {glass: !!o.glass, e, ry: o.ry || 0, rx: o.rx || 0, rz: o.rz || 0, ns: o.ns ? 1 : 0, seg: o.seg};
  if (t === 'box') box(ph[0], ph[1], ph[2], ...(o.s || [1, 1, 1]), c, f);
  else if (t === 'cyl') cyl(ph[0], ph[1], ph[2], o.r || 0.5, o.h || 1, c, Object.assign(f, {rt: o.rt, rb: o.rb}));
  else if (t === 'sph') sph(ph[0], ph[1], ph[2], o.r || 0.5, c, f);
  else if (t === 'link') link(o.a || [0, 0, 0], o.b || [0, 1, 0], o.r || 0.1, c, f);
  else if (t === 'path') path(o.pts || [], o.r || 0.1, c, f);
  else if (t === 'flow') { const pts = o.pts || [[0, 0, 0], [1, 0, 0]], n = Math.min(40, o.n || 6); for (let k = 0; k < n; k++) sph(...along(pts, fr(k / n + TT * (o.w == null ? 0.5 : o.w))), o.r || 0.15, o.c || '#ffe07a', {e: 1, ns: 1}); }
  else if (t === 'group') (o.kids || []).forEach((k, j) => buildObj(k, i + '_' + j));
  else if (COMP[t] || COMP[o.k]) { CURID = cid; ANCH[cid] = wpt([0, o.ah != null ? o.ah : 1, 0]); (COMP[t] || COMP[o.k])(o, cid); }
  popM();
}
