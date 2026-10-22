#!/usr/bin/env python3
"""End-to-end self-test of the video-editor skill (about 3 min on 4 CPUs).

Generates Romanian test footage (Piper TTS + a public-domain portrait), runs pipeline.py
(16:9 talking head + a VFR, rotated phone clip -> 9:16 Reels with hook, music and a DaVinci package),
then asserts: no QC FAIL, duration = cut list, loudness -14 +-1 LUFS, the timeline read-back is OK,
the caption layout check passed (safe zone, no overlaps, nothing under the hook) and the cover exists.
Usage: selftest.py WORKDIR [--skip-media]
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workdir")
    ap.add_argument("--skip-media", action="store_true", help="reuse WORKDIR/media")
    a = ap.parse_args()
    w = os.path.abspath(a.workdir)
    media = os.path.join(w, "media")
    if not a.skip_media:
        subprocess.run([sys.executable, os.path.join(HERE, "make_test_media.py"), media], check=True)
    out = os.path.join(w, "out")
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, "pipeline.py"), os.path.join(media, "talk_16x9.mp4"),
                        os.path.join(media, "phone_vfr_rot.mp4"), "-o", out, "--hook", "Cum editezi un reel în 5 minute",
                        "--music", os.path.join(media, "music.wav"), "--resolve"], capture_output=True, text=True)
    log = p.stdout + p.stderr
    open(os.path.join(w, "pipeline.log"), "w").write(log)
    ok = True
    def check(cond, msg):
        nonlocal ok
        ok &= bool(cond)
        print(("PASS " if cond else "FAIL ") + msg)
    check(p.returncode == 0, "pipeline exit code 0")
    if p.returncode == 0:
        qc = json.load(open(os.path.join(out, "qc", "qc.json")))
        check(qc["fail"] == 0, f"QC: {qc['fail']} FAIL, {qc['warn']} WARN")
        check("OK" in log and "MISMATCH" not in log, "timeline read-back OK")
        cap = log.split("=== 5 captions")[-1].split("=== 6a")[0]
        check("WARNING" not in cap and "layout check: OK" in cap, "captions: safe zone, no overlaps, none under the hook")
        check(os.path.exists(os.path.join(out, "cover_9x16.jpg")), "cover_9x16.jpg written")
        s = json.load(open(os.path.join(out, "summary.json")))
        check(15 < s["duration"] < 45, f"output duration {s['duration']}s (fillers/retake/pauses cut)")
        loud = [r for r in qc["results"] if r[1].startswith("loudness ")][0]
        check(loud[0] == "PASS", loud[1])
        print(f"total {s['total_seconds']}s; look at {s['qc_sheets']}")
    print("SELFTEST", "OK" if ok else "FAILED", "- log:", os.path.join(w, "pipeline.log"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
