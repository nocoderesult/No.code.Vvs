# Insertul cu ingredientele

Type: prototype
Status: open
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
