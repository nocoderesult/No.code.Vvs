# Regulile modelelor: schemă, prompt, filtre și preț

Cercetare pentru ticketul `issues/01-regulile-modelelor.md` (harta: `map.md`). Data: 10 noiembrie 2026.

**Metodă.** Doar documentație publică, din surse primare: paginile `llms.txt` și schemele OpenAPI de pe fal.ai,
documentația Google (Gemini API / AI Studio și DeepMind), ghidul oficial Kling 4.0 și politicile Kling, documentația
ByteDance BytePlus ModelArk. Nu am apelat niciun model, nu am încărcat nimic și nu am folosit `FAL_KEY`.

**Convenții.**

- Sursa fiecărei afirmații e între paranteze drepte, de exemplu [fal-omni]. Lista cu URL-uri e la final.
- **neconfirmat** = n-am găsit afirmația într-o sursă primară sau sursele se contrazic.
- **inferență** = concluzia mea pe baza surselor, nu o regulă scrisă de furnizor.
- Prețurile sunt cele din secțiunile „Pricing” ale paginilor `llms.txt` la data de mai sus. fal spune că prețul curent
  exact se află acolo [fal-pricing].

## Pe scurt

1. Toate cele trei modele video primesc pe fal un cadru de pornire și unul final. Limitele cu cadru final: Omni 3–10 s,
   Kling 3–30 s, Seedance 4–30 s. Un clip de 4 s merge la toate [fal-omni] [fal-kling] [fal-sd25].
2. 24 fps e confirmat pentru Omni și Seedance [g-omni-card] [bp-video-tut]. Pentru Kling 4.0 e **neconfirmat**.
3. Formatul 9:16: la Omni trebuie setat `aspect_ratio: "9:16"`, fiindcă implicit e 16:9 [fal-omni]. La Kling și
   Seedance ieșirea urmează raportul cadrelor de intrare [fal-kling-api] [bp-sd25].
4. Omni și Kling împart implicit clipul în mai multe planuri. Trebuie cerut explicit un singur plan continuu
   [g-omni] [k-guide].
5. **Blocaj posibil:** pe fal, API-ul Kling 4.0 apărea ca „coming soon” în paginile fal din 21 octombrie și
   4 noiembrie 2026 [fal-kling4-page] [fal-kling-vs-sd]. Dacă e deschis azi: **neconfirmat**.
6. Draftul Seedance 2.5 se face la 480p, iar completarea se face doar la 1080p. Completarea costă cât un 1080p direct,
   iar draftul se plătește separat [fal-sd25-draft] [bp-sd25].
7. Cost pentru 4 s (720p / 1080p): Omni ≈ $0.33 / $0.49, Kling ≈ $0.63 / $0.94, Seedance ≈ $1.85–1.89 / $4.55–4.66.
   Drumul draft + completare la Seedance costă ≈ $5.37–5.54 (calcul propriu din [fal-omni] [fal-kling] [fal-sd25]).

---

## 1. Gemini Omni Flash 1.2 — `google/gemini-omni-flash/v1.2/image-to-video`

### 1.1 Schema pe fal

| Parametru | Tip | Valori / implicit | Note |
|---|---|---|---|
| `prompt` | string, obligatoriu | max. 20 000 de caractere | descrie cum se animă primul cadru sau cum se interpolează spre cel final [fal-omni] [fal-omni-api] |
| `image_url` | string, obligatoriu | — | „URL of the first frame to animate” [fal-omni] |
| `end_image_url` | string, opțional | — | interpolare între cele două imagini „in their listed order”, durată plafonată la 10 s [fal-omni] |
| `aspect_ratio` | enum | `"16:9"` (implicit), `"9:16"` | [fal-omni] |
| `resolution` | enum | `"360p"`, `"720p"` (implicit), `"1080p"`, `"4k"` | [fal-omni] |
| `duration` | **integer** | 3–15, implicit `8`; max. 10 cu `end_image_url` | [fal-omni] |

- Ieșirea e `video` (obiect File: `url`, `content_type`, `file_name`, `file_size`) [fal-omni-api].
- În schema fal nu există parametru audio, `seed`, `negative_prompt` sau `enable_safety_checker` [fal-omni-api].
  Google confirmă că negative prompts, system instructions, `temperature` și `top_p` nu sunt suportate. Negațiile se
  scriu direct în prompt („Do not do X”) [g-omni].
- Ieșirea are 3–15 s, la 360p/720p/1080p/4K și **24 FPS**. La interpolarea first/last frame durata e 3–10 s
  [g-omni-card].
- Variantele `1080p` și `4k` sunt **upscaled** [g-omni]. Pagina de prețuri Google le numește „with upsampling”
  [g-pricing].
- Sunetul e generat nativ la fiecare video („The model generates a video with audio”) și nu poate fi oprit [g-omni].
  Pe fal: „Native audio is included” [fal-omni]. Numărul de canale și rata de eșantionare: **neconfirmat**.
- Ce se întâmplă cu o imagine 9:16 dacă `aspect_ratio` rămâne pe 16:9: **neconfirmat** (nedocumentat). Dimensiunile
  exacte în pixeli pentru 9:16: **neconfirmat**.
- Toate videourile au watermark SynthID, invizibil [g-omni].
- Engleza e complet suportată. Celelalte limbi „have not been evaluated” [g-omni].

### 1.2 Interpolarea spre cadrul final

- Cu două imagini, modelul animă scena de la primul cadru la ultimul, iar tranziția se descrie în prompt [g-omni].
- Durata e de 3–10 s. Peste 10 s cu două cadre, API-ul Google întoarce „invalid argument error” [g-omni]. Pe fal durata
  e plafonată la 10 s [fal-omni].
- La image-to-video cu o singură imagine, Google spune: „Depending on your prompt, the model will decide how to use the
  image” [g-omni]. API-ul Google are parametrul `task` ca soluție de rezervă (de exemplu `image_to_video`), dar pe fal
  acest parametru lipsește [g-omni] [fal-omni-api]. **Inferență:** pe fal, rolul imaginilor trebuie spus clar în
  prompt.
- Etichetele de control `<FIRST_FRAME>` și `<LAST_FRAME>` sunt depreciate și nu trebuie puse în prompt. Rolul fiecărei
  imagini se descrie în limbaj natural [g-omni].
- DeepMind: „Clearly define what is in your initial frame, specify the exact camera movement or transition path that
  takes place in between, and state precisely what the final frame should reveal.” Exemplul oficial se termină cu
  „One continuous shot, no jump cuts.” [g-omni-guide].

### 1.3 Ghidul oficial de prompt (Google)

- Elementele unui prompt: shot framing and motion, style, lighting, location, action [g-omni-guide].
- Nivelul de detaliu: „The more detail you add, the more control you’ll have”. Totuși, față de Veo, „with Gemini Omni,
  you don't have to be as prescriptive with your prompt” [g-omni-guide].
- **Un singur plan:** „By default Omni Flash will try to create a video with a few different shots.” Pentru un singur
  plan, Google recomandă „In a single unbroken scene”, „In a single continuous shot”, „No scene cuts” [g-omni].
- Negații simple acceptate: „No dialogue”, „No embellishments”, „No extra sound effects” [g-omni].
- Vocabular de cameră: „one continuous shot” sau „oner”; „static”, „locked off”, „fixed”; „push in”, „punch in”,
  „dolly zoom”; „natural smartphone zoom”, „film camera”, „webcam style”. Încadrare wide, medium, close-up. Mișcarea
  camerei: „glide gently” sau „rush suddenly” [g-omni-guide].
- Sunet: implicit, modelul creează singur o pistă potrivită. Tipul de sunet se descrie în prompt, mai ales când vrei
  muzică [g-omni]. Exemplu oficial: „Sound design: Gentle breeze, distant bird chirps. No dialogue.” [g-omni].
- Ghidul Veo, din aceeași familie, adaugă: dialogul între ghilimele, efectele sonore descrise explicit, ambientul
  descris ca peisaj sonor [g-veo]. Veo 3.1 Preview a fost oprit în Gemini API pe 22 octombrie 2026, deci ghidul e doar
  o referință complementară [g-video].
- Momentele din clip se pot fixa în limbaj natural („After 3 seconds…”) sau cu timecode, de exemplu `[0-5s] …` [g-omni].
- Text în video: Omni îl redă corect și lizibil. Dacă în scenă apare text, „it can help to define what it should say”
  [g-omni].
