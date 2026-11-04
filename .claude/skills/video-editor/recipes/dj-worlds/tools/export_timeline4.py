"""Editable timeline for Premiere Pro / DaVinci Resolve / Final Cut from the Reel4 v2 render.
V1 = the graded shots (effects baked, no text) cut exactly as in the MP4, V2 = typography with alpha (ProRes 4444),
A1 = song stem, A2 = SFX stem. Writes FCP7 XML (Premiere + Resolve), FCPXML (Resolve + Final Cut) and a CMX3600 EDL
(V1 only), then reads every file back and checks clip count, cut points and total duration against edit_plan.json.
Media paths point at MAC_DIR so nothing needs relinking when the folder is copied there.
usage: export_timeline4.py reel4_dir clean_master.mov overlay_png_dir outdir"""
import json, os, shutil, subprocess, sys
import opentimelineio as otio

R, CLEAN, OVDIR, OUT = sys.argv[1:5]
P = json.load(open(f"{R}/pack/edit_plan.json"))
FPS, N = P["fps"], P["frames"]
NAME = "DJ_v2"
MAC_DIR = f"/Users/Shared/Claude-Edit/{NAME}"
RT = lambda f: otio.opentime.RationalTime(f, FPS)           # noqa: E731
TR = lambda a, d: otio.opentime.TimeRange(RT(a), RT(d))     # noqa: E731
os.makedirs(f"{OUT}/clips", exist_ok=True)
os.makedirs(f"{OUT}/audio", exist_ok=True)


def run(cmd):
    subprocess.run(cmd, check=True)


# media: one file per shot (frame-exact), the text layer with alpha, the two stems
shots = [s for s in P["shots"]]
for s in shots:
    n = s["to"] - s["from"]
    run(["ffmpeg", "-v", "error", "-y", "-i", CLEAN, "-vf", f"select='between(n\\,{s['from']}\\,{s['to'] - 1})',setpts=N/FRAME_RATE/TB",
         "-frames:v", str(n), "-r", str(FPS), "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p",
         "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-tag:v", "avc1", "-an", f"{OUT}/clips/{s['id']}.mp4"])
run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{OVDIR}/%03d.png", "-c:v", "prores_ks", "-profile:v", "4444",
     "-pix_fmt", "yuva444p10le", "-vendor", "apl0", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
     f"{OUT}/text_overlay_alpha.mov"])
shutil.copy(f"{R}/work/stem_song.wav", f"{OUT}/audio/song.wav")
shutil.copy(f"{R}/work/stem_sfx.wav", f"{OUT}/audio/sfx.wav")
shutil.copy(f"{R}/work/mix4b.wav", f"{OUT}/audio/mix_final.wav")


def clip(name, rel, dur, kind="video"):
    ref = otio.schema.ExternalReference(target_url="file://" + f"{MAC_DIR}/{rel}", available_range=TR(0, dur))
    return otio.schema.Clip(name=name, media_reference=ref, source_range=TR(0, dur))


tl = otio.schema.Timeline(name=NAME, global_start_time=RT(0))
v1 = otio.schema.Track(name="V1 cadre", kind=otio.schema.TrackKind.Video)
for s in shots:
    v1.append(clip(s["id"], f"clips/{s['id']}.mp4", s["to"] - s["from"]))
v2 = otio.schema.Track(name="V2 text", kind=otio.schema.TrackKind.Video)
v2.append(clip("text_overlay_alpha", "text_overlay_alpha.mov", N))
a1 = otio.schema.Track(name="A1 melodie", kind=otio.schema.TrackKind.Audio)
a1.append(clip("song", "audio/song.wav", N))
a2 = otio.schema.Track(name="A2 efecte", kind=otio.schema.TrackKind.Audio)
a2.append(clip("sfx", "audio/sfx.wav", N))
tl.tracks.extend([v1, v2, a1, a2])

otio.adapters.write_to_file(tl, f"{OUT}/{NAME}_premiere_resolve.xml", adapter_name="fcp_xml")
otio.adapters.write_to_file(tl, f"{OUT}/{NAME}.fcpxml", adapter_name="fcpx_xml")
edl_tl = otio.schema.Timeline(name=NAME, global_start_time=RT(0))
edl_tl.tracks.append(v1.clone())
otio.adapters.write_to_file(edl_tl, f"{OUT}/{NAME}_V1.edl", adapter_name="cmx_3600", rate=FPS)

# read back and verify
want = [s["from"] for s in shots] + [N]
problems = []
for fn, ad in ((f"{NAME}_premiere_resolve.xml", "fcp_xml"), (f"{NAME}.fcpxml", "fcpx_xml"), (f"{NAME}_V1.edl", "cmx_3600")):
    t = otio.adapters.read_from_file(f"{OUT}/{fn}", adapter_name=ad, **({"rate": FPS} if ad == "cmx_3600" else {}))
    vt = [tr for tr in t.tracks if tr.kind == otio.schema.TrackKind.Video]
    cl = [c for c in vt[0] if isinstance(c, otio.schema.Clip)]
    edges, pos = [], 0
    for c in vt[0]:
        edges.append(round(pos))
        pos += c.duration().rescaled_to(FPS).value
    edges.append(round(pos))
    if len(cl) != len(shots):
        problems.append(f"{fn}: {len(cl)} clips on V1, expected {len(shots)}")
    if edges != want:
        problems.append(f"{fn}: cut points {edges} != {want}")
    ntr = (len(vt), len([tr for tr in t.tracks if tr.kind == otio.schema.TrackKind.Audio]))
    print(f"{fn}: V1 clips {len(cl)}, video/audio tracks {ntr}, V1 duration {round(pos)} frames")
for s in shots:
    n = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames",
                            "-of", "csv=p=0", f"{OUT}/clips/{s['id']}.mp4"], capture_output=True, text=True).stdout.strip())
    if n != s["to"] - s["from"]:
        problems.append(f"clips/{s['id']}.mp4 has {n} frames, expected {s['to'] - s['from']}")
print("PROBLEMS:", problems if problems else "none")
sys.exit(4 if problems else 0)
