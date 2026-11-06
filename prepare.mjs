// Mengunduh props.json dan voiceover.wav dari Google Drive (file dibagikan "siapa saja yang punya tautan"),
// lalu menghitung durasi suara dan menulis work/props.json untuk Remotion.
import fs from 'node:fs';

const {PROPS_ID, AUDIO_ID, QUALITY = 'standard', LANG_CODE = 'en', PROJECT = ''} = process.env;
if (!PROPS_ID || !AUDIO_ID) {
  console.error('PROPS_ID dan AUDIO_ID wajib diisi.');
  process.exit(1);
}

async function download(id) {
  const urls = [
    `https://drive.usercontent.google.com/download?id=${id}&export=download&confirm=t`,
    `https://drive.google.com/uc?export=download&id=${id}`,
  ];
  let lastError = 'tidak ada respons';
  for (const url of urls) {
    for (let attempt = 1; attempt <= 3; attempt++) {
      try {
        const res = await fetch(url, {redirect: 'follow'});
        if (!res.ok) {
          lastError = `HTTP ${res.status} dari ${new URL(url).host}`;
          continue;
        }
        const buf = Buffer.from(await res.arrayBuffer());
        const head = buf.subarray(0, 20).toString('utf8').toLowerCase();
        if (head.includes('<!doctype') || head.includes('<html')) {
          lastError = 'Drive mengirim halaman HTML (file belum dibagikan publik?)';
          continue;
        }
        return buf;
      } catch (e) {
        lastError = String(e);
      }
      await new Promise((r) => setTimeout(r, 2000 * attempt));
    }
  }
  throw new Error(`Gagal mengunduh file Drive ${id}: ${lastError}`);
}

function wavSeconds(buf) {
  if (buf.subarray(0, 4).toString() !== 'RIFF' || buf.subarray(8, 12).toString() !== 'WAVE') {
    throw new Error('voiceover bukan file WAV yang valid');
  }
  // cari chunk "fmt " dan "data"
  let pos = 12;
  let byteRate = 0;
  let dataSize = 0;
  while (pos + 8 <= buf.length) {
    const id = buf.subarray(pos, pos + 4).toString();
    const size = buf.readUInt32LE(pos + 4);
    if (id === 'fmt ') byteRate = buf.readUInt32LE(pos + 16);
    if (id === 'data') {
      dataSize = Math.min(size, buf.length - (pos + 8));
      break;
    }
    pos += 8 + size + (size % 2);
  }
  if (!byteRate || !dataSize) throw new Error('header WAV tidak lengkap');
  return dataSize / byteRate;
}

fs.mkdirSync('work', {recursive: true});
fs.mkdirSync('public', {recursive: true});
fs.mkdirSync('out', {recursive: true});

const propsBuf = await download(PROPS_ID);
const audioBuf = await download(AUDIO_ID);

const props = JSON.parse(propsBuf.toString('utf8'));
const seconds = wavSeconds(audioBuf);
fs.writeFileSync('public/voiceover.wav', audioBuf);

if (!Array.isArray(props.scenes) || props.scenes.length === 0) {
  throw new Error('props.json tidak berisi scenes');
}

const out = {
  ...props,
  lang: props.lang || LANG_CODE,
  project: props.project || PROJECT,
  audioSeconds: Number(seconds.toFixed(2)),
  audioFile: 'voiceover.wav',
  quality: QUALITY,
};
fs.writeFileSync('work/props.json', JSON.stringify(out));
console.log(`Props siap. Adegan: ${props.scenes.length}, durasi suara: ${seconds.toFixed(1)} detik`);
