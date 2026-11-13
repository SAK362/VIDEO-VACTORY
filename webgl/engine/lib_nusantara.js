// ---------- Pustaka komponen NUSANTARA: Rumah Gadang, Borobudur, Pinisi, kereta cepat ----------
// Satuan ~ meter. Tanah y=0. Setiap komponen punya jangkar (anc) untuk label.
const tIn = (v, d) => Array.isArray(v) ? sm((TS - v[0]) / Math.max(0.3, v[1] - v[0])) : (v || d || 0);
const WOOD = ['#7a4a2b', '#6b3f24', '#8a5732'], WOODL = '#b8864b';

// ===== RUMAH GADANG =====
reg('rumah_gadang', 'Rumah Gadang Minangkabau: rumah panggung, tiang diletakkan di atas batu sandi (tanpa ditanam), sambungan pasak, tiang luar miring, atap ijuk bergonjong. Sumbu x = panjang. param: ex (tampak terurai 0-1 atau [t0,t1]), shake (amplitudo gempa 0-1 atau [t0,t1] atur waktu aktif), amp. jangkar: batu, tiang, pasak, atap, kolong, lantai, tiangmiring', (o) => {
  const ex = tIn(o.ex), sk = tIn(o.shake), L = 12, Wd = 5.6, H = 2.6;
  const dx = sk * Math.sin(TT * 13) * (o.amp || 0.28) * (0.6 + 0.4 * Math.sin(TT * 5.1)), cols = 5, rows = 3;
  const xs = Array.from({length: cols}, (_, i) => -L / 2 + 1 + i * (L - 2) / (cols - 1)), zs = [-Wd / 2 + 0.4, 0, Wd / 2 - 0.4];
  for (const x of xs) for (const z of zs) { cyl(x, 0.12, z, 0.62, 0.24, '#a6a39a', {seg: 12}); cyl(x, 0.26, z, 0.5, 0.06, '#8d8a82', {seg: 12}); }
  anc('batu', [xs[1], 0.25, zs[2]]);
  pushM(T(dx, 0, 0));
  for (const x of xs) for (let r = 0; r < rows; r++) {
    const z = zs[r], tilt = r === 1 ? 0 : (r === 0 ? -1 : 1) * 0.11, wob = sk * 0.05 * Math.sin(TT * 13);
    pushM(T(x, 0.28, z)); pushM(RX(tilt + wob)); cyl(0, H / 2, 0, 0.2, H, WOOD[(((r + Math.round(x)) % 3) + 3) % 3], {seg: 8}); popM(); popM();
    if (r !== 1 && x === xs[1]) anc('tiangmiring', [x, H * 0.5, z + (r === 0 ? 1 : -1) * 0.0]);
  }
  anc('tiang', [xs[3], H * 0.55, zs[1]]); anc('kolong', [0, 1.0, zs[2] + 0.2]);
  pushM(T(0, ex * 1.4, 0));
  box(0, H + 0.45, 0, L + 0.9, 0.22, Wd + 0.8, WOODL); // lantai
  anc('lantai', [-L / 2 - 0.3, H + 0.5, Wd / 2 + 0.2]);
  for (const x of xs) for (const z of zs) { box(x, H + 0.34, z, 0.28, 0.12, 0.28, '#f0a53a'); }
  for (let i = 0; i < 2; i++) for (const x of xs.slice(0, 4)) box(x + (L - 2) / 6, H + 0.34, i === 0 ? zs[0] : zs[2], 0.2, 0.2, 0.2, '#f0a53a'), 0;
  anc('pasak', [xs[2], H + 0.34, zs[2]]);
  popM();
  pushM(T(0, ex * 2.8, 0));
  box(0, H + 1.55, Wd / 2 + 0.04, L, 2.0, 0.14, '#9b5a30'); box(0, H + 1.55, -Wd / 2 - 0.04, L, 2.0, 0.14, '#8a4f2a'); // dinding
  for (let i = 0; i < 9; i++) { const x = -L / 2 + 0.9 + i * 1.3; box(x, H + 1.55, Wd / 2 + 0.13, 0.4, 1.6, 0.05, '#d9a441'); box(x, H + 2.0, Wd / 2 + 0.13, 0.7, 0.18, 0.05, '#d4402e'); }
  box(L / 2 + 0.04, H + 1.55, 0, 0.14, 2.0, Wd, '#9b5a30'); box(-L / 2 - 0.04, H + 1.55, 0, 0.14, 2.0, Wd, '#9b5a30');
  popM();
  pushM(T(0, ex * 5.5, 0));
  const y0 = H + 2.55; // atap ijuk: dua lereng + ujung gonjong
  for (const s of [-1, 1]) { pushM(T(0, y0 + 0.7, s * Wd * 0.28)); pushM(RX(-s * 0.55)); box(0, 0, 0, L * 0.86, 0.3, Wd * 0.62, '#2b2622'); popM(); popM(); }
  box(0, y0 + 1.55, 0, L * 0.86, 0.16, 0.5, '#1f1b18');
  for (const s of [-1, 1]) {
    const gx = s * L * 0.43; path([[gx, y0 + 0.6, -Wd * 0.3], [gx + s * 0.35, y0 + 1.5, -Wd * 0.2], [gx + s * 1.1, y0 + 2.5, -Wd * 0.1], [gx + s * 1.9, y0 + 3.5, 0]], 0.22, '#2b2622', {seg: 6});
    path([[gx, y0 + 0.6, Wd * 0.3], [gx + s * 0.35, y0 + 1.5, Wd * 0.2], [gx + s * 1.1, y0 + 2.5, Wd * 0.1], [gx + s * 1.9, y0 + 3.5, 0]], 0.22, '#2b2622', {seg: 6});
    for (const z of [-1, 0, 1]) path([[gx + s * 0.2, y0 + 1.2, z * 0.8], [gx + s * 1.5, y0 + 3.0, 0]], 0.13, '#3a322c', {seg: 5});
  }
  anc('atap', [0, y0 + 1.7, 0]);
  popM();
  popM();
});

