// ---------- Pustaka NUSANTARA v3: adegan penjelas per kalimat naskah ----------
const mixc3 = (a, b, u) => { const p = s => [1, 3, 5].map(i => parseInt(s.substr(i, 2), 16)); const A = p(a), B = p(b); return '#' + A.map((v, i) => Math.round(v + (B[i] - v) * u).toString(16).padStart(2, '0')).join(''); };
const STONE3 = ['#9a9183', '#8c8477', '#a39a8b'];
const bounce3 = (u) => 0.5 - 0.5 * Math.cos(Math.PI * 2 * u);

// ===== Borobudur: tiga jenis kuncian batu =====
reg('batu_kunci', 'tiga pasang batu andesit saling mengunci tanpa semen: tonjolan-lekukan, ekor burung, lidah-alur; blok atas naik-turun memperlihatkan sambungan. jangkar: knob, ekor, lekuk', (o) => {
  const gap = 0.1 + 1.7 * sm(TS / 2.2), W = 4.2, H = 1.5, D = 3.0, dk = '#1b1814';
  const lower = (x, c) => box(x, H / 2, 0, W, H, D, c);
  const upper = (x, c) => box(x, H + gap + H / 2, 0, W, H, D, c);
  // 1. tonjolan & lekukan
  { const x = -5.2; lower(x, STONE3[0]); upper(x, STONE3[1]);
    for (const dx of [-1.0, 1.0]) { cyl(x + dx, H + 0.28, 0, 0.42, 0.56, STONE3[2], {seg: 14}); box(x + dx, H + gap + 0.3, D / 2 + 0.012, 0.9, 0.62, 0.03, dk); }
    anc('knob', [x + 1.0, H + 0.4, D / 2 + 0.05]); }
  // 2. ekor burung (dovetail): leher sempit + kepala lebar
  { const x = 0, hw = 0.5; lower(x, STONE3[1]); upper(x, STONE3[0]);
    box(x, H + 0.28, 0, 0.95, 0.56, D * 0.92, STONE3[2]); box(x, H + 0.8, 0, 1.9, 0.5, D * 0.92, STONE3[2]);
    box(x, H + gap + 0.28, D / 2 + 0.012, 0.95, 0.56, 0.03, dk); box(x, H + gap + 0.3, D / 2 + 0.012, 1.9, 0.5, 0.03, dk);
    box(x, H + gap + 0.55, D / 2 + 0.012, 1.9, 0.12, 0.03, dk);
    anc('ekor', [x + 1.0, H + 0.85, D / 2 + 0.05]); }
  // 3. lidah & alur
  { const x = 5.2; lower(x, STONE3[0]); upper(x, STONE3[1]);
    box(x, H + 0.0, D / 2 + 0.012, 1.0, 0.45, 0.03, dk); box(x, H + 0.28, 0, 1.0, 0.56, D * 0.9, STONE3[2]);
    box(x, H + gap + 0.0, D / 2 + 0.012, 1.0, 0.1, 0.03, dk);
    anc('lekuk', [x + 0.6, H + 0.3, D / 2 + 0.05]); }
  box(0, -0.15, 0, 17, 0.3, 5.2, '#6f685d');
});

// ===== Borobudur: tanah isian jenuh air mendorong dinding =====
reg('tanah_isian', 'irisan tanah isian di belakang dinding batu Borobudur: air hujan meresap, tanah jenuh membengkak, dinding batu miring pelan dan retak. jangkar: dinding, tanah, retak, tekanan', (o) => {
  const lean = 0.01 + 0.2 * sm(TS / 5.5), W = 12, Dz = 3.2, wet = sm(TS / 3.2);
  box(0, 0.6, 0, W + 2, 1.2, Dz + 0.4, '#5d4a37');
  box(-1, 2.4, 0, W - 2, 2.4, Dz, mixc3('#8b6a47', '#4a3a2a', wet)); box(-1, 3.74, 0, W - 2, 0.28, Dz, mixc3('#a38455', '#5b4a35', wet));
  const R = rng(5); for (let k = 0; k < 20; k++) sph(-6 + R() * 10, 1.4 + R() * 2.6 * wet + 0.1, Dz / 2 + 0.03, 0.07, '#7cc4ee', {seg: 5, ns: 1, e: 0.6});
  anc('tanah', [-4, 2.4, Dz / 2]);
  // dinding batu (tumpukan) yang bergeser keluar dan miring
  for (let r = 0; r < 5; r++) for (let c = 0; c < 2; c++) {
    const h = r * 0.75 + 0.4, off = lean * Math.pow(h, 1.15) * 3.2; pushM(T(5.2 + c * 0.0 + off + (r % 2) * 0.35 * (c ? 1 : -1) * 0, 1.2 + h + 0.0, 0)); pushM(RZ(-lean * 0.6));
    box(0, 0, 0, 1.6, 0.72, Dz, STONE3[(r + c) % 3]); popM(); popM();
  }
  anc('dinding', [6.2 + lean * 8, 3.2, Dz / 2]);
  // retak yang membesar
  for (let k = 0; k < 4; k++) { const f = sm((lean - 0.06) / 0.16); box(5.9 + lean * 5 + (k % 2) * 0.5, 1.9 + k * 0.7, Dz / 2 + 0.06, 0.04 + 0.1 * f, 0.5 * f + 0.001, 0.02, '#1b1814', {rz: 0.5 * (k % 2 ? 1 : -1)}); }
  anc('retak', [6.6 + lean * 5, 2.9, Dz / 2 + 0.1]);
  // panah tekanan dari tanah
  for (let k = 0; k < 3; k++) { const ph = fr(TT * 0.7 + k / 3), x = 1.5 + ph * 2.2; cyl(x, 2.0 + k * 0.7, 0, 0.1, 0.9, '#d9442a', {rz: -Math.PI / 2, seg: 8, ns: 1}); cyl(x + 0.62, 2.0 + k * 0.7, 0, 0.26, 0.4, '#d9442a', {rz: -Math.PI / 2, rt: 0.01, rb: 1, seg: 8, ns: 1}); }
  anc('tekanan', [3, 3.8, Dz / 2]);
  // hujan
  for (let k = 0; k < 14; k++) { const f = fr(TT * 0.9 + k / 14); box(-6 + (k * 0.9) % 11, 9 - f * 5.2, Dz / 2 - 0.4 + (k % 3) * 0.4, 0.06, 0.5, 0.06, '#8fd0f5', {ns: 1, e: 0.6}); }
});

