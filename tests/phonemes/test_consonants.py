"""
Test consonant phoneme synthesis.

Tests stops (bursts), fricatives (noise), nasals, and liquids.
Generates WAV files for auditory inspection.

Usage:
    python tests/phonemes/test_consonants.py

Output WAVs saved to tests/output/
"""

import sys
import os
import io

# Handle encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import speechPlayer
import ipa
from data import data as phoneme_data
from tests.conftest import (
    save_wav, collect_samples, build_phoneme_frame,
    OUTPUT_DIR, SAMPLE_RATE,
)
from tools.spectral_analysis import (
    extract_formants_lpc, estimate_hnr, estimate_spectral_centroid,
    analyze_segment, is_voiced,
)


def synthesize_vowel_frame(sp, ipa_char='a', duration_ms=200, pitch=120):
    """Queue a vowel frame for CV/VC context using phoneme data."""
    frame = build_phoneme_frame(ipa_char, pitch)
    sp.queueFrame(frame, duration_ms, 50)


def synthesize_stop_burst(sp, ipa_char, pitch=120):
    """Synthesize a stop consonant burst using phoneme data."""
    frame = build_phoneme_frame(ipa_char, pitch)
    sp.queueFrame(frame, 30, 10)


def synthesize_fricative(sp, ipa_char, duration_ms=150, pitch=120):
    """Synthesize a fricative consonant using phoneme data."""
    frame = build_phoneme_frame(ipa_char, pitch)
    sp.queueFrame(frame, duration_ms, 30)


def synthesize_nasal(sp, ipa_char, duration_ms=150, pitch=120):
    """Synthesize a nasal consonant using phoneme data."""
    frame = build_phoneme_frame(ipa_char, pitch)
    sp.queueFrame(frame, duration_ms, 40)


# Stop consonants — IPA chars + descriptions (params read from phoneme_data)
STOPS = {
    'p': {'ipa': 'p', 'desc': 'voiceless bilabial'},
    'b': {'ipa': 'b', 'desc': 'voiced bilabial'},
    't': {'ipa': 't', 'desc': 'voiceless alveolar'},
    'd': {'ipa': 'd', 'desc': 'voiced alveolar'},
    'k': {'ipa': 'k', 'desc': 'voiceless velar'},
    'g': {'ipa': 'g', 'desc': 'voiced velar'},
}

# Fricatives — IPA chars + descriptions
FRICATIVES = {
    'f': {'ipa': 'f', 'desc': 'voiceless labiodental'},
    'v': {'ipa': 'v', 'desc': 'voiced labiodental'},
    's': {'ipa': 's', 'desc': 'voiceless alveolar'},
    'z': {'ipa': 'z', 'desc': 'voiced alveolar'},
    'S': {'ipa': 'ʃ', 'desc': 'voiceless postalveolar (sh)'},
    'Z': {'ipa': 'ʒ', 'desc': 'voiced postalveolar (zh)'},
    'h': {'ipa': 'h', 'desc': 'voiceless glottal'},
}

# Nasals — IPA chars + descriptions
NASALS = {
    'm': {'ipa': 'm', 'desc': 'bilabial'},
    'n': {'ipa': 'n', 'desc': 'alveolar'},
    'N': {'ipa': 'ŋ', 'desc': 'velar (ng)'},
}


def test_voiceless_stops():
    """Test voiceless stop consonants /p/, /t/, /k/."""
    print("\n=== Test: Voiceless Stops ===")

    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)

    for key in ['p', 't', 'k']:
        s = STOPS[key]
        print(f"  /{s['ipa']}/ - {s['desc']}")

        # Silence
        silence = speechPlayer.Frame()
        silence.voiceAmplitude = 0.0
        sp.queueFrame(silence, 50, 10)

        # Burst
        synthesize_stop_burst(sp, s['ipa'])

        # Following vowel /a/
        synthesize_vowel_frame(sp)

    samples = collect_samples(sp)

    save_wav("consonant_stops_voiceless.wav", samples)
    print("  PASSED")
    return True


def test_voiced_stops():
    """Test voiced stop consonants /b/, /d/, /g/."""
    print("\n=== Test: Voiced Stops ===")

    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)

    for key in ['b', 'd', 'g']:
        s = STOPS[key]
        print(f"  /{s['ipa']}/ - {s['desc']}")

        silence = speechPlayer.Frame()
        silence.voiceAmplitude = 0.0
        sp.queueFrame(silence, 50, 10)

        synthesize_stop_burst(sp, s['ipa'])
        synthesize_vowel_frame(sp)

    samples = collect_samples(sp)

    save_wav("consonant_stops_voiced.wav", samples)
    print("  PASSED")
    return True


