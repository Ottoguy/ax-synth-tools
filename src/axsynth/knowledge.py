"""Access to the AX-Synth knowledge base (knowledge/knowledge.json).

The KB holds Roland's own explanations of every parameter and effect type
(Editor manual, plus Owner's Manual / MIDI Implementation where noted), each
linked to data-model paths. Source of truth: knowledge/*.toml; regenerate the
JSON with research/tools/build_knowledge.py.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KB_JSON = ROOT / "knowledge" / "knowledge.json"


def _norm(path: str) -> str:
    return re.sub(r"\[\d+\]", "[]", path)


@lru_cache(maxsize=1)
def load() -> dict:
    return json.loads(KB_JSON.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _index() -> dict[str, list[dict]]:
    """normalized data-model path -> KB entries (params and effect params) describing it."""
    idx: dict[str, list[dict]] = {}
    kb = load()
    for p in kb["params"]:
        for m in p.get("model", []):
            if m:
                idx.setdefault(m["path"], []).append({"kind": "param", "id": p["id"], "entry": p})
    for key in ("mfx", "chorus", "reverb"):
        for e in kb[key]:
            for p in e["params"]:
                for m in p["model"]:
                    if m:
                        idx.setdefault(m["path"], []).append(
                            {"kind": key, "number": e["number"], "type": e["name"], "entry": p})
    return idx


def describe(path: str) -> list[dict]:
    """KB entries for a data-model path, e.g. 'fm.pat.tone[2].tvfCutoffFrequency'
    or 'fm.pat.mfx.equalizer-loGain'. Empty list if undocumented (reserves)."""
    return _index().get(_norm(path), [])


def effect(kind: str, number: int) -> dict | None:
    """One effect type: kind in {'mfx', 'chorus', 'reverb'}."""
    return next((e for e in load()[kind] if e["number"] == number), None)


def concept(concept_id: str) -> dict | None:
    return next((c for c in load()["concepts"] if c["id"] == concept_id), None)


def param(param_id: str) -> dict | None:
    return next((p for p in load()["params"] if p["id"] == param_id), None)
