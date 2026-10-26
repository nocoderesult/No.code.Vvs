#!/usr/bin/env python3
"""Transcribe one or more clips with faster-whisper -> words.json (word timestamps) + transcript.txt (+ SRT).

Defaults are tuned for Romanian: model large-v3-turbo (small drops diacritics on noisy audio), language ro,
beam 5, condition_on_previous_text False, VAD off (it swallowed first words in tests), a prompt that
nudges verbatim fillers and comma-below diacritics. Post-processing:
  * ş/ţ (cedilla) -> ș/ț (comma below), NFC
  * clitic / punctuation tokens merged ("v" + "-a" -> "v-a", "corecte" + "." -> "corecte.")
  * word STARTS after a pause are snapped forward to the real speech onset from the energy envelope
    (whisper starts after pauses were measured 0.2-0.6 s early)
  * hallucination screen (VAD stays off, so Whisper invents text on music/ambience/silence; measured: a 12 s
    ambient clip gave 'Să vă mulțumim pentru vizionare!' with p 0.72-0.95 and no_speech_prob 0.00). Per
    segment it checks: speech rate > 6 words/s, >= 2 zero-length words, speech energy (RNNoise envelope) in
    < 35% of the span, a known Romanian outro/credit phrase, and Whisper's own no_speech/logprob/compression
    stats. 2+ signals (or Whisper's stats) -> segment removed (listed in words.txt); 1 signal -> words kept
    but marked "flag" (plan_cuts shows the phrase as SUSPECT).
  * sentence punctuation Whisper leaves out at segment ends is added (vcommon.tidy_transcript)
Audio is decoded with the ffmpeg CLI (faster_whisper.decode_audio crashes with PyAV 19).

words.json schema:
  {"language","model","sources":[{"path","name","duration"}],
   "segments":[{"src","s","e","text","nsp","lp","cr"}], "words":[{"src","w","s","e","p","si"[,"flag"]}],
   "removed":[{"src","s","e","text","why"}]}

Examples:
  transcribe.py clip.mov -o work/words.json
  transcribe.py a.mov b.mov -o work/words.json --srt work/raw.srt
  transcribe.py clip.mp4 -o w.json --model small          # fast draft (worse Romanian)
  transcribe.py clip.mp4 -o w.json --lang en --prompt ""
"""
import argparse
import os
import re
import time

import numpy as np

import vcommon as vc

# Tested on Romanian TTS speech: this prompt kept "Ăă, deci, practic." and "subtitrări" verbatim; a prompt
# starting with "Salut!" biased the first words, no prompt gave "subtitri" and dropped the hesitation.
RO_PROMPT = "Vorbim despre editare video, subtitrări și sunet. Ăăă, deci, îîî, practic, așa că, în fine."
PUNCT_ONLY = set(".,!?;:…\"'„”«»-–—")


def merge_tokens(words):
    """Attach clitics ('-a', '-mi', '-l') and punctuation-only tokens to the previous word."""
    out = []
    for w in words:
        t = w["w"].strip()
        if not t or t in ("-", "–", "—"):
            continue
        if out and out[-1]["src"] == w["src"] and (t[0] == "-" or all(c in PUNCT_ONLY for c in t)):
            prev = out[-1]
            prev["w"] = prev["w"] + t
            prev["e"] = max(prev["e"], w["e"])
            prev["p"] = round(min(prev["p"], w["p"]), 3)
            continue
        out.append({**w, "w": t})
    return out


def refine_starts(words, db, hop, thr, min_gap=0.12, max_shift=0.8):
    """Move a word start forward to the first envelope frame above thr (only after a pause)."""
    n = 0
    for i, w in enumerate(words):
        gap = w["s"] - words[i - 1]["e"] if i and words[i - 1]["src"] == w["src"] else 9
        if gap < min_gap:
            continue
        a = int(w["s"] / hop)
        b = int(min(w["e"] - 0.04, w["s"] + max_shift) / hop)
        if b <= a or a >= len(db):
            continue
        above = np.where(db[a:b] > thr)[0]
        if len(above) and above[0] > 0:
            ns = round((a + above[0]) * hop, 3)
            if ns - w["s"] >= 0.03:
                w["s"] = ns
                n += 1
    return n


