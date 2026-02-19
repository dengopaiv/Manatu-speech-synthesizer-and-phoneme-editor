# Manatu Synthesis Changes Log

This document tracks changes to the synthesis engine, phoneme data, and processing pipeline.

## Format
Each entry documents:
- Date and summary
- What changed
- How phonemes are handled differently
- Files modified

---

## [2026-02-19] - Cascade HF Shelf Compensation + sourceBrightness Cleanup

### Summary
Restored HF shelf filter on cascade output to compensate for the cascade formant chain's structural HF loss (~57 dB at 8 kHz through 6 series allPole resonators). Removed dead `sourceBrightness` parameter from all vowel phoneme data. This loss exists regardless of glottal model — removing the shelf during the LF restoration was incorrect.

### What Changed

**Cascade HF shelf** (`src/speechWaveGenerator.cpp`):
- Added `HFShelfFilter` class: 1st-order HPF shelf topology `y = x + boost * HPF(x)`, transparent at DC
- Corner frequency: 3000 Hz, Boost: +6 dB (reduced from BLIT-era +9 dB — LF model has more natural HF content than the aggressively-lowpassed BLIT, so less compensation needed)
- Applied only to cascade output, after ducking and before mixing with parallel path
- Parallel path (fricative/sibilant HF) is unaffected

**sourceBrightness cleanup** (`data/vowels_*.py`):
- Removed `sourceBrightness` entries from all 39 vowel phoneme dicts (front, back, central, nasalized)
- These controlled the BLIT's glottal lowpass (fg = F0 × value) which no longer exists
- Field kept in `frame.h` and `speechPlayer.py` for ABI stability

**Editor** (`editor/phoneme_editor_constants.py`):
- Updated `sourceBrightness` slider description to indicate it's reserved/inactive

### Files Modified
- `src/speechWaveGenerator.cpp`, `data/vowels_front.py`, `data/vowels_back.py`, `data/vowels_central.py`, `data/vowels_nasalized.py`, `editor/phoneme_editor_constants.py`, `docs/CHANGELOG.md`, `docs/SYNTHESIS.md`, `docs/MODIFICATIONS.md`

---

## [2026-02-19] - Restore LF Glottal Model + 4x Oversampling + 96 kHz Output

### Summary
Reverted BLIT glottal source back to the LF (Liljencrants-Fant) time-domain model with improved anti-aliasing. Upgraded from 2x Bartlett oversampling to 4x halfband FIR decimation. Moved output sample rate from 44.1 kHz to 96 kHz for minimal ZDF frequency warping. Restored 12 dB/oct spectral tilt with 5 kHz reference. Removed HFShelfFilter (BLIT compensation hack no longer needed).

### What Changed

**Glottal source** (`src/speechWaveGenerator.cpp`):
- Replaced BLIT (band-limited impulse train) with restored LF model using `computeGlottalWave()` — three-phase waveform (raised cosine opening, cosinusoidal closing, exponential return) with Rd-dependent parameter mapping
- Restored `polyBLEP()` anti-aliasing at cycle boundary and te excitation point
- Restored DC centering: `voice = glottalWave * 2.0 - ampNorm`
- Removed `computeBLIT()`, `integratorState`, `glottalLpState` BLIT-specific state

**4x oversampling** (`src/speechWaveGenerator.cpp`):
- Added `HalfbandDecimator` class: 7-tap halfband FIR with structural zeros, >60 dB stopband, only 4 multiplies per output sample
- VoiceGenerator evaluates LF waveform at 4 symmetric phases per output sample with PolyBLEP at each (dt_os = dt/4 → more precise corrections)
- Two cascaded HalfbandDecimator stages: 4x→2x→1x decimation
- Replaced 3-point symmetric Bartlett (2x) decimation

**Spectral tilt** (`src/speechWaveGenerator.cpp`):
- Restored two-stage cascaded lowpass (12 dB/oct) replacing single-stage (6 dB/oct)
- Reference frequency restored to 5 kHz (from 6 kHz BLIT version)

**HFShelfFilter removed** (`src/speechWaveGenerator.cpp`):
- Removed `HFShelfFilter` class and its usage in `SpeechWaveGeneratorImpl` — the +9 dB global HF boost above 3 kHz was a BLIT compensation hack

