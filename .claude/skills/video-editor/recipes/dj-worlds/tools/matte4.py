"""Hero-on-black matte for the raw 120 fps take: RVM person alpha (CPU) + a static booth mask.
usage: matte4.py reel4_dir first last   (120 fps frame indices, inclusive) -> work/matte/a_XXXXX.png"""
import os, subprocess, sys
import cv2
import numpy as np
import torch

R, A, B = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
W, H = 1080, 1920
OUT = f"{R}/work/matte"
MODEL = os.environ.get("RVM_MODEL", f"{R}/models/rvm_mobilenetv3_fp32.torchscript")   # Robust Video Matting, torchscript fp32
SRC = f"{R}/src/music_src.mov"


def decode(sel, n):
    vf = f"select='{sel}',scale={W}:{H}:flags=bicubic,format=rgb24"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-vf", vf, "-vsync", "0", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)[:n]


# --- static booth mask from a temporal median (camera is locked off)
med = np.median(decode("not(mod(n\\,60))", 40), axis=0).astype(np.uint8)
hsv = cv2.cvtColor(med, cv2.COLOR_RGB2HSV)
dark = (hsv[..., 2] < 95).astype(np.uint8)
dark[:1150] = 0                                       # booth lives below the DJ's chest
yy, xx = np.mgrid[:H, :W]
dark[(yy < 1252) & (xx > 270) & (xx < 830)] = 0       # above the deck line only the side posts / headphones belong to the booth
n, lab, st, _ = cv2.connectedComponentsWithStats(dark, 8)
k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
booth = (lab == k).astype(np.uint8) * 255
booth = cv2.morphologyEx(booth, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))
cnts, _ = cv2.findContours(booth, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
booth = np.zeros_like(booth)
cv2.drawContours(booth, cnts, -1, 255, -1)            # fill holes (LEDs, knobs)
booth = cv2.GaussianBlur(booth, (0, 0), 1.5)
cv2.imwrite(f"{OUT}/booth.png", booth)
cv2.imwrite(f"{OUT}/median.jpg", cv2.cvtColor(med, cv2.COLOR_RGB2BGR))

# --- RVM person alpha with warm-up so the recurrent state is settled
torch.set_num_threads(4)
model = torch.jit.load(MODEL).eval()
w0 = max(A - 24, 0)
frames = decode(f"between(n\\,{w0}\\,{B})", B - w0 + 1)
rec = [None] * 4
with torch.no_grad():
    for i, fr in enumerate(frames):
        x = torch.from_numpy(fr.copy()).permute(2, 0, 1)[None].float() / 255
        fgr, pha, *rec = model(x, *rec, 0.25)
        idx = w0 + i
        if idx >= A:
            p = (pha[0, 0].numpy() * 255 + 0.5).astype(np.uint8)
            cv2.imwrite(f"{OUT}/r_{idx:05d}.png", p)       # person only; booth.png is combined at composite time
print("matte frames", A, "-", B, "ok; booth px", int((booth > 127).sum()))
