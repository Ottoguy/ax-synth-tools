# Sound-design knowledge: what settings produce what sounds

This part of the knowledge base answers questions the Roland manuals don't: *which settings make a sound bright, hollow, breathy, brassy or bell-like, and how do you build a trumpet, a string machine, a Hammond or an 808 kick on the AX-Synth?*

It is distilled from all 63 parts of Gordon Reid's **"Synth Secrets"** (Sound On Sound, May 1999 – July 2004), and every idea is mapped onto AX-Synth parameters, waves, effects and factory Tones.

## Evidence

| What | Label | Source |
|---|---|---|
| Acoustics and synthesis reasoning (principle `rule`, descriptor `meaning`, recipe `summary`, digest "Setting → sound facts") | **[3P]** | Synth Secrets, part numbers in `ss` |
| Every AX-Synth mapping: `ax` / `steps` / `performance` / `effects` entries, value hints, wave and factory Tone choices, digest "AX-Synth translation" | **[I]** | Our inference onto the AX-Synth; **not hardware-verified** |
| Parameter meanings behind every `ref` | [D] | Roland Editor manual via `../knowledge.md` |

Values are **starting points to tune by ear**. The AX-Synth's envelope times (0–127) and cutoff values have no documented Hz/ms scale. Synth Secrets settings are given for analogue synths (Minimoog, SH101, Juno, JX10 …) and have been translated approximately. The wave numbering *N* = `internalWaveNameTableA[N−1]` is strongly supported but not yet confirmed on hardware.

## Files

| File | Content | Edit? |
|---|---|---|
| `../sound_design.toml` | 27 `[[principle]]` (general rules) + 37 `[[descriptor]]` (perceptual words → acoustic cause → AX-Synth moves) | source |
| `../sound_recipes.toml` | 35 `[[recipe]]`: brass, strings, winds, organ, piano, keys, guitars, bass, drums, percussion, bells, leads, pads, choir | source |
| `digests/NN-<slug>.md` | One digest per Synth Secrets part: the setting → sound facts, numbers and recipes it contains, plus an AX-Synth translation | source (hand-written, own words) |
| `sound-design.md` | Human-readable rendering of principles, descriptors and recipes | **generated** |
| `../knowledge.json` → `sound_design` | Machine-readable, validated, with wave names, effect names and part metadata joined in | **generated** |
| `../../reference/synth-secrets/` | Local copies of the 63 articles (Markdown), fetched by `research/tools/fetch_synth_secrets.py` | **git-ignored** (copyright SOS Publications; not redistributed) |

## How to use it (LLM sound design)

1. **Understand the request in sound terms.** Map the user's words to descriptors: `axsynth.knowledge.descriptor("warm")` returns the `dark` descriptor, with its cause and the parameter moves.
2. **Pick a recipe or a factory starting point.** Recipes list factory Tones (`factory`) to start from, following Roland's tip "start from the closest patch", and suitable PCM waves (`waves`).
3. **Apply principles** as constraints and checks: e.g. `dynamics.louder_is_brighter` (couple brightness to velocity/pressure), `attack.high_harmonics_speak_later` (brass), `modulation.right_kind_per_instrument`, `layering.similar_not_identical`, `filter.resonance_sounds_electronic`.
4. **Resolve every `ref`** through the main KB (`axsynth.knowledge.param(id)`, `knowledge.md`) for its exact range, meaning and data-model address. Validate values with `axsynth.schema.encode_value`.
5. **Keep a keytar in mind:** principle `performance.controllers_over_envelopes`. Map the ribbon, mod bar, aftertouch knob and D-Beam to meaningful destinations.

For the reasoning and numbers behind an entry, open the digest of each part in `ss`. The original article is in `reference/synth-secrets/` locally, or at the URL in the digest.

## Format

All three kinds live in TOML and are validated by `research/tools/build_knowledge.py` (exit 1 on any error).

```toml
[[principle]]
id = "dynamics.louder_is_brighter"      # unique across principles/descriptors/recipes
title = "..."
rule = """..."""                        # [3P] Synth Secrets reasoning
ss = [12, 24, 25]                       # Synth Secrets part numbers (each must have a digest)
ax = [ { ref = "tone.cutoff_vel_sens", do = "positive: harder = brighter" } ]   # [I]

[[descriptor]]
id = "dark"
terms = ["dark", "dull", "warm", ...]   # words users say; used by knowledge.descriptor()
meaning = "..."                         # acoustic cause [3P]
opposite = "bright"                     # optional, must be a descriptor id
ss = [...]
ax = [ { ref, do } ]

[[recipe]]
id = "brass.synth"
name = "..."
family = "Brass/Poly Synth"             # a factory family, "SuperNATURAL", "SPECIAL" or "other"
factory = ["Analog Brass", ...]         # must be factory Tone names (Owner's Manual list)
waves = [185, 177]                      # PCM wave numbers 1-313 (names joined in the JSON)
ss = [...]
summary = """..."""
steps       = [ { ref, set, why } ]     # the patch itself
performance = [ { ref, set, why } ]     # controllers, mono/legato, bend, matrix routings
effects     = [ { ref, set, why } ]
pitfalls = ["..."]
```

`ref` is a main-KB id (param, group or concept; see `../knowledge.md`), or `mfx:N` (1–78), `chorus:N` (1–2), `reverb:N` (1–4), `wave:N` (1–313).

## Regenerate

```
py -3 research/tools/fetch_synth_secrets.py        # only if reference/synth-secrets/ is missing (network)
py -3 research/tools/build_knowledge.py            # validate + write knowledge.json, knowledge.md, sound-design.md
py -3 -m unittest discover -s tests                 # KnowledgeBase tests check the JSON is current
```

## Coverage and limits

- All 63 parts are digested, and every part is cited by at least one principle, descriptor or recipe.
- Parts that are mostly background theory (digital logic in SS60, sampling theory in SS17, keyboard scanning in SS21) have short digests.
- Some Synth Secrets techniques have **no direct AX-Synth equivalent**. The digests say so and give substitutes:
  - oscillator hard sync → wave 219 "Sync Sweep" or FXM + Matrix
  - true PWM → two saws, one pitch-modulated (SS47)
  - audio-rate LFO growl → fast LFO/random
  - self-oscillating filter as a sine source → unverified
  - external input/vocoder → none
  - spring reverb → SRV PLATE/REVERB
- Synth Secrets predates the AX-Synth and is about analogue/modular synths. The AX-Synth is a PCM "wave + TVF + TVA" engine with 4 tones per patch, so for acoustic instruments (piano, guitar, cymbals) its PCM waves beat any synthesis recipe. The recipes say so.
