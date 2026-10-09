# Editing craft for short vertical video and 16:9 talking-head YouTube

How sure each point is:
- **[OFFICIAL]**: the platform's own documentation.
- **[3P]**: what third-party sources agree on.
- **[?]**: uncertain, or the sources disagree.
- **[practice]**: a working value used by editors, with no single source behind it.

Researched in October 2026.

## 1. Hook (first 1–2 s)

- **Cold open.** Start on the strongest line or the payoff. Don't open with a greeting, logo or intro, and cut "Salut, bine ați venit". Starting mid-sentence is fine. [3P]
  - In the scripts: `plan_cuts.py --cold-open P7`, or `--select P7,P1-P6`.
- **Frame 0 must already be doing something:**
  - The face is already talking, or the result or B-roll is on screen.
  - The hook text (3–7 words) is visible from frame 0. `captions.py --hook` does this: no fade-in, and it stays clear of the face.
  - Something visual changes by about 1.5 s: a punch-in, B-roll or a text pop. `plan_cuts` puts the first zoom cut of the opening segment at 1.2–2.0 s, so this happens even in one long take.
- **Hook metric on Shorts:** "Viewed vs swiped away". About 70% is OK; 75–80% or more is strong. [3P] Since March 2025 a Shorts view counts on any start or replay.
- **Instagram signals:** watch time, likes per reach and sends per reach (Mosseri, January 2025). Never upload a file with a TikTok watermark; Instagram downranks visible watermarks from other apps. [3P]
- **Make it loop.** Write the last line so it leads back into the first, and end on a button (`pipeline.py --loop`: the music stops on the last frame instead of fading). [practice]

## 2. Pacing, silences, jump cuts

- **Silence removal for short-form:**
  - Cut pauses longer than about 0.25–0.35 s.
  - Keep 0.05–0.15 s of padding around speech.
  - Don't merge sentences, and don't clip word tails.
  - The `plan_cuts --pace` presets:

    | Preset | Split pauses at | Padding before | Padding after |
    |---|---|---|---|
    | tight | 0.25 s | 0.05 s | 0.10 s |
    | normal | 0.30 s | 0.06 s | 0.12 s |
    | relaxed | 0.50 s | 0.10 s | 0.20 s |

- **Change cadence** [3P, sources disagree]:

  | Format | Something changes every… |
  |---|---|
  | Short-form | 2–4 s: a cut, punch-in, B-roll or text change (average shot 1.5–3 s) |
  | Long 16:9, first 30 s | 3–5 s |
  | Long 16:9, body | 5–7 s up to 15–30 s; re-hook every 60–90 s |

  - Viewers aged 25–35 and older are put off by over-editing.
- **Zoom cuts** [practice]: a long take with no jump cut still needs a change every 2–4 s. `plan_cuts` marks word-boundary points inside every kept segment longer than about 3.5 s (prefers a Whisper segment end or a comma, ≥ 1.2 s from either edge), and `render_cuts --zoom-cuts` (default on for vertical) splits the take there into back-to-back shots with no time jump, alternating 100% / punch framing. Measured on a real 95 s selfie vlog cut to 40 s: 20 shots, average 2.0 s, longest 3.4 s, first change at 1.6 s (before: first change at 9.0 s, 7 of 9 shots over 4 s).
- **Punch-ins** [practice]:
  - Alternate 100% and 112–120% on consecutive shots. The default is 1.12 on every 2nd shot (1.08 for 16:9).
  - When the source is already upscaled more than 2× (720p into 1080×1920), the punch is capped at 1.05: a 12% crop on top looks soft.
  - Use 130–140% for an emphasis line.
  - On long takes, push slowly from 100% to 106% over 3–6 s (`--push 1.06`).
  - Land punch-ins on stressed words.
  - A 4K source gives 2× crop headroom.
  - Static punch-ins have zero jitter. Animated zooms use `perspective` with `eval=frame`, never `zoompan`, which jitters.
