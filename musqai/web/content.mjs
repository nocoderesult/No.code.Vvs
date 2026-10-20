/* Conținutul site-ului MUSQAI. Tot ce se schimbă pe parcurs (caractere, prețuri, procese) se editează aici,
   apoi se rulează: node musqai/web/build.mjs */

export const brand = {
  name: "MUSQAI",
  full: "Marketing Universe Studio · Quantum AI",
  url: "https://musqai.com",
  email: "contact@musqai.com",
  instagram: "@musqai"
};

export const characters = [
  {
    id: "iness",
    name: "Iness",
    age: 25,
    role: "Ambasadoare lifestyle & lux",
    archetype: "Fata care știe locurile bune",
    status: "live",
    statusLabel: "Prima ambasadoare MUSQAI",
    photo: { main: "/assets/img/iness-960", card: "/assets/img/iness-600.webp", face: "/assets/img/iness-fata.webp" },
    palette: ["#1a0f14", "#5b1f3a", "#ff8a6b"],
    comp: [
      ["Vârstă", "25"],
      ["Păr", "Negru, drept, bob la maxilar, cărare pe mijloc"],
      ["Ochi", "Verde-alune"],
      ["Ten", "Bronzat cald, pistrui fini"],
      ["Semne", "Cercei rotunzi argintii · fără tatuaje"],
      ["Stil", "Minimalist luxos"]
    ],
    summary: "Iness arată produse de modă, bijuterii și locuri premium ca o prietenă cu gust bun. Calmă, încrezătoare, cu umor fin. Spune deschis că e AI.",
    look: "Păr negru-corb, drept, tuns bob la nivelul maxilarului, cu cărare pe mijloc. Ochi verde-alune, gene dese, sprâncene groase și naturale. Ten bronzat cald, cu pistrui fini pe nas și pe pomeți. Buze pline, nude. Cercei rotunzi argintii. Fără tatuaje.",
    style: "Minimalist luxos: satin champagne, negru, alb, blazer bej, trench. Accesorii fine. Machiaj natural ziua, mai intens seara.",
    personality: ["încrezătoare", "caldă", "ironică fin", "atentă la detalii"],
    voice: "Română naturală, caldă, ușor joasă. Ritm calm, zâmbet în voce, dicție clară.",
    niches: ["Modă, bijuterii, accesorii", "Turism premium", "Evenimente", "HoReCa premium"],
    pillars: [
      ["Ținute și detalii", 30, "3 piese care fac orice ținută să pară scumpă"],
      ["Locuri și experiențe", 25, "Cel mai fotogenic rooftop din oraș"],
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
        "Produsul arătat exact ca în realitate, după pozele brandului",
        "#ad sau „Paid partnership” la colaborările plătite",
        "Același aspect în fiecare imagine"
      ],
      dont: [
        "Nu spune că a cumpărat sau a folosit produsul ca o persoană reală",
        "Fără nuditate și fără conținut sexual",
        "Fără promisiuni de sănătate sau de rezultat corporal",
        "Nu apare lângă minori și nu face conținut politic"
      ]
    },
    schedule: "5 postări pe săptămână, seara · stories zilnic",
    platforms: ["Instagram", "TikTok"],
    handle: "@iness.musqai",
    imageStyle: "a 25-year-old woman with warm tan skin and light freckles, a sleek straight jet-black jaw-length bob with a center part, green-hazel eyes, thick natural eyebrows, silver hoop earrings",
    pipeline: [
      ["Fișa personajului", "done"],
      ["Fața și corpul de referință", "done"],
      ["Primul model al feței (LoRA v1)", "done"],
      ["Setul nou de antrenare: 34 de poze", "doing"],
      ["Modelul final + testul de realism", "todo"],
      ["Vocea", "todo"],
      ["Conturile de Instagram și TikTok", "todo"],
      ["Modelul pentru video", "todo"]
    ]
  },
  {
    id: "matei",
    name: "Matei",
    age: 33,
    role: "Ambasador business & imobiliare",
    archetype: "Consultantul pe care îl suni",
    status: "casting",
    statusLabel: "În casting · din decembrie",
    palette: ["#0c1424", "#24456f", "#8fb4e6"],
    comp: [
      ["Vârstă", "33"],
      ["Păr", "Șaten-închis, scurt, cu cărare laterală"],
      ["Ochi", "Căprui-închis"],
      ["Ten", "Deschis-măsliniu"],
      ["Semne", "Barbă scurtă îngrijită · ceas metalic"],
      ["Stil", "Smart casual"]
    ],
    summary: "Matei prezintă proprietăți, mașini și servicii ca un om de încredere. Direct, calm, fără vorbe goale.",
    look: "Păr șaten-închis, scurt, cu cărare laterală. Barbă scurtă, îngrijită. Ochi căprui-închis, maxilar definit. Ten deschis-măsliniu. Siluetă atletic-zveltă. Ceas metalic discret.",
    style: "Smart casual: cămăși albe și bleu, sacou navy, pulover de merinos, pantofi maro. Fără logo-uri mari.",
    personality: ["calm", "de încredere", "direct", "atent la cifre"],
    voice: "Baritonală caldă, ritm măsurat, clar. Sună ca un consultant bun, nu ca un vânzător.",
    niches: ["Imobiliare", "Auto", "Servicii B2B", "Modă masculină"],
    pillars: [
      ["Tururi de proprietăți", 35, "Apartamentul ăsta are o cameră pe care n-o vezi în anunț"],
      ["Piața pe scurt", 25, "Prețurile din cartierul tău, luna asta, în 30 de secunde"],
      ["Sfaturi de cumpărare", 25, "5 întrebări pe care să le pui la vizionare"],
      ["Viața de business", 15, "O zi de lucru, de la 7 la 7"]
    ],
    hooks: ["Nu cumpăra apartament până nu verifici asta.", "Am întrebat un dezvoltator ce nu scrie în broșură.", "Diferența de preț dintre etajul 2 și 8, explicată."],
    rules: {
      do: ["Proprietatea e filmată real; Matei e doar prezentatorul", "Cifrele vin de la client sau din surse publice", "Eticheta AI la fiecare video"],
      dont: ["Nu inventează finisaje, priveliști sau dotări", "Nu dă sfaturi financiare personalizate", "Nu promite randamente"]
    },
    schedule: "3 video-uri pe săptămână",
    platforms: ["Instagram", "LinkedIn", "YouTube Shorts"],
    handle: "@matei.musqai",
    imageStyle: "a 33-year-old man with light olive skin, short dark-brown side-parted hair, a short well-groomed beard, deep brown eyes, a minimalist steel watch",
    pipeline: [["Fișa personajului", "done"], ["Fața aleasă din 40 de variante", "todo"], ["Setul de antrenare", "todo"], ["Modelul feței (LoRA)", "todo"], ["Vocea", "todo"], ["Conturile", "todo"]]
  },
  {
    id: "ilinca",
    name: "Ilinca",
    age: 29,
    role: "Exploratoare: travel & food",
    archetype: "Prietena care găsește mereu locul",
    status: "casting",
    statusLabel: "În casting · din ianuarie",
    palette: ["#1f0f08", "#8a4320", "#ffc28f"],
    comp: [
      ["Vârstă", "29"],
      ["Păr", "Castaniu-arămiu, lung, ondulat"],
      ["Ochi", "Căprui-verzi"],
      ["Ten", "Deschis cald, pistrui fini"],
      ["Semne", "Zâmbet larg · pălărie de paie"],
      ["Stil", "Natural, de călătorie"]
    ],
    summary: "Ilinca descoperă hoteluri, pensiuni și restaurante. Curioasă, spontană, povestește ca o prietenă care tocmai s-a întors din vacanță.",
    look: "Păr castaniu-arămiu, lung, ondulat, des prins într-un coc lejer. Ochi căprui-verzi, pistrui fini pe nas. Ten deschis cald. Zâmbet larg. Siluetă zveltă.",
    style: "In natural, cămăși oversize, pălărie de paie, sneakers albi, rucsac mic. Culori de pământ.",
    personality: ["curioasă", "spontană", "caldă", "bună povestitoare"],
    voice: "Luminoasă și energică, ușor răgușită. Vorbește repede când e entuziasmată.",
    niches: ["Hoteluri boutique și pensiuni", "Restaurante și cafenele", "Experiențe și tururi"],
    pillars: [
      ["Weekend în…", 35, "48 de ore în Sibiu, fără să stai la coadă"],
      ["Ce comand aici", 25, "Trei feluri pe care nu le ratezi la locul ăsta"],
      ["Locuri ascunse", 25, "Pensiunea cu 9 camere pe care n-o găsești pe prima pagină"],
      ["Ghid de sezon", 15, "Unde mergi în decembrie dacă nu vrei aglomerație"]
    ],
    hooks: ["Locul ăsta are 9 camere și e plin până în martie.", "Am venit pentru priveliște. Am rămas pentru micul-dejun.", "Nu-ți spun unde e. Ba da, îți spun."],
    rules: {
      do: ["Ambasador AI declarat, nu oaspete real", "Imaginile locației sunt reale, de la client", "Eticheta AI la fiecare postare"],
      dont: ["Nu scrie recenzii și nu dă note", "Nu inventează facilități sau priveliști", "Nu promovează consumul excesiv de alcool"]
    },
    schedule: "4 postări pe săptămână",
    platforms: ["Instagram", "TikTok"],
    handle: "@ilinca.musqai",
    imageStyle: "a 29-year-old woman with fair warm skin and light freckles, long wavy copper-brown hair in a loose low bun, hazel-brown eyes, a wide genuine smile",
    pipeline: [["Fișa personajului", "done"], ["Fața aleasă din 40 de variante", "todo"], ["Setul de antrenare", "todo"], ["Modelul feței (LoRA)", "todo"], ["Vocea", "todo"], ["Conturile", "todo"]]
  },
  {
    id: "ioana",
    name: "Ioana",
    age: 27,
    role: "Produse de zi cu zi",
    archetype: "Omul practic din grupul de prieteni",
    status: "planned",
    statusLabel: "Planificat",
    palette: ["#16131f", "#4c3f78", "#d7c8ff"],
    comp: [
      ["Vârstă", "27"],
      ["Păr", "Blond-închis, până la umeri, coc lejer"],
      ["Ochi", "Albaștri-cenușii"],
      ["Ten", "Deschis, natural"],
      ["Semne", "Machiaj aproape absent"],
      ["Stil", "Comod, de acasă"]
    ],
    summary: "Ioana arată cum se folosesc lucrurile de zi cu zi, acasă, în bucătărie sau în mașină. Sinceră, amuzantă, practică.",
    look: "Păr blond-închis până la umeri, des prins într-un coc lejer. Ochi albaștri-cenușii. Ten deschis, natural, machiaj discret. Înălțime medie. Față relaxată, prietenoasă.",
    style: "Hanorace, tricouri simple, blugi, pijamale comode. Decoruri reale: casă, bucătărie, mașină.",
    personality: ["sinceră", "amuzantă", "practică", "directă"],
    voice: "Naturală, conversațională, ritm alert. Sună ca un mesaj vocal de la o prietenă.",
    niches: ["Magazine online mass-market", "Casă și decor", "Produse de zi cu zi", "Aplicații"],
    pillars: [
      ["Prima impresie", 35, "Am deschis cutia. Uite ce e înăuntru"],
      ["Cum se folosește", 30, "Trei feluri de a folosi asta în bucătărie"],
      ["Trucuri pentru casă", 20, "Dulapul meu, organizat în 10 minute"],
      ["O zi obișnuită", 15, "Ce fac luni la 7 dimineața"]
    ],
    hooks: ["Nimeni nu mi-a spus că se poate face și așa.", "Trei lucruri din bucătărie pe care le folosesc zilnic.", "Dacă ai un balcon mic, uite."],
    rules: {
      do: ["Demonstrație de produs făcută de un ambasador AI declarat", "Arată ce face produsul, cu imagini reale de la brand", "Eticheta AI la fiecare postare"],
      dont: ["Nu spune „l-am cumpărat” sau „îl folosesc de 3 luni”", "Nu face „recenzii” și nu dă stele", "Nu compară cu produse concurente pe nume"]
    },
    schedule: "5 clipuri pe săptămână, 9:16",
    platforms: ["TikTok", "Instagram"],
    handle: "@ioana.musqai",
    imageStyle: "a 27-year-old woman with fair natural skin, shoulder-length dark-blonde hair in a messy bun, grey-blue eyes, light natural makeup, a relaxed friendly face",
    pipeline: [["Fișa personajului", "done"], ["Fața aleasă din 40 de variante", "todo"], ["Setul de antrenare", "todo"], ["Modelul feței (LoRA)", "todo"], ["Vocea", "todo"], ["Conturile", "todo"]]
  },
  {
    id: "mira",
    name: "Mira",
    age: 30,
    role: "Fața platformei MUSQAI",
    archetype: "Explică AI-ul ca pe o rețetă",
    status: "planned",
    statusLabel: "Planificat",
    palette: ["#071a16", "#17644f", "#8ff0cf"],
    comp: [
      ["Vârstă", "30"],
      ["Păr", "Șaten-închis, lung, drept, cu breton"],
      ["Ochi", "Căprui-închis"],
      ["Ten", "Măsliniu cald"],
      ["Semne", "Ochelari rotunzi cu ramă subțire"],
      ["Stil", "Minimalist tech"]
    ],
    summary: "Mira explică pe scurt cum folosesc afacerile AI-ul și arată ce se întâmplă în culisele MUSQAI. Clară, calmă, cu umor sec.",
    look: "Păr șaten-închis, lung, drept, cu breton drept. Ochi căprui-închis. Ten măsliniu cald. Ochelari rotunzi cu ramă subțire. Siluetă zveltă.",
    style: "Minimalist tech: negru, gri și un singur accent colorat. Cămăși structurate, pulovere fine.",
    personality: ["clară", "calmă", "deșteaptă", "umor sec"],
    voice: "Clară, registru mediu, profesională și prietenoasă. Pauze scurte înainte de ideile importante.",
    niches: ["Promovarea MUSQAI", "Educație AI pentru afaceri"],
    pillars: [
      ["AI pentru afaceri în 60 de secunde", 40, "Cum faci 30 de poze de produs fără ședință foto"],
      ["Din culisele MUSQAI", 30, "Așa arată o zi în studio"],
      ["Studii de caz (cu acordul clientului)", 20, "Ce s-a schimbat după 30 de zile"],
      ["Știri AI pe scurt", 10, "Ce a apărut săptămâna asta și ce înseamnă pentru tine"]
    ],
    hooks: ["Ai un magazin online? Asta te costă mai puțin decât crezi.", "Sunt AI și îți explic de ce contează eticheta asta.", "Ce nu-ți spune nimeni despre reclamele cu AI."],
    rules: {
      do: ["Explică simplu, cu exemple reale", "Studiile de caz doar cu acord scris", "Eticheta AI la fiecare postare"],
      dont: ["Fără promisiuni de venit", "Fără atacuri la concurenți", "Fără cifre neverificate"]
    },
    schedule: "3 postări pe săptămână",
    platforms: ["LinkedIn", "TikTok", "YouTube Shorts"],
    handle: "@mira.musqai",
    imageStyle: "a 30-year-old woman with warm olive skin, long straight dark-brown hair with blunt bangs, dark brown eyes, thin-framed round glasses, minimalist black clothing",
    pipeline: [["Fișa personajului", "done"], ["Fața aleasă din 40 de variante", "todo"], ["Setul de antrenare", "todo"], ["Modelul feței (LoRA)", "todo"], ["Vocea", "todo"], ["Conturile", "todo"]]
  }
];

