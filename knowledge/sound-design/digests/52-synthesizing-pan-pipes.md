# SS52 Synthesizing Pan Pipes (Aug 2003): digest

Source: Synth Secrets part 52, https://www.soundonsound.com/techniques/synthesizing-pan-pipes. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- The flute family (pan pipes, recorder, shakuhachi, flue organ pipes, flute, piccolo) is excited by blowing against an **edge** (a flow valve).
- **A pan pipe is closed at the bottom**, so it produces **odd harmonics only** (square/triangle family) and is **mellow** (weak upper harmonics). Brass (conical) is saw-like.
- **Turbulence noise** is the defining feature, but not as independent added noise: the noise is **coloured by the pipe**, so it's **pitched**, tuned to the note's harmonics, and most audible at **high frequencies** (the high harmonics are masked by noisy bands).
  - Synthesis: "blue" noise (white → gentle HPF) → a band-pass formant bank tracking the note; ~6 bands near self-oscillation at octaves and fifths is enough for a lovely breathiness.
- **The chiff:** a noisy attack burst, independent of the tone: *the* defining pan-pipe feature. Noise → LPF + VCA on a fast AR envelope (the filter passes only during attack/decay).
- **The tone swells in after the chiff and the breath noise** (a slight delay before the tonal attack).
- Modulation: vibrato, a little tremolo and a little filter modulation, with the **tremolo inverted relative to the filter** (gain down as the filter opens) to keep the loudness steady.
- **Noise injected into the tonal filter's cutoff** (a little high-frequency noise → cutoff CV) = a rough, breathy edge that binds tone and noise into one sound.
- Keyboard needs:
  - oscillator and noise formants **track together**
  - **multi-triggering** (a chiff on every note, even legato)
  - filter key tracking under 1:1
- Expression: joystick Y = modulation depth, X = pitch bend (real pan-pipe players bend a lot); a velocity-sensitive attack is a big improvement; a breath controller would be even better; add reverb.
- Real flutes are *simpler* than pan pipes (less breath dominance), so they work on basic synths (SS53).

## AX-Synth translation (pan flute) [I]
- Quick route: PCM 100 "Pan Flute", 101 "Shakuhachi", 99 "Flute" (they already include chiff/breath).
- Synthesised (3 tones):
  - Tone 1 (tone): 214/215 triangle or 196 square, LPF `tone.cutoff` ≈ 50–65, `tone.cutoff_kf` ≈ +50…+70.
    - TVA T1 ≈ 15–25 with `tone.delay_mode` NORMAL + `tone.delay_time` small, so it swells in after the chiff.
    - LFO1: small `tone.lfo_depth_pitch` (vibrato), small `tone.lfo_depth_tvf` (+), small `tone.lfo_depth_tva` with **negative** sign (inverted tremolo).
  - Tone 2 (pitched breath): 232 "White Noise" or 228 "Shaku Noise"/229 "Digi Breath".
    - `tone.filter_type` BPF, `tone.cutoff_kf` +100 (tracks the note), `tone.resonance` high (near oscillation)
    - TVA sustained at a low level
  - Tone 3 (chiff): white noise, LPF, TVA T1 0, T3 very short (≈ 5–10), L3 0; `tone.tva_vel_sens` + (a velocity-sensitive chiff).
- Every note chiffs: `common.legato_sw` OFF (or `common.legato_retrigger` ON).
- Noise on the cutoff: `tone.lfo_waveform` RND at a high rate, tiny `tone.lfo_depth_tvf` on tone 1 (a rough edge).
- Expression: ribbon bends (`common.bend_up` 2), Matrix CC01 → LFO1 PCH DEPTH, AFTERTOUCH → LEVEL/CUTOFF; `tone.aenv_t1_sens` + (a velocity-sensitive attack).
- Reverb: SRV HALL, generous.
