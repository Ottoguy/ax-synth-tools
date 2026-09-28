// Roland AX-Synth SysEx: a port of src/axsynth/sysex.py + the value codec
// of src/axsynth/schema.py. Builds and parses bytes only; midi.js sends them.
//
// SAFETY: buildDT1 refuses every address outside the volatile Temporary
// Patch (1F 00 00 00 .. end of Tone 4). Stored sounds (30 ..), System (02 ..),
// Setup (01 ..) and the undocumented command area (0F ..) cannot be written
// from this app. RQ1 (read requests) are allowed on Temporary, User patches,
// Setup and System only.

export const ROLAND = 0x41;
export const MODEL_ID = [0x00, 0x00, 0x3c];
export const DEVICE = 0x10;
export const RQ1 = 0x11;
export const DT1 = 0x12;

export function addrToInt(bytes) {
  return bytes.reduce((v, b) => v * 128 + b, 0);
}

export function intToAddr(n, width = 4) {
  const out = new Array(width).fill(0);
  for (let i = width - 1; i >= 0; i--) {
    out[i] = n % 128;
    n = Math.floor(n / 128);
  }
  if (n) throw new Error("address out of range");
  return out;
}

export const hex = (bytes) => Array.from(bytes, (b) => b.toString(16).toUpperCase().padStart(2, "0")).join(" ");

export const TEMPORARY_PATCH = addrToInt([0x1f, 0, 0, 0]);
const TEMPORARY_END = addrToInt([0x1f, 0, 0x26, 0]) + 154; // exclusive: end of Tone 4
const USER_FIRST = addrToInt([0x30, 0, 0, 0]);
const USER_END = addrToInt([0x31, 0x7f, 0x26, 0]) + 154;
const READ_AREAS = [
  [addrToInt([0x01, 0, 0, 0]), addrToInt([0x01, 0, 0, 0x34])], // Setup
  [addrToInt([0x02, 0, 0, 0]), addrToInt([0x02, 0, 0x40, 0x50])], // System
  [TEMPORARY_PATCH, TEMPORARY_END],
  [USER_FIRST, USER_END],
];

export function checksum(body) {
  return (128 - (body.reduce((a, b) => a + b, 0) % 128)) % 128;
}

export function isWritable(address, length) {
  return address >= TEMPORARY_PATCH && address + length <= TEMPORARY_END;
}

export function buildDT1(address, data) {
  if (!isWritable(address, data.length)) {
    throw new Error(`refused: DT1 to ${hex(intToAddr(address))} is outside the Temporary Patch`);
  }
  if (data.some((b) => b > 0x7f)) throw new Error("DT1 data bytes must be 7-bit");
  const body = [...intToAddr(address), ...data];
  return Uint8Array.from([0xf0, ROLAND, DEVICE, ...MODEL_ID, DT1, ...body, checksum(body), 0xf7]);
}

// Storing into a memory slot (user request 2026-09-28): the ONLY write outside
// the Temporary Patch. Allowed: one whole patch block of User patch n (0..255),
// exactly as Roland's Librarian export writes them (dumps/). Everything else
// (partial blocks, other areas) is refused.
export const PATCH_BLOCK_LAYOUT = [ // [offset within a patch (base-128 int), size]
  [addrToInt([0x00, 0x00, 0x00]), 79], [addrToInt([0x00, 0x02, 0x00]), 145], [addrToInt([0x00, 0x04, 0x00]), 84],
  [addrToInt([0x00, 0x06, 0x00]), 83], [addrToInt([0x00, 0x10, 0x00]), 41], [addrToInt([0x00, 0x20, 0x00]), 154],
  [addrToInt([0x00, 0x22, 0x00]), 154], [addrToInt([0x00, 0x24, 0x00]), 154], [addrToInt([0x00, 0x26, 0x00]), 154],
];
export function buildUserPatchDT1(n, blockOffset, data) {
  if (!Number.isInteger(n) || n < 0 || n > 255) throw new Error("refused: memory slot must be 0..255");
  const blk = PATCH_BLOCK_LAYOUT.find(([o]) => o === blockOffset);
  if (!blk || data.length !== blk[1]) throw new Error("refused: only whole patch blocks can be stored");
  if (data.some((b) => b > 0x7f)) throw new Error("DT1 data bytes must be 7-bit");
  const body = [...intToAddr(userPatchAddress(n) + blockOffset), ...data];
  return Uint8Array.from([0xf0, ROLAND, DEVICE, ...MODEL_ID, DT1, ...body, checksum(body), 0xf7]);
}

