# SS56 Synthesizing Tonewheel Organs: Part 2 (Dec 2003): digest

Source: Synth Secrets part 56, https://www.soundonsound.com/techniques/synthesizing-tonewheel-organs-part-2. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- The self-oscillating-filter trick works only for 88 8000 000.
  - Tuning the filter higher passes unwanted harmonics (5th, 7th …), which aren't in the Hammond series, so it's too bright.
  - Filter tracking also gets unstable at high harmonics.
- **Tonewheel spectra contain only harmonics 1, 2, 3, 4, 6, 8, 10, 12, 16 (re 16'); odd harmonics like 5, 7, 9 are absent.** Stray harmonics make it too bright, the wrong character.
- **Layering oscillators as drawbars (Prophet 10 Double mode):**
  - Four oscillators = four drawbars: triangle (≈ the tonewheel sine) at 16', a 33 % pulse at 8', and on the second layer 5⅓' and 4'
  - LPF low enough to remove the extra harmonics of the non-sine waves, **no resonance**
  - organ amp envelope (instant attack, full sustain, no release)
  - **all modulation off**
  - Any registration of ≤ 4 drawbars.
- **Tuning precision matters:** slightly mistuned voices or filters sound "just plain wrong" for organ (not "analogue warmth"). Stable, precise DCOs (Juno) beat the revered Prophet here.
- **Kawai K3 additive:** set the partial amplitudes directly (e.g. harmonics 1, 2, 3 at max = 88 8000 000). Filter a little to remove strays; key-click via a zero-time filter envelope at full amount; a square amplitude envelope; velocity and pressure OFF; key tracking ~100 %; no chorus. The best result.
- Still not a real Hammond without chorus/vibrato, percussion and overdrive (SS57).

## AX-Synth translation [I]
- Drawbar layering on the AX-Synth: up to 4 tones = 4 drawbars.
  - 220 "Sine" (the closest to a tonewheel) or 214 triangle through LPF to remove its extra harmonics
  - tunings per SS55 (−12/+7/0/+12/+19/+24/+28/+31/+36); `tone.level` = drawbar levels
  - `tone.fine_tune` 0 exactly (precision matters)
  - `tone.resonance` 0, `tone.fenv_depth` 0 (or a tiny click blip), `common.analog_feel` 0, LFO depths 0
  - `tone.tva_vel_curve` FIX; no aftertouch routing
- More than 4 drawbars: use an organ PCM that already contains the registration (30 "JD Full Draw", 258–281 VK/Full/Jazz organs) and add 1–3 sine tones for extra drawbars.
- Key-click: `tone.fenv_depth` +, TVF T1 0, T2 ≈ 1–3, L2/L3 = base (a fast blip), or the "Org Click" PCM tone.
