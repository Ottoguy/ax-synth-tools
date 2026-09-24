# SS46 Synthesizing Strings: String Machines (Feb 2003): digest

Source: Synth Secrets part 46, https://www.soundonsound.com/techniques/synthesizing-strings-string-machines. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- String machines (Freeman String Synth, Solina, ARP Omni, Logan …) are loved instruments in their own right, not realistic strings.
- **Detune:** two oscillators a few Hz apart beat at the difference frequency. Detuned **saws** give a thicker, less pronounced beating.
  - Small detune = thickening; large detune = an "off-colour" honky-tonk sound (wrong for strings).
- **String-machine recipe (Jupiter 6):**
  1. Two **sawtooths**, minimal detune.
  2. Subtle vibrato (triangle LFO) on **one oscillator only**, so the detune amount itself wobbles. Best when the LFO rate differs from the beat rate.
  3. Replace the regular LFO with **random (S&H) at minimal depth**: no periodic wobble, a "thick and unstable", human/analogue character. Too much depth = unnatural pitch jumps.
  4. **No velocity** (string machines weren't dynamic).
  5. LPF about **half closed**, moderate key follow (brighter upward), **no filter envelope/modulation**.
  6. VCA **trapezoid**: a slow crescendo attack, full sustain, a long release tail.
  - This gives a "carpet" pad. For true ensemble sheen, add **chorus** (e.g. a Roland Dimension C gives Pink Floyd-style ARP Omni strings).
- **PWM:** a triangle-modulated pulse contains two pitches wobbling around the note (inherently chorused). Two detuned PWM oscillators = four pitches: much lusher. Adding saws removes PWM's slight hollowness.
- Variations: VCO2 an octave down (weight), longer attack/release (dreamy pads).
- Summing same-frequency sines always gives a sine. Complex (quasi-aperiodic) modulation needs several LFOs at unrelated rates, which gives a human feel.

## AX-Synth translation (string machine / pad) [I]
- Waves: tone 1 saw (e.g. 185 "JP-8 Saw"), tone 2 saw (e.g. 174 "Juno Saw HD" or the same) with `tone.fine_tune` +4…+8. Or ready PCM: 124 "Warm Pad", 125/126 "OB2 Pad", 121 "Unison Saw", 301–304 string ensembles.
- Detune wobble:
  - LFO1 TRI on tone 1 only, small `tone.lfo_depth_pitch`, `tone.lfo_rate` ≈ slow (distinct from the beat rate)
  - or `tone.lfo_waveform` RND/S&H at a tiny depth
  - plus `common.analog_feel` ≈ 20–40 for 1/f instability
  - `tone.lfo_rate_detune` for per-note rate variation
- No velocity: `tone.tva_vel_curve` FIX (or `tone.tva_vel_sens` 0), `tone.cutoff_vel_sens` 0.
- Filter: LPF, `tone.cutoff` ≈ 60–75, `tone.resonance` 0–10, `tone.cutoff_kf` ≈ +30…+50, `tone.fenv_depth` 0.
- TVA trapezoid: T1 ≈ 40–70 (crescendo), L1–L3 127, T4 ≈ 50–80.
- Sheen: `chorus.type` CHORUS with `chorus.level` high, or MFX 28 SPACE-D (Dimension-style), 26 HEXA-CHORUS, 23 CHORUS.
- PWM substitute: two saw tones, one with a tiny square/triangle LFO on pitch (SS47, the best method). Or pulse waves 207–209 on two tones detuned + chorus, or the booster trick (`structure.booster`).
- Weight: tone 2 `tone.coarse_tune` −12. Dreamy: longer T1/T4 + reverb SRV HALL.
