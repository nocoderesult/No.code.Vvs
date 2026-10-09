# Romanian: ASR, diacritics, fillers, user-facing text

## Diacritics (always correct before anything is shown or burned in)

- **Correct letters:**
  - Comma-below: ș U+0219, ț U+021B, Ș U+0218, Ț U+021A.
  - Also ă, â, î and Ă, Â, Î.
- **Wrong letters that ASR and old keyboards produce:**
  - Cedilla forms: ş U+015F, ţ U+0163, Ş, Ţ.
  - Whisper sometimes writes Portuguese ã instead of ă.
- **The fix:** `vcommon.fix_ro()` maps all of these and applies NFC. `transcribe.py`, `captions.py` and `plan_cuts.py` all call it. `qc.py` fails the video if any cedilla or ã reaches the captions.
- **Missing diacritics:** the commonest errors are si→și, sa→să, in→în, asa→așa, fara→fără, dupa→după, pana→până, cand→când, daca→dacă, putin→puțin, stiu→știu.
  - `qc.py` lists likely cases.
  - Fix them with `captions.py --replace putin=puțin`, or edit `words.json`.
- **Fonts:** Inter (all weights) and DejaVu cover every Romanian glyph. Python `.upper()` uppercases Romanian correctly (ș→Ș).

## Choosing the ASR model

| Model | Quality on Romanian | Speed (4 CPUs) |
|---|---|---|
| `large-v3-turbo` (default, cached) | Word-perfect sentences with correct diacritics, even at SNR 7.5 dB | RTF ≈ 0.45–0.6 |
| `small` | Many errors. Drops diacritics on noisy audio ("Asta-ti va arat cum sa"). | RTF ≈ 0.4 |
| `large-v3` | Reported about 8% WER on FLEURS-ro [?] | Slower |

Use `small` only for quick drafts.

- **Settings:**
  - `language="ro"`, `beam_size=5`, `condition_on_previous_text=False`.
  - Keep VAD **off**: turbo with VAD dropped the first words ("Salut tuturor").
  - Decode audio with the ffmpeg CLI. `faster_whisper.decode_audio` crashes with PyAV 19.
- **Word timing:**
  - Word starts after a pause come out 0.2–0.6 s early. `transcribe.py` snaps them to the energy onset.
  - Word ends are accurate to about ±0.1 s.
- **Prompt** (`transcribe.RO_PROMPT`): "Vorbim despre editare video, subtitrări și sunet. Ăăă, deci, îîî, practic, așa că, în fine."
  - In A/B tests on Romanian speech it kept the hesitation "Ăă, deci, practic." and "subtitrări" verbatim.
  - A prompt starting with "Salut!" biased the first words.
  - No prompt at all gave "subtitri" and dropped the hesitation.
- **Whisper's own habits:**
  - It writes numbers as digits ("5 minute"). That's fine for captions.
  - It often drops fillers on purpose. A filler it dropped leaves a gap between words; if the gap is 0.25–0.3 s or more, `plan_cuts` cuts it automatically.
- **Hallucinations** (VAD is off, so Whisper "hears" speech in music, ambience and silence): the classic Romanian ones are YouTube outros and subtitle credits — „Vă mulțumim pentru vizionare!”, „Mulțumesc pentru vizionare”, „Abonați-vă”, „Nu uitați să dați like”, „Subtitrare realizată de …”. Measured: a 12 s ambient clip with no speech gave „Să vă mulțumim pentru vizionare!” (5 words in 0.32 s, p 0.74–0.94, two zero-length words, no_speech_prob 0.00 — Whisper's own stats did not catch it). `transcribe.py` screens each segment (speech rate > 6 words/s, ≥ 2 zero-length words, speech energy in < 35% of the span, the phrase list above, Whisper's no_speech/logprob/compression stats): 2+ signals remove it (listed under "removed" in words.txt), 1 signal marks the phrase SUSPECT in phrases.txt. `qc.py` WARNs on captions faster than 6 words/s.
- **Confident errors:** the low-confidence list only catches words Whisper itself doubts. On real speech turbo also writes plausible wrong words with p > 0.97 ('pogneau' for 'porneau', 'nu pot să o ții minte' for 'țin'). Proofread every kept phrase as a Romanian reader before rendering; fix with `--replace` or a `words.json` edit.
- **Punctuation:** Whisper often ends a segment without a full stop and capitalises the next segment, or capitalises after a comma ('roșu, După care'). `vcommon.tidy_transcript` adds the full stop at segment ends and lowercases a common word after a comma; the SRT starts a new entry at each sentence.
- **Clitic tokens:** whisper splits "v-a", "s-a", "n-am", "într-o" into separate tokens ("v" and "-a"). `transcribe.py` merges them back. Check them in captions anyway.
- **Optional extra precision:** WhisperX alignment has a Romanian model (`gigant/romanian-wav2vec2`). It isn't installed; only consider it if word timing is visibly off.

