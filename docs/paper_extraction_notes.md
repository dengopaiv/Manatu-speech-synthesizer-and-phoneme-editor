# Paper Extraction Notes

Reference notes for extracting synthesis parameters from academic papers.
Complements `paper_notes.md` (Stevens - Acoustic Phonetics).

---

## Papers to Process

### 1. Hillenbrand et al. (1995)
**Title**: "Acoustic characteristics of American English vowels"
**Source**: J. Acoust. Soc. Am. 97(5), May 1995
**File**: `papers/hillenbrand1995.pdf`

**Key Content**:
- Updated vowel formant data (F1-F4) for 45 men, 48 women, 46 children
- 12 vowels: /i, I, e, E, ae, a, O, o, U, u, V, 3r/
- Vowel durations in /hVd/ context
- F0 measurements
- Spectral change patterns (vowel trajectories)

**Synthesis Relevance**:
- Modern replacement for Peterson & Barney (1952) formant values
- Duration data for inherent vowel lengths
- Dynamic formant trajectories (not just static targets)

**Tables to Extract**:
- Table V: Average durations, F0, F1-F4 for men/women/children
- Table VI: Vowel identification rates
- Figure 9: Spectral change patterns

---

### 2. Klatt (1987)
**Title**: "Review of text-to-speech conversion for English"
**Source**: J. Acoust. Soc. Am. 82(3), September 1987
**File**: `papers/klatt 1987/klatt1987_part*.pdf` (6 parts, 58 pages)

**Key Content**:
- Historical development of formant synthesizers
- Cascade vs parallel formant configurations
- Voicing source models and improvements
- Source-filter theory
- Synthesis-by-rule strategies
- Duration and F0 rules
- Allophonic variations

**Synthesis Relevance**:
- Direct applicability to KLSYN88 implementation
- Voicing source parameters (open quotient, spectral tilt)
- Formant transition rules
- Prosodic control strategies

**Sections to Extract**:
- Section I.A.1-3: Source-filter theory, vocal tract models
- Section I.A.3: Voicing source models (relates to lfRd, spectralTilt, flutter)
- Section I.B: Acoustic properties of phonetic segments
- Section I.C: Segmental synthesis-by-rule programs
- Section I.D: Prosody rules (duration, F0)

---

### 3. Klatt (1980)
**Title**: "Software for a cascade/parallel formant synthesizer"
**Source**: J. Acoust. Soc. Am. 67(3), March 1980
**File**: `papers/klatt 1980/klatt1980_part*.pdf` (3 parts, 25 pages)

**Key Content**:
- Complete 39-parameter specification (Table I)
- Cascade vs parallel formant configuration
- Voicing source waveform (RGP, RGZ filters)
- Parameter ranges and typical values

**Synthesis Relevance**:
- Original KLSYN synthesizer documentation
- Direct parameter specifications for implementation
- Formant frequency ranges for English sounds

**Tables to Extract**:
- Table I: Complete parameter specification with ranges
- Section V: Suggested parameter values by phoneme

---

### 4. Klatt & Klatt (1990)
**Title**: "Analysis, synthesis, and perception of voice quality variations among female and male talkers"
**Source**: J. Acoust. Soc. Am. 87(2), February 1990
**File**: `papers/klatt 1990/klatt1990_part*.pdf` (4 parts, 38 pages)

**Key Content**:
- KLSYN88 synthesizer with KLGLOTT88 voicing source
- Voice quality parameters: OQ, TL, FL, DI, AH
- LF (Liljencrants-Fant) glottal model
- Male vs female voice differences
- Tracheal coupling for breathy voice
- Acoustic correlates of breathiness

**Synthesis Relevance**:
- Updated KLSYN88 implementation details
- Voice quality control parameters
- Gender-specific synthesis settings
- Aspiration and breathiness modeling

**Tables to Extract**:
- Tables XI, XII: Complete KLSYN88 parameter specifications
- Tables II, III: H1-H2 amplitude differences (male/female)
- Table VII: Tracheal pole frequencies
- Figure 10: KLGLOTT88 voicing source model

---

### 5. Ladefoged & Maddieson (1996)
**Title**: "The Sounds of the World's Languages"
**Source**: Blackwell Publishers, 1996
**File**: `papers/ladefoged paged/ladefoged_part*.pdf` (43 parts, ~430 pages)

**Key Content**:
- Chapter 2: Places of Articulation (pages 9-46)
- Chapter 3: Stops - laryngeal settings, airstream mechanisms (pages 47-96)
- Chapter 4: Nasals and Nasalized Consonants (pages 97-136)
- Chapter 5: Fricatives - sibilants, non-sibilants, acoustic differences (pages 137-181)
- Chapter 6: Laterals (pages 182-214)
- Chapter 7: Rhotics - trills, taps, approximants (pages 215-245)
- Chapter 8: Clicks (pages 246-281)
- Chapter 9: Vowels (pages 282-326)
- Chapter 10: Consonant-Vowel Interactions, Secondary Articulations (pages 327-368)

**Synthesis Relevance**:
- Cross-linguistic phonetic data for IPA coverage
- Articulatory descriptions for consonant place contrasts
- Acoustic characteristics distinguishing similar sounds
- Secondary articulation parameters (palatalization, velarization, etc.)

---

## Parameter Mapping Guide

### Mapping Papers to Synthesizer Parameters

| Paper Source | Synthesis Parameter | Frame Field |
|--------------|---------------------|-------------|
| Klatt 1990 Table XII | Open quotient | glottalOpenQuotient |
| Klatt 1990 Table XII | Spectral tilt | spectralTilt |
| Klatt 1990 Table XII | Flutter | flutter |
| Klatt 1990 Table XII | Diplophonia | diplophonia |
| Klatt 1990 Table XII | Aspiration | aspirationAmplitude |
| Klatt 1990 Table XII | Tracheal poles | ftpFreq1, ftpFreq2 |
| Klatt 1990 Tables II,III | H1-H2 difference | (via lfRd) |
| Klatt 1980 Table I | Formants F1-F5 | cf1-cf5 |
| Klatt 1980 Table I | Bandwidths B1-B5 | cb1-cb5 |
| Hillenbrand Table V | Vowel F1-F4 | cf1-cf4 |
| Hillenbrand Table V | Vowel durations | (duration rules) |
| Klatt 1987 Sec. I.A.3 | Voicing source shape | lfRd |
| Klatt 1987 Sec. I.D | Duration rules | (ipa.py rules) |
| Stevens Table 8.5 | Tracheal poles | ftpFreq1, ftpFreq2 |
| Ladefoged Ch. 5 | Fricative spectra | noiseFilterFreq, pa1-pa6 |
| Ladefoged Ch. 4 | Nasal resonances | cfNP, cfN0, cbNP, cbN0 |

---

## Extraction Priorities

### High Priority (Direct Synthesis Application)
1. **Hillenbrand Table V** - Updated vowel formants F1-F4 for all speaker groups
2. **Klatt voicing source** - Parameters for natural voice quality
3. **Ladefoged fricative acoustics** - Place-specific noise filtering

### Medium Priority (Rule Development)
4. **Klatt duration rules** - Systematic duration modifications
5. **Klatt F0 rules** - Intonation contour generation
6. **Ladefoged stop acoustics** - VOT, burst characteristics

### Lower Priority (Extended Coverage)
7. **Ladefoged secondary articulations** - Palatalization, etc.
8. **Ladefoged clicks** - Non-pulmonic consonants
9. **Cross-linguistic vowel systems** - Beyond English

