// ---------- Direktur adegan: membaca SPEC (JSON) + timing.js, merender frame ----------
const TM = window.TIMING, SS = TM.sent_spans, FPS = 30, TOTAL = TM.dur + 0.8, SPEC = window.SPEC || {scenes: []};
const sm = u => { u = Math.max(0, Math.min(1, u)); return u * u * (3 - 2 * u); };
const lp = (a, b, u) => a.map((v, i) => v + (b[i] - v) * u);
const lpn = (a, b, u) => a + (b - a) * u;
const orb = (c, r, a0, a1, h0, h1, u) => { const a = (a0 + (a1 - a0) * u) * Math.PI / 180, h = h0 + (h1 - h0) * u; return [c[0] + r * Math.sin(a), c[1] + h, c[2] + r * Math.cos(a)]; };
const sentT = i => SS[Math.max(0, Math.min(SS.length - 1, i))][0];
const tabs = (x, s0) => typeof x === 'number' ? s0 + x : (x && x.sent != null ? sentT(x.sent) + (x.off || 0) : s0);

// ----- timing kata / subtitle -----
const PH = []; (function () {
  const bySent = {}; TM.words.forEach((w, i) => { (bySent[w.si] = bySent[w.si] || []).push(i); });
  Object.keys(bySent).forEach(k => {
    const idx = bySent[k], segs = [[]]; idx.forEach(i => { segs[segs.length - 1].push(i); if (/[,:]$/.test(TM.words[i].w) && i !== idx[idx.length - 1]) segs.push([]); });
    segs.forEach(sg => { const n = Math.ceil(sg.length / 6), per = Math.ceil(sg.length / n); for (let j = 0; j < sg.length; j += per) PH.push(sg.slice(j, j + per)); });
  });
})();
const T0 = i => TM.words[i].start, T1 = i => TM.words[i].end;
function phraseAt(t) {
  let cur = null; for (let p = 0; p < PH.length; p++) { const a = T0(PH[p][0]) - 0.05, nxt = PH[p + 1] ? T0(PH[p + 1][0]) - 0.05 : 1e9, end = Math.min(nxt, T1(PH[p][PH[p].length - 1]) + 0.35); if (t >= a && t < end) { cur = PH[p]; break; } }
  if (!cur) return null; let act = 0; for (let j = 0; j < cur.length; j++) if (t >= T0(cur[j])) act = j; return {words: cur.map(i => TM.words[i].w), act};
}
const mouthAt = t => { const f = t * FPS, i = Math.floor(f), a = TM.mouth[Math.min(i, TM.mouth.length - 1)] || 0, b = TM.mouth[Math.min(i + 1, TM.mouth.length - 1)] || 0; return a + (b - a) * (f - i); };

