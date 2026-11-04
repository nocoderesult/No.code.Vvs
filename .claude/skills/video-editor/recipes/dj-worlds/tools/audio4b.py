"""Reel4 v2 sound: the user's song (beat-exact, 5-bar loop from the break), a resonant low-pass that keeps
"reality" muffled and opens through the void into the drop, and a few restrained hits/whooshes on the cuts.
Static gain to -14 LUFS + 4x-oversampled true-peak limiter.  usage: audio4b.py reel4_dir -> work/mix4b.wav"""
import json, os, re, subprocess, sys
import numpy as np
from scipy.signal import istft, stft

R = sys.argv[1]
P = json.load(open(f"{R}/pack/edit_plan.json"))
SR, FPS, N = 48000, P["fps"], P["frames"]
T0 = P["song"]["start_s"]
BEAT_S = P["song"]["beat_frames"] / FPS
SFX = os.environ.get("SFX_DIR", f"{R}/assets/sfx")   # Mixkit ids used below: 498, 784, 2909, 1492, 166, 1489, 1490
DUR = N / FPS
L = int(round(DUR * SR))


def rd(path, ch=2):
    x = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", str(ch), "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True, check=True).stdout
    return np.frombuffer(x, np.float32).reshape(-1, ch).copy()


def lufs(path):
    p = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", p.stderr)[-1]), float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", p.stderr)[-1])


def wr(path, x, codec="pcm_f32le"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", codec, path],
                   input=np.ascontiguousarray(x, np.float32).tobytes(), check=True)


# 1) song: 5 bars from the start of the break (beat 8)
song = rd(f"{R}/src/music_src.mov")
a = int(round(T0 * SR))
mix = song[a:a + L].copy()
assert len(mix) == L, (len(mix), L)

# 2) resonant low-pass: "reality" muffled (beats 8-9), sweeps open through the void (beats 10-11), bypass on the drop
t_void, t_open = 2 * BEAT_S, 4 * BEAT_S - 0.035
f, tt, Z = stft(mix.T, SR, nperseg=2048, noverlap=2048 - 256)
fc = np.where(tt < t_void, 1500.0, 1500.0 * (18000 / 1500.0) ** np.clip((tt - t_void) / (t_open - t_void), 0, 1))
r = f[:, None] / fc[None, :]
Q = 1.25
Hm = 1 / np.sqrt((1 - r ** 2) ** 2 + (r / Q) ** 2)
Hm[:, tt >= t_open] = 1.0
_, y = istft(Z * Hm[None], SR, nperseg=2048, noverlap=2048 - 256)
mix = y.T[:L].astype(np.float32)

# 3) normalise the music bed so SFX levels below are relative to a -14 LUFS song
wr(f"{R}/work/bed.wav", mix)
I0, _ = lufs(f"{R}/work/bed.wav")
mix *= 10 ** ((-14 - I0) / 20)


bed = mix.copy()
sfx = np.zeros_like(mix)


def place(name, hit_s, peak_dbfs, reverse=False, fade_in=0.0):
    x = rd(f"{SFX}/{name}")
    if reverse:
        x = x[::-1].copy()
    env = np.sqrt(np.convolve((x ** 2).mean(1), np.ones(480) / 480, "same"))
    pk = int(np.argmax(env))
    x = x / (np.abs(x).max() + 1e-9) * 10 ** (peak_dbfs / 20)
    if fade_in > 0:
        n = min(int(fade_in * SR), len(x))
        x[:n] *= np.linspace(0, 1, n)[:, None] ** 2
    start = int(round(hit_s * SR)) - pk
    s0, s1 = max(start, 0), min(start + len(x), L)
    if s1 > s0:
        sfx[s0:s1] += x[s0 - start:s1 - start]


drop = 4 * BEAT_S
place("498.wav", 2 * BEAT_S, -16)                      # lights out (beat 10): low heartbeat thump
place("784.wav", drop - 0.02, -19, reverse=True, fade_in=1.2)   # reversed impact swells into the drop
place("2909.wav", drop, -10)                           # the drop
for k in (8, 12):                                       # bars 3 and 4: new world
    place("1492.wav", k * BEAT_S, -22)
place("166.wav", 10 * BEAT_S, -21)                      # handstand jump cut
place("1489.wav", 16 * BEAT_S - 0.05, -23)              # fog whiteout -> ocean
place("1490.wav", 18 * BEAT_S, -23)                     # sunset

# loop-safe edges
n = int(0.006 * SR)
for buf in (bed, sfx):
    buf[:n] *= np.linspace(0, 1, n)[:, None]
    buf[-n:] *= np.linspace(1, 0, n)[:, None]
mix = bed + sfx

# 4) master
tmp = f"{R}/work/mix4b_pre.wav"
wr(tmp, mix)
I, _ = lufs(tmp)
lim = "aresample=192000,alimiter=limit=0.84:attack=1:release=50:level=disabled,aresample=48000"
out = f"{R}/work/mix4b.wav"
g = -14 - I
for _ in range(3):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", f"volume={g:.2f}dB,{lim}", "-c:a", "pcm_s24le", out], check=True)
    I2, tp = lufs(out)
    if abs(I2 + 14) <= 0.2:
        break
    g += -14 - I2
print(f"mix4b.wav: {DUR:.3f}s, {I2:.1f} LUFS, true peak {tp} dBTP, gain {g:+.2f} dB")
# stems for the editable timeline: same static gain as the master, no limiter (bed + sfx ~= mix)
for name, buf in (("stem_song", bed), ("stem_sfx", sfx)):
    wr(f"{R}/work/{name}.wav", buf * 10 ** (g / 20), "pcm_s24le")
print("stems: work/stem_song.wav, work/stem_sfx.wav")
