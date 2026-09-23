# Script.xml: what it is and how it works

**File:** `original-roland-files/Script/A8EE/Script.xml` (1,129,507 bytes, 37,610 lines, SHA-256 `33799461bb98…`).
There is no file called `script`. This is the Editor's `Script.xml`. `A8EE` is the Editor's internal product code (`A8EE.exe`) and `A8EL` the Librarian's. The Librarian has **no** script: its model is compiled into `A8EL.exe`.

Machine-readable extraction: [`research/script-schema.json`](script-schema.json), built by [`tools/extract_script_schema.py`](tools/extract_script_schema.py). Every element in it keeps its source line number.

Evidence labels: **[F]** = our files, **[D]** = official Roland documentation, **[3P]** = third-party, **[I]** = my inference.

---

## 1. What the file is

It is a **complete declarative definition of the AX-Synth Editor**, interpreted at runtime by a generic Roland editor engine. The engine's classes are named `CKoa…` in `A8EE.exe`, so this document calls it the "Koa" framework. The file has four parts:

| Part | Elements | Lines | Purpose |
|---|---|---|---|
| Data model | 3 root `<struct>`, 27 `<structType>`, 1,539 `<value>` | 7–12,850 | Parameter memory map |
| MIDI binding | 2 `<midiIn>`, 2 `<midiOut>`, 1 `<midiStruct>` | ~12,850–12,960 | Which parts of the model go to which MIDI port, and with which model ID |
| Lookup tables | 155 `<stringTable>`, 6 `<numberTable>`, 14 `<textWriter>` | 13,406–16,197 | Display labels, legal-value sets, fonts |
| UI | 166 `<bitmap>`, 206 `<panelType>`, 1,746 `<control>` | 12,960–37,474 | Windows, panels, knobs, and their `valueRef` bindings to the model |

Evidence that it is interpreted, not just documentation:
- **[F]** `A8EE.exe` contains the parser's vocabulary and error messages: `Unable to read structType %s.`, `Struct type can not have both structs and values.`, `Unable to resolve macros.`, `Value size must be %02X.`, `MIDI %s addressSize must be 1 through 4.`, `Value address range exceeds parent struct's one.`, and the literal path `/Script/Script.xml`.
- **[F]** The file declares `encoding="Shift_JIS"` but contains no bytes above 0x7F. Long runs of blank lines (for example lines 43–77) suggest comments were stripped before shipping **[I]**.

## 2. Data model

### Root structs (address spaces)

| Root | structType | Address | Bound to MIDI? |
|---|---|---|---|
| `fm` (FileModel) | FileModel | `00 00 00 00` | **yes**, `<rootStruct>fm</rootStruct>` in `midiIn`/`midiOut` "AX-Synth" |
| `cm` (CommunicationModel) | CommunicationModel | `0F 00 00 00` | **yes** |
| `vs` (ViewState) | ViewState | `00 00 00 00` | no; Editor-local UI state |

### Tree (`fm`, the synth's parameter memory)

```
fm  FileModel                                  00 00 00 00  size 1F 01 00 00
├── setup   Setup                (8 values)    01 00 00 00  size 00 00 00 34
├── system  System                             02 00 00 00  size 00 00 40 4F
│   ├── common      SystemCommon   (19)        +00 00       size 1E
│   └── controller  SystemController (14)      +40 00       size 4F   (doc: 50!)
└── pat     Patch                              1F 00 00 00  size 27 1A  (= "Temporary Patch")
    ├── common  PatchCommon       (67)         +00 00 00 00 size 4F
    ├── mfx     PatchCommonMFX    (1,060)      +00 00 02 00 size 01 11
    ├── cho     PatchCommonChorus (54)         +00 00 04 00 size 54
    ├── rev     PatchCommonReverb (62)         +00 00 06 00 size 53
    ├── tmt     PatchTMT          (41)         +00 00 10 00 size 29
    └── tone    PatchTone ×4      (142 each)   +00 00 20 00 / 22 00 / 24 00 / 26 00, size 01 1A
