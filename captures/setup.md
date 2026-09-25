# Setup (NEXT-STEPS step 0)

Written from the user's report, 2026-09-25.

| Question | Answer | What it means |
|---|---|---|
| Connection | **USB cable directly** to the PC (Windows 10). No MIDI interface. | MIDI goes over the synth's USB port only. |
| USB driver mode | **"Gen"** ([SHIFT] + PGM CHANGE [INC]) | Windows' built-in class driver is used, and Roland's driver isn't installed. Roland warns that with the OS generic driver over USB, the Editor and Librarian may not work at the same time and may fail to read/write (Editor manual p.8, [D]). Windows 10's class driver lets only one program open the port [I]. So Editor, Librarian and MIDI-OX can't share the synth directly; MIDI-OX in the middle (step 3.0) is the way to capture. If READ misbehaves, Roland's fix is its own driver ("Uen", listed on Roland's AX-Synth support page as the "GW-8 Driver", only up to Windows 8), but try the MIDI-OX route first. Left as is; the mode was not changed. |
| MIDI port name | **"Roland AX-Synth"**, in Device Manager and in the Editor's MIDI device list | Use this port in MIDI-OX (step 3.0). It's a single port pair (one in, one out). |
| Firmware version | **2.01** (VARIATION [+] + [–] + TONE [8] at power-on) | Newer than all our documents: Owner's Manual (Oct 2009), MIDI Implementation v1.00 (Jan 2010), Editor/Librarian v1.00 (2009). Roland publishes no firmware update for download, so 2.01 was probably factory-installed [I]. See "Firmware 2.01" below. |
| MIDI channel | Not reported | Doesn't matter for SysEx (device ID 10H is fixed). Factory default is 1. |
| Stored sounds overwritten before? | Unknown: bought second hand, "if so, not much". User: "let's not fret about it". | The backup (step 3.1) is compared name-by-name with the factory list, and differing slots are marked as non-factory. |

## Firmware 2.01: what it could change (all [I], checked by step 3)

- **Identity Reply:** the MIDI Implementation prints the software revision as `00 01 00 00`. A 2.01 unit may answer differently. `midiox_log.py` now decodes the reply and lists every field that differs from the doc. If the Editor v1.00 rejected an unknown revision, READ would still fail with the synth connected. That would itself be a finding.
- **Sounds:** the Owner's Manual warns that "your unit may incorporate a newer, enhanced version of the system (e.g., includes newer sounds)". The factory Tone list we use comes from the 2009 manual, and the backup will confirm or correct it.
- **Data model:** Script.xml (Editor v1.00) could lack parameters added later. Signs of that would be RQ1 replies longer than our block sizes, or bytes that are never zero in reserved fields.
