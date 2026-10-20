# PLAN COMPLET: studio și platformă de marketing cu caractere AI

*Numele: **MUSQAI** (Marketing Universe Studio · Quantum AI). Versiunea 1, octombrie 2026. E un document viu: îl actualizăm după fiecare etapă. Deciziile și progresul se notează în `plan/JURNAL.md`. Planul zi cu zi și site-ul sunt în `musqai/`.*

---

## 0. Rezumatul pe o pagină

- **Ce construim:** un studio care dă afacerilor **ambasadori AI** și conținut gata de postat: poze, reels, texte, ore de postare, rapoarte. La început e serviciu, apoi devine platformă. Pornim în română, apoi trecem în Europa de Est.
- **De ce noi:** competitorii (Higgsfield, Arcads, Predis, Ocoya etc.) fac bucăți separate, în engleză, pentru marketeri mari. Noi legăm totul cap-coadă, local, cu **învățare din rezultate** și **conformitate cu AI Act** încă din construcție.
- **Cum facem bani:**
  1. **acum:** servicii pentru firme, după modelul de bani din `skills/money-model`;
  2. **după ce automatizăm:** abonamente pe platformă, cu credite;
  3. **contracte de brand** pentru caracterele casei (Daria și celelalte).
- **Ordinea:** validăm pe bani reali → automatizăm ce funcționează → deschidem platforma.
- **Nișele le testăm pe rând, cu același protocol:**
  1. magazine online;
  2. imobiliare;
  3. turism și HoReCa;
  4. evenimente;
  5. wellness și cosmetice, doar cu reguli stricte.

  Saloanele sunt pe pauză.
- **Primul pas:** Daria live + mostre pentru nișa 1 + primele 30 de contacte.

---

## 1. Viziune și poziționare

**Viziune pe 3 ani:** cea mai simplă cale pentru o afacere mică din regiune să aibă un ambasador AI propriu și conținut care vinde, fără agenție scumpă.

**Promisiunea către client:**
> „Conținut nou în fiecare săptămână, cu un ambasador care arată mereu la fel, fără ședințe foto. Și știi exact ce a adus.”

**Cei 5 diferențiatori:**
1. **Local:** limba română nativ (texte, voce, hashtag-uri, ore de postare) și înțelegerea pieței.
2. **Cap-coadă:** caracter → idei → poze și video → editare → postare → rezultate.
3. **Învață din rezultate:** fiecare postare e etichetată și măsurată, iar recomandările devin mai bune cu fiecare client.
4. **Legal din construcție:** etichetă AI automată, marcaj în fișier, acord pentru fețe reale, fără mărturii false.
5. **Clientul își deține caracterul.**

**Ce facem (regula Higgsfield):** integrăm rapid cel mai bun model nou de pe piață, nu antrenăm modele proprii de la zero.

**Ce NU facem, niciodată:**
- conținut NSFW;
- fețe reale fără acord scris;
- persoane care par minore;
- mărturii false („clientă mulțumită”);
- promisiuni medicale sau de rezultat corporal;
- conținut politic.

### Competitorii, pe scurt

| Competitor | Ce face | Ce învățăm de la ei |
|---|---|---|
| Higgsfield | caractere AI + video (Soul ID, AI Influencer Studio) | livrează foarte repede, integrează orice model nou în 24 h, CEO-ul construiește în public, unelte gratuite care aduc trafic |
| Arcads | reclame video cu „actori” AI | ~10 mil. $ venit anual în ~22 de luni, cu **vânzări directe** și un rezultat clar (reclame care vând) |
| The Clueless (Aitana) | agenție cu personaj AI | personajul e o afacere în sine, cu contracte de brand |
| Predis, Ocoya, Apaya | conținut + programare + analiză | automatizarea e standard; diferența o face calitatea și nișa |
| Buffer, Sprout, Metricool | orele de postare | orele generale sunt slabe. Orele bune vin din **datele contului** |

---

## 2. Principii de lucru

