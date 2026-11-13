// ---------- Pustaka NUSANTARA v2: detail tinggi, berdasarkan riset bentuk asli ----------
// Rumah Gadang (rumah gonjong, anjuang, singkok, rangkiang), Borobudur (ukuran asli 123 m x 35 m, 72 stupa),
// Pinisi (dua tiang, tujuh layar: 3 layar depan di bowsprit, 2 layar gaff, 2 topsail), Whoosh CR400AF (8 gerbong 4M4T), terowongan.
const lerpv = (a, b, u) => a + (b - a) * u;
const IJUK = ['#2a2420', '#352d27', '#2f2722'];

// strip vertikal untuk kain layar / bidang: polygon konveks di bidang x-y pada kedalaman z
function polyStrips(pts, n, z, col, o = {}) {
  let x0 = 1e9, x1 = -1e9; pts.forEach(p => { x0 = Math.min(x0, p[0]); x1 = Math.max(x1, p[0]); });
  const dx = (x1 - x0) / n;
  for (let i = 0; i < n; i++) {
    const xc = x0 + (i + 0.5) * dx; let lo = 1e9, hi = -1e9;
    for (let k = 0; k < pts.length; k++) { const a = pts[k], b = pts[(k + 1) % pts.length]; if ((a[0] <= xc && b[0] >= xc) || (b[0] <= xc && a[0] >= xc)) { const t = a[0] === b[0] ? 0 : (xc - a[0]) / (b[0] - a[0]); const y = a[1] + (b[1] - a[1]) * t; lo = Math.min(lo, y); hi = Math.max(hi, y); } }
    if (hi - lo < 0.02) continue;
    const f = (i + 0.5) / n, bz = (o.belly || 0) * Math.sin(Math.PI * f) * (0.7 + 0.3 * Math.sin(TT * 1.4 + (o.ph || 0))) + (o.flut || 0) * Math.sin(TT * 5 + i * 0.7) * f;
    box(xc, (lo + hi) / 2, z + bz, dx * 1.04, hi - lo, o.th || 0.05, o.alt && i % 2 ? o.alt : col, {ns: o.ns == null ? 1 : o.ns, e: o.e == null ? 0.28 : o.e});
  }
}

// atap pelana bergonjong (Minangkabau): punggung melengkung ke atas di kedua ujung, bilah ijuk, tanduk di ujung
function gonjongRoof(L, Wd, y0, o = {}) {
  const N = o.n || 20, ridge = o.ridge || 1.5, lift = o.lift || 2.4, th = 0.34;
  for (let i = 0; i < N; i++) {
    const u = -1 + 2 * (i + 0.5) / N, xm = u * L / 2, dxs = L / N * 1.06, rd = ridge + lift * Math.pow(Math.abs(u), 2.3), wid = Wd * (1 - 0.14 * Math.abs(u));
    const rise = rd, half = wid / 2, ang = Math.atan2(rise, half), sl = Math.hypot(rise, half);
    for (const s of [-1, 1]) { pushM(T(xm, y0 + rise / 2, s * half / 2)); pushM(RX(s * ang)); box(0, 0, 0, dxs, th, sl * 1.04, IJUK[i % 3]); popM(); popM(); }
    box(xm, y0 + rd + 0.08, 0, dxs, 0.16, 0.5, '#4a3d33'); // bubungan
    if (i % 4 === 0) for (const s of [-1, 1]) box(xm, y0 + 0.02, s * (half - 0.1), dxs * 0.3, 0.14, 0.2, '#14100e'); // tepi atap
  }
  // gonjong: tanduk melengkung di kedua ujung
  for (const sx of [-1, 1]) {
    const bx = sx * L / 2, by = y0 + ridge + lift, hh = o.horn || 3.2, hl = o.hornL || 1.9;
    for (let k = -2; k <= 2; k++) { const zz = k * Wd * 0.085, taper = 1 - Math.abs(k) * 0.12; const pts = []; for (let j = 0; j <= 6; j++) { const t = j / 6; pts.push([bx + sx * (hl * Math.pow(t, 1.25)), by - 0.2 + hh * Math.pow(t, 1.7) * taper, zz * (1 - t * 0.55)]); } for (let j = 0; j < 6; j++) link(pts[j], pts[j + 1], 0.2 * (1 - j / 8) * (1 - Math.abs(k) * 0.1), IJUK[(j + k + 4) % 3], {seg: 5}); }
    for (let j = 0; j < 6; j++) { const t = (j + 0.5) / 6; box(bx + sx * hl * Math.pow(t, 1.25) * 0.98, by - 0.15 + hh * Math.pow(t, 1.7) * 0.92, 0, 0.2, 0.18, Wd * 0.17 * (1 - t * 0.6), IJUK[j % 3]); }
    // singkok: dinding segitiga di bawah ujung atap
    const gh = ridge + lift - 0.25;
    for (let k = 0; k < 9; k++) { const f = k / 9; box(bx - sx * 0.12, y0 + 0.1 + (k + 0.5) * gh / 9, 0, 0.14, gh / 9 * 1.02, Wd * 0.92 * (1 - f * 0.98) , ['#8c2a22', '#d9a441', '#2f6f4a', '#8c2a22'][k % 4]); }
  }
}

function ukiran(x, y, z, w, h, side, seed) { // panel ukiran berwarna pada dinding (sisi z=side)
  const zz = z + side * 0.07;
  box(x, y, zz, w, h, 0.06, '#6b2a1c'); box(x, y, zz + side * 0.04, w * 0.84, h * 0.84, 0.04, '#7f3320');
  pushM(T(x, y, zz + side * 0.07)); pushM(RZ(Math.PI / 4)); box(0, 0, 0, Math.min(w, h) * 0.42, Math.min(w, h) * 0.42, 0.04, '#e0aa44'); popM(); popM();
  box(x, y + h * 0.33, zz + side * 0.07, w * 0.7, 0.07, 0.03, '#2f6f4a'); box(x, y - h * 0.33, zz + side * 0.07, w * 0.7, 0.07, 0.03, '#2f6f4a');
  for (const q of [-1, 1]) sph(x + q * w * 0.3, y, zz + side * 0.08, 0.07, '#e0aa44', {seg: 6, ns: 1});
}

