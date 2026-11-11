# Reguli

Regulile astea vin înaintea oricărei decizii creative. Unele sunt lege, altele sunt reguli de platformă, altele sunt limitele proiectului.

## 1. Dezvăluirea că e AI

| Unde | Ce trebuie | De unde vine |
|---|---|---|
| Profilul Instagram | eticheta „AI-generated profile” activată | regulă Instagram anunțată pe 31 august 2026: conturile fără etichetă pot avea distribuția limitată; cele care se etichetează singure nu sunt penalizate |
| Fiecare postare | dezvăluirea de conținut AI la publicare | eticheta „AI info”; din 22 iunie 2026 API-ul de publicare acceptă dezvăluirea direct la postare |
| Bio | o mențiune clară, de exemplu „personaj creat cu AI” | bună practică, acoperă și cerința legală de vizibilitate |
| Legal, UE | dezvăluire **vizibilă pentru public** că imaginea e generată | AI Act, articolul 50(4), aplicabil din 2 august 2026; un marcaj invizibil în fișier nu ajunge |
| Platforme de abonament | eticheta AI a platformei | platformele care acceptă modele AI o cer pe profil |

De verificat înainte de lansare: textul exact al regulii Instagram și numele parametrului de dezvăluire din API. Sursele sunt articole de presă și jurnalul de modificări Meta, nu am citit pagina de politică propriu-zisă.

## 2. Persoane reale

- Personajul e **original**. Nu pornește de la fața unei persoane reale și nu seamănă intenționat cu una.
- Nu folosim poze sau clipuri ale altor creatori ca bază pentru „face swap” sau „character swap”.
- Pozele altora pot fi **inspirație de stil** (lumină, cadru, ținută), descrise în cuvinte. Nu intră ca imagine de referință pentru identitate.
- Dacă o generare iese semănând cu o persoană cunoscută, se aruncă.

## 3. Conținut

- Personajul e adult, descris explicit ca atare în fiecare prompt de bază.
- Conținutul e potrivit pentru Instagram: fără nuditate, fără conținut sexual explicit.
- Fără afirmații false prezentate ca fapte: personajul nu „a testat” un produs, nu „a fost” într-un loc real ca martor, nu dă sfaturi medicale sau financiare ca expert.
- Reclamele se marchează ca reclame.

## 4. Postare și creștere

- Publicare doar prin API-ul oficial Instagram sau din aplicație.
- Fără cumpărat de urmăritori, fără boți de interacțiune, fără rețele de conturi care se comentează între ele.
- Fără promisiuni către public pe care un personaj AI nu le poate ține (întâlniri, apeluri „reale”).

## 5. Drepturi

- Verifici licența fiecărui model de bază și LoRA folosit înainte de uz comercial. Unele modele sunt doar pentru uz necomercial.
- Muzica din reels vine din biblioteca Instagram sau are licență.
- Logo-urile și mărcile din cadru se evită sau se scot.

## 6. Date și chei

- Cheile (RunPod, Meta) stau doar în `.env`, care nu intră în git.
- Depozitul `no.code.vvs` este **public**. Nimic sensibil nu se urcă acolo: nici chei, nici setul de date, nici LoRA-ul.
