# Metaprompt: ingredientele ies din sticlă (SNOOZZ Ginger Energy)

Acesta e șablonul din care se scriu prompturile pentru insert, pentru fiecare model. Blocurile fixe din secțiunea 2
se copiază cuvânt cu cuvânt în fiecare prompt, ca produsul, eticheta și lumina să rămână aceleași de la un model la
altul. Prompturile sunt în engleză, singura limbă pe care toate modelele o suportă complet. Regulile pe model vin din
[research/01-regulile-modelelor.md](research/01-regulile-modelelor.md).

Referința de stil e reclama cu grapefruitul care iese din doză. Din ea luăm tehnica, nu brandul: totul arată ca filmat
la viteză mare, cu stropi înghețați în aer, detaliu macro pe pulpă, lumină puternică din spate și încetinitor.

## 1. Legătura cu montajul

- **Cadrul de pornire:** cadrul 185 din montaj (7,71 s), curățat de subtitrare. Capacul e încă pus și mâna îl răsucește,
  ca sticla să se poată umfla puțin înainte să se deschidă: așa se vede presiunea din ea.
- **Cadrul de final:** cadrul 214 (8,92 s), curățat de subtitrarea „să-l ignori!”. E ultimul cadru cu sticla ținută
  lângă fereastră, chiar înaintea tăieturii la gura care bea (cadrul 215).
- **Ce înlocuiește insertul:** cadrele 185–214 din montaj, adică ridicarea capacului, crossfade-ul și cadrul de la
  fereastră (1,25 s), cu ~5 s de presiune și explozie. După insert, montajul continuă cu cadrul 215, exact ca acum.
- **De ce merge:** Kling a respectat ambele capete în proba anterioară (diferență 1,1 și 1,4 din 255). Explozia
  acoperă trecerea de la fundalul verde închis al macro-ului la fereastra luminoasă, ca o tranziție naturală.

## 2. Blocurile fixe (în engleză, cuvânt cu cuvânt)

- **PRODUCT:** `a small 100 ml clear plastic bottle of pale yellow, cloudy ginger juice, with a white tamper ring on its
  open threaded neck and a round orange label on the front`
- **LABEL (imagini):** `the round orange label reads "SNOOZZ" in bold black letters with the two O's drawn as solid
  black dots, then "Ginger Energy", then "ghimbir, lămâie, măr" and "100 ml" in smaller black letters, exactly as in the
  reference image`
- **LABEL (video):** `the label reads "SNOOZZ" and "Ginger Energy" and stays unchanged`. La video nu cerem rândul în
  română: modelele nu garantează textul românesc și ar încerca să-l rescrie.
- **INGREDIENTS:** `thin crisp apple slices with red-blushed skin and pale, juicy flesh, small lemon wheels and wedges
  with translucent, glistening pulp and bright yellow rind, and small coins and knobs of fresh ginger root with beige
  skin and fibrous pale-yellow flesh`
- **REALISM:** `filmed like a high-speed commercial at 1000 frames per second and played back in slow motion: every
  droplet is round and frozen in the air, catching specular highlights and tiny caustics, the pieces follow real
  gravity and momentum in natural arcs, every texture is crisp macro detail, shallow depth of field with creamy bokeh`
- **LIGHT_START:** `warm morning café light, with a dark green out-of-focus plant behind the bottle`
- **LIGHT_END:** `bright, warm backlight from a large café window with plants, a soft sun flare from the top right`

**Mărimea bucăților:** bucăți mici și felii subțiri, care pot trece prin gâtul sticlei (~3 cm). Pe măsură ce urcă, se
răsfiră. Așa rămâne credibil, nu desen animat.

## 3. Momentele (5 s)

1. **0–0,8 s, presiunea:** mâna răsucește capacul, iar sticla se umflă foarte puțin: pereții de plastic se bombează abia
   vizibil, bule mici urcă repede prin suc și se aude un scârțâit fin și un șuierat care crește.
