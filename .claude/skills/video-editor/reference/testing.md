# How this skill was tested, and how to re-test it

## Self-test (about 3 minutes)

Run it when the environment changes or a script is edited:

```bash
python3 .claude/skills/video-editor/scripts/dev/selftest.py /tmp/ve_selftest
```

What it does:

1. Generates Romanian test footage with Piper TTS (`dev/make_test_media.py`).
2. Runs the full pipeline:
   - 16:9 talking head plus a VFR, rotated phone clip
   - output 9:16, with hook, music and the DaVinci package
3. Checks:
   - `qc.json` has no FAIL
   - duration equals the cut list
   - loudness is −14 ±1 LUFS
   - the timeline read-back is OK

## Results measured on 2026-10-08

Container: 4 CPUs, 15 GB RAM, no GPU.

**Inputs:**
- 41.7 s 16:9 talking head with pink room noise. The speech contains a greeting, the filler phrase "Ăăă, deci, practic.", a retake, and pauses of 1.6 s and 2.2 s.
- An 11 s vertical phone clip: stored rotated 90°, VFR (avg 23.5 of a nominal 30 fps), full-range yuvj420p, mono 44.1 kHz audio.

**Per-step results:**

| Step | Result |
|---|---|
| Transcribe (large-v3-turbo, int8, 4 threads) | Model load 4–17 s; RTF 0.47 (41.7 s audio) and 0.63 (11 s). Correct diacritics; "Ăă, deci, practic." captured verbatim; 10 word starts snapped to speech onset. |
| Plan cuts (pace tight) | Filler phrase removed; retake ("Al doilea pas … pe telefon" restarted) removed; garbled letter-spelling removed as fillers; leading "Âu," hesitation trimmed. 52.7 s → 33.4 s in 8 segments. Under 2 s. |
| Reframe | Faces in 100% of samples; the crop followed a face swinging ±260 px; 10 s analysis for 41.7 s. |
| Audio | RNNoise chain, pass 0 at −21.8 LUFS, loudnorm stayed linear: −14.0 LUFS, −1.6 dBTP. With music: bed −32.0 LUFS under speech, mix −14.0 LUFS, −1.8 dBTP. |
| Render (track crop, 4 punch-ins, karaoke captions, hook, grade, mixed audio) | 33.367 s = 1001 frames exactly; audio 33.366 s; −14.0 LUFS, −1.7 dBTP after AAC; H.264 High 4.2, BT.709 tags, faststart. Took 30 s, about 1.1× realtime. |
| QC | 0 FAIL, 0 WARN. Sheets inspected visually: captions inside the universal safe zone, hook above the eyes, Ș/Ț/Ă rendered with comma-below. |
| DaVinci package | 8 clips, 1001 frames (equal to the MP4); FCPXML / EDL / OTIO / FCP7 read back with OTIO and all matched the cut list; VFR clip replaced by a CFR copy; ProRes 4444 alpha overlay of 1001 frames. |
| Full pipeline | 135 s for 52.7 s of source with `--clean --resolve` (second render, QC, package). The `dev/selftest.py` run took 105 s for the pipeline and 152 s including test-media generation; all 6 checks passed. |

**Other runs:**

| Run | Result |
|---|---|
| 16:9 YouTube, relaxed pace, clean captions, cold open (P7 first), push-in | 26.7 s; 6 segments in 2 runs (reorder); −13.8 LUFS; GOP 15 (half fps); balanced two-line captions; 45 s total |
| HLG 10-bit HEVC → 9:16 blur fill, pop captions, b-roll clip plus still with Ken Burns, vidstab | Tone-mapped colours match the SDR original; overlays at the right times; 42 s total |
| Vertical VFR → 1:1 with face track (y axis, face at 0.38 H), box captions, hook | Hook clear of the eyes; no overlapping chunks |
| A/V sync | Flash+beep source with 34–37 random cuts plus a 3-segment reorder, on CFR and VFR sources: the offset after the cut equals the source's own (max 20.1 ms both, which is AAC/measurement bias), inline and external-audio paths alike |
| Mixed sources, one without audio | Silence inserted, durations exact |
| 16:9, hook only (`--captions none --hook`), `--cut silence` | Hook burned with no captions, SRT written; 34.3 s from 41.7 s (energy cut keeps the fillers); 70 s total |