- La image-to-video, Google cere imagini de rezoluție mare și descrieri precise ale mișcării camerei, a subiectului și
  a efectelor, nu „make it move” [g-omni].
- Lungime: Google nu dă o limită recomandată. Pe fal limita e de 20 000 de caractere [fal-omni-api].

### 1.4 Reguli de utilizare și filtre

- Omni aplică filtre de siguranță atât pe prompt, cât și pe videoul generat. Filtrele diferă de la o regiune la alta, iar
  prompturile care încalcă politicile sunt blocate [g-omni].
- „Uploading and editing images containing certain recognizable people is not supported.” [g-omni]
- Se aplică Generative AI Prohibited Use Policy [g-abuse]. Ea interzice încălcarea drepturilor de proprietate
  intelectuală și „Misrepresenting the provenance of generated content by claiming it was created solely by a human,
  in order to deceive” [g-pup].
- Google monitorizează automat și manual. Prompturile și rezultatele se păstrează 55 de zile pentru detectarea abuzurilor
  [g-abuse].
- Pentru branduri, logo-uri, text pe produs, mâncare și băuturi sau mâini, documentația Omni nu are reguli dedicate.
  Existența unor filtre specifice: **neconfirmat**.
- `enable_safety_checker` nu există pe acest endpoint [fal-omni-api].

### 1.5 Prețul pe fal

- Se plătește pe secundă de video, după rezoluție: 360p $0.0273, 720p $0.0819, 1080p $0.1229, 4K $0.2457. Audio e
  inclus. Separat se plătesc tokenii de intrare, cu $1.50 pe milion (text, imagine, video) [fal-omni].
- Aceeași pagină spune însă și că „the input images are not billed”, deci e o contradicție internă [fal-omni]. În orice
  caz, costul intrării e neglijabil (**inferență:** câteva mii de tokeni înseamnă sub $0.01).
- **4 s:** 720p ≈ $0.33; 1080p ≈ $0.49.
- Prin comparație, direct la Google costă ≈ $0.07/s la 720p și $0.104/s la 1080p [g-pricing]. Nu se aplică pe fal.

---

## 2. Kling 4.0 — `kling/v4/image-to-video`

### 2.0 Disponibilitate (blocaj posibil)

- `llms.txt` publică schema, exemple de apel API și prețul [fal-kling].
- Pagina fal despre Kling 4.0 (modificată pe 21 octombrie 2026) spune însă „Now on fal · API coming soon” și „API access
  to Kling 4.0 on fal is coming soon. Until then, you can generate in the playground and fal Agent.” [fal-kling4-page]
- Articolul fal din 4 noiembrie 2026 spune „the Kling 4.0 API isn't open yet”, dar adaugă „(might already be out by the
  time you read this)” [fal-kling-vs-sd].
- Dacă API-ul e deschis azi: **neconfirmat**, fiindcă n-am avut voie să-l apelez.
- Kling 4.0 Flash (`kling/v4/flash/image-to-video`) are pagină API, dar „Flash does not take an end frame” și merge doar
  la 720p [fal-kling-flash]. Kling confirmă că Flash nu suportă start-and-last frames [k-guide].

### 2.1 Schema pe fal

| Parametru | Tip | Valori / implicit | Note |
|---|---|---|---|
| `prompt` | string, opțional | max. 26 000 de caractere | poate lipsi complet [fal-kling-api] |
| `start_image_url` | string, obligatoriu | max. 30 MB, min. 300×300 px, raport 0,40–2,50, timeout 20 s | [fal-kling] |
| `middle_image_urls` | listă, opțional | max. 8 cadre intermediare, în ordine | [fal-kling] |
| `end_image_url` | string, opțional | aceleași limite ca la cadrul de start | [fal-kling-api] |
| `multi_prompt` | listă de `KlingV4Shot` | `prompt` de 1–512 caractere, `duration` 1–30 (implicit 5) | durata clipului e suma planurilor [fal-kling-api] |
| `duration` | **integer** | 3–30, implicit `5` | [fal-kling] |
| `resolution` | enum | `"720p"`, `"1080p"` (implicit) | [fal-kling] |

- Ieșirea e `video` (mp4) [fal-kling].
- Endpointul nu are `aspect_ratio`: „The output aspect ratio follows the input frames.” [fal-kling-api] Kling: „After
  uploading images, the aspect ratio follows the first keyframe.” [k-guide]
- Nu există parametri audio, `seed`, `negative_prompt` sau `enable_safety_checker` [fal-kling-api].
- **Audio:** Kling 4.0 generează sunet stereo pe 2 canale [k-guide]. Ghidul Kling: „Audio-visual synchronization and
  Smart Storyboard are enabled by default and have no separate toggles” [k-guide]. Pagina fal spune că Kling 4.0
  „generates two-channel stereo audio” [fal-kling4-page], iar articolul fal notează că „The Kling 4.0 schema has no
  audio switch at all” [fal-kling-vs-sd]. Că fișierul livrat de API-ul fal chiar are pistă audio: **neconfirmat**.
- fps: **neconfirmat** (nu apare nici în ghidul Kling 4.0, nici pe fal). Dimensiunile în pixeli la 9:16:
  **neconfirmat**.
- Kling anunță 4K și 10-bit HDR pe propria platformă, cu HDR „coming soon”. Pe fal există doar 720p și 1080p
  [k-guide] [fal-kling4-page].

### 2.2 Interpolarea spre cadrul final

- Formatul oficial: „Use @Image1 as the first frame and @Image2 as the last frame, then describe the [process] in
  between.” Un exemplu oficial cere: „The entire video should be one continuous lateral tracking shot from the side,
  with no cuts, angle changes, or scene changes.” [k-guide]
- Kling recomandă first/last frame pentru „transformation processes, craftsmanship, and before-and-after comparisons”
  [k-guide].
- Pe platforma Kling, etichetele `@Image1`, `@Image2` vin din ordinea încărcării [k-guide]. Dacă endpointul fal le
  leagă de `start_image_url` și `end_image_url`: **neconfirmat**.
- Ghidul fal folosește limbaj natural. Pentru cadrul de start: „Begin from the supplied … portrait and preserve…”.
  Pentru cadrul final: „Use the supplied image as the final composition. Match its framing, arrangement of figures, and
  lighting exactly at the end of the move.” [fal-kling-guide]
- Greșeli de evitat, după Kling:
  - un keyframe care schimbă deodată personajul, mediul, produsul, unghiul camerei, lumina și stilul („an unnecessarily
    difficult transition”);
  - referințe care nu se potrivesc între ele;
  - un prompt care contrazice ordinea cadrelor [k-keyframes].
- Cu cadru final nu există o limită de durată separată (rămâne 3–30 s) [fal-kling]. În total pot fi 10 cadre: startul,
  8 intermediare și finalul. Asta se potrivește cu „up to 10 keyframe inputs” din ghidul Kling [k-guide].
- În testul fal cu cadru final, un take era respins dacă „the last frame misses the edited still because the desk
  height or framing jumps at the very end” [fal-kling-vs-sd]. Criteriul e util pentru QC.

### 2.3 Ghidul oficial de prompt (Kling)

- Principiu: „Use descriptive language and minimize abstract terms and negative instructions.” Doar două negații sunt
  cu adevărat necesare: „no subtitles and no background music” [k-guide].
- Abstracțiunile se înlocuiesc cu descrieri concrete. Exemplu: „Premium look” devine „Side backlighting outlines the
  object's edges, the background is blurred, and fine matte grain is visible on the surface.” [k-guide]
- Structura oficială are patru blocuri [k-guide]:
  - `[Asset Roles]`;
  - `[Overall Settings]` (scene and texture, visual style, camera tone);
  - `[Sequence of Events]` (`0–X s: … X–Y s: … Y s–end: …`);
  - `[Audio]` (dialogue/voiceover + ambient sounds + music + sound effects).
- Lungime: până la 8 000 de tokeni. Totuși, la întrebarea „Are longer prompts always better?” ghidul răspunde: „No.
  Start with one sentence that clearly describes the element, scene, action, and emotion. Then add only the details
  that meaningfully affect the result.” [k-guide]
- „Multi-shot is enabled by default, allowing the model to automatically split shots” [k-guide]. Deci un singur plan
  trebuie cerut explicit.
- Camera: Kling 4.0 tratează natural push-ins, pull-outs, pans, tracking shots și orbit shots. Exemplele oficiale
  precizează optica („50mm equivalent lens with a 40° horizontal field of view”) și felul în care se mișcă operatorul
  [k-guide].
