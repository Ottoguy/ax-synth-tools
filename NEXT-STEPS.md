# Next steps for you

**Goal:** you describe a sound to an LLM, and your AX-Synth ends up with a patch that sounds like it. Along the way there will be a simple GUI with a handful of meaningful controls instead of the Editor's 800+ parameters.

**Where we are:** the whole data model is decoded and checked against Roland's docs, Roland's own export files and two real patches (`research/REPORT.md`). What's missing is almost entirely things only you can do: **real hardware, real factory sounds, your ears, and your preferences.**

The steps are ordered. Steps 1–3 need no risky writes, and most of step 2 needs no synth at all.

---

## The safety rules (read once, apply always)

1. **Back up first.** Do step 3.1 before *anything* is sent to the synth.
2. **Only send to the Temporary Patch.** Every file I prepare for you to send targets `1F 00 00 00`, the working copy the synth throws away when you switch patches or power off. The `*-temporary.syx` files are safe.
3. **Never play `dumps/AX-Synth Librarian Clean export.mid` to the synth.** It would overwrite all 256 patches with INIT PATCH.
4. **Never send anything I haven't prepared or named** as safe, and never press WRITE on the synth or in the apps unless I ask you to in a specific step.
5. When in doubt, stop and tell me. A wrong read costs nothing, and a wrong write costs your patches.

---

## Step 0: Tell me about your setup (5 minutes, just answer)

Write the answers in `captures/setup.md` (create the folder):

- [ ] How the synth connects: **USB cable directly**, or a **MIDI interface + 5-pin cables**? Which interface?
- [ ] Which driver: Roland's own AX-Synth driver, or the Windows generic one? (The Roland manuals recommend Roland's driver if the Editor and Librarian run together.)
- [ ] The exact **MIDI port names** Windows shows (e.g. in the Editor's *Setup → Set Up MIDI Devices*).
- [ ] Your AX-Synth **firmware/system version**, if the synth shows it (usually at power-on or in a SYSTEM/INFO page).
- [ ] Does the synth have a **Device ID** setting? If so, what is it set to? (The doc expects 17 = `10H`.)
- [ ] Have you ever edited or overwritten the synth's stored patches, or are they still factory?

---

## Step 1: Get me the documents I don't have (15 minutes)

Download from Roland's support site (roland.com → Support → AX-Synth → Owner's Manuals) and put in `docs/`:

- [ ] **AX-Synth Owner's Manual** (English). It should contain the **factory patch list**, the **wave list**, and **explanations of every MFX/parameter**. Those explanations are what the LLM needs in order to know *what a parameter does to the sound*, and they're the most valuable document still missing.
- [ ] **Erratum 1**, if it exists (we have "Erratum2").
- [ ] Any **"Sound List"**, "Parameter Guide" or "Patch List" PDF offered for the AX-Synth.
- [ ] *(Optional)* The **Juno-Di or Juno-D Editor** installer from Roland's site. It's the closest sibling instrument. Its `Script.xml` may explain the patch-write handshake we still don't understand. Just put the installed files in `reference/juno-editor/`.

---

## Step 2: Capture the Editor's live traffic, no synth needed (30–45 minutes)

**Why:** the SMF exports showed how whole patches are sent. What we still don't know is what the Editor sends when you **turn one knob**, press **READ**, **SYNC** or **WRITE**. That answers the open questions (the `00 81` address bug, how patch names are listed, how "write to slot" works) without touching the synth.

**Setup:**
1. Install **loopMIDI** (Tobias Erichsen, free) and create one port, e.g. `loopAX`.
2. Install **MIDI-OX** (free). Set its MIDI **input** to `loopAX` and open the *SysEx View* (View → SysEx). Make its SysEx input buffers large (Options → SysEx…, e.g. 64 buffers × 4096 bytes).
3. In the AX-Synth **Editor**: *Setup → Set Up MIDI Devices* → **Output = `loopAX`**. Leave Input on nothing, or on another loopMIDI port. The Editor will likely complain that it gets no answers; that's expected.