2. **0,8–1 s, deschiderea:** mâna ridică capacul și presiunea se eliberează dintr-odată.
3. **1–2,8 s, explozia:** pornește imediat și frumos, cu încetinitorul. Feliile de măr, rotițele de lămâie și bucățile de
   ghimbir ies din gât într-o coroană de picături de suc și se rotesc încet. Camera se retrage ușor până se vede toată
   sticla și trece prin cadrul-cheie al exploziei.
4. **2,8–4,2 s:** bucățile se răsfiră în arc și cad pe lângă sticlă, afară din cadru. Picăturile plutesc, iar lumina se
   încălzește spre fereastra luminoasă.
5. **4,2–5 s:** aerul se limpezește. Sticla, ținută de mâna din dreapta, ajunge în cadrul final de lângă fereastră, cu
   eticheta spre cameră.

## 4. Prompturile compilate

### 4.1 Nano Banana Pro edit: cadrul de final curat (2K, 9:16, PNG)

Intrări: cadrul 214, apoi cadrul de referință pentru etichetă (sticla pe masă).

> Using the provided images, remove only the white caption text "să-l ignori!" with its soft dark outline and shadow
> that is overlaid across the bottle, and restore what is behind it as if the caption was never there: the round orange
> label exactly as in the second image, where the label reads "SNOOZZ" in bold black letters with the two O's drawn as
> solid black dots, then "Ginger Energy", then "ghimbir, lămâie, măr" and "100 ml" in smaller black letters, and the
> pale yellow, cloudy juice around it. Keep everything else in the image exactly the same, preserving the original
> lighting, colours, focus, grain and composition: the hand holding the bottle from the right, the open bottle neck, the
> wooden table and the bright café window with plants behind. Do not add any text, logo or object.

După generare se lipește înapoi în cadrul real doar zona subtitrării, ca la cadrul de pornire, iar eticheta se verifică
literă cu literă.

### 4.2 Nano Banana Pro edit: cadrul-cheie al exploziei (2K, 9:16, PNG)

Intrări: cadrul de final curat, cadrul de referință pentru etichetă și cadrul de pornire curat (8,04 s). Încadrarea e cea din
cadrul de final, ca a doua jumătate a clipului să fie doar bucățile care cad.

> Using the provided images, show the peak moment of the shot in the framing and light of the first image: a small
> 100 ml clear plastic bottle of pale yellow, cloudy ginger juice, with a white tamper ring on its open threaded neck
> and a round orange label on the front, held by the same hand from the right, where the label reads "SNOOZZ" in bold
> black letters with the two O's drawn as solid black dots, then "Ginger Energy", then "ghimbir, lămâie, măr" and
> "100 ml" in smaller black letters, exactly as in the reference image. Bursting up out of the open neck in a crown of
> pale yellow juice droplets are thin crisp apple slices with red-blushed skin and pale, juicy flesh, small lemon wheels
> and wedges with translucent, glistening pulp and bright yellow rind, and small coins and knobs of fresh ginger root
> with beige skin and fibrous pale-yellow flesh, spinning in the air above and around the bottle while the label stays
> fully visible below them. Bright, warm backlight from a large café window with plants, a soft sun flare from the top
> right, rim light on every droplet and slice. Filmed like a high-speed commercial at 1000 frames per second and played
> back in slow motion: every droplet is round and frozen in the air, catching specular highlights and tiny caustics, the
> pieces follow real gravity and momentum in natural arcs, every texture is crisp macro detail, shallow depth of field
> with creamy bokeh. A photorealistic vertical 9:16 product photograph for a social video, matching the colours, white
> balance and fine grain of the first image.

### 4.3 Kling 4.0: clipul (1080p, 5 s; start + cadrul-cheie + final)

Parametri: `start_image_url` = cadrul de pornire curat, `middle_image_urls` = [cadrul-cheie], `end_image_url` =
cadrul de final curat, `duration: 5`, `resolution: "1080p"`. Structura e cea din ghidul Kling: rolurile cadrelor,
setările, momentele, apoi sunetul.

