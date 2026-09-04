#!/usr/bin/env python3
"""The Ukrainian language ladder. Codex reviews; it NEVER rewrites the file.

A language model editing prose silently changes facts. Every pass returns findings against a
numbered segment; a Claude editor applies them; then the citation gates re-run.

  python3 scripts/lang_review.py README.md            all passes
  python3 scripts/lang_review.py README.md L2 L6      selected passes
"""
import json, re, sys, importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "codex_direct", Path.home() / "Projects/claude-sops/scripts/lib/codex_direct.py")
cx = importlib.util.module_from_spec(spec); sys.modules["codex_direct"] = cx
spec.loader.exec_module(cx)

OUT = REPO / "research/lang"; OUT.mkdir(parents=True, exist_ok=True)
STAGE = cx.workspace("chile-med-lang")
SCHEMA = REPO / "scripts/schema_lang.json"

READER = """THE READER: a Ukrainian woman, doctor of medicine, кандидат медичних наук, доцент of
rheumatology at a Ukrainian medical university. Decades of teaching and publishing. She is an expert
in her field and a complete beginner in Chilean bureaucracy. She is not a bureaucrat, not a student,
and absolutely not a novice who needs to be talked down to. Write for a respected senior colleague."""

PASSES = {
"L1": ("gpt-5.6-sol", "xhigh", """PASS L1 — TRANSLATIONESE.

You are an editor at a Kyiv academic press. Judge this text as if it were written natively in
Ukrainian. It must not read as a translation.

Flag every segment whose word order, participial chains, possessive stacking, connective choice or
sentence rhythm betrays an English or Spanish original. Typical tells: English SVO order forced onto
Ukrainian, chains of nominalisations ("здійснення проведення оцінювання"), "є" copula overuse,
Spanish-style relative clauses, mechanical "цей/ця/це" where Ukrainian would drop the pronoun,
and paragraph-initial connectives translated one-for-one ("Крім того," "Однак," "Таким чином,"
repeated mechanically).

For each finding give a NATIVE rewrite that preserves EVERY fact, number, URL and Spanish term exactly.
Rate each ## section 1-5, where 5 = indistinguishable from native writing.
PASS BAR: no segment rated "clearly translated"; at most 5% "slightly foreign"."""),

"L2": ("gpt-5.6-sol", "xhigh", """PASS L2 — RUSSIANISMS AND CALQUES. THIS IS THE HARD ZERO.

For this reader a russianism is a correctness bug, not a style note. Find every one.

Known traps (not an exhaustive list — find others):
приймати участь → брати участь · на протязі → протягом · у відповідності з → відповідно до ·
при умові → за умови · любий → будь-який · слідуючий → наступний · вірний → правильний ·
задача → завдання · міроприємство → захід · в залежності від → залежно від · по питанню → з питання ·
área "даний" used for "this" → цей · "носить характер" → має характер · "являється" → є ·
active participles (працюючий, керуючий, наступаючий) → Ukrainian has no such form, rewrite ·
"з метою" overused → щоб · "на протязі року" · "більш детально" → докладніше ·
"в основному" → здебільшого · "у якості" → як · "приходити до висновку" → доходити висновку ·
"мати місце" → відбуватися · "по крайній мірі" → принаймні · "тим не менше" → проте ·
"на рахунок" → щодо · "співпадати" → збігатися · "відмінити" → скасувати ·
"учбовий" → навчальний · "міроприємство" · "справка" → довідка · "поступити" (до ВНЗ) → вступити

Also flag: Russian-mediated transliteration of foreign names, Russian orthography leaking in
(ы э ъ ё anywhere is an automatic blocker), and Russian-style patronymic or address forms.

Every confirmed russianism is severity "blocker".
PASS BAR: ZERO confirmed russianisms. This is the only hard zero in the ladder."""),

"L3": ("gpt-5.6-sol", "xhigh", """PASS L3 — MEDICAL, LEGAL AND ACADEMIC TERMINOLOGY.

Use live web search into zakon.rada.gov.ua, mon.gov.ua, moz.gov.ua and НАЗЯВО to check terms.

For every medical, legal, educational or administrative term ask:
(a) does this word actually exist in current Ukrainian?
(b) is it the term Ukrainian law / МОН / МОЗ actually uses?
(c) does it mean what this sentence needs it to mean?
(d) would a доцент of rheumatology actually say it?

NAMED TRAPS TO CHECK EXPLICITLY:
- «доцент» vs Spanish «docente». These are FALSE FRIENDS. «docente» means "teaching staff", not
  the rank «доцент». If the text ever equates them, that is a blocker.
- Chilean academic ranks must be DESCRIBED, never equated to Ukrainian ones. "Profesor Asociado is
  roughly comparable to доцент" is acceptable; "доцент = Profesor Asociado" is a blocker.
- «кандидат наук» / «доктор філософії» — check the text states the Ukrainian legal equation correctly.
- «нострифікація» vs «визнання» vs «підтвердження» — Ukrainian ENIC uses «визнання». Check which
  the text uses and whether it is consistent.
- Chile issues NO «ліцензія на медичну практику». It has registration in a Registro. If the text
  says "ліцензія", that is a factual error dressed as a word choice.
- «інтернатура» / «ординатура» vs Chilean «beca» — not the same thing.

PASS BAR: zero terms that do not exist or carry the wrong meaning."""),

"L4": ("gpt-5.6-terra", None, """PASS L4 — CASE GOVERNMENT AND AGREEMENT.

Check ONLY grammatical government and agreement. Do not comment on style.

Cover at minimum: згідно з + орудний · відповідно до + родовий · завдяки / всупереч / наперекір +
давальний · на підставі + родовий · потребувати / зазнати / набувати / вимагати + родовий ·
numeral-noun agreement (два роки / п'ять років / 21 рік / 22 місяці) · дієприслівникові звороти
attached to the wrong subject · agreement of adjectives with borrowed nouns · prepositional case
after «у/в» vs «на» with institutions (в університеті / на факультеті).

For each: the phrase, the governing word, the case required, the case used, and the correction.
PASS BAR: zero uncorrected government errors."""),

"L5": ("gpt-5.6-luna", None, """PASS L5 — TRANSLITERATION OF SPANISH PROPER NOUNS.

Every Spanish proper noun rendered in Cyrillic must be rendered the SAME WAY everywhere, and must
follow Ukrainian (not Russian) transliteration.

Rules for this document:
- Spanish «j» → х (Jorge → Хорхе), never ж
- silent «h» is dropped (Chile → Чилі)
- «v» → в (Valparaíso → Вальпараїсо)
- «ñ» → нь · «ll» → й or ль · «y» as vowel → і
- Ukrainian «ї» after a vowel: Вальпараїсо, not Вальпараисо (Russian form)
- «Santiago» → Сантьяго · «Concepción» → Консепсьйон
- Ukrainian «г» for Spanish «g», never Russian «г» pronounced as [g] confusion — use г, not ґ,
  unless the text has established otherwise

List EVERY Cyrillic rendering of a Spanish name you find, with its Spanish original. Flag any name
rendered two different ways anywhere in the text, and any Russian-mediated form.
PASS BAR: one Spanish name, one Cyrillic form, everywhere."""),

"L6": ("gpt-5.6-sol", "xhigh", """PASS L6 — REGISTER.

Read the WHOLE document as one piece and judge the register.

Flag:
- talking down to the reader, over-explaining what a professor already knows
- HR / startup / marketing register ("ключовий крок", "важливо розуміти", "давайте розглянемо")
- undecoded legalese dumped on the reader without a plain-language gloss
- register DRIFT: one section formal and another chatty
- AI/chatbot tells: «важливо зазначити», «варто пам'ятати», «у цій статті ми розглянемо»,
  «слід мати на увазі», «підсумовуючи вищесказане», «отже, як ми бачимо», rhetorical questions
  used as section openers, tricolon padding, and any sentence that exists only to announce the
  next sentence
- false warmth or reassurance not supported by the facts

Rate each ## section 1-5 for register fit.
PASS BAR: all sections within 1 point of each other, none below 3. Any AI tell is an automatic
rewrite regardless of score."""),

"L7": ("gpt-5.6-terra", "xhigh", """PASS L7 — BACK-TRANSLATION FIDELITY. THIS IS A CORRECTNESS PASS, NOT A LANGUAGE PASS.

Translate the document literally back into English, sentence by sentence — literally, not elegantly.

Then, for every factual statement, report the MODALITY the Ukrainian actually carries:
  MUST (обов'язково / потрібно / вимагається)
  MAY (може / дозволяється / є можливість)
  USUALLY (зазвичай / як правило / на практиці)
  UNKNOWN (невідомо / не вдалося підтвердити)

Flag as a BLOCKER any sentence where the Ukrainian asserts a stronger modality than a careful reading
would support — for example «потрібно підтвердити диплом» where the underlying rule is that a
university MAY require it. A modality flip is wrong advice to a real person, and it is the single
most likely way a language edit breaks this document.

Also flag: numbers that changed, dates that changed, Spanish terms altered or dropped, negations lost.
PASS BAR: zero modality inflations, zero altered facts."""),
}