reg('rumah_gadang', 'Rumah Gadang Minangkabau bergonjong empat: rumah panggung berkolong, tiang di atas batu sandi (tidak ditanam), balok & pasak, dinding berukir, tangga, dua anjuang, atap ijuk bergonjong + singkok, rangkiang. Sumbu x. param: ex (tampak terurai 0-1 atau [t0,t1]), shake (gempa 0-1), amp, people(true). jangkar: batu, tiang, pasak, atap, kolong, lantai, tiangmiring, gonjong, ukiran', (o) => {
  const ex = tIn(o.ex), sk = tIn(o.shake), L = 15, Wd = 6.4, H = 2.4, fy = H + 0.35;
  const dx = sk * Math.sin(TT * 13) * (o.amp || 0.3) * (0.65 + 0.35 * Math.sin(TT * 5.1));
  const cols = 6, rows = 4, xs = Array.from({length: cols}, (_, i) => -L / 2 + 0.9 + i * (L - 1.8) / (cols - 1)), zs = Array.from({length: rows}, (_, i) => -Wd / 2 + 0.45 + i * (Wd - 0.9) / (rows - 1));
  // tanah halaman + jalan setapak
  box(0, 0.02, 7.2, 26, 0.04, 3.2, '#b6a27c', {ns: 1});
  // batu sandi (datar, lebar) dan debu saat gempa
  for (const x of xs) for (const z of zs) { cyl(x, 0.11, z, 0.62, 0.22, '#9f9c93', {seg: 12}); cyl(x, 0.24, z, 0.52, 0.06, '#b4b1a7', {seg: 12}); if (sk > 0.15) { const f = fr(TT * 1.3 + x * 0.37 + z); sph(x + 0.5, 0.35 + f * 0.8, z + 0.5, 0.12 + f * 0.25, '#cdbf9c', {seg: 6, ns: 1}); } }
  anc('batu', [xs[1], 0.25, zs[3]]);
  pushM(T(dx, 0, 0));
  // tiang: tepi luar miring ke dalam (seperti badan kapal)
  for (let ci = 0; ci < cols; ci++) for (let r = 0; r < rows; r++) {
    const x = xs[ci], z = zs[r], tilt = r === 0 ? -0.09 : r === rows - 1 ? 0.09 : 0, wob = sk * 0.05 * Math.sin(TT * 13 + ci);
    pushM(T(x, 0.27, z)); pushM(RX(tilt + wob)); cyl(0, H / 2 + 0.05, 0, 0.2, H + 0.1, WOOD[(((r + ci) % 3) + 3) % 3], {seg: 8}); popM(); popM();
  }
  anc('tiang', [xs[3], H * 0.55, zs[1]]); anc('tiangmiring', [xs[2], H * 0.5, zs[0] - 0.1]); anc('kolong', [0, 1.1, zs[3] + 0.3]);
  // rangka lantai: balok melintang (pasak oranye menembus tiang)
  pushM(T(0, ex * 1.3, 0));
  for (const z of zs) box(0, fy - 0.2, z, L + 0.4, 0.26, 0.24, '#5f3a22');
  for (const x of xs) box(x, fy - 0.45, 0, 0.24, 0.26, Wd + 0.3, '#6b4228');
  for (const x of xs) for (const z of zs) box(x, fy - 0.2, z, 0.12, 0.3, 0.12, '#f0a53a');
  anc('pasak', [xs[2], fy - 0.2, zs[3] + 0.12]);
  for (let i = 0; i < 13; i++) box(-L / 2 + 0.5 + i * (L - 1) / 12, fy + 0.02, 0, (L - 1) / 12 * 0.96, 0.12, Wd + 0.2, i % 2 ? '#b8864b' : '#a97a42'); // papan lantai
  anc('lantai', [-L / 2 + 1, fy + 0.1, Wd / 2 + 0.2]);
  // tangga depan
  for (let k = 0; k < 5; k++) box(0.2, fy - 0.35 - k * 0.5 + 0.0 + 0.5, Wd / 2 + 0.6 + (4 - k) * 0.28 + 0.1, 1.9, 0.14, 0.34, '#9a6a3d'), 0;
  for (const s of [-1, 1]) link([s * 1.0 + 0.2, fy + 0.8, Wd / 2 + 0.3], [s * 1.0 + 0.2, 0.7, Wd / 2 + 1.9], 0.05, '#5f3a22', {seg: 5});
  popM();
  // anjuang di kedua ujung (lantai lebih tinggi) + atap gonjong kecil
  pushM(T(0, ex * 1.8, 0));
  for (const sx of [-1, 1]) { const ax = sx * (L / 2 + 1.6); for (const z of [-Wd * 0.3, Wd * 0.3]) for (const q of [-0.9, 0.9]) cyl(ax + q, 1.4, z, 0.18, 2.4, WOOD[1], {seg: 7}); box(ax, fy + 0.28, 0, 3.4, 0.16, Wd * 0.72, '#b8864b'); }
  popM();
  // dinding berukir
  pushM(T(0, ex * 2.8, 0));
  const wh = 2.7, wy = fy + 0.06 + wh / 2;
  for (const s of [-1, 1]) { box(0, wy, s * (Wd / 2 - 0.05), L, wh, 0.14, '#5b2f1b'); for (let i = 0; i < 12; i++) { const x = -L / 2 + 0.7 + i * (L - 1.4) / 11; if (i % 3 === 1) { box(x, wy + 0.1, s * (Wd / 2 + 0.03), 0.9, 1.1, 0.06, '#1a1512'); box(x, wy + 0.1, s * (Wd / 2 + 0.07), 0.04, 1.1, 0.04, '#7a4a2b'); } else ukiran(x, wy, s * (Wd / 2), 1.0, 2.2, s, i); } }
  anc('ukiran', [xs[1], wy, Wd / 2 + 0.15]);
  for (const sx of [-1, 1]) { box(sx * (L / 2 - 0.05), wy, 0, 0.14, wh, Wd, '#5b2f1b'); for (let k = 0; k < 4; k++) ukiran(sx * (L / 2 + 0.03), wy, -Wd / 2 + 0.9 + k * (Wd - 1.8) / 3, 1.2, 2.2, sx, k); }
  // dinding anjuang
  for (const sx of [-1, 1]) { const ax = sx * (L / 2 + 1.6); box(ax, fy + 0.28 + 0.9, Wd * 0.36 - 0.05, 3.4, 1.7, 0.1, '#5b2f1b'); box(ax, fy + 0.28 + 0.9, -(Wd * 0.36 - 0.05), 3.4, 1.7, 0.1, '#5b2f1b'); box(ax + sx * 1.7, fy + 0.28 + 0.9, 0, 0.1, 1.7, Wd * 0.72, '#5b2f1b'); }
  popM();
  // atap utama
  pushM(T(0, ex * 5.4, 0));
  const y0 = fy + 0.06 + wh;
  gonjongRoof(L + 0.8, Wd + 1.4, y0, {ridge: 1.9, lift: 2.6, horn: 3.6, hornL: 2.0, n: 22});
  anc('atap', [0, y0 + 2.0, Wd * 0.35]); anc('gonjong', [L / 2 + 1.6, y0 + 1.9 + 2.6 + 3.2, 0]);
  popM();
  pushM(T(0, ex * 3.6, 0));
  for (const sx of [-1, 1]) { pushM(T(sx * (L / 2 + 1.6), fy + 0.28 + 1.75, 0)); gonjongRoof(3.8, Wd * 0.82, 0, {ridge: 1.0, lift: 1.4, horn: 1.9, hornL: 1.2, n: 8}); popM(); }
  popM();
  popM();
  // rangkiang (lumbung padi) di halaman
  pushM(T(-L * 0.62, 0, 8.2));
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) cyl(sx * 0.9, 0.7, sz * 0.7, 0.14, 1.4, WOOD[0], {seg: 6});
  box(0, 2.0, 0, 2.3, 1.4, 1.9, '#7a4a2b'); for (let k = 0; k < 4; k++) box(-0.84 + k * 0.56, 2.0, 0.96, 0.4, 1.0, 0.04, k % 2 ? '#e0aa44' : '#8c2a22');
  gonjongRoof(3.4, 3.0, 2.7, {ridge: 0.8, lift: 1.1, horn: 1.5, hornL: 0.9, n: 8});
  popM();
  // orang berjalan di halaman
  if (o.people !== false) for (let k = 0; k < 2; k++) { const x = -9 + ((TT * 0.9 + k * 11) % 22); pushM(T(x, 0, 6.2 + k * 0.9)); pushM(RY(Math.PI / 2)); pushM(S(0.62, 0.62, 0.62)); COMP.person({col: k ? '#b3392e' : '#2f66c9'}, 'gp' + k); popM(); popM(); popM(); }
});

