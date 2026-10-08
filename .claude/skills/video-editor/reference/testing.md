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

## Known limitations

- **Resolve import** is not tested in Resolve itself; only the OTIO read-back was checked.
- **Real phone footage** wasn't available. Speech was synthetic Piper TTS and faces came from a moving still image. Re-check thresholds on the first real job:
  - the noise floor and the speech threshold
  - filler detection on fast speakers
- **Fillers whisper doesn't transcribe** are removed only when the gap they leave is ≥ the pace's gap (0.25–0.5 s). Shorter "ăă"s inside a sentence stay.
- **Multi-person shots:** the face tracker follows the largest or most continuous face. For two-person podcasts use `--reframe blur` or `center`, or cut per speaker manually with `--cut`/`--select`.
- **Long renders:** about 1× realtime at 1080×1920. HDR 4K sources are 3–4× slower because of float tone mapping.
- **Emoji** in burned captions aren't supported. Use plain text.
