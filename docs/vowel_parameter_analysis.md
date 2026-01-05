# NVSpeechPlayer Vowel Parameter Analysis

This document analyzes the current vowel parameters and provides recommendations for improvement.

## Reference: Standard Formant Values (Adult Male, Hz)

Based on Peterson & Barney (1952) and Hillenbrand et al. (1995):

| Vowel | F1 | F2 | F3 | Description |
|-------|-----|------|------|-------------|
| i | 270-310 | 2290-2790 | 3010-3310 | Close front unrounded |
| ɪ | 390-400 | 1990-2100 | 2550-2650 | Near-close front |
| e | 400-480 | 2020-2290 | 2600-2700 | Close-mid front |
| ɛ | 530-580 | 1840-1920 | 2480-2590 | Open-mid front |
| æ | 660-750 | 1720-1850 | 2410-2500 | Near-open front |
| a | 730-850 | 1090-1350 | 2440-2600 | Open front |
| ɑ | 710-770 | 1090-1220 | 2440-2640 | Open back unrounded |
| ɔ | 570-640 | 840-920 | 2410-2680 | Open-mid back rounded |
| o | 450-500 | 830-920 | 2380-2500 | Close-mid back rounded |
| ʊ | 440-470 | 1020-1100 | 2240-2380 | Near-close back rounded |
| u | 300-340 | 870-1020 | 2240-2380 | Close back rounded |
| ə | 500-520 | 1400-1500 | 2400-2500 | Mid central (schwa) |

---

## Current Values vs. Reference

### FRONT VOWELS

#### i (Close front unrounded)
| Param | Current | Reference | Status |
|-------|---------|-----------|--------|
| cf1 | 398 | 270-310 | HIGH - should be ~290 |
| cf2 | 2500 | 2290-2790 | OK |
| cf3 | 3500 | 3010-3310 | HIGH - should be ~3100 |

**Issues:**
- F1 too high (398 vs 290) - vowel sounds less close
- openQuotientShape=1.0 is outlier (most vowels use 0.3-0.5)

#### ɪ (Near-close front)
| Param | Current | Reference | Status |
|-------|---------|-----------|--------|
| cf1 | 360 | 390-400 | SLIGHTLY LOW |
| cf2 | 1800 | 1990-2100 | LOW - should be ~2000 |
| cf3 | 2570 | 2550-2650 | OK |

**Issues:**
- F2 is 200Hz too low - affects diphthong targets

#### e (Close-mid front)
| Param | Current | Reference | Status |
|-------|---------|-----------|--------|
| cf1 | 480 | 400-480 | OK (upper bound) |
| cf2 | 2100 | 2020-2290 | OK |
| cf3 | 2700 | 2600-2700 | OK |

**Status:** GOOD after recent adjustments

#### ɛ (Open-mid front)
| Param | Current | Reference | Status |
|-------|---------|-----------|--------|
| cf1 | 530 | 530-580 | OK |
| cf2 | 1680 | 1840-1920 | LOW - should be ~1880 |
| cf3 | 2500 | 2480-2590 | OK |

**Issues:**
- F2 is 200Hz too low

#### æ (Near-open front)
| Param | Current | Reference | Status |
|-------|---------|-----------|--------|
| cf1 | 1000 | 660-750 | VERY HIGH - should be ~700 |
| cf2 | 1869 | 1720-1850 | SLIGHTLY HIGH |
| cf3 | 2430 | 2410-2500 | OK |

**Issues:**
- F1 drastically too high (1000 vs 700)
- spectralTilt=12 is outlier
- lfRd=2.7 is outlier (most use 0)

#### y (Close front rounded)
| Param | Current | Reference | Status |
|-------|---------|-----------|--------|
| cf1 | 290 | ~280 | OK |
| cf2 | 1900 | ~1900 | OK |
| cf3 | 2098 | ~2100 | OK |

**Issues:**
- openQuotientShape=0.12 is outlier (very low)
- pf1=1000 doesn't match cf1=290 (should match)

---

### BACK VOWELS

#### u (Close back rounded)
| Param | Current | Reference | Status |
|-------|---------|-----------|--------|
| cf1 | 280 | 300-340 | SLIGHTLY LOW |
| cf2 | 700 | 870-1020 | LOW - should be ~900 |
| cf3 | 2300 | 2240-2380 | OK |

**Issues:**
- F2 too low (700 vs 900)
- openQuotientShape=0.0 is extreme outlier
- lfRd=2.7 is outlier
- pf1=540 doesn't match cf1=280