1. **Validăm înainte să construim.** Nu scriem cod pentru o funcție pe care n-a cerut-o sau n-a plătit-o niciun client.
2. **Fiecare postare e o informație.** O notăm în tabelul de rezultate (§14).
3. **Un singur lucru odată:** o nișă activă și un singur caracter nou o dată.
4. **Livrăm repede, corectăm repede:** pilot mic → feedback → îmbunătățire.
5. **Totul scris:** deciziile și progresul stau în acest repo, care e memoria noastră.
6. **Calitate înaintea cantității:** mai bine 3 clipuri perfecte decât 10 care arată „a AI”.
7. **Regulile din `skills/money-model`:** nu vindem același lucru mai ieftin, creștem prețul în trepte, dăm banii înapoi dacă cineva îi cere, nu mințim niciodată.

---

## 3. Ce avem deja

| Ce | Stare |
|---|---|
| Daria: fișa, fața, corpul | ✅ `personaj/CARACTER.md` |
| LoRA v1 Daria (Krea 2) | ✅ cel mai bun checkpoint: pasul 2500. Ai făcut și un v3 |
| Setul de antrenare v2 (34 de poze) | 📝 planul e gata: `personaj/04_dataset_v2.md` + `04_captions_v2.txt` |
| Pod RunPod + ComfyUI + agentul de pe pod | ✅ volum de 250 GB, L40S, contextul în `DARIA_CONTEXT.md` pe pod |
| Imagini: Krea 2 + realism (Z-Image) | ✅ merge. De rezolvat aspectul de plastic (LoRA v2) |
| Video | SCAIL-2 pentru înlocuire (de instalat complet). MiniMax H3 și Qwen rămân pe volum. Wan 2.2 de evaluat |
| Voce | HeyGen / ElevenLabs. Vocea „Daria” trebuie salvată |
| Skill-uri | ✅ conținut: caption, carusel, calendar, reel-script, DM, nișă, statistici, prompt-builder. ✅ vânzare: `money-model`, `sales-call`, `abonament-retentie` |
| Conturile de social media ale Dariei | ❌ de făcut |

---

## 4. Caracterele casei (5)

| # | Nume de lucru | Rol | Nișe | Când îl facem |
|---|---|---|---|---|
| 1 | **Daria** | ambasadoare lifestyle & lux | magazine online (modă, accesorii), turism, evenimente | acum |
| 2 | **„Ambasadorul”** (bărbat, 30–35 de ani) | elegant, încrezător, „omul de business” | imobiliare, auto, modă masculină, servicii | când nișa imobiliare arată interes |
| 3 | **„Exploratoarea”** (28–32 de ani, alt stil decât Daria) | travel & food | turism, HoReCa | la sprintul turism |
| 4 | **„Vecina de alături”** (25–30 de ani, look natural, accesibil) | stil UGC autentic, produse de zi cu zi | magazine online mass-market, home decor | când magazinele cer un look mai „de zi cu zi” |
| 5 | **„Fața platformei”** | explică AI și marketing, promovează studioul | promovarea noastră | în faza 2 (platforma) |

**Reguli pentru orice caracter:**
- **adult clar** (25+) și **fictiv**: nu seamănă intenționat cu nicio persoană reală;
- **fișă scrisă**, ca `personaj/CARACTER.md`;
- **set de antrenare** pe structura v2: 12 poze cu fața + 10 de studio + 12 „insta”;
- **LoRA pentru imagini**, plus LoRA video (Wan) când e nevoie;
- **voce proprie salvată**, aceeași mereu;
- **conturi etichetate AI**.

---

## 5. Nișele, testate pe rând

### 5.1 Protocolul de test (același pentru fiecare nișă, ~3 săptămâni)

| Săpt. | Ce facem |
|---|---|
| 1 | Profilul clientului ideal + o listă cu 30 de firme + **5 mostre** făcute pe produsele sau locațiile lor reale. Mostrele le arătăm doar firmei respective și nu le publicăm fără acordul ei |
| 2 | Contactăm cele 30 de firme (DM + email) și revenim după 3 și după 7 zile |
| 3 | Discuții (după `skills/sales-call`), oferte de pilot, apoi decizia |

**Pragurile de decizie** (sunt de pornire și le ajustăm):
- **≥ 15% răspunsuri** (≥ 5 din 30);
- **≥ 3 discuții reale**;
- **≥ 1 pilot plătit**, sau 2 piloți cu acord de studiu de caz.

✅ Dacă pragurile sunt atinse, nișa trece la livrare. ❌ Dacă nu, notăm în jurnal de ce și trecem la următoarea nișă. **Schimbăm mesajul și oferta înainte să abandonăm nișa.**

