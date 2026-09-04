#!/usr/bin/env python3
"""Assert the headline numbers in README.md match the datasets they come from.

A number typed into prose drifts from the table it came from the moment either changes. These are
the figures a reader would act on, so each one is recomputed from the CSV and compared.
"""
import csv, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NB = " "


def forms(n):
    n = int(n)
    s = f"{n:,}"
    return {str(n), s.replace(",", NB), s.replace(",", " "), s.replace(",", " ")}


def main():
    txt = REPO / "README.md"
    t = txt.read_text(encoding="utf-8")
    schools = list(csv.DictReader((REPO / "data/medical-schools.csv").open()))
    vac = list(csv.DictReader((REPO / "data/vacancies.csv").open()))
    elig = list(csv.DictReader((REPO / "data/eligible-institutions.csv").open()))

    checks = [
        ("universities with Medicina", len(schools)),
        ("programme-campuses", sum(int(r["campuses_with_medicina"]) for r in schools)),
        ("total Medicina enrolment", sum(int(r["matricula_total_2026"]) for r in schools)),
        ("first-year intake", sum(int(r["matricula_primer_ano_2026"]) for r in schools)),
        ("state universities with Medicina", sum(1 for r in schools if r["is_state"] == "yes")),
        ("open academic posts", sum(int(r["open_academic_posts_2026_09_03"] or 0) for r in vac)),
        ("rheumatology units confirmed", sum(1 for r in vac if r["rheumatology_unit"] == "yes")),
        ("eligible to revalidate", sum(1 for r in elig if r["can_revalidate_medical_degree"] == "yes")),
    ]
    # UTM arithmetic must recompute exactly
    utm = 71721
    utm_checks = [(f"{k} UTM in CLP", k * utm) for k in (2, 3, 15, 20)]

    bad = []
    for label, val in checks + utm_checks:
        if not any(f in t for f in forms(val)):
            bad.append((label, val))
        else:
            print(f"  ok  {label:<34} {val:,}".replace(",", " "))
    for label, val in bad:
        print(f"  MISSING  {label:<30} expected {val:,} — not found in README".replace(",", " "))
    print(f"{'FAIL' if bad else 'OK'}: {len(checks)+len(utm_checks)-len(bad)}/"
          f"{len(checks)+len(utm_checks)} headline numbers match their dataset")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
