#!/usr/bin/env python3
"""Cover / thumbnail from the edit: picks the best face frame of the KEPT footage and adds the title.

Candidates: ~2 frames per output second, taken from the source clips at the kept (cuts.json) times, framed like
the render (face track crop for 16:9 -> 9:16), so no burned captions end up on the cover. Each is scored with
YuNet: a face must be found; then sharpness (Laplacian variance of the face), eyes open (edge energy around the
eye landmarks, low when blinking), detector confidence and a face size that reads on a phone.
Writes (in -o OUTDIR):
  cover_9x16.jpg   1080x1920 Reels/TikTok cover, title in white boxes inside the 3:4 profile-grid area
                   (y 240-1680) and clear of the face            (vertical formats)
  thumb_16x9.jpg   1280x720 YouTube thumbnail, big outlined title on the side away from the face (16:9)
  cover_frame.jpg  the chosen frame without text (to use your own design)
Look at the result (Read) before sending; pass --at SECONDS to force a moment.

Examples:
  cover.py work/cuts.json -o out --format reels --track 0=work/track_0.json --title "3 GREȘELI LA MONTAJ"
  cover.py work/cuts.json -o out --format youtube --title "Cum editezi un vlog în 10 minute"
"""
import argparse
import os

os.environ.setdefault("OPENCV_LOG_LEVEL", "ERROR")
import cv2  # noqa: E402
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import render_cuts as rc
import vcommon as vc
from captions import balance
from contact_sheet import grab


def candidates(cuts, n_per_s=2.0, max_n=60):
    fps = vc.frac(cuts["fps"])
    segs = vc.align_segments(cuts["segments"], fps)
    total = float(sum(g["E"] - g["S"] for g in segs))
    n = int(min(max_n, max(6, total * n_per_s)))
    out, acc = [], 0.0
    times = [(k + 0.5) * total / n for k in range(n)]
    for g in segs:
        d = float(g["E"] - g["S"])
        for t in times:
            if acc + 0.25 <= t < acc + d - 0.25:
                out.append((t, g["src"], float(g["S"]) + t - acc))
        acc += d
    return out, total


