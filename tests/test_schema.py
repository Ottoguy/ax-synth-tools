"""Evidence tests: each assertion ties the generated model to a source.

Run:  py -3 -m unittest discover -s tests -v
(regenerate first if Script.xml tooling changed:
   py -3 research/tools/extract_script_schema.py
   py -3 research/tools/crosscheck_midi_impl.py)
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research" / "tools"))

from axsynth import sysex  # noqa: E402
from axsynth.schema import Schema, addr_to_int, decode_value, encode_value, fmt_addr, int_to_addr  # noqa: E402

S = Schema.load()
P = {p.path: p for p in S.parameters(root=None)}


class ExtractionCounts(unittest.TestCase):
    def test_counts(self):
        c = S.data["counts"]
        self.assertEqual(c["structTypes"], 27)
        self.assertEqual(c["values"], 1539)

    def test_types_are_exactly_the_exe_vocabulary_subset(self):
        # A8EE.exe knows: string int4x4 int3x4 int2x4 int5x7 int3x7 int2x7 int1x7
        exe_types = {"string", "int4x4", "int3x4", "int2x4", "int5x7", "int3x7", "int2x7", "int1x7"}
        used = {v.type for t in S.data["structTypes"] for v in S.values(t)}
        self.assertLessEqual(used, exe_types)

    def test_size_matches_type_width(self):
        for t in S.data["structTypes"]:
            for v in S.values(t):
                if v.bits:
                    self.assertEqual(v.size, v.bits[0], f"{t}.{v.name}")


class AddressesMatchOfficialMap(unittest.TestCase):
    """docs/AX Synth docs.pdf, section 3 'Parameter Address Map'."""
    CASES = {
        "fm.setup.kbdPatchBankSelectMsb": "01 00 00 04",   # Setup 00 04
        "fm.setup.octaveShift": "01 00 00 13",
        "fm.system.common.masterTune": "02 00 00 00",       # nibbled, 24..2024
        "fm.system.controller.neckSwitchSelect": "02 00 40 4E",
        "fm.pat.common.patchName": "1F 00 00 00",
        "fm.pat.mfx.mfxType": "1F 00 02 00",
        "fm.pat.mfx.mfxParameter29": "1F 00 03 01",
        "fm.pat.cho.chorusType": "1F 00 04 00",
        "fm.pat.rev.reverbType": "1F 00 06 00",
        "fm.pat.tmt.structureType12": "1F 00 10 00",
        "fm.pat.tone[0].toneLevel": "1F 00 20 00",
        "fm.pat.tone[1].toneLevel": "1F 00 22 00",
        "fm.pat.tone[3].tvfCutoffFrequency": "1F 00 26 49",
        "fm.pat.tone[3].lfoStep16": "1F 00 27 19",
    }

    def test_addresses(self):
        for path, addr in self.CASES.items():
            self.assertEqual(P[path].address, addr, path)

    def test_struct_sizes_match_doc_total_size(self):
        doc = {"Setup": 0x34, "SystemCommon": 0x1E, "PatchCommon": 0x4F,
               "PatchCommonMFX": addr_to_int("01 11"), "PatchCommonChorus": 0x54,
               "PatchCommonReverb": 0x53, "PatchTMT": 0x29, "PatchTone": addr_to_int("01 1A")}
        for t, n in doc.items():
            self.assertEqual(S.struct_size(t), n, t)

    def test_known_discrepancy_system_controller(self):
        # doc: Total Size 00 00 00 50 (includes 00 4F Portament Mode);
        # Script.xml: 00 00 00 4F. Kept visible until hardware settles it.
        self.assertEqual(S.struct_size("SystemController"), 0x4F)

    def test_step_pitch_shifter_anomaly_resolves_to_doc_slots(self):
        self.assertEqual(P["fm.pat.mfx.stepPitchShifter-bal"].address, "1F 00 03 01")
        self.assertEqual(P["fm.pat.mfx.stepPitchShifter-level"].address, "1F 00 03 05")
        self.assertTrue(P["fm.pat.mfx.stepPitchShifter-bal"].notes)


class Codec(unittest.TestCase):
    def test_doc_nibble_examples(self):
        # doc p.15 Example3: nibbled 0A 03 09 0D = 41885; Example4: 1258 -> 00 04 0E 0A
        v = S.value("SystemCommon", "masterTune")
        self.assertEqual(decode_value(v, bytes([0x0A, 0x03, 0x09, 0x0D])), 41885)
        self.assertEqual(encode_value(v, 1258), bytes([0, 4, 0x0E, 0x0A]))
        self.assertEqual(encode_value(v, 1024), bytes([0, 4, 0, 0]))

    def test_mfx_param_zero_point(self):
        v = S.value("PatchCommonMFX", "mfxParameter1")
        self.assertEqual(v.range, (12768, 52768))           # doc: -20000..+20000
        self.assertEqual(encode_value(v, 32768), bytes([8, 0, 0, 0]))

    def test_roundtrip_all_defaults(self):
        for t in S.data["structTypes"]:
            for v in S.values(t):
                if isinstance(v.default, int) and v.bits and (v.range is None or v.range[0] <= v.default <= v.range[1]):
                    self.assertEqual(decode_value(v, encode_value(v, v.default)), v.default)

    def test_address_helpers(self):
        self.assertEqual(int_to_addr(addr_to_int("00 7D") + 4, 2), bytes([1, 1]))


class RolandDataFiles(unittest.TestCase):
    def setUp(self):
        import a8_files
        self.a8 = a8_files
        self.a8e = a8_files.parse(ROOT / "original-roland-files/Script/A8EE/InitialData.a8e", S)
        self.a8l = a8_files.parse(ROOT / "original-roland-files/Script/A8EL/InitialData.a8l", S)

    def test_a8e_fully_consumed(self):
        self.assertEqual(self.a8e["bytes_consumed"], self.a8e["file_size"])
        self.assertEqual(self.a8e["header"]["root"], "fm")

    def test_a8l_fully_consumed(self):
        self.assertEqual(self.a8l["bytes_consumed"], self.a8l["file_size"])
        p = self.a8l["patches"][0]
        self.assertTrue(all(b["size_ok"] and b["count_ok"] for b in p["blocks"]))

    def test_a8e_active_values_equal_script_defaults(self):
        # Only reserved / unreachable (gm2*) values may differ.
        for b in self.a8e["blocks"]:
            for v in b["values"]:
                if not v["is_default"]:
                    name = v["path"].rsplit(".", 1)[1]
                    self.assertTrue(name.startswith(("reserve", "gm2")), v["path"])

    def test_same_init_patch_in_both_files(self):
        a8e = {b["path"].removeprefix("fm."): b for b in self.a8e["blocks"] if b["path"].startswith("fm.pat")}
        a8l = {b["path"]: b for b in self.a8l["patches"][0]["blocks"]}
        self.assertEqual(sorted(a8e), sorted(a8l))
        self.assertEqual(len(a8l), 9)  # common mfx cho rev tmt tone[0..3]
        for k in a8l:
            self.assertEqual([v["raw"] for v in a8e[k]["values"]], [v["raw"] for v in a8l[k]["values"]], k)


class SysEx(unittest.TestCase):
    def test_checksum_known_gs_reset(self):
        # Widely published GS Reset: F0 41 10 42 12 40 00 7F 00 41 F7 (third-party
        # knowledge; checks the doc p.16 formula)
        self.assertEqual(sysex.checksum(bytes([0x40, 0x00, 0x7F, 0x00])), 0x41)

    def test_dt1_roundtrip(self):
        m = sysex.build_dt1(bytes([0x1F, 0, 0x20, 0x49]), bytes([0x40]))
        self.assertEqual(m[:7], bytes([0xF0, 0x41, 0x10, 0x00, 0x00, 0x3C, 0x12]))
        r = sysex.parse(m)
        self.assertTrue(r.checksum_ok)
        self.assertEqual(r.address, bytes([0x1F, 0, 0x20, 0x49]))

    def test_rq1_temporary_patch_common(self):
        m = sysex.build_rq1(bytes([0x1F, 0, 0, 0]), S.struct_size("PatchCommon"))
        self.assertEqual(m[7:15], bytes([0x1F, 0, 0, 0, 0, 0, 0, 0x4F]))
        self.assertTrue(sysex.parse(m).checksum_ok)

    def test_identity_reply_doc_fields(self):
        r = sysex.parse_identity_reply(sysex.IDENTITY_REPLY_DOC)
        self.assertEqual((r.device, r.manufacturer), (0x10, sysex.ROLAND))
        self.assertEqual((r.family, r.family_number, r.revision),
                         (bytes([0x3C, 0x02]), bytes(2), bytes([0, 1, 0, 0])))
        self.assertEqual(r.differences_from_doc(), [])
        other = bytearray(sysex.IDENTITY_REPLY_DOC)
        other[10:14] = bytes([0, 2, 0, 1])   # hypothetical revision, e.g. firmware 2.01
        self.assertEqual(sysex.parse_identity_reply(bytes(other)).differences_from_doc(),
                         ["revision: 00 02 00 01 (doc 00 01 00 00)"])
        with self.assertRaises(ValueError):
            sysex.parse_identity_reply(sysex.identity_request())


class RolandSmfExports(unittest.TestCase):
    """dumps/: 'Export SMF' from the Editor and Librarian (INIT data, no synth
    attached). Our encoder must reproduce Roland's bytes exactly."""

    @classmethod
    def setUpClass(cls):
        import a8_files
        import smf_inspect
        path = ROOT / "original-roland-files/Script/A8EE/InitialData.a8e"
        buf = path.read_bytes()
        res = a8_files.parse(path, S)
        cls.init = {b["path"].removeprefix("fm.pat."): buf[b["file_offset"]:b["file_offset"] + b["size"]]
                    for b in res["blocks"] if b["path"].startswith("fm.pat")}

        def load(name):
            evs = [e for t, e in smf_inspect.events((ROOT / "dumps" / name).read_bytes()) if t == "event"]
            return [e for e in evs if e[3] == "sysex"]
        cls.editor = load("AX-Synth Editor clean export.mid")
        cls.librarian = load("AX-Synth Librarian Clean export.mid")

    def test_editor_export_is_byte_identical_to_our_encoder(self):
        ours = sysex.patch_messages(self.init)  # Temporary Patch
        self.assertEqual([e[4] for e in self.editor], ours)

    def test_librarian_export_is_256_user_patches(self):
        self.assertEqual(len(self.librarian), 256 * 9)
        for n in (0, 1, 127, 128, 255):
            ours = sysex.patch_messages(self.init, sysex.user_patch_address(n))
            self.assertEqual([e[4] for e in self.librarian[9 * n:9 * n + 9]], ours, n)
        self.assertEqual(fmt_addr(int_to_addr(sysex.user_patch_address(255))), "31 7F 00 00")

    def test_export_timing_model(self):
        for msgs in (self.editor, self.librarian):
            for cur, nxt in zip(msgs, msgs[1:]):
                self.assertEqual(nxt[2], sysex.roland_export_delay_ticks(len(cur[4])))


