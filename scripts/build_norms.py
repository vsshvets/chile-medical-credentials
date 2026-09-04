#!/usr/bin/env python3
"""One flat CSV of every Chilean norm read for this report, with its version dates."""
import csv, glob, json
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
rows = []
for f in sorted(glob.glob(str(REPO / "sources/leychile/*.meta.json"))):
    d = json.loads(Path(f).read_text())
    rows.append({
        "norma_id": d["norma_id"],
        "title": " ".join((d.get("titulo") or "").split()),
        "organismo": d.get("organismo", ""),
        "promulgated": d.get("fecha_promulgacion", ""),
        "published_diario_oficial": d.get("fecha_publicacion", ""),
        "latest_version": d.get("latest_version", ""),
        "repealed": d.get("derogado", ""),
        "parts": d.get("n_partes", 0),
        "url": d.get("url_human", ""),
        "machine_text_url": d.get("url_api", ""),
        "stored_text": f"sources/leychile/{d['norma_id']}.txt",
    })
rows.sort(key=lambda r: r["published_diario_oficial"])
with (REPO / "data/norms.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(f"data/norms.csv: {len(rows)} Chilean norms read verbatim")
for r in rows:
    print(f"  {r['published_diario_oficial']}  {r['title'][:66]}")
