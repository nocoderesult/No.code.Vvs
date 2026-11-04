"""Effect events + captions on the output clock, from work/timeline.json.
Writes work/events.json (compositor + audio) and <remotion>/src/data.json (graphics).
usage: events.py reel3_dir remotion_dir"""
import json, sys
import numpy as np

R, RV = sys.argv[1], sys.argv[2]
tl = json.load(open(f"{R}/work/timeline.json"))
FPS = tl["fps"]
words = tl["words"]
frames = tl["frames"]
segs = {s["id"]: s for s in tl["segments"]}


def seg_t(sid, edge="start"):
    s = segs[sid]
    return (s["out_start"] + (0 if edge == "start" else s["n"])) / FPS


def w(sid, text, nth=0):
    """Output start time of the nth occurrence of `text` (prefix match, case-insensitive) inside segment sid."""
    hits = [x for x in words if x["seg"] == sid and x["w"].lower().strip(",.?!").startswith(text.lower())]
    return hits[nth]["s"]


def w_end(sid, text, nth=0):
    hits = [x for x in words if x["seg"] == sid and x["w"].lower().strip(",.?!").startswith(text.lower())]
    return hits[nth]["e"]


def seg_face(sid):
    s = segs[sid]
    f = np.median(np.array([fr["face"] for fr in frames[s["out_start"]:s["out_start"] + s["live"]]]), 0)
    return [round(float(x), 4) for x in f]


ev = {}
# 1 text behind the head: "AI" through the hook, then "+5" for "mai sunt încă 5"
ev["behind"] = [
    dict(text="AI", start=0.0, end=w("C", "mai") - 0.12, rise=0.42, glow=w("B", "ai-ul"), anchors=["A", "B", "C"]),
    dict(text="+5", start=w("C", "încă") - 0.05, end=seg_t("C", "end"), rise=0.30, anchors=["C"]),
]
# effect pills
ev["pills"] = [
    dict(n=1, label="Text behind head", start=seg_t("C") + 0.10, end=w("C", "mai") - 0.15),
    dict(n=2, label="Over the shoulder", start=seg_t("D") + 0.12, end=seg_t("D") + 1.70),
    dict(n=3, label="Glass graph", start=seg_t("E1") + 0.10, end=seg_t("E1") + 1.75),
    dict(n=4, label="Tier list", start=seg_t("F2") + 0.05, end=seg_t("G1") + 0.9),
    dict(n=5, label="Freeze frame", start=None, end=None),                 # filled below
    dict(n=6, label="Color grade", start=seg_t("I1") + 0.10, end=seg_t("I1") + 1.70),
]
# 2 over the shoulder: push + BEFORE/AFTER cards behind him
d0 = seg_t("D")
ev["ots"] = dict(start=d0, end=seg_t("D", "end"), push_end=d0 + 0.6,
                 card1=w("D", "înainte"), val1=w("D", "3"), card2=w("D", "acum"), val2=w("D", "15"),
                 chip=w("D", "minute") + 0.15, face_end=frames[segs["D"]["out_start"] + 30]["face"],
                 head_right=round(max(fr["face"][0] + fr["face"][2] * 1.08 for fr in frames[segs["D"]["out_start"] + 18:
                                                                                         segs["D"]["out_start"] + segs["D"]["n"]]), 4))
# 3 glass graph 4 -> 20
ev["graph"] = dict(start=w("E1", "numărul"), end=seg_t("E2", "end"), four=w("E2", "4"),
                   count_start=w("E2", "la", 1), count_end=w("E2", "20") + 0.45, chip=w("E2", "20") + 0.50)
# big top words (reference style)
ev["top"] = [
    dict(text="TOP 5", sub="AI-uri", start=w("F1", "top"), sub_start=w("F1", "ai-uri"), end=seg_t("F1", "end") - 0.05),
    dict(text="De ce?", sub=None, start=seg_t("J"), end=w("J", "pentru") - 0.02),
]
# 4 tier list under the face
ev["tier"] = dict(start=seg_t("F2"), end=seg_t("H1", "end"),
                  drops=[dict(tier="S", name="Claude Code", logo="claude_mark.svg", bg="#F5F0E8", t=w("G1", "claude")),
                         dict(tier="A", name="ChatGPT", logo="openai_mark.svg", bg="#0D0D0D", t=w("G2", "chatgpt")),
                         dict(tier="B", name="Gemini", logo="gemini_mark.svg", bg="#FFFFFF", t=w("G3", "gemini")),
                         dict(tier="C", name="Meta Muse", logo="meta_mark.svg", bg="#FFFFFF", t=w("G4", "meta")),
                         dict(tier="D", name="Grok", logo="grok_mark.svg", bg="#0D0D0D", t=w("G5", "grok"))],
                  suspense=w("G5", "ultimul"), face=seg_face("G1"))
