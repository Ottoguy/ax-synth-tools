# AX-Synth knowledge base

What every AX-Synth parameter and effect type **means**, in Roland's own words, linked to the exact data-model values (`research/script-schema.json`) that store it. It's meant for LLM sound design, for humans, and for a future simplified GUI.

## Sources

| Code | Document | Coverage |
|---|---|---|
| **EM** | AX-Synth **Editor** manual (`docs/AX-SynthEditorManualE.pdf`, text: `research/generated/editor-manual.pdf.txt`) | System (p.12–13), effect routing (p.14–17), patch parameters (p.18–43), Effects List: all 78 MFX + chorus + reverb (p.44–78), concepts (p.9–11) |
| **OM** | AX-Synth **Owner's Manual** (`docs/AX-Synth_OM.pdf`) | Performance controllers, SuperNATURAL portamento mode |
| **MI** | AX-Synth **MIDI Implementation** (`docs/AX Synth docs.pdf`) | Setup block, patch category, wave group, "ignored" output-assign values |

The Owner's Manual itself has no parameter explanations; the Editor manual is the main source. Page numbers are the printed page numbers of each document.

## Files

| File | Content | Edit? |
|---|---|---|
| `concepts.toml` | 24 concepts: architecture, signal path, polyphony, memory, structure types 1–10, booster, ring mod, FXM, waves, tone delay, LFO fade modes, TMT, Matrix Control, MFX control, STEP RESET, 3D effects, scale tunings, controllers, Roland's editing tips | source |
| `system.toml` | System Common / Controller and Setup parameters | source |
| `patch.toml` | Patch Common, portamento, bend, offsets, structure/TMT, tone WG / tone delay / pitch env / TVF / TVF env / TVA / TVA env / output / LFO / step LFO / control switches, Matrix Control, MFX routing and control, chorus/reverb unit settings | source |
| `mfx-01-42.toml`, `mfx-43-78.toml` | All 78 MFX types with every parameter | source |
| `chorus_reverb.toml` | Chorus unit types (CHORUS, DELAY) and reverb unit types (REVERB, SRV ROOM/HALL/PLATE) | source |
| `sound_design.toml`, `sound_recipes.toml` | **Sound design** (not from Roland): 27 principles, 37 descriptors (words → settings), 35 instrument/sound recipes distilled from Gordon Reid's *Synth Secrets* [3P] and mapped onto AX-Synth parameters [I]. See `sound-design/README.md` | source |
| `sound-design/digests/` | One digest per Synth Secrets part (63), with an AX-Synth translation | source |
| `sound-design/sound-design.md` | Rendering of the sound-design entries | **generated** |
| `knowledge.json` | Everything above, validated, with data-model facts joined in (`sound_design` section for the Synth Secrets material) | **generated** |
| `knowledge.md` | Human-readable rendering of everything | **generated** |

Regenerate and validate: `py -3 research/tools/build_knowledge.py` (exit code 1 on any broken link). Test: `tests/test_schema.py::KnowledgeBase` (also checks that `knowledge.json` is current).

## TOML format

Why TOML: human-readable, and machine-readable with Python's standard library (`tomllib`).