// ===== BOROBUDUR (ukuran riset: alas 123 m, tinggi ±35 m, 6 teras persegi, 3 teras bundar, 72 stupa) =====
reg('borobudur', 'Candi Borobudur ukuran asli (alas 123 m, tinggi 35 m): kaki, lima teras persegi dengan dinding relief + pagar relung arca Buddha, tangga empat sisi, tiga teras bundar dengan 72 stupa berlubang (32/24/16), stupa induk, 100 pancuran makara. param: rain, flow. jangkar: spout, tier, stupa, base, relief, niche', (o) => {
  box(0, 0.75, 0, 123, 1.5, 123, '#6f695f'); box(0, 3.5, 0, 113, 4, 113, '#7d776c'); box(0, 5.6, 0, 115, 0.3, 115, '#948b7d');
  for (let k = 0; k < 11; k++) for (const s of [-1, 1]) { box(-52 + k * 10.4, 3.5, s * 56.55, 7.5, 3.0, 0.14, '#7d776c'); box(s * 56.55, 3.5, -52 + k * 10.4, 0.14, 3.0, 7.5, '#7d776c'); }
  anc('base', [56.8, 3.5, 20]);
  const W = [99, 91, 83, 75, 67]; let y = 5.75; const spouts = [];
  W.forEach((w, i) => {
    box(0, y + 0.1, 0, w + 1, 0.3, w + 1, '#a29a8b'); // lantai teras
    const wallW = w - 8, h = 3.4;
    box(0, y + h / 2, 0, wallW, h, wallW, i % 2 ? '#8a8174' : '#7f786c'); // dinding utama
    box(0, y + h + 0.1, 0, wallW + 0.8, 0.2, wallW + 0.8, '#bdb4a4');
    const bh = 1.5, bo = w / 2 - 0.55; // pagar luar (balustrade)
    for (const s of [-1, 1]) { box(0, y + bh / 2 + 0.25, s * bo, w - 0.4, bh, 1.0, '#887f72'); box(s * bo, y + bh / 2 + 0.25, 0, 1.0, bh, w - 0.4, '#9a9183'); box(0, y + bh + 0.35, s * bo, w, 0.25, 1.25, '#b8afa0'); box(s * bo, y + bh + 0.35, 0, 1.25, 0.25, w, '#b8afa0'); }
    // relief pada dinding utama (menghadap koridor)
    const np = Math.floor(wallW / 4.5);
    for (let k = 0; k < np; k++) { const t = -wallW / 2 + 2.25 + k * 4.5; for (const s of [-1, 1]) { box(t, y + h * 0.5, s * (wallW / 2 + 0.06), 3.6, 2.4, 0.1, k % 2 ? '#7f776b' : '#847c70'); box(t, y + h * 0.5, s * (wallW / 2 + 0.11), 3.0, 1.9, 0.05, '#a49b8c'); box(s * (wallW / 2 + 0.06), y + h * 0.5, t, 0.1, 2.4, 3.6, k % 2 ? '#7f776b' : '#847c70'); box(s * (wallW / 2 + 0.11), y + h * 0.5, t, 0.05, 1.9, 3.0, '#a49b8c'); } }
    if (i === 2) anc('relief', [wallW / 2 + 0.2, y + h * 0.5, 6]);
    // relung berisi arca Buddha di pagar luar
    const nn = Math.max(5, Math.floor(w / 9));
    for (let k = 0; k < nn; k++) { const t = -w / 2 + 6 + k * (w - 12) / Math.max(1, nn - 1); for (const s of [-1, 1]) { box(t, y + 1.3, s * (bo - 0.55), 1.5, 1.2, 0.1, '#4a4540'); box(t, y + 1.1, s * (bo - 0.62), 0.6, 0.7, 0.2, '#b9b19f'); sph(t, y + 1.7, s * (bo - 0.62), 0.22, '#c6bda9', {seg: 8, ns: 1}); box(s * (bo - 0.55), y + 1.3, t, 0.1, 1.2, 1.5, '#4a4540'); box(s * (bo - 0.62), y + 1.1, t, 0.2, 0.7, 0.6, '#b9b19f'); sph(s * (bo - 0.62), y + 1.7, t, 0.22, '#c6bda9', {seg: 8, ns: 1}); } }
    if (i === 3) anc('niche', [w / 2 - 1, y + 1.3, 10]);
    // pancuran makara: 20 per teras (4 sudut + 16 sisi) = 100
    const so = w / 2 + 0.2, yy = y + 0.45;
    for (const sx of [-1, 1]) for (const sz of [-1, 1]) spouts.push([sx * so, yy, sz * so, sx, sz, y]);
    for (const s of [-1, 1]) for (const q of [-0.375, -0.125, 0.125, 0.375]) { spouts.push([q * w, yy, s * so, 0, s, y]); spouts.push([s * so, yy, q * w, s, 0, y]); }
    if (i === 1) anc('tier', [w / 2, y + 1.5, 0]);
    y += 3.8;
  });
  // tangga empat sisi (dari tanah sampai teras atas)
  for (let a = 0; a < 4; a++) { pushM(RY(a * Math.PI / 2)); for (let k = 0; k < 8; k++) box(61.5 - k * 0.9 - 0.3, k * 0.72 + 0.5, 0, 0.9, 0.2, 7, '#a9a091'); for (let j = 0; j < 5; j++) for (let k = 0; k < 6; k++) box(W[j] / 2 + 1.2 - k * 0.65, 5.75 + j * 3.8 + k * 0.62, 0, 0.65, 0.22, 7, '#a9a091'); popM(); }
  // tiga teras bundar + 72 stupa berlubang + stupa induk
  const ring = [[25.6, 32, 20.8, 3.4], [19.0, 24, 14.9, 3.0], [12.7, 16, 9.0, 2.6]];
  let yc = y;
  cyl(0, yc + 0.1, 0, 27.5, 0.4, '#b3aa9b', {seg: 36});
  ring.forEach((r, i) => {
    cyl(0, yc + 0.65, 0, r[0], 1.3, i % 2 ? '#948b7d' : '#9c9385', {seg: 40}); cyl(0, yc + 1.35, 0, r[0] - 0.4, 0.2, '#bdb4a4', {seg: 40});
    for (let k = 0; k < r[1]; k++) { const a = k / r[1] * 6.2832, px = Math.cos(a) * r[2], pz = Math.sin(a) * r[2], by = yc + 1.45;
      cyl(px, by + 0.25, pz, r[3] * 0.34, 0.5, '#a39a8c', {seg: 10});
      cyl(px, by + 1.15, pz, r[3] * 0.42, 1.5, '#aaa194', {seg: 10, rt: 0.8, rb: 1.05});
      for (let q = 0; q < 4; q++) { const aq = q * 1.5708 + a; box(px + Math.cos(aq) * r[3] * 0.4, by + 1.1, pz + Math.sin(aq) * r[3] * 0.4, 0.4, 0.55, 0.4, '#3d3935', {ry: -aq}); }
      sph(px, by + 1.1, pz, 0.28, '#c9c0ac', {seg: 7, ns: 1});
      cyl(px, by + 2.1, pz, r[3] * 0.2, 0.5, '#bdb4a4', {seg: 10, rt: 0.3, rb: 1}); cyl(px, by + 2.55, pz, 0.12, 0.7, '#c4bbab', {seg: 6});
    }
    yc += 1.3;
  });
  cyl(0, yc + 0.25, 0, 5.6, 0.5, '#b7ae9f', {seg: 28}); cyl(0, yc + 2.9, 0, 4.9, 4.8, '#b0a799', {seg: 28, rt: 0.65, rb: 1}); cyl(0, yc + 5.6, 0, 1.8, 0.7, '#bdb4a4', {seg: 16}); cyl(0, yc + 6.5, 0, 0.9, 1.4, '#c4bbab', {seg: 10, rt: 0.3, rb: 1}); cyl(0, yc + 7.4, 0, 0.12, 1.2, '#d2c9b6', {seg: 6});
  anc('stupa', [0, yc + 3.0, 0]);
  // pancuran dan aliran air
  spouts.forEach((p, i) => {
    const dx = p[3], dz = p[4]; box(p[0] + dx * 0.5, p[1], p[2] + dz * 0.5, 0.5 + 0.9 * Math.abs(dx), 0.42, 0.5 + 0.9 * Math.abs(dz), '#2b2723'); box(p[0] + dx * 1.0, p[1] + 0.05, p[2] + dz * 1.0, 0.3 + 0.2 * Math.abs(dx), 0.25, 0.3 + 0.2 * Math.abs(dz), '#1d1a17'); sph(p[0] + dx * 0.95, p[1] + 0.27, p[2] + dz * 0.95, 0.09, '#d8d0bd', {seg: 5, ns: 1});
    if (o.flow) for (let j = 0; j < 2; j++) { const k = fr(TT * 0.8 + i * 0.137 + j * 0.5), run = 1.3 + k * 1.1, fall = 0.2 + k * k * 4.6; sph(p[0] + dx * (1.0 + run * 0.6), p[1] - fall, p[2] + dz * (1.0 + run * 0.6), 0.11, '#8fd0f5', {e: 0.6, ns: 1}); }
    if (i === 5) anc('spout', [p[0] + dx * 1.0, p[1], p[2] + dz * 1.0]);
  });
  if (o.rain) { const R = rng(5); for (let k = 0; k < 220; k++) { const f = fr(TT * 1.6 + R()), x = -75 + R() * 150, z = -75 + R() * 150; box(x, 48 - f * 48, z, 0.08, 1.6, 0.08, '#a7d6f2', {e: 0.5, ns: 1}); } }
});

