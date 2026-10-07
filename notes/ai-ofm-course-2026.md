# Notițe: „Full AI OFM Course SEPTEMBER 2026” – Dr. Hadi Talks

- Sursă: https://youtu.be/IMyJOdfTRuI (1:19:59, engleză)
- Metodă: notițele sunt făcute din transcrierea completă a videoclipului. Imaginea nu a putut fi descărcată (YouTube a blocat serverul), dar autorul citește aproape tot ce scrie pe tablă, deci conținutul e acoperit.
- Notițele sunt rezumat și parafrază în română, nu transcriere.

---

## 0. Despre ce e vorba

„AI OFM” = conducerea unui model virtual generat cu AI, monetizat pe o platformă de abonamente (autorul colaborează cu **Fanvue**). Traficul vine de pe rețele sociale, iar banii vin din abonamente, conținut plătit (PPV) și chat.

Fluxul complet:

```
Creezi modelul (imagine) → Produci conținut (poze + video)
  → Postezi pe Instagram (+ 1–2 platforme) → Landing page
  → Fanvue (abonament) → Chat (≈80% din venit)
  → Telegram = plasă de siguranță pentru audiență
```

## 1. Primele 12 minute (00:00–12:42): prezentare și reclamă

- Autorul spune deschis că video-ul promovează comunitatea lui plătită și colaborarea cu Fanvue.
- Comunitatea oferă: peste 30 de ore de cursuri (9,5 ore doar despre generare de conținut), 12 „camere” pe platforme de trafic, 3 apeluri de grup pe lună (generare, chat, trafic), un avocat și workflow-uri gata făcute.
- Ținta de la final: un model creat, cu **peste 30 de zile de conținut pregătit** înainte de lansare, un cont Fanvue funcțional, rețele sociale și un sistem de chat.
- Mesajul principal: tratează-l ca pe o afacere, cu sisteme, procese standard (SOP), delegare și automatizare, nu ca pe un hobby de jumătate de oră pe zi.

## 2. Uneltele (12:42)

| Scop | Unealtă | Note |
|---|---|---|
| Imaginea de bază (SFW) | **Nano Banana Pro**, rulat prin WaveSpeed sau Higgsfield | punctul de plecare pentru model |
| Rafinare | **Seedream 4.5** (desktop) | unghiuri ale feței, detalii, ținute |
| Curățare | eliminare metadate | scoate metadatele și watermark-ul, exportă la calitate maximă |
| Avansat | **ComfyUI workflows** (rulate local) | tot lanțul de generare într-un singur graf reutilizabil; fața nu mai „derivează”; generezi pe lot conținutul pe o zi sau o săptămână |
| Video (realism maxim) | **Seedance 2.5** | cel mai realist, dar cel mai scump per generare |
| Video (mai ieftin) | **Kling 3.0** | motion transfer, image-to-video; merge bine dacă editarea e bună |
| Editare | **CapCut Pro** / Edits (Instagram) | subtitrări, hook, retenție |
| Voce | **ElevenLabs** | o singură voce constantă pentru model |
| Prompturi | Claude | scrie prompturile de mișcare pentru video |

Ideea de bază: editarea și execuția decid dacă un reel prinde, nu modelul AI folosit.

## 3. Crearea modelului și fluxul de imagini (16:37)

**Pașii:**
1. Alegi **nișa și strategia de conținut ÎNAINTE** de față. Fața se potrivește strategiei, nu invers.
2. Strângi 2–3 referințe de față de calitate (de pe Pinterest): unghiuri bune, lumină bună, fără umbre puternice.
3. Generezi baza în Nano Banana Pro și fixezi fața, părul și tenul.
4. **Referința principală a feței**: 1–2 imagini, rezoluție mare, din față, bine luminate.

**Spectrul feței:** pentru primul model recomandă trăsături feminine accentuate (față rotundă, frunte mare, ochi și buze mari). Spune că funcționează în „9 din 10” nișe.

**3 greșeli frecvente:**
- **Perfecționismul**: generezi 20 de modele și nu lansezi niciodată. Construiești o investiție, nu „iubita ideală”.
- **Lipsa intenției**: model generic, fără nișă și fără strategie.
- **Nișa prea îngustă**: exemplul cu „angajata McDonald's” care poartă uniforma în fiecare poză. Caută calea de mijloc.

