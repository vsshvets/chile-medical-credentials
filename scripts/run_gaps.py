#!/usr/bin/env python3
"""Targeted lookups for the specific gaps the orchestrator could not close from primary text."""
import sys, importlib.util
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "codex_direct", Path.home() / "Projects/claude-sops/scripts/lib/codex_direct.py")
cx = importlib.util.module_from_spec(spec); sys.modules["codex_direct"] = cx
spec.loader.exec_module(cx)
OUT = REPO / "research/codex"; STAGE = cx.workspace("chile-med-gaps")
SCHEMA = REPO / "scripts/schema_gaps.json"

HEAD = """Today is 3 September 2026. Use live web search. Answer ONLY the questions asked, precisely.

DO NOT RUN SHELL COMMANDS. No curl, no wget, no scripts. Use only your built-in web search and page
reading. A job that runs a shell command is discarded in full.

CONTEXT ALREADY ESTABLISHED FROM PRIMARY SOURCES (do not re-derive, build on it):
- Decreto 174/2024 MINEDUC (published in the Diario Oficial 2026-02-17) entered into force 2026-08-17.
- Its art. 5: only STATE universities with institutional accreditation at ADVANCED level for at least
  5 years may recognise/revalidate foreign PROFESSIONAL titles and academic degrees.
- Its art. 4: an institution may only act for programmes it teaches, with at least one graduated
  cohort; and for compulsory-accreditation programmes (Medicina is one) only if its own programme
  holds that accreditation.
- Its art. 1: Universidad de Chile is covered by this reglamento ONLY for TECHNICAL titles; for
  professional titles it continues under DFL 3, 2006, MINEDUC, art. 6.
- Its art. 20 and second transitional article: MINEDUC had to fix the aranceles by administrative act
  within four months of publication, i.e. by about 17 June 2026.

EVIDENCE RULES: every answer needs a real URL and a VERBATIM Spanish quote from that page. If you
cannot resolve a question, set resolved to "no" and say what you checked. Guessing is worse than
"not found"."""

QS = """
QUESTIONS:

Q1. Find DFL N° 3 de 2006 del Ministerio de Educación (the consolidated Estatuto de la Universidad
de Chile, which consolidated DFL 153 de 1981). Give its LeyChile idNorma and the direct URL. Then
quote ARTÍCULO 6 VERBATIM and in full. State whether that article is currently in force, and give
the "Texto vigente" / última versión date shown by LeyChile. This article is what still governs
Universidad de Chile's power over foreign PROFESSIONAL titles, so the exact wording matters.

Q2. Did the Ministerio de Educación actually issue the administrative act fixing the ARANCELES
required by Decreto 174 art. 20 and its second transitional article? Search the Diario Oficial and
mineduc.cl for a 2026 decreto or resolución fixing aranceles for "reconocimiento y revalidación de
títulos... obtenidos en el extranjero". If it exists: give its number, date, URL, and the actual fee
amounts. If you cannot find it, say so plainly — that would mean the new route has no published
price and may not be operable.

Q3. Has the Subsecretaría de Educación Superior published the centralised digital platform or the
official list of institutions authorised to recognise/revalidate under Decreto 174? Give the URL if
it exists. Has MINEDUC published any guidance page for applicants since 17 August 2026?

Q4. Which Chilean STATE universities currently hold institutional accreditation at NIVEL AVANZADO
(or EXCELENCIA) for 5 or more years? Give each one's name, level, years, and accreditation expiry
date from the CNA register at cnachile.cl. This is the exact set art. 5 empowers. Be complete and
say which you could not verify.

Q5. For the Ukrainian side: what does Ukraine's Ministry of Education (MON) currently charge and how
long does it take to apostille a diploma, a diploma supplement, and a кандидат наук diploma in 2026,
during martial law? Give the official MON page and the fee. Also state whether Ukraine's electronic
apostille register is accepted abroad.
"""

jobs = [cx.Job(key="GAPS", prompt=HEAD + QS, schema=SCHEMA, out=OUT / "GAPS.json",
               model="gpt-5.6-sol", effort="xhigh", stall_s=2700, retries=2)]
rep = cx.run_jobs(jobs, width=1, stage="gaps", stage_dir=STAGE,
                  expected_keys={"GAPS"}, allow_missing=True)
print(rep.summary())