> Begin exactly on the supplied start frame: in a café, a hand grips the white cap of a small 100 ml clear plastic
> bottle of pale yellow, cloudy ginger juice, with a white tamper ring on its threaded neck and a round orange label
> on the front, held by another hand. Pass through the supplied middle frame at the peak of the burst. End exactly on
> the supplied end frame, matching its framing and lighting: the bottle held by the hand on the right, by a bright
> café window.
> One continuous shot, with no cuts, angle changes, or scene changes. Photorealistic high-speed product commercial,
> macro detail, shallow depth of field.
> 0-0.8 s: the hand twists the cap while pressure builds inside: the bottle swells very slightly, its plastic walls
> bulging just visibly, and tiny bubbles race up through the juice.
> 0.8-1 s: the hand lifts the cap off to the top right and the pressure releases at once.
> 1-2.8 s: instantly and beautifully, in slow motion, thin crisp apple slices with red-blushed skin and pale, juicy
> flesh, small lemon wheels and wedges with translucent, glistening pulp and bright yellow rind, and small coins and
> knobs of fresh ginger root with beige skin and fibrous pale-yellow flesh burst up out of the open neck in an elegant
> crown of juice droplets, spinning slowly, while the camera eases back to show the whole bottle.
> 2.8-4.2 s: the pieces arc outward and fall past the bottle and out of frame, droplets drift and sparkle, and the
> light warms into bright backlight from the café window.
> 4.2-5 s: the air clears and the bottle settles into the end frame, the label facing the camera.
> Every droplet is round and catches specular highlights, and the pieces follow real gravity and momentum. The bottle
> shape, the clear plastic, the pale yellow cloudy juice and the round orange label stay the same; the label reads
> "SNOOZZ" and "Ginger Energy", correctly spelled and stable.
> Sound: a faint creak and a rising hiss as the pressure builds, the cap popping off, a juicy burst, crisp airy
> whooshes as the slices fly, and fine droplets pattering. SFX only, no music, no score, no song, no soundtrack. No
> subtitles.

### 4.4 Seedance 2.5: varianta pentru final (1080p, 5 s; doar start + final)

Parametri: `image_url` = cadrul de pornire curat, `end_image_url` = cadrul de final curat, `duration: "5"`,
`resolution: "1080p"`, `codec: "H264"`, `generate_audio: true`. Seedance nu are cadru-cheie la mijloc. Fiindcă
cuvintele despre apă și plescăit îi strică sunetul, aici scriem doar „droplets”, „spray” și „burst”.

> No subtitles. No BGM, no music, no score, no instrumental, no melody; only action sounds. A small 100 ml clear
> plastic bottle of pale yellow, cloudy ginger juice, with a white tamper ring on its threaded neck and a round orange
> label on the front, held by a hand in a café. 0-1s: the other hand twists the white cap while pressure builds and
> the bottle swells very slightly, its plastic walls bulging just visibly <a faint creak> <a rising hiss>, then lifts
> the cap off to the top right <the cap pops off>. 1-3s: instantly, thin crisp apple slices, small lemon wheels and
> small coins of fresh ginger burst up out of the open neck in an elegant crown of droplets and spin slowly in the air
> <a soft juicy burst> <crisp airy whooshes>. 3-5s: the pieces arc outward and fall out of frame, the light warms into
> bright backlight from a large café window with plants, and the bottle settles, the label facing the camera, reading
> "SNOOZZ" and "Ginger Energy". Photorealistic high-speed product commercial, slow motion, macro detail, shallow depth
> of field, the camera eases back slightly. No subtitles. No BGM, no music; only action sounds.

## 5. Variații de testat

- **A (din șablon):** retragere ușoară și lumină din spate de la fereastră.
- **B:** camera rămâne mai jos, aproape de nivelul gâtului, cu o apropiere lentă spre explozie, iar razele de soare
  intră pe diagonală prin stropi.
- **C:** fără retragere: camera stă fixă, cu explozia mai mare, care umple aproape tot cadrul înainte să se limpezească.

## 6. De evitat

Avoid: pieces larger than the bottle neck appearing from nowhere, cartoon or CGI look, plastic-looking fruit, extra
bottles, a changed or misspelled label, text or watermarks added to the frame, faces in the frame.
