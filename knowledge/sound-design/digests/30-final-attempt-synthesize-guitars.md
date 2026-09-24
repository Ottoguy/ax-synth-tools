# SS30 A Final Attempt To Synthesize Guitars (Oct 2001): digest

Source: Synth Secrets part 30, https://www.soundonsound.com/techniques/final-attempt-synthesize-guitars. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Electric guitar = strings + a solid body (few resonances) + **pickups** + amp/speaker.
  - A pickup "hears" only a short section of string. Harmonics with a node above it vanish, so the pickup acts as a **comb filter whose spacing depends on the note played**.
  - The electric spectrum is relatively **flat in the low harmonics** (unlike a 1/n saw).
  - The speaker/amp response is another major filter.
- Classic patch-book guitar tricks:
  - **ARP Axxe "Jazz Guitar":** a **25 % pulse** instead of a saw (the holes in its spectrum crudely imitate pickup/body notches); instant attack; D ≈ 6–7; the same contour on VCF and VCA; manual vibrato and bends.
  - **SH101 "Fuzz Guitar":** a pulse (~80 % width) with **pulse width following the envelope**, plus some saw to fill the notches, which adds movement. This mimics nodes sliding along the string as the amplitude decays.
  - **Minimoog "Electric Guitar" (Rhea):** pulse (70 %) + ramp (50 %) from **independent** oscillators, **sustain 0** on both envelopes, and a **filter decay faster than the amp decay** (highs die first) for a more natural tail.
- Reid: jazz-guitar sustain should be 0 (no indefinite sustain) unless imitating feedback sustain.
- None of these sounds truly like a guitar. Synth "guitars" only convince when **so heavily distorted** that the distortion dominates the timbre.
- Pitch drift: right after the pluck the high amplitude makes the string effectively shorter, so it's slightly sharp and inharmonic. As it decays the pitch drops slightly and the partials become more harmonic.

## AX-Synth translation [I]
- Realistic electric guitar = PCM + amp sim:
  - waves: 56 "Clean Gtr", 57 "Bright Strat", 58 "FstPick 70s", 59 "Funk Gtr", 60 "Funk Mute Gt", 61 "Overdrive Gt", 62 "DistortionGt"
  - MFX 39 GUITAR AMP SIMULATOR (amp + speaker type), 35/36 OVERDRIVE/DISTORTION, 37/38 VS versions, 66–71 OD/DIST → CHORUS/FLANGER/DELAY
  - This is the factory Lead Guitar family (SearingGtr 1 = Lead Guitar #1; `patches/guitar*.a8e`).
- Synth-guitar tricks:
  - 25 % pulse (206 "JP8 Pls 25HD") instead of a saw for jazz-guitar hollowness
  - mixed pulse + saw on two tones slightly detuned (independent layers)
  - TVA and TVF sustain 0, with the TVF decaying faster than the TVA (TVF T2/T3 < TVA T2/T3)
- Pluck pitch drift: pitch envelope L0 slightly positive (+2…+5) falling to 0 over T1/T2 ≈ 20–40 (`tone.penv_levels`, `tone.penv_times`) [I].
- Envelope-driven "pulse width" movement: no PWM. Use the booster trick (Structure TYPE 03/04) or a TVF envelope with PKG/BPF for a moving notch/peak.
- Feedback sustain for leads: TVA sustain high + distortion MFX. The forum patches use CC70 → matrix for "feedback" (see `research/third-party-patches-analysis.md`).
