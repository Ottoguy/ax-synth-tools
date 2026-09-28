# AX-Synth Tools

A **web editor for the Roland AX-Synth keytar**, and the reverse-engineering research behind it.

## 👉 Just want the editor?

| | |
|---|---|
| **Use it online** (nothing to install) | **https://ottoguy.github.io/ax-synth-tools/**: open in Microsoft Edge or Google Chrome |
| **Download it** (works offline) | **[AX-Synth-Web-Editor.zip](https://github.com/Ottoguy/ax-synth-tools/releases/latest/download/AX-Synth-Web-Editor.zip)**: unzip, then double-click `Start-AX-Synth-Editor.bat` (Windows) |
| **How to use it** | [app/README.md](app/README.md), and the *Start here* tab inside the editor |

You need an AX-Synth connected by USB and Edge or Chrome. **You don't need anything else in this repository**: the editor is only the [`app/`](app/) folder.

It has:
- all sound parameters of Roland's AX-Synth Editor
- a Simple mode with the easy settings
- the four tones side by side
- an effects signal-path diagram
- controller (mod bar / D-Beam / ribbon / aftertouch) shortcuts
- undo, *Send whole sound + check*, and *Store in synth slot* (asks first)

## What's in this repository

| Folder / file | Part of | What it is |
|---|---|---|
| **[`app/`](app/)** | **The product** | The web editor, self-contained: this is what the download contains |
| [`knowledge/`](knowledge/) | Knowledge base | What every AX-Synth parameter and effect does (from Roland's manuals), plus sound-design knowledge (which settings make which sounds). Written for people and LLMs |
| [`research/`](research/) | Research | Reverse-engineering reports ([`research/REPORT.md`](research/REPORT.md) is the overview), analysis tools (`research/tools/`), generated data (`research/generated/`) |
| [`src/axsynth/`](src/axsynth/) | Research (library) | Python library: the AX-Synth data model, SysEx encoding/decoding, knowledge lookup. Used by the tools and to generate `app/model.json` |
| [`tests/`](tests/) | Research | Evidence tests: our model and the editor's bytes vs. Roland's own files and captured synth traffic |
| [`captures/`](captures/), [`dumps/`](dumps/), [`patches/`](patches/) | Research data | MIDI logs from the real synth, Roland's export files, example patches |
| [`original-roland-files/`](original-roland-files/) | Source material | Parts of Roland's AX-Synth Editor installation that the data model is extracted from (Roland's property) |
| [`NEXT-STEPS.md`](NEXT-STEPS.md) | Project | The project checklist (hardware steps, decisions) |
| [`CLAUDE.md`](CLAUDE.md), [`AGENTS.md`](AGENTS.md) | Project | Dense context for AI coding assistants working on this repo |

The long-term goal: describe a sound in plain language, and an AI builds it on the AX-Synth. The knowledge base and data model here are the groundwork for that.

## For developers

- **Python 3** (standard library only) for the research tools and tests: `py -3 -m unittest discover -s tests` (Windows) or `python3 -m unittest discover -s tests`. The web-editor tests also need **Node.js**.
- After changing the data model or the knowledge base, regenerate the editor's data with `python research/tools/build_web_model.py` (writes `app/model.json`; a test fails if it's stale).
- Run the editor from the repo: `app/Start-AX-Synth-Editor.bat`, or `python3 app/serve.py`.
- Publishing:
  - Every push to `main` that changes `app/` updates the online version (GitHub Pages).
  - Pushing a tag like `v1.0.0` builds a new downloadable zip (GitHub Releases).
  - Both are GitHub Actions in [`.github/workflows/`](.github/workflows/).

## License and credits

- **Our own code and documents** (the editor, tools, library, tests, knowledge base texts) are under the [MIT License](LICENSE).
- **Roland material is not ours and not covered by that license**:
  - the files in `original-roland-files/` and `dumps/`
  - Roland's manuals
  - data derived from them (parameter names, value tables, factory sound names, the INIT patch)

  Roland and AX-Synth are trademarks of Roland Corporation. This project is **not affiliated with or endorsed by Roland**.
- The example patches in `patches/` belong to their authors.
- *Synth Secrets* by Gordon Reid (Sound On Sound) is summarized in our own words in `knowledge/sound-design/`. The articles themselves aren't included.
