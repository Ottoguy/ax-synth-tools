# The synth's own Bulk Dump: a memory image, decoded

**Sources:**
- `captures/bulkdump/bulkdump-2026-09-26.syx`: NEXT-STEPS 3.2, the user's synth with firmware 2.01.
- `captures/rq1/`: 3.3.
- Ground truth: the Librarian backup `captures/backup/ax-synth-backup-2026-09-26.mid`.

**Tool:** `research/tools/bulkdump.py` (`info`, `solve`, `verify`, `export`).
- Derived layout: `research/generated/bulkdump-layout.json`.
- Request file for 3.5: `research/generated/experiment-rq1-setup-system.syx`.

**Tests:** `SynthBulkDump`, `SynthRequests`.

Labels: **[F]** captured bytes; **[D]** Roland docs; **[I]** inference.

## Summary

1. **The Bulk Dump isn't a patch transfer. It's a raw image of the synth's user memory [F].** 16,230 SysEx messages, all with valid checksums:
   - `F0 41 dev 7F 12 a a a a <data> sum F7`: a DT1 with a **1-byte model ID `7F`**, not the AX-Synth's `00 00 3C`.
   - The address is a byte offset in base-128. The checksum is Roland's, over address + data.
   - Data is **7-in-8 packed**: every 8 bytes on the wire are 1 byte of high bits (bit *j* → data byte *j*) plus 7 low-7-bit bytes.
   - The first message (device `11`) is a header holding the image length `0x1A0040` = 1,704,000.
   - Then come 16,228 messages of 120 data bytes each (= 105 image bytes, addresses in steps of 105), and a text trailer `Roland RE409DUMP VER.1.00-BLD.00009 0101 12 00 00`.
   - The file also contains 2,784 zero bytes in 56 runs *between* messages (MIDI-OX buffer padding; ignored).
2. **Image map [F]:**

   | Image offset | Size | Content |
   |---|---|---|
   | `0x000000` | 0x47A | **System area**: `00 1A 00 10` + signature `Roland 9S409D` + 3 bytes, bit-packed system data, signature again at `0x46A` |
   | `0x000480`–`0x01FFFF` | | erased (FF) |
   | `0x020000` | 0x14 | `FF FF FF FF` + signature |
   | `0x020014` | 80 | **16 FAVORITE memories** (item 4) |
   | `0x020064` | 256 × 664 | **256 User patches**, bit-packed (item 3) |
   | `0x049864` | 16 | signature |
   | rest | ~1.3 MB | erased flash (FF), then the trailer |

   So only about 190 KB of the 1.7 MB is data. There's no firmware in it. "9S409D"/"RE409" are Roland-internal identifiers; they're probably the board or system name [I].