export const niches = [
  {
    id: "n1", code: "01", name: "Magazine online", avail: "Disponibil acum",
    who: "Branduri românești de modă, accesorii, bijuterii și decor, cu magazin online, care rulează deja reclame.",
    pain: "Reclamele se uzează repede, ședințele foto sunt scumpe și nu au o față constantă.",
    deliver: ["Poze lifestyle cu produsul pe ambasador", "Reels de 8–15 s pentru reclame și organic", "Variante de hook pentru test A/B", "Textele, în română"],
    rules: ["Produsul identic cu realitatea, după pozele brandului", "Ambasador AI declarat, nu „clientă”", "Eticheta AI la fiecare postare"],
    metric: "CTR și ROAS față de reclamele vechi · costul pe creativ",
    character: "iness"
  },
  {
    id: "n2", code: "02", name: "Imobiliare", avail: "Din decembrie",
    who: "Dezvoltatori premium și agenții de top.",
    pain: "Fac puțin video, producția e scumpă, iar ansamblurile sunt greu de „vândut” emoțional.",
    deliver: ["Prezentator AI în video cu proprietatea filmată real", "„O zi în viața ta aici”", "Noutăți de piață săptămânale"],
    rules: ["Nu inventăm finisaje, priveliști sau dotări", "Cifrele vin de la client", "Eticheta AI"],
    metric: "Cereri de vizionare · lead-uri",
    character: "matei"
  },
  {
    id: "n3", code: "03", name: "Turism și HoReCa", avail: "Din ianuarie",
    who: "Hoteluri boutique, pensiuni premium, rooftop-uri, spa-uri, restaurante.",
    pain: "Conținutul e sezonier, fotografii sunt scumpi, iar atmosfera e greu de prins.",
    deliver: ["Ambasadorul „descoperă” locul, pe imagini reale ale locației", "Reels de atmosferă", "Ghiduri de sezon"],
    rules: ["Ambasador AI declarat, nu oaspete real", "Fără recenzii false", "Fără facilități inventate"],
    metric: "Rezervări și mesaje venite din Instagram",
    character: "ilinca"
  },
  {
    id: "n4", code: "04", name: "Evenimente și nightlife", avail: "În curând",
    who: "Cluburi, organizatori de evenimente, festivaluri mici.",
    pain: "Promovarea începe târziu și arată la fel de la un eveniment la altul.",
    deliver: ["Teasere și numărători inverse", "Anunțuri de line-up", "Recapitulări după eveniment"],
    rules: ["Regulile de reclamă pentru alcool", "Fără minori", "Eticheta AI"],
    metric: "Bilete vândute · înscrieri",
    character: "iness"
  },
  {
    id: "n5", code: "05", name: "Wellness și cosmetice", avail: "În curând",
    who: "Studiouri de fitness, spa-uri, branduri de cosmetice.",
    pain: "Conținutul trebuie să fie frumos, dar fără să promită rezultate.",
    deliver: ["Prezentarea produsului sau a serviciului", "Atmosfera locului", "Educație fără promisiuni"],
    rules: ["Fără înainte/după", "Fără promisiuni medicale sau de rezultat corporal", "Un corp generat nu e prezentat ca rezultat"],
    metric: "Programări · mesaje",
    character: "ioana"
  }
];

