#!/usr/bin/env python3
"""Burn-in captions (ASS for libass) + SRT, on the EDITED timeline (word times remapped through cuts.json).

Styles (all Inter, Romanian diacritics with comma-below, positioned per word so the active-word pop never
shifts its neighbours):
  karaoke : 1-3 words on ONE line, white + black outline, active word yellow and 110%   (default, 9:16)
  box     : 1-3 words on one line, active word black on a rounded yellow box
  pop     : one word at a time, big, pop-in scale animation
  clean   : sentence subtitles, max 2 lines, no animation (16:9 YouTube, calm content)
A chunk that would not fit the line width is split; a single word that is still too wide (Romanian has
'NECONSTITUȚIONALITATEA') gets a smaller \\fs for that chunk, measured with the 110% pop and the outline.
Titles: --hook (top of the safe area from frame 0, white rounded boxes) and --cta (end card for the last
--cta-dur s). Layout treats the face band (--avoid) AND the caption line as obstacles: a title is placed where
it touches neither (shrinking it if needed); if no such place exists the captions move for the title's
duration. After writing, every event box is re-measured from the .ass (ass_boxes, also used by qc.py) and the
run FAILS (exit 3) if any box leaves the safe zone or a caption overlaps a title in time and space.

Examples:
  captions.py work/words.json --cuts work/cuts.json -o work/captions.ass --srt out/final.srt
  captions.py w.json --cuts c.json -o c.ass --style box --hook "3 GREȘELI LA MONTAJ" --cta "SALVEAZĂ PENTRU MAI TÂRZIU"
  captions.py w.json --cuts c.json -o c.ass --format youtube --style clean
  captions.py w.json --cuts c.json -o c.ass --replace "Cloud=Claude" --replace "davinci=DaVinci"
"""
import argparse
import functools
import re
import sys

from PIL import ImageFont

import vcommon as vc

STRIP = re.compile(r"[.,;:…\"„”«»“]+")
TITLE_SCALES = (1.0, 0.92, 0.85, 0.78, 0.72)        # hook/CTA sizes tried before moving the captions
TITLE_SMALL = (0.66, 0.6, 0.55, 0.5)                 # last resort
INK = 1.03   # libass ink is up to ~3% wider than PIL's advance width (measured: long words, pop, outline)


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


def out_duration(cuts, words):
    if cuts:
        fps = vc.frac(cuts["fps"])
        return float(sum(g["E"] - g["S"] for g in vc.align_segments(cuts["segments"], fps)))
    return max((w["e"] for w in words), default=0.0)


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


def parse_ts(s):
    h, m, sec = s.strip().split(":")
    return int(h) * 3600 + int(m) * 60 + float(sec)


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
    """Sentence groups: break at pauses, sentence-final punctuation, cuts and Whisper segment ends."""
    out, cur = [], []
    for w in words:
        if cur and (w["s"] - cur[-1]["e"] > max_gap or re.search(r"[.!?…]$", cur[-1]["w"])
                    or w.get("seg") != cur[-1].get("seg")
                    or ("si" in w and "si" in cur[-1] and w["si"] != cur[-1]["si"])):
            out.append(cur)
            cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return out


def overlap(a0, a1, b0, b1, margin=0.0):
    return a0 < b1 + margin and b0 < a1 + margin


# ------------------------------------------------------------------ measuring an .ass (self-check + qc.py)


@functools.lru_cache(maxsize=None)
def _font(name, bold, px):
    weight = {"Inter Black": "Black", "Inter ExtraBold": "ExtraBold", "Inter SemiBold": "SemiBold"}.get(name)
    if weight is None:
        weight = "Bold" if name == "Inter" else None
    if weight:
        _, _, f, ratio = vc.font_for(weight)
    else:
        f = vc.run(["fc-match", "-f", "%{file}", f"{name}:{'bold' if bold else 'regular'}"], capture=True,
                   check=False).stdout.strip() or "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        from PIL import ImageFont as IF
        asc, desc = IF.truetype(f, 1000).getmetrics()
        ratio = 1000.0 / (asc + desc)
    return ImageFont.truetype(f, max(4, round(px * ratio)))


def _num(tag, txt, default=None):
    m = re.search(r"\\" + tag + r"(-?[\d.]+)", txt)
    return float(m.group(1)) if m else default


