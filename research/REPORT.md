# AX-Synth data model: research report (phase 1)

Scope: how Roland represents an AX-Synth patch, established from Roland's own files. No AI or sound-design code. **Nothing has been sent to the hardware.**

Evidence labels: **[F]** our Roland files · **[D]** official Roland documentation · **[3P]** third party · **[I]** inference.

## Bottom line

`Script.xml` is **the Editor's executable data model**. Its `fm`/`cm` address tree *is* the AX-Synth's SysEx (DT1/RQ1) address space, its types *are* the wire encodings, and Roland's own data files store patches in exactly that encoding. The chain

```
Script.xml  ->  parameter model  ->  bytes  ->  DT1 SysEx (F0 41 10 00 00 3C 12 addr data sum F7)
```

is **direct, with no hidden translation layer**: struct offsets equal SysEx address offsets, and struct images equal DT1 payloads. **Roland's own software confirms this**: the Editor and Librarian "Export SMF" files ([smf-export-analysis.md](smf-export-analysis.md)) contain 2,313 DT1 messages whose payloads are byte-identical to the struct images in `InitialData.a8e`, and our encoder reproduces them byte-for-byte. Of the 813 non-effect-specific parameter instances in `fm`, **807 are independently confirmed** (address, encoding, range) by the official MIDI Implementation. The other 6 are 3 range typos in the doc (one repeated across the 4 Tones). This rests on documents and Roland's files; it has not yet been observed on the hardware. **Since 2026-09-23 it also rests on Roland's live traffic**: every value edit the Editor transmitted through a loopback port equals, byte for byte, what our library builds for that parameter ([live-capture-analysis.md](live-capture-analysis.md), item 15).

## What we know (directly supported)

1. **The address system.** Script addresses are 7-bit, MSB-first Roland addresses. Short forms are right-aligned, parent + child offsets are added base-128, and repeated `<address>` tags define arrays (4 Tones). Setup `01 00 00 00`, System `02 00 00 00`, Temporary Patch `1F 00 00 00` with blocks at `+00 00 00` Common, `02 00` MFX, `04 00` Chorus, `06 00` Reverb, `10 00` TMT, `20/22/24/26 00` Tone 1–4. **[F+D]** Tied to MIDI by `<midiOut>` model ID `00 00 3C` and `rootStruct fm, cm` **[F]**. The official doc gives the same model ID and map **[D]**, and adds User Patches at `30 00 00 00 + n·(00 01 00 00)`, n = 0…255.
2. **Types.** `int<W>x<B>` = W wire bytes of B low bits each, MSB first. Used here: `int1x7` (372), `int4x4` (1,157, "nibbled" in the doc), `int2x4` (4), `int5x7` (4, UI-only), `string` (ASCII). The exe knows exactly this vocabulary and enforces size = W **[F]**. The doc's nibble definition agrees **[D]**, and BOSS TONE STUDIO code uses the same grammar **[3P]**. Signed values are stored offset (64 = 0; 32768 = 0 for effect parameters).
3. **Cross-check.** All 515 parameter rows in the MIDI Implementation were compared with the script ([generated/crosscheck-midi-implementation.md](generated/crosscheck-midi-implementation.md)). Offsets, nibble/7-bit encoding, ranges and block sizes agree, except for 3 range typos in the doc and one missing parameter (item 3 of "remains unknown").
4. **Effect unions.** MFX (79 types), Chorus (3) and Reverb (5) parameters are unions over generic 4-byte slots. `*ValuePathTable` defines which named members apply to which type, e.g. MFX type 1 EQUALIZER → `equalizer-loGain` = slot 2 = `1F 00 02 15`. Type names come from `A8EE.exe` **[F]**. **The official doc does not contain this mapping** (it only says "MFX Parameter 1–32").
5. **Display semantics.** 526 parameters have enum labels and 986 have display offsets, taken from the UI bindings and labelled "ui-derived". Sparse enums use `numberTable`s, e.g. output assign `0,1,5,6,13`. The script ships **313 internal wave names** (`internalWaveNameTableA`) and MFX categories.
6. **Data files.** `.a8e` (Koa data file) = 256-byte header plus raw images of every leaf struct under `fm`. `.a8l` (Librarian) = 160-byte header, u32 BE count, then per patch a u32 record length and length-prefixed blocks (same container as Juno-G/Fantom-X librarians **[3P]**). Both hold the **same INIT PATCH**, equal to the script defaults, in DT1 encoding. **Neither contains SysEx framing or factory presets.**
7. **Framework.** Roland's "Koa" editor engine, shared with XV-5050/Fantom-X/Juno-class editors. Evidence: control types `xvToneSelectButton`, `fantomXLfoControl`; `…XV5050Table`; and a `CommunicationModel` with performance, rhythm and sample fields the AX-Synth lacks **[F]**.
8. **Editor vs Librarian targets [D manuals].** The Editor reads and writes the **Temporary Area**. The Librarian reads and writes the **256 User patches** (Bank 1–8 × 1–32), and its Audition sends to Temporary. Both can **Export/Import SMF**.
9. **Whole-patch wire format [F, dumps/].** A patch is sent as **9 DT1s, one per block** (Common, MFX, Chorus, Reverb, TMT, Tone 1–4), each carrying the full struct image (up to 154 data bytes, crossing 7-bit address boundaries), with device ID `10`. The Editor sends to `1F 00 00 00`. The Librarian sends User patch *n* to `30 00 00 00 + n × 00 01 00 00` using plain DT1, with no `0F` command. Export pacing = wire time at 31,250 baud + 20 ms per message (fits all 2,312 gaps). Implemented and tested as `sysex.patch_messages()`, `user_patch_address()`, `roland_export_delay_ticks()`.

