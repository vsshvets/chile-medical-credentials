#!/usr/bin/env python3
"""Detect text accidentally duplicated immediately after itself.

Mechanical find-and-replace can nest a replacement inside its own match, leaving a run of words
repeated back-to-back:
    "щоб (1) викладати щоб (1) викладати на медичному…"
    "і різниця не і різниця не в кілька разів…"
It reads as garbage but breaks no other check — links resolve, numbers match, no calques — so it
shipped once in the page subtitle before this existed.

THE ALGORITHM MATTERS. An earlier version slid a fixed 22-character window and looked for the same
window twice. The repeated unit in the shipped defect was 18 characters, so no 22-character window
could ever repeat and the check silently passed everything — the second dead gate in this repo.
This version instead asks directly, at every position: is the next k characters equal to the k
after that? That is what "repeated immediately" means, and it cannot miss by window size.
"""
import re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KMIN, KMAX = 10, 80    # length of the repeated run to look for


def adjacent_repeat(p: str):
    """Return the repeated run if some substring is immediately followed by itself."""
    n = len(p)
    for i in range(n - KMIN * 2):
        for k in range(KMIN, min(KMAX, (n - i) // 2) + 1):
            if p[i:i + k] == p[i + k:i + 2 * k] and p[i:i + k].strip():
                return p[i:i + k]
    return None


def dupes(text):
    out = []
    for para in re.split(r"\n\s*\n", text):
        if para.lstrip().startswith("|") or "\n|" in para:
            continue
        clean = re.sub(r"(?m)^>\s?", "", para)          # blockquotes hid the shipped defect
        clean = re.sub(r"\]\([^)]*\)", "]", clean)
        clean = re.sub(r"https?://\S+", " ", clean)
        p = " ".join(clean.split())
        if len(p) < KMIN * 2:
            continue
        frag = adjacent_repeat(p)
        if frag:
            out.append((frag, p[:130]))
    return out


def main():
    bad = 0
    for f in sorted(REPO.rglob("*.md")):
        rel = str(f.relative_to(REPO))
        if rel.startswith(("raw/", ".git/")):
            continue
        body = re.split(r"(?m)^##+\s*Джерела\s*$", f.read_text(encoding="utf-8"))[0]
        for frag, ctx in dupes(body):
            print(f"  DUPLICATED {rel}: «{frag[:70]}»")
            print(f"             in: {ctx}")
            bad += 1
    print(f"{'FAIL' if bad else 'OK'}: {bad} self-duplicated passage(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