### 5.2 Fișele nișelor

#### N1. Magazine online mici (modă, accesorii, bijuterii, home decor)
- **Clientul ideal:** brand românesc cu magazin online (Shopify, WooCommerce sau Instagram Shop), 1–20 angajați, **care rulează deja reclame**. Verifici în Meta Ad Library: dacă rulează reclame, are buget.
- **Durerea:** reclamele se „ard” repede, ședințele foto sunt scumpe și n-au o față constantă.
- **Ce livrăm:**
  - poze lifestyle cu produsul pe Daria;
  - reels de 8–15 secunde, pentru reclame și organic;
  - variante de hook pentru testare A/B;
  - textele.
- **Reguli speciale:**
  - produsul trebuie **identic cu realitatea**: folosim pozele lor ca referință;
  - Daria e **ambasadoare AI declarată**, nu „clientă”;
  - postările au etichetă AI.
- **Unde găsim clienți:** Meta Ad Library, TikTok Shop, Instagram, listele de magazine românești, marketplace-uri.
- **Metrica clientului:** CTR și ROAS ale reclamelor cu Daria față de reclamele lor vechi; costul pe creativ.

#### N2. Imobiliare (dezvoltatori premium, agenții de top)
- **Durerea:** fac puțin video, producția e scumpă, iar ansamblurile sunt greu de „vândut” emoțional.
- **Ce livrăm:**
  - un prezentator AI (Ambasadorul sau Daria) în video cu **proprietatea reală, filmată real**;
  - „o zi în viața ta aici”;
  - noutăți de piață săptămânale.
- **Reguli speciale:** nu inventăm finisaje, priveliști sau dotări. Etichetă AI.
- **Unde găsim clienți:** portaluri imobiliare, site-urile dezvoltatorilor, LinkedIn.
- **Metrica clientului:** cereri de vizionare, lead-uri.

#### N3. Turism și HoReCa (hoteluri boutique, pensiuni premium, rooftop, spa)
- **Durerea:** conținutul e sezonier, fotografii sunt scumpi și au nevoie de „atmosferă”.
- **Ce livrăm:** Daria sau Exploratoarea „descoperă” locul, **declarată ambasador AI, nu oaspete real**. Reels de atmosferă pe imagini reale ale locației.
- **Reguli speciale:** nu inventăm facilități și nu facem recenzii false.
- **Unde găsim clienți:** Booking și Google Maps. Rating mare + Instagram slab = oportunitate.
- **Metrica clientului:** rezervări și mesaje venite din Instagram.

#### N4. Evenimente și nightlife (cluburi, organizatori, festivaluri mici)
- **Ce livrăm:** teasere, anunțuri, numărătoare inversă cu Daria.
- **Reguli speciale:** respectăm regulile de reclamă pentru alcool. Etichetă AI.
- **Metrica clientului:** bilete vândute, înscrieri.

#### N5. Wellness, fitness, cosmetice (doar cu reguli stricte, la final)
- **Riscul:** un corp sau o piele generată AI prezentată ca „rezultat” e reclamă înșelătoare.
- **Permis:** prezentarea produsului sau serviciului, **fără înainte/după și fără promisiuni**.

#### Saloane / beauty local: **pe pauză** (decizie, vezi jurnalul).

---

## 6. Oferta: modelul de bani (după `skills/money-model`)

**Regula celor 30 de zile:** profitul brut încasat de la un client în primele 30 de zile trebuie să acopere costul de a-l obține și de a-l servi. Ținta e să acopere costul pentru **2 clienți**.

| Etapa | Ce oferim | Când |
|---|---|---|
| **I. Atragere** | o ofertă de intrare care „ar fi o prostie să n-o încerci” | de la primul contact |
| **II. Upsell / downsell** | mai mult după un „da”, mai mic după un „nu” (fără să reducem prețul aceluiași lucru) | în aceeași discuție, la momentul nevoii |
| **III. Abonament** | conținut lunar, rapoarte, caracter dedicat | după primele rezultate (poate fi după ziua 30) |

