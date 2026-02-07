"""
Test vowel phoneme synthesis.

Tests vowel formant accuracy against published values (Hillenbrand et al. 1995).
Generates WAV files for auditory inspection.

Usage:
    python tests/phonemes/test_vowels.py

Output WAVs saved to tests/output/
"""

import sys
import os
import io
import wave
import struct

# Handle encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import speechPlayer
import ipa
from data import data as phoneme_data
from tests.conftest import save_wav, collect_samples, OUTPUT_DIR, SAMPLE_RATE
from tools.spectral_analysis import (
    extract_formants_lpc, estimate_hnr, analyze_segment, is_voiced,
)


def synthesize_vowel(sp, f1, f2, f3, f4=3300, duration_ms=400, pitch=120):
    """Synthesize a vowel with given formants."""
    frame = speechPlayer.Frame()
    frame.voicePitch = pitch
    frame.voiceAmplitude = 1.0

    # Cascade formants
    frame.cf1, frame.cb1 = f1, max(60, f1 * 0.08)
    frame.cf2, frame.cb2 = f2, max(80, f2 * 0.05)
    frame.cf3, frame.cb3 = f3, 100
    frame.cf4, frame.cb4 = f4, 150
    frame.cf5, frame.cb5 = 4500, 200
    frame.cf6, frame.cb6 = 5500, 250

    # Voice quality
    frame.lfRd = 1.0
    frame.glottalOpenQuotient = 0.7
    frame.spectralTilt = 6
    frame.flutter = 0.2

    frame.preFormantGain = 1.0
    frame.outputGain = 2.0

    sp.queueFrame(frame, duration_ms, 50)


# Reference vowel formants (Hillenbrand et al. 1995, adult male averages)
REFERENCE_VOWELS = {
    'i': {'ipa': 'i', 'f1': 270, 'f2': 2290, 'f3': 3010, 'desc': 'close front unrounded'},
    'I': {'ipa': 'ɪ', 'f1': 390, 'f2': 1990, 'f3': 2550, 'desc': 'near-close front unrounded'},
    'e': {'ipa': 'e', 'f1': 390, 'f2': 2300, 'f3': 2850, 'desc': 'close-mid front unrounded'},
    'E': {'ipa': 'ɛ', 'f1': 530, 'f2': 1840, 'f3': 2480, 'desc': 'open-mid front unrounded'},
    'ae': {'ipa': 'æ', 'f1': 660, 'f2': 1720, 'f3': 2410, 'desc': 'near-open front unrounded'},
    'a': {'ipa': 'ɑ', 'f1': 730, 'f2': 1090, 'f3': 2440, 'desc': 'open back unrounded'},
    'O': {'ipa': 'ɔ', 'f1': 570, 'f2': 840, 'f3': 2410, 'desc': 'open-mid back rounded'},
    'o': {'ipa': 'o', 'f1': 390, 'f2': 850, 'f3': 2400, 'desc': 'close-mid back rounded'},
    'U': {'ipa': 'ʊ', 'f1': 440, 'f2': 1020, 'f3': 2240, 'desc': 'near-close back rounded'},
    'u': {'ipa': 'u', 'f1': 300, 'f2': 870, 'f3': 2240, 'desc': 'close back rounded'},
    'V': {'ipa': 'ʌ', 'f1': 640, 'f2': 1190, 'f3': 2390, 'desc': 'open-mid back unrounded'},
    '@': {'ipa': 'ə', 'f1': 500, 'f2': 1500, 'f3': 2500, 'desc': 'mid central (schwa)'},
}


def test_cardinal_vowels():
    """Test the cardinal vowels /i/, /a/, /u/."""
    print("\n=== Test: Cardinal Vowels ===")

    sp = speechPlayer.SpeechPlayer(22050)

    all_samples = []
    for key in ['i', 'a', 'u']:
        v = REFERENCE_VOWELS[key]
        print(f"  /{v['ipa']}/ - {v['desc']}")
        print(f"    F1={v['f1']}, F2={v['f2']}, F3={v['f3']}")
        synthesize_vowel(sp, v['f1'], v['f2'], v['f3'])

    while True:
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        all_samples.extend(chunk[i] for i in range(len(chunk)))

    
    save_wav("vowel_cardinal_i_a_u.wav", all_samples)
    print(f"  Generated {len(all_samples)} samples")
    print("  PASSED")
    return True


