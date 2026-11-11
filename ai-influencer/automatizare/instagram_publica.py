#!/usr/bin/env python3
"""Publică rândurile programate din calendar.csv prin Instagram Content Publishing API.

NETESTAT pe un cont real. Fluxul e cel din documentația Meta:
  1. POST /<ig-user-id>/media            -> container
  2. GET  /<container-id>?fields=status_code   până la FINISHED
  3. POST /<ig-user-id>/media_publish    -> postarea
Înainte de fiecare publicare se citește /<ig-user-id>/content_publishing_limit.

Publică doar rândurile cu stare=programat și data+ora deja trecute.
Implicit rulează de probă: arată ce ar publica. Publicarea reală cere --publica.

  python instagram_publica.py ../07-continut-si-calendar/calendar.csv
  python instagram_publica.py ../07-continut-si-calendar/calendar.csv --publica --maxim 1

Coloana "fisier" trebuie să fie o adresă https publică (API-ul descarcă fișierul de acolo).
Format acceptat: poza (o adresă), reel (o adresă video), carusel (adrese separate prin |).
"""
import argparse
import csv
import datetime as dt
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


def incarca_env(cale=".env"):
    p = pathlib.Path(__file__).with_name(cale)
    if not p.exists():
        return
    for linie in p.read_text(encoding="utf-8").splitlines():
        linie = linie.strip()
        if linie and not linie.startswith("#") and "=" in linie:
            k, v = linie.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


class Api:
    def __init__(self):
        self.gazda = os.environ.get("IG_API_HOST", "graph.facebook.com")
        self.versiune = os.environ.get("IG_API_VERSION")
        self.cont = os.environ.get("IG_USER_ID")
        self.token = os.environ.get("IG_ACCESS_TOKEN")
        lipsa = [n for n, v in (("IG_API_VERSION", self.versiune), ("IG_USER_ID", self.cont), ("IG_ACCESS_TOKEN", self.token)) if not v]
        if lipsa:
            raise SystemExit("Lipsesc din .env: " + ", ".join(lipsa))

    def cere(self, metoda, cale, parametri=None):
        parametri = dict(parametri or {})
        parametri["access_token"] = self.token
        url = f"https://{self.gazda}/{self.versiune}/{cale}"
        date = None
        if metoda == "GET":
            url += "?" + urllib.parse.urlencode(parametri)
        else:
            date = urllib.parse.urlencode(parametri).encode()
        req = urllib.request.Request(url, data=date, method=metoda)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Instagram a răspuns {e.code}: {e.read().decode()[:600]}")

    def limita(self):
        r = self.cere("GET", f"{self.cont}/content_publishing_limit", {"fields": "quota_usage,config"})
        d = (r.get("data") or [{}])[0]
        return d.get("quota_usage", 0), (d.get("config") or {}).get("quota_total")

    def asteapta(self, container, maxim=600):
        start = time.time()
        while True:
            r = self.cere("GET", container, {"fields": "status_code,status"})
            cod = r.get("status_code")
            if cod == "FINISHED":
                return
            if cod in ("ERROR", "EXPIRED"):
                raise RuntimeError(f"containerul {container} a ajuns în {cod}: {r.get('status')}")
            if time.time() - start > maxim:
                raise RuntimeError(f"containerul {container} nu s-a terminat în {maxim}s (stare {cod})")
            time.sleep(5)

    def container(self, parametri):
        # Dezvăluirea de conținut AI: API-ul o acceptă din iunie 2026, dar numele parametrului
        # NU a fost verificat. Se completează în .env după documentația curentă:
        #   IG_AI_PARAM=<nume parametru>   IG_AI_VALUE=<valoare>
        nume, valoare = os.environ.get("IG_AI_PARAM"), os.environ.get("IG_AI_VALUE")
        if nume and valoare:
            parametri[nume] = valoare
        return self.cere("POST", f"{self.cont}/media", parametri)["id"]

    def publica(self, rand):
        fmt = rand["format"].strip().lower()
        text = "\n\n".join(x for x in (rand.get("descriere", "").strip(), rand.get("indemn", "").strip()) if x)
        adrese = [a.strip() for a in rand["fisier"].split("|") if a.strip()]
        if fmt == "poza":
            c = self.container({"image_url": adrese[0], "caption": text})
        elif fmt == "reel":
            c = self.container({"media_type": "REELS", "video_url": adrese[0], "caption": text})
        elif fmt == "carusel":
            copii = []
            for a in adrese:
                cid = self.cere("POST", f"{self.cont}/media", {"image_url": a, "is_carousel_item": "true"})["id"]
                self.asteapta(cid)
                copii.append(cid)
            c = self.container({"media_type": "CAROUSEL", "children": ",".join(copii), "caption": text})
        else:
            raise RuntimeError(f"format necunoscut: {rand['format']}")
        self.asteapta(c)
        return self.cere("POST", f"{self.cont}/media_publish", {"creation_id": c})["id"]


