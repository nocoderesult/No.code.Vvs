"""Prepare data for the Remotion reel: word captions on the OUTPUT timeline + face-aware sticker spots.
usage: prep.py words.json cuts.json base.mp4 out_dir
"""
import json, os, subprocess, sys
import cv2
import numpy as np

words_p, cuts_p, base, out_dir = sys.argv[1:5]
FPS, W, H = 30, 1080, 1920
words = json.load(open(words_p))["words"]
cuts = json.load(open(cuts_p))

# ---- words -> output time
out_words, t_out = [], 0.0
for si, seg in enumerate(cuts["segments"]):
    for w in words:
        if w["src"] == seg["src"] and seg["s"] - 0.02 <= w["s"] < seg["e"]:
            s = t_out + (w["s"] - seg["s"]); e = t_out + (min(w["e"], seg["e"]) - seg["s"])
            out_words.append({"text": w["w"].strip(), "start": round(s, 3), "end": round(max(e, s + 0.12), 3), "seg": si})
    t_out += seg["e"] - seg["s"]

# ---- chunk into 1-3 words, <= 16 chars, break at punctuation / segment change / gaps
chunks, cur = [], []
def flush():
    if cur:
        chunks.append({"words": list(cur), "start": cur[0]["start"], "end": cur[-1]["end"]})
        cur.clear()
for w in out_words:
    txt = w["text"].upper().strip(",.!?…")
    item = {"text": txt, "start": w["start"], "end": w["end"]}
    if cur and (w["seg"] != cur[-1]["seg"] or w["start"] - cur[-1]["end"] > 0.30 or len(cur) >= 3
                or len(" ".join(x["text"] for x in cur) + " " + txt) > 16):
        flush()
    item["seg"] = w["seg"]
    cur.append(item)
    if w["text"].endswith((",", ".", "!", "?", "…")):
        flush()
flush()
for i, c in enumerate(chunks):          # hold a chunk until the next one if the gap is short
    nxt = chunks[i + 1]["start"] if i + 1 < len(chunks) else t_out
    c["end"] = round(min(nxt, c["end"] + 0.35), 3)
    for w in c["words"]:
        w.pop("seg", None)

# ---- face boxes per frame
YUNET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "models", "face_detection_yunet_2023mar.onnx")
det = cv2.FaceDetectorYN.create(YUNET, "", (270, 480), 0.6)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", base, "-vf", "scale=270:480,format=bgr24", "-f", "rawvideo", "-"],
                     capture_output=True).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, 480, 270, 3)
faces = []
for f in frames:
    _, d = det.detect(f)
    if d is None or len(d) == 0:
        faces.append(None)
    else:
        x, y, w, h = (max(d, key=lambda r: r[2] * r[3])[:4] * 4.0).tolist()
        faces.append([round(x), round(y), round(w), round(h)])

json.dump({"fps": FPS, "duration": round(t_out, 3), "chunks": chunks, "faces": faces},
          open(f"{out_dir}/data.json", "w"), ensure_ascii=False, indent=1)
print(f"{len(out_words)} words, {len(chunks)} chunks, {sum(f is not None for f in faces)}/{len(faces)} frames with a face")
for c in chunks:
    print(f"  {c['start']:6.2f}-{c['end']:6.2f}  " + " ".join(w["text"] for w in c["words"]))