class ThirdPartyPatches(unittest.TestCase):
    """patches/: two .a8e files shared on a forum by their author, with a
    description of what was changed (research/third-party-patches-analysis.md).
    The description is independent ground truth for our meanings/labels."""

    @classmethod
    def setUpClass(cls):
        import a8_files

        def load(name):
            res = a8_files.parse(ROOT / "patches" / name, S)
            return {v["path"].removeprefix("fm."): v for b in res["blocks"] for v in b["values"]}, res
        (cls.g, cls.g_res), (cls.g1, cls.g1_res) = load("guitar.a8e"), load("guitar01.a8e")

    def v(self, patch, path):
        return patch[path]["value"]

    def test_files_parse_completely(self):
        for res in (self.g_res, self.g1_res):
            self.assertEqual(res["bytes_consumed"], res["file_size"])

    def test_pitch_bend_two_octaves_down_one_up(self):
        for p in (self.g, self.g1):
            self.assertEqual(self.v(p, "pat.common.pitchBendRangeDown"), 24)
            self.assertEqual(self.v(p, "pat.common.pitchBendRangeUp"), 12)

    def test_mono(self):
        for p in (self.g, self.g1):
            self.assertEqual(self.v(p, "pat.common.monoPoly"), 0)  # doc: MONO, POLY

    def test_velocity_1_69_layer_is_tone4(self):
        for p in (self.g, self.g1):
            self.assertEqual(self.v(p, "pat.tmt.tmtToneSwitch[3]"), 1)
            self.assertEqual(self.v(p, "pat.tmt.tmtVelocityRangeLower[3]"), 1)
            self.assertEqual(self.v(p, "pat.tmt.tmtVelocityRangeUpper[3]"), 69)

    def test_cc70_matrix_source_label(self):
        p = P["fm.pat.common.matrixControl3Source"]
        raw = self.v(self.g, "pat.common.matrixControl3Source")
        self.assertEqual(raw, 70)
        self.assertTrue(p.enum[raw - p.range[0]].startswith("CC70"))  # table keeps a '32:OFF' slot

    def test_feedback_patch_has_beam_on_cc70(self):
        # "controller number 70 (if you choose it for your beam controller)";
        # guitar01 = "feedback works". Beam table has no CC32 slot: raw 68 = CC70.
        p = P["fm.system.controller.beamAssign"]
        raw = self.v(self.g1, "system.controller.beamAssign")
        self.assertEqual(raw, 68)
        self.assertTrue(p.enum[raw - p.range[0]].startswith("CC70"))

    def test_24_semitone_layer_in_guitar01(self):
        p = P["fm.pat.tone[1].toneCoarseTune"]
        self.assertEqual(self.v(self.g1, "pat.tone[1].toneCoarseTune") + p.display_offset, 24)

    def test_mfx_is_guitar_amp(self):
        names = S.data["effect_unions"]["mfx"]["display_names"]["names"]
        self.assertEqual(names[self.v(self.g, "pat.mfx.mfxType")], "GUITAR AMP SIMULATOR")
        active = {k for k, v in self.g.items() if v["active"] and k.startswith("pat.mfx.guitarAmp")}
        self.assertTrue(active)

    def test_all_active_values_within_script_range(self):
        # only known exception: SystemController reserve04 (=100 in every .a8e
        # seen, incl. Roland's InitialData; script says 0..1, doc says 7-bit)
        for p in (self.g, self.g1):
            for path, v in p.items():
                prm = P.get("fm." + path)
                if not v["active"] or prm is None or not prm.range or not isinstance(v["value"], int):
                    continue
                if path == "system.controller.reserve04":
                    continue
                self.assertTrue(prm.range[0] <= v["value"] <= prm.range[1], path)