# Known Whisper hallucinations on non-speech audio (subtitle credits and YouTube outros from its training data),
# matched on vcommon.fold() text (lowercase, no diacritics). A real speaker CAN say these, so a match alone only
# flags the segment; it is removed only together with another signal.
HALLU_RE = re.compile(
    r"\b(va |sa va )?multum(esc|im)( frumos| mult)? (pentru|de) (vizionare|vizionat|urmarire|atentie)\b"
    r"|\babona(ti|ti-va|ti va|-va|eaza-te|eaza te)\b|\bnu uita(ti)? sa (va abonati|dati like|lasati un)"
    r"|\bsubtitr(are|area|ari)( realizata| facuta| de| traducere)|\bamara org\b|\blike (si|,)? ?(share|subscribe)"
    r"|\bapasati (pe )?clopotel")


def screen_segment(ws, db, hop, thr, nsp=0.0, lp=0.0, cr=1.0):
    """Hallucination signals for one Whisper segment's words -> (drop, [reasons])."""
    toks = [w for w in ws if re.search(r"\w", w["w"])]
    if not toks:
        return True, ["no words"]
    why = []
    span = toks[-1]["e"] - toks[0]["s"]
    if len(toks) >= 3 and len(toks) / max(span, 0.01) > 6.0:
        why.append(f"too fast ({len(toks) / max(span, 0.01):.0f} words/s)")
    z = sum(1 for w in toks if w["e"] - w["s"] < 0.02)
    if z >= 2 and z >= 0.25 * len(toks):
        why.append(f"{z} zero-length words")
    if db is not None and len(db):
        a, b = int(toks[0]["s"] / hop), int(toks[-1]["e"] / hop) + 1
        seg = db[max(0, a): max(a + 1, min(len(db), b))]
        if len(seg) and float(np.mean(seg > thr)) < 0.35:
            why.append(f"no speech energy ({100 * float(np.mean(seg > thr)):.0f}% of the span)")
    if HALLU_RE.search(vc.fold(" ".join(w["w"] for w in toks))):
        why.append("known outro/credit phrase")
    whisper = (nsp > 0.6 and lp < -1.0) or cr > 2.4
    if whisper:
        why.append(f"whisper no_speech {nsp:.2f} / logprob {lp:.2f} / compression {cr:.1f}")
    return whisper or len(why) >= 2, why


