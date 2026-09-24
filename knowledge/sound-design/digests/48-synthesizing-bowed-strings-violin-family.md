# SS48 Synthesizing Bowed Strings: The Violin Family (Apr 2003): digest

Source: Synth Secrets part 48, https://www.soundonsound.com/techniques/synthesizing-bowed-strings-violin-family. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- **Stick-slip bowing:**
  - static friction drags the string, then it slips back (the Helmholtz motion)
  - the bow speed sets the **amplitude**, not the pitch
  - the bow position removes harmonics (1/n positions), but an arbitrary position excites all of them
  - rosin: static friction rises and dynamic friction falls with warmth, so the string sticks and releases cleanly
- The **force on the bridge is a sawtooth**, which is why violins, violas and cellos are synthesised from **saw waves** (and why multiple saws make ensembles).
- Faults and effects:
  - too little bow pressure gives "double-slip" = **surface sound** (sync-like timbre, same pitch)
  - multiple slips = harsh noises
  - bowing at an angle = squeals (longitudinal vibrations)
  - louder notes go **slightly flat**; pitch **jitter** as the corner of the wave passes the bow
- **Body:**
  - top/bottom plates, trapped air, sound post, bridge resonance: complex, but a similar shape within a family (all violins sound like violins)
  - response to a sine sweep: flat over a few hundred Hz, steep bass roll-off, ~9 dB/oct high roll-off
  - when bowed: **dominant resonances at a few hundred Hz** plus a broad **2–5 kHz** resonance region. Both are essential for realism.
- Direction matters (a cello radiates forward at 200 Hz, backward at 250 Hz, upward at 800 Hz), so mic placement changes the tone.
- **Wolf tones:** energy sloshing between string and body at a few Hz makes an unsteady flutter on certain notes (cellos especially).
- Synthesis priorities:
  1. the bowed "shape" (vs pluck: pizzicato violin ≈ banjo-like)
  2. the body spectrum (low-mid resonances + 2–5 kHz)
  3. performance: **glide and vibrato**

## AX-Synth translation [I]
- Source: saw (e.g. 177/185/174) or string PCM (301 "RSS Str L"/302 R, 303/304 "US Strings L/R" = ensembles).
- Body spectrum: MFX 1 EQUALIZER with a mid peak (few hundred Hz) and a broad presence boost (2–5 kHz), a low cut (steep bass roll-off). Or MFX 2 SPECTRUM.
- Brightness roll-off: LPF with a moderate cutoff (≈ 80–95), `tone.cutoff_kf` ≈ +50.
- Loud-goes-flat / jitter: `common.analog_feel` small; `tone.random_pitch` 1–3 cents; a tiny RND LFO on pitch.
- Surface sound (light bow): add a quiet layer of 219 "Sync Sweep" or a thin pulse (205 "JP8 Pls 15HD"), velocity-switched to low velocities [I].
- Pizzicato: the same saw with a short plucked TVA (T1 0, T3 short, L3 0) + a decaying TVF env, banjo-like.
- Performance: vibrato and glide (see SS49/SS50).
