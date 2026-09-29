"""Generate app/model.json: everything the web editor needs, from the
existing research outputs (no hand-typed parameter data, CLAUDE.md rule 5).

Sources
  - axsynth.schema (Script.xml extraction + doc cross-check): addresses,
    types, ranges, defaults, enum labels, display offsets, effect unions
  - research/script-schema.json: ui_bindings (control types), wave names,
    MFX type -> Control Assign table (parsed from Script.xml MFXDestination
    panels, line numbers kept), MFX display names
  - knowledge/knowledge.json: Editor-manual labels, groups, meanings, and
    per-effect parameter labels (Editor manual Effects List)
  - original-roland-files/Script/A8EE/InitialData.a8e (INIT patch, .a8e
    template), axsynth.factory (Tone list for the slot picker)

Usage: py -3 research/tools/build_web_model.py   (writes app/model.json)
"""
from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research" / "tools"))
from axsynth import factory, sysex  # noqa: E402
from axsynth.schema import Schema, addr_to_int  # noqa: E402

OUT = ROOT / "app" / "model.json"
SCRIPT = ROOT / "original-roland-files/Script/A8EE/Script.xml"
INITIAL = ROOT / "original-roland-files/Script/A8EE/InitialData.a8e"
GENERIC = re.compile(r"^(mfxParameter|chorusParameter|reverbParameter)\d+$")
UNION_KIND = {"PatchCommonMFX": "mfx", "PatchCommonChorus": "chorus", "PatchCommonReverb": "reverb"}
BLOCK_OF_STRUCT = {"PatchCommon": "common", "PatchCommonMFX": "mfx", "PatchCommonChorus": "cho",
                   "PatchCommonReverb": "rev", "PatchTMT": "tmt"}
READONLY_AREAS = [  # System/Setup: shown read-only (user decision 2026-09-28)
    {"name": "setup", "struct": "Setup", "address": "01 00 00 00", "size": 0x34},
    {"name": "system.common", "struct": "SystemCommon", "address": "02 00 00 00", "size": 0x1E},
    {"name": "system.controller", "struct": "SystemController", "address": "02 00 40 00", "size": 0x50},
]

# Simple mode = the settings the user picked as easy to grasp (2026-09-28):
# all of Common, MFX (not MFX control), chorus and reverb units with their
# type parameters, and per tone: coarse/fine tune, random pitch, wave L/R,
# tone delay mode/time, filter type + cutoff, TVA level + pan, all outputs/sends.
SIMPLE_GROUPS = {"common", "common.bend", "common.offset", "common.portamento",
                 "fx.mfx", "fx.chorus", "fx.reverb", "tone.output"}
SIMPLE_IDS = {"tone.coarse_tune", "tone.fine_tune", "tone.random_pitch", "tone.wave_number",
              "tone.delay_mode", "tone.delay_time", "tone.filter_type", "tone.cutoff",
              "tone.level", "tone.pan"}
EXPERT_IDS = {"mfx.output_assign"}   # user: expert-only even though its group is simple (2026-09-28)
# Shown as level faders (graphically distinct): tone outputs/sends + the other volume-like levels.
LEVEL_IDS = {"common.level", "tone.level", "mfx.output_level", "mfx.chorus_send", "mfx.reverb_send",
             "chorus.level", "reverb.level"}
# Expert-only effect members (user, 2026-09-29): those the manual doesn't list
# (schemaOnly tempo-sync variants) and those whose on-screen value would be a
# raw number above this (effect values without a display offset show 32768…).
SIMPLE_MAX_SHOWN = 32000

