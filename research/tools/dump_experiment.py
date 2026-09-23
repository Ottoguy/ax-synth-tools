"""Experiment support: generate read-only RQ1 requests and decode DT1 replies.

This tool never opens a MIDI port. It writes/reads files only.

  python dump_experiment.py make-requests out.syx
      Writes one RQ1 per Temporary-Patch block (common, mfx, cho, rev, tmt,
      tone 1-4) plus System Controller with the doc's size 0x50, to test the
      4F-vs-50 discrepancy. RQ1 only asks the synth to reply; it changes no
      synth memory.

  python dump_experiment.py decode reply.syx|export.mid
      Parses DT1 messages (raw .syx, or an SMF written by the Editor/Librarian
      "Export SMF"), checks checksums and model ID, assembles an address->byte
      map and decodes every known parameter with our schema.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from axsynth import sysex  # noqa: E402
from axsynth.schema import Schema, addr_to_int, decode_value, fmt_addr, int_to_addr  # noqa: E402

S = Schema.load()


def requests():
    out = []
    for path, stype in S.leaf_structs("fm"):
        if not path.startswith("fm.pat"):
            continue
        first = next(p for p in S.parameters() if p.path.startswith(path + "."))
        base = addr_to_int(first.address) - S.value(stype, first.name).offset
        out.append((path, base, S.struct_size(stype)))
    out.append(("fm.system.controller (doc size 0x50)", addr_to_int("02 00 40 00"), 0x50))
    return out


def make_requests(dest):
    blob = b""
    for label, base, size in requests():
        m = sysex.build_rq1(base, size)
        blob += m
        print(f"{label:40s} {m.hex(' ').upper()}")
    Path(dest).write_bytes(blob)
    print(f"wrote {len(blob)} bytes to {dest} (NOT sent anywhere)")


def decode(src):
    data = Path(src).read_bytes()
    msgs = sysex.smf_sysex(data) if data[:4] == b"MThd" else sysex.split_sysex(data)
    mem = {}
    for m in msgs:
        try:
            r = sysex.parse(m)
        except ValueError:
            print("non-Roland message:", m[:12].hex(" "))
            continue
        base = addr_to_int(r.address)
        print(f"{'DT1' if r.command == 0x12 else hex(r.command)} dev={r.device:02X} model={r.model_id.hex(' ')}"
              f" addr={fmt_addr(r.address)} len={len(r.payload)} checksum_ok={r.checksum_ok}")
        if r.command == sysex.DT1:
            for i, b in enumerate(r.payload):
                mem[base + i] = b
    params = S.parameters(root=None)

    def read(p):
        a = addr_to_int(p.address)
        if not all(a + k in mem for k in range(p.size)):
            return None, None
        raw = bytes(mem[a + k] for k in range(p.size))
        try:
            return raw, decode_value(S.value(p.structure, p.name), raw)
        except ValueError as e:
            return raw, f"DECODE ERROR {e}"

    # current effect types select which union members are meaningful
    active = {}
    for key, disc in (("mfx", "fm.pat.mfx.mfxType"), ("chorus", "fm.pat.cho.chorusType"),
                      ("reverb", "fm.pat.rev.reverbType")):
        p = next(x for x in params if x.path == disc)
        active[key] = read(p)[1]
    hits = 0
    for p in params:
        if p.effect and active.get(p.effect.split(":")[0]) != p.effect_index:
            continue
        raw, val = read(p)
        if raw is None:
            continue
        hits += 1
        shown = val
        if p.enum and isinstance(val, int):
            vals = p.enum_values or list(range(p.range[0], p.range[0] + len(p.enum)))
            if val in vals:
                shown = f"{val} ({p.enum[vals.index(val)]})"
        print(f"  {p.path:55s} {p.address}  {raw.hex(' ').upper():12s} = {shown}")
    print(f"{len(mem)} bytes received, {hits} parameter reads decoded")


if __name__ == "__main__":
    {"make-requests": make_requests, "decode": decode}[sys.argv[1]](sys.argv[2])
