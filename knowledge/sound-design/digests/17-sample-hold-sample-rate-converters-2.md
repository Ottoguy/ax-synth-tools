# SS17 From Sample & Hold To Sample-rate Converters (2) (Sep 2000): digest

Source: Synth Secrets part 17, https://www.soundonsound.com/techniques/sample-hold-sample-rate-converters-2. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- A step sequencer clocked at audio rate becomes a waveform generator (staircase saw, square, pulse, arbitrary shapes): the idea behind wavetable/PCM playback.
- Digital audio = S&H + quantisation.
  - Coarse amplitude resolution (fewer bits) adds quantisation noise and grit.
  - A low sample rate makes frequencies above Nyquist (half the sample rate) fold down as **aliasing**: inharmonic, metallic, "digital" artefacts that move the wrong way when the pitch changes.
  - Anti-alias and reconstruction low-pass filters prevent this. Properly done, digital audio isn't "steppy".
- Sound-design relevance: bit/sample-rate reduction is a deliberate **lo-fi** colour (crunchy, gritty, old sampler/game console).

## AX-Synth translation
- The AX-Synth is itself a PCM (sampled-wave) instrument, so its source waves are "stored sequences" in exactly this sense.
- Deliberate lo-fi/digital grit: MFX 56 LOFI NOISE, 57 LOFI COMPRESS, 58 LOFI RADIO, 59 TELEPHONE, 60 PHONOGRAPH (see their parameters in `knowledge.md` for sample-rate/bit reduction and noise).
- "Old digital" PCM character: 159 "Old DigiBell", 163 "JD Brt Digi", 222 "Digi Loop", 225 "DigiSpectrum".
- Mostly background theory. No direct parameter mapping beyond the lo-fi effects.
