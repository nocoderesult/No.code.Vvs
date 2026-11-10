# Insertul cu ingredientele

Type: prototype
Status: resolved
Blocked by: —

## Question

Iese realist, ca în referința cu grapefruitul, insertul în care din sticla deschisă ies bucăți de măr, lămâie și
ghimbir? Pornește din cadrul real de la 8,04 s (cadrul 193) și se termină pe cadrul real de lângă fereastră (cadrul 214,
curățat), ca montajul să continue cu cadrul 215. Prompturile sunt în [metaprompt.md](../metaprompt.md):
- cadrul de final curat (Nano Banana Pro);
- cadrul-cheie al exploziei (Nano Banana Pro);
- clipul Kling 4.0 (1080p, 5 s, start + cadru-cheie + final);
- varianta Seedance 2.5.

## Comments

- 10 nov: ai cerut ca înainte de deschidere sticla să se umfle puțin, ca să se vadă presiunea, iar la deschidere să
  explodeze direct, frumos. De aceea cadrul de pornire se mută pe cadrul 185 (7,71 s), cu capacul încă pus, iar
  metapromptul are momentul de presiune la 0–0,8 s.
- Cadrul de final (214) e curățat: Nano Banana Pro, `01a1c5ed-f8e6-7022-9cd4-c5f7f0ddaf9a`, 2 variante, $0,30. Eticheta
  de sub „să-l ignori!” e refăcută corect la ambele. Am lipit înapoi doar zona subtitrării (ECC 0,9994) și folosim
  varianta 0.
- Cadrul-cheie al exploziei: Nano Banana Pro, `01a1c5ef-4f5f-7190-82f2-ba1f88e7550f`, 2 variante, $0,30.
  - Varianta 0 are mai multe bucăți și sticla mai mică, dar eticheta scrie „lămâle”.
  - Varianta 1 are eticheta corectă și sticla aproape de mărimea din cadrul de final. Pe ea o recomand.
- Cadrul de pornire de la 7,71 s (cadrul 185, capacul încă pus) e curățat: Nano Banana Pro,
  `01a1c5f4-2d45-7343-92fe-1d1eac361f35`, $0,15. ECC 0,9906. Modelul a refăcut toată banda subtitrării ca plastic
  ceva mai limpede pe umărul sticlei, așa că am lipit înapoi toată banda: decât litere fantomă, mai bine așa.
- Clipul Kling 4.0 e trimis: 1080p, 5 s, cadrele 185 → varianta 1 a exploziei → 214. L-ai aprobat ($1,18).
- 10 nov, clipul Kling 4.0: `01a1c5f5-61f9-7581-87dd-9ac8947ae8ad`, 226 s în coadă, $1,18. 1080×1920, 24 fps, 121 de cadre.
  - Capetele: primul cadru e exact cadrul de pornire (0,8/255), ultimul exact cadrul de final curat (1,4/255), fără
    tăieturi. Saltul la intrare (16,6) e cât mișcarea reală dintre cadrele 184 și 185 (16,2). Ieșirea spre cadrul 215
    (66,6) e aceeași tăietură tare ca în montajul original (~64).
  - Ce se vede: bucățile de fruct se văd deja în suc, înainte de deschidere, și urcă. La ~1 s capacul iese și ele țâșnesc
    cu o coroană de suc. Între 3 și 4 s cad, iar lumina trece spre fereastră. Eticheta e corectă în explozie și la final.
  - Umflarea sticlei nu se vede clar. Kling a transmis presiunea prin bucățile care urcă prin suc.
  - Sunetul ieșea cu TP +1,6 dBFS. L-am coborât static cu 2,6 dB, la −1,0 dBTP (−17,6 LUFS), resamplat la 48 kHz.
    Video-ul e copiat fără re-encodare și etichetat BT.709.
- 10 nov, direcția nouă, aleasă de tine:
  - Ordinea: sticla se învârte ca în varianta Kling, se scutură ușor, se umflă puțin, apoi capacul sare și explozia e
    ușoară.
  - Realismul: bucățile cad pe masă după gravitație și rămân acolo, stropii rămân pe lemn, iar câteva picături rămân pe
    sticlă.
  - Modelul și durata: Wan 3.0 Prime, cu promptul scris ca JSON, 8 s la 1080p.
  - Cadrul de final: devine cadrul 214 cu urmele exploziei. Merge, fiindcă următorul cadru din montaj e gura care bea.
- Cadrul final cu urmele exploziei: Nano Banana Pro, `01a1c60a-ee95-7f01-8cc4-21e6e4fe1635`, 2 variante, $0,30. L-am
  aliniat la cadrul 214 (ECC 0,999; partea de sus diferă de cea reală cu ~3/255). Eticheta e corectă la ambele variante.
  Am ales varianta 1: are toate trei ingredientele pe masă și picături care se scurg pe sticlă.
