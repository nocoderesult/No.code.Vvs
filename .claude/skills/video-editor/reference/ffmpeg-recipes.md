# Verified ffmpeg/Python recipes and their measured numbers

**Environment:** ffmpeg 6.1.1, Python 3.13, 4 CPUs, no GPU.

Every recipe here was run in the container and measured; the scripts use them. Read this file when you need to go beyond the scripts or debug them.

## Cut rendering and A/V sync

**Method:** trim/atrim + concat in ONE filtergraph, with cut points snapped to the frame grid (`Fraction(round(t*fps))/fps`).
- At 48 kHz and 30 fps, one frame is exactly 1600 samples.
- Each audio segment gets a 6 ms `afade` at both ends, which prevents clicks and moves sync by under 3 ms.

**Measured, research run (49 cuts, 120 s):**

| Method | Max A/V offset |
|---|---|
| **Frame-aligned trim+concat** | **0.1 ms**, durations identical |
| Same, cut points not aligned | 42 ms, and +0.24 s duration |
| `select`/`aselect` with `between(t)` | up to 185 ms |
| Per-segment AAC files + concat demuxer | up to 198 ms (AAC priming) |
| Per-segment PCM-in-MKV + concat | 3.9 ms |

**Measured, skill run (`render_cuts.py`).**
- **Test:** a flash+beep source, 34–37 random cuts with 3 segments moved to the front (reordered), on a CFR source and on a VFR copy of it. The offset was compared against the source's own offset.

| Path | Result |
|---|---|
| Audio inline | Offset unchanged: max 20.1 ms in the source vs max 20.1 ms after the cut |
| `--audio-only` → master → `--audio` | Same |
| VFR source | Same, after VFR→CFR |
| MP4 stream durations | Video and audio equal within 1 ms; the frame count is exact (1001 frames = 33.367 s) |

- **Reordered segments** (cold open): a run is a group of consecutive segments in increasing source time. Each run opens the source again as a new `-i` input, so split branches never buffer frames.
- **Long graphs:** pass them with `-filter_complex_script graph.txt`. ffmpeg 7.1+ renames this to `-/filter_complex`.
- **Output length:** limit it with `-t <exact total>` rather than `-shortest`.

## Normalizing phone footage

Put these filters in front of the trim (render_cuts does this inline):

- **VFR → CFR:** `fps=F:start_time=0` on video, and `aresample=48000:async=1:first_pts=0` on audio.
  - Also decode every analysis audio with `first_pts=0`, so a late-starting audio track stays aligned with video time.
  - `start_time=0` matters when the VIDEO starts late (stream-copy trims, screen recordings, some Android files: video start_time 0.2, audio 0.0). Plain `fps=F` starts the video at its first frame, so every segment before it played 200 ms early (measured A−V +213 ms, QC FAIL "video 10.033 s / audio 10.233 s"). With `start_time=0` the first frame is repeated to fill the gap: A−V +1.2 ms, the same as the source. `render_cuts` then asserts that the video and audio stream durations match within one frame.
- **Rotation:** ffmpeg auto-rotates (the display matrix) in `-vf` and `-filter_complex`. OpenCV auto-rotates too, so face coordinates match.
- **HDR (HLG or PQ) → SDR:** `zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=mobius:param=0.5:desat=0,zscale=t=bt709:m=bt709:r=tv:d=error_diffusion,format=yuv420p`.
  - Mean RGB error against the SDR original: 9.2, versus 27.4 for the common hable/npl=100 recipe (which is also too dark) and 41 for naive conversion.
  - Speed: about 1.1× realtime at 1080p; 4K is roughly 4× slower.
  - zscale fails with "no path between colorspaces" on frames with UNTAGGED colour. Tag them first with `setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv`.
- **Full range (yuvj) or BT.601 → TV-range BT.709:** `scale=in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709`. Set `in_color_matrix` explicitly, because swscale assumes BT.601 for untagged HD.
- **Final tags:** `setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709`, plus the x264 `-colorspace`/`-color_*` flags.

## Reframing

