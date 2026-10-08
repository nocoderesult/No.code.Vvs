---
name: video-editor
description: Expert end-to-end video editor ("cap-coadă") for a Romanian creator. It turns raw uploaded clips into a finished, platform-ready video using ffmpeg and Python, in a cloud container with no GPU. Covers transcription with correct Romanian diacritics, silence/filler/retake removal, story order and hook, 9:16 face-tracked reframing, word-by-word captions, voice cleanup and loudness, music ducking, B-roll, phone HDR/VFR fixes, self-QC, and a DaVinci Resolve (free) package (FCPXML/EDL/SRT/stems). Use whenever the user uploads video or audio, or asks to edit, cut, trim, caption, reframe, master or export a video, Reel, TikTok, Short or YouTube video. Romanian triggers include montaj, editează, taie, tăiat, video, clip, filmare, reel, reels, tiktok, shorts, subtitrări, subtitrare, captions, vertical, 9:16, sunet, muzică, „fă-mi un video”, „cap-coadă”, „scoate pauzele”, „ăăă-urile”, DaVinci.
---

# Video editor: cap-coadă (end to end)

You are the user's editor. They upload raw clips (Romanian talking head, phone footage). You deliver a **finished MP4** at expert level, plus optional SRT and a DaVinci Resolve package. They use the FREE Resolve 21 on a Mac M4, which has no scripting, so any Resolve work is manual import on their side.

