#!/usr/bin/env python3
"""Render cuts.json to a finished MP4 in ONE encode: normalize -> reframe -> cut -> punch-ins -> b-roll ->
grade -> burned captions -> H.264/AAC export (or only the cut audio with --audio-only).

Sync: every cut point is snapped to the output frame grid and rendered with trim/atrim + concat in a single
filtergraph (measured 0.1 ms A/V offset over 49 cuts; select/aselect drifted up to 185 ms, per-segment AAC
files up to 198 ms). 6 ms audio micro-fades at each cut prevent clicks.
Phone footage: VFR -> CFR (fps filter + aresample async), rotation auto-applied, HDR HLG/PQ tone-mapped to
SDR BT.709 (zscale npl=203 + mobius), full-range / BT.601 converted to TV-range BT.709, mono -> stereo.
Video that starts after the audio (stream-copy trims, screen recordings, some Android files) is padded with
its first frame (fps start_time=0), the same way aresample first_pts=0 pads late audio, so both share t=0.
Reframe modes: track (face path from reframe.py), wide (face track + blurred fill, for close-up selfies whose
face would fill > 40% of a 9:16 crop: face scaled to ~30% of the height at 0.40 H, less upscaling), center,
blur (blurred fill), fit (black bars), none (cover). auto picks track / wide / blur.
Zoom cuts (--zoom-cuts): segments carrying "zooms" (plan_cuts.py) are split there into back-to-back shots with
no time jump, and the framing alternates 100% / --punch, so a long take still changes picture every 2-4 s.
Reordered segments (cold open) are handled by opening the source again for each out-of-order run.
After encoding, video and audio stream durations are compared (must match within one frame).

Examples:
  render_cuts.py work/cuts.json --audio-only work/cut.wav
  render_cuts.py work/cuts.json -o out/final.mp4 --format reels --reframe track --track 0=work/track_0.json \\
      --ass work/captions.ass --audio work/mix.wav --punch 1.12
  render_cuts.py work/cuts.json -o out/yt.mp4 --format youtube --grade natural
  render_cuts.py work/cuts.json -o out/r.mp4 --format reels --reframe blur --broll work/broll.json
broll.json: [{"path": "b.mp4", "at": 3.2, "dur": 2.0, "in": 5.0}, {"path": "photo.jpg", "at": 9, "dur": 2.5, "zoom": 1.08}]
  ("at" = OUTPUT seconds; the voice keeps playing under the b-roll.)
"""
import argparse
import math
import os
import tempfile
import time
from fractions import Fraction

import vcommon as vc

GRADES = {
    "none": "",
    "natural": "eq=contrast=1.04:saturation=1.07",
    "punchy": "eq=contrast=1.08:saturation=1.15",
    "bright": "eq=brightness=0.025:gamma=1.12:contrast=1.03:saturation=1.06",
}
TONEMAP = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=mobius:param=0.5:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv:d=error_diffusion,format=yuv420p")
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")


def f6(x):
    return f"{float(x):.6f}"


def colour_norm(info, H):
    """Explicit range/matrix conversion to TV-range BT.709 (swscale assumes BT.601 for untagged input)."""
    if info.get("hdr"):
        return TONEMAP
    rng = "pc" if info.get("full_range") else "tv"
    cs = info.get("color_space")
    mat = "bt601" if cs in ("bt470bg", "smpte170m") else "bt709" if cs == "bt709" else \
        ("bt709" if max(info["w"], info["h"]) >= 1280 else "bt601")
    return f"scale=in_range={rng}:out_range=tv:in_color_matrix={mat}:out_color_matrix=bt709,format=yuv420p"


WIDE_FACE = 0.40      # auto: a face taller than this fraction of the 9:16 crop -> "wide" framing
WIDE_TARGET = 0.30    # wide: face height as a fraction of the canvas (room for captions under the chin)
WIDE_POS = 0.40       # wide: face centre at this fraction of the canvas height