- Sunet: se descrie în blocul audio. Muzica și efectele sonore nu se pot încărca, ele sunt generate „based on the
  visuals” [k-guide]. Când nu vor muzică, exemplele oficiale scriu în blocul audio „SFX only, no music, no score, no
  song, no soundtrack.” [k-guide]
- Text și logo: Kling 4.0 „Supports clear and stable generation of multilingual text, emojis, and logos”. Limbile
  listate sunt chineza, engleza, japoneza, coreeana, spaniola, portugheza, germana, franceza și hindi [k-guide]. Româna
  nu e listată.
- Exemplul oficial cu produs cere: „The white Kling wordmark remains correctly spelled, stable, and attached to the same
  chest position.” [k-guide]
- Ghidul fal, pentru produse: „name the silhouette, material, label, and markings that must survive the shot” și „Keep
  the package geometry and label unchanged” [fal-kling-guide].

### 2.4 Reguli de utilizare și filtre

- Kling AI Community Guidelines, în vigoare din 8 septembrie 2026 [k-community]:
  - utilizatorii trebuie să respecte drepturile altora, inclusiv mărcile;
  - e interzis „Fabricating brand partnerships or imitating official brand promotional materials”;
  - e interzisă „Unauthorized removal, alteration, or concealment of AI-generated content labels”;
  - conținutul e verificat tehnic și de oameni, iar sancțiunile merg de la blocarea generării la închiderea contului.
- Regulile despre minori interzic să fie arătați consumând alcool sau alte substanțe interzise [k-community]. Nu e
  cazul aici (shot de ghimbir).
- Pentru mâini, mâncare sau băuturi nealcoolice nu am găsit reguli: **neconfirmat** că ar exista.
- `enable_safety_checker` nu există pe endpoint [fal-kling-api].

### 2.5 Prețul pe fal

- 720p: $0.157/s; 1080p: $0.235/s [fal-kling].
- **4 s:** 720p ≈ $0.63; 1080p ≈ $0.94.
- Flash costă $0.094/s la 720p, dar nu acceptă cadru final [fal-kling-flash].

---

## 3. Seedance 2.5 US — `bytedance/seedance-2.5/us/image-to-video`

### 3.1 Schema pe fal

| Parametru | Tip | Valori / implicit | Note |
|---|---|---|---|
| `prompt` | string, opțional | — | [fal-sd25] |
| `image_url` | string, obligatoriu | JPEG, PNG, WebP, BMP, TIFF, GIF, HEIC, HEIF; max. 30 MB | [fal-sd25] |
| `end_image_url` | string, opțional | aceleași formate | „the generated video will transition from the starting image to this ending image” [fal-sd25] |
| `resolution` | enum | `"480p"`, `"720p"` (implicit), `"1080p"` | [fal-sd25] |
| `draft` | boolean | `false` | `true` = preview la 480p care ignoră `resolution` și întoarce `draft_id` [fal-sd25] |
| `duration` | **string** enum | `"auto"` (implicit), `"4"` … `"30"` | [fal-sd25-api] |
| `aspect_ratio` | const | `"auto"` | la image-to-video e mereu `auto` [fal-sd25-api] |
| `generate_audio` | boolean | `true` | prețul e același cu sau fără sunet [fal-sd25] |
| `bitrate_mode` | enum | `"standard"` (implicit), `"high"` | [fal-sd25] |
| `codec` | enum | `"auto"` (implicit), `"H264"`, `"H265"` | [fal-sd25] |
| `end_user_id` | string | — | [fal-sd25] |

- Ieșirea are `video` și `seed` (obligatorii) și `draft_id`, care e null când nu folosești draftul [fal-sd25-api].
- La intrare nu există `seed`, `negative_prompt`, `camera_fixed` sau `enable_safety_checker` [fal-sd25-api]. BytePlus
  confirmă că `seed` și `camera_fixed` funcționează doar la Seedance 1.x [bp-api].

Specificații de la ByteDance (BytePlus ModelArk):

- Seedance 2.5 scoate video la 24 fps, de 4–30 s, în format MP4 [bp-video-tut]. Articolul fal confirmă „24 fps on fal”
  [fal-sd25-workflows].
- 480p și 720p sunt pe 8 biți. **1080p e pe 10 biți, codat H.265/HEVC**, ceea ce „may not be compatible with some
  playback environments” [bp-sd25].
- Dimensiunile în pixeli la 9:16: 480p = 480×854; 720p = 720×1280; 1080p = 1080×1920 [bp-sd25].
- La first frame și first-last frame, `ratio` poate fi doar `adaptive`, iar ieșirea păstrează raportul imaginii
  `first_frame` [bp-sd25]. Pe fal asta corespunde lui `aspect_ratio: "auto"` [fal-sd25].
- Imaginile de intrare: raport între 0,4 și 2,5, laturi între 300 și 6000 px, sub 30 MB [bp-sd25].
- Audio: cu `generate_audio: true`, modelul generează automat voce, efecte sonore și muzică de fundal, după prompt și
  imagine. Dialogul se pune între ghilimele duble. „All generated videos with audio are mono.” [bp-api]
- BytePlus oferă `output_format: "mov"` pentru post-producție [bp-sd25], dar pe fal opțiunea nu există
  [fal-sd25-api].

### 3.2 Interpolarea spre cadrul final

- Cadrele first/last sunt „locked”: „The input asset is strictly placed as a segment on the output video timeline.”
  Raportul ieșirii se fixează după primul cadru, iar durata o alegi tu [bp-sd25-pg].
- Când ultimul cadru are alt raport decât primul, sursele BytePlus nu spun același lucru. Ghidul de prompt: „it will be
  stretched” [bp-sd25-pg]. Referința API: „the last frame image will be automatically cropped to fit” [bp-api].
  Concluzia comună: ambele cadre trebuie să aibă același raport, ideal aceeași rezoluție.
- Primul și ultimul cadru pot fi identici [bp-api].
- Modul strict e cel în care rolul `first_frame` sau `last_frame` e dat prin parametri. Varianta prin `reference_image`
  nu fixează raportul, iar rezultatul „may not match them exactly” [bp-sd25-pg]. **Inferență:** `image_url` și
  `end_image_url` de pe fal corespund modului strict, după descrierea fal [fal-sd25].
- Cu cadru final nu există o limită de durată separată: 4–30 s [fal-sd25] [bp-sd25].
- La BytePlus, parametrii care nu respectă aceste constrângeri dau eroarea asincronă `InvalidParameter.TaskTypeConstraint`
  [bp-sd25]. Pe fal, `aspect_ratio` e blocat pe `auto`, deci eroarea e evitată.

### 3.3 Modul draft

Cum funcționează:

1. Trimiți o cerere obișnuită cu `draft: true`. Primești un video la 480p și un `draft_id` [fal-sd25].
2. Apelezi `bytedance/seedance-2.5/us/draft/complete` cu `draft_id` (obligatoriu) și, opțional, `codec`. Câmpul
   `resolution` e fixat la `"1080p"`: „Completed drafts only support 1080p output.” [fal-sd25-draft]
   [fal-sd25-draft-api]

Reguli:

- **Valabilitate:** un `draft_id` „Valid for 14 days (7 days for US drafts) and only for the original caller”
  [fal-sd25-draft]. Pe endpointul US avem deci **7 zile**. BytePlus dă 14 zile pentru ID-urile create după 28 octombrie
  2026, dar asta e pe platforma lor [bp-sd25].
- **Ce se refolosește:** modelul, promptul, imaginile, seedul, setarea audio, raportul și durata. La BytePlus aceștia
  nu se pot retrimite: „An error occurs even if their values match” [bp-sd25]. **Inferență:** la completare nu poți
  schimba nici promptul, nici durata. Orice schimbare înseamnă un draft nou.
- **Cost:** pasul 1 se facturează ca un video normal la 480p. Pasul 2 se facturează la rezoluția țintă (1080p), iar
  draftul nu e socotit video de intrare [bp-sd25]. Pe fal, completarea costă „roughly $1.164 per second of generated
  video”, adică ≈ $0.0234 per 1 000 de tokeni la 1080p [fal-sd25-draft].
- **Calcul pentru 4 s** (din prețurile de mai sus): draftul ≈ $0.82–0.88 și completarea ≈ $4.55–4.66, deci în total
  ≈ $5.37–5.54. Un 1080p direct costă ≈ $4.55–4.66.
  - Dacă păstrezi chiar primul take, draftul te costă cu ≈ 19% mai mult.
  - Câștigi de la a doua încercare: 2 drafturi + 1 completare ≈ $6.42, față de 2 × 1080p direct ≈ $9.31.
