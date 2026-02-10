# Manatu

*manatu* (Estonian) — the one who has been enchanted with words

A KLSYN88-based Klatt formant speech synthesizer with complete IPA coverage, written in C++ with Python bindings.

## Overview

Manatu is a free and open-source speech synthesizer targeting the quality of classic Klatt synthesizers like DecTalk and Eloquence. It covers 121 IPA phonemes — vowels, consonants, diphthongs, nasalized vowels, and retroflexes — using modern DSP techniques: Zero Delay Feedback resonators for stable formant filtering, a Liljencrants-Fant glottal model for natural voice quality, and context-aware coarticulation with F2 locus equations for smooth phoneme transitions.

Manatu is delivered both as a standalone synthesis engine (`speechPlayer.dll`) and as an NVDA screen reader addon for blind and visually impaired users.

## Features

- **121 IPA phonemes** — front/back/central vowels, r-colored vowels, nasalized vowels, stops, nasals, fricatives, affricates, liquids, glides, trills, taps, and 22 diphthongs
- **KLSYN88 cascade/parallel formant synthesis** — dual-path architecture with 6 cascade and 6 parallel formant resonators
- **Zero Delay Feedback (ZDF) resonators** — Zavalishin (2012) topology; 4th-order (24 dB/oct) for F1-F3, 2nd-order for F4-F6
- **Liljencrants-Fant (LF) glottal model** — continuous voice quality control from tense (Rd=0.3) through modal (Rd=1.0) to breathy (Rd=2.7)
- **Context-aware coarticulation** — F2 locus equations by consonant place of articulation for natural transitions
- **Hermite smoothstep interpolation** — smooth parameter trajectories between phoneme frames
- **Trill modulator and burst pre-filtering** — dedicated mechanisms for trills (/r/, /ʀ/, /ʙ/) and stop bursts
- **NVDA screen reader addon** — packages as a ready-to-install `.nvda-addon`

## Tools

### Phoneme Editor

`editor/phoneme_editor.py` — wxPython GUI for tuning all 47 Klatt synthesis parameters with live audio preview.

- Slider controls for every parameter (formants, bandwidths, voice quality, noise, gains)
- Browse and load from the full phoneme data library or saved presets
- Sequence testing: hear phonemes in VCV and word contexts
- Export parameter sets as Python dicts or JSON

### Conlang GUI

`conlang_gui.py` / `conlang_gui_wx.py` — Desktop synthesizer for testing IPA input. The wxPython version provides full screen reader accessibility.

### IPA Keyboard

`ipa_keyboard.py` — Alt+key input method for IPA symbols, cycling through related characters on repeated presses.

### Analysis Tools

The `tools/` directory contains scripts for development and phoneme tuning:

- `spectral_analysis.py` — LPC formant extraction and spectral envelope plotting
- `phoneme_validator.py` — automated F1/F2/F3 accuracy checking against target values
- `vowel_autotuner.py` — iterative parameter optimization for vowel formants
- `fricative_autotuner.py` — noise parameter tuning for fricative consonants
- `consonant_diagnostic.py` — spectral and temporal analysis of consonant output

## Background

The 70s and 80s saw much research in speech synthesis. One of the most prominent synthesis models that appeared was a formant-frequency synthesis known as Klatt synthesis. Some well-known Klatt synthesizers are DecTalk and Eloquence. They are well suited for use by the blind as they are extremely responsive, their pronunciation is smooth and predictable, and they are small in memory footprint. However, research soon moved onto other forms of synthesis such as concatenative speech, as although this was slower, it was much closer to the human voice. This was an advantage for usage in mainstream applications such as GPS units or telephone systems, but not necessarily so much of an advantage to the blind, who tend to care more about responsiveness and predictability over prettiness.

Although synthesizers such as DecTalk and Eloquence continued to be maintained and available for nearly 20 years, now they are becoming harder to get, with multiple companies saying that these, and their variants, have been end-of-lifed and will not be updated anymore.

Concatenative synthesis is now starting to show promise as a replacement as the responsiveness and smoothness is improving. However, most if not all of the acceptable quality synthesizers are commercial and are rather expensive.

