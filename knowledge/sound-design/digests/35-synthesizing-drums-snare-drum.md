# SS35 Synthesizing Drums: The Snare Drum (Mar 2002): digest

Source: Synth Secrets part 35, https://www.soundonsound.com/techniques/synthesizing-drums-snare-drum. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Without snares, a snare drum ≈ a shallow double-headed tom.
  - Modes: two quasi-harmonic series (spacing ≈ 111 Hz, offset differently) plus the two 0,1-mode frequencies (≈ **180 Hz and 330 Hz**).
  - The 0,1 modes decay **more than twice as fast** as the others, but provide the **depth and bottom** of the drum. Don't drop them.
- The snare wires rattle against the snare head: repeated collisions excite a band-limited, **noise-like** spectrum. Optimal adjustment = many head-on collisions = the characteristic **snap**, with energy radiated quickly.
- **Velocity is the key control:**
  - light hit: drum modes dominate (tonal, "tom-like")
  - harder hit: louder, **more high-frequency energy**, modes widen, and the sound becomes **noisier** (the snare dominates)
  - very hard hit: mostly wide noise
- Synthesis:
  - noise → VCA/EG (basic)
  - better: noise → **LPF with velocity-controlled cutoff** (brighter when harder) + a few **notch filters** for spectral holes
  - best: add the tonal drum-mode generator and **crossfade by velocity** (tonal ↔ noise)
- Snare tension: too tight = no rattle; too loose = flabby. Shell size/material and mounting also colour the sound.

## AX-Synth translation (snare) [I]
- Tone 1 (body/"tom" part):
  - 220 "Sine" or 214 triangle, tuned so the fundamental ≈ 180 Hz (≈ F#3); tone 2 an octave-ish above (≈ 330 Hz: `tone.coarse_tune` +10…+11)
  - fast decay (TVA T3 short), a short downward pitch envelope (`tone.penv_depth` small)
- Tone 3 (snares): 232 "White Noise"
  - `tone.filter_type` LPF with `tone.cutoff_vel_sens` + (harder = brighter) and `tone.cutoff` ≈ 70–100
  - TVA decay a bit longer than the body (≈ 20–40)
  - optional PKG/BPF instead for a "tuned" snare
- Velocity crossfade: `tmt.velocity_control` ON with velocity ranges and fades (`tmt.velo_fade_lower` on the noise tone, `tmt.velo_fade_upper` on the tonal tone), or simply `tone.tva_vel_sens` high on the noise tone and low on the body.
- Spectral holes: MFX 1 EQUALIZER notch-ish cuts (patch-wide) [I].
- Classic 808/909-style snare = tonal body + noise with a separate short envelope (see SS19, SS36).
- Room: a short reverb, SRV ROOM or MFX 65 GATED REVERB for an '80s gated snare.
