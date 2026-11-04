"""Reel4 v2 look: one pack for five AI worlds + the B&W reality plate.
Per-world tone/chroma targets come from the measured pack (pack/grade_src.json): every world ends with deep blacks,
real highlights and a capped chroma, so the cut from world to world reads as one film. Shared texture: halation,
vignette, grain. All functions take/return float32 RGB in [0,1] (display-referred BT.709)."""
import cv2
import numpy as np
from scipy.interpolate import PchipInterpolator

# (src L*, target L*) control points and chroma gain / soft cap, per world  (src points = measured p1/p50/p99)
WORLDS = {
    "w1_foc":    {"L": [(0, 0), (1.9, 1.5), (16.6, 17.5), (60, 63), (96.9, 94.0), (100, 97)], "cg": 1.00, "cap": 58},
    "w2_noapte": {"L": [(0, 0), (1.5, 1.5), (10.2, 12.5), (30, 38), (55.2, 76.0), (100, 100)], "cg": 1.05, "cap": 58},
    "w3_ceata":  {"L": [(0, 0), (2.2, 2.0), (25, 22.5), (43.4, 40.0), (54.9, 52.0), (80, 80), (100, 100)], "cg": 1.0, "cap": 95},
    "w4_ocean":  {"L": [(0, 0.8), (14.8, 16.5), (40, 47), (70.9, 84.0), (100, 100)], "cg": 1.18, "cap": 58},
    "w5_apus":   {"L": [(0, 0), (1.2, 1.2), (27.7, 27.0), (70, 72), (97.4, 94.5), (100, 97)], "cg": 1.00, "cap": 55},
}
_CURVES = {k: PchipInterpolator(*zip(*v["L"])) for k, v in WORLDS.items()}
_LUT_X = np.linspace(0, 100, 1001, dtype=np.float32)
_LUTS = {k: c(_LUT_X).astype(np.float32) for k, c in _CURVES.items()}


def _soft_cap(C, cap, knee=0.75):
    k0 = cap * knee
    over = np.maximum(C - k0, 0)
    return np.where(C > k0, k0 + (cap - k0) * np.tanh(over / (cap - k0)), C)


def grade_world(rgb, world):
    p = WORLDS[world]
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2Lab)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    L2 = np.interp(L, _LUT_X, _LUTS[world]).astype(np.float32)
    C = np.sqrt(a * a + b * b) + 1e-6
    C2 = _soft_cap(C * p["cg"], p["cap"])
    # keep chroma sane where L was pushed toward the ends (avoid neon blacks / clipped whites)
    room = np.clip(np.minimum(L2, 100 - L2) / 12.0, 0.35, 1.0)
    s = (C2 / C) * np.where(L2 > L, room, 1.0)
    out = cv2.cvtColor(np.dstack([L2, a * s, b * s]).astype(np.float32), cv2.COLOR_Lab2RGB)
    return np.clip(out, 0, 1)


_BW_CURVE = PchipInterpolator([0, 3, 20, 45, 60, 68, 80, 100], [0, 2.2, 15, 41, 57, 65, 77, 96])
_BW_LUT = _BW_CURVE(_LUT_X).astype(np.float32)


def grade_bw(rgb):
    """Neutral silver B&W: red-leaning luminance mix for skin, deep booth blacks, wall kept light grey."""
    y = rgb[..., 0] * 0.36 + rgb[..., 1] * 0.50 + rgb[..., 2] * 0.14
    lab = cv2.cvtColor(np.dstack([y, y, y]).astype(np.float32), cv2.COLOR_RGB2Lab)
    L2 = np.interp(lab[..., 0], _LUT_X, _BW_LUT).astype(np.float32)
    z = np.zeros_like(L2)
    out = cv2.cvtColor(np.dstack([L2, z + 0.4, z + 1.2]).astype(np.float32), cv2.COLOR_Lab2RGB)   # faint warm silver
    return np.clip(out, 0, 1)


def halation(rgb, strength=0.16, sigma=14):
    y = rgb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    hl = np.clip((y - 0.72) / 0.28, 0, 1) ** 1.5
    small = cv2.resize(rgb * hl[..., None], None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
    glow = cv2.resize(cv2.GaussianBlur(small, (0, 0), sigma / 4), (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_LINEAR)
    glow *= np.array([1.0, 0.42, 0.20], np.float32) * strength
    return 1 - (1 - rgb) * (1 - glow)


_VIG = {}


def vignette(rgb, amount=0.16):
    h, w = rgb.shape[:2]
    if (h, w, amount) not in _VIG:
        yy, xx = np.mgrid[:h, :w].astype(np.float32)
        r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 * 0.55 + ((yy - h * 0.47) / (h / 2)) ** 2)
        _VIG[(h, w, amount)] = (1 - amount * np.clip(r / 1.25, 0, 1) ** 2.4).astype(np.float32)[..., None]
    return rgb * _VIG[(h, w, amount)]


def grain(rgb, seed, amount=0.032):
    rng = np.random.default_rng(seed)
    h, w = rgb.shape[:2]
    n = rng.standard_normal((h // 2, w // 2)).astype(np.float32)
    n = cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)
    n = cv2.GaussianBlur(n, (0, 0), 0.6)
    y = rgb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    weight = 0.35 + 0.65 * (4 * y * (1 - y))           # most grain in the mids, little in deep black / white
    return np.clip(rgb + (n * amount * weight)[..., None], 0, 1)
