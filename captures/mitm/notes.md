# MIDI-OX in the middle (NEXT-STEPS 3.0 / 3.1), 2026-09-26

Written from the user's report. Setup as in NEXT-STEPS 3.0: Editor/Librarian → loopMIDI → MIDI-OX → "Roland AX-Synth" and back. In the logs, **IN PORT 1 = software → synth** and **IN PORT 3 = synth → software**. The files were renamed from `*.txt.txt`.

| File | What was done | Result |
|---|---|---|
| `01-librarian-read-selected.txt` | Librarian: Read Selected on row 1-1 | Identity exchange, Setup bank read, then 9 RQ1/DT1 pairs for User patch 0 "AX Saw Lead" |
| `02-editor-read.txt` | Editor: READ | Identity exchange, Setup/System reads, then 9 RQ1/DT1 pairs for the Temporary patch ("INIT PATCH") |
| `03-editor-sync.txt` | Editor: SYNC (after the backup) | Identity exchange, then 12 DT1s: Setup, System Common, System Controller, the 9 Temporary blocks |

Between the captures: Librarian **Read All Data**, then **Export SMF** → `captures/backup/`. The user didn't know how to save the `.a8l`; see NEXT-STEPS 3.1.

Analysis: `research/mitm-capture-analysis.md`.
