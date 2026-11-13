// ---------- Pustaka komponen SIPIL / TEROWONGAN (TBM) ----------
// Poros mesin = sumbu x (maju ke +x). Radial: [0,cos,sin]. Dibangun detail: kepala pemotong + disc cutter menggelinding,
// perisai tembus pandang berisi motor/dongkrak, lengan erector, cincin segmen beton, ban berjalan, batuan berlapis.
const ROCKS = ['#8f8a80', '#7d786f', '#a29b8d', '#6f6b64'];
const hold = () => sm(Math.min(1, fr(TT / 5) / 0.7)); // siklus pemasangan segmen 5 dtk

function discAt(c, ax, R, th, a, col) { // cakram baja (disc cutter) pusat c, sumbu ax, jari-jari R, tebal th, sudut gelinding a
  const ref = Math.abs(ax[1]) < 0.9 ? [0, 1, 0] : [1, 0, 0], u = nrm(cross(ax, ref)), v = cross(ax, u), h = th / 2;
  const Pt = k => [c[0] + ax[0] * k, c[1] + ax[1] * k, c[2] + ax[2] * k];
  link(Pt(-h), Pt(h), R * 0.8, col || '#aeb8c0', {seg: 20});
  link(Pt(-h * 0.9), Pt(h * 0.9), R, '#e1e7ea', {seg: 20});
  link(Pt(-h * 1.3), Pt(h * 1.3), R * 0.3, '#4c555d', {seg: 10});
  for (let k = 0; k < 3; k++) {
    const ang = a + k * 2.094, d = [u[0] * Math.cos(ang) + v[0] * Math.sin(ang), u[1] * Math.cos(ang) + v[1] * Math.sin(ang), u[2] * Math.cos(ang) + v[2] * Math.sin(ang)];
    for (const s of [-1, 1]) { const q = Pt(s * (h + 0.012)); link([q[0] + d[0] * R * 0.38, q[1] + d[1] * R * 0.38, q[2] + d[2] * R * 0.38], [q[0] + d[0] * R * 0.74, q[1] + d[1] * R * 0.74, q[2] + d[2] * R * 0.74], 0.03, '#ff9a2e', {ns: 1, seg: 6}); }
  }
}

function ringBoxes(x, R, w, th, n, col, o = {}) { // cincin dari n balok mengelilingi sumbu x
  const arc = 2 * Math.PI * R / n * 1.04;
  for (let i = 0; i < n; i++) { pushM(RX(i * 2 * Math.PI / n)); box(x, R, 0, w, th, arc, Array.isArray(col) ? col[i % col.length] : col, o); popM(); }
}

function drawRing(Rc, th, w, n, o = {}) { // cincin segmen beton: n segmen + 1 segmen kunci (di atas). o.skip = indeks segmen dilewati, o.ex = peledakan 0..1
  const ks = 0.38, sp = (2 * Math.PI - ks) / n, ex = o.ex || 0, cols = ['#c8cdd0', '#b4babe'];
  const spans = [{a0: -ks / 2, a1: ks / 2, key: true, k: -1}]; for (let k = 0; k < n; k++) spans.push({a0: ks / 2 + k * sp, a1: ks / 2 + (k + 1) * sp, key: false, k});
  spans.forEach(s => {
    if (s.k === o.skip && !s.key) return;
    const m = Math.max(2, Math.ceil((s.a1 - s.a0) / 0.14)), d = (s.a1 - s.a0) / m, mid = (s.a0 + s.a1) / 2, off = ex * (s.key ? 2.2 : 1.6), col = s.key ? '#e08a2c' : cols[s.k % 2];
    for (let i = 0; i < m; i++) { const am = s.a0 + (i + 0.5) * d; pushM(RX(am)); box(0, Rc + off, 0, w, th, Rc * d * 1.05, col); popM(); }
    pushM(RX(mid)); for (const e of [s.a0, s.a1]) { pushM(RX(e - mid)); sph(0, Rc + off - th * 0.5 - 0.01, 0, 0.07, '#2b2f34', {seg: 6, ns: 1}); sph(0, Rc + off + th * 0.5 + 0.01, 0, 0.07, '#2b2f34', {seg: 6, ns: 1}); popM(); } popM();
  });
}