**Ofertele de intrare propuse, pe nișă** (le alegem și le testăm pe rând):
- **N1, Decoy:** reclamă pentru „5 creative AI pentru reclamele tale, 99 €”. La discuție prezinți alături varianta completă: „ambasador AI + 12 creative + variante A/B + raport, 490 €”.
- **N1 / N2, Win Your Money Back:**
  > „Plătești pachetul. Dacă ne trimiți materialele în 48 h, rulezi creativele cel puțin 14 zile și ne dai cifrele, primești toată suma credit la abonamentul de 6 luni.”

  Bonus: datele pe care le primim alimentează ciclul de învățare.
- **N3 / N4, Pay Less Now or Pay More Later:** pentru sezon și evenimente.

**Pachetele lunare (prețuri de test, le ajustăm după primele 10 discuții):**

| Pachet | Ce include | Preț de test |
|---|---|---|
| Start | 8 poze + 4 reels + texte + calendar | 300–400 €/lună |
| Growth | 12 poze + 8 reels + variante pentru reclame (A/B) + raport lunar | 600–800 €/lună |
| Pro | Growth + caracter dedicat, exclusiv pe nișa lor + strategie | 1.200 €+/lună |

**Extra:** caracter exclusiv (setup unic), voce și lip-sync, versiuni în alte limbi, automatizare DM.

**Abonamentul (după `skills/abonament-retentie`):**
- bonus de intrare;
- facturare la 4 săptămâni;
- plată în avans: „plătești 5 luni, a 6-a e gratuită”;
- politică de anulare clară, scrisă în contract;
- interviu de ieșire când cineva vrea să plece.

**Exemplu de calcul pentru regula celor 30 de zile** (ipoteze, le înlocuim cu cifrele reale):
- Client Start: 350 €. Costul livrării: GPU + unelte ≈ 30 € + timpul tău.
- Costul de obținere: 5 mostre ≈ 15 € GPU + ~5 h de muncă.
- ⇒ Primul client plătitor acoperă costul de obținere pentru încă cel puțin 2 clienți. ✅

---

## 7. Vânzarea: pașii de urmat

1. **Lista:** 30 de firme pe nișă, notate în tabelul de vânzări (CRM).
2. **Mostra personalizată:** pe produsul sau locația lor.
3. **Mesajul scurt** (Anexa A) prin DM și email.
4. **Revenim** după 3 și după 7 zile (Anexa A).
5. **Apel de 15 minute**, după `skills/sales-call`:
   - 2 min despre ei;
   - 5 min despre problemă;
   - 5 min mostra;
   - 3 min propunerea.
6. **Pilot** → contract → abonament.

**Obiecțiile frecvente** (răspunsurile complete sunt în `skills/sales-call`):
- „E fals / e AI” → *„Exact. E ambasador AI declarat, legal și etichetat. Clienții voștri văd produsul real, pe o față constantă, fără ședință foto.”*
- „E scump” → schimbi **cum plătește** sau **ce primește**, niciodată prețul aceluiași lucru.
- „Mă mai gândesc” → întrebarea 1–10, apoi o probă cu condiții.

**Tabelul de vânzări (Google Sheets sau Notion), coloane:** firma, nișa, persoana de contact, canalul, data contactului, revenire 1, revenire 2, răspuns (da/nu), apel, ofertă, rezultat, motivul refuzului.

**Ce măsurăm la vânzare:** % răspunsuri, % apeluri, % piloți, % clienți, valoarea medie, timpul până la închidere.

---

## 8. Producția: linia de fabricație

| Pas | Ce | Cu ce |
|---|---|---|
| 1 | Brief: produs, public, ton, obiectiv, referințe | formular (Anexa B) |
| 2 | Idei, hook-uri, scripturi, texte | Claude + skill-urile de conținut |
| 3 | Imagini | Krea 2 + LoRA caracter + realism (Z-Image). Cu **poza produsului ca referință** (Nano Banana / GPT Image), pentru fidelitate |
| 4 | Video | din imagine (Wan 2.2 I2V / MiniMax H3), înlocuire (SCAIL-2), cloud (Seedance / Kling) doar când merită |
| 5 | Voce | ElevenLabs (vocea caracterului) → lip-sync (HeyGen / LatentSync) |
| 6 | Editare | acum manual (CapCut / DaVinci), mai târziu automat (Remotion / Shotstack): subtitrări, tăieturi, muzică licențiată, text pe ecran |
| 7 | Verificarea calității | Anexa C |
| 8 | Livrare + programarea postărilor | folderul clientului + calendar |
| 9 | Raport lunar | Anexa D |

