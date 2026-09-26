# Bulk Dump (NEXT-STEPS 3.2), 2026-09-26

Written from the user's report ("no errors or complications"). The synth was powered on with VARIATION [–]+[+]+TONE [6] ("dMP"), then FAVORITE [B] (send). MIDI-OX recorded until "dNE" (~16 min). The file was renamed from `bulkdump-2026-09-26.sysx.syx`.

- `bulkdump-2026-09-26.syx`: 2,128,751 bytes = 16,230 SysEx messages, all checksums valid, plus 2,784 stray `00` bytes between messages (MIDI-OX padding, ignored).
- It isn't Roland's patch format. It's a **raw memory image** (model ID `7F`, 7-in-8 packing), 1,704,000 bytes long, and it holds the System settings, the 16 FAVORITE memories and all 256 User patches. Decoded by `research/tools/bulkdump.py`; analysis in `research/bulkdump-analysis.md`.
- All 256 patches rebuilt from it are **byte-identical to the Librarian backup** (`captures/backup/`), so this is a second, independent backup.

⚠ It's also a restore file: sending it back while the synth is in Bulk Dump *receive* mode (FAVORITE [A]) would overwrite everything. Never do that unless restoring on purpose.
