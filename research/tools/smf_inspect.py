"""Inspect a Standard MIDI File event by event (read-only).

Prints header, every event with delta/absolute ticks, and for Roland SysEx
the device, model ID, command, address, length and checksum validity.

Usage: python smf_inspect.py file.mid [--summary]
"""
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from axsynth import sysex  # noqa: E402


def varlen(buf, i):
    v = 0
    while True:
        b = buf[i]; i += 1
        v = (v << 7) | (b & 0x7F)
        if not b & 0x80:
            return v, i


def events(data):
    """Yield (track, abs_tick, delta, kind, payload) for every event."""
    assert data[:4] == b"MThd"
    hlen = int.from_bytes(data[4:8], "big")
    fmt, ntrk, div = (int.from_bytes(data[8 + 2 * k:10 + 2 * k], "big") for k in range(3))
    yield ("header", {"format": fmt, "tracks": ntrk, "division": div, "header_len": hlen})
    i, t = 8 + hlen, 0
    while i < len(data):
        cid, ln = data[i:i + 4], int.from_bytes(data[i + 4:i + 8], "big")
        trk, i = data[i + 8:i + 8 + ln], i + 8 + ln
        if cid != b"MTrk":
            yield ("chunk", {"id": cid, "len": ln})
            continue
        j, tick, status = 0, 0, 0
        while j < len(trk):
            d, j = varlen(trk, j)
            tick += d
            b = trk[j]
            if b in (0xF0, 0xF7):
                n, j2 = varlen(trk, j + 1)
                body = trk[j2:j2 + n]
                j = j2 + n
                yield ("event", (t, tick, d, "sysex" if b == 0xF0 else "sysex-cont",
                                 (bytes([0xF0]) + body) if b == 0xF0 else body))
            elif b == 0xFF:
                typ = trk[j + 1]
                n, j2 = varlen(trk, j + 2)
                yield ("event", (t, tick, d, f"meta:{typ:02X}", trk[j2:j2 + n]))
                j = j2 + n
            else:
                if b & 0x80:
                    status, j = b, j + 1
                n = 1 if (status & 0xF0) in (0xC0, 0xD0) else 2
                yield ("event", (t, tick, d, f"ch:{status:02X}", trk[j:j + n]))
                j += n
        t += 1


def main(path, summary=False):
    data = Path(path).read_bytes()
    kinds, addrs, lens, deltas = Counter(), [], Counter(), Counter()
    first_ok = True
    for tag, ev in events(data):
        if tag != "event":
            print(tag, ev)
            continue
        trk, tick, d, kind, payload = ev
        kinds[kind] += 1
        deltas[d] += 1
        line = f"trk{trk} tick={tick:6d} d={d:3d} {kind:10s} len={len(payload):4d}"
        if kind == "sysex":
            try:
                r = sysex.parse(payload)
                addrs.append(r.address)
                lens[len(r.payload)] += 1
                first_ok &= r.checksum_ok
                line += (f" dev={r.device:02X} model={r.model_id.hex(' ')} cmd={r.command:02X}"
                         f" addr={r.address.hex(' ').upper()} data={len(r.payload)} sum_ok={r.checksum_ok}")
            except ValueError as e:
                line += f" {e} {payload[:12].hex(' ')}"
        elif kind.startswith("meta"):
            line += f" {payload.hex(' ')}"
        if not summary:
            print(line)
    print("kinds:", dict(kinds))
    print("DT1 data lengths:", dict(lens))
    print("delta ticks:", dict(deltas))
    print("all checksums ok:", first_ok)
    if addrs:
        print("first/last address:", addrs[0].hex(" ").upper(), addrs[-1].hex(" ").upper(),
              "distinct:", len(set(addrs)))


if __name__ == "__main__":
    main(sys.argv[1], "--summary" in sys.argv)
