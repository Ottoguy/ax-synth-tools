# SS06 Of Responses & Resonance (Oct 1999): digest

Source: Synth Secrets part 6, https://www.soundonsound.com/techniques/responses-resonance. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Filter types:
  - **LPF** removes highs (duller)
  - **HPF** removes lows (thinner)
  - **BPF** keeps a band (nasal, telephone-like, focused)
  - **notch/band-reject** removes a band (hollow)
  - **comb** (see SS04)
- Static filters act as tone controls and are boring on their own. Movement comes from voltage-controlled cutoff (envelope, LFO): **filter sweeps**.
- **Resonance (Q)** boosts harmonics near the cutoff and slightly thins the lows. Low Q gives a broad, gentle emphasis; high Q a sharp, "whistling", vocal peak. Sweeping a resonant cutoff gives the classic analogue "wow/zap/squelch".
- Maximum Q makes the filter self-oscillate: a sine at the cutoff frequency, playable as an extra oscillator if it tracks the keyboard. Near self-oscillation it rings with input harmonics and gives a distinctive distortion.
- Uses:
  - static resonant peak: emphasise a band so a sound stands out in a mix
  - two or more static peaks: **formants** (voice, acoustic instrument bodies)
  - moderate Q with cutoff tracking pitch: a consistent "emphasised" character across the keyboard
  - edge-of-oscillation: off-the-wall sounds
- The filter defines a synth's character more than the oscillator does.

## AX-Synth translation
- `tone.filter_type`:
  - LPF: classic warm/dark and sweeps
  - HPF: thin, removes body (percussion, "tinny", layering a bright top)
  - BPF: nasal, focused, telephone/vocal
  - PKG (peaking): emphasises the cutoff region; with an LFO on cutoff it gives wah-wah
  - LPF2/LPF3: natural/acoustic, and they ignore resonance
- `tone.resonance`: 0–127. The manual warns that very high values can oscillate and distort [D EM p.32]; whether the TVF self-oscillates as a clean sine is unverified on hardware.
- Sweeps: TVF envelope (`tone.fenv_depth`, `tone.fenv_times`, `tone.fenv_levels`), LFO (`tone.lfo_depth_tvf`), or Matrix Control to CUTOFF (`matrix.destination`).
- Tracking: `tone.cutoff_kf` (+100 ≈ cutoff follows pitch 1:1 [I from the KF definition]).
- Patch-level "resonance" macro: `common.offset_resonance`. Real-time CC71 (resonance) and CC74 (cutoff) are received [D OM].
- Formants without two filters: MFX types (e.g. filter/EQ types in the Effects List), or the AX-Synth's formant PCM waves (234–238 "Aah/Eeh/Iih/Ooh/Uuh Formant").