// ----- komponen -----
reg('tbm_head', 'kepala pemotong TBM batu keras: pelat bulat dengan jari-jari baja dan puluhan disc cutter yang menggelinding; berputar pelan. Sumbu x, muka ke +x. param: rad(3.2), w(0.5), n(24). jangkar: face, rim, disc', (o) => {
  const R = o.rad || 3.2, w = o.w == null ? 0.5 : o.w, n = o.n || 32, a0 = TT * w;
  anc('face', [0.7, 0, 0]); anc('rim', [0.3, R * 0.96, 0]);
  pushM(RX(a0));
  link([-0.9, 0, 0], [0.15, 0, 0], R * 0.95, '#34425a', {seg: 40}); link([0.15, 0, 0], [0.3, 0, 0], R * 0.99, '#4d6285', {seg: 40});
  ringBoxes(-0.1, R - 0.15, 0.7, 0.3, 28, '#2b3850');
  for (let k = 0; k < 6; k++) { pushM(RX(k * Math.PI / 3)); box(0.4, R * 0.5, 0, 0.16, R * 0.92, 0.36, '#2a3a52'); popM(); pushM(RX(k * Math.PI / 3 + Math.PI / 6)); box(0.33, R * 0.78, 0, 0.12, 0.7, 0.9, '#0d1118'); popM(); }
  link([0.3, 0, 0], [0.75, 0, 0], 0.95, '#2a3a52', {seg: 20});
  for (let j = 0; j < n; j++) {
    const r = 0.95 + j * (R - 1.45) / (n - 1), th = j * 2.39996, dr = 0.3;
    pushM(RX(th)); box(0.4, r, 0, 0.14, 0.44, 0.34, '#2a3a52');
    discAt([0.52, r, 0], [0, 0, 1], dr, 0.16, -(a0 + th) * 0 - TT * w * r / dr, '#aeb8c0');
    if (j === 0) anc('disc', [0.62, r, 0]);
    popM();
  }
  popM();
});

reg('tbm_shield', 'perisai baja TBM tembus pandang (berisi dinding sekat, motor penggerak biru, 14 dongkrak hidrolik yang memanjang-memendek). Sumbu x, ujung depan x=-0.95 ke belakang. param: rad(3.2), len(7), jack(0-1 override). jangkar: shell, motor, jack, bulkhead', (o) => {
  const R = o.rad || 3.2, L = o.len || 7, x0 = -0.95, x1 = x0 - L, c = fr(TT * 0.15), e0 = c < 0.6 ? c / 0.6 : 1 - (c - 0.6) / 0.4, ex = o.jack != null ? o.jack : sm(e0), Rj = R - 0.4;
  anc('shell', [x0 - L * 0.5, R * 1.0, 0]); anc('bulkhead', [-1.35, R * 0.55, 0]); anc('motor', [-2.4, 1.7, 0]); anc('jack', [x1 + 1.6, Rj, 0]);
  link([x0, 0, 0], [x1, 0, 0], R * 1.02, '#8fa6c0', {glass: true, seg: 36});
  ringBoxes(x0 - 0.2, R * 1.02 - 0.12, 0.4, 0.28, 32, '#c9552e'); ringBoxes(x1 + 0.3, R * 1.02 - 0.12, 0.5, 0.28, 32, '#c9552e');
  link([-1.25, 0, 0], [-1.4, 0, 0], R * 0.97, '#34425a', {seg: 36}); link([-1.4, 0, 0], [-1.85, 0, 0], 1.15, '#9aa3ab', {seg: 24});
  for (let k = 0; k < 6; k++) { pushM(RX(k * Math.PI / 3)); link([-1.45, 1.75, 0], [-3.3, 1.75, 0], 0.5, '#2f66c9', {seg: 14}); link([-3.3, 1.75, 0], [-3.5, 1.75, 0], 0.52, '#1f4a9a', {seg: 14}); popM(); }
  for (let k = 0; k < 14; k++) {
    pushM(RX(k * 2 * Math.PI / 14 + 0.1)); const xr = x1 + 1.2 - ex * 1.1;
    link([x1 + 3.0, Rj, 0], [x1 + 1.2, Rj, 0], 0.17, '#e8eef0', {seg: 10}); link([x1 + 1.2, Rj, 0], [xr, Rj, 0], 0.1, '#b7c0c6', {seg: 8}); box(xr - 0.05, Rj, 0, 0.1, 0.3, 0.5, '#3f4c55');
    popM();
  }
});

reg('erector', 'lengan robot erector merah di belakang perisai: berputar, memanjang, memegang segmen beton. Sumbu x. param: rad(2.5), ang(rad), tip(panjang lengan). jangkar: arm, hub', (o) => {
  const R = o.rad || 2.5, a = o.ang != null ? o.ang : TT * 0.6, tip = o.tip != null ? o.tip : 1.7 + 0.8 * Math.sin(TT * 1.3);
  anc('hub', [0, 0, 0]); ringBoxes(0, R + 0.05, 0.4, 0.14, 24, '#5d6670');
  link([-0.45, 0, 0], [0.45, 0, 0], 0.42, '#7b838e', {seg: 16});
  pushM(RX(a)); link([0, 0.3, 0], [0, 1.3, 0], 0.22, '#d9433a', {seg: 10}); link([0, 1.3, 0], [0, tip, 0], 0.15, '#ff8c80', {seg: 8}); box(0, tip + 0.1, 0, 0.9, 0.2, 1.2, '#d9433a'); anc('arm', [0, (1.3 + tip) / 2, 0]); popM();
});

