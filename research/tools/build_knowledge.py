"""Validate and render the AX-Synth knowledge base.

Inputs : knowledge/*.toml (hand-extracted from the Roland manuals, see knowledge/README.md)
         research/script-schema.json (via axsynth.schema)
Outputs: knowledge/knowledge.json  machine-readable, KB text joined with data-model facts
         knowledge/knowledge.md    human-readable rendering

Validation (exit code 1 on any error):
  * unique ids; every param's group exists; every 'related' id exists
  * every schema path / effect member exists in Script.xml's data model
  * MFX numbers 1-78 present once, names equal A8EE.exe display names;
    chorus 1-2, reverb 1-4 present; 'control' member lists are subsets of 'schema'
Coverage (reported, not an error):
  * data-model values not referenced by any KB entry (reserves, generic slots,
    and schema-only members such as tempo-sync variants)

Usage: py -3 research/tools/build_knowledge.py
"""
from __future__ import annotations

import json
import re
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from axsynth.schema import Schema  # noqa: E402

KB = ROOT / "knowledge"
DOCS = {"EM": "AX-Synth Editor manual (docs/AX-SynthEditorManualE.pdf; text research/generated/editor-manual.pdf.txt)",
        "OM": "AX-Synth Owner's Manual (docs/AX-Synth_OM.pdf; text research/generated/owners-manual.pdf.txt)",
        "MI": "AX-Synth MIDI Implementation (docs/AX Synth docs.pdf; text research/generated/midi-implementation.pdf.txt)"}
UNIONS = {"mfx": ("PatchCommonMFX", "fm.pat.mfx"), "chorus": ("PatchCommonChorus", "fm.pat.cho"),
          "reverb": ("PatchCommonReverb", "fm.pat.rev")}


def norm(path: str) -> str:
    return re.sub(r"\[\d+\]", "[]", path)


def load_toml():
    data = defaultdict(list)
    files = {}
    for f in sorted(KB.glob("*.toml")):
        d = tomllib.loads(f.read_text(encoding="utf-8"))
        for key, items in d.items():
            for it in items:
                it["_file"] = f.name
            data[key].extend(items)
        files[f.name] = {k: len(v) for k, v in d.items()}
    return data, files


