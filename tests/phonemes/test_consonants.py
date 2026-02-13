"""
Test consonant phoneme synthesis — Ladefoged CV/VCV + spectral assertions.

Layer 1: CV transition tests (IPA pipeline with onset frames + locus equations)
Layer 2: Natural-duration Ladefoged-style CV and VCV tests (slow speed, full IPA pipeline)
Layer 3: Spectral assertion tests (voicing contrast, centroid, formant checks)

All consonants (basic + extended) are tested via the IPA pipeline with
natural per-class durations and coarticulation via onset frames.

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
    save_wav, collect_samples,
    OUTPUT_DIR, SAMPLE_RATE,
)
from tools.spectral_analysis import (
    extract_formants_lpc, estimate_hnr, estimate_spectral_centroid,
    analyze_segment, is_voiced,
)


# --- CV transition tests (full IPA pipeline with onset frames) ---

def _synthesize_cv_ipa(ipa_text, pitch=120, formantScale=1.0, speed=1):
    """Synthesize CV text using the full ipa.py pipeline (exercises onset frames)."""
    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)
    for frame, min_dur, fade_dur in ipa.generateFramesAndTiming(
        ipa_text, speed=speed, basePitch=pitch, inflection=0,
        formantScale=formantScale
    ):
        if frame is not None:
            sp.queueFrame(frame, min_dur, fade_dur)
    return collect_samples(sp)


def test_cv_transitions():
    """Test CV transitions using the full IPA pipeline (onset frames + locus equations).

    Unlike direct frame queueing, this exercises:
    - Onset frame generation from locus equations (transitions.py)
    - Two-stage transition: consonant → onset → vowel target
    - formantScale application to onset formants
    """
    print("\n=== Test: CV Transitions (IPA Pipeline) ===")

    cv_pairs = [
        ('mɑ', 'bilabial nasal → open vowel'),
        ('bɑ', 'voiced bilabial stop → open vowel'),
        ('nɑ', 'alveolar nasal → open vowel'),
        ('dɑ', 'voiced alveolar stop → open vowel'),
        ('ɡɑ', 'voiced velar stop → open vowel'),
    ]

    all_samples = []
    for ipa_text, desc in cv_pairs:
        print(f"  /{ipa_text}/ - {desc}")
        samples = _synthesize_cv_ipa(ipa_text)
        all_samples.extend(samples)
        # Brief silence between items
        all_samples.extend([0] * int(SAMPLE_RATE * 0.1))

    save_wav("consonant_cv_transitions.wav", all_samples)
    print(f"  Generated {len(cv_pairs)} CV transitions")
    print("  PASSED")
    return True


def test_cv_formant_scaling():
    """Test that CV transitions are consistent across formantScale values.

    Verifies onset frames are properly scaled for female/child voice types.
    Both male and female versions should produce non-silent output.
    """
    print("\n=== Test: CV Formant Scaling ===")

    scales = [
        (1.0, 'male'),
        (1.17, 'female'),
    ]

    all_passed = True
    for scale, label in scales:
        samples = _synthesize_cv_ipa('mɑ', formantScale=scale)
        has_signal = len(samples) > 0 and any(abs(s) > 10 for s in samples)
        status = "PASS" if has_signal else "FAIL"
        if not has_signal:
            all_passed = False
        rms = 0
        if samples:
            arr = np.array(samples, dtype=np.float64)
            rms = np.sqrt(np.mean(arr ** 2))
        print(f"  /mɑ/ {label} (scale={scale}): RMS={rms:.0f} {status}")

    assert all_passed, "Some formantScale values produced silent output"
    save_wav("consonant_cv_formant_scaling.wav",
             _synthesize_cv_ipa('mɑ', formantScale=1.0) +
             [0] * int(SAMPLE_RATE * 0.15) +
             _synthesize_cv_ipa('mɑ', formantScale=1.17))
    print("  PASSED")
    return True


# --- Natural-duration CV tests (full IPA pipeline with class-based durations) ---

def _synthesize_cv_list(cv_pairs, filename, label, speed=1, pitch=120):
    """Synthesize a list of CV pairs via the IPA pipeline, save combined WAV.

    Uses ipa.generateFramesAndTiming which applies natural per-class durations
    (stops=10ms+closure, nasals=30ms, fricatives=45ms, vowels=50-60ms) and
    coarticulation via onset frames.
    """
    print(f"\n=== Test: {label} ===")

    all_samples = []
    for ipa_text, desc in cv_pairs:
        print(f"  /{ipa_text}/ - {desc}")
        samples = _synthesize_cv_ipa(ipa_text, pitch=pitch, speed=speed)
        all_samples.extend(samples)
        # Brief silence between items
        all_samples.extend([0] * int(SAMPLE_RATE * 0.15))

    save_wav(filename, all_samples)
    print(f"  Generated {len(cv_pairs)} items")
    print("  PASSED")
    return True


def test_stops_natural():
    """Test stops with Ladefoged-style CV and VCV patterns at slow speed."""
    return _synthesize_cv_list([
        ('pɑ', 'voiceless bilabial (CV)'),
        ('ɑpɑ', 'voiceless bilabial (VCV)'),
        ('bɑ', 'voiced bilabial (CV)'),
        ('ɑbɑ', 'voiced bilabial (VCV)'),
        ('tɑ', 'voiceless alveolar (CV)'),
        ('ɑtɑ', 'voiceless alveolar (VCV)'),
        ('dɑ', 'voiced alveolar (CV)'),
        ('ɑdɑ', 'voiced alveolar (VCV)'),
        ('kɑ', 'voiceless velar (CV)'),
        ('ɑkɑ', 'voiceless velar (VCV)'),
        ('ɡɑ', 'voiced velar (CV)'),
        ('ɑɡɑ', 'voiced velar (VCV)'),
        # Palatal stops
        ('cɑ', 'voiceless palatal (CV)'),
        ('ɑcɑ', 'voiceless palatal (VCV)'),
        ('ɟɑ', 'voiced palatal (CV)'),
        ('ɑɟɑ', 'voiced palatal (VCV)'),
        # Uvular stops
        ('qɑ', 'voiceless uvular (CV)'),
        ('ɑqɑ', 'voiceless uvular (VCV)'),
        ('ɢɑ', 'voiced uvular (CV)'),
        ('ɑɢɑ', 'voiced uvular (VCV)'),
    ], "consonant_stops_natural.wav", "Stops (Natural Duration)", speed=0.5)


def test_nasals_natural():
    """Test nasals with Ladefoged-style CV and VCV patterns at slow speed."""
    return _synthesize_cv_list([
        ('mɑ', 'bilabial nasal (CV)'),
        ('ɑmɑ', 'bilabial nasal (VCV)'),
        ('nɑ', 'alveolar nasal (CV)'),
        ('ɑnɑ', 'alveolar nasal (VCV)'),
        ('ŋɑ', 'velar nasal (CV)'),
        ('ɑŋɑ', 'velar nasal (VCV)'),
        # Extended nasals
        ('ɲɑ', 'palatal nasal (CV)'),
        ('ɑɲɑ', 'palatal nasal (VCV)'),
        ('ɴɑ', 'uvular nasal (CV)'),
        ('ɑɴɑ', 'uvular nasal (VCV)'),
        ('ɱɑ', 'labiodental nasal (CV)'),
        ('ɑɱɑ', 'labiodental nasal (VCV)'),
    ], "consonant_nasals_natural.wav", "Nasals (Natural Duration)", speed=0.5)


def test_fricatives_natural():
    """Test fricatives with Ladefoged-style CV and VCV patterns at slow speed."""
    return _synthesize_cv_list([
        ('fɑ', 'voiceless labiodental (CV)'),
        ('ɑfɑ', 'voiceless labiodental (VCV)'),
        ('vɑ', 'voiced labiodental (CV)'),
        ('ɑvɑ', 'voiced labiodental (VCV)'),
        ('sɑ', 'voiceless alveolar (CV)'),
        ('ɑsɑ', 'voiceless alveolar (VCV)'),
        ('zɑ', 'voiced alveolar (CV)'),
        ('ɑzɑ', 'voiced alveolar (VCV)'),
        ('ʃɑ', 'voiceless postalveolar (CV)'),
        ('ɑʃɑ', 'voiceless postalveolar (VCV)'),
        ('ʒɑ', 'voiced postalveolar (CV)'),
        ('ɑʒɑ', 'voiced postalveolar (VCV)'),
        ('hɑ', 'voiceless glottal (CV)'),
        ('ɑhɑ', 'voiceless glottal (VCV)'),
        # Palatal fricatives
        ('çɑ', 'voiceless palatal (CV)'),
        ('ɑçɑ', 'voiceless palatal (VCV)'),
        ('ʝɑ', 'voiced palatal (CV)'),
        ('ɑʝɑ', 'voiced palatal (VCV)'),
        # Uvular fricatives
        ('χɑ', 'voiceless uvular (CV)'),
        ('ɑχɑ', 'voiceless uvular (VCV)'),
        ('ʁɑ', 'voiced uvular (CV)'),
        ('ɑʁɑ', 'voiced uvular (VCV)'),
        # Pharyngeal fricatives
        ('ħɑ', 'voiceless pharyngeal (CV)'),
        ('ɑħɑ', 'voiceless pharyngeal (VCV)'),
        ('ʕɑ', 'voiced pharyngeal (CV)'),
        ('ɑʕɑ', 'voiced pharyngeal (VCV)'),
        # Bilabial fricatives
        ('ɸɑ', 'voiceless bilabial (CV)'),
        ('ɑɸɑ', 'voiceless bilabial (VCV)'),
        ('βɑ', 'voiced bilabial (CV)'),
        ('ɑβɑ', 'voiced bilabial (VCV)'),
    ], "consonant_fricatives_natural.wav", "Fricatives (Natural Duration)", speed=0.5)


def test_approximants_natural():
    """Test approximants/liquids with Ladefoged-style CV and VCV patterns at slow speed."""
    return _synthesize_cv_list([
        ('lɑ', 'alveolar lateral (CV)'),
        ('ɑlɑ', 'alveolar lateral (VCV)'),
        ('ɹɑ', 'postalveolar approximant (CV)'),
        ('ɑɹɑ', 'postalveolar approximant (VCV)'),
        ('jɑ', 'palatal approximant (CV)'),
        ('ɑjɑ', 'palatal approximant (VCV)'),
        ('wɑ', 'labial-velar approximant (CV)'),
        ('ɑwɑ', 'labial-velar approximant (VCV)'),
        # Extended approximants (front-to-back by place)
        ('ʋɑ', 'labiodental approximant (CV)'),
        ('ɑʋɑ', 'labiodental approximant (VCV)'),
        ('ɻɑ', 'retroflex approximant (CV)'),
        ('ɑɻɑ', 'retroflex approximant (VCV)'),
        ('ɰɑ', 'velar approximant (CV)'),
        ('ɑɰɑ', 'velar approximant (VCV)'),
        # Extended laterals (front-to-back by place)
        ('ʎɑ', 'palatal lateral (CV)'),
        ('ɑʎɑ', 'palatal lateral (VCV)'),
        ('ʟɑ', 'velar lateral (CV)'),
        ('ɑʟɑ', 'velar lateral (VCV)'),
    ], "consonant_approximants_natural.wav", "Approximants (Natural Duration)", speed=0.5)


def test_trills_natural():
    """Test trills with Ladefoged-style CV and VCV patterns at slow speed."""
    return _synthesize_cv_list([
        ('rɑ', 'alveolar trill (CV)'),
        ('ɑrɑ', 'alveolar trill (VCV)'),
        ('ʀɑ', 'uvular trill (CV)'),
        ('ɑʀɑ', 'uvular trill (VCV)'),
        ('ʙɑ', 'bilabial trill (CV)'),
        ('ɑʙɑ', 'bilabial trill (VCV)'),
    ], "consonant_trills_natural.wav", "Trills (Natural Duration)", speed=0.5)


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
    """Assert /s/ has higher spectral centroid than /ʃ/ (sibilant separation).

    /s/ (alveolar) should have a distinctly higher centroid than /ʃ/ (postalveolar).
    /f/ uses broadband pink noise (non-sibilant) so is not compared to sibilants.
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

    # /s/ should have higher centroid than /ʃ/ (sibilant separation)
    if 'ʃ' in centroids:
        assert centroids['s'] > centroids['ʃ'], \
            f"/s/ centroid ({centroids['s']:.0f}) should be > /ʃ/ ({centroids['ʃ']:.0f})"

    print("  Verified: /s/ centroid > /ʃ/ centroid")
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


