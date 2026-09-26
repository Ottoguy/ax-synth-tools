# research/ index

Start with `../CLAUDE.md` (project context) and `REPORT.md` (findings). This file maps **questions → the file that answers them**. Evidence labels used throughout: [F] our Roland files, [D] official Roland docs, [3P] third party, [I] inference.

## Documents

| File | Scope | Key sections |
|---|---|---|
| `REPORT.md` | Main report | Bottom line; What we know (items 1–13); Strongly suspect; Remains unknown (table); Most valuable discoveries; Next experiments; Files produced |
| `script-analysis.md` | `Script.xml` | 1 What the file is · 2 Data model (roots, tree, CommunicationModel, effect unions, relationships) · 3 Address system (+ anomaly, SystemController discrepancy) · 4 Data types table · 5 MIDI/SysEx/file references |
| `initialdata-analysis.md` | `.a8e`, `.a8l` | Byte-offset tables for both formats; block table; correspondence to Script.xml; unknowns |
| `smf-export-analysis.md` | `../dumps/*.mid` | Message table (order, sizes, delays); what it settles (items 1–7); still open; safety note |
| `bulkdump-analysis.md` | `../captures/bulkdump/*.syx` (the synth's Bulk Dump), `../captures/rq1/*.syx` (our RQ1 file's replies) | Bulk Dump wire format (model 7F, 7-in-8), image map, bit-packed patch records rebuilt = backup, FAVORITE memories, System Common; SystemController 0x50, Temporary follows panel, panel volume = FAVORITE value |
| `mitm-capture-analysis.md` | `../captures/mitm/*.txt` (Editor/Librarian ↔ synth via MIDI-OX), `../captures/backup/*.mid` | Identity Reply, RQ1 replies, READ/SYNC/Read Selected sequences, factory mapping + wave numbering confirmed, forum-patch diffs, `patchCategory` numbering |
| `live-capture-analysis.md` | `../captures/live/*.txt` (Editor/Librarian live output, loopback) | Summary; findings 1–5 (value-edit DT1s, `00 81` settled, effect type change, Identity Request gating, name RQ1); settled/open table; consequences |
| `third-party-patches-analysis.md` | `../patches/*.a8e` | Claim-vs-data table; what this changes (items 1–6); SearingGtr 1 = factory Lead Guitar #1; provenance |
| `owners-manual-analysis.md` | `../docs/AX-Synth_OM.pdf` | 1 Factory Tone list · 2 UI constraints (3-character display, WRITE) · 3 Power-on functions · 4 Confirmations · 5 Performance controls · 6 Implications for the goal · 7 Terminology |
| `roland-installation-inventory.md` | All installation files + external docs | Per-file purpose/relevance; what was searched for and absent |
| `online-research.md` | Web/GitHub | Exact-term search results; third-party evidence; common "Koa" editor framework |

## Question → where to look

