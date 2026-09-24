# SS04 Of Filters & Phase Relationships (Aug 1999): digest

Source: Synth Secrets part 4, https://www.soundonsound.com/techniques/filters-phase-relationships. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Mixing two identical signals with a time offset creates a **comb filter**: some harmonics are cancelled, some reinforced, and the notch spacing is set by the delay. Two saws half a cycle apart give a saw one octave up, not silence. "Out-of-phase" complex signals rarely cancel completely.
- Every filter also **phase-shifts** harmonics (a simple RC low-pass: −45° at the cutoff, up to −90° far above). A filter distorts the waveform as well as attenuating it, which is part of why different filters "sound" different.
- Short delays mixed with the dry signal = comb filtering. This is the basis of flanging, phasing and chorus (later parts).

## AX-Synth translation
- Comb-filter/flanging colour: MFX FLANGER, PHASER, STEP FLANGER and CHORUS types, or the chorus unit (`chorus.type`). Short fixed comb effects: MFX delay types with a very short delay time and feedback.
- Two layers playing the same wave with a slight `tone.fine_tune` offset or `tone.delay_time` interact by phase: slow beating (detune) or static comb colouring (tiny delay).
- LPF2/LPF3 (`tone.filter_type`) are Roland's "different nuance" low-passes for acoustic instruments; the phase/character differences between filter types are audible.