def ass_boxes(path):
    """Every Dialogue event of an .ass as {t0,t1,layer,style,name,kind,box=(x0,y0,x1,y1),text}: what libass will
    cover, including the largest \\fscx/\\fscy reached by a \\t() pop, the outline and the shadow.
    kind: 'caption' (W/Box styles) or 'title' (Hook/HookBox: hook and CTA)."""
    styles, out = {}, []
    play = (1080, 1920)
    for line in open(path, encoding="utf-8"):
        if line.startswith("PlayResX:"):
            play = (int(line.split(":")[1]), play[1])
        elif line.startswith("PlayResY:"):
            play = (play[0], int(line.split(":")[1]))
        elif line.startswith("Style:"):
            f = [x.strip() for x in line[6:].split(",")]
            styles[f[0]] = {"font": f[1], "size": float(f[2]), "bold": f[7] not in ("0", ""),
                            "bord": float(f[16]), "shad": float(f[17]), "an": int(f[18])}
        elif line.startswith("Dialogue:"):
            f = line[9:].split(",", 9)
            st = styles.get(f[3].strip(), {"font": "Inter Black", "size": 80, "bold": False, "bord": 4, "shad": 2,
                                           "an": 5})
            text = f[9].rstrip("\n")
            tags = "".join(re.findall(r"\{([^}]*)\}", text))
            plain = re.sub(r"\{[^}]*\}", "", text)
            m = re.search(r"\\pos\(([-\d.]+),([-\d.]+)\)", tags)
            x, y = (float(m.group(1)), float(m.group(2))) if m else (play[0] / 2, play[1] / 2)
            an = int(_num("an", tags, st["an"]))
            size = _num("fs", tags, st["size"])
            sx = max([_num("fscx", tags, 100)] + [float(v) for v in re.findall(r"\\fscx([\d.]+)", tags)]) / 100
            sy = max([_num("fscy", tags, 100)] + [float(v) for v in re.findall(r"\\fscy([\d.]+)", tags)]) / 100
            bord = _num("bord", tags, st["bord"])
            shad = _num("shad", tags, st["shad"])
            if re.search(r"\\p[1-9]", tags):
                nums = [float(v) for v in re.findall(r"-?[\d.]+", plain)]
                xs, ys = nums[0::2], nums[1::2]
                w, h = (max(xs) - min(xs)) * sx, (max(ys) - min(ys)) * sy
                bord = shad = 0 if "\\bord" not in tags else bord
            else:
                lines = plain.split("\\N")
                fnt = _font(st["font"], st["bold"], size)
                w = max(fnt.getlength(l) for l in lines) * sx * INK
                h = size * sy * (1 + 1.15 * (len(lines) - 1))
            col = (an - 1) % 3          # 0 left, 1 centre, 2 right
            row = (an - 1) // 3         # 0 bottom, 1 middle, 2 top
            x0 = x - (0 if col == 0 else w / 2 if col == 1 else w)
            y0 = y - (h if row == 0 else h / 2 if row == 1 else 0)
            box = (x0 - bord, y0 - bord, x0 + w + bord + shad, y0 + h + bord + shad)
            sty = f[3].strip()
            out.append({"t0": parse_ts(f[1]), "t1": parse_ts(f[2]), "layer": int(f[0]), "style": sty,
                        "name": f[4].strip(), "kind": "title" if sty.startswith("Hook") else "caption",
                        "box": tuple(round(v, 1) for v in box), "text": plain})
    return out, play


def check_boxes(boxes, safe, tol=1.5):
    """Problems: boxes outside the safe zone; captions overlapping a title (hook/CTA) in time AND space."""
    x0, y0, x1, y1 = safe
    probs = []
    outside = [b for b in boxes if b["box"][0] < x0 - tol or b["box"][1] < y0 - tol or b["box"][2] > x1 + tol
               or b["box"][3] > y1 + tol]
    if outside:
        b = outside[0]
        probs.append(f"{len(outside)} event(s) outside the safe zone x {x0:.0f}-{x1:.0f}, y {y0:.0f}-{y1:.0f}; first "
                     f"'{b['text'][:30]}' at {b['t0']:.2f}s box x {b['box'][0]:.0f}-{b['box'][2]:.0f} "
                     f"y {b['box'][1]:.0f}-{b['box'][3]:.0f}")
    titles = [b for b in boxes if b["kind"] == "title"]
    caps = [b for b in boxes if b["kind"] == "caption"]
    hits = [(c, t) for c in caps for t in titles
            if overlap(c["t0"], c["t1"], t["t0"], t["t1"], -0.011)
            and overlap(c["box"][0], c["box"][2], t["box"][0], t["box"][2])
            and overlap(c["box"][1], c["box"][3], t["box"][1], t["box"][3])]
    if hits:
        c, t = hits[0]
        probs.append(f"{len(hits)} caption/title overlap(s); first caption '{c['text'][:20]}' at {c['t0']:.2f}s "
                     f"y {c['box'][1]:.0f}-{c['box'][3]:.0f} under '{t['name'] or 'title'}' y {t['box'][1]:.0f}-"
                     f"{t['box'][3]:.0f}")
    return probs


