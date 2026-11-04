# Six signature effects on a 4K master

A recipe for a talking-head reel shot in Apple Log (iPhone ProRes, 4K portrait) that needs some or all of the
six effects, a custom grade and a 4K "upscaled" master. It produced reel 3 (46.8 s, 20 cuts, 1404 frames).

| # | Effect | Where it lives |
|---|--------|----------------|
| 1 | Text behind the head (huge word rising from behind him) | Remotion `Behind` layer + person matte |
| 2 | Over the shoulder (push in, BEFORE/AFTER cards behind him) | camera move in `timeline.py`, cards in `Behind`, frost mask red |
| 3 | Glass graph (frosted card, number counts, line draws) | `Front` layer, frost mask green |
| 4 | Tier list S/A/B/C/D built under the face, logos drop on the spoken names | `Front` + frost mask green |
| 5 | Freeze frame: flash, grey world, cut-out sticker with white outline + tag | compositor (`freeze_frame`) + tag in `Front` |
| 6 | Colour grade: washed Log, then a light line wipes in the graded image | compositor (`light_line`, Log plate) |

Templates: `tools/` (Python, ffmpeg) and `remotion/` (`Reel3.tsx`, `Root.tsx`). The cut list (`SEGS` in
`tools/timeline.py`) and the word-to-effect mapping (`tools/events.py`) are per video; everything else is reusable.

## Steps

1. **Probe, transcribe, track** with the main skill (`scripts/probe.py`, `transcribe.py`, face/hand tracking).
   Done when `work/words.json` has the opening words (a long silent lead-in makes Whisper drop them: transcribe that
   span separately) and `work/track.json` has a face box for most frames.
2. **Grade**: copy `look3.py`, measure skin/wall/neutrals on two stills (`grade_preview.py` prints skin IRE and the
   vectorscope angle), tune `P`, write the `.cube`. Done when skin sits within ±5° of the skin line (123°) and
   denim reads blue on the iPhone-view preview.
3. **Cut list + camera**: plot the voice energy with the planned cuts (`envplot.py`), cut 60-100 ms before onsets,
   then `timeline.py` writes every output frame (source frame, crop, zoom, roll, face box in output space).
   Done when every segment's face centre and eye line print inside 0.45-0.55 / 0.30-0.40 (except deliberate moves).
4. **Matte**: `matte.py` (RVM, graded input, 1080x1920, 8 warm-up frames per run). Done when a matte overlaid on its
   frame hugs the hair with no lag on moving hands.
5. **Events + graphics**: `events.py` turns word times into effect timings and caption chunks; render the Remotion
   layers at 1080 first, composite a dozen frames with `compose.py --scale 1 --list ...` and look at them.
   Done when every effect has been seen on a real frame and nothing leaves the 1080x1920 frame.
6. **Sound**: `audio.py` (WPE dereverb -> cut -> voice chain -> SFX on every effect -> ducked music -> -14 LUFS).
7. **4K**: Remotion `--scale=2` for Front/Behind (masks stay 1080), four `compose.py --range` workers into ProRes,
   `finalize.sh` for the 4K and 1080p files, `qc_final.py` for the sheet and loudness.

## Lessons that are not visible in the code

- **Apple players decode BT.709 with the inverse camera curve (~1.96 gamma)**, so a 2.4-encoded grade looks washed
  on iPhone. `look3.py` encodes with the BT.709 OETF (Rec.709-A behaviour); preview through `apple_view()`.
- **iPhone ProRes carries a 4-channel spatial (ambisonic) track** next to the stereo one. Multichannel WPE
  (`nara_wpe`) over all six channels takes the room off the voice; beamforming the ambisonics gained < 1 dB.
- **Dark painted walls are full of blotchy chroma noise** that a 1.5x upscale magnifies. Smooth the wall only, by
  normalized convolution over wall pixels (`clean_wall`); a plain blur pulls skin colour into the wall and leaves a
  bright halo around the head.
- **Frosted glass must be a separate mask**: Remotion has no backdrop on a transparent layer, so the `Masks`
  composition paints glass shapes red (behind) / green (front) with `mix-blend-mode: screen` and the compositor
  blurs the plate there.
- **Seeking is frame-exact** on intra-only ProRes with `-ss (idx - 0.15)/30` before `-i` (verified against
  `select=eq(n,…)`), so mattes and plates decoded separately stay aligned.
- **`--image-sequence-pattern='[frame].[ext]'`** pads to the digits of the last frame; rename to `%05d.png`.
- **Cost at 4K**: ~2.5 s per frame per worker after confining every blend to the bounding box of its mask/alpha;
  four workers render ~47 s of 4K in about 25 minutes on 4 CPUs.
- **Honest upscale**: the crop (67 % of the frame) is resampled to 2160x3840 with Lanczos, luma-only unsharp mask
  and fine grain. AI super-resolution on CPU is far too slow for 1400 4K frames and invents skin texture.
