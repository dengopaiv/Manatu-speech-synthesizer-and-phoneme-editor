# Manatu Synthesis Architecture

Technical reference for the KLSYN88-based speech synthesis engine.

## Overview

Manatu synthesizes speech by generating glottal pulses and filtering them through cascaded and parallel formant resonators. The C++ engine handles real-time synthesis while Python manages phoneme data and linguistic processing.

```
IPA Text → Phoneme Parsing → Coarticulation → Pitch Contours → Frames
                                                                  ↓
Audio ← PeakLimiter ← Mix ← Parallel Path ←── Noise/Burst
                       ↑
             Cascade Path ← HF Shelf (+6 dB @ 3 kHz) ← Tracheal ← Spectral Tilt ← DC Block ← Glottal Pulse (4x oversampled + PolyBLEP + halfband decimation)
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

LF model (Liljencrants-Fant) using Rd parameter:
- **Rd=0.3**: Tense voice (sharp pulse, short open quotient)
- **Rd=1.0**: Modal voice (natural, balanced)
- **Rd=2.7**: Breathy voice (soft pulse, extended return phase)

Derives Rk, Rg, Ra from Rd using Fant 1985 polynomial fits.

**Waveform phases:**
1. Rising (0 to tp): Sinusoidal rise
2. Falling (tp to te): Cosinusoidal fall
3. Return (te to 1.0): Exponential decay

**Anti-aliasing:** 4x oversampled with PolyBLEP at glottal closure and excitation boundaries, decimated through two cascaded 7-tap halfband FIR stages (4x→2x→1x, >60 dB stopband attenuation). At 96 kHz output, the LF model runs at 384 kHz — PolyBLEP corrections are extremely precise. DC block filter (20 Hz cutoff) removes glottal source DC offset.

*Location: `speechWaveGenerator.cpp` — LF model + 4x oversampling in VoiceGenerator, polyBLEP(), HalfbandDecimator, DCBlockFilter*

**Note:** When `lfRd = 0`, no glottal voicing is generated (used for voiceless consonants).

---

## 2. Voice Quality

| Parameter | Range | Effect |
|-----------|-------|--------|
| `spectralTilt` | 0-41 dB | HF attenuation via 2-stage lowpass (12 dB/oct), 5 kHz reference |
| `flutter` | 0-1 | Stochastic jitter/shimmer depth (cycle-synchronous) |
| `diplophonia` | 0-1 | Period alternation (creaky voice) |

### Spectral Tilt Filter
Two cascaded 1st-order lowpass stages (12 dB/oct total). Reference frequency 5 kHz: at `spectralTilt=N` dB, the filter attenuates by N dB at 5 kHz. Typical values: voiceless fricatives 2-3, voiced fricatives 4, nasals 4, pharyngeals 10-14.
*Location: `speechWaveGenerator.cpp` — SpectralTiltFilter class*

### Jitter/Shimmer Generator
Stochastic pitch and amplitude perturbation applied cycle-synchronously. Replaces deterministic 3-LFO flutter with random walk for more natural voice quality.
*Location: `speechWaveGenerator.cpp:338-364`*

### Sinusoidal Voicing
Pure sine wave for voicebars in voiced fricatives. Controlled by `sinusoidalVoicingAmplitude`.
*Location: `speechWaveGenerator.cpp:586-592`*

---

## 3. Formant Processing

### Cascade Path (Primary)
Series connection: F6 → F5 → F4 → F3 → F2 → F1

- **F1-F3**: 4th-order resonators (24 dB/octave, sharper peaks)
- **F4-F6**: 2nd-order resonators (12 dB/octave)
- Includes nasal pole (cfNP) and anti-resonance (cfN0)

**Pitch-Synchronous F1 Modulation:**
During glottal open phase, F1 and B1 increase by `deltaF1`/`deltaB1`, modeling subglottal coupling.

**Cascade Ducking:**
When frication amplitude is high, cascade gain is reduced to prevent double-voicing artifacts.

**HF Shelf Compensation:**
First-order HPF shelf (`y = x + boost * HPF(x)`) applied to cascade output only. Corner: 3000 Hz, boost: +6 dB. Compensates for the cascade chain's structural HF loss (~57 dB at 8 kHz through 6 series allPole resonators). Transparent at DC, does not affect parallel path.

*Location: `speechWaveGenerator.cpp` (cascade, ducking, HF shelf)*

### Parallel Path (Secondary)
Parallel connection with individual amplitude control (pa1-pa6):
- Used for fricatives where noise needs per-formant shaping
- `parallelBypass` blends unfiltered signal through
- `parallelVoiceMix` routes voice through parallel path (for laterals)
- **Parallel anti-resonator** (`parallelAntiFreq`/`parallelAntiBw`) creates spectral zeros for lateral fricatives

*Location: `speechWaveGenerator.cpp:798-835`*

### Resonator Implementation

**Zero Delay Feedback (ZDF) Resonators** - Based on Zavalishin (2012).

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

*Location: `speechWaveGenerator.cpp:146-253` (ZDF 2nd-order), `603-632` (4th-order)*

---

## 4. Tracheal Resonances

Models subglottal coupling for breathy voice:

| Parameter | Typical | Purpose |
|-----------|---------|---------|
| `ftpFreq1` | ~600 Hz | First tracheal pole |
| `ftzFreq1` | ~550 Hz | First tracheal zero |
| `ftpFreq2` | ~1400 Hz | Second tracheal pole |

Bypassed when frequency = 0 (backward compatible).

*Location: `speechWaveGenerator.cpp:634-669`*

---

## 5. Noise Generation

### Colored Noise (Fricatives)
Bandpass-filtered noise for place-specific spectra using 4th-order ZDF filtering:

| Fricative | Center Freq | Bandwidth | Character |
|-----------|-------------|-----------|-----------|
| /s/, /z/ | 8000 Hz | 2487 Hz | Bright alveolar sibilant |
| /ʃ/, /ʒ/ | 2800 Hz | 1800 Hz | Mid postalveolar |
| /ɕ/, /ʑ/ | 3600 Hz | 2000 Hz | Alveolo-palatal (between /ʃ/ and /ç/) |
| /ç/, /ʝ/ | 6100/4500 Hz | 2000 Hz | Palatal (higher than postalveolar) |
| /θ/, /ð/ | 7600 Hz | 3025 Hz | Dental (high, broad) |
| /f/, /v/ | 0 (pink) | 1000 Hz | Diffuse labiodental |

*Location: `speechWaveGenerator.cpp:255-299`*

### Burst Generator
Self-sustaining plosive transients with quadratic decay envelope:
- `burstAmplitude`: 0-1 intensity
- `burstDuration`: 0-1 (maps to 5-20ms)
- `burstNoiseColor`: 0=white, 1=pink (for bilabial/uvular bursts)
- Triggers on amplitude edge detection
- Onset transient duration scales with burst filter frequency
- Place-specific bandpass filtering for spectral shaping

*Location: `speechWaveGenerator.cpp:726-796`*

### White Noise
xorshift128+ PRNG with gentle smoothing (0.7/0.3 mix). Includes pink noise generator via first-order IIR filter.

*Location: `speechWaveGenerator.cpp:70-126`*

---

## 6. Frame System

### Frame Structure
~80 parameters per frame including:
- Voicing (pitch, amplitude, aspiration)
- Voice quality (spectralTilt, flutter, diplophonia)
- Cascade formants (cf1-cf6, cb1-cb6, nasal pole/zero)
- Parallel formants (pf1-pf6, pb1-pb6, pa1-pa6, anti-resonator)
- Fricative noise (amplitude, filter freq/bw, colored noise)
- Burst (amplitude, duration, noise color, filter)
- Tracheal resonances (poles, zeros)
- Control (gains, bypass, voice mix, cascade ducking)

*Location: `frame.h`*

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

### CV/VC Waypoints
Coarticulation applies bidirectionally:
- **CV**: Vowel formants start at consonant-influenced onset
- **VC**: Vowel formants shift toward following consonant's locus at end

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

*Location: `ipa.py`*

---

## 9. Parameter Reference

### Voicing
| Parameter | Range | Purpose |
|-----------|-------|---------|
| `voicePitch` | 40-400 Hz | Fundamental frequency |
| `voiceAmplitude` | 0-1 | Voice source level |
| `aspirationAmplitude` | 0-1 | Aspiration noise |
| `lfRd` | 0-2.7 | LF model voice quality (0=voiceless, 1=modal, 2.7=breathy) |

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

| Feature | Classic | Manatu |
|---------|---------|----------------|
| Glottal model | OQ/SQ/TL polynomial | LF model with Rd (Fant 1985), 4x oversampled + halfband decimation |
| Anti-aliasing | None | PolyBLEP at glottal closure + excitation, applied at 4x rate |
| Resonator topology | 2nd-order IIR biquads | ZDF SVF (Zavalishin 2012) |
| F1-F3 order | 2nd-order | 4th-order (24 dB/oct) |
| Flutter | 3 fixed-freq LFOs | Stochastic jitter/shimmer |
| Tilt filter | 1st-order, 3 kHz ref | 2 cascaded stages (12 dB/oct), 5 kHz ref |
| Noise | White noise, LCG PRNG | xorshift128+, bandpass-filtered colored noise |
| Pitch contours | Linear | 3-point (tonal languages) |
| Interpolation | Linear | Hermite smoothstep |
| Output limiting | Hard clip | PeakLimiter (transparent below -3 dB, fast release in silence) |
| DC removal | None | 1st-order DC block filter |
| Bursts | Simple noise × decay | Self-sustaining, place-specific bandpass, onset transient scaling |
| Parallel path | Formant resonators only | + anti-resonator, voice mix, bypass |
| Cascade HF | No compensation | +6 dB shelf above 3 kHz (compensates allPole chain rolloff) |

See `docs/MODIFICATIONS.md` for a detailed catalog of all deviations from KLSYN88.

---

## 11. Known Gaps

| Issue | Impact | Potential Fix |
|-------|--------|---------------|
| Static bandwidths | Less natural formant width | Frequency-dependent BW |
| Simplified nasal coupling | Velopharyngeal approximation | Dynamic velic model |
| F1 cutback not modeled | Stop-to-vowel transitions less natural | Per-formant interpolation timing |

---

## References

- Klatt 1980: "Software for a cascade/parallel formant synthesizer"
- Klatt & Klatt 1990: "Analysis, synthesis, and perception of voice quality variations"
- Stevens 1998: "Acoustic Phonetics"
- Fant 1985: LF model parameter derivation
- Agrawal & Stevens 1992: Retroflex consonant parameters
- Zavalishin 2012: "The Art of VA Filter Design" (Zero Delay Feedback topology)
- Valimaki & Huovilainen 2006: "Oscillator and Filter Algorithms for Virtual Analog Synthesis" (PolyBLEP anti-aliasing)
