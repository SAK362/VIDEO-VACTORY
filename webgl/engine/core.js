const W = 1080, H = 1920;
const glc = document.getElementById('gl'), c2 = document.getElementById('c2'), ctx = c2.getContext('2d');
const gl = glc.getContext('webgl', {antialias: true, stencil: true, preserveDrawingBuffer: true, alpha: true, premultipliedAlpha: true});

// ---------- shaders ----------
function sh(t, s) { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; }
const prog = gl.createProgram();
gl.attachShader(prog, sh(gl.VERTEX_SHADER, `
attribute vec3 p; attribute vec3 n; attribute vec4 c;
uniform mat4 VP; varying vec3 vn; varying vec4 vc; varying vec3 wp;
void main(){ vn=n; vc=c; wp=p; gl_Position=VP*vec4(p,1.); }`));
gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, `
precision highp float;
uniform vec3 L; uniform vec3 cam; uniform vec3 fogc; uniform float fn; uniform float ff; uniform float alpha; uniform float shadow;
varying vec3 vn; varying vec4 vc; varying vec3 wp;
void main(){
  if(shadow>0.5){ gl_FragColor=vec4(0.05,0.08,0.12,0.30); return; }
  vec3 N=normalize(vn); 
  float d=max(dot(N,-L),0.);
  float hemi=N.y*.5+.5;
  vec3 amb=mix(vec3(.40,.37,.35),vec3(.66,.76,.90),hemi);
  vec3 col=vc.rgb*(amb*.78+vec3(1.,.94,.84)*d*.82);
  vec3 V=normalize(cam-wp); vec3 Hh=normalize(V-L);
  col+=pow(max(dot(N,Hh),0.),48.)*.14;
  col+=pow(1.-max(dot(N,V),0.),3.)*.07*hemi;
  col=mix(col,vc.rgb*1.15,vc.a);
  float dist=length(cam-wp);
  float f=clamp((dist-fn)/(ff-fn),0.,1.);
  col=mix(col,fogc,f*f*(3.-2.*f));
  gl_FragColor=vec4(col,alpha);
}`));
gl.linkProgram(prog); gl.useProgram(prog);
const U = {}; ['VP', 'L', 'cam', 'fogc', 'fn', 'ff', 'alpha', 'shadow'].forEach(k => U[k] = gl.getUniformLocation(prog, k));
const A = {p: gl.getAttribLocation(prog, 'p'), n: gl.getAttribLocation(prog, 'n'), c: gl.getAttribLocation(prog, 'c')};

