# Getting Started with Manatu

A practical guide to building, using, and contributing to the Manatu speech synthesizer.

## Building

### Prerequisites

- Python 3.7+
- SCons 3 ([scons.org](http://www.scons.org/))
- Visual Studio 2019 Community (C++ desktop workload)

### Build

```bash
scons
```

This produces:
- `speechPlayer.dll` — the synthesis engine
- `nvSpeechPlayer_<version>.nvda-addon` — NVDA addon package (version from git revision)

## Your First Synthesis

Once the DLL is built, you can synthesize speech from Python:

```python
import wave
import struct
import speechPlayer
import ipa

# Create a synthesizer at 44.1 kHz
sp = speechPlayer.SpeechPlayer(44100)

# Generate frames from IPA text
for frame, duration, fade in ipa.generateFramesAndTiming(
    "ˈhɛloʊ",          # IPA for "hello"
    speed=1,             # Normal speed
    basePitch=120,       # F0 in Hz
    inflection=0.5,      # Pitch variation
    clauseType='.',      # Falling intonation
):
    sp.queueFrame(frame, duration, fade)

# Synthesize audio samples
samples = []
while True:
    buf = sp.synthesize(4096)
    if buf is None:
        break
    samples.extend(buf)

# Save to WAV
with wave.open("hello.wav", "w") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(44100)
    wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))
```

### Key parameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `speed` | 1.0 | Speech rate multiplier (higher = faster) |
| `basePitch` | 100 | Fundamental frequency in Hz |
| `inflection` | 0.5 | Pitch variation amount (0 = monotone, 1 = expressive) |
| `clauseType` | `'.'` | Intonation pattern: `.` `,` `?` `!` |
| `formantScale` | 1.0 | Vocal tract scaling (1.17 = female, 1.35 = child) |

## Using the Phoneme Editor

The phoneme editor lets you tune all 47 Klatt synthesis parameters with live audio preview.

```bash
python editor/phoneme_editor.py
```

Requires wxPython (`pip install wxPython`).

### What the tabs do

- **Parameters** — slider controls for every parameter (formants, bandwidths, voice quality, noise, gains)
- **Presets** — browse the full phoneme library and saved presets; click "Load to Current" to load
- **Sequence Testing** — test phonemes in VCV and word contexts
- **View** — read-only display of current parameters as a Python dict
- **File** — export parameter sets as Python dicts or JSON

### Typical workflow

1. Select a phoneme from the Presets tab
2. Load it to the current editor
3. Adjust parameters using the sliders — listen in real time
4. Test in context using the Sequence Testing tab
5. Export or save when satisfied

## Running Tests

```bash
python tests/synthesis/test_engine.py    # Core DSP tests
python tests/phonemes/test_vowels.py     # Vowel formant accuracy
python tests/phonemes/test_consonants.py # Consonant tests
```

### What each test covers

| Test | What it checks |
|------|----------------|
| `test_engine.py` | Basic synthesis pipeline, pitch variation, amplitude envelope, noise generation |
| `test_vowels.py` | Vowel formant accuracy against Hillenbrand (1995), voicing detection, cardinal vowel space |
| `test_consonants.py` | Stop bursts, fricative spectral centroids, nasal F1, place contrasts, voicing contrasts |
| `test_vowel_pitch.py` | Pitch stability across different contour types |
| `test_coarticulation.py` | CV transition and coarticulation validation |

### Interpreting output

- **WAV files** are saved to `tests/output/` — listen to these for naturalness
- **Spectral assertions** print PASS/FAIL with measured vs. expected values
- A phoneme can pass spectral assertions but still sound unnatural — always listen

## Modifying a Phoneme

Phoneme data lives in `data/*.py`, organized by category:

| File | Category |
|------|----------|
| `vowels_front.py` | Front vowels (a, i, e, ɪ, ɛ, æ, y, ʏ, ø, œ, ɶ) |
| `vowels_central.py` | Central vowels (ə, ɜ, ɞ, ɐ, ɨ, ʉ, ɘ, ɵ) |
| `vowels_back.py` | Back vowels (u, ʊ, o, ɔ, ɑ, ɒ, ɯ, ɤ, ʌ) |
| `vowels_rcolored.py` | R-colored vowels (ɝ, ɚ) |
| `vowels_nasalized.py` | Nasalized vowels (ã, ɛ̃, ɔ̃, œ̃) |
| `diphthongs.py` | Diphthongs and triphthongs |
| `stops.py` | Stop consonants (p, b, t, d, k, g, etc.) |
| `fricatives.py` | Fricatives (f, v, s, z, ʃ, ʒ, etc.) |
| `affricates.py` | Affricates (t͡ʃ, d͡ʒ, etc.) |
| `nasals.py` | Nasal consonants (m, n, ŋ, etc.) |
| `liquids_glides.py` | Approximants, trills, taps, glides |

Each phoneme is a Python dict with parameter groups:

- **Cascade formants**: `cf1`-`cf6` (Hz), `cb1`-`cb6` (bandwidth Hz)
- **Voice quality**: `lfRd`, `flutter`, `spectralTilt`, `voiceAmplitude`
- **Noise**: `fricationAmplitude`, `noiseFilterFreq`, `noiseFilterBw`
- **Bursts**: `burstAmplitude`, `burstDuration`
- **Gains**: `preFormantGain`, `outputGain`

See [SYNTHESIS.md](SYNTHESIS.md) for the full parameter reference.

### Verification workflow

1. Edit the phoneme data in the appropriate `data/*.py` file
2. Run the relevant test: `python tests/phonemes/test_vowels.py`
3. Listen to the WAV output in `tests/output/`
4. Use the phoneme editor for interactive fine-tuning

## Adding a New Phoneme

1. **Choose the right file** — pick the data file matching the phoneme category (e.g., `fricatives.py` for a new fricative)

2. **Add the entry** — create a new dict keyed by the IPA symbol:
   ```python
   'ɕ': {  # Voiceless alveolo-palatal fricative
       '_isNasal': False,
       '_isStop': False,
       '_isLiquid': False,
       '_isVowel': False,
       '_isVoiced': False,
       'voiceAmplitude': 0,
       'aspirationAmplitude': 0,
       'cf1': 300,
       'cf2': 2200,
       # ... full formant data
       'fricationAmplitude': 1,
       'noiseFilterFreq': 4500,
       'noiseFilterBw': 1200,
       'lfRd': 0,
   }
   ```

3. **Set classification flags** — these control timing and behavior in `ipa.py`:
   - `_isVowel`, `_isVoiced`, `_isStop`, `_isNasal`, `_isLiquid`, `_isSemivowel`
   - `_isAfricate` (for multi-phase affricates)

4. **Add coarticulation** (if consonant) — add the place of articulation to `data/transitions.py` for F2 locus equation support

5. **Test** — run the consonant tests and listen to the output

## Using Analysis Tools

The `tools/` directory provides scripts for development and phoneme tuning:

| Tool | Purpose | Usage |
|------|---------|-------|
| `spectral_analysis.py` | LPC formant extraction, pitch estimation, HNR | Imported by tests and other tools |
| `phoneme_validator.py` | Check synthesized formants against phoneme data targets | `python tools/phoneme_validator.py` |
| `vowel_autotuner.py` | Iterative vowel formant parameter optimization | `python tools/vowel_autotuner.py` |
| `fricative_autotuner.py` | Noise parameter tuning for fricatives | `python tools/fricative_autotuner.py` |
| `consonant_diagnostic.py` | Spectral/temporal analysis of consonant output | `python tools/consonant_diagnostic.py` |
| `sync_presets.py` | Sync JSON editor presets from Python phoneme data | `python tools/sync_presets.py` |

## NVDA Addon

The build produces an `.nvda-addon` file that can be installed directly into NVDA:

1. Build with `scons`
2. Find `nvSpeechPlayer_<version>.nvda-addon` in the project root
3. Double-click the file or use NVDA's Add-on Manager to install
4. Select "Manatu" as your synthesizer in NVDA settings

Everything needed is packaged in the addon — no extra DLLs or files need to be copied.
