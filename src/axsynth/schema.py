"""AX-Synth parameter model, generated from Roland's own Script.xml.

Source of truth chain:
    original-roland-files/Script/A8EE/Script.xml         (Roland, immutable)
      -> research/tools/extract_script_schema.py
      -> research/script-schema.json                      (generated)
      -> this module                                      (typed access)

Nothing here is hand-typed parameter data. Every Parameter carries the
Script.xml line it came from plus a confidence tag:

  "script+doc"   offset/encoding/range also match the official MIDI
                 Implementation (docs/AX Synth docs.pdf); see
                 research/generated/crosscheck-midi-implementation.md
  "script"       only in Script.xml (e.g. per-effect MFX parameter names,
                 the undocumented CommunicationModel at 0F 00 00 00)
  "ui-derived"   (on enum labels / display offsets only) inferred from how
                 the Editor's <control> elements display the value

Encoding (int<N>x<B>, confirmed by the official MIDI Implementation's
"nibbled" definition and by InitialData.a8e contents):
  N bytes, each carrying B low-order bits, most significant byte first.
  int1x7: 1 byte 0..127         int4x4: 4 nibbles, 0..65535
  int2x4: 2 nibbles, 0..255     int5x7: 5x7 bits (view-state only)
  string: 1 ASCII byte per char (32..127), space padded
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA = ROOT / "research" / "script-schema.json"
DEFAULT_CROSSCHECK = ROOT / "research" / "generated" / "crosscheck.json"
SCRIPT_FILE = "original-roland-files/Script/A8EE/Script.xml"

_TYPE = re.compile(r"int(\d)x(\d)")


# ---------------------------------------------------------------------------
# address helpers (Roland addresses: 7-bit bytes, MSB first)
# ---------------------------------------------------------------------------
def addr_to_int(a: str | bytes | list[int]) -> int:
    toks = a.split() if isinstance(a, str) else list(a)
    v = 0
    for t in toks:
        v = v * 128 + (int(t, 16) if isinstance(t, str) else t)
    return v


def int_to_addr(v: int, width: int = 4) -> bytes:
    out = []
    for _ in range(width):
        out.append(v & 0x7F)
        v >>= 7
    if v:
        raise ValueError("address overflow")
    return bytes(reversed(out))


def fmt_addr(b: bytes) -> str:
    return " ".join(f"{x:02X}" for x in b)


# ---------------------------------------------------------------------------
# value codec
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ValueDef:
    struct_type: str
    name: str
    type: str
    offset: int | None
    size: int
    range: tuple[int, int] | None
    default: int | str | None
    number_table: str | None
    line: int
    anomaly: str | None = None

    @property
    def bits(self) -> tuple[int, int] | None:
        m = _TYPE.fullmatch(self.type)
        return (int(m.group(1)), int(m.group(2))) if m else None


def decode_value(v: ValueDef, raw: bytes):
    if v.type == "string":
        return raw.decode("ascii")
    n, bits = v.bits
    if len(raw) != n:
        raise ValueError(f"{v.name}: expected {n} bytes, got {len(raw)}")
    mask = (1 << bits) - 1
    out = 0
    for b in raw:
        if b & ~mask:
            raise ValueError(f"{v.name}: byte {b:#04x} exceeds {bits} bits")
        out = (out << bits) | b
    return out


def encode_value(v: ValueDef, value, check_range: bool = True) -> bytes:
    """Wire bytes for one value. check_range=False reproduces stored data
    that lies outside the script's range (e.g. PatchCommon reserve1F = 0)."""
    if v.type == "string":
        s = str(value).ljust(v.size)[: v.size]
        if any(not 32 <= ord(c) <= 127 for c in s):
            raise ValueError(f"{v.name}: characters must be ASCII 32..127")
        return s.encode("ascii")
    n, bits = v.bits
    if check_range and v.range and not v.range[0] <= value <= v.range[1]:
        raise ValueError(f"{v.name}: {value} outside {v.range}")
    mask = (1 << bits) - 1
    if value >> (n * bits):
        raise ValueError(f"{v.name}: {value} does not fit {v.type}")
    return bytes((value >> (bits * (n - 1 - i))) & mask for i in range(n))


# ---------------------------------------------------------------------------
# parameter records
# ---------------------------------------------------------------------------
@dataclass
class Parameter:
    path: str                   # e.g. fm.pat.tone[2].tvfCutoffFrequency
    name: str
    structure: str              # structType
    address: str                # absolute, e.g. '1F 00 24 49'
    size: int
    type: str
    range: tuple[int, int] | None
    default: int | str | None
    source: dict                # {'file':..., 'line':...}
    confidence: str
    effect: str | None = None   # union member: e.g. 'mfx:EQUALIZER' (active when type==N)
    effect_index: int | None = None
    # ui-derived labels: enum[i] labels raw value enum_values[i] if given,
    # else raw value range[0] + i
    enum: list[str] | None = None
    enum_values: list[int] | None = None   # legal raw values (numberTable), if sparse
    display_offset: int | None = None      # ui-derived: shown value = raw + offset
    description: str | None = None         # official doc description, when matched
    notes: list[str] = field(default_factory=list)