**Sample rate 44100 → 96000**:
- Updated in all Python files, tools, tests, docs, and C++ comments
- 96 kHz benefits: ZDF warping 4% at 8 kHz (vs 20% at 44.1 kHz), Nyquist at 48 kHz (no speech content near it), LF model runs at 384 kHz with 4x oversampling

### Files Modified
- `src/speechWaveGenerator.cpp`, `nvdaAddon/synthDrivers/nvSpeechPlayer/__init__.py`, `conlang_gui.py`, `conlang_gui_wx.py`, `tests/conftest.py`, `editor/audio_manager.py`, `tools/phoneme_validator.py`, `tools/consonant_diagnostic.py`, `tools/fricative_autotuner.py`, `tools/vowel_autotuner.py`, `docs/GETTING_STARTED.md`, `docs/SYNTHESIS.md`, `docs/MODIFICATIONS.md`, `docs/CHANGELOG.md`

---

## [2026-02-17] - Brightness, Documentation & Stability Audit

### Summary
Addressed compounding HF attenuation that made synthesizer output muffled. Three layers of attenuation were identified and reduced: excessive voiced fricative `spectralTilt`, high open vowel `lfRd`, and aggressive tilt filter reference frequency.

### What Changed

**Spectral tilt filter** (`src/speechWaveGenerator.cpp`):
- Reference frequency raised from 5 kHz to 6 kHz. All `spectralTilt` values now produce ~20% higher cutoff frequencies (e.g., tilt=4 now gives fc=4878 Hz instead of 4065 Hz).

**Voiced fricative brightness** (`data/fricatives.py`):
- `spectralTilt` reduced from 7 to 4 for 10 voiced fricatives: v, z, ʒ, ð, β, ʝ, ʐ, ʑ, ɣ, ʁ. Cutoff moves from ~1915 Hz to ~4878 Hz. Pharyngeal/epiglottal fricatives (ʕ, ʢ, ħ, ʜ, ɦ, ɮ) intentionally unchanged.

**Open vowel voice quality** (`data/vowels_front.py`, `data/vowels_back.py`, `data/vowels_central.py`, `data/vowels_nasalized.py`):
- Open-mid vowels (ɛ, œ, ɔ, ʌ, ɜ, ɞ): `lfRd` 2.0-2.3 → 1.5-1.7
- Near-open/open vowels (a, æ, ɑ, ɒ, ɐ, ɶ): `lfRd` 1.7-2.0 → 1.3-1.5
- All open/open-mid vowels: `spectralTilt` 3 → 2
- Nasalized vowels (ã, ɛ̃, ɔ̃, œ̃) updated to match base vowel changes

**New tools and tests**:
- `tools/spectral_analysis.py`: Added `estimate_hf_energy_ratio()` for quantitative brightness measurement
- `tests/synthesis/test_spectral.py`: Brightness regression tests (HF ratio, centroid ordering, formant prominence)
- `tools/phoneme_audit.py`: Parameter consistency scanner with CRITICAL/WARNING/INFO severity grouping

**Documentation**:
- `docs/MODIFICATIONS.md`: New file cataloging all deviations from KLSYN88 (Klatt & Klatt 1990)
- `docs/SYNTHESIS.md`: Fixed all stale line number references, updated for current engine state (jitter/shimmer, PeakLimiter, colored noise, PolyBLEP, DC block, parallel anti-resonator, tilt filter)
- `docs/CHANGELOG.md`: Added entries for all commits since 2026-02-11

### Files Modified
- `src/speechWaveGenerator.cpp`, `data/fricatives.py`, `data/vowels_front.py`, `data/vowels_back.py`, `data/vowels_central.py`, `data/vowels_nasalized.py`, `tools/spectral_analysis.py`, `tools/phoneme_audit.py`, `tests/synthesis/test_spectral.py`, `docs/SYNTHESIS.md`, `docs/MODIFICATIONS.md`, `docs/CHANGELOG.md`

---

## [2026-02-16] - Speed Up Consonant Tests

### Summary
Optimized consonant test suite for faster execution by using bulk sample extraction and natural phoneme durations.

### What Changed
- `tests/phonemes/test_consonants.py`: Switched from frame-by-frame sample collection to bulk `collect_samples()` helper. Reduced test phoneme durations from 400ms to natural durations (~100-200ms).

---

## [2026-02-15] - Editor Presets & Settings