---

## Notes Format Template

When extracting data, use this format:

```markdown
### [Source] - [Topic]

#### Key Data
| Parameter | Value | Notes |
|-----------|-------|-------|

#### Synthesis Relevance
- Direct parameter mapping: `parameterName` = value
- Rule implications: [description]

#### Implementation Notes
- Current implementation: [how it's done now]
- Suggested change: [improvement based on paper]
```

---

## Extraction Status

| Paper | Section/Table | Status | Notes |
|-------|---------------|--------|-------|
| Klatt 1980 | Table I | **Complete** | 39-parameter specification |
| Klatt 1980 | Tables II, III | **Complete** | Vowel & consonant parameters |
| Klatt 1990 | Tables XI, XII | **Complete** | Voice source parameters |
| Klatt 1990 | Tables II, III | **Complete** | H1-H2 male/female |
| Klatt 1990 | Table VII | **Complete** | Tracheal pole frequencies |
| Klatt 1990 | Tables V, VI | **Complete** | Aspiration noise by position |
| Klatt 1990 | Table X | **Complete** | Acoustic-perceptual correlations |
| Klatt 1990 | Tables XIII-XV | **Complete** | Synthesis perception tests |
| Hillenbrand 1995 | Table V | **Complete** | F1-F4 formants, M/W/C |
| Hillenbrand 1995 | Duration data | **Complete** | Vowel lengths, F0 |
| Klatt 1987 | Parts 3-4 | **Complete** | Duration, F0, coarticulation rules |
| Klatt 1987 | Parts 1-2, 5-6 | Pending | History, source, text analysis |
| Ladefoged Ch. 2 | Places | Pending | Articulation |
| Ladefoged Ch. 3 | Stops | **Complete** | VOT categories, ejectives, implosives |
| Ladefoged Ch. 4 | Nasals | **Complete** | Nasal pole/zero by place (Table 4.6) |
| Ladefoged Ch. 5 | Fricatives | **Complete** | Sibilant spectral peaks, non-sibilants |
| Ladefoged Ch. 6 | Laterals | Pending | /l/ variants |
| Ladefoged Ch. 7 | Rhotics | Pending | /r/ variants |
| Ladefoged Ch. 9 | Vowels | Pending | Vowel systems |

---

## Cross-Reference to Existing Notes

The `paper_notes.md` file contains Stevens data for:
- Vowels: Peterson & Barney formants (can compare with Hillenbrand)
- Fricatives: Table 8.1-8.3 amplitude differences
- Nasals: Pole/zero frequencies by place
- Glides: F1 values, transition times
- Liquids: /r/ vs /l/ formant patterns
- Coarticulation: Context effects on schwa

New extractions should complement rather than duplicate this material.

---

## Extracted Data

### Klatt & Klatt (1990) - KLSYN88 Voice Source Parameters

**Source**: J. Acoust. Soc. Am. 87(2), February 1990, Tables XI, XII

#### Voice Source Parameters (Table XII)

| Parameter | Min | Default | Max | Description |
|-----------|-----|---------|-----|-------------|
| F0 | 0 | 1000 | 5000 | Fundamental frequency (tenths of Hz) |
| AV | 0 | 60 | 80 | Amplitude of voicing (dB) |
| OQ | 10 | 50 | 99 | Open quotient (%) |
| SQ | 100 | 200 | 500 | Speed quotient (LF model only, %) |
| TL | 0 | 0 | 41 | Spectral tilt (dB down @ 3 kHz) |
| FL | 0 | 0 | 100 | Flutter (% of max) |
| DI | 0 | 0 | 100 | Diplophonia (% of max) |
| AH | 0 | 0 | 80 | Aspiration amplitude (dB) |

#### Tracheal Coupling Parameters (Table XII)

| Parameter | Min | Default | Max | Description |
|-----------|-----|---------|-----|-------------|
| FTP | 300 | 2150 | 3000 | Tracheal pole frequency (Hz) |
| BTP | 40 | 180 | 1000 | Tracheal pole bandwidth (Hz) |
| FTZ | 300 | 2150 | 3000 | Tracheal zero frequency (Hz) |
| BTZ | 40 | 180 | 2000 | Tracheal zero bandwidth (Hz) |

#### Pitch-Synchronous F1 Variation (Table XII)

| Parameter | Min | Default | Max | Description |
|-----------|-----|---------|-----|-------------|
| DF1 | 0 | 0 | 100 | Delta F1 during open phase (Hz) |
| DB1 | 0 | 0 | 400 | Delta B1 during open phase (Hz) |

#### Synthesis Relevance

**Direct parameter mappings:**
- `glottalOpenQuotient` = OQ (10-99%, default 50%)
- `spectralTilt` = TL (0-41 dB, increase for breathiness)
- `flutter` = FL (0-100%, ~25% typical)
- `diplophonia` = DI (0-100%, 0 for normal voice)
- `aspirationAmplitude` = AH (0-80 dB, increase for breathiness)

**Flutter formula (Eq. 1):**
```
Δf0 = (FL/50)(F0/100)[sin(2π×12.7t) + sin(2π×7.1t) + sin(2π×4.7t)] Hz
```

#### Implementation Notes

- Current implementation uses `lfRd` parameter (LF model)
- Paper shows OQ and TL are primary breathiness controls
- Tracheal coupling adds spectral zeros ~600, 1400, 2200 Hz for breathy voice

---

### Klatt & Klatt (1990) - Male vs Female Voice Quality

**Source**: J. Acoust. Soc. Am. 87(2), February 1990, Tables II, III, VII

#### H1-H2 Amplitude Differences

| Speaker Group | Average | Range |
|---------------|---------|-------|
| Female | 11.9 dB | 8.4-17.1 dB |
| Male | 6.2 dB | 4.6-9.7 dB |
| **Difference** | ~5.7 dB | - |

*H1-H2 correlates with open quotient; higher values = more breathy*

#### Tracheal Pole Frequencies (Table VII median values)

| Pole | Female | Male |
|------|--------|------|
| P1 | ~750 Hz | - |
| P2 | ~1650 Hz | ~1550 Hz |
| P3 | ~2350 Hz | ~2200 Hz |
| P4 | ~3150 Hz | ~3275 Hz |

#### Typical Values - Normal vs Breathy Voice (Female Speaker LK)

| Parameter | Normal | Breathy |
|-----------|--------|---------|
| AV | 60 | 60 |
| OQ | 60 | 80 |
| TL | 8 | 24 |
| AH | 0-40 | 52 |
| DI | 0 | 0 |
| FL | 25 | 25 |

#### Synthesis Relevance

**For female voice synthesis:**
- Increase OQ to ~60-80% (vs ~50% for male)
- Increase TL by ~8-16 dB relative to male
- H1-H2 ~12 dB (vs ~6 dB for male)
- Add slight aspiration noise (AH ~40-52 dB for breathy)

**For male voice synthesis:**
- OQ ~40-50%
- TL ~0-8 dB
- H1-H2 ~6 dB
- Lower aspiration (AH ~0-40 dB)

#### Implementation Notes

- Current `lfRd` parameter maps approximately to OQ
- May need separate male/female voice profiles
- Tracheal coupling parameters could improve breathiness quality

---

### Klatt (1980) - Original 39-Parameter Specification

**Source**: J. Acoust. Soc. Am. 67(3), March 1980, Table I

#### Complete Parameter List (Table I)

**Variable Parameters (V) - Changed during synthesis:**

