# Next steps for you

**Goal:** you describe a sound to an LLM, and your AX-Synth ends up with a patch that sounds like it. Along the way there will be a simple GUI with a handful of meaningful controls instead of the Editor's 800+ parameters.

**Where we are:** the whole data model is decoded and checked against Roland's docs, Roland's own export files, two real patches, the Owner's Manual, and (step 2) the Editor's own live messages, which our code reproduces byte for byte (`research/REPORT.md`). **Since steps 3.1–3.3 it is also checked against your real synth:** we've seen the complete read conversation, our own read requests work, and your backup and the synth's own memory dump agree byte for byte. The factory-sound order and the wave list are confirmed, and the Editor's model covers everything the synth stores for a sound (`research/generated/user-patches.csv` lists every sound with its waves and effects). **Next is the first write (step 4).** There is now also a **sound-design knowledge base** built from all 63 parts of *Synth Secrets*: which settings make a sound bright, hollow, breathy, brassy, bell-like…, plus 35 instrument recipes mapped onto the AX-Synth (`knowledge/sound-design/`). It hasn't been checked by ear yet; that's what your listening steps are for. We also have the list of all 256 factory sounds (`research/generated/factory-tones.csv`) and Roland's parameter and effect explanations (Editor manual). What's missing is almost entirely things only you can do: **real hardware, your ears, and your preferences.**

