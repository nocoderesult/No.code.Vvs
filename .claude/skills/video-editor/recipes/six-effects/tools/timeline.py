"""Reel 3 timeline: cut list -> per-output-frame source frame + virtual camera + face box in output space,
plus words and effect events on the output clock. Writes work/timeline.json (shared by Remotion,
the compositor and the audio mix).

Framing rules (9:16 out of the 2160x3840 portrait source):
  * base crop = 67% of the frame (1446x2571 px) -> zoom z shrinks it; never leaves the source.
  * eyes sit at `ey` of the output height (0.30-0.38), face centred horizontally (unless moved).
  * per-segment framing is locked off on the segment's median face (no jittery tracking);
    long takes get a slow push-in; jump cuts alternate size by >= 10% so they read as intent.
"""
import json, math, sys
import numpy as np

R = sys.argv[1]                       # reel3 dir
FPS = 30
SRC_W, SRC_H = 2160, 3840
BASE_SPAN = 0.6695                    # crop span (fraction of width == fraction of height) at z = 1

# id, in, out, framing: z0 -> z1 (linear unless noted), ey, optional dx (face x offset), roll
SEGS = [
    dict(id="A",  i=16.02, o=18.84, z=(1.00, 1.02), ey=0.385),
    dict(id="B",  i=19.60, o=21.08, z=(1.16, 1.17), ey=0.37),
    dict(id="C",  i=21.40, o=24.18, z=(1.00, 1.03), ey=0.385),
    dict(id="D",  i=24.86, o=28.56, ots=True),                       # over-the-shoulder push (custom)
    dict(id="E1", i=28.98, o=32.80, z=(1.00, 1.02), ey=0.33),
    dict(id="E2", i=33.30, o=35.34, z=(1.07, 1.08), ey=0.33),
    dict(id="F1", i=36.36, o=39.86, z=(1.00, 1.04), ey=0.36),
    dict(id="F2", i=40.98, o=41.84, z=(1.10, 1.10), ey=0.30),
    dict(id="G1", i=42.20, o=43.62, z=(1.10, 1.10), ey=0.30),
    dict(id="G2", i=44.02, o=44.86, z=(1.10, 1.10), ey=0.30),
    dict(id="G3", i=45.62, o=46.44, z=(1.10, 1.10), ey=0.30),
    dict(id="G4", i=47.02, o=47.88, z=(1.10, 1.10), ey=0.30),
    dict(id="G5", i=48.40, o=49.84, z=(1.10, 1.10), ey=0.30),
    dict(id="H1", i=50.06, o=52.52, z=(1.10, 1.10), ey=0.30),
    dict(id="H2", i=52.68, o=55.00, z=(1.00, 1.00), ey=0.37, freeze_at=53.467),
    dict(id="I1", i=55.28, o=60.30, z=(1.00, 1.05), ey=0.36),
    dict(id="I2", i=60.56, o=61.16, z=(1.18, 1.19), ey=0.36),
    dict(id="J",  i=61.86, o=64.26, z=(1.12, 1.13), ey=0.36),
    dict(id="K",  i=65.40, o=70.90, z=(1.00, 1.00), ey=0.37, log_until="wipe"),
    dict(id="END", i=70.90, o=71.55, z=(1.00, 1.02), ey=0.37, hold=1.55),   # then hold last frame
]


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def ease_io_cubic(t):
    t = min(max(t, 0.0), 1.0)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


# ---------- face track (normalized source coords), gap-filled and lightly smoothed
track = json.load(open(f"{R}/work/track.json"))
n_src = len(track)
fb = np.full((n_src, 4), np.nan)
for k, e in enumerate(track):
    if e and e.get("face"):
        fb[k] = e["face"]