// ----- lingkungan -----
const flat = (col, y = 0) => box(0, y - 0.25, 0, 600, 0.5, 600, col, {ns: 1});
const ENV = {
  outdoor: {sky: ['#6fa8dc', '#d9ecf6'], fog: [0.80, 0.88, 0.94], fn: 28, ff: 190, shadowY: 0, build(o) { flat(P.grass); const R = rng(21); for (let i = 0; i < 70; i++) box(-90 + R() * 180, 0.01, (R() < .5 ? -1 : 1) * (6 + R() * 60), 6 + R() * 22, 0.02, 5 + R() * 16, ['#6a9648', '#78a251', '#557f41'][i % 3], {ns: 1}); scenery(o.seed || 7, {poles: false, houses: o.houses !== false}); }},
  rail: {sky: ['#6fa8dc', '#d9ecf6'], fog: [0.80, 0.88, 0.94], fn: 28, ff: 190, shadowY: 0, build() { groundBase(); scenery(7); }},
  road: {sky: ['#7fb2e0', '#dcedf6'], fog: [0.82, 0.9, 0.95], fn: 28, ff: 190, shadowY: 0, build() { flat(P.grass); box(0, -0.06, 0, 600, 0.1, 6, '#4a4f55', {ns: 1}); const g = ((AN.goff % 5) + 5) % 5; for (let x = -80 + g - 5; x < 80; x += 5) box(x, 0.0, 0, 2.2, 0.03, 0.18, '#f4f0d0', {ns: 1}); scenery(9, {poles: false}); }},
  room: {sky: ['#f3ead8', '#efe2c8'], clouds: false, fog: [0.94, 0.9, 0.82], fn: 60, ff: 260, shadowY: 0, build() { box(0, -0.1, 0, 60, 0.2, 40, '#c9a77c', {ns: 1}); box(0, 7, -9, 60, 14, 0.3, '#efe6d6', {ns: 1}); box(0, 0.3, -8.8, 60, 0.6, 0.1, '#b89a72', {ns: 1}); box(-8, 5, -8.8, 5, 4, 0.08, '#bfe0f2', {ns: 1}); box(-8, 5, -8.75, 0.15, 4.1, 0.1, '#ffffff', {ns: 1}); box(-8, 5, -8.75, 5.1, 0.15, 0.1, '#ffffff', {ns: 1}); }},
  stage: {sky: ['#d9ece4', '#f3efe0'], clouds: false, fog: [0.9, 0.94, 0.92], fn: 60, ff: 240, shadowY: 0, build() { cyl(0, -0.06, 0, 9, 0.12, '#dfe6e3', {seg: 48, ns: 1}); cyl(0, -0.16, 0, 9.4, 0.1, '#9fb0aa', {seg: 48, ns: 1}); }},
  studio: {sky: ['#e8eef2', '#f6f3ea'], clouds: false, fog: [0.93, 0.95, 0.95], fn: 60, ff: 260, shadowY: 0, build() { flat('#e9eceb'); }},
  sea: {sky: ['#7fb2e0', '#e6f2f7'], fog: [0.8, 0.9, 0.95], fn: 30, ff: 200, shadowY: null, build() { box(0, -0.4, 0, 600, 0.8, 600, '#3d86b8', {ns: 1}); for (let i = 0; i < 40; i++) { const R = rng(i + 3); box(-60 + R() * 120, 0.02 + 0.03 * Math.sin(TT * 1.3 + i), -40 + R() * 90, 3 + R() * 4, 0.04, 0.3, '#cfe8f5', {ns: 1}); } }},
  space: {sky: ['#05060f', '#1a1f3a'], clouds: false, stars: true, fog: [0.03, 0.04, 0.08], fn: 500, ff: 900, shadowY: null, build() {}},
  underground: {sky: ['#1f1b18', '#4a3f35'], clouds: false, fog: [0.19, 0.16, 0.13], fn: 40, ff: 160, shadowY: null, build() {}},
  night: {sky: ['#0b1230', '#2a3a66'], clouds: false, stars: true, fog: [0.12, 0.16, 0.3], fn: 40, ff: 200, shadowY: 0, build() { flat('#2e4a3a'); }}
};
function bgFor(env) {
  const e = ENV[env] || ENV.outdoor; sky(e.sky[0], e.sky[1], {h: .5, seed: 11, clouds: e.clouds !== false});
  if (e.stars) { const R = rng(5); ctx.fillStyle = '#fff'; for (let i = 0; i < 140; i++) { ctx.globalAlpha = 0.4 + R() * 0.6; ctx.fillRect(R() * W, R() * H * 0.8, 2 + R() * 2, 2 + R() * 2); } ctx.globalAlpha = 1; }
}

// ----- kamera -----
function camOf(c, u, t, S0) {
  if (!c) return null; if (c.win) { const a = tabs(c.win[0], S0), b = tabs(c.win[1], S0); u = sm((t - a) / Math.max(0.1, b - a)); } else u = sm(u);
  const fov = Array.isArray(c.fov) ? lpn(c.fov[0], c.fov[1], u) : (c.fov || 48);
  if (c.c) return {eye: orb(c.c, c.r || 24, c.a ? c.a[0] : 30, c.a ? c.a[1] : 30, c.h ? c.h[0] : 4, c.h ? c.h[1] : 4, u), at: c.c, fov};
  const nested = x => Array.isArray(x[0]); const eye = nested(c.eye) ? lp(c.eye[0], c.eye[1], u) : c.eye, at = nested(c.at) ? lp(c.at[0], c.at[1], u) : c.at; return {eye, at, fov};
}
function autocam(u, up) {
  const c = [(BB[0] + BB[3]) / 2, (BB[1] + BB[4]) / 2, (BB[2] + BB[5]) / 2], ex = Math.max(BB[3] - BB[0], BB[5] - BB[2], 1), hy = BB[4] - BB[1], fov = 48;
  const d = Math.max(ex * 1.12 / (0.5625 * 2 * Math.tan(fov * Math.PI / 360)), hy * 1.05 / (2 * Math.tan(fov * Math.PI / 360)) * 1.1);
  const a0 = 38 - 26 * sm(u); return {eye: [c[0] + d * Math.sin(a0 * Math.PI / 180), c[1] + hy * 0.55 + d * 0.22, c[2] + d * Math.cos(a0 * Math.PI / 180)], at: [c[0], c[1] - hy * (up ? 0.22 : 0.05), c[2]], fov};
}

