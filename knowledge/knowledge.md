# AX-Synth knowledge base

Generated from `knowledge/*.toml` by `research/tools/build_knowledge.py`. **Do not edit by hand.** Machine-readable form: `knowledge.json`. Format and conventions: `knowledge/README.md`.

Sources: **EM** = AX-Synth Editor manual (docs/AX-SynthEditorManualE.pdf; text research/generated/editor-manual.pdf.txt); **OM** = AX-Synth Owner's Manual (docs/AX-Synth_OM.pdf; text research/generated/owners-manual.pdf.txt); **MI** = AX-Synth MIDI Implementation (docs/AX Synth docs.pdf; text research/generated/midi-implementation.pdf.txt)

## Contents

1. [Concepts](#concepts)
2. [Parameters](#parameters)
3. [MFX types](#mfx-types)
4. [Chorus unit types](#chorus-unit-types)
5. [Reverb unit types](#reverb-unit-types)
6. [Coverage](#coverage)

## Concepts

### Controller section and sound generator section
*id `architecture.overview` · EM p.9*

The AX-Synth consists of a controller section and a sound generator section. The controller section is the keyboard, touch controller (ribbon), modulation bar, panel buttons and knobs, D Beam controller, and pedals connected to the rear panel; the performance information it generates (pressing/releasing keys, pressing the hold button, etc.) is transmitted as MIDI messages to the sound generator section and/or an external MIDI device. The sound generator section produces the sound: it receives MIDI messages from the controller section or an external device, generates sound accordingly, and outputs it from the output and headphone jacks. The AX-Synth plays a single Patch at a time; a variety of effects can be used on that patch.

### Patch = up to four Tones
*id `architecture.patch` · EM p.9, 18*

Patches are the basic sound configurations you play. Each patch combines up to four tones; each tone can be turned on/off individually (TONE SWITCH, see TMT). A tone is the smallest unit of sound, but a tone cannot be played by itself: the patch is the playable unit and the tones are its building blocks.

> Terminology [D OM]: the Owner's Manual calls a whole sound a 'Tone' (8 families x 32). In the Editor/MIDI Implementation that object is a Patch, and 'Tone 1-4' are its internal layers. This knowledge base uses the Editor meaning: tone = layer.

### Signal path inside a tone: WG -> TVF -> TVA, with envelopes and 2 LFOs
*id `architecture.tone_signal_path` · EM p.9, 10*

WG (Wave Generator): specifies the PCM waveform (wave) that is the basis of the sound, and how the pitch changes.
TVF (Time Variant Filter): specifies how the frequency components of the sound change.
TVA (Time Variant Amplifier): specifies volume changes and the sound's position in the stereo field.
Envelope: initiates changes over time. There are separate envelopes for Pitch, TVF (filter) and TVA (volume).
LFO (Low Frequency Oscillator): creates cyclic changes (modulation). There are two LFOs per tone; either or both can be applied to WG pitch (vibrato), TVF cutoff (wah) and/or TVA volume (tremolo).

### Polyphony (128 voices) and voice counting
*id `architecture.polyphony` · EM p.10*

The AX-Synth plays up to 128 notes simultaneously. Voices used = (patches being played) x (tones used by the patch) x (waves used in the tones). Example: a patch combining four tones, each using two waves (stereo), uses eight voices per note. When more than 128 voices are requested, currently sounding notes are turned off to make room, lowest priority first, as set by Patch Priority (LAST or LOUDEST; usually LAST).

> Owner's Manual p.35 says the same: notes are cut off beyond 128 voices.

### Effect units: one MFX, one Chorus, one Reverb per patch
*id `architecture.effects` · EM p.10, 14, 15*

Multi-effects (MFX) are multi-purpose effects that completely change the sound type; 78 effect types (plus 00 THROUGH) including simple effects such as distortion and flanger, and types that connect effects in series or parallel. Chorus adds depth and spaciousness and can alternatively work as a delay. Reverb adds the reverberation of halls or auditoriums; four types. Although chorus and reverb types also exist among the MFX types, the separate Chorus and Reverb units are handled by a different system. MFX, chorus and reverb are set individually for each patch; the same effects apply to all tones of the patch, and the per-tone send levels control how strongly each tone is affected. Effect changes are lost when another patch is selected unless the patch is written.

### Temporary area, Patch memory (256), System memory
*id `architecture.memory` · EM p.11, 19*

Temporary memory holds the data of the patch selected with the panel buttons; the instrument sounds from this data. Editing modifies the temporary area, not memory; the temporary area is lost at power-off or when another patch is selected. To keep settings, write them into Patch memory, which holds 256 patches (Patch Write / the Editor's WRITE button; the previous contents of the destination are overwritten; never switch off while saving). System memory stores system parameters (System Write).

> [D MI] Temporary Patch = SysEx address 1F 00 00 00; User/Patch memory n = 30 00 00 00 + n x 00 01 00 00 (n = 0..255).
> [D OM p.10, p.26] The synth's own panel [WRITE] button stores FAVORITE/system settings only; patches are written from the Editor/Librarian.

### Four tips when creating patches (Roland)
*id `editing.tips` · EM p.18*

1. Choose a patch that is close to what you have in mind; editing an arbitrary patch blindly makes little progress.
2. Decide which tones you will use: use TONE SWITCH 1-4 to make each tone heard or silent. Turning off unneeded tones also conserves polyphony.
3. Check the STRUCTURE setting first: it specifies how the four tones are combined; understand the relationship between tones before editing them.
4. Turn the effects off while editing: effects have a major impact, and turning them off lets you hear the patch itself and the result of your changes. Sometimes editing only the effects is enough to get the sound you want.

> [I] Directly relevant to the AI strategy: start from the nearest factory patch (see research/generated/factory-tones.csv).

### Initialize / Copy / Paste (Editor)
*id `editing.initialize_copy` · EM p.18*

Initialize Patch resets the currently selected patch only; to return all settings to factory values, run a Factory Reset on the AX-Synth itself. Copy copies settings to the clipboard; Paste pastes them to a chosen destination. With TONE SELECT you choose which tone(s) to edit; Shift+click selects several tones and edits change all selected tones simultaneously.

### SUMMARY / Zoom view ADSR = envelope T1/T3/L3/T4
*id `editing.summary_adsr` · EM p.7, 21, 22, 23*

In [SUMMARY] (Pro Edit) and the Zoom Edit envelope views, the simplified ENV A/D/S/R controls for WG (pitch), TVF and TVA change these envelope values: A (Attack) = ENV T1, D (Decay) = ENV T3, S (Sustain) = ENV L3, R (Release) = ENV T4.

> [I] Useful macro mapping for a simplified GUI: ADSR -> T1, T3, L3, T4 of the chosen envelope.

### Stereo waves (L/R pairs)
*id `wave.stereo` · EM p.19, 21, 29*

Some waves are stereo. A left-channel wave name ends in 'L', a right-channel wave name ends in 'R', and they are numbered consecutively: the right wave number is one greater than the left. In mono only WAVE NUMBER L is specified; in stereo WAVE NUMBER R is also specified (in the Editor: select L, then double-click R to pick the matching right wave). A stereo wave uses two voices per note.

### One-shot vs. loop waveforms
*id `wave.oneshot_loop` · EM p.19*

The AX-Synth's internal waveforms are complex PCM waves; choosing a waveform very different from the original may give unexpected results. Two kinds:
One-shot: short-decay sounds containing the whole sound from attack to silence (percussion, or attack components such as a piano hammer strike or guitar fret noise). The envelope cannot give a one-shot wave a longer decay than it contains, nor make it sustain.
Loop: long-decay or sustaining sounds; a portion is looped once the sound is stable (vibrating piano string, resonating pipe, ...).
Example: an electric organ can combine a one-shot key-click with a looped organ wave.
Many acoustic instruments (piano, sax) have a sudden timbre change at the very start that defines their character; with such waves use the waveform's own attack unmodified and use the envelope only to shape the decay; modifying the attack with the envelope interacts with the wave's own attack and may not give the intended result.

### STRUCTURE types 1-10 (how tone pairs 1&2 and 3&4 are connected)
*id `structure.types` · EM p.27, 28*

TYPE 01: tones 1 and 2 (or 3 and 4) are independent. Use it to preserve PCM sounds or to create and combine sounds per tone.
TYPE 02: stacks the two filters together to intensify the filter characteristics. Tone 1 (3) TVA controls the volume balance between the two tones.
TYPE 03: mixes tone 1 (3) and tone 2 (4), applies a filter, then a booster to distort the waveform.
TYPE 04: applies a booster to distort the waveform, then combines the two filters. Tone 1 (3) TVA controls the volume balance between the two tones and adjusts the booster level.
TYPE 05: a ring modulator creates new overtones, and the two filters are combined. Tone 1 (3) TVA controls the balance of the two tones, adjusting the ring modulator depth.
TYPE 06: ring modulator creates new overtones, and the sound of tone 2 (4) is also mixed in and the two filters stacked. Tone 1 (3) TVA adjusts the amount of ring-modulated sound.
TYPE 07: filters tone 1 (3) and ring-modulates it with tone 2 (4) to create new overtones.
TYPE 08: sends filtered tone 1 (3) and tone 2 (4) through a ring modulator, then mixes in tone 2 (4) and applies a filter to the result.
TYPE 09: passes the filtered sound of each tone through a ring modulator to create new overtones. Tone 1 (3) TVA controls the balance of the two tones, adjusting ring modulator depth.
TYPE 10: passes the filtered sound of each tone through a ring modulator and also mixes in tone 2 (4). Tone 1 (3) TVA adjusts the amount of ring-modulated sound.
Rules: when TYPE 02-10 is selected and one tone of the pair is off, the other sounds as TYPE 01 regardless of the display. Key ranges or velocity ranges in which one tone of the pair does not sound behave the same way (notes there sound as TYPE 01). With TYPE 02-10, several settings of tone 1 (3) follow tone 2 (4) because the pair's outputs are combined into tone 2 (4): output assign, tone delay, pan keyfollow / random pan / alternate pan, and LFO settings.

> [D MI] Stored value 0-9 = TYPE 01-10.

### Booster
*id `structure.booster` · EM p.28*

The booster distorts the incoming signal by boosting it (distortion like an electric guitar; higher values = stronger distortion). Used with Structure TYPE 03 or 04. It can also use the waveform of one tone (WG1) as an LFO that shifts the other waveform (WG2) up or down, creating modulation similar to PWM (pulse width modulation). Works best together with WAVE GAIN (set GAIN to maximum when using the booster for distortion).

### Ring modulator
*id `structure.ring_modulator` · EM p.28*

A ring modulator multiplies the waveforms of two tones, generating many new overtones not present in either waveform (evenly spaced harmonic components are usually not generated unless one waveform is a sine wave). As the pitch difference between the two waveforms changes the harmonic structure, the result is an unpitched metallic sound; suitable for metallic sounds such as bells. Available in Structure TYPE 05-10.

### FXM (Frequency Cross Modulation)
*id `wave.fxm` · EM p.29*

FXM uses a specified waveform to apply frequency modulation to the selected waveform, creating complex overtones; useful for dramatic sounds or sound effects. FXM COLOR: higher = grainier, lower = more metallic. FXM DEPTH: depth of modulation.

### Tone Delay
*id `tone.delay_modes` · EM p.30*

Tone Delay produces a time delay between the key being pressed (or released) and the tone starting to sound; it can shift the timing at which each tone sounds. Unlike an effect delay, the delayed tones can have their own sound and pitch, so arpeggio-like passages can be played with a single key. If not used: MODE = NORMAL and TIME = 0. With STRUCTURE TYPE 02-10, tone 1 (3) follows tone 2 (4).

### How to apply the LFO (FADE MODE with DELAY TIME and FADE TIME)
*id `lfo.fade_modes` · EM p.39*

ON-IN: apply the LFO gradually after the key is pressed. DELAY TIME = time from key press until the LFO begins; FADE TIME = time for the LFO amplitude to reach maximum after the delay.
ON-OUT: apply the LFO immediately at key press, then gradually decrease it. DELAY TIME = time the LFO continues after key press; FADE TIME = time to reach minimum after the delay.
OFF-IN: apply the LFO gradually after the key is released. DELAY TIME = time from key release until the LFO begins; FADE TIME = time to reach maximum.
OFF-OUT: apply the LFO from key press until release, and gradually decrease it after release. DELAY TIME = time the LFO continues after release; FADE TIME = time to reach minimum.
Positive vs. negative DEPTH values give opposite modulation phase: two tones with the same depth but opposite sign modulate in reverse phase, which can alternate between two tones or, combined with pan, move the sound image cyclically.

### TMT (Tone Mix Table): velocity and key ranges per tone
*id `tmt.overview` · EM p.40, 41*

The force with which keys are played (velocity) and the note number can control which tones sound. For each tone, a velocity range (LOWER/UPPER with FADE LOWER/UPPER) and a key range (LOWER/UPPER with FADE LOWER/UPPER) are set. Instead of velocity, the Matrix Control can switch tones (TMT CONTROL SW), but keyboard velocity and Matrix Control cannot be used simultaneously for tone switching: when using Matrix Control, set VELOCITY CONTROL to OFF.

### Matrix Control
*id `matrix.overview` · EM p.41, 42*

Matrix Control uses MIDI messages (SOURCE) to change tone parameters (DESTINATION) in real time by an amount (SENS), for chosen tones (TONE). Up to four Matrix Controls per patch; each can control up to four destinations simultaneously. VELOCITY and KEYFOLLOW correspond to note messages. LFO1/LFO2/PITCH ENV/TVF ENV/TVA ENV are not MIDI messages but can be used as sources: the tone settings then change in real time as the patch is played. If RCV BENDER / RCV EXP / RCV HOLD-1 are ON, those incoming messages also apply their normal pitch bend / expression / hold effect in addition to the destination; turn them OFF to affect only the destination. Parameters that Matrix Control can modulate are marked in the manual with a symbol (lost in text extraction; this KB records the corresponding destination in each param's 'matrix' field instead).

### Multi-Effect Control (real-time control of MFX parameters)
*id `mfx.control` · EM p.16, 17*

Instead of system exclusive messages, control changes and other common MIDI messages can control the most important MFX parameters in real time (e.g. touch controller -> amount of distortion, keyboard touch -> delay time). The controllable parameters are predetermined per MFX type and are marked '#' in the Effects List ('#1'/'#2': two items change simultaneously). Up to four assignments: SOURCE (MIDI message), DESTINATION (parameter), SENS (amount). Matrix Control (MFX-CTRL1-4 destinations) can also be used. If a tone's RCV BENDER / RCV EXP / RCV HOLD-1 is ON, the message also applies its normal effect; leave them OFF to control only the MFX parameter.

### STEP RESET for step-sequencer MFX types
*id `mfx.step_reset` · EM p.45*

06 STEP FILTER, 16 STEP RING MODULATOR, 19 STEP PAN, 20 SLICER and 63 STEP PITCH SHIFTER contain a 16-step sequencer. A Multi-Effect Control with DESTINATION = STEP RESET restarts the sequence from the first step. Example: SOURCE = CC01 (modulation bar), DESTINATION = STEP RESET, SENS = +63 restarts the sequence whenever the modulation bar is operated.

### 3D (RSS) effects and OUTPUT MODE
*id `mfx.3d` · EM p.45*

29 3D CHORUS, 30 3D FLANGER, 31 3D STEP FLANGER and 52 3D DELAY use RSS (Roland Sound Space) to create spaciousness beyond delay/reverb/chorus. Place speakers appropriately and away from side walls; if the speakers are too far apart or the room is very reverberant, the full 3D effect may not appear. Each has OUTPUT MODE: SPEAKER when listening through speakers, PHONES when listening through headphones.

### Scale Tune examples (equal, just, Arabian)
*id `scale.examples` · EM p.12*

Equal temperament divides the octave into 12 equal parts (used when Scale Tune Switch is OFF). Just intonation (tonic C): the principal triads sound pure, but only in one key. Arabian scale: E and B a quarter-tone lower and C#, F#, G# a quarter-tone higher than equal temperament; usable in G, C and F.
Example offsets in cents (C, C#, D, D#, E, F, F#, G, G#, A, A#, B):
Equal: 0 0 0 0 0 0 0 0 0 0 0 0
Just (C): 0 -8 +4 +16 -14 -2 -10 +2 +14 -16 +14 -12
Arabian: -6 +45 -2 -12 -51 -8 +43 -4 +47 0 -10 -49

> The sharp/flat signs were lost in the PDF text; the note order follows the MIDI Implementation's example table (p.16), which lists the same values.

### The instrument's real-time controllers (what a patch can respond to)
*id `performance.controllers` · OM p.10, 11, 22, 23, 24, 25, 27*

MODULATION BAR: sends CC01 (vibrato in most patches; 'Dynamics' for SuperNATURAL tones). The response depends on the patch's assignments made in the Editor.
TOUCH CONTROLLER ribbon: pitch bend (BENDER MODE off = normal; lit = 'Catch + Last': a note played while touching off-center keeps normal pitch until the finger crosses the center; allows guitar-like 'double bendings'). Not available for SuperNATURAL tones.
AFTER TOUCH knob: sends channel aftertouch for the notes being played; the keyboard itself sends no aftertouch (it is velocity sensitive). The knob does not return to zero by itself.
D Beam: PITCH (changes pitch), FILTER (changes cutoff/brightness), ASSIGNABLE (sends the assigned CC01-95, CC32 not available; stored in the system).
PORTAMENTO button: portamento on/off (for SuperNATURAL tones selectable Hld / SUt mode).
HOLD button and FOOT PEDAL: hold/sustain (CC64); any pedal acts as hold, expression pedals are not supported.
Keyboard: 49 keys, velocity sensitive.

> [D Erratum2] The VOLUME knob is analog and transmits no MIDI (CC07).
> [D OM p.40] Recognized CCs include 1, 5, 7, 10, 11, 64, 65, 66, 71-75, 84, 91, 93.

## Parameters

### PATCH COMMON
*group `common` · EM p.20, 24, 25*

Settings that apply to the whole patch (all four tones).

- **PATCH NAME** (12 characters (ASCII 32–127)) *[EM p.24, 5]*: Patch name. Allowed characters: space ! " # $ % & ' ( ) * + , - . / 0-9 : ; < = > ? @ A-Z [ \ ] ^ _ ` a-z { | } ~ (EM p.5).
  - model: `fm.pat.common.patchName` @ 1F 00 00 00
- **Patch Category** (0–127) *[MI p.8]*: Category number of the patch (used by the Editor's patch list).
  - Not described in the Editor manual; listed in the MIDI Implementation only. [3P/I] Numbering probably follows Roland's XV/Fantom category scheme (forum guitar patch = 11); unverified.
  - model: `fm.pat.common.patchCategory` @ 1F 00 00 0C, raw [0, 127]
- **LEVEL** (0–127) *[EM p.20, 24]*: Volume of the patch.
  - model: `fm.pat.common.patchLevel` @ 1F 00 00 0E, raw [0, 127]
- **PAN** (L64–0–63R) *[EM p.24]*: Left/right position of the patch.
  - model: `fm.pat.common.patchPan` @ 1F 00 00 0F, raw [0, 127]
- **OUTPUT ASSIGN (PATCH OUTPUT ASSIGN)** (MFX, L+R, L, R, TONE) *[EM p.15, 24]*: How the direct (unprocessed) sound of the patch is output. MFX: in stereo through the multi-effect (chorus and reverb can also be applied after it). L+R: in stereo to the OUTPUT jacks without passing through the MFX. L: in mono to OUTPUT L without the MFX. R: in mono to OUTPUT R without the MFX. TONE: according to each tone's own OUTPUT ASSIGN.
  - [F] Legal stored values are 0, 1, 5, 6, 13 (numberTable outputAssignXV5050Table) = MFX, L+R, L, R, TONE.
  - model: `fm.pat.common.patchOutputAssign` @ 1F 00 00 27, raw [0, 13]
- **OCTAVE SHIFT** (-3–+3) *[EM p.24]*: Pitch of the patch's sound in octaves.
  - model: `fm.pat.common.octaveShift` @ 1F 00 00 13, raw [61, 67]
- **TUNE COARSE** (-48–+48) *[EM p.24]*: Pitch of the patch's sound in semitones (±4 octaves).
  - model: `fm.pat.common.patchCoarseTune` @ 1F 00 00 11, raw [16, 112]
- **TUNE FINE** (-50–+50) *[EM p.24]*: Pitch of the patch's sound in 1-cent steps (1 cent = 1/100 semitone).
  - model: `fm.pat.common.patchFineTune` @ 1F 00 00 12, raw [14, 114]
- **STRETCH TUNE DEPTH** (OFF, 1–3) *[EM p.24]*: Stretched tuning, the way acoustic pianos are normally tuned: the low range lower and the high range higher than mathematical tuning. OFF: equal temperament. 1–3: higher settings give a greater pitch difference between low and high ranges.
  - model: `fm.pat.common.stretchTuneDepth` @ 1F 00 00 14, raw [0, 3]
- **PRIORITY** (LAST, LOUDEST) *[EM p.10, 25]*: How notes are managed when maximum polyphony (128 voices) is exceeded. LAST: the last-played voices get priority (notes are turned off beginning with the first-played). LOUDEST: the loudest voices get priority (the lowest-volume voice is turned off first). Usually LAST.
  - model: `fm.pat.common.patchPriority` @ 1F 00 00 10, raw [0, 1]
- **MONO/POLY** (MONO, POLY) *[EM p.20, 25]*: MONO: only the last-played note sounds; effective for solo instrument patches such as sax or flute. POLY: two or more notes can be played simultaneously.
  - model: `fm.pat.common.monoPoly` @ 1F 00 00 16, raw [0, 1]
- **LEGATO SW (Switch)** (OFF, ON) *[EM p.25]*: Whether the Legato Switch is used. Valid only with MONO. When ON, pressing a key while still holding a previous key changes the pitch to the newest key while the note keeps sounding: a smooth transition that simulates a guitarist's hammer-on/pull-off.
  - EM caution: with LEGATO SW ON and RETRIGGER OFF, a legato to a higher key may not reach the intended pitch (stops at an intermediate pitch) because the wave-level pitch-rise limit is exceeded; with multiple tones using waves with different upper limits the patch may stop being heard in MONO. For large pitch changes set LEGATO RETRIGGER ON.
  - model: `fm.pat.common.legatoSwitch` @ 1F 00 00 17, raw [0, 1]
- **LEGATO RETRIGGER** (OFF, ON) *[EM p.25]*: Whether sounds are replayed (ON) or not (OFF) when playing legato. Valid when MONO and LEGATO SW ON. Normally ON. When OFF, holding one key and pressing another changes only the pitch, without playing the new key's attack; set OFF for wind and string phrases or when using modulation with a mono synth keyboard sound.
  - model: `fm.pat.common.legatoRetrigger` @ 1F 00 00 18, raw [0, 1]
- **ANALOG FEEL** (0–127) *[EM p.25]*: Depth of 1/f modulation (a pleasant, naturally occurring modulation ratio, like a babbling brook or rustling wind). Simulates the natural instability of an analog synthesizer.
  - model: `fm.pat.common.analogFeel` @ 1F 00 00 15, raw [0, 127]

### Pitch bend range
*group `common.bend` · EM p.24*

Range of the TOUCH CONTROLLER ribbon (pitch bend).

- **PITCH BEND RANGE UP** (0–+48) *[EM p.24]*: Pitch change in semitones when the touch controller is all the way right.
  - model: `fm.pat.common.pitchBendRangeUp` @ 1F 00 00 29, raw [0, 48]
- **PITCH BEND RANGE DOWN** (-48–0) *[EM p.24]*: Pitch change in semitones when the touch controller is all the way left.
  - [F] Stored as a positive number of semitones (e.g. 24 = -24).
  - model: `fm.pat.common.pitchBendRangeDown` @ 1F 00 00 2A, raw [0, 48]

### OFFSET (Modify): patch-wide offsets applied to all tones
*group `common.offset` · EM p.25*

Offsets that modify the corresponding per-tone parameters of all tones at once. Stored 1–127 with 64 = 0 [D MI]. [I] Natural candidates for simplified 'big knob' controls.

- **OFFSET CUTOFF** (-63–+63) *[EM p.25]*: Offset applied to the tones' TVF CUTOFF.
  - model: `fm.pat.common.cutoffOffset` @ 1F 00 00 22, raw [1, 127]
- **OFFSET RES (Resonance)** (-63–+63) *[EM p.25]*: Offset applied to the tones' TVF RES (resonance).
  - model: `fm.pat.common.resonanceOffset` @ 1F 00 00 23, raw [1, 127]
- **OFFSET ATTACK TIME** (-63–+63) *[EM p.25]*: Offset applied to TVF Envelope Time 1 and TVA Envelope Time 1 (attack).
  - model: `fm.pat.common.attackTimeOffset` @ 1F 00 00 24, raw [1, 127]
- **OFFSET RELEASE TIME** (-63–+63) *[EM p.25]*: Offset applied to TVF Envelope Time 4 and TVA Envelope Time 4 (release).
  - model: `fm.pat.common.releaseTimeOffset` @ 1F 00 00 25, raw [1, 127]
- **OFFSET VELOCITY SENS** (-63–+63) *[EM p.25]*: Offset applied to TVF Cutoff Velocity Sens and TVA VEL SENS (velocity sensitivity).
  - model: `fm.pat.common.velocitySensOffset` @ 1F 00 00 26, raw [1, 127]

### PORTAMENTO
*group `common.portamento` · EM p.20, 26*

Portamento smoothly changes the pitch from the first-played key to the next-played key.

- **PORTAMENTO SW** (OFF, ON) *[EM p.20, 26]*: Whether the portamento effect is applied.
  - [D OM p.24] The panel [PORTAMENTO] button switches portamento on/off for regular patches.
  - model: `fm.pat.common.portamentoSwitch` @ 1F 00 00 19, raw [0, 1]
- **PORTAMENTO MODE** (NORMAL, LEGATO) *[EM p.26]*: NORMAL: portamento is always applied. LEGATO: portamento is applied only when you play legato.
  - model: `fm.pat.common.portamentoMode` @ 1F 00 00 1A, raw [0, 1]
- **PORTAMENTO TYPE** (RATE, TIME) *[EM p.26]*: RATE: uniform speed of pitch change (the time taken corresponds to the pitch distance). TIME: constant time regardless of how far apart the notes are.
  - model: `fm.pat.common.portamentoType` @ 1F 00 00 1B, raw [0, 1]
- **PORTAMENTO START** (PITCH, NOTE) *[EM p.26]*: PITCH: a new portamento starts from the current (moving) pitch when another key is pressed during a glide. NOTE: the new portamento begins from the pitch where the current change would have ended.
  - model: `fm.pat.common.portamentoStart` @ 1F 00 00 1C, raw [0, 1]
- **PORTAMENTO TIME** (0–127) *[EM p.20, 26]*: Time over which the pitch changes.
  - model: `fm.pat.common.portamentoTime` @ 1F 00 00 1D, raw [0, 127]

### STRUCTURE (tone pair connection) and BOOSTER
*group `tmt.structure` · EM p.27, 28*

See concept structure.types for the 10 connection types.

- **STRUCTURE TONE 1 & 2 TYPE** (TYPE 1–10) *[EM p.27]*: How tones 1 and 2 are connected (independent, stacked filters, booster, ring modulator variants). See concept structure.types.
  - model: `fm.pat.tmt.structureType12` @ 1F 00 10 00, raw [0, 9]
- **STRUCTURE TONE 3 & 4 TYPE** (TYPE 1–10) *[EM p.27]*: How tones 3 and 4 are connected. See concept structure.types.
  - model: `fm.pat.tmt.structureType34` @ 1F 00 10 02, raw [0, 9]
- **BOOSTER (TONE 1 & 2)** (0, +6, +12, +18 (dB)) *[EM p.28]*: Amount of boost applied when the Structure Type is 03 or 04. The booster distorts the sound by boosting the input signal (electric-guitar-style distortion); higher = stronger distortion.
  - model: `fm.pat.tmt.booster12` @ 1F 00 10 01, raw [0, 3]
- **BOOSTER (TONE 3 & 4)** (0, +6, +12, +18 (dB)) *[EM p.28]*: Same as BOOSTER for tones 3 & 4.
  - model: `fm.pat.tmt.booster34` @ 1F 00 10 03, raw [0, 3]
- **TONE SWITCH (SW) 1–4** (OFF, ON) *[EM p.18]*: Turns each of the four tones on (heard) or off (silent). Turning off unneeded tones conserves polyphony.
  - model: `fm.pat.tmt.tmtToneSwitch[]` @ 1F 00 10 05 (+3), raw [0, 1]

### VELOCITY RANGE (TMT)
*group `tmt.velocity` · EM p.40*

Per tone: which velocities make the tone sound; see concept tmt.overview.

- **VELOCITY CONTROL** (OFF, ON, RANDOM, CYCLE) *[EM p.40]*: Whether a different tone is played depending on velocity (ON) or not (OFF). RANDOM: the patch's tones sound randomly regardless of velocity. CYCLE: the tones sound consecutively regardless of velocity. Set OFF when using Matrix Control to switch tones.
  - model: `fm.pat.tmt.tmtVelocityControl` @ 1F 00 10 04, raw [0, 3]
- **TMT CONTROL SW** (OFF, ON) *[EM p.40]*: Use the Matrix Control (destination TMT) to enable (ON) or disable (OFF) sounding of different tones.
  - model: `fm.pat.common.tmtControlSwitch` @ 1F 00 00 28, raw [0, 1]
- **VELOCITY FADE LOWER** (0–127) *[EM p.40]*: What happens to the tone's level when played at a velocity lower than Velocity Range Lower (a fade). Set 0 if the tone should not sound at all below the range.
  - model: `fm.pat.tmt.tmtVelocityFadeWidthLower[]` @ 1F 00 10 0C (+3), raw [0, 127]
- **VELOCITY RANGE LOWER** (1–(UPPER)) *[EM p.40]*: Lowest velocity at which the tone sounds.
  - Matrix Control destination: TMT
  - model: `fm.pat.tmt.tmtVelocityRangeLower[]` @ 1F 00 10 0A (+3), raw [1, 127]
- **VELOCITY RANGE UPPER** ((LOWER)–127) *[EM p.40]*: Highest velocity at which the tone sounds.
  - Matrix Control destination: TMT
  - model: `fm.pat.tmt.tmtVelocityRangeUpper[]` @ 1F 00 10 0B (+3), raw [1, 127]
- **VELOCITY FADE UPPER** (0–127) *[EM p.40]*: What happens to the tone's level when played at a velocity greater than Velocity Range Upper. Set 0 if the tone should not sound at all above the range.
  - model: `fm.pat.tmt.tmtVelocityFadeWidthUpper[]` @ 1F 00 10 0D (+3), raw [0, 127]

### KEY RANGE (TMT)
*group `tmt.key` · EM p.41*

Per tone: which notes make the tone sound (keyboard split/layer).

- **KEY FADE LOWER** (0–127) *[EM p.41]*: What happens to the tone's level when a note lower than Key Range Lower is played. Set 0 if the tone should not sound at all.
  - model: `fm.pat.tmt.tmtKeyboardFadeWidthLower[]` @ 1F 00 10 08 (+3), raw [0, 127]
- **KEY RANGE LOWER** (C-1–(UPPER)) *[EM p.41]*: Lowest note at which the tone sounds.
  - model: `fm.pat.tmt.tmtKeyboardRangeLower[]` @ 1F 00 10 06 (+3), raw [0, 127]
- **KEY RANGE UPPER** ((LOWER)–G9) *[EM p.41]*: Highest note at which the tone sounds.
  - model: `fm.pat.tmt.tmtKeyboardRangeUpper[]` @ 1F 00 10 07 (+3), raw [0, 127]
- **KEY FADE UPPER** (0–127) *[EM p.41]*: What happens to the tone's level when a note higher than Key Range Upper is played. Set 0 if the tone should not sound at all.
  - model: `fm.pat.tmt.tmtKeyboardFadeWidthUpper[]` @ 1F 00 10 09 (+3), raw [0, 127]

### WG (Wave Generator): waveform and pitch
*group `tone.wg` · EM p.21, 29*

Per tone. Modifies waveform, pitch and pitch envelope.

- **Wave Group Type / Wave Group ID** (Type: ---, INT, ---, --- ; ID: OFF, 1–16384) *[MI p.13]*: Which wave bank the wave number refers to. Only INT (internal) exists on the AX-Synth.
  - Not described in the Editor manual; from the MIDI Implementation.
  - model: `fm.pat.tone[].waveGroupType` @ 1F 00 20 27 (+3), raw [0, 3]; `fm.pat.tone[].waveGroupID` @ 1F 00 20 28 (+3), raw [0, 16384]
- **WAVE NUMBER L (Mono) / R** (Off, 1–) *[EM p.21, 29, 19]*: Basic waveform of the tone. In mono only L is specified; in stereo R is also specified (select L first, then pick the matching R, whose number is L+1).
  - [F] Wave names: Script.xml stringTable internalWaveNameTableA (313 names); wave N probably = entry N-1 [I, strongly supported by the forum patches].
  - model: `fm.pat.tone[].waveNumberL` @ 1F 00 20 2C (+3), raw [0, 16384]; `fm.pat.tone[].waveNumberR` @ 1F 00 20 30 (+3), raw [0, 16384]
- **GAIN** (-6, 0, +6, +12 (dB)) *[EM p.21, 29]*: Gain (amplification) of the waveform in 6 dB steps; +6 dB doubles the gain. When using the Booster to distort the sound, set this to its maximum.
  - model: `fm.pat.tone[].waveGain` @ 1F 00 20 34 (+3), raw [0, 3]
- **FXM ON** (OFF, ON) *[EM p.21, 29]*: Whether FXM (frequency cross modulation) is used.
  - model: `fm.pat.tone[].waveFXMSwitch` @ 1F 00 20 35 (+3), raw [0, 1]
- **FXM COLOR** (1–4) *[EM p.21, 29]*: How FXM performs frequency modulation: higher settings give a grainier sound, lower settings a more metallic sound.
  - model: `fm.pat.tone[].waveFXMColor` @ 1F 00 20 36 (+3), raw [0, 3]
- **FXM DEPTH** (0–16) *[EM p.21, 29]*: Depth of the modulation produced by FXM.
  - Matrix Control destination: FXM DEPTH
  - model: `fm.pat.tone[].waveFXMDepth` @ 1F 00 20 37 (+3), raw [0, 16]
- **TUNE COARSE** (-48–+48) *[EM p.21, 29]*: Pitch of the tone's sound in semitones (±4 octaves).
  - Matrix Control destination: PITCH
  - model: `fm.pat.tone[].toneCoarseTune` @ 1F 00 20 01 (+3), raw [16, 112]
- **TUNE FINE** (-50–+50) *[EM p.21, 29]*: Pitch of the tone's sound in 1-cent steps (1/100 semitone).
  - Matrix Control destination: PITCH
  - model: `fm.pat.tone[].toneFineTune` @ 1F 00 20 02 (+3), raw [14, 114]
- **RANDOM PITCH** (0–1200 (cents; stored as 31 steps: 0–10, 20–100 by 10, 200–1200 by 100)) *[EM p.29]*: Width of random pitch deviation each time a key is pressed. Set 0 for no random pitch change.
  - model: `fm.pat.tone[].toneRandomPitchDepth` @ 1F 00 20 03 (+3), raw [0, 30]
- **PITCH KF (Pitch Keyfollow)** (-200–+200) *[EM p.29]*: Amount of pitch change when you play a key one octave higher. +100: the pitch rises one octave per octave as on a conventional keyboard; +200: two octaves.
  - model: `fm.pat.tone[].wavePitchKeyfollow` @ 1F 00 20 39 (+3), raw [44, 84]

### TONE DELAY
*group `tone.delay` · EM p.30*

See concept tone.delay_modes.

- **TONE DELAY MODE** (NORMAL, HOLD, KEY-OFF-NOR, KEY-OFF-DCY) *[EM p.30]*: NORMAL: the tone begins after the delay time. HOLD: begins after the delay time, but if the key is released before the time has elapsed the tone is not played. KEY-OFF-NOR: the tone begins the delay time after the key is released instead of while it is held (e.g. simulating guitar noises). KEY-OFF-DCY: like KEY-OFF-NOR but the TVA envelope already runs while the key is held, so often only the release portion is heard. With a decaying (one-shot) wave, KEY-OFF modes may give no sound.
  - model: `fm.pat.tone[].toneDelayMode` @ 1F 00 20 09 (+3), raw [0, 3]
- **TONE DELAY TIME** (0–127) *[EM p.30]*: Time from key press (or, in KEY-OFF modes, from key release) until the tone sounds.
  - model: `fm.pat.tone[].toneDelayTime` @ 1F 00 20 0A (+3), raw [0, 127]

### PITCH ENV (Wave Pitch Envelope)
*group `tone.pitch_env` · EM p.21, 31*

Five levels L0–L4 joined by four times T1–T4; T1 starts at note-on, T4 is the release. Levels are relative to the pitch set by coarse/fine tune.

- **DEPTH (PITCH ENV DEPTH)** (-12–+12) *[EM p.21, 31]*: Depth of the pitch envelope. Higher settings produce greater change; negative settings invert the envelope's shape.
  - model: `fm.pat.tone[].pitchEnvDepth` @ 1F 00 20 3A (+3), raw [52, 76]
- **TIME KF (Time Keyfollow)** (-100–+100) *[EM p.31]*: Makes pitch envelope times T2–T4 depend on key position. Relative to C4, positive settings make notes above C4 have increasingly shorter times.
  - model: `fm.pat.tone[].pitchEnvTimeKeyFollow` @ 1F 00 20 3E (+3), raw [54, 74]
- **VEL SENS (Velocity Sens)** (-63–+63) *[EM p.31]*: Lets keyboard dynamics control the pitch envelope depth; positive = more effect for strongly played notes.
  - model: `fm.pat.tone[].pitchEnvVelocitySens` @ 1F 00 20 3B (+3), raw [1, 127]
- **T1 SENS (T1 Velocity Sens)** (-63–+63) *[EM p.31]*: Lets keyboard dynamics affect T1; positive = T1 speeds up for strongly played notes.
  - model: `fm.pat.tone[].pitchEnvTime1VelocitySens` @ 1F 00 20 3C (+3), raw [1, 127]
- **T4 SENS (T4 Velocity Sens)** (-63–+63) *[EM p.31]*: Lets key release speed affect T4; positive = T4 speeds up for quickly released notes.
  - model: `fm.pat.tone[].pitchEnvTime4VelocitySens` @ 1F 00 20 3D (+3), raw [1, 127]
- **T1–T4 (Time 1–4)** (0–127) *[EM p.21, 31]*: Pitch envelope times; higher = longer time until the next pitch level is reached. Simplified controls: PITCH ENV A = T1, D = T3, R = T4.
  - Matrix Control destination: PCH ENV A-TIME (T1), PCH ENV D-TIME (T3), PCH ENV R-TIME (T4)
  - model: `fm.pat.tone[].pitchEnvTime1` @ 1F 00 20 3F (+3), raw [0, 127]; `fm.pat.tone[].pitchEnvTime2` @ 1F 00 20 40 (+3), raw [0, 127]; `fm.pat.tone[].pitchEnvTime3` @ 1F 00 20 41 (+3), raw [0, 127]; `fm.pat.tone[].pitchEnvTime4` @ 1F 00 20 42 (+3), raw [0, 127]
- **L0–L4 (Level 0–4)** (-63–+63) *[EM p.21, 31]*: Pitch envelope levels: how the pitch changes at each point relative to the pitch set by COARSE/FINE TUNE. Simplified control PITCH ENV S = L3.
  - model: `fm.pat.tone[].pitchEnvLevel0` @ 1F 00 20 43 (+3), raw [1, 127]; `fm.pat.tone[].pitchEnvLevel1` @ 1F 00 20 44 (+3), raw [1, 127]; `fm.pat.tone[].pitchEnvLevel2` @ 1F 00 20 45 (+3), raw [1, 127]; `fm.pat.tone[].pitchEnvLevel3` @ 1F 00 20 46 (+3), raw [1, 127]; `fm.pat.tone[].pitchEnvLevel4` @ 1F 00 20 47 (+3), raw [1, 127]

### TVF (filter)
*group `tone.tvf` · EM p.22, 32*

A filter cuts or boosts a frequency region to change the sound's brightness, thickness or other qualities.

- **FILTER TYPE** (OFF, LPF, BPF, HPF, PKG, LPF2, LPF3) *[EM p.22, 32]*: OFF: no filter. LPF (low pass): reduces all frequencies above the cutoff to round off / un-brighten the sound. BPF (band pass): leaves only frequencies around the cutoff; useful for distinctive sounds. HPF (high pass): cuts frequencies below the cutoff; suits percussive sounds emphasizing higher tones. PKG (peaking): emphasizes frequencies around the cutoff; with an LFO sweeping the cutoff gives wah-wah. LPF2: low pass with half the sensitivity of LPF; good for simulated instruments such as acoustic piano. LPF3: low pass whose sensitivity changes with the cutoff frequency; also for acoustic instruments, with a different nuance from LPF2 even with the same envelope. With LPF2/LPF3 the RES setting is ignored.
  - model: `fm.pat.tone[].tvfFilterType` @ 1F 00 20 48 (+3), raw [0, 6]
- **CUTOFF (Cutoff Frequency)** (0–127) *[EM p.22, 32]*: Frequency at which the filter begins to affect the waveform's frequency components.
  - Matrix Control destination: CUTOFF
  - model: `fm.pat.tone[].tvfCutoffFrequency` @ 1F 00 20 49 (+3), raw [0, 127]
- **RES (Resonance)** (0–127) *[EM p.22, 32]*: Emphasizes the region around the cutoff frequency, adding character. Excessively high settings can produce oscillation, causing distortion.
  - Matrix Control destination: RESONANCE
  - model: `fm.pat.tone[].tvfResonance` @ 1F 00 20 4D (+3), raw [0, 127]
- **RES VEL SENS (Resonance Velocity Sens)** (-63–+63) *[EM p.32]*: Lets velocity modify the resonance amount; positive = strongly played notes get more resonance.
  - model: `fm.pat.tone[].tvfResonanceVelocitySens` @ 1F 00 20 4E (+3), raw [1, 127]
- **CUTOFF KF (Cutoff Keyfollow)** (-200–+200) *[EM p.32]*: Makes the cutoff depend on the key played. Relative to C4, positive settings raise the cutoff for notes above C4, negative settings lower it; larger = more change.
  - model: `fm.pat.tone[].tvfCutoffKeyfollow` @ 1F 00 20 4A (+3), raw [44, 84]

### FILTER ENV (TVF Envelope) and cutoff velocity
*group `tone.tvf_env` · EM p.22, 33*

Five levels L0–L4 joined by times T1–T4, relative to the CUTOFF value.

- **VEL CURVE (Cutoff Velocity Curve)** (FIX, 1–7) *[EM p.33]*: Curve by which velocity affects the cutoff frequency. FIX: the cutoff is not affected by velocity.
  - model: `fm.pat.tone[].tvfCutoffVelocityCurve` @ 1F 00 20 4B (+3), raw [0, 7]
- **VEL SENS (Cutoff Velocity Sens)** (-63–+63) *[EM p.33]*: How playing velocity changes the cutoff; positive = strongly played notes raise the cutoff (brighter).
  - model: `fm.pat.tone[].tvfCutoffVelocitySens` @ 1F 00 20 4C (+3), raw [1, 127]
- **DEPTH (FILTER ENV DEPTH)** (-63–+63) *[EM p.22, 33]*: Depth of the TVF envelope. Higher settings produce greater change; negative settings invert the envelope's shape.
  - model: `fm.pat.tone[].tvfEnvDepth` @ 1F 00 20 4F (+3), raw [1, 127]
- **TIME KF (Time Keyfollow)** (-100–+100) *[EM p.33]*: Makes TVF envelope times T2–T4 depend on key position; relative to C4, positive = shorter times for higher notes.
  - model: `fm.pat.tone[].tvfEnvTimeKeyfollow` @ 1F 00 20 54 (+3), raw [54, 74]
- **VEL CURVE (Velocity Curve)** (FIX, 1–7) *[EM p.33]*: Curve by which velocity affects the TVF envelope. FIX: the envelope is not affected by velocity.
  - model: `fm.pat.tone[].tvfEnvVelocityCurve` @ 1F 00 20 50 (+3), raw [0, 7]
- **VEL SENS (Velocity Sens)** (-63–+63) *[EM p.33]*: How velocity affects the TVF envelope depth; positive = greater effect for strongly played notes, negative = less.
  - model: `fm.pat.tone[].tvfEnvVelocitySens` @ 1F 00 20 51 (+3), raw [1, 127]
- **T1 SENS** (-63–+63) *[EM p.33]*: Lets keyboard dynamics affect T1 of the TVF envelope; positive = T1 speeds up for strongly played notes.
  - model: `fm.pat.tone[].tvfEnvTime1VelocitySens` @ 1F 00 20 52 (+3), raw [1, 127]
- **T4 SENS** (-63–+63) *[EM p.33]*: Lets key release speed affect T4 of the TVF envelope; positive = T4 speeds up for quickly released notes.
  - model: `fm.pat.tone[].tvfEnvTime4VelocitySens` @ 1F 00 20 53 (+3), raw [1, 127]
- **T1–T4 (Time 1–4)** (0–127) *[EM p.22, 33]*: TVF envelope times; higher = longer until the next cutoff level is reached. Simplified FILTER ENV A = T1, D = T3, R = T4. The patch OFFSET ATTACK/RELEASE TIME modifies T1/T4.
  - Matrix Control destination: TVF ENV A-TIME (T1), TVF ENV D-TIME (T3), TVF ENV R-TIME (T4)
  - model: `fm.pat.tone[].tvfEnvTime1` @ 1F 00 20 55 (+3), raw [0, 127]; `fm.pat.tone[].tvfEnvTime2` @ 1F 00 20 56 (+3), raw [0, 127]; `fm.pat.tone[].tvfEnvTime3` @ 1F 00 20 57 (+3), raw [0, 127]; `fm.pat.tone[].tvfEnvTime4` @ 1F 00 20 58 (+3), raw [0, 127]
- **L0–L4 (Level 0–4)** (0–127) *[EM p.22, 33]*: TVF envelope levels: how the cutoff changes at each point relative to the CUTOFF value. Simplified FILTER ENV S = L3.
  - model: `fm.pat.tone[].tvfEnvLevel0` @ 1F 00 20 59 (+3), raw [0, 127]; `fm.pat.tone[].tvfEnvLevel1` @ 1F 00 20 5A (+3), raw [0, 127]; `fm.pat.tone[].tvfEnvLevel2` @ 1F 00 20 5B (+3), raw [0, 127]; `fm.pat.tone[].tvfEnvLevel3` @ 1F 00 20 5C (+3), raw [0, 127]; `fm.pat.tone[].tvfEnvLevel4` @ 1F 00 20 5D (+3), raw [0, 127]

### TVA (amplifier): level, velocity, bias, pan
*group `tone.tva` · EM p.23, 34, 35*

TVA adjusts the volume and stereo position of the tone.

- **LEVEL** (0–127) *[EM p.23, 34]*: Volume of the tone; mainly for adjusting the volume balance between tones.
  - Matrix Control destination: LEVEL
  - model: `fm.pat.tone[].toneLevel` @ 1F 00 20 00 (+3), raw [0, 127]
- **VEL CURVE (Velocity Curve)** (FIX, 1–7) *[EM p.34]*: Curve by which velocity affects the volume. FIX: the tone's volume is not affected by velocity.
  - model: `fm.pat.tone[].tvaLevelVelocityCurve` @ 1F 00 20 61 (+3), raw [0, 7]
- **VEL SENS (Velocity Sens)** (-63–+63) *[EM p.34]*: How playing dynamics change the tone's volume; positive = louder the harder you play; negative = softer the harder you play.
  - model: `fm.pat.tone[].tvaLevelVelocitySens` @ 1F 00 20 62 (+3), raw [1, 127]
- **BIAS LEVEL** (-100–+100) *[EM p.34]*: Bias makes the volume depend on keyboard position (useful for acoustic instruments). BIAS LEVEL is the angle of the volume change in the selected direction; larger = more change; negative inverts the direction.
  - model: `fm.pat.tone[].biasLevel` @ 1F 00 20 5E (+3), raw [54, 74]
- **BIAS POSITION** (C-1–G9) *[EM p.34]*: Key relative to which the volume is modified.
  - model: `fm.pat.tone[].biasPosition` @ 1F 00 20 5F (+3), raw [0, 127]
- **BIAS DIRECTION** (LOWER, UPPER, LO&UP, ALL) *[EM p.34]*: LOWER: volume modified below the bias position. UPPER: above it. LO&UP: symmetrically on both sides. ALL: volume changes linearly with the bias position at the center.
  - model: `fm.pat.tone[].biasDirection` @ 1F 00 20 60 (+3), raw [0, 3]
- **PAN** (L64–0–63R) *[EM p.23, 35]*: Left/right position of the tone.
  - Matrix Control destination: PAN
  - model: `fm.pat.tone[].tonePan` @ 1F 00 20 04 (+3), raw [0, 127]
- **PAN KF (Pan Keyfollow)** (-100–+100) *[EM p.35]*: Makes key position affect panning: positive = notes above C4 pan increasingly to the right; negative = to the left; larger = more change. With Structure TYPE 02–10 tone 1 (3) follows tone 2 (4).
  - model: `fm.pat.tone[].tonePanKeyfollow` @ 1F 00 20 05 (+3), raw [54, 74]
- **RANDOM PAN DEPTH** (0–63) *[EM p.35]*: Stereo position changes randomly each time a key is pressed; higher = more change.
  - model: `fm.pat.tone[].toneRandomPanDepth` @ 1F 00 20 06 (+3), raw [0, 63]
- **ALT. PAN DEPTH (Alternate Pan Depth)** (L63–0–63R) *[EM p.35]*: Panning alternates between left and right each time a key is pressed; higher = more change. L or R reverses the alternation order: two tones set to L and R respectively alternate opposite to each other.
  - model: `fm.pat.tone[].toneAlternatePanDepth` @ 1F 00 20 07 (+3), raw [1, 127]

### AMP ENV (TVA Envelope)
*group `tone.tva_env` · EM p.23, 36*

Four times T1–T4 and three levels L1–L3 (level 0 at start and end), relative to the LEVEL value.

- **TIME KF (Time Keyfollow)** (-100–+100) *[EM p.36]*: Makes TVA envelope times T2–T4 depend on key position; relative to C4, positive = shorter times for higher notes, negative = longer; larger = more change.
  - model: `fm.pat.tone[].tvaEnvTimeKeyfollow` @ 1F 00 20 65 (+3), raw [54, 74]
- **T1 SENS** (-63–+63) *[EM p.36]*: Lets keyboard dynamics affect T1 (attack) of the TVA envelope; positive = faster for strongly played notes, negative = slower.
  - model: `fm.pat.tone[].tvaEnvTime1VelocitySens` @ 1F 00 20 63 (+3), raw [1, 127]
- **T4 SENS** (-63–+63) *[EM p.36]*: Lets key release speed affect T4 (release); positive = faster for quickly released notes, negative = slower.
  - model: `fm.pat.tone[].tvaEnvTime4VelocitySens` @ 1F 00 20 64 (+3), raw [1, 127]
- **T1–T4 (Time 1–4)** (0–127) *[EM p.23, 36]*: TVA envelope times; higher = longer until the next volume level is reached. Simplified AMP ENV A = T1, D = T3, R = T4. The patch OFFSET ATTACK/RELEASE TIME modifies T1/T4.
  - Matrix Control destination: TVA ENV A-TIME (T1), TVA ENV D-TIME (T3), TVA ENV R-TIME (T4)
  - model: `fm.pat.tone[].tvaEnvTime1` @ 1F 00 20 66 (+3), raw [0, 127]; `fm.pat.tone[].tvaEnvTime2` @ 1F 00 20 67 (+3), raw [0, 127]; `fm.pat.tone[].tvaEnvTime3` @ 1F 00 20 68 (+3), raw [0, 127]; `fm.pat.tone[].tvaEnvTime4` @ 1F 00 20 69 (+3), raw [0, 127]
- **L1–L3 (Level 1–3)** (0–127) *[EM p.23, 36]*: TVA envelope levels: how the volume changes at each point relative to LEVEL. Simplified AMP ENV S = L3 (sustain level).
  - model: `fm.pat.tone[].tvaEnvLevel1` @ 1F 00 20 6A (+3), raw [0, 127]; `fm.pat.tone[].tvaEnvLevel2` @ 1F 00 20 6B (+3), raw [0, 127]; `fm.pat.tone[].tvaEnvLevel3` @ 1F 00 20 6C (+3), raw [0, 127]

### Tone OUTPUT and send levels
*group `tone.output` · EM p.15, 23, 37*

Where each tone's direct sound goes and how much of it is sent to chorus and reverb. Sounds are always sent to chorus and reverb in mono.

- **OUTPUT ASSIGN (TONE OUTPUT ASSIGN)** (MFX, L+R, L, R) *[EM p.15, 37]*: How the tone's direct sound is output. MFX: stereo through the multi-effect (chorus/reverb can follow). L+R: stereo to the OUTPUT jacks bypassing the MFX. L / R: mono to OUTPUT L / R bypassing the MFX. Valid only if PATCH OUTPUT ASSIGN is TONE. With Structure TYPE 02–10 tone 1 (3) follows tone 2 (4).
  - [F] Legal stored values 0, 1, 5, 6 (numberTable toneOutputAssignXV5050Table).
  - model: `fm.pat.tone[].toneOutputAssign` @ 1F 00 20 11 (+3), raw [0, 12]
- **SEND LEVEL OUT (Output Level / TONE OUTPUT LEVEL)** (0–127) *[EM p.15, 23, 37]*: Level of the tone's signal sent to the destination set by OUTPUT ASSIGN.
  - Matrix Control destination: OUTPUT LEVEL
  - model: `fm.pat.tone[].toneDrySendLevel` @ 1F 00 20 0C (+3), raw [0, 127]
- **CHO (Chorus Send), OUTPUT ASSIGN = MFX** (0–127) *[EM p.23, 37]*: Level sent to chorus for the tone when the tone goes through the MFX.
  - Matrix Control destination: CHORUS SEND
  - model: `fm.pat.tone[].toneChorusSendLevelMFX` @ 1F 00 20 0D (+3), raw [0, 127]
- **REV (Reverb Send), OUTPUT ASSIGN = MFX** (0–127) *[EM p.23, 37]*: Level sent to reverb for the tone when the tone goes through the MFX.
  - Matrix Control destination: REVERB SEND
  - model: `fm.pat.tone[].toneReverbSendLevelMFX` @ 1F 00 20 0E (+3), raw [0, 127]
- **CHO (Chorus Send), OUTPUT ASSIGN = non MFX** (0–127) *[EM p.23, 37]*: Level sent to chorus for the tone when the tone does not go through the MFX.
  - Matrix Control destination: CHORUS SEND
  - model: `fm.pat.tone[].toneChorusSendLevelNonMFX` @ 1F 00 20 0F (+3), raw [0, 127]
- **REV (Reverb Send), OUTPUT ASSIGN = non MFX** (0–127) *[EM p.23, 37]*: Level sent to reverb for the tone when the tone does not go through the MFX.
  - Matrix Control destination: REVERB SEND
  - [D OM p.26] The on-device 'reU' (Reverb Send) edit changes a reverb send of regular patches and can only be saved to FAVORITE memories; which address it changes is unverified.
  - model: `fm.pat.tone[].toneReverbSendLevelNonMFX` @ 1F 00 20 10 (+3), raw [0, 127]

### LFO1 / LFO2
*group `tone.lfo` · EM p.20, 21, 37, 38, 39*

Each tone has two LFOs with identical parameters. They cyclically change pitch (vibrato), cutoff (wah), volume (tremolo) and pan. Schema arrays: [0] = LFO1, [1] = LFO2. With Structure TYPE 02–10, tone 1 (3) follows tone 2 (4). See concept lfo.fade_modes.

- **WAVEFORM** (SIN, TRI, SAW-UP, SAW-DW, SQR, RND, BEND-UP, BEND-DW, TRP, S&H, CHS, VSIN, STEP) *[EM p.20, 37]*: SIN sine; TRI triangle; SAW-UP sawtooth; SAW-DW sawtooth (negative polarity); SQR square; RND random; BEND-UP: once the attack of the LFO waveform has developed normally, it continues without further change; BEND-DW: once the decay has developed normally, it continues without further change; TRP trapezoid; S&H sample & hold (value changes once per cycle); CHS chaos; VSIN modified sine whose amplitude is randomly varied once each cycle; STEP: waveform generated from LFO STEP 1–16 (stepped change with a fixed pattern, like a step modulator). BEND-UP/BEND-DW require KEY TRIGGER ON, otherwise they have no effect.
  - model: `fm.pat.tone[].lfoWaveForm[]` @ 1F 00 20 6D (+7), raw [0, 12]
- **RATE (RATE VALUE)** (0–127) *[EM p.20, 38]*: Modulation speed of the LFO. Ignored when WAVEFORM is CHS.
  - Matrix Control destination: LFO1 RATE / LFO2 RATE
  - model: `fm.pat.tone[].lfoRate[]` @ 1F 00 20 6E (+7), raw [0, 127]
- **OFFSET** (-100, -50, 0, +50, +100) *[EM p.38]*: Raises or lowers the LFO waveform relative to the central value (pitch or cutoff). Positive: modulation occurs upward from the central value. Negative: downward.
  - model: `fm.pat.tone[].lfoOffset[]` @ 1F 00 20 70 (+7), raw [0, 4]
- **RATE DETUNE** (0–127) *[EM p.38]*: Subtly changes the LFO rate each time a key is pressed; higher = greater change.
  - model: `fm.pat.tone[].lfoRateDetune[]` @ 1F 00 20 71 (+7), raw [0, 127]
- **DELAY (DELAY TIME)** (0–127) *[EM p.21, 38]*: Time before the LFO effect is applied (or continues) after the key is pressed (or released), depending on FADE MODE. For violin, wind and similar sounds, adding vibrato only after the note has been drawn out can be effective.
  - model: `fm.pat.tone[].lfoDelayTime[]` @ 1F 00 20 72 (+7), raw [0, 127]
- **DELAY KEYFOLLOW (Delay Time Keyfollow)** (-100–+100) *[EM p.38]*: Adjusts DELAY TIME by key position relative to C4; positive = shorter delay for notes above C4.
  - model: `fm.pat.tone[].lfoDelayTimeKeyfollow[]` @ 1F 00 20 73 (+7), raw [54, 74]
- **FADE MODE** (ON-IN, ON-OUT, OFF-IN, OFF-OUT) *[EM p.38, 39]*: How the LFO is applied over time (fade in/out after key on/off). See concept lfo.fade_modes.
  - model: `fm.pat.tone[].lfoFadeMode[]` @ 1F 00 20 74 (+7), raw [0, 3]
- **FADE TIME** (0–127) *[EM p.38]*: Time over which the LFO amplitude reaches its maximum (or minimum), per FADE MODE.
  - model: `fm.pat.tone[].lfoFadeTime[]` @ 1F 00 20 75 (+7), raw [0, 127]
- **KEY TRIGGER** (OFF, ON) *[EM p.38]*: Whether the LFO cycle restarts in sync with each key press (ON) or free-runs (OFF). Required ON for BEND-UP/BEND-DW waveforms.
  - model: `fm.pat.tone[].lfoKeyTrigger[]` @ 1F 00 20 76 (+7), raw [0, 1]
- **DEPTH PITCH** (-63–+63) *[EM p.21, 38]*: How deeply the LFO affects pitch (vibrato). Opposite signs on two tones give opposite modulation phase.
  - Matrix Control destination: LFO1 PCH DEPTH / LFO2 PCH DEPTH
  - model: `fm.pat.tone[].lfoPitchDepth[]` @ 1F 00 20 77 (+7), raw [1, 127]
- **DEPTH TVF** (-63–+63) *[EM p.21, 38]*: How deeply the LFO affects the cutoff frequency (wah).
  - Matrix Control destination: LFO1 TVF DEPTH / LFO2 TVF DEPTH
  - model: `fm.pat.tone[].lfoTvfDepth[]` @ 1F 00 20 78 (+7), raw [1, 127]
- **DEPTH TVA** (-63–+63) *[EM p.21, 38]*: How deeply the LFO affects the volume (tremolo).
  - Matrix Control destination: LFO1 TVA DEPTH / LFO2 TVA DEPTH
  - model: `fm.pat.tone[].lfoTvaDepth[]` @ 1F 00 20 79 (+7), raw [1, 127]
- **DEPTH PAN** (-63–+63) *[EM p.21, 38]*: How deeply the LFO affects the pan (auto-pan).
  - Matrix Control destination: LFO1 PAN DEPTH / LFO2 PAN DEPTH
  - model: `fm.pat.tone[].lfoPanDepth[]` @ 1F 00 20 7A (+7), raw [1, 127]

### STEP LFO
*group `tone.step_lfo` · EM p.39*

Data for LFO waveform STEP (one set per tone, shared by LFO1 and LFO2).

- **STEP TYPE** (TYPE1, TYPE2) *[EM p.39]*: Whether the step LFO level changes abruptly at each step (TYPE1: stair-step) or is connected linearly (TYPE2: linear).
  - model: `fm.pat.tone[].lfoStepType` @ 1F 00 21 09 (+3), raw [0, 1]
- **STEP 1–16** (-36–+36) *[EM p.39]*: Step LFO data. With LFO PITCH DEPTH +63, each +1 unit of step data corresponds to +50 cents.
  - model: `fm.pat.tone[].lfoStep1` @ 1F 00 21 0A (+3), raw [28, 100]; `fm.pat.tone[].lfoStep2` @ 1F 00 21 0B (+3), raw [28, 100]; `fm.pat.tone[].lfoStep3` @ 1F 00 21 0C (+3), raw [28, 100]; `fm.pat.tone[].lfoStep4` @ 1F 00 21 0D (+3), raw [28, 100]; `fm.pat.tone[].lfoStep5` @ 1F 00 21 0E (+3), raw [28, 100]; `fm.pat.tone[].lfoStep6` @ 1F 00 21 0F (+3), raw [28, 100]; `fm.pat.tone[].lfoStep7` @ 1F 00 21 10 (+3), raw [28, 100]; `fm.pat.tone[].lfoStep8` @ 1F 00 21 11 (+3), raw [28, 100]; `fm.pat.tone[].lfoStep9` @ 1F 00 21 12 (+3), raw [28, 100]; `fm.pat.tone[].lfoStep10` @ 1F 00 21 13 (+3), raw [28, 100]; `fm.pat.tone[].lfoStep11` @ 1F 00 21 14 (+3), raw [28, 100]; `fm.pat.tone[].lfoStep12` @ 1F 00 21 15 (+3), raw [28, 100]; `fm.pat.tone[].lfoStep13` @ 1F 00 21 16 (+3), raw [28, 100]; `fm.pat.tone[].lfoStep14` @ 1F 00 21 17 (+3), raw [28, 100]; `fm.pat.tone[].lfoStep15` @ 1F 00 21 18 (+3), raw [28, 100]; `fm.pat.tone[].lfoStep16` @ 1F 00 21 19 (+3), raw [28, 100]

### CONTROL SW (per-tone MIDI reception and envelope mode)
*group `tone.control_sw` · EM p.43*

Per-tone switches for which MIDI messages affect the tone.

- **RCV BENDER (Receive Bender)** (OFF, ON) *[EM p.43]*: Whether this tone receives MIDI Pitch Bend.
  - model: `fm.pat.tone[].toneReceiveBender` @ 1F 00 20 12 (+3), raw [0, 1]
- **RCV EXP (Receive Expression)** (OFF, ON) *[EM p.43]*: Whether this tone receives MIDI Expression (CC11).
  - model: `fm.pat.tone[].toneReceiveExpression` @ 1F 00 20 13 (+3), raw [0, 1]
- **RCV HOLD-1 (Receive Hold-1)** (OFF, ON) *[EM p.43]*: Whether this tone receives MIDI Hold-1 (CC64). No effect if ENV MODE is NO-SUS.
  - model: `fm.pat.tone[].toneReceiveHold-1` @ 1F 00 20 14 (+3), raw [0, 1]
- **REDAMPER** (OFF, ON) *[EM p.43]*: Whether the sound is held when Hold 1 is received after a key is released but before the sound has decayed to silence; set ON to sustain. Effective for piano sounds. Requires RCV HOLD-1 ON.
  - model: `fm.pat.tone[].toneRedamperSwitch` @ 1F 00 20 16 (+3), raw [0, 1]
- **RCV PAN MODE (Receive Pan Mode)** (CONTINUOUS, KEY-ON) *[EM p.43]*: How Pan messages are received. CONTINUOUS: the stereo position changes whenever a Pan message arrives. KEY-ON: the pan changes only when the next note is played. Pan messages cannot be ignored entirely.
  - model: `fm.pat.tone[].toneReceivePanMode` @ 1F 00 20 15 (+3), raw [0, 1]
- **ENV MODE (Envelope Mode)** (NO-SUS, SUSTAIN) *[EM p.43]*: With a loop waveform the sound normally continues while the key is held; NO-SUS makes it decay naturally even with the key held. A one-shot wave does not sustain even with SUSTAIN.
  - model: `fm.pat.tone[].toneEnvMode` @ 1F 00 20 08 (+3), raw [0, 1]

### MATRIX CONTROL 1–4
*group `common.matrix` · EM p.41, 42*

Four matrix controls per patch; each has one SOURCE and up to four DESTINATION/SENS pairs. See concept matrix.overview.

- **SOURCE 1–4** (OFF, CC01–31, CC33–95, PITCH BEND, AFTERTOUCH, VELOCITY, KEYFOLLOW, LFO1, LFO2, PITCH ENV, TVF ENV, TVA ENV) *[EM p.41]*: Message used to change tone parameters. OFF: not used. CC01–31, 33–95: controller numbers. PITCH BEND. AFTERTOUCH. VELOCITY: how hard the key is pressed. KEYFOLLOW: keyboard position with C4 = 0. LFO1, LFO2, PITCH ENV, TVF ENV, TVA ENV: internal modulators.
  - [F] Stored index keeps a placeholder at 32, so raw value = CC number (raw 70 = CC70). The MIDI Implementation also lists unused slots ('---') between AFT and VELOCITY and between KEYFOLLOW and LFO1.
  - model: `fm.pat.common.matrixControl1Source` @ 1F 00 00 2B, raw [0, 109]; `fm.pat.common.matrixControl2Source` @ 1F 00 00 34, raw [0, 109]; `fm.pat.common.matrixControl3Source` @ 1F 00 00 3D, raw [0, 109]; `fm.pat.common.matrixControl4Source` @ 1F 00 00 46, raw [0, 109]
- **DESTINATION 1–4** (OFF, PITCH, CUTOFF, RESONANCE, LEVEL, PAN, OUTPUT LEVEL, CHORUS SEND, REVERB SEND, LFO1/2 PCH DEPTH, LFO1/2 TVF DEPTH, LFO1/2 TVA DEPTH, LFO1/2 PAN DEPTH, LFO1/2 RATE, PCH ENV A-TIME, PCH ENV D-TIME, PCH ENV R-TIME, TVF ENV A-TIME, TVF ENV D-TIME, TVF ENV R-TIME, TVA ENV A-TIME, TVA ENV D-TIME, TVA ENV R-TIME, TMT, FXM DEPTH, MFX-CTRL1–4) *[EM p.42]*: Tone parameters controlled by the matrix control; up to four per matrix control, controlled simultaneously. MFX-CTRL1–4 route to the multi-effect control parameters. TMT switches tones (with TMT CONTROL SW ON).
  - model: `fm.pat.common.matrixControl1Destination1` @ 1F 00 00 2C, raw [0, 33]; `fm.pat.common.matrixControl1Destination2` @ 1F 00 00 2E, raw [0, 33]; `fm.pat.common.matrixControl1Destination3` @ 1F 00 00 30, raw [0, 33]; `fm.pat.common.matrixControl1Destination4` @ 1F 00 00 32, raw [0, 33]; `fm.pat.common.matrixControl2Destination1` @ 1F 00 00 35, raw [0, 33]; `fm.pat.common.matrixControl2Destination2` @ 1F 00 00 37, raw [0, 33]; `fm.pat.common.matrixControl2Destination3` @ 1F 00 00 39, raw [0, 33]; `fm.pat.common.matrixControl2Destination4` @ 1F 00 00 3B, raw [0, 33]; `fm.pat.common.matrixControl3Destination1` @ 1F 00 00 3E, raw [0, 33]; `fm.pat.common.matrixControl3Destination2` @ 1F 00 00 40, raw [0, 33]; `fm.pat.common.matrixControl3Destination3` @ 1F 00 00 42, raw [0, 33]; `fm.pat.common.matrixControl3Destination4` @ 1F 00 00 44, raw [0, 33]; `fm.pat.common.matrixControl4Destination1` @ 1F 00 00 47, raw [0, 33]; `fm.pat.common.matrixControl4Destination2` @ 1F 00 00 49, raw [0, 33]; `fm.pat.common.matrixControl4Destination3` @ 1F 00 00 4B, raw [0, 33]; `fm.pat.common.matrixControl4Destination4` @ 1F 00 00 4D, raw [0, 33]
- **SENS 1–4** (-63–+63) *[EM p.42]*: Amount of the matrix control's effect. Positive: modifies the destination in the positive direction (higher, to the right, faster, ...) from its current setting; negative: in the negative direction. Larger absolute values = more change; 0 = no effect.
  - model: `fm.pat.common.matrixControl1Sens1` @ 1F 00 00 2D, raw [1, 127]; `fm.pat.common.matrixControl1Sens2` @ 1F 00 00 2F, raw [1, 127]; `fm.pat.common.matrixControl1Sens3` @ 1F 00 00 31, raw [1, 127]; `fm.pat.common.matrixControl1Sens4` @ 1F 00 00 33, raw [1, 127]; `fm.pat.common.matrixControl2Sens1` @ 1F 00 00 36, raw [1, 127]; `fm.pat.common.matrixControl2Sens2` @ 1F 00 00 38, raw [1, 127]; `fm.pat.common.matrixControl2Sens3` @ 1F 00 00 3A, raw [1, 127]; `fm.pat.common.matrixControl2Sens4` @ 1F 00 00 3C, raw [1, 127]; `fm.pat.common.matrixControl3Sens1` @ 1F 00 00 3F, raw [1, 127]; `fm.pat.common.matrixControl3Sens2` @ 1F 00 00 41, raw [1, 127]; `fm.pat.common.matrixControl3Sens3` @ 1F 00 00 43, raw [1, 127]; `fm.pat.common.matrixControl3Sens4` @ 1F 00 00 45, raw [1, 127]; `fm.pat.common.matrixControl4Sens1` @ 1F 00 00 48, raw [1, 127]; `fm.pat.common.matrixControl4Sens2` @ 1F 00 00 4A, raw [1, 127]; `fm.pat.common.matrixControl4Sens3` @ 1F 00 00 4C, raw [1, 127]; `fm.pat.common.matrixControl4Sens4` @ 1F 00 00 4E, raw [1, 127]
- **TONE 1–4 (Tone Switch 1–4)** (OFF, ON, REV) *[EM p.42]*: Which tones the matrix control affects. OFF: not applied. ON: applied. REV: applied in reverse.
  - [I] Storage is per tone: toneControl{c}Switch{d} in tone t is the switch for matrix control c, destination d, applied to tone t (the MIDI Implementation lists 'Tone Control c Switch d' inside each Patch Tone block).
  - model: `fm.pat.tone[].toneControl1Switch1` @ 1F 00 20 17 (+3), raw [0, 2]; `fm.pat.tone[].toneControl1Switch2` @ 1F 00 20 18 (+3), raw [0, 2]; `fm.pat.tone[].toneControl1Switch3` @ 1F 00 20 19 (+3), raw [0, 2]; `fm.pat.tone[].toneControl1Switch4` @ 1F 00 20 1A (+3), raw [0, 2]; `fm.pat.tone[].toneControl2Switch1` @ 1F 00 20 1B (+3), raw [0, 2]; `fm.pat.tone[].toneControl2Switch2` @ 1F 00 20 1C (+3), raw [0, 2]; `fm.pat.tone[].toneControl2Switch3` @ 1F 00 20 1D (+3), raw [0, 2]; `fm.pat.tone[].toneControl2Switch4` @ 1F 00 20 1E (+3), raw [0, 2]; `fm.pat.tone[].toneControl3Switch1` @ 1F 00 20 1F (+3), raw [0, 2]; `fm.pat.tone[].toneControl3Switch2` @ 1F 00 20 20 (+3), raw [0, 2]; `fm.pat.tone[].toneControl3Switch3` @ 1F 00 20 21 (+3), raw [0, 2]; `fm.pat.tone[].toneControl3Switch4` @ 1F 00 20 22 (+3), raw [0, 2]; `fm.pat.tone[].toneControl4Switch1` @ 1F 00 20 23 (+3), raw [0, 2]; `fm.pat.tone[].toneControl4Switch2` @ 1F 00 20 24 (+3), raw [0, 2]; `fm.pat.tone[].toneControl4Switch3` @ 1F 00 20 25 (+3), raw [0, 2]; `fm.pat.tone[].toneControl4Switch4` @ 1F 00 20 26 (+3), raw [0, 2]

### PATCH EFFECTS: ROUTING
*group `fx.routing` · EM p.14, 15*

One MFX, one chorus and one reverb per patch. Patch/tone OUTPUT ASSIGN and the tone send levels (tone.output group) decide what reaches which effect.


### Multi-effect (MFX) settings
*group `fx.mfx` · EM p.15, 16*

Type-specific parameters: knowledge/mfx.toml.

- **MFX TYPE** (00: THROUGH – 78: SYMPATHETIC RESONANCE) *[EM p.15, 16]*: Type of multi-effect. 00 THROUGH = no multi-effect. See knowledge/mfx.toml for the 78 types.
  - model: `fm.pat.mfx.mfxType` @ 1F 00 02 00, raw [0, 78]
- **MFX OUTPUT LEVEL (SEND LEVEL OUT)** (0–127) *[EM p.15, 16]*: Volume of the sound processed by the multi-effect.
  - model: `fm.pat.mfx.mfxDrySendLevel` @ 1F 00 02 01, raw [0, 127]
- **MFX CHORUS SEND LEVEL (CHO)** (0–127) *[EM p.15, 16]*: Amount of chorus applied to the sound processed by the multi-effect.
  - model: `fm.pat.mfx.mfxChorusSendLevel` @ 1F 00 02 02, raw [0, 127]
- **MFX REVERB SEND LEVEL (REV)** (0–127) *[EM p.15, 16]*: Amount of reverb applied to the sound processed by the multi-effect.
  - model: `fm.pat.mfx.mfxReverbSendLevel` @ 1F 00 02 03, raw [0, 127]
- **MFX Output Assign** (A, ---, ---, ---) *[MI p.10]*: Output of the multi-effect. Only 'A' exists; the MIDI Implementation marks it as ignored on reception.
  - model: `fm.pat.mfx.mfxOutputAssign` @ 1F 00 02 04, raw [0, 1]

### MFX CONTROL (Multi-Effect Control 1–4)
*group `fx.mfx_control` · EM p.16*

See concept mfx.control.

- **CONTROL SOURCE 1–4** (OFF, CC01–31, CC33–95, PITCH BEND, AFTERTOUCH) *[EM p.16]*: MIDI message that controls the corresponding MFX control parameter. OFF: not used.
  - [F] Same index rule as matrix source (raw = CC number, 97 = AFTERTOUCH).
  - model: `fm.pat.mfx.mfxControl1Source` @ 1F 00 02 05, raw [0, 97]; `fm.pat.mfx.mfxControl2Source` @ 1F 00 02 07, raw [0, 97]; `fm.pat.mfx.mfxControl3Source` @ 1F 00 02 09, raw [0, 97]; `fm.pat.mfx.mfxControl4Source` @ 1F 00 02 0B, raw [0, 97]
- **DESTINATION 1–4** (per MFX type (parameters marked '#' in knowledge/mfx.toml), OFF, 1–16) *[EM p.16]*: Which MFX parameter the CONTROL SOURCE controls. The selectable parameters depend on the MFX type.
  - [F] Script.xml has a '<type>-destinationTable' string table per MFX type listing the destinations in index order.
  - model: `fm.pat.mfx.mfxControlAssign1` @ 1F 00 02 0D, raw [0, 16]; `fm.pat.mfx.mfxControlAssign2` @ 1F 00 02 0E, raw [0, 16]; `fm.pat.mfx.mfxControlAssign3` @ 1F 00 02 0F, raw [0, 16]; `fm.pat.mfx.mfxControlAssign4` @ 1F 00 02 10, raw [0, 16]
- **SENS 1–4** (-63–+63) *[EM p.16]*: Depth of multi-effect control. Positive changes the destination in the positive direction (larger, toward the right, faster, ...), negative in the negative direction; larger values give more control.
  - model: `fm.pat.mfx.mfxControl1Sens` @ 1F 00 02 06, raw [1, 127]; `fm.pat.mfx.mfxControl2Sens` @ 1F 00 02 08, raw [1, 127]; `fm.pat.mfx.mfxControl3Sens` @ 1F 00 02 0A, raw [1, 127]; `fm.pat.mfx.mfxControl4Sens` @ 1F 00 02 0C, raw [1, 127]

### Chorus unit settings
*group `fx.chorus` · EM p.15, 17, 77*

Type-specific parameters: knowledge/chorus_reverb.toml.

- **CHORUS TYPE** (OFF, CHORUS, DELAY) *[EM p.15, 17, 77]*: OFF: chorus/delay not used. CHORUS: chorus. DELAY: the chorus unit works as a stereo delay.
  - model: `fm.pat.cho.chorusType` @ 1F 00 04 00, raw [0, 2]
- **CHORUS LEVEL** (0–127) *[EM p.15, 17, 77]*: Volume of the sound processed by the chorus.
  - model: `fm.pat.cho.chorusLevel` @ 1F 00 04 01, raw [0, 127]
- **CHORUS OUTPUT SELECT** (MAIN, MAIN+REV, REV) *[EM p.15, 17]*: Destination of the chorus output. MAIN: stereo to the OUTPUT jacks. MAIN+REV: stereo to OUTPUT and mono to the reverb. REV: mono to the reverb only.
  - [F] Stored order is MAIN, REV, MAIN+REV (MIDI Implementation: 0 MAIN, 1 REV, 2 MAIN+REV).
  - model: `fm.pat.cho.chorusOutputSelect` @ 1F 00 04 03, raw [0, 2]
- **Chorus Output Assign** (A, ---, ---, ---) *[MI p.11]*: Output of the chorus; only 'A' exists; ignored on reception.
  - model: `fm.pat.cho.chorusOutputAssign` @ 1F 00 04 02, raw [0, 3]

### Reverb unit settings
*group `fx.reverb` · EM p.15, 17, 78*

Type-specific parameters: knowledge/chorus_reverb.toml.

- **REVERB TYPE** (OFF, REVERB, SRV ROOM, SRV HALL, SRV PLATE) *[EM p.15, 17, 78]*: OFF: not used. REVERB: basic reverb (with room/stage/hall and delay variations). SRV ROOM: simulates room reverberation in greater detail. SRV HALL: simulates hall reverberation in greater detail. SRV PLATE: simulation of plate echo (a reverb device using a vibrating metal plate).
  - model: `fm.pat.rev.reverbType` @ 1F 00 06 00, raw [0, 4]
- **REVERB LEVEL** (0–127) *[EM p.15, 17, 78]*: Volume of the sound processed by the reverb.
  - model: `fm.pat.rev.reverbLevel` @ 1F 00 06 01, raw [0, 127]
- **Reverb Output Assign** (A, ---, ---, ---) *[MI p.11]*: Output of the reverb; only 'A' exists; ignored on reception.
  - model: `fm.pat.rev.reverbOutputAssign` @ 1F 00 06 02, raw [0, 3]

### System COMMON
*group `system.common` · EM p.12*

Global settings stored in System memory (address 02 00 00 00, System Common block).

- **MASTER LEVEL** (0–127) *[EM p.12, 20]*: Volume of the entire AX-Synth.
  - model: `fm.system.common.masterLevel` @ 02 00 00 05, raw [0, 127]
- **MASTER TUNE** (415.3–466.2 Hz) *[EM p.12]*: Overall tuning of the AX-Synth. The display shows the frequency of the A4 note (center A).
  - [D OM p.21] Factory default 440 Hz; also settable on the panel ([SHIFT]+[TRANSPOSE]).
  - model: `fm.system.common.masterTune` @ 02 00 00 00, raw [24, 2024]
- **MASTER KEY SHIFT** (-24–+24) *[EM p.12]*: Shifts the overall pitch of the AX-Synth in semitone steps.
  - model: `fm.system.common.masterKeyShift` @ 02 00 00 04, raw [40, 88]
- **PATCH RX/TX CH (Patch Rx/Tx Channel)** (1–16) *[EM p.12, 20]*: Channel used to transmit and receive MIDI messages for the Keyboard part.
  - [D OM p.27] Receive channel always equals the transmit channel; set on the panel with [SHIFT]+[TX ON]+key.
  - model: `fm.system.common.kbdPatchRxTxChannel` @ 02 00 00 0A, raw [0, 15]
- **RCV PC (Receive Program Change)** (OFF, ON) *[EM p.12]*: Specifies whether Program Change messages will be received (ON) or not (OFF).
  - model: `fm.system.common.receiveProgramChange` @ 02 00 00 1C, raw [0, 1]
- **RCV BS (Receive Bank Select)** (OFF, ON) *[EM p.12]*: Specifies whether Bank Select messages will be received (ON) or not (OFF).
  - model: `fm.system.common.receiveBankSelect` @ 02 00 00 1D, raw [0, 1]
- **SCALE TUNE SWITCH** (OFF, ON) *[EM p.12]*: Turn this on when you wish to use a tuning scale other than equal temperament.
  - model: `fm.system.common.scaleTuneSwitch` @ 02 00 00 06, raw [0, 1]
- **PATCH SCALE TUNE C–B** (-64–+63 (cents)) *[EM p.12]*: Pitch of each note of the octave relative to equal temperament, in one-cent units (1 cent = 1/100 semitone), allowing temperaments other than equal temperament. One set of Scale Tune settings can be created; it also applies to MIDI messages received from an external device.
  - Despite the 'patch' name these values are in System Common (one global set).
  - model: `fm.system.common.patchScaleTuneForC` @ 02 00 00 0C, raw [0, 127]; `fm.system.common.patchScaleTuneForC#` @ 02 00 00 0D, raw [0, 127]; `fm.system.common.patchScaleTuneForD` @ 02 00 00 0E, raw [0, 127]; `fm.system.common.patchScaleTuneForD#` @ 02 00 00 0F, raw [0, 127]; `fm.system.common.patchScaleTuneForE` @ 02 00 00 10, raw [0, 127]; `fm.system.common.patchScaleTuneForF` @ 02 00 00 11, raw [0, 127]; `fm.system.common.patchScaleTuneForF#` @ 02 00 00 12, raw [0, 127]; `fm.system.common.patchScaleTuneForG` @ 02 00 00 13, raw [0, 127]; `fm.system.common.patchScaleTuneForG#` @ 02 00 00 14, raw [0, 127]; `fm.system.common.patchScaleTuneForA` @ 02 00 00 15, raw [0, 127]; `fm.system.common.patchScaleTuneForA#` @ 02 00 00 16, raw [0, 127]; `fm.system.common.patchScaleTuneForB` @ 02 00 00 17, raw [0, 127]

### System CONTROLLER
*group `system.controller` · EM p.13*

Controller behaviour stored in System memory (address 02 00 40 00).

- **KEYBOARD VELOCITY** (REAL, 1–127) *[EM p.13]*: Velocity value transmitted when you play the keyboard. REAL: the actual keyboard velocity is transmitted. 1–127: a fixed velocity is transmitted regardless of how you play.
  - model: `fm.system.controller.keyboardVelocity` @ 02 00 40 02, raw [0, 127]
- **HOLD PEDAL POLARITY** (STANDARD, REVERSE) *[EM p.13]*: Polarity of the hold pedal. Some pedals output the opposite electrical signal when pressed/released; if your pedal works the wrong way round set REVERSE. For a Roland pedal (no polarity switch) set STANDARD.
  - model: `fm.system.controller.holdPedalPolarity` @ 02 00 40 05, raw [0, 1]
- **D BEAM ASSIGN** (CC01–CC31, CC33–CC95) *[EM p.13]*: Function (controller number) sent by the D Beam controller when its [ASSIGNABLE] button is active.
  - [F] Stored index has no CC32 slot: raw 0 = CC01, raw 30 = CC31, raw 31 = CC33, raw 68 = CC70.
  - [D OM p.24] Settable on the panel: [SHIFT]+[ASSIGNABLE], 'C01'…'C95'.
  - model: `fm.system.controller.beamAssign` @ 02 00 40 0A, raw [0, 93]
- **D BEAM RANGE MIN** (0–127) *[EM p.13]*: Lower limit of the D Beam controller's range. By setting D BEAM RANGE MAX below MIN you can invert the range of change.
  - model: `fm.system.controller.beamRangeLower` @ 02 00 40 0B, raw [0, 127]
- **D BEAM RANGE MAX** (0–127) *[EM p.13]*: Upper limit of the D Beam controller's range. Setting MAX below MIN inverts the range of change.
  - model: `fm.system.controller.beamRangeUpper` @ 02 00 40 0C, raw [0, 127]
- **OCTAVE/VARIATION BUTTONS ASSIGN** (OCTAVE SWITCH, OCTAVE HOLD, VARIATION) *[EM p.13]*: Function of the OCTAVE/VARIATION buttons on the neck. OCTAVE SWITCH: each press shifts the range by one octave (within ±3 octaves). OCTAVE HOLD: the range is raised/lowered by one octave only while the button is held. VARIATION: select the patch.
  - [D OM p.18, 22] Panel display codes: OCS, OCH, Var.
  - model: `fm.system.controller.neckSwitchSelect` @ 02 00 40 4E, raw [0, 2]
- **Portament Mode (SuperNATURAL portamento: Hld / SUt)** (SWITCH, HOLD) *[OM p.24]*: Portamento button behaviour for SuperNATURAL tones only. Hld: portamento applies while the [PORTAMENTO] button is held. SUt: the button toggles portamento on/off. Ignored by regular tones.
  - [D MI] SystemController offset 00 4F. [F] Not in the Editor's Script.xml (its SystemController size is 4F), so no schema path; the Owner's Manual shows the setting exists on the hardware.

### SETUP (current selection and switches)
*group `setup` · MI p.7*

Setup block at 01 00 00 00. Not described in the Editor manual; descriptions from the MIDI Implementation. Many other Setup bytes are reserved and ignored on reception.

- **Patch Bank Select MSB (CC#0)** (0–127 (66: SuperNATURAL, 87: Regular/Special Patch)) *[MI p.7]*: Bank Select MSB of the currently selected patch.
  - [F] Real .a8e files store the bank/program that was selected when the file was saved (e.g. 87/0/96 = factory 'SearingGtr 1').
  - model: `fm.setup.kbdPatchBankSelectMsb` @ 01 00 00 04, raw [0, 127]
- **Patch Bank Select LSB (CC#32)** (0–127 (0: SuperNATURAL, 0–1: Regular Patch, 64: Special Patch)) *[MI p.7]*: Bank Select LSB of the currently selected patch.
  - model: `fm.setup.kbdPatchBankSelectLsb` @ 01 00 00 05, raw [0, 127]
- **Patch Program Number (PC)** (0–127) *[MI p.7]*: Program number (0-based) of the currently selected patch.
  - model: `fm.setup.kbdPatchProgramNumber` @ 01 00 00 06, raw [0, 127]
- **MFX1 Switch** (BYPASS, ON) *[MI p.7]*: Multi-effect on/bypass (the Editor's MFX ON/OFF switch; EM p.16: the effect on/off settings cannot be saved in the patch).
  - model: `fm.setup.mfx1Switch` @ 01 00 00 0A, raw [0, 1]
- **Chorus Switch** (OFF, ON) *[MI p.7]*: Chorus on/off (not saved in the patch; EM p.17).
  - model: `fm.setup.chorusSwitch` @ 01 00 00 0D, raw [0, 1]
- **Reverb Switch** (OFF, ON) *[MI p.7]*: Reverb on/off (not saved in the patch; EM p.17).
  - model: `fm.setup.reverbSwitch` @ 01 00 00 0E, raw [0, 1]
- **Transpose Value** (-5–+6 (stored 59–70)) *[MI p.7]*: Keyboard transposition in semitones (panel TRANSPOSE function).
  - [D OM p.21] Set with [TRANSPOSE] + OCTAVE/VARIATION [+]/[–].
  - model: `fm.setup.transposeValue` @ 01 00 00 12, raw [59, 70]
- **Octave Shift** (-3–+3 (stored 61–67)) *[MI p.7]*: Keyboard octave shift (panel OCTAVE function).
  - model: `fm.setup.octaveShift` @ 01 00 00 13, raw [61, 67]

## MFX types

`#` = usable as Multi-Effect Control / Matrix Control destination (EM p.44). Stored values are raw+32768.

### 01 EQUALIZER
*FILTER · EM p.46*

A four-band stereo equalizer (low, mid x 2, high).

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Low Freq | 200, 400 Hz |  | Frequency of the low range. | `equalizer-loFreq` |
| Low Gain | -15–+15 dB | # | Gain of the low range. | `equalizer-loGain` |
| Mid1 Freq | 200–8000 Hz |  | Frequency of the middle range 1. | `equalizer-mid1Freq` |
| Mid1 Gain | -15–+15 dB |  | Gain of the middle range 1. | `equalizer-mid1Gain` |
| Mid1 Q | 0.5, 1.0, 2.0, 4.0, 8.0 |  | Width of the middle range 1. A higher Q narrows the range affected. | `equalizer-mid1Q` |
| Mid2 Freq | 200–8000 Hz |  | Frequency of the middle range 2. | `equalizer-mid2Freq` |
| Mid2 Gain | -15–+15 dB |  | Gain of the middle range 2. | `equalizer-mid2Gain` |
| Mid2 Q | 0.5, 1.0, 2.0, 4.0, 8.0 |  | Width of the middle range 2. A higher Q narrows the range affected. | `equalizer-mid2Q` |
| High Freq | 2000, 4000, 8000 Hz |  | Frequency of the high range. | `equalizer-hiFreq` |
| High Gain | -15–+15 dB | # | Gain of the high range. | `equalizer-hiGain` |
| Level | 0–127 | # | Output level. | `equalizer-level` |

### 02 SPECTRUM
*FILTER · EM p.46*

A stereo spectrum: a type of filter that modifies the timbre by boosting or cutting the level at specific frequencies.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Band1 (250 Hz) … Band8 (8000 Hz) | -15–+15 dB each; bands 250, 500, 1000, 1250, 2000, 3150, 4000, 8000 Hz |  | Gain of each frequency band. | `spectrum-band1`, `spectrum-band2`, `spectrum-band3`, `spectrum-band4`, `spectrum-band5`, `spectrum-band6`, `spectrum-band7`, `spectrum-band8` |
| Q | 0.5, 1.0, 2.0, 4.0, 8.0 |  | Simultaneously adjusts the width of the adjusted ranges for all frequency bands. | `spectrum-width` |
| Level | 0–127 | # | Output level. | `spectrum-level` |

### 03 ISOLATOR
*FILTER · EM p.46*

An equalizer that cuts the volume greatly, allowing you to add a special effect to the sound by cutting the volume in varying ranges.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Boost/Cut Low / Mid / High | -60–+4 dB | # | Boost and cut each of the Low, Middle and High frequency ranges. At -60 dB the range becomes inaudible; 0 dB equals the input level. | `isolator-loLevel`, `isolator-midLevel`, `isolator-hiLevel` |
| Anti Phase Low Sw | OFF, ON |  | Turns the Anti-Phase function on/off for the Low range. When on, the counter-channel of the stereo sound is inverted and added to the signal. | `isolator-loApSw` |
| Anti Phase Low Level | 0–127 |  | Level of the Anti-Phase function for the Low range. Adjusting it for certain frequencies lends emphasis to specific parts (effective only for a stereo source). | `isolator-loAp` |
| Anti Phase Mid Sw | OFF, ON |  | Anti-Phase on/off for the Middle range (same as for Low). | `isolator-midApSw` |
| Anti Phase Mid Level | 0–127 |  | Anti-Phase level for the Middle range (same as for Low). | `isolator-midAp` |
| Low Boost Sw | OFF, ON |  | Turns the Low Booster on/off; emphasizes the bottom to create a heavy bass sound. | `isolator-boostSw` |
| Low Boost Level | 0–127 |  | Increasing this value gives a heavier low end. Depending on the Isolator and filter settings this effect may be hard to distinguish. | `isolator-boostLevel` |
| Level | 0–127 |  | Output level. | `isolator-level` |

### 04 LOW BOOST
*FILTER · EM p.47*

Boosts the volume of the lower range, creating powerful lows.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Boost Frequency | 50–125 Hz | # | Center frequency at which the lower range will be boosted. | `lowBoost-freq` |
| Boost Gain | 0–+12 dB | # | Amount by which the lower range will be boosted. | `lowBoost-gain` |
| Boost Width | WIDE, MID, NARROW |  | Width of the lower range that will be boosted. | `lowBoost-width` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high frequency range (2-band EQ). | `lowBoost-eqLo`, `lowBoost-eqHi` |
| Level | 0–127 |  | Output level. | `lowBoost-level` |

### 05 SUPER FILTER
*FILTER · EM p.47*

A filter with an extremely sharp slope. The cutoff frequency can be varied cyclically.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Filter Type | LPF, BPF, HPF, NOTCH |  | Frequency range that passes: LPF below the cutoff; BPF around the cutoff; HPF above the cutoff; NOTCH everything except the region around the cutoff. | `superFilter-filtType` |
| Filter Slope | -12, -24, -36 dB |  | Attenuation per octave: -12 dB gentle, -24 dB steep, -36 dB extremely steep. | `superFilter-filtSlope` |
| Filter Cutoff | 0–127 | # | Cutoff frequency; higher = higher cutoff. | `superFilter-filtCutoff` |
| Filter Resonance | 0–127 | # | Filter resonance; higher emphasizes the region near the cutoff. | `superFilter-filtReso` |
| Filter Gain | 0–+12 dB |  | Amount of boost for the filter output. | `superFilter-filtGain` |
| Modulation Sw | OFF, ON |  | On/off switch for cyclic change of the cutoff. | `superFilter-modSw` |
| Modulation Wave | TRI, SQR, SIN, SAW1, SAW2 |  | How the cutoff is modulated: triangle, square, sine, sawtooth upward (SAW1), sawtooth downward (SAW2). | `superFilter-modWave` |
| Rate | 0.05–10.00 Hz | # | Rate of modulation. | `superFilter-rateHz` |
| Depth | 0–127 |  | Depth of modulation. | `superFilter-depth` |
| Attack | 0–127 | # | Speed at which the cutoff changes; effective if Modulation Wave is SQR, SAW1 or SAW2. | `superFilter-attack` |
| Level | 0–127 |  | Output level. | `superFilter-level` |

Schema-only members (in the data model, not described in the manual): `superFilter-rateSync`, `superFilter-rateNote`

### 06 STEP FILTER
*FILTER · EM p.47*

A filter whose cutoff frequency can be modulated in steps; you specify the pattern by which the cutoff changes (16-step sequencer; STEP RESET available).

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Step 01–16 | 0–127 |  | Cutoff frequency at each step. | `stepFilter-step01`, `stepFilter-step02`, `stepFilter-step03`, `stepFilter-step04`, `stepFilter-step05`, `stepFilter-step06`, `stepFilter-step07`, `stepFilter-step08`, `stepFilter-step09`, `stepFilter-step10`, `stepFilter-step11`, `stepFilter-step12`, `stepFilter-step13`, `stepFilter-step14`, `stepFilter-step15`, `stepFilter-step16` |
| Rate | 0.05–10.00 Hz | # | Rate of modulation (sequence speed). | `stepFilter-rateHz` |
| Attack | 0–127 | # | Speed at which the cutoff changes between steps. | `stepFilter-attack` |
| Filter Type | LPF, BPF, HPF, NOTCH |  | LPF passes below the cutoff; BPF around it; HPF above it; NOTCH everything except the region around it. | `stepFilter-filtType` |
| Filter Slope | -12, -24, -36 dB |  | Attenuation per octave: gentle, steep, extremely steep. | `stepFilter-filtSlope` |
| Filter Resonance | 0–127 | # | Filter resonance; higher emphasizes the region near the cutoff. | `stepFilter-filtReso` |
| Filter Gain | 0–+12 dB |  | Amount of boost for the filter output. | `stepFilter-filtGain` |
| Level | 0–127 |  | Output level. | `stepFilter-level` |

Schema-only members (in the data model, not described in the manual): `stepFilter-rateSync`, `stepFilter-rateNote`

### 07 ENHANCER
*FILTER · EM p.48*

Controls the overtone structure of the high frequencies, adding sparkle and tightness to the sound.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Sens | 0–127 | # | Sensitivity of the enhancer. | `enhancer-sens` |
| Mix | 0–127 | # | Level of the overtones generated by the enhancer. | `enhancer-mix` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `enhancer-eqLo`, `enhancer-eqHi` |
| Level | 0–127 |  | Output level. | `enhancer-level` |

### 08 AUTO WAH
*FILTER · EM p.48*

Cyclically controls a filter to create cyclic change in timbre.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Filter Type | LPF, BPF |  | LPF: the wah effect is applied over a wide frequency range. BPF: over a narrow range. | `autoWah-mode` |
| Manual | 0–127 | # | Center frequency at which the effect is applied. | `autoWah-manual` |
| Peak | 0–127 |  | Amount of wah effect around the center frequency; a higher value narrows the affected range (like Q). | `autoWah-peak` |
| Sens | 0–127 | # | Sensitivity with which the filter is controlled. | `autoWah-sens` |
| Polarity | UP, DOWN |  | Direction the frequency changes when the filter is modulated: UP toward higher, DOWN toward lower. | `autoWah-polarity` |
| Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `autoWah-rateHz` |
| Depth | 0–127 | # | Depth of modulation. | `autoWah-depth` |
| Phase | 0–180 deg | # | Phase shift between the left and right sounds while the wah is applied. | `autoWah-phs` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `autoWah-eqLo`, `autoWah-eqHi` |
| Level | 0–127 |  | Output level. | `autoWah-level` |

Schema-only members (in the data model, not described in the manual): `autoWah-rateSync`, `autoWah-rateNote`

### 09 HUMANIZER
*FILTER · EM p.48*

Adds a vowel character to the sound, making it similar to a human voice (overdrive -> formant filter -> 2-band EQ -> pan).

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Drive Sw | OFF, ON |  | Turns Drive on/off. | `humanizer-driveSw` |
| Drive | 0–127 | # | Degree of distortion; also changes the volume. | `humanizer-drv` |
| Vowel1 / Vowel2 | a, e, i, o, u |  | The two vowels the effect switches between. | `humanizer-vowel1`, `humanizer-vowel2` |
| Rate | 0.05–10.00 Hz | # | Frequency at which the two vowels switch. | `humanizer-rateHz` |
| Depth | 0–127 | # | Effect depth. | `humanizer-depth` |
| Input Sync Sw | OFF, ON |  | Whether the LFO switching the vowels is reset by the input signal (ON) or not (OFF). | `humanizer-ksSw` |
| Input Sync Threshold | 0–127 |  | Volume level at which the reset is applied. | `humanizer-ksThre` |
| Manual | 0–100 | # | Point at which Vowel 1/2 switch: 49 or less = Vowel 1 lasts longer; 50 = equal; 51 or more = Vowel 2 lasts longer. | `humanizer-manual` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high frequency range. | `humanizer-eqLo`, `humanizer-eqHi` |
| Pan | L64–63R | # | Stereo location of the output. | `humanizer-pan` |
| Level | 0–127 |  | Output level. | `humanizer-level` |

Schema-only members (in the data model, not described in the manual): `humanizer-rateSync`, `humanizer-rateNote`

### 10 SPEAKER SIMULATOR
*FILTER · EM p.49*

Simulates the speaker type and the mic settings used to record the speaker sound.

> Speaker types (cabinet / speaker inches x units / mic): SMALL 1 small open-back 10 dynamic; SMALL 2 small open-back 10 dynamic; MIDDLE open back 12x1 dynamic; JC-120 open back 12x2 dynamic; BUILT-IN 1 open back 12x2 dynamic; BUILT-IN 2–5 open back 12x2 condenser; BG STACK 1 sealed 12x2 condenser; BG STACK 2 large sealed 12x2 condenser; MS STACK 1 and 2 large sealed 12x4 condenser; METAL STACK large double stack 12x4 condenser; 2-STACK large double stack 12x4 condenser; 3-STACK large triple stack 12x4 condenser.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Speaker Type | SMALL 1, SMALL 2, MIDDLE, JC-120, BUILT-IN 1–5, BG STACK 1–2, MS STACK 1–2, METAL STACK, 2-STACK, 3-STACK |  | Type of speaker (see notes for cabinet/speaker/mic of each). | `speakerSimulator-spType` |
| Mic Setting | 1, 2, 3 |  | Location of the mic recording the speaker; it becomes more distant in the order 1, 2, 3. | `speakerSimulator-micSetting` |
| Mic Level | 0–127 | # | Volume of the microphone. | `speakerSimulator-micLevel` |
| Direct Level | 0–127 | # | Volume of the direct sound. | `speakerSimulator-directLevel` |
| Level | 0–127 | # | Output level. | `speakerSimulator-level` |

### 11 PHASER
*MODULATION · EM p.49*

A phase-shifted sound is added to the original sound and modulated.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Mode | 4-STAGE, 8-STAGE, 12-STAGE |  | Number of stages in the phaser. | `phaser-mode` |
| Manual | 0–127 | # | Basic frequency from which the sound is modulated. | `phaser-manual` |
| Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `phaser-rateHz` |
| Depth | 0–127 |  | Depth of modulation. | `phaser-depth` |
| Polarity | INVERSE, SYNCHRO |  | INVERSE: left and right modulation phase opposite; spreads a mono source. SYNCHRO: same phase; select for a stereo source. | `phaser-polarity` |
| Resonance | 0–127 | # | Amount of feedback. | `phaser-reso` |
| Cross Feedback | -98–+98% |  | Proportion of the phaser sound fed back into the effect; negative settings invert the phase. | `phaser-xfbk` |
| Mix | 0–127 | # | Level of the phase-shifted sound. | `phaser-mix` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `phaser-eqLo`, `phaser-eqHi` |
| Level | 0–127 |  | Output level. | `phaser-level` |

Schema-only members (in the data model, not described in the manual): `phaser-rateSync`, `phaser-rateNote`

### 12 STEP PHASER
*MODULATION · EM p.50*

The phaser effect is varied in steps (stepwise change of the phaser effect at Step Rate).

> The manual's one-line description reads 'The phaser effect will be varied gradually.'

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Mode | 4-STAGE, 8-STAGE, 12-STAGE |  | Number of stages in the phaser. | `stepPhaser-mode` |
| Manual | 0–127 | # | Basic frequency from which the sound is modulated. | `stepPhaser-manual` |
| Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `stepPhaser-rateHz` |
| Depth | 0–127 |  | Depth of modulation. | `stepPhaser-depth` |
| Polarity | INVERSE, SYNCHRO |  | INVERSE: left/right phase opposite (spreads a mono source). SYNCHRO: same phase (for a stereo source). | `stepPhaser-polarity` |
| Resonance | 0–127 | # | Amount of feedback. | `stepPhaser-reso` |
| Cross Feedback | -98–+98% |  | Proportion of the phaser sound fed back into the effect; negative inverts the phase. | `stepPhaser-xfbk` |
| Step Rate | 0.10–20.00 Hz | # | Rate of the step-wise change in the phaser effect. | `stepPhaser-sRateHz` |
| Mix | 0–127 | # | Level of the phase-shifted sound. | `stepPhaser-mix` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `stepPhaser-eqLo`, `stepPhaser-eqHi` |
| Level | 0–127 |  | Output level. | `stepPhaser-level` |

Schema-only members (in the data model, not described in the manual): `stepPhaser-rateSync`, `stepPhaser-rateNote`, `stepPhaser-sRateSync`, `stepPhaser-sRateNote`

### 13 MULTI STAGE PHASER
*MODULATION · EM p.50*

Extremely high settings of the phase difference produce a deep phaser effect.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Mode | 4-STAGE, 8-STAGE, 12-STAGE, 16-STAGE, 20-STAGE, 24-STAGE |  | Number of phaser stages. | `multiStagePhaser-mode` |
| Manual | 0–127 | # | Basic frequency from which the sound is modulated. | `multiStagePhaser-manual` |
| Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `multiStagePhaser-rateHz` |
| Depth | 0–127 |  | Depth of modulation. | `multiStagePhaser-depth` |
| Resonance | 0–127 | # | Amount of feedback. | `multiStagePhaser-reso` |
| Mix | 0–127 | # | Level of the phase-shifted sound. | `multiStagePhaser-mix` |
| Pan | L64–63R | # | Stereo location of the output sound. | `multiStagePhaser-pan` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `multiStagePhaser-eqLo`, `multiStagePhaser-eqHi` |
| Level | 0–127 |  | Output level. | `multiStagePhaser-level` |

Schema-only members (in the data model, not described in the manual): `multiStagePhaser-rateSync`, `multiStagePhaser-rateNote`

### 14 INFINITE PHASER
*MODULATION · EM p.50*

A phaser that keeps raising/lowering the frequency at which the sound is modulated.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Mode | 1, 2, 3, 4 |  | Higher values produce a deeper phaser effect. | `infinitePhaser-mode` |
| Speed | -100–+100 | # | Speed at which the modulated frequency is raised (+) or lowered (-). | `infinitePhaser-speed` |
| Resonance | 0–127 | # | Amount of feedback. | `infinitePhaser-reso` |
| Mix | 0–127 | # | Level of the phase-shifted sound. | `infinitePhaser-mix` |
| Pan | L64–63R | # | Panning of the output sound. | `infinitePhaser-pan` |
| Low Gain / High Gain | -15–+15 dB |  | Boost/cut for the low / high frequency range. | `infinitePhaser-eqLo`, `infinitePhaser-eqHi` |
| Level | 0–127 |  | Output volume. | `infinitePhaser-level` |

### 15 RING MODULATOR
*MODULATION · EM p.51*

Applies amplitude modulation (AM) to the input signal, producing bell-like sounds. The modulation frequency can also change in response to the volume of the sound sent into the effect.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Frequency | 0–127 | # | Frequency at which modulation is applied. | `ringModulator-freq` |
| Sens | 0–127 | # | Amount of frequency modulation applied (response to input volume). | `ringModulator-sens` |
| Polarity | UP, DOWN |  | Whether the frequency modulation moves toward higher (UP) or lower (DOWN) frequencies. | `ringModulator-polarity` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high frequency range. | `ringModulator-eqLo`, `ringModulator-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the effect sound (W). | `ringModulator-bal` |
| Level | 0–127 |  | Output level. | `ringModulator-level` |

### 16 STEP RING MODULATOR
*MODULATION · EM p.51*

A ring modulator that uses a 16-step sequence to vary the modulation frequency (STEP RESET available).

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Step 01–16 | 0–127 |  | Frequency of ring modulation at each step. | `stepRingModulator-step01`, `stepRingModulator-step02`, `stepRingModulator-step03`, `stepRingModulator-step04`, `stepRingModulator-step05`, `stepRingModulator-step06`, `stepRingModulator-step07`, `stepRingModulator-step08`, `stepRingModulator-step09`, `stepRingModulator-step10`, `stepRingModulator-step11`, `stepRingModulator-step12`, `stepRingModulator-step13`, `stepRingModulator-step14`, `stepRingModulator-step15`, `stepRingModulator-step16` |
| Rate | 0.05–10.00 Hz | # | Rate at which the 16-step sequence cycles. | `stepRingModulator-rateHz` |
| Attack | 0–127 | # | Speed at which the modulation frequency changes between steps. | `stepRingModulator-attack` |
| Low Gain / High Gain | -15–+15 dB |  | Boost/cut for the low / high frequency range. | `stepRingModulator-eqLo`, `stepRingModulator-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance of the original sound (D) and effect sound (W). | `stepRingModulator-bal` |
| Level | 0–127 |  | Output volume. | `stepRingModulator-level` |

Schema-only members (in the data model, not described in the manual): `stepRingModulator-rateSync`, `stepRingModulator-rateNote`

### 17 TREMOLO
*MODULATION · EM p.51*

Cyclically modulates the volume to add tremolo to the sound.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Mod Wave | TRI, SQR, SIN, SAW1, SAW2 |  | Modulation wave: triangle, square, sine, sawtooth (SAW1/SAW2 = rising/falling). | `tremolo-modWave` |
| Rate | 0.05–10.00 Hz | # | Frequency of the change. | `tremolo-rateHz` |
| Depth | 0–127 | # | Depth to which the effect is applied. | `tremolo-depth` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `tremolo-eqLo`, `tremolo-eqHi` |
| Level | 0–127 |  | Output level. | `tremolo-level` |

Schema-only members (in the data model, not described in the manual): `tremolo-rateSync`, `tremolo-rateNote`

### 18 AUTO PAN
*MODULATION · EM p.52*

Cyclically modulates the stereo location of the sound.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Mod Wave | TRI, SQR, SIN, SAW1, SAW2 |  | Modulation wave: triangle, square, sine, sawtooth (SAW1/SAW2). | `autoPan-modWave` |
| Rate | 0.05–10.00 Hz | # | Frequency of the change. | `autoPan-rateHz` |
| Depth | 0–127 | # | Depth to which the effect is applied. | `autoPan-depth` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `autoPan-eqLo`, `autoPan-eqHi` |
| Level | 0–127 |  | Output level. | `autoPan-level` |

Schema-only members (in the data model, not described in the manual): `autoPan-rateSync`, `autoPan-rateNote`

### 19 STEP PAN
*MODULATION · EM p.52*

Uses a 16-step sequence to vary the panning of the sound (STEP RESET available).

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Step 01–16 | L64–63R |  | Pan at each step. | `stepPan-step01`, `stepPan-step02`, `stepPan-step03`, `stepPan-step04`, `stepPan-step05`, `stepPan-step06`, `stepPan-step07`, `stepPan-step08`, `stepPan-step09`, `stepPan-step10`, `stepPan-step11`, `stepPan-step12`, `stepPan-step13`, `stepPan-step14`, `stepPan-step15`, `stepPan-step16` |
| Rate | 0.05–10.00 Hz | # | Rate at which the 16-step sequence cycles. | `stepPan-rateHz` |
| Attack | 0–127 | # | Speed at which the pan changes between steps. | `stepPan-attack` |
| Input Sync Sw | OFF, ON |  | Whether an input note makes the sequence resume from its first step. | `stepPan-resetSw` |
| Input Sync Threshold | 0–127 |  | Volume at which an input note is detected. | `stepPan-resetThre` |
| Level | 0–127 |  | Output volume. | `stepPan-level` |

Schema-only members (in the data model, not described in the manual): `stepPan-rateSync`, `stepPan-rateNote`

### 20 SLICER
*MODULATION · EM p.52*

Applies successive cuts to the sound, turning a conventional sound into one that appears to be played as a backing phrase; especially effective on sustain-type sounds (16-step sequence; STEP RESET available).

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Step 01–16 | 0–127 |  | Level at each step. | `slicer-step01`, `slicer-step02`, `slicer-step03`, `slicer-step04`, `slicer-step05`, `slicer-step06`, `slicer-step07`, `slicer-step08`, `slicer-step09`, `slicer-step10`, `slicer-step11`, `slicer-step12`, `slicer-step13`, `slicer-step14`, `slicer-step15`, `slicer-step16` |
| Rate | 0.05–10.00 Hz | # | Rate at which the 16-step sequence cycles. | `slicer-rateHz` |
| Attack | 0–127 | # | Speed at which the level changes between steps. | `slicer-attack` |
| Input Sync Sw | OFF, ON |  | Whether an input note makes the sequence resume from its first step. | `slicer-resetSw` |
| Input Sync Threshold | 0–127 |  | Volume at which an input note is detected. | `slicer-resetThre` |
| Mode | LEGATO, SLASH |  | How the volume changes from step to step. LEGATO: unaltered; equal consecutive levels give no change. SLASH: the level is momentarily set to 0 before the next step, even if the next level is the same. | `slicer-mode` |
| Shuffle | 0–127 | # | Timing of the level changes on even-numbered steps (2, 4, 6, …); higher = later (swing). | `slicer-shuffle` |
| Level | 0–127 |  | Output level. | `slicer-level` |

Schema-only members (in the data model, not described in the manual): `slicer-rateSync`, `slicer-rateNote`

### 21 ROTARY
*MODULATION · EM p.53*

Simulates the rotary speakers often used with electric organs. The high-range and low-range rotors can be set independently, closely simulating the characteristic modulation. Most suitable for electric organ patches.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Speed | SLOW, FAST | # | Switches the rotation speed of both rotors simultaneously to their Slow / Fast rates. | `rotary-speed` |
| Woofer Slow Speed / Woofer Fast Speed | 0.05–10.00 Hz |  | Slow and fast rotation speeds of the low-frequency rotor. | `rotary-wfSlowSpeed`, `rotary-wfFastSpeed` |
| Woofer Acceleration | 0–15 |  | Time the low-frequency rotor takes to reach the new speed when switching; lower values = longer times. | `rotary-wfAccel` |
| Woofer Level | 0–127 |  | Volume of the low-frequency rotor. | `rotary-wfLevel` |
| Tweeter Slow Speed / Fast Speed / Acceleration / Level | 0.05–10.00 Hz / 0.05–10.00 Hz / 0–15 / 0–127 |  | Same settings for the high-frequency rotor. | `rotary-twSlowSpeed`, `rotary-twFastSpeed`, `rotary-twAccel`, `rotary-twLevel` |
| Separation | 0–127 |  | Spatial dispersion of the sound. | `rotary-sepa` |
| Level | 0–127 | # | Output level. | `rotary-level` |

### 22 VK ROTARY
*MODULATION · EM p.53*

Rotary speaker with modified response and the low end boosted further; same specifications as the VK-7's built-in rotary speaker.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Speed | SLOW, FAST | # | Rotational speed of the rotating speaker. | `vkRotary-speed` |
| Brake | OFF, ON | # | ON: the rotation gradually stops. OFF: the rotation gradually resumes. | `vkRotary-brake` |
| Woofer Slow Speed / Woofer Fast Speed | 0.05–10.00 Hz |  | Low-speed and high-speed rotation of the woofer. | `vkRotary-wfSlowSpeed`, `vkRotary-wfFastSpeed` |
| Woofer Trans Up | 0–127 |  | Rate at which the woofer rotation speeds up when switched from Slow to Fast. | `vkRotary-wfTransUp` |
| Woofer Trans Down | 0–127 |  | Rate at which the woofer rotation changes when switched from Fast to Slow. | `vkRotary-wfTransDw` |
| Woofer Level | 0–127 |  | Volume of the woofer. | `vkRotary-wfLevel` |
| Tweeter Slow Speed / Fast Speed / Trans Up / Trans Down / Level | 0.05–10.00 Hz / 0.05–10.00 Hz / 0–127 / 0–127 / 0–127 |  | Same settings for the tweeter. | `vkRotary-twSlowSpeed`, `vkRotary-twFastSpeed`, `vkRotary-twTransUp`, `vkRotary-twTransDw`, `vkRotary-twLevel` |
| Spread | 0–10 |  | Stereo image of the rotary speaker; higher = wider. | `vkRotary-spread` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `vkRotary-eqLo`, `vkRotary-eqHi` |
| Level | 0–127 | # | Output level. | `vkRotary-level` |
| Type | STANDARD, STACK, CLEAN |  | Type of rotary speaker. | `vkRotary-type` |

### 23 CHORUS
*CHORUS · EM p.54*

A stereo chorus, with a filter to adjust the timbre of the chorus sound.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Filter Type | OFF, LPF, HPF |  | OFF: no filter. LPF: cuts above the Cutoff Freq. HPF: cuts below the Cutoff Freq. | `chorus-filt` |
| Cutoff Freq | 200–8000 Hz |  | Center frequency of the filter. | `chorus-splt` |
| Pre Delay | 0.0–100 msec |  | Delay from the direct sound until the chorus sound is heard. | `chorus-dly` |
| Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `chorus-rateHz` |
| Depth | 0–127 |  | Depth of modulation. | `chorus-depth` |
| Phase | 0–180 deg |  | Spatial spread of the sound. | `chorus-phs` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `chorus-eqLo`, `chorus-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the chorus sound (W). | `chorus-bal` |
| Level | 0–127 |  | Output level. | `chorus-level` |

Schema-only members (in the data model, not described in the manual): `chorus-rateSync`, `chorus-rateNote`

### 24 FLANGER
*CHORUS · EM p.54*

A stereo flanger (LFO in phase for left and right). Produces a metallic resonance that rises and falls like a jet airplane taking off or landing; a filter adjusts the timbre of the flanged sound.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Filter Type | OFF, LPF, HPF |  | OFF: no filter. LPF: cuts above the Cutoff Freq. HPF: cuts below it. | `flanger-filt` |
| Cutoff Freq | 200–8000 Hz |  | Center frequency of the filter. | `flanger-splt` |
| Pre Delay | 0.0–100 msec |  | Delay from when the direct sound begins until the flanger sound is heard. | `flanger-dly` |
| Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `flanger-rateHz` |
| Depth | 0–127 |  | Depth of modulation. | `flanger-depth` |
| Phase | 0–180 deg |  | Spatial spread of the sound. | `flanger-phs` |
| Feedback | -98–+98% | # | Proportion of the flanger sound fed back into the effect; negative inverts the phase. | `flanger-fbk` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `flanger-eqLo`, `flanger-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the flanger sound (W). | `flanger-bal` |
| Level | 0–127 |  | Output level. | `flanger-level` |

Schema-only members (in the data model, not described in the manual): `flanger-rateSync`, `flanger-rateNote`

### 25 STEP FLANGER
*CHORUS · EM p.55*

A flanger whose pitch changes in steps. The speed of the pitch change can also be specified as a note value of a specified tempo.

> [F] The tempo/note-value option corresponds to the schema members sRateSync/sRateNote (not further documented).

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Filter Type | OFF, LPF, HPF |  | OFF: no filter. LPF: cuts above the Cutoff Freq. HPF: cuts below it. | `stepFlanger-filt` |
| Cutoff Freq | 200–8000 Hz |  | Center frequency of the filter. | `stepFlanger-splt` |
| Pre Delay | 0.0–100 msec |  | Delay from when the direct sound begins until the flanger sound is heard. | `stepFlanger-dly` |
| Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `stepFlanger-rateHz` |
| Depth | 0–127 |  | Depth of modulation. | `stepFlanger-depth` |
| Phase | 0–180 deg |  | Spatial spread of the sound. | `stepFlanger-phs` |
| Feedback | -98–+98% | # | Proportion of the flanger sound fed back into the effect; negative inverts the phase. | `stepFlanger-fbk` |
| Step Rate | 0.10–20.00 Hz | # | Rate (period) of the pitch change. | `stepFlanger-sRateHz` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `stepFlanger-eqLo`, `stepFlanger-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the flanger sound (W). | `stepFlanger-bal` |
| Level | 0–127 |  | Output level. | `stepFlanger-level` |

Schema-only members (in the data model, not described in the manual): `stepFlanger-rateSync`, `stepFlanger-rateNote`, `stepFlanger-sRateSync`, `stepFlanger-sRateNote`

### 26 HEXA-CHORUS
*CHORUS · EM p.55*

A six-phase chorus (six layers of chorused sound) giving richness and spatial spread.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Pre Delay | 0.0–100 msec |  | Delay from the direct sound until the chorus sound is heard. | `hexaChorus-dly` |
| Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `hexaChorus-rateHz` |
| Depth | 0–127 |  | Depth of modulation. | `hexaChorus-depth` |
| Pre Delay Deviation | 0–20 |  | Differences in Pre Delay between the chorus sounds. | `hexaChorus-dlyDev` |
| Depth Deviation | -20–+20 |  | Difference in modulation depth between the chorus sounds. | `hexaChorus-depthDev` |
| Pan Deviation | 0–20 |  | Difference in stereo location between the chorus sounds: 0 = all in the center; 20 = spaced at 60-degree intervals relative to the center. | `hexaChorus-panDev` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the chorus sound (W). | `hexaChorus-bal` |
| Level | 0–127 |  | Output level. | `hexaChorus-level` |

Schema-only members (in the data model, not described in the manual): `hexaChorus-rateSync`, `hexaChorus-rateNote`

### 27 TREMOLO CHORUS
*CHORUS · EM p.56*

A chorus with added tremolo (cyclic modulation of volume).

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Pre Delay | 0.0–100 msec |  | Delay from the direct sound until the chorus sound is heard. | `tremoloChorus-dly` |
| Chorus Rate | 0.05–10.00 Hz | # | Modulation frequency of the chorus. | `tremoloChorus-choRateHz` |
| Chorus Depth | 0–127 |  | Modulation depth of the chorus. | `tremoloChorus-choDepth` |
| Tremolo Rate | 0.05–10.00 Hz | # | Modulation frequency of the tremolo. | `tremoloChorus-treRateHz` |
| Tremolo Separation | 0–127 |  | Spread of the tremolo effect. | `tremoloChorus-treSepa` |
| Tremolo Phase | 0–180 deg |  | Spread of the tremolo effect (phase). | `tremoloChorus-trePhs` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the tremolo chorus sound (W). | `tremoloChorus-bal` |
| Level | 0–127 |  | Output level. | `tremoloChorus-level` |

Schema-only members (in the data model, not described in the manual): `tremoloChorus-choRateSync`, `tremoloChorus-choRateNote`, `tremoloChorus-treRateSync`, `tremoloChorus-treRateNote`

### 28 SPACE-D
*CHORUS · EM p.56*

A multiple chorus applying two-phase modulation in stereo. It gives no impression of modulation, but a transparent chorus effect.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Pre Delay | 0.0–100 msec |  | Delay from the direct sound until the chorus sound is heard. | `spaceD-dly` |
| Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `spaceD-rateHz` |
| Depth | 0–127 |  | Depth of modulation. | `spaceD-depth` |
| Phase | 0–180 deg |  | Spatial spread of the sound. | `spaceD-phs` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `spaceD-eqLo`, `spaceD-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the chorus sound (W). | `spaceD-bal` |
| Level | 0–127 |  | Output level. | `spaceD-level` |

Schema-only members (in the data model, not described in the manual): `spaceD-rateSync`, `spaceD-rateNote`

### 29 3D CHORUS
*CHORUS · EM p.56*

Applies a 3D (RSS) effect to the chorus sound: the chorus sound is positioned 90 degrees left and 90 degrees right.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Filter Type | OFF, LPF, HPF |  | OFF: no filter. LPF: cuts above the Cutoff Freq. HPF: cuts below it. | `3dChorus-filt` |
| Cutoff Freq | 200–8000 Hz |  | Center frequency of the filter. | `3dChorus-splt` |
| Pre Delay | 0.0–100 msec |  | Delay from the direct sound until the chorus sound is heard. | `3dChorus-dly` |
| Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `3dChorus-rateHz` |
| Depth | 0–127 |  | Modulation depth of the chorus. | `3dChorus-depth` |
| Phase | 0–180 deg |  | Spatial spread of the sound. | `3dChorus-phs` |
| Output Mode | SPEAKER, PHONES |  | How the output is heard: SPEAKER for speakers, PHONES for headphones (optimal 3D effect). | `3dChorus-out` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `3dChorus-eqLo`, `3dChorus-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the chorus sound (W). | `3dChorus-bal` |
| Level | 0–127 |  | Output level. | `3dChorus-level` |

Schema-only members (in the data model, not described in the manual): `3dChorus-rateSync`, `3dChorus-rateNote`

### 30 3D FLANGER
*CHORUS · EM p.57*

Applies a 3D effect to the flanger sound, positioned 90 degrees left and 90 degrees right.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Filter Type | OFF, LPF, HPF |  | OFF: no filter. LPF: cuts above the Cutoff Freq. HPF: cuts below it. | `3dFlanger-filt` |
| Cutoff Freq | 200–8000 Hz |  | Center frequency of the filter. | `3dFlanger-splt` |
| Pre Delay | 0.0–100 msec |  | Delay from when the direct sound begins until the flanger sound is heard. | `3dFlanger-dly` |
| Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `3dFlanger-rateHz` |
| Depth | 0–127 |  | Depth of modulation. | `3dFlanger-depth` |
| Phase | 0–180 deg |  | Spatial spread of the sound. | `3dFlanger-phs` |
| Feedback | -98–+98% | # | Proportion of the flanger sound fed back into the effect; negative inverts the phase. | `3dFlanger-fbk` |
| Output Mode | SPEAKER, PHONES |  | SPEAKER for speakers, PHONES for headphones (optimal 3D effect). | `3dFlanger-out` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `3dFlanger-eqLo`, `3dFlanger-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the flanger sound (W). | `3dFlanger-bal` |
| Level | 0–127 |  | Output level. | `3dFlanger-level` |

Schema-only members (in the data model, not described in the manual): `3dFlanger-rateSync`, `3dFlanger-rateNote`

### 31 3D STEP FLANGER
*CHORUS · EM p.57*

Applies a 3D effect to the step flanger sound, positioned 90 degrees left and 90 degrees right.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Filter Type | OFF, LPF, HPF |  | OFF: no filter. LPF: cuts above the Cutoff Freq. HPF: cuts below it. | `3dStepFlanger-filt` |
| Cutoff Freq | 200–8000 Hz |  | Center frequency of the filter. | `3dStepFlanger-splt` |
| Pre Delay | 0.0–100 msec |  | Delay from when the direct sound begins until the flanger sound is heard. | `3dStepFlanger-dly` |
| Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `3dStepFlanger-rateHz` |
| Depth | 0–127 |  | Depth of modulation. | `3dStepFlanger-depth` |
| Phase | 0–180 deg |  | Spatial spread of the sound. | `3dStepFlanger-phs` |
| Feedback | -98–+98% | # | Proportion of the flanger sound fed back into the effect; negative inverts the phase. | `3dStepFlanger-fbk` |
| Step Rate | 0.10–20.00 Hz | # | Rate (period) of the pitch change. | `3dStepFlanger-sRateHz` |
| Output Mode | SPEAKER, PHONES |  | SPEAKER for speakers, PHONES for headphones (optimal 3D effect). | `3dStepFlanger-out` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `3dStepFlanger-eqLo`, `3dStepFlanger-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the flanger sound (W). | `3dStepFlanger-bal` |
| Level | 0–127 |  | Output level. | `3dStepFlanger-level` |

Schema-only members (in the data model, not described in the manual): `3dStepFlanger-rateSync`, `3dStepFlanger-rateNote`, `3dStepFlanger-sRateSync`, `3dStepFlanger-sRateNote`

### 32 2 BAND CHORUS
*CHORUS · EM p.58*

A chorus that applies the effect independently to the low-frequency and high-frequency ranges.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Split Freq | 200–8000 Hz |  | Frequency at which the low and high ranges are divided. | `2bandChorus-splt` |
| Low Pre Delay | 0.0–100 msec |  | Delay from the original sound to the low-range chorus sound. | `2bandChorus-loDly` |
| Low Rate | 0.05–10.00 Hz | # | Rate at which the low-range chorus sound is modulated. | `2bandChorus-loRateHz` |
| Low Depth | 0–127 |  | Modulation depth of the low-range chorus sound. | `2bandChorus-loDepth` |
| Low Phase | 0–180 deg |  | Spaciousness of the low-range chorus sound. | `2bandChorus-loPhs` |
| High Pre Delay | 0.0–100 msec |  | Delay from the original sound to the high-range chorus sound. | `2bandChorus-hiDly` |
| High Rate | 0.05–10.00 Hz | # | Rate at which the high-range chorus sound is modulated. The manual's explanation text says 'low-range' here, evidently a typo. | `2bandChorus-hiRateHz` |
| High Depth | 0–127 |  | Modulation depth of the high-range chorus sound. | `2bandChorus-hiDepth` |
| High Phase | 0–180 deg |  | Spaciousness of the high-range chorus sound. | `2bandChorus-hiPhs` |
| Balance | D100:0W–D0:100W | # | Volume balance of the original sound (D) and the chorus sound (W). | `2bandChorus-bal` |
| Level | 0–127 |  | Output volume. | `2bandChorus-level` |

Schema-only members (in the data model, not described in the manual): `2bandChorus-loRateSync`, `2bandChorus-loRateNote`, `2bandChorus-hiRateSync`, `2bandChorus-hiRateNote`

### 33 2 BAND FLANGER
*CHORUS · EM p.58*

A flanger that applies the effect independently to the low-frequency and high-frequency ranges.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Split Freq | 200–8000 Hz |  | Frequency at which the low and high ranges are divided. | `2bandFlanger-splt` |
| Low Pre Delay / Low Rate / Low Depth / Low Phase | 0.0–100 msec / 0.05–10.00 Hz / 0–127 / 0–180 deg | #: loRateHz | Low-range flanger: delay from the original sound, modulation rate, modulation depth, spaciousness. | `2bandFlanger-loDly`, `2bandFlanger-loRateHz`, `2bandFlanger-loDepth`, `2bandFlanger-loPhs` |
| Low Feedback | -98–+98% | # | Proportion of the low-range flanger sound returned to the input (negative inverts the phase). | `2bandFlanger-loFbk` |
| High Pre Delay / High Rate / High Depth / High Phase | 0.0–100 msec / 0.05–10.00 Hz / 0–127 / 0–180 deg | #: hiRateHz | High-range flanger: delay, modulation rate, depth, spaciousness. | `2bandFlanger-hiDly`, `2bandFlanger-hiRateHz`, `2bandFlanger-hiDepth`, `2bandFlanger-hiPhs` |
| High Feedback | -98–+98% | # | Proportion of the high-range flanger sound returned to the input (negative inverts the phase). | `2bandFlanger-hiFbk` |
| Balance | D100:0W–D0:100W | # | Volume balance of the original sound (D) and the flanger sound (W). | `2bandFlanger-bal` |
| Level | 0–127 |  | Output volume. | `2bandFlanger-level` |

Schema-only members (in the data model, not described in the manual): `2bandFlanger-loRateSync`, `2bandFlanger-loRateNote`, `2bandFlanger-hiRateSync`, `2bandFlanger-hiRateNote`

### 34 2 BAND STEP FLANGER
*CHORUS · EM p.59*

A step flanger that applies the effect independently to the low-frequency and high-frequency ranges.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Split Freq | 200–8000 Hz |  | Frequency at which the low and high ranges are divided. | `2bandStepFlanger-splt` |
| Low Pre Delay / Low Rate / Low Depth / Low Phase | 0.0–100 msec / 0.05–10.00 Hz / 0–127 / 0–180 deg | #: loRateHz | Low-range flanger: delay, modulation rate, depth, spaciousness. | `2bandStepFlanger-loDly`, `2bandStepFlanger-loRateHz`, `2bandStepFlanger-loDepth`, `2bandStepFlanger-loPhs` |
| Low Feedback | -98–+98% | # | Proportion of the low-range flanger sound returned to the input. | `2bandStepFlanger-loFbk` |
| Low Step Rate | 0.10–20.00 Hz | # | Rate at which the steps cycle for the low-range flanger sound. | `2bandStepFlanger-loSRateHz` |
| High Pre Delay / High Rate / High Depth / High Phase | 0.0–100 msec / 0.05–10.00 Hz / 0–127 / 0–180 deg | #: hiRateHz | High-range flanger: delay, modulation rate, depth, spaciousness. | `2bandStepFlanger-hiDly`, `2bandStepFlanger-hiRateHz`, `2bandStepFlanger-hiDepth`, `2bandStepFlanger-hiPhs` |
| High Feedback | -98–+98% | # | Proportion of the high-range flanger sound returned to the input. | `2bandStepFlanger-hiFbk` |
| High Step Rate | 0.10–20.00 Hz | # | Rate at which the steps cycle for the high-range flanger sound. | `2bandStepFlanger-hiSRateHz` |
| Balance | D100:0W–D0:100W | # | Volume balance of the original sound (D) and the flanger sound (W). | `2bandStepFlanger-bal` |
| Level | 0–127 |  | Output volume. | `2bandStepFlanger-level` |

Schema-only members (in the data model, not described in the manual): `2bandStepFlanger-loRateSync`, `2bandStepFlanger-loRateNote`, `2bandStepFlanger-loSRateSync`, `2bandStepFlanger-loSRateNote`, `2bandStepFlanger-hiRateSync`, `2bandStepFlanger-hiRateNote`, `2bandStepFlanger-hiSRateSync`, `2bandStepFlanger-hiSRateNote`

### 35 OVERDRIVE
*DYNAMICS · EM p.59*

Creates a soft distortion similar to that produced by vacuum tube amplifiers (overdrive -> amp simulator -> 2-band EQ).

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Drive | 0–127 | # | Degree of distortion; also changes the volume. | `overdrive-drv` |
| Amp Type | SMALL, BUILT-IN, 2-STACK, 3-STACK |  | Type of guitar amp: small amp, single-unit amp, large double stack, large triple stack. | `overdrive-ampType` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `overdrive-eqLo`, `overdrive-eqHi` |
| Pan | L64–63R | # | Stereo location of the output sound. | `overdrive-pan` |
| Level | 0–127 |  | Output level. | `overdrive-level` |

### 36 DISTORTION
*DYNAMICS · EM p.59*

Produces a more intense distortion than Overdrive. Parameters are the same as 35 OVERDRIVE.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Drive | 0–127 | # | Degree of distortion; also changes the volume. | `distortion-drv` |
| Amp Type | SMALL, BUILT-IN, 2-STACK, 3-STACK |  | Type of guitar amp: small, single-unit, large double stack, large triple stack. | `distortion-ampType` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `distortion-eqLo`, `distortion-eqHi` |
| Pan | L64–63R | # | Stereo location of the output sound. | `distortion-pan` |
| Level | 0–127 |  | Output level. | `distortion-level` |

### 37 VS OVERDRIVE
*DYNAMICS · EM p.60*

An overdrive that provides heavy distortion.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Drive | 0–127 | # | Degree of distortion; also changes the volume. | `vsOverdrive-drv` |
| Tone | 0–127 | # | Sound quality of the overdrive effect. | `vsOverdrive-tone` |
| Amp Sw | OFF, ON |  | Turns the amp simulator on/off. | `vsOverdrive-ampSw` |
| Amp Type | SMALL, BUILT-IN, 2-STACK, 3-STACK |  | Type of guitar amp: small, single-unit, large double stack, large triple stack. | `vsOverdrive-ampType` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `vsOverdrive-eqLo`, `vsOverdrive-eqHi` |
| Pan | L64–63R | # | Stereo location of the output sound. | `vsOverdrive-pan` |
| Level | 0–127 |  | Output level. | `vsOverdrive-level` |

### 38 VS DISTORTION
*DYNAMICS · EM p.60*

A distortion that provides heavy distortion. Parameters are the same as 37 VS OVERDRIVE.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Drive | 0–127 | # | Degree of distortion; also changes the volume. | `vsDistortion-drv` |
| Tone | 0–127 | # | Sound quality of the distortion effect. | `vsDistortion-tone` |
| Amp Sw | OFF, ON |  | Turns the amp simulator on/off. | `vsDistortion-ampSw` |
| Amp Type | SMALL, BUILT-IN, 2-STACK, 3-STACK |  | Type of guitar amp. | `vsDistortion-ampType` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `vsDistortion-eqLo`, `vsDistortion-eqHi` |
| Pan | L64–63R | # | Stereo location of the output sound. | `vsDistortion-pan` |
| Level | 0–127 |  | Output level. | `vsDistortion-level` |

### 39 GUITAR AMP SIMULATOR
*DYNAMICS · EM p.60, 61*

Simulates the sound of a guitar amplifier (pre-amp -> speaker).

> Speaker types as for 10 SPEAKER SIMULATOR (see that entry's notes).
> [3P] Used by the forum metal-lead patches (patches/*.a8e) with Pre Amp Type METAL LEAD and speaker MS STACK 1.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Pre Amp Sw | OFF, ON |  | Turns the amp on/off. | `guitarAmpSimulator-ampSw` |
| Pre Amp Type | JC-120, CLEAN TWIN, MATCH DRIVE, BG LEAD, MS1959I, MS1959II, MS1959I+II, SLDN LEAD, METAL 5150, METAL LEAD, OD-1, OD-2 TURBO, DISTORTION, FUZZ |  | Type of guitar amp. | `guitarAmpSimulator-ampType` |
| Pre Amp Volume | 0–127 | # | Volume and amount of distortion of the amp. | `guitarAmpSimulator-ampVolume` |
| Pre Amp Master | 0–127 | # | Volume of the entire pre-amp. | `guitarAmpSimulator-ampMaster` |
| Pre Amp Gain | LOW, MIDDLE, HIGH |  | Amount of pre-amp distortion. | `guitarAmpSimulator-ampGain` |
| Pre Amp Bass / Middle / Treble | 0–127 |  | Tone of the bass / mid / treble range. Middle cannot be set if the Pre Amp Type is MATCH DRIVE. | `guitarAmpSimulator-ampBass`, `guitarAmpSimulator-ampMiddle`, `guitarAmpSimulator-ampTreble` |
| Pre Amp Presence | 0–127 |  | Tone of the ultra-high frequency range. | `guitarAmpSimulator-ampPresence` |
| Pre Amp Bright | OFF, ON |  | ON gives a sharper, brighter sound. Applies to the JC-120, CLEAN TWIN and BG LEAD types. | `guitarAmpSimulator-ampBright` |
| Speaker Sw | OFF, ON |  | Whether the signal passes through the speaker simulation. | `guitarAmpSimulator-spSw` |
| Speaker Type | SMALL 1, SMALL 2, MIDDLE, JC-120, BUILT-IN 1–5, BG STACK 1–2, MS STACK 1–2, METAL STACK, 2-STACK, 3-STACK |  | Type of speaker. | `guitarAmpSimulator-spType` |
| Mic Setting | 1, 2, 3 |  | Location of the mic capturing the speaker; more distant as the value increases. | `guitarAmpSimulator-micSetting` |
| Mic Level | 0–127 |  | Volume of the mic. | `guitarAmpSimulator-micLevel` |
| Direct Level | 0–127 |  | Volume of the direct sound. | `guitarAmpSimulator-directLevel` |
| Pan | L64–63R | # | Stereo location of the output. | `guitarAmpSimulator-pan` |
| Level | 0–127 | # | Output level. | `guitarAmpSimulator-level` |

### 40 COMPRESSOR
*DYNAMICS · EM p.61*

Flattens out high levels and boosts low levels, smoothing out fluctuations in volume.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Attack | 0–127 | # | Time from when the input exceeds the Threshold until compression starts. | `compressor-atk` |
| Threshold | 0–127 | # | Volume at which compression begins. | `compressor-thres` |
| Post Gain | 0–+18 dB |  | Output gain. | `compressor-gain` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high frequency range. | `compressor-eqLo`, `compressor-eqHi` |
| Level | 0–127 | # | Output level. | `compressor-level` |

### 41 LIMITER
*DYNAMICS · EM p.61*

Compresses signals that exceed a specified volume level, preventing distortion.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Release | 0–127 | # | Time after the signal falls below the Threshold until compression is no longer applied. | `limiter-rels` |
| Threshold | 0–127 | # | Volume at which compression begins. | `limiter-thres` |
| Ratio | 1.5:1, 2:1, 4:1, 100:1 |  | Compression ratio. | `limiter-ratio` |
| Post Gain | 0–+18 dB |  | Output gain. | `limiter-gain` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high frequency range. | `limiter-eqLo`, `limiter-eqHi` |
| Level | 0–127 | # | Output level. | `limiter-level` |

### 42 GATE
*DYNAMICS · EM p.61*

Cuts the reverb's delay according to the volume of the sound sent into the effect; use it to create an artificial-sounding decrease in the reverb's decay.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Threshold | 0–127 | # | Volume level at which the gate begins to close. | `gate-thres` |
| Mode | GATE, DUCK |  | GATE: the gate closes when the original sound's volume decreases, cutting it. DUCK (ducking): the gate closes when the original sound's volume increases, cutting it. | `gate-mode` |
| Attack | 0–127 |  | Time for the gate to fully open after being triggered. | `gate-atk` |
| Hold | 0–127 |  | Time until the gate starts closing after the source falls below the Threshold. | `gate-hold` |
| Release | 0–127 |  | Time for the gate to fully close after the hold time. | `gate-rels` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the effect sound (W). | `gate-bal` |
| Level | 0–127 |  | Output level. | `gate-level` |

### 43 DELAY
*DELAY · EM p.62*

A stereo delay. Feedback Mode NORMAL feeds each channel back into itself; CROSS feeds each channel back into the opposite channel.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Delay Left / Delay Right | 0–1300 msec |  | Time until the delay sound is heard (left / right). | `delay-dlyLMsec`, `delay-dlyRMsec` |
| Phase Left / Phase Right | NORMAL, INVERSE |  | Phase of the delay sound (left / right). | `delay-phsL`, `delay-phsR` |
| Feedback Mode | NORMAL, CROSS |  | How the delay sound is fed back into the effect (NORMAL: same channel; CROSS: crossed L/R). | `delay-fbkMode` |
| Feedback | -98–+98% | # | Amount of delay sound fed back into the effect; negative inverts the phase. | `delay-fbk` |
| HF Damp | 200–8000 Hz, BYPASS |  | Frequency above which the fed-back sound is filtered out. BYPASS: no high frequencies are filtered. | `delay-hfDamp` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high frequency range. | `delay-eqLo`, `delay-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the delay sound (W). | `delay-bal` |
| Level | 0–127 |  | Output level. | `delay-level` |

Schema-only members (in the data model, not described in the manual): `delay-dlyLSync`, `delay-dlyLNote`, `delay-dlyRSync`, `delay-dlyRNote`

### 44 LONG DELAY
*DELAY · EM p.62*

A delay that provides a long delay time.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Delay Time | 0–2600 msec |  | Delay from the original sound until the delay sound is heard. | `longDelay-dlyMsec` |
| Phase | NORMAL, INVERSE |  | Phase of the delay (non-inverted / inverted). | `longDelay-phs` |
| Feedback | -98–+98% | # | Proportion of the delay sound returned to the input (negative inverts the phase). | `longDelay-fbk` |
| HF Damp | 200–8000 Hz, BYPASS |  | Frequency at which the high-frequency content of the delayed sound is cut (BYPASS: no cut). | `longDelay-hfDamp` |
| Pan | L64–63R | # | Panning of the delay sound. | `longDelay-pan` |
| Low Gain / High Gain | -15–+15 dB |  | Boost/cut for the low / high frequency range. The manual text describes Low Gain as 'high-frequency range', evidently a typo. | `longDelay-eqLo`, `longDelay-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance of the original sound (D) and the delay sound (W). | `longDelay-bal` |
| Level | 0–127 |  | Output volume. | `longDelay-level` |

Schema-only members (in the data model, not described in the manual): `longDelay-dlySync`, `longDelay-dlyNote`

### 45 SERIAL DELAY
*DELAY · EM p.63*

Two delay units connected in series; feedback can be applied independently to each, producing complex delay sounds.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Delay 1 Time | 0–1300 msec |  | Delay from when sound is input to delay 1 until its delay sound is heard. | `serialDelay-dly1Msec` |
| Delay 1 Feedback | -98–+98% | # | Proportion of the delay sound returned to the input of delay 1 (negative inverts the phase). | `serialDelay-dly1Fbk` |
| Delay 1 HF Damp | 200–8000 Hz, BYPASS |  | Frequency at which the high-frequency content of delay 1's delayed sound is cut (BYPASS: no cut). | `serialDelay-dly1HfDamp` |
| Delay 2 Time | 0–1300 msec |  | Delay from when sound is input to delay 2 until its delay sound is heard. | `serialDelay-dly2Msec` |
| Delay 2 Feedback | -98–+98% | # | Proportion of the delay sound returned to the input of delay 2. | `serialDelay-dly2Fbk` |
| Delay 2 HF Damp | 200–8000 Hz, BYPASS |  | Frequency at which the high-frequency content of delay 2's delayed sound is cut. | `serialDelay-dly2HfDamp` |
| Pan | L64–63R | # | Panning of the delay sound. | `serialDelay-pan` |
| Low Gain / High Gain | -15–+15 dB |  | Boost/cut for the low / high frequency range. | `serialDelay-eqLo`, `serialDelay-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance of the original sound (D) and the delay sound (W). | `serialDelay-bal` |
| Level | 0–127 |  | Output volume. | `serialDelay-level` |

Schema-only members (in the data model, not described in the manual): `serialDelay-dly1Sync`, `serialDelay-dly1Note`, `serialDelay-dly2Sync`, `serialDelay-dly2Note`

### 46 MODULATION DELAY
*DELAY · EM p.63*

Adds modulation to the delayed sound (Feedback Mode NORMAL or CROSS as for 43 DELAY).

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Delay Left / Delay Right | 0–1300 msec |  | Time until the delay sound is heard (left / right). | `modulationDelay-dlyLMsec`, `modulationDelay-dlyRMsec` |
| Feedback Mode | NORMAL, CROSS |  | How the delay sound is fed back into the effect. | `modulationDelay-fbkMode` |
| Feedback | -98–+98% | # | Amount of delay sound fed back; negative inverts the phase. | `modulationDelay-fbk` |
| HF Damp | 200–8000 Hz, BYPASS |  | Frequency above which the fed-back sound is filtered out (BYPASS: none). | `modulationDelay-hfDamp` |
| Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `modulationDelay-rateHz` |
| Depth | 0–127 |  | Depth of modulation. | `modulationDelay-depth` |
| Phase | 0–180 deg |  | Spatial spread of the sound. | `modulationDelay-phs` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high frequency range. | `modulationDelay-eqLo`, `modulationDelay-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the delay sound (W). | `modulationDelay-bal` |
| Level | 0–127 |  | Output level. | `modulationDelay-level` |

Schema-only members (in the data model, not described in the manual): `modulationDelay-dlyLSync`, `modulationDelay-dlyLNote`, `modulationDelay-dlyRSync`, `modulationDelay-dlyRNote`, `modulationDelay-rateSync`, `modulationDelay-rateNote`

### 47 3TAP PAN DELAY
*DELAY · EM p.64*

Produces three delay sounds: center, left and right.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Delay Left / Right / Center | 0–2600 msec |  | Time from the original sound until the left, right and center delay sounds are heard. | `3tapPanDelay-dlyLMsec`, `3tapPanDelay-dlyRMsec`, `3tapPanDelay-dlyCMsec` |
| Center Feedback | -98–+98% | # | Amount of delay sound fed back into the effect; negative inverts the phase. | `3tapPanDelay-fbk` |
| HF Damp | 200–8000 Hz, BYPASS |  | Frequency above which the fed-back sound is filtered out (BYPASS: none). | `3tapPanDelay-hfDamp` |
| Left / Right / Center Level | 0–127 |  | Volume of each delay. | `3tapPanDelay-levelL`, `3tapPanDelay-levelR`, `3tapPanDelay-levelC` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high frequency range. | `3tapPanDelay-eqLo`, `3tapPanDelay-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the delay sound (W). | `3tapPanDelay-bal` |
| Level | 0–127 |  | Output level. | `3tapPanDelay-level` |

Schema-only members (in the data model, not described in the manual): `3tapPanDelay-dlyLSync`, `3tapPanDelay-dlyLNote`, `3tapPanDelay-dlyRSync`, `3tapPanDelay-dlyRNote`, `3tapPanDelay-dlyCSync`, `3tapPanDelay-dlyCNote`

### 48 4TAP PAN DELAY
*DELAY · EM p.64*

A delay with four delays at fixed stereo locations (shown in the manual's diagram).

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Delay 1–4 Time | 0–2600 msec |  | Time from the original sound until delay sounds 1–4 are heard. | `4tapPanDelay-dly1Msec`, `4tapPanDelay-dly2Msec`, `4tapPanDelay-dly3Msec`, `4tapPanDelay-dly4Msec` |
| Delay 1 Feedback | -98–+98% | # | Amount of delay sound fed back into the effect; negative inverts the phase. | `4tapPanDelay-fbk` |
| HF Damp | 200–8000 Hz, BYPASS |  | Frequency above which the fed-back sound is filtered out (BYPASS: none). | `4tapPanDelay-hfDamp` |
| Delay 1–4 Level | 0–127 |  | Volume of each delay. | `4tapPanDelay-level1`, `4tapPanDelay-level2`, `4tapPanDelay-level3`, `4tapPanDelay-level4` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high frequency range. | `4tapPanDelay-eqLo`, `4tapPanDelay-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the delay sound (W). | `4tapPanDelay-bal` |
| Level | 0–127 |  | Output level. | `4tapPanDelay-level` |

Schema-only members (in the data model, not described in the manual): `4tapPanDelay-dly1Sync`, `4tapPanDelay-dly1Note`, `4tapPanDelay-dly2Sync`, `4tapPanDelay-dly2Note`, `4tapPanDelay-dly3Sync`, `4tapPanDelay-dly3Note`, `4tapPanDelay-dly4Sync`, `4tapPanDelay-dly4Note`

### 49 MULTI TAP DELAY
*DELAY · EM p.65*

Four delays whose panning and level can each be set.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Delay 1–4 Time | 0–2600 msec |  | Time until delays 1–4 are heard. | `multiTapDelay-dly1Msec`, `multiTapDelay-dly2Msec`, `multiTapDelay-dly3Msec`, `multiTapDelay-dly4Msec` |
| Delay 1 Feedback | -98–+98% | # | Amount of delay sound fed back into the effect; negative inverts the phase. | `multiTapDelay-fbk` |
| HF Damp | 200–8000 Hz, BYPASS |  | Frequency above which the fed-back sound is filtered out (BYPASS: none). | `multiTapDelay-hfDamp` |
| Delay 1–4 Pan | L64–63R |  | Stereo location of delays 1–4. | `multiTapDelay-pan1`, `multiTapDelay-pan2`, `multiTapDelay-pan3`, `multiTapDelay-pan4` |
| Delay 1–4 Level | 0–127 |  | Output level of delays 1–4. | `multiTapDelay-level1`, `multiTapDelay-level2`, `multiTapDelay-level3`, `multiTapDelay-level4` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high frequency range. | `multiTapDelay-eqLo`, `multiTapDelay-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the effect sound (W). | `multiTapDelay-bal` |
| Level | 0–127 |  | Output level. | `multiTapDelay-level` |

Schema-only members (in the data model, not described in the manual): `multiTapDelay-dly1Sync`, `multiTapDelay-dly1Note`, `multiTapDelay-dly2Sync`, `multiTapDelay-dly2Note`, `multiTapDelay-dly3Sync`, `multiTapDelay-dly3Note`, `multiTapDelay-dly4Sync`, `multiTapDelay-dly4Note`

### 50 REVERSE DELAY
*DELAY · EM p.65*

Adds a reversed and delayed sound to the input sound; a tap delay is connected immediately after the reverse delay.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Threshold | 0–127 |  | Volume at which the reverse delay begins to be applied. | `reverseDelay-threshold` |
| Rev Delay Time | 0–1300 msec |  | Delay from when sound enters the reverse delay until its delay sound is heard. | `reverseDelay-dlyrMsec` |
| Rev Delay Feedback | -98–+98% | # | Proportion of the delay sound returned to the reverse delay's input (negative inverts the phase). | `reverseDelay-dlyrFbk` |
| Rev Delay HF Damp | 200–8000 Hz, BYPASS |  | Frequency at which the high-frequency content of the reverse-delayed sound is cut (BYPASS: no cut). | `reverseDelay-dlyrHfDamp` |
| Rev Delay Pan | L64–63R |  | Panning of the reverse delay sound. | `reverseDelay-dlyrPan` |
| Rev Delay Level | 0–127 |  | Volume of the reverse delay sound. | `reverseDelay-dlyrLvl` |
| Delay 1–3 Time | 0–1300 msec |  | Delay from when sound enters the tap delay until each delay sound is heard. | `reverseDelay-dly1Msec`, `reverseDelay-dly2Msec`, `reverseDelay-dly3Msec` |
| Delay 3 Feedback | -98–+98% | # | Proportion of the delay sound returned to the tap delay's input (negative inverts the phase). | `reverseDelay-dly3Fbk` |
| Delay HF Damp | 200–8000 Hz, BYPASS |  | Frequency at which the tap delay sound is damped (BYPASS: no cut). The manual says 'low-frequency content' here while every other HF Damp cuts high frequencies; probably a typo. | `reverseDelay-dlyHfDamp` |
| Delay 1 Pan / Delay 2 Pan | L64–63R |  | Panning of the tap delay sounds. | `reverseDelay-dly1Pan`, `reverseDelay-dly2Pan` |
| Delay 1 Level / Delay 2 Level | 0–127 |  | Volume of the tap delay sounds. | `reverseDelay-dly1Lvl`, `reverseDelay-dly2Lvl` |
| Low Gain / High Gain | -15–+15 dB |  | Boost/cut for the low / high frequency range. | `reverseDelay-eqLo`, `reverseDelay-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance of the original sound (D) and the delay sound (W). | `reverseDelay-bal` |
| Level | 0–127 |  | Output volume. | `reverseDelay-level` |

Schema-only members (in the data model, not described in the manual): `reverseDelay-dlyrSync`, `reverseDelay-dlyrNote`, `reverseDelay-dly1Sync`, `reverseDelay-dly1Note`, `reverseDelay-dly2Sync`, `reverseDelay-dly2Note`, `reverseDelay-dly3Sync`, `reverseDelay-dly3Note`

### 51 SHUFFLE DELAY
*DELAY · EM p.66*

Adds a shuffle to the delay sound, giving a bouncy delay effect with a swing feel (delays A and B).

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Delay Time | 0–2600 msec | # | Time until the delay sound is heard. | `shuffleDelay-dlyMsec` |
| Shuffle Rate | 0–100 | # | Time before delay B sounds as a percentage of the time before delay A sounds; 100 = the same time. | `shuffleDelay-shuffle` |
| Acceleration | 0–15 |  | Speed with which the Delay Time changes from the current setting to a new setting. | `shuffleDelay-accel` |
| Feedback | -98–+98% | # | Amount of delay fed back into the effect; negative inverts the phase. | `shuffleDelay-fbk` |
| HF Damp | 200–8000 Hz, BYPASS |  | Frequency above which the fed-back sound is filtered out (BYPASS: none). | `shuffleDelay-hfDamp` |
| Pan A / Pan B | L64–63R |  | Stereo location of delay A / B. | `shuffleDelay-panA`, `shuffleDelay-panB` |
| Level A / Level B | 0–127 |  | Volume of delay A / B. | `shuffleDelay-levelA`, `shuffleDelay-levelB` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high frequency range. | `shuffleDelay-eqLo`, `shuffleDelay-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the effect sound (W). | `shuffleDelay-bal` |
| Level | 0–127 |  | Output level. | `shuffleDelay-level` |

Schema-only members (in the data model, not described in the manual): `shuffleDelay-dlySync`, `shuffleDelay-dlyNote`

### 52 3D DELAY
*DELAY · EM p.66*

Applies a 3D (RSS) effect to the delay sound, positioned 90 degrees left and 90 degrees right.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Delay Left / Right / Center | 0–2600 msec |  | Delay from the direct sound until each delay sound is heard. | `3dDelay-dlyLMsec`, `3dDelay-dlyRMsec`, `3dDelay-dlyCMsec` |
| Center Feedback | -98–+98% | # | Proportion of the delay sound fed back into the effect; negative inverts the phase. | `3dDelay-fbk` |
| HF Damp | 200–8000 Hz, BYPASS |  | Frequency above which the fed-back sound is cut (BYPASS: none). | `3dDelay-hfDamp` |
| Left / Right / Center Level | 0–127 |  | Output level of each delay sound. | `3dDelay-lLevel`, `3dDelay-rLevel`, `3dDelay-cLevel` |
| Output Mode | SPEAKER, PHONES |  | SPEAKER for speakers, PHONES for headphones (optimal 3D effect). | `3dDelay-out` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `3dDelay-eqLo`, `3dDelay-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the effect sound (W). | `3dDelay-bal` |
| Level | 0–127 |  | Output level. | `3dDelay-level` |

Schema-only members (in the data model, not described in the manual): `3dDelay-dlyLSync`, `3dDelay-dlyLNote`, `3dDelay-dlyRSync`, `3dDelay-dlyRNote`, `3dDelay-dlyCSync`, `3dDelay-dlyCNote`

### 53 ANALOG DELAY
*DELAY · EM p.67*

A stereo delay whose delay time can be varied smoothly.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Delay Time | 0–1300 msec | # | Time until the delay is heard. | `timeCtrlDelay-dlyMsec` |
| Acceleration | 0–15 |  | Speed with which the Delay Time changes to a newly specified setting; the rate of change of the delay time directly affects the rate of pitch change. | `timeCtrlDelay-accel` |
| Feedback | -98–+98% | # | Amount of delay fed back into the effect; negative inverts the phase. | `timeCtrlDelay-fbk` |
| HF Damp | 200–8000 Hz, BYPASS |  | Frequency above which the fed-back sound is filtered out (BYPASS: none). | `timeCtrlDelay-hfDamp` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high frequency range. | `timeCtrlDelay-eqLo`, `timeCtrlDelay-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the delay sound (W). | `timeCtrlDelay-bal` |
| Level | 0–127 |  | Output level. | `timeCtrlDelay-level` |

Schema-only members (in the data model, not described in the manual): `timeCtrlDelay-dlySync`, `timeCtrlDelay-dlyNote`

### 54 ANALOG LONG DELAY
*DELAY · EM p.67*

A delay whose delay time can be varied smoothly, allowing an extended delay.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Delay Time | 0–2600 msec | # | Time until the delay is heard. | `longTimeCtrlDelay-dlyMsec` |
| Acceleration | 0–15 |  | Speed with which the Delay Time changes to a new setting; directly affects the rate of pitch change. | `longTimeCtrlDelay-accel` |
| Feedback | -98–+98% | # | Amount of delay fed back; negative inverts the phase. | `longTimeCtrlDelay-fbk` |
| HF Damp | 200–8000 Hz, BYPASS |  | Frequency above which the fed-back sound is filtered out (BYPASS: none). | `longTimeCtrlDelay-hfDamp` |
| Pan | L64–63R | # | Stereo location of the delay. | `longTimeCtrlDelay-pan` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high frequency range. | `longTimeCtrlDelay-eqLo`, `longTimeCtrlDelay-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the delay sound (W). | `longTimeCtrlDelay-bal` |
| Level | 0–127 |  | Output level. | `longTimeCtrlDelay-level` |

Schema-only members (in the data model, not described in the manual): `longTimeCtrlDelay-dlySync`, `longTimeCtrlDelay-dlyNote`

### 55 TAPE ECHO
*DELAY · EM p.68*

A virtual tape echo with a realistic tape delay sound; simulates the tape echo section of a Roland RE-201 Space Echo.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Mode | S, M, L, S+M, S+L, M+L, S+M+L |  | Combination of playback heads: three heads with different delay times (S short, M middle, L long). | `tapeEcho-mode` |
| Repeat Rate | 0–127 | # | Tape speed; increasing it shortens the spacing of the delayed sounds. | `tapeEcho-rpRate` |
| Intensity | 0–127 | # | Amount of delay repeats. | `tapeEcho-intens` |
| Bass / Treble | -15–+15 dB |  | Boost/cut for the lower / upper range of the echo sound. | `tapeEcho-bass`, `tapeEcho-treble` |
| Head S / M / L Pan | L64–63R |  | Independent panning for the short, middle and long playback heads. | `tapeEcho-panS`, `tapeEcho-panM`, `tapeEcho-panL` |
| Tape Distortion | 0–5 |  | Amount of tape-dependent distortion added; simulates slight tonal changes detectable by signal-analysis equipment. Higher = more distortion. | `tapeEcho-dist` |
| Wow/Flutter Rate | 0–127 |  | Speed of wow/flutter (complex pitch variation caused by tape wear and rotational irregularity). | `tapeEcho-wfRate` |
| Wow/Flutter Depth | 0–127 |  | Depth of wow/flutter. | `tapeEcho-wfDepth` |
| Echo Level | 0–127 | # | Volume of the echo sound. | `tapeEcho-echoLev` |
| Direct Level | 0–127 | # | Volume of the original sound. | `tapeEcho-directLev` |
| Level | 0–127 |  | Output level. | `tapeEcho-level` |

### 56 LOFI NOISE
*LO-FI · EM p.68*

A lo-fi effect that also adds various types of noise such as white noise and disc (record) noise.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| LoFi Type | 1–9 |  | Degrades the sound quality; poorer as the value increases. | `lofiNoise-lofiType` |
| Post Filter Type | OFF, LPF, HPF |  | Filter following the LoFi effect. OFF: none. LPF: cuts above the cutoff. HPF: cuts below the cutoff. | `lofiNoise-filType` |
| Post Filter Cutoff | 200–8000 Hz |  | Center frequency of the filter. | `lofiNoise-cutoff` |
| W/P Noise Type | WHITE, PINK |  | Switches between white noise and pink noise. | `lofiNoise-wPType` |
| W/P Noise LPF | 200–8000 Hz, BYPASS |  | Center frequency of the low pass filter applied to the white/pink noise (BYPASS: no cut). | `lofiNoise-wPLpf` |
| W/P Noise Level | 0–127 | # | Volume of the white/pink noise. | `lofiNoise-wPLevel` |
| Disc Noise Type | LP, EP, SP, RND |  | Type of record noise; the frequency at which the noise is heard depends on the type. | `lofiNoise-discType` |
| Disc Noise LPF | 200–8000 Hz, BYPASS |  | Cutoff of the low pass filter applied to the record noise (BYPASS: none). | `lofiNoise-discLpf` |
| Disc Noise Level | 0–127 | # | Volume of the record noise. | `lofiNoise-discLevel` |
| Hum Noise Type | 50 Hz, 60 Hz |  | Frequency of the hum noise. | `lofiNoise-humType` |
| Hum Noise LPF | 200–8000 Hz, BYPASS |  | Center frequency of the low pass filter applied to the hum noise (BYPASS: no cut). | `lofiNoise-humLpf` |
| Hum Noise Level | 0–127 | # | Volume of the hum noise. | `lofiNoise-humLevel` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `lofiNoise-eqLo`, `lofiNoise-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the effect sound (W). | `lofiNoise-bal` |
| Level | 0–127 |  | Output level. | `lofiNoise-level` |

### 57 LOFI COMPRESS
*LO-FI · EM p.69*

Intentionally degrades the sound quality for creative purposes (compressor -> lo-fi -> 2-band EQ).

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Pre Filter Type | 1–6 |  | Filter applied before the Lo-Fi effect. 1: compressor off; 2–6: compressor on. | `lofiCompress-preFilt` |
| LoFi Type | 1–9 |  | Degrades the sound quality; poorer as the value increases. | `lofiCompress-lofiType` |
| Post Filter Type | OFF, LPF, HPF |  | OFF: no filter. LPF: cuts above the cutoff. HPF: cuts below the cutoff. | `lofiCompress-postFilt` |
| Post Filter Cutoff | 200–8000 Hz |  | Basic frequency of the post filter. | `lofiCompress-cutoff` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `lofiCompress-eqLo`, `lofiCompress-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the effect sound (W). | `lofiCompress-bal` |
| Level | 0–127 | # | Output level. | `lofiCompress-level` |

### 58 LOFI RADIO
*LO-FI · EM p.69*

A lo-fi effect that also generates radio noise.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| LoFi Type | 1–9 |  | Degrades the sound quality; poorer as the value increases. | `lofiRadio-lofiType` |
| Post Filter Type | OFF, LPF, HPF |  | OFF: no filter. LPF: cuts above the cutoff. HPF: cuts below the cutoff. | `lofiRadio-filType` |
| Post Filter Cutoff | 200–8000 Hz |  | Basic frequency of the post filter. | `lofiRadio-cutoff` |
| Radio Detune | 0–127 | # | Simulates radio tuning noise; the higher the value, the further the tuning drifts. | `lofiRadio-rDetune` |
| Radio Noise Level | 0–127 | # | Volume of the radio noise. | `lofiRadio-rNzLev` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `lofiRadio-eqLo`, `lofiRadio-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the effect sound (W). | `lofiRadio-bal` |
| Level | 0–127 |  | Output level. | `lofiRadio-level` |

### 59 TELEPHONE
*LO-FI · EM p.69*

Produces a muffled sound, like that heard through a telephone.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Voice Quality | 0–15 | # | Audio quality of the telephone voice. | `telephone-quality` |
| Treble | -15–+15 dB |  | Bandwidth of the telephone voice. | `telephone-treble` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the effect sound (W). | `telephone-bal` |
| Level | 0–127 |  | Output level. | `telephone-level` |

### 60 PHONOGRAPH
*LO-FI · EM p.70*

Simulates a sound recorded on an analog record and played back on a record player, including typical record noise and the rotational irregularities of an old turntable.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Signal Distortion | 0–127 |  | Depth of distortion. | `phonograph-dist` |
| Frequency Range | 0–127 |  | Frequency response of the playback system; lower values give the impression of an old system with poor frequency response. | `phonograph-range` |
| Disc Type | LP, EP, SP |  | Rotational speed of the turntable; affects the frequency of the scratch noise. | `phonograph-disc` |
| Scratch Noise Level | 0–127 |  | Amount of noise due to scratches on the record. | `phonograph-scratch` |
| Dust Noise Level | 0–127 |  | Volume of noise due to dust on the record. | `phonograph-dust` |
| Hiss Noise Level | 0–127 |  | Volume of continuous hiss. | `phonograph-hiss` |
| Total Noise Level | 0–127 | # | Volume of the overall noise. | `phonograph-totalNs` |
| Wow | 0–127 |  | Depth of long-cycle rotational irregularity. | `phonograph-wow` |
| Flutter | 0–127 |  | Depth of short-cycle rotational irregularity. | `phonograph-flt` |
| Random | 0–127 |  | Depth of indefinite-cycle rotational irregularity. | `phonograph-random` |
| Total Wow/Flutter | 0–127 | # | Depth of the overall rotational irregularity. | `phonograph-totalWf` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the effect sound (W). | `phonograph-bal` |
| Level | 0–127 |  | Output level. | `phonograph-level` |

### 61 PITCH SHIFTER
*PITCH · EM p.70*

A stereo pitch shifter.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Coarse | -24–+12 semi | #1 | Pitch of the pitch-shifted sound in semitone steps. | `pitchShifter-crs` |
| Fine | -100–+100 cent | #1 | Pitch of the pitch-shifted sound in 2-cent steps. | `pitchShifter-fine` |
| Delay Time | 0–1300 msec |  | Delay from the direct sound until the pitch-shifted sound is heard. | `pitchShifter-dlyMsec` |
| Feedback | -98–+98% | # | Proportion of the pitch-shifted sound fed back into the effect; negative inverts the phase. | `pitchShifter-fbk` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `pitchShifter-eqLo`, `pitchShifter-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the pitch-shifted sound (W). | `pitchShifter-bal` |
| Level | 0–127 |  | Output level. | `pitchShifter-level` |

Schema-only members (in the data model, not described in the manual): `pitchShifter-dlySync`, `pitchShifter-dlyNote`

### 62 2VOICE PITCH SHIFTER
*PITCH · EM p.71*

Two pitch shifters that add two pitch-shifted sounds to the original sound.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Pitch1 Coarse / Pitch1 Fine | -24–+12 semi / -100–+100 cent (2-cent steps) | #1 | Pitch of Pitch Shift 1 in semitones / fine steps. | `2voicePitchShifter-crs1`, `2voicePitchShifter-fine1` |
| Pitch1 Delay | 0–1300 msec |  | Delay from the direct sound until the Pitch Shift 1 sound is heard. | `2voicePitchShifter-dly1Msec` |
| Pitch1 Feedback | -98–+98% | # | Proportion of the pitch-shifted sound fed back into the effect; negative inverts the phase. | `2voicePitchShifter-fbk1` |
| Pitch1 Pan | L64–63R | # | Stereo location of the Pitch Shift 1 sound. | `2voicePitchShifter-pan1` |
| Pitch1 Level | 0–127 |  | Volume of the Pitch Shift 1 sound. | `2voicePitchShifter-level1` |
| Pitch2 Coarse / Pitch2 Fine | -24–+12 semi / -100–+100 cent | #2 | Pitch of Pitch Shift 2 (same as Pitch Shift 1). | `2voicePitchShifter-crs2`, `2voicePitchShifter-fine2` |
| Pitch2 Delay | 0–1300 msec |  | Delay of the Pitch Shift 2 sound. | `2voicePitchShifter-dly2Msec` |
| Pitch2 Feedback | -98–+98% | # | Feedback of Pitch Shift 2. | `2voicePitchShifter-fbk2` |
| Pitch2 Pan | L64–63R | # | Stereo location of the Pitch Shift 2 sound. | `2voicePitchShifter-pan2` |
| Pitch2 Level | 0–127 |  | Volume of the Pitch Shift 2 sound. | `2voicePitchShifter-level2` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `2voicePitchShifter-eqLo`, `2voicePitchShifter-eqHi` |
| Balance | D100:0W–D0:100W |  | Volume balance between the direct sound (D) and the pitch-shifted sound (W). | `2voicePitchShifter-bal` |
| Level | 0–127 |  | Output level. | `2voicePitchShifter-level` |

Schema-only members (in the data model, not described in the manual): `2voicePitchShifter-dly1Sync`, `2voicePitchShifter-dly1Note`, `2voicePitchShifter-dly2Sync`, `2voicePitchShifter-dly2Note`

### 63 STEP PITCH SHIFTER
*PITCH · EM p.71*

A pitch shifter whose amount of pitch shift is varied by a 16-step sequence (STEP RESET available).

> [F] Balance and Level have invalid addresses in Script.xml (00 81 / 00 85); the intended addresses are MFX Parameter 29/30 (01 01 / 01 05).

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Step 01–16 | -24–+12 semi |  | Amount of pitch shift at each step (semitones). | `stepPitchShifter-step01`, `stepPitchShifter-step02`, `stepPitchShifter-step03`, `stepPitchShifter-step04`, `stepPitchShifter-step05`, `stepPitchShifter-step06`, `stepPitchShifter-step07`, `stepPitchShifter-step08`, `stepPitchShifter-step09`, `stepPitchShifter-step10`, `stepPitchShifter-step11`, `stepPitchShifter-step12`, `stepPitchShifter-step13`, `stepPitchShifter-step14`, `stepPitchShifter-step15`, `stepPitchShifter-step16` |
| Rate | 0.05–10.00 Hz | # | Rate at which the 16-step sequence cycles. | `stepPitchShifter-rateHz` |
| Attack | 0–127 | # | Speed at which the amount of pitch shift changes between steps. | `stepPitchShifter-attack` |
| Gate Time | 0–127 | # | Duration of the pitch-shifted sound at each step. | `stepPitchShifter-gate` |
| Fine | -100–+100 cent |  | Pitch-shift adjustment for all steps (2-cent units). | `stepPitchShifter-fine` |
| Delay Time | 0–1300 msec |  | Delay from the original sound until the pitch-shifted sound is heard. | `stepPitchShifter-dlyMsec` |
| Feedback | -98–+98% | # | Proportion of the pitch-shifted sound returned to the input (negative inverts the phase). | `stepPitchShifter-fbk` |
| Low Gain / High Gain | -15–+15 dB |  | Boost/cut for the low / high frequency range. | `stepPitchShifter-eqLo`, `stepPitchShifter-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance of the original sound (D) and the pitch-shifted sound (W). | `stepPitchShifter-bal` |
| Level | 0–127 |  | Output volume. | `stepPitchShifter-level` |

Schema-only members (in the data model, not described in the manual): `stepPitchShifter-rateSync`, `stepPitchShifter-rateNote`, `stepPitchShifter-dlySync`, `stepPitchShifter-dlyNote`

### 64 REVERB
*REVERB · EM p.72*

Adds reverberation to the sound, simulating an acoustic space.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Type | ROOM1, ROOM2, STAGE1, STAGE2, HALL1, HALL2 |  | ROOM1: dense reverb with short decay. ROOM2: sparse reverb with short decay. STAGE1: more late reverberation. STAGE2: strong early reflections. HALL1: clear reverberance. HALL2: rich reverberance. | `reverb-type` |
| Pre Delay | 0.0–100 msec |  | Delay from the direct sound until the reverb sound is heard. | `reverb-dly` |
| Time | 0–127 | # | Length of the reverberation. | `reverb-tm` |
| HF Damp | 200–8000 Hz, BYPASS |  | Frequency above which the reverberant sound is cut; lower settings cut more highs for a softer, more muted reverb. BYPASS: no cut. | `reverb-hfDamp` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `reverb-eqLo`, `reverb-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the reverb sound (W). | `reverb-bal` |
| Level | 0–127 |  | Output level. | `reverb-level` |

### 65 GATED REVERB
*REVERB · EM p.72*

A special reverb in which the reverberant sound is cut off before its natural length.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Type | NORMAL, REVERSE, SWEEP1, SWEEP2 |  | NORMAL: conventional gated reverb. REVERSE: backwards reverb. SWEEP1: the reverberant sound moves from right to left. SWEEP2: from left to right. | `gatedReverb-type` |
| Pre Delay | 0.0–100 msec |  | Delay from the direct sound until the reverb sound is heard. | `gatedReverb-dly` |
| Gate Time | 5–500 msec |  | Time from when the reverb is heard until it disappears. | `gatedReverb-tm` |
| Low Gain / High Gain | -15–+15 dB |  | Gain of the low / high range. | `gatedReverb-eqLo`, `gatedReverb-eqHi` |
| Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the reverb sound (W). | `gatedReverb-bal` |
| Level | 0–127 | # | Output level. | `gatedReverb-level` |

### 66 OVERDRIVE → CHORUS
*COMBINATION · EM p.72*

Overdrive followed by chorus, in series.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Overdrive Drive | 0–127 | # | Degree of distortion; also changes the volume. | `overdriveToChorus-odDrv` |
| Overdrive Pan | L64–63R | # | Stereo location of the overdrive sound. | `overdriveToChorus-odPan` |
| Chorus Pre Delay | 0.0–100 msec |  | Delay from the direct sound until the chorus sound is heard. | `overdriveToChorus-choDly` |
| Chorus Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `overdriveToChorus-choRateHz` |
| Chorus Depth | 0–127 |  | Depth of modulation. | `overdriveToChorus-choDepth` |
| Chorus Balance | D100:0W–D0:100W | # | Volume balance between the sound sent through the chorus (W) and the sound not sent through it (D). | `overdriveToChorus-choBal` |
| Level | 0–127 |  | Output level. | `overdriveToChorus-level` |

Schema-only members (in the data model, not described in the manual): `overdriveToChorus-choRateSync`, `overdriveToChorus-choRateNote`

### 67 OVERDRIVE → FLANGER
*COMBINATION · EM p.73*

Overdrive followed by flanger, in series.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Overdrive Drive | 0–127 | # | Degree of distortion; also changes the volume. | `overdriveToFlanger-odDrv` |
| Overdrive Pan | L64–63R | # | Stereo location of the overdrive sound. | `overdriveToFlanger-odPan` |
| Flanger Pre Delay | 0.0–100 msec |  | Delay from when the direct sound begins until the flanger sound is heard. | `overdriveToFlanger-flgDly` |
| Flanger Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `overdriveToFlanger-flgRateHz` |
| Flanger Depth | 0–127 |  | Depth of modulation. | `overdriveToFlanger-flgDepth` |
| Flanger Feedback | -98–+98% | # | Proportion of the flanger sound fed back into the effect; negative inverts the phase. | `overdriveToFlanger-flgFbk` |
| Flanger Balance | D100:0W–D0:100W | # | Balance between the sound sent through the flanger (W) and not (D). | `overdriveToFlanger-flgBal` |
| Level | 0–127 |  | Output level. | `overdriveToFlanger-level` |

Schema-only members (in the data model, not described in the manual): `overdriveToFlanger-flgRateSync`, `overdriveToFlanger-flgRateNote`

### 68 OVERDRIVE → DELAY
*COMBINATION · EM p.73*

Overdrive followed by delay, in series.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Overdrive Drive | 0–127 | # | Degree of distortion; also changes the volume. | `overdriveToDelay-odDrv` |
| Overdrive Pan | L64–63R | # | Stereo location of the overdrive sound. | `overdriveToDelay-odPan` |
| Delay Time | 0–2600 msec |  | Delay from the direct sound until the delay sound is heard. | `overdriveToDelay-dlyMsec` |
| Delay Feedback | -98–+98% | # | Proportion of the delay sound fed back into the effect; negative inverts the phase. | `overdriveToDelay-dlyFbk` |
| Delay HF Damp | 200–8000 Hz, BYPASS |  | Frequency above which the fed-back sound is cut (BYPASS: none). | `overdriveToDelay-dlyHfDamp` |
| Delay Balance | D100:0W–D0:100W | # | Balance between the sound sent through the delay (W) and not (D). | `overdriveToDelay-dlyBal` |
| Level | 0–127 |  | Output level. | `overdriveToDelay-level` |

Schema-only members (in the data model, not described in the manual): `overdriveToDelay-dlySync`, `overdriveToDelay-dlyNote`

### 69 DISTORTION → CHORUS
*COMBINATION · EM p.73*

Distortion followed by chorus. Parameters as 66 OVERDRIVE→CHORUS with Overdrive Drive/Pan replaced by Distortion Drive/Pan.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Distortion Drive | 0–127 | # | Degree of distortion; also changes the volume. | `distortionToChorus-dstDrv` |
| Distortion Pan | L64–63R | # | Stereo location of the distortion sound. | `distortionToChorus-dstPan` |
| Chorus Pre Delay | 0.0–100 msec |  | Delay from the direct sound until the chorus sound is heard. | `distortionToChorus-choDly` |
| Chorus Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `distortionToChorus-choRateHz` |
| Chorus Depth | 0–127 |  | Depth of modulation. | `distortionToChorus-choDepth` |
| Chorus Balance | D100:0W–D0:100W | # | Balance between the sound sent through the chorus (W) and not (D). | `distortionToChorus-choBal` |
| Level | 0–127 |  | Output level. | `distortionToChorus-level` |

Schema-only members (in the data model, not described in the manual): `distortionToChorus-choRateSync`, `distortionToChorus-choRateNote`

### 70 DISTORTION → FLANGER
*COMBINATION · EM p.74*

Distortion followed by flanger. Parameters as 67 OVERDRIVE→FLANGER with Overdrive Drive/Pan replaced by Distortion Drive/Pan.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Distortion Drive | 0–127 | # | Degree of distortion; also changes the volume. | `distortionToFlanger-dstDrv` |
| Distortion Pan | L64–63R | # | Stereo location of the distortion sound. | `distortionToFlanger-dstPan` |
| Flanger Pre Delay | 0.0–100 msec |  | Delay from when the direct sound begins until the flanger sound is heard. | `distortionToFlanger-flgDly` |
| Flanger Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `distortionToFlanger-flgRateHz` |
| Flanger Depth | 0–127 |  | Depth of modulation. | `distortionToFlanger-flgDepth` |
| Flanger Feedback | -98–+98% | # | Proportion of the flanger sound fed back; negative inverts the phase. | `distortionToFlanger-flgFbk` |
| Flanger Balance | D100:0W–D0:100W | # | Balance between the sound sent through the flanger (W) and not (D). | `distortionToFlanger-flgBal` |
| Level | 0–127 |  | Output level. | `distortionToFlanger-level` |

Schema-only members (in the data model, not described in the manual): `distortionToFlanger-flgRateSync`, `distortionToFlanger-flgRateNote`

### 71 DISTORTION → DELAY
*COMBINATION · EM p.74*

Distortion followed by delay. Parameters as 68 OVERDRIVE→DELAY with Overdrive Drive/Pan replaced by Distortion Drive/Pan.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Distortion Drive | 0–127 | # | Degree of distortion; also changes the volume. | `distortionToDelay-dstDrv` |
| Distortion Pan | L64–63R | # | Stereo location of the distortion sound. | `distortionToDelay-dstPan` |
| Delay Time | 0–2600 msec |  | Delay from the direct sound until the delay sound is heard. | `distortionToDelay-dlyMsec` |
| Delay Feedback | -98–+98% | # | Proportion of the delay sound fed back; negative inverts the phase. | `distortionToDelay-dlyFbk` |
| Delay HF Damp | 200–8000 Hz, BYPASS |  | Frequency above which the fed-back sound is cut (BYPASS: none). | `distortionToDelay-dlyHfDamp` |
| Delay Balance | D100:0W–D0:100W | # | Balance between the sound sent through the delay (W) and not (D). | `distortionToDelay-dlyBal` |
| Level | 0–127 |  | Output level. | `distortionToDelay-level` |

Schema-only members (in the data model, not described in the manual): `distortionToDelay-dlySync`, `distortionToDelay-dlyNote`

### 72 ENHANCER → CHORUS
*COMBINATION · EM p.74*

Enhancer followed by chorus, in series.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Enhancer Sens | 0–127 | # | Sensitivity of the enhancer. | `enhancerToChorus-ehSens` |
| Enhancer Mix | 0–127 | # | Level of the overtones generated by the enhancer. | `enhancerToChorus-ehMix` |
| Chorus Pre Delay | 0.0–100 msec |  | Delay from the direct sound until the chorus sound is heard. | `enhancerToChorus-choDly` |
| Chorus Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `enhancerToChorus-choRateHz` |
| Chorus Depth | 0–127 |  | Depth of modulation. | `enhancerToChorus-choDepth` |
| Chorus Balance | D100:0W–D0:100W | # | Balance between the sound sent through the chorus (W) and not (D). | `enhancerToChorus-choBal` |
| Level | 0–127 |  | Output level. | `enhancerToChorus-level` |

Schema-only members (in the data model, not described in the manual): `enhancerToChorus-choRateSync`, `enhancerToChorus-choRateNote`

### 73 ENHANCER → FLANGER
*COMBINATION · EM p.74*

Enhancer followed by flanger, in series.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Enhancer Sens | 0–127 | # | Sensitivity of the enhancer. | `enhancerToFlanger-ehSens` |
| Enhancer Mix | 0–127 | # | Level of the overtones generated by the enhancer. | `enhancerToFlanger-ehMix` |
| Flanger Pre Delay | 0.0–100 msec |  | Delay from when the direct sound begins until the flanger sound is heard. | `enhancerToFlanger-flgDly` |
| Flanger Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `enhancerToFlanger-flgRateHz` |
| Flanger Depth | 0–127 |  | Depth of modulation. | `enhancerToFlanger-flgDepth` |
| Flanger Feedback | -98–+98% | # | Proportion of the flanger sound fed back; negative inverts the phase. | `enhancerToFlanger-flgFbk` |
| Flanger Balance | D100:0W–D0:100W | # | Balance between the sound sent through the flanger (W) and not (D). | `enhancerToFlanger-flgBal` |
| Level | 0–127 |  | Output level. | `enhancerToFlanger-level` |

Schema-only members (in the data model, not described in the manual): `enhancerToFlanger-flgRateSync`, `enhancerToFlanger-flgRateNote`

### 74 ENHANCER → DELAY
*COMBINATION · EM p.75*

Enhancer followed by delay, in series.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Enhancer Sens | 0–127 | # | Sensitivity of the enhancer. | `enhancerToDelay-ehSens` |
| Enhancer Mix | 0–127 | # | Level of the overtones generated by the enhancer. | `enhancerToDelay-ehMix` |
| Delay Time | 0–2600 msec |  | Delay from the direct sound until the delay sound is heard. | `enhancerToDelay-dlyMsec` |
| Delay Feedback | -98–+98% | # | Proportion of the delay sound fed back; negative inverts the phase. | `enhancerToDelay-dlyFbk` |
| Delay HF Damp | 200–8000 Hz, BYPASS |  | Frequency above which the fed-back sound is cut (BYPASS: none). | `enhancerToDelay-dlyHfDamp` |
| Delay Balance | D100:0W–D0:100W | # | Balance between the sound sent through the delay (W) and not (D). | `enhancerToDelay-dlyBal` |
| Level | 0–127 |  | Output level. | `enhancerToDelay-level` |

Schema-only members (in the data model, not described in the manual): `enhancerToDelay-dlySync`, `enhancerToDelay-dlyNote`

### 75 CHORUS → DELAY
*COMBINATION · EM p.75*

Chorus followed by delay, in series.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Chorus Pre Delay | 0.0–100 msec |  | Delay from the direct sound until the chorus sound is heard. | `chorusToDelay-choDly` |
| Chorus Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `chorusToDelay-choRateHz` |
| Chorus Depth | 0–127 |  | Depth of modulation. | `chorusToDelay-choDepth` |
| Chorus Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the chorus sound (W). | `chorusToDelay-choBal` |
| Delay Time | 0–2600 msec |  | Delay from the direct sound until the delay sound is heard. | `chorusToDelay-dlyMsec` |
| Delay Feedback | -98–+98% | # | Proportion of the delay sound fed back; negative inverts the phase. | `chorusToDelay-dlyFbk` |
| Delay HF Damp | 200–8000 Hz, BYPASS |  | Frequency above which the fed-back sound is cut (BYPASS: none). | `chorusToDelay-dlyHfDamp` |
| Delay Balance | D100:0W–D0:100W | # | Balance between the sound sent through the delay (W) and not (D). | `chorusToDelay-dlyBal` |
| Level | 0–127 |  | Output level. | `chorusToDelay-level` |

Schema-only members (in the data model, not described in the manual): `chorusToDelay-choRateSync`, `chorusToDelay-choRateNote`, `chorusToDelay-dlySync`, `chorusToDelay-dlyNote`

### 76 FLANGER → DELAY
*COMBINATION · EM p.75*

Flanger followed by delay, in series.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Flanger Pre Delay | 0.0–100 msec |  | Delay from when the direct sound begins until the flanger sound is heard. | `flangerToDelay-flgDly` |
| Flanger Rate | 0.05–10.00 Hz | # | Frequency of modulation. | `flangerToDelay-flgRateHz` |
| Flanger Depth | 0–127 |  | Depth of modulation. | `flangerToDelay-flgDepth` |
| Flanger Feedback | -98–+98% | # | Proportion of the flanger sound fed back; negative inverts the phase. | `flangerToDelay-flgFbk` |
| Flanger Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the flanger sound (W). | `flangerToDelay-flgBal` |
| Delay Time | 0–2600 msec |  | Delay from the direct sound until the delay sound is heard. | `flangerToDelay-dlyMsec` |
| Delay Feedback | -98–+98% | # | Proportion of the delay sound fed back; negative inverts the phase. | `flangerToDelay-dlyFbk` |
| Delay HF Damp | 200–8000 Hz, BYPASS |  | Frequency above which the fed-back sound is cut (BYPASS: none). | `flangerToDelay-dlyHfDamp` |
| Delay Balance | D100:0W–D0:100W | # | Balance between the sound sent through the delay (W) and not (D). | `flangerToDelay-dlyBal` |
| Level | 0–127 |  | Output level. | `flangerToDelay-level` |

Schema-only members (in the data model, not described in the manual): `flangerToDelay-flgRateSync`, `flangerToDelay-flgRateNote`, `flangerToDelay-dlySync`, `flangerToDelay-dlyNote`

### 77 CHORUS → FLANGER
*COMBINATION · EM p.76*

Chorus followed by flanger, in series.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Chorus Pre Delay | 0.0–100 msec |  | Delay from the direct sound until the chorus sound is heard. | `chorusToFlanger-choDly` |
| Chorus Rate | 0.05–10.00 Hz | # | Modulation frequency of the chorus. | `chorusToFlanger-choRateHz` |
| Chorus Depth | 0–127 |  | Modulation depth of the chorus. | `chorusToFlanger-choDepth` |
| Chorus Balance | D100:0W–D0:100W | # | Volume balance between the direct sound (D) and the chorus sound (W). | `chorusToFlanger-choBal` |
| Flanger Pre Delay | 0.0–100 msec |  | Delay from when the direct sound begins until the flanger sound is heard. | `chorusToFlanger-flgDly` |
| Flanger Rate | 0.05–10.00 Hz | # | Modulation frequency of the flanger. | `chorusToFlanger-flgRateHz` |
| Flanger Depth | 0–127 |  | Modulation depth of the flanger. | `chorusToFlanger-flgDepth` |
| Flanger Feedback | -98–+98% | # | Proportion of the flanger sound fed back; negative inverts the phase. | `chorusToFlanger-flgFbk` |
| Flanger Balance | D100:0W–D0:100W | # | Balance between the sound sent through the flanger (W) and not (D). | `chorusToFlanger-flgBal` |
| Level | 0–127 |  | Output level. | `chorusToFlanger-level` |

Schema-only members (in the data model, not described in the manual): `chorusToFlanger-choRateSync`, `chorusToFlanger-choRateNote`, `chorusToFlanger-flgRateSync`, `chorusToFlanger-flgRateNote`

### 78 SYMPATHETIC RESONANCE
*PIANO · EM p.76*

On an acoustic piano, holding the damper pedal lets other strings resonate in sympathy with the notes played, creating rich, spacious resonance. This effect simulates these sympathetic resonances (followed by a 3-band EQ).

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Depth | 0–127 | # | Depth of the effect. | `sympatheticResonance-depth` |
| Damper | 0–127 | # | Depth to which the damper pedal is pressed (controls the resonant sound). | `sympatheticResonance-damp` |
| Pre LPF | 16–15000 Hz, BYPASS |  | Frequency of the filter that cuts the high-frequency content of the input sound (BYPASS: no cut). | `sympatheticResonance-preLpf` |
| Pre HPF | BYPASS, 16–15000 Hz |  | Frequency of the filter that cuts the low-frequency content of the input sound (BYPASS: no cut). | `sympatheticResonance-preHpf` |
| Peaking Freq | 200–8000 Hz |  | Frequency of the filter that boosts/cuts a specific region of the input sound. | `sympatheticResonance-pkgFreq` |
| Peaking Gain | -15–+15 dB |  | Amount of boost/cut at the Peaking Freq. | `sympatheticResonance-pkgGain` |
| Peaking Q | 0.5, 1.0, 2.0, 4.0, 8.0 |  | Width of the region boosted/cut by Peaking Gain (larger values = narrower). | `sympatheticResonance-pkgQ` |
| HF Damp | 16–15000 Hz, BYPASS |  | Frequency at which the high-frequency content of the resonant sound is cut (BYPASS: no cut). | `sympatheticResonance-hfDamp` |
| LF Damp | BYPASS, 16–15000 Hz |  | Frequency at which the low-frequency content of the resonant sound is cut (BYPASS: no cut). | `sympatheticResonance-lfDamp` |
| Lid | 1–6 |  | Simulates the change in sound when the lid of a grand piano is set at different heights. | `sympatheticResonance-lid` |
| EQ Low Freq / EQ Low Gain | 200, 400 Hz / -15–+15 dB |  | Frequency and amount of the low-range EQ boost/cut. | `sympatheticResonance-loFreq`, `sympatheticResonance-loGain` |
| EQ Mid Freq / EQ Mid Gain / EQ Mid Q | 200–8000 Hz / -15–+15 dB / 0.5, 1.0, 2.0, 4.0, 8.0 |  | Frequency, amount and width (larger Q = narrower) of the midrange EQ. | `sympatheticResonance-midFreq`, `sympatheticResonance-midGain`, `sympatheticResonance-midQ` |
| EQ High Freq / EQ High Gain | 2000, 4000, 8000 Hz / -15–+15 dB |  | Frequency and amount of the high-range EQ boost/cut. | `sympatheticResonance-hiFreq`, `sympatheticResonance-hiGain` |
| Level | 0–127 |  | Output level. | `sympatheticResonance-level` |

## Chorus unit types

### 01 CHORUS
*CHORUS · EM p.77*

The chorus unit used as a chorus (chorusType = CHORUS).

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Filter Type | OFF, LPF, HPF |  | OFF: no filter. LPF: cuts above the Cutoff Freq. HPF: cuts below the Cutoff Freq. | `chorus-filt` |
| Cutoff Freq | 200–8000 Hz |  | Basic frequency of the filter. | `chorus-splt` |
| Pre Delay | 0.0–100 msec |  | Delay from the direct sound until the chorus sound is heard. | `chorus-delay` |
| Rate | 0.05–10.00 Hz |  | Frequency of modulation. | `chorus-rateHz` |
| Depth | 0–127 |  | Depth of modulation. | `chorus-depth` |
| Phase | 0–180 deg |  | Spatial spread of the sound. | `chorus-phs` |
| Feedback | 0–127 |  | Amount of the chorus sound fed back into the effect. | `chorus-fb` |

Schema-only members (in the data model, not described in the manual): `chorus-rateSync`, `chorus-rateNote`

### 02 DELAY
*CHORUS · EM p.77*

The chorus unit used as a stereo delay (chorusType = DELAY) with left, right and center delays.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Delay Left / Delay Right / Delay Center | 0–1000 msec |  | Delay from the direct sound until each delay sound is heard. | `delay-dlyLMsec`, `delay-dlyRMsec`, `delay-dlyCMsec` |
| Center Feedback | -98–+98% |  | Proportion of the delay sound fed back into the effect; negative inverts the phase. | `delay-fbk` |
| HF Damp | 200–8000 Hz, BYPASS |  | Frequency above which the fed-back sound is cut. BYPASS: no cut. | `delay-hfDamp` |
| Left Level / Right Level / Center Level | 0–127 |  | Volume of each delay sound. | `delay-levelL`, `delay-levelR`, `delay-levelC` |

Schema-only members (in the data model, not described in the manual): `delay-dlyLSync`, `delay-dlyLNote`, `delay-dlyRSync`, `delay-dlyRNote`, `delay-dlyCSync`, `delay-dlyCNote`

## Reverb unit types

### 01 REVERB
*REVERB · EM p.78*

Basic reverb unit type (reverbType = REVERB), which also offers delay and pan-delay variations.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Type | ROOM1, ROOM2, STAGE1, STAGE2, HALL1, HALL2, DELAY, PAN-DELAY |  | ROOM1: short reverb with high density. ROOM2: short reverb with low density. STAGE1: more late reverberation. STAGE2: strong early reflections. HALL1: very clear-sounding reverb. HALL2: rich reverb. DELAY: conventional delay effect. PAN-DELAY: delay with echoes that pan left and right. | `reverb-type` |
| Time | 0–127 |  | Length of the reverberation (types ROOM1–HALL2) or the delay time (types DELAY, PAN-DELAY). | `reverb-time` |
| HF Damp | 200–8000 Hz, BYPASS |  | Frequency above which the high-frequency content of the reverb sound is cut ('damped'). BYPASS: no cut. | `reverb-HF` |
| Delay Feedback | 0–127 |  | Amount of delay sound returned to the input; valid only when Type is DELAY or PAN-DELAY. | `reverb-fb` |

### 02 SRV ROOM
*REVERB · EM p.78*

Reverb that simulates typical room acoustic reflections in greater detail.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Pre Delay | 0.0–100 msec |  | Delay from the direct sound until the reverb sound is heard. | `srvRoom-dly` |
| Time | 0–127 |  | Length of the reverberation. | `srvRoom-tm` |
| Size | 1–8 |  | Size of the simulated room or hall. | `srvRoom-size` |
| High Cut | 160–12500 Hz, BYPASS |  | Frequency above which the high-frequency content of the reverb is reduced. BYPASS: no reduction. | `srvRoom-hicut` |
| Density | 0–127 |  | Density of the reverb. | `srvRoom-dnsty` |
| Diffusion | 0–127 |  | Change in the density of the reverb over time; higher = density increases more with time (most pronounced with long reverb times). | `srvRoom-dfsn` |
| LF Damp Freq | 50–4000 Hz |  | Frequency below which the low-frequency content of the reverb is reduced ('damped'). | `srvRoom-lfdmpf` |
| LF Damp Gain | -36–0 dB |  | Amount of damping applied below LF Damp Freq; 0 = no reduction of the low frequencies. | `srvRoom-lfdmpg` |
| HF Damp Freq | 4000–12500 Hz |  | Frequency above which the high-frequency content of the reverb is reduced ('damped'). | `srvRoom-HFDmpF` |
| HF Damp Gain | -36–0 dB |  | Amount of damping applied above HF Damp Freq; 0 = no reduction of the high frequencies. | `srvRoom-HFDmpG` |

### 03 SRV HALL
*REVERB · EM p.78*

Reverb that simulates typical concert hall acoustic reflections in greater detail. Same parameters as SRV ROOM.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Pre Delay | 0.0–100 msec |  | Delay from the direct sound until the reverb sound is heard. | `srvHall-dly` |
| Time | 0–127 |  | Length of the reverberation. | `srvHall-tm` |
| Size | 1–8 |  | Size of the simulated room or hall. | `srvHall-size` |
| High Cut | 160–12500 Hz, BYPASS |  | Frequency above which the high-frequency content is reduced. BYPASS: no reduction. | `srvHall-hicut` |
| Density | 0–127 |  | Density of the reverb. | `srvHall-dnsty` |
| Diffusion | 0–127 |  | Change in density over time; higher = density increases more with time. | `srvHall-dfsn` |
| LF Damp Freq | 50–4000 Hz |  | Frequency below which the low frequencies are damped. | `srvHall-lfdmpf` |
| LF Damp Gain | -36–0 dB |  | Amount of low-frequency damping; 0 = none. | `srvHall-lfdmpg` |
| HF Damp Freq | 4000–12500 Hz |  | Frequency above which the high frequencies are damped. | `srvHall-HFDmpF` |
| HF Damp Gain | -36–0 dB |  | Amount of high-frequency damping; 0 = none. | `srvHall-HFDmpG` |

### 04 SRV PLATE
*REVERB · EM p.78*

Simulates a reverb plate, an artificial reverb unit that derives its sound from the vibration of a metallic plate. Same parameters as SRV ROOM.

| Parameter | Values | # | Meaning | Data model |
|---|---|---|---|---|
| Pre Delay | 0.0–100 msec |  | Delay from the direct sound until the reverb sound is heard. | `srvPlate-dly` |
| Time | 0–127 |  | Length of the reverberation. | `srvPlate-tm` |
| Size | 1–8 |  | Size of the simulated space. | `srvPlate-size` |
| High Cut | 160–12500 Hz, BYPASS |  | Frequency above which the high-frequency content is reduced. BYPASS: no reduction. | `srvPlate-hicut` |
| Density | 0–127 |  | Density of the reverb. | `srvPlate-dnsty` |
| Diffusion | 0–127 |  | Change in density over time; higher = density increases more with time. | `srvPlate-dfsn` |
| LF Damp Freq | 50–4000 Hz |  | Frequency below which the low frequencies are damped. | `srvPlate-lfdmpf` |
| LF Damp Gain | -36–0 dB |  | Amount of low-frequency damping; 0 = none. | `srvPlate-lfdmpg` |
| HF Damp Freq | 4000–12500 Hz |  | Frequency above which the high frequencies are damped. | `srvPlate-HFDmpF` |
| HF Damp Gain | -36–0 dB |  | Amount of high-frequency damping; 0 = none. | `srvPlate-HFDmpG` |

## Coverage

Data-model values (root `fm`) without a KB entry:

- `fm.pat.common.reserve0D`
- `fm.pat.common.reserve1E`
- `fm.pat.common.reserve1F`
- `fm.pat.common.reserve21`
- `fm.pat.tone[].reserve38`
- `fm.system.controller.reserve00`
- `fm.system.controller.reserve01`
- `fm.system.controller.reserve03`
- `fm.system.controller.reserve04`
- `fm.system.controller.reserve06`
- `fm.system.controller.reserve07`
- `fm.system.controller.reserve08`
- `fm.system.controller.reserve09`