def verifica(rand):
    """Întoarce lista de probleme care opresc publicarea unui rând."""
    probleme = []
    fmt = rand.get("format", "").strip().lower()
    adrese = [a.strip() for a in rand.get("fisier", "").split("|") if a.strip()]
    if fmt not in ("poza", "reel", "carusel"):
        probleme.append(f"format '{rand.get('format')}' (acceptat: poza, reel, carusel)")
    if not adrese:
        probleme.append("lipsește fișierul")
    if any(not a.startswith("https://") for a in adrese):
        probleme.append("fișierul trebuie să fie o adresă https publică")
    if fmt == "carusel" and not 2 <= len(adrese) <= 10:
        probleme.append(f"caruselul are {len(adrese)} imagini (permis 2-10)")
    if fmt in ("poza", "reel") and len(adrese) > 1:
        probleme.append("o singură adresă pentru poză sau reel")
    if not rand.get("descriere", "").strip():
        probleme.append("lipsește descrierea")
    if len(rand.get("descriere", "")) > 2200:
        probleme.append("descrierea trece de 2200 de caractere")
    return probleme


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("calendar")
    ap.add_argument("--publica", action="store_true", help="publică de-adevăratelea")
    ap.add_argument("--maxim", type=int, default=1, help="câte postări cel mult la o rulare")
    ap.add_argument("--acum", help="AAAA-LL-ZZ HH:MM, pentru probă")
    a = ap.parse_args()

    incarca_env()
    cale = pathlib.Path(a.calendar)
    with cale.open(encoding="utf-8", newline="") as f:
        cititor = csv.DictReader(f)
        coloane = cititor.fieldnames
        randuri = list(cititor)

    acum = dt.datetime.strptime(a.acum, "%Y-%m-%d %H:%M") if a.acum else dt.datetime.now()
    de_publicat = []
    for i, r in enumerate(randuri):
        if r.get("stare", "").strip().lower() != "programat":
            continue
        try:
            cand = dt.datetime.strptime(f"{r['data'].strip()} {r['ora'].strip()}", "%Y-%m-%d %H:%M")
        except ValueError:
            print(f"rândul {i + 2}: dată sau oră greșită ({r.get('data')} {r.get('ora')}), sărit")
            continue
        if cand <= acum:
            de_publicat.append((i, r))

    if not de_publicat:
        print("nimic de publicat acum.")
        return

    api = Api() if a.publica else None
    publicate = 0
    for i, r in de_publicat:
        eticheta = f"rândul {i + 2} ({r['data']} {r['ora']}, {r['format']}: {r.get('idee', '')[:50]})"
        probleme = verifica(r)
        if probleme:
            print(f"{eticheta}: OPRIT, " + "; ".join(probleme))
            continue
        if not a.publica:
            print(f"{eticheta}: ar fi publicat [probă]")
            continue
        if publicate >= a.maxim:
            print(f"{eticheta}: amânat, limita de {a.maxim} pe rulare e atinsă")
            continue
        folosit, total = api.limita()
        if total is not None and folosit >= total:
            print(f"limita Instagram e atinsă ({folosit}/{total}), mă opresc.")
            break
        try:
            randuri[i]["publicat_id"] = api.publica(r)
            randuri[i]["stare"] = "publicat"
            publicate += 1
            print(f"{eticheta}: publicat, id {randuri[i]['publicat_id']}")
        except RuntimeError as e:
            print(f"{eticheta}: EȘUAT, {e}")
        # calendarul se rescrie după fiecare postare, ca o întrerupere să nu ducă la dublă publicare
        with cale.open("w", encoding="utf-8", newline="") as f:
            scriitor = csv.DictWriter(f, fieldnames=coloane)
            scriitor.writeheader()
            scriitor.writerows(randuri)


if __name__ == "__main__":
    sys.exit(main())
