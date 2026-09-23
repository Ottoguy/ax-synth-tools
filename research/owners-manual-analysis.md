# Owner's Manual: findings

**Source:** `docs/AX-Synth_OM.pdf`: "AX-Synth Owner's Manual", Roland Europe ©2009, doc no. 602.00.0354.02 RES 750-09, file `AX-Synth_e2` (12 Oct 2009), 44 pages. Text: `generated/owners-manual.pdf.txt` (all pages read). Page references are the printed page numbers. `docs/AX-Synth_Erratum2.pdf` corrects p.27 (the VOLUME knob sends no CC07).

The manual is about *playing* and *setting up* the instrument. It contains **no sound-parameter explanations** and **no wave list**: TVF, TVA, MFX and so on are "edited using the AX-Synth Editor". The explanations of what each parameter does to the sound are in the **Editor manual** we already have (`generated/editor-manual.pdf.txt`): the parameter guide on **p.9–43** (System, Effects, Patch: WG/TVF/TVA/LFO/TMT/Matrix Control) and the **Effects List on p.44–78** (every MFX/Chorus/Reverb type and its parameters). Together with the factory Tone list below, that is the knowledge base for the LLM; it is now extracted into `knowledge/` (see `knowledge/README.md`). The only wave-name source remains Script.xml's `internalWaveNameTableA` (313 names).

## 1. Factory Tone list (p.37–38): the most valuable part

Extracted by `tools/extract_tone_list.py` → [`generated/factory-tones.json` / `.csv`](generated/factory-tones.csv), accessed via `src/axsynth/factory.py`.

| Group | Count | Bank CC00/CC32 | PC | Editable |
|---|---|---|---|---|
| SuperNATURAL: Violin, Cello, Shakuhachi, Trombone | 4 | 66 / 0 | 1–4 | no (not in patch area; no volume/reverb edit either, p.26) |
| SPECIAL: Trumpet, Sax, Strings, Jazz Scat | 4 | 87 / 64 | 1–4 | no |
| Synth Lead 1 · Synth Lead 2 · Bass · Lead Guitar | 4 × 32 | 87 / 0 | 1–128 | yes |
| Brass/Poly Synth · Strings/Pad · Organ/Clavi · Choir/Piano | 4 × 32 | 87 / 1 | 1–128 | yes |

Consistent with the MIDI Implementation's Setup notes ("66: SuperNATURAL, 87: Regular/Special; LSB 0–1 Regular, 64 Special") and the Setup default bank MSB 87.

**Tones = the 256 User patches [I, strong].** p.9/p.18/p.39: "256 Tones (8 families × 32)". Librarian manual: the Patch Area holds "256 patches … Bank (1–8) × Number (1–32)". Factory reset (p.34) restores "all parameters", including sounds edited with the Editor. So the factory Tones live in the rewritable Patch Area (`30 00 00 00` + n × `00 01 00 00`), with **n = LSB × 128 + PC − 1** and **family = n ÷ 32**. Checks so far:
- The regular Tones' indices come out contiguous 0–255, and family ↔ n÷32 holds for all 256.
- The forum patches are named `SearingGtr 1` and their Setup stores bank 87/0, program 96 (0-based). The manual lists **SearingGtr 1 = Lead Guitar #1 = 87/0/PC 97**, which maps to slot 4-1, address `30 60 00 00` (test `OwnersManual`).
- Still to confirm: a Librarian "Read All Data" should show exactly these names in this order.

**Names are catalogue names, not always the stored bytes.** "Vintage Org 1/2" are 13 characters as printed, but `patchName` holds 12, so lookups ignore spaces, dots and case (`factory.by_name`).

**Why it matters for the goal:** the names are descriptive ("80s Brass 1", "Shimmer Pad", "TB Dist Bs", "JD-800 Piano"), grouped by family, and each is a professionally designed starting point. An LLM that edits the nearest factory Tone will do far better than one building from INIT.

