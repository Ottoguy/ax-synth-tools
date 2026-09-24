# SS60 From Analogue To Digital Effects (Apr 2004): digest

Source: Synth Secrets part 60, https://www.soundonsound.com/techniques/analogue-digital-effects. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Leslie refinements:
  - The horn's radiation pattern has **lobes**, so the loudness wobbles as they rotate past, differently for each frequency.
  - The **bass rotor** is too small to Doppler-shift low frequencies much: it's mainly **tremolo (amplitude)**, not vibrato.
- Some analogue effects have a valued "warmth" (Electro-Harmonix Electric Mistress and MXR flangers, Small Stone phaser, Big Muff fuzz). Digital is king for rotary simulation and new, esoteric effects.
- The rest of the article is digital-logic background (logic gates, flip-flops, shift registers = a digital delay line equivalent to a BBD). No sound-design content beyond: **delay time = the number of stages × the clock period**, and anti-alias/reconstruction filtering.

## AX-Synth translation [I]
- The rotary MFX (21/22) models these details. If approximating manually, give the low tones a TVA LFO (tremolo) and no pitch LFO; give the high tones both.
- Warm analogue-style modulation effects: MFX 24 FLANGER, 11 PHASER, 13 MULTI STAGE PHASER, 53/54 ANALOG DELAY / ANALOG LONG DELAY, 55 TAPE ECHO; fuzz-like drive: 36 DISTORTION, 38 VS DISTORTION.
- Background theory only; no parameter mapping needed.
