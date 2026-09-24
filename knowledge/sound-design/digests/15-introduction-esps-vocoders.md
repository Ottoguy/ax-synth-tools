# SS15 An Introduction To ESPs & Vocoders (Jul 2000): digest

Source: Synth Secrets part 15, https://www.soundonsound.com/techniques/introduction-esps-vocoders. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- External-signal processing: pitch-to-CV converters and envelope followers let an external instrument or voice play the synth. A vocoder = a filter bank + envelope followers: the modulator (voice) articulates the carrier (a synth).
  - Best carriers: saw (richest), rounded pulse (closest to vocal cords), noise (speech).
  - A noise band is needed for sibilants and consonants.
- **Slew generator / lag** = a 6 dB/oct low-pass on a control voltage. It rounds abrupt CV jumps. Its common use is **portamento/glide** between notes.
- Rhythmic gating: an envelope follower on a drum track triggers the VCA of a sustained chord, so the chord "plays" in rhythm.

## AX-Synth translation
- **Not applicable to the AX-Synth:** it has no external audio input, envelope follower or vocoder [D OM]. Don't promise vocoder sounds.
  - Closest substitutes: vocal/choir PCM (128 "SBF Vox", 129/130 "Syn Vox", 165 "Digital Vox", 234–238 formant waves), or MFX 9 HUMANIZER (vowel formant filter).
- Portamento = slew: `common.portamento_sw`, `common.portamento_time`, `common.portamento_mode` (normal / legato only), `common.portamento_type` (rate/time).
- Rhythmic gating of a sustained sound, without an envelope follower: MFX 20 SLICER, 17 TREMOLO (square), 19 STEP PAN; or a STEP LFO on TVA (`tone.step_type`, `tone.steps`, `tone.lfo_waveform` STEP → `tone.lfo_depth_tva`).
