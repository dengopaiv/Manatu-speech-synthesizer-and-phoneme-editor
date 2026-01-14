# NVSpeechPlayer Synthesis Architecture

Technical reference for the KLSYN88-based speech synthesis engine.

## Overview

NVSpeechPlayer synthesizes speech by generating glottal pulses and filtering them through cascaded and parallel formant resonators. The C++ engine handles real-time synthesis while Python manages phoneme data and linguistic processing.

```
IPA Text → Phoneme Parsing → Coarticulation → Pitch Contours → Frames
                                                                  ↓
Audio ← Soft Limit ← Mix ← Parallel Path ←── Noise/Burst
                      ↑
              Cascade Path ← Tracheal ← Spectral Tilt ← Glottal Pulse
```

---

## File Structure

| File | Purpose |
|------|---------|
| `src/speechWaveGenerator.cpp` | Core synthesis: voice, formants, noise |
| `src/frame.cpp` | Frame scheduling, interpolation, pitch contours |
| `speechPlayer.py` | Python ctypes wrapper |
| `ipa.py` | IPA parsing, timing, intonation |
| `data/*.py` | Phoneme parameter definitions |
| `data/transitions.py` | Coarticulation rules |

---

## 1. Glottal Source

Two models available, selected via `lfRd` parameter:

### LF Model (lfRd > 0)
Liljencrants-Fant model using Rd parameter (0.3-2.7):
- **Rd=0.3**: Tense voice (sharp pulse, short open quotient)
- **Rd=1.0**: Modal voice (natural, balanced)
- **Rd=2.7**: Breathy voice (soft pulse, extended return phase)

Derives Rk, Rg, Ra from Rd using Fant 1985 polynomial fits.

**Waveform phases:**
1. Rising (0 to tp): Sinusoidal rise
2. Falling (tp to te): Cosinusoidal fall
3. Return (te to 1.0): Exponential decay

*Location: `speechWaveGenerator.cpp:265-303`*

### Legacy Model (lfRd = 0)
Uses `glottalOpenQuotient`, `openQuotientShape`, `speedQuotient`:
- OQ controls fraction of cycle glottis is open
- Shape controls linear (0) vs exponential (1) decay
- SQ controls rise/fall asymmetry

*Location: `speechWaveGenerator.cpp:305-328`*

---

## 2. Voice Quality (KLSYN88)

| Parameter | Range | Effect |
|-----------|-------|--------|
| `spectralTilt` | 0-41 dB | High-frequency attenuation (breathy) |
| `flutter` | 0-1 | Pitch jitter via 3 LFOs at 12.7/7.1/4.7 Hz |
| `diplophonia` | 0-1 | Period alternation (creaky voice) |

### Spectral Tilt Filter
First-order lowpass attenuating high frequencies for breathy voice.
*Location: `speechWaveGenerator.cpp:139-172`*

### Flutter Generator
Sum of three sine waves creating natural pitch micro-variations (±2% at full).
*Location: `speechWaveGenerator.cpp:177-201`*

### Sinusoidal Voicing
Pure sine wave for voicebars in voiced fricatives.
*Location: `speechWaveGenerator.cpp:340-344`*

---

## 3. Formant Processing

### Cascade Path (Primary)
Series connection: F6 → F5 → F4 → F3 → F2 → F1

- **F1-F3**: 4th-order resonators (24 dB/octave, sharper peaks)
- **F4-F6**: 2nd-order resonators (12 dB/octave)
- Includes nasal pole (cfNP) and anti-resonance (cfN0)

**Pitch-Synchronous F1 Modulation:**
During glottal open phase, F1 and B1 increase by `deltaF1`/`deltaB1`, modeling subglottal coupling.

*Location: `speechWaveGenerator.cpp:469-502`*

### Parallel Path (Secondary)
Parallel connection with individual amplitude control (pa1-pa6):
- Used for fricatives where noise needs per-formant shaping
- `parallelBypass` blends unfiltered signal through

*Location: `speechWaveGenerator.cpp:552-572`*

### Resonator Implementation

**Zero Delay Feedback (ZDF) Resonators** - State-of-the-art implementation based on Zavalishin (2012).

The synthesis engine uses modern ZDF topology for all formant resonators, replacing traditional IIR filters with inherently stable, smooth-modulating designs.

