#!/usr/bin/env python3
"""Generate synthetic test footage with REAL Romanian speech (Piper TTS) for self-testing the skill.

Creates in OUTDIR:
  speech_a.wav      Romanian talk: greeting, filler phrase "Ăăă, deci, practic.", a retake, long pauses
  talk_16x9.mp4     1920x1080 30 fps talking head (public-domain NASA portrait moving left/right) + speech_a
                    with room noise (-48 dB) -> tests face-tracked 9:16 crop, cuts, captions, mastering
  phone_vfr_rot.mp4 vertical phone-style clip: stored 1920x1080 + rotation 90, VFR, mono 44.1 kHz, full range
  hdr_hlg.mov       5 s HLG (arib-std-b67, bt2020, 10-bit HEVC) clip -> tests HDR->SDR tone mapping
  music.wav         30 s 120 BPM instrumental bed (kick + chords) -> tests ducking
  broll.mp4         4 s moving test pattern; still.png -> tests b-roll / Ken Burns

Needs: pip install --break-system-packages piper-tts ; downloads the ro_RO-mihai-medium voice (63 MB) to
~/.cache/video-editor/voices (curl with resume: python downloads were seen truncated -> ONNX parse error).
Usage: make_test_media.py OUTDIR [--face face.png]
"""
import argparse
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import vcommon as vc  # noqa: E402

VOICE = "https://huggingface.co/rhasspy/piper-voices/resolve/main/ro/ro_RO/mihai/medium/ro_RO-mihai-medium.onnx"
FACE = "https://gitlab.com/scikit-image/data/-/raw/master/astronaut.png"  # NASA portrait, public domain

SENTS_A = [
    ("Salut tuturor! Astăzi vă arăt cum să editați un videoclip în mai puțin de cinci minute.", 0.4),
    ("Ăăă, deci, practic.", 1.6),
    ("Primul pas este să tăiați pauzele și cuvintele de umplutură.", 0.3),
    ("Al doilea pas este să puneți subtitrări care se văd bine pe telefon.", 0.9),
    ("Al doilea pas este să adăugați subtitrări mari, cu diacritice corecte: ă, â, î, ș, ț.", 2.2),
    ("Și ultimul pas, foarte important, este sunetul. Nimeni nu se uită la un video cu sunet prost.", 0.5),
    ("Dacă v-a plăcut, lăsați un comentariu și urmăriți pagina pentru mai multe sfaturi.", 0.8),
]
SENTS_B = [
    ("Bună! Asta e o filmare verticală de pe telefon.", 0.7),
    ("Îîî, stai puțin.", 1.2),
    ("Lumina de la fereastră face toată diferența la o filmare.", 0.6),
]


def sh(cmd):
    subprocess.run(cmd, check=True)


def get_voice():
    d = os.path.join(vc.CACHE, "voices")
    os.makedirs(d, exist_ok=True)
    onnx = os.path.join(d, "ro_RO-mihai-medium.onnx")
    if not os.path.exists(onnx + ".json"):
        sh(["curl", "-sSL", "--retry", "3", "-o", onnx + ".json", VOICE + ".json"])
    for _ in range(4):
        if os.path.exists(onnx) and os.path.getsize(onnx) > 63_000_000:
            return onnx
        subprocess.run(["curl", "-sSL", "--retry", "3", "-C", "-", "-o", onnx, VOICE])
    raise SystemExit("voice download incomplete")