// ===== Rumah Gadang: ijuk vs genteng di timbangan =====
reg('timbang', 'timbangan: atap ijuk ringan (kiri) vs tumpukan genteng berat (kanan); balok miring ke sisi genteng. jangkar: ijuk, genteng', (o) => {
  const tilt = 0.27 * sm(TS / 2.2) + 0.02 * Math.sin(TT * 2.5), L = 4.4, yc = 6.2;
  cyl(0, 2.9, 0, 0.35, 5.8, '#6b4c33', {seg: 10}); box(0, 0.15, 0, 4.4, 0.3, 2.2, '#4a2f1c'); sph(0, yc, 0, 0.45, '#c99a10', {seg: 10});
  pushM(T(0, yc, 0)); pushM(RZ(-tilt)); box(0, 0, 0, L * 2, 0.28, 0.4, '#8a5a2b'); popM(); popM();
  const ly = yc + L * Math.sin(tilt), ry = yc - L * Math.sin(tilt), lx = -L * Math.cos(tilt), rx = L * Math.cos(tilt), ch = 3.0;
  for (const [x, y] of [[lx, ly], [rx, ry]]) { link([x, y, 0], [x - 1.4, y - ch, 0], 0.05, '#555', {seg: 4}); link([x, y, 0], [x + 1.4, y - ch, 0], 0.05, '#555', {seg: 4}); cyl(x, y - ch - 0.08, 0, 1.6, 0.16, '#c8c2b3', {seg: 18}); }
  pushM(T(lx, ly - ch + 0.1, 0)); pushM(S(0.52, 0.52, 0.52)); gonjongRoof(4.4, 3.0, 0.2, {n: 12, ridge: 0.8, lift: 1.1, horn: 1.4, hornL: 0.9}); popM(); popM();
  anc('ijuk', [lx, ly - ch + 1.0, 0.8]);
  for (let r = 0; r < 4; r++) for (let c = 0; c < 4 - r; c++) box(rx - 1.1 + c * 0.55 + r * 0.27, ry - ch + 0.35 + r * 0.32, 0, 0.5, 0.28, 1.3, ['#b5532f', '#a64a2a'][(r + c) % 2]);
  anc('genteng', [rx, ry - ch + 0.8, 0.8]);
});