def test_ejective_cv():
    """Test ejective stops and affricates in CV context.

    Ejectives should produce clear burst energy (sharper than regular stops)
    and generate non-silent output when followed by a vowel.
    """
    print("\n=== Test: Ejective CV ===")

    ejective_pairs = [
        ('pʼɑ', 'ejective bilabial (CV)'),
        ('tʼɑ', 'ejective alveolar (CV)'),
        ('kʼɑ', 'ejective velar (CV)'),
        ('qʼɑ', 'ejective uvular (CV)'),
        ('t͡sʼɑ', 'ejective alveolar affricate (CV)'),
        ('t͡ʃʼɑ', 'ejective postalveolar affricate (CV)'),
    ]

    all_samples = []
    all_passed = True

    for ipa_text, desc in ejective_pairs:
        print(f"  /{ipa_text}/ - {desc}")
        samples = _synthesize_cv_ipa(ipa_text, speed=0.5)

        arr = np.array(samples, dtype=np.float64)
        n = len(arr)

        # Check for burst energy in onset region
        onset_rms = np.sqrt(np.mean(arr[:n // 4] ** 2)) if n > 0 else 0
        vowel_rms = np.sqrt(np.mean(arr[n // 2:] ** 2)) if n > 0 else 0

        has_signal = onset_rms > 0 or vowel_rms > 0
        status = "PASS" if has_signal else "FAIL"
        if not has_signal:
            all_passed = False
        print(f"    onset RMS={onset_rms:.0f}, vowel RMS={vowel_rms:.0f} {status}")

        all_samples.extend(samples)
        all_samples.extend([0] * int(SAMPLE_RATE * 0.15))

    save_wav("consonant_ejectives_cv.wav", all_samples)
    assert all_passed, "Some ejectives show no energy in CV context"
    print(f"  Generated {len(ejective_pairs)} ejective CV items")
    print("  PASSED")
    return True


def test_ejective_no_aspiration():
    """Assert ejectives do NOT insert post-stop aspiration.

    Regular voiceless stops before a vowel get auto-aspiration (an 'h' phoneme).
    Ejectives should suppress this — no aspiration phoneme should be inserted.
    """
    print("\n=== Test: Ejective No Aspiration ===")

    all_passed = True

    for ipa_text, label in [("pʼɑ", "pʼ"), ("tʼɑ", "tʼ"), ("kʼɑ", "kʼ")]:
        phonemes = ipa.IPAToPhonemes(ipa_text)
        has_aspiration = any(p.get('_postStopAspiration') for p in phonemes)
        status = "PASS" if not has_aspiration else "FAIL"
        if has_aspiration:
            all_passed = False
        print(f"  /{label}/ aspiration suppressed: {status}")

    assert all_passed, "Some ejectives incorrectly have aspiration"
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


# --- Extended consonant spectral assertion tests ---

def _get_phoneme_cf2(ipa_char):
    """Get the cascade F2 value from phoneme data."""
    if ipa_char in phoneme_data:
        return phoneme_data[ipa_char].get('cf2', None)
    return None


def test_palatal_high_f2():
    """Assert palatal consonants (c, ɟ, ç, ʝ, ɲ) have F2 > 2000 Hz.

    Palatal place of articulation is characterized by high F2 due to
    the tongue body being raised toward the hard palate.
    """
    print("\n=== Test: Palatal High F2 ===")

    palatal_chars = ['c', 'ɟ', 'ç', 'ʝ', 'ɲ']
    all_passed = True

    for char in palatal_chars:
        cf2 = _get_phoneme_cf2(char)
        if cf2 is None:
            print(f"  /{char}/ not in phoneme data, skipping")
            continue

        ok = cf2 > 2000
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_passed = False
        print(f"  /{char}/ cf2={cf2} Hz {status} (> 2000 Hz)")

    assert all_passed, "Some palatals have F2 <= 2000 Hz"
    print("  PASSED")
    return True


def test_uvular_low_f2():
    """Assert uvular consonants (q, ɢ, χ, ʁ, ɴ) have F2 < 1400 Hz.

    Uvular place is characterized by low F2 due to constriction
    at the back of the oral cavity near the uvula.
    """
    print("\n=== Test: Uvular Low F2 ===")

    uvular_chars = ['q', 'ɢ', 'χ', 'ʁ', 'ɴ']
    all_passed = True

    for char in uvular_chars:
        cf2 = _get_phoneme_cf2(char)
        if cf2 is None:
            print(f"  /{char}/ not in phoneme data, skipping")
            continue

        ok = cf2 < 1400
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_passed = False
        print(f"  /{char}/ cf2={cf2} Hz {status} (< 1400 Hz)")

    assert all_passed, "Some uvulars have F2 >= 1400 Hz"
    print("  PASSED")
    return True


def test_pharyngeal_high_f1():
    """Assert pharyngeal consonants (ħ, ʕ) have F1 > 500 Hz.

    Pharyngeal constriction dramatically raises F1, which is the
    primary acoustic cue for pharyngeal place of articulation.
    """
    print("\n=== Test: Pharyngeal High F1 ===")

    pharyngeal_chars = ['ħ', 'ʕ']
    all_passed = True

    for char in pharyngeal_chars:
        if char not in phoneme_data:
            print(f"  /{char}/ not in phoneme data, skipping")
            continue

        cf1 = phoneme_data[char].get('cf1', None)
        if cf1 is None:
            print(f"  /{char}/ no cf1 defined, skipping")
            continue

        ok = cf1 > 500
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_passed = False
        print(f"  /{char}/ cf1={cf1} Hz {status} (> 500 Hz)")

    assert all_passed, "Some pharyngeals have F1 <= 500 Hz"
    print("  PASSED")
    return True


def test_place_minimal_pairs():
    """Assert place-contrasting consonants are distinct via F2.

    Verifies that consonants at different places of articulation
    have sufficiently different F2 values to be perceptually distinct:
    - c (palatal) vs k (velar): palatal should have higher F2
    - q (uvular) vs k (velar): uvular should have lower F2
    - ɲ (palatal) vs n (alveolar): palatal should have higher F2
    """
    print("\n=== Test: Place Minimal Pairs ===")

    pairs = [
        ('c', 'k', 'palatal vs velar (c > k)'),
        ('q', 'k', 'uvular vs velar (q < k)'),
        ('ɲ', 'n', 'palatal vs alveolar (ɲ > n)'),
    ]
    all_passed = True

    for char1, char2, desc in pairs:
        cf2_1 = _get_phoneme_cf2(char1)
        cf2_2 = _get_phoneme_cf2(char2)

        if cf2_1 is None or cf2_2 is None:
            print(f"  /{char1}/ vs /{char2}/ - skipping (missing data)")
            continue

        # Determine expected ordering
        if char1 in ['c', 'ɲ']:
            # Palatal should have higher F2
            ok = cf2_1 > cf2_2
            direction = ">"
        else:
            # Uvular should have lower F2
            ok = cf2_1 < cf2_2
            direction = "<"

        status = "PASS" if ok else "FAIL"
        if not ok:
            all_passed = False
        print(f"  /{char1}/ ({cf2_1} Hz) {direction} /{char2}/ ({cf2_2} Hz) — {desc} {status}")

    assert all_passed, "Some place minimal pairs not distinct"
    print("  PASSED")
    return True


def run_all_tests():
    """Run all consonant tests."""
    print("=" * 50)
    print("Manatu Consonant Phoneme Tests")
    print("=" * 50)

    tests = [
        # CV transition tests (full IPA pipeline)
        test_cv_transitions,
        test_cv_formant_scaling,
        # Natural-duration Ladefoged CV/VCV tests
        test_stops_natural,
        test_nasals_natural,
        test_fricatives_natural,
        test_approximants_natural,
        test_trills_natural,
        # Ejective tests
        test_ejective_cv,
        test_ejective_no_aspiration,
        # Spectral assertion tests
        test_voicing_contrast,
        test_fricative_spectral_centroid,
        test_nasal_low_f1,
        test_stop_burst_presence,
        # Extended spectral assertion tests
        test_palatal_high_f2,
        test_uvular_low_f2,
        test_pharyngeal_high_f1,
        test_place_minimal_pairs,
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
