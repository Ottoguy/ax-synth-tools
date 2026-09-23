"""Export the generated parameter database for browsing.

Writes research/generated/parameters.json and parameters.csv from
axsynth.schema.Schema.parameters() (root 'fm' = the MIDI-addressable model,
plus 'cm' = the undocumented CommunicationModel).
"""
import csv
import dataclasses
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from axsynth.schema import Schema  # noqa: E402

s = Schema.load()
params = [p for p in s.parameters(root=None) if p.path.split(".")[0] in ("fm", "cm")]
rows = [dataclasses.asdict(p) for p in params]
out = ROOT / "research" / "generated"
(out / "parameters.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
cols = ["path", "address", "type", "size", "range", "default", "structure", "effect",
        "confidence", "display_offset", "enum", "enum_values", "description", "notes", "source"]
with open(out / "parameters.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(cols)
    for r in rows:
        w.writerow([json.dumps(r[c]) if isinstance(r[c], (list, dict, tuple)) else r[c] for c in cols])
print(len(rows), "parameters")
print("confidence:", Counter(r["confidence"] for r in rows))
print("union members:", sum(1 for r in rows if r["effect"]), "| with enum labels:",
      sum(1 for r in rows if r["enum"]), "| with display offset:", sum(1 for r in rows if r["display_offset"] is not None))
print("non-union fm params:", sum(1 for r in rows if r["path"].startswith("fm") and not r["effect"]))