export const offers = {
  small: { name: "5 creative AI", price: "99 €", note: "Testul", items: ["5 imagini cu produsul tău pe un ambasador AI", "Format pentru reclame: 4:5 și 9:16", "Gata în 5 zile lucrătoare"] },
  full: { name: "Lansarea completă", price: "490 €", note: "Recomandat", items: ["Ambasador AI dedicat campaniei", "12 creative: poze și reels", "Variante de hook pentru test A/B", "Textele reclamelor", "Raport după 14 zile"] },
  guarantee: "Dacă ne trimiți materialele în 48 de ore, rulezi creativele cel puțin 14 zile și ne dai cifrele, toată suma plătită se scade din abonamentul pe 6 luni.",
  prepay: "Plătești 5 luni în avans, a 6-a e gratuită."
};

export const packages = [
  { name: "Start", price: "350 €", note: "Pentru primul ambasador", items: ["8 poze", "4 reels", "Textele, în română", "Calendarul de postare"] },
  { name: "Growth", price: "700 €", note: "Pentru branduri care rulează reclame", items: ["12 poze", "8 reels", "Variante pentru reclame (A/B)", "Raport lunar", "Tot din Start"], featured: true },
  { name: "Pro", price: "de la 1.200 €", note: "Un caracter doar al tău", items: ["Caracter dedicat, exclusiv pe nișa ta", "Voce proprie", "Strategie lunară", "Tot din Growth"] }
];