- **Face track:**
  - YuNet (`cv2.FaceDetectorYN`, bundled 230 KB model) at 640 px wide, sampled at 6 fps.
  - Median filter (k=5) → interpolate per frame → deadzone → offline Gaussian smoothing (σ 0.5 s, no lag).
  - The crop is driven by `sendcmd=f=cmds.txt,crop@rf=w=608:h=1080:x=..:y=0`; each line in cmds.txt looks like `0.0333 crop@rf x 708;`.
  - **Measured:** 5–10 s of analysis for 40 s of 1080p; on the test talking head the face stayed centred throughout.
  - **Settings:** deadzone 0.02·W for a moving subject. Use 0.06·W for a static talking head: it's steadier, but lags about 120 px on a fast move.
- **Vertical crops** (9:16 → 1:1, 4:5): the face centre is placed at 0.38 of the height (natural headroom).
- **Blur fill:**
  ```
  split[a][b];[a]scale=W/4:H/4:force_original_aspect_ratio=increase,crop=W/4:H/4,gblur=sigma=12,eq=brightness=-0.06,scale=W:H[bg];[b]scale=W:H:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2
  ```
- **Auto rule:**

  | Situation | Mode |
  |---|---|
  | Same aspect | scale |
  | Wider source with faces in ≥ 25% of samples | track |
  | Wider source, face taller than 40% of the crop (close-up selfie) | wide: face-track crop scaled so the face is 30% of H, centred at 0.40 H, over the blur fill |
  | Taller source where the crop keeps ≥ 50% (9:16 → 1:1) | track |
  | Otherwise | blur |

- **Wide:** `[fg]sendcmd=…,crop@rf=w=CW:h=SH:x=..,scale=W:BH[fg];[bg][fg]overlay=0:TOP` with `k = 0.30·H / (face_h·SH)` (clamped between W/SW and H/SH), `CW = W/k`, `BH = SH·k`. Measured on a 1280×720 selfie with the face at 51% of the height: upscale 2.67× → 1.56×, face band 624–1085 px, captions under the chin at y 1157 instead of on the forehead.
- **Zoom cuts:** a kept segment is split at the `zooms` points from `plan_cuts` into several `trim` branches of the same `split` with contiguous frame ranges (no time jump), and every 2nd shot gets the punch crop. Audio stays one `atrim` per segment, so nothing changes for sync.

## Zoom / punch-in jitter

Jitter here is the standard deviation of the second difference of the zoom centre, in px:

| Method | Jitter |
|---|---|
| `zoompan` | 1.14 / 1.85 px (visible) |
| `zoompan` on a 4× upscale | 0.42 / 0.67 px |
| **`perspective` with `eval=frame`** | **0.23 / 0.49 px** (the variable is `in`, the frame index; there is no `t`) |
| `scale=eval=frame` + `crop` | broken |

- **Static punch-in:** `crop=w='trunc(iw/1.12/2)*2':h=..:x='max(0,min(iw-ow,AX*iw-ow/2))':y=..,scale=W:H,setsar=1`.
  - It is anchored at the face (AX, AY). `setsar=1` is required, or concat fails with an SAR 7712:7713 mismatch.

## Audio

- **Denoise comparison** at input SNR 7.5 dB:

  | Filter | SI-SDR | Noise in pauses |
  |---|---|---|
  | `arnndn=m=sh.rnnn` | 10.5 dB | −61.7 dB |
  | `afftdn` | 8.3 dB | −39.6 dB |
  | Input | 7.9 dB | — |

  - The `sh.rnnn` model is bundled. Its README states it is not subject to copyright.
- **Chain latency:** RNNoise delays the voice by 12 ms and afftdn by 27 ms (HPF+EQ alone 2 ms), measured by cross-correlating `cut.wav` with the processed voice. Uncompensated, every output had the sound 12 ms behind the picture and the voice stem 12–27 ms behind A1 in Resolve. `audio_master` measures the lag of its own chain on each file and trims it (`atrim=start=lat,asetpts=PTS-STARTPTS`, then pads to the input length).
- **Leveling:** when the chained voice has LRA above 10 LU (near/far from the phone), an offline gain rider moves 3 s loudness toward the median (±12 dB, smoothed, held through pauses) before loudness normalization.
- **Loudness:** pass 0 measures after the chain, then applies `volume=(target−I0)dB` and `alimiter`, then two-pass loudnorm with `linear=true`.
  - Plain two-pass loudnorm fell back to *dynamic* mode on −27 LUFS input.
  - Pass 0 alone was not enough on speech with big level swings (8 s sections alternating −38 / −12 LUFS): loudnorm still went dynamic and rode the quiet sections unevenly (−30, −24, −26 LUFS short-term), LRA 19.3. If linear mode is impossible after leveling, the script now uses a static gain + 4× oversampled true-peak limiter instead, and says so.
  - Measured: −14.0 LUFS, −1.6 dBTP on the WAV, about −1.7 dBTP after AAC 256k.
