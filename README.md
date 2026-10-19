# RA Barbershop — site de prezentare (varianta de telefon)

Site gândit pentru telefon (pe calculator apare ca o coloană de telefon pe centru), cu:

- **Intrare cinematică**: video-ul salonului rulează odată cu scroll-ul. Monograma **RA** urcă
  literă cu literă, apare „BARBERSHOP”, apoi literele devin ferestre prin care se vede video-ul.
  La final apar mesajul și butonul de programare.
- **Studio**: prezentare scurtă și o fotografie.
- **Servicii și tarife**: atingerea unui serviciu deschide programarea cu serviciul ales.
- **Probă virtuală („Vezi-o pe tine”)**: selfie → tunsoare (8 modele sau descrisă liber) → barbă →
  previzualizare AI (GPT Image, OpenAI) → comparator înainte/după → programare cu tunsoarea aleasă.
- **Galerie** cu glisare, **Programări** (online, WhatsApp, telefon, program, adresă) și footer.
- Buton „Programează-te” care rămâne la îndemână în timpul scroll-ului.

Animațiile folosesc doar transform și opacitate (GSAP + ScrollTrigger + SplitText), ca să curgă
lin pe telefon. Pe telefoanele cu „mișcare redusă” activată, animațiile se opresc automat.

## Ce trebuie completat cu datele reale

| Ce | Unde |
| --- | --- |
| Telefon, WhatsApp, localitate, Instagram, link de programare (Booksy/MERO etc.) | `public/js/config.js` |
| Prețuri și durate | `public/index.html`, secțiunea „Servicii” |
| Program | `public/index.html`, secțiunea „Programări” |
| Date pentru Google (telefon, adresă, program) | `public/index.html`, blocul `application/ld+json` |
| Video de intrare și poze proprii | vezi mai jos |

## Structura

```
public/                 site-ul (ce se publică)
  index.html            textele și secțiunile
  css/style.css         designul (culori în :root)
  js/config.js          datele salonului
  js/intro.js           intrarea cu monograma RA
  js/tryon.js           proba virtuală
  js/catalog.js         tunsorile și opțiunile de barbă
  assets/seq/           cadrele video-ului de intrare
  assets/img/           pozele
functions/api/tryon.js  serverul care trimite selfie-ul la OpenAI (cheia stă aici, nu în browser)
worker/index.js         intrarea pe Cloudflare: fișierele din public/ + /api/tryon
wrangler.jsonc          setările Cloudflare
scripts/make-sequence.sh  video → cadre pentru intrare
CREDITS.md              sursele foto/video și licențele
```

## Vezi site-ul pe calculator

```
cd public && python3 -m http.server 8080
```

Apoi deschide http://localhost:8080 (cel mai bine în modul „telefon” al browserului).
Local, proba virtuală rulează în mod demo.

## Video-ul de intrare

```
scripts/make-sequence.sh intrare.mp4
```

Merge orice video; unul orizontal e decupat automat pe centru la format de telefon.
Iese cel mai frumos o filmare calmă, făcută mergând încet prin salon, cu detalii de aproape la final:
acele cadre se văd prin literele RA.

## Publicare

### Cloudflare (site-ul principal, cu AI)

Site-ul rulează ca Worker cu fișiere statice: `wrangler.jsonc` publică folderul `public/`,
iar `worker/index.js` răspunde la `/api/tryon`. Se publică automat de pe ramura `main`.

1. Cloudflare → **Workers & Pages** → **Create** → importă repository-ul `nocoderesult/No.code.Vvs`.
2. Project name: `ra-barbershop` (trebuie să fie identic cu `name` din `wrangler.jsonc`) ·
   Build command: gol · Deploy command: `npx wrangler deploy` · **Enable Preview builds: oprit** → **Deploy**.
3. Proiect → **Settings** → **Variables and Secrets** → **Add** → tip **Secret**, nume `OPENAI_API_KEY`,
   valoarea = cheia OpenAI → **Deploy**. Opțional, ca variabile text: `OPENAI_IMAGE_MODEL`
   (implicit `gpt-image-2.5-flare`; mai precis, dar mai lent: `gpt-image-2.5-sunburst`) și
   `OPENAI_IMAGE_QUALITY` (`low`, `medium` implicit, `high`).
4. Opțional: **Domains & Routes** → domeniul salonului.

Fără `OPENAI_API_KEY`, site-ul merge normal, iar proba virtuală rulează în mod demo.

În contul OpenAI: cheia se face din **API keys**. Contul are nevoie de credit și, pentru modelele
GPT Image, poate cere **Organization verification**. Pune și o **limită lunară de cost**
(Settings → Limits), ca proba virtuală să nu poată depăși un buget fix.

### GitHub Pages (copie gratuită, fără AI)

https://nocoderesult.github.io/No.code.Vvs/ se actualizează automat la fiecare modificare în `public/` pe `main`
(workflow-ul `.github/workflows/publica-site.yml`). Aici proba virtuală rulează în mod demo.

## Proba virtuală și datele personale

- Poza e micșorată în browser și trimisă doar pentru generare; nu o salvăm nicăieri.
- Clientul bifează acordul înainte de generare.
- Pe API, OpenAI nu folosește implicit datele pentru antrenarea modelelor; le poate păstra temporar
  pentru prevenirea abuzurilor.
- În pagina de confidențialitate a salonului trebuie o frază despre proba virtuală
  (procesare de către OpenAI, fără stocare la noi).
