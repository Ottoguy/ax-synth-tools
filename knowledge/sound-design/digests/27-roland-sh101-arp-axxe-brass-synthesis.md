# SS27 Roland SH101 & ARP Axxe Brass Synthesis (Jul 2001): digest

Source: Synth Secrets part 27, https://www.soundonsound.com/techniques/roland-sh101-arp-axxe-brass-synthesis. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Brass principles carry across synths: **once you know what defines "brassiness", you can program it on any subtractive synth**.
- SH101 brass:
  - sawtooth only (pulse, sub-oscillator and noise at zero, or the sound stops being brassy); 4' range; no vibrato LFO
  - VCA on the gate (a square loudness contour)
  - the single ADSR on the filter only: cutoff near zero, envelope amount near max, a touch of resonance, key tracking a little under 100 %
  - ADSR ≈ A 20 %, D 50 %, S 50 %, R 20 %
  - A small release (not 0) avoids an audible click as the envelope snaps shut.
- **Valve (legato) note changes don't re-articulate**: use gate-only (no retrigger) for smooth valve-style transitions. Tongued notes = slightly staccato playing.
- Growl = the LFO at max rate (triangle) into the filter, faded out by hand as the note reaches sustain (≈ 60 % → 0).
- **Why a factory "Trumpet" failed:**
  - envelope attack/decay too short
  - too little envelope amount
  - initial cutoff too high (too many harmonics at the note start)
  - no modulation: a static, dull patch
- **Tuba body trick:** saw at 60 % + a square sub-oscillator one octave down at 100 %. The saw alone lacks body; the square alone is hollow; the mix is right. **Combining waveforms defines the timbre** as much as the filter and envelopes do.
- ARP Axxe:
  - VCA initial gain > 0 means the note never stops. Use the ADSR on the VCA for silence between notes.
  - Longer decay, lower sustain and less envelope-to-filter emphasise the initial **"parp"**.
  - With a 20 Hz LFO max there's no rasp, so use gentle ~5 Hz vibrato, ideally pressure-controlled (more natural than a fixed LFO amount).

## AX-Synth translation [I]
- Tuba/low-brass body: tone 1 saw (e.g. 177 "MG Saw HD"), tone 2 square (196 "Fat Square") at `tone.coarse_tune` −12, `tone.level` a bit higher than tone 1. Structure TYPE 01, both through similar LPF envelopes (or TYPE 02 for a combined filter).
- Smooth valve-legato: `common.mono_poly` MONO, `common.legato_sw` ON, `common.legato_retrigger` OFF. Tongued style: legato OFF (each note re-attacks).
- Avoid clicks: TVA T4 ≥ ~3–5 rather than 0; the same for very fast T1 on sine/sub-heavy sounds.
- "Parp" emphasis: TVF T2/T3 longer, L3 lower, `tone.fenv_depth` moderate.
- Pressure vibrato: Matrix `matrix.source` AFTERTOUCH → `matrix.destination` LFO1 PCH DEPTH (the aftertouch knob), LFO1 ≈ 5 Hz.
- Don't reach a brass patch that never stops: TVA sustain is released at note-off (T4). Only `tone.env_mode`/hold pedal keep notes on.
