# VIDEO-VACTORY (mesin render "studio")

Render video CurioSphere memakai Python (numpy + Pillow + ffmpeg), tanpa Remotion/Chrome.

- `studio/core.py`    : z-buffer 3D, teks atas, label, kartu angka, subtitle per kata, Curio, watermark
- `studio/render.py`  : `meta` / `chunk` / `stills`
- `studio/kits/*.py`  : dunia 3D per topik (pompa, eskalator, lift, petir, kulkas) dengan daftar SHOT
- `prepare.mjs`       : unduh props.json + voiceover.wav dari Drive
- `align.py`          : cocokkan waktu tiap kata dengan suara (faster-whisper)
- `.github/workflows/render.yml` : prep -> 4 potongan paralel -> gabung + suara -> Drive -> lapor n8n

Coba di komputer sendiri:
    pip install numpy pillow
    STUDIO_WIDTH=720 python -m studio.render stills contoh.json hasil/