**Two facts about the AX-Synth that shape everything below** (Owner's Manual):
- Its display has **3 characters**. It can't show patch names, wave names or values, so checks go through the **Editor (READ)** or a SysEx dump.
- The synth's own **[WRITE] button can't store sound edits**. It stores favorites and system settings only. Sounds are stored by the Editor/Librarian.

---

## The safety rules (read once, apply always)

1. **Back up first.** Do the backup in step 3.1 before *anything* except read requests is sent to the synth.
2. **Only send to the Temporary Patch.** Every file I prepare for you to send targets `1F 00 00 00`, the working copy the synth throws away when you switch sounds or power off. The `*-temporary.syx` files are safe.
3. **Never play `dumps/AX-Synth Librarian Clean export.mid` to the synth.** It would overwrite all 256 sounds with INIT PATCH. (Safety net: a factory reset restores the factory sounds, but not your own edits. Owner's Manual p.34.)
4. **Never send anything I haven't prepared or named** as safe. Don't use WRITE or SYNC in the Editor, Write in the Librarian, the synth's Bulk Dump *receive* mode, or factory reset unless a step asks for it. (SYNC also overwrites the synth's system settings.)
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

## Step 3: First contact with the synth, read-only

### 3.0 + 3.1 MIDI-OX in the middle, captures and backup ✅ done (2026-09-26)

Your three logs are in `captures/mitm/` (renamed from `*.txt.txt`, with `notes.md` written for you), and the backup is in `captures/backup/`. The full analysis is in `research/mitm-capture-analysis.md`. What they showed:

- **The MIDI-OX route works, and your firmware 2.01 is no problem.** The synth answers "who's there?" exactly as Roland's 2010 document says, and the Editor and Librarian accept it.
- **Reading is simple.** For each part of a sound the software asks once, and the synth answers with exactly that part a few milliseconds later. There's no splitting into packets and no special handshake. Our own code builds the same requests.
- **Your backup is complete and good:** all 256 sounds, all checksums valid.
  - **254 of 256 names match the factory list**, in the expected order, so the memory-slot ↔ factory-sound mapping is now confirmed.
  - The two exceptions are Bass 10 and 11 (printed "Reso Bs 2"/"Reso Bs 3"), stored as "Reso Bs 1"/"Reso Bs 2". They're real, distinct sounds, so they're either a Roland naming quirk or a previous owner's touch. Either way, nothing to worry about.
- **Our wave list is confirmed.** Every factory sound uses the waves its name suggests (Soprano Sax → "Sop Sax" waves, Folk Gtr → "Ac.Gtr", Steel Drums → "Steel Drums"…).
- **The forum guitar patches are factory SearingGtr 1 plus exactly the edits their author described.** Comparing them with your backup shows every changed setting: bend range, the CC70 "feedback" routing, the extra soft-note tone, and so on.
- **One surprise:** when the Editor READ, the synth's working copy held the Editor's blank "INIT PATCH", plus the Editor's default Setup/System settings. That was probably caused by an earlier SYNC, or an automatic send while you were testing 3.0. It doesn't affect your 256 stored sounds. **But SYNC also sends the Editor's system settings** (MIDI channel, D-Beam assignment, velocity curve, master tune) to the synth. So from now on: **don't press SYNC** unless a step asks for it. If a system setting on the synth seems changed, that's the likely reason; set it back on the panel.

**About the `.a8l` file (you asked).** The Librarian can only *save* a Library Window. The Main Window, which you read into, isn't one (Librarian manual p.5–6). If you want the `.a8l` (optional, since your `.mid` already holds the same sounds):
1. Click inside the **Main Window** (the one with your 256 sounds).
2. **File → Duplicate**. This opens a new Library Window with a copy of all 256 sounds.
3. With that new window active: **File → Save As** → `captures/backup/ax-synth-backup-2026-09-26.a8l`.

It's a nice extra check of the file format, but not required. **Do put a copy of the `.mid` outside this project** (cloud drive, USB stick) if you haven't yet. ⚠ That `.mid` is a full *restore* file: playing it to the synth rewrites all 256 memory slots, so use it only when you deliberately want to restore.

### 3.1b ~~Re-check~~: no longer needed
Step 3.3 already answered it: the working copy does follow the sound you pick on the synth. With LEAD GUITAR 1 selected, it was byte for byte your stored SearingGtr 1. So the "INIT PATCH" in 3.1 came from something sent earlier, most likely a SYNC while testing 3.0.

### 3.2 The synth's own Bulk Dump ✅ done (2026-09-26)
Your file is in `captures/bulkdump/` (renamed from `.sysx.syx`). The analysis is in `research/bulkdump-analysis.md`.
- **It turned out to be a raw copy of the synth's memory**, not a list of sounds. I decoded it completely:
  - The patch area holds your 256 sounds in a compact, bit-packed form.
  - Rebuilt from it, **all 256 sounds are byte for byte identical to your Librarian backup**, so you now have two independent backups that agree.
  - It also proves that the Editor's data model covers *everything* the synth stores for a sound. There are no hidden sound parameters we'd be missing.
- **The 16 FAVORITE memories are in it too:** A1 GR300 Lead 1, A2 Saw Lead 1, A3 Hot Coffee, A4 Air Lead, A5 Modular Bs1, A6 SearingGtr 3, A7 MS1959 II, A8 Funk EGtr; B1 Wide SynBrs, B2 Harmonica, B3 Cosmic Rays, B4 Bustranza, B5 AX Dist Org1, B6 Phase Clavi, B7 Phase Stage, B8 Wurly EP. Each has its own volume and reverb send; B2, B7 and B8 are a bit louder.
- **Your system settings are the standard defaults:** 440 Hz, MIDI channel 1, normal velocity, D-Beam ASSIGNABLE = CC01.
- The 1-1 sound (AX Saw Lead) carries a small hidden difference that suggests it was sent to the synth over MIDI at some point, maybe by a previous owner. Its content is otherwise normal. Nothing to do.

### 3.3 Read-only request test ✅ done (2026-09-26)
`captures/rq1/`, with `notes.md` written for you.
- **Our own request file works on the real synth.** Every request got exactly the expected answer.
- It **settled an old question**: the synth's controller-settings block is 80 bytes, as Roland's MIDI document says; the Editor only knows 79.
- **The volume change didn't show up**, and that's correct. Per the Owner's Manual p.26, that [SHIFT] + TONE volume belongs to a **FAVORITE memory** and is stored only with [WRITE] + FAVORITE, not in the sound itself. (My guess that it was the patch level was wrong.) For our app this means the sound's own level and reverb settings are what we control.

### 3.4 Describe sounds in your own words (your ears are the scarce resource)
Take `research/generated/factory-tones.csv` and play through about **20–40 factory sounds from different families** (you select them with the family button + variation number). For each, add a line to `captures/factory/descriptions.md`:

*`Strings/Pad 23 Shimmer Pad — slow bright attack, glassy, wide, lots of movement; great for ambient intros`*

Write the way you'd describe a sound to the LLM later. These lines become the **language ↔ sound** examples the AI learns from. Any words are fine; they'll be matched against the descriptor vocabulary in `knowledge/sound-design/sound-design.md` (bright, warm, hollow, breathy, punchy, lush, metallic, …), and your words will extend it. You don't need to save any files here: step 3.1 already captured all the sounds.

Also note whether the **SuperNATURAL** and **SPECIAL** sounds can be read by the Editor at all.

### 3.5 *(Optional, 10 minutes)* Where the synth keeps a few panel settings
Only if you're curious. It isn't needed for the goal. With MIDI-OX set up as in 3.3 (input = the synth), SysEx → Send/Receive SysEx:
- [ ] Send `research/generated/experiment-rq1-setup-system.syx` (3 read-only requests) and save the reply as `captures/rq1/system-before.syx`.
- [ ] Hold [SHIFT], press the lit TONE button ("UOl"), change the volume a few steps, release [SHIFT] (**no WRITE**). Send again → `captures/rq1/system-after-volume.syx`. Switch sounds to discard the change.
- [ ] Sleep interval: hold [SHIFT] + PGM CHANGE [DEC], note the shown value, change it one step, press [WRITE]. Send again → `captures/rq1/system-after-sleep.syx`. **Then set it back** the same way and press [WRITE].
- [ ] One line per file in `captures/rq1/notes.md`.

---

## Step 4: First write, Temporary only (15 minutes), ready now

Everything it depends on is now confirmed:
- the working copy follows the panel and is thrown away when you switch sounds
- the synth accepts whole-block writes to it (Roland's SYNC did exactly that)
- our request file reads it back

This is the last untested piece of the chain: **our code → synth**.

Setup as in 3.3: MIDI-OX, *SysEx → Send/Receive SysEx*, input and output = `Roland AX-Synth`, and no Editor or Librarian running.
- [ ] Select **LEAD GUITAR 1** (SearingGtr 1) on the synth, so you can compare the two sounds.
- [ ] Set a **delay between messages of 60 ms** (in the SysEx window's options, "Delay after F7" or similar). That's slightly slower than Roland's own software (21–60 ms).
- [ ] Send `research/generated/guitar01-temporary.syx`: the forum patch, encoded by *our* code, 9 messages, to the Temporary patch only.
- [ ] **Without switching sounds**, send `research/generated/experiment-rq1-temporary-patch.syx` and save the reply as `captures/first-write/reply.syx`. I'll check it byte for byte against what we sent.
- [ ] Listen and note in `captures/first-write/notes.md`:
  - Does it sound different from the factory SearingGtr 1? More like a metal lead guitar?
  - Soft notes (velocity below ~70): does an extra high pure tone appear?
  - Pitch bend on the ribbon: **2 octaves down, 1 up** (the factory sound bends 2 semitones up, 1 octave down)?
  - *(Optional)* D-Beam: the patch expects CC70 on [ASSIGNABLE]. Yours is CC01 (the default). To try it, hold [SHIFT] + [ASSIGNABLE], choose "C70", [WRITE]; later set it back to "C01" the same way.
- [ ] Switch to another sound and back. You should hear the factory SearingGtr 1 again (Temporary is volatile).

If the synth shows an error or nothing changes, save the MIDI-OX log and stop. That's a finding too.

**Then comes the listening test.** Once step 4 works, I'll prepare 6–10 small `.syx` files, all Temporary-only, each starting from a factory sound and changing *one* thing: brightness (cutoff), resonance, attack, release, vibrato, reverb, chorus, an effect type, a layer on or off. You send each one and say whether you hear what the model predicts. That confirms our parameter meanings by ear, which is the basis for the "big knobs".

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
- Folder names so far: `captures/live/` (step 2), `captures/mitm/` and `captures/backup/` (3.1), `captures/bulkdump/` (3.2), `captures/rq1/` (3.3), all done; next `captures/first-write/` (4) and `captures/factory/` (3.4).
- Then just tell me "step N done". I'll read the files, decode them, update the research and tests, and prepare the next step.

## What I'll build with it (for orientation)

1. **Hardware-verified model**: ~~reading~~ done (steps 2–3.3). Still to go: writing to the Temporary patch (step 4) and checking the parameter meanings by ear (listening test).
2. **Safe sender** *(needs your go-ahead, because it's the first code that talks to the synth)*: a small tool that loads a patch into the Temporary patch with safe pacing and reads it back to verify. It can **never** address the memory slots or system settings. Until then you send my prepared files with MIDI-OX. Where it runs depends on your answer to step 5 question 1 (web page or Python).
3. **Sound corpus + meaning layer**:
   - the 256 factory sounds, fully decoded from your backup (`research/generated/user-patches.csv` has the overview)
   - your descriptions (3.4)
   - Roland's parameter and effect explanations
   - the *Synth Secrets* sound-design knowledge

   On top of these comes the big-knob **macro** layer. The patch format has built-in candidates: patch-wide cutoff, resonance, attack, release and velocity offsets.
4. **Simple GUI** with those macros, a factory-sound picker, and "send to synth".
5. **LLM integration**: you describe the sound, and the LLM picks the nearest factory sound and sets the macros (and specific parameters when needed). The model validates every value, and the result goes to the Temporary patch. You listen, say "brighter" or "less reverb", and it adjusts.

**Where your time helps most now:** step 4 (15 min), then 3.4 (descriptions) and step 5 (decisions). Those two are what the GUI and the AI are designed around.