- **Scopul**, după BytePlus: validezi structura scenei, planificarea cadrelor, mișcarea subiectului și intenția
  promptului înainte de varianta finală [bp-sd25].

### 3.4 Ghidul oficial de prompt (ByteDance)

- Formula: „subject + action/event + scene and environment + visual style + camera movement/shot cuts + sound”.
  Părțile de care nu ai nevoie se pot omite [bp-sd25].
- Caractere speciale pentru sunet: `()` pentru muzică, `<>` pentru efecte sonore, `{}` pentru dialog și `【】` pentru
  subtitrări [bp-sd25].
- Lungime recomandată: cel mult 500 de caractere chinezești sau 1 000 de cuvinte în engleză [bp-api].
- Descrierile pozitive au prioritate. Negațiile merg pentru subtitrări și sunet, de exemplu „No subtitles” sau „No BGM;
  generate only environmental sounds and action sounds” [bp-sd25-pg].
- Timestamps: unitatea de bază e 1 s. Fără goluri între intervale. Prea mult conținut într-un interval duce la
  tăieturi în exces sau la scene sărite [bp-sd25-pg].
- Vocabular de cameră [bp-sd25-pg]:
  - mărimea planului: extreme wide shot, wide shot, medium shot, medium close-up, close-up;
  - mișcări: push in, pull out, pan, track, follow, orbit, dive, pull back, tilt up, handheld shake;
  - unghiuri: low angle, overhead shot, first-person perspective;
  - tehnici: one-shot/long take, dolly zoom, FPV, bullet time, speed ramp;
  - termenii foarte tehnici se scriu ca „[term + descriptive explanation]”.
- Acțiunile se descriu general, cu detalii doar pentru câteva momente memorabile [bp-sd25-pg].
- Există un skill oficial pentru optimizarea prompturilor, `sd25-pe` [bp-sd25-pg].

FAQ-uri relevante pentru noi [bp-sd25-pg]:

- **Text greșit în video** (litere înlocuite, adăugate sau lipsă): desparte cuvântul în litere care apar pe rând, sau
  dă textul corect ca imagine.
- **Subtitrări apărute deși ai cerut să nu fie:** problema nu poate fi eliminată complet. Subtitrările dintr-un video
  de referință pot anula instrucțiunea „no subtitles”.
- **Muzică de fundal apărută deși ai cerut „no BGM”:** enumeră termenii (music, background music, BGM, score,
  instrumental, melody, synth effects, ambient pad) și repetă constrângerea la începutul și la finalul promptului.
- **Artefacte audio** (bolborosit, ecouri, fluierat slab): scoate din prompt instrucțiunile despre apă, valuri sau
  ecou.
- **Texturi ca de amprentă:** apar când intrarea e o imagine generată AI de rezoluție mare. Redimensionează imaginea ca
  să nu depășească rezoluția video. Problema apare mai rar la 1080p decât la 720p.
- **JPG-uri cu subeșantionare de culoare nestandard:** dau HTTP 400. Convertește-le cu FFmpeg sau salvează-le ca PNG.
- **Ochi care strălucesc** la indicații emoționale puternice: folosește un limbaj neutru. **Inferență:** limbajul
  hiperbolic poate produce efecte de lumină nedorite în general.

### 3.5 Reguli de utilizare și filtre

- „Seedance 2.5 does not support directly uploading reference images or videos containing real human faces.”
  [bp-sd25] [bp-portrait] Codul de eroare e `InputImageSensitiveContentDetected.PrivacyInformation` („may contain real
  person”) [bp-errors].
- Mâinile nu sunt menționate nicăieri, deci **neconfirmat** că ar declanșa ceva. „Trust” se aplică doar când se
  declanșează moderarea de fețe [bp-portrait].
- Coduri de moderare: `…SensitiveContentDetected` pentru textul, imaginea, videoul și audio-ul de intrare și de ieșire,
  plus variantele `.PolicyViolation` („may be related to copyright restrictions”), inclusiv pentru videoul și audio-ul
  generate [bp-errors].
- BytePlus Acceptable Use Policy, în vigoare din 30 septembrie 2026 [bp-aup]:
  - fără încălcarea drepturilor de autor sau a mărcilor;
  - fără ștergerea sau ascunderea identificatorilor și etichetelor AI din rezultat;
  - fără folosirea mărcilor „BytePlus” sau „Seedance” fără acord scris și fără a sugera că BytePlus aprobă produsul;
  - fără folosirea AI pentru „misleading statements”;
  - fără ocolirea filtrelor.
- `enable_safety_checker` nu există pe endpointul fal [fal-sd25-api].

### 3.6 Prețul pe fal

- 480p ≈ $0.2205/s; 720p ≈ $0.4730/s; 1080p ≈ $1.164/s [fal-sd25].
- Facturarea se face pe tokeni: $0.0214 per 1 000 la 480p și 720p, ≈ $0.0234 per 1 000 la 1080p. Numărul de tokeni ≈
  (înălțime × lățime × (durata videoului de intrare + durata ieșirii) × 24) / 1024. Audio nu schimbă prețul [fal-sd25].
- **4 s la 9:16** (calcul propriu cu dimensiunile din [bp-sd25]; intervalul merge de la formula pe tokeni la prețul pe
  secundă): 480p ≈ $0.82–0.88; 720p ≈ $1.85–1.89; 1080p ≈ $4.55–4.66.

---

## 4. Nano Banana Pro edit — `fal-ai/nano-banana-pro/edit`

### 4.1 Schema pe fal

| Parametru | Valori / implicit | Note |
|---|---|---|
| `prompt` (obligatoriu) | 3–50 000 de caractere | [fal-nbp-api] |
| `image_urls` | listă | imaginile de editat sau de referință [fal-nbp] |
| `num_images` | 1–4, implicit 1 | [fal-nbp] |
| `aspect_ratio` | `"auto"` (implicit), `"21:9"`, `"16:9"`, `"3:2"`, `"4:3"`, `"5:4"`, `"1:1"`, `"4:5"`, `"3:4"`, `"2:3"`, `"9:16"`, `"4:1"`, `"1:4"`, `"8:1"`, `"1:8"` | [fal-nbp] |
| `resolution` | `"1K"` (implicit), `"2K"`, `"4K"` | [fal-nbp] |
| `output_format` | `"png"` (implicit), `"jpeg"`, `"webp"` | [fal-nbp] |
| `safety_tolerance` | `"1"`–`"6"`, implicit `"4"`; 1 e cel mai strict | [fal-nbp] |
| `limit_generations` | implicit `true`: ignoră din prompt orice instrucțiune despre numărul de imagini | [fal-nbp] |
| `enable_web_search` | implicit `false` | [fal-nbp] |
| altele | `seed`, `temperature` (0–2), `top_p` (0–1), `max_output_tokens`, `system_prompt`, `thinking_level` (doar `"high"`), `include_thoughts`, `history`, `context`, `return_history`, `sync_mode` | [fal-nbp] |

- Ieșirea conține `images`, `description` și, opțional, `conversations` și `grounding_metadata` [fal-nbp].
- Google: implicit, „the model matches the output image size to that of your input image” [g-nb].
- Dimensiunile pentru 9:16 la Nano Banana Pro (Gemini 3 Pro Image): 1K = 768×1376, 2K = 1536×2752, 4K = 3072×5504
  [g-nb]. Raportul lor e 0,558, nu exact 0,5625 ca la 1080×1920 (calcul propriu).
- Modelul primește până la 14 imagini de intrare, iar 5 dintre ele cu fidelitate mare [g-nb].
- Toate imaginile au watermark SynthID [g-nb].

### 4.2 Ghidul oficial de prompt (Google)

- Șablon pentru editare: „Using the provided image of [subject], please [add/remove/modify] [element] to/from the
  scene. Ensure the change is [description of how the change should integrate].” [g-nb]
- Editare țintită (inpainting semantic): „Using the provided image, change only the [specific element] to [new
  element/description]. Keep everything else in the image exactly the same, preserving the original style, lighting,
  and composition.” [g-nb]
- Detaliile critice: „To ensure critical details (like a face or logo) are preserved during an edit, describe them in
  great detail along with your edit request.” [g-nb]
- Șablon fotorealist: „A photorealistic [type of shot] of a [subject description] in a [setting description].
  [Description of the light]. Shot from a [camera angle] with a [lens type].” [g-nb]
