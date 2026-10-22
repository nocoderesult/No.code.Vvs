"""Synthesize punchy SFX (no licences needed) and lay them on a timeline.

usage: sfx.py events.json duration out.wav
events: [{"t": 1.367, "kind": "impact", "db": 0}, ...]  (t = start; for riser/swell, t = the hit time it builds into)
"""
import json, sys
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def env_exp(n, tau):
    t = np.arange(n) / SR
    return np.exp(-t / tau)


def lowpass(x, fc):
    # one-pole, applied forward+backward (zero phase)
    a = np.exp(-2 * np.pi * fc / SR)
    def run(v):
        y = np.empty_like(v); acc = 0.0
        for i, s in enumerate(v):
            acc = (1 - a) * s + a * acc; y[i] = acc
        return y
    return run(run(x)[::-1])[::-1]


def band_sweep(noise, f_of_t, q=0.35):
    """Time-varying band-pass via STFT masking (centre frequency follows f_of_t)."""
    n = len(noise); hop = 256; win = 1024
    w = np.hanning(win)
    out = np.zeros(n + win)
    freqs = np.fft.rfftfreq(win, 1 / SR)
    for start in range(0, n, hop):
        seg = np.zeros(win); chunk = noise[start:start + win]; seg[:len(chunk)] = chunk
        spec = np.fft.rfft(seg * w)
        fc = f_of_t((start + win / 2) / SR)
        bw = fc * q * 2
        mask = np.exp(-0.5 * ((freqs - fc) / bw) ** 2)
        out[start:start + win] += np.fft.irfft(spec * mask) * w
    return out[:n] / 1.5


def norm(x, peak=0.98):
    m = np.max(np.abs(x)) or 1.0
    return x / m * peak


def impact(big=True):
    dur = 1.6 if big else 1.1
    n = int(dur * SR); t = np.arange(n) / SR
    f = 30 + 110 * np.exp(-t / 0.07)                 # pitch drop 140 -> 30 Hz
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.45 if big else 0.3)
    body = lowpass(rng.standard_normal(n), 1800) * env_exp(n, 0.09) * 2.5
    click = rng.standard_normal(n) * env_exp(n, 0.004) * 0.8
    tail = lowpass(rng.standard_normal(n), 600) * env_exp(n, 0.5) * 0.25
    x = np.tanh(1.8 * (sub * 1.0 + body * 0.5 + click + tail))
    x[:48] *= np.linspace(0, 1, 48)
    return norm(x)


def whoosh(dur=0.45, f0=250, f1=3500, f2=700):
    n = int(dur * SR); t = np.arange(n) / SR
    peak = 0.6
    def fc(tt):
        p = tt / dur
        return f0 * (f1 / f0) ** (p / peak) if p < peak else f1 * (f2 / f1) ** ((p - peak) / (1 - peak))
    x = band_sweep(rng.standard_normal(n), fc)
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    e = np.where(t / dur < peak, (t / (dur * peak)) ** 2, np.exp(-(t - dur * peak) / (dur * 0.18)))
    return norm(x * e)


def riser(dur=0.55):
    n = int(dur * SR); t = np.arange(n) / SR; p = t / dur
    f = 180 * (2200 / 180) ** p
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.15
    nz = band_sweep(rng.standard_normal(n), lambda tt: 400 * (6000 / 400) ** (tt / dur), q=0.5)
    x = (tone + nz * 0.9) * p ** 2.2
    return norm(x)


def swell(dur=0.35):
    # reversed noise burst with decay = "reverse cymbal" swell into a hit
    n = int(dur * SR)
    x = lowpass(rng.standard_normal(n), 5000) * env_exp(n, dur * 0.35)
    return norm(x[::-1])


def pop(f_hi=1300, f_lo=380, dur=0.09):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f_lo + (f_hi - f_lo) * np.exp(-t / 0.012)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.025)
    x[:24] *= np.linspace(0, 1, 24)
    return norm(x)


def ding(f=1568, dur=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * k * t) * env_exp(n, d)
            for k, a, d in [(1, 1, 0.45), (2.0, 0.35, 0.25), (3.01, 0.2, 0.15), (4.2, 0.1, 0.08)])
    x[:96] *= np.linspace(0, 1, 96)
    return norm(x)


def shutter():
    n = int(0.12 * SR)
    x = np.zeros(n)
    for off in (0, int(0.045 * SR)):
        b = lowpass(rng.standard_normal(int(0.02 * SR)), 4000) * env_exp(int(0.02 * SR), 0.004)
        x[off:off + len(b)] += b
    return norm(x)


KINDS = {"impact": lambda: impact(True), "impact_small": lambda: impact(False), "whoosh": whoosh,
         "riser": riser, "swell": swell, "pop": pop, "pop_hi": lambda: pop(1900, 600, 0.07),
         "ding": ding, "shutter": shutter}
LEADS = {"riser": True, "swell": True}   # these end exactly at t


def main():
    events = json.load(open(sys.argv[1])); dur = float(sys.argv[2]); out = sys.argv[3]
    n = int(round(dur * SR))
    L = np.zeros(n); R = np.zeros(n)
    for ev in events:
        x = KINDS[ev["kind"]]() * 10 ** (ev.get("db", 0) / 20)
        start = int(round(ev["t"] * SR)) - (len(x) if ev["kind"] in LEADS else 0)
        pan = ev.get("pan", 0.0)
        if ev["kind"] == "whoosh" and "pan" not in ev:      # sweep left -> right
            p = np.linspace(-0.7, 0.7, len(x)); gl = np.sqrt((1 - p) / 2); gr = np.sqrt((1 + p) / 2)
        else:
            gl = np.sqrt((1 - pan) / 2) * np.sqrt(2); gr = np.sqrt((1 + pan) / 2) * np.sqrt(2)
            gl = min(gl, 1.0); gr = min(gr, 1.0)
        s0 = max(start, 0); x = x[s0 - start:]; e = min(n, s0 + len(x))
        if isinstance(gl, np.ndarray):
            gl = gl[s0 - start:][:e - s0]; gr = gr[s0 - start:][:e - s0]
        L[s0:e] += x[:e - s0] * gl; R[s0:e] += x[:e - s0] * gr
    st = (np.stack([L, R], 1) * 0.5).astype(np.float32)   # -6 dB headroom; the mix adds it back
    import wave
    pcm = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open(out, "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())
    print(f"wrote {out}: {len(events)} events, peak {20*np.log10(np.max(np.abs(st))+1e-9):.1f} dBFS")


if __name__ == "__main__":
    main()
