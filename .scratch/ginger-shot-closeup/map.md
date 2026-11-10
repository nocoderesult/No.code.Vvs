# Hartă: close-up generat la deschiderea capacului (SNOOZZ Ginger Energy)

Label: wayfinder:map

## Destination

Un insert generat cu fal.ai, gata de pus în montajul tău. Close-up pe toată sticla SNOOZZ Ginger Energy, cu eticheta,
din momentul în care se deschide capacul. Amplifică energia shot-ului și are sunetul generat de model. Montajul
reel-ului îl faci tu, în Premiere sau DaVinci.

## Notes

- Domeniu: reel de produs hibrid, adică filmare reală plus inserturi generate. Sursa: „SNOOZZ SHOT GHIMBIR.mp4”
  (18,8 s, 1080×1920, 24 fps, subtitrări arse în imagine). Momentul deschiderii: mâna ajunge la capac la 6,46 s,
  îl răsucește până la 7,7 s, capacul iese din gât la 7,7–8,0 s, apoi urmează un crossfade spre sticla ținută lângă
  fereastră (8,1–8,9 s). Subtitrările sunt peste sticlă în toate aceste cadre. Singurul cadru curat cu toată sticla e
  sticla pe masă (5,9–6,4 s).
- Eticheta, citită din cadrul curat de pe masă: „SNOOZZ” (cei doi O plini), „Ginger Energy”, „ghimbir, lămâie, măr”,
  „100 ml”, pe un cerc portocaliu.
- Skill-uri de consultat: fal-ai-media (modele, cost), prompt-builder (prompturi în engleză, pe structura fiecărui
  model), taste (direcție, lumină), video-editor (`scripts/fal_run.py`, `reference/fal.md`, QC), grilling +
  domain-modeling (glosarul din `CONTEXT.md`).
- Preferințe fixe:
  - toată sticla, cu eticheta;
  - întâi cadrul de vârf ca imagine (2–3 variante, alegi tu), apoi animăm de la cadrul de pornire la el;
  - probe cu Gemini Omni Flash 1.2 și Kling 4.0, finalul cu Seedance 2.5;
  - sunetul îl generează modelul;
  - respectăm regulile platformelor și ale fiecărui model, ca promptul și rezultatul să iasă cum trebuie.
- **Revizuit pe 10 nov.:** în loc de orbita camerei, sticla levitează fix în centrul cadrului și se învârte repede.
  Runda de probe se face cu Kling 4.0 (1080p, 5 s). Dacă iese bine, clipul poate fi chiar finalul.
- **Revizuit din nou pe 10 nov., după referința ta (grapefruitul care iese din doză):** din sticla deschisă ies bucăți
  realiste de măr, lămâie și ghimbir cu stropi de suc, cu încetinitorul. Insertul se termină pe cadrul real de lângă
  fereastră (cadrul 214), ca montajul să continue cu cadrul 215. Șablonul de prompturi e în [metaprompt.md](metaprompt.md).
- Execuția intră în hartă: harta se termină cu insertul livrat, nu doar cu planul.
- Cost: prețul se verifică înainte de orice generare (`fal_run.py price` / `estimate`), se trimite doar cu `--yes`,
  iar ID-ul fiecărui job se păstrează. **Înainte de fiecare generare îl întreb pe creator ce model folosesc, pentru ce
  și cât costă.** Nu există un plafon fix.
- Cercetările se salvează în `research/`, lângă hartă, pe ramura de lucru.

## Decisions so far

- [Regulile modelelor pentru prompturi](issues/01-regulile-modelelor.md): cadrul de vârf păstrează încadrarea, camera aproape fixă, un singur plan, sunet fără muzică, Seedance fără fețe și cu H.264; API-ul Kling pe fal e neconfirmat.
- [Structura close-up-ului](issues/05-structura-close-up.md): din macro, la ieșirea capacului, retragere cu orbită completă până la toată sticla; răsărit „The Day Starters” cu fibre de ghimbir și picături de lămâie; 3 momente în ~4 s; cadrul de vârf cu Nano Banana Pro; fără plafon fix, cu întrebare înainte de fiecare generare.
- [Credit pe contul fal](issues/03-credit-fal.md): contul are credit, iar upload-ul în stocarea fal merge.
- [Clipurile sursă fără subtitrări](issues/04-clipuri-fara-subtitrari.md): nu există; cadrul de pornire se curăță cu o editare de imagine, doar în zona subtitrării.
- [Cadrul de pornire curat](issues/09-cadrul-de-pornire.md): ambele cadre (7,83 s și 8,04 s) curățate cu Nano Banana Pro, doar în zona subtitrării; restul e cadrul filmat.
- [Cadrul de vârf: variante de imagine](issues/06-cadrul-de-varf.md): v1 (în mână) și v3 (plutind) merg la probe; v2 a căzut din cauza etichetei („lămâle”).
- [Probe video: Gemini Omni Flash 1.2 și Kling 4.0](issues/07-probe-video.md): Gemini nu ține cadrul de pornire; Kling și Wan 3.0 Prime țin ambele capete.
- [Insertul cu ingredientele](issues/10-insert-ingrediente.md): două versiuni complete (Kling, Wan), insert pe cadrele 185–303, sunet original neatins, subtitrări originale puse la loc, același format ca originalul.
- [Finalul cu Seedance 2.5](issues/08-final-seedance.md): înlocuit, la alegerea ta, de variantele Kling și Wan.

## Not yet specified

- Formatul de livrare: 24 fps ca montajul, 1080×1920, H.264 sau ProRes, sunetul inclus sau pe pistă separată.
- Potrivirea culorii cu cadrele din jur.
- Eticheta în timpul orbitei: cadre de ghidaj din lateral și din spate (Kling acceptă cadre intermediare), alt take,
  sau eticheta refăcută în post.
- Ce model de probă înlocuiește Kling dacă API-ul lui nu e deschis pe fal (se decide la „Probe video”).
- Unde tai exact în timeline și cât stă insertul în montaj.

## Out of scope

- Montajul complet al reel-ului, subtitrările și muzica: le faci tu.
