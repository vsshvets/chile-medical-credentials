#!/usr/bin/env python3
"""Wave 2: reconcile the two independent engines lane by lane. Codex sol adjudicates.

Only runs a lane where BOTH engines produced a file — a one-sided lane has nothing to reconcile.
"""
import json, sys, importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "codex_direct", Path.home() / "Projects/claude-sops/scripts/lib/codex_direct.py")
cx = importlib.util.module_from_spec(spec); sys.modules["codex_direct"] = cx
spec.loader.exec_module(cx)

CODEX, CLAUDE = REPO / "research/codex", REPO / "research/claude"
OUT = REPO / "research/merged"; OUT.mkdir(parents=True, exist_ok=True)
STAGE = cx.workspace("chile-med-reconcile")
SCHEMA = REPO / "scripts/schema_reconcile.json"


def trim(d: dict) -> str:
    """Only the fields the adjudicator needs — full files blow the latency budget."""
    out = {"claims": [], "open_questions": d.get("open_questions", [])[:6],
           "unknowns_declared": d.get("unknowns_declared", [])[:8]}
    for c in d.get("claims") or []:
        out["claims"].append({
            "id": c.get("id"), "statement": c.get("statement"),
            "confidence": c.get("confidence"), "regime_side": (c.get("regime") or {}).get("regime_side"),
            "sources": [{"url": s.get("url"), "date": s.get("date_of_content"),
                         "quote": (s.get("quote_original") or "")[:320]}
                        for s in (c.get("sources") or [])[:2]],
        })
    return json.dumps(out, ensure_ascii=False, indent=0)


pairs = []
for f in sorted(CODEX.glob("L*.json")):
    g = CLAUDE / f.name
    if g.exists():
        pairs.append((f.stem, f, g))
    else:
        print(f"  skip {f.stem}: no Claude counterpart")
if not pairs:
    sys.exit("no lanes have both engines' output yet")

want = sys.argv[1:]
if want:
    pairs = [p for p in pairs if p[0] in want]

jobs = []
for lid, cf_, clf in pairs:
    a, b = json.loads(cf_.read_text()), json.loads(clf.read_text())
    prompt = f"""Today is 3 September 2026. You are the ADJUDICATOR.

Two independent research engines — one OpenAI, one Anthropic — were given the IDENTICAL brief for
lane {lid} of a project about recognising a Ukrainian doctor's credentials in Chile. Neither saw the
other's work. Your job is to reconcile them into one trustworthy answer.

This matters because it is advice for a real person planning a move. A wrong answer costs her money
and months.

ENGINE A (OpenAI Codex) produced:
{trim(a)}

ENGINE B (Anthropic Claude) produced:
{trim(b)}

YOUR TASK:
1. AGREEMENTS — where both independently reached the same finding. These are the strongest claims in
   the project. Pick the better-evidenced source of the two for each.
2. CONFLICTS — where they say materially different things. THIS IS THE MOST VALUABLE PART OF YOUR JOB.
   For each conflict you MUST go and check the primary source LIVE yourself before adjudicating.
   Do not simply prefer the more confident-sounding engine. Rate materiality honestly: does this
   change the ADVICE she receives, or only a detail? If you cannot settle it, say UNRESOLVED and say
   exactly what would settle it. An honest UNRESOLVED is worth more than a confident guess.
3. SINGLE-ENGINE FINDINGS — anything material that only one engine found. Verify each one LIVE.
   A finding one engine missed entirely is either a genuine discovery or a hallucination; decide which.
4. GAPS — anything the brief asked for that NEITHER engine answered.

CRITICAL CONTEXT: on 17 August 2026 Decreto 174/2024 with Ley 21.325 art. 143 ended the Universidad
de Chile monopoly on revalidating foreign degrees. Most of the open web still describes the old regime.
If one engine describes the old regime and the other the new one, that is not a tie — check the date
of each source and prefer the one that is actually current.

Set lane_id to "{lid}". Return JSON matching the schema."""
    jobs.append(cx.Job(key=lid, prompt=prompt, schema=SCHEMA, out=OUT / f"{lid}.json",
                       model="gpt-5.6-sol", effort="xhigh", stall_s=2700, retries=2))

rep = cx.run_jobs(jobs, width=min(13, len(jobs)), stage="reconcile", stage_dir=STAGE,
                  expected_keys={p[0] for p in pairs}, allow_missing=True)
print(rep.summary())
