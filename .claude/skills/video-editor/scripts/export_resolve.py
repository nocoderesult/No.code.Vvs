#!/usr/bin/env python3
"""Export the edit (cuts.json) as a DaVinci Resolve (free) package for manual finishing on the user's Mac.

Writes into OUTDIR:
  timeline.fcpxml   FCPXML 1.10 (File > Import > Timeline). Clips point at the ORIGINAL file names under
                    --mac-dir (default /Users/Shared/Claude-Edit, exists on every Mac) -> no relinking needed if
                    the user copies the originals there; otherwise Relink / import-into-Media-Pool-first works.
                    The sequence has its own <format> at the cut list's frame rate (= the MP4's), whatever the
                    first clip's rate is; clip offsets/durations are on that grid, clip starts on each source's grid.
  timeline.edl      CMX3600 fallback (one AA/V event per cut + "* FROM CLIP NAME", UTF-8). Only written when every
                    source has the timeline's frame rate: CMX3600 has one rate per file, so a 60p clip in a 25p
                    timeline can't be described (CITESTE-MA says so).
  timeline.otio     OpenTimelineIO (Resolve 18.5+ imports it), and timeline_fcp7.xml, if opentimelineio is installed.
  subtitles.srt     (--srt) edited-timeline subtitles;  captions_alpha.mov (--alpha) ProRes 4444 overlay of the
                    burned captions with transparency;  stems (--stems) voice/music WAVs; CITESTE-MA_DaVinci.txt.
Cut points are frame-exact. Variable-frame-rate phone clips get a CFR copy in media/ at the TIMELINE rate (the
same conversion the render does) without a timecode track, and the timeline points to it, so Resolve matches
the MP4 frame-for-frame. Asset start = the media file's own embedded start timecode (0 if it has none).
Verified by parsing the written FCPXML/EDL back with exact fractions (sequence frame duration, every clip's
offset/start/duration, asset start vs the media's timecode, EDL timecode fields); any mismatch -> exit 4.
Resolve itself is not available in the cloud container. The final MP4 is NOT copied in (the user already has
it; --include-final to add it).

Examples:
  export_resolve.py work/cuts.json -o out/davinci --srt out/final.srt --stems work/stems
  export_resolve.py work/cuts.json -o out/davinci --alpha work/captions.ass --format reels --zip
  export_resolve.py work/cuts.json -o out/davinci --mac-dir "/Users/ana/Movies/Reel 12" --name "Reel 12"
"""
import argparse
import os
import re
import shutil
import sys
import tempfile
import urllib.parse
import xml.etree.ElementTree as ET
from fractions import Fraction
from xml.sax.saxutils import quoteattr

import vcommon as vc

README = """CUM DESCHIZI MONTAJUL ÎN DAVINCI RESOLVE (varianta gratuită)
=============================================================

Ce e în folder:
  timeline.fcpxml      montajul (tăieturile) – se importă în Resolve
  {edl_line}
  timeline.otio        variantă de rezervă, dacă FCPXML nu merge
  subtitles.srt        subtitrările pe timeline-ul editat
  captions_alpha.mov   subtitrările animate, cu fundal transparent (dacă există)
  stems/               vocea masterizată (voice.wav), muzica cu ducking (music_ducked.wav), efectele (sfx.wav), 48 kHz
  media/               (dacă există) copii CFR ale clipurilor cu frame rate variabil – pune-le lângă originale
  Video-ul final ({final_name}) ți l-am trimis separat; folosește-l ca referință.

PASUL 1 – clipurile originale
  Montajul folosește fișierele tale ORIGINALE: {names}
  Cel mai simplu: în Finder apasă Cmd+Shift+G, scrie {mac_dir} și pune acolo clipurile originale,
  cu exact aceleași nume{media_note}. (Dacă folderul nu există, creează-l.)

PASUL 2 – importul
  DaVinci Resolve → File → Import → Timeline… → alege timeline.fcpxml.
  În fereastra de import lasă bifat „Automatically import source clips into media pool”.
  Dacă clipurile apar roșii (offline): selectează-le în Media Pool → click dreapta →
  „Relink Selected Clips…” → alege folderul unde ai clipurile (Resolve le găsește după numele fișierului).
  Alternativă: importă întâi clipurile în Media Pool, apoi importă timeline-ul cu bifa de mai sus DEBIFATĂ
  (Resolve le potrivește după nume și timecode).
  Dacă FCPXML dă eroare: {fallback}

PASUL 3 – format vertical (Reels/TikTok/Shorts)
  Timeline-ul vine la rezoluția clipului original ({src_res}), {fps} fps. Pentru 9:16:
  click dreapta pe timeline în Media Pool → Timelines → Timeline Settings… → debifează „Use Project Settings” →
  rezoluție 1080 x 1920 → la „Mismatched resolution files” alege „Scale full frame with crop”.
  Apoi, pe fiecare clip: Inspector → Transform → Position X ca să încadrezi fața
  (Smart Reframe există doar în Resolve Studio; în video-ul final eu am făcut deja încadrarea automată).
{positions}
PASUL 4 – subtitrări și sunet
  Subtitrări editabile: File → Import → Subtitle… → subtitles.srt, apoi trage-le pe timeline
  (sau trage fișierul .srt direct în Media Pool).
  Subtitrări animate ca în video-ul final: pune captions_alpha.mov pe pista V2, la începutul timeline-ului
  (merge doar dacă timeline-ul e 1080x1920 și nu schimbi tăieturile).
  Sunet masterizat: pune stems/voice.wav pe A2 și stems/music_ducked.wav pe A3, de la început,
  și dă mute la A1 (sunetul original).

PASUL 5 – export
  Pagina Deliver → Custom Export: MP4, H.264, 1080x1920 (sau 1920x1080), {fps} fps,
  „Restrict to” 10000 Kb/s, audio AAC 320 kb/s. Pentru YouTube 16:9 poți urca subtitles.srt separat ca subtitrare.
"""