// ===== BOROBUDUR: penampang sistem drainase =====
reg('boro_drain', 'penampang drainase Borobudur (irisan): inti bukit/tanah isian, lapisan penyaring pasir, lapisan kedap air, lantai beton, batu andesit berpola, pipa, pancuran makara; air hujan mengalir ke pancuran & rembesan ke pipa. param: flow. jangkar: stone, filter, seal, slab, pipe, spout, rain, core', (o) => {
  const W = 13, Dz = 3.2, top = 2.6;
  box(0, 1.3, 0, W, 2.6, Dz, '#7a5a3e'); { const R = rng(3); for (let k = 0; k < 14; k++) box(-W / 2 + 1 + R() * (W - 2), 0.4 + R() * 2, Dz / 2 + 0.01, 0.5 + R() * 0.5, 0.35, 0.04, '#5f4630'); } anc('core', [-W * 0.3, 1.3, Dz / 2]);
  box(0, top + 0.2, 0, W, 0.4, Dz, '#dcc77f'); { const R = rng(4); for (let k = 0; k < 26; k++) sph(-W / 2 + R() * W, top + 0.06 + R() * 0.28, Dz / 2 + 0.01, 0.05, '#c7ae63', {seg: 5, ns: 1}); } anc('filter', [-W * 0.35, top + 0.2, Dz / 2]);
  box(0, top + 0.55, 0, W, 0.26, Dz, '#2f5f8f'); anc('seal', [-W * 0.35, top + 0.55, Dz / 2]);
  box(0, top + 0.9, 0, W, 0.44, Dz, '#9aa0a6'); anc('slab', [-W * 0.35, top + 0.9, Dz / 2]);
  // batu andesit tersusun dengan garis sambungan
  const bw = 1.1, bh2 = 0.7; for (let r = 0; r < 2; r++) for (let c = 0; c < 4; c++) { const x = -W / 2 + 0.6 + c * bw + (r % 2) * bw / 2; box(x, top + 1.5 + r * bh2, 0, bw * 0.97, bh2 * 0.96, Dz, (r + c) % 2 ? '#948b7d' : '#9a9183'); }
  for (let r = 0; r < 2; r++) for (let c = 0; c < 2; c++) box(W / 2 - 0.6 - c * bw, top + 1.5 + r * bh2, 0, bw * 0.97, bh2 * 0.96, Dz, (r + c) % 2 ? '#948b7d' : '#9a9183');
  anc('stone', [-W / 2 + 2.2, top + 1.8, Dz / 2]);
  box(0, top + 1.14, 0, 4.0, 0.12, Dz * 0.9, '#bdb4a4'); // lantai teras
  link([-1.3, top + 1.0, 0], [W / 2 + 1.4, top + 1.0, 0], 0.2, '#e8edf0', {seg: 10}); anc('pipe', [W / 2 - 2.5, top + 1.08, Dz / 2 + 0.2]);
  box(W / 2 + 0.6, top + 0.55, 0, 1.6, 0.55, 1.0, '#2b2723'); box(W / 2 + 1.5, top + 0.52, 0, 0.5, 0.4, 0.6, '#1d1a17'); anc('spout', [W / 2 + 1.8, top + 0.55, Dz / 2]);
  for (let k = 0; k < 16; k++) { const f = fr(TT * 0.8 + k / 16), x = -4.5 + (k % 8) * 1.1 + (k > 7 ? 0.5 : 0), z = -Dz / 2 + 0.3 + (k * 0.77) % (Dz - 0.6); box(x, top + 7.5 - f * 5.7, z, 0.06, 0.6, 0.06, '#a7d6f2', {e: 0.5, ns: 1}); }
  anc('rain', [-3, top + 6, Dz / 2]);
  // air mengalir di lantai teras ke pipa ke pancuran, dan menetes
  const fl = [[-3.5, top + 1.25, 0.4], [-1.3, top + 1.22, 0.2], [0.5, top + 1.1, 0], [W / 2 + 0.4, top + 1.1, 0], [W / 2 + 1.7, top + 0.9, 0]];
  for (let k = 0; k < 10; k++) sph(...along(fl, fr(TT * 0.35 + k / 10)), 0.13, '#8fd0f5', {e: 0.6, ns: 1});
  for (let k = 0; k < 6; k++) { const f = fr(TT * 0.9 + k / 6); sph(W / 2 + 1.9 + f * 0.9, top + 0.7 - f * f * 3.4, 0, 0.12, '#8fd0f5', {e: 0.7, ns: 1}); }
  // rembesan ke bawah melalui lapisan penyaring menuju pipa
  for (let k = 0; k < 8; k++) { const f = fr(TT * 0.25 + k / 8), x = -5 + k * 0.9; sph(x + f * 1.5, top + 0.35 - f * 0.18, Dz / 2 + 0.04, 0.07, '#8fd0f5', {e: 0.7, ns: 1}); }
});