- **Ducking:** use an offline gain curve in numpy from the voice envelope, not `sidechaincompress`.
  - With `sidechaincompress` (threshold 0.02, ratio 4) the music ended up 31 dB under the voice: too deep and hard to predict.
  - With the curve, `--duck 12` measured −32.0 LUFS for the bed under constant speech and −28.5 LUFS integrated on a clip with pauses (the bed rises in the gaps); the voice sits about 18–22 dB above it. On a tight-cut reel (voice on 94% of the time) that was −31.5 LUFS, 21 dB under the voice: inaudible on a phone.
  - So the bed level is now set relative to the voice: `--music-under 15` (dB under the voice while talking) with `--duck 8`. Measured on a 40 s reel: ducked bed −28.8 LUFS = 14.7 LU under the voice.
- **amix:** always use `normalize=0`, or the voice level drops.
- **True-peak limiting:** `aresample=192000,alimiter=...,aresample=48000` gives an oversampled, approximately true-peak limiter.
- **arnndn:** needs 48 kHz input. Don't combine `-ar 48000` with `aresample=16000` in one chain; it silently resamples back and breaks the time axis.

## Captions (libass)

- **Font:** `Fontname: Inter Black` with `Bold=0` resolves to Inter-Black.otf.
  - The family "Inter Bold" does NOT exist. Bold is `Fontname Inter` with `Bold=-1`.
- **Size:** libass font size = ascent + descent. The PIL size is the ASS size × 0.8157 (measured for Inter).
- **Layout:**
  - Every word is its own event with `\an5\pos(x,y)`.
  - Word slots are reserved at 110% width so the active-word pop (`\t(0,80,\fscx110\fscy110)`) never touches its neighbours.
  - Gap between words = space + 2×outline + 0.07×size.
  - Line breaks are balanced by DP, which avoids orphan words. Sentence chunks are split evenly ("sfaturi." alone never happens).
- **Header:** `ScaledBorderAndShadow: yes`, `WrapStyle: 2`, `YCbCr Matrix: TV.709`, PlayRes equal to the canvas.
- **Hook:** `\fad(0,200)`, with no fade-in, so it is visible on frame 0. The first caption chunk is extended back to t=0.
- **Burn-in:** `subtitles=filename='/abs/path.ass'`, escaping `\` and `:`. An apostrophe can't be escaped reliably inside a quoted filter argument (two escaping levels): a folder named "Reel lui Ion's" failed with "Option not found". `vcommon.filter_file()` copies any .ass / sendcmd file whose path isn't plain ASCII into the render's temp dir first (render_cuts, export_resolve --alpha, reframe --preview).
- **Transparent overlay for Resolve:**
  ```
  ffmpeg -f lavfi -i color=c=black@0.0:s=1080x1920:r=30:d=DUR,format=yuva444p -vf subtitles=f.ass:alpha=1 -c:v prores_ks -profile:v 4444 -qscale:v 9 -pix_fmt yuva444p10le -vendor apl0 captions_alpha.mov
  ```
  - About 2 MB/s.

## Inspection

- **Contact sheet:** `contact_sheet.py` grabs accurate-seek frames with PIL tiling and timestamps. It tone-maps HDR sources so they look the way the export will. `--scenes` uses PySceneDetect `AdaptiveDetector`.
- **Waveform:** `showwavespic` draws on a transparent background, so overlay it on `color=c=black`.
- **Detection in QC:** `silencedetect=n=-45dB:d=0.9` finds missed cuts; `blackdetect` and `freezedetect` find dead picture.

## Test media

- **Romanian speech:** `pip install --break-system-packages piper-tts` with the voice `ro_RO-mihai-medium`. Download it with `curl -C -`; the Python downloader truncated it.
  - `scripts/dev/make_test_media.py` builds the test footage.
- **Test face:** the public-domain NASA portrait from `gitlab.com/scikit-image/data/-/raw/master/astronaut.png`.
  - github raw is an LFS pointer, and media.githubusercontent.com returned 404.
