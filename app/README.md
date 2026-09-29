# AX-Synth Web Editor

Edit the sounds of your **Roland AX-Synth** keytar from your computer, live while you play. It has every sound setting of Roland's own AX-Synth Editor, a **Simple mode** with just the easy settings, a signal-path diagram for the effects, undo for everything, and sending/storing sounds to the synth.

## What you need

- A **Roland AX-Synth** connected to the computer with a **USB cable** and switched on.
- **Microsoft Edge** or **Google Chrome** (they support Web MIDI; Firefox and Safari don't).
- No other program using the synth at the same time. Close Roland's editor/librarian or MIDI tools first: only one program can use the synth's USB port.

## Start it: two ways

### A) Online: nothing to download

Open **https://ottoguy.github.io/ax-synth-tools/** in Edge or Chrome, and click **Connect**.

### B) Downloaded: works offline

1. Download **[AX-Synth-Web-Editor.zip](https://github.com/Ottoguy/ax-synth-tools/releases/latest/download/AX-Synth-Web-Editor.zip)** and unzip it anywhere.
2. **Windows:** double-click **`Start-AX-Synth-Editor.bat`**. A small black window opens (keep it open while you use the editor), and Edge opens the editor. Nothing needs to be installed.
   If Windows shows *"Windows protected your PC"*, click **More info → Run anyway** (the file is a plain launcher you can open in Notepad to check).
   **Mac / Linux:** in a terminal, in the unzipped folder, run `python3 serve.py` and open http://localhost:8765 in Chrome.
3. Click **Connect**.

The first time, the browser asks whether the page may use your **MIDI devices**: click **Allow**.

## Using it

The **Start here** tab in the editor explains everything in a few minutes. In short:

1. **Start from a sound:** *Read from synth* (the sound playing now), *Load* one of the 256 stored sounds, *Open .a8e* (a sound file) or *New (INIT)*.
2. **Change it:** every change is heard immediately.
   - *Common*: the whole sound.
   - *Tones 1–4*: the up to four layers, side by side. Waves are picked by category, then wave.
   - *Controllers*: what the mod bar, D-Beam, ribbon and aftertouch knob do.
   - *Effects*: MFX (picked by category, then type), chorus/delay and reverb, with a diagram.
3. **Undo:** the ↺ next to any changed setting, or the *Changes* tab (every change with its tab and section, before and now; *Revert all*).
4. **Keep it:**
   - *Save .a8e* saves a file on your computer.
   - *Store in synth slot…* stores it inside the synth. This replaces the sound in that slot; it asks first and can download the old one as a backup.

**Safe by design:** editing and *Send whole sound* only change the synth's working copy (the sound playing now). Selecting another sound on the keytar brings the stored one back. Only *Store in synth slot…* changes a stored sound, and only after you confirm. The editor never changes the synth's system settings.

## Troubleshooting

- **"AX-Synth not found":** the synth is off or unplugged, or another program is using it. Close that program and click Connect again.
- **The browser never asked about MIDI:** click the lock icon in the address bar → Site permissions → MIDI devices → Allow, then reload.
- **An effect is silent:** the diagram on the *Effects* tab shows why (e.g. nothing is sent to the reverb).
- **Anything else:** tab *MIDI log* (Expert mode) → *Copy log*, and include it when you report the problem.

## Files in this folder

| File | What it is |
|---|---|
| `index.html`, `style.css`, `app.js`, `patch.js`, `midi.js`, `sysex.js` | The editor itself (plain web page, no build step) |
| `model.json` | All AX-Synth sound parameters, generated from Roland's own editor data |
| `Start-AX-Synth-Editor.bat`, `serve.ps1` | Windows launcher: a tiny local web server built into Windows |
| `serve.py` | The same for Mac/Linux (Python 3) |

Part of **[ax-synth-tools](https://github.com/Ottoguy/ax-synth-tools)**. Not affiliated with or endorsed by Roland. Roland and AX-Synth are trademarks of Roland Corporation.