- Clipul Wan 3.0 Prime e trimis: 1080p, 8 s, promptul în JSON, cadrele 185 → urmele exploziei. L-ai aprobat ($2,24).
- 10 nov, clipul Wan 3.0 Prime: `01a1c60c-18cc-7372-a79f-8471ad125268`, seed `1544616857`, 136 s, $2,24. 1080×1920 la
  **30 fps** (240 de cadre, 8,0 s). `actual_prompt` a venit gol.
  - Capetele: primul cadru e exact cadrul de pornire (2,5/255), ultimul e exact cadrul cu urmele exploziei (3,3/255).
  - Ce se vede, pe rând:
    - 0,6–0,9 s: retragere rapidă, iar fundalul sare la fereastră, ca o mișcare bruscă de cameră;
    - 0,9–2 s: sticla închisă plutește și se rotește puțin;
    - 2–4 s: sticla e în mână, dar scuturarea și umflarea nu se văd clar;
    - 4,4 s: capacul sare;
    - 4,6–6 s: bucățile ies una după alta, cu stropi;
    - 6–8 s: bucățile cad pe masă și rămân acolo, cu stropi pe lemn și pe sticlă.
  - Sunetul ieșea cu TP +1,9 dBFS și l-am coborât cu 3 dB (−1,1 dBTP), la 48 kHz.
  - Livrare: versiunea originală la 30 fps (video copiat), o versiune la 24 fps pentru montaj și o previzualizare în
    montaj.

## Answer

Livrate: două versiuni ale videoclipului complet, „SNOOZZ SHOT GHIMBIR (Kling).mp4” și „SNOOZZ SHOT GHIMBIR (Wan).mp4”.
- **Montajul:** insertul acoperă imaginea în cadrele 185–303 (7,71–12,63 s). E pauza dintre „...să-l ignori.” (8,98 s) și
  subtitrarea „Bun, acum putem” (cadrul 304), așa că restul videoclipului e originalul.
- **Sunetul:** cel original, copiat neatins (pachetele audio sunt identice cu originalul). Sunetul generat de modele nu e
  folosit.
- **Subtitrările:** „gust pe care nu” (cadrele 185–193), „ai cum” (194–201) și „să-l ignori!” (202–214) sunt puse la loc cu
  pixelii originali. Le-am extras printr-un matting pe gri dintre cadrul cu subtitrare și fundalul curățat, din 3 cadre
  la „gust”, iar la „ai cum” cu fundal reconstruit prin inpainting.
- **Ce intră din fiecare model:**
  - Kling: primele 119 cadre din 121.
  - Wan: cadrele 0–21 normal, 22–71 accelerate de 1,85 ori cu estompare de mișcare, apoi 99–168. Am scos
    momentul static cu sticla în mână și finalul static.
- **Formatul:** același ca originalul: H.264 High 4.0, 1080×1920, 24 fps, 450 de cadre, ~16,9 Mbps (2 treceri), un
  cadru-cheie la 25 de cadre, BT.709 tv, AAC-LC 48 kHz stereo 320 kbps, timecode 01:00:00:00, MP4 isom, 18,816 s.
- **Verificări:** cadrele neatinse au PSNR minim 46,4 dB față de original (media ~51,5 dB). Tăietura de intrare (15,4)
  e cât mișcarea reală. Tăietura de ieșire spre prezentatoare e o tăietură tare, ca celelalte din montaj.

## Comments (după livrare)

- 10 nov: ai observat că versiunile livrate nu mai au secvența cu băutul. Insertul (overwrite pe cadrele 185–303) a
  acoperit gura care bea, fata din cafenea care bea și începutul cadrului cu prezentatoarea care bea. Am ales singur să
  acopăr cadrele, fără să te întreb. Lecția e acum în skill: `reference/insert-into-edit.md` și un rând în `SKILL.md`.
  Refacerea: insert ripple, deci toate cadrele originale rămân, iar sub secundele adăugate muzica originală se prelungește
  pe beat (~103,4 BPM).
- 10 nov, refăcut cu insert ripple, după ce ai aprobat lista de cadre:
  - **Cadrele:** toate cadrele originale sunt păstrate. Insertul înlocuiește doar cadrele 185–214 (ridicarea capacului,
    crossfade-ul și cadrul de la fereastră). Kling are 141 de cadre (ultima secundă încetinită de 1,83 ori, cu
    estompare). Wan are 197 de cadre (coada statică prelungită de 1,24 ori).
  - **Sunetul:** cel original, cu muzica prelungită prin repetarea unei măsuri (4 bătăi, 2,3187 s) din pauza fără voce. La
    Kling se repetă de 2 ori (+4,637 s), la Wan de 3 ori (+6,956 s). Punctul de lipire e la 11,970 s, cu fade-uri de
    40 ms. Nu apare nicio pocnitură, bătaia rămâne regulată (~0,58 s), iar după lipituri sunetul e identic eșantion cu
    eșantion cu originalul.
  - **Sincronizarea după insert:** Kling +12 ms, Wan −2 ms.
  - **Subtitrarea „să-l ignori!”:** e pe insert pe cadrele 202–215, ca în original. Pe primul cadru cu gura care bea (215)
    am pus copia cadrului 216, ca să nu rămână subtitrarea veche, care ar fi clipit o dată.
  - **Formatul:** H.264 High 4.0, ~16,9 Mbps, 24 fps, BT.709, AAC-LC 48 kHz stereo la ~321 kbps (encoderul în modul
    `fast` atinge bitrate-ul original), timecode 01:00:00:00.
  - **Durata:** Kling 23,41 s, Wan 25,73 s. Loudness-ul integrat (−12,5 și −13,0 LUFS față de −11,5) scade doar din cauza
    secundelor în plus fără voce, câștigul n-a fost schimbat.