- Bune practici [g-nb]:
  - descriere foarte specifică;
  - contextul și scopul imaginii;
  - iterații mici;
  - instrucțiuni pas cu pas;
  - „semantic negative prompts”: descrii pozitiv ce vrei, în loc de „no X”;
  - limbaj de cameră: „wide-angle shot”, „macro shot”, „low-angle perspective”.
- Textul se pune între ghilimele, împreună cu stilul tipografic [g-nb-guide]. „Gemini works best if you first generate
  the text and then ask for an image with the text” [g-nb].
- În prompt se pot cere raportul și formatul, de exemplu „vertical social post” [g-nb-guide].
- Variantele multiple se pot cere în prompt („three distinct variations…”) [g-nb-guide]. Pe fal însă
  `limit_generations: true` ignoră această cerere, așa că se folosește `num_images` [fal-nbp].
- Limite din model card [g-nbp-card]:
  - textul mic iese slab („often blurry in 1k model”), la fel paragrafele lungi;
  - consistența dintre imaginea de intrare și cea generată „is not always perfect”;
  - „infrequent copying/pasting from user's input image to generated image”;
  - confuzii stânga/dreapta.
- Limbi cu rezultate optime: EN, ar-EG, de-DE, es-MX, fr-FR, hi-IN, id-ID, it-IT, ja-JP, ko-KR, pt-BR, ru-RU, ua-UA,
  vi-VN, zh-CN [g-nb]. Româna nu e pe listă.

### 4.3 Reguli de utilizare și filtre

- „Make sure you have the necessary rights to any images you upload. Don't generate content that infringe on others'
  rights.” Se aplică Prohibited Use Policy [g-nb] [g-pup].
- Politicile de siguranță din model card acoperă: CSAM, discurs de ură, conținut periculos, hărțuire, conținut sexual
  explicit și sfaturi medicale contrare consensului științific [g-nbp-card].
- `safety_tolerance` reglează moderarea pe fal. fal spune că „Some models have their own moderation layer that fal does
  not control” [fal-errors]. **Inferență:** filtrele Google se aplică oricum, separat.

### 4.4 Prețul pe fal

- $0.15 pe imagine. La 4K prețul se dublează ($0.30). Web search costă în plus $0.015 [fal-nbp].
- 3 variante la 2K = $0.45.

---

## 5. Seedream 5.0 Pro edit — `bytedance/seedream/v5/pro/edit` (alternativa)

### 5.1 Schema pe fal

| Parametru | Valori / implicit | Note |
|---|---|---|
| `prompt` (obligatoriu) | — | [fal-sdr5] |
| `image_urls` (obligatoriu) | max. 10; dacă trimiți mai multe, se folosesc ultimele 10 | [fal-sdr5] |
| `image_size` | enum (`square_hd`, `square`, `portrait_4_3`, `portrait_16_9`, `landscape_4_3`, `landscape_16_9`, `auto_1K`, `auto_1.5K`, `auto_2K` implicit) sau `{width, height}` | total 921 600–4 624 220 px, raport 1/16–16 [fal-sdr5-api] |
| `num_images` | 1–6 | [fal-sdr5] |
| `output_format` | `"jpeg"` (implicit), `"png"` | [fal-sdr5] |
| `watermark` | `false` | [fal-sdr5] |
| `enable_safety_checker` | `true` | dezactivarea „requires account authorization; unauthorized requests are always checked” [fal-sdr5] |
| `background` | `"opaque"` / `"transparent"` | [fal-sdr5] |
| `enhance_prompt_mode` | `"standard"` / `"fast"` | [fal-sdr5] |

- Ieșirea e `images` [fal-sdr5].
- 1080×1920 înseamnă 2 073 600 px, deci intră în limite: `image_size: {"width": 1080, "height": 1920}` e valid (calcul
  propriu din [fal-sdr5-api]).
- Variantele standard ByteDance pentru 9:16: 1K = 800×1424, 1.5K = 1152×2048, 2K = 1584×2816 [bp-sdr5].
- Intrări: până la 10 imagini, sub 30 MB fiecare, raport 1/16–16 [bp-sdr5].
- Zona de editat se poate indica și vizual, cu coordonate, casete, săgeți sau marcaje [bp-sdr5].
- Textul multilingv nativ acoperă 14 limbi în plus: rusă, arabă, filipineză, thai, turcă, coreeană, malaeză, spaniolă,
  portugheză, indoneziană, franceză, germană, vietnameză și japoneză [bp-sdr5]. Româna nu e pe listă.

### 5.2 Ghidul oficial de prompt (ByteDance)

- Limbaj natural și coerent: subiect + acțiune + mediu, apoi stil, culoare, lumină și compoziție dacă estetica
  contează [bp-sdr-pg].
- Spune scopul și tipul imaginii [bp-sdr-pg].
- Textul care trebuie să apară în imagine se pune între ghilimele duble [bp-sdr-pg].
- La editare: instrucțiuni scurte și clare, fără pronume vagi. Spune explicit ce rămâne neschimbat [bp-sdr-pg].
- Cu mai multe imagini, spune ce iei din fiecare („Image 1”, „Image 2”) [bp-sdr-pg].
- Promptul trebuie să rămână sub 600 de cuvinte în engleză [bp-img-tut].
- Ghidul BytePlus e scris pentru Seedream 4.0 și 4.5. Tutorialul trimite la el sub numele „Seedream 4.0-5.0 prompt
  guide” [bp-img-tut] [bp-sdr-pg].

### 5.3 Reguli de utilizare și filtre

- Se aplică aceeași BytePlus AUP ca la Seedance [bp-aup]. Pe fal, `enable_safety_checker` e implicit `true` [fal-sdr5].

### 5.4 Prețul pe fal

- Prima imagine de intrare e gratuită; fiecare imagine de intrare în plus costă $0.0045 [fal-sdr5].
- Imaginea generată costă $0.0675 dacă are cel mult 1536×1536 px în arie, și $0.135 dacă are între 1536×1536 și
  2048×2048 px [fal-sdr5].
- La 1080×1920 costul e $0.0675 pe imagine, plus $0.0045 pentru fiecare imagine de intrare în plus. 3 variante cu o
  singură imagine de intrare costă $0.20.
- Valoarea implicită `auto_2K` dă la 9:16 1584×2816 px (4,46 MP), peste 2048×2048. Prețul pentru această arie nu e
  listat: **neconfirmat**.

---

## 6. Stratul fal, comun tuturor

- **`content_policy_violation`**: răspuns 422, „Retryable: false”. „The content may have been flagged by either fal's
  filter or one of our partners'.” [fal-errors]
  - Câmpul `categories` poate conține `harassment`, `hate`, `illicit`, `self-harm`, `sexual`, `violence`.
  - Se adaugă `model_moderated` când refuzul vine din moderarea proprie a modelului.
  - Printre încălcări intră și „Generation of content that infringes on third-party intellectual property rights”.
- **`no_media_generated`**: răspuns 422, când modelul nu produce niciun fișier [fal-errors].
- **Facturare:** erorile de server (500+) nu se plătesc. Erorile 422 „may still be charged if a runner spent GPU time”
  [fal-faq]. Timpul de așteptare în coadă nu se plătește [fal-pricing].
- **Fișiere:** stau pe CDN-ul fal „at least 7 days” și au implicit URL public [fal-faq].
- **AUP fal:** interzice încălcarea drepturilor de autor, a mărcilor și a altor drepturi de proprietate intelectuală,
  deepfake-urile fără consimțământ și ocolirea filtrelor [fal-aup].
- **Licență:** fiecare model are licența proprie, iar pe pagina modelului trebuie să apară insigna „Commercial use”
  [fal-faq]. N-am verificat insigna pentru cele 5 endpointuri: **neconfirmat**.

---

## 7. Tabel comparativ

### 7.1 Modelele video

