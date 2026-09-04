#!/usr/bin/env python3
"""Render the eligible-institutions table from the CSV, into raw/ for inclusion in README.md.

Generated, not pasted: the first version was hand-assembled and a thousands-separator replace ate
the commas that separated accreditation level from years.
"""
import csv
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
(REPO / "raw").mkdir(exist_ok=True)
rows = list(csv.DictReader((REPO / "data/eligible-institutions.csv").open()))
NB = " "


def th(n):
    return f"{int(n):,}".replace(",", NB)


yes = [r for r in rows if r["can_revalidate_medical_degree"] == "yes"]
cond = [r for r in rows if r["can_revalidate_medical_degree"] == "conditional"]
yes.sort(key=lambda r: -int(r["medicina_students_2026"] or 0))

out = ["| Університет | Акредитація закладу | Акредитація програми | Студентів медицини |",
       "|---|---|---|--:|"]
for r in yes:
    out.append(f"| [{r['institution']}](universities/{r['slug']}.md) "
               f"| {r['institutional_level']}, {r['institutional_years']} р. "
               f"(до {r['institutional_until']}) "
               f"| {r['programme_accred_years']} р., до {r['programme_accred_until']} "
               f"| {th(r['medicina_students_2026'])} |")
for r in cond:
    out.append(f"| ⚠️ [{r['institution']}](universities/{r['slug']}.md) "
               f"| {r['institutional_level']}, {r['institutional_years']} р. "
               f"(до {r['institutional_until']}) "
               f"| **акредитація програми в процесі** "
               f"| {th(r['medicina_students_2026'])} |")
(REPO / "raw/_table_eligible.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"raw/_table_eligible.md · {len(yes)} eligible + {len(cond)} conditional")