// ===== Rumah Gadang: kayu direndam di kolam =====
reg('rendam_kayu', 'kolam perendaman: batang kayu juha tua berwarna makin gelap, gelembung, rayap menjauh dari kayu yang sudah direndam. jangkar: kayu, kolam, rayap', (o) => {
  const d = sm(TS / 5);
  box(0, -0.6, 0, 13, 1.2, 6.4, '#6d5a43'); box(0, 1.0, 0, 12, 2.4, 5.4, '#4b9bd0', {glass: true, ns: 1}); box(0, 0.4, 0, 11.6, 0.1, 5, '#3a6e90');
  for (const [i, z] of [[0, -1.4], [1, 0], [2, 1.4]]) { const c = mixc3('#b98a52', '#4b2e1b', d); cyl(0, 0.9 + i * 0.05, z, 0.62, 10.4, c, {rz: Math.PI / 2, seg: 14}); cyl(5.22, 0.9 + i * 0.05, z, 0.5, 0.04, mixc3('#d8b680', '#6b4a2e', d), {rz: Math.PI / 2, seg: 14}); }
  anc('kayu', [5.2, 1.2, 1.4]);
  for (let k = 0; k < 10; k++) { const f = fr(TT * 0.5 + k / 10), x = -4.5 + (k * 1.07) % 9; sph(x + Math.sin(TT * 3 + k) * 0.15, 0.5 + f * 1.7, -2 + (k % 4) * 1.3, 0.09, '#d7effb', {seg: 5, ns: 1, e: 0.6}); }
  box(0, 2.15, 0, 12, 0.06, 5.4, '#a5d8f2', {glass: true, ns: 1}); anc('kolam', [-5.6, 1.6, 2.7]);
  // rayap kecil: mendekat lalu menjauh
  for (let k = 0; k < 3; k++) { const ph = fr(TT * 0.25 + k * 0.33), a = ph < 0.5 ? ph * 2 : 1 - (ph - 0.5) * 2, x = 7.4 - a * 1.9, z = -1.6 + k * 1.6; sph(x, 2.45 + 0.0, z, 0.19, '#2a2018', {seg: 6}); sph(x - 0.22 * (ph < 0.5 ? 1 : -1) * -1, 2.45, z, 0.13, '#3a2c20', {seg: 6}); }
  for (let r = 0; r < 4; r++) cyl(8.3, 0.45 + r * 0.9, 0, 0.45, 5.4, '#c9a066', {rx: Math.PI / 2, seg: 10}); anc('rayap', [7.2, 2.7, 0]);
});

// ===== Rumah Gadang: batu sandi vs tiang tertanam saat air tanah naik =====
reg('batu_sandi_air', 'irisan tanah: tiang yang ditanam (kiri) membusuk oleh air tanah, tiang di atas batu sandi (kanan) tetap kering. jangkar: batu, airtanah, tiangbusuk', (o) => {
  const rise = 0.5 + 0.5 * sm(TS / 4), W = 14, rot = sm(TS / 5);
  box(0, 0.6, 0, W, 1.2, 4, '#5d4a37'); box(0, 1.9, 0, W, 1.4, 4, '#8b6a47'); box(0, 2.62, 0, W, 0.14, 4, '#6e9a4a');
  box(0, 1.1 + rise * 0.4, 2.02, W, 0.9 + rise * 0.8, 0.04, '#3f8ec9', {glass: true, ns: 1}); anc('airtanah', [-4.8, 1.6 + rise * 0.4, 2.1]);
  // kiri: tiang ditanam
  box(-4.2, 1.5 + 3.6, 0, 0.8, 7.2, 0.8, mixc3('#8b5a2b', '#3d2a1c', rot * 0.0)); box(-4.2, 1.6 + 0.9, 0, 0.84, 1.8, 0.84, mixc3('#8b5a2b', '#2e2118', rot));
  { const R = rng(9); for (let k = 0; k < 7; k++) sph(-4.2 + (R() - 0.5) * 0.9, 1.0 + R() * 1.6, 0.44, 0.07 + 0.08 * rot * R(), '#5a7a3a', {seg: 5, ns: 1}); }
  anc('tiangbusuk', [-3.6, 1.9, 0.5]);
  // kanan: batu sandi
  box(4.2, 2.8, 0, 1.9, 0.38, 1.9, '#b5ad9d'); box(4.2, 2.8 + 0.19, 0, 1.7, 0.04, 1.7, '#a49c8c'); box(4.2, 3.0 + 3.6, 0, 0.8, 7.2, 0.8, '#8b5a2b'); anc('batu', [4.9, 3.0, 1.0]);
  for (let k = 0; k < 12; k++) { const f = fr(TT * 0.6 + k / 12); box(-6 + (k * 1.07) % 12, 9.5 - f * 6.7, 0.5 + (k % 3) * 0.5, 0.06, 0.5, 0.06, '#8fd0f5', {ns: 1, e: 0.6}); }
  for (let k = 0; k < 6; k++) { const f = fr(TT * 0.3 + k / 6); sph(-4.2 - 0.8 + k * 1.6 % 3, 2.6 - f * 1.6, 0.55, 0.08, '#7cc4ee', {seg: 5, ns: 1, e: 0.6}); }
});

// ===== gelombang gempa merambat di tanah =====
reg('gelombang_gempa', 'gelombang gempa: cincin kejut melebar dari pusat gempa di tanah, retakan tanah. param: n cincin. jangkar: pusat', (o) => {
  const n = o.n || 4;
  for (let i = 0; i < n; i++) { const f = fr(TT * 0.35 + i / n), r = 2 + f * 34, th = 1.2 * (1 - f) + 0.2; for (let k = 0; k < 40; k++) { const a = k / 40 * 6.2832; box(Math.cos(a) * r, 0.1, Math.sin(a) * r, th, 0.1, r * 0.2, '#d9442a', {ry: -a, ns: 1, e: 0.5}); } }
  sph(0, 0.5 + 0.3 * Math.sin(TT * 14), 0, 1.0, '#f08a24', {seg: 10, e: 0.9, ns: 1}); anc('pusat', [0, 1.6, 0]);
});

