# SS22 From Springs, Plates & Buckets To Physical Modelling (Feb 2001): digest

Source: Synth Secrets part 22, https://www.soundonsound.com/techniques/springs-plates-buckets-physical-modelling. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Echo = a few discrete reflections. Reverb = the original + early reflections (distinct, first 1–2 bounces) + a dense tail (reflections under ~30 ms apart fuse).
- RT60 = the time for a 60 dB decay: longer in big, hard rooms; shorter with more absorption. Rooms have resonant modes, so reverb colours the frequency response too (time/frequency duality).
- Reverb types:
  - echo chamber: natural
  - **plate**: bright, dense, smooth; a classic vocal/drum sheen
  - **spring**: few modes, so a metallic "boing" with regular echoes; characterful
- Acoustic instrument **bodies** (violin, guitar) are small resonant rooms. The body's modes impose a fixed frequency response on the source. A violin string at the bridge is almost a sawtooth, yet a violin doesn't sound like a saw because of its body.
- Physical-modelling trick: put very short delays/reverbs (≈1–4 ms, with feedback) **inside** the sound (before the final ambience) to create body resonances. Three parallel short delays at different times give a more 3-D body. A harder material means a longer decay (RT60).
  - Worked example: a 500 Hz body mode ↔ 0.34 m cavity ↔ ~2 ms round-trip delay. The article misprints "microseconds".
- Then add a large hall reverb at the end: acoustic instruments often sound best in a concert-hall-sized space.

## AX-Synth translation
- Final ambience: the reverb unit, `reverb.type`
  - REVERB (general)
  - SRV ROOM (small, early reflections)
  - SRV HALL (large, long tail, orchestral)
  - SRV PLATE (bright, dense)
  - Amount: `reverb.level` and the per-tone sends (`tone.reverb_send_mfx`/`tone.reverb_send_direct`). There's no spring type in the reverb unit.
- Body resonance/formants: the AX-Synth effects are post-voice (one MFX per patch). For **static, linear** filtering (EQ, fixed formant peaks) that's equivalent to per-voice filtering, so body modes can be approximated with MFX 1 EQUALIZER (peaking bands), 2 SPECTRUM (8-band graphic), or 9 HUMANIZER (vowel formants) [I].
  - Short comb/body delay with feedback: MFX 24 FLANGER or 43 DELAY with ms-range delay and feedback. Metallic resonance at short delays.
- The best route is to start from PCM that already contains the body: 49–56 acoustic/electric guitars, 301–304 strings, 103/104 oboe, 99 flute, etc. The PCM wave already has the body modes; add the TVF/TVA contours on top.
