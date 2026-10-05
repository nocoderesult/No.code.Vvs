# Daria — fișa personajului (NU se modifică)

Personaj 100% fictiv, generat cu AI. Nu seamănă intenționat cu nicio persoană reală.

## Identitate
- Nume: **Daria** · vârstă aparentă 27 · nișă: lifestyle & lux (mașini, hoteluri, călătorii, outfit-uri)
- Cuvânt-declanșator LoRA: **d4ria**

## Descrierea fixă (se copiază identic în fiecare prompt — căsuța „Personaj (fix)”)
```
d4ria, a 27-year-old woman with warm olive tan skin, long glossy dark brown hair with subtle chocolate highlights falling past her chest, center part, almond-shaped hazel-brown eyes, defined dark eyebrows, high cheekbones, small straight nose with a slightly rounded tip, full lips, a tiny beauty mark under her left eye, slim athletic hourglass figure, natural skin texture with visible pores
```

## Semne care NU se schimbă niciodată
alunița sub ochiul stâng · cărarea pe mijloc · ochii căprui-alune · tenul măsliniu

## Ce se poate schimba
machiaj (natural ↔ smoky de seară), coafură (liber, coadă, coc lejer), haine, loc, lumină.

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