// ===== BOROBUDUR (tampak luar) =====
reg('borobudur', 'Candi Borobudur: enam teras persegi + tiga teras bundar + stupa induk, seratus pancuran makara di sudut dan sisi teras. param: rain (hujan 0/1), flow(aliran air di pancuran 0/1). jangkar: spout, tier, stupa, base', (o) => {
  const sq = [34, 30, 26, 22, 18, 14], hh = 1.9; let y = 0;
  box(0, 0.35, 0, 36, 0.7, 36, '#8c8579'); y = 0.7;
  sq.forEach((w, i) => {
    box(0, y + hh / 2, 0, w, hh, w, i % 2 ? '#a79e90' : '#9c9385');
    box(0, y + hh + 0.12, 0, w + 0.5, 0.24, w + 0.5, '#b3aa9b');
    for (const s of [-1, 1]) { box(0, y + hh + 0.65, s * (w / 2 - 0.5), w - 1, 0.7, 0.3, '#bdb4a4'); box(s * (w / 2 - 0.5), y + hh + 0.65, 0, 0.3, 0.7, w - 1, '#bdb4a4'); }
    for (let k = -3; k <= 3; k++) for (const s of [-1, 1]) { box(k * (w / 8), y + hh * 0.55, s * (w / 2 + 0.02), 1.5, 1.0, 0.1, '#7f776b'); box(s * (w / 2 + 0.02), y + hh * 0.55, k * (w / 8), 0.1, 1.0, 1.5, '#7f776b'); }
    for (const sx of [-1, 1]) for (const sz of [-1, 1]) { const px = sx * (w / 2 + 0.3), pz = sz * (w / 2 + 0.3); box(px, y + hh * 0.35, pz, 0.7, 0.45, 0.7, '#2f2b27'); }
    y += hh + 0.5;
    if (i === 2) anc('tier', [w / 2, y - 1, 0]);
  });
  const rr = [11, 8.5, 6]; rr.forEach((r, i) => {
    cyl(0, y + 0.45, 0, r, 0.9, '#b0a799', {seg: 28}); cyl(0, y + 0.95, 0, r * 0.93, 0.2, '#c0b7a8', {seg: 28});
    const n = [16, 12, 8][i]; for (let k = 0; k < n; k++) { const a = k / n * 6.2832; const px = Math.cos(a) * r * 0.72, pz = Math.sin(a) * r * 0.72; cyl(px, y + 1.55, pz, 0.62, 1.1, '#a39a8c', {seg: 8, rt: 0.55, rb: 1}); cyl(px, y + 2.3, pz, 0.3, 0.5, '#bfb6a6', {seg: 8, rt: 0.1, rb: 1}); }
    y += 1.0;
  });
  cyl(0, y + 1.6, 0, 3.4, 3.2, '#b7ae9f', {seg: 24, rt: 0.5, rb: 1}); cyl(0, y + 3.9, 0, 0.3, 1.4, '#c4bbab', {seg: 8});
  anc('stupa', [0, y + 3.0, 0]); anc('base', [18, 0.5, 0]);
  const sp = []; // pancuran makara: sudut + titik sepanjang sisi teras
  let yy = 0.7; sq.forEach((w, i) => { const top = yy + hh + 0.5; for (const sx of [-1, 1]) for (const sz of [-1, 1]) sp.push([sx * (w / 2 + 0.3), top - 0.55, sz * (w / 2 + 0.3), sx, sz]); for (const s of [-1, 1]) for (const k of [-2, 2]) { sp.push([k * w / 6, top - 0.55, s * (w / 2 + 0.3), 0, s]); sp.push([s * (w / 2 + 0.3), top - 0.55, k * w / 6, s, 0]); } yy = top; });
  sp.forEach((p, i) => {
    const dx = p[3], dz = p[4]; box(p[0] + dx * 0.4, p[1], p[2] + dz * 0.4, 0.5 + 0.4 * Math.abs(dx), 0.4, 0.5 + 0.4 * Math.abs(dz), '#2a2623');
    if (o.flow) { const k = fr(TT * 0.9 + i * 0.13); sph(p[0] + dx * (0.9 + k * 0.5), p[1] - 0.2 - k * k * 3.2, p[2] + dz * (0.9 + k * 0.5), 0.15, '#7cc3ee', {e: 1, ns: 1}); }
    if (i === 5) anc('spout', [p[0] + dx * 0.5, p[1], p[2] + dz * 0.5]);
  });
  if (o.rain) { const R = rng(5); for (let k = 0; k < 60; k++) { const f = fr(TT * 1.1 + R()), x = -20 + R() * 40, z = -20 + R() * 40; box(x, 26 - f * 26, z, 0.06, 0.9, 0.06, '#9bd0f0', {e: 1, ns: 1}); } }
});

