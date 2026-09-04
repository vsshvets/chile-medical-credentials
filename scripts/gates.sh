#!/bin/bash
# Every gate this repo must pass before it ships. Any red stops the ship.
cd "$(dirname "$0")/.." || exit 1
fail=0
run() { echo; echo "── $1"; shift; "$@" || fail=1; }
run "house documentation validator" python3 ~/.claude/skills/github-docs-assistant/scripts/validate.py .
run "in-page and cross-file anchors" python3 scripts/check_anchors.py
run "headline numbers vs datasets"  python3 scripts/check_numbers.py
run "university pages vs dataset"   python3 scripts/verify_pages.py
run "self-duplicated text"            python3 scripts/check_duplication.py
run "evidence, quotes, links, regime stamps" python3 scripts/verify.py
echo; [ $fail -eq 0 ] && echo "ALL GATES PASS" || echo "GATES FAILED"
exit $fail
