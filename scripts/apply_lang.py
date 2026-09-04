#!/usr/bin/env python3
"""Apply language-review findings to a document. Exact matches only, never fuzzy.

The reviewer never edits the file; this does, and only where the quoted text matches EXACTLY.
Anything else is reported for a human. A fuzzy match here would silently corrupt a fact.

  python3 scripts/apply_lang.py README.md            apply every pass's findings
  python3 scripts/apply_lang.py README.md L1 L4      selected passes
  python3 scripts/apply_lang.py README.md --dry      report only
"""
import json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LANG = REPO / "research/lang"

# A "rewrite" that is really a note to a human. Applying these would insert prose about the fix
# into the document itself.
REFUSAL = re.compile(r"^(без перепису|не пропоную|потрібно уточнити|рекоменд)", re.I)


def norm_ws(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    target = REPO / sys.argv[1]
    dry = "--dry" in sys.argv
    passes = [a for a in sys.argv[2:] if not a.startswith("--")]
    text = target.read_text(encoding="utf-8")

    findings = []
    for f in sorted(LANG.glob(f"{target.stem}.*.json")):
        pid = f.stem.split(".")[-1]
        if passes and pid not in passes:
            continue
        d = json.loads(f.read_text())
        for x in d["findings"]:
            findings.append((pid, x))
    # blockers first, then major, then minor
    order = {"blocker": 0, "major": 1, "minor": 2}
    findings.sort(key=lambda t: order.get(t[1]["severity"], 3))

    applied = skipped = refused = stale = 0
    report = []
    for pid, x in findings:
        q, r = x["quoted_text"], x["suggested_rewrite"]
        if not q or not r or REFUSAL.match(r.strip()):
            refused += 1
            report.append(("REFUSAL", pid, x["severity"], norm_ws(q)[:80], norm_ws(r)[:80]))
            continue
        if q == r:
            skipped += 1
            continue
        if q in text:
            text = text.replace(q, r, 1)
            applied += 1
            continue
        # Whitespace-insensitive retry: the document is hard-wrapped, the reviewer quoted it
        # flowed onto one line. Build the pattern by joining tokens with \s+ — re.escape does
        # NOT escape spaces on modern Python, so escaping the whole string then substituting
        # "\ " silently never matches, and every wrapped finding is reported as stale.
        flat_q = norm_ws(q)
        pat = re.compile(r"\s+".join(re.escape(t) for t in flat_q.split()))
        m = pat.search(text)
        if m:
            text = text[:m.start()] + norm_ws(r) + text[m.end():]
            applied += 1
        else:
            stale += 1
            report.append(("NOT-FOUND", pid, x["severity"], norm_ws(q)[:80], norm_ws(r)[:80]))

    print(f"{len(findings)} findings · applied {applied} · already-correct {skipped} · "
          f"refusals {refused} · not found (text already changed) {stale}")
    for kind, pid, sev, q, r in report[:18]:
        print(f"  {kind:<10} {pid} [{sev}] «{q}»")
    if not dry:
        target.write_text(text, encoding="utf-8")
        print(f"wrote {target}")


if __name__ == "__main__":
    main()
