#!/usr/bin/env bash
# Transformă video-ul de intrare în cadrele pe care le derulează scroll-ul (format telefon, 9:16).
#
#   scripts/make-sequence.sh intrare.mp4
#
# Un video orizontal e decupat automat pe centru la 9:16. Reglaje: FRAMES (implicit 110),
# QUALITY (calitatea WebP, implicit 74).
set -euo pipefail

IN="${1:?Folosire: scripts/make-sequence.sh intrare.mp4}"
OUT="$(cd "$(dirname "$0")/.." && pwd)/public/assets/seq"
FRAMES="${FRAMES:-110}"
QUALITY="${QUALITY:-74}"

duration=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
fps=$(python3 -c "print(round($FRAMES / $duration, 4))")

mkdir -p "$OUT/mobile"
find "$OUT/mobile" -name '*.webp' -delete

ffmpeg -nostdin -v error -i "$IN" \
  -vf "fps=$fps,crop='min(iw,ih*9/16)':'min(ih,iw*16/9)',scale=720:1280:flags=lanczos" \
  -frames:v "$FRAMES" -c:v libwebp -quality "$QUALITY" -compression_level 6 "$OUT/mobile/%04d.webp"

count=$(find "$OUT/mobile" -name '*.webp' | wc -l | tr -d ' ')
cat > "$OUT/manifest.json" <<EOF
{
  "mobile": { "path": "assets/seq/mobile/", "count": $count, "ext": "webp", "pad": 4 }
}
EOF

echo "Gata: $count cadre, $(du -sh "$OUT/mobile" | cut -f1)"
