# First write with the web editor (NEXT-STEPS step 4), 2026-09-28

Written from the user's report: **"It works!"**

- **Confirmed working on the synth** (live edits from the web editor):
  - Tone delay settings
  - volume
  - octave shift
  - several WG (Wave Generator) settings on all four tones
- **Reverb:** it worked with the loaded sound, but after the user changed the **reverb type and reverb parameters**, they couldn't get it back.
  - The editor's type change behaves like Roland's Editor: the whole Reverb block with the new type's Script.xml defaults, then the type byte (tested).
  - Reverb is only audible if something is sent to it: tone REV sends, MFX REVERB SEND, or chorus → reverb. A member such as SRV time or density at its minimum can also make it near-inaudible.
  - A small real bug was fixed: a throttled parameter edit could arrive *after* an effect type change.
  - Added in response (web editor v2): a Changes tab with Reset/Revert all, an Effects routing check that says why an effect is (in)audible, and Edit tones together.
  - The MIDI log of the failing session wasn't saved. If reverb stays silent after "Revert all", save the log to `captures/web/log.txt`.
- **Question: more than one MFX at once?** No: one MFX, one Chorus and one Reverb per sound (Editor manual). Tremolo + phaser = the phaser in the MFX, plus tremolo from the tone LFOs (DEPTH TVA, all tones via "Edit tones together"), or a combination MFX type (27 TREMOLO CHORUS, 66–77).
