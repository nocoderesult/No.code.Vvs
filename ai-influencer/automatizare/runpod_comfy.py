#!/usr/bin/env python3
"""Rulează un workflow ComfyUI pe un endpoint serverless RunPod (worker-comfyui).

NETESTAT pe un endpoint real. Scris după README-ul runpod-workers/worker-comfyui:
  POST /v2/<endpoint>/run     cu {"input": {"workflow": {...}, "images": [...]}}
  GET  /v2/<endpoint>/status/<id>
Forma răspunsului diferă între versiunile worker-ului; vezi extrage_imagini().

Folosire:
  python runpod_comfy.py cerere.json --iesire ../05-generare-imagini/iesiri/2026-11-12
  python runpod_comfy.py cerere.json --proba      # arată cererea, nu trimite nimic

cerere.json:
  {
    "workflow": "../05-generare-imagini/workflows/portret.json",
    "inlocuiri": {"6.inputs.text": "promptul", "3.inputs.seed": 12345},
    "nume": "2026-11-12_sala_negru"
  }
Cheile din "inlocuiri" sunt "<id nod>.inputs.<câmp>" din workflow-ul exportat cu Export (API).
"""
import argparse
import base64
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

API = "https://api.runpod.ai/v2"


def incarca_env(cale=".env"):
    p = pathlib.Path(__file__).with_name(cale)
    if not p.exists():
        return
    for linie in p.read_text(encoding="utf-8").splitlines():
        linie = linie.strip()
        if linie and not linie.startswith("#") and "=" in linie:
            k, v = linie.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def aplica_inlocuiri(workflow, inlocuiri):
    for cale, valoare in inlocuiri.items():
        parti = cale.split(".")
        nod = workflow
        for parte in parti[:-1]:
            if parte not in nod:
                raise KeyError(f"calea '{cale}' nu există în workflow (lipsește '{parte}')")
            nod = nod[parte]
        if parti[-1] not in nod:
            raise KeyError(f"calea '{cale}' nu există în workflow (lipsește '{parti[-1]}')")
        nod[parti[-1]] = valoare
    return workflow


def cere(metoda, url, cheie, corp=None):
    date = json.dumps(corp).encode() if corp is not None else None
    req = urllib.request.Request(url, data=date, method=metoda)
    req.add_header("Authorization", f"Bearer {cheie}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"RunPod a răspuns {e.code}: {e.read().decode()[:500]}")


def extrage_imagini(iesire):
    """Întoarce o listă de (nume, octeți). Acceptă cele două forme cunoscute de răspuns."""
    rezultat = []
    if isinstance(iesire, dict) and isinstance(iesire.get("images"), list):
        for i, img in enumerate(iesire["images"]):
            date = img.get("data") or img.get("image")
            if img.get("type") == "s3_url" or (isinstance(date, str) and date.startswith("http")):
                with urllib.request.urlopen(date, timeout=120) as r:
                    rezultat.append((img.get("filename", f"imagine_{i}.png"), r.read()))
            elif date:
                rezultat.append((img.get("filename", f"imagine_{i}.png"), base64.b64decode(date.split(",")[-1])))
    elif isinstance(iesire, dict) and isinstance(iesire.get("message"), str):
        rezultat.append(("imagine_0.png", base64.b64decode(iesire["message"].split(",")[-1])))
    return rezultat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cerere")
    ap.add_argument("--iesire", default=".")
    ap.add_argument("--proba", action="store_true", help="arată cererea fără să o trimită")
    ap.add_argument("--asteptare", type=int, default=900, help="secunde maxime de așteptare")
    a = ap.parse_args()

    incarca_env()
    cale_cerere = pathlib.Path(a.cerere)
    cerere = json.loads(cale_cerere.read_text(encoding="utf-8"))
    workflow = json.loads((cale_cerere.parent / cerere["workflow"]).read_text(encoding="utf-8"))
    try:
        workflow = aplica_inlocuiri(workflow, cerere.get("inlocuiri", {}))
    except KeyError as e:
        raise SystemExit(f"cerere greșită: {e.args[0]}")
    corp = {"input": {"workflow": workflow}}
    nume = cerere.get("nume", cale_cerere.stem)

    if a.proba:
        print(json.dumps(corp, indent=2, ensure_ascii=False)[:3000])
        print(f"\n[probă] {len(workflow)} noduri, nimic trimis.")
        return

    cheie = os.environ.get("RUNPOD_API_KEY")
    endpoint = os.environ.get("RUNPOD_ENDPOINT_ID")
    if not cheie or not endpoint:
        raise SystemExit("Lipsesc RUNPOD_API_KEY sau RUNPOD_ENDPOINT_ID din .env")

    job = cere("POST", f"{API}/{endpoint}/run", cheie, corp)
    job_id = job.get("id")
    if not job_id:
        raise SystemExit(f"Răspuns neașteptat la pornire: {job}")
    print(f"pornit: {job_id}")

    start = time.time()
    while True:
        stare = cere("GET", f"{API}/{endpoint}/status/{job_id}", cheie)
        s = stare.get("status")
        if s == "COMPLETED":
            break
        if s in ("FAILED", "CANCELLED", "TIMED_OUT"):
            raise SystemExit(f"lucrarea s-a încheiat cu {s}: {json.dumps(stare)[:800]}")
        if time.time() - start > a.asteptare:
            raise SystemExit(f"am așteptat {a.asteptare}s, lucrarea e încă {s}. ID: {job_id}")
        time.sleep(5)

    imagini = extrage_imagini(stare.get("output"))
    if not imagini:
        raise SystemExit(f"lucrarea s-a terminat, dar nu am găsit imagini în răspuns: {json.dumps(stare)[:800]}")

    dosar = pathlib.Path(a.iesire)
    dosar.mkdir(parents=True, exist_ok=True)
    for i, (_, octeti) in enumerate(imagini):
        tinta = dosar / f"{nume}_{i:02d}.png"
        tinta.write_bytes(octeti)
        print(f"salvat: {tinta}")
    # cererea se păstrează lângă imagini, ca poza să poată fi refăcută
    (dosar / f"{nume}.cerere.json").write_text(json.dumps(cerere, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