| | Gemini Omni Flash 1.2 | Kling 4.0 | Seedance 2.5 US |
|---|---|---|---|
| Cadru de start / final | `image_url` / `end_image_url` | `start_image_url` / `end_image_url`, plus până la 8 `middle_image_urls` | `image_url` / `end_image_url` |
| Durate | 3–15 s (integer, implicit 8); max. 10 s cu cadru final | 3–30 s (integer, implicit 5) | `"4"`–`"30"` (string) sau `"auto"` (implicit) |
| Rezoluții | 360p, 720p (implicit), 1080p și 4K (upscaled) | 720p, 1080p (implicit) | 480p, 720p (implicit), 1080p (10-bit HEVC); draftul e la 480p |
| 9:16 | `aspect_ratio: "9:16"` (implicit 16:9) | urmează cadrele de intrare | `"auto"`, urmează primul cadru |
| fps | 24 | **neconfirmat** | 24 |
| Audio | mereu; fără parametru | mereu, stereo; fără parametru (pe API-ul fal **neconfirmat**) | `generate_audio` (implicit `true`), mono, același preț |
| 4 s la 720p | ≈ $0.33 | ≈ $0.63 | ≈ $1.85–1.89 |
| 4 s la 1080p | ≈ $0.49 | ≈ $0.94 | ≈ $4.55–4.66 (draft + completare ≈ $5.37–5.54) |
| API pe fal | da | „coming soon” (azi **neconfirmat**) | da |
| Surse | [fal-omni] [g-omni] [g-omni-card] | [fal-kling] [fal-kling-api] [k-guide] [fal-kling4-page] | [fal-sd25] [fal-sd25-draft] [bp-sd25] [bp-video-tut] [bp-api] |

### 7.2 Modelele de imagine (cadrul de vârf)

| | Nano Banana Pro edit | Seedream 5.0 Pro edit |
|---|---|---|
| Intrări | `image_urls` (până la 14; 5 cu fidelitate mare) | `image_urls` (max. 10) |
| Ieșire 9:16 | `aspect_ratio: "9:16"`: 768×1376 / 1536×2752 / 3072×5504 | `image_size: {1080, 1920}` exact; sau 800×1424 / 1152×2048 / 1584×2816 |
| Filtru | `safety_tolerance` 1–6 (implicit `"4"`) | `enable_safety_checker` (implicit `true`) |
| Preț | $0.15 la 1K și 2K, $0.30 la 4K | $0.0675 până la 1536² px, $0.135 până la 2048² px, plus $0.0045 pe imagine de intrare în plus |
| 3 variante | $0.45 (2K) | ≈ $0.20 (1080×1920, o singură imagine de intrare) |
| Surse | [fal-nbp] [g-nb] [g-nbp-card] | [fal-sdr5] [fal-sdr5-api] [bp-sdr5] |

---

## 8. Ce înseamnă pentru promptul nostru

### 8.1 Reguli comune pentru toate modelele

**Fă:**

- **Cadrele pregătite în afara modelelor, la 1080×1920 și în PNG.** La Seedance, cadrul final cu alt raport e întins
  sau decupat, iar JPG-urile nestandard dau eroarea 400 [bp-sd25-pg] [bp-api].
- **Cadrul de start fără subtitrări arse.** Conform `map.md`, subtitrările acoperă sticla în toate cadrele deschiderii.
  La Seedance cadrul de start e pus exact pe timeline („locked”) [bp-sd25-pg]. **Inferență:** subtitrarea ar apărea în
  primul cadru și probabil ar rămâne.
- **Fără față în cadre.** Seedance respinge fețele reale [bp-sd25], iar Omni nu acceptă unele persoane recognoscibile
  [g-omni].
- **Un singur plan continuu de 4 s, cerut explicit.** Omni și Kling fac implicit mai multe planuri [g-omni]
  [k-guide].
- **Diferențe mici între cadrul de start și cel final.** Kling avertizează că schimbarea simultană a produsului, a
  unghiului, a luminii și a stilului face tranziția dificilă [k-keyframes]. **Inferență:** cadrul de vârf ar trebui să
  păstreze încadrarea, unghiul și poziția sticlei din cadrul de start. Se schimbă doar lumina și particulele.
- **Spune ce se întâmplă cu mâna și cu capacul între cadre**, de exemplu „the hand lifts the cap away and exits frame
  right during the first second”. Omni cere „the exact … transition path” [g-omni-guide], iar exemplele Kling descriu
  explicit cum intră și ies mâinile din cadru [k-guide].
- **Sunet doar din efecte, fără muzică.** Muzica o pui tu în montaj (`map.md`). Efecte posibile: clicul capacului
  răsucit, sigiliul care cedează, un „pop” scurt, un whoosh cald în creștere, o sclipire subtilă. „No music” se cere
  explicit [k-guide] [g-omni] [bp-sd25-pg].
- **Eticheta se păstrează, nu se regenerează.** Cere „keep the label exactly as in the first frame”. Kling, Seedream și
  Nano Banana nu listează româna printre limbile în care randează text [k-guide] [bp-sdr5] [g-nb]. Omni declară complet
  suportată doar engleza [g-omni], iar pentru Seedance n-am găsit o listă de limbi pentru text (**neconfirmat**).
  **Inferență:** rândul „ghimbir, lămâie, măr” e cel mai expus. Verifică eticheta la fiecare take și ține camera
  aproape fixă, ca eticheta să nu fie redesenată din alt unghi.
- **Prompturi în engleză**, singura limbă complet suportată de Omni [g-omni].
- **Numește produsul „100 ml ginger juice bottle”, nu „ginger shot”.** **Inferență:** „shot” e termen de cameră în
  toate ghidurile de prompt și ar putea fi citit ca indicație de montaj.

**Nu face:**

- **Nu scrie „no text / no logos” la negații.** Exemplele Seedance o fac des [bp-sd25-pg], dar la noi ar lupta cu
  eticheta. Scrie în schimb „no subtitles, no added text or watermarks; the existing bottle label stays unchanged”.
- **Nu șterge și nu ascunde etichetele sau watermark-urile AI** [k-community] [bp-aup].
- **Nu sugera o colaborare oficială cu brandul dacă nu există** [k-community].
- **Afirmațiile de sănătate nu țin de model.** Nicio politică a modelelor nu interzice o băutură nealcoolică.
  Afirmațiile de sănătate țin de regulile platformelor (ticketul 02).

### 8.2 Gemini Omni Flash 1.2

**Fă:**

- **Parametri:** `aspect_ratio: "9:16"`, `duration: 4` (integer), `resolution: "720p"` la probe, fiindcă 1080p e oricum
  upscaled [fal-omni] [g-omni].
- **Prompt în trei părți:** ce e în cadrul inițial, mișcarea sau tranziția, ce arată cadrul final [g-omni-guide]. Plus
  „Single continuous shot, no scene cuts.” [g-omni]
- **Sunetul explicit:** „Sound design: …”, urmat de „No dialogue. No music.” [g-omni]
- **Textul etichetei definit:** `The bottle label reads "SNOOZZ" and "Ginger Energy" and stays unchanged.`
  [g-omni]
- **Timpii:** limbaj natural („during the first second…”, „by the final frame…”) sau `[0-1s] … [1-4s] …` [g-omni].
- **Camera:** „locked off” / „static”, sau cel mult „slow push in” [g-omni-guide].

**Nu face:**

- **Nu lăsa `aspect_ratio` pe valoarea implicită** (16:9) [fal-omni].
- **Nu cere peste 10 s** când ai `end_image_url` [g-omni].
- **Nu folosi `<FIRST_FRAME>` / `<LAST_FRAME>`** [g-omni].
- **Nu descrie excesiv.** Omni „you don't have to be as prescriptive” [g-omni-guide]. **Inferență:** 60–120 de cuvinte
  ajung pentru 4 s.
- **Nu căuta `negative_prompt` sau `seed`:** nu există [fal-omni-api] [g-omni].

### 8.3 Kling 4.0

**Fă:**

- **Verifică întâi dacă API-ul e deschis** [fal-kling4-page] [fal-kling-vs-sd]. Dacă nu e, proba se face manual în
  playground-ul fal.
- **Parametri:** `duration: 4`, `resolution: "720p"` la probe. Nu există `aspect_ratio`, deci cadre 9:16 dau un clip
  9:16 [fal-kling] [fal-kling-api].
- **Structura Kling:** rolurile cadrelor → setările generale → evenimentele (`0–1 s`, `1–3 s`, `3–4 s`) → sunetul
  [k-guide]. Cadrele se numesc în limbaj natural: „Begin exactly on the supplied start frame… End exactly on the
  supplied end frame, matching its framing and lighting.” [fal-kling-guide]
- **Un singur plan:** „One continuous shot, with no cuts, angle changes, or scene changes.” [k-guide]
- **Lumina descrisă concret**, nu „premium” sau „cinematic”, de exemplu „warm golden backlight rising from the open
  neck, rays fanning upward” [k-guide].
