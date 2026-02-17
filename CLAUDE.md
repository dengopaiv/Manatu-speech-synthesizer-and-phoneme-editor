# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Manatu is a KLSYN88-based Klatt formant speech synthesizer written in C++ with Python bindings. It produces human-like speech for NVDA (NonVisual Desktop Access) screen reader. The goal is to exceed DecTalk/Eloquence quality with complete IPA phoneme coverage.

## Build Commands

```bash
# Build everything (requires SCons 3, Visual Studio 2019, x86_64)
scons

# Outputs:
# - speechPlayer.dll (synthesis engine)
# - nvSpeechPlayer_<version>.nvda-addon (NVDA addon package)
```

Version is auto-generated from git revision. Build artifacts go to `build/`.

## Running Tests

```bash
python tests/synthesis/test_engine.py    # Core DSP tests
python tests/phonemes/test_vowels.py     # Vowel formant accuracy
python tests/phonemes/test_consonants.py # Consonant tests
```

Tests generate WAV files to `tests/output/` for auditory inspection (gitignored). There are no automated assertion-based unit tests; quality is verified by listening.

## Architecture

### Signal Flow

```
IPA Text → ipa.py parsing → Frames with 70+ parameters
                                    ↓
Audio ← Soft Limit ← Mix ← Parallel Formants ←── Noise/Burst
                      ↑
              Cascade Formants ← Tracheal ← Spectral Tilt ← LF Glottal Pulse
```

### Key Components

| Component | Files | Purpose |
|-----------|-------|---------|
| Synthesis Engine | `src/speechWaveGenerator.cpp` | Glottal source, ZDF resonators, noise generation |
| Frame System | `src/frame.cpp`, `src/frame.h` | Parameter interpolation (Hermite smoothstep), pitch contours |
| DLL Interface | `src/speechPlayer.cpp` | Public API exported from speechPlayer.dll |
| Python Wrapper | `speechPlayer.py` | ctypes bindings mapping C structs to Python |
| IPA Processing | `ipa.py` | Phoneme parsing, duration/timing, coarticulation, pitch contours |
| Phoneme Data | `data/*.py` | Formant frequencies, bandwidths, voice quality per phoneme |
| Coarticulation | `data/transitions.py` | F2 locus equations by consonant place of articulation |
| NVDA Addon | `nvdaAddon/synthDrivers/nvSpeechPlayer/` | NVDA synth driver packaging |

### Formant Resonators

Uses Zero Delay Feedback (ZDF) topology (Zavalishin 2012) instead of classic IIR:
- 4th-order for F1-F3 (sharper 24 dB/octave peaks)
- 2nd-order for F4-F6
- Smooth parameter modulation without zipper noise
- Anti-resonator mode for nasal zeros
- Implementation: `src/speechWaveGenerator.cpp:146-253` (2nd-order), `603-632` (4th-order)

### Voice Quality (LF Model)

The `lfRd` parameter controls glottal pulse shape (Liljencrants-Fant model):
- `lfRd=0`: No voicing (voiceless consonants)
- `lfRd=1.0`: Modal voice (voiced consonants)
- `lfRd=1.3-1.7`: Vowels (close=1.0, open=1.3-1.5, open-mid=1.5-1.7)
- `lfRd=2.7`: Maximum breathy voice (diacritics only)
- Valid range: 0.3-2.7 (0 means unvoiced)

### Frame Interpolation

Frames use Hermite smoothstep `t²(3-2t)` for smooth transitions between phonemes. Exceptions that step instantly: `burstAmplitude`, `burstDuration`, `preFormantGain`.

## Phoneme Data Structure

Each phoneme in `data/*.py` is a dict with these parameter groups:
- **Cascade formants**: `cf1`-`cf6` (Hz), `cb1`-`cb6` (bandwidth Hz)
- **Voice quality**: `lfRd`, `flutter`, `spectralTilt`, `voiceAmplitude`
- **Noise**: `fricationAmplitude`, `noiseFilterFreq`, `noiseFilterBw`
- **Bursts**: `burstAmplitude`, `burstDuration`
- **Gains**: `preFormantGain`, `outputGain`

Defaults defined in `ipa.py` as `KLSYN88_DEFAULTS`. Coarticulation uses F2 locus equations: `F2_onset = F2_locus + 0.75 * (F2_vowel - F2_locus)`.

## Detailed Documentation

- `docs/SYNTHESIS.md` — Full technical reference for the synthesis engine
- `docs/VISION.md` — Project goals and development phases
- `docs/CHANGELOG.md` — Changes to synthesis and phoneme data
- `data/README.md` — Phoneme parameter documentation and deprecated params

## Development Tools

- `phoneme_editor.py` — Interactive phoneme parameter tuning with live audio
- `conlang_gui.py` / `conlang_gui_wx.py` — GUI synthesizer for testing
- `ipa_keyboard.py` — IPA character input helper