# reject false detections (a hand, a reflection): far from the running median of the face centre
cx_raw, cy_raw = fb[:, 0] + fb[:, 2] / 2, fb[:, 1] + fb[:, 3] / 2
def _runmed(v, w=15):
    pad = np.pad(v, w // 2, mode="edge")
    return np.array([np.nanmedian(pad[i:i + w]) for i in range(len(v))])
mx, my = _runmed(cx_raw), _runmed(cy_raw)
bad = (np.abs(cx_raw - mx) > 0.05) | (np.abs(cy_raw - my) > 0.04)
fb[bad] = np.nan
print("face outliers rejected:", int(np.nansum(bad)))
for c in range(4):
    v = fb[:, c]
    ok = ~np.isnan(v)
    fb[:, c] = np.interp(np.arange(n_src), np.flatnonzero(ok), v[ok])
ker = np.ones(7) / 7
fbs = np.stack([np.convolve(np.pad(fb[:, c], 3, mode="edge"), ker, mode="valid") for c in range(4)], 1)
# heavy low-pass (gaussian, sigma 0.5 s) used by the "camera operator" to follow leans softly
g = np.exp(-0.5 * (np.arange(-45, 46) / 15.0) ** 2); g /= g.sum()
fbl = np.stack([np.convolve(np.pad(fbs[:, c], 45, mode="edge"), g, mode="valid") for c in range(4)], 1)
FOLLOW_X, FOLLOW_Y = 0.75, 0.5


def face_at(src_frame):
    return fbs[min(max(src_frame, 0), n_src - 1)]


def crop_for(cx_face, ey_face, span, ey, fx=0.5):
    """Crop (u0, v0, span) that puts the eyes at (fx, ey) of the output; clamped inside the source."""
    u0 = cx_face - fx * span
    v0 = ey_face - ey * span
    u0 = min(max(u0, 0.0), 1.0 - span)
    v0 = min(max(v0, 0.0), 1.0 - span)
    return u0, v0


frames = []          # per output frame
segs_out = []
t_out = 0
for s in SEGS:
    fi, fo = round(s["i"] * FPS), round(s["o"] * FPS)
    n = fo - fi
    hold = round(s.get("hold", 0) * FPS)
    src_idx = list(range(fi, fo)) + [fo - 1] * hold
    # segment median face -> locked framing
    med = np.median(fbs[fi:fo], 0)
    fcx = med[0] + med[2] / 2
    fey = med[1] + 0.42 * med[3]                       # eye line inside the YuNet box
    seg_rec = dict(id=s["id"], src_in=fi / FPS, src_out=fo / FPS, out_start=t_out, n=len(src_idx),
                   live=n, face_med=[round(float(x), 4) for x in med])
    freeze_f = round(s["freeze_at"] * FPS) if "freeze_at" in s else None
    for k, sf in enumerate(src_idx):
        u = k / max(len(src_idx) - 1, 1)
        roll = 0.0
        fx = 0.5
        if s.get("ots"):
            # over the shoulder: push 1.00 -> 1.30 in 0.6 s (cubic in-out), face slides to the left third,
            # then a slow drift 1.30 -> 1.37 with a slight roll
            tt = k / FPS
            a = ease_io_cubic(tt / 0.6)
            z = 1.0 + 0.30 * a + 0.07 * max(0.0, (tt - 0.6) / (n / FPS - 0.6))
            fx = 0.5 - 0.135 * a
            ey = 0.38 - 0.02 * a
            roll = -0.9 * a - 0.4 * max(0.0, (tt - 0.6) / (n / FPS - 0.6))
        else:
            z = s["z"][0] + (s["z"][1] - s["z"][0]) * ease(u)
            ey = s["ey"]
        if freeze_f is not None and sf >= freeze_f:
            sf = freeze_f
        span = BASE_SPAN / z
        lp = fbl[min(fi + k, fo - 1)] if freeze_f is None or (fi + k) < freeze_f else fbl[freeze_f]
        cx_t = fcx + FOLLOW_X * ((lp[0] + lp[2] / 2) - fcx)
        ey_t = fey + FOLLOW_Y * ((lp[1] + 0.42 * lp[3]) - fey)
        u0, v0 = crop_for(cx_t, ey_t, span, ey, fx)
        fr = dict(seg=s["id"], src=int(sf), u0=round(u0, 5), v0=round(v0, 5), span=round(span, 5),
                  roll=round(roll, 3), z=round(z, 4))
        if freeze_f is not None and sf == freeze_f and (fi + k) >= freeze_f:
            fr["freeze"] = round(((fi + k) - freeze_f) / FPS, 4)        # seconds since freeze start
        if s.get("log_until"):
            fr["logwipe"] = True
        if hold and k >= n:
            fr["hold"] = round((k - n) / FPS, 4)
        # face box in output (normalized 0..1 of the output frame), ignoring roll
        f = face_at(sf)
        fr["face"] = [round((f[0] - u0) / span, 4), round((f[1] - v0) / span, 4), round(f[2] / span, 4), round(f[3] / span, 4)]
        frames.append(fr)
    segs_out.append(seg_rec)
    t_out += len(src_idx)

# ---------- words on the output clock (onsets/ends snapped to the voice energy)
import subprocess
words = json.load(open(f"{R}/work/words.json"))["words"]
_raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{R}/work/voice_src.wav", "-ac", "1", "-ar", "48000", "-af",
                       "highpass=f=120,lowpass=f=5000", "-f", "f32le", "-"], capture_output=True).stdout
