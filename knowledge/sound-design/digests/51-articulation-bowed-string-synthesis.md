# SS51 Articulation & Bowed-string Synthesis (Jul 2003): digest

Source: Synth Secrets part 51, https://www.soundonsound.com/techniques/articulation-bowed-string-synthesis. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Keyboards impose discrete, equal-tempered notes. Unfretted strings, trombone, voice and many winds play continuous pitch. Alternative temperaments don't change that philosophy.
- **Ondes Martenot control:** continuous pitch (a ring on a wire) + a pressure button for loudness (silent when released).
  - With only a **sawtooth oscillator and a VCA**, this gives violin (high) and cello/contrabass (low) imitations far better than complex keyboard patches.
  - Vibrato by wiggling the pitch finger (natural rate and depth); glide by holding loudness while moving pitch; every note uniquely articulated.
- Gate-only (organ) articulation of a saw = a 1970s prog organ-like sound, not a bowed string.
- Mapping one controller to both **loudness and waveform/brightness** (saw → triangle as it gets quieter) reproduces the natural rule: **quieter = fewer high harmonics** (blown, bowed, strummed and struck instruments alike).
- **Brass via the filter:** replace the VCA with a low-pass VCF whose initial cutoff is 0 and put the pressure control on the cutoff. Silence between notes, and the swell brightens and louder together: magic brass, swells, pitch slips, trombone slides; 2 octaves down = the most realistic analogue tuba. Add a good reverb.
- **Synth Secret:** two modules and an appropriate controller can be more expressive and realistic than many modules driven by an unsuitable controller.

## AX-Synth translation (keytar expressiveness) [I]
- The AX-Synth *is* a performance controller:
  - **ribbon** = continuous pitch (bend)
  - **aftertouch knob** = channel aftertouch (a continuous "button")
  - **mod bar** = CC01
  - **D-Beam** = a hand-distance CC
- **Martenot-style strings/brass:**
  - Matrix `matrix.source` AFTERTOUCH (or CC01, or the D-Beam CC) → `matrix.destination` LEVEL (+) and CUTOFF (+) with suitable `matrix.sens`
  - TVA sustain L3 127 with a short attack; low `tone.level` so the controller provides the swell
  - For the brass variant: `tone.cutoff` near 0 so the note is silent or dark until the controller opens it (the filter gates the note)
- Fretless slides and vibrato on the ribbon: a wider `common.bend_up`/`common.bend_down` (e.g. 12) for trombone/violin slides; small (2) for subtle bends. The ribbon's BENDER MODE is a system/controller setting (`controllers` concept in `knowledge.md`).
- The loudness ↔ brightness coupling on one control is always good for acoustic imitation: a single matrix source to both LEVEL and CUTOFF.
- Tuba: the same brass patch at `tone.coarse_tune` −24 (or `common.octave_shift` −2), + reverb.
- D-Beam FILTER mode (a system setting) gives hand-controlled cutoff for any patch [D OM].