| # | Sym | Name | Min | Max | Typical |
|---|-----|------|-----|-----|---------|
| 1 | AV | Amplitude of voicing (dB) | 0 | 80 | 0 |
| 2 | AF | Amplitude of frication (dB) | 0 | 80 | 0 |
| 3 | AH | Amplitude of aspiration (dB) | 0 | 80 | 0 |
| 4 | AVS | Amplitude of sinusoidal voicing (dB) | 0 | 80 | 0 |
| 5 | F0 | Fundamental frequency (Hz) | 0 | 500 | 0 |
| 6 | F1 | First formant frequency (Hz) | 150 | 900 | 450 |
| 7 | F2 | Second formant frequency (Hz) | 500 | 2500 | 1450 |
| 8 | F3 | Third formant frequency (Hz) | 1300 | 3500 | 2450 |
| 9 | F4 | Fourth formant frequency (Hz) | 2500 | 4500 | 3300 |
| 10 | FNZ | Nasal zero frequency (Hz) | 200 | 700 | 250 |
| 13 | A2 | Second formant amplitude (dB) | 0 | 80 | 0 |
| 14 | A3 | Third formant amplitude (dB) | 0 | 80 | 0 |
| 15 | A4 | Fourth formant amplitude (dB) | 0 | 80 | 0 |
| 16 | A5 | Fifth formant amplitude (dB) | 0 | 80 | 0 |
| 17 | A6 | Sixth formant amplitude (dB) | 0 | 80 | 0 |
| 18 | AB | Bypass path amplitude (dB) | 0 | 80 | 0 |
| 19 | B1 | First formant bandwidth (Hz) | 40 | 500 | 50 |
| 20 | B2 | Second formant bandwidth (Hz) | 40 | 500 | 70 |
| 21 | B3 | Third formant bandwidth (Hz) | 40 | 500 | 110 |
| 28 | F5 | Fifth formant frequency (Hz) | 3500 | 4900 | 3750 |

**Constant Parameters (C) - Usually fixed:**

| # | Sym | Name | Min | Max | Typical |
|---|-----|------|-----|-----|---------|
| 11 | AN | Nasal formant amplitude (dB) | 0 | 80 | 0 |
| 12 | A1 | First formant amplitude (dB) | 0 | 80 | 0 |
| 22 | SW | Cascade/parallel switch | 0 | 1 | 0 (cascade) |
| 23 | FGP | Glottal resonator 1 freq (Hz) | 0 | 600 | 0 |
| 24 | BGP | Glottal resonator 1 BW (Hz) | 100 | 2000 | 100 |
| 25 | FGZ | Glottal zero frequency (Hz) | 0 | 5000 | 1500 |
| 26 | BGZ | Glottal zero bandwidth (Hz) | 100 | 9000 | 6000 |
| 27 | B4 | Fourth formant bandwidth (Hz) | 100 | 500 | 250 |
| 29 | B5 | Fifth formant bandwidth (Hz) | 150 | 700 | 200 |
| 30 | F6 | Sixth formant frequency (Hz) | 4000 | 4999 | 4900 |
| 31 | B6 | Sixth formant bandwidth (Hz) | 200 | 2000 | 1000 |
| 32 | FNP | Nasal pole frequency (Hz) | 200 | 500 | 250 |
| 33 | BNP | Nasal pole bandwidth (Hz) | 50 | 500 | 100 |
| 34 | BNZ | Nasal zero bandwidth (Hz) | 50 | 500 | 100 |
| 35 | BGS | Glottal resonator 2 BW (Hz) | 100 | 1000 | 200 |
| 36 | SR | Sampling rate | 5000 | 20000 | 10000 |
| 37 | NWS | Samples per update chunk | 1 | 200 | 50 |
| 38 | G0 | Overall gain control (dB) | 0 | 80 | 47 |
| 39 | NFC | Number of cascade formants | 4 | 6 | 5 |

#### Synthesis Relevance

**Direct parameter mappings:**
- `voicingAmplitude` = AV (0-80 dB, ~60 for strong vowel)
- `fricationAmplitude` = AF (0-80 dB, ~60 for strong fricative)
- `aspirationAmplitude` = AH (0-80 dB)
- `cf1`-`cf5` = F1-F5 formant frequencies
- `cb1`-`cb5` = B1-B5 formant bandwidths
- `pa2`-`pa6` = A2-A6 parallel amplitudes
- `cfNP`, `cfNZ` = FNP, FNZ nasal pole/zero frequencies

**Key design notes:**
- Cascade configuration for sonorants (formant amplitudes automatic)
- Parallel configuration for fricatives (explicit amplitude control)
- Parameter update rate: 5 ms (200 Hz)
- Default sampling rate: 10000 Hz (5 kHz bandwidth)
- 4-6 formants in cascade depending on vocal tract length

#### Implementation Notes

- Current implementation uses similar cascade/parallel hybrid
- Voicing source uses RGP (low-pass) and RGZ (antiresonator) to shape glottal pulse
- Quasi-sinusoidal voicing (AVS) for voiced fricatives and voicebars
- Frication noise is amplitude-modulated by voicing when both active

---

### Hillenbrand et al. (1995) - American English Vowel Formants

