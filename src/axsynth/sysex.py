"""Roland DT1/RQ1 message helpers for the AX-Synth. Builds and parses bytes
only; nothing here talks to a MIDI port.

From the official MIDI Implementation (docs/AX Synth docs.pdf, p.4 & p.16):
  RQ1: F0 41 dev 00 00 3C 11 aa bb cc dd ss tt uu vv sum F7
  DT1: F0 41 dev 00 00 3C 12 aa bb cc dd <data...>   sum F7
  dev = 10H (default) or 7FH (broadcast, receive only)
  sum = (128 - (sum(address + data|size) % 128)) % 128
  DT1 data > 256 bytes is sent as packets of <= 256 bytes (~20 ms apart).
"""
from __future__ import annotations

from dataclasses import dataclass

ROLAND = 0x41
MODEL_ID = bytes([0x00, 0x00, 0x3C])   # doc p.4; also <modelID> in Script.xml midiOut
DEFAULT_DEVICE = 0x10
RQ1, DT1 = 0x11, 0x12


def checksum(body: bytes) -> int:
    return (128 - sum(body) % 128) % 128


def _addr(address: int | bytes) -> bytes:
    if isinstance(address, int):
        from .schema import int_to_addr
        return int_to_addr(address)
    if len(address) != 4 or any(b > 0x7F for b in address):
        raise ValueError("address must be 4 7-bit bytes")
    return bytes(address)


def build_dt1(address: int | bytes, data: bytes, device: int = DEFAULT_DEVICE) -> bytes:
    a = _addr(address)
    if any(b > 0x7F for b in data):
        raise ValueError("DT1 data bytes must be 7-bit")
    body = a + bytes(data)
    return bytes([0xF0, ROLAND, device, *MODEL_ID, DT1]) + body + bytes([checksum(body), 0xF7])


def build_rq1(address: int | bytes, size: int, device: int = DEFAULT_DEVICE) -> bytes:
    from .schema import int_to_addr
    body = _addr(address) + int_to_addr(size)
    return bytes([0xF0, ROLAND, device, *MODEL_ID, RQ1]) + body + bytes([checksum(body), 0xF7])


@dataclass
class RolandMessage:
    device: int
    model_id: bytes
    command: int
    address: bytes
    payload: bytes          # DT1: data; RQ1: 4-byte size
    checksum_ok: bool


def parse(msg: bytes) -> RolandMessage:
    """Parse one F0..F7 Roland message with a 3-byte model ID."""
    if msg[0] != 0xF0 or msg[-1] != 0xF7 or msg[1] != ROLAND:
        raise ValueError("not a Roland SysEx message")
    device, model, cmd = msg[2], bytes(msg[3:6]), msg[6]
    body = bytes(msg[7:-2])
    return RolandMessage(device, model, cmd, body[:4], body[4:], checksum(body) == msg[-2])


def split_sysex(stream: bytes) -> list[bytes]:
    """Split a raw byte stream (e.g. a .syx file) into F0..F7 messages."""
    out, cur = [], None
    for b in stream:
        if b == 0xF0:
            cur = bytearray([b])
        elif cur is not None:
            cur.append(b)
            if b == 0xF7:
                out.append(bytes(cur))
                cur = None
    return out


def smf_sysex(data: bytes) -> list[bytes]:
    """Extract SysEx events from a Standard MIDI File (as written by the
    Editor/Librarian 'Export SMF'). Returns complete F0..F7 messages."""
    def varlen(buf, i):
        v = 0
        while True:
            b = buf[i]; i += 1
            v = (v << 7) | (b & 0x7F)
            if not b & 0x80:
                return v, i
    if data[:4] != b"MThd":
        raise ValueError("not an SMF")
    i = 8 + int.from_bytes(data[4:8], "big")
    out = []
    while i < len(data):
        cid, ln = data[i:i + 4], int.from_bytes(data[i + 4:i + 8], "big")
        trk, i = data[i + 8:i + 8 + ln], i + 8 + ln
        if cid != b"MTrk":
            continue
        j, status = 0, 0
        while j < len(trk):
            _, j = varlen(trk, j)
            b = trk[j]
            if b == 0xF0:
                n, j = varlen(trk, j + 1)
                out.append(bytes([0xF0]) + trk[j:j + n])
                j += n
            elif b == 0xF7:
                n, j = varlen(trk, j + 1)
                j += n
            elif b == 0xFF:
                n, j2 = varlen(trk, j + 2)
                j = j2 + n
            else:
                if b & 0x80:
                    status, j = b, j + 1
                j += 1 if (status & 0xF0) in (0xC0, 0xD0) else 2
    return out
