# 05 · Generarea imaginilor

Două drumuri, același rezultat: până există LoRA-ul, generezi cu imagine de referință pe modele găzduite; după, generezi în ComfyUI cu LoRA.

## Structura promptului

Fiecare prompt are aceleași șase părți, în aceeași ordine:

1. **Tipul pozei:** `Raw amateur smartphone photo, unedited, taken with an iPhone rear camera`.
2. **Blocul de identitate:** textul fix din `02-personaj/bloc-identitate.txt`, neschimbat.
3. **Scena:** ținuta, locul și poza corpului, luate din fișa personajului.
4. **Detalii biologice:** pori, puf fin pe maxilar, roșeață ușoară, umezeală în colțul ochilor.
5. **Aparat și lumină:** de unde vine lumina, zgomot de senzor, balans de alb imperfect.
6. **De evitat:** lista de mai jos.

Scena se scrie pornind de la un șablon din biblioteca `nano-banana-pro-prompts-recommend-skill`, ales pentru locul respectiv. Șabloanele folosite în sesiune: sală (2859), mașină (18289), plajă la apus (13294), bliț de aparat vechi (1067), fișă de referință (13285).

## Regulile anti-plastic

Măsurate în bibliotecă, pe prompturile cu cel mai bun realism.

**Cuvinte care ajută:**

| Cuvânt | În câte prompturi apare |
|---|---|
| visible pores | 691 |
| raw photo | 327 |
| subsurface scattering | 259 |
| amateur | 106 |
| vellus hair / peach fuzz | 156 |
| no beautification / no airbrush / no retouch | 171 |

**Ce pui la „Avoid”:** `plastic skin, airbrushing, over-smoothing, beauty filter, beautification, artificial perfection, AI glow, HDR, cinematic color grading, studio look, heavy contour makeup, glossy doll face, exaggerated proportions, CGI, text, watermark`.

**Ce nu scrii niciodată în prompt:** `flawless`, `perfect skin`, `stunning`, `gorgeous`, `doll`, `8k masterpiece`. Împing modelul exact spre fața de păpușă.

**Decorul trebuie să fie imperfect:** pereți cu urme, praf, cabluri, o cană uitată. Un decor steril face și persoana să pară generată.

## Poarta de calitate

Nicio poză nu ajunge în calendar fără să treacă tot:

- [ ] e ea: fața și semnele fixe sunt corecte;
- [ ] mâinile, dinții și ochii sunt normali;
- [ ] pielea are textură;
- [ ] ținuta și locul sunt cele din fișă;
- [ ] obiectele personale sunt cele din fișă (aceeași husă de telefon);
- [ ] textul din cadru, dacă există, e lizibil și corect;
- [ ] nu apare nicio marcă sau logo;
- [ ] nu seamănă cu o persoană reală cunoscută;
- [ ] e potrivită pentru Instagram;
- [ ] se potrivește cu ziua din calendar: anotimp, oră, loc.

Greșeli văzute în sesiune, de căutat special: piercingul mutat pe obraz, litere stricate pe obiecte, culoarea ochilor schimbată, corpul diferit de la o poză la alta.

## Drumul A · modele găzduite, cu referință

Bun până la LoRA și pentru teste rapide.

| Model | Cost în sesiune | Ce a ieșit |
|---|---|---|
| Seedream 5.0 Pro | 2,5 credite | cel mai apropiat de cerere, față credibilă |
| Nano Banana 2.1 | 2 credite | realist, dar ține corpul moderat |
| Nano Banana 2 | 2 credite | foarte real ca „poză de telefon”, mai puțin control |

Poza de bază intră ca referință, cu instrucțiunea de a păstra fața identică. Limita: fața alunecă puțin la fiecare generare.

## Drumul B · ComfyUI cu LoRA

1. Construiești workflow-ul în interfață: model de bază, LoRA la intensitatea din `04`, prompt, mărire de rezoluție.
2. Îl verifici de mână pe 10 prompturi.
3. Îl exporți în format API (`Export (API)`) în `workflows/`.
4. De aici îl rulează `automatizare/runpod_comfy.py`.

Sfaturi din ghiduri: LoRA-ul ține identitatea de bază, iar o imagine de referință (IP-Adapter) poate fi adăugată peste, la intensitate mai mică, ca asigurare.

## Organizarea rezultatelor

```
05-generare-imagini/
  workflows/     workflow-uri ComfyUI în format API
  cereri/        câte un fișier de cerere pe lot
  iesiri/AAAA-LL-ZZ/   tot ce s-a generat în ziua aceea
  acceptate/     ce a trecut poarta, gata de calendar
```

Fișierele se numesc `AAAA-LL-ZZ_loc_tinuta_NN.jpg`. Promptul și sămânța fiecărei poze acceptate se păstrează alături, într-un `.json`, ca să o poți reface.

## Gata când

- [ ] există un prompt de bază care dă constant rezultate bune;
- [ ] 14 poze au trecut poarta de calitate;
- [ ] fiecare are promptul și sămânța salvate.