class Schema:
    def __init__(self, data: dict, crosscheck: dict | None = None):
        self.data = data
        self.crosscheck = crosscheck or {}
        self._values = {
            t: [self._mk(t, c) for c in st["children"] if c["kind"] == "value"]
            for t, st in data["structTypes"].items()
        }

    @classmethod
    def load(cls, path: Path = DEFAULT_SCHEMA, crosscheck: Path = DEFAULT_CROSSCHECK):
        cc = json.loads(crosscheck.read_text(encoding="utf-8")) if crosscheck.exists() else None
        return cls(json.loads(path.read_text(encoding="utf-8")), cc)

    @staticmethod
    def _mk(stype, c) -> ValueDef:
        return ValueDef(stype, c["name"], c["type"], c["offset"], c["size_bytes"],
                        tuple(c["range"]) if c.get("range") else None,
                        c.get("default"), c.get("numberTableRef"), c["line"], c.get("anomaly"))

    # -- structure ---------------------------------------------------------
    def values(self, struct_type: str) -> list[ValueDef]:
        return self._values[struct_type]

    def value(self, struct_type: str, name: str) -> ValueDef:
        for v in self._values[struct_type]:
            if v.name == name:
                return v
        raise KeyError(f"{struct_type}.{name}")

    def struct_size(self, struct_type: str) -> int:
        """Byte size of a leaf struct (size field decoded base-128)."""
        return addr_to_int(self.data["structTypes"][struct_type]["size_raw"])

    def child_types(self, struct_type: str) -> dict[str, tuple[str, int]]:
        st = self.data["structTypes"][struct_type]
        return {c["name"]: (c["type"], len(c["addresses_raw"]))
                for c in st["children"] if c["kind"] == "struct"}

    def leaf_structs(self, root: str, _path=None, _type=None):
        """Depth-first (path, structType) of value-bearing structs under a root."""
        if _type is None:
            rs = next(r for r in self.data["root_structs"] if r["name"] == root)
            _type, _path = rs["type"], root
        st = self.data["structTypes"][_type]
        if any(c["kind"] == "value" for c in st["children"]):
            yield _path, _type
            return
        for c in st["children"]:
            if c["kind"] != "struct" or not c["addresses_raw"]:
                continue
            n = len(c["addresses_raw"])
            for i in range(n):
                p = f"{_path}.{c['name']}" + (f"[{i}]" if n > 1 else "")
                yield from self.leaf_structs(root, p, c["type"])

    # -- effect unions -------------------------------------------------------
    @cached_property
    def union_membership(self) -> dict[tuple[str, str], tuple[str, int, str]]:
        """(structType, value name) -> (union key, type index, label).

        MFX labels are the display names in A8EE.exe; chorus/reverb labels are
        the member-name prefix used in Script.xml (e.g. 'srvHall').
        """
        out = {}
        names = self.data["effect_unions"].get("mfx", {}).get("display_names", {}).get("names", [])
        for key, u in self.data["effect_unions"].items():
            if "groups" not in u:
                continue
            for g in u["groups"][1:]:
                i = g["index"]
                prefix = g["members"][0]["name"].split("-")[0] if g["members"] else None
                label = names[i] if key == "mfx" and i < len(names) else prefix
                for m in g["members"]:
                    out[(u["struct"], m["name"])] = (key, i, label)
        return out

    @cached_property
    def unreachable(self) -> set[tuple[str, str]]:
        """(structType, name) of effect members listed in no *ValuePathTable
        group (gm2Chorus-*, gm2Reverb-*): never meaningful on the AX-Synth."""
        return {(u["struct"], n) for u in self.data["effect_unions"].values()
                if "struct" in u for n in u.get("unlisted_members", [])}

    # -- parameter database -------------------------------------------------
    def parameters(self, root: str | None = "fm") -> list[Parameter]:
        ui = self.data["ui_bindings"]
        st_tables = self.data["stringTables"]
        num_tables = self.data["numberTables"]
        cc = self.crosscheck
        unreachable = self.unreachable
        out = []
        for p in self.data["resolved_parameters"]:
            if root and p["root"] != root:
                continue
            key = re.sub(r"\[\d+\]", "[]", p["path"])
            b = ui.get(key, {})
            um = self.union_membership.get((p["structType"], p["name"]))
            vd = self.value(p["structType"], p["name"])
            off_key = f"{p['structType']}:{vd.offset}"
            doc = cc.get(off_key)
            dead = (p["structType"], p["name"]) in unreachable
            if dead:
                doc = None  # shares a slot offset with a documented generic value; not itself documented
            conf = "script+doc" if doc and doc.get("status") == "match" and not um else "script"
            prm = Parameter(
                path=p["path"], name=p["name"], structure=p["structType"],
                address=p["abs_address"], size=p["size_bytes"], type=p["type"],
                range=tuple(p["range"]) if p["range"] else None, default=p["default"],
                source={"file": SCRIPT_FILE, "line": p["line"]}, confidence=conf,
                description=doc.get("desc") if doc and not um else None,
            )
            if um:
                prm.effect, prm.effect_index = f"{um[0]}:{um[2]}", um[1]
            if p.get("anomaly"):
                prm.notes.append(p["anomaly"])
            if dead:
                prm.notes.append("unreachable: in no *ValuePathTable group; outside effect-type range")
            if doc and doc.get("status") != "match" and not um:
                prm.notes.append(f"doc cross-check: {doc.get('status')}")
            # unresolved macros such as '$table' are skipped, not guessed
            refs = [r for r in (b.get("stringTableRefs") or []) if r in st_tables]
            if len(refs) == 1 and prm.range:
                items = [x for x in st_tables[refs[0]]["items"] if x != ""]
                lo, hi = prm.range
                if p.get("numberTableRef"):
                    prm.enum_values = num_tables[p["numberTableRef"]]["items"]
                    prm.enum = items[: len(prm.enum_values)]
                elif len(items) == hi - lo + 1:
                    prm.enum = items
                elif len(items) > hi:
                    prm.enum = items[lo: hi + 1]
                if prm.enum is not None:
                    prm.notes.append(f"enum labels ui-derived from stringTable {refs[0]}")
            offs = b.get("offsetValues") or []
            if len(offs) == 1 and offs[0].lstrip("-").isdigit():
                prm.display_offset = int(offs[0])
            out.append(prm)
        return out
