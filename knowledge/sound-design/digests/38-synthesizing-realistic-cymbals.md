# SS38 Synthesizing Realistic Cymbals (Jun 2002): digest

Source: Synth Secrets part 38, https://www.soundonsound.com/techniques/synthesizing-realistic-cymbals. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- A cymbal's spectrum is a dense, fairly **flat fog of enharmonic partials** reaching beyond 20 kHz (up to 40 % of the energy may be supersonic). A synth with a filter ceiling around 12 kHz can't make convincing cymbals, so full bandwidth matters.
- Source: heavy FM of an unfiltered square carrier (~2.5 kHz) by a pulse modulator (~1 kHz), at maximum depth. The ratio is chosen so the partials don't clump and spread up to ~18.5 kHz. This beat noise-based cymbals to Reid's ears.
- **Two paths (ride cymbal):**
  1. **Ping:** 24 dB BPF whose centre sweeps **down to ~1 kHz over ~0.2 s**, with the same fast attack-decay envelope on its amplitude (to silence in ~0.2 s).
  2. **Tail:** 12 dB **HPF** at ~2.6 kHz, opened to maximum over ~200 ms (energy moving upward), then closing slowly (~3.7 s). Mixed **louder** than the ping.
  - Final AD envelope on the sum: instant attack, **decay ≈ 0.75 s** (ride).
- The long filter tail behind a shorter final envelope gives natural variation on retriggers: longer gaps let the band drop lower.
- Shorter decays = closed hi-hat; longer = open hat/other cymbals. Result: "cymbal-ness" like a good analogue drum machine, not a real cymbal.
- Test groove: a jazz ride pattern "tsssh t-t tsssh".

## AX-Synth translation (ride/hat) [I]
- Source: FXM at high depth on a bright pulse/square wave played high (`tone.fxm_sw`, `tone.fxm_depth` 12–16, `tone.fxm_color` 1–2), or ring mod of two square tones a non-integer interval apart (Structure TYPE 05/06), or noise 232 as a fallback.
- Tone 1 (ping): `tone.filter_type` BPF, TVF env from a higher L0 down to mid over T1/T2 ≈ 0.2 s, TVA fast decay (T3 ≈ 15–25), L3 0.
- Tone 2 (tail): `tone.filter_type` HPF, `tone.cutoff` mid-high, TVF env rising over ~0.2 s then slowly falling (`tone.fenv_levels` L1 high, T3 long), TVA decay ≈ 40–60 (ride) with `tone.env_mode` NO-SUS, `tone.level` > tone 1.
- Hi-hat closed/open: TVA T3 short (≈ 5–15) vs long (≈ 50–70). Open/closed on the same key via velocity layers or key ranges (`tmt.key_lower`/`tmt.key_upper`).
- Keep the cutoff high (`tone.cutoff` near 127 on the tail) for full bandwidth.
- PCM alternatives: 242 "JD Rattles", 239–241 "Metal Vox", 223 "JD MetalWind".
