# SS49 Practical Bowed-string Synthesis (May 2003): digest

Source: Synth Secrets part 49, https://www.soundonsound.com/techniques/practical-bowed-string-synthesis. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- **Violin model:** sawtooth → LPF (gentle high roll-off) → HPF (steep bass cut) → a resonant formant bank of three band-passes:
  - **≈ 300 Hz** (moderate resonance)
  - **≈ 700 Hz** (moderate resonance)
  - **≈ 3 kHz** (broad, lower resonance, loudest)
  - Filter order doesn't matter much. At least three formants are needed.
- Tuning a filter by making it self-oscillate and matching a reference note: A = 110/220/440/880 Hz; E above each A = ×1.5 (330/660/1320/2640 Hz).
- **Korg 700 violin:**
  - saw at 4'; 12 dB LPF lowered a bit, 12 dB HPF raised (cut the lows)
  - amplitude: attack ≈ 5–6/10 (a **bowing attack**), full sustain ("singing")
  - A percussive envelope makes it a **banjo**.
- A single note may sound bowed, but phrases need **performance:**
  - **Vibrato:** finger vibrato is **5–8 Hz**, depth surprisingly large (**up to a quarter tone**), introduced **after** the bow stroke and varied musically. It also causes amplitude modulation (tremolo) through the body resonances.
  - **Pitch:** unfretted players land slightly sharp or flat and "hunt" for the pitch, and they glide.
  - Use the tiniest portamento: just off zero. More destroys the illusion.
- Result: a pleasing "violin-y" 1970s synth violin, best at higher pitches.

## AX-Synth translation (solo violin) [I]
- Tone: 185/177 saw with `tone.coarse_tune` +12 (4' register), or 301/303 string PCM.
- Filter: `tone.filter_type` LPF, `tone.cutoff` ≈ 85–100; the bass cut and formants go in MFX 1 EQUALIZER (low cut; peaks ≈ 300 Hz and 700 Hz moderate Q; a broad boost ≈ 3 kHz).
  - Alternative: 3 tones with the same saw, each `tone.filter_type` BPF at fixed cutoffs (`tone.cutoff_kf` 0) ≈ 300 Hz / 700 Hz / 3 kHz with moderate resonance, levels like the article (the 3 kHz one loudest).
- TVA: T1 ≈ 20–35 (bow attack), L1–L3 127, T4 ≈ 20–30.
- Vibrato:
  - LFO1 TRI/SIN, `tone.lfo_rate` ≈ 5–8 Hz feel
  - `tone.lfo_depth_pitch` moderate (a quarter tone max; lower for sections)
  - `tone.lfo_fade_mode` ON-IN, `tone.lfo_delay` ≈ 30–50, `tone.lfo_fade_time` ≈ 30–60
  - add a matching small `tone.lfo_depth_tva` (vibrato-induced tremolo)
  - `tone.lfo_rate_detune` small (irregularity)
- Pitch hunting: `tone.random_pitch` 5–10 cents; the pitch envelope starting slightly off (L0 ±2 → 0, short T1).
- Glide: `common.portamento_sw` ON, `common.portamento_time` very small (≈ 5–15), `common.portamento_mode` LEGATO; `common.mono_poly` MONO for a solo line.
- Expression: Matrix AFTERTOUCH or CC01 → LFO1 PCH DEPTH (the player controls the vibrato amount).
