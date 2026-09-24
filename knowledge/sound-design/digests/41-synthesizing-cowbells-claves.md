# SS41 Synthesizing Cowbells & Claves (Sep 2002): digest

Source: Synth Secrets part 41, https://www.soundonsound.com/techniques/synthesizing-cowbells-claves. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Cowbells are small hammered-sheet "3-D plates", not tuned like church bells.
- **TR-808/CR-8000 cowbell:**
  - two tones at **≈ 587 Hz and 845 Hz (ratio 1 : 1.44)**, precisely tuned; small deviations ruin the illusion
  - **triangle** waves (pulse was too bright, "synthy"); a little more level on the higher tone for "clank"
  - **two-stage amplitude decay:** a loud, short impact, then a longer tail
  - **band-pass ≈ 2.64 kHz**, 12 dB/oct (24 dB too narrow) with slight resonance
  - a faint halo of **pink-ish noise**, mainly in the impact
- Single-oscillator version: one triangle at 587 Hz + the filter **self-oscillating at 845 Hz** with the VCA *before* the filter: more percussive and aggressive than the Roland.
- **Claves (TR-808):** a pinged decaying oscillator. Equivalent: triangle → band-pass with **no resonance** → a **very short decay** = a woody click.
- Analysis trick: replay a target sample 2–3 octaves lower to reveal fast/high components (e.g. a noise halo).

## AX-Synth translation [I]
- Cowbell (2 tones + optional noise):
  - Tone 1: 214 "Syn Triangle" (or 215/216), play D5 (≈ 587 Hz) or map with `tone.coarse_tune`
  - Tone 2: the same wave `tone.coarse_tune` +6, `tone.fine_tune` +31 (ratio 1.44), `tone.level` slightly higher than tone 1
  - Both: `tone.filter_type` BPF, `tone.cutoff` ≈ high-mid (2.6 kHz region), `tone.resonance` low–moderate
  - TVA: T1 0, L1 127, T2 very short, L2 ≈ 50–60, T3 medium, L3 0 (a two-stage decay), `tone.env_mode` NO-SUS
  - `tone.pitch_kf` low so it stays a "cowbell" across keys, or keep 100 and play one key.
  - Optional tone 3: 233 "Pink Noise", low level, very short decay.
- PCM shortcut: 153 "JD Cowbell", 149–151 agogo waves, 230 "Agogo Noise".
- Claves: 214 triangle, `tone.filter_type` BPF, `tone.resonance` 0, TVA T3 ≈ 3–8 (very short). Also 139 "JD Wood Crak", 142 "JD Log Drum" PCM.
