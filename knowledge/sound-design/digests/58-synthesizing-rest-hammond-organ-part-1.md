# SS58 Synthesizing The Rest Of The Hammond Organ: Part 1 (Feb 2004): digest

Source: Synth Secrets part 58, https://www.soundonsound.com/techniques/synthesizing-rest-hammond-organ-part-1. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- **Leslie rotary speaker:**
  - crossover at **800 Hz**: a treble **horn** rotor (upward) and a bass **drum rotor** (downward)
  - two speeds each: slow "chorale" and fast "tremolo"; the horn and bass rotor spin at **different** speeds and **accelerate/decelerate at different rates** when switching
  - the result combines pitch, amplitude and tone modulation plus cabinet reverberation, with highs and lows swirling independently
  - near walls, the reflections make a mono source sound stereo
  - dual-rotor models sound better than single-rotor ones
- **Components of the effect:**
  - Doppler **vibrato:** a sine pitch modulation, peaking when the horn moves fastest toward you
  - **tremolo:** loudness peaks when the horn points at you, **90° out of phase** with the vibrato
  - **tone modulation:** brighter when pointing at you (in phase with the tremolo)
  - **reflections** from the cabinet walls/room: each delayed, duller, and phase-shifted in modulation. Interference with the direct sound creates moving **comb filtering**.
- A convincing analogue Leslie never existed. A proper model needs many delayed, filtered, modulated paths, and must process any input (a delay-line based pitch modulation, not oscillator vibrato).

## AX-Synth translation [I]
- Use the dedicated MFX: 21 ROTARY and 22 VK ROTARY. Their parameters (in `knowledge.md`) include slow/fast rotor speeds, separate woofer/tweeter speeds and acceleration, balance and drive (VK ROTARY), mirroring Reid's analysis.
  - Speed switching in performance: route a controller (e.g. the mod bar CC01, or a D-Beam CC) to the rotary speed via `mfx.control_source` → `mfx.control_destination` (the MFX control ports).
  - Keep the reverb modest after the rotary.
- Organ PCM with a Leslie already baked in: 26–29 "JLOrg Slow/Fast L/R" (stereo pairs), 37–41 "RtryOrg 1/2 L/R", 41 "LoFi RtryOrg". Crossfading slow/fast layers: TMT/matrix (`matrix.destination` TMT) or velocity.
- Manual approximation (not recommended when the MFX exists): an LFO on pitch (`tone.lfo_depth_pitch`) and amplitude (`tone.lfo_depth_tva`) with a phase offset between the two LFOs; LFO pan (`tone.lfo_depth_pan`) for the swirl; different rates for high and low tones.
- Rotary on other sounds (guitars, EPs, vocals): MFX 21/22 on any patch. The rotary MFX treats any input, not just organ.