**Timpi-țintă după rodaj** (ipoteze): o poză în 10–20 min, un reel în 45–90 min.
**Costul GPU:** pornești podul doar când lucrezi și îl oprești imediat după.

---

## 9. Promovarea organică (primele 90 de zile)

**Canale:**
- Instagram + TikTok, cu Daria;
- LinkedIn + X, cu tine, construind în public;
- YouTube Shorts, cu aceleași clipuri refolosite.

**Piloni de conținut:**
1. Lifestyle Daria: **60%**.
2. „Cum am făcut-o” / din culise: **15%**.
3. Studii de caz cu clienți, doar cu acordul lor: **15%**.
4. Educativ, AI pentru afaceri în română: **10%**.

**Frecvență:** Daria 4–5 postări pe săptămână + stories zilnic. Tu 3 postări pe săptămână.

**Unelte gratuite pe site** (aduc trafic din Google și clienți noi, ca la Higgsfield):
- image-to-prompt;
- generator de captions în română;
- „la ce oră să postezi”.

**Colaborări:** conturi din aceeași nișă, creatori mici.

**Reguli:** „AI creator” în bio, etichetă „AI info” la postări, #ad sau „Paid partnership” la colaborări plătite.

**Ce urmărim:** urmăritori, salvări, distribuiri, mesaje primite, lead-uri.

---

## 10. Platforma (produsul)

### 10.1 Fazele
- **F0 (acum):** unelte manuale + skill-uri + pod.
- **F1 (lunile 3–6): unealta internă.** Automatizează munca noastră pentru clienți.
- **F2 (lunile 6–12): beta pentru clienți.** Self-serve, pe credite.
- **F3 (12+ luni):** învățare pe date multe, API, marketplace de caractere, alte limbi.

### 10.2 Modulele

| Modul | F1 (intern) | F2 (clienți) | F3 |
|---|---|---|---|
| 1. Character Studio | fișe + bibliotecă de caractere | creare rapidă din referințe, cu **acord pentru fețe reale** | LoRA la cerere, marketplace |
| 2. Content Brain | idei, scripturi, texte (skill-urile) | același, pentru clienți | agenți automați pe calendar |
| 3. Image-to-Prompt | ✅ | ✅ unealtă gratuită pe site | — |
| 4. Generare | ComfyUI dintr-un click (GPU la cerere) | pe credite | rutare automată pe cel mai bun model |
| 5. Editare automată | șabloane de reels | șabloane pentru clienți | editare după performanță |
| 6. Publicare + ore | programare (după aprobarea Meta / TikTok) | ✅ | ore din datele fiecărui cont |
| 7. Analiză + învățare | tabelul de rezultate + raport | panou de rezultate pentru client | recomandări din date agregate și anonimizate |
| 8. Conformitate | etichete AI | + marcaj în fișier (C2PA), acorduri, filtre de conținut | audit automat |

### 10.3 Arhitectura

```
Client (web/telefon)
   └─ Aplicația (Next.js) ── Conturi + bază de date + fișiere (Supabase)
        ├─ Claude API: texte, imagini→prompt, skill-uri, agenți programați
        ├─ Coadă de lucrări → GPU la cerere (RunPod Serverless / ComfyDeploy) → workflow-urile noastre ComfyUI
        ├─ Video din cloud când merită (fal.ai: Seedance / Kling)
        ├─ Randare automată (Remotion / Shotstack)
        ├─ Publicare (Instagram Graph API / TikTok API)
        ├─ Rezultate → ciclul de învățare
        ├─ Plăți pe credite (Stripe) + statistici de utilizare (PostHog)
        └─ Conformitate: etichete, C2PA, acorduri, filtre (obligatorii prin licența Krea 2 dacă îl oferim ca serviciu)
```

**Modelele Claude se aleg după sarcină:** modelul mare pentru strategie, cel mediu pentru volum, cel mic pentru sarcinile simple și ieftine.

### 10.4 Datele de bază
Utilizator → Spațiu de lucru (firmă) → Caracter (fișă, LoRA, voce, acorduri) → Brief → Idee → Fișier (imagine/video) → Postare → Rezultate. Plus Acord (cine, ce, când, dovada) și Factură / Credit.

