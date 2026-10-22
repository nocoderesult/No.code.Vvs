#!/usr/bin/env python3
"""One-command edit: raw clip(s) -> finished video (+ SRT, cover, QC sheets, optional DaVinci Resolve package).

Steps (each prints the exact command so any step can be re-run by hand after editing its JSON):
  1 probe          phone-footage issues (HDR, VFR, rotation, mono, ...)
  2 transcribe     faster-whisper large-v3-turbo, Romanian, word timestamps   -> work/words.json (cached)
  3 plan cuts      silences + fillers + retakes, phrase list, zoom-cut points    -> work/cuts.json, work/phrases.txt
  4 reframe        face tracking when the aspect changes                         -> work/track_N.json (cached)
  5 captions       word-by-word ASS on the edited timeline (+ hook, CTA), SRT    -> work/captions.ass, OUT/NAME.srt
  6 audio          cut audio -> voice chain + loudness (+ ducked music, sfx)     -> work/mix.wav, work/stems/
  7 render         single encode, frame-exact cuts, zoom cuts, captions          -> OUT/NAME.mp4
  8 QC             checks + contact sheets to LOOK at                            -> OUT/qc/
  9 cover          best face frame + title                                       -> OUT/cover_9x16.jpg | thumb_16x9.jpg
 10 DaVinci        FCPXML/EDL/OTIO + SRT + stems + instructions (--resolve)      -> OUT/davinci/ (+ .zip)
At the end it prints every WARN collected on the way (unused clips, SUSPECT phrases, upscaling, QC) and the
QC result; deliver only at QC 0 FAIL.

Examples:
  pipeline.py clip.mov -o out/reel1                                   # Reels/TikTok/Shorts defaults
  pipeline.py clip.mov -o out/reel1 --hook "3 GREȘELI LA MONTAJ" --cta "SALVEAZĂ-L" --music track.mp3 --resolve
  pipeline.py a.mov b.mov -o out/r --select P9,P1-P6 --captions box   # story order chosen from phrases.txt
  pipeline.py vlog.mp4 -o out/yt --format youtube --pace relaxed      # 16:9, SRT for YouTube CC, no burn-in
  pipeline.py vlog.mp4 -o out/yt --format youtube --words out/reel1/work/words.json --pace tight  # 'ambele'
  pipeline.py clip.mov -o out/r --cut none --captions pop             # keep everything, just reframe+captions
"""
import argparse
import os
import shlex
import shutil
import subprocess
import sys
import time

import vcommon as vc

HERE = os.path.dirname(os.path.abspath(__file__))
WARNS = []


def step(title, cmd, log, ok_codes=(0,)):
    print(f"\n=== {title}\n$ {' '.join(shlex.quote(str(c)) for c in cmd)}", flush=True)
    t = time.time()
    p = subprocess.run([str(c) for c in cmd], text=True, capture_output=True)
    out = (p.stdout or "") + ("\n" + p.stderr if p.returncode else "")
    lines = [l for l in out.splitlines() if "Warning" not in l]
    print("\n".join(lines[-40:]))
    for l in (p.stdout or "").splitlines():
        if l.startswith(("WARN", "WARNING", "FAIL")) and title not in ("8 QC", "3 plan cuts"):
            WARNS.append(f"[{title}] {l}")
    log.append({"step": title, "cmd": cmd, "seconds": round(time.time() - t, 1), "rc": p.returncode})
    if p.returncode not in ok_codes:
        raise vc.EditError(f"step '{title}' failed (see output above)")
    return p.stdout


