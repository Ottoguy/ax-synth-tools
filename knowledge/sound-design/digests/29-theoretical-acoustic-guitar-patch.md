# SS29 The Theoretical Acoustic Guitar Patch (Sep 2001): digest

Source: Synth Secrets part 29, https://www.soundonsound.com/techniques/theoretical-acoustic-guitar-patch. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Two acoustic truisms:
  - **higher pitch = brighter** (filter tracks the keyboard)
  - **louder (at any moment) = brighter** (one contour drives both cutoff and amplitude)
- Plucks use an "unconditional" AD envelope: the decay runs to completion even if the key is released.
- Voice assignment matters: notes on the same string cut off the previous one (re-initialising the brightness/loudness contours), while arpeggios across strings ring on. A keyboard doesn't know which string, so guitar realism needs a string-aware note allocation.
- Pick hardness ≈ a high-frequency shelf before everything else: a boosted top = hard plectrum; a cut top = soft fingers/thumb.
- Pick direction:
  - perpendicular: higher attack level, shorter decay
  - parallel: lower level, longer decay
  - Velocity can raise both attack level and decay time.
- A plucked string's wave tends toward a sine as it decays (only the fundamental is left): an LPF following the same AD as the VCA.
- Body resonances need many precise, high-Q parametric EQs. Graphic EQs and combs are useless.
- Each string (thick wound low E vs thin high E) has a different initial tone and decay.
- Performance realism:
  - per-string vibrato (pressure → depth, ideally rate too)
  - single-string bends (whole-patch bends sound horrible on chords)
  - string squeaks triggered only at top velocities (e.g. 124–127)
  - slides quantised to frets vs smooth bends
- Conclusion: only digital technology does a convincing acoustic guitar.

## AX-Synth translation [I]
- Start from guitar PCM (49–57), never from a saw, for realistic guitar.
- One contour for brightness + loudness: give the TVF envelope the same times as the TVA, `tone.fenv_depth` +, plus `tone.cutoff_kf` + (higher = brighter).
- Unconditional decay: TVA sustain L3 = 0 with `tone.env_mode` NO-SUS. T4 long enough not to chop the tail on quick release, or equal to T3.
- Velocity → level and decay:
  - `tone.tva_vel_sens` +
  - Matrix `matrix.source` VELOCITY → `matrix.destination` TVA ENV D-TIME (+) (harder = longer ring)
  - `tone.cutoff_vel_sens` + (harder = brighter)
- Hard/soft pick: MFX 1 EQUALIZER high shelf (patch-wide), or per-tone `tone.cutoff` offset.
- Squeaks/fret noise: a velocity layer at `tmt.velo_lower` 120+ with a noise-type wave (e.g. 248 "Key On Click", 139 "JD Wood Crak") [I, no dedicated squeak wave]. Release noise: `tone.delay_mode` KEY-OFF-NOR on a short noise tone.
- Single-string lines: `common.mono_poly` MONO (notes cut each other like one string); chords: POLY.
- Bend realism: whole-patch bend only (ribbon). Keep `common.bend_up` 2 (whole tone) for guitar-style bends.
- Vibrato by pressure: Matrix AFTERTOUCH → LFO1 PCH DEPTH (depth) and LFO1 RATE (rate) together.
