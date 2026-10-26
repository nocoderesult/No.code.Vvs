"""Plot the voice energy (10 ms, dB) with word boxes and the planned cut segments, 4 rows.
usage: envplot.py voice.wav words.json edl.json out.png"""
import json, subprocess, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

wav, words_p, edl_p, out = sys.argv[1:5]
sr = 48000
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-ac", "1", "-ar", str(sr), "-af", "highpass=f=120,lowpass=f=5000",
                      "-f", "f32le", "-"], capture_output=True).stdout
x = np.frombuffer(raw, np.float32)
hop = sr // 100
n = len(x) // hop
E = 10 * np.log10((x[:n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12)
t = np.arange(n) / 100
words = json.load(open(words_p))["words"]
segs = json.load(open(edl_p))["segments"] if edl_p != "-" else []

rows = [(15, 29.5), (29.5, 44), (44, 58.5), (58.5, 73)]
fig, axes = plt.subplots(len(rows), 1, figsize=(30, 14))
for ax, (a, b) in zip(axes, rows):
    m = (t >= a) & (t < b)
    ax.plot(t[m], E[m], lw=0.8, color="k")
    ax.set_xlim(a, b); ax.set_ylim(-90, -20)
    ax.set_xticks(np.arange(np.ceil(a * 2) / 2, b, 0.5))
    ax.tick_params(labelsize=7)
    ax.grid(alpha=0.3)
    for w in words:
        if a <= w["s"] < b:
            ax.axvspan(w["s"], w["e"], ymin=0.86, ymax=0.97, color="tab:blue", alpha=0.25)
            ax.text(w["s"], -24, w["w"], fontsize=8, rotation=0)
    for s in segs:
        if s["out"] > a and s["in"] < b:
            ax.axvspan(s["in"], s["out"], ymin=0, ymax=0.08, color="tab:red", alpha=0.6)
            ax.text(max(s["in"], a), -88, s["id"], fontsize=9, color="tab:red")
plt.tight_layout()
plt.savefig(out, dpi=70)
print("wrote", out)
