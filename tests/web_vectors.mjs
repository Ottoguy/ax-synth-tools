// Node runner for tests/test_web.py: executes the browser modules in web/
// on test cases and prints the results as JSON. No MIDI involved.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, isAbsolute, join } from "node:path";
import * as sx from "../web/sysex.js";
import { Patch, display, routing } from "../web/patch.js";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const model = JSON.parse(readFileSync(join(ROOT, "web/model.json"), "utf8"));
const cases = JSON.parse(readFileSync(process.argv[2], "utf8"));
const bytes = (rel) => new Uint8Array(readFileSync(isAbsolute(rel) ? rel : join(ROOT, rel)));
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


// diff / clone
{
  const orig = Patch.initial(model);
  const p = orig.clone();
  p.set("fm.pat.tone[0].tvfCutoffFrequency", 40);
  p.set("fm.pat.common.patchLevel", 100);
  const d1 = p.diff(orig).map((r) => [r.path, r.from, r.to]);
  p.changeEffectType("reverb", 3);
  const d2 = p.diff(orig).map((r) => r.path);
  out.diff = { d1, d2, origUntouched: orig.get("fm.pat.tone[0].tvfCutoffFrequency") };
}

// linked tones: tone 1 edit with tones 1 and 3 linked
{
  const p = Patch.initial(model);
  const ch = p.setLinked("fm.pat.tone[0].tvfCutoffFrequency", 33, [0, 2]);
  const solo = p.setLinked("fm.pat.tone[1].tvfCutoffFrequency", 44, [0, 2]);
  out.linked = { values: [0, 1, 2, 3].map((t) => p.get(`fm.pat.tone[${t}].tvfCutoffFrequency`)),
                 dt1: ch.concat(solo).map((c) => sx.hex(sx.buildDT1(c.address, Array.from(c.data)))) };
}

// routing on files and, if given, on every patch of a backup (.syx of 30 nn DT1s)
out.routing = Object.fromEntries(cases.a8e.map((rel) => [rel, routing(Patch.fromA8e(model, bytes(rel)))]));
{
  const p = Patch.initial(model);
  p.changeEffectType("reverb", 4);
  p.set("fm.pat.tmt.tmtToneSwitch[0]", 1);
  const silent = routing(p).filter((r) => r.unit === "reverb").map((r) => r.level);
  p.set("fm.pat.tone[0].toneReverbSendLevelMFX", 50);
  const toneFed = routing(p).filter((r) => r.unit === "reverb").map((r) => r.level);
  p.set("fm.pat.tone[0].toneReverbSendLevelMFX", 0);
  p.changeEffectType("chorus", 1);
  p.set("fm.pat.tone[0].toneChorusSendLevelMFX", 50);
  p.set("fm.pat.cho.chorusOutputSelect", 2);
  const choFed = routing(p).filter((r) => r.unit === "reverb").map((r) => r.level);
  const setupOff = routing(p, { reverbSwitch: 0 }).filter((r) => r.unit === "reverb").map((r) => r.level);
  out.routingCases = { silent, toneFed, choFed, setupOff };
}
if (cases.backup) {
  const msgs = sx.splitSysex(bytes(cases.backup));
  const byAddr = new Map(msgs.map((m) => [sx.parse(m).address, Uint8Array.from(sx.parse(m).payload)]));
  const summary = { reverbOn: 0, reverbWarn: [], warnUnits: {} };
  for (let n = 0; n < 256; n++) {
    const blocks = {};
    for (const b of model.blocks) blocks[b.name] = byAddr.get(sx.userPatchAddress(n) + b.offset);
    const p = new Patch(model, blocks);
    const r = routing(p);
    if (p.effectType("reverb") && p.get("fm.pat.rev.reverbLevel")) summary.reverbOn++;
    for (const x of r) if (x.level === "warn") summary.warnUnits[x.unit] = (summary.warnUnits[x.unit] || 0) + 1;
    if (r.some((x) => x.unit === "reverb" && x.level === "warn")) {
      (p.get("fm.pat.rev.reverbLevel") === 0 ? (summary.reverbLevel0 ||= []) : summary.reverbWarn).push(n);
    }
  }
  out.backupRouting = summary;
}

process.stdout.write(JSON.stringify(out));
