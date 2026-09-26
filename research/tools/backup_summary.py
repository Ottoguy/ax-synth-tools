"""Summarize a whole-synth backup (256 User patches) against the factory list.

Input : a Librarian "Export SMF" .mid or a .syx of whole-block DT1s
        (default: the newest captures/backup/ax-synth-backup-*.mid)
Output: research/generated/user-patches.json and user-patches.csv

Per User patch n: Librarian slot, factory family, printed factory name
(Owner's Manual), stored 12-character name, whether they match, patch
category, and per Tone (layer 1-4): switch, wave number + wave name
(internalWaveNameTableA[N-1]), coarse tune; plus MFX/chorus/reverb type.
Values come from the decoded blocks, not from hand-typed data.

Usage:
  py -3 research/tools/backup_summary.py [backup.mid] [--quiet]
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from axsynth import factory, sysex  # noqa: E402
from axsynth.schema import Schema, decode_value  # noqa: E402

OUT = ROOT / "research/generated"


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def names_match(printed, stored):
    """Stored names are 12 characters; the printed list can be longer
    ("Vintage Org 1") or differ in spacing/punctuation."""
    p, s = norm(printed), norm(stored)
    return p == s or (len(printed) > 12 and p.startswith(s))


def summarize(path, schema=None):
    S = schema or Schema.load()
    buf = Path(path).read_bytes()
    msgs = sysex.smf_sysex(buf) if buf[:4] == b"MThd" else sysex.split_sysex(buf)
    patches = sysex.patch_blocks(msgs)
    raw = json.loads((ROOT / "research/script-schema.json").read_text(encoding="utf-8"))
    waves = [w.strip() for w in raw["stringTables"]["internalWaveNameTableA"]["items"]]
    kb = json.loads((ROOT / "knowledge/knowledge.json").read_text(encoding="utf-8"))
    mfx_names = {m["number"]: m["name"] for m in kb["mfx"]}
    child = S.child_types("Patch")

    def val(blocks, block, name):
        stype = child[block.split("[")[0]][0]
        v = S.value(stype, name)
        return decode_value(v, blocks[block][v.offset:v.offset + v.size])

    rows = []
    for n in range(256):
        b = patches.get(n)
        t = factory.by_user_index(n)
        if b is None or len(b) != len(sysex.PATCH_BLOCKS):
            rows.append({"user_patch": n, "librarian_slot": t.librarian_slot, "complete": False})
            continue
        stored = val(b, "common", "patchName")
        row = {"user_patch": n, "librarian_slot": t.librarian_slot, "complete": True,
               "family": t.group, "factory_name": t.name, "stored_name": stored.rstrip(),
               "name_matches_factory": names_match(t.name, stored),
               "category": val(b, "common", "patchCategory"),
               "mfx_type": val(b, "mfx", "mfxType"),
               "mfx_name": mfx_names.get(val(b, "mfx", "mfxType"), "THROUGH"),
               "chorus_type": val(b, "cho", "chorusType"),
               "reverb_type": val(b, "rev", "reverbType"), "tones": []}
        for i in range(4):
            w = val(b, f"tone[{i}]", "waveNumberL")
            row["tones"].append({
                "on": bool(val(b, "tmt", f"tmtToneSwitch[{i}]")),
                "wave": w, "wave_name": waves[w - 1] if 1 <= w <= len(waves) else None,
                "coarse_tune": val(b, f"tone[{i}]", "toneCoarseTune") - 64})
        rows.append(row)
    return rows


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    src = Path(args[0]) if args else sorted((ROOT / "captures/backup").glob("ax-synth-backup-*.mid"))[-1]
    rows = summarize(src)
    meta = {"source": src.relative_to(ROOT).as_posix() if src.is_relative_to(ROOT) else str(src),
            "patches": len(rows), "complete": sum(r["complete"] for r in rows),
            "names_matching_factory": sum(r.get("name_matches_factory", False) for r in rows),
            "wave_name_rule": "wave N = internalWaveNameTableA[N-1] (Script.xml)"}
    (OUT / "user-patches.json").write_text(json.dumps({"meta": meta, "patches": rows}, indent=1),
                                           encoding="utf-8")
    with open(OUT / "user-patches.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["user_patch", "librarian_slot", "family", "factory_name", "stored_name",
                    "name_matches_factory", "category", "mfx", "chorus_type", "reverb_type"]
                   + [f"tone{i + 1}" for i in range(4)])
        for r in rows:
            if not r["complete"]:
                w.writerow([r["user_patch"], r["librarian_slot"]] + [""] * 12)
                continue
            w.writerow([r["user_patch"], r["librarian_slot"], r["family"], r["factory_name"],
                        r["stored_name"], r["name_matches_factory"], r["category"],
                        f"{r['mfx_type']}:{r['mfx_name']}", r["chorus_type"], r["reverb_type"]]
                       + [f"{'on' if t['on'] else 'off'} {t['wave']}:{t['wave_name']} {t['coarse_tune']:+d}"
                          for t in r["tones"]])
    if "--quiet" not in argv:
        print(json.dumps(meta, indent=1))
        for r in rows:
            if r["complete"] and not r["name_matches_factory"]:
                print(f"  name differs: {r['user_patch']} ({r['librarian_slot']}) printed "
                      f"{r['factory_name']!r} stored {r['stored_name']!r}")


if __name__ == "__main__":
    main(sys.argv)
