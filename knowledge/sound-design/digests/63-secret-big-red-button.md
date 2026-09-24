# SS63 The Secret Of The Big Red Button (Jul 2004): digest

Source: Synth Secrets part 63, https://www.soundonsound.com/techniques/secret-big-red-button. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts (the series' conclusions)
- Think of a synth as **Sources, Modifiers and Controllers**, not just "oscillator = pitch, filter = timbre, amp = loudness".
  - **Sources:** oscillators, noise, external input. **The source waveform constrains everything:** you can't make hollow sounds without a hollow wave, or brass without a saw-like/brass wave. Learn to recognise waveforms by ear:
    - saw: bright, buzzy, full; brass/strings
    - square: hollow, woody; clarinet
    - narrow pulse: thin, nasal, reedy
    - triangle/sine: soft, pure; flute/whistle
  - **Modifiers:** LPF, HPF, BPF, notch, comb, S&H, ring mod, frequency shifter, slew, reverb, chorus, and they can go in any order.
  - **Controllers:** envelopes, LFOs, wheels, joysticks, aftertouch.
  - Roles depend on the patch: an oscillator can be a controller (FM), and a resonant filter can be a source (self-oscillation).
- **Control the controllers:** VCAs/filters/S&H on control signals (e.g. an envelope amount, an LFO depth on the mod wheel).
- Know triggers vs gates, single vs multi-trigger, key priority, mono vs poly for each sound.
- **Expression:** envelopes and LFOs make every note identical, which is both their strength and their weakness. Use physical controllers (bend/ribbon for vibrato, aftertouch, mod) so notes "speak" differently.
- **Sforzando brass** needs ≥ 5 envelope stages (peak, die away, swell later); many "mighty" analogues can't do it, while cheap digital synths with multi-stage envelopes can.
- Analogue isn't always better: it's best for overdriven LPF sweeps of saws; for close brass/EP imitations or lush evolving textures, digital/sample-based synths often win. Choose the instrument per sound.
- Random knob-twiddling produces clichés. **Analyse the target sound** (source, modifiers, controllers) and select deliberately.
- "There is no Big Red Button."

## AX-Synth translation [I]
- The AX-Synth's "sources" are its 313 PCM waves (choosing the right wave is step 1); its "modifiers" are the TVF types, Structure (booster/ring mod), FXM and the MFX/chorus/reverb; its "controllers" are 3 envelopes, 2 LFOs + a step LFO, Matrix Control and the performance controllers (ribbon, mod bar, aftertouch knob, D-Beam).
- Sforzando: AX-Synth TVA/TVF envelopes have T1–T4 with 3–5 levels, enough for sforzando/spit-brass (see SS08).
- Controlling controllers: `matrix.destination` LFO1/LFO2 depths/rates and envelope times, all modulatable by `matrix.source` (CC01, AFTERTOUCH, VELOCITY, KEYFOLLOW …); `mfx.control_source` for effect parameters.
- Expression-first design for a keytar: map the ribbon (bend), the mod bar (CC01) and the aftertouch knob to musically meaningful destinations in every generated patch.