- **Ce trebuie să rămână neschimbat** [fal-kling-guide] [k-guide]: forma sticlei, capacul alb, PET-ul transparent,
  lichidul galben-pal tulbure, iar eticheta cu „SNOOZZ” și „Ginger Energy” scrisă corect, stabilă și în aceeași
  poziție.
- **Sunetul:** „SFX only, no music, no score, no song, no soundtrack. No subtitles.” [k-guide]

**Nu face:**

- **Nu folosi `multi_prompt` pentru 4 s.** **Inferență** din [fal-kling-api]: ar împărți clipul în planuri.
- **Nu adăuga negații** în afară de „no subtitles” și „no background music” [k-guide].
- **Nu folosi Kling 4.0 Flash:** nu acceptă cadru final [fal-kling-flash].
- **Nu presupune 24 fps** (**neconfirmat**). Verifică rezultatul cu `ffprobe`.

### 8.4 Seedance 2.5 (finalul)

**Fă:**

- **Parametri:** `duration: "4"` (string), `codec: "H264"`, ca fișierul să se deschidă sigur în Premiere sau DaVinci
  (1080p e implicit H.265 pe 10 biți) [fal-sd25] [bp-sd25]. La final, `bitrate_mode: "high"` [fal-sd25].
- **Validarea pe Seedance se face cu draftul.** Probele Omni și Kling nu prezic aspectul Seedance (**inferență**).
  Folosește `draft: true`, apoi `draft/complete` în cel mult 7 zile. Promptul nu se mai poate schimba după draft
  [fal-sd25-draft] [bp-sd25].
- **Ordinea din prompt:** subiect + acțiune + scenă + stil + cameră + sunet [bp-sd25]. Efectele sonore între `<>`, de
  exemplu `<the cap seal cracks>`, `<a short soft pop>`, `<a warm rising whoosh>` [bp-sd25].
- **Timestamps la secundă:** `0-1s …`, `1-3s …`, `3-4s …` [bp-sd25-pg].
- **Constrângerea de sunet**, la începutul și la finalul promptului: „No subtitles. No BGM, no music, no score, no
  instrumental, no melody; only action sounds.” [bp-sd25-pg]
- **Cadrul final redimensionat** la cel mult rezoluția video (1080×1920 sau 720×1280), ca să eviți texturile ca de
  amprentă [bp-sd25-pg]. Cadrele în PNG [bp-sd25-pg].

**Nu face:**

- **Nu pune fețe reale în cadre** [bp-sd25].
- **Nu scrie despre apă, valuri, plescăit sau ecou** („sloshing liquid”, „splash”): dau artefacte audio [bp-sd25-pg].
- **Nu înghesui multe acțiuni în 4 s** [bp-sd25-pg].
- **Nu lăsa `duration: "auto"`** [fal-sd25].
- **Nu presupune că poți refolosi un `seed`:** la intrare nu există [fal-sd25-api] [bp-api].
- **Nu folosi marca „Seedance” în materialul public** și nu sugera că BytePlus aprobă produsul [bp-aup].

### 8.5 Nano Banana Pro edit (cadrul de vârf)

**Fă:**

- **Intrarea:** cadrul de start curățat, la 1080×1920.
- **Parametri** [fal-nbp] [g-nbp-card]:
  - `aspect_ratio: "9:16"` sau `"auto"`;
  - `resolution: "2K"`, fiindcă textul mic iese slab la 1K;
  - `num_images: 3` pentru 2–3 variante;
  - `output_format: "png"`.
- **Șablonul Google:** „Using the provided image, change only … Keep everything else in the image exactly the same,
  preserving the original style, lighting, and composition.” Eticheta descrisă în detaliu, ca să fie păstrată [g-nb].
- **Lumina descrisă fotografic:** sursa (deschiderea gâtului), direcția (în sus și în evantai), culoarea (auriu cald),
  plus particulele de ghimbir și lămâie [g-nb] [g-nb-guide].
- **Descrieri pozitive** în loc de „no X” [g-nb].
- **După generare, crop sau resize la exact 1080×1920**, fiindcă ieșirea 9:16 are raportul 0,558 [g-nb].

**Nu face:**

- **Nu cere rescrierea textului de pe etichetă.** Româna nu e printre limbile recomandate [g-nb].
- **Nu cere „3 variations” în prompt:** `limit_generations` ignoră cererea [fal-nbp].
- **Nu activa `enable_web_search`:** costă în plus și nu ajută [fal-nbp].
- **Lasă `safety_tolerance` pe implicit** (`"4"`) [fal-nbp].

### 8.6 Seedream 5.0 Pro edit (alternativa)

**Fă:**

- **Parametri:** `image_size: {"width": 1080, "height": 1920}`, adică exact formatul montajului, la $0.0675 pe imagine
  [fal-sdr5] [fal-sdr5-api]. Plus `output_format: "png"` și `num_images: 2–3`.
- **Prompt cu două părți:** ce se schimbă și ce rămâne neschimbat. Textul pe care îl numești, între ghilimele duble.
  Scopul imaginii, de exemplu „vertical product ad frame” [bp-sdr-pg].
- **Sub 600 de cuvinte** [bp-img-tut].

**Nu face:**

- **Nu lăsa `auto_2K`:** dă 1584×2816 px, cu preț nelistat [fal-sdr5] [bp-sdr5].
- **Nu dezactiva `enable_safety_checker`:** cere autorizarea contului [fal-sdr5].
- **Nu folosi pronume vagi** („make it brighter”) [bp-sdr-pg].

---

## 9. Ce blochează sau pune planul în risc

1. **API-ul Kling 4.0 pe fal poate fi încă închis** [fal-kling4-page] [fal-kling-vs-sd]. În acest caz `fal_run.py` nu
   poate rula proba Kling. Variante: playground-ul fal (manual) sau doar proba Omni.
2. **Cadrul de pornire are subtitrări arse peste sticlă** (`map.md`). Trebuie curățat, de exemplu cu Nano Banana edit,
   sau înlocuit. Altfel modelele le preiau (**inferență** pe baza [bp-sd25-pg]).
3. **Eticheta e în română, cu diacritice.** Kling, Seedream și Nano Banana nu listează româna pentru text [k-guide]
   [bp-sdr5] [g-nb], iar Omni declară complet suportată doar engleza [g-omni]. Rămâne nevoie de un plan de rezervă în
   post (e deja la „Not yet specified” în hartă).
4. **Seedance la 1080p e implicit H.265 pe 10 biți** [bp-sd25]. Setează `codec: "H264"`.
5. **Draftul Seedance expiră în 7 zile pe endpointul US**, iar completarea costă cât un 1080p direct [fal-sd25-draft].
6. **Neconfirmate la Kling:** dacă sunetul ajunge în fișierul de pe API-ul fal și ce fps are ieșirea.
7. **Durată minimă:** Seedance începe de la 4 s [fal-sd25]. Un insert mai scurt se taie în montaj.

## 10. Lista „neconfirmat”

- Dacă API-ul Kling 4.0 e deschis azi pe fal.
- Dacă ieșirea Kling de pe fal are pistă audio; fps-ul Kling 4.0; dimensiunile în pixeli la 9:16 pentru Kling și Omni.
- Cum tratează Omni o imagine 9:16 când `aspect_ratio` e lăsat pe 16:9.
- Numărul de canale și rata de eșantionare la Omni.
- Dacă fal taxează imaginile de intrare la Omni (pagina se contrazice) [fal-omni].
- Dacă mâinile declanșează vreun filtru: n-am găsit nicio regulă.
- Dacă un nume de brand în prompt declanșează `…PolicyViolation` (copyright) la Seedance. Codul există [bp-errors], dar
  declanșatorul nu e documentat.
- Dacă etichetele `@Image1` funcționează la Kling pe fal.
- Prețul Seedream pentru arii peste 2048×2048.
- Adâncimea de culoare cu `codec: "H264"` la Seedance 1080p.
- Licența comercială a fiecărui endpoint (insigna „Commercial use” pe pagina modelului) [fal-faq].

---

## Surse

fal.ai:

- `fal-omni`: <https://fal.ai/models/google/gemini-omni-flash/v1.2/image-to-video/llms.txt>
- `fal-omni-api`: <https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=google/gemini-omni-flash/v1.2/image-to-video>
- `fal-kling`: <https://fal.ai/models/kling/v4/image-to-video/llms.txt>
- `fal-kling-api`: <https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=kling/v4/image-to-video>
- `fal-kling-flash`: <https://fal.ai/models/kling/v4/flash/image-to-video/llms.txt>
- `fal-kling4-page`: <https://fal.ai/kling-4> (dateModified 2026-10-21)
- `fal-kling-vs-sd`: <https://fal.ai/learn/devs/kling-4-0-vs-seedance-2-5> (4 noiembrie 2026)
- `fal-kling-guide`: <https://fal.ai/learn/devs/kling-4-prompting-guide> (21 octombrie 2026)
- `fal-sd25`: <https://fal.ai/models/bytedance/seedance-2.5/us/image-to-video/llms.txt>
- `fal-sd25-api`: <https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=bytedance/seedance-2.5/us/image-to-video>
- `fal-sd25-draft`: <https://fal.ai/models/bytedance/seedance-2.5/us/draft/complete/llms.txt>
- `fal-sd25-draft-api`: <https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=bytedance/seedance-2.5/us/draft/complete>
- `fal-sd25-workflows`: <https://fal.ai/learn/tools/seedance-2-5-workflows>
- `fal-nbp`: <https://fal.ai/models/fal-ai/nano-banana-pro/edit/llms.txt>
- `fal-nbp-api`: <https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=fal-ai/nano-banana-pro/edit>
- `fal-sdr5`: <https://fal.ai/models/bytedance/seedream/v5/pro/edit/llms.txt>
- `fal-sdr5-api`: <https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=bytedance/seedream/v5/pro/edit>
- `fal-pricing`: <https://fal.ai/pricing.md>
- `fal-errors`: <https://fal.ai/docs/documentation/model-apis/errors.md>
- `fal-faq`: <https://fal.ai/docs/documentation/model-apis/faq.md>
- `fal-aup`: <https://fal.ai/legal/acceptable-use-policy>

Google:

- `g-omni`: <https://ai.google.dev/gemini-api/docs/omni> (identic cu <https://aistudio.google.com/docs/omni.md>)
- `g-omni-card`: <https://ai.google.dev/gemini-api/docs/models/gemini-omni-flash>
- `g-omni-guide`: <https://deepmind.google/models/gemini-omni/prompt-guide/>
- `g-video`: <https://ai.google.dev/gemini-api/docs/video>
- `g-veo`: <https://aistudio.google.com/docs/veo.md>
- `g-pricing`: <https://aistudio.google.com/docs/pricing.md>
- `g-pup`: <https://policies.google.com/terms/generative-ai/use-policy>
- `g-abuse`: <https://aistudio.google.com/docs/usage-policies.md>
- `g-nb`: <https://aistudio.google.com/docs/image-generation.md>
- `g-nb-guide`: <https://deepmind.google/models/gemini-image/prompt-guide/>
- `g-nbp-card`: <https://deepmind.google/models/model-cards/gemini-3-pro-image/> (PDF, „Gemini 3 Pro Image External Model Card”)

Kling:

- `k-guide`: <https://kling.ai/quickstart/kling-4-model-user-guide> (Kling 4.0 User Guide, 4 noiembrie 2026)
- `k-keyframes`: <https://kling.ai/blog/kling-4-multiple-keyframes-guide>
- `k-community`: <https://kling.ai/docs/community-policy> (în vigoare din 8 septembrie 2026)

ByteDance / BytePlus ModelArk:

- `bp-sd25`: <https://docs.byteplus.com/docs/en/modelark/seedance-2-5.md> (Dreamina Seedance 2.5 tutorial, actualizat 2026-10-28)
- `bp-sd25-pg`: <https://docs.byteplus.com/docs/en/modelark/seedance-2-5-prompt-guide.md>
- `bp-video-tut`: <https://docs.byteplus.com/docs/en/modelark/video-generation-tutorial.md>
- `bp-api`: <https://docs.byteplus.com/docs/en/modelark/create-video-generation-task-api.md>
- `bp-errors`: <https://docs.byteplus.com/docs/en/modelark/error-codes.md>
- `bp-portrait`: <https://docs.byteplus.com/docs/en/modelark/seedance-portrait-asset-guide.md>
- `bp-aup`: <https://docs.byteplus.com/en/docs/legal/docs-acceptable-use-policy> (în vigoare din 30 septembrie 2026)
- `bp-sdr5`: <https://docs.byteplus.com/docs/en/modelark/seedream-5-0-pro.md>
- `bp-sdr-pg`: <https://docs.byteplus.com/docs/en/modelark/seedream-4-0-5-0-prompt-guide.md>
- `bp-img-tut`: <https://docs.byteplus.com/docs/en/modelark/image-generation-tutorial.md>

[fal-omni]: https://fal.ai/models/google/gemini-omni-flash/v1.2/image-to-video/llms.txt
[fal-omni-api]: https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=google/gemini-omni-flash/v1.2/image-to-video
[fal-kling]: https://fal.ai/models/kling/v4/image-to-video/llms.txt
[fal-kling-api]: https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=kling/v4/image-to-video
[fal-kling-flash]: https://fal.ai/models/kling/v4/flash/image-to-video/llms.txt
[fal-kling4-page]: https://fal.ai/kling-4
[fal-kling-vs-sd]: https://fal.ai/learn/devs/kling-4-0-vs-seedance-2-5
[fal-kling-guide]: https://fal.ai/learn/devs/kling-4-prompting-guide
[fal-sd25]: https://fal.ai/models/bytedance/seedance-2.5/us/image-to-video/llms.txt
[fal-sd25-api]: https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=bytedance/seedance-2.5/us/image-to-video
[fal-sd25-draft]: https://fal.ai/models/bytedance/seedance-2.5/us/draft/complete/llms.txt
[fal-sd25-draft-api]: https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=bytedance/seedance-2.5/us/draft/complete
[fal-sd25-workflows]: https://fal.ai/learn/tools/seedance-2-5-workflows
[fal-nbp]: https://fal.ai/models/fal-ai/nano-banana-pro/edit/llms.txt
[fal-nbp-api]: https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=fal-ai/nano-banana-pro/edit
[fal-sdr5]: https://fal.ai/models/bytedance/seedream/v5/pro/edit/llms.txt
[fal-sdr5-api]: https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=bytedance/seedream/v5/pro/edit
[fal-pricing]: https://fal.ai/pricing.md
[fal-errors]: https://fal.ai/docs/documentation/model-apis/errors.md
[fal-faq]: https://fal.ai/docs/documentation/model-apis/faq.md
[fal-aup]: https://fal.ai/legal/acceptable-use-policy
[g-omni]: https://ai.google.dev/gemini-api/docs/omni
[g-omni-card]: https://ai.google.dev/gemini-api/docs/models/gemini-omni-flash
[g-omni-guide]: https://deepmind.google/models/gemini-omni/prompt-guide/
[g-video]: https://ai.google.dev/gemini-api/docs/video
[g-veo]: https://aistudio.google.com/docs/veo.md
[g-pricing]: https://aistudio.google.com/docs/pricing.md
[g-pup]: https://policies.google.com/terms/generative-ai/use-policy
[g-abuse]: https://aistudio.google.com/docs/usage-policies.md
[g-nb]: https://aistudio.google.com/docs/image-generation.md
[g-nb-guide]: https://deepmind.google/models/gemini-image/prompt-guide/
[g-nbp-card]: https://deepmind.google/models/model-cards/gemini-3-pro-image/
[k-guide]: https://kling.ai/quickstart/kling-4-model-user-guide
[k-keyframes]: https://kling.ai/blog/kling-4-multiple-keyframes-guide
[k-community]: https://kling.ai/docs/community-policy
[bp-sd25]: https://docs.byteplus.com/docs/en/modelark/seedance-2-5.md
[bp-sd25-pg]: https://docs.byteplus.com/docs/en/modelark/seedance-2-5-prompt-guide.md
[bp-video-tut]: https://docs.byteplus.com/docs/en/modelark/video-generation-tutorial.md
[bp-api]: https://docs.byteplus.com/docs/en/modelark/create-video-generation-task-api.md
[bp-errors]: https://docs.byteplus.com/docs/en/modelark/error-codes.md
[bp-portrait]: https://docs.byteplus.com/docs/en/modelark/seedance-portrait-asset-guide.md
[bp-aup]: https://docs.byteplus.com/en/docs/legal/docs-acceptable-use-policy
[bp-sdr5]: https://docs.byteplus.com/docs/en/modelark/seedream-5-0-pro.md
[bp-sdr-pg]: https://docs.byteplus.com/docs/en/modelark/seedream-4-0-5-0-prompt-guide.md
[bp-img-tut]: https://docs.byteplus.com/docs/en/modelark/image-generation-tutorial.md