// ===== BOROBUDUR: penampang sistem air =====
reg('boro_drain', 'penampang sistem drainase Borobudur (irisan tipis): batu andesit, lapisan penyaring, lapisan kedap air, lantai beton, pipa, pancuran; air hujan mengalir. param: t(0-1 hujan mengalir), flow. jangkar: stone, filter, seal, slab, pipe, spout, rain, core', (o) => {
  const W = 12, Dz = 3;
  box(0, 1.2, 0, W, 2.4, Dz, '#7a5a3e'); anc('core', [-W * 0.3, 1.2, Dz / 2]);
  const top = 2.4;
  box(0, top + 0.18, 0, W, 0.36, Dz, '#d9c27a'); anc('filter', [-W * 0.35, top + 0.18, Dz / 2]);
  box(0, top + 0.5, 0, W, 0.24, Dz, '#2f5f8f'); anc('seal', [-W * 0.35, top + 0.5, Dz / 2]);
  box(0, top + 0.82, 0, W, 0.4, Dz, '#9aa0a6'); anc('slab', [-W * 0.35, top + 0.82, Dz / 2]);
  box(-W / 2 + 2.2, top + 1.7, 0, 4.4, 1.4, Dz, '#a79e90'); anc('stone', [-W / 2 + 2.2, top + 1.7, Dz / 2]);
  box(W / 2 - 1.2, top + 1.7, 0, 2.4, 1.4, Dz, '#a79e90');
  link([-1.0, top + 1.1, 0], [W / 2 + 1.2, top + 1.1, 0], 0.2, '#e8edf0', {seg: 10}); anc('pipe', [W / 2 - 3, top + 1.15, Dz / 2 + 0.2]);
  box(W / 2 + 0.6, top + 0.6, 0, 1.5, 0.5, 0.9, '#2a2623'); anc('spout', [W / 2 + 1.5, top + 0.6, Dz / 2]);
  const n = 10; for (let k = 0; k < n; k++) { const f = fr(TT * 0.7 + k / n); sph(-3 + k * 0.7 - 0.5, top + 7 - f * 5.6, Dz / 2 - 0.2 + (k % 3) * 0.4, 0.14, '#7cc3ee', {e: 1, ns: 1}); }
  anc('rain', [-3, top + 6, Dz / 2]);
  const fl = [[-1.2, top + 1.5, 0], [-1.0, top + 1.1, 0], [W / 2 - 1, top + 1.1, 0], [W / 2 + 1.6, top + 1.1, 0], [W / 2 + 1.9, top - 1.0, 0]];
  for (let k = 0; k < 8; k++) sph(...along(fl, fr(TT * 0.4 + k / 8)), 0.17, '#7cc3ee', {e: 1, ns: 1});
});

