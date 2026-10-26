"""Reel 3 compositor: graded plate -> virtual camera -> clean-up/relight -> effect layers -> grain.

Per output frame:
  plate   = source frame (Apple Log -> v3 LUT, or raw Log for the "before" side of the colour wipe)
  camera  = crop/zoom/roll from timeline.json (Lanczos; 3-tap shutter blur while the camera whips)
  clean   = olive wall smoothed outside the person (iPhone shadow noise), face lift + vignette, sharpen
  layers  = behind glass -> Behind overlay -> person (matte) -> front glass -> Front overlay
  freeze  = flash, grey world, cut-out sticker with white outline + shadow
  wipe    = Log | graded split behind a light line that follows his hand
  grain   = fine monochrome film grain on the plate (not on the graphics)

usage: compose.py reel3_dir layers_dir --scale 1|2 (--list k,k,... out_dir | --range a b out.mov)
"""
import json, math, os, subprocess, sys, time
import cv2
import numpy as np

cv2.setNumThreads(int(os.environ.get("CV_THREADS", "2")))
R, LAY = sys.argv[1], sys.argv[2]
S = int(sys.argv[sys.argv.index("--scale") + 1])
FF = os.environ.get("FFMPEG", "ffmpeg")        # any ffmpeg with lut3d + prores_ks
FPS = 30
OW, OH = 1080 * S, 1920 * S
SW, SH = (2160, 3840) if S == 2 else (1080, 1920)        # decoded source size (portrait)
tl = json.load(open(f"{R}/work/timeline.json"))
ev = json.load(open(f"{R}/work/events.json"))
TRACK = json.load(open(f"{R}/work/track.json"))
FR = tl["frames"]
LUT = f"{R}/lut/reel3_v3_65.cube"


# ------------------------------------------------------------------ source decoding
class Source:
    """Sequential reader of graded (or raw Log) source frames; reseeks only when the timeline jumps."""

    def __init__(self, log=False):
        self.log, self.p, self.next, self.last = log, None, None, (None, None)

    def _open(self, idx):
        if self.p:
            self.p.kill()
        vf = f"scale={SW}:{SH}:in_color_matrix=bt2020:in_range=tv:flags=lanczos,format=rgb48le"
        if not self.log:
            vf = f"hqdn3d=1.2:4:2.5:5,{vf},lut3d={LUT}:interp=tetrahedral"
        cmd = [FF, "-v", "error", "-ss", f"{(idx - 0.15) / FPS:.5f}", "-i", f"{R}/src/raw.mov", "-an", "-vf", vf,
               "-f", "rawvideo", "-"]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=SW * SH * 6)
        self.next = idx

    def get(self, idx):
        if self.last[0] == idx:
            return self.last[1]
        if self.p is None or idx != self.next:
            self._open(idx)
        buf = self.p.stdout.read(SW * SH * 6)
        img = np.frombuffer(buf, np.uint16).reshape(SH, SW, 3).astype(np.float32)
        img *= 1 / 65535.0
        self.next = idx + 1
        self.last = (idx, img)
        return img


def matte_src(idx):
    m = cv2.imread(f"{R}/work/matte/m_{idx:05d}.png", cv2.IMREAD_GRAYSCALE)
    return None if m is None else m.astype(np.float32) / 255.0


# ------------------------------------------------------------------ camera
def cam_params(k, sub=0.0):
    """u0, v0, span, roll at output frame k (+ fraction of a frame, for shutter blur)."""
    a = FR[k]
    if sub == 0 or not (0 <= k + (1 if sub > 0 else -1) < len(FR)):
        return a["u0"], a["v0"], a["span"], a["roll"]
    b = FR[k + (1 if sub > 0 else -1)]
    if b["seg"] != a["seg"]:
        return a["u0"], a["v0"], a["span"], a["roll"]
    w = abs(sub)
    return tuple(a[x] * (1 - w) + b[x] * w for x in ("u0", "v0", "span", "roll"))


