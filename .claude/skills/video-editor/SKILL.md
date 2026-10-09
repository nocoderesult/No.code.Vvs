---
name: video-editor
description: Expert end-to-end video editor ("cap-coadă") for a Romanian creator. It turns raw uploaded clips into a finished, platform-ready video with ffmpeg/Python in a cloud container (no GPU). Transcription with correct diacritics, silence/filler/retake removal, story order and hook, 9:16 face-tracked reframing, word-by-word captions, voice cleanup and loudness, music ducking, B-roll, cover, phone HDR/VFR fixes, self-QC, and a DaVinci Resolve (free) package. Use when the user uploads or points to video/audio footage, or asks to edit, cut, trim, caption, reframe, master or export footage they have (Reel, TikTok, Short, YouTube). Romanian triggers include „am încărcat clipurile”, „editează / montează / taie video-ul”, „fă-mi montajul”, „cap-coadă”, „scoate pauzele / ăăă-urile”, „pune subtitrări pe clip”, „fă-l vertical”, „curăță sunetul”, „export pentru DaVinci”. Not for scripts, post captions or ideas without footage (use reel-script / caption-writer).
---

# Video editor: cap-coadă (end to end)

You are the user's editor. They upload raw clips (Romanian talking head, phone footage). You deliver a **finished MP4** at expert level, plus SRT, a cover and an optional DaVinci Resolve package. They use the FREE Resolve 21 on a Mac M4, which has no scripting, so any Resolve work is manual import on their side.

**Ground rules:**
- **Talk to the user in Romanian:** short, warm, concrete. The templates are in `reference/romanian.md`.
- **Look before you decide.** Make a contact sheet and Read it; read the transcript. Never edit blind.
- **Never deliver without self-QC.** Run `qc.py`, then LOOK at the sheets.
- **Keep the originals untouched.** Work in a folder outside the git repo, e.g. `<scratchpad>/edit/<proiect>`. **Never `git add` media.**
- **Diacritics are law:** ă â î ș ț with comma-below; ş/ţ/ã are errors.
- **Give realistic times.** Turbo transcription runs at about 0.4–0.6× clip length. Render runs at about 1× output length for 1080×1920 (3–4× slower for HDR 4K). A 1-minute clip takes about 2–4 minutes end to end.

