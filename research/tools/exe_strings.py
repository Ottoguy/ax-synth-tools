"""Extract printable ASCII and UTF-16LE strings from a binary (read-only).

Usage: python exe_strings.py <file> [min_len] > out.txt
Each line: <hex offset> <A|W> <string>
"""
import re
import sys


def extract(data: bytes, min_len: int = 5):
    for m in re.finditer(rb"[\x20-\x7e]{%d,}" % min_len, data):
        yield m.start(), "A", m.group().decode("ascii")
    for m in re.finditer(rb"(?:[\x20-\x7e]\x00){%d,}" % min_len, data):
        yield m.start(), "W", m.group().decode("utf-16le")


if __name__ == "__main__":
    path = sys.argv[1]
    min_len = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    data = open(path, "rb").read()
    for off, kind, s in sorted(extract(data, min_len)):
        print(f"{off:08X} {kind} {s}")
