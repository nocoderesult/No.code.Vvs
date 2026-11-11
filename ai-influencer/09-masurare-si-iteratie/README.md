# 09 · Măsurare și iterație

O dată pe săptămână te uiți la cifre și iei **o** decizie. Fără asta, calendarul rămâne ghicit.

## Ce măsori

| Cifră | Ce îți spune |
|---|---|
| Conturi atinse care nu te urmăresc | dacă algoritmul te arată cuiva nou |
| Timp mediu de vizionare la reels | dacă primele secunde țin omul |
| Distribuiri | cel mai puternic semn că a plăcut |
| Salvări | că a fost util |
| Comentarii | că a stârnit o reacție |
| Urmăritori noi pe postare | ce aduce public |
| Vizite pe profil | că a trezit curiozitate |

Aprecierile singure spun puțin. Numărul de urmăritori e un rezultat, nu ceva ce poți regla direct.

## Jurnalul

`jurnal-postari.csv` are un rând pe postare, completat la 24 de ore și actualizat la 7 zile. Coloanele `pilon`, `format`, `loc` și `tinuta` vin din calendar, ca să poți compara.

## Revizia săptămânală, 30 de minute

1. Sortezi postările săptămânii după distribuiri și după conturi noi atinse.
2. La primele două: ce au în comun? Pilonul, formatul, cârligul, locul?
3. La ultimele două: ce le-a lipsit?
4. Citești comentariile și notezi întrebările care se repetă.
5. Iei **o singură decizie** pentru săptămâna următoare și o scrii în `decizii-saptamanale.md`.

Exemple de decizii: „încă două reels cu același cârlig”, „renunț la pozele în cafenea”, „mut postarea de vineri la ora 19”.

## Experimente

Schimbi un singur lucru o dată și îl ții cel puțin două săptămâni.

| Ce testezi | Variante |
|---|---|
| Cârligul | întrebare / afirmație / text pe ecran |
| Ora | dimineață / prânz / seară |
| Lungimea reel-ului | 7 secunde / 15 / 30 |
| Coperta | față apropiată / corp întreg / text |
| Descrierea | scurtă / poveste |

Cu puține postări, diferențele mici sunt întâmplare. Tragi concluzii doar din diferențe mari și repetate.

## Semne că trebuie schimbat ceva mai mare

| Semn | Unde te întorci |
|---|---|
| nimeni nou nu vede postările, patru săptămâni la rând | `01`, nișa, sau `07`, cârligele |
| oamenii văd, dar nu urmăresc | `02`, personajul nu are destulă personalitate |
| comentarii „pare fals” | `05`, realismul, și verifici eticheta AI |
| fața diferă între postări | `04`, LoRA-ul |
| nu ții ritmul | `07`, mai puține postări, formate mai ieftine |

## Gata când

- [ ] jurnalul e la zi;
- [ ] există o revizie pentru fiecare săptămână;
- [ ] fiecare revizie se încheie cu o decizie scrisă.
