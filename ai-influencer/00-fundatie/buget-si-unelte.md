# Buget și unelte

Prețurile sunt orientative și se schimbă. Verifică-le în consolă înainte de fiecare cheltuială.

## Unelte, pe etape

| Etapă | Unealtă | Rol | Stare |
|---|---|---|---|
| Prompturi | `nano-banana-pro-prompts-recommend-skill` (YouMind) | șabloane de prompt cu exemple | folosit în sesiune |
| Poza de bază | Seedream 5.0 Pro, Nano Banana 2.1 (Higgsfield) | primele imagini ale personajului | folosit în sesiune |
| Set de date | generare cu referință + triere manuală | 30–40 de poze consistente | de făcut |
| Antrenare | `ostris/ai-toolkit` pe RunPod | LoRA-ul personajului | de făcut |
| Generare zilnică | ComfyUI + LoRA | poze de conținut | de făcut |
| Generare prin API | `runpod-workers/worker-comfyui` | ComfyUI ca serviciu, plătit la secundă | de făcut |
| Video | model imagine-în-video cu referință | reels | de făcut |
| Colorizare | `unelte/culoare/` (ffmpeg + LUT propriu) | finisaj video | folosit în sesiune |
| Publicare | Instagram Content Publishing API | postare programată | de făcut |

## Candidați de pe GitHub (de evaluat, nu sunt testați)

| Depozit | Stele | Pentru ce |
|---|---|---|
| `Comfy-Org/ComfyUI` | ~146.000 | motorul de generare |
| `Comfy-Org/ComfyUI-Manager` | ~16.800 | instalarea nodurilor lipsă |
| `ostris/ai-toolkit` | ~12.600 | antrenare LoRA, are șablon pe RunPod |
| `cocktailpeanut/fluxgym` | ~3.300 | antrenare LoRA cu interfață simplă, pentru VRAM mic |
| `runpod-workers/worker-comfyui` | ~750 | ComfyUI ca API serverless |
| `artokun/comfyui-mcp` | ~920 | control ComfyUI din Claude |
| `perfectgf/lora-dataset-studio` | ~350 | construit și descris seturi de date |
| `vavo/lora-pilot` | ~90 | de la set de date la LoRA, într-un singur loc |
| `ralphcrisostomo/n8n-nodes-meta-publisher` | ~23 | publicare Instagram din n8n |

Numărul de stele arată popularitatea, nu calitatea. Fiecare se verifică înainte de folosire: ultima actualizare, licența, problemele deschise.

## Costuri RunPod, ordin de mărime

| Element | Cost orientativ | Observație |
|---|---|---|
| Placă de 24 GB | circa 0,3–0,7 $/oră | ajunge pentru antrenare LoRA și generare |
| Antrenare LoRA de personaj | 2–5 ore, deci câțiva dolari | depinde de model și de numărul de pași |
| Volum de rețea | circa 0,07 $/GB/lună | **se plătește și cu pod-ul oprit** |
| Serverless | la secundă, doar cât rulează | potrivit pentru generarea zilnică |

Capcane de cost:
- un pod uitat pornit peste noapte;
- un volum de rețea prea mare, păstrat luni de zile;
- modelele descărcate din nou la fiecare pornire, în loc să stea pe volum.

## Buget lunar, trei trepte

| Treaptă | Ce acoperă |
|---|---|
| Sub 30 € | o antrenare, generare de imagini, fără video generat |
| 30–80 € | reantrenări, generare zilnică, câteva clipuri pe săptămână |
| Peste 80 € | video zilnic, voce, teste pe mai multe modele |
