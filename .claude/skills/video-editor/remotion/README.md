# Expert motion pass (Remotion)

The ffmpeg pipeline (`../scripts/pipeline.py`) gives a clean, correct edit. This folder adds the layer that makes a reel
look produced: kinetic word captions, an animated hook, impact hits (flash + zoom blur + chromatic aberration + shake),
glitch and whip-pan transitions, light leaks, animated emoji, badges, an animated CTA and layered sound design.
It is the template used for the first client reel (two "proba" clips, 10.5 s). `src/Reel.tsx` keeps that reel's
timeline constants (`SWAP1`, `SWAP2`, `CUT_B`, beats, sticker list, `SFX` list): change them per project.

Built following the official Remotion Agent Skills (`npx skills add remotion-dev/skills`, or the "Remotion" plugin).

## Steps

1. Run the normal pipeline first, then render a high-quality base **without captions** (same flags as the pipeline's
   step 7, no `--ass`, `--crf 12`) to `work/clean.mp4`. Bake any per-clip colour fix into `public/base.mp4`.
2. Scaffold a project outside the repo and copy this template over it:
   ```bash
   npx create-video@latest --yes --blank --no-tailwind reel && cd reel
   npx remotion add @remotion/media @remotion/effects @remotion/transitions @remotion/lottie @remotion/fonts
   cp -r <skill>/remotion/src <skill>/remotion/remotion.config.ts .
   npx remotion browser ensure
   ```
3. Data: `python3 <skill>/remotion/prep.py work/words.json work/cuts.json public/base.mp4 src` writes `src/data.json`
   (word captions on the output timeline, 1–3 words per chunk, and a face box per frame for sticker placement).
4. Assets in `public/` (not committed; download per project):
   - `voice.wav`: the pipeline's `work/mix.wav`.
   - `sfx/`: meme/impact SFX from `https://remotion.media/<name>.wav` (vine-boom, whoosh, whip, shutter-modern, ding,
     anime-wow, record-scratch, snapchat-notification, switch, bruh, …; list in the remotion-markup `sfx.md` rule) and
     CC0 Kenney packs from `github.com/kapishdima/soundcn` (`assets/kenney_*`: glitch_00x, tick_00x, drop_00x,
     impactPunch_*). Convert .ogg to 48 kHz wav. `riser.wav`: `python3 <skill>/remotion/synth_sfx.py ev.json 0.6 public/sfx/riser.wav` with `ev.json` = `[{"t":0.55,"kind":"riser","db":0}]` (also synthesizes impact, whoosh, swell, pop, ding, shutter).
   - `emoji/<codepoint>.json`: Google Noto animated emoji (CC BY 4.0) from
     `https://fonts.gstatic.com/s/e/notoemoji/latest/<codepoint>/lottie.json` (1f631 😱, 1f440 👀, 1f602 😂, 1f44c 👌,
     1f447 👇, 1f525 🔥, 1f92f 🤯).
   - `fonts/`: Montserrat 900 woff2, latin + latin-ext subsets (URLs from
     `https://fonts.googleapis.com/css2?family=Montserrat:wght@900` with a browser User-Agent). The headless browser
     cannot reach Google Fonts through the proxy, so `@remotion/google-fonts` fails: load local files with `@remotion/fonts`.
5. Check frames before a full render: `npx remotion render Reel out/frames --frames=0,41,44,150,190,262 --image-format=jpeg`,
   tile them and look. Effects need WebGL2: in this container only `swangle` works (`remotion.config.ts`).
6. Render: `npx remotion render Reel out/raw.mov --codec h264 --crf 16 --audio-codec pcm-16` (~1.7 min for 10 s).
7. Master and deliver: measure integrated loudness, apply static gain to −14 LUFS, true-peak limit at 4× oversampling
   (`aresample=192000,alimiter=limit=0.79,aresample=48000`), then encode with `setparams` BT.709 tags, CRF 18,
   maxrate 10M, AAC 256k, faststart. Run `../scripts/qc.py` on the result and look at the sheets.

## Craft notes from the first reel

- Hook text must be readable on frame 0: start springs at ≤ 1.2× scale or the text leaves the frame.
- Reserve every word of a caption chunk in the layout (opacity 0 until spoken) or the line re-centres and jumps.
  Keep 20 px margins per word and the active-word scale ≤ 1.06 so neighbours never touch.
- Light leak over a cut: ≤ 16 frames at 0.6 opacity, or it hides the face of the next clip.
- Stickers: pick one static spot per sticker that avoids the face for its whole interval (`bestSpot`) instead of
  following the face; moving stickers look cheap.
- Meme SFX land best in silences; keep anything under speech ≥ 10 dB quieter.