def tc_frames(tc, fps):
    if not tc:
        return 0
    try:
        hh, mm, ss, ff = [int(x) for x in tc.replace(";", ":").split(":")]
    except ValueError:
        return 0
    nom = round(float(fps))
    return ((hh * 60 + mm) * 60 + ss) * nom + ff  # NDF assumption (phones write NDF)


def frames_tc(n, fps):
    nom = round(float(fps))
    return f"{n // (3600 * nom):02d}:{n // (60 * nom) % 60:02d}:{n // nom % 60:02d}:{n % nom:02d}"


def rate_token(fps):
    """FCP format-name rate: 23.976 -> 2398, 29.97 -> 2997, 59.94 -> 5994, 25 -> 25."""
    f = vc.frac(fps)
    if f.denominator == 1:
        return str(f.numerator)
    return {Fraction(24000, 1001): "2398", Fraction(30000, 1001): "2997", Fraction(60000, 1001): "5994"}.get(
        f, f"{float(f):.2f}".replace(".", ""))


class Src:
    def __init__(self, info, mac_dir, name=None):
        self.info = info
        self.name = name or info["name"]
        self.fps = vc.frac(info["fps"])
        self.fd = Fraction(1) / self.fps
        self.tc0 = tc_frames(info.get("timecode"), self.fps)
        self.nframes = int(round(info["duration"] * float(self.fps)))
        self.url = "file://" + urllib.parse.quote(os.path.join(mac_dir, self.name))

    def frame(self, t):
        return int(round(t * float(self.fps)))


def build(cuts, mac_dir, outdir=None, mezzanine=True):
    """VFR phone clips get a CFR mezzanine (media/<name>_CFR.mp4) at the timeline rate, made with the SAME fps
    conversion as the render, so the Resolve timeline matches the MP4 frame-for-frame (NLEs play VFR clips with
    drift). Clips: (src, first source frame, end source frame, timeline frames)."""
    fps = vc.frac(cuts["fps"])
    segs = vc.align_segments(cuts["segments"], fps)
    srcs = []
    for s in cuts["sources"]:
        info = vc.media_info(s["path"])
        if info.get("vfr") and mezzanine and outdir:
            from normalize import normalize
            name = os.path.splitext(info["name"])[0] + "_CFR.mp4"
            dst = os.path.join(outdir, "media", name)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.exists(dst) or vc.frac(vc.media_info(dst)["fps"]) != fps:
                normalize(info["path"], dst, fps=fps, keep_tc=False)
            m = vc.media_info(dst)        # its own embedded timecode (none) -> asset start
            srcs.append(Src(m, mac_dir, name))
            print(f"  VFR source {info['name']} -> CFR {fps} fps copy media/{name} (timeline points to it)")
        else:
            srcs.append(Src(info, mac_dir))
    clips = []
    for g in segs:
        s = srcs[g["src"]]
        a, b = s.frame(g["S"]), s.frame(g["E"])
        if b > a:
            clips.append((g["src"], a, b, g["fe"] - g["fs"]))
    return fps, srcs, clips