// ===== Pinisi: galangan Tana Beru (pantai, bengkel, tumpukan kayu, pengrajin) =====
const orang3 = (x, z, ry, col, o = {}) => {
  pushM(T(x, 0, z)); pushM(RY(ry)); COMP.person({col, walk: o.walk === true});
  if (o.songkok) cyl(0, 2.58, 0, 0.29, 0.24, '#141414', {seg: 10});
  if (o.sarung) box(0, 0.62, 0, 0.46, 1.0, 0.66, o.sarung);
  if (o.alat) { pushM(T(0.0, 1.95, 0.5)); pushM(RZ(Math.sin(TT * 5 + x) * 0.9 - 0.3)); box(0, -0.55, 0, 0.1, 1.1, 0.1, '#6b4c33'); box(0.12, -1.1, 0, 0.32, 0.12, 0.1, '#9aa3ad'); popM(); popM(); }
  popM(); popM();
};
reg('galangan', 'galangan kapal di pantai Tana Beru: bengkel beratap, tumpukan kayu, pengrajin memahat, panrita lopi (berpeci hitam, bersarung) memberi arah. jangkar: panrita, tukang, bengkel', (o) => {
  box(-12, 3.1, -8, 9, 0.35, 7, '#8a5a2b'); for (const dx of [-3.8, 3.8]) for (const dz of [-3, 3]) box(-12 + dx, 1.45, -8 + dz, 0.4, 3.0, 0.4, '#6b4c33');
  for (let k = 0; k < 9; k++) box(-12, 3.34 + (k % 2) * 0.02, -8 - 3.2 + k * 0.8, 9.2, 0.1, 0.84, ['#a98a5a', '#9a7a4c'][k % 2]);
  for (let r = 0; r < 4; r++) for (let c = 0; c < 4 - r; c++) cyl(10 + c * 1.1 + r * 0.55, 0.45 + r * 0.9, -5, 0.5, 4.6, ['#8a5a2b', '#a37a45'][(r + c) % 2], {rx: Math.PI / 2, seg: 10});
  orang3(4.5, 1.8, -2.3, '#2f66c9', {alat: true}); orang3(-4.5, 2.6, 2.0, '#c9742a', {alat: true}); orang3(1.5, 4.4, 3.5, '#2f8f6a', {alat: true}); orang3(7.0, 3.5, -1.2, '#b24a3a', {alat: true});
  orang3(-7.8, 6.2, 0.9, '#f2f2f2', {songkok: true, sarung: '#7a2d2d', walk: false}); anc('panrita', [-7.8, 3.2, 6.2]); anc('tukang', [4.5, 3.0, 1.8]); anc('bengkel', [-12, 4.4, -8]);
  for (let k = 0; k < 4; k++) { const R = rng(k + 11)(); palm(-26 + k * 5, -16 - (k % 2) * 3, 8 + R * 2, k + 1); }
});

// ===== Pinisi: kayu besi vs bitti, papan dilengkungkan =====
reg('kayu_lengkung', 'dua jenis kayu (besi/ulin gelap padat, bitti terang lentur) dan papan bitti yang dilengkungkan dengan tali pada penjepit. jangkar: besi, bitti, lengkung', (o) => {
  for (let i = 0; i < 3; i++) { cyl(-7.5, 0.55 + 0, -2.2 + i * 1.15, 0.55, 5.6, '#5a2f1e', {rx: Math.PI / 2, seg: 12}); cyl(-7.5, 1.7, -1.65 + i * 1.15 * 0.0, 0.0001, 0.0001, '#000'); }
  cyl(-7.5, 1.55, -1.65, 0.55, 5.6, '#5a2f1e', {rx: Math.PI / 2, seg: 12}); cyl(-7.5, 1.55, -0.5, 0.55, 5.6, '#4d2819', {rx: Math.PI / 2, seg: 12});
  for (let i = 0; i < 2; i++) cyl(-7.5, 0.55, 2.4 + i * 1.15, 0.55, 5.6, '#d2ad74', {rx: Math.PI / 2, seg: 12});
  cyl(-7.5, 1.55, 2.95, 0.55, 5.6, '#c9a066', {rx: Math.PI / 2, seg: 12}); anc('besi', [-7.5, 1.2, -2.8 + 5.6 / 2 * 0.0]); anc('bitti', [-7.5, 1.9, 3.1]);
  const bend = sm(TS / 3.5), N = 16, L = 11, Rr = 12; let x = 0, y = 0, a = 0, ds = L / N; const px = 1.2, py = 0.9;
  box(px - 0.7, py - 0.4, 0, 0.5, 1.8, 0.9, '#4a2f1c'); box(px + L * 0.62, py - 0.55, 0, 0.5, 2.1, 0.9, '#4a2f1c');
  for (let i = 0; i < N; i++) { a = bend * (i + 0.5) / Rr * ds * 0.9; const dx = Math.cos(a) * ds, dy = Math.sin(a) * ds; pushM(T(px + x + dx / 2, py + y + dy / 2 + 0.55, 0)); pushM(RZ(a)); box(0, 0, 0, ds * 1.03, 0.3, 1.9, ['#c9a066', '#d2ad74'][i % 2]); popM(); popM(); x += dx; y += dy; }
  anc('lengkung', [px + L * 0.5, py + 1.0 + y * 0.45, 1]); link([px + L, py + y + 0.55, 0.7], [px + L + 1.6, py - 1.2, 0.7], 0.08, '#d9c9a0', {seg: 4}); link([px, py + 0.55, 0.7], [px - 0.9, py - 1.2, 0.7], 0.08, '#d9c9a0', {seg: 4});
});