```toml
[[concept]]            # an explanation that isn't a single parameter
id = "structure.types" # unique across concepts, groups and params
title = "…"
doc = "EM"             # EM | OM | MI
pages = [27, 28]
text = """…"""         # faithful extraction from the manual
schema = ["fm.pat.tmt.structureType12"]   # optional: related data-model paths or structs
related = ["tmt.structure"]               # optional: ids of other entries
notes = ["…"]          # optional: project-side facts, labelled [F]/[D]/[3P]/[I]

[[group]]              # a parameter group (manual section)
id, title, doc, pages, text

[[param]]              # one parameter (or a family: L0–L4, STEP 1–16, SOURCE 1–4, …)
id = "tone.cutoff"
group = "tone.tvf"
label = "CUTOFF (Cutoff Frequency)"        # as printed in the manual
schema = ["fm.pat.tone[].tvfCutoffFrequency"]   # "[]" = every tone / array element
values = "0–127"                           # as printed (display values, not raw)
meaning = "…"
matrix = "CUTOFF"      # optional: Matrix Control destination that modulates it
notes = ["…"]
doc = "EM"
pages = [22, 32]

[[mfx]]                # also [[chorus]], [[reverb]]
number = 39            # = stored type value (mfxType / chorusType / reverbType)
name = "GUITAR AMP SIMULATOR"   # = A8EE.exe display name (validated)
manual_name = "…"      # only when printed differently (e.g. "2 BAND CHORUS", "OVERDRIVE → CHORUS")
category = "DYNAMICS"; pages = [60]; description = "…"; notes = ["…"]

[[mfx.param]]
label = "Pre Amp Volume"
schema = ["ampVolume"]  # member names inside this type's union group (full path: fm.pat.mfx.guitarAmpSimulator-ampVolume)
values = "0–127"
meaning = "…"
control = true          # manual '#': usable as Multi-Effect Control / Matrix Control destination.
                        # "#1"/"#2" = linked pair; a list = only those members are '#'
```

## `knowledge.json` structure

```
meta      {title, generated_by, sources, files, note}
concepts  [concept + file]
groups    [group + file]
params    [param + file + model: [facts per schema path]]
mfx | chorus | reverb  [effect + file + params: [param + model: [...]] + schema_only_members]
coverage  {data_model_values_without_kb_entry: [...], schema_only_effect_members: {kind: {number: [...]}}}
```

Each `model` entry (joined from the data model; never hand-typed) contains:
- `path`, `instances`, `addresses` (every tone/array instance), `type`, `size`
- `raw_range`, `default`: **stored** values
- `enum`, `enum_values`, `display_offset`: labels are ui-derived. `enum[i]` labels raw `enum_values[i]` if given, otherwise raw `raw_range[0] + i`; displayed number = raw + `display_offset`.
- `doc_confirmed` (the official MIDI Implementation agrees), `source_line` (Script.xml)

`values` in the TOML are what the manual prints (display units), while `raw_range` is what's stored. Example: MFX Rate prints "0.05–10.00 Hz" but is stored as raw 32769–32968.

Lookup from code: `axsynth.knowledge.describe("fm.pat.tone[2].tvfCutoffFrequency")`, `.effect("mfx", 39)`, `.concept(id)`, `.param(id)`; sound design: `.descriptor("warm")`, `.recipe("brass.synth")`, `.principle(id)`, `.sound_design()`.

## Coverage (as validated)

- **Every** non-reserved value in the `fm` data model has an entry. The only undocumented values are 13 `reserve*` bytes.
- All 78 MFX types, 2 chorus types and 4 reverb types; 697 effect-parameter rows linking to effect members.
- **172 effect members exist in the data model but not in the manual**: all are tempo-sync variants (`…Sync`, `…Note`) of rate/delay-time parameters, inherited from the Fantom-X-class engine. The AX-Synth manual only documents the Hz/msec form, and the step flanger's "note value of a specified tempo" is the only hint. Treat them as undocumented and leave them at their defaults unless verified on hardware.

## Conventions and limits

- **Faithful extraction.** Wording is condensed from the manual, not embellished. Obvious manual typos are kept visible in `notes` rather than silently fixed.
- **`notes` evidence labels:** **[F]** our Roland files, **[D]** Roland documentation, **[3P]** third party, **[I]** inference. Anything without a label is from the entry's `doc`.
- **`matrix` field.** The manual marks Matrix-controllable parameters with a symbol that was lost in text extraction, so `matrix` links each parameter to the matching destination name in the Matrix Control DESTINATION list (EM p.42).
- **Combination MFX (66–77).** Their one-line descriptions ("X followed by Y, in series") come from the Effects List intro ("effects connected in series", p.44) and the manual's signal-flow diagrams; the manual prints no separate prose for them.
- **Not included:** signal-flow diagrams (only described in text), the Editor's UI operation (menus, buttons), and wave names. Wave names are in `research/script-schema.json` → `stringTables.internalWaveNameTableA`; the factory sound list is `research/generated/factory-tones.csv`.
