# Third-party patches (patches/)

Two AX-Synth Editor files found online, with the author's forum description (quoted in the conversation of 2026-09-23; summarised below). They are the first **non-default, human-made** patch data in the project. Because the author says in plain words what they changed, they give ground truth that is **independent of Roland's files**, which lets us check our parameter *meanings* and not just their layout.

Tools: `tools/describe_a8.py` (values with labels / diff), `tools/a8_files.py`. Tests: `tests/test_schema.py::ThirdPartyPatches` (9 tests).

| File | Size | Patch name | Author's description |
|---|---|---|---|
| `patches/guitar.a8e` | 1,465 | `SearingGtr 1` | "muted chugs" emulation (play staccato); CC70 feedback does **not** work |
| `patches/guitar01.a8e` | 1,465 | `SearingGtr 1` | no chug emulation; CC70 feedback works |

Both are standard `.a8e` Koa data files (Setup + System + one Patch) and parse to the byte (1465/1465). The name is unchanged from what looks like the factory "SearingGtr 1" guitar patch.

## Author's claims vs decoded data

| Claim | Decoded | Verdict |
|---|---|---|
| "Pitch bend extended to 2 octaves down, one octave up" | `pitchBendRangeDown` = 24, `pitchBendRangeUp` = 12 (both files) | ✅ exact |
| "Velocity 1–69 plays an extra … tone" | TMT: Tone 4 on, velocity 1–**69**; Tone 3 70–118; Tone 1 119–127 | ✅ exact. Confirms TMT array index [3] = Tone 4 |
| "24+ … tone" | guitar01: Tone 2 coarse raw 88 → **+24** (offset −64); wave 220 | ✅ confirms the coarse-tune display offset |
| "Switched to mono" | `monoPoly` = 0 (doc: 0 = MONO) | ✅ |
| "Controller 70 … gives feedback" | `matrixControl3Source` = 70 → `CC70` label; routed to LEVEL (guitar) / CUTOFF (guitar01) and TVA attack time | ✅ |
| "CC70 if you choose it for your beam controller"; feedback works in guitar01 only | guitar01 System `beamAssign` = 68 → **CC70**; guitar: 69 → CC71 | ✅ (the file also saves the System block from the author's setup) |
| "Muted chugs … play staccato" (guitar only) | Only in guitar: Tone 2 is a short percussive layer (TVA T1 = 0, L2 = 0, L3 = 3, resonance 58, random pitch 20, velocity curve 7) | ✅ plausible synthesis of a muted pluck |
| "Vibrato exaggerated" | Matrix Control 1 → LFO1 RATE and higher sensitivities; both LFOs key-triggered with changed offsets | ✅ consistent (not a precise claim) |
| "A note lasts longer" | Tone TVA/TVF envelope times raised (e.g. TVA T3 = 117) | ✅ consistent |

MFX type 39 = **GUITAR AMP SIMULATOR** (EXE name list), and the active union members are `guitarAmpSimulator-*` with amp type **METAL LEAD** and speaker MS STACK 1. That confirms the MFX group ↔ type mapping on real data. Chorus = DELAY (L 350 ms / R 700 ms), Reverb = SRV PLATE.

## What this changes

1. **Meanings and labels are validated by an independent source** (previously only by Roland's own files and doc).
2. **The two CC tables use different index rules [F, now confirmed by real data].** `controlSourceTable` (matrix sources, range 0–109) keeps a `32:OFF` placeholder, so raw = CC number (raw 70 = CC70). `beamControlSourceTable` (range 0–93) has no CC32 slot, so raw 68 = CC70. The official doc's wording "CC01~CC31, CC33~CC95" hides this difference. The enum labels in our database handle both correctly. Roland's Owner's Manual erratum (`docs/AX-Synth_Erratum2.pdf`) independently states that the D Beam transmits "CC01~31, CC33~95", which matches the beam table.
3. **Wave numbers: *N* ↔ `internalWaveNameTableA[N−1]` is now well supported [I].** Tone 1 wave 61 → "Overdrive Gt" (guitar patch); Tones 2/4 wave 220 → "Sine" with the filter OFF, as a pure tone layer. The alternative *N* ↔ [N] gives "DistortionGt" and "JD Fine Wine", and the latter fits a pure +24 layer poorly. Tone 3 wave 2 → "Stage EP p" with FXM depth 16 (FXM on an EP for grit). Still to be confirmed: the synth's 3-character display can't show wave names, so confirm in the Editor (READ the patch and look at Tone 1's wave) or by listening.
4. **Script range error found.** SystemController `reserve04` = 100 in every `.a8e` we have (Roland's InitialData and both user files). The script says 0–1, and the doc says a full 7-bit byte (`0aaa aaaa`). Real data follows the doc.
5. **`.a8e` saves System and Setup too.** The author's beam assignment travels with the file, and Setup `kbdPatchProgramNumber` = 96 in both. The Setup program number most likely records the program selected on the synth when the file was saved **[I]**. When sending an `.a8e` patch to a synth, **send only the Patch blocks**, not the author's System settings.
6. **Real-data regression tests:** every active value in both files lies inside the script range (apart from item 4), and every decode is clean.

## Ready for hardware (not sent)

`research/generated/guitar-temporary.syx` and `guitar01-temporary.syx` hold each patch as 9 DT1s to the **Temporary Patch** only (`dump_experiment.py a8-to-syx`), in the same format as Roland's Editor export. Sending one is volatile and non-destructive, and it would be the first audible check of the whole chain. The synth can't display the name; the Editor's READ should show "SearingGtr 1".

**Update (Owner's Manual):** "SearingGtr 1" is factory Tone **Lead Guitar #1** (bank 87/0, PC 97), matching the stored Setup program 96 (0-based). The author tuned a factory Tone, so once the factory original is read from the synth, diffing it against these files will show exactly what the author changed. PatchCommon `patchCategory` = 11: in Roland's XV/Fantom category scheme, 11 is a distortion-guitar category **[3P/I, unverified]**; the factory corpus will show the category numbering.

## Provenance note

These files are someone else's work, shared publicly on a forum. They are kept as test fixtures; check the author's terms before redistributing them in a public repository.