**Fluxul zilnic de imagini:** bază în Nano Banana Pro (cu referința feței) → rafinare în Seedream 4.5 → eliminare metadate → descărcare la calitate maximă → arhivare în Drive, etichetată după folosință (carusel, reel, poză de profil, story).

## 4. Producția video (22:31)

- **Seedance 2.5**: iei un video de referință ca format și îl refaci cu modelul tău, cu aceeași față, lip-sync, același ritm și aceeași expresie. 8–15 secunde, video care se poate rula în buclă. Finisare în CapCut.
- **Kling 3.0**:
  - *Motion transfer*: primul cadru cu fața modelului tău plus mișcarea din referință. Explică faptul că video-urile virale de tip „bărbat transformat în femeie” sunt făcute exact așa.
  - *Image-to-video*: animezi o imagine bună (mișcare naturală a capului, a corpului, camera care se leagănă ușor). Promptul contează mult.
- **ComfyUI SFW**: tot ce ajunge pe rețele iese dintr-un singur graf. Format 9:16 nativ, niciodată tăiat; referința personajului e fixată, așa că pozele și video-urile arată același model; generezi pe lot reel-urile pentru o săptămână.
- **ComfyUI NSFW**: rulat local, doar pentru platforma plătită. **Regula de fier: nimic de aici nu ajunge pe rețelele sociale** (e cel mai rapid mod de a lua ban).

**Ce merge acum (septembrie 2026):** reel-uri cu personalitate și vorbit direct în cameră, selfie din mașină, păreri, reel-uri în stradă filmate „la persoana a treia”, format de interviu pe stradă, nișa îngrijitoare sau asistentă.
**Ce nu mai merge:** „schimbarea ținutei” cu retenție falsă, reel-uri doar cu tranziții între imagini (formatul a murit de vreo 6 luni).
Tendințele se schimbă lunar sau chiar mai des.

**De ce devine un video viral:** cârlig (primele 3 secunde) → retenție → recompensă la final. Scopul e ca oamenii să-l vadă cel puțin o dată până la capăt, ideal de două ori. Structura funcționează pe toate platformele.

## 5. Marketing pe Instagram (30:48)

- Instagram = **sursa principală** de trafic: vizualizări gratuite prin conținut viral, apoi CTA către Fanvue.
- **„2 funnel-uri, nu 7”**: Instagram plus 1–2 platforme sunt suficiente. Scalezi prin **mai multe conturi**, nu prin mai multe platforme.
- **Cota per cont:** 3 reel-uri pe zi, 2 caruseluri pe săptămână, 2 story-uri pe zi, 2 story-uri cu CTA pe săptămână.
- **Structura conturilor:** minimum 2 conturi, fiecare pe **o nișă complet diferită**. Testezi minimum o lună, citești datele, apoi pui accent pe ce convertește. Al doilea cont e și protecție: dacă primul ia ban, nu pierzi tot.
- **Nu recomandă boost plătit** la început.
- **Cercetarea pentru reel-uri:** un cont separat de inspirație, folosit doar pentru research, care urmărește modelele de top. Algoritmul începe să-ți arate formatele care merg. Le copiezi **formatul**, nu conținutul cuvânt cu cuvânt. 42 de reel-uri pe săptămână nu le poți inventa de la zero.
- **Carusel în 5 slide-uri:** imagine-cârlig → altă poză → cadru mai apropiat → poză care arată personalitatea → imagine finală puternică. Contează câte slide-uri sunt parcurse.
- **Story-uri:** 2 pe zi; ține o arhivă de ~30 de story-uri pe lună ca să nu improvizezi zilnic; link către landing page de 2 ori pe săptămână, discret.
- **Identitate vizuală:** aceeași paletă de culori, aceeași lumină, aceleași unghiuri, 3–5 locații recurente. Grid-ul trebuie să arate ca o singură „lume”. Exemple: outdoor (plajă, câine, natură), goth (tonuri închise), sală (oglindă, neon).

## 6. Alte platforme (43:15)

