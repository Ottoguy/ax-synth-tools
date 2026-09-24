# SS44 Synthesizing Acoustic Pianos On The Roland JX10 [Part 2] (Dec 2002): digest

Source: Synth Secrets part 44, https://www.soundonsound.com/techniques/synthesizing-acoustic-piano-roland-jx10. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- The piano's magic is its **dynamic range**: caress some notes, pound others. Piano-like synthesis needs a velocity response, not just a timbre. Attention to dynamics "repays itself many times over" for strings, brass and percussion too.
- **Velocity curves:** a curve maps key velocity to an "amount" (level, cutoff, vibrato depth …). Different curves for different destinations let one velocity produce e.g. 55 % level, 47 % brightness and 17 % vibrato. JX10 curves:
  - 1: offset + exponential rise
  - 2: linear from zero
  - 3: near-zero then a steep rise
- **JX10 "Piano 1-B" filter & amp:**
  - HPF off
  - LPF cutoff ≈ mid (53/99, so it never closes fully), resonance 2/99 (a barely-there accent)
  - key follow **24 %** (higher notes somewhat brighter)
  - Env2 (piano-shaped: instant attack, long decay, S 0, medium release, key-follow) → cutoff at only ~14 %, velocity-scaled (curve 1)
  - VCA: Env2, velocity curve 2 (linear). Reid would prefer curve 3: real piano notes are never inaudibly quiet once the hammer reaches the string.
  - **No chorus** (it fattens inappropriately for an acoustic piano); **no LFO** anywhere
- Result: a fine **electro-mechanical piano** (RMI Electrapiano, Rhodes/Wurlitzer territory), not a grand. "It's not what you've got, it's what you can do with it."

## AX-Synth translation [I]
- Velocity curves: `tone.tva_vel_curve` (FIX, 1–7) and `tone.cutoff_vel_curve` (and `tone.fenv_vel_curve`) choose separate response curves per destination, with separate amounts: `tone.tva_vel_sens`, `tone.cutoff_vel_sens`, `tone.fenv_vel_sens`. The global keyboard feel is `system.keyboard_velocity`. The exact AX-Synth curve shapes aren't documented; try them by ear.
- EP-style synth piano: a bright, wiry source (a clav/EP PCM such as 16 "Hard E.Pno", 19 "ClavDB Brt", or a saw) → LPF cutoff ≈ mid (60–75), `tone.resonance` ≈ 0–5, `tone.cutoff_kf` ≈ +20…+30, `tone.fenv_depth` small + (≈ +8…+12) with `tone.fenv_vel_sens` +.
  - TVA piano shape: T1 0, L1 127, T3 long, L3 0, T4 medium, `tone.aenv_time_kf` +.
- For acoustic realism, keep the chorus off (`chorus.level` 0 / `tone.chorus_send_mfx` 0) and the LFO depths at 0.
- Minimum loudness at soft velocities: a moderate `tone.tva_vel_sens` (not maximum), so soft notes stay audible.
