# SS31 Synthesizing Percussion (Nov 2001): digest

Source: Synth Secrets part 31, https://www.soundonsound.com/techniques/synthesizing-percussion. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Percussion families:
  - membranophones (drums): pitched (timpani, tabla) or unpitched (kick, snare, toms)
  - idiophones: glockenspiel, xylophone, bells, gongs (pitched); cymbals, hi-hats (unpitched); shaken, scraped, struck
  - aerophones (whistles)
  - chordophones (piano)
- Ideal membrane mode ratios (0,1 = 1.00): 1,1 = 1.59; 2,1 = 2.14; 0,2 = 2.30; 3,1 = 2.65; 1,2 = 2.92; 4,1 = 3.16; 2,2 = 3.50; 0,3 = 3.60 … Inharmonic.
- **Timpani:**
  - Air loading and the kettle pull the radial modes almost into a harmonic series: principal (1,1) = 1.00, then ≈1.50 (a fifth), ≈1.98 (an octave), ≈2.44.
  - The **principal isn't the fundamental** (which lies at ~63 % of the principal).
  - Struck ~¼ of the way in from the edge = musical; struck at the centre = a dull, toneless thump.
- Time structure: a **short burst of enharmonic, noise-like partials** (circular modes decay fast), then a **longer quasi-harmonic tone** (radial modes). Near the end the principal can vanish, so the perceived pitch may jump up a fifth or an octave.
- Small hand drums (tabla) have more inharmonic modes. The loaded heads (gum/rice paste) are stiffened to make the modes more harmonic.
- Some drums rise in pitch when hit harder (timpani barely). Timpani and tabla can be pitch-bent over a small range (pedal/hand pressure, ≈ half an octave on timpani).

## AX-Synth translation [I]
- Timpani layer recipe (4 tones):
  - Tone 1 (principal): sine/triangle (220 "Sine", 214 "Syn Triangle"), long decay (TVA T1 0, L1 127, T3 long, L3 0), `tone.env_mode` NO-SUS.
  - Tone 2: same wave at `tone.coarse_tune` +7 (fifth, ≈1.50), slightly lower level, decay a bit longer (so the pitch "rises" at the tail).
  - Tone 3: +12 (octave, ≈1.98) quieter.
  - Tone 4: noise (232/233) through BPF/LPF, very short decay = the enharmonic strike burst. Or FXM/ring mod for clangy partials.
- Pitch control: `common.bend_up`/`common.bend_down` ≈ 5–7 semitones (pedal-timpani range) on the ribbon.
- Hit-harder-higher (other drums): `tone.penv_vel_sens` + with a short downward pitch envelope.
- PCM shortcuts: 142 "JD Log Drum", 140/141 "JD Gamelan", 147 "Steel Drums" (pitched percussion).
