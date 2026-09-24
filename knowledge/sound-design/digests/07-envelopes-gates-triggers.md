# SS07 Envelopes, Gates & Triggers (Nov 1999): digest

Source: Synth Secrets part 7, https://www.soundonsound.com/techniques/envelopes-gates-triggers. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- The "true" envelope of a parameter is the sum of every modulator acting on it (EG + LFO + velocity + …), not just the EG.
- AD (attack–decay) shapes are powerful. Two different ADs summed on one destination create 4-stage contours no ADSR can make.
- Trigger (note-on pulse) vs gate (held key). Re-triggering on every note (ARP Odyssey) keeps fast legato solos punchy, because each note gets its attack spike. Single-triggering (Minimoog) lets overlapped notes slur at the sustain level: less punch, but natural for flute-like or legato phrasing.
- A "reset-to-zero" envelope on every note sounds disjointed ("swallowing its tongue"), especially with slow attacks (string machines).
- Useful extras:
  - key-tracked envelope times (faster at high pitches, like pianos and guitars)
  - a short pitch transient: many instruments start slightly sharp
  - contours on LFO rate/depth: human-like vibrato/tremolo that isn't mechanically regular
- The first few milliseconds identify an instrument. Roland's LA synthesis used a short sampled attack + a synthesised sustain. A flute attack = filtered saw + a little noise with the right brightness/loudness contour.
- To program deterministically, analyse and recreate the **brightness contour** and the **loudness contour** of the target.

## AX-Synth translation
- Legato/trigger behaviour:
  - `common.mono_poly` MONO
  - `common.legato_sw` ON: overlapped notes don't re-attack (flute/brass/lead legato)
  - `common.legato_retrigger`: whether the envelope retriggers
  - For a punchy staccato-style mono lead, legato OFF.
- Key-tracked envelope times: `tone.aenv_time_kf`, `tone.fenv_time_kf`, `tone.penv_time_kf` (positive = shorter at high notes, like piano/guitar).
- Attack pitch transient: pitch envelope (`tone.penv_depth`, `tone.penv_levels` L0 slightly above 0 → back to 0 in a short `tone.penv_times` T1).
- Humanised modulation: `tone.lfo_fade_mode` ON-IN with `tone.lfo_delay` and `tone.lfo_fade_time` (delayed vibrato); `common.analog_feel` (1/f wander). LFO rate/depth can be driven through Matrix Control (`matrix.destination` LFO1/LFO2 RATE/PCH DEPTH …).
- The LA-style "attack sample + sustain" is native to the AX-Synth: layer a one-shot attack wave (e.g. 228 "Shaku Noise", 229 "Digi Breath", 248 "Key On Click", 246 "SynBassClick", 247 "JD EP Atk") on one tone with a sustaining wave on another (`wave.oneshot_loop`, `tmt.tone_switch`).
- Two summed contours on one parameter: use two tones with different envelopes on the same wave (Structure TYPE 01), or pitch/TVF/TVA envelopes plus LFO fades.
