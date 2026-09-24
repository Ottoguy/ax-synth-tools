# SS18 Priorities & Triggers (Oct 2000): digest

Source: Synth Secrets part 18, https://www.soundonsound.com/techniques/priorities-triggers. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- Mono synths must choose which held note sounds:
  - lowest-note (US: Moog, ARP)
  - highest-note (Japanese: SH-09, MS-20, CS20)
  - last-note (always plays the key just pressed, the most "natural" for fast playing)
  - first-note
- Overlapping notes (normal legato playing) can make notes speak late or be cut short depending on the priority.
- Triggering:
  - **single-trigger**: a new envelope only when all keys were released. Overlapped notes slur at the sustain level, which is natural for legato wind/brass phrasing.
  - **multi-trigger**: re-articulates on every key press. Punchy, but with low/high priority the attacks can land on the wrong note.
  - **reset-to-zero**: choppy.
- If sustain = 0 (AR/AD envelopes), a note that becomes audible later (after an overlap) may be silent. Sustained envelopes are needed for legato mono lines.
- Performance trick (Wakeman/Emerson): hold a low drone note on a high-note-priority, multi-trigger mono synth and play staccato above; the pitch drops to the drone between notes, un-articulated. Add a touch of portamento for swoops.

## AX-Synth translation
- Mono playing: `common.mono_poly` MONO.
  - `common.legato_sw` ON ≈ single-trigger slurs (no re-attack while overlapping)
  - `common.legato_retrigger` controls whether the envelope restarts on legato
  - legato OFF ≈ multi-trigger
- The note priority in MONO mode isn't documented in the Editor manual [I: most likely last-note, as on Roland PCM synths; verify by ear].
- `common.priority` (LAST/LOUDEST) is **voice stealing** when polyphony is exceeded, not mono note priority.
- Legato mono lines (lead, flute, brass) need non-zero TVA sustain (`tone.aenv_levels` L3) so slurred notes stay audible.
- Glide swoops on legato: `common.portamento_sw` ON, `common.portamento_mode` LEGATO (glide only on overlapping notes), `common.portamento_time`.
