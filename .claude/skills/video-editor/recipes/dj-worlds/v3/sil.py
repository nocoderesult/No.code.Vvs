"""Silhouettes (RVM alpha, 270x480 in AI geometry) for white-take frames (mapped into the AI framing) and AI frames.
usage: sil.py reel4_dir"""
import subprocess, sys
import numpy as np, torch, cv2
R = sys.argv[1]
MODEL = __import__("os").environ.get("RVM_MODEL", f"{R}/models/rvm_mobilenetv3_fp32.torchscript")
torch.set_num_threads(4)
m = torch.jit.load(MODEL).eval()
def run(path, vf, n_hint, w=540, h=960):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", vf + f",scale={w}:{h},format=rgb24", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    rec = [None] * 4; out = []
    with torch.no_grad():
        while True:
            b = p.stdout.read(w * h * 3)
            if len(b) < w * h * 3: break
            x = torch.from_numpy(np.frombuffer(b, np.uint8).reshape(h, w, 3).copy()).permute(2, 0, 1)[None].float() / 255
            fgr, pha, *rec = m(x, *rec, 0.4)
            out.append(cv2.resize(pha[0, 0].numpy(), (270, 480), interpolation=cv2.INTER_AREA))
    p.wait(); return np.array(out, np.float32)
# white take at 60 fps, placed into the AI framing: scale 0.571 about origin then translate (262,360) on a 1080x1920 canvas
s, tx, ty = 0.571, 262, 360
W = int(round(1080 * s)); Hh = int(round(1920 * s))
vfw = f"fps=60,scale={W}:{Hh},pad=1080:1920:{tx}:{ty}:color=0xC8C8C8"
white = run(f"{R}/src/music_src.mov", vfw, 834)
np.save(f"{R}/v3/matte/white60_sil.npy", white)
ai = run(f"{R}/src/clipA.mov", "scale=1080:1920", 423)
np.save(f"{R}/v3/matte/ai_sil.npy", ai)
print("white", white.shape, "ai", ai.shape)
