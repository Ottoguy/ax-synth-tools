# SS42 Synthesizing Pianos (Oct 2002): digest

Source: Synth Secrets part 42, https://www.soundonsound.com/techniques/synthesizing-pianos. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- No subtractive, additive or FM synth has made a convincing acoustic piano. **Only samples** do (Kurzweil 250; the Roland RD1000/MKS20; the Roland U20 RS-PCM, an ancestor of the JV engine, the family the AX-Synth belongs to).
- **Construction:** 88 notes spanning ~80 % of human hearing. Bass: single thick wound strings; then pairs; then **tricords** (three strings) of wound, then plain strings. The tone changes greatly across the range.
- **The hammer** stays on the string long enough to make the strike point a **node**:
  - struck at the centre, the fundamental and odd harmonics are missing initially
  - real hammers strike 1/7–1/15 of the way along, varying across the keyboard
  - the spectrum changes with velocity, inconsistently across the range
- **Tricord detuning:** the strings are never exactly in tune, so there's **beating and energy exchange** between them.
- **Amplitude:**
  - a hammer impact then a slow decay whose **rate diminishes** over time: a two-slope "double decay" with a tail lasting tens of seconds
  - **velocity → level**
  - **low notes decay slower; high notes decay faster and peak quieter**
- **Brightness:**
  - three stages: a hammer "chink" (brief partials above the pitch + mechanical noise) → a transitional spectrum → a tail dominated by the fundamental (the highs die fastest)
  - harder = brighter; higher notes start brighter but lose their highs faster
  - so the cutoff needs velocity + key tracking + an envelope, with **key-dependent envelope times**
- The lowest notes have a weak fundamental (an implied pitch).
- **Stretch tuning:** stretched string partials mean an equal-tempered piano sounds flat/dull. Tune the upper octaves slightly sharp (and the bass flat): a "sweeter" sound.
- **Sustain pedal:** lifts all dampers, so the struck notes excite other strings (**sympathetic resonance**), and the soundboard and body add rich resonance and reverberation.
- Analogue results sound like Wurlitzer/Pianet (piano-*like*, fine for rock'n'roll), not a Bösendorfer.

## AX-Synth translation [I]
- Use the grand PCM:
  - 254/255 "AX Grand mpL/R" (soft layer, stereo pair), 256/257 "AX Grand ffL/R" (loud layer)
  - crossfade them with `tmt.velo_lower`/`tmt.velo_upper` and `tmt.velo_fade_lower`/`tmt.velo_fade_upper`
  - 1 "JD Piano" as an alternative
  - Keep the wave's attack (`wave.oneshot_loop`).
- `tone.filter_type` LPF2 (the manual: "good for acoustic piano"), `tone.cutoff_vel_sens` + (harder = brighter), `tone.cutoff_kf` + (higher = brighter), TVF env decaying (L1 high → lower L3).
- Decay by key: `tone.aenv_time_kf` + and `tone.fenv_time_kf` + (high notes decay faster); `tone.bias_level`/`tone.bias_position`/`tone.bias_direction` (high notes slightly quieter).
- Double decay: TVA T1 0, L1 127, T2 short, L2 ≈ 90, T3 long, L3 0, `tone.env_mode` NO-SUS.
- Tricord beating/chorus: a second layer of the same wave with `tone.fine_tune` +2…+4 cents (subtle).
- `common.stretch_tune` 1–3 (piano stretch).
- Sustain pedal: `tone.rcv_hold` ON + `tone.redamper` ON; MFX 78 SYMPATHETIC RESONANCE (the damper/pedal resonance effect); reverb SRV HALL/ROOM.
- Hammer "chink": a short tone with a bright attack wave (247 "JD EP Atk", 248 "Key On Click") tuned above the note, TVA T3 very short.
- Electric pianos (Reid: synth pianos end up Rhodes/Wurli-like): 2–16 Stage/Dyno EP, Wurly, 80's (DX) EPs are available as PCM.