// ===== KAPAL PINISI =====
reg('pinisi', 'kapal pinisi Bulukumba (lambung palari bergaya Tana Beru): lunas, gading, strake papan, pasak kayu, geladak, dua tiang (depan lebih tinggi) dengan layar gaff berdiri + topsail + tiga layar depan di bowsprit (anjong) = tujuh layar. Sumbu x, haluan +x. param: build (0-6 atau [t0,t1]: lunas, gading, papan, pasak, tiang, layar), sail. jangkar: keel, rib, plank, pasak, mast, sail, bow, jib', (o) => {
  const b = Array.isArray(o.build) ? sm((TS - o.build[0]) / Math.max(0.3, o.build[1] - o.build[0])) * 6 : (o.build == null ? 6 : o.build);
  const L = 18, ns = 19, step = L / (ns - 1), nP = 14, bm = 2.6;
  const prof = (x) => { const u = x / (L / 2), ua = Math.abs(u); const br = bm * Math.pow(Math.max(0.0004, 1 - Math.pow(ua, u > 0 ? 1.9 : 2.6)), 0.55) + 0.06; const top = 3.0 + (u > 0 ? 1.0 * u * u : 0.7 * u * u); const kl = 0.5 + (u > 0 ? 1.6 * Math.pow(u, 2.2) : 1.1 * u * u); return {br, top, kl}; };
  const hp = (x, a) => { const p = prof(x); return [x, p.top - (p.top - p.kl) * Math.pow(Math.max(0, Math.cos(a)), 0.9), p.br * Math.sin(a)]; };
  const roll = Math.sin(TT * 0.8) * 0.02, bob = Math.sin(TT * 1.1) * 0.08;
  const slip = b <= 3.01; pushM(T(0, slip ? 1.5 : -1.2 + bob, 0)); pushM(slip ? T(0, 0, 0) : RX(roll));
  if (slip) { popM(); popM(); for (let q = -3; q <= 3; q++) { box(q * 2.6, -0.35, 0, 0.5, 1.3, 4.2, '#7a5535'); box(q * 2.6, 0.35, 0, 0.5, 0.3, 1.1, '#5f3a22'); } box(0, -0.95, 0, 21, 0.3, 1.0, '#4a2f1c'); pushM(T(0, 1.5, 0)); pushM(T(0, 0, 0)); }
  // lunas
  if (b > 0) { const f = Math.min(1, b), nk = Math.round(f * (ns - 1)); const pts = []; for (let i = 0; i <= nk; i++) { const x = -L / 2 + i * step; pts.push([x, prof(x).kl - 0.05, 0]); } if (pts.length > 1) path(pts, 0.2, '#5b3a22', {seg: 6}); anc('keel', [0, prof(0).kl - 0.05, 0]); if (f > 0.9) { const kb = prof(L / 2); path([[L / 2, kb.kl, 0], [L / 2 + 0.5, kb.top - 0.4, 0], [L / 2 + 1.0, kb.top + 0.5, 0]], 0.2, '#5b3a22', {seg: 6}); const ks = prof(-L / 2); path([[-L / 2, ks.kl, 0], [-L / 2 - 0.2, ks.top - 0.3, 0], [-L / 2 - 0.2, ks.top + 0.6, 0]], 0.2, '#5b3a22', {seg: 6}); anc('bow', [L / 2 + 1.0, kb.top + 0.5, 0]); } }
  // gading
  if (b > 1) { const f = Math.min(1, b - 1); for (let i = 1; i < ns - 1; i += 2) { if ((i - 1) / (ns - 2) > f) break; const x = -L / 2 + i * step, pts = []; for (let j = 0; j <= 10; j++) pts.push(hp(x, -1.45 + j * 2.9 / 10)); path(pts, 0.1, '#8a5a34', {seg: 5}); } const p5 = hp(-L / 2 + 6 * step, 1.15); anc('rib', p5); }
  // strake papan
  if (b > 2) { const f = Math.min(1, b - 2), cols = ['#c9954f', '#b8823f', '#d1a05c', '#be8944']; for (let j = 0; j < nP; j++) { if ((j + 1) / nP > f + 0.08) break; const a0 = -1.45 + j * 2.9 / nP, a1 = a0 + 2.9 / nP, am = (a0 + a1) / 2; for (let i = 0; i < ns - 1; i++) { const x0 = -L / 2 + i * step, x1 = x0 + step; link(hp(x0, am), hp(x1, am), 0.2, cols[(j + (i >> 2)) % 4], {seg: 5}); } } anc('plank', hp(0.5, 0.9).map((v, k) => k === 2 ? v + 0.18 : v)); }
  // bulwark, geladak, bangunan
  if (b > 2.4) {
    for (const s of [-1, 1]) { const pts = []; for (let i = 0; i < ns; i++) { const x = -L / 2 + i * step, p = prof(x); pts.push([x, p.top + 0.55, s * p.br]); } path(pts, 0.1, '#4a2f1c', {seg: 5}); for (let i = 1; i < ns; i += 2) { const x = -L / 2 + i * step, p = prof(x); link([x, p.top, s * p.br], [x, p.top + 0.55, s * p.br], 0.07, '#5f3a22', {seg: 4}); } const pr = []; for (let i = 0; i < ns; i++) { const x = -L / 2 + i * step, p = prof(x); pr.push([x, p.top + 0.02, s * p.br]); } path(pr, 0.12, '#3b2414', {seg: 5}); }
    for (let i = 0; i < ns - 1; i++) { const x = -L / 2 + (i + 0.5) * step, p = prof(x); box(x, p.top - 0.06, 0, step * 1.02, 0.12, p.br * 1.9, i % 2 ? '#b88650' : '#a97a42'); }
    // rumah geladak belakang + geladak buritan tinggi
    box(-6.6, 4.25, 0, 4.2, 1.9, 2.8, '#c8995a'); box(-6.6, 5.28, 0, 4.4, 0.16, 3.0, '#7a4a2b'); for (let k = 0; k < 4; k++) for (const s of [-1, 1]) box(-8.0 + k * 1.0, 4.4, s * 1.42, 0.55, 0.6, 0.05, '#1f2a33');
    box(-8.2, 3.9, 0, 2.4, 0.7, 4.4, '#b88650'); anc('lantai', [-6.6, 4.4, 1.5]);
    cyl(3.0, 3.35, 0, 0.35, 0.7, '#5f3a22', {seg: 8}); box(5.4, 3.6, 0, 0.8, 0.5, 0.9, '#6b3f24'); // windlass & hatch
    for (const s of [-1, 1]) path([[-9.4, 2.4, s * 1.2], [-11.2, 0.6, s * 1.5]], 0.14, '#6b3f24', {seg: 6}); // dayung kemudi
  }
  if (b > 3) { for (let i = 1; i < ns - 1; i += 1) for (let j = 1; j < nP; j += 2) { const x = -L / 2 + i * step, a = -1.45 + j * 2.9 / nP; const p = hp(x, a), q = hp(x, -a); sph(p[0], p[1], p[2] + (p[2] > 0 ? 0.17 : -0.17), 0.055, '#3b2414', {seg: 5, ns: 1}); sph(q[0], q[1], q[2] + (q[2] > 0 ? 0.17 : -0.17), 0.055, '#3b2414', {seg: 5, ns: 1}); } anc('pasak', hp(1.0, 0.8).map((v, k) => k === 2 ? v + 0.2 : v)); }
  // tiang + bowsprit
  const mfx = 2.2, mmx = -3.6, mfh = 15.5, mmh = 12.0, deckY = 3.0;
  const bsT = [L / 2 + 0.9, prof(L / 2).top + 0.3, 0], bsE = [L / 2 + 7.6, prof(L / 2).top + 3.2, 0];
  if (b > 4) {
    const f = Math.min(1, b - 4);
    [[mfx, mfh], [mmx, mmh]].forEach(([x, h], k) => { cyl(x, deckY + h * f / 2, 0, 0.24 - k * 0.03, h * f, '#6b3f24', {seg: 8}); if (f > 0.95) { box(x, deckY + h * 0.55, 0, 0.5, 0.3, 0.5, '#5f3a22'); } });
    path([bsT, bsE], 0.2, '#6b3f24', {seg: 6}); anc('mast', [mfx, deckY + 5.0, 0.25]);
    if (f > 0.95) { for (const [x, h] of [[mfx, mfh], [mmx, mmh]]) for (const s of [-1, 1]) for (let q = 0; q < 3; q++) { const t = prof(x + (q - 1) * 0.8); link([x, deckY + h * (0.82 - q * 0.04), 0], [x + (q - 1) * 0.8, t.top + 0.55, s * (t.br - 0.05)], 0.03, '#2b2118', {seg: 4, ns: 1}); } link([mfx, deckY + mfh, 0], bsE, 0.035, '#2b2118', {seg: 4, ns: 1}); link([mfx, deckY + mfh, 0], [-L / 2 - 0.2, 3.6, 0], 0.035, '#2b2118', {seg: 4, ns: 1}); }
  }
  const sf = o.sail != null ? o.sail : (b > 5 ? Math.min(1, b - 5) : 0);
  if (sf > 0) {
    const can = '#f2ebd8', can2 = '#e8dfc6', sc = (t) => 1 - (1 - sf) * (1 - t);
    [[mfx, mfh, 0.05, 0], [mmx, mmh, -0.05, 2]].forEach(([x, h, z, ph]) => {
      const yb = deckY + 0.9, yg = deckY + h * 0.5, Lb = 5.6 * sf, gx = x - 4.2 * sf, gy = yg + 2.3 * sf; // layar gaff berdiri
      polyStrips([[x - 0.15, yb], [x - Lb, yb], [x - Lb, gy - 0.2], [x - 0.15, yg + 0.1]], 24, z + 0.3, can, {alt: can2, belly: 0.5 * sf, ph, flut: 0.05});
      link([x, yg + 0.1, z + 0.25], [gx - 0.2, gy, z + 0.25], 0.07, '#4a2f1c', {seg: 5}); link([x, yb, z + 0.25], [x - Lb, yb, z + 0.25], 0.07, '#4a2f1c', {seg: 5}); // gaff & boom
      const ty = deckY + h * 0.97; polyStrips([[x - 0.15, yg + 0.35], [x - 3.6 * sf, gy + 0.2], [x - 0.15, ty]], 10, z + 0.3, can, {alt: can2, belly: 0.4 * sf, ph: ph + 1, flut: 0.08}); // topsail
    });
    for (let k = 0; k < 3; k++) { const hx = mfx + 0.1, hy = deckY + mfh * (0.93 - k * 0.1), tx = lerpv(bsT[0], bsE[0], 0.45 + k * 0.28), ty2 = lerpv(bsT[1], bsE[1], 0.45 + k * 0.28), cx = mfx + 0.7 + k * 0.2, cy = deckY + 3.4 + k * 1.2;
      polyStrips([[hx, hy], [tx, ty2 + 0.1], [cx + 0.5, cy]], 9, 0.08, can2, {alt: can, belly: 0.55 * sf, ph: k * 1.7, flut: 0.12}); if (k === 1) anc('jib', [(hx + tx) / 2, (hy + ty2) / 2, 0.3]); }
    anc('sail', [mmx - 2.8, deckY + 4.3, 0.5]);
    for (const [x, h, c] of [[mfx, mfh, '#c93a2e'], [mmx, mmh, '#1f4aa0']]) polyStrips([[x, deckY + h], [x - 1.6, deckY + h - 0.15 + Math.sin(TT * 4) * 0.1], [x, deckY + h - 0.5]], 6, 0.1, c, {flut: 0.25}); // bendera
  }
  popM(); popM();
  // riak busa di sekeliling lambung
  for (let k = 0; k < 14; k++) { const f = fr(TT * 0.25 + k / 14), x = -L / 2 - 1 + f * (L + 2), s = k % 2 ? 1 : -1; box(x, 0.03, s * (prof(Math.max(-L / 2, Math.min(L / 2, x))).br + 0.4 + f * 0.9), 1.4 + f, 0.04, 0.16, '#eef6fa', {ns: 1}); }
});

