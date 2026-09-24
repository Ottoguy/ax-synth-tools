# SS34 Practical Bass Drum Synthesis (Feb 2002): digest

Source: Synth Secrets part 34, https://www.soundonsound.com/techniques/practical-bass-drum-synthesis. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- **Classic analogue kick on a one-oscillator synth:**
  - filter **resonance at max** (self-oscillating ≈ a sine), cutoff at **minimum**, no key tracking
  - envelope → cutoff ≈ 50–60 %, envelope A = 0, D = R ≈ 50 % (the same whether held or released), S = 0
  - the same envelope fully on the VCA, no initial gain
  - The downward-sweeping sine = the kick. The pitch never "sustains".
- Slightly less resonance lets some oscillator through: a tonal "shell" quality, more like a real drum than a drum-box.
- Adding a 16' saw/sub-oscillator with a lower envelope amount and a cutoff just opening the lowest harmonics gives a ringing tonal kick. It's very sensitive to cutoff: from **huge booming** to **tight snappy**.
- **SynDrum "ray gun":** the same patch with 100 % key tracking, played high. The cheesy late-'70s zap.
- A zero attack makes an audible click: a desirable part of the beater sound, not a fault.
- Mid/high noise matters less than theory suggests for modern (low-emphasised) kicks. Real concert bass drums have much more mid content.
- **TR-909 kick:** a sawtooth **waveshaped to ~sine** with a pitch envelope (instant attack, slow decay) through an AR VCA; plus low-passed noise + a click pulse through a second short envelope; the two are mixed. Accent raises the level and alters the decay.
- **TR-808 kick:** a self-decaying resonant (bridged-T) oscillator "pinged" by the trigger; a trigger pulse is added as the click; an LPF tames the click. It **goes slightly flat on long decays**, which makes it convincing.

## AX-Synth translation [I]
- 808-style:
  - tone = 220 "Sine", play C1–G1
  - TVA T1 0, L1 127, T3 long (boom length), L3 0, `tone.env_mode` NO-SUS
  - pitch env: `tone.penv_depth` +, L0 ≈ +8, a fast T1 back to ~0, then L3/L4 slightly **negative** (−1…−3) over a long T3, i.e. the pitch sags on long decays
  - click: low `tone.cutoff` LPF or a small separate click tone
- 909-style:
  - body: triangle/sine (214/220) with a larger, faster pitch drop (L0 +20…+30, T1 short)
  - tone 2: 232 "White Noise" through LPF (`tone.cutoff` ≈ 60–80), TVA decay ≈ 10–20
  - tone 3: click 248 "Key On Click"
  - Accent = velocity: `tone.tva_vel_sens` +, `tone.penv_vel_sens` +.
- Self-oscillating-filter method: the AX-Synth TVF's self-oscillation is unverified, so prefer the sine + pitch-envelope method.
- SynDrum zap: sine, pitch env L0 +40…+63, T1 medium, `tone.pitch_kf` 100, played high.
- Tight vs boomy: the TVA T3 length and the pitch-drop speed. Tight = short T3 + fast drop; boomy = long T3 + slower drop.
- A punchy mix: MFX 40 COMPRESSOR or 4 LOW BOOST.