**Shell setup — variables do NOT survive between Bash calls** (each call is a fresh shell, and a subagent's cwd resets). Find the scripts folder once (`git rev-parse --show-toplevel` from the repo, or wherever this SKILL.md lives), then start **every** Bash call with the same absolute definitions:

```bash
S=/abs/path/to/.claude/skills/video-editor/scripts; OUT=<scratchpad>/edit/<proiect>; W=$OUT/work; mkdir -p $W
```

Never use a relative `S=.claude/...` (it breaks when the cwd changes) and never rely on a variable set in an earlier call (`python3 $S/probe.py` becomes `python3 /probe.py`). Quote paths that contain spaces or diacritics. All scripts have `--help` and fail with clear `ERROR:` lines. The pipeline reuses a cached transcript or face track only from `$OUT/work`, so keep intake outputs there.

## 1. Intake

1. **Find the files.** If the user didn't give paths, run `python3 $S/probe.py --find`. It searches /home/user, ~, /tmp, /mnt and similar for media changed in the last 72 h. If nothing turns up, ask them to attach the clips, or give a direct download link (then fetch it with `curl -L`).
2. **Probe them:** `python3 $S/probe.py clip1.mov clip2.mov --loudness`. Note the issues: HDR, VFR, rotation, mono, 44.1 kHz, no audio, video starting after the audio, low resolution (upscale > 2× looks soft). The scripts fix these automatically; mention only what matters to the user (for example "filmat în HDR – îl convertesc").
3. **Look at the footage:** `python3 $S/contact_sheet.py clip.mov -o $W/sheet_clip.jpg`, then **Read the jpg**. Use `--scenes` for multi-shot or B-roll footage. Judge framing and where the face is (a face filling the frame becomes `--reframe wide` automatically), light, shake, background, number of people, 16:9 or 9:16.
4. **Transcribe:** `python3 $S/transcribe.py clip1.mov clip2.mov -o $W/words.json`. Large-v3-turbo with Romanian defaults. Give the clips in story order, with the same paths you will later pass to the pipeline. Whisper invents text on music/ambience/silence (classic: "Vă mulțumim pentru vizionare!"); the script screens segments and lists what it removed at the bottom of `$W/words.txt`. Read `$W/words.txt` for the content, the strongest line (hook), the CTA, repeated takes and the low-confidence words.
5. **Plan cuts:** `python3 $S/plan_cuts.py $W/words.json -o $W/cuts.json --pace tight` (`--pace normal` for 16:9; the pipeline defaults to the same). Read `$W/phrases.txt`: numbered phrases P1…Pn (one per sentence; long ones split at a comma/pause) with status KEEP / FILLER / RETAKE, flags `SUSPECT` (possible hallucination: listen, `--drop` it if not real) and `NO-SPEECH` (clip without words, kept whole), the output order, the zoom-cut points and `WARN` lines (unused clips, length over the platform max).
6. **Proofread (mandatory).** Read every KEEP phrase you will use **as a Romanian proofreader**. The low-confidence list misses confident errors (measured: 'pogneau' for 'porneau' at p=0.98, 'nu pot să o ții minte' for 'țin' at p=0.99). Fix misheard words with `--replace greșit=corect` (whole word, everywhere) or by editing the `"w"` fields of `$W/words.json` with a small Python snippet. Burned captions are UPPERCASE, so casing errors only show in the SRT and in Resolve.
7. **ONE message to the user** (template in `reference/romanian.md`): your proposed plan (opening line, structure, length "din 3:12 rămân ~41 s", hook text, look) **plus** numbered options with defaults, so that "ok" starts the render: format, length, caption style, music, on-screen CTA / end card, B-roll or photos to insert (list 3–5 moments where B-roll would help: output time + what to show), cover, DaVinci package (da/nu).
   - If the user said "fă tu tot" / "cum crezi tu", don't wait: state the assumptions and render.
   - **Defaults:** 9:16 for Reels+TikTok+Shorts, 30–45 s, karaoke captions in yellow, no music, your hook, no on-screen CTA unless they name one, cover on, no DaVinci package, −14 LUFS.

## 2. Editorial decisions (from phrases.txt)

The craft and story structure are in `reference/craft.md` §1, §2 and §6.
- **Cold open:** put the strongest line first: `--cold-open P9`, or the full order with `--select P9,P1-P4,P7,P12`.
- **Hit the target length:** drop weak or repeated phrases with `--drop P5,P6`. Over 180 s is not a Reel/Short (QC FAILs it).
- **Loop:** if the last line leads back into the first, add `--loop` (music stops hard on the last frame).
- **Overrides:** `--restore P3` (wrongly flagged filler/retake), `--keep-words practic`, `--cut-range 0:12.40-12.95` (one in-sentence stumble; times from `$W/words.json`), `--add-range` (force-keep). These are the pipeline's names; on `plan_cuts.py` directly they are `--cut` / `--add`.
- **Phrase IDs depend on `--pace`.** Re-read `phrases.txt` after changing the pace.
- **Hook text:** 3–7 words, the payoff or a curiosity gap, Romanian with diacritics. **CTA** (optional): 2–5 words ("SALVEAZĂ-L PENTRU MAI TÂRZIU", "URMĂREȘTE PENTRU PARTEA 2").

## 3. Execute

**One command does it all** (cached transcript and face tracks, so re-running after a change is cheap):

```bash
python3 $S/pipeline.py clip1.mov clip2.mov -o $OUT --format reels \
    --select P9,P1-P4,P7,P12 --hook "3 GREȘELI LA MONTAJ" [--cta "SALVEAZĂ-L"] [--music track.mp3] [--resolve]
```

**Main options:**

| Need | Option |
|---|---|
| Format | `--format reels\|tiktok\|shorts\|vertical` (1080×1920), `youtube` (1920×1080, YouTube GOP), `square`, `portrait` (4:5), `WxH`, `source` |
| Captions | `--captions karaoke` (default vertical) \| `box` (busy backgrounds) \| `pop` (one big word) \| `clean` (sentence subtitles, 16:9) \| `none` (default for 16:9; the SRT is always written). `--accent "#2EE66B"`, `--replace "Cloud=Claude"` |
| Titles | `--hook "…"` (frame 0 to `--hook-dur` 3 s), `--cta "…"` (end card for the last `--cta-dur` 3 s). Both are placed clear of the face and of the caption line, shrunk if needed |
| Cutting | `--cut auto` (transcript) \| `silence` (energy only) \| `none` (keep all). `--pace`, `--select`, `--drop`, `--restore`, `--cold-open`, `--keep-words`, `--cut-range 0:S-E`, `--add-range` |
| Picture | `--reframe auto` (face track; `wide` = smaller face + blurred fill when the face would fill > 40% of the 9:16 crop; blur fill without a face) \| `track` \| `wide` \| `center` \| `blur` \| `fit`. `--punch 1.12` (every 2nd shot; default 1.12 vertical / 1.08 16:9; auto-capped at 1.05 when the source is upscaled > 2×), `--zoom-cuts auto` (long takes split into alternating 100%/punch shots so the picture changes every ≤ 3.5 s; on for vertical), `--push 1.06`, `--grade natural\|punchy\|bright\|none`, `--stabilize`, `--vdenoise` |
| B-roll | `--broll broll.json`: `[{"path":"b.mp4","at":3.2,"dur":2,"in":5},{"path":"poza.jpg","at":9,"dur":2.5,"zoom":1.08}]`. `at` is in OUTPUT seconds; the voice keeps playing underneath. B-roll clips are never main inputs. |
| Audio | `--music file` (bed `--music-under 15` dB under the voice while talking, `--duck 8`), `--loop` (music cut on the last frame instead of a fade), `--sfx` (synthesized pop on hook/CTA, whoosh on B-roll, ~20 dB under the voice), `--denoise auto\|rnnoise\|afftdn\|off`, `--target -14` |
| Delivery | `--resolve` (DaVinci package + zip), `--alpha` (captions overlay MOV), `--mac-dir`, `--clean` (extra render without captions), `--name`, `--no-cover`, `--cover-title`, `--crf` (default 20 social / 18 YouTube) |
| Both 9:16 and 16:9 ("ambele") | Run the pipeline twice into two `$OUT` folders with the same clips; the second run takes `--words $OUT1/work/words.json` (no second transcription). Phrase IDs depend on `--pace`: pass the same `--pace` to both runs, or re-read the second run's `phrases.txt` before choosing `--select`. |

The pipeline also writes `cover_9x16.jpg` (vertical: best face frame + title inside the 3:4 profile-grid area) or `thumb_16x9.jpg` (16:9), `cover_frame.jpg` (no text), `chapters_draft.txt` (16:9 only) and `summary.json`. At the end it prints every WARN collected on the way (unused clips, SUSPECT phrases, upscaling, QC) — read each one.

**Manual chain** (use it to tweak one step; the pipeline prints every command):

```
transcribe.py → plan_cuts.py → reframe.py (per source) → captions.py (--avoid face band) →
render_cuts.py --audio-only cut.wav → audio_master.py cut.wav -o mix.wav [--music] →
render_cuts.py cuts.json -o final.mp4 --format reels --track 0=track_0.json --ass captions.ass --audio mix.wav →
qc.py → cover.py → export_resolve.py
```

`captions.py` exits 3 when a caption or title leaves the safe zone or a caption sits under the hook/CTA; fix it (shorter hook, `--hook-y`, `--size`, `--reframe wide`) rather than passing `--no-check`.

## 4. Self-QC (mandatory before delivery)

`pipeline.py` runs `qc.py`. After any manual render, run it yourself:

```bash
python3 $S/qc.py $OUT/final.mp4 --format reels --cuts $W/cuts.json --ass $W/captions.ass --words $W/words.json --sheets $OUT/qc
```

1. **Fix every FAIL.** Read each WARN and decide.

   | Check | Expected | Level |
   |---|---|---|
   | Container / codec | Faststart, H.264 High yuv420p, CFR, BT.709, AAC 48 kHz stereo | FAIL / WARN |
   | Durations | Video = audio within 1 frame (the A/V sync proxy); duration = cut list | FAIL |
   | Platform max length | Reels/Shorts ≤ 180 s, TikTok ≤ 600 s | FAIL |
   | Loudness | −14 ±1 LUFS, true peak ≤ −1 dBTP | FAIL |
   | Loudness range | LRA ≤ 11 | WARN |
   | Silences / black / frozen | None over 0.9 s / none | WARN |
   | Longest shot without a visual change | ≤ 4 s vertical, ≤ 15 s 16:9 | WARN |
   | Caption layout | Every caption/title box inside the safe zone, no caption under the hook/CTA | FAIL |
   | Caption text | No ş/ţ/ã (FAIL); likely missing diacritics (WARN; hyphenated clitics s-a, n-a are correct) | |
   | Caption speech rate | ≤ 6 words/s (faster = probably a Whisper hallucination) | WARN |

2. **Look at the sheets.**
   - `qc/qc_sheet.jpg` has **true colours** (safe area as thin lines). Judge framing and colour **only here**: face framed with headroom, crop doesn't cut chin or forehead, natural skin (no orange or grey), no blown highlights, punch-ins and zoom cuts look intentional, no black or garbage frames.
   - `qc/qc_captions.jpg` shades the platform UI red/orange and draws the measured caption boxes (cyan) and hook/CTA boxes (magenta); it includes the last frames of the hook and the CTA's first frames. Check: captions clear of eyes and mouth and of the hook, inside the safe area, no glued or overlapping words, diacritics render, the hook is readable on frame 0. **Never judge colour on this sheet** — the shading tints it.
   - The cover (`cover_9x16.jpg` / `thumb_16x9.jpg`): eyes open, sharp, title readable and clear of the face. Re-run `cover.py --at SECONDS` to pick another moment.
3. **Read the caption vocabulary** that qc prints. Look for misspelled Romanian words, names and brands. Fix and re-render.
4. **Check the duration** against the user's target.
5. If you changed anything, re-run QC. Only deliver at 0 FAIL, and after you have looked at the sheets.

**DaVinci package check:** `export_resolve.py` parses the written FCPXML/EDL back with exact fractions (sequence frame rate, every clip's offset/start/duration, asset start vs the media's timecode). On any mismatch it prints `ERROR: timeline check failed` and exits 4, so the pipeline stops before DONE. Don't ship that package: deliver the MP4 and SRT without `--resolve`, tell the user the Resolve package will follow, and fix the exporter.

## 5. Delivery

- **Send the files** with **SendUserFile**: the final MP4, the cover, and the SRT if the user wants captions on YouTube or in Resolve. With `--resolve`, also send `davinci.zip` (timeline FCPXML/EDL/OTIO, SRT, voice/music/sfx stems, CFR copies of VFR clips, `CITESTE-MA_DaVinci.txt` with Romanian steps; the final MP4 is not inside — the user already has it).
  - State the file sizes (the pipeline prints them). Social renders are CRF 20 capped at 10 Mbps, so at most ~1.25 MB per second (a 40 s reel from noisy 720p phone footage measured 49 MB; clean footage is far smaller). If a send fails because the file is too large, re-render with `--crf 23` and say so.
- **Write the message in Romanian** (template in `reference/romanian.md`): what you did (3–5 bullets), specs (length, format, −14 LUFS), assumptions, the file list with sizes, an offer of specific tweaks, recording tips only if the footage had problems. For 16:9, rewrite `chapters_draft.txt` into real YouTube chapters (first at 0:00, ≥ 3, each ≥ 10 s) and propose a title + description.
- **Offer the post text:** "Vrei și textul pentru postare?" — if yes, use the caption-writer skill.
- **DaVinci instructions, in short** (full version in `reference/davinci-resolve.md`):
  1. Copy the original clips to `/Users/Shared/Claude-Edit/` (Cmd+Shift+G in Finder), keeping the same names.
  2. Resolve → File → Import → Timeline… → `timeline.fcpxml`.
  3. Clips that show offline: Relink Selected Clips.
  4. For vertical: Timeline Settings → 1080×1920 → "Scale full frame with crop", then Position X per clip (starting values are listed in CITESTE-MA).
  5. Subtitles: File → Import → Subtitle → `subtitles.srt`.
  6. Mastered sound: stems on A2/A3 (A4 sfx), and mute A1.
- **Iterate.** On feedback, change only what was asked: re-plan, re-caption or re-render. The pipeline reuses the cached transcript and tracks. Re-run QC, then re-deliver.

## 6. Craft cheat-sheet (numbers)

Details and sources are in `reference/craft.md` and `reference/platforms.md`.

- **Hook:** frame 0 is already active (a face talking or the payoff). Hook text of 3–7 words visible from frame 0 (92 px Inter Black, white boxes, top of the safe area; shrinks rather than covering the eyes or the captions). Something visually changes by 1.2–2.0 s (the first zoom cut lands there). Cold-open on the payoff; no "Salut, bine ați venit".
- **Pacing:**
  - Short-form: cut pauses over 0.25–0.35 s; keep 0.05–0.15 s padding.
  - Change something every 2–4 s (zoom cuts every ≤ 3.5 s inside long takes); shots average 1.5–3 s.
  - 16:9: change every 5–15 s and re-hook every 60–90 s. Don't over-cut for audiences aged 25+.
- **Framing (16:9 → 9:16):** face about 30–38% of the frame height. A close-up selfie (face > 40% of the crop, upscale ~2.7×) switches to `wide`: face at ~30% of the height at 0.40 H over a blurred fill, captions under the chin.
- **Punch-ins:** 100% ↔ 112% on alternating shots, anchored on the face (≤ 105% when the source is already upscaled > 2×); 130–140% for emphasis; slow push to 106% over 3–6 s on long takes.
- **Captions (1080×1920):**
  - Inter Black, 80 px (60–90 range), white, 6 px black outline plus shadow. The active word is yellow #FFD400 and pops to 110%.
  - 1–3 words, ≤ 14 characters, ONE line per chunk; a single long word (NECONSTITUȚIONALITATEA) is drawn smaller to fit.
  - Centre y ≈ 1130; text x ≈ 200–880. Below the chin when it fits, above the brows otherwise.
  - Each word appears at onset and lasts ≥ 0.15 s, with no flicker. Chunks break at cuts, punctuation and Whisper segment ends.
  - For 16:9: an SRT for YouTube CC (2 × 42 characters, ≤ 6 s, one sentence per entry). Optional `clean` burn-in at 56 px in sentence case.
- **Safe zones (1080×1920):** Reels top 269, bottom 672, sides 65 · TikTok top 240, bottom 660, sides 120 (+ right 300 px clear below y = 840) · Shorts top 288, bottom 672, left 48, right 192 · **Universal box: x 120–888, y 290–1240.** Cover title inside the profile-grid 3:4 area (y 240–1680).
- **Audio:**
  - HPF 80 → RNNoise → −2 dB at 250 Hz → +2 dB at 3.5 kHz → de-ess → 3:1 compression → expander → (slow leveler when LRA is high) → loudness. The chain's delay (RNNoise 12 ms, afftdn 27 ms) is measured and removed.
  - Deliver −14 LUFS integrated, ≤ −1.5 dBTP before AAC, LRA ≤ 11.
  - Music: instrumental, 100–130 BPM for upbeat. The bed sits 15 dB under the voice while talking and rises ~8 dB in gaps (80 ms attack, 450 ms release). End on a button (`--loop`) or a 1.5 s fade.
  - Sound effects sparingly, ~20 dB under the voice. On Instagram/TikTok, trending in-app audio is often better than burned-in music. Shorts over 60 s with a Content ID music claim are blocked worldwide.
- **Export:**
  - Social (Reels/TikTok/Shorts): 1080×1920 H.264 High 4.2, yuv420p, CFR at the native rate, CRF 20 with maxrate 10M (14M at 60 fps), GOP 2 s, BT.709 TV range, AAC 48 kHz 256k, faststart. The apps re-encode to a few Mbps anyway.
  - YouTube: CRF 18 with maxrate 16M (20M at 60 fps), closed GOP of half the frame rate.
  - Upload H.264, not HEVC. TikTok compresses 4K to 1080p.
- **Lengths:** Reels 3 min in-app · TikTok 10 min in-app · Shorts ≤ 3 min, vertical or square only · sweet spot 20–45 s.
- **Colour:** HDR phone footage is tone-mapped (npl 203 + mobius). Grade gently (contrast +4–8%, saturation +6–15%). No extra sharpening. Advise HDR off, 4K30 or 1080p30, exposure locked, window light in front.

## 7. Gotchas (all hit in testing)

**Transcription:**
- Use turbo, not small, for Romanian: small drops diacritics on noisy audio.
- Keep VAD off (it ate first words); hallucinations are screened instead (speech rate, zero-length words, energy, known outro phrases, Whisper's no_speech/logprob). Ambient/music clips must come out with no words.
- Whisper starts after pauses are 0.2–0.6 s early; `transcribe.py` snaps them to the onset.
- Whisper splits clitics ("v" + "-a"), writes "ã", leaves sentences without full stops and capitalises after commas; all fixed.
- `faster_whisper.decode_audio` crashes with PyAV 19; the ffmpeg CLI is used instead.

**Cutting and rendering:**
- Cut with frame-aligned trim/atrim + concat in one graph. Never per-segment AAC files + concat demuxer (up to 198 ms drift) and never `select`/`between` (up to 185 ms).
- Video that starts after the audio (start_time 0.2 vs 0.0) is padded with `fps=…:start_time=0`, or it plays early; the render asserts video and audio lengths match.
- Reordered segments need a separate input per run; `render_cuts` does this.
- A project folder with an apostrophe ("Reel lui Ion's") broke the `subtitles=` filter; filter files are copied to a plain temp path.
- `amix` needs `normalize=0`. Ducking uses an offline gain curve, not `sidechaincompress`.
- Two-pass loudnorm falls back to dynamic mode (uneven gain) on big level swings; the leveler + static-gain fallback avoid it.
- `arnndn` needs 48 kHz input. zscale fails on untagged colour; `setparams` first. swscale assumes BT.601 for untagged HD.
- The punch-in crop needs `setsar=1` before concat. zoompan jitters; use static crops or `perspective` with `eval=frame`.

**Captions:**
- libass Fontname "Inter Black" works; "Inter Bold" does not (use "Inter" with Bold=-1).
- A fade-in hides the hook on frame 0, so the hook has none.
- When the face pushes the captions up, they can land on the hook: titles treat the caption line as an obstacle and the layout check fails the run if they still meet.

**DaVinci:**
- OTIO's FCPXML adapter floors rational times (29.97 read as 29 fps) — never verify a timeline with it.
- CMX3600 EDL has one frame rate: it is written only when every clip has the timeline's rate, in UTF-8.
- Phone VFR clips drift in Resolve, so the package ships CFR copies (`media/*_CFR.mp4`) without a timecode track.

**Workflow:**
- auto-editor and other tools write `/tmp/...` paths into timelines. Never ship those.
- Phrase IDs change with `--pace`.
- Two-person shots: the tracker follows one face. Use `--reframe blur` or `center`, or cut manually.
- B-roll belongs in `--broll`, not in the main inputs. A clip with no speech in the main inputs is kept whole as a NO-SPEECH phrase with a WARN; a clip that ends up unused is listed as WARN.

## 8. Files

| Script | Purpose |
|---|---|
| `probe.py` | Media info, phone issues, `--find` uploads, `--loudness` |
| `contact_sheet.py` | Timestamped frame grid; `--scenes`, `--safe`, `--outline`, `--times` (HDR shown tone-mapped) |
| `transcribe.py` | faster-whisper → `words.json` + `words.txt` (+ SRT), hallucination screen; `--model`, `--lang`, `--prompt` |
| `plan_cuts.py` | Silence/filler/retake removal, sentence phrases, zoom-cut points, `--select`/`--drop`/`--cold-open`/`--cut`/`--add`, `--silence-only`, `--full` |
| `reframe.py` | Face track → `track.json` (`--target`, `--deadzone`, `--sigma`, `--face-pos`, `--preview`) |
| `captions.py` | ASS karaoke/box/pop/clean + hook + CTA + SRT on the edited timeline; `--avoid` face band, `--replace`; layout self-check |
| `audio_master.py` | Voice chain (latency-compensated), leveler, loudness, music bed with gain-curve ducking, sfx, stems |
| `render_cuts.py` | Single-encode render (normalize, reframe track/wide, cuts, zoom cuts, punch/push, b-roll, grade, captions, export) or `--audio-only` |
| `cover.py` | Best face frame of the kept footage + title → `cover_9x16.jpg` / `thumb_16x9.jpg` |
| `export_resolve.py` | FCPXML 1.10 / EDL / OTIO / FCP7 + SRT + stems + alpha MOV + Romanian README (+ zip), verified by exact parsing |
| `qc.py` | Technical and caption checks, plus sheets to look at |
| `normalize.py` | CFR / SDR / upright mezzanine (H.264 or ProRes) |
| `pipeline.py` | All of the above, with caching and a final WARN summary |
| `dev/make_test_media.py`, `dev/selftest.py` | Synthetic Romanian test footage and an end-to-end self-test (`reference/testing.md`) |

**Reference files:**
- `reference/craft.md`: editing craft and story
- `reference/platforms.md`: safe zones, export, limits
- `reference/romanian.md`: ASR, diacritics, fillers, message templates
- `reference/ffmpeg-recipes.md`: verified recipes and measurements
- `reference/davinci-resolve.md`: handoff
- `reference/testing.md`: test results and limitations

**Models and fonts:**
- Bundled: `assets/models/` holds YuNet (MIT) and RNNoise `sh.rnnn` (stated not subject to copyright). If missing, they are downloaded and checked by sha256.
- Whisper models come from Hugging Face. `large-v3-turbo` is about 1.6 GB on first use.
- Fonts: Inter, with DejaVu as fallback.
