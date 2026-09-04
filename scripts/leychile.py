#!/usr/bin/env python3
"""Fetch Chilean norms as VERBATIM text from the LeyChile XML API.

The human-facing bcn.cl/leychile pages are a JavaScript shell — fetching one returns no legal text
at all, so a quote "verified" against it would be verified against nothing. This endpoint returns
the real normative text plus the version dates the staleness gate depends on:

    https://www.bcn.cl/leychile/Consulta/obtxml?opt=7&idNorma=<id>

  python3 scripts/leychile.py 1158549 1221526 ...     fetch by idNorma
  python3 scripts/leychile.py --key                   fetch the norms this project turns on
  python3 scripts/leychile.py 1158549 --art 143       print one article verbatim
"""
import hashlib, json, re, sys, unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetchlib

REPO = Path(__file__).resolve().parent.parent
LAW = REPO / "sources/leychile"; LAW.mkdir(parents=True, exist_ok=True)
API = "https://www.bcn.cl/leychile/Consulta/obtxml?opt=7&idNorma={}"
NS = re.compile(r"\{[^}]*\}")

# The norms this project's answer actually turns on.
KEY_NORMS = {
    "1158549": "Ley 21.325 — Ley de Migración y Extranjería (art. 143 is the recognition rule)",
    "1221526": "Decreto 174/2024 MINEDUC — the reconocimiento/revalidación regulation",
    "270584":  "Ley 20.261 — EUNACOM",
    "1118991": "Ley 21.091 — Sobre Educación Superior (university autonomy)",
    "236392":  "Ley 18.834 — Estatuto Administrativo (art. 12 nationality rule)",
    "5595":    "Código Sanitario (art. 112 — who may practise medicine)",
    "1146301": "Ley 21.094 — Universidades Estatales",
}


def tag(e):
    return NS.sub("", e.tag)


def text_of(e):
    return " ".join(t.strip() for t in e.itertext() if t and t.strip())


def fetch(norma_id: str) -> dict:
    dest = LAW / f"{norma_id}.xml"
    if not dest.exists() or dest.stat().st_size < 500:
        _, raw, _, _ = fetchlib.get(API.format(norma_id), timeout=90)
        dest.write_bytes(raw)
    root = ET.fromstring(dest.read_bytes())
    meta = {"norma_id": norma_id, "url_api": API.format(norma_id),
            "url_human": f"https://www.bcn.cl/leychile/navegar?idNorma={norma_id}",
            "derogado": root.attrib.get("derogado", ""),
            "fecha_version_solicitada": root.attrib.get("fechaVersion", "")}
    parts, title = [], ""
    for e in root.iter():
        t = tag(e)
        if t == "Identificador":
            meta["fecha_promulgacion"] = e.attrib.get("fechaPromulgacion", "")
            meta["fecha_publicacion"] = e.attrib.get("fechaPublicacion", "")
        if t == "Organismo" and e.text and "organismo" not in meta:
            meta["organismo"] = e.text.strip()
        if t == "TituloNorma" and not title:
            title = text_of(e)
        if t in ("EstructuraFuncional", "Encabezado", "Anexo"):
            body = ""
            for c in e:
                if tag(c) == "Texto":
                    body = text_of(c); break
            if body:
                parts.append({"tipo": e.attrib.get("tipoParte", tag(e)),
                              "id_parte": e.attrib.get("idParte", ""),
                              "fecha_version": e.attrib.get("fechaVersion", ""),
                              "derogado": e.attrib.get("derogado", ""),
                              "transitorio": e.attrib.get("transitorio", ""),
                              "texto": body})
    meta["titulo"] = title
    meta["n_partes"] = len(parts)
    versions = sorted({p["fecha_version"] for p in parts if p["fecha_version"]})
    meta["version_range"] = f"{versions[0]} … {versions[-1]}" if versions else ""
    meta["latest_version"] = versions[-1] if versions else ""

    flat = "\n\n".join(f"[{p['tipo']} · versión {p['fecha_version']}"
                       + (" · DEROGADO" if "no derogado" not in p["derogado"] else "") + "]\n"
                       + p["texto"] for p in parts)
    (LAW / f"{norma_id}.txt").write_text(flat, encoding="utf-8")
    (LAW / f"{norma_id}.meta.json").write_text(
        json.dumps({**meta, "partes": parts}, ensure_ascii=False, indent=1), encoding="utf-8")
    # also store under the sha1 of the human URL so verify.py finds it like any other source
    h = hashlib.sha1(meta["url_human"].encode()).hexdigest()
    (REPO / f"sources/{h}.txt").write_text(flat, encoding="utf-8")
    return meta


def find_article(norma_id: str, art: str) -> list:
    parts = json.loads((LAW / f"{norma_id}.meta.json").read_text())["partes"]
    pat = re.compile(rf"art[íi]culo\s+{re.escape(art)}\b", re.I)
    return [p for p in parts if pat.search(p["texto"][:400])]


def main():
    args = [a for a in sys.argv[1:]]
    if "--art" in args:
        i = args.index("--art")
        nid, art = args[0], args[i + 1]
        fetch(nid)
        hits = find_article(nid, art)
        if not hits:
            print(f"Artículo {art} not found as its own part in norm {nid}")
            body = (LAW / f"{nid}.txt").read_text(encoding="utf-8")
            for m in re.finditer(rf"Art[íi]culo\s+{re.escape(art)}\b.{{0,1400}}", body, re.S | re.I):
                print(m.group(0)); break
            return
        for p in hits:
            print(f"--- {p['tipo']} · versión {p['fecha_version']} · {p['derogado']}")
            print(p["texto"][:2500]); print()
        return

    ids = list(KEY_NORMS) if ("--key" in args or not args) else args
    for nid in ids:
        try:
            m = fetch(nid)
            note = KEY_NORMS.get(nid, "")
            print(f"{nid}  {m['n_partes']:>4} partes · publicada {m.get('fecha_publicacion','?')} · "
                  f"versiones {m['version_range']} · {m['derogado']}")
            print(f"        {(m['titulo'] or note)[:110]}")
        except Exception as e:
            print(f"{nid}  FAILED: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
