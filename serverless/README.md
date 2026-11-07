# Pozele lui Iness pe RunPod Serverless (fără pod pornit)

Cererea pleacă din chat (sau de oriunde), RunPod pornește singur o placă video, generează, întoarce poza și se oprește. Se plătesc doar secundele de lucru; cu 0 workeri activi, când nu generezi nu plătești nimic pentru GPU (stocarea Network Volume se plătește separat, lunar).

| Fișier | Ce face |
|---|---|
| `Dockerfile` | Worker-ul oficial `runpod/worker-comfyui:5.10.0-base-cuda12.8.1` + nodurile din `krea2_studio` (rgthree, Impact Pack + Subpack, ProPost). Fără modele în imagine. |
| `extra_model_paths.yaml` | Unde caută ComfyUI modelele pe Network Volume: întâi în `runpod-slim/ComfyUI/models` (volumul pod-ului de acum), apoi în `models/` (volum nou). |
| `workflows/iness_krea2_raw_api.json` | Workflow-ul de bază în format API: Krea 2 raw + LoRA `d4ria` → poză 896×1152. |
| `genereaza.py` | `info` (volume, endpoint-uri, pod-uri din cont) și `poza "scena"` (trimite cererea, așteaptă, salvează PNG-ul). Doar biblioteca standard Python. |

## Instalare (o singură dată)

### 1. Modelele pe un Network Volume
Serverless citește modelele doar de pe un **Network Volume** (montat la `/runpod-volume`).

- RunPod → **Storage**. Dacă volumul pod-ului de acum apare acolo ca Network Volume, notează-i centrul de date: îl folosim direct, fără copiere (ComfyUI e în `runpod-slim/ComfyUI`).
- Dacă nu apare: **New Network Volume**, ~80 GB, într-un centru de date cu plăci de 48 GB libere. Pornești un pod mic cu volumul ăsta atașat (montat la `/workspace`) și copiezi doar ce trebuie:

| Fișier | Folder pe volumul nou |
|---|---|
| `krea2_raw_bf16.safetensors` | `models/diffusion_models/` |
| `qwen3vl_4b_fp8_scaled.safetensors` | `models/text_encoders/` |
| `qwen_image_vae.safetensors` | `models/vae/` |
| LoRA-ul `d4ria` v2 (Krea 2) | `models/loras/` |

### 2. Endpoint-ul Serverless
RunPod → **Serverless → New Endpoint → GitHub**:
- Repository `nocoderesult/No.code.Vvs`, branch `comfy-ui-rr`, Dockerfile `serverless/Dockerfile`, build context `serverless`. Prima dată RunPod cere legarea contului GitHub.
- GPU: 48 GB (L40S / A6000) ajunge pentru poze; RTX PRO 6000 doar dacă vrei mai repede.
- **Active workers: 0**, **Max workers: 1**, Idle timeout: 5 s, FlashBoot pornit.
- Advanced → **Network Volume**: volumul de la pasul 1. Container disk: 20 GB.
- Notezi **Endpoint ID**.

### 3. Cheia pentru Claude
Cheia RunPod (Settings → API Keys) se pune în setările mediului din Claude, la **Network secrets**, tip Bearer, pentru `rest.runpod.io` și `api.runpod.ai`. Niciodată în chat sau în repo.

## Folosire
```
python3 serverless/genereaza.py info
python3 serverless/genereaza.py poza --endpoint ENDPOINT_ID --lora NUME_LORA.safetensors "sitting in a sunny cafe, morning light"
```
Prima cerere după o pauză durează câteva minute (încarcă modelul de 24 GB). Dacă numele LoRA-ului e greșit, eroarea worker-ului listează LoRA-urile pe care le vede: îl alegi de acolo.

## De știut
- `krea2_turbo_fp8` a fost șters de pe volum (30.10.2026), deci workflow-ul folosește **Krea 2 raw**. Pașii (28) și CFG (3,5) sunt valori de pornire, de reglat la primele teste.
- Worker-ul întoarce doar **poze** (`output.images`); clipurile nu sunt acoperite aici.
- Doar Krea 2, Wan, LTX sau alte modele cu licență valabilă în UE. MiniMax H3 nu (vezi `plan/wayfinder/iness-30/issues/13-licenta-minimax-h3.md`).