export const extras = [
  ["Caracter exclusiv", "Îl creăm o dată, apoi îl folosești doar tu."],
  ["Voce și sincronizarea buzelor", "Ambasadorul vorbește în română."],
  ["Alte limbi", "Aceleași clipuri, dublate."],
  ["Automatizare DM", "Răspunsuri la mesajele venite din reclame."]
];

export const faq = [
  ["E legal să folosesc un ambasador AI?", "Da, dacă e etichetat corect. Din 2 august 2026, în UE, conținutul generat cu AI care pare real trebuie marcat (AI Act, articolul 50). Noi etichetăm fiecare postare, iar imaginile din zonele de generare primesc și un marcaj în fișier."],
  ["Oamenii vor ști că e AI?", "Da. Ambasadorul are „AI creator” în bio, iar fiecare postare are eticheta AI. Produsul e real și arată exact ca în magazin."],
  ["Produsul meu va arăta exact ca în realitate?", "Lucrăm după pozele voastre. Nu schimbăm culoarea, forma, logo-ul sau textul de pe produs, iar fiecare livrabil trece printr-o verificare înainte să-l primiți."],
  ["Pot avea un caracter doar al meu?", "Da. În pachetul Pro creăm un caracter exclusiv pentru nișa ta, cu voce proprie. Caracterele casei, ca Iness, rămân ale MUSQAI."],
  ["Cât durează până primesc primele materiale?", "Mostra o primești în 3–5 zile lucrătoare de la brief. În abonament, livrăm săptămânal."],
  ["Ce se întâmplă dacă nu-mi place?", "Ai două runde de revizii la fiecare livrabil. Abonamentul se anulează cu o lună înainte, iar condițiile sunt scrise în contract."],
  ["Folosiți fețe de oameni reali?", "Doar cu acordul scris al persoanei și după verificare. Nu facem niciodată conținut cu fețe reale fără acord."]
];

