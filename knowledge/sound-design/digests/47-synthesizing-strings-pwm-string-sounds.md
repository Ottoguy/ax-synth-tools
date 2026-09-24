# SS47 Synthesizing Strings: PWM & String Sounds (Mar 2003): digest

Source: Synth Secrets part 47, https://www.soundonsound.com/techniques/synthesizing-strings-pwm-string-sounds. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- **Pulse spectra follow a sinc envelope.**
  - Every nth harmonic is missing for a 1/n duty cycle, but below 33 % the remaining amplitudes are *not* 1/n.
  - Narrow pulses have a flatter, "buzzier" spectrum.
  - A "saw spectrum with holes" is a staircase wave, not a pulse.
- **PWM = two signals**, one frequency-modulated against the other (the rising and falling edges behave like two oscillators), which is why PWM sounds chorused.
- **PWM without PWM:** mix **two sawtooth oscillators** and apply slight **pitch modulation to one of them** (a square- or triangle-wave LFO at a small depth). This sounds all but identical to a single PWM oscillator. Adding a small static detune on top gives an even warmer result than a Juno's PWM.
- **Korg T2 (M1 engine) PWM strings:**
  - two saws at 16', filters ≈ 75/99 with slight key tracking, no filter envelope
  - amp: a **fast-but-smooth attack**, full sustain, a gentle release (≈ half)
  - amp key tracking **negative** (weights loudness toward the bass: warmer)
  - velocity 0
  - pitch LFO **square**, fairly fast, intensity 2 (tiny), on osc 2 only
  - osc 2 detune ≈ 10
  - then EQ, chorus and a splash of reverb for a convincing vintage ensemble
- **Super JX10 PWM string patch:**
  - DCO1 saw 8', LFO depth 2 (square LFO, rate 78/99); DCO2 saw 8', fine −4 cents; mixed equally
  - LPF 47/99, no resonance, envelope amount 14 with ENV1 (A 15, S 99, R 39), key follow 64 %
  - VCA ENV2 (A 45, S 99, R 54); no dynamics; chorus off
  - "Smoother, stringier, more usable in a mix" than the Jupiter 6's real PWM.
- **Layering** a second, slightly different string patch (different LFO rate/depth, oscillator detune and filter/envelope) hides any periodic modulation, so the ear can't separate them: rich, deep. Then chorus both: "far better than most string machines".
- Three layers at 16'/8'/4' emulate the cello/viola/violin registers of better ensembles.

## AX-Synth translation (this is directly doable) [I]
- **PWM strings on the AX-Synth:**
  - Tone 1 and tone 2: the same saw (e.g. 185 "JP-8 Saw" or 174 "Juno Saw HD"), Structure TYPE 01.
  - Tone 2: `tone.fine_tune` −4…−10.
  - Tone 1 only: `tone.lfo_waveform` SQR (or TRI), `tone.lfo_rate` ≈ 70–90 (fairly fast), `tone.lfo_depth_pitch` very small (1–3).
  - Both: `tone.filter_type` LPF, `tone.cutoff` ≈ 60–75, `tone.resonance` 0, `tone.cutoff_kf` ≈ +40…+60; TVF env small (+10…+15) with a medium attack.
  - TVA: T1 ≈ 30–50, L1–L3 127, T4 ≈ 50–65; `tone.tva_vel_sens` 0.
  - `tone.bias_level` negative with `tone.bias_direction` toward the high keys (quieter high end = warmer) [I: check the direction semantics in `knowledge.md`].
- Layer 2 (tones 3+4): the same idea with a different LFO rate/depth, a different detune and a slightly different cutoff, optionally `tone.coarse_tune` −12 (cello register) or +12 (violins).
- Finish: `chorus.type` CHORUS (`chorus.level` moderate) or MFX 28 SPACE-D / 26 HEXA-CHORUS, plus reverb.
- This supersedes the "no PWM" caveat: saw + pitch-modulated saw **is** the PWM sound.