**Actions.** Clear the MIDI-OX log before each one and **save the log as a separate file** afterwards (File → Save, or copy the SysEx view text):

| # | Do this in the Editor | Save as |
|---|---|---|
| 2.1 | Move **Tone 1 TVF Cutoff** one step up, then back | `captures/live/01-cutoff.txt` |
| 2.2 | Change **Patch Name** to `TEST` | `02-name.txt` |
| 2.3 | Set **MFX type** to *STEP PITCH SHIFTER*, then move **Balance** and **Level** (the two bugged addresses) | `03-steppitch.txt` |
| 2.4 | Change **Master Tune** (System) and **Beam Range** | `04-system.txt` |
| 2.5 | Press **READ** | `05-read.txt` |
| 2.6 | Press **SYNC** | `06-sync.txt` |
| 2.7 | Press **WRITE** and pick User patch 1-1 (safe here: it only goes to the loopback) | `07-write.txt` |
| 2.8 | Same idea in the **Librarian**: set its Output to `loopAX`, press **Read Selected** and **Write Selected** on one row | `08-librarian-read.txt`, `09-librarian-write.txt` |

For each file, add one line to `captures/live/notes.md` saying what you did, plus anything the app showed (error dialogs, timeouts). Screenshots of error dialogs help too.

---

## Step 3: First contact with the synth, read-only (45 minutes)

Connect the synth. Set the Editor/Librarian ports back to the real AX-Synth ports.

### 3.1 Back up everything (do this first, always)
- [ ] Open the **Librarian** and press **Read All Data**. This *reads* all 256 patches from the synth.
- [ ] **Save** it as `captures/backup/ax-synth-backup-YYYY-MM-DD.a8l`.
- [ ] Also **File → Export SMF** to `captures/backup/ax-synth-backup-YYYY-MM-DD.mid`.
- [ ] Put a copy somewhere outside this project (cloud drive, USB stick).

This backup is also the **most valuable dataset for the AI**: 256 professionally designed sounds with names, which the LLM can use as starting points and examples.

### 3.2 Read-only request test (checks our own SysEx code against the real synth)
- [ ] On the synth, select a patch you know (write down its **name** and roughly what it sounds like).
- [ ] In MIDI-OX: *SysEx → Send/Receive SysEx*, load `research/generated/experiment-rq1-temporary-patch.syx`, and send it with the input set to the synth. Save everything received as `captures/rq1/reply.syx`. (These are *requests*; they change nothing on the synth.)
- [ ] Note in `captures/rq1/notes.md`: the patch name on the display, how many messages came back, and any errors.

### 3.3 Factory sound corpus with the Editor
For about **10–20 patches spanning different categories** (piano, brass, lead, pad, bass, strings, organ, FX, guitar…):
- [ ] Select the patch on the synth, press **READ** in the Editor, and **File → Save As** `captures/factory/<patch name>.a8e`.
- [ ] Add one line per patch to `captures/factory/notes.md` in **your own words**: how it sounds, what it's good for, anything notable. For example: *"PWM Strings – slow attack, warm, wide, 80s pad."*

Your descriptions are the start of the *language ↔ parameters* mapping the LLM will learn from, so write them the way you'd describe a sound to the LLM later.

Also check: are the **SuperNATURAL** and **Special** patches (bank MSB 66 / MSB 87 LSB 64) editable in the Editor, or read-only? Note what happens.

---

## Step 4: First write, Temporary only (15 minutes)

Only after step 3.1 is done.

