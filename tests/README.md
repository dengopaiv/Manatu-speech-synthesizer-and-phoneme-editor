# Manatu Tests

## Directory Structure

```
tests/
├── synthesis/          # Core synthesis engine tests
│   └── test_engine.py  # DSP quality, basic synthesis
├── phonemes/           # Phoneme quality tests
│   ├── test_vowels.py  # Vowel formant accuracy
│   ├── test_consonants.py  # Stops, fricatives, nasals
│   └── test_vowel_pitch.py # Pitch stability across contours
├── transitions/        # Coarticulation tests
│   └── test_coarticulation.py  # CV transition validation
├── output/             # Generated WAV files (gitignored)
├── conftest.py         # Test utilities and fixtures
└── README.md
```

## Running Tests

From project root (DLL must be built first with `scons`):

```bash
# Run all synthesis tests
python tests/synthesis/test_engine.py

# Run vowel tests
python tests/phonemes/test_vowels.py

# Run consonant tests
python tests/phonemes/test_consonants.py
```

## What Tests Produce

Tests have two layers of output:

### 1. WAV Files (Auditory Inspection)

All tests generate WAV files to `tests/output/` for manual listening. This directory is gitignored. Listen to these files to evaluate naturalness, transitions, and overall quality — aspects that are difficult to capture with automated metrics.

### 2. Spectral Assertions (Automated Checks)

Key tests include programmatic assertions using LPC spectral analysis (`tools/spectral_analysis.py`):

- **Vowel formant accuracy** — F1 within 15% of phoneme data targets
- **Voicing detection** — vowels verified as voiced via Harmonic-to-Noise Ratio (HNR)
- **Formant ordering** — F1 < F2 < F3 for all vowels
- **Cardinal vowel space** — /a/ has highest F1; /i/ and /u/ have lower F1
- **Fricative spectral centroid** — /s/ has higher centroid than /ʃ/
- **Nasal low F1** — nasals verified with F1 < 500 Hz
- **Stop burst presence** — stops show energy spike in CV context
- **Place contrasts** — palatal high F2, uvular low F2, pharyngeal high F1
- **Place minimal pairs** — place-contrasting consonants have distinct F2 values

## Interpreting Results

- **PASS**: Spectral properties match expected ranges
- **FAIL**: A phoneme's measured formants or spectral properties fall outside tolerance. Check the specific assertion message and compare against the phoneme data in `data/*.py`
- **WAV quality**: Even when assertions pass, listen to the output — a phoneme can have correct formants but still sound unnatural due to timing, transitions, or voice quality issues
