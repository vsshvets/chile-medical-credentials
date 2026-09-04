#!/bin/bash
# Checkpoint-commit the research run. Deriving tables again is free; re-collecting is not.
cd "$(dirname "$0")/.." || exit 1
git add -A
if ! git diff --cached --quiet; then
  git commit -q -m "Checkpoint: research run $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  git push -q origin main 2>/dev/null && echo "pushed $(date -u +%H:%M:%SZ)" || echo "push failed $(date -u +%H:%M:%SZ)"
else
  echo "no changes $(date -u +%H:%M:%SZ)"
fi
