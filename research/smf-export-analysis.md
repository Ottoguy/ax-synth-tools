# "Export SMF" captures (dumps/)

Produced 2026-09-23 by clicking **File → Export SMF** in each application, with **no AX-Synth connected**. The apps export their own in-memory data (the INIT patch), so this needs no hardware. Inspector: [`tools/smf_inspect.py`](tools/smf_inspect.py). Tests: `tests/test_schema.py::RolandSmfExports`.

| File | Size | Contents |
|---|---|---|
| `dumps/AX-Synth Editor clean export.mid` | 1,214 | SMF format 0, 1 track, 96 PPQ, **9 DT1** messages + End of Track |
| `dumps/AX-Synth Librarian Clean export.mid` | 304,154 | SMF format 0, 1 track, 96 PPQ, **2,304 DT1** (256 patches × 9) + End of Track |

No tempo, channel, RQ1 or `0F …` (CommunicationModel) messages. Setup and System are not exported, only patches. **[F]**

## What the messages are [F]

Every message is `F0 41 10 00 00 3C 12 <addr ×4> <data> <sum> F7`: Roland, device ID **10H**, model `00 00 3C`, **DT1**. All 2,313 checksums are valid.

**One DT1 per Patch block, carrying the whole struct image, always in this order:**

| # | Block | Offset | Data bytes | SMF delay after (ticks) |
|---|---|---|---|---|
| 1 | Common | `00 00 00` | 79 | 10 |
| 2 | MFX | `00 02 00` | 145 | 14 |
| 3 | Chorus | `00 04 00` | 84 | 10 |
| 4 | Reverb | `00 06 00` | 83 | 10 |
| 5 | TMT | `00 10 00` | 41 | 8 |
| 6–9 | Tone 1–4 | `00 20 00` … `00 26 00` | 154 each | 15 |

- **Editor** → base `1F 00 00 00` = **Temporary Patch**.
- **Librarian** → base `30 00 00 00 + n × 00 01 00 00` for n = 0…255, i.e. `30 00 00 00` … `31 7F 00 00` = **User Patch 001–256**, matching the official Parameter Address Map exactly.

## What this settles

1. **File blocks = DT1 payloads (confirmed).** All 2,313 payloads are byte-identical to the INIT PATCH blocks in `InitialData.a8e` / `.a8l`. The model → bytes → SysEx chain is shown end to end by Roland's own software, not just inferred.
2. **Our encoder matches Roland's.** `axsynth.sysex.patch_messages()` fed with the `.a8e` blocks reproduces the Editor export byte-for-byte, and with `user_patch_address(n)` the Librarian's.
3. **Block DT1s are longer than 128 bytes and cross 7-bit address boundaries.** The MFX DT1 starts at `1F 00 02 00` and carries 145 bytes, so it runs past `…02 7F` into `…03 xx`. Roland's software treats the address space as contiguous base-128, as our model does. Nothing is split into ≤128-byte packets, and nothing reaches the doc's 256-byte packet limit.
4. **The two invalid addresses (`00 81`/`00 85`) don't matter for whole-patch transfers.** Blocks are sent as images, so individual parameter addresses play no part. They only matter for single-parameter DT1s (live knob edits).
5. **Writing a User patch via SMF uses plain DT1 to `30 nn xx 00`.** No `0F 00 10 00` write-request handshake appears in the export. The `cm.command.write*` values are therefore probably only the Editor's live "WRITE Temporary → User" operation **[I]**.
6. **The `.a8l` trailing 4 bytes are not transmitted.** They are Librarian-file-only data (memo hypothesis still open).
7. **Pacing model [F fit, I meaning].** Every gap (2,312 of 2,312) equals `ceil((message_bytes × 0.32 ms + 20 ms) / tick)`, with tick = 500 ms / 96 (default 120 BPM, since there's no tempo event). That is MIDI wire time at 31,250 baud plus the doc's "about 20 ms". Implemented as `sysex.roland_export_delay_ticks()`.

## Still open

- Whether the hardware **accepts** these streams: timing tolerance, and whether User-area DT1s commit to flash immediately. (The 3-character display won't show names; check by Editor READ or an RQ1 dump.)
- System Controller size (`4F` vs `50`): Setup/System aren't exported.
- The single-parameter addressing the Editor uses (e.g. the `00 81` case) and the `cm` protocol. These appear only in live traffic, which can also be captured without a synth (see the REPORT's next steps).

## ⚠ Safety note for later hardware work

Playing the **Librarian** export to a real AX-Synth would, if the synth accepts DT1 to the User area, **overwrite all 256 User patches with INIT PATCH**. Never send it without a verified backup (Librarian "Read All Data", or the synth's own Bulk Dump, Owner's Manual p.29). If it happens anyway, a factory reset (p.34) restores the *factory* Tones, but not your own edits. The **Editor** export targets only the Temporary Patch, which is volatile and doesn't touch stored patches.
