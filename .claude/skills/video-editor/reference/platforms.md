# Platform specs: safe zones, export settings, length limits

## Safe zones on a 1080×1920 canvas, in px

No platform publishes a safe zone for organic posts. The figures below are ad specs or community measurements. `vcommon.SAFE_ZONES` holds the same numbers.

| Platform | Top | Bottom | Left | Right | Notes |
|---|---|---|---|---|---|
| Instagram Reels | 269 (14%) | 672 (35%) | 65 | 65 | Meta ad spec, August 2026. Bottom is 768 if disclaimers are shown. |
| TikTok in-feed | 240 | 660 | 120 | 120 | Also keep the right 300 px clear below y = 840 (action rail). 3P measurement, 2026-09. |
| YouTube Shorts | 288 | 672 | 48 | 192 | 3P measurement. |
| **Universal** (default) | 290 | 680 | 120 | 192 | Safe area x 120–888, y 290–1240. |

- **Organic posts** [3P, sources disagree]: TikTok about 480 bottom and 120–150 right. Shorts about 380 top, 380 bottom, 60 left and 120 right.
- **Instagram profile grid:** shows the middle 3:4 (1080×1440), cutting 240 px from the top and bottom. Keep the cover title inside that area (`cover.py` places it in y 270–1650, clear of the face).
- **Where the scripts place things:**
  - Captions sit at a centre of y = 1130 with text at x ≈ 200–880.
  - The hook (and the CTA end card) is top-aligned at y ≈ 313 and moves or shrinks to keep the eyes, the mouth and the caption line clear.
  - `captions.py` measures every event box (pop scale, outline, shadow included) and fails if one leaves the zone; `qc.py` repeats the check on the final .ass.
  - `qc_captions.jpg` and `contact_sheet.py --safe universal` shade the UI zones red so you can check placement; `qc_sheet.jpg` (`--outline`) only draws thin lines, so colours there are true.

## Export

| Use | Settings |
|---|---|
| Reels / TikTok / Shorts | 1080×1920, H.264 High, 4.2, yuv420p, CFR at the native rate (30 typical), CRF 20 with maxrate 10M (14M at 60 fps), GOP 2 s, BT.709 TV range tags, AAC-LC 48 kHz stereo 256k, `+faststart`. The apps re-encode to a few Mbps, so more only makes the download bigger (a 40 s reel from noisy 720p footage: 49 MB at 9.9 Mbps; before, CRF 18/16M gave 67.6 MB for 43 s) |
| YouTube 16:9 [OFFICIAL] | 1920×1080 (or 1440p/4K for better YouTube re-encodes [?]), H.264 High, progressive, 2 B-frames, closed GOP of half the frame rate (`--gop youtube`), native frame rate, 8 Mbps at 1080p30 / 12 at 1080p60 minimum (the scripts: CRF 18, maxrate 16M / 20M at 60 fps), AAC 48 kHz |

- **Instagram** downsamples anything above 8–12 Mbps. Upload H.264, not HEVC. Tell the user to turn on "Upload at highest quality" in the Instagram app [?: the setting may have moved].
- **TikTok** compresses 4K to 1080p, so upload 1080p.

## Length limits

| Platform | Limit |
|---|---|
| Reels | 3 min in-app; uploads up to 15 min, 20 min in testing [?] |
| TikTok | 10 min in-app; 60 min by upload |
| YouTube Shorts [OFFICIAL] | Up to 3 min, square or vertical only (16:9 is never a Short). Over 1 min with a Content ID music claim, the Short is blocked worldwide. |

`qc.py` FAILs a video over the platform maximum (180 s for reels/shorts/vertical, 600 s for tiktok) — a 181 s "Short" is not a Short — and `plan_cuts.py --platform-max` (passed by the pipeline) warns at planning time.

## Loudness

- Deliver at −14 LUFS integrated, ≤ −1.5 dBTP before AAC, LRA ≤ 11. `qc.py` FAILs more than 1 LU off target or a true peak above −1 dBTP after encoding; LRA above 11 is a WARN.
- YouTube turns loud audio down to −14 and never boosts quiet audio.
- TikTok and Instagram publish no target and use adaptive normalization. A few guides push −10 to −12 LUFS for them [?]; the scripts don't, because louder masters distort after AAC encoding.
