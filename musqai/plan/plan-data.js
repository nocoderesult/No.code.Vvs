/* Planul MUSQAI: 12 săptămâni, zi cu zi.
   Un bloc = [prioritate, minute, categorie, titlu, [pașii], „gata când”].
   Prioritatea: 1 = drumul critic (modul de 2 ore), 2 = important (modul de 4 ore), 3 = accelerează (modul de 8 ore).
   Rutina zilnică (planul zilei, închiderea, postarea de la 19:00, recenzia de duminică) o adaugă pagina singură.
   Dacă schimbi ordinea blocurilor dintr-o zi, bifele deja puse pe ziua respectivă se pot muta. */
window.PLAN = {
  startDefault: "2026-10-26",
  postTime: "19:00",

  cats: {
    prod: "Producție",
    cont: "Conținut",
    vanz: "Vânzări",
    tech: "Pod și tehnic",
    inv: "Învățare",
    admin: "Admin și plan",
    eu: "Cu Claude"
  },

  principles: [
    ["Blocuri de timp", "Cal Newport, „Deep Work”", "Fiecare oră are o sarcină. Munca grea vine dimineața, în blocuri de 60–90 de minute, cu telefonul pe silențios."],
    ["Program de creator", "Paul Graham, „Maker's Schedule, Manager's Schedule”", "Producția are nevoie de blocuri lungi, fără întreruperi. Mesajele și apelurile le grupezi după-amiaza."],
    ["Regula celor 100", "Alex Hormozi, „$100M Leads”", "O acțiune principală în fiecare zi, fără excepție. La noi: aproximativ 100 de minute pe ce aduce clienți, adică producție sau vânzare."],
    ["Conținut în loturi", "practica marilor creatori", "Creezi conținutul unei săptămâni într-o zi, îl programezi, apoi doar răspunzi live."],
    ["Fereastra de după postare", "practica marilor creatori", "În primele 15–30 de minute după postare răspunzi la comentarii și mesaje. Atunci se decide cât de departe ajunge postarea."],
    ["Ritualul de închidere", "Cal Newport", "La final de zi bifezi, notezi cifrele și scrii primul pas de mâine. Apoi te oprești de tot."],
    ["Recenzia săptămânală", "David Allen, „Getting Things Done”", "Duminica, 30 de minute: cifrele, ce a mers, ce nu, o singură schimbare pentru săptămâna următoare."],
    ["Plan detaliat aproape, larg departe", "planificarea în valuri", "Primele săptămâni sunt planificate pe oră. Cele de după se rafinează în fiecare duminică, după cifre."]
  ],

  themes: [
    ["Luni", "Producție", "Lotul de imagini al săptămânii, pe pod. Sesiunea cu Claude."],
    ["Marți", "Video și editare", "Reels, voce, montaj, programare."],
    ["Miercuri", "Vânzări", "Liste, mesaje, apeluri."],
    ["Joi", "Clienți și mostre", "Livrabile pentru clienți și mostre noi."],
    ["Vineri", "Vânzări și public", "Reveniri, build in public, ce a rămas."],
    ["Sâmbătă", "Jumătate de zi", "Recuperezi și programezi săptămâna următoare."],
    ["Duminică", "Recenzie și odihnă", "30 de minute de recenzie. În rest, liber."]
  ],

  week0: [
    ["Cumperi domeniul musqai.com", "Pe 20 octombrie 2026 părea liber. Verifici și musqai.ro."],
    ["Rezervi numele @musqai", "Instagram, TikTok, YouTube, LinkedIn, X. Chiar dacă nu postezi încă."],
    ["Alegi numele contului lui Iness", "Ex.: @iness.musqai. Verifici să fie liber pe Instagram și TikTok."],
    ["Răspunzi la cele 6 întrebări din plan (§17)", "PFA sau SRL, bugetul, orele pe zi, ordinea nișelor, prima ofertă."],
    ["Mărești volumul RunPod la ~350 GB", "Ca să încapă SCAIL-2 lângă MiniMax și Qwen."],
    ["Instalezi Meta Business Suite pe telefon", "Aici programezi postările și vezi statisticile."],
    ["Alegi modul de lucru și ora de start", "Sus, în pagină: 2, 4 sau 8 ore pe zi."]
  ],

  weeks: [
    /* ---------------- Săptămâna 1 ---------------- */
    {
      title: "Setul v2 și conturile",
      goal: "34 de poze v2 aprobate, conturile lui Iness create și etichetate AI, 9 postări de lansare pregătite, LoRA v2 pornit.",
      kpi: ["34 / 34 poze aprobate", "Instagram, TikTok și pagina FB create", "9 postări pregătite ca ciorne"],
      live: false,
      post: [],
      eu: ["Fișa detaliată pentru nișa 1 (magazine online)", "Criteriile pentru firmele-țintă și unde le găsești", "Mesajele de abordare, în 3 variante", "Planul celor 5 mostre", "Textele celor 9 postări de lansare"],
      days: [
        { theme: "Producție: setul v2", blocks: [
          [1, 30, "prod", "Referințele curate, fără tatuaj", ["Nano Banana: urci daria_ref.png și scrii „Remove the tattoo from her wrist. Keep everything else exactly identical.”", "Salvezi ref_fata.png. Repeți cu front_00002_.png și salvezi ref_corp.png."], "Ai ref_fata.png și ref_corp.png, fără tatuaj."],
          [1, 55, "prod", "Setul v2: pozele 01–06 (fața)", ["Deschizi personaj/04_dataset_v2.md.", "Prompt = ÎNCEPUT + rândul din tabel + SFÂRȘIT. Urci ref_fata.png.", "Salvezi cu numele exact: daria_v2_01.png și așa mai departe."], "6 poze care trec checklist-ul din fișă."],
          [2, 45, "eu", "Sesiune cu Claude: pornim săptămâna 1", ["Îmi scrii: „Citește plan/PLAN_COMPLET.md și plan/JURNAL.md, suntem la săptămâna 1.”", "Îmi ceri fișa N1, mesajele și textele celor 9 postări."], "Ai livrabilele mele pentru săptămâna 1."],
          [2, 60, "cont", "Contul de Instagram al lui Iness", ["Creezi contul (ex. @iness.musqai) și îl treci pe Profesional, apoi Creator.", "Bio: „AI creator ✨” și o propoziție despre ea.", "Poza de profil: cea mai bună față de până acum."], "Cont Creator, cu „AI creator” în bio."],
          [3, 45, "cont", "TikTok și pagina de Facebook a lui Iness", ["TikTok: cont, bio cu „AI creator”.", "Facebook: o pagină „Iness”, legată de contul de Instagram. O cere API-ul mai târziu."], "TikTok gata, pagina FB legată de Instagram."],
          [3, 60, "inv", "Studiu: cum postează creatorii AI de top", ["Alegi 3 conturi mari de influenceri AI (ex. Aitana López).", "Notezi cât de des postează, ce formate, ce hook-uri, cum spun că sunt AI."], "5 lucruri de preluat, notate."],
          [3, 60, "tech", "Pod: verifici SCAIL-2", ["Pornești podul și agentul (vezi Rutinele).", "Îi ceri să verifice cele 7 fișiere SCAIL-2 și să descarce ce lipsește, dacă ai spațiu.", "Oprești podul la final."], "SCAIL-2 e complet sau știi exact ce lipsește."]
        ]},
        { theme: "Producție: setul v2", blocks: [
          [1, 85, "prod", "Setul v2: pozele 07–14", ["07–12: urci ref_fata.png. 13–14: urci ref_fata.png și ref_corp.png.", "Chat nou după fiecare 5 poze.", "Verifici mâinile: 5 degete, unghii nude-roz, fără tatuaj."], "14 poze aprobate."],
          [2, 60, "cont", "Cele 9 postări de lansare: pozele", ["Alegi 9 poze (v1 și v2): 3 cu fața, 3 cu ținute, 3 „din viață”.", "Le aranjezi în ordinea grilei, într-o aplicație de previzualizare."], "9 poze, în ordinea grilei."],
          [2, 60, "cont", "Textele celor 9 postări", ["Pornești de la textele mele.", "Le scurtezi pe vocea lui Iness: calde, cu o întrebare la final.", "3–5 hashtag-uri pe postare."], "9 texte gata."],
          [3, 90, "prod", "Reel-ul de lansare", ["3 clipuri de 3–5 s din pozele de lansare (Wan 2.2 I2V pe pod sau alt generator).", "Montaj de 8–12 s în CapCut, cu textul „Bună, sunt Iness. Și da, sunt AI.”"], "Reel-ul de lansare e gata."],
          [3, 60, "inv", "Regulile Meta și TikTok pentru conținut AI", ["Citești cum funcționează eticheta „AI info” pe Instagram.", "Citești regulile TikTok pentru conținutul generat cu AI.", "Notezi ce bifezi la fiecare postare."], "Știi exact cum etichetezi."]
        ]},
        { theme: "Producție: setul v2", blocks: [
          [1, 85, "prod", "Setul v2: pozele 15–22 (studio)", ["Urci ref_fata.png și ref_corp.png la fiecare chat nou.", "Verifici proporțiile corpului și lipsa tatuajelor."], "22 de poze aprobate."],
          [2, 45, "cont", "Stories de lansare", ["3 stories: „Cine e Iness”, „Cum e făcută”, „Ce urmează”.", "Coperți pentru highlights."], "3 stories gata."],
          [2, 60, "admin", "Conturile MUSQAI", ["Instagram, TikTok și LinkedIn pentru @musqai.", "Bio: „Ambasadori AI pentru branduri. Conținut gata de postat.”"], "@musqai e rezervat și completat."],
          [3, 120, "tech", "Test SCAIL-2 cu filmarea ta", ["Filmezi 10 s cu tine: lumină bună, mișcări lente, nimic în fața feței.", "Îi ceri agentului înlocuirea cu Iness. Referința: cea mai bună poză a ei.", "Compari fața, mâinile și fundalul, apoi notezi."], "Primul test de înlocuire, notat în jurnal."],
          [3, 60, "inv", "Studiu: 10 reclame de modă din România", ["Biblioteca de reclame Meta, țara România: „rochii”, „bijuterii”, „genți”.", "Salvezi 10 reclame care rulează de peste 30 de zile.", "Notezi formatul, hook-ul și durata."], "10 exemple salvate pentru mostre."]
        ]},
        { theme: "Producție: setul v2", blocks: [
          [1, 85, "prod", "Setul v2: pozele 23–28 (insta)", ["Aspect de telefon: lumină reală, fundal aglomerat.", "Dacă arată „prea perfect”, o refaci."], "28 de poze aprobate."],
          [2, 75, "cont", "Lansarea, pregătită ca ciorne", ["Meta Business Suite: încarci cele 9 postări și reel-ul ca ciorne.", "Eticheta AI bifată la fiecare.", "Lansarea e luni, în săptămâna 2."], "Toate postările de lansare sunt ciorne etichetate."],
          [2, 30, "vanz", "Tabelul de vânzări", ["Google Sheets cu coloanele din plan (§7).", "O filă pentru fiecare nișă."], "Tabelul e gata de completat."],
          [3, 120, "prod", "6 scene noi cu LoRA v1", ["Pod: workflow-ul de realism, scene din personaj/03_scene_lux.txt.", "Păstrezi doar ce trece checklist-ul."], "6 imagini noi pentru săptămâna 2."],
          [3, 60, "inv", "Editare de reels în CapCut", ["Tăieturi pe ritm, text pe ecran, subtitrări automate în română.", "Exersezi pe reel-ul de lansare."], "Un reel de 10 s îți ia 20 de minute."]
        ]},
        { theme: "Producție și verificare", blocks: [
          [1, 85, "prod", "Setul v2: pozele 29–34 (insta)", ["Aceleași reguli: lumină reală, fundal aglomerat, fără tatuaj.", "Salvezi cu numele exacte."], "Toate cele 34 de poze sunt făcute."],
          [2, 60, "prod", "Verificarea finală a setului", ["Le pui una lângă alta și le compari.", "Scoți orice poză cu fața diferită, tatuaj, mâini greșite sau text.", "Mai bine 28 perfecte decât 34 cu greșeli."], "Setul final, fără nicio poză îndoielnică."],
          [2, 45, "cont", "Primul post „build in public”", ["LinkedIn sau X: „Construiesc MUSQAI, un studio de ambasadori AI. Săptămâna 1: Iness.”", "O captură din culise, nu doar rezultatul."], "Primul post public despre MUSQAI."],
          [3, 90, "tech", "Setul și captions-urile pe pod", ["Urci pozele în /workspace/datasets/daria_v2/.", "Agentul scrie captions-urile din personaj/04_captions_v2.txt lângă fiecare poză.", "Verifici că niciun caption nu conține „tattoo”."], "Setul e pe pod, gata de antrenare."],
          [3, 45, "eu", "Calendarul de conținut pe 2 săptămâni", ["Îmi ceri calendarul (skill-ul content-calendar).", "4 postări în săptămâna 2, 5 în săptămâna 3, stories zilnic."], "Calendarul e aprobat."]
        ]},
        { theme: "Antrenare și recuperare", blocks: [
          [1, 85, "tech", "Pornești antrenarea LoRA v2", ["Pod și agent: „Read /workspace/persist/DARIA_CONTEXT.md, the pod restarted, continue.”", "Krea 2 Raw, trigger d4ria, rank 32, lr 1e-4, 3.000 de pași, checkpoint la fiecare 250.", "Verifici primele imagini de test, apoi o lași să ruleze (~3 ore)."], "Antrenarea rulează."],
          [2, 60, "admin", "Recuperezi ce a rămas", ["Te uiți la blocurile nebifate ale săptămânii.", "Termini ce ține de lansare: conturi, ciorne, texte."], "Nimic critic nu trece în săptămâna 2."],
          [2, 20, "tech", "Oprești podul după antrenare", ["Checkpoint-urile rămân în /workspace.", "Agentul actualizează DARIA_CONTEXT.md, apoi oprești podul."], "Podul e oprit."]
        ]},
        { theme: "Recenzie și odihnă", blocks: [] }
      ]
    },

    /* ---------------- Săptămâna 2 ---------------- */
    {
      title: "LoRA v2 și lansarea lui Iness",
      goal: "Checkpoint-ul LoRA v2 ales, Iness live cu 4 postări, vocea „Iness” salvată, primele cifre notate.",
      kpi: ["Iness e live", "4 postări + stories zilnic", "Vocea salvată", "Lista N1: 30 de firme"],
      live: true,
      post: [1, 3, 5, 6],
      postTitles: { 1: "Lansarea: reel-ul de la 19:00" },
      eu: ["Conceptele și scripturile pentru cele 5 mostre N1", "Prompturile pentru mostre (produsul pe Iness)", "Textele postărilor din săptămâna 3", "Răspunsuri-tip la comentarii („ești reală?”)"],
      days: [
        { theme: "Lansare", blocks: [
          [1, 40, "prod", "Alegi checkpoint-ul LoRA v2", ["Același prompt cu checkpoint-urile 1500, 2000, 2500 și 3000.", "Alegi după: fața seamănă, pielea nu e de plastic, mâinile sunt bune."], "Un singur checkpoint ales și notat."],
          [1, 45, "cont", "Lansarea: primele 3 postări din grilă", ["Dimineața publici 3 postări din grilă, la 30 de minute una de alta.", "Eticheta AI la fiecare.", "Reel-ul de lansare iese la 19:00."], "Profilul are 3 postări."],
          [2, 60, "prod", "Testul de realism cu LoRA v2", ["Krea 2 Turbo + LoRA v2, apoi Z-Image 0.25, FaceDetailer 0.20 și grain.", "10 scene de telefon (flash, fundal aglomerat). Compari cu v1."], "10 imagini mai realiste decât v1."],
          [2, 45, "eu", "Sesiune cu Claude: săptămâna 2", ["Îmi trimiți checkpoint-ul ales și 3 imagini de test.", "Îmi ceri conceptele celor 5 mostre N1."], "Ai conceptele mostrelor."],
          [3, 60, "cont", "Comunitatea în ziua lansării", ["Urmărești 30 de conturi din modă și lifestyle din România.", "Lași comentarii utile, nu spam."], "30 de conturi urmărite, 15 comentarii lăsate."],
          [3, 90, "prod", "Vocea lui Iness", ["ElevenLabs Voice Design, cu descrierea: „Young Romanian woman, mid-20s, warm and slightly low voice, calm confident pace, friendly smile in the voice, clear diction, studio-quality recording.”", "3 variante, alegi una și o salvezi ca „Iness”.", "Test: un text de 15 s în română."], "Vocea „Iness” e salvată."]
        ]},
        { theme: "Video și editare", blocks: [
          [1, 85, "prod", "Imaginile săptămânii, în lot", ["Pod: 12 imagini cu LoRA v2 pentru postările din săptămânile 2 și 3.", "Scenele din calendarul aprobat."], "12 imagini aprobate în folderul „postări”."],
          [2, 60, "cont", "Textele și programarea", ["Textele pentru miercuri, vineri și sâmbătă.", "Le programezi la 19:00, cu eticheta AI."], "Postările săptămânii sunt programate."],
          [2, 60, "prod", "Primul reel vorbit", ["Un text de 10–15 s: cine e Iness și de ce e AI.", "Vocea „Iness” și sincronizarea buzelor (HeyGen sau LatentSync)."], "Un reel vorbit, gata de programat."],
          [3, 120, "tech", "LoRA video (Wan): ce ne trebuie", ["Setul v2 și 6–10 clipuri scurte cu Iness (din I2V).", "Îi ceri agentului ce lipsește pentru Wan 2.1 14B LoRA și cât spațiu ocupă."], "Lista cu ce lipsește pentru LoRA video."],
          [3, 45, "inv", "Primele 24 de ore, în cifre", ["Insights: reach, vizite pe profil, urmăritori noi.", "Le notezi în tabelul de rezultate."], "Primele cifre sunt notate."]
        ]},
        { theme: "Pregătirea vânzărilor", blocks: [
          [1, 85, "vanz", "Alegi cele 5 branduri pentru mostre", ["Din reclamele salvate în săptămâna 1, alegi 5 branduri românești care rulează reclame acum.", "Salvezi pozele produselor de pe site-ul lor.", "Le notezi în tabel: brand, produs, link."], "5 branduri, fiecare cu 1–2 produse alese."],
          [2, 60, "vanz", "Lista N1: firmele 1–10", ["Criteriile din fișa N1.", "Biblioteca de reclame Meta și Instagram: branduri care rulează reclame.", "Le notezi în tabelul de vânzări."], "10 firme în tabel."],
          [2, 45, "cont", "Răspunsuri-tip la comentarii", ["„Ești reală?”, „Cine te-a făcut?”, „De unde e rochia?”.", "Le salvezi ca răspunsuri rapide în Instagram."], "5 răspunsuri rapide salvate."],
          [3, 120, "prod", "Al doilea reel, din imagini", ["I2V din 3 imagini noi, montaj de 8–12 s.", "Text pe ecran cu un hook din fișa lui Iness."], "Reel gata pentru săptămâna 3."],
          [3, 60, "inv", "Studiu: reclamele cu actori AI", ["Te uiți la exemplele publice ale unor studiouri ca Arcads.", "Notezi hook-ul, durata, formatul 9:16 și îndemnul."], "3 idei pentru mostrele noastre."]
        ]},
        { theme: "Video și liste", blocks: [
          [1, 85, "prod", "Reels din imagini, în lot", ["4 clipuri I2V de 3–5 s, pe pod.", "Le montezi în 2 reels."], "2 reels gata."],
          [2, 60, "cont", "Carusel: „Cine e Iness”", ["5 slide-uri: cine e, ce face, de ce e AI, ce urmează, o întrebare.", "Textul îl scrii cu skill-ul carousel-builder."], "Caruselul e programat."],
          [2, 60, "vanz", "Lista N1: firmele 11–20", ["Aceleași criterii.", "Pentru fiecare: persoana de contact și canalul (DM sau email)."], "20 de firme în tabel."],
          [3, 120, "tech", "SCAIL-2, al doilea test", ["Altă filmare: mai multă mișcare, alt unghi.", "Notezi ce merge și ce nu: fața, mâinile, mișcarea."], "Știi când SCAIL-2 e destul de bun pentru clienți."],
          [3, 60, "inv", "Creatorii AI de top, partea a doua", ["Ce postează în weekend, cum răspund la comentarii.", "Ce colaborări fac și cum le marchează."], "3 lucruri noi de preluat."]
        ]},
        { theme: "Cifre și public", blocks: [
          [1, 85, "cont", "Analiza primei săptămâni", ["Ce postare a avut cel mai mare reach și ce postare cele mai multe salvări.", "Ce întrebări se repetă în comentarii.", "Notezi 3 concluzii."], "3 concluzii în jurnal."],
          [2, 60, "vanz", "Lista N1: firmele 21–30", ["Completezi lista până la 30.", "Marchezi cu „mostră” cele 5 branduri alese miercuri."], "30 de firme în tabel."],
          [2, 45, "cont", "Build in public: săptămâna 2", ["Post pe LinkedIn: lansarea lui Iness și primele cifre.", "O imagine din culise."], "Postat."],
          [3, 120, "prod", "Imaginile pentru săptămâna 3", ["8 imagini noi, după calendar.", "Variante de telefon, pentru realism."], "8 imagini gata."],
          [3, 60, "admin", "Facturarea și forma juridică", ["Vorbești cu un contabil: PFA sau SRL, facturare în euro, TVA.", "Notezi decizia în jurnal."], "Știi cum facturezi primul client."]
        ]},
        { theme: "Jumătate de zi", blocks: [
          [1, 85, "cont", "Programarea săptămânii 3", ["Cele 5 postări din săptămâna 3, cu texte. Una la 12:30, pentru test, restul la 19:00.", "Eticheta AI la fiecare."], "Săptămâna 3 e programată."],
          [2, 60, "admin", "Recuperezi ce a rămas", ["Blocurile nebifate care țin de lansare și de listă.", "Restul le muți în săptămâna 3."], "Lista și lansarea sunt complete."]
        ]},
        { theme: "Recenzie și odihnă", blocks: [] }
      ]
    },

    /* ---------------- Săptămâna 3 ---------------- */
    {
      title: "Mostrele N1 și lista de 30",
      goal: "5 mostre N1 (3 imagini și un reel fiecare), mesajele personalizate pregătite, oferta și contractul în ciornă.",
      kpi: ["5 / 5 mostre", "30 de mesaje personalizate", "5 postări Iness"],
      live: true,
      post: [1, 2, 4, 5, 6],
      eu: ["Oferta N1: o pagină sau un PDF cu pachetele", "Ciorna de contract și anexa „conținut AI”", "Scriptul apelului de 15 minute", "Mesajele personalizate pentru primele 10 firme"],
      days: [
        { theme: "Producție: mostre", blocks: [
          [1, 85, "prod", "Mostra 1: 3 imagini", ["Referința: poza produsului de pe site-ul brandului.", "Krea 2 + LoRA v2 sau Nano Banana: Iness cu produsul.", "Produsul identic: culoare, logo, formă, text."], "3 imagini care arată ca o reclamă reală."],
          [2, 45, "eu", "Sesiune cu Claude: săptămâna 3", ["Îmi arăți mostra 1.", "Îmi ceri oferta, contractul și scriptul apelului."], "Ai oferta și ciorna de contract."],
          [2, 75, "prod", "Lotul de imagini al lui Iness", ["Pod: 8 imagini pentru postările săptămânii.", "Oprești podul imediat după."], "8 imagini gata."],
          [3, 90, "vanz", "Mesajele personalizate: firmele 1–10", ["Pornești de la mesajele mele.", "Pentru fiecare: produsul lor, numele persoanei, linkul la mostră."], "10 mesaje gata de trimis."],
          [3, 60, "inv", "Reclamele celor 5 branduri", ["Ce reclame rulează, de cât timp, în ce format.", "Mostra ta trebuie să arate mai bine decât reclama lor de acum."], "Știi ce să le spui fiecăruia."]
        ]},
        { theme: "Producție: mostre", blocks: [
          [1, 85, "prod", "Mostra 2: 3 imagini", ["Aceeași rețetă ca la mostra 1.", "Verifici produsul cu poza originală, detaliu cu detaliu."], "3 imagini pentru brandul 2."],
          [2, 60, "prod", "Reel pentru mostra 1", ["2 clipuri I2V din cele mai bune imagini.", "Montaj de 8–10 s, 9:16, cu beneficiul produsului pe ecran."], "Mostra 1 e completă."],
          [2, 45, "cont", "Reel vorbit pentru Iness", ["Un hook din fișa ei, 10 s, cu vocea „Iness”.", "Îl programezi pentru joi."], "Reel programat."],
          [3, 90, "vanz", "Mesajele personalizate: firmele 11–20", ["Aceeași structură.", "Le notezi în tabel ca „gata de trimis”."], "20 de mesaje gata."],
          [3, 60, "admin", "Citești oferta și contractul", ["Notezi ce nu e clar sau ce ai schimba.", "Mi le trimiți în sesiunea următoare."], "Lista de întrebări e gata."]
        ]},
        { theme: "Producție: mostre", blocks: [
          [1, 85, "prod", "Mostra 3: 3 imagini", ["Aceeași rețetă.", "Dacă produsul are text sau logo, îl verifici literă cu literă."], "3 imagini pentru brandul 3."],
          [2, 60, "prod", "Reel pentru mostra 2", ["2 clipuri I2V, montaj de 8–10 s, 9:16."], "Mostra 2 e completă."],
          [2, 45, "cont", "Comunitate: 30 de minute", ["Răspunzi la tot și lași comentarii utile în nișă.", "Notezi întrebările care se repetă."], "Toate mesajele au răspuns."],
          [3, 90, "vanz", "Mesajele personalizate: firmele 21–30", ["Aceeași structură.", "Verifici că fiecare mesaj are numele corect al brandului."], "30 de mesaje gata."],
          [3, 60, "inv", "Apelul de vânzare: exersezi", ["Citești skill-ul sales-call.", "Exersezi cu voce tare: 2 minute despre ei, 5 problema, 5 mostra, 3 propunerea."], "Știi apelul pe de rost."]
        ]},
        { theme: "Producție: mostre", blocks: [
          [1, 85, "prod", "Mostra 4: 3 imagini", ["Aceeași rețetă.", "Încerci un alt tip de scenă: stradă, cafenea, seară."], "3 imagini pentru brandul 4."],
          [2, 60, "prod", "Reel pentru mostra 3", ["2 clipuri I2V, montaj de 8–10 s, 9:16."], "Mostra 3 e completă."],
          [2, 45, "cont", "Story-uri interactive", ["Sondaj: „Care ținută?” cu 2 poze.", "O întrebare deschisă."], "2 stories cu interacțiune."],
          [3, 120, "tech", "Workflow-ul pentru produs, salvat", ["Salvezi pe pod workflow-ul care a mers cel mai bine pentru mostre.", "Agentul îl notează în DARIA_CONTEXT.md."], "Mostrele următoare durează jumătate din timp."]
        ]},
        { theme: "Producție: mostre", blocks: [
          [1, 85, "prod", "Mostra 5: 3 imagini", ["Aceeași rețetă.", "Ultima mostră: alegi cel mai bun unghi din cele 4 de până acum."], "3 imagini pentru brandul 5."],
          [2, 60, "prod", "Reel pentru mostra 4", ["2 clipuri I2V, montaj de 8–10 s, 9:16."], "Mostra 4 e completă."],
          [2, 30, "cont", "Build in public: săptămâna 3", ["„Am făcut 5 reclame fără ședință foto.” O mostră, cu acordul brandului sau cu produsul ascuns."], "Postat."],
          [3, 60, "prod", "Reel pentru mostra 5", ["2 clipuri I2V, montaj de 8–10 s, 9:16."], "Mostra 5 e completă."],
          [3, 60, "admin", "Calendarul săptămânii 4", ["Programezi postările lui Iness pentru săptămâna 4.", "Îți blochezi orele pentru mesaje în calendar."], "Săptămâna 4 e programată."]
        ]},
        { theme: "Verificare", blocks: [
          [1, 85, "prod", "Verificarea celor 5 mostre", ["Lista de verificare: fața, mâinile, produsul, textul, formatul.", "Refaci orice imagine cu dubii."], "5 mostre fără greșeli."],
          [2, 30, "vanz", "Linkuri private pentru mostre", ["Un folder privat pentru fiecare brand (Google Drive), cu link de vizualizare.", "Linkul îl pui în mesajul lor."], "5 linkuri gata."],
          [2, 45, "cont", "Programarea săptămânii 4", ["Postările și textele.", "Eticheta AI la fiecare."], "Săptămâna 4 e programată."]
        ]},
        { theme: "Recenzie și odihnă", blocks: [] }
      ]
    },

    /* ---------------- Săptămâna 4 ---------------- */
    {
      title: "Abordarea celor 30",
      goal: "30 de firme contactate pe DM și email, prima revenire la 3 zile, primele răspunsuri notate, apelurile programate.",
      kpi: ["30 / 30 contactate", "≥ 5 răspunsuri", "Apelurile programate"],
      live: true,
      post: [1, 2, 4, 5, 6],
      eu: ["Răspunsurile la obiecții, din răspunsurile reale", "Mesajele ajustate după primele 10 trimiteri", "Întrebările și oferta pentru fiecare apel"],
      days: [
        { theme: "Vânzări", blocks: [
          [1, 85, "vanz", "Mesaje: firmele 1–6", ["Mesajul personalizat și linkul la mostra lor (sau la cea mai apropiată).", "DM pe Instagram și email, în aceeași zi.", "Notezi în tabel data și canalul."], "6 firme contactate."],
          [2, 75, "prod", "Lotul de imagini al lui Iness", ["Pod: 8 imagini pentru săptămână.", "Oprești podul imediat după."], "8 imagini gata."],
          [2, 45, "eu", "Sesiune cu Claude: săptămâna 4", ["Îmi trimiți primele răspunsuri, dacă există.", "Lucrăm împreună răspunsurile la obiecții."], "Ai răspunsurile pregătite."],
          [3, 90, "vanz", "Pregătești firmele 7–18", ["Verifici contactele: emailul, numele persoanei, contul de Instagram.", "Ajustezi mesajele."], "12 mesaje verificate."],
          [3, 60, "inv", "Obiecțiile: le exersezi", ["„E prea scump”, „Mă mai gândesc”, „E fals”.", "Răspunsurile din skill-ul sales-call, cu voce tare."], "Știi ce răspunzi la fiecare."]
        ]},
        { theme: "Vânzări", blocks: [
          [1, 85, "vanz", "Mesaje: firmele 7–12", ["Aceeași rețetă: mesaj personalizat și link la mostră.", "DM și email."], "12 firme contactate."],
          [2, 60, "prod", "Reel-ul săptămânii", ["Din imaginile de luni, 8–12 s.", "Îl programezi pentru joi."], "Reel programat."],
          [2, 45, "vanz", "Răspunzi la ce a venit", ["Răspunzi în aceeași zi.", "Cine vrea să vorbească: propui 2 intervale pentru apel."], "Toate răspunsurile au primit răspuns."],
          [3, 90, "prod", "Mostră nouă pentru cine a răspuns", ["Dacă un brand a răspuns cu interes, mai faci 2 imagini pe alt produs de-al lor.", "Le duci la apel."], "Mostra extra e gata."],
          [3, 60, "cont", "Comunitate", ["Comentarii utile la 10 conturi din nișă.", "Răspunsuri la toate mesajele lui Iness."], "Gata."]
        ]},
        { theme: "Vânzări", blocks: [
          [1, 85, "vanz", "Mesaje: firmele 13–18", ["Aceeași rețetă.", "Notezi în tabel."], "18 firme contactate."],
          [2, 60, "prod", "Reel vorbit pentru Iness", ["Un hook din fișa ei, 10 s, cu vocea „Iness”."], "Reel gata."],
          [2, 45, "vanz", "Răspunsuri și apeluri", ["Răspunzi la tot ce a venit.", "Programezi apelurile în săptămâna 5."], "Apelurile sunt în calendar."],
          [3, 120, "tech", "LoRA video: pregătirea datelor", ["Agentul pregătește clipurile pentru antrenarea Wan.", "Verifici că totul încape pe volum."], "Datele pentru LoRA video sunt gata."]
        ]},
        { theme: "Vânzări", blocks: [
          [1, 50, "vanz", "Mesaje: firmele 19–24", ["Aceeași rețetă."], "24 de firme contactate."],
          [1, 35, "vanz", "Revenirea 1: firmele 1–6", ["Mesajul de revenire din Anexa A, ziua 3.", "Oferi varianta 9:16 a mostrei."], "6 reveniri trimise."],
          [2, 60, "cont", "Carusel cu sfaturi de stil", ["5 slide-uri, textul cu skill-ul carousel-builder.", "Programat pentru sâmbătă."], "Carusel programat."],
          [2, 45, "vanz", "Răspunsuri și apeluri", ["Răspunzi la tot.", "Programezi apelurile."], "Toate mesajele au răspuns."],
          [3, 120, "prod", "Imagini pentru săptămâna 5", ["8 imagini noi pentru Iness.", "Alegi scene care au mers bine până acum."], "8 imagini gata."]
        ]},
        { theme: "Vânzări și public", blocks: [
          [1, 50, "vanz", "Mesaje: firmele 25–30", ["Aceeași rețetă."], "30 de firme contactate."],
          [1, 35, "vanz", "Revenirea 1: firmele 7–12", ["Mesajul de revenire, ziua 3."], "12 reveniri trimise."],
          [2, 45, "eu", "Ajustăm mesajele cu Claude", ["Îmi trimiți ce a răspuns lumea și ce n-a răspuns.", "Schimbăm o singură variabilă: primul rând sau oferta."], "Mesajul nou e gata."],
          [2, 30, "cont", "Build in public: săptămâna 4", ["Ce ai învățat din primele 30 de mesaje (fără nume de firme)."], "Postat."],
          [3, 120, "prod", "Reels pentru săptămâna 5", ["2 reels din imaginile de joi."], "2 reels gata."]
        ]},
        { theme: "Jumătate de zi", blocks: [
          [1, 85, "vanz", "Revenirea 1: firmele 13–18 și răspunsuri", ["Mesajul de revenire, ziua 3.", "Răspunzi la tot ce a venit în săptămână."], "Toate reveniri trimise."],
          [2, 45, "cont", "Programarea săptămânii 5", ["Postările și textele.", "Eticheta AI la fiecare."], "Săptămâna 5 e programată."],
          [2, 30, "vanz", "Calendarul apelurilor", ["Fiecare apel are oră, link și mostra pregătită."], "Apelurile sunt pregătite."]
        ]},
        { theme: "Recenzie și odihnă", blocks: [] }
      ]
    },

    /* ---------------- Săptămâna 5 ---------------- */
    {
      title: "Apeluri, piloți și decizia N1",
      goal: "Cel puțin 3 apeluri, cel puțin un pilot plătit (sau 2 piloți cu acord de studiu de caz) și decizia pentru nișa 1.",
      gate: "Decizia N1: ≥ 15% răspunsuri (≥ 5 din 30), ≥ 3 apeluri, ≥ 1 pilot plătit.",
      kpi: ["≥ 3 apeluri", "≥ 1 pilot plătit", "Decizia scrisă în jurnal"],
      live: true,
      post: [1, 2, 4, 5, 6],
      eu: ["Raportul sprintului N1: cifre și concluzii", "Contractul de pilot, final", "Modelul de factură și formularul de brief"],
      days: [
        { theme: "Vânzări", blocks: [
          [1, 50, "vanz", "Revenirea 1: firmele 19–30", ["Mesajul de revenire, ziua 3 (pentru cei de joi și vineri)."], "Toate primele reveniri trimise."],
          [1, 35, "vanz", "Revenirea 2: firmele 1–6", ["Mesajul din Anexa A, ziua 7: scurt, fără presiune."], "6 reveniri finale trimise."],
          [2, 75, "prod", "Lotul de imagini al lui Iness", ["Pod: 8 imagini.", "Oprești podul imediat după."], "8 imagini gata."],
          [2, 45, "eu", "Sesiune cu Claude: săptămâna 5", ["Pregătim fiecare apel: ce știm despre firmă, ce ofertă prezinți întâi."], "Fiecare apel are o fișă."],
          [3, 120, "vanz", "Repetiția apelului", ["Faci apelul de probă cu un prieten sau cu voce tare.", "Ai mostra deschisă pe ecran, oferta pregătită, linkul de plată sau factura."], "Ești pregătit."]
        ]},
        { theme: "Apeluri", blocks: [
          [1, 85, "vanz", "Apeluri de 15 minute", ["2 minute despre ei, 5 problema, 5 mostra, 3 propunerea.", "Prezinți întâi lansarea completă (490 €), apoi pachetul de 5 creative (99 €).", "Notezi răspunsul și motivul în tabel."], "Fiecare apel are rezultatul notat."],
          [2, 60, "prod", "Reel-ul săptămânii", ["8–12 s, din imaginile de luni."], "Reel programat."],
          [2, 45, "vanz", "Mesaje după apel", ["În aceeași zi: rezumatul, oferta și pasul următor.", "Fără reduceri la același pachet."], "Fiecare apel are mesajul de după."],
          [3, 120, "tech", "Pornești antrenarea LoRA video", ["Agentul pornește antrenarea Wan, după datele pregătite.", "O lași să ruleze; verifici seara."], "LoRA video se antrenează."]
        ]},
        { theme: "Vânzări", blocks: [
          [1, 50, "vanz", "Revenirea 2: firmele 7–18", ["Mesajul de revenire, ziua 7."], "Reveniri finale trimise."],
          [1, 35, "vanz", "Apeluri", ["Aceeași structură de 15 minute."], "Rezultatele notate."],
          [2, 60, "vanz", "Oferte scrise pentru cine a zis „da”", ["Contractul de pilot și factura.", "Condițiile scrise înainte de plată."], "Ofertele trimise."],
          [2, 45, "cont", "Comunitate", ["Răspunsuri și comentarii utile."], "Gata."],
          [3, 120, "prod", "Imagini pentru săptămâna 6", ["8 imagini noi pentru Iness."], "8 imagini gata."]
        ]},
        { theme: "Clienți", blocks: [
          [1, 85, "vanz", "Apeluri și piloți", ["Apelurile rămase.", "Cine a semnat: îi trimiți formularul de brief (Anexa B)."], "Piloții semnați au brief-ul."],
          [2, 60, "prod", "Pilotul 1: primele idei", ["Din brief: 10 idei, alegem 5 cu clientul.", "Folosești zona „Idei de conținut” de pe site."], "Ideile aprobate."],
          [2, 45, "vanz", "Revenirea 2: firmele 19–30", ["Mesajul de revenire, ziua 7."], "Toate reveniri trimise."],
          [3, 120, "tech", "Verifici LoRA video", ["Testezi checkpoint-urile pe 2 clipuri.", "Notezi ce merge."], "Știi dacă LoRA video e folosibil."]
        ]},
        { theme: "Decizie", blocks: [
          [1, 60, "admin", "Decizia pentru nișa 1", ["Cifrele: % răspunsuri, apeluri, piloți.", "Pragurile: ≥ 15% răspunsuri, ≥ 3 apeluri, ≥ 1 pilot plătit.", "Dacă nu sunt atinse: schimbăm mesajul și oferta și mai încercăm 2 săptămâni, sau trecem la N2."], "Decizia e scrisă în jurnal."],
          [1, 25, "eu", "Raportul sprintului, cu Claude", ["Îmi trimiți tabelul de vânzări.", "Scriu raportul și actualizez planul."], "Raportul e în repo."],
          [2, 60, "prod", "Pilotul 1: imaginile", ["Lotul 1: 6 imagini din ideile aprobate."], "6 imagini gata de verificare."],
          [2, 30, "cont", "Build in public: rezultatele sprintului", ["Cifrele, fără nume de firme."], "Postat."],
          [3, 120, "prod", "Reels pentru săptămâna 6", ["2 reels pentru Iness."], "2 reels gata."]
        ]},
        { theme: "Jumătate de zi", blocks: [
          [1, 85, "prod", "Pilotul 1: planul pe 14 zile", ["Ce livrăm, când, cum măsurăm.", "Îl trimiți clientului spre aprobare."], "Planul e aprobat."],
          [2, 45, "cont", "Programarea săptămânii 6", ["Atenție: 30 noiembrie și 1 decembrie sunt sărbători legale. Pregătești o postare de 1 Decembrie."], "Săptămâna 6 e programată."]
        ]},
        { theme: "Recenzie și odihnă", blocks: [] }
      ]
    },

    /* ---------------- Săptămâna 6 ---------------- */
    {
      title: "Pilotul N1 și pregătirea N2",
      goal: "Primul lot din pilotul N1 livrat, profilul și lista de 30 pentru nișa 2 (imobiliare).",
      kpi: ["Lotul 1 al pilotului livrat", "Lista N2: 30 de firme", "Fișa lui Matei (dacă e nevoie)"],
      live: true,
      post: [1, 2, 4, 5, 6],
      postTitles: { 2: "1 Decembrie: postarea de Ziua Națională" },
      eu: ["Codul F1: baza platformei (conturi, caractere, fișiere)", "Fișa detaliată N2 (imobiliare)", "Mesajele pentru N2"],
      days: [
        { theme: "Sărbătoare: producție ușoară", blocks: [
          [1, 85, "prod", "Pilotul 1: imaginile rămase și reels, lotul 1", ["Termini imaginile, dacă au rămas.", "2 reels din imaginile aprobate.", "Fără mesaje către firme azi."], "Lotul 1 e gata de verificare."]
        ]},
        { theme: "Sărbătoare: producție ușoară", blocks: [
          [1, 60, "prod", "Pilotul 1: verificare și livrare", ["Lista de verificare la fiecare fișier.", "Livrezi în folderul clientului, cu un mesaj scurt."], "Lotul 1 e livrat."],
          [1, 25, "cont", "Ziua Națională: comunitate", ["Răspunzi la comentariile de la postarea de 1 Decembrie."], "Gata."]
        ]},
        { theme: "Clienți și N2", blocks: [
          [1, 85, "vanz", "N2: profilul clientului ideal", ["Pornești de la fișa N2 de la mine.", "Dezvoltatori premium și agenții de top: ce postează, cine decide."], "Profilul e clar, cu 3 criterii."],
          [2, 45, "eu", "Sesiune cu Claude: săptămâna 6", ["Feedback-ul clientului la lotul 1.", "Îmi ceri fișa N2 și mesajele."], "Ai fișa N2."],
          [2, 75, "prod", "Lotul de imagini al lui Iness", ["Pod: 8 imagini."], "8 imagini gata."],
          [3, 60, "inv", "Studiu: imobiliarele pe Instagram", ["10 conturi de dezvoltatori și agenții din România.", "Cine face video, cine nu, ce tip de video."], "Știi ce lipsește în nișă."],
          [3, 90, "prod", "Matei: fișa și primele 20 de fețe", ["Doar dacă N2 cere un prezentator bărbat.", "Fișa de pe site, pagina Matei."], "20 de fețe pentru Matei."],
          [3, 45, "tech", "F1: conturile tehnice", ["Supabase și Vercel pe numele tău.", "Cheile nu le pui în chat."], "Conturile există."]
        ]},
        { theme: "Clienți", blocks: [
          [1, 85, "prod", "Pilotul 1: reviziile", ["Ce a cerut clientul, punct cu punct.", "Maximum 2 runde de revizii."], "Reviziile livrate."],
          [2, 60, "vanz", "Lista N2: firmele 1–15", ["Portaluri imobiliare, site-urile dezvoltatorilor, LinkedIn."], "15 firme în tabel."],
          [2, 60, "cont", "Reel-ul săptămânii", ["Din imaginile de miercuri."], "Reel programat."],
          [3, 120, "prod", "Matei: alegi fața", ["Din cele 20 de fețe alegi una.", "Corpul de referință: 4 imagini."], "Fața lui Matei e aleasă."]
        ]},
        { theme: "Vânzări și public", blocks: [
          [1, 85, "vanz", "Lista N2: firmele 16–30", ["Aceleași surse.", "Persoana de contact pentru fiecare."], "30 de firme N2 în tabel."],
          [2, 60, "prod", "Pilotul 1: lotul 2, planificare", ["Ce a mers în lotul 1, ce schimbăm.", "Ideile pentru lotul 2."], "Lotul 2 e planificat."],
          [2, 30, "cont", "Build in public", ["Ce am învățat din primul pilot."], "Postat."],
          [3, 120, "prod", "Imagini pentru săptămâna 7", ["8 imagini pentru Iness."], "8 imagini gata."]
        ]},
        { theme: "Jumătate de zi", blocks: [
          [1, 85, "prod", "Pilotul 1: lotul 2, imaginile", ["6 imagini noi."], "6 imagini gata."],
          [2, 45, "cont", "Programarea săptămânii 7", ["Postările și textele, etichetate."], "Săptămâna 7 e programată."]
        ]},
        { theme: "Recenzie și odihnă", blocks: [] }
      ]
    },

    /* ---------------- Săptămâna 7 ---------------- */
    {
      title: "Mostrele N2 și pilotul N1",
      goal: "5 mostre N2, lotul 2 al pilotului N1 livrat, mesajele N2 pregătite.",
      kpi: ["5 / 5 mostre N2", "Lotul 2 livrat", "30 de mesaje N2 gata"],
      live: true,
      post: [1, 2, 4, 5, 6],
      eu: ["Platforma internă (F1): biblioteca de caractere și de idei", "Scripturile pentru mostrele N2", "Raportul de la jumătatea pilotului"],
      days: [
        { theme: "Producție: mostre N2", blocks: [
          [1, 85, "prod", "Mostra N2 #1", ["Pozele publice ale unei proprietăți de la firma respectivă (doar pentru mostra trimisă lor).", "Video de 15–20 s: imagini animate și prezentatorul AI (Iness sau Matei), declarat AI."], "Mostra 1 e gata."],
          [2, 45, "eu", "Sesiune cu Claude: săptămâna 7", ["Scripturile pentru mostrele N2.", "Raportul de la jumătatea pilotului."], "Ai scripturile."],
          [2, 75, "prod", "Lotul de imagini al lui Iness", ["Pod: 8 imagini."], "8 imagini gata."],
          [3, 120, "prod", "Matei: setul de antrenare, partea 1", ["Pozele 01–17 după structura v2."], "17 poze gata."]
        ]},
        { theme: "Producție: mostre N2", blocks: [
          [1, 85, "prod", "Mostra N2 #2", ["Aceeași rețetă."], "Mostra 2 e gata."],
          [2, 60, "prod", "Pilotul 1: lotul 2, reels", ["2 reels."], "Reels gata."],
          [2, 45, "cont", "Reel-ul lui Iness", ["Din imaginile de luni."], "Programat."],
          [3, 120, "prod", "Matei: setul de antrenare, partea 2", ["Pozele 18–34."], "Setul lui Matei e complet."]
        ]},
        { theme: "Producție: mostre N2", blocks: [
          [1, 85, "prod", "Mostra N2 #3", ["Aceeași rețetă."], "Mostra 3 e gata."],
          [2, 60, "prod", "Pilotul 1: verificarea și livrarea lotului 2", ["Lista de verificare, apoi livrarea."], "Lotul 2 livrat."],
          [2, 45, "vanz", "Mesajele N2: firmele 1–15", ["Personalizate, cu linkul la mostră."], "15 mesaje gata."],
          [3, 120, "tech", "Matei: antrenarea LoRA", ["Agentul pornește antrenarea, ca la Iness."], "LoRA Matei se antrenează."]
        ]},
        { theme: "Producție: mostre N2", blocks: [
          [1, 85, "prod", "Mostra N2 #4", ["Aceeași rețetă."], "Mostra 4 e gata."],
          [2, 60, "vanz", "Mesajele N2: firmele 16–30", ["Personalizate."], "30 de mesaje gata."],
          [2, 45, "cont", "Carusel pentru Iness", ["5 slide-uri."], "Programat."],
          [3, 120, "tech", "Matei: alegi checkpoint-ul", ["Același test ca la Iness."], "Checkpoint ales."]
        ]},
        { theme: "Producție și public", blocks: [
          [1, 85, "prod", "Mostra N2 #5", ["Aceeași rețetă."], "Toate cele 5 mostre N2 sunt gata."],
          [2, 60, "admin", "Pilotul 1: cifrele de la jumătate", ["Statisticile reclamelor sau ale postărilor, de la client.", "Notezi în tabel."], "Cifrele sunt notate."],
          [2, 30, "cont", "Build in public", ["Primul video cu un prezentator AI pentru imobiliare (fără numele firmei)."], "Postat."],
          [3, 120, "prod", "Imagini pentru săptămâna 8", ["8 imagini pentru Iness."], "8 imagini gata."]
        ]},
        { theme: "Jumătate de zi", blocks: [
          [1, 85, "prod", "Verificarea mostrelor N2", ["Lista de verificare.", "Linkuri private pentru fiecare."], "5 mostre gata de trimis."],
          [2, 45, "cont", "Programarea săptămânii 8", ["Postările și textele, etichetate."], "Săptămâna 8 e programată."]
        ]},
        { theme: "Recenzie și odihnă", blocks: [] }
      ]
    },

    /* ---------------- Săptămâna 8 ---------------- */
    {
      title: "Abordarea N2 și raportul pilotului",
      goal: "30 de firme N2 contactate până joi, raportul pilotului N1 și propunerea de abonament.",
      kpi: ["30 / 30 firme N2 contactate", "Raportul pilotului trimis", "Propunerea de abonament"],
      live: true,
      post: [1, 2, 4, 5, 6],
      eu: ["Raportul pilotului N1 (skill-ul stats-report)", "Propunerea de abonament (skill-ul abonament-retentie)", "Răspunsurile la obiecții pentru N2"],
      days: [
        { theme: "Vânzări", blocks: [
          [1, 85, "vanz", "Mesaje N2: firmele 1–8", ["DM, email sau LinkedIn, cu linkul la mostră."], "8 firme contactate."],
          [2, 45, "eu", "Sesiune cu Claude: săptămâna 8", ["Raportul pilotului și propunerea de abonament."], "Ai raportul."],
          [2, 75, "prod", "Lotul de imagini al lui Iness", ["Pod: 8 imagini, cu tematică de iarnă."], "8 imagini gata."],
          [3, 120, "prod", "Conținutul de sărbători al lui Iness", ["Imagini pentru săptămânile 9 și 10: decembrie, cadouri, Revelion.", "Pregătești totul acum, ca să ai liber de sărbători."], "Conținutul de sărbători e gata."]
        ]},
        { theme: "Vânzări", blocks: [
          [1, 85, "vanz", "Mesaje N2: firmele 9–16", ["Aceeași rețetă."], "16 firme contactate."],
          [2, 60, "admin", "Raportul pilotului: îl citești", ["Verifici cifrele.", "Pregătești apelul de prezentare."], "Raportul e verificat."],
          [2, 45, "cont", "Reel-ul săptămânii", ["Din imaginile de luni."], "Programat."],
          [3, 120, "prod", "Reels de sărbători", ["3 reels pentru săptămânile 9 și 10."], "3 reels gata."]
        ]},
        { theme: "Vânzări", blocks: [
          [1, 85, "vanz", "Mesaje N2: firmele 17–24", ["Aceeași rețetă."], "24 de firme contactate."],
          [2, 60, "vanz", "Apelul de raport cu clientul N1", ["Ce am livrat, cifrele, ce am învățat.", "Propunerea de abonament, la momentul nevoii."], "Clientul are propunerea."],
          [2, 45, "vanz", "Revenirea 1: firmele N2 1–8", ["Mesajul de revenire, ziua 3."], "Reveniri trimise."],
          [3, 120, "tech", "Zonele de generare: ce cer clienții", ["Te uiți ce au generat vizitatorii (din mesajele primite) și ce întreabă.", "Notezi ce zonă lipsește sau ce trebuie îmbunătățit."], "Lista de îmbunătățiri e notată."]
        ]},
        { theme: "Vânzări", blocks: [
          [1, 85, "vanz", "Mesaje N2: firmele 25–30 și reveniri", ["Ultimele mesaje.", "Revenirea 1 pentru firmele 9–16."], "Toate cele 30 contactate."],
          [2, 60, "vanz", "Răspunsuri și apeluri N2", ["Programezi apelurile înainte de sărbători, dacă se poate."], "Apelurile sunt în calendar."],
          [2, 45, "cont", "Programarea sărbătorilor", ["Toate postările până pe 3 ianuarie, programate."], "Sărbătorile sunt acoperite."],
          [3, 120, "inv", "Turism și HoReCa: studiu pentru N3", ["Hoteluri boutique și pensiuni cu rating mare și Instagram slab.", "Notezi 15 exemple."], "15 locații notate."]
        ]},
        { theme: "Vânzări și public", blocks: [
          [1, 85, "vanz", "Apeluri N2 și reveniri", ["Apelurile programate.", "Revenirea 1 pentru firmele 17–30."], "Rezultatele sunt notate."],
          [2, 60, "vanz", "Clientul N1: abonamentul", ["Dacă a zis „da”: contract și factură.", "Dacă nu: află motivul și oferă varianta potrivită (fără reducere la același pachet)."], "Decizia clientului e notată."],
          [2, 30, "cont", "Build in public", ["Primul pilot încheiat: ce am învățat."], "Postat."],
          [3, 120, "prod", "Imagini pentru săptămâna 9", ["Ce lipsește din conținutul de sărbători."], "Gata."]
        ]},
        { theme: "Jumătate de zi", blocks: [
          [1, 85, "vanz", "Răspunsuri și reveniri", ["Tot ce a venit în săptămână."], "Toate mesajele au răspuns."],
          [2, 45, "admin", "Planul pentru sărbători", ["Ce faci în săptămânile 9 și 10, ce lași automat."], "Știi ce faci de sărbători."]
        ]},
        { theme: "Recenzie și odihnă", blocks: [] }
      ]
    },

    /* ---------------- Săptămâna 9 ---------------- */
    {
      title: "Sărbători: lista N3 și LoRA video",
      goal: "Lista de 30 de locații pentru N3, conținutul de sărbători rulând automat, LoRA video testat. Fără mesaje către firme.",
      kpi: ["Lista N3: 30 de locații", "Postările de sărbători rulează", "LoRA video testat"],
      live: true,
      post: [1, 2, 3, 6],
      eu: ["Fișa detaliată N3 (turism și HoReCa)", "Mesajele pentru N3, pentru ianuarie", "Ilinca: fișa completă"],
      days: [
        { theme: "Liste", blocks: [
          [1, 85, "vanz", "Lista N3: locațiile 1–15", ["Booking și Google Maps: rating mare și Instagram slab.", "Hoteluri boutique, pensiuni premium, rooftop-uri, spa-uri."], "15 locații în tabel."],
          [2, 45, "eu", "Sesiune cu Claude: săptămâna 9", ["Îmi ceri fișa N3 și fișa Ilincăi."], "Ai fișele."],
          [2, 60, "vanz", "Răspunsuri N2", ["Răspunzi la tot ce a venit."], "Gata."],
          [3, 120, "tech", "LoRA video: test complet", ["Un clip de 5 s cu Iness din LoRA video.", "Compari cu SCAIL-2 și cu I2V simplu."], "Știi ce folosești pentru video."]
        ]},
        { theme: "Liste", blocks: [
          [1, 85, "vanz", "Lista N3: locațiile 16–30", ["Aceleași surse."], "30 de locații în tabel."],
          [2, 60, "prod", "Ilinca: primele 20 de fețe", ["Fișa de pe site, pagina Ilinca."], "20 de fețe."],
          [3, 120, "prod", "Ilinca: alegi fața și corpul", ["Fața, apoi 4 imagini de corp."], "Referințele Ilincăi sunt gata."]
        ]},
        { theme: "Producție ușoară", blocks: [
          [1, 85, "prod", "Mostrele N3: alegi 5 locații", ["Cele mai potrivite 5 din listă.", "Salvezi pozele lor publice."], "5 locații alese."],
          [2, 60, "cont", "Comunitate", ["Răspunsuri la postările de sărbători."], "Gata."]
        ]},
        { theme: "Ajunul Crăciunului: liber după P1", blocks: [
          [1, 45, "cont", "Verifici postările programate", ["Totul iese la timp, cu eticheta AI.", "Răspunzi la mesaje, apoi închizi."], "Gata. Restul zilei e liber."]
        ]},
        { theme: "Crăciun", blocks: [] },
        { theme: "Crăciun", blocks: [] },
        { theme: "Recenzie și odihnă", blocks: [] }
      ]
    },

    /* ---------------- Săptămâna 10 ---------------- */
    {
      title: "Anul nou: mostrele N3",
      goal: "5 mostre N3 cu atmosferă de iarnă, planul pe ianuarie, Ilinca pregătită pentru antrenare.",
      kpi: ["5 / 5 mostre N3", "Planul pe ianuarie", "Setul Ilincăi început"],
      live: true,
      post: [1, 2, 4, 7],
      postTitles: { 4: "Postarea de Revelion" },
      eu: ["Scripturile mostrelor N3", "Planul pe ianuarie", "Mesajele N3, personalizate"],
      days: [
        { theme: "Producție: mostre N3", blocks: [
          [1, 85, "prod", "Mostra N3 #1", ["Imaginile reale ale locației (publice, doar pentru mostra trimisă lor).", "Ambasadorul „descoperă” locul, declarat AI. Reel de 10–15 s."], "Mostra 1 e gata."],
          [2, 45, "eu", "Sesiune cu Claude: săptămâna 10", ["Scripturile mostrelor N3 și planul pe ianuarie."], "Ai scripturile."],
          [2, 60, "prod", "Mostra N3 #2", ["Aceeași rețetă."], "Mostra 2 e gata."],
          [3, 120, "prod", "Ilinca: setul de antrenare, partea 1", ["Pozele 01–17."], "17 poze gata."]
        ]},
        { theme: "Producție: mostre N3", blocks: [
          [1, 85, "prod", "Mostra N3 #3", ["Aceeași rețetă."], "Mostra 3 e gata."],
          [2, 60, "prod", "Mostra N3 #4", ["Aceeași rețetă."], "Mostra 4 e gata."],
          [3, 120, "prod", "Ilinca: setul de antrenare, partea 2", ["Pozele 18–34."], "Setul Ilincăi e complet."]
        ]},
        { theme: "Producție: mostre N3", blocks: [
          [1, 85, "prod", "Mostra N3 #5 și verificarea", ["Ultima mostră și lista de verificare pentru toate 5."], "5 mostre N3 fără greșeli."],
          [2, 60, "vanz", "Mesajele N3, personalizate", ["30 de mesaje, cu linkul la mostră."], "30 de mesaje gata."]
        ]},
        { theme: "Revelion: liber după P1", blocks: [
          [1, 30, "admin", "Închiderea anului", ["Notezi în jurnal 3 lucruri care au mers în 2026 și unul pe care îl schimbi în 2027."], "Gata. Restul zilei e liber."]
        ]},
        { theme: "Anul Nou", blocks: [] },
        { theme: "Anul Nou", blocks: [] },
        { theme: "Recenzie și odihnă", blocks: [
          [1, 45, "cont", "Programarea săptămânii 11", ["Postările lui Iness pentru prima săptămână din ianuarie.", "6 și 7 ianuarie sunt sărbători legale."], "Săptămâna 11 e programată."]
        ]}
      ]
    },

    /* ---------------- Săptămâna 11 ---------------- */
    {
      title: "Abordarea N3 și decizia N2",
      goal: "30 de locații N3 contactate în zilele lucrătoare, decizia pentru nișa 2, LoRA Ilinca pornit.",
      gate: "Decizia N2: aceleași praguri ca la N1.",
      kpi: ["30 / 30 locații N3 contactate", "Decizia N2 scrisă", "LoRA Ilinca pornit"],
      live: true,
      post: [1, 2, 5, 6],
      eu: ["Raportul sprintului N2", "Răspunsurile la obiecții pentru N3", "Image-to-prompt și generarea dintr-un click în cod (F1)"],
      days: [
        { theme: "Vânzări", blocks: [
          [1, 85, "vanz", "Mesaje N3: locațiile 1–10", ["DM și email, cu linkul la mostră."], "10 locații contactate."],
          [2, 45, "eu", "Sesiune cu Claude: săptămâna 11", ["Tabelul N2: pregătim decizia."], "Decizia N2 e pregătită."],
          [2, 75, "prod", "Lotul de imagini al lui Iness", ["Pod: 8 imagini de ianuarie."], "8 imagini gata."],
          [3, 120, "tech", "Ilinca: antrenarea LoRA", ["Agentul pornește antrenarea."], "LoRA Ilinca se antrenează."]
        ]},
        { theme: "Vânzări", blocks: [
          [1, 85, "vanz", "Mesaje N3: locațiile 11–20", ["Aceeași rețetă."], "20 de locații contactate."],
          [2, 60, "admin", "Decizia pentru nișa 2", ["Pragurile: ≥ 15% răspunsuri, ≥ 3 apeluri, ≥ 1 pilot plătit.", "Scrii decizia în jurnal."], "Decizia N2 e scrisă."],
          [2, 45, "cont", "Reel-ul săptămânii", ["Din imaginile de luni."], "Programat."],
          [3, 120, "tech", "Ilinca: alegi checkpoint-ul", ["Același test ca la Iness."], "Checkpoint ales."]
        ]},
        { theme: "Sărbătoare (Boboteaza)", blocks: [
          [1, 60, "prod", "Producție ușoară", ["Imagini pentru săptămâna 12, fără mesaje către firme."], "Gata."]
        ]},
        { theme: "Sărbătoare (Sf. Ioan)", blocks: [
          [1, 60, "admin", "Pregătești bilanțul", ["Aduni cifrele celor 11 săptămâni într-un singur tabel."], "Tabelul bilanțului e gata."]
        ]},
        { theme: "Vânzări", blocks: [
          [1, 85, "vanz", "Mesaje N3: locațiile 21–30", ["Aceeași rețetă."], "30 de locații contactate."],
          [2, 60, "vanz", "Revenirea 1: locațiile 1–20", ["Mesajul de revenire (pentru cei contactați luni și marți)."], "Reveniri trimise."],
          [2, 30, "cont", "Build in public", ["Al treilea ambasador: Ilinca, în culise."], "Postat."],
          [3, 120, "prod", "Ilinca: primele 6 postări", ["Imagini și texte pentru lansarea ei (când decidem)."], "6 postări gata."]
        ]},
        { theme: "Jumătate de zi", blocks: [
          [1, 85, "vanz", "Răspunsuri și apeluri N3", ["Programezi apelurile în săptămâna 12."], "Apelurile sunt în calendar."],
          [2, 45, "cont", "Programarea săptămânii 12", ["Postările și textele, etichetate."], "Săptămâna 12 e programată."]
        ]},
        { theme: "Recenzie și odihnă", blocks: [] }
      ]
    },

    /* ---------------- Săptămâna 12 ---------------- */
    {
      title: "Bilanțul celor 12 săptămâni",
      goal: "Prețurile finale, nișele câștigătoare, decizia pentru platforma F1 și planul pe lunile 4–6.",
      gate: "Bilanț: ce nișe merg, ce prețuri rămân, ce construim în F1.",
      kpi: ["Raportul pe 12 săptămâni", "Prețurile finale", "Planul pe lunile 4–6"],
      live: true,
      post: [1, 2, 4, 5, 6],
      eu: ["Raportul complet pe 12 săptămâni", "Prețurile finale, după discuții", "Planul pe lunile 4–6 și actualizarea PLAN_COMPLET.md"],
      days: [
        { theme: "Apeluri N3", blocks: [
          [1, 85, "vanz", "Apeluri N3 și revenirea 2", ["Apelurile programate.", "Revenirea 2 pentru locațiile 1–20."], "Rezultatele notate."],
          [2, 45, "eu", "Sesiune cu Claude: bilanțul", ["Îmi trimiți toate tabelele.", "Pregătim raportul pe 12 săptămâni."], "Raportul e în lucru."],
          [2, 75, "prod", "Lotul de imagini al lui Iness", ["Pod: 8 imagini."], "8 imagini gata."]
        ]},
        { theme: "Bilanț: cifre", blocks: [
          [1, 85, "admin", "Cifrele celor 12 săptămâni", ["Contacte, răspunsuri, apeluri, piloți, clienți, venit, costuri.", "Pe fiecare nișă."], "Tabelul final e complet."],
          [2, 60, "vanz", "Revenirea 2: locațiile 21–30 și apeluri", ["Ultimele reveniri."], "Gata."],
          [2, 45, "cont", "Reel-ul săptămânii", ["Din imaginile de luni."], "Programat."]
        ]},
        { theme: "Bilanț: prețuri", blocks: [
          [1, 85, "admin", "Prețurile finale", ["Ce au zis clienții la fiecare pachet.", "Ce rămâne, ce se schimbă, după regulile din money-model."], "Prețurile finale sunt scrise."],
          [2, 60, "vanz", "Decizia N3", ["Aceleași praguri."], "Decizia N3 e scrisă."]
        ]},
        { theme: "Bilanț: platforma", blocks: [
          [1, 85, "admin", "Decizia pentru F1", ["Ce module construim primele, după ce a cerut lumea.", "Cât costă și cât durează."], "Decizia F1 e scrisă."],
          [2, 60, "tech", "F1: ce e deja făcut", ["Testezi tot ce e pe site și în repo: cele 5 zone de generare și platforma internă."], "Lista de buguri și de idei."]
        ]},
        { theme: "Planul pe lunile 4–6", blocks: [
          [1, 85, "eu", "Planul pe lunile 4–6, cu Claude", ["Nișele câștigătoare, caracterele, platforma, prețurile.", "Actualizăm PLAN_COMPLET.md și pagina asta."], "Planul nou e în repo."],
          [2, 30, "cont", "Build in public: 12 săptămâni", ["Ce am construit, ce am învățat, ce urmează."], "Postat."]
        ]},
        { theme: "Jumătate de zi", blocks: [
          [1, 60, "admin", "Celebrezi și te odihnești", ["Ai terminat primele 12 săptămâni.", "Notezi în jurnal 3 lucruri de care ești mândru."], "Gata."]
        ]},
        { theme: "Recenzie și odihnă", blocks: [] }
      ]
    }
  ],

  holidays: {
    "2026-11-30": "Sfântul Andrei",
    "2026-12-01": "Ziua Națională",
    "2026-12-25": "Crăciunul",
    "2026-12-26": "A doua zi de Crăciun",
    "2027-01-01": "Anul Nou",
    "2027-01-02": "Anul Nou",
    "2027-01-06": "Boboteaza",
    "2027-01-07": "Sfântul Ioan",
    "2027-01-24": "Unirea Principatelor",
    "2027-04-30": "Vinerea Mare",
    "2027-05-01": "Ziua Muncii",
    "2027-05-02": "Paștele",
    "2027-05-03": "A doua zi de Paște",
    "2027-06-01": "Ziua Copilului",
    "2027-06-20": "Rusaliile",
    "2027-06-21": "A doua zi de Rusalii"
  }
};
