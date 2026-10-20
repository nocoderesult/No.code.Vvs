#!/usr/bin/env python3
"""Imaginea de distribuire (1200x630) pentru linkurile MUSQAI. Rulare: python3 musqai/web/tools/og.py"""
import pathlib
from io import BytesIO
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "static" / "fonts"
IMG = ROOT / "static" / "assets" / "img"


def ttf(name, size, wght=None):
    """Încarcă un woff2 ca TTF (din memorie) și, dacă e variabil, alege grosimea."""
    font = TTFont(FONTS / name)
    font.flavor = None
    buf = BytesIO()
    font.save(buf)
    buf.seek(0)
    f = ImageFont.truetype(buf, size)
    f.chars = set(chr(c) for c in font.getBestCmap())
    if wght is not None:
        try:
            axes = f.get_variation_axes()
            vals = []
            for a in axes:
                tag = a.get("name", b"")
                tag = tag.decode() if isinstance(tag, bytes) else str(tag)
                if "eight" in tag:
                    vals.append(wght)
                elif "ptical" in tag:
                    vals.append(min(a["maximum"], max(a["minimum"], 72)))
                else:
                    vals.append(a["default"])
            f.set_variation_by_axes(vals)
        except Exception as e:  # font fără axe: rămâne grosimea implicită
            print("variații indisponibile:", e)
    return f


def draw(dr, xy, text, fonts, fill):
    """Scrie textul literă cu literă, cu primul font care conține litera (latin sau latin-ext)."""
    x, y = xy
    for ch in text:
        f = next((f for f in fonts if ch in f.chars), fonts[0])
        dr.text((x, y), ch, font=f, fill=fill)
        x += dr.textlength(ch, font=f)


def main():
    W, H = 1200, 630
    bg = Image.new("RGB", (W, H), (10, 9, 12))
    glow = Image.new("RGB", (W, H), (10, 9, 12))
    d = ImageDraw.Draw(glow)
    d.ellipse((-260, 260, 520, 900), fill=(120, 20, 70))
    d.ellipse((260, 380, 900, 980), fill=(70, 30, 120))
    glow = glow.filter(ImageFilter.GaussianBlur(140))
    bg = Image.blend(bg, glow, 0.85)

    photo = Image.open(IMG / "iness-960.jpg").convert("RGB").resize((420, 630), Image.LANCZOS)
    mask = Image.new("L", photo.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 419, 629), radius=0, fill=255)
    bg.paste(photo, (W - 420, 0), mask)
    # trecere moale între fundal și poză
    fade = Image.new("L", (120, H))
    for x in range(120):
        ImageDraw.Draw(fade).line([(x, 0), (x, H)], fill=int(255 * (1 - x / 119)))
    dark = Image.new("RGB", (120, H), (10, 9, 12))
    bg.paste(dark, (W - 420, 0), fade)

    dr = ImageDraw.Draw(bg)
    word = [ttf("BricolageGrotesque-normal-latin.woff2", 34, 800)]
    head = [ttf("BricolageGrotesque-normal-latin.woff2", 66, 800), ttf("BricolageGrotesque-normal-latin-ext.woff2", 66, 800)]
    small = [ttf("Manrope-normal-latin.woff2", 22, 600), ttf("Manrope-normal-latin-ext.woff2", 22, 600)]
    x = 72
    draw(dr, (x, 64), "MUSQAI", word, (247, 242, 238))
    y = 170
    for line in ["Ambasadori AI", "care îți vând", "produsele."]:
        draw(dr, (x, y), line, head, (247, 242, 238))
        y += 76
    # bara în degrade
    bar = Image.new("RGB", (220, 6))
    for i in range(220):
        t = i / 219
        if t < 0.5:
            a, b, k = (255, 138, 61), (255, 45, 120), t / 0.5
        else:
            a, b, k = (255, 45, 120), (157, 92, 255), (t - 0.5) / 0.5
        ImageDraw.Draw(bar).line([(i, 0), (i, 5)], fill=tuple(int(a[j] + (b[j] - a[j]) * k) for j in range(3)))
    bg.paste(bar, (x, y + 22))
    draw(dr, (x, y + 52), "Marketing Universe Studio · Quantum AI", small, (207, 198, 192))
    draw(dr, (x, H - 70), "Conținut generat cu AI, etichetat ca atare.", small, (149, 140, 148))
    bg.save(IMG / "og.jpg", "JPEG", quality=86, optimize=True, progressive=True)
    print("og.jpg", (IMG / "og.jpg").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
