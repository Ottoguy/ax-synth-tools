# InitialData.a8l and InitialData.a8e

Two initial-data files ship with the software:

| File | Size | SHA-256 (prefix) | Owner |
|---|---|---|---|
| `original-roland-files/Script/A8EL/InitialData.a8l` | 1,276 | `7ca5fb708d37` | Librarian (`A8EL.exe`: `Unable to read initial file.`, `\Script\A8EL\`) |
| `original-roland-files/Script/A8EE/InitialData.a8e` | 1,465 | `1117aca9459b` | Editor (`A8EE.exe`: `InitialData.a8e`, `Unable to read initial data file.`) |

Parser: [`tools/a8_files.py`](tools/a8_files.py) (read-only, schema-driven). Tests: `tests/test_schema.py::RolandDataFiles`.
Both files are binary and parse with **0 unexplained bytes** in the `.a8e` and **4** in the `.a8l`.

## Summary

- Both files contain **one patch, "INIT PATCH  "**. Its bytes are **identical** in both files (tested block by block).
- Every *active* parameter equals the `<default>` in `Script.xml`. The only differences are in `reserve*` bytes and the unreachable `gm2Chorus-*`/`gm2Reverb-*` union members.
- Data is stored in the **same 7-bit/nibble encoding as SysEx DT1 payloads**, laid out exactly as the Script.xml structs. `masterTune` 1024 → `00 04 00 00`; MFX zero → `08 00 00 00`. Struct sizes equal the "Total Size" rows of the official MIDI Implementation.
- **Neither file contains SysEx framing** (no `F0`, `41`, model ID, addresses, or checksums). They are memory images, not dumps.
- These are **not factory presets**. They are the blank template a new document or library starts from ("INIT data" in the Librarian manual). The factory patches are not in the installation.

## `.a8e`: Koa data file (Editor document)

| Offset | Size | Content |
|---|---|---|
| 0x000 | 16 | `KoaDataFile00001` (magic; the exe has the same literal and class `CKoaDataFile`) |
| 0x010 | 64 | root struct name `fm`, space padded |
| 0x050 | 16 | model name `AX-Synth`, space padded |
| 0x060 | 160 | all zero |
| 0x100 | 52 | `fm.setup` (Setup) |
| 0x134 | 30 | `fm.system.common` |
| 0x152 | 79 | `fm.system.controller` (script size 4F; the doc says 50) |
| 0x1A1 | 79 | `fm.pat.common` (`INIT PATCH  ` …) |
| 0x1F0 | 145 | `fm.pat.mfx` |
| 0x281 | 84 | `fm.pat.cho` |
| 0x2D5 | 83 | `fm.pat.rev` |
| 0x328 | 41 | `fm.pat.tmt` |
| 0x351 / 0x3EB / 0x485 / 0x51F | 154 each | `fm.pat.tone[0..3]` |
| **0x5B9** | | **= 1,465 = file size** |

So an `.a8e` is: header, then every **leaf struct under the root named in the header**, depth-first in Script.xml declaration order, each exactly `<size>` bytes. It stores full struct images, including reserved bytes the script never declares (e.g. Setup byte `01` = `0x55`). A generic save routine like this makes sense for a framework that saves whatever root the script defines **[I]**.

Reserved-byte values that differ from the script defaults: SystemController `reserve04`=100, `reserve07`=11, `reserve09`=5. PatchCommon `reserve1F` (int2x4, script range 20–250) = **0**, which is outside the script's own range. These probably came from a real device or from firmware defaults **[I]**.

## `.a8l`: Librarian library file

| Offset | Size | Content |
|---|---|---|
| 0x000 | 32 | `A8ELibrarianFile0000` + spaces (exe literal `A8ELibrarianFile0000            `) |
| 0x020 | 4 | **u32 big-endian patch count** (= 1) |
| 0x024 | 124 | zero |
| 0x0A0 | 4 | u32 BE **record length** = 1112 (bytes that follow, up to the end of the record) |
| 0x0A4 | | for each Patch child struct in order `common, mfx, cho, rev, tmt, tone`: **u32 BE instance count**, then *count* × (**u32 BE instance size**, *size* bytes) |
| 0x4F8 | 4 | `00 00 00 00`: inside the record, **meaning unknown** |

Block table from the file:

| block | count | size | data offset |
|---|---|---|---|
| common | 1 | 79 (0x4F) | 0x0AC |
| mfx | 1 | 145 (0x91) | 0x103 |
| cho | 1 | 84 (0x54) | 0x19C |
| rev | 1 | 83 (0x53) | 0x1F8 |
| tmt | 1 | 41 (0x29) | 0x253 |
| tone | **4** | 154 (0x9A) each, each prefixed with its own size | 0x284, 0x322, 0x3C0, 0x45E |

**Third-party corroboration [3P]:** `cmatsuoka/fsex` (`library.c`), which reads Juno-G/Fantom-X/Fantom-S librarian files (`.jgl/.fxl/.fsl`), uses the same container: 32-byte ID, u32 BE patch count at offset 32, a 160-byte header (it seeks to byte 159 when creating a file), then per patch a u32 BE size followed by 4-byte-length-prefixed blocks. So `.a8l` is the AX-Synth instance of an existing Roland librarian format.

The trailing 4 bytes: the Librarian lets each patch carry **Memo 1–4** comments that are "not saved to the AX-Synth" (Librarian manual p.9). A zero count or length for memo data would fit **[I, unverified]**. Saving a library with a memo filled in would settle it.

The `.a8l` stores **only patches** (no Setup/System). The Librarian manages the 256 User patches, addressed `30 00 00 00`…`31 7F 00 00` in the doc. The Librarian's `CPatch` class is compiled into `A8EL.exe` rather than scripted.

## Does the data correspond to Script.xml? Yes.

- Sizes: every block size equals the script's `<size>` for that struct type, and the official "Total Size".
- Values: decoding with the script's types gives script defaults for every active parameter.
- The Editor file header names the script's root struct (`fm`).

## What remains unknown

1. The 4 trailing bytes in each `.a8l` record (memo hypothesis).
2. Whether a real User-patch dump from the hardware is byte-identical to an `.a8l` block. Very likely, since both use the same encoding and struct sizes, but unverified.
3. The source of the non-default reserved bytes in `.a8e`.
4. The `.mid` (Export SMF) format both apps can write. It is expected to contain DT1 SysEx; see `src/axsynth/sysex.py::smf_sysex` for a reader.
