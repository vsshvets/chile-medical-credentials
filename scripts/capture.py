#!/usr/bin/env python3
"""Fetch and STORE every cited source, so a quote can be re-checked later and after the run.

Disk-idempotent: a URL already stored is skipped. One bad URL never kills the batch.
"""
import concurrent.futures as cf
import gzip, hashlib, io, json, re, sys, time, urllib.request, urllib.error
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "sources"; SRC.mkdir(exist_ok=True)
IDX = SRC / "index.json"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")


def sha(u: str) -> str:
    return hashlib.sha1(u.strip().encode()).hexdigest()


def urls_from_research() -> dict:
    """url -> list of (lane, claim_id)."""
    out = {}
    for f in sorted((REPO / "research").rglob("*.json")):
        try:
            d = json.loads(f.read_text())
        except Exception as e:
            print(f"  ! unparseable {f.name}: {e}"); continue
        for c in d.get("claims") or []:
            for s in c.get("sources") or []:
                u = (s.get("url") or "").strip()
                if u.startswith("http"):
                    out.setdefault(u, []).append(f"{f.parent.name}/{c.get('id')}")
    return out


def strip_html(h: str) -> str:
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?is)<br\s*/?>|</(p|div|li|tr|h[1-6])>", "\n", h)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    import html as H
    h = H.unescape(h)
    h = h.replace("\xa0", " ")
    h = re.sub(r"[ \t -​]+", " ", h)
    return re.sub(r"\n\s*\n+", "\n\n", h).strip()


def fetch(u: str) -> tuple:
    """-> (status, text, final_url, err)"""
    req = urllib.request.Request(u, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/pdf,*/*",
        "Accept-Language": "es-CL,es;q=0.9,en;q=0.8,uk;q=0.7",
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            ct = (r.headers.get_content_type() or "").lower()
            final = r.geturl()
            code = r.status
    except urllib.error.HTTPError as e:
        return e.code, "", u, f"HTTP {e.code}"
    except Exception as e:
        return 0, "", u, f"{type(e).__name__}: {e}"[:200]

    if "pdf" in ct or raw[:5] == b"%PDF-":
        try:
            from pypdf import PdfReader
            txt = "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(raw)).pages)
            return code, txt, final, "" if txt.strip() else "pdf: no extractable text"
        except Exception as e:
            return code, "", final, f"pdf extract failed: {e}"[:160]

    for enc in ("utf-8", "latin-1"):
        try:
            html = raw.decode(enc); break
        except Exception:
            html = raw.decode("utf-8", "replace")
    return code, strip_html(html), final, ""


def main():
    urls = urls_from_research()
    print(f"{len(urls)} unique cited URLs across research/")
    idx = json.loads(IDX.read_text()) if IDX.exists() else {}
    todo = [u for u in urls if u not in idx or not (SRC / f"{sha(u)}.txt").exists()]
    print(f"{len(todo)} to fetch, {len(urls)-len(todo)} already stored")
    if not todo:
        return
    done = 0
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch, u): u for u in todo}
        for fu in cf.as_completed(futs):          # as_completed, never .map — one bad URL
            u = futs[fu]                           # must never kill the batch
            try:
                code, text, final, err = fu.result()
            except Exception as e:
                code, text, final, err = 0, "", u, f"worker died: {e}"[:160]
            h = sha(u)
            if text:
                (SRC / f"{h}.txt").write_text(text, encoding="utf-8")
            idx[u] = {"sha1": h, "status": code, "final_url": final, "chars": len(text),
                      "error": err, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                      "cited_by": urls[u]}
            done += 1
            if done % 20 == 0:
                print(f"  {done}/{len(todo)}")
    IDX.write_text(json.dumps(idx, indent=1, ensure_ascii=False))
    ok = sum(1 for v in idx.values() if v["chars"] > 200)
    print(f"stored: {ok} usable / {len(idx)} total")
    for u, v in sorted(idx.items()):
        if v["chars"] <= 200:
            print(f"  FAIL {v['status']:>4} {v['error'][:60]:<62} {u[:90]}")


if __name__ == "__main__":
    main()
