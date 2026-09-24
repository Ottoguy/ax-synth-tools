# SS11 Amplitude Modulation (Mar 2000): digest

Source: Synth Secrets part 11, https://www.soundonsound.com/techniques/amplitude-modulation. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Audio-rate AM (modulator → VCA gain) creates **sum and difference** frequencies (carrier ± modulator) as well as the carrier. A **ring modulator** outputs only sum and difference (carrier and modulator removed).
- **Fixed-frequency modulator** (doesn't track the keyboard): the harmonic relationship changes with every note. Mostly **enharmonic, clangorous, aggressive**, varying dramatically across the keyboard (a few special notes sound "sweet"). Modulator level controls how enharmonic it sounds.
- **Tracking modulator** (both follow the keyboard at a fixed ratio): the same timbre on every note, i.e. a playable, new, non-harmonic tone.
- Complex waves (saw × saw) create many sidebands, i.e. very complex tones: good raw material for further filtering.
- Real VCAs leak the modulator, which adds more enharmonicity.
- Audio-rate filter modulation = each harmonic gets its own amplitude modulation, another route to complex, gritty tones.

## AX-Synth translation
- Ring mod between two tones: `tmt.structure_12`/`tmt.structure_34` TYPE 05–10 (`structure.ring_modulator`):
  - TYPE 05/09: ring mod only, balance set by the tone 1 TVA
  - TYPE 06/10: ring-modulated sound plus tone 2 mixed in (keeps some pitch focus)
  - TYPE 07/08: filter before/after the ring mod
- Ratio control: `tone.coarse_tune` / `tone.fine_tune` of the second tone sets the carrier:modulator ratio.
  - Integer/octave ratios (0, ±12, +19, +24 semitones) → more harmonic, bell- or organ-like
  - Odd intervals (e.g. +7 ± some cents, +11, +13) → clangorous metal
- Fixed vs tracking modulator: `tone.pitch_kf` on the modulator tone.
  - 100 = tracks, so the timbre stays consistent
  - 0 = fixed pitch, so the timbre changes per note (the classic enharmonic ring-mod effect)
- Sine carriers keep the result cleaner. The manual notes evenly spaced harmonics appear only if one wave is a sine (wave 220 "Sine") [D EM].
- MFX 15 RING MODULATOR (fixed-frequency ring mod on the whole patch, often with frequency modulated by an LFO/ctrl) and 16 STEP RING MODULATOR (stepped sequence of frequencies): quick "robotic/metallic/clangorous" treatments.
- Audio-rate filter modulation isn't available (the LFO rate is sub-audio). Use FXM (`tone.fxm_sw`) for grit.
