#!/usr/bin/env python3
"""Generate docs/SOURCES.md from the stored-source index. Never hand-typed."""
import json, re
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
idx = json.loads((REPO / "sources/index.json").read_text())

TIERS = [
 ("Первинне законодавство Чилі", ["bcn.cl", "leychile.cl", "diariooficial"]),
 ("Державні органи Чилі", [".gob.cl", "chileatiende", "mifuturo.cl", "cnachile.cl", "cned.cl"]),
 ("Іспит EUNACOM і професійні органи", ["eunacom.cl", "asofamech", "conacem", "sochire", "colegiomedico"]),
 ("Чилійські університети", ["uchile.cl", "uc.cl", "udec", "usach", "uv.cl", "ufro", "utalca",
                             "unab", "uss.cl", "udd.cl", "umayor", "uandes", "ucn.cl", "uct.cl",
                             "ubiobio", "ucentral", "uta.cl", "umag.cl", "uda.cl", "uantof",
                             "ucm.cl", "ucsc.cl", "uach.cl", "uoh.cl", "udp.cl", "uft.cl",
                             "ubo.cl", "uda", "userena", "ulagos", "uautonoma", "udalba"]),
 ("Українські джерела", [".gov.ua", ".ua/", "rada.gov"]),
 ("Інше", []),
]


def tier(u):
    for name, pats in TIERS[:-1]:
        if any(p in u.lower() for p in pats):
            return name
    return TIERS[-1][0]


groups = defaultdict(list)
for u, m in sorted(idx.items()):
    groups[tier(u)].append((u, m))

usable = sum(1 for m in idx.values() if m.get("chars", 0) > 200)
lines = [
 "# Джерела", "",
 f"Усі {len(idx)} джерел, на які спирається цей звіт. Кожне було завантажене й **збережене**, "
 f"щоб будь-яку цитату можна було перевірити пізніше, а не лише в момент дослідження.", "",
 f"**Придатних до перевірки: {usable} з {len(idx)}.** Причини недоступності вказані окремо нижче.", "",
 "> ⚠️ Сторінки `bcn.cl/leychile` — це JavaScript-оболонки: у їхньому HTML **немає тексту закону**.",
 "> Тому тексти чилійських законів беруться з машинного інтерфейсу LeyChile",
 "> (`Consulta/obtxml?opt=7&idNorma=…`) і зберігаються в [`sources/leychile/`](../sources/leychile/).",
 "> Скрипт: [`scripts/leychile.py`](../scripts/leychile.py).", "",
]
for name, _ in TIERS:
    rows = groups.get(name)
    if not rows:
        continue
    lines += [f"## {name}", "", "| Джерело | Стан | Дата отримання |", "|---|---|---|"]
    for u, m in rows:
        st = ("✅" if m.get("chars", 0) > 200 else "⚠️")
        note = m.get("source", "")
        label = re.sub(r"^https?://(www\.)?", "", u)
        if len(label) > 88:
            label = label[:85] + "…"
        extra = f" · {m['titulo'][:44]}" if m.get("titulo") else (f" · {note}" if note else "")
        lines.append(f"| [{label}]({u}) | {st}{extra} | {m.get('fetched_at','')[:10]} |")
    lines.append("")

dead = [(u, m) for u, m in sorted(idx.items()) if m.get("chars", 0) <= 200]
if dead:
    lines += ["## Джерела, які не вдалося зберегти", "",
              "Це не означає, що твердження хибне — означає, що його цитату не можна перевірити "
              "механічно проти збереженої копії.", "",
              "| Джерело | Причина |", "|---|---|"]
    for u, m in dead:
        why = m.get("error") or ("сторінка віддає порожній HTML (JavaScript-застосунок)"
                                 if m.get("status") == 200 else f"HTTP {m.get('status')}")
        lines.append(f"| `{re.sub(r'^https?://(www\\.)?', '', u)[:86]}` | {why} |")
    lines.append("")

lines += ["## Як це перебудувати", "", "```bash",
          "python3 scripts/capture.py             # завантажити й зберегти кожне цитоване джерело",
          "python3 scripts/leychile_backfill.py   # тексти законів через XML-інтерфейс LeyChile",
          "python3 scripts/build_sources.py       # перебудувати цю сторінку",
          "python3 scripts/verify.py              # механічні перевірки цитат, посилань і дат",
          "```", ""]
(REPO / "docs/SOURCES.md").write_text("\n".join(lines), encoding="utf-8")
print(f"wrote docs/SOURCES.md · {len(idx)} sources, {usable} usable, {len(dead)} unstorable")
