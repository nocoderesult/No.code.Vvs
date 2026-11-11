# 02 · Personajul

Personajul e o fișă scrisă, nu o poză. Poza vine din fișă. Tot ce nu e scris aici se va schimba singur de la o generare la alta.

## Fișierul principal

`fisa-personaj.yaml`, pornit din `fisa-personaj.sablon.yaml`. E sursa unică: din el se construiesc prompturile, descrierile și tonul.

## Ce conține și de ce

| Secțiune | Detalii care se uită de obicei |
|---|---|
| Identitate | vârstă exactă, zi de naștere, oraș, limbă, înălțime |
| Față | forma feței, maxilar, pomeți, nas, buze, ochi, sprâncene, urechi, dinți |
| Semne fixe | alunițe, pistrui, cicatrici, piercing: **poziția exactă**, stânga sau dreapta |
| Păr | culoare, rădăcini, lungime, textură, cărare, cum îl poartă la sală și seara |
| Corp | tip, proporții, postură, mâini, unghii |
| Piele | nuanță, textură, ce imperfecțiuni are și unde |
| Machiaj | de zi, de seară, la sală |
| Garderobă | 5–7 ținute de bază, culori permise, culori interzise, bijuterii |
| Locuri | 3–5 locuri care se repetă, descrise fix: dormitor, sală, cafenea |
| Obiecte | telefonul și husa lui, cana, geanta, mașina |
| Personalitate | trei trăsături, un defect, ce o enervează, ce o amuză |
| Voce scrisă | cum scrie: lungimea frazelor, emoji, cuvinte proprii, cuvinte interzise |
| Voce vorbită | ton, ritm, accent, o voce de referință |
| Poveste | de unde e, ce face, ce vrea, ce nu spune |
| Limite | ce nu face și nu spune niciodată personajul |

## De ce contează detaliile fixe

Un om real are aceeași aluniță în fiecare poză, același dormitor și același telefon. Lipsa lor e ce trădează un personaj generat. De aceea:

- **Semnele fixe** se scriu cu poziție: „aluniță mică deasupra buzei, pe stânga ei”.
- **Locurile** se descriu o dată și se refolosesc cuvânt cu cuvânt.
- **Obiectele personale** apar la fel: aceeași husă de telefon în fiecare selfie în oglindă.

Stânga și dreapta se scriu mereu din perspectiva personajului, nu a privitorului. Într-un selfie în oglindă imaginea e inversată, deci notezi și asta.

## Blocul de identitate

Din fișă se scrie un singur paragraf în engleză, **blocul de identitate**, care intră neschimbat în fiecare prompt. Regulile lui:

- același text, cuvânt cu cuvânt, de fiecare dată;
- conține vârsta și faptul că e femeie adultă;
- conține fața, părul, semnele fixe și corpul;
- nu conține haine, loc sau lumină, care se schimbă de la o poză la alta;
- nu conține cuvinte care împing spre plastic: „flawless”, „perfect skin”, „stunning”, „doll”.

Blocul se salvează în `bloc-identitate.txt`.

## Gata când

- [ ] `fisa-personaj.yaml` nu are câmpuri goale;
- [ ] `bloc-identitate.txt` există și are sub 120 de cuvinte;
- [ ] semnele fixe au poziție scrisă;
- [ ] există cel puțin 5 ținute și 3 locuri descrise;
- [ ] vocea scrisă are 5 exemple de descrieri de postare.
