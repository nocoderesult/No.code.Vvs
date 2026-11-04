#!/usr/bin/env python3
"""Master a voice track (after cutting) and optionally lay a ducked music bed under it.

Voice chain: highpass 80 Hz -> (mains hum notch) -> RNNoise denoise (bundled model; afftdn fallback) ->
de-mud EQ -2 dB @250 Hz -> presence +2 dB @3.5 kHz -> de-esser -> compressor 3:1 -> gentle expander.
Latency: the chain delays the voice (measured RNNoise +12 ms, afftdn +27 ms, EQ/HPF alone +2 ms), which would
put the sound behind the picture and the stems behind A1 in Resolve; it is measured by cross-correlating the
chain output with the input and trimmed off (output keeps the input's exact length).
Leveling: if the chained voice has LRA > 10 LU (quiet and loud passages, e.g. near/far from the phone), an
offline gain rider brings 3 s loudness toward the median (+-12 dB, smoothed, held through pauses).
Loudness: pass 0 measures after the chain and pre-gains + limits so loudnorm can stay LINEAR, then classic
two-pass loudnorm. If linear mode is still impossible (LRA or true peak out of range), a static gain + 4x
oversampled true-peak limiter is used instead of loudnorm's dynamic mode (which rode quiet passages unevenly).
Music: looped/trimmed, faded (or cut on the last frame with --music-end cut, for loops), set so that while the
voice talks the bed sits --music-under dB below it (default 15; --music-level sets the un-ducked bed level
instead), then ducked by --duck dB with an offline gain curve computed from the voice (look-ahead 80 ms,
attack 80 ms, release 450 ms, gaps < 0.35 s held so it never pumps between words); mixed with amix
normalize=0, true-peak limited (4x oversampled). Default target: -14 LUFS integrated, -1.5 dBTP.
Sound effects (--sfx events.json, [{"t": 0.05, "kind": "pop"|"whoosh"}]): synthesized (no licence issues),
about 20 dB under the voice.

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


def read_f32(path, sr=48000, ch=2):
    raw = vc.run_bytes(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-map", "0:a:0", "-af",
                        "aresample=async=1:first_pts=0", "-ac", str(ch), "-ar", str(sr), "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()


def write_f32(x, path, sr=48000, codec="pcm_f32le"):
    p = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", str(x.shape[1]),
                        "-i", "-", "-c:a", codec, path], input=np.ascontiguousarray(x, np.float32).tobytes(),
                       capture_output=True)
    if p.returncode:
        raise vc.EditError(p.stderr.decode()[-500:])


def chain_lag(ref, out, sr=48000, max_ms=80):
    """Delay of `out` relative to `ref` in samples (cross-correlation of the first 60 s, mono)."""
    a, b = ref.mean(1), out.mean(1)
    n = min(len(a), len(b), sr * 60)
    a, b = a[:n] - a[:n].mean(), b[:n] - b[:n].mean()
    if n < sr // 10 or not a.any() or not b.any():
        return 0
    N = 1 << int(np.ceil(np.log2(2 * n)))
    c = np.fft.irfft(np.fft.rfft(b, N) * np.conj(np.fft.rfft(a, N)), N)
    m = int(sr * max_ms / 1000)
    cc = np.concatenate([c[-m:], c[: m + 1]])
    return int(np.argmax(cc)) - m


def level_rider(x, sr=48000, max_db=12.0, hop=0.1, win=3.0, sigma=0.75):
    """Offline slow leveler: 3 s loudness of the speech-active parts pulled toward their median (+-max_db),
    gain held through pauses and smoothed (no pumping). Returns (y, applied dB range)."""
    mono = x.mean(1).astype(np.float64)
    h, w = int(sr * hop), int(sr * 0.4)
    n = max(1, (len(mono) - w) // h + 1)
    p = np.array([np.mean(mono[i * h: i * h + w] ** 2) for i in range(n)]) + 1e-12
    db = 10 * np.log10(p)
    act = db > max(-70.0, 10 * np.log10(np.mean(p[db > -70])) - 20 if (db > -70).any() else -70)
    if act.sum() < 5:
        return x, (0.0, 0.0)
    k = int(win / hop / 2)
    L = np.full(n, np.nan)
    for i in np.where(act)[0]:
        sl = slice(max(0, i - k), i + k + 1)
        L[i] = 10 * np.log10(np.mean(p[sl][act[sl]]))
    target = float(np.median(L[act]))
    g = np.clip(target - L, -max_db, max_db)
    idx = np.where(act)[0]
    g = np.interp(np.arange(n), idx, g[idx])          # hold through pauses
    sg = max(1, int(sigma / hop))
    kern = np.exp(-0.5 * (np.arange(-3 * sg, 3 * sg + 1) / sg) ** 2)
    g = np.convolve(np.pad(g, 3 * sg, mode="edge"), kern / kern.sum(), mode="valid")
    t = (np.arange(n) * h + w / 2) / sr
    gs = 10 ** (np.interp(np.arange(len(mono)) / sr, t, g) / 20)
    return (x * gs[:, None]).astype(np.float32), (round(float(g.min()), 1), round(float(g.max()), 1))


def tp_limit(I, TP):
    return f"aresample=192000,alimiter=limit={10 ** ((TP - 0.3) / 20):.4f}:attack=1:release=50:level=false,aresample=48000"


def master_voice(src, out, I=-14.0, TP=-1.5, LRA=11.0, **chain_kw):
    pre, used = chain(**chain_kw)
    tmp = tempfile.mkdtemp(prefix="ve_voice_")
    rep = {"denoise": used, "chain": pre}
    # 1 chain -> float WAV, then remove the chain's latency (RNNoise/afftdn/IIR group delay)
    ch_wav = os.path.join(tmp, "chain.wav")
    vc.run(vc.ffmpeg_cmd("-i", src, "-map", "0:a:0", "-af", f"aresample=48000:async=1:first_pts=0,{pre},"
                         "aformat=channel_layouts=stereo", "-ar", "48000", "-c:a", "pcm_f32le", ch_wav))
    x_in = read_f32(src)
    y = read_f32(ch_wav)
    lag = chain_lag(x_in, y)
    rep["latency_ms"] = round(1000 * lag / 48000, 2)
    if lag > 0:
        y = np.concatenate([y[lag:], np.zeros((lag, 2), np.float32)])
    elif lag < 0:
        y = np.concatenate([np.zeros((-lag, 2), np.float32), y[:lag]])
    y = y[: len(x_in)] if len(y) >= len(x_in) else np.concatenate([y, np.zeros((len(x_in) - len(y), 2), np.float32)])
    # 2 slow leveler when the voice swings a lot (loudnorm would otherwise go dynamic and ride it unevenly)
    write_f32(y, ch_wav)
    L0 = vc.ebur128(ch_wav)
    rep["chain_LRA"] = L0["LRA"]
    if L0["LRA"] > LRA - 1:
        y, rng = level_rider(y)
        write_f32(y, ch_wav)
        rep["leveler_db"] = rng
        rep["leveled_LRA"] = vc.ebur128(ch_wav)["LRA"]
    # 3 pass 0 pre-gain + limiter, then two-pass loudnorm (linear) or static gain + true-peak limiter
    i0 = measure_I(ch_wav, "anull")
    if i0 < -60:
        raise vc.EditError(f"voice is silent or nearly silent ({i0} LUFS)")
    lim = 10 ** ((TP - 0.5) / 20)
    pre0 = f"volume={I - i0:.2f}dB,alimiter=limit={lim:.4f}:attack=2:release=60:level=false"
    p1 = vc.run(["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-i", ch_wav, "-af",
                 f"{pre0},loudnorm=I={I}:TP={TP}:LRA={LRA}:print_format=json", "-f", "null", "-"], capture=True)
    m = loudnorm_json(p1.stderr)
    # the same test ffmpeg's loudnorm applies before it silently switches to dynamic mode
    linear_ok = float(m["input_lra"]) <= LRA and float(m["input_tp"]) + I - float(m["input_i"]) <= TP
    if linear_ok:
        ln = (f"loudnorm=I={I}:TP={TP}:LRA={LRA}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:"
              f"linear=true:print_format=json")
        p2 = vc.run(["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-y", "-i", ch_wav, "-af",
                     f"{pre0},{ln},aresample=48000,aformat=channel_layouts=stereo", "-ar", "48000", "-c:a",
                     "pcm_s24le", out], capture=True)
        norm = loudnorm_json(p2.stderr).get("normalization_type")
    else:
        norm = "dynamic"
    if norm != "linear":
        # never let loudnorm ride the gain: static gain to the target, then an oversampled true-peak limiter
        gain = I - float(m["input_i"])
        vc.run(vc.ffmpeg_cmd("-i", ch_wav, "-af", f"{pre0},volume={gain:.2f}dB,{tp_limit(I, TP)},"
                             "aformat=channel_layouts=stereo", "-ar", "48000", "-c:a", "pcm_s24le", out))
        L = vc.ebur128(out)
        if abs(L["I"] - I) > 0.3:   # the limiter ate some loudness: one correction pass
            fixed = out + ".tmp.wav"
            vc.run(vc.ffmpeg_cmd("-i", out, "-af", f"volume={I - L['I']:.2f}dB,{tp_limit(I, TP)}", "-ar", "48000",
                                 "-c:a", "pcm_s24le", fixed))
            os.replace(fixed, out)
        norm = "static gain + true-peak limiter (loudnorm could not stay linear)"
    # the limiters' look-ahead delays the voice too (~2 ms): re-measure against the input and trim the residue
    z = read_f32(out)
    lag2 = chain_lag(x_in, z)
    if abs(lag2) >= 12:   # >= 0.25 ms
        z = np.concatenate([z[lag2:], np.zeros((lag2, 2), np.float32)]) if lag2 > 0 else \
            np.concatenate([np.zeros((-lag2, 2), np.float32), z[:lag2]])
        write_f32(z, out, codec="pcm_s24le")
    rep["latency_ms"] = round(rep["latency_ms"] + 1000 * lag2 / 48000, 2)
    shutil.rmtree(tmp, ignore_errors=True)
    rep.update({"pass0_I": i0, "normalization": norm})
    return rep


def synth_sfx(kind, sr=48000):
    """Small synthesized sound effects (no licence issues): 'pop' (text appears), 'whoosh' (transition)."""
    rng = np.random.default_rng(7)
    if kind == "whoosh":
        n = int(0.45 * sr)
        t = np.arange(n) / sr
        noise = rng.standard_normal(n)
        env = np.sin(np.pi * t / t[-1]) ** 2
        # sweep a one-pole low-pass from dark to bright and back (moving air)
        fc = 400 + 3600 * env
        a = np.exp(-2 * np.pi * fc / sr)
        y = np.empty(n)
        acc = 0.0
        for i in range(n):
            acc = (1 - a[i]) * noise[i] + a[i] * acc
            y[i] = acc
        y *= env
    else:
        n = int(0.09 * sr)
        t = np.arange(n) / sr
        y = np.sin(2 * np.pi * (520 + 900 * np.exp(-t / 0.012)) * t) * np.exp(-t / 0.025)
    y = y / (np.sqrt(np.mean(y ** 2)) + 1e-9)
    return np.stack([y, y], 1).astype(np.float32)


def add_sfx(path, events, rel_db=-20.0, I=-14.0, TP=-1.5):
    """Mix synthesized effects into `path` in place, RMS about `rel_db` under the voice's integrated level."""
    x = read_f32(path)
    lvl = 10 ** ((I + rel_db + 3) / 20)   # RMS of a short burst sits ~3 dB under its momentary loudness
    for e in events:
        fx = synth_sfx(e.get("kind", "pop")) * lvl
        i = int(float(e["t"]) * 48000)
        if 0 <= i < len(x):
            j = min(len(x), i + len(fx))
            x[i:j] += fx[: j - i]
    tmp = path + ".sfx.wav"
    write_f32(x, tmp)
    vc.run(vc.ffmpeg_cmd("-i", tmp, "-af", tp_limit(I, TP), "-ar", "48000", "-c:a", "pcm_s24le", path))
    os.unlink(tmp)
    return len(events)


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


