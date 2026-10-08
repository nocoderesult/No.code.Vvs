#!/usr/bin/env python3
"""Analyse a clip for reframing (e.g. 16:9 -> 9:16): face-tracked crop path -> track.json.

YuNet face detector (OpenCV, bundled model; Haar cascade fallback) sampled at --sample-fps, largest face
with continuity, median filter -> per-frame interpolation -> deadzone -> offline Gaussian smoothing (no lag).
Times are real timestamps (VFR-safe); OpenCV auto-rotates like ffmpeg so coordinates match.
render_cuts.py turns the path into an ffmpeg sendcmd-driven crop. It also stores the median face
position, used to anchor punch-in zooms on the face instead of the frame centre.

Measured: detection+smoothing ~5 s per 37 s of 1080p; deadzone 0.02*W + sigma 0.5 s tracks a moving
subject within ~10-20 px; use --deadzone 0.06 for a near-static talking head (rock-steady frame).

Examples:
  reframe.py clip.mp4 -o work/track_0.json                 # for 9:16 output
  reframe.py clip.mp4 -o t.json --target 1:1 --deadzone 0.06
  reframe.py clip.mp4 -o t.json --preview work/rf_preview.mp4
"""
import argparse
import os

os.environ.setdefault("OPENCV_LOG_LEVEL", "ERROR")
import cv2  # noqa: E402
import numpy as np

import vcommon as vc