**Mathematical foundation:**
```
Analog prototype: H(s) = (g*s) / (s² + 2*R*g*s + g²)

ZDF coefficients:
g = tan(π * f / fs)     // Frequency warping (bilinear transform)
Q = f / BW               // Quality factor
R = 1 / (2*Q)            // Damping coefficient
k1 = 1 / (1 + 2*R*g + g*g)  // Normalization

State equations (trapezoidal integration):
v0 = k1 * (in - 2*R*s1 - s2)  // Bandpass output (implicit feedback)
v1 = s1 + g*v0                 // Lowpass state
v2 = s2 + g*v1                 // Lowpass output
s1 = v1 + g*v0                 // Update integrator 1
s2 = v2 + g*v1                 // Update integrator 2
```

**Key advantages over traditional IIR:**
- **Smooth parameter modulation**: No zipper noise during formant transitions (diphthongs, coarticulation)
- **Inherent stability**: No pole clamping or soft saturation needed - stable for all positive g, R
- **Clean pitch-synchronous modulation**: Handles deltaF1/deltaB1 without discontinuities
- **Modern DSP**: Aligned with current VA filter research

**Anti-resonator mode** (for nasal zeros): Subtracts bandpass from input to create notch filter.

**4th-order variant**: Cascades two ZDF sections with 0.80 bandwidth adjustment for equivalent Q.

*Location: `speechWaveGenerator.cpp:571-713`*

**Legacy IIR implementation** (commented out): Preserved at lines 459-569 for reference.

---

## 4. Tracheal Resonances

Models subglottal coupling for breathy voice:

| Parameter | Typical | Purpose |
|-----------|---------|---------|
| `ftpFreq1` | ~600 Hz | First tracheal pole |
| `ftzFreq1` | ~550 Hz | First tracheal zero |
| `ftpFreq2` | ~1400 Hz | Second tracheal pole |

Bypassed when frequency = 0 (backward compatible).

*Location: `speechWaveGenerator.cpp:432-467`*

---

## 5. Noise Generation

### Colored Noise (Fricatives)
Bandpass-filtered noise for place-specific spectra:

| Fricative | Center Freq | Character |
|-----------|-------------|-----------|
| /s/, /z/ | ~5500 Hz | Bright, high |
| /ʃ/, /ʒ/ | ~3500 Hz | Mid-high |
| /f/, /v/ | 0 (white) | Diffuse |

*Location: `speechWaveGenerator.cpp:79-137`*

### Burst Generator
Plosive transients with quadratic decay envelope:
- `burstAmplitude`: 0-1 intensity
- `burstDuration`: 0-1 (maps to 5-20ms)
- Triggers on amplitude edge detection

*Location: `speechWaveGenerator.cpp:504-550`*

### White Noise
xorshift128+ PRNG with gentle smoothing (0.7/0.3 mix).

*Location: `speechWaveGenerator.cpp:35-75`*

---

## 6. Frame System

### Frame Structure
70 parameters per frame including:
- Voicing (pitch, amplitude, aspiration)
- Voice quality (KLSYN88 parameters)
- Cascade formants (cf1-cf6, cb1-cb6, nasal)
- Parallel formants (pf1-pf6, pb1-pb6, pa1-pa6)
- Fricative noise (amplitude, filter freq/bw)
- Burst (amplitude, duration)
- Control (gains, bypass)

*Location: `frame.h:22-72`*

### Interpolation
S-curve (Hermite smoothstep) for smooth parameter transitions:
```
smoothstep(t) = t² * (3 - 2t)
```
Zero velocity at endpoints prevents clicks.

**Exceptions (step instantly):**
- `burstAmplitude`, `burstDuration` (need sharp onset)
- `preFormantGain`

*Location: `frame.cpp:43-96`, `utils.h:26-31`*

### Pitch Contours
Supports 3-point contours for tonal languages:
- `voicePitch`: F0 at frame start
- `midVoicePitch`: F0 at midpoint (if > 0)
- `endVoicePitch`: F0 at frame end

*Location: `frame.cpp:116-132`*

---

## 7. Coarticulation

### F2 Locus Equations
Consonant place determines vowel F2 onset:

