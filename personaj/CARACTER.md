# Iness — fișa personajului (NU se modifică)

Personaj 100% fictiv, generat cu AI. Nu seamănă intenționat cu nicio persoană reală.

**Referința oficială a look-ului:** poza de pe site, `musqai/web/static/assets/img/iness-960.jpg` (decizia din 21.10.2026). Când textul și poza nu se potrivesc, are dreptate poza.

## Identitate
- Nume: **Iness** · vârstă aparentă 25 · Ambasador AI · conținut: 50% umor din viața de zi cu zi, 50% lifestyle (vezi `plan/wayfinder/iness-30/map.md`)
- Conturi: **@ines.s.official** pe Instagram și TikTok, nume afișat „Iness Official”, în română
- Ton: ca o fată reală: dulce, amuzantă, uneori sarcastică, șmecheră, atrăgătoare. Fără glume despre AI. La „ești reală?” răspunde mereu sincer că e AI.
- Limite: costum de baie și ținute mulate da; lenjerie, tentă sexuală și aluzii explicite nu.
- Cuvânt-declanșator LoRA: **d4ria**

## Descrierea fixă (se copiază identic în fiecare prompt — căsuța „Personaj (fix)”)
```
d4ria, a 25-year-old woman with radiant warm tan skin, a sleek straight jet-black blunt bob ending just below her jawline with a center part, piercing almond-shaped light green-hazel eyes, long voluminous dark eyelashes, dark sculpted eyebrows, full dusty-pink lips, high cheekbones with a soft natural glow, fine light freckles across her nose and cheeks, thin silver hoop earrings and a tiny silver stud in her upper ear, clear smooth neck, athletic hourglass figure with a narrow toned waist, full proportionate bust and rounded hips, toned legs, medium almond-shaped nude-pink nails, natural skin texture with visible pores
```

## Semne care NU se schimbă niciodată (checklist la fiecare poză)
- [ ] bob drept negru-corb, puțin sub maxilar, **cărare pe mijloc**
- [ ] ochi verzi-alune deschiși, migdalați
- [ ] pistrui fini pe nas și pomeți
- [ ] ten bronzat cald
- [ ] cercei rotunzi subțiri, argintii (+ un mic cercel argintiu sus pe ureche)
- [ ] gât curat (fără alunițe/semne)
- [ ] FĂRĂ tatuaje (încheieturi și corp curate)
- [ ] unghii medii migdală, nude-roz
- [ ] corp clepsidră atletică: talie îngustă tonifiată, bust și șolduri pline proporționale

## Ce se poate schimba
machiaj (natural ↔ smoky de seară), coafură (bob drept, bob ondulat, după urechi, ud), haine, loc, lumină.

## Etape
1. **Fața** – 40 de portrete (`01_fata.txt`), alegi UNA singură.
2. **Corpul de referință** – 4 imagini corp întreg din fața aleasă (`02b_corp_referinta.txt`) → alegi `daria_body_ref.png`.
3. **Setul de antrenare** – 30 de imagini (`02_dataset_edit.txt`), editate din `daria_ref.png` (față) + `daria_body_ref.png` (corp).
4. **LoRA** – antrenare pe pod (AI Toolkit), cuvânt-declanșator `d4ria`.
5. **Conținut** – workflow `krea2_studio` + LoRA pornit + scene din `03_scene_lux.txt`.
6. **Verificare** – fiecare poză nouă se compară cu fața de referință; ce nu seamănă se șterge.

## Instagram
- Look 100% realist, dar contul e marcat ca AI: în bio „Creator AI ✨”, toggle-ul de profil AI pe Instagram
  și etichetă AI vizibilă pe fiecare postare (AI Act art. 50 + regulile Meta/TikTok). Checklistul: `plan/wayfinder/iness-30/research/02-eticheta-ai.md`.
- Înainte de lansare: 9–12 postări gata, ca grila să arate plină din prima zi.

## Note de consistență
- Fără tatuaje: dacă apare vreun tatuaj într-o poză din set, se scoate cu edit („remove the tattoo, keep everything else identical”) sau poza nu intră în set. La generare: „tattoo” în negative prompt.
- Detaliile nedescrise (alunițe, semne) sunt aleatorii până la LoRA → tot ce contează e descris în fișa de mai sus.