### Summary
Added JSON preset overlay system for the phoneme editor and updated development settings.

### What Changed
- `editor/presets/`: Added tuned preset files for editor use
- `.claude/settings.local.json`: Updated local development settings

---

## [2026-02-15] - Voiced Fricative Refinement: /v/ Cascade Resonance

### Summary
Reduced /v/ parallel bypass to preserve cascade resonance, preventing nasal-like quality.

### What Changed
- `data/fricatives.py`: /v/ `parallelBypass` tuned to balance cascade voice quality with frication noise routing.

---

## [2026-02-14] - C++ Engine Cleanup & ABI Fix

### Summary
Fixed Python/C++ struct ABI mismatch, removed deprecated parameters, and fixed voiced fricative detection in the VC coarticulation path.

### What Changed
- `src/frame.h`, `src/frame.cpp`: Aligned frame struct layout between C++ and Python ctypes binding
- `speechPlayer.py`: Updated ctypes struct to match C++ layout
- `data/*.py`: Removed deprecated `openQuotientShape`/`speedQuotient` parameters
- `ipa.py`: Fixed VC offset coarticulation to properly detect voiced fricatives

---

## [2026-02-14] - C++ Engine Review: Audio Quality & Portability

### Summary
Comprehensive review and cleanup of the C++ synthesis engine covering audio quality, numerical stability, and code portability.

### What Changed
- `src/speechWaveGenerator.cpp`: Various audio quality and portability improvements identified in engine review

---

## [2026-02-13] - CV/VC Coarticulation Waypoints

### Summary
Extended coarticulation system with bidirectional CV/VC waypoints and editor visualization.

### What Changed
- `ipa.py`: Added VC (vowel-to-consonant) coarticulation offset for fricatives, semivowels, and liquids
- `data/transitions.py`: Added CV/VC waypoint calculations
- Editor: Added coarticulation trajectory visualization

---

## [2026-02-13] - Bilabial Stop Improvements

### Summary
Applied frication-based bilabial release to all bilabial stops and refined burst parameters.

### What Changed
- `data/stops.py`: Updated /p/, /b/, /pʼ/, /ɓ/, /ᵐb/ with frication-based release instead of simple burst
- `data/fricatives.py`: Refined ç/ɕ fricative parameters; deleted stale editor presets
- `data/liquids_glides.py`: Refined w/j glide parameters

---

## [2026-02-12] - Parallel Anti-Resonator & Lateral Fricatives

### Summary
Added parallel anti-resonator support and completely reworked lateral fricatives /ɬ/ and /ɮ/.

### What Changed
- `src/speechWaveGenerator.cpp`: Added parallel anti-resonator (notch filter) in parallel formant path
- `src/frame.h`, `speechPlayer.py`: Added `parallelAntiFreq`, `parallelAntiBw` fields
- `data/fricatives.py`: Reworked /ɬ/ and /ɮ/ with anti-resonator at 3500 Hz lateral zero
- `data/affricates.py`: Added lateral affricates t͡ɬ, d͡ɮ

---

## [2026-02-12] - Velar/Uvular Aspiration Routing & Uvular Trill

### Summary
Switched velar/uvular fricatives from frication to aspiration routing, added subtle uvular trill modulation.

### What Changed
- `data/fricatives.py`: /x/, /ɣ/, /χ/, /ʁ/ now use `aspirationAmplitude` instead of `fricationAmplitude` for more natural posterior fricative quality. Added `trillRate`/`trillDepth` for uvular trill.

---

## [2026-02-12] - F4-F6 Bandwidth Normalization

### Summary
Normalized F4-F6 bandwidths to Q=4.0 across core stops and fricatives for consistency.

### What Changed
- `data/stops.py`, `data/fricatives.py`: Standardized cb4/cb5/cb6 and pb4/pb5/pb6 using Q=4.0 formula (bandwidth = frequency / 4.0).

---

## [2026-02-12] - Fricative Tuning: /v/, /f/, /z/, /ð/, /s/, /θ/

### Summary
Multi-session editor-tuned refinement of core fricative parameters for voiced pattern alignment.

### What Changed
- `data/fricatives.py`: Tuned /v/ (removed voicebar, boosted frication), /z/ (voicebar + sibilant spectrum), /ð/ (voicebar + dental spectrum), /f/ and /θ/ (spectral shape), /s/ (HF parallel formants)

