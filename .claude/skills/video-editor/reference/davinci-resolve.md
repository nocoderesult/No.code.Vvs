# Handing the edit to DaVinci Resolve 21 (free) on the user's Mac

The user runs Resolve **free** 21.1 on a Mac M4. That means:

- No scripting API (it's Studio-only), so nothing can be automated inside Resolve.
- No Smart Reframe, Magic Mask or Voice Isolation.
- Export is limited to UHD 60p.
- Some Studio-only effects watermark the render [?].

Everything has to arrive as **files the user imports by hand**.

## What `export_resolve.py` writes (also via `pipeline.py --resolve`)

| File | What it is | Import with |
|---|---|---|
| `timeline.fcpxml` | FCPXML 1.10 with the same structure as auto-editor's `--export resolve`. The sequence has its own `<format>` at the cut list's (= the MP4's) frame rate, whatever rate the first clip has; offsets/durations are on that grid, clip starts on each source's grid. Times are unreduced frame multiples (`154/30s`); one asset per source, asset `start` = the media's embedded start timecode (0 if none); `media-rep src` = `file:///Users/Shared/Claude-Edit/<original name>`. Format names use the true rate (`FFVideoFormat720p2997` for 30000/1001). | File → Import → Timeline… |
| `timeline.edl` | CMX3600, UTF-8: one `AA/V` event per cut (separate V and A lines with the same number are read as a dissolve), an ASCII reel name plus `* FROM CLIP NAME:` with the real file name (diacritics kept — Resolve relinks by that name), record TC starting at 01:00:00:00, source TC from the file's `timecode` tag. **Only written when every source has the timeline's frame rate**: CMX3600 has one rate per file, so a 60p clip in a 25p timeline would need frame fields like `:34`. Otherwise it is skipped and CITESTE-MA points to the OTIO. | File → Import → Timeline… (clips already in the Media Pool) |
| `timeline.otio`, `timeline_fcp7.xml` | OpenTimelineIO (Resolve 18.5+ imports it) and FCP7 XML | File → Import → Timeline… |
| `subtitles.srt` | Edited-timeline subtitles (2 × 42 chars) | File → Import → Subtitle…, or drag it into the Media Pool [? not verified in the free version] |
| `captions_alpha.mov` (`--alpha`) | ProRes 4444 with alpha: the animated captions exactly as burned in | Put on V2 at the timeline start |
| `stems/voice.wav`, `stems/music_ducked.wav`, `stems/sfx.wav` | Mastered voice, ducked music and sound effects, 48 kHz / 24-bit, aligned to the timeline start. The voice chain's processing delay (RNNoise 12 ms) is removed, so the voice stem lines up with A1. | Put on A2/A3/A4 and mute A1 |
| `media/<name>_CFR.mp4` | A CFR copy (at the timeline rate, no timecode track) of any variable-frame-rate source. The timeline points at it, so cuts match the MP4 frame-for-frame. | Put next to the originals |
| `final.mp4` | Not included by default (the user already received it; `--include-final` adds it) | — |
| `CITESTE-MA_DaVinci.txt` | Step-by-step instructions in Romanian | — |

**Verification:**
- `export_resolve.py` parses the FCPXML and EDL it wrote with exact `Fraction`s: the sequence frameDuration must be 1/fps of the cut list, every clip's offset/start/duration must equal the cut list's frames, every asset start must equal the media's own start timecode, and EDL timecode fields must be valid for the timeline rate. The OTIO file is compared too. Any mismatch prints `ERROR: timeline check failed`, exits 4 and stops `pipeline.py` — don't ship that package.
- Don't verify with OTIO's `fcpx_xml` adapter: it floors rational times (`3952/30s` read as frame 3951, 29.97 read as 29 fps) and printed MISMATCH for correct files while passing broken ones (wrong sequence rate, zeroed timecode).
- Resolve itself can't run in the cloud container, so an actual import has **not** been tested.
- If FCPXML import fails on the user's machine, the EDL (when present) and OTIO files are the fallbacks.

## Paths and relinking

- The default media path is `/Users/Shared/Claude-Edit/`. That folder exists (or can be created) on every Mac, and needs no username.
- Simplest instruction for the user: "Cmd+Shift+G → /Users/Shared → create Claude-Edit → copy the original clips there, same names". With that, the import links with no relinking.
- If the user already has the clips elsewhere, give their folder with `--mac-dir "/Users/<name>/Movies/Proiect"`, or tell them to use one of these:
  - Media Pool → select the clips → right-click → **Relink Selected Clips…**
  - Import the clips into the Media Pool first, then import the timeline with "Automatically import source clips into media pool" unticked. Resolve then matches the clips by name and timecode.
- **Never** let absolute cloud paths (`/tmp/...`, `/home/user/...`) end up in a timeline file. auto-editor writes such paths by default.

## Vertical (9:16) in Resolve free

The FCPXML timeline is at the source resolution (for example 1920×1080). Writing a 1080×1920 sequence with per-clip `adjust-transform` / `adjust-conform` from the face track was considered, but whether free Resolve 21 honours those on FCPXML import ("Use sizing information") can't be tested here, and a wrongly applied conform would leave the user a worse starting point than the manual steps. So the package stays at the source resolution and `CITESTE-MA` lists a starting **Position X per clip**, computed from the median face-track centre of that clip (timeline px for 1080×1920 with "Scale full frame with crop", zoom 1.0). To work vertically:

1. In the Media Pool, right-click the timeline → Timelines → Timeline Settings…
2. Untick "Use Project Settings" and set 1080 × 1920.
3. Set "Mismatched resolution files" to **Scale full frame with crop**.
4. On each clip, set Inspector → Transform → Position X to the value from CITESTE-MA, then adjust by eye (Zoom for punch-ins).

If the user later confirms that Resolve keeps FCPXML transforms, emitting them is the next step.

For a pixel-identical vertical version, the user uses the rendered MP4 (or `--clean` = the version without captions) as the base clip in Resolve and adds titles or graphics on top.

## When the user wants to finish in Resolve

- **Grading only:** deliver `final_fara_subtitrari.mp4` (`pipeline.py --clean`), `captions_alpha.mov` and the stems.
  - The user grades the clean MP4, keeps the captions on V2, and exports.
  - Recommended Resolve export settings:
    - MP4, H.264, 1080×1920, 30 fps.
    - Quality: restrict to 12,000 Kb/s.
    - Audio: AAC 320 kb/s.
- **Re-cut by hand:** the FCPXML plus the original clips plus `subtitles.srt`.