// ===== Pinisi: mendempul sela papan =====
reg('dempul', 'sela antar papan lambung diisi serat dan dempul oleh pengrajin dengan pahat & palu; sela kosong dibandingkan sela yang sudah tertutup, air tertahan. jangkar: celah, dempul, palu', (o) => {
  const pr = sm(TS / 6), L = 12;
  for (let i = 0; i < 4; i++) box(0, i * 1.45, 0, L, 1.3, 0.8, ['#c9954f', '#b8823f', '#d1a05c', '#be8944'][i]);
  for (let i = 0; i < 3; i++) { const y = 0.725 + i * 1.45; box(0, y, 0.2, L - 0.1, 0.15, 0.42, '#20130b'); }
  const x1 = -L / 2 + pr * L; box((x1 - L / 2) / 2 - 0.0, 0.725, 0.42, x1 + L / 2, 0.15, 0.1, '#e6d9b8'); box((x1 - L / 2) / 2, 0.725 + 0.0, 0.48, x1 + L / 2, 0.08, 0.06, '#9a7f52');
  anc('celah', [4.5, 2.2, 0.45]); anc('dempul', [-L / 2 + 1, 0.725, 0.5]);
  pushM(T(x1, 1.5, 0.9)); pushM(RZ(-0.5)); box(0, 0, 0, 0.14, 1.2, 0.14, '#9aa3ad'); popM(); pushM(T(0.35, 1.0 + Math.abs(Math.sin(TT * 9)) * 0.4, 0.0)); pushM(RZ(-0.2)); box(0, 0.2, 0, 0.14, 0.9, 0.14, '#6b4c33'); box(0, 0.8, 0, 0.7, 0.4, 0.4, '#8a5a2b'); popM(); popM(); popM();
  anc('palu', [x1 + 0.4, 2.0, 0.9]);
});

// ===== Pinisi: arah timur laut (kompas) =====
reg('kompas_lunas', 'kompas datar: lunas kayu diarahkan ke timur laut sebelum dipotong. utara = -z, timur = +x. jangkar: timurlaut, utara, lunas', (o) => {
  const sw = 0.12 * Math.sin(TT * 1.2);
  cyl(0, 0.1, 0, 4.2, 0.2, '#e8e1cf', {seg: 40}); cyl(0, 0.24, 0, 3.9, 0.08, '#2b3a55', {seg: 40});
  for (let k = 0; k < 16; k++) { const a = k / 16 * 6.2832, L = k % 4 === 0 ? 0.9 : 0.45; box(Math.sin(a) * 3.45, 0.3, -Math.cos(a) * 3.45, 0.1, 0.06, L, k === 0 ? '#d9442a' : '#e8e1cf', {ry: a}); }
  sph(0, 0.4, -3.3, 0.22, '#d9442a', {seg: 8}); sph(3.3, 0.4, 0, 0.18, '#e8e1cf', {seg: 8}); sph(0, 0.4, 3.3, 0.18, '#e8e1cf', {seg: 8}); sph(-3.3, 0.4, 0, 0.18, '#e8e1cf', {seg: 8});
  pushM(T(0, 0.5, 0)); pushM(RY(-0.785 + sw)); box(0, 0, -1.4, 0.3, 0.1, 2.8, '#d9442a'); box(0, 0, 1.4, 0.3, 0.1, 2.8, '#e8e1cf'); popM(); popM();
  pushM(T(0, 1.2, 0)); pushM(RY(-0.785)); box(0, 0, 0, 0.7, 0.6, 9.6, '#a8743a'); box(0, 0.35, 0, 0.5, 0.06, 9.6, '#c9954f'); cyl(0, 0.0, -5.4, 0.0001, 0.0001, '#000'); popM(); popM();
  const e = Math.sin(TT * 3) * 0.2; for (let k = 0; k < 3; k++) { const f = fr(TT * 0.6 + k / 3); pushM(T(Math.sin(0.785) * (4.6 + f * 3), 1.5, -Math.cos(0.785) * (4.6 + f * 3))); sph(0, 0, 0, 0.3 * (1 - f * 0.5), '#ffd23a', {seg: 8, e: 0.8, ns: 1}); popM(); }
  cyl(Math.sin(0.785) * 4.9, 1.5, -Math.cos(0.785) * 4.9, 0.55, 1.1, '#f2c14a', {rz: 0, seg: 10, rt: 0.01, rb: 1, ns: 1});
  anc('timurlaut', [Math.sin(0.785) * 5.2, 2.2, -Math.cos(0.785) * 5.2]); anc('utara', [0, 0.6, -4.3]); anc('lunas', [-1.0, 1.9, 1.0]);
});

