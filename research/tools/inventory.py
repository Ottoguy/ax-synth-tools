"""Inventory of original-roland-files/ (read-only): size, sha256, text/binary,
magic bytes. Writes research/generated/inventory.json."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "original-roland-files"
rows = []
for p in sorted(BASE.rglob("*")):
    if not p.is_file():
        continue
    b = p.read_bytes()
    nontext = sum(1 for x in b[:4096] if x < 9 or 13 < x < 32 or x > 126)
    rows.append({"path": p.relative_to(ROOT).as_posix(), "ext": p.suffix.lower(), "size": len(b),
                 "sha256": hashlib.sha256(b).hexdigest(),
                 "kind": "text" if nontext == 0 else "binary",
                 "magic": b[:16].hex(" ")})
(ROOT / "research/generated/inventory.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
from collections import Counter
print(len(rows), "files;", Counter(r["ext"] for r in rows))
for r in rows:
    if r["ext"] != ".bmp":
        print(f'{r["path"]:60s} {r["size"]:>9} {r["kind"]:6s} {r["magic"][:23]}  {r["sha256"][:12]}')
bmps = [r for r in rows if r["ext"] == ".bmp"]
print("bmp total bytes", sum(r["size"] for r in bmps), "all start with BM:", all(r["magic"].startswith("42 4d") for r in bmps))
