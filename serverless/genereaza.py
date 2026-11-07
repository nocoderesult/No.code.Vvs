#!/usr/bin/env python3
"""Generează poze cu Iness pe RunPod Serverless, fără pod pornit.

Folosire:
  python3 genereaza.py info
  python3 genereaza.py poza --endpoint ID --lora d4ria_v2.safetensors "la o cafenea, dimineața"

Cheia: variabila RUNPOD_API_KEY. În sesiunile Claude cu cheia salvată în setările
mediului (network secrets), cheia o pune proxy-ul și variabila poate lipsi.
"""
import argparse
import base64
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REST = "https://rest.runpod.io/v1"
RUN = "https://api.runpod.ai/v2"
HERE = Path(__file__).resolve().parent

# Descrierea fixă a lui Iness, din personaj/CARACTER.md (cuvântul LoRA e d4ria).
INESS = ("d4ria, a 25-year-old woman with radiant warm tan skin, a sleek straight jet-black blunt bob "
         "ending just below her jawline with a center part, piercing almond-shaped light green-hazel eyes, "
         "long voluminous dark eyelashes, dark sculpted eyebrows, full dusty-pink lips, high cheekbones with "
         "a soft natural glow, fine light freckles across her nose and cheeks, thin silver hoop earrings and a "
         "tiny silver stud in her upper ear, natural skin texture with visible pores")
SFARSIT = "real smartphone photo, natural light, not airbrushed, no text, no watermark"


def call(method, url, body=None):
    key = os.environ.get("RUNPOD_API_KEY", "injectat-de-proxy")
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"Eroare {e.code} la {url}: {e.read().decode()[:500]}")


def info(_):
    for name in ("networkvolumes", "endpoints", "pods"):
        print(f"=== {name} ===")
        data = call("GET", f"{REST}/{name}")
        for x in data if isinstance(data, list) else data.get("items", data.get(name, [])):
            keep = {k: x.get(k) for k in ("id", "name", "dataCenterId", "size", "desiredStatus", "gpuTypeIds",
                                          "networkVolumeId", "templateId", "workersMin", "workersMax") if k in x}
            print(json.dumps(keep, ensure_ascii=False))


def workflow(a):
    wf = json.loads((HERE / "workflows" / "iness_krea2_raw_api.json").read_text())
    wf["2"]["inputs"].update(lora_name=a.lora, strength_model=a.forta)
    wf["4"]["inputs"]["text"] = f"{INESS}, {a.scena}, {SFARSIT}"
    wf["6"]["inputs"].update(width=a.latime, height=a.inaltime, batch_size=a.bucati)
    wf["7"]["inputs"].update(seed=a.seed if a.seed is not None else random.randint(1, 2**48),
                             steps=a.pasi, cfg=a.cfg)
    return wf


def poza(a):
    wf = workflow(a)
    if a.doar_json:
        print(json.dumps({"input": {"workflow": wf}}, indent=1, ensure_ascii=False))
        return
    job = call("POST", f"{RUN}/{a.endpoint}/run", {"input": {"workflow": wf}})
    jid = job.get("id") or sys.exit(f"N-a pornit: {job}")
    print(f"Cerere trimisă ({jid}). Aștept (prima pornire poate dura câteva minute)...", flush=True)
    start = time.time()
    while True:
        st = call("GET", f"{RUN}/{a.endpoint}/status/{jid}")
        s = st.get("status")
        if s == "COMPLETED":
            break
        if s in ("FAILED", "CANCELLED", "TIMED_OUT"):
            sys.exit(f"Generarea a eșuat ({s}): {json.dumps(st.get('error') or st.get('output'), ensure_ascii=False)[:2000]}")
        if time.time() - start > a.timeout:
            sys.exit(f"Încă nu e gata după {a.timeout} s (status {s}). Verifici cu: status {jid}")
        time.sleep(4)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    imgs = (st.get("output") or {}).get("images", [])
    for i, im in enumerate(imgs, 1):
        if im.get("type") == "base64":
            data = im["data"].split(",", 1)[-1]
            p = out / f"iness_{jid[:8]}_{i}.png"
            p.write_bytes(base64.b64decode(data))
            print(p)
        else:
            print(im.get("data"))
    for e in (st.get("output") or {}).get("errors", []):
        print("Atenție:", e)
    print(f"Gata în {time.time() - start:.0f} s, {len(imgs)} poze.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("info", help="volume, endpoint-uri și pod-uri din cont").set_defaults(fn=info)
    p = sub.add_parser("poza", help="o poză cu Iness")
    p.add_argument("scena", help="scena, în engleză sau română (de ex. 'sitting in a cafe, morning light')")
    p.add_argument("--endpoint", default=os.environ.get("RUNPOD_ENDPOINT_ID"))
    p.add_argument("--lora", default=os.environ.get("INESS_LORA", "d4ria_v2.safetensors"))
    p.add_argument("--forta", type=float, default=0.9)
    p.add_argument("--latime", type=int, default=896)
    p.add_argument("--inaltime", type=int, default=1152)
    p.add_argument("--bucati", type=int, default=1)
    p.add_argument("--pasi", type=int, default=28)
    p.add_argument("--cfg", type=float, default=3.5)
    p.add_argument("--seed", type=int)
    p.add_argument("--timeout", type=int, default=900)
    p.add_argument("--out", default="iesiri")
    p.add_argument("--doar-json", action="store_true", help="doar afișează cererea, fără s-o trimită")
    p.set_defaults(fn=poza)
    a = ap.parse_args()
    if a.cmd == "poza" and not a.endpoint and not a.doar_json:
        sys.exit("Lipsește --endpoint (sau RUNPOD_ENDPOINT_ID).")
    a.fn(a)


if __name__ == "__main__":
    main()
