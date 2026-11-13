#!/bin/bash
# Instalează workflow-ul MATRIX Krea 2 V1 (github.com/JsonMatrixLab/MATRIX-Krea2-Workflow, Apache-2.0)
# pe un pod ComfyUI cu volumul global la /workspace-global. Se poate rula de mai multe ori:
# ce e deja pe volum nu se mai descarcă. comfy_global.sh îl rulează la fiecare pornire.
set -u
G="${GLOBAL_DIR:-/workspace-global}"
C="${COMFY_DIR:-/workspace/runpod-slim/ComfyUI}"
REL="https://github.com/JsonMatrixLab/MATRIX-Krea2-Workflow/releases/download/v1.1.0/MATRIX-Krea2-V1.zip"
RGTHREE_COMMIT="2c5342a8cb0eaecaabf61435a5f37dd594c510ba"
M="$G/models"

# fișier | URL | SHA-256  (din MODELS.md al release-ului 1.1.0)
MODELE='diffusion_models/krea2_turbo_fp8_scaled.safetensors|https://huggingface.co/Comfy-Org/Krea-2/resolve/952f49d49653cb42e7d6cf7cbfad74738073ec7d/diffusion_models/krea2_turbo_fp8_scaled.safetensors|eb4dd8c612cfd10f64f25b057e6e6bbcb5737c94a7372177e456dbf7579502f1
text_encoders/qwen3vl_4b_bf16.safetensors|https://huggingface.co/Comfy-Org/Qwen3-VL/resolve/5529a3c630b649351fb72d8c251577b5962371d8/text_encoders/qwen3vl_4b_bf16.safetensors|36f3ff447ef59201722e8f9ce6020c9819fdcfba6aa2608c4e09b1c0ce114e34
vae/wan_2.1_vae.safetensors|https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/617a7633e636506f850e043bc4605f290a466a8e/split_files/vae/wan_2.1_vae.safetensors|2fc39d31359a4b0a64f55876d8ff7fa8d780956ae2cb13463b0223e15148976b
ultralytics/bbox/Eyeful_v2-Individual.pt|https://huggingface.co/Bryan32/Adetailer/resolve/701874bdc5ebc0db00543eb867dd0e778db93d1c/Eyeful_v2-Individual.pt|278fee230b1be01cfb8c47c3f9ad7118c7aa33149a2249b80cea4da236361fbe
sams/sam_vit_b_01ec64.pth|https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth|ec2df62732614e57411cdcf32a23ffdf28910380d03139ee0f4fcbe91eb8c912
onnx/rembg/u2net_human_seg.onnx|https://huggingface.co/jellybox/u2net-human-seg/resolve/736b768145e597134968bde9ace5bf8fd19ffa8c/u2net_human_seg.onnx|01eb6a29a5c4d8edb30b56adad9bb3a2a0535338e480724a213e0acfd2d1c73c
onnx/human-parts/deeplabv3p-resnet50-human.onnx|https://huggingface.co/Metal3d/deeplabv3p-resnet50-human/resolve/b9b594a494958301fe7bfe50cc30f1976e1073ce/deeplabv3p-resnet50-human.onnx|a6e823a82da10ba24c29adfb544130684568c46bfac865e215bbace3b4035a71'

echo "== Modele MATRIX pe volumul global"
echo "$MODELE" | while IFS='|' read -r rel url sha; do
  dest="$M/$rel"; ok="$dest.sha256ok"
  if [ -s "$dest" ] && [ -f "$ok" ]; then echo "✓ $rel"; continue; fi
  mkdir -p "$(dirname "$dest")"
  echo "Descarc $rel ..."
  curl -fsSL --retry 5 --retry-delay 5 -o "$dest" "$url" || { echo "❌ descărcare eșuată: $rel"; rm -f "$dest"; continue; }
  if [ "$(sha256sum "$dest" | cut -d' ' -f1)" = "$sha" ]; then echo ok > "$ok"; echo "✓ $rel (SHA-256 corect)"
  else echo "❌ SHA-256 greșit la $rel, îl șterg"; rm -f "$dest"; fi
done

echo "== Workflow și noduri"
Z="$G/instalari/MATRIX-Krea2-V1.zip"
mkdir -p "$G/instalari"
[ -s "$Z" ] || curl -fsSL --retry 5 -o "$Z" "$REL" || { echo "❌ nu pot descărca $REL"; exit 1; }
T="$(mktemp -d)"; python3 -m zipfile -e "$Z" "$T"   # unzip nu e în imagine
R="$T/MATRIX-Krea2-V1"
mkdir -p "$G/comfyui/workflows"
cp "$R/MATRIX-Krea2-V1.json" "$G/comfyui/workflows/MATRIX-Krea2-V1.json"
cp "$R/API/MATRIX-Krea2-V1.api.json" "$G/instalari/MATRIX-Krea2-V1.api.json"

if [ ! -f "$C/custom_nodes/MATRIX-LAB-Nodes/MANIFEST.json" ]; then
  mkdir -p "$T/n" && python3 -m zipfile -e "$R/Custom-Nodes/MATRIX-LAB-Nodes-0.4.0.zip" "$T/n"
  cp -r "$T/n/MATRIX-LAB-Nodes" "$C/custom_nodes/MATRIX-LAB-Nodes" && echo "✓ MATRIX-LAB-Nodes 0.4.0" \
    || echo "❌ MATRIX-LAB-Nodes nu s-a putut copia"
fi
if [ ! -d "$C/custom_nodes/rgthree-comfy" ]; then
  git clone -q https://github.com/rgthree/rgthree-comfy "$C/custom_nodes/rgthree-comfy" \
    && git -C "$C/custom_nodes/rgthree-comfy" checkout -q "$RGTHREE_COMMIT" && echo "✓ rgthree-comfy"
fi
rm -rf "$T"

VENV="$(ls -d "$C"/.venv-* 2>/dev/null | head -1)"
if [ -n "$VENV" ] && ! "$VENV/bin/python" -c "import onnxruntime, ultralytics, segment_anything" 2>/dev/null; then
  echo "Instalez pachetele Python pentru piele și ochi..."
  # constrângerile imaginii păstrează Torch/CUDA neatinse
  PIP_CONSTRAINT=/opt/comfyui-runtime-constraints.txt "$VENV/bin/python" -m pip install -q \
    -r "$C/custom_nodes/MATRIX-LAB-Nodes/requirements.txt" \
    onnxruntime==1.29.0 ultralytics==8.4.142 segment-anything==1.0 2>&1 | grep -E "^ERROR" || true
fi
echo "✓ MATRIX Krea 2 gata"
