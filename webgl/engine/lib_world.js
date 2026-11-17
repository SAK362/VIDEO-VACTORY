const AN = {wa: 0, fa: 0, ph: 0, cr: 0, goff: 0};
function wheelMarks(ax, s) {
  const zc = s * 0.64;
  for (let k = 0; k < 3; k++) box(ax, 0.55, zc, 0.92, 0.1, 0.05, k === 0 ? '#ff9a2e' : '#c5ccd2', {rz: AN.wa + k * Math.PI / 3, ns: 1});
  cyl(ax, 0.55, s * 0.655, 0.16, 0.06, '#e8edf0', {rx: Math.PI / 2, seg: 10, ns: 1});
}
// ---------- world pieces ----------
function groundBase(o = {}) {
  box(0, -0.75, 0, 600, 0.5, 600, o.grass || P.grass, {ns: 1});
  { const R = rng(21); for (let i = 0; i < 90; i++) { const x = -90 + R() * 180, z = (R() < .5 ? -1 : 1) * (6 + R() * 60); box(x, -0.495, z, 6 + R() * 22, 0.02, 5 + R() * 16, ['#6a9648', '#78a251', '#557f41', '#86a95a', '#6f8f47'][i % 5], {ns: 1}); } }
  box(0, -0.335, 0, 600, 0.33, 3.3, P.ballast, {ns: 1});
  box(0, -0.335, 0, 600, 0.3, 4.1, '#7d7a74', {ns: 1});
  for (const s of [-1, 1]) box(0, -0.085, s * 0.5335, 600, 0.17, 0.075, P.rail, {ns: 1});
  const x0 = o.x0 == null ? -60 : o.x0, x1 = o.x1 == null ? 70 : o.x1;
  const gsh = ((AN.goff % 0.65) + 0.65) % 0.65; for (let x = x0 + gsh - 0.65; x < x1; x += 0.65) box(x, -0.25, 0, 0.24, 0.16, 2.35, P.sleeper, {ns: 1});
}
const wr = x => (((x + AN.goff + 100) % 200) + 200) % 200 - 100;
function scenery(seed, o = {}) {
  const R = rng(seed);
  for (const h of [[-60, -120, 90, 24], [20, -140, 120, 30], [110, -110, 80, 22], [-150, -90, 90, 26]]) cyl(h[0], h[3] / 2 - 1, h[1], 1, h[3], '#79a176', {rt: .05, rb: 1, seg: 14, ns: 1, ry: 0}), 0;
  for (let i = 0; i < 110; i++) {
    const side = R() < .72 ? -1 : 1, z = side * (side < 0 ? 7 + R() * 40 : 22 + R() * 30), x = wr(-100 + R() * 200), hh = 3 + R() * 4, g = R() < .5 ? '#4f8a45' : '#5d9a4c';
    cyl(x, 0.9, z, 0.18, 1.8, '#6b4c33', {seg: 6, ns: 0}); cyl(x, 0.8 + hh / 2 + 0.7, z, hh * 0.35, hh, g, {rt: .02, rb: 1, seg: 9});
  }
  if (o.houses !== false) for (let i = 0; i < 14; i++) { const x = wr(-100 + i * 14.3 + R() * 5), z = -(13 + R() * 10), w = 5 + R() * 2, d = 4 + R() * 2; box(x, 1.3, z, w, 2.6, d, ['#efe6d6', '#f2e0c4', '#e9d9c9'][i % 3]); cyl(x, 3.3, z, Math.max(w, d) * 0.78, 1.5, '#c8553a', {seg: 4, rt: .1, rb: 1, ry: Math.PI / 4}); box(x, 1.0, z + d / 2 + .02, 0.9, 1.6, 0.06, '#7a5a3a'); }
  if (o.poles !== false) for (let k = 0; k < 10; k++) { const x = wr(-100 + k * 20); cyl(x, 4.0, -4.6, 0.12, 8, '#8c8f94', {seg: 6}); box(x, 7.4, -4.6, 0.12, 0.12, 2.6, '#8c8f94'); for (const dz of [-1.1, 0, 1.1]) link([x, 7.4, -4.6 + dz], [x + 20, 7.4, -4.6 + dz], 0.025, '#2b2f34', {seg: 4}); }
}
const mixc = (a, b, u) => { a = C(a); b = C(b); return [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u]; };
