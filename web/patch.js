// The patch being edited: 9 byte blocks (the single source of truth), read
// and written through the value codec. No DOM, no MIDI (tested with Node).
import { decodeValue, encodeValue } from "./sysex.js";

export function base64ToBytes(b64) {
  const s = typeof atob === "function" ? atob(b64) : Buffer.from(b64, "base64").toString("binary");
  return Uint8Array.from(s, (c) => c.charCodeAt(0));
}

export class Patch {
  constructor(model, blocks) {
    this.model = model;
    this.blocks = {};
    for (const b of model.blocks) this.blocks[b.name] = Uint8Array.from(blocks[b.name]);
  }

  static fromA8e(model, bytes) {
    const magic = String.fromCharCode(...bytes.slice(0, 16));
    if (magic !== "KoaDataFile00001") throw new Error("not an AX-Synth Editor file (.a8e)");
    if (bytes.length !== model.a8e.size) throw new Error(`unexpected .a8e size ${bytes.length} (expected ${model.a8e.size})`);
    const blocks = {};
    for (const e of model.a8e.layout) {
      if (e.path.startsWith("fm.pat.")) blocks[e.path.slice(7)] = bytes.slice(e.offset, e.offset + e.size);
    }
    return new Patch(model, blocks);
  }

  static initial(model) {
    return Patch.fromA8e(model, base64ToBytes(model.a8e.initial));
  }

  // .a8e = a template (the file it was opened from, or Roland's InitialData)
  // with this patch's blocks written in. Setup/System stay from the template.
  toA8e(template) {
    const out = Uint8Array.from(template || base64ToBytes(this.model.a8e.initial));
    for (const e of this.model.a8e.layout) {
      if (e.path.startsWith("fm.pat.")) out.set(this.blocks[e.path.slice(7)], e.offset);
    }
    return out;
  }

  param(path) {
    const p = this.model.params[path];
    if (!p) throw new Error(`unknown parameter ${path}`);
    return p;
  }

  get(path) {
    const p = this.param(path);
    return decodeValue(p, this.blocks[p.block].slice(p.offset, p.offset + p.size));
  }

  // Returns the change to transmit: {address, data} (one value = one DT1,
  // exactly like the Roland Editor's live edits, captures/live/).
  set(path, value, checkRange = true) {
    const p = this.param(path);
    const bytes = encodeValue(p, value, checkRange);
    this.blocks[p.block].set(bytes, p.offset);
    return { address: this.address(p), data: bytes };
  }

  address(p) {
    const b = this.model.blocks.find((x) => x.name === p.block);
    return this.model.meta.temporaryPatch + b.offset + p.offset;
  }

  blockAddress(name) {
    return this.model.meta.temporaryPatch + this.model.blocks.find((x) => x.name === name).offset;
  }

  // Effect type change, as the Roland Editor does it (captures/live/03-steppitch):
  // the whole block with the new type's members at their Script.xml defaults,
  // then the type byte again. Kept from the current patch: send levels, output
  // and control sources; reset: generic slots and Control Assign [inference].
  changeEffectType(kind, number) {
    const eff = this.model.effects[kind];
    const disc = this.param(eff.discriminator);
    const block = disc.block;
    for (const [path, p] of Object.entries(this.model.params)) {
      if (p.block !== block || !p.union || p.union[0] !== kind) continue;
      if (p.union[1] === 0) this.set(path, p.default, false);
    }
    for (const [path, p] of Object.entries(this.model.params)) {
      if (p.block !== block || !p.union || p.union[0] !== kind) continue;
      if (p.union[1] === number) this.set(path, p.default, false);
    }
    this.set(eff.discriminator, number);
    return [
      { address: this.blockAddress(block), data: Array.from(this.blocks[block]) },
      { address: this.address(disc), data: encodeValue(disc, number) },
    ];
  }

  effectType(kind) {
    return this.get(this.model.effects[kind].discriminator);
  }

  // Parameters to show for an effect: the members of its current type.
  effectParams(kind) {
    const t = this.model.effects[kind].types.find((x) => x.number === this.effectType(kind));
    return t ? t.params : [];
  }

  // Selecting a wave also sets the wave group to the internal PCM group
  // (type 1, ID 23): every active tone of all 256 factory patches uses it
  // (captures/backup), and the Editor manual says only INT exists.
  setWave(path, number) {
    const changes = [this.set(path, number)];
    const tone = path.match(/^fm\.pat\.tone\[(\d)\]/)[1];
    if (number > 0) {
      for (const [name, v] of [["waveGroupType", 1], ["waveGroupID", 23]]) {
        const gp = `fm.pat.tone[${tone}].${name}`;
        if (this.get(gp) !== v) changes.push(this.set(gp, v));
      }
    }
    return changes;
  }

  name() {
    return this.get("fm.pat.common.patchName").trimEnd();
  }

  clone() {
    return new Patch(this.model, this.blocks);
  }

