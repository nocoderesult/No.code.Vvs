#!/usr/bin/env python3
"""Plan the edit: remove silences, fillers (ăă, îî, "deci, practic."...) and retakes -> cuts.json + phrases.txt.

Whisper decides WHAT was said, an energy envelope (RNNoise-denoised) decides WHERE speech starts/ends.
Words are grouped into numbered phrases (P1, P2, ...) split at pauses >= --gap, at sentence ends, at Whisper
segment boundaries (fluent speech often has no punctuation) and, above --max-phrase s (8), at the best comma
or pause inside, so --select/--cold-open can pick single sentences. Then:
  * retakes   : a phrase whose first 6 words match the next phrase (difflib >= 0.72) is dropped (speaker restarted)
  * fillers   : phrases made only of hesitations/discourse markers are dropped; hesitations at phrase edges trimmed
  * boundaries: start snapped to real speech onset, end never before whisper's word end, then padded
Clips with no speech (no audio track, or only ambience) become one whole-clip phrase marked NO-SPEECH, in
story order, so they are never dropped silently; phrases with words transcribe.py flagged are marked SUSPECT.
Each kept segment also gets "zooms": word-boundary points (no time jump) where render_cuts.py --zoom-cuts
alternates the framing, so a long take changes picture every <= --zoom-every s (first change by 1.2-2.0 s).
Read phrases.txt, then re-run with --select / --drop / --cold-open / --cut to make editorial decisions
(story order, hook first, target length). Cut points are snapped to the output frame grid.

cuts.json schema (all times in SOURCE seconds; order of "segments" = output order):
  {"fps":"30/1", "sources":[{"path","name","duration","fps"}],
   "segments":[{"src","s","e","phrases":[...],"text","zooms":[source s, ...]}], "phrases":[...], "removed":[...],
   "duration":out_s, "unused_sources":[...]}

Examples:
  plan_cuts.py work/words.json -o work/cuts.json                       # auto: silences+fillers+retakes
  plan_cuts.py work/words.json -o work/cuts.json --pace tight          # Shorts/Reels rhythm
  plan_cuts.py work/words.json -o work/cuts.json --select P7,P1-P5     # cold open on P7, then P1..P5
  plan_cuts.py work/words.json -o work/cuts.json --drop P3 --cut 0:12.40-12.95 --keep-words practic
  plan_cuts.py --silence-only clip.mp4 -o work/cuts.json               # no transcript (music/b-roll/talk)
  plan_cuts.py --full a.mp4 b.mp4 -o work/cuts.json                    # no cutting, just join clips
"""
import argparse
import difflib
import re

import numpy as np

import vcommon as vc

# pure hesitations: always removable
HESIT = {"ă", "ăă", "ăăă", "ăăăă", "â", "ââ", "î", "îî", "îîî", "ăm", "ăăm", "ăăăm", "îm", "îîm", "hm", "hmm", "mm",
         "mmm", "eee", "ee", "aaa", "aa", "ah", "eh", "ăh", "uhm", "um", "uh", "ehm", "îhm"}
# discourse markers: removable only when a whole phrase consists of them (plus hesitations)
WEAK = HESIT | {"a", "e", "deci", "practic", "adică", "gen", "bine", "na", "păi", "uite", "așa", "știi", "ok", "okay",
                "okei", "bun", "zic", "cumva", "efectiv", "oricum", "da", "nu", "în", "fine", "fapt", "de", "să", "cum",
                "pur", "și", "simplu", "ideea", "că", "so", "like", "well", "yeah"}
STRONG_WEAK = {"a", "e", "deci", "păi", "practic", "adică", "gen"}
PACE = {  # gap (split at pauses >=), pre/post padding, min keep length
    "tight": dict(gap=0.25, pre=0.05, post=0.10, min_keep=0.25),
    "normal": dict(gap=0.30, pre=0.06, post=0.12, min_keep=0.25),
    "relaxed": dict(gap=0.50, pre=0.10, post=0.20, min_keep=0.30),
}


