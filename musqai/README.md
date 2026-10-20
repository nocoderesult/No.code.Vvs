# MUSQAI

**MUSQAI: Marketing Universe Studio · Quantum AI.** Studioul și platforma de ambasadori AI.

| Ce | Fișierele | Link (privat) |
|---|---|---|
| Site-ul (prototip pe mai multe pagini + Studio demo) | `musqai/site/` | https://claude.ai/artifact/Pfw75NmdRWfk1g54VUmsi1 |
| Planul interactiv pe 12 săptămâni | `musqai/plan/` | https://claude.ai/artifact/PxsV2fLh32QkoKwrvYGqW2 |

## Site-ul public (Cloudflare Pages)
Versiunea publică stă în `musqai/public/`. Ea ascunde prompturile, declanșatorii LoRA și rutina internă de pe pod, iar fonturile sunt găzduite local. Formularul de contact deschide emailul vizitatorului, adresat către contact@musqai.com.

- **Din GitHub (se actualizează singur la fiecare push):** Cloudflare → Workers & Pages → Create application → Pages → Import an existing Git repository → `nocoderesult/No.code.Vvs`. Branch: `comfy-ui-rr`. Framework preset: None. Build command: gol. Build output directory: `musqai/public`.
- **Prin încărcare directă:** Workers & Pages → Create application → Get started → Drag and drop your files. Încarci arhiva zip a folderului `musqai/public`. Un proiect creat așa nu mai poate fi legat de GitHub mai târziu.

După orice modificare în `musqai/site/`, rulezi `python3 musqai/build_public.py` și faci commit la `musqai/public/`.

## Cum se actualizează
- Caracterele, nișele, ofertele și procesele: `musqai/site/data.js`.
- Blocurile planului, zi cu zi: `musqai/plan/plan-data.js`.
- După o modificare, Claude republică pagina la același link.

## Ce se salvează și unde
- Bifele, notițele zilelor și setările planului (modul, ora de start, prima zi): baza de date a paginii planului. Claude le poate citi.
- Banca de idei din Studio (Content Brain): baza de date a site-ului.
