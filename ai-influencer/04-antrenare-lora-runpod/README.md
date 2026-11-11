# 04 · Antrenarea LoRA pe RunPod

LoRA-ul e ce ține fața la fel fără nicio imagine de referință. E pasul care lipsea în sesiunea de până acum, unde fața a variat între generări.

Tot ce e mai jos e plan, scris după documentația și ghidurile publice. **Nu a fost rulat.** Valorile de antrenare sunt puncte de pornire și se confirmă la prima rulare.

## Alegerea modelului de bază

| Model | Ce spun sursele | Observație |
|---|---|---|
| Flux.2 Klein (9B sau 4B) | într-un test pe șase modele a ținut cel mai bine asemănarea; varianta 4B are licență permisivă | pielea poate ieși ceroasă; se compensează din prompt și din set |
| Z-Image (Base pentru antrenare, Turbo pentru generare) | cel mai bun fotorealism brut dintre cele comparate | antrenezi pe Base, generezi pe Turbo |
| Krea 2 | folosit pe platforma HazeGen cu LoRA-uri de realism | nu am găsit comparații independente |
| Qwen Image | mai slab la piele, bun la text în imagine | nu e prima alegere pentru personaj |

Sursele sunt bloguri și forumuri din 2026, nu teste controlate. Recomandarea: antrenezi pe **un** model, verifici pielea pe setul tău și abia apoi încerci al doilea. Verifici licența modelului înainte de uz comercial.

## Pregătirea RunPod, o singură dată

1. Cont, metodă de plată și **limită de cheltuieli** setată.
2. **Volum de rețea** de 50–100 GB, în aceeași regiune cu plăcile pe care le vei folosi. Pe el stau modelele, setul de date și rezultatele.
3. Cheie API, salvată doar în `.env`.
4. Cheie SSH adăugată în cont, pentru transfer de fișiere.

Structura de pe volum:
```
/workspace/
  models/      modele de bază, text encoders, VAE
  datasets/    <personaj>/ poze + descrieri
  output/      <personaj>_v1/ LoRA-uri și mostre
  workflows/   workflow-uri ComfyUI exportate
```

## Antrenarea, pas cu pas

1. Pornești un pod din șablonul **ai-toolkit** (îl găsești căutând „ostris” la Templates), cu volumul atașat și o placă de 24 GB.
2. Urci `dataset/` în `/workspace/datasets/<personaj>/`.
3. Creezi lucrarea din interfață, pornind de la valorile din tabelul de mai jos.
4. Pornești antrenarea și te uiți la mostrele generate la fiecare salvare.
5. Descarci toate punctele de salvare, nu doar ultimul.
6. **Oprești pod-ul.** Volumul rămâne.

## Valori de pornire

| Setare | Valoare | De ce |
|---|---|---|
| Tip de rețea | LoRA standard | recomandat pentru personaje, în locul LoCon |
| Rang | 32 | 32–64 pentru detaliu de față; începi de jos |
| Rezoluție | 1024 | la fel ca pozele din set |
| Pași | 2.000–3.000 | cu salvare la fiecare 250 |
| Mărimea lotului | 1–4 | cât permite memoria plăcii |
| Cuvânt-cheie | cel din descrieri | un cuvânt inventat |
| Mostre | 4 prompturi fixe, aceeași sămânță | ca să compari punctele de salvare între ele |

Prompturile de mostră acoperă: portret, corp întreg, altă ținută, alt loc. Unul dintre ele **nu** conține nimic din setul de antrenare, ca să vezi dacă LoRA-ul generalizează.

## Alegerea punctului de salvare

Nu ultimul e cel mai bun. Semne:

| Semn | Înseamnă |
|---|---|
| fața nu seamănă încă | prea puțini pași |
| fața seamănă, hainele și locul se schimbă la cerere | zona bună |
| aceeași ținută sau același fundal apar orice ai cere | supraantrenat |
| pielea devine ceroasă, cadrele devin rigide | supraantrenat |

## Testul de intensitate

Pentru punctul ales, generezi același prompt cu aceeași sămânță la intensități de la 0,4 la 1,2, din 0,1 în 0,1. Alegi cea mai mică intensitate la care fața e clar a ei. Ghidurile dau 0,7–1,0 ca zonă obișnuită.

Rezultatul se scrie în `rezultate.md`: modelul, punctul de salvare, intensitatea, data.

## Testul de acceptare

LoRA-ul e bun dacă, la intensitatea aleasă, din 20 de generări pe prompturi noi:

- [ ] cel puțin 16 sunt clar aceeași femeie;
- [ ] semnele fixe apar în cele mai multe prim-planuri;
- [ ] ținuta și locul se schimbă după prompt;
- [ ] pielea are textură;
- [ ] merge și în cadre care nu erau în set (de exemplu în mașină).

Dacă pică, nu mărești pașii orbește. Te uiți întâi la set: de obicei problema e acolo.

## Greșeli care costă

- pod lăsat pornit după antrenare;
- modele descărcate pe discul pod-ului, nu pe volum, deci pierdute la oprire;
- un singur punct de salvare păstrat;
- set de date fără copie de siguranță;
- reantrenare fără să notezi ce ai schimbat.

## Gata când

- [ ] LoRA-ul trece testul de acceptare;
- [ ] `rezultate.md` are modelul, punctul de salvare și intensitatea;
- [ ] fișierul `.safetensors` are copie în afara RunPod;
- [ ] pod-ul e oprit.
