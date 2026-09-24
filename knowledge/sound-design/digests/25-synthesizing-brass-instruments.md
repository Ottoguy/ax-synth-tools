# SS25 Synthesizing Brass Instruments (May 2001): digest

Source: Synth Secrets part 25, https://www.soundonsound.com/techniques/synthesizing-brass-instruments. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Instruments with the same harmonic series are told apart by:
  1. the loudness contour
  2. the tone (brightness) contour
  3. the pitch contour
  4. formants
  5. noise content
- **Amplitude:**
  - Soft or vigorous blowing ≈ an ADS shape (attack, slight overshoot/decay, sustain).
  - A plosive ("T"/"D" tonguing) start = an instant spike, then a slower second rise to sustain.
  - Harder blowing gives a faster transient, so velocity should shorten the attack.
  - Then optional (delayed) tremolo, swell or diminuendo during the note, and a **very short release** when blowing stops.
  - "Swell brass" needs a multi-stage envelope. Great synth brass is still possible with a plain ADSR (Odyssey, Prophet 5, OB-X, Memorymoog).
- **Tone:**
  - Louder = more harmonics (cutoff follows loudness/velocity).
  - Resonance rising with loudness accentuates high harmonics (overblown character).
  - **Higher harmonics take longer to speak than lower ones.** Brightness rises more slowly than loudness, and this is perhaps the most important cue for identifying an instrument.
  - The initial overblown "parp" needs a filter ADSR (a bright spike, then settling).
  - Velocity controls the filter-envelope amount; pressure (aftertouch) controls the sustained brightness.
- **Pitch/growl:**
  - Brass notes have ~50 ms of pitch instability at the start (about a dozen cycles).
  - Don't modulate the oscillator pitch periodically (it causes FM sidebands). Instead modulate the **filter** with ~80 Hz triangle "growl" through a short AD envelope, so the growl exists only at the attack.
  - Aftertouch can re-introduce growl for overblown expression.
- **Vibrato:** delayed (none in the transient), ~5 Hz, very shallow, otherwise it sounds electronic. Via a ramp (AR) on the LFO amount.
- **Noise:** a low-level turbulent breath noise shaped by the instrument's formants adds realism. It should be barely audible for orchestral brass; for pan pipes it's a big part of the sound.
- Real partials are slightly stretched (sharp) at higher harmonic numbers. Additive synths do brass best, but subtractive can make "more than a passable stab".

## AX-Synth translation (brass patch recipe) [I]
- Wave: 185 "JP-8 Saw", 177 "MG Saw HD" or 174 "Juno Saw HD" (synth brass); or 114/297–300 trumpet, 115 "Tp Section", 118 "XP Brass" (realistic).
- TVA:
  - T1 ≈ 5–15 with `tone.aenv_t1_sens` +20…+40 (harder = faster attack)
  - L1 127, T2 short, L2 ≈ 100, T3 medium, L3 (sustain) ≈ 90–110
  - T4 ≈ 5–15 (short release)
  - `tone.tva_vel_sens` moderate
- TVF:
  - LPF, `tone.cutoff` ≈ 40–70, `tone.resonance` low–moderate (10–30)
  - `tone.fenv_depth` +30…+50
  - TVF env: L0 low, T1 slightly **longer** than the TVA T1 (brightness lags loudness), L1 high = the "parp", T2/T3 settling to L3 ≈ 60–80, T4 short
  - `tone.fenv_vel_sens` + (velocity → envelope amount), `tone.res_vel_sens` + (louder = more resonant)
  - `tone.cutoff_kf` ≈ +50…+80 (high notes relatively darker)
- Growl at the attack: LFO2 TRI, rate high (the maximum rate is below 80 Hz on the AX-Synth [I], so it will be a fast flutter rather than true audio-rate growl), `tone.lfo_depth_tvf` moderate, `tone.lfo_fade_mode` ON-OUT with a short `tone.lfo_delay` and `tone.lfo_fade_time` (growl only at the note start).
  - Alternative: a small pitch-envelope blip (`tone.penv_depth` small, `tone.penv_levels` L0 slightly below/above 0 → 0 within ~50 ms).
- Delayed vibrato: LFO1 SIN/TRI, rate ≈ 5 Hz feel, `tone.lfo_depth_pitch` very small, `tone.lfo_fade_mode` ON-IN, `tone.lfo_delay` ≈ 30–60, `tone.lfo_fade_time` ≈ 40–70.
- Expression:
  - aftertouch knob → brightness: `matrix.source` AFTERTOUCH → `matrix.destination` CUTOFF (+) and/or LFO TVF DEPTH (overblown growl)
  - mod bar CC01 → LFO1 PCH DEPTH (vibrato)
- Breath noise: optional 4th tone, 229 "Digi Breath" or 232 white noise, BPF around the formant (cutoff ~70–90), `tone.level` low, a short envelope at the attack.
- Mono lead brass: `common.mono_poly` MONO, `common.legato_sw` ON, `common.legato_retrigger` OFF (the Editor manual recommends OFF for wind phrases).
- Spit/swell brass: see SS08 (`tone.aenv_levels` L1 high, L2 low, long T3 to L3 = 127).
- Section fatness: 2 tones detuned ±5–10 cents (`tone.fine_tune`), chorus unit `chorus.type` CHORUS, reverb SRV HALL.