HESIT_RE = re.compile(r"([ăâîaeiou])\1+[mh]?|[ăâî]m+|h?m{2,}|hm+|[ăâîae]h|uh|uhm|ehm|âu|ăăm")


def is_hesit(t):
    return t in HESIT or bool(HESIT_RE.fullmatch(t))


def norm(w):
    return re.sub(r"[^\wăâîșț-]", "", vc.fix_ro(w).lower())


def phrases_of(words, gap, max_len=8.0):
    """Split at pauses >= gap, sentence-final punctuation and Whisper segment boundaries; then split phrases
    longer than max_len at their best internal comma/pause."""
    out, cur = [], []
    for w in words:
        if cur and (w["s"] - cur[-1]["e"] >= gap or cur[-1]["w"].rstrip().endswith((".", "!", "?", "…"))
                    or ("si" in w and "si" in cur[-1] and w["si"] != cur[-1]["si"])):
            out.append(cur)
            cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return [p for ph in out for p in split_long(ph, max_len)]


def split_long(ph, max_len, min_part=1.5):
    """Recursively split a phrase longer than max_len at the internal word boundary with the best score:
    comma/semicolon after the word, then the longest pause, slightly preferring the middle."""
    dur = ph[-1]["e"] - ph[0]["s"]
    if dur <= max_len or len(ph) < 4:
        return [ph]
    best, bi = -1e9, None
    for i in range(1, len(ph)):
        left, right = ph[i - 1]["e"] - ph[0]["s"], ph[-1]["e"] - ph[i]["s"]
        if left < min_part or right < min_part:
            continue
        gap = max(0.0, ph[i]["s"] - ph[i - 1]["e"])
        sc = (1.0 if ph[i - 1]["w"].rstrip().endswith((",", ";", ":", "–", "—")) else 0) + min(gap, 0.4) / 0.4 \
            - 0.6 * abs(left - dur / 2) / dur
        if sc > best:
            best, bi = sc, i
    if bi is None:
        return [ph]
    return split_long(ph[:bi], max_len, min_part) + split_long(ph[bi:], max_len, min_part)


def is_filler(ph, keep_words):
    toks = [t for t in (norm(w["w"]) for w in ph) if t]
    if not toks or any(t in keep_words for t in toks):
        return False
    if len(toks) == 1:  # a lone "a"/"e" is often a real word or a spelled letter
        return is_hesit(toks[0])
    return all(t in WEAK or is_hesit(t) for t in toks) and any(is_hesit(t) or t in STRONG_WEAK for t in toks)


def is_retake(a, b, thr=0.72, k=6):
    x = " ".join(norm(w["w"]) for w in a[:k])
    y = " ".join(norm(w["w"]) for w in b[:k])
    return len(x) > 8 and difflib.SequenceMatcher(None, x, y).ratio() >= thr


def refine(t0, t1, db, hop, thr, search=1.2):
    """start -> first frame above thr near t0; end -> last frame above thr near t1."""
    i0, i1 = int(t0 / hop), int(t1 / hop)
    lo, hi = max(0, int((t0 - 0.15) / hop)), min(len(db) - 1, int((t1 + 0.15) / hop))
    a = np.where(db[lo: min(hi, i0 + int(search / hop))] > thr)[0]
    s = (lo + a[0]) * hop if len(a) else t0
    base = max(lo, i1 - int(search / hop))
    b = np.where(db[base: hi] > thr)[0]
    e = (base + b[-1] + 1) * hop if len(b) else t1
    return (s, e) if e > s else (t0, t1)


def parse_ids(spec, all_ids):
    """'P7,P1-P5' -> ['P7','P1','P2',...]"""
    out = []
    for part in [p.strip() for p in (spec or "").split(",") if p.strip()]:
        m = re.fullmatch(r"P?(\d+)\s*-\s*P?(\d+)", part, re.I)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            rng = range(a, b + 1) if a <= b else range(a, b - 1, -1)
            out += [f"P{i}" for i in rng]
        else:
            m = re.fullmatch(r"P?(\d+)", part, re.I)
            if not m:
                raise vc.EditError(f"bad phrase id '{part}' (use P3, P1-P5)")
            out.append(f"P{int(m.group(1))}")
    bad = [i for i in out if i not in all_ids]
    if bad:
        raise vc.EditError(f"unknown phrase id(s): {bad}; this plan has P1-P{len(all_ids)}. Phrase ids depend on "
                           f"--pace/--gap: run once without --select/--drop and read phrases.txt first")
    return out


