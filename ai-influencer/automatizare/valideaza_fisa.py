#!/usr/bin/env python3
"""Verifică fișa personajului: câmpuri goale, vârstă, semne fără poziție, minime din plan.

  python valideaza_fisa.py ../02-personaj/fisa-personaj.yaml

Iese cu cod 0 dacă fișa e completă și cu 1 dacă are probleme. Cere PyYAML (pip install pyyaml).
"""
import pathlib
import sys

try:
    import yaml
except ImportError:
    raise SystemExit("Lipsește PyYAML: pip install pyyaml")


def goale(nod, cale=""):
    """Întoarce căile tuturor câmpurilor goale."""
    gasite = []
    if isinstance(nod, dict):
        for k, v in nod.items():
            gasite += goale(v, f"{cale}.{k}" if cale else k)
    elif isinstance(nod, list):
        if not nod:
            gasite.append(cale)
        for i, v in enumerate(nod):
            gasite += goale(v, f"{cale}[{i}]")
    elif nod is None or nod == "" or (nod == 0 and not isinstance(nod, bool)):
        gasite.append(cale)
    return gasite


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    fisa = yaml.safe_load(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")) or {}
    probleme = [f"câmp gol: {c}" for c in goale(fisa)]

    varsta = (fisa.get("identitate") or {}).get("varsta") or 0
    if varsta and varsta < 21:
        probleme.append(f"vârsta este {varsta}; planul cere cel puțin 21")

    for i, s in enumerate(fisa.get("semne_fixe") or []):
        if isinstance(s, dict) and s.get("tip") and not s.get("pozitie"):
            probleme.append(f"semnul fix {i} ({s['tip']}) nu are poziție")

    minime = (
        ("garderoba.tinute", (fisa.get("garderoba") or {}).get("tinute"), 5),
        ("locuri", fisa.get("locuri"), 3),
        ("voce_scrisa.exemple_descrieri", (fisa.get("voce_scrisa") or {}).get("exemple_descrieri"), 5),
    )
    for nume, lista, minim in minime:
        n = len([x for x in (lista or []) if x and (not isinstance(x, dict) or any(x.values()))])
        if n < minim:
            probleme.append(f"{nume}: {n} completate, planul cere cel puțin {minim}")

    trasaturi = (fisa.get("personalitate") or {}).get("trasaturi") or []
    if trasaturi and len(trasaturi) != 3:
        probleme.append(f"personalitate.trasaturi: {len(trasaturi)}, planul cere exact 3")

    ai = fisa.get("dezvaluire_ai") or {}
    if ai.get("eticheta_profil") is not True or ai.get("eticheta_postare") is not True:
        probleme.append("dezvaluire_ai: eticheta de profil și cea de postare trebuie să fie true")

    if probleme:
        print(f"{len(probleme)} probleme:")
        for p in probleme:
            print("  -", p)
        return 1
    print("fișa e completă.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