export function buildRQ1(address, size) {
  if (!READ_AREAS.some(([a, b]) => address >= a && address + size <= b)) {
    throw new Error(`refused: RQ1 ${hex(intToAddr(address))} size ${size} is outside the known read areas`);
  }
  const body = [...intToAddr(address), ...intToAddr(size)];
  return Uint8Array.from([0xf0, ROLAND, DEVICE, ...MODEL_ID, RQ1, ...body, checksum(body), 0xf7]);
}

export const identityRequest = () => Uint8Array.from([0xf0, 0x7e, DEVICE, 0x06, 0x01, 0xf7]);

// Parse one F0..F7 Roland message with the 3-byte AX-Synth model ID.
export function parse(msg) {
  const m = Array.from(msg);
  if (m[0] !== 0xf0 || m[m.length - 1] !== 0xf7 || m[1] !== ROLAND) return null;
  if (m[3] !== MODEL_ID[0] || m[4] !== MODEL_ID[1] || m[5] !== MODEL_ID[2]) return null;
  const body = m.slice(7, -2);
  return {
    device: m[2], command: m[6], address: addrToInt(body.slice(0, 4)), payload: body.slice(4),
    checksumOk: checksum(body) === m[m.length - 2],
  };
}

export function splitSysex(bytes) {
  const out = [];
  let cur = null;
  for (const b of bytes) {
    if (b === 0xf0) cur = [b];
    else if (cur) {
      cur.push(b);
      if (b === 0xf7) { out.push(Uint8Array.from(cur)); cur = null; }
    }
  }
  return out;
}

// --- value codec (schema.py: int<W>x<B> = W wire bytes x B low bits, MSB first)
function bitsOf(type) {
  const m = /^int(\d+)x(\d+)$/.exec(type);
  if (!m) throw new Error(`unknown type ${type}`);
  return [Number(m[1]), Number(m[2])];
}

export function encodeValue(p, value, checkRange = true) {
  if (p.type === "string") {
    const s = String(value).padEnd(p.size, " ").slice(0, p.size);
    const codes = Array.from(s, (c) => c.charCodeAt(0));
    if (codes.some((c) => c < 32 || c > 127)) throw new Error("characters must be ASCII 32..127");
    return codes;
  }
  const [n, bits] = bitsOf(p.type);
  if (checkRange && p.range && (value < p.range[0] || value > p.range[1])) {
    throw new Error(`${value} outside ${p.range}`);
  }
  if (Math.floor(value / 2 ** (n * bits)) !== 0) throw new Error(`${value} does not fit ${p.type}`);
  const out = [];
  for (let i = 0; i < n; i++) out.push(Math.floor(value / 2 ** (bits * (n - 1 - i))) % 2 ** bits);
  return out;
}

export function decodeValue(p, bytes) {
  if (p.type === "string") return String.fromCharCode(...bytes);
  const [, bits] = bitsOf(p.type);
  return bytes.reduce((v, b) => v * 2 ** bits + (b % 2 ** bits), 0);
}

// --- whole patch: 9 blocks, Roland's order (sysex.PATCH_BLOCKS)
export function patchMessages(model, blocks) {
  return model.blocks.map((b) => buildDT1(model.meta.temporaryPatch + b.offset, Array.from(blocks[b.name])));
}

// Inverse: collect whole-block DT1s addressed to the Temporary Patch.
export function temporaryBlocks(model, messages) {
  const out = {};
  for (const msg of messages) {
    const r = parse(msg);
    if (!r || r.command !== DT1 || !r.checksumOk) continue;
    const b = model.blocks.find((x) => model.meta.temporaryPatch + x.offset === r.address);
    if (b && r.payload.length === b.size) out[b.name] = Uint8Array.from(r.payload);
  }
  return out;
}

export function userPatchAddress(n) {
  if (!(n >= 0 && n <= 255)) throw new Error("user patch number must be 0..255");
  return USER_FIRST + n * addrToInt([0x01, 0x00, 0x00]);
}
