# SS62 More Creative Synthesis With Delays (Jun 2004): digest

Source: Synth Secrets part 62, https://www.soundonsound.com/techniques/more-creative-synthesis-delays. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- **Chorus without a chorus unit:** saw + PWM pulse (itself two virtual pitches) + detune + vibrato on the saw, with vibrato and PWM at **different rates**. So much activity that the ear can't count the pitches: the Jupiter 8/Prophet/OB-X ensemble patches.
- **Basic chorus** = the dry signal + a copy through a modulated delay (pitch wobbling above and below):
  - **delay ≈ 10–50 ms** (shorter = flanging, longer = audible echo)
  - modulation depth **minimal**
  - rate: **< 1 Hz = gentle chorus; ~5–7 Hz = typical "synth ensemble"**
  - mix 50/50
  - Two paths sound like just two players (not lush).
- **Lusher:**
  - three delay paths modulated by one LFO at **0°/120°/240°** phases (the classic '70s string-machine chorus)
  - better still: each path modulated by **two LFOs** summed, a slow (~0.5–0.7 Hz) + a fast (~6–7 Hz), non-integer related, so it doesn't repeat for a long time
  - more independent LFOs, LFO-on-LFO, and random modulation (imitating human pitch instability) give ever richer ensembles
- **Classic ensemble:** two LFOs (≈ 1 Hz + ≈ 6 Hz) → three phase-shifted modulations of three delays (e.g. Solina). The Roland VP330 uses two delays (thinner); the Korg Polysix three delays with independent LFOs (richer).
- **Stereo chorus is the classic synth effect:** send different delay-path mixes to L and R and **omit the dry signal** (it reduces width). The Roland CE-1 only caught on once people used its stereo output.
- Chorus artefacts: warble (poor modulation) and "swishing" noise when idle.
- A bland waveform + a good chorus/ensemble = a lush sound (string synths, and DX/digital synths once chorus was added back).

## AX-Synth translation [I]
- Chorus unit: `chorus.type` CHORUS, `chorus.level` (amount), per-tone `tone.chorus_send_mfx`/`tone.chorus_send_direct`, `chorus.output_select` (routing, e.g. to reverb). Chorus-type parameters (rate, depth, pre-delay, feedback, phase) are in `knowledge.md` (chorus.toml).
  - Gentle: slow rate, small depth. Ensemble: faster (≈ 5–7 Hz feel) + moderate depth.
- MFX ensemble types:
  - 23 CHORUS
  - 26 HEXA-CHORUS (six-phase: the multi-path lush ensemble)
  - 28 SPACE-D (Roland Dimension-style multi-phase, less warble)
  - 29 3D CHORUS
  - 32 2BAND CHORUS
  - 27 TREMOLO CHORUS
- Stereo width: keep the MFX wet high (a low dry share) for width.
- Chorus without effects: two tones saw + saw/pulse, detune (`tone.fine_tune`), tone 1 pitch LFO at one rate, tone 2 at a different rate (`tone.lfo_rate`), plus the SS47 PWM trick, `tone.lfo_rate_detune`, `common.analog_feel`. Then add CHORUS for even more.
- Chorus + delay: MFX 75 CHORUS→DELAY; chorus + flanger 77.