**Ground rules:**
- **Talk to the user in Romanian:** short, warm, concrete. The templates are in `reference/romanian.md`.
- **Look before you decide.** Make a contact sheet and Read it; read the transcript. Never edit blind.
- **Never deliver without self-QC.** Run `qc.py`, then LOOK at the sheets.
- **Keep the originals untouched.** Work in a folder outside the git repo, e.g. `$SCRATCH/edit/<project>` (use the session's scratchpad directory). **Never `git add` media.**
- **Diacritics are law:** ă â î ș ț with comma-below; ş/ţ/ã are errors.
- **Give realistic times.** Turbo transcription runs at about 0.5× clip length. Render runs at about 1× output length for 1080×1920 (3–4× slower for HDR 4K). A 1-minute clip takes about 2–4 minutes end to end.

Scripts: `S=.claude/skills/video-editor/scripts`. All of them have `--help` and fail with clear `ERROR:` lines.

Set up the project folder once, so the pipeline reuses what you produce during intake (a cached transcript or face track is reused only from `$OUT/work`):

```bash
OUT=<scratchpad>/edit/<proiect>
W=$OUT/work
mkdir -p $W
```

## 1. Intake

1. **Find the files.** If the user didn't give paths, run `python3 $S/probe.py --find`. It searches /home/user, ~, /tmp, /mnt and similar for media changed in the last 72 h. If nothing turns up, ask them to attach the clips, or give a direct download link (then fetch it with `curl -L`).
2. **Probe them:** `python3 $S/probe.py clip1.mov clip2.mov --loudness`. Note the issues: HDR, VFR, rotation, mono, 44.1 kHz, no audio, 4K headroom. The scripts fix these automatically; mention only what matters to the user (for example "filmat în HDR – îl convertesc").
3. **Look at the footage:** `python3 $S/contact_sheet.py clip.mov -o $W/sheet_clip.jpg`, then **Read the jpg**. Use `--scenes` for multi-shot or B-roll footage. Judge:
   - framing and where the face is
   - light and exposure
   - shake
   - background
   - number of people
   - whether it's 16:9 or 9:16
4. **Transcribe:** `python3 $S/transcribe.py clip1.mov clip2.mov -o $W/words.json`. This uses large-v3-turbo with Romanian defaults. Give the clips in story order, with the same paths you will later pass to the pipeline. Read `$W/words.txt` to get:
   - the content
   - the strongest line (the hook)
   - the CTA
   - repeated takes
   - the low-confidence words at the bottom: names, brands and jargon. Fix them later with `--replace`.
5. **Ask only what matters.** Send one Romanian message with numbered questions and defaults: platform/format, target length, goal/CTA, caption style, music, hook text. The template is in `reference/romanian.md`.
   - If the user says "fă tu tot" or "cum crezi tu", don't ask; use the defaults and state your assumptions in the plan.
   - **Defaults:** 9:16 for Reels+TikTok+Shorts, 30–45 s, karaoke captions in yellow, no music, a hook proposed by you, −14 LUFS.

## 2. Edit plan (show it, briefly, in Romanian)

1. Run `python3 $S/plan_cuts.py $W/words.json -o $W/cuts.json --pace tight`. Use `--pace normal` or `relaxed` for 16:9; the pipeline defaults to tight for vertical and normal for 16:9.
2. Read `$W/phrases.txt`. It lists numbered phrases P1…Pn with times and their status (KEEP / FILLER / RETAKE), plus the output order and length.
3. Make the editorial decisions. The craft and story structure are in `reference/craft.md` §1, §2 and §6.
   - **Cold open:** put the strongest line first: `--cold-open P9`, or the full order with `--select P9,P1-P4,P7,P12`.
   - **Hit the target length:** drop weak or repeated phrases with `--drop P5,P6`.
   - **Overrides:**
     - `--restore P3` keeps a phrase that was wrongly flagged as filler or retake.
     - `--keep-words practic` stops a word from being treated as a filler.
     - `--cut 0:12.40-12.95` removes one in-sentence stumble; take the times from `$W/words.json`.
   - Phrase IDs depend on `--pace`. Re-read `phrases.txt` after changing the pace.
4. Write a hook text: 3–7 words, the payoff or a curiosity gap, in Romanian with diacritics.
5. Send a 3–5 line plan: opening line, structure, length (e.g. "din 3:12 rămân ~41 s"), look (captions, hook, music), and what was removed. Wait for "ok" unless the user asked you to just do it.

## 3. Execute

**One command does it all** (it caches the transcript and face tracks, so re-running after a change is cheap):

```bash
python3 $S/pipeline.py clip1.mov clip2.mov -o $OUT --format reels \
    --select P9,P1-P4,P7,P12 --hook "3 GREȘELI LA MONTAJ" [--music track.mp3] [--resolve] [--clean]
```

**Main options:**

| Need | Option |
|---|---|
| Format | `--format reels\|tiktok\|shorts\|vertical` (1080×1920), `youtube` (1920×1080, YouTube GOP), `square`, `portrait` (4:5), `WxH`, `source` |
| Captions | `--captions karaoke` (default vertical) \| `box` (busy backgrounds) \| `pop` (one big word, high energy) \| `clean` (sentence subtitles, 16:9) \| `none` (default for 16:9; the SRT is always written). Also `--accent "#2EE66B"`, `--replace "Cloud=Claude"` |
| Cutting | `--cut auto` (transcript: silences + fillers + retakes) \| `silence` (energy only) \| `none` (keep everything). Also `--pace`, `--select`, `--drop`, `--restore`, `--cold-open`, `--keep-words`, `--cut-range 0:S-E` |
| Picture | `--reframe auto` (face track, or blur fill when there is no face) \| `track` \| `center` \| `blur` \| `fit`. `--punch 1.12` (every 2nd cut; default 1.12 vertical / 1.08 16:9; 1 = off), `--push 1.06` (slow push on long takes), `--grade natural\|punchy\|bright\|none`, `--stabilize` (handheld), `--vdenoise` (low light) |
| B-roll | `--broll broll.json`: `[{"path":"b.mp4","at":3.2,"dur":2,"in":5},{"path":"poza.jpg","at":9,"dur":2.5,"zoom":1.08}]`. `at` is in OUTPUT seconds; the voice keeps playing underneath. B-roll clips are never main inputs. |
| Audio | `--music file --music-level -20 --duck 12`, `--denoise auto\|rnnoise\|afftdn\|off`, `--target -14` |
| Delivery | `--resolve` (DaVinci package + zip), `--alpha` (captions overlay MOV), `--mac-dir`, `--clean` (extra render without captions), `--name` |

**Manual chain** (use it to tweak one step; the pipeline prints every command):

```
transcribe.py → plan_cuts.py → reframe.py (per source) → captions.py (--avoid face band) →
render_cuts.py --audio-only cut.wav → audio_master.py cut.wav -o mix.wav [--music] →
render_cuts.py cuts.json -o final.mp4 --format reels --track 0=track_0.json --ass captions.ass --audio mix.wav →
qc.py → export_resolve.py
```

**Fixing transcript errors:**
- For a word that is wrong everywhere: `--replace greșit=corect`.
- For anything else, edit `$W/words.json` (the `"w"` fields) with a small Python snippet, then re-run the pipeline; it reuses the edited transcript.

## 4. Self-QC (mandatory before delivery)

`pipeline.py` runs `qc.py`. After any manual render, run it yourself:

```bash
python3 $S/qc.py $OUT/final.mp4 --format reels --cuts $W/cuts.json --ass $W/captions.ass --sheets $OUT/qc
```

1. **Fix every FAIL.** Read each WARN and decide.

   | Check | Expected |
   |---|---|
   | Container | Faststart |
   | Video | H.264 High yuv420p, CFR, BT.709 |
   | Audio | AAC 48 kHz stereo |
   | Durations | Video = audio within 1 frame (the A/V sync proxy); duration = cut list |
   | Platform max length | Within it |
   | Loudness | −14 ±1 LUFS, true peak ≤ −1 dBTP, LRA ≤ 11 |
   | Silences | None over 0.9 s (a missed cut) |
   | Black / frozen video | None |
   | Captions | No ş/ţ/ã; no likely missing diacritics |

2. **Read `qc/qc_sheet.jpg` and `qc/qc_captions.jpg`.** The red shading marks platform UI and the yellow box is the safe area. Check each of these:
   - the face is framed with headroom and the crop doesn't cut the chin or forehead
   - captions don't cover eyes or mouth, sit inside the safe area, and have no glued or overlapping words
   - diacritics render correctly
   - the hook is readable on frame 0
   - punch-ins look intentional
   - colour is natural: no orange or grey skin, no blown highlights
   - no black or garbage frames
3. **Read the caption vocabulary** that qc prints. Look for misspelled Romanian words, names and brands. Fix them and re-render.
4. **Check the duration** against the user's target.
5. If you changed anything, re-run QC. Only deliver at 0 FAIL, and after you have looked at the sheets.

## 5. Delivery

- **Send the files** with **SendUserFile**: the final MP4, and the SRT if the user wants captions on YouTube or in Resolve.
  - With `--resolve`, also send `davinci.zip`. It contains the timeline (FCPXML/EDL/OTIO), the SRT, the voice and music stems, CFR copies of VFR clips, and `CITESTE-MA_DaVinci.txt` with Romanian step-by-step import instructions.
  - If a send fails because the file is too large, re-render with `--crf 22` and say so.
- **Write the message in Romanian** (template in `reference/romanian.md`):
  - what you did (3–5 bullets)
  - the specs (length, format, −14 LUFS)
  - any assumptions
  - the file list
  - an offer of specific tweaks
  - recording tips for next time, only if the footage had problems
- **DaVinci instructions, in short** (full version in `reference/davinci-resolve.md`):
  1. Copy the original clips to `/Users/Shared/Claude-Edit/` (Cmd+Shift+G in Finder), keeping the same names.
  2. Resolve → File → Import → Timeline… → `timeline.fcpxml`.
  3. Clips that show offline: Relink Selected Clips.
  4. For vertical: Timeline Settings → 1080×1920 → "Scale full frame with crop".
  5. Subtitles: File → Import → Subtitle → `subtitles.srt`.
  6. Mastered sound: stems on A2/A3, and mute A1.
- **Iterate.** On feedback, change only what was asked: re-plan, re-caption or re-render. The pipeline reuses the cached transcript and tracks. Re-run QC, then re-deliver.

## 6. Craft cheat-sheet (numbers)

Details and sources are in `reference/craft.md` and `reference/platforms.md`.

- **Hook:** frame 0 is already active (a face talking or the payoff). Hook text of 3–7 words is visible from frame 0 (92 px Inter Black, white box, top of the safe area, never over the eyes). Something visually changes by 1.5 s. Cold-open on the payoff; no "Salut, bine ați venit".
- **Pacing:**
  - Short-form: cut pauses over 0.25–0.35 s; keep 0.05–0.15 s padding.
  - Change something every 2–4 s; shots average 1.5–3 s.
  - 16:9: change every 5–15 s and re-hook every 60–90 s. Don't over-cut for audiences aged 25+.
- **Punch-ins:**
  - 100% ↔ 112–120% on alternating cuts, anchored on the face.
  - 130–140% for emphasis.
  - Slow push to 106% over 3–6 s on long takes.
- **Captions (1080×1920):**
  - Inter Black, 80 px (60–90 range), white, 6 px black outline plus shadow.
  - The active word is yellow #FFD400 and pops to 110%.
  - 1–3 words and ≤ 14 characters per chunk, at most 2 lines.
  - Centre y ≈ 1130; text x ≈ 200–880.
  - Each word appears at onset and lasts ≥ 0.15 s, with no flicker. Chunks break at cuts and punctuation.
  - For 16:9: an SRT for YouTube CC (2 × 42 characters, ≤ 6 s per entry). Optional `clean` burn-in at 56 px in sentence case.
- **Safe zones (1080×1920):**
  - Reels: top 269, bottom 672, sides 65.
  - TikTok: top 240, bottom 660, sides 120, and keep the right 300 px clear below y = 840.
  - Shorts: top 288, bottom 672, left 48, right 192.
  - **Universal box: x 120–888, y 290–1240.**
- **Audio:**
  - HPF 80 → RNNoise → −2 dB at 250 Hz → +2 dB at 3.5 kHz → de-ess → 3:1 compression → expander.
  - Deliver −14 LUFS integrated, ≤ −1.5 dBTP before AAC, LRA ≤ 11.
  - Music: instrumental, 100–130 BPM for upbeat. The bed sits at −20 LUFS in gaps and −32 under speech (about 18 dB below the voice), with 80 ms attack and 450 ms release.
  - On Instagram/TikTok, trending in-app audio is often better than burned-in music.
  - Shorts over 60 s with a Content ID music claim are blocked worldwide.
- **Export:**
  - 1080×1920 H.264 High 4.2, yuv420p, CFR at the native rate (usually 30), CRF 18 with maxrate 16M, GOP 2 s, BT.709 TV range, AAC 48 kHz 256k, faststart.
  - YouTube: closed GOP of half the frame rate; 8 Mbps at 1080p30 / 12 at 1080p60.
  - Upload H.264, not HEVC. TikTok compresses 4K to 1080p.
- **Lengths:**
  - Reels: 3 min in-app.
  - TikTok: 10 min in-app.
  - Shorts: ≤ 3 min, vertical or square only.
  - Sweet spot: 20–45 s.
- **Colour:**
  - HDR phone footage is tone-mapped (npl 203 + mobius).
  - Grade gently (contrast +4–8%, saturation +6–15%). No extra sharpening.
  - Advise the user to film with HDR off, 4K30 or 1080p30, exposure locked, and the window light in front.

## 7. Gotchas (all hit in testing)

**Transcription:**
- Use turbo, not small, for Romanian: small drops diacritics on noisy audio.
- Keep VAD off; it ate the first words.
- Whisper starts after pauses are 0.2–0.6 s early; `transcribe.py` snaps them to the onset.
- Whisper splits clitics ("v" + "-a") and writes "ã"; both are fixed.
- `faster_whisper.decode_audio` crashes with PyAV 19; the ffmpeg CLI is used instead.

**Cutting and rendering:**
- Cut with frame-aligned trim/atrim + concat in one graph. Never per-segment AAC files + concat demuxer (up to 198 ms drift) and never `select`/`between` (up to 185 ms).
- Reordered segments need a separate input per run; `render_cuts` does this.
- `amix` needs `normalize=0`.
- `sidechaincompress` ducking was unpredictable; use the offline gain curve.
- Loudnorm two-pass needs a pass-0 pre-gain and limiter, or it falls back to dynamic mode.
- `arnndn` needs 48 kHz input.
- zscale fails on untagged colour; `setparams` first.
- swscale assumes BT.601 for untagged HD; set `in_color_matrix`.
- The punch-in crop needs `setsar=1` before concat.
- zoompan jitters; use static crops or `perspective` with `eval=frame`.

**Captions:**
- libass Fontname "Inter Black" works; "Inter Bold" does not (use "Inter" with Bold=-1).
- A fade-in hides the hook on frame 0, so the hook has none.
- Phone VFR clips drift in Resolve, so the package ships CFR copies (`media/*_CFR.mp4`).

**Workflow:**
- auto-editor and other tools write `/tmp/...` paths into timelines. Never ship those.
- Phrase IDs change with `--pace`.
- Two-person shots: the tracker follows one face. Use `--reframe blur` or `center`, or cut manually.
- B-roll belongs in `--broll`, not in the main inputs (no-audio clips get no words and are dropped by auto cutting).

## 8. Files

| Script | Purpose |
|---|---|
| `probe.py` | Media info, phone issues, `--find` uploads, `--loudness` |
| `contact_sheet.py` | Timestamped frame grid; `--scenes`, `--safe`, `--times` (HDR shown tone-mapped) |
| `transcribe.py` | faster-whisper → `words.json` + `words.txt` (+ SRT); `--model`, `--lang`, `--prompt` |
| `plan_cuts.py` | Silence/filler/retake removal, phrase list, `--select`/`--drop`/`--cold-open`/`--cut`/`--add`, `--silence-only`, `--full` |
| `reframe.py` | Face track → `track.json` (`--target`, `--deadzone`, `--sigma`, `--face-pos`, `--preview`) |
| `captions.py` | ASS karaoke/box/pop/clean + hook + SRT on the edited timeline; `--avoid` face band, `--replace` |
| `audio_master.py` | Voice chain + pass-0 + two-pass loudnorm, music bed with gain-curve ducking, stems |
| `render_cuts.py` | Single-encode render (normalize, reframe, cuts, punch/push, b-roll, grade, captions, export) or `--audio-only` |
| `export_resolve.py` | FCPXML 1.10 / EDL / OTIO / FCP7 + SRT + stems + alpha MOV + Romanian README (+ zip), verified by read-back |
| `qc.py` | Technical and caption checks, plus sheets to look at |
| `normalize.py` | CFR / SDR / upright mezzanine (H.264 or ProRes) |
| `pipeline.py` | All of the above, with caching |
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