---

## [2026-02-12] - Plosive Burst Spectral Coloring

### Summary
Added `burstNoiseColor` parameter for place-appropriate spectral shaping of stop bursts.

### What Changed
- `src/speechWaveGenerator.cpp`: BurstGenerator now supports pink noise via `burstNoiseColor` parameter (0=white, 1=pink)
- `src/frame.h`, `speechPlayer.py`: Added `burstNoiseColor` field
- `data/stops.py`: Bilabial (/p/, /b/) and uvular (/q/, /ɢ/) stops use pink noise bursts

---

## [2026-02-12] - Extended Phonemes: Clicks, Ejectives, Implosives, Prenasalized, Epiglottals

### Summary
Major expansion of the phoneme inventory with non-pulmonic and extended consonants.

### What Changed
- `data/clicks.py`: 5 click consonants (ǀ, ǁ, ǂ, ǃ, ʘ) with forward/velar burst phases
- `data/stops.py`: 6 ejective consonants (pʼ, tʼ, kʼ, qʼ) with IPA diacritic support; 5 implosive consonants (ɓ, ɗ, ʄ, ɠ, ʛ) with voicebar through closure; 3 prenasalized stops (ᵐb, ⁿd, ᵑɡ)
- `data/fricatives.py`: 2 epiglottal fricatives (ʜ, ʢ), 2 alveolo-palatal fricatives (ɕ, ʑ)
- `data/affricates.py`: 5 new affricates (clicks as affricates, velarized laterals)
- `data/special.py`: Generic phoneme modifiers with acoustic-aware scaling

---

## [2026-02-11] - Engine Improvements for Plosive Burst Audibility

### Summary
Two C++ engine changes to improve stop burst audibility, particularly for bilabial /p/ which has the least energy margin among plosives.

### What Changed
- `src/speechWaveGenerator.cpp` (BurstGenerator): Onset transient duration now scales with burst filter frequency. Low-frequency bursts (/p/ at 1500 Hz) get 2.0ms instead of the previous 1.5ms, giving the ZDF bandpass filter enough cycles to ring up. High-frequency bursts (/t/, /k/) are unchanged (1.5ms floor).
- `src/speechWaveGenerator.cpp` (PeakLimiter): Added fast-release mode (5ms time constant) that activates during silence (preGain < 0.01). During stop closure gaps, the limiter now recovers ~91% of gain reduction vs ~21% with the standard 50ms release. Bursts arrive at near-unity limiter gain. No effect during normal speech.

### How Phonemes Are Handled Differently
- /p/,/b/ bursts: onset transient 1.5ms → 2.0ms (filter fully rings up before onset fades)
- /q/,/ɢ/ bursts: onset transient 1.5ms → 2.5ms (lowest filter frequency)
- /t/,/d/,/k/,/g/ bursts: unchanged (high filter frequency, 1.5ms floor sufficient)
- All stops after vowels: limiter recovers during closure gap, burst not attenuated

### Files Modified
- `src/speechWaveGenerator.cpp`

---

## [2026-02-11] - Unify Stops with Phase System

### Summary
Generalized the affricate `_phases` system to work for all stop consonants, enabling ejectives, geminates, and Estonian quantity distinctions as pure data additions.

### What Changed
- `ipa.py`: Renamed `_isAffricatePhase` → `_isPhase` throughout timing logic
- `ipa.py`: Reordered timing checks so `_isPhase` is checked before `_isStop` (taps/flaps without `_phases` fall through to `_isStop` fallback)
- `ipa.py`: Gap duration now data-driven via `_closureDuration` (defaults to 12ms)
- `ipa.py`: `_closureDuration` propagated from phoneme data into pre-stop gap frames
- `data/stops.py`: Added `_phases` to all 14 stops — voiceless 10ms/3ms fade, voiced 8ms/3ms fade (reflecting natural VOT differences)

### How Phonemes Are Handled Differently
- Stops now use the same `_phases` expansion path as affricates instead of hardcoded single-frame timing
- Closure duration is configurable per-phoneme via `_closureDuration` (e.g., `180` for Estonian overlong)
- Taps/flaps (ɾ, ɽ, ⱱ) are unaffected — they have `_isStop` but no `_phases`, so they use the fallback path
- Auto-aspiration continues to work: last phase frame inherits `_isStop`/`_isVoiced` from base data