cm  CommunicationModel                         0F 00 00 00  size 01 00 00 00
└── command SystemInformation (41)             +00 00 00    size 00 01 00 00
```

- A struct can hold child structs **or** values, never both **[F]** (the exe error message above).
- **Repeated `<address>` tags in a `<struct>` define an array.** Tone has four addresses, so there are four instances: `tone[0..3]`.
- **Value names with `[n]`** (`tmtToneSwitch[0..3]`, `lfoRate[0..1]`, …) are *flattened* arrays. Each element is a separate `<value>` with its own address. Controls index them as `fm.pat.tone[vs.control.patchToneActiveValue].lfoWaveForm[$id]`.
- **`$name`, `$address`, `$size`, `$listCurRangeUp`, `$toneID`, `$mfx`, …** are macros. The referencing `<struct>` or panel fills them in **[F]**: the exe has `Unable to resolve macros. : %s`. Panel macros each have exactly one concrete binding: `$mfx`→`fm.pat.mfx` (l.19096), `$chorusParam`→`fm.pat.cho` (l.17746), `$reverbParam`→`fm.pat.rev` (l.18242), `$valueRefP`→`fm.pat` (l.37067).

### The `CommunicationModel` (`0F 00 00 00`): undocumented

Not in the official address map **[D]**. The values are information/command bytes:

| Offset | Values |
|---|---|
| 00 00–00 03 | `uexpInformation`, `preset{Performance,Patch,RhythmSet}BankInformation` |
| 01 00–01 04 | `waveNumberInformation`, `wave{A,B}NameInformation{,2}` |
| 02 xx / 03 xx / 04 xx | performance / patch / patch-category / rhythm-set number & name info |
| 06 xx / 07 xx / 0F 0x | multisample, sample, sample memory |
| **10 00 / 10 01 / 10 02** | **`writeRequest`, `writeStart`, `writeComplete`** |
| 20 00 | `phrasePreviewSwitch` (0–16) |
| 7F 00 / 7F 01 | `pcModeRequest` / `pcModeResult` |

Most of these (performances, rhythm sets, samples, phrase preview) do not exist on the AX-Synth. The block is inherited from a larger Fantom-X/Juno-G class instrument **[I]**. `A8EE.exe` references `cm.command.writeRequest`, `writeStart` and `writeComplete` by path, plus functions `WritePatch` and `ReadReservedPatches` **[F]**. This is almost certainly how the Editor stores the Temporary patch into a User slot **[I]**. **Payload semantics are unknown. Do not send.** The live WRITE capture never got that far: the Editor stops at an unanswered Identity Request ([live-capture-analysis.md](live-capture-analysis.md) §4–5).

### Effect unions (the biggest thing the doc doesn't tell you)

The official map only says "MFX Parameter 1…32" (4-byte nibbled slots at `00 11 + 4k`). The script defines **1,060** MFX values: the 36 generic slot/assign values plus **named per-effect members** that overlay the same slots, e.g. `equalizer-loGain` at `00 15` = slot 2.

The discriminator mapping is in `<stringTable name="mfxValuePathTable">` (l.14930): `DELIMITER`-separated groups, where group *N* lists the members that are meaningful when `mfxType == N`. Group 0 is the generic list, and type 0 (THROUGH) has no members.

- **[F]** All 78 MFX groups lay out as consecutive 4-byte slots starting at `00 11`.
- **[F]** Group index ↔ type name verified by matching prefixes against the display names hard-coded in `A8EE.exe` (bytes `0xF8FC0–0xF9438`, stored in reverse order): 1 = EQUALIZER (`equalizer-*`), 2 = SPECTRUM, …, 78 = SYMPATHETIC RESONANCE.
- Chorus (`chorusValuePathTable`): 1 = `chorus-*`, 2 = `delay-*`. Reverb: 1 = `reverb-*`, 2 = `srvRoom-*`, 3 = `srvHall-*`, 4 = `srvPlate-*`.
- `gm2Chorus-*` / `gm2Reverb-*` members exist in the structs but appear in no path table and lie outside the type ranges (0–2, 0–4). They are unreachable leftovers **[I]**.

### Relationships and cross-references

- `numberTableRef` (8 values) lists the **legal raw values** of a sparse enum. Example: `patchOutputAssign` range 0–13, table `outputAssignXV5050Table` = `0,1,5,6,13`, labelled MFX / L+R / L / R / TONE. The doc says "MFX, A, ---, ---, ---, 1, 2, ---, …, TONE" **[D]**, which agrees. The **XV5050** in the table name points to reuse from the XV-5050 editor **[I]**.
- The UI links each value to its display: `<control><valueRef>` → `<stringTableRef>` (labels) and `<offsetValue>` (−64 for signed 7-bit, −32768 for nibbled effect parameters). These links are captured in `script-schema.json` → `ui_bindings`. They show how the Editor *displays* values, and are evidence rather than hardware facts.
- `internalWaveNameTableA` (l.16202, 313 wave names) is not referenced by any control. `A8EE.exe` loads it by the constructed name `internalWaveNameTable%c` for the `a8eWaveIndexSelect` control (which has `waveGroupType`/`waveGroupID`/`waveNumberL/R` refs; "INTERNAL", `%04d %s` strings in the exe). Wave number *N* ↔ entry *N−1* **[I]**.
- `midiStruct ms` is a built-in channel-message model, used as `ms.ch[n].note` by the on-screen keyboard. It is not SysEx.

## 3. The address system (Task 2)

**Conclusion: the `fm` and `cm` addresses are Roland DT1/RQ1 SysEx addresses. They are not byte offsets, indices, or little-endian values.**

Evidence:
1. **[F]** `<midiOut><name>AX-Synth</name><modelID>00 00 3C</modelID><rootStruct>fm</rootStruct><rootStruct>cm</rootStruct>` ties both trees to a MIDI port with model ID `00 00 3C`.
2. **[D]** The official MIDI Implementation gives model ID `00H 00H 3CH` and the map `01 00 00 00` Setup, `02 00 00 00` System (+`00 40 00` Controller), `1F 00 00 00` Temporary Patch (+`00 02 00` MFX, `04 00` Chorus, `06 00` Reverb, `10 00` TMT, `20/22/24/26 00` Tone 1–4). This is identical to the script.
3. **[F+D]** [`generated/crosscheck-midi-implementation.md`](generated/crosscheck-midi-implementation.md) checks every parameter row in the doc (515 rows) against the script. Offset, nibbled-or-not, and range agree everywhere except for 3 ranges that look like doc typos and one missing parameter (below).
4. **[F]** `A8EE.exe` contains `FKoaSendDt1`, `FKoaSendRq1`, `FKoaRequestRq1Dt1` and the format `address=%08lX %08lX`.

How to read the address strings:
- Each token is one **7-bit byte, MSB first**. Shorter strings are right-aligned (implied leading zeros). Setup's `<address>12</address>` = doc `00 12`, and `00 04` in SystemCommon = doc offset `00 04`.
- Absolute address = parent base + child offset, **added base-128**. Across all 1,952 resolved values, plain byte-wise concatenation gives the same result as base-128 addition except in the one anomaly below (`address_carry_events` in the JSON).
- `<size>` on a **leaf** struct = byte count (in 7-bit notation: `01 1A` = 154). On a **node** struct it is the address extent (`Patch` size `27 1A` = end of Tone 4). `FileModel` size `1F 01 00 00` = end of the patch area.
- `vs` (ViewState) also starts at `00 00 00 00`, but it is not a MIDI root. It is a separate, Editor-internal address space.

**Anomaly [F]:** `stepPitchShifter-bal` / `-level` have `<address>00 81</address>` / `00 85`, and bytes above 0x7F are illegal in SysEx. The generic `mfxParameter29/30` sit at `01 01` / `01 05`, which the doc agrees with. Decoding leniently in base 128 (`0×128 + 0x81 = 129` = `01 01`) gives the doc address. The author probably did hex arithmetic `7D + 4` **[I]**. **Settled 2026-09-23 [F]:** the live capture (`captures/live/03-steppitch.txt`, [live-capture-analysis.md](live-capture-analysis.md) §2) shows the Editor sending Balance/Level to `1F 00 03 01`/`1F 00 03 05`. So the Koa engine resolves the script's addresses base-128 exactly as our extractor does, and the anomaly is harmless.

**Discrepancy [F vs D]:** SystemController. The doc says Total Size `00 00 00 50` and lists `00 4F` "Portament Mode (SWITCH/HOLD)". The script size is `4F` and has no such value, and `InitialData.a8e` holds 79 bytes. **Update:** the Owner's Manual (p.24) describes exactly this setting, the SuperNATURAL Portamento mode "Hld"/"SUt", as a system setting remembered after power-off. So the hardware has it, and the doc's size `50` is most likely right; the Editor script just doesn't expose it. Confirm with an RQ1 of size `50`.

## 4. Data types (Task 3)

The type grammar is **`int<W>x<B>`: W wire bytes, each carrying B low-order bits, most significant group first.**

- **[D]** The MIDI Implementation, p.15: "*Data marked 'nibbled' is expressed in hexadecimal in 4-bit units … 0a 0bH has the value of a × 16 + b*". Every `#`-marked (nibbled) doc row maps to an `int?x4` script value, and every other row maps to `int1x7` or `string`.
- **[F]** `A8EE.exe` knows exactly: `string int4x4 int3x4 int2x4 int5x7 int3x7 int2x7 int1x7`. The parser enforces size = W (`Value size must be %02X`); all 1,539 values comply.
- **[F]** `InitialData.a8e`: `masterTune` default 1024 is stored as `00 04 00 00`, and the MFX zero point 32768 as `08 00 00 00`.
- **[3P]** `github.com/teemow/midi-device` (derived from decompiled BOSS TONE STUDIO JS): "*int<W>x<B> splits the value into W big-endian groups of B bits, one group per wire byte (low bits)*". Roland still uses the same vocabulary years later.

