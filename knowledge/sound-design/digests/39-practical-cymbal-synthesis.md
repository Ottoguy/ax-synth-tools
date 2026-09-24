# SS39 Practical Cymbal Synthesis (Jul 2002): digest

Source: Synth Secrets part 39, https://www.soundonsound.com/techniques/practical-cymbal-synthesis. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- **TR-909 cymbal = a sample** (6-bit ROM) through a VCA whose decay tracks the sample's playback position (so retuning never truncates it) and an LPF against aliasing. The lesson: for cymbals, **samples win**.
- **TR-808 cymbal:**
  - **six square-wave oscillators tuned enharmonically**, mixed, lows removed: a mid/high partial cluster
  - split into bands: a low band (decay user-set); a high band split again into a short-decay "top" and a medium-decay "mid"
  - each band high-passed, then mixed (the tone control sets the band mix)
  - Unequal decays make the spectral balance change over time. It lacks the dynamic filter sweep of a real cymbal.
- Weak synths (one ring mod + noise) give an aggressive, non-cymbal "metal noise": usable punctuation, but not a cymbal.
- **The secret for affordable metallic percussion:** **several pairs of frequency/ring-modulated square-wave oscillators**, detuned against each other and mixed (Korg Rhythm 55 approach). "Stunning": big and small cymbals, Eastern cymbals, rides, crashes, hi-hats, tambourine jingles, depending on waveforms, pitches and filter/amp contours.

## AX-Synth translation (metal via two ring-mod pairs) [I]
- Set both `tmt.structure_12` and `tmt.structure_34` to a ring-mod type (TYPE 05/06/09/10). All four tones are square waves (196 "Fat Square", 197 "JP-8 Square", 198 "SH-2 Square"), with enharmonic coarse/fine tunings, e.g. tone 1 0, tone 2 +6 st +23 ct, tone 3 +11 st −17 ct, tone 4 +17 st +37 ct [I: any non-integer ratios work; tune by ear].
- Filtering: `tone.filter_type` HPF on all tones (remove lows), cutoff ≈ 60–90. Different TVA decays per pair: the high pair short (T3 ≈ 10–20), the lower pair medium (≈ 30–50), `tone.env_mode` NO-SUS.
- Variations:
  - closed hi-hat: all decays short (≈ 5–10)
  - open hat: ≈ 40–60
  - crash: longer + TVF upward sweep (SS38)
  - tambourine jingle: higher pitches + short decays
  - Eastern cymbal/gong: lower pitches, long decay, a slower TVF sweep
- `tone.pitch_kf` low (e.g. 0–20) so the metal barely changes with key; transpose by key for variety.
- FXM on square tones (`tone.fxm_sw`, low `tone.fxm_color`) adds more partials inside each pair.
- The AX-Synth has no cymbal samples (drum kits aren't in its wave list); the closest PCM are 242 "JD Rattles" and 239–241 "Metal Vox".
