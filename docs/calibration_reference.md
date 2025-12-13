# Phoneme Calibration Reference

This document lists acoustic anchor phonemes that serve as calibration landmarks for tuning synthesizer parameters. These sounds have well-documented acoustic properties and form the foundation for deriving parameters for other phonemes.

---

## 1. Corner Vowels (Primary Acoustic Anchors)

The three acoustic vowel triangle corners are the most fundamental calibration points:

| Vowel | Description | F1 (Hz) | F2 (Hz) | F3 (Hz) | Role |
|-------|-------------|---------|---------|---------|------|
| **i** | High front unrounded | 398 | 2500 | 3500 | Maximum F2, minimum F1 |
| **ɑ** | Low back unrounded | 700 | 1220 | 2600 | Maximum F1 |
| **u** | High back rounded | 280 | 700 | 2300 | Minimum F1, minimum F2 |

**Usage**: All other vowels should fall within the triangle defined by these three points in F1×F2 space.

---

## 2. Vowel Height Series (F1 Calibration)

F1 correlates inversely with vowel height. Use these to calibrate the F1 range:

| Height | Vowels | F1 Range (Hz) |
|--------|--------|---------------|
| High | i (398), u (280), ɪ (452), ʊ (314) | 280-450 |
| Mid | e (530), o (465), ə (519), ɛ (730), ɔ (578) | 450-750 |
| Low | a (1000), ɑ (700), æ (860), ɐ (700) | 700-1000 |

**Rule**: Higher vowels → lower F1; lower vowels → higher F1.

---

## 3. Vowel Backness Series (F2 Calibration)

F2 correlates with front/back position. Use these to calibrate the F2 range:

| Position | Vowels | F2 Range (Hz) |
|----------|--------|---------------|
| Front | i (2500), e (2500), ɛ (1680), æ (1700) | 1680-2500 |
| Central | ə (1209), ɐ (1310), ʌ (1090) | 1090-1400 |
| Back | u (700), o (890), ɔ (900), ɑ (1220) | 700-1220 |

**Rule**: Front vowels → high F2; back vowels → low F2.

---

## 4. Rounded vs Unrounded (F2/F3 Lowering)

Lip rounding lowers both F2 and F3:

| Pair | Unrounded F2 | Rounded F2 | Difference |
|------|--------------|------------|------------|
| i vs y | 2500 | 1838 | -662 Hz |
| e vs ø | 2500 | 1700 | -800 Hz |

**Rule**: Rounding lowers F2 by 500-800 Hz and F3 by 200-400 Hz.

---

## 5. Stop Consonant Calibration (F2 Locus by Place)

The F2 locus is where formant transitions "point to" during CV coarticulation:

| Place | F2 Locus (Hz) | Reference Stops | Transition Duration |
|-------|---------------|-----------------|---------------------|
| Bilabial | 900 | p, b | 40 ms |
| Alveolar | 1700 | t, d | 40 ms |
| Retroflex | 1800 | ʈ, ɖ | 60 ms (slow) |
| Velar | 1500 | k, ɡ | 40 ms |

**Usage**: When a stop precedes a vowel, the vowel's F2 starts partway between the locus and its target (Klatt locus equation).

---

## 6. Fricative Calibration (Noise Center Frequency)

Fricative noise spectrum is determined by place of articulation:

| Type | Noise Center (Hz) | Reference Sounds | Spectral Shape |
|------|-------------------|------------------|----------------|
| Labiodental | White/flat | f, v | Weak, diffuse |
| Dental | White/flat | θ, ð | Weak, diffuse |
| Alveolar sibilant | 5500 | s, z | Strong, focused peak |
| Postalveolar sibilant | 3500 | ʃ, ʒ | Lower than alveolar |
| Retroflex sibilant | 3500 | ʂ, ʐ | Similar to postalveolar |
| Glottal | Follows F1 | h | Breathy, vowel-colored |

**Rule**: More anterior constriction → higher noise frequency.

---

## 7. Nasal Calibration (Nasal Zero Frequency)

The nasal zero (anti-resonance) frequency varies by place:

| Place | cfN0 (Hz) | Reference Nasal | Nasal Formant |
|-------|-----------|-----------------|---------------|
| Bilabial | 750 | m | Low zero |
| Alveolar | 1450 | n | Mid zero |
| Retroflex | 1500 | ɳ | Slightly higher |
| Velar | 3000 | ŋ | High zero |

**Usage**: The nasal zero cancels energy near its frequency, creating the characteristic nasal timbre.

---

## 8. Liquid F3 Calibration

Liquids are distinguished primarily by F3:

| Sound | F3 (Hz) | Characteristic | Notes |
|-------|---------|----------------|-------|
| l (lateral) | 2880 | High F3 | Clear lateral quality |
| ɹ (retroflex approx) | 1350 | Very low F3 | American English r |
| ɭ (retroflex lateral) | 2200 | Intermediate | Lower than plain l |

**Rule**: Retroflex articulation lowers F3 dramatically (by 500-1500 Hz).

---

## 9. R-Coloring Reference

Retroflex/rhotic quality is primarily signaled by lowered F3 and F4:

| Parameter | Normal | R-colored | Difference |
|-----------|--------|-----------|------------|
| F3 | 2500-2800 | 1350-1650 | -1000-1200 Hz |
| F4 | 3300 | 2900 | -400 Hz |

**Usage**: To add r-coloring to any vowel, lower F3 toward 1500 Hz.

---

## 10. Voice Quality Anchors

| Parameter | Breathy | Modal | Creaky |
|-----------|---------|-------|--------|
| Open quotient | 0.7+ | 0.5 | 0.3- |
| Aspiration | High | Low | Very low |
| F0 perturbation | Low | Low | High (jitter) |

---

## Quick Lookup Tables

### Vowel F1×F2 Quick Reference
```
        F2 (Hz)
        2500  2000  1500  1000  700
F1 300   i                      u
   400   ɪ                      ʊ
   500   e     ə
   600        ɛ/ʌ          o
   700             ɔ       ɑ
   800        æ
   1000  a
```

### Consonant Place → F2 Locus
```
Bilabial (900) ← Velar (1500) ← Alveolar (1700) ← Retroflex (1800) ← Palatal (2300)
```

### Sibilant Noise Frequency
```
s/z (5500) → ʃ/ʒ (3500) ≈ ʂ/ʐ (3500)
```

---

## References

- Klatt 1980: "Software for a cascade/parallel formant synthesizer"
- Klatt 1987: "Review of text-to-speech conversion for English"
- Agrawal & Stevens 1992: "Towards Synthesis of Hindi Consonants using KLSYN 88"
- Stevens 1998: "Acoustic Phonetics"
