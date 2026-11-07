# VIDEO-VACTORY (CurioSphere Video Factory)

Repo ini merender video explainer 3D low-poly "cutaway" (9:16) dengan Remotion di GitHub Actions (gratis untuk repo publik).
Dipicu otomatis oleh n8n (workflow "FULL OTOMATIS CURIOSPHERE"). Kamu tidak perlu menjalankan apa pun secara manual.

## Alur
1. n8n memanggil workflow `render.yml` (workflow_dispatch) dengan: project, row_no, lang, folder_id, props_id, audio_id, upload_url, callback_url, quality.
2. `scripts/prepare.mjs` mengunduh `props.json` + `voiceover.wav` dari Google Drive (tautan publik).
3. Remotion merender `CurioVideo` menjadi `out/video.mp4`.
4. MP4 dikirim ke Google Drive lewat `upload_url` (sesi unggah yang dibuat n8n).
5. Hasil dilaporkan ke n8n lewat `callback_url` dengan header `X-Curio-Key`.

## Pengaturan wajib (sekali saja)
Repo → Settings → Secrets and variables → Actions → New repository secret
- Name: `CALLBACK_KEY`
- Secret: kunci acak yang diberikan di chat (harus sama dengan di n8n)

## Kualitas
- `standard` : 1080x1920 penuh
- `fast`     : skala 0.6667 (lebih cepat, lebih ringan)

## Uji lokal (opsional)
```
npm install
npm run studio
```