  // Copy every setting of tone `from` to tone `to` (0-based): the whole tone
  // block, plus that tone's key/velocity range in the TMT block. The tone
  // ON/OFF switch is left as it is. Returns {block: {address, data}, changes}
  // (the tone block is sent whole, like the Editor's effect-type changes).
  copyTone(from, to) {
    if (from === to) throw new Error("choose two different tones");
    const src = `tone[${from}]`, dst = `tone[${to}]`;
    this.blocks[dst] = Uint8Array.from(this.blocks[src]);
    const changes = [];
    for (const [path, p] of Object.entries(this.model.params)) {
      const m = path.match(/^fm\.pat\.tmt\.(tmt\w+)\[(\d)\]$/);
      if (!m || Number(m[2]) !== from || m[1] === "tmtToneSwitch") continue;
      changes.push(this.set(`fm.pat.tmt.${m[1]}[${to}]`, this.get(path), false));
    }
    return { block: { address: this.blockAddress(dst), data: Array.from(this.blocks[dst]) }, changes };
  }

  // Visible parameters that differ from `original`. Effect members count only
  // for the effect type active in either patch.
  diff(original) {
    const out = [];
    for (const [path, p] of Object.entries(this.model.params)) {
      if (p.hidden) continue;
      if (p.union && p.union[1] > 0) {
        const kind = p.union[0];
        if (this.effectType(kind) !== p.union[1] && original.effectType(kind) !== p.union[1]) continue;
      }
      const from = original.get(path);
      const to = this.get(path);
      if (from !== to) out.push({ path, label: p.label, from, to });
    }
    return out;
  }

  // An edit to fm.pat.tone[t].X applied to every tone in `tones` (0-based),
  // like Roland's Editor with several TONE SELECT buttons pressed.
  setLinked(path, value, tones) {
    const m = path.match(/^fm\.pat\.tone\[(\d)\]\.(.+)$/);
    const targets = m && tones.includes(Number(m[1])) ? tones : [m ? Number(m[1]) : null];
    const changes = [];
    for (const t of targets) {
      const p = m ? `fm.pat.tone[${t}].${m[2]}` : path;
      if (this.model.params[p].control === "wave") changes.push(...this.setWave(p, value));
      else changes.push(this.set(p, value));
    }
    return changes;
  }
}

const TONE_OUTPUT_MFX = 0;
const PATCH_OUTPUT = { MFX: 0, TONE: 13 };

// The signal path as data (for the routing diagram): which tones play, which
// go through the MFX, and every send/level on the way to the output.
export function signalPath(patch) {
  const g = (p) => patch.get(p);
  const name = (kind) => patch.model.effects[kind].types.find((t) => t.number === patch.effectType(kind))?.name;
  const pa = g("fm.pat.common.patchOutputAssign");
  const tones = [0, 1, 2, 3].map((t) => {
    const via = pa === PATCH_OUTPUT.MFX || (pa === PATCH_OUTPUT.TONE && g(`fm.pat.tone[${t}].toneOutputAssign`) === TONE_OUTPUT_MFX);
    const v = via ? "MFX" : "NonMFX";
    return { tone: t, on: !!g(`fm.pat.tmt.tmtToneSwitch[${t}]`), via,
             out: g(`fm.pat.tone[${t}].toneDrySendLevel`),
             cho: g(`fm.pat.tone[${t}].toneChorusSendLevel${v}`), rev: g(`fm.pat.tone[${t}].toneReverbSendLevel${v}`),
             wave: g(`fm.pat.tone[${t}].waveNumberL`) };
  });
  return {
    tones,
    mfx: { type: patch.effectType("mfx"), name: name("mfx"), out: g("fm.pat.mfx.mfxDrySendLevel"),
           cho: g("fm.pat.mfx.mfxChorusSendLevel"), rev: g("fm.pat.mfx.mfxReverbSendLevel") },
    chorus: { type: patch.effectType("chorus"), name: name("chorus"), level: g("fm.pat.cho.chorusLevel"),
              toMain: g("fm.pat.cho.chorusOutputSelect") <= 1, toReverb: g("fm.pat.cho.chorusOutputSelect") >= 1 },
    reverb: { type: patch.effectType("reverb"), name: name("reverb"), level: g("fm.pat.rev.reverbLevel") },
  };
}

