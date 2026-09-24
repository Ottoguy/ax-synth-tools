# SS05 Further With Filters (Sep 1999): digest

Source: Synth Secrets part 5, https://www.soundonsound.com/techniques/further-filters. Claims = [3P]; AX-Synth lines = [I].

## Setting → sound facts
- A low-pass filter is already −3 dB **at** its cutoff, so audible dulling starts at and slightly below the cutoff, not just above it.
- Slope: 6 dB/oct (1-pole) = tone-control dullness only ("the same sound, but duller"). 12 dB/oct (2-pole) and 24 dB/oct (4-pole) actually reshape timbre. Real 4-pole filters pass through 6/12/18 dB/oct regions before reaching 24.
- Even a gentle LPF at 3 kHz on a 100 Hz saw leaves 30 harmonics untouched, yet the ear hears the missing top as "dull/lacking top end". The ear is very sensitive to the high harmonics.
- Every filter design sounds different: Moog, ARP, MS-20 and SEM each have their own character. A filter that can't open fully (e.g. ARP 4075 capped at ~12 kHz) makes an instrument sound "dull and lifeless".

## AX-Synth translation
- `tone.filter_type`:
  - LPF: the standard resonant low-pass
  - LPF2: half the sensitivity of LPF, i.e. a gentler, tone-control-like response for "natural"/acoustic instruments
  - LPF3: sensitivity varies with cutoff
  - With LPF2/LPF3 the resonance is ignored. The dB/octave slope isn't documented [D EM p.32].
- For "just a bit less bright", lower `tone.cutoff` slightly or use LPF2. For a "new timbre", use LPF with a lower cutoff plus envelope movement.
- `common.offset_cutoff` shifts all tones' cutoff together: a patch-wide "brightness" macro.
- To keep full brightness, use cutoff 127 or `tone.filter_type` OFF (the PCM wave passes unfiltered).
