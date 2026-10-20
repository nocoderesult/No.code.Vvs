# MUSQAI

**MUSQAI: Marketing Universe Studio · Quantum AI.** Studioul și platforma de ambasadori AI. Prima ambasadoare: **Iness**.

| Ce | Unde |
|---|---|
| Site-ul public, cu zonele de generare | `musqai/web/` (se publică pe Cloudflare Pages) |
| Planul interactiv pe 12 săptămâni | `musqai/plan/` · https://claude.ai/artifact/PxsV2fLh32QkoKwrvYGqW2 |
| Prototipul vechi al site-ului (înlocuit de `musqai/web/`) | `musqai/site/` |

## Site-ul (`musqai/web/`)
- `content.mjs`: tot textul site-ului (caractere, nișe, prețuri, procese, zone).
- `build.mjs`: face câte o pagină HTML pentru fiecare adresă, în `public/`. Rulare: `node musqai/web/build.mjs`.
- `static/`: stilul, scripturile, fonturile găzduite local, pozele lui Iness, favicon-ul.
- `functions/api/`: cele 5 zone de generare (idei, imagine, prompt, text, caracter), care rulează pe Cloudflare cu Workers AI.
- `lib/ai.js`: verificările de siguranță, modelele folosite și marcajul AI din imagini.
- `tools/assets.py` și `tools/og.py`: refac fonturile, pozele și imaginea de distribuire.

După orice schimbare în `content.mjs` sau `static/`, rulezi `node musqai/web/build.mjs` și faci commit și la `public/`.

## Publicarea pe Cloudflare Pages (o singură dată)
1. Cloudflare → Workers & Pages → Create application → Pages → Connect to Git / Import an existing Git repository.
2. Repo: `nocoderesult/No.code.Vvs`. Numele proiectului: `musqai`. Production branch: `comfy-ui-rr`.
3. Framework preset: None. Build command: gol. Build output directory: `public`. Root directory (Advanced): `musqai/web`.
4. Save and Deploy.

Legătura cu Workers AI (`AI`) e declarată în `musqai/web/wrangler.toml`. Dacă Cloudflare nu o preia, o adaugi manual: proiectul → Settings → Bindings → Add → Workers AI, cu numele `AI`, apoi faci din nou Deploy.

Zonele de generare nu merg dacă proiectul e făcut prin încărcarea directă a unei arhive: Cloudflare nu acceptă funcții în acest mod. Ai nevoie de varianta din GitHub.

## Modelele din zonele de generare
- Texte: `@cf/meta/llama-3.3-70b-instruct-fp8-fast` (Built with Llama).
- Imagini: `@cf/black-forest-labs/flux-1-schnell`, pătrate 1024 × 1024, cu marcaj XMP „generat cu AI” în fișier.
- Citirea pozelor: `@cf/llava-hf/llava-1.5-7b-hf`.

Pe planul gratuit Cloudflare există o limită zilnică de utilizare. Când e atinsă, zonele afișează un mesaj și merg din nou a doua zi. Pe planul gratuit nu se plătește nimic în plus.
