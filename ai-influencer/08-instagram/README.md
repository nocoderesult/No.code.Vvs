# 08 · Instagram

Cont, etichetă AI, publicare prin API-ul oficial. Scriptul din `automatizare/instagram_publica.py` e scris după documentația Meta, dar **nu a fost rulat**.

## Pregătirea contului

1. Cont nou sau existent, trecut pe **cont profesional**. Unele surse spun că publicarea prin API merge doar pe conturi Business, nu și Creator; verifici în documentația Meta înainte să alegi.
2. Poza de profil: un prim-plan acceptat, față clară.
3. Bio: fraza de poziționare, pe scurt, plus dezvăluirea („personaj creat cu AI”).
4. **Eticheta „AI-generated profile” activată** din setările contului.
5. Autentificare în doi pași.
6. Nouă postări gata înainte de a face contul vizibil, ca profilul să nu arate gol.

## Primele două săptămâni

Nu am găsit date independente despre „încălzirea” unui cont nou; ce urmează e precauție, nu regulă dovedită.

- primele postări se fac **manual**, din aplicație;
- ritm mic la început, apoi cel din calendar;
- fără acțiuni în masă: fără zeci de follow-uri sau comentarii pe oră;
- API-ul se conectează după ce contul are deja câteva postări făcute de mână.

## Publicarea prin API

Ce trebuie: aplicație în Meta for Developers, permisiunea de publicare de conținut, un token cu durată lungă și identificatorul contului Instagram.

Fluxul are trei pași:

1. **Creezi un container** cu adresa publică a fișierului și descrierea.
2. **Aștepți** până containerul e procesat. La video durează.
3. **Publici** containerul.

Pentru carusel creezi câte un container pentru fiecare imagine, apoi unul părinte care le leagă.

### Limite

| Ce | Valoare | Sursă |
|---|---|---|
| Postări prin API | 100 în 24 de ore, fereastră mobilă | documentația Meta; unele pagini mai vechi spun 50 sau 25 |
| Carusel | contează ca o singură postare | documentația Meta |
| Imagini într-un carusel prin API | 2–10 | ghiduri terțe |
| Reel | MP4 sau MOV, 9:16, 5–90 de secunde pentru fila Reels | ghiduri terțe |

Valoarea reală a limitei se citește din API, de la `content_publishing_limit`. Scriptul o verifică înainte de fiecare publicare.

### Fișierul trebuie să fie la o adresă publică

API-ul nu primește fișierul direct, ci îl descarcă de la o adresă. Ai nevoie de un loc de găzduire: un bucket de stocare sau un folder servit public. Adresa trebuie să rămână valabilă până se termină publicarea.

### Dezvăluirea de conținut AI

Din 22 iunie 2026, API-ul de publicare acceptă dezvăluirea de conținut AI la postare. **Numele exact al parametrului nu l-am verificat**; în script e lăsat ca setare de completat din documentația curentă. Până atunci, eticheta se pune manual, din aplicație.

## Ce nu se automatizează

- răspunsurile la comentarii și la mesaje: le scrii sau le aprobi tu, una câte una;
- follow, like, comentarii pe alte conturi;
- orice ocolește API-ul oficial (automatizare de browser, aplicații neoficiale). Riscul e pierderea contului.

## După publicare

- verifici postarea în aplicație: copertă, descriere, etichetă AI;
- treci `publicat_id` în calendar;
- răspunzi la comentarii în prima oră;
- cifrele se culeg la 24 de ore și la 7 zile, în `09-masurare-si-iteratie/`.

## Gata când

- [ ] contul e profesional și are eticheta de profil AI;
- [ ] nouă postări sunt publicate manual;
- [ ] aplicația Meta are permisiunea de publicare;
- [ ] o postare de probă a ieșit prin script și arată corect în aplicație.
