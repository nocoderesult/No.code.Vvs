# 06 · Video și voce

Reels sunt formatul care aduce public nou. Video-ul costă însă de 10–50 de ori mai mult decât o poză, deci intră după ce pozele merg.

## Trei feluri de clip, de la ieftin la scump

| Fel | Cum se face | Cost | Când |
|---|---|---|---|
| Poze animate ușor | mișcare lentă de cameră peste o poză, text și muzică | aproape zero | din prima zi |
| Imagine în video | o poză acceptată devine clip de 5–10 secunde | mediu | după prima lună |
| Video cu referință | personajul face o acțiune descrisă, cu identitatea păstrată | mare | când bugetul permite |

Ce **nu** facem: înlocuirea persoanei din clipul altui creator („character swap”) sau copierea mișcării din clipul unei persoane reale fără acordul ei.

## Costuri văzute în sesiune (Higgsfield, clip de 6,9 secunde)

| Model | Cost |
|---|---|
| FLUX 3 Video Edit | 15 credite |
| Cinema Studio 4.0, 720p | 48 de credite |
| Cinema Studio 4.0, 1080p | 110 credite |
| Seedance 2.5, 1080p | 138 de credite |

Concluzia: pentru colorizare și finisaj nu folosim modele generative. Ele regenerează imaginea, scad rezoluția și costă mult.

## Rețeta unui reel

1. **Cârligul, secundele 0–2:** o mișcare, o întrebare sau un text pe ecran. Fără introducere.
2. **Corpul, secundele 2–12:** o singură idee.
3. **Finalul:** un îndemn sau o buclă care duce înapoi la început.

Specificații: vertical 9:16, 1080×1920, 30 de cadre pe secundă, între 5 și 90 de secunde ca să intre în fila Reels. Textul important stă departe de marginile de sus și de jos, unde vin butoanele aplicației.

## Lista de verificare video

- [ ] fața rămâne aceeași în tot clipul, nu doar în primul cadru;
- [ ] mâinile și dinții nu se deformează în mișcare;
- [ ] fundalul nu „curge” și obiectele nu apar din nimic;
- [ ] nu pâlpâie pielea sau părul;
- [ ] textul de pe ecran e corect și lizibil pe telefon;
- [ ] sunetul e curat și are drepturi;
- [ ] primul cadru arată bine și ca imagine de copertă.

Te uiți la tot clipul, cadru cu cadru în zonele de mișcare. Un cadru bun la mijloc nu spune nimic despre restul.

## Vocea

- o singură voce, aleasă o dată și scrisă în fișa personajului;
- vocea e **generată**, nu clonată după o persoană reală fără acordul ei;
- aceleași setări la fiecare clip: ton, viteză, limbă;
- un text de probă fix, de 20 de secunde, pe care îl refaci când schimbi unealta, ca să compari.

## Colorizarea

Scriptul din `unelte/culoare/` face colorizare clasică pe fișierul original: conversie din Apple Log, expunere, contrast de film, tentă pe umbre și lumini. A fost folosit în sesiune pe un clip 4K de pe iPhone și păstrează rezoluția, cadența și sunetul.

Pentru clipuri generate, care nu sunt filmate în Log, se folosește doar partea de „look”, cu valori mai blânde.

Fluxul stabilit: întâi cadre de probă, apoi videoclipul. Nu randezi tot clipul înainte să fie aprobate pozele.

## Gata când

- [ ] există un șablon de reel care se poate reface în sub 30 de minute;
- [ ] vocea e aleasă și notată în fișă;
- [ ] un clip a trecut toată lista de verificare.
