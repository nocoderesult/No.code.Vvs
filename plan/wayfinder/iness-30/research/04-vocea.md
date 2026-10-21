# Cercetare: ce voce română are Iness?

Tichet: [issues/04-vocea.md](../issues/04-vocea.md) · verificat live pe 21.10.2026

## Pe scurt

- **ElevenLabs rămâne alegerea bună**, dar pe modelul nou **Eleven v4** (lansat pe 28.09.2026), nu pe v3. Vocea o creăm cu **Voice Design** și o salvăm în My Voices. Planul **Creator** costă 11 $/lună (22 $ în prima lună) și include licență comercială și un clon profesional, dacă vrem să fixăm vocea mai târziu.
- **Vocea nativă din uneltele video nu știe română.** Kling 3.0 vorbește 5 limbi, Veo 3.1 e evaluat doar pe engleză, iar pentru Seedance 2.0 nu există o listă oficială. Deci vocea vine din ElevenLabs, iar buzele se sincronizează **după audio** (Kling Lip Sync sau Kling Avatar 2.0).
- **„Promptul de voce existent” nu există în plan.** În `PLAN_COMPLET.md` scrie doar „ElevenLabs (vocea caracterului)” (r. 250) și „Vocea «Iness» trebuie salvată” (r. 86). Nu am găsit niciun text de prompt. Mai jos propun unul.

## 1. Opțiuni pentru o voce feminină proprie, mereu aceeași

| Opțiune | Română? | Voce proprie, stabilă | Notă |
|---|---|---|---|
| **ElevenLabs v4 + Voice Design** | da (`ro`), v4 are 90+ limbi | descrii vocea în text → primești 3 variante → o salvezi în My Voices | recomandat |
| ElevenLabs v3 | da, 70+ limbi | la fel | e marcat acum „previous generation” |
| ElevenLabs Multilingual v2 | da, 29 de limbi | la fel | cel mai stabil la texte lungi, dar mai puțin expresiv |
| ElevenLabs Professional Voice Clone | da | cea mai constantă, conform ElevenLabs | cere o înregistrare lungă cu o voce reală. Pentru o voce sintetică ar trebui să clonăm chiar ieșirea din Voice Design, ceea ce e de verificat |
| Gemini 3.8 Flash TTS | da (listat explicit) | are voice design (`type="prompted"`). O voce salvată expiră după 1 an | foarte ieftin. Merge doar prin API, fără interfață comodă de creator |
| HeyGen | 175+ limbi pe planurile plătite | are clonare de voce | 29 $/lună. Util mai ales ca unealtă de lip-sync, nu ca sursă de voce |
| Voce nativă Kling / Veo / Seedance | **nu** (vezi §4) | Kling poate lega o voce de un personaj („Element Voice Control”) | nu se poate folosi pentru română |