| Place | F2 Locus |
|-------|----------|
| Bilabial | 900 Hz |
| Labiodental | 1100 Hz |
| Alveolar | 1700 Hz |
| Postalveolar | 2000 Hz |
| Palatal | 2300 Hz |
| Velar | 1500 Hz |

Formula: `F2_onset = F2_locus + 0.75 * (F2_vowel - F2_locus)`

### Transition Durations
| Context | Duration |
|---------|----------|
| Stop → Vowel | 40 ms |
| Fricative → Vowel | 50 ms |
| Nasal → Vowel | 35 ms |
| Vowel → Vowel | 60 ms |

*Location: `transitions.py:47-150`*

---

## 8. Synthesis Pipeline

```python
# 1. Parse IPA text
phonemes = IPAToPhonemes(ipaText)

# 2. Calculate durations
calculatePhonemeTimes(phonemes, speed)

# 3. Apply coarticulation
transitions.apply_coarticulation(phonemes)

# 4. Calculate pitch contours
calculatePhonemePitches(phonemes, basePitch, inflection)

# 5. Generate frames
for phoneme in phonemes:
    frame = speechPlayer.Frame()
    applyPhonemeToFrame(frame, phoneme)
    sp.queueFrame(frame, duration_ms, fade_ms)

# 6. Synthesize
samples = sp.synthesize(count)
```

*Location: `ipa.py:699-746`*

---

## 9. Parameter Reference

### Voicing
| Parameter | Range | Purpose |
|-----------|-------|---------|
| `voicePitch` | 40-400 Hz | Fundamental frequency |
| `voiceAmplitude` | 0-1 | Voice source level |
| `aspirationAmplitude` | 0-1 | Aspiration noise |
| `glottalOpenQuotient` | 0-1 | Open phase fraction |

### Formants
| Parameter | Range | Purpose |
|-----------|-------|---------|
| `cf1`-`cf6` | 0-8000 Hz | Cascade frequencies |
| `cb1`-`cb6` | 50-500 Hz | Cascade bandwidths |
| `pf1`-`pf6` | 0-8000 Hz | Parallel frequencies |
| `pa1`-`pa6` | 0-1 | Parallel amplitudes |

### Fricatives
| Parameter | Range | Purpose |
|-----------|-------|---------|
| `fricationAmplitude` | 0-1 | Noise source level |
| `noiseFilterFreq` | 0-8000 Hz | Bandpass center |
| `noiseFilterBw` | 100-2000 Hz | Bandpass width |

### Bursts
| Parameter | Range | Purpose |
|-----------|-------|---------|
| `burstAmplitude` | 0-1 | Transient intensity |
| `burstDuration` | 0-1 | Length (5-20 ms) |

---

## 10. Enhancements Over Classic KLSYN88

| Feature | Classic | NVSpeechPlayer |
|---------|---------|----------------|
| Glottal model | OQ/SQ only | LF model + legacy |
| Resonator order | 2nd-order | 4th-order for F1-F3 |
| Pitch contours | Linear | 3-point (tonal languages) |
| Interpolation | Linear | Hermite smoothstep |
| Noise PRNG | LCG | xorshift128+ |
| Output limiting | Hard clip | tanh soft limiter |

---

## 11. Known Gaps

| Issue | Impact | Potential Fix |
|-------|--------|---------------|
| No parallel anti-resonators | Fricative spectral nulls not modeled | Add zero path |
| Static bandwidths | Less natural formant width | Frequency-dependent BW |
| Simplified nasal coupling | Velopharyngeal approximation | Dynamic velic model |
| Some vowel instability | Requires hand-tuning | Parameter optimization |

---

## References

- Klatt 1980: "Software for a cascade/parallel formant synthesizer"
- Klatt & Klatt 1990: "Analysis, synthesis, and perception of voice quality variations"
- Stevens 1998: "Acoustic Phonetics"
- Fant 1985: LF model parameter derivation
- Agrawal & Stevens 1992: Retroflex consonant parameters
- Zavalishin 2012: "The Art of VA Filter Design" (Zero Delay Feedback topology)
- Välimäki & Huovilainen 2006: "Oscillator and Filter Algorithms for Virtual Analog Synthesis" (PolyBLEP anti-aliasing)
