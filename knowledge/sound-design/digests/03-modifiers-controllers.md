# SS03 Modifiers & Controllers (Jul 1999): digest

Source: Synth Secrets part 3, https://www.soundonsound.com/techniques/modifiers-controllers. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Static, unchanging tones are musically dull, and no natural sound is stationary. A sound needs loudness (and tone) contours over time.
- ADSR: Attack = time to reach peak; Decay = time to fall to the sustain level; Sustain = level held while the key is down; Release = time to fade after key-up.
- Envelope archetypes:
  - **Organ:** instant attack, full sustain, instant release. A rectangular "organ envelope".
  - **Trombone/brass:** moderate attack, a peak, a moderate decay to a moderate sustain, a fairly quick release when blowing stops.
  - **Thunderclap:** slowish rise, no sustain, long die-away after the peak (A + long D, S = 0).
- LFO (≈0.1–20 Hz) on amplifier gain = tremolo. LFOs pushed into the audio range = modulation that changes timbre (AM/FM, later parts).
- Modules are generators, modifiers (VCA, VCF) or controllers (EG, LFO). The same signal can be audio or control: the destination defines its role.

## AX-Synth translation
- TVA envelope = the amplitude ADSR: `tone.aenv_times` T1 (attack), T2/T3 (decay), `tone.aenv_levels` L3 (sustain), T4 (release). The Editor's SUMMARY A/D/S/R = T1/T3/L3/T4 (`editing.summary_adsr`).
  - organ: T1 ≈ 0, L1–L3 = 127, T4 ≈ 0–5
  - brass: T1 moderate (~20–40), L1 = 127, L2/L3 ≈ 80–100, T4 short–moderate
  - thunder: T1 moderate–long, L3 = 0, T3 long, and `tone.env_mode` NO-SUS if the wave loops
- Tremolo: `tone.lfo_depth_tva` with `tone.lfo_waveform` SIN/TRI and `tone.lfo_rate`, or the TREMOLO MFX.
- Patch-wide attack/release trims: `common.offset_attack`, `common.offset_release` (64 = no change).
