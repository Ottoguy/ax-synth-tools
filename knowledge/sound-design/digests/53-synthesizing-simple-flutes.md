# SS53 Synthesizing Simple Flutes (Sep 2003): digest

Source: Synth Secrets part 53, https://www.soundonsound.com/techniques/synthesizing-simple-flutes. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Edge-tone excitation: the air jet oscillates across the edge at a rate proportional to blowing speed. **Blowing harder jumps the pitch up the harmonic series** (overblowing).
- Holed flutes (shakuhachi, recorder, orchestral flute) are **open pipes, so all harmonics**. Only the stopped pan pipe/stopped organ flute is odd-harmonic.
- Recorder:
  - tuning is stretched by more than a semitone over its range (the player blows low notes harder)
  - alternative fingerings give slightly sharp/flat pitches and different timbres
  - range works over ~2 octaves from middle C upward
- **Recorder spectrum:** a **dominant fundamental**, a **very weak 2nd harmonic**, a few weak overtones, strong noise; higher partials stretched sharp. Saw, square and triangle each sound wrong; two oscillators an octave apart drift and chorus (wrong).
- **Minimoog recorder (Rhea):**
  - low-level **triangle** + a little white noise
  - filter closed, a **fast filter attack** + moderate emphasis
  - Osc 3 modulates **brightness, not pitch** (pitch vibrato sounds wrong on recorder)
  - a **VCA attack slower than the filter attack**, so the brightness peaks while loudness is still rising: a short burst of bright noise at the start = the blowing "chiff"
- **Oddity recorder (better):**
  - **~40 % pulse** (strong fundamental, weak 2nd, slightly weakened 3rd: woody with some edge), an octave above middle C, + a little white noise
  - LPF opened by an ADSR, a little resonance (edge), key tracking ~65 %
  - a carefully set release gives a pleasant **wooden "thunk" at note-off**
  - **smoothed random (S&H + slew) at ≤ 5 % on the filter** = blowing-pressure inconsistency
  - VCA from the ADSR, no initial gain
- Real recorders also have mode-jumping flutter and tuned noise (only modelling synths or big modulars get close). Expression: tonguing, gentle attacks, legato.

## AX-Synth translation (recorder/whistle) [I]
- Quick: PCM 99 "Flute", 102 "JD Fl Push", 101 "Shakuhachi" (+ 228 "Shaku Noise").
- Synth recorder:
  - tone 1 = 208 "JP8 Pls 40HD" (≈ 40 % pulse), `tone.coarse_tune` +12
  - LPF `tone.cutoff` ≈ 45–60, `tone.resonance` ≈ 10–20, `tone.cutoff_kf` ≈ +65
  - TVF env: T1 short (fast), L1 high, decaying to L3 ≈ 40–60
  - TVA T1 **slower** than the TVF T1 (e.g. TVF T1 5, TVA T1 15–20), L3 127, T4 short–medium (the note-off "thunk")
- Breath: tone 2 = 232/229 noise at a low level (or add a little to tone 1's layer), optionally BPF tracked (`tone.cutoff_kf` 100).
- Blowing inconsistency: `tone.lfo_waveform` RND (smooth random), `tone.lfo_rate` slow–moderate, `tone.lfo_depth_tvf` very small (≤ 5 % feel); `tone.lfo_depth_pitch` 0 (no vibrato for recorder).
- Range/register: best from middle C up two octaves; alto/tenor via `tone.coarse_tune` 0/−12.
- Tonguing vs legato: `common.mono_poly` MONO, `common.legato_sw` ON with `common.legato_retrigger` ON for tongued, OFF for slurred.
