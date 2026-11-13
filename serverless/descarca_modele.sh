#!/bin/bash
# Descarcă pe volumul global modelele Krea 2 de care are nevoie Serverless (~18,6 GB).
# Rulezi pe un pod care are volumul global la /workspace-global:
#   bash descarca_modele.sh
# Sursa: https://huggingface.co/Comfy-Org/Krea-2 (licența Krea 2 Community License).
set -e
G="${GLOBAL_DIR:-/workspace-global}"
[ -d "$G" ] || { echo "Nu găsesc volumul global la $G."; exit 1; }
R="https://huggingface.co/Comfy-Org/Krea-2/resolve/main"

# Folderele unet/ și clip/ le citesc și ComfyUI de pe pod, și worker-ul oficial de Serverless.
ia() {  # ia <folder pe Hugging Face> <fișier> <folder pe volum>
  local dest="$G/models/$3/$2"
  mkdir -p "$G/models/$3" "$G/models/loras"
  if [ -s "$dest" ]; then echo "✓ $2 e deja pe volum"; return; fi
  echo "Descarc $2 ..."
  # direct în fișierul final: volumul global nu garantează redenumiri
  curl -fL --retry 5 --retry-delay 5 -o "$dest" "$R/$1/$2" || { rm -f "$dest"; exit 1; }
  echo "✓ $2"
}

ia diffusion_models krea2_raw_fp8_scaled.safetensors unet   # 13,1 GB
ia text_encoders    qwen3vl_4b_fp8_scaled.safetensors clip  # 5,2 GB
ia vae              qwen_image_vae.safetensors vae      # 0,25 GB

echo
echo "Gata. Modelele sunt în $G/models (unet, clip, vae). LoRA-urile tale le pui în $G/models/loras."
du -sh "$G/models" 2>/dev/null || true
