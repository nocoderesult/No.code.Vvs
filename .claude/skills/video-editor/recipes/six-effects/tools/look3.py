"""Reel 3 grade: Apple Log 2 (Apple Wide Gamut) -> Rec.709, tuned for the olive-wall / warm-lamp room.

Scene steps (linear): decode -> partial white balance (Bradford, measured on denim + black tee)
-> exposure -> gamut compression -> filmic tonemap with highlight path-to-white.
Look (Oklab, display-linear): skin hue/chroma placement, olive wall pushed to a deeper green,
beige couch calmed, denim kept blue, subtle split tone, filmic contrast with a soft floor.
Output: BT.709 OETF code values, so iPhone / Mac players (which decode BT.709 with the inverse
OETF) show the intended contrast instead of the washed-out 2.4 look.

usage as a script: look3.py out.cube size [--log-passthrough]
"""
import sys
import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])

# ---------------- Apple Log / Apple Wide Gamut
R0, Rt, c, b, g, be = -0.05641088, 0.01, 47.28711236, 0.00964052, 0.08550479, 0.69336945
Pt = c * (Rt - R0) ** 2


def applelog_decode(P):
    P = np.asarray(P, np.float64)
    return np.where(P >= Pt, 2 ** ((P - be) / g) - b, np.where(P > 0, np.sqrt(np.maximum(P, 0) / c) + R0, R0))


def npm(prim, wp):
    xy = np.array(prim + [wp])
    XYZ = np.stack([xy[:, 0] / xy[:, 1], np.ones(4), (1 - xy[:, 0] - xy[:, 1]) / xy[:, 1]], 1)
    S = np.linalg.solve(XYZ[:3].T, XYZ[3])
    return XYZ[:3].T * S


D65 = (0.3127, 0.3290)
AWG = [(0.725, 0.301), (0.221, 0.814), (0.068, -0.076)]
REC709 = [(0.64, 0.33), (0.30, 0.60), (0.15, 0.06)]
M_AWG = npm(AWG, D65)
M_709 = npm(REC709, D65)
AWG_to_709 = np.linalg.inv(M_709) @ M_AWG
BRADFORD = np.array([[0.8951, 0.2664, -0.1614], [-0.7502, 1.7135, 0.0367], [0.0389, -0.0685, 1.0296]])

# ---------------- parameters (tuned on frames 25.5 s and 47.3 s)
P = dict(
    wb_rgb=(1.26, 1.0, 0.89),   # measured illuminant in linear 709 (R/G, 1, B/G), from denim + black tee
    wb_amount=0.62,             # how much of the cast to remove (keep some lamp warmth)
    expo=-0.20,                 # stops
    grey_out=0.165, p=1.30,     # tonemap: 18% grey -> display 0.165, contrast power
    skin_hue=62.0, skin_pull=0.45, skin_chroma=0.80,
    wall_hue=128.0, wall_pull=0.35, wall_chroma=1.18, wall_dL=-0.035,
    couch_chroma=0.80, blue_chroma=1.12, sat=1.06,
    floor=0.010, contrast=0.050,
)


def wb_matrix(amount, wb):
    """Bradford adaptation (in 709 linear) from the measured illuminant toward D65, by `amount`."""
    src = np.array(wb, float)
    src_xyz = M_709 @ src
    d65_xyz = M_709 @ np.ones(3)
    ls, ld = BRADFORD @ src_xyz, BRADFORD @ d65_xyz
    gain = (ld / ls) ** amount
    M = np.linalg.inv(M_709) @ np.linalg.inv(BRADFORD) @ np.diag(gain) @ BRADFORD @ M_709
    # keep luminance of neutral grey
    y = np.array([0.2126, 0.7152, 0.0722])
    return M / (y @ M @ np.ones(3))


def rgc(lin):
    ach = np.max(lin, axis=-1, keepdims=True)
    d = np.where(ach > 1e-6, (ach - lin) / np.maximum(np.abs(ach), 1e-6), 0.0)
    thr, lim, pw = np.array([0.815, 0.803, 0.880]), np.array([1.147, 1.264, 1.312]), 1.2
    s = (lim - thr) / (((1 - thr) / (lim - thr)) ** (-pw) - 1) ** (1 / pw)
    comp = np.where(d < thr, d, thr + s * ((d - thr) / s) / (1 + ((d - thr) / s) ** pw) ** (1 / pw))
    return ach - comp * np.abs(ach)


def tonemap(n, p, grey_out):
    s = 0.18 / grey_out ** (1 / p) - 0.18
    return (n / (n + s)) ** p


M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566],
               [0.0883024619, 0.2817188376, 0.6299787005]])
M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099],
               [0.0259040371, 0.7827717662, -0.8086757660]])
