// Overlay 2D (panel judul, label, subtitle, watermark, maskot) — dipindahkan dari engine/core.js agar tampilan sama.
export function createOverlay(c2, W, H, proj) {
const ctx = c2.getContext('2d');
function rng(s) { let a = s >>> 0; return () => ((a = (a * 1664525 + 1013904223) >>> 0) / 4294967296); }
const FONT = 'Poppins, Inter, sans-serif', MONO = '"DejaVu Sans Mono", monospace';
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
function sky(top, bot, o = {}) {
  const g = ctx.createLinearGradient(0, 0, 0, H * (o.h || 0.62)); g.addColorStop(0, top); g.addColorStop(1, bot); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  if (o.clouds !== false) { const R = rng(o.seed || 5); for (let i = 0; i < 9; i++) { const x = R() * W, y = 80 + R() * 520, s = 120 + R() * 180; for (let k = 0; k < 5; k++) { const rg = ctx.createRadialGradient(x + k * s * .35, y + R() * 30, 0, x + k * s * .35, y, s * .55); rg.addColorStop(0, 'rgba(255,255,255,.85)'); rg.addColorStop(1, 'rgba(255,255,255,0)'); ctx.fillStyle = rg; ctx.fillRect(x + k * s * .35 - s, y - s, s * 2, s * 2); } } }
}
const TEAL = '#1F7A63';
let PO = null, SUBO = null, TAGO = null, FADE = 1;
function panel(kicker, heading) {
  if (PO) { kicker = PO[0]; heading = PO[1]; }
  const g = ctx.createLinearGradient(0, 0, 0, 340); g.addColorStop(0, 'rgba(237,235,221,.97)'); g.addColorStop(.72, 'rgba(237,235,221,.85)'); g.addColorStop(1, 'rgba(237,235,221,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, 340);
  ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.font = `700 25px ${MONO}`; ctx.letterSpacing = '6px'; ctx.fillStyle = '#56655e'; ctx.fillText(kicker.toUpperCase(), W / 2 + 3, 82); ctx.letterSpacing = '0px';
  const words = []; heading.split('*').forEach((p, i) => p.split(' ').forEach(w => { if (w) words.push({t: w, kw: i % 2 === 1}); }));
  ctx.font = `800 58px Inter, ${FONT}`; const sp = ctx.measureText(' ').width; const MAXW = 940, lines = [[]]; let cw = 0;
  words.forEach(w => { w.w = ctx.measureText(w.t).width; const add = (lines[lines.length - 1].length ? sp : 0) + w.w; if (cw + add > MAXW && lines[lines.length - 1].length) { lines.push([w]); cw = w.w; } else { lines[lines.length - 1].push(w); cw += add; } });
  let y = lines.length === 1 ? 190 : 160; ctx.textAlign = 'left';
  lines.forEach(l => { const tw = l.reduce((a, w) => a + w.w, 0) + sp * (l.length - 1); let x = W / 2 - tw / 2; l.forEach(w => { ctx.fillStyle = w.kw ? TEAL : '#14181b'; ctx.fillText(w.t, x, y); x += w.w + sp; }); y += 74; });
}
function watermark() { // FAKTA UNIK kanan bawah
  ctx.font = `800 36px Inter, ${FONT}`; const w1 = ctx.measureText('FAKTA ').width, w2 = ctx.measureText('UNIK').width, ph = 76, pw = w1 + w2 + 108, x = W - 36 - pw, y = 1806;
  ctx.fillStyle = 'rgba(21,34,31,.94)'; rr(x, y, pw, ph, 38); ctx.fill();
  ctx.fillStyle = '#7fe0c2'; ctx.beginPath(); ctx.arc(x + 38, y + ph / 2, 13, 0, 7); ctx.fill(); ctx.fillStyle = '#15221f'; ctx.fillRect(x + 32, y + ph / 2 - 4, 12, 8);
  ctx.textBaseline = 'middle'; ctx.fillStyle = '#fff'; ctx.fillText('FAKTA ', x + 64, y + ph / 2 + 2);
  ctx.fillStyle = '#7fe0c2'; rr(x + 64 + w1 - 6, y + 12, w2 + 18, ph - 24, 11); ctx.fill(); ctx.fillStyle = '#15221f'; ctx.fillText('UNIK', x + 64 + w1 + 3, y + ph / 2 + 2);
}
let LABMIN = 360;
function callout(text, p3, dx, dy, col = '#f08a1c', o = {}) {
  const [px, py] = proj(p3); ctx.font = `700 29px ${FONT}`; const w = ctx.measureText(text).width + 40, h = 50;
  let bx = px + dx, by = py + dy; bx = Math.max(24, Math.min(W - 24 - w, bx)); by = Math.max(LABMIN, by);
  const ax = Math.max(bx + 20, Math.min(bx + w - 20, px)), ay = py < by ? by : by + h;
  ctx.strokeStyle = '#13151a'; ctx.lineWidth = 7; ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(ax, by + (py < by ? 0 : h)); ctx.stroke();
  ctx.strokeStyle = '#fff'; ctx.lineWidth = 3; ctx.stroke();
  ctx.fillStyle = '#13151a'; ctx.beginPath(); ctx.arc(px, py, 11, 0, 7); ctx.fill(); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(px, py, 7, 0, 7); ctx.fill();
  ctx.fillStyle = 'rgba(0,0,0,.28)'; rr(bx + 3, by + 5, w, h, 14); ctx.fill(); ctx.fillStyle = col; rr(bx, by, w, h, 14); ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = '#13151a'; ctx.stroke();
  ctx.fillStyle = o.fg || '#fff'; ctx.textBaseline = 'middle'; ctx.fillText(text, bx + 20, by + h / 2 + 2);
}
function badge(n, p3, col) { const [x, y] = proj(p3); ctx.fillStyle = '#13151a'; ctx.beginPath(); ctx.arc(x, y, 30, 0, 7); ctx.fill(); ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y, 25, 0, 7); ctx.fill(); ctx.fillStyle = '#fff'; ctx.font = `800 32px ${FONT}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(String(n), x, y + 2); ctx.textAlign = 'left'; }
function dataCard(big, small, x = 40, y = 370, w = 330) {
  ctx.fillStyle = 'rgba(0,0,0,.25)'; rr(x + 5, y + 7, w, 150, 24); ctx.fill(); ctx.fillStyle = '#fff'; rr(x, y, w, 150, 24); ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = '#13151a'; ctx.stroke();
  ctx.fillStyle = TEAL; ctx.font = `900 72px Inter, ${FONT}`; ctx.textBaseline = 'alphabetic'; ctx.fillText(big, x + 28, y + 84); ctx.fillStyle = '#3a3f45'; ctx.font = `600 25px Inter, ${FONT}`; ctx.fillText(small, x + 28, y + 126);
}
function tag(t) { if (TAGO) t = TAGO; ctx.font = `700 23px ${MONO}`; ctx.letterSpacing = '2px'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineWidth = 5; ctx.strokeStyle = 'rgba(15,20,18,.9)'; ctx.strokeText(t, W / 2, 1376); ctx.fillStyle = '#f6f2e2'; ctx.fillText(t, W / 2, 1376); ctx.letterSpacing = '0px'; ctx.textAlign = 'left'; }
function ajak(text) { const w = 900, h = 112, x = W / 2 - w / 2, y = 1130; ctx.fillStyle = 'rgba(0,0,0,.25)'; rr(x + 5, y + 7, w, h, 56); ctx.fill(); ctx.fillStyle = '#fff'; rr(x, y, w, h, 56); ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = '#13151a'; ctx.stroke();
  ctx.fillStyle = TEAL; rr(x + 28, y + 28, 64, 52, 14); ctx.fill(); ctx.beginPath(); ctx.moveTo(x + 44, y + 78); ctx.lineTo(x + 40, y + 98); ctx.lineTo(x + 62, y + 80); ctx.fill(); ctx.fillStyle = '#fff'; for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.arc(x + 46 + i * 14, y + 54, 4.5, 0, 7); ctx.fill(); }
  ctx.fillStyle = '#14181b'; ctx.font = `800 33px Inter, ${FONT}`; ctx.textBaseline = 'middle'; ctx.fillText(text, x + 116, y + h / 2 + 2); }
function subtitle(words, act) {
  if (SUBO === 'none') return; if (SUBO) { words = SUBO.words; act = SUBO.act; }
  ctx.font = `700 50px ${FONT}`; ctx.textBaseline = 'middle';
  const sp = ctx.measureText(' ').width, ws = words.map(w => ctx.measureText(w).width), MAXW = 800;
  const lines = [[]]; let cw = 0;
  words.forEach((w, i) => { const add = (lines[lines.length - 1].length ? sp : 0) + ws[i]; if (cw + add > MAXW && lines[lines.length - 1].length) { lines.push([i]); cw = ws[i]; } else { lines[lines.length - 1].push(i); cw += add; } });
  const lw = lines.map(l => l.reduce((a, i) => a + ws[i], 0) + sp * (l.length - 1)), bw = Math.max(...lw) + 70, LH = 72, bh = lines.length * LH + 30, cx = W / 2, cy = 1522;
  ctx.fillStyle = 'rgba(30,58,52,.93)'; rr(cx - bw / 2, cy - bh / 2, bw, bh, 30); ctx.fill();
  lines.forEach((l, li) => { let x = cx - lw[li] / 2; const y = cy - bh / 2 + 15 + li * LH + LH / 2;
    l.forEach(i => { if (i === act) { const bx = x - 10, by = y - 36, bw2 = ws[i] + 20, bh2 = 70; ctx.save(); rr(bx, by, bw2, bh2, 13); ctx.clip(); ctx.fillStyle = 'rgba(150,235,205,.28)'; ctx.fillRect(bx, by, bw2, bh2); ctx.strokeStyle = 'rgba(190,255,230,.85)'; ctx.lineWidth = 2; for (let k = -bh2; k < bw2; k += 10) { ctx.beginPath(); ctx.moveTo(bx + k, by + bh2); ctx.lineTo(bx + k + bh2, by); ctx.stroke(); } ctx.restore(); }
      ctx.fillStyle = '#fff'; ctx.fillText(words[i], x, y); x += ws[i] + sp; }); });
}
const CU = {t: 0, mouth: 0, wave: 0};
function curio() {
  const im = document.getElementById('curio'), h0 = 290, k0 = h0 / im.naturalHeight, w0 = im.naturalWidth * k0, t = CU.t;
  if (t < 0.15) return;
  const pop = Math.min(1, (t - 0.15) / 0.35), sc = pop < 1 ? (1 - Math.pow(1 - pop, 3)) * 1.08 - Math.sin(pop * Math.PI) * 0.0 : 1, ov = pop < 1 ? 1 + 0.08 * Math.sin(pop * Math.PI) : 1, k = k0 * Math.min(1, 0.4 + 0.6 * pop) * ov;
  const x0 = 24, yb = H - 12, w = im.naturalWidth * k, h = im.naturalHeight * k;
  ctx.save(); ctx.translate(x0 + w0 / 2, yb); ctx.rotate(CU.wave * Math.sin(t * 6.0) * 0.045); ctx.translate(0, -CU.mouth * 3);
  ctx.translate(-w0 / 2, 0);
  // face overlays in image space
  ctx.save(); ctx.scale(k, k); ctx.translate((w0 / k - im.naturalWidth) / 2, -im.naturalHeight);
  ctx.drawImage(im, 0, 0);
  const skin = '#f2c9a0', navy = '#0b1f3a', m = CU.mouth;
  if (m > 0.06) {
    ctx.fillStyle = skin; ctx.beginPath(); ctx.ellipse(440, 538, 66, 34, 0, 0, 7); ctx.fill();
    const rx = 30 + 14 * m, ry = 5 + 26 * m; ctx.fillStyle = navy; ctx.beginPath(); ctx.ellipse(440, 536 + ry * 0.35, rx, ry, 0, 0, 7); ctx.fill();
    ctx.save(); ctx.beginPath(); ctx.ellipse(440, 536 + ry * 0.35, rx - 3, ry - 3, 0, 0, 7); ctx.clip(); ctx.fillStyle = '#e9707a'; ctx.beginPath(); ctx.ellipse(440, 536 + ry * 0.35 + ry * 0.75, rx * 0.7, ry * 0.55, 0, 0, 7); ctx.fill(); ctx.restore();
    ctx.fillStyle = '#fff'; ctx.fillRect(440 - rx * 0.6, 536 + ry * 0.35 - ry + 3, rx * 1.2, Math.min(9, ry * 0.4));
  }
  const bp = ((t % 3.1) / 3.1); if (bp > 0.965 || (t > 5.9 && t < 6.0)) { ctx.fillStyle = skin; for (const ex of [380, 500]) { ctx.beginPath(); ctx.ellipse(ex, 456, 27, 25, 0, 0, 7); ctx.fill(); ctx.strokeStyle = navy; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(ex, 452, 20, 0.15 * Math.PI, 0.85 * Math.PI); ctx.stroke(); } }
  ctx.restore(); ctx.restore();
}
function chrome() { if (CU.t >= 0.3) { ctx.save(); ctx.globalAlpha = Math.min(1, (CU.t - 0.3) / 0.25); watermark(); ctx.restore(); } curio(); }
return { setO: (po, subo, tago) => { PO = po; SUBO = subo; TAGO = tago; }, ctx, panel, watermark, callout, badge, dataCard, tag, ajak, subtitle, chrome, CU, rr, setLabMin: v => { LABMIN = v; }, FONT, MONO };
}