def wide_geometry(info, W, H, track):
    """Scale k (canvas px per source px), crop width (source px), band height/top (canvas px) for 'wide'."""
    sw, sh = info["w"], info["h"]
    fh = max(0.05, float(track.get("face_h", 0.3)))
    k = WIDE_TARGET * H / (fh * sh)
    k = min(k, H / sh)                              # never tighter than a full-height crop (= plain track)
    k = max(k, W / sw + 1e-6)                       # the crop can't be wider than the source
    cw = int(round(W / k / 2) * 2)
    bh = int(round(sh * k / 2) * 2)
    top = int(round((WIDE_POS * H - float(track.get("face_y", 0.45)) * bh) / 2) * 2)
    top = max(0, min(H - bh, top))
    return k, cw, bh, top


def plan_reframe(info, W, H, mode, track):
    """Return (filter, out_is_canvas, anchor_x, anchor_y, mode). Filter 'TRACK'/'WIDE' = built by the caller."""
    sw, sh = info["w"], info["h"]
    same = abs(sw / sh - W / H) < 0.01
    faces = bool(track and track.get("detect_ratio", 0) >= 0.25)
    if mode == "auto":
        keep = min((W / H) / (sw / sh), (sw / sh) / (W / H))  # fraction of the source a crop would keep
        if same:
            mode = "none"
        elif faces and (sw / sh > W / H or keep >= 0.5):
            mode = "track"   # 16:9 -> 9:16 talking head, or 9:16 -> 1:1 / 4:5
            if sw / sh > W / H and track.get("face_h", 0) > WIDE_FACE:
                mode = "wide"  # close-up selfie: a full-height crop would be an extreme close-up, heavily upscaled
        else:
            mode = "blur"    # no face, or a crop would throw away too much (9:16 -> 16:9)
    if mode == "wide" and not (faces and sw / sh > W / H):
        mode = "track" if faces else "blur"
    ax, ay = 0.5, 0.42
    if track:
        ay = track.get("face_y", 0.42)
    if mode == "none" or (same and mode in ("track", "center", "wide")):
        return f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}", True, ax, ay, "none"
    if mode == "fit":
        return (f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black",
                True, 0.5, 0.5, mode)
    if mode == "wide":
        k, cw, bh, top = wide_geometry(info, W, H, track)
        return "WIDE", True, 0.5, (top + float(track.get("face_y", 0.45)) * bh) / H, mode
    if mode == "blur":
        bw, bh = max(2, W // 4 // 2 * 2), max(2, H // 4 // 2 * 2)
        f = (f"split[bgA][fgA];[bgA]scale={bw}:{bh}:force_original_aspect_ratio=increase,crop={bw}:{bh},"
             f"gblur=sigma=12,eq=brightness=-0.06,scale={W}:{H}[bgB];[fgA]scale={W}:{H}:force_original_aspect_ratio="
             f"decrease:flags=lanczos[fgB];[bgB][fgB]overlay=(W-w)/2:(H-h)/2")
        if sw / sh > W / H:   # landscape into taller canvas: fg is a horizontal band in the middle
            fgh = W * sh / sw
            ay = ((H - fgh) / 2 + ay * fgh) / H
        return f, True, 0.5, ay, mode
    # crop modes (output = crop at source resolution, scaled per segment so punch-ins keep resolution)
    if sw / sh > W / H:
        cw, ch, axis = int(round(sh * W / H / 2) * 2), sh, "x"
    else:
        cw, ch, axis = sw, int(round(sw * H / W / 2) * 2), "y"
    if mode == "track" and track:
        if track.get("axis") != axis:
            raise vc.EditError(f"track file was made for another target aspect ({track.get('target')}); re-run reframe.py")
        return ("TRACK", False, 0.5, ay if axis == "x" else track.get("face_pos", 0.38), mode)
    x0, y0 = (sw - cw) // 2, (sh - ch) // 2
    return f"crop={cw}:{ch}:{x0}:{y0}", False, 0.5, (ay if axis == "x" else 0.42), "center"


def upscale(info, W, H, mode, track):
    """Canvas px per source px of the main picture (>2 looks soft on a phone)."""
    sw, sh = info["w"], info["h"]
    if mode == "wide":
        return wide_geometry(info, W, H, track)[0]
    if mode in ("track", "center"):
        return H / sh if sw / sh > W / H else W / sw
    if mode in ("blur", "fit"):
        return min(W / sw, H / sh)
    return max(W / sw, H / sh)


def face_band(info, track, W, H, mode):
    """Face band (brows..chin) in canvas px, so the hook/captions never cover eyes or mouth."""
    if not track or track.get("detect_ratio", 0) < 0.25:
        return None
    fy, fh = track["face_y"], track["face_h"]
    sw, sh = info["w"], info["h"]
    if mode == "wide":
        k, cw, bh, top = wide_geometry(info, W, H, track)
        cy, h = top + fy * bh, fh * bh
    elif mode == "blur" and sw / sh > W / H:
        fgh = W * sh / sw
        off = (H - fgh) / 2
        cy, h = off + fy * fgh, fh * fgh
    elif mode in ("track", "center", "none") and sw / sh >= W / H:
        cy, h = fy * H, fh * H
    elif mode == "track":   # vertical crop: face placed at face_pos of the frame height
        ch = sw * H / W
        cy, h = track.get("face_pos", 0.38) * H, fh * sh / ch * H
    else:
        return None
    return round(cy - 0.25 * h), round(cy + 0.55 * h)


def write_sendcmd(track, info, fps, path, name, crop_w=None):
    """Face path -> sendcmd file. crop_w (wide mode): re-centre the path for a wider crop."""
    tf = float(vc.frac(track.get("path_fps", info["fps"])))
    axis = track["axis"]
    pos = track["pos"]
    cw, ch = track["crop_w"], track["crop_h"]
    if crop_w:
        lim = info["w"] - crop_w
        pos = [int(max(0, min(lim, v + track["crop_w"] / 2 - crop_w / 2))) for v in pos]
        cw, ch = crop_w, info["h"]
    with open(path, "w") as f:
        last = None
        for k, v in enumerate(pos):
            if v != last:
                f.write(f"{k / tf:.4f} {name} {axis} {v};\n")
                last = v
    p0 = pos[0] if pos else 0
    x0, y0 = (p0, 0) if axis == "x" else (0, p0)
    return f"sendcmd=f='{vc.ass_filter_path(path)}',crop@{name.split('@')[1]}=w={cw}:h={ch}:x={x0}:y={y0}"


def stabilize_pass(info, fps, tmp, idx):
    trf = os.path.join(tmp, f"stab{idx}.trf")
    vc.run(vc.ffmpeg_cmd("-i", info["path"], "-vf", f"fps={fps}:start_time=0,vidstabdetect=shakiness=5:accuracy=15:"
                         f"result='{vc.ass_filter_path(trf)}'", "-f", "null", "-"))
    return f"vidstabtransform=input='{vc.ass_filter_path(trf)}':smoothing=15:optzoom=1:zoom=0:interpol=bicubic"


def shots_of(g, fps, zoom_cuts):
    """Frame ranges [(fs, fe)] of the shots inside one aligned segment (zoom-cut points, >= 0.5 s apart)."""
    fs, fe = g["fs"], g["fe"]
    if not zoom_cuts:
        return [(fs, fe)]
    pts = []
    for z in g.get("zooms") or []:
        f = round(Fraction(z).limit_denominator(10 ** 6) * fps)
        if f - (pts[-1] if pts else fs) >= 0.5 * fps and fe - f >= 0.5 * fps:
            pts.append(f)
    b = [fs] + pts + [fe]
    return list(zip(b[:-1], b[1:]))


def stream_durations(path):
    j = vc.ffprobe_json(path)
    d = {}
    for st in j["streams"]:
        if st.get("codec_type") in ("video", "audio") and st["codec_type"] not in d:
            d[st["codec_type"]] = float(st.get("duration", 0) or 0)
    return d


def build(a):
    cuts = vc.load_json(a.cuts)
    fps = vc.frac(a.fps or cuts["fps"])
    segs = vc.align_segments(cuts["segments"], fps)
    if not segs:
        raise vc.EditError("cuts.json has no segments")
    infos = [vc.media_info(s["path"]) for s in cuts["sources"]]
    total = sum(g["E"] - g["S"] for g in segs)
    tracks = {}
    for t in a.track or []:
        k, p = t.split("=", 1) if "=" in t else ("0", t)
        tracks[int(k)] = vc.load_json(p)
    if a.format == "source":
        v0 = next((i for i in infos if i.get("has_video")), None)
        if not v0:
            raise vc.EditError("no video source")
        W, H = v0["w"] // 2 * 2, v0["h"] // 2 * 2
    else:
        W, H, _ = vc.canvas_for(a.format)
    runs = vc.runs_of(segs)
    tmp = tempfile.mkdtemp(prefix="ve_render_")
    inputs, graph = [], []
    vlabels, alabels = [], []
    want_video = not a.audio_only
    want_audio = a.audio_only or not a.audio
    zoom_cuts = a.zoom_cuts == "on" or (a.zoom_cuts == "auto" and H > W * 1.2)
    seg_no = shot_no = 0
    info_lines = []
    stab = {}
    punch_src = {}
    for r, run in enumerate(runs):
        si = run["src"]
        info = infos[si]
        k = len(run["segs"])
        shots = [shots_of(g, fps, zoom_cuts) for g in run["segs"]]
        nv = sum(len(x) for x in shots)
        idx = inputs.count("-i")
        inputs += ["-i", info["path"]]
        if want_video:
            if not info.get("has_video"):
                raise vc.EditError(f"{info['name']} has no video")
            rf, is_canvas, ax, ay, mode = plan_reframe(info, W, H, a.reframe, tracks.get(si))
            if rf == "TRACK":
                rf = write_sendcmd(tracks[si], info, fps, os.path.join(tmp, f"rf{r}.cmd"), f"crop@rf{r}")
            elif rf == "WIDE":
                kk, cw, bh, top = wide_geometry(info, W, H, tracks[si])
                sc = write_sendcmd(tracks[si], info, fps, os.path.join(tmp, f"rf{r}.cmd"), f"crop@rf{r}", crop_w=cw)
                bw_, bh_ = max(2, W // 4 // 2 * 2), max(2, H // 4 // 2 * 2)
                rf = (f"split[bgA][fgA];[bgA]scale={bw_}:{bh_}:force_original_aspect_ratio=increase,crop={bw_}:{bh_},"
                      f"gblur=sigma=12,eq=brightness=-0.06,scale={W}:{H}[bgB];[fgA]{sc},scale={W}:{bh}:flags=lanczos[fgB];"
                      f"[bgB][fgB]overlay=0:{top}")
            rf = rf.replace("bgA", f"bgA{r}").replace("fgA", f"fgA{r}").replace("bgB", f"bgB{r}").replace("fgB", f"fgB{r}")
            pre = [f"fps={fps}:start_time=0", colour_norm(info, H)]
            if a.stabilize:
                if si not in stab:
                    stab[si] = stabilize_pass(info, fps, tmp, si)
                pre.append(stab[si])
            if a.vdenoise:
                pre.append("hqdn3d=1.5:1.5:6:6")
            pre.append(rf)
            chain = ",".join(pre)
            graph.append(f"[{idx}:v]{chain},setsar=1,split={nv}" + "".join(f"[r{r}v{j}]" for j in range(nv)))
            up = upscale(info, W, H, mode, tracks.get(si))
            if si not in punch_src:
                p_ = a.punch
                if up > 2.0 and a.punch > 1.05:
                    p_ = 1.05   # already soft: a 12% punch on top of a >2x upscale looks blurry
                punch_src[si] = p_
            if r == 0 or runs[r - 1]["src"] != si:
                info_lines.append(f"src[{si}] {info['name']} {info['w']}x{info['h']} -> {W}x{H} reframe={mode} "
                                  f"upscale {up:.2f}x{' HDR->SDR' if info.get('hdr') else ''}"
                                  f"{' VFR->CFR' if info.get('vfr') else ''}"
                                  f"{' video starts %.2fs after audio: padded' % (info.get('v_start', 0) - info.get('a_start', 0)) if info.get('has_audio') and info.get('v_start', 0) - info.get('a_start', 0) > 0.02 else ''}")
                if up > 2.0:
                    info_lines.append(f"WARN src[{si}] upscale {up:.2f}x ({info['w']}x{info['h']} source): soft on a "
                                      f"phone; punch-in capped at {punch_src[si]:.2f}" +
                                      ("" if mode != "track" else "; a wider framing needs --reframe wide or blur"))
        if want_audio:
            if info.get("has_audio"):
                graph.append(f"[{idx}:a]aresample=48000:async=1:first_pts=0,aformat=sample_fmts=fltp:"
                             f"channel_layouts=stereo,asplit={k}" + "".join(f"[r{r}a{j}]" for j in range(k)))
        vj = 0
        for j, g in enumerate(run["segs"]):
            d = g["E"] - g["S"]
            if want_video:
                for fs_, fe_ in shots[j]:
                    S_, E_ = Fraction(fs_) / fps, Fraction(fe_) / fps
                    sd = E_ - S_
                    zoom = ""
                    p = punch_src.get(si, a.punch)
                    punched = p > 1.0 and a.punch_every > 0 and shot_no % a.punch_every == a.punch_every - 1 \
                        and sd >= 0.6
                    if punched:
                        zoom = (f",crop=w='trunc(iw/{p}/2)*2':h='trunc(ih/{p}/2)*2':"
                                f"x='max(0,min(iw-ow,{ax}*iw-ow/2))':y='max(0,min(ih-oh,{ay}*ih-oh/2))'")
                    push = ""
                    if a.push and not punched and sd >= 4.0:
                        n = max(1, int(float(sd) * float(fps)))
                        Z = f"(1+{a.push - 1:.4f}*min(in/{n},1))"
                        push = (f",perspective=x0='W/2-W/2/{Z}':y0='H/2-H/2/{Z}':x1='W/2+W/2/{Z}':y1='H/2-H/2/{Z}':"
                                f"x2='W/2-W/2/{Z}':y2='H/2+H/2/{Z}':x3='W/2+W/2/{Z}':y3='H/2+H/2/{Z}':"
                                f"interpolation=linear:eval=frame")
                    graph.append(f"[r{r}v{vj}]trim=start={f6(S_)}:end={f6(E_)},setpts=PTS-STARTPTS{zoom},"
                                 f"scale={W}:{H}:flags=lanczos,setsar=1{push}[v{shot_no}]")
                    vlabels.append(f"[v{shot_no}]")
                    vj += 1
                    shot_no += 1
            if want_audio:
                fade = 0.006 if d > 0.05 else 0
                af = f",afade=t=in:d={fade},afade=t=out:st={f6(d - Fraction(fade).limit_denominator(1000))}:d={fade}" \
                    if fade else ""
                if info.get("has_audio"):
                    graph.append(f"[r{r}a{j}]atrim=start={f6(g['S'])}:end={f6(g['E'])},asetpts=PTS-STARTPTS{af}[a{seg_no}]")
                else:
                    graph.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={f6(d)},aformat=sample_fmts=fltp[a{seg_no}]")
                alabels.append(f"[a{seg_no}]")
            seg_no += 1
    n = seg_no
    if want_video:
        graph.append("".join(vlabels) + f"concat=n={len(vlabels)}:v=1:a=0[vcat]")
        cur = "vcat"
        # b-roll overlays (output timeline)
        for bi, b in enumerate(vc.load_json(a.broll) if a.broll else []):
            bidx = inputs.count("-i")
            bp, at, dur = b["path"], float(b["at"]), float(b["dur"])
            if bp.lower().endswith(IMG_EXT):
                inputs += ["-loop", "1", "-framerate", str(fps), "-t", f6(dur), "-i", bp]
            else:
                inputs += ["-ss", f6(b.get("in", 0)), "-t", f6(dur), "-i", bp]
            kb = ""
            z = float(b.get("zoom", 1.08 if bp.lower().endswith(IMG_EXT) else 1.0))
            if z > 1.0:
                nfr = max(1, int(dur * float(fps)))
                Z = f"(1+{z - 1:.4f}*min(in/{nfr},1))"
                kb = (f",perspective=x0='W/2-W/2/{Z}':y0='H/2-H/2/{Z}':x1='W/2+W/2/{Z}':y1='H/2-H/2/{Z}':"
                      f"x2='W/2-W/2/{Z}':y2='H/2+H/2/{Z}':x3='W/2+W/2/{Z}':y3='H/2+H/2/{Z}':interpolation=linear:eval=frame")
            graph.append(f"[{bidx}:v]fps={fps},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
                         f"crop={W}:{H},setsar=1,format=yuv420p{kb},setpts=PTS-STARTPTS+{at:.6f}/TB[b{bi}]")
            graph.append(f"[{cur}][b{bi}]overlay=eof_action=pass:enable='between(t,{at:.3f},{at + dur:.3f})'[ov{bi}]")
            cur = f"ov{bi}"
        post = []
        if GRADES.get(a.grade):
            post.append(GRADES[a.grade])
        if a.ass:
            post.append(f"subtitles=filename='{vc.filter_file(a.ass, tmp, 'captions.ass')}'")
        post.append("format=yuv420p,setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709")
        graph.append(f"[{cur}]" + ",".join(post) + "[vout]")
    if want_audio:
        graph.append("".join(alabels) + f"concat=n={n}:v=0:a=1[aout]")
    gfile = os.path.join(tmp, "graph.txt")
    with open(gfile, "w") as f:
        f.write(";\n".join(graph))

    if a.audio_only:
        cmd = vc.ffmpeg_cmd(*inputs, "-filter_complex_script", gfile, "-map", "[aout]", "-ar", "48000",
                            "-c:a", "pcm_s24le", "-t", f6(total), a.audio_only)
        out = a.audio_only
    else:
        if a.audio:
            ext_idx = inputs.count("-i")
            inputs += ["-i", a.audio]
            amap = ["-map", f"{ext_idx}:a:0"]
        else:
            amap = ["-map", "[aout]"]
        F = float(fps)
        big = W * H > 1920 * 1080 * 1.1
        if a.gop == "youtube":
            maxrate = 60 if big else (20 if F > 31 else 16)
        else:  # social apps re-encode to ~2-8 Mbps; above ~10 Mbps only the file grows
            maxrate = 40 if big else (14 if F > 31 else 10)
        crf = a.crf if a.crf is not None else (18 if a.gop == "youtube" else 20)
        gop = max(1, math.ceil(F / 2)) if a.gop == "youtube" else int(round(2 * F))
        level = "5.1" if big else "4.2"
        cmd = vc.ffmpeg_cmd(*inputs, "-filter_complex_script", gfile, "-map", "[vout]", *amap,
                            "-c:v", "libx264", "-preset", a.preset, "-crf", str(crf), "-maxrate", f"{maxrate}M",
                            "-bufsize", f"{2 * maxrate}M", "-profile:v", "high", "-level:v", level, "-pix_fmt", "yuv420p",
                            "-g", str(gop), "-keyint_min", str(max(1, gop // 2)), "-bf", "2", "-r", str(fps),
                            "-fps_mode", "cfr", "-colorspace", "bt709", "-color_primaries", "bt709",
                            "-color_trc", "bt709", "-color_range", "tv",
                            "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
                            "-t", f6(total), "-movflags", "+faststart", a.out)
        out = a.out
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    t0 = time.time()
    vc.run(cmd)
    el = time.time() - t0
    for l in info_lines:
        print(l)
    extra = f", {len(vlabels)} shots ({len(vlabels) - n} zoom cuts)" if want_video and len(vlabels) != n else ""
    print(f"{n} segments in {len(runs)} run(s){extra}, {float(total):.3f}s @ {fps} fps, rendered in {el:.1f}s -> {out}")
    if not a.audio_only:
        d = stream_durations(out)
        vd, ad = d.get("video", 0), d.get("audio", 0)
        size_mb = os.path.getsize(out) / 1e6
        print(f"streams: video {vd:.3f}s, audio {ad:.3f}s; {size_mb:.1f} MB ({8 * size_mb / max(vd, 0.01):.1f} Mbps)")
        if ad and abs(vd - ad) > 1 / float(fps) + 0.03:
            raise vc.EditError(f"A/V length mismatch in {out}: video {vd:.3f}s vs audio {ad:.3f}s "
                               f"({1000 * (ad - vd):+.0f} ms) - picture and sound would drift; check the source "
                               f"start times (probe.py) and the --audio file length")
    if os.environ.get("VE_KEEP_TMP"):
        print("graph:", gfile)
    return out, float(total)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cuts", help="cuts.json from plan_cuts.py")
    ap.add_argument("-o", "--out", help="output MP4")
    ap.add_argument("--audio-only", metavar="WAV", help="only render the cut source audio (48k/24-bit) for mastering")
    ap.add_argument("--format", default="source",
                    help="reels/tiktok/shorts/vertical (1080x1920), youtube (1920x1080), square, portrait, WxH, source")
    ap.add_argument("--reframe", choices=["auto", "track", "wide", "center", "blur", "fit", "none"], default="auto",
                    help="auto = track, wide when the face would fill > 40%% of a 9:16 crop, blur without a face")
    ap.add_argument("--track", action="append", help="SRC=track.json from reframe.py (repeatable), e.g. 0=work/track_0.json")
    ap.add_argument("--ass", help="captions .ass to burn in")
    ap.add_argument("--audio", help="replacement audio (mastered/mixed WAV aligned to the cut timeline)")
    ap.add_argument("--punch", type=float, default=1.0, help="punch-in zoom on every Nth segment (1.12 typical; 1 = off)")
    ap.add_argument("--punch-every", type=int, default=2, help="punch every Nth shot (2)")
    ap.add_argument("--zoom-cuts", choices=["auto", "on", "off"], default="auto",
                    help="split long segments at their 'zooms' points (plan_cuts.py) into shots with alternating "
                         "framing; auto = on for vertical canvases")
    ap.add_argument("--push", type=float, default=0, help="slow push-in on long (>=4 s) unpunched segments, e.g. 1.06")
    ap.add_argument("--broll", help="broll.json (see above)")
    ap.add_argument("--grade", choices=list(GRADES), default="none")
    ap.add_argument("--vdenoise", action="store_true", help="hqdn3d for noisy low-light footage")
    ap.add_argument("--stabilize", action="store_true", help="vidstab 2-pass (handheld footage; slower)")
    ap.add_argument("--fps", help="output fps (default: cuts.json fps)")
    ap.add_argument("--crf", type=int, help="x264 CRF (default 20 social with maxrate 10M, 18 with --gop youtube)")
    ap.add_argument("--preset", default="medium", help="x264 preset (medium; slow = smaller file, 2x time)")
    ap.add_argument("--gop", choices=["social", "youtube"], default="social",
                    help="youtube = closed GOP of half the frame rate (YouTube spec); social = 2 s")
    a = ap.parse_args()
    if not a.out and not a.audio_only:
        ap.error("need -o OUT.mp4 or --audio-only OUT.wav")
    if a.push and a.push < 1:
        ap.error("--push must be > 1 (e.g. 1.06)")
    build(a)


if __name__ == "__main__":
    main()