reg('seg_ring', 'satu cincin terowongan dari segmen beton prefabrikasi (enam segmen abu + satu segmen kunci oranye di atas) berbaut. Sumbu x. param: rad(3.0 radius luar), th(0.45), w(1.4), n(6), ex (peledakan 0-1 atau [t0,t1] waktu adegan). jangkar: key, seg, ring', (o) => {
  const Rc = (o.rad || 3.0) - (o.th || 0.45) / 2, th = o.th || 0.45; let ex = 0; if (Array.isArray(o.ex)) ex = sm((TS - o.ex[0]) / Math.max(0.3, o.ex[1] - o.ex[0])); else if (o.ex) ex = o.ex;
  drawRing(Rc, th, o.w || 1.4, o.n || 6, {ex});
  anc('key', [0, Rc + th / 2 + ex * 2.2, 0]); pushM(RX(2.6)); anc('seg', [0, Rc + th / 2 + ex * 1.6, 0]); popM(); anc('ring', [0, -(Rc + th / 2), 0]);
});

reg('ring_build', 'pemasangan segmen: cincin beton hampir lengkap, satu segmen kuning diangkat erector merah dari tengah ke dinding (siklus 5 dtk). Sumbu x. param: rad(3.0), w(1.4), idx(2). jangkar: placing, arm, ring', (o) => {
  const Ro = o.rad || 3.0, th = 0.45, Rc = Ro - th / 2, w = o.w || 1.4, n = 6, idx = o.idx == null ? 2 : o.idx, ks = 0.38, sp = (2 * Math.PI - ks) / n, u = hold();
  drawRing(Rc, th, w, n, {skip: idx});
  const a0 = ks / 2 + idx * sp, a1 = a0 + sp, mid = (a0 + a1) / 2, roff = -(1 - u) * 1.9, xoff = -(1 - u) * 1.5;
  const m = Math.ceil(sp / 0.14), d = sp / m;
  for (let i = 0; i < m; i++) { pushM(RX(a0 + (i + 0.5) * d)); box(xoff, Rc + roff, 0, w, th, Rc * d * 1.05, '#f2c21c'); popM(); }
  pushM(RX(mid)); anc('placing', [xoff, Rc + roff + th / 2, 0]); popM();
  pushM(T(-w / 2 - 1.1, 0, 0)); COMP.erector({rad: Ro - 0.3, ang: mid, tip: Rc + roff - 0.25}, 'eb'); popM(); anc('ring', [0, -Ro, 0]);
  pushM(RX(mid)); anc('arm', [-w / 2 - 1.1, (1.3 + Rc + roff - 0.25) / 2, 0]); popM();
});

reg('lining', 'lapisan terowongan jadi di belakang perisai: deretan cincin segmen beton + lapisan grout oranye di sela, lantai & rel. Sumbu x, maju ke -x. param: n(5), rad(3.0), w(1.4), x0(awal). jangkar: ring, grout', (o) => {
  const n = o.n || 5, Ro = o.rad || 3.0, w = o.w || 1.4, th = 0.45, Rc = Ro - th / 2, gp = w + 0.03;
  for (let i = 0; i < n; i++) {
    pushM(T(-i * gp - w / 2, 0, 0)); drawRing(Rc, th, w, 6);
    if (i >= 1) ringBoxes(0, Ro + 0.13, w, 0.26, 28, '#d98a3b', {ns: 1});
    popM();
  }
  const Lg = n * gp; box(-Lg / 2, -1.75, 0, Lg, 0.25, 4.2, '#6f747a'); for (const z of [-0.9, 0.9]) box(-Lg / 2, -1.58, z, Lg, 0.1, 0.12, '#9aa3ab');
  anc('ring', [-w / 2, Ro, 0]); anc('grout', [-gp * 1.5, Ro + 0.13, 0]);
  for (let k = 0; k < 3; k++) { pushM(RX(k * 2.1 + 0.9)); const pts = [[w / 2 + 0.2, Ro + 0.9, 0], [w / 2 - 0.2, Ro + 0.5, 0], [w / 2 - 0.3, Ro + 0.13, 0]]; path(pts, 0.07, '#7b838e'); for (let q = 0; q < 4; q++) sph(...along(pts, fr(q / 4 + TT * 0.5)), 0.11, '#ffb347', {e: 1, ns: 1, seg: 8}); popM(); }
});