class OwnersManual(unittest.TestCase):
    """docs/AX-Synth_OM.pdf (text: research/generated/owners-manual.pdf.txt)."""

    def test_tone_list_shape(self):
        from axsynth import factory
        t = factory.tones()
        self.assertEqual(len(t), 264)
        reg = [x for x in t if x.editable]
        self.assertEqual(len(reg), 256)
        self.assertEqual(sorted(x.user_patch_index for x in reg), list(range(256)))
        self.assertEqual(len(factory.families()), 8)
        self.assertEqual(factory.by_name("Violin").cc00_msb, 66)   # SuperNATURAL bank
        self.assertEqual(factory.by_name("Sax").cc32_lsb, 64)      # SPECIAL bank

    def test_forum_patch_is_factory_searing_gtr_1(self):
        # Both forum files keep name 'SearingGtr 1' and Setup bank 87/0, program 96 (0-based):
        # the manual lists SearingGtr 1 as Lead Guitar #1 = 87/0/PC 97.
        import a8_files
        from axsynth import factory
        res = a8_files.parse(ROOT / "patches" / "guitar.a8e", S)
        v = {x["path"]: x["value"] for b in res["blocks"] for x in b["values"]}
        t = factory.by_program(v["fm.setup.kbdPatchBankSelectMsb"], v["fm.setup.kbdPatchBankSelectLsb"],
                               v["fm.setup.kbdPatchProgramNumber"])
        self.assertEqual(t.name, "SearingGtr 1")
        self.assertEqual(factory.by_name(v["fm.pat.common.patchName"]), t)
        self.assertEqual((t.group, t.position, t.librarian_slot), ("Lead Guitar", 1, "4-1"))

    def test_setup_default_bank_is_regular(self):
        # Setup default kbdPatchBankSelectMsb = 87 = regular/special Tone bank (manual p.37)
        self.assertEqual(S.value("Setup", "kbdPatchBankSelectMsb").default, 87)

    def test_manual_ranges_match_model(self):
        # Transpose -5..+6 (p.21), octave +-3 (p.22), master tune 415.3-466.2 Hz (p.21)
        self.assertEqual(S.value("Setup", "transposeValue").range, (59, 70))
        self.assertEqual(S.value("Setup", "octaveShift").range, (61, 67))
        mt = [x for x in S.data["stringTables"]["masterTuneTable"]["items"] if x]
        self.assertEqual((mt[0], mt[-1]), ("415.30", "466.20"))