### 10.5 Etichetele fiecărei postări (motorul de învățare)
- **Etichete:** caracter, nișă, format, tipul de hook, durata, ora, ziua, CTA, muzică, text pe ecran, costul de producție.
- **Rezultate:** reach, durata medie de vizionare, salvări, distribuiri, comentarii, click-uri, vânzări sau lead-uri.

Cu ele aflăm ce tip de caracter, format și hook merge, pe ce nișă și la ce oră. Asta e avantajul pe care competitorii nu-l pot copia ușor.

### 10.6 Ordinea de construcție (F1)
1. Baza: conturi, spații de lucru, caractere, bibliotecă de fișiere.
2. Content Brain (cu skill-urile).
3. Image-to-prompt.
4. Generare de imagini dintr-un click (ComfyUI API).
5. Tabelul de rezultate + raportul automat.
6. Programarea postărilor (după aprobarea Meta).
7. Video + editare automată.

### 10.7 Cine face ce la construcție
- **Eu (Claude):** codul, structura, testele, documentația, în acest repo.
- **Tu:**
  - conturile pe numele tău: Vercel, Supabase, Stripe, Meta Developer, TikTok Developer, domeniul;
  - cheile API, puse în siguranță (niciodată în chat);
  - testezi și aprobi.
- **Recomandat:** un developer cu jumătate de normă care verifică securitatea și plățile înainte de primii clienți reali.

---

## 11. Legal și conformitate

*Nu e consultanță juridică. Verificăm cu un avocat și cu un contabil.*

- **Forma juridică:** PFA sau SRL, alegi cu un contabil.
- **Contract de servicii + anexă „conținut AI”:** etichetare, drepturi de folosire, revizii, politica de anulare.
- **GDPR:**
  - politică de confidențialitate;
  - acord explicit pentru datele colectate;
  - date anonimizate pentru învățare;
  - contracte de prelucrare a datelor (DPA) cu furnizorii.
- **AI Act, Art. 50** (se aplică din 2 august 2026):
  - conținutul sintetic sau deepfake se etichetează;
  - cine oferă un generator trebuie să pună un marcaj citibil de mașină;
  - în platformă: etichete automate + metadate C2PA.
- **Fețe reale:** doar cu acord scris și verificare.
- **Mărturii false:** interzise. Caracterul e ambasador AI declarat.
- **Reclame:** „Paid partnership” / #ad. Reguli speciale pentru alcool, sănătate și servicii financiare.

**Licențele modelelor (de confirmat pe pagina oficială a fiecăruia înainte de lansare):**

| Model | Comercial | Note |
|---|---|---|
| Krea 2 | ✅ sub 1 mil. $ pe an | dacă îl oferim altora ca serviciu, **filtrele de conținut sunt obligatorii**. Derivatele publicate trebuie să înceapă cu „Krea” |
| Wan 2.2 / Wan Animate | ✅ Apache 2.0 | o pagină a proiectului spune „pentru cercetare”, deci de confirmat |
| SCAIL-2 | ✅ probabil (MIT / Apache) | de confirmat. SAM3 are licența lui separată |
| Z-Image | ? | de verificat |
| FLUX.2 dev | ❌ non-comercial | doar pentru teste |
| FLUX.2 klein 4B | ✅ Apache 2.0 | |
| InsightFace (modele) | ❌ non-comercial | de înlocuit înainte de platformă |
| Ultralytics YOLO (detectoare) | ⚠️ AGPL | de verificat pentru platformă sau de înlocuit |
| ElevenLabs / HeyGen | după plan | verifici termenii comerciali ai planului ales |
| Muzică | doar licențiată | sau din biblioteca platformei sociale |

---

## 12. Finanțe (estimări de pornire, le actualizăm lunar)

| Cost lunar (F0–F1) | Estimare |
|---|---|
| Volumul RunPod de 250 GB | ~17,5 $ |
| GPU L40S (~30–60 h) | ~25–65 $ |
| ElevenLabs (plan de bază) | ~5–25 $ (verifică) |
| HeyGen | opțional |
| Claude | abonamentul tău existent |
| Domeniu + email | ~2–5 € |
| Supabase / Vercel | gratuit la început |
| **Total** | **~60–150 $/lună** |