## Bugs found by looking at output frames (and fixed)

- The hook covered the eyes. It now has face-band avoidance: top-aligned, moved below the face, or shrunk.
- The active-word pop overlapped its neighbours ("PAUZELEȘI"). Slots are now reserved at 110% width.
- Two chunks were on screen at once when a word's minimum duration crossed the next chunk. The bounds are now enforced, and every run prints an overlap check.
- The hook and the first caption were invisible on frame 0 because of the fade-in. Fade-in removed; the first chunk is extended back to t=0.
- Uppercase in 16:9 clean subtitles, and orphan words ("sfaturi."). Sentence case and even splitting fixed these.
- The default 9:16 caption width ran into the Shorts right rail (x > 888). Max width is now 680 px.
- Music ducking with `sidechaincompress` came out 31 dB under the voice. Replaced with an offline gain curve.
- Whisper wrote Portuguese "ã" for ă. `fix_ro` maps it.

## QA round 2 (2026-10-09): issues found on real and adversarial footage, and fixed

Inputs: a real 95 s selfie vlog (1280×720 29.97, Romanian, outdoors), a 3.4 min 16:9 vlog, and adversarial clips (ambient-only, no audio, 60p VFR, PQ HDR, video starting 0.2 s after the audio, embedded timecode, apostrophe in the project folder). Every repro was re-run after the fix:

| Problem | Before | After |
|---|---|---|
| Whisper hallucination on a 12 s ambient clip | "Să vă mulțumim pentru vizionare!" kept as P1 and burned in; QC 0 WARN | segment removed (4 signals: 16 words/s, 2 zero-length words, 15% speech energy, outro phrase); clip kept whole as NO-SPEECH with a WARN; no caption |
| Hook over the captions when the face pushes them up | captions at y 499 under the hook box for 0–3 s; "OK" | hook placed clear of the caption line (61–78 px if needed); captions.py exits 3 if any caption meets a title; qc.py checks it too |
| Long Romanian words | NECONSTITUȚIONALITATEA drawn at x 11–1073 | drawn at 63%: pixels at x 198–884 in all styles (universal box 120–888) |
| Video starting 0.2 s after the audio | A−V +213 ms, QC FAIL | A−V +1.2 ms (= source); render asserts equal stream lengths |
| Denoise latency | sound 12 ms (RNNoise) / 27 ms (afftdn) behind picture | measured and trimmed: 0.00 ms for off/rnnoise/afftdn; outputs A−V +0.0–1.0 ms on same-rate sources |
| Two-pass loudnorm on −38/−12 LUFS sections | dynamic mode, LRA 19.3, quiet parts at −30/−24/−26 | leveler (LRA 19.8 → 3.4) + static gain/limiter: −14.1 LUFS, LRA 4.2, short-term −17.0…−12.7 |
| Music bed with tight cuts | −31.5 LUFS, 21 dB under the voice | `--music-under 15`: 14.7 LU under the voice |
| Long static shots in a talking-head reel | first change at 9.0 s, 7 of 9 shots > 4 s | zoom cuts: 20 shots in 39.7 s, mean 2.0 s, max 3.4 s, first change 1.6 s |
| Close-up selfie 16:9 → 9:16 | face 51% of H, upscale 2.67×, captions on the forehead | `wide`: upscale 1.56×, face band 624–1085, captions under the chin (y 1157) |
| Phrases on fluent speech | 10–25 s phrases; cold-open line buried | one phrase per sentence (P21 "Ai fost ales să găsești comoara lui Harry Potter." on its own) |
| No-audio clip in a multi-clip auto edit | silently dropped | kept in story order as NO-SPEECH + WARN; unused clips listed as WARN |
| FCPXML after a cold open on a 60p clip | sequence declared 1/60 s, clips off-grid | sequence `<format>` at the cut-list rate (1/25 s); exact-fraction read-back OK |
| 29.97 footage read-back | false MISMATCH (OTIO read 29 fps) | exact parse: OK; format named FFVideoFormat720p2997 |
| EDL | diacritics → '?', 60p source TCs like :34 in a 25p EDL | UTF-8 names; EDL only when all sources share the timeline rate, else skipped and explained in CITESTE-MA |
| Embedded timecode on a VFR source | CFR copy kept TC 13:42:17:05, timeline said 0 | CFR copy written without a timecode track; read-back compares asset start with the media's TC |
| Apostrophe in the project folder | render failed ("Option not found") | filter files copied to a plain temp path; renders fine |
| QC severities | over-length, loudness, true peak only WARN | FAIL (181 s reel: FAIL + early WARN from plan_cuts) |
| Hyphenated clitics | "S-A" reported as missing diacritics | not flagged |
| qc_sheet.jpg shading | red tint made foliage orange | true colours, outline-only safe box; shading only on qc_captions.jpg |
| Delivery size | final.mp4 copied into davinci.zip (84.8 MB zip) | not copied (zip 15.9 MB for the 40 s reel); social CRF 20 / 10 Mbps |