- **B-roll:**
  - Use it to cover jump cuts and abstract statements.
  - In Shorts each insert runs 1–3 s.
  - Keep the voice running under it (L-cut / J-cut).
  - Ken Burns on stills: 100% → 108–110%.
  - Talking head plus B-roll beats a pure talking head. [3P]
- **Sound design** [practice]: a whoosh on transitions and a pop when text appears, about 18–24 dB under the voice, used sparingly. `pipeline.py --sfx` synthesizes them (no licence issues): a pop when the hook and the CTA appear, a whoosh 0.12 s before each B-roll insert, ~20 dB under the voice; they also go to `stems/sfx.wav`.

## 3. Captions (burned in, 1080×1920)

- **Size:**
  - Optimal 60–75 px; karaoke 70–90 px; hard maximum about 100 px.
  - Weight 700–900 with a black outline. [3P]
  - Defaults in the scripts: karaoke and box 80 px, pop 96, clean 62.
- **Words on screen:**
  - Word-by-word style: 1–3 words at a time.
  - Phrase style: 3–5 words.
  - At most 2 lines of about 16–20 characters. The default is 14 characters per chunk, so most chunks fit on one line.
- **Style:**
  - White text with a 5–7 px black outline at PlayRes 1080, plus a soft shadow.
  - Active word yellow #FFD400 (or green #2EE66B), or a box behind it on busy footage.
  - No script fonts.
  - ALL CAPS is fine, since Inter has Ă Â Î Ș Ț.
- **Position:**
  - Centred, with the text inside x ≈ 200–880, so it clears the right action rails. One line per chunk; a single word too long for that width (NECONSTITUȚIONALITATEA, ÎNTREPRINDERILOR) is drawn smaller (`\fs`) instead of crossing the safe zone. The width check includes the 110% pop and the outline.
  - Bottom of the text at or above y ≈ 1240.
  - Typical centre line y ≈ 1100–1250; the default is 1130.
  - Never over the eyes or mouth. The `--avoid` band does this automatically: below the chin when the line fits above y 1240, otherwise above the brows.
  - Hook and CTA boxes are placed clear of both the face band and the caption line (shrunk to as little as 50% if needed); if no spot exists, the captions move for the title's duration. `captions.py` re-measures every event from the .ass and fails the run if a caption sits under a title.
- **Timing:**
  - Each caption appears at word onset and stays at least 0.15 s.
  - Hold the line between words; never flicker.
  - Chunks break at punctuation, at pauses over 0.45 s, and at cuts.
- **16:9 YouTube:**
  - Upload the SRT as closed captions (CC). Burn-in is optional; if you burn in, use the `clean` style in sentence case.
  - SRT format: at most 2 lines × 42 characters, at most 6 s per entry.
- **Emoji:** libass colour-emoji support is uncertain [?]. Don't put emoji in burned captions; put them in the post caption.

## 4. Audio

- **Voice chain:** HPF 80 Hz → (50 Hz hum notch if needed) → RNNoise denoise → −2 dB at 250 Hz → +2 dB at 3.5 kHz → de-ess → compress 3:1 → gentle expander → two-pass loudnorm.
- **Delivery target:** −14 LUFS integrated, true peak ≤ −1.5 dBTP before AAC (it comes out around −1.7 after encoding), speech LRA ≤ 7–11.

  | Platform | Integrated | True peak | Behaviour | Status |
  |---|---|---|---|---|
  | YouTube / Shorts | −14 LUFS | −1 dBTP | Turns loud audio down only; never boosts | [3P / near-official] |
  | TikTok | none published; about −14 observed | −1 dBTP advised | adaptive | [?] |
  | Instagram Reels | none published | −1 dBTP advised | adaptive | [?] |

- **Music under voice:**
  - The voice sits at −14 LUFS.
  - Set the bed relative to the voice, not as an absolute level: **15 dB under the voice while talking** (`--music-under 15`, ≈ −29 LUFS), rising by the duck depth (`--duck 8`, ≈ −21 LUFS) in pauses. With tight cuts the voice is on 90–95% of the time, so the old "−20 in gaps, duck 12" left the bed at −31.5 LUFS, 21 dB under the voice, nearly inaudible on a phone speaker. WCAG 1.4.7 advises ≥ 20 dB for accessibility-critical speech; use `--music-under 20` for that.
  - The scripts use an offline gain curve: look-ahead 80 ms, attack 80 ms, release 450 ms, and gaps under 0.35 s held so the bed doesn't pump.
