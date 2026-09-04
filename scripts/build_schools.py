#!/usr/bin/env python3
"""Build data/medical-schools.csv from the OFFICIAL SIES 2026 enrolment dataset.

The numbers are never typed by hand and never read off a page by a model. They are computed from
the file the Chilean Ministry of Education publishes, so they can be recomputed and audited.

Source: SIES / mifuturo.cl, "Matrícula 2026", published 2026-07-10.
https://www.mifuturo.cl/bases-de-datos-de-matriculados/
"""
import csv, json, re, unicodedata
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "raw/sies/Matricula_2026_WEB_10_07_2026.csv"
DATASET_URL = "https://www.mifuturo.cl/wp-content/uploads/2026/07/Matricula_2026_WEB_10_07_2026.zip"
DATASET_DATE = "2026-07-10"


def num(x):
    x = (x or "").strip().replace(".", "").replace(",", "")
    return int(x) if x.isdigit() else 0


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def main():
    rows = list(csv.DictReader(SRC.open(encoding="latin-1"), delimiter=";"))
    med = [r for r in rows
           if r["ÁREA CARRERA GENÉRICA"].strip().upper() == "MEDICINA"
           and r["NOMBRE CARRERA"].strip().upper() == "MEDICINA"
           and r["NIVEL GLOBAL"].strip().lower() == "pregrado"]

    inst = defaultdict(lambda: {"total": 0, "first_year": 0, "women": 0, "men": 0,
                                "sedes": [], "regions": set(), "acc_inst": "", "acc_prog": set(),
                                "type1": "", "type2": "", "duration": set(), "modes": set()})
    for r in med:
        k = r["NOMBRE INSTITUCIÓN"].strip()
        d = inst[k]
        d["total"] += num(r["TOTAL MATRÍCULA"])
        d["first_year"] += num(r["TOTAL MATRÍCULA PRIMER AÑO"])
        d["women"] += num(r["TOTAL MATRÍCULA MUJERES"])
        d["men"] += num(r["TOTAL MATRÍCULA HOMBRES"])
        d["sedes"].append({"sede": r["NOMBRE SEDE"].strip(), "comuna": r["COMUNA"].strip(),
                           "region": r["REGIÓN"].strip(),
                           "total": num(r["TOTAL MATRÍCULA"]),
                           "first_year": num(r["TOTAL MATRÍCULA PRIMER AÑO"]),
                           "acc_prog": r["ACREDITACIÓN CARRERA"].strip(),
                           "jornada": r["JORNADA"].strip()})
        d["regions"].add(r["REGIÓN"].strip())
        d["acc_inst"] = r["ACREDITACIÓN INSTITUCIONAL"].strip()
        d["acc_prog"].add(r["ACREDITACIÓN CARRERA"].strip())
        d["type1"] = r["CLASIFICACIÓN INSTITUCIÓN NIVEL 2"].strip()
        d["type2"] = r["CLASIFICACIÓN INSTITUCIÓN NIVEL 3"].strip()
        d["duration"].add(r["DURACIÓN TOTAL DE CARRERA"].strip())
        d["modes"].add(r["JORNADA"].strip())

    out = []
    for name, d in sorted(inst.items(), key=lambda x: -x[1]["total"]):
        is_state = "Estatal" in d["type2"] or "estatal" in d["type2"].lower()
        out.append({
            "slug": slug(name),
            "institution": name,
            "type": d["type1"],
            "subtype": d["type2"],
            "is_state": "yes" if is_state else "no",
            "is_cruch": "yes" if "CRUCH" in d["type1"].upper() else "no",
            "regions": " | ".join(sorted(d["regions"])),
            "campuses_with_medicina": len(d["sedes"]),
            "campus_list": " | ".join(f"{s['sede']} ({s['comuna']})" for s in d["sedes"]),
            "matricula_total_2026": d["total"],
            "matricula_primer_ano_2026": d["first_year"],
            "women_2026": d["women"],
            "men_2026": d["men"],
            "pct_women": round(100 * d["women"] / d["total"], 1) if d["total"] else "",
            "institutional_accreditation": d["acc_inst"],
            "programme_accreditation": " | ".join(sorted(x for x in d["acc_prog"] if x)),
            "duration_semesters": " | ".join(sorted(x for x in d["duration"] if x)),
            "new_programme_2026": "yes" if d["total"] == d["first_year"] and d["total"] > 0 else "no",
            "metric_note": "matrícula total and matrícula de primer año are DIFFERENT metrics; "
                           "both are 2026 values summed across this institution's campuses",
            "source": "SIES/MINEDUC Matrícula 2026",
            "source_url": DATASET_URL,
            "source_date": DATASET_DATE,
        })

    dest = REPO / "data/medical-schools.csv"
    with dest.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader(); w.writerows(out)

    (REPO / "data/medical-schools-campuses.json").write_text(
        json.dumps({k: v["sedes"] for k, v in inst.items()}, ensure_ascii=False, indent=1))

    tot = sum(r["matricula_total_2026"] for r in out)
    p1 = sum(r["matricula_primer_ano_2026"] for r in out)
    print(f"{len(out)} institutions · {sum(r['campuses_with_medicina'] for r in out)} programme-campuses")
    print(f"matrícula total 2026: {tot:,} · matrícula primer año 2026: {p1:,}")
    print(f"state universities: {sum(1 for r in out if r['is_state']=='yes')} · "
          f"CRUCH: {sum(1 for r in out if r['is_cruch']=='yes')} · "
          f"new in 2026: {sum(1 for r in out if r['new_programme_2026']=='yes')}")
    print(f"wrote {dest}")
    return tot, p1


if __name__ == "__main__":
    main()
