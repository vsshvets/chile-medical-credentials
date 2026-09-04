#!/usr/bin/env python3
"""Scrape the CNA programme-accreditation register for Medicina.

SIES says only "ACREDITADA". CNA gives the YEARS and the expiry date — and in Chile programme
accreditation for Medicina is mandatory, so an expired or absent accreditation is material.
Source: https://www.cnachile.cl/Paginas/medicina.aspx
"""
import csv, html, json, re, sys, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetchlib

REPO = Path(__file__).resolve().parent.parent
URL = "https://www.cnachile.cl/Paginas/medicina.aspx"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")


def clean(s):
    s = html.unescape(re.sub(r"(?s)<[^>]+>", " ", s))
    s = s.replace("​", "").replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()


def key(s):
    """Match CNA names to SIES names: strip accents, punctuation, case."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z]", "", s)


def main():
    _, raw, _, _ = fetchlib.get(URL)
    body = raw.decode("utf-8", "replace")
    (REPO / "raw").mkdir(exist_ok=True)
    (REPO / "raw/cna-medicina.html").write_text(body, encoding="utf-8")

    out = []
    for tr in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", body):
        cells = [clean(c) for c in re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", tr)]
        cells = [c for c in cells if c]
        if len(cells) >= 5 and cells[0].upper() != "MEDICAL SCHOOL":
            out.append({"cna_name": cells[0], "result": cells[1],
                        "years": cells[2], "from": cells[3].replace("/", "-"),
                        "until": cells[4].replace("/", "-")})
    print(f"CNA lists {len(out)} accredited Medicina programmes")

    schools = list(csv.DictReader((REPO / "data/medical-schools.csv").open()))
    idx = {key(r["cna_name"]): r for r in out}
    # Declared aliases only. Never fuzzy-match institution names: a near-miss silently attaches one
    # university's accreditation to another, and nothing downstream would catch it.
    alias = {}
    af = REPO / "data/aliases.csv"
    if af.exists():
        for a in csv.DictReader(af.open(encoding="utf-8")):
            alias.setdefault(key(a["canonical_name"]), []).append(key(a["alias"]))
    matched = 0
    for s in schools:
        m = idx.get(key(s["institution"])) or idx.get(key(s["sies_name"]))
        if not m:
            for al in alias.get(key(s["institution"]), []):
                if al in idx:
                    m = idx[al]; break
        if m:
            matched += 1
            s["prog_accred_years"] = m["years"]
            s["prog_accred_from"] = m["from"]
            s["prog_accred_until"] = m["until"]
            s["prog_accred_source"] = URL
        else:
            s["prog_accred_years"] = ""
            s["prog_accred_from"] = ""
            s["prog_accred_until"] = ""
            s["prog_accred_source"] = ""

    with (REPO / "data/medical-schools.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(schools[0])); w.writeheader(); w.writerows(schools)
    (REPO / "data/cna-medicina-accreditation.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1))

    print(f"matched {matched}/{len(schools)} institutions")
    unmatched_sies = [s["institution"] for s in schools if not s["prog_accred_years"]]
    unmatched_cna = [m["cna_name"] for m in out
                     if not any(key(m["cna_name"]) in (key(s["institution"]), key(s["sies_name"]))
                                for s in schools)]
    if unmatched_sies:
        print("NO CNA programme accreditation found for:")
        for u in unmatched_sies:
            print("   ", u)
    if unmatched_cna:
        print("CNA rows that matched no SIES institution:")
        for u in unmatched_cna:
            print("   ", u)


if __name__ == "__main__":
    main()