**Source**: J. Acoust. Soc. Am. 97(5), May 1995, Table V
**Speakers**: 45 men (M), 48 women (W), 46 children ages 10-12 (C)
**Context**: /hVd/ syllables (heed, hid, hayed, head, had, hod, hawed, hoed, hood, who'd, hud, heard)

#### Vowel Duration (ms)

| Vowel | IPA | M | W | C |
|-------|-----|-----|-----|-----|
| heed | /i/ | 243 | 306 | 297 |
| hid | /ɪ/ | 192 | 237 | 248 |
| hayed | /e/ | 267 | 320 | 314 |
| head | /ɛ/ | 189 | 254 | 235 |
| had | /æ/ | 278 | 332 | 322 |
| hod | /ɑ/ | 267 | 323 | 311 |
| hawed | /ɔ/ | 283 | 353 | 319 |
| hoed | /o/ | 265 | 326 | 310 |
| hood | /ʊ/ | 192 | 249 | 247 |
| who'd | /u/ | 237 | 303 | 278 |
| hud | /ʌ/ | 188 | 226 | 234 |
| heard | /ɝ/ | 263 | 321 | 307 |

#### Fundamental Frequency F0 (Hz)

| Vowel | IPA | M | W | C |
|-------|-----|-----|-----|-----|
| heed | /i/ | 138 | 227 | 246 |
| hid | /ɪ/ | 135 | 224 | 241 |
| hayed | /e/ | 129 | 219 | 237 |
| head | /ɛ/ | 127 | 214 | 230 |
| had | /æ/ | 123 | 215 | 228 |
| hod | /ɑ/ | 123 | 215 | 229 |
| hawed | /ɔ/ | 121 | 210 | 225 |
| hoed | /o/ | 129 | 217 | 236 |
| hood | /ʊ/ | 133 | 230 | 243 |
| who'd | /u/ | 143 | 235 | 249 |
| hud | /ʌ/ | 133 | 218 | 236 |
| heard | /ɝ/ | 130 | 217 | 237 |

#### Formant Frequencies F1-F4 (Hz) - Men

| Vowel | IPA | F1 | F2 | F3 | F4 |
|-------|-----|-----|------|------|------|
| heed | /i/ | 342 | 2322 | 3000 | 3657 |
| hid | /ɪ/ | 427 | 2034 | 2684 | 3618 |
| hayed | /e/ | 476 | 2089 | 2691 | 3649 |
| head | /ɛ/ | 580 | 1799 | 2605 | 3677 |
| had | /æ/ | 588 | 1952 | 2601 | 3624 |
| hod | /ɑ/ | 768 | 1333 | 2522 | 3687 |
| hawed | /ɔ/ | 652 | 997 | 2538 | 3486 |
| hoed | /o/ | 497 | 910 | 2459 | 3384 |
| hood | /ʊ/ | 469 | 1122 | 2434 | 3400 |
| who'd | /u/ | 378 | 997 | 2343 | 3357 |
| hud | /ʌ/ | 623 | 1200 | 2550 | 3557 |
| heard | /ɝ/ | 474 | 1379 | 1710 | 3334 |

#### Formant Frequencies F1-F4 (Hz) - Women

| Vowel | IPA | F1 | F2 | F3 | F4 |
|-------|-----|-----|------|------|------|
| heed | /i/ | 437 | 2761 | 3372 | 4352 |
| hid | /ɪ/ | 483 | 2365 | 3053 | 4334 |
| hayed | /e/ | 536 | 2530 | 3047 | 4319 |
| head | /ɛ/ | 731 | 2058 | 2979 | 4294 |
| had | /æ/ | 669 | 2349 | 2972 | 4290 |
| hod | /ɑ/ | 936 | 1551 | 2815 | 4299 |
| hawed | /ɔ/ | 781 | 1136 | 2824 | 3923 |
| hoed | /o/ | 555 | 1035 | 2828 | 3927 |
| hood | /ʊ/ | 519 | 1225 | 2827 | 4052 |
| who'd | /u/ | 459 | 1105 | 2735 | 4115 |
| hud | /ʌ/ | 753 | 1426 | 2933 | 4092 |
| heard | /ɝ/ | 523 | 1588 | 1929 | 3914 |

#### Formant Frequencies F1-F4 (Hz) - Children

| Vowel | IPA | F1 | F2 | F3 | F4 |
|-------|-----|-----|------|------|------|
| heed | /i/ | 452 | 3081 | 3702 | 4572 |
| hid | /ɪ/ | 511 | 2552 | 3403 | 4575 |
| hayed | /e/ | 564 | 2656 | 3323 | 4422 |
| head | /ɛ/ | 749 | 2267 | 3310 | 4671 |
| had | /æ/ | 717 | 2501 | 3289 | 4409 |
| hod | /ɑ/ | 1002 | 1688 | 2950 | 4307 |
| hawed | /ɔ/ | 803 | 1210 | 2982 | 3919 |
| hoed | /o/ | 597 | 1137 | 2987 | 4167 |
| hood | /ʊ/ | 568 | 1490 | 3072 | 4328 |
| who'd | /u/ | 494 | 1345 | 2988 | 4276 |
| hud | /ʌ/ | 749 | 1546 | 3145 | 4320 |
| heard | /ɝ/ | 586 | 1719 | 2143 | 3788 |

#### Synthesis Relevance

**Direct parameter mappings (using Men's averages for adult male voice):**
- `cf1` = F1 values (342-768 Hz range)
- `cf2` = F2 values (910-2322 Hz range)
- `cf3` = F3 values (1710-3000 Hz range)
- `cf4` = F4 values (3334-3687 Hz range)

**Key observations:**
- /ɝ/ (r-colored schwa) has uniquely low F3 (~1710 Hz men, ~1929 Hz women)
- Front vowels (/i, ɪ, e, ɛ, æ/) have high F2 (1800-2300 Hz)
- Back vowels (/ɑ, ɔ, o, ʊ, u/) have low F2 (900-1400 Hz)
- Duration varies 188-283 ms for men, longer for women/children

#### Autocalibration Notes

- Compare synthesized F1-F4 against these targets
- Acceptable tolerance: ±5% of formant frequency
- Note: Data from Michigan dialect speakers (1995)
- Women's formants ~15-20% higher than men's
- Children's formants ~20-30% higher than men's

---

### Klatt (1980) - Phoneme Synthesis Values (Section V)

**Source**: J. Acoust. Soc. Am. 67(3), March 1980, Tables II and III
**Context**: Parameter values for English consonants before front vowels

#### Table II - Vowel Parameters

Note: Where two values are given (onset/offset), the vowel is diphthongized or has a schwa-like offglide.

| Vowel | IPA | F1 | F2 | F3 | B1 | B2 | B3 |
|-------|-----|-----|------|------|-----|-----|-----|
| [iʸ] | /i/ | 310→290 | 2020→2070 | 2960→2960 | 45→60 | 200 | 400 |
| [Iᵊ] | /ɪ/ | 400→470 | 1800→1600 | 2570→2600 | 50 | 100 | 140 |
| [eʸ] | /e/ | 480→330 | 1720→2020 | 2520→2600 | 70→55 | 100 | 200 |
| [eᵊ] | /ɛ/ | 530→620 | 1680→1530 | 2500→2530 | 60 | 90 | 200 |
| [æᵊ] | /æ/ | 620→650 | 1660→1490 | 2430→2470 | 70 | 150→100 | 320 |
| [a] | /ɑ/ | 700 | 1220 | 2600 | 130 | 70 | 160 |
| [ɔᵊ] | /ɔ/ | 600→630 | 990→1040 | 2570→2600 | 90 | 100 | 80 |
| [ʌ] | /ʌ/ | 620 | 1220 | 2550 | 80 | 50 | 140 |
| [oʷ] | /o/ | 540→450 | 1100→900 | 2300 | 80 | 70 | 70 |
| [uᵊ] | /ʊ/ | 450→500 | 1100→1180 | 2350→2390 | 80 | 100 | 80 |
| [uʷ] | /u/ | 350→320 | 1250→900 | 2200 | 65 | 110 | 140 |
| [ɝ] | /ɝ/ | 470→420 | 1270→1310 | 1540 | 100 | 60 | 110 |
| [aʸ] | /aɪ/ | 660→400 | 1200→1880 | 2550→2500 | 100→70 | 70→100 | 200 |
| [aᵘ] | /aʊ/ | 640→420 | 1230→940 | 2550→2350 | 80 | 70 | 140→80 |
| [oʸ] | /ɔɪ/ | 550→360 | 960→1820 | 2400→2450 | 80→60 | 50 | 130→160 |

#### Table III - Consonant Parameters (Before Front Vowels)

**Source Amplitudes (for reference):**
- Voiceless fricatives: AF=60, AV=0, AVS=0
- Voiced fricatives: AF=50, AV=47, AVS=47
- Voiced plosives: Lower F1, smaller B1 due to voicing
- Sonorant amplitude: AV ~10 dB less than adjacent vowel

##### Sonorant Consonants

| Sound | IPA | F1 | F2 | F3 | B1 | B2 | B3 |
|-------|-----|-----|------|------|-----|-----|-----|
| [w] | /w/ | 290 | 610 | 2150 | 50 | 80 | 60 |
| [y] | /j/ | 260 | 2070 | 3020 | 40 | 250 | 500 |
| [r] | /ɹ/ | 310 | 1060 | 1380 | 70 | 100 | 120 |
| [l] | /l/ | 310 | 1050 | 2880 | 50 | 100 | 280 |

**Notes:**
- [h] is not shown; synthesize using following vowel's formants with B1~300 Hz, aspiration instead of voicing
- Sonorant formant values serve as "loci" for CV transitions
- [r] has characteristically low F3 (~1380 Hz)

##### Fricatives

| Sound | IPA | F1 | F2 | F3 | B1 | B2 | B3 | A2 | A3 | A4 | A5 | A6 | AB |
|-------|-----|-----|------|------|-----|-----|-----|----|----|----|----|----|----|
| [f] | /f/ | 340 | 1100 | 2080 | 200 | 120 | 150 | 0 | 0 | 0 | 0 | 0 | 57 |
| [v] | /v/ | 220 | 1100 | 2080 | 60 | 90 | 120 | 0 | 0 | 0 | 0 | 0 | 57 |
| [θ] | /θ/ | 320 | 1290 | 2540 | 200 | 90 | 200 | 0 | 0 | 0 | 0 | 28 | 48 |
| [ð] | /ð/ | 270 | 1290 | 2540 | 60 | 80 | 170 | 0 | 0 | 0 | 0 | 28 | 48 |
| [s] | /s/ | 320 | 1390 | 2530 | 200 | 80 | 200 | 0 | 0 | 0 | 0 | 52 | 0 |
| [z] | /z/ | 240 | 1390 | 2530 | 70 | 60 | 180 | 0 | 0 | 0 | 0 | 52 | 0 |
| [ʃ] | /ʃ/ | 300 | 1840 | 2750 | 200 | 100 | 300 | 0 | 57 | 48 | 48 | 46 | 0 |

**Notes on Parallel Amplitude (A2-A6, AB):**
- AB (bypass) used for labiodentals [f,v] and interdentals [θ,ð] - flat spectrum
- A6 (F6~4900 Hz) excited for sibilants [s,z] - very high frequency noise
- A3-A5 excited for postalveolar [ʃ] - mid-high frequency noise
- A2 is 0 for all fricatives before front vowels (but ~60 for velars before back vowels)

##### Affricates

| Sound | IPA | F1 | F2 | F3 | B1 | B2 | B3 | A2 | A3 | A4 | A5 | A6 | AB |
|-------|-----|-----|------|------|-----|-----|-----|----|----|----|----|----|----|
| [tʃ] | /tʃ/ | 350 | 1800 | 2820 | 200 | 90 | 300 | 0 | 44 | 60 | 53 | 53 | 0 |
| [dʒ] | /dʒ/ | 260 | 1800 | 2820 | 60 | 80 | 270 | 0 | 44 | 60 | 53 | 53 | 0 |

**Notes:**
- Values refer to fricative portion of affricate
- Burst portion similar to corresponding stop [t] or [d]

##### Plosive Bursts

| Sound | IPA | F1 | F2 | F3 | B1 | B2 | B3 | A2 | A3 | A4 | A5 | A6 | AB |
|-------|-----|-----|------|------|-----|-----|-----|----|----|----|----|----|----|
| [p] | /p/ | 400 | 1100 | 2150 | 300 | 150 | 220 | 0 | 0 | 0 | 0 | 0 | 63 |
| [b] | /b/ | 200 | 1100 | 2150 | 60 | 110 | 130 | 0 | 0 | 0 | 0 | 0 | 63 |
| [t] | /t/ | 400 | 1600 | 2600 | 300 | 120 | 250 | 0 | 30 | 45 | 57 | 63 | 0 |
| [d] | /d/ | 200 | 1600 | 2600 | 60 | 100 | 170 | 0 | 47 | 60 | 62 | 60 | 0 |
| [k] | /k/ | 300 | 1990 | 2850 | 250 | 160 | 330 | 0 | 53 | 43 | 45 | 45 | 0 |
| [g] | /g/ | 200 | 1990 | 2850 | 60 | 150 | 280 | 0 | 53 | 43 | 45 | 45 | 0 |

**Notes:**
- F1 higher, B1 larger when glottis is open (voiceless stops)
- Bilabials [p,b]: Low-frequency burst, bypass path excited (flat spectrum)
- Alveolars [t,d]: Mid-high frequency burst, A3-A6 excited
- Velars [k,g]: Front cavity resonance, A3-A5 excited
- Formant values serve as virtual loci for transitions

##### Nasal Consonants

| Sound | IPA | FNP | FNZ | F1 | F2 | F3 | B1 | B2 | B3 |
|-------|-----|-----|-----|-----|------|------|-----|-----|-----|
| [m] | /m/ | 270 | 450 | 480 | 1270 | 2130 | 40 | 200 | 200 |
| [n] | /n/ | 270 | 450 | 480 | 1340 | 2470 | 40 | 300 | 300 |

**Notes:**
- FNP (nasal pole) fixed at ~270 Hz for all nasals
- FNZ (nasal zero) controls vowel nasalization - increase above 270 Hz during nasals
- F2/F3 differences distinguish [m] from [n] place
- Vowel nasalization: increase F1 ~100 Hz, set FNZ = average of new F1 and 270 Hz
- [ŋ] not shown; similar to [n] but with velar F2/F3 loci

#### Synthesis Relevance

**Direct parameter mappings to phoneme editor:**
- `cf1`-`cf3` = F1-F3 formant frequencies (Hz)
- `cb1`-`cb3` = B1-B3 formant bandwidths (Hz)
- `pa2`-`pa6` = A2-A6 parallel amplitudes (dB)
- `parallelBypass` = AB bypass amplitude (dB)
- `cfNP` = FNP nasal pole frequency (Hz)
- `cfNZ` = FNZ nasal zero frequency (Hz)

**Key synthesis principles from Klatt 1980:**
1. Cascade configuration for sonorants (formant amplitudes calculated automatically)
2. Parallel configuration for fricatives/bursts (explicit amplitude control via A2-A6, AB)
3. Voiceless sounds: higher F1 (~300-400 Hz), wider B1 (~200-300 Hz)
4. Voiced obstruents: lower F1 (~200-270 Hz), narrower B1 (~60-70 Hz)
5. Formant values serve as "loci" - actual transitions interpolate toward vowel targets

#### Comparison with Hillenbrand 1995

| Vowel | Klatt F1 | Hillenbrand F1 | Klatt F2 | Hillenbrand F2 |
|-------|----------|----------------|----------|----------------|
| /i/ | 310 | 342 | 2020 | 2322 |
| /ɪ/ | 400 | 427 | 1800 | 2034 |
| /ɛ/ | 530 | 580 | 1680 | 1799 |
| /æ/ | 620 | 588 | 1660 | 1952 |
| /ɑ/ | 700 | 768 | 1220 | 1333 |
| /ʌ/ | 620 | 623 | 1220 | 1200 |
| /u/ | 350 | 378 | 1250 | 997 |
| /ɝ/ | 470 | 474 | 1270 | 1379 |

**Note**: Klatt values are from a single speaker (the author); Hillenbrand values are averages of 45 men. General agreement is good, but individual variation exists.

---

### Klatt (1987) - TTS Synthesis Rules

**Source**: J. Acoust. Soc. Am. 82(3), September 1987 (58 pages)
**Context**: Comprehensive review of text-to-speech conversion for English

#### Table I - Physical and Subjective Components of Prosody

| Physical Quantity | Nearest Subjective Attributes |
|-------------------|------------------------------|
| Intensity pattern | syllabic structure, vocal effort, stress |
| Duration pattern | speaking rate, rhythm, stress, emphasis, syntactic structure |
| F0 pattern | intonation, stress, emphasis, gender, vocal tract length, psychological state, attitude |

#### Table II - Duration Rules (Klatt 1979a)

**Duration Model Formula:**
```
DUR = MINDUR + (INHDUR - MINDUR) × PRCNT / 100
```
Where:
- INHDUR = inherent duration of segment (ms)
- MINDUR = minimum duration if stressed
- PRCNT = percentage shortening from rules below

**11 Duration Rules:**

1. **PAUSE INSERTION**: Insert brief pause before each sentence-internal main clause and at boundaries delimited by orthographic comma.

2. **CLAUSE-FINAL LENGTHENING**: The vowel or syllabic consonant in the syllable just before a pause is lengthened. Any consonants in the rhyme (between this vowel and pause) are also lengthened.

3. **PHRASE-FINAL LENGTHENING**: Syllabic segments (vowels and syllabic consonants) are lengthened if in a phrase-final syllable. Durational increases at NP/VP boundary more likely in complex NP.

4. **NON-WORD-FINAL SHORTENING**: Syllabic segments are shortened slightly if not in a word-final syllable.

5. **POLYSYLLABIC SHORTENING**: Syllabic segments in a polysyllabic word are shortened slightly.

6. **NON-INITIAL-CONSONANT SHORTENING**: Consonants in non-word-initial position are shortened.

7. **UNSTRESSED SHORTENING**: Unstressed segments are shorter and more compressible than stressed segments.

8. **LENGTHENING FOR EMPHASIS**: An emphasized vowel is significantly lengthened.

9. **POSTVOCALIC CONTEXT OF VOWELS**: Vowel shortened if following consonant (in same word) is voiceless. Effects greatest at phrase/clause boundaries.

10. **SHORTENING IN CLUSTERS**: Segments shortened in consonant-consonant sequences (disregarding word boundaries, but not across phrase boundaries).

11. **LENGTHENING DUE TO PLOSIVE ASPIRATION**: A stressed vowel or sonorant preceded by a voiceless plosive is lengthened.

#### F0 Contour Generation Rules

**Intonation Tunes (Clause-Final):**
- **Falling**: Statement ending
- **Rising**: Question ending
- **Fall-Rise**: Continuation rise

**Hat Pattern Model:**
- Intonation rises on first stressed syllable of phrase
- Remains high until final stressed syllable
- Falls dramatically (statement) or fall-rises (continuation)

**F0 Generation via Impulse/Step Commands (Öhman 1967):**
- Step commands: baseline declination, hat rise/fall
- Impulse commands: stress-related local rises
- Output filtered through low-pass smoothing filter

**Declination:**
- F0 starts high at sentence beginning
- Falls gradually throughout sentence
- Reset higher at paragraph boundaries

**Stress-Related F0:**
- Local rises above phrasal hat top
- Magnitude depends on phrasal position (reduced over phrase)
- Rise timing relative to stressed vowel affects perception

**Segmental Perturbations:**
- F0 higher near voiceless consonants
- F0 higher on high vowels (reduced in sentence contexts)

#### Allophonic Variation Rules

**Key Allophone Substitutions (Table III):**

| Allophone | Symbol | Description |
|-----------|--------|-------------|
| ɾ | DX | flap (intervocalic /t,d/) |
| ʔ | Q | glottal stop |
| tˀ | TX | glottalized t |
| ɹ̩ | RX | postvocalic r |
| l̩ | LX | postvocalic l |
| iɹ | IR | vowel in "beer" |
| ɛɹ | ER | vowel in "bear" |
| ɑɹ | AR | vowel in "bar" |
| ɔɹ | OR | vowel in "boar" |
| ʊɹ | UR | vowel in "poor" |

**Word Boundary Cues:**
- Laryngealized vowel onset signals word-initial vowel
- Aspirated [p,t,k] becomes unaspirated after same-word /s/ ("the spot" vs "this pot")
- Initial vs final allophone of /r/ or /l/ depends on word boundary
- Vowel longer in open syllable, shorter before voiceless word-final consonant
- Word-final [t,d] flapped or glottalized before word beginning with stressed vowel

**Voice Onset Time (VOT) Rules (Klatt 1975b):**
- VOT ~50 ms for /t/ typically
- ~10 ms longer in word-initial position
- Shorter in prestressed word-medial positions
- Shorter if following vowel is unstressed
- Longer with following sonorant consonant
- Shorter after preceding /s/
- Shorter if preceded by voiced segment

**Palatalization:**
- Word-final alveolar consonants palatalize if next word begins with palatal
- "did you" → [dɪdʒu], "this shoe" → [ðɪʃʃu]

#### Coarticulation Rules

**VCV Formant Interactions (Öhman 1966):**
- Formant transitions for CV depend on preceding vowel
- Can be modeled as additive perturbations:
  1. Underlying vowel target
  2. Transition from prevocalic consonant
  3. Transition from postvocalic consonant

**Vowel Space in Sentences:**
- Vowel space shrinks in sentence context vs isolation
- May neutralize toward schwa or accede to consonant demands (Lindblom 1963)

#### Synthesis Relevance

**Duration parameters:**
- Each phoneme needs INHDUR (inherent duration)
- Each phoneme needs MINDUR (minimum duration)
- Rules apply percentage modifications

**F0 parameters:**
- `voicePitch` = baseline F0
- `voicePitchDelta` = F0 change over segment
- Stress impulses add local F0 rises

**Timing considerations:**
- Phrase-final lengthening: ~1.3-1.5× normal duration
- Unstressed shortening: ~0.6-0.8× normal duration
- Cluster shortening: varies by context

#### Implementation Notes

Current NVSpeechPlayer could implement:
1. Inherent durations per phoneme class
2. Simple phrase-final lengthening
3. Unstressed vowel shortening
4. Basic F0 declination
5. Stress-related F0 rises

---

### Ladefoged & Maddieson (1996) - Consonant Acoustics

**Source**: "The Sounds of the World's Languages", Blackwell Publishers, 1996
**Chapters**: 3 (Stops), 4 (Nasals), 5 (Fricatives)

#### Chapter 3 - Stops

**Voice Onset Time (VOT) Categories:**

| Category | Description | VOT Range | Examples |
|----------|-------------|-----------|----------|
| Voiced | Vocal fold vibration during closure | -125 to -75 ms | French /b,d,g/ |
| Voiceless unaspirated | Short-lag VOT | 0-25 ms | Spanish /p,t,k/ |
| Voiceless aspirated | Long-lag VOT | 50-100+ ms | English /p,t,k/ |

**VOT by Place of Articulation (general tendency):**
- Bilabials: shortest VOT
- Alveolars: intermediate VOT
- Velars: longest VOT

**Glottal Stops:**
- Complete cessation of voicing
- Irregular voice onset ("creaky voice") at release
- F0 perturbation (lowering) on adjacent vowels

**Ejectives:**
- Glottalic egressive airstream
- Higher intensity burst than pulmonic stops
- Longer closure duration
- VOT similar to voiceless unaspirated stops

**Implosives:**
- Glottalic ingressive airstream
- Maintain voicing during closure
- F0 may rise during closure (larynx lowering)
- Lower intensity burst

#### Chapter 4 - Nasals

**Acoustic Structure of Voiced Nasals:**

The nasal acoustic spectrum shows:
1. **Nasal murmur**: Low-frequency resonance (~200-300 Hz)
2. **Anti-resonance (zero)**: From closed oral cavity
3. **Higher poles**: From nasal tract configuration

**Table 4.6 - Catalan Nasal Resonances (Recasens 1983):**

| Place | IPA | Resonance Mean (Hz) | Zero Mean (Hz) |
|-------|-----|---------------------|----------------|
| Alveolar | [n] | 1403 | 167 |
| Retroflex | [ɳ] | 1634 | 201 |
| Palato-alveolar | [ɲ] | 2094 | 233 |

**Synthesis Relevance:**
- `cfNP` (nasal pole): ~270 Hz for nasal murmur (consistent across places)
- `cfNZ` (nasal zero): varies by place (higher = more back constriction)
- Higher oral cavity resonance correlates with more forward place

**Nasal Murmur Characteristics:**
- Fixed low-frequency pole around 250-300 Hz (pharyngo-nasal coupling)
- Variable zero from oral side cavity (determines place perception)
- Higher formants (F2, F3) provide secondary place cues

**Place Distinctions:**

| Nasal | Place | Oral Cavity | Zero Position |
|-------|-------|-------------|---------------|
| [m] | bilabial | largest | lowest (~1000 Hz) |
| [n] | alveolar | medium | medium (~1400 Hz) |
| [ŋ] | velar | smallest | highest (~2000+ Hz) |

#### Chapter 5 - Fricatives

**Non-Sibilant vs Sibilant Distinction:**

| Type | Place Examples | Spectral Character | Energy Level |
|------|----------------|-------------------|--------------|
| Non-sibilant | [f,θ,x,h] | Flat/diffuse spectrum | Low intensity |
| Sibilant | [s,ʃ,ɕ,ʂ] | Peaked spectrum | High intensity |

**Non-Sibilant Fricatives (Anterior):**

| Sound | IPA | Place | Spectral Characteristics |
|-------|-----|-------|-------------------------|
| Labiodental | [f,v] | Lips-teeth | Very flat spectrum, low intensity, bypass path |
| Dental | [θ,ð] | Tongue-teeth | Flat spectrum, slightly higher than [f] |

**Sibilant Fricatives - Spectral Peak Frequencies:**

The key acoustic cue is the lower cut-off frequency of noise energy, which gets lower as the front cavity gets larger.

| Sound | IPA | Place | Spectral Peak | Notes |
|-------|-----|-------|---------------|-------|
| Alveolar | [s] | Tongue-alveolar ridge | ~5000 Hz | Small front cavity, highest frequency |
| Alveolo-palatal | [ɕ] | Tongue-hard palate | ~2500 Hz (unrounded) | Medium front cavity |
| Palato-alveolar | [ʃ] | Tongue-postalveolar | ~2000 Hz | Larger front cavity |
| Retroflex | [ʂ] | Tongue tip curled back | ~2000 Hz | Large sublingual cavity |

**Place Distinction Rule:**
- Smaller front cavity → higher spectral peak
- Larger front cavity → lower spectral peak
- Lip rounding → lower spectral peak (adds front cavity volume)

**Posterior Non-Sibilant Fricatives:**

| Sound | IPA | Place | Characteristics |
|-------|-----|-------|-----------------|
| Palatal | [ç,ʝ] | Tongue-hard palate | Weak frication, high F2-F3 |
| Velar | [x,ɣ] | Tongue-velum | Variable, back vowel lowers formants |
| Uvular | [χ,ʁ] | Tongue-uvula | Very back constriction |
| Pharyngeal | [ħ,ʕ] | Tongue root-pharynx | F1 > 1000 Hz characteristic |

**Voiced vs Voiceless Fricatives:**
- Voiceless: noise only, longer duration
- Voiced: noise + voicebar, shorter duration, lower noise amplitude

#### Synthesis Parameter Mapping

**Fricative Noise Filtering (`noiseFilterFreq`, `noiseFilterBW`):**

| Fricative Type | noiseFilterFreq | noiseFilterBW | Notes |
|----------------|-----------------|---------------|-------|
| [f,v] labiodental | bypass | - | Use `parallelBypass` |
| [θ,ð] dental | bypass | - | Use `parallelBypass` |
| [s,z] alveolar | 5000 Hz | 2000 Hz | Narrow high-frequency peak |
| [ʃ,ʒ] palato-alveolar | 2500 Hz | 1500 Hz | Broader mid-high peak |
| [ɕ,ʑ] alveolo-palatal | 3000 Hz | 1500 Hz | Between [s] and [ʃ] |
| [ʂ,ʐ] retroflex | 2000 Hz | 1500 Hz | Similar to [ʃ] |
| [x,ɣ] velar | 1500-2500 Hz | 1000 Hz | Depends on vowel context |
| [h] glottal | following vowel | wide | Formant structure of vowel |

**Nasal Parameters:**

| Parameter | Value | Source |
|-----------|-------|--------|
| `cfNP` | 250-300 Hz | Fixed nasal murmur pole |
| `cfNZ` [m] | 1000 Hz | Bilabial oral cavity zero |
| `cfNZ` [n] | 1400 Hz | Alveolar oral cavity zero |
| `cfNZ` [ŋ] | 2000+ Hz | Velar oral cavity zero |
| `cbNP` | 80-100 Hz | Nasal pole bandwidth |
| `cbNZ` | 80-100 Hz | Nasal zero bandwidth |

#### Implementation Notes

**Current synthesis improvements possible:**
1. Differentiate sibilant spectral peaks by place
2. Use bypass path for non-sibilants [f,θ] instead of filtered noise
3. Vary nasal zero frequency by place of articulation
4. Add pharyngeal characteristic (high F1) for [ħ,ʕ]

**Cross-linguistic considerations:**
- Many languages contrast [s] vs [ʃ] vs [ɕ] - need distinct spectral peaks
- Retroflex [ʂ] very similar to [ʃ] acoustically
- Pharyngeals important for Arabic, Hebrew synthesis

---

## Klatt 1990 - Aspiration Noise & Perceptual Cues (Phase 3)

**Source**: Klatt, D. H. & Klatt, L. C. (1990). "Analysis, synthesis, and perception of voice quality variations among female and male talkers." JASA 87(2), 820-857.

### Tables V & VI - Aspiration Noise Patterns by Position

These tables show noisiness ratings for F3 excitation across syllables in utterances, using a 4-point scale (1 = periodic/harmonic, 4 = noise prominent).

#### Table V - Female Talkers (Noisiness Ratings)

| Position | Stressed | Unstressed | Mean |
|----------|----------|------------|------|
| Initial syllable | 2.2 | 2.5 | 2.35 |
| Medial syllable | 2.5 | 2.9 | 2.70 |
| Final syllable | 2.7 | 3.3 | 3.00 |
| **Column Mean** | **2.47** | **2.90** | **2.68** |

#### Table VI - Male Talkers (Noisiness Ratings)

| Position | Stressed | Unstressed | Mean |
|----------|----------|------------|------|
| Initial syllable | 1.3 | 1.5 | 1.40 |
| Medial syllable | 1.5 | 1.9 | 1.70 |
| Final syllable | 1.8 | 2.3 | 2.05 |
| **Column Mean** | **1.53** | **1.90** | **1.72** |

#### Key Findings - Aspiration Patterns

| Effect | Magnitude | Synthesis Implication |
|--------|-----------|----------------------|
| Gender difference | Females +1.0 noisier | Higher `aspirationAmplitude` for female voices |
| Position effect | +0.55 per position | Increase AH toward utterance boundaries |
| Stress effect | +0.6 for unstressed | Higher AH on reduced syllables |
| Interaction | Effects additive | Combine all factors |

**Synthesis Mapping for `aspirationAmplitude` (dB):**

| Voice Type | Initial Stressed | Final Unstressed | Range |
|------------|------------------|------------------|-------|
| Male modal | 25-30 | 40-45 | 15-20 dB |
| Female modal | 35-40 | 50-55 | 15-20 dB |
| Breathy female | 45-50 | 60-65 | 15-20 dB |

### Table X - Acoustic-Perceptual Correlations

Correlation matrix between 12 acoustic measures and 4 perceptual rating categories (PRC1=breathy, PRC2=rough, PRC3=strained, PRC4=resonance).

| Acoustic Measure | Description | PRC1 (Breathy) | Best Predictor Of |
|------------------|-------------|----------------|-------------------|
| H1re2 | H1 minus 2nd harmonic | **r = 0.83** | Breathiness |
| NOIS5 | Noise in 5-8 kHz band | r = 0.81 | Breathiness |
| NOIS3 | Noise in 1-3 kHz band | r = 0.76 | Breathiness |
| H1reA1 | H1 minus F1 amplitude | r = 0.72 | Spectral tilt |
| F0 | Fundamental frequency | r = 0.31 | Gender (indirect) |

**Strongest Cues for Breathiness (Ranked):**
1. H1-H2 amplitude difference (spectral tilt) - r = 0.83
2. High-frequency aspiration noise (5-8 kHz) - r = 0.81
3. Mid-frequency aspiration noise (1-3 kHz) - r = 0.76
4. H1-A1 difference (formant-relative tilt) - r = 0.72

### Tables XIII-XV - Synthesis Parameter Effects on Perception

#### Table XIII - Reference Stimulus Parameters (Female [ə])

Baseline parameters for the modal female voice used in perception testing:

| Parameter | KLSYN88 Name | Value | NVSpeechPlayer Mapping |
|-----------|--------------|-------|------------------------|
| F0 | F0 | 200 Hz | `voicePitch` = 200 |
| F1 | F1 | 800 Hz | `cf1` = 800 |
| F2 | F2 | 1200 Hz | `cf2` = 1200 |
| F3 | F3 | 2500 Hz | `cf3` = 2500 |
| B1 | BW1 | 200 Hz | `cb1` = 200 |
| OQ | OQ | 65% | `glottalOpenQuotient` = 65 |
| TL | TL | 3 dB | `spectralTilt` = 3 |
| AH | AH | 40 dB | `aspirationAmplitude` = 40 |
| AV | AV | 60 dB | `voiceAmplitude` = 60 |
| FL | FL | 0% | `flutter` = 0 |
| DI | DI | 0% | `diplophonia` = 0 |

#### Table XIV - Synthesis Modifications Tested

11 systematic modifications to the reference stimulus:

| # | Modification | Parameters Changed |
|---|--------------|-------------------|
| 1 | F0 +10 Hz | F0 = 210 Hz |
| 2 | OQ +10% | OQ = 75% |
| 3 | TL +6 dB | TL = 9 dB |
| 4 | B1 +100 Hz | B1 = 300 Hz |
| 5 | B1 +200 Hz | B1 = 400 Hz |
| 6 | AH +10 dB | AH = 50 dB |
| 7 | AH +20 dB | AH = 60 dB |
| 8 | AH +20 dB + noise filter | Colored aspiration |
| 9 | OQ + TL combined | OQ=75, TL=9 |
| 10 | OQ + TL + B1 | OQ=75, TL=9, B1=300 |
| 11 | All cues | OQ=75, TL=9, B1=300, AH=60 |

#### Table XV - Breathiness Perception Results

Mean breathiness ratings (0-5 scale, 0=not breathy, 5=very breathy):

| # | Modification | Breathiness Rating | Effect Size |
|---|--------------|-------------------|-------------|
| 0 | Reference (baseline) | 0.76 | — |
| 1 | F0 +10 Hz | 0.88 | +0.12 |
| 2 | OQ +10% alone | 1.12 | +0.36 |
| 3 | TL +6 dB alone | 1.00 | +0.24 |
| 4 | B1 +100 Hz alone | 0.46 | -0.30 |
| 5 | B1 +200 Hz alone | 0.52 | -0.24 |
| 6 | AH +10 dB alone | 1.76 | +1.00 |
| 7 | AH +20 dB alone | 2.64 | +1.88 |
| **8** | **AH +20 dB filtered** | **2.88** | **+2.12** |
| 9 | OQ + TL | 1.36 | +0.60 |
| 10 | OQ + TL + B1 | 2.24 | +1.48 |
| **11** | **All cues combined** | **3.76** | **+3.00** |

#### Key Findings - Synthesis Parameter Effects

**Single Cue Effectiveness (Ranked):**

| Rank | Cue | Rating Change | Synthesis Parameter |
|------|-----|---------------|---------------------|
| 1 | Aspiration +20 dB | +2.12 | `aspirationAmplitude` |
| 2 | OQ increase | +0.36 | `glottalOpenQuotient` |
| 3 | TL increase | +0.24 | `spectralTilt` |
| 4 | F0 increase | +0.12 | `voicePitch` |
| 5 | B1 increase | -0.24 | `cb1` (counterproductive alone) |

**Combined Cue Synergy:**

| Configuration | Rating | Synergy Factor |
|---------------|--------|----------------|
| Single best (AH alone) | 2.88 | 1.0x |
| OQ + TL | 1.36 | 2.3x vs sum |
| OQ + TL + B1 | 2.24 | 3.7x vs sum |
| All cues | 3.76 | Combined > sum |

**Critical Finding**: Aspiration noise is the strongest single cue for breathiness perception. However, combining multiple cues (OQ + TL + B1 + AH) produces significantly higher breathiness ratings than any single cue, and higher than the sum of individual effects. This demonstrates perceptual synergy.

### Synthesis Implementation Recommendations

#### Voice Quality Presets

**Modal Voice (Default):**
```
aspirationAmplitude = 30-40
spectralTilt = 0-3
glottalOpenQuotient = 50-60
cb1 = 60-80
```

**Breathy Voice:**
```
aspirationAmplitude = 55-65  (primary cue)
spectralTilt = 6-12          (secondary)
glottalOpenQuotient = 70-80  (supporting)
cb1 = 150-250                (supporting)
```

**Pressed/Tense Voice:**
```
aspirationAmplitude = 15-25  (reduced)
spectralTilt = -3 to 0       (negative tilt)
glottalOpenQuotient = 30-40  (low)
cb1 = 40-60                  (narrow)
```

#### Position-Dependent Aspiration Rules

```python
def calculate_aspiration(base_ah, position, stressed, gender):
    """
    Calculate position-dependent aspiration amplitude.

    Based on Klatt 1990 Tables V, VI findings.

    Args:
        base_ah: Base aspiration amplitude (dB)
        position: 0=initial, 1=medial, 2=final
        stressed: True/False
        gender: 'male' or 'female'

    Returns:
        Adjusted aspiration amplitude (dB)
    """
    # Position effect: +5 dB per position toward end
    position_adjustment = position * 5

    # Stress effect: +5 dB for unstressed
    stress_adjustment = 0 if stressed else 5

    # Gender baseline: females +10 dB higher
    gender_baseline = 10 if gender == 'female' else 0

    return base_ah + position_adjustment + stress_adjustment + gender_baseline
```

#### Perceptual Cue Priority for Voice Quality

When synthesizing voice quality variations, apply parameters in this priority order:

1. **Aspiration amplitude** (`aspirationAmplitude`) - Strongest perceptual effect
2. **Spectral tilt** (`spectralTilt`) - Second strongest, enhances breathiness
3. **Open quotient** (`glottalOpenQuotient`) - Supporting cue
4. **F1 bandwidth** (`cb1`) - Only effective in combination

Note: F1 bandwidth increase alone actually reduces perceived breathiness (-0.24), but enhances it when combined with other cues (+1.48 for OQ+TL+B1).
