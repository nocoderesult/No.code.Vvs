#!/usr/bin/env python3
"""Burn-in captions (ASS for libass) + SRT, on the EDITED timeline (word times remapped through cuts.json).

Styles (all Inter, Romanian diacritics with comma-below, positioned per word so the active-word pop never
shifts its neighbours):
  karaoke : 1-3 words, white + black outline, active word yellow and slightly bigger   (default, 9:16)
  box     : 1-3 words, active word black on a rounded yellow box
  pop     : one word at a time, big, pop-in scale animation
  clean   : sentence subtitles, max 2 lines, no animation (16:9 YouTube, calm content)
Optional hook title (--hook) at the top from frame 0, white rounded box with black text.
Positions respect platform safe zones (universal 9:16 box: x 120-888, y 290-1240) and are checked.

Examples:
  captions.py work/words.json --cuts work/cuts.json -o work/captions.ass --srt out/final.srt
  captions.py w.json --cuts c.json -o c.ass --style box --hook "3 GREȘELI LA MONTAJ"
  captions.py w.json --cuts c.json -o c.ass --format youtube --style clean
  captions.py w.json --cuts c.json -o c.ass --replace "Cloud=Claude" --replace "davinci=DaVinci"
"""
import argparse
import re

from PIL import ImageFont

import vcommon as vc

STRIP = re.compile(r"[.,;:…\"„”«»“]+")


# ------------------------------------------------------------------ timing


def remap(words, cuts):
    """Source-time words -> output-time words, following cuts.json segment order. Overlap rule (not
    midpoint): whisper starts can be early, a midpoint test dropped real words in tests."""
    if not cuts:
        return [dict(w) for w in words if w.get("src", 0) == 0]
    fps = vc.frac(cuts["fps"])
    out, acc = [], 0.0
    for gi, g in enumerate(vc.align_segments(cuts["segments"], fps)):
        s, e = float(g["S"]), float(g["E"])
        for w in words:
            if w.get("src", 0) != g["src"]:
                continue
            ov = min(w["e"], e) - max(w["s"], s)
            if ov > 0 and ov >= min(0.08, 0.3 * (w["e"] - w["s"])):
                out.append({**w, "s": max(w["s"], s) - s + acc, "e": min(w["e"], e) - s + acc, "seg": gi})
        acc += e - s
    return out


def apply_replacements(words, reps):
    table = {}
    for r in reps or []:
        if "=" not in r:
            raise vc.EditError(f"bad --replace '{r}' (use wrong=right)")
        k, v = r.split("=", 1)
        table[vc.fix_ro(k).lower()] = vc.fix_ro(v)
    if not table:
        return words
    for w in words:
        m = re.match(r"^([\"„«]*)(.*?)([.,;:!?…\"”»]*)$", w["w"])
        core = m.group(2)
        if core.lower() in table:
            w["w"] = m.group(1) + table[core.lower()] + m.group(3)
    return words


def chunks_by(words, max_words, max_chars, max_gap=0.45):
    chunks, cur = [], []
    for w in words:
        txt = " ".join(x["w"] for x in cur + [w])
        if cur and (len(cur) >= max_words or len(txt) > max_chars or w["s"] - cur[-1]["e"] > max_gap
                    or re.search(r"[.!?,:;…]$", cur[-1]["w"]) or w.get("seg") != cur[-1].get("seg")):
            chunks.append(cur)
            cur = []
        cur.append(w)
    if cur:
        chunks.append(cur)
    return chunks


def ts(t):
    cs = max(0, int(round(t * 100)))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def rounded_rect(w, h, r):
    k = 0.55 * r
    return (f"m {r} 0 l {w - r} 0 b {w - r + k} 0 {w} {r - k} {w} {r} l {w} {h - r} b {w} {h - r + k} {w - r + k} {h} "
            f"{w - r} {h} l {r} {h} b {r - k} {h} 0 {h - r + k} 0 {h - r} l 0 {r} b 0 {r - k} {r - k} 0 {r} 0")


def ass_color(hexrgb, alpha=0):
    h = hexrgb.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper().replace("&H", "&H")