def segment(md: str) -> str:
    """Number every block so a finding can point at one. A finding with no id is discarded."""
    out, n = [], 0
    for block in re.split(r"\n\s*\n", md):
        if not block.strip():
            continue
        n += 1
        out.append(f"[[{n}]] {block}")
    return "\n\n".join(out)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    target = REPO / sys.argv[1]
    want = sys.argv[2:] or list(PASSES)
    md = target.read_text(encoding="utf-8")
    seg = segment(md)
    terms = (REPO / "data/terms.csv").read_text(encoding="utf-8")
    jobs = []
    for pid in want:
        model, effort, brief = PASSES[pid]
        prompt = f"""You are reviewing a Ukrainian-language document. Today is 3 September 2026.

{READER}

{brief}

THE FROZEN TERMINOLOGY LOCK (data/terms.csv) — these Ukrainian renderings are DECIDED. Do not
suggest changing them; do flag any place the text departs from them:
{terms}

RULES FOR YOUR OUTPUT:
- Point every finding at a [[N]] segment marker. A finding without one will be thrown away.
- quoted_text must be copied VERBATIM from the segment.
- suggested_rewrite must preserve every fact, number, date, URL and Spanish term EXACTLY as they
  appear. You are fixing language, not content. If fixing the language would require changing a
  fact, do not rewrite — flag it and say so.
- Do NOT rewrite the document. Findings only.

THE DOCUMENT ({target.name}), segmented:

{seg}
"""
        jobs.append(cx.Job(key=f"{target.stem}-{pid}", prompt=prompt, schema=SCHEMA,
                           out=OUT / f"{target.stem}.{pid}.json", model=model, effort=effort,
                           stall_s=2400, retries=2))
    rep = cx.run_jobs(jobs, width=len(jobs), stage=f"lang-{target.stem}", stage_dir=STAGE,
                      expected_keys={j.key for j in jobs}, allow_missing=True)
    print(rep.summary())
    for j in jobs:
        if j.out.exists():
            d = json.loads(j.out.read_text())
            b = sum(1 for f in d["findings"] if f["severity"] == "blocker")
            print(f"  {d['pass_id']:<3} {d['overall_verdict']:<16} "
                  f"{len(d['findings']):>3} findings ({b} blockers) — {d['verdict_reason'][:80]}")


if __name__ == "__main__":
    main()