def to_srt(words, max_chars=42, max_dur=5.0):
    import re
    lines, cur = [], []
    for w in words:
        txt = " ".join(x["w"] for x in cur + [w])
        if cur and (len(txt) > max_chars or w["e"] - cur[0]["s"] > max_dur or re.search(r"[.!?]$", cur[-1]["w"])
                    or w["s"] - cur[-1]["e"] > 1.0):
            lines.append(cur)
            cur = []
        cur.append(w)
    if cur:
        lines.append(cur)

    def st(t):
        ms = int(round(max(0, t) * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    return "\n".join(f"{i + 1}\n{st(l[0]['s'])} --> {st(l[-1]['e'])}\n{vc.fix_ro(' '.join(x['w'] for x in l))}\n"
                     for i, l in enumerate(lines))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="media files (audio track 0 is used)")
    ap.add_argument("-o", "--out", required=True, help="output words.json")
    ap.add_argument("--model", default="large-v3-turbo",
                    help="faster-whisper model: large-v3-turbo (default, best RO), large-v3, medium, small (fast draft)")
    ap.add_argument("--lang", default="ro", help="language code (ro) or 'auto'")
    ap.add_argument("--beam", type=int, default=5)
    ap.add_argument("--prompt", default=None, help="initial_prompt (default: Romanian verbatim/diacritics prompt)")
    ap.add_argument("--vad", action="store_true", help="enable Silero VAD (can drop first words; off by default)")
    ap.add_argument("--threads", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--srt", help="also write an SRT of the raw (uncut) transcript, source 0 timeline")
    ap.add_argument("--no-refine", action="store_true", help="keep whisper's raw word starts")
    ap.add_argument("--no-screen", action="store_true", help="keep every segment (no hallucination screening)")
    a = ap.parse_args()

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise vc.EditError("faster-whisper missing: pip install --break-system-packages faster-whisper")

    infos = [vc.media_info(p) for p in a.inputs]
    for i in infos:
        if not i["has_audio"]:
            vc.log(f"warning: {i['name']} has no audio; it will have no words")
    lang = None if a.lang == "auto" else a.lang
    prompt = a.prompt if a.prompt is not None else (RO_PROMPT if a.lang == "ro" else None)
    t0 = time.time()
    model = WhisperModel(a.model, device="cpu", compute_type="int8", cpu_threads=a.threads)
    print(f"model {a.model} loaded in {time.time() - t0:.1f}s")
    rnn = vc.model_path("rnnoise")
    words, segments, sources, removed = [], [], [], []
    for si, info in enumerate(infos):
        sources.append({"path": info["path"], "name": info["name"], "duration": info["duration"]})
        if not info["has_audio"]:
            continue
        t1 = time.time()
        audio = vc.load_audio(info["path"], 16000)
        segs, tinfo = model.transcribe(audio, language=lang, beam_size=a.beam, word_timestamps=True,
                                       condition_on_previous_text=False, initial_prompt=prompt or None,
                                       vad_filter=a.vad,
                                       vad_parameters=dict(min_silence_duration_ms=500, speech_pad_ms=200) if a.vad else None)
        sw = []
        db, hop = vc.envelope_db(info["path"], rnn)
        thr, _ = vc.speech_threshold(db)
        n_removed = n_flag = 0
        for s in segs:
            ws = [{"src": si, "w": vc.fix_ro(w.word.strip()), "s": round(w.start, 3), "e": round(w.end, 3),
                   "p": round(w.probability, 3)} for w in s.words or []]
            text = vc.fix_ro(s.text.strip())
            drop, why = (False, []) if a.no_screen else screen_segment(
                ws, db, hop, thr, s.no_speech_prob, s.avg_logprob, s.compression_ratio)
            if drop:
                removed.append({"src": si, "s": round(s.start, 3), "e": round(s.end, 3), "text": text,
                                "why": "; ".join(why)})
                n_removed += 1
                continue
            k = len(segments)
            segments.append({"src": si, "s": round(s.start, 3), "e": round(s.end, 3), "text": text,
                             "nsp": round(s.no_speech_prob, 3), "lp": round(s.avg_logprob, 3),
                             "cr": round(s.compression_ratio, 2), **({"flag": why[0]} if why else {})})
            n_flag += bool(why)
            for w in ws:
                w["si"] = k
                if why:
                    w["flag"] = why[0]
            sw += ws
        sw = merge_tokens(sw)
        el = time.time() - t1
        moved = 0
        if not a.no_refine and sw:
            moved = refine_starts(sw, db, hop, thr)
        words += sw
        lang_found = tinfo.language
        print(f"[{si}] {info['name']}: {len(sw)} words, lang={lang_found}, {el:.1f}s for {tinfo.duration:.1f}s audio "
              f"(RTF {el / max(tinfo.duration, 0.01):.2f}), {moved} starts snapped to speech onset"
              + (f", {n_removed} hallucinated segment(s) removed" if n_removed else "")
              + (f", {n_flag} segment(s) flagged SUSPECT" if n_flag else ""))
        if not sw:
            print(f"[{si}] {info['name']}: NO SPEECH found (plan_cuts keeps it whole as a no-speech phrase)")

    nt = vc.tidy_transcript(words)
    out = {"language": a.lang, "model": a.model, "sources": sources, "segments": segments, "words": words,
           "removed": removed}
    vc.save_json(out, a.out)
    # human-readable transcript for Claude to read (segments with times)
    txt = os.path.splitext(a.out)[0] + ".txt"
    with open(txt, "w", encoding="utf-8") as f:
        for k, s in enumerate(segments):
            text = " ".join(w["w"] for w in words if w.get("si") == k) or s["text"]
            f.write(f"[{s['src']}] {vc.fmt_tc(s['s'])}-{vc.fmt_tc(s['e'])}  {text}"
                    f"{'   <- SUSPECT: ' + s['flag'] if s.get('flag') else ''}\n")
        for si, src in enumerate(sources):
            if not any(w["src"] == si for w in words):
                f.write(f"[{si}] (no speech in {src['name']})\n")
        if removed:
            f.write("\n# removed as likely Whisper hallucinations (not speech; restore with --no-screen if wrong):\n")
            for r in removed:
                f.write(f"#  [{r['src']}] {vc.fmt_tc(r['s'])}-{vc.fmt_tc(r['e'])} '{r['text']}' ({r['why']})\n")
        low = [w for w in words if w["p"] < 0.5]
        if low:
            f.write("\n# low-confidence words (check names/brands/terms):\n")
            for w in low:
                f.write(f"#  [{w['src']}] {vc.fmt_tc(w['s'])} '{w['w']}' p={w['p']}\n")
        f.write("\n# Confident errors are NOT listed above (e.g. 'pogneau' for 'porneau', p=0.98): proofread every\n"
                "# kept phrase as a Romanian reader and fix with --replace or by editing words.json.\n")
    if nt:
        print(f"punctuation: {nt} sentence boundaries / capitals fixed")
    if a.srt:
        with open(a.srt, "w", encoding="utf-8") as f:
            f.write(to_srt([w for w in words if w["src"] == 0]))
    print(f"wrote {a.out} and {txt}{' and ' + a.srt if a.srt else ''} ({time.time() - t0:.1f}s total)")


if __name__ == "__main__":
    main()
