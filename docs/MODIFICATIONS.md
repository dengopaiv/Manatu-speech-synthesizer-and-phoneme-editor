# Manatu Deviations from KLSYN88

Catalog of all architectural deviations from Klatt & Klatt 1990 ("Analysis, synthesis, and perception of voice quality variations among female and male talkers").

---

## Resonators

| | KLSYN88 Original | Manatu |
|---|---|---|
| **Topology** | 2nd-order IIR biquads | ZDF SVF (Zavalishin 2012) |
| **F1-F3 order** | 2nd-order (12 dB/oct) | 4th-order (24 dB/oct, two cascaded ZDF stages) |
| **F4-F6 order** | 2nd-order | 2nd-order (unchanged) |
| **Modulation** | Coefficient recalculation per sample | Implicit ZDF feedback — no zipper noise |
| **Anti-resonator** | Cascade nasal zero only | Cascade nasal zero + parallel anti-resonator for laterals |

**Rationale:** ZDF topology eliminates zipper noise during formant transitions (diphthongs, coarticulation). 4th-order for F1-F3 gives sharper peaks matching natural vowel spectra.

*Location: `speechWaveGenerator.cpp:146-253` (ZDF), `603-632` (4th-order)*

---

## Glottal Source

| | KLSYN88 Original | Manatu |
|---|---|---|
| **Model** | OQ/SQ/TL polynomial (Klatt 1980) | LF model with Rd parameter (Fant 1985) |
| **Parameters** | Open quotient, speed quotient, tilt | Single Rd parameter (0.3-2.7) derives Rk, Rg, Ra |
| **Sample rate** | 1x | 4x oversampled with halfband FIR decimation (4x→2x→1x) |
| **Anti-aliasing** | None | PolyBLEP at glottal closure and excitation boundaries (applied at 4x rate) |
| **Output sample rate** | N/A | 96 kHz (minimal ZDF warping: 4% at 8 kHz, 6% at 10 kHz) |
| **DC component** | Accepted | Explicit DC block filter after source |

**Rationale:** LF model is more parsimonious (1 parameter vs 3) with well-studied perceptual correlates. 4x oversampling with halfband decimation (two cascaded 7-tap halfband FIR stages, >60 dB stopband) provides superior alias rejection. At 96 kHz output, the LF model runs at 384 kHz — PolyBLEP corrections are extremely precise. The 96 kHz output rate also minimizes ZDF frequency warping (4% at 8 kHz vs 20% at 44.1 kHz).

*Location: `speechWaveGenerator.cpp` — VoiceGenerator, computeGlottalWave(), polyBLEP(), HalfbandDecimator, DCBlockFilter*

---

## Spectral Tilt Filter

| | KLSYN88 Original | Manatu |
|---|---|---|
| **Order** | 1st-order lowpass (6 dB/oct) | 2 cascaded 1st-order stages (12 dB/oct) |
| **Reference frequency** | 3 kHz | 5 kHz |
| **Control** | TL parameter in dB | `spectralTilt` parameter in dB |

**Rationale:** Two cascaded stages provide a steeper rolloff slope that better matches measured breathy voice spectra. The 5 kHz reference preserves energy in the 2-4 kHz speech band while providing effective tilt at high values.

*Location: `speechWaveGenerator.cpp` — SpectralTiltFilter class*

---

## Flutter / Pitch Perturbation

| | KLSYN88 Original | Manatu |
|---|---|---|
| **Method** | 3 fixed-frequency LFOs (12.7, 7.1, 4.7 Hz) | Stochastic jitter + shimmer (cycle-synchronous) |
| **Pitch variation** | Deterministic sinusoidal sum | Random walk with configurable depth |
| **Amplitude variation** | None | Shimmer (cycle-to-cycle amplitude variation) |

**Rationale:** Deterministic LFO flutter produces audible periodicity. Stochastic jitter/shimmer sounds more natural and matches measured vocal perturbation distributions.

*Location: `speechWaveGenerator.cpp:338-364`*

---

## Noise Generation

| | KLSYN88 Original | Manatu |
|---|---|---|
| **PRNG** | Linear congruential generator | xorshift128+ (better spectral flatness) |
| **Fricative noise** | White noise → parallel formants | Bandpass-filtered colored noise (place-specific center freq) |
| **Burst noise** | Simple noise × decay envelope | Self-sustaining burst with place-specific bandpass and onset transient |
| **Burst coloring** | N/A | `burstNoiseColor` parameter for pink noise (bilabial/uvular) |

**Rationale:** Colored noise provides immediate place cues before formant filtering. Self-sustaining bursts complete their envelope independently of frame transitions.

*Location: `speechWaveGenerator.cpp:70-126` (white noise), `255-299` (colored noise), `726-796` (burst generator)*

---

## Output Processing

| | KLSYN88 Original | Manatu |
|---|---|---|
| **Limiting** | Hard clip at ±1.0 | PeakLimiter (transparent below -3 dB, fast release in silence) |
| **DC removal** | None | 1st-order DC block filter (20 Hz cutoff) |
| **Cascade HF shelf** | None | +6 dB shelf above 3 kHz on cascade output only |

**Rationale:** PeakLimiter prevents digital clipping while preserving dynamics. Fast-release mode allows limiter recovery during stop closure gaps so bursts are not attenuated. DC block removes glottal source DC offset that can reduce dynamic range. Cascade HF shelf compensates for the cascade chain's structural HF loss (~57 dB at 8 kHz through 6 series allPole resonators) — applied only to cascade path, not parallel (which carries fricative/sibilant HF naturally).

*Location: `speechWaveGenerator.cpp:860-888` (PeakLimiter), `384-410` (DC block)*

---

## Additional Features (Not in KLSYN88)

| Feature | Purpose | Location |
|---------|---------|----------|
| **Sinusoidal voicing** | Pure sine voicebar for voiced fricatives | `speechWaveGenerator.cpp:586-592` |
| **Tracheal resonator** | Subglottal coupling for breathy voice | `speechWaveGenerator.cpp:634-669` |
| **Cascade ducking** | Reduces cascade gain when frication is strong | `speechWaveGenerator.cpp:837-855` |
| **Parallel anti-resonator** | Spectral zero in parallel path for lateral fricatives | `speechWaveGenerator.cpp:798-835` |
| **Trill modulator** | Amplitude LFO for trill consonants (r, ʀ, ʙ) | `speechWaveGenerator.cpp:369-382` |
| **Pitch-sync F1/B1 modulation** | Subglottal coupling during glottal open phase | `speechWaveGenerator.cpp:687-708` |
| **Diplophonia** | Period alternation for creaky voice quality | Frame parameter, modulates pitch |
| **PolyBLEP** | Band-limited step at glottal closure for anti-aliasing | `speechWaveGenerator.cpp:49-66` |
| **3-point pitch contours** | Start/mid/end F0 per frame for tonal languages | `frame.cpp:116-132` |
| **Hermite smoothstep** | S-curve interpolation for smooth formant transitions | `frame.cpp:43-96` |

---

## References

- Klatt 1980: "Software for a cascade/parallel formant synthesizer" (JASA)
- Klatt & Klatt 1990: "Analysis, synthesis, and perception of voice quality variations" (JASA)
- Fant 1985: LF model and Rd parameter derivation
- Zavalishin 2012: "The Art of VA Filter Design" (ZDF topology)
- Valimaki & Huovilainen 2006: PolyBLEP anti-aliasing
- Agrawal & Stevens 1992: Retroflex consonant KLSYN88 parameters (ICSLP)