export const steps = [
  ["Brief", "Produsul, publicul, tonul, obiectivul și ce nu vrei. Un formular de 15 minute."],
  ["Idei și scripturi", "Hook-uri, scenarii și texte, scrise pe vocea ambasadorului."],
  ["Imagini", "Ambasadorul cu produsul tău, după pozele tale."],
  ["Video", "Clipuri din imagini sau ambasadorul pus în filmări reale."],
  ["Voce", "Vocea ambasadorului, sincronizată cu buzele."],
  ["Editare", "Tăieturi pe ritm, subtitrări în română, text pe ecran, muzică licențiată."],
  ["Verificare", "Fața, mâinile, produsul, eticheta AI, formatul. Nimic nu pleacă nebifat."],
  ["Livrare și programare", "Fișierele în folderul tău și postările programate la orele bune."],
  ["Raport", "Ce a mers, ce am învățat, ce schimbăm luna viitoare."]
];

export const timeline = [
  ["Ziua 0", "Apel de 15 minute și brief-ul."],
  ["Ziua 1–2", "Ideile și planul pe 30 de zile, trimise spre aprobare."],
  ["Ziua 3–5", "Primele livrabile: poze și reels."],
  ["Ziua 7", "Postările programate. Prima săptămână live."],
  ["Ziua 14", "Primele cifre și ajustările."],
  ["Ziua 30", "Raportul lunar și planul pentru luna următoare."]
];

