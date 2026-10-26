"""Shared helpers for the video-editor skill scripts (ffmpeg/ffprobe wrappers, media info,
formats, safe zones, Romanian text fixes, models, fonts, loudness measurement).

Every CLI script in this folder imports this module; run the scripts with python3 from anywhere
(the script's own folder is on sys.path automatically).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.request
from fractions import Fraction

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(SKILL_DIR, "assets")
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "video-editor")

# --------------------------------------------------------------------------- errors / running


class EditError(SystemExit):
    """Clean, user-facing failure (no traceback)."""

    def __init__(self, msg: str):
        super().__init__(f"ERROR: {msg}")


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def need_bin(name: str):
    if not shutil.which(name):
        raise EditError(f"'{name}' not found on PATH (install ffmpeg >= 6).")


def run(cmd, capture=False, check=True, quiet=False):
    """Run a command; on failure print the last stderr lines and raise EditError."""
    if not quiet and os.environ.get("VE_DEBUG"):
        log("+", " ".join(map(str, cmd)))
    p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if check and p.returncode != 0:
        tail = "\n".join((p.stderr or "").strip().splitlines()[-25:])
        raise EditError(f"command failed ({p.returncode}): {' '.join(map(str, cmd[:6]))} ...\n{tail}")
    return p if capture else p


def run_bytes(cmd):
    p = subprocess.run([str(c) for c in cmd], capture_output=True)
    if p.returncode != 0:
        tail = "\n".join(p.stderr.decode("utf-8", "replace").strip().splitlines()[-20:])
        raise EditError(f"command failed: {' '.join(map(str, cmd[:6]))} ...\n{tail}")
    return p.stdout


def ffmpeg_cmd(*args):
    return ["ffmpeg", "-nostdin", "-hide_banner", "-v", "error", "-y", *args]


# --------------------------------------------------------------------------- probing

NOMINAL = [23.976, 24, 25, 29.97, 30, 47.952, 48, 50, 59.94, 60, 120]


def frac(x) -> Fraction:
    if isinstance(x, Fraction):
        return x
    if isinstance(x, (int, float)):
        return Fraction(x).limit_denominator(1001000)
    s = str(x).strip()
    if "/" in s:
        n, d = s.split("/")
        return Fraction(int(n), int(d)) if int(d) else Fraction(0)
    return Fraction(s)


def snap_fps(f) -> Fraction:
    """Snap a measured frame rate to the nearest standard rate (29.97 -> 30000/1001 etc.)."""
    f = float(frac(f))
    if f <= 0:
        return Fraction(30)
    for n in (24, 25, 30, 48, 50, 60, 120):
        if abs(f - n) < 0.02 * n / 30 + 0.005:
            return Fraction(n)
        if abs(f - n * 1000 / 1001) < 0.01:
            return Fraction(n * 1000, 1001)
    return frac(f).limit_denominator(1001)


def ffprobe_json(path: str) -> dict:
    need_bin("ffprobe")
    if not os.path.exists(path):
        raise EditError(f"file not found: {path}")
    p = run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", path], capture=True)
    return json.loads(p.stdout)


def media_info(path: str) -> dict:
    """Normalized media description used by every script."""
    j = ffprobe_json(path)
    fmt = j.get("format", {})
    vs = [s for s in j["streams"] if s.get("codec_type") == "video"
          and not (s.get("disposition", {}) or {}).get("attached_pic")]
    aus = [s for s in j["streams"] if s.get("codec_type") == "audio"]
    info = {"path": os.path.abspath(path), "name": os.path.basename(path),
            "size_mb": round(int(fmt.get("size", 0) or 0) / 1e6, 1),
            "duration": float(fmt.get("duration", 0) or 0),
            "container": fmt.get("format_name"), "start_time": float(fmt.get("start_time", 0) or 0),
            "has_video": bool(vs), "has_audio": bool(aus)}
    tags = {**(fmt.get("tags") or {})}
    if vs:
        v = vs[0]
        rot = 0
        for sd in v.get("side_data_list", []) or []:
            if "rotation" in sd:
                rot = int(sd["rotation"])
        rot = int((v.get("tags") or {}).get("rotate", rot) or rot)
        sw, sh = int(v.get("width", 0)), int(v.get("height", 0))
        w, h = (sh, sw) if abs(rot) % 180 == 90 else (sw, sh)
        r = frac(v.get("r_frame_rate", "0/1"))
        avg = frac(v.get("avg_frame_rate", "0/1") or "0/1")
        vfr = bool(avg and r and abs(float(r) - float(avg)) / float(avg) > 0.003)
        fps = snap_fps(avg if avg else r)
        if vfr or fps not in [snap_fps(x) for x in NOMINAL]:
            # VFR phone clip: use the nominal rate (r_frame_rate) if it is a standard one, else the closest standard
            rs = snap_fps(r) if r else Fraction(0)
            std = [Fraction(n) for n in (24, 25, 30, 50, 60)] + [Fraction(n * 1000, 1001) for n in (24, 30, 60)]
            fps = rs if rs in std else min(std, key=lambda c: abs(float(c) - float(avg or r or 30)))
        trc = v.get("color_transfer")
        dv = any("dovi" in json.dumps(sd).lower() or "dolby" in json.dumps(sd).lower()
                 for sd in v.get("side_data_list", []) or [])
        pix = v.get("pix_fmt", "")
        bitdepth = int(v.get("bits_per_raw_sample") or (10 if "10" in pix else 12 if "12" in pix else 8))
        info.update(vcodec=v.get("codec_name"), profile=v.get("profile"), w=w, h=h, stored_w=sw, stored_h=sh,
                    rotation=rot, fps=str(fps), fps_float=round(float(fps), 3), r_frame_rate=str(r),
                    avg_frame_rate=str(avg), vfr=vfr, pix_fmt=pix, bit_depth=bitdepth,
                    color_transfer=trc, color_primaries=v.get("color_primaries"),
                    color_space=v.get("color_space"), color_range=v.get("color_range"),
                    hdr=("hlg" if trc == "arib-std-b67" else "pq" if trc == "smpte2084" else None),
                    dolby_vision=dv, full_range=(v.get("color_range") == "pc" or pix.startswith("yuvj")),
                    v_start=float(v.get("start_time", 0) or 0),
                    v_bitrate_mbps=round(int(v.get("bit_rate", 0) or 0) / 1e6, 1),
                    nb_frames=int(v.get("nb_frames", 0) or 0))
        tags.update(v.get("tags") or {})
    if aus:
        a = aus[0]
        info.update(acodec=a.get("codec_name"), sample_rate=int(a.get("sample_rate", 0) or 0),
                    channels=int(a.get("channels", 0) or 0), a_start=float(a.get("start_time", 0) or 0),
                    audio_streams=len(aus))
    tc = tags.get("timecode")
    if not tc:
        for s in j["streams"]:
            tc = tc or (s.get("tags") or {}).get("timecode")
    info["timecode"] = tc
    info["creation_time"] = tags.get("creation_time")
    return info


# --------------------------------------------------------------------------- formats / safe zones

FORMATS = {  # name: (W, H, platform-for-safe-zone)
    "reels": (1080, 1920, "reels"), "tiktok": (1080, 1920, "tiktok"), "shorts": (1080, 1920, "shorts"),
    "vertical": (1080, 1920, "universal"), "youtube": (1920, 1080, "youtube"), "landscape": (1920, 1080, "youtube"),
    "square": (1080, 1080, "none"), "portrait": (1080, 1350, "none"), "youtube4k": (3840, 2160, "youtube"),
}

# Safe zones on a 1080x1920 canvas: (top, bottom, left, right) in px. No platform publishes an organic
# spec; these are the ad-spec / measured values from reference/platforms.md. "universal" = union of all three.
SAFE_ZONES = {
    "reels": (269, 672, 65, 65),
    "tiktok": (240, 660, 120, 120),       # + right action rail: keep x < 780 below y = 840
    "shorts": (288, 672, 48, 192),
    "universal": (290, 680, 120, 192),
    "youtube": (54, 54, 96, 96),          # 16:9 title-safe-ish (5%), only the progress bar/controls matter
    "none": (90, 90, 54, 54),             # feed formats (square / 4:5): ~5% breathing room
}


def canvas_for(fmt: str):
    if fmt in FORMATS:
        return FORMATS[fmt]
    m = re.fullmatch(r"(\d+)x(\d+)", fmt or "")
    if m:
        return int(m.group(1)), int(m.group(2)), "none"
    raise EditError(f"unknown format '{fmt}'. Use one of {', '.join(FORMATS)} or WxH")


def safe_box(platform: str, W: int, H: int):
    """Return (x0, y0, x1, y1) of the safe area scaled to the canvas."""
    t, b, l, r = SAFE_ZONES.get(platform, SAFE_ZONES["none"])
    if platform in ("youtube",):
        return l * W / 1920, t * H / 1080, W - r * W / 1920, H - b * H / 1080
    sx, sy = W / 1080, H / 1920
    return l * sx, t * sy, W - r * sx, H - b * sy


# --------------------------------------------------------------------------- Romanian text

# cedilla forms -> comma-below; whisper sometimes emits Portuguese ã for Romanian ă
CEDILLA = str.maketrans({"ş": "ș", "ţ": "ț", "Ş": "Ș", "Ţ": "Ț", "ã": "ă", "Ã": "Ă"})


def fix_ro(text: str) -> str:
    """cedilla -> comma-below (correct Romanian), ã -> ă, NFC (composed ă â î ș ț)."""
    t = unicodedata.normalize("NFC", text or "")
    t = t.replace("s\u0327", "ș").replace("t\u0327", "ț").replace("S\u0327", "Ș").replace("T\u0327", "Ț")
    return unicodedata.normalize("NFC", t.translate(CEDILLA))


def upper_ro(text: str) -> str:
    return fix_ro(text).upper()


def fold(text: str) -> str:
    """lowercase, no diacritics, letters/digits/spaces only (for matching phrases)."""
    t = unicodedata.normalize("NFD", fix_ro(text).lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s-]", " ", t)).strip()


def assign_segments(words, segments):
    """Give every word the index ("si") of the Whisper segment it belongs to. New transcripts store it;
    for older words.json it is recovered from the segment times (word midpoint, nearest segment)."""
    if all("si" in w for w in words):
        return words
    by_src = {}
    for k, s in enumerate(segments):
        by_src.setdefault(s.get("src", 0), []).append((s["s"], s["e"], k))
    for w in words:
        if "si" in w:
            continue
        mid = (w["s"] + w["e"]) / 2
        cands = by_src.get(w.get("src", 0), [])
        if cands:
            w["si"] = min(cands, key=lambda c: 0 if c[0] - 0.05 <= mid <= c[1] + 0.05 else
                          min(abs(mid - c[0]), abs(mid - c[1])) + 1)[2]
    return words


END_PUNCT = (".", "!", "?", "…")


def tidy_transcript(words):
    """Sentence punctuation Whisper leaves out (words need "si", see assign_segments). Idempotent.
      * a segment that ends without punctuation (or with a comma) before a capitalised next segment gets a
        full stop: 'lui Harry Potter Vă dați seama' -> 'Potter. Vă dați seama'
      * a capitalised common word after a comma inside a sentence is lowercased ('roșu, După care' ->
        'roșu, după care') when the transcript also has it in lowercase (names/brands never are)."""
    lower_seen = {fold(w["w"]) for w in words if w["w"][:1].islower()}
    n = 0
    for a, b in zip(words, words[1:]):
        if a.get("src", 0) != b.get("src", 0):
            continue
        bw = b["w"].lstrip("„\"«(")
        if not bw[:1].isupper() or (len(bw) > 1 and bw.isupper()):
            continue
        aw = a["w"].rstrip("\"”»)")
        if aw.endswith(END_PUNCT):
            continue
        if a.get("si") is not None and a.get("si") != b.get("si"):
            a["w"] = a["w"].rstrip(",;:") + "."
            n += 1
        elif aw.endswith(",") and fold(bw) in lower_seen:
            b["w"] = b["w"].replace(bw, bw[0].lower() + bw[1:], 1)
            n += 1
    return n


# --------------------------------------------------------------------------- audio helpers


def load_audio(path: str, sr: int = 16000, af_extra: str = ""):
    """Decode audio track 0 to mono float32 at `sr`, aligned to the file's t=0 (pads late-starting audio)."""
    import numpy as np
    af = f"aresample=async=1:first_pts=0{(',' + af_extra) if af_extra else ''},aresample={sr}"
    raw = run_bytes(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-map", "0:a:0", "-ac", "1",
                     "-af", af, "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32).copy()


def envelope_db(path: str, rnn: str | None = None, hop: float = 0.01, sr: int = 16000):
    """10 ms RMS envelope in dBFS (smoothed 30 ms), computed on high-passed (optionally RNNoise-denoised) audio.
    Note: arnndn needs 48 kHz; don't pass -ar together with aresample (silently breaks the time axis)."""
    import numpy as np
    pre = "aresample=48000,highpass=f=80" + (f",arnndn=m='{rnn}'" if rnn else "")
    a = load_audio(path, sr, pre)
    h = int(sr * hop)
    n = len(a) // h
    if n == 0:
        return np.array([-120.0]), hop
    rms = np.sqrt(np.mean(a[: n * h].reshape(n, h) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    db = np.convolve(db, np.ones(3) / 3, mode="same")
    return db, hop


def speech_threshold(db):
    import numpy as np
    floor = float(np.percentile(db, 10))
    return max(floor + 10, float(np.percentile(db, 60)) - 25), floor


def ebur128(path: str, stream: str = "0:a:0") -> dict:
    """Integrated loudness / LRA / true peak as measured by ffmpeg's EBU R128 meter."""
    p = run(["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-i", path, "-map", stream,
             "-af", "ebur128=peak=true", "-f", "null", "-"], capture=True)
    s = p.stderr[p.stderr.rfind("Summary:"):]
    def g(k):
        m = re.search(k + r":\s+(-?[\d.]+|-inf)", s)
        return float(m.group(1)) if m and m.group(1) != "-inf" else float("-inf")
    return {"I": g(r"\bI"), "LRA": g("LRA"), "TP": g("Peak")}


# --------------------------------------------------------------------------- models / fonts

MODELS = {
    "yunet": ("face_detection_yunet_2023mar.onnx",
              "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
              "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4"),
    "rnnoise": ("rnnoise_sh.rnnn",
                "https://raw.githubusercontent.com/GregorR/rnnoise-models/master/somnolent-hogwash-2018-09-01/sh.rnnn",
                "70bb6685eb0c2a1d18e2918dca3fbfbd39317010b1802eb1b6ea73a92f3fdec0"),
}


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def model_path(key: str) -> str | None:
    """Bundled model (assets/models) -> cache -> download (sha256-checked). None if unavailable."""
    fname, url, sha = MODELS[key]
    for p in (os.path.join(ASSETS, "models", fname), os.path.join(CACHE, "models", fname)):
        if os.path.exists(p):
            return p
    dst = os.path.join(CACHE, "models", fname)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    try:
        log(f"downloading {key} model ...")
        urllib.request.urlretrieve(url, dst + ".part")
        if _sha(dst + ".part") != sha:
            os.unlink(dst + ".part")
            log(f"warning: {key} model checksum mismatch; skipping")
            return None
        os.replace(dst + ".part", dst)
        return dst
    except Exception as e:  # network blocked etc.
        log(f"warning: could not download {key} model ({e})")
        return None


FONT_WEIGHTS = {  # weight -> (fontconfig query, ASS Fontname, ASS Bold flag). libass resolves via fontconfig.
    "Black": ("Inter:style=Black", "Inter Black", 0),       # verified: (Inter Black, 400, 0) -> Inter-Black.otf
    "ExtraBold": ("Inter:style=ExtraBold", "Inter ExtraBold", 0),
    "Bold": ("Inter:style=Bold", "Inter", 1),
    "SemiBold": ("Inter:style=SemiBold", "Inter SemiBold", 0),
}


def font_for(weight: str = "Black"):
    """(ASS Fontname, ASS Bold flag, font file, pil_ratio) for Inter <weight>; DejaVu Sans Bold fallback.
    pil_ratio converts an ASS font size to a PIL size (libass size = ascent+descent, Inter: 0.8157)."""
    q, fam, bold = FONT_WEIGHTS.get(weight, FONT_WEIGHTS["Black"])
    f = ""
    try:
        f = run(["fc-match", "-f", "%{file}", q], capture=True, check=False).stdout.strip()
    except FileNotFoundError:
        pass
    if not (f and "inter" in os.path.basename(f).lower()):
        f = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if not os.path.exists(f):
            raise EditError("no usable font found (need Inter or DejaVu Sans)")
        log(f"warning: Inter {weight} not found, falling back to DejaVu Sans Bold")
        fam, bold = "DejaVu Sans", 1
    if "inter" in os.path.basename(f).lower():
        return fam, bold, f, 0.8157  # measured against libass rendering
    from PIL import ImageFont
    asc, desc = ImageFont.truetype(f, 1000).getmetrics()
    return fam, bold, f, 1000.0 / (asc + desc)


def ass_filter_path(path: str) -> str:
    """Escape a path for use inside subtitles=filename='...' in a filtergraph. Only safe for paths without an
    apostrophe (ffmpeg's two escaping levels make a quoted ' unreliable); use filter_file() for anything a user named."""
    return os.path.abspath(path).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


_SAFE_PATH = re.compile(r"[A-Za-z0-9/_.+-]+")


def filter_file(path: str, tmpdir: str, name: str) -> str:
    """Path to put inside a filtergraph argument (subtitles=, sendcmd=, vidstab ...). Project folders are named
    after the user's title ("Reel lui Ion's", diacritics, colons), and an apostrophe breaks ffmpeg's filter
    parser, so anything that isn't plain ASCII is copied into the render's temp dir under `name` first."""
    p = os.path.abspath(path)
    if not _SAFE_PATH.fullmatch(p):
        dst = os.path.join(tmpdir, name)
        shutil.copy(p, dst)
        p = dst
        if not _SAFE_PATH.fullmatch(p):
            raise EditError(f"temp dir {tmpdir} has characters ffmpeg filters can't take; set TMPDIR=/tmp")
    return ass_filter_path(p)


# --------------------------------------------------------------------------- json helpers


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def fmt_tc(t: float) -> str:
    t = max(0.0, t)
    return f"{int(t // 60):02d}:{t % 60:05.2f}"


def align_segments(segments, fps: Fraction):
    """Snap segment boundaries to the output frame grid (exact Fractions). Drops empty segments.
    Every renderer/exporter uses this, so audio, video, captions and timelines agree to the sample."""
    out = []
    for sg in segments:
        a, b = round(Fraction(sg["s"]).limit_denominator(10**6) * fps), round(Fraction(sg["e"]).limit_denominator(10**6) * fps)
        if b > a:
            out.append({**sg, "fs": a, "fe": b, "S": Fraction(a) / fps, "E": Fraction(b) / fps})
    return out


def runs_of(segments):
    """Group consecutive segments that come from the same source in increasing time order. Each run can be
    decoded with one sequential pass (split+trim) without buffering frames; a reorder starts a new run."""
    runs = []
    for sg in segments:
        if runs and runs[-1]["src"] == sg["src"] and sg["S"] >= runs[-1]["segs"][-1]["E"]:
            runs[-1]["segs"].append(sg)
        else:
            runs.append({"src": sg["src"], "segs": [sg]})
    return runs