// ===== KAPAL PINISI =====
reg('pinisi', 'kapal pinisi Bulukumba: lunas, gading (rangka), papan lambung, pasak kayu, dua tiang dengan tujuh layar (3 depan, 2 tengah, 2 belakang). Sumbu x, haluan +x. param: build (0-6 atau [t0,t1] -> 0-6: lunas, gading, papan, pasak, tiang, layar), sail (layar penuh). jangkar: keel, rib, plank, pasak, mast, sail, bow', (o) => {
  let b = Array.isArray(o.build) ? sm((TS - o.build[0]) / Math.max(0.3, o.build[1] - o.build[0])) * 6 : (o.build == null ? 6 : o.build);
  const L = 16, B = 2.6, D = 2.0, ns = 17, step = L / (ns - 1), nP = 11, roll = Math.sin(TT * 0.9) * 0.025;
  pushM(RX(roll));
  const prof = (x, a) => { const u = x / (L / 2), br = B * Math.pow(Math.max(0, 1 - u * u), 0.55) + 0.08, dp = D * (1 - 0.4 * Math.abs(u)); return [x, 1.6 + dp * 0.02 - dp * Math.cos(a) * (0.45 + 0.55 * Math.abs(Math.cos(a))) + dp * 0.95, br * Math.sin(a)]; };
  const hullPt = (x, a) => { const u = x / (L / 2), br = B * Math.pow(Math.max(0, 1 - u * u), 0.5) + 0.05, dp = D * (1 - 0.35 * Math.abs(u * u)), top = 2.0 + 0.8 * u * u * Math.sign(u + 1e-6) * (u > 0 ? 1.6 : 0.5); return [x, top - dp * Math.cos(a), br * Math.sin(a)]; };
  const ang = Array.from({length: nP + 1}, (_, j) => -1.35 + j * 2.7 / nP);
  // lunas
  if (b > 0) { const f = Math.min(1, b); path(Array.from({length: ns}, (_, i) => { const x = -L / 2 + i * step; return [x * f + (f < 1 ? 0 : 0), hullPt(x, 0)[1] - 0.05, 0]; }).filter((p, i) => i <= Math.round(f * (ns - 1))), 0.17, '#5b3a22', {seg: 6}); anc('keel', [0, hullPt(0, 0)[1] - 0.05, 0]); const kb = hullPt(L / 2, 0); path([[L / 2, hullPt(L / 2, 0)[1] - 0.05, 0], [L / 2 + 0.7, 3.0, 0], [L / 2 + 1.4, 4.1, 0]], 0.16, '#5b3a22', {seg: 6}); path([[-L / 2, hullPt(-L / 2, 0)[1] - 0.05, 0], [-L / 2 - 0.3, 2.4, 0], [-L / 2 - 0.4, 3.0, 0]], 0.16, '#5b3a22', {seg: 6}); anc('bow', [L / 2 + 1.4, 4.1, 0]); }
  // gading (rangka)
  if (b > 1) { const f = Math.min(1, b - 1); for (let i = 1; i < ns - 1; i += 2) { if ((i - 1) / (ns - 2) > f) break; const x = -L / 2 + i * step; path(ang.map(a => hullPt(x, a)), 0.08, '#8a5a34', {seg: 5}); } anc('rib', [-L / 2 + 5 * step, hullPt(-L / 2 + 5 * step, 1.2)[1], hullPt(-L / 2 + 5 * step, 1.2)[2]]); }
  // papan lambung
  if (b > 2) { const f = Math.min(1, b - 2); for (let j = 0; j < nP; j++) { if ((j + 1) / nP > f + 0.12) break; for (let i = 0; i < ns - 1; i++) { const x0 = -L / 2 + i * step, x1 = x0 + step; for (const s of [-1, 1]) { const p0 = hullPt(x0, s * (-1.35 + (j) * 2.7 / nP) * (s > 0 ? 1 : 1)), p1 = hullPt(x1, s * (-1.35 + j * 2.7 / nP)); if (s > 0) continue; const q0 = hullPt(x0, -1.35 + (j + 0.5) * 2.7 / nP), q1 = hullPt(x1, -1.35 + (j + 0.5) * 2.7 / nP); link(q0, q1, 0.3, j % 2 ? WOODL : '#c8955a', {seg: 5}); const r0 = hullPt(x0, 1.35 - (j + 0.5) * 2.7 / nP), r1 = hullPt(x1, 1.35 - (j + 0.5) * 2.7 / nP); link(r0, r1, 0.3, j % 2 ? WOODL : '#c8955a', {seg: 5}); } } } anc('plank', [0, hullPt(0, 1.0)[1] + 0.15, hullPt(0, 1.0)[2] + 0.1]); }
  // pasak kayu
  if (b > 3) { for (let i = 1; i < ns - 1; i += 2) for (let j = 0; j < nP; j += 2) { const p = hullPt(-L / 2 + i * step, 1.35 - (j + 0.5) * 2.7 / nP); sph(p[0], p[1], p[2] + 0.16, 0.06, '#3b2414', {seg: 6, ns: 1}); } anc('pasak', hullPt(0.5, 0.7).map((v, k) => k === 2 ? v + 0.2 : v)); }
  // dek
  if (b > 2.3) { const yd = 2.15; box(0, yd, 0, L * 0.82, 0.12, B * 1.5, '#b88650'); box(-L * 0.28, yd + 0.55, 0, 3.4, 1.0, 1.9, '#9a6a3d'); }
  // tiang
  const mf = [3.2, -3.4], mh = 9.2;
  if (b > 4) { const f = Math.min(1, b - 4); mf.forEach((x, k) => { cyl(x, 2.1 + mh * f / 2, 0, 0.16, mh * f, '#6b3f24', {seg: 8}); if (f > 0.9) { box(x + 0.2, 2.1 + mh * 0.5, 0, 0.1, 0.1, 0.1, '#6b3f24'); } }); anc('mast', [mf[0], 5.0, 0.2]); }
  // layar
  const sf = o.sail != null ? o.sail : (b > 5 ? Math.min(1, b - 5) : 0);
  if (sf > 0) {
    const tri = (p, w, h, col, dir) => { const n = 9; for (let k = 0; k < n; k++) { const u0 = k / n, ww = w * (1 - u0 * 0.92); box(p[0] + dir * (u0 * w * 0.0) + (ww / 2) * dir, p[1] + u0 * h * sf, p[2] + Math.sin(TT * 1.6 + k * 0.5) * 0.06 * u0, ww, h / n * 1.04 * sf, 0.05, col, {ns: 0}); } };
    const sail = '#f4efe4', sail2 = '#e9dfc9';
    tri([mf[0] - 0.2, 3.0, 0.15], 3.8, 5.8, sail, -1); tri([mf[0] - 0.2, 8.4, 0.15], 2.4, 2.8, sail2, -1);
    tri([mf[1] - 0.2, 3.0, 0.15], 3.8, 5.8, sail, -1); tri([mf[1] - 0.2, 8.4, 0.15], 2.4, 2.8, sail2, -1);
    for (let k = 0; k < 3; k++) { const x0 = L / 2 + 1.2 - k * 0.15; link([x0, 4.0 - k * 0.1, 0], [mf[0] + 0.1, 8.2 - k * 1.3, 0], 0.03, '#d9d2c0', {seg: 4, ns: 1}); const bx = L / 2 + 0.9 - k * 1.5; for (let q = 0; q < 8; q++) { const u = q / 8; box(bx - u * 2.0 + 0.9 - k * 0.1, 3.0 + k * 1.4 + u * (3.2 - k * 0.6) * sf - 0.2, 0.05, (1 - u * 0.8) * 2.0, 0.42 * sf, 0.04, k === 1 ? sail2 : sail, {ns: 1}); } }
    anc('sail', [mf[0] - 1.6, 5.8, 0.25]);
  }
  popM();
});

