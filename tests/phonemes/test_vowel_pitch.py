# -*- coding: utf-8 -*-
"""
Test vowel /a/ synthesis across pitch contours.

Validates that formant structure remains stable regardless of F0,
and generates WAV files + a comparison report.

Usage:
    python tests/phonemes/test_vowel_pitch.py

Output WAVs and report saved to tests/output/
"""

import sys
import os
import io

# Handle encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import speechPlayer
import ipa
from data import data as phoneme_data
from tests.conftest import save_wav, collect_samples, OUTPUT_DIR, SAMPLE_RATE
from tools.spectral_analysis import extract_formants_lpc

FORMANT_TOLERANCE = 0.15  # 15% for F1 stability across pitch


def _build_vowel_a_frame(pitch_start, pitch_end, pitch_mid=0):
    """Create a frame for /a/ with specified pitch contour.

    Args:
        pitch_start: voicePitch (Hz)
        pitch_end: endVoicePitch (Hz)
        pitch_mid: midVoicePitch (Hz, 0 = linear interpolation)

    Returns:
        speechPlayer.Frame configured for /a/.
    """
    frame = speechPlayer.Frame()
    ipa.applyPhonemeToFrame(frame, phoneme_data['a'])
    frame.preFormantGain = 1.0
    frame.outputGain = 2.0
    frame.voicePitch = pitch_start
    frame.endVoicePitch = pitch_end
    frame.midVoicePitch = pitch_mid
    return frame


# Pitch contour definitions
CONTOURS = {
    'lowering': {
        'desc': 'Lowering (180 -> 80 Hz)',
        'frames': [{'pitch_start': 180, 'pitch_end': 80, 'pitch_mid': 0,
                     'duration_ms': 600, 'fade_ms': 50}],
    },
    'rising': {
        'desc': 'Rising (80 -> 180 Hz)',
        'frames': [{'pitch_start': 80, 'pitch_end': 180, 'pitch_mid': 0,
                     'duration_ms': 600, 'fade_ms': 50}],
    },
    'monotone': {
        'desc': 'Monotone (120 Hz)',
        'frames': [{'pitch_start': 120, 'pitch_end': 120, 'pitch_mid': 0,
                     'duration_ms': 600, 'fade_ms': 50}],
    },
    'wave': {
        'desc': 'Wave (120->160->120->160 Hz)',
        'frames': [
            {'pitch_start': 120, 'pitch_end': 160, 'pitch_mid': 0,
             'duration_ms': 200, 'fade_ms': 30},
            {'pitch_start': 160, 'pitch_end': 120, 'pitch_mid': 0,
             'duration_ms': 200, 'fade_ms': 30},
            {'pitch_start': 120, 'pitch_end': 160, 'pitch_mid': 0,
             'duration_ms': 200, 'fade_ms': 30},
        ],
    },
}


def _synthesize_contour(contour_name):
    """Synthesize /a/ with the given pitch contour.

    Returns:
        List of int16 samples.
    """
    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)
    contour = CONTOURS[contour_name]
    for fdef in contour['frames']:
        frame = _build_vowel_a_frame(fdef['pitch_start'], fdef['pitch_end'],
                                     fdef['pitch_mid'])
        sp.queueFrame(frame, fdef['duration_ms'], fdef['fade_ms'])
    return collect_samples(sp)


def test_pitch_contours():
    """Generate WAV files for all four pitch contours."""
    print("\n=== Test: Pitch Contours (WAV Generation) ===")

    for name, contour in CONTOURS.items():
        samples = _synthesize_contour(name)
        filename = f"vowel_a_pitch_{name}.wav"
        save_wav(filename, samples)
        duration = len(samples) / SAMPLE_RATE
        print(f"  {contour['desc']}: {filename} ({duration:.2f}s, {len(samples)} samples)")

    print("  PASSED")
    return True


def test_pitch_formant_stability():
    """Assert F1 stays within 15% of cf1=850 Hz across all contours."""
    print("\n=== Test: Pitch-Formant Stability ===")

    expected_f1 = phoneme_data['a']['cf1']
    all_passed = True

    for name, contour in CONTOURS.items():
        samples = _synthesize_contour(name)
        n = len(samples)
        mid = samples[n // 4: 3 * n // 4]  # Middle 50%
        formants = extract_formants_lpc(mid, SAMPLE_RATE, num_formants=3)

        if len(formants) < 1:
            print(f"  {name}: SKIP (no formants extracted)")
            continue

        measured_f1 = formants[0][0]
        deviation = abs(measured_f1 - expected_f1) / expected_f1
        passed = deviation <= FORMANT_TOLERANCE
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False

        print(f"  {name}: F1={measured_f1:.0f} Hz (expected {expected_f1}, "
              f"dev={deviation:.1%}) [{status}]")

    assert all_passed, "F1 deviated beyond tolerance in one or more contours"
    print("  PASSED")
    return True


def generate_pitch_report():
    """Write a formant comparison report across pitch contours."""
    print("\n=== Generating Pitch Report ===")

    pdata = phoneme_data['a']
    report_lines = [
        "Vowel Pitch Variation Report",
        "=============================",
        "Vowel: /a/ (open front unrounded)",
        f"Data parameters: cf1={pdata['cf1']}, cb1={pdata['cb1']}, "
        f"cf2={pdata['cf2']}, cb2={pdata['cb2']}, "
        f"cf3={pdata['cf3']}, cb3={pdata['cb3']}",
        "",
    ]

    for name, contour in CONTOURS.items():
        samples = _synthesize_contour(name)
        n = len(samples)
        mid = samples[n // 4: 3 * n // 4]
        formants = extract_formants_lpc(mid, SAMPLE_RATE, num_formants=3)

        report_lines.append(f"Contour: {contour['desc']}")

        measured = []
        deviations = []
        for i, key in enumerate(['cf1', 'cf2', 'cf3']):
            expected = pdata.get(key, 0)
            if i < len(formants) and expected > 0:
                m = formants[i][0]
                dev = abs(m - expected) / expected * 100
                measured.append(f"F{i+1}={m:.0f} Hz")
                deviations.append(f"F{i+1}={dev:.1f}%")
            else:
                measured.append(f"F{i+1}=N/A")
                deviations.append(f"F{i+1}=N/A")

        report_lines.append(f"  Measured: {', '.join(measured)}")
        report_lines.append(f"  Deviation: {', '.join(deviations)}")
        report_lines.append("")

    report_path = os.path.join(OUTPUT_DIR, "vowel_pitch_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print(f"  Report written to {report_path}")
    return True


def run_all_tests():
    """Run all vowel pitch tests."""
    print("=" * 50)
    print("NVSpeechPlayer Vowel Pitch Variation Tests")
    print("=" * 50)

    tests = [
        test_pitch_contours,
        test_pitch_formant_stability,
        generate_pitch_report,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print(f"Output files in: {OUTPUT_DIR}")
    print("=" * 50)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