def detect(path, sample_fps=6.0, det_w=640):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise vc.EditError(f"OpenCV cannot open {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ok, fr = cap.read()
    if ok:  # actual decoded (auto-rotated) size
        H, W = fr.shape[:2]
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    scale = det_w / W
    dsize = (det_w, int(round(H * scale)))
    model = vc.model_path("yunet")
    yunet = cv2.FaceDetectorYN.create(model, "", dsize, score_threshold=0.6, nms_threshold=0.3, top_k=20) if model else None
    haar = None
    if yunet is None:
        vc.log("warning: YuNet unavailable, using Haar cascade (less accurate)")
        haar = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml"))
    step = max(1, round(fps / sample_fps))
    T, X, Y, S = [], [], [], []
    i, sampled, prev = 0, 0, None
    while True:
        if not cap.grab():
            break
        if i % step == 0:
            t = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            ok, fr = cap.retrieve()
            if not ok:
                break
            sampled += 1
            small = cv2.resize(fr, dsize, interpolation=cv2.INTER_AREA)
            faces = []
            if yunet is not None:
                _, f = yunet.detect(small)
                faces = [] if f is None else [(x[0], x[1], x[2], x[3], x[14]) for x in f]
            else:
                g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
                faces = [(x, y, w, h, 1.0) for x, y, w, h in haar.detectMultiScale(g, 1.1, 5, minSize=(30, 30))]
            if faces:
                def score(f):  # big faces win; continuity bonus near the previous position
                    cx = f[0] + f[2] / 2
                    near = 0 if prev is None else abs(cx / scale - prev) / W
                    return f[2] * f[3] * (1.0 - min(near, 0.5))
                f = max(faces, key=score)
                cx, cy = (f[0] + f[2] / 2) / scale, (f[1] + f[3] / 2) / scale
                T.append(t); X.append(cx); Y.append(cy); S.append(f[3] / scale)
                prev = cx
        i += 1
    cap.release()
    return dict(fps=fps, W=W, H=H, frames=i, sampled=sampled, t=np.array(T), x=np.array(X), y=np.array(Y),
                s=np.array(S))


def smooth(ts, vs, times, span, crop, sigma_s, deadzone, fps, med_k=5, pos=0.5):
    """Return crop offsets (top-left) along one axis for each time in `times`; the subject is placed at
    `pos` of the crop (0.5 = centred; 0.38 vertically = classic headroom)."""
    if len(ts) == 0:
        return np.full(len(times), (span - crop) / 2)
    if len(vs) >= med_k:
        pad = med_k // 2
        vp = np.pad(vs, pad, mode="edge")
        vs = np.array([np.median(vp[k:k + med_k]) for k in range(len(vs))])
    c = np.interp(times, ts, vs)
    tgt = np.empty_like(c)
    cur = c[0]
    dz = deadzone * span
    for k, v in enumerate(c):
        if abs(v - cur) > dz:
            cur = v - np.sign(v - cur) * dz
        tgt[k] = cur
    sg = max(1, int(sigma_s * fps))
    kk = np.arange(-3 * sg, 3 * sg + 1)
    g = np.exp(-0.5 * (kk / sg) ** 2)
    g /= g.sum()
    sm = np.convolve(np.pad(tgt, 3 * sg, mode="edge"), g, mode="valid")
    return np.clip(sm - crop * pos, 0, span - crop)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("-o", "--out", required=True, help="output track.json")
    ap.add_argument("--target", default="9:16", help="output aspect W:H (9:16, 1:1, 4:5, 16:9)")
    ap.add_argument("--sample-fps", type=float, default=6.0, help="face detections per second (6)")
    ap.add_argument("--sigma", type=float, default=0.5, help="smoothing (s): higher = calmer camera (0.5)")
    ap.add_argument("--deadzone", type=float, default=0.02, help="fraction of width the face may move "
                    "before the crop follows (0.02 tracking, 0.06 static talking head)")
    ap.add_argument("--face-pos", type=float, default=0.38, help="vertical crops (9:16 -> 1:1/4:5/16:9): face "
                    "centre at this fraction of the frame height (0.38 = natural headroom)")
    ap.add_argument("--preview", help="render a quick low-res preview MP4 of the tracked crop")
    a = ap.parse_args()

    info = vc.media_info(a.input)
    tw, th = [float(x) for x in a.target.split(":")]
    d = detect(a.input, a.sample_fps)
    W, H = d["W"], d["H"]
    fps = float(vc.frac(info["fps"]))
    ratio = len(d["t"]) / max(1, d["sampled"])
    tgt = tw / th
    if W / H > tgt:  # source wider -> crop width, track x
        axis, cw, ch = "x", int(round(H * tgt / 2) * 2), H
        span, crop, vals = W, cw, d["x"]
    else:            # source taller -> crop height, track y
        axis, cw, ch = "y", W, int(round(W / tgt / 2) * 2)
        span, crop, vals = H, ch, d["y"]
    n = max(1, int(info["duration"] * fps))
    times = np.arange(n) / fps
    pos = smooth(d["t"], vals, times, span, crop, a.sigma, a.deadzone, fps, pos=0.5 if axis == "x" else a.face_pos)
    fy = float(np.median(d["y"]) / H) if len(d["y"]) else 0.4
    fx = float(np.median(d["x"]) / W) if len(d["x"]) else 0.5
    fh = float(np.median(d["s"]) / H) if len(d["s"]) else 0.0
    rec = "track" if ratio >= 0.5 else ("track (partial)" if ratio >= 0.25 else "blur")
    out = {"source": info["path"], "name": info["name"], "W": W, "H": H, "fps": str(vc.frac(info["fps"])),
           "target": a.target, "axis": axis, "crop_w": cw, "crop_h": ch,
           "detect_ratio": round(ratio, 3), "detections": int(len(d["t"])), "recommend": rec,
           "face_x": round(fx, 4), "face_y": round(fy, 4), "face_h": round(fh, 4),
           "face_pos": a.face_pos if axis == "y" else 0.5,
           "path_fps": str(vc.frac(info["fps"])), "pos": [int(round(v)) for v in pos],
           "det_t": [round(float(v), 3) for v in d["t"]], "det_v": [round(float(v), 1) for v in vals]}
    vc.save_json(out, a.out)
    span_px = (max(out["pos"]) - min(out["pos"])) if out["pos"] else 0
    print(f"{info['name']}: {W}x{H} -> crop {cw}x{ch} along {axis}; faces in {ratio:.0%} of samples "
          f"({len(d['t'])}/{d['sampled']}), median face at x={fx:.2f} y={fy:.2f} h={fh:.2f}; "
          f"crop travel {span_px}px; recommend: {rec}")
    if a.preview:
        cmds = a.out + ".sendcmd"
        with open(cmds, "w") as f:
            last = None
            for k, v in enumerate(out["pos"]):
                if v != last:
                    f.write(f"{k / fps:.4f} crop@rf {axis} {v};\n")
                    last = v
        x0, y0 = (out["pos"][0], 0) if axis == "x" else (0, out["pos"][0])
        pw = 360 if axis == "x" else 640
        vc.run(vc.ffmpeg_cmd("-i", a.input, "-vf", f"fps={info['fps']},sendcmd=f='{cmds}',crop@rf=w={cw}:h={ch}:x={x0}:y={y0},"
                             f"scale={pw}:-2", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", a.preview))
        print(f"preview: {a.preview}")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