_x = np.frombuffer(_raw, np.float32)
_n = len(_x) // 480
_E = 10 * np.log10((_x[:_n * 480].reshape(_n, 480) ** 2).mean(1) + 1e-12)
_act = _E > -58


def _active_run(i, need=3):
    return i + need <= _n and _act[i:i + need].all()


for w in words:
    i0, i1 = int(w["s"] * 100), int(w["e"] * 100)
    if not _act[min(i0, _n - 1)]:
        j = next((j for j in range(i0, min(i0 + 150, _n - 3)) if _active_run(j)), None)
        if j is not None and j / 100 < w["e"] + 1.2:
            w["s"] = round(j / 100 - 0.02, 3)
            w["e"] = max(w["e"], w["s"] + 0.12)
    i0, i1 = int(w["s"] * 100), int(w["e"] * 100)
    if not _act[min(i1, _n - 1)]:
        j = next((j for j in range(i1, i0, -1) if _act[j]), None)
        if j is not None:
            w["e"] = round(max(j / 100 + 0.03, w["s"] + 0.1), 3)
out_words = []
_lin = 10 ** (_E / 10)
for w in words:
    # the word belongs to the segment holding most of its voice energy (cut-points split some words' boxes)
    best, best_m = None, 0.0
    for seg in segs_out:
        a, b = max(w["s"], seg["src_in"]), min(w["e"], seg["src_out"])
        if b - a > 0.03:
            m = _lin[int(a * 100):int(b * 100) + 1].sum()
            if m > best_m:
                best, best_m = seg, m
    if best is None:
        continue
    a, b = best["src_in"], best["src_out"]
    s0 = best["out_start"] / FPS + (max(w["s"], a) - a)
    e0 = best["out_start"] / FPS + (min(w["e"], b) - a)
    out_words.append(dict(w=w["w"], s=round(s0, 3), e=round(max(e0, s0 + 0.1), 3), seg=best["id"]))
out_words.sort(key=lambda d: d["s"])

total = len(frames)
json.dump(dict(fps=FPS, n=total, duration=round(total / FPS, 3), segments=segs_out, frames=frames, words=out_words),
          open(f"{R}/work/timeline.json", "w"), ensure_ascii=False)
print(f"{total} frames = {total / FPS:.2f} s")
for s in segs_out:
    print(f"  {s['id']:4} out {s['out_start'] / FPS:6.2f}s  src {s['src_in']:6.2f}-{s['src_out']:6.2f}  n={s['n']}")
print(" ".join(f"{w['w']}@{w['s']:.2f}" for w in out_words))
