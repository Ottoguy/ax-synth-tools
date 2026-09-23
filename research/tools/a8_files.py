"""Read-only parser for AX-Synth Editor (.a8e) and Librarian (.a8l) files.

Layouts below were inferred from InitialData.a8e / InitialData.a8l and the
struct sizes in Script.xml; see research/initialdata-analysis.md.

  .a8e  (magic 'KoaDataFile00001')
    0x000  16  magic
    0x010  64  root struct name, space padded   ('fm')
    0x050  16  model name, space padded         ('AX-Synth')
    0x060 160  zero
    0x100      raw images of every leaf struct under 'fm', depth-first in
               Script.xml order, each exactly <size> bytes (7-bit / nibble
               encoded, i.e. the same bytes a DT1 would carry)

  .a8l  (magic 'A8ELibrarianFile0000', space padded to 32)
    0x020  u32be  patch count
    0x024  ...    zero up to 0xA0
    0x0A0  per patch:  u32be record length (bytes after this field), then
                       for each Patch child struct (common, mfx, cho, rev,
                       tmt, tone):
                         u32be instance count
                         count x ( u32be instance size, <size> bytes )
                       then 4 unexplained bytes (00 00 00 00 in the only
                       sample) that are still inside the record length

Usage:
  python a8_files.py <file>            summary + non-default values
  python a8_files.py <file> --all      every value
  python a8_files.py <file> --json     machine-readable dump
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from axsynth.schema import Schema, decode_value  # noqa: E402


def leaf_blocks(schema: Schema, root: str):
    """Depth-first (path, structType) for leaf structs below a root struct."""
    return list(schema.leaf_structs(root))


DISCRIMINATOR = {"PatchCommonMFX": "mfxType", "PatchCommonChorus": "chorusType",
                 "PatchCommonReverb": "reverbType"}


def decode_block(schema: Schema, stype: str, data: bytes, path: str):
    """Decode every value of one struct image.

    Effect-union members (e.g. 'equalizer-loGain') overlay the generic slots;
    only those belonging to the currently selected effect type are 'active'.
    """
    active_type = None
    if stype in DISCRIMINATOR:
        d = schema.value(stype, DISCRIMINATOR[stype])
        active_type = decode_value(d, data[d.offset:d.offset + d.size])
    out = []
    for v in schema.values(stype):
        if v.offset is None:
            continue
        raw = data[v.offset:v.offset + v.size]
        um = schema.union_membership.get((stype, v.name))
        active = (um is None or um[1] == active_type) and (stype, v.name) not in schema.unreachable
        val = decode_value(v, raw)
        out.append({"path": f"{path}.{v.name}", "raw": raw.hex(" ").upper(),
                    "value": val, "default": v.default, "active": active,
                    "is_default": val == v.default or not active})
    return out


def parse_a8e(buf: bytes, schema: Schema):
    assert buf[:16] == b"KoaDataFile00001", "not a Koa data file"
    hdr = {"magic": buf[:16].decode(), "root": buf[16:80].decode().rstrip(),
           "model": buf[80:96].decode().rstrip(),
           "reserved_all_zero": not any(buf[96:256])}
    pos = 0x100
    blocks = []
    for path, stype in leaf_blocks(schema, hdr["root"]):
        size = schema.struct_size(stype)
        blocks.append({"path": path, "type": stype, "file_offset": pos, "size": size,
                       "values": decode_block(schema, stype, buf[pos:pos + size], path)})
        pos += size
    return {"format": "a8e", "header": hdr, "blocks": blocks,
            "bytes_consumed": pos, "file_size": len(buf), "trailing": buf[pos:].hex(" ")}


PATCH_ORDER = ["common", "mfx", "cho", "rev", "tmt", "tone"]


def parse_a8l(buf: bytes, schema: Schema):
    magic = buf[:32]
    assert magic.startswith(b"A8ELibrarianFile"), "not an AX-Synth Librarian file"
    count = struct.unpack(">I", buf[32:36])[0]
    hdr = {"magic": magic.decode().rstrip(), "patch_count": count,
           "reserved_all_zero": not any(buf[36:0xA0])}
    pos = 0xA0
    patches = []
    patch_type = schema.child_types("Patch")  # name -> (structType, n_instances)
    for pi in range(count):
        rec_len = struct.unpack(">I", buf[pos:pos + 4])[0]
        start = pos
        pos += 4
        blocks = []
        for name in PATCH_ORDER:
            n = struct.unpack(">I", buf[pos:pos + 4])[0]
            pos += 4
            stype, exp_n = patch_type[name]
            exp_sz = schema.struct_size(stype)
            for i in range(n):
                sz = struct.unpack(">I", buf[pos:pos + 4])[0]  # per-instance size prefix
                pos += 4
                data = buf[pos:pos + sz]
                path = f"pat.{name}" + (f"[{i}]" if exp_n > 1 else "")
                blocks.append({"path": path, "type": stype, "file_offset": pos, "size": sz,
                               "count_ok": n == exp_n, "size_ok": sz == exp_sz,
                               "values": decode_block(schema, stype, data, path)})
                pos += sz
        # InitialData.a8l has 4 more bytes (00 00 00 00) inside the record
        # length after the tone blocks. Meaning unknown (candidate: count of
        # Librarian-only memo fields). Reported, not interpreted.
        rec_end = start + 4 + rec_len
        tail = buf[pos:rec_end]
        patches.append({"record_offset": start, "record_length": rec_len,
                        "structured_bytes": pos - start - 4,
                        "unexplained_record_tail": tail.hex(" ").upper(), "blocks": blocks})
        pos = rec_end
    return {"format": "a8l", "header": hdr, "patches": patches,
            "bytes_consumed": pos, "file_size": len(buf),
            "trailing": buf[pos:].hex(" ").upper()}


def parse(path: str | Path, schema: Schema | None = None):
    schema = schema or Schema.load()
    buf = Path(path).read_bytes()
    if buf.startswith(b"KoaDataFile"):
        return parse_a8e(buf, schema)
    if buf.startswith(b"A8ELibrarianFile"):
        return parse_a8l(buf, schema)
    raise ValueError("unknown file type")


def _blocks(res):
    if res["format"] == "a8e":
        yield from res["blocks"]
    else:
        for p in res["patches"]:
            yield from p["blocks"]


def main(argv):
    res = parse(argv[1])
    if "--json" in argv:
        print(json.dumps(res, indent=1))
        return
    print(json.dumps(res["header"]))
    print(f"file_size={res['file_size']} consumed={res['bytes_consumed']} trailing={res['trailing']!r}")
    if res["format"] == "a8l":
        for p in res["patches"]:
            print(f"patch record @0x{p['record_offset']:X}: length field={p['record_length']}"
                  f" structured bytes={p['structured_bytes']}"
                  f" unexplained tail={p['unexplained_record_tail']!r}")
    show_all = "--all" in argv
    for b in _blocks(res):
        flags = "" if b.get("count_ok", True) and b.get("size_ok", True) else "  !! count/size mismatch"
        nd = [v for v in b["values"] if not v["is_default"]]
        print(f"\n[{b['path']}] {b['type']} @0x{b['file_offset']:X} size={b['size']}"
              f" non-default={len(nd)}{flags}")
        for v in (b["values"] if show_all else nd):
            print(f"   {v['path']:55s} raw={v['raw']:12s} value={v['value']!r} default={v['default']!r}")


if __name__ == "__main__":
    main(sys.argv)
