import { renderScene, proj, ANCH, SHOT_DEFS, W, H } from './scene.js';
import { createOverlay } from './overlay.js';
const TM = window.TIMING, SS = TM.sent_spans, FPS = 30, TOTAL = TM.dur + 0.8, SPEC = window.SPEC || { scenes: [] };
const sm = u => { u = Math.max(0, Math.min(1, u)); return u * u * (3 - 2 * u); };
const lpn = (a, b, u) => a + (b - a) * u, lp = (a, b, u) => a.map((v, i) => lpn(v, b[i], u));
const sentT = i => SS[Math.max(0, Math.min(SS.length - 1, i))][0];
const LBLC = ['#f08a1c', '#1f9fd1', '#d6457a', '#3aa655', '#8a5cd6'];

// ----- timing kata / subtitle (sama dengan engine lama) -----
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
  if (!cur) return null; let act = 0; for (let j = 0; j < cur.length; j++) if (t >= T0(cur[j])) act = j; return { words: cur.map(i => TM.words[i].w), act };
}
const mouthAt = t => { const f = t * FPS, i = Math.floor(f), a = TM.mouth[Math.min(i, TM.mouth.length - 1)] || 0, b = TM.mouth[Math.min(i + 1, TM.mouth.length - 1)] || 0; return a + (b - a) * (f - i); };

// ----- adegan -----
const SC = SPEC.scenes;
const START = SC.map((s, i) => i === 0 ? 0 : Math.max(0, sentT(s.sent[0]) - 0.25));
const c2 = document.getElementById('c2'), glc = document.getElementById('gl');
const O = createOverlay(c2, W, H, proj), ctx = O.ctx;

function shotAt(sc, u) {
  const [a, b] = (sc.cam || ['wide', 'wide']).map(n => SHOT_DEFS[n] || SHOT_DEFS.wide), e = sm(u);
  return { p: lp(a.p, b.p, e), l: lp(a.l, b.l, e), f: lpn(a.f, b.f, e), front: !!(u < 0.5 ? (a.front || sc.cam[0].startsWith('front')) : (b.front || sc.cam[1].startsWith('front'))) };
}
window.TOTAL = TOTAL;
window.renderFrame = function (t) {
  let si = 0; while (si + 1 < START.length && t >= START[si + 1]) si++;
  const sc = SC[si] || {}, S0 = START[si], S1 = si + 1 < START.length ? START[si + 1] : TOTAL, u = Math.max(0, Math.min(1, (t - S0) / Math.max(0.1, S1 - S0)));
  renderScene(t, shotAt(sc, u));
  ctx.clearRect(0, 0, W, H); ctx.drawImage(glc, 0, 0);
  O.CU.t = t; O.CU.mouth = mouthAt(t); O.CU.wave = (t < 3.2 || (si === SC.length - 1 && t > S0 + 0.5)) ? 1 : 0;
  O.setO(null, phraseAt(t + 0.06) || 'none', null);
  O.panel(sc.kicker || '', sc.heading || '');
  O.setLabMin(sc.card ? 560 : 360);
  const fade = Math.min(1, (t - S0) / 0.4);
  ctx.save(); ctx.globalAlpha = fade;
  (sc.labels || []).forEach((l, i) => { const p = ANCH[l.at] || l.at; const sp = p && proj(p); if (p && sp[0] > 40 && sp[0] < 1040 && sp[1] > 380 && sp[1] < 1290) O.callout(l.text, p, l.dx != null ? l.dx : (i % 2 ? 90 : -250), l.dy != null ? l.dy : 90 + (i % 3) * 70, LBLC[i % LBLC.length]); });
  if (sc.card) O.dataCard(sc.card.big, sc.card.small);
  ctx.restore();
  if (sc.tag) O.tag(sc.tag); if (sc.ajak) O.ajak(sc.ajak);
  O.subtitle([], 0); O.chrome();
};
window.frameJPEG = (t, q) => { window.renderFrame(t); return c2.toDataURL('image/jpeg', q || 0.92); };
Promise.all(['700 30px Poppins', '600 30px Inter', '800 30px Inter', '900 30px Inter', '700 30px "DejaVu Sans Mono"'].map(f => document.fonts.load(f))).then(() => { window.READY = true; });

window.__anch = () => Object.fromEntries(Object.entries(ANCH).map(([k, v]) => [k, proj(v).map(Math.round)]));
