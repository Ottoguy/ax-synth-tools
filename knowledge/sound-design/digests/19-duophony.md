# SS19 Duophony (Nov 2000): digest

Source: Synth Secrets part 19, https://www.soundonsound.com/techniques/duophony. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Duophony (two pitches from the lowest and highest held keys) on a single signal path (ARP Odyssey) has side effects:
  - a single note fattens as both oscillators merge
  - chords re-fire envelopes oddly
  - it does help fast playing by re-triggering even when fingers overlap
- Duo-**timbral** (two independent synths in one box, e.g. Korg 800DV) is far more useful. Two distinct sounds, key-assign modes (one note → lower only, two notes → both, etc.), and repeat/retrigger modes.
- Classic two-layer analogue drums:
  - upper = high-pass-filtered **noise burst** with fast decay (hi-hat, snare "rattle")
  - lower = **tonal** voice that decays more slowly with a **downward pitch sweep** (kick at low notes, toms in the middle)
  - both together = snare
- **Partials**: a noise "chiff" snippet followed quickly by a tonal sustaining voice changes the sound's nature mid-note, the principle behind Roland's D-50 (PCM attack + synthesised sustain).
- An interval memory (two-note memory) is a programmable detune: stacked fourths/fifths.

## AX-Synth translation
- The AX-Synth is 128-voice polyphonic with 4 tones per patch, so every tone is a "timbre" layer.
- Key split (upper/lower sounds): `tmt.key_lower`/`tmt.key_upper` (+ `tmt.key_fade_lower`/`tmt.key_fade_upper` for crossfades) per tone.
- Velocity-switched layers: `tmt.velo_lower`/`tmt.velo_upper`, `tmt.velocity_control`.
- Noise + tonal drum voice:
  - tone 1 = 232 "White Noise", `tone.filter_type` HPF, short TVA decay
  - tone 2 = 220 "Sine"/triangle, `tone.penv_depth` positive with the pitch env falling (L0 high → 0) over a short `tone.penv_times` T1/T2, a moderate TVA decay
  - `tone.pitch_kf` 100 (or lower for less spread)
- Partials, D-50 style: tone 1 = a short one-shot attack wave (e.g. 229 "Digi Breath", 138 "JD Klmba Atk", 247 "JD EP Atk") with a fast TVA decay; tone 2 = the sustaining body.
  - Tone Delay can **stagger** a layer: `tone.delay_mode` NORMAL + `tone.delay_time` makes tone 2 enter after tone 1.
- Stacked intervals (fourths/fifths/octaves): `tone.coarse_tune` +5/+7/+12 on a second tone.