def mix_music(voice, music, out, stems=None, music_level=None, duck=8.0, I=-14.0, TP=-1.5,
              fade_in=0.4, fade_out=1.5, under=15.0):
    dur = vc.media_info(voice)["duration"]
    tmp = tempfile.mkdtemp(prefix="ve_mix_")
    m_fit = os.path.join(tmp, "music_fit.wav")
    # loop/trim the music to the voice length, fade in/out (fade_out 0.08 = 'button' ending for loops)
    vc.run(vc.ffmpeg_cmd("-stream_loop", "-1", "-i", music, "-t", f"{dur:.3f}", "-af",
                         f"aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d={fade_in},"
                         f"afade=t=out:st={max(0, dur - fade_out):.3f}:d={fade_out}",
                         "-c:a", "pcm_s24le", m_fit))
    mI = vc.ebur128(m_fit)["I"]
    if mI == float("-inf") or mI < -70:
        raise vc.EditError("music track is silent")
    if music_level is None:   # bed level in pauses so that, ducked under speech, it sits `under` dB below the voice
        music_level = I - under + duck
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
    lim = tp_limit(I, TP)
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
    vI = vc.ebur128(voice)["I"]
    shutil.rmtree(tmp, ignore_errors=True)
    return {"music_input_I": mI, "music_level": round(music_level, 1), "music_gain_db": round(g0, 2), "duck_db": duck,
            "talk_ratio": round(talk_ratio, 2), "music_ducked_I": ml, "voice_I": vI,
            "voice_over_music_LU": round(vI - ml, 1), "voice_over_music_db_while_talking": vom}


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
    ap.add_argument("--music-under", type=float, default=15.0,
                    help="dB the ducked bed sits under the voice while talking (15 -> audible on a phone speaker)")
    ap.add_argument("--music-level", type=float, help="override: music bed LUFS when nobody talks "
                    "(default = target - music-under + duck, i.e. -21 LUFS)")
    ap.add_argument("--duck", type=float, default=8.0, help="music dip under speech, dB (8)")
    ap.add_argument("--music-end", choices=["fade", "cut"], default="fade",
                    help="fade = 1.5 s fade-out; cut = stops on the last frame (80 ms), for videos that loop")
    ap.add_argument("--sfx", help="events.json [{\"t\": s, \"kind\": \"pop\"|\"whoosh\"}] mixed ~20 dB under the voice")
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
        rep.update(mix_music(voice, a.music, a.out, a.stems, a.music_level, a.duck, a.target, a.tp,
                             fade_out=1.5 if a.music_end == "fade" else 0.08, under=a.music_under))
    elif a.stems:
        os.makedirs(a.stems, exist_ok=True)
        shutil.copy(a.out, os.path.join(a.stems, "voice.wav"))
    if a.sfx:
        ev = vc.load_json(a.sfx)
        rep["sfx"] = add_sfx(a.out, ev, I=a.target, TP=a.tp)
        if a.stems:
            sx = np.zeros_like(read_f32(a.out))
            lvl = 10 ** ((a.target - 20 + 3) / 20)
            for e in ev:
                fx = synth_sfx(e.get("kind", "pop")) * lvl
                i = int(float(e["t"]) * 48000)
                if 0 <= i < len(sx):
                    j = min(len(sx), i + len(fx))
                    sx[i:j] += fx[: j - i]
            write_f32(sx, os.path.join(a.stems, "sfx.wav"), codec="pcm_s24le")
    shutil.rmtree(tmpdir, ignore_errors=True)
    rep["final"] = vc.ebur128(a.out)
    print(f"denoise={rep['denoise']} (noise floor {floor if floor is None else round(floor, 1)} dB), chain latency "
          f"{rep['latency_ms']:+.1f} ms removed, LRA {rep['chain_LRA']:.1f}"
          + (f" -> leveler {rep['leveler_db'][0]:+.0f}..{rep['leveler_db'][1]:+.0f} dB -> LRA {rep['leveled_LRA']:.1f}"
             if "leveler_db" in rep else "")
          + f", pass0 {rep['pass0_I']:.1f} LUFS, normalization: {rep['normalization']}")
    if a.music:
        print(f"music: input {rep['music_input_I']:.1f} LUFS, gain {rep['music_gain_db']} dB, duck {rep['duck_db']} dB, "
              f"talking {rep['talk_ratio']:.0%} of the time, ducked bed {rep['music_ducked_I']:.1f} LUFS = "
              f"{rep['voice_over_music_LU']} LU under the voice (target {a.music_under:.0f}; unweighted RMS while "
              f"talking {rep['voice_over_music_db_while_talking']} dB)")
    if rep.get("sfx"):
        print(f"sfx: {rep['sfx']} effect(s) mixed ~20 dB under the voice")
    F = rep["final"]
    print(f"FINAL {a.out}: {F['I']:.1f} LUFS, LRA {F['LRA']:.1f} LU, true peak {F['TP']:.1f} dBTP")
    if a.json:
        vc.save_json(rep, a.json)


if __name__ == "__main__":
    main()
