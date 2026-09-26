# Read-only request test (NEXT-STEPS 3.3), 2026-09-26

Written from the user's report ("no errors or complications").

1. Selected LEAD GUITAR, variation 1 (SearingGtr 1).
2. MIDI-OX *Send/Receive SysEx*: sent `research/generated/experiment-rq1-temporary-patch.syx` (10 RQ1s) and saved the reply as `reply.syx`: 10 DT1s, all checksums valid.
3. [SHIFT] + lit LEAD GUITAR button → "UOl", lowered the volume a few steps, released [SHIFT] without WRITE. Sent the same requests again → `reply-after-volume.syx`: again 10 DT1s.
4. Switched to another sound and back.

Results (tests `SynthRequests`):
- **Our own request file works.** Every RQ1 got exactly one DT1 with the same address and the requested size.
- **System Controller is 0x50 (80) bytes**, as the MIDI Implementation says. The Editor's model has 0x4F. Byte `00 4F` = 1 (Portamento Mode).
- **The Temporary patch = SearingGtr 1**, byte-identical to User patch 96 in the backup, so the working copy follows the panel selection.
- **Both replies are byte-identical.** The panel volume ("UOl") isn't a patch or System Controller value: per Owner's Manual p.26, it belongs to a FAVORITE memory (stored only by [WRITE] + FAVORITE). Where the synth keeps the live, unsaved value is untested; the candidate is Setup. See NEXT-STEPS 3.5 (optional).