class KnowledgeBase(unittest.TestCase):
    """knowledge/*.toml (manual extraction) validated against the data model."""

    @classmethod
    def setUpClass(cls):
        import build_knowledge
        cls.kb, cls.errors = build_knowledge.build()

    def test_builds_without_errors(self):
        self.assertEqual([e for e in self.errors if not e.startswith("WARNING")], [])

    def test_all_effect_types_present(self):
        self.assertEqual([e["number"] for e in self.kb["mfx"]], list(range(1, 79)))
        self.assertEqual([e["number"] for e in self.kb["chorus"]], [1, 2])
        self.assertEqual([e["number"] for e in self.kb["reverb"]], [1, 2, 3, 4])

    def test_only_reserved_values_undocumented(self):
        for path in self.kb["coverage"]["data_model_values_without_kb_entry"]:
            self.assertIn("reserve", path.rsplit(".", 1)[1])

    def test_schema_only_effect_members_are_tempo_sync_variants(self):
        for groups in self.kb["coverage"]["schema_only_effect_members"].values():
            for members in groups.values():
                for m in members:
                    self.assertRegex(m, r"(Sync|Note)$")

    def test_committed_json_is_current(self):
        import json
        committed = json.loads((ROOT / "knowledge/knowledge.json").read_text(encoding="utf-8"))
        self.assertEqual(committed, json.loads(json.dumps(self.kb, ensure_ascii=False)),
                         "rerun research/tools/build_knowledge.py")

    def test_lookup_api(self):
        from axsynth import knowledge
        d = knowledge.describe("fm.pat.tone[2].tvfCutoffFrequency")
        self.assertEqual(d[0]["id"], "tone.cutoff")
        e = knowledge.describe("fm.pat.mfx.guitarAmpSimulator-ampType")
        self.assertEqual((e[0]["kind"], e[0]["number"]), ("mfx", 39))
        self.assertEqual(knowledge.effect("reverb", 4)["name"], "SRV PLATE")

    def test_sound_design_section(self):
        # Synth Secrets knowledge [3P] mapped to the AX-Synth [I]; every ref, wave,
        # factory Tone and part number is validated by build() (no errors above)
        sd = self.kb["sound_design"]
        self.assertEqual([p["part"] for p in sd["synth_secrets"]], list(range(1, 64)))
        for p in sd["synth_secrets"]:
            self.assertTrue((ROOT / p["digest"]).exists())
            self.assertTrue(p["url"].startswith("https://www.soundonsound.com/techniques/"))
        self.assertGreaterEqual(len(sd["principles"]), 25)
        self.assertGreaterEqual(len(sd["descriptors"]), 35)
        self.assertGreaterEqual(len(sd["recipes"]), 30)
        cited = {n for kind in ("principles", "descriptors", "recipes") for e in sd[kind] for n in e["ss"]}
        self.assertLessEqual(cited, set(range(1, 64)))

    def test_sound_design_lookup(self):
        from axsynth import knowledge
        self.assertEqual(knowledge.descriptor("warm")["id"], "dark")
        self.assertEqual(knowledge.recipe("perc.cowbell")["waves"][0], {"number": 214, "name": "Syn Triangle"})
        self.assertIn(54, knowledge.principle("dynamics.flute_pressure_is_brightness")["ss"])