Full runs after the fixes (all exit 0, QC loudness −13.8…−14.0 LUFS, true peak −1.2…−1.8 dBTP after AAC, video = audio duration to the ms):

| Run | Result |
|---|---|
| Real selfie vlog → 39.7 s reel (cold open + loop, hook, CTA, music, sfx, `--resolve`) | 152 s total; reframe wide; 17 shots; QC 0 FAIL 0 WARN; ducked bed 14.7 LU under the voice; music cut on the last frame; cover picked at 3.6 s (eyes open); FCPXML/EDL/OTIO read-back OK |
| 3.4 min 16:9 vlog → reels with hook (`--words` reuse) | 180.3 s → plan_cuts WARN + QC FAIL "length 180.3 s (platform max 180 s)" as intended; hook 313–471, captions at 555, no overlap |
| Same vlog → youtube (`--words` from the reel run = "ambele") | 181.2 s, CRF 18 → 3.8 Mbps; chapters_draft.txt with 6 entries; thumb_16x9.jpg |
| 5 clips 25/60/25/30/30 fps incl. no-audio | 40.2 s; no-audio clip kept (NO-SPEECH WARN); EDL skipped (mixed rates), FCPXML/OTIO OK; A−V +0.0–1.0 ms on 25 fps sources (±1 output frame of quantization on 30/60 fps sources) |
| Ambient + speech clip | hallucination removed, no caption on the ambient part, 1 WARN (NO-SPEECH kept whole) |

## Known limitations

- **Resolve import** is not tested in Resolve itself; the FCPXML/EDL are checked by exact parsing and the OTIO by read-back. The vertical crop is not carried into the FCPXML (Position X values are listed in CITESTE-MA instead).
- **Wide framing** puts a blurred fill under the picture (about the bottom 30% of the frame on a 720p selfie). It is the trade-off for a softer, extreme close-up; `--reframe track` restores the full-height crop.
- **Real phone footage:** one real selfie vlog was tested in QA round 2; the rest is synthetic Piper TTS with faces from a moving still image. Re-check thresholds on the first real jobs:
  - the noise floor and the speech threshold
  - filler detection on fast speakers
- **Fillers whisper doesn't transcribe** are removed only when the gap they leave is ≥ the pace's gap (0.25–0.5 s). Shorter "ăă"s inside a sentence stay.
- **Multi-person shots:** the face tracker follows the largest or most continuous face. For two-person podcasts use `--reframe blur` or `center`, or cut per speaker manually with `--cut`/`--select`.
- **Long renders:** about 1× realtime at 1080×1920. HDR 4K sources are 3–4× slower because of float tone mapping.
- **Emoji** in burned captions aren't supported. Use plain text.
