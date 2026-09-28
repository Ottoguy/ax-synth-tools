"""Web editor (web/): its JavaScript codec must produce exactly the bytes of
the Python library, which the other tests tie to Roland's own bytes
(exports, live edits, synth replies). Runs web modules in Node; skipped if
Node isn't installed. No MIDI involved."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "research" / "tools")]

from axsynth import sysex  # noqa: E402
from axsynth.schema import Schema, addr_to_int, encode_value  # noqa: E402

S = Schema.load()
P = {p.path: p for p in S.parameters("fm")}
MODEL = json.loads((ROOT / "web/model.json").read_text(encoding="utf-8"))
NODE = shutil.which("node")
BACKUP = ROOT / "captures/backup/ax-synth-backup-2026-09-26.mid"
hexs = lambda b: bytes(b).hex(" ").upper()  # noqa: E731


class WebModel(unittest.TestCase):
    def test_model_is_current(self):
        import build_web_model
        self.assertEqual(json.loads(json.dumps(build_web_model.build(), separators=(",", ":"))), MODEL)

    def test_every_patch_value_is_in_the_model(self):
        expected = {p for p, prm in P.items() if p.startswith("fm.pat.")
                    and (prm.structure, prm.name) not in S.unreachable}
        self.assertEqual(set(MODEL["params"]), expected)

    def test_every_visible_value_has_a_control_and_label(self):
        placed = {p for pan in MODEL["panels"] for s in pan["sections"] for p in s["params"]}
        members = {p for k in MODEL["effects"].values() for t in k["types"] for p in t["params"]}
        for path, e in MODEL["params"].items():
            if e["hidden"]:
                continue
            self.assertTrue(e["label"], path)
            self.assertTrue(path in placed or path in members, path)

    def test_editor_manual_value_lists_become_labels(self):
        self.assertEqual(MODEL["params"]["fm.pat.cho.chorusOutputSelect"]["enum"], ["MAIN", "MAIN+REV", "REV"])
        self.assertEqual(MODEL["params"]["fm.pat.common.monoPoly"]["enum"], ["MONO", "POLY"])   # forum 'mono' patch stores 0

    def test_effect_types_and_members(self):
        fx = MODEL["effects"]
        self.assertEqual([len(fx[k]["types"]) for k in ("mfx", "chorus", "reverb")], [79, 3, 5])
        self.assertEqual(fx["mfx"]["types"][63]["name"], "STEP PITCH SHIFTER")
        self.assertEqual(fx["mfx"]["types"][1]["assign"]["labels"], ["OFF", "LOW GAIN", "HIGH GAIN", "LEVEL"])
        for kind, t in ((k, t) for k in fx for t in fx[k]["types"]):
            for path in t["params"]:
                self.assertEqual(MODEL["params"][path]["union"][1], t["number"], path)

    def test_address_offsets_match_the_schema(self):
        for path, e in MODEL["params"].items():
            block = next(b for b in MODEL["blocks"] if b["name"] == e["block"])
            self.assertEqual(sysex.TEMPORARY_PATCH + block["offset"] + e["offset"], addr_to_int(P[path].address), path)


@unittest.skipUnless(NODE, "node not installed")
class WebCodec(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        visible = [p for p, e in MODEL["params"].items() if e["type"] != "string"]
        cls.dt1_cases = [[p, (P[p].range[1] if P[p].range else 1)] for p in visible] + \
                        [["fm.pat.common.patchName", "Test Name   "]]
        cls.live = cls.captured_patch_edits()
        cls.dt1_cases += [[p, v] for p, v, _ in cls.live]
        cls.rt_cases = [[p, v] for p in visible if P[p].range
                        for v in {P[p].range[0], P[p].range[1], P[p].default if isinstance(P[p].default, int) else P[p].range[0]}]
        cls.cases = {
            "dt1": cls.dt1_cases, "roundtrip": cls.rt_cases,
            "a8e": ["patches/guitar01.a8e", "patches/guitar.a8e", "original-roland-files/Script/A8EE/InitialData.a8e"],
            "reply": "captures/rq1/reply.syx", "users": [0, 96, 255], "mfxType": 63,
            "guard": [["30 00 00 00", 1], ["31 7F 26 00", 154], ["0F 00 10 00", 1], ["02 00 40 0A", 1],
                      ["01 00 00 04", 1], ["1F 00 00 00", 79], ["1F 00 26 00", 154], ["1F 00 26 00", 155],
                      ["1F 00 20 49", 1], ["1E 7F 7F 7F", 2]],
            "display": [["fm.pat.tone[0].tvfCutoffFrequency", 127], ["fm.pat.tone[0].waveNumberL", 61],
                        ["fm.pat.mfx.equalizer-loGain", 32783], ["fm.pat.mfx.mfxType", 63],
                        ["fm.pat.common.pitchBendRangeDown", 24], ["fm.pat.tone[0].tvfFilterType", 1]],
        }
        cls.cases["guard"] = [[list(bytes.fromhex(a)), n] for a, n in cls.cases["guard"]]
        tmp = []
        if BACKUP.exists():   # the user's backup (git-ignored): routing over all 256 factory patches
            with tempfile.NamedTemporaryFile("wb", suffix=".syx", delete=False) as fb:
                fb.write(b"".join(sysex.smf_sysex(BACKUP.read_bytes())))
            cls.cases["backup"] = fb.name
            tmp.append(fb.name)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(cls.cases, f)
        tmp.append(f.name)
        run = subprocess.run([NODE, str(ROOT / "tests/web_vectors.mjs"), f.name], capture_output=True, text=True)
        for name in tmp:
            Path(name).unlink()
        if run.returncode:
            raise RuntimeError(run.stderr)
        cls.out = json.loads(run.stdout)

    def py_dt1(self, path, value):
        prm = P[path]
        return hexs(sysex.build_dt1(addr_to_int(prm.address), encode_value(S.value(prm.structure, prm.name), value, check_range=False)))

    def test_every_value_edit_equals_the_python_dt1(self):
        for (path, value), got in zip(self.dt1_cases, self.out["dt1"]):
            self.assertEqual(got, self.py_dt1(path, value), path)

    @staticmethod
    def captured_patch_edits():
        """Every single-value DT1 the Roland Editor sent to the Temporary Patch
        in captures/live (cutoff, name, STEP PITCH SHIFTER values)."""
        import midiox_log
        from axsynth.schema import decode_value
        by_addr = {addr_to_int(prm.address): prm for prm in P.values()
                   if prm.path in MODEL["params"] and not MODEL["params"][prm.path]["hidden"]}
        out = []
        for f in sorted((ROOT / "captures/live").glob("0*.txt")):
            for _, _, _, m in midiox_log.read_log(f):
                r = sysex.parse(bytes(m)) if m[1] == sysex.ROLAND else None
                if not r or r.command != sysex.DT1 or len(r.payload) > 12:
                    continue
                prm = by_addr.get(addr_to_int(r.address))
                if prm and prm.size == len(r.payload):
                    out.append([prm.path, decode_value(S.value(prm.structure, prm.name), r.payload), hexs(m)])
        return out

    def test_captured_editor_edits_are_reproduced_byte_for_byte(self):
        self.assertGreaterEqual(len(self.live), 10)
        self.assertEqual(self.out["dt1"][-len(self.live):], [h for _, _, h in self.live])

    def test_roundtrip(self):
        self.assertEqual(self.out["roundtrip"], [v for _, v in self.rt_cases])

    def test_a8e_to_temporary_dt1s_equal_the_python_tool(self):
        files = {"patches/guitar01.a8e": "research/generated/guitar01-temporary.syx",
                 "patches/guitar.a8e": "research/generated/guitar-temporary.syx"}
        for a8e, syx in files.items():
            expected = [hexs(m) for m in sysex.split_sysex((ROOT / syx).read_bytes())]
            self.assertEqual(self.out["a8e"][a8e], expected, a8e)
        editor_export = [hexs(m) for m in sysex.smf_sysex((ROOT / "dumps/AX-Synth Editor clean export.mid").read_bytes())]
        self.assertEqual(self.out["a8e"]["original-roland-files/Script/A8EE/InitialData.a8e"], editor_export)

    def test_a8e_save_roundtrip(self):
        self.assertTrue(all(self.out["a8eRoundtrip"].values()))

    def test_synth_reply_decodes_to_the_same_blocks(self):
        tmp = sysex.patch_blocks(sysex.split_sysex((ROOT / "captures/rq1/reply.syx").read_bytes()))["temporary"]
        self.assertEqual(self.out["replyBlocks"], {k: hexs(v) for k, v in tmp.items()})

    def test_read_requests_equal_our_rq1_file_and_the_librarian(self):
        ours = [hexs(m) for m in sysex.split_sysex((ROOT / "research/generated/experiment-rq1-temporary-patch.syx").read_bytes())]
        self.assertEqual(self.out["rq1"], ours[:9])
        self.assertEqual(self.out["rq1User"], [hexs(sysex.build_rq1(sysex.user_patch_address(n), 79)) for n in (0, 96, 255)])
        import midiox_log
        lib = [bytes(m) for _, p, _, m in midiox_log.read_log(ROOT / "captures/mitm/01-librarian-read-selected.txt") if str(p) == "1"]
        self.assertEqual(self.out["rq1User"][0], hexs(lib[2]))   # Librarian's RQ1 for slot 1-1 Common

    def test_mfx_type_change_equals_the_roland_editor(self):
        import midiox_log
        msgs = [bytes(m) for _, _, _, m in midiox_log.read_log(ROOT / "captures/live/03-steppitch.txt")]
        self.assertEqual(self.out["mfxChange"], [hexs(msgs[0]), hexs(msgs[1])])
        self.assertTrue(all(p.startswith("fm.pat.mfx.stepPitchShifter-") for p in self.out["mfxChangeParams"]))

    def test_only_the_temporary_patch_is_writable(self):
        self.assertEqual(self.out["guard"], ["refused", "refused", "refused", "refused", "refused",
                                             "allowed", "allowed", "refused", "allowed", "refused"])

    def test_display(self):
        self.assertEqual(self.out["display"][:4], ["127", "61: Overdrive Gt", "0 dB", "STEP PITCH SHIFTER"])


    def test_diff_lists_exactly_the_changes(self):
        d = self.out["diff"]
        self.assertEqual(sorted(map(tuple, d["d1"])), [("fm.pat.common.patchLevel", 127, 100),
                                                       ("fm.pat.tone[0].tvfCutoffFrequency", 127, 40)])
        self.assertIn("fm.pat.rev.reverbType", d["d2"])
        self.assertTrue(all(p.startswith(("fm.pat.rev.", "fm.pat.common.patchLevel", "fm.pat.tone[0].tvf")) for p in d["d2"]))
        self.assertEqual(d["origUntouched"], 127)   # clone is independent

    def test_linked_tones(self):
        lk = self.out["linked"]
        self.assertEqual(lk["values"], [33, 44, 33, 127])   # tone 2 isn't linked: only itself changes
        self.assertEqual(lk["dt1"], [self.py_dt1(f"fm.pat.tone[{t}].tvfCutoffFrequency", v) for t, v in ((0, 33), (2, 33), (1, 44))])

    def test_routing_rules(self):
        rc = self.out["routingCases"]
        self.assertEqual(rc["silent"], ["warn"])     # reverb on, nothing sent to it
        self.assertEqual(rc["toneFed"], ["ok"])      # tone REV send
        self.assertEqual(rc["choFed"], ["ok"])       # chorus -> reverb (OUTPUT SELECT = REV)
        self.assertEqual(rc["setupOff"], ["ok", "warn"])
        init = self.out["routing"]["original-roland-files/Script/A8EE/InitialData.a8e"]
        self.assertEqual({r["level"] for r in init if r["unit"] in ("mfx", "chorus", "reverb")}, {"info"})

    @unittest.skipUnless(BACKUP.exists(), "user's backup not present")
    def test_routing_on_all_factory_patches(self):
        """Factory patches with reverb on and level > 0: only the 4 with an
        unused reverb (no sends, no chorus->reverb) are flagged; the other
        reverb warnings are patches whose REVERB LEVEL is 0."""
        b = self.out["backupRouting"]
        self.assertEqual(b["reverbOn"], 193)
        self.assertEqual(b["reverbWarn"], [71, 101, 137, 182])   # Acdg Bass, Dist.Fingerz, Octa Brass, …
        self.assertEqual(b["reverbLevel0"], [154, 165, 170, 176, 184, 187, 189, 191])

    def test_wave_selection_sets_the_internal_wave_group(self):
        self.assertEqual(self.out["wave"], [2, 1, 23])


if __name__ == "__main__":
    unittest.main()
