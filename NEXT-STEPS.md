# Next steps for you

**Goal:** you describe a sound to an LLM, and your AX-Synth ends up with a patch that sounds like it. Along the way there will be a simple GUI with a handful of meaningful controls instead of the Editor's 800+ parameters.

**Where we are:** the whole data model is decoded and checked against Roland's docs, Roland's own export files, two real patches, the Owner's Manual, and (step 2) the Editor's own live messages, which our code reproduces byte for byte (`research/REPORT.md`). **Since steps 3.1–3.3 it is also checked against your real synth:** we've seen the complete read conversation, our own read requests work, and your backup and the synth's own memory dump agree byte for byte. The factory-sound order and the wave list are confirmed, and the Editor's model covers everything the synth stores for a sound (`research/generated/user-patches.csv` lists every sound with its waves and effects). **Next is the first write (step 4).** There is now also a **sound-design knowledge base** built from all 63 parts of *Synth Secrets*: which settings make a sound bright, hollow, breathy, brassy, bell-like…, plus 35 instrument recipes mapped onto the AX-Synth (`knowledge/sound-design/`). It hasn't been checked by ear yet; that's what your listening steps are for. We also have the list of all 256 factory sounds (`research/generated/factory-tones.csv`) and Roland's parameter and effect explanations (Editor manual). What's missing is almost entirely things only you can do: **real hardware, your ears, and your preferences.**