// ===== KERETA CEPAT WHOOSH (CR400AF) =====
reg('whoosh', 'kereta cepat CR400AF 8 gerbong (4 bermotor, 4 tanpa motor), hidung ramping, pantograf. Sumbu x, depan +x, alas rel di y=0. param: n(8), speed (lunak, geser tekstur roda), ex(tampak terurai bogie 0-1 atau [t0,t1]). jangkar: nose, pantograf, motor, trailer, bogie, window', (o) => {
  const n = o.n || 8, cl = 7.5, gap = 0.18, ex = tIn(o.ex), W = 1.9, Hc = 1.9, y0 = 0.55; const total = n * (cl + gap);
  for (let i = 0; i < n; i++) {
    const cx = -total / 2 + (i + 0.5) * (cl + gap) - 1.0, motor = (i === 1 || i === 2 || i === 5 || i === 6);
    box(cx, y0 + Hc / 2, 0, cl, Hc, W, '#f3f4f2'); box(cx, y0 + 0.28, 0, cl + 0.02, 0.34, W + 0.02, '#c9302c'); // body + strip merah
    box(cx, y0 + Hc * 0.62, 0, cl - 0.8, 0.5, W + 0.03, '#23303a', {glass: false}); // jendela gelap
    box(cx, y0 + Hc + 0.04, 0, cl - 0.4, 0.1, W * 0.7, '#e1e4e2');
    box(cx + cl / 2 + gap / 2, y0 + Hc * 0.55, 0, gap, Hc * 0.8, W * 0.82, '#2b2f33');
    for (const bx of [-cl * 0.3, cl * 0.3]) { const o2 = ex * 1.5; for (const s of [-1, 1]) { cyl(cx + bx, 0.38 - o2 * 0, s * (0.78 + o2), 0.38, 0.12, '#2b2f33', {rx: Math.PI / 2, seg: 14}); } box(cx + bx, 0.52 - o2 * 0.2, 0, 1.9, 0.22, 1.5 + o2 * 1.2, motor ? '#d98a3b' : '#59626b'); }
    if (motor) { box(cx, 0.45 - ex * 0.55, 0, 3.2, 0.5, 1.4, '#d98a3b'); if (i === 1) anc('motor', [cx, 0.45 - ex * 0.55, W / 2 + 0.2]); } else if (i === 3) anc('trailer', [cx, y0 + Hc * 0.7, W / 2 + 0.2]);
    if (i === 3) anc('window', [cx + 1.5, y0 + Hc * 0.62, W / 2 + 0.05]);
    if (i === 1) anc('bogie', [cx + cl * 0.3, 0.4, W / 2 + 0.3]);
    if (i === 2 || i === 5) { const px = cx; box(px, y0 + Hc + 0.28, 0, 1.4, 0.12, 0.9, '#2b2f33'); link([px - 0.6, y0 + Hc + 0.3, 0], [px - 0.1, y0 + Hc + 1.35, 0], 0.05, '#2b2f33', {seg: 5}); link([px - 0.1, y0 + Hc + 1.35, 0], [px + 0.5, y0 + Hc + 0.3, 0], 0.05, '#2b2f33', {seg: 5}); box(px - 0.1, y0 + Hc + 1.42, 0, 0.9, 0.05, 0.12, '#e8edf0'); if (i === 2) anc('pantograf', [px - 0.1, y0 + Hc + 1.4, 0]); }
  }
  // hidung ramping (depan +x) dan ekor (-x)
  for (const sgn of [1, -1]) { const x0 = sgn * (total / 2 - 1.0 + 0.0) - (sgn > 0 ? 0.12 : 0.0); for (let k = 0; k < 9; k++) { const u = k / 8, len = 0.95, h = Hc * (1 - 0.55 * u * u) + 0.0, w = W * (1 - 0.75 * u * u), yy = y0 + (Hc * (1 - 0.55 * u * u)) / 2 - 0.2 * u * u * 0.5; box(x0 + sgn * (u * 5.4 + 0.3), y0 + h / 2 - 0.05 * u, 0, 0.75, h, w, k > 5 ? '#d9dcda' : '#f3f4f2'); if (k < 6) box(x0 + sgn * (u * 5.4 + 0.3), y0 + 0.28 - 0.1 * u, 0, 0.76, 0.3 * (1 - u), w + 0.02, '#c9302c'); } box(x0 + sgn * 3.9, y0 + Hc * 0.72, 0, 1.6, 0.5, W * 0.62, '#23303a'); }
  anc('nose', [total / 2 + 4.3, y0 + 0.9, 0]);
  // sirkuit bogie: roda berputar
  const g = TT * (o.speed == null ? 6 : o.speed);
  for (let i = 0; i < n; i++) { const cx = -total / 2 + (i + 0.5) * (cl + gap) - 1.0; for (const bx of [-cl * 0.3, cl * 0.3]) for (const s of [-1, 1]) box(cx + bx, 0.38, s * 0.78, 0.5, 0.08, 0.14, '#ff9a2e', {rz: g, ns: 1}); }
});