def tts(voice, sents, out, lead=0.6):
    from piper import PiperVoice
    v = PiperVoice.load(voice)
    sr = v.config.sample_rate
    parts = [np.zeros(int(sr * lead), np.int16)]
    for s, gap in sents:
        for ch in v.synthesize(s):
            parts.append(ch.audio_int16_array)
        parts.append(np.zeros(int(sr * gap), np.int16))
    a = np.concatenate(parts)
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(a.tobytes())
    return len(a) / sr


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("outdir")
    ap.add_argument("--face", help="portrait image (default: download public-domain NASA portrait)")
    a = ap.parse_args()
    o = os.path.abspath(a.outdir)
    os.makedirs(o, exist_ok=True)
    voice = get_voice()
    da = tts(voice, SENTS_A, f"{o}/speech_a.wav")
    db = tts(voice, SENTS_B, f"{o}/speech_b.wav")
    face = a.face or f"{o}/face.png"
    if not os.path.exists(face):
        sh(["curl", "-sSL", "--retry", "3", "-o", face, FACE])
    # 16:9 talking head: blurred warm background + portrait sliding slowly left/right (period 12 s)
    sh(vc.ffmpeg_cmd(
        "-f", "lavfi", "-i", f"gradients=s=1920x1080:c0=0x3a2a20:c1=0x8a6a50:x0=0:y0=0:x1=1920:y1=1080:d={da}:r=30",
        "-loop", "1", "-framerate", "30", "-t", f"{da}", "-i", face,
        "-i", f"{o}/speech_a.wav",
        "-f", "lavfi", "-t", f"{da}", "-i", "anoisesrc=c=pink:a=0.004:r=48000",
        "-filter_complex",
        "[1:v]scale=760:760,setsar=1[f];[0:v][f]overlay=x='580+260*sin(2*PI*t/12)':y=180:shortest=1,"
        "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='%{pts\\:hms}':x=20:y=20:"
        "fontsize=28:fontcolor=white@0.6,format=yuv420p[v];"
        "[2:a]aresample=48000,pan=stereo|c0=c0|c1=c0[s];[3:a]pan=stereo|c0=c0|c1=c0[n];"
        "[s][n]amix=inputs=2:normalize=0:duration=first,volume=-6dB[a]",
        "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-g", "60",
        "-c:a", "aac", "-b:a", "192k", "-t", f"{da}", f"{o}/talk_16x9.mp4"))
    # phone-style vertical: rendered upright 1080x1920, then STORED rotated (1920x1080 + display matrix 90),
    # VFR timestamps, mono 44.1 kHz audio, full-range yuvj420p
    sh(vc.ffmpeg_cmd(
        "-f", "lavfi", "-i", f"gradients=s=1080x1920:c0=0x203040:c1=0x608090:d={db}:r=30",
        "-loop", "1", "-framerate", "30", "-t", f"{db}", "-i", face, "-i", f"{o}/speech_b.wav",
        "-filter_complex", "[1:v]scale=900:900[f];[0:v][f]overlay=x=90:y=420:shortest=1,transpose=1,format=yuvj420p[v]",
        "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-ar", "44100", "-ac", "1", "-t", f"{db}", f"{o}/_upright_rot.mp4"))
    # VFR: drop frames irregularly, keep timestamps (passthrough)
    sh(vc.ffmpeg_cmd("-i", f"{o}/_upright_rot.mp4", "-vf", "select='not(eq(mod(n,7),3))*not(eq(mod(n,11),5))'",
                     "-fps_mode", "passthrough", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                     "-pix_fmt", "yuvj420p", "-color_range", "pc", "-c:a", "copy", f"{o}/_vfr.mp4"))
    sh(vc.ffmpeg_cmd("-display_rotation", "90", "-i", f"{o}/_vfr.mp4", "-c", "copy", f"{o}/phone_vfr_rot.mp4"))
    for f in ("_upright_rot.mp4", "_vfr.mp4"):
        os.unlink(f"{o}/{f}")
    # HLG HDR 10-bit HEVC (5 s from the talking head)
    sh(vc.ffmpeg_cmd("-i", f"{o}/talk_16x9.mp4", "-t", "5", "-vf",
                     "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv,zscale=t=linear:npl=203,format=gbrpf32le,"
                     "zscale=p=bt2020:t=arib-std-b67:m=bt2020nc:r=tv:npl=203,format=yuv420p10le",
                     "-c:v", "libx265", "-preset", "ultrafast", "-crf", "22", "-x265-params",
                     "colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:log-level=error",
                     "-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc",
                     "-tag:v", "hvc1", "-c:a", "copy", f"{o}/hdr_hlg.mov"))
    # music bed: 120 BPM kick + soft minor chords, 30 s
    kick = "0.9*sin(2*PI*(50+80*exp(-40*mod(t,0.5)))*t)*exp(-9*mod(t,0.5))"
    chords = ("0.12*(sin(2*PI*220*t)+sin(2*PI*261.63*t)+sin(2*PI*329.63*t))*(1-0.3*gt(mod(t,4),2))"
              "+0.05*sin(2*PI*110*t)")
    hat = "0.05*(random(0)-0.5)*exp(-60*mod(t+0.25,0.5))"
    sh(vc.ffmpeg_cmd("-f", "lavfi", "-i", f"aevalsrc='{kick}+{chords}+{hat}|{kick}+{chords}+{hat}':s=48000:d=30",
                     "-af", "lowpass=f=9000,volume=-6dB", "-c:a", "pcm_s16le", f"{o}/music.wav"))
    sh(vc.ffmpeg_cmd("-f", "lavfi", "-i", "testsrc2=s=1280x720:r=30:d=4", "-c:v", "libx264", "-preset", "veryfast",
                     f"{o}/broll.mp4"))
    sh(vc.ffmpeg_cmd("-f", "lavfi", "-i", "mandelbrot=s=1600x1200:end_pts=1", "-frames:v", "1", f"{o}/still.png"))
    print(f"speech_a {da:.1f}s, speech_b {db:.1f}s; files in {o}")


if __name__ == "__main__":
    main()