export const clientGives = ["Pozele reale ale produselor sau ale locației", "Logo-ul și culorile", "Ce vrei să vinzi luna asta", "Accesul la statistici (opțional, pentru raport)"];

export const processes = [
  { name: "Livrabil nou: de la brief la postare", time: "1–3 zile", steps: [["Brief-ul clientului", "15 min"], ["Idei, hook-uri, scripturi", "30 min"], ["Imaginile", "10–20 min / poză"], ["Clipurile video", "45–90 min / reel"], ["Vocea și buzele", "20 min"], ["Editarea", "30 min / reel"], ["Verificarea calității", "10 min"], ["Livrarea și programarea", "15 min"]] },
  { name: "Clientul nou: primele 14 zile", time: "14 zile", steps: [["Contractul și factura", "ziua 0"], ["Materialele clientului", "ziua 1–2"], ["Apelul de pornire", "ziua 2"], ["Planul pe 30 de zile", "ziua 2"], ["Primele livrabile", "ziua 3–5"], ["Postările programate", "ziua 7"], ["Primele cifre și ajustări", "ziua 14"]] },
  { name: "Caracter nou: de la fișă la lansare", time: "2–3 săptămâni", steps: [["Fișa: aspect, stil, voce, reguli", "1 h"], ["40 de fețe, alegi una", "2 h"], ["Corpul de referință", "1 h"], ["Setul de antrenare: 34 de poze", "6–8 h"], ["Modelul feței (LoRA)", "3–4 h"], ["Testul de realism", "1 h"], ["Vocea", "30 min"], ["Conturile, etichetate AI", "1 h"], ["9 postări gata, apoi lansarea", "2 zile"]] },
  { name: "Conformitate, la fiecare livrabil", time: "5 min", steps: [["Eticheta AI pregătită", "1 min"], ["#ad sau „Paid partnership” la colaborări", "1 min"], ["Acord scris pentru orice față reală", "la nevoie"], ["Muzică licențiată", "1 min"], ["Fără promisiuni medicale sau de rezultat", "1 min"], ["Marcaj în fișier", "automat"]] },
  { name: "Raportul lunar pentru client", time: "1 h", steps: [["Statisticile lunii", "10 min"], ["Top 3 postări și cifrele principale", "15 min"], ["Ce am învățat: hook-uri, formate, ore", "10 min"], ["Ce schimbăm luna viitoare", "15 min"], ["Recomandarea, doar dacă rezolvă o problemă reală", "10 min"]] }
];