// ===== Pinisi: upacara maccera lopi =====
reg('upacara_lopi', 'upacara maccera lopi: orang3 berkumpul mengelilingi lambung kapal yang selesai di pantai; sesaji tumpeng & talam, kain di haluan, asap dupa. jangkar: sesaji, pemimpin, kapal', (o) => {
  const n = 9; for (let k = 0; k < n; k++) { const a = -1.2 + k * (Math.PI * 1.1 / (n - 1)), r = 9; orang3(Math.sin(a) * r, 6 + Math.cos(a) * 4.2, a + 3.1, ['#b24a3a', '#2f66c9', '#2f8f6a', '#c9742a', '#6f4a9c'][k % 5], {walk: false, songkok: k % 2 === 0}); }
  orang3(0, 9.0, 3.14, '#f4f4f4', {walk: false, songkok: true, sarung: '#7a2d2d'}); anc('pemimpin', [0, 3.2, 9]);
  box(-3, 0.3, 11.5, 3.2, 0.4, 2.0, '#8a5a2b'); cyl(-3.8, 1.5, 11.5, 0.9, 1.9, '#f2d27a', {rt: 0.05, rb: 1, seg: 12}); cyl(-2.2, 0.8, 11.5, 0.9, 0.5, '#f2f2f2', {seg: 14}); sph(-2.2, 1.2, 11.5, 0.35, '#e8a13a', {seg: 8}); anc('sesaji', [-3, 2.8, 11.5]);
  box(3, 0.3, 11.2, 2.4, 0.4, 1.8, '#8a5a2b'); for (let k = 0; k < 5; k++) sph(2.3 + k * 0.35, 0.8, 11.2, 0.3, ['#f2c14a', '#d9442a'][k % 2], {seg: 6});
  for (let k = 0; k < 6; k++) { const f = fr(TT * 0.3 + k / 6); sph(-3.8 + Math.sin(TT + k) * 0.3, 2.9 + f * 2.2, 11.5, 0.16 + f * 0.2, '#e6e6e6', {seg: 6, ns: 1, e: 0.5}); }
  for (const s of [-1, 1]) { cyl(s * 6, 3.5, 10, 0.07, 7, '#6b4c33', {seg: 6}); polyStrips([[0, 0], [0, -1.6], [2.4, -0.8]].map(p => [p[0] * s, p[1] + 6.6]), 6, 10, s > 0 ? '#d9442a' : '#f2c14a', {th: 0.04, flut: 0.18, ph: s}); }
});

// ===== jam / waktu =====
reg('jam', 'jam dinding besar: jarum menit berputar dan busur hijau menunjukkan 45 menit. param: sz', (o) => {
  const sz = o.sz || 3, f = sm(TS / 5);
  cyl(0, 0, 0, sz, 0.3, '#f4f1e6', {rx: Math.PI / 2, seg: 30}); cyl(0, 0, -0.0, sz * 1.08, 0.2, '#2b3a55', {rx: Math.PI / 2, seg: 30});
  for (let k = 0; k < 60; k++) { const a = k / 60 * 6.2832, on = k < 45 * f; box(Math.sin(a) * sz * 0.86, Math.cos(a) * sz * 0.86, 0.2, 0.1, k % 5 === 0 ? 0.42 : 0.2, 0.06, on ? '#2f8f6a' : '#9a9a9a', {rz: -a, e: on ? 0.4 : 0}); }
  pushM(T(0, 0, 0.25)); pushM(RZ(-f * 4.712)); box(0, sz * 0.38, 0, 0.12, sz * 0.78, 0.08, '#13151a'); popM(); popM();
  pushM(T(0, 0, 0.3)); pushM(RZ(-f * 4.712 / 12)); box(0, sz * 0.26, 0, 0.18, sz * 0.52, 0.08, '#13151a'); popM(); popM();
  sph(0, 0, 0.32, 0.16, '#d9442a', {seg: 8});
});

