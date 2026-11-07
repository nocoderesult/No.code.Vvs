# Worker Serverless RunPod pentru pozele lui Iness (ComfyUI + Krea 2 + LoRA d4ria).
# Modelele NU sunt în imagine: vin de pe Network Volume (vezi extra_model_paths.yaml).
# Bază: worker-ul oficial RunPod, varianta CUDA 12.8 (merge și pe plăcile Blackwell).
FROM runpod/worker-comfyui:5.10.0-base-cuda12.8.1

# Nodurile custom din workflow-ul krea2_studio (nume din registry.comfy.org).
RUN comfy-node-install rgthree-comfy comfyui-impact-pack comfyui-impact-subpack comfyui-propost

# Căile modelelor pe Network Volume (montat la /runpod-volume pe Serverless).
COPY extra_model_paths.yaml /comfyui/extra_model_paths.yaml
