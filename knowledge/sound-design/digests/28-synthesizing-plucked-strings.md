# SS28 Synthesizing Plucked Strings (Aug 2001): digest

Source: Synth Secrets part 28, https://www.soundonsound.com/techniques/synthesizing-plucked-strings. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Plucking a string at its centre gives a triangle-like start: odd harmonics only, amplitudes 1/n². Plucking at 1/n of the length removes every nth harmonic.
  - Moving the pick position sweeps these spectral holes: a flanging-like swept-comb effect.
  - Near the bridge = thin, bright, nasal; near the middle = round, hollow, warm.
- A soft, wide pluck (thumb) rounds the kink, acting as a low-pass: warmer, darker. A thin, hard pick is brighter. Pick hardness ≈ brightness of the attack.
- The soundboard/plate has inharmonic modes (a plate alone goes "boing"). String and body are coupled resonators: within a few cycles the body changes the string's waveform, adding modes not present in the pluck.
- The hollow body adds low-frequency comb-like resonances (bass-reflex-like air resonance) and back-plate resonances.
- **Amplitude:**
  - a pluck perpendicular to the top gives a higher initial peak with a faster decay
  - a pluck parallel to the top gives a lower peak with a slower decay
  - real plucks mix both: a fast initial drop, then a long tail (a two-slope decay)
- Sympathetic resonance of the undamped strings changes the tone. Strings are slightly inharmonic: high, loud partials are sharpened ("stretched").
- The radiated sound varies by up to 20 dB per frequency with listening position.
- Reid's conclusion: an authentic acoustic guitar is beyond analogue subtractive synthesis. **Only digital (sample/model) will do.**

## AX-Synth translation [I]
- Use PCM, which the AX-Synth has: 49–51 "Brt N.Gtr p/mf/ff" (nylon, velocity-layered), 52–54 "Ac.Gtr mp/mf/ff", 55 "Jazz Gtr", 56 "Clean Gtr", 57 "Bright Strat", 63 "Harp", 64–66 sitar, 67 "Santur", 68 "Dulcimer".
  - Velocity layers: `tmt.velo_lower`/`tmt.velo_upper` with fades across the p/mf/ff waves.
  - Keep the wave's own attack (`wave.oneshot_loop`: don't reshape the attack of an acoustic PCM with the envelope).
- Pick hardness → brightness: `tone.cutoff_vel_sens` + (with LPF2/LPF3 for natural response), `tone.fenv_vel_sens` +.
- Two-slope decay: TVA T1 = 0, L1 127, T2 short, L2 ≈ 70–90, T3 long, L3 = 0 (with `tone.env_mode` NO-SUS for loop waves). `tone.aenv_time_kf` + (high notes decay faster).
- Brightness fades faster than loudness: TVF env L1 high → lower L2/L3 with a shorter T2 than the TVA.
- Pick-position comb sweep: MFX 24 FLANGER with slow or no modulation (static comb colour), or 11 PHASER.
- Stretched partials/inharmonic body: `common.stretch_tune` (for piano-like stretch across the keyboard). There's no per-partial stretch.
- Sympathetic resonance: MFX 78 SYMPATHETIC RESONANCE (designed for piano damper resonance; may add string-like sympathetic ring — try it).
