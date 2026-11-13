// Tekstur prosedural (kanvas) untuk batu, beton, baja. Tanpa aset luar.
import * as THREE from 'three';

function rng(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }

export function makeNoise(seed = 1) {
  const R = rng(seed), P = new Uint8Array(512), p = [...Array(256).keys()];
  for (let i = 255; i > 0; i--) { const j = Math.floor(R() * (i + 1)); [p[i], p[j]] = [p[j], p[i]]; }
  for (let i = 0; i < 512; i++) P[i] = p[i & 255];
  const g = new Float32Array(256).map(() => R() * 2 - 1);
  const fade = t => t * t * t * (t * (t * 6 - 15) + 10);
  const lerp = (a, b, t) => a + (b - a) * t;
  const v = (x, y) => g[P[(x & 255) + P[y & 255]]];
  const noise = (x, y) => {
    const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi, u = fade(xf), w = fade(yf);
    return lerp(lerp(v(xi, yi), v(xi + 1, yi), u), lerp(v(xi, yi + 1), v(xi + 1, yi + 1), u), w);
  };
  const fbm = (x, y, o = 5) => { let a = 0.5, f = 1, s = 0; for (let i = 0; i < o; i++) { s += a * noise(x * f, y * f); f *= 2; a *= 0.5; } return s; };
  return { noise, fbm };
}

function toNormalCanvas(h, w, hh, strength) {
  const c = document.createElement('canvas'); c.width = w; c.height = hh;
  const x = c.getContext('2d'), id = x.createImageData(w, hh), d = id.data;
  for (let j = 0; j < hh; j++) for (let i = 0; i < w; i++) {
    const l = h[j * hh * 0 + j * w + ((i - 1 + w) % w)], r = h[j * w + ((i + 1) % w)];
    const u = h[((j - 1 + hh) % hh) * w + i], dn = h[((j + 1) % hh) * w + i];
    let nx = (l - r) * strength, ny = (dn - u) * strength, nz = 1;
    const n = Math.hypot(nx, ny, nz); nx /= n; ny /= n; nz /= n;
    const k = (j * w + i) * 4; d[k] = (nx * 0.5 + 0.5) * 255; d[k + 1] = (ny * 0.5 + 0.5) * 255; d[k + 2] = (nz * 0.5 + 0.5) * 255; d[k + 3] = 255;
  }
  x.putImageData(id, 0, 0); return c;
}

// Lapisan batuan: pita ber-gelombang, retakan, butiran. Mengembalikan {map, normalMap, roughnessMap}.
export function strataTexture(opts = {}) {
  const W = opts.w || 1024, H = opts.h || 1024, N = makeNoise(opts.seed || 7), R = rng((opts.seed || 7) * 31);
  const pal = opts.palette || [[160, 128, 92], [104, 92, 80], [186, 150, 104], [84, 80, 76], [140, 104, 70], [196, 172, 134], [120, 96, 74]];
  const bands = opts.bands || 22, h = new Float32Array(W * H);
  const layerCol = [...Array(bands + 3).keys()].map(() => pal[Math.floor(R() * pal.length)]);
  const layerRough = [...Array(bands + 3).keys()].map(() => 0.75 + R() * 0.2);
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const x = c.getContext('2d'), id = x.createImageData(W, H), d = id.data;
  for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
    const u = i / W, v = j / H;
    const warp = N.fbm(u * 1.5, v * 1.5, 3) * 0.035 + N.fbm(u * 6, v * 3, 3) * 0.008;
    const b = (v + warp) * bands, li = Math.floor(b), f = b - li;
    const col = layerCol[((li % layerCol.length) + layerCol.length) % layerCol.length], grain = N.fbm(u * 60, v * 60, 4), mid = N.fbm(u * 14, v * 14, 4);
    const edge = Math.min(f, 1 - f);
    let shade = 0.9 + grain * 0.3 + mid * 0.18 - (edge < 0.02 ? 0.12 : 0) + (li % 2 ? 0.1 : -0.08) + N.fbm(u * 3, v * 30, 3) * 0.25;
    // retakan: ridged noise
    const rd = Math.abs(N.noise(u * 30 + v * 9, v * 6)); const crack = (rd < 0.012 && N.noise(u * 2.5, v * 4) > 0.2) ? 1 : 0;
    if (crack) shade *= 0.45;
    const k = (j * W + i) * 4; d[k] = Math.min(255, col[0] * shade); d[k + 1] = Math.min(255, col[1] * shade); d[k + 2] = Math.min(255, col[2] * shade); d[k + 3] = 255;
    h[j * W + i] = grain * 0.5 + mid * 0.6 + (crack ? -0.9 : 0) + (edge < 0.02 ? -0.12 : 0);
  }
  x.putImageData(id, 0, 0);
  const map = new THREE.CanvasTexture(c); map.colorSpace = THREE.SRGBColorSpace;
  const nm = new THREE.CanvasTexture(toNormalCanvas(h, W, H, opts.nstrength || 2.2));
  for (const t of [map, nm]) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 4; }
  return { map, normalMap: nm };
}

// Permukaan bor: batu hancur kasar bergaris
export function boreTexture(seed = 3) {
  const W = 512, H = 512, N = makeNoise(seed), h = new Float32Array(W * H);
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const x = c.getContext('2d'), id = x.createImageData(W, H), d = id.data;
  for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
    const u = i / W, v = j / H, g = N.fbm(u * 24, v * 24, 5), s = Math.sin((v + N.fbm(u * 6, v * 6, 3) * 0.2) * 90) * 0.12;
    const val = 0.5 + g * 0.5 + s; const k = (j * W + i) * 4;
    d[k] = 98 * val * 1.5; d[k + 1] = 88 * val * 1.5; d[k + 2] = 78 * val * 1.5; d[k + 3] = 255; h[j * W + i] = g + s;
  }
  x.putImageData(id, 0, 0);
  const map = new THREE.CanvasTexture(c); map.colorSpace = THREE.SRGBColorSpace;
  const nm = new THREE.CanvasTexture(toNormalCanvas(h, W, H, 3.0));
  for (const t of [map, nm]) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 4; }
  return { map, normalMap: nm };
}

// Beton: butir halus + bercak
export function concreteTexture(seed = 5) {
  const W = 512, H = 512, N = makeNoise(seed), h = new Float32Array(W * H);
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const x = c.getContext('2d'), id = x.createImageData(W, H), d = id.data;
  for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
    const u = i / W, v = j / H, g = N.fbm(u * 80, v * 80, 4), b = N.fbm(u * 5, v * 5, 3);
    const val = 0.74 + g * 0.22 + b * 0.18; const k = (j * W + i) * 4;
    d[k] = 168 * val; d[k + 1] = 166 * val; d[k + 2] = 160 * val; d[k + 3] = 255; h[j * W + i] = g * 0.8;
  }
  x.putImageData(id, 0, 0);
  const map = new THREE.CanvasTexture(c); map.colorSpace = THREE.SRGBColorSpace;
  const nm = new THREE.CanvasTexture(toNormalCanvas(h, W, H, 1.2));
  for (const t of [map, nm]) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 4; }
  return { map, normalMap: nm };
}
