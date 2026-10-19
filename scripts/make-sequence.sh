#!/usr/bin/env bash
# Transformă video-ul de intrare în cadrele pe care le derulează scroll-ul.
#
#   scripts/make-sequence.sh intrare.mp4                       # un singur video (orizontal)
#   scripts/make-sequence.sh intrare.mp4 intrare-vertical.mp4  # + varianta pentru telefon
#
# Fără video vertical, varianta de telefon e decupată din centrul celui orizontal.
# Reglaje: FRAMES (cadre desktop, implicit 150), FRAMES_MOBILE (implicit 120).
set -euo pipefail

IN="${1:?Folosire: scripts/make-sequence.sh intrare.mp4 [intrare-vertical.mp4]}"
IN_MOBILE="${2:-}"
OUT="$(cd "$(dirname "$0")/.." && pwd)/public/assets/seq"
FRAMES="${FRAMES:-150}"
FRAMES_MOBILE="${FRAMES_MOBILE:-120}"

duration() { ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"; }
fps_for() { python3 -c "print(round($1 / $(duration "$2"), 4))"; }

rm -rf "$OUT"
mkdir -p "$OUT/desktop" "$OUT/mobile"

echo "Desktop: $FRAMES cadre…"
ffmpeg -v error -i "$IN" \
  -vf "fps=$(fps_for "$FRAMES" "$IN"),scale=1600:-2:flags=lanczos" \
  -frames:v "$FRAMES" -c:v libwebp -quality 72 -compression_level 6 "$OUT/desktop/%04d.webp"

echo "Telefon: $FRAMES_MOBILE cadre…"
if [[ -n "$IN_MOBILE" ]]; then
  ffmpeg -v error -i "$IN_MOBILE" \
    -vf "fps=$(fps_for "$FRAMES_MOBILE" "$IN_MOBILE"),scale=900:-2:flags=lanczos" \
    -frames:v "$FRAMES_MOBILE" -c:v libwebp -quality 66 -compression_level 6 "$OUT/mobile/%04d.webp"
else
  ffmpeg -v error -i "$IN" \
    -vf "fps=$(fps_for "$FRAMES_MOBILE" "$IN"),crop='min(iw,ih*9/16)':ih,scale=900:-2:flags=lanczos" \
    -frames:v "$FRAMES_MOBILE" -c:v libwebp -quality 66 -compression_level 6 "$OUT/mobile/%04d.webp"
fi

count() { find "$1" -name '*.webp' | wc -l | tr -d ' '; }
cat > "$OUT/manifest.json" <<EOF
{
  "desktop": { "path": "assets/seq/desktop/", "count": $(count "$OUT/desktop"), "ext": "webp", "pad": 4 },
  "mobile": { "path": "assets/seq/mobile/", "count": $(count "$OUT/mobile"), "ext": "webp", "pad": 4 }
}
EOF

echo "Gata:"
du -sh "$OUT/desktop" "$OUT/mobile"
cat "$OUT/manifest.json"
