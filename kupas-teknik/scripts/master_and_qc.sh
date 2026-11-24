#!/usr/bin/env bash
# Master encode + full layered QC gate (G1–G6). Run from anywhere.
# Usage: bash master_and_qc.sh <episode_dir> <raw.mp4> <tag> <subs.json>
#   episode_dir must contain shots.json, episode.json, 05_audio/vo_full.wav, 05_audio/timeline.json
set -u
E="$(cd "$1" && pwd)"; RAW="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"; TAG="$3"; SUBS="$(cd "$(dirname "$4")" && pwd)/$(basename "$4")"
S="$(cd "$(dirname "$0")" && pwd)"; cd "$E"
EPID=$(python -I -c "import json;e=json.load(open('episode.json',encoding='utf-8'));print(e['episode']+'_'+e['slug'])")
M="06_edit/${EPID}_${TAG}_MASTER.mp4"; Q="07_qc/${TAG}"; mkdir -p "$Q" 06_edit
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$RAW")
echo "== encode master (180° motion blur tmix 1-2-1, grain, vignette, VO ≈ -14 LUFS)"
ffmpeg -v error -y -i "$RAW" -i 05_audio/vo_full.wav -filter_complex \
 "[0:v]tmix=frames=3:weights='1 2 1',eq=contrast=1.04:saturation=1.07,vignette=PI/7,noise=alls=3:allf=t,scale=out_range=tv,format=yuv420p[v];[1:a]aresample=192000,volume=4.1dB,alimiter=limit=0.8:level=false:attack=1:release=60,aresample=48000,apad=whole_dur=${DUR},aformat=channel_layouts=stereo[a]" \
 -map "[v]" -map "[a]" -t "$DUR" -c:v libx264 -profile:v high -level 4.2 -preset slow -crf 20 -pix_fmt yuv420p -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
 -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$M" || { echo "ENCODE FAIL"; exit 1; }
echo "== G1 duration gate (105–150 s)"
python -I -c "d=float('$DUR');print(f'{d:.2f}s','PASS' if 105<=d<=150 else 'FAIL')"
echo "== G2 stream spec (must be 1080x1920, 30/1, h264 High, yuv420p, aac 48k stereo)"
ffprobe -v error -show_entries stream=codec_name,profile,width,height,r_frame_rate,nb_frames,pix_fmt,color_range,sample_rate,channels:format=duration,size -of compact "$M"
echo "== G3 black / freeze"
ffmpeg -hide_banner -i "$M" -vf "blackdetect=d=0.2:pix_th=0.10,freezedetect=n=0.002:d=1.5" -an -f null - 2>&1 | grep -E "black_start|freeze_start" || echo "0 black, 0 freeze -> PASS"
echo "== G4 glitch detector on MASTER (target 0 flags)"
python -I "$S/qc_video_glitch.py" "$M" 05_audio/timeline.json "$Q/glitch" 2>&1 | grep -vE "^picked"
echo "== G5 contact sheet (review manually!)"
ffmpeg -v error -y -i "$M" -vf "fps=12/${DUR},scale=270:480,tile=4x3" -frames:v 1 "$Q/contact_sheet.jpg" && echo "$Q/contact_sheet.jpg"
echo "== G6 voice-over layers L1–L6"
python -I "$S/qc_vo_layers.py" . "$M" "$SUBS" 2>&1 | grep -viE "warn"
