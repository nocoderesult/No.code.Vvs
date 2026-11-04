# DJ worlds: one real take, five AI worlds, beat-locked loop

A recipe for a music reel built from a phone take (here 120 fps, 1080x1920) and an AI vid2vid version of the
same take that moves the performer through several "worlds". It produced the DJ reel v2: 9.5 s, 285 frames,
five bars of the creator's own song, every cut on a beat, and a loop that restarts seamlessly.

It was rebuilt this way after a first edit (emoji titles, white flashes, template glitches, cuts that ignored
the music) was judged weak. The taste skills drove the rebuild: `taste` (direction), `taste-distillation`
(measure the worlds into a pack), `taste-application` (grade and cut from the pack), `tasteforge-video`
(cadence, editable timeline) and `remotion-video-creation` (typography layer).

## Structure (5 bars at 126 BPM, 14.28 frames per beat)

| Frames | Beats | Shot | What happens |
|--------|-------|------|--------------|
| 0-27 | break 1-2 | `00 REAL` | real take, B&W, 0.5x slow motion, ink serif "Asta am filmat." on the light wall; song low-passed |
| 28-54 | break 3-4 | void | lights flicker out on the beat, performer + booth stay (RVM + static booth mask), 0.35x, zoom out to the AI framing; "Restul e AI.", the word AI ignites in ember on the next beat; filter sweeps open |
| 55-56 | | blackout | 2 black frames before the drop (the song has its own gap there) |
| 57-113 | bar 2 | `01 FOC` | drop: bloom reveal 0.85, short shake, impact |
| 114-170 | bar 3 | `02 NOAPTE` | 2 beats standing, jump cut on beat 3 to the handstand |
| 171-227 | bar 4 | `03 CEAȚĂ` | fog rises and whites out exactly on the next downbeat (transition taken from the content) |
| 228-256 | bar 5 | `04 OCEAN` | CTA comes in, over the dark booth |
| 257-284 | bar 5 | `05 APUS` | last world; frame 284 loops to frame 0 (drop bar back to the break) |

## Steps

1. **Song first.** Beat grid from the song (`tempo`, first beat, energy per beat finds break and drop). Align the
   song to the take by cross-correlating spectral flux with the camera's room sound: here the creator's file was
   185 ms late against what played in the room. Choose a window of whole bars, so the loop is musically seamless.
   Done when the beat residuals are a few ms and the drop sits on a bar line.
2. **Map the AI clip.** Per-frame sharpness + hue-histogram change finds the world boundaries and the blurred morph
   frames between them (never use those). The AI motion only loosely follows the take, so do not try to time-lock
   it: pick clean ranges per world and cut them on beats.
3. **Measure into a pack** (`measure.py`): per world L* p1/p50/p99, L* std (contrast), background % (L*<10),
   chroma and hue per L* zone (median). Write targets in `grade4.py` (`WORLDS`): common black point, real
   highlights where a world has none, chroma soft cap; keep each world's hue. Verify after grading.
   Done when black points sit within ~1.5 L* of each other and no world looks muddy on a board of real frames.
4. **Matte** (`matte4.py`): RVM person alpha on the frames the void uses, plus a static booth mask from a
   temporal median (camera is locked off) clamped to the measured booth edges and faded toward the bottom.
5. **Plan** (`pack/edit_plan.json`): shots with source in-points and steps, labels, bloom per cut, text timings.
6. **Typography** (`remotion/Overlay.tsx`): transparent PNG sequence. Two voices only: Instrument Serif Italic
   speaks (hook, CTA), JetBrains Mono labels the worlds. Label colour follows the measured background behind it
   (ink above L* ~58, bone below). `npx remotion render src/index.ts Overlay out/ov --sequence --image-format=png
   --image-sequence-pattern='[frame].[ext]'`.
7. **Compose** (`compose4.py`): grade, void, punch 5% + 0.8% beat pulse, bloom reveal, halation, vignette, grain,
   overlay, ProRes master. **Sound** (`audio4b.py`): resonant low-pass on "reality", sweep through the void,
   restrained SFX, -14 LUFS, stems. **Timeline** (`export_timeline4.py`): shots + alpha text + stems as FCP7 XML,
   FCPXML and EDL, read back and verified.

## Lessons that are not visible in the code

- **Lab chroma cuts turn a saturated red backdrop salmon**, and a steep L* curve over a backdrop gradient bands.
  For a flat colour world, deepen L* gently and keep the chroma.
- **A curve's p99 is not always "highlights"**: in the red world p99 was the backdrop itself.
- **Grain survives Instagram** at 0.02-0.03 amplitude (2 px grain), as checked with a 3.5 Mbps re-encode; heavier
  grain turns to mush and steals bits.
- **The AI framing is ~1.75x wider than the take**: scale the real performer down on black to match it (the 1080p
  take stays sharp), never scale the 720p AI frame up.
- **Cut 0-17 ms early**: the floor of `beat_frame + 0.25` keeps every cut on or just before the beat.

## V3: locked track, match cuts, one question (`v3/`)

A stricter brief: the creator's track is locked (one continuous passage, static gain only, no filters, no loops),
no flashes, a single static question on frame 0, every junction checked at slow speed. Templates in `v3/`.

- **Song source check**: cross-correlate the delivered reel's audio with every source before choosing the master;
  the identical track here existed only for 13.9 s, which capped the reel (ask for the song file when the brief
  wants more).
- **White room on the AI deck axis** (`white_plate.py`): solve scale/offset from the booth's side edges and deck
  edge, extend the wall by confidence-weighted normalized convolution (no dark halo), continue the cabinet from its
  last real row, contact shadow, neutral white wall.
- **Match cuts by silhouette** (`sil.py`): RVM silhouettes of the take (placed on the AI axis) and of the AI clip,
  IoU in the upper body + hand-palm distance; pick the pair where the hand is still descending in the take and has
  landed in the AI frame. Blue enters before the lift (silhouette top profile finds prep, full extension, descent).
- **Remotion**: editable timeline (one `<Video>` node per clip with literal `trimBefore/from/durationInFrames`,
  `premountFor={fps}`), local OFL fonts via `@remotion/fonts` (the render browser cannot reach fonts.gstatic.com
  through the proxy), `TypeBoard` to audition faces on the real frame. Remotion tags output as sRGB: retag BT.709
  with `h264_metadata` (no re-encode).
