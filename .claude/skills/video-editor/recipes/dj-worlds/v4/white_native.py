"""White take at its NATIVE framing (nothing synthesized), 1.5x lanczos (1620x2880) so Remotion punch-ins up to 1.5x
stay at source sharpness, 120 fps kept for slow motion, same clean-white look as V3.
usage: white_native.py reel4_dir out.mp4 first_raw120 last_raw120"""
import subprocess, sys
import cv2
import numpy as np
R, OUT, A, B = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
W, H = 1620, 2880
lut_x = np.linspace(0, 1, 256, dtype=np.float32)
curve = np.interp(lut_x, [0, 0.05, 0.25, 0.55, 0.70, 0.86, 1.0], [0, 0.045, 0.24, 0.62, 0.845, 0.95, 1.0]).astype(np.float32)
src = subprocess.Popen(["ffmpeg", "-v", "error", "-i", f"{R}/src/music_src.mov", "-vf",
                        f"select='between(n\\,{A}\\,{B})',scale={W}:{H}:flags=lanczos+accurate_rnd+full_chroma_int,format=bgr24",
                        "-vsync", "0", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr48le", "-s", f"{W}x{H}", "-r", "120", "-i", "-",
                       "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-pix_fmt", "yuv420p", "-g", "24",
                       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                       "-vf", "scale=out_color_matrix=bt709:out_range=tv", OUT], stdin=subprocess.PIPE)
rng = np.random.default_rng(11); n = 0
while True:
    b = src.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    f = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
    lab = cv2.cvtColor(f, cv2.COLOR_BGR2Lab)
    lab[..., 0] = np.interp(lab[..., 0] / 100, lut_x, curve) * 100
    lab[..., 1:] *= np.where(lab[..., :1] > 70, 0.55, 0.92)
    img = cv2.cvtColor(lab, cv2.COLOR_Lab2BGR)
    g = cv2.resize(rng.standard_normal((H // 3, W // 3)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    img = np.clip(img + g[..., None] * 0.008, 0, 1)
    ff.stdin.write((img * 65535 + 0.5).astype("<u2").tobytes()); n += 1
ff.stdin.close(); ff.wait(); print("white native frames", n, A, "->", B)
