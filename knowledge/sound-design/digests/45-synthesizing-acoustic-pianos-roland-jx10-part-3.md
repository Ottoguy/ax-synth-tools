# SS45 Synthesizing Acoustic Pianos On The Roland JX10 [Part 3] (Jan 2003): digest

Source: Synth Secrets part 45, https://www.soundonsound.com/techniques/synthesizing-acoustic-pianos-roland-jx10-part-3. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Oscillator coupling options: hard sync; FM ("XMOD"); sync + FM (SNC2 = sync-dominated but richer mids and highs).
  - In sync, the **slave's** waveform shapes the tone; the master's wave matters only if FM is also applied.
  - The slave:master interval hugely changes the timbre (+14 vs +33 semitones).
- A static sync/FM interval (no sweep) gives no attack "clunk": the attack is less defined. A **swept** sync at the attack gives a definite thunk.
- **Layering secret:** layer two **similar-but-not-identical** patches at equal level with a **small detune**. The result is richer, more vibrant, more expressive and more "real" than either alone.
  - Layer B supplies the attack thunk; layer A supplies the richer body spectrum.
  - Detuned complex waveforms drift in and out of phase, imitating the energy exchange inside a piano.
  - Layer B's longer decay/release lets it dominate the tail while the filter closes to the fundamental.
  - Contrast: layering two *different* sounds (piccolo + bass) just sounds like two instruments; layering two *identical* sounds just sounds chorused.
- **Piano performance rules:** aftertouch → nothing (a piano note can't be changed after it's struck); no LFO modulation; hold pedal ON; poly mode, no portamento; pitch bend 0 (Reid: a 2-semitone bend on a piano is "wrong").
- Result: an expressive, usable "analogue piano", as usable as a Rhodes/Wurlitzer, with its own character.

## AX-Synth translation [I]
- A 4-tone layer = the JX10 Dual mode doubled. For piano/EP:
  - tone 1 = the attack-heavy layer (brighter, shorter TVA decay, e.g. 16 "Hard E.Pno", or the AX Grand ff layer)
  - tone 2 = the body layer (a richer wave, longer decay)
  - `tone.fine_tune` offset between them ≈ 3–8 cents
  - equal `tone.level`
  - tone 2's TVA T3/T4 longer so it dominates the tail
  - Structure TYPE 01 (independent)
- Piano performance settings:
  - `common.bend_up`/`common.bend_down` 0 (or leave the ribbon unused)
  - no matrix routing from AFTERTOUCH/CC01
  - `tone.lfo_depth_pitch`/`tone.lfo_depth_tvf`/`tone.lfo_depth_tva` 0
  - `tone.rcv_hold` ON
  - `common.mono_poly` POLY, `common.portamento_sw` OFF
- General rule for rich sounds: combine two related waves (e.g. two saw variants 177 + 185, or two EPs) with slight detune and different envelopes. That beats one wave + chorus.
