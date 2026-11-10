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
- 10 nov: tu ai văzut probele și nu ți-au plăcut. Direcția nouă:
  - sticla levitează fix în mijlocul cadrului și se învârte tare, ca să iasă în evidență;
  - runda o facem cu Kling 4.0, la 1080p și 5 s;
  - prețul l-ai aprobat înainte: $1,48, adică 2 cadre finale plus un clip.
- Cadrele finale noi sunt de la Nano Banana Pro (`01a1c5cd-8897-7590-83ad-328c5b6fc372`, 2 imagini, $0,30). Sticla
  plutește centrată (eticheta la 0,53 din lățime), cu o spirală de lumină în jur, iar eticheta e corectă la amândouă.
  Pentru Kling am ales varianta 0.
- 10 nov, proba Kling 4.0 (1080p, 5 s, $1,18, request id `01a1c5ce-cbda-7a22-82ba-53825e474a25`, 277 s în coadă). API-ul
  Kling pe fal e deschis.
  - Pornirea și sfârșitul: primul cadru e exact cadrul de pornire (diferență medie 1,1/255), iar ultimul e exact cadrul
    final centrat (1,4/255). E un singur plan, fără tăieturi, 1080×1920 la 24 fps.
  - Mișcarea: capacul iese, sticla se desprinde din mână, urcă în centru și se învârte de ~2,5–3 ori (de la 0,9 la
    2,9 s), cu spirala de lumină în jur. Apoi se oprește cu eticheta spre cameră. În rotire eticheta e mișcată, iar la
    final e corectă.
  - Sunetul: stereo la 44,1 kHz, −17,7 LUFS, TP −3,4 dBFS, cu o coborâre în ultima secundă.
  - În previzualizarea tăieturii (macro-ul real 6,46–8,00 s, apoi insertul), schimbarea la tăietură e 31,9, cât
    mișcarea reală din cadrele de dinainte (23–30). Subtitrarea arsă dispare la tăietură.
