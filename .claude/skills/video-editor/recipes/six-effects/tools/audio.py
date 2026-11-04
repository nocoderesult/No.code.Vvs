"""Reel 3 sound: dereverbed voice cut to the timeline, voice chain, SFX on every effect, ducked music, -14 LUFS master.
usage: audio.py reel3_dir   -> work/mix_music.wav, work/mix_nomusic.wav (48 kHz, 24-bit)"""
import json, os, re, subprocess, sys
import numpy as np

R = sys.argv[1]
W = f"{R}/work"
SR = 48000
FPS = 30
tl = json.load(open(f"{W}/timeline.json"))
ev = json.load(open(f"{W}/events.json"))
N = tl["n"] * SR // FPS
SFX_DIR = f"{R}/assets/sfx_dl"
MUSIC = f"{R}/assets/music_dl/175.mp3"           # Mixkit "Digital Clouds"
RNN = "/home/user/No.code.Vvs/.claude/skills/video-editor/assets/models/rnnoise_sh.rnnn"


def ff_read(path, ch=1, extra=()):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, *extra, "-ac", str(ch), "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()


def ff_write(path, x):
    x = np.ascontiguousarray(x, np.float32)
    ch = 1 if x.ndim == 1 else x.shape[1]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", str(ch), "-i", "-",
                    "-c:a", "pcm_f32le", path], input=x.tobytes(), check=True)


def ff_filter(src, dst, af):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", af, "-c:a", "pcm_f32le", dst], check=True)


def lufs(path):
    p = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", p.stderr)[-1])
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", p.stderr)
    return I, (float(tp[-1]) if tp else None)


# ------------------------------------------------------------------ 1. dereverbed voice (multichannel WPE)
wpe = f"{W}/voice_wpe.wav"
if not os.path.exists(wpe):
    from nara_wpe.wpe import wpe as run_wpe
    from nara_wpe.utils import stft, istft
    t0, t1 = 15.0, 73.0
    amb = ff_read(f"{W}/amb4.wav", 4)[int(t0 * SR):int(t1 * SR)]
    st = ff_read(f"{W}/st2.wav", 2)[int(t0 * SR):int(t1 * SR)]
    y = np.concatenate([amb, st], 1).T.astype(np.float64)
    Y = stft(y, size=1024, shift=256).transpose(2, 0, 1)
    Z = run_wpe(Y, taps=10, delay=3, iterations=3, statistics_mode="full")
    z = istft(Z.transpose(1, 2, 0), size=1024, shift=256)[0, :y.shape[1]]
    full = np.zeros(int(80 * SR), np.float32)
    full[int(t0 * SR):int(t0 * SR) + len(z)] = z
    ff_write(wpe, full)
    print("WPE done")
src = ff_read(wpe, 1)[:, 0]

# ------------------------------------------------------------------ 2. cut to the timeline (8 ms fades at every cut)
voice = np.zeros(N, np.float32)
fade = int(0.008 * SR)
ramp_in = np.sin(np.linspace(0, np.pi / 2, fade)) ** 2
pos = 0
for s in tl["segments"]:
    a = int(round(s["src_in"] * SR))
    live = s["live"] * SR // FPS
    seg = src[a:a + live].copy()
    seg[:fade] *= ramp_in
    seg[-fade:] *= ramp_in[::-1]
    if s["id"] == "END":                               # he only smiles here: let the room tone die away
        seg *= np.linspace(1, 0, len(seg)) ** 2
    voice[pos:pos + len(seg)] = seg
    pos += s["n"] * SR // FPS
ff_write(f"{W}/voice_cut.wav", voice)

