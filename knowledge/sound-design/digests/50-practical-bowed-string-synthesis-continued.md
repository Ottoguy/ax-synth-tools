# SS50 Practical Bowed-string Synthesis (continued) (Jun 2003): digest

Source: Synth Secrets part 50, https://www.soundonsound.com/techniques/practical-bowed-string-synthesis-continued. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- **Korg MS-20 violin:**
  - one saw at 4', a little portamento
  - lower the LPF a bit (tames the "electronic" brightness)
  - but a strong HPF **guts the sound** (an annoying buzz), and **any resonance makes it sound electronic**
  - not every synth's filters suit every sound
- **Envelope:** no hold/delay; non-zero attack and release (so it's not organ-like); preferably a **slight bump at the start** (attack overshoot, then a slightly lower sustain).
- **Delayed vibrato** = an LFO through a VCA whose gain rises (a hold-attack envelope) after the note starts. Pitch only, no filter modulation (that gives a "wow").
- LPF key tracking at ~50 %: brighter high notes, duller low notes.
- **Pitch bend ±2 semitones** is "musically pleasing" for violin.
- **Modular violin (the best result):**
  - saw → **resonant HPF just below self-oscillation at ~700 Hz** (one big low-mid body resonance) → a fixed filter bank for the plateau and roll-offs (in series, so the responses multiply) → VCA → **spring reverb**
  - **no envelope:** a joystick Y axis controls **both loudness and vibrato depth**; X = pitch bend
  - Hand-controlled articulation (slow or fast note entry, bow speed/pressure mid-note, bends) is **far more human** than envelopes: "it's not the complexity of the patch that creates the performance. It's the performance."

## AX-Synth translation (expressive keytar violin) [I]
- Base patch:
  - saw at +12, LPF `tone.cutoff` ≈ 85–95, `tone.resonance` 0
  - `tone.cutoff_kf` ≈ +50
  - PKG filter at ≈ 700 Hz for the body bump (`tone.filter_type` PKG, `tone.cutoff_kf` 0, moderate `tone.resonance`), or MFX 1 EQUALIZER
- TVA "bump": T1 ≈ 20–30, L1 127, T2 short, L2/L3 ≈ 105–115, T4 ≈ 20–30.
- Delayed vibrato: pitch only, `tone.lfo_fade_mode` ON-IN (`tone.lfo_delay`, `tone.lfo_fade_time`), `tone.lfo_depth_tvf` 0.
- **Performance-controlled loudness (the SS50 lesson):**
  - Matrix Control `matrix.source` AFTERTOUCH (the AX-Synth aftertouch *knob*) or CC01 (mod bar) → `matrix.destination` LEVEL (+) **and** LFO1 PCH DEPTH (+), with `matrix.sens` +
  - Keep `tone.level` low enough that the controller adds the swell. Or put the same source on CUTOFF for bow-pressure brightness.
  - The D-Beam (assignable CC, a system setting `system.beam_assign`) can be the "bow" hand: map its CC as the matrix source [D OM: beam CC01–95].
- Bend: `common.bend_up`/`common.bend_down` 2 via the ribbon.
- Reverb: SRV ROOM/HALL. The AX-Synth has no spring reverb; SRV PLATE or REVERB can substitute.
