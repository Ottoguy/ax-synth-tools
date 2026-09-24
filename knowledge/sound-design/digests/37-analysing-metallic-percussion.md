# SS37 Analysing Metallic Percussion (May 2002): digest

Source: Synth Secrets part 37, https://www.soundonsound.com/techniques/analysing-metallic-percussion. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Cymbals, hi-hats, tam-tams, gongs = thin metal plates fixed at the centre, free at the rim, with rigid-body vibrations.
  - Many inharmonic modes at discrete frequencies (hundreds of them). A dome raises the mode frequencies vs a flat plate.
  - Sound depends on alloy, size, thickness, shape (dome vs turned-up gong rim) and how and where it's struck (stick vs soft mallet, edge vs near the dome, crashed pairs, bowed).
- **Time evolution of a struck cymbal:**
  1. a few ms of complex impact waves
  2. energy into strong modal peaks at a **few hundred Hz**
  3. over the next few hundred ms the energy **moves up** to a **few kHz** (the ringing shimmer)
  4. the high modes die first, so the tail returns to the **mid frequencies**
- Light hit: clearly metallic, ringing modes. Hard hit: modes split, sub-harmonics appear, and vibration becomes **chaotic**, so the spectrum is essentially **noise**. Hence early drum machines' white-noise cymbals weren't completely wrong.
- Kraftwerk-style "weedy" synthetic cymbals show how hard realism is.

## AX-Synth translation [I]
- Realistic metal needs moving, dense inharmonic partials. Options:
  - ring mod between two tones at non-integer intervals (Structure TYPE 05–10, e.g. tone 2 `tone.coarse_tune` +6…+11 with an odd `tone.fine_tune`)
  - FXM with a low colour (`tone.fxm_color` 1–2 = metallic) and high depth
  - noise (232) through HPF/BPF for loud crashes
  - PCM 239–241 "Metal Vox", 242 "JD Rattles", 223 "JD MetalWind", 149–151 agogo, 153 "JD Cowbell"
- The upward-then-downward spectral motion (≈ hundreds of Hz → kHz → mids): TVF envelope on a BPF/PKG with L0 mid, L1 high (T1 ≈ a few hundred ms), then decaying back down (T2/T3), `tone.fenv_depth` + [I].
- Loud vs soft: velocity mixes noise vs ringing partials (`tmt.velo_lower`/`tmt.velo_upper` on a noise tone and a ring-mod tone, or `tone.tva_vel_sens` high on the noise tone).