def parse_ranges(specs):
    out = []
    for sp in specs or []:
        m = re.fullmatch(r"(?:(\d+):)?([\d.]+)-([\d.]+)", sp.strip())
        if not m:
            raise vc.EditError(f"bad range '{sp}' (use SRC:START-END, e.g. 0:12.4-13.1)")
        out.append((int(m.group(1) or 0), float(m.group(2)), float(m.group(3))))
    return out


def subtract(ranges, cut):
    s0, e0 = cut
    out = []
    for s, e in ranges:
        if e <= s0 or s >= e0:
            out.append((s, e))
            continue
        if s < s0:
            out.append((s, s0))
        if e > e0:
            out.append((e0, e))
    return out


def plan_from_words(W, a, P):
    keep_words = {norm(x) for x in (a.keep_words or "").split(",") if x.strip()}
    rnn = vc.model_path("rnnoise")
    phrases, removed = [], []
    pid = 0
    vc.assign_segments(W["words"], W.get("segments", []))
    vc.tidy_transcript(W["words"])  # no-op on new transcripts (transcribe.py already did it)
    for si, src in enumerate(W["sources"]):
        words = [w for w in W["words"] if w.get("src", 0) == si]
        if not words:
            # no speech (no audio track, or ambience only): keep the whole clip as one phrase in story order so the
            # footage never disappears silently; Claude decides (--drop / --cut / move it to --broll)
            pid += 1
            why = "clip fără sunet" if not src.get("has_audio", True) else "fără vorbire, doar sunet ambiental"
            phrases.append({"id": f"P{pid}", "src": si, "s": 0.0, "e": src["duration"], "text": f"({why})",
                            "status": "keep", "kind": "nospeech", "ks": 0.0, "ke": src["duration"]})
            continue
        db, hop = vc.envelope_db(src["path"], rnn)
        thr, floor = vc.speech_threshold(db)
        phs = phrases_of(words, P["gap"], a.max_phrase)
        for k, ph in enumerate(phs):
            pid += 1
            p = {"id": f"P{pid}", "src": si, "s": ph[0]["s"], "e": ph[-1]["e"],
                 "text": vc.fix_ro(" ".join(w["w"] for w in ph)), "status": "keep"}
            flags = sorted({w["flag"] for w in ph if w.get("flag")})
            if flags:
                p["suspect"] = "; ".join(flags)
            if a.retakes and k + 1 < len(phs) and is_retake(ph, phs[k + 1]):
                p["status"] = "retake"
            elif a.fillers and is_filler(ph, keep_words):
                p["status"] = "filler"
            else:
                core = list(ph)
                if a.fillers:
                    while core and is_hesit(norm(core[0]["w"])) and norm(core[0]["w"]) not in keep_words:
                        removed.append({"src": si, "s": core[0]["s"], "e": core[0]["e"], "type": "hesitation",
                                        "text": core[0]["w"]})
                        core = core[1:]
                    while core and is_hesit(norm(core[-1]["w"])) and norm(core[-1]["w"]) not in keep_words:
                        removed.append({"src": si, "s": core[-1]["s"], "e": core[-1]["e"], "type": "hesitation",
                                        "text": core[-1]["w"]})
                        core = core[:-1]
                if not core:
                    p["status"] = "filler"
                else:
                    s, e = refine(core[0]["s"], core[-1]["e"], db, hop, thr)
                    e = max(e, core[-1]["e"])  # soft word tails sit below any threshold
                    ks, ke = max(0.0, s - P["pre"]), min(src["duration"], e + P["post"])
                    # phrases split without a pause (Whisper segment / long-phrase split): never reach into the
                    # neighbouring words, or a cold open starts with the previous sentence's last syllable
                    i0, i1 = words.index(ph[0]), words.index(ph[-1])
                    if i0 > 0:
                        ks = max(ks, (words[i0 - 1]["e"] + core[0]["s"]) / 2)
                    if i1 + 1 < len(words):
                        ke = min(ke, (core[-1]["e"] + words[i1 + 1]["s"]) / 2)
                    p["ks"], p["ke"] = round(ks, 3), round(max(ke, ks + 0.05), 3)
            if p["status"] != "keep":
                removed.append({"src": si, "s": p["s"], "e": p["e"], "type": p["status"], "text": p["text"]})
            phrases.append(p)
    return phrases, removed