Both DecTalk and Eloquence were closed-source commercial products themselves. However, there is a substantial amount of source code and research material on Klatt synthesis available to the community. Manatu takes advantage of this by being a modern, research-grounded Klatt synthesizer, in the hopes to either be a replacement for synthesizers like DecTalk or Eloquence, or at least restart research and conversation around this synthesis method.

The eSpeak synthesizer, itself a free and open-source product, has proved well as a replacement to a certain number of people in the community, but many people are extremely quick to point out its "metallic" sound and cannot seem to continue to use it. One goal of Manatu is to understand better this resistance to eSpeak, which may have something to do with eSpeak's spectral frequency synthesis versus Klatt synthesis, or with the fact that consonants in eSpeak are gathered from recorded speech and can therefore be perceived as being injected into the speech stream.

## Implementation

The synthesis engine is written in C++ using modern idioms, closely following the implementation of klsyn-88 from the [Berkeley Phonetics Lab](http://linguistics.berkeley.edu/phonlab/resources/).

[eSpeak](http://espeak.sourceforge.net/) is used to parse text into phonemes represented in IPA, making use of existing eSpeak dictionary processing.

The initial Klatt formant data for each phoneme was collected from [PyKlatt](http://code.google.com/p/pyklatt/) and has since been extensively retuned based on published acoustic research — primarily Hillenbrand et al. (1995) vowel formant measurements, Stevens (1998) acoustic phonetics data, and Klatt & Klatt (1990) voice quality parameters.

The rules for phoneme lengths, gaps, speed and intonation have been coded by hand in Python, with eSpeak's intonation data used as a reference.

## Building

You will need:
- Python 3.7+
- SCons 3: http://www.scons.org/
- Visual Studio 2019 Community

To build, run `scons` from the project root. This produces:
- `speechPlayer.dll` — the synthesis engine
- `nvSpeechPlayer_<version>.nvda-addon` — NVDA addon (version from git revision)

Installing the addon into NVDA will allow you to use the Manatu synthesizer. Everything needed is packaged in the addon; no extra DLLs or files need to be copied.

## Running Tests

```
python tests/synthesis/test_engine.py    # Core DSP tests
python tests/phonemes/test_vowels.py     # Vowel formant accuracy
python tests/phonemes/test_consonants.py # Consonant tests
```

Tests generate WAV files to `tests/output/` for auditory inspection. The DLL must be built first.

## Architecture

```
IPA Text --> Phoneme Parsing --> Coarticulation --> Pitch Contours --> Frames
                                                                        |
Audio <-- Soft Limit <-- Mix <-- Parallel Path <---- Noise/Burst        v
                          ^                                             |
                  Cascade Path <-- Tracheal <-- Spectral Tilt <-- Glottal Pulse
```

The C++ engine handles real-time sample generation while Python manages phoneme data, linguistic processing, and coarticulation rules. See `docs/SYNTHESIS.md` for the full technical reference.

## Origins and Acknowledgments

Manatu was originally developed as **NV Speech Player** by [NV Access Limited](https://www.nvaccess.org/). NV Access is no longer maintaining the original project; this fork continues the work with expanded phoneme coverage, modern DSP, and research-based parameter tuning.

The [eSpeak-ng](https://github.com/espeak-ng/espeak-ng) project includes a copy of the original speechPlayer code as an alternative Klatt implementation.

Thanks to the projects and research that made Manatu possible:
- **klsyn-88** (Berkeley Phonetics Lab) — the original Klatt synthesis implementation
- **PyKlatt** — initial formant parameter data
- **Dennis Klatt** and the Klatt synthesis research community
- **Zavalishin (2012)** — Zero Delay Feedback filter topology
- **Liljencrants & Fant** — the LF glottal pulse model

## Licence and Copyright

Manatu is Copyright (c) 2014 NV Speech Player contributors, 2024-2026 Manatu contributors.

Manatu is covered by the GNU General Public License (Version 2).
You are free to share or change this software in any way you like
as long as it is accompanied by the license and you make all
source code available to anyone who wants it. This applies to
both original and modified copies of this software, plus any
derivative works.

For further details, you can view the license online at:
http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
