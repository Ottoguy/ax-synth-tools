"""Decode the AX-Synth's own Bulk Dump (Owner's Manual p.29: power-on with
VARIATION [-]+[+]+TONE [6], then FAVORITE [B] "Snd").

Findings (captures/bulkdump/, research/bulkdump-analysis.md):

  Wire format [F]
    F0 41 dev 7F 12 a3 a2 a1 a0 <data> sum F7     (1-byte model ID 7F, DT1)
    sum = Roland checksum over address + data. Address = 8-bit byte offset
    in base-128. Data = 7-in-8 packing: each 8-byte group is one byte of
    high bits (bit j -> data byte j) followed by 7 low-7-bit bytes.
    First message (dev 11): header, whose packed payload holds the image
    length (0x1A0040). Then 131-byte messages of 120 data bytes = 105 image
    bytes each, addresses in steps of 105, and a text trailer
    "Roland RE409DUMP VER.1.00-BLD.00009 ...".

  Image (1,704,000 bytes) [F]
    0x000000  system area: "00 1A 00 10" + "Roland 9S409D" + 3 bytes, bit-packed
              System data (System Common at bit 101 after 0x14), signature
              again at 0x46A
    0x020000  patch area: FF FF FF FF + "Roland 9S409D" + 3 bytes
    0x020014  16 FAVORITE entries x 40 bits: MSB(8) LSB(7) PC(7) volume(7)
              reverb send(7) pad(4)
    0x020064  256 User patch records x 664 bytes (5,312 bits), bit-packed,
              fields in Script.xml order (see `solve`)
    0x049864  signature; the rest is erased flash (FF)

  Patch record: every data-model value (effect-union members excluded:
  they are the generic slots) at the smallest width for its range, MSB
  first. Unsigned values are stored as-is; values centred on 64 are stored
  offset-binary (v - (64 - 2^(w-1))). The layout is *derived* from the
  user's backup (solve) and saved to research/generated/bulkdump-layout.json.

Usage:
  py -3 research/tools/bulkdump.py info   <dump.syx>
  py -3 research/tools/bulkdump.py solve  <dump.syx> <backup.mid>
  py -3 research/tools/bulkdump.py verify <dump.syx> <backup.mid>
  py -3 research/tools/bulkdump.py export <dump.syx> <out.syx>
      (256 User patches as whole-block DT1s to 30 nn ..., like a Librarian
       export. A RESTORE file: never send it unless restoring on purpose.)
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from axsynth import factory, sysex  # noqa: E402
from axsynth.schema import Schema, decode_value, encode_value  # noqa: E402

LAYOUT = ROOT / "research/generated/bulkdump-layout.json"
MODEL = 0x7F
SIGNATURE = b"Roland 9S409D"
PATCH_AREA = 0x20000
FAVORITES = 0x20014
RECORDS = 0x20064
RECORD_BYTES = 664
TONE_STRIDE = 792   # bits between Tone 1..4 fields
SYSTEM_COMMON_BIT = 101  # after image offset 0x14


def a7(b: bytes) -> int:
    v = 0
    for x in b:
        v = v * 128 + x
    return v


def unpack78(p: bytes) -> bytes:
    out = bytearray()
    for i in range(0, len(p), 8):
        msb, g = p[i], p[i + 1:i + 8]
        out += bytes(b | (((msb >> j) & 1) << 7) for j, b in enumerate(g))
    return bytes(out)


def read_dump(path) -> dict:
    msgs = sysex.split_sysex(Path(path).read_bytes())
    bad = [i for i, m in enumerate(msgs)
           if m[1] != sysex.ROLAND or m[3] != MODEL or m[4] != sysex.DT1 or sysex.checksum(m[5:-2]) != m[-2]]
    header, body = msgs[0], msgs[1:]
    image = bytearray()
    gaps = []
    for m in body:
        addr = a7(m[5:9])
        if addr != len(image):
            gaps.append((len(image), addr))
        data = unpack78(m[9:-2])
        image[addr:addr + len(data)] = data
    hdr = unpack78(header[9:-2])
    return {"messages": len(msgs), "bad": bad, "header_device": header[2], "header": hdr,
            "declared_length": int.from_bytes(hdr[4:8], "big"), "image": bytes(image), "gaps": gaps}


def trailer(image: bytes) -> str:
    i = image.rfind(b"Roland RE")
    return image[i:].split(b"\x00")[0].decode("ascii", "replace") if i >= 0 else ""


class Bits:
    def __init__(self, data: bytes):
        self.n = len(data) * 8
        self.v = int.from_bytes(data, "big")

    def get(self, pos: int, width: int) -> int:
        return (self.v >> (self.n - pos - width)) & ((1 << width) - 1)


def favorites(image: bytes) -> list[dict]:
    b = Bits(image[FAVORITES:FAVORITES + 80])
    out = []
    for k in range(16):
        o = 40 * k
        msb, lsb, pc = b.get(o, 8), b.get(o + 8, 7), b.get(o + 15, 7)
        t = factory.by_program(msb, lsb, pc)
        out.append({"memory": f"{'AB'[k // 8]}{k % 8 + 1}", "bank_msb": msb, "bank_lsb": lsb, "pc": pc,
                    "tone": t.name if t else None, "volume": b.get(o + 22, 7),
                    "reverb_send": b.get(o + 29, 7), "pad": b.get(o + 36, 4)})
    return out


def records(image: bytes) -> list[Bits]:
    return [Bits(image[RECORDS + n * RECORD_BYTES:RECORDS + (n + 1) * RECORD_BYTES]) for n in range(256)]


def fields(S: Schema):
    """(block, name, index, ValueDef) for every stored value, Script.xml order;
    strings split into characters."""
    child = S.child_types("Patch")
    for block, _ in sysex.PATCH_BLOCKS:
        st = child[block.split("[")[0]][0]
        for v in S.values(st):
            if v.offset is None or (st, v.name) in S.union_membership or (st, v.name) in S.unreachable:
                continue
            if v.type == "string":
                for i in range(v.size):
                    yield block, v.name, i, v
            else:
                yield block, v.name, None, v


def truth(pb, block, v, idx, n):
    raw = pb[n][block][v.offset:v.offset + v.size]
    return raw[idx] if idx is not None else decode_value(v, raw)


def solve(image: bytes, backup_path) -> list[dict]:
    S = Schema.load()
    recs = records(image)
    pb = sysex.patch_blocks(sysex.smf_sysex(Path(backup_path).read_bytes()))
    flist = list(fields(S))
    layout, pos, tone_base = [], 0, None
    tone_rel = {}
    for block, name, idx, v in flist:
        tone = int(block[5]) if block.startswith("tone[") else None
        if tone is not None and tone > 0:     # reuse Tone 1's layout, shifted
            rel = tone_rel[name]
            layout.append({**rel, "block": block, "pos": rel["pos"] + TONE_STRIDE * tone})
            continue
        lo, hi = (32, 127) if v.type == "string" else v.range
        wr = max(1, math.ceil(math.log2(hi - lo + 1)))
        if tone == 0:
            samples = [(recs[n], t, truth(pb, f"tone[{t}]", v, idx, n)) for n in range(256) for t in range(4)]
        else:
            samples = [(recs[n], 0, truth(pb, block, v, idx, n)) for n in range(256)]
        const = len({s[2] for s in samples}) == 1
        pref = [(wr, off) for off in (0, 64 - 2 ** (wr - 1), 32768 - 2 ** (wr - 1))]
        other = [(w, off) for w in range(1, 17) for off in (0, 64 - 2 ** (w - 1), 32768 - 2 ** (w - 1))]
        found = None
        for group in (pref, other):
            for skip in range(25):
                for w, off in group:
                    if all(r.get(pos + skip + TONE_STRIDE * t, w) == val - off for r, t, val in samples):
                        found = (skip, w, off)
                        break
                if found:
                    break
            if found:
                break
        if not found:
            raise SystemExit(f"no match for {block}.{name} at bit {pos}")
        skip, w, off = found
        e = {"block": block, "name": name, "index": idx, "pos": pos + skip, "width": w, "offset": off,
             "skip": skip, "range_width": wr, "verified": not const}
        layout.append(e)
        if tone == 0:
            tone_rel[name if idx is None else f"{name}[{idx}]"] = e
            tone_rel[name] = e
        pos += skip + w
    return layout


def decode_patch(rec: Bits, layout, S: Schema) -> dict[str, bytes]:
    child = S.child_types("Patch")
    blocks = {b: bytearray(S.struct_size(child[b.split("[")[0]][0])) for b, _ in sysex.PATCH_BLOCKS}
    for e in layout:
        st = child[e["block"].split("[")[0]][0]
        v = S.value(st, e["name"])
        val = rec.get(e["pos"], e["width"]) + e["offset"]
        if e["index"] is not None:
            blocks[e["block"]][v.offset + e["index"]] = val
        else:
            blocks[e["block"]][v.offset:v.offset + v.size] = encode_value(v, val, check_range=False)
    return {k: bytes(b) for k, b in blocks.items()}


def system_common(image: bytes) -> dict:
    """The documented System Common values at their packed positions [F for
    the values that match the synth's READ reply; gap fields unknown]."""
    b = Bits(image[0x14:0x46A])
    p = SYSTEM_COMMON_BIT
    out = {"masterTune": b.get(p, 11), "masterKeyShift": b.get(p + 11, 6) + 32,
           "masterLevel": b.get(p + 17, 7), "scaleTuneSwitch": b.get(p + 24, 1),
           "hidden_bits_126_140": format(b.get(p + 25, 15), "015b"),
           "scaleTunes": [b.get(p + 40 + 7 * i, 7) for i in range(12)]}
    return out


def main(argv):
    cmd, dump = argv[1], read_dump(argv[2])
    img = dump["image"]
    if cmd == "info":
        print(f"messages={dump['messages']} bad={len(dump['bad'])} gaps={dump['gaps'][:3]} "
              f"image={len(img)} declared={dump['declared_length']} header_dev={dump['header_device']:02X}")
        print("trailer:", trailer(img))
        print("signatures at", [hex(i) for i in range(len(img)) if img.startswith(SIGNATURE, i)])
        print("system common:", system_common(img))
        for f in favorites(img):
            print("favorite", f)
        recs = records(img)
        names = ["".join(chr(r.get(7 * i, 7)) for i in range(12)) for r in recs]
        print("patch names:", names[:4], "...", names[-2:])
        return
    if cmd == "solve":
        layout = solve(img, argv[3])
        LAYOUT.write_text(json.dumps({"source": "research/tools/bulkdump.py solve", "record_bits": RECORD_BYTES * 8,
                                      "tone_stride_bits": TONE_STRIDE, "fields": layout}, indent=0),
                          encoding="utf-8")
        ver = sum(e["verified"] for e in layout)
        end = max(e["pos"] + e["width"] for e in layout)
        print(f"{len(layout)} fields, {ver} verified by varying data, last bit {end} of {RECORD_BYTES * 8}")
        return
    S = Schema.load()
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))["fields"]
    patches = [decode_patch(r, layout, S) for r in records(img)]
    if cmd == "verify":
        pb = sysex.patch_blocks(sysex.smf_sysex(Path(argv[3]).read_bytes()))
        bad = [(n, b) for n in range(256) for b in pb[n] if patches[n][b] != pb[n][b]]
        print(f"256 patches, {len(bad)} blocks differ from the backup", bad[:10])
    elif cmd == "export":
        out = b"".join(m for n in range(256)
                       for m in sysex.patch_messages(patches[n], sysex.user_patch_address(n)))
        Path(argv[3]).write_bytes(out)
        print("wrote", argv[3], len(out), "bytes")


if __name__ == "__main__":
    main(sys.argv)
