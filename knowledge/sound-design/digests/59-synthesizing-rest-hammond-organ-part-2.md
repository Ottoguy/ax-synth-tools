# SS59 Synthesizing The Rest Of The Hammond Organ: Part 2 (Mar 2004): digest

Source: Synth Secrets part 59, https://www.soundonsound.com/techniques/synthesizing-rest-hammond-organ-part-2. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- A BBD (bucket-brigade) delay = a chain of S&H stages clocked at a rate; anti-alias + reconstruction low-pass filters. Modulating the clock modulates the pitch of **any** input (vibrato on any sound); modulating it at audio rate waveshapes (FM/phase-distortion-like, DX/CZ timbres).
- **Leslie numbers:**
  - Doppler pitch depth is small: about **±1 %**
  - rotation can be **slower than 1 Hz** on "chorale"
  - two speeds (chorale/tremolo) with **slewed transitions** (the acceleration/deceleration is audible and characteristic)
  - **split at 800 Hz** into horn and bass paths with independent speeds and ramp times
  - add amplitude and tone modulation **90° out of phase** with the pitch modulation
  - plus cabinet/room reflections (more delays)
- Analogue rotary simulations were never fully convincing (the Dynacord CLS222 was the best); digital models compute thousands of paths.
- The ideal chain: organ → **valve overdrive** → **rotary simulation** → **speaker/cabinet simulation** (a little "dull woodiness"). E.g. the Korg G4 after a Juno 60 or Kawai K3: "magic".
- BBD delays also underpin echo, flanging, chorus and ensemble (SS60–62).

## AX-Synth translation [I]
- Signal chain on the AX-Synth: the tones (organ PCM or sine drawbars) → **MFX 22 VK ROTARY** (includes overdrive/drive and a woofer/tweeter model per the Effects List) or **MFX 21 ROTARY** → chorus unit off → reverb low.
  - Drive before the rotary: VK ROTARY's drive, or MFX 66 OVERDRIVE→CHORUS is *not* a rotary; prefer VK ROTARY.
  - Speaker "dull woodiness": MFX 10 SPEAKER SIMULATOR exists but only one MFX runs per patch. With VK ROTARY chosen, use the per-tone LPF (`tone.cutoff` slightly lowered) for cabinet dulling.
- Slow↔fast switching with ramp: the VK ROTARY speed parameter via the MFX control (`mfx.control_source` CC01 mod bar, or the D-Beam CC, → speed), with the MFX's own rise/fall time parameters giving the acceleration/deceleration.
- Separate horn/rotor speeds and ramp times are parameters of the rotary MFX (see `knowledge.md` ROTARY / VK ROTARY entries).
- Delay-line pitch modulation of any sound = MFX 23 CHORUS / 24 FLANGER / 46 MODULATION DELAY (SS60–62).
