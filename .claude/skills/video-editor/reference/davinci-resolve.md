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
| `timeline.fcpxml` | FCPXML 1.10 with the same structure as auto-editor's `--export resolve`. Times are unreduced frame multiples (`154/30s`); one asset per source; `media-rep src` = `file:///Users/Shared/Claude-Edit/<original name>` | File → Import → Timeline… |
| `timeline.edl` | CMX3600: one `AA/V` event per cut (separate V and A lines with the same number are read as a dissolve), `* FROM CLIP NAME:`, record TC starting at 01:00:00:00, source TC from the file's `timecode` tag | File → Import → Timeline… (clips already in the Media Pool) |
| `timeline.otio`, `timeline_fcp7.xml` | OpenTimelineIO (Resolve 18.5+ imports it) and FCP7 XML | File → Import → Timeline… |
| `subtitles.srt` | Edited-timeline subtitles (2 × 42 chars) | File → Import → Subtitle…, or drag it into the Media Pool [? not verified in the free version] |
| `captions_alpha.mov` (`--alpha`) | ProRes 4444 with alpha: the animated captions exactly as burned in | Put on V2 at the timeline start |
| `stems/voice.wav`, `stems/music_ducked.wav` | Mastered voice and ducked music, 48 kHz / 24-bit, aligned to the timeline start | Put on A2/A3 and mute A1 |
| `media/<name>_CFR.mp4` | A CFR copy of any variable-frame-rate source. The timeline points at it, so cuts match the MP4 frame-for-frame. | Put next to the originals |
| `final.mp4` | Reference render | — |
| `CITESTE-MA_DaVinci.txt` | Step-by-step instructions in Romanian | — |

**Verification:**
- All four timeline files were read back with OpenTimelineIO, and every clip's in and out frames matched the cut list exactly (8 of 8, two sources, one of them a VFR source replaced by its CFR copy).
- Resolve itself can't run in the cloud container, so an actual import has **not** been tested.
- If FCPXML import fails on the user's machine, the EDL and OTIO files are the fallbacks.

## Paths and relinking

- The default media path is `/Users/Shared/Claude-Edit/`. That folder exists (or can be created) on every Mac, and needs no username.
- Simplest instruction for the user: "Cmd+Shift+G → /Users/Shared → create Claude-Edit → copy the original clips there, same names". With that, the import links with no relinking.
- If the user already has the clips elsewhere, give their folder with `--mac-dir "/Users/<name>/Movies/Proiect"`, or tell them to use one of these:
  - Media Pool → select the clips → right-click → **Relink Selected Clips…**
  - Import the clips into the Media Pool first, then import the timeline with "Automatically import source clips into media pool" unticked. Resolve then matches the clips by name and timecode.
- **Never** let absolute cloud paths (`/tmp/...`, `/home/user/...`) end up in a timeline file. auto-editor writes such paths by default.

## Vertical (9:16) in Resolve free

The FCPXML timeline is at the source resolution (for example 1920×1080), because the face-tracked crop can't be expressed reliably in FCPXML for Resolve. To work vertically:

1. In the Media Pool, right-click the timeline → Timelines → Timeline Settings…
2. Untick "Use Project Settings" and set 1080 × 1920.
3. Set "Mismatched resolution files" to **Scale full frame with crop**.
4. On each clip, adjust Inspector → Transform → Position X / Zoom.

For a pixel-identical vertical version, the user uses the rendered MP4 (or `--clean` = the version without captions) as the base clip in Resolve and adds titles or graphics on top.

## When the user wants to finish in Resolve

- **Grading only:** deliver `final_fara_subtitrari.mp4` (`pipeline.py --clean`), `captions_alpha.mov` and the stems.
  - The user grades the clean MP4, keeps the captions on V2, and exports.
  - Recommended Resolve export settings:
    - MP4, H.264, 1080×1920, 30 fps.
    - Quality: restrict to 12,000 Kb/s.
    - Audio: AAC 320 kb/s.
- **Re-cut by hand:** the FCPXML plus the original clips plus `subtitles.srt`.
