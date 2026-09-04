#!/usr/bin/env python3
"""Write the 31 university pages in Ukrainian. One job per page, numbers injected from the CSV."""
import csv, json, sys, importlib.util
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "codex_direct", Path.home() / "Projects/claude-sops/scripts/lib/codex_direct.py")
cx = importlib.util.module_from_spec(spec); sys.modules["codex_direct"] = cx
spec.loader.exec_module(cx)

OUT = REPO / "research/pages"; OUT.mkdir(parents=True, exist_ok=True)
STAGE = cx.workspace("chile-med-pages")
SCHEMA = REPO / "scripts/schema_page.json"
SPEC = (REPO / "scripts/uni_page_spec.md").read_text(encoding="utf-8")
TERMS = (REPO / "data/terms.csv").read_text(encoding="utf-8")

RULES = """
УКРАЇНСЬКА МОВА — читає українська професорка медицини. Кожен із цих пунктів — дефект:
- ЖОДНИХ русизмів і кальок: не «на протязі» (протягом), не «у відповідності з» (відповідно до),
  не «приймати участь» (брати участь), не «задача» замість «завдання», не «даний» замість «цей»,
  не «являється» замість «є», не «в залежності від» (залежно від), не «слідуючий» (наступний),
  не «міроприємство» (захід), не «учбовий» (навчальний), не «поступити» до ВНЗ (вступити).
- ЖОДНИХ активних дієприкметників (працюючий, керуючий) — в українській мові їх немає.
- ЖОДНИХ літер ы э ъ ё.
- Апостроф лише U+2019: п'ять, м'який, з'явитися.
- Не пиши перекладною мовою. Перечитай кожне речення й спитай, чи так написала б українська професорка.

ІСПАНСЬКІ НАЗВИ — головне правило:
Ніколи не транслітеруй те, що вона писатиме в документах: назви університетів, факультетів,
лікарень, міст, посад, порталів. Вони лишаються іспанською з усіма наголосами
(Universidad de Valparaíso, Facultad de Medicina, Concepción, Hospital Clínico).
Кирилиця — щоб читати, іспанська — щоб подавати документи.

ЧЕСНІСТЬ:
- Ніколи не вигадуй декана, e-mail, підрозділ, лікарню чи вакансію. «Не вдалося підтвердити» —
  це правильна й цінна відповідь. Перелічи все таке в unverified_items.
- Будь-яке твердження про відкриті вакансії супроводжується датою: «станом на 3 вересня 2026».
- Жодних маркетингових прикметників — ані своїх, ані скопійованих із сайту університету.
- ЖОДНОГО абзацу довшого за 400 символів. Порахуй перед тим, як віддати результат.
"""


def clip(o, n=2600):
    return json.dumps(o, ensure_ascii=False)[:n]


rows = {r["slug"]: r for r in csv.DictReader((REPO / "data/medical-schools.csv").open())}
want = sys.argv[1:] or list(rows)
jobs = []
for slug in want:
    r = rows[slug]
    src = REPO / f"research/universities/{slug}.json"
    if not src.exists():
        print(f"skip {slug}: no research"); continue
    d = json.loads(src.read_text())
    acc = (f"{r['prog_accred_years']} років, до {r['prog_accred_until']}"
           if r["prog_accred_years"] else "немає в реєстрі CNA")
    kind = ("державний" if r["is_state"] == "yes"
            else "приватний (CRUCH)" if r["is_cruch"] == "yes" else "приватний")
    prompt = f"""Напиши ОДНУ довідкову сторінку українською мовою. Сьогодні 3 вересня 2026 року.

ЧИТАЧКА: українка, лікарка, кандидатка медичних наук, доцентка кафедри ревматології українського
медичного університету, десятиліття викладання. Вона фахівчиня у своїй справі і початківець у
чилійській бюрократії. Пиши для шанованої старшої колеги — без повчального тону й без води.

DO NOT RUN SHELL COMMANDS. No curl, no wget, no scripts. Work only from the data given below.

УНІВЕРСИТЕТ: {r['institution']} ({r['short_name']})

ЧИСЛА — БЕРИ ЛИШЕ ЗВІДСИ, не з дослідження і не з пам'яті:
- Тип: {kind}
- Регіони: {r['regions'].replace(' | ', ', ')}
- Кампусів з медициною: {r['campuses_with_medicina']} — {r['campus_list']}
- Студентів медицини (matrícula total 2026): {r['matricula_total_2026']}
- Набір 1-го курсу (matrícula primer año 2026): {r['matricula_primer_ano_2026']}
- Жінок: {r['pct_women']}%
- Акредитація програми (CNA): {acc}
- Тривалість навчання: {r['duration_semesters']} семестрів
- Нова програма 2026 року: {'ТАК — тому загальна кількість дорівнює першому курсу' if r['new_programme_2026']=='yes' else 'ні'}

ДАНІ ДОСЛІДЖЕННЯ (факти для прози; усе, чого тут немає, — «не вдалося підтвердити»):
Факультет: {clip(d['faculty_of_medicine'])}
Ревматологія: {clip(d['rheumatology'])}
Клінічні бази: {clip(d['teaching_hospitals'], 900)}
Наймання: {clip(d['hiring'])}
Міжнародне: {clip(d['international'], 900)}
Профіль (англійською — переклади суть українською, не дослівно): {clip(d['profile_paragraphs'], 3200)}
Джерела: {clip(d['sources'], 2600)}

{SPEC}

ЗАМОК ТЕРМІНОЛОГІЇ (ці українські відповідники ВЖЕ ВИРІШЕНІ, вживай саме їх):
{TERMS}

{RULES}

Поверни ПОВНУ сторінку в полі markdown. Slug: "{slug}". Перше посилання-хлібна крихта має вести
на README.md у тій самій теці й на ../README.md."""
    jobs.append(cx.Job(key=slug, prompt=prompt, schema=SCHEMA, out=OUT / f"{slug}.json",
                       model="gpt-5.6-terra", stall_s=1500, retries=2))

rep = cx.run_jobs(jobs, width=14, stage="pages", stage_dir=STAGE,
                  expected_keys={j.key for j in jobs}, allow_missing=True)
print(rep.summary())