reg('viaduk', 'jalur layang kereta cepat: dek beton di atas pilar, rel, tiang listrik (katenari) dan kabel. Sumbu x. param: len(60), h(9). jangkar: deck, pier, catenary', (o) => {
  const Ln = o.len || 60, h = o.h || 9;
  box(0, h - 0.6, 0, Ln, 1.2, 6.2, '#b9b6ae'); box(0, h + 0.05, 0, Ln, 0.3, 6.4, '#cfccc4');
  for (const s of [-1, 1]) box(0, h + 0.55, s * 3.15, Ln, 0.8, 0.2, '#a9a69e');
  for (let x = -Ln / 2 + 4; x < Ln / 2; x += 12) { box(x, h / 2 - 0.6, 0, 1.8, h - 1.2, 3.0, '#a8a59d'); box(x, 0.3, 0, 4.2, 0.6, 5.2, '#8d8a82'); }
  for (const s of [-0.75, 0.75]) box(0, h + 0.28, s, Ln, 0.12, 0.1, '#7b838e');
  for (let x = -Ln / 2 + 6; x < Ln / 2; x += 9) { cyl(x, h + 3.3, 2.6, 0.12, 6.6, '#8c8f94', {seg: 6}); box(x, h + 6.3, 1.2, 0.12, 0.12, 2.9, '#8c8f94'); }
  box(0, h + 4.4, 0, Ln, 0.03, 0.03, '#2b2f33', {ns: 1});
  anc('deck', [Ln * 0.25, h, 3.1]); anc('pier', [-Ln / 2 + 16, h * 0.5, 1.5]); anc('catenary', [-Ln / 2 + 15, h + 4.4, 0]);
});