def clean_text(t):
    return t.replace("{", "(").replace("}", ")").replace("\\", "/")


def balance(widths, space, max_w):
    """Split words into the fewest lines that fit max_w, choosing break points that minimise the widest line
    (avoids 'CUM EDITEZI UN / REEL ÎN 5 / MINUTE' orphans). DP over break points."""
    n = len(widths)
    greedy, cur, cw = [], [], 0
    for i, wd in enumerate(widths):
        add = wd + (space if cur else 0)
        if cur and cw + add > max_w:
            greedy.append(cur)
            cur, cw, add = [], 0, wd
        cur.append(i)
        cw += add
    greedy.append(cur)
    k = len(greedy)
    if k == 1:
        return greedy
    pre = [0.0]
    for w in widths:
        pre.append(pre[-1] + w)
    lw = lambda a, b: pre[b] - pre[a] + space * (b - a - 1)
    INF = float("inf")
    # best[j][i]: minimal max width splitting words[:i] into j lines
    best = [[INF] * (n + 1) for _ in range(k + 1)]
    arg = [[0] * (n + 1) for _ in range(k + 1)]
    best[0][0] = 0
    for j in range(1, k + 1):
        for i in range(j, n + 1):
            for t in range(j - 1, i):
                v = max(best[j - 1][t], lw(t, i))
                if v < best[j][i]:
                    best[j][i], arg[j][i] = v, t
    if best[k][n] > max_w + 0.5:
        return greedy
    lines, i = [], n
    for j in range(k, 0, -1):
        t = arg[j][i]
        lines.append(list(range(t, i)))
        i = t
    return lines[::-1]


def split_even(group, fits):
    """Split a sentence into the fewest consecutive parts that all satisfy fits(part), cutting near equal
    character counts (no one-word orphans like 'sfaturi.')."""
    for k in range(1, len(group) + 1):
        lens = [len(w["w"]) + 1 for w in group]
        tot = sum(lens)
        parts, cur, acc, nxt = [], [], 0, 1
        for w, L in zip(group, lens):
            if cur and nxt < k and acc + L / 2 > tot * nxt / k:
                parts.append(cur)
                cur, nxt = [], nxt + 1
            cur.append(w)
            acc += L
        parts.append(cur)
        if all(fits(p) for p in parts):
            return parts
    return [[w] for w in group]


def sentences(words, max_gap):
    out, cur = [], []
    for w in words:
        if cur and (w["s"] - cur[-1]["e"] > max_gap or re.search(r"[.!?…]$", cur[-1]["w"])
                    or w.get("seg") != cur[-1].get("seg")):
            out.append(cur)
            cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return out


# ------------------------------------------------------------------ builder


class Builder:
    def __init__(self, W, H, style, size, y, max_w, accent, upper, platform, hook_size=None):
        self.W, self.H, self.style, self.size, self.y, self.max_w = W, H, style, size, y, max_w
        self.accent, self.upper, self.platform = accent, upper, platform
        weight = "Bold" if style == "clean" else "Black"
        self.fam, self.bold, ffile, ratio = vc.font_for(weight)
        self.pil = ImageFont.truetype(ffile, max(8, round(size * ratio)))
        self.bord = max(2, round(size * (0.06 if style == "clean" else 0.075)))
        self.shad = max(1, round(size * 0.035))
        self.space = self.pil.getlength(" ") + 2 * self.bord + max(4, size * 0.07)
        self.pop = 1.10 if style == "karaoke" else 1.0      # active-word scale-up
        self.grow = self.pop
        self.lh = size * 1.12
        hf, hb, hfile, hr = vc.font_for("Black")
        self.hook_fam = hf
        self.hook_size = hook_size or round((92 if H > W * 1.2 else 72) * min(W, H) / 1080)
        self.hpil = ImageFont.truetype(hfile, max(8, round(self.hook_size * hr)))
        self.events = []
        self.spans = []  # (start, end) per caption chunk -> overlap check
        self.bbox = [1e9, 1e9, -1e9, -1e9]

    def header(self):
        acc = ass_color(self.accent)
        return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {self.W}
