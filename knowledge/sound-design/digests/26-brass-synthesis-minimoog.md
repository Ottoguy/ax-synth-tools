# SS26 Brass Synthesis On A Minimoog (Jun 2001): digest

Source: Synth Secrets part 26, https://www.soundonsound.com/techniques/brass-synthesis-minimoog. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts (Reid's Minimoog trumpet)
- **One sawtooth oscillator** only. Detuned multiple oscillators are unrepresentative of a single real instrument (fine for "fatter tutti/section" sounds). Range 4' (an octave up) for trumpet/cornet/alto & soprano sax; lower for tuba, horn, trombone.
- Oscillator level at mid (5/10) to avoid overdriving the filter. Mild drive is nice for some sounds, but not clean brass.
- **Loudness:** attack ≈ **100 ms**, sustain **max**, release ≈ instant (brass stops quickly when blowing stops).
- **Filter:**
  - cutoff fully closed; envelope amount ≈ 65 %
  - filter envelope attack ≈ **600 ms**, decay ≈ **800 ms**, sustain ≈ **50 %**, instant release
  - resonance ≈ 20 % (a slight bump only)
  - keyboard tracking 100 % (ideal: a bit under 1:1)
  - The filter opens more slowly than the amp, so the higher harmonics enter one by one over ~0.5 s. This is the key brass cue.
- **Growl/rasp:** audio-rate triangle (Osc3, not tracking the keyboard) into the filter, faded in and out manually with the mod wheel at note starts. Tom Rhea's tuba instead roughens the filter with **noise** modulation (avoids FM sidebands, very effective).
- Vibrato done by hand on the pitch wheel can be more natural than an LFO. Trombone slides = larger pitch-wheel moves.
- **Brass fails if:** a non-saw waveform, **instant attacks**, or **high filter emphasis**.
  - More muted ↔ brassier: lower/raise the envelope amount and cutoff.
  - Lower brass (trombone, tuba) is more forgiving: the ear is less sensitive there.
- Tom Rhea's trumpet (3 unison oscillators, a more open filter, less envelope, 66 % tracking, no modulation) sounds more muted and static.
- Performance matters as much as the patch: phrase like a brass player.

## AX-Synth translation [I]
- TVA T1 ≈ 100 ms. The TVA time scale is 0–127, non-linear, and the ms mapping isn't documented: start around T1 ≈ 20–30 and adjust by ear. L1–L3 = 127, T4 ≈ 5–10.
- TVF:
  - LPF, `tone.cutoff` low (≈ 20–40)
  - `tone.fenv_depth` ≈ +40…+55
  - TVF env: T1 ≈ 6× the TVA attack (≈ 50–65), T2/T3 ≈ 60–70, L3 ≈ 64 (50 %), T4 short
  - `tone.resonance` ≈ 15–25
  - `tone.cutoff_kf` ≈ +80…+100
- Filter roughness without pitch FM: `tone.lfo_waveform` RND or S&H at a high rate → small `tone.lfo_depth_tvf`, faded out after the attack (`tone.lfo_fade_mode` ON-OUT). Or leave it to the mod bar: Matrix `matrix.source` CC01 → `matrix.destination` LFO1 TVF DEPTH.
- Octave: `tone.coarse_tune` +12 or `common.octave_shift` for trumpet register; 0/−12 for trombone/tuba.
- Manual vibrato ≈ the AX-Synth ribbon (pitch bend). Keep `common.bend_up`/`common.bend_down` small (1–2 semitones) for realistic brass bends; wider (up to 12) for trombone-like slides.
- Avoid for realistic brass: square/pulse waves, T1 = 0, `tone.resonance` > ~40.
