#!/usr/bin/env python3
"""Flatten every costed process step into one CSV, so the scenario totals can be audited.

A derived total legitimately carries no URL. What it must carry instead is the table it was
computed from. This is that table.
"""
import csv, glob, json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
rows = []
for f in sorted(glob.glob(str(REPO / "research/*/*.json"))):
    if any(x in f for x in ("/universities/", "/pages/", "/lang/", ".voided.")):
        continue
    d = json.loads(Path(f).read_text())
    lane = Path(f).stem
    for s in d.get("process_steps") or []:
        rows.append({
            "lane": lane,
            "step_no": s.get("step_no", ""),
            "name": " ".join((s.get("name") or "").split()),
            "actor": s.get("actor", ""),
            "where": s.get("where", ""),
            "requires_presence_in_chile": s.get("requires_presence_in_chile", ""),
            "requires_rut": s.get("requires_rut", ""),
            "cost_amount": s.get("cost_amount", ""),
            "cost_unit": s.get("cost_unit", ""),
            "cost_as_of": s.get("cost_as_of", ""),
            "duration_days_min": s.get("duration_days_min", ""),
            "duration_days_max": s.get("duration_days_max", ""),
            "documents": " | ".join(s.get("documents") or []),
            "source_claim_ids": " ".join(s.get("source_claim_ids") or []),
        })
with (REPO / "data/process-steps.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(f"data/process-steps.csv: {len(rows)} costed steps across {len({r['lane'] for r in rows})} lanes")