| Type | Wire bytes | Value bits | Count | Where | Notes |
|---|---|---|---|---|---|
| `int1x7` | 1 | 7 (0–127) | 372 | everywhere | Plain SysEx data byte |
| `int2x4` | 2 | 8 (0–255) | 4 | `toneDelayTime`, `lfoRate[0/1]` (0–127), PatchCommon `reserve1F` (20–250, default 120) | Doc marks the first three `#` with `0000 aaaa 0000 bbbb`. `reserve1F`'s 20–250 range looks like tempo BPM **[I]** |
| `int4x4` | 4 | 16 (0–65535) | 1,157 | `masterTune` (24–2024), `waveGroupID`/`waveNumberL`/`waveNumberR` (0–16384), all effect params | Effect params are biased: raw 32768 = 0 (doc 12768–52768 ↔ −20000…+20000). UI `offsetValue −32768` |
| `int5x7` | 5 | 35 | 4 | `EntityNameList` (vs only) | Editor-internal patch list; never on the wire |
| `string` | n | ASCII 32–127 | 2 | `patchName` (12, space padded), `vs.midiMessage` (06 00 = 768, UI only) | Doc: Patch Name 1–12, `(32~127) [ASCII]` |
| `int2x7`, `int3x7`, `int3x4` | – | – | 0 | – | Known to the exe, unused by this script |

