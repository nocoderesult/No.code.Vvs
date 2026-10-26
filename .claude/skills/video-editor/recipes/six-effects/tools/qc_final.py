"""QC of a delivered reel: stream facts, loudness, black/frozen-frame scan and a timed contact sheet.
usage: qc_final.py video.mp4 sheet.jpg [t1,t2,...]"""
import json, re, subprocess, sys
import cv2
import numpy as np

path, sheet = sys.argv[1], sys.argv[2]
times = [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
                               capture_output=True, text=True).stdout)
v = next(s for s in pr["streams"] if s["codec_type"] == "video")
a = next(s for s in pr["streams"] if s["codec_type"] == "audio")
print(f"video {v['codec_name']} {v.get('profile')} L{v.get('level')} {v['width']}x{v['height']} {v['r_frame_rate']} "
      f"{v.get('pix_fmt')} prim={v.get('color_primaries')} trc={v.get('color_transfer')} mat={v.get('color_space')} "
      f"frames={v.get('nb_frames')} dur={float(v['duration']):.3f}s")
print(f"audio {a['codec_name']} {a['sample_rate']} Hz ch={a['channels']} dur={float(a['duration']):.3f}s "
      f"bitrate={int(a.get('bit_rate', 0)) // 1000} kb/s")
print(f"file {int(pr['format']['size']) / 1e6:.1f} MB, total {int(pr['format']['bit_rate']) / 1e6:.1f} Mb/s")
p = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-map", "0:a", "-af", "ebur128=peak=true", "-f", "null", "-"],
                   capture_output=True, text=True)
I = re.findall(r"I:\s+(-?[\d.]+) LUFS", p.stderr)[-1]
TP = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", p.stderr)[-1]
print(f"loudness {I} LUFS, true peak {TP} dBTP")
# decode at 270x480 for the scans
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", "scale=270:480", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                     capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, 480, 270, 3)
means = fr.reshape(len(fr), -1).mean(1)
diffs = np.abs(np.diff(fr.astype(np.int16), axis=0)).reshape(len(fr) - 1, -1).mean(1)
print(f"decoded {len(fr)} frames; darkest frame mean {means.min():.1f}; "
      f"identical consecutive frames: {int((diffs < 0.05).sum())}")
if times is None:
    times = list(np.arange(0.2, len(fr) / 30, 1.5))
tiles = []
for t in times:
    k = min(int(round(t * 30)), len(fr) - 1)
    im = cv2.cvtColor(fr[k], cv2.COLOR_RGB2BGR).copy()
    cv2.putText(im, f"{t:.2f}", (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    tiles.append(im)
cols = 8
while len(tiles) % cols:
    tiles.append(np.zeros_like(tiles[0]))
rows = [np.concatenate(tiles[i:i + cols], 1) for i in range(0, len(tiles), cols)]
cv2.imwrite(sheet, np.concatenate(rows, 0), [cv2.IMWRITE_JPEG_QUALITY, 88])
print("sheet", sheet)
