#!/usr/bin/env python3
"""Probe media files and flag phone-footage problems before editing.

Prints, per file: duration, display resolution (after rotation), fps (nominal / average, VFR flag),
codec, bit depth, HDR (HLG/PQ/Dolby Vision), colour range, rotation, audio format, timecode, and a list
of ISSUES with what the pipeline will do about them. Optionally measures loudness (EBU R128).

Examples:
  probe.py clip1.mov clip2.mp4
  probe.py --find                       # list recently uploaded media files in the usual places
  probe.py --find /home/user/uploads --json media.json
  probe.py clip.mov --loudness --json info.json
"""
import argparse
import glob
import os
import time

import vcommon as vc

MEDIA_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".mts", ".m2ts", ".3gp", ".hevc",
             ".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".jpg", ".jpeg", ".png", ".heic", ".webp"}
SEARCH_DIRS = ["/home/user", os.path.expanduser("~"), "/tmp", "/mnt", "/workspace", "/data", "/uploads",
               "/mnt/user-data", "/mnt/data"]
SKIP = ("/.cache/", "/node_modules/", "/.git/", "/site-packages/", "/proc/", "/.claude/skills/", "/__pycache__/")


def find_media(dirs, max_age_h=48.0):
    seen, out = set(), []
    now = time.time()
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for root, subdirs, files in os.walk(d):
            if any(s in root + "/" for s in SKIP) or root.count(os.sep) - d.count(os.sep) > 6:
                subdirs[:] = []
                continue
            for f in files:
                p = os.path.join(root, f)
                if os.path.splitext(f)[1].lower() in MEDIA_EXT and p not in seen:
                    try:
                        st = os.stat(p)
                    except OSError:
                        continue
                    if st.st_size > 10_000 and now - st.st_mtime < max_age_h * 3600:
                        seen.add(p)
                        out.append((st.st_mtime, p, st.st_size))
    return [(p, s) for _, p, s in sorted(out)]


def issues_for(i):
    """Human-readable problems + what the scripts do about them."""
    iss = []
    if i.get("has_video"):
        if i.get("hdr"):
            iss.append(f"HDR {i['hdr'].upper()}{' + Dolby Vision' if i.get('dolby_vision') else ''}: will tone-map to "
                       "SDR BT.709 (zscale npl=203 + mobius). Tell the user: next time film with HDR Video OFF.")
        if i.get("vfr"):
            iss.append(f"variable frame rate (r={i['r_frame_rate']} avg={i['avg_frame_rate']}): render converts to "
                       f"CFR {i['fps']}; Resolve timeline cuts may drift slightly on long clips.")
        if i.get("rotation"):
            iss.append(f"rotation metadata {i['rotation']} deg: ffmpeg auto-rotates (display {i['w']}x{i['h']}).")
        if i.get("full_range"):
            iss.append("full-range (pc/yuvj) video: converted to TV range BT.709 on export.")
        if i.get("bit_depth", 8) > 8 and not i.get("hdr"):
            iss.append(f"{i['bit_depth']}-bit SDR source: output is 8-bit yuv420p (fine for social).")
        if i.get("vcodec") in ("hevc", "prores", "dnxhd", "vp9", "av1"):
            iss.append(f"{i['vcodec']} source: decoding is slower on CPU; output is H.264.")
        if max(i.get("w", 0), i.get("h", 0)) >= 3840:
            iss.append("4K source: 2x crop headroom for punch-ins / reframing without upscaling.")
        if i.get("color_space") in ("bt470bg", "smpte170m") and max(i.get("w", 0), i.get("h", 0)) >= 1280:
            iss.append("HD tagged BT.601: will be converted to BT.709 matrix on export.")
        if not i.get("has_audio"):
            iss.append("NO AUDIO stream: cannot transcribe/cut by speech; silence will be used.")
    if i.get("has_audio"):
        if i.get("sample_rate") and i["sample_rate"] != 48000:
            iss.append(f"audio {i['sample_rate']} Hz: resampled to 48 kHz.")
        if i.get("channels") == 1:
            iss.append("mono audio: upmixed to dual-mono stereo.")
        if i.get("audio_streams", 1) > 1:
            iss.append(f"{i['audio_streams']} audio streams: only the first is used (check which mic it is).")
        if i.get("has_video") and abs(i.get("a_start", 0) - i.get("v_start", 0)) > 0.02:
            iss.append(f"audio starts {i['a_start'] - i['v_start']:+.3f}s vs video: handled (aresample first_pts=0).")
    return iss


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="media files to probe")
    ap.add_argument("--find", nargs="*", metavar="DIR", help="search DIRs (default: usual upload places) for media")
    ap.add_argument("--max-age", type=float, default=72, help="--find: only files modified in the last N hours (72)")
    ap.add_argument("--loudness", action="store_true", help="also measure integrated loudness / true peak")
    ap.add_argument("--json", help="write all results to this JSON file")
    a = ap.parse_args()

    files = list(a.files)
    if a.find is not None:
        found = find_media(a.find or SEARCH_DIRS, a.max_age)
        print(f"# {len(found)} media file(s) found:")
        for p, s in found:
            print(f"  {s / 1e6:9.1f} MB  {p}")
        files += [p for p, _ in found if os.path.splitext(p)[1].lower() not in (".jpg", ".jpeg", ".png", ".webp", ".heic")]
    if not files:
        if a.find is None:
            ap.error("give files or --find")
        return
    expanded = []
    for f in files:
        expanded += sorted(glob.glob(f)) or [f]
    results = []
    for f in expanded:
        try:
            i = vc.media_info(f)
        except SystemExit as e:
            print(f"\n## {f}\n  {e}")
            continue
        if a.loudness and i.get("has_audio"):
            i["loudness"] = vc.ebur128(f)
        i["issues"] = issues_for(i)
        results.append(i)
        print(f"\n## {i['name']}  ({i['size_mb']} MB, {i['duration']:.2f}s, {i['container']})")
        if i["has_video"]:
            print(f"  video : {i['vcodec']} {i.get('profile') or ''} {i['w']}x{i['h']} (stored {i['stored_w']}x{i['stored_h']}, "
                  f"rot {i['rotation']}) fps {i['fps']} [{i['fps_float']}] avg {i['avg_frame_rate']} "
                  f"{'VFR' if i['vfr'] else 'CFR'} {i['pix_fmt']} {i['bit_depth']}bit "
                  f"trc={i['color_transfer']} prim={i['color_primaries']} range={i['color_range']} "
                  f"{i['v_bitrate_mbps']} Mbps")
            ar = i["w"] / i["h"] if i["h"] else 0
            print(f"  aspect: {ar:.3f} ({'vertical' if ar < 0.9 else 'square' if ar < 1.1 else 'landscape'})")
        if i["has_audio"]:
            print(f"  audio : {i['acodec']} {i['sample_rate']} Hz {i['channels']} ch")
        if i.get("loudness"):
            L = i["loudness"]
            print(f"  loud  : {L['I']} LUFS, LRA {L['LRA']} LU, true peak {L['TP']} dBTP")
        if i.get("timecode"):
            print(f"  tc    : {i['timecode']}")
        for s in i["issues"]:
            print(f"  ! {s}")
    if a.json:
        vc.save_json(results, a.json)
        print(f"\nwrote {a.json}")


if __name__ == "__main__":
    main()
