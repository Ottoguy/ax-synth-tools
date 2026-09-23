"""Extract the factory Tone list (Owner's Manual p.37-38) to JSON/CSV.

Input : research/generated/owners-manual.pdf.txt  (pdf2txt.py of docs/AX-Synth_OM.pdf)
Output: research/generated/factory-tones.json, factory-tones.csv

Per Tone: group (family / SuperNATURAL / SPECIAL), position in group,
name, CC00 (bank MSB), CC32 (bank LSB), PC (1-based, as printed), plus for
regular Tones the derived User-patch index/address.

Derivation [inference, strong]: the Owner's Manual has 256 regular Tones in
8 families x 32, and the Librarian manual says the 256 patches are 'Bank (1-8)'
x 'Number (1-32)' of the Patch Area (30 00 00 00 + n*00 01 00 00). The PCs
are sequential across families (LSB 0: PC 1-128, LSB 1: PC 1-128), so
n = LSB*128 + PC-1 and family = n // 32. To be confirmed by a Librarian
'Read All Data' (names in slot n should equal this list).
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from axsynth import sysex  # noqa: E402
from axsynth.schema import fmt_addr, int_to_addr  # noqa: E402

SRC = ROOT / "research/generated/owners-manual.pdf.txt"
lines = SRC.read_text(encoding="utf-8").splitlines()
start = next(i for i, l in enumerate(lines) if l.strip() == "Tone list")
end = next(i for i, l in enumerate(lines) if i > start and "12. Specifications" in l)

HEADER = re.compile(r"^(.*?)\s*CC00 CC32 PC$")
ENTRY = re.compile(r"^(\d+) (.+?)\s+(\d+) (\d+) (\d+)$")

tones, group, position_groups = [], None, iter(["SuperNATURAL", "SPECIAL"])
for i in range(start, end):
    l = lines[i].strip()
    m = HEADER.match(l)
    if m:
        group = m.group(1)
        if group == "Position Tone":
            group = next(position_groups)
        continue
    m = ENTRY.match(l)
    if m and group:
        pos, name, msb, lsb, pc = m.group(1), m.group(2).strip(), *map(int, m.group(3, 4, 5))
        t = {"group": group, "position": int(pos), "name": name,
             "cc00_msb": msb, "cc32_lsb": lsb, "pc": pc, "source_line": i + 1}
        if msb == 87 and lsb in (0, 1):
            n = lsb * 128 + pc - 1
            t.update(user_patch_index=n, librarian_slot=f"{n // 32 + 1}-{n % 32 + 1}",
                     user_patch_address=fmt_addr(int_to_addr(sysex.user_patch_address(n))),
                     editable=True)
        else:
            t["editable"] = False  # SuperNATURAL / SPECIAL: not in the patch area
        tones.append(t)

out = ROOT / "research/generated"
(out / "factory-tones.json").write_text(json.dumps(
    {"source": "docs/AX-Synth_OM.pdf p.37-38 via research/generated/owners-manual.pdf.txt",
     "note": __doc__.split("Derivation", 1)[1].strip(), "tones": tones}, indent=1), encoding="utf-8")
with open(out / "factory-tones.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["group", "position", "name", "cc00_msb", "cc32_lsb", "pc",
                                      "user_patch_index", "librarian_slot", "user_patch_address",
                                      "editable", "source_line"])
    w.writeheader()
    w.writerows(tones)

from collections import Counter
print(len(tones), "tones;", dict(Counter(t["group"] for t in tones)))
reg = [t for t in tones if t.get("editable")]
print("regular:", len(reg), "indices contiguous:", sorted(t["user_patch_index"] for t in reg) == list(range(256)))
print("family == index//32:", all(
    list(dict.fromkeys(x["group"] for x in reg)).index(t["group"]) == t["user_patch_index"] // 32 for t in reg))
print("max name length:", max(len(t["name"]) for t in tones))
