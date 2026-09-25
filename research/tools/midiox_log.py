"""Decode MIDI-OX SysEx-view text logs (captures/live/*.txt) message by message.

This tool never opens a MIDI port. It reads text files only.

  python midiox_log.py <log.txt> [more logs...] [--syx out.syx]

MIDI-OX log format (one message = header line + one or more SYSX: lines):
   TIMESTAMP IN PORT STATUS DATA1 DATA2 CHAN NOTE EVENT
   0000303A   1  --     F0  Buffer:    14 Bytes   System Exclusive
   SYSX: F0 41 10 00 00 3C 12 1F 00 20 49 7C 7C F7
TIMESTAMP is hexadecimal milliseconds since MIDI-OX started.

For each message: timestamp, gap to the previous one, byte count check
(against the "Buffer: N Bytes" header), Roland checksum, and every parameter
whose bytes the message covers, decoded with our schema (User Patch addresses
are mapped onto the Temporary Patch layout). Effect-union members
(MFX / chorus / reverb) are shown for the effect type last seen in the same
log (e.g. a whole-MFX-block DT1 earlier in the capture), otherwise only the
generic slot names are shown. Universal identity request/reply are named.
--syx writes all messages, concatenated, as a raw .syx file.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from axsynth import sysex  # noqa: E402
from axsynth.schema import Schema, addr_to_int, decode_value, fmt_addr  # noqa: E402

HEADER = re.compile(r"^\s*([0-9A-Fa-f]{8})\s+(\S+)\s+\S+\s+F0\s+Buffer:\s+(\d+)\s+Bytes")
DATA = re.compile(r"^\s*SYSX:\s*((?:[0-9A-Fa-f]{2}\s*)+)$")


def read_log(path):
    """-> list of (timestamp_ms, in_port, declared_len, bytes). in_port is
    MIDI-OX's IN PORT column (tells directions apart in a two-port capture)."""
    msgs = []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        if m := HEADER.match(line):
            msgs.append([int(m.group(1), 16), m.group(2), int(m.group(3)), bytearray()])
        elif (m := DATA.match(line)) and msgs:
            msgs[-1][3].extend(int(t, 16) for t in m.group(1).split())
    return [(t, port, n, bytes(b)) for t, port, n, b in msgs]


S = Schema.load()
PARAMS = S.parameters(root=None)
BY_ADDR = sorted(((addr_to_int(p.address), p) for p in PARAMS), key=lambda x: x[0])
DISCRIMINATORS = {"mfx": "fm.pat.mfx.mfxType", "chorus": "fm.pat.cho.chorusType",
                  "reverb": "fm.pat.rev.reverbType"}


def label(p, val):
    if p.enum and isinstance(val, int):
        vals = p.enum_values or list(range(p.range[0], p.range[0] + len(p.enum)))
        if val in vals:
            return f"{val} ({p.enum[vals.index(val)]})"
    if p.display_offset and isinstance(val, int):
        return f"{val} (display {val + p.display_offset:+d})"
    return repr(val) if isinstance(val, str) else str(val)


def covered(start, data, active):
    """Parameters lying inside [start, start+len(data)), plus partial overlaps."""
    end = start + len(data)
    full, partial = [], []
    for a, p in BY_ADDR:
        if a >= end or a + p.size <= start:
            continue
        if p.effect:
            kind = p.effect.split(":")[0]
            if active.get(kind) != p.effect_index:
                continue
        if a >= start and a + p.size <= end:
            raw = data[a - start:a - start + p.size]
            try:
                val = decode_value(S.value(p.structure, p.name), raw)
            except ValueError as e:
                val = f"DECODE ERROR {e}"
            full.append((p, raw, val))
        else:
            partial.append(p)
    return full, partial


def to_model_address(start):
    """User Patch n (30 00 00 00 + n*00 01 00 00) is not in Script.xml; map it
    onto the Temporary Patch layout (same blocks, doc p.7) -> (addr, note)."""
    user0, temp = sysex.user_patch_address(0), sysex.TEMPORARY_PATCH
    step = sysex.user_patch_address(1) - user0
    if user0 <= start < user0 + 256 * step:
        n, off = divmod(start - user0, step)
        return temp + off, f"User Patch {n} (Librarian {n // 32 + 1}-{n % 32 + 1}); shown as Temporary-Patch paths"
    return start, None


def describe(msg, active):
    if msg[:2] == b"\xF0\x7E" and len(msg) >= 6 and msg[3:5] == b"\x06\x01":
        return [f"Universal Identity Request, device ID {msg[2]:02X}"]
    if msg[:2] == b"\xF0\x7E" and len(msg) >= 6 and msg[3:5] == b"\x06\x02":
        head = f"Universal Identity Reply, device ID {msg[2]:02X}: {msg[5:-1].hex(' ').upper()}"
        try:
            diff = sysex.parse_identity_reply(bytes(msg)).differences_from_doc()
        except ValueError as e:
            return [head, f"  {e}"]
        return [head, "  differs from MIDI Implementation p.6: " + "; ".join(diff) if diff
                else "  identical to MIDI Implementation p.6"]
    try:
        r = sysex.parse(msg)
    except (ValueError, IndexError):
        return ["not a Roland DT1/RQ1 message"]
    start, note = to_model_address(addr_to_int(r.address))
    head = (f"dev={r.device:02X} model={r.model_id.hex(' ').upper()} checksum_ok={r.checksum_ok} "
            f"addr={fmt_addr(r.address)}")
    if note:
        head += f"  [{note}]"
    if r.command == sysex.RQ1:
        size = addr_to_int(r.payload)
        full, partial = covered(start, bytes(size), active)
        out = [f"RQ1 {head} size={size} (0x{size:X})"]
        out += [f"    requests {p.path} [{p.address}, {p.size} B]" for p, _, _ in full]
        return out
    if r.command != sysex.DT1:
        return [f"command {r.command:02X} {head}"]
    full, partial = covered(start, r.payload, active)
    # a DT1 that sets an effect type switches which union members are meaningful
    for kind, path in DISCRIMINATORS.items():
        for p, _, val in full:
            if p.path == path and isinstance(val, int):
                if active.get(kind) != val:
                    active[kind] = val
                    full, partial = covered(start, r.payload, active)
    out = [f"DT1 {head} len={len(r.payload)}"]
    for p, raw, val in full:
        eff = f"  [{p.effect}]" if p.effect else ""
        out.append(f"    {p.path:50s} {p.address}  {raw.hex(' ').upper():12s} = {label(p, val)}{eff}")
    for p in partial:
        out.append(f"    PARTIAL overlap with {p.path} [{p.address}, {p.size} B]")
    if not full and not partial:
        out.append("    (no known parameter at this address)")
    return out


def main(argv):
    syx_out = None
    if "--syx" in argv:
        i = argv.index("--syx")
        syx_out = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    blob = b""
    for path in argv:
        print(f"===== {path}")
        active, prev = {}, None
        for t, port, declared, msg in read_log(path):
            blob += msg
            gap = "" if prev is None else f" (+{t - prev} ms)"
            prev = t
            ok = "" if declared == len(msg) else f"  LENGTH MISMATCH: header says {declared}"
            print(f"{t:>9d} ms{gap}  port {port}  {len(msg)} B{ok}")
            for line in describe(msg, active):
                print("  " + line)
    if syx_out:
        Path(syx_out).write_bytes(blob)
        print(f"wrote {len(blob)} bytes to {syx_out} (NOT sent anywhere)")


if __name__ == "__main__":
    main(sys.argv[1:])
