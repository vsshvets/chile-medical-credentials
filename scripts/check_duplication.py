#!/usr/bin/env python3
"""Detect text accidentally duplicated inside itself.

Mechanical find-and-replace can nest a replacement inside its own match, producing
"X and the difference is not **X and the difference is not an order of magnitude.**, but an order
of magnitude.**". It reads as garbage but breaks no other check: links resolve, numbers match,
no calques. Roughly 200 such replacements were applied to this repo, so this looks for the damage.
"""
import re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MIN = 40   # a repeated run this long inside one paragraph is not natural prose


def dupes(text):
    """Prose only. URLs from one domain repeat naturally in a source list, and table rows share
    their scaffolding — comparing those produces nothing but false positives (30 of them, first
    time round). So links, tables and list scaffolding come out before anything is compared."""
    out = []
    for para in re.split(r"\n\s*\n", text):
        if para.lstrip().startswith("|") or "\n|" in para:
            continue
        # drop link targets and bare URLs, keep the human-readable text
        clean = re.sub(r"\]\([^)]*\)", "]", para)
        clean = re.sub(r"https?://\S+", " ", clean)
        clean = re.sub(r"^\s*[-*]\s+", " ", clean, flags=re.M)
        p = " ".join(clean.split())
        if len(p) < MIN * 2:
            continue
        seen = {}
        for i in range(len(p) - MIN):
            frag = p[i:i + MIN]
            if frag in seen and i - seen[frag] > MIN:
                out.append((frag, p[:90]))
                break
            seen.setdefault(frag, i)
    return out


def main():
    bad = 0
    for f in sorted(REPO.rglob("*.md")):
        rel = str(f.relative_to(REPO))
        if rel.startswith(("raw/", ".git/")):
            continue
        body = f.read_text(encoding="utf-8")
        # A source list legitimately repeats a long institution name across several link titles.
        body = re.split(r"(?m)^##+\s*Джерела\s*$", body)[0]
        for frag, ctx in dupes(body):
            print(f"  DUPLICATED {rel}: «{frag[:60]}…»")
            print(f"             in: {ctx}")
            bad += 1
    print(f"{'FAIL' if bad else 'OK'}: {bad} self-duplicated passage(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