**Facebook:** cont separat, fără cross-post din Instagram. Refolosești conținutul de pe Instagram exact cum e. Ajungi la 500 de prieteni, activezi modul creator și pui landing page-ul în bio. 5–10 cereri de prietenie pe zi, grupuri mici de nișă, albume care fac profilul să pară real. **Niciodată link direct spre Fanvue.**

**Snapchat:** profil public, Bitmoji asemănător modelului, handle-ul de Instagram în bio (pe Snapchat nu se pot pune linkuri). 3–5 Quick Adds pe zi, din demografia țintă. 2–3 story-uri pe zi, Spotlight cu reel-urile de pe Instagram. Link de Telegram **o dată pe săptămână** (dacă îl pui mai des, scad vizualizările). Pentru începători, singurul rol al Snapchat e să umple canalul de Telegram.

**Telegram:** canal de tip broadcast (doar tu postezi). 2 postări pe zi, cu conținut cu un nivel mai „picant” decât pe Instagram, dar fără nuditate. Un mesaj fixat sus, cu imagine-teaser, link Fanvue și CTA. Rolul principal: **plasă de siguranță**. Un canal de 3.000 de membri reconstruiește un cont de Instagram banat în câteva zile. E și a doua cale de conversie pentru cei care nu se abonează direct de pe Instagram.

**TikTok:** volum și viralitate. Image-to-video în buclă **plus sunet în trend** (pe TikTok sunetul contează, pe Instagram nu). Merge bine adaptat specific pentru TikTok, nu doar repostat. Unii membri fac 10–15K pe lună doar din TikTok.

**Regula refolosirii:** același conținut poate merge pe platforme diferite, dar **niciodată pe două conturi de pe aceeași platformă**.

## 7. Landing page (53:44)

- Poză de profil SFW, bio scurt, un singur CTA. **Ordinea: Fanvue primul, Telegram al doilea.** Nu pui alte linkuri care împrăștie atenția.
- Cât mai SFW, ca Instagram să nu aibă motiv să dea ban.
- **Un landing page per cont social** și **un tracking link Fanvue per landing page**, ca să poți măsura fiecare sursă.
- Platforma recomandată: Get All My Links (Link.me a fost semnalat de Instagram, iar dezvoltatorii LinkBB nu mai răspund).
- Rolul landing page-ului: un pas intermediar sigur, ca să nu pui niciodată linkul Fanvue direct pe rețea.

## 8. Chat (57:09)

- Autorul recomandă să înveți întâi singur **psihologia** chatului, chiar dacă angajezi apoi o agenție. Altfel nu știi dacă agenția face 10K dintr-un potențial de 100K.
- **Chatul bun ≈ 80% din venitul lunar.** Chatul prost pierde bani din același trafic.
- **Scara conținutului:** începi casual, construiești curiozitate, apoi treci la conținut premium, pachete și „girlfriend experience” recurent.
- **Segmentarea abonaților:**
  - 🐋 **Whale**: cheltuie mult și vrea exclusivitate. E prioritatea absolută.
  - ❤️ **Pe conexiune**: pune conversația mai presus de conținut. Uneori e whale, alteori e doar „freeloader”.
  - 💲 **Tranzacțional**: vrea totul rapid; direct și eficient.
  - ⏰ **Puțin interes**: pierde timp și e sensibil la preț; nu investești mult în el.
  - Eticheta cu emoji se pune imediat ce intră abonatul.
- **Date:** mesaj automat de bun venit. Note despre fiecare fan: job, hobby-uri, locație, relație, preferințe, **fusul orar** (sus în profil).

## 9. Sistemul de operare (01:06:06)

**Zilnic (per cont de Instagram):** 3 reel-uri și 2 story-uri. Snapchat: 3 story-uri și un Spotlight. Telegram: 2 postări.
**Săptămânal:** 2 caruseluri, 2 story-uri cu CTA, re-fixarea postării de pe Telegram, link de Telegram pe Snapchat o dată, analiza datelor din Fanvue, **o zi de generare a conținutului pe toată săptămâna** (organizat în Drive, programat în Meta Business Suite), verificarea calității conversațiilor din chat.

