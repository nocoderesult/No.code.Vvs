# Probe video: Gemini Omni Flash 1.2 și Kling 4.0

Type: prototype
Status: claimed
Blocked by: 06

## Question

Cu ce mișcare, sunet și fidelitate a etichetei iese animația de la cadrul de pornire la cadrul de vârf, la rezoluție
mică, pe cele două modele de probă? Ce prompt ducem la Seedance 2.5?

## Comments

- 10 nov: patru probe cu Gemini Omni Flash 1.2 (720p, 4 s, 9:16, $1,31 în total), din cadrele de 7,83 s și 8,04 s spre
  v1 și v3. Request id-urile: `01a1c5bf-66a9-7983-99a7-fae63c471a44` (7,83 → v1), `01a1c5bf-6ec0-7e32-9fd4-4af91bf29cd7`
  (7,83 → v3), `01a1c5bf-76df-76b3-b48b-61dab2e358f3` (8,04 → v1), `01a1c5bf-7fd7-7420-88c8-1ea07faccdc3` (8,04 → v3).
  - Ce merge:
    - lumina aurie, razele și particulele;
    - un singur plan, fără tăieturi;
    - 720×1280 la 24 fps, ca montajul;
    - ultimul cadru e exact cadrul de vârf (diferență medie ~2/255);
    - eticheta corectă pe tot clipul, fiindcă rămâne din față;
    - sunetul are doar efecte: aproape liniște în prima secundă, apoi whoosh și sclipire, −24…−28 LUFS.
  - Ce nu merge:
    - Primul cadru nu e cel dat. Gemini reface scena cu capacul încă pus și repetă deschiderea. Doar proba din 7,83 s
      spre v1 ajunge aproape de cadrul real, la cadrul 8 (diferență medie 13,7/255). Probele din 8,04 s schimbă
      încadrarea și fundalul.
    - Orbita nu apare: camera doar se retrage.