3. **Patch record = every data-model value, bit-packed in Script.xml order, at the smallest width for its range [F, derived].**
   - A record is 664 bytes = 5,312 bits. The patch name comes first, as twelve 7-bit ASCII characters (this is how the names were found).
   - Then come Common, MFX, Chorus, Reverb, TMT and Tone 1–4 fields, each MSB-first. Tone 1–4 repeat with a stride of 792 bits.
   - Encoding rules:
     - Unsigned values are stored as-is.
     - Values centred on 64 use offset binary (v − (64 − 2^(w−1))); e.g. Octave Shift is 3 bits, 64 → 4.
     - Waves use 16-bit fields, and a few 8-bit fields have a zero high bit.
     - Effect parameters are stored as their 16-bit generic slots (union members aren't stored separately).
   - `bulkdump.py solve` derives each field's position and width from the backup: 256 patches, with Tone fields solved jointly over 4 × 256 samples. 690 of 783 fields are **verified by varying values**. The other 93 are constant in every factory patch, so their place follows only from the order.
   - **All 256 × 9 DT1 blocks rebuilt from the dump are byte-identical to the Librarian backup [F].** This proves three things:
     - the Librarian's Read All returns exactly what the synth stores
     - the Script.xml model covers every stored patch byte
     - all bytes between values in the DT1 blocks are zero
   - After Tone 4, **146 bits per record are outside the data model.** They're identical in 255 records. In User patch 0 (1-1 "AX Saw Lead") they look like a reset/default pattern. Hypothesis [I]: they're hidden per-patch data that a SysEx write doesn't set, and 1-1 was rewritten over MIDI once (e.g. by a previous owner). This fits the user's "may have been overwritten, but not much". It's harmless for the Temporary patch.
4. **FAVORITE memories [F positions; I for which field is volume].** 16 entries × 40 bits: bank MSB (8 bits), LSB (7), PC (7), then two 7-bit values (volume and Reverb Send, in the Owner's Manual p.26 order), then 4 zero bits.

   | Memory | Tone | Vol / Rev |
   |---|---|---|
   | A1–A8 | GR300 Lead 1, Saw Lead 1, Hot Coffee, Air Lead, Modular Bs1, SearingGtr 3, MS1959 II, Funk EGtr | 100 / 100 |
   | B1–B8 | Wide SynBrs, Harmonica (vol 115), Cosmic Rays, Bustranza, AX Dist Org1, Phase Clavi, Phase Stage (115), Wurly EP (115) | 100 / 100 |

   There are two per family, which looks like Roland's factory selection [I]. A quick check: FAVORITE [A] + TONE 1 should play GR300 Lead 1 (Synth Lead 1, variation 3).
5. **System area [F partly].** System Common sits at bit 101 after offset `0x14`, packed the same way:
   - master tune 1024 (11 bits), key shift (6 bits, offset), level 127, scale-tune switch 1
   - a 15-bit gap: the three undocumented bytes `07–09` + MIDI channel (4 bits) + byte `0B`
   - 12 scale tunes of 64

   These equal what the synth returned to READ and RQ1. The rest of the ~1.1 KB area (System Controller, Setup, and likely the sleep interval and USB driver mode) isn't mapped: with a single sample the positions of constant values are ambiguous. A before/after diff would pin them down (NEXT-STEPS 3.5).
6. **The stored system settings are the Editor's defaults** (440 Hz, channel 1, velocity REAL, D-Beam CC01 0–127…). The System Controller reply after power-cycling (3.3, after the bulk dump) is still byte-identical to `InitialData.a8e` plus `00 4F` = 1. So either the synth's factory settings equal the Editor's defaults, or the earlier SYNC's System DT1s were stored permanently. The data can't tell these apart [I]. Either way, the user's System settings are now standard defaults.

## Step 3.3 results (read-only requests, `captures/rq1/`)

- **Our own request file works on the hardware.** 10 RQ1s → 10 DT1s, each with the same address and exactly the requested size, all checksums valid.
- **System Controller is 0x50 bytes on the hardware** (the doc's size). The Editor's Script.xml uses 0x4F. Byte `00 4F` = 1 is the doc's "Portament Mode" (Owner's Manual: SuperNATURAL Hld/SUt). The script model isn't changed (rule: generated from Roland sources); the discrepancy is documented and tested.
- **The Temporary patch follows the panel selection.** With LEAD GUITAR 1 selected, it's byte-identical to User patch 96 (SearingGtr 1). This also resolves the earlier "Temporary = INIT" oddity: that state came from something sent before capture 02 (most likely a SYNC during setup), not from how the synth works. NEXT-STEPS 3.1b is no longer needed.
- **The panel volume edit ("UOl") changes neither the Temporary patch nor the System Controller.** The two replies are byte-identical. Per the Owner's Manual p.26, "UOl"/"reU" are the volume and Reverb Send of a **FAVORITE memory**, stored with [WRITE] + FAVORITE. The earlier prediction (PatchCommon `patchLevel`) is **refuted**. Where the unsaved live value sits (Setup?) is untested (3.5).

## What this means for the project

- **Data model: complete for patches.** Every byte the synth stores for a patch is accounted for by Script.xml, except 146 hidden bits per record that SysEx can't reach. There's no hidden parameter we'd need for sound design.
- **Two independent backups** exist (Librarian `.mid`, Bulk Dump `.syx`), and they agree byte for byte. `bulkdump.py export` can turn a bulk dump into a Librarian-style DT1 stream, so any future bulk dump can serve as a backup or corpus too.
- **Reading from the synth is fully solved** (RQ1 → exact-size DT1, ≤154 B, 2–47 ms). **Writing to the Temporary patch is the next and last protocol step.** Roland's SYNC already wrote 12 whole-block DT1s (21–60 ms apart), and the synth accepted and later returned them, so our Temporary-only write (NEXT-STEPS 4) uses the same mechanism.
- **FAVORITE memories are outside the Editor's reach.** They're set only on the panel (or by Bulk Dump receive). An app can't set FAVORITE volume/reverb over normal SysEx [I]. For the GUI, the patch's own `patchLevel` and reverb level are the controls to use.

## Open

| Question | How to settle |
|---|---|
| Where the live (unsaved) FAVORITE volume/reverb send and the sleep interval / USB driver mode are stored | 3.5: RQ1 Setup/System before and after a panel change (read-only) |
| System Controller / Setup layout inside the bulk-dump system area | A second bulk dump after one known panel change (optional; 16 min) |
| Meaning of the 146 hidden bits per patch record, and why 1-1 differs | Not needed for the goal; could compare after the first *write* to a User slot (not planned) |
| Which of the two FAVORITE 7-bit values is volume | Panel check: FAVORITE B2 (Harmonica, 115) sounds louder than B1 at the same playing [I] |
