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
- Skill-uri de consultat: fal-ai-media (modele, cost), prompt-builder (prompturi în engleză, pe structura fiecărui
  model), taste (direcție, lumină), video-editor (`scripts/fal_run.py`, `reference/fal.md`, QC), grilling +
  domain-modeling (glosarul din `CONTEXT.md`).
- Preferințe fixe:
  - toată sticla, cu eticheta;
  - întâi cadrul de vârf ca imagine (2–3 variante, alegi tu), apoi animăm de la cadrul de pornire la el;
  - probe cu Gemini Omni Flash 1.2 și Kling 4.0, finalul cu Seedance 2.5;
  - sunetul îl generează modelul;
  - respectăm regulile platformelor și ale fiecărui model, ca promptul și rezultatul să iasă cum trebuie.
- Execuția intră în hartă: harta se termină cu insertul livrat, nu doar cu planul.
- Cost: prețul se verifică înainte de orice generare (`fal_run.py price` / `estimate`), se trimite doar cu `--yes`,
  iar ID-ul fiecărui job se păstrează. **Înainte de fiecare generare îl întreb pe creator ce model folosesc, pentru ce
  și cât costă.** Nu există un plafon fix.
- Cercetările se salvează în `research/`, lângă hartă, pe ramura de lucru.

## Decisions so far

- [Regulile modelelor pentru prompturi](issues/01-regulile-modelelor.md): cadrul de vârf păstrează încadrarea, camera aproape fixă, un singur plan, sunet fără muzică, Seedance fără fețe și cu H.264; API-ul Kling pe fal e neconfirmat.
- [Structura close-up-ului](issues/05-structura-close-up.md): din macro, la ieșirea capacului, retragere cu orbită completă până la toată sticla; răsărit „The Day Starters” cu fibre de ghimbir și picături de lămâie; 3 momente în ~4 s; cadrul de vârf cu Nano Banana Pro; fără plafon fix, cu întrebare înainte de fiecare generare.

## Not yet specified

- Formatul de livrare: 24 fps ca montajul, 1080×1920, H.264 sau ProRes, sunetul inclus sau pe pistă separată.
- Potrivirea culorii cu cadrele din jur.
- Eticheta în timpul orbitei: cadre de ghidaj din lateral și din spate (Kling acceptă cadre intermediare), alt take,
  sau eticheta refăcută în post.
- Ce model de probă înlocuiește Kling dacă API-ul lui nu e deschis pe fal (se decide la „Probe video”).
- Unde tai exact în timeline și cât stă insertul în montaj.

## Out of scope

- Montajul complet al reel-ului, subtitrările și muzica: le faci tu.