# Wave categories for the two-step wave picker (UI only; the wave number is
# unchanged). Roland publishes no categories for these 313 waves: the groups
# are our reading of the names, which the list keeps together by instrument
# [I]. (name, [(first, last), ...]); every wave 1-313 is in exactly one group
# (tests/test_web.py). 0 = OFF.
WAVE_CATEGORIES = [
    ("OFF (no wave)", [(0, 0)]),
    ("Piano & electric piano", [(1, 16), (254, 257)]),
    ("Clav, harpsichord & celesta", [(17, 25)]),
    ("Organ", [(26, 48), (258, 281), (309, 313)]),
    ("Guitar", [(49, 62)]),
    ("Harp, sitar & dulcimer", [(63, 68)]),
    ("Bass", [(69, 98)]),
    ("Woodwind, sax & reed", [(99, 112), (164, 164), (282, 296)]),
    ("Brass", [(113, 118), (297, 300)]),
    ("Strings & orchestra", [(119, 120), (301, 304)]),
    ("Synth pads & big saws", [(121, 127)]),
    ("Voices & choir", [(128, 137), (305, 308)]),
    ("Mallets & bells", [(138, 155)]),
    ("Digital & synth textures", [(156, 163), (165, 173)]),
    ("Synth saw", [(174, 193)]),
    ("Synth square & pulse", [(194, 212)]),
    ("Synth triangle, sine & other", [(213, 221)]),
    ("Noise & atmosphere", [(222, 233)]),
    ("Formant & vox", [(234, 241)]),
    ("Attacks & clicks", [(242, 253)]),
]
# MFX groups for the two-step type picker: Roland's own categories from the
# Editor manual's Effects List (knowledge/mfx-*.toml `category`) with
# plain-English names. A Roland category with a single type goes to
# "Miscellaneous" (user request 2026-09-29); 0 THROUGH is its own group.
MFX_CATEGORY_NAMES = {"FILTER": "Filter & EQ", "MODULATION": "Modulation (phaser, tremolo, pan…)",
                      "CHORUS": "Chorus & flanger", "DYNAMICS": "Drive & dynamics", "DELAY": "Delay",
                      "LO-FI": "Lo-fi", "PITCH": "Pitch shift", "REVERB": "Reverb",
                      "COMBINATION": "Combinations (two effects in series)"}


def enum_explanations(labels, meaning: str):
    """Per-value explanations from an Editor-manual meaning text written as
    'LPF (low pass): reduces … . BPF (band pass): …' (knowledge.json). Returns
    [{short, text}] in enum order, or None unless every label is explained."""
    if not labels or len(labels) < 2:
        return None
    out = []
    for lab in labels:
        m = re.search(r"(?:^|[.;]\s+)" + re.escape(lab) + r"(?:\s*\(([^)]*)\))?:\s*([^.;]*)", meaning)
        if not m:
            return None
        out.append({"short": m.group(1) or "", "text": m.group(2).strip()})
    return out


def readable_help(text: str, concepts: dict) -> str:
    """Group texts in knowledge.json are written for LLMs and point to other
    entries ('See concept X', 'knowledge/*.toml', 'Schema arrays'). For the
    UI, inline the referenced concept's first sentences and drop file refs."""
    def concept(m):
        c = concepts.get(m.group(1).rstrip("."))
        if not c:
            return ""
        first = re.split(r"(?<=\.)\s+", c["text"])
        return " ".join(first[:2])
    text = re.sub(r"Type-specific parameters: knowledge/[\w.-]+\.toml\.?", "Choose a type; its own settings appear below.", text)
    text = re.sub(r"\s*See knowledge/[\w.-]+ for [^.]*\.", "", text)
    text = re.sub(r"\s*\([^)]*knowledge/[^)]*\),?", "", text)
    text = re.sub(r"[;,]?\s*[Ss]ee concept ([a-z_]+\.[a-z_]+)(?: for [^.]*)?\.", lambda m: ". " + concept(m), text)
    text = " ".join(s for s in re.split(r"(?<=\.)\s+", text) if "Schema" not in s)
    return user_text(re.sub(r"\s*\.\s*\.", ".", text).strip(" .") + ".")


def user_text(text: str) -> str:
    """Drop research-only markup from KB text: sentences that are inference
    notes ([I]) and evidence tags such as [D MI], [F], [3P]."""
    text = " ".join(s for s in re.split(r"(?<=\.)\s+", text) if "[I]" not in s)
    return re.sub(r"\s*\[(?:D|F|3P)[^\]]*\]", "", text).strip()