PlayResY: {self.H}
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: W,{self.fam},{self.size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H7A000000,{-1 if self.bold else 0},0,0,0,100,100,0,0,1,{self.bord},{self.shad},5,0,0,0,1
Style: Box,{self.fam},{self.size},{acc},{acc},{acc},&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Hook,{self.hook_fam},{self.hook_size},&H00000000,&H00000000,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: HookBox,{self.hook_fam},{self.hook_size},&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def _grow(self, x0, y0, x1, y1):
        b = self.bbox
        self.bbox = [min(b[0], x0), min(b[1], y0), max(b[2], x1), max(b[3], y1)]

    def disp(self, w):
        t = clean_text(vc.fix_ro(w))
        if self.style != "clean":
            t = STRIP.sub("", t).strip()
        return t.upper() if self.upper else t

    def layout(self, texts, pil=None, max_w=None, y=None, lh=None, grow=None, anchor="center"):
        """Balanced line breaking (fewest lines, then the most even widths); returns word centres, widths, n lines.
        `grow` reserves room for the active-word scale-up so neighbours never touch. anchor='top': y = top edge."""
        pil, max_w, y, lh = pil or self.pil, max_w or self.max_w, y or self.y, lh or self.lh
        grow = self.grow if grow is None else grow
        widths = [pil.getlength(t) for t in texts]
        slot = [w * grow for w in widths]
        lines = balance(slot, self.space, max_w)
        pos = {}
        for li, line in enumerate(lines):
            tot = sum(slot[i] for i in line) + self.space * (len(line) - 1)
            x = self.W / 2 - tot / 2
            yy = (y + li * lh) if anchor == "top" else (y + (li - (len(lines) - 1) / 2) * lh)
            for i in line:
                pos[i] = (x + slot[i] / 2, yy)
                x += slot[i] + self.space
        return pos, widths, len(lines)

    def word_chunks(self, words, chunks):
        accent = ass_color(self.accent)
        for ci, ch in enumerate(chunks):
            texts = [self.disp(w["w"]) for w in ch]
            keep = [i for i, t in enumerate(texts) if t]
            ch = [ch[i] for i in keep]
            texts = [texts[i] for i in keep]
            if not ch:
                continue
            pos, widths, nl = self.layout(texts)
            nxt = chunks[ci + 1][0]["s"] if ci + 1 < len(chunks) else 1e9
            c_end = min(ch[-1]["e"] + 0.25, nxt)              # hold the line briefly, never over the next chunk
            c_end = max(c_end, min(ch[-1]["s"] + 0.15, nxt))  # last word visible >= 0.15 s
            self.spans.append((ch[0]["s"], c_end))
            for i, t in enumerate(texts):
                px, py = pos[i]
                hw = widths[i] / 2 + self.bord
                self._grow(px - hw, py - self.size * 0.62, px + hw, py + self.size * 0.62)
            for k, w in enumerate(ch):
                t0 = ch[0]["s"] if k == 0 else w["s"]
                if ci == 0 and k == 0 and t0 < 0.5:
                    t0 = 0.0  # first caption on frame 0: the opening frame is never empty
                t1 = ch[k + 1]["s"] if k + 1 < len(ch) else c_end
                if t1 - t0 < 0.01:
                    continue
                for i, t in enumerate(texts):
                    px, py = pos[i]
                    if self.style == "pop":
                        self.events.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},W,,0,0,0,,{{\\pos({px:.1f},{py:.1f})"
                                           f"\\fscx78\\fscy78\\t(0,110,\\fscx100\\fscy100)}}{t}")
                    elif i == k and self.style == "box":
                        bw, bh = widths[i] + self.size * 0.42, self.size * 0.98
                        self.events.append(f"Dialogue: 0,{ts(t0)},{ts(t1)},Box,,0,0,0,,{{\\an7\\pos({px - bw / 2:.1f},"
                                           f"{py - bh / 2:.1f})\\p1}}{rounded_rect(round(bw), round(bh), round(self.size * 0.24))}")
                        self.events.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},W,,0,0,0,,{{\\pos({px:.1f},{py:.1f})"
                                           f"\\bord0\\shad0\\c&H000000&}}{t}")
                    elif i == k:
                        self.events.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},W,,0,0,0,,{{\\pos({px:.1f},{py:.1f})"
                                           f"\\c{accent}&\\fscx100\\fscy100\\t(0,80,\\fscx{self.pop * 100:.0f}\\fscy{self.pop * 100:.0f})}}{t}")
                    else:
                        self.events.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},W,,0,0,0,,{{\\pos({px:.1f},{py:.1f})}}{t}")

    def clean_chunks(self, words, max_lines=2, max_gap=0.7, max_dur=5.5):
        def fits(p):
            _, _, nl = self.layout([self.disp(x["w"]) for x in p])
            return nl <= max_lines and p[-1]["e"] - p[0]["s"] <= max_dur
        chunks = [c for sent in sentences(words, max_gap) for c in split_even(sent, fits)]
        for ci, ch in enumerate(chunks):
            texts = [self.disp(w["w"]) for w in ch]
            pos, widths, nl = self.layout(texts)
            lines = {}
            for i, t in enumerate(texts):
                lines.setdefault(round(pos[i][1], 1), []).append(t)
            body = "\\N".join(" ".join(v) for _, v in sorted(lines.items()))
            t0 = ch[0]["s"]
            nxt = chunks[ci + 1][0]["s"] if ci + 1 < len(chunks) else 1e9
            t1 = min(ch[-1]["e"] + 0.3, nxt)
            t1 = max(t1, min(t0 + 0.7, nxt))
            self.spans.append((t0, t1))
            for i in range(len(texts)):
                hw = widths[i] / 2 + self.bord
                self._grow(pos[i][0] - hw, pos[i][1] - self.size * 0.62, pos[i][0] + hw, pos[i][1] + self.size * 0.62)
            self.events.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},W,,0,0,0,,{{\\pos({self.W / 2:.1f},{self.y:.1f})}}{body}")

    def hook(self, text, dur, y=None, avoid=None, cap_top=None):
        """Hook title in white rounded boxes. Default: top-aligned just inside the safe zone; if that would
        cover the face (avoid=(y0,y1) in canvas px) it moves below the face, else shrinks to fit above it."""
        text = clean_text(vc.fix_ro(text))
        text = text.upper() if self.upper else text
        words = text.split()
        sx0, sy0, sx1, sy1 = vc.safe_box(self.platform, self.W, self.H)
        top0 = sy0 + 0.012 * self.H
        cap_top = cap_top or (self.y - self.size)
        base, _, ffile, ratio = vc.font_for("Black")
        size = self.hook_size
        for attempt in range(5):  # shrink to at most ~0.66x
            pil = ImageFont.truetype(ffile, max(8, round(size * ratio)))
            pad_x, pad_y = size * 0.42, size * 0.20
            lh = size * 1.22
            old = self.space
            self.space = pil.getlength(" ")
            probe_pos, _, nl = self.layout(words, pil=pil, max_w=self.max_w + 60 - 2 * pad_x, y=0, lh=lh, grow=1.0)
            self.space = old
            bh = size * 0.98 + 2 * pad_y
            block = (nl - 1) * lh + bh
            if y is not None:                      # explicit centre
                top = y - block / 2
                break
            top = top0
            if not avoid or top + block <= avoid[0] - 0.01 * self.H:
                break
            below = avoid[1] + 0.02 * self.H
            if below + block <= cap_top - 0.015 * self.H:
                top = below
                break
            size *= 0.9                            # shrink and retry above the face
        else:
            top = top0
            vc.log("warning: hook overlaps the face (eyes/mouth); use a shorter hook or --hook-y")
        self.hook_box = (top, top + block)
        old = self.space
        self.space = pil.getlength(" ")
        pos, widths, nl = self.layout(words, pil=pil, max_w=self.max_w + 60 - 2 * pad_x, y=top + bh / 2, lh=lh,
                                      grow=1.0, anchor="top")
        self.space = old
        lines = {}
        for i in range(len(words)):
            lines.setdefault(round(pos[i][1], 1), []).append(i)
        fade = "\\fad(0,200)"  # visible on frame 0 (feed preview / first impression), fade out only
        fs = f"\\fs{round(size)}" if round(size) != self.hook_size else ""
        for ly, idx in sorted(lines.items()):
            x0 = pos[idx[0]][0] - widths[idx[0]] / 2 - pad_x
            x1 = pos[idx[-1]][0] + widths[idx[-1]] / 2 + pad_x
            self.events.append(f"Dialogue: 2,{ts(0)},{ts(dur)},HookBox,,0,0,0,,{{\\an7\\pos({x0:.1f},{ly - bh / 2:.1f}){fade}\\p1}}"
                               f"{rounded_rect(round(x1 - x0), round(bh), round(size * 0.22))}")
            self.events.append(f"Dialogue: 3,{ts(0)},{ts(dur)},Hook,,0,0,0,,{{\\pos({(x0 + x1) / 2:.1f},{ly:.1f}){fade}{fs}}}"
                               f"{' '.join(words[i] for i in idx)}")
            self._grow(x0, ly - bh / 2, x1, ly + bh / 2)

    def text(self):
        return self.header() + "\n".join(self.events) + "\n"


