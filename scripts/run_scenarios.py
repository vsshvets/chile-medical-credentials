#!/usr/bin/env python3
"""L13: money and time for the three scenarios, built on everything already established."""
import json, glob, sys, importlib.util
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "codex_direct", Path.home() / "Projects/claude-sops/scripts/lib/codex_direct.py")
cx = importlib.util.module_from_spec(spec); sys.modules["codex_direct"] = cx
spec.loader.exec_module(cx)
OUT = REPO / "research/codex"; STAGE = cx.workspace("chile-med-scenarios")

def digest():
    out = []
    for f in sorted(glob.glob(str(REPO / "research/*/*.json"))):
        if ".voided." in f or "/universities/" in f:
            continue
        d = json.loads(Path(f).read_text())
        lane = Path(f).parent.name + "/" + Path(f).stem
        for c in (d.get("claims") or [])[:22]:
            out.append(f"[{lane}] {c.get('statement','')[:300]}")
    return "\n".join(out)

ESTABLISHED = """
ALREADY ESTABLISHED FROM PRIMARY SOURCES — treat as given, do not re-derive, but DO verify any number:
- Decreto 174/2024 MINEDUC: published 2026-02-17, in force 2026-08-17. Art. 5: only STATE universities
  with institutional accreditation at ADVANCED level >= 5 years may revalidate foreign PROFESSIONAL
  titles. Art. 4: only for programmes they teach, with a graduated cohort, and for compulsory-
  accreditation programmes (Medicina) only if their own programme is accredited. Art. 1: Universidad
  de Chile is covered by this reglamento only for TECHNICAL titles; for a professional title it
  continues under DFL 3/2006 art. 6 and its own DU Exento N 0030.203 of 2005.
- Ley 20.261 art. 1 inc. 3, verbatim: passing EUNACOM means the professional "habra revalidado
  automaticamente su titulo profesional de medico cirujano, sin necesitar cumplir ningun otro
  requisito para este efecto." EUNACOM is therefore an ALTERNATIVE to revalidacion, not a step after it.
- EUNACOM is never sat abroad. A passport suffices to register; no RUT, visa or residency needed.
- Reported UChile revalidation fees: 2 + 3 + 15 UTM, plus a diploma fee; MINEDUC Decreto Exento N 384
  of 17 June 2026 reportedly fixes those national ceilings. VERIFY the decree number and the amounts.
- Reported EUNACOM fees: about CLP 310,000 (seccion teorica) + CLP 720,000 (seccion practica).
- CONACEM treats Reumatologia as derived from Medicina Interna: a foreign applicant must certify in
  Internal Medicine FIRST, then Rheumatology — two certifications, four exams, in Spanish.
- She is in Ukraine, has no RUT, no visa, no Chilean bank account. Her son lives in Chile and can act
  as a proxy where a Chilean resident is needed.
"""

prompt = f"""Today is 3 September 2026. Use live web search to verify every figure you state.

DO NOT RUN SHELL COMMANDS. No curl, no wget, no scripts. Built-in web search and page reading only.
A job that runs a shell command is discarded in full.

THE PERSON: Ukrainian citizen in Vinnytsia, Ukraine. Medical doctor, кандидат медичних наук (PhD),
доцент (associate professor) of rheumatology at Vinnytsia National Medical University. Teaches
rheumatology, has taught international students in English. Assume no Spanish. No Chilean residency,
no visa, no RUT, no Chilean bank account. Her son lives in Chile.

{ESTABLISHED}

FINDINGS FROM THE RESEARCH LANES SO FAR (leads to build on, not gospel):
{digest()[:14000]}

YOUR TASK — three scenarios, costed and timed honestly.

Scenario A — she takes an ACADEMIC post at a Chilean medical faculty, no patient contact.
Scenario B — academic post that INCLUDES clinical teaching with patients.
Scenario C — full clinical practice as a rheumatologist.

For each, as process_steps: every required step in order, the actor, where it happens, whether
presence in Chile is required, whether a RUT is required, the cost with its unit, and realistic
min/max duration in days. Order them so the reader can follow them as instructions.

Then in claims[], per scenario: total realistic cost, total realistic elapsed time, what is strictly
REQUIRED versus merely useful, and the single biggest risk of that scenario failing.

Cost every line: Ukrainian apostilles (MON for education documents), official translation into
Spanish, courier of originals, Chilean aranceles, EUNACOM fees, CONACEM fees, Superintendencia
registry, visa fees, flights and accommodation for each step requiring presence, and Spanish tuition
to a working clinical level.

CURRENCY RULE: give the current UTM value in CLP and the month it applies to. Give a CLP/USD and a
CLP/UAH rate with its date. A CLP figure quoted without its UTM original and month is wrong within
30 days, so always record the UTM value where the source states UTM.

Be honest about the cheapest realistic path and say plainly which scenario is best value for her.
Do not flatter. If a scenario is impractical, say so and say why.

Set lane_id to "L13". Return JSON matching the schema."""

jobs = [cx.Job(key="L13", prompt=prompt, schema=REPO / "scripts/schema_lane.json",
               out=OUT / "L13.json", model="gpt-5.6-sol", effort="xhigh", stall_s=2700, retries=2)]
rep = cx.run_jobs(jobs, width=1, stage="scenarios", stage_dir=STAGE,
                  expected_keys={"L13"}, allow_missing=True)
print(rep.summary())