def merge_touching(segs, tol=0.08):
    out = []
    for g in segs:
        if out and out[-1]["src"] == g["src"] and out[-1]["s"] <= g["s"] <= out[-1]["e"] + tol:
            out[-1]["e"] = max(out[-1]["e"], g["e"])
            out[-1]["phrases"] = out[-1]["phrases"] + g["phrases"]
            out[-1]["text"] = (out[-1]["text"] + " " + g["text"]).strip()
        else:
            out.append(dict(g))
    return out


def segments_from_phrases(phrases, order, P, cuts, adds, natural_order):
    by_id = {p["id"]: p for p in phrases}
    segs = [{"src": by_id[i]["src"], "s": by_id[i]["ks"], "e": by_id[i]["ke"], "phrases": [i],
             "text": by_id[i]["text"]} for i in order]
    segs += [{"src": src, "s": s, "e": e, "phrases": [], "text": "(manual keep)"} for src, s, e in adds]
    if natural_order:
        segs.sort(key=lambda g: (g["src"], g["s"]))
    segs = merge_touching(segs)
    out = []
    for g in segs:
        rngs = [(g["s"], g["e"])]
        for src, s, e in cuts:
            if src == g["src"]:
                rngs = subtract(rngs, (s, e))
        for s, e in rngs:
            if e - s >= P["min_keep"]:
                out.append({**g, "s": round(s, 3), "e": round(e, 3)})
    return out


def zoom_points(seg, words, first, every, min_shot=1.2):
    """Source times inside a kept segment where the framing may change without a time jump (zoom cut): gaps
    between words, preferring punctuation / Whisper segment ends, every <= `every` s, never closer than min_shot
    to a cut. The first output segment changes picture between 1.2 and 2.0 s (hook rhythm)."""
    s0, e0 = seg["s"], seg["e"]
    ws = [w for w in words if w.get("src", 0) == seg["src"] and w["s"] >= s0 - 0.02 and w["e"] <= e0 + 0.02]
    cands = []
    for a, b in zip(ws, ws[1:]):
        gap = b["s"] - a["e"]
        if gap < -0.01:
            continue
        punct = a["w"].rstrip().endswith((",", ".", "!", "?", "…", ";", ":")) or a.get("si") != b.get("si")
        cands.append(((a["e"] + b["s"]) / 2, punct, max(0.0, gap)))
    out, cur, k = [], s0, 0
    while True:
        lo, hi = cur + min_shot, cur + every
        target = 1.6 if (first and k == 0) else min(every, 2.6)
        if first and k == 0:
            hi = min(hi, cur + 2.0)
        elif e0 - cur <= every:
            break
        win = [c for c in cands if lo <= c[0] <= hi and e0 - c[0] >= min_shot]
        if not win and first and k == 0:
            win = [c for c in cands if lo <= c[0] <= cur + every and e0 - c[0] >= min_shot]
        if not win:
            later = [c for c in cands if c[0] > hi and e0 - c[0] >= min_shot]
            if not later or (first and k == 0):
                break
            win = later[:1]
        t = max(win, key=lambda c: (0.8 if c[1] else 0) + min(c[2], 0.3) - abs((c[0] - cur) - target) / every)[0]
        out.append(round(t, 3))
        cur, k = t, k + 1
    return out