| Question | Answer location |
|---|---|
| Absolute address / type / range / default / enum labels of parameter X | `generated/parameters.csv` (or `.json`); code: `axsynth.schema.Schema.parameters()` |
| Raw Script.xml element for X (with line number) | `script-schema.json` → `structTypes.<Type>.children[]` (`line` field) |
| Does X match the official doc? | `generated/crosscheck-midi-implementation.md`; machine: `generated/crosscheck.json` keyed `"<StructType>:<offset int>"` |
| Which MFX/chorus/reverb parameters apply to effect type N | `script-schema.json` → `effect_unions.{mfx,chorus,reverb}.groups[N]`; MFX names: `effect_unions.mfx.display_names.names[N]` |
| How to make a sound (bright, hollow, breathy …; brass, strings, organ, drums …) | **`../knowledge/sound-design/`** (README, `sound-design.md`), `../knowledge/sound_design.toml` (principles, descriptors), `../knowledge/sound_recipes.toml` (recipes); code: `axsynth.knowledge.descriptor('warm')`, `.recipe(id)`. Per-article reasoning: `../knowledge/sound-design/digests/` |
| What a parameter/effect *does* to the sound | **`../knowledge/`**: `knowledge.md` (read), `knowledge.json` (machine), `*.toml` (source); code: `axsynth.knowledge.describe(path)`. Raw source text: `generated/editor-manual.pdf.txt` (parameter guide p.9–43, Effects List p.44–78) |
| Which effect parameters are `#` (real-time controllable) | `../knowledge/knowledge.json` → `mfx[].params[].control` |
| Concepts (structure types, LFO fade modes, TMT, Matrix Control, …) | `../knowledge/concepts.toml` / `knowledge.md` §Concepts |
| Official byte-level spec text | `generated/midi-implementation.pdf.txt` |
| Factory sound names, family, bank/PC, memory slot | `generated/factory-tones.csv`; code: `axsynth.factory` |
| What each of the user's 256 stored sounds contains (stored name, category, waves, effects) | `generated/user-patches.csv` (from `captures/backup/`) |
| Wave names | `script-schema.json` → `stringTables.internalWaveNameTableA.items` (313; wave N ↔ item N−1 [I]) |
| Enum label table for a UI value | `script-schema.json` → `ui_bindings["fm.pat.tone[].x"].stringTableRefs` → `stringTables` |
| How a whole patch is sent | `smf-export-analysis.md`; code: `axsynth.sysex.patch_messages` |
| What the Editor sends for one knob move, an effect type change, READ/SYNC/WRITE | `live-capture-analysis.md`; decode a MIDI-OX log: `tools/midiox_log.py <log.txt>` |
| Byte layout of `.a8e` / `.a8l` | `initialdata-analysis.md`; code: `tools/a8_files.py` |
| Hardware UI limits, maintenance key combinations, controllers | `owners-manual-analysis.md` §2, §3, §5 |
| Strings inside the Roland EXEs (class names, format strings, type vocabulary) | `generated/A8EE.exe.strings.txt`, `generated/A8EL.exe.strings.txt` |
| SHA-256 of original files (immutability check) | `generated/inventory.json` |
| Open questions and planned experiments | `REPORT.md` "What remains unknown" and "Next experiment"; user-side steps in `../NEXT-STEPS.md` |

## Generated artifacts (never edit by hand; regenerate)

| Artifact | Producer |
|---|---|
| `script-schema.json` | `tools/extract_script_schema.py` |
| `generated/crosscheck-midi-implementation.md`, `generated/crosscheck.json` | `tools/crosscheck_midi_impl.py` |
| `generated/parameters.{csv,json}` | `tools/build_parameter_db.py` |
| `generated/factory-tones.{csv,json}` | `tools/extract_tone_list.py` |
| `generated/user-patches.{csv,json}` | `tools/backup_summary.py` |
| `generated/bulkdump-layout.json` | `tools/bulkdump.py solve <dump> <backup>` |
| `generated/experiment-rq1-setup-system.syx` | `tools/dump_experiment.py make-system-requests` |
| `generated/inventory.json` | `tools/inventory.py` |
| `generated/*.exe.strings.txt` | `tools/exe_strings.py` (output redirected) |
| `generated/*.pdf.txt` | `tools/pdf2txt.py` (then renamed) |
| `generated/experiment-rq1-temporary-patch.syx` | `tools/dump_experiment.py make-requests` |
| `generated/guitar{,01}-temporary.syx` | `tools/dump_experiment.py a8-to-syx` |
| `../knowledge/knowledge.{json,md}`, `../knowledge/sound-design/sound-design.md` | `tools/build_knowledge.py` (from `../knowledge/*.toml`, which are hand-extracted sources, and the digests) |
| `../reference/synth-secrets/*.md` (git-ignored) | `tools/fetch_synth_secrets.py` |

Order and exact commands: `../CLAUDE.md` §5.