### Enables (future, no code changes needed)
- Ejectives (pʼ, tʼ, kʼ): multi-phase stop + glottal closure as pure data
- Estonian three-way quantity: short/long/overlong via `_closureDuration`
- Geminates: extended closure duration as data

---

## [2026-02-11] - Self-Sustaining Burst & Stop Latency Reduction

### Summary
Made BurstGenerator self-sustaining so burst envelopes complete independently of frame transitions. Removed fadeOut workaround frame and tightened stop timing for lower latency.

### What Changed
- `src/speechWaveGenerator.cpp`: BurstGenerator now captures burst parameters (amplitude, duration, filter freq/bw) at trigger time and uses stored values for the entire envelope, preventing frame interpolation from corrupting mid-burst parameters
- `ipa.py`: Removed `_fadeOutToSilence` frame insertion before stop gaps — no longer needed since burst is self-sustaining
- `ipa.py`: Tightened stop timing: pre-stop gap 20ms→12ms, aspiration 20ms→15ms, burst fade 5ms→3ms

### Gap Analysis (Klatt Literature Review)
Compared our labial plosive implementation against Klatt 1980, Stevens Ch.7, and DECtalk:
- **Well-covered**: bypass path for diffuse bilabial character, diffuse-falling parallel formant weighting, onset transient, lip turbulence, instant-step for burst parameters
- **Systemic gaps for future work** (all stops, not bilabial-specific):
  - F1 cutback: per-formant interpolation timing during burst-to-vowel transition
  - Vowel-dependent burst spectrum: coarticulated burst filter frequencies (mainly affects velars)

### How Phonemes Are Handled Differently
- Stop bursts now run to completion even when frame transitions occur mid-burst
- One fewer frame per stop sequence (fadeOut removed), reducing total stop duration
- Tighter timing improves responsiveness at high speech rates

---

## [2026-02-11] - Phase 3: Extended Consonant Validation & Testing

### Summary
Validated, tuned, and added comprehensive test coverage for all Phase 3 extended consonants: palatals, uvulars, pharyngeals, bilabial fricatives, trills, extended laterals, and approximants.

### What Changed
- `data/transitions.py`: Added ʀ (uvular trill) and ʙ (bilabial trill) to PHONEME_PLACE coarticulation map
- `data/nasals.py`: Tuned ɲ cf2 from 2000→2200 Hz (better palatal place match)
- `data/fricatives.py`: Tuned ç cf2 from 2100→2200 Hz, ʝ cf2 from 2100→2300 Hz (better separation from postalveolar ʃ/ʒ at 1840)
- `data/liquids_glides.py`: Tuned ʙ trillRate from 28→24 Hz (bilabial trills not faster than alveolar ~25 Hz)
- `tests/phonemes/test_consonants.py`: Added 14 new test functions covering all extended consonants

### New Tests Added
**WAV-generation tests** (CV context with /ɑ/):
- Palatal stops (c, ɟ), uvular stops (q, ɢ)
- Palatal fricatives (ç, ʝ), uvular fricatives (χ, ʁ)
- Pharyngeal fricatives (ħ, ʕ), bilabial fricatives (ɸ, β)
- Extended nasals (ɲ, ɴ, ɱ), trills (r, ʀ, ʙ)
- Extended laterals (ʎ, ʟ), extended approximants (ʋ, ɻ, ɰ)

**Spectral assertion tests** (parameter validation):
- Palatal high F2 (> 2000 Hz for c, ɟ, ç, ʝ, ɲ)
- Uvular low F2 (< 1400 Hz for q, ɢ, χ, ʁ, ɴ)
- Pharyngeal high F1 (> 500 Hz for ħ, ʕ)
- Place minimal pairs (c vs k, q vs k, ɲ vs n)

### How Phonemes Are Handled Differently
- Palatal fricatives now have higher F2 separation from postalveolars
- Palatal nasal ɲ better matches palatal stop formant range
- Bilabial trill uses more realistic oscillation rate
- All extended consonants now have coarticulation support via PHONEME_PLACE

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

### Future Work
- F1 cutback: per-formant interpolation timing during burst-to-vowel transition
- Vowel-dependent burst spectrum: coarticulated burst filter frequencies (mainly velars)
- Dynamic velic model for more realistic nasal coupling
- Physical modeling refinements for click articulation