// ---------- math ----------
const mm = (a, b) => { const r = new Array(16).fill(0); for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) { let s = 0; for (let k = 0; k < 4; k++) s += a[k * 4 + j] * b[i * 4 + k]; r[i * 4 + j] = s; } return r; };
const T = (x, y, z) => [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, x, y, z, 1];
const S = (x, y, z) => [x, 0, 0, 0, 0, y, 0, 0, 0, 0, z, 0, 0, 0, 0, 1];
const RX = a => { const c = Math.cos(a), s = Math.sin(a); return [1, 0, 0, 0, 0, c, s, 0, 0, -s, c, 0, 0, 0, 0, 1]; };
const RY = a => { const c = Math.cos(a), s = Math.sin(a); return [c, 0, -s, 0, 0, 1, 0, 0, s, 0, c, 0, 0, 0, 0, 1]; };
const RZ = a => { const c = Math.cos(a), s = Math.sin(a); return [c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]; };
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const nrm = a => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
const lookAt = (e, t, up = [0, 1, 0]) => { const f = nrm(sub(t, e)), s = nrm(cross(f, up)), u = cross(s, f); return [s[0], u[0], -f[0], 0, s[1], u[1], -f[1], 0, s[2], u[2], -f[2], 0, -dot(s, e), -dot(u, e), dot(f, e), 1]; };
const persp = (fov, asp, n, f) => { const q = 1 / Math.tan(fov * Math.PI / 360); return [q / asp, 0, 0, 0, 0, q, 0, 0, 0, 0, (f + n) / (n - f), -1, 0, 0, 2 * f * n / (n - f), 0]; };
let VPm = null;
function proj(p) { const m = VPm; const x = m[0] * p[0] + m[4] * p[1] + m[8] * p[2] + m[12], y = m[1] * p[0] + m[5] * p[1] + m[9] * p[2] + m[13], w = m[3] * p[0] + m[7] * p[1] + m[11] * p[2] + m[15]; return [(x / w * .5 + .5) * W, (1 - (y / w * .5 + .5)) * H]; }
function rng(seed) { return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

// ---------- unit shapes ----------
const shapes = {};
function mkBox() {
  const t = [], f = [[[1, 0, 0], [[.5, -.5, -.5], [.5, .5, -.5], [.5, .5, .5], [.5, -.5, .5]]], [[-1, 0, 0], [[-.5, -.5, .5], [-.5, .5, .5], [-.5, .5, -.5], [-.5, -.5, -.5]]],
    [[0, 1, 0], [[-.5, .5, -.5], [-.5, .5, .5], [.5, .5, .5], [.5, .5, -.5]]], [[0, -1, 0], [[-.5, -.5, .5], [-.5, -.5, -.5], [.5, -.5, -.5], [.5, -.5, .5]]],
    [[0, 0, 1], [[-.5, -.5, .5], [.5, -.5, .5], [.5, .5, .5], [-.5, .5, .5]]], [[0, 0, -1], [[.5, -.5, -.5], [-.5, -.5, -.5], [-.5, .5, -.5], [.5, .5, -.5]]]];
  f.forEach(([n, q]) => { [[0, 1, 2], [0, 2, 3]].forEach(i => t.push({p: i.map(k => q[k]), n: [n, n, n]})); });
  return t;
}
function mkCyl(seg, rt, rb) {
  const t = [], sl = (rb - rt);
  for (let i = 0; i < seg; i++) {
    const a0 = i / seg * Math.PI * 2, a1 = (i + 1) / seg * Math.PI * 2, c0 = Math.cos(a0), s0 = Math.sin(a0), c1 = Math.cos(a1), s1 = Math.sin(a1);
    const n0 = nrm([c0, sl, s0]), n1 = nrm([c1, sl, s1]);
    const p00 = [c0 * rb, -.5, s0 * rb], p10 = [c1 * rb, -.5, s1 * rb], p01 = [c0 * rt, .5, s0 * rt], p11 = [c1 * rt, .5, s1 * rt];
    t.push({p: [p00, p10, p11], n: [n0, n1, n1]}); t.push({p: [p00, p11, p01], n: [n0, n1, n0]});
    if (rt > 0) t.push({p: [[0, .5, 0], p01, p11], n: [[0, 1, 0], [0, 1, 0], [0, 1, 0]]});
    if (rb > 0) t.push({p: [[0, -.5, 0], p10, p00], n: [[0, -1, 0], [0, -1, 0], [0, -1, 0]]});
  }
  return t;
}
function mkSph(seg, ring) {
  const t = [], P = (i, j) => { const a = i / seg * Math.PI * 2, b = j / ring * Math.PI; return [Math.cos(a) * Math.sin(b), Math.cos(b), Math.sin(a) * Math.sin(b)]; };
  for (let j = 0; j < ring; j++) for (let i = 0; i < seg; i++) {
    const a = P(i, j), b = P(i + 1, j), c = P(i + 1, j + 1), d = P(i, j + 1);
    if (j > 0) t.push({p: [a, b, c], n: [a, b, c]}); if (j < ring - 1) t.push({p: [a, c, d], n: [a, c, d]});
  }
  return t.map(q => ({p: q.p.map(v => v.map(x => x * 0.5 * 2 / 2)), n: q.n}));
}
shapes.box = mkBox();
const cylCache = {}; const cylShape = (seg, rt, rb) => { const k = seg + '_' + rt + '_' + rb; return cylCache[k] || (cylCache[k] = mkCyl(seg, rt, rb)); };
const sphCache = {}; const sphShape = (s) => sphCache[s] || (sphCache[s] = mkSph(s, Math.max(6, s >> 1)));

// ---------- batches ----------
const newB = () => ({d: [], sh: []});
let OP, GL;
let MS = null; const MSst = [];
const IDM = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
function pushM(M) { MSst.push(MS); MS = MS ? mm(MS, M) : M; }
function popM() { MS = MSst.pop(); }
const wpt = p => MS ? [MS[0] * p[0] + MS[4] * p[1] + MS[8] * p[2] + MS[12], MS[1] * p[0] + MS[5] * p[1] + MS[9] * p[2] + MS[13], MS[2] * p[0] + MS[6] * p[1] + MS[10] * p[2] + MS[14]] : p.slice();
let BBon = false; const BB = [1e9, 1e9, 1e9, -1e9, -1e9, -1e9];
function add(B, tris, M, col, emi, noShadow) {
  if (MS) M = mm(MS, M);
  const a0 = [M[0], M[1], M[2]], a1 = [M[4], M[5], M[6]], a2 = [M[8], M[9], M[10]];
  const c12 = cross(a1, a2), c20 = cross(a2, a0), c01 = cross(a0, a1), det = dot(a0, c12), sg = det < 0 ? -1 : 1;
  for (const t of tris) for (let k = 0; k < 3; k++) {
    const p = t.p[k], n = t.n[k];
    const x = M[0] * p[0] + M[4] * p[1] + M[8] * p[2] + M[12], y = M[1] * p[0] + M[5] * p[1] + M[9] * p[2] + M[13], z = M[2] * p[0] + M[6] * p[1] + M[10] * p[2] + M[14];
    let nx = n[0] * c12[0] + n[1] * c20[0] + n[2] * c01[0], ny = n[0] * c12[1] + n[1] * c20[1] + n[2] * c01[1], nz = n[0] * c12[2] + n[1] * c20[2] + n[2] * c01[2];
    const l = Math.hypot(nx, ny, nz) || 1; nx *= sg / l; ny *= sg / l; nz *= sg / l;
    if (BBon) { if (x < BB[0]) BB[0] = x; if (y < BB[1]) BB[1] = y; if (z < BB[2]) BB[2] = z; if (x > BB[3]) BB[3] = x; if (y > BB[4]) BB[4] = y; if (z > BB[5]) BB[5] = z; }
    B.d.push(x, y, z, nx, ny, nz, col[0], col[1], col[2], emi || 0);
  }
  if (!noShadow && B === OP) { /* shadow source tracked separately */ const n = tris.length * 3; for (let i = B.d.length - n * 10; i < B.d.length; i += 10) B.sh.push(B.d[i], B.d[i + 1], B.d[i + 2]); }
}
const hex = h => [parseInt(h.slice(1, 3), 16) / 255, parseInt(h.slice(3, 5), 16) / 255, parseInt(h.slice(5, 7), 16) / 255];
const C = s => typeof s === 'string' ? hex(s) : s;
function box(x, y, z, sx, sy, sz, col, o = {}) { const M = mm(T(x, y, z), mm(RY(o.ry || 0), mm(RX(o.rx || 0), mm(RZ(o.rz || 0), S(sx, sy, sz))))); add(o.glass ? GL : OP, shapes.box, M, C(col), o.e, o.ns); }
function cyl(x, y, z, r, h, col, o = {}) { const M = mm(T(x, y, z), mm(RY(o.ry || 0), mm(RX(o.rx || 0), mm(RZ(o.rz || 0), S(r, h, r))))); add(o.glass ? GL : OP, cylShape(o.seg || 18, o.rt == null ? 1 : o.rt, o.rb == null ? 1 : o.rb), M, C(col), o.e, o.ns); }
function sph(x, y, z, r, col, o = {}) { const M = mm(T(x, y, z), S(r * 2, r * 2, r * 2)); add(o.glass ? GL : OP, sphShape(o.seg || 14), M, C(col), o.e, o.ns); }
function link(a, b, r, col, o = {}) {
  const d = sub(b, a), len = Math.hypot(...d) || 1e-6, y = [d[0] / len, d[1] / len, d[2] / len], ref = Math.abs(y[1]) < .9 ? [0, 1, 0] : [1, 0, 0], x = nrm(cross(ref, y)), z = cross(x, y), mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2];
  const M = [x[0] * r, x[1] * r, x[2] * r, 0, y[0] * len, y[1] * len, y[2] * len, 0, z[0] * r, z[1] * r, z[2] * r, 0, mid[0], mid[1], mid[2], 1];
  add(o.glass ? GL : OP, cylShape(o.seg || 12, o.rt == null ? 1 : o.rt, o.rb == null ? 1 : o.rb), M, C(col), o.e, o.ns);
}
function path(pts, r, col, o = {}) { for (let i = 0; i < pts.length - 1; i++) link(pts[i], pts[i + 1], r, col, o); }
function along(pts, t) { // point on polyline at fraction t
  const L = []; let tot = 0; for (let i = 0; i < pts.length - 1; i++) { const l = Math.hypot(...sub(pts[i + 1], pts[i])); L.push(l); tot += l; }
  let d = t * tot; for (let i = 0; i < L.length; i++) { if (d <= L[i] || i === L.length - 1) { const u = Math.min(1, d / L[i]); return pts[i].map((v, k) => v + (pts[i + 1][k] - v) * u); } d -= L[i]; }
}

