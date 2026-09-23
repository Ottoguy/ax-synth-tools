"""Extract the Koa data-model schema from Roland's AX-Synth Editor Script.xml.

Reads (never modifies) original-roland-files/Script/A8EE/Script.xml and writes
research/script-schema.json.

Design rules:
  * Preserve raw text exactly (addresses/sizes stay as the hex-token strings
    Roland wrote). Derived/decoded fields are added alongside, never instead.
  * Every element carries its source line number in Script.xml.
  * Nothing about UI layout is interpreted beyond what links values to
    display tables (stringTableRef / offsetValue / unit) - those links are
    recorded as evidence, not as facts about the hardware.

Usage:  python research/tools/extract_script_schema.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "original-roland-files" / "Script" / "A8EE" / "Script.xml"
OUT = ROOT / "research" / "script-schema.json"
SRC_REL = "original-roland-files/Script/A8EE/Script.xml"


# --------------------------------------------------------------------------
# Parsing with line numbers (ElementTree drops them; use expat directly)
# --------------------------------------------------------------------------
LINES: dict[int, int] = {}  # id(element) -> source line (elements stay alive via the tree)


def parse_with_lines(text: str) -> ET.Element:
    """Build an ElementTree, recording each element's line in LINES.

    The file declares Shift_JIS but is pure ASCII (0 bytes > 0x7F), and expat
    rejects Shift_JIS, so the declaration is dropped. The remainder still
    starts on line 1, so line numbers match the original file.
    """
    from xml.parsers import expat
    body = text.split("?>", 1)[1] if text.startswith("<?xml") else text
    p = expat.ParserCreate()
    stack: list[ET.Element] = []
    root: list[ET.Element] = []

    def start(tag, attrs):
        e = ET.Element(tag, attrs)
        LINES[id(e)] = p.CurrentLineNumber
        e.text = ""
        if stack:
            stack[-1].append(e)
        else:
            root.append(e)
        stack.append(e)

    def end(tag):
        stack.pop()

    def chars(data):
        if stack:
            stack[-1].text += data

    p.StartElementHandler = start
    p.EndElementHandler = end
    p.CharacterDataHandler = chars
    p.Parse(body, True)
    return root[0]


def txt(e, tag):
    c = e.find(tag)
    return None if c is None else (c.text or "").strip()


def line(e):
    return LINES.get(id(e))


# --------------------------------------------------------------------------
# Address arithmetic
# --------------------------------------------------------------------------
def hex_tokens(s: str | None):
    """'00 00 1F 00' -> [0,0,0x1F,0]; returns None for macros like $address."""
    if s is None or s.startswith("$"):
        return None
    toks = s.split()
    if not all(re.fullmatch(r"[0-9A-Fa-f]{2}", t) for t in toks):
        return None
    return [int(t, 16) for t in toks]


def to_int7(tokens):
    """Right-aligned big-endian 7-bit bytes -> integer (sum of b * 128^i).

    Deliberately lenient: Script.xml contains two offsets with a byte > 0x7F
    ('00 81', '00 85' for stepPitchShifter-bal/level). Decoding them
    base-128 gives 129/133 == '01 01'/'01 05', the official MFX Parameter
    29/30 slots. Callers flag such bytes via has_invalid_7bit().
    """
    v = 0
    for b in tokens:
        v = v * 128 + b
    return v


def has_invalid_7bit(tokens):
    return tokens is not None and any(b > 0x7F for b in tokens)


def from_int7(v, width=4):
    out = []
    for _ in range(width):
        out.append(v & 0x7F)
        v >>= 7
    if v:
        raise ValueError("address overflow")
    return list(reversed(out))


def fmt(tokens):
    return " ".join(f"{b:02X}" for b in tokens)


# --------------------------------------------------------------------------
# Type table (grammar confirmed by strings in A8EE.exe: int1x7 int2x7 int3x7
# int5x7 int2x4 int3x4 int4x4 string; "Value size must be %02X")
# --------------------------------------------------------------------------
TYPE_RE = re.compile(r"int(\d)x(\d)")


def type_info(t: str):
    m = TYPE_RE.fullmatch(t)
    if m:
        n, bits = int(m.group(1)), int(m.group(2))
        return {"kind": "int", "bytes": n, "bits_per_byte": bits,
                "total_bits": n * bits}
    if t == "string":
        return {"kind": "string"}
    return {"kind": "unknown"}


# --------------------------------------------------------------------------
# Extraction
# --------------------------------------------------------------------------
def element_to_raw(e):
    """Faithful generic dump: ordered list of (tag, text|children, line)."""
    children = list(e)
    if not children:
        return (e.text or "")
    return [{"tag": c.tag, "line": line(c), "value": element_to_raw(c)} for c in children]


def extract_value(v):
    raw_addr = [a.text.strip() for a in v.findall("address")]
    t = txt(v, "type")
    d = {
        "name": txt(v, "name"),
        "type": t,
        "type_info": type_info(t),
        "address_raw": raw_addr[0] if raw_addr else None,
        "size_raw": txt(v, "size"),
        "range_raw": txt(v, "range"),
        "default_raw": (v.find("default").text if v.find("default") is not None else None),
        "numberTableRef": txt(v, "numberTableRef"),
        "line": line(v),
    }
    extra = [c.tag for c in v if c.tag not in (
        "name", "type", "address", "size", "range", "default", "numberTableRef")]
    if extra:
        d["unknown_tags"] = extra
    if len(raw_addr) > 1:
        d["address_raw_all"] = raw_addr
    tok = hex_tokens(d["address_raw"])
    d["offset"] = to_int7(tok) if tok is not None else None
    if has_invalid_7bit(tok):
        d["anomaly"] = (f"address byte > 0x7F in '{d['address_raw']}'; base-128 decode"
                        f" gives offset {fmt(from_int7(d['offset'], 2))}")
    stok = hex_tokens(d["size_raw"])
    d["size_bytes"] = to_int7(stok) if stok is not None else None
    if d["range_raw"]:
        lo, hi = (int(x) for x in d["range_raw"].split(","))
        d["range"] = [lo, hi]
    if d["default_raw"] is not None and d["default_raw"].strip().startswith("$"):
        d["default_macro"] = d["default_raw"].strip()  # filled from the referencing <struct>
    elif d["default_raw"] is not None and t != "string":
        d["default"] = int(d["default_raw"])
    elif t == "string":
        d["default"] = d["default_raw"]
    return d


def extract_struct_ref(s):
    return {
        "type": txt(s, "type"),
        "name": txt(s, "name"),
        "addresses_raw": [a.text.strip() for a in s.findall("address")],
        "size_raw": txt(s, "size"),
        "other": {c.tag: (c.text or "").strip() for c in s
                  if c.tag not in ("type", "name", "address", "size")},
        "line": line(s),
    }


def parse_table(text):
    """stringTable/numberTable: comma separated, whitespace/newline padded."""
    if text is None:
        return []
    items = [x.strip() for x in text.replace("\r", "").split(",")]
    return items


def main():
    text = SCRIPT.read_text(encoding="ascii")
    root = parse_with_lines(text)

    struct_types = {}
    order = []
    for st in root.findall("structType"):
        t = txt(st, "type")
        entry = {
            "type": t,
            "name_raw": txt(st, "name"),
            "address_raw": txt(st, "address"),
            "size_raw": txt(st, "size"),
            "line": line(st),
            "children": [],   # in document order
        }
        for c in st:
            if c.tag == "struct":
                entry["children"].append({"kind": "struct", **extract_struct_ref(c)})
            elif c.tag == "value":
                entry["children"].append({"kind": "value", **extract_value(c)})
            elif c.tag not in ("type", "name", "address", "size"):
                entry.setdefault("unknown_tags", []).append(c.tag)
        if t in struct_types:
            raise SystemExit(f"duplicate structType {t}")
        struct_types[t] = entry
        order.append(t)

    root_structs = [extract_struct_ref(s) for s in root.findall("struct")]

    midi = {tag: [{"line": line(e), "fields": [
        {"tag": c.tag, "text": (c.text or "").strip()} for c in e]}
        for e in root.findall(tag)] for tag in ("midiIn", "midiOut", "midiStruct")}

    string_tables = {txt(s, "name"): {"line": line(s), "items": parse_table(s.find("table").text)}
                     for s in root.findall("stringTable")}
    number_tables = {txt(s, "name"): {"line": line(s),
                                      "items": [int(x) for x in parse_table(s.find("table").text) if x]}
                     for s in root.findall("numberTable")}

    # ---------------- resolve absolute addresses by walking root structs ---
    params = []
    warnings = []
    carry_events = []

    def naive_add(a, b):
        """Byte-wise add with NO carry (what you'd get treating addresses as
        plain hex concatenation). Used only to check whether it matters."""
        a4 = [0] * (4 - len(a)) + a
        b4 = [0] * (4 - len(b)) + b
        return [x + y for x, y in zip(a4, b4)]

    def walk(type_name, path, base, naive, root_name):
        st = struct_types[type_name]
        for ch in st["children"]:
            if ch["kind"] == "struct":
                addrs = ch["addresses_raw"]
                if not addrs:
                    # view-state helper structs with no address: UI-only
                    warnings.append(f"{path}.{ch['name']}: struct without address (line {ch['line']})")
                    continue
                # ViewState children omit <name>; their structType has a fixed
                # <name> (e.g. 'control') instead of '$name'.
                base_name = ch["name"] or struct_types[ch["type"]]["name_raw"]
                for i, a in enumerate(addrs):
                    tok = hex_tokens(a)
                    cname = base_name if len(addrs) == 1 else f"{base_name}[{i}]"
                    walk(ch["type"], f"{path}.{cname}", base + to_int7(tok),
                         naive_add(naive, tok), root_name)
            else:
                if ch["offset"] is None:
                    warnings.append(f"{path}.{ch['name']}: value without address (line {ch['line']})")
                    continue
                abs_addr = base + ch["offset"]
                nv = naive_add(naive, hex_tokens(ch["address_raw"]))
                if nv != from_int7(abs_addr):
                    carry_events.append({"path": f"{path}.{ch['name']}",
                                         "naive": fmt(nv), "base128": fmt(from_int7(abs_addr))})
                params.append({
                    "path": f"{path}.{ch['name']}",
                    "root": root_name,
                    "structType": type_name,
                    "name": ch["name"],
                    "type": ch["type"],
                    "abs_address": fmt(from_int7(abs_addr)),
                    "abs_address_int7": abs_addr,
                    "size_bytes": ch["size_bytes"],
                    "range": ch.get("range"),
                    "default": ch.get("default"),
                    "numberTableRef": ch["numberTableRef"],
                    "line": ch["line"],
                    **({"anomaly": ch["anomaly"]} if "anomaly" in ch else {}),
                })

    for rs in root_structs:
        tok = hex_tokens(rs["addresses_raw"][0])
        walk(rs["type"], rs["name"], to_int7(tok), tok, rs["name"])

    # ---------------- effect unions (MFX / chorus / reverb) ----------------
    # <stringTable name="xxxValuePathTable">: DELIMITER-separated groups;
    # group N lists the value paths meaningful when xxxType == N. Group 0 is
    # the generic slot list (mfxParameter1..32 etc).
    unions = {}
    for key, struct_name, type_value in (("mfx", "PatchCommonMFX", "mfxType"),
                                         ("chorus", "PatchCommonChorus", "chorusType"),
                                         ("reverb", "PatchCommonReverb", "reverbType")):
        tname = f"{key}ValuePathTable"
        if tname not in string_tables:
            continue
        items = [x for x in string_tables[tname]["items"] if x]
        groups, cur = [], []
        for it in items:
            if it == "DELIMITER":
                groups.append(cur); cur = []
            else:
                cur.append(it)
        if cur:  # tables end with a trailing DELIMITER
            groups.append(cur)
        members_by_name = {c["name"]: c for c in struct_types[struct_name]["children"] if c["kind"] == "value"}
        type_val = members_by_name[type_value]
        out_groups = []
        for idx, g in enumerate(groups):
            mem = []
            for path in g:
                vname = path.split(".", 1)[1]
                v = members_by_name.get(vname)
                mem.append({"path": path, "name": vname,
                            "offset": fmt(from_int7(v["offset"], 2)) if v else None,
                            "found": v is not None})
            out_groups.append({"index": idx, "members": mem})
        unions[key] = {"struct": struct_name, "discriminator": type_value,
                       "discriminator_range": type_val.get("range"),
                       "path_table": tname, "path_table_line": string_tables[tname]["line"],
                       "groups": out_groups,
                       # '<effect>-<param>' members that no group lists (e.g. gm2Chorus-*)
                       "unlisted_members": sorted(
                           n for n in members_by_name
                           if "-" in n and n not in {m["name"] for g in out_groups for m in g["members"]}),
                       "note": f"groups[0] = generic slot list (valid for any {type_value}); "
                               f"groups[N], N>=1 = members meaningful when {type_value} == N. "
                               f"{type_value} 0 (THROUGH/OFF) has no type-specific members. "
                               "N<->type mapping verified by matching member-name prefixes to "
                               "the display names in A8EE.exe (e.g. group 1 'equalizer-*' = EQUALIZER)."}

    # MFX type display names: hard-coded in A8EE.exe (not in Script.xml).
    exe = ROOT / "original-roland-files" / "A8EE.exe"
    if exe.exists():
        blob = exe.read_bytes()[0xF8FC0:0xF9440]
        names = [s.decode("ascii") for s in blob.split(b"\x00") if s]
        names.reverse()  # stored last-to-first in the string pool
        unions.setdefault("mfx", {})["display_names"] = {
            "source": "original-roland-files/A8EE.exe bytes 0xF8FC0-0xF9440, reversed",
            "names": names}

    # ---------------- UI bindings: value -> display tables -----------------
    ui = defaultdict(lambda: {"stringTableRefs": set(), "offsetValues": set(),
                              "units": set(), "control_types": set(), "lines": []})
    # Panel macros each have exactly one concrete binding in Script.xml:
    #   <mfx>fm.pat.mfx</mfx> (l.19096), <chorusParam>fm.pat.cho</chorusParam>
    #   (l.17746), <reverbParam>fm.pat.rev</reverbParam> (l.18242),
    #   <valueRefP>fm.pat</valueRefP> (l.37067...)
    macro_bindings = {}
    for tag in ("mfx", "chorusParam", "reverbParam", "valueRefP"):
        concrete = {(e.text or "").strip() for e in root.iter(tag) if not (e.text or "").strip().startswith("$")}
        if len(concrete) == 1:
            macro_bindings["$" + tag] = concrete.pop()
    for c in root.iter("control"):
        vr = txt(c, "valueRef")
        if not vr:
            continue
        head, _, rest = vr.partition(".")
        if head in macro_bindings:
            vr = f"{macro_bindings[head]}.{rest}"
        key = re.sub(r"\[[^\]]*\]", "[]", vr)
        b = ui[key]
        if txt(c, "stringTableRef"):
            b["stringTableRefs"].add(txt(c, "stringTableRef"))
        if txt(c, "offsetValue"):
            b["offsetValues"].add(txt(c, "offsetValue"))
        if txt(c, "unit"):
            b["units"].add(txt(c, "unit"))
        b["control_types"].add(txt(c, "type"))
        b["lines"].append(line(c))
    ui_bindings = {k: {kk: sorted(vv) if isinstance(vv, set) else vv[:20]
                       for kk, vv in v.items()} for k, v in sorted(ui.items())}

    out = {
        "source": {"file": SRC_REL, "bytes": len(text.encode("ascii")),
                   "declared_encoding": "Shift_JIS", "actual_content": "ASCII only"},
        "notes": [
            "address_raw/size_raw are verbatim. Tokens are 7-bit bytes, MSB first,"
            " right-aligned (shorter strings have implied leading 00s).",
            "offset/size_bytes/abs_address_int7 decode those tokens base-128.",
            "Repeated <address> in a <struct> = array instances (e.g. 4 Tones).",
            "'$name', '$address', '$size' are macro placeholders filled by the"
            " referencing <struct> (A8EE.exe: 'Unable to resolve macros').",
            "ui_bindings are derived from <control> elements; they show how the"
            " Editor DISPLAYS a value, and are evidence, not hardware facts.",
        ],
        "root_structs": root_structs,
        "midi": midi,
        "structTypes": {k: struct_types[k] for k in order},
        "stringTables": string_tables,
        "numberTables": number_tables,
        "effect_unions": unions,
        "resolved_parameters": params,
        "resolve_warnings": warnings,
        "address_carry_events": carry_events,
        "ui_bindings": ui_bindings,
        "ui_macro_bindings": macro_bindings,
        "counts": {
            "structTypes": len(struct_types),
            "values": sum(1 for s in struct_types.values() for c in s["children"] if c["kind"] == "value"),
            "resolved_parameters": len(params),
            "stringTables": len(string_tables),
            "numberTables": len(number_tables),
        },
    }
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out["counts"]), f"warnings={len(warnings)}")


if __name__ == "__main__":
    sys.exit(main())
