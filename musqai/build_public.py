#!/usr/bin/env python3
"""Construiește versiunea publică a site-ului MUSQAI, pentru Cloudflare Pages.

Pornește de la musqai/site/ (pagina din Claude) și scrie în musqai/public/:
- index.html ca document complet (lang="ro", favicon, meta pentru distribuire);
- fonturile găzduite local, ca vizitatorii să nu fie trimiși la Google Fonts;
- modul public: fără prompturi, declanșatori LoRA sau rutina de pe pod.

Rulare: python3 musqai/build_public.py
"""
import pathlib
import re
import shutil
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "site"
OUT = ROOT / "public"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
KEEP_SUBSETS = ("latin", "latin-ext")

FAVICON = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
    "<rect width='64' height='64' rx='14' fill='#121614'/>"
    "<text x='32' y='45' font-family='Georgia,serif' font-size='38' font-weight='700' text-anchor='middle' fill='#f3f5f1'>M</text>"
    "</svg>"
)

HEAD = """<!doctype html>
<html lang="ro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#121614">
<meta property="og:type" content="website">
<meta property="og:title" content="MUSQAI · Marketing Universe Studio">
<meta property="og:description" content="Ambasadori AI pentru branduri. Poze și reels noi în fiecare săptămână, etichetate corect.">
<link rel="icon" href="data:image/svg+xml,{favicon}">
<link rel="stylesheet" href="fonts/fonts.css">
<style>:root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
"""

# Textele care se schimbă pentru varianta publică: (ce caut, cu ce înlocuiesc).
BODY_SWAPS = [
    ("<span>Prototip MUSQAI</span><span>Prețurile și datele din Studio sunt de test</span>",
     "<span>MUSQAI · lansare în curând</span><span>Prețuri de lansare pentru primii clienți</span>"),
    ("© 2026 MUSQAI · prototip", "© 2026 MUSQAI"),
    ('<script src="data.js"></script>', '<script>window.MQ_PUBLIC = true;</script>\n<script src="data.js"></script>'),
]

HEADERS = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()

/fonts/*
  Cache-Control: public, max-age=31536000, immutable
"""


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def build_fonts(fonts_url):
    """Descarcă fonturile (doar latin și latin-ext, unde sunt ș, ț, ă, â, î) și scrie fonts/fonts.css."""
    css = fetch(fonts_url).decode("utf-8")
    fonts_dir = OUT / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    blocks = []
    for subset, block in re.findall(r"/\* ([\w-]+) \*/\s*(@font-face\s*\{[^}]*\})", css):
        if subset not in KEEP_SUBSETS:
            continue
        url = re.search(r"url\((https://[^)]+)\)", block).group(1)
        family = re.search(r"font-family:\s*'([^']+)'", block).group(1)
        style = re.search(r"font-style:\s*(\w+)", block).group(1)
        name = f"{family.replace(' ', '')}-{style}-{subset}.woff2"
        target = fonts_dir / name
        if not target.exists():
            target.write_bytes(fetch(url))
        blocks.append(block.replace(url, name))
    if not blocks:
        raise SystemExit("Nu am găsit fonturile în CSS-ul de la Google Fonts.")
    (fonts_dir / "fonts.css").write_text("\n".join(blocks) + "\n", encoding="utf-8")
    return len(blocks)


def main():
    page = (SRC / "index.html").read_text(encoding="utf-8")
    cut = page.index('<div class="proto">')
    head_part, body_part = page[:cut], page[cut:]

    fonts_url = re.search(r'<link rel="stylesheet" href="(https://fonts\.googleapis\.com/[^"]+)">', head_part).group(1)
    head_part = re.sub(r'<link rel="preconnect"[^>]*>\n?', "", head_part)
    head_part = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/[^"]+">\n?', "", head_part)
    head_part = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\n?', "", head_part)

    for old, new in BODY_SWAPS:
        if old not in body_part:
            raise SystemExit(f"Nu am găsit în pagină: {old!r}")
        body_part = body_part.replace(old, new)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    count = build_fonts(fonts_url)

    favicon = urllib.parse.quote(FAVICON, safe="")
    html = HEAD.format(favicon=favicon) + head_part.strip() + "\n</head>\n<body>\n" + body_part.strip() + "\n</body>\n</html>\n"
    (OUT / "index.html").write_text(html, encoding="utf-8")
    for name in ("app.js", "data.js"):
        shutil.copy(SRC / name, OUT / name)
    (OUT / "_headers").write_text(HEADERS, encoding="utf-8")
    print(f"Gata: {OUT} ({count} fonturi)")


if __name__ == "__main__":
    main()