def py(script):
    return [sys.executable, os.path.join(HERE, script)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="raw clips in story order")
    ap.add_argument("-o", "--outdir", required=True)
    ap.add_argument("--name", default="final", help="output file base name (final)")
    ap.add_argument("--format", default="reels", help="reels/tiktok/shorts/vertical/youtube/square/portrait/WxH/source")
    ap.add_argument("--captions", default="auto", choices=["auto", "karaoke", "box", "pop", "clean", "none"],
                    help="auto = karaoke for vertical/square, none for 16:9 (SRT is always written)")
    ap.add_argument("--hook", help="hook title on screen for the first seconds (3-7 words)")
    ap.add_argument("--hook-dur", type=float, default=3.0)
    ap.add_argument("--cta", help="on-screen call to action / end card for the last --cta-dur s ('SALVEAZĂ-L')")
    ap.add_argument("--cta-dur", type=float, default=3.0)
    ap.add_argument("--accent", default="#FFD400", help="caption highlight colour")
    ap.add_argument("--replace", action="append", help="caption word fix wrong=right (repeatable)")
    ap.add_argument("--words", help="use this words.json (e.g. from the 9:16 run when making the 16:9 one too); "
                    "copied into work/, sources must be the same files")
    ap.add_argument("--cut", default="auto", choices=["auto", "silence", "none"],
                    help="auto = transcript-based (silences+fillers+retakes); silence = energy only; none = keep all")
    ap.add_argument("--pace", choices=["tight", "normal", "relaxed"], help="default tight (vertical) / normal (16:9)")
    for k in ("select", "drop", "restore", "cold-open", "keep-words"):
        ap.add_argument(f"--{k}", help=f"passed to plan_cuts.py --{k}")
    ap.add_argument("--cut-range", action="append", help="plan_cuts --cut SRC:S-E (repeatable)")
    ap.add_argument("--add-range", action="append", help="plan_cuts --add SRC:S-E force-keep (repeatable)")
    ap.add_argument("--reframe", default="auto", choices=["auto", "track", "wide", "center", "blur", "fit", "none"])
    ap.add_argument("--punch", type=float, help="punch-in zoom every 2nd shot (default 1.12 vertical, 1.08 16:9; 1=off)")
    ap.add_argument("--zoom-cuts", default="auto", choices=["auto", "on", "off"],
                    help="alternate framing inside long takes (auto = on for vertical)")
    ap.add_argument("--push", type=float, default=0, help="slow push-in on long shots, e.g. 1.06")
    ap.add_argument("--grade", default="natural", choices=["none", "natural", "punchy", "bright"])
    ap.add_argument("--broll", help="broll.json for render_cuts.py")
    ap.add_argument("--stabilize", action="store_true")
    ap.add_argument("--vdenoise", action="store_true")
    ap.add_argument("--music", help="music bed (instrumental)")
    ap.add_argument("--music-under", type=float, default=15.0, help="bed this many dB under the voice while talking")
    ap.add_argument("--music-level", type=float, help="override: bed LUFS in pauses")
    ap.add_argument("--duck", type=float, default=8.0)
    ap.add_argument("--loop", action="store_true", help="the video loops: music stops on the last frame (no fade)")
    ap.add_argument("--sfx", action="store_true", help="pop when the hook/CTA appear, whoosh on b-roll (~20 dB under voice)")
    ap.add_argument("--denoise", default="auto", choices=["auto", "rnnoise", "afftdn", "off"])
    ap.add_argument("--target", type=float, default=-14.0, help="loudness LUFS")
    ap.add_argument("--model", default="large-v3-turbo")
    ap.add_argument("--lang", default="ro")
    ap.add_argument("--clean", action="store_true", help="also render a version without burned captions")
    ap.add_argument("--no-cover", action="store_true", help="skip cover_9x16.jpg / thumb_16x9.jpg")
    ap.add_argument("--cover-title", help="text on the cover (default: the hook)")
    ap.add_argument("--resolve", action="store_true", help="DaVinci Resolve package (FCPXML/EDL/OTIO/SRT/stems)")
    ap.add_argument("--alpha", action="store_true", help="with --resolve: captions_alpha.mov overlay (ProRes 4444)")
    ap.add_argument("--mac-dir", default="/Users/Shared/Claude-Edit")
    ap.add_argument("--redo", action="store_true", help="ignore cached transcript / face tracks")
    ap.add_argument("--crf", type=int, help="x264 CRF (default 20 social / 18 YouTube)")
    a = ap.parse_args()

    t0 = time.time()
    log = []
    out = os.path.abspath(a.outdir)
    work = os.path.join(out, "work")
    os.makedirs(work, exist_ok=True)
    inputs = [os.path.abspath(p) for p in a.inputs]
    infos = [vc.media_info(p) for p in inputs]
    if a.format == "source":
        W, H = infos[0]["w"], infos[0]["h"]
    else:
        W, H, _ = vc.canvas_for(a.format)
    vertical = H > W * 1.2
    landscape = W > H * 1.2
    captions = a.captions if a.captions != "auto" else ("none" if landscape else "karaoke")
    pace = a.pace or ("tight" if not landscape else "normal")
    punch = a.punch if a.punch is not None else (1.12 if not landscape else 1.08)
    fmt_arg = a.format if a.format != "source" else f"{W}x{H}"
    plat_max = {"reels": 180, "shorts": 180, "vertical": 180, "tiktok": 600}.get(a.format)

    # 1 probe
    step("1 probe", py("probe.py") + inputs, log)

    # 2 transcribe (cached)
    words = os.path.join(work, "words.json")
    has_audio = any(i.get("has_audio") for i in infos)
    if a.words:
        wsrc = vc.load_json(a.words)
        if [s["path"] for s in wsrc["sources"]] != inputs:
            raise vc.EditError(f"--words {a.words} was made from other clips: {[s['name'] for s in wsrc['sources']]}")
        if os.path.abspath(a.words) != words:
            shutil.copy(a.words, words)
            txt = os.path.splitext(a.words)[0] + ".txt"
            if os.path.exists(txt):
                shutil.copy(txt, os.path.join(work, "words.txt"))
        print(f"\n=== 2 transcribe: using {a.words}")
    elif has_audio:
        cached = False
        if os.path.exists(words) and not a.redo:
            w = vc.load_json(words)
            cached = [s["path"] for s in w["sources"]] == inputs and w.get("model") == a.model
        if cached:
            print(f"\n=== 2 transcribe: using cached {words}")
        else:
            step("2 transcribe", py("transcribe.py") + inputs + ["-o", words, "--model", a.model, "--lang", a.lang], log)
    else:
        print("\n=== 2 transcribe: skipped (no audio)")
        captions = "none"

    # 3 plan cuts
    cuts = os.path.join(work, "cuts.json")
    zoom_every = "3.5" if not landscape else "7"
    if a.cut == "auto" and has_audio:
        cmd = py("plan_cuts.py") + [words, "-o", cuts, "--pace", pace, "--zoom-every", zoom_every]
        for k in ("select", "drop", "restore", "cold_open", "keep_words"):
            if getattr(a, k):
                cmd += [f"--{k.replace('_', '-')}", getattr(a, k)]
        for r in a.cut_range or []:
            cmd += ["--cut", r]
        for r in a.add_range or []:
            cmd += ["--add", r]
    elif a.cut == "silence" and has_audio:
        cmd = py("plan_cuts.py") + ["--silence-only"] + inputs + ["-o", cuts, "--pace", pace, "--zoom-every", zoom_every]
    else:
        cmd = py("plan_cuts.py") + ["--full"] + inputs + ["-o", cuts, "--zoom-every", zoom_every]
    if a.cut != "auto" and os.path.exists(words):
        cmd += ["--words", words]
    if plat_max:
        cmd += ["--platform-max", str(plat_max)]
    step("3 plan cuts", cmd, log)

    # 4 reframe analysis (cached)
    tracks, track_args = {}, []
    from render_cuts import face_band, plan_reframe
    for si, info in enumerate(infos):
        if not info.get("has_video"):
            continue
        same = abs(info["w"] / info["h"] - W / H) < 0.01
        tj = os.path.join(work, f"track_{si}.json")
        want = a.reframe in ("auto", "track", "wide", "blur", "center") and (not same or info["h"] > info["w"])
        if want:
            if os.path.exists(tj) and not a.redo and vc.load_json(tj).get("source") == info["path"] \
                    and vc.load_json(tj).get("target") == f"{W}:{H}":
                print(f"\n=== 4 reframe [{si}]: using cached {tj}")
            else:
                step(f"4 reframe [{si}]", py("reframe.py") + [info["path"], "-o", tj, "--target", f"{W}:{H}"], log)
            tracks[si] = vc.load_json(tj)
            track_args += ["--track", f"{si}={tj}"]
    band = None
    for si, info in enumerate(infos):
        if si in tracks:
            _, _, _, _, mode = plan_reframe(info, W, H, a.reframe, tracks[si])
            band = face_band(info, tracks[si], W, H, mode)
            if band:
                print(f"face band {band[0]}-{band[1]} px (reframe {mode}, face {tracks[si]['face_h']:.0%} of the source height)")
                break

    # 5 captions + SRT
    ass = os.path.join(work, "captions.ass")
    srt = os.path.join(out, f"{a.name}.srt")
    if has_audio and os.path.exists(words):
        cmd = py("captions.py") + [words, "--cuts", cuts, "-o", ass, "--srt", srt, "--format", fmt_arg,
                                   "--style", captions, "--accent", a.accent]
        if vertical:
            cmd += ["--platform", "universal"]
        if a.hook:
            cmd += ["--hook", a.hook, "--hook-dur", str(a.hook_dur)]
        if a.cta:
            cmd += ["--cta", a.cta, "--cta-dur", str(a.cta_dur)]
        if band:
            cmd += ["--avoid", f"{band[0]}:{band[1]}"]
        for r in a.replace or []:
            cmd += ["--replace", r]
        step("5 captions", cmd, log)
    elif a.hook or a.cta:
        print("note: --hook/--cta need an audio transcript in this version; skipped")

    # 6 audio
    cut_wav = os.path.join(work, "cut.wav")
    mix = os.path.join(work, "mix.wav")
    stems = os.path.join(work, "stems")
    c = vc.load_json(cuts)
    sfx = []
    if a.sfx:
        if a.hook:
            sfx.append({"t": 0.04, "kind": "pop"})
        if a.cta:
            sfx.append({"t": max(a.hook_dur if a.hook else 0, c["duration"] - a.cta_dur) + 0.02, "kind": "pop"})
        for b in vc.load_json(a.broll) if a.broll else []:
            sfx.append({"t": max(0.0, float(b["at"]) - 0.12), "kind": "whoosh"})
        vc.save_json(sfx, os.path.join(work, "sfx.json"))
    if has_audio:
        step("6a cut audio", py("render_cuts.py") + [cuts, "--audio-only", cut_wav], log)
        cmd = py("audio_master.py") + [cut_wav, "-o", mix, "--target", str(a.target), "--denoise", a.denoise,
                                       "--stems", stems, "--json", os.path.join(work, "audio.json")]
        if a.music:
            cmd += ["--music", os.path.abspath(a.music), "--music-under", str(a.music_under), "--duck", str(a.duck),
                    "--music-end", "cut" if a.loop else "fade"]
            if a.music_level is not None:
                cmd += ["--music-level", str(a.music_level)]
        if sfx:
            cmd += ["--sfx", os.path.join(work, "sfx.json")]
        step("6b master audio", cmd, log)

    # 7 render
    final = os.path.join(out, f"{a.name}.mp4")
    base = py("render_cuts.py") + [cuts, "--format", fmt_arg, "--reframe", a.reframe, "--punch", str(punch),
                                   "--grade", a.grade, "--zoom-cuts", a.zoom_cuts,
                                   "--gop", "youtube" if a.format in ("youtube", "landscape", "youtube4k") else "social"]
    if a.crf is not None:
        base += ["--crf", str(a.crf)]
    base += track_args
    if has_audio:
        base += ["--audio", mix]
    if a.push:
        base += ["--push", str(a.push)]
    if a.broll:
        base += ["--broll", os.path.abspath(a.broll)]
    if a.stabilize:
        base += ["--stabilize"]
    if a.vdenoise:
        base += ["--vdenoise"]
    burn = captions != "none" or a.hook or a.cta
    step("7 render", base + (["--ass", ass] if burn and os.path.exists(ass) else []) + ["-o", final], log)
    if a.clean and burn:
        step("7b render clean", base + ["-o", os.path.join(out, f"{a.name}_fara_subtitrari.mp4")], log)

    # 8 QC
    qcj = os.path.join(out, "qc", "qc.json")
    qc = py("qc.py") + [final, "--format", fmt_arg, "--cuts", cuts, "--target", str(a.target),
                        "--sheets", os.path.join(out, "qc"), "--json", qcj]
    if burn and os.path.exists(ass):
        qc += ["--ass", ass]
    if os.path.exists(words):
        qc += ["--words", words]
    step("8 QC", qc, log)

    # 9 cover / thumbnail
    cover = None
    if not a.no_cover:
        cmd = py("cover.py") + [cuts, "-o", out, "--format", fmt_arg] + track_args
        title = a.cover_title or a.hook
        if title:
            cmd += ["--title", title]
        try:
            step("9 cover", cmd, log)
            cover = os.path.join(out, "cover_9x16.jpg" if H > W else "thumb_16x9.jpg")
        except SystemExit as e:
            WARNS.append(f"[9 cover] skipped: {e}")

    # chapters draft for 16:9 YouTube (Claude rewrites the titles)
    chapters = None
    if landscape and c.get("phrases"):
        chapters = os.path.join(out, "chapters_draft.txt")
        t, last, rows = 0.0, -1e9, []
        by_id = {p["id"]: p for p in c["phrases"]}
        for g in c["segments"]:
            if t - last >= 30 or not rows:
                ids = [i for i in g.get("phrases", []) if i in by_id]
                txt = by_id[ids[0]]["text"] if ids else g.get("text", "")
                rows.append(f"{int(t // 60)}:{int(t % 60):02d} {' '.join(txt.split()[:7])}")
                last = t
            t += g["e"] - g["s"]
        with open(chapters, "w", encoding="utf-8") as f:
            f.write("# YouTube chapters DRAFT: first at 0:00, >= 3 chapters, each >= 10 s. Rewrite the titles\n"
                    "# (2-5 words, Romanian) and merge/move them to real topic changes before giving them to the user.\n"
                    + "\n".join(rows) + "\n")

    # 10 DaVinci package
    if a.resolve:
        cmd = py("export_resolve.py") + [cuts, "-o", os.path.join(out, "davinci"), "--mac-dir", a.mac_dir,
                                         "--final", final, "--zip", "--format", fmt_arg] + track_args
        if os.path.exists(srt):
            cmd += ["--srt", srt]
        if os.path.isdir(stems):
            cmd += ["--stems", stems]
        if a.alpha and os.path.exists(ass):
            cmd += ["--alpha", ass]
        step("10 DaVinci package", cmd, log)

    c = vc.load_json(cuts)
    for w in c.get("warnings", []):
        WARNS.insert(0, f"[3 plan cuts] {w}")
    q = vc.load_json(qcj) if os.path.exists(qcj) else {"fail": None, "warn": None, "results": []}
    for lvl, msg in q.get("results", []):
        if lvl in ("FAIL", "WARN"):
            WARNS.append(f"[8 QC] {lvl} {msg}")
    src_total = sum(s["duration"] for s in c["sources"])
    sizes = {os.path.basename(p): round(os.path.getsize(p) / 1e6, 1) for p in
             [final, srt, cover, os.path.join(out, "davinci.zip")] if p and os.path.exists(p)}
    summary = {"final": final, "srt": srt if os.path.exists(srt) else None, "format": f"{W}x{H}",
               "duration": c["duration"], "source_duration": round(src_total, 2),
               "segments": len(c["segments"]), "captions": captions, "pace": pace, "punch": punch,
               "cover": cover, "chapters_draft": chapters, "sizes_mb": sizes,
               "qc_sheets": [os.path.join(out, "qc", f) for f in ("qc_sheet.jpg", "qc_captions.jpg")
                             if os.path.exists(os.path.join(out, "qc", f))],
               "qc": {"fail": q.get("fail"), "warn": q.get("warn")}, "warnings": WARNS,
               "unused_sources": c.get("unused_sources", []),
               "davinci_zip": os.path.join(out, "davinci.zip") if a.resolve else None,
               "phrases": os.path.join(work, "phrases.txt"), "total_seconds": round(time.time() - t0, 1),
               "steps": log}
    vc.save_json(summary, os.path.join(out, "summary.json"))
    if WARNS:
        print("\n=== WARNINGS (read each one; they are also in summary.json)")
        for w in WARNS:
            print("  " + w)
    print(f"\n=== DONE in {summary['total_seconds']}s: {final} ({c['duration']:.1f}s from {src_total:.1f}s source, "
          f"{len(c['segments'])} segments); QC: {q.get('fail')} FAIL, {q.get('warn')} WARN"
          f"{' -> FIX BEFORE DELIVERY' if q.get('fail') else ''}")
    print("sizes: " + ", ".join(f"{k} {v} MB" for k, v in sizes.items()))
    print(f"LOOK at: {', '.join(summary['qc_sheets'] + ([cover] if cover else []))}   |   phrases: {summary['phrases']}")


if __name__ == "__main__":
    main()
