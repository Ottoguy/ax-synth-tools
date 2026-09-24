# SS08 More About Envelopes (Dec 1999): digest

Source: Synth Secrets part 8, https://www.soundonsound.com/techniques/more-about-envelopes. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- **Spit brass** contour (loudness and brightness alike): silence → a fast "psst" spike → drop to a much lower, muted level → slow swell to full volume and brightness → quick fall to silence at note-off. A plain ADSR can't do it (its peak is always at the end of the attack, and sustain starts where the decay ends).
- Envelope families: AR, AD, trapezoid (A-hold-R), ADSR, DAR (delay-attack-release; delay is good for delayed vibrato), ADSHR (hold after release), and Alpha-Juno-style 4 times + 3 levels (T1 L1 T2 L2 T3 L3(sustain) T4).
- A multi-level envelope can imitate any simpler one:
  - sustain = max → trapezoid
  - sustain = 0 with release = decay → AD/AR
  - L2 as a break point (ADBSSR)
- Lowering L1 below the later levels gives the spit brass swell.
- Parameter resolution matters: 5-bit (0–31) steps are too coarse for fine attack timing. 7-bit (0–127) is typical.
- Choose the instrument/engine for the sound you want.

## AX-Synth translation
- The AX-Synth envelopes **are** the flexible type:
  - TVA: T1–T4 with L1–L3; start and end fixed at 0
  - TVF and pitch: T1–T4 with L0–L4; start and end levels free
  - `tone.aenv_times`, `tone.aenv_levels`, `tone.fenv_times`, `tone.fenv_levels`, `tone.penv_times`, `tone.penv_levels`, all 0–127
- **Spit brass on the AX-Synth:**
  - TVA: T1 very short (~0–5), L1 high (~110–127), T2 short (~10–20), L2 low (~50–70), T3 long (~60–90, the swell), L3 (sustain) 127, T4 short (~10–25)
  - TVF: the same shape, with `tone.fenv_depth` positive
  - Exact numbers are a starting point [I]; tune by ear.
- Delayed vibrato (the DAR use case): `tone.lfo_fade_mode` ON-IN + `tone.lfo_delay` + `tone.lfo_fade_time`.
- "Hold after release": `tone.lfo_fade_mode` OFF-OUT for the LFO. Amplitude hold isn't available beyond the TVA T4 release and hold pedal (`tone.rcv_hold`, `tone.redamper`).
