#!/usr/bin/env python3
"""Generate the university table markdown FROM data/medical-schools.csv.

The README table is never hand-typed. If the CSV changes, the table changes. They cannot drift.
Writes data/_table_universities.md for the assembler to include verbatim.
"""
import csv
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader((REPO / "data/medical-schools.csv").open()))
rows.sort(key=lambda r: -int(r["matricula_total_2026"]))

def kind(r):
    if r["is_state"] == "yes":
        return "державний"
    return "приватний (CRUCH)" if r["is_cruch"] == "yes" else "приватний"

lines = [
    "| # | Університет | Тип | Регіон(и) | Студентів медицини | Набір 1-го курсу | Кампусів | Сторінка |",
    "|--:|---|---|---|--:|--:|--:|---|",
]
NB = "\u202f"  # narrow no-break space: a thousands separator that never collides with a comma


def th(n):
    return f"{int(n):,}".replace(",", NB)


for i, r in enumerate(rows, 1):
    regions = r["regions"].replace(" | ", ", ")
    if len(regions) > 44:
        regions = regions[:41] + "…"
    new = " 🆕" if r["new_programme_2026"] == "yes" else ""
    lines.append(
        f"| {i} | **{r['institution']}**{new} | {kind(r)} | {regions} | "
        f"{th(r['matricula_total_2026'])} | {th(r['matricula_primer_ano_2026'])} | "
        f"{r['campuses_with_medicina']} | [деталі](universities/{r['slug']}.md) |"
    )

tot = sum(int(r["matricula_total_2026"]) for r in rows)
p1 = sum(int(r["matricula_primer_ano_2026"]) for r in rows)
camp = sum(int(r["campuses_with_medicina"]) for r in rows)
state = sum(1 for r in rows if r["is_state"] == "yes")
new = sum(1 for r in rows if r["new_programme_2026"] == "yes")
lines.append(f"| | **Разом: {len(rows)} університетів** | з них {state} державних | | "
             f"**{th(tot)}** | **{th(p1)}** | {camp} | |")

foot = (
    f"\n*Джерело всіх чисел у цій таблиці: офіційний набір даних SIES/MINEDUC «Matrícula 2026», "
    f"опублікований 10 липня 2026 року. Числа обчислені з файлу, а не переписані з вебсторінки — "
    f"див. [`data/medical-schools.csv`](data/medical-schools.csv) і скрипт "
    f"[`scripts/build_schools.py`](scripts/build_schools.py).*\n\n"
    f"*«Студентів медицини» — це **matrícula total** (усі курси). «Набір 1-го курсу» — це "
    f"**matrícula de primer año** (зараховані на перший курс 2026 року). Це два різні показники; "
    f"їх постійно плутають.* {'🆕 позначає програми, що стартували 2026 року (' + str(new) + ' шт.): у них перший курс дорівнює всім студентам.' if new else ''}\n"
)

out = REPO / "data/_table_universities.md"
out.write_text("\n".join(lines) + "\n" + foot, encoding="utf-8")
print(f"wrote {out} · {len(rows)} rows · total {tot:,} · first-year {p1:,}")
