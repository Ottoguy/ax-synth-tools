# SS33 Synthesizing Drums: The Bass Drum (Jan 2002): digest

Source: Synth Secrets part 33, https://www.soundonsound.com/techniques/synthesizing-drums-bass-drum. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- A double-headed bass drum with equal tension gives quasi-harmonic low modes (a harmonic series frequency-shifted up ~7 Hz: 50, 93, 136, 179 Hz …).
  - With the carry head detuned (lower tension), or a **kick with a port hole**, the modes are close to a true harmonic series.
- **Kick drum rule:** a harmonic-ish spectrum at low frequencies + densely packed **enharmonic partials at mid/high frequencies**, especially **250 Hz–1 kHz** (where the ear is most sensitive).
- Low modes loudest, amplitudes falling fast with frequency: a **triangle or filtered saw** is a good source. Decay is roughly the same for all important partials (one envelope).
- **Pitch drop:** a hard hit stretches the head, raising the tension and so the pitch. The pitch falls as the vibration decays: **a couple of semitones** from start to finish (~10 % pitch change vs 100 % amplitude change). Drive both from the same AR envelope, pitch at reduced depth.
- **Beater click:** hundreds of very short-lived high partials lasting a few ms. Either a short noise burst, or a very fast envelope briefly opening an LPF on an FM/enharmonic mid-band component.
- Mid-band enharmonic cluster: two oscillators in FM + a band-pass filter.
- A frequency shifter adds a fixed Hz to all partials (making them inharmonic), unlike a pitch shifter (fixed ratio). Missing-fundamental illusion: correctly spaced partials make the brain hear an absent fundamental (organ 32' trick).

## AX-Synth translation (kick) [I]
- Tone 1 body:
  - 214 "Syn Triangle" or 220 "Sine" (or 98 "Atk Syn Bass" for an 808/909 flavour)
  - play low (C1–C2), `tone.pitch_kf` 100 or lower
  - TVA T1 0, T3 short–medium, L3 0, `tone.env_mode` NO-SUS
  - Pitch envelope: `tone.penv_depth` +, `tone.penv_levels` L0 ≈ +10…+20 falling to 0 over T1/T2 ≈ 20–40. Deep "boom" = small drop (2 semitones, realistic); electronic "zap" = large, fast drop (808/909-style).
  - `tone.penv_vel_sens` + (harder = bigger drop)
- Tone 2 mid cluster (250 Hz–1 kHz): FXM on (`tone.fxm_sw`, `tone.fxm_depth` high) on a sine/triangle at +12…+24, `tone.filter_type` BPF around the low-mid, short decay. Or noise 233 through BPF.
- Tone 3 click: 248 "Key On Click", 246 "SynBassClick" or 232 white noise with HPF, TVA T3 ≈ 0–5 (a few ms).
- Keep the reverb send low on kicks (`tone.reverb_send_mfx`), and optionally MFX 40 COMPRESSOR for punch.
