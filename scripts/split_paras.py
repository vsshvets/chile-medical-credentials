#!/usr/bin/env python3
"""Split any prose paragraph over 400 rendered characters at a sentence boundary.

The house rule is 400 characters of RENDERED text. Splitting is mechanical and safe: it never
changes a word, only where the line break falls. Tables, quotes, lists and headings are left alone.
"""
import re, sys
from pathlib import Path

LIMIT = 400


def rendered(p):
    """Length as the reader sees it: markdown link URLs do not count."""
    return len(re.sub(r"\]\([^)]*\)", "]", p))


def split_para(p):
    if rendered(p) <= LIMIT:
        return [p]
    # split on sentence end followed by a capital / quote / bold marker
    sents = re.split(r"(?<=[.!?»])\s+(?=[«**A-ZА-ЯЇІЄҐ])", p.replace("\n", " "))
    if len(sents) < 2:
        return [p]
    out, cur = [], ""
    for s in sents:
        cand = (cur + " " + s).strip()
        if cur and rendered(cand) > LIMIT:
            out.append(cur); cur = s
        else:
            cur = cand
    if cur:
        out.append(cur)
    return out


def process(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"\n\s*\n", text)
    changed, new = 0, []
    for b in blocks:
        s = b.strip()
        skip = (not s or s.startswith(("|", ">", "#", "-", "*", "```", "1.", "2.", "3.", "4.", "5.",
                                       "6.", "7.", "8.", "9."))
                or "\n|" in s or s.startswith("["))
        if skip or rendered(s) <= LIMIT:
            new.append(b); continue
        parts = split_para(s)
        if len(parts) > 1:
            changed += 1
            new.append("\n\n".join(parts))
        else:
            new.append(b)
    if changed:
        path.write_text("\n\n".join(x.strip("\n") for x in new).strip() + "\n", encoding="utf-8")
    return changed


if __name__ == "__main__":
    tot = 0
    for arg in sys.argv[1:]:
        for f in sorted(Path().glob(arg)) if "*" in arg else [Path(arg)]:
            n = process(f)
            tot += n
            if n:
                print(f"  {f}: split {n} paragraph(s)")
    print(f"{tot} paragraph(s) split")
