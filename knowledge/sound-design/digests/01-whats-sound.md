# SS01 What's In A Sound? (May 1999): digest

Source: Synth Secrets part 1, https://www.soundonsound.com/techniques/whats-sound. Claims = [3P] Gordon Reid; "AX-Synth" lines = [I] our mapping.

## Setting → sound facts
- A pitched sound is a fundamental plus harmonics at integer multiples (f, 2f = octave, 3f = octave + fifth, 4f = 2 octaves, …). Integer-related harmonic series ⇒ clear pitch; intervals sound consonant when harmonics of the two notes coincide (1:2 octave, 2:3 fifth).
- Waveform and harmonic spectrum are two descriptions of the same thing: "sawtooth"/"square" are shorthand for particular harmonic recipes.
- Sawtooth: every harmonic present, amplitude of the nth = 1/n. The brightest, fullest basic wave.
- Subtractive synthesis = start from a harmonically rich wave and remove harmonics with a filter. Keeping only the first few harmonics of a saw produces a rounder, duller, different-sounding wave.
- Rooms and pipes are harmonic oscillators too (room resonances, organ pipes).

## AX-Synth translation
- The AX-Synth is a PCM "wave + TVF + TVA" subtractive engine (`architecture.tone_signal_path`). Raw material = the wave (`tone.wave_number`). Classic analogue-style source waves exist as PCM: saws (174–193, e.g. 185 "JP-8 Saw", 177 "MG Saw HD"), square (194–202), pulses of fixed widths (203–212), triangle (213–216), sine (220), noise (232 White, 233 Pink).
- Removing harmonics = `tone.filter_type` LPF + lowering `tone.cutoff`. The filter's position decides how many harmonics of the saw survive.
