#!/usr/bin/env python3
"""Wave 1: the 13 research lanes, direct Codex, schema-enforced, disk-idempotent.

Re-run any time. A lane whose out-file exists and validates is skipped instantly.
"""
import sys, importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

spec = importlib.util.spec_from_file_location(
    "codex_direct", Path.home() / "Projects/claude-sops/scripts/lib/codex_direct.py")
cx = importlib.util.module_from_spec(spec)
sys.modules["codex_direct"] = cx   # 3.14 dataclasses read sys.modules[cls.__module__]
spec.loader.exec_module(cx)

import lanes

OUT = REPO / "research" / "codex"
OUT.mkdir(parents=True, exist_ok=True)
STAGE = cx.workspace("chile-med-research")
SCHEMA = REPO / "scripts" / "schema_lane.json"

# sol for the three lanes that turn on subtle legal reading; terra elsewhere.
SOL = {"L01", "L04", "L06"}

WANT = sys.argv[1:] or [k for k in lanes.LANES if k != "L13"]

jobs = []
for lid in WANT:
    title, brief = lanes.LANES[lid]
    prompt = f"""You are a meticulous research analyst. Today is 3 September 2026.
You are researching ONE lane of a larger project. Use live web search extensively.

LANE {lid} — {title}

{lanes.SUBJECT}
{lanes.RULES}

YOUR ASSIGNMENT:
{brief}


DO NOT RUN SHELL COMMANDS. No curl, no wget, no scripts, no file writes. Use ONLY your built-in
web search and page reading. A job that runs a shell command is discarded in full, however good
its findings are.

Return JSON matching the schema exactly. Set lane_id to "{lid}".
Aim for 10-25 well-evidenced claims. Quality of evidence beats quantity of claims.
Every claim id must start with "{lid}-C".
"""
    jobs.append(cx.Job(
        key=lid,
        prompt=prompt,
        schema=SCHEMA,
        out=OUT / f"{lid}.json",
        model="gpt-5.6-sol" if lid in SOL else "gpt-5.6-terra",
        effort="xhigh" if lid in SOL else None,
        stall_s=2400,
        retries=2,
        meta={"title": title},
    ))

rep = cx.run_jobs(jobs, width=13, stage=f"research-{'-'.join(WANT)[:40]}",
                  stage_dir=STAGE, expected_keys=set(WANT), allow_missing=True)
print(rep.summary())
for k in sorted(set(WANT) - {j.key for j in jobs if cx.is_done(j)}):
    print(f"  MISSING: {k}")