def cam_matrix(u0, v0, span, roll, src_w, src_h):
    """Affine (output px -> source px) for an output of OW x OH."""
    th = math.radians(roll)
    c, s = math.cos(th), math.sin(th)
    sx = span * src_w / OW                       # source px per output px
    xc, yc = OW / 2, OH / 2
    # X' = R (X - c) + c ; src = (u0 * src_w, v0 * src_h) + sx * X'
    M = np.array([[sx * c, -sx * s, 0.0], [sx * s, sx * c, 0.0]])
    off = np.array([xc - (c * xc - s * yc), yc - (s * xc + c * yc)])
    M[:, 2] = sx * off + np.array([u0 * src_w, v0 * src_h])
    return M


def warp(img, M, interp=cv2.INTER_LANCZOS4):
    return cv2.warpAffine(img, M, (OW, OH), flags=interp | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)


def speed(k):
    if k + 1 >= len(FR) or FR[k + 1]["seg"] != FR[k]["seg"]:
        return 0.0
    a, b = FR[k], FR[k + 1]
    return (abs(a["u0"] - b["u0"]) * SW + abs(a["v0"] - b["v0"]) * SH + abs(a["span"] - b["span"]) * SH) / S


# ------------------------------------------------------------------ helpers
def blur_small(img, sigma_out, factor=4):
    """Large gaussian blur done at 1/factor resolution (frosted glass, wall clean-up)."""
    h, w = img.shape[:2]
    small = cv2.resize(img, (w // factor, h // factor), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), sigma_out / factor)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)


def luma(img):
    return img @ np.array([0.2126, 0.7152, 0.0722], np.float32)


def load_layer(name, k, size):
    p = f"{LAY}/{name}/{k:05d}.png"
    if not os.path.exists(p):
        return None
    im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    if im is None:
        return None
    if im.shape[1] != size[0]:
        im = cv2.resize(im, size, interpolation=cv2.INTER_LINEAR)
    return im


def bbox(mask, pad=0):
    """(x0, y0, x1, y1) of the non-zero area of a uint8/float mask, padded and clipped; None if empty."""
    m = mask if mask.dtype == np.uint8 else (mask > 0.003).astype(np.uint8)
    x, y, w, h = cv2.boundingRect(m)
    if w == 0 or h == 0:
        return None
    return max(0, x - pad), max(0, y - pad), min(m.shape[1], x + w + pad), min(m.shape[0], y + h + pad)


def lerp_(dst, src, w, bb):
    """In place, inside bb: dst += (src - dst) * w.  src/w are full-frame arrays (or scalars for src)."""
    x0, y0, x1, y1 = bb
    d = dst[y0:y1, x0:x1]
    ww = w[y0:y1, x0:x1, None] if w.ndim == 2 else w[y0:y1, x0:x1]
    sv = src[y0:y1, x0:x1] if isinstance(src, np.ndarray) else src
    tmp = sv - d
    tmp *= ww
    d += tmp


def over(dst, layer):
    """Straight-alpha BGRA (uint8) over float RGB, in place, only where the layer is not transparent."""
    if layer is None or layer.shape[2] < 4:
        return dst
    bb = bbox(layer[..., 3])
    if bb is None:
        return dst
    x0, y0, x1, y1 = bb
    a = layer[y0:y1, x0:x1, 3:4].astype(np.float32) * (1 / 255)
    rgb = layer[y0:y1, x0:x1, 2::-1].astype(np.float32) * (1 / 255)
    d = dst[y0:y1, x0:x1]
    d += (rgb - d) * a
    return dst


def frost(img, m, sigma, lift):
    """Frosted glass in place: blur (computed on the padded mask box only) blended by mask m."""
    bb = bbox(m, pad=int(3 * sigma))
    if bb is None:
        return img
    x0, y0, x1, y1 = bb
    sub = img[y0:y1, x0:x1]
    h, w = sub.shape[:2]
    f = 4
    small = cv2.resize(sub, (max(w // f, 1), max(h // f, 1)), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), sigma / f)
    bl = cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR) * 0.93 + lift
    sub += (bl - sub) * m[y0:y1, x0:x1, None]
    return img


XROW = np.arange(OW, dtype=np.float32)


_yq, _xq = np.mgrid[0:OH // 8, 0:OW // 8].astype(np.float32)
_yq, _xq = (_yq + 0.5) / (OH // 8), (_xq + 0.5) / (OW // 8)


def relight(img, face):
    fx, fy, fw, fh = face
    cx, cy = fx + fw / 2, fy + fh * 0.55
    # soft face lift (+5 %), wide vignette (-20 % corners), heavier at the bottom (couch / jeans); built at 1/8 res
    d_face = ((_xq - cx) / (fw * 1.1)) ** 2 + ((_yq - cy) / (fh * 1.2)) ** 2
    lift = 1 + 0.05 * np.exp(-d_face)
    d = ((_xq - 0.5) / 0.75) ** 2 + ((_yq - (cy + 0.05)) / 0.95) ** 2
    vig = 1 - 0.20 * np.clip(d, 0, 1.6) ** 1.4 / 1.6 ** 1.4
    bottom = 1 - 0.10 * np.clip((_yq - 0.78) / 0.22, 0, 1) ** 1.5
    gain = cv2.resize((lift * vig * bottom).astype(np.float32), (OW, OH), interpolation=cv2.INTER_LINEAR)
    img *= gain[..., None]
    return img


def wall_mask(img, person):
    """Olive wall pixels (dark, low-chroma greenish) that are not the person; built at 1/4 res."""
    q = (OW // 4, OH // 4)
    small = cv2.resize(img, q, interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(np.clip(small, 0, 1), cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    m = ((h > 45) & (h < 150) & (s > 0.08) & (s < 0.75) & (v < 0.45)).astype(np.float32)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    m = cv2.GaussianBlur(m, (0, 0), 3)
    ps = cv2.resize(person, q, interpolation=cv2.INTER_AREA)
    keep = cv2.dilate((ps > 0.02).astype(np.float32), np.ones((5, 5), np.uint8))
    keep = cv2.GaussianBlur(keep, (0, 0), 1.2)
    m = np.clip(m * (1 - keep), 0, 1)
    return cv2.resize(m, (OW, OH), interpolation=cv2.INTER_LINEAR)


def clean_wall(img, wm, sigma=26):
    """Replace the wall by its smooth estimate from wall pixels only (normalized convolution)."""
    f = 4
    small_w = cv2.resize(wm, (OW // f, OH // f), interpolation=cv2.INTER_AREA)
    small_i = cv2.resize(img, (OW // f, OH // f), interpolation=cv2.INTER_AREA)
    sg = sigma * S / f
    num = cv2.GaussianBlur(small_i * small_w[..., None], (0, 0), sg)
    den = cv2.GaussianBlur(small_w, (0, 0), sg)[..., None]
    est = np.where(den > 1e-3, num / np.maximum(den, 1e-3), small_i).astype(np.float32)
    est = cv2.resize(est, (OW, OH), interpolation=cv2.INTER_LINEAR)
    bb = bbox(wm)
    if bb is not None:
        lerp_(img, est, wm, bb)
    return img


def sharpen(img, amount_map):
    """Unsharp mask on luma only (no colour fringes)."""
    Y = luma(img)
    d = Y - cv2.GaussianBlur(Y, (0, 0), 1.4 * S)
    d *= amount_map
    img += d[..., None]
    return img


RNG = np.random.default_rng(7)


def grain(img, k):
    g = np.random.default_rng(1000 + k).standard_normal((OH // 2, OW // 2)).astype(np.float32)
    g = cv2.resize(g, (OW, OH), interpolation=cv2.INTER_LINEAR)
    L = luma(img)
    amp = 0.016 * (0.35 + 2.6 * L * (1 - L))
    img += (g * amp)[..., None]
    return img


def hand_x_out(k):
    """Index fingertip x in output coords (None if no hand), for the wipe."""
    a = FR[k]
    e = TRACK[a["src"]]
    if not e or not e.get("hands"):
        return None
    xs = [h[8][0] for h in e["hands"] if 0.40 < h[8][1] < 0.70]
    if not xs:
        return None
    return (min(xs) - a["u0"]) / a["span"]


WIPE = {}


def wipe_curve():
    g = ev["grade"]
    k0, k1 = round(g["wipe_start"] * FPS), round(g["wipe_end"] * FPS)
    cur = -0.06
    for k in range(k0, k1 + 1):
        u = (k - k0) / max(k1 - k0, 1)
        e = u * u * (3 - 2 * u)
        x = -0.06 + 1.14 * e
        hx = hand_x_out(k)
        if hx is not None and u < 0.55:
            x = max(x, min(hx, 0.75))
        cur = max(cur, x)
        WIPE[k] = cur


wipe_curve()


# ------------------------------------------------------------------ one frame
SRC = Source()
LOG = Source(log=True)
FREEZE_CACHE = {}


def person_alpha(k, plate_out, M, refine):
    a = FR[k]
    m = matte_src(a["src"])
    if m is None:
        return np.zeros((OH, OW), np.float32)
    Mm = M.copy()
    Mm[:, :] *= m.shape[1] / SW                 # matte is 1080 wide in source space
    al = cv2.warpAffine(m, Mm, (OW, OH), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
    if refine:
        guide = luma(plate_out)
        al = cv2.ximgproc.guidedFilter(guide=guide, src=al, radius=6 * S, eps=1e-3)
        al = np.clip((al - 0.04) / 0.92, 0, 1)
    return al


def render(k):
    a = FR[k]
    t = k / FPS
    g = ev["grade"]
    use_log = "logwipe" in a and k < round(g["wipe_end"] * FPS)
    plate_src = SRC.get(a["src"])
    M = cam_matrix(a["u0"], a["v0"], a["span"], a["roll"], SW, SH)
    if speed(k) > 6:                            # whip: 3-tap shutter
        acc = np.zeros((OH, OW, 3), np.float32)
        for sub in (-0.33, 0.0, 0.33):
            acc += warp(plate_src, cam_matrix(*cam_params(k, sub), SW, SH))
        plate = acc / 3
    else:
        plate = warp(plate_src, M)

    behind = load_layer("behind", k, (OW, OH))
    front = load_layer("front", k, (OW, OH))
    masks = load_layer("mask", k, (OW, OH))
    freeze = "freeze" in a
    refine = behind is not None or freeze
    alpha = person_alpha(k, plate, M, refine)

    # clean the olive wall, relight, sharpen the person
    wm = wall_mask(plate, alpha)
    plate = clean_wall(plate, wm)
    plate = relight(plate, a["face"])
    plate = sharpen(plate, 0.28 + 0.45 * alpha)

    if use_log:
        log_plate = warp(LOG.get(a["src"]), M)
        x = WIPE.get(k, -1.0)
        if x <= -0.05:
            plate = log_plate
        else:
            edge = np.clip((XROW / OW - x) / 0.012, 0, 1)[None, :, None]   # right of the line = still Log
            plate = plate * (1 - edge) + log_plate * edge
    plate = grain(plate, k)

    # ---- layering
    mr = mg = None
    if masks is not None:
        mr = masks[..., 2].astype(np.float32) * (1 / 255)
        mg = masks[..., 1].astype(np.float32) * (1 / 255)
    if freeze:
        out = freeze_frame(k, plate, alpha)
    else:
        out = plate.copy() if (behind is not None or mr is not None) else plate
        if mr is not None:
            frost(out, mr, 22 * S, 0.03)
        if behind is not None:
            over(out, behind)
            m_b = behind[..., 3] if mr is None else np.maximum(behind[..., 3], masks[..., 2])
            bb = bbox(m_b)
            if bb is not None:
                lerp_(out, plate, alpha, bb)
    if mg is not None:
        frost(out, mg, 24 * S, 0.02)
    if "logwipe" in a and k in WIPE and -0.05 < WIPE[k] < 1.05:
        out = light_line(out, WIPE[k])
    if "hold" in a:
        c = ev["cta"]
        u = np.clip((t - c["hold"]) / 0.6, 0, 1)
        u = u * u * (3 - 2 * u)
        if u > 0:
            out = out * (1 - 0.38 * u) * (1 - u) + blur_small(out, 10 * S) * (1 - 0.38 * u) * u
    out = over(out, front)
    if freeze:
        out = flash(out, k)
    return np.clip(out, 0, 1)


def light_line(img, x):
    X = x * OW
    d = (XROW - X)
    core = np.exp(-(d / (3.5 * S)) ** 2)
    glow = np.exp(-(d / (38 * S)) ** 2) * 0.45 + np.exp(-(d / (140 * S)) ** 2) * 0.12
    col = np.array([1.0, 0.93, 0.80], np.float32)
    add = (core * 0.95 + glow)[None, :, None] * col
    return 1 - (1 - img) * (1 - np.clip(add, 0, 1))          # screen


def freeze_frame(k, plate, alpha):
    a = FR[k]
    t_in = a["freeze"]
    if "base" not in FREEZE_CACHE:
        FREEZE_CACHE["base"] = (plate.copy(), alpha.copy())
    plate0, al0 = FREEZE_CACHE["base"]
    g = np.clip(t_in / 0.18, 0, 1)
    grey = luma(plate0)[..., None].repeat(3, 2)
    bg = plate0 * (1 - g) + (grey * 0.62 + 0.035) * g
    bg = bg * (1 - 0.6 * g) + blur_small(bg, 6 * S) * 0.6 * g
    # sticker pop: spring scale + slight rotation about the person's centroid
    sp = 1 - math.exp(-t_in / 0.07) * math.cos(t_in * 22)
    scale = 1 + 0.045 * sp
    rot = -2.5 * sp
    ys, xs = np.nonzero(al0 > 0.5)
    cy, cx = (ys.mean(), xs.mean()) if len(xs) else (OH / 2, OW / 2)
    Mt = cv2.getRotationMatrix2D((float(cx), float(cy)), rot, scale)
    person = cv2.warpAffine(plate0, Mt, (OW, OH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    al = cv2.warpAffine(al0, Mt, (OW, OH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    border = 15 * S
    ring = cv2.dilate((al > 0.5).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * border + 1, 2 * border + 1))).astype(np.float32)
    ring = cv2.GaussianBlur(ring, (0, 0), 0.8 * S)
    shadow = cv2.GaussianBlur(ring, (0, 0), 16 * S)
    shadow = np.roll(shadow, 22 * S, axis=0) * 0.5 * g
    out = bg * (1 - shadow[..., None])
    out = out * (1 - ring[..., None] * g) + 1.0 * ring[..., None] * g
    pa = np.maximum(al, 1 - g)[..., None] if g < 1 else al[..., None]
    out = out * (1 - pa) + person * pa
    return out


def flash(img, k):
    t_in = FR[k]["freeze"]
    a = 0.92 * math.exp(-t_in / 0.075) if t_in < 0.5 else 0.0
    return img * (1 - a) + a


# ------------------------------------------------------------------ main
def to_u16(img):
    return (np.clip(img, 0, 1) * 65535 + 0.5).astype(np.uint16)


if "--list" in sys.argv:
    ks = [int(x) for x in sys.argv[sys.argv.index("--list") + 1].split(",")]
    od = sys.argv[sys.argv.index("--list") + 2]
    os.makedirs(od, exist_ok=True)
    for k in sorted(ks):
        t0 = time.time()
        img = render(k)
        cv2.imwrite(f"{od}/c_{k:05d}.jpg", (img[..., ::-1] * 255 + 0.5).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
        print(f"frame {k} ({FR[k]['seg']}) {time.time() - t0:.2f}s", flush=True)
else:
    a, b = (int(x) for x in sys.argv[sys.argv.index("--range") + 1:sys.argv.index("--range") + 3])
    out = sys.argv[sys.argv.index("--range") + 3]
    enc = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb48le", "-s", f"{OW}x{OH}", "-r", "30",
                            "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv422p10le",
                            "-c:v", "prores_ks", "-profile:v", "3", "-vendor", "apl0",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
                            out], stdin=subprocess.PIPE)
    t0 = time.time()
    for k in range(a, b):
        enc.stdin.write(to_u16(render(k)).tobytes())
        if (k - a) % 20 == 0:
            el = time.time() - t0
            print(f"[{a}-{b}] {k - a + 1}/{b - a}  {el / (k - a + 1):.2f}s/frame", flush=True)
    enc.stdin.close()
    enc.wait()
    print(f"done {out} in {time.time() - t0:.0f}s")
