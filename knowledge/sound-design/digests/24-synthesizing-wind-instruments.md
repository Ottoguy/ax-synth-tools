# SS24 Synthesizing Wind Instruments (Apr 2001): digest

Source: Synth Secrets part 24, https://www.soundonsound.com/techniques/synthesizing-wind-instruments. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Open pipe (flute, recorder: an edge excites it): all harmonics; fundamental wavelength = 2 × length.
- Closed pipe (clarinet: reed/lip valve at one end, cylindrical bore): **odd harmonics only** → hollow, square-like; an octave lower than the open pipe of the same length.
- Conical and flared bores (brass, oboe, saxophone): the full harmonic series despite the lip/reed valve, so brass is **brash, sawtooth-like**, not square.
- Waveform suggestions:
  - recorder: saw or triangle (full series, soft)
  - clarinet: **square**
  - brass: **sawtooth**
- Overblowing: the recorder jumps an octave (2nd harmonic); the clarinet jumps a twelfth (3rd harmonic).
- Harmonic **amplitudes** matter as much as which harmonics exist.
- **Loud vs soft brass:** a quiet note has ~6 harmonics with a dominant fundamental (soft); a loud note has ≥15 significant harmonics, a relatively weaker fundamental, and upper harmonics dominating (brighter, "brassier").
- Higher notes have fewer significant harmonics than low notes (the instrument's finite bandwidth).
- **Trumpet recipe (four rules):**
  1. Sawtooth source.
  2. LPF cutoff rises and falls with loudness: brighter when louder (couple the filter to dynamics).
  3. Emphasise upper harmonics as loudness increases (resonance or EQ rising with level).
  4. Cutoff tracking less than 1:1 with pitch (cutoff rises more slowly than pitch, tapering the harmonics of high notes).

## AX-Synth translation
- Waves:
  - brass: saws 174–193 or brass PCM 113 "Flugel", 114 "Trumpet 1", 115 "Tp Section", 116/117 "Oct Brass p/f", 118 "XP Brass", 297–300 "Trumpet 2/3"
  - clarinet-like: square 196 "Fat Square", 197 "JP-8 Square"
  - recorder/flute: 213–216 triangles, 99 "Flute", 102 "JD Fl Push"
- Brighter-when-louder:
  - `tone.cutoff_vel_sens` positive (velocity opens the filter) with `tone.cutoff_vel_curve`
  - `tone.fenv_vel_sens` positive (a harder hit gives a bigger envelope sweep)
  - `tone.res_vel_sens` positive (rule 3)
  - For sustained dynamics after the attack: Matrix Control `matrix.source` AFTERTOUCH or CC01 → CUTOFF + LEVEL together (the AX-Synth aftertouch knob or mod bar as a "breath" control).
- Rule 4: `tone.cutoff_kf` around +50 to +80 (less than +100) so high notes are relatively darker [I: exact scale unverified].
- Velocity-switched layers (soft vs loud PCM): `tmt.velo_lower`/`tmt.velo_upper` with fades (`tmt.velo_fade_lower`/`tmt.velo_fade_upper`), e.g. 116 "Oct Brass p" at low velocity and 117 "Oct Brass f" at high velocity; similarly 297/298/299 Trumpet 2 p/mf/ff, 285–296 Sax p/mf/f.
