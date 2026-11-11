# Surse și limitele cercetării

Cercetare făcută pe 11 noiembrie 2026. Regulile de platformă și prețurile se schimbă; se reverifică înainte de lansare.

## Ce am putut citi și ce nu

| Sursă | Stare |
|---|---|
| GitHub | căutat direct, după număr de stele |
| Web (bloguri, presă, documentație) | căutat |
| Canalul public de Telegram al lui Hazedy | citit integral, 756 de postări |
| hazedy.com și pagina publică hazegen.com | citite |
| Reddit | **necitit**: accesul direct e blocat din acest mediu |
| X | **necăutat** |
| Instagram | **necitit**: cere autentificare |
| Grupul plătit AI MASTERS | fără acces |

Concluziile despre „ce recomandă comunitățile” vin deci din GitHub și din bloguri, nu din discuții de pe Reddit sau X. Multe bloguri sunt ale unor vânzători de unelte.

## Fapte cu sursă

| Afirmație | Sursă | Cât de sigură |
|---|---|---|
| Instagram cere eticheta „AI-generated profile” pentru conturile cu persoană AI și poate limita distribuția celor fără ea (anunț din 31 august 2026) | [TechCrunch](https://techcrunch.com/2026/08/31/instagram-puts-new-limits-on-undisclosed-ai-profiles/), [Engadget](https://engadget.com/2246914/instagram-will-demote-ai-generated-influencers-if-they-dont-clearly-label-their-account/), [Metricool](https://metricool.com/instagrams-new-ai-label/) | presă, mai multe surse de acord; pagina de politică Meta necitită |
| API-ul de publicare acceptă dezvăluirea de conținut AI la postare (22 iunie 2026) | [jurnalul de modificări Meta](https://developers.facebook.com/documentation/instagram-platform/changelog) | din rezumatul căutării; numele parametrului neverificat |
| Limita de publicare prin API: 100 de postări în 24 de ore, caruselul contează ca una | [documentația Meta](https://developers.facebook.com/documentation/instagram-platform/content-publishing) | documentație oficială; pagini mai vechi dau 50 sau 25 |
| AI Act, articolul 50, se aplică din 2 august 2026; dezvăluirea trebuie să fie vizibilă pentru public | [Morgan Lewis](https://www.morganlewis.com/de/blogs/sourcingatmorganlewis/2026/08/eu-ai-acts-transparency-rules-what-went-into-effect-on-2-august), [McCann FitzGerald](https://www.mccannfitzgerald.com/knowledge/data-privacy-and-cyber-risk/ai-transparency-european-commissions-guidelines-on-article-50-part-2-deployer-obligations), [artificialintelligenceact.eu](https://artificialintelligenceact.eu/?p=6131) | analize juridice; nu e consultanță legală |
| Volumele de rețea RunPod se plătesc și cu pod-ul oprit; circa 0,07 $/GB/lună | [RunPod](https://www.runpod.io/pricing-page), [CostBench](https://www.costbench.com/software/ai-gpu-cloud/runpod/hidden-costs/) | prețuri orientative |
| ai-toolkit are șablon pe RunPod; rezultatele ajung în folderul `output` | [weirdwonderfulai.art](https://weirdwonderfulai.art/tutorial/in-depth-tutorial-using-ostris-ai-toolkit-on-runpod/) | ghid terț |
| worker-comfyui primește workflow-ul la `/run` și întoarce imagini în base64 sau ca adrese S3 | README-ul `runpod-workers/worker-comfyui` | citit direct |
| Set de 15–30 de poze variate; LoRA standard; intensitate 0,7–1,0; rang 32–64 | [Apatero](https://www.apatero.com/blog/comfyui-character-consistency-advanced-workflows-2026), [runflow.io](https://www.runflow.io/blog/comfyui-consistent-characters-flux) | bloguri cu interes comercial |
| Flux.2 Klein ține cel mai bine asemănarea într-un test pe șase modele; Z-Image Turbo are fotorealism mai bun | [mesmer.tools](https://mesmer.tools/blog/best-base-model-for-lora-training-2026), [iimagined.ai](https://iimagined.ai/blog/best-comfyui-models-2026) | bloguri, nu teste controlate |

## Din sesiunea de lucru

- Cuvintele anti-plastic și frecvența lor au fost numărate în biblioteca `nano-banana-pro-prompts-recommend-skill` (15.846 de prompturi, 6.006 cu femei).
- Costurile Higgsfield sunt cele afișate de platformă înainte de fiecare generare.
- Editările repetate ale unei imagini AI au adunat aspect de plastic; generarea de la zero cu prompt anti-plastic a dat cel mai real rezultat.
- Pipeline-ul public HazeGen: poză de bază, set de 39 de poze dintr-o referință, LoRA propriu, test de intensitate pe 12 valori, apoi editare cu identitatea păstrată.

## Inferențe, nu fapte

- Că un set de 30–40 de poze e mai bun decât 15–30 pentru personajul nostru: e o alegere de siguranță, neverificată.
- Că un cont nou trebuie „încălzit” două săptămâni: n-am găsit date independente.
- Că piloni în proporție 40/30/20/10 sunt potriviți: e un punct de pornire, se ajustează după cifre.
- Valorile de antrenare din `04`: puncte de pornire, de confirmat la prima rulare.

## De reverificat înainte de lansare

- [ ] pagina oficială Instagram despre eticheta de profil AI;
- [ ] numele parametrului de dezvăluire AI din Content Publishing API;
- [ ] dacă publicarea prin API merge pe cont Creator sau doar Business;
- [ ] licența modelului de bază ales, pentru uz comercial;
- [ ] prețurile RunPod din consolă;
- [ ] discuțiile recente de pe r/StableDiffusion și r/comfyui despre modelul ales.
