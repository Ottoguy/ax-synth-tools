# SS40 Synthesizing Bells (Aug 2002): digest

Source: Synth Secrets part 40, https://www.soundonsound.com/techniques/synthesizing-bells. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Hi-hats from the cymbal model:
  - shorter envelopes = hi-hats; very brief = the stick "tick"
  - the mix of stick impact vs body sets the character
  - varying the decay over time (open/closed) keeps it lively vs static samples
  - TR-808: six square oscillators → HPF → VCA/AR; the closed hat **chokes** the open hat's decay
- Church/hand bells are cast and lathed so their modes form a **quasi-harmonic** series (tunable, playable), unlike cymbals.
- **Three phases of a bell:**
  1. **Strike:** enharmonic metal-on-metal clang, decays fast
  2. **Strike note:** a handful of strong low partials, slightly **stretched** (sharper as they go up). The perceived pitch may be an **implied fundamental**: partials at 2:3:4 make you hear "1" (100/150/200 Hz → hear 50 Hz).
  3. **Hum:** lingering energy at a **sub-harmonic an octave below**, which dominates the tail
- **Warble** ("boii-yoy-yoy-ng"): nearly degenerate mode pairs at almost equal frequencies beat against each other.
- Synthesis:
  - strike note: additive, six sines with stretched ratios, a two-stage decay (fast peak, then slow decay); warble via an LFO on the amplitude of one of two parallel envelope/amp paths
  - clapper strike: two-operator sine FM with a shorter envelope
  - hum: two sines about an octave down, **detuned slightly to beat**, with a **slower attack and a long tail**
  - Designed for one key (≈ middle C); realistic only near there.

## AX-Synth translation (bell) [I]
- Quick route: PCM 154 "Tubular Bell", 155 "Church Bell", 148 "D-50 Bell", 146 "Glocken", 157 "JD Crystal", 161 "TinyBellWave", 160 "JD Bell Wave".
- Synthesised bell (4 tones):
  - Tone 1 (strike note): 220 "Sine" + FXM (`tone.fxm_sw`, `tone.fxm_depth` ≈ 4–8, `tone.fxm_color` 1–2) or ring mod with tone 2 (Structure TYPE 06 keeps some of tone 2 for pitch focus). TVA: T1 0, L1 127, T2 short, L2 ≈ 70, T3 long, L3 0.
  - Tone 2: sine at a stretched interval, e.g. `tone.coarse_tune` +12 `tone.fine_tune` +15…+30 (stretched octave), or +19/+24 with slight sharpening.
  - Tone 3 (hum): sine `tone.coarse_tune` −12, T1 slower (≈ 20–40), long T3.
  - Tone 4: the same as tone 3 but `tone.fine_tune` +2…+4 cents, so it **beats** (warble/hum beating).
  - Clapper: a short FXM burst on a tone, or MFX 15 RING MODULATOR lightly.
- Warble alternative: `tone.lfo_depth_tva` small with `tone.lfo_rate` ≈ 3–6 Hz on the strike-note tone.
- Stretch: `common.stretch_tune` for keyboard-wide stretch (piano-style); per-partial stretch via `tone.fine_tune` on each layer.
- Hi-hat choke: put open and closed hats in one patch with `common.mono_poly` MONO, so a new hit cuts the previous one (a choke-like effect) [I].
- Keep bells in a reverb: `reverb.type` SRV HALL or REVERB, long.
