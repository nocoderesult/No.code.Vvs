"""Person matte (Robust Video Matting, CPU) for every source frame the timeline uses.
Frames are decoded with the grade applied (RVM was trained on display-referred video), at 1080x1920.
Each contiguous source run gets 8 warm-up frames so the recurrent state is settled.
usage: matte.py reel3_dir [--only A,B,...]"""
import json, os, subprocess, sys, time
import cv2
import numpy as np
import torch

R = sys.argv[1]
only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
FF = os.environ.get("FFMPEG", "ffmpeg")
W, H, FPS = 1080, 1920, 30
out_dir = f"{R}/work/matte"
os.makedirs(out_dir, exist_ok=True)
torch.set_num_threads(4)
model = torch.jit.load(f"{R}/models/rvm_mobilenetv3_fp32.torchscript").eval()

tl = json.load(open(f"{R}/work/timeline.json"))
need = sorted({f["src"] for f in tl["frames"] if only is None or f["seg"] in only})
runs, cur = [], [need[0]]
for s in need[1:]:
    if s == cur[-1] + 1:
        cur.append(s)
    else:
        runs.append(cur); cur = [s]
runs.append(cur)
print(f"{len(need)} frames in {len(runs)} runs", flush=True)

t0 = time.time(); done = 0
for run in runs:
    if all(os.path.exists(f"{out_dir}/m_{s:05d}.png") for s in run):
        continue
    a = max(run[0] - 8, 0); b = run[-1] + 1
    cmd = [FF, "-v", "error", "-ss", f"{a / FPS:.4f}", "-i", f"{R}/src/raw.mov", "-frames:v", str(b - a),
           "-vf", f"scale={W}:{H}:in_color_matrix=bt2020:in_range=tv:flags=bicubic,format=rgb48le,"
                  f"lut3d={R}/lut/reel3_v3_33.cube:interp=tetrahedral,format=rgb24",
           "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    rec = [None] * 4
    k = a
    with torch.no_grad():
        while True:
            buf = p.stdout.read(W * H * 3)
            if len(buf) < W * H * 3:
                break
            x = torch.from_numpy(np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()).permute(2, 0, 1)[None].float() / 255
            fgr, pha, *rec = model(x, *rec, 0.25)
            if k >= run[0]:
                al = (pha[0, 0].numpy() * 255 + 0.5).astype(np.uint8)
                cv2.imwrite(f"{out_dir}/m_{k:05d}.png", al)
                done += 1
            k += 1
    p.wait()
    el = time.time() - t0
    print(f"run {run[0]}-{run[-1]} ok  ({done} frames, {el / max(done, 1):.2f} s/frame)", flush=True)
print("matte done", round(time.time() - t0), "s")
