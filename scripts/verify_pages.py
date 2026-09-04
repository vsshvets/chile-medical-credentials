#!/usr/bin/env python3
"""Check every number on a university page against data/medical-schools.csv.

The pages were written by a model from injected data. This proves the numbers that reached the
page are the numbers in the dataset — the one thing a reader cannot check for themselves.
"""
import csv, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NB = " "


def variants(n):
    n = int(n)
    s = f"{n:,}"
    return {str(n), s.replace(",", NB), s.replace(",", " "), s.replace(",", " ")}


def main():
    rows = {r["slug"]: r for r in csv.DictReader((REPO / "data/medical-schools.csv").open())}
    bad, checked, missing = [], 0, []
    for slug, r in rows.items():
        f = REPO / f"universities/{slug}.md"
        if not f.exists():
            missing.append(slug); continue
        t = f.read_text(encoding="utf-8")
        for field, label in (("matricula_total_2026", "students"),
                             ("matricula_primer_ano_2026", "first-year"),
                             ("campuses_with_medicina", "campuses")):
            checked += 1
            if not any(v in t for v in variants(r[field])):
                bad.append((slug, label, r[field]))
        # the institution's own official name must appear
        checked += 1
        if r["institution"] not in t:
            bad.append((slug, "official name", r["institution"]))
        # accreditation, where the register has it
        if r["prog_accred_years"] and "progress" not in r["prog_accred_until"].lower():
            checked += 1
            if r["prog_accred_until"] not in t:
                bad.append((slug, "accreditation expiry", r["prog_accred_until"]))
    print(f"{len(rows)} pages · {checked} values checked · {len(bad)} mismatches · {len(missing)} pages missing")
    for s, lab, v in bad[:25]:
        print(f"  MISMATCH {s}: {lab} = {v} not found on page")
    for m in missing:
        print(f"  MISSING PAGE {m}")
    return 1 if bad or missing else 0


if __name__ == "__main__":
    sys.exit(main())
