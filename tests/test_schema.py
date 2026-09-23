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
from axsynth.schema import Schema, addr_to_int, decode_value, encode_value, int_to_addr  # noqa: E402

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


if __name__ == "__main__":
    unittest.main()
