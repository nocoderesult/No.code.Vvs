"""Preview the reel-3 grade on 16-bit Log stills as an iPhone would show it (BT.709 inverse-OETF decode).
usage: grade_preview.py out.jpg log1.png [log2.png ...] [--set key=val ...]"""
import json, sys
import cv2
import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import look3

args = [a for a in sys.argv[1:] if not a.startswith("--set")]
sets = [a.split("=", 1) for a in sys.argv[1:] if a.startswith("--set")]
p = dict(look3.P)
for k, v in sets:
    k = k[len("--set"):].lstrip(":")
    p[k] = json.loads(v)
out, ins = args[0], args[1:]


def apple_view(code):
    """BT.709 code -> what an Apple player emits (inverse OETF) -> sRGB for viewing here."""
    code = np.clip(code, 0, 1)
    lin = np.where(code < 0.081, code / 4.5, ((code + 0.099) / 1.099) ** (1 / 0.45))
    srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)
    return srgb


tiles = []
for path in ins:
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)[:, :, ::-1].astype(np.float64) / 65535
    small = cv2.resize(im, (540, 960), interpolation=cv2.INTER_AREA)
    graded = look3.transform(small.reshape(-1, 3), p).reshape(small.shape)
    tiles.append(apple_view(small))           # log, as-is (washed)
    tiles.append(apple_view(graded))
    # stats: skin patch from the face box if a sidecar exists
    try:
        fx, fy, fw, fh = json.load(open(path + ".face.json"))
        H, W = graded.shape[:2]
        roi = graded[int((fy + 0.45 * fh) * H):int((fy + 0.75 * fh) * H), int((fx + 0.25 * fw) * W):int((fx + 0.75 * fw) * W)]
        m = np.median(roi.reshape(-1, 3), 0)
        y = m @ [0.2126, 0.7152, 0.0722]
        cb, cr = (m[2] - y) / 1.8556, (m[0] - y) / 1.5748
        ang = np.degrees(np.arctan2(cr, cb)) % 360
        print(f"{path.rsplit('/', 1)[-1]}: skin code {np.round(m, 3)}  luma {y * 100:.0f} IRE  vectorscope angle {ang:.0f} deg (skin line ~123)")
    except FileNotFoundError:
        pass
row = np.concatenate(tiles, 1)
cv2.imwrite(out, (np.clip(row, 0, 1)[:, :, ::-1] * 255 + 0.5).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
print("wrote", out)
