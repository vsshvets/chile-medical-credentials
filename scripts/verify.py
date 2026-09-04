#!/usr/bin/env python3
"""Mechanical gates over the research JSON. Every check here exists because it can ship broken.

  python3 scripts/verify.py            all gates, exit 1 on any BLOCKER
  python3 scripts/verify.py quotes     one gate
"""
import json, re, sys, unicodedata
from pathlib import Path
from collections import Counter, defaultdict

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "sources"
IDX = SRC / "index.json"
REGIME_DATE = "2026-08-17"

TIER_A = {"bcn.cl","leychile.cl","diariooficial.interior.gob.cl","mineduc.cl","ayudamineduc.cl",
          "superdesalud.gob.cl","minsal.cl","eunacom.cl","cned.cl","mifuturo.cl","cnachile.cl",
          "serviciomigraciones.cl","minrel.gob.cl","sii.cl","registrocivil.cl","chile.gob.cl",
          "subsecretariadesaluddigital.gob.cl","superintendenciadeeducacionsuperior.cl",
          "educacionsuperior.mineduc.cl","serviciocivil.cl","empleospublicos.cl","conacem.cl",
          "zakon.rada.gov.ua","mon.gov.ua","moz.gov.ua","naqa.gov.ua","hcch.net"}

def _tier_a(host: str) -> bool:
    """Subdomain-aware. `nuevo.leychile.cl` IS LeyChile; a bare-host test called it off-tier and
    would have blocked fourteen correctly-sourced legal claims."""
    h = host.lower()
    if h.endswith(".gob.cl") or h.endswith(".gov.ua") or h.endswith(".gov.cl"):
        return True
    return any(h == d or h.endswith("." + d) for d in TIER_A)


# The lane whose entire job is cataloguing stale pages necessarily carries PRE-tagged claims.
# Reporting that a page is out of date is not the same as being out of date.
DECOY_LANES = {"L12"}

FAIL = []          # blockers
WARN = []


def load_claims():
    out = []
    for f in sorted((REPO / "research").rglob("*.json")):
        if f.name == "index.json":
            continue
        try:
            d = json.loads(f.read_text())
        except Exception as e:
            FAIL.append(f"unparseable research file {f}: {e}"); continue
        lane = f.parent.name
        for c in d.get("claims") or []:
            out.append((lane, f.name, c))
    return out


def norm(s: str) -> str:
    """Normalise for substring matching. Extraction never returns a page character-for-character."""
    s = unicodedata.normalize("NFC", s or "")
    s = (s.replace("’", "'").replace("‘", "'").replace("“", '"')
          .replace("”", '"').replace("«", '"').replace("»", '"')
          .replace("–", "-").replace("—", "-").replace("−", "-")
          .replace(" ", " ").replace("­", "").replace("​", ""))
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def gate_quotes():
    """A quote absent from its own source is a fabricated citation wearing a real link."""
    if not IDX.exists():
        WARN.append("quotes: no sources/index.json yet — run capture.py first"); return
    idx = json.loads(IDX.read_text())
    cache, tot, hit, miss, nosrc = {}, 0, 0, [], 0
    for lane, fn, c in load_claims():
        for s in c.get("sources") or []:
            q, u = (s.get("quote_original") or "").strip(), (s.get("url") or "").strip()
            if not q or len(q) < 15:
                continue
            tot += 1
            meta = idx.get(u)
            if not meta or meta.get("chars", 0) < 200:
                nosrc += 1; continue
            p = SRC / f"{meta['sha1']}.txt"
            if p not in cache:
                cache[p] = norm(p.read_text(encoding="utf-8", errors="replace"))
            body = cache[p]
            # A quote lifted from page SOURCE (attributes, tags) can never match tag-stripped text.
            # Strip markup out of the QUOTE too before deciding it is missing.
            q_plain = re.sub(r"<[^>]+>", " ", q)
            if q_plain != q and norm(q_plain) in body:
                hit += 1
                continue
            # ellipsis-joined fragments each pass independently
            frags = [f for f in re.split(r"\s*(?:\.\.\.|…|\[\.\.\.\])\s*", q) if len(f.strip()) > 12]
            if all(norm(f) in body for f in (frags or [q])):
                hit += 1
            else:
                miss.append((lane, c["id"], u, q[:90]))
    checked = hit + len(miss)
    print(f"\n[quotes] {tot} quotes · {checked} checkable · {hit} found · {len(miss)} NOT on their page · "
          f"{nosrc} source not stored")
    for m in miss[:25]:
        print(f"   MISS {m[0]}/{m[1]}  {m[3]}\n        {m[2][:110]}")
    if len(miss) > 25:
        print(f"   … and {len(miss)-25} more")
    if checked >= 20:
        rate = len(miss) / checked
        if rate == 0:
            FAIL.append("quotes: 0% miss rate over 20+ quotes — the checker is almost certainly "
                        "broken (house rate is ~6%). Verify normalisation before trusting this.")
        elif rate > 0.35:
            FAIL.append(f"quotes: {rate:.0%} of quotes are not on their cited page — fabrication level")
        elif rate > 0.15:
            WARN.append(f"quotes: {rate:.0%} miss rate — each miss must be dropped or re-sourced")


