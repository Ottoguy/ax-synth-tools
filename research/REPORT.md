# AX-Synth data model: research report (phase 1)

Scope: how Roland represents an AX-Synth patch, established from Roland's own files. No AI or sound-design code. **Nothing that writes has been sent by our tools.** Since 2026-09-26 the user's Roland Editor/Librarian have read from the synth, one Editor SYNC was sent (Temporary + Setup/System only), the synth sent its Bulk Dump, and the user sent our **read-only** RQ1 file (`captures/`).

Evidence labels: **[F]** our Roland files · **[D]** official Roland documentation · **[3P]** third party · **[I]** inference.

## Bottom line

`Script.xml` is **the Editor's executable data model**. Its `fm`/`cm` address tree *is* the AX-Synth's SysEx (DT1/RQ1) address space, its types *are* the wire encodings, and Roland's own data files store patches in exactly that encoding. The chain

```
Script.xml  ->  parameter model  ->  bytes  ->  DT1 SysEx (F0 41 10 00 00 3C 12 addr data sum F7)
```

is **direct, with no hidden translation layer**: struct offsets equal SysEx address offsets, and struct images equal DT1 payloads. **Roland's own software confirms this**: the Editor and Librarian "Export SMF" files ([smf-export-analysis.md](smf-export-analysis.md)) contain 2,313 DT1 messages whose payloads are byte-identical to the struct images in `InitialData.a8e`, and our encoder reproduces them byte-for-byte. Of the 813 non-effect-specific parameter instances in `fm`, **807 are independently confirmed** (address, encoding, range) by the official MIDI Implementation. The other 6 are 3 range typos in the doc (one repeated across the 4 Tones). This rests on documents and Roland's files; it has not yet been observed on the hardware. **Since 2026-09-23 it also rests on Roland's live traffic**: every value edit the Editor transmitted through a loopback port equals, byte for byte, what our library builds for that parameter ([live-capture-analysis.md](live-capture-analysis.md), item 15). **Since 2026-09-26 it rests on the synth itself**: its RQ1 replies have exactly the model's block sizes, and a backup of all 256 User patches decodes into the factory Tone list with the expected waves ([mitm-capture-analysis.md](mitm-capture-analysis.md), item 18).

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

