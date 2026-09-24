# SS43 Synthesizing Acoustic Pianos On The Roland JX10 [Part 1] (Nov 2002): digest

Source: Synth Secrets part 43, https://www.soundonsound.com/techniques/synthesizing-acoustic-pianos-roland-jx10-1102. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- **Hard sync:** the slave oscillator's phase is reset every master cycle.
  - Rule 1: the output pitch = the **master** pitch.
  - Rule 2: if the slave is higher than the master, changing the slave pitch changes the **timbre** (not the pitch). Integer ratios give saw-like waves; in between, exotic bright waves.
  - **Sweeping the slave** (with an envelope, LFO, S&H …) gives the classic "tearing/zeeeoww" **sync lead** (Moog Prodigy, ARP Odyssey).
  - A slave tracking only via the master gives a different tone on every note; the slave tracking the keyboard too keeps the timbre consistent.
- Sync is also great for **hammered/plucked string attacks**: harpsichord, clavinet, piano.
- **JX10 "Piano 1-B" oscillators:**
  - DCO1 = 8' square (the sync master, also mixed at ~25 %)
  - DCO2 = sawtooth at +14 semitones +10 cents, **hard-synced** to DCO1, its pitch swept by Env1 at full depth
  - Env1: A 0, D ≈ 1, S ≈ 6, R ≈ 35, key-follow 1. A huge tonal blip at the attack (imitating the hammer's spectral chaos), a "wiry" sustained sync tone, and a gentler sync sweep on release.
  - Env2 (A 0, D 70, S 0, R 40, key-follow 2) scales DCO2's level, so the synced "wire" fades and the plain square becomes more prominent as the note decays.
  - Envelope key-follow: times halve or quarter from bottom to top (faster at higher pitches, like acoustic instruments).

## AX-Synth translation [I]
- The AX-Synth has **no oscillator sync**. Substitutes:
  - PCM 219 "Sync Sweep" (a sampled sync sweep; use its natural motion, plus TVF movement)
  - "sweeping timbre" via FXM with Matrix `matrix.source` TVF ENV (or PITCH ENV) → `matrix.destination` FXM DEPTH: a brightness/harmonic blip at the attack that settles
  - a fast pitch-envelope blip on a bright, high layer (`tone.penv_depth`, T1/T2 very short) combined with a short TVA: a hammer "twang" transient
- Hammered/plucked attack realism: prefer the AX-Synth PCM (AX Grand 254–257, harpsichord 25, clavs 19–24).
- Wiry clav/harpsichord character: 25 "Harpsichord", 19–24 Clav waves, `tone.filter_type` HPF or PKG for a thin wire tone; `tone.aenv_time_kf`/`tone.fenv_time_kf` positive (times shorten upward, like JX key-follow).
- "Plain tone gaining prominence as the note decays": two tones, a bright wiry one with a shorter decay (TVA T3 short) and a plain square/sine with a longer decay.