// ===== KERETA CEPAT WHOOSH (KCIC400AF / CR400AF) — 8 gerbong 4M4T, panjang 209 m, lebar 3,36 m =====
reg('whoosh', 'kereta cepat Whoosh CR400AF/KCIC400AF "Komodo Merah": 8 gerbong (M bermotor: gerbong 2,4,5,7; T tanpa motor: 1,3,6,8 dengan pantograf di 3 & 6), hidung aerodinamis, bogie berputar, kabel & pantograf. Sumbu x, depan +x, rel y=0. param: n, ex (bogie terurai), v (laju m/dtk bergerak relatif), x0, lines (garis kecepatan). jangkar: nose, pantograf, motor, trailer, bogie, window, roof', (o) => {
  const n = o.n || 8, cl = 7.45, gap = 0.2, W = 1.9, ex = tIn(o.ex), y0 = 0.62, total = n * (cl + gap), RED = '#c9302c', SIL = '#e9ecec';
  const motors = [1, 3, 4, 6], x00 = (o.x0 || 0) + (o.v || 0) * TS;
  pushM(T(x00, 0, 0));
  const bodyX = i => -total / 2 + (i + 0.5) * (cl + gap) - 1.0;
  for (let i = 0; i < n; i++) {
    const cx = bodyX(i), motor = motors.includes(i);
    box(cx, y0 + 0.36, 0, cl, 0.72, W, RED); // badan bawah merah
    box(cx, y0 + 1.18, 0, cl, 0.95, W * 0.98, SIL); // badan atas perak
    box(cx, y0 + 1.15, 0, cl - 0.5, 0.5, W * 0.99 + 0.04, '#1b2a38'); // pita kaca
    for (let k = 0; k < 9; k++) { const wx = cx - cl / 2 + 0.55 + k * (cl - 1.1) / 8; for (const s of [-1, 1]) box(wx, y0 + 1.15, s * (W / 2 + 0.022), 0.5, 0.42, 0.02, '#26394a'); }
    box(cx, y0 + 1.76, 0, cl, 0.3, W * 0.86, '#d3d7d9'); box(cx, y0 + 1.98, 0, cl - 0.6, 0.16, W * 0.62, '#aeb4b8'); // atap melengkung
    box(cx, y0 + 0.72, 0, cl + 0.01, 0.07, W + 0.03, '#f2c21c'); // garis kuning
    for (const s of [-1, 1]) for (const dxx of [-1, 1]) box(cx + dxx * cl * 0.38, y0 + 0.95, s * (W / 2 + 0.03), 0.62, 0.85, 0.03, '#d8dcdc'); // pintu
    box(cx + cl / 2 + gap / 2, y0 + 1.0, 0, gap, 1.5, W * 0.84, '#26292d'); // gangway
    const motorOff = ex * 1.4;
    for (const bx of [-cl * 0.3, cl * 0.3]) {
      box(cx + bx, 0.58 - ex * 0.5, 0, 1.9, 0.2, 1.1 + motorOff * 0.4, motor ? '#d98a3b' : '#5a636c'); if (motor) box(cx + bx, 0.52 - ex * 0.5, 0, 0.6, 0.34, 0.8, '#b86a22');
      for (const s of [-1, 1]) for (const ax of [-0.65, 0.65]) { cyl(cx + bx + ax, 0.4 - ex * 0.5, s * (0.78 + motorOff), 0.4, 0.14, '#33383e', {rx: Math.PI / 2, seg: 14}); }
      box(cx + bx, 0.4 - ex * 0.5, 0, 0.3, 0.06, 1.6 + motorOff * 0.4, '#454b54'); box(cx + bx + 0.65, 0.4 - ex * 0.5, 0, 0.08, 0.08, 1.7 + motorOff * 0.4, '#6b6f75'); box(cx + bx - 0.65, 0.4 - ex * 0.5, 0, 0.08, 0.08, 1.7 + motorOff * 0.4, '#6b6f75');
    }
    if (motor) { box(cx, 0.45 - ex * 0.6, 0, 2.4, 0.3, 1.3, '#d98a3b'); if (i === 1) anc('motor', [cx, 0.45 - ex * 0.6, W / 2 + 0.3]); } else if (i === 2) anc('trailer', [cx, y0 + 1.2, W / 2 + 0.2]);
    if (i === 1) anc('bogie', [cx + cl * 0.3, 0.45 - ex * 0.5, W / 2 + 0.3]); if (i === 4) anc('window', [cx + 1.2, y0 + 1.15, W / 2 + 0.05]);
    if (i === 2 || i === 5) { const px = cx - 0.5, ty = y0 + 2.06; box(px, ty + 0.12, 0, 2.0, 0.16, 1.1, '#2b2f33'); for (const sz of [-0.3, 0.3]) { link([px - 0.9, ty + 0.2, sz], [px - 0.2, ty + 1.3, sz * 0.4], 0.045, '#2b2f33', {seg: 5}); link([px - 0.2, ty + 1.3, sz * 0.4], [px + 0.7, ty + 0.2, sz], 0.045, '#2b2f33', {seg: 5}); } box(px - 0.2, ty + 1.38, 0, 0.9, 0.05, 0.14, '#e8edf0'); box(px + 0.6, ty + 0.2, 0, 0.6, 0.22, 0.6, '#c0c5c9'); if (i === 2) anc('pantograf', [px - 0.2, ty + 1.4, 0]); }
    if (i === 3) anc('roof', [cx, y0 + 2.1, 0]);
  }
  // hidung aerodinamis (depan +x dan belakang -x)
  for (const sg of [1, -1]) {
    const x0 = sg * (total / 2 - 1.0 - 0.02), NL = 6.8;
    for (let k = 0; k < 16; k++) { const u = k / 15, xx = x0 + sg * (0.3 + u * NL), hT = 1.62 * (1 - 0.66 * Math.pow(u, 2.1)), wk = W * (1 - 0.8 * Math.pow(u, 1.7)), hb = Math.min(0.72, hT * 0.52);
      box(xx, y0 + hb / 2, 0, NL / 15 * 1.15, hb, wk, RED); box(xx, y0 + hb + (hT - hb) / 2 + 0.02, 0, NL / 15 * 1.15, hT - hb, wk * 0.98, k > 9 ? '#d7dbdc' : SIL);
      if (k > 1 && k < 13) box(xx, y0 + hb + (hT - hb) * 0.55, 0, NL / 15 * 1.16, (hT - hb) * 0.26, wk * 0.82, '#1b2a38'); // kaca kabin
      box(xx, y0 + hT + 0.06, 0, NL / 15 * 1.15, 0.12, wk * 0.5, '#b9bfc3'); }
    box(x0 + sg * (NL + 0.45), y0 + 0.3, 0, 0.4, 0.34, 0.5, '#3a3f45'); for (const s of [-1, 1]) box(x0 + sg * (NL + 0.25), y0 + 0.46, s * 0.14, 0.12, 0.1, 0.16, sg > 0 ? '#fff6c8' : '#ff4a3a', {e: 1});
  }
  anc('nose', [total / 2 + 5.4, y0 + 0.9, 0]);
  const g = TT * (o.speed == null ? 9 : o.speed);
  for (let i = 0; i < n; i++) { const cx = bodyX(i); for (const bx of [-cl * 0.3, cl * 0.3]) for (const ax of [-0.65, 0.65]) for (const s of [-1, 1]) { box(cx + bx + ax, 0.4 - ex * 0.5, s * (0.78 + ex * 1.4 + 0.08), 0.5, 0.07, 0.04, '#ff9a2e', {rz: g, ns: 1}); box(cx + bx + ax, 0.4 - ex * 0.5, s * (0.78 + ex * 1.4 + 0.08), 0.07, 0.5, 0.04, '#e2e7ea', {rz: g, ns: 1}); } }
  // garis kecepatan
  if (o.lines) { const R = rng(12); for (let k = 0; k < 14; k++) { const f = fr(TT * 1.4 + R()), xx = total / 2 + 8 - f * (total + 30), zz = (R() < 0.5 ? -1 : 1) * (2.2 + R() * 2.5), yy = 0.8 + R() * 3; box(xx, yy, zz, 6 + R() * 6, 0.05, 0.05, '#ffffff', {e: 0.8, ns: 1}); } }
  popM();
});

