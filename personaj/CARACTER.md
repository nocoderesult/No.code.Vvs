# Daria — fișa personajului (NU se modifică)

Personaj 100% fictiv, generat cu AI. Nu seamănă intenționat cu nicio persoană reală.

## Identitate
- Nume: **Daria** · vârstă aparentă 25 · nișă: lifestyle & lux (mașini, hoteluri, călătorii, outfit-uri)
- Cuvânt-declanșator LoRA: **d4ria**

## Descrierea fixă (se copiază identic în fiecare prompt — căsuța „Personaj (fix)”)
```
d4ria, a 25-year-old woman with radiant warm tan skin, a sleek jet-black bob haircut ending at her jawline with a sharp side part, piercing almond-shaped green-hazel eyes, long voluminous dark eyelashes, dark sculpted eyebrows, full dusty-pink lips, high cheekbones with a soft natural glow, small diamond stud earrings, clear smooth neck, athletic hourglass figure with a narrow toned waist, full proportionate bust and rounded hips, toned legs, medium almond-shaped nude-pink nails, natural skin texture with visible pores
```

## Semne care NU se schimbă niciodată (checklist la fiecare poză)
- [ ] bob negru-corb până la maxilar, cărare laterală
- [ ] ochi verzi-alune, migdalați
- [ ] ten bronzat cald
- [ ] cercei mici cu diamant
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
- Look 100% realist, dar contul e marcat ca AI: în bio „AI creator ✨” + eticheta „AI info” la postări
  (regula Meta pentru conținut fotorealist AI + AI Act în UE).
- Înainte de lansare: 9–12 postări gata, ca grila să arate plină din prima zi.

## Note de consistență
- Fără tatuaje: dacă apare vreun tatuaj într-o poză din set, se scoate cu edit („remove the tattoo, keep everything else identical”) sau poza nu intră în set. La generare: „tattoo” în negative prompt.
- Detaliile nedescrise (alunițe, semne) sunt aleatorii până la LoRA → tot ce contează e descris în fișa de mai sus.