// ===== Whoosh: detail bogie =====
reg('bogie_detail', 'bogie kereta cepat terurai: rangka H, dua poros dan roda berputar, pegas primer, pegas udara sekunder, motor traksi & gearbox, peredam getar. jangkar: rangka, pegas, motor, as, damper', (o) => {
  const ex = 0.5 + 0.5 * sm(bounce3(TT * 0.12)), wr = 0.9;
  for (const s of [-1, 1]) box(0, 1.35, s * 1.9, 5.6, 0.45, 0.5, '#3b4553'); for (const x of [-1.6, 1.6]) box(x, 1.35, 0, 0.5, 0.45, 3.8, '#3b4553');
  anc('rangka', [2.8, 1.35, 2.2]);
  for (const x of [-2.2, 2.2]) { cyl(x, wr, 0, 0.1, 4.4, '#8e959c', {rx: Math.PI / 2, seg: 8}); for (const s of [-1, 1]) { pushM(T(x, wr, s * 1.4)); pushM(RZ(-AN.wa * 1.0 * 0 - TT * 5)); cyl(0, 0, 0, wr, 0.3, '#5b6470', {rx: Math.PI / 2, seg: 20}); for (let k = 0; k < 4; k++) box(0, 0, s * 0.18, 0.12, wr * 1.8, 0.04, '#c8ccd0', {rz: k * 0.785}); popM(); popM(); } anc('as', [x, wr, 2.2]); }
  for (const x of [-2.2, 2.2]) for (const s of [-1, 1]) { const y = 1.9 + ex * 0.0; cyl(x, 1.65, s * 1.9, 0.26, 0.5 + ex * 0.0, '#e0a020', {seg: 10}); for (let k = 0; k < 4; k++) cyl(x, 1.45 + k * 0.1, s * 1.9, 0.3, 0.05, '#b8861b', {seg: 10}); }
  anc('pegas', [2.2, 1.7, 2.2]);
  for (const s of [-1, 1]) { const y0 = 2.9 + ex * 1.8; cyl(0, y0, s * 1.2, 0.8, 0.9, '#2a2d31', {seg: 16}); for (let k = 0; k < 3; k++) cyl(0, y0 - 0.3 + k * 0.3, s * 1.2, 0.84, 0.06, '#444a50', {seg: 16}); }
  cyl(-0.4, 2.5 + ex * 0.8, 0, 0.6, 1.8, '#2f66c9', {rx: Math.PI / 2, seg: 16}); box(0.9, 2.1 + ex * 0.8, 0, 1.0, 0.8, 1.0, '#7a8590'); anc('motor', [-0.6, 3.0 + ex * 0.8, 0.9]);
  for (const x of [-1.0, 1.0]) cyl(x, 2.4, 2.1, 0.09, 1.2, '#d9442a', {rz: 0.3, seg: 6}); anc('damper', [1.0, 2.5, 2.2]);
  for (let k = 0; k < 4; k++) { const f = fr(TT * 0.8 + k / 4); for (const dz of [-1, 1]) { box(-4.4 - f * 3.4, 1.3 + k * 0.4, dz * 2.4, 0.12, 0.12, 1.1 * (1 - f), '#8fd0f5', {ns: 1, e: 0.6}); } }
});

// ===== iklim tropis: matahari, panas, hujan, kelembapan =====
reg('iklim', 'tanda iklim tropis di atas kereta: matahari besar bersinar, gelombang panas, hujan deras, termometer naik, tetes kelembapan. jangkar: matahari, termometer, hujan', (o) => {
  const t = sm(TS / 2.4);
  sph(-14, 16, -14, 3.0, '#ffcf3a', {seg: 14, e: 1, ns: 1}); for (let k = 0; k < 12; k++) { const a = k / 12 * 6.2832 + TT * 0.3; box(-14 + Math.cos(a) * 5.0, 16 + Math.sin(a) * 5.0, -14, 0.35, 1.7, 0.35, '#ffcf3a', {rz: a - 1.5708, e: 1, ns: 1}); }
  anc('matahari', [-14, 16, -14]);
  for (let k = 0; k < 7; k++) { const f = fr(TT * 0.5 + k / 7); for (let j = 0; j < 5; j++) box(-10 + k * 3.2 + Math.sin(f * 14 + j) * 0.3, 1.0 + f * 5 + j * 0.0, -6, 0.16, 0.6, 0.16, '#f5ae4a', {ns: 1, e: 0.7}); }
  for (let k = 0; k < 24; k++) { const f = fr(TT * 1.0 + k / 24); box(-12 + (k * 1.3) % 28, 18 - f * 18, 6 + (k % 5) * 1.5, 0.07, 1.1, 0.07, '#8fd0f5', {ns: 1, e: 0.6}); }
  anc('hujan', [8, 12, 8]);
  box(16, 4.2, -4, 0.9, 8.4, 0.9, '#f4f4f4'); box(16, 0.8 + t * 6.2, -4, 0.5, 1.6 + t * 6.2, 0.5, '#d9442a', {ns: 1}); sph(16, 0.4, -4, 0.9, '#d9442a', {seg: 12}); anc('termometer', [16, 8, -4]);
  for (let k = 0; k < 4; k++) { const f = fr(TT * 0.4 + k / 4); sph(18.2 + (k % 2) * 0.9, 7 - f * 5, -4, 0.28, '#3f8ec9', {seg: 8, ns: 1}); }
});

