# Live Editor/Librarian traffic (captures/live/)

**What:** MIDI-OX logs of what AX-Synth Editor v1.00 and Librarian v1.00 transmit on their MIDI output while a user edits values and presses READ/SYNC/WRITE. The output went to a loopMIDI port, **no synth was connected**, and nothing was ever answered. These are NEXT-STEPS step 2 captures, made 2026-09-23. The user's notes are in `captures/live/notes.md`.

**Decoder:** `py -3 research/tools/midiox_log.py captures/live/*.txt`. For each message it prints the timestamp, gap, length check, checksum and every parameter covered, named and decoded with our schema. Tests: `tests/test_schema.py::LiveEditorCaptures` (6 tests, byte-exact).

Evidence labels: **[F]** our files (these captures count as [F]: bytes Roland's software produced), **[D]** Roland docs, **[I]** inference.

## Summary

- **53 messages, all well formed [F].** Every length matches MIDI-OX's buffer count, every Roland checksum is correct, and all messages use device ID `10` and model `00 00 3C`.
- **Every edit message is reproduced byte-for-byte by our code** (`build_dt1` + schema address + `encode_value`): cutoff, name, Master Tune, Beam Range, the two STEP PITCH SHIFTER values, and the 145-byte MFX block.
- **What changes in the project:**
  - Two open questions are closed: the `00 81` address, and how single-parameter edits look on the wire.
  - One inference is replaced: patch names are read by plain RQ1 on the User area, not through `cm`.
  - The Editor's communication protocol is gated behind an Identity Request. A loopback without a synth therefore can't show any more of READ/SYNC/WRITE, and everything that remains needs the real synth (see "Consequences").

## Findings

### 1. Single-parameter edits: one DT1 per value, sent immediately [F]

| Capture | Address | Parameter (our schema) | Payload | Decoded |
|---|---|---|---|---|
| 01 | `1F 00 20 49` | `fm.pat.tone[0].tvfCutoffFrequency` | 1 B | 124 |
| 02 | `1F 00 00 00` | `fm.pat.common.patchName` | 12 B | `TEST` padded with 8 spaces (the **whole name** is sent) |
| 03 | `1F 00 03 01` | `stepPitchShifter-bal` (= mfxParameter29) | 4 B nibbled | 32780…32768 = D88:12W … D100:0W |
| 03 | `1F 00 03 05` | `stepPitchShifter-level` (= mfxParameter30) | 4 B nibbled | 32892…32880 = 124…112 |
| 04 | `02 00 00 00` | `fm.system.common.masterTune` | 4 B nibbled | 1297…1151 (447.00…443.24 Hz) |
| 04 | `02 00 40 0B` / `0C` | `fm.system.controller.beamRangeLower` / `Upper` | 1 B | 3…33 / 124…109 |

- The wire size of each message is the value's own size (1, 4 or 12 bytes). The Editor never sends a neighbouring value or a whole block for a plain value edit.
- There's no handshake and no Identity Request before edits. The Editor sends them fire-and-forget, even though nothing ever answered.
- There's **no pacing** either: messages leave as fast as the mouse moves. The gaps are 1–50 ms, the smallest is 1 ms (04, beam lower 28 → 30), and many are 6–14 ms. That is well under the 20 ms the SMF exports put between whole blocks. Whether the synth keeps up at that rate is a hardware question; over 5-pin MIDI, a 14-byte message alone takes 4.5 ms on the wire. [F; tolerance unknown]
- The System area is edited live with DT1 to `02 00 …`, the same way as the patch. The Editor manual ([D] p.9) says system settings are kept only after a "System Write", so these DT1s are probably volatile too [I].

### 2. The `00 81` / `00 85` question is settled [F]

Script.xml gives `stepPitchShifter-bal`/`-level` the illegal addresses `00 81`/`00 85`. The Editor transmits **`1F 00 03 01`** and **`1F 00 03 05`**, which is MFX base `00 02 00` + `01 01`/`01 05`. So the Koa engine does resolve the script's addresses base-128, exactly as `extract_script_schema.py` does, and it agrees with the official doc (MFX Parameter 29/30). The anomaly is harmless: our addresses equal the Editor's.

### 3. Changing an effect type sends the whole effect block, filled with that type's Script.xml defaults [F]

When the MFX type was set to 63 (STEP PITCH SHIFTER):
1. One DT1 to `1F 00 02 00` carrying the **complete 145-byte MFX block**. mfxType = 63, and every STEP PITCH SHIFTER member (step01–16, rate, attack, gate, fine, delay, feedback, EQ, balance, level) equals **its Script.xml `<default>`**. The two unused slots 31/32 and the common MFX fields are at their defaults too; they were at INIT values beforehand, so we can't tell "reset" from "kept" for those.
2. 52 ms later, one DT1 with just the mfxType byte again.

The test builds the block from the schema alone (generic defaults, overlaid with the type-63 members' defaults) and it equals the captured message byte for byte.

**Consequence for sound design:** when a generated patch changes an effect type, the right starting values for that type's members are the Script.xml defaults, and the whole block should be sent. We already have those defaults in `parameters.json`. This probably applies to chorus/reverb type changes too, but only MFX was captured [I].

### 4. READ, SYNC and the Librarian begin with a Universal Identity Request [F]

- **Message:** `F0 7E 10 06 01 F7`, sent to **device ID `10`**, not the broadcast `7F`. The MIDI Implementation ([D] p.3) allows both.
- **Timeout and retries:** no reply within **~3.0 s** (2,987–2,999 ms) → one retry → the dialog "Unable to read/write data." (string at `A8EE.exe` 0x0F83F0, Editor manual §6). Nothing else is sent after that.
- **Where it applies:** READ, SYNC, the WRITE step after choosing a slot, and the Librarian's Read Selected all behave this way.
- **Expected reply** ([D] p.6): `F0 7E 10 06 02 41 3C 02 00 00 00 01 00 00 F7`. What the Editor checks in the reply is unknown.

`sysex.identity_request()` reproduces the request.

### 5. WRITE first reads the target slot's name with a plain RQ1 on the User area [F]

Pressing WRITE produced two RQ1s, 3.0 s apart: `F0 41 10 00 00 3C 11 30 00 00 00 00 00 00 0C 44 F7`. That is **User Patch 0 (Librarian 1-1), 12 bytes from offset 0 = `patchName`**. So:
- The Editor reads User-slot names by **RQ1 directly on `30 nn 00 00`**, the documented User Patch area. This **replaces the earlier inference** that names are read through `cm` `…Information` addresses at `0F …` (script-analysis.md §2), at least for the WRITE dialog. It is probably a list: slots 0, 1, 2 … would follow if the synth answered [I].
- RQ1 on the User area is something Roland's own software does. Reading any User patch by RQ1 is therefore a legitimate, read-only operation for our own tools later (whole blocks or names).
- After the name read failed, two Identity Requests followed, 4.9 s later. Most likely the user confirmed the dialog and the Editor checked the connection before writing [I]. **No DT1 and no `0F 00 10 0x` write command was sent**, because the sequence stopped at the unanswered identity check. The write handshake is therefore still unknown.

## What this settles and what it doesn't

| Question (REPORT.md "remains unknown") | Status |
|---|---|
| What the Editor sends for `00 81`/`00 85` | **Settled:** `01 01`/`01 05` (base-128) |
| What single-parameter edits look like | **Settled:** one DT1 per value, own size, unpaced, no handshake |
| How patch-name lists are read | **Largely settled:** plain RQ1 of `patchName` on `30 nn 00 00` (only slot 0 was observed) |
| Effect type change | **New:** whole block with per-type Script.xml defaults |
| READ/SYNC RQ1 sequence, reply packetization, write handshake (`0F 00 10 0x`) | **Still open.** Gated behind the Identity Reply, so it needs the synth |
| Minimum DT1 spacing the synth tolerates | **Still open.** The Editor itself sends at up to ~1 ms gaps |

## Consequences

1. **A loopback without a synth has given everything it can.** Every further step waits on the Identity Reply. (Faking the reply by hand in MIDI-OX within 3 s would only move the timeout to the first RQ1.)
2. **Next captures should be made with the synth attached, with MIDI-OX in the middle** (Editor → loopMIDI → MIDI-OX → synth, and back). Then the same log shows both directions, and the `IN PORT` column, which `midiox_log.py` prints, tells them apart. This observes the identity exchange, the READ RQ1s, the synth's reply packetization and the Librarian's Read All without extra risk. See NEXT-STEPS step 3.
3. **For the planned GUI and live editing:** Roland's own live-edit protocol is exactly what our library already produces: one small DT1 per changed value to `1F …`. The one thing left to check on hardware is whether the synth keeps up with that rate.
