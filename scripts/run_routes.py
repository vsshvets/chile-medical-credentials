#!/usr/bin/env python3
"""Exhaustively enumerate every route + every portal, and settle what the remembered site was."""
import sys, importlib.util
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "codex_direct", Path.home() / "Projects/claude-sops/scripts/lib/codex_direct.py")
cx = importlib.util.module_from_spec(spec); sys.modules["codex_direct"] = cx
spec.loader.exec_module(cx)
OUT = REPO / "research/codex"; STAGE = cx.workspace("chile-med-routes")
SCHEMA = REPO / "scripts/schema_routes.json"

HEAD = """Today is 6 September 2026. Use live web search extensively. Answer in ENGLISH.

DO NOT RUN SHELL COMMANDS. No curl, no wget, no scripts. Built-in web search and page reading only.
A job that runs a shell command is discarded in full.

THE PERSON: Ukrainian citizen, in Ukraine, no Chilean visa/residency/RUT. Medical doctor
(Ukrainian medical degree), PhD (кандидат медичних наук), associate professor of rheumatology.
Wants to (a) teach at a Chilean medical faculty and/or (b) practise medicine in Chile.

ALREADY ESTABLISHED FROM PRIMARY TEXT — build on it, do not re-derive:
- Decreto 174/2024 MINEDUC, in force 2026-08-17, regulates reconocimiento / revalidación /
  convalidación. Art. 5: only STATE universities with institutional accreditation at ADVANCED
  level >= 5 years may act for professional titles and academic degrees. Art. 4: only for
  programmes they teach, accredited, with a graduated cohort.
- Art. 1: Universidad de Chile is covered by that reglamento only for TECHNICAL titles; for a
  professional title it acts under its own statute DFL 3/2006 art. 6.
- Ley 20.261 art. 1 inc. 3: passing EUNACOM means the professional "habrá revalidado
  automáticamente su título profesional de médico cirujano".
- Decreto Exento 384/2026 sets national maximum fees: 2 / 3 / 15 / 20 UTM by stage.
- No Chile-Ukraine mutual-recognition treaty exists.

EVIDENCE RULES: every claim needs a real URL you fetched and a VERBATIM Spanish quote from it.
Never invent a quote or a URL. "Not found" is a valid answer. Be precise about whether something
is LIVE TODAY versus historical."""

JOBS = {
"ROUTES": """YOUR TASK — enumerate EVERY route, exhaustively.

List every distinct legal path by which a foreign medical degree becomes usable in Chile. For each,
state exactly what you hold at the end and what it lets you do. Include routes that do NOT apply to
a Ukrainian, clearly marked, because she needs to know why they are closed to her.

At minimum consider, and confirm or rule out each:
1. Revalidación of the título profesional through Universidad de Chile (its own statute).
2. Revalidación/reconocimiento through another State university under Decreto 174/2024.
3. EUNACOM (Ley 20.261) as automatic revalidation.
4. Bilateral-treaty recognition (MINREL / MINEDUC convenio routes).
5. Reconocimiento of the academic degree (doctorado) as distinct from the professional title.
6. Specialty certification via CONACEM, and the Ley 20.261 art. 2 bis MINSAL-authorised route.
7. Registration in the Registro Nacional de Prestadores Individuales de Salud.
8. Anything else that exists that is not on this list.

For EACH route give the exact online portal URL where an applicant creates an account or files, or
NONE. State what identity document opens that account: passport, RUT, ClaveÚnica.

Then fill portals_that_are_not_routes: Chilean platforms she might FIND while searching and mistake
for a recognition route — say what each actually is and who it is for.""",

"PORTAL": """YOUR TASK — settle a specific memory, and map every online platform.

The person searching remembers "a website where you create an account, then confirm your
credentials" as a way to get a foreign degree recognised in Chile. Identify what that was. Examine
each of these and say precisely what it is, who may use it, whether a Ukrainian doctor can, and
whether it is live TODAY:

- https://reconocimientodetitulos.minrel.gob.cl/  (does this exist? what is it?)
- https://ucampus.uchile.cl/m/prorrectoria_revalidacion_postulacion/  and Cuenta UChile
- https://www.chileatiende.gob.cl/fichas/2461-reconocimiento-de-titulos-profesionales-obtenidos-en-el-extranjero
- The Superintendencia de Salud form at webserver.superdesalud.gob.cl (frmsoltitulo)
- https://www.eunacom.cl/inscripcion/
- Any MINEDUC "trámite digital" or Subsecretaría de Educación Superior platform
- Any SIES / mifuturo / Ayuda Mineduc account system
- ClaveÚnica itself — what is it, can a foreigner abroad get one

ALSO: was there previously a DIFFERENT online system for foreign-degree recognition in Chile that
has since been replaced or shut down? Search for historical MINEDUC/MINREL platforms, any system
predating Decreto 174/2024, and any that appears in older guidance but is now dead. If the answer
is that no such separate system ever existed and people are remembering the Universidad de Chile
Ucampus portal, say that plainly.

Fill routes[] with anything that turns out to be a genuine route; put everything else in
portals_that_are_not_routes.""",
}

jobs=[cx.Job(key=k, prompt=HEAD+"\n\n"+v, schema=SCHEMA, out=OUT/f"{k}.json",
             model="gpt-5.6-sol", effort="xhigh", stall_s=2700, retries=2)
      for k,v in JOBS.items()]
rep = cx.run_jobs(jobs, width=2, stage="routes", stage_dir=STAGE,
                  expected_keys=set(JOBS), allow_missing=True)
print(rep.summary())