# ------------------------------------------------------------------ builder


class Builder:
    def __init__(self, W, H, style, size, y, max_w, accent, upper, platform, hook_size=None):
        self.W, self.H, self.style, self.size, self.y, self.max_w = W, H, style, size, y, max_w
        self.accent, self.upper, self.platform = accent, upper, platform
        weight = "Bold" if style == "clean" else "Black"
        self.fam, self.bold, ffile, ratio = vc.font_for(weight)
        self.ffile, self.ratio = ffile, ratio
        self.pil = ImageFont.truetype(ffile, max(8, round(size * ratio)))
        self.bord = max(2, round(size * (0.06 if style == "clean" else 0.075)))
        self.shad = max(1, round(size * 0.035))
        self.space = self.pil.getlength(" ") + 2 * self.bord + max(4, size * 0.07)
        self.pop = 1.10 if style == "karaoke" else 1.0      # active-word scale-up
        self.grow = self.pop
        self.word_extra = max(size * 0.42, 2 * self.bord) + self.shad if style == "box" else 2 * self.bord + self.shad
        self.lh = size * 1.12
        hf, hb, hfile, hr = vc.font_for("Black")
        self.hook_fam, self.hfile, self.hratio = hf, hfile, hr
        self.hook_size = hook_size or round((92 if H > W * 1.2 else 72) * min(W, H) / 1080)
        self.events = []
        self.spans = []  # (start, end) per caption chunk -> overlap check
        self.cap_windows = []  # (t0, t1, y): caption line moved while a title is on screen
        self.titles = []       # placements, for the report
        self.shrunk = []       # chunks drawn smaller so a long word fits

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

    def disp(self, w):
        t = clean_text(vc.fix_ro(w))
        if self.style != "clean":
            t = STRIP.sub("", t).strip()
        return t.upper() if self.upper else t

    def cap_half(self):
        """Half height of the caption line as libass draws it (pop scale, outline, shadow)."""
        if self.style == "clean":
            return 0.5 * self.lh + 0.5 * self.size + self.bord + self.shad   # up to 2 lines
        return 0.5 * self.size * self.pop + self.bord + self.shad

    def y_at(self, t0, t1):
        for a, b, y in self.cap_windows:
            if t0 < b and t1 > a:
                return y
        return self.y

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

    def line_width(self, texts):
        """Drawn width of one caption line: words at the active-word pop, gaps, plus the outline/shadow (or the
        box padding) that \\fs does not shrink."""
        ws = [self.pil.getlength(t) * INK for t in texts]
        return sum(w * self.grow for w in ws) + self.space * (len(ws) - 1) + self.word_extra

    def fit_chunks(self, chunks):
        """One line per chunk: split chunks wider than max_w; a single word still too wide gets a scale < 1."""
        out = []
        for ch in chunks:
            ch = [w for w in ch if self.disp(w["w"])]
            parts, cur = [], []
            for w in ch:
                if cur and self.line_width([self.disp(x["w"]) for x in cur + [w]]) > self.max_w:
                    parts.append(cur)
                    cur = []
                cur.append(w)
            if cur:
                parts.append(cur)
            for p in parts:
                lw = self.line_width([self.disp(x["w"]) for x in p])
                ex = 2 * self.bord + self.shad
                out.append((p, (self.max_w - ex) / (lw - ex) if lw > self.max_w else 1.0))
        return [(c, s) for c, s in out if c]

    def word_chunks(self, words, chunks):
        accent = ass_color(self.accent)
        fitted = self.fit_chunks(chunks)
        for ci, (ch, sc) in enumerate(fitted):
            texts = [self.disp(w["w"]) for w in ch]
            if sc < 1.0:
                sc = int(sc * 100) / 100.0
                self.shrunk.append((" ".join(texts), sc))
            size = self.size * sc
            widths = [self.pil.getlength(t) * sc * INK for t in texts]
            slot = [w * self.grow for w in widths]
            space = self.space * sc
            nxt = fitted[ci + 1][0][0]["s"] if ci + 1 < len(fitted) else 1e9
            c_end = min(ch[-1]["e"] + 0.25, nxt)              # hold the line briefly, never over the next chunk
            c_end = max(c_end, min(ch[-1]["s"] + 0.15, nxt))  # last word visible >= 0.15 s
            c_start = 0.0 if ci == 0 and ch[0]["s"] < 0.5 else ch[0]["s"]  # opening frame is never empty
            self.spans.append((c_start, c_end))
            y = self.y_at(c_start, c_end)
            tot = sum(slot) + space * (len(slot) - 1)
            x, pos = self.W / 2 - tot / 2, []
            for s_ in slot:
                pos.append(x + s_ / 2)
                x += s_ + space
            fs = f"\\fs{size:.0f}" if sc < 1.0 else ""
            for k, w in enumerate(ch):
                t0 = c_start if k == 0 else w["s"]
                t1 = ch[k + 1]["s"] if k + 1 < len(ch) else c_end
                if t1 - t0 < 0.01:
                    continue
                for i, t in enumerate(texts):
                    px = pos[i]
                    if self.style == "pop":
                        self.events.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},W,,0,0,0,,{{\\pos({px:.1f},{y:.1f}){fs}"
                                           f"\\fscx78\\fscy78\\t(0,110,\\fscx100\\fscy100)}}{t}")
                    elif i == k and self.style == "box":
                        bw, bh = widths[i] + size * 0.42, size * 0.98
                        self.events.append(f"Dialogue: 0,{ts(t0)},{ts(t1)},Box,,0,0,0,,{{\\an7\\pos({px - bw / 2:.1f},"
                                           f"{y - bh / 2:.1f})\\p1}}{rounded_rect(round(bw), round(bh), round(size * 0.24))}")
                        self.events.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},W,,0,0,0,,{{\\pos({px:.1f},{y:.1f}){fs}"
                                           f"\\bord0\\shad0\\c&H000000&}}{t}")
                    elif i == k:
                        self.events.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},W,,0,0,0,,{{\\pos({px:.1f},{y:.1f}){fs}"
                                           f"\\c{accent}&\\fscx100\\fscy100\\t(0,80,\\fscx{self.pop * 100:.0f}\\fscy{self.pop * 100:.0f})}}{t}")
                    else:
                        self.events.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},W,,0,0,0,,{{\\pos({px:.1f},{y:.1f}){fs}}}{t}")

    def clean_chunks(self, words, max_lines=2, max_gap=0.7, max_dur=5.5):
        def fits(p):
            _, _, nl = self.layout([self.disp(x["w"]) for x in p])
            return nl <= max_lines and p[-1]["e"] - p[0]["s"] <= max_dur
        chunks = [c for sent in sentences(words, max_gap) for c in split_even(sent, fits)]
        for ci, ch in enumerate(chunks):
            texts = [self.disp(w["w"]) for w in ch]
            t0 = ch[0]["s"]
            nxt = chunks[ci + 1][0]["s"] if ci + 1 < len(chunks) else 1e9
            t1 = min(ch[-1]["e"] + 0.3, nxt)
            t1 = max(t1, min(t0 + 0.7, nxt))
            y = self.y_at(t0, t1)
            pos, widths, nl = self.layout(texts, y=y)
            lines = {}
            for i, t in enumerate(texts):
                lines.setdefault(round(pos[i][1], 1), []).append(t)
            body = "\\N".join(" ".join(v) for _, v in sorted(lines.items()))
            self.spans.append((t0, t1))
            self.events.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},W,,0,0,0,,{{\\pos({self.W / 2:.1f},{y:.1f})}}{body}")

    # ---------------------------------------------------------------- titles (hook / CTA)

    def title_layout(self, words, size, box_w):
        pil = ImageFont.truetype(self.hfile, max(8, round(size * self.hratio)))
        pad_x, pad_y = size * 0.42, size * 0.20
        space = pil.getlength(" ")
        widths = [pil.getlength(w) * INK for w in words]
        lines = balance(widths, space, box_w - 2 * pad_x)
        lw = [sum(widths[i] for i in l) + space * (len(l) - 1) for l in lines]
        bh = size * 0.98 + 2 * pad_y
        lh = size * 1.22
        fits = max(lw) + 2 * pad_x <= box_w + 0.5
        return {"size": size, "lines": lines, "lw": lw, "bh": bh, "lh": lh, "pad_x": pad_x,
                "block": (len(lines) - 1) * lh + bh, "fits": fits}

    def place_title(self, text, t0, t1, avoid, has_caps, y=None, prefer="top"):
        """Find a spot for a title shown during [t0, t1] that is inside the safe area and clear of the face band
        and of the caption line. Returns (layout, top, caption_y_override or None, ok)."""
        words = text.split()
        sx0, sy0, sx1, sy1 = vc.safe_box(self.platform, self.W, self.H)
        m = 0.012 * self.H
        F = avoid
        hb = self.cap_half()
        C = (self.y - hb, self.y + hb) if has_caps else None
        sym = 2 * min(self.W / 2 - sx0, sx1 - self.W / 2) - 4     # titles are centred: symmetric safe width
        widths = sorted({round(min(self.max_w + 60, sym)), round(sym)})

        def free(top, block, cap=C):
            if top < sy0 - 0.5 or top + block > sy1 + 0.5:
                return False
            if F and overlap(top, top + block, F[0], F[1], m / 2):
                return False
            return not (cap and overlap(top, top + block, cap[0], cap[1], m / 2))

        def tops(block):
            if y is not None:
                return [y - block / 2]
            first = [sy0 + m] if prefer == "top" else []
            cands = first + ([F[1] + m] if F else []) + ([C[1] + m] if C else []) + \
                ([C[0] - m - block] if C else []) + ([F[0] - m - block] if F else [])
            if prefer != "top":
                cands.append(sy0 + m)
            return cands

        def search(scales, move):
            for sc in scales:
                for bw in widths:
                    lay = self.title_layout(words, self.hook_size * sc, bw)
                    if not lay["fits"]:
                        continue
                    for top in tops(lay["block"]):
                        if not move:
                            if free(top, lay["block"]):
                                return lay, top, None
                            continue
                        if not free(top, lay["block"], cap=None):
                            continue
                        r0, r1 = top, top + lay["block"]          # move the captions off the title instead
                        cys = [r1 + m + hb, r0 - m - hb] + ([F[1] + m + hb, F[0] - m - hb] if F else [])
                        for cy in cys:
                            if cy - hb < sy0 or cy + hb > sy1 or overlap(cy - hb, cy + hb, r0, r1, m / 2):
                                continue
                            if F and overlap(cy - hb, cy + hb, F[0], F[1]):
                                continue
                            return lay, top, cy
            return None

        for scales, move in ((TITLE_SCALES, False), (TITLE_SCALES, True), (TITLE_SMALL, False), (TITLE_SMALL, True)):
            if move and not C:
                continue
            r = search(scales, move)
            if r:
                return (*r, True)
        lay = self.title_layout(words, self.hook_size * TITLE_SMALL[-1], widths[-1])
        return lay, (y - lay["block"] / 2) if y is not None else sy0 + m, None, False

    def title(self, text, t0, t1, avoid, has_caps, y=None, kind="hook"):
        text = clean_text(vc.fix_ro(text)).strip()
        text = text.upper() if self.upper else text
        lay, top, cap_y, ok = self.place_title(text, t0, t1, avoid, has_caps, y, prefer="top")
        if cap_y is not None:
            self.cap_windows.append((t0, t1, cap_y))
        if not ok:
            vc.log(f"warning: {kind} '{text}' does not fit clear of the face and captions; shorten it")
        words = text.split()
        size, bh, lh, pad_x = lay["size"], lay["bh"], lay["lh"], lay["pad_x"]
        fade = "\\fad(0,200)" if kind == "hook" else "\\fad(150,0)"  # hook visible on frame 0; CTA pops in
        fs = f"\\fs{round(size)}" if round(size) != self.hook_size else ""
        for li, (line, lw) in enumerate(zip(lay["lines"], lay["lw"])):
            cy = top + bh / 2 + li * lh
            x0 = self.W / 2 - lw / 2 - pad_x
            x1 = self.W / 2 + lw / 2 + pad_x
            self.events.append(f"Dialogue: 2,{ts(t0)},{ts(t1)},HookBox,{kind},0,0,0,,{{\\an7\\pos({x0:.1f},{cy - bh / 2:.1f})"
                               f"{fade}\\p1}}{rounded_rect(round(x1 - x0), round(bh), round(size * 0.22))}")
            self.events.append(f"Dialogue: 3,{ts(t0)},{ts(t1)},Hook,{kind},0,0,0,,{{\\pos({self.W / 2:.1f},{cy:.1f}){fade}{fs}}}"
                               f"{' '.join(words[i] for i in line)}")
        self.titles.append({"kind": kind, "t0": t0, "t1": t1, "top": round(top), "bottom": round(top + lay["block"]),
                            "size": round(size), "lines": len(lay["lines"]),
                            "captions_moved_to": round(cap_y) if cap_y is not None else None, "ok": ok})

    def text(self):
        return self.header() + "\n".join(self.events) + "\n"


