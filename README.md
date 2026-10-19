# No.code.Vvs — site barbershop

Site de prezentare pentru un barbershop, cu o intrare cinematică (video-ul salonului derulat de scroll)
și o probă virtuală de tunsoare cu AI („Vezi-o pe tine”), inspirat de reel-ul @tmvdesignstudio cu „The Ink Experience”.

## Ce conține

| Secțiune | Ce face |
| --- | --- |
| Preloader | numele urcă literă cu literă, contorul urmărește încărcarea video-ului |
| 00 · Intrarea | video-ul salonului e derulat de scroll pe un canvas; apar pe rând „The Barber Experience → La milimetru → Fără grabă”, apoi titlul și butonul |
| 01 · Studioul | secțiunea urcă peste video ca o cortină; manifestul se „aprinde” cuvânt cu cuvânt; poze cu dezvăluire și parallax; contoare |
| 02 · Servicii | meniul cu prețuri; liniile se desenează, poza urmărește cursorul; click = programare |
| Bandă | text infinit care accelerează și se înclină după viteza scroll-ului |
| 03 · Vezi-o pe tine | selfie → tunsoare (8 modele sau descrisă liber), fade, barbă, culoare → AI → comparator înainte/după → „Programează tunsoarea asta” |
| 04 · Galerie | galerie orizontală fixată pe desktop, glisare pe telefon |
| 05 · Echipa | carduri care se înclină după mouse, poze alb-negru → color |
| 06 · Recenzii | citate care se schimbă singure |
| 07 · Programare | programare online / WhatsApp / telefon, adresă, program |
| Footer | numele uriaș care urcă literă cu literă |

Peste tot: scroll fluid (Lenis), cursor personalizat, butoane magnetice, granulație de film, bară de progres.
Animațiile sunt GSAP (ScrollTrigger + SplitText, gratuite și pentru uz comercial).
Pe telefoanele cu „mișcare redusă” activată, animațiile se opresc automat.

## Structura

```
public/                 site-ul (ce se publică)
  index.html            textele și secțiunile
  css/style.css         design (culori în :root)
  js/config.js          nume, telefon, WhatsApp, link de programare, Instagram
  js/intro.js           intrarea cinematică
  js/tryon.js           proba virtuală
  js/catalog.js         tunsorile, bărbile, culorile
  assets/seq/           cadrele video-ului de intrare (generate cu scriptul de mai jos)
  assets/img/           pozele salonului
functions/api/tryon.js  serverul care trimite selfie-ul la AI (cheia stă aici, nu în browser)
scripts/make-sequence.sh  video → cadre pentru intrare
```

## Vezi site-ul pe calculator

```
cd public && python3 -m http.server 8080
```

Apoi deschide http://localhost:8080. Local, proba virtuală rulează în mod demo.

## Video-ul de intrare

```
scripts/make-sequence.sh intrare.mp4                        # doar orizontal
scripts/make-sequence.sh intrare.mp4 intrare-vertical.mp4   # + varianta de telefon
```

Iese cel mai bine dintr-o singură filmare continuă, făcută mergând încet: afară → ușă → interior → scaun → close-up pe tuns.
Fără video vertical, varianta de telefon se decupează din centrul celui orizontal.

## Publicare (Cloudflare Pages, gratuit și pentru uz comercial)

1. Cloudflare → Workers & Pages → Create → Pages → conectezi acest repository GitHub.
2. Build command: gol. Build output directory: `public`.
3. Settings → Variables and Secrets → adaugi secretul `GEMINI_API_KEY` (cheia din Google AI Studio).
   Opțional, `GEMINI_IMAGE_MODEL`: implicit `gemini-2.5-flash-image`.
4. Custom domains → adaugi domeniul salonului.

Fără `GEMINI_API_KEY`, site-ul merge, iar proba virtuală rulează în mod demo.

## Proba virtuală și datele personale

- Poza e micșorată în browser și trimisă doar pentru generare; nu o salvăm nicăieri.
- Clientul trebuie să bifeze acordul înainte de generare.
- Folosește cheia Gemini pe un proiect cu facturare activă: pe nivelul gratuit, Google poate folosi datele pentru îmbunătățirea produselor.
- Pune în pagina de confidențialitate a salonului o frază despre proba virtuală (procesare de către Google, fără stocare).
