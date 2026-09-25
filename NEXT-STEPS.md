# Next steps for you

**Goal:** you describe a sound to an LLM, and your AX-Synth ends up with a patch that sounds like it. Along the way there will be a simple GUI with a handful of meaningful controls instead of the Editor's 800+ parameters.

**Where we are:** the whole data model is decoded and checked against Roland's docs, Roland's own export files, two real patches, the Owner's Manual, and (step 2) the Editor's own live messages, which our code reproduces byte for byte (`research/REPORT.md`). There is now also a **sound-design knowledge base** built from all 63 parts of *Synth Secrets*: which settings make a sound bright, hollow, breathy, brassy, bell-like…, plus 35 instrument recipes mapped onto the AX-Synth (`knowledge/sound-design/`). It hasn't been checked by ear yet; that's what your listening steps are for. We also have the list of all 256 factory sounds (`research/generated/factory-tones.csv`) and Roland's parameter and effect explanations (Editor manual). What's missing is almost entirely things only you can do: **real hardware, your ears, and your preferences.**

**Two facts about the AX-Synth that shape everything below** (Owner's Manual):
- Its display has **3 characters**. It can't show patch names, wave names or values, so checks go through the **Editor (READ)** or a SysEx dump.
- The synth's own **[WRITE] button can't store sound edits**. It stores favorites and system settings only. Sounds are stored by the Editor/Librarian.

---

## The safety rules (read once, apply always)

1. **Back up first.** Do the backup in step 3.1 before *anything* except read requests is sent to the synth.
2. **Only send to the Temporary Patch.** Every file I prepare for you to send targets `1F 00 00 00`, the working copy the synth throws away when you switch sounds or power off. The `*-temporary.syx` files are safe.
3. **Never play `dumps/AX-Synth Librarian Clean export.mid` to the synth.** It would overwrite all 256 sounds with INIT PATCH. (Safety net: a factory reset restores the factory sounds, but not your own edits. Owner's Manual p.34.)
4. **Never send anything I haven't prepared or named** as safe. Don't use WRITE in the Editor/Librarian, the synth's Bulk Dump *receive* mode, or factory reset unless a step asks for it.
5. When in doubt, stop and tell me. A wrong read costs nothing, and a wrong write costs your sounds.

---

## Step 0: Your setup ✅ done (2026-09-25)

Your answers are in `captures/setup.md`. What they mean:

- **USB cable directly, driver mode "Gen", port "Roland AX-Synth".** With Windows' own driver, only one program can use the synth's port at a time. Roland's Editor manual (p.8) warns that the Editor and Librarian may not both work over it. That's exactly why step 3.0 puts MIDI-OX in the middle: MIDI-OX is the only program that opens "Roland AX-Synth", and the Editor and Librarian talk to MIDI-OX. **Don't change the driver mode.** Roland's own driver (Uen) only exists for Windows up to 8, so it's a last resort.
- **Firmware 2.01.** This is newer than every document we have: the manuals from 2009, the MIDI Implementation v1.00 from 2010 and the Editor/Librarian v1.00. Roland never published a firmware update, so your synth probably came from the factory with 2.01. It probably changes little, but three things are now worth watching in step 3:
  - The synth's answer to the Editor's "who's there?" question may report a different version than Roland's document. My log tool now decodes the answer and prints any difference.
  - If the Editor refuses to READ even with the synth connected, the version check could be the reason. Tell me the exact error.
  - The stored sounds and the data layout could differ slightly from the 2009 documents. The backup will show this.
- **Possibly overwritten sounds (second hand).** No problem. When I get the backup, I'll compare all 256 names with the factory list and mark any slot that differs, so the AI never mistakes an old owner's sound for a factory one.
- *Still unknown, optional:* your MIDI channel. It doesn't matter for anything we send (SysEx), and the factory default is 1.

---

## Step 1: Documents ✅ mostly done

- [x] Owner's Manual: done (`docs/AX-Synth_OM.pdf`). It gave us the **factory sound list**. Correction to what I said earlier: the *parameter explanations* weren't in it; they were already in the **Editor manual** we had (parameter guide p.9–43, effects list p.44–78).
- [x] Those explanations are now extracted into the **knowledge base** (`knowledge/knowledge.md` to read; `knowledge.json` for the AI).
- [ ] **Erratum 1**, if it exists (we have "Erratum2").
- [ ] *(Optional)* The **Juno-Di or Juno-D Editor** installer from Roland's site. It's the closest sibling instrument. Its `Script.xml` may explain the patch-write handshake we still don't understand. Put the installed files in `reference/juno-editor/`.

---

## Step 2: Capture the Editor's live traffic, no synth needed ✅ done (2026-09-23)

Your 8 logs are in `captures/live/`. I renamed them from `*.txt.txt` to `*.txt` and wrote `captures/live/notes.md` from your report. The full analysis is in `research/live-capture-analysis.md`. What they showed:

- **Turning a knob sends one small message for that value only**, immediately and without any waiting. Our code builds **exactly the same bytes** for every value you changed (cutoff, name, the STEP PITCH SHIFTER values, Master Tune, Beam Range). The drags with several steps were fine: every step is a separate, correct message.
- **The `00 81` bug is harmless.** The Editor sends the correct address, the same one our model uses.
- **Changing the effect type sends the whole effect block** with Roland's default settings for the new effect. Our model reproduces that message exactly too. This matters later: when the AI picks an effect, it should start from those defaults.
- **The "Unable to read/write data." errors were expected.** Before READ, SYNC, WRITE or a Librarian read, the software first asks "who's there?" (an *Identity Request*). It waits 3 seconds, asks once more, and then gives up with that message. Without a synth nobody answers, so a loopback can't show more. Everything still unknown about READ/WRITE now needs the synth.
- **WRITE first asks for the name of memory slot 1-1**, using an ordinary read request on the stored-patch area. So reading names and patches from the synth's memory is a normal, read-only operation.
- `09-librarian-write` isn't needed: it would have stopped at the same question.

---

## Step 3: First contact with the synth, read-only (1–1.5 hours, mostly waiting)

Connect the synth.

### 3.0 Put MIDI-OX in the middle, so we see both directions (15 minutes, new)
Step 2 showed that the interesting part is the conversation between the software and the synth. MIDI-OX can pass the messages through and log both sides:

```
Editor/Librarian ──> loopMIDI "loopAX" ──> MIDI-OX ──> AX-Synth
Editor/Librarian <── loopMIDI "loopAX-back" <── MIDI-OX <── AX-Synth
```

1. In loopMIDI, add a second port, `loopAX-back`.
2. **Close the Editor and Librarian first**, because only one program can hold the synth's port (step 0). Then in MIDI-OX, *Options → MIDI Devices*: **inputs** `loopAX` + `Roland AX-Synth`; **outputs** `Roland AX-Synth` + `loopAX-back`.
3. *View → Port Routings*: keep **exactly two** connections, and delete any others MIDI-OX added automatically:
   - `loopAX` (in) → `Roland AX-Synth` (out)
   - `Roland AX-Synth` (in) → `loopAX-back` (out)

   ⚠ There must **never** be a route from `Roland AX-Synth` (in) to `Roland AX-Synth` (out): the synth's own data would be sent straight back into it. If unsure, send me a screenshot of the routing window before continuing.
4. Make sure *Options → Pass SysEx* is ticked, and keep the large SysEx buffers from step 2.
5. Editor and Librarian, *Setup → Set Up MIDI Devices*: **Output = `loopAX`, Input = `loopAX-back`**. (This also avoids the "Generic driver can't be shared between Editor and Librarian" problem, because only MIDI-OX opens the synth's port.)
6. Test: press **READ** in the Editor. If the error from step 2 is gone, the route works. If it still says "Unable to read/write data.", save the MIDI-OX log anyway as `captures/mitm/00-read-failed.txt`. It shows whether the synth answered and what version it reported, which tells us whether the problem is the routing or the Editor rejecting firmware 2.01.

If this setup gives you trouble, skip it: close MIDI-OX, connect the Editor (or the Librarian, **one at a time**) directly to `Roland AX-Synth` and do 3.1 without captures.

### 3.1 Capture the read conversation, then back up everything (do this before anything else is sent to the synth)
Clear the MIDI-OX log before each capture and save it afterwards, as in step 2:

- [ ] Librarian: **Read Selected** on one row (1-1) → `captures/mitm/01-librarian-read-selected.txt`
- [ ] Editor: **READ** → `captures/mitm/02-editor-read.txt` (reads the sound currently selected on the synth)
- [ ] Librarian: **Read All Data** (if you connected directly, close the Editor first). This *reads* all 256 sounds from the synth. The log isn't needed here, and it may be too long for MIDI-OX anyway.
- [ ] **Save** it as `captures/backup/ax-synth-backup-YYYY-MM-DD.a8l`.
- [ ] Also **File → Export SMF** to `captures/backup/ax-synth-backup-YYYY-MM-DD.mid`.
- [ ] Put a copy somewhere outside this project (cloud drive, USB stick).
- [ ] *After the backup:* Editor **SYNC** → `captures/mitm/03-editor-sync.txt`. SYNC sends the Editor's current sound into the synth's temporary working copy (lost when you switch sounds) and reads the name list. Switch sounds afterwards to get your stored sound back.
- [ ] Still **no WRITE** in the Editor or Librarian.
- [ ] One line per file in `captures/mitm/notes.md`, as before.

The backup file is also the **main dataset for the AI**: all 256 professionally designed sounds, which the LLM will use as starting points. It also lets me confirm that the synth's memory slots are in the same order as the factory sound list.

### 3.2 The synth's own Bulk Dump (second backup + a very useful capture, ~16 minutes)
The synth can send "all of its settings" by itself (Owner's Manual p.29). This shows *how the synth formats its own SysEx*, including areas nobody documented (favorites, system settings).
- [ ] Close the Editor and Librarian. In MIDI-OX, set the input to the synth and clear the SysEx view. If the step 3.0 routing is still active, **remove it first** (or at least check that nothing routes the AX-Synth input to the AX-Synth output).
- [ ] Switch the synth off. Hold **VARIATION [–] + [+] + TONE [6] (STRINGS/PAD)** and switch on. The display shows **"dMP"**.
- [ ] Press **FAVORITE [B]** (= *send*; display "Snd"). **Do not press [A]**: [A] is *receive* mode.
- [ ] Wait until **"dNE"** (about 16 minutes). Save the capture as `captures/bulkdump/bulkdump-YYYY-MM-DD.syx`.
- [ ] Switch the synth off and on again.

### 3.3 Read-only request test (checks our own SysEx code against the real synth)
- [ ] Select **LEAD GUITAR** (family button), **variation 1**. That's factory "SearingGtr 1", the sound the forum patches were made from.
- [ ] In MIDI-OX: *SysEx → Send/Receive SysEx*, load `research/generated/experiment-rq1-temporary-patch.syx`, and send it with the input set to the synth. Save everything received as `captures/rq1/reply.syx`. (These are *requests*; they change nothing.)
- [ ] Now, **without storing anything**: hold [SHIFT], press the lit LEAD GUITAR button until "UOl" appears, and lower the volume a few steps with VARIATION [–]. Release [SHIFT] and **don't press WRITE**. Send the same requests again and save as `captures/rq1/reply-after-volume.syx`. This shows where the synth keeps that setting.
- [ ] Switch to another sound and back (this discards the volume change).
- [ ] Note in `captures/rq1/notes.md` what you did, how many messages came back each time, and any errors.

### 3.4 Describe sounds in your own words (your ears are the scarce resource)
Take `research/generated/factory-tones.csv` and play through about **20–40 factory sounds from different families** (you select them with the family button + variation number). For each, add a line to `captures/factory/descriptions.md`:

*`Strings/Pad 23 Shimmer Pad — slow bright attack, glassy, wide, lots of movement; great for ambient intros`*

Write the way you'd describe a sound to the LLM later. These lines become the **language ↔ sound** examples the AI learns from. Any words are fine; they'll be matched against the descriptor vocabulary in `knowledge/sound-design/sound-design.md` (bright, warm, hollow, breathy, punchy, lush, metallic, …), and your words will extend it. You don't need to save any files here: step 3.1 already captured all the sounds.

Also note whether the **SuperNATURAL** and **SPECIAL** sounds can be read by the Editor at all.

---

## Step 4: First write, Temporary only (15 minutes)

Only after step 3.1 is done.

- [ ] In MIDI-OX, set a **delay between messages** of at least **25 ms** (Options → SysEx → "Delay after F7"; Roland's own software uses about 20 ms plus transmission time).
- [ ] Send `research/generated/guitar01-temporary.syx` (the forum patch, encoded by *our* code, to the Temporary patch only).
- [ ] Check and write down in `captures/first-write/notes.md`:
  - Does it sound like a **metal lead guitar**, different from the factory SearingGtr 1?
  - Soft notes (velocity below ~70): does an extra high pure tone appear?
  - Pitch bend on the ribbon: **2 octaves down, 1 up**?
  - Press the D-Beam **[ASSIGNABLE]** button and wave your hand. Does it change the sound? (The patch expects **CC70**. To set it, hold [SHIFT] + [ASSIGNABLE], choose "C70", then [WRITE]. This changes a *system* setting, so note the old value "C__" first so you can set it back.)
  - In the **Editor**, press **READ**. Does it show the name **"SearingGtr 1"**, and does **Tone 1's wave** read **"Overdrive Gt"**? (This confirms our wave numbering.)
- [ ] Switch to another sound and back. The stored factory sound should be unchanged (Temporary is volatile).

After this I'll prepare a small **listening test**: a few `.syx` files that each change one thing (cutoff, attack, reverb…) so you can confirm by ear that each parameter does what the model says.

---

## Step 5: Decisions only you can make

Answer these in `captures/decisions.md`. Rough answers are fine, and you can change your mind later.

**The GUI**
1. **Where should it run?** (a) a **web page** in Chrome/Edge that talks to the synth directly via Web MIDI (no install, and it can be published as a link), (b) a **desktop app** (Python), (c) no preference. My default recommendation is (a).
2. **Which "big knobs" do you want?** Pick or add from: brightness, warmth, attack (soft ↔ percussive), release/length, sustain, body/thickness, detune/width, movement/vibrato, grit/distortion, space (reverb), echo (delay), octave/layering, mono/poly/glide, velocity sensitivity, "age"/lo-fi. Which 6–10 matter most for how you play?
3. Should the GUI also let you **pick a factory sound as a starting point** and then adjust the big knobs? (I think this gives much better results than starting from INIT.)
4. **Which performance controls do you actually use**, and what should they do in *new* sounds by default? The AX-Synth has: the **mod bar** (usually vibrato), the **AFTER TOUCH knob** (the keys send no aftertouch), the **ribbon** (pitch bend), the **D-Beam** (pitch, filter, or an assigned CC), **portamento** and **hold**.

**The LLM**

5. Which assistant do you want in the loop: **Claude via the API** (needs an API key, costs a little per request), **Claude here in Claude Code** (I generate the patch and you send it), or both?
6. Is it fine for the LLM to **start from the nearest factory sound and edit it**, rather than build every sound from scratch? (This is my recommendation.)
7. Should the app ever **store sounds into the synth's memory slots** by itself? Or should it always load them into the **Temporary** patch, and you store the keepers yourself (the app would ask for explicit confirmation and the target slot)? My recommendation is the latter.

**Your sounds**

8. Write **15–30 example requests** you would actually type, in your own words, for example:
   - "fat 80s brass stab for a synth-pop chorus"
   - "glassy bell pad with slow shimmer"
   - "screaming mono lead like a guitar solo, with pitch bend"
   These become the **test set** for judging whether the AI does a good job.
9. Styles/genres you mostly play, and anything you **don't** want (e.g. "never too quiet", "no huge reverb").

---

## Step 6: Optional, but valuable

- [ ] **More patches with descriptions**: any `.a8e`, `.a8l` or `.syx` AX-Synth patches you find online, especially with text describing the sound. Put them in `patches/` with a `.txt` of the description next to each.
- [ ] **Audio recordings**: later, short recordings (a few notes and a chord, WAV) of sounds. This makes it possible to check automatically whether a generated sound matches its description. Not needed yet.
- [ ] **Juno-D/Juno-Di or Fantom-X material**: the AX-Synth's sounds are "derived from Roland's latest synthesizers" of that era and use the same engine family, so tutorials on programming those synths apply almost 1:1.

---

## How to hand things back to me

- Put everything under `captures/` with the file names above, plus a `notes.md` per folder.
- Folder names so far: `captures/live/` (step 2, done), `captures/mitm/` and `captures/backup/` (3.1), `captures/bulkdump/`, `captures/rq1/`, `captures/factory/`, `captures/first-write/`.
- Then just tell me "step N done". I'll read the files, decode them, update the research and tests, and prepare the next step.

## What I'll build with it (for orientation)

1. **Hardware-verified model**: confirm or fix the open questions (steps 2–4).
2. **Safe sender**: a small tool that loads any patch into the Temporary patch with correct pacing, and can never touch memory slots unless explicitly told to.
3. **Sound corpus + meaning layer**: the 256 factory sounds, your descriptions, Roland's parameter/effect explanations (Editor manual, done), and the general sound-design knowledge from *Synth Secrets* (done, `knowledge/sound-design/`). On top of that, the big-knob **macro** layer. The patch format already has some built-in candidates: patch-wide cutoff, resonance, attack, release and velocity offsets.
4. **Simple GUI** with those macros, a factory-sound picker, and "send to synth".
5. **LLM integration**: you describe the sound, the LLM picks the nearest factory sound and sets the macros (and, when needed, specific parameters), the model validates every value, and the result goes to the Temporary patch. You listen, say "brighter" or "less reverb", and it adjusts.
