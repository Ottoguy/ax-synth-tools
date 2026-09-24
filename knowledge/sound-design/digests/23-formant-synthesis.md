# SS23 Formant Synthesis (Mar 2001): digest

Source: Synth Secrets part 23, https://www.soundonsound.com/techniques/formant-synthesis. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Band-pass filters in series narrow the band. In parallel with different centre frequencies they create a multi-peak response (instrument body/cavity modes).
- **Formants are fixed in frequency, independent of the played pitch.** As the pitch changes, different harmonics get emphasised, which makes an instrument family recognisable across its range. Pitch-tracking synth filters behave differently: they keep the same harmonic emphasised.
- Graphic EQs are too broad for sharp modes. Use **parametric EQ** (frequency, gain, Q) for fixed instrument formants.
- Human voice = pitched source + noise + moving formants (the vocal tract). The first three formants identify a vowel. Adult male values (Hz, F1/F2/F3):

  | Vowel | F1 | F2 | F3 |
  |---|---|---|---|
  | "ee" (leap) | 270 | 2300 | 3000 |
  | "oo" (loop) | 300 | 870 | 2250 |
  | "i" (lip) | 400 | 2000 | 2550 |
  | "e" (let) | 530 | 1850 | 2500 |
  | "u" (lug) | 640 | 1200 | 2400 |
  | "a" (lap) | 660 | 1700 | 2400 |

  For "ee": F1 0 dB Q 5, F2 −15 dB Q 20, F3 −9 dB Q 50. Male formant bandwidth ≈ 100 Hz; women's are slightly wider and higher.
- Q = centre frequency / bandwidth: high Q = sharp, narrow; low Q = broad.
- Speech: F2 moves the most. Consonants are noise bursts shaped by amplitude contours.
- Six or more formants make a very lifelike voice. Static formants suit fixed-body instruments (guitar, strings); moving formants are needed for talking/"wow" sounds.
- A resonant LPF ≈ a broad formant at 0 Hz + a narrow peak at the cutoff. The peak's gain = resonance.
- Guitar strings: a brighter wave and longer decays sound "new strings"; filtered and shorter sounds "old, dull thunk".

## AX-Synth translation
- Vowel sources: the formant PCM waves 234 "Aah Formant", 235 "Eeh", 236 "Iih", 237 "Ooh", 238 "Uuh". Choir/vox waves: 131–137 (Female Ahs/Oos, Male Aahs, Jazz Doos, Gospel Hum, Soprano Vox), 128–130, 165.
- Vowel filtering on any sound: MFX 9 HUMANIZER (vowel formant filter; `knowledge.md` lists its vowel parameters). Morphing between vowels by a controller uses the MFX control route (`mfx.control_source` → `mfx.control_destination`).
- Fixed body formants: MFX 1 EQUALIZER (parametric mid bands with frequency, gain and Q). One MFX per patch, so it's patch-wide.
- Per-tone formant peaks: `tone.filter_type` BPF or PKG with fixed `tone.cutoff` and `tone.cutoff_kf` 0, so the peak doesn't follow pitch. Up to 4 tones = up to 4 peaks, each a tone with the same wave and a different BPF/PKG centre [I].
- "Wah/talking" movement: PKG/BPF with TVF envelope or LFO (`tone.fenv_depth`, `tone.lfo_depth_tvf`), or MFX 8 AUTO WAH.