def build():
    """Validate and assemble the KB in memory. Returns (kb, errors)."""
    S = Schema.load()
    params_all = S.parameters(root=None)
    by_norm = defaultdict(list)
    for p in params_all:
        by_norm[norm(p.path)].append(p)

    data, files = load_toml()
    errors, warnings = [], []

    # ---- ids ---------------------------------------------------------------
    ids = {}
    for kind in ("concept", "group", "param"):
        for it in data[kind]:
            if it["id"] in ids:
                errors.append(f"duplicate id {it['id']} ({it['_file']})")
            ids[it["id"]] = kind
    for it in data["param"]:
        if it["group"] not in ids or ids[it["group"]] != "group":
            errors.append(f"param {it['id']}: unknown group {it['group']}")
    for kind in ("concept", "group", "param"):
        for it in data[kind]:
            for r in it.get("related", []):
                if r not in ids:
                    errors.append(f"{kind} {it['id']}: related id {r!r} not found")
            if it.get("doc", "EM") not in DOCS:
                errors.append(f"{kind} {it['id']}: unknown doc {it.get('doc')}")

    # ---- schema links for concepts/params ------------------------------------
    referenced = set()

    def model_facts(path):
        ps = by_norm.get(norm(path))
        if not ps:
            return None
        p0 = ps[0]
        return {"path": norm(path), "instances": len(ps),
                "addresses": [p.address for p in ps], "type": p0.type, "size": p0.size,
                "raw_range": list(p0.range) if p0.range else None, "default": p0.default,
                "enum": p0.enum, "enum_values": p0.enum_values, "display_offset": p0.display_offset,
                "doc_confirmed": p0.confidence == "script+doc", "source_line": p0.source["line"]}

    for kind in ("concept", "param"):
        for it in data[kind]:
            for path in it.get("schema", []):
                n = norm(path)
                is_struct = kind == "concept" and any(k.startswith(n + ".") for k in by_norm)
                if n not in by_norm and not is_struct:
                    errors.append(f"{kind} {it['id']}: schema path {path} not in data model")
                referenced.add(n)

    # ---- effect unions -------------------------------------------------------
    names = S.data["effect_unions"]["mfx"]["display_names"]["names"]
    effects_out = {}
    for key, (stype, base) in UNIONS.items():
        u = S.data["effect_unions"][key]
        groups = {g["index"]: g for g in u["groups"]}
        entries = data[key]
        seen = set()
        out = []
        for e in entries:
            n = e["number"]
            if n in seen:
                errors.append(f"{key} {n}: duplicate")
            seen.add(n)
            g = groups.get(n)
            if not g:
                errors.append(f"{key} {n}: no such type in data model")
                continue
            if key == "mfx" and names[n] != e["name"]:
                errors.append(f"mfx {n}: name {e['name']!r} != A8EE.exe {names[n]!r}")
            members = {m["name"].split("-", 1)[1]: m["name"] for m in g["members"]}
            used = set()
            params = []
            for p in e.get("param", []):
                ctl = p.get("control", False)
                if isinstance(ctl, list) and not set(ctl) <= set(p["schema"]):
                    errors.append(f"{key} {n} {p['label']}: control members not in schema")
                facts = []
                for m in p["schema"]:
                    if m not in members:
                        errors.append(f"{key} {n} {p['label']}: member {m!r} not in group")
                        continue
                    used.add(m)
                    full = f"{base}.{members[m]}"
                    referenced.add(full)
                    facts.append(model_facts(full))
                params.append({k: v for k, v in p.items() if not k.startswith("_")} | {"model": facts})
            schema_only = [members[m] for m in members if m not in used]
            out.append({k: v for k, v in e.items() if k not in ("param",) and not k.startswith("_")}
                       | {"file": e["_file"], "params": params, "schema_only_members": schema_only})
        expected = set(groups) - {0}
        if seen != expected:
            errors.append(f"{key}: numbers {sorted(expected - seen)} missing, {sorted(seen - expected)} extra")
        effects_out[key] = sorted(out, key=lambda x: x["number"])

    # ---- coverage of the non-union data model --------------------------------
    uncovered = []
    union_structs = {v[0] for v in UNIONS.values()}
    for np_, ps in sorted(by_norm.items()):
        p = ps[0]
        if p.path.split(".")[0] != "fm":
            continue
        if p.effect or (p.structure, p.name) in S.unreachable:
            continue
        if p.structure in union_structs and re.fullmatch(r"(mfx|chorus|reverb)Parameter\d+", p.name):
            continue  # generic slots: described through the per-type entries
        if np_ not in referenced:
            uncovered.append(np_)

    # ---- assemble JSON -------------------------------------------------------
    def clean(it):
        return {k: v for k, v in it.items() if not k.startswith("_")} | {"file": it["_file"]}

    kb = {
        "meta": {
            "title": "AX-Synth knowledge base",
            "generated_by": "research/tools/build_knowledge.py",
            "sources": DOCS,
            "files": files,
            "note": "Text is extracted from the Roland manuals (doc/pages on every entry). 'model' blocks are "
                    "joined from research/script-schema.json: raw stored ranges/defaults, addresses, enum labels "
                    "(enum[i] = raw enum_values[i] or raw_range[0]+i) and display offsets.",
        },
        "concepts": [clean(c) for c in data["concept"]],
        "groups": [clean(g) for g in data["group"]],
        "params": [clean(p) | {"model": [model_facts(s) for s in p.get("schema", [])]} for p in data["param"]],
        "mfx": effects_out["mfx"], "chorus": effects_out["chorus"], "reverb": effects_out["reverb"],
        "coverage": {
            "data_model_values_without_kb_entry": uncovered,
            "schema_only_effect_members": {k: {e["number"]: e["schema_only_members"] for e in v if e["schema_only_members"]}
                                           for k, v in effects_out.items()},
        },
    }
    return kb, errors + [f"WARNING {w}" for w in warnings]


def main():
    kb, errors = build()
    (KB / "knowledge.json").write_text(json.dumps(kb, indent=1, ensure_ascii=False), encoding="utf-8")
    (KB / "knowledge.md").write_text(render_md(kb), encoding="utf-8")
    effects_out = {k: kb[k] for k in ("mfx", "chorus", "reverb")}
    uncovered = kb["coverage"]["data_model_values_without_kb_entry"]

    n_eff_params = sum(len(e["params"]) for v in effects_out.values() for e in v)
    print(f"concepts={len(kb['concepts'])} groups={len(kb['groups'])} params={len(kb['params'])} "
          f"mfx={len(kb['mfx'])} chorus={len(kb['chorus'])} reverb={len(kb['reverb'])} effect_params={n_eff_params}")
    print(f"data-model values without KB entry: {len(uncovered)}")
    for u in uncovered:
        print("   ", u)
    so = sum(len(x) for v in kb["coverage"]["schema_only_effect_members"].values() for x in v.values())
    print(f"schema-only effect members (not in manual): {so}")
    for e in errors:
        print("ERROR", e)
    return 1 if any(not e.startswith("WARNING") for e in errors) else 0


