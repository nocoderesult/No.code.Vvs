# Influencer AI: de la idee la postare

Plan complet și structură de lucru pentru un personaj AI propriu: nișă, personaj, set de date, antrenare pe RunPod, generare de conținut, postare pe Instagram, măsurare.

Stare: **plan și schelet**. Scripturile din `automatizare/` sunt scrise după documentația publică, dar **nu au fost rulate** (nu există încă cont RunPod, token Instagram sau personaj final). Fiecare fază de mai jos are un criteriu clar de „gata”.

## Cum arată lanțul

```
01 nișă ──► 02 personaj ──► 03 referințe + set de date ──► 04 LoRA pe RunPod
                                                                  │
09 măsurare ◄── 08 Instagram ◄── 07 calendar ◄── 06 video ◄── 05 imagini
     │                                                            ▲
     └──────────── ce a mers intră înapoi în calendar ────────────┘
```

Fiecare săgeată e un punct de control: nu treci mai departe până nu e bifat criteriul din folderul respectiv.

## Foldere

| Folder | Ce decide sau produce | Gata când |
|---|---|---|
| `00-fundatie/` | reguli, buget, unelte, decizii deschise | regulile sunt citite și deciziile din `decizii.md` au răspuns |
| `01-nisa-si-pozitionare/` | nișa, publicul, ocupația | o nișă câștigă în fișa de punctaj și are 10 conturi de referință |
| `02-personaj/` | fișa completă a personajului | `fisa-personaj.yaml` e completă, fără câmpuri goale |
| `03-referinte-si-dataset/` | poza de bază, fișa de referință, setul de antrenare | 30–40 de poze trecute de controlul de calitate, cu descrieri |
| `04-antrenare-lora-runpod/` | LoRA-ul personajului | LoRA-ul trece testul de asemănare la intensitatea aleasă |
| `05-generare-imagini/` | poze de conținut | fiecare poză trece poarta de calitate |
| `06-video-si-voce/` | reels, voce, colorizare | clipul trece lista de verificare video |
| `07-continut-si-calendar/` | piloni, formate, calendar | două săptămâni de conținut sunt în coadă |
| `08-instagram/` | cont, etichetă AI, publicare | prima postare iese prin API și apare corect |
| `09-masurare-si-iteratie/` | cifre, revizie săptămânală | există o revizie pe săptămână, cu o decizie |
| `10-monetizare/` | surse de venit | abia după ce contul are public constant |
| `automatizare/` | scripturi și arhitectură | vezi fazele de mai jos |
| `cercetare/` | surse și ce nu am putut verifica | — |
| `unelte/` | scripturi mici refolosibile (colorizare) | — |

## Ordinea de lucru

1. **Săptămâna 0, fundația.** Răspunzi la `00-fundatie/decizii.md`. Fără asta, restul e ghicit.
2. **Săptămâna 1, nișa și personajul.** Folderele 01 și 02. Totul pe hârtie, fără nicio generare.
3. **Săptămâna 2, identitatea vizuală.** Folderul 03: poza de bază, fișa de referință, setul de antrenare.
4. **Săptămâna 2–3, LoRA.** Folderul 04. O singură antrenare bună bate zece încercări la întâmplare.
5. **Săptămâna 3, primul lot de conținut.** Folderele 05–07: 14 postări gata înainte de prima publicare.
6. **Săptămâna 4, lansarea.** Folderul 08: cont, etichetă AI, primele postări manual, apoi prin API.
7. **Continuu.** Folderul 09 în fiecare săptămână. Folderul 10 doar după ce cifrele o cer.

## Fazele automatizării

| Fază | Ce se automatizează | Depinde de |
|---|---|---|
| A | structura de foldere, fișa personajului, validarea ei | nimic |
| B | generarea pe RunPod dintr-un fișier de cerere | cont RunPod, workflow ComfyUI exportat |
| C | poarta de calitate și denumirea fișierelor | faza B |
| D | coada de postări și publicarea pe Instagram | cont profesional, aplicație Meta, token |
| E | colectarea cifrelor și raportul săptămânal | faza D |

Automatizarea vine **după** ce un pas a mers o dată de mână. Un pas pe care nu l-ai făcut manual nu știi cum arată când se strică.

## Trei reguli care nu se negociază

1. **Personajul e etichetat ca AI**, pe profil și la postare. E regulă Instagram din 31 august 2026 și obligație legală în UE din 2 august 2026. Detalii în `00-fundatie/reguli.md`.
2. **Nicio persoană reală.** Fără fața, corpul sau clipurile altcuiva, fără „face swap” pe conținutul altor creatori.
3. **Postare doar prin API-ul oficial.** Fără boți de like-uri, de follow sau de comentarii.
