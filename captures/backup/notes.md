# Backup of the user's AX-Synth, 2026-09-26

- `ax-synth-backup-2026-09-26.mid`: Librarian **Read All Data**, then **File → Export SMF**. It holds 2,304 DT1s = 256 User patches × 9 blocks, all checksums valid, in the same format as Roland's own Librarian export (SMF format 0, 96 PPQ).
- There is no `.a8l` yet. The Librarian saves only *Library Windows*, not the Main Window (Librarian manual p.5–6). See NEXT-STEPS 3.1. It's optional, since the `.mid` holds the same sound data.
- Summary against the factory list: `research/generated/user-patches.{csv,json}` (`research/tools/backup_summary.py`).
  - 254 of 256 stored names equal the Owner's Manual list.
  - Slots 3-10 and 3-11 (Owner's Manual "Reso Bs 2"/"Reso Bs 3") are stored as "Reso Bs 1"/"Reso Bs 2". They are different sounds from 3-1 "Reso Bs 1". It's unknown whether this is a factory naming quirk or a previous owner's edit.

⚠ **This file restores all 256 sounds.** Playing it to the synth (or Librarian *Import SMF* + *Write All*) overwrites every User patch with this backup. Use it only as a deliberate restore. Keep a copy outside the project.