# ------------------------------------------------------------------ rendering --
def fmt_model(model):
    parts = []
    for m in model or []:
        if not m:
            continue
        s = f"`{m['path']}` @ {m['addresses'][0]}"
        if m["instances"] > 1:
            s += f" (+{m['instances'] - 1})"
        s += f", raw {m['raw_range']}" if m["raw_range"] else ""
        parts.append(s)
    return "; ".join(parts)


def render_md(kb):
    L = ["# AX-Synth knowledge base", "",
         "Generated from `knowledge/*.toml` by `research/tools/build_knowledge.py`. **Do not edit by hand.** "
         "Machine-readable form: `knowledge.json`. Format and conventions: `knowledge/README.md`.", "",
         "Sources: " + "; ".join(f"**{k}** = {v}" for k, v in kb["meta"]["sources"].items()), "",
         "## Contents", "", "1. [Concepts](#concepts)", "2. [Parameters](#parameters)",
         "3. [MFX types](#mfx-types)", "4. [Chorus unit types](#chorus-unit-types)",
         "5. [Reverb unit types](#reverb-unit-types)", "6. [Coverage](#coverage)", ""]
    L += ["## Concepts", ""]
    for c in kb["concepts"]:
        L += [f"### {c['title']}", f"*id `{c['id']}` · {c.get('doc', 'EM')} p.{', '.join(map(str, c['pages']))}*", "",
              c["text"].strip(), ""]
        for n in c.get("notes", []):
            L.append(f"> {n}")
        if c.get("notes"):
            L.append("")
    L += ["## Parameters", ""]
    by_group = defaultdict(list)
    for p in kb["params"]:
        by_group[p["group"]].append(p)
    for g in kb["groups"]:
        L += [f"### {g['title']}", f"*group `{g['id']}` · {g.get('doc', 'EM')} p.{', '.join(map(str, g['pages']))}*", "",
              g.get("text", ""), ""]
        for p in by_group[g["id"]]:
            L.append(f"- **{p['label']}** ({p['values']}) *[{p.get('doc', 'EM')} p.{', '.join(map(str, p['pages']))}]*: {p['meaning']}")
            if p.get("matrix"):
                L.append(f"  - Matrix Control destination: {p['matrix']}")
            for n in p.get("notes", []):
                L.append(f"  - {n}")
            fm = fmt_model(p.get("model"))
            if fm:
                L.append(f"  - model: {fm}")
        L.append("")
    for key, title in (("mfx", "MFX types"), ("chorus", "Chorus unit types"), ("reverb", "Reverb unit types")):
        L += [f"## {title}", ""]
        if key == "mfx":
            L += ["`#` = usable as Multi-Effect Control / Matrix Control destination (EM p.44). Stored values are raw+32768.", ""]
        for e in kb[key]:
            head = f"### {e['number']:02d} {e.get('manual_name', e['name'])}"
            L += [head, f"*{e.get('category', key.upper())} · EM p.{', '.join(map(str, e['pages']))}*", "", e["description"], ""]
            for n in e.get("notes", []):
                L.append(f"> {n}")
            if e.get("notes"):
                L.append("")
            L += ["| Parameter | Values | # | Meaning | Data model |", "|---|---|---|---|---|"]
            for p in e["params"]:
                ctl = p.get("control", False)
                ctl = "#" if ctl is True else (ctl if isinstance(ctl, str) else ("#: " + ", ".join(ctl) if ctl else ""))
                meaning = p["meaning"] + (" " + " ".join(p.get("notes", [])) if p.get("notes") else "")
                members = ", ".join(f"`{m['path'].rsplit('.', 1)[1]}`" for m in p["model"] if m)
                L.append(f"| {p['label']} | {p['values']} | {ctl} | {meaning.replace('|', '/')} | {members} |")
            if e["schema_only_members"]:
                L += ["", "Schema-only members (in the data model, not described in the manual): "
                      + ", ".join(f"`{m}`" for m in e["schema_only_members"])]
            L.append("")
    L += ["## Coverage", "", "Data-model values (root `fm`) without a KB entry:", ""]
    L += [f"- `{u}`" for u in kb["coverage"]["data_model_values_without_kb_entry"]] or ["- none"]
    L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
