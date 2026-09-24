# SS09 An Introduction To VCAs (Jan 2000): digest

Source: Synth Secrets part 9, https://www.soundonsound.com/techniques/introduction-vcas. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Gains in series multiply. The final loudness at any instant = product of every gain stage (EG × velocity × level × LFO …).
- "Initial gain" (a constant offset added to the envelope) makes the amplifier pass sound permanently, a drone even with no key held.
- Overdriving an amplifier past its headroom clips the waveform: harsh clipping distortion during the loudest envelope stages (attack/decay peaks), which disappears as the level drops. Softer clipping (rounded) is warmer, tape-like saturation.
- "Amount"/depth controls are VCAs in the control path. They scale how much an envelope/LFO affects cutoff or amplitude relative to the initial (base) value.
  - Cutoff knob = base value; env amount = how far the envelope moves it. This is the essential pair for filter programming.

## AX-Synth translation
- Gain chain per tone:
  - `tone.level` × TVA envelope (`tone.aenv_levels`)
  - × velocity (`tone.tva_vel_sens`, `tone.tva_vel_curve`)
  - × key bias (`tone.bias_level`)
  - × LFO (`tone.lfo_depth_tva`)
  - then `common.level` and the effects output levels
- Filter base vs amount: `tone.cutoff` (base) + `tone.fenv_depth` (amount, may be negative = inverted envelope) + `tone.cutoff_vel_sens` (velocity amount).
- Clipping/overdrive character:
  - Booster (`tmt.booster_12`/`tmt.booster_34` with Structure TYPE 03/04, `tone.wave_gain` +12 dB)
  - MFX 35 OVERDRIVE, 36 DISTORTION, 37/38 VS OVERDRIVE/DISTORTION, 39 GUITAR AMP SIMULATOR
  - Soft saturation: MFX 57 LOFI COMPRESS, or low-drive OVERDRIVE.
- There's no "initial gain" drone. For a sustaining drone use a looping wave with TVA sustain L3 = 127 and `tone.env_mode` SUSTAIN (it still stops at note-off plus release; with the hold pedal it continues).
