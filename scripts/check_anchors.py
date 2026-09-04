#!/usr/bin/env python3
"""Verify every in-page #anchor resolves to a real heading.

The repo validator checks FILE links, not fragments. A heading reworded after the table of
contents was written leaves a link that looks fine and goes nowhere — which is how a reader
clicks "Вакансії" and lands on nothing.

Two details of GitHub's rule that are easy to get wrong: a removed emoji LEAVES the space beside
it, so "## ⚡ Головне" anchors as "#-головне"; and EACH space becomes its own hyphen, so an em
dash between spaces yields a double hyphen. Collapsing whitespace reports correct links as broken.
"""
import re, sys, unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP = ("raw/", ".git/")


def slug(h: str) -> str:
    s = unicodedata.normalize("NFC", h).strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    return s.replace(" ", "-")


def main() -> int:
    bad = 0
    for f in sorted(REPO.rglob("*.md")):
        rel = str(f.relative_to(REPO))
        if any(rel.startswith(s) for s in SKIP):
            continue
        t = f.read_text(encoding="utf-8")
        heads = {slug(m.group(1)) for m in re.finditer(r"(?m)^#{1,6}\s+(.+?)\s*$", t)}
        for m in re.finditer(r"\]\(#([^)]+)\)", t):
            if m.group(1) not in heads:
                print(f"  BROKEN {rel} -> #{m.group(1)}")
                bad += 1
        # CROSS-FILE anchors: a link into another document's heading. The repo validator checks
        # that the FILE exists; nobody checks that the heading inside it does. Nine banner links
        # were added pointing at one heading in README.md — if it is ever reworded they all die
        # silently, and this is the only check that would notice.
        for m in re.finditer(r"\]\(([^)#\s]+\.md)#([^)]+)\)", t):
            dest = (f.parent / m.group(1)).resolve()
            if not dest.exists():
                continue  # the repo validator already reports a missing file
            dt = dest.read_text(encoding="utf-8")
            dheads = {slug(x.group(1)) for x in re.finditer(r"(?m)^#{1,6}\s+(.+?)\s*$", dt)}
            if m.group(2) not in dheads:
                print(f"  BROKEN {rel} -> {m.group(1)}#{m.group(2)}")
                bad += 1
    print(f"{'FAIL' if bad else 'OK'}: {bad} broken in-page anchor(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