def t_str(frames, fd):
    return "0s" if frames == 0 else f"{frames * fd.numerator}/{fd.denominator}s"


def fcpxml(fps, srcs, clips, name):
    fd = Fraction(1) / fps
    fmts, res = {}, []

    def fmt_id(w, h, rate):
        key = (w, h, rate)
        if key not in fmts:
            fid = f"r{len(fmts) + 1}"
            fmts[key] = fid
            rfd = Fraction(1) / rate
            res.append(f'    <format id="{fid}" name="FFVideoFormat{h}p{rate_token(rate)}" '
                       f'frameDuration="{rfd.numerator}/{rfd.denominator}s" width="{w}" height="{h}" '
                       f'colorSpace="1-1-1 (Rec. 709)"/>')
        return fmts[key]
    s0 = srcs[clips[0][0]].info if clips else srcs[0].info
    seq_fmt = fmt_id(s0["w"], s0["h"], fps)        # the sequence runs at the cut list / MP4 rate
    for s in srcs:
        s.fid = fmt_id(s.info["w"], s.info["h"], s.fps)
    n0 = len(res)
    for i, s in enumerate(srcs):
        s.aid = f"r{n0 + i + 1}"
        base = os.path.splitext(s.name)[0]
        res.append(f'    <asset id="{s.aid}" name={quoteattr(base)} start="{t_str(s.tc0, s.fd)}" '
                   f'duration="{t_str(s.nframes, s.fd)}" hasVideo="1" format="{s.fid}" '
                   f'hasAudio="{1 if s.info.get("has_audio") else 0}" audioSources="1" '
                   f'audioChannels="{s.info.get("channels") or 2}" audioRate="{s.info.get("sample_rate") or 48000}">\n'
                   f'      <media-rep kind="original-media" src={quoteattr(s.url)}/>\n    </asset>')
    spine, off = [], 0
    for si, a, b, dur_tl in clips:
        s = srcs[si]
        spine.append(f'        <asset-clip name={quoteattr(os.path.splitext(s.name)[0])} ref="{s.aid}" '
                     f'offset="{t_str(off, fd)}" start="{t_str(a + s.tc0, s.fd)}" duration="{t_str(dur_tl, fd)}" '
                     f'tcFormat="NDF" format="{s.fid}"/>')
        off += dur_tl
    resources = "\n".join(res)
    body = "\n".join(spine)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>
<fcpxml version="1.10">
  <resources>
{resources}
  </resources>
  <library>
    <event name={quoteattr(name)}>
      <project name={quoteattr(name)}>
        <sequence format="{seq_fmt}" duration="{t_str(off, fd)}" tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">
          <spine>
{body}
          </spine>
        </sequence>
      </project>
    </event>
  </library>