def gate_urls():
    if not IDX.exists():
        WARN.append("urls: no index yet"); return
    idx = json.loads(IDX.read_text())
    bad_status = [(u, v["status"], v["error"][:50]) for u, v in idx.items() if v["chars"] < 200]
    # a redirect whose final path is / is the real-but-unrelated-URL failure
    root = [u for u, v in idx.items()
            if v.get("final_url") and re.sub(r"https?://[^/]+", "", v["final_url"]).strip("/") in ("", "index", "index.html")
            and re.sub(r"https?://[^/]+", "", u).strip("/") not in ("", "index", "index.html")]
    print(f"\n[urls] {len(idx)} cited · {len(bad_status)} unfetchable · {len(root)} redirected to site root")
    for u, st, e in bad_status[:20]:
        print(f"   DEAD {st:>4} {e:<52} {u[:95]}")
    for u in root[:10]:
        print(f"   ROOT-REDIRECT {u[:110]}")
    if root:
        FAIL.append(f"urls: {len(root)} citation(s) redirect to the site root — those links do not "
                    f"support their claim")


def gate_regime():
    """Every legal claim must be dateable. Undated is stale."""
    legal, pre, undated, blank = 0, [], [], []
    for lane, fn, c in load_claims():
        r = c.get("regime") or {}
        side = (r.get("regime_side") or "").upper()
        norm_ = (r.get("norm") or "").strip().upper()
        is_legal = norm_ not in ("", "NONE", "N/A") or c.get("evidence_type") == "primary_law"
        if not is_legal:
            continue
        legal += 1
        if side == "PRE" and not any(c["id"].startswith(d) for d in DECOY_LANES):
            pre.append((lane, c["id"], c["statement"][:80]))
        if side in ("", "UNKNOWN"):
            blank.append((lane, c["id"], c["statement"][:80]))
        dates = [(s.get("date_of_content") or "").strip().upper() for s in c.get("sources") or []]
        if side == "POST" and dates and all(d in ("", "UNDATED") or d < REGIME_DATE for d in dates):
            undated.append((lane, c["id"], c["statement"][:80]))
    print(f"\n[regime] {legal} legal claims · {len(pre)} tagged PRE · {len(blank)} undateable · "
          f"{len(undated)} POST claims resting only on pre-{REGIME_DATE}/undated sources")
    for grp, lbl in ((pre, "PRE-REGIME"), (blank, "UNDATEABLE"), (undated, "STALE-SUPPORT")):
        for lane, cid, st in grp[:8]:
            print(f"   {lbl} {lane}/{cid}: {st}")
    if pre:
        FAIL.append(f"regime: {len(pre)} claim(s) describe the pre-{REGIME_DATE} regime")
    if undated:
        WARN.append(f"regime: {len(undated)} POST claim(s) supported only by stale/undated sources — "
                    f"re-source or demote")


def gate_evidence():
    """No claim without a source; no source without a verbatim quote."""
    nosrc, noq, shortq = [], [], []
    for lane, fn, c in load_claims():
        srcs = c.get("sources") or []
        if not srcs:
            nosrc.append((lane, c["id"], c["statement"][:80])); continue
        for s in srcs:
            q = (s.get("quote_original") or "").strip()
            if not q:
                noq.append((lane, c["id"], s.get("url", "")[:70]))
            elif len(q) < 25:
                shortq.append((lane, c["id"], q))
    print(f"\n[evidence] {len(nosrc)} claims with no source · {len(noq)} sources with no quote · "
          f"{len(shortq)} quotes under 25 chars")
    for lane, cid, st in nosrc[:10]:
        print(f"   NOSRC {lane}/{cid}: {st}")
    if nosrc:
        FAIL.append(f"evidence: {len(nosrc)} claim(s) carry no source at all")
    if noq:
        WARN.append(f"evidence: {len(noq)} source(s) carry no verbatim quote")


def gate_tiers():
    off = []
    for lane, fn, c in load_claims():
        if c.get("evidence_type") != "primary_law":
            continue
        hosts = [re.sub(r"^www\.", "", re.sub(r"https?://([^/]+).*", r"\1", s.get("url", "")))
                 for s in c.get("sources") or []]
        if hosts and not any(_tier_a(h) for h in hosts):
            off.append((lane, c["id"], hosts[:2]))
    print(f"\n[tiers] {len(off)} primary_law claim(s) citing no tier-A domain")
    for lane, cid, h in off[:10]:
        print(f"   OFF-TIER {lane}/{cid}: {h}")
    if off:
        FAIL.append(f"tiers: {len(off)} legal claim(s) rest on non-authoritative domains")


def gate_shape():
    claims = load_claims()
    per = Counter(l for l, _, _ in claims)
    print(f"\n[shape] {len(claims)} claims across {len(per)} lane-dirs: {dict(per)}")
    lanes_seen = defaultdict(set)
    for lane, fn, c in claims:
        lanes_seen[lane].add(fn)
    for lane, files in sorted(lanes_seen.items()):
        print(f"   {lane}: {len(files)} files, {sum(1 for l,_,_ in claims if l==lane)} claims")
    # Two engines answering the same lane SHOULD produce the same claim ids. Key by lane+id.
    dupes = [i for i, n in Counter(f"{l}/{c['id']}" for l, f, c in claims).items() if n > 1]
    if dupes:
        WARN.append(f"shape: duplicate claim ids: {dupes[:8]}")


GATES = {"shape": gate_shape, "evidence": gate_evidence, "quotes": gate_quotes,
         "urls": gate_urls, "regime": gate_regime, "tiers": gate_tiers}

if __name__ == "__main__":
    want = sys.argv[1:] or list(GATES)
    for g in want:
        GATES[g]()
    print("\n" + "=" * 72)
    for w in WARN:
        print(f"WARN     {w}")
    for f in FAIL:
        print(f"BLOCKER  {f}")
    print(f"{len(FAIL)} blocker(s), {len(WARN)} warning(s)")
    sys.exit(1 if FAIL else 0)
