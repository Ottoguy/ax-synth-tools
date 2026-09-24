# SS55 Synthesizing Tonewheel Organs: Part 1 (Nov 2003): digest

Source: Synth Secrets part 55, https://www.soundonsound.com/techniques/synthesizing-tonewheel-organs-part-1. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- The Hammond tonewheel organ is an electromechanical **additive synth**: near-sine tonewheels, nine drawbars, each at levels 0–8.
- Drawbars (pitch → harmonic number relative to 16'):

  | Drawbar | Name | Harmonic |
  |---|---|---|
  | 16' | Bass (sub-octave) | 1 |
  | 5⅓' | Quint | 3 |
  | 8' | Unison | 2 |
  | 4' | Octave | 4 |
  | 2⅔' | Nazard | 6 |
  | 2' | Block-flute | 8 |
  | 1⅗' | Tierce | 10 |
  | 1⅓' | Larigot | 12 |
  | 1' | Sifflute | 16 |

- Registrations are written as xx xxxx xxx:
  - **88 8000 000**: the punchy classic of Jimmy Smith, Keith Emerson and heavy rock
  - **88 8888 888**: very full and bright
  - **83 4211 100** ≈ a sawtooth-like 1/n series
  - **00 8030 200** ≈ a square-like (odd-harmonic) series
  - 80 0000 000: a plain sine (dull)
  - Only 16' + 8' is uninteresting; the 5⅓' gives depth.
- **Key-click/"spit"** at note-on: a short transient (once considered a defect, now essential).
- The amplitude envelope is rectangular (gate on/off).
- Juno-6 trick for 88 8000 000: a square sub-oscillator + a 33 % pulse (removes every 3rd harmonic) through an LPF tuned 19 semitones above the sub, **self-oscillating** to supply the 5⅓' sine. A fast filter-envelope blip gives the click. The VCA is on the gate.
- Result: sounds like a 1970s transistor organ. **A real Hammond needs its treatments** (percussion, vibrato/chorus scanner, Leslie, overdrive, reverb) as well.

## AX-Synth translation [I]
- Quick, and best: organ PCM
  - 30 "JD Full Draw", 31/32 "Org Basic", 33 "Ballad Org", 34 "3rd Perc Org", 35 "Perc Organ", 36 "Rock Organ"
  - 258–281 and 309–313 VK/Full/Jazz/Vintage organs
  - 26–29 JLOrg Slow/Fast L/R, 37–41 rotary organs (Leslie baked in)
  - clicks: 249–253 "Org Click 1–5"
- Additive drawbar emulation with sine layers (8' = the played key; 4 tones max per patch [I]):
  - `tone.coarse_tune` offsets: 16' −12, 5⅓' +7, 8' 0, 4' +12, 2⅔' +19, 2' +24, 1⅗' +28 (−14 cents for a just 5th harmonic), 1⅓' +31, 1' +36
  - drawbar level ≈ `tone.level` (8 → 127; each drawbar step ≈ 3 dB [I])
  - e.g. 88 8000 000 = tones at −12, +7, 0 with equal levels (+ a click tone)
- Organ envelope: TVA T1 0, L1–L3 127, T4 ≈ 0–3; `tone.fenv_depth` 0; `tone.tva_vel_curve` FIX (organs aren't velocity-sensitive).
- Key-click: a short tone with 249–253 "Org Click" at a low level, TVA T3 very short; or a TVF blip (`tone.fenv_depth` +, T2 very short) on a sine layer.
- Next parts: percussion, scanner vibrato/chorus, Leslie (MFX 21 ROTARY / 22 VK ROTARY), overdrive (MFX 35 OVERDRIVE).
