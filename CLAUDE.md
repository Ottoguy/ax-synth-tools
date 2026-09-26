# CLAUDE.md: ax-synth-ai project context

Loaded automatically by Claude Code. Written for LLM agents; dense on purpose. Last updated 2026-09-26 (steps 3.2/3.3).

## 1. Goal and current phase

- **End goal:** the user describes a sound in natural language, an LLM produces a patch, and the patch reaches a **Roland AX-Synth** keytar via MIDI SysEx. There's an intermediate goal of a **simple GUI** with a few high-level "big knob" controls (abstracting the Roland Editor's ~825 parameters).
- **Intended architecture** (user-specified separation; keep it):
  `natural language → LLM sound design → AX-Synth parameter model → patch representation → encoder → DT1 SysEx → hardware`
- **Phase now: research / reverse engineering (phase 1) is complete on the file/doc side.** NEXT-STEPS step 2 (live Editor output via loopback, no synth) is **done** (`captures/live/`, `research/live-capture-analysis.md`). Step 0 (the user's setup) is **done** (`captures/setup.md`). **Steps 3.0–3.3 are done** (2026-09-26):
  - the Editor/Librarian ↔ synth conversation was logged through MIDI-OX (`captures/mitm/`)
  - a full backup of all 256 User patches exists (`captures/backup/`)
  - the synth's Bulk Dump is decoded and equals the backup (`captures/bulkdump/`, `research/bulkdump-analysis.md`)
  - our own read-only RQ1 file works (`captures/rq1/`)

  **Reading is solved; nothing that writes has been sent by our tools.** Next: NEXT-STEPS step 4, the first write of *our* bytes to the Temporary patch (`guitar01-temporary.syx`, verified by an RQ1 read-back). Then a listening test (single-parameter Temporary patches), then 3.4/step 5 (user descriptions, decisions). A MIDI-I/O "safe sender" needs the user's explicit go-ahead.
- **Not built yet, on purpose:** AI preset generator, GUI, MIDI I/O code. Don't build these unless the user asks. Keep code evidence-driven and small; no speculative application code.
- **The user's checklist of manual tasks** (hardware steps, captures, decisions) is `NEXT-STEPS.md`. Results go under `captures/` (`live/` exists; next: `mitm/`, `backup/`, `bulkdump/`, `rq1/`, …). The user saves MIDI-OX *Monitor* text logs (Windows may add a double `.txt.txt`), and may skip writing notes.md; write it for them from their message. When the user says "step N done", read those captures, decode them with the tools, and update research, tests and NEXT-STEPS.

## 2. Hard rules

1. **`original-roland-files/` is immutable source material.** Never write inside it. SHA-256 hashes of all 176 files are in `research/generated/inventory.json`; re-verify after work.
2. **Never transmit to hardware**, and never add code that opens MIDI ports, unless the user explicitly moves to that phase. Tools only read and write files.
3. When preparing anything the user will send: **target only the Temporary Patch `1F 00 00 00`** (volatile). Never the User area `30 00 00 00`–`31 7F 26 00` (overwrites stored sounds), never `0F …` (the undocumented command area), never the synth's Bulk Dump *receive* mode. Don't tell the user to press Editor **SYNC** unless needed: it also overwrites Setup + System (`01 …`, `02 …`) with the Editor's values.
4. **`dumps/AX-Synth Librarian Clean export.mid` must never be played to the synth** (and `captures/backup/*.mid` only as a deliberate full restore; it rewrites all 256 slots): 2,304 DT1s that would overwrite all 256 User patches with INIT PATCH. (Recovery: factory reset, Owner's Manual p.34, which restores factory sounds but loses user edits.)
5. **Don't hand-type parameter data.** Everything is generated from Roland sources by `research/tools/`. Keep provenance (file + line or page) on every fact.
6. **Label evidence** in research docs: **[F]** our Roland files, **[D]** official Roland documentation, **[3P]** third party, **[I]** inference. Don't present [I] as fact.
7. **The user's setup** (`captures/setup.md`): USB directly to Windows 10, driver mode "Gen" (OS generic, effectively one program per port; Editor manual p.8), port name **"Roland AX-Synth"**, **firmware 2.01** (newer than all our v1.00-era docs; Roland published no update, so it was probably factory-installed [I]). The synth is second hand and a few User patches may be non-factory; diff the backup against the factory list. Don't tell the user to switch driver mode (Roland's Uen driver stops at Windows 8).
8. **Hardware facts that constrain instructions to the user:** the synth has a **3-character 7-segment LED display** (it can't show names, waves or values, so verify via the Editor's READ or an RQ1 dump), and the synth's panel **[WRITE] stores only FAVORITE/system settings, never sound edits**. Sounds are stored only via Editor/Librarian SysEx.

## 3. Environment (Windows 10, PowerShell 5.1)

- Python: **`py -3`** (3.14). `python` isn't on PATH. Every run prints a harmless `Could not find platform independent libraries <prefix>` on stderr; redirect with `2>$null`. Exit code 255 when piping into `Select-Object -First` is also harmless.
- `.venv/` (project-local) exists **only** for `pypdf` (used by `research/tools/pdf2txt.py`); run it as `.\.venv\Scripts\python.exe`. Everything else is stdlib-only and runs with `py -3`.
- PowerShell mangles quotes passed to native exes. Put non-trivial Python in a script file, not in `py -3 -c "..."`.
- Tests: `py -3 -m unittest discover -s tests` (**73 tests, all passing**; the backup/bulk-dump classes skip if those files are absent). No pytest.
- Git repo, branch `main`, remote `origin` = github.com/Ottoguy/ax-synth-tools. Commit/push only when the user asks. `.gitignore`: see §9.

## 4. Repository map

```
ax-synth-ai/
├── CLAUDE.md                 this file
├── AGENTS.md                 pointer to this file (for non-Claude agents)
├── NEXT-STEPS.md             user-facing checklist: steps 0-6, safety rules, decisions to make
├── .gitignore
├── .claude/settings.local.json   personal permission allowlist (git-ignored)
├── original-roland-files/    IMMUTABLE. AX-Synth Editor/Librarian v1.00 install (2009)
│   ├── A8EE.exe              Editor ("Koa" engine, MFC). Contains MFX display names @0xF8FC0-0xF9438 (reversed) [git-ignored]
│   ├── A8EL.exe              Librarian; patch model hard-coded (class CPatch), no script [git-ignored]
│   ├── Manual/               Editor + Librarian manuals, English and Japanese PDFs
│   └── Script/
│       ├── A8EE/Script.xml   THE primary source: Editor data model + MIDI binding + UI (37,610 lines, ASCII despite Shift_JIS decl.)
│       ├── A8EE/InitialData.a8e   Editor blank document (Setup+System+INIT PATCH), 1,465 B
│       ├── A8EE/*.bmp        167 UI images [git-ignored]
│       └── A8EL/InitialData.a8l   Librarian blank library (1 INIT PATCH), 1,276 B
├── docs/                     [git-ignored] reference PDFs, see §6
│   ├── AX Synth docs.pdf              official "AX-Synth MIDI Implementation" v1.00, Roland Europe, Jan 2010, 16 pp
│   ├── AX-Synth_OM.pdf                Owner's Manual, 44 pp
│   ├── AX-Synth_Erratum2.pdf          erratum to Owner's Manual p.27
│   ├── AX-SynthEditorManualE.pdf      = original-roland-files/Manual copy (78 pp; parameter guide p.9-43, Effects List p.44-78)
│   └── AX-SynthLibrarianManualE.pdf   = original-roland-files/Manual copy (10 pp)
├── dumps/                    Roland "Export SMF" captures (no synth attached; INIT data); test fixtures
│   ├── AX-Synth Editor clean export.mid      9 DT1 -> Temporary Patch 1F 00 00 00
│   └── AX-Synth Librarian Clean export.mid   2,304 DT1 -> User 30 00 00 00..31 7F 26 00  (DANGEROUS, rule 4)
├── patches/                  third-party forum patches (.a8e) + author's description; test fixtures; check license before publishing
│   ├── guitar.a8e            "SearingGtr 1" tuned: "muted chug" layer, beam=CC71
│   └── guitar01.a8e          "SearingGtr 1" tuned: CC70 "feedback" works, beam=CC70, +24 sine layer
├── captures/setup.md         the user's hardware setup (step 0): USB direct, driver "Gen", port "Roland AX-Synth", firmware 2.01
├── captures/live/           user's MIDI-OX logs of Editor/Librarian live output (step 2, no synth) + notes.md; test fixtures
├── captures/mitm/           MIDI-OX logs Editor/Librarian <-> synth (IN PORT 1 = software->synth, 3 = synth->software): Read Selected, READ, SYNC + notes.md
├── captures/backup/         user's full backup: Librarian Read All -> Export SMF (256 User patches, 2,304 DT1) + notes.md. RESTORE FILE
├── captures/bulkdump/       the synth's own Bulk Dump (16,230 msgs, model 7F, raw 1.7 MB memory image) + notes.md. RESTORE FILE
├── captures/rq1/            replies to our experiment-rq1-temporary-patch.syx (before/after a panel volume edit) + notes.md
├── reference/synth-secrets/  [git-ignored, copyrighted] 63 Synth Secrets articles as Markdown + index.{md,json} (fetch_synth_secrets.py)
├── knowledge/                LLM/human KNOWLEDGE BASE: meaning of every parameter & effect type (see knowledge/README.md)
│   ├── concepts.toml, system.toml, patch.toml, mfx-01-42.toml, mfx-43-78.toml, chorus_reverb.toml   SOURCE (hand-extracted from Editor manual + OM + MI, page refs, schema links)
│   ├── sound_design.toml, sound_recipes.toml   SOURCE: SOUND DESIGN from Synth Secrets [3P] mapped to AX-Synth [I]: 27 principles, 37 descriptors, 35 recipes
│   ├── sound-design/         README (format, how an LLM uses it), digests/NN-*.md (63 per-article digests), sound-design.md (GENERATED)
│   ├── knowledge.json        GENERATED: validated, joined with data-model facts (addresses, raw ranges, defaults, enums); `sound_design` section
│   ├── knowledge.md          GENERATED: human-readable rendering
│   └── README.md             format spec, conventions, coverage
├── src/axsynth/              typed library (stdlib only), see §8
│   ├── __init__.py           package docstring
│   ├── schema.py             Schema, Parameter, ValueDef, value codec, address helpers
│   ├── sysex.py              DT1/RQ1 build/parse, checksum, whole-patch encoder, .syx/SMF readers (no MIDI I/O)
│   ├── factory.py            factory Tone list access
│   └── knowledge.py          knowledge-base lookup (describe(path), effect(kind, n), concept(id), param(id))
├── tests/test_schema.py      73 evidence tests (§10)
└── research/
    ├── README.md             index: question -> file
    ├── REPORT.md             MAIN findings report: known / suspected / unknown / next experiments / files
    ├── script-analysis.md    Script.xml structure, address system, types (tasks 1-3, 7)
    ├── initialdata-analysis.md   .a8e / .a8l byte layouts
    ├── smf-export-analysis.md    dumps/ analysis: whole-patch wire format, pacing
    ├── live-capture-analysis.md  captures/live/ analysis: value-edit DT1s, effect type change, Identity Request gating, name RQ1
    ├── bulkdump-analysis.md  captures/bulkdump/ + rq1/: Bulk Dump image format, bit-packed patch records (= backup), FAVORITE memories, System Common; SystemController 0x50
    ├── mitm-capture-analysis.md  captures/mitm/ + backup: Identity Reply, RQ1 replies, READ/SYNC sequences, factory mapping + waves confirmed, forum diffs, patchCategory
    ├── third-party-patches-analysis.md   patches/ vs author's description (ground truth)
    ├── owners-manual-analysis.md Owner's Manual: Tone list, UI limits, maintenance combos, controllers, terminology
    ├── roland-installation-inventory.md  every installation file + external docs
    ├── online-research.md    web/GitHub findings, Koa framework evidence
    ├── script-schema.json    GENERATED full Script.xml extraction (2 MB)
    ├── tools/                analysis CLIs (§7)
    └── generated/            GENERATED artifacts (all tracked in git)
        ├── parameters.{csv,json}          parameter DB: 1,934 fm+cm parameters (Schema.parameters)
        ├── crosscheck-midi-implementation.md, crosscheck.json   script vs official doc, per row
        ├── factory-tones.{csv,json}       264 factory Tones (256 regular + 4 SuperNATURAL + 4 SPECIAL)
        ├── user-patches.{csv,json}        the user's 256 User patches (backup_summary.py): names vs factory, category, waves, effect types
        ├── bulkdump-layout.json           bulk-dump patch-record layout (bulkdump.py solve): bit position/width/offset per field, verified flag
        ├── experiment-rq1-setup-system.syx   3 read-only RQ1s (Setup, System Common, System Controller 0x50), NOT sent yet (NEXT-STEPS 3.5)
        ├── inventory.json                 SHA-256 of original-roland-files/*
        ├── A8EE.exe.strings.txt, A8EL.exe.strings.txt   strings dumps (offset, A=ASCII / W=UTF-16)
        ├── midi-implementation.pdf.txt, owners-manual.pdf.txt, editor-manual.pdf.txt,
        │   librarian-manual.pdf.txt, erratum2.pdf.txt     PDF text extracts (docs/ is git-ignored, these are not)
        ├── experiment-rq1-temporary-patch.syx   10 read-only RQ1s (9 patch blocks + SystemController size 0x50), NOT sent
        └── guitar-temporary.syx, guitar01-temporary.syx   forum patches as 9 DT1s to Temporary Patch, NOT sent
```

## 5. Generation pipeline (run from repo root)

| Order | Command | Reads | Writes |
|---|---|---|---|
| 1 | `py -3 research/tools/extract_script_schema.py` | Script.xml, A8EE.exe (MFX names; skipped if absent) | `research/script-schema.json` |
| 2 | `py -3 research/tools/crosscheck_midi_impl.py` | script-schema.json, `generated/midi-implementation.pdf.txt` | `generated/crosscheck-midi-implementation.md`, `generated/crosscheck.json` |
| 3 | `py -3 research/tools/build_parameter_db.py` | via `axsynth.schema` (schema + crosscheck.json) | `generated/parameters.{json,csv}` |
| 4 | `py -3 research/tools/extract_tone_list.py` | `generated/owners-manual.pdf.txt` | `generated/factory-tones.{json,csv}` |
| 5 | `py -3 research/tools/build_knowledge.py` | `knowledge/*.toml`, `knowledge/sound-design/digests/`, data model (via `axsynth.schema`), factory Tones | `knowledge/knowledge.{json,md}`, `knowledge/sound-design/sound-design.md`; exit 1 on broken links |
| – | `py -3 research/tools/backup_summary.py [backup.mid]` | newest `captures/backup/ax-synth-backup-*.mid`, factory Tones, knowledge.json (MFX names) | `generated/user-patches.{csv,json}` |
| – | `py -3 research/tools/fetch_synth_secrets.py [outdir]` | soundonsound.com (network, ~1.5 s/request) | `reference/synth-secrets/NN-*.md`, `index.{md,json}` (git-ignored) |
| – | `.\.venv\Scripts\python.exe research/tools/pdf2txt.py x <outdir> <pdf>...` | PDFs | `<outdir>/<pdf stem, spaces→_>.txt` (argv[1] is an unused placeholder); rename to the `*.pdf.txt` convention by hand |
| – | `py -3 research/tools/exe_strings.py <file> [minlen] > out.txt` | binary | strings list |
| – | `py -3 research/tools/inventory.py` | original-roland-files/ | `generated/inventory.json` |

Rerun 1→3 (+5) after changing the extractor or schema.py, and 5 after editing `knowledge/*.toml`; then run the tests (a test fails if `knowledge.json` is stale).

## 6. Source documents and what each is authoritative for

| Source | Authoritative for | Notes |
|---|---|---|
| `Script.xml` [F] | parameter names, per-value address/size/type/range/default, struct tree, effect unions (`mfxValuePathTable` etc.), enum labels (`stringTable`), sparse enum values (`numberTable`), 313 wave names (`internalWaveNameTableA`, l.16202), undocumented `CommunicationModel` | Has anomalies (§11) |
| MIDI Implementation PDF [D] | model ID, DT1/RQ1 format, checksum, address map incl. **User patches `30 00 00 00`+n·`00 01 00 00`**, nibble encoding definition, packet rule (≤256 B, ~20 ms) | Has typos (§11) |
| Owner's Manual [D] | factory Tone list (p.37–38), UI/panel, Bulk Dump (p.29), factory reset/firmware (p.34), controllers, Implementation Chart (p.40) | No parameter explanations, no wave list |
| Editor manual [D] | **meaning of every parameter** (p.9–43) and every effect type (Effects List p.44–78) | Fully extracted into `knowledge/` (validated against the data model) |
| Librarian manual [D] | 256 patches = Bank 1–8 × Number 1–32; memos aren't stored on the device | |
| Erratum2 [D] | VOLUME knob is analog, sends no CC07; D-Beam sends CC01–31, 33–95 | |
| dumps/*.mid [F] | exact bytes/order/pacing Roland software sends | |
| patches/*.a8e [3P] | real non-default data + author's description = semantic ground truth | |
| Synth Secrets [3P] (Gordon Reid, SOS 1999–2004) | general acoustics and synthesis: what settings produce what sounds, instrument recipes | Analogue/modular-centric; AX-Synth mappings are [I]. Copies git-ignored; digests in `knowledge/sound-design/digests/` |

## 7. Tools (`research/tools/`, all read-only on inputs, none touch MIDI ports)

| Tool | Usage | Purpose |
|---|---|---|
| `extract_script_schema.py` | no args | Script.xml → script-schema.json (line numbers, base-128 address resolution, unions, UI bindings, macro bindings, carry check) |
| `crosscheck_midi_impl.py` | no args | parse doc rows, compare offset/encoding/range/size |
| `build_parameter_db.py` | no args | export `Schema.parameters(None)` for fm+cm |
| `extract_tone_list.py` | no args | Owner's Manual Tone list → factory-tones |
| `build_knowledge.py` | no args | validate `knowledge/*.toml` against the data model (incl. sound-design refs, waves 1–313, factory Tone names, Synth Secrets parts); write `knowledge.json` + `knowledge.md` + `sound-design/sound-design.md`; report coverage |
| `fetch_synth_secrets.py` | `[outdir] [--force]` | download the 63 Synth Secrets articles as clean Markdown (only network tool; output git-ignored) |
| `a8_files.py` | `<file.a8e/.a8l/.mid/.syx> [--all] [--json]` | parse Koa data / Librarian files / whole-block DT1 dumps (per User patch or temporary), decode all values, flag inactive union members |
| `describe_a8.py` | `<A> [B] [--all]` | non-default active values with labels; or A-vs-B diff; flags out-of-range. `FILE#N` picks patch N of an .a8l or a dump (e.g. `captures/backup/…mid#96` = SearingGtr 1) |
| `bulkdump.py` | `info <dump.syx>` · `solve <dump.syx> <backup.mid>` · `verify <dump.syx> <backup.mid>` · `export <dump.syx> <out.syx>` | the synth's Bulk Dump: unpack the image, favorites, System Common, 256 patch names; derive/verify the patch-record layout; export as Librarian-style DT1s (a restore file) |
| `backup_summary.py` | `[backup.mid] [--quiet]` | backup → `generated/user-patches.{csv,json}`; prints slots whose names differ from the factory list |
| `midiox_log.py` | `<log.txt>... [--syx out.syx]` | MIDI-OX Monitor text log → per-message timestamp/gap/IN PORT, length+checksum check, Identity Reply fields diffed against the doc, every covered parameter decoded (User area mapped to patch paths, effect members for the type seen in the log) |
| `smf_inspect.py` | `<file.mid> [--summary]` | every SMF event with ticks; Roland SysEx header, address, length, checksum |
| `dump_experiment.py` | `make-requests <out.syx>` · `make-system-requests <out.syx>` · `decode <in.syx or .mid>` · `a8-to-syx <patch.a8e> <out.syx>` | build RQ1 file; decode DT1 stream into named params (active union members only, enum labels); patch → Temporary-only DT1s |
| `exe_strings.py`, `inventory.py`, `pdf2txt.py` | see §5 | |

## 8. Library API (`src/axsynth`)

`schema.py`
- `Schema.load(path=research/script-schema.json, crosscheck=research/generated/crosscheck.json)`
- `.values(structType) -> list[ValueDef]`, `.value(structType, name)`, `.struct_size(structType)` (bytes, base-128 decode of `<size>`), `.child_types(structType) -> {name: (structType, n_instances)}`, `.leaf_structs(root) -> iter[(path, structType)]` (depth-first, arrays expanded)
- `.union_membership -> {(structType, name): (union_key, type_index, label)}`, `.unreachable -> {(structType, name)}` (gm2*)
- `.parameters(root="fm"|"cm"|"vs"|None) -> list[Parameter]`. Parameter fields: `path, name, structure, address ("1F 00 20 49"), size, type, range, default, source {file,line}, confidence ("script+doc"|"script"), effect ("mfx:EQUALIZER"), effect_index, enum, enum_values, display_offset, description (doc text), notes`. Enum rule: `enum[i]` labels raw `enum_values[i]` if given, else raw `range[0]+i`.
- `decode_value(ValueDef, bytes)`, `encode_value(ValueDef, value, check_range=True)` (range-checked unless reproducing stored data), `addr_to_int(str|bytes)`, `int_to_addr(int, width=4)`, `fmt_addr(bytes)`

`sysex.py`
- Constants: `ROLAND=0x41`, `MODEL_ID=00 00 3C`, `DEFAULT_DEVICE=0x10`, `RQ1=0x11`, `DT1=0x12`, `TEMPORARY_PATCH`, `PATCH_BLOCKS` (9 (name, offset) in Roland's order)
- `checksum(body)`, `build_dt1(addr, data, device)`, `build_rq1(addr, size, device)`, `identity_request(device)`, `IDENTITY_REPLY_DOC`, `parse_identity_reply(msg) -> IdentityReply(device, manufacturer, family, family_number, revision)` + `.differences_from_doc()`, `parse(msg) -> RolandMessage(device, model_id, command, address, payload, checksum_ok)`, `split_sysex(bytes)`, `smf_sysex(bytes)`
- `user_patch_address(n)`, `patch_messages(blocks: {name: image}, base=TEMPORARY_PATCH) -> 9 DT1` (**byte-identical to Roland's export**), `patch_blocks(messages) -> {n | "temporary": {block: image}}` (inverse; whole-block DT1s only, from exports or synth replies), `roland_export_delay_ticks(msg_len, ppq=96, bpm=120)`

`knowledge.py` (reads `knowledge/knowledge.json`)
- `describe(path) -> list[{kind, id|number, type, entry}]` (any data-model path, tone/array index ignored), `effect(kind, number)`, `concept(id)`, `param(id)`, `load()`
- Sound design: `descriptor(word)` (id or any term, e.g. 'warm' → `dark`), `recipe(id)`, `principle(id)`, `sound_design()` (principles, descriptors, recipes, synth_secrets part index, meta)

`factory.py`
- `tones() -> tuple[FactoryTone]` (group, position, name, cc00_msb, cc32_lsb, pc [1-based], editable, user_patch_index, librarian_slot, user_patch_address), `by_name(name)` (ignores spaces/dots/case), `by_program(msb, lsb, pc0)`, `by_user_index(n)`, `families()`

## 9. `.gitignore` policy (user decisions)

Ignored: `original-roland-files/**/*.exe`, `original-roland-files/**/*.bmp`, `docs/`, `reference/synth-secrets/` (copyrighted articles; only our digests/TOML are tracked), `captures/backup/*` and `captures/bulkdump/*` except their `notes.md` (the user's full synth backups = Roland factory data; restore files; tests skip without them), `.venv/` and other Python caches, IDE/OS files, `.claude/settings.local.json`, `*.log`, `tmp/`, `scratch/`. Everything else is tracked, including `src/`, `research/` (all of `generated/`), `tests/`, `dumps/`, `patches/`, Script.xml, InitialData files and the manuals under `original-roland-files/Manual/`. Consequence: on a fresh clone, rerunning the extractor without A8EE.exe loses the MFX display names (falls back to prefixes); the committed JSON keeps them.

## 10. Test coverage (`tests/test_schema.py`)

`ExtractionCounts` (27 structTypes, 1,539 values, type vocabulary, size = type width) · `AddressesMatchOfficialMap` (addresses, block sizes, SystemController 4F discrepancy, step-pitch anomaly) · `Codec` (doc nibble examples, MFX zero point, roundtrip) · `RolandDataFiles` (.a8e/.a8l fully consumed, defaults, identical INIT patch) · `SysEx` (checksum, DT1/RQ1, Identity Reply parse/diff) · `RolandSmfExports` (encoder = Roland bytes, 256 User slots, pacing) · `ThirdPartyPatches` (author's claims) · `OwnersManual` (Tone list, SearingGtr 1, ranges) · `LiveEditorCaptures` (captured value edits = our DT1 bytes, `00 81` → `01 01`, MFX type change = schema-default block, Identity Request ×2 @3 s, WRITE name RQ1) · `SynthConversation` (Identity Reply = doc, RQ1 → one exact-size DT1, Read Selected/READ/SYNC sequences, SYNC = READ payloads, READ returned InitialData) · `SynthBackup` (skipped if the backup is absent: 256 complete patches, 254/256 factory names, wave numbering, Read Selected = backup, forum patch vs factory SearingGtr 1, categories, user-patches.json current) · `SynthRequests` (our RQ1 file → exact DT1s, SystemController 0x50, Temporary = panel selection = backup slot 96, panel volume edit invisible, system request file = Editor's bytes) · `SynthBulkDump` (skipped if absent: wire format, all 2,304 blocks rebuilt = backup, layout rules, favorites, System Common) · `KnowledgeBase` (KB builds without errors, all effect types, only reserves undocumented, schema-only members are tempo-sync, committed JSON current, lookup API, sound-design section: 63 digests/parts, counts, lookups).

## 11. Core technical facts (quick reference; details in `research/`)

**SysEx.** `F0 41 <dev=10> 00 00 3C <11 RQ1 | 12 DT1> <addr×4> <data | size×4> <sum> F7`, where `sum = (128 − Σ(addr+data) mod 128) mod 128`. Addresses are 7-bit bytes, MSB first, and arithmetic is **base-128**. Identity reply: `F0 7E 10 06 02 41 3C 02 00 00 00 01 00 00 F7` (doc v1.00; the user's firmware-2.01 unit sends exactly this). **RQ1 reply** = one DT1, same address, exactly the requested size (≤154 B, no packetization), 2–47 ms later.

**Address map.**

| Area | Address | Size |
|---|---|---|
| Setup | `01 00 00 00` | 0x34 |
| System | `02 00 00 00` (Common +`00 00`, 0x1E; Controller +`40 00`) | Controller: **0x50 on the hardware** (doc), script 0x4F |
| Temporary Patch | `1F 00 00 00` | – |
| User Patch n (0–255) | `30 00 00 00` + n·`00 01 00 00` | – |
| CommunicationModel (undocumented) | `0F 00 00 00` | incl. `writeRequest/Start/Complete` @ `0F 00 10 00–02` (**never send**) |

Patch blocks (offset → bytes): Common `00 00 00`→79 · MFX `00 02 00`→145 · Chorus `00 04 00`→84 · Reverb `00 06 00`→83 · TMT `00 10 00`→41 · Tone 1–4 `00 20/22/24/26 00`→154 each (total 1,048).

**Types.** `int<W>x<B>` = W wire bytes × B low bits, MSB first. Used: `int1x7` (372), `int4x4` (1,157; "nibbled"), `int2x4` (4: toneDelayTime, lfoRate[0/1], PatchCommon reserve1F), `int5x7` (4, UI only), `string` (ASCII 32–127, space-padded; patchName = 12). Signed values are stored with an offset: 64 = 0 (7-bit), 32768 = 0 (effect params; doc 12768–52768 = −20000…+20000).

**Script.xml semantics.**
- Short addresses are right-aligned.
- Repeated `<address>` in a `<struct>` = array (4 Tones).
- `name[n]` values = flattened arrays (TMT ×4, LFO ×2).
- `$name`/`$address`/`$size` are macros.
- A struct holds structs **or** values, never both.
- Leaf `<size>` = byte count; node `<size>` = address extent.
- Roots `fm` and `cm` are bound to MIDI (`<midiOut> rootStruct`); `vs` is Editor UI state only.

**Effect unions.**
- MFX (79 types, 0 = THROUGH), Chorus (0 OFF, 1 chorus, 2 delay) and Reverb (0 OFF, 1 reverb, 2 srvRoom, 3 srvHall, 4 srvPlate) parameters are named per type (`<effect>-<param>`) and overlay generic 4-byte slots (MFX: `00 11 + 4k`, k = 0…31).
- `*ValuePathTable` group N = members active when type == N.
- MFX names come from A8EE.exe.
- `gm2Chorus-*` / `gm2Reverb-*` are unreachable leftovers.

**Enum indexing gotchas.**
- The matrix/MFX control-source table keeps a `32:OFF` slot, so **raw = CC number**.
- The beam table (`beamControlSourceTable`, range 0–93) has **no CC32 slot**, so raw 68 = CC70.
- Sparse enums use `numberTableRef`, e.g. output assign `0,1,5,6,13` = MFX, L+R, L, R, TONE.

**File formats.**
- `.a8e`: `KoaDataFile00001` + root name (64 B) + model (16 B) + zeros to 0x100, then every leaf struct under `fm` in Script.xml order, each `<size>` bytes (1,465 B total). It also saves Setup and System (including the author's beam setting), so **send only the Patch blocks** to a synth.
- `.a8l`: 32 B magic `A8ELibrarianFile0000` + u32 BE count @0x20, zeros to 0xA0. Per patch: u32 BE record length; for common, mfx, cho, rev, tmt, tone: u32 count, then count × (u32 size + data); then 4 unexplained bytes (`00 00 00 00`). The same container family as Juno-G/Fantom-X librarian files [3P].
- Block images in both files = DT1 payloads (**confirmed** by dumps/).

**Whole-patch transfer (Roland software).**
- 9 DT1s in `PATCH_BLOCKS` order, each a full block, crossing 7-bit address boundaries.
- Editor → Temporary; Librarian → User n. No `0F` handshake appears in either export.
- SMF format 0, 96 PPQ, gap = `ceil((bytes×0.32 ms + 20 ms)/tick)`.

**Live Editor protocol [F, captures/live/].**
- Value edit = one DT1 per value, only that value's bytes (the whole 12-byte name for a name edit), sent immediately with no handshake and no pacing (gaps down to 1 ms). System values too (`02 00 …`).
- Effect (MFX) type change = the whole 145-byte block with every member of the new type at its Script.xml default, then the type byte again.
- READ / SYNC / WRITE / Librarian reads start with Identity Request `F0 7E 10 06 01 F7` (dev 10). No reply in ~3.0 s → 1 retry → "Unable to read/write data.", then nothing more. A loopback without a synth can't get further.
- WRITE first sends RQ1 `30 00 00 00` size 12, reading User patch 0's name. Names are read on the User area, not via `cm`.

**Synth conversation [F, captures/mitm/].**
- Librarian Read Selected: Identity → RQ1 `01 00 00 04` size 2 → RQ1 per patch block of `30 nn …` (PATCH_BLOCKS order, Script.xml sizes).
- Editor READ: Identity → Setup bank MSB, LSB (1 B each) → Setup `01 00 00 00` 0x34 → System Common 0x1E → System Controller 0x4F → 9 Temporary blocks. No name list.
- Editor SYNC: Identity → 12 whole-block DT1s (Setup, System Common, System Controller, 9 Temporary), 21–60 ms apart, no reads (contrary to the Editor manual p.8).
- Before the capture, the synth's Temporary/Setup/System equalled `InitialData.a8e` (INIT PATCH) although the panel Tone was AX Saw Lead: something (probably a SYNC during setup) had sent the blank document [I]. Normally Temporary = the panel-selected patch (step 3.3).
- Our RQ1 file (`experiment-rq1-temporary-patch.syx`) works: RQ1 SystemController size 0x50 → 80 bytes (`00 4F` = 1).
- The panel volume/reverb-send edit ("UOl"/"reU") is a **FAVORITE-memory** value (OM p.26), invisible in the Temporary patch and SystemController.

**Bulk Dump [F, captures/bulkdump/, research/bulkdump-analysis.md].**
- It's a raw memory image: `F0 41 dev 7F 12 aaaa <data> sum F7`, 1-byte model `7F`, byte addresses in base-128, 7-in-8 packing (first byte of each 8 = high bits, bit j → byte j), 105 image bytes per 131-byte message; the header (dev 11) holds the length 0x1A0040; the trailer is "Roland RE409DUMP VER.1.00".
- Image map: System area @0 (bit-packed; System Common at bit 101 after 0x14), FAVORITES @0x20014 (16 × 40 bits: MSB8 LSB7 PC7 vol7 rev7 pad4), 256 patch records @0x20064 × 664 bytes.
- Patch record = all non-union values in Script.xml order, MSB-first, width = ceil(log2(range)); unsigned stored as-is, centred values as v − (64 − 2^(w−1)); Tone stride 792 bits; +146 hidden bits. Rebuilt blocks = the Librarian backup byte for byte (all 256).
- The factory FAVORITES are A1–A8 GR300 Lead 1 … Funk EGtr, B1–B8 Wide SynBrs … Wurly EP (two per family).

**Factory Tones.**
- 256 regular Tones = 8 families × 32: Synth Lead 1, Synth Lead 2, Bass, Lead Guitar (bank 87/0, PC 1–128); Brass/Poly Synth, Strings/Pad, Organ/Clavi, Choir/Piano (87/1, PC 1–128).
- 4 SuperNATURAL (66/0) and 4 SPECIAL (87/64) are not editable.
- **Confirmed by the user's backup:** Tone ↔ User patch n = LSB·128 + PC − 1, family = n ÷ 32, Librarian slot f-v (254/256 stored names equal; 3-10/3-11 stored as "Reso Bs 1"/"Reso Bs 2", cause unknown).
- **Wave numbering confirmed:** wave N = `internalWaveNameTableA[N−1]` (all factory patches use fitting waves).
- `patchCategory` numbers group by instrument (11 dist. guitar, 9 ac. guitar, 7 accordion, 8 harmonica, 22/23 leads, 28/29 pads…; table in mitm-capture-analysis.md); the names are Roland's XV/Fantom list [3P, unverified].
- Setup `kbdPatch{BankSelectMsb,Lsb,ProgramNumber}` records the selected Tone; the forum files store 87/0/96 → SearingGtr 1 (Lead Guitar 1).
- Printed names can differ from the 12-character stored names ("Vintage Org 1" is stored as "Vintage Org1"); exact stored names are in `generated/user-patches.csv`.

**Terminology.** Owner's Manual "Tone" = a whole sound = Editor/MIDI "Patch" (`fm.pat`). Editor "Tone 1–4" = the four layers inside a patch (`fm.pat.tone[0..3]`). Always say which.

**Controllers.**
- Mod bar = CC01.
- AFTER TOUCH *knob* = channel aftertouch; the keys send none.
- Ribbon = pitch bend (BENDER MODE normal / catch+last).
- D-Beam: PITCH / FILTER / ASSIGNABLE (CC01–95, no 32; a system setting).
- PORTAMENTO, HOLD = CC64. The foot pedal is hold only; no expression pedal.
- Received real-time CCs 71–75 (+76–78 per MIDI Impl.), 91 and 93 are relative offsets that aren't stored.
- Patch-level macro-like params: PatchCommon `cutoffOffset`, `resonanceOffset`, `attackTimeOffset`, `releaseTimeOffset`, `velocitySensOffset` (1–127, 64 = 0).

**Knowledge base facts.**
- All 78 MFX, 2 chorus and 4 reverb types are documented, with 697 effect-parameter links.
- Every non-reserved `fm` value has an entry.
- 172 effect members (`…Sync`/`…Note` tempo-sync variants of rate/delay parameters) exist in the data model but not in the AX-Synth manual; leave them at their defaults.
- **Sound design** (`knowledge/sound_*.toml`, `knowledge/sound-design/`): general acoustics/synthesis knowledge from Gordon Reid's *Synth Secrets* (SOS 1999–2004, all 63 parts) [3P], every mapping onto AX-Synth parameters/waves/effects/factory Tones [I], unverified on hardware. Key AX-Synth findings: PWM sound = two saw tones with a tiny pitch LFO on one (SS47); no oscillator sync (use wave 219 or FXM + Matrix TVF ENV→FXM DEPTH); Matrix sources AFTERTOUCH/CC01/D-Beam CC → LEVEL/CUTOFF/LFO depth give the most expressive keytar patches (SS50/51); Structure ring-mod on both tone pairs = the 'pairs of modulated squares' metal recipe (SS39).

**Known anomalies/discrepancies.**
- `stepPitchShifter-bal/level` have address `00 81`/`00 85` (bytes > 0x7F); base-128 decoding gives the doc's `01 01`/`01 05`. **Settled:** the Editor sends `1F 00 03 01`/`05` (live capture), so our addresses are right.
- SystemController: script 0x4F vs doc 0x50. **Settled by the hardware: 0x50** (RQ1 reply of 80 bytes; `00 4F` = 1 = Portamento mode Hld/SUt, label mapping unknown). The script model stays as generated; send/request 0x50 when reading the whole block.
- SystemController `reserve04` = 100 in every `.a8e` (script range 0–1 is wrong).
- PatchCommon `reserve1F` (20–250, tempo?) = 0 in all files.
- Doc range typos: `mfxOutputAssign`, TMT2 velocity lower, LFO1 key trigger.
- The doc claims CC07 is transmitted; the Erratum says it isn't.

## 12. Open questions (need hardware or live captures; see REPORT.md "What remains unknown")

- Whether the synth accepts **our** DT1s to Temporary (NEXT-STEPS 4) and what spacing it tolerates (Roland: 21–60 ms; plan 60 ms).
- Whether System DT1s (SYNC) persist (undecidable so far: stored = Editor defaults).
- Where the sleep interval, USB driver mode and live FAVORITE volume sit (optional NEXT-STEPS 3.5); the 146 hidden bits per bulk-dump patch record.
- Whether a DT1 to `30 …` commits to flash.
- The `0F` write handshake payloads.
- What firmware 2.01 changed vs the v1.00 docs (nothing visible so far: same Identity Reply, block sizes and factory list).
- The Librarian Read All sequence (not logged) and the WRITE handshake.
- Why 3-10/3-11 are stored as "Reso Bs 1"/"Reso Bs 2".
- The `.a8l` trailing 4 bytes.
- The `patchCategory` names (numbers known).

## 13. User preferences / working style

- Wants thorough, verified, evidence-labelled investigation; don't assume, and say explicitly when something is inference.
- Wants tools over manual retyping; provenance on every fact.
- Prefers being shown proposals before commits (e.g. `.gitignore`); commits and pushes to `main` when asked.
- Documents for the user: `NEXT-STEPS.md` (their checklist) and `research/REPORT.md` (findings). Keep both consistent after every new discovery, together with the relevant `research/*-analysis.md`.
