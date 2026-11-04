"""Reel4 v2 compositor: graded base plates + void matte + punch/pulse transforms + bloom reveals + halation, vignette,
grain; then the Remotion typography layer (PNG with alpha) on top. Writes a ProRes 422 HQ master.
usage: compose4.py reel4_dir [--overlay dir] [--frames a:b] [--preview] [--out name]"""
import json, math, os, subprocess, sys
import cv2
import numpy as np

R = sys.argv[1]
sys.path.insert(0, f"{R}/tools")
import grade4 as G  # noqa: E402

P = json.load(open(f"{R}/pack/edit_plan.json"))
W, H, FPS, N = P["w"], P["h"], P["fps"], P["frames"]
OV = sys.argv[sys.argv.index("--overlay") + 1] if "--overlay" in sys.argv else None
FR = [int(x) for x in sys.argv[sys.argv.index("--frames") + 1].split(":")] if "--frames" in sys.argv else [0, N]
PREVIEW = "--preview" in sys.argv
BEAT = P["song"]["beat_frames"]
geo = P["geometry"]


def dec(path, sel, scale_flags, extra=""):
    vf = f"select='{sel}',scale={W}:{H}:flags={scale_flags}{extra},format=rgb24"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", vf, "-vsync", "0", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


# ---------- sources
shots = P["shots"]
raw_lo = min(int(s["in"]) for s in shots if s["src"] == "raw")
raw_hi = max(int(math.ceil(s["in"] + s["step"] * (s["to"] - s["from"]))) for s in shots if s["src"] == "raw")
RAW = dec(f"{R}/src/music_src.mov", f"between(n\\,{raw_lo}\\,{raw_hi})", "lanczos+accurate_rnd+full_chroma_int")
BOOTH = cv2.imread(f"{R}/work/matte/booth.png", 0).astype(np.float32) / 255
_band = BOOTH - cv2.erode((BOOTH > 0.5).astype(np.float32), np.ones((25, 25), np.uint8))
BOOTH_EDGE = np.clip(_band, 0, 1)
_yy, _xx = np.mgrid[:H, :W].astype(np.float32)
_cols = np.clip((_xx - 20) / 2, 0, 1) * np.clip((1038 - _xx) / 2, 0, 1)          # booth spans x 20..1038 (measured)
_fade = np.clip((1880 - _yy) / 320, 0, 1) ** 1.6                                  # cabinet dissolves into the dark
BOOTH = BOOTH * _cols * _fade
AI = {}


def ai_frames(s):
    if s["id"] not in AI:
        a, b = s["in"], s["in"] + (s["to"] - s["from"]) - 1
        AI[s["id"]] = dec(f"{R}/src/clipA.mov", f"between(n\\,{a}\\,{b})", "lanczos+accurate_rnd+full_chroma_int", ",cas=0.45")
    return AI[s["id"]]


def raw_frame(idx):
    i = int(round(idx))
    return RAW[i - raw_lo].astype(np.float32) / 255, i


def void_alpha(i, rgb):
    person = cv2.imread(f"{R}/work/matte/r_{i:05d}.png", 0).astype(np.float32) / 255
    v = rgb.max(axis=2)
    dark = np.clip((0.58 - v) / 0.16, 0, 1)                   # wall slivers at the booth's outer edge are light
    booth = BOOTH * (1 - BOOTH_EDGE * (1 - dark))
    return np.maximum(person * _fade, booth)