reg('conveyor', 'ban berjalan pengangkut serpihan batu keluar dari terowongan, serpihan batu bergerak di atasnya. Memanjang ke -x. param: len(10), w(kecepatan 0.45), width(1.1). jangkar: belt, start', (o) => {
  const Ln = o.len || 10, sp = o.w == null ? 0.45 : o.w, Wd = o.width || 1.1;
  box(-Ln / 2, 0, 0, Ln, 0.12, Wd + 0.2, '#3f4c55'); for (const s of [-1, 1]) box(-Ln / 2, 0.2, s * (Wd / 2 + 0.1), Ln, 0.3, 0.1, '#5d6670');
  box(-Ln / 2, 0.1, 0, Ln, 0.05, Wd, '#23282d');
  const off = fr(TT * sp / 0.8) * 0.8; for (let x = off; x < Ln; x += 0.8) box(-x, 0.128, 0, 0.07, 0.01, Wd, '#3a4048', {ns: 1});
  const n = Math.round(Ln * 1.1); for (let i = 0; i < n; i++) { const x = -fr(i / n + TT * sp / Ln) * Ln, s = 0.16 + 0.2 * (((i * 53) % 10) / 10); box(x, 0.125 + s / 2, (((i * 37) % 7) - 3) * Wd * 0.12, s, s * 0.8, s * 1.1, ROCKS[i % 4], {ry: i, rz: 0.4 * (i % 3)}); }
  anc('belt', [-Ln * 0.45, 0.5, 0]); anc('start', [-0.3, 0.4, 0]);
});

reg('disc_cutter', 'satu disc cutter besar (cakram baja bermata) bertumpu pada dudukan, berputar menggelinding. Sumbu cakram z. param: rad(1.0), th(0.5), w(rad/dtk 2). jangkar: disc, edge', (o) => {
  const R = o.rad || 1.0, th = o.th || 0.5, w = o.w == null ? 2 : o.w;
  box(0, R + 0.9, 0, 1.8, 0.5, th * 2.4, '#2a3a52'); box(0, R + 0.5, th * 0.65, 0.5, 0.9, 0.14, '#4d6285'); box(0, R + 0.5, -th * 0.65, 0.5, 0.9, 0.14, '#4d6285');
  discAt([0, R, 0], [0, 0, 1], R, th, -TT * w, '#aeb8c0'); anc('disc', [0, R, th]); anc('edge', [0, 0, 0]);
});

reg('cut_demo', 'demonstrasi pemecahan batu: dua disc cutter menggelinding di permukaan batu, meninggalkan dua alur; batu di antaranya retak dan terlepas jadi serpihan, panah merah = gaya tekan. Siklus 5 dtk. param: rad(1.0). jangkar: disc, groove, chip, force', (o) => {
  const R = o.rad || 1.0, tt = fr(TT * 0.2) * 5, xc = -2.5 + tt, pen = 0.12, zs = [-0.95, 0.95];
  box(0, -1.3, 0, 8.2, 2.6, 4.6, '#8b857a'); for (let i = 0; i < 6; i++) box(-3.4 + i * 1.3, -2.55, 0, 1.2, 0.35, 4.62, ROCKS[i % 4], {ns: 1});
  for (const z of zs) { discAt([xc, R - pen, z], [0, 0, 1], R, 0.3, -xc / R, '#aeb8c0'); box(xc, R + 0.6, z, 0.5, 0.35, 0.5, '#2a3a52'); box((xc - 2.6) / 2, 0.005, z, xc + 2.6 + 1.0, 0.012, 0.2, '#3d3a35', {ns: 1}); }
  for (let i = 0; i < 9; i++) {
    const xi = -2.4 + i * 0.6, dt = tt - (xi + 2.5) - 0.1;
    if (dt < 0) { box(xi, -0.02, 0, 0.58, 0.04, 1.5, '#b3ac9f', {ns: 1}); continue; }
    if (dt > 2.4) { box(xi, -0.14, 0, 0.58, 0.04, 1.5, '#5b574f', {ns: 1}); continue; }
    const up = sm(dt / 0.5), fall = sm((dt - 1.2) / 1.2), sc = 1 - 0.8 * fall;
    box(xi, -0.14, 0, 0.58, 0.04, 1.5, '#5b574f', {ns: 1});
    box(xi, 0.02 + 0.3 * up - 1.2 * fall, (i % 2 ? 1 : -1) * 0.4 * up * (1 + fall), 0.56 * sc, 0.14 * sc, 1.4 * sc, '#cfc8ba', {rz: (i % 2 ? 1 : -1) * 0.5 * up, rx: 0.3 * up * (i % 3 - 1)});
    if (dt < 1.0) { for (const s of [-1, 1]) link([xi, -0.1, s * 0.82], [xi, -0.01, s * 0.15], 0.018, '#2b2724', {seg: 4, ns: 1}); }
  }
  link([xc, R * 2 + 2.6, 0], [xc, R * 2 + 0.95, 0], 0.13, '#e8403a', {seg: 8}); link([xc, R * 2 + 0.95, 0], [xc, R * 2 + 0.3, 0], 0.38, '#e8403a', {rt: 0, rb: 1, seg: 8});
  anc('disc', [xc, R - pen, zs[1] + 0.2]); anc('groove', [-1.5, 0.02, zs[0]]); anc('chip', [-1.2 + 0, 0.15, 0]); anc('force', [xc, R * 2 + 2.0, 0]);
});