## Fillers

- **Always cut (hesitations):** ăă, ăăă, ăm, ăăm, îî, îm, ââ, âu, mmm, hmm, ee. `plan_cuts` also catches any repeated vowel (uuu, aaa, eee) with a regex.
- **Cut only when the whole phrase is made of them** (so meaningful uses survive): deci, practic, adică, gen, bine, na, păi, știi, zic, uite, bun, ok/okei, cumva, efectiv, oricum, de fapt, în fine, pur și simplu, ideea e că.
  - To always keep a word: `--keep-words practic`.
  - To cut a single in-sentence filler: `--cut 0:12.40-12.95`, using times from `words.json`.
- **Retakes** (false starts, "eu, eu am…"):
  - When the first 6 words of a phrase match the next phrase (difflib ratio ≥ 0.72), the earlier phrase is dropped.
  - Always read `phrases.txt`: two takes that start differently aren't caught automatically. Use `--drop` for those.
- **A lone "a", "e" or "o" is never auto-cut.** These are real words in Romanian.

## Talking to the user (always in Romanian, short, friendly, concrete)

### Plan + questions (ONE message, after transcribing and planning the cuts)

On a phone every round-trip costs minutes, so the plan and the questions go in a single message, with defaults
marked, and a plain "ok" starts the render. Fill in the real numbers from `phrases.txt`:

> Am primit clipurile (2 fișiere, 3:12 în total) și le-am ascultat pe tot. **Planul meu:**
> încep direct cu „…” (cel mai puternic moment), apoi pașii 1–3, și închei cu „…”. Tai pauzele și „ăăă”-urile: din 3:12 rămân ~41 s. Hook sus în primele 3 s: **„3 GREȘELI LA MONTAJ”**. Sunetul îl curăț și îl aduc la -14 LUFS.
>
> Scrie **„ok”** și pornesc, sau schimbă doar ce vrei (răspunde cu numărul):
> 1. **Format:** Reels + TikTok + Shorts, vertical 9:16 *(implicit)* · YouTube 16:9 · ambele
> 2. **Durată:** ~41 s, ca mai sus *(implicit)* · mai scurt (~30 s) · tot ce e bun
> 3. **Subtitrări:** cuvânt cu cuvânt, galben pe cuvântul activ *(implicit)* · cu cutie colorată · un cuvânt mare · simple · fără
> 4. **Muzică:** fără *(implicit; pui sunet trending direct în aplicație)* · am o piesă (trimite fișierul)
> 5. **Text de final pe ecran (CTA):** fără *(implicit)* · „SALVEAZĂ-L PENTRU MAI TÂRZIU” · „URMĂREȘTE PENTRU PARTEA 2” · scrie-l tu
> 6. **Poze/clipuri de inserat (B-roll)?** Ar merge bine la: 0:08 (aplicația pe ecran), 0:19 (rezultatul), 0:31 (…). Trimite-le dacă le ai; altfel rămâne doar fața ta *(implicit)*
> 7. **Copertă:** fac eu una din cel mai bun cadru, cu titlul hook-ului *(implicit)* · fără
> 8. **Pachet pentru DaVinci Resolve** (ca să mai lucrezi tu pe montaj): nu *(implicit)* · da

If the user already said "fă tu tot" / "cum crezi tu", skip the questions: send the plan as a statement and start.
For **ambele**, say that the 16:9 version keeps more (e.g. "~2:30, fără tăieturi agresive") and render both.

### Delivery message

> **Gata!** Video-ul final: 41 s, 1080×1920, sunet -14 LUFS, subtitrări verificate (diacritice ok).
> Ce am făcut: … (3–5 puncte)
> Atașat: final.mp4 (12 MB) · cover_9x16.jpg · final.srt · davinci.zip (montajul pentru DaVinci Resolve + instrucțiuni, 9 MB)
> Vrei modificări? Spune-mi ce schimb (ex.: „scoate partea cu…”, „hook-ul altfel”, „subtitrări mai mici”).
> Vrei și textul pentru postare (descriere + hashtag-uri)? *(if yes: caption-writer skill)*

### Recording tips for next time

Give these only when the footage showed a problem:
- HDR Video OFF.
- 4K30 or 1080p30.
- Lock exposure and focus.
- Light from the front or side (a window).
- A lapel mic, or the phone at most 50 cm from the mouth.
- 2 s of silence before speaking.