reg('terowongan_hsr', 'mulut terowongan kereta cepat: bukit hijau, kepala terowongan beton, cincin lining, lorong gelap dengan lampu, rel masuk. Sumbu x (kereta masuk ke +x), portal di x=0. jangkar: portal, lining, bukit', (o) => {
  const R = o.rad || 4.2;
  cyl(26, 9, 0, 34, 20, '#5f8f4c', {rt: 0.35, rb: 1, seg: 16, ns: 1}); cyl(30, 17, -3, 18, 12, '#6a9a54', {rt: 0.25, rb: 1, seg: 12, ns: 1});
  { const Rr = rng(8); for (let k = 0; k < 18; k++) broadTree(6 + Rr() * 40, (Rr() - 0.5) * 36, 4 + Rr() * 3, ['#3f8a45', '#4c9a4c'][k % 2]); }
  const hr = R + 0.25;
  for (const s of [-1, 1]) box(0.5, 6.0, s * (hr + (10 - hr) / 2), 1.4, 12, 10 - hr, '#c9c6bd');
  box(0.5, (2 * R + 0.3 + 12) / 2, 0, 1.4, 12 - 2 * R - 0.3, 2 * hr, '#c9c6bd'); box(0.5, 12.4, 0, 1.6, 0.6, 21, '#aaa79f');
  box(1.6, R + 0.05, 0, 1.0, 2 * R + 0.3, 2 * hr + 0.2, '#0a0a0c');
  pushM(T(0, R + 0.05, 0)); ringBoxes(0, R + 0.2, 1.6, 0.7, 20, ['#d8d5cc', '#c6c3ba'], {}); popM();
  link([0.4, R + 0.05, 0], [16, R + 0.05, 0], R * 0.97, '#0a0a0c', {seg: 22});
  for (let k = 0; k < 6; k++) sph(3 + k * 2.4, R * 1.8, 0, 0.18, '#ffeeb0', {e: 1, ns: 1, seg: 6});
  for (const s of [-0.72, 0.72]) box(8, 0.2, s, 16, 0.18, 0.12, '#4b4f55');
  anc('portal', [0.5, R * 1.9, 0]); anc('lining', [0.5, R * 0.8, R * 0.9]); anc('bukit', [24, 16, 0]);
});
