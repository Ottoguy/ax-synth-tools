# First conversation with the synth: MIDI-OX in the middle + backup

**Sources:**
- `captures/mitm/01-03*.txt`: MIDI-OX Monitor logs, both directions, 2026-09-26. IN PORT 1 = Editor/Librarian → synth; IN PORT 3 = synth → software.
- `captures/backup/ax-synth-backup-2026-09-26.mid`: Librarian Read All → Export SMF.
- Hardware: the user's second-hand AX-Synth, **firmware 2.01**, USB, generic driver (`captures/setup.md`).

**Tools:**
- `research/tools/midiox_log.py`: per-message decode.
- `research/tools/backup_summary.py`: writes `research/generated/user-patches.{csv,json}`.
- `research/tools/describe_a8.py FILE.mid#N other.a8e`: diffs a backup slot against a patch file.
- `sysex.patch_blocks()`: collects whole-block DT1s into patches.

**Tests:** `SynthConversation`, `SynthBackup` in `tests/test_schema.py`.

All labels are **[F]** (captured bytes) unless marked.

## Summary

1. **The synth answers the Identity Request exactly as documented.** The reply is `F0 7E 10 06 02 41 3C 02 00 00 00 01 00 00 F7`, including software revision `00 01 00 00`, despite firmware 2.01. Editor/Librarian v1.00 accept it, and every read in this session worked.
2. **RQ1 → one DT1 of exactly the requested block.** The reply carries the same address and size, arrives 2–47 ms later, and is not packetized (every block is ≤154 bytes, below the doc's 256-byte packet limit). This settles the reply format for all 9 patch blocks and for Setup/System.
3. **The Librarian reads a patch block by block.** Read Selected: an Identity exchange, then an RQ1 of 2 bytes at `01 00 00 04` (Setup bank MSB/LSB), then 9 RQ1s on `30 00 00 00 + block` in `PATCH_BLOCKS` order with the Script.xml block sizes. The patch read back is byte-identical to the same slot in the backup.
4. **The Editor's READ reads Setup, System and the Temporary patch.** In order:
   - an Identity exchange
   - Setup bank MSB, then LSB (1 byte each)
   - the whole Setup (0x34)
   - System Common (0x1E)
   - System Controller (**0x4F**, the Editor's own size, so this doesn't settle the 0x4F/0x50 question)
   - the 9 Temporary blocks

   It reads **no name list** and nothing on `0F …`.
5. **SYNC writes, with no reads.** After the Identity exchange it sends 12 whole-block DT1s: Setup, System Common, System Controller, then the 9 Temporary blocks. They are paced 21–60 ms apart. The payloads are byte-identical to what READ received just before. The Editor manual p.8 says SYNC also reads "the name lists". That didn't happen here, and no RQ1 was sent at all.
   - ⚠ **Consequence: SYNC overwrites the synth's Setup and System settings** (master tune, MIDI channel, velocity curve, D-Beam assignment…) with the Editor's values, not just the volatile Temporary patch. Whether System DT1s persist across power-off is unknown [I: probably not until a System Write, Editor manual p.9].
6. **The data READ returned was the Editor's blank document.** Setup, System Common, System Controller and all 9 Temporary blocks are byte-identical to `InitialData.a8e`, including the patch name "INIT PATCH". The Setup even says the selected Tone is 87/0/PC 1 (AX Saw Lead), yet the Temporary patch isn't AX Saw Lead. Per the Editor manual p.11, the Temporary area holds the patch selected on the panel. So before capture 02, something had sent the Editor's blank document (Setup + System + INIT patch) to the synth **[I]**. The most likely candidate is a SYNC, or an automatic send when the Editor connected during the step 3.0 test; it was not captured. The User patches are unaffected (item 7), and the Temporary patch is restored by selecting a Tone on the panel. The **System settings may now be Editor defaults**:
   - MIDI channel 1
   - velocity REAL
   - D-Beam ASSIGNABLE = CC01, range 0–127
   - master tune 440.0 Hz
   - hold polarity standard

   These may differ from what the previous owner had set.
7. **Backup: 256 complete patches, and the factory mapping is confirmed.** There are 2,304 DT1s with the same layout and pacing as Roland's Librarian export (`dumps/`), and `sysex.patch_messages()` reproduces them byte for byte.
   - 254 of 256 stored names equal the Owner's Manual Tone list at User patch *n* = LSB·128 + PC − 1 (Librarian slot *f*-*v*). The earlier strong inference is now **confirmed**.
   - The two exceptions: 3-10/3-11, printed "Reso Bs 2"/"Reso Bs 3", are stored as "Reso Bs 1"/"Reso Bs 2". They are distinct sounds from 3-1 "Reso Bs 1". It's unknown whether this is a factory naming quirk or an edit by a previous owner.
8. **Wave numbering confirmed: wave *N* = `internalWaveNameTableA[N−1]`.** Across all 256 patches the waves fit the sound names:

   | Patch | Waves |
   |---|---|
   | Soprano Sax | 285–287 "Sop Sax 2 p/mf/f" |
   | Folk Gtr 1 | 52–54 "Ac.Gtr mp/mf/ff" |
   | Steel Drums | 147 "Steel Drums" |
   | Sitar | 64 "Sitar" + 65 "Sitar Drone" |
   | Blend Piano | 254/256 "AX Grand mpL/ffL" |
   | VK Organ 1 | 261 "VK Jazz Org1" |
   | SearingGtr 1 | 61 "Overdrive Gt" |
9. **The forum patches are factory SearingGtr 1 plus exactly the edits their author described** (`describe_a8.py backup.mid#96 patches/guitar01.a8e`). Changes from the factory original:
   - bend 2/12 → 12/24 ("2 octaves down, 1 up")
   - matrix control 3 source CC04 → **CC70**, routed to cutoff and TVA attack time ("feedback")
   - a new Tone 4, a +12 sine at velocity ≤69 ("extra high pure tone on soft notes")
   - Tone 2, a **factory** +7 sine layer, retuned to +24
   - mono/poly and portamento settings changed
   - FXM on Tone 3
   - longer TVA envelope times

   `guitar.a8e` differs mostly in Tone 2 (the "muted chug": resonance, fast decay, random pitch) and a louder reverb. This turns the earlier [3P] ground truth into exact, verified parameter diffs.
10. **`patchCategory` numbering.** 27 distinct values, grouped by instrument:

    | Value | Patches (examples) | Probable Roland label [3P/I] |
    |---|---|---|
    | 1 | AX Grand, Honky Tonk | AC.PIANO |
    | 2 | Stage EP, Wurly EP, FM EP 1 | EL.PIANO |
    | 3 | AX Clav 1, Harpsichord | KEYBOARDS |
    | 4 | D-50 Fantsia, FM Sparkles | BELL |
    | 5 | AX Vibe, Marimba, Steel Drums | MALLET |
    | 6 | Lord Organ 1, VK Organ 1 | ORGAN |
    | 7 | Musette | ACCORDION |
    | 8 | Harmonica | HARMONICA |
    | 9 | Nylon Gtr, Folk Gtr | AC.GUITAR |
    | 10 | Jazz EGtr, Clean EGtr | EL.GUITAR |
    | 11 | SearingGtr 1–4, AX DistGt | DIST.GUITAR |
    | 12 | Acoustic Bs, Finger EBs | BASS |
    | 13 | Reso Bs, Moogue Bs | SYNTH BASS |
    | 14 | AX Strings, Tape Strings | STRINGS |
    | 19 | AX BrassSect, Sax Sect | AC.BRASS |
    | 20 | 80s Brass, Analog Brass | SYNTH BRASS |
    | 21 | Soprano/Alto/Tenor Sax | SAX |
    | 22 | AX Saw Lead, GR300 Lead | HARD LEAD |
    | 23 | JupiterLead2, Pulse Lead | SOFT LEAD |
    | 24 | Trance Synth, SuperSaw Pad | TECHNO SYNTH |
    | 25 | Xadecimal, Sliced Pad | PULSATING |
    | 27 | Poly Synth, Super Saw | OTHER SYNTH |
    | 28 | PhaserPad, Heaven Pad | BRIGHT PAD |
    | 29 | Soft Pad, JP Strings | SOFT PAD |
    | 30 | Angels Choir, Vox Pad | VOX |
    | 31 | Harp, Sitar | PLUCKED |
    | 32 | Pan Pipes, Santur Stack | ETHNIC |

    Neither Script.xml nor the executables contain category names. The labels are Roland's XV/Fantom-era category list **[3P, from memory; unverified]**, and every observed group fits it. The per-patch numbers themselves are [F].

## Timing

| Exchange | Observed |
|---|---|
| Identity Request → Reply | 1–2 ms |
| RQ1 → DT1 reply | 2–47 ms (longer for 83–154-byte blocks) |
| Software's next RQ1 after a reply | 6–37 ms |
| SYNC DT1 spacing (whole blocks) | 21–60 ms |

The synth kept up with Roland's own pacing. The minimum DT1 spacing the synth tolerates is still untested; step 4 uses ≥25 ms.

## Settled / still open

| Question | Status |
|---|---|
| Does firmware 2.01 answer the Identity Request, and does Editor v1.00 accept it? | **Settled:** identical to the doc, accepted |
| RQ1 reply format and packetization | **Settled** for all blocks ≤154 B: one DT1, same address, exact size |
| Tone ↔ User patch mapping | **Settled:** 254/256 names; the 2 exceptions are named above |
| Wave numbering *N* ↔ `[N−1]` | **Settled** |
| `patchCategory` numbering | Numbers settled [F]; names [3P/I] |
| What READ / SYNC / Read Selected send | **Settled** (items 3–5) |
| Why the synth held the Editor's INIT document | Temporary follows the panel (bulkdump-analysis.md, step 3.3), so INIT had been sent before capture 02 [I] |
| SystemController size 0x4F vs 0x50 | **Settled:** 0x50 (step 3.3, bulkdump-analysis.md) |
| The WRITE handshake (`0F 00 10 0x`) | Open (WRITE is still off-limits) |
| Whether DT1s to `02 …` (System) persist after power-off | Open |
| Reso Bs 2/3 stored names | Open (factory quirk or previous owner) |
| FAVORITE / driver-mode / sleep storage | FAVORITE found in the Bulk Dump; driver mode and sleep still open (bulkdump-analysis.md) |