reg('rel_dua_jenis', 'perbandingan rel: kiri rel di atas balas kerikil, kanan rel di atas pelat beton tanpa kerikil. Sumbu x. jangkar: balas, pelat, rel, bantalan', (o) => {
  for (const s of [-1, 1]) {
    const z = s * 3.2;
    if (s < 0) { box(0, 0.3, z, 24, 0.6, 4.6, '#8d8a84'); for (let i = 0; i < 30; i++) box(-11.5 + i * 0.8, 0.72, z, 0.3, 0.22, 2.7, '#7d7a74'); anc('bantalan', [-3, 0.8, z + 1.6]); anc('balas', [6, 0.3, z + 2.3]); }
    else { box(0, 0.3, z, 24, 0.6, 4.6, '#b9b6ae'); box(0, 0.72, z, 24, 0.22, 3.6, '#cfccc4'); for (let i = 0; i < 24; i++) box(-11.5 + i, 0.88, z, 0.16, 0.12, 3.0, '#a9a69e'); anc('pelat', [6, 0.75, z + 1.9]); }
    for (const q of [-0.72, 0.72]) box(0, 1.0, z + q, 24, 0.26, 0.14, '#6b6f75');
    if (s > 0) anc('rel', [-6, 1.1, z + 0.72]);
  }
});

reg('sinyal_ka', 'sistem sinyal kereta cepat: balise di antara rel, sirkuit rel (blok warna), antena kereta, menara RBC. Sumbu x. jangkar: balise, rbc, blok, kereta', (o) => {
  box(0, 0.3, 0, 40, 0.6, 4, '#8d8a84'); for (const q of [-0.72, 0.72]) box(0, 0.75, q, 40, 0.22, 0.14, '#6b6f75');
  for (let i = 0; i < 4; i++) { box(-15 + i * 10, 0.62, 0, 0.9, 0.2, 0.7, '#f2c21c'); } anc('balise', [-5, 0.72, 0]);
  for (let i = 0; i < 4; i++) box(-15 + i * 10 + 5, 0.9, 1.6, 9.2, 0.14, 0.14, i === 2 ? '#d94b3d' : '#3aa655'); anc('blok', [5, 0.9, 1.6]);
  cyl(-8, 5, -5, 0.5, 10, '#aab0b6', {seg: 8}); box(-8, 10.3, -5, 2.4, 0.8, 0.8, '#d94b3d'); for (let k = 0; k < 3; k++) { const f = fr(TT * 0.8 + k / 3); sph(-8 + (-8 - -8) + f * 16, 10.3 - f * 8.8, -5 + f * 5, 0.2, '#6fc3ff', {e: 1, ns: 1}); }
  anc('rbc', [-8, 10.3, -5]);
  const x = -20 + fr(TT * 0.15) * 40; box(x, 1.7, 0, 9, 1.8, 1.9, '#f3f4f2'); box(x, 1.2, 0, 9.02, 0.3, 1.92, '#c9302c'); box(x, 0.9, 0, 1.0, 0.2, 0.6, '#6fc3ff', {e: 1}); anc('kereta', [x, 2.5, 1]);
});

reg('rute_hsr', 'peta rute Jakarta-Bandung: garis rute dengan 4 stasiun dan titik kereta bergerak. Bidang xz. jangkar: halim, karawang, padalarang, tegalluar, kereta', (o) => {
  box(0, -0.1, 0, 50, 0.2, 18, '#dfe9d2'); const pts = [[-20, 0.2, 5], [-8, 0.2, 2.5], [6, 0.2, -1], [20, 0.2, -4.5]];
  path(pts, 0.18, '#3f7fd0', {seg: 6}); const nm = ['halim', 'karawang', 'padalarang', 'tegalluar']; pts.forEach((p, i) => { cyl(p[0], 0.5, p[2], 0.9, 0.6, '#ffffff', {seg: 14}); cyl(p[0], 0.82, p[2], 0.6, 0.12, i % 2 ? '#d94b3d' : '#f2c21c', {seg: 14}); anc(nm[i], [p[0], 1.0, p[2]]); });
  const k = fr(TT * 0.12); sph(...along(pts, k).map((v, i) => i === 1 ? 0.9 : v), 0.5, '#d94b3d', {e: 0.3}); anc('kereta', along(pts, k).map((v, i) => i === 1 ? 1.6 : v));
});