// Why each effect unit is or isn't audible. Rules from the Editor manual
// (PATCH/TONE OUTPUT ASSIGN, sends, CHORUS OUTPUT SELECT), checked against the
// 256 factory patches: 252 are consistent, 4 have an unused reverb.
export function routing(patch, setup = null) {
  const g = (p) => patch.get(p);
  const typeName = (kind) => patch.model.effects[kind].types.find((t) => t.number === patch.effectType(kind))?.name;
  const active = [0, 1, 2, 3].filter((t) => g(`fm.pat.tmt.tmtToneSwitch[${t}]`));
  const pa = g("fm.pat.common.patchOutputAssign");
  const viaMfx = (t) => pa === PATCH_OUTPUT.MFX || (pa === PATCH_OUTPUT.TONE && g(`fm.pat.tone[${t}].toneOutputAssign`) === TONE_OUTPUT_MFX);
  const send = (t, unit) => g(`fm.pat.tone[${t}].tone${unit}SendLevel${viaMfx(t) ? "MFX" : "NonMFX"}`);
  const anyVia = active.some(viaMfx);
  const out = [];
  const add = (level, unit, text) => out.push({ level, unit, text });
  const switchOff = (name) => setup && setup[name] === 0;
  if (!active.length) add("warn", "patch", "No tone is switched on (TMT tab, TONE SWITCH): the patch is silent.");

  // MFX
  const mfx = patch.effectType("mfx");
  const mfxAudible = mfx !== 0 && anyVia && g("fm.pat.mfx.mfxDrySendLevel") > 0;
  if (mfx === 0) add("info", "mfx", "MFX is THROUGH (no multi-effect).");
  else if (!anyVia) add("warn", "mfx", `MFX ${typeName("mfx")} is unheard: no active tone is routed to the MFX (OUTPUT ASSIGN).`);
  else if (!mfxAudible) add("warn", "mfx", `MFX ${typeName("mfx")}: its OUTPUT LEVEL is 0, so only its chorus/reverb sends are heard.`);
  else add("ok", "mfx", `MFX ${typeName("mfx")} is in the signal path (${active.filter(viaMfx).map((t) => `Tone ${t + 1}`).join(", ")}).`);
  if (switchOff("mfx1Switch")) add("warn", "mfx", "MFX is switched off in the synth's Setup (not stored in the patch).");

  // Chorus
  const cho = patch.effectType("chorus");
  const choFeeds = active.filter((t) => send(t, "Chorus") > 0).map((t) => `Tone ${t + 1}`);
  if (anyVia && g("fm.pat.mfx.mfxChorusSendLevel") > 0) choFeeds.push("MFX CHORUS SEND");
  const choAudible = cho !== 0 && g("fm.pat.cho.chorusLevel") > 0 && choFeeds.length > 0;
  if (cho === 0) add("info", "chorus", "Chorus is OFF.");
  else if (g("fm.pat.cho.chorusLevel") === 0) add("warn", "chorus", `Chorus ${typeName("chorus")} is inaudible: CHORUS LEVEL is 0.`);
  else if (!choFeeds.length) add("warn", "chorus", `Chorus ${typeName("chorus")} is inaudible: no tone sends to it (tone CHO sends are 0) and the MFX CHORUS SEND LEVEL is 0 or no tone goes through the MFX.`);
  else add("ok", "chorus", `Chorus ${typeName("chorus")} is fed by ${choFeeds.join(", ")}.`);
  if (switchOff("chorusSwitch")) add("warn", "chorus", "Chorus is switched off in the synth's Setup (not stored in the patch).");

  // Reverb
  const rev = patch.effectType("reverb");
  const revFeeds = active.filter((t) => send(t, "Reverb") > 0).map((t) => `Tone ${t + 1}`);
  if (anyVia && g("fm.pat.mfx.mfxReverbSendLevel") > 0) revFeeds.push("MFX REVERB SEND");
  const choSel = g("fm.pat.cho.chorusOutputSelect"); // MAIN, MAIN+REV, REV
  if (choAudible && choSel >= 1) revFeeds.push("the chorus (CHORUS OUTPUT SELECT)");
  if (rev === 0) add("info", "reverb", "Reverb is OFF.");
  else if (g("fm.pat.rev.reverbLevel") === 0) add("warn", "reverb", `Reverb ${typeName("reverb")} is inaudible: REVERB LEVEL is 0.`);
  else if (!revFeeds.length) {
    const sends = active.map((t) => `Tone ${t + 1} REV send ${send(t, "Reverb")}`).join(", ");
    add("warn", "reverb", `Reverb ${typeName("reverb")} is inaudible: nothing is sent to it (${sends}; MFX REVERB SEND LEVEL ${g("fm.pat.mfx.mfxReverbSendLevel")}; chorus not routed to reverb).`);
  } else add("ok", "reverb", `Reverb ${typeName("reverb")} (level ${g("fm.pat.rev.reverbLevel")}) is fed by ${revFeeds.join(", ")}.`);
  if (switchOff("reverbSwitch")) add("warn", "reverb", "Reverb is switched off in the synth's Setup (not stored in the patch).");
  return out;
}

// Display text for a raw value (enum label, or number with the Editor's offset).
export function display(p, raw, waves) {
  if (p.control === "wave") return raw === 0 ? "0: OFF" : `${raw}: ${waves[raw - 1] ?? "?"}`;
  if (p.enum) {
    const i = p.enumValues ? p.enumValues.indexOf(raw) : raw - (p.range ? p.range[0] : 0);
    if (i >= 0 && i < p.enum.length) return p.enum[i];
    return String(raw);
  }
  if (p.displayOffset != null) {
    const v = raw + p.displayOffset;
    return v > 0 && p.range && p.range[0] + p.displayOffset < 0 ? `+${v}` : String(v);
  }
  return String(raw);
}

// [raw, label] pairs for a select control.
export function options(p) {
  if (!p.enum) return [];
  return p.enum.map((label, i) => [p.enumValues ? p.enumValues[i] : (p.range ? p.range[0] : 0) + i, label]);
}