## 2. The instrument's user interface constrains our workflow

- **Display: 3 × 7-segment LED** (p.10, p.39). The synth **cannot show patch names, wave names or parameter values**, only Tone numbers (1–32) and 3-letter codes. All verification of names and values must go through the Editor (READ) or a SysEx dump.
- **On-board editing is limited to Volume ("UOl") and Reverb Send ("reU")** of regular Tones, and those are saved **only into FAVORITE memories**, not into the Tone (p.26). Everything else is "edited using the AX-Synth Editor". The panel [WRITE] button stores favorites and system settings, not patches (p.10). **Patches are stored only via Editor/Librarian SysEx.**
- **FAVORITE**: 2 banks × 8 memories = Tone assignment + Volume + Reverb Send (p.19, p.39). Not in the documented address map, so it is stored somewhere undocumented (a Bulk Dump should contain it).
- **Monotimbral, 128 voices**, not GS/GM2 (p.16, p.35).
- **Receive channel = transmit channel** (p.15, p.27), set with [SHIFT]+[TX ON]+key. That's `system.common.kbdPatchRxTxChannel`. No Device ID setting is mentioned anywhere, so we assume the fixed `10H` from the MIDI Implementation.

## 3. Maintenance functions (power-on key combinations)

| Function | How (p.) | Relevance |
|---|---|---|
| **Bulk Dump send/receive** | Hold VARIATION [−]+[+]+TONE [6] at power-on → "dMP". FAVORITE [B] = send ("Snd"… "dNE"); [A] = receive ("RCU" → "Urt" → "dne"; "Err" on failure). **About 16 minutes.** (p.29–30) | "Transmits all of the AX-Synth's settings", made by the **synth itself**, with no Librarian involved. It's a backup, and a capture of the synth's own DT1 format (packet size, pacing, and undocumented areas such as FAVORITE/system). 16 min for ≈ 270 kB of patch data implies very slow pacing, or much more data than the patches alone **[I]** |
| **Factory reset** | VARIATION [+]+[−]+TONE [7] at power-on → "FCt", then [WRITE] (p.34) | **Recovery path**: restores all 256 factory Tones. It also erases your own edits |
| **Firmware version** | VARIATION [+]+[−]+TONE [8] at power-on (p.34) | Answers a Step 0 question |
| **USB driver mode** | [SHIFT]+PGM CHANGE [INC]: "Gen" (OS generic) / "Uen" (Roland driver) + [WRITE], then power-cycle (p.32) | A system setting not in the documented map (candidate: a SystemController reserved byte **[I]**) |
| **Sleep interval** | [SHIFT]+PGM CHANGE [DEC]: Off/15/30/60 min (p.34) | Same |

## 4. Confirmations of the data model

| Manual | Model | Status |
|---|---|---|
| Transpose −5…+6 (p.21) | Setup `transposeValue` 59–70 (64 = 0) | ✅ |
| Octave shift ±3 (p.22) | Setup `octaveShift` 61–67 | ✅ |
| Master Tune 415.3–466.2 Hz, default 440 (p.21) | `masterTune` 24–2024 (default 1024); `masterTuneTable` 415.30…466.20 | ✅ exact |
| OCTAVE/VARIATION button mode "OCS/OCH/Var" (p.18, 22) | SystemController `neckSwitchSelect` 0–2; doc: OCTAVE SWITCH, OCTAVE HOLD, VARIATION | ✅ (order from doc) |
| D-Beam ASSIGNABLE "C01~C95 (C32 is not available)", remembered after power-off (p.24) | `beamAssign` 0–93, beam table without CC32 | ✅ (also Erratum) |
| **SuperNATURAL Portamento mode "Hld"/"SUt"**, remembered after power-off (p.24) | Doc: SystemController `00 4F` "Portament Mode: SWITCH, HOLD", total size `50`. **Script: size `4F`, no such value** | ⚠ Resolves the discrepancy in favour of the doc: the parameter exists on the hardware. The Editor probably omits it because it only affects SuperNATURAL Tones **[I]**. An RQ1 of size 0x50 should return 80 bytes |
| Patch/pitch bend range is only changeable in the Editor (p.35) | `pitchBendRangeUp/Down` in PatchCommon | ✅ |
| "Notes cut off above 128 voices" | 4 Tones per patch: polyphony drops with layered patches **[I]** | design note |