Surse:
- [modelele ElevenLabs](https://elevenlabs.io/docs/models)
- [Eleven v4](https://elevenlabs.io/blog/eleven-v4)
- [Voice Design](https://elevenlabs.io/docs/product-guides/voices/voice-design)
- [Voci: IVC și PVC](https://elevenlabs.io/docs/overview/capabilities/voices)
- [Gemini TTS](https://ai.google.dev/gemini-api/docs/speech-generation)
- [prețuri HeyGen](https://www.heygen.com/pricing)

## 2. Calitatea în română (ce știm și ce testăm)

**Din surse:**
- Româna (`ro`) e suportată de v4, v3, Multilingual v2 și Flash v2.5 ([models](https://elevenlabs.io/docs/models)).
- Pentru v4, ElevenLabs promite că urmează mai bine audio tag-urile (emoție, pauze, râs) și că pronunția prin IPA s-a îmbunătățit ([blog v4](https://elevenlabs.io/blog/eleven-v4)).
- Ghidul Voice Design spune:
  - limba și varianta regională se scriu **în prima propoziție**, ca vocea să nu alunece spre alt accent;
  - nu folosești cuvântul „accent” când te referi la intonație;
  - textul de previzualizare trebuie să fie lung și scris în limba vocii ([Voice Design](https://elevenlabs.io/docs/product-guides/voices/voice-design)).
- Clasamentul „primul în Artificial Analysis” și preferința de ~75% sunt cifre date de ElevenLabs, nu teste independente ([blog v4](https://elevenlabs.io/blog/eleven-v4)).

**De testat de noi** (nu am găsit surse primare despre româna din v4):
1. **Diacriticele.** Scriem ș/ț cu virgulă dedesubt (U+0219/U+021B), nu cu sedilă (ş/ţ). Ascultăm „și”, „ține”, „înțeleg”, „mâine”.
2. **Cifrele și prețurile** le scriem în litere („nouăzeci și nouă de euro”).
3. **Ritmul.** Un reel de ~15 s are 35–45 de cuvinte. Testăm v4 față de Multilingual v2 pe aceeași replică și verificăm să nu sune cu intonație „de engleză”.
4. **Tag-urile de emoție** ([laughs], [sarcastic]) pe umorul „o AI care trăiește în România”.

## 3. Prețul pe lună pentru ~20 de reels de ~15 s

**Calculul:**
- 15 s de voce în română ≈ 220–250 de caractere, deci 20 de reels ≈ 5 000 de caractere.
- Cu 3–4 variante pe replică ajungem la ~15–20 de mii de caractere pe lună.
- Pe planuri, prețul se calculează în credite. Starter are 30 de mii de credite ≈ ~30 de minute de TTS, adică ~1 credit pe caracter ([pricing](https://elevenlabs.io/pricing)).

| Plan ElevenLabs | Preț/lună | Credite | Ajunge? | Licență comercială | PVC |
|---|---|---|---|---|---|
| Free | 0 $ | 10 mii | nu | **nu** | nu |
| Starter | 6 $ | 30 mii | da, la limită cu reluări | da | nu |
| **Creator** | **11 $** (22 $ în prima lună) | 121 mii | da, cu rezervă mare | da | 1 |
| Pro | 99 $ | 600 mii | prea mult | da | 1 |

Sursă: [elevenlabs.io/pricing](https://elevenlabs.io/pricing). Prin API, v4, v3 și Multilingual v2 costă 0,08 $ la 1 000 de caractere, deci ~1,6 $ pentru 20 de mii de caractere ([pricing/api](https://elevenlabs.io/pricing/api)).

**Ce mai costă:**
- **Gemini 3.8 Flash TTS:** 9 $ la 1 milion de tokeni audio până la 31.12.2026, adică ~0,002 $ la 10 s, deci câțiva cenți pe lună. Pe planul gratuit, datele se folosesc pentru antrenare ([pricing Gemini](https://ai.google.dev/gemini-api/docs/pricing)).
- **Kling Avatar 2.0:** 4 credite/s pe Standard și 8 credite/s pe Professional ([ghid Avatar 2.0](https://kling.ai/quickstart/kling-ai-avatar-2-user-guide)). **Kling Lip Sync:** 5 credite la 5 s ([ghid Lip Sync](https://kling.ai/quickstart/ai-lip-sync-guide)). Prețul abonamentului Kling nu l-am putut citi: pagina de membership s-a încărcat goală.

## 4. Cum ajunge vocea în lip-sync

**Audio nativ (vocea generată de unealta video):**
- **Kling 3.0 Omni** vorbește nativ chineză, engleză, japoneză, coreeană și spaniolă ([Kling blog](https://kling.ai/blog/kling-video-3-omni-native-lip-sync-audio-guide)). Româna lipsește.
- **Veo 3.1:** „English (EN) is fully supported, but other languages have not been evaluated”. Nu primește audio ca input ([Gemini API Veo](https://ai.google.dev/gemini-api/docs/veo)). În plus, modelele preview Veo 3.1 se închid pe **22.10.2026**, în aceeași sursă.
- **Seedance 2.0** generează audio și video împreună și acceptă audio ca referință ([seed.bytedance.com](https://seed.bytedance.com/en/seedance2_0)). Nu există o listă oficială de limbi. Sursele terțe vorbesc de „8+ limbi”, cu chineza și engleza cele mai bune ([Hedra](https://www.hedra.com/models/video/bytedance/seedance-20)). Româna nu e confirmată.

**Lip-sync după audio (recomandat):**
- **Kling Lip Sync:** generezi clipul cu Iness, apoi încarci fișierul de voce. Dacă audio e mai lung decât clipul, se taie ([ghid](https://kling.ai/quickstart/ai-lip-sync-guide)).
- **Kling Avatar 2.0:** pornește de la o poză (care e și primul cadru) plus audio încărcat. Prin API acceptă mp3/wav/m4a/aac între 2 și 300 s ([ghid](https://kling.ai/quickstart/kling-ai-avatar-2-user-guide), [API](https://kling.ai/document-api/apiReference/model/avatar)). Lista de limbi afișată (EN, JA, KO, ZH) nu spune clar dacă e valabilă și pentru audio încărcat. Sincronizarea se face după sunet, deci ar trebui să meargă și în română, dar **trebuie testat**.
- **Alternative:** HeyGen (avatar din poză, 29 $/lună) sau LatentSync pe pod (deja în `PLAN_COMPLET.md`, r. 250; licența e de verificat).

**Rețeta propusă:**
1. Scriem replica în română.
2. Generăm vocea în ElevenLabs v4, cu vocea „Iness” salvată.
3. Generăm clipul în Kling: cadru cu fața completă, fără replică în prompt.
4. Facem lip-sync în Kling cu audio-ul încărcat.
5. Montăm în CapCut.

## 5. Drepturi comerciale

- **ElevenLabs:**
  - planul Free nu are licență comercială și cere atribuire;
  - toate planurile plătite includ licență comercială, **cu excepția „Beta Services”**, al căror conținut nu se poate folosi comercial;
  - ce generezi cât ai abonament rămâne licențiat și după ce renunți la el.

  Surse: [help ElevenLabs](https://elevenlabs.io/docs/help-center/legal/can-i-publish-the-content-i-generate-on-the-platform), [Terms](https://elevenlabs.io/terms-of-use). Înainte de lansare, verificăm că v4 și Voice Design nu sunt marcate „beta” în contul nostru. Pagina de API îl arată pe v4 doar ca „New” ([pricing/api](https://elevenlabs.io/pricing/api)).
- **Kling:** planul Basic e „not for commercial use”. Pentru 1080p ai nevoie de Standard sau mai sus ([Kling blog](https://kling.ai/blog/kling-video-3-omni-native-lip-sync-audio-guide)).
- **Vocea e sintetică (Voice Design), nu a unei persoane reale.** Asta respectă regula „fără persoane reale” din hartă.

## 6. E încă bun promptul din plan?

Nu există un prompt propriu-zis, doar alegerea „ElevenLabs → lip-sync (HeyGen / LatentSync)”. Direcția rămâne corectă, cu trei ajustări:
- folosim **v4**, nu v3;
- facem lip-sync în **Kling, după audio**, ca să nu mai plătim o unealtă în plus;
- **nu ne bazăm pe vocea nativă** din Kling/Veo/Seedance pentru română.

**Prompt propus pentru Voice Design** (în engleză, pe structura din ghid: limbă → gen/vârstă → calitate → persona → emoție → timbru/ritm):

> Native Romanian speaker from Bucharest, standard Romanian pronunciation. Female, late twenties. Studio-quality, close-mic recording. A warm, witty lifestyle creator who talks to camera like texting a close friend. Playful and self-ironic, light smile in the voice. Medium-low pitch, smooth slightly husky timbre, clear diction, natural conversational pace with quick comic pauses.

**Text de previzualizare** (în română, lung, pe tonul vocii):

> Bună, sunt Iness. Da, sunt făcută de AI, dar trăiesc în România, așa că am învățat deja trei lucruri: că „vin în cinci minute” înseamnă o oră, că mama are mereu dreptate și că nu ieși din casă fără o geacă în plus.

Generăm 2–3 runde, alegem o variantă și o salvăm ca „Iness”. Apoi notăm în fișa personajului modelul, setările (stability, guidance) și ID-ul vocii.

## Recomandare

1. **ElevenLabs Creator (11 $/lună, 22 $ în prima lună)** + Eleven v4 + Voice Design, cu vocea „Iness” salvată și setările notate. Costul ajunge la ~2–5 % din bugetul de 150–300 €.
2. **Lip-sync după audio în Kling** (Lip Sync sau Avatar 2.0). Înainte de 26.10 facem un test pe 3 replici în română. Dacă buzele nu se potrivesc, trecem la HeyGen sau LatentSync.
3. **Rezervă ieftină:** Gemini 3.8 Flash TTS cu voice design, doar dacă ElevenLabs sună „străin” în română.
4. **Înainte de lansare:** verificăm că nimic din ce folosim nu e „beta” în ElevenLabs și că avem plan Kling Standard sau mai sus.