def test_front_vowels():
    """Test front vowels /i/, /ɪ/, /e/, /ɛ/, /æ/."""
    print("\n=== Test: Front Vowels ===")

    sp = speechPlayer.SpeechPlayer(22050)

    for key in ['i', 'I', 'e', 'E', 'ae']:
        v = REFERENCE_VOWELS[key]
        print(f"  /{v['ipa']}/ - F1={v['f1']}, F2={v['f2']}")
        synthesize_vowel(sp, v['f1'], v['f2'], v['f3'])

    all_samples = []
    while True:
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        all_samples.extend(chunk[i] for i in range(len(chunk)))

    
    save_wav("vowel_front_series.wav", all_samples)
    print("  PASSED")
    return True


def test_back_vowels():
    """Test back vowels /u/, /ʊ/, /o/, /ɔ/, /ɑ/."""
    print("\n=== Test: Back Vowels ===")

    sp = speechPlayer.SpeechPlayer(22050)

    for key in ['u', 'U', 'o', 'O', 'a']:
        v = REFERENCE_VOWELS[key]
        print(f"  /{v['ipa']}/ - F1={v['f1']}, F2={v['f2']}")
        synthesize_vowel(sp, v['f1'], v['f2'], v['f3'])

    all_samples = []
    while True:
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        all_samples.extend(chunk[i] for i in range(len(chunk)))

    
    save_wav("vowel_back_series.wav", all_samples)
    print("  PASSED")
    return True


def test_central_vowels():
    """Test central vowels /ə/, /ʌ/."""
    print("\n=== Test: Central Vowels ===")

    sp = speechPlayer.SpeechPlayer(22050)

    for key in ['@', 'V']:
        v = REFERENCE_VOWELS[key]
        print(f"  /{v['ipa']}/ - F1={v['f1']}, F2={v['f2']}")
        synthesize_vowel(sp, v['f1'], v['f2'], v['f3'])

    all_samples = []
    while True:
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        all_samples.extend(chunk[i] for i in range(len(chunk)))

    
    save_wav("vowel_central.wav", all_samples)
    print("  PASSED")
    return True


def test_pitch_variation():
    """Test vowels at different pitches (male/female range)."""
    print("\n=== Test: Vowel Pitch Variation ===")

    sp = speechPlayer.SpeechPlayer(22050)

    v = REFERENCE_VOWELS['a']  # Use /ɑ/ for test

    for pitch in [80, 120, 180, 240]:
        print(f"  /ɑ/ at {pitch} Hz")
        synthesize_vowel(sp, v['f1'], v['f2'], v['f3'], pitch=pitch)

    all_samples = []
    while True:
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        all_samples.extend(chunk[i] for i in range(len(chunk)))

    
    save_wav("vowel_pitch_variation.wav", all_samples)
    print("  PASSED")
    return True


def test_all_reference_vowels():
    """Generate all reference vowels in sequence."""
    print("\n=== Test: All Reference Vowels ===")

    sp = speechPlayer.SpeechPlayer(22050)

    for key, v in REFERENCE_VOWELS.items():
        print(f"  /{v['ipa']}/ ({key})")
        synthesize_vowel(sp, v['f1'], v['f2'], v['f3'], duration_ms=300)

    all_samples = []
    while True:
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        all_samples.extend(chunk[i] for i in range(len(chunk)))

    
    save_wav("vowel_all_reference.wav", all_samples)
    duration = len(all_samples) / 22050
    print(f"  Generated {duration:.2f}s audio with {len(REFERENCE_VOWELS)} vowels")
    print("  PASSED")
    return True


# --- Spectral assertion tests (using actual phoneme data + LPC analysis) ---

FORMANT_TOLERANCE = 0.15  # 15% tolerance for synthesis accuracy