reg('rockmass', 'penampang tanah/batu terpotong: dinding belakang & lantai berlapis, langit-langit, dan sumbat batu padat di depan muka terowongan (x=face). Memanjang ke -x. param: rad(3.4), face(0.5), len(26), mountain(false). jangkar: face', (o) => {
  const Rb = o.rad || 3.4, xf = o.face == null ? 0.5 : o.face, Ln = o.len || 26, zb = -(Rb + 0.4), xm = xf - Ln / 2 + 7, XL = Ln + 14;
  const bands = [[-9.5, -6.6, '#6e6354'], [-6.6, -3.5, '#8c7a63'], [-3.5, 0.6, '#9a8b73'], [0.6, 3.8, '#85766a'], [3.8, 7.4, '#7a6b58']];
  bands.forEach(b => box(xm, (b[0] + b[1]) / 2, zb - 1.5, XL, b[1] - b[0], 3, b[2], {ns: 1}));
  box(xm, -3.45 - 1.2, (zb + 0) / 2, XL, 2.4, -zb, '#7c6f5e', {ns: 1}); box(xm, -3.45 - 2.5, (zb + 0) / 2, XL, 0.1, -zb + 0.02, '#5b5143', {ns: 1});
  box(xm, 3.7 + 1.5, (zb - 0.5) / 2, XL, 3, -zb - 0.5, '#85766a', {ns: 1});
  const pl = [[-3.5 - 3.3, -3.5, '#7c6f5e'], [-3.5, 0.6, '#9a8b73'], [0.6, 3.7, '#85766a'], [3.7, 7.2, '#7a6b58']];
  pl.forEach(b => box(xf + 7, (b[0] + b[1]) / 2, zb / 2, 14, b[1] - b[0], -zb, b[2], {ns: 1}));
  for (let i = 0; i < 16; i++) { const R = rng(i + 4); box(xf + 0.6 + R() * 12, -3 + R() * 8, -0.02, 0.5 + R(), 0.35 + R() * 0.5, 0.05, ROCKS[i % 4], {ns: 1}); }
  if (o.mountain) { cyl(xm + 2, -9.5 + 11, -26, 15, 22, '#6d8a5e', {rt: 0.04, rb: 1, seg: 14, ns: 1}); cyl(xm + 2, -9.5 + 19, -26, 3.6, 6, '#eef2f4', {rt: 0.02, rb: 1, seg: 14, ns: 1}); cyl(xm - 14, -9.5 + 7, -22, 10, 14, '#5f7c52', {rt: 0.04, rb: 1, seg: 12, ns: 1}); }
  anc('face', [xf, 0, 0.05]);
});

reg('tbm', 'mesin bor terowongan lengkap (TBM): kepala pemotong + perisai tembus pandang + erector + ban berjalan + 3 cincin beton di belakang, bergerak maju pelan. Sumbu x. param: rad(3.2), len(7), w(0.5). jangkar: face, disc, rim, shell, motor, jack, arm, belt, ring', (o) => {
  const L = o.len || 7, x1 = -0.95 - L;
  COMP.tbm_head({rad: o.rad, w: o.w}, 'h'); COMP.tbm_shield({rad: o.rad, len: L}, 's');
  pushM(T(x1 + 0.4, 0, 0)); COMP.erector({}, 'e'); popM();
  pushM(T(-1.45, -2.3, 0)); COMP.conveyor({len: L + 7}, 'c'); popM();
  pushM(T(x1, 0, 0)); COMP.lining({n: 3}, 'l'); popM();
});
