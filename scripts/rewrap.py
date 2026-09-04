#!/usr/bin/env python3
"""Re-wrap prose paragraphs to ~100 columns. Never touches tables, quotes, lists, code or headings.

Markdown renders either way; this keeps the source readable and the diffs small.
"""
import re, sys, textwrap
from pathlib import Path

W = 100


def wrap_block(b: str) -> str:
    s = b.strip("\n")
    t = s.lstrip()
    if (not t or t.startswith(("|", ">", "#", "-", "*", "```", "> "))
            or re.match(r"^\d+\.", t) or "\n|" in s or "```" in s):
        return b
    if max((len(l) for l in s.split("\n")), default=0) <= W:
        return b
    return "\n".join(textwrap.wrap(re.sub(r"\s+", " ", s), W, break_long_words=False,
                                   break_on_hyphens=False))


def main():
    for a in sys.argv[1:]:
        p = Path(a)
        t = p.read_text(encoding="utf-8")
        out = "\n\n".join(wrap_block(b) for b in re.split(r"\n\s*\n", t))
        p.write_text(out.rstrip() + "\n", encoding="utf-8")
        print(f"rewrapped {p}")


if __name__ == "__main__":
    main()
