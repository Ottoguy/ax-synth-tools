// Node runner for tests/test_web.py: executes the browser modules in web/
// on test cases and prints the results as JSON. No MIDI involved.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import * as sx from "../web/sysex.js";
import { Patch, display } from "../web/patch.js";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const model = JSON.parse(readFileSync(join(ROOT, "web/model.json"), "utf8"));
const cases = JSON.parse(readFileSync(process.argv[2], "utf8"));
const bytes = (rel) => new Uint8Array(readFileSync(join(ROOT, rel)));
const out = {};

// one live edit = one DT1 (Patch.set from INIT)
out.dt1 = cases.dt1.map(([path, value]) => {
  const p = Patch.initial(model);
  const c = p.set(path, value, false);
  return sx.hex(sx.buildDT1(c.address, Array.from(c.data)));
});

// decode(encode(v)) for every visible parameter at lo/default/hi
out.roundtrip = cases.roundtrip.map(([path, value]) => {
  const pr = model.params[path];
  return sx.decodeValue(pr, sx.encodeValue(pr, value, false));
});

// .a8e -> 9 Temporary DT1s (must equal dump_experiment.py a8-to-syx output)
out.a8e = Object.fromEntries(cases.a8e.map((rel) => [rel,
  sx.patchMessages(model, Patch.fromA8e(model, bytes(rel)).blocks).map(sx.hex)]));

// .a8e open -> save round trip (with the same file as template)
out.a8eRoundtrip = Object.fromEntries(cases.a8e.map((rel) => {
  const b = bytes(rel);
  return [rel, sx.hex(Patch.fromA8e(model, b).toA8e(b)) === sx.hex(b)];
}));

// synth reply -> Temporary blocks
out.replyBlocks = Object.fromEntries(Object.entries(sx.temporaryBlocks(model, sx.splitSysex(bytes(cases.reply))))
  .map(([k, v]) => [k, sx.hex(v)]));

// RQ1s for the 9 Temporary blocks and for User patch n
out.rq1 = model.blocks.map((b) => sx.hex(sx.buildRQ1(model.meta.temporaryPatch + b.offset, b.size)));
out.rq1User = cases.users.map((n) => sx.hex(sx.buildRQ1(sx.userPatchAddress(n), model.blocks[0].size)));

// MFX type change from INIT (compare with the Roland Editor's captured block)
{
  const p = Patch.initial(model);
  const [block, type] = p.changeEffectType("mfx", cases.mfxType);
  out.mfxChange = [sx.hex(sx.buildDT1(block.address, block.data)), sx.hex(sx.buildDT1(type.address, Array.from(type.data)))];
  out.mfxChangeParams = p.effectParams("mfx");
}

// the address guard
out.guard = cases.guard.map(([addr, len]) => {
  try {
    sx.buildDT1(sx.addrToInt(addr), new Array(len).fill(0));
    return "allowed";
  } catch (e) {
    return "refused";
  }
});

// display strings
out.display = cases.display.map(([path, raw]) => display(model.params[path], raw, model.waves));

// wave selection sets the wave group
{
  const p = Patch.initial(model);
  p.set("fm.pat.tone[0].waveGroupType", 0);
  const ch = p.setWave("fm.pat.tone[0].waveNumberL", 61);
  out.wave = [ch.length, p.get("fm.pat.tone[0].waveGroupType"), p.get("fm.pat.tone[0].waveGroupID")];
}

process.stdout.write(JSON.stringify(out));
