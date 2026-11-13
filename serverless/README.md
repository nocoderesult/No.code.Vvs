# Poze prin Runpod Serverless, cu volumul global

Cererea pleacă dintr-o pagină, din chat sau din script. Runpod pornește singur o placă video oriunde are una liberă, generează poza, o trimite înapoi și se oprește. Se plătesc doar secundele de lucru. Cu 0 workeri activi, când nu generează nimeni nu plătești nimic pentru GPU. Volumul global se plătește separat, după cât ocupă (~0,09 $/GB pe lună plus cereri).

| Fișier | Ce face |
|---|---|
| `Dockerfile` | Worker-ul oficial `runpod/worker-comfyui:5.10.0-base-cuda12.8.1` + nodurile din `krea2_studio` (rgthree, Impact Pack + Subpack, ProPost). Fără modele în imagine. |
| `extra_model_paths.yaml` | Unde caută ComfyUI modelele: `/runpod-volume/models` (volumul global) sau `runpod-slim/ComfyUI/models` (volum vechi de pod). |
| `descarca_modele.sh` | Descarcă pe volumul global modelele Krea 2 (~18,6 GB) din `Comfy-Org/Krea-2`. |
| `workflows/iness_krea2_raw_api.json` | Workflow-ul de bază în format API: Krea 2 raw fp8 + LoRA (opțional) → poză 896×1152. |
| `genereaza.py` | `info` (volume, endpoint-uri, pod-uri) și `poza "scena"` (trimite cererea, așteaptă, salvează PNG-ul). Doar biblioteca standard Python. |

## Instalare (o singură dată)

### 1. Modelele pe volumul global
Pe un pod cu volumul global montat la `/workspace-global`, în terminal:
```
curl -fsSL https://raw.githubusercontent.com/nocoderesult/No.code.Vvs/comfy-ui-rr/serverless/descarca_modele.sh -o /workspace/descarca_modele.sh
bash /workspace/descarca_modele.sh
```
Modelele ajung în `/workspace-global/models/{unet,clip,vae}`: folderele pe care le citește și worker-ul oficial `runpod/worker-comfyui`, fără imagine proprie. LoRA-urile tale (de exemplu `d4ria`) le pui în `/workspace-global/models/loras/`.

| Fișier | Folder pe volumul global | Mărime |
|---|---|---|
| `krea2_raw_fp8_scaled.safetensors` | `models/unet/` | 13,1 GB |
| `qwen3vl_4b_fp8_scaled.safetensors` | `models/clip/` | 5,2 GB |
| `qwen_image_vae.safetensors` | `models/vae/` | 0,25 GB |

Folosim varianta fp8 a lui Krea 2 raw (13 GB, nu 26 GB): pornire la rece mai scurtă și jumătate din stocare, cu diferențe mici de calitate.

### 2. Endpoint-ul Serverless
Runpod → **Serverless → New Endpoint → Deploy from a GitHub repository**:
- Repository `nocoderesult/No.code.Vvs`, branch `comfy-ui-rr`, Dockerfile `serverless/Dockerfile`, build context `serverless`. Prima dată Runpod cere legarea contului GitHub.
- **Compute type: GPU**. Plăci de 48 GB (L40S / A6000) sau 32 GB; bifează mai multe tipuri, ca să găsească repede una liberă.
- **Active workers: 0**, **Max workers: 1** (sau 2 dacă generează mai mulți deodată), Idle timeout: 5 s, FlashBoot pornit.
- **Advanced → Global volume:** volumul tău global. Câmpul Network volumes rămâne gol (nu merg amândouă).
- Container disk: 20 GB. Notezi **Endpoint ID**.

Volumul global nu leagă endpoint-ul de un centru de date, deci Runpod caută plăci libere peste tot.

### 3. Cheia Runpod
Cheia (Settings → API Keys) nu se pune niciodată în chat, în repo sau într-o pagină publică.
- Pentru Claude: în setările mediului, la **Network secrets**, tip Bearer, pentru `rest.runpod.io` și `api.runpod.ai`.
- Pentru o pagină folosită de alte persoane: cheia stă pe un server intermediar (de exemplu un Cloudflare Worker cu secret), iar pagina vorbește doar cu el.

## Folosire
```
python3 serverless/genereaza.py info
python3 serverless/genereaza.py poza --endpoint ENDPOINT_ID --lora d4ria_v2.safetensors "sitting in a sunny cafe, morning light"
python3 serverless/genereaza.py poza --endpoint ENDPOINT_ID --lora none "test fără LoRA"
```
Prima cerere după o pauză durează câteva minute (încarcă modelul de pe volumul global). Dacă numele LoRA-ului e greșit, eroarea worker-ului listează LoRA-urile pe care le vede: îl alegi de acolo.

## De știut
- Worker-ul întoarce doar **poze** (`output.images`); clipurile nu sunt acoperite aici.
- Volumul global e citit bine, scris mai încet. E potrivit pentru modele, nu pentru fișiere care se schimbă des.
- Dacă soldul Runpod ajunge la 0 $, volumul global se șterge după 15 zile. Pune alertă de sold mic.
- Krea 2 are licența proprie (Krea 2 Community License). Înainte să oferi generări altor persoane sau clienților, verifică ce permite pentru folosire comercială.
- Doar Krea 2, Wan, LTX sau alte modele cu licență valabilă în UE. MiniMax H3 nu (vezi `plan/wayfinder/iness-30/issues/13-licenta-minimax-h3.md`).

## Pagina de generare
- Pe site: `https://musqai.tavit5050.workers.dev/generator/` (din `musqai/web/static/generator/`, cererile trec prin Worker-ul site-ului).
- Fișier de sine stătător: `serverless/generator_krea2.html`, se deschide direct în browser și vorbește direct cu `api.runpod.ai`.
- Amândouă cer o cheie Runpod **restricționată** doar la endpoint-ul `musqai-matrix-pro6000` (Read/Write). Cheia nu stă niciodată în pagină sau în repo.
