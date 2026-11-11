# Automatizare

Trei scripturi mici, fără dependențe în afară de PyYAML la validare. Fiecare face un singur lucru și poate fi rulat de probă, fără să trimită nimic.

| Script | Ce face | Stare |
|---|---|---|
| `valideaza_fisa.py` | verifică fișa personajului | rulat pe șablon |
| `runpod_comfy.py` | rulează un workflow ComfyUI pe RunPod și salvează pozele | doar modul de probă a fost rulat |
| `instagram_publica.py` | publică rândurile programate din calendar | doar modul de probă a fost rulat |

Niciun script nu a fost rulat împotriva unui serviciu real. Înainte de prima folosire reală le verifici pe o singură cerere.

## Pregătire

```bash
cp .env.exemplu .env
```

Completezi `.env`. Fișierul nu intră în git.

## Lanțul

```
fisa-personaj.yaml ──► valideaza_fisa.py
                              │
cerere.json ──► runpod_comfy.py ──► iesiri/AAAA-LL-ZZ/ ──► [poarta de calitate, de mână] ──► acceptate/
                                                                                                │
                                                     [urcare la o adresă publică, de mână] ◄────┘
                                                                    │
calendar.csv (stare=programat) ──► instagram_publica.py ──► postare + publicat_id în calendar
```

Cei doi pași din paranteze drepte rămân manuali, cu intenție:

- **Poarta de calitate.** O poză greșită publicată automat costă mai mult decât timpul de verificare.
- **Urcarea fișierelor.** Depinde de unde alegi să le găzduiești.

## Comenzi

Validarea fișei:

```bash
python valideaza_fisa.py ../02-personaj/fisa-personaj.yaml
```

Generare, de probă, apoi reală:

```bash
python runpod_comfy.py ../05-generare-imagini/cereri/exemplu.json --proba
```

```bash
python runpod_comfy.py ../05-generare-imagini/cereri/exemplu.json --iesire ../05-generare-imagini/iesiri/2026-11-12
```

Publicare, de probă, apoi reală, câte o postare:

```bash
python instagram_publica.py ../07-continut-si-calendar/calendar.csv
```

```bash
python instagram_publica.py ../07-continut-si-calendar/calendar.csv --publica --maxim 1
```

## Ce protecții are publicarea

- rulează de probă dacă nu primește `--publica`;
- publică doar rânduri cu `stare=programat` și data trecută;
- oprește rândurile fără descriere, fără adresă https sau cu format greșit;
- publică cel mult `--maxim` postări la o rulare (implicit una);
- citește limita contului înainte de fiecare postare;
- rescrie calendarul după fiecare postare, ca o întrerupere să nu ducă la o postare dublă.

## Ce lipsește, pe faze

| Fază | De construit | Depinde de |
|---|---|---|
| B | un workflow ComfyUI exportat și un fișier de cerere real | LoRA-ul din `04` |
| B | construirea promptului din fișa personajului și din calendar | fișa completă |
| C | redenumirea și mutarea automată a fișierelor acceptate | regulile de nume din `05` |
| D | urcarea fișierelor la o adresă publică | alegerea găzduirii |
| D | parametrul de dezvăluire AI din API | documentația Meta curentă |
| D | rulare la oră fixă | un loc care rulează zilnic |
| E | citirea cifrelor fiecărei postări în `jurnal-postari.csv` | permisiunea de statistici a aplicației |

Ordinea contează: fiecare fază se construiește după ce pasul ei a fost făcut o dată de mână.

## Ce nu intră aici

Niciun script de follow, like, comentarii sau mesaje automate și nimic care ocolește API-ul oficial.