- [ ] In MIDI-OX, set a **delay between messages** of at least **25 ms** (Options → SysEx → "Delay after F7"; Roland's own software uses about 20 ms plus transmission time).
- [ ] Send `research/generated/guitar01-temporary.syx` (the forum patch, encoded by *our* code, to the Temporary patch only).
- [ ] Check and write down in `captures/first-write/notes.md`:
  - Does the display show **"SearingGtr 1"**?
  - Does it sound like a **metal lead guitar**?
  - Soft notes (velocity below ~70): does an extra high pure tone appear?
  - Pitch bend: **2 octaves down, 1 up**?
  - If you assign the **D-Beam to CC70**, does it change the sound (the "feedback")?
  - On the synth's edit screen for Tone 1, what **wave name** does it show? (We predict **"Overdrive Gt"**. This confirms the wave numbering.)
- [ ] Switch to another patch and back. The stored patch should be unchanged (Temporary is volatile).

After this I'll prepare a small **listening test**: a few `.syx` files that each change one thing (cutoff, attack, reverb…) so you can confirm by ear that each parameter does what the model says.

---

## Step 5: Decisions only you can make

Answer these in `captures/decisions.md`. Rough answers are fine, and you can change your mind later.

**The GUI**
1. **Where should it run?** (a) a **web page** in Chrome/Edge that talks to the synth directly via Web MIDI (no install, and it can be published as a link), (b) a **desktop app** (Python), (c) no preference. My default recommendation is (a).
2. **Which "big knobs" do you want?** Pick or add from: brightness, warmth, attack (soft ↔ percussive), release/length, sustain, body/thickness, detune/width, movement/vibrato, grit/distortion, space (reverb), echo (delay), octave/layering, mono/poly/glide, velocity sensitivity, "age"/lo-fi. Which 6–10 matter most for how you play?
3. Should the GUI also let you **pick a factory patch as a starting point** and then adjust the big knobs? (I think this gives much better results than starting from INIT.)

**The LLM**
4. Which assistant do you want in the loop: **Claude via the API** (needs an API key, costs a little per request), **Claude here in Claude Code** (I generate the patch and you send it), or both?
5. Is it fine for the LLM to **start from the nearest factory patch and edit it**, rather than build every patch from scratch? (This is my recommendation.)
6. Should the app ever **store patches in the synth's memory** by itself, or always load them into the **Temporary** patch and let *you* press WRITE on the synth when you like one? (My recommendation is the latter; it's much safer.)

**Your sounds**
7. Write **15–30 example requests** you would actually type, in your own words, for example:
   - "fat 80s brass stab for a synth-pop chorus"
   - "glassy bell pad with slow shimmer"
   - "screaming mono lead like a guitar solo, with pitch bend"
   These become the **test set** for judging whether the AI does a good job.
8. Styles/genres you mostly play, and anything you **don't** want (e.g. "never too quiet", "no huge reverb").

---

## Step 6: Optional, but valuable

- [ ] **More patches with descriptions**: any `.a8e`, `.a8l` or `.syx` AX-Synth patches you find online, especially with text describing the sound. Put them in `patches/` with a `.txt` of the description next to each.
- [ ] **Audio recordings**: later, short recordings (a few notes and a chord, WAV) of patches. This makes it possible to check automatically whether a generated sound matches its description. Not needed yet.
- [ ] **Juno-Di / Fantom-X owners' material**: the AX-Synth shares its sound engine family with these, so tutorials on programming *Juno-D/Juno-Di* patches apply almost 1:1.

---

## How to hand things back to me

- Put everything under `captures/` with the file names above, plus a `notes.md` per folder.
- Then just tell me "step N done". I'll read the files, decode them, update the research and tests, and prepare the next step.

## What I'll build with it (for orientation)

1. **Hardware-verified model**: confirm or fix the open questions (steps 2–4).
2. **Safe sender**: a small tool that loads any patch into the Temporary patch with correct pacing, and can never touch User slots unless explicitly told to.
3. **Sound corpus + meaning layer**: factory patches, your descriptions, and the Owner's Manual turned into a "what each parameter does to the sound" knowledge base, plus the big-knob **macro** layer (e.g. *brightness* = cutoff + filter envelope + velocity-to-cutoff across all active tones).
4. **Simple GUI** with those macros, a starting-patch picker, and "send to synth".
5. **LLM integration**: you describe the sound, the LLM picks a starting patch and sets the macros (and, when needed, specific parameters), the model validates every value, and the result goes to the Temporary patch. You listen, say "brighter" or "less reverb", and it adjusts.