export const zones = [
  { id: "idei", name: "Idei de conținut", short: "Hook-uri, cadre și texte pentru reels, gata de filmat.", icon: "spark" },
  { id: "imagine", name: "Imagine din text", short: "Scrii ideea în română. Primești imaginea, etichetată AI.", icon: "image" },
  { id: "prompt", name: "Image → Prompt", short: "Urci o poză care îți place. Primești promptul ei.", icon: "swap" },
  { id: "text", name: "Texte pentru postări", short: "Descrieri cu hook, îndemn și hashtag-uri, în trei variante.", icon: "text" },
  { id: "caracter", name: "Creează-ți caracterul", short: "Descrii ambasadorul. Primești fișa și primul portret.", icon: "user" }
];

export const modules = [
  ["Caractere", "Fișă, model al feței, voce și acorduri, pentru fiecare ambasador."],
  ["Idei", "Idei, hook-uri, scripturi și texte, după nișă și caracter."],
  ["Image → Prompt", "Orice imagine devine un prompt pe care îl poți refolosi."],
  ["Generare", "Imagini și clipuri, pe GPU, când ai nevoie."],
  ["Editare automată", "Reels montate din șabloane: tăieturi, subtitrări, text."],
  ["Publicare și ore", "Postările programate la orele care merg pentru contul tău."],
  ["Rezultate", "Fiecare postare e etichetată și măsurată. Recomandările se îmbunătățesc."],
  ["Conformitate", "Etichete AI, marcaj în fișier, acorduri, filtre de conținut."]
];

export const phases = [
  ["Acum", "Studio + zonele de generare de pe site."],
  ["Lunile 3–6", "Platforma internă: tot procesul într-un singur loc."],
  ["Lunile 6–12", "Platforma pentru clienți, pe credite."],
  ["După 12 luni", "Marketplace de caractere, API, alte limbi."]
];

export const marquee = ["Poze lifestyle", "Reels 9:16", "Voce în română", "Variante A/B", "Etichetă AI", "Texte care vând", "Ore de postare", "Raport lunar"];
