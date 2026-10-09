#!/usr/bin/env python3
"""Self-QC of a finished video BEFORE delivery. Prints PASS / WARN / FAIL lines and writes contact sheets
for Claude to look at (Read tool): a general sheet and a caption sheet with the platform safe-zone overlay.

Checks: container faststart (moov before mdat), H.264 High yuv420p, resolution vs format, CFR fps,
BT.709 tags, AAC 48 kHz stereo, video/audio duration match (A/V sync proxy), expected duration from cuts.json,
platform length limits, loudness (integrated, true peak, LRA), long silences (missed cuts), black/frozen
stretches, the longest shot without a visual change, and captions: text (cedilla ş/ţ, Portuguese ã, common
Romanian words missing diacritics), every event box inside the safe zone, no caption under the hook/CTA,
and (with --words) caption speech rate (Whisper hallucinations come out at 10-20 words/s).
FAIL = must fix before delivery: container/sync/duration, over the platform length limit, loudness more than
1 LU off target, true peak above --tp, captions outside the safe zone or under a title, cedilla letters.
Sheets: qc_sheet.jpg has true colours (safe area as thin lines) -> judge framing, colour, skin there;
qc_captions.jpg has the UI zones shaded red and the measured caption (cyan) / title (magenta) boxes drawn.

Examples:
  qc.py out/final.mp4 --format reels --cuts work/cuts.json --ass work/captions.ass --sheets out/qc
  qc.py out/yt.mp4 --format youtube --target -14
"""
import argparse
import math
import os
import re
import struct

import vcommon as vc

NO_DIACRITICS = {  # common words written without diacritics by weak ASR / typing (word -> correct form)
    "si": "și", "sa": "să", "in": "în", "asa": "așa", "fara": "fără", "dupa": "după", "pana": "până", "cand": "când",
    "inca": "încă", "daca": "dacă", "astazi": "astăzi", "maine": "mâine", "multumesc": "mulțumesc", "putin": "puțin",
    "stiu": "știu", "stii": "știi", "atat": "atât", "cat": "cât", "niste": "niște", "ati": "ați", "sunteti": "sunteți",
    "cateva": "câteva", "inainte": "înainte", "intotdeauna": "întotdeauna", "incerc": "încerc", "gandesc": "gândesc",
    "romania": "România", "romana": "română", "bucuresti": "București", "urmariti": "urmăriți", "lasati": "lăsați",
    "intr": "într", "pasi": "pași", "subtitrari": "subtitrări", "aratam": "arătăm",
    "arat": "arăt", "fiti": "fiți", "faceti": "faceți", "puteti": "puteți", "vreti": "vreți", "stiti": "știți",
    "aveti": "aveți", "uitati": "uitați", "incepem": "începem",
    "intrebare": "întrebare", "raspuns": "răspuns", "pret": "preț", "bucatarie": "bucătărie",
    "mancare": "mâncare", "cumparat": "cumpărat", "gasit": "găsit", "facut": "făcut", "placut": "plăcut",
}
PLATFORM_MAX = {"reels": 180, "tiktok": 600, "shorts": 180, "youtube": 12 * 3600, "vertical": 180,
                "landscape": 12 * 3600, "youtube4k": 12 * 3600}


def scene_changes(path, thr=8.0):
    """Times where the picture changes (cuts, punch-in/zoom cuts, b-roll): ffmpeg scdet scores above thr."""
    st = vc.run(["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-i", path, "-map", "0:v:0", "-vf",
                 "scale=270:-2,scdet=threshold=0.1,metadata=print:key=lavfi.scd.score", "-f", "null", "-"],
                capture=True, check=False).stderr
    out, t = [], None
    for line in st.splitlines():
        m = re.search(r"pts_time:([\d.]+)", line)
        if m:
            t = float(m.group(1))
        m = re.search(r"lavfi\.scd\.score=([\d.]+)", line)
        if m and t is not None and float(m.group(1)) >= thr:
            out.append(t)
    return out