def build_srt(words, line_chars=42, max_dur=6.0):
    """Subtitle-standard SRT: up to 2 lines x 42 characters, <= 6 s, sentence-aware (entries end at sentence
    punctuation, cuts and Whisper segment ends), balanced lines."""
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


def caption_y(y, half, avoid, safe, H):
    """Move the caption line off the face band: below the chin if it fits the safe area, else above the brows;
    if neither fits, the side with less overlap (chin before eyes)."""
    if not avoid:
        return y, None
    m = 0.01 * H
    if not overlap(y - half, y + half, avoid[0], avoid[1], m):
        return y, None
    sy0, sy1 = safe[1], safe[3]
    below = avoid[1] + m + half
    if below + half <= sy1:
        return below, "below"
    above = avoid[0] - m - half
    if above - half >= sy0:
        return above, "above"
    return sy1 - half, "below (overlaps the chin: face too big in frame, consider --reframe wide)"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("words", help="words.json from transcribe.py")
    ap.add_argument("--cuts", help="cuts.json from plan_cuts.py (omit = uncut source 0 timeline)")
    ap.add_argument("-o", "--out", required=True, help="output .ass")
    ap.add_argument("--srt", help="also write an SRT (edited timeline) for YouTube CC / Resolve")
    ap.add_argument("--format", default="reels", help="canvas: reels/tiktok/shorts/youtube/square/portrait or WxH")
    ap.add_argument("--style", choices=["karaoke", "box", "pop", "clean", "none"], default="karaoke",
                    help="none = no burned captions (only the --hook/--cta, if given); the SRT is still written")
    ap.add_argument("--platform", choices=list(vc.SAFE_ZONES), help="safe zone to check (default from format)")
    ap.add_argument("--size", type=float, help="font size in canvas px (default 80 karaoke on 1080x1920)")
    ap.add_argument("--y", type=float, help="vertical centre of the caption line (px)")
    ap.add_argument("--max-width", type=float, help="max caption line width (px)")
    ap.add_argument("--max-words", type=int, help="words per chunk (karaoke/box 3, pop 1)")
    ap.add_argument("--max-chars", type=int, default=14, help="max characters per chunk (14 -> one line at 80 px)")
    ap.add_argument("--accent", default="#FFD400", help="active word colour (#FFD400 yellow, #2EE66B green)")
    ap.add_argument("--case", choices=["auto", "upper", "keep"], default="auto",
                    help="auto = UPPER for karaoke/box/pop, sentence case for clean")
    ap.add_argument("--hook", help="hook title shown from frame 0 (3-7 words)")
    ap.add_argument("--hook-dur", type=float, default=3.0, help="hook duration (s)")
    ap.add_argument("--hook-y", type=float, help="hook vertical centre (px)")
    ap.add_argument("--cta", help="on-screen call to action for the last --cta-dur s (e.g. 'SALVEAZĂ-L PENTRU MAI TÂRZIU')")
    ap.add_argument("--cta-dur", type=float, default=3.0, help="CTA duration at the end (s)")
    ap.add_argument("--avoid", help="face band to keep clear, 'Y0:Y1' in canvas px (pipeline passes it from "
                    "reframe.py); captions/hook/CTA are moved off it")
    ap.add_argument("--replace", action="append", help="fix a word everywhere: wrong=right (repeatable)")
    ap.add_argument("--no-check", action="store_true", help="report layout problems but exit 0")
    a = ap.parse_args()

    W, H, plat = vc.canvas_for(a.format)
    plat = a.platform or plat
    safe = vc.safe_box(plat, W, H)
    size, y, max_w, hook_y = defaults(W, H, a.style if a.style != "none" else "karaoke")
    size = round(a.size or size)
    y = a.y or y
    max_w = a.max_width or max_w
    avoid = tuple(float(v) for v in a.avoid.split(":")) if a.avoid else None
    W_ = vc.load_json(a.words)
    vc.assign_segments(W_["words"], W_.get("segments", []))
    vc.tidy_transcript(W_["words"])
    cuts = vc.load_json(a.cuts) if a.cuts else None
    words = apply_replacements(remap(W_["words"], cuts), a.replace)
    for w in words:
        w["w"] = vc.fix_ro(w["w"])
    upper = a.case == "upper" or (a.case == "auto" and a.style != "clean")
    b = Builder(W, H, a.style, size, y, max_w, a.accent, upper, plat)
    if avoid and not a.y and a.style != "none":
        b.y, where = caption_y(y, b.cap_half(), avoid, safe, H)
        if where:
            print(f"captions moved {where} the face ({avoid[0]:.0f}-{avoid[1]:.0f}) to y={b.y:.0f}")
    total = out_duration(cuts, words)
    has_caps = a.style != "none" and bool(words)
    if a.hook:
        b.title(a.hook, 0.0, min(a.hook_dur, total or a.hook_dur), avoid, has_caps, a.hook_y, kind="hook")
    if a.cta and total > 0:
        t0 = max(0.0, total - a.cta_dur)
        if a.hook and t0 < a.hook_dur:
            t0 = a.hook_dur
        if t0 < total - 0.5:
            b.title(a.cta, t0, total, avoid, has_caps, None, kind="cta")
    if a.style == "clean":
        b.clean_chunks(words)
    elif a.style != "none":
        mw = a.max_words or (1 if a.style == "pop" else 3)
        b.word_chunks(words, chunks_by(words, mw, a.max_chars if a.style != "pop" else 99))
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(b.text())
    if a.srt:
        with open(a.srt, "w", encoding="utf-8") as f:
            f.write(build_srt(words))
    sp = sorted(b.spans)
    over = [(x, y_) for x, y_ in zip(sp, sp[1:]) if y_[0] < x[1] - 0.011]
    print(f"{len(words)} words -> {len(b.events)} events, style {a.style}, size {size}px, canvas {W}x{H}; "
          f"{'no overlapping chunks' if not over else f'WARNING {len(over)} overlapping chunks at {over[0][1][0]:.2f}s'}")
    for t in b.titles:
        print(f"{t['kind']}: {t['t0']:.2f}-{t['t1']:.2f}s y {t['top']}-{t['bottom']}, {t['lines']} line(s) at {t['size']}px"
              + (f"; captions moved to y={t['captions_moved_to']} while it is on screen" if t["captions_moved_to"] else ""))
    for txt, sc in b.shrunk:
        print(f"long word: '{txt}' drawn at {100 * sc:.0f}% so it fits the {max_w:.0f}px line")
    boxes, _ = ass_boxes(a.out)
    if boxes:
        bx = [min(x["box"][0] for x in boxes), min(x["box"][1] for x in boxes),
              max(x["box"][2] for x in boxes), max(x["box"][3] for x in boxes)]
        print(f"measured bbox (incl. pop, outline, shadow) x {bx[0]:.0f}-{bx[2]:.0f}, y {bx[1]:.0f}-{bx[3]:.0f}; "
              f"safe zone ({plat}) x {safe[0]:.0f}-{safe[2]:.0f}, y {safe[1]:.0f}-{safe[3]:.0f}")
    probs = check_boxes(boxes, safe)
    if avoid:
        on_face = [x for x in boxes if overlap(x["box"][1], x["box"][3], avoid[0], avoid[1])]
        if on_face:
            print(f"WARNING {len(on_face)} event(s) touch the face band {avoid[0]:.0f}-{avoid[1]:.0f} "
                  f"(first '{on_face[0]['text'][:20]}' at {on_face[0]['t0']:.2f}s)")
    print(f"wrote {a.out}" + (f" and {a.srt}" if a.srt else ""))
    if over:
        probs.append(f"{len(over)} caption chunks on screen at the same time")
    for p in probs:
        print(f"FAIL {p}")
    if probs and not a.no_check:
        print("ERROR: caption layout check failed (fix: shorter hook/CTA, --size, --hook-y, --reframe wide; "
              "--no-check to keep it anyway)")
        sys.exit(3)
    print("layout check: OK (inside the safe zone, no caption under a title)")


if __name__ == "__main__":
    main()
