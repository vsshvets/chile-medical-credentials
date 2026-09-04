#!/usr/bin/env python3
"""Generate the university table markdown FROM data/medical-schools.csv.

The README table is never hand-typed. If the CSV changes, the table changes. They cannot drift.
Writes data/_table_universities.md for the assembler to include verbatim.
"""
import csv
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
(REPO / "raw").mkdir(exist_ok=True)
rows = list(csv.DictReader((REPO / "data/medical-schools.csv").open()))
rows.sort(key=lambda r: -int(r["matricula_total_2026"]))

def kind(r):
    if r["is_state"] == "yes":
        return "державний"
    return "приватний (CRUCH)" if r["is_cruch"] == "yes" else "приватний"

# THE LINK-DEPTH RULE. The same table is included from two different depths: the root README
# (needs "universities/x.md") and universities/README.md (needs "x.md"). Emitting one string for
# both is failure mode #1 in the house doctrine — it broke 62% of links in a shipped repo, and it
# broke 70 of 157 here before this was fixed. So the table is rendered TWICE, once per depth.
def build(prefix):
  lines = [
    "| # | Університет | Тип | Регіон(и) | Студентів медицини | Набір 1-го курсу | Кампусів | Сторінка |",
    "|--:|---|---|---|--:|--:|--:|---|",
  ]
  for i, r in enumerate(rows, 1):
    regions = r["regions"].replace(" | ", ", ")
    if len(regions) > 44:
        regions = regions[:41] + "…"
    new = " 🆕" if r["new_programme_2026"] == "yes" else ""
    lines.append(
        f"| {i} | **{r['institution']}**{new} | {kind(r)} | {regions} | "
        f"{th(r['matricula_total_2026'])} | {th(r['matricula_primer_ano_2026'])} | "
        f"{r['campuses_with_medicina']} | [деталі]({prefix}{r['slug']}.md) |"
    )
  lines.append(f"| | **Разом: {len(rows)} університетів** | з них {state} державних | | "
               f"**{th(tot)}** | **{th(p1)}** | {camp} | |")
  return "\n".join(lines)

NB = "\u202f"  # narrow no-break space: a thousands separator that never collides with a comma


def th(n):
    return f"{int(n):,}".replace(",", NB)


tot = sum(int(r["matricula_total_2026"]) for r in rows)
p1 = sum(int(r["matricula_primer_ano_2026"]) for r in rows)
camp = sum(int(r["campuses_with_medicina"]) for r in rows)
state = sum(1 for r in rows if r["is_state"] == "yes")
new = sum(1 for r in rows if r["new_programme_2026"] == "yes")

foot = (
    f"\n*Джерело всіх чисел у цій таблиці: офіційний набір даних SIES/MINEDUC «Matrícula 2026», "
    f"опублікований 10 липня 2026 року. Числа обчислені з файлу, а не переписані з вебсторінки.*\n\n"
    f"*«Студентів медицини» — це **matrícula total** (усі курси). «Набір 1-го курсу» — це "
    f"**matrícula de primer año** (зараховані на перший курс 2026 року). Це два різні показники; "
    f"їх постійно плутають.* "
    f"{'🆕 позначає програми, що стартували 2026 року (' + str(new) + ' шт.): у них перший курс дорівнює всім студентам.' if new else ''}\n"
)

(REPO / "raw/_table_universities_root.md").write_text(build("universities/") + "\n" + foot, encoding="utf-8")
(REPO / "raw/_table_universities_local.md").write_text(build("") + "\n" + foot, encoding="utf-8")
print(f"wrote both depth variants · {len(rows)} rows · total {tot:,} · first-year {p1:,}")
