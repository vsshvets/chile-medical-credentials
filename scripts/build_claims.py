#!/usr/bin/env python3
"""Flatten every research claim into ONE CSV — the claim ledger.

192 JSON files are the evidence; nobody can read them. This is the same content as one flat table
that opens in Excel and renders on GitHub, so a reader can audit any statement in the report.
"""
import csv, glob, json, re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
IDX = json.loads((REPO / "sources/index.json").read_text()) if (REPO / "sources/index.json").exists() else {}
SRC = REPO / "sources"

FIELDS = ["claim_id", "lane", "engine", "statement", "confidence", "evidence_type",
          "regime_side", "norm", "in_force_from", "applies_to_her", "condition",
          "source_url", "source_publisher", "source_date", "quote_locator", "quote_original",
          "quote_found_on_page", "source_stored"]


def norm(s):
    s = (s or "")
    for a, b in [("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("«", '"'), ("»", '"'),
                 ("–", "-"), ("—", "-"), ("−", "-"), (" ", " "), ("­", ""), ("​", "")]:
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip().lower()


def main():
    cache, rows = {}, []
    for f in sorted(glob.glob(str(REPO / "research/*/*.json"))):
        if ".voided." in f or "/universities/" in f or "/pages/" in f or "/lang/" in f:
            continue
        d = json.loads(Path(f).read_text())
        engine = Path(f).parent.name
        lane = Path(f).stem
        for c in d.get("claims") or []:
            srcs = c.get("sources") or [{}]
            for s in srcs:
                u = (s.get("url") or "").strip()
                q = (s.get("quote_original") or "").strip()
                meta = IDX.get(u) or {}
                stored = meta.get("chars", 0) > 200
                found = ""
                if stored and len(q) > 15:
                    p = SRC / f"{meta['sha1']}.txt"
                    if p not in cache:
                        cache[p] = norm(p.read_text(encoding="utf-8", errors="replace"))
                    frags = [x for x in re.split(r"\s*(?:\.\.\.|…)\s*", q) if len(x.strip()) > 12]
                    found = "yes" if all(norm(x) in cache[p] for x in (frags or [q])) else "no"
                r = c.get("regime") or {}
                rows.append({
                    "claim_id": c.get("id", ""), "lane": lane, "engine": engine,
                    "statement": " ".join((c.get("statement") or "").split()),
                    "confidence": c.get("confidence", ""), "evidence_type": c.get("evidence_type", ""),
                    "regime_side": r.get("regime_side", ""), "norm": r.get("norm", ""),
                    "in_force_from": r.get("vigencia", ""),
                    "applies_to_her": c.get("applies_to_her", ""),
                    "condition": " ".join((c.get("condition") or "").split())[:200],
                    "source_url": u, "source_publisher": s.get("publisher", ""),
                    "source_date": s.get("date_of_content", ""),
                    "quote_locator": s.get("quote_locator", ""),
                    "quote_original": " ".join(q.split()),
                    "quote_found_on_page": found,
                    "source_stored": "yes" if stored else "no",
                })
    with (REPO / "data/claims.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    ids = {r["claim_id"] for r in rows}
    ok = sum(1 for r in rows if r["quote_found_on_page"] == "yes")
    no = sum(1 for r in rows if r["quote_found_on_page"] == "no")
    print(f"data/claims.csv: {len(rows)} rows · {len(ids)} distinct claims · "
          f"quote verified on page: {ok} · not found: {no} · unverifiable: {len(rows)-ok-no}")


if __name__ == "__main__":
    main()
