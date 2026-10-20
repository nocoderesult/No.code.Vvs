#!/usr/bin/env python3
"""Pregătește fonturile (găzduite local) și pozele pentru site. Se rulează o singură dată sau când schimbi o poză/un font.

  python3 musqai/web/tools/assets.py <poza_iness.png>
"""
import pathlib, re, sys, urllib.request
from io import BytesIO

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
FONTS = STATIC / "fonts"
IMG = STATIC / "assets" / "img"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
FONTS_URL = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800"
             "&family=Instrument+Serif:ital@0;1&family=Manrope:wght@400..800&display=swap")
RO = "ăâîșțĂÂÎȘȚ„”«»–—·→€"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def fonts():
    from fontTools.ttLib import TTFont
    FONTS.mkdir(parents=True, exist_ok=True)
    css = fetch(FONTS_URL).decode()
    out, files = [], []
    for subset, block in re.findall(r"/\* ([\w-]+) \*/\s*(@font-face\s*\{[^}]*\})", css):
        if subset not in ("latin", "latin-ext"):
            continue
        url = re.search(r"url\((https://[^)]+)\)", block).group(1)
        fam = re.search(r"font-family:\s*'([^']+)'", block).group(1)
        style = re.search(r"font-style:\s*(\w+)", block).group(1)
        name = f"{fam.replace(' ', '')}-{style}-{subset}.woff2"
        (FONTS / name).write_bytes(fetch(url))
        files.append((fam, style, name))
        out.append(block.replace(url, name))
    (FONTS / "fonts.css").write_text("\n".join(out) + "\n", encoding="utf-8")
    # Verificare: fiecare familie+stil trebuie să aibă toate literele românești (în latin sau latin-ext).
    cover = {}
    for fam, style, name in files:
        cmap = TTFont(FONTS / name).getBestCmap()
        cover.setdefault((fam, style), set()).update(chr(c) for c in cmap)
    bad = {k: [ch for ch in RO if ch not in v] for k, v in cover.items()}
    for k, missing in bad.items():
        print("OK " if not missing else "LIPSESC ", k, "".join(missing))
    return files


def images(src):
    from PIL import Image
    IMG.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    w, h = im.size
    print("poza:", w, h)

    def save(img, name, q=82):
        if name.endswith(".webp"):
            img.save(IMG / name, "WEBP", quality=q, method=6)
        else:
            img.save(IMG / name, "JPEG", quality=q, optimize=True, progressive=True)
        print(name, img.size, (IMG / name).stat().st_size // 1024, "KB")

    full = im.resize((960, round(960 * h / w)), Image.LANCZOS)
    save(full, "iness-960.webp", 84)
    save(full, "iness-960.jpg", 84)
    card = im.resize((600, round(600 * h / w)), Image.LANCZOS)
    save(card, "iness-600.webp", 82)
    # prim-plan pe față, pătrat
    face = im.crop((round(w * 0.15), round(h * 0.22), round(w * 0.85), round(h * 0.22) + round(w * 0.70)))
    save(face.resize((640, 640), Image.LANCZOS), "iness-fata.webp", 84)
    # imaginea pentru distribuire (1200x630)
    s = im.resize((1200, round(1200 * h / w)), Image.LANCZOS)
    top = round(s.size[1] * 0.25)
    save(s.crop((0, top, 1200, top + 630)), "og-iness.jpg", 84)


if __name__ == "__main__":
    fonts()
    if len(sys.argv) > 1:
        images(sys.argv[1])