# 5 freeze frame: starts on the first frozen output frame
fz = next(k for k, fr in enumerate(frames) if "freeze" in fr)
fz_end = segs["H2"]["out_start"] + segs["H2"]["n"]
ev["freeze"] = dict(start=fz / FPS, end=fz_end / FPS, face=frames[fz]["face"], src=frames[fz]["src"],
                    tag="Tu decizi.", sub="Scrie-ți topul în comentarii")
ev["pills"][4].update(start=fz / FPS + 0.12, end=fz_end / FPS - 0.05)
# 6 colour grade: Log first, then a light-line wipe driven by his hand sweep
k0 = segs["K"]["out_start"]
ev["grade"] = dict(log_start=seg_t("K"), wipe_start=k0 / FPS + (68.86 - segs["K"]["src_in"]),
                   wipe_end=k0 / FPS + (69.56 - segs["K"]["src_in"]), end=seg_t("K", "end"))
# CTA end card
ev["cta"] = dict(start=seg_t("END") + 0.12, hold=seg_t("END") + segs["END"]["live"] / FPS, end=tl["duration"])

# ---- captions: one word at a time (reference style); hidden while a panel/top word owns the screen
hide = [(ev["graph"]["start"] - 0.02, ev["graph"]["end"]),
        (ev["top"][0]["start"] - 0.02, ev["top"][0]["end"] + 0.1),
        (ev["tier"]["start"], seg_t("H1")),
        (ev["freeze"]["start"], ev["freeze"]["end"]),
        (ev["top"][1]["start"] - 0.02, ev["top"][1]["end"])]
EMPH = {"ai-ul", "primul", "5", "3", "ore", "15", "minute", "4", "20", "top", "original", "diferențele", "culoarea",
        "tot", "decizi", "eu"}
chunks = []
for x in words:
    if any(a <= x["s"] < b for a, b in hide):
        continue
    t = x["w"]
    key = t.lower().strip(",.?!")
    if chunks and chunks[-1]["merge_next"] and x["s"] - chunks[-1]["end"] < 0.15:
        c = chunks[-1]
        c["text"] += " " + t
        c["end"] = x["e"]
        c["merge_next"] = False
        c["emph"] = c["emph"] or key in EMPH
        continue
    short = len(key) <= 2 and (x["e"] - x["s"]) < 0.2 and not t.endswith((".", ",", "?"))
    chunks.append(dict(text=t, start=x["s"], end=x["e"], emph=key in EMPH, merge_next=short, seg=x["seg"]))
for i, c in enumerate(chunks):
    nxt = chunks[i + 1]["start"] if i + 1 < len(chunks) else tl["duration"]
    c["end"] = round(min(nxt, max(c["end"] + 0.22, c["start"] + 0.28)), 3)
    if nxt - c["end"] < 0.12:
        c["end"] = round(nxt, 3)
    c["start"] = round(c["start"], 3)
    c.pop("merge_next")
    f = seg_face(c["seg"])
    c["y"] = round(min(max(f[1] + f[3] + 0.078, 0.50), 0.68), 4)
for c in chunks:
    if c["seg"] == "H1":
        c["y"] = 0.775
ev["captions"] = chunks

seg_faces = {sid: seg_face(sid) for sid in segs}
data = dict(fps=FPS, n=tl["n"], duration=tl["duration"],
            segments=[dict(id=s["id"], start=s["out_start"], n=s["n"], face=seg_faces[s["id"]]) for s in tl["segments"]],
            faces=[fr["face"] for fr in frames], **ev)
json.dump(ev, open(f"{R}/work/events.json", "w"), ensure_ascii=False, indent=1)
json.dump(data, open(f"{RV}/src/data.json", "w"), ensure_ascii=False)
print(json.dumps({k: v for k, v in ev.items() if k != "captions"}, ensure_ascii=False, indent=1)[:4000])
print(len(chunks), "caption chunks:", " | ".join(f"{c['text']}@{c['start']}" for c in chunks))