**Two facts about the AX-Synth that shape everything below** (Owner's Manual):
- Its display has **3 characters**. It can't show patch names, wave names or values, so checks go through the **Editor (READ)** or a SysEx dump.
- The synth's own **[WRITE] button can't store sound edits**. It stores favorites and system settings only. Sounds are stored by the Editor/Librarian.

---

## Sharing the editor (one-time setup, ~2 minutes)

The editor is the self-contained **`app/`** folder. The repo's front page (README.md) points people to it. Two ways to share it:
1. **Online link** (nothing to install for anyone):
   - On GitHub, open the repository → **Settings** → **Pages** → *Build and deployment* → **Source: GitHub Actions**.
   - After the next push, the **Actions** tab runs *Publish web editor*, and the editor is live at **https://ottoguy.github.io/ax-synth-tools/**. Every later push that changes `app/` updates it automatically.
2. **Download zip**: tell me "make a release v1.0.0" (or run `git tag v1.0.0` and `git push origin v1.0.0`).
   - The *Release downloadable editor* action builds **AX-Synth-Web-Editor.zip**, which contains only the app.
   - It's always available at https://github.com/Ottoguy/ax-synth-tools/releases/latest/download/AX-Synth-Web-Editor.zip.
   - The downloaded version starts with `Start-AX-Synth-Editor.bat` and needs no Python or other install.

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

## Step 1: Documents ✅ done

- [x] Owner's Manual: done (`docs/AX-Synth_OM.pdf`). It gave us the **factory sound list**. Correction to what I said earlier: the *parameter explanations* weren't in it; they were already in the **Editor manual** we had (parameter guide p.9–43, effects list p.44–78).
- [x] Those explanations are now extracted into the **knowledge base** (`knowledge/knowledge.md` to read; `knowledge.json` for the AI).
- ~~Erratum 1~~: doesn't exist (you checked). ~~Juno-D/Di Editor~~: skipped (your decision, 2026-09-28).

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

## Step 4: The web editor = first write ✅ done (2026-09-28)

**It works on your synth.** You confirmed tone delay, volume, octave shift and Wave settings on all tones (`captures/first-write/notes.md`).

**About the reverb that stopped working.** Changing the reverb type works like Roland's Editor. But reverb is only heard if something is *sent* to it:
- the tones' REV send levels
- the MFX REVERB SEND LEVEL
- or the chorus routed into the reverb

Some reverb parameters (e.g. SRV time or density at minimum) also make it almost inaudible. I also fixed a small bug where a value you were dragging could arrive just *after* a type change. **New in the editor (reload the page to get it):**
- **Changes tab**: every value you changed since Read/Load/Open, with **Reset** per row and **Revert all**. Try Revert all on the sound where reverb disappeared.
- **Effects routing box** (top of the Effects tab, ⚠ on the tab when something is off): says in plain words whether MFX, chorus and reverb are audible and why not, e.g. "Reverb SRV HALL is inaudible: nothing is sent to it (Tone 1 REV send 0 …)". I checked its rules on all 256 factory sounds: the only warnings are the 4 sounds where Roland left reverb unused and the 8 with REVERB LEVEL 0.
- **Edit together** (now the column headers on the Tones tab): tick tones, and an edit on one is applied to all ticked tones, like Shift + TONE SELECT in Roland's Editor.
- On/off and choice settings now show names (OFF/ON, MONO/POLY, MAIN/MAIN+REV/REV …) instead of 0/1/2.

**Latest layout (reload the page):**
- **Tones 1–4** are one tab with four columns side by side. Tick column headers (**Edit together**) to change several tones at once; the **ON/OFF** switch in each header turns that tone on or off.
- The **Effects** tab starts with a **signal-path diagram**: green arrows carry sound; the thicker an arrow, the higher its level or send; dotted arrows are set to 0. Click **MFX**, **Chorus/Delay** or **Reverb** to show only that effect's settings below; click a **Tone** to jump to the Tones tab; click an underlined value (e.g. "send 0", "level 127") to change it right in the diagram.
- **⬆ Send whole sound to synth + check** is the big green button at the top, and again in the summary at the bottom of **Changes**. It replaces the sound the synth is playing right now (never your stored sounds) and confirms with ✓.
- Simple settings are beige; expert-only settings are leaf green. Tabs follow the same colours: beige tabs exist in Simple mode, green tabs are Expert-only.
- **Where the tones go** (Effects tab, under the diagram): OUTPUT ASSIGN for the whole sound and for each tone (also via the underlined "output assign" in the diagram).
- **Controllers** tab (also in Simple mode): what the **modulation bar** (targets, amounts, and MFX control if used), the **D-Beam** (its CC and range from the synth, read-only, plus what that CC does in the sound), the **ribbon** (bend range) and the **aftertouch knob** do in this sound. These are shortcuts to the same settings as on the Matrix and Common tabs.
- **Copy a tone** (Tones tab, under Edit together): copies every setting of one tone to another (including its key/velocity range; the target's ON/OFF stays). The **Simple / Expert** switch is at the top right; System and MIDI log appear in Expert mode only.
- Anything that replaces the sound you're editing (Load, New, Open, Read, Revert all, changing an effect type) asks "are you sure?" first.
- **Store in synth slot…** (next to Save .a8e): stores the sound permanently in one of the 256 memory slots, **replacing** the sound there.
  - It asks you to confirm you have a backup.
  - It can download the slot's old sound as an .a8e file first (a tick box, on by default; recommended).
  - It asks "are you sure?" once more, then writes and reads back to check.
  - **First time: please test it on a slot you don't need**, then switch the synth off and on and use *Load stored sound* on that slot. That confirms the write survives power-off (it's never been tested on this synth). Tell me the result, and if something's off, save the MIDI log to `captures/web/store-log.txt`.

**Earlier additions:**
- A **Start here** tab with a short how-to (it opens by itself the first time).
- **Simple / Expert mode** (the switch at the top right). Simple mode shows only the easy settings you picked; Expert shows everything, with the easy ones marked by a blue edge. Levels and sends always look like green faders.
- A small **↺** next to every setting you changed: back to the value from the last Read / Load / Open.
- Filter types and other choices are explained in words (e.g. "LPF (low pass): reduces all frequencies above the cutoff…").

If reverb still stays silent after **Revert all**, copy the **MIDI log** into `captures/web/log.txt` and tell me.

**One MFX at a time?** Yes: the AX-Synth has one MFX, one Chorus and one Reverb per sound. For tremolo *and* phaser:
1. set the MFX to **PHASER**
2. on a Tone tab, tick **Edit tones together** for the tones you use
3. in the LFO section, set LFO1 **WAVEFORM** (e.g. TRI), **RATE**, and **DEPTH TVA** (= tremolo)

Or use a combination MFX: 27 TREMOLO CHORUS, or 66–77 (e.g. OVERDRIVE->CHORUS, CHORUS->DELAY).

### How the web editor works (reference)

There's now a **web editor** with every sound parameter of Roland's AX-Synth Editor: Common, Tone 1–4, TMT/Structure, Matrix Control, all 78 MFX types, chorus and reverb, with the Editor manual's labels and explanations (hover over a name). It talks to the synth directly from Microsoft Edge.

**It can only change the synth's working copy (Temporary patch).** Stored sounds, system settings and FAVORITES can't be written from it; that's enforced in its code and tested. Anything you do is undone by selecting another sound on the synth.

**Start it:**
1. Close **MIDI-OX**, the **Roland Editor** and the **Librarian** (only one program can use the synth's USB port).
2. Double-click **`app/Start-AX-Synth-Editor.bat`** (or use the online link in README.md). A small black window opens (the local server; leave it open), and Edge opens `http://localhost:8765`.
3. Click **Connect**. The first time, Edge asks whether the site may use MIDI devices / control them: click **Allow**. The status turns green: "Connected: Roland AX-Synth".

**First use (done):**
- [ ] On the synth, select **LEAD GUITAR 1** (SearingGtr 1). Click **Read from synth**: the name field should say "SearingGtr 1" and the controls show its values. The **System (read-only)** tab shows your system settings.
- [ ] **Open .a8e** → `patches/guitar01.a8e`. It's sent to the synth automatically and read back. Next to the buttons you should see **"✓ sent and verified"**. That's the first write of our own bytes, checked byte for byte.
- [ ] Listen, and note in `captures/first-write/notes.md`:
  - Does it sound different from the factory SearingGtr 1? More like a metal lead guitar?
  - Soft notes (velocity below ~70): does an extra high pure tone appear?
  - Pitch bend on the ribbon: **2 octaves down, 1 up** (the factory sound bends 2 semitones up, 1 octave down)?
- [ ] Move a control while playing, e.g. **Tone 1 → TVF → CUTOFF**: the sound should change as you drag.
- [ ] Switch to another sound on the synth and back: you hear the factory SearingGtr 1 again.

**If something doesn't work:**
- Open the **MIDI log** tab, click **Copy log**, and paste it into `captures/web/log.txt`. It shows every message in both directions.
- "AX-Synth not found" means another program still holds the port, or the synth is off.
- If Edge never asked about MIDI, check the lock/site icon in the address bar → *Site permissions* → MIDI devices → Allow.

**Other things it can do:**
- **Load stored sound** reads one of your 256 memory slots (read-only) and plays it via the working copy, so you can edit it.
- **New (INIT)** loads Roland's blank patch.
- **Save .a8e** saves the current patch as a Roland Editor file.

To *keep* a sound in one of the synth's memory slots, save the `.a8e`, open it in Roland's Editor and use its WRITE, as before. The web editor deliberately can't store sounds (see step 5, question 7).

**Next: the listening test.** I'll prepare 6–10 small patches (`.a8e` files you open in the web editor). Each starts from a factory sound and changes *one* thing: brightness (cutoff), resonance, attack, release, vibrato, reverb, chorus, an effect type, a layer on or off. You say whether you hear what the model predicts. That confirms our parameter meanings by ear, which is the basis for the "big knobs".

---

## Step 5: Decisions only you can make

Answer these in `captures/decisions.md`. Rough answers are fine, and you can change your mind later.

**The GUI**
1. ~~Where should it run?~~ **Decided (2026-09-28):** a web page in Edge: online at https://ottoguy.github.io/ax-synth-tools/ or downloaded (`app/`, `Start-AX-Synth-Editor.bat`, no install needed). Sound parameters only, sent live; system settings read-only.
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
- *(Background only, no action)* Tutorials for the Juno-D/Juno-Di or Fantom-X apply almost 1:1: same engine family.

---

## How to hand things back to me

- Put everything under `captures/` with the file names above, plus a `notes.md` per folder.
- Folder names so far: `captures/live/` (step 2), `captures/mitm/` and `captures/backup/` (3.1), `captures/bulkdump/` (3.2), `captures/rq1/` (3.3), all done; next `captures/first-write/` (4), `captures/web/` (web editor logs, if needed) and `captures/factory/` (3.4).
- Then just tell me "step N done". I'll read the files, decode them, update the research and tests, and prepare the next step.

## What I'll build with it (for orientation)

1. **Hardware-verified model**: ~~reading~~ done (steps 2–3.3). Still to go: writing to the Temporary patch (step 4) and checking the parameter meanings by ear (listening test).
2. **Safe sender + full editor**: ✅ built (2026-09-28), the web editor (step 4). It sends only to the Temporary patch, with safe pacing and read-back verification, and **never** addresses the memory slots or system settings.
3. **Sound corpus + meaning layer**:
   - the 256 factory sounds, fully decoded from your backup (`research/generated/user-patches.csv` has the overview)
   - your descriptions (3.4)
   - Roland's parameter and effect explanations
   - the *Synth Secrets* sound-design knowledge

   On top of these comes the big-knob **macro** layer. The patch format has built-in candidates: patch-wide cutoff, resonance, attack, release and velocity offsets.
4. **Simple GUI** with those macros, a factory-sound picker, and "send to synth". The full-parameter web editor (step 4) is its foundation: the big knobs will be a panel on top of it.
5. **LLM integration**: you describe the sound, and the LLM picks the nearest factory sound and sets the macros (and specific parameters when needed). The model validates every value, and the result goes to the Temporary patch. You listen, say "brighter" or "less reverb", and it adjusts.

**Where your time helps most now:** step 4 (15 min), then 3.4 (descriptions) and step 5 (decisions). Those two are what the GUI and the AI are designed around.
