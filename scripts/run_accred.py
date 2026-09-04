#!/usr/bin/env python3
"""L14: which universities may ACTUALLY revalidate a foreign medical degree today.

Splits the work so no single job runs long: one job establishes the legal threshold and covers the
state universities that also teach Medicina; a second covers the remaining state universities.
"""
import csv, sys, importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "codex_direct", Path.home() / "Projects/claude-sops/scripts/lib/codex_direct.py")
cx = importlib.util.module_from_spec(spec); sys.modules["codex_direct"] = cx
spec.loader.exec_module(cx)

OUT = REPO / "research/codex"; OUT.mkdir(parents=True, exist_ok=True)
STAGE = cx.workspace("chile-med-accred")
SCHEMA = REPO / "scripts/schema_accred.json"

rows = list(csv.DictReader((REPO / "data/medical-schools.csv").open()))
state_med = [r["institution"] for r in rows if r["is_state"] == "yes"]

COMMON = """Today is 3 September 2026. Use live web search extensively.

BACKGROUND. Until 17 August 2026, Universidad de Chile held a "privativa y excluyente" legal monopoly
on revalidating and recognising foreign professional titles and academic degrees in Chile. Decreto
174/2024 of the Ministerio de Educación, together with article 143 of Ley 21.325, changed this: other
universities meeting an accreditation threshold may now do it too. This is only weeks old and almost
every page on the open web still describes the old regime.

THE PERSON THIS IS FOR: a Ukrainian doctor, PhD, associate professor of rheumatology, currently in
Ukraine with no Chilean visa or residency. She needs to know WHERE she can actually file.


DO NOT RUN SHELL COMMANDS. No curl, no wget, no scripts, no file writes. Use ONLY your built-in
web search and page reading. A job that runs a shell command is discarded in full, however good
its findings are.

EVIDENCE RULES:
- Every fact needs a real URL you fetched and a VERBATIM quote from that page. Never invent a quote.
- Authoritative sources: bcn.cl/leychile, diariooficial.interior.gob.cl, cnachile.cl (the CNA
  accreditation register), the universities' own .cl domains, mineduc.cl.
- If a university has NOT published a revalidation procedure, say so plainly. Legal empowerment is
  not the same as an operating process, and reporting the difference honestly is the point of this job.
- accreditation_years -1 and level UNKNOWN are acceptable answers. Guessing is not.
"""

jobs = [
    cx.Job(key="L14a",
           prompt=COMMON + f"""
YOUR TASK — PART A.

1. Establish the EXACT eligibility rule. Find Decreto 174/2024 and Ley 21.325 art. 143 and quote
   VERBATIM the text stating which institutions may recognise/revalidate foreign titles and degrees.
   State precisely: how many years of accreditation are required, at what level (básico / avanzado /
   excelencia), and whether the rule is limited to STATE universities or open to accredited private
   ones too. If the reported "five years of advanced accreditation" is wrong, say so.

2. For EACH of these 13 STATE universities — all of which run a Medicina programme — find in the CNA
   register (cnachile.cl) its current institutional accreditation: number of years, level, start date,
   end date. Then decide whether it meets the threshold. Then search that university's own site for a
   published reglamento or procedure for "reconocimiento y revalidación de títulos y grados
   extranjeros". Report the URL if it exists and say plainly if it does not.

{chr(10).join('   - ' + n for n in state_med)}

3. bottom_line: as of today, where can she realistically file, and is Universidad de Chile still in
   practice the only working route?

Return JSON matching the schema.""",
           schema=SCHEMA, out=OUT / "L14a.json", model="gpt-5.6-sol", effort="xhigh",
           stall_s=2700, retries=2),

    cx.Job(key="L14b",
           prompt=COMMON + """
YOUR TASK — PART B.

Chile has 18 state universities (universidades estatales, members of CUECH). Part A of this job
covers the 13 that run a Medicina programme. YOUR job covers the REST — every state university that
does NOT run a Medicina programme — plus any PRIVATE university that the eligibility rule also covers.

1. Enumerate the full list of Chilean state universities from an authoritative source (uestatales.cl
   or mineduc.cl) and quote it. Identify which ones Part A did not cover.

2. For each of those, find its CNA accreditation (years, level, dates) and whether it has published a
   reconocimiento/revalidación procedure since August 2026.

3. IMPORTANT: determine whether NON-state accredited universities are also empowered by the rule. If
   they are, identify the private universities that qualify and whether any has opened a process.

4. bottom_line: does any institution outside Universidad de Chile actually accept foreign
   degree-recognition files today? Answer honestly, including "none found".

Also set threshold_rule as in Part A, independently — do not assume.

Return JSON matching the schema.""",
           schema=SCHEMA, out=OUT / "L14b.json", model="gpt-5.6-sol", effort="xhigh",
           stall_s=2700, retries=2),
]

rep = cx.run_jobs(jobs, width=2, stage="accreditation", stage_dir=STAGE,
                  expected_keys={"L14a", "L14b"}, allow_missing=True)
print(rep.summary())
