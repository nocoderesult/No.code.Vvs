#!/usr/bin/env python3
"""Contact sheet (grid of timestamped frames) so Claude can LOOK at footage with the Read tool.

Frames are sampled evenly (default 12), at fixed intervals (--every), at explicit times (--times),
or one per detected scene (--scenes, PySceneDetect). Optional safe-zone overlay for vertical output QC.

Examples:
  contact_sheet.py raw.mov -o sheet.jpg
  contact_sheet.py final.mp4 -o qc.jpg --n 8 --safe universal
  contact_sheet.py broll.mp4 -o scenes.jpg --scenes
  contact_sheet.py final.mp4 -o caps.jpg --times 1.2,4.5,9.0 --width 540
"""
import argparse
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import vcommon as vc
from render_cuts import TONEMAP


def grab(path, t, w, info):
    """One frame at time t (accurate seek), scaled to width w, returned as PIL image."""
    h = int(round(w * info["h"] / info["w"] / 2) * 2)
    tm = (TONEMAP + ",") if info.get("hdr") else ""  # show HDR the way the SDR export will look
    raw = vc.run_bytes(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1",
                        "-vf", f"{tm}scale={w}:{h}:flags=bicubic,format=rgb24", "-f", "rawvideo", "-"])
    if len(raw) < w * h * 3:
        return None
    return Image.fromarray(np.frombuffer(raw[: w * h * 3], np.uint8).reshape(h, w, 3))


def scene_times(path, n):
    from scenedetect import AdaptiveDetector, detect
    scenes = detect(path, AdaptiveDetector())
    sec = lambda tc: float(getattr(tc, "seconds", None) if not callable(getattr(tc, "seconds", None))
                           and getattr(tc, "seconds", None) is not None else tc.get_seconds())
    ts = [(sec(s) + sec(e)) / 2 for s, e in scenes]
    if len(ts) > n:
        idx = np.linspace(0, len(ts) - 1, n).round().astype(int)
        ts = [ts[i] for i in idx]
    return ts, [(sec(s), sec(e)) for s, e in scenes]


def draw_safe(img, platform, info):
    if info["w"] / info["h"] > 0.8 and platform not in ("youtube",):
        return img
    x0, y0, x1, y1 = vc.safe_box(platform, img.width, img.height)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    red = (255, 40, 40, 70)
    d.rectangle([0, 0, img.width, y0], fill=red)
    d.rectangle([0, y1, img.width, img.height], fill=red)
    d.rectangle([0, y0, x0, y1], fill=red)
    d.rectangle([x1, y0, img.width, y1], fill=red)
    if platform in ("tiktok", "universal"):  # right action rail below y=840
        d.rectangle([img.width * (1 - 300 / 1080), img.height * 840 / 1920, x1, y1], fill=(255, 140, 0, 60))
    d.rectangle([x0, y0, x1, y1], outline=(255, 255, 0, 200), width=2)
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def build(path, out, n=12, every=None, times=None, cols=None, width=None, safe=None, scenes=False, title=True):
    info = vc.media_info(path)
    if not info.get("has_video"):
        raise vc.EditError(f"{path} has no video stream")
    dur = info["duration"]
    vertical = info["w"] < info["h"]
    width = width or (270 if vertical else 480)
    if times:
        ts = times
    elif scenes:
        ts, sc = scene_times(path, n)
        print(f"{max(1, len(sc))} scene(s): " + (", ".join(f"{a:.2f}-{b:.2f}" for a, b in sc) or "no cuts detected"))
        if not ts:
            ts = [(k + 0.5) * dur / n for k in range(n)]
    elif every:
        ts = list(np.arange(every / 2, dur, every))
    else:
        ts = [(k + 0.5) * dur / n for k in range(n)]
    ts = [min(max(0.0, t), max(0.0, dur - 0.05)) for t in ts]
    cols = cols or (6 if vertical else 4)
    if len(ts) < cols:
        cols = max(1, len(ts))
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", max(12, width // 16))
    tiles = []
    for t in ts:
        im = grab(path, t, width, info)
        if im is None:
            continue
        if safe:
            im = draw_safe(im, safe, info)
        d = ImageDraw.Draw(im)
        label = f"{int(t // 60):02d}:{t % 60:05.2f}"
        bb = d.textbbox((6, 4), label, font=font)
        d.rectangle([bb[0] - 3, bb[1] - 2, bb[2] + 3, bb[3] + 2], fill=(0, 0, 0))
        d.text((6, 4), label, fill=(255, 255, 255), font=font)
        tiles.append(im)
    if not tiles:
        raise vc.EditError("no frames could be extracted")
    tw, th = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    head = 28 if title else 0
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 4, rows * th + (rows + 1) * 4 + head), (24, 24, 24))
    if title:
        f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        ImageDraw.Draw(sheet).text((6, 5), f"{info['name']}  {info['w']}x{info['h']}  {info['fps']}fps  "
                                   f"{dur:.2f}s", fill=(220, 220, 220), font=f2)
    for k, im in enumerate(tiles):
        r, c = divmod(k, cols)
        sheet.paste(im, (4 + c * (tw + 4), head + 4 + r * (th + 4)))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    sheet.save(out, quality=88)
    return out, ts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("-o", "--out", required=True, help="output .jpg")
    ap.add_argument("--n", type=int, default=12, help="number of evenly spaced frames (12)")
    ap.add_argument("--every", type=float, help="one frame every N seconds instead of --n")
    ap.add_argument("--times", help="comma-separated explicit times in seconds")
    ap.add_argument("--scenes", action="store_true", help="one frame per detected scene (PySceneDetect)")
    ap.add_argument("--cols", type=int, help="columns (default 6 vertical / 4 landscape)")
    ap.add_argument("--width", type=int, help="tile width px (default 270 vertical / 480 landscape)")
    ap.add_argument("--safe", choices=list(vc.SAFE_ZONES), help="draw platform safe-zone overlay (red = UI)")
    a = ap.parse_args()
    times = [float(x) for x in a.times.split(",")] if a.times else None
    out, ts = build(a.input, a.out, a.n, a.every, times, a.cols, a.width, a.safe, a.scenes)
    print(f"wrote {out} ({len(ts)} frames) -> view it with the Read tool")


if __name__ == "__main__":
    main()
