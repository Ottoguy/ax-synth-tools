# SS13 More On Frequency Modulation (May 2000): digest

Source: Synth Secrets part 13, https://www.soundonsound.com/techniques/more-frequency-modulation. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Carrier:modulator (C:M) ratio decides the spectrum (β = index decides the amplitudes, via Bessel functions):
  - **1:1** → all harmonics ≈ a **filtered sawtooth**
  - **1:2** → odd harmonics only ≈ a **filtered square** (hollow)
  - **1:3** ≈ a 33 % pulse
  - **1:4** ≈ square-like
  - **non-integer ratios** → enharmonic (bells, metal, clangs); the carrier is no longer the lowest partial
- Increasing β moves energy outward into higher sidebands, so the sound gets brighter. At some β values the carrier vanishes. Low β gives just a few harmonics, "filtered".
- Enveloping the modulator level produces dramatic timbre sweeps, often sci-fi. With a percussive carrier envelope, simple 2-operator FM makes excellent drums/percussion.
- Operators and algorithms: stack modulators for complex attack partials, and sum carriers as separate partials. Example: one carrier pair sustains an evolving tone while a cascaded stack adds a complex attack partial.
- Two modulators on one carrier ≈ the sum of the two individual results.
- Feedback (an operator modulating itself) turns a sine into a saw-like wave, with brightness set by the feedback amount. Cross-feedback between operators at non-integer ratios becomes **noise** (useful for percussion).

## AX-Synth translation
- FXM approximates this family. `tone.fxm_depth` ≈ β (brightness); `tone.fxm_color` changes the character (low = metallic, high = grainy). The ratio can't be set directly.
- For a "filtered saw/square via FM" there's no need for FXM: use saw/square PCM + LPF (cheaper and predictable).
- Enharmonic FM bells: FXM on bell/sine waves, or Structure ring mod with non-octave `tone.coarse_tune` intervals (`structure.ring_modulator`), plus a short percussive TVA.
- Operator stacking ≈ AX-Synth tone layering: up to 4 tones, each with its own wave and envelopes (`tmt.tone_switch`). E.g. tone 1 = sustained body, tone 2 = short bright attack partial (fast-decaying TVA, a different wave or FXM on).
- FM drums: FXM with high depth on a sine/triangle, a fast pitch envelope (`tone.penv_depth`), and a short TVA.
