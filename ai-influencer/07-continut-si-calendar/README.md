# 07 · Conținut și calendar

Calendarul leagă personajul de postare. Fiecare rând din `calendar.csv` e o postare cu tot ce îi trebuie.

## Pilonii de conținut

Trei până la cinci teme care se repetă. Fiecare postare aparține unuia.

| Pilon | Pondere | Exemplu |
|---|---|---|
| Util | 40% | ceva ce publicul poate folosi azi, din ocupația ei |
| Viața ei | 30% | ziua obișnuită, locurile care se repetă |
| Personalitate | 20% | păreri, umor, lucruri care o enervează |
| Comunitate | 10% | răspunsuri la comentarii, întrebări către public |

Pilonii se rescriu după nișa aleasă în `01`.

## Formate

| Format | La ce e bun | Cost de producție |
|---|---|---|
| Reel | public nou | mare |
| Carusel | salvări și distribuiri, explică ceva pas cu pas | mediu |
| Poză | prezență, legătură cu publicul existent | mic |
| Story | zilnic, informal, nu rămâne pe profil | mic |

## Ritmul săptămânal de pornire

| Zi | Ce |
|---|---|
| Luni | reel, pilon util |
| Marți | story |
| Miercuri | carusel, pilon util |
| Joi | story |
| Vineri | reel, pilon personalitate |
| Sâmbătă | poză, pilon viața ei |
| Duminică | story și revizia săptămânii |

Trei–patru postări pe săptămână, ținute constant, bat șapte postări într-o săptămână și zero în următoarea. Ritmul se ajustează după timpul din `00-fundatie/decizii.md`.

## Coloanele din calendar

| Coloană | Ce conține |
|---|---|
| `data`, `ora` | când se publică |
| `pilon`, `format` | din tabelele de mai sus |
| `idee` | o propoziție |
| `loc`, `tinuta` | nume din fișa personajului, nu descrieri noi |
| `prima_fraza` | cârligul: primele cuvinte din clip sau din descriere |
| `descriere` | textul postării, în vocea ei |
| `indemn` | un singur lucru cerut publicului |
| `fisier` | calea către poza sau clipul acceptat |
| `stare` | idee, generat, acceptat, programat, publicat |
| `publicat_id` | identificatorul primit de la Instagram |

## Continuitatea

Detaliile care fac un personaj credibil în timp:

- **anotimp și vreme:** fără rochie de vară în ianuarie;
- **ora:** lumina din poză se potrivește cu ora postării;
- **locuri:** aceleași trei–cinci locuri, descrise la fel;
- **garderobă:** hainele se repetă, ca la un om real;
- **firul poveștii:** dacă a spus că are examen joi, vineri pomenește cum a fost;
- **zilele speciale:** ziua ei, sărbători, evenimente din orașul ei.

Un fișier `continuitate.md` ține ce a „spus” și „făcut” personajul, ca să nu se contrazică.

## Descrierea postării

1. prima frază, care se vede fără „mai mult”;
2. două–patru rânduri de conținut;
3. un singur îndemn;
4. trei–cinci hashtaguri legate de subiect.

Descrierile se scriu în vocea din fișa personajului. Pentru ele se pot folosi skill-urile `caption-writer`, `reel-script`, `carousel-builder` și `content-calendar`.

## Reguli

- fiecare postare primește dezvăluirea de conținut AI;
- nimic prezentat ca experiență reală a unui om: „am încercat” devine „uite cum arată”;
- reclamele se marchează;
- nu se copiază postările altor conturi, nici textul, nici cadrul.

## Gata când

- [ ] pilonii sunt scriși pentru nișa aleasă;
- [ ] calendarul are 14 zile completate;
- [ ] fiecare rând are fișier acceptat și descriere;
- [ ] `continuitate.md` există.
