# SS21 From Polyphony To Digital Synths (Jan 2001): digest

Source: Synth Secrets part 21, https://www.soundonsound.com/techniques/polyphony-digital-synths. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Voice-allocating polysynths (Oberheim 4-Voice, Prophet 5): a limited number of complete voices assigned to keys. Too many notes means note-stealing (cycling) or delayed notes (first-note priority).
- **Unison**: all voices stacked on one note gives an overpowering, huge mono sound (the 4-Voice in unison was "one of the most overpowering monosynths of all time").
- Digital control has side effects: parameter quantisation causes "zipper noise" on knob moves, and envelope/LFO calculation rates are limited.
- **Organic warmth of vintage polysynths:** each voice differs slightly (detune, filter opening). Non-strict (random) voice rotation keeps a solo from sounding mechanically patterned. Modern "analogue feel" parameters imitate this with small random fluctuations.

## AX-Synth translation
- Unison-style fatness: layer 2–4 tones with the same wave, detuned by `tone.fine_tune` (e.g. −7/+7 cents, ±12–15 for wider) and spread with `tone.pan`. Or use PCM ensemble waves 121 "Unison Saw", 122 "Super Saw", 123 "Trance Saw". Mono unison lead: `common.mono_poly` MONO + detuned layers.
- Voice-to-voice variation ("organic"):
  - `common.analog_feel` (1/f fluctuation)
  - `tone.random_pitch` (small, 1–10 cents)
  - `tone.lfo_waveform` RND at a low depth on TVF
  - `tone.random_pan` / `tone.alt_pan` (stereo movement per note)
- Zipper noise: CC-driven real-time cutoff (CC74) moves in 7-bit steps. Keep sweeps envelope- or LFO-driven for smoothness [I].
