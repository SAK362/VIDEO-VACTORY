# Mesin render 3D WebGL (Phase 1)

Render 1080x1920 @ 30 fps di GitHub Actions (Chrome headless + SwiftShader). Tanpa token Claude.

- `engine.html` : mesin 3D + overlay (panel judul, subtitle arsir per kata, label, Curio berbicara, FAKTA UNIK).
- `align_whisper.py` : Whisper (prompt = naskah) -> wordTimes; `make_timing.py` merapikan (geser kata keluar dari jeda) -> `timing.js` + mulut Curio.
- `make_timing.py` : cadangan bila `align_envelope.py` gagal (wordTimes Whisper atau perkiraan).
- `clean_audio.py` : jeda > 0,7 dtk -> 0,55 dtk, loudnorm -14 LUFS.
- `render_webgl.py` : `meta | chunk i n out.mp4 | still T`.
- `diesel_props.json` : contoh props topik 0008 (satu adegan = satu kalimat).
- Workflow: `.github/workflows/render-webgl.yml` (input sama dengan `render.yml`; di n8n ganti nama file workflow yang dipanggil).

Batas Phase 1: urutan shot/kamera di `engine.html` (SHOTS) masih khusus topik diesel (14 kalimat).
Phase 2: pustaka objek + spesifikasi adegan JSON agar topik apa pun otomatis.
Uji lokal: salin `curio.png` ke folder ini, siapkan `work/props.json` + `public/voiceover.wav`, jalankan `make_timing.py`, lalu `render_webgl.py still 20`.