M1i, M2i = np.linalg.inv(M1), np.linalg.inv(M2)


def to_oklab(rgb):
    return np.cbrt(np.maximum(rgb @ M1.T, 0)) @ M2.T


def from_oklab(lab):
    return ((lab @ M2i.T) ** 3) @ M1i.T


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def band(h, a0, a1, b0, b1):
    return smooth(a0, a1, h) * (1 - smooth(b0, b1, h))


def look(D, p):
    lab = to_oklab(D)
    L, a, bb = lab[..., 0], lab[..., 1], lab[..., 2]
    C = np.hypot(a, bb)
    h = np.degrees(np.arctan2(bb, a)) % 360
    chroma_ok = smooth(0.008, 0.03, C)
    skin = band(h, 15, 35, 80, 98) * chroma_ok * smooth(0.25, 0.45, L)
    wall = band(h, 92, 105, 150, 170) * chroma_ok
    couch = band(h, 70, 80, 92, 102) * chroma_ok * smooth(0.55, 0.75, L)
    blue = band(h, 200, 225, 275, 295) * chroma_ok
    dh = (p["skin_hue"] - h) * p["skin_pull"] * skin + (p["wall_hue"] - h) * p["wall_pull"] * wall
    sat = p["sat"] * (1 + (p["skin_chroma"] - 1) * skin + (p["wall_chroma"] - 1) * wall
                      + (p["couch_chroma"] - 1) * couch + (p["blue_chroma"] - 1) * blue)
    sat = 1 + (sat - 1) * (1 - smooth(0.88, 1.0, L))          # no colour boost near white
    h2 = np.radians(h + dh)
    C2 = C * sat
    a, bb = C2 * np.cos(h2), C2 * np.sin(h2)
    L = L + p["wall_dL"] * wall * (1 - smooth(0.5, 0.7, L))
    # split tone: deep teal-green shadows, warm creamy highlights (subtle)
    ws, wh = (1 - smooth(0.12, 0.50, L)) ** 1.5, smooth(0.60, 0.95, L)
    a += -0.007 * ws + 0.002 * wh
    bb += -0.004 * ws + 0.008 * wh
    # filmic S in L around 0.55 with a soft (not crushed) floor
    L2 = L + p["contrast"] * np.sin((L - 0.55) * np.pi) * smooth(0.0, 0.25, L) * (1 - smooth(0.88, 1.0, L))
    L2 = p["floor"] + L2 * (1 - p["floor"])
    return from_oklab(np.stack([L2, a, bb], -1))


def oetf709(x):
    x = np.clip(x, 0, 1)
    return np.where(x < 0.018, 4.5 * x, 1.099 * x ** 0.45 - 0.099)


def scene(code, p=P):
    lin = applelog_decode(code) @ AWG_to_709.T
    lin = lin @ wb_matrix(p["wb_amount"], p["wb_rgb"]).T
    lin = lin * 2 ** p["expo"]
    return np.maximum(rgc(lin), 0)


def display(lin, p=P):
    n = np.max(lin, axis=-1, keepdims=True)
    D = lin * np.where(n > 1e-9, tonemap(n, p["p"], p["grey_out"]) / np.maximum(n, 1e-9), 0)
    Dn = np.max(D, axis=-1, keepdims=True)
    w = smooth(0.72, 1.0, Dn) * 0.85
    lum = D @ np.array([0.2126, 0.7152, 0.0722])
    D = D * (1 - w) + lum[..., None] * w
    return np.clip(look(D, p), 0, 1)


def transform(code, p=P):
    """Apple Log code values (0..1) -> BT.709 OETF code values (0..1)."""
    return oetf709(display(scene(code, p), p))


def write_cube(path, size, fn, title):
    gg = np.linspace(0, 1, size)
    B_, G_, R_ = np.meshgrid(gg, gg, gg, indexing="ij")    # .cube: R fastest
    grid = np.stack([R_, G_, B_], -1).reshape(-1, 3)
    out = fn(grid)
    with open(path, "w") as f:
        f.write(f'TITLE "{title}"\n')
        f.write("# Input: Apple Log 2 / Apple Wide Gamut, full-range code values\n")
        f.write("# Output: Rec.709 primaries, BT.709 OETF encoding (Rec.709-A style, correct on Apple players)\n")
        f.write(f"LUT_3D_SIZE {size}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n")
        np.savetxt(f, out, fmt="%.6f")


if __name__ == "__main__":
    out, size = sys.argv[1], int(sys.argv[2])
    write_cube(out, size, transform, "NoCode AppleLog2 Reel3 Cinematic v3")
    print("wrote", out, "grey 0.488 ->", transform(np.array([[0.488] * 3]))[0].round(3))
