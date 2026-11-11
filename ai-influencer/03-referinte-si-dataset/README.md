# 03 · Referințe și set de date

Trei lucruri, în ordine: poza de bază, fișa de referință, setul de antrenare. Fiecare se face o singură dată, cu grijă.

## Structură

```
03-referinte-si-dataset/
  baza/            poza de bază aleasă + variantele respinse, cu motiv
  fisa-referinta/  corp întreg și prim-planuri din mai multe unghiuri
  candidate/       tot ce s-a generat pentru set, netriat
  dataset/         pozele acceptate + câte un .txt cu descrierea fiecăreia
  respinse/        pozele picate la control, pe motive
```

Folderele `candidate/`, `dataset/` și `respinse/` nu se urcă în depozitul public.

## Pasul 1 · Poza de bază

O singură imagine care stabilește fața. Tot restul pornește de la ea.

- generată **de la zero**, fără imagine de referință, cu blocul de identitate și regulile anti-plastic din `05-generare-imagini/`;
- portret din față, lumină naturală moale, expresie neutră, fără ochelari, fără păr peste față;
- generezi 8–12 variante și alegi una. Criterii: arată a om real, are semnele fixe, nu seamănă cu o persoană cunoscută;
- o dată aleasă, **nu se mai schimbă**.

Lecție din sesiune: editările repetate pornind de la o imagine AI adună plastic. Fiecare editare netezește mai mult. Dacă fața nu e bună, generezi alta de la zero, nu o corectezi pe cea veche.

## Pasul 2 · Fișa de referință

Aceeași femeie din mai multe unghiuri, folosind poza de bază ca referință de identitate.

| Cadru | Câte |
|---|---|
| corp întreg: față, trei sferturi stânga, trei sferturi dreapta, profil, spate | 5 |
| prim-plan față: față, trei sferturi stânga și dreapta, profil stânga și dreapta | 5 |
| expresii: neutră, zâmbet cu dinți, râs, serioasă, privire în jos | 5 |

Fond simplu, lumină uniformă, haine simple și mulate ca să se vadă proporțiile.

## Pasul 3 · Setul de antrenare

Ținta: **30–40 de poze** acceptate. Ghidurile publice recomandă între 15 și 30; un set mai variat dă un LoRA mai flexibil.

### Compoziția setului

| Categorie | Pondere | De ce |
|---|---|---|
| prim-planuri de față | 35% | identitatea stă în față |
| bust (de la piept în sus) | 30% | cadrul cel mai folosit în postări |
| corp întreg | 25% | proporțiile corpului |
| detalii (mâini, profil apropiat) | 10% | semnele fixe |

### Varietatea obligatorie

| Ce variază | Minimum |
|---|---|
| lumină | zi afară, fereastră, interior cald, bliț, apus |
| loc | cel puțin 6 locuri diferite |
| ținută | cel puțin 8, în culori diferite |
| expresie | cel puțin 5 |
| unghi | față, trei sferturi, profil, de sus, de jos |
| coafură | lăsat, coadă, prins |
| distanță | apropiat, mediu, departe |

Dacă toate pozele au aceeași ținută sau același fundal, LoRA-ul le învață ca parte din personaj. Ce vrei să rămână fix (fața, semnele) apare în toate. Ce vrei să poți schimba (haine, loc, lumină) trebuie să varieze.

### Controlul de calitate, poză cu poză

O poză intră în `dataset/` doar dacă trece tot:

- [ ] e aceeași femeie ca în poza de bază, fără dubiu;
- [ ] semnele fixe sunt prezente și pe partea corectă;
- [ ] mâinile au cinci degete și arată normal;
- [ ] ochii sunt simetrici, privirea e coerentă;
- [ ] pielea are textură, fără aspect de ceară;
- [ ] nu are text, logo sau filigran;
- [ ] fața nu e acoperită de păr, mână, telefon sau ochelari de soare;
- [ ] nu e neclară și nu e tăiată ciudat;
- [ ] latura scurtă are cel puțin 1024 de pixeli;
- [ ] nu e aproape identică cu altă poză din set.

Pozele picate se mută în `respinse/`, cu motivul în numele fișierului. Motivele care se repetă îți arată ce să schimbi în prompt.

### Descrierile (captions)

Fiecare poză are un `.txt` cu același nume.

- începe cu **cuvântul-cheie** al personajului, un cuvânt inventat care nu există în limbă (de exemplu `mrav1`);
- descrie ce **variază**: ținuta, locul, lumina, unghiul, expresia;
- **nu** descrie ce e fix: fața, culoarea ochilor, semnele. Acelea trebuie să se lege de cuvântul-cheie;
- un format, același la toate pozele.

Exemplu:
```
mrav1, a woman taking a mirror selfie in a gym, black sports bra and leggings, hair in a high ponytail, overhead fluorescent light, slight smile, medium shot
```

### Denumirea fișierelor

`NNN_cadru_loc_tinuta.jpg`, de exemplu `014_bust_cafenea_pulover-crem.jpg`. Descrierea e `014_bust_cafenea_pulover-crem.txt`.

## Gata când

- [ ] poza de bază e aleasă și salvată în `baza/`;
- [ ] fișa de referință are cele 15 cadre;
- [ ] `dataset/` are 30–40 de poze, fiecare cu descrierea ei;
- [ ] compoziția și varietatea respectă tabelele;
- [ ] setul are o copie de siguranță în afara RunPod.