// ----- timeline adegan -----
const SCN = (SPEC.scenes || []).map((s, i) => { const sents = Array.isArray(s.sent) ? s.sent : [s.sent == null ? i : s.sent, s.sent == null ? i : s.sent]; return Object.assign({}, s, {s0: sents[0], s1: sents[1]}); });
const START = SCN.map((s, i) => i === 0 ? 0 : (s.start != null ? tabs(s.start, 0) : sentT(s.s0) - 0.25));
for (let i = 1; i < START.length; i++) START[i] = Math.max(START[i], START[i - 1] + 0.6);
const LBLC = ['#2f8fbf', '#d97a1c', '#2f8f6a', '#7a5cc9', '#c99a10', '#2f66c9', '#127a76', '#e07a10'];
let WARNED = {};
function drawLabels(sc, S0, t) {
  const L = (sc.labels || []).filter(l => !l.show || (t >= tabs(l.show[0], S0) && t <= tabs(l.show[1], S0))); if (!L.length) return;
  const hasCard = !!(sc.card || sc.legend); LABMIN = hasCard ? 660 : 380;
  ctx.font = `700 29px ${FONT}`;
  const items = L.map((l, i) => { const p3 = typeof l.at === 'string' ? ANCH[l.at] : l.at; if (!p3) return null; const [px, py] = proj(p3); return {l, p3, px, py, w: ctx.measureText(l.text).width + 40, col: l.col || LBLC[i % LBLC.length]}; }).filter(Boolean).filter(x => x.py > 250 && x.py < 1500);
  items.sort((a, b) => a.py - b.py); let y = -1e9; const LO = LABMIN, HI = 1320;
  items.forEach(it => { it.ty = Math.max(LO, Math.min(HI, it.py - 60)); it.ty = Math.max(it.ty, y + 64); y = it.ty; });
  for (let i = items.length - 1, lim = HI + 64; i >= 0; i--) { items[i].ty = Math.min(items[i].ty, lim - 64); lim = items[i].ty; }
  items.forEach((it, i) => { const side = it.l.side || (it.px < W / 2 ? 1 : -1), bx = side > 0 ? it.px + 70 : it.px - 70 - it.w; callout(it.l.text, it.p3, (it.l.dx != null ? it.l.dx : bx - it.px), (it.l.dy != null ? it.l.dy : it.ty - it.py), it.col); });
  LABMIN = 360;
}
function drawExtras(sc, S0, t) {
  if (sc.card) dataCard(String(sc.card.big), sc.card.small || '', 40, 370, sc.card.w || Math.max(330, 60 + (sc.card.small || '').length * 15));
  if (sc.legend) { ctx.font = `700 28px ${FONT}`; let y = 372; sc.legend.forEach((it, i) => { const n = String(it.n != null ? it.n : i + 1), col = it.col || LBLC[i % LBLC.length]; ctx.fillStyle = '#13151a'; rr(40, y, 320, 52, 14); ctx.fill(); ctx.fillStyle = col; ctx.beginPath(); ctx.arc(70, y + 26, 20, 0, 7); ctx.fill(); ctx.fillStyle = '#fff'; ctx.textBaseline = 'middle'; ctx.font = `800 26px ${FONT}`; ctx.textAlign = 'center'; ctx.fillText(n, 70, y + 28); ctx.textAlign = 'left'; ctx.font = `700 27px ${FONT}`; ctx.fillText(it.text, 104, y + 28); y += 62; }); }
  (sc.badges || []).forEach((b, i) => { const p3 = typeof b.at === 'string' ? ANCH[b.at] : b.at; if (p3) badge(b.n != null ? b.n : i + 1, p3, b.col || LBLC[i % LBLC.length]); });
  if (sc.tag) tag(sc.tag); if (sc.ajak) ajak(sc.ajak);
}
window.TOTAL = TOTAL;
window.renderFrame = function (t) {
  let si = 0; while (si + 1 < START.length && t >= START[si + 1]) si++;
  const sc = SCN[si] || {}, S0 = START[si], S1 = si + 1 < START.length ? START[si + 1] : TOTAL, len = S1 - S0, u = Math.max(0, Math.min(1, (t - S0) / Math.max(0.1, len)));
  TT = t; TS = t - S0; for (const k in ANCH) delete ANCH[k];
  let dist = sc.move ? sc.move * t : 0; if (sc.roll) { const a = tabs(sc.roll.from, S0), b = a + (sc.roll.dur || 4), V = sc.roll.v || 4; if (t > a) { const x = (t - a) / (b - a); dist = x < 1 ? V * (b - a) * (x ** 3 - x ** 4 / 2) : V * (b - a) * 0.5 + V * (t - b); } else dist = 0; }
  AN.cr = t * 2 * Math.PI * 1.15; AN.fa = t * 9; AN.ph = t * 0.55; AN.wa = -dist / 0.55; AN.goff = -dist; AN.open = sm(TS / Math.max(0.5, len * 0.7));
  PO = null; TAGO = null; let ph = (sc.phases || []).find(p => (p.until == null || t < tabs(p.until, S0)) && (p.from == null || t >= tabs(p.from, S0))); if (ph && ph.heading) PO = [ph.kicker || sc.kicker || '', ph.heading]; else if (sc.heading) PO = [sc.kicker || '', sc.heading];
  SUBO = phraseAt(t + 0.06) || 'none'; CU.t = t; CU.mouth = mouthAt(t); CU.wave = (t < 3.2 || (si === SCN.length - 1 && t > S0 + 0.5)) ? 1 : 0;
  OP = newB(); GL = newB(); ctx.clearRect(0, 0, W, H); MS = null; MSst.length = 0;
  let cam, env = ENV[sc.env] || ENV.outdoor, opt = {shadowY: env.shadowY, fog: env.fog, fn: env.fn, ff: env.ff, glassA: sc.glassA || 0.32};
  if (sc.legacy) { const L = SC[sc.legacy]; L.bg(); L.build(); cam = camOf(sc.cam, u, t, S0) || L.cam; Object.assign(opt, {shadowY: L.shadowY, fog: L.fog, fn: L.fn, ff: L.ff, L: L.L, glassA: L.glassA}); }
  else {
    bgFor(sc.env); (env.build || (() => {}))(sc);
    BBon = true; BB.splice(0, 6, 1e9, 1e9, 1e9, -1e9, -1e9, -1e9); (sc.objs || []).forEach((o, i) => { if (!(COMP[o.t || o.k] || ['box', 'cyl', 'sph', 'link', 'path', 'flow', 'group'].includes(o.t))) { if (!WARNED[o.t]) { console.log('WARN jenis tidak dikenal:', o.t); WARNED[o.t] = 1; } return; } try { const nb = o.nobb || o.t === 'sun' || o.t === 'cloud'; if (nb) BBon = false; buildObj(o, i); BBon = true; } catch (e) { console.log('WARN objek gagal', o.t, e.message); } }); BBon = false;
    cam = camOf(sc.cam, u, t, S0) || autocam(u, !!(sc.ajak || sc.card));
  }
  renderGL(cam, opt); ctx.drawImage(glc, 0, 0); LABMIN = 360;
  if (sc.legacy) { SC[sc.legacy].ov(); } else { panel(sc.kicker || '', sc.heading || ''); drawLabels(sc, S0, t); drawExtras(sc, S0, t); subtitle([], 0); }
  chrome();
};
window.frameJPEG = function (t, q) { renderFrame(t); return c2.toDataURL('image/jpeg', q || 0.92); };
Promise.all(['700 30px Poppins', '600 30px Inter', '800 30px Inter', '900 30px Inter', '700 30px "DejaVu Sans Mono"'].map(f => document.fonts.load(f))).then(() => { window.READY = true; });