// ---------- palette ----------
const P = {
  grass: '#5f8a48', grass2: '#6f9d4d', ballast: '#8d8a84', sleeper: '#8a8577', rail: '#6b6f75', steel: '#454b54', steelL: '#7b838e',
  blue: '#1d3f86', blueD: '#17316b', orange: '#f08a1c', white: '#eef0ee', floor: '#4e535b', wallIn: '#c9ccc7', glass: '#9fd0e6',
  engine: '#6c7a86', engineD: '#3d4852', head: '#a9b6a2', cap: '#8e9c96', alt: '#2f66c9', altD: '#1f4a9a', copper: '#d98a3b', rad: '#7ec3e6', radD: '#4a97bd',
  tank: '#eeb92a', tankD: '#b98a12', red: '#d94b3d', teal: '#1aa6a0', tealD: '#127a76', cable: '#ff8b1f', fuelc: '#ffd23a', black: '#22262b', yellow: '#ffd23a'
};

// ---------- rendering ----------
function upload(B, mode) {
  const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(B.d), gl.STATIC_DRAW);
  gl.enableVertexAttribArray(A.p); gl.vertexAttribPointer(A.p, 3, gl.FLOAT, false, 40, 0);
  gl.enableVertexAttribArray(A.n); gl.vertexAttribPointer(A.n, 3, gl.FLOAT, false, 40, 12);
  gl.enableVertexAttribArray(A.c); gl.vertexAttribPointer(A.c, 4, gl.FLOAT, false, 40, 24);
  gl.drawArrays(gl.TRIANGLES, 0, B.d.length / 10);
}
function renderGL(cam, o = {}) {
  gl.viewport(0, 0, W, H); gl.clearColor(0, 0, 0, 0); gl.clearStencil(0); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT | gl.STENCIL_BUFFER_BIT);
  gl.enable(gl.DEPTH_TEST); gl.depthFunc(gl.LEQUAL);
  const V = lookAt(cam.eye, cam.at), Pm = persp(cam.fov, W / H, 0.3, 700); VPm = mm(Pm, V);
  const Ld = nrm(o.L || [-0.5, -0.82, -0.42]);
  gl.uniformMatrix4fv(U.VP, false, new Float32Array(VPm)); gl.uniform3fv(U.L, Ld); gl.uniform3fv(U.cam, cam.eye);
  gl.uniform3fv(U.fogc, o.fog || [0.80, 0.88, 0.94]); gl.uniform1f(U.fn, o.fn || 30); gl.uniform1f(U.ff, o.ff || 190);
  gl.uniform1f(U.alpha, 1); gl.uniform1f(U.shadow, 0); gl.disable(gl.BLEND);
  upload(OP, 0);
  if (o.shadowY != null) {
    const sd = [], gy = o.shadowY;
    for (let i = 0; i < OP.sh.length; i += 9) {
      const tri = []; let ok = true;
      for (let k = 0; k < 3; k++) { const x = OP.sh[i + k * 3], y = OP.sh[i + k * 3 + 1], z = OP.sh[i + k * 3 + 2]; if (y < gy - 0.02) { ok = false; break; } const t = (gy - y) / Ld[1]; tri.push(x + Ld[0] * t, gy + 0.012, z + Ld[2] * t); }
      if (ok) for (let k = 0; k < 3; k++) sd.push(tri[k * 3], tri[k * 3 + 1], tri[k * 3 + 2], 0, 1, 0, 0, 0, 0, 0);
    }
    gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA); gl.depthMask(false);
    gl.enable(gl.STENCIL_TEST); gl.stencilFunc(gl.EQUAL, 0, 255); gl.stencilOp(gl.KEEP, gl.KEEP, gl.INCR);
    gl.uniform1f(U.shadow, 1); upload({d: sd}, 1); gl.uniform1f(U.shadow, 0);
    gl.disable(gl.STENCIL_TEST); gl.depthMask(true);
  }
  if (GL.d.length) { gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA); gl.depthMask(false); gl.uniform1f(U.alpha, o.glassA || 0.32); upload(GL, 1); gl.depthMask(true); gl.uniform1f(U.alpha, 1); }
}

// ---------- 2D overlay helpers ----------
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
function chrome(o = {}) { if (CU.t >= 0.3) { ctx.save(); ctx.globalAlpha = Math.min(1, (CU.t - 0.3) / 0.25); watermark(); ctx.restore(); } curio(); }