- **Choosing music:**
  - Instrumental, or minimal vocals, under Romanian speech.
  - 100–130 BPM for upbeat content.
  - End on a button or hard stop so it loops cleanly (`--loop`); otherwise a 1.5 s fade-out.
  - On Instagram and TikTok, trending in-app audio added at low volume is safer for reach and copyright than burned-in commercial music. [practice]
  - **YouTube [OFFICIAL]:** Shorts over 1 minute with any Content ID claim are blocked globally.

## 4b. Framing a 16:9 selfie as 9:16

- A full-height 9:16 crop of a 16:9 frame keeps only 32% of the width. On an arm's-length selfie the face then fills ~50% of the frame height, the 720p source is upscaled 2.7× (3× with a punch) and looks soft, and the captions have nowhere to go but the forehead.
- Pro framing: face ≈ 30–38% of the frame height, eyes around 0.35–0.40 H, captions on the chest. `render_cuts --reframe auto` switches to **wide** when the tracked face is taller than 40% of the crop: the face-tracked picture is scaled so the face is ~30% of the height (centre at 0.40 H) over a blurred, darkened fill of the same frame. Upscale drops to about 1.6×, and the captions sit under the chin.
- `render_cuts` prints the upscale factor per source and a WARN above 2×.

## 5. Colour for phone footage

- iPhone records HDR by default (HLG / Dolby Vision). The scripts tone-map it with zscale (npl=203) and mobius. Tell the user to turn **HDR Video OFF** for the next shoot.
- **Grading order:**
  1. White balance on something neutral.
  2. Exposure: highlights 90–95 IRE, blacks just above 0.
  3. Skin on the vectorscope skin line, face at about 60–70 IRE [?].
  4. Then gently: contrast +4–8%, saturation +6–15%. These are the `--grade natural` and `--grade punchy` presets.
- **Phones already sharpen.** Don't sharpen again, or use only a light `cas=0.2` after downscaling 4K.
- **Low light:** `--vdenoise` (hqdn3d).
- **Handheld:** `--stabilize` (vidstab, 2-pass).

## 6. Story structure for a 30–60 s talking-head reel

1. **Hook (0–2 s):** the payoff line or a bold claim, plus on-screen hook text.
2. **Context (2–8 s):** why it matters, in one sentence.
3. **Body:** 2–4 beats with one idea each. Change the visual every 2–4 s.
4. **Payoff / CTA (last 3–5 s):** one CTA only ("salvează", "trimite unui prieten", "comentează X"). Avoid a long outro. If the speaker didn't say it, put it on screen: `pipeline.py --cta "SALVEAZĂ-L PENTRU MAI TÂRZIU"` (last 3 s, hook-style boxes, clear of face and captions).
5. **Loop:** the last line leads back into the first.

How to build it from `phrases.txt`:
- Choose phrases with `--select`, putting the strongest one first.
- Drop repetitions and weak lines.
- Keep total length near the goal. Usual ranges: Reels/TikTok 20–45 s, Shorts under 60 s (and under 60 s whenever there is music).

## Sources

- CapCut hooks guide; socialk.it TikTok editing guide; subscribr.ai (Shorts metrics); creatoressentials.com glossary; dataslayer.ai (Instagram 2025); epidemicsound.com (jump cuts); air.io and pixflow.net (retention editing); nofilmschool.com and vizard.ai (punch-ins); mysocial.io (presenter-led video); blitzcutai.com (caption sizes); openclip.app (caption styling and audio normalization); kapwing.com and opus.pro (caption styles); disabilityworld.org (WCAG 1.4.7); forasoft.com (LUFS targets); support.google.com/youtube/answer/15424877 (Shorts and music); dev.to (HDR tone mapping); videobgremover.com and Adobe HelpX (colour correction).
