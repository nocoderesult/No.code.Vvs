# Daria — fișa personajului (NU se modifică)

Personaj 100% fictiv, generat cu AI. Nu seamănă intenționat cu nicio persoană reală.

## Identitate
- Nume: **Daria** · vârstă aparentă 25 · nișă: lifestyle & lux (mașini, hoteluri, călătorii, outfit-uri)
- Cuvânt-declanșator LoRA: **d4ria**

## Descrierea fixă (se copiază identic în fiecare prompt — căsuța „Personaj (fix)”)
```
d4ria, a 25-year-old woman with radiant warm tan skin, a sleek jet-black bob haircut ending at her jawline with a sharp side part, piercing almond-shaped green-hazel eyes, long voluminous dark eyelashes, dark sculpted eyebrows, full dusty-pink lips, high cheekbones with a soft natural glow, small diamond stud earrings, slim athletic hourglass figure, natural skin texture with visible pores
```

## Semne care NU se schimbă niciodată
bob negru-corb până la maxilar cu cărare laterală · ochii verzi-alune · tenul bronzat · cerceii mici cu diamant

## Ce se poate schimba
machiaj (natural ↔ smoky de seară), coafură (bob drept, bob ondulat, după urechi, ud), haine, loc, lumină.

## Etape
1. **Fața** – 40 de portrete (`01_fata.txt`), alegi UNA singură.
2. **Setul de antrenare** – 30 de imagini cu aceeași față (`02_dataset_edit.txt`), făcute prin editare din fața aleasă.
3. **LoRA** – antrenare pe pod (AI Toolkit), cuvânt-declanșator `d4ria`.
4. **Conținut** – workflow `krea2_studio` + LoRA pornit + scene din `03_scene_lux.txt`.
5. **Verificare** – fiecare poză nouă se compară cu fața de referință; ce nu seamănă se șterge.

## Instagram
- Look 100% realist, dar contul e marcat ca AI: în bio „AI creator ✨” + eticheta „AI info” la postări
  (regula Meta pentru conținut fotorealist AI + AI Act în UE).
- Înainte de lansare: 9–12 postări gata, ca grila să arate plină din prima zi.
