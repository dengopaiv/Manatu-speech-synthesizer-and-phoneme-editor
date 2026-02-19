#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phoneme Validation Framework for NVSpeechPlayer.

Two-tier validation:
  Tier 1 (PASS/FAIL): Do synthesized formants match the intended phoneme data?
  Tier 2 (informational): How far are phoneme data values from published references?

Uses LPC-based spectral analysis (no parselmouth dependency).

Usage:
    python tools/phoneme_validator.py                     # All phonemes
    python tools/phoneme_validator.py --category vowels   # Just vowels
    python tools/phoneme_validator.py --phoneme i ɑ u     # Specific phonemes
    python tools/phoneme_validator.py --transitions       # CV pairs
    python tools/phoneme_validator.py --verbose           # Full detail
"""

import os
import sys
import argparse
import io

# Fix Unicode output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import speechPlayer
import ipa
from data import data as phoneme_data
from data import transitions
from tools.spectral_analysis import (
    extract_formants_lpc, estimate_f0, estimate_hnr,
    estimate_spectral_centroid, is_voiced, analyze_segment,
)

SAMPLE_RATE = 96000

# Tier 1 tolerance: synthesized formants must be within this fraction of target
FORMANT_TOLERANCE = 0.15  # 15%

# --- Reference data (Tier 2) ---

# Hillenbrand et al. 1995 adult male averages
REFERENCE_VOWELS = {
    'i':  {'F1': 270, 'F2': 2290, 'F3': 3010},
    'ɪ':  {'F1': 390, 'F2': 1990, 'F3': 2550},
    'e':  {'F1': 390, 'F2': 2300, 'F3': 2850},
    'ɛ':  {'F1': 530, 'F2': 1840, 'F3': 2480},
    'æ':  {'F1': 660, 'F2': 1720, 'F3': 2410},
    'a':  {'F1': 730, 'F2': 1090, 'F3': 2440},
    'ɑ':  {'F1': 730, 'F2': 1090, 'F3': 2440},
    'ɔ':  {'F1': 570, 'F2': 840, 'F3': 2410},
    'o':  {'F1': 390, 'F2': 850, 'F3': 2400},
    'ʊ':  {'F1': 440, 'F2': 1020, 'F3': 2240},
    'u':  {'F1': 300, 'F2': 870, 'F3': 2240},
    'ʌ':  {'F1': 640, 'F2': 1190, 'F3': 2390},
    'ə':  {'F1': 500, 'F2': 1500, 'F3': 2500},
}

# Fricative spectral centroid ranges (Hz) - from Stevens 1998
FRICATIVE_CENTROID_RANGES = {
    's':  (4000, 8000),   # Alveolar: high centroid
    'z':  (4000, 8000),
    'ʃ':  (2500, 5000),   # Postalveolar: medium-high
    'ʒ':  (2500, 5000),
    'f':  (1500, 6000),   # Labiodental: diffuse/flat spectrum
    'v':  (1500, 6000),
    'θ':  (1500, 6000),   # Dental: similar to labiodental
    'ð':  (1500, 6000),
    'x':  (1000, 3000),   # Velar: low centroid
    'ç':  (3000, 6000),   # Palatal: medium
    'h':  (500, 5000),    # Glottal: depends on context
}

# Nasal F1 range (Hz) - all nasals should have low F1
NASAL_F1_MAX = 500


# --- Synthesis helpers ---

def synthesize_phoneme(ipa_char, duration_ms=400, pitch=120):
    """Synthesize a single phoneme using the full ipa.py pipeline.

    Args:
        ipa_char: IPA character string
        duration_ms: Duration in milliseconds
        pitch: Fundamental frequency in Hz

    Returns:
        List of int16 sample values, or empty list on failure.
    """
    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)

    # Use generateSubFramesAndTiming for the full pipeline with KLSYN88_DEFAULTS
    frames = list(ipa.generateSubFramesAndTiming(ipa_char, speed=1, basePitch=pitch, inflection=0))

    if not frames:
        return []

    for frame, min_dur, fade_dur in frames:
        # Override duration to ensure enough signal for analysis
        sp.queueFrame(frame, max(min_dur, duration_ms), fade_dur)

    # Collect samples
    samples = []
    while True:
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        samples.extend(chunk[i] for i in range(len(chunk)))

    return samples


def synthesize_cv_pair(consonant, vowel, pitch=120):
    """Synthesize a CV pair with coarticulation.

    Args:
        consonant: IPA consonant character
        vowel: IPA vowel character
        pitch: Fundamental frequency in Hz

    Returns:
        List of int16 sample values.
    """
    text = consonant + vowel
    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)

    for frame, min_dur, fade_dur in ipa.generateSubFramesAndTiming(text, speed=1, basePitch=pitch, inflection=0):
        sp.queueFrame(frame, min_dur, fade_dur)

    samples = []
    while True:
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        samples.extend(chunk[i] for i in range(len(chunk)))

    return samples


# --- Validation result types ---

class ValidationResult:
    """Result of validating a single phoneme."""

    def __init__(self, ipa_char, category):
        self.ipa_char = ipa_char
        self.category = category
        self.tier1_pass = True
        self.tier1_details = []
        self.tier2_details = []
        self.measured = {}
        self.expected = {}
        self.error_msg = None

    @property
    def status(self):
        if self.error_msg:
            return 'ERROR'
        return 'PASS' if self.tier1_pass else 'FAIL'

    def __str__(self):
        status = self.status
        lines = [f"  [{status}] /{self.ipa_char}/ ({self.category})"]
        if self.error_msg:
            lines.append(f"    Error: {self.error_msg}")
        for detail in self.tier1_details:
            lines.append(f"    {detail}")
        for detail in self.tier2_details:
            lines.append(f"    (ref) {detail}")
        return '\n'.join(lines)


class ValidationReport:
    """Aggregate validation results."""

    def __init__(self):
        self.results = []

    def add(self, result):
        self.results.append(result)

    @property
    def passed(self):
        return sum(1 for r in self.results if r.status == 'PASS')

    @property
    def failed(self):
        return sum(1 for r in self.results if r.status == 'FAIL')

    @property
    def errors(self):
        return sum(1 for r in self.results if r.status == 'ERROR')

    def __str__(self):
        lines = ['=' * 60, 'PHONEME VALIDATION REPORT', '=' * 60, '']

        # Group by category
        categories = {}
        for r in self.results:
            categories.setdefault(r.category, []).append(r)

        for cat, results in categories.items():
            lines.append(f'--- {cat} ---')
            for r in results:
                lines.append(str(r))
            lines.append('')

        lines.append('=' * 60)
        total = len(self.results)
        lines.append(f'Total: {total} | PASS: {self.passed} | FAIL: {self.failed} | ERROR: {self.errors}')
        lines.append('=' * 60)

        return '\n'.join(lines)


# --- Validation functions ---

def _check_formant_accuracy(measured_formants, expected_cf, label, result, tolerance=FORMANT_TOLERANCE):
    """Compare measured formants against expected cascade formants.

    F1 accuracy is the primary PASS/FAIL criterion since LPC reliably
    extracts F1 across all vowel types. F2/F3 are checked with wider
    tolerance because LPC analysis has known limitations for back rounded
    vowels where F1 and F2 are close together.

    Args:
        measured_formants: List of (freq, bw) tuples from LPC
        expected_cf: Dict with 'cf1', 'cf2', 'cf3' keys
        label: Description for messages
        result: ValidationResult to populate
        tolerance: Fractional tolerance (default 0.15 = 15%)
    """
    # F2/F3 get wider tolerance due to LPC limitations
    formant_tolerances = {
        'cf1': tolerance,        # F1: strict (LPC is reliable here)
        'cf2': tolerance * 2,    # F2: relaxed (back rounded vowels)
        'cf3': tolerance * 2.5,  # F3: most relaxed (hardest to resolve)
    }

    for i, key in enumerate(['cf1', 'cf2', 'cf3']):
        expected = expected_cf.get(key, 0)
        if expected <= 0:
            continue

        tol = formant_tolerances[key]

        if i < len(measured_formants):
            measured = measured_formants[i][0]
            deviation = abs(measured - expected) / expected

            result.measured[key] = measured
            result.expected[key] = expected

            if deviation > tol:
                # Only F1 failures cause PASS->FAIL
                if key == 'cf1':
                    result.tier1_pass = False
                result.tier1_details.append(
                    f"F{i+1}: measured {measured:.0f} Hz vs expected {expected:.0f} Hz "
                    f"({deviation:.0%} off, tolerance {tol:.0%})"
                )
            else:
                result.tier1_details.append(
                    f"F{i+1}: {measured:.0f} Hz OK (expected {expected:.0f} Hz, {deviation:.0%} off)"
                )
        else:
            if key == 'cf1':
                result.tier1_pass = False
            result.tier1_details.append(f"F{i+1}: not detected (expected {expected:.0f} Hz)")


def _check_reference_deviation(ipa_char, measured_formants, result):
    """Compare measured formants against published reference (Tier 2, informational)."""
    ref = REFERENCE_VOWELS.get(ipa_char)
    if not ref:
        return

    for i, key in enumerate(['F1', 'F2', 'F3']):
        ref_val = ref.get(key, 0)
        if ref_val <= 0 or i >= len(measured_formants):
            continue

        measured = measured_formants[i][0]
        deviation = abs(measured - ref_val) / ref_val
        direction = 'high' if measured > ref_val else 'low'

        if deviation > 0.20:
            result.tier2_details.append(
                f"F{i+1}: {measured:.0f} Hz vs Hillenbrand {ref_val} Hz ({deviation:.0%} {direction})"
            )


def validate_vowel(ipa_char, verbose=False):
    """Validate a vowel phoneme.

    Tier 1: Synthesize, extract formants via LPC, compare to phoneme data (cf1/cf2/cf3).
    Tier 2: Compare to Hillenbrand reference.

    Args:
        ipa_char: IPA vowel character
        verbose: Include tier 2 reference comparison

    Returns:
        ValidationResult
    """
    result = ValidationResult(ipa_char, 'vowel')

    # Get phoneme data
    pdata = phoneme_data.get(ipa_char)
    if not pdata:
        result.error_msg = f"No phoneme data found for '{ipa_char}'"
        return result

    if not pdata.get('_isVowel'):
        result.error_msg = f"'{ipa_char}' is not marked as a vowel"
        return result

    # Synthesize
    samples = synthesize_phoneme(ipa_char, duration_ms=400, pitch=120)
    if len(samples) < 100:
        result.error_msg = "Synthesis produced too few samples"
        return result

    # Analyze middle 50% (most stable region)
    n = len(samples)
    mid_samples = samples[n // 4: 3 * n // 4]

    analysis = analyze_segment(mid_samples, SAMPLE_RATE)

    # Tier 1: Check synthesis accuracy
    _check_formant_accuracy(analysis.formants, pdata, 'synthesis', result)

    # Check voicing
    if not analysis.is_voiced:
        result.tier1_pass = False
        result.tier1_details.append("Not voiced (expected voiced)")

    # Tier 2: Reference comparison (informational)
    if verbose:
        _check_reference_deviation(ipa_char, analysis.formants, result)

    return result


def validate_fricative(ipa_char, verbose=False):
    """Validate a fricative phoneme.

    Checks spectral centroid range and voicing expectation.

    Args:
        ipa_char: IPA fricative character
        verbose: Include extra details

    Returns:
        ValidationResult
    """
    result = ValidationResult(ipa_char, 'fricative')

    pdata = phoneme_data.get(ipa_char)
    if not pdata:
        result.error_msg = f"No phoneme data found for '{ipa_char}'"
        return result

    # Synthesize
    samples = synthesize_phoneme(ipa_char, duration_ms=300, pitch=120)
    if len(samples) < 100:
        result.error_msg = "Synthesis produced too few samples"
        return result

    n = len(samples)
    mid_samples = samples[n // 4: 3 * n // 4]

    analysis = analyze_segment(mid_samples, SAMPLE_RATE)

    # Check voicing expectation
    expected_voiced = pdata.get('_isVoiced', False)
    if expected_voiced and not analysis.is_voiced:
        result.tier1_details.append("WARNING: Expected voiced but detected as unvoiced")
    elif not expected_voiced and analysis.is_voiced:
        result.tier1_details.append("WARNING: Expected voiceless but detected as voiced")
    else:
        voicing_label = "voiced" if expected_voiced else "voiceless"
        result.tier1_details.append(f"Voicing: {voicing_label} OK")

    # Check spectral centroid
    centroid = analysis.spectral_centroid
    ref_range = FRICATIVE_CENTROID_RANGES.get(ipa_char)
    if ref_range and centroid:
        low, high = ref_range
        if low <= centroid <= high:
            result.tier1_details.append(f"Centroid: {centroid:.0f} Hz OK (range {low}-{high})")
        else:
            result.tier1_details.append(f"Centroid: {centroid:.0f} Hz (expected {low}-{high})")

    # Check noise source is configured (frication or aspiration)
    fric_amp = pdata.get('fricationAmplitude', 0)
    asp_amp = pdata.get('aspirationAmplitude', 0)
    if fric_amp <= 0 and asp_amp <= 0:
        result.tier1_pass = False
        result.tier1_details.append("No noise source (fricationAmplitude and aspirationAmplitude both 0)")
    elif fric_amp > 0:
        result.tier1_details.append(f"fricationAmplitude: {fric_amp} OK")
    else:
        result.tier1_details.append(f"aspirationAmplitude: {asp_amp} OK (aspiration-based fricative)")

    return result


def validate_stop(ipa_char, verbose=False):
    """Validate a stop consonant.

    Checks burst presence in CV context (with /a/).

    Args:
        ipa_char: IPA stop character
        verbose: Include extra details

    Returns:
        ValidationResult
    """
    result = ValidationResult(ipa_char, 'stop')

    pdata = phoneme_data.get(ipa_char)
    if not pdata:
        result.error_msg = f"No phoneme data found for '{ipa_char}'"
        return result

    # Synthesize in CV context
    samples = synthesize_cv_pair(ipa_char, 'a', pitch=120)
    if len(samples) < 100:
        result.error_msg = "Synthesis produced too few samples"
        return result

    # Check for energy spike in first third (burst region)
    n = len(samples)
    burst_region = np.abs(np.array(samples[:n // 3], dtype=np.float64))
    vowel_region = np.abs(np.array(samples[n // 2:], dtype=np.float64))

    burst_rms = np.sqrt(np.mean(burst_region ** 2)) if len(burst_region) > 0 else 0
    vowel_rms = np.sqrt(np.mean(vowel_region ** 2)) if len(vowel_region) > 0 else 0

    if vowel_rms > 0:
        result.tier1_details.append(f"Burst RMS: {burst_rms:.0f}, Vowel RMS: {vowel_rms:.0f}")
    else:
        result.tier1_details.append(f"Burst RMS: {burst_rms:.0f} (vowel silent)")

    # Check voicing
    expected_voiced = pdata.get('_isVoiced', False)
    voicing_label = "voiced" if expected_voiced else "voiceless"
    result.tier1_details.append(f"Expected: {voicing_label}")

    # Check burstAmplitude in phoneme data
    burst_amp = pdata.get('burstAmplitude', 0)
    if burst_amp > 0:
        result.tier1_details.append(f"burstAmplitude: {burst_amp} OK")
    elif pdata.get('_isStop'):
        result.tier1_details.append(f"burstAmplitude: {burst_amp} (stops typically have burst > 0)")

    return result


def validate_nasal(ipa_char, verbose=False):
    """Validate a nasal consonant.

    Checks voicing and low F1.

    Args:
        ipa_char: IPA nasal character
        verbose: Include extra details

    Returns:
        ValidationResult
    """
    result = ValidationResult(ipa_char, 'nasal')

    pdata = phoneme_data.get(ipa_char)
    if not pdata:
        result.error_msg = f"No phoneme data found for '{ipa_char}'"
        return result

    # Synthesize
    samples = synthesize_phoneme(ipa_char, duration_ms=300, pitch=120)
    if len(samples) < 100:
        result.error_msg = "Synthesis produced too few samples"
        return result

    n = len(samples)
    mid_samples = samples[n // 4: 3 * n // 4]

    analysis = analyze_segment(mid_samples, SAMPLE_RATE)

    # Check voicing (all nasals should be voiced)
    if analysis.is_voiced:
        result.tier1_details.append("Voicing: voiced OK")
    else:
        result.tier1_pass = False
        result.tier1_details.append("Not voiced (nasals should be voiced)")

    # Check low F1 (nasals characteristically have low F1)
    if analysis.formants:
        f1 = analysis.formants[0][0]
        if f1 < NASAL_F1_MAX:
            result.tier1_details.append(f"F1: {f1:.0f} Hz OK (< {NASAL_F1_MAX} Hz)")
        else:
            result.tier1_details.append(
                f"F1: {f1:.0f} Hz (expected < {NASAL_F1_MAX} Hz for nasal)"
            )
    else:
        result.tier1_details.append("No formants detected")

    # Check nasal pole/zero are set
    if pdata.get('cfNP', 0) > 0 and pdata.get('caNP', 0) > 0:
        result.tier1_details.append(f"Nasal pole: {pdata['cfNP']} Hz OK")
    else:
        result.tier1_details.append("WARNING: Nasal pole not configured (cfNP/caNP)")

    return result


def validate_cv_transition(consonant, vowel, verbose=False):
    """Validate CV transition using locus equation.

    Checks that F2 onset is pulled toward the consonant's F2 locus.

    Args:
        consonant: IPA consonant character
        vowel: IPA vowel character
        verbose: Include extra details

    Returns:
        ValidationResult
    """
    result = ValidationResult(f"{consonant}{vowel}", 'cv_transition')

    # Get consonant place and locus
    place = transitions.PHONEME_PLACE.get(consonant)
    if not place:
        result.error_msg = f"No place of articulation for '{consonant}'"
        return result

    f2_locus = transitions.F2_LOCUS.get(place)
    if f2_locus is None:
        result.error_msg = f"No F2 locus for place '{place}'"
        return result

    # Get vowel F2 target
    vowel_data = phoneme_data.get(vowel)
    if not vowel_data:
        result.error_msg = f"No phoneme data for vowel '{vowel}'"
        return result
    vowel_f2 = vowel_data.get('cf2', 0)
    if vowel_f2 <= 0:
        result.error_msg = f"Vowel '{vowel}' has no cf2"
        return result

    # Synthesize CV pair
    samples = synthesize_cv_pair(consonant, vowel, pitch=120)
    if len(samples) < 200:
        result.error_msg = "Synthesis produced too few samples"
        return result

    # Extract formant trajectory
    from tools.spectral_analysis import extract_formants_lpc_trajectory
    trajectory = extract_formants_lpc_trajectory(samples, SAMPLE_RATE)

    if len(trajectory) < 4:
        result.error_msg = "Trajectory too short for analysis"
        return result

    # Find F2 values: onset (early frames) and target (late frames)
    onset_f2_values = []
    for frame_data in trajectory[:len(trajectory) // 4]:
        formants = frame_data['formants']
        if len(formants) >= 2:
            onset_f2_values.append(formants[1][0])

    target_f2_values = []
    for frame_data in trajectory[-len(trajectory) // 4:]:
        formants = frame_data['formants']
        if len(formants) >= 2:
            target_f2_values.append(formants[1][0])

    if not onset_f2_values or not target_f2_values:
        result.error_msg = "Could not extract F2 from trajectory"
        return result

    onset_f2 = np.mean(onset_f2_values)
    target_f2 = np.mean(target_f2_values)

    # Expected onset from locus equation: F2_onset = F2_locus + 0.75 * (F2_vowel - F2_locus)
    expected_onset = f2_locus + 0.75 * (vowel_f2 - f2_locus)

    result.measured = {'onset_f2': onset_f2, 'target_f2': target_f2}
    result.expected = {'f2_locus': f2_locus, 'vowel_cf2': vowel_f2, 'expected_onset': expected_onset}

    # Check: onset should be pulled toward locus relative to target
    # The onset F2 should be between the locus and the vowel target
    if vowel_f2 > f2_locus:
        # Vowel F2 is above locus, onset should be below vowel
        pulled = onset_f2 < target_f2
    else:
        # Vowel F2 is below locus, onset should be above vowel
        pulled = onset_f2 > target_f2

    result.tier1_details.append(
        f"Place: {place}, F2 locus: {f2_locus} Hz"
    )
    result.tier1_details.append(
        f"Onset F2: {onset_f2:.0f} Hz, Target F2: {target_f2:.0f} Hz"
    )
    result.tier1_details.append(
        f"Expected onset: {expected_onset:.0f} Hz (locus equation k=0.75)"
    )

    if pulled:
        result.tier1_details.append("F2 onset pulled toward locus: YES")
    else:
        result.tier1_details.append("F2 onset NOT pulled toward locus")

    return result


def validate_all(categories=None, phonemes=None, include_transitions=False, verbose=False):
    """Batch validation of all phonemes.

    Args:
        categories: List of category names to validate ('vowels', 'fricatives', etc.)
                   None = all categories
        phonemes: Specific IPA characters to validate (overrides categories)
        include_transitions: Also validate CV transitions
        verbose: Include tier 2 reference comparisons

    Returns:
        ValidationReport
    """
    report = ValidationReport()

    if phonemes:
        # Validate specific phonemes
        for char in phonemes:
            pdata = phoneme_data.get(char)
            if not pdata:
                r = ValidationResult(char, 'unknown')
                r.error_msg = f"Not found in phoneme data"
                report.add(r)
                continue

            if pdata.get('_isVowel'):
                report.add(validate_vowel(char, verbose))
            elif pdata.get('_isNasal'):
                report.add(validate_nasal(char, verbose))
            elif pdata.get('_isStop'):
                report.add(validate_stop(char, verbose))
            elif pdata.get('fricationAmplitude', 0) > 0:
                report.add(validate_fricative(char, verbose))
            else:
                report.add(validate_vowel(char, verbose))  # Default to vowel-style
        return report

    # Validate by category
    all_cats = categories is None
    do_vowels = all_cats or 'vowels' in (categories or [])
    do_fricatives = all_cats or 'fricatives' in (categories or [])
    do_stops = all_cats or 'stops' in (categories or [])
    do_nasals = all_cats or 'nasals' in (categories or [])

    if do_vowels:
        for char, pdata in phoneme_data.items():
            if pdata.get('_isVowel') and not pdata.get('_components'):
                report.add(validate_vowel(char, verbose))

    if do_fricatives:
        for char in FRICATIVE_CENTROID_RANGES:
            if char in phoneme_data:
                report.add(validate_fricative(char, verbose))

    if do_stops:
        for char, pdata in phoneme_data.items():
            if pdata.get('_isStop') and not pdata.get('_isAfricate'):
                report.add(validate_stop(char, verbose))

    if do_nasals:
        for char, pdata in phoneme_data.items():
            if pdata.get('_isNasal'):
                report.add(validate_nasal(char, verbose))

    if include_transitions:
        # Test representative CV pairs
        cv_pairs = [
            ('p', 'a'), ('p', 'i'), ('p', 'u'),  # Bilabial
            ('t', 'a'), ('t', 'i'), ('t', 'u'),  # Alveolar
            ('k', 'a'), ('k', 'i'), ('k', 'u'),  # Velar
        ]
        for c, v in cv_pairs:
            if c in phoneme_data and v in phoneme_data:
                report.add(validate_cv_transition(c, v, verbose))

    return report


def main():
    parser = argparse.ArgumentParser(
        description='Validate NVSpeechPlayer phoneme synthesis accuracy'
    )
    parser.add_argument('--category', nargs='+',
                       choices=['vowels', 'fricatives', 'stops', 'nasals'],
                       help='Phoneme categories to validate')
    parser.add_argument('--phoneme', nargs='+',
                       help='Specific IPA phonemes to validate')
    parser.add_argument('--transitions', action='store_true',
                       help='Include CV transition validation')
    parser.add_argument('--verbose', action='store_true',
                       help='Include tier 2 reference comparisons')

    args = parser.parse_args()

    report = validate_all(
        categories=args.category,
        phonemes=args.phoneme,
        include_transitions=args.transitions,
        verbose=args.verbose,
    )

    print(report)

    # Exit with non-zero if any failures
    sys.exit(0 if report.failed == 0 and report.errors == 0 else 1)


if __name__ == '__main__':
    main()