18. **First conversation with the synth + full backup [F, `captures/mitm/`, `captures/backup/`, 2026-09-26]**, see [mitm-capture-analysis.md](mitm-capture-analysis.md). MIDI-OX sat between Editor/Librarian and the synth, logging both directions.
    - **Identity Reply = the doc, byte for byte**, including revision `00 01 00 00` on firmware 2.01. Editor/Librarian v1.00 accept it.
    - **RQ1 → one DT1 with the same address and exactly the requested size**, 2–47 ms later, not packetized (all blocks ≤154 B). Checksums from the synth are valid.
    - **Librarian Read Selected:** Setup bank (RQ1 `01 00 00 04`, 2 B), then the 9 patch blocks of `30 nn …` in `PATCH_BLOCKS` order. **Editor READ:** Setup bank bytes, Setup, System Common, System Controller (size `4F`), then the 9 Temporary blocks. **Editor SYNC:** 12 DT1s (Setup, System Common, System Controller, 9 Temporary blocks) with the Editor's current values and no reads, contrary to the manual's "name lists are read". So SYNC overwrites the synth's system settings.
    - The Temporary patch, Setup and System read back were **identical to `InitialData.a8e`** ("INIT PATCH"), although the panel's Tone was AX Saw Lead. Something had sent the Editor's blank document before the capture [I]; NEXT-STEPS 3.1b re-checks this.
    - **Backup:** 2,304 DT1s, 256 complete patches, same layout as Roland's Librarian export. `backup_summary.py` → `generated/user-patches.{csv,json}`.
    - **Confirmed (was strong inference):** User patch *n* = factory Tone *n* (254/256 stored names equal the Owner's Manual; 3-10/3-11 are stored as "Reso Bs 1"/"Reso Bs 2", cause unknown), and wave *N* = `internalWaveNameTableA[N−1]` (Soprano Sax → "Sop Sax 2 p/mf/f", Folk Gtr → "Ac.Gtr mp/mf/ff", SearingGtr 1 → "Overdrive Gt"…).
    - **Forum patches vs their factory original** (User patch 96, `describe_a8.py backup.mid#96 patches/guitar01.a8e`): the author's claims are exact parameter diffs (bend 2/12 → 12/24, matrix 3 source CC04 → CC70 → cutoff + attack time, new +12 sine Tone 4 at velocity ≤69, factory +7 sine Tone 2 retuned to +24).
    - **`patchCategory`:** 27 values grouped by instrument (11 = dist. guitar, 9 = ac. guitar, 7 = Musette, 8 = Harmonica, 22/23 = leads, 28/29 = pads…). The numbers are [F]; the names are Roland's XV/Fantom category list [3P, unverified].

19. **The synth's own Bulk Dump, decoded + our first RQ1s [F, `captures/bulkdump/`, `captures/rq1/`, 2026-09-26]**, see [bulkdump-analysis.md](bulkdump-analysis.md).
    - The Bulk Dump is a **raw memory image**: DT1 with 1-byte model ID `7F`, 7-in-8 packed, 1,704,000 bytes, 16,230 messages with valid checksums, trailer "Roland RE409DUMP VER.1.00". It contains the System area, the **16 FAVORITE memories** (bank/PC + volume + reverb send, 40 bits each) and **256 User patch records of 664 bytes**.
    - The patch records are **every data-model value bit-packed in Script.xml order at the smallest width for its range** (unsigned as-is, centred values offset-binary). `bulkdump.py solve` derived the layout from the backup; 690/783 fields are verified by varying values.
    - **All 2,304 DT1 blocks rebuilt from the dump are byte-identical to the Librarian backup.** So the Librarian's Read All = the synth's storage, and **the Script.xml model covers every stored patch byte**. The only extras are 146 hidden bits per record, identical except in 1-1: rewritten over MIDI once? [I].
    - **Our own RQ1 file works:** 10 RQ1s → 10 exact DT1s. **System Controller = 0x50 bytes on the hardware** (doc right, script 0x4F short; `00 4F` = 1). The **Temporary patch follows the panel selection** (byte-identical to User patch 96 with LEAD GUITAR 1 selected).
    - **The panel volume edit ("UOl") is a FAVORITE-memory value**, not a patch or System Controller value (Owner's Manual p.26; replies before and after were byte-identical). The prediction `patchLevel` is refuted.
    - The stored System settings equal the Editor's defaults (System Common decoded in the dump; System Controller after power-cycling = `InitialData.a8e`).

## What we strongly suspect (evidence-backed, unverified)


- The hardware accepts Roland's own stream: DT1 to `30 nn …` stores User patch *nn* (that's what the Librarian export would do when played back). (Its RQ1 replies do match the export block format: item 18.)
- `cm.command.writeRequest/writeStart/writeComplete` at `0F 00 10 00–02` belong only to the Editor's live **WRITE (Temporary → User)** operation. They don't appear in either export, and the live WRITE capture stopped (at the unanswered Identity Request) before reaching them. ~~The Editor reads patch-name lists through `cm` "…Information" addresses~~: **refuted for the WRITE dialog** by the live capture, where names are read by RQ1 on `30 nn 00 00` (item 15). Neither READ nor SYNC read any names in the MITM capture (item 18); the name list is probably read only by the WRITE dialog.
- `gm2Chorus-*` (7) / `gm2Reverb-*` (5) are dead leftovers: in no path table, and outside the chorus/reverb type ranges.
- Changing the chorus or reverb type behaves like the captured MFX type change: whole block, members at their Script.xml defaults. (Only MFX was captured.)
- System-area DT1s (the Editor sends Master Tune etc. live to `02 00 …`) are volatile until a "System Write" (Editor manual p.9).
- PatchCommon `reserve1F` (int2x4, 20–250, default 120) is a tempo.
- An `.a8l` record's final 4 bytes relate to Librarian memo fields.
- Script.xml files from sibling Koa editors would parse with the same tools.

## What remains unknown

| Area | Open question |
|---|---|
| SysEx | ~~Whether the synth accepts RQ1 for a whole block and how it packetizes replies~~ **settled** (item 18: one DT1 per block). Still open: the *minimum* DT1 spacing it tolerates. Roland's software uses device ID `10`, 31,250-baud time + 20 ms between whole blocks in exports, and **no pacing at all** for live value edits (gaps down to 1 ms) |
| Identity Reply | **Settled** for the user's unit: identical to the doc (item 18). Which fields the Editor checks remains unknown and no longer matters |
| Firmware 2.01 | Nothing visible so far: same Identity Reply, same block sizes, and the factory Tone list matches (item 18). Any change is outside the patch/Setup/System data read so far |
| SystemController | **Settled** (item 19): 0x50 bytes on the hardware; `00 4F` = 1. Open: which value means Hld vs SUt |
| Undocumented storage | FAVORITE memories **found** in the Bulk Dump (item 19). Open: where the USB driver mode and sleep interval sit (bulk-dump system area; RQ1 diff, NEXT-STEPS 3.5), and where the *unsaved* live FAVORITE volume/reverb send is held |
| Stored vs printed names | **Settled** by the backup (`generated/user-patches.csv`), e.g. "Vintage Org1". Open: why 3-10/3-11 are stored as "Reso Bs 1"/"Reso Bs 2" (factory quirk or previous owner) |
| Temporary = INIT | Resolved as far as it matters: the Temporary patch follows the panel (item 19), so INIT had been *sent* before capture 02 (probably a SYNC). Not reproducible from the logs |
| System writes | Whether System DT1s (e.g. from SYNC) persist after power-off. The stored values equal the Editor defaults, which may also be the factory values, so this is undecidable from the data |
| Hidden patch bits | 146 bits per patch record outside the data model (item 19); why 1-1 differs |
| Checksums | **Settled**: also valid on every message from the synth (item 18) |
| Patch storage | Whether the synth commits a DT1 to `30 nn …` to flash immediately (the Librarian export implies yes), and the Editor's live WRITE handshake (`0F 00 10 0x` payloads). **Do not experiment with writes yet** |
| .a8l | Trailing 4 bytes per record (not transmitted in exports; memo hypothesis) |
| Serialization | Whether the hardware's reply includes reserved bytes identical to `.a8e`; `reserve1F` = 0 lies outside the script's range |
| MIDI comms | READ, SYNC and Read Selected are **settled** (item 18). Open: the Librarian Read All sequence (not logged) and the WRITE handshake |

## Most valuable discoveries (ranked)

1. **`Script.xml` data model + `<midiOut>` binding.** It is the machine-readable AX-Synth SysEx map with names, types, ranges and defaults. Extracted to [script-schema.json](script-schema.json).
2. **`docs/AX Synth docs.pdf` (MIDI Implementation).** Independent confirmation, plus the checksum, User-patch addresses and packet rules.
3. **`mfxValuePathTable` / `chorus…` / `reverb…` + MFX names in `A8EE.exe`.** Per-effect parameter meaning, which is essential for sound design and exists nowhere else.
4. **The display tables** (enum labels, offsets, 313 wave names). What a musician or an AI needs in order to reason about values.
5. **`InitialData.a8e`/`.a8l`.** A verified reference INIT patch and the library container for importing and exporting whole banks.

## Next experiment (single most useful): first write to the Temporary patch

**Status 2026-09-26:** reading is solved: Editor/Librarian READ (item 18), our own RQ1 file, and the Bulk Dump (item 19). The chain `model → encoder → DT1 → synth` has been exercised only by Roland's SYNC (12 whole-block DT1s, accepted), never by our bytes.

1. Select LEAD GUITAR 1 (SearingGtr 1) on the synth.
2. MIDI-OX *Send/Receive SysEx*, with a 60 ms delay after each F7: send `research/generated/guitar01-temporary.syx` (9 DT1s to `1F 00 00 00`, built by `dump_experiment.py a8-to-syx patches/guitar01.a8e`).
3. Without switching sounds, send `research/generated/experiment-rq1-temporary-patch.syx` and save `captures/first-write/reply.syx`.
4. Expect: the reply's 9 Temporary blocks = the 9 blocks we sent, byte for byte. The sound audibly differs from SearingGtr 1 in the ways the forum author described (bend 12/24, a soft-note +12 sine, retuned Tone 2). Switching sounds restores SearingGtr 1.

**Then:** a listening test of single-parameter changes (NEXT-STEPS step 4, end), and on the user's go-ahead a Temporary-only "safe sender" (MIDI I/O).

**Done (for the record):**
- 2026-09-23, without hardware: Export SMF ([smf-export-analysis.md](smf-export-analysis.md)) and a live loopback capture ([live-capture-analysis.md](live-capture-analysis.md), item 15).
- 2026-09-26, with the synth:
  - MIDI-OX in the middle, plus a Librarian Read All backup ([mitm-capture-analysis.md](mitm-capture-analysis.md), item 18)
  - the synth's Bulk Dump and our read-only RQ1 file ([bulkdump-analysis.md](bulkdump-analysis.md), item 19)

⚠ **Never** play the Librarian export (`dumps/…Librarian Clean export.mid`) or the user's backups (`captures/backup/*.mid`, `captures/bulkdump/*.syx`) to the synth except as a deliberate restore: they rewrite all 256 User patches. Factory reset (Owner's Manual p.34) restores factory Tones, not user edits.

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
| `research/bulkdump-analysis.md` | The synth's Bulk Dump: wire format (model `7F`, 7-in-8), image map, bit-packed patch records, FAVORITE memories, System Common; step 3.3 RQ1 results |
| `research/tools/bulkdump.py` → `research/generated/bulkdump-layout.json` | Bulk-dump decoder: `info`, `solve` (derive the record layout from a backup), `verify`, `export` (dump → Librarian-style DT1s) |
| `research/generated/experiment-rq1-setup-system.syx` | 3 read-only RQ1s: Setup, System Common, System Controller (0x50); `dump_experiment.py make-system-requests` |
| `research/mitm-capture-analysis.md` | First conversation with the synth (MIDI-OX in the middle) + backup: Identity Reply, RQ1 replies, READ/SYNC sequences, factory mapping and wave numbering confirmed, forum-patch diffs, `patchCategory` |
| `research/tools/backup_summary.py` → `research/generated/user-patches.{csv,json}` | Every User patch in a backup: slot, factory vs stored name, category, 4 tones (switch, wave + name, coarse tune), MFX/chorus/reverb type |
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
| `tests/test_schema.py` | 73 evidence tests (`py -3 -m unittest discover -s tests`) |

Regenerate: `extract_script_schema.py` → `crosscheck_midi_impl.py` → `build_parameter_db.py` (the `.venv` with `pypdf` is only needed for `pdf2txt.py`).