10. **Independent ground truth [3P, patches/].** Two forum-shared `.a8e` patches, whose author described the changes (pitch bend −24/+12, mono, velocity 1–69 layer on Tone 4, CC70 "feedback" routing, beam on CC70, a +24 layer), decode to exactly those values with our model. Details in [third-party-patches-analysis.md](third-party-patches-analysis.md). The same data showed that matrix-source and beam CC tables use **different index rules** (raw = CC number vs. no CC32 slot), and that the script's range for SystemController `reserve04` is wrong (real value 100).

11. **Roland erratum [D, `docs/AX-Synth_Erratum2.pdf`].** The [VOLUME] knob is analog and **transmits no CC07**. This also contradicts the MIDI Implementation, which lists Volume (CC7) under "Data transmission" (p.5; `generated/midi-implementation.pdf.txt` l.772). There's no effect on SysEx, addresses or patch data. The same page confirms the D Beam transmits "CC01~31, CC33~95" (no CC32), the beam-table indexing found in item 10. Practical rule: don't expect volume-knob CCs from the synth, and don't use CC07 from the synth as a signal. Receiving CC07 is not affected by the erratum.

12. **Owner's Manual [D, `docs/AX-Synth_OM.pdf`], see [owners-manual-analysis.md](owners-manual-analysis.md):**
    - The **factory Tone list**: 256 regular Tones in 8 families × 32 (bank 87/0 and 87/1, PC 1–128), plus 4 SuperNATURAL (66/0) and 4 SPECIAL (87/64), which aren't editable. Extracted to `generated/factory-tones.{json,csv}` and available through `axsynth.factory`.
    - The forum patches are factory **SearingGtr 1** (Lead Guitar #1, 87/0/PC 97 ↔ Setup program 96).
    - The instrument has a **3-character LED display** and no patch editing on the device.
    - A synth-initiated **Bulk Dump** (~16 min), **factory reset** and **firmware display** are available via power-on key combinations.
    - The real-time controllers are the mod bar (CC01), the aftertouch *knob* (the keys send no aftertouch), the ribbon (bend), the D-Beam (pitch / filter / CC01–95 without 32), portamento and hold.
    - The Implementation Chart lists CC71–75, 91 and 93 as received.
13. **Parameter knowledge base [D].** The **Editor manual** we already had explains every parameter (p.9–43) and every effect type (Effects List p.44–78). No document contains a wave list; `internalWaveNameTableA` in Script.xml remains the only source.
14. **Knowledge base built** (`knowledge/`, see its README).
    - **Contents:** Roland's explanation of every parameter and all 78 MFX + 2 chorus + 4 reverb types, plus 24 concepts: structure types, LFO fade modes, TMT, Matrix Control, STEP RESET, 3D effects, controllers and more.
    - **Format:** each entry has page references and exact data-model links. The TOML sources are validated by `tools/build_knowledge.py`, which also generates `knowledge.json` (joined with addresses, raw ranges, defaults and enum labels) and `knowledge.md`.
    - **Validation findings:**
      - The effect names in the manual equal the A8EE.exe names for all 78 MFX types.
      - Every non-reserved data-model value has an entry.
      - **172 effect members are tempo-sync variants (`…Sync`/`…Note`) that the AX-Synth manual never documents** [F]. They are likely inherited from the Fantom-X engine.
      - The `#` (real-time controllable) flags are recorded per parameter.
15. **Live Editor/Librarian output [F, `captures/live/`, 2026-09-23]**, see [live-capture-analysis.md](live-capture-analysis.md). 53 messages were captured through loopMIDI + MIDI-OX with no synth attached. All are well formed with device `10`, and all are decoded by `tools/midiox_log.py`.
    - **Value edits = one DT1 per value**, carrying only that value's bytes (1 B cutoff, 4 B nibbled MFX/masterTune, the whole 12 B name). They are sent immediately, with no handshake and no pacing (gaps down to 1 ms). Reproduced byte-for-byte by `build_dt1` + schema.
    - **`00 81`/`00 85` settled:** the Editor sends STEP PITCH SHIFTER Balance/Level to `1F 00 03 01`/`05`, i.e. base-128, exactly our resolved addresses.
    - **Effect type change** = the whole 145-byte MFX block, with every member of the new type at its Script.xml default (rebuilt from the schema alone in the test), then the type byte again.
    - **READ, SYNC, WRITE and the Librarian's Read Selected start with a Universal Identity Request** `F0 7E 10 06 01 F7` (device 10). With no reply within ~3.0 s, the Editor retries once, then shows "Unable to read/write data." and sends nothing more.
    - **WRITE first reads User Patch 1-1's name with a plain RQ1** (`30 00 00 00`, size 12). Patch names are therefore read on the documented User area, not via `cm` (replaces an earlier inference). No `0F` write command was reached.
16. **Sound-design knowledge [3P → I, 2026-09-24]** (`knowledge/sound-design/`, `knowledge/sound_*.toml`). All 63 parts of Gordon Reid's *Synth Secrets* (SOS 1999–2004) were read and digested one by one, then condensed into 27 principles, 37 descriptors (words → acoustic cause → AX-Synth moves) and 35 recipes (brass, strings, winds, organ, piano, guitars, bass, drums, percussion, bells, leads, pads, choir). Every reference is validated against the KB, the wave table, the MFX list and the factory Tone list. The mappings onto the AX-Synth are inference, not hardware-verified. Relevant findings for this instrument:
    - the PWM sound can be built from two saw tones, one with a tiny pitch LFO (SS47)
    - the Matrix sources AFTERTOUCH (the knob), CC01 and the D-Beam CC routed to LEVEL/CUTOFF/LFO depth reproduce the "hand-controlled" articulation Reid found most realistic (SS50/51)
    - Structure ring-mod on both tone pairs matches the "pairs of modulated squares" cymbal recipe (SS39)
    - the AX-Synth lacks oscillator sync, audio-rate LFOs and an audio input; the substitutes are documented
17. **The user's hardware [user report, `captures/setup.md`, 2026-09-25].**
    - USB directly to Windows 10, driver mode **"Gen"** (OS generic driver), and one port pair named **"Roland AX-Synth"**. The Editor manual p.8 [D] warns that the Editor and Librarian may not both work over the generic driver, so captures go through MIDI-OX as the only program holding the port (NEXT-STEPS 3.0).
    - **Firmware 2.01.** Every document we have is older: OM Oct 2009, MIDI Implementation v1.00 Jan 2010, Editor/Librarian v1.00. Roland's support page offers no firmware update and no newer Editor (checked 2026-09-25), so 2.01 is probably the factory-installed version of later units [I]. What it changed is undocumented.
    - The unit is second hand, and some User patches may not be factory. The backup has to be diffed against the factory list before it is used as the factory corpus.
    - `sysex.parse_identity_reply()` and `midiox_log.py` decode the Identity Reply and report every field that differs from the doc (the expected candidate is the software revision `00 01 00 00`).

## What we strongly suspect (evidence-backed, unverified)

- **The 256 factory Tones are the 256 User patches**: Tone (family *f*, variation *v*) = User patch *n* = 32·*f* + *v* − 1 = LSB·128 + PC − 1, at address `30 00 00 00 + n·00 01 00 00`, Librarian slot *f*-*v*. Supported by the manuals (8 × 32 = Bank 1–8 × Number 1–32, factory reset restores edits) and by the forum patch's Setup; confirm with a Librarian Read All.
- **SystemController really is `0x50` bytes**, as in the doc. The Owner's Manual describes the SuperNATURAL Portamento mode Hld/SUt as a remembered system setting, which is the doc's `00 4F` "Portament Mode". The Editor's script (size `4F`) just omits it.

- The hardware accepts Roland's own stream: DT1 to `30 nn …` stores User patch *nn* (that's what the Librarian export would do when played back). Its replies to RQ1 will match the `.a8l`/export blocks. (The software side is now confirmed; the hardware side isn't.)
- `cm.command.writeRequest/writeStart/writeComplete` at `0F 00 10 00–02` belong only to the Editor's live **WRITE (Temporary → User)** operation. They don't appear in either export, and the live WRITE capture stopped (at the unanswered Identity Request) before reaching them. ~~The Editor reads patch-name lists through `cm` "…Information" addresses~~: **refuted for the WRITE dialog** by the live capture, where names are read by RQ1 on `30 nn 00 00` (item 15). The Editor probably reads names for all 256 slots that way when the synth answers.
- `gm2Chorus-*` (7) / `gm2Reverb-*` (5) are dead leftovers: in no path table, and outside the chorus/reverb type ranges.
- Changing the chorus or reverb type behaves like the captured MFX type change: whole block, members at their Script.xml defaults. (Only MFX was captured.)
- System-area DT1s (the Editor sends Master Tune etc. live to `02 00 …`) are volatile until a "System Write" (Editor manual p.9).
- PatchCommon `reserve1F` (int2x4, 20–250, default 120) is a tempo.
- Wave number *N* ↔ `internalWaveNameTableA[N−1]`. Well supported by the third-party patches: 61 → "Overdrive Gt" in a guitar patch, and 220 → "Sine" on filter-off pure-tone layers.
- An `.a8l` record's final 4 bytes relate to Librarian memo fields.
- Script.xml files from sibling Koa editors would parse with the same tools.

## What remains unknown

| Area | Open question |
|---|---|
| SysEx | Whether the synth accepts RQ1 for a whole block and how it packetizes replies (doc: ≤256-byte packets ~20 ms apart); the *minimum* DT1 spacing it tolerates. Roland's software uses device ID `10`, 31,250-baud time + 20 ms between whole blocks in exports, and **no pacing at all** for live value edits (gaps down to 1 ms) |
| Identity Reply | Which fields of the reply the Editor checks (the doc gives `F0 7E 10 06 02 41 3C 02 00 00 00 01 00 00 F7`). This gates READ/SYNC/WRITE. The user's unit runs **firmware 2.01**, so its software revision probably differs from the doc; whether Editor v1.00 accepts it is the first thing the MIDI-OX capture shows |
| Firmware 2.01 | What changed since the v1.00-era documents: factory sounds (the OM p.3 warns of "newer sounds"), block sizes or new parameters. Settled by the backup names and RQ1 reply lengths vs `Schema.struct_size` |
| SystemController | Doc size `50` (includes `00 4F` Portamento Mode, which the Owner's Manual confirms exists as the SuperNATURAL Hld/SUt setting) vs script/`.a8e` size `4F`. An RQ1 of size `50` settles it |
| Undocumented storage | Where FAVORITE memories (2×8: Tone + volume + reverb send), USB driver mode (Gen/Uen) and sleep interval are stored. A synth-initiated Bulk Dump capture should reveal these areas |
| Stored vs printed names | Exact 12-character stored names of the factory Tones ("Vintage Org 1" is 13 characters as printed) |
| Checksums | Formula confirmed on 2,313 messages produced by Roland's software; not yet on a message from the synth itself |
| Patch storage | Whether the synth commits a DT1 to `30 nn …` to flash immediately (the Librarian export implies yes), and the Editor's live WRITE handshake (`0F 00 10 0x` payloads). **Do not experiment with writes yet** |
| .a8l | Trailing 4 bytes per record (not transmitted in exports; memo hypothesis) |
| Serialization | Whether the hardware's reply includes reserved bytes identical to `.a8e`; `reserve1F` = 0 lies outside the script's range |
| MIDI comms | Which RQ1s the Editor sends on READ/SYNC after a successful Identity exchange. The loopback capture proved these are gated behind the Identity Reply; names are read by RQ1 on `30 nn 00 00` (item 15). **Needs the synth, observed via MIDI-OX in the middle** |

## Most valuable discoveries (ranked)

1. **`Script.xml` data model + `<midiOut>` binding.** It is the machine-readable AX-Synth SysEx map with names, types, ranges and defaults. Extracted to [script-schema.json](script-schema.json).
2. **`docs/AX Synth docs.pdf` (MIDI Implementation).** Independent confirmation, plus the checksum, User-patch addresses and packet rules.
3. **`mfxValuePathTable` / `chorus…` / `reverb…` + MFX names in `A8EE.exe`.** Per-effect parameter meaning, which is essential for sound design and exists nowhere else.
4. **The display tables** (enum labels, offsets, 313 wave names). What a musician or an AI needs in order to reason about values.
5. **`InitialData.a8e`/`.a8l`.** A verified reference INIT patch and the library container for importing and exporting whole banks.

## Next experiment (single most useful): read-only Temporary-patch dump

**Goal:** confirm on real hardware that addresses, sizes, encoding, checksums and enum mapping match the model, with **zero risk of changing synth memory** (RQ1 only asks the synth to reply).

1. On the AX-Synth, select a known factory Tone by family button + variation number, e.g. LEAD GUITAR variation 1. The synth's 3-character display can't show names; the expected name comes from `generated/factory-tones.csv` ("SearingGtr 1").
2. Send `research/generated/experiment-rq1-temporary-patch.syx` (10 RQ1s: 9 patch blocks + SystemController with size 50) using a SysEx utility such as MIDI-OX. Record all incoming SysEx to `reply.syx`.
3. `py -3 research/tools/dump_experiment.py decode reply.syx`
   Expect: 9–10 DT1 replies with `checksum_ok=True`, patchName = the Tone-list name, labels that make sense (e.g. `tvfFilterType = LPF`), and the SystemController reply length answering the 4F/50 question. For SearingGtr 1, the non-edited parts should also equal the forum patches' unchanged values.
4. Change **one** value without storing anything. Use the synth's own Volume edit ([SHIFT] + the lit TONE button → "UOl", change the value; Owner's Manual p.26) but **don't press WRITE**. Then re-send, re-record and diff. That shows where the on-device volume edit lives (prediction: PatchCommon `patchLevel`, `1F 00 00 0E`). Alternatively, change one value in the Editor (e.g. Tone 1 cutoff), which should change `1F 00 20 49`.

**Done without hardware (2026-09-23):** Export SMF from both apps. See [smf-export-analysis.md](smf-export-analysis.md). It confirmed the block format, User-patch addressing, checksums and pacing, but it can't show live traffic.

**Done without hardware (2026-09-23): live loopback capture** (loopMIDI + MIDI-OX; `captures/live/`, [live-capture-analysis.md](live-capture-analysis.md), item 15). It settled single-parameter addressing (incl. `00 81`), effect-type-change behaviour and name reads. It also showed that **everything else (READ/SYNC RQ1s, the write handshake) waits for the synth's Identity Reply**, so zero-hardware capture is exhausted.

**Next capture, with the synth: MIDI-OX as a man-in-the-middle.** Editor/Librarian → loopMIDI port A → MIDI-OX → AX-Synth, and AX-Synth → MIDI-OX → loopMIDI port B → Editor/Librarian. MIDI-OX logs both directions in one log, and `midiox_log.py` prints the IN PORT column to tell them apart. Doing the Librarian **Read All** (backup, NEXT-STEPS 3.1) and the Editor **READ** this way shows the Identity Reply, the RQ1 sequence and the synth's reply packetization, all from read-only operations. WRITE stays off-limits until a verified backup exists and the user decides to test it.

**Useful follow-up once the synth is connected (non-destructive):** send `research/generated/guitar01-temporary.syx`, a real patch encoded by our tools for the Temporary Patch only. It should sound like a metal lead, with the velocity layers and CC70 behaviour the author described. The synth can't show the name, so confirm it with the Editor's READ ("SearingGtr 1") or an RQ1 dump. Alternatively play `dumps/AX-Synth Editor clean export.mid` to the synth, which targets only the volatile Temporary Patch (the name read back should be "INIT PATCH"). ⚠ **Never** play the Librarian export without a verified backup: it would overwrite all 256 User patches. If that happens by accident, factory reset (Owner's Manual p.34) restores the factory Tones, but not your own edits.

**Synth-initiated capture (read-only for the synth):** record the **Bulk Dump** (power-on with VARIATION [−]+[+]+TONE [6], then FAVORITE [B]; ~16 min; Owner's Manual p.29) in MIDI-OX. It's a full backup *and* shows the synth's own DT1 format: addresses, packet sizes and pacing, plus the undocumented FAVORITE/system areas.

## Files produced

| Path | What |
|---|---|
| `CLAUDE.md`, `AGENTS.md` | Project context for LLM agents: rules, environment, repository map, pipeline, API, core facts |
| `research/README.md` | Index: question → file; generated artifact → producer |
| `research/script-analysis.md` | Tasks 1–3, 7: structure, address system, type table |
| `research/initialdata-analysis.md` | Task 4: `.a8e`/`.a8l` formats |
| `research/roland-installation-inventory.md` | Task 5 |
| `research/online-research.md` | Task 6 |
| `research/smf-export-analysis.md` | Editor/Librarian "Export SMF" captures in `dumps/` |
| `research/live-capture-analysis.md` | Editor/Librarian live MIDI output via loopback (`captures/live/`): value-edit DT1s, effect type change, Identity Request gating, name RQ1 |
| `research/third-party-patches-analysis.md` | Forum-shared patches in `patches/`, checked against the author's description |
| `research/owners-manual-analysis.md` | Owner's Manual: Tone list, UI limits, maintenance functions, controllers, design implications, terminology |
| `research/generated/factory-tones.{json,csv}` | 264 factory Tones (`tools/extract_tone_list.py`); `src/axsynth/factory.py` |
| `knowledge/sound-design/`, `knowledge/sound_design.toml`, `knowledge/sound_recipes.toml` | Sound-design knowledge from *Synth Secrets* (63 digests, 27 principles, 37 descriptors, 35 recipes); `tools/fetch_synth_secrets.py` (articles → git-ignored `reference/synth-secrets/`) |
| `knowledge/` | Knowledge base: meaning of every parameter/effect (TOML sources + generated `knowledge.json`/`knowledge.md`); `tools/build_knowledge.py`; `src/axsynth/knowledge.py` |
| `research/generated/guitar{,01}-temporary.syx` | Those patches as Temporary-Patch DT1s (not sent) |
| `research/script-schema.json` | Complete extraction (every element + source line), resolved absolute addresses, unions, tables, UI bindings |
| `research/generated/parameters.{csv,json}` | Parameter database: 1,934 `fm`+`cm` parameters with address, type, range, default, enum, effect, source line, confidence |
| `research/generated/crosscheck-midi-implementation.md`, `crosscheck.json` | Script vs official doc, row by row |
| `research/generated/*.strings.txt`, `*.pdf.txt`, `inventory.json` | EXE strings, PDF text, hashes |
| `research/generated/experiment-rq1-temporary-patch.syx` | Ready-to-send read-only requests (not sent) |
| `research/tools/` | `extract_script_schema.py`, `crosscheck_midi_impl.py`, `extract_tone_list.py`, `build_knowledge.py`, `a8_files.py`, `describe_a8.py`, `build_parameter_db.py`, `dump_experiment.py`, `smf_inspect.py`, `midiox_log.py`, `exe_strings.py`, `inventory.py`, `pdf2txt.py` |
| `dumps/` | Roland "Export SMF" captures (test fixtures) |
| `patches/` | Third-party `.a8e` patches (test fixtures) |
| `src/axsynth/schema.py` | Typed model: `Schema`, `Parameter`, `decode_value`/`encode_value`, address helpers |
| `src/axsynth/sysex.py` | Checksum, DT1/RQ1/Identity Request builders, whole-patch encoder matching Roland's export, parser, `.syx`/SMF readers (no MIDI I/O) |
| `captures/live/` | User's MIDI-OX logs of the Editor/Librarian live output (step 2) + `notes.md` |
| `tests/test_schema.py` | 49 evidence tests (`py -3 -m unittest discover -s tests`) |

Regenerate: `extract_script_schema.py` → `crosscheck_midi_impl.py` → `build_parameter_db.py` (the `.venv` with `pypdf` is only needed for `pdf2txt.py`).
