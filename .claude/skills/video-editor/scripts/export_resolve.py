#!/usr/bin/env python3
"""Export the edit (cuts.json) as a DaVinci Resolve (free) package for manual finishing on the user's Mac.

Writes into OUTDIR:
  timeline.fcpxml   FCPXML 1.10 (File > Import > Timeline). Clips point at the ORIGINAL file names under
                    --mac-dir (default /Users/Shared/Claude-Edit, exists on every Mac) -> no relinking needed if
                    the user copies the originals there; otherwise Relink / import-into-Media-Pool-first works.
  timeline.edl      CMX3600 fallback (one AA/V event per cut + "* FROM CLIP NAME").
  timeline.otio     OpenTimelineIO (Resolve 18.5+ imports it), and timeline_fcp7.xml, if opentimelineio is installed.
  subtitles.srt     (--srt) edited-timeline subtitles;  captions_alpha.mov (--alpha) ProRes 4444 overlay of the
                    burned captions with transparency;  stems (--stems) voice/music WAVs; CITESTE-MA_DaVinci.txt.
Cut points are frame-exact. Variable-frame-rate phone clips get a CFR copy in media/ (same conversion as the
render) and the timeline points to it, so Resolve matches the MP4 frame-for-frame.
Verified by reading the files back with OpenTimelineIO (clip in/out frames = cut list); Resolve itself is not
available in the cloud container.

Examples:
  export_resolve.py work/cuts.json -o out/davinci --srt out/final.srt --stems work/stems
  export_resolve.py work/cuts.json -o out/davinci --alpha work/captions.ass --format reels --zip
  export_resolve.py work/cuts.json -o out/davinci --mac-dir "/Users/ana/Movies/Reel 12" --name "Reel 12"
"""
import argparse
import os
import shutil
import urllib.parse
from fractions import Fraction
from xml.sax.saxutils import quoteattr

import vcommon as vc