## 5. Performance controls (what a patch should respond to)

From p.10–11, p.22–25, p.27 and the MIDI Implementation Chart (p.40):

| Control | Sends / does | Patch-side hook |
|---|---|---|
| MODULATION BAR | CC01 (vibrato "in most cases") | Matrix Control source CC01, or LFO depth via matrix |
| TOUCH CONTROLLER ribbon | Pitch Bend; BENDER MODE Normal / "Catch + Last" (not for SuperNATURAL) | `pitchBendRangeUp/Down` |
| AFTER TOUCH knob | Channel aftertouch (**the keys send none**) | Matrix/MFX control source `AFT` (the forum patch drives its amp sim with it) |
| D-Beam PITCH / FILTER / ASSIGNABLE | Pitch / cutoff ("brightness") / CC01–95 (no 32) | Matrix source = the assigned CC, e.g. CC70 in the forum patch |
| PORTAMENTO button | On/off (CC65) | `portamentoSwitch/Time/Mode/Type` |
| HOLD button, FOOT PEDAL | CC64 (the pedal always acts as Hold; no expression pedal) | `toneReceiveHold-1` |
| Keyboard | 49 keys, velocity only | Velocity → TVA/TVF sens, TMT velocity layers |

The **MIDI Implementation Chart (March 2009, v1.00)** lists as recognized: CC 0/32, 1, 5, 6/38, 7, 10, 11, a breath/foot controller (the PDF extraction garbled the number), 64, 65, 66, **71 (resonance), 72 (release), 73 (attack), 74 (cutoff), 75 (decay)**, 84, **91 (reverb)**, **93 (chorus)**, and RPN. The MIDI Implementation text (Jan 2010) additionally documents **CC76–78 (vibrato rate/depth/delay)** as received. These are *relative* offsets on the current sound (MIDI Impl.: 40H = no change).

## 6. Implications for the goal (AI → preset, simple GUI)

1. **The starting-point catalogue exists**: 256 named, family-grouped factory Tones → "pick the nearest factory Tone, then edit" becomes the core LLM strategy.
2. **Two levels of control for the GUI [I]:**
   - *Live audition without SysEx:* CC71–75 (+ 76–78, 91, 93) change resonance, release, attack, cutoff, decay, vibrato, reverb and chorus instantly on the current sound. They don't persist in the patch.
   - *Persistent edits:* the patch's own macro-like parameters in Patch Common: `cutoffOffset`, `resonanceOffset`, `attackTimeOffset`, `releaseTimeOffset`, `velocitySensOffset` (1–127, 64 = 0, applied to all Tones). They are natural targets for the GUI's big knobs.
3. **Design for the AX-Synth's real controllers**: mod bar, aftertouch *knob*, ribbon, D-Beam (and its CC), portamento and hold. There's no poly-aftertouch keybed and no expression pedal.
4. **No on-device feedback**: the GUI/LLM loop must show names and values itself; the synth only makes sound.

## 7. Terminology (to avoid confusion)

| Owner's Manual | MIDI Impl. / Editor / our code |
|---|---|
| Tone (a whole sound), Tone family, variation 1–32 | Patch (`fm.pat`), Patch Area slot, Librarian bank-number |
| — | Tone 1–4 = the four layers *inside* a patch (`fm.pat.tone[0..3]`) |
| FAVORITE memory | (undocumented) |
| Bulk Dump | DT1 stream from the synth |
