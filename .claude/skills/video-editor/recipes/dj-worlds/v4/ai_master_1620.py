"""AI worlds master for V3: lanczos 720->1080 + mild CAS, the measured per-world grade from the style pack (no bloom,
no halation), grade parameters cross-faded through the source's own fog->water transition, light grain.
usage: ai_master.py reel4_dir out.mp4"""
import subprocess, sys
import cv2
import numpy as np
R, OUT = sys.argv[1], sys.argv[2]
sys.path.insert(0, f"{R}/tools")
import grade4 as G
W, H = 1620, 2880
def world_weights(a):
    """(world, weight) list for AI frame a; transitions blend the two grades."""
    if a <= 75: return [("w1_foc", 1.0)]
    if a <= 178: return [("w2_noapte", 1.0)]
    if a < 250: return [("w3_ceata", 1.0)]
    if a < 290:
        u = (a - 250) / 40.0; return [("w3_ceata", 1 - u), ("w4_ocean", u)]
    if a <= 343: return [("w4_ocean", 1.0)]
    if a < 352:
        u = (a - 343) / 9.0; return [("w4_ocean", 1 - u), ("w5_apus", u)]
    return [("w5_apus", 1.0)]
src = subprocess.Popen(["ffmpeg", "-v", "error", "-i", f"{R}/src/clipA.mov", "-vf",
                        "scale=1620:2880:flags=lanczos+accurate_rnd+full_chroma_int,cas=0.35,format=rgb24", "-f", "rawvideo", "-"],
                       stdout=subprocess.PIPE)
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb48le", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                       "-c:v", "libx264", "-preset", "slow", "-crf", "8", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
                       "-color_trc", "bt709", "-colorspace", "bt709", "-vf", "scale=out_color_matrix=bt709:out_range=tv", OUT],
                      stdin=subprocess.PIPE)
a = 0
while True:
    b = src.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    f = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
    img = sum(w * G.grade_world(f, k) for k, w in world_weights(a))
    img = G.grain(img, seed=500 + a, amount=0.012)
    ff.stdin.write((np.clip(img, 0, 1) * 65535 + 0.5).astype("<u2").tobytes())
    a += 1
ff.stdin.close(); ff.wait(); print("ai master frames:", a)
