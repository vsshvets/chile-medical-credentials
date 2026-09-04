#!/usr/bin/env python3
"""One Codex job per university with a Medicina programme. One agent, one file, no clobbering."""
import csv, sys, importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "codex_direct", Path.home() / "Projects/claude-sops/scripts/lib/codex_direct.py")
cx = importlib.util.module_from_spec(spec); sys.modules["codex_direct"] = cx
spec.loader.exec_module(cx)

OUT = REPO / "research/universities"; OUT.mkdir(parents=True, exist_ok=True)
STAGE = cx.workspace("chile-med-unis")
SCHEMA = REPO / "scripts/schema_uni.json"

rows = list(csv.DictReader((REPO / "data/medical-schools.csv").open()))
want = sys.argv[1:]
if want:
    rows = [r for r in rows if r["slug"] in want]

jobs = []
for r in rows:
    prompt = f"""Today is 3 September 2026. Use live web search. Research ONE Chilean university.

UNIVERSITY: {r['institution']} ({r['short_name']})
Its Medicina programme, per the official SIES 2026 dataset: {r['matricula_total_2026']} students total,
{r['matricula_primer_ano_2026']} in first year, across {r['campuses_with_medicina']} campus(es) in
{r['regions'].replace(' | ', ', ')}. Type: {r['type']} / {r['subtype']}.

WHO THIS IS FOR: a Ukrainian doctor — PhD, associate professor of rheumatology at a Ukrainian medical
university, currently in Ukraine with no Chilean visa. She is deciding which Chilean medical faculties
are worth approaching, for a teaching post and/or clinical work. Everything you find should serve that
decision.

FIND, from the university's OWN website wherever possible:
1. The medical faculty: official Spanish name, URL, founding year, current dean, contact email, phone, address.
2. RHEUMATOLOGY: does the university or its teaching hospital have a rheumatology unit, department or
   service? Does it run a rheumatology specialty programme (especialidad / beca)? Give URLs and a
   verbatim Spanish quote proving it. If you cannot find one, answer "no" or "unknown" honestly —
   do NOT invent a department.
3. Teaching hospitals it is affiliated with.
4. HIRING: find the REAL page where academic vacancies (concursos académicos / "trabaja con nosotros"
   / "concursos") are published — not the homepage. Count how many academic posts are open TODAY.
   Read the requisitos of any open post and report VERBATIM what they say about foreign degrees,
   revalidación, or Chilean nationality. If nothing is open, say so plainly.
5. International: does it teach any medicine in English? International office URL.
6. 3-5 short factual paragraphs in ENGLISH profiling this medical faculty for her. Max 400 characters
   each. Facts with sources, not marketing language copied from the university.


DO NOT RUN SHELL COMMANDS. No curl, no wget, no scripts, no file writes. Use ONLY your built-in
web search and page reading. A job that runs a shell command is discarded in full, however good
its findings are.

EVIDENCE RULES:
- Every source you list needs a real URL you fetched and a VERBATIM quote from it.
- Never invent a dean's name, a department, an email or a vacancy. "unknown" is a correct answer.
- Do not copy the university's own promotional adjectives. Report what it IS, not how it sells itself.

Set slug to exactly "{r['slug']}". Return JSON matching the schema."""
    jobs.append(cx.Job(key=r["slug"], prompt=prompt, schema=SCHEMA,
                       out=OUT / f"{r['slug']}.json", model="gpt-5.6-terra",
                       stall_s=1800, retries=2))

rep = cx.run_jobs(jobs, width=16, stage="universities", stage_dir=STAGE,
                  expected_keys={r["slug"] for r in rows}, allow_missing=True)
print(rep.summary())
