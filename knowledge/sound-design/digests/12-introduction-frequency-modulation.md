# SS12 An Introduction To Frequency Modulation (Apr 2000): digest

Source: Synth Secrets part 12, https://www.soundonsound.com/techniques/introduction-frequency-modulation. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- FM = vibrato pushed to audio rate. When the modulator frequency approaches or exceeds the carrier, vibrato disappears and a new complex tone appears.
- Sidebands at carrier ± n × modulator.
  - Modulator frequency (ratio) decides **where** the partials lie: harmonic for simple integer ratios, clangorous for odd ones.
  - **Modulation index β** (∝ modulator amplitude / modulator frequency) decides **how many and how strong**: low β ≈ AM-like with few sidebands, mellow; high β (~5) is broad, bright and complex, and the carrier itself can vanish.
- Bandwidth ≈ 2 × fm × (1 + β): index works like a brightness control.
- In FM, timbre changes come from envelopes on **modulator level**, not from a filter.
  - Modulator level rising while amplitude falls = a sound that gets brighter as it decays (unnatural, but characteristic).
  - Natural sounds are brighter when louder, so couple the index to the amplitude envelope or velocity for acoustic realism.
- To keep a constant timbre across the keyboard, both carrier and modulator must track, with the modulator amplitude scaling with pitch.
- FM gives tones unobtainable subtractively (complex spectral motion).

## AX-Synth translation
- The AX-Synth has **FXM** (frequency cross modulation) per tone:
  - `tone.fxm_sw` turns it on
  - `tone.fxm_depth` 0–16 ≈ modulation index, i.e. brightness/complexity
  - `tone.fxm_color` 1–4: lower = more metallic, higher = grainier
- FXM is less controllable than DX-style FM: no free carrier:modulator ratio. Use it for bells, digital/metallic textures, grit.
- Time-varying "index" **is possible**: `matrix.destination` includes FXM DEPTH, and `matrix.source` includes TVF ENV, TVA ENV, VELOCITY, KEYFOLLOW, LFO1/2 and CC01 [D EM p.42]. So:
  - TVF ENV → FXM DEPTH = FM-style brightness envelope (a DX bell/EP "ping" that mellows)
  - VELOCITY → FXM DEPTH = brighter when played harder (natural)
  - KEYFOLLOW → FXM DEPTH (negative sens) = the constant-timbre compensation described above
- Alternative: crossfade a bright FXM tone against a clean tone, using two tones with different TVA envelopes.
- DX-style bell/EP timbres are available directly as PCM: 148 "D-50 Bell", 159 "Old DigiBell", 12–15 "80's EP" (DX-type electric pianos).
