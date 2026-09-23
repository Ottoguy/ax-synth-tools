# Roland installation inventory

Source: `original-roland-files/` (176 files). Generated data with SHA-256 for every file: [`generated/inventory.json`](generated/inventory.json) (`tools/inventory.py`). Nothing in `original-roland-files/` was modified; re-run the tool and compare hashes to check.

## Relevant files

| File | Ext | Size | Text/binary | Apparent purpose | Why it matters |
|---|---|---|---|---|---|
| `Script/A8EE/Script.xml` | .xml | 1,129,507 | text (ASCII; declared Shift_JIS) | Complete Editor definition: data model, MIDI binding, UI | **Primary source.** Parameter names, addresses, sizes, types, ranges, defaults, effect unions, and display labels for all 1,539 values. See `script-analysis.md` |
| `Script/A8EE/InitialData.a8e` | .a8e | 1,465 | binary, magic `KoaDataFile00001` | Editor's blank document: Setup + System + INIT patch | Proves the file encoding equals the SysEx encoding; the reference INIT patch. See `initialdata-analysis.md` |
| `Script/A8EL/InitialData.a8l` | .a8l | 1,276 | binary, magic `A8ELibrarianFile0000` | Librarian's blank library entry (1 INIT patch) | Defines the library container format for 256-patch libraries |
| `A8EE.exe` | .exe | 2,183,168 | binary PE, "AX-Synth Editor" 1.00, © 2009 Roland Corp. | Koa editor engine (MFC) | Parser vocabulary (all type names), `FKoaSendDt1/SendRq1/RequestRq1Dt1`, the 79 MFX display names, the `.a8e` format, a hidden MIDI monitor/dump menu, `WritePatch`, `ReadReservedPatches`. Strings in `generated/A8EE.exe.strings.txt` |
| `A8EL.exe` | .exe | 1,875,968 | binary PE, "AX-Synth Librarian" 1.00 | Librarian (Koa MIDI layer, hard-coded patch model) | `ReadTemporary/WriteTemporary/ReadUser/WriteUser`, `.a8l` magic, SMF reader/writer, overwrite confirmations. Strings in `generated/A8EL.exe.strings.txt` |
| `Manual/AX-SynthEditorManualE.pdf` | .pdf | 2,644,829 | binary | English Editor manual (identical to `docs/`) | Read/Write/Sync semantics (Editor writes to the **Temporary Area**), Export/Import SMF, parameter descriptions |
| `Manual/AX-SynthLibrarianManualE.pdf` | .pdf | 463,949 | binary | English Librarian manual | 256 patches = Bank 1–8 × 1–32; Audition sends to Temporary; memos not stored on the device |
| `Manual/*J.pdf` | .pdf | 2.7 MB / 456 KB | binary | Japanese manuals | Same content; not analysed |
| `Script/A8EE/*.bmp` (167) | .bmp | 72.7 MB total | binary (`BM`) | UI artwork: panels, knobs, 79 `mfxN.bmp` effect diagrams, envelope zoom views | Little data value. `mfx0..78.bmp` visually document each MFX algorithm; possibly useful for human reference later. 166 are referenced by Script.xml; `PatchEffectsDryOut.bmp` is unused; `patchToneControl` vs `PatchToneControl` differ only in case |

Also in the project but outside the installation:
- `docs/AX Synth docs.pdf` = **"AX-Synth MIDI Implementation", Roland Europe, Jan 2010, v1.00, 16 pages**. It is the official SysEx specification and the most important external reference (text in `generated/midi-implementation.pdf.txt`).
- `docs/AX-Synth_Erratum2.pdf` (91,497 bytes, 1 page, Roland doc no. 602.00.0399 RES 747-09, dated 5 Oct 2009) = **erratum to the Owner's Manual p.27** (text in `generated/erratum2.pdf.txt`). It deletes the "Volume, CC07, transmission: [VOLUME] knob" row, because *"The AX-Synth's [VOLUME] knob cannot transmit MIDI messages, because it is analog."* The file name implies an Erratum 1 exists; we don't have it.
- `docs/AX-Synth_OM.pdf` (5,048,286 bytes, 44 pages, doc no. 602.00.0354.02 RES 750-09, file `AX-Synth_e2`, 12 Oct 2009) = **Owner's Manual** (text in `generated/owners-manual.pdf.txt`). Contains the **factory Tone list** (→ `generated/factory-tones.*`), panel/UI description, Bulk Dump, factory reset, firmware check, the MIDI Implementation Chart and the CC list. No parameter explanations and no wave list; see `owners-manual-analysis.md`.

## Searched for and not present

- `.syx`, `.mid`, `.bin`, `.dat`, `.ini`, language/resource DLLs, factory preset banks: **none** in the installation.
- DLLs: none shipped. Imports are only Windows system DLLs, and MIDI goes through `WINMM.dll` (`midiOutLongMsg`, `midiInAddBuffer`, …).
- MFX type display names are **not** in `Script.xml`; they are compiled into `A8EE.exe`. The script does have `mfxCategoryTable` (NO ASSIGN, FILTER, MODULATION, …).
- **Wave names ARE in `Script.xml`**: `stringTable internalWaveNameTableA` (l.16202), **313 names** ("JD Piano", "Stage EP p", …). No `<control>` references it; `A8EE.exe` builds the name at runtime (`internalWaveNameTable%c`). Doc: wave number 0 = OFF, 1…16384. So wave *N* ↔ entry *N−1* is likely **[I, verify on hardware]**.
- `ViewState.txt` is named in `A8EE.exe` but not shipped. It is probably written at runtime for UI state **[I]**.
