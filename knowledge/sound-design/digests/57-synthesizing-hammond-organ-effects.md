# SS57 Synthesizing Hammond Organ Effects (Jan 2004): digest

Source: Synth Secrets part 57, https://www.soundonsound.com/techniques/synthesizing-hammond-organ-effects. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- A resonant self-oscillating filter reduces the low end, so the synth's "88 8000 000" sounded like 67 8000 000, or 67 8321 000 including the filter's leakage.
- **Percussion (Hammond sense):** a decaying accent of the **2nd or 3rd harmonic of 8'** (the 4' or 2⅔' pitch) at note start.
  - switches: Normal/Soft (level), Fast/Slow (decay)
  - it slightly lowers the sustained level
  - **single-triggered:** no percussion if another key is still held
  - Imitating it with a VCA "blip" on the whole sound is wrong (and a longer filter decay turns the click into a "soggy squelch"). The percussion must be a **separate path** (a separate pitch with its own AD envelope).
- **Scanner chorus/vibrato:** a tapped delay line scanned mechanically (≈ 6–7 Hz, the "six and a bit" LFO setting).
  - V-1/2/3 = pure pitch vibrato at three depths
  - **C-1/2/3 = the dry signal + one vibrato'd copy** = the classic chorus; **C-3** is organists' favourite
  - Lush multi-stage ensemble choruses are too lush for it.
  - All drawbar pitches must be modulated **equally**.
  - Reid dislikes pure V settings ("cheesy").
- **Leakage:** a faint mix of other tonewheel pitches and noise gives a throaty quality. A tiny bit of noise can suggest it (if it's not resonantly filtered).
- **Overdrive and compression:** valve preamp/amp breakup, from mild burr to full crackle. Adding chord notes compresses (a natural chord compression that clipping also produces).
- **Reverb:** spring reverb in spinets/A100 (after the overdrive; the A100 has a separate reverb amp/speaker, so the reverb is kept in parallel with the dry signal).
- The Leslie rotary speaker is the most important effect (SS58).

## AX-Synth translation [I]
- Percussion: a dedicated tone (e.g. tone 4 = 220 sine or an organ wave) at `tone.coarse_tune` +12 (2nd) or +19 (3rd). TVA: T1 0, L1 127, T3 short (fast ≈ 20–30) or longer (slow ≈ 40–60), L3 0, `tone.env_mode` NO-SUS. `tone.level` sets Normal/Soft.
  - Single-trigger isn't reproducible in POLY [I]; PCM 34 "3rd Perc Org" and 35 "Perc Organ" contain percussion.
- Scanner chorus C-3 ≈ MFX 23 CHORUS or the chorus unit with a ≈ 6–7 Hz rate, medium depth, 50 % wet (dry + one modulated copy). Vibrato V-x ≈ LFO on all tones' `tone.lfo_depth_pitch` equally, rate ≈ 6–7 Hz, `tone.lfo_key_trigger` OFF (free-running like a scanner).
- Leakage: a very low-level noise tone (233 pink) or a faint extra sine drawbar.
- Overdrive + reverb: MFX 35 OVERDRIVE (or 22 VK ROTARY with drive; see SS58), then the reverb unit (`reverb.type` REVERB/SRV ROOM) and MFX reverb sends, so the reverb comes after the drive, as on the A100.
- Organ PCM with effects baked in: 37–41 "RtryOrg", 26–29 "JLOrg Slow/Fast L/R", 270 "OD Organ".
