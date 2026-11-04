"""taste-distillation measurements for reel4 v2: per-segment L* distribution, contrast, background %,
chroma/hue per L* zone (median + MAD). usage: measure.py reel4_dir -> pack/grade_src.json"""
import json, subprocess, sys
import cv2
import numpy as np

R = sys.argv[1]
SEG = {  # per video: name: (file, first frame, last frame, fps) - clean frames only (skip AI morphs between worlds)
    "raw": ("src/music_src.mov", 0, 1660, 120),
    "w1_foc": ("src/clipA.mov", 2, 75, 30),
    "w2_noapte": ("src/clipA.mov", 76, 178, 30),
    "w3_ceata": ("src/clipA.mov", 182, 250, 30),
    "w4_ocean": ("src/clipA.mov", 288, 342, 30),
    "w5_apus": ("src/clipA.mov", 352, 422, 30),
}
ZONES = [0, 15, 35, 55, 75, 100]


def frames(path, a, b, fps, step):
    vf = f"select='between(n\\,{a}\\,{b})*not(mod(n-{a}\\,{step}))',scale=360:640:flags=area"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", vf, "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 640, 360, 3)


def mad(x):
    m = np.median(x)
    return float(np.median(np.abs(x - m)))


out = {}
for name, (f, a, b, fps) in SEG.items():
    fr = frames(f"{R}/{f}", a, b, fps, 4 if fps == 120 else 2)
    lab = np.concatenate([cv2.cvtColor(x.astype(np.float32) / 255, cv2.COLOR_BGR2Lab).reshape(-1, 3) for x in fr])
    L, A, B = lab[:, 0], lab[:, 1], lab[:, 2]
    C = np.hypot(A, B)
    zones = []
    for z0, z1 in zip(ZONES[:-1], ZONES[1:]):
        m = (L >= z0) & (L < z1)
        if m.sum() < 500:
            zones.append({"L": [z0, z1], "share": float(m.mean()), "a": None, "b": None, "C": None})
            continue
        zones.append({"L": [z0, z1], "share": round(float(m.mean()), 4),
                      "a": round(float(np.median(A[m])), 2), "b": round(float(np.median(B[m])), 2),
                      "C": round(float(np.median(C[m])), 2), "C_mad": round(mad(C[m]), 2),
                      "hue_deg": round(float(np.degrees(np.arctan2(np.median(B[m]), np.median(A[m]))) % 360), 1)})
    out[name] = {
        "frames": [a, b], "fps": fps, "n_sampled": len(fr),
        "L_pct": {p: round(float(np.percentile(L, p)), 2) for p in (1, 5, 25, 50, 75, 95, 99)},
        "contrast_Lstd": round(float(L.std()), 2),
        "background_pct_Llt10": round(float((L < 10).mean() * 100), 2),
        "chroma_median": round(float(np.median(C)), 2),
        "zones": zones,
    }
    print(f"{name:10s} L p1/50/99 {out[name]['L_pct'][1]:5.1f}/{out[name]['L_pct'][50]:5.1f}/{out[name]['L_pct'][99]:5.1f}"
          f"  std {out[name]['contrast_Lstd']:5.1f}  bg% {out[name]['background_pct_Llt10']:5.1f}  C {out[name]['chroma_median']:5.1f}  "
          + " ".join(f"[{z['L'][0]}-{z['L'][1]}:{z['share']:.2f} C{z['C']} h{z.get('hue_deg')}]" for z in zones))
json.dump(out, open(f"{R}/pack/grade_src.json", "w"), indent=1)
