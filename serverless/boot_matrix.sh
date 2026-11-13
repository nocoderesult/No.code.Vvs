#!/bin/bash
# Pregătește worker-ul oficial runpod/worker-comfyui pentru workflow-ul MATRIX Krea 2,
# fără imagine proprie: nodurile vin de pe volumul global, pachetele Python din PyPI.
# Endpoint-ul îl pornește cu: bash /runpod-volume/boot_matrix.sh && exec /start.sh
set -u
V=/runpod-volume
T0=$(date +%s)
echo "boot_matrix: start"

# 1. Nodurile MATRIX-LAB-Nodes + rgthree-comfy (arhivate pe volum de pe pod)
if [ -f "$V/instalari/noduri_serverless.tar" ]; then
  tar -xf "$V/instalari/noduri_serverless.tar" -C /comfyui/custom_nodes
  echo "boot_matrix: noduri copiate ($(( $(date +%s) - T0 )) s)"
else
  echo "boot_matrix: lipsește $V/instalari/noduri_serverless.tar" >&2
fi

# 2. Pachetele pentru piele și ochi; Torch-ul imaginii rămâne neatins
PY=$(command -v python3)
"$PY" -m pip install -q --no-cache-dir onnxruntime==1.29.0 ultralytics==8.4.142 segment-anything==1.0 scipy \
  "torch==$("$PY" -c 'import torch;print(torch.__version__)')" 2>&1 | grep -E "^ERROR" || true
echo "boot_matrix: pachete instalate ($(( $(date +%s) - T0 )) s)"

# 3. Unde sunt modelele pe volumul global
cat > /comfyui/extra_model_paths.yaml <<'EOF'
volum_global:
  base_path: /runpod-volume
  checkpoints: models/checkpoints/
  diffusion_models: |
    models/diffusion_models/
    models/unet/
  text_encoders: |
    models/text_encoders/
    models/clip/
  vae: models/vae/
  loras: models/loras/
  upscale_models: models/upscale_models/
  sams: models/sams/
  ultralytics: models/ultralytics/
  ultralytics_bbox: models/ultralytics/bbox/
  ultralytics_segm: models/ultralytics/segm/
  onnx: models/onnx/
EOF
echo "boot_matrix: gata în $(( $(date +%s) - T0 )) s"