def build_srt(words, line_chars=42, max_dur=6.0):
    """Subtitle-standard SRT: up to 2 lines x 42 characters, <= 6 s, sentence-aware, balanced lines."""
    fits = lambda p: len(" ".join(x["w"] for x in p)) <= 2 * line_chars and p[-1]["e"] - p[0]["s"] <= max_dur
    entries = [c for sent in sentences(words, 1.0) for c in split_even(sent, fits)]

    def two_lines(ws):
        t = vc.fix_ro(" ".join(x["w"] for x in ws))
        if len(t) <= line_chars:
            return t
        best = min(range(1, len(ws)), key=lambda i: abs(len(" ".join(x["w"] for x in ws[:i])) - len(t) / 2))
        return vc.fix_ro(" ".join(x["w"] for x in ws[:best]) + "\n" + " ".join(x["w"] for x in ws[best:]))

    def st(t):
        ms = int(round(max(0, t) * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    return "\n".join(f"{i + 1}\n{st(l[0]['s'])} --> {st(l[-1]['e'])}\n{two_lines(l)}\n" for i, l in enumerate(entries))


def defaults(W, H, style):
    s = min(W, H) / 1080
    vertical = H > W * 1.2
    size = {"karaoke": 80, "box": 80, "pop": 96, "clean": 62}[style]
    if not vertical:
        size = {"karaoke": 72, "box": 72, "pop": 96, "clean": 56}[style] * (H / 1080)
    else:
        size *= s
    if vertical:
        y = H * (1130 / 1920) if style != "clean" else H * (1150 / 1920)
        max_w = W * 680 / 1080   # text x ~200..880 (+outline): clears the Shorts/TikTok right action rail
        hook_y = H * 470 / 1920
    elif H > W * 0.9:   # square / 4:5
        y, max_w, hook_y = H * 0.74, W * 0.80, H * 0.16
    else:               # 16:9
        y, max_w, hook_y = H * 0.83, W * 0.72, H * 0.17
    return round(size), y, max_w, hook_y


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("words", help="words.json from transcribe.py")
    ap.add_argument("--cuts", help="cuts.json from plan_cuts.py (omit = uncut source 0 timeline)")
    ap.add_argument("-o", "--out", required=True, help="output .ass")
    ap.add_argument("--srt", help="also write an SRT (edited timeline) for YouTube CC / Resolve")
    ap.add_argument("--format", default="reels", help="canvas: reels/tiktok/shorts/youtube/square/portrait or WxH")
    ap.add_argument("--style", choices=["karaoke", "box", "pop", "clean", "none"], default="karaoke",
                    help="none = no burned captions (only the --hook, if given); the SRT is still written")
    ap.add_argument("--platform", choices=list(vc.SAFE_ZONES), help="safe zone to check (default from format)")
    ap.add_argument("--size", type=float, help="font size in canvas px (default 80 karaoke on 1080x1920)")
    ap.add_argument("--y", type=float, help="vertical centre of the caption block (px)")
    ap.add_argument("--max-width", type=float, help="max caption line width (px)")
    ap.add_argument("--max-words", type=int, help="words per chunk (karaoke/box 3, pop 1)")
    ap.add_argument("--max-chars", type=int, default=14, help="max characters per chunk (14 -> mostly one line at 80 px)")
    ap.add_argument("--accent", default="#FFD400", help="active word colour (#FFD400 yellow, #2EE66B green)")
    ap.add_argument("--case", choices=["auto", "upper", "keep"], default="auto",
                    help="auto = UPPER for karaoke/box/pop, sentence case for clean")
    ap.add_argument("--hook", help="hook title shown from frame 0 (3-7 words)")
    ap.add_argument("--hook-dur", type=float, default=3.0, help="hook duration (s)")
    ap.add_argument("--hook-y", type=float, help="hook vertical centre (px)")
    ap.add_argument("--avoid", help="face band to keep clear, 'Y0:Y1' in canvas px (pipeline passes it from "
                    "reframe.py); captions/hook are moved off it")
    ap.add_argument("--replace", action="append", help="fix a word everywhere: wrong=right (repeatable)")
    a = ap.parse_args()

    W, H, plat = vc.canvas_for(a.format)
    plat = a.platform or plat
    size, y, max_w, hook_y = defaults(W, H, a.style if a.style != "none" else "karaoke")
    size = round(a.size or size)
    y = a.y or y
    avoid = tuple(float(v) for v in a.avoid.split(":")) if a.avoid else None
    if avoid and not a.y and avoid[0] - size < y < avoid[1] + size:
        # captions would sit on the face: move them just below it if that stays in the safe zone, else above
        sy1 = vc.safe_box(a.platform or plat, W, H)[3]
        y = avoid[1] + size * 1.1 if avoid[1] + size * 2.2 < sy1 else max(avoid[0] - size * 1.6, H * 0.2)
        print(f"captions moved to y={y:.0f} to keep the face ({avoid[0]:.0f}-{avoid[1]:.0f}) clear")
    max_w = a.max_width or max_w
    W_ = vc.load_json(a.words)
    cuts = vc.load_json(a.cuts) if a.cuts else None
    words = apply_replacements(remap(W_["words"], cuts), a.replace)
    for w in words:
        w["w"] = vc.fix_ro(w["w"])
    upper = a.case == "upper" or (a.case == "auto" and a.style != "clean")
    b = Builder(W, H, a.style, size, y, max_w, a.accent, upper, plat)
    if a.style == "none":
        pass
    elif a.style == "clean":
        b.clean_chunks(words)
    else:
        mw = a.max_words or (1 if a.style == "pop" else 3)
        b.word_chunks(words, chunks_by(words, mw, a.max_chars if a.style != "pop" else 99))
    if a.hook:
        b.hook(a.hook, a.hook_dur, a.hook_y, avoid)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(b.text())
    if a.srt:
        with open(a.srt, "w", encoding="utf-8") as f:
            f.write(build_srt(words))
    x0, y0, x1, y1 = vc.safe_box(plat, W, H)
    bx = b.bbox
    ok = bx[0] >= x0 and bx[1] >= y0 and bx[2] <= x1 and bx[3] <= y1
    sp = sorted(b.spans)
    over = [(x, y) for x, y in zip(sp, sp[1:]) if y[0] < x[1] - 0.011]
    print(f"{len(words)} words -> {len(b.events)} events, style {a.style}, size {size}px, canvas {W}x{H}; "
          f"{'no overlapping chunks' if not over else f'WARNING {len(over)} overlapping chunks at {over[0][1][0]:.2f}s'}")
    if bx[0] < 1e8:
        print(f"caption bbox x {bx[0]:.0f}-{bx[2]:.0f}, y {bx[1]:.0f}-{bx[3]:.0f}; safe zone ({plat}) "
              f"x {x0:.0f}-{x1:.0f}, y {y0:.0f}-{y1:.0f}: {'OK' if ok else 'WARNING: outside safe zone'}")
    print(f"wrote {a.out}" + (f" and {a.srt}" if a.srt else ""))


if __name__ == "__main__":
    main()
