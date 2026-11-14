# Kit render BeYourBest (dipakai semua akun Claude)

Alur per video (lihat ATURAN_BEYOURBEST.txt):
1. Taruh `NNNN.wav` + `NNNN_narasi.txt` di `beyourbest/align/`, push. Workflow `align-beyourbest` menjalankan Whisper dan menyimpan `NNNN_heard.json` (±3 menit). `gh run list -R SAK362/VIDEO-VACTORY` untuk memantau, lalu `git pull`.
2. `wal.py`: cocokkan kata Whisper ke kata naskah per huruf (memakai `webgl/align_whisper.py: align_tokens`) -> `wtimes.json`. Lalu rapatkan awal kata ke awal suara (silencedetect -35 dB, d=0.10, potongan >= 0.25 dtk, geser maks 0,5 dtk).
3. `audio3.py`: rapikan jeda > 0,7 dtk jadi 0,55 dtk, loudnorm -14 LUFS, tulis `timing.json` (kata, kalimat, envelope mulut).
4. Adegan: `scenes_part.py` (adegan per topik, ditulis ulang tiap video, pindah adegan memakai awal unit/kalimat) + `gen_build.py` -> `build2.py` memakai fungsi gambar di `build_0001_lib.py` (boy, room, bubble, cloud, bulb, chip, mascot, dst).
5. Render 2 potongan paralel: `python3 build2.py chunk 0 2 ch0.mp4` dan `chunk 1 2 ch1.mp4` (±8 menit, 3300 frame), concat `-c copy`, tambah suara `-c:v copy -c:a aac`.
6. Thumbnail: `thumb.py`. Push mp4 + narasi + thumbnail ke `beyourbest/outbox/`.

Catatan: path di skrip memakai /home/claude/beyourbest/v2; sesuaikan bila folder kerja berbeda. Butuh rsvg-convert, ffmpeg, Poppins, python3 pillow numpy.
