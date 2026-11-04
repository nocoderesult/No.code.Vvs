"""White room in the AI framing. The 1080x1920 120 fps take is scaled (s, tx, ty from the booth edges) so the deck sits
exactly where it sits in every AI world; the missing room around it is extended from the take's own wall
(normalized convolution of wall pixels, so the seam carries the real wall colour), the cabinet is continued down to
the AI cabinet bottom, the floor is a slightly darker cyclorama with a contact shadow.
usage: white_plate.py reel4_dir out.mp4 first_raw120 n_frames [step]   -> H.264 plate, 30 fps"""
import json, subprocess, sys
import cv2
import numpy as np

R, OUT, FIRST, N = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
STEP = float(sys.argv[5]) if len(sys.argv) > 5 else 4.0          # 120 fps -> 30 fps real time
g = json.load(open(f"{R}/v3/work/white_geom.json"))
s, tx, ty, CAB = g["s"], g["tx"], g["ty"], g["cab_bottom"]
W, H = 1080, 1920
M = np.array([[s, 0, tx], [0, s, ty]], np.float32)
yb = int(round(ty + 1920 * s))                     # bottom of the filmed area in the canvas (1458)
x0, x1, y0 = int(round(tx)), int(round(tx + 1080 * s)), int(round(ty))
cy, cx = np.mgrid[:H, :W].astype(np.float32)

med = cv2.imread(f"{R}/work/matte/median.jpg").astype(np.float32) / 255
booth = cv2.imread(f"{R}/work/matte/booth.png", 0).astype(np.float32) / 255
_bx = np.arange(1080, dtype=np.float32)[None, :]
booth = booth * np.clip((_bx - 20) / 2, 0, 1) * np.clip((1038 - _bx) / 2, 0, 1)   # measured booth sides (no floor slivers)
med_s = cv2.warpAffine(med, M, (W, H), flags=cv2.INTER_AREA)
booth_s = cv2.warpAffine(booth, M, (W, H), flags=cv2.INTER_LINEAR)
inside = cv2.warpAffine(np.ones((1920, 1080), np.float32), M, (W, H), flags=cv2.INTER_LINEAR)

