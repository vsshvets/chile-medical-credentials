#!/usr/bin/env python3
"""Which Chilean universities may actually revalidate HER medical degree.

Derived, not asserted. Three conditions must all hold, and each has a primary source:

  Decreto 174 art. 5  — a STATE university with institutional accreditation at ADVANCED level
                        (or excellence) for at least five years.
  Decreto 174 art. 4  — it may only act for a programme it teaches, whose own accreditation is
                        current (Medicina is a compulsory-accreditation programme), and which has
                        produced at least one graduating cohort.
  Decreto 174 art. 1  — Universidad de Chile is OUTSIDE this route for a professional title; it
                        continues under its own statute, DFL 3/2006 art. 6.

Institutional accreditation is from the CNA register as reported in research/codex/GAPS.json (Q4);
programme accreditation is scraped from CNA directly by fetch_cna.py; enrolment is from SIES.
"""
import csv, json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# CNA institutional accreditation of every state university clearing the art.5 threshold,
# from the CNA advanced search (GAPS Q4, retrieved 2026-09-03).
INSTITUTIONAL = {
    "Universidad de Chile":                 ("Excelencia", 7, "2032-12-23"),
    "Universidad de Santiago de Chile":     ("Excelencia", 7, "2028-02-25"),
    "Universidad de Talca":                 ("Excelencia", 7, "2033-06-01"),
    "Universidad de Tarapacá":              ("Excelencia", 6, "2029-06-22"),
    "Universidad de Valparaíso":            ("Excelencia", 6, "2029-03-08"),
    "Universidad Arturo Prat":              ("Avanzado",   5, "2027-07-06"),
    "Universidad de Antofagasta":           ("Avanzado",   5, "2027-09-07"),
    "Universidad de Atacama":               ("Avanzado",   5, "2031-04-01"),
    "Universidad del Bío-Bío":              ("Avanzado",   5, "2030-01-15"),
    "Universidad de La Frontera":           ("Avanzado",   5, "2030-09-03"),
    "Universidad de La Serena":             ("Avanzado",   5, "2026-11-03"),
    "Universidad de Los Lagos":             ("Avanzado",   5, "2026-09-09"),
    "Universidad de Magallanes":            ("Avanzado",   5, "2028-12-31"),
    "Universidad de Playa Ancha":           ("Avanzado",   5, "2027-05-25"),
}


def main():
    schools = {r["institution"]: r for r in csv.DictReader((REPO / "data/medical-schools.csv").open())}
    rows = []
    for name, (level, years, until) in sorted(INSTITUTIONAL.items()):
        s = schools.get(name)
        has_med = s is not None
        prog_years = s["prog_accred_years"] if s else ""
        prog_until = s["prog_accred_until"] if s else ""
        new_2026 = s["new_programme_2026"] == "yes" if s else False
        # art. 4: needs an accredited programme AND a graduated cohort. A 2026 start has neither.
        if name == "Universidad de Chile":
            verdict, why = "own_route", "Діє за власним статутом (DFL 3/2006, ст. 6), а не за Decreto 174"
        elif not has_med:
            verdict, why = "no", "Не викладає медицину — ст. 4 не дозволяє"
        elif new_2026:
            verdict, why = "no", "Програма стартувала 2026 року: немає ані акредитації, ані випуску"
        elif not prog_years:
            verdict, why = "no", "Програма з медицини не значиться в реєстрі акредитацій CNA"
        elif "progress" in (prog_years + " " + prog_until).lower():
            verdict, why = "conditional", "Акредитація програми в процесі — треба уточнювати"
        else:
            verdict, why = "yes", "Відповідає ст. 5 і ст. 4"
        rows.append({
            "institution": name, "is_state": "yes",
            "institutional_level": level, "institutional_years": years,
            "institutional_until": until,
            "teaches_medicina": "yes" if has_med else "no",
            "programme_accred_years": prog_years, "programme_accred_until": prog_until,
            "medicina_students_2026": s["matricula_total_2026"] if s else "",
            "new_programme_2026": "yes" if new_2026 else "no",
            "can_revalidate_medical_degree": verdict,
            "reason_uk": why,
            "slug": s["slug"] if s else "",
        })
    rows.sort(key=lambda r: ({"yes": 0, "own_route": 1, "conditional": 2, "no": 3}[r["can_revalidate_medical_degree"]],
                             -int(r["medicina_students_2026"] or 0)))
    with (REPO / "data/eligible-institutions.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    yes = [r for r in rows if r["can_revalidate_medical_degree"] == "yes"]
    print(f"data/eligible-institutions.csv · {len(rows)} state universities assessed")
    print(f"CAN take a foreign MEDICAL degree under Decreto 174: {len(yes)}")
    for r in rows:
        m = {"yes": "✅", "own_route": "🔵", "conditional": "⚠️", "no": "❌"}[r["can_revalidate_medical_degree"]]
        print(f"  {m} {r['institution'][:40]:<40} {r['institutional_level'][:10]:<10} {r['institutional_years']}y  {r['reason_uk'][:52]}")


if __name__ == "__main__":
    main()
