# SS14 An Introduction To Additive Synthesis (Jun 2000): digest

Source: Synth Secrets part 14, https://www.soundonsound.com/techniques/introduction-additive-synthesis. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Additive = summing sine partials with chosen amplitudes. Nine equal-amplitude harmonics sound much brighter than a saw's 1/n series.
- A Hammond drawbar organ is a 9-partial additive synth: sine-ish tonewheels at fixed pitch ratios (16', 5⅓', 8', 4', 2⅔', 2', 1⅗', 1⅓', 1'), each at 9 levels.
- **Key secret:** any timbre, however complex, sounds static and **organ-like if it doesn't change over time**. Effects (phaser, Leslie, echo) add interest but don't change the essential nature.
- Plucked/hammered string ≈ all harmonics starting loud and bright, with higher harmonics decaying faster (harmonic n decays in T/n). The sound gets darker as it fades, equivalent to a saw + LPF with an AD envelope (A = 0, D = T).
- Letting some mid harmonics swell mid-note (not just decay) gives evolving timbres a single-filter synth can't make.
- Realism needs per-partial pitch/amplitude modulation; one LFO on everything sounds "cheesy". It also needs velocity and pressure control.
- **Sinusoids + noise:** real acoustic instruments (flute, trumpet) always carry a residual **filtered noise** component, and without it many synthesised sounds are unconvincing. The noise needs its own filter and envelope.
- Detuned octaves/fifths from two oscillators are already simple additive synthesis.

## AX-Synth translation
- Tonewheel organ additive: the AX-Synth has organ PCM (30 "JD Full Draw", 31/32 "Org Basic", 258–281 VK/Full/Jazz/Vintage organs). Additive layering: up to 4 tones with sine (220) or organ waves at `tone.coarse_tune` 0 / +12 / +19 / +24 (8', 4', 2⅔', 2'), balanced by `tone.level`.
- Anti-"static" rule: always give sustained patches some change over time:
  - TVF envelope movement (`tone.fenv_depth`)
  - slow LFO on TVF/TVA/pan (`tone.lfo_depth_tvf`, `tone.lfo_depth_pan`)
  - `common.analog_feel`
  - different LFO rates per tone (`tone.lfo_rate` differing across tones, not one shared LFO), `tone.lfo_rate_detune`
- Plucked darkening: TVF envelope with L0/L1 high → decaying to a low sustain level (`tone.fenv_levels`), `tone.fenv_time_kf` positive (faster decay at high notes), LPF.
- Evolving spectrum: tone 2 with a bright/filtered wave whose TVA rises slowly (T1 long) while tone 1 stays constant.
- "Sinusoids + noise": add a tone with a noise/breath wave (229 "Digi Breath", 228 "Shaku Noise", 232/233 white/pink noise) through BPF/LPF with its own envelope, low `tone.level`.
