# SS16 From Sample & Hold To Sample-rate Converters (1) (Aug 2000): digest

Source: Synth Secrets part 16, https://www.soundonsound.com/techniques/sample-hold-sample-rate-converters-1. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Sample & hold of noise, clocked, gives a stepped random voltage.
  - To pitch (subtle): delicate random pitch wavering, which humanises digital sounds and is vital for acoustic imitations whose pitch wavers. It's less obvious than cyclic LFO vibrato.
  - To pitch (strong): random-note bleeps (classic sci-fi/computer).
  - To filter cutoff: the timbre changes on every clock tick, the classic ELP "Karn Evil 9" burbling sound.
- Step sequencer = user-set voltage per step: repeating bass lines/melodies (the "I Feel Love" disco bass). A quantiser snaps to semitones; a scale quantiser on random S&H = a random arpeggiator.
- A quantised glide is a glissando (stepped) rather than a portamento.
- Slewing S&H output gives the "shark's tooth": smooth random wandering instead of steps.

## AX-Synth translation
- `tone.lfo_waveform`:
  - S&H: stepped random, once per LFO cycle
  - RND: random
  - CHS: chaos
  - VSIN: a sine whose amplitude varies randomly each cycle
- Subtle humanising wander: RND or VSIN at a low depth on `tone.lfo_depth_pitch`; or `common.analog_feel` (1/f fluctuation, Roland's built-in "analogue instability"); or `tone.random_pitch` (a random offset per key press, e.g. 2–10 cents for ensembles/strings).
- Burbling random filter: `tone.lfo_waveform` S&H → `tone.lfo_depth_tvf` with high `tone.resonance`, `tone.lfo_rate` ~4–10 Hz (or synced).
- Random bleeps: S&H → large `tone.lfo_depth_pitch`.
- Step patterns: STEP LFO (`tone.step_type`, `tone.steps` 1–16, `tone.lfo_waveform` STEP) on pitch = a 16-step sequence per note (step values are pitch offsets), on TVF = rhythmic filter patterns. Also MFX 6 STEP FILTER, 12 STEP PHASER, 16 STEP RING MODULATOR, 19 STEP PAN, 63 STEP PITCH SHIFTER.
- Portamento vs glissando: `common.portamento_sw` + `common.portamento_time`. The AX-Synth has no quantised glissando mode [D EM].
