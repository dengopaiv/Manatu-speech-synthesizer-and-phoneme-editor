# NVSpeechPlayer Synthesis Changes Log

This document tracks changes to the synthesis engine, phoneme data, and processing pipeline.

## Format
Each entry documents:
- Date and summary
- What changed
- How phonemes are handled differently
- Files modified

---

## [2025-12-12] - Retroflex Consonants (Phase 3)

### Summary
Added 6 retroflex consonants using KLSYN88 parameters from Agrawal & Stevens 1992. These sounds are essential for Hindi, Tamil, and other South Asian languages.

### What Changed
- `data/stops.py`: Added ʈ (voiceless), ɖ (voiced) retroflex stops
- `data/nasals.py`: Added ɳ (retroflex nasal)
- `data/fricatives.py`: Added ʂ (voiceless), ʐ (voiced) retroflex fricatives
- `data/liquids_glides.py`: Added ɭ (retroflex lateral)
- `data/transitions.py`: Added slow transition rate (60ms) for retroflexes

### Key Parameters (Agrawal Table II)
| Sound | F2 | F3 | Key Distinction |
|-------|------|------|-----------------|
| Retroflex | 1800 | 2700 | F2 higher than alveolar (1600) |
| Alveolar | 1600 | 2600 | Reference for comparison |

### How Phonemes Are Handled Differently
- Retroflex consonants use F2=1800 Hz (vs 1600 Hz for alveolars)
- F3 is higher at 2700 Hz for retroflex place coloring
- Transition duration is 60ms (slowest of all stops per Agrawal Table IV)
- Retroflex sibilants (ʂ, ʐ) use noiseFilterFreq=3500 Hz (lower than alveolar s)
- Retroflex lateral (ɭ) has lowered F3=2200 Hz (vs 2880 Hz for alveolar l)

### Reference
Agrawal & Stevens 1992: "Towards Synthesis of Hindi Consonants using KLSYN 88" (ICSLP)

---

## [2025-12-12] - Coarticulation Module (Phase 2)

### Summary
Added context-aware formant transitions using Klatt's locus equation theory. Vowel formants now start at calculated onset positions based on the preceding consonant's place of articulation.

### What Changed
- `data/transitions.py`: NEW - Complete coarticulation module
- `ipa.py`: Added import and integration after `calculatePhonemeTimes()`

### Key Features

**Klatt Locus Equation:**
```
F_onset = F_locus + k * (F_vowel - F_locus)
```
Where k=0.75 (25% undershoot from vowel target)

**F2 Locus Values by Place:**
| Place | F2 Locus (Hz) |
|-------|---------------|
| Bilabial | 900 |
| Labiodental | 1100 |
| Dental | 1400 |
| Alveolar | 1700 |
| Postalveolar | 2000 |
| Retroflex | 1800 |
| Palatal | 2300 |
| Velar | 1500 |
| Uvular | 1200 |

**Transition Durations by Class Pair:**
- Stop → Vowel: 40ms
- Fricative → Vowel: 50ms
- Nasal → Vowel: 35ms
- Vowel → Stop: 50ms
- Vowel → Vowel: 60ms

### How Phonemes Are Handled Differently
- CV transitions: Vowel F2/F3 now start at calculated onset positions
- Example: /pi/ with i.cf2=2500, bilabial locus=900 → onset_cf2=2100
- The S-curve interpolation (Phase 1) smoothly transitions from onset to target
- Handles post-stop aspiration correctly (looks past 'h' to find consonant)
- Vowel classification by frontness/roundness for future context-dependent rules

### Technical Note
The onset values are stored as `_onset_cf2` and `_onset_cf3` in phoneme dictionaries. These inform where the formant transition begins, combined with the smoothstep interpolation for natural-sounding CV transitions.

---

## [2025-12-12] - S-Curve Transition Smoothing

### Summary
Replaced linear parameter interpolation with Hermite smoothstep S-curve for gentler formant transitions.

### What Changed
- `src/utils.h`: Added `smoothstep()` function implementing Hermite interpolation: `t * t * (3.0 - 2.0 * t)`
- `src/utils.h`: Modified `calculateValueAtFadePosition()` to apply smoothstep to fade ratio

### How Phonemes Are Handled Differently
- All parameter transitions now have gentle acceleration at start and deceleration at end
- Formant "sweeps" between phonemes are less audible
- Same fade durations produce perceptually smoother results
- Particularly beneficial for:
  - CV (consonant-vowel) transitions where F2 shifts rapidly
  - Vowel-to-vowel sequences (diphthongs)
  - Stop releases into vowels

### Technical Details
The smoothstep function maps linear interpolation parameter `t` (0 to 1) through an S-curve:
```
                    smoothstep(t)
    1.0 |              ___----
        |          __--
        |       _-'
        |    _-'
        | __'
    0.0 +'------------------
        0.0              1.0
```

This produces zero velocity at both endpoints, eliminating abrupt parameter jumps.

---

## [2025-12-12] - Stop Phoneme Improvements

### Summary
Comprehensive update to stop consonant phoneme data based on Klatt's diffuseness research.

### What Changed
- `data/stops.py`: Updated all stop consonants with improved parameters
- Applied diffuse parallel amplitudes to labials (p, b, m)
- Fixed glottal stop formant values
- Unified g/ɡ Unicode variants

### How Phonemes Are Handled Differently
- Labial stops (p, b) now have diffuse spectral energy spread across formants
- Glottal stop (ʔ) uses appropriate low F1 with controlled bandwidth
- Velar stops use consistent IPA character (ɡ U+0261)

---

## [2025-12-11] - Klatt Table III Parallel Amplitudes

### Summary
Applied original Klatt Table III values for fricative parallel formant amplitudes.

### What Changed
- `data/fricatives.py`: Updated pa1-pa6 values from Klatt 1980 Table III
- Place-specific spectral shaping now matches documented research

### How Phonemes Are Handled Differently
- Fricatives have more accurate spectral envelopes matching their place of articulation
- Alveolar fricatives (s, z) emphasize F4-F5 region
- Palato-alveolar fricatives (ʃ, ʒ) have characteristic mid-frequency energy
- Dental fricatives (θ, ð) show diffuse weak energy

---

## Planned Changes

### Phase 3: Extended Sound Classes
- Retroflex consonants using Agrawal & Stevens 1992 KLSYN88 parameters
- Ejective timing rules (shortened stop + glottal closure)
- Implosive parameter derivation (reversed amplitude curves)
- Prenasalized stop expansion

### Phase 4: Advanced Features
- Click burst generator for non-pulmonic consonants
- Physical modeling approach for click articulation
