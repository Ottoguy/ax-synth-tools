// Web MIDI connection to the AX-Synth: identity check, paced sending, RQ1
// request/reply. Every outgoing Roland message is built by sysex.js, whose
// DT1 builder only allows the Temporary Patch.
import { DT1, hex, identityRequest, intToAddr, parse, buildRQ1 } from "./sysex.js";

const PORT_NAME = /ax-?synth/i; // Windows shows "Roland AX-Synth" (captures/setup.md)

export class Synth {
  constructor(log) {
    this.log = log;
    this.access = null;
    this.input = null;
    this.output = null;
    this.queue = [];
    this.busy = false;
    this.waiters = [];
    this.lastSend = 0;
  }

  async connect(identityReply) {
    if (!navigator.requestMIDIAccess) throw new Error("This browser has no Web MIDI. Use Microsoft Edge or Chrome.");
    this.access = await navigator.requestMIDIAccess({ sysex: true });
    const ins = [...this.access.inputs.values()];
    const outs = [...this.access.outputs.values()];
    this.log(`MIDI ports: in [${ins.map((p) => p.name).join(", ")}] out [${outs.map((p) => p.name).join(", ")}]`);
    this.input = ins.find((p) => PORT_NAME.test(p.name));
    this.output = outs.find((p) => PORT_NAME.test(p.name));
    if (!this.input || !this.output) {
      throw new Error("AX-Synth not found. Is it switched on and connected by USB, and are MIDI-OX, the Roland Editor and the Librarian closed?");
    }
    await this.input.open();
    await this.output.open();
    this.input.onmidimessage = (e) => this.receive(e.data);
    const reply = await this.exchange(identityRequest(), (m) => m[1] === 0x7e && m[3] === 0x06 && m[4] === 0x02, 1000);
    const expected = hex(identityReply);
    if (hex(reply) !== expected) this.log(`note: Identity Reply ${hex(reply)} differs from the documented ${expected}`);
    return reply;
  }

  receive(data) {
    const msg = Uint8Array.from(data);
    if (msg[0] !== 0xf0) return; // ignore notes/CCs from playing
    this.log(`← ${describe(msg)}`);
    const i = this.waiters.findIndex((w) => w.match(msg));
    if (i >= 0) {
      const [w] = this.waiters.splice(i, 1);
      clearTimeout(w.timer);
      w.resolve(msg);
    }
  }

  // Send in order, at least `gap` ms after the previous message.
  send(msg, gap = 20) {
    return new Promise((resolve, reject) => {
      this.queue.push({ msg, gap, resolve, reject });
      this.pump();
    });
  }

  async pump() {
    if (this.busy) return;
    this.busy = true;
    while (this.queue.length) {
      const { msg, gap, resolve, reject } = this.queue.shift();
      const wait = this.lastSend + gap - performance.now();
      if (wait > 0) await new Promise((r) => setTimeout(r, wait));
      try {
        if (!this.output) throw new Error("not connected");
        this.output.send(msg);
        this.lastSend = performance.now();
        this.log(`→ ${describe(msg)}`);
        resolve();
      } catch (e) {
        reject(e);
      }
    }
    this.busy = false;
  }

  exchange(msg, match, timeout = 800) {
    return new Promise((resolve, reject) => {
      const w = { match, resolve };
      w.timer = setTimeout(() => {
        this.waiters.splice(this.waiters.indexOf(w), 1);
        reject(new Error(`no reply to ${describe(msg)} within ${timeout} ms`));
      }, timeout);
      this.waiters.push(w);
      this.send(msg).catch(reject);
    });
  }

  // RQ1 -> the synth answers with one DT1 of exactly that address and size
  // (captures/mitm, captures/rq1). Returns the payload bytes.
  async request(address, size) {
    const reply = await this.exchange(buildRQ1(address, size), (m) => {
      const r = parse(m);
      return r && r.command === DT1 && r.address === address;
    });
    const r = parse(reply);
    if (!r.checksumOk || r.payload.length !== size) throw new Error(`bad reply to RQ1 ${hex(intToAddr(address))}`);
    return Uint8Array.from(r.payload);
  }
}

export function describe(msg) {
  const r = parse(msg);
  if (!r) return hex(msg);
  const kind = { 0x11: "RQ1", 0x12: "DT1" }[r.command] || `cmd ${r.command}`;
  const extra = r.command === 0x11 ? `size ${r.payload.reduce((v, b) => v * 128 + b, 0)}` : `${r.payload.length} B`;
  return `${kind} ${hex(intToAddr(r.address))} ${extra}${r.checksumOk ? "" : " BAD CHECKSUM"}`;
}
