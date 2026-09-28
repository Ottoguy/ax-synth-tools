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
