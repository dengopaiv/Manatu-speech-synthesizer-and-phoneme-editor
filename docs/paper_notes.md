# Speech Synthesis Reference Notes

Notes extracted from academic papers for Manatu synthesizer tuning.

---

## Table of Contents

1. [Stevens - Acoustic Phonetics](#stevens---acoustic-phonetics)
2. [Ladefoged - Phonetics](#ladefoged---phonetics)
3. [Formant Reference Tables](#formant-reference-tables)
4. [Voice Quality Parameters](#voice-quality-parameters)

---

## Stevens - Acoustic Phonetics

### Overview
Kenneth Stevens' "Acoustic Phonetics" (1998) - Technical reference for acoustic properties of speech sounds.

---

### Part 1 (Pages 1-10) - Anatomy & Physiology

**Chapter 1: Anatomy and Physiology of Speech Production**

#### Subglottal System
| Parameter | Value | Notes |
|-----------|-------|-------|
| Trachea cross-section | ~2.5 cm² | Adult speaker |
| Trachea length | 10-12 cm | Adult speaker |
| Vital capacity | 3000-5000 cm³ | Max lung volume range |
| Speech lung volume | 500-1000 cm³ | 10-20% of vital capacity |
| Lung pressure (speech) | 5-10 cm H₂O | Normal speaking level |

#### Larynx Dimensions
| Parameter | Value | Notes |
|-----------|-------|-------|
| Vocal fold length | 1.0-1.5 cm | Adult |
| Vocal fold thickness | 2-3 mm | |
| Cricoid cartilage diameter | 1.9 cm (F) / 2.4 cm (M) | Internal diameter |

**Synthesis Relevance:**
- Trachea dimensions inform tracheal resonance parameters (`ftpFreq1`, `ftpFreq2`)
- Vocal fold dimensions affect fundamental frequency range

---

### Parts 27-29 (Pages 261-290) - Chapter 6: Vowels

#### Table 6.2 - American English Vowel Formants (Peterson & Barney 1952)

**Female Speakers:**
| Vowel | F1 (Hz) | F2 (Hz) | F3 (Hz) | F0 (Hz) |
|-------|---------|---------|---------|---------|
| i | 310 | 2790 | 3310 | 235 |
| e | 560 | 2320 | 2950 | 223 |
| æ | 860 | 2050 | 2850 | 220 |
| ɑ | 850 | 1220 | 2810 | 212 |
| o | 600 | 1200 | 2540 | 220 |
| u | 370 | 950 | 2670 | 232 |

**Male Speakers:**
| Vowel | F1 (Hz) | F2 (Hz) | F3 (Hz) | F0 (Hz) |
|-------|---------|---------|---------|---------|
| i | 270 | 2290 | 3010 | 136 |
| e | 460 | 1890 | 2670 | 130 |
| æ | 660 | 1720 | 2410 | 127 |
| ɑ | 730 | 1090 | 2440 | 124 |
| o | 450 | 1050 | 2610 | 130 |
| u | 300 | 870 | 2240 | 137 |

#### High Vowel Parameters
- F1 range: 250-310 Hz
- F1 bandwidth: ~80 Hz (modal voicing)
- F1-F0 spacing: < 3 bark (perceptual threshold)

#### Vowel Feature Classification (Table 6.1)
| Feature | i | e | æ | ɑ | o | u |
|---------|---|---|---|---|---|---|
| High | + | | - | - | - | + |
| Low | | | + | + | - | - |
| Back | | | - | + | + | + |

#### Key Acoustic Principles
- Female formants ~18% higher than male on average
- Front vowels: F2-F3 spacing < 3.5 bark
- Back vowels: F1-F2 spacing 2.1-4.7 bark
- High vowels: F1-F0 spacing 0.8-1.6 bark

---

### Parts 35-40 (Pages 341-400) - Chapter 7-8: Stop Consonants & Fricatives

#### Stop Consonant Timing
| Parameter | Value | Notes |
|-----------|-------|-------|
| Closure duration | ~80 ms | Typical |
| Burst duration | ~10 ms | Transient |
| Labial release rate | 100 cm²/s | /p/, /b/ |
| Alveolar release rate | 50 cm²/s | /t/, /d/ |

#### Fricative Spectral Characteristics

**Table 8.1 - /f/ vs Vowel Amplitude Differences (dB)**
| Region | VCV Measured | Calculated |
|--------|--------------|------------|
| ΔA2 | 30(3) | 33 |
| ΔA3 | 19(6) | 23 |
| ΔA4 | 9(7) | 6 |
| ΔA5 | -19(6) | -16 |

**Table 8.2 - /s/ vs Vowel Amplitude Differences (dB)**
| Region | VCV Measured | Calculated |
|--------|--------------|------------|
| ΔA2 | 30(3) | 33 |
| ΔA3 | 19(6) | 23 |
| ΔA4 | 9(7) | 6 |
| ΔA5 | -19(6) | -16 |

**Table 8.3 - /ʃ/ vs Vowel Amplitude Differences (dB)**
| Region | VCV Measured | Calculated |
|--------|--------------|------------|
| ΔA2 | 15(4) | 19 |
| ΔA3 | -5(5) | 0 |
| ΔA4 | -6(7) | -10 |

#### Fricative Resonance Frequencies
| Fricative | Front Cavity | Key Resonance | Bandwidth |
|-----------|--------------|---------------|-----------|
| /s/ | ~2 cm | ~4500 Hz | ~600 Hz |
| /ʃ/ | ~4 cm | ~2500 Hz | ~200 Hz |
| /f/ | No front cavity | Flat spectrum | - |

**Synthesis Relevance:**
- `/s/`: High `noiseFilterFreq` (~4500 Hz), parallel F5 emphasis
- `/ʃ/`: Lower `noiseFilterFreq` (~2500 Hz), F3-F4 emphasis
- `/f/`: Flat frication, weak amplitude (10-25 dB below vowel)

---

### Parts 41-43 (Pages 401-430) - Affricates & Aspiration

#### Section 8.2 - Affricates /tʃ/, /dʒ/

**Affricate Timing**
| Parameter | Value | Notes |
|-----------|-------|-------|
| Initial transient | 1-2 ms | Brief burst at release |
| Frication rise | 40-50 ms | Noise amplitude increases |
| Total duration | 85-160 ms | Average 110 ms (voiceless) |
| Voicing onset | ~110 ms | From release to vowel |

**Table 8.4 - Affricate F4 Amplitude (dB re vowel)**
| Time After Release | Measured | Calculated |
|--------------------|----------|------------|
| Initial transient | -3(7) | +6 |
| 10 ms after | -5(6) | +3 |
| 50 ms after | +9(4) | +9 |

**Synthesis Relevance:**
- Affricates need `_isAffricate` flag
- Model as stop burst → fricative sequence
- `burstDuration` ~2 ms, then frication ~50 ms

---

#### Section 8.3 - Aspiration & /h/

**Glottal Configuration for /h/**
| Parameter | Value | Notes |
|-----------|-------|-------|
| Max glottal area | 0.25 cm² | During consonant |
| Peak airflow | 600-850 cm³/s | Intervocalic /h/ |
| Duration | ~200 ms | Modal→spread→modal |
| H1-H2 change | 8-10 dB | Voice quality marker |

**Breathy vs Modal Voicing (Figure 8.35)**
| Voice Type | H1 Amplitude | H2 Amplitude | H1-H2 |
|------------|--------------|--------------|-------|
| Modal | ~40 dB | ~35 dB | ~5 dB |
| Breathy | ~40 dB | ~25 dB | ~15 dB |

**Turbulence Noise Source**
- Location: 1.0-2.5 cm above glottis (epiglottis/ventricular folds)
- Amplitude proportional to: U³A⁻²·⁵
- Reference level: 28 dB re 0.0002 dyne/cm² at 2500 Hz

**Synthesis Relevance:**
- `/h/`: Use `aspirationAmplitude`, spread glottis
- Breathy voice: Increase `spectralTilt` (more H1-H2 difference)
- `voiceTurbulenceAmplitude` for noise during breathy voicing
- `glottalOpenQuotient` affects breathiness

---

### Parts 44-46 (Pages 431-460) - Tracheal Resonances & Aspirated Stops

#### Table 8.5 - Subglottal (Tracheal) Pole Frequencies (Hz)

| Pole | Female | Male |
|------|--------|------|
| P1 | 750 | — |
| P2 | 1050 | 1550 |
| P3 | 2350 | 2200 |

*Note: Lowest pole for male speakers not consistently observed (Klatt & Klatt, 1990)*

**Synthesis Relevance:**
- Map to `ftpFreq1` (~750-1050 Hz), `ftpFreq2` (~1550-2350 Hz)
- Tracheal coupling strongest during /h/ and breathy voicing
- Bandwidth ~300 Hz for 0.25 cm² glottal opening

#### Modal vs Breathy Voicing Spectra (Figure 8.55)

| Parameter | Modal | Breathy |
|-----------|-------|---------|
| Periodic dominates | < 3 kHz | < 2 kHz |
| Noise dominates | > 4 kHz | > 3 kHz |
| Relative noise level | -10 to -20 dB | -6 to -10 dB |

**Voice Quality Synthesis Parameters:**
- `spectralTilt`: Higher for breathy (steeper rolloff)
- `voiceTurbulenceAmplitude`: Higher for breathy voice
- Noise amplitude ∝ U³A⁻²·⁵ (airflow³ × area⁻²·⁵)

#### Voiceless Aspirated Stops /pʰ, tʰ, kʰ/

**Timing Sequence (Figure 8.66)**
| Phase | Time | Description |
|-------|------|-------------|
| T (Transient) | 0-4 ms | Burst at consonant release |
| F (Frication) | 4-25 ms | Noise at supraglottal constriction |
| A (Aspiration) | 10-50 ms | Noise near glottis |
| V (Voicing) | ~50 ms | Modal voicing onset |

**Airflow During Aspiration (Figure 8.60)**
| Place | Peak Airflow | Notes |
|-------|--------------|-------|
| Labial /pʰ/ | ~1000 cm³/s | Faster rise |
| Velar /kʰ/ | ~700 cm³/s | Slower rise |

**Synthesis Relevance:**
- Aspirated stops: longer `aspirationAmplitude` interval
- Voicing onset delayed ~50 ms after release
- F0 raised ~18 Hz at vowel onset after aspirated stop

---

### Parts 47-49 (Pages 461-490) - Voiced Obstruents & Nasal Consonants

#### Section 8.4 - Voicing for Obstruents

**F0 Effects Near Consonants**
| Consonant Type | F0 Change | Time Course |
|----------------|-----------|-------------|
| Voiced stop | -5 to -7% | Initial 50-100 ms of vowel |
| Voiceless stop | +5 to +10% | Initial 20-40 ms of vowel |
| Voiced aspirated | Breathy onset | 80 ms aspiration interval |

**Voice Quality During Voiced Consonants**
- Vocal tract expands ~15 cm³ during closure
- Vocal fold stiffness decreases 9-15%
- Glottal vibration continues through closure if transglottal pressure maintained
- H1 amplitude 5-10 dB below vowel during closure

---

## Chapter 9 - Nasal Consonants

#### Section 9.1 - Articulatory Description

**Velopharyngeal Parameters**
| Parameter | Value | Notes |
|-----------|-------|-------|
| Velopharyngeal area | ~0.2 cm² | Peak opening |
| Total movement time | 200-250 ms | Open→close cycle |
| Port open duration | ~200 ms | Actual open interval |
| Intraoral pressure | <1 cm H₂O | Near atmospheric |

#### Section 9.1.2 - Nasal Acoustic Transfer Function

**Nasal Pole-Zero Frequencies**
| Component | Frequency | Bandwidth | Notes |
|-----------|-----------|-----------|-------|
| Nasal pole 1 (FN) | 250-300 Hz | ~100 Hz | Helmholtz resonance |
| Nasal pole 2 | 750-1000 Hz | ~200 Hz | Nasal cavity resonance |
| Nasal zero (Z1) | >1000 Hz | Varies | Place-dependent |
| Nasal cavity natural freq | ~500 Hz | - | Closed velum reference |

**Synthesis Parameter Mapping:**
- `cfNP` (nasal pole freq): 250-300 Hz
- `cbNP` (nasal pole bandwidth): 100-200 Hz
- `cfN0` (nasal zero freq): 1000-1500 Hz (place-dependent)
- `cbN0` (nasal zero bandwidth): 100-200 Hz

#### Nasal Consonant Place Cues (Figure 9.3)

| Nasal | Zero Frequency | F2 Transition | Notes |
|-------|----------------|---------------|-------|
| /m/ (labial) | ~1000 Hz | Rising | Longer front cavity |
| /n/ (alveolar) | ~1500 Hz | Varies | Medium front cavity |
| /ŋ/ (velar) | ~3000 Hz | Falling | Short/no front cavity |

**Key Acoustic Features of Nasals:**
1. Low-frequency prominence (~250 Hz) - "nasal murmur"
2. Reduced amplitude above 500 Hz (anti-resonances)
3. Formant transitions at closure/release boundaries
4. Continuous voicing throughout

**Synthesis Relevance:**
- Set `_isNasal` flag for nasal consonants
- Use low `cf1` (~250-300 Hz) during nasal murmur
- Enable nasal pole/zero parameters (`cfNP`, `cfN0`)
- Reduce higher formant amplitudes during murmur

#### Nasal Place-Specific Zero Frequencies (Section 9.1.3)

| Nasal | Front Cavity Length | Lowest Zero (Z1) | Second Zero |
|-------|---------------------|------------------|-------------|
| /m/ (labial) | 14-17 cm | ~1000-1200 Hz | ~3000 Hz |
| /n/ (alveolar) | 5-8 cm | ~1600-1900 Hz | ~4500 Hz |
| /ŋ/ (velar) | 3-7 cm | ~3000 Hz | Cancelled by pole |

**Amplitude Changes at Nasal Boundaries (Figure 9.13)**
| Boundary | ΔA2 Change | ΔA3 Change | Notes |
|----------|------------|------------|-------|
| /n/ implosion/release | 18-20 dB | 10 dB | Consistent across vowels |
| /m/ release (front V) | 20 dB | - | Before /i/, /e/ |
| /m/ release (back V) | 5-8 dB | - | Before /o/, /u/ |

**Synthesis Parameter Mapping (Place-Specific):**
- `/m/`: `cfN0` ~1000 Hz (lower zero)
- `/n/`: `cfN0` ~1500-1900 Hz (mid zero)
- `/ŋ/`: `cfN0` ~3000 Hz (high zero, may be cancelled)

---

### Parts 50-52 (Pages 491-520) - Glides /w/, /j/

#### Section 9.2 - Glide Characteristics

**Definition:** Consonants with constriction narrow enough to affect spectrum but not narrow enough to create turbulence. Air flows past constriction during voicing.

#### Table 9.1 - Glide F1 Frequencies (Hz)

| Speaker | /w/ | /j/ | Before High V | Before Non-High V |
|---------|-----|-----|---------------|-------------------|
| Female | 280 | 253 | 245 | 291 |
| Male | 298 | 250 | 255 | 293 |

**A1 Amplitude Reduction (dB re following vowel)**
| Speaker | Before High Vowels | Before Non-High Vowels |
|---------|-------------------|----------------------|
| Female | 12.2 dB | 6.9 dB |
| Male | 9.1 dB | 5.1 dB |

#### Glide Acoustic Properties

| Parameter | Value | Notes |
|-----------|-------|-------|
| Minimum constriction area | 0.17 cm² | No turbulence threshold |
| Transition duration | 200-250 ms | Slower than stops |
| F1 bandwidth | 100-150 Hz | Wider than vowels |
| Glottal source reduction | 2-3 dB | During constriction |
| F2 source reduction | ~9 dB | During /j/ |

#### Palatal Glide /j/ Configuration

| Parameter | Value |
|-----------|-------|
| Volume behind constriction | 50 cm³ (male) / 40 cm³ (female) |
| Constriction length | 3.0 cm |
| Cross-sectional area | 0.17 cm² |
| Calculated F1 | ~260 Hz (male) / ~320 Hz (female) |

#### Labial Glide /w/ Configuration

| Parameter | Velar Part | Labial Part |
|-----------|-----------|-------------|
| Volume | 35 cm³ | 15 cm³ |
| Area | 0.2 cm² | 0.17 cm² |
| Length | 3.5 cm | 0.8 cm |
| F1 contribution | ~290 Hz | ~410 Hz |
| Combined F1 | ~270 Hz | - |

**Synthesis Relevance:**
- `/j/`: Set `_isSemivowel`, low `cf1` (~250-260 Hz), high `cf2` (~2200+ Hz)
- `/w/`: Set `_isSemivowel`, low `cf1` (~270-300 Hz), low `cf2` (~700-900 Hz)
- Use wider `cb1` (~100-150 Hz) for glides
- Reduce `voiceAmplitude` by 5-10 dB during constriction
- Transition time ~200-250 ms (slower than stops)

#### Section 9.2.3 - Summary of Glide Characteristics

**Labial Glide /w/ Spectrum:**
- F1: ~270-300 Hz (dominant peak)
- F2: Well below 1 kHz (~700 Hz)
- F2 bandwidth: ~200 Hz (wide, merged with F1)
- F3 and higher: >30 dB below F1 (obscured)

**Palatal Glide /j/ Spectrum:**
- F1: ~250-260 Hz
- F2-F3-F4: High-frequency cluster at 3-4 kHz
- F3 bandwidth: ~200-300 Hz (large due to constriction losses)
- Dominant energy in F4 region (~3.5 kHz)

---

### Parts 53-55 (Pages 521-550) - Liquids /r/, /l/

#### Section 9.3 - Liquid Characteristics

**Key Distinction from Glides:**
- Shorter constriction (~1 cm vs ~3 cm for glides)
- Higher F1 (~400 Hz vs ~250-300 Hz)
- Introduces acoustic side branch in airway

#### Section 9.3.1 - Low-Frequency Characteristics

**Liquid F1 Values (Hz)**
| Speaker | F1 Range | Average |
|---------|----------|---------|
| Female | 350-480 | ~400 |
| Male | 330-430 | ~380 |

**Acoustic Parameters:**
| Parameter | Value | Notes |
|-----------|-------|-------|
| Minimum constriction area | 0.17 cm² | Same as glides |
| Constriction length | ~1.0 cm | Shorter than glides |
| Volume behind constriction | ~40 cm³ | |
| F1 bandwidth | ~140 Hz | 80 Hz above vowel baseline |
| F1 amplitude | -10 dB | Below following vowel |

#### Table 9.2 - Retroflex /r/ Formant Frequencies (Hz)

| Speaker | F1 | F2 | F_R (extra) |
|---------|----|----|-------------|
| Female | 360-480 | 1030-1240 | 1800-2050 |
| Male | 330-430 | 880-1200 | 1380-1610 |

#### Section 9.3.2.1 - Retroflex /r/ Acoustics

**Vocal Tract Configuration (Figure 9.36a):**
| Cavity | Length | Volume | Area |
|--------|--------|--------|------|
| Back cavity | 13.5 cm | 40 cm³ | - |
| Front cavity | 1.2 cm | 8 cm³ | 0.5 cm² |
| Constriction | 0.8 cm | - | 0.17 cm² |

**Key Acoustic Features:**
- F_R (front-cavity resonance): ~1300-1660 Hz
- Zero from sublingual space: ~2-3 kHz
- F2 and F_R close together (characteristic "bunching")
- F_R appears as shoulder on high side of F2
- At release: F_R and F3 merge into single peak
- Amplitude rise at release: 10-20 dB over 20 ms

**Synthesis Relevance:**
- `/r/`: Set `_isLiquid`, low `cf3` (~1500-1800 Hz close to F2)
- Use extra pole near F2 frequency
- Consider zero around 2-3 kHz for sublingual cavity

#### Section 9.3.2.2 - Lateral /l/ Acoustics

**Vocal Tract Configuration (Figure 9.43):**
| Cavity | Length | Volume/Area |
|--------|--------|-------------|
| Back cavity | 13.5 cm | 40 cm³ |
| Side branch | 2.5 cm | 2-3 cm³ |
| Constriction | 1.0 cm | 0.17 cm² |

**Key Acoustic Features:**
- F3 high and well separated from F2 (opposite of /r/)
- High-frequency pole cluster: 2500-4000 Hz (3 poles + 1 zero)
- Zero frequency: 2200-4400 Hz (varies with side branch length)
- F2: ~1100 Hz (lowered by backed tongue body)
- F2 bandwidth: ~140 Hz

**Lateral /l/ Spectrum Poles (Figure 9.44):**
| Formant | Frequency | Bandwidth |
|---------|-----------|-----------|
| F1 | 360 Hz | 160 Hz |
| F2 | 1100 Hz | 140 Hz |
| F3 | 2800 Hz | 150 Hz |
| F4 | 3500 Hz | 300 Hz |
| Zero | 3400 Hz | 300 Hz |
| F5 | 3900 Hz | 1000 Hz |

#### Table 9.3 - Lateral /l/ Formant Measurements

**Prestressed Position:**
| Speaker | F1 (SD) | F2 (SD) | ΔF1 | ΔF2 | ΔA1 | ΔA2 | ΔA3 |
|---------|---------|---------|-----|-----|-----|-----|-----|
| Female | 350 (67) | 1180 (84) | 190 | 280 | 6 dB | 13 dB | 14 dB |
| Male | 360 (43) | 900 (120) | 150 | 220 | 9 dB | 13 dB | 12 dB |

**Poststressed Position:**
| Speaker | ΔF1 | ΔF2 | ΔA1 | ΔA2 | ΔA3 |
|---------|-----|-----|-----|-----|-----|
| Female | 20 | 100 | 2 dB | 5 dB | 3 dB |
| Male | 60 | 150 | 1 dB | 5 dB | 3 dB |

**Synthesis Relevance:**
- `/l/`: Set `_isLiquid`, high `cf3` (~2500-2800 Hz, well above F2)
- F2 lower than /r/ (~900-1100 Hz)
- Wider `cb1` and `cb2` (~140-160 Hz)
- High-frequency pole cluster with zero
- Greater amplitude changes at release vs implosion

#### /r/ vs /l/ Acoustic Contrast Summary

| Feature | /r/ (retroflex) | /l/ (lateral) |
|---------|-----------------|---------------|
| F2 | 880-1240 Hz | 900-1180 Hz |
| F3 | Close to F2 (~1500 Hz) | High (~2500-2800 Hz) |
| F2-F3 spacing | Small (~300-500 Hz) | Large (~1500+ Hz) |
| Extra resonance | F_R between F2-F3 | Pole cluster 2.5-4 kHz |
| Zero | ~2-3 kHz (sublingual) | ~3.4 kHz (side branch) |
| Key cue | Low F3 | High F3, irregular HF |

#### Section 9.3.3 - Summary of Liquid Characteristics

- Both /r/ and /l/ have F1 ~350-480 Hz (higher than glides)
- F2 generally 900-1200 Hz
- Both have acoustic side branch → additional poles/zeros above 1500 Hz
- Acoustic influence extends 200-250 ms
- Key distinction: /r/ has low F3 (close to F2), /l/ has high F3

---

### Parts 56-58 (Pages 551-580) - Chapter 10: Context Effects

#### Coarticulation on Vowels

**Table 10.1 - Vowel /ʌ/ Formants by Consonant Context (Hz)**

| Context | Female F1 | Female F2 | Female F3 | Male F1 | Male F2 | Male F3 |
|---------|-----------|-----------|-----------|---------|---------|---------|
| Velar (*cover*) | 750 | 1320 | 2810 | 600 | 1050 | 2530 |
| Alveolar (*justice*) | 630 | 1550 | 3540 | 560 | 1310 | 2560 |

*Note: F2 difference 200-300 Hz based on consonant place*

**Table 10.2 - Schwa Formants in Different Contexts (Hz)**

| Context | Female F1 | Female F2 | Female F3 | Male F1 | Male F2 | Male F3 |
|---------|-----------|-----------|-----------|---------|---------|---------|
| Alveolar (*pass a dip*) | 494 | 1785 | 3513 | 423 | 1491 | 2624 |
| Labial (*rub a book*) | 410 | 1071 | 2908 | 488 | 912 | 2474 |

*Note: F2 difference ~600-700 Hz between contexts!*

#### Section 10.4 - Reduced Vowels (Schwa)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Duration | 50-130 ms | Much shorter than stressed vowels |
| F1 | 330-490 Hz | Relatively stable |
| F2 | 900-1800 Hz | Highly variable by context |
| Max oral opening | 0.2-0.3 cm² | Small opening |

#### Coarticulation Timing

| Movement | Duration | Notes |
|----------|----------|-------|
| Consonant influence on vowel | 100-150 ms | Extends into vowel |
| Tongue body back→front | ~100 ms | Rapid transition |
| Complete front-back cycle | 200-300 ms | Full movement |
| Vowel influence threshold | <200 ms | Shorter vowels fully affected |

**Synthesis Relevance:**
- Schwa: Use `_copyAdjacent` flag to inherit adjacent formants
- F2 coarticulation: ±200-700 Hz based on adjacent consonant place
- Reduced vowels: Shorter duration, wider F1 bandwidth
- Consonant clusters: Consider overlapping gestures

---

### Parts 59-61 (Pages 581-602) - Notes, References, Index

**Technical Notes from Chapter 8:**
- Aspiration noise dipole source: lowest zero at ~1400 Hz for source placed 2.5 cm from glottis
- Delay of ~0.5 ms for airflow from glottis to epiglottis where high-frequency noise is generated
- Below ~2 kHz, monopole source dominates over dipole source

**Technical Notes from Chapter 9:**
- Liquid consonants with turbulence at tongue blade constriction exist in some languages (not sonorant /r/, /l/)
- Bandwidth increase due to constriction resistance calculated similarly to glide /j/
- X-ray microbeam studies show wide range of tongue shapes for /r/ with little relation to resulting formant patterns

**Technical Notes from Chapter 10:**
- Syllabic /r/ (ṛ) can be viewed as feature merging of /ə/ + /n/ into single segment

---

## Stevens - Acoustic Phonetics (REVIEW COMPLETE)

**Summary of Key Data Extracted:**

| Category | Tables/Data | Primary Synthesis Parameters |
|----------|-------------|------------------------------|
| Vowels | Table 6.2 (Peterson & Barney formants) | cf1-cf6, cb1-cb6 |
| Fricatives | Table 8.1 (noise spectra), Table III (amplitudes) | fricationAmplitude, pa1-pa6, noiseFilterFreq |
| Affricates | Section 8.3 (timing) | burstAmplitude, burstDuration |
| Nasals | Table 8.5 (tracheal), Chapter 9 (zeros) | cfNP, cbNP, cfN0, cbN0, ftpFreq1/2 |
| Glides | Table 9.1 (F1 frequencies) | cf1, cf2, voiceAmplitude |
| Liquids | Tables 9.2, 9.3 (/r/, /l/ formants) | cf1-cf4, cb1-cb4 |
| Coarticulation | Tables 10.1, 10.2 (context effects) | _copyAdjacent, formant interpolation |

---

