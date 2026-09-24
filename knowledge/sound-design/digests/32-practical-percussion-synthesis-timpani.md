# SS32 Practical Percussion Synthesis: Timpani (Dec 2001): digest

Source: Synth Secrets part 32, https://www.soundonsound.com/techniques/practical-percussion-synthesis-timpani. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Timpani = additive tone + a short enharmonic burst.
  - **Pitched part:** four sine partials at **1.00 : 1.50 : 1.98 : 2.44** × the principal (a large kettle drum's principal is ≈ **150 Hz**, i.e. not very deep), amplitudes ≈ **5 : 4 : 3 : 1**.
  - Relative decay times ≈ **45 %, 73 %, 91 %, 84 %**: the principal decays fastest, so the sound thins upward.
  - Attack 0; decay = release (the decay completes whether or not the key is held).
- **Enharmonic strike:** densely clustered partials that die quickly.
  - Ring-modulating two sawtooths at unrelated pitches (e.g. 100 Hz × 87 Hz) gives thousands of clustered partials. High-pass it (the drum has only one partial below the principal), with a short decay. FM (DX7) is even better.
  - Or narrow-band **pink noise, high-passed and slightly distorted, through overlapping resonant filters** (Korg's MS20 timpani): "extraordinarily life-like", with the oscillators supplying the shell ring.
- Velocity controls loudness only (timpani timbre barely changes with force).
- Play pitch with a bend/pedal (±a fifth), not chromatic keys.
- Filtering a triangle with HP + LP (resonant) removes the fundamental and leaves partials spaced like 1 : 1.5 : 2 : 2.5.
- An envelope to the LPF (brighter at the start, darker as it decays) mimics the higher partials dying faster.
- The initial enharmonic transient is where realism lives: Yamaha's own DX7 timpani (algorithm 16) beat the "correct" additive version because of its more realistic attack.

## AX-Synth translation (timpani, 4 tones) [I]
- Tones 1–3: 220 "Sine", with all detuning computed as 1200·log₂(ratio):
  - Tone 1: 0 st
  - Tone 2: `tone.coarse_tune` +7, `tone.fine_tune` +2 (ratio 1.50)
  - Tone 3: +12, −17 cents (1.98)
  - Tone 4 (optional, instead of noise): +15, +44 cents (2.44)
- Levels ≈ 5:4:3:1 via `tone.level` (e.g. 127/102/76/25).
- TVA per tone: T1 0, L1 127, L2/L3 0, T3 decays ≈ 45/73/91/84 % of the longest; `tone.env_mode` NO-SUS; T4 ≈ T3 (release = decay).
- Strike burst: a tone with 233 "Pink Noise" (or 232), `tone.filter_type` BPF, `tone.resonance` moderate–high, `tone.cutoff` ≈ mid, very short TVA decay; plus MFX 35 OVERDRIVE lightly for roughness (patch-wide) [I]. Alternative: ring mod (Structure TYPE 05–10) of two saw tones a non-integer interval apart, then HPF.
- Velocity → level only: `tone.tva_vel_sens` +, cutoff velocity sens ≈ 0.
- Pitch span: `common.bend_up`/`common.bend_down` 7 (±a fifth), played from one or two keys.
- Needs 4+ tones, so use Structure TYPE 01 for both pairs, and keep the chorus off (`chorus.level` 0) for a clean orchestral sound; reverb SRV HALL.
