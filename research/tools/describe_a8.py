"""Human-readable description of .a8e/.a8l files, optionally diffed.

For every *active* value that differs from the script default (or from a
second file), prints raw value, enum label / display value, and default.
Display values use the ui-derived enum labels and offsetValue from
Script.xml, so they are marked as such.

Usage:
  python describe_a8.py A.a8e              non-default active values
  python describe_a8.py A.a8e B.a8e        values where A and B differ
  add --all to include values equal to the default
  A file may be FILE#N to pick patch N of an .a8l (0-based record) or of a
  .mid/.syx dump (User patch 0..255, or #temporary); default: the first.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "research" / "tools")]
import a8_files  # noqa: E402
from axsynth.schema import Schema  # noqa: E402

S = Schema.load()
PARAMS = {p.path: p for p in S.parameters(root=None)}


def display(path, value):
    p = PARAMS.get(path) or PARAMS.get("fm." + path)
    if p is None or not isinstance(value, int):
        return repr(value)
    if p.enum:
        vals = p.enum_values or list(range(p.range[0], p.range[0] + len(p.enum)))
        if value in vals:
            return f"{p.enum[vals.index(value)]!r}"
        return f"(outside enum {p.range})"
    if p.display_offset is not None:
        return f"{value + p.display_offset:+d}"
    return str(value)


def load(spec):
    path, _, sel = spec.partition("#")
    res = a8_files.parse(path, S)
    if res["format"] == "a8e":
        blocks = res["blocks"]
    elif res["format"] == "dump" and sel:
        key = sel if sel == "temporary" else int(sel)
        blocks = next(p for p in res["patches"] if p["slot"] == key)["blocks"]
    else:
        blocks = res["patches"][int(sel or 0)]["blocks"]
    return {v["path"].removeprefix("fm."): v for b in blocks for v in b["values"]}


def check_range(path, value):
    p = PARAMS.get("fm." + path) or PARAMS.get(path)
    if p and p.range and isinstance(value, int) and not p.range[0] <= value <= p.range[1]:
        return f"  !! OUTSIDE script range {p.range}"
    return ""


def main(argv):
    show_all = "--all" in argv
    files = [a for a in argv[1:] if not a.startswith("--")]
    a = load(files[0])
    b = load(files[1]) if len(files) > 1 else None
    for path, v in a.items():
        if not v["active"] and not (b and b[path]["active"]):
            continue
        if b is None:
            if v["is_default"] and not show_all:
                continue
            print(f"{path:48s} raw={v['value']!r:<14} shown={display(path, v['value']):<22}"
                  f" default={v['default']!r}{check_range(path, v['value'])}")
        else:
            w = b[path]
            if v["raw"] == w["raw"] and not show_all:
                continue
            print(f"{path:48s} A={v['value']!r:<8} {display(path, v['value']):<20}"
                  f" B={w['value']!r:<8} {display(path, w['value'])}")


if __name__ == "__main__":
    main(sys.argv)
