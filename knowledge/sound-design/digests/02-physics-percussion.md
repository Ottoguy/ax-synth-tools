# SS02 The Physics Of Percussion (Jun 1999): digest

Source: Synth Secrets part 2, https://www.soundonsound.com/techniques/physics-percussion. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Three basic waves cover most acoustic instruments:
  - sawtooth → brass and bowed strings (also a lead guitar through effects)
  - square → "woody", hollow tones such as the clarinet
  - narrow pulse → thinner, reedier tones (oboe, bassoon)
  - saw + pulse together → convincing bass guitar
- Strings and pipes are 1-dimensional oscillators with harmonic overtones. Drums, cymbals, gongs and bells are 2-dimensional: their overtones are inharmonic (drum membrane modes at 1, 2.296, 3.6 × f …), unevenly clustered and ever denser upward. The result is atonal, with no clear pitch.
- Each mode has its own amplitude and its own decay rate. Striking harder raises a drum's pitch (the pitch depends on displacement).
- Imitation strategy:
  - drums: filtered **noise**, as in the CR-78/CR5000/TR-808 and parts of the TR-909
  - metallic percussion (cymbals, gongs, bells): a **ring modulator**, whose dense inharmonic clusters, with suitable filter and envelope, give metal sounds. Noise alone won't make a convincing bell.
- Toolkit for almost all acoustic sounds: harmonic oscillators + noise + ring modulator.

## AX-Synth translation
- Woody/hollow: square waves 194–202 (e.g. 196 "Fat Square"). Reedy/thin: narrow pulses 204 "JP8 Pls 10HD", 205 (15 %), 206 (25 %). Brass/strings: saws 174–193.
- Drums: noise waves 232 "White Noise", 233 "Pink Noise" through `tone.filter_type` BPF/HPF/LPF with short `tone.aenv_times`. The AX-Synth also has PCM percussion attacks (139 "JD Wood Crak", 142 "JD Log Drum", 153 "JD Cowbell") to use as they are.
- Metal: ring modulator via `tmt.structure_12`/`tmt.structure_34` TYPE 05–10 (`structure.ring_modulator`), or FXM (`tone.fxm_sw`, `tone.fxm_color` low = more metallic). Bell PCM waves also exist (148 "D-50 Bell", 154 "Tubular Bell", 155 "Church Bell", 157 "JD Crystal").
- Harder hits = higher pitch: positive `tone.penv_vel_sens` with a short downward pitch envelope (`tone.penv_depth`, `tone.penv_levels`).
