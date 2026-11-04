#!/usr/bin/env python3
"""Make an edit-friendly mezzanine from a phone clip: CFR, upright, SDR BT.709 TV-range 8-bit, 48 kHz stereo.

Needed rarely (render_cuts.py normalizes on the fly). Use it to give DaVinci Resolve a clip that matches the
cloud edit frame-for-frame (variable-frame-rate phone clips drift in NLEs), or to tame odd sources before
analysis. Fixes: rotation (auto-applied), HDR HLG/PQ -> SDR (zscale npl=203 + mobius, mean error 9.2 vs 41 for
naive), VFR -> CFR (fps filter + aresample async; video starting after the audio is padded with its first
frame), full range / BT.601 -> BT.709 TV range, any audio -> 48 kHz. The source timecode is kept only when the
frame rate is unchanged.

Examples:
  normalize.py IMG_1234.MOV work/IMG_1234_CFR.mp4
  normalize.py clip.mov out.mov --fps 25 --prores        # ProRes 422 HQ + PCM for heavy grading
"""
import argparse

import vcommon as vc
from render_cuts import colour_norm


def normalize(src, out, fps=None, prores=False, crf=16, keep_tc=True):
    """keep_tc=False: no timecode track (export_resolve: a CFR copy at the timeline rate can't carry the source's
    timecode, and the FCPXML asset start must equal the file's own timecode)."""
    info = vc.media_info(src)
    if not info.get("has_video"):
        raise vc.EditError(f"{src} has no video")
    fps = vc.frac(fps) if fps else vc.frac(info["fps"])
    vf = f"fps={fps}:start_time=0,{colour_norm(info, info['h'])},setsar=1"
    if prores:
        vf = vf.replace("format=yuv420p", "format=yuv422p10le")
        venc = ["-c:v", "prores_ks", "-profile:v", "3", "-vendor", "apl0", "-pix_fmt", "yuv422p10le"]
        aenc = ["-c:a", "pcm_s24le"]
    else:
        g = int(round(float(fps)))
        venc = ["-c:v", "libx264", "-preset", "fast", "-crf", str(crf), "-g", str(g), "-bf", "2", "-pix_fmt", "yuv420p"]
        aenc = ["-c:a", "aac", "-b:a", "320k"]
    cmd = vc.ffmpeg_cmd("-i", src, "-map", "0:v:0", "-vf", vf, *venc, "-r", str(fps), "-fps_mode", "cfr",
                        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv")
    if info.get("has_audio"):
        cmd += ["-map", "0:a:0", "-af", "aresample=48000:async=1:first_pts=0,aformat=channel_layouts=stereo",
                "-ar", "48000", *aenc]
    if info.get("timecode") and keep_tc and vc.frac(info["fps"]) == fps:
        cmd += ["-timecode", info["timecode"].replace(";", ":")]
    else:
        cmd += ["-map_metadata", "-1", "-write_tmcd", "0"]
    cmd += ["-movflags", "+faststart", out]
    vc.run(cmd)
    return info, vc.media_info(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--fps", help="output frame rate (default: nominal source rate)")
    ap.add_argument("--prores", action="store_true", help="ProRes 422 HQ 10-bit + PCM (use a .mov output)")
    ap.add_argument("--crf", type=int, default=16)
    a = ap.parse_args()
    i, o = normalize(a.src, a.out, a.fps, a.prores, a.crf)
    print(f"in : {i['w']}x{i['h']} rot={i.get('rotation')} fps r={i.get('r_frame_rate')} avg={i.get('avg_frame_rate')} "
          f"vfr={i.get('vfr')} hdr={i.get('hdr')} pix={i.get('pix_fmt')} audio={i.get('sample_rate')}Hz/{i.get('channels')}ch")
    print(f"out: {o['w']}x{o['h']} rot={o.get('rotation')} fps r={o.get('r_frame_rate')} avg={o.get('avg_frame_rate')} "
          f"vfr={o.get('vfr')} hdr={o.get('hdr')} pix={o.get('pix_fmt')} trc={o.get('color_transfer')} "
          f"audio={o.get('sample_rate')}Hz/{o.get('channels')}ch -> {a.out}")


if __name__ == "__main__":
    main()