- **Pragul de rentabilitate:** un singur client Start acoperă costurile.
- **Ținte (nu promisiuni):** luna 3 → 3 clienți. Luna 6 → 8–10 clienți.
- **Ordinea în care reinvestim:**
  1. automatizare și GPU;
  2. un developer cu jumătate de normă;
  3. creatori pentru promovare.

---

## 13. Roadmap: primele 12 săptămâni

| Săpt. | Tu | Eu |
|---|---|---|
| 1 | Setul v2 pentru Daria (Nano Banana). Conturile IG + TikTok, bio „AI creator”. 9 postări gata | Fișa detaliată N1, criteriile pentru firme, mesajele, planul celor 5 mostre |
| 2 | LoRA v2 Krea + test de realism. Lansarea Dariei (3–4 postări pe săptămână) | Concepte și scripturi pentru cele 5 mostre N1 |
| 3 | Faci cele 5 mostre N1 și lista de 30 de branduri | Oferta (pagină / PDF), ciorna de contract, tabelul de vânzări |
| 4 | Contactezi cele 30 de branduri și revii după 3 și 7 zile | Răspunsurile la obiecții, ajustez mesajele după răspunsuri |
| 5 | Apeluri + piloți N1 → **decizie go/no-go** | Raportul sprintului, actualizez jurnalul |
| 6–8 | Livrezi piloții N1. Sprintul N2 imobiliare (caracterul 2, dacă e nevoie) | Încep codul F1: baza + Content Brain |
| 9–11 | Sprintul N3 turism / HoReCa. LoRA video (Wan) | Image-to-prompt + generare dintr-un click |
| 12 | **Bilanț:** ce nișe merg, prețurile finale, decizia pentru F1 complet | Raport + planul pentru lunile 4–6 |

**Lunile 4–6:** livrare pe nișele câștigătoare, abonamente, unealta internă completă, sprintul N4.
**Lunile 6–12:** beta pentru clienți, caracterele 4–5, promovarea platformei, piața din afara României.

---

## 14. Ce măsurăm în fiecare săptămână

- **Afacere:** contacte, % răspunsuri, apeluri, piloți, clienți, venit lunar recurent, clienți pierduți.
- **Producție:** timp pe livrabil, cost GPU pe livrabil, revizii pe livrabil.
- **Daria:** urmăritori, reach, salvări, distribuiri, mesaje.
- **Tabelul de rezultate pe postare:** data, ora, caracterul, nișa, formatul, hook-ul, durata, CTA-ul, reach, vizionarea medie, salvări, distribuiri, comentarii, click-uri, costul.

---

## 15. Riscuri și planul B

| Risc | Ce facem |
|---|---|
| Nicio nișă nu răspunde | schimbăm întâi mesajul și oferta, apoi nișa |
| Clienții resping aspectul „de AI” | realism (LoRA v2, poze insta), clipuri scurte, editare atentă |
| Contul de Instagram e restricționat | etichetare corectă, fără conținut riscant, TikTok și YouTube ca rezervă |
| Se schimbă modelele sau prețurile | arhitectura permite schimbarea rapidă a furnizorului |
| Licențele | tabelul din §11 + alternative cu licență Apache pregătite |
| Costurile GPU | GPU doar la cerere, oprit când nu lucrăm, pachete cu limită de livrabile |
| Depindem de un singur client | minimum 3 clienți înainte să construim ceva pentru unul anume |
| Timpul tău | rutina de 1–2 ore pe zi. Eu pregătesc totul gata de folosit |

---

## 16. Cum lucrăm noi doi

- **La începutul unei sesiuni cu mine:**
  > „Citește plan/PLAN_COMPLET.md și plan/JURNAL.md, suntem la săptămâna X.”
- **La final:** actualizăm `plan/JURNAL.md` cu deciziile, rezultatele și pasul următor.
- **Pe pod:** agentul citește `/workspace/persist/DARIA_CONTEXT.md` (Anexa E).
- **Recenzia săptămânală** (duminica, 20 de minute): cifrele din §14 + ce schimbăm.

---

## 17. Întrebări deschise (le decizi tu)