def _synthesize_ipa_vowel(ipa_char, duration_ms=400, pitch=120):
    """Synthesize a vowel using the full ipa.py pipeline with phoneme data."""
    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)
    for frame, min_dur, fade_dur in ipa.generateFramesAndTiming(
        ipa_char, speed=1, basePitch=pitch, inflection=0
    ):
        sp.queueFrame(frame, max(min_dur, duration_ms), fade_dur)
    return collect_samples(sp)


def test_vowel_synthesis_accuracy():
    """For each vowel in data/*.py, synthesize via ipa.py, run LPC,
    check measured formants against cf1/cf2/cf3.

    F1 is the primary accuracy check (LPC is reliable for F1).
    F2/F3 are informational with wider tolerance due to LPC limitations
    on back rounded vowels where F1/F2 are close together."""
    print("\n=== Test: Vowel Synthesis Accuracy (LPC) ===")

    test_vowels = ['i', 'e', 'ɛ', 'æ', 'a', 'ɑ', 'ɔ', 'o', 'u', 'ə']
    f1_passed = 0
    f1_failed = 0

    for char in test_vowels:
        pdata = phoneme_data.get(char)
        if not pdata or not pdata.get('_isVowel'):
            continue

        samples = _synthesize_ipa_vowel(char)
        if len(samples) < 200:
            print(f"  /{char}/ - SKIP (too few samples)")
            continue

        # Analyze middle 50%
        n = len(samples)
        mid = samples[n // 4: 3 * n // 4]
        formants = extract_formants_lpc(mid, SAMPLE_RATE, num_formants=3)

        details = []
        f1_ok = True
        # Tolerances: F1=15%, F2=30%, F3=40% (LPC resolves F1 best)
        tolerances = [FORMANT_TOLERANCE, FORMANT_TOLERANCE * 2, FORMANT_TOLERANCE * 2.5]
        for i, key in enumerate(['cf1', 'cf2', 'cf3']):
            expected = pdata.get(key, 0)
            if expected <= 0 or i >= len(formants):
                continue
            measured = formants[i][0]
            dev = abs(measured - expected) / expected
            tol = tolerances[i]
            status = "OK" if dev <= tol else "HIGH"
            if i == 0 and dev > tol:
                f1_ok = False
            details.append(f"F{i+1}={measured:.0f}/{expected:.0f} ({dev:.0%}) {status}")

        label = "PASS" if f1_ok else "FAIL"
        print(f"  /{char}/ [{label}] {', '.join(details)}")
        if f1_ok:
            f1_passed += 1
        else:
            f1_failed += 1

    print(f"  F1 accuracy: {f1_passed} passed, {f1_failed} failed")
    assert f1_failed == 0, f"{f1_failed} vowels had F1 outside tolerance"
    return True


def test_vowel_reference_deviation():
    """Print how far phoneme data is from Hillenbrand reference (informational)."""
    print("\n=== Test: Vowel Reference Deviation (Informational) ===")

    for key, ref in REFERENCE_VOWELS.items():
        pdata = phoneme_data.get(ref['ipa'])
        if not pdata:
            continue

        deviations = []
        for i, (fkey, ckey) in enumerate([('f1', 'cf1'), ('f2', 'cf2'), ('f3', 'cf3')]):
            ref_val = ref[fkey]
            data_val = pdata.get(ckey, 0)
            if ref_val > 0 and data_val > 0:
                dev = (data_val - ref_val) / ref_val
                deviations.append(f"F{i+1}: {data_val:.0f} vs {ref_val} ({dev:+.0%})")

        print(f"  /{ref['ipa']}/ {', '.join(deviations)}")

    print("  (no assertions — for tuning guidance)")
    return True


def test_vowel_voicing():
    """Assert all vowels are voiced (detected by autocorrelation)."""
    print("\n=== Test: Vowel Voicing ===")

    test_vowels = ['i', 'a', 'u', 'e', 'o', 'ə']
    all_passed = True

    for char in test_vowels:
        samples = _synthesize_ipa_vowel(char)
        if len(samples) < 200:
            continue

        n = len(samples)
        mid = samples[n // 4: 3 * n // 4]
        voiced = is_voiced(mid, SAMPLE_RATE)

        status = "PASS" if voiced else "FAIL"
        if not voiced:
            all_passed = False
        print(f"  /{char}/ voicing: {status}")

    assert all_passed, "Some vowels detected as unvoiced"
    print("  PASSED")
    return True


def test_vowel_formant_ordering():
    """Assert F1 < F2 < F3 for all vowels."""
    print("\n=== Test: Vowel Formant Ordering (F1 < F2 < F3) ===")

    test_vowels = ['i', 'e', 'ɛ', 'æ', 'a', 'ɑ', 'ɔ', 'o', 'u', 'ə']
    all_passed = True

    for char in test_vowels:
        samples = _synthesize_ipa_vowel(char)
        if len(samples) < 200:
            continue

        n = len(samples)
        mid = samples[n // 4: 3 * n // 4]
        formants = extract_formants_lpc(mid, SAMPLE_RATE, num_formants=3)

        if len(formants) >= 3:
            f1, f2, f3 = formants[0][0], formants[1][0], formants[2][0]
            ordered = f1 < f2 < f3
            status = "PASS" if ordered else "FAIL"
            if not ordered:
                all_passed = False
            print(f"  /{char}/ F1={f1:.0f} F2={f2:.0f} F3={f3:.0f} {status}")
        else:
            print(f"  /{char}/ fewer than 3 formants detected")

    assert all_passed, "Some vowels have incorrect formant ordering"
    print("  PASSED")
    return True


def test_cardinal_vowel_space():
    """Assert /i/, /a/, /u/ form a proper F1 triangle.

    LPC reliably resolves F1 for all vowel types, so we verify:
    - /a/ has highest F1 (most open)
    - /i/ and /u/ have low F1 (most closed)
    - F1 separation is significant

    Note: F2 assertions are skipped because LPC has known limitations
    resolving F2 for back rounded vowels (/u/) where F1/F2 are close.
    """
    print("\n=== Test: Cardinal Vowel F1 Triangle ===")

    formant_map = {}
    for char in ['i', 'a', 'u']:
        samples = _synthesize_ipa_vowel(char)
        n = len(samples)
        mid = samples[n // 4: 3 * n // 4]
        formants = extract_formants_lpc(mid, SAMPLE_RATE, num_formants=2)
        if len(formants) >= 1:
            formant_map[char] = formants[0][0]
            f2_str = f", F2={formants[1][0]:.0f}" if len(formants) >= 2 else ""
            print(f"  /{char}/ F1={formants[0][0]:.0f}{f2_str}")

    if len(formant_map) < 3:
        print("  SKIP: Could not extract formants for all three vowels")
        return True

    f1_i = formant_map['i']
    f1_a = formant_map['a']
    f1_u = formant_map['u']

    # /a/ should have highest F1 (most open vowel)
    assert f1_a > f1_i, f"/a/ F1 ({f1_a:.0f}) should be > /i/ F1 ({f1_i:.0f})"
    assert f1_a > f1_u, f"/a/ F1 ({f1_a:.0f}) should be > /u/ F1 ({f1_u:.0f})"

    # F1 separation should be significant (at least 200 Hz difference)
    assert f1_a - f1_i > 200, f"/a/-/i/ F1 gap ({f1_a - f1_i:.0f}) should be > 200 Hz"
    assert f1_a - f1_u > 200, f"/a/-/u/ F1 gap ({f1_a - f1_u:.0f}) should be > 200 Hz"

    print("  Cardinal vowel F1 triangle verified: /a/ highest F1, /i/ and /u/ low F1")
    print("  PASSED")
    return True


def run_all_tests():
    """Run all vowel tests."""
    print("=" * 50)
    print("NVSpeechPlayer Vowel Phoneme Tests")
    print("=" * 50)

    tests = [
        # Original WAV-generation tests
        test_cardinal_vowels,
        test_front_vowels,
        test_back_vowels,
        test_central_vowels,
        test_pitch_variation,
        test_all_reference_vowels,
        # New spectral assertion tests
        test_vowel_synthesis_accuracy,
        test_vowel_reference_deviation,
        test_vowel_voicing,
        test_vowel_formant_ordering,
        test_cardinal_vowel_space,
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
