# NVSpeechPlayer Tests

## Directory Structure

```
tests/
├── synthesis/          # Core synthesis engine tests
│   └── test_engine.py  # DSP quality, basic synthesis
├── phonemes/           # Phoneme quality tests
│   ├── test_vowels.py  # Vowel formant accuracy
│   └── test_consonants.py  # Stops, fricatives, nasals
├── output/             # Generated WAV files (gitignored)
└── README.md
```

## Running Tests

From project root:

```bash
# Run all synthesis tests
python tests/synthesis/test_engine.py

# Run vowel tests
python tests/phonemes/test_vowels.py

# Run consonant tests
python tests/phonemes/test_consonants.py
```

## Output

Test WAV files are saved to `tests/output/` for auditory inspection.
This directory is gitignored.
