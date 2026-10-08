#!/usr/bin/env python3
"""Transcribe one or more clips with faster-whisper -> words.json (word timestamps) + transcript.txt (+ SRT).

Defaults are tuned for Romanian: model large-v3-turbo (small drops diacritics on noisy audio), language ro,
beam 5, condition_on_previous_text False, VAD off (it swallowed first words in tests), a prompt that
nudges verbatim fillers and comma-below diacritics. Post-processing:
  * ş/ţ (cedilla) -> ș/ț (comma below), NFC
  * clitic / punctuation tokens merged ("v" + "-a" -> "v-a", "corecte" + "." -> "corecte.")
  * word STARTS after a pause are snapped forward to the real speech onset from the energy envelope
    (whisper starts after pauses were measured 0.2-0.6 s early)
Audio is decoded with the ffmpeg CLI (faster_whisper.decode_audio crashes with PyAV 19).

words.json schema:
  {"language","model","sources":[{"path","name","duration"}],
   "segments":[{"src","s","e","text"}], "words":[{"src","w","s","e","p"}]}

Examples:
  transcribe.py clip.mov -o work/words.json
  transcribe.py a.mov b.mov -o work/words.json --srt work/raw.srt
  transcribe.py clip.mp4 -o w.json --model small          # fast draft (worse Romanian)
  transcribe.py clip.mp4 -o w.json --lang en --prompt ""
"""
import argparse
import os
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
    words, segments, sources = [], [], []
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
        for s in segs:
            segments.append({"src": si, "s": round(s.start, 3), "e": round(s.end, 3), "text": vc.fix_ro(s.text.strip())})
            for w in s.words or []:
                sw.append({"src": si, "w": vc.fix_ro(w.word.strip()), "s": round(w.start, 3), "e": round(w.end, 3),
                           "p": round(w.probability, 3)})
        sw = merge_tokens(sw)
        el = time.time() - t1
        moved = 0
        if not a.no_refine and sw:
            db, hop = vc.envelope_db(info["path"], rnn)
            thr, _ = vc.speech_threshold(db)
            moved = refine_starts(sw, db, hop, thr)
        words += sw
        lang_found = tinfo.language
        print(f"[{si}] {info['name']}: {len(sw)} words, lang={lang_found}, {el:.1f}s for {tinfo.duration:.1f}s audio "
              f"(RTF {el / max(tinfo.duration, 0.01):.2f}), {moved} starts snapped to speech onset")

    out = {"language": a.lang, "model": a.model, "sources": sources, "segments": segments, "words": words}
    vc.save_json(out, a.out)
    # human-readable transcript for Claude to read (segments with times)
    txt = os.path.splitext(a.out)[0] + ".txt"
    with open(txt, "w", encoding="utf-8") as f:
        for s in segments:
            f.write(f"[{s['src']}] {vc.fmt_tc(s['s'])}-{vc.fmt_tc(s['e'])}  {s['text']}\n")
        low = [w for w in words if w["p"] < 0.5]
        if low:
            f.write("\n# low-confidence words (check names/brands/terms):\n")
            for w in low:
                f.write(f"#  [{w['src']}] {vc.fmt_tc(w['s'])} '{w['w']}' p={w['p']}\n")
    if a.srt:
        with open(a.srt, "w", encoding="utf-8") as f:
            f.write(to_srt([w for w in words if w["src"] == 0]))
    print(f"wrote {a.out} and {txt}{' and ' + a.srt if a.srt else ''} ({time.time() - t0:.1f}s total)")


if __name__ == "__main__":
    main()
