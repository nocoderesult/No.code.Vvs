/* MUSQAI: conținutul site-ului. Tot ce se schimbă pe parcurs (caractere, procese, prețuri) se editează aici. */
window.MQ = {
  brand: {
    name: "MUSQAI",
    full: "Marketing Universe Studio · Quantum AI",
    tagline: "Ambasadori AI pentru branduri care vor să vândă.",
    email: "contact@musqai.com",
    instagram: "@musqai"
  },

  /* ---------------- Caracterele casei ---------------- */
  characters: [
    {
      id: "daria",
      name: "Daria",
      age: 25,
      role: "Ambasadoare lifestyle & lux",
      archetype: "Fata care știe locurile bune",
      status: "live",
      statusLabel: "În lucru · lansare în săpt. 2",
      palette: ["#0f2a20", "#2c6a4d", "#e9d9bd", "#c9a97a"],
      comp: [
        ["Vârstă", "25"],
        ["Păr", "Bob negru-corb, la maxilar, cărare laterală"],
        ["Ochi", "Verde-alune, migdalați"],
        ["Ten", "Bronzat cald"],
        ["Siluetă", "Clepsidră atletică"],
        ["Semne", "Fără tatuaje · cercei mici cu diamant"],
        ["Declanșator", "d4ria"]
      ],
      summary: "Daria arată produse de modă, bijuterii și locuri premium ca o prietenă cu gust bun. Calmă, încrezătoare, cu umor fin. Spune deschis că e AI.",
      look: "Bob negru-corb până la maxilar, cu cărare laterală. Ochi verde-alune, migdalați, gene dese. Ten bronzat cald, buze roz-prăfuit, pomeți înalți. Cercei mici cu diamant, gât curat, unghii medii migdală nude-roz. Fără tatuaje.",
      style: "Minimalist luxos: satin champagne, negru, alb, blazer bej, trench. Accesorii fine aurii. Machiaj natural ziua, smoky seara.",
      personality: ["încrezătoare", "caldă", "ironică fin", "atentă la detalii"],
      voice: {
        desc: "Română naturală, caldă, ușor joasă. Ritm calm, zâmbet în voce, dicție clară, fără accent regional marcat.",
        design: "Young Romanian woman, mid-20s, warm and slightly low voice, calm confident pace, friendly smile in the voice, clear diction, natural Romanian accent, studio-quality recording."
      },
      niches: ["Magazine online: modă, bijuterii, accesorii", "Turism premium", "Evenimente", "HoReCa premium"],
      pillars: [
        ["Outfit-uri și detalii", 30, "3 piese care fac orice ținută să pară scumpă"],
        ["Locuri și experiențe", 25, "Am testat cel mai fotogenic rooftop din oraș"],
        ["Rutina ei", 20, "O dimineață de duminică, în 15 secunde"],
        ["Din culise AI", 15, "Sunt AI. Uite cum se face o ședință foto fără fotograf"],
        ["Colaborări declarate", 10, "#ad · rochia de satin de la un brand românesc"]
      ],
      hooks: [
        "Dacă porți negru tot timpul, salvează asta.",
        "Nu sunt reală. Ținuta asta e.",
        "Bugetul a fost 300 de lei. Arată de 3.000.",
        "Trei lucruri pe care nu le mai port după 25 de ani."
      ],
      rules: {
        do: [
          "„AI creator” în bio și eticheta AI la fiecare postare",
          "Produsul arătat exact ca în realitate (după pozele brandului)",
          "#ad sau „Paid partnership” la colaborări plătite",
          "Același aspect în fiecare imagine (checklist-ul din fișă)"
        ],
        dont: [
          "Nu spune că a cumpărat sau a folosit produsul ca o persoană reală",
          "Fără nuditate, fără conținut sugestiv explicit",
          "Fără promisiuni de sănătate sau de rezultat corporal",
          "Nu apare lângă minori și nu face conținut politic"
        ]
      },
      prompt: "d4ria, a 25-year-old woman with radiant warm tan skin, a sleek jet-black bob haircut ending at her jawline with a sharp side part, piercing almond-shaped green-hazel eyes, long voluminous dark eyelashes, dark sculpted eyebrows, full dusty-pink lips, high cheekbones with a soft natural glow, small diamond stud earrings, clear smooth neck, athletic hourglass figure with a narrow toned waist, full proportionate bust and rounded hips, toned legs, medium almond-shaped nude-pink nails, natural skin texture",
      negative: "tattoo, text, watermark, extra fingers, plastic skin, airbrushed",
      schedule: "5 postări pe săptămână, la 19:00 (test și la 12:30) · stories zilnic",
      platforms: ["Instagram", "TikTok"],
      handle: "@daria.musqai (propus)",
      pipeline: [
        ["Fișa personajului", "done"],
        ["Fața și corpul de referință", "done"],
        ["Setul de antrenare v1", "done"],
        ["LoRA v1 (Krea 2), pasul 2500", "done"],
        ["Setul v2: 34 de poze, fără tatuaj", "doing"],
        ["LoRA v2 + testul de realism", "todo"],
        ["Vocea „Daria”", "todo"],
        ["Conturile IG și TikTok", "todo"],
        ["LoRA video (Wan)", "todo"]
      ]
    },
    {
      id: "matei",
      name: "Matei",
      age: 33,
      role: "Ambasador business & imobiliare",
      archetype: "Consultantul pe care îl suni",
      status: "casting",
      statusLabel: "În casting · săpt. 6–7",
      palette: ["#101a2b", "#2b4466", "#d6dde8", "#8aa4c8"],
      comp: [
        ["Vârstă", "33"],
        ["Păr", "Șaten-închis, scurt, cu cărare laterală"],
        ["Ochi", "Căprui-închis"],
        ["Ten", "Deschis-măsliniu"],
        ["Siluetă", "Atletic-zvelt, 1,85 m"],
        ["Semn", "Barbă scurtă îngrijită · ceas metalic"],
        ["Declanșator", "m4tei"]
      ],
      summary: "Matei prezintă proprietăți, mașini și servicii ca un om de încredere. Direct, calm, fără vorbe goale.",
      look: "Păr șaten-închis, scurt, cu cărare laterală. Barbă scurtă, bine îngrijită. Ochi căprui-închis, maxilar definit. Ten deschis-măsliniu. Siluetă atletic-zveltă. Ceas metalic discret.",
      style: "Smart casual: cămăși albe și bleu, sacou navy, pulover de merinos, pantofi maro. Fără logo-uri mari.",
      personality: ["calm", "de încredere", "direct", "atent la cifre"],
      voice: {
        desc: "Baritonală caldă, ritm măsurat, clar. Sună ca un consultant bun, nu ca un vânzător.",
        design: "Romanian man in his early 30s, warm baritone voice, measured calm pace, clear and trustworthy, slight smile, studio-quality recording."
      },
      niches: ["Imobiliare: dezvoltatori premium, agenții", "Auto", "Servicii B2B", "Modă masculină"],
      pillars: [
        ["Tururi de proprietăți", 35, "Apartamentul ăsta are o cameră pe care n-o vezi în anunț"],
        ["Piața pe scurt", 25, "Prețurile din cartierul tău, luna asta, în 30 de secunde"],
        ["Sfaturi de cumpărare", 25, "5 întrebări pe care să le pui la vizionare"],
        ["Viața de business", 15, "O zi de lucru, de la 7 la 7"]
      ],
      hooks: [
        "Nu cumpăra apartament până nu verifici asta.",
        "Am întrebat un dezvoltator ce nu scrie în broșură.",
        "Diferența de preț dintre etajul 2 și 8, explicată."
      ],
      rules: {
        do: [
          "Proprietatea e filmată real; Matei e doar prezentatorul",
          "Cifrele vin de la client sau din surse publice citate",
          "Eticheta AI la fiecare video"
        ],
        dont: [
          "Nu inventează finisaje, priveliști sau dotări",
          "Nu dă sfaturi financiare personalizate",
          "Nu promite randamente"
        ]
      },
      prompt: "m4tei, a 33-year-old man with light olive skin, short dark-brown hair neatly side-parted, a short well-groomed beard, deep brown eyes, defined jawline, athletic lean build, minimalist steel watch, natural skin texture",
      negative: "tattoo, text, watermark, extra fingers, plastic skin",
      schedule: "3 video-uri pe săptămână · LinkedIn + Instagram",
      platforms: ["Instagram", "LinkedIn", "YouTube Shorts"],
      handle: "@matei.musqai (propus)",
      pipeline: [
        ["Fișa personajului", "done"],
        ["40 de fețe, alegerea uneia", "todo"],
        ["Corpul de referință", "todo"],
        ["Setul de antrenare (34)", "todo"],
        ["LoRA imagini", "todo"],
        ["Vocea", "todo"],
        ["Conturile", "todo"]
      ]
    },
    {
      id: "ilinca",
      name: "Ilinca",
      age: 29,
      role: "Exploratoare: travel & food",
      archetype: "Prietena care găsește mereu locul",
      status: "casting",
      statusLabel: "În casting · săpt. 9–10",
      palette: ["#2a1a10", "#8a5a36", "#f2dcc2", "#e0a873"],
      comp: [
        ["Vârstă", "29"],
        ["Păr", "Castaniu-arămiu, lung, ondulat"],
        ["Ochi", "Căprui-verzi"],
        ["Ten", "Deschis cald, pistrui fini"],
        ["Siluetă", "Zveltă"],
        ["Semn", "Zâmbet larg · pălărie de paie"],
        ["Declanșator", "il1nca"]
      ],
      summary: "Ilinca descoperă hoteluri, pensiuni și restaurante. Curioasă, spontană, povestește ca o prietenă care tocmai s-a întors din vacanță.",
      look: "Păr castaniu-arămiu, lung, ondulat, des prins într-un coc lejer. Ochi căprui-verzi, pistrui fini pe nas. Ten deschis cald. Zâmbet larg. Siluetă zveltă.",
      style: "In natural, cămăși oversize, pălărie de paie, sneakers albi, rucsac mic. Culori de pământ.",
      personality: ["curioasă", "spontană", "caldă", "bună povestitoare"],
      voice: {
        desc: "Luminoasă și energică, ușor răgușită. Vorbește repede când e entuziasmată.",
        design: "Romanian woman around 30, bright energetic voice with a slight rasp, enthusiastic storyteller, natural pace, studio-quality recording."
      },
      niches: ["Hoteluri boutique și pensiuni", "Restaurante și cafenele", "Experiențe și tururi"],
      pillars: [
        ["Weekend în…", 35, "48 de ore în Sibiu, fără să stai la coadă"],
        ["Ce comand aici", 25, "Trei feluri pe care nu le ratezi la locul ăsta"],
        ["Locuri ascunse", 25, "Pensiunea cu 9 camere pe care n-o găsești pe prima pagină"],
        ["Ghid de sezon", 15, "Unde mergi în decembrie dacă nu vrei aglomerație"]
      ],
      hooks: [
        "Locul ăsta are 9 camere și e plin până în martie.",
        "Am venit pentru priveliște. Am rămas pentru mic-dejun.",
        "Nu-ți spun unde e. Ba da, îți spun."
      ],
      rules: {
        do: [
          "Ambasador AI declarat, nu oaspete real",
          "Imaginile locației sunt reale, de la client",
          "Eticheta AI la fiecare postare"
        ],
        dont: [
          "Nu scrie recenzii și nu dă note",
          "Nu inventează facilități sau priveliști",
          "Nu promovează consum excesiv de alcool"
        ]
      },
      prompt: "il1nca, a 29-year-old woman with fair warm skin and light freckles across her nose, long wavy copper-brown hair in a loose low bun, hazel-brown eyes, wide genuine smile, slim build, natural skin texture",
      negative: "tattoo, text, watermark, extra fingers, plastic skin",
      schedule: "4 postări pe săptămână · Reels + carusele",
      platforms: ["Instagram", "TikTok"],
      handle: "@ilinca.musqai (propus)",
      pipeline: [
        ["Fișa personajului", "done"],
        ["40 de fețe, alegerea uneia", "todo"],
        ["Corpul de referință", "todo"],
        ["Setul de antrenare (34)", "todo"],
        ["LoRA imagini", "todo"],
        ["Vocea", "todo"],
        ["Conturile", "todo"]
      ]
    },
    {
      id: "ioana",
      name: "Ioana",
      age: 27,
      role: "Vecina de alături: produse de zi cu zi",
      archetype: "Omul practic din grupul de prieteni",
      status: "planned",
      statusLabel: "Planificat · când îl cer magazinele",
      palette: ["#1d2430", "#5b6f8a", "#efe6da", "#d9b99b"],
      comp: [
        ["Vârstă", "27"],
        ["Păr", "Blond-închis, până la umeri, coc lejer"],
        ["Ochi", "Albaștri-cenușii"],
        ["Ten", "Deschis, natural"],
        ["Siluetă", "Medie"],
        ["Semn", "Machiaj aproape absent"],
        ["Declanșator", "i0ana"]
      ],
      summary: "Ioana arată cum se folosesc lucrurile de zi cu zi, acasă, în bucătărie sau în mașină. Sinceră, amuzantă, practică.",
      look: "Păr blond-închis până la umeri, des prins într-un coc lejer. Ochi albaștri-cenușii. Ten deschis, natural, machiaj discret. Înălțime medie. Față relaxată, prietenoasă.",
      style: "Hanorace, tricouri simple, blugi, pijamale comode. Decoruri reale: casă, bucătărie, mașină.",
      personality: ["sinceră", "amuzantă", "practică", "directă"],
      voice: {
        desc: "Naturală, conversațională, ritm alert. Sună ca un mesaj vocal de la o prietenă.",
        design: "Romanian woman in her late 20s, natural conversational voice, quick friendly pace, casual and funny, like a voice message to a friend."
      },
      niches: ["Magazine online mass-market", "Casă și decor", "Produse de zi cu zi", "Aplicații"],
      pillars: [
        ["Prima impresie", 35, "Am deschis cutia. Uite ce e înăuntru"],
        ["Cum se folosește", 30, "Trei feluri de a folosi asta în bucătărie"],
        ["Trucuri pentru casă", 20, "Dulapul meu, organizat în 10 minute"],
        ["O zi obișnuită", 15, "Ce fac luni la 7 dimineața"]
      ],
      hooks: [
        "Nimeni nu mi-a spus că se poate face și așa.",
        "Trei lucruri din bucătărie pe care le folosesc zilnic.",
        "Dacă ai un balcon mic, uite."
      ],
      rules: {
        do: [
          "Demonstrație de produs făcută de un ambasador AI declarat",
          "Arată ce face produsul, cu imagini reale de la brand",
          "Eticheta AI la fiecare postare"
        ],
        dont: [
          "Nu spune „l-am cumpărat” sau „îl folosesc de 3 luni”",
          "Nu face „recenzii” și nu dă stele",
          "Nu compară cu produse concurente pe nume"
        ]
      },
      prompt: "i0ana, a 27-year-old woman with fair natural skin, shoulder-length dark-blonde hair in a messy bun, grey-blue eyes, light natural makeup, relaxed friendly face, average height, natural skin texture",
      negative: "tattoo, text, watermark, extra fingers, plastic skin",
      schedule: "5 clipuri pe săptămână · stil UGC, 9:16",
      platforms: ["TikTok", "Instagram"],
      handle: "@ioana.musqai (propus)",
      pipeline: [
        ["Fișa personajului", "done"],
        ["40 de fețe, alegerea uneia", "todo"],
        ["Corpul de referință", "todo"],
        ["Setul de antrenare (34)", "todo"],
        ["LoRA imagini", "todo"],
        ["Vocea", "todo"],
        ["Conturile", "todo"]
      ]
    },
    {
      id: "mira",
      name: "Mira",
      age: 30,
      role: "Fața platformei MUSQAI",
      archetype: "Explică AI-ul ca pe o rețetă",
      status: "planned",
      statusLabel: "Planificat · faza 2, platforma",
      palette: ["#141414", "#3d4a44", "#e6ece8", "#6bc497"],
      comp: [
        ["Vârstă", "30"],
        ["Păr", "Șaten-închis, lung, drept, cu breton"],
        ["Ochi", "Căprui-închis"],
        ["Ten", "Măsliniu cald"],
        ["Siluetă", "Zveltă"],
        ["Semn", "Ochelari rotunzi cu ramă subțire"],
        ["Declanșator", "m1ra"]
      ],
      summary: "Mira explică pe scurt cum folosesc afacerile AI-ul și arată ce se întâmplă în culisele MUSQAI. Clară, calmă, cu umor sec.",
      look: "Păr șaten-închis, lung, drept, cu breton drept. Ochi căprui-închis. Ten măsliniu cald. Ochelari rotunzi cu ramă subțire. Siluetă zveltă.",
      style: "Minimalist tech: negru, gri, un singur accent verde-jad. Cămăși structurate, pulovere fine.",
      personality: ["clară", "calmă", "deșteaptă", "umor sec"],
      voice: {
        desc: "Clară, registru mediu, profesională și prietenoasă. Pauze scurte înainte de ideile importante.",
        design: "Romanian woman around 30, clear medium-pitched voice, professional and friendly, calm explainer pace, short pauses before key points."
      },
      niches: ["Promovarea MUSQAI", "Educație AI pentru afaceri"],
      pillars: [
        ["AI pentru afaceri în 60 de secunde", 40, "Cum faci 30 de poze de produs fără ședință foto"],
        ["Din culisele MUSQAI", 30, "Așa arată o zi în studio"],
        ["Studii de caz (cu acordul clientului)", 20, "Ce s-a schimbat după 30 de zile"],
        ["Știri AI pe scurt", 10, "Ce a apărut săptămâna asta și ce înseamnă pentru tine"]
      ],
      hooks: [
        "Ai un magazin online? Asta te costă mai puțin decât crezi.",
        "Sunt AI și îți explic de ce contează eticheta asta.",
        "Ce nu-ți spune nimeni despre reclamele cu AI."
      ],
      rules: {
        do: [
          "Explică simplu, cu exemple reale",
          "Studiile de caz doar cu acord scris",
          "Eticheta AI la fiecare postare"
        ],
        dont: [
          "Fără promisiuni de venit",
          "Fără atacuri la concurenți",
          "Fără cifre neverificate"
        ]
      },
      prompt: "m1ra, a 30-year-old woman with warm olive skin, long straight dark-brown hair with blunt bangs, dark brown eyes, thin-framed round glasses, calm confident expression, minimalist black and grey clothing, natural skin texture",
      negative: "tattoo, text, watermark, extra fingers, plastic skin",
      schedule: "3 postări pe săptămână · LinkedIn + TikTok",
      platforms: ["LinkedIn", "TikTok", "YouTube Shorts"],
      handle: "@mira.musqai (propus)",
      pipeline: [
        ["Fișa personajului", "done"],
        ["40 de fețe, alegerea uneia", "todo"],
        ["Corpul de referință", "todo"],
        ["Setul de antrenare (34)", "todo"],
        ["LoRA imagini", "todo"],
        ["Vocea", "todo"],
        ["Conturile", "todo"]
      ]
    }
  ],

  /* ---------------- Nișele (testate pe rând) ---------------- */
  niches: [
    {
      id: "n1", code: "N1", name: "Magazine online", order: "Prima nișă testată",
      who: "Branduri românești de modă, accesorii, bijuterii și decor, cu magazin online și 1–20 de angajați, care rulează deja reclame.",
      pain: "Reclamele se uzează repede, ședințele foto sunt scumpe și n-au o față constantă.",
      deliver: ["Poze lifestyle cu produsul pe ambasador", "Reels de 8–15 s pentru reclame și organic", "Variante de hook pentru test A/B", "Textele, în română"],
      rules: ["Produsul identic cu realitatea, după pozele brandului", "Ambasador AI declarat, nu „clientă”", "Eticheta AI la fiecare postare"],
      metric: "CTR și ROAS față de reclamele vechi · costul pe creativ",
      character: "daria"
    },
    {
      id: "n2", code: "N2", name: "Imobiliare", order: "A doua",
      who: "Dezvoltatori premium și agenții de top.",
      pain: "Fac puțin video, producția e scumpă, iar ansamblurile sunt greu de „vândut” emoțional.",
      deliver: ["Prezentator AI în video cu proprietatea filmată real", "„O zi în viața ta aici”", "Noutăți de piață săptămânale"],
      rules: ["Nu inventăm finisaje, priveliști sau dotări", "Cifrele vin de la client", "Eticheta AI"],
      metric: "Cereri de vizionare · lead-uri",
      character: "matei"
    },
    {
      id: "n3", code: "N3", name: "Turism și HoReCa", order: "A treia",
      who: "Hoteluri boutique, pensiuni premium, rooftop-uri, spa-uri, restaurante.",
      pain: "Conținutul e sezonier, fotografii sunt scumpi, iar „atmosfera” e greu de prins.",
      deliver: ["Ambasadorul „descoperă” locul, pe imagini reale ale locației", "Reels de atmosferă", "Ghiduri de sezon"],
      rules: ["Ambasador AI declarat, nu oaspete real", "Fără recenzii false", "Fără facilități inventate"],
      metric: "Rezervări și mesaje venite din Instagram",
      character: "ilinca"
    },
    {
      id: "n4", code: "N4", name: "Evenimente și nightlife", order: "A patra",
      who: "Cluburi, organizatori de evenimente, festivaluri mici.",
      pain: "Promovarea începe târziu și arată la fel de la un eveniment la altul.",
      deliver: ["Teasere și numărători inverse", "Anunțuri de line-up", "Recapitulări după eveniment"],
      rules: ["Regulile de reclamă pentru alcool", "Fără minori", "Eticheta AI"],
      metric: "Bilete vândute · înscrieri",
      character: "daria"
    },
    {
      id: "n5", code: "N5", name: "Wellness și cosmetice", order: "La final, cu reguli stricte",
      who: "Studiouri de fitness, spa-uri, branduri de cosmetice.",
      pain: "Conținutul trebuie să fie frumos, dar fără să promită rezultate.",
      deliver: ["Prezentarea produsului sau a serviciului", "Atmosfera locului", "Educație fără promisiuni"],
      rules: ["Fără înainte/după", "Fără promisiuni medicale sau de rezultat corporal", "Un corp generat nu e prezentat ca rezultat"],
      metric: "Programări · mesaje",
      character: "ioana"
    }
  ],

  /* ---------------- Ofertele ---------------- */
  offers: {
    entry: {
      small: { name: "5 creative AI", price: "99 €", items: ["5 imagini cu produsul tău pe un ambasador AI", "Format pentru reclame (4:5 și 9:16)", "Gata în 5 zile lucrătoare"] },
      full: { name: "Lansarea completă", price: "490 €", items: ["Ambasador AI dedicat campaniei", "12 creative: poze și reels", "Variante de hook pentru test A/B", "Textele reclamelor", "Raport după 14 zile"] }
    },
    guarantee: "Dacă ne trimiți materialele în 48 de ore, rulezi creativele cel puțin 14 zile și ne dai cifrele, toată suma plătită se scade din abonamentul pe 6 luni.",
    prepay: "Plătești 5 luni în avans, a 6-a e gratuită."
  },

  packages: [
    { id: "start", name: "Start", price: "350 €", per: "pe lună", note: "Pentru primul ambasador", items: ["8 poze", "4 reels", "Textele, în română", "Calendarul de postare"] },
    { id: "growth", name: "Growth", price: "700 €", per: "pe lună", note: "Pentru branduri care rulează reclame", items: ["12 poze", "8 reels", "Variante pentru reclame (A/B)", "Raport lunar", "Tot din Start"], featured: true },
    { id: "pro", name: "Pro", price: "de la 1.200 €", per: "pe lună", note: "Un caracter doar al tău", items: ["Caracter dedicat, exclusiv pe nișa ta", "Strategie lunară", "Tot din Growth"] }
  ],

  extras: [
    ["Caracter exclusiv", "setup unic, apoi îl folosești doar tu"],
    ["Voce și sincronizarea buzelor", "ambasadorul vorbește în română"],
    ["Alte limbi", "aceleași clipuri, dublate"],
    ["Automatizare DM", "răspunsuri la mesajele venite din reclame"]
  ],

  faq: [
    ["E legal să folosesc un ambasador AI?", "Da, dacă e etichetat corect. Din 2 august 2026, în UE, conținutul generat cu AI care pare real trebuie marcat (AI Act, articolul 50). Noi etichetăm fiecare postare. În platformă adăugăm și marcajul în fișier."],
    ["Oamenii vor ști că e AI?", "Da. Ambasadorul are „AI creator” în bio, iar fiecare postare are eticheta AI. Produsul e real și arată exact ca în magazin."],
    ["Produsul meu va arăta exact ca în realitate?", "Lucrăm după pozele voastre. Nu schimbăm culoarea, forma, logo-ul sau textul de pe produs, iar fiecare livrabil trece printr-o verificare înainte să-l primiți."],
    ["Pot avea un caracter doar al meu?", "Da. În pachetul Pro creăm un caracter exclusiv pentru nișa ta, cu voce proprie. Caracterele casei (Daria și ceilalți) rămân ale MUSQAI."],
    ["Cât durează până primesc primele materiale?", "Mostra o primești în 3–5 zile lucrătoare de la brief. În abonament, livrăm săptămânal."],
    ["Ce se întâmplă dacă nu-mi place?", "Ai două runde de revizii la fiecare livrabil. Abonamentul se anulează cu o lună înainte, iar condițiile sunt scrise în contract."],
    ["Folosiți fețe de oameni reali?", "Doar cu acordul scris al persoanei și după verificare. Nu facem niciodată conținut cu fețe reale fără acord."]
  ],

  /* ---------------- Cum lucrăm ---------------- */
  steps: [
    ["Brief", "Produsul, publicul, tonul, obiectivul și ce NU vrei. Un formular de 15 minute.", "formular"],
    ["Idei și scripturi", "Hook-uri, scenarii și texte, scrise pe vocea ambasadorului.", "Claude + skill-urile de conținut"],
    ["Imagini", "Ambasadorul cu produsul tău, după pozele tale ca referință.", "Krea 2 + LoRA + realism"],
    ["Video", "Clipuri din imagini, înlocuire în filmări reale sau video din cloud, când merită.", "Wan 2.2 · SCAIL-2 · Seedance / Kling"],
    ["Voce", "Vocea ambasadorului și sincronizarea buzelor.", "ElevenLabs + lip-sync"],
    ["Editare", "Tăieturi pe ritm, subtitrări în română, text pe ecran, muzică licențiată.", "CapCut / DaVinci, apoi automat"],
    ["Verificare", "Fața, mâinile, produsul, eticheta AI, formatul. Nimic nu pleacă nebifat.", "lista de verificare"],
    ["Livrare și programare", "Fișierele în folderul tău și postările programate la orele bune.", "calendar"],
    ["Raport", "Ce a mers, ce am învățat, ce schimbăm luna viitoare.", "raport lunar"]
  ],

  timeline: [
    ["Ziua 0", "Apel de 15 minute și brief-ul."],
    ["Ziua 1–2", "Ideile și planul pe 30 de zile, trimise spre aprobare."],
    ["Ziua 3–5", "Primele livrabile: poze și reels."],
    ["Ziua 7", "Postările programate. Prima săptămână live."],
    ["Ziua 14", "Primele cifre și ajustările."],
    ["Ziua 30", "Raportul lunar și planul pentru luna următoare."]
  ],

  clientGives: ["Pozele reale ale produselor sau ale locației", "Logo-ul și culorile", "Ce vrei să vinzi luna asta", "Accesul la statistici (opțional, pentru raport)"],

  /* ---------------- Procesele (biblioteca din Studio) ---------------- */
  processes: [
    {
      id: "livrabil", name: "Livrabil nou: de la brief la postare", area: "Producție", time: "1–3 zile",
      steps: [
        ["Brief-ul clientului", "Client", "formularul (Anexa B)", "15 min"],
        ["Idei, hook-uri, scripturi", "Claude", "skill-urile de conținut", "30 min"],
        ["Imaginile", "Tu", "pod: Krea 2 + LoRA + realism", "10–20 min / poză"],
        ["Clipurile video", "Tu", "Wan 2.2 I2V · SCAIL-2 · cloud", "45–90 min / reel"],
        ["Vocea și buzele", "Tu", "ElevenLabs + HeyGen / LatentSync", "20 min"],
        ["Editarea", "Tu", "CapCut / DaVinci", "30 min / reel"],
        ["Verificarea calității", "Tu", "lista de verificare", "10 min"],
        ["Livrarea și programarea", "Tu", "folderul clientului + Meta Business Suite", "15 min"]
      ]
    },
    {
      id: "vanzare", name: "Vânzarea: de la listă la contract", area: "Vânzări", time: "3 săptămâni",
      steps: [
        ["Lista: 30 de firme pe nișă", "Tu", "Biblioteca de reclame Meta, Instagram", "2 h"],
        ["Mostra personalizată", "Tu", "produsul lor pe ambasador", "1–2 h / mostră"],
        ["Primul mesaj: DM și email", "Tu", "Anexa A", "10 min / firmă"],
        ["Revenirea 1, ziua 3", "Tu", "Anexa A", "5 min / firmă"],
        ["Revenirea 2, ziua 7", "Tu", "Anexa A", "5 min / firmă"],
        ["Apelul de 15 minute", "Tu", "skill-ul sales-call", "15 min"],
        ["Pilotul și contractul", "Tu + Claude", "ciorna de contract", "30 min"]
      ]
    },
    {
      id: "onboarding", name: "Clientul nou: primele 14 zile", area: "Clienți", time: "14 zile",
      steps: [
        ["Contractul și factura", "Tu", "modelul de contract", "ziua 0"],
        ["Materialele clientului", "Client", "în 48 h", "ziua 1–2"],
        ["Apelul de pornire", "Tu", "30 min", "ziua 2"],
        ["Planul pe 30 de zile", "Claude", "skill-ul content-calendar", "ziua 2"],
        ["Primele livrabile", "Tu", "linia de producție", "ziua 3–5"],
        ["Postările programate", "Tu", "Meta Business Suite", "ziua 7"],
        ["Primele cifre și ajustări", "Tu + Claude", "skill-ul stats-report", "ziua 14"]
      ]
    },
    {
      id: "caracter", name: "Caracter nou: de la fișă la lansare", area: "Caractere", time: "2–3 săptămâni",
      steps: [
        ["Fișa: aspect, stil, voce, reguli", "Claude", "fișa standard", "1 h"],
        ["40 de fețe, alegi una", "Tu", "Krea 2 / Nano Banana", "2 h"],
        ["Corpul de referință", "Tu", "4 imagini, corp întreg", "1 h"],
        ["Setul de antrenare: 34 de poze", "Tu", "12 față + 10 studio + 12 insta", "6–8 h"],
        ["Captions", "Claude", "doar părțile care variază", "30 min"],
        ["LoRA pentru imagini", "Agentul de pe pod", "AI Toolkit, 3.000 de pași", "3–4 h GPU"],
        ["Testul de realism", "Tu", "workflow-ul de realism", "1 h"],
        ["Vocea", "Tu", "ElevenLabs Voice Design", "30 min"],
        ["LoRA video (când e nevoie)", "Agentul de pe pod", "Wan 2.1 14B", "o zi GPU"],
        ["Conturile, etichetate AI", "Tu", "Instagram, TikTok", "1 h"],
        ["9 postări gata, apoi lansarea", "Tu + Claude", "skill-urile de conținut", "2 zile"]
      ]
    },
    {
      id: "nisa", name: "Testul unei nișe", area: "Vânzări", time: "3 săptămâni",
      steps: [
        ["Profilul clientului ideal", "Claude", "fișa nișei", "săpt. 1"],
        ["Lista de 30 de firme", "Tu", "tabelul de vânzări", "săpt. 1"],
        ["5 mostre pe produsele lor", "Tu", "linia de producție", "săpt. 1"],
        ["Mesajele și revenirile", "Tu", "Anexa A", "săpt. 2"],
        ["Apelurile și piloții", "Tu", "skill-ul sales-call", "săpt. 3"],
        ["Decizia: ≥15% răspunsuri, ≥3 apeluri, ≥1 pilot plătit", "Tu + Claude", "jurnalul", "săpt. 3"]
      ]
    },
    {
      id: "postare", name: "Postarea zilnică", area: "Conținut", time: "20 min / zi",
      steps: [
        ["Verifici postarea programată și eticheta AI", "Tu", "Meta Business Suite", "2 min"],
        ["1–3 stories: din culise, sondaj, întrebare", "Tu", "Instagram", "5 min"],
        ["Răspunzi la toate comentariile și mesajele", "Tu", "Instagram, TikTok", "10 min"],
        ["5 comentarii utile la conturi din nișă", "Tu", "Instagram", "5 min"],
        ["Notezi cifrele zilei", "Tu", "tabelul de rezultate", "2 min"]
      ]
    },
    {
      id: "raport", name: "Raportul lunar pentru client", area: "Clienți", time: "1 h",
      steps: [
        ["Exporți statisticile lunii", "Tu", "Meta Business Suite", "10 min"],
        ["Top 3 postări și cifrele principale", "Claude", "skill-ul stats-report", "15 min"],
        ["Ce am învățat: hook-uri, formate, ore", "Claude", "tabelul de rezultate", "10 min"],
        ["Ce schimbăm luna viitoare", "Tu + Claude", "raportul", "15 min"],
        ["Recomandarea (doar dacă rezolvă o problemă reală)", "Tu", "skill-ul money-model", "10 min"]
      ]
    },
    {
      id: "conformitate", name: "Conformitate, la fiecare livrabil", area: "Legal", time: "5 min",
      steps: [
        ["Eticheta AI pregătită", "Tu", "„AI info” / eticheta TikTok", "1 min"],
        ["#ad sau „Paid partnership” la colaborări plătite", "Tu", "Instagram", "1 min"],
        ["Acord scris pentru orice față reală", "Tu", "registrul de acorduri", "la nevoie"],
        ["Muzică licențiată", "Tu", "biblioteca platformei", "1 min"],
        ["Fără promisiuni medicale sau de rezultat", "Tu", "lista de verificare", "1 min"],
        ["Marcaj în fișier (C2PA)", "Platforma", "faza 2", "automat"]
      ]
    },
    {
      id: "pod", name: "Rutina pe pod (GPU)", area: "Tehnic", time: "5 min + lucrul",
      steps: [
        ["Pornești podul L40S pe RunPod", "Tu", "volumul de 250 GB", "2 min"],
        ["Rulezi porneste.sh și copiezi Bridge URL-ul", "Tu", "/workspace/porneste.sh", "1 min"],
        ["Primul mesaj către agent", "Tu", "„Read /workspace/persist/DARIA_CONTEXT.md, the pod restarted, continue.”", "1 min"],
        ["Lucrezi în loturi: tot ce ai de generat azi", "Tu + agentul", "workflow-urile ComfyUI", "1–3 h"],
        ["Mesajul de final: agentul actualizează contextul", "Agentul", "DARIA_CONTEXT.md", "2 min"],
        ["Oprești podul imediat", "Tu", "RunPod", "1 min"]
      ]
    },
    {
      id: "recenzie", name: "Recenzia săptămânală", area: "Plan", time: "30 min",
      steps: [
        ["Cifrele săptămânii", "Tu", "tabelul de rezultate", "10 min"],
        ["Ce a mers și ce nu", "Tu + Claude", "jurnalul", "10 min"],
        ["O singură schimbare pentru săptămâna viitoare", "Tu", "planul", "5 min"],
        ["Notezi în plan/JURNAL.md", "Claude", "repo-ul", "5 min"]
      ]
    }
  ],

  /* ---------------- Platforma ---------------- */
  modules: [
    { id: "character", name: "Character Studio", job: "Creezi și ții minte caracterele: fișă, LoRA, voce, acorduri.", f1: "Fișe și bibliotecă de caractere", f2: "Creare rapidă din referințe, cu acord pentru fețe reale", f3: "LoRA la cerere, marketplace de caractere" },
    { id: "brain", name: "Content Brain", job: "Idei, hook-uri, scripturi și texte, cu skill-urile noastre.", f1: "Pentru echipa noastră", f2: "Pentru clienți", f3: "Agenți care lucrează după calendar" },
    { id: "i2p", name: "Image-to-Prompt", job: "Urci o imagine care îți place și primești promptul.", f1: "Intern", f2: "Unealtă gratuită pe site", f3: "Prompturi după performanță" },
    { id: "gen", name: "Generare", job: "Workflow-urile ComfyUI, dintr-un click, pe GPU la cerere.", f1: "Imagini dintr-un click", f2: "Pe credite", f3: "Alege automat cel mai bun model" },
    { id: "edit", name: "Editare automată", job: "Reels montate automat: tăieturi, subtitrări, text, muzică.", f1: "Șabloane de reels", f2: "Șabloane pentru clienți", f3: "Editare după ce a mers" },
    { id: "publish", name: "Publicare și ore", job: "Programezi postările la orele care merg pentru contul tău.", f1: "Programare (după aprobarea Meta)", f2: "Pentru clienți", f3: "Ore din datele fiecărui cont" },
    { id: "learn", name: "Rezultate și învățare", job: "Fiecare postare e etichetată și măsurată. Recomandările se îmbunătățesc cu fiecare client.", f1: "Tabelul de rezultate + raport", f2: "Panou de rezultate pentru client", f3: "Recomandări din date agregate, anonimizate" },
    { id: "comply", name: "Conformitate", job: "Etichete AI, marcaj în fișier, acorduri, filtre de conținut.", f1: "Etichete AI", f2: "C2PA, acorduri, filtre", f3: "Audit automat" }
  ],

  phases: [
    ["F0", "Acum", "Unelte manuale, skill-uri și pod. Validăm pe bani reali."],
    ["F1", "Lunile 3–6", "Unealta internă: automatizăm munca noastră pentru clienți."],
    ["F2", "Lunile 6–12", "Beta pentru clienți: self-serve, pe credite."],
    ["F3", "După 12 luni", "Învățare pe multe date, API, marketplace de caractere, alte limbi."]
  ],

  /* ---------------- Date demonstrative pentru Studio ---------------- */
  demo: {
    kpis: [
      ["Postări programate", "5", "săptămâna asta"],
      ["Livrabile în lucru", "7", "2 la verificare"],
      ["Mostre trimise", "5 / 5", "nișa magazine online"],
      ["Ore GPU", "18 / 40", "luna asta"]
    ],
    today: [
      ["09:00", "Lotul de imagini al săptămânii", "Producție", "doing"],
      ["10:30", "Mostra 3: brandul de bijuterii", "Producție", "todo"],
      ["14:00", "Mesaje: firmele 13–18", "Vânzări", "todo"],
      ["19:00", "Postarea zilei + 15 min răspunsuri", "Conținut", "todo"]
    ],
    board: [
      ["Brief", [["Rochie satin, brand 2", "Daria"], ["Pensiune Bran", "Ilinca"]]],
      ["Producție", [["Mostra 3: cercei", "Daria"], ["Reel lansare", "Daria"], ["Carusel „3 piese”", "Daria"]]],
      ["Verificare", [["Mostra 1: geantă", "Daria"], ["Mostra 2: rochie", "Daria"]]],
      ["Livrat", [["9 postări de lansare", "Daria"]]]
    ],
    alerts: [
      ["LoRA v2 Daria: antrenare la pasul 1.900 din 3.000", "ok"],
      ["2 imagini trebuie refăcute: mâinile", "warn"],
      ["2 livrabile așteaptă verificarea", "warn"]
    ],
    calendar: [
      { day: 0, time: "19:00", type: "Reel", title: "3 piese care fac orice ținută să pară scumpă", status: "programat" },
      { day: 1, time: "12:30", type: "Carusel", title: "Ce port la o cină de lucru (5 slide-uri)", status: "programat" },
      { day: 3, time: "19:00", type: "Reel", title: "#ad · rochia de satin, brand românesc", status: "draft" },
      { day: 4, time: "19:00", type: "Foto", title: "Rooftop, ora de aur", status: "draft" },
      { day: 5, time: "11:00", type: "Reel", title: "Sunt AI. Uite cum se face o ședință foto", status: "idee" }
    ],
    heatHours: ["08", "10", "12", "14", "16", "18", "20", "22"],
    heat: [
      [18, 31, 58, 36, 30, 61, 84, 52],
      [20, 33, 62, 38, 32, 64, 88, 55],
      [17, 29, 55, 35, 31, 60, 80, 50],
      [21, 35, 64, 40, 34, 66, 92, 58],
      [19, 30, 52, 37, 36, 58, 76, 63],
      [12, 41, 57, 49, 45, 54, 66, 59],
      [10, 38, 61, 52, 47, 59, 71, 44]
    ],
    posts: [
      ["Reel", "Întrebare", "Lu 19:00", 12400, 61, 410, 88],
      ["Carusel", "Listă", "Ma 12:30", 8300, 0, 520, 41],
      ["Reel", "Contrast", "Jo 19:00", 15800, 68, 380, 133],
      ["Foto", "—", "Vi 19:00", 5100, 0, 96, 12],
      ["Reel", "Din culise", "Sâ 11:00", 9700, 54, 210, 64],
      ["Reel", "Listă", "Lu 19:00", 11200, 58, 455, 70],
      ["Carusel", "Întrebare", "Ma 12:30", 7600, 0, 488, 35],
      ["Reel", "Contrast", "Jo 20:00", 17900, 71, 402, 151]
    ],
    insights: [
      "Reels-urile cu hook de contrast („Nu sunt reală. Ținuta asta e.”) au cea mai mare vizionare medie.",
      "Caruselele aduc cele mai multe salvări. Le păstrăm pentru sfaturi.",
      "Joi seara e cea mai bună fereastră. Mutăm colaborările acolo."
    ],
    consents: [
      ["Daria", "Personaj fictiv", "Nu e nevoie de acord", "ok"],
      ["Filmarea fondatorului (test SCAIL-2)", "Persoană reală, propria filmare", "Acord semnat", "ok"],
      ["Clientul X: chipul managerului", "Persoană reală", "Acord lipsă: nu se folosește", "bad"]
    ],
    ideas: [
      { titlu: "Ținuta de 300 de lei care arată de 3.000", hook: "Bugetul a fost 300 de lei. Arată de 3.000.", cadre: ["Daria în oglindă, ținuta completă", "Prim-plan pe rochia de satin și cercei", "Mers spre cameră, zâmbet"], text_pe_ecran: "300 lei · 3 piese", caption: "Trei piese, un singur buget. Pe care ai purta-o prima? Linkurile sunt în bio. #ad", ora: "19:00", de_ce: "Contrastul preț–aspect ține privirea primele 2 secunde." },
      { titlu: "Sunt AI. Ținuta e reală.", hook: "Nu sunt reală. Ținuta asta e.", cadre: ["Daria se întoarce spre cameră", "Produsul în mână, prim-plan", "Eticheta brandului, clar"], text_pe_ecran: "AI creator · produs real", caption: "Eu sunt generată cu AI. Rochia o găsești la brandul din tag. Ce culoare ai alege?", ora: "19:00", de_ce: "Transparența devine hook și construiește încredere." },
      { titlu: "3 detalii care fac diferența", hook: "Dacă porți negru tot timpul, salvează asta.", cadre: ["Ținută neagră simplă", "Adaugă cercei aurii", "Adaugă blazer bej, rezultatul"], text_pe_ecran: "1 · 2 · 3", caption: "Același negru, trei detalii. Salvează pentru weekend.", ora: "12:30", de_ce: "Format de listă: aduce salvări." }
    ],
    examplePrompt: {
      prompt: "d4ria, sitting at a small marble cafe table by a large window, morning light, holding a latte in both hands, beige knit cardigan over a white t-shirt, laughing and looking slightly off-camera, people softly blurred in the background, shot on a smartphone at eye level, 26mm lens, natural colors, light film grain, candid lifestyle photo",
      negative: "tattoo, text, watermark, extra fingers, plastic skin, studio lighting",
      setari: "4:5 vertical · Krea 2 Turbo + LoRA d4ria, apoi realism (Z-Image 0.25)",
      note: "Exemplu: așa arată rezultatul pentru o poză de cafenea."
    }
  }
};
