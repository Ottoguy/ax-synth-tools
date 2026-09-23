# AX-Synth data model: research report (phase 1)

Scope: how Roland represents an AX-Synth patch, established from Roland's own files. No AI or sound-design code. **Nothing has been sent to the hardware.**

Evidence labels: **[F]** our Roland files · **[D]** official Roland documentation · **[3P]** third party · **[I]** inference.

## Bottom line

`Script.xml` is **the Editor's executable data model**. Its `fm`/`cm` address tree *is* the AX-Synth's SysEx (DT1/RQ1) address space, its types *are* the wire encodings, and Roland's own data files store patches in exactly that encoding. The chain

```
Script.xml  ->  parameter model  ->  bytes  ->  DT1 SysEx (F0 41 10 00 00 3C 12 addr data sum F7)
```

is **direct, with no hidden translation layer**: struct offsets equal SysEx address offsets, and struct images equal DT1 payloads. Of the 813 non-effect-specific parameter instances in `fm`, **807 are independently confirmed** (address, encoding, range) by the official MIDI Implementation. The other 6 are 3 range typos in the doc (one repeated across the 4 Tones). This rests on documents and Roland's files; it has not yet been observed on the hardware.

## What we know (directly supported)

1. **The address system.** Script addresses are 7-bit, MSB-first Roland addresses. Short forms are right-aligned, parent + child offsets are added base-128, and repeated `<address>` tags define arrays (4 Tones). Setup `01 00 00 00`, System `02 00 00 00`, Temporary Patch `1F 00 00 00` with blocks at `+00 00 00` Common, `02 00` MFX, `04 00` Chorus, `06 00` Reverb, `10 00` TMT, `20/22/24/26 00` Tone 1–4. **[F+D]** Tied to MIDI by `<midiOut>` model ID `00 00 3C` and `rootStruct fm, cm` **[F]**. The official doc gives the same model ID and map **[D]**, and adds User Patches at `30 00 00 00 + n·(00 01 00 00)`, n = 0…255.
2. **Types.** `int<W>x<B>` = W wire bytes of B low bits each, MSB first. Used here: `int1x7` (372), `int4x4` (1,157, "nibbled" in the doc), `int2x4` (4), `int5x7` (4, UI-only), `string` (ASCII). The exe knows exactly this vocabulary and enforces size = W **[F]**. The doc's nibble definition agrees **[D]**, and BOSS TONE STUDIO code uses the same grammar **[3P]**. Signed values are stored offset (64 = 0; 32768 = 0 for effect parameters).
3. **Cross-check.** All 515 parameter rows in the MIDI Implementation were compared with the script ([generated/crosscheck-midi-implementation.md](generated/crosscheck-midi-implementation.md)). Offsets, nibble/7-bit encoding, ranges and block sizes agree, except for 3 range typos in the doc and one missing parameter (item 3 of "remains unknown").
4. **Effect unions.** MFX (79 types), Chorus (3) and Reverb (5) parameters are unions over generic 4-byte slots. `*ValuePathTable` defines which named members apply to which type, e.g. MFX type 1 EQUALIZER → `equalizer-loGain` = slot 2 = `1F 00 02 15`. Type names come from `A8EE.exe` **[F]**. **The official doc does not contain this mapping** (it only says "MFX Parameter 1–32").
5. **Display semantics.** 526 parameters have enum labels and 986 have display offsets, taken from the UI bindings and labelled "ui-derived". Sparse enums use `numberTable`s, e.g. output assign `0,1,5,6,13`. The script ships **313 internal wave names** (`internalWaveNameTableA`) and MFX categories.
6. **Data files.** `.a8e` (Koa data file) = 256-byte header plus raw images of every leaf struct under `fm`. `.a8l` (Librarian) = 160-byte header, u32 BE count, then per patch a u32 record length and length-prefixed blocks (same container as Juno-G/Fantom-X librarians **[3P]**). Both hold the **same INIT PATCH**, equal to the script defaults, in DT1 encoding. **Neither contains SysEx framing or factory presets.**
7. **Framework.** Roland's "Koa" editor engine, shared with XV-5050/Fantom-X/Juno-class editors. Evidence: control types `xvToneSelectButton`, `fantomXLfoControl`; `…XV5050Table`; and a `CommunicationModel` with performance, rhythm and sample fields the AX-Synth lacks **[F]**.
8. **Editor vs Librarian targets [D manuals].** The Editor reads and writes the **Temporary Area**. The Librarian reads and writes the **256 User patches** (Bank 1–8 × 1–32), and its Audition sends to Temporary. Both can **Export/Import SMF**.

## What we strongly suspect (evidence-backed, unverified)

- A User-patch DT1 dump from the hardware is byte-identical to an `.a8l` patch block (same encoding and sizes everywhere else).
- `cm.command.writeRequest/writeStart/writeComplete` at `0F 00 10 00–02` is the handshake the Editor's `WritePatch` uses to store the Temporary patch into a User slot. The Editor also appears to read patch-name lists through `cm` "…Information" addresses.
- `gm2Chorus-*` (7) / `gm2Reverb-*` (5) are dead leftovers: in no path table, and outside the chorus/reverb type ranges.
- `stepPitchShifter-bal/level` (`00 81`/`00 85`, invalid 7-bit bytes) are meant to be `01 01`/`01 05`, the doc's MFX Parameter 29/30.
- PatchCommon `reserve1F` (int2x4, 20–250, default 120) is a tempo.
- Wave number *N* ↔ `internalWaveNameTableA[N−1]`.
- An `.a8l` record's final 4 bytes relate to Librarian memo fields.
- Script.xml files from sibling Koa editors would parse with the same tools.

