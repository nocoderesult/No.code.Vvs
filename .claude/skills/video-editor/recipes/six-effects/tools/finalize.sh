#!/bin/bash
# Join the ProRes parts, mux the master audio and encode the deliverables.
# usage: finalize.sh reel3_dir out_dir
set -euo pipefail
R="$1"; OUT="$2"
FF=${FFMPEG:-ffmpeg}
mkdir -p "$OUT"
cd "$R/render"
printf "file 'part%d.mov'\n" 0 1 2 3 > parts.txt
"$FF" -v error -y -f concat -safe 0 -i parts.txt -c copy master_prores.mov

TAGS=(-color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv)
# 4K: H.264 High 5.1, quality-capped VBR (IG/TikTok/YouTube accept it; iPhone plays it natively)
"$FF" -v error -y -i master_prores.mov -i "$R/work/mix_music.wav" -map 0:v -map 1:a \
  -vf "format=yuv420p" -c:v libx264 -preset slow -profile:v high -level 5.1 -crf 15 -maxrate 45M -bufsize 90M \
  -g 30 -bf 2 -tune film "${TAGS[@]}" -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest \
  "$OUT/Reel3_4K_2160x3840.mp4"
# 1080p for direct upload (Lanczos down from the 4K master)
for v in music nomusic; do
  name="Reel3_1080p.mp4"; [ "$v" = nomusic ] && name="Reel3_1080p_fara_muzica.mp4"
  "$FF" -v error -y -i master_prores.mov -i "$R/work/mix_$v.wav" -map 0:v -map 1:a \
    -vf "scale=1080:1920:flags=lanczos:in_color_matrix=bt709:out_color_matrix=bt709,format=yuv420p" \
    -c:v libx264 -preset slow -profile:v high -level 4.2 -crf 16 -maxrate 20M -bufsize 40M -g 30 -bf 2 -tune film \
    "${TAGS[@]}" -c:a aac -b:a 256k -ar 48000 -movflags +faststart -shortest "$OUT/$name"
done
ls -la "$OUT"