def short_label(label: str):
    """A shorter on-screen name where the Editor-manual label is an
    abbreviation plus explanation: 'CHO (Chorus Send), OUTPUT ASSIGN = MFX'
    -> 'Chorus Send · via MFX'; 'RES (Resonance)' -> 'Resonance'. None if
    the label is fine as it is (the full label stays in the tooltip)."""
    m = re.match(r"^(\S{1,4})\s*\(([^)]+)\)(.*)$", label)
    if not m:
        return None
    head, paren, tail = m.groups()
    route = " · via MFX" if re.search(r"= MFX\b", tail) else " · direct" if "non MFX" in tail else ""
    extra = re.sub(r",?\s*OUTPUT ASSIGN = (non )?MFX", "", tail).strip()
    return f"{paren}{(' ' + extra) if extra else ''}{route}"


def split_label(label: str, n_schema: int, index: int) -> str:
    """'Wave Group Type / Wave Group ID' with two schema paths -> the part for
    this path; a short part ('R') borrows the first part's stem ('WAVE NUMBER R')."""
    parts = [x.strip() for x in label.split(" / ")]
    if n_schema < 2 or len(parts) != n_schema or "(" in label.split(" / ")[-1] and ")" not in parts[-1]:
        return label
    part = parts[index]
    if len(part) <= 3:
        part = re.sub(r"\s+\S{1,3}(\s*\(.*\))?$", "", parts[0]) + " " + part
    return part


def kb_path(path: str) -> str:
    """fm.pat.tone[2].lfoRate[1] -> fm.pat.tone[].lfoRate[] (knowledge.json form)."""
    return re.sub(r"\[\d+\]", "[]", path)


def suffix(path: str, drop_tone: bool) -> str:
    """Distinguishing part for multi-instance KB entries: name digits and
    array indices, e.g. matrixControl2Destination3 -> '2-3', lfoRate[1] -> '2'."""
    p = re.sub(r"^fm\.pat\.tone\[\d+\]\.", "", path) if drop_tone else path
    name = p.rsplit(".", 1)[-1]
    parts = re.findall(r"\d+", re.sub(r"\[\d+\]", "", name))
    parts += [str(int(i) + 1) for i in re.findall(r"\[(\d+)\]", name)]
    return "-".join(parts)


def shown_max(e: dict) -> int:
    """Largest number a slider shows for this value (0 for labelled values)."""
    if e["enum"] or e["control"] != "slider" or not e["range"]:
        return 0
    off = e["displayOffset"] or 0
    return max(abs(e["range"][0] + off), abs(e["range"][1] + off))


def mfx_categories(types: list) -> list:
    """[{name, roland, types}] in type-number order (see MFX_CATEGORY_NAMES)."""
    count: dict = {}
    for t in types:
        count[t["category"]] = count.get(t["category"], 0) + 1
    out: dict = {}
    for t in types:
        c = t["category"]
        name = ("No effect (THROUGH)" if t["number"] == 0 else
                MFX_CATEGORY_NAMES[c] if count[c] > 1 else "Miscellaneous")
        out.setdefault(name, {"name": name, "roland": [], "types": []})
        if c and c not in out[name]["roland"]:
            out[name]["roland"].append(c)
        out[name]["types"].append(t["number"])
    misc = out.pop("Miscellaneous", None)
    return list(out.values()) + ([misc] if misc else [])


def mfx_assign_tables(schema_json) -> dict[int, dict]:
    text = SCRIPT.read_text(encoding="ascii", errors="replace")
    out = {}
    for m in re.finditer(r"<type>MFXDestination</type>\s*<name>mfxType(\d+)</name>\s*<mfx>\$mfx</mfx>\s*"
                         r"<table>([^<]+)</table>", text):
        table = schema_json["stringTables"][m.group(2)]
        out[int(m.group(1))] = {"table": m.group(2), "labels": table["items"],
                                "line": text.count("\n", 0, m.start()) + 1}
    return out