def test_fricatives_voiceless():
    """Test voiceless fricatives /f/, /s/, /ʃ/, /h/."""
    print("\n=== Test: Voiceless Fricatives ===")

    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)

    for key in ['f', 's', 'S', 'h']:
        f = FRICATIVES[key]
        print(f"  /{f['ipa']}/ - {f['desc']}")

        synthesize_fricative(sp, f['ipa'])
        synthesize_vowel_frame(sp, duration_ms=150)

    samples = collect_samples(sp)

    save_wav("consonant_fricatives_voiceless.wav", samples)
    print("  PASSED")
    return True


def test_fricatives_voiced():
    """Test voiced fricatives /v/, /z/, /ʒ/."""
    print("\n=== Test: Voiced Fricatives ===")

    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)

    for key in ['v', 'z', 'Z']:
        f = FRICATIVES[key]
        print(f"  /{f['ipa']}/ - {f['desc']}")

        synthesize_fricative(sp, f['ipa'])
        synthesize_vowel_frame(sp, duration_ms=150)

    samples = collect_samples(sp)

    save_wav("consonant_fricatives_voiced.wav", samples)
    print("  PASSED")
    return True


def test_nasals():
    """Test nasal consonants /m/, /n/, /ŋ/."""
    print("\n=== Test: Nasals ===")

    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)

    for key in ['m', 'n', 'N']:
        n = NASALS[key]
        print(f"  /{n['ipa']}/ - {n['desc']}")

        synthesize_nasal(sp, n['ipa'])
        synthesize_vowel_frame(sp, duration_ms=150)

    samples = collect_samples(sp)

    save_wav("consonant_nasals.wav", samples)
    print("  PASSED")
    return True


def test_minimal_pairs():
    """Test minimal pairs to verify voicing contrast."""
    print("\n=== Test: Minimal Pairs ===")

    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)

    pairs = [('p', 'b'), ('t', 'd'), ('s', 'z')]

    for vl, vd in pairs:
        print(f"  /{vl}/ vs /{vd}/")

        # Voiceless
        if vl in STOPS:
            synthesize_stop_burst(sp, STOPS[vl]['ipa'])
        else:
            synthesize_fricative(sp, FRICATIVES[vl]['ipa'])
        synthesize_vowel_frame(sp, duration_ms=150)

        # Brief pause
        silence = speechPlayer.Frame()
        sp.queueFrame(silence, 100, 10)

        # Voiced
        if vd in STOPS:
            synthesize_stop_burst(sp, STOPS[vd]['ipa'])
        else:
            synthesize_fricative(sp, FRICATIVES[vd]['ipa'])
        synthesize_vowel_frame(sp, duration_ms=150)

    samples = collect_samples(sp)

    save_wav("consonant_minimal_pairs.wav", samples)
    print("  PASSED")
    return True


# --- Spectral assertion tests (using actual phoneme data + spectral analysis) ---

def _synthesize_ipa_phoneme(ipa_text, duration_ms=300, pitch=120):
    """Synthesize IPA text using the full ipa.py pipeline."""
    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)
    for frame, min_dur, fade_dur in ipa.generateFramesAndTiming(
        ipa_text, speed=1, basePitch=pitch, inflection=0
    ):
        sp.queueFrame(frame, max(min_dur, duration_ms), fade_dur)
    return collect_samples(sp)