1. ~~Numele~~ ✅ **MUSQAI**. Rămâne domeniul: musqai.com părea liber pe 20 octombrie 2026.
2. PFA sau SRL?
3. Bugetul lunar maxim pentru început?
4. Câte ore pe zi poți lucra la asta?
5. Confirmi ordinea nișelor: magazine online → imobiliare → turism → evenimente?
6. Care ofertă de intrare o testăm prima la N1: Decoy (99 €) sau Win Your Money Back?

---

## Anexe

### A. Mesajele de abordare (N1, magazine online)

**Primul mesaj (DM sau email):**
> Salut, [Nume]! Am văzut reclamele voastre pentru [produs], arată foarte bine. Lucrez cu un ambasador AI, Daria, și am făcut un exemplu cu [produsul vostru], ca să vedeți cum ar arăta o reclamă nouă fără ședință foto: [link]. E conținut AI declarat și etichetat corect. Dacă vă place, vă pot face câteva variante pentru test. Vă interesează?

**Revenirea 1 (ziua 3):**
> Revin scurt: ați apucat să vă uitați la exemplul cu [produs]? Pot să vă trimit și o variantă în format de reclamă (9:16), dacă vă ajută.

**Revenirea 2 (ziua 7):**
> Ultimul mesaj din partea mea: dacă reclamele noi nu sunt o prioritate acum, nicio problemă. Dacă vreți totuși să testați 5 creative noi pe produsele voastre, îmi scrieți aici.

### B. Brief-ul clientului (formular)
Produsul sau serviciul și pozele reale · publicul țintă · obiectivul (vânzări / lead-uri / notorietate) · tonul · ce NU vor · referințe care le plac · platformele · termene · persoana care aprobă.

### C. Verificarea calității înainte de livrare
- [ ] fața = caracterul (compar cu referința)
- [ ] mâini, degete, ochi, dinți corecți
- [ ] produsul identic: culoare, logo, formă, text
- [ ] fără text străin, logo-uri sau watermark
- [ ] fără nimic care să sugereze minori, nuditate, alcool sau promisiuni medicale nepermise
- [ ] eticheta AI pregătită și #ad dacă e colaborare plătită
- [ ] format corect (9:16 / 4:5), durata, subtitrări corecte în română
- [ ] muzică licențiată
- [ ] fișierul denumit corect și pus în folderul clientului

### D. Raportul lunar pentru client
1. Ce am livrat.
2. Rezultate: top 3 postări, cifrele principale, comparația cu luna trecută.
3. Ce am învățat (hook-uri, formate, ore).
4. Ce schimbăm luna viitoare.
5. Recomandarea pentru luna viitoare (upsell, doar dacă rezolvă o problemă reală).

### E. Mesajele pentru agentul de pe pod
- **La pornire:**
  > Read /workspace/persist/DARIA_CONTEXT.md, the pod restarted, continue.
- **La final:**
  > Before we stop: update /workspace/persist/DARIA_CONTEXT.md with what we did today, the file paths, and the next step.

---

## Sursele principale

- Higgsfield: [Soul ID](https://higgsfield.ai/blog/Soul-ID-AI-Character-Consistency) · [growth teardown](https://www.productgrowth.blog/p/higgsfield-growth-teardown) · [TechCrunch](https://techcrunch.com/2026/01/15/ai-video-startup-higgsfield-founded-by-ex-snap-exec-lands-1-3b-valuation/)
- Arcads: [Stripe case study](https://stripe.com/customers/arcads) · [Founderpath](https://founderpath.com/resources/romain-torres-arcads-10m-arr-ai-video-ads-sales)
- AI Act Art. 50: [ghid](https://artificialintelligenceact.eu/transparency-rules-article-50/) · [Codul de bune practici, Comisia Europeană](https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content)
- Licența Krea 2: [ghid pe clauze](https://krea2ai.com/blog/krea-2-license-commercial-use) · [rezumat](https://www.canirun.ai/license/krea-2-community)
- Instagram API: [limite 2026](https://www.keyapi.ai/blog/instagram-api-rate-limits-2026-what-changed-and-how-to-adapt/)
- ComfyUI ca API: [comparație de opțiuni](https://www.runflow.io/blog/comfyui-deploy-self-host-serverless-managed)
- Editare automată: [programmatic video tools 2026](https://rendercomp.com/blog/best-programmatic-video-tools-2026/)
- Orele de postare: [Buffer, 9,6 mil. postări](https://buffer.com/resources/when-is-the-best-time-to-post-on-instagram/)