// ===== LINGKUNGAN: bukit jauh, pohon cincin, burung, sawah =====
function palm(x, z, h, seed) { // pohon kelapa: batang melengkung + pelepah berayun
  const R = rng(seed || 1), lean = (R() - 0.5) * 0.5; let px = x, py = 0, pz = z;
  const n = 6; for (let i = 0; i < n; i++) { const nx = px + lean * h / n * 0.6, ny = py + h / n, nz = pz; link([px, py, pz], [nx, ny, nz], 0.28 - i * 0.025, i % 2 ? '#8a6a45' : '#7d5f3d', {seg: 6, ns: i < 3 ? 0 : 1}); px = nx; py = ny; pz = nz; }
  for (let k = 0; k < 8; k++) { const a = k / 8 * 6.283 + R(), sw = Math.sin(TT * 1.3 + k + seed) * 0.12, L = h * 0.42; const m = [px + Math.cos(a) * L * 0.55, py + L * 0.18 - 0.1 + sw * L * 0.3, pz + Math.sin(a) * L * 0.55], e = [px + Math.cos(a) * L, py - L * 0.2 + sw * L * 0.4, pz + Math.sin(a) * L]; link([px, py, pz], m, 0.07, '#3f7a35', {seg: 4, ns: 1}); link(m, e, 0.05, '#4f9140', {seg: 4, ns: 1}); }
}
function broadTree(x, z, h, col) { cyl(x, h * 0.2, z, h * 0.05 + 0.1, h * 0.4, '#6b4c33', {seg: 6, ns: 1}); sph(x, h * 0.62, z, h * 0.32, col || '#3f8a45', {seg: 8, ns: 1}); sph(x + h * 0.18, h * 0.5, z + h * 0.08, h * 0.24, '#4c9a4c', {seg: 7, ns: 1}); }
function farRing(seed, rmin, rmax, n, o = {}) {
  const R = rng(seed); for (let i = 0; i < n; i++) { const a = R() * 6.283, r = rmin + R() * (rmax - rmin), x = Math.cos(a) * r, z = Math.sin(a) * r; if (o.palm && R() < o.palm) palm(x, z, 9 + R() * 5, i + seed); else broadTree(x, z, 6 + R() * 6, ['#3f8a45', '#4c9a4c', '#35783c'][i % 3]); }
}
function hillRing(seed, r, cols, o = {}) { const R = rng(seed); for (let i = 0; i < (o.n || 16); i++) { const a = i / (o.n || 16) * 6.283 + R() * 0.2, rr = r * (0.9 + R() * 0.3), w = 130 + R() * 90, h = (o.h || 40) * (0.35 + 0.5 * R()); cyl(Math.cos(a) * rr, h / 2 - 2, Math.sin(a) * rr, w * 0.5, h, cols[i % cols.length], {rt: 0.38, rb: 1, seg: 10, ns: 1}); } }
function birds(n, seed, o = {}) { const R = rng(seed || 4); for (let i = 0; i < n; i++) { const sp = 6 + R() * 5, ph = R() * 200, x = ((TT * sp + ph * 7) % 240) - 120, z = -60 + R() * 120, y = (o.y || 22) + R() * 14 + Math.sin(TT * 0.6 + i) * 1.5, w = Math.sin(TT * 9 + i) * 0.6; for (const s of [-1, 1]) { pushM(T(x, y, z)); pushM(RX(s * w)); box(0, 0, s * 0.6, 0.35, 0.05, 1.2, '#2c2f33', {ns: 1}); popM(); popM(); } box(x, y, z, 0.5, 0.12, 0.14, '#2c2f33', {ns: 1}); } }
function paddy(seed, x0, x1, z0, z1, step, o = {}) { const R = rng(seed); for (let x = x0; x < x1; x += step) for (let z = z0; z < z1; z += step) { if (o.hole && x + step > o.hole[0] && x < o.hole[1] && z + step > o.hole[2] && z < o.hole[3]) continue; const c = ['#86b255', '#7aa64d', '#93ba5a', '#6f9c49', '#a4c065'][Math.floor(R() * 5)]; box(x + step / 2, 0.015, z + step / 2, step * 0.94, 0.03, step * 0.94, c, {ns: 1}); } }
function volcano(x, z, h, w) { cyl(x, h / 2 - 2, z, w * 0.5, h, '#6f7f93', {rt: 0.06, rb: 1, seg: 14, ns: 1}); cyl(x, h * 0.62, z, w * 0.2, h * 0.5, '#8795a6', {rt: 0.05, rb: 1, seg: 10, ns: 1}); for (let k = 0; k < 6; k++) { const f = fr(TT * 0.05 + k / 6); sph(x + f * 14, h + f * 22, z + 2, 5 + f * 9, '#e6ebf0', {seg: 8, ns: 1, glass: true}); } }