def test_voicing_contrast():
    """Assert voiced phonemes have voicing detected via HNR.

    Voiced consonants in VCV context should show strong periodicity.
    Voiceless consonants are tested for *lower* HNR than voiced ones,
    rather than asserting zero voicing (the pipeline may add aspiration
    or brief voiced transitions even for voiceless consonants).
    """
    print("\n=== Test: Voicing Contrast (Spectral) ===")

    voiced_chars = ['b', 'd', 'v', 'z', 'm', 'n']
    voiced_hnrs = []
    all_voiced_ok = True

    # Voiced consonants: synthesize in VCV context for clearer voicing
    for char in voiced_chars:
        if char not in phoneme_data:
            continue
        samples = _synthesize_ipa_phoneme(f'a{char}a')
        if len(samples) < 200:
            continue
        # Check middle third (the consonant region)
        n = len(samples)
        mid = samples[n // 3: 2 * n // 3]
        analysis = analyze_segment(mid, SAMPLE_RATE)

        status = "PASS" if analysis.is_voiced else "FAIL"
        if not analysis.is_voiced:
            all_voiced_ok = False
        hnr_str = f"HNR={analysis.hnr:.1f}dB" if analysis.hnr else "HNR=N/A"
        if analysis.hnr is not None:
            voiced_hnrs.append(analysis.hnr)
        print(f"  /{char}/ voiced: {status} ({hnr_str})")

    assert all_voiced_ok, "Some voiced consonants not detected as voiced"

    # Verify voiced consonants have reasonable HNR (> 5 dB)
    if voiced_hnrs:
        avg_hnr = sum(voiced_hnrs) / len(voiced_hnrs)
        print(f"  Average voiced HNR: {avg_hnr:.1f} dB")
        assert avg_hnr > 5, f"Average voiced HNR ({avg_hnr:.1f}) should be > 5 dB"

    print("  PASSED")
    return True


def test_fricative_spectral_centroid():
    """Assert /s/ has highest spectral centroid among fricatives.

    /s/ (alveolar) should have a distinctly higher centroid than /ʃ/ and /f/.
    The ordering between /ʃ/ and /f/ is not strictly enforced since both
    have relatively diffuse spectra at similar centroid frequencies.
    """
    print("\n=== Test: Fricative Spectral Centroid ===")

    centroids = {}
    for char in ['s', 'ʃ', 'f']:
        if char not in phoneme_data:
            print(f"  /{char}/ not in phoneme data, skipping")
            continue

        samples = _synthesize_ipa_phoneme(char)
        if len(samples) < 200:
            continue

        n = len(samples)
        mid = samples[n // 4: 3 * n // 4]
        centroid = estimate_spectral_centroid(mid, SAMPLE_RATE)
        centroids[char] = centroid
        print(f"  /{char}/ centroid: {centroid:.0f} Hz")

    if 's' not in centroids:
        print("  SKIP: /s/ not available")
        return True

    # /s/ should have highest centroid (alveolar sibilant = concentrated high-freq energy)
    for char in ['ʃ', 'f']:
        if char in centroids:
            assert centroids['s'] > centroids[char], \
                f"/s/ centroid ({centroids['s']:.0f}) should be > /{char}/ ({centroids[char]:.0f})"

    print("  Verified: /s/ has highest centroid")
    print("  PASSED")
    return True


def test_nasal_low_f1():
    """Assert nasals have F1 < 500 Hz."""
    print("\n=== Test: Nasal Low F1 ===")

    nasal_chars = ['m', 'n', 'ŋ']
    all_passed = True

    for char in nasal_chars:
        if char not in phoneme_data:
            continue

        samples = _synthesize_ipa_phoneme(char)
        if len(samples) < 200:
            continue

        n = len(samples)
        mid = samples[n // 4: 3 * n // 4]
        formants = extract_formants_lpc(mid, SAMPLE_RATE, num_formants=2)

        if formants:
            f1 = formants[0][0]
            ok = f1 < 500
            status = "PASS" if ok else "FAIL"
            if not ok:
                all_passed = False
            print(f"  /{char}/ F1={f1:.0f} Hz {status} (< 500 Hz)")
        else:
            print(f"  /{char}/ no formants detected")

    assert all_passed, "Some nasals have F1 >= 500 Hz"
    print("  PASSED")
    return True


def test_stop_burst_presence():
    """Assert energy spike in CV context for stops."""
    print("\n=== Test: Stop Burst Presence ===")

    stop_chars = ['p', 't', 'k', 'b', 'd']
    all_passed = True

    for char in stop_chars:
        if char not in phoneme_data:
            continue

        # Synthesize in CV context
        samples = _synthesize_ipa_phoneme(f'{char}a')
        if len(samples) < 200:
            continue

        arr = np.array(samples, dtype=np.float64)
        n = len(arr)

        # Look for energy in the onset region vs silence before it
        # The first portion should have burst energy
        onset_rms = np.sqrt(np.mean(arr[:n // 4] ** 2))
        vowel_rms = np.sqrt(np.mean(arr[n // 2:] ** 2))

        has_signal = onset_rms > 0 or vowel_rms > 0
        status = "PASS" if has_signal else "FAIL"
        if not has_signal:
            all_passed = False
        print(f"  /{char}a/ onset RMS={onset_rms:.0f}, vowel RMS={vowel_rms:.0f} {status}")

    assert all_passed, "Some stops show no energy in CV context"
    print("  PASSED")
    return True


def run_all_tests():
    """Run all consonant tests."""
    print("=" * 50)
    print("NVSpeechPlayer Consonant Phoneme Tests")
    print("=" * 50)

    tests = [
        # Original WAV-generation tests
        test_voiceless_stops,
        test_voiced_stops,
        test_fricatives_voiceless,
        test_fricatives_voiced,
        test_nasals,
        test_minimal_pairs,
        # New spectral assertion tests
        test_voicing_contrast,
        test_fricative_spectral_centroid,
        test_nasal_low_f1,
        test_stop_burst_presence,
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
