# MUSQAI

**MUSQAI: Marketing Universe Studio · Quantum AI.** Studioul și platforma de ambasadori AI. Prima ambasadoare: **Iness**.

| Ce | Unde |
|---|---|
| Site-ul public, cu zonele de generare | `musqai/web/` (se publică pe Cloudflare Workers) |
| Planul interactiv pe 12 săptămâni | `musqai/plan/` · https://claude.ai/artifact/PxsV2fLh32QkoKwrvYGqW2 |
| Prototipul vechi al site-ului (înlocuit de `musqai/web/`) | `musqai/site/` |

## Site-ul (`musqai/web/`)
- `content.mjs`: tot textul site-ului (caractere, nișe, prețuri, procese, zone).
- `build.mjs`: face câte o pagină HTML pentru fiecare adresă, în `public/`. Rulare: `node musqai/web/build.mjs`.
- `static/`: stilul, scripturile, fonturile găzduite local, pozele lui Iness, favicon-ul.
- `worker.js` și `functions/api/`: cele 5 zone de generare (idei, imagine, prompt, text, caracter), care rulează pe Cloudflare cu Workers AI.
- `lib/ai.js`: verificările de siguranță, modelele folosite și marcajul AI din imagini.
- `tools/assets.py` și `tools/og.py`: refac fonturile, pozele și imaginea de distribuire.

După orice schimbare în `content.mjs` sau `static/`, rulezi `node musqai/web/build.mjs` și faci commit și la `public/`.

## Publicarea pe Cloudflare Workers (o singură dată)
1. Cloudflare → Workers & Pages → Create application → importă repo-ul `nocoderesult/No.code.Vvs`.
2. Project name: `musqai` (trebuie să fie exact numele din `wrangler.toml`). Build command: gol. Deploy command: `npx wrangler deploy`.
3. Deploy. Primul build pică, pentru că Cloudflare ia branch-ul `main`, unde e alt proiect, cu alt nume.
4. În Worker-ul `musqai`: Settings → Build → Branch control → Production branch: `comfy-ui-rr` → Save. Următorul push pe `comfy-ui-rr` publică site-ul.

Root directory poate rămâne gol: în rădăcina repo-ului e un `wrangler.toml` care trimite la `musqai/web`. Merge și cu Root directory `musqai/web`, unde e un `wrangler.toml` echivalent.

Configurația declară tot ce trebuie: paginile din `musqai/web/public`, intrarea `musqai/web/worker.js` pentru `/api/*` și legătura Workers AI cu numele `AI`. Verificată cu `wrangler deploy --dry-run` (wrangler 4.151.3).

## Modelele din zonele de generare
- Texte: `@cf/meta/llama-3.3-70b-instruct-fp8-fast` (Built with Llama).
- Imagini: `@cf/black-forest-labs/flux-1-schnell`, pătrate 1024 × 1024, cu marcaj XMP „generat cu AI” în fișier.
- Citirea pozelor: `@cf/llava-hf/llava-1.5-7b-hf`.

Pe planul gratuit Cloudflare există o limită zilnică de utilizare. Când e atinsă, zonele afișează un mesaj și merg din nou a doua zi. Pe planul gratuit nu se plătește nimic în plus.