def silence_only(infos, P, min_sil):
    rnn = vc.model_path("rnnoise")
    segs = []
    for si, info in enumerate(infos):
        if not info.get("has_audio"):
            segs.append({"src": si, "s": 0.0, "e": info["duration"], "phrases": [], "text": "(no audio)"})
            continue
        db, hop = vc.envelope_db(info["path"], rnn)
        thr, floor = vc.speech_threshold(db)
        on = db > thr
        idx = np.where(on)[0]
        if not len(idx):
            continue
        rngs, start, last = [], idx[0], idx[0]
        for k in idx[1:]:
            if (k - last) * hop > min_sil:
                rngs.append((start * hop, (last + 1) * hop))
                start = k
            last = k
        rngs.append((start * hop, (last + 1) * hop))
        for s, e in rngs:
            s, e = max(0.0, s - P["pre"]), min(info["duration"], e + P["post"])
            if segs and segs[-1]["src"] == si and s <= segs[-1]["e"]:
                segs[-1]["e"] = round(e, 3)
            elif e - s >= P["min_keep"]:
                segs.append({"src": si, "s": round(s, 3), "e": round(e, 3), "phrases": [], "text": ""})
        print(f"[{si}] {info['name']}: floor {floor:.1f} dB, threshold {thr:.1f} dB")
    return segs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="words.json (default) or media files with --silence-only/--full")
    ap.add_argument("-o", "--out", required=True, help="output cuts.json (phrases.txt written next to it)")
    ap.add_argument("--pace", choices=list(PACE), default="normal",
                    help="tight (Shorts/Reels), normal, relaxed (16:9 YouTube)")
    ap.add_argument("--gap", type=float, help="split phrases at pauses >= this (s); overrides --pace")
    ap.add_argument("--pre", type=float, help="padding before speech (s)")
    ap.add_argument("--post", type=float, help="padding after speech (s)")
    ap.add_argument("--min-keep", type=float, help="drop kept pieces shorter than this (s)")
    ap.add_argument("--select", help="phrase ids in OUTPUT order, e.g. 'P7,P1-P5' (others dropped)")
    ap.add_argument("--drop", help="phrase ids to drop, e.g. 'P3,P9'")
    ap.add_argument("--restore", help="phrase ids to keep even if auto-flagged (filler/retake)")
    ap.add_argument("--cold-open", help="phrase ids moved to the very start (hook first)")
    ap.add_argument("--cut", action="append", help="remove SRC:START-END (source seconds); repeatable")
    ap.add_argument("--add", action="append", help="force-keep SRC:START-END (source seconds); repeatable")
    ap.add_argument("--keep-words", help="comma list never treated as filler (e.g. 'practic,deci')")
    ap.add_argument("--no-fillers", dest="fillers", action="store_false", help="don't remove fillers")
    ap.add_argument("--no-retakes", dest="retakes", action="store_false", help="don't remove retakes")
    ap.add_argument("--silence-only", action="store_true", help="inputs are media: cut silences by energy only")
    ap.add_argument("--min-silence", type=float, default=0.35, help="--silence-only: cut pauses longer than this")
    ap.add_argument("--full", action="store_true", help="inputs are media: keep everything (join clips in order)")
    ap.add_argument("--fps", help="output frame rate for cut alignment (default: first source's rate)")
    ap.add_argument("--max-duration", type=float, help="warn if the result is longer than this (s)")
    ap.add_argument("--platform-max", type=float, help="hard platform length limit (s): WARN line in phrases.txt "
                    "and stdout if the plan is longer (pipeline passes 180 for Reels/Shorts)")
    ap.add_argument("--max-phrase", type=float, default=8.0, help="split phrases longer than this (s) at a comma/pause")
    ap.add_argument("--zoom-every", type=float, default=3.5,
                    help="zoom-cut points: change framing at least every N s inside long takes (3.5 vertical; "
                         "pipeline passes 7 for 16:9); 0 = none")
    ap.add_argument("--words", help="--full/--silence-only: words.json, only used for zoom-cut points")
    a = ap.parse_args()

    P = dict(PACE[a.pace])
    for k in ("gap", "pre", "post", "min_keep"):
        if getattr(a, k) is not None:
            P[k] = getattr(a, k)
    phrases, removed = [], []
    words_all = []
    if a.silence_only or a.full:
        infos = [vc.media_info(p) for p in a.inputs]
        sources = [{"path": i["path"], "name": i["name"], "duration": i["duration"], "fps": i.get("fps", "30"),
                    "has_audio": i["has_audio"]} for i in infos]
        if a.words:
            Wd = vc.load_json(a.words)
            if [s_["path"] for s_ in Wd["sources"]] == [i["path"] for i in infos]:
                words_all = vc.assign_segments(Wd["words"], Wd.get("segments", []))
        if a.full:
            segs = [{"src": k, "s": 0.0, "e": i["duration"], "phrases": [], "text": ""} for k, i in enumerate(infos)]
        else:
            segs = silence_only(infos, P, a.min_silence)
        cuts = parse_ranges(a.cut)
        for src, s, e in cuts:
            new = []
            for g in segs:
                new += ([{**g, "s": x, "e": y} for x, y in subtract([(g["s"], g["e"])], (s, e))]
                        if g["src"] == src else [g])
            segs = new
    else:
        if len(a.inputs) != 1 or not a.inputs[0].endswith(".json"):
            raise vc.EditError("give one words.json (or use --silence-only / --full with media files)")
        W = vc.load_json(a.inputs[0])
        sources = []
        for s in W["sources"]:
            i = vc.media_info(s["path"])
            sources.append({"path": i["path"], "name": i["name"], "duration": i["duration"], "fps": i.get("fps", "30"),
                            "has_audio": i["has_audio"]})
        W["sources"] = sources
        phrases, removed = plan_from_words(W, a, P)
        words_all = W["words"]
        ids = [p["id"] for p in phrases]
        by_id = {p["id"]: p for p in phrases}
        for i in parse_ids(a.restore, ids):
            p = by_id[i]
            if p["status"] != "keep":
                p["status"] = "keep"
                p["ks"], p["ke"] = round(max(0, p["s"] - P["pre"]), 3), round(p["e"] + P["post"], 3)
                removed = [r for r in removed if not (r["src"] == p["src"] and r["s"] == p["s"] and r["e"] == p["e"])]
        for i in parse_ids(a.drop, ids):
            by_id[i]["status"] = "dropped"
        if a.select:
            order = parse_ids(a.select, ids)
            for p in phrases:
                if p["id"] not in order and p["status"] == "keep":
                    p["status"] = "unselected"
            skipped = [i for i in order if by_id[i]["status"] != "keep"]
            if skipped:
                print(f"note: selected but flagged {skipped} -> not used (add them to --restore to force)")
            order = [i for i in order if by_id[i]["status"] == "keep"]
        else:
            order = [p["id"] for p in phrases if p["status"] == "keep"]
        if a.cold_open:
            co = [i for i in parse_ids(a.cold_open, ids) if by_id[i]["status"] == "keep"]
            order = co + [i for i in order if i not in co]
        segs = segments_from_phrases(phrases, order, P, parse_ranges(a.cut), parse_ranges(a.add),
                                     natural_order=not (a.select or a.cold_open))

    fps = vc.frac(a.fps) if a.fps else vc.frac(sources[0]["fps"])
    aligned = vc.align_segments(segs, fps)
    out_segs = [{k: v for k, v in g.items() if k not in ("fs", "fe", "S", "E")} | {"s": round(float(g["S"]), 6),
                                                                                       "e": round(float(g["E"]), 6)}
                for g in aligned]
    if a.zoom_every > 0 and words_all:
        for k, g in enumerate(out_segs):
            z = zoom_points(g, words_all, k == 0, a.zoom_every)
            if z:
                g["zooms"] = z
    total = float(sum(g["E"] - g["S"] for g in aligned))
    src_total = sum(s["duration"] for s in sources)
    kept = [0.0] * len(sources)
    for g in aligned:
        kept[g["src"]] += float(g["E"] - g["S"])
    unused = [{"src": k, "name": s["name"], "duration": round(s["duration"], 2)} for k, s in enumerate(sources)
              if kept[k] < 0.05]
    warns = []
    for u in unused:
        ids = [p["id"] for p in phrases if p["src"] == u["src"]]
        why = ("all its phrases are dropped/flagged: " + ",".join(ids)) if ids else "nothing kept"
        warns.append(f"WARN src[{u['src']}] {u['name']} ({u['duration']:.1f}s) is NOT in the edit ({why}). "
                     f"Intended? Otherwise --restore/--select it, or use it as --broll.")
    for p in phrases:
        if p.get("kind") == "nospeech" and p["status"] == "keep":
            warns.append(f"WARN {p['id']} src[{p['src']}] {sources[p['src']]['name']}: no speech, kept whole "
                         f"({p['e']:.1f}s) {p['text']}. Shorten it (--cut-range), drop it (--drop {p['id']}) or "
                         f"move it to --broll.")
        elif p.get("suspect") and p["status"] == "keep":
            warns.append(f"WARN {p['id']} SUSPECT ({p['suspect']}): \"{p['text'][:60]}\" - listen/check it is real "
                         f"speech, else --drop {p['id']}.")
    if a.platform_max and total > a.platform_max:
        warns.append(f"WARN planned length {total:.1f}s > platform max {a.platform_max:.0f}s: QC will FAIL. "
                     f"Choose phrases with --select/--drop.")
    cuts = {"version": 1, "fps": str(fps), "sources": sources, "segments": out_segs, "phrases": phrases,
            "removed": removed, "params": {**P, "pace": a.pace, "zoom_every": a.zoom_every},
            "duration": round(total, 3), "unused_sources": unused, "warnings": warns}
    vc.save_json(cuts, a.out)

    txt = a.out.rsplit(".", 1)[0] + "_phrases.txt" if not a.out.endswith("cuts.json") else \
        a.out[: -len("cuts.json")] + "phrases.txt"
    with open(txt, "w", encoding="utf-8") as f:
        f.write(f"# {len(phrases)} phrases | output {total:.2f}s of {src_total:.2f}s source "
                f"({100 * total / max(src_total, 0.01):.0f}%) | {len(out_segs)} segments @ {fps} fps\n")
        f.write("# status: keep / filler / retake / dropped / unselected.  Re-run with --select/--drop/--cold-open.\n")
        for p in phrases:
            st = p["status"].upper() + ("*" if p.get("suspect") else "")
            note = "  [NO-SPEECH]" if p.get("kind") == "nospeech" else \
                (f"  [SUSPECT: {p['suspect']}]" if p.get("suspect") else "")
            f.write(f"{p['id']:>4} [{p['src']}] {vc.fmt_tc(p['s'])}-{vc.fmt_tc(p['e'])} {st:10s} {p['text']}{note}\n")
        f.write("\n# OUTPUT ORDER\n")
        t = 0.0
        for g in out_segs:
            d = g["e"] - g["s"]
            z = f" [{len(g['zooms'])} zoom cut{'s' if len(g['zooms']) > 1 else ''}]" if g.get("zooms") else ""
            f.write(f"  out {vc.fmt_tc(t)} +{d:5.2f}s  src[{g['src']}] {vc.fmt_tc(g['s'])}-{vc.fmt_tc(g['e'])}  "
                    f"{','.join(g['phrases'])}{z}  {g['text'][:80]}\n")
            t += d
        if warns:
            f.write("\n" + "\n".join(warns) + "\n")
    print(open(txt, encoding="utf-8").read())
    print(f"wrote {a.out} and {txt}")
    if a.max_duration and total > a.max_duration:
        print(f"WARNING: {total:.1f}s > target {a.max_duration:.0f}s -> choose phrases with --select/--drop")


if __name__ == "__main__":
    main()