Signed values are **not** a separate type. They are stored offset: 64 = 0 for 7-bit (e.g. coarse tune 16–112 ↔ −48…+48), 32768 = 0 for nibbled effect params. The Editor applies `offsetValue` only for display.

## 5. MIDI / SysEx / file references found in the script

- **MIDI**: `midiIn`/`midiOut` "AX-Synth" (model ID, roots `fm`,`cm`, `midiStructRef ms`, `midiMessageValueRef vs.midiMessage.midiMessage`), "Through" port pair; the keyboard control (`ms.ch[…].note`); `receiveProgramChange`, `receiveBankSelect`, `kbdPatchRxTxChannel`, control sources `CC01…CC95` (stringTable `controlSourceTable`).
- **SysEx**: not named explicitly in the script. The model ID plus DT1/RQ1 classes in the exe are the link.
- **Banks/patches**: Setup `kbdPatchBankSelectMsb/Lsb/ProgramNumber` (doc: MSB 87 Regular/Special, 66 SuperNATURAL); `vs.patchNameList` (the Editor's patch list). ~~fed by `cm` name-information requests~~: the live WRITE capture shows the Editor reading a User slot's name by **plain RQ1 of `patchName` at `30 nn 00 00`** **[F]** ([live-capture-analysis.md](live-capture-analysis.md) §5).
- **Files**: none in the script. The exe names `InitialData.a8e`, `ViewState.txt`, `Untitled.mid`, `/Script/Script.xml`.
