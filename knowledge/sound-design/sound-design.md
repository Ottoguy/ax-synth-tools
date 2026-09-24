# AX-Synth sound design: what settings produce what sounds

Generated from `knowledge/sound_design.toml` and `knowledge/sound_recipes.toml` by `research/tools/build_knowledge.py`. **Do not edit by hand.** Machine-readable: `knowledge/knowledge.json` → `sound_design`.

Source: Gordon Reid, 'Synth Secrets', Sound On Sound 1999-2004, 63 parts (https://www.soundonsound.com/series/synth-secrets-sound-sound). Evidence: principle/descriptor meanings and recipe summaries = [3P] Synth Secrets (parts in 'ss'); all AX-Synth mappings (ax/steps/performance/effects, values, waves, factory Tones) = [I] inference, not hardware-verified.

Per-article digests: [`digests/`](digests/). Parameter meanings: [`../knowledge.md`](../knowledge.md).

## Contents

1. [Principles](#principles)
2. [Descriptors (words → settings)](#descriptors)
3. [Recipes](#recipes)
4. [Synth Secrets parts](#synth-secrets-parts)

## Principles

### The source waveform decides the instrument family
*id `source.waveform_defines_family` · Synth Secrets SS01, SS02, SS10, SS24, SS47, SS53, SS63*

Choose the wave first; filters and envelopes can't create harmonics that aren't in the source.
- Sawtooth (all harmonics, 1/n): bright, full, buzzy; brass, bowed strings, most leads and pads.
- Square (odd harmonics): hollow, woody; clarinet, closed pipes (pan pipes).
- Narrow pulse (5-15 %): thin, nasal, reedy; oboe, bassoon.
- 25-45 % pulse: between hollow and full; recorder (40 %), 'jazz guitar' (25 %).
- Triangle/sine: soft, pure, few harmonics; flutes, whistles, sub bass, drum bodies.
- Noise: drums, breath, wind, cymbals.
- Inharmonic sources (ring mod, FM, metallic PCM): bells, metal, clangs.

- `tone.wave_number`: pick the wave family first: saws 174-193, squares 194-202, pulses 203-212 (JP8 10/15/25/30/40/45 %), triangles 213-216, sine 220, noise 232/233, metallic 239-241
- `architecture.tone_signal_path`: the WG (wave) is the source; TVF and TVA only remove or shape what the wave contains

### Timbres that don't change over time sound static and organ-like
*id `time.static_sounds_organlike` · Synth Secrets SS03, SS10, SS14, SS63*

No natural sound is stationary. However rich the wave, a sound whose spectrum and loudness never change sounds like an organ (or a cheap test tone). Give sustained sounds movement: filter envelopes, slow LFOs, detuned layers, chorus, random wander, or player control. Effects add interest but don't change the essential nature of the sound.

- `tone.fenv_depth`: any non-zero filter envelope gives the timbre a life-cycle
- `tone.lfo_depth_tvf`: slow LFO on cutoff (rate low) for gentle movement
- `common.analog_feel`: 1/f wander (20-40) makes sustained notes feel alive
- `tone.fine_tune`: a second, slightly detuned tone adds beating movement

### In natural instruments, louder means brighter
*id `dynamics.louder_is_brighter` · Synth Secrets SS12, SS24, SS25, SS29, SS35, SS42, SS51*

Blown, bowed, struck and plucked instruments get brighter (more and stronger upper harmonics) as they get louder, and duller as they get quieter. Couple brightness to whatever sets loudness: velocity, the amplitude envelope, pressure/aftertouch. Keeping brightness constant while loudness changes sounds synthetic. (Deliberately inverting it is an FM-style special effect.)

- `tone.cutoff_vel_sens`: positive: harder = brighter
- `tone.fenv_vel_sens`: positive: harder = bigger filter sweep
- `matrix.source`: AFTERTOUCH or CC01 to both LEVEL and CUTOFF (destinations) for sustained dynamics
- `tone.fenv_levels`: shape the TVF envelope like the TVA envelope so brightness follows loudness

### Flutes (and other edge-blown pipes) get brighter, not louder
*id `dynamics.flute_pressure_is_brightness` · Synth Secrets SS53, SS54*

Blowing harder into a flute mainly adds upper harmonics; the loudness barely changes. Flute 'vibrato' is a 5-6 Hz brightness (blowing-pressure) modulation of about +-10 %, not a pitch vibrato and not a tremolo.

- `tone.lfo_depth_tvf`: flute vibrato goes on the filter
- `tone.lfo_depth_pitch`: keep 0 for flute/recorder
- `matrix.destination`: pressure (AFTERTOUCH/CC01) to CUTOFF, not LEVEL

### In brass, the higher harmonics arrive later than the lower ones
*id `attack.high_harmonics_speak_later` · Synth Secrets SS25, SS26, SS27*

When a brass note starts, the low harmonics reach full level quickly and the upper harmonics build up over roughly half a second. The ear uses this difference in onset as a main clue to the instrument's identity. Synthesis: make the filter attack clearly slower than the amplitude attack (e.g. amp attack about 100 ms, filter attack about 600 ms), with a brief initial overblown 'parp'.

- `tone.fenv_times`: TVF T1 several times longer than TVA T1
- `tone.aenv_times`: TVA T1 short-moderate (not 0) for brass

### Struck and plucked sounds get darker as they decay
*id `decay.highs_die_first` · Synth Secrets SS14, SS20, SS28, SS30, SS32, SS42*

After a pluck or strike, the high partials decay fastest; the tail is dominated by the fundamental (bells and cymbals are exceptions with their own patterns). Make the filter decay faster than the amplitude decay, and make both faster for higher notes.

- `tone.fenv_times`: TVF T2/T3 shorter than the TVA's
- `tone.fenv_time_kf`: positive: shorter at higher notes
- `tone.aenv_time_kf`: positive: high notes ring shorter (piano, guitar)

### The first milliseconds identify the instrument
*id `attack.first_milliseconds_identify` · Synth Secrets SS07, SS19, SS25, SS42, SS52, SS55*

Listeners identify an instrument mostly from its attack transient: a flute's chiff, a hammer's clunk, a brass 'parp', a beater click, an organ's key-click. A convincing attack plus a simple sustain (Roland's LA synthesis idea) goes a long way. When a PCM wave already contains the real attack, don't reshape it with the envelope; layer extra transients instead.

- `wave.oneshot_loop`: keep acoustic PCM attacks intact; shape only the decay
- `tmt.tone_switch`: add a short attack layer (e.g. wave 229 Digi Breath, 248 Key On Click, 247 JD EP Atk, 249-253 Org Click) on another tone
- `tone.delay_time`: stagger layers: a tonal body entering just after a noise chiff

### Brightness tracks pitch, but usually by less than 1:1
*id `keyboard.tracking_less_than_one` · Synth Secrets SS24, SS26, SS29, SS42, SS44, SS47, SS54*

Higher notes are usually brighter, but real instruments have a limited bandwidth, so high notes carry relatively fewer harmonics: brass and flute filters should track at somewhat less than 100 %, and strings/pads at around 30-65 %. Where a fixed spectral ceiling exists (the flute's ~2 kHz), track only a few percent. High notes also decay faster.

- `tone.cutoff_kf`: +50...+80 brass; +30...+65 strings/pads; +5...+15 flute; +100 when the cutoff must follow the pitch exactly (self-oscillating/tuned noise)

### Lushness comes from several slightly different pitches moving at unrelated rates
*id `lushness.detune_and_unrelated_modulation` · Synth Secrets SS10, SS21, SS46, SS47, SS62*

Thickness comes from multiple near-identical sources beating against each other. Keep the detune small (large detune sounds off-colour/honky-tonk), and modulate the sources differently: one layer vibrato'd, rates that differ from the beat rate, two LFOs at unrelated rates (e.g. ~0.5-1 Hz and ~6 Hz), a touch of randomness. PWM is itself two pitches moving against each other, and it can be imitated with two saws, one of them slightly pitch-modulated. Then a good chorus/ensemble adds the final sheen.

- `tone.fine_tune`: +-3...+-10 cents between otherwise identical tones
- `tone.lfo_depth_pitch`: tiny depth on ONE of two saw tones = the PWM sound
- `tone.lfo_rate`: use different rates per tone
- `tone.lfo_rate_detune`: per-note rate variation
- `chorus.type`: CHORUS for sheen
- `mfx:26` (HEXA-CHORUS): HEXA-CHORUS for multi-phase ensemble
- `mfx:28` (SPACE-D): SPACE-D (Dimension-style) ensemble

### Layer similar-but-not-identical sounds
*id `layering.similar_not_identical` · Synth Secrets SS45, SS47, SS25*

Two related patches (slightly different waves, envelopes, filter settings and modulation) layered at equal level with a small detune sound richer, more vibrant and more real than either alone. One can supply the attack, the other the body; the one with the longer decay takes over in the tail. Layering two different instruments just sounds like two instruments; layering two identical ones just sounds chorused.

- `tmt.structure_12`: TYPE 01 keeps tones independent for layering
- `tone.level`: equal levels for the layered pair
- `tone.aenv_times`: give one layer a shorter, attack-focused envelope and the other the long body

### Each instrument has its own kind of natural modulation
*id `modulation.right_kind_per_instrument` · Synth Secrets SS10, SS25, SS49, SS53, SS54, SS57, SS40, SS62*

- Violin/viola/cello: finger vibrato of 5-8 Hz, fairly deep (up to a quarter tone), delayed, with a little tremolo from the body.
- Brass: small, delayed ~5 Hz vibrato; filter 'growl' only at the attack.
- Flute: brightness modulation (~5-6 Hz), no pitch vibrato.
- Recorder: tiny random brightness wander, no vibrato.
- Hammond: scanner chorus/vibrato at ~6-7 Hz (C-3 chorus is the favourite) and the Leslie.
- Bells: warble (beating between near-identical modes).
- Ensembles: several unrelated slow and fast modulations.
Regular, identical LFO modulation on every note sounds mechanical.

- `tone.lfo_depth_pitch`: violin: moderate; brass: small; flute/recorder: 0
- `tone.lfo_depth_tvf`: flute and brass growl
- `tone.lfo_depth_tva`: small companion tremolo for violin/brass
- `tone.lfo_fade_mode`: ON-IN delayed modulation for violin, brass, voice

### Vibrato belongs after the attack
*id `modulation.delayed_vibrato` · Synth Secrets SS08, SS25, SS49, SS50*

Players add vibrato after a note has started, and they vary it. Delayed vibrato (the LFO depth fading in after the note starts) is far more natural than vibrato that is present from the very first moment.

- `tone.lfo_fade_mode`: ON-IN
- `tone.lfo_delay`: about 30-60
- `tone.lfo_fade_time`: about 30-70
- `lfo.fade_modes`: see the four fade modes

### Hand control makes sounds human
*id `performance.controllers_over_envelopes` · Synth Secrets SS50, SS51, SS52, SS54, SS63*

Envelopes and LFOs make every note identical, which is their strength and their weakness. The most realistic violin, brass and flute results come from putting loudness, brightness, vibrato depth and pitch on the player's hands (joystick, pressure, ribbon), even in very simple patches. On a keytar, map the ribbon, mod bar, aftertouch knob and D-Beam to musically meaningful destinations.

- `matrix.source`: AFTERTOUCH (knob), CC01 (mod bar), a D-Beam CC
- `matrix.destination`: LEVEL + CUTOFF for swell/bow/breath; LFO1 PCH DEPTH for vibrato; FXM DEPTH, RESONANCE, TVA ENV times for expression
- `common.bend`: ribbon bend range: 2 for most, 12+ for slides
- `performance.controllers`: the AX-Synth's physical controllers

### Drums are noise + a falling sine; metal is ring-mod/FM pairs
*id `percussion.inharmonic_recipes` · Synth Secrets SS02, SS11, SS31, SS32, SS33, SS34, SS35, SS36, SS37, SS38, SS39, SS40, SS41*

- Membranes (drums) have inharmonic, quickly decaying partials. Synthesise them as filtered noise plus one or two sines with a short downward pitch sweep (the pitch drops as the tension falls).
- Snares: velocity moves the balance from tonal to noisy.
- Cymbals/hi-hats: dense, flat, inharmonic fog. Several pairs of ring-modulated/FM'd square waves at unrelated pitches work best (noise is a weaker substitute), with band-split envelopes.
- Tuned metal (bells): stretched partials, a fast clangy strike, a strike note, and a long sub-octave hum that beats.

- `structure.ring_modulator`: Structure TYPE 05-10 for metallic partials
- `tone.fxm_color`: low values = more metallic
- `tone.penv_depth`: downward pitch sweep for drum bodies
- `wave:232` (White Noise): White Noise for snares/hats; wave:233 Pink Noise for softer noise

### Instrument bodies and vowels are fixed resonances that don't follow pitch
*id `body.fixed_formants` · Synth Secrets SS06, SS22, SS23, SS48, SS49, SS50*

Body resonances (violin: a few hundred Hz plus 2-5 kHz; guitar and piano soundboards) and vowel formants stay at fixed frequencies whatever note is played. That's why an instrument family sounds consistent across its range. Emulate them with fixed EQ/band-pass peaks (no key tracking), not with a pitch-tracking filter. Static linear filtering after the voices (in the MFX) is equivalent to filtering each voice.

- `mfx:1` (EQUALIZER): EQUALIZER: parametric peaks for body resonances
- `mfx:9` (HUMANIZER): HUMANIZER: vowel formants
- `tone.cutoff_kf`: 0 on BPF/PKG tones used as fixed formants
- `tone.filter_type`: BPF or PKG at a fixed cutoff

### Resonance reads as 'synth'
*id `filter.resonance_sounds_electronic` · Synth Secrets SS06, SS26, SS50, SS54*

A resonant peak sweeping through the spectrum is the signature analogue synth sound (squelch, wow, zap), and it's great for synth leads, basses and effects. For acoustic imitations (violin, brass, flute) resonance above a slight touch makes the result sound electronic. Keep it at 0 to about 20 % there, unless it's used deliberately as a fixed body peak.

- `tone.resonance`: 0-20 for acoustic imitations; 40-100 for synth squelch
- `common.offset_resonance`: patch-wide resonance trim

### Envelope archetypes
*id `envelope.archetypes` · Synth Secrets SS03, SS07, SS08, SS25, SS26, SS42, SS46, SS50, SS54, SS63*

- Organ: rectangular (instant attack, full sustain, instant release).
- Brass: moderate attack, slight overshoot/decay to a high sustain, short release. Swell/spit brass: a spike, a dip, a slow swell.
- Bowed strings: a gentle bow attack (slight bump), full sustain, a moderate release.
- Plucked/struck: instant attack, decay to silence, no sustain (a two-slope decay for guitars and pianos).
- Pads/string machines: a trapezoid (slow attack, full sustain, long release).
- Drums: instant attack, short decay.
- Flute: not instant but not slow; the release is just long enough to avoid 'sucking' between legato notes.

- `tone.aenv_times`: T1 attack, T2/T3 decay, T4 release
- `tone.aenv_levels`: L1 peak, L2 break point, L3 sustain
- `editing.summary_adsr`: Editor A/D/S/R = T1/T3/L3/T4
- `tone.env_mode`: NO-SUS for plucked/struck sounds on looped waves

### Choose retriggering to suit the phrasing
*id `trigger.legato_choice` · Synth Secrets SS07, SS18, SS19, SS27, SS52*

- Re-articulating every note (multi-trigger) keeps fast lines punchy and gives every note its chiff/attack (pan pipes).
- Single-trigger/legato slurs overlapped notes at the sustain level, which is natural for flute, brass valve changes and bowed legato.
- Envelopes that reset to zero on every note sound choppy.
- Mono sounds whose sustain is 0 can go silent when notes overlap.

- `common.mono_poly`: MONO for solo lines
- `common.legato_sw`: ON for slurs
- `common.legato_retrigger`: OFF = slur without re-attack (wind/strings); ON = re-attack
- `common.portamento_mode`: LEGATO = glide only when overlapping

### Give level, brightness and modulation their own velocity curves
*id `velocity.curves_per_destination` · Synth Secrets SS44, SS42, SS46, SS56*

Expressive patches respond to velocity differently per destination: for example, loudness strongly, brightness moderately, vibrato depth slightly. Pianos need soft notes that are still audible (don't use a curve that goes to silence). String machines, organs and some pads should ignore velocity entirely.

- `tone.tva_vel_curve`: FIX = no velocity response (organs, string machines)
- `tone.cutoff_vel_curve`: separate curve for brightness
- `tone.tva_vel_sens`: moderate for pianos so soft notes stay audible

### Space is part of acoustic sounds
*id `space.reverb_essential_for_acoustic` · Synth Secrets SS22, SS54, SS57, SS61*

Acoustic instruments are heard in rooms: flutes radiate from many holes with complex phase, which a reverberant room smooths; strings and brass need a hall. A dry synthesized flute or violin sounds wrong. Use a hall-type reverb for orchestral imitations, and keep the reverb low on kicks and bass.

- `reverb.type`: SRV HALL for orchestral; SRV ROOM for drums/small; SRV PLATE for bright dense sheen
- `tone.reverb_send_mfx`: per-tone reverb amount

### Chorus fattens, but not everything should be fat
*id `chorus.not_for_every_sound` · Synth Secrets SS26, SS44, SS57, SS62*

Chorus/ensemble makes bland waveforms lush (string machines, pads, EPs) and stereo chorus is the classic synth effect. It is inappropriate for acoustic piano imitations and single solo acoustic instruments (a solo trumpet isn't a section), and multi-stage ensemble chorus is too lush for a Hammond's scanner chorus.

- `chorus.level`: 0 for acoustic piano/solo instruments; high for pads and string machines
- `mfx:23` (CHORUS): CHORUS: simple dry + modulated copy (Hammond C-type)

### Some sounds need samples
*id `limits.use_pcm_for_guitars_pianos` · Synth Secrets SS28, SS29, SS30, SS39, SS42, SS43, SS44, SS45*

Acoustic guitars, acoustic pianos and cymbals are beyond practical subtractive synthesis: coupled strings and bodies, stretched partials, sympathetic resonance and hammer/pick physics. Synth versions end up electric-piano-like or 'synth-guitar' (convincing only under heavy distortion). Use sampled/PCM sources for these and shape them lightly.

- `wave:254` (AX Grand mpL): AX Grand mp L (with 255 R, 256/257 ff)
- `wave:52` (Ac.Gtr mp): Ac.Gtr mp (53 mf, 54 ff); 49-51 nylon
- `mfx:39` (GUITAR AMP SIMULATOR): GUITAR AMP SIMULATOR for electric guitar realism

### Analyse the target, then choose sources, modifiers and controllers
*id `method.analyse_dont_twiddle` · Synth Secrets SS07, SS63*

To design a sound, work out: the source (which waveform or noise), the modifiers (which filters and effects, and where), and the controllers (envelopes, LFOs, the player's hands). Then set them deliberately. Also describe the target's brightness contour and loudness contour. Random twiddling produces clichés. There is no 'Big Red Button'.

- `editing.tips`: Roland's tip: start from the closest patch

### Precise tuning for organs, tiny randomness for humans
*id `tuning.precision_vs_human` · Synth Secrets SS16, SS21, SS49, SS53, SS56*

Organ emulations need exact tuning and stable filters; slightly mistuned voices sound 'just wrong', not warm. Imitations of human players (strings, winds, voices) benefit from tiny random pitch/brightness wander, random voice-to-voice differences, and pitch 'hunting' at note starts. Too much sounds broken.

- `common.analog_feel`: 0 for organ; 10-40 for human/analogue feel
- `tone.random_pitch`: 0 for organ; 2-10 cents for strings/voices
- `tone.lfo_waveform`: RND at low depth for random wander

### Very fast attacks and releases click
*id `clicks.fast_edges` · Synth Secrets SS27, SS34, SS55*

A zero attack or release produces an audible click. That's desirable as a drum beater click or organ key-click, but it's undesirable on smooth sounds. Use a small non-zero release (and attack) to avoid clicks on sine/sub-heavy tones.

- `tone.aenv_times`: T4 about 3-5 rather than 0 on smooth sounds; T1 0 for deliberate clicks

### The ear supplies missing fundamentals
*id `pitch.implied_fundamental` · Synth Secrets SS33, SS40, SS42*

If partials lie in a harmonic pattern (e.g. 2:3:4), the ear hears the implied fundamental even when it's absent: the organ builders' 32' trick, the strike note of bells, the lowest piano notes. A weak or missing fundamental can still sound deep if the upper partials are correctly spaced.

- `tone.coarse_tune`: layer partials at +12/+19/+24 to imply a lower pitch

### Effects are part of the synthesis
*id `effects.are_sound_design` · Synth Secrets SS04, SS58, SS59, SS61, SS62*

Effects shape the sound as much as the voice does: the Leslie *is* the Hammond sound, amp simulation is the electric guitar, and chorus is what makes string machines lush. Program effects deliberately (order, delay times, feedback, modulation), not just as presets. Delays: 10-50 ms modulated = chorus; shorter = flanging/comb; longer = echo; cascaded with feedback = reverb (metallic if the delay times are fixed).

- `fx.routing`: one MFX per patch, then chorus and reverb sends
- `mfx:24` (FLANGER): FLANGER for short comb sweeps
- `mfx:43` (DELAY): DELAY for echoes; 55 TAPE ECHO / 53 ANALOG DELAY for degrading repeats

## Descriptors

| Descriptor | Words | Acoustic cause | AX-Synth moves [I] |
|---|---|---|---|
| **bright** (opposite: dark) | bright, brilliant, crisp, cutting, present, sharp, trebly | Strong upper harmonics. Comes from a harmonically rich wave (saw, narrow pulse), a high cutoff, a positive filter envelope, or strong playing. | `tone.cutoff` raise; `common.offset_cutoff` raise (patch-wide brightness macro, 64 = no change); `tone.wave_number` choose a saw or narrow pulse; `tone.fenv_depth` raise the positive amount; `mfx:7` ENHANCER adds presence |
| **dark** (opposite: bright) | dark, dull, muffled, mellow, soft-toned, rounded, warm | Few upper harmonics. The ear hears even a gentle high-frequency roll-off as dullness; 'warm' usually means rolled-off highs with a full low-mid. | `tone.cutoff` lower; `tone.filter_type` LPF (LPF2 for a gentler, natural roll-off); `common.offset_cutoff` lower; `tone.wave_number` triangle/sine/soft waves (213-216, 220) |
| **hollow** | hollow, woody, clarinet-like, square, boxy | Odd harmonics only (square wave, closed pipe): the clarinet or pan-pipe character. | `wave:196` Fat Square (or 197/198); `tone.filter_type` LPF moderately closed to mellow it |
| **nasal** | nasal, reedy, thin, oboe-like, pinched, honky | A narrow pulse (5-15 %), a band-pass focus, or a formant peak in the upper mids. | `wave:204` JP8 Pls 10HD (or 205 15 %); `tone.filter_type` BPF for a focused, telephone-like nasality; `mfx:59` TELEPHONE for an extreme band-limited effect |
| **thin** (opposite: fat) | thin, weedy, small, lightweight, tinny | Lacking low harmonics/body: a high-pass filter, narrow pulses, or a single un-layered source. | `tone.filter_type` HPF removes body (for layering a bright top, or hats); `tone.coarse_tune` to fix thinness, add a -12 layer instead |
| **fat** (opposite: thin) | fat, thick, full, big, huge, wide-bodied, beefy | Several detuned sources, a sub-octave layer, rich waves, unison stacking; the classic 'unison' mono lead or the Minimoog bass. | `tone.fine_tune` detune a second/third layer by 5-15 cents; `tone.coarse_tune` add a -12 (sub-octave) layer; SH101 tuba trick: saw + square an octave down; `wave:122` Super Saw (121 Unison Saw, 123 Trance Saw); `common.mono_poly` MONO + layers = unison-style lead |
| **buzzy** | buzzy, raspy, edgy, saw-like, brassy, brash | A sawtooth-rich spectrum with little filtering. Brass is 'brash' because its conical bore gives the full harmonic series. | `tone.wave_number` a saw (e.g. 185 JP-8 Saw, 177 MG Saw HD); `tone.cutoff` fairly open |
| **soft_attack** (opposite: punchy) | soft attack, slow attack, swelling, fade in, bowed, gentle start, pad-like | A gradual amplitude (and brightness) rise: bowed strings, pads, swells. | `tone.aenv_times` raise T1 (20-40 bowed; 40-80 pad swell); `common.offset_attack` raise (patch-wide attack macro); `tone.fenv_times` raise TVF T1 so the brightness swells too |
| **punchy** (opposite: soft_attack) | punchy, snappy, percussive, tight, attacky, hard-hitting | An instant attack with a strong initial transient, often a brightness spike that settles quickly; re-triggered on every note. | `tone.aenv_times` T1 0, a short T2 to a lower L2/L3; `tone.fenv_depth` positive with a fast decay (a brightness spike); `common.legato_sw` OFF (re-attack every note); `mfx:40` COMPRESSOR for punch |
| **plucked** | plucked, plucky, pizzicato, picked, harp-like, stabby | An instant attack, decay to silence, highs dying first; brightness follows loudness. | `tone.aenv_levels` L3 = 0 (no sustain); `tone.env_mode` NO-SUS on loop waves; `tone.fenv_times` TVF decay faster than the TVA; `tone.aenv_time_kf` positive: shorter at high notes |
| **sustained** | sustained, held, organ-like, constant, drone | Full sustain while held; a rectangular organ envelope; no decay. | `tone.aenv_levels` L1-L3 127; `tone.aenv_times` T1 0, T4 0-5; `tone.env_mode` SUSTAIN |
| **long_tail** | long release, long tail, ringing, lingering, decaying slowly, ambient | A slow release or decay, often plus reverb. | `tone.aenv_times` raise T4 (release) or T3 (decay); `common.offset_release` raise (patch-wide release macro); `reverb.level` raise |
| **short** | short, staccato, clipped, dry, choppy | A short decay/release; little reverb. | `tone.aenv_times` short T3 and T4; `common.offset_release` lower; `reverb.level` lower |
| **breathy** | breathy, airy, windy, flute-like, whispery, husky | Turbulence noise coloured by the instrument: pitched, high-frequency breath noise tracking the note, plus a chiff at the start. | `wave:229` Digi Breath (228 Shaku Noise, 226 JD Vox Noise) on an extra tone; `tone.filter_type` BPF on the noise tone with cutoff_kf +100 = pitched breath; `tone.level` keep the breath layer low for orchestral winds; higher for pan pipes |
| **metallic** | metallic, clangy, clangorous, tinny-metal, industrial, robotic | Inharmonic partials from ring modulation, FM at odd ratios, or metal PCM; a fixed-frequency ring-mod carrier changes timbre across the keyboard. | `structure.ring_modulator` Structure TYPE 05-10 with a non-integer interval between the tones; `tone.fxm_sw` FXM on; low FXM COLOR = more metallic; `mfx:15` RING MODULATOR (16 STEP RING MODULATOR); `wave:239` Metal Vox 1 (240, 241), 223 JD MetalWind |
| **bell_like** | bell, bell-like, chime, glassy, crystalline, tinkly, glockenspiel | Quasi-harmonic, slightly stretched partials; an instant attack, long ringing decay, sometimes a beating warble and a sub-octave hum. | `wave:148` D-50 Bell (154 Tubular, 155 Church, 157 JD Crystal, 146 Glocken); `tone.fxm_depth` moderate FXM on a sine for DX-style bells; `tone.fine_tune` a second layer a few cents off for warble |
| **distorted** | distorted, gritty, dirty, overdriven, fuzzy, crunchy, aggressive, saturated | Clipping adds harmonics and compression; soft clipping is warm, hard clipping harsh. Synth 'guitars' only convince under heavy distortion. | `mfx:35` OVERDRIVE (36 DISTORTION, 37/38 VS versions, 39 GUITAR AMP SIMULATOR); `structure.booster` Booster (Structure TYPE 03/04) + WAVE GAIN +12 for per-voice drive; `tone.wave_gain` +12 with the booster |
| **lush** | lush, chorused, ensemble, rich, shimmering, swirling, dreamy | Multiple slightly different pitches moving at unrelated rates, plus chorus/ensemble. | `tone.fine_tune` a detuned layer; `chorus.type` CHORUS, level up; `mfx:26` HEXA-CHORUS / 28 SPACE-D; `tone.lfo_depth_pitch` tiny pitch LFO on one saw layer (PWM sound) |
| **wide** | wide, stereo, spacious, panoramic, enveloping | Different signals in left and right: stereo chorus (without the dry signal), panned layers, stereo PCM pairs, ping-pong delays. | `tone.pan` spread layers left/right; `tone.alt_pan` alternate pan per note; `tone.random_pan` random pan per note; `mfx:29` 3D CHORUS / 52 3D DELAY; `wave.stereo` use L/R stereo wave pairs |
| **evolving** (opposite: static) | evolving, moving, animated, alive, shifting, morphing | The timbre changes over the note: slow filter envelopes/LFOs, layers with different envelopes crossfading, spectral swells. | `tone.lfo_depth_tvf` slow LFO (about 0.1 Hz) on cutoff; `tone.aenv_times` one layer fading in slowly while another decays; `tone.step_type` STEP LFO patterns for rhythmic evolution |
| **static** (opposite: evolving) | static, sterile, lifeless, cheap, flat, boring | No change over time. Fix with movement (see 'evolving') or player control. | `common.analog_feel` raise slightly; `tone.fenv_depth` add a filter contour |
| **vibrato** | vibrato, wavering pitch, singing, expressive pitch | Periodic pitch modulation, about 5-8 Hz for human players, usually delayed and player-controlled. | `tone.lfo_depth_pitch` set depth; `tone.lfo_rate` about 5-7 Hz feel; `tone.lfo_fade_mode` ON-IN for delayed vibrato; `matrix.destination` CC01/AFTERTOUCH to LFO1 PCH DEPTH |
| **tremolo** | tremolo, pulsing, throbbing, amplitude wobble | Periodic loudness modulation (not pitch). | `tone.lfo_depth_tva` set depth; `mfx:17` TREMOLO (27 TREMOLO CHORUS, 20 SLICER for rhythmic chopping) |
| **wah** | wah, wah-wah, talking, quacky, funky filter | A resonant band-pass/peaking filter swept at about 1-2 Hz, by an envelope, or by a controller. | `tone.filter_type` PKG or BPF; `tone.lfo_depth_tvf` at about 1-2 Hz; `mfx:8` AUTO WAH; `mfx:9` HUMANIZER for vowel 'talking' |
| **growl** | growl, rasp, snarl, flutter | Fast (about 10-20 Hz, ideally audio-rate) modulation of the filter. On brass it belongs at the note start only, or it can be brought in by overblowing (aftertouch). | `tone.lfo_depth_tvf` fast LFO rate; `tone.lfo_fade_mode` ON-OUT so it fades after the attack; `matrix.destination` AFTERTOUCH to LFO TVF DEPTH for expressive growl |
| **squelchy** | squelchy, resonant, acid, zappy, wet filter, rubbery | High resonance with the cutoff swept by an envelope or LFO: the defining analogue-synth sound. | `tone.resonance` raise (60-110); `tone.fenv_depth` a large positive amount, fast decay; `tone.cutoff` lower base cutoff |
| **vocal** | vocal, voice-like, formant, vowel, choir, ooh, aah | Fixed formant peaks (vowels) on a rich source; the second formant moves most in speech. | `wave:234` Aah Formant (235 Eeh, 236 Iih, 237 Ooh, 238 Uuh); choirs 131-137; `mfx:9` HUMANIZER vowel filter; `tone.filter_type` BPF/PKG at fixed formant frequencies (cutoff_kf 0) |
| **spacious** | spacious, reverberant, roomy, hall, cathedral, ambient | Early reflections + a dense reverberant tail; the size sets the length. | `reverb.type` SRV HALL (large), SRV ROOM (small), SRV PLATE (bright); `reverb.level` raise |
| **echo** | echo, delay, repeats, slapback, ping-pong, dub | Discrete repeats; feedback sets how many; analogue/tape repeats degrade and darken. | `mfx:43` DELAY (55 TAPE ECHO, 53 ANALOG DELAY, 47/48 TAP PAN DELAY for ping-pong); `chorus.type` DELAY (send delay) |
| **lofi** | lo-fi, retro digital, crunchy digital, bit-crushed, old sampler, radio, vinyl | Reduced bandwidth, bit/sample-rate reduction, noise. | `mfx:56` LOFI NOISE (57 LOFI COMPRESS, 58 LOFI RADIO, 60 PHONOGRAPH); `wave:231` Vinyl Noise layer |
| **clicky** | clicky, key click, percussive click, spitty | A very short broadband transient at note-on (organ key-click, beater click). | `wave:249` Org Click 1 (250-253), 248 Key On Click, as a short extra tone; `tone.fenv_depth` a very fast positive TVF blip |
| **human** | human, organic, natural, analogue, unstable, imperfect, warm (analogue) | Small random variations: pitch wander, voice-to-voice differences, irregular modulation, pitch hunting at note starts. | `common.analog_feel` 10-40; `tone.random_pitch` 2-10 cents; `tone.lfo_rate_detune` raise slightly; `tone.lfo_waveform` RND/VSIN at a low depth |
| **scifi** | sci-fi, zap, laser, ray gun, bleepy, computer, space | Fast pitch sweeps (SynDrum zap), random S&H bleeps, FM/ring-mod sweeps, a self-oscillating resonance. | `tone.penv_depth` large pitch envelope sweep; `tone.lfo_waveform` S&H on pitch for random bleeps; `matrix.destination` TVF ENV to FXM DEPTH for FM sweeps |
| **deep** | deep, boomy, subby, low, heavy, weighty | Strong low fundamentals: sub-octave layers, sine/triangle bodies, a slow pitch drop on drums. | `tone.coarse_tune` a -12 or -24 layer; `wave:220` Sine or 214 triangle for sub layers; `mfx:4` LOW BOOST |
| **glide** | glide, portamento, slide, swoop, legato slide | A continuous pitch transition between notes: a slew on the pitch. | `common.portamento_sw` ON; `common.portamento_time` tiny (5-15) for string/voice realism; larger for synth swoops; `common.portamento_mode` LEGATO to glide only on overlapping notes |
| **sync_lead** | sync, tearing, hard sync, screaming lead, zeeow | Hard-sync timbre sweeps: the slave oscillator's pitch swept by an envelope changes the timbre, not the pitch. | `wave:219` Sync Sweep PCM (no oscillator sync on the AX-Synth); `matrix.destination` TVF ENV to FXM DEPTH for a timbre-sweep alternative |
| **expressive** | expressive, playable, dynamic, responsive, touch-sensitive | Velocity curves per destination, pressure/aftertouch control, bend and vibrato under the player's hands. | `tone.tva_vel_sens` moderate; `tone.cutoff_vel_sens` positive; `matrix.source` AFTERTOUCH/CC01 to LEVEL, CUTOFF, LFO depth |

## Recipes

### Analogue synth brass (Prophet/OB/Minimoog style)
*id `brass.synth` · family Brass/Poly Synth · Synth Secrets SS24, SS25, SS26, SS27*

Brass has the full harmonic series, so use a sawtooth. The key cue is a filter that opens more slowly than the amplitude (the higher harmonics speak later), a brief overblown 'parp', a high sustain and a short release. Harder = brighter. Avoid instant attacks, heavy resonance, and square/pulse waves.

Start from factory Tones: Analog Brass, Juno Brass, Poly Brass, 106 Brass, 80s Brass 1, Brite SynBrs, Soft SynBrs
Waves: 185 JP-8 Saw, 177 MG Saw HD, 174 Juno Saw HD, 179 P5 Saw HD

**Steps**

- `tone.wave_number`: saw (185 JP-8 Saw / 177 MG Saw HD) (*full harmonic series = brass*)
- `tone.filter_type`: LPF
- `tone.cutoff`: 25-45 (fairly closed) (*the envelope opens it*)
- `tone.resonance`: 10-25 (*a slight bump only; more sounds electronic*)
- `tone.fenv_depth`: +35...+55
- `tone.fenv_times`: T1 40-65, T2 30-60, T3 40-70, T4 5-15 (*filter attack slower than amp attack*)
- `tone.fenv_levels`: L0 0, L1 127, L2 100, L3 60-80, L4 0 (*parp, then settle*)
- `tone.aenv_times`: T1 10-25, T2 20, T3 30, T4 5-15 (*about a 100 ms attack, quick release*)
- `tone.aenv_levels`: L1 127, L2 115, L3 100-115
- `tone.aenv_t1_sens`: +20...+40 (*harder = faster attack*)
- `tone.cutoff_kf`: +60...+90 (*slightly under 1:1 tracking*)
- `tone.fenv_vel_sens`: +20...+40 (*harder = brighter*)
- `tone.res_vel_sens`: +10 (*louder = more upper-harmonic emphasis*)
- `tone.fine_tune`: tone 2 same wave +5...+8 cents (*a section/fat variant; single tone for solo*)

**Performance**

- `matrix.source`: AFTERTOUCH -> CUTOFF + (*sustained brightness swell*)
- `matrix.destination`: CC01 -> LFO1 PCH DEPTH (*mod-bar vibrato*)
- `tone.lfo_fade_mode`: ON-IN, delay 40, fade 50, rate ~5 Hz, pitch depth small (*delayed vibrato*)

**Effects**

- `chorus.type`: CHORUS, moderate (*ensemble brass*)
- `reverb.type`: SRV HALL

**Pitfalls**

- Instant attack or high resonance kills the brass illusion.
- A square/pulse wave sounds like a clarinet, not brass.
- The filter opening at the same speed as the amp sounds like a generic synth.

### Realistic trumpet / flugelhorn
*id `brass.trumpet_realistic` · family Brass/Poly Synth · Synth Secrets SS24, SS25, SS26*

Start from trumpet PCM (velocity layers p/mf/ff) and add what samples lack: brighter-when-louder dynamics, delayed small vibrato, brief growl at the attack, faint breath, mono legato, and a hall. Trumpet sits an octave above the keyboard's 8' feel.

Start from factory Tones: Trumpeter, Trumpet, AX BrassSect, Soft Brass
Waves: 114 Trumpet 1, 297 Trumpet 2 p, 298 Trumpet 2 mf, 299 Trumpet 2 ff, 300 Trumpet 3, 113 Flugel, 115 Tp Section

**Steps**

- `tmt.velocity`: tone 1 wave 297 (p) vel 1-70, tone 2 wave 298 (mf) vel 60-110, tone 3 wave 299 (ff) vel 100-127, with fades (*velocity-switched timbre = dynamic brightness*)
- `tone.filter_type`: LPF2 (*natural roll-off*)
- `tone.cutoff_vel_sens`: +20
- `tone.aenv_times`: keep T1 0 (sample attack), T4 5-15 (*don't overwrite the PCM attack*)
- `tone.lfo_fade_mode`: ON-IN delay 40-60 (*delayed vibrato*)
- `tone.lfo_depth_pitch`: small (2-5) (*subtle ~5 Hz vibrato*)

**Performance**

- `common.mono_poly`: MONO (*solo line*)
- `common.legato_retrigger`: OFF (*valve legato (Editor manual recommends OFF for wind phrases)*)
- `common.bend`: up 2 / down 2 (*lip bends and falls*)
- `matrix.source`: AFTERTOUCH -> CUTOFF and LFO1 TVF DEPTH (*overblown brightness/growl*)

**Effects**

- `reverb.type`: SRV HALL
- `chorus.level`: 0 (*a solo trumpet isn't a section*)

**Pitfalls**

- Vibrato from the first instant sounds synthetic.
- Too much pitch vibrato depth sounds electronic.

### Spit / swell brass (sforzando)
*id `brass.spit_swell` · family Brass/Poly Synth · Synth Secrets SS08, SS25, SS63*

Silence, then a fast 'psst' spike, a drop to a much lower and duller level, a slow swell to full volume and brightness, then a quick release. It needs multi-level envelopes, which the AX-Synth TVA/TVF envelopes provide.

Start from factory Tones: Brite SynBrs, Wide SynBrs, Octa Brass, Alpha Spit
Waves: 185 JP-8 Saw, 177 MG Saw HD, 118 XP Brass

**Steps**

- `tone.aenv_times`: T1 0-5, T2 10-20, T3 60-90, T4 10-25 (*spike, dip, swell*)
- `tone.aenv_levels`: L1 110-127, L2 50-70, L3 127 (*L1 is not the max of the swell; L2 is the dip*)
- `tone.fenv_levels`: same shape as TVA (L1 high, L2 low, L3 high) (*brightness follows loudness*)
- `tone.fenv_depth`: +40

**Performance**

- `common.offset_attack`: use as a swell-speed macro

**Effects**

- `reverb.type`: SRV HALL

**Pitfalls**

- A plain ADSR can't make this shape; use L1/L2/L3.

### Tuba / low brass
*id `brass.tuba_low` · family Brass/Poly Synth · Synth Secrets SS26, SS27, SS51*

Low brass is more forgiving. The SH101 trick: saw plus a square an octave down gives body (the saw alone lacks body, the square alone is hollow). A noise-roughened filter (not pitch modulation) adds rasp. Play 1-2 octaves down.

Start from factory Tones: Trombone, Soft Brass, Analog Brass
Waves: 177 MG Saw HD, 196 Fat Square, 185 JP-8 Saw

**Steps**

- `tone.wave_number`: tone 1 177 MG Saw HD; tone 2 196 Fat Square (*the waveform mix defines the timbre*)
- `tone.coarse_tune`: tone 2 -12; whole patch -12 or -24 for tuba
- `tone.level`: tone 1 ~75 %, tone 2 ~100 % (*per the SH101 mixer*)
- `tone.cutoff`: 20-35 + filter env +40
- `tone.lfo_waveform`: RND, fast, small TVF depth, ON-OUT fade (*noise-like rasp at the note start*)

**Performance**

- `matrix.source`: AFTERTOUCH -> CUTOFF (pressure brass, silent until pressed if base cutoff ~0) (*SS51 filter-gated brass*)

**Effects**

- `reverb.type`: SRV HALL

### String machine / ensemble pad (Solina, Omni, Logan)
*id `strings.string_machine` · family Strings/Pad · Synth Secrets SS20, SS46, SS47, SS62*

Two saws, minimal detune, a subtle vibrato on only one of them (or small random modulation), no velocity, a filter about half closed with moderate tracking and no envelope, a trapezoid amp envelope, then chorus/ensemble for the sheen.

Start from factory Tones: Tape Strings, Synth Str 1, Synth Str 2, JX Strings, JP Strings, 106 Strings, Sawtooth Str, OB Strings, Chorus Pad
Waves: 185 JP-8 Saw, 174 Juno Saw HD, 121 Unison Saw, 124 Warm Pad, 125 OB2 Pad 1, 126 OB2 Pad 2

**Steps**

- `tone.wave_number`: tones 1+2 saw (185 or 174)
- `tone.fine_tune`: tone 2 +4...+8 (*small detune = thickening*)
- `tone.lfo_depth_pitch`: tone 1 only, tiny; TRI or RND; rate distinct from the beat (*the detune itself wobbles*)
- `common.analog_feel`: 20-40
- `tone.filter_type`: LPF
- `tone.cutoff`: 60-75 (*half closed*)
- `tone.cutoff_kf`: +30...+50
- `tone.fenv_depth`: 0 (*string machines had no filter sweep*)
- `tone.tva_vel_curve`: FIX (*not velocity-sensitive*)
- `tone.aenv_times`: T1 40-70, T4 50-80 (*trapezoid: crescendo + long tail*)
- `tone.aenv_levels`: L1-L3 127

**Performance**

- `tone.coarse_tune`: optional tone 3 -12 (*weight / cello register*)

**Effects**

- `mfx:28` (SPACE-D): SPACE-D or 26 HEXA-CHORUS (*ensemble sheen*)
- `chorus.type`: CHORUS
- `reverb.type`: SRV HALL

**Pitfalls**

- Large detune sounds honky-tonk.
- Identical regular modulation on both tones = plain vibrato, not ensemble.

### PWM strings / pad without PWM (two saws, one pitch-modulated)
*id `strings.pwm_pad` · family Strings/Pad · Synth Secrets SS10, SS46, SS47, SS62*

The PWM sound equals two sawtooths with one of them slightly frequency-modulated (square or triangle LFO, tiny depth), plus a small static detune, which can be warmer than real PWM. Layer a second, slightly different pair for depth, then add chorus.

Start from factory Tones: AX Strings 1, AX Strings 2, Soft Pad 1, Soft Pad 2, JX Strings, Hollow Pad
Waves: 185 JP-8 Saw, 174 Juno Saw HD, 207 JP8 Pls 30HD

**Steps**

- `tone.wave_number`: tones 1+2 saw 185
- `tone.fine_tune`: tone 2 -4...-10
- `tone.lfo_waveform`: tone 1 SQR (or TRI)
- `tone.lfo_rate`: 70-90 (fairly fast)
- `tone.lfo_depth_pitch`: tone 1 only: 1-3 (*the PWM effect*)
- `tone.cutoff`: 60-75, env +10...+15, medium env attack
- `tone.cutoff_kf`: +40...+60
- `tone.aenv_times`: T1 30-50, T4 50-65 (*fast-but-smooth attack, gentle release*)
- `tone.tva_vel_sens`: 0
- `tone.bias_level`: negative (quieter upwards) (*bass-weighted warmth (Korg T2 trick)*)

**Performance**

- `tmt.structure_34`: tones 3+4: a second pair with a different LFO rate/depth, detune and cutoff; optional -12/+12 (*layer = cello/violin registers*)

**Effects**

- `chorus.type`: CHORUS
- `mfx:26` (HEXA-CHORUS): HEXA-CHORUS
- `reverb.type`: SRV HALL

### Expressive solo violin / cello
*id `strings.solo_violin` · family Strings/Pad · Synth Secrets SS48, SS49, SS50, SS51*

The bowed string drives the bridge with a sawtooth; the body adds resonances (a few hundred Hz plus 2-5 kHz). Use a bowing attack with a slight bump, full sustain, deep delayed 5-8 Hz vibrato with a little tremolo, tiny glide, pitch hunting, and above all hand control of loudness and vibrato.

Start from factory Tones: Violin, Cello, Strings, AX Strings 1
Waves: 185 JP-8 Saw, 177 MG Saw HD, 301 RSS Str L, 302 RSS Str R, 303 US Strings L, 304 US Strings R

**Steps**

- `tone.wave_number`: saw 185/177 (or string PCM 301/303)
- `tone.coarse_tune`: +12 violin (4'), 0/-12 cello
- `tone.filter_type`: LPF, cutoff 85-100, resonance 0 (*resonance sounds electronic here*)
- `tone.cutoff_kf`: +50
- `tone.aenv_times`: T1 20-35, T2 short, T4 20-30 (*bow attack*)
- `tone.aenv_levels`: L1 127, L2/L3 105-115 (*slight bump*)
- `tone.lfo_fade_mode`: ON-IN, delay 30-50, fade 30-60 (*delayed vibrato*)
- `tone.lfo_depth_pitch`: moderate (up to a quarter tone) (*finger vibrato 5-8 Hz*)
- `tone.lfo_depth_tva`: small (*body-induced tremolo*)
- `tone.random_pitch`: 5-10 cents (*pitch hunting*)

**Performance**

- `common.mono_poly`: MONO, legato ON, retrigger OFF
- `common.portamento_time`: 5-15 (just off zero), mode LEGATO (*fingered glide*)
- `matrix.source`: AFTERTOUCH (or CC01 / D-Beam CC) -> LEVEL + and LFO1 PCH DEPTH +; low base tone.level (*the SS50/51 lesson: hand-controlled bowing*)
- `common.bend`: 2 (12 for slides)

**Effects**

- `mfx:1` (EQUALIZER): EQUALIZER: low cut, peaks ~300 Hz and ~700 Hz, broad boost ~3 kHz (*body formants*)
- `reverb.type`: SRV HALL / ROOM

**Pitfalls**

- A percussive envelope turns a violin into a banjo.
- Resonance and a strong HPF make it sound electronic or gutted.

### Pizzicato / plucked strings
*id `strings.pizzicato` · family Strings/Pad · Synth Secrets SS28, SS48*

Pizzicato violin is banjo-like: the saw source with a plucked envelope, the filter decaying faster than the amp, and shorter decays higher up.

Start from factory Tones: Harp, Aerial Harp
Waves: 185 JP-8 Saw, 301 RSS Str L, 63 Harp

**Steps**

- `tone.aenv_times`: T1 0, T3 20-40
- `tone.aenv_levels`: L3 0
- `tone.env_mode`: NO-SUS
- `tone.fenv_depth`: +30, decay faster than TVA (*highs die first*)
- `tone.aenv_time_kf`: +20...+40

**Effects**

- `reverb.type`: SRV HALL

### Orchestral flute
*id `wind.flute` · family Brass/Poly Synth · Synth Secrets SS53, SS54*

The flute spectrum is capped around 2 kHz for every note (HPF at a few hundred Hz, LPF ~2 kHz, tracking only a few %). Pressure changes brightness, not loudness. Vibrato is 5-6 Hz brightness modulation. The amp attack is not instant, sustain is full, and the release is just long enough to avoid 'sucking' in legato. Reid finds added noise detracts. Reverb is essential.

Start from factory Tones: Shakuhachi, Pan Pipes, Air Lead, Soft Lead
Waves: 99 Flute, 102 JD Fl Push, 185 JP-8 Saw

**Steps**

- `tone.wave_number`: 99 Flute (PCM) or saw 185 for synth flute
- `tone.filter_type`: LPF, cutoff ~60-75 (the 2 kHz region; calibrate by ear), resonance 15-30 (*resonance adds edge without sounding electronic*)
- `tone.cutoff_kf`: +5...+15 (*a fixed spectral ceiling*)
- `tone.aenv_times`: T1 10-20, T4 10-20
- `tone.lfo_depth_tvf`: small-moderate, rate ~5-6 Hz (*brightness vibrato*)
- `tone.lfo_depth_pitch`: 0
- `tone.lfo_fade_mode`: ON-IN, short delay (*after the chiff*)
- `tone.cutoff_vel_sens`: +20

**Performance**

- `matrix.source`: AFTERTOUCH -> CUTOFF + and LFO1 TVF DEPTH + (*blowing pressure = brightness*)
- `common.mono_poly`: MONO, legato ON, retrigger OFF

**Effects**

- `mfx:1` (EQUALIZER): EQUALIZER low cut (few hundred Hz) (*the HPF part of the flute spectrum*)
- `reverb.type`: SRV HALL, generous (*the flute radiates from many holes*)

**Pitfalls**

- Pitch vibrato and tremolo sound wrong on flute.
- A velocity-to-level mapping that's too strong: flutes don't get much louder.

### Pan pipes / pan flute
*id `wind.pan_pipes` · family Brass/Poly Synth · Synth Secrets SS52*

A stopped pipe gives odd harmonics only (triangle/square, mellow). Pitched, high-frequency breath noise tracks the note. A noisy chiff starts every note, and the tone swells in just after the chiff. Add small vibrato, filter modulation and inverted tremolo, plus bends, and a generous reverb.

Start from factory Tones: Pan Pipes, Shakuhachi, BagShakuLead
Waves: 100 Pan Flute, 101 Shakuhachi, 214 Syn Triangle, 196 Fat Square, 228 Shaku Noise, 229 Digi Breath, 232 White Noise

**Steps**

- `wave:100` (Pan Flute): Pan Flute PCM as the quick route
- `tone.wave_number`: synth: tone 1 214 triangle (or 196 square), LPF cutoff 50-65, cutoff_kf +50...+70 (*mellow odd-harmonic tone*)
- `tone.delay_time`: tone 1 delay mode NORMAL, small time; TVA T1 15-25 (*the tone swells in after the chiff*)
- `tone.filter_type`: tone 2 noise (232/228) BPF, cutoff_kf +100, resonance high, low sustained level (*pitched breath*)
- `tone.aenv_times`: tone 3 white noise LPF, T1 0, T3 5-10, L3 0 (*the chiff*)
- `tone.lfo_depth_tva`: tone 1 small NEGATIVE while lfo_depth_tvf small positive (*inverted tremolo keeps the loudness steady*)
- `tone.aenv_t1_sens`: + (*velocity-sensitive attack*)

**Performance**

- `common.legato_sw`: OFF (or retrigger ON) (*a chiff on every note*)
- `common.bend`: 2 (*pan pipe players bend a lot*)
- `matrix.source`: CC01 -> LFO1 PCH DEPTH

**Effects**

- `reverb.type`: SRV HALL, generous

**Pitfalls**

- Plain square + independent noise sounds disassociated; the noise must be pitched and move with the note.

### Recorder / penny whistle
*id `wind.recorder` · family Brass/Poly Synth · Synth Secrets SS53*

A dominant fundamental and a weak 2nd harmonic: a ~40 % pulse (woody with some edge) or a quiet triangle. The filter envelope peaks before the amplitude (a bright chiff while the note is still rising), a note-off 'thunk' from a set release, a tiny random brightness wander, no vibrato. Best from middle C up two octaves.

Start from factory Tones: Shakuhachi, Soft Lead, Simple Tri
Waves: 208 JP8 Pls 40HD, 214 Syn Triangle, 99 Flute

**Steps**

- `wave:208` (JP8 Pls 40HD): JP8 Pls 40HD (tone 1), coarse +12
- `tone.cutoff`: 45-60, resonance 10-20, cutoff_kf +65
- `tone.fenv_times`: TVF T1 short (~5) (*brightness peaks first*)
- `tone.aenv_times`: TVA T1 15-20, T4 short-medium (*the amp slower than the filter; release = thunk*)
- `tone.lfo_waveform`: RND, slow, tiny TVF depth; pitch depth 0 (*blowing-pressure inconsistency*)

**Performance**

- `common.mono_poly`: MONO
- `common.bend`: 2 (*pressure-like bends*)

**Effects**

- `reverb.type`: SRV ROOM

**Pitfalls**

- Pitch vibrato sounds wrong on recorder.

### Clarinet-like woodwind
*id `wind.clarinet` · family Brass/Poly Synth · Synth Secrets SS02, SS10, SS24*

A closed cylindrical pipe with a reed gives odd harmonics only: a square wave, 'hollow'. Mellow LPF, a moderate attack, delayed gentle vibrato.

Start from factory Tones: Soft Lead, Round SQR, Soft Squ Ld
Waves: 196 Fat Square, 197 JP-8 Square

**Steps**

- `wave:196` (Fat Square): Fat Square (*odd harmonics = hollow*)
- `tone.cutoff`: 45-65, small positive env
- `tone.aenv_times`: T1 8-15, T4 10-15
- `tone.lfo_fade_mode`: ON-IN, small pitch depth

**Performance**

- `matrix.source`: AFTERTOUCH -> CUTOFF

**Effects**

- `reverb.type`: SRV HALL

### Oboe / reedy double-reed
*id `wind.oboe_reed` · family Brass/Poly Synth · Synth Secrets SS02, SS10*

Thin and nasal: a narrow pulse (5-15 %) or oboe PCM, a moderately open filter, delayed vibrato.

Start from factory Tones: Breathy Sax, Soprano Sax
Waves: 204 JP8 Pls 10HD, 205 JP8 Pls 15HD, 103 Oboe 1 Mezzo, 104 Oboe 1 Forte

**Steps**

- `wave:204` (JP8 Pls 10HD): JP8 Pls 10HD (or oboe PCM 103/104) (*narrow pulse = nasal*)
- `tone.cutoff`: 60-80
- `tone.lfo_fade_mode`: ON-IN, small depth

**Effects**

- `reverb.type`: SRV HALL

### Tonewheel drawbar organ (unadorned)
*id `organ.drawbar` · family Organ/Clavi · Synth Secrets SS14, SS55, SS56*

A Hammond is additive: sine partials at 16' (-12), 5 1/3' (+7), 8' (0), 4' (+12), 2 2/3' (+19), 2' (+24), 1 3/5' (+28), 1 1/3' (+31) and 1' (+36), with drawbar levels. 88 8000 000 = the classic punchy registration. Rectangular envelope, key-click, no velocity, precise tuning.

Start from factory Tones: D-Bars 1, D-Bars 2, D-Bars 3, D-Bars 4, D-Bars 5, VK Organ 1, VK Organ 2, Vintage Org 1
Waves: 220 Sine, 30 JD Full Draw, 258 Full Organ 1, 259 VK Full Org1, 261 VK Jazz Org1, 249 Org Click 1

**Steps**

- `wave:220` (Sine): Sine on up to 4 tones (or organ PCM 30/258-281 for full registrations)
- `tone.coarse_tune`: per drawbar: -12, +7, 0, +12, +19, +24, +28, +31, +36 (*footage to semitones*)
- `tone.fine_tune`: 0 (exact) (*mistuning sounds wrong on organs*)
- `tone.level`: = drawbar levels (8 -> 127)
- `tone.aenv_times`: T1 0, T4 0-3 (*rectangular*)
- `tone.aenv_levels`: L1-L3 127
- `tone.tva_vel_curve`: FIX (*organs aren't velocity-sensitive*)
- `common.analog_feel`: 0

**Performance**

- `tone.fenv_depth`: optional tiny fast blip on one tone (*key-click*)

**Effects**

- `mfx:22` (VK ROTARY): VK ROTARY (see organ.hammond_full)

**Pitfalls**

- Filter resonance or extra harmonics (5th, 7th) make it too bright.
- Velocity sensitivity makes it un-organ-like.

### Full Hammond: percussion, scanner chorus, overdrive, Leslie
*id `organ.hammond_full` · family Organ/Clavi · Synth Secrets SS55, SS57, SS58, SS59, SS60*

The Hammond sound = tonewheels + percussion (a decaying 2nd or 3rd harmonic accent) + scanner chorus (C-3: dry + one vibrato'd copy, ~6-7 Hz) + valve overdrive (with chord compression) + the Leslie (horn and rotor above/below 800 Hz, separate speeds, audible acceleration, Doppler about +-1 %, tremolo 90 deg out of phase, reflections). Chain: organ -> drive -> rotary -> cabinet.

Start from factory Tones: Rotary Org 1, Rotary Org 2, Lord Organ 1, Lord Organ 2, AX Dist Org1, AX Dist Org2, Amped D6
Waves: 26 JLOrg Slow L, 27 JLOrg Slow R, 28 JLOrg Fast L, 29 JLOrg Fast R, 34 3rd Perc Org, 35 Perc Organ, 36 Rock Organ, 37 RtryOrg 1 L, 38 RtryOrg 1 R, 270 OD Organ

**Steps**

- `tone.wave_number`: organ PCM (VK 259-263, Jazz 271/275) or sine drawbars (organ.drawbar)
- `tone.coarse_tune`: percussion tone: +12 (2nd) or +19 (3rd) (*Hammond percussion*)
- `tone.aenv_times`: percussion tone: T1 0, T3 20-30 (fast) or 40-60 (slow), L3 0, NO-SUS
- `tone.level`: percussion tone lower for Soft
- `wave:249` (Org Click 1): Org Click on a short tone, low level (*key-click*)

**Performance**

- `mfx.control_source`: CC01 (mod bar) or D-Beam CC -> rotary speed (*slow/fast Leslie switching*)

**Effects**

- `mfx:22` (VK ROTARY): VK ROTARY (drive + rotary; woofer/tweeter speeds and rise/fall times) (*the defining effect*)
- `mfx:21` (ROTARY): ROTARY (alternative)
- `reverb.level`: low-moderate (*spring-like room after the drive*)

**Pitfalls**

- Multi-stage ensemble chorus is too lush for Hammond scanner chorus.
- Pure V (vibrato) settings sound cheesy to many players.

### Acoustic grand piano
*id `piano.acoustic` · family Choir/Piano · Synth Secrets SS42, SS44, SS45*

Only samples convince. Keep the wave's attack; crossfade soft/loud layers by velocity; harder = brighter; high notes brighter but shorter and quieter; a two-slope decay; stretch tuning; sustain pedal with sympathetic resonance; no chorus, no LFO, no bend; a hall/room.

Start from factory Tones: AX Grand, E-Grand, JD-800 Piano, Blend Piano, Honky Tonk
Waves: 254 AX Grand mpL, 255 AX Grand mpR, 256 AX Grand ffL, 257 AX Grand ffR, 1 JD Piano

**Steps**

- `tmt.velocity`: tones 1+2 = 254/255 (mp L/R), tones 3+4 = 256/257 (ff L/R) with velocity fades (*velocity layers*)
- `tone.filter_type`: LPF2 (*the Editor manual: good for acoustic piano*)
- `tone.cutoff_vel_sens`: +15...+30
- `tone.cutoff_kf`: +20...+40
- `tone.aenv_time_kf`: +20...+40 (*high notes decay faster*)
- `tone.bias_level`: slightly negative toward the top (*high notes quieter*)
- `common.stretch_tune`: 1-2 (*stretched tuning sounds sweeter*)
- `tone.tva_vel_sens`: moderate (*soft notes still audible*)

**Performance**

- `tone.redamper`: ON (with RCV HOLD-1 ON) (*sustain pedal behaviour*)
- `common.bend`: 0 (*a piano can't bend*)

**Effects**

- `mfx:78` (SYMPATHETIC RESONANCE): SYMPATHETIC RESONANCE (*damper/pedal resonance*)
- `chorus.level`: 0 (*chorus is wrong for acoustic piano*)
- `reverb.type`: SRV HALL or ROOM

**Pitfalls**

- Reshaping the PCM attack with the envelope ruins the hammer transient.
- Chorus or LFO on an acoustic piano sounds cheap.

### Analogue-synth piano / electric piano character (JX10 'Acoustic Piano')
*id `piano.analog_ep` · family Choir/Piano · Synth Secrets SS42, SS43, SS44, SS45*

Subtractive 'pianos' end up Rhodes/Wurlitzer-like, which is valuable in itself. The JX10 recipe: a wiry synced tone with a big timbral blip at the attack (the hammer), a plain square body that takes over in the decay, a piano-shaped envelope (instant attack, long decay, no sustain), key-follow shortening, a modest velocity-scaled filter envelope, no chorus/LFO. Then layer two similar variants with a slight detune.

Start from factory Tones: Stage EP, Dyno EP, Wurly EP, SA EP, FM EP 1, Phase Stage, PhaseEP
Waves: 2 Stage EP p, 4 Dyno EP mp, 7 Wurly mp, 12 80's EP 1 mp, 16 Hard E.Pno, 19 ClavDB Brt

**Steps**

- `tone.wave_number`: tone 1 EP/clav PCM (16 Hard E.Pno / 19 ClavDB Brt) or saw; tone 2 a softer EP or square (*attack layer + body layer*)
- `tone.cutoff`: 60-75, resonance 0-5, cutoff_kf +20...+30
- `tone.fenv_depth`: +8...+12 with fenv_vel_sens +
- `tone.aenv_times`: T1 0, T3 long, T4 medium; tone 1 shorter than tone 2 (*the body dominates the tail*)
- `tone.aenv_levels`: L3 0
- `tone.aenv_time_kf`: +20...+40
- `tone.fine_tune`: tone 2 +3...+8 (*similar-not-identical layering*)
- `matrix.destination`: TVF ENV -> FXM DEPTH on the attack tone (FXM on) (*a timbral blip at the attack instead of oscillator sync*)

**Performance**

- `tone.tva_vel_curve`: a curve that keeps soft notes audible

**Effects**

- `chorus.level`: 0 for piano-like; moderate for EP
- `mfx:17` (TREMOLO): TREMOLO / 18 AUTO PAN for classic EP

### Clavinet / harpsichord (wiry plucked keys)
*id `keys.clav_harpsichord` · family Organ/Clavi · Synth Secrets SS43, SS28*

A wiry, bright, fast-decaying pluck: hard-sync-like harmonic richness at the attack, key-follow on the envelope times. Use clav/harpsichord PCM; for synthetic versions, use a thin pulse with a PKG/HPF emphasis.

Start from factory Tones: AX Clav 1, AX Clav 2, Pulse Clav 1, Pulse Clav 2, Harpsichord, Sweepin Clav
Waves: 19 ClavDB Brt, 20 Reg.Clav, 21 Retro Clav, 22 Tight Clav, 23 Hard Clav, 25 Harpsichord

**Steps**

- `tone.wave_number`: 19-24 clav, 25 Harpsichord
- `tone.aenv_time_kf`: +20...+40
- `tone.filter_type`: PKG or HPF for thin wire tone
- `tone.cutoff_vel_sens`: +20

**Effects**

- `mfx:8` (AUTO WAH): AUTO WAH for funky clav
- `mfx:11` (PHASER): PHASER

### Electric (overdriven) lead guitar
*id `guitar.electric_lead` · family Lead Guitar · Synth Secrets SS30, SS57*

Pickups comb-filter the string spectrum by note and the amp/speaker shapes the rest; subtractive synths only convince under heavy distortion. Use guitar PCM + an amp simulator; wide bends, mono legato, and feedback-like sustain for leads.

Start from factory Tones: SearingGtr 1, SearingGtr 2, SearingGtr 3, SearingGtr 4, Metal Lead, OD-2 Turbo, Nice Dist Gt, MS1959 I
Waves: 61 Overdrive Gt, 62 DistortionGt, 57 Bright Strat, 58 FstPick 70s

**Steps**

- `wave:61` (Overdrive Gt): Overdrive Gt (62 DistortionGt)
- `tone.aenv_levels`: sustain high for lead feedback sustain
- `common.bend`: up 12 / down 24 (as in the SearingGtr forum patch) (*guitar-style bends and dives*)

**Performance**

- `common.mono_poly`: MONO, legato ON
- `matrix.source`: a CC (e.g. D-Beam CC70) -> a feedback/+24 sine layer (TMT or LEVEL) (*see patches/guitar01.a8e: a CC70 'feedback' layer*)

**Effects**

- `mfx:39` (GUITAR AMP SIMULATOR): GUITAR AMP SIMULATOR (*the amp and speaker are the sound*)
- `mfx:68` (OVERDRIVE->DELAY): OVERDRIVE->DELAY / 71 DISTORTION->DELAY

**Pitfalls**

- Clean synth 'guitars' sound like synths; the distortion must dominate.

### Synth 'jazz guitar' (patch-book style)
*id `guitar.synth_jazz` · family Lead Guitar · Synth Secrets SS30*

Patch-book trick: a 25 % pulse (its spectral holes crudely mimic pickup/body notches), an instant attack, the same contour on filter and amp, sustain 0 (Reid), and the filter decaying faster than the amp. Pulse + saw from separate layers adds movement.

Start from factory Tones: Jazz EGtr, Clean EGtr
Waves: 206 JP8 Pls 25HD, 177 MG Saw HD, 55 Jazz Gtr

**Steps**

- `wave:206` (JP8 Pls 25HD): JP8 Pls 25HD on tone 1; optional tone 2 saw slightly detuned
- `tone.aenv_levels`: L3 0 (*a guitar doesn't sustain indefinitely*)
- `tone.fenv_times`: decay faster than TVA
- `tone.penv_levels`: L0 +2...+5 falling to 0 over T1/T2 20-40 (*a pluck starts slightly sharp*)

**Effects**

- `mfx:39` (GUITAR AMP SIMULATOR): GUITAR AMP SIMULATOR (clean amp)

### Acoustic / nylon guitar
*id `guitar.acoustic` · family Lead Guitar · Synth Secrets SS28, SS29*

Acoustic guitars can't be synthesized subtractively; use PCM with velocity layers. Harder pluck = brighter and longer (Matrix VELOCITY -> TVA decay), a two-slope decay, the filter following the amp, and shorter decays at high notes. Mono for single-string lines.

Start from factory Tones: Nylon Gtr 1, Nylon Gtr 2, Nylon Gtr 3, Folk Gtr 1, Folk Gtr 2, Folk Gtr 3
Waves: 49 Brt N.Gtr p, 50 Brt N.Gtr mf, 51 Brt N.Gtr ff, 52 Ac.Gtr mp, 53 Ac.Gtr mf, 54 Ac.Gtr ff

**Steps**

- `tmt.velocity`: 49/50/51 (nylon p/mf/ff) or 52/53/54 (steel mp/mf/ff) across velocity
- `tone.cutoff_vel_sens`: +20 (*pick hardness = brightness*)
- `matrix.destination`: VELOCITY -> TVA ENV D-TIME + (*harder = longer ring*)
- `tone.aenv_time_kf`: +20...+30

**Performance**

- `common.bend`: 2

**Effects**

- `mfx:24` (FLANGER): FLANGER with slow/no modulation (static comb) for pick-position colour (*optional*)
- `reverb.type`: SRV ROOM

**Pitfalls**

- Don't reshape the PCM attack.

### Classic analogue synth bass / bass guitar imitation
*id `bass.synth_classic` · family Bass · Synth Secrets SS02, SS21, SS27*

Synth Secrets notes that saw + pulse together give remarkably accurate bass-guitar imitations; saw + square an octave down gives body. Punchy: instant attack, a filter envelope spike, multi-trigger. Fat: detuned layers or unison.

Start from factory Tones: Moogue Bs1, Moogue Bs2, Fat Analog, Round Bs, Punch MG, Modular Bs1, JunoSqu Bs, Finger EBs 1, Pick Bs 1
Waves: 95 MG Bass 1, 96 MG Bass 2, 97 MG Bass 3, 93 SH-101 Bs, 177 MG Saw HD, 207 JP8 Pls 30HD

**Steps**

- `tone.wave_number`: saw (177/95-97 MG Bass) + pulse (207) on two tones
- `tone.cutoff`: 30-50, env +30...+50 fast decay, resonance to taste
- `tone.aenv_times`: T1 0; sustain medium-high for synth, 0 for plucked bass

**Performance**

- `common.mono_poly`: MONO; legato OFF for punch
- `common.portamento_time`: small, LEGATO mode, for slides

**Effects**

- `reverb.level`: low
- `mfx:40` (COMPRESSOR): COMPRESSOR

### 808-style kick (boom)
*id `drum.kick_808` · family other · Synth Secrets SS33, SS34*

A pinged, self-decaying sine with a small pitch drop that goes slightly flat on long decays, plus a trigger click tamed by an LPF. Boom length = decay.

Waves: 220 Sine, 214 Syn Triangle, 248 Key On Click

**Steps**

- `wave:220` (Sine): Sine, play C1-G1
- `tone.aenv_times`: T1 0, T3 long, L3 0, NO-SUS
- `tone.penv_depth`: +
- `tone.penv_levels`: L0 +8, back to 0 fast, then L3/L4 -1...-3 over a long T3 (*slight sag on long decays*)
- `tone.penv_vel_sens`: + (*accent = bigger drop*)

**Effects**

- `reverb.level`: low
- `mfx:40` (COMPRESSOR): COMPRESSOR / 4 LOW BOOST

**Pitfalls**

- Avoid an unintended click on smooth kicks: T1 not exactly 0 if clicky.

### 909-style kick (punchy)
*id `drum.kick_909` · family other · Synth Secrets SS33, SS34*

A near-sine body with a bigger, faster pitch drop, plus low-passed noise and a click pulse with their own short envelopes. Tight = short decay + fast drop.

Waves: 214 Syn Triangle, 220 Sine, 232 White Noise, 248 Key On Click

**Steps**

- `tone.penv_levels`: tone 1: L0 +20...+30, T1 short
- `tone.aenv_times`: tone 1 T3 short-medium; tone 2 (232 noise, LPF cutoff 60-80) T3 10-20; tone 3 (248 click) T3 ~0-5
- `tone.tva_vel_sens`: + (*accent*)

**Effects**

- `mfx:40` (COMPRESSOR): COMPRESSOR

### Snare drum (analogue-style)
*id `drum.snare` · family other · Synth Secrets SS19, SS35, SS36*

A tonal body (0,1 modes ~180 Hz and ~330 Hz, the upper decaying faster) plus snare-wire noise. Velocity moves the balance from tonal to noisy and brightens it. Simple version: full noise, LPF fully open, no resonance, a short decay, retrigger on every hit for rolls.

Waves: 232 White Noise, 220 Sine, 214 Syn Triangle

**Steps**

- `tone.wave_number`: tone 1 sine ~F#3 (180 Hz), tone 2 sine +10 st (330 Hz), tone 3 232 White Noise
- `tone.aenv_times`: body T3 short (tone 2 shorter), noise T3 15-30, all L3 0
- `tone.filter_type`: noise: LPF open (100-127) or HPF 40-60 for 808 snap; resonance 0 (*resonance makes an 'oww'*)
- `tone.cutoff_vel_sens`: noise + (*harder = brighter*)
- `tone.tva_vel_sens`: noise high, body low (*harder = noisier*)

**Performance**

- `common.mono_poly`: POLY (*rolls*)

**Effects**

- `mfx:65` (GATED REVERB): GATED REVERB for an '80s snare
- `reverb.type`: SRV ROOM

### Hi-hats, ride and crash cymbals (metal)
*id `drum.hihat_cymbal` · family other · Synth Secrets SS37, SS38, SS39, SS40*

A dense, flat, inharmonic fog. The best affordable method is several pairs of ring/FM-modulated square waves at unrelated pitches (Korg Rhythm 55), band-split with different decays (highs shortest). Crash/ride: a mid 'ping' sweeping down to ~1 kHz over 0.2 s plus a high-passed tail opening upward over 0.2 s and closing slowly. Hats = short decays; open hat = longer.

Waves: 196 Fat Square, 197 JP-8 Square, 198 SH-2 Square, 232 White Noise, 242 JD Rattles

**Steps**

- `tmt.structure_12`: ring-mod type (05/06/09/10); same for tmt.structure_34 (*two ring-mod pairs*)
- `tone.wave_number`: all squares (196/197/198)
- `tone.coarse_tune`: e.g. 0, +6 (+23 ct), +11 (-17 ct), +17 (+37 ct) (*unrelated ratios*)
- `tone.filter_type`: HPF, cutoff 60-90 (*remove lows*)
- `tone.aenv_times`: closed hat T3 5-10; open 40-60; ride 40-60 with NO-SUS
- `tone.pitch_kf`: 0-20 (*metal barely tracks the keyboard*)
- `tone.fxm_sw`: optional ON, color 1-2 (*more partials*)

**Performance**

- `common.mono_poly`: MONO with open and closed hats in one patch (*choke-like behaviour*)

**Effects**

- `reverb.type`: SRV ROOM

**Pitfalls**

- Noise alone gives a 'weedy' synthetic cymbal.
- A low filter ceiling kills cymbals: keep the cutoff high.

### 808/CR-8000 cowbell
*id `perc.cowbell` · family other · Synth Secrets SS41*

Two triangles at 587 Hz and 845 Hz (ratio 1:1.44), the upper slightly louder, band-pass ~2.6 kHz (12 dB) with slight resonance, a two-stage decay (a loud short impact, then a tail), and a faint pink-noise halo. Exact tuning matters.

Waves: 214 Syn Triangle, 153 JD Cowbell, 233 Pink Noise

**Steps**

- `wave:214` (Syn Triangle): Syn Triangle on tones 1+2; play D5 (*587 Hz*)
- `tone.coarse_tune`: tone 2 +6 with fine_tune +31 (*ratio 1.44*)
- `tone.filter_type`: BPF, cutoff high-mid, resonance low-moderate
- `tone.aenv_levels`: L1 127, L2 50-60, L3 0 (T2 very short, T3 medium) (*a two-stage decay*)
- `wave:233` (Pink Noise): optional tone 3 Pink Noise, very short, low

**Pitfalls**

- Small tuning deviations destroy the cowbell illusion.

### Claves / woodblock
*id `perc.claves` · family other · Synth Secrets SS41*

A triangle through a band-pass with no resonance and a very short decay: a woody click. PCM 139 JD Wood Crak / 142 JD Log Drum are alternatives.

Waves: 214 Syn Triangle, 139 JD Wood Crak, 142 JD Log Drum

**Steps**

- `wave:214` (Syn Triangle): Syn Triangle
- `tone.filter_type`: BPF, resonance 0
- `tone.aenv_times`: T1 0, T3 3-8

### Timpani (kettle drum)
*id `perc.timpani` · family other · Synth Secrets SS31, SS32*

Four sine partials at 1.00 : 1.50 : 1.98 : 2.44 of the principal (~150 Hz), amplitudes ~5:4:3:1, relative decays ~45/73/91/84 %, plus a short enharmonic strike burst (tuned rough pink noise or ring mod). Velocity sets only the level. Play pitch with the bend (+-a fifth).

Waves: 220 Sine, 233 Pink Noise

**Steps**

- `wave:220` (Sine): Sine on tones 1-3 (or 1-4)
- `tone.coarse_tune`: 0; +7 (+2 ct); +12 (-17 ct); +15 (+44 ct) (*the partial ratios*)
- `tone.level`: 127 / 102 / 76 / 25 (*5:4:3:1*)
- `tone.aenv_times`: T1 0; T3 ~45/73/91/84 % of the longest; T4 = T3; NO-SUS
- `tone.filter_type`: strike tone: 233 Pink Noise BPF resonant, very short decay
- `tone.tva_vel_sens`: + (level only; cutoff vel sens 0)

**Performance**

- `common.bend`: 7 / 7 (*pedal timpani range*)

**Effects**

- `reverb.type`: SRV HALL
- `chorus.level`: 0

### Church / tubular / hand bell
*id `perc.bell` · family other · Synth Secrets SS02, SS13, SS40*

Three phases: a fast inharmonic strike (clang); a strike note of a few strong, slightly stretched low partials (a 2:3:4 pattern implies the pitch); a long sub-octave hum that beats slowly. Warble from nearly identical modes beating. Needs a reverb.

Start from factory Tones: FM Sparkles, D-50 Fantsia, Dreaming Box
Waves: 154 Tubular Bell, 155 Church Bell, 148 D-50 Bell, 157 JD Crystal, 220 Sine

**Steps**

- `wave:154` (Tubular Bell): Tubular Bell / 155 Church Bell as the quick route
- `tone.fxm_depth`: synth: tone 1 sine + FXM 4-8, color 1-2; decay two-stage
- `tone.coarse_tune`: tone 2 +12 with +15...+30 ct (stretched); tone 3 -12 (hum); tone 4 -12 +2...+4 ct (beating)
- `tone.aenv_times`: hum tones: T1 20-40 (slower), T3 long (*the hum lingers*)
- `tone.lfo_depth_tva`: small, 3-6 Hz, optional (*warble*)

**Effects**

- `reverb.type`: SRV HALL, long

### Metallic / clangorous percussion and FX
*id `perc.metallic_fx` · family other · Synth Secrets SS02, SS11, SS13, SS39*

Inharmonic partials: ring mod between tones at odd ratios (a fixed-pitch modulator = the timbre changes across the keyboard), FXM with low colour, FM-style envelopes on the index, short percussive envelopes.

Start from factory Tones: Ethno Keys, Steel Drums
Waves: 239 Metal Vox 1, 240 Metal Vox 2, 241 Metal Vox 3, 242 JD Rattles, 223 JD MetalWind, 147 Steel Drums

**Steps**

- `structure.ring_modulator`: TYPE 05-10; tone 2 at an odd interval (+6, +11, +13 with odd cents)
- `tone.pitch_kf`: modulator tone 0 for an enharmonic keyboard sweep; 100 for a consistent timbre
- `matrix.destination`: TVF ENV -> FXM DEPTH (*an FM-like brightness envelope*)

**Effects**

- `mfx:15` (RING MODULATOR): RING MODULATOR / 16 STEP RING MODULATOR

### Classic mono synth lead
*id `synth.mono_lead` · family Synth Lead 1 · Synth Secrets SS06, SS07, SS18, SS21, SS25, SS50*

Saw (or square for hollow), a resonant LPF with a punchy envelope spike, mono with a chosen trigger mode (legato slurs vs multi-trigger punch), portamento, delayed vibrato on the mod bar, bend. Fat = detuned unison layers.

Start from factory Tones: Saw Lead 1, Classic Ld, Pro Fat Ld, JupiterLead1, Waspy Lead, Mini Growl, Fat GR Lead
Waves: 177 MG Saw HD, 185 JP-8 Saw, 174 Juno Saw HD, 122 Super Saw, 196 Fat Square

**Steps**

- `tone.wave_number`: saw 177/185 (square 196 for hollow)
- `tone.cutoff`: 40-70; resonance 20-60; env +30...+50, fast T2
- `tone.fine_tune`: tones 2/3 +-7...+-15 (*unison fatness*)

**Performance**

- `common.mono_poly`: MONO
- `common.legato_sw`: ON for singing lines, OFF for punchy staccato
- `common.portamento_sw`: ON, time 10-40, mode LEGATO
- `matrix.source`: CC01 -> LFO1 PCH DEPTH; AFTERTOUCH -> CUTOFF or LFO TVF DEPTH (growl)
- `common.bend`: 2 (or 12 for dives)

**Effects**

- `mfx:43` (DELAY): DELAY
- `reverb.level`: moderate

### 'Sync' lead (tearing timbre sweep)
*id `synth.sync_lead` · family Synth Lead 1 · Synth Secrets SS43, SS45*

Hard sync sweeps timbre, not pitch, as the slave's pitch is swept by an envelope. The AX-Synth has no oscillator sync: use the 219 Sync Sweep PCM, or FXM with the TVF envelope routed to FXM DEPTH for an evolving harmonic sweep.

Start from factory Tones: AX Sync Lead, Octa Sync, Hot Sync, Sync Tank
Waves: 219 Sync Sweep

**Steps**

- `wave:219` (Sync Sweep): Sync Sweep
- `tone.fxm_sw`: alternative: FXM ON on a saw; Matrix TVF ENV -> FXM DEPTH +

**Performance**

- `common.mono_poly`: MONO

**Effects**

- `mfx:35` (OVERDRIVE): OVERDRIVE light

### Warm pad ('carpet')
*id `synth.pad_carpet` · family Strings/Pad · Synth Secrets SS14, SS46, SS62*

Detuned saws or pad PCM, a moderate LPF with slow movement (slow LFO or a long filter envelope), a slow attack and long release, no velocity, chorus + a hall. Evolving: layers with different envelopes crossfading.

Start from factory Tones: Soft Pad 1, Soft Pad 2, Heaven Pad, Angelis Pad, Nu Epic Pad, Shimmer Pad, Voyager
Waves: 124 Warm Pad, 125 OB2 Pad 1, 126 OB2 Pad 2, 127 D-50 Heaven, 185 JP-8 Saw, 190 Air Wave

**Steps**

- `tone.wave_number`: 124 Warm Pad / 125-126 OB2 Pad / 127 D-50 Heaven / detuned saws
- `tone.aenv_times`: T1 40-80, T4 60-100
- `tone.lfo_depth_tvf`: small, very slow (*gentle movement*)
- `common.analog_feel`: 20-40

**Performance**

- `matrix.source`: CC01 -> CUTOFF for hand-opened brightness

**Effects**

- `chorus.type`: CHORUS
- `reverb.type`: SRV HALL, long

### Choir / vocal / formant sound
*id `voice.choir_formant` · family Choir/Piano · Synth Secrets SS15, SS23*

Vowels are fixed formant peaks (ee 270/2300/3000 Hz, oo 300/870/2250, a 660/1700/2400 for an adult male; women's slightly higher/wider). Use choir or formant PCM or a HUMANIZER vowel filter; a slow attack, a little vibrato, chorus and hall. The AX-Synth has no vocoder/audio input.

Start from factory Tones: Angels Choir, Aerial Choir, Humming, Gospel Hum, Vox Pad 1, SynVox 1, Jazz Dooos
Waves: 131 Female Ahs, 132 Female Oos, 133 Male Aahs, 134 Jazz Doos, 136 Gospel Hum, 234 Aah Formant, 235 Eeh Formant, 236 Iih Formant, 237 Ooh Formant, 238 Uuh Formant

**Steps**

- `wave:131` (Female Ahs): Female Ahs (132 Oos, 133 Male Aahs, 234-238 formant waves)
- `tone.aenv_times`: T1 20-40
- `tone.lfo_fade_mode`: ON-IN, small pitch depth

**Performance**

- `mfx.control_source`: CC01 -> HUMANIZER vowel (*vowel morph*)

**Effects**

- `mfx:9` (HUMANIZER): HUMANIZER
- `reverb.type`: SRV HALL

**Pitfalls**

- Don't promise vocoder sounds: there's no audio input.

## Synth Secrets parts

| Part | Published | Title | Digest |
|---|---|---|---|
| 1 | May 1999 | [What's In A Sound?](https://www.soundonsound.com/techniques/whats-sound) | [01-whats-sound.md](digests/01-whats-sound.md) |
| 2 | Jun 1999 | [The Physics Of Percussion](https://www.soundonsound.com/techniques/physics-percussion) | [02-physics-percussion.md](digests/02-physics-percussion.md) |
| 3 | Jul 1999 | [Modifiers & Controllers](https://www.soundonsound.com/techniques/modifiers-controllers) | [03-modifiers-controllers.md](digests/03-modifiers-controllers.md) |
| 4 | Aug 1999 | [Of Filters & Phase Relationships](https://www.soundonsound.com/techniques/filters-phase-relationships) | [04-filters-phase-relationships.md](digests/04-filters-phase-relationships.md) |
| 5 | Sep 1999 | [Further With Filters](https://www.soundonsound.com/techniques/further-filters) | [05-further-filters.md](digests/05-further-filters.md) |
| 6 | Oct 1999 | [Of Responses & Resonance](https://www.soundonsound.com/techniques/responses-resonance) | [06-responses-resonance.md](digests/06-responses-resonance.md) |
| 7 | Nov 1999 | [Envelopes, Gates & Triggers](https://www.soundonsound.com/techniques/envelopes-gates-triggers) | [07-envelopes-gates-triggers.md](digests/07-envelopes-gates-triggers.md) |
| 8 | Dec 1999 | [More About Envelopes](https://www.soundonsound.com/techniques/more-about-envelopes) | [08-more-about-envelopes.md](digests/08-more-about-envelopes.md) |
| 9 | Jan 2000 | [An Introduction To VCAs](https://www.soundonsound.com/techniques/introduction-vcas) | [09-introduction-vcas.md](digests/09-introduction-vcas.md) |
| 10 | Feb 2000 | [Modulation](https://www.soundonsound.com/techniques/modulation) | [10-modulation.md](digests/10-modulation.md) |
| 11 | Mar 2000 | [Amplitude Modulation](https://www.soundonsound.com/techniques/amplitude-modulation) | [11-amplitude-modulation.md](digests/11-amplitude-modulation.md) |
| 12 | Apr 2000 | [An Introduction To Frequency Modulation](https://www.soundonsound.com/techniques/introduction-frequency-modulation) | [12-introduction-frequency-modulation.md](digests/12-introduction-frequency-modulation.md) |
| 13 | May 2000 | [More On Frequency Modulation](https://www.soundonsound.com/techniques/more-frequency-modulation) | [13-more-frequency-modulation.md](digests/13-more-frequency-modulation.md) |
| 14 | Jun 2000 | [An Introduction To Additive Synthesis](https://www.soundonsound.com/techniques/introduction-additive-synthesis) | [14-introduction-additive-synthesis.md](digests/14-introduction-additive-synthesis.md) |
| 15 | Jul 2000 | [An Introduction To ESPs & Vocoders](https://www.soundonsound.com/techniques/introduction-esps-vocoders) | [15-introduction-esps-vocoders.md](digests/15-introduction-esps-vocoders.md) |
| 16 | Aug 2000 | [From Sample & Hold To Sample-rate Converters (1)](https://www.soundonsound.com/techniques/sample-hold-sample-rate-converters-1) | [16-sample-hold-sample-rate-converters-1.md](digests/16-sample-hold-sample-rate-converters-1.md) |
| 17 | Sep 2000 | [From Sample & Hold To Sample-rate Converters (2)](https://www.soundonsound.com/techniques/sample-hold-sample-rate-converters-2) | [17-sample-hold-sample-rate-converters-2.md](digests/17-sample-hold-sample-rate-converters-2.md) |
| 18 | Oct 2000 | [Priorities & Triggers](https://www.soundonsound.com/techniques/priorities-triggers) | [18-priorities-triggers.md](digests/18-priorities-triggers.md) |
| 19 | Nov 2000 | [Duophony](https://www.soundonsound.com/techniques/duophony) | [19-duophony.md](digests/19-duophony.md) |
| 20 | Dec 2000 | [Introducing Polyphony](https://www.soundonsound.com/techniques/introducing-polyphony) | [20-introducing-polyphony.md](digests/20-introducing-polyphony.md) |
| 21 | Jan 2001 | [From Polyphony To Digital Synths](https://www.soundonsound.com/techniques/polyphony-digital-synths) | [21-polyphony-digital-synths.md](digests/21-polyphony-digital-synths.md) |
| 22 | Feb 2001 | [From Springs, Plates & Buckets To Physical Modelling](https://www.soundonsound.com/techniques/springs-plates-buckets-physical-modelling) | [22-springs-plates-buckets-physical-modelling.md](digests/22-springs-plates-buckets-physical-modelling.md) |
| 23 | Mar 2001 | [Formant Synthesis](https://www.soundonsound.com/techniques/formant-synthesis) | [23-formant-synthesis.md](digests/23-formant-synthesis.md) |
| 24 | Apr 2001 | [Synthesizing Wind Instruments](https://www.soundonsound.com/techniques/synthesizing-wind-instruments) | [24-synthesizing-wind-instruments.md](digests/24-synthesizing-wind-instruments.md) |
| 25 | May 2001 | [Synthesizing Brass Instruments](https://www.soundonsound.com/techniques/synthesizing-brass-instruments) | [25-synthesizing-brass-instruments.md](digests/25-synthesizing-brass-instruments.md) |
| 26 | Jun 2001 | [Brass Synthesis On A Minimoog](https://www.soundonsound.com/techniques/brass-synthesis-minimoog) | [26-brass-synthesis-minimoog.md](digests/26-brass-synthesis-minimoog.md) |
| 27 | Jul 2001 | [Roland SH101 & ARP Axxe Brass Synthesis](https://www.soundonsound.com/techniques/roland-sh101-arp-axxe-brass-synthesis) | [27-roland-sh101-arp-axxe-brass-synthesis.md](digests/27-roland-sh101-arp-axxe-brass-synthesis.md) |
| 28 | Aug 2001 | [Synthesizing Plucked Strings](https://www.soundonsound.com/techniques/synthesizing-plucked-strings) | [28-synthesizing-plucked-strings.md](digests/28-synthesizing-plucked-strings.md) |
| 29 | Sep 2001 | [The Theoretical Acoustic Guitar Patch](https://www.soundonsound.com/techniques/theoretical-acoustic-guitar-patch) | [29-theoretical-acoustic-guitar-patch.md](digests/29-theoretical-acoustic-guitar-patch.md) |
| 30 | Oct 2001 | [A Final Attempt To Synthesize Guitars](https://www.soundonsound.com/techniques/final-attempt-synthesize-guitars) | [30-final-attempt-synthesize-guitars.md](digests/30-final-attempt-synthesize-guitars.md) |
| 31 | Nov 2001 | [Synthesizing Percussion](https://www.soundonsound.com/techniques/synthesizing-percussion) | [31-synthesizing-percussion.md](digests/31-synthesizing-percussion.md) |
| 32 | Dec 2001 | [Practical Percussion Synthesis: Timpani](https://www.soundonsound.com/techniques/practical-percussion-synthesis-timpani) | [32-practical-percussion-synthesis-timpani.md](digests/32-practical-percussion-synthesis-timpani.md) |
| 33 | Jan 2002 | [Synthesizing Drums: The Bass Drum](https://www.soundonsound.com/techniques/synthesizing-drums-bass-drum) | [33-synthesizing-drums-bass-drum.md](digests/33-synthesizing-drums-bass-drum.md) |
| 34 | Feb 2002 | [Practical Bass Drum Synthesis](https://www.soundonsound.com/techniques/practical-bass-drum-synthesis) | [34-practical-bass-drum-synthesis.md](digests/34-practical-bass-drum-synthesis.md) |
| 35 | Mar 2002 | [Synthesizing Drums: The Snare Drum](https://www.soundonsound.com/techniques/synthesizing-drums-snare-drum) | [35-synthesizing-drums-snare-drum.md](digests/35-synthesizing-drums-snare-drum.md) |
| 36 | Apr 2002 | [Practical Snare Drum Synthesis](https://www.soundonsound.com/techniques/practical-snare-drum-synthesis) | [36-practical-snare-drum-synthesis.md](digests/36-practical-snare-drum-synthesis.md) |
| 37 | May 2002 | [Analysing Metallic Percussion](https://www.soundonsound.com/techniques/analysing-metallic-percussion) | [37-analysing-metallic-percussion.md](digests/37-analysing-metallic-percussion.md) |
| 38 | Jun 2002 | [Synthesizing Realistic Cymbals](https://www.soundonsound.com/techniques/synthesizing-realistic-cymbals) | [38-synthesizing-realistic-cymbals.md](digests/38-synthesizing-realistic-cymbals.md) |
| 39 | Jul 2002 | [Practical Cymbal Synthesis](https://www.soundonsound.com/techniques/practical-cymbal-synthesis) | [39-practical-cymbal-synthesis.md](digests/39-practical-cymbal-synthesis.md) |
| 40 | Aug 2002 | [Synthesizing Bells](https://www.soundonsound.com/techniques/synthesizing-bells) | [40-synthesizing-bells.md](digests/40-synthesizing-bells.md) |
| 41 | Sep 2002 | [Synthesizing Cowbells & Claves](https://www.soundonsound.com/techniques/synthesizing-cowbells-claves) | [41-synthesizing-cowbells-claves.md](digests/41-synthesizing-cowbells-claves.md) |
| 42 | Oct 2002 | [Synthesizing Pianos](https://www.soundonsound.com/techniques/synthesizing-pianos) | [42-synthesizing-pianos.md](digests/42-synthesizing-pianos.md) |
| 43 | Nov 2002 | [Synthesizing Acoustic Pianos On The Roland JX10 [Part 1]](https://www.soundonsound.com/techniques/synthesizing-acoustic-pianos-roland-jx10-1102) | [43-synthesizing-acoustic-pianos-roland-jx10-1102.md](digests/43-synthesizing-acoustic-pianos-roland-jx10-1102.md) |
| 44 | Dec 2002 | [Synthesizing Acoustic Pianos On The Roland JX10 [Part 2]](https://www.soundonsound.com/techniques/synthesizing-acoustic-piano-roland-jx10) | [44-synthesizing-acoustic-piano-roland-jx10.md](digests/44-synthesizing-acoustic-piano-roland-jx10.md) |
| 45 | Jan 2003 | [Synthesizing Acoustic Pianos On The Roland JX10 [Part 3]](https://www.soundonsound.com/techniques/synthesizing-acoustic-pianos-roland-jx10-part-3) | [45-synthesizing-acoustic-pianos-roland-jx10-part-3.md](digests/45-synthesizing-acoustic-pianos-roland-jx10-part-3.md) |
| 46 | Feb 2003 | [Synthesizing Strings: String Machines](https://www.soundonsound.com/techniques/synthesizing-strings-string-machines) | [46-synthesizing-strings-string-machines.md](digests/46-synthesizing-strings-string-machines.md) |
| 47 | Mar 2003 | [Synthesizing Strings: PWM & String Sounds](https://www.soundonsound.com/techniques/synthesizing-strings-pwm-string-sounds) | [47-synthesizing-strings-pwm-string-sounds.md](digests/47-synthesizing-strings-pwm-string-sounds.md) |
| 48 | Apr 2003 | [Synthesizing Bowed Strings: The Violin Family](https://www.soundonsound.com/techniques/synthesizing-bowed-strings-violin-family) | [48-synthesizing-bowed-strings-violin-family.md](digests/48-synthesizing-bowed-strings-violin-family.md) |
| 49 | May 2003 | [Practical Bowed-string Synthesis](https://www.soundonsound.com/techniques/practical-bowed-string-synthesis) | [49-practical-bowed-string-synthesis.md](digests/49-practical-bowed-string-synthesis.md) |
| 50 | Jun 2003 | [Practical Bowed-string Synthesis (continued)](https://www.soundonsound.com/techniques/practical-bowed-string-synthesis-continued) | [50-practical-bowed-string-synthesis-continued.md](digests/50-practical-bowed-string-synthesis-continued.md) |
| 51 | Jul 2003 | [Articulation & Bowed-string Synthesis](https://www.soundonsound.com/techniques/articulation-bowed-string-synthesis) | [51-articulation-bowed-string-synthesis.md](digests/51-articulation-bowed-string-synthesis.md) |
| 52 | Aug 2003 | [Synthesizing Pan Pipes](https://www.soundonsound.com/techniques/synthesizing-pan-pipes) | [52-synthesizing-pan-pipes.md](digests/52-synthesizing-pan-pipes.md) |
| 53 | Sep 2003 | [Synthesizing Simple Flutes](https://www.soundonsound.com/techniques/synthesizing-simple-flutes) | [53-synthesizing-simple-flutes.md](digests/53-synthesizing-simple-flutes.md) |
| 54 | Oct 2003 | [Practical Flute Synthesis](https://www.soundonsound.com/techniques/practical-flute-synthesis) | [54-practical-flute-synthesis.md](digests/54-practical-flute-synthesis.md) |
| 55 | Nov 2003 | [Synthesizing Tonewheel Organs: Part 1](https://www.soundonsound.com/techniques/synthesizing-tonewheel-organs-part-1) | [55-synthesizing-tonewheel-organs-part-1.md](digests/55-synthesizing-tonewheel-organs-part-1.md) |
| 56 | Dec 2003 | [Synthesizing Tonewheel Organs: Part 2](https://www.soundonsound.com/techniques/synthesizing-tonewheel-organs-part-2) | [56-synthesizing-tonewheel-organs-part-2.md](digests/56-synthesizing-tonewheel-organs-part-2.md) |
| 57 | Jan 2004 | [Synthesizing Hammond Organ Effects](https://www.soundonsound.com/techniques/synthesizing-hammond-organ-effects) | [57-synthesizing-hammond-organ-effects.md](digests/57-synthesizing-hammond-organ-effects.md) |
| 58 | Feb 2004 | [Synthesizing The Rest Of The Hammond Organ: Part 1](https://www.soundonsound.com/techniques/synthesizing-rest-hammond-organ-part-1) | [58-synthesizing-rest-hammond-organ-part-1.md](digests/58-synthesizing-rest-hammond-organ-part-1.md) |
| 59 | Mar 2004 | [Synthesizing The Rest Of The Hammond Organ: Part 2](https://www.soundonsound.com/techniques/synthesizing-rest-hammond-organ-part-2) | [59-synthesizing-rest-hammond-organ-part-2.md](digests/59-synthesizing-rest-hammond-organ-part-2.md) |
| 60 | Apr 2004 | [From Analogue To Digital Effects](https://www.soundonsound.com/techniques/analogue-digital-effects) | [60-analogue-digital-effects.md](digests/60-analogue-digital-effects.md) |
| 61 | May 2004 | [Creative Synthesis With Delays](https://www.soundonsound.com/techniques/creative-synthesis-delays) | [61-creative-synthesis-delays.md](digests/61-creative-synthesis-delays.md) |
| 62 | Jun 2004 | [More Creative Synthesis With Delays](https://www.soundonsound.com/techniques/more-creative-synthesis-delays) | [62-more-creative-synthesis-delays.md](digests/62-more-creative-synthesis-delays.md) |
| 63 | Jul 2004 | [The Secret Of The Big Red Button](https://www.soundonsound.com/techniques/secret-big-red-button) | [63-secret-big-red-button.md](digests/63-secret-big-red-button.md) |
