#!/usr/bin/env python3
"""Fetch every LeyChile norm cited anywhere in the research, via the XML API.

A bcn.cl/leychile HTML page is a JavaScript shell: it contains no legal text at all. Storing one and
checking a quote against it proves nothing, and marks correct quotes as missing. This resolves every
cited LeyChile URL to its idNorma, pulls the real normative text, and stores it under the sha1 of
the URL as cited, so verify.py checks the quote against the actual law.
"""
import hashlib, json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import leychile

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "sources"
IDX = SRC / "index.json"
LEY_HOST = re.compile(r"https?://(?:www\.|nuevo\.)?(?:bcn\.cl/leychile|leychile\.cl)", re.I)
ID_RE = re.compile(r"[?&]idNorma=(\d+)", re.I)


def main():
    idx = json.loads(IDX.read_text()) if IDX.exists() else {}
    urls = [u for u in idx if LEY_HOST.match(u)]
    by_norm = {}
    for u in urls:
        m = ID_RE.search(u)
        if m:
            by_norm.setdefault(m.group(1), []).append(u)
    print(f"{len(urls)} cited LeyChile URLs across {len(by_norm)} distinct norms")
    ok = fail = 0
    for nid, cited in sorted(by_norm.items()):
        try:
            meta = leychile.fetch(nid)
            text = (REPO / f"sources/leychile/{nid}.txt").read_text(encoding="utf-8")
        except Exception as e:
            print(f"  {nid}: FAILED {type(e).__name__}: {e}"); fail += 1; continue
        for u in cited:
            h = hashlib.sha1(u.strip().encode()).hexdigest()
            (SRC / f"{h}.txt").write_text(text, encoding="utf-8")
            idx[u] = {**idx.get(u, {}), "sha1": h, "status": 200, "final_url": u,
                      "chars": len(text), "error": "",
                      "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                      "source": "LeyChile XML API (obtxml opt=7)",
                      "norma_id": nid, "titulo": meta.get("titulo", ""),
                      "fecha_publicacion": meta.get("fecha_publicacion", ""),
                      "latest_version": meta.get("latest_version", "")}
        ok += 1
        print(f"  {nid}: {len(text):>7} chars · {len(cited)} cited URL(s) · {meta.get('titulo','')[:60]}")
    IDX.write_text(json.dumps(idx, indent=1, ensure_ascii=False))
    print(f"backfilled {ok} norms, {fail} failed")


if __name__ == "__main__":
    main()