# ------------------------------------------------------------------ 3. voice chain
chain = ",".join([
    "highpass=f=75:poles=2",
    f"arnndn=m='{RNN}':mix=0.55",
    "equalizer=f=120:t=h:w=1.0:g=1.5",
    "equalizer=f=280:t=q:w=1.0:g=-2.5",
    "equalizer=f=3200:t=q:w=1.3:g=2.5",
    "treble=g=1.5:f=9000:t=s",
    "deesser=i=0.35:m=0.5:f=0.5:s=o",
    "acompressor=threshold=-24dB:ratio=3:attack=6:release=120:knee=4:makeup=4dB",
    "acompressor=threshold=-14dB:ratio=2:attack=3:release=60:knee=2:makeup=1dB",
    "agate=threshold=0.012:ratio=1.6:range=0.4:attack=8:release=220",
])
ff_filter(f"{W}/voice_cut.wav", f"{W}/voice_chain.wav", chain)
Iv, _ = lufs(f"{W}/voice_chain.wav")
voice = ff_read(f"{W}/voice_chain.wav", 1)[:, 0] * 10 ** ((-16.0 - Iv) / 20)
print(f"voice {Iv:.1f} LUFS -> -16")

# ------------------------------------------------------------------ 4. SFX bus
PEAK = {"166": 0.34, "498": 0.08, "1109": 0.07, "1133": 0.19, "1489": 0.72, "1490": 0.73, "1492": 1.08, "2350": 0.45,
        "2356": 0.13, "2364": 0.05, "2568": 0.01, "2573": 0.12, "2574": 0.14, "2870": 0.03, "3005": 0.03, "3120": 0.10,
        "3124": 0.02, "914": 0.49}
_cache = {}


def sfx(name):
    if name not in _cache:
        x = ff_read(f"{SFX_DIR}/{name}.wav", 1)[:, 0]
        _cache[name] = x / (np.abs(x).max() + 1e-9) * 10 ** (-1 / 20)
    return _cache[name]


bus = np.zeros(N + SR * 4, np.float32)
OFF = SR * 2                                            # sounds may start before 0 (pre-laps)
log = []


def place(name, hit, db, rate=1.0):
    x = sfx(name)
    if rate != 1.0:                                     # pitch/speed change by resampling
        idx = np.arange(0, len(x) - 1, rate)
        x = np.interp(idx, np.arange(len(x)), x).astype(np.float32)
    start = int(round((hit - PEAK[name] / rate) * SR)) + OFF
    end = min(start + len(x), len(bus))
    if end > start >= 0:
        bus[start:end] += x[:end - start] * 10 ** (db / 20)
        log.append((round(hit, 2), name, db))


E = ev
o, g, tr, fz, gr, cta = E["ots"], E["graph"], E["tier"], E["freeze"], E["grade"], E["cta"]
# 1 hook: word rises from behind the head
place("498", 0.04, -17); place("166", 0.30, -17)
place("2350", E["behind"][0]["glow"] + 0.10, -24)
place("166", E["behind"][0]["end"] - 0.10, -24)
place("166", E["behind"][1]["start"] + 0.26, -19); place("2568", E["behind"][1]["start"] + 0.33, -17)
for p in E["pills"]:
    if p["start"] is not None:
        place("3005", p["start"] + 0.03, -21)
# 2 over the shoulder
place("1492", o["start"] + 0.27, -14)
for t_card, t_val in ((o["card1"], o["val1"]), (o["card2"], o["val2"])):
    place("2568", t_card + 0.03, -16); place("166", t_card + 0.12, -23); place("3124", t_val + 0.02, -18)
place("2870", o["chip"] + 0.02, -21)
# 3 glass graph
place("2574", g["start"] + 0.02, -18); place("166", g["start"] + 0.10, -22)
place("1109", g["four"] + 0.02, -18)
for i in range(8):
    place("3124", g["count_start"] + i * (g["count_end"] - g["count_start"]) / 8, -24 + i * 0.6, rate=1.0 + 0.05 * i)
place("2870", g["chip"] + 0.02, -18)
# big top words: crisp clicks like the reference
for t_ in E["top"]:
    place("2568", t_["start"] + 0.02, -14)
    if t_.get("sub_start"):
        place("1109", t_["sub_start"] + 0.02, -18)
# 4 tier list
place("3120", tr["start"] + 0.05, -16); place("166", tr["start"] + 0.12, -21)
for d in tr["drops"]:
    land = d["t"] + 0.20
    if d["tier"] == "D":
        place("2364", land, -15)
    else:
        place("2573", land, -16)
    if d["tier"] == "S":
        place("2870", land + 0.05, -20)