**Când lansezi linkul de Fanvue:**
- ❌ NU: câteva sute de urmăritori, cont mai nou de 2–3 săptămâni, nimic viral, niciun mesaj primit. Ai doar risc de ban, fără câștig.
- ✅ DA: conținut care devine viral, creștere constantă, interes real. Atunci faci **o zi mare de lansare** anunțată din timp. Exemplul autorului: 4 săptămâni, 10K urmăritori, interes real, deci o zi de 5 cifre.

**Tracking:** câte un landing page per cont (IG1, IG2, Telegram…). Măsori clic → abonat → bani cheltuiți pe fiecare nișă, apoi pui accent pe ce merge.

**Promoții Fanvue:** pentru început, **abonament gratuit** pentru o perioadă și un număr limitat de locuri, cu numărătoare inversă. Reduce bariera la intrare și dă echipei de chat mai mult trafic.

**Lunar:** optimizezi nișa pe baza datelor, nu după impresii. Înlocuiești conturile slabe, ajustezi funnel-urile, testezi prețuri.

## 10. Scalare și automatizare (01:11:54)

- **Mai multe modele ≠ mai mulți bani.** Lansezi modelul 2 doar când primul e profitabil, ai SOP-uri, ai lichidități, ai asistenți virtuali (VA) și automatizări, ai atins un plafon real sau ai o nișă opusă.
- Pârghii de scalare: SOP-uri documentate (de exemplu pe Miro) după care poate lucra un asistent virtual. Delegi în ordinea: chat → generare → rețele sociale. Ai zile dedicate generării. Scalezi conturile, nu platformele („5 conturi de Instagram bat 7 funnel-uri”). Traficul plătit vine abia după luni de date.
- **Automatizarea conținutului cu Claude:** o persona per cont. Generezi imaginea → Claude scrie scriptul după persona și durată → generezi video-ul în Seedance → îl asamblezi.
- Proporția recomandată: o agenție matură e cam 70% manual și 30% automat. Pornești cu 10% automatizare și crești treptat (20%, apoi 40%) doar dacă performanța se menține.
- **Capcana automatizării:** pierzi luni construind un CRM în loc să lucrezi. Automatizezi întâi **crearea conținutului**, acolo se duce timpul.
- **Fanvue MCP:** răspunsuri automate și ciorne de răspuns, citirea mesajelor necitite, programarea postărilor, informații despre abonați și KPI, organizarea arhivei media, mesaje în masă, mod agenție (mai multe modele).

## 11. Final

- Doar cu ce e în video și cu încercări repetate spune că se poate ajunge la ~10K pe lună. Afirmațiile despre membri cu 6–7 cifre pe lună sunt ale autorului, neverificate.

---

## ⚠️ Atenție înainte să construim planul

Câteva lucruri din video sunt riscante juridic sau încalcă regulile platformelor. Nu le includem în planul nostru:

1. **Ascunderea faptului că modelul e AI.** Video-ul insistă ca fanii să creadă că e o persoană reală: șterge metadatele, amestecă poze reale, ascunde fusul orar. Fanvue cere marcarea conținutului AI, iar Meta și TikTok cer etichete pentru conținutul realist generat cu AI. Să încasezi bani de la oameni convinși că vorbesc cu o femeie reală e înșelătorie, cu risc de ban și de plângeri sau chargeback-uri.
2. **Poze și story-uri luate de la alți creatori reali.** Video-ul recomandă să le descarci și să le amesteci cu cele AI. Asta încalcă drepturile de autor și dreptul la imagine.
3. **Metodele „gray hat” și „black hat”** (spam, ferme de telefoane, ocolirea banurilor) încalcă termenii platformelor.
4. **Copierea fețelor unor persoane reale** pentru model. Nu se face.

Ce rămâne perfect utilizabil: uneltele, fluxul de producție, consecvența vizuală, structura viral (cârlig, retenție, recompensă), funnel-ul, landing page-ul, tracking-ul, segmentarea fanilor, sistemul de operare, SOP-urile și automatizarea. Toate merg la fel de bine pentru un **creator AI declarat ca AI**. Pe Fanvue există o categorie întreagă pentru așa ceva.