# ---------- helpers
def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease_io_cubic(x):
    x = min(max(x, 0.0), 1.0)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def warp(img, s, anchor_src, anchor_dst, border=0):
    M = np.array([[s, 0, anchor_dst[0] - s * anchor_src[0]], [0, s, anchor_dst[1] - s * anchor_src[1]]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC if s > 1 else cv2.INTER_AREA,
                          borderMode=cv2.BORDER_CONSTANT if border == 0 else cv2.BORDER_REFLECT)


def bloom(img, k):
    if k < 0.01:
        return img
    small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    glow = cv2.resize(cv2.GaussianBlur(small, (0, 0), 9), (W, H), interpolation=cv2.INTER_LINEAR) * 1.25
    out = 1 - (1 - img) * (1 - np.clip(glow * k, 0, 1))
    flash = np.array([1.0, 0.94, 0.86], np.float32) * (0.62 * k)
    return out + (1 - out) * flash


BEATS = [i * BEAT for i in range(0, 21)]          # reel frames of every beat (beat 8 .. 28 of the song)
DROP = 4 * BEAT


def beat_pulse(f):
    if f < DROP - 0.5:
        return 0.0
    past = [b for b in BEATS if b <= f + 0.5 and b >= DROP - 0.5]
    if not past:
        return 0.0
    return 0.008 * math.exp(-(f - past[-1]) / 3.0)


WALL = {28: 0.30, 29: 0.0, 30: 0.10, 31: 0.0}          # lights-out flicker on beat 10

# ---------- render
OUTNAME = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else ("preview" if PREVIEW else "master")
out_path = f"{R}/render/{OUTNAME}.mov"
enc = (["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p"] if PREVIEW else
       ["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le", "-vendor", "apl0"])
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb48le", "-s", f"{W}x{H}", "-r", str(FPS),
                       "-i", "-", *enc, "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                       "-vf", "scale=out_color_matrix=bt709:out_range=tv", out_path], stdin=subprocess.PIPE)
rf, rt = geo["raw_face"], geo["ai_face"]
for f in range(FR[0], FR[1]):
    s = next(x for x in shots if x["from"] <= f < x["to"])
    k = f - s["from"]
    if s["src"] == "black":
        img = np.zeros((H, W, 3), np.float32)
    elif s["src"] == "raw":
        rgb, i = raw_frame(s["in"] + s["step"] * k)
        g = G.grade_bw(rgb)
        if not s.get("void"):
            sc = 1.0 + 0.045 * (k / (s["to"] - s["from"]))
            img = warp(g, sc, (rf[0], 1000), (rf[0], 1000))
        else:
            a = void_alpha(i, rgb)
            wl = WALL.get(f, 0.0)
            g = g * a[..., None] + g * (1 - a[..., None]) * wl
            # zoom out from the reality framing to the AI framing, then hold
            s0, s1 = 1.045, geo["raw_to_ai_scale"]
            p0 = (1.045 * rf[0] - 0.045 * rf[0], 1.045 * rf[1] - 0.045 * 1000)
            p1 = (s1 * rf[0] + geo["raw_to_ai_t"][0], s1 * rf[1] + geo["raw_to_ai_t"][1])
            u = ease_io_cubic(k / 24.0)
            sc = math.exp((1 - u) * math.log(s0) + u * math.log(s1))
            pd = (p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u)
            img = warp(g, sc, rf, pd)
    else:
        fr = ai_frames(s)[k].astype(np.float32) / 255
        g = G.halation(G.grade_world(fr, s["look"]))
        punch = 0.05 * math.exp(-k / 3.5) if s["id"] != "S5" else 0.08 * math.exp(-k / 3.0)
        drift = 0.022 * k / (s["to"] - s["from"])
        sc = 1.0 + punch + drift + beat_pulse(f)
        dx = dy = 0.0
        if s["id"] == "S3" and k < 9:                        # drop: short decaying shake
            amp = 7.0 * math.exp(-k / 3.0)
            dx, dy = amp * math.sin(k * 2.7), amp * math.cos(k * 3.9)
        img = warp(g, sc, rt, (rt[0] + dx, rt[1] + dy), border=1)
        if "bloom" in s:
            A, tau = s["bloom"]
            img = bloom(img, A * math.exp(-k / tau))
    look = s.get("look", "")
    img = G.vignette(img, 0.22 if look == "bw" else 0.16)
    img = G.grain(img, seed=1000 + f, amount=0.034 if look == "bw" else 0.022)
    ovp = next((q for q in (f"{OV}/{f:03d}.png", f"{OV}/{f:05d}.png", f"{OV}/{f}.png") if OV and os.path.exists(q)), None)
    if ovp:
        o = cv2.imread(ovp, cv2.IMREAD_UNCHANGED)
        if o is not None and o.shape[2] == 4:
            oa = o[..., 3:4].astype(np.float32) / 255
            orgb = cv2.cvtColor(o[..., :3], cv2.COLOR_BGR2RGB).astype(np.float32) / 255
            img = img * (1 - oa) + orgb * oa
    ff.stdin.write((np.clip(img, 0, 1) * 65535 + 0.5).astype("<u2").tobytes())
    if f % 30 == 0:
        print("frame", f, flush=True)
ff.stdin.close()
ff.wait()
print("wrote", out_path)