for i in range(3):
    place("3124", tr["suspense"] + 0.25 * i, -25)
place("166", tr["end"] - 0.15, -23)
# 5 freeze frame
place("1133", fz["start"], -9); place("1490", fz["start"] + 0.02, -21); place("498", fz["start"] + 0.01, -18)
place("2356", fz["start"] + 0.20, -15); place("3005", fz["start"] + 0.42, -21)
place("166", fz["end"] + 0.05, -23)
# 6 colour grade
place("498", gr["log_start"] + 0.02, -21)
place("2350", (gr["wipe_start"] + gr["wipe_end"]) / 2, -16); place("1490", gr["wipe_start"] + 0.25, -22)
place("3005", gr["wipe_end"] - 0.03, -20)
# end card
place("3120", cta["start"] + 0.05, -18)
for i in range(6):
    place("2356", cta["start"] + (6 + i * 3) / FPS + 0.08, -25)
sfx_bus = bus[OFF:OFF + N]
print(f"{len(log)} sfx placed")

# ------------------------------------------------------------------ 5. music, ducked under the voice
mus = ff_read(MUSIC, 2)
if len(mus) < N:
    mus = np.concatenate([mus, mus])
mus = mus[:N].copy()
ff_write(f"{W}/music_raw.wav", mus)
Im, _ = lufs(f"{W}/music_raw.wav")
hop = SR // 100
env = np.sqrt(np.convolve(voice ** 2, np.ones(hop * 3) / (hop * 3), mode="same"))
act = (20 * np.log10(env + 1e-9) > -42).astype(np.float32)
# attack 60 ms, release 350 ms
duck = np.zeros_like(act)
a_k, r_k = 1 - np.exp(-1 / (0.06 * SR)), 1 - np.exp(-1 / (0.35 * SR))
y_ = 0.0
for i in range(0, N, 32):                               # control rate 1.5 kHz is plenty
    tgt = act[i]
    y_ += (tgt - y_) * (1 - (1 - (a_k if tgt > y_ else r_k)) ** 32)
    duck[i:i + 32] = y_
under = 10 ** ((-16 - 17.0 - Im) / 20)                  # music 17 LU under the voice while he talks
gaps = 10 ** ((-16 - 10.0 - Im) / 20)                   # 10 LU under in pauses
gain = gaps + (under - gaps) * duck
t = np.arange(N) / SR
end_t = cta["start"] - 0.3
gain = np.where(t > end_t, gain * np.clip(1 + (t - end_t) / 0.6 * 0.6, 1, 1.6), gain)    # lift for the end card
gain *= np.clip((tl["duration"] - t) / 1.4, 0, 1) ** 1.5                               # tail fade
gain *= np.clip(t / 0.05, 0, 1)
music = mus * gain[:, None]


# ------------------------------------------------------------------ 6. mix + master (-14 LUFS, true peak <= -1 dBTP)
def master(stereo, out):
    tmp = out.replace(".wav", "_pre.wav")
    ff_write(tmp, stereo)
    I, _ = lufs(tmp)
    lim = "aresample=192000,alimiter=limit=0.8128:attack=1:release=60:level=disabled,aresample=48000"   # -1.8 dBFS @4x
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", f"volume={-14.0 - I:.2f}dB,{lim}",
                    "-c:a", "pcm_s24le", out], check=True)
    I2, tp = lufs(out)
    if abs(I2 + 14) > 0.3:                              # limiter ate some level: one corrective pass
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", f"volume={-14.0 - I + (-14.0 - I2):.2f}dB,{lim}",
                        "-c:a", "pcm_s24le", out], check=True)
        I2, tp = lufs(out)
    os.remove(tmp)
    print(f"{os.path.basename(out)}: {I2:.1f} LUFS, true peak {tp} dBTP")


v2 = np.stack([voice, voice], 1)
s2 = np.stack([sfx_bus, sfx_bus], 1)
master(v2 + s2 + music, f"{W}/mix_music.wav")
master(v2 + s2, f"{W}/mix_nomusic.wav")
json.dump(log, open(f"{W}/sfx_log.json", "w"))