def build() -> dict:
    S = Schema.load()
    sj = json.loads((ROOT / "research/script-schema.json").read_text(encoding="utf-8"))
    kb = json.loads((ROOT / "knowledge/knowledge.json").read_text(encoding="utf-8"))
    ui = sj["ui_bindings"]
    concepts = {c["id"]: c for c in kb["concepts"]}
    waves = [w.strip() for w in sj["stringTables"]["internalWaveNameTableA"]["items"]]
    child = S.child_types("Patch")

    blocks, block_base = [], {}
    for name, off in sysex.PATCH_BLOCKS:
        st = child[name.split("[")[0]][0]
        blocks.append({"name": name, "offset": off, "size": S.struct_size(st), "struct": st})
        block_base[name] = off

    def control_of(path: str, prm) -> str:
        b = ui.get(path) or ui.get(kb_path(path)) or ui.get("$tone." + prm.name) or {}
        types = b.get("control_types", [])
        if prm.type == "string":
            return "text"
        if "a8eWaveIndexSelect" in types:
            return "wave"
        if prm.enum:
            return "select"
        return "slider"

    # --- every editable patch value ------------------------------------------------
    params = {}
    for prm in S.parameters("fm"):
        if not prm.path.startswith("fm.pat."):
            continue
        if (prm.structure, prm.name) in S.unreachable:
            continue
        rel = prm.path[len("fm.pat."):]
        block = rel.split(".")[0]
        base = sysex.TEMPORARY_PATCH + block_base[block]
        um = S.union_membership.get((prm.structure, prm.name))
        params[prm.path] = {
            "block": block, "offset": addr_to_int(prm.address) - base, "size": prm.size, "type": prm.type,
            "range": prm.range, "default": prm.default, "displayOffset": prm.display_offset,
            "enum": prm.enum, "enumValues": prm.enum_values, "control": control_of(prm.path, prm),
            "label": None, "help": prm.description or "",
            "union": [UNION_KIND[prm.structure], um[1]] if um else None,
            "line": prm.source["line"],
            "hidden": bool(GENERIC.match(prm.name)) or "reserve" in prm.name,
        }

    # --- labels, help and panel layout from the knowledge base ----------------------
    groups = {g["id"]: g for g in kb["groups"]}
    sections: dict[str, list] = {}
    for kp in kb["params"]:
        concrete = []
        for sp in kp["schema"]:
            for path, e in params.items():
                if kb_path(path) == sp:
                    concrete.append(path)
        for path in concrete:
            e = params[path]
            tone = path.startswith("fm.pat.tone[")
            idx = kp["schema"].index(kb_path(path))
            own = split_label(kp["label"], len(kp["schema"]), idx)
            if own != kp["label"]:
                e["label"] = own
                e["help"] = readable_help((kp.get("meaning") or "") + (f" Values: {kp['values']}." if kp.get("values") else ""), concepts)
                e["kb"] = kp["id"]
                sections.setdefault(kp["group"], []).append(path)
                long = enum_explanations(e["enum"], kp.get("meaning") or "")
                if long:
                    e["enumLong"] = long
                continue
            sfx = suffix(path, drop_tone=True) if len(concrete) > (4 if tone else 1) else ""
            base_label = re.sub(r"\s*\d–\d\s*$", "", kp["label"]) if sfx else kp["label"]
            e["label"] = base_label + (f" {sfx}" if sfx else "")
            e["help"] = readable_help((kp.get("meaning") or "") + (f" Values: {kp['values']}." if kp.get("values") else ""), concepts)
            e["kb"] = kp["id"]
            sections.setdefault(kp["group"], []).append(path)
            # Editor-manual value list as labels where the script has none
            # (e.g. CHORUS OUTPUT SELECT "MAIN, MAIN+REV, REV"): only when the
            # list length equals the raw range size [D].
            items = [x.strip() for x in (kp.get("values") or "").split(",")]
            if (not e["enum"] and e["range"] and e["control"] == "slider"
                    and len(items) == e["range"][1] - e["range"][0] + 1 > 1 and all(items)):
                e["enum"], e["control"], e["enumSource"] = items, "select", "knowledge"
            long = enum_explanations(e["enum"], kp.get("meaning") or "")
            if long:
                e["enumLong"] = long

    # --- simple mode (user's selection, 2026-09-28) and level styling ----------------
    for path, e in params.items():
        if e["label"] and short_label(e["label"]):
            e["short"] = short_label(e["label"])
        kb_id, group = e.get("kb"), next((g for g, ps in sections.items() if path in ps), None)
        e["simple"] = ((group in SIMPLE_GROUPS or kb_id in SIMPLE_IDS
                        or bool(e["union"] and e["union"][1] > 0))      # MFX/chorus/reverb type parameters
                       and kb_id not in EXPERT_IDS)
        e["level"] = group == "tone.output" or kb_id in LEVEL_IDS

    def order(paths):
        return sorted(dict.fromkeys(paths), key=lambda p: (params[p]["block"], params[p]["offset"]))

    def sec(gid, paths):
        g = groups[gid]
        return {"id": gid, "title": g["title"], "help": readable_help(g["text"], concepts), "params": order(paths)}

    tone_groups = [g for g in groups if g.startswith("tone.")]
    panels = [
        {"id": "common", "title": "Common",
         "sections": [sec(g, sections.get(g, [])) for g in ("common", "common.bend", "common.offset", "common.portamento")]},
    ]
    for t in range(4):
        panels.append({"id": f"tone{t + 1}", "title": f"Tone {t + 1}", "tone": t,
                       "sections": [sec(g, [p for p in sections.get(g, []) if p.startswith(f"fm.pat.tone[{t}].")])
                                    for g in tone_groups]})
    panels.append({"id": "tmt", "title": "TMT / Structure",
                   "sections": [sec(g, sections.get(g, [])) for g in ("tmt.structure", "tmt.velocity", "tmt.key")]})
    matrix = sections.get("common.matrix", [])
    panels.append({"id": "matrix", "title": "Matrix Control",
                   "sections": [sec("common.matrix", [p for p in matrix if not p.startswith("fm.pat.tone[")])] +
                               [dict(sec("common.matrix", [p for p in matrix if p.startswith(f"fm.pat.tone[{t}].")]),
                                     id=f"common.matrix.tone{t + 1}", title=f"Tone {t + 1}: matrix control switches")
                                for t in range(4)]})
    panels.append({"id": "effects", "title": "Effects",
                   "sections": [sec(g, sections.get(g, [])) for g in ("fx.routing", "fx.mfx", "fx.mfx_control", "fx.chorus", "fx.reverb")]})

    # --- effect types: per-type parameter lists with Editor-manual labels ------------
    assign = mfx_assign_tables(sj)
    effects = {}
    for kind, key, disc in (("mfx", "mfx", "fm.pat.mfx.mfxType"), ("chorus", "chorus", "fm.pat.cho.chorusType"),
                            ("reverb", "reverb", "fm.pat.rev.reverbType")):
        union = sj["effect_unions"][kind]
        names = union.get("display_names", {}).get("names")
        types = []
        for g in union["groups"]:
            n = g["index"]
            entry = next((x for x in kb[key] if x["number"] == n), None)
            label = {}
            if entry:
                for ep in entry["params"]:
                    for m in ep["model"]:
                        label[m["path"]] = (ep["label"], readable_help((ep.get("meaning") or "") +
                                            (f" Values: {ep['values']}." if ep.get("values") else ""), concepts))
            plist = []
            if n > 0:
                for m in g["members"]:
                    path = "fm.pat." + m["path"]
                    if path not in params:
                        continue
                    lab, hlp = label.get(path, (None, None))
                    params[path]["label"] = lab or m["name"].split("-", 1)[-1]
                    params[path]["help"] = hlp or ("Tempo-sync variant; not in the AX-Synth manual "
                                                   "(leave at its default)." if lab is None else params[path]["help"])
                    params[path]["schemaOnly"] = lab is None
                    plist.append(path)
            t = {"number": n, "name": (names[n] if names else (entry["name"] if entry else ("OFF" if n == 0 else str(n)))),
                 "category": entry.get("category") if entry else None, "description": entry.get("description") if entry else None,
                 "params": plist}
            if kind == "mfx":
                t["assign"] = assign.get(n)
            types.append(t)
        effects[kind] = {"discriminator": disc, "types": types}
        params[disc]["enum"] = [t["name"] for t in types]
        params[disc]["control"] = "effectType"
    effects["mfx"]["categories"] = mfx_categories(effects["mfx"]["types"])

    # --- expert-only effect members (see SIMPLE_MAX_SHOWN) -----------------------------
    for path, e in params.items():
        if e["union"] and e["union"][1] > 0 and (e.get("schemaOnly") or shown_max(e) > SIMPLE_MAX_SHOWN):
            e["simple"] = False

    # --- read-only System/Setup ------------------------------------------------------
    ro_params = []
    for area in READONLY_AREAS:
        for prm in S.parameters("fm"):
            if prm.structure != area["struct"]:
                continue
            kp = next((k for k in kb["params"] if prm.path in k["schema"] or kb_path(prm.path) in k["schema"]), None)
            if kp is None:
                continue
            ro_params.append({"path": prm.path, "area": area["name"], "offset": addr_to_int(prm.address) - addr_to_int(area["address"]),
                              "size": prm.size, "type": prm.type, "label": kp["label"], "displayOffset": prm.display_offset,
                              "enum": prm.enum, "enumValues": prm.enum_values, "range": prm.range})

    # --- .a8e template: leaf struct order and sizes -----------------------------------
    a8e_layout, pos = [], 0x100
    for path, st in S.leaf_structs("fm"):
        a8e_layout.append({"path": path, "struct": st, "offset": pos, "size": S.struct_size(st)})
        pos += S.struct_size(st)

    missing_labels = [p for p, e in params.items() if e["label"] is None and not e["hidden"]]
    return {
        "meta": {"generator": "research/tools/build_web_model.py",
                 "sources": ["research/script-schema.json", "research/generated/crosscheck.json",
                             "knowledge/knowledge.json", "original-roland-files/Script/A8EE/Script.xml",
                             "original-roland-files/Script/A8EE/InitialData.a8e"],
                 "temporaryPatch": sysex.TEMPORARY_PATCH, "unlabelled": missing_labels},
        "blocks": blocks, "params": params, "panels": panels, "effects": effects, "waves": waves,
        "waveCategories": [{"name": n, "waves": [w for a, b in r for w in range(a, b + 1)]} for n, r in WAVE_CATEGORIES],
        "readonly": {"areas": READONLY_AREAS, "params": ro_params},
        "a8e": {"layout": a8e_layout, "size": pos, "initial": base64.b64encode(INITIAL.read_bytes()).decode()},
        "factory": [{"n": t.user_patch_index, "slot": t.librarian_slot, "family": t.group, "name": t.name}
                    for t in factory.tones() if t.user_patch_index is not None],
        "identityReply": list(sysex.IDENTITY_REPLY_DOC),
    }


def main():
    model = build()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(model, separators=(",", ":")), encoding="utf-8")
    p = model["params"]
    print(f"wrote {OUT.relative_to(ROOT)}: {len(p)} params, {len(model['panels'])} panels, "
          f"{sum(len(t['params']) for t in model['effects']['mfx']['types'])} MFX members, "
          f"unlabelled {len(model['meta']['unlabelled'])}")
    for u in model["meta"]["unlabelled"][:20]:
        print("  unlabelled:", u)


if __name__ == "__main__":
    main()
