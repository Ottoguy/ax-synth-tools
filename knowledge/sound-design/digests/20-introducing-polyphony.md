# SS20 Introducing Polyphony (Dec 2000): digest

Source: Synth Secrets part 20, https://www.soundonsound.com/techniques/introducing-polyphony. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Many simple sounds reduce to three attributes: (1) the principal waveform (initial tone and pitch), (2) the brightness contour, (3) the loudness contour, plus modulation (vibrato/tremolo/growl).
- Percussive strings (piano, guitar) are loudest and brightest at the start, dying away over seconds, with brightness fading faster than loudness.
- True polyphony means **every note is articulated independently** (its own filter and amp envelopes). "Paraphonic" string machines/organs (one shared filter/envelope for all notes) make later notes of a chord enter at the sustain level with no attack: a smeared, organ/string-machine character.
- Organs have per-key on/off gating: a rectangular envelope, constant tone.
- String machines with per-note AR envelopes (Logan String Melody) sound more natural than paraphonic ones (Solina) when playing chords.

## AX-Synth translation
- The AX-Synth is fully polyphonic (128 voices) with per-note TVF/TVA envelopes, so every note is articulated individually.
- Paraphonic string-machine "smear" can't be reproduced exactly [I]. Approximate it with slow attack/release (`tone.aenv_times` T1/T4) and a chorus/ensemble effect.
- Organ-like: TVA T1 ≈ 0, L1–L3 = 127, T4 ≈ 0; no TVF movement (`tone.fenv_depth` 0).
- Voice budget: voices per note = tones used × waves (stereo waves count 2), 128 max (`architecture.polyphony`). Four stereo tones = 8 voices per note, so fast pads with long releases can steal notes; `common.priority` LAST/LOUDEST.