</fcpxml>
"""


def reel_name(name):
    r = "".join(c for c in os.path.splitext(vc.fold(name).upper())[0] if c.isascii() and c.isalnum())[:8]
    return r or "AX"


def edl_possible(fps, srcs, clips):
    return all(srcs[si].fps == fps for si, *_ in clips)


def edl(fps, srcs, clips, name):
    """CMX3600, one frame rate for all timecodes (only called when every clip source runs at `fps`).
    Reel names are ASCII (8 chars); the real file name, diacritics included, is on the UTF-8 comment line."""
    lines = [f"TITLE: {name[:70] or 'Montaj'}", "FCM: NON-DROP FRAME", ""]
    rec = 3600 * round(float(fps))  # record TC starts 01:00:00:00 (Resolve default)
    for i, (si, a, b, dur) in enumerate(clips, 1):
        s = srcs[si]
        lines.append(f"{i:03d}  {reel_name(s.name):<8} AA/V  C        {frames_tc(a + s.tc0, s.fps)} "
                     f"{frames_tc(a + s.tc0 + dur, s.fps)} {frames_tc(rec, fps)} {frames_tc(rec + dur, fps)}")
        lines.append(f"* FROM CLIP NAME: {s.name}")
        lines.append("")
        rec += dur
    return "\n".join(lines) + "\n"


def otio_files(fps, srcs, clips, name, base):
    try:
        import opentimelineio as otio
    except ImportError:
        return []
    f = float(fps)
    tl = otio.schema.Timeline(name=name, global_start_time=otio.opentime.RationalTime(3600 * f, f))
    for kind, tname in ((otio.schema.TrackKind.Video, "V1"), (otio.schema.TrackKind.Audio, "A1")):
        tr = otio.schema.Track(name=tname, kind=kind)
        for si, a, b, dur in clips:
            s = srcs[si]
            sf = float(s.fps)
            ref = otio.schema.ExternalReference(target_url=s.url, available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(s.tc0, sf), otio.opentime.RationalTime(s.nframes, sf)))
            tr.append(otio.schema.Clip(name=s.name, media_reference=ref, source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(a + s.tc0, sf), otio.opentime.RationalTime(dur * sf / f, sf))))
        tl.tracks.append(tr)
    out = []
    otio.adapters.write_to_file(tl, base + ".otio")
    out.append(base + ".otio")
    try:
        otio.adapters.write_to_file(tl, base + "_fcp7.xml", adapter_name="fcp_xml")
        out.append(base + "_fcp7.xml")
    except Exception as e:  # adapter plugin missing
        vc.log(f"note: FCP7 XML skipped ({e})")
    return out


def _T(s):
    s = (s or "0s").rstrip("s")
    if "/" in s:
        n, d = s.split("/")
        return Fraction(int(n), int(d))
    return Fraction(s)


def verify_fcpxml(path, clips, srcs, fps):
    """Parse the FCPXML with exact fractions and compare it with the cut list. Returns a list of problems."""
    probs = []
    root = ET.parse(path).getroot()
    fmts = {f.get("id"): f for f in root.iter("format")}
    assets = {a.get("id"): a for a in root.iter("asset")}
    seq = next(root.iter("sequence"))
    sfd = _T(fmts[seq.get("format")].get("frameDuration"))
    if sfd != 1 / fps:
        probs.append(f"sequence frameDuration {sfd} != 1/{fps}")
    items = list(next(root.iter("spine")))
    if len(items) != len(clips):
        probs.append(f"{len(items)} clips in the spine, cut list has {len(clips)}")
    run = Fraction(0)
    for i, (c, (si, a, b, dur)) in enumerate(zip(items, clips)):
        s = srcs[si]
        off, st, du = _T(c.get("offset")), _T(c.get("start")), _T(c.get("duration"))
        asset = assets.get(c.get("ref"))
        if asset is None:
            probs.append(f"clip {i}: unknown asset {c.get('ref')}")
            continue
        afd = _T(fmts[asset.get("format")].get("frameDuration"))
        if off != run:
            probs.append(f"clip {i}: offset {off} != running total {run}")
        if (off / sfd).denominator != 1 or (du / sfd).denominator != 1:
            probs.append(f"clip {i}: offset/duration {off}/{du} not on the sequence grid {sfd}")
        if du != dur / fps:
            probs.append(f"clip {i}: duration {du} != {dur} timeline frames")
        if (st / afd).denominator != 1 or st / afd != a + s.tc0:
            probs.append(f"clip {i}: start {st} = {float(st / afd):.2f} source frames, cut list {a + s.tc0}")
        a_st = _T(asset.get("start"))
        if a_st != s.tc0 * s.fd:
            probs.append(f"asset {asset.get('name')}: start {a_st} != media start timecode ({s.tc0} frames)")
        if st < a_st or st + du > a_st + _T(asset.get("duration")) + afd:
            probs.append(f"clip {i}: [{float(st):.3f}, {float(st + du):.3f}] outside its media")
        run += du
    if _T(seq.get("duration")) != run:
        probs.append(f"sequence duration {seq.get('duration')} != sum of clips {run}")
    return probs


def verify_edl(path, clips, srcs, fps):
    probs = []
    txt = open(path, encoding="utf-8").read()
    nom = round(float(fps))
    ev = re.findall(r"^(\d{3})\s+(\S+)\s+AA/V\s+C\s+(\S+) (\S+) (\S+) (\S+)\n\* FROM CLIP NAME: (.*)$", txt, re.M)
    if len(ev) != len(clips):
        probs.append(f"{len(ev)} events, cut list has {len(clips)}")
    rec = 3600 * nom
    for (n, reel, si_, so, ri, ro, cname), (si, a, b, dur) in zip(ev, clips):
        s = srcs[si]
        for tc in (si_, so, ri, ro):
            if int(tc.split(":")[3]) >= nom:
                probs.append(f"event {n}: timecode {tc} has a frame field >= {nom}")
        want = (frames_tc(a + s.tc0, s.fps), frames_tc(a + s.tc0 + dur, s.fps), frames_tc(rec, fps),
                frames_tc(rec + dur, fps))
        if (si_, so, ri, ro) != want:
            probs.append(f"event {n}: {si_} {so} {ri} {ro} != {' '.join(want)}")
        if cname != s.name:
            probs.append(f"event {n}: clip name '{cname}' != media '{s.name}'")
        rec += dur
    return probs


def verify_otio(path, clips, srcs, fps):
    try:
        import opentimelineio as otio
    except ImportError:
        return None
    tl = otio.adapters.read_from_file(path)
    v = [c for c in tl.video_tracks()[0] if isinstance(c, otio.schema.Clip)]
    got = [(c.source_range.start_time.value, c.source_range.start_time.rate) for c in v]
    want = [(a + srcs[si].tc0, float(srcs[si].fps)) for si, a, b, d in clips]
    return [] if [(round(x), r) for x, r in got] == [(x, r) for x, r in want] else \
        [f"clip starts {got[:3]} != {want[:3]}"]


def position_hints(clips, srcs, tracks, fps, W, H):
    """Approximate Inspector > Position X per clip for a 1080x1920 timeline with 'Scale full frame with crop'
    (source scaled to the timeline height): the face-track centre of each clip, in timeline pixels."""
    rows = []
    for i, (si, a, b, dur) in enumerate(clips, 1):
        t = tracks.get(si)
        s = srcs[si].info
        if not t or t.get("axis") != "x" or not t.get("pos"):
            continue
        tf = float(vc.frac(t.get("path_fps", s["fps"])))
        k0 = int(a / float(srcs[si].fps) * tf)
        k1 = max(k0 + 1, int(b / float(srcs[si].fps) * tf))
        seg = sorted(t["pos"][k0:k1]) or t["pos"]
        cx = seg[len(seg) // 2] + t["crop_w"] / 2           # face centre, source px
        scale = H / s["h"]
        rows.append(f"    clipul {i:2d}: Position X ≈ {round((s['w'] / 2 - cx) * scale):+d}")
    if not rows:
        return ""
    return ("  Valori de pornire pentru Position X (aproximative, din urmărirea feței; Zoom 1.0):\n"
            + "\n".join(rows) + "\n")


def alpha_overlay(ass, W, H, fps, dur, out):
    tmp = tempfile.mkdtemp(prefix="ve_alpha_")
    vc.run(vc.ffmpeg_cmd("-f", "lavfi", "-i", f"color=c=black@0.0:s={W}x{H}:r={fps}:d={float(dur):.6f},format=yuva444p",
                         "-vf", f"subtitles=filename='{vc.filter_file(ass, tmp, 'captions.ass')}':alpha=1",
                         "-c:v", "prores_ks", "-profile:v", "4444", "-qscale:v", "9", "-pix_fmt", "yuva444p10le",
                         "-vendor", "apl0", out))
    shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cuts")
    ap.add_argument("-o", "--outdir", required=True)
    ap.add_argument("--mac-dir", default="/Users/Shared/Claude-Edit",
                    help="folder of the ORIGINAL clips on the user's Mac (default /Users/Shared/Claude-Edit)")
    ap.add_argument("--name", default="Montaj Claude", help="timeline name")
    ap.add_argument("--srt", help="SRT to include (edited timeline)")
    ap.add_argument("--stems", help="folder with voice.wav / music_ducked.wav to include")
    ap.add_argument("--alpha", help="captions .ass -> captions_alpha.mov (ProRes 4444 with alpha)")
    ap.add_argument("--format", default="reels", help="canvas for --alpha and Position X hints (reels/youtube/WxH)")
    ap.add_argument("--track", action="append", help="SRC=track.json (face track) -> Position X hints in CITESTE-MA")
    ap.add_argument("--final", help="name of the final MP4 the user receives (mentioned in CITESTE-MA)")
    ap.add_argument("--include-final", action="store_true", help="also copy --final into the package (bigger zip)")
    ap.add_argument("--zip", action="store_true", help="also zip the folder (one download for the user)")
    ap.add_argument("--no-mezzanine", action="store_true", help="don't make CFR copies of VFR sources")
    a = ap.parse_args()

    cuts = vc.load_json(a.cuts)
    os.makedirs(a.outdir, exist_ok=True)
    fps, srcs, clips = build(cuts, a.mac_dir, a.outdir, not a.no_mezzanine)
    if not clips:
        raise vc.EditError("no clips to export")
    base = os.path.join(a.outdir, "timeline")
    with open(base + ".fcpxml", "w", encoding="utf-8") as f:
        f.write(fcpxml(fps, srcs, clips, a.name))
    paths = {"timeline.fcpxml": base + ".fcpxml"}
    has_edl = edl_possible(fps, srcs, clips)
    if os.path.exists(base + ".edl"):
        os.unlink(base + ".edl")
    if has_edl:
        with open(base + ".edl", "w", encoding="utf-8") as f:
            f.write(edl(fps, srcs, clips, a.name))
        paths["timeline.edl"] = base + ".edl"
    else:
        rates = sorted({str(srcs[si].fps) for si, *_ in clips})
        print(f"  EDL skipped: sources at {', '.join(rates)} fps in a {fps} fps timeline (CMX3600 has one rate)")
    extra = otio_files(fps, srcs, clips, a.name, base)
    if a.srt:
        shutil.copy(a.srt, os.path.join(a.outdir, "subtitles.srt"))
    if a.stems and os.path.isdir(a.stems):
        shutil.copytree(a.stems, os.path.join(a.outdir, "stems"), dirs_exist_ok=True)
    final_name = os.path.basename(a.final) if a.final else "video-ul final"
    if a.final and a.include_final:
        shutil.copy(a.final, os.path.join(a.outdir, final_name))
    tl_frames = sum(d for *_, d in clips)
    W, H, _ = vc.canvas_for(a.format)
    if a.alpha:
        alpha_overlay(a.alpha, W, H, fps, Fraction(tl_frames) / fps, os.path.join(a.outdir, "captions_alpha.mov"))
    tracks = {}
    for t in a.track or []:
        k, p = t.split("=", 1) if "=" in t else ("0", t)
        tracks[int(k)] = vc.load_json(p)
    s0 = srcs[0].info
    mezz = any(s.name.endswith("_CFR.mp4") for s in srcs)
    fallback = ("File → Import → Timeline… → timeline.edl (clipurile trebuie să fie deja în Media Pool) sau timeline.otio."
                if has_edl else "File → Import → Timeline… → timeline.otio. (Nu există EDL: clipurile au frame rate-uri "
                "diferite de timeline, iar formatul EDL nu poate descrie asta.)")
    with open(os.path.join(a.outdir, "CITESTE-MA_DaVinci.txt"), "w", encoding="utf-8") as f:
        f.write(README.format(
            names=", ".join(s.name for s in srcs), mac_dir=a.mac_dir, src_res=f"{s0['w']}x{s0['h']}",
            fps=round(float(fps), 3), final_name=final_name, fallback=fallback,
            edl_line=("timeline.edl         variantă de rezervă (CMX3600)" if has_edl else
                      "(fără timeline.edl: clipurile au frame rate-uri diferite, EDL nu le poate descrie)"),
            media_note=(" (și copiile din folderul media/ al pachetului)" if mezz else ""),
            positions=(position_hints(clips, srcs, tracks, fps, W, H) if H > W else "")))
    probs = {}
    probs["timeline.fcpxml"] = verify_fcpxml(base + ".fcpxml", clips, srcs, fps)
    if has_edl:
        probs["timeline.edl"] = verify_edl(base + ".edl", clips, srcs, fps)
    if base + ".otio" in extra:
        r = verify_otio(base + ".otio", clips, srcs, fps)
        if r is not None:
            probs["timeline.otio"] = r
    for s in srcs:   # the asset start must be the media's own start timecode
        real = tc_frames(vc.media_info(s.info["path"]).get("timecode"), s.fps)
        if real != s.tc0:
            probs.setdefault("timeline.fcpxml", []).append(f"{s.name}: asset start {s.tc0} frames but the media "
                                                           f"starts at timecode frame {real}")
    print(f"{len(clips)} clips, timeline {tl_frames} frames ({tl_frames / float(fps):.2f}s) @ {fps} fps; "
          f"media expected in {a.mac_dir}")
    for k, v in probs.items():
        print(f"  check {k}: " + ("OK (parsed back: sequence rate, every clip offset/start/duration exact)"
                                  if not v and k == "timeline.fcpxml" else "OK" if not v else
                                  "MISMATCH: " + "; ".join(v[:4])))
    if a.zip:
        z = shutil.make_archive(a.outdir.rstrip("/"), "zip", a.outdir)
        print(f"zip: {z} ({os.path.getsize(z) / 1e6:.1f} MB)")
    print(f"wrote {a.outdir}")
    bad = {k: v for k, v in probs.items() if v}
    if bad:
        print(f"ERROR: timeline check failed for {', '.join(bad)} - do not ship this package; "
              f"fix export_resolve.py or deliver without --resolve")
        sys.exit(4)


if __name__ == "__main__":
    main()
