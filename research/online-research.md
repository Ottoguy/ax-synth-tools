# Online research (Task 6), searched 2026-09-23

## Exact-term searches

| Query | Result |
|---|---|
| `"int1x7" Roland` | One hit: [teemow/midi-device usbcodec](https://pkg.go.dev/github.com/teemow/midi-device/device/usbcodec) (see below) |
| `"structType" "int4x4" Roland Script.xml` | Nothing matching this schema. Related: [Roland-Zen-Decode-XML](https://github.com/DrKnackeratorStrikesAgain/Roland-Zen-Decode-XML) |
| `kbdPatchBankSelectMsb` / `mfx1Switch` / `transposeValue` AX-Synth | **No hits.** These names appear to be undocumented online |
| `InitialData.a8l`, `.a8l`, `KoaDataFile` | **No hits** |
| `"AX-Synth" SysEx editor github`, AX-Synth reverse engineering | No open-source AX-Synth editor or reverse-engineering project found; only forums and download pages ([Roland support](https://www.roland.com/global/support/by_product/ax-synth/updates_drivers/), [Softpedia](https://www.softpedia.com/get/Multimedia/Audio/Other-AUDIO-Tools/AX-Synth-Editor.shtml)) |
| AX-Synth SysEx `1F 00 00 00` / `00 00 3C` | Nothing AX-Synth-specific. An XV-5080 thread uses Temporary Patch `1F 00 00 00` ([Roland Clan](https://forums.rolandclan.com/viewtopic.php?p=338879)), showing the same address convention across the XV family |

As far as these searches show, **our reading of Script.xml and the two data formats is new**.

## Third-party evidence [3P]

1. **teemow/midi-device (Go)**: defines `int<W>x<B>` as "*splits the value into W big-endian groups of B bits, one group per wire byte (low bits)*", with `int4x4` 1220 → `00 04 0C 04` and `int2x4` 0xAB → `0A 0B`. The page says these came from "*decompiled 'BOSS TONE STUDIO' config/constant.js + utilities/converter.js*". So Roland has kept this type vocabulary from the 2009 Koa editors into its later web-based editors. This matches our reading exactly.
2. **cmatsuoka/fsex (C)**, [github](https://github.com/cmatsuoka/fsex): Fantom-S/X and Juno-G SysEx and librarian tools. `library.c` reads `.jgl/.fxl/.fsl` librarian files with a 32-byte ID, big-endian u32 patch count at offset 32, a 160-byte header, and per-patch u32 size plus length-prefixed blocks. That is **the same container as `.a8l`**. The README also notes Juno-G model ID `00 00 15` and says the Fantom/Juno address maps are shared.
3. **Roland-Zen-Decode-XML**: decodes the *later* Roland editor XML (Jupiter-X, Fantom 6/7/8, Juno-X, MC-707/101). That schema is different (`<baseblock>`, `<param>`, `<concrete>`, `<alternate>` for unions), so it is a successor framework, not the same one.
4. **MC-808 "Improved editor script"** thread ([Roland Clan](https://forums.rolandclan.com/viewtopic.php?t=30428), page timed out; search summary only): users replaced the MC-808 editor's "XML and resource files". This suggests the MC-808 editor used the same script-driven design **[unverified]**.
5. [Patch Base](https://coffeeshopped.com/patch-base/editor/roland/xv-5050) has a third-party XV-5050 editor; possibly useful as a reference for the XV-family SysEx model.

## Did Roland use a common editor framework? Yes (strong evidence)

- **[F]** `A8EE.exe` class names: `CKoaDataFile`, `CKoaMidiOutDevice`, `CKoaBufferManager`, `CKoaEntityManager`, `FKoaSendDt1`, … ("Koa" framework).
- **[F]** Control types in Script.xml carry *other products'* names: `xvToneSelectButton` (XV), `fantomXMfxSelectCombo`, `fantomXLfoControl`, `fantomXSwSlider` (Fantom-X), `juxSelectPanelButton` (Juno-? "JUX"), alongside `a8e*` (AX-Synth-specific).
- **[F]** Number tables `outputAssignXV5050Table`, `toneOutputAssignXV5050Table`.
- **[F]** The `CommunicationModel` includes performances, rhythm sets, samples, and phrase preview, none of which the AX-Synth has. These are Fantom-X-class features.
- **[3P]** Same `.a8l` container as Juno-G/Fantom-X librarian files; same type vocabulary in BOSS TONE STUDIO.
- **[D]** The AX-Synth address map (Temporary Patch `1F 00 00 00`, Tones at `00 20 00 + 2 00·n`, MFX/Chorus/Reverb/TMT offsets) follows the XV/Fantom/Juno-D family layout.

**Practical consequence [I]:** Script.xml files from sibling Koa editors (Juno-D, Juno-G, Fantom-X, XV-5050, MC-808, SonicCell?) would parse with the same tool, and could help fill gaps such as the `0F 00 10 00` write protocol.
