# SS10 Modulation (Feb 2000): digest

Source: Synth Secrets part 10, https://www.soundonsound.com/techniques/modulation. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Envelopes alone still give a static "beep". **Modulation** makes sounds live and breathe.
- Vibrato = periodic pitch change (LFO → oscillator pitch), with depth under player control (mod wheel), e.g. a string player rocking a finger.
- Tremolo = periodic loudness change (LFO → VCA). It's often confused with vibrato.
- LFO → filter cutoff gives three effects by rate:
  - ~0.1 Hz: slow sweep (ambient pads)
  - ~1–2 Hz: wah-wah
  - ~10–20 Hz: **growl** (great for brass)
- Better synths have separate LFOs per destination, with depths on mod wheel / aftertouch / pedal for expressive playing.
- Pulse duty cycle and timbre: a 1:n pulse = saw spectrum with every nth harmonic missing.
  - Square (50 %): odd harmonics only, **hollow** → clarinet, "woody"
  - 33 %: every 3rd harmonic missing
  - 25 %: every 4th missing
  - Narrow 5–10 %: **thin, nasal** → oboe
  - As the width approaches 50 % the sound thickens, then turns hollow exactly at 50 %.
- **PWM** (LFO sweeping the pulse width) gives the lush, moving, "chorused" analogue sound, ideal for string ensembles and rich leads. It's different from a chorus effect, because it modulates harmonic amplitudes at the source.
- Modulating at audio rates creates new timbres (AM/FM), not faster vibrato.

## AX-Synth translation
- Vibrato: `tone.lfo_depth_pitch` (LFO1 or LFO2) with `tone.lfo_waveform` TRI/SIN and `tone.lfo_rate` (~5–6 Hz feel). Player-controlled via Matrix Control: `matrix.source` CC01 (mod bar) → `matrix.destination` PCH (pitch) LFO depth, set in `matrix.sens`.
- Tremolo: `tone.lfo_depth_tva`, or MFX 17 TREMOLO / 27 TREMOLO CHORUS.
- Filter sweep / wah / growl: `tone.lfo_depth_tvf` with `tone.lfo_rate` slow / ~1–2 Hz / fast. Also MFX 8 AUTO WAH, or `tone.filter_type` PKG + LFO for wah.
- Pulse widths are fixed PCM waves:
  - 196/197/198 square (hollow, clarinet)
  - 207 30 %, 208 40 %, 209 45 % (fuller)
  - 206 25 %, 205 15 %, 204 10 % (thinner, nasal, oboe)
- **No PWM parameter on a single wave, but SS47 shows the PWM sound = two saws with one slightly pitch-modulated** (square/triangle LFO, tiny depth) plus slight detune, which the AX-Synth can do exactly with two tones (see digest 47). Other approximations [I]:
  - (a) Booster with Structure TYPE 03/04, where WG1 acts as an LFO shifting WG2, "similar to PWM" (`structure.booster`)
  - (b) two tones with detuned pulse/saw waves (`tone.fine_tune`, a few cents) = beating movement
  - (c) chorus (`chorus.type` CHORUS, MFX 23 CHORUS / 26 HEXA-CHORUS / 28 SPACE-D)
  - (d) PCM waves recorded with movement: 125/126 "OB2 Pad", 124 "Warm Pad", 121 "Unison Saw", 122 "Super Saw", 301–304 string ensembles