def moov_first(path):
    with open(path, "rb") as f:
        order = []
        while len(order) < 12:
            h = f.read(8)
            if len(h) < 8:
                break
            size, typ = struct.unpack(">I4s", h)
            typ = typ.decode("latin1")
            if size == 1:
                size = struct.unpack(">Q", f.read(8))[0]
                f.seek(size - 16, 1)
            elif size == 0:
                order.append(typ)
                break
            else:
                f.seek(size - 8, 1)
            order.append(typ)
    return ("moov" in order and "mdat" in order and order.index("moov") < order.index("mdat")), order


def detect(path, vf=None, af=None):
    args = ["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-i", path]
    if vf:
        args += ["-vf", vf]
    else:
        args += ["-vn"]
    if af:
        args += ["-af", af]
    else:
        args += ["-an"]
    return vc.run(args + ["-f", "null", "-"], capture=True, check=False).stderr


def ass_words(path):
    out = []
    for line in open(path, encoding="utf-8"):
        if line.startswith("Dialogue:"):
            txt = line.split(",", 9)[9].strip()
            if "\\p1" in txt:
                continue
            txt = re.sub(r"\{[^}]*\}", "", txt).replace("\\N", " ")
            out += txt.split()
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--format", default="reels", help="expected format (reels/tiktok/shorts/youtube/WxH)")
    ap.add_argument("--platform", help="safe-zone overlay (default from format; universal for vertical)")
    ap.add_argument("--cuts", help="cuts.json -> check expected duration")
    ap.add_argument("--ass", help="captions .ass -> spelling/diacritics check + caption sheet")
    ap.add_argument("--target", type=float, default=-14.0, help="target integrated LUFS")
    ap.add_argument("--tp", type=float, default=-1.0, help="max true peak dBTP after encoding")
    ap.add_argument("--sheets", help="folder for qc_sheet.jpg / qc_captions.jpg (default: next to video)")
    ap.add_argument("--words", help="words.json (with --cuts): caption speech-rate check")
    ap.add_argument("--max-static", type=float, help="WARN if a shot lasts longer without a visual change "
                    "(default 4 s vertical, 15 s 16:9; 0 = skip)")
    ap.add_argument("--json", help="write results JSON")
    a = ap.parse_args()

    res = []
    def rep(level, msg):
        res.append((level, msg))
        print(f"{level:4s} {msg}")

    i = vc.media_info(a.video)
    j = vc.ffprobe_json(a.video)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), {})
    au = next((s for s in j["streams"] if s["codec_type"] == "audio"), {})
    W, H, plat = vc.canvas_for(a.format)
    if H > W * 1.2:
        plat = a.platform or "universal"
    else:
        plat = a.platform or plat
    ok, order = moov_first(a.video)
    rep("PASS" if ok else "FAIL", f"faststart (moov before mdat): {order[:4]}")
    rep("PASS" if v.get("codec_name") == "h264" and v.get("profile") == "High" and v.get("pix_fmt") == "yuv420p"
        else "WARN", f"video {v.get('codec_name')} {v.get('profile')} {v.get('pix_fmt')} level {v.get('level')}")
    rep("PASS" if (i.get("w"), i.get("h")) == (W, H) else "FAIL", f"resolution {i.get('w')}x{i.get('h')} (expected {W}x{H})")
    rep("PASS" if not i.get("vfr") and i.get("fps_float") in (23.976, 24, 25, 29.97, 30, 50, 59.94, 60) else "WARN",
        f"frame rate {i.get('fps')} {'VFR' if i.get('vfr') else 'CFR'}")
    tags = (v.get("color_space"), v.get("color_transfer"), v.get("color_primaries"), v.get("color_range"))
    rep("PASS" if tags == ("bt709", "bt709", "bt709", "tv") else "WARN", f"colour tags {tags}")
    if au:
        rep("PASS" if au.get("codec_name") == "aac" and au.get("sample_rate") == "48000" and au.get("channels") == 2
            else "WARN", f"audio {au.get('codec_name')} {au.get('sample_rate')} Hz {au.get('channels')} ch")
        vd, ad = float(v.get("duration", 0)), float(au.get("duration", 0))
        fr = 1 / max(i.get("fps_float", 30), 1)
        rep("PASS" if abs(vd - ad) <= fr + 0.03 else "FAIL", f"durations video {vd:.3f}s / audio {ad:.3f}s "
            f"(diff {1000 * (ad - vd):+.0f} ms; render is frame-aligned so this is the A/V sync proxy)")
    else:
        rep("FAIL", "no audio stream")
    dur = i["duration"]
    if a.cuts:
        c = vc.load_json(a.cuts)
        segs = vc.align_segments(c["segments"], vc.frac(c["fps"]))
        exp = float(sum(g["E"] - g["S"] for g in segs))
        rep("PASS" if abs(dur - exp) < 0.05 else "FAIL", f"duration {dur:.3f}s vs cut list {exp:.3f}s")
    mx = PLATFORM_MAX.get(a.format)
    if mx:
        rep("PASS" if dur <= mx else "FAIL", f"length {dur:.1f}s (platform max {mx}s"
            f"{'; Shorts > 60 s with Content-ID music get blocked' if a.format == 'shorts' and dur > 60 else ''})")
    if au:
        L = vc.ebur128(a.video)
        rep("PASS" if abs(L["I"] - a.target) <= 1.0 else "FAIL", f"loudness {L['I']:.1f} LUFS (target {a.target} ±1)")
        rep("PASS" if L["TP"] <= a.tp else "FAIL", f"true peak {L['TP']:.1f} dBTP (max {a.tp})")
        rep("PASS" if L["LRA"] <= 11 else "WARN", f"loudness range {L['LRA']:.1f} LU (speech <= 7-11)")
        sil = re.findall(r"silence_start: ([\d.]+)[\s\S]*?silence_duration: ([\d.]+)",
                         detect(a.video, af="silencedetect=n=-45dB:d=0.9"))
        sil = [(float(s), float(d)) for s, d in sil]
        rep("PASS" if not sil else "WARN", "long silences (>0.9 s): " + (", ".join(f"{s:.1f}s+{d:.1f}" for s, d in sil[:8])
                                                                         or "none"))
    st = detect(a.video, vf="blackdetect=d=0.4:pix_th=0.08,freezedetect=n=-60dB:d=2.5")
    blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", st)
    frz = re.findall(r"freeze_start: ([\d.]+)", st)
    rep("PASS" if not blacks else "WARN", "black stretches: " + (", ".join(f"{float(x):.1f}-{float(y):.1f}s" for x, y in blacks)
                                                                 or "none"))
    rep("PASS" if not frz else "WARN", "frozen video (>2.5 s): " + (", ".join(f"{float(x):.1f}s" for x in frz) or "none"))
    ms = a.max_static if a.max_static is not None else (4.0 if H > W * 1.2 else 15.0)
    if ms > 0:
        ch = [0.0] + scene_changes(a.video) + [dur]
        gaps = sorted(((y - x, x) for x, y in zip(ch, ch[1:])), reverse=True)
        n_long = sum(1 for g, _ in gaps if g > ms)
        rep("PASS" if not n_long else "WARN", f"longest shot without a visual change {gaps[0][0]:.1f}s at "
            f"{gaps[0][1]:.1f}s ({len(ch) - 2} changes; {n_long} shot(s) > {ms:.0f}s"
            f"{': zoom cuts/--punch/b-roll' if n_long else ''})")
    if a.words and a.cuts:
        import captions as capm
        Wd = vc.load_json(a.words)
        ws = capm.remap(Wd["words"], vc.load_json(a.cuts))
        utt, cur = [], []
        for w in ws:
            if cur and w["s"] - cur[-1]["e"] > 0.3:
                utt.append(cur)
                cur = []
            cur.append(w)
        if cur:
            utt.append(cur)
        fast = [(len(u) / max(u[-1]["e"] - u[0]["s"], 0.01), u) for u in utt if len(u) >= 3]
        fast = [(r, u) for r, u in fast if r > 6.0]
        rep("PASS" if not fast else "WARN", "caption speech rate: " + (
            "; ".join(f"{u[0]['s']:.1f}s '{' '.join(w['w'] for w in u)[:40]}' {r:.0f} words/s" for r, u in fast[:3])
            + " - faster than speech: likely a Whisper hallucination, check and --drop/--cut it" if fast
            else "<= 6 words/s"))
    cap_times = None
    boxes = []
    if a.ass:
        words = ass_words(a.ass)
        txt = " ".join(words)
        bad = sorted(set(re.findall(r"\S*[şţŞŢãÃ]\S*", txt)))
        rep("PASS" if not bad else "FAIL", f"cedilla/foreign diacritics: {bad or 'none'}")

        def core(w):  # only edge punctuation; hyphenated clitics (s-a, n-a, c-a, într-o) are correct as written
            return re.sub(r"^\W+|\W+$", "", w.lower())
        sus = sorted({w for w in words if "-" not in core(w) and core(w) in NO_DIACRITICS
                      and core(w) != NO_DIACRITICS[core(w)].lower()})
        rep("PASS" if not sus else "WARN", f"words that probably miss diacritics: {sus or 'none'}")
        import captions as capm
        boxes, play = capm.ass_boxes(a.ass)
        if boxes:
            safe = vc.safe_box(plat, W, H)
            probs = capm.check_boxes(boxes, safe)
            rep("PASS" if not probs else "FAIL", "caption/title layout: " + (
                "; ".join(probs) if probs else
                f"all {len(boxes)} events inside the {plat} safe zone, no caption under the hook/CTA"))
        uniq = sorted(set(re.sub(r"[^\wăâîșțĂÂÎȘȚ-]", "", w) for w in words))
        print(f"INFO caption vocabulary ({len(uniq)}): {' '.join(uniq)[:1500]}")
        starts = []
        for line in open(a.ass, encoding="utf-8"):
            if line.startswith("Dialogue:") and ",W," in line:
                t = line.split(",")[1]
                h, m, s = t.split(":")
                starts.append(int(h) * 3600 + int(m) * 60 + float(s))
        starts = sorted(set(starts))
        titles = sorted({(b["name"], b["t0"], b["t1"]) for b in boxes if b["kind"] == "title"})
        extra = []
        for name, t0, t1 in titles:   # last frames of the hook (fade-out over captions) / CTA appearing
            extra += [max(0.0, t1 - 0.1)] if name == "hook" else [min(dur - 0.05, t0 + 0.3)]
        if starts or extra:
            step = max(1, len(starts) // 8)
            cap_times = sorted({0.0, *extra, *[min(dur - 0.05, t + 0.12) for t in starts[::step][:7] if t > 0.2]})
    out = a.sheets or os.path.dirname(os.path.abspath(a.video))
    os.makedirs(out, exist_ok=True)
    import contact_sheet as cs
    p1, _ = cs.build(a.video, os.path.join(out, "qc_sheet.jpg"), n=12, safe=plat if H > W else None, shade=False)
    print(f"INFO sheet (true colours, safe area as thin lines): {p1}")
    if cap_times:
        fpsf = float(vc.frac(i.get("fps", "30")))

        def overlay(t):
            tf = math.ceil(t * fpsf - 1e-6) / fpsf + 0.001   # the frame an accurate seek to t lands on
            return [(b["box"], (0, 255, 255) if b["kind"] == "caption" else (255, 0, 255))
                    for b in boxes if b["t0"] <= tf < b["t1"]]
        p2, _ = cs.build(a.video, os.path.join(out, "qc_captions.jpg"), times=cap_times[:12],
                         safe=plat if H > W else None, width=360 if H > W else 640, cols=4, overlay=overlay)
        print(f"INFO caption sheet (UI zones shaded, caption boxes cyan, hook/CTA boxes magenta): {p2}")
    nfail = sum(1 for l, _ in res if l == "FAIL")
    nwarn = sum(1 for l, _ in res if l == "WARN")
    print(f"RESULT: {nfail} FAIL, {nwarn} WARN -> {'fix before delivery' if nfail else 'ok to deliver (review WARN)'}; "
          f"now LOOK at the sheets with the Read tool")
    if a.json:
        vc.save_json({"results": res, "fail": nfail, "warn": nwarn}, a.json)


if __name__ == "__main__":
    main()