## What remains unknown

| Area | Open question |
|---|---|
| SysEx | Device ID in practice (doc: 10H/7FH); whether the synth accepts RQ1 for a whole block, and how it packetizes replies (doc: ≤256-byte packets ~20 ms apart); timing needed between DT1s |
| Address conversion | What the Editor actually sends for the two `00 81`/`00 85` addresses |
| SystemController | Doc size `50` (includes `00 4F` Portamento Mode) vs script/`.a8e` size `4F` |
| Checksums | Formula documented; not yet observed on a real message from this synth |
| Patch storage | How a Temporary patch is committed to a User slot: the `0F 00 10 0x` payloads, and whether a DT1 to `30 xx 00 00` writes flash directly or needs a command. **Do not experiment with writes yet** |
| .a8l | Trailing 4 bytes per record; memo storage |
| Serialization | Whether the hardware's reply includes reserved bytes identical to `.a8e`; `reserve1F` = 0 lies outside the script's range |
| MIDI comms | Which RQ1s the Editor sends on READ/SYNC (the name list via `cm`?) |

## Most valuable discoveries (ranked)

1. **`Script.xml` data model + `<midiOut>` binding.** It is the machine-readable AX-Synth SysEx map with names, types, ranges and defaults. Extracted to [script-schema.json](script-schema.json).
2. **`docs/AX Synth docs.pdf` (MIDI Implementation).** Independent confirmation, plus the checksum, User-patch addresses and packet rules.
3. **`mfxValuePathTable` / `chorus…` / `reverb…` + MFX names in `A8EE.exe`.** Per-effect parameter meaning, which is essential for sound design and exists nowhere else.
4. **The display tables** (enum labels, offsets, 313 wave names). What a musician or an AI needs in order to reason about values.
5. **`InitialData.a8e`/`.a8l`.** A verified reference INIT patch and the library container for importing and exporting whole banks.

## Next experiment (single most useful): read-only Temporary-patch dump

**Goal:** confirm on real hardware that addresses, sizes, encoding, checksums and enum mapping match the model, with **zero risk of changing synth memory** (RQ1 only asks the synth to reply).

1. On the AX-Synth, select a known factory patch. Note its name and a few values (e.g. filter type, patch level).
2. Send `research/generated/experiment-rq1-temporary-patch.syx` (10 RQ1s: 9 patch blocks + SystemController with size 50) using a SysEx utility such as MIDI-OX. Record all incoming SysEx to `reply.syx`.
3. `py -3 research/tools/dump_experiment.py decode reply.syx`
   Expect: 9–10 DT1 replies with `checksum_ok=True`, patchName = the displayed name, labels that make sense (e.g. `tvfFilterType = LPF`), and the SystemController reply length answering the 4F/50 question.
4. Change **one** parameter on the synth's panel (e.g. cutoff via the knob), re-send, re-record, and diff. Exactly the predicted address (Tone *n* `…49` TVF cutoff) should change.

**Zero-hardware alternative worth doing first:** run the Editor or Librarian offline, use **File → Export SMF** on the INIT patch (and on a patch with one edited value), then `dump_experiment.py decode export.mid`. This shows the exact DT1 messages Roland's own software produces, including how it handles the `00 81` addresses.

## Files produced

| Path | What |
|---|---|
| `research/script-analysis.md` | Tasks 1–3, 7: structure, address system, type table |
| `research/initialdata-analysis.md` | Task 4: `.a8e`/`.a8l` formats |
| `research/roland-installation-inventory.md` | Task 5 |
| `research/online-research.md` | Task 6 |
| `research/script-schema.json` | Complete extraction (every element + source line), resolved absolute addresses, unions, tables, UI bindings |
| `research/generated/parameters.{csv,json}` | Parameter database: 1,934 `fm`+`cm` parameters with address, type, range, default, enum, effect, source line, confidence |
| `research/generated/crosscheck-midi-implementation.md`, `crosscheck.json` | Script vs official doc, row by row |
| `research/generated/*.strings.txt`, `*.pdf.txt`, `inventory.json` | EXE strings, PDF text, hashes |
| `research/generated/experiment-rq1-temporary-patch.syx` | Ready-to-send read-only requests (not sent) |
| `research/tools/` | `extract_script_schema.py`, `crosscheck_midi_impl.py`, `a8_files.py`, `build_parameter_db.py`, `dump_experiment.py`, `exe_strings.py`, `inventory.py`, `pdf2txt.py` |
| `src/axsynth/schema.py` | Typed model: `Schema`, `Parameter`, `decode_value`/`encode_value`, address helpers |
| `src/axsynth/sysex.py` | Checksum, DT1/RQ1 builders, parser, `.syx`/SMF readers (no MIDI I/O) |
| `tests/test_schema.py` | 18 evidence tests (`py -3 -m unittest discover -s tests`) |

Regenerate: `extract_script_schema.py` → `crosscheck_midi_impl.py` → `build_parameter_db.py` (the `.venv` with `pypdf` is only needed for `pdf2txt.py`).
