# SS36 Practical Snare Drum Synthesis (Apr 2002): digest

Source: Synth Secrets part 36, https://www.soundonsound.com/techniques/practical-snare-drum-synthesis. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- **TR-909 snare:**
  - two oscillators, waveshaped to ≈ sines, for the two 0,1 modes (≈ 180/330 Hz), **each with its own VCA and decay** (different amplitudes and decay rates), plus a pitch envelope
  - noise path: LPF'd noise split into (a) a high-passed narrow band with its own short envelope and (b) an unfiltered band with another envelope, so the highs and lows of the noise decay differently
- **TR-808 snare:** two self-decaying ("pinged") oscillators mixed at fixed levels + white noise through a VCA with a "snappy" envelope, **high-passed**, then mixed. It captures "snareyness" without realism.
- Early drum boxes: noise → static LPF/BPF → AR VCA. Better: an envelope also on the filter cutoff.
- **Simple synth snare (SH101):**
  - noise at full level only
  - LPF **fully open** (cutoff max + envelope + key tracking max), so it's brightest at the start and closes slightly
  - **no resonance** (it would make an "oowww" as it decays)
  - A = 0, S = 0, D = R ≈ 2/10 (short, identical whether held or released)
  - retrigger on every key (Gate + Trig) for rolls: trill two adjacent keys
- Slight noise overdrive into the filter = a harsher, punchier snare.
- Lower cutoff + full key tracking gives brighter high keys, darker low keys: variation like a drummer's inconsistent hits.
- EQ and reverb turn the same patch into a booming deep-shell, a bright military snare, or an '80s gated (Phil Collins) snare.
- A "shell" tone via FM: a fast LFO (audio-rate) modulating a 25 % pulse, played high, mixed ~35 % with the noise. Very sensitive settings.

## AX-Synth translation [I]
- Minimal snare:
  - 1 tone, 232 "White Noise"
  - `tone.filter_type` LPF, `tone.cutoff` 100–127, `tone.resonance` 0
  - `tone.fenv_depth` small +, TVF T3 short
  - TVA T1 0, T3 ≈ 15–30, L3 0, T4 = T3
  - `tone.cutoff_kf` + (pitch variation across keys)
- 808-style: + tone 2 = 220 sine at ≈ 180 Hz with a shorter decay, + tone 3 = sine at ≈ 330 Hz (+10 st) with an even shorter decay; noise tone `tone.filter_type` HPF (cutoff ≈ 40–60).
- 909-style noise split: two noise tones, one HPF (short decay, "snap"), one LPF (longer decay, "body").
- Rolls: POLY mode (each hit its own voice) and fast repeated notes. Keep `common.mono_poly` POLY.
- Gated '80s snare: MFX 65 GATED REVERB. Deep shell: MFX 4 LOW BOOST / 1 EQUALIZER. Military: brighter cutoff, shorter decay, SRV ROOM.
- FM shell tone: `tone.fxm_sw` ON on a pulse wave (206 "JP8 Pls 25HD") played high, level ≈ 35 % of the noise.
