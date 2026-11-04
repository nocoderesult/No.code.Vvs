#!/bin/bash
# Installs what .claude/skills/video-editor needs in Claude Code cloud sessions.
# Idempotent: each step is skipped when its dependency is already present.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

PIP="pip install --quiet --break-system-packages --root-user-action=ignore"

# System tools: ffmpeg (with libass) and the Inter font used for burned-in captions.
missing_apt=()
command -v ffmpeg >/dev/null 2>&1 || missing_apt+=(ffmpeg)
fc-list : family 2>/dev/null | grep -q "^Inter" || missing_apt+=(fonts-inter)
if [ ${#missing_apt[@]} -gt 0 ]; then
  apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "${missing_apt[@]}"
fi

# Python packages used by the skill's scripts (and piper-tts by scripts/dev/ self-tests).
if ! python3 -c "import faster_whisper, cv2, scenedetect, numpy, PIL, opentimelineio, piper" 2>/dev/null \
   || ! python3 -c "import opentimelineio as o; a={x.name for x in o.plugins.ActiveManifest().adapters}; assert {'fcp_xml','fcpx_xml','cmx_3600'} <= a" 2>/dev/null \
   || ! command -v auto-editor >/dev/null 2>&1; then
  $PIP faster-whisper opencv-python-headless scenedetect numpy pillow auto-editor piper-tts \
       opentimelineio otio-fcp-adapter otio-fcpx-xml-adapter otio-cmx3600-adapter
fi

# auto-editor fetches its platform binary on first run.
auto-editor --version >/dev/null 2>&1 || true

# Pre-fetch the default Whisper model (~1.6 GB) so the first transcription doesn't wait on it.
python3 -c "from faster_whisper import download_model; download_model('large-v3-turbo')" >/dev/null 2>&1 \
  || echo "warning: could not pre-download Whisper large-v3-turbo; transcribe.py will fetch it on first use" >&2
