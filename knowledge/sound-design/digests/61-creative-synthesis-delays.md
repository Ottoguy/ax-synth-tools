# SS61 Creative Synthesis With Delays (May 2004): digest

Source: Synth Secrets part 61, https://www.soundonsound.com/techniques/creative-synthesis-delays. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Effects are part of sound design: program them creatively rather than accepting presets.
- **Analogue (BBD) vs digital delays:** a BBD adds cumulative per-stage errors (noise, systematic colouration), so repeats degrade, darken and get noisy (the "warm" sound). Clean digital repeats stay identical.
- **Tape echo:** multiple playback heads give multiple, possibly **syncopated** taps; an erase head / **regeneration (feedback)** sets how the repeats decay (0 % = one set of taps; 100 % = endless mush). Repeats degrade with each pass on tape/BBD.
- **Mix the dry signal in** so the first sound lands on the beat.
- **Ping-pong delay:** cross-fed L/R delays make the repeats bounce between the speakers.
- **Reverb from delays:** cascading delay lines with feedback at decreasing delay times turns discrete echoes into dense early reflections + a tail. Constant delay times leave a **metallic** colouration (like a spring reverb's three modes): a useful effect, not a realistic room. Different left/right delays give a spacious stereo reverb (real rooms give each ear different reflections; high concert-hall ceilings help).

## AX-Synth translation [I]
- Echo types in MFX:
  - 43 DELAY (clean digital, L/R times, feedback)
  - 44 LONG DELAY
  - 45 SERIAL DELAY (two delays in series)
  - 47 3TAP PAN DELAY, 48 4TAP PAN DELAY, 49 MULTI TAP DELAY (multi-head, syncopated taps)
  - 50 REVERSE DELAY, 51 SHUFFLE DELAY (swing), 52 3D DELAY
  - 53 ANALOG DELAY, 54 ANALOG LONG DELAY (BBD-style degradation)
  - 55 TAPE ECHO (tape heads + wow/flutter)
  - combos 68 OVERDRIVE→DELAY, 71 DISTORTION→DELAY, 74 ENHANCER→DELAY, 75 CHORUS→DELAY, 76 FLANGER→DELAY
- The chorus unit's second type is a delay: `chorus.type` DELAY (patch-wide send effect, `tone.chorus_send_mfx`/`tone.chorus_send_direct`).
- Ping-pong: MFX 43 DELAY with feedback and different L/R times (or the 3TAP/4TAP pan delays).
- Feedback ≈ "regeneration"; dry/wet balance parameters exist in each type (see `knowledge.md`).
- Metallic/spring-like reverb flavour: short multi-tap delays with feedback; for natural ambience use the reverb unit (`reverb.type` SRV ROOM/HALL/PLATE).
