# captures/live: notes (NEXT-STEPS step 2)

Set-up: AX-Synth Editor / Librarian output → loopMIDI port → MIDI-OX (Monitor, SysEx lines). **No synth connected**, and nothing answered on the Editor's input.
Logged 2026-09-23 by the user. These notes were written afterwards from the user's report and the decoded logs (`py -3 research/tools/midiox_log.py captures/live/*.txt`).
The files were saved as `*.txt.txt` and have been renamed to `*.txt`; the content is unchanged.

| File | What was done | What the app showed | What the log contains |
|---|---|---|---|
| `01-cutoff.txt` | Tone 1 TVF Cutoff moved | – | 1 DT1: cutoff 127 → **124** (`1F 00 20 49`). INIT's cutoff is already 127, so it couldn't go "up". The move back isn't in the log. |
| `02-name.txt` | Patch name → `TEST` | – | 1 DT1: the whole 12-byte name `TEST␠␠␠␠␠␠␠␠` at `1F 00 00 00` |
| `03-steppitch.txt` | MFX type → STEP PITCH SHIFTER, then Balance and Level dragged | – | Whole-MFX-block DT1 (145 B), then mfxType DT1, then 9 × Balance (`1F 00 03 01`: 100 → 0 % wet) and 5 × Level (`1F 00 03 05`: 127 → 112). The user said it was hard to move one tick, so there are several steps per drag. |
| `04-system.txt` | Master Tune and Beam Range changed | – | 7 × masterTune (`02 00 00 00`), 11 × beamRangeLower (`02 00 40 0B`: 0 → 33), 7 × beamRangeUpper (`02 00 40 0C`: 127 → 109) |
| `05-read.txt` | Editor **READ** | "Unable to read/write data." | 2 × Identity Request, 3.0 s apart |
| `06-sync.txt` | Editor **SYNC** | "Unable to read/write data." | 2 × Identity Request, 3.0 s apart |
| `07-write.txt` | Editor **WRITE** | "Unable to read/write data." | 2 × RQ1 for **User patch 1-1's name** (`30 00 00 00`, 12 B), then 2 × Identity Request |
| `08-librarian.txt` | Librarian **Read Selected** | "Unable to read/write data." | 2 × Identity Request, 3.0 s apart |
| (`09-librarian-write`) | not captured: the Librarian's read already failed | – | – |

The analysis is in `research/live-capture-analysis.md`.