# --- wall field: normalized convolution of wall pixels (inside the filmed area, not booth, not DJ, not floor slivers)
wallm = (inside > 0.99) & (booth_s < 0.02) & ~((cx > 330) & (cx < 760) & (cy > 740)) & (cy < 1330)
wallm = wallm.astype(np.float32)
def nconv(img, m, sig):
    small = lambda a: cv2.resize(a, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    num = cv2.GaussianBlur(small(img * m[..., None]), (0, 0), sig / 4)
    den = cv2.GaussianBlur(small(m), (0, 0), sig / 4)
    up = lambda a: cv2.resize(a, (W, H), interpolation=cv2.INTER_CUBIC)
    return up(num / np.maximum(den, 1e-6)[..., None]), up(den)
# three scales; each is trusted only where its own support (den) is solid, so nothing far from the wall goes dark
n1, d1 = nconv(med_s, wallm, 20)
n2, d2 = nconv(med_s, wallm, 90)
n3, d3 = nconv(med_s, wallm, 420)
c1 = np.clip(d1 / 0.35, 0, 1)[..., None] ** 2
c2 = np.clip(d2 / 0.30, 0, 1)[..., None] ** 2
bg = n1 * c1 + (1 - c1) * (n2 * c2 + (1 - c2) * n3)
# floor: below the wall/floor line (real floor line of the room maps to ~y 1377), a touch darker and warmer
floor = np.clip((cy - 1360) / 160, 0, 1)[..., None]
bg = bg * (1 - 0.14 * floor) + np.array([0.0, 0.004, 0.012], np.float32) * floor
# cabinet: continue the last real rows of the booth straight down to the AI cabinet bottom; the side edges are the
# edges of the last real row, so the extension is exactly as wide as the filmed cabinet
last = np.clip((booth_s[yb - 14] - 0.5) * 6 + 0.5, 0, 1)            # crisp 1-row profile of the cabinet width
strip = med_s[yb - 46:yb - 14]
ext = cv2.resize(strip, (W, CAB - (yb - 14)), interpolation=cv2.INTER_LINEAR)
ext *= np.linspace(1.0, 0.86, ext.shape[0])[:, None, None]
cab = np.zeros((H, W), np.float32)
cab[yb - 14:CAB] = last[None, :]
cab_img = np.zeros_like(bg); cab_img[yb - 14:CAB] = ext
# contact shadow
sh = np.zeros((H, W), np.float32)
cv2.ellipse(sh, (537, CAB + 4), (322, 22), 0, 0, 360, 1.0, -1)
sh = cv2.GaussianBlur(sh, (0, 0), 16)
bg = bg * (1 - 0.42 * sh[..., None])
static = bg * (1 - cab[..., None]) + cab_img * cab[..., None]

# where the filmed frame is used: everything inside the filmed area, except the floor/wall slivers next to the booth in
# the lower part (there only the cabinet itself is kept, with its real edge); top/left/right borders feathered on the wall
edge = np.minimum.reduce([cx - x0, x1 - 1 - cx, cy - y0])
feather = np.clip(edge / 36.0, 0, 1) ** 1.5
use = inside * feather
lower = cy >= 1250
cabm = np.clip((booth_s - 0.5) * 6 + 0.5, 0, 1)
use = np.where(lower, inside * cabm, use)
side = (cy >= 1095) & ((cx < 238) | (cx > 834))          # wall/shadow slivers beside the booth: room extension instead
use = np.where(side, 0.0, use)
use[cy >= yb - 8] = 0                                     # below: cabinet extension / floor only
use = cv2.GaussianBlur(use, (0, 0), 0.8)[..., None]

# look: the room reads white (wall L* ~70 -> ~82), blacks kept; soft enough to sit next to the 720p AI worlds
lut_x = np.linspace(0, 1, 256, dtype=np.float32)
curve = np.interp(lut_x, [0, 0.05, 0.25, 0.55, 0.70, 0.86, 1.0], [0, 0.045, 0.24, 0.62, 0.845, 0.95, 1.0]).astype(np.float32)
def look(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
    lab[..., 0] = np.interp(lab[..., 0] / 100, lut_x, curve) * 100
    lab[..., 1:] *= np.where(lab[..., :1] > 70, 0.55, 0.92)          # neutral, clean white wall; skin keeps its colour
    return cv2.cvtColor(lab, cv2.COLOR_Lab2BGR)

ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr48le", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                       "-c:v", "libx264", "-preset", "slow", "-crf", "8", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
                       "-color_trc", "bt709", "-colorspace", "bt709", "-vf", "scale=out_color_matrix=bt709:out_range=tv", OUT],
                      stdin=subprocess.PIPE)
idx = [int(round(FIRST + k * STEP)) for k in range(N)]
sel = "+".join(f"eq(n\\,{i})" for i in sorted(set(idx)))
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{R}/src/music_src.mov", "-vf", f"select='{sel}'", "-vsync", "0",
                      "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True, check=True).stdout
frames = dict(zip(sorted(set(idx)), np.frombuffer(raw, np.uint8).reshape(-1, 1920, 1080, 3)))
rng = np.random.default_rng(7)
for k, i in enumerate(idx):
    f = frames[i].astype(np.float32) / 255
    fs = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_AREA)
    img = static * (1 - use) + fs * use
    img = cv2.GaussianBlur(img, (0, 0), 0.55)
    img = look(img)
    n = cv2.resize(rng.standard_normal((H // 2, W // 2)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    img = np.clip(img + n[..., None] * 0.010, 0, 1)
    ff.stdin.write((img * 65535 + 0.5).astype("<u2").tobytes())
ff.stdin.close(); ff.wait()
print("plate", OUT, len(idx), "frames, raw", idx[0], "->", idx[-1])
