#!/usr/bin/env python3
"""Master a voice track (after cutting) and optionally lay a ducked music bed under it.

Voice chain: highpass 80 Hz -> (mains hum notch) -> RNNoise denoise (bundled model; afftdn fallback) ->
de-mud EQ -2 dB @250 Hz -> presence +2 dB @3.5 kHz -> de-esser -> compressor 3:1 -> gentle expander.
Loudness: pass 0 measures after the chain and pre-gains + limits so loudnorm can stay LINEAR (plain
two-pass fell back to dynamic mode on quiet phone audio), then classic two-pass loudnorm.
Music: looped/trimmed, faded, normalized to --music-level LUFS (bed level in pauses), then ducked with an
offline gain curve computed from the voice (look-ahead 80 ms, attack 80 ms, release 450 ms, gaps < 0.35 s
held so it never pumps between words); mixed with amix normalize=0, true-peak limited (4x oversampled). Default target: -14 LUFS integrated, -1.5 dBTP (headroom for AAC).

Examples:
  audio_master.py work/cut.wav -o work/voice.wav
  audio_master.py work/cut.wav -o work/mix.wav --music track.mp3 --stems work/stems
  audio_master.py clip.mp4 -o voice.wav --denoise off --target -16      # podcast-ish / already clean
  audio_master.py work/cut.wav -o mix.wav --music m.mp3 --music-level -20 --duck 16
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile

import numpy as np

import vcommon as vc


def chain(denoise="auto", rnn=None, hum=None, deess=0.35, comp=True, floor_db=None):
    f = ["highpass=f=80:poles=2"]
    if hum:
        f += [f"bandreject=f={hum * k}:width_type=q:w=10" for k in (1, 2, 3)]
    if denoise == "auto":
        denoise = "off" if (floor_db is not None and floor_db < -62) else ("rnnoise" if rnn else "afftdn")
    if denoise == "rnnoise" and rnn:
        f.append(f"arnndn=m='{rnn}':mix=0.85")
    elif denoise in ("afftdn", "rnnoise"):
        f.append("afftdn=nr=12:nf=-45:tn=1")
    f += ["equalizer=f=250:t=q:w=1.0:g=-2", "equalizer=f=3500:t=q:w=1.2:g=2"]
    if deess > 0:
        f.append(f"deesser=i={deess}:m=0.5:f=0.5:s=o")
    if comp:
        f += ["acompressor=threshold=-20dB:ratio=3:attack=8:release=150:knee=4:makeup=3dB",
              "agate=threshold=0.01:ratio=2:range=0.25:attack=10:release=250"]
    return ",".join(f), denoise


def measure_I(src, pre):
    p = vc.run(["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-i", src, "-map", "0:a:0", "-af",
                f"{pre},ebur128", "-f", "null", "-"], capture=True)
    v = re.findall(r"I:\s+(-?[\d.]+) LUFS", p.stderr)
    return float(v[-1]) if v else -70.0


def loudnorm_json(stderr):
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", stderr, re.S)
    if not m:
        raise vc.EditError("loudnorm produced no measurement (silent input?)")
    return json.loads(m.group(0))


def master_voice(src, out, I=-14.0, TP=-1.5, LRA=11.0, **chain_kw):
    pre, used = chain(**chain_kw)
    i0 = measure_I(src, pre)
    if i0 < -60:
        raise vc.EditError(f"voice is silent or nearly silent ({i0} LUFS)")
    lim = 10 ** ((TP - 0.5) / 20)
    pre = f"{pre},volume={I - i0:.2f}dB,alimiter=limit={lim:.4f}:attack=2:release=60:level=false"
    p1 = vc.run(["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-i", src, "-map", "0:a:0", "-af",
                 f"{pre},loudnorm=I={I}:TP={TP}:LRA={LRA}:print_format=json", "-f", "null", "-"], capture=True)
    m = loudnorm_json(p1.stderr)
    ln = (f"loudnorm=I={I}:TP={TP}:LRA={LRA}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:"
          f"linear=true:print_format=json")
    p2 = vc.run(["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-y", "-i", src, "-map", "0:a:0", "-af",
                 f"{pre},{ln},aresample=48000,aformat=channel_layouts=stereo", "-ar", "48000", "-c:a", "pcm_s24le", out],
                capture=True)
    m2 = loudnorm_json(p2.stderr)
    return {"pass0_I": i0, "denoise": used, "normalization": m2.get("normalization_type"), "chain": pre}


def duck_curve(voice_mono, sr, duck_db, hop=0.01, hold=0.35, lookahead=0.08, attack=0.08, release=0.45):
    """Gain curve (dB per hop) for the music: 0 dB in pauses, -duck_db while the voice talks.
    Offline, so it can look ahead (music dips slightly BEFORE the first syllable) and never pumps between words."""
    h = int(sr * hop)
    n = len(voice_mono) // h
    rms = np.sqrt(np.mean(voice_mono[: n * h].reshape(n, h) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    thr = max(float(np.percentile(db, 10)) + 12, float(db.max()) - 38)
    act = db > thr
    # fill short gaps between words (hold) so the bed doesn't pump
    k = int(hold / hop)
    idx = np.where(act)[0]
    for a, b in zip(idx[:-1], idx[1:]):
        if 1 < b - a <= k:
            act[a:b] = True
    la = int(lookahead / hop)  # look-ahead: start ducking before speech
    act = act | np.concatenate([act[la:], np.zeros(la, bool)])
    target = np.where(act, -duck_db, 0.0)
    g = np.empty_like(target)
    cur = 0.0
    ca, cr = 1 - np.exp(-hop / attack), 1 - np.exp(-hop / release)
    for i, t in enumerate(target):
        cur += (t - cur) * (ca if t < cur else cr)
        g[i] = cur
    return g, hop, float(np.mean(act))


def mix_music(voice, music, out, stems=None, music_level=-20.0, duck=12.0, I=-14.0, TP=-1.5,
              fade_in=0.4, fade_out=1.5):
    dur = vc.media_info(voice)["duration"]
    tmp = tempfile.mkdtemp(prefix="ve_mix_")
    m_fit = os.path.join(tmp, "music_fit.wav")
    # loop/trim the music to the voice length, fade in/out
    vc.run(vc.ffmpeg_cmd("-stream_loop", "-1", "-i", music, "-t", f"{dur:.3f}", "-af",
                         f"aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d={fade_in},"
                         f"afade=t=out:st={max(0, dur - fade_out):.3f}:d={fade_out}",
                         "-c:a", "pcm_s24le", m_fit))
    mI = vc.ebur128(m_fit)["I"]
    if mI == float("-inf") or mI < -70:
        raise vc.EditError("music track is silent")
    g0 = music_level - mI
    sr = 48000
    v = vc.load_audio(voice, sr)
    raw = vc.run_bytes(["ffmpeg", "-nostdin", "-v", "error", "-i", m_fit, "-f", "f32le", "-ac", "2", "-ar", str(sr), "-"])
    m = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    gdb, hop, talk_ratio = duck_curve(v, sr, duck)
    t_s = np.arange(len(m)) / sr
    gain = 10 ** ((g0 + np.interp(t_s, (np.arange(len(gdb)) + 0.5) * hop, gdb)) / 20)
    m *= gain[:, None].astype(np.float32)
    music_out = os.path.join(tmp, "music_ducked.wav")
    p = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", "2", "-i", "-",
                        "-c:a", "pcm_s24le", music_out], input=m.tobytes(), capture_output=True)
    if p.returncode:
        raise vc.EditError(p.stderr.decode()[-500:])
    lim = f"aresample=192000,alimiter=limit={10 ** ((TP - 0.3) / 20):.4f}:attack=1:release=50:level=false,aresample=48000"
    vc.run(vc.ffmpeg_cmd("-i", voice, "-i", music_out, "-filter_complex",
                         f"[0:a][1:a]amix=inputs=2:normalize=0:duration=first,{lim}[o]", "-map", "[o]",
                         "-ar", "48000", "-c:a", "pcm_s24le", out))
    L = vc.ebur128(out)
    if abs(L["I"] - I) > 0.3:  # music adds a little loudness: trim the mix back onto the target
        fixed = out + ".tmp.wav"
        vc.run(vc.ffmpeg_cmd("-i", out, "-af", f"volume={I - L['I']:.2f}dB,{lim}", "-ar", "48000", "-c:a", "pcm_s24le", fixed))
        os.replace(fixed, out)
    # measure: music level while talking vs voice level (short-term, 400 ms windows)
    w = int(0.4 * sr)
    nw = min(len(v), len(m)) // w
    vr = 10 * np.log10(np.mean(v[: nw * w].reshape(nw, w) ** 2, 1) + 1e-12)
    mm = m[: nw * w].mean(1)
    mr = 10 * np.log10(np.mean(mm.reshape(nw, w) ** 2, 1) + 1e-12)
    talk = vr > vr.max() - 15
    vom = round(float(np.median(vr[talk]) - np.median(mr[talk])), 1) if talk.any() else None
    if stems:
        os.makedirs(stems, exist_ok=True)
        shutil.copy(voice, os.path.join(stems, "voice.wav"))
        shutil.copy(music_out, os.path.join(stems, "music_ducked.wav"))
    ml = vc.ebur128(music_out)["I"]
    shutil.rmtree(tmp, ignore_errors=True)
    return {"music_input_I": mI, "music_gain_db": round(g0, 2), "duck_db": duck, "talk_ratio": round(talk_ratio, 2),
            "music_ducked_I": ml, "voice_over_music_db_while_talking": vom}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="voice audio (cut WAV from render_cuts.py --audio-only, or any media)")
    ap.add_argument("-o", "--out", required=True, help="output WAV (48 kHz 24-bit stereo)")
    ap.add_argument("--target", type=float, default=-14.0, help="integrated LUFS (-14 social/YouTube)")
    ap.add_argument("--tp", type=float, default=-1.5, help="true-peak ceiling dBTP (-1.5)")
    ap.add_argument("--denoise", choices=["auto", "rnnoise", "afftdn", "off"], default="auto")
    ap.add_argument("--hum", type=int, choices=[50, 60], help="notch mains hum (50 Hz in RO/EU)")
    ap.add_argument("--deess", type=float, default=0.35, help="de-esser intensity 0-1 (0 = off)")
    ap.add_argument("--no-comp", action="store_true", help="skip compressor/expander (already processed audio)")
    ap.add_argument("--music", help="music bed file (looped/trimmed to length)")
    ap.add_argument("--music-level", type=float, default=-20.0, help="music bed LUFS when nobody talks (-20)")
    ap.add_argument("--duck", type=float, default=12.0, help="music dip under speech, dB (12 -> ~-32 LUFS bed, "
                    "18 dB under a -14 LUFS voice)")
    ap.add_argument("--stems", help="folder for voice.wav + music_ducked.wav stems (DaVinci)")
    ap.add_argument("--json", help="write a report JSON")
    a = ap.parse_args()

    rnn = vc.model_path("rnnoise")
    floor = None
    if a.denoise == "auto":
        db, _ = vc.envelope_db(a.input)
        floor = float(np.percentile(db, 10))
    tmpdir = tempfile.mkdtemp(prefix="ve_am_")
    voice = a.out if not a.music else os.path.join(tmpdir, "voice.wav")
    rep = master_voice(a.input, voice, a.target, a.tp, denoise=a.denoise, rnn=rnn, hum=a.hum, deess=a.deess,
                       comp=not a.no_comp, floor_db=floor)
    rep["noise_floor_db"] = floor
    if a.music:
        rep.update(mix_music(voice, a.music, a.out, a.stems, a.music_level, a.duck, a.target, a.tp))
    elif a.stems:
        os.makedirs(a.stems, exist_ok=True)
        shutil.copy(a.out, os.path.join(a.stems, "voice.wav"))
    shutil.rmtree(tmpdir, ignore_errors=True)
    rep["final"] = vc.ebur128(a.out)
    print(f"denoise={rep['denoise']} (noise floor {floor if floor is None else round(floor, 1)} dB), "
          f"pass0 {rep['pass0_I']:.1f} LUFS, loudnorm {rep['normalization']}")
    if a.music:
        print(f"music: input {rep['music_input_I']:.1f} LUFS, gain {rep['music_gain_db']} dB, duck {rep['duck_db']} dB, "
              f"talking {rep['talk_ratio']:.0%} of the time, ducked bed {rep['music_ducked_I']:.1f} LUFS, voice above "
              f"music while talking {rep['voice_over_music_db_while_talking']} dB")
    F = rep["final"]
    print(f"FINAL {a.out}: {F['I']:.1f} LUFS, LRA {F['LRA']:.1f} LU, true peak {F['TP']:.1f} dBTP")
    if a.json:
        vc.save_json(rep, a.json)


if __name__ == "__main__":
    main()