def frame_for(info, src_t, W, H, track):
    """Source frame at src_t framed for a WxH canvas like the render does (face-track crop when the source is
    wider; 'wide' framing with blurred fill for close-up selfies)."""
    sw, sh = info["w"], info["h"]
    im = grab(info["path"], src_t, min(sw, 1920) // 2 * 2, info)
    if im is None:
        return None
    k = im.width / sw
    if abs(sw / sh - W / H) < 0.01:
        return im.resize((W, H), Image.LANCZOS)
    if sw / sh > W / H:
        if track and track.get("axis") == "x" and track.get("pos"):
            tf = float(vc.frac(track.get("path_fps", info["fps"])))
            i = min(len(track["pos"]) - 1, max(0, int(src_t * tf)))
            cx = track["pos"][i] + track["crop_w"] / 2
        else:
            cx = sw / 2
        _, _, _, _, mode = rc.plan_reframe(info, W, H, "auto", track) if track else (0, 0, 0, 0, "center")
        if mode == "wide":
            kk, cw, bh, top = rc.wide_geometry(info, W, H, track)
            x0 = max(0, min(sw - cw, cx - cw / 2))
            fg = im.crop((int(x0 * k), 0, int((x0 + cw) * k), im.height)).resize((W, bh), Image.LANCZOS)
            sm = im.copy()
            sm.thumbnail((W // 4, H // 4))
            r = max(W / 4 / sm.width, H / 4 / sm.height)
            sm = sm.resize((max(1, int(sm.width * r + 1)), max(1, int(sm.height * r + 1))))
            l, t_ = (sm.width - W // 4) // 2, (sm.height - H // 4) // 2
            bg = sm.crop((l, t_, l + W // 4, t_ + H // 4)).filter(ImageFilter.GaussianBlur(12)).resize((W, H))
            bg = Image.eval(bg, lambda v: int(v * 0.88))
            bg.paste(fg, (0, top))
            return bg
        cw = sh * W / H
        x0 = max(0, min(sw - cw, cx - cw / 2))
        box = (x0 * k, 0, (x0 + cw) * k, im.height)
    else:
        ch = sw * H / W
        y0 = max(0, min(sh - ch, sh * 0.42 - ch * 0.42))
        box = (0, y0 * k, im.width, (y0 + ch) * k)
    return im.crop(tuple(int(round(v)) for v in box)).resize((W, H), Image.LANCZOS)


def score_faces(imgs):
    model = vc.model_path("yunet")
    if not model:
        raise vc.EditError("YuNet face model unavailable")
    rows = []
    for t, im in imgs:
        bgr = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
        sc = 640 / bgr.shape[1]
        small = cv2.resize(bgr, (640, int(round(bgr.shape[0] * sc))), interpolation=cv2.INTER_AREA)
        det = cv2.FaceDetectorYN.create(model, "", (small.shape[1], small.shape[0]), score_threshold=0.6)
        _, f = det.detect(small)
        if f is None or not len(f):
            continue
        f = max(f, key=lambda r: r[2] * r[3]) / np.array([sc] * 14 + [1])
        x, y, w, h = f[:4]
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        roi = gray[max(0, int(y)): int(y + h), max(0, int(x)): int(x + w)]
        if roi.size < 100:
            continue
        roi = cv2.resize(roi, (128, int(128 * roi.shape[0] / max(1, roi.shape[1]))))
        sharp = float(cv2.Laplacian(roi, cv2.CV_64F).var())
        eyes = []
        r = max(4, int(0.09 * w))
        for ex, ey in ((f[4], f[5]), (f[6], f[7])):
            p = gray[max(0, int(ey - r)): int(ey + r), max(0, int(ex - r)): int(ex + r)].astype(np.float64)
            if p.size:
                eyes.append(float(np.mean(np.abs(np.diff(p, axis=0)))) / (p.mean() + 8))
        rows.append({"t": t, "img": im, "face": (float(x), float(y), float(w), float(h)), "conf": float(f[14]),
                     "eye_y": float((f[5] + f[7]) / 2),
                     "sharp": sharp, "eyes": float(np.mean(eyes)) if eyes else 0.0})
    if not rows:
        return []

    def rank(k):
        v = np.array([r[k] for r in rows])
        return (v.argsort().argsort() + 0.5) / len(v)
    rs, re_ = rank("sharp"), rank("eyes")
    H = rows[0]["img"].height
    for i, r in enumerate(rows):
        size = r["face"][3] / H
        size_ok = 1.0 - min(1.0, abs(size - 0.3) / 0.3)
        r["score"] = round(0.4 * rs[i] + 0.35 * re_[i] + 0.1 * r["conf"] + 0.15 * size_ok, 3)
    return sorted(rows, key=lambda r: -r["score"])


def fit_lines(words, font_file, size, max_w, max_lines, min_size=30):
    """Fewest balanced lines (no lone short word) that fit max_w, shrinking the font if needed."""
    while True:
        f = ImageFont.truetype(font_file, size)
        widths = [f.getlength(w) for w in words]
        lines = balance(widths, f.getlength(" "), max_w)
        txt = [" ".join(words[i] for i in l) for l in lines]
        if (len(lines) <= max_lines and all(f.getlength(t) <= max_w for t in txt)) or size <= min_size:
            return f, txt, size
        size = int(size * 0.92)


def compose_vertical(im, face, eye_y, title, out):
    """Title in white boxes inside the 3:4 profile-grid area, above the brows or below the chin (whichever
    holds it bigger), never over the eyes or mouth."""
    W, H = im.size
    _, _, ffile, _ = vc.font_for("Black")
    words = vc.upper_ro(title).split()
    g0, g1 = H * 240 / 1920 + 30, H * 1680 / 1920 - 30   # Instagram profile grid shows the middle 3:4
    above = (g0, eye_y - 0.22 * face[3] - 20)
    below = (face[1] + 1.08 * face[3] + 20, g1)
    best = None
    for region in (above, below):
        size = round(120 * W / 1080)
        while size >= 56:
            f, lines, size = fit_lines(words, ffile, size, W * 0.74, 4, min_size=56)
            pad_y, lh = size * 0.2, size * 1.25
            block = (len(lines) - 1) * lh + size + 2 * pad_y
            if block <= region[1] - region[0]:
                if not best or size > best[0]:
                    top = region[0] if region is below else region[1] - block
                    best = (size, f, lines, top, block)
                break
            size = int(size * 0.92)
    if not best:   # nothing fits clear of the face: small title at the bottom of the grid area
        f, lines, size = fit_lines(words, ffile, 56, W * 0.8, 4, min_size=40)
        block = (len(lines) - 1) * size * 1.25 + size * 1.4
        best = (size, f, lines, g1 - block, block)
    size, f, lines, top, block = best
    pad_x, pad_y, lh = size * 0.42, size * 0.2, size * 1.25
    d = ImageDraw.Draw(im)
    for i, line in enumerate(lines):
        tw = f.getlength(line)
        y = top + i * lh
        d.rounded_rectangle([W / 2 - tw / 2 - pad_x, y, W / 2 + tw / 2 + pad_x, y + size + 2 * pad_y],
                            radius=size * 0.22, fill=(255, 255, 255))
        d.text((W / 2, y + pad_y + size / 2), line, font=f, fill=(0, 0, 0), anchor="mm")
    im.save(out, quality=92)
    return top, top + block


def compose_thumb(im, face, title, out):
    W, H = im.size
    _, _, ffile, _ = vc.font_for("Black")
    words = vc.upper_ro(title).split()
    left = face[0] + face[2] / 2 > W / 2          # face on the right -> text on the left
    f, lines, size = fit_lines(words, ffile, round(118 * H / 720), W * 0.47, 3)
    lh = size * 1.08
    block = (len(lines) - 1) * lh + size
    x = W * 0.04 if left else W * 0.51
    top = (H - block) / 2
    shade = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(shade)
    sd.rectangle([0 if left else W * 0.46, 0, W * 0.54 if left else W, H], fill=110)
    shade = shade.filter(ImageFilter.GaussianBlur(40))
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, shade)
    d = ImageDraw.Draw(im)
    for i, line in enumerate(lines):
        d.text((x, top + i * lh), line, font=f, fill=(255, 255, 255) if i else (255, 212, 0),
               stroke_width=max(3, size // 14), stroke_fill=(0, 0, 0))
    im.save(out, quality=92)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cuts", help="cuts.json")
    ap.add_argument("-o", "--outdir", required=True)
    ap.add_argument("--format", default="reels", help="reels/tiktok/shorts/vertical -> cover_9x16; youtube -> thumb_16x9")
    ap.add_argument("--title", help="text on the cover (default: none, only the frame)")
    ap.add_argument("--track", action="append", help="SRC=track.json (face track from reframe.py)")
    ap.add_argument("--at", type=float, help="force this OUTPUT time instead of scoring")
    a = ap.parse_args()

    cuts = vc.load_json(a.cuts)
    W, H, _ = vc.canvas_for(a.format)
    vertical = H > W
    if not vertical:
        W, H = 1280, 720
    tracks = {}
    for t in a.track or []:
        k, p = t.split("=", 1) if "=" in t else ("0", t)
        tracks[int(k)] = vc.load_json(p)
    infos = [vc.media_info(s["path"]) for s in cuts["sources"]]
    cands, total = candidates(cuts)
    if a.at is not None:
        cands = [min(cands, key=lambda c: abs(c[0] - a.at))]
    imgs = []
    for t, si, st in cands:
        if not infos[si].get("has_video"):
            continue
        im = frame_for(infos[si], st, W, H, tracks.get(si))
        if im is not None:
            imgs.append((t, im))
    rows = score_faces(imgs)
    if not rows:
        if not imgs:
            raise vc.EditError("no frames could be read")
        t, im = imgs[len(imgs) // 3]
        rows = [{"t": t, "img": im, "face": (W * 0.35, H * 0.3, W * 0.3, H * 0.2), "score": 0}]
        print("no face found: using a frame from the first third")
    best = rows[0]
    os.makedirs(a.outdir, exist_ok=True)
    best["img"].save(os.path.join(a.outdir, "cover_frame.jpg"), quality=92)
    name = "cover_9x16.jpg" if vertical else "thumb_16x9.jpg"
    out = os.path.join(a.outdir, name)
    if a.title:
        if vertical:
            compose_vertical(best["img"].copy(), best["face"], best.get("eye_y", best["face"][1] + 0.4 * best["face"][3]),
                             a.title, out)
        else:
            compose_thumb(best["img"].copy(), best["face"], a.title, out)
    else:
        best["img"].save(out, quality=92)
    alts = ", ".join(f"{r['t']:.1f}s ({r['score']:.2f})" for r in rows[1:4])
    print(f"cover frame at output {best['t']:.2f}s (score {best['score']:.2f}; next: {alts}) -> {out}")


if __name__ == "__main__":
    main()