#### ʊ (Near-close back rounded)
| Param | Current | Reference | Status |
|-------|---------|-----------|--------|
| cf1 | 372 | 440-470 | LOW - should be ~450 |
| cf2 | 1047 | 1020-1100 | OK |
| cf3 | 2300 | 2240-2380 | OK |

**Issues:**
- F1 too low (372 vs 450)
- flutter=0.25 is outlier (most use 0.10-0.12)
- lfRd=2.7 is outlier

#### o (Close-mid back rounded)
| Param | Current | Reference | Status |
|-------|---------|-----------|--------|
| cf1 | 465 | 450-500 | OK |
| cf2 | 890 | 830-920 | OK |
| cf3 | 2300 | 2380-2500 | SLIGHTLY LOW |

**Status:** GOOD

#### ɔ (Open-mid back rounded)
| Param | Current | Reference | Status |
|-------|---------|-----------|--------|
| cf1 | 580 | 570-640 | OK |
| cf2 | 880 | 840-920 | OK |
| cf3 | 2550 | 2410-2680 | OK |

**Status:** GOOD after recent adjustments

#### ɑ (Open back unrounded)
| Param | Current | Reference | Status |
|-------|---------|-----------|--------|
| cf1 | 700 | 710-770 | OK |
| cf2 | 1220 | 1090-1220 | OK (upper bound) |
| cf3 | 2600 | 2440-2640 | OK |

**Issues:**
- spectralTilt=13 is high
- flutter=0.0 is extreme low (no natural jitter)
- pf1=1000 doesn't match cf1=700
- Has tracheal resonances enabled (ftpFreq1=700) - may not be needed

---

### CENTRAL VOWELS

#### ə (Mid central - schwa)
| Param | Current | Reference | Status |
|-------|---------|-----------|--------|
| cf1 | 519 | 500-520 | OK |
| cf2 | 1209 | 1400-1500 | LOW - should be ~1450 |
| cf3 | 2100 | 2400-2500 | LOW - should be ~2450 |

**Issues:**
- F2 is 240Hz too low
- F3 is 350Hz too low
- pf2=1400 doesn't match cf2=1209

#### ɨ (Close central unrounded)
| Param | Current | Reference | Status |
|-------|---------|-----------|--------|
| cf1 | 664 | ~300 | VERY HIGH - should be ~300 |
| cf2 | 1268 | ~1600 | LOW |
| cf3 | 2681 | ~2500 | SLIGHTLY HIGH |

**Issues:**
- F1 drastically too high (664 vs ~300)
- spectralTilt=12 is outlier
- lfRd=2.7 is outlier
- Has complex tracheal resonances

#### ʉ (Close central rounded)
| Param | Current | Reference | Status |
|-------|---------|-----------|--------|
| cf1 | 313 | ~320 | OK |
| cf2 | 1217 | ~1500 | LOW |
| cf3 | 2374 | ~2300 | OK |

**Issues:**
- speedQuotient=1.8 is extreme outlier (most use 0.5-1.0)
- spectralTilt=15 is extreme outlier
- lfRd=1.5 is outlier

---

## Voice Quality Parameter Analysis

### Summary Table

| Vowel | glottalOQ | oqShape | speedQ | specTilt | flutter | lfRd |
|-------|-----------|---------|--------|----------|---------|------|
| **Typical** | 0.12 | 0.4-0.5 | 0.5 | 2-5 | 0.10-0.12 | 0 |
| a | 0.3 | 0.5 | 1.0 | 8 | 0.15 | 1.5 |
| i | 0.12 | **1.0** | 0.5 | 0 | 0.12 | 0 |
| æ | 0.12 | **1.0** | 0.5 | **12** | 0.10 | **2.7** |
| y | 0.18 | **0.12** | 0.5 | 3 | 0.10 | 0 |
| u | 0.12 | **0.0** | 0.7 | 5 | 0.12 | **2.7** |
| ʊ | 0.10 | 0.5 | 0.97 | 5 | **0.25** | **2.7** |
| ɑ | 0.12 | **0.0** | 0.5 | **13** | **0.0** | 0 |
| ɨ | 0.12 | 0.7 | 0.95 | **12** | 0.12 | **2.7** |
| ʉ | 0.12 | **0.0** | **1.8** | **15** | 0.12 | 1.5 |
| ɶ | 0.12 | **0.1** | 0.5 | **12** | **0.02** | 0 |
| ɒ | 0.12 | **0.1** | 0.5 | **11** | **0.02** | 0 |

**Bold** = outlier values

### Issues Identified