README = """CUM DESCHIZI MONTAJUL ÎN DAVINCI RESOLVE (varianta gratuită)
=============================================================

Ce e în folder:
  timeline.fcpxml      montajul (tăieturile) – se importă în Resolve
  timeline.edl / .otio variante de rezervă, dacă FCPXML nu merge
  subtitles.srt        subtitrările pe timeline-ul editat
  captions_alpha.mov   subtitrările animate, cu fundal transparent (dacă există)
  stems/               vocea masterizată (voice.wav) și muzica cu ducking (music_ducked.wav), 48 kHz
  {final_name}         video-ul final, ca referință
  media/               (dacă există) copii CFR ale clipurilor cu frame rate variabil – pune-le lângă originale

PASUL 1 – clipurile originale
  Montajul folosește fișierele tale ORIGINALE: {names}
  Cel mai simplu: în Finder apasă Cmd+Shift+G, scrie {mac_dir} și pune acolo clipurile originale,
  cu exact aceleași nume. (Dacă folderul nu există, creează-l.)

PASUL 2 – importul
  DaVinci Resolve → File → Import → Timeline… → alege timeline.fcpxml.
  În fereastra de import lasă bifat „Automatically import source clips into media pool”.
  Dacă clipurile apar roșii (offline): selectează-le în Media Pool → click dreapta →
  „Relink Selected Clips…” → alege folderul unde ai clipurile.
  Alternativă: importă întâi clipurile în Media Pool, apoi importă timeline-ul cu bifa de mai sus DEBIFATĂ
  (Resolve le potrivește după nume și timecode).
  Dacă FCPXML dă eroare: File → Import → Timeline… → timeline.edl (clipurile trebuie să fie deja în Media Pool)
  sau timeline.otio.

PASUL 3 – format vertical (Reels/TikTok/Shorts)
  Timeline-ul vine la rezoluția clipului original ({src_res}). Pentru 9:16:
  click dreapta pe timeline în Media Pool → Timelines → Timeline Settings… → debifează „Use Project Settings” →
  rezoluție 1080 x 1920 → la „Mismatched resolution files” alege „Scale full frame with crop”.
  Apoi, pe fiecare clip: Inspector → Transform → Position X ca să încadrezi fața
  (Smart Reframe există doar în Resolve Studio; în video-ul final eu am făcut deja încadrarea automată).

PASUL 4 – subtitrări și sunet
  Subtitrări editabile: File → Import → Subtitle… → subtitles.srt, apoi trage-le pe timeline
  (sau trage fișierul .srt direct în Media Pool).
  Subtitrări animate ca în video-ul final: pune captions_alpha.mov pe pista V2, la începutul timeline-ului
  (merge doar dacă timeline-ul e 1080x1920 și nu schimbi tăieturile).
  Sunet masterizat: pune stems/voice.wav pe A2 și stems/music_ducked.wav pe A3, de la început,
  și dă mute la A1 (sunetul original).

PASUL 5 – export
  Pagina Deliver → Custom Export: MP4, H.264, 1080x1920 (sau 1920x1080), {fps} fps,
  „Restrict to” 12000 Kb/s, audio AAC 320 kb/s. Pentru YouTube 16:9 poți urca subtitles.srt separat ca subtitrare.
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
    """VFR phone clips get a CFR mezzanine (media/<name>_CFR.mp4) made with the SAME fps conversion as the render,
    so the Resolve timeline matches the MP4 frame-for-frame (NLEs play VFR clips with drift)."""
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
            if not os.path.exists(dst):
                normalize(info["path"], dst)
            m = vc.media_info(dst)
            m["timecode"] = None
            srcs.append(Src(m, mac_dir, name))
            print(f"  VFR source {info['name']} -> CFR mezzanine media/{name} (timeline points to it)")
        else:
            srcs.append(Src(info, mac_dir))
    clips = []
    for g in segs:
        s = srcs[g["src"]]
        a, b = s.frame(g["S"]), s.frame(g["E"])
        if b > a:
            clips.append((g["src"], a, b))
    return fps, srcs, clips


def t_str(frames, fd):
    return "0s" if frames == 0 else f"{frames * fd.numerator}/{fd.denominator}s"


def fcpxml(fps, srcs, clips, name):
    fd = Fraction(1) / fps
    fmts, res = {}, []
    for s in srcs:
        key = (s.info["w"], s.info["h"], s.fps)
        if key not in fmts:
            fid = f"r{len(fmts) + 1}"
            fmts[key] = fid
            sfd = s.fd
            res.append(f'    <format id="{fid}" name="FFVideoFormat{s.info["h"]}p{round(float(s.fps))}" '
                       f'frameDuration="{sfd.numerator}/{sfd.denominator}s" width="{s.info["w"]}" height="{s.info["h"]}" '
                       f'colorSpace="1-1-1 (Rec. 709)"/>')
    nf = len(fmts)
    for i, s in enumerate(srcs):
        aid = f"r{nf + i + 1}"
        s.aid, s.fid = aid, fmts[(s.info["w"], s.info["h"], s.fps)]
        base = os.path.splitext(s.name)[0]
        res.append(f'    <asset id="{aid}" name={quoteattr(base)} start="{t_str(s.tc0, s.fd)}" '
                   f'duration="{t_str(s.nframes, s.fd)}" hasVideo="1" format="{s.fid}" '
                   f'hasAudio="{1 if s.info.get("has_audio") else 0}" audioSources="1" '
                   f'audioChannels="{s.info.get("channels") or 2}" audioRate="{s.info.get("sample_rate") or 48000}">\n'
                   f'      <media-rep kind="original-media" src={quoteattr(s.url)}/>\n    </asset>')
    seq_fmt = srcs[clips[0][0]].fid if clips else "r1"
    spine, off = [], 0
    for si, a, b in clips:
        s = srcs[si]
        dur_tl = int(round((b - a) * s.fd * fps))  # timeline frames
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
    r = "".join(c for c in os.path.splitext(name)[0].upper() if c.isalnum())[:8]
    return r or "AX"


def edl(fps, srcs, clips, name):
    lines = [f"TITLE: {name}", "FCM: NON-DROP FRAME", ""]
    rec = 3600 * round(float(fps))  # record TC starts 01:00:00:00 (Resolve default)
    for i, (si, a, b) in enumerate(clips, 1):
        s = srcs[si]
        dur = int(round((b - a) * s.fd * fps))
        lines.append(f"{i:03d}  {reel_name(s.name):<8} AA/V  C        {frames_tc(a + s.tc0, s.fps)} "
                     f"{frames_tc(b + s.tc0, s.fps)} {frames_tc(rec, fps)} {frames_tc(rec + dur, fps)}")
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
        for si, a, b in clips:
            s = srcs[si]
            sf = float(s.fps)
            ref = otio.schema.ExternalReference(target_url=s.url, available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(s.tc0, sf), otio.opentime.RationalTime(s.nframes, sf)))
            tr.append(otio.schema.Clip(name=s.name, media_reference=ref, source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(a + s.tc0, sf), otio.opentime.RationalTime(b - a, sf))))
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


def verify(paths, clips, srcs, fps):
    """Read timelines back with OTIO and compare clip in/out frames with the cut list."""
    try:
        import opentimelineio as otio
    except ImportError:
        return {}
    res = {}
    for p in paths:
        try:
            kw = {"rate": float(fps)} if p.endswith(".edl") else {}
            tl = otio.adapters.read_from_file(p, **kw)
            if not isinstance(tl, otio.schema.Timeline):  # fcpxml adapter returns a collection
                tl = next(iter(tl.find_children(descended_from_type=otio.schema.Timeline) if hasattr(tl, "find_children")
                               else [x for x in tl if isinstance(x, otio.schema.Timeline)]))
            v = [c for c in tl.video_tracks()[0] if isinstance(c, otio.schema.Clip)]
            got = [(round(c.source_range.start_time.value), round(c.source_range.duration.value)) for c in v]
            want = [(a + srcs[si].tc0, b - a) for si, a, b in clips]
            res[os.path.basename(p)] = f"OK ({len(got)} clips match)" if got == want else \
                f"MISMATCH {got[:3]} vs {want[:3]}"
        except Exception as e:
            res[os.path.basename(p)] = f"not verifiable with OTIO ({str(e)[:70]})"
    return res


def alpha_overlay(ass, W, H, fps, dur, out):
    vc.run(vc.ffmpeg_cmd("-f", "lavfi", "-i", f"color=c=black@0.0:s={W}x{H}:r={fps}:d={float(dur):.6f},format=yuva444p",
                         "-vf", f"subtitles=filename='{vc.ass_filter_path(ass)}':alpha=1", "-c:v", "prores_ks",
                         "-profile:v", "4444", "-qscale:v", "9", "-pix_fmt", "yuva444p10le", "-vendor", "apl0", out))


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
    ap.add_argument("--format", default="reels", help="canvas for --alpha (reels/youtube/WxH)")
    ap.add_argument("--final", help="final MP4 to copy into the package as reference")
    ap.add_argument("--zip", action="store_true", help="also zip the folder (one download for the user)")
    ap.add_argument("--no-mezzanine", action="store_true", help="don't make CFR copies of VFR sources")
    a = ap.parse_args()

    cuts = vc.load_json(a.cuts)
    os.makedirs(a.outdir, exist_ok=True)
    fps, srcs, clips = build(cuts, a.mac_dir, a.outdir, not a.no_mezzanine)
    if not clips:
        raise vc.EditError("no clips to export")
    os.makedirs(a.outdir, exist_ok=True)
    base = os.path.join(a.outdir, "timeline")
    with open(base + ".fcpxml", "w", encoding="utf-8") as f:
        f.write(fcpxml(fps, srcs, clips, a.name))
    with open(base + ".edl", "w", encoding="ascii", errors="replace") as f:
        f.write(edl(fps, srcs, clips, a.name))
    extra = otio_files(fps, srcs, clips, a.name, base)
    if a.srt:
        shutil.copy(a.srt, os.path.join(a.outdir, "subtitles.srt"))
    if a.stems and os.path.isdir(a.stems):
        shutil.copytree(a.stems, os.path.join(a.outdir, "stems"), dirs_exist_ok=True)
    final_name = "(video final)"
    if a.final:
        final_name = os.path.basename(a.final)
        shutil.copy(a.final, os.path.join(a.outdir, final_name))
    tl_frames = sum(int(round((b - a_) * srcs[si].fd * fps)) for si, a_, b in clips)
    if a.alpha:
        W, H, _ = vc.canvas_for(a.format)
        alpha_overlay(a.alpha, W, H, fps, Fraction(tl_frames) / fps, os.path.join(a.outdir, "captions_alpha.mov"))
    s0 = srcs[0].info
    with open(os.path.join(a.outdir, "CITESTE-MA_DaVinci.txt"), "w", encoding="utf-8") as f:
        f.write(README.format(names=", ".join(s.name for s in srcs), mac_dir=a.mac_dir,
                              src_res=f"{s0['w']}x{s0['h']}", fps=round(float(fps), 3), final_name=final_name))
    checks = verify([base + ".fcpxml", base + ".edl"] + extra, clips, srcs, fps)
    print(f"{len(clips)} clips, timeline {tl_frames} frames ({tl_frames / float(fps):.2f}s) @ {fps} fps; "
          f"media expected in {a.mac_dir}")
    for k, v in checks.items():
        print(f"  read-back {k}: {v}")
    if a.zip:
        z = shutil.make_archive(a.outdir.rstrip("/"), "zip", a.outdir)
        print(f"zip: {z}")
    print(f"wrote {a.outdir}")


if __name__ == "__main__":
    main()
