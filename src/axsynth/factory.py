"""Factory Tone list (Owner's Manual p.37-38), generated data access.

Source chain: docs/AX-Synth_OM.pdf -> research/tools/pdf2txt.py ->
research/tools/extract_tone_list.py -> research/generated/factory-tones.json

Terminology: the Owner's Manual calls a sound a "Tone" (8 families x 32
"variations"); the MIDI Implementation / Editor call the same object a
"Patch", whose four layers are *also* called Tones (Tone 1-4). Here,
FactoryTone = one whole patch.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "research" / "generated" / "factory-tones.json"


@dataclass(frozen=True)
class FactoryTone:
    group: str                 # family, "SuperNATURAL" or "SPECIAL"
    position: int              # 1-32 within family (1-8 for SN/SPECIAL)
    name: str                  # as printed; may differ slightly from the 12-char stored name
    cc00_msb: int
    cc32_lsb: int
    pc: int                    # 1-based, as printed
    editable: bool             # regular Tones only
    user_patch_index: int | None = None     # 0-255 [inferred mapping, see JSON note]
    librarian_slot: str | None = None       # "bank-number", e.g. "4-1"
    user_patch_address: str | None = None   # e.g. "30 60 00 00"


def _norm(s: str) -> str:
    return re.sub(r"[\s.]", "", s).lower()


@lru_cache(maxsize=1)
def tones() -> tuple[FactoryTone, ...]:
    raw = json.loads(DATA.read_text(encoding="utf-8"))["tones"]
    return tuple(FactoryTone(**{k: v for k, v in t.items() if k != "source_line"}) for t in raw)


def by_name(name: str) -> FactoryTone | None:
    """Match ignoring spaces, dots and case ('Vintage Org 1' is 13 chars as
    printed but patch names are 12)."""
    key = _norm(name)
    return next((t for t in tones() if _norm(t.name) == key), None)


def by_program(msb: int, lsb: int, pc0: int) -> FactoryTone | None:
    """Look up by bank select + 0-based program number (as stored in the
    Setup block: kbdPatchBankSelectMsb/Lsb, kbdPatchProgramNumber)."""
    return next((t for t in tones() if (t.cc00_msb, t.cc32_lsb, t.pc - 1) == (msb, lsb, pc0)), None)


def by_user_index(n: int) -> FactoryTone | None:
    return next((t for t in tones() if t.user_patch_index == n), None)


def families() -> list[str]:
    return list(dict.fromkeys(t.group for t in tones() if t.editable))