1. **openQuotientShape inconsistency:**
   - 0.0 (extreme): u, ɑ, ʉ
   - 0.1-0.12 (very low): y, ɶ, ɒ
   - 1.0 (very high): i, æ
   - Most vowels use 0.3-0.5

2. **spectralTilt inconsistency:**
   - Range from 0-15 across vowels
   - Very high (11-15): æ, ɑ, ɶ, ɒ, ɨ, ʉ
   - Very low (0): i
   - This causes dramatic voice quality changes in diphthongs

3. **lfRd (LF model) inconsistency:**
   - Most vowels use 0 (disabled)
   - Outliers use 2.7: æ, u, ʊ, ɨ
   - Creates different voice quality between vowels

4. **flutter inconsistency:**
   - Most use 0.10-0.12
   - ʊ uses 0.25 (very high)
   - ɑ, ɶ, ɒ use 0.0-0.02 (no jitter)

---

## Cascade vs Parallel Formant Mismatches

Several vowels have cascade (cf) and parallel (pf) formants that don't match:

| Vowel | cf1 | pf1 | cf2 | pf2 | Issue |
|-------|-----|-----|-----|-----|-------|
| y | 290 | 1000 | 1900 | 1250 | Major mismatch |
| u | 280 | 540 | 700 | 1100 | Major mismatch |
| ɑ | 700 | 1000 | 1220 | 1220 | pf1 mismatch |
| ə | 519 | 500 | 1209 | 1400 | pf2 mismatch |

These mismatches can cause phase/interference issues in synthesis.

---

## Priority Recommendations

### HIGH PRIORITY (Formant Accuracy)

1. **Fix ɨ (Close central unrounded)**
   - cf1: 664 → 300
   - cf2: 1268 → 1600
   - This vowel is completely wrong

2. **Fix æ (Near-open front)**
   - cf1: 1000 → 700
   - Also normalize voice quality params

3. **Fix i (Close front unrounded)**
   - cf1: 398 → 290

4. **Fix ɪ (Near-close front)** - Important for diphthongs
   - cf2: 1800 → 2000

5. **Fix ə (Schwa)** - Very common vowel
   - cf2: 1209 → 1450
   - cf3: 2100 → 2450

### MEDIUM PRIORITY (Voice Quality Consistency)

6. **Normalize openQuotientShape**
   - Target: 0.4-0.5 for all vowels
   - Fix outliers: u(0.0), ɑ(0.0), ʉ(0.0), i(1.0), æ(1.0)

7. **Normalize spectralTilt**
   - Target: 3-6 for all vowels
   - Fix outliers: æ(12), ɑ(13), ʉ(15), etc.

8. **Normalize lfRd**
   - Target: 0 for all vowels (or consistent non-zero value)
   - Remove 2.7 values from æ, u, ʊ, ɨ

9. **Normalize flutter**
   - Target: 0.10-0.12 for all vowels
   - Fix ʊ(0.25), ɑ(0.0)

### LOW PRIORITY (Cascade/Parallel Matching)

10. **Align parallel formants with cascade**
    - pf1 should equal cf1
    - pf2 should equal cf2
    - Fix mismatches in: y, u, ɑ, ə

---

## Suggested "Normalized" Voice Quality Template

For consistency across all vowels (smooth diphthong transitions):

```python
# Voice quality - normalized for smooth transitions
'glottalOpenQuotient': 0.25,  # Modal voice
'openQuotientShape': 0.5,     # Moderate
'speedQuotient': 0.7,         # Slightly asymmetric
'spectralTilt': 4,            # Slight tilt for naturalness
'flutter': 0.12,              # Natural F0 jitter
'lfRd': 0,                    # Disabled (or 1.0 if preferred)
'diplophonia': 0,             # No creaky voice
```

Individual vowels can deviate slightly for phonetic accuracy, but extreme outliers should be avoided for diphthong smoothness.

---

## Testing Methodology

After making changes, test with:

1. **Individual vowels:** Listen for naturalness
2. **Diphthongs:** aɪ, aʊ, eɪ, oʊ, ɔɪ - check for smooth glides
3. **Minimal pairs:** bit/bet, boot/book, etc.
4. **Full sentences:** Check overall voice quality consistency

```bash
# Test individual vowels
echo "i e ɛ æ a ɑ ɔ o ʊ u ə" > test_vowels.txt
python test_speakIpa.py test_vowels.txt

# Test diphthongs
echo "aɪ aʊ eɪ oʊ ɔɪ" > test_diphthongs.txt
python test_speakIpa.py test_diphthongs.txt
```