if __name__ == "__main__":
    unittest.main()


class LiveEditorCaptures(unittest.TestCase):
    """captures/live/*.txt: MIDI-OX logs of the Editor's/Librarian's live
    output through a loopback port (NEXT-STEPS step 2; no synth attached,
    so nothing ever answered). See research/live-capture-analysis.md."""

    @classmethod
    def setUpClass(cls):
        import midiox_log
        cls.logs = {f.stem: midiox_log.read_log(f) for f in (ROOT / "captures" / "live").glob("*.txt")}

    def msgs(self, stem):
        return [m for _, _, _, m in self.logs[stem]]

    def test_all_captured_messages_well_formed(self):
        self.assertEqual(len(self.logs), 8)
        for stem, log in self.logs.items():
            for _, _, declared, m in log:
                self.assertEqual(declared, len(m), stem)
                if m[1] == sysex.ROLAND:
                    r = sysex.parse(m)
                    self.assertTrue(r.checksum_ok, stem)
                    self.assertEqual((r.device, r.model_id), (sysex.DEFAULT_DEVICE, sysex.MODEL_ID))

    def dt1(self, path, value):
        p = P[path]
        return sysex.build_dt1(addr_to_int(p.address), encode_value(S.value(p.structure, p.name), value))

    def test_single_parameter_edits_are_one_dt1_per_value(self):
        self.assertEqual(self.msgs("01-cutoff"), [self.dt1("fm.pat.tone[0].tvfCutoffFrequency", 124)])
        self.assertEqual(self.msgs("02-name"), [self.dt1("fm.pat.common.patchName", "TEST")])
        sysmsgs = self.msgs("04-system")
        self.assertEqual(sysmsgs[0], self.dt1("fm.system.common.masterTune", 1297))
        self.assertEqual(sysmsgs[7], self.dt1("fm.system.controller.beamRangeLower", 3))
        self.assertEqual(sysmsgs[-1], self.dt1("fm.system.controller.beamRangeUpper", 109))

    def test_step_pitch_shifter_addresses_are_base128(self):
        # Script.xml says 00 81 / 00 85; the Editor sends 1F 00 03 01 / 05,
        # exactly what our base-128 resolution gives.
        m = self.msgs("03-steppitch")
        self.assertEqual(P["fm.pat.mfx.stepPitchShifter-bal"].address, "1F 00 03 01")
        self.assertEqual(P["fm.pat.mfx.stepPitchShifter-level"].address, "1F 00 03 05")
        self.assertEqual(m[2], self.dt1("fm.pat.mfx.stepPitchShifter-bal", 32768 + 12))
        self.assertEqual(m[-1], self.dt1("fm.pat.mfx.stepPitchShifter-level", 32768 + 112))
        self.assertEqual({sysex.parse(x).address for x in m[2:]},
                         {bytes.fromhex("1F000301"), bytes.fromhex("1F000305")})

    def test_mfx_type_change_sends_whole_block_of_script_defaults(self):
        # new type 63 = STEP PITCH SHIFTER; every member = Script.xml default
        mfx_type = 63
        base = addr_to_int(P["fm.pat.mfx.mfxType"].address)
        block = bytearray(S.struct_size("PatchCommonMFX"))
        for p in sorted((p for p in P.values() if p.path.startswith("fm.pat.mfx.")
                         and (p.effect is None or p.effect_index == mfx_type)),
                        key=lambda p: p.effect is not None):   # members overlay generic slots
            v = mfx_type if p.name == "mfxType" else p.default
            raw = encode_value(S.value(p.structure, p.name), v)
            o = addr_to_int(p.address) - base
            block[o:o + len(raw)] = raw
        m = self.msgs("03-steppitch")
        self.assertEqual(m[0], sysex.build_dt1(base, bytes(block)))
        self.assertEqual(m[1], self.dt1("fm.pat.mfx.mfxType", mfx_type))   # then the type byte again

    def test_read_sync_librarian_start_with_identity_request(self):
        for stem in ("05-read", "06-sync", "08-librarian"):
            log = self.logs[stem]
            self.assertEqual([m for *_, m in log], [sysex.identity_request()] * 2, stem)
            self.assertAlmostEqual(log[1][0] - log[0][0], 3000, delta=50)   # ~3 s timeout, 1 retry

    def test_write_reads_user_patch_name_by_plain_rq1(self):
        m = self.msgs("07-write")
        rq = sysex.build_rq1(sysex.user_patch_address(0), P["fm.pat.common.patchName"].size)
        self.assertEqual(m, [rq, rq, sysex.identity_request(), sysex.identity_request()])