// ===== timbunan jalur kereta (irisan) =====
reg('timbunan', 'irisan timbunan jalur kereta cepat: tanah dasar, lapisan tanah padat bertahap, lapisan penopang, balas kerikil, rel; lereng miring berumput. sumbu x. jangkar: timbunan, balas, tanahdasar', (o) => {
  const H = 4.2, L = o.len || 40, W0 = 22, W1 = 9, ang = Math.atan2(H, (W0 - W1) / 2), sl = Math.hypot(H, (W0 - W1) / 2);
  box(0, -0.4, 0, L, 0.8, W0 + 4, '#6b5a43'); anc('tanahdasar', [-L / 2, -0.2, W0 / 2 + 1]);
  for (let i = 0; i < 4; i++) { const w = W0 - (W0 - W1) * i / 4 - (W0 - W1) / 8, y = 0.55 + i * 1.0; box(0, y, 0, L, 0.98, w, ['#8b6f4a', '#9a7d54', '#a98a5d', '#b89a6a'][i]); }
  for (const s of [-1, 1]) { pushM(T(0, H / 2, s * (W0 + W1) / 4)); pushM(RX(s * -ang + 0)); box(0, 0, 0, L + 0.5, 0.18, sl, '#5f9a48'); popM(); popM(); }
  box(0, H + 0.12, 0, L, 0.3, W1 + 0.6, '#9a9690'); anc('balas', [-L / 2, H + 0.3, 0]);
  for (let k = 0; k < Math.floor(L / 0.7); k++) box(-L / 2 + k * 0.7 + 0.35, H + 0.34, 0, 0.26, 0.14, 2.6, '#cfc9bd');
  for (const s of [-0.72, 0.72]) box(0, H + 0.48, s, L, 0.2, 0.12, '#4b4f55');
  anc('timbunan', [-L / 2, H * 0.55, W0 * 0.3]);
});

// ===== Borobudur: pancuran makara (dekat) =====
reg('makara', 'pancuran makara batu andesit: kepala dengan mata besar, rahang & gigi, belalai melengkung ke atas dan menggulung; air deras keluar dari mulut. jangkar: makara, air', (o) => {
  const dk = '#2a2622';
  box(-0.4, 1.0, 0, 3.8, 2.0, 2.4, STONE3[0]); box(-0.4, 2.08, 0, 3.4, 0.2, 2.2, STONE3[1]);
  box(1.9, 1.3, 0, 1.6, 1.3, 2.0, STONE3[2]); box(2.5, 0.7, 0, 1.4, 0.5, 1.6, dk); box(1.9, 0.62, 0, 0.9, 0.12, 1.7, STONE3[1]);
  for (let k = 0; k < 5; k++) { box(1.6 + k * 0.28, 0.95, 0.75 - k * 0.38, 0.14, 0.3, 0.14, '#f2eee4'); }
  const cx = -0.4, cy = 3.9, N = 18;
  for (let k = 0; k < N; k++) { const t = k / (N - 1), th = -Math.PI / 2 - t * 4.2, r = 1.7 - 1.15 * t; pushM(T(cx + 1.7 + r * Math.cos(th) - 1.7 * 0 + 0.0, cy + r * Math.sin(th), 0)); pushM(RZ(th + Math.PI)); box(0, 0, 0, 0.5, 0.7 - 0.35 * t, 1.9 - 1.0 * t, STONE3[k % 3]); popM(); popM(); }
  for (const s of [-1, 1]) { sph(0.7, 2.7, s * 1.22, 0.42, '#f2eee4', {seg: 10}); sph(0.82, 2.72, s * 1.5, 0.2, '#141414', {seg: 8}); box(0.7, 3.25, s * 1.2, 0.9, 0.18, 0.18, STONE3[1]); for (let k = 0; k < 3; k++) sph(-1.4 + k * 0.5, 2.4 + (k % 2) * 0.3, s * 1.3, 0.3, STONE3[(k + 1) % 3], {seg: 6}); }
  for (let k = 0; k < 16; k++) { const f = fr(TT * 0.9 + k / 16); sph(3.1 + f * 3.0, 0.7 - 6.0 * f * f, (Math.sin(k * 2.1)) * 0.2, 0.22 - f * 0.07, '#8fd0f5', {seg: 6, e: 0.6, ns: 1}); }
  box(4.5, 0.4, 0, 2.6, 0.12, 0.8, '#cfe8f5', {e: 0.5, ns: 1});
  anc('makara', [0.6, 4.2, 1.4]); anc('air', [4.8, 0.2, 0.6]);
});
