# SS54 Practical Flute Synthesis (Oct 2003): digest

Source: Synth Secrets part 54, https://www.soundonsound.com/techniques/practical-flute-synthesis. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- The modern flute is cylindrical, keyed, and nearly chromatic, so it's more keyboard-friendly than the recorder.
  - Larger holes give a brighter tone; small-holed wooden folk flutes are mellow, recorder-like.
  - Overblowing jumps an octave.
- **Spectrum:** the flute can't support partials above ≈ **2 kHz** (a hard ceiling for every note).
  - Low notes: strong 2nd–4th harmonics, then ~1/n up to 2 kHz, with a comparatively weaker fundamental.
  - An octave up: the fundamental and 2nd are suppressed, then 1/n.
  - Higher: just a few 1/n harmonics under 2 kHz.
  - Synthesis: **sawtooth → HPF at a few hundred Hz → LPF at ≈ 2 kHz** with only a few % key tracking.
- **Blowing pressure:** soft notes keep the same fundamental and low-harmonic level but lose upper harmonics. **Pressure → LPF cutoff** (aftertouch on the Pro Soloist: press harder = brighter). **A flute doesn't get significantly louder or softer with blowing; it gets brighter or duller.**
- Loudness contour: a non-instant but not-slow attack, no decay, full sustain, a quick release. The release must be **long enough to avoid the "sucking" re-attack between legato notes**, but not sluggish.
- **Flute vibrato is brightness modulation** (blowing pressure ±10 % at **5–6 Hz**) → LFO to the **filter cutoff**, not pitch (vibrato) or amplitude (tremolo). Ideally delayed until after the chiff. Pressure can also scale the modulation depth.
- Reid thinks adding white noise to a basic flute patch **detracts** from it (unlike pan pipes).
- Moderate resonance at the LPF adds an edge without sounding electronic.
- **Reverb is critical:** the flute radiates from several holes with complex phase, and a reverberant space smooths this.
- The same contour on the LPF as on the VCA is fine (brightness tracks articulation).

## AX-Synth translation (orchestral flute) [I]
- Quick: PCM 99 "Flute", 102 "JD Fl Push".
- Synth flute: 185/177 saw
  - `tone.filter_type` LPF, `tone.cutoff` ≈ 2 kHz region (≈ 60–75 [I: calibrate by ear]), `tone.cutoff_kf` small (+5…+15), `tone.resonance` ≈ 15–30
  - HPF: MFX 1 EQUALIZER low cut (a few hundred Hz), or a 2nd identical tone with HPF mixed (the AX-Synth has one filter per tone; Structure TYPE 02 stacks two tones' filters, so tone 1 HPF + tone 2 LPF = band-pass [I])
- TVA: T1 ≈ 10–20, L1–L3 127, T4 ≈ 10–20 (enough to avoid the "suck" in legato).
- Brightness vibrato:
  - LFO1 SIN/TRI, rate ≈ 5–6 Hz feel, `tone.lfo_depth_tvf` small–moderate, `tone.lfo_depth_pitch` 0, `tone.lfo_depth_tva` 0
  - `tone.lfo_fade_mode` ON-IN with a short `tone.lfo_delay` (after the chiff)
- Blowing pressure: Matrix `matrix.source` AFTERTOUCH (the aftertouch knob) or CC01 → `matrix.destination` CUTOFF (+) and LFO1 TVF DEPTH (+). Not LEVEL.
- Velocity: `tone.cutoff_vel_sens` + rather than a big `tone.tva_vel_sens`.
- Mono legato: `common.mono_poly` MONO, `common.legato_sw` ON, `common.legato_retrigger` OFF.
- Reverb: SRV HALL, generous `reverb.level`.
