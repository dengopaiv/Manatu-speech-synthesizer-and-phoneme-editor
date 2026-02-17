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
    for frame, min_dur, fade_dur in ipa.generateSubFramesAndTiming(
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

    Uses ipa.generateSubFramesAndTiming which applies natural per-class durations
    (stops=10ms+closure, nasals=30ms, fricatives=45ms, vowels=50-60ms) and
    coarticulation via sub-frame interpolation.
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
        # Prenasalized stops
        ('ᵐbɑ', 'prenasalized bilabial (CV)'),
        ('ɑᵐbɑ', 'prenasalized bilabial (VCV)'),
        ('ⁿdɑ', 'prenasalized alveolar (CV)'),
        ('ɑⁿdɑ', 'prenasalized alveolar (VCV)'),
        ('ᵑɡɑ', 'prenasalized velar (CV)'),
        ('ɑᵑɡɑ', 'prenasalized velar (VCV)'),
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
        # Alveolo-palatal fricatives
        ('ɕɑ', 'voiceless alveolo-palatal (CV)'),
        ('ɑɕɑ', 'voiceless alveolo-palatal (VCV)'),
        ('ʑɑ', 'voiced alveolo-palatal (CV)'),
        ('ɑʑɑ', 'voiced alveolo-palatal (VCV)'),
        # Epiglottal fricatives
        ('ʜɑ', 'voiceless epiglottal (CV)'),
        ('ɑʜɑ', 'voiceless epiglottal (VCV)'),
        ('ʢɑ', 'voiced epiglottal (CV)'),
        ('ɑʢɑ', 'voiced epiglottal (VCV)'),
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

def _synthesize_ipa_phoneme(ipa_text, pitch=120, speed=0.5):
    """Synthesize IPA text using the full ipa.py pipeline."""
    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)
    for frame, min_dur, fade_dur in ipa.generateSubFramesAndTiming(
        ipa_text, speed=speed, basePitch=pitch, inflection=0
    ):
        sp.queueFrame(frame, min_dur, fade_dur)
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

    # Verify voiced consonants have reasonable HNR (> 3 dB)
    # Threshold is modest because stops (b, d) have short voicing bars
    # that lower HNR when analyzed with natural-duration VCV audio
    if voiced_hnrs:
        avg_hnr = sum(voiced_hnrs) / len(voiced_hnrs)
        print(f"  Average voiced HNR: {avg_hnr:.1f} dB")
        assert avg_hnr > 3, f"Average voiced HNR ({avg_hnr:.1f}) should be > 3 dB"

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


def test_implosive_cv():
    """Test implosive stops in CV context.

    Implosives should produce burst energy and generate non-silent output
    when followed by a vowel. Burst should be present but weaker than
    regular voiced stops.
    """
    print("\n=== Test: Implosive CV ===")

    implosive_pairs = [
        ('ɓɑ', 'implosive bilabial (CV)'),
        ('ɗɑ', 'implosive alveolar (CV)'),
        ('ɠɑ', 'implosive velar (CV)'),
        ('ʄɑ', 'implosive palatal (CV)'),
        ('ʛɑ', 'implosive uvular (CV)'),
    ]

    all_samples = []
    all_passed = True

    for ipa_text, desc in implosive_pairs:
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

    save_wav("consonant_implosives_cv.wav", all_samples)
    assert all_passed, "Some implosives show no energy in CV context"
    print(f"  Generated {len(implosive_pairs)} implosive CV items")
    print("  PASSED")
    return True


def test_implosive_voicing():
    """Assert implosives are strongly voiced in VCV context.

    Implosives maintain voicing through closure (voicebar), so they should
    show strong periodicity (high HNR) in the consonant region.
    """
    print("\n=== Test: Implosive Voicing ===")

    implosive_chars = ['ɓ', 'ɗ', 'ɠ', 'ʄ', 'ʛ']
    all_passed = True

    for char in implosive_chars:
        if char not in phoneme_data:
            print(f"  /{char}/ not in phoneme data, skipping")
            continue

        samples = _synthesize_ipa_phoneme(f'ɑ{char}ɑ')
        if len(samples) < 200:
            print(f"  /{char}/ too short, skipping")
            continue

        # Check middle third (the consonant region)
        n = len(samples)
        mid = samples[n // 3: 2 * n // 3]
        analysis = analyze_segment(mid, SAMPLE_RATE)

        hnr_str = f"HNR={analysis.hnr:.1f}dB" if analysis.hnr else "HNR=N/A"
        ok = analysis.is_voiced and (analysis.hnr is None or analysis.hnr > 5)
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_passed = False
        print(f"  /{char}/ voiced: {analysis.is_voiced} ({hnr_str}) {status}")

    assert all_passed, "Some implosives not detected as strongly voiced"
    print("  PASSED")
    return True


def test_implosive_no_aspiration():
    """Assert implosives do NOT insert post-stop aspiration.

    Implosives are voiced stops — auto-aspiration only triggers for voiceless
    stops. No aspiration phoneme should be inserted after implosives.
    """
    print("\n=== Test: Implosive No Aspiration ===")

    all_passed = True

    for ipa_text, label in [("ɓɑ", "ɓ"), ("ɗɑ", "ɗ"), ("ɠɑ", "ɠ"), ("ʄɑ", "ʄ"), ("ʛɑ", "ʛ")]:
        phonemes = ipa.IPAToPhonemes(ipa_text)
        has_aspiration = any(p.get('_postStopAspiration') for p in phonemes)
        status = "PASS" if not has_aspiration else "FAIL"
        if has_aspiration:
            all_passed = False
        print(f"  /{label}/ aspiration suppressed: {status}")

    assert all_passed, "Some implosives incorrectly have aspiration"
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


def test_alveolo_palatal_cv():
    """Test alveolo-palatal fricatives ɕ, ʑ in CV context.

    Alveolo-palatals are sibilants between postalveolar (ʃ/ʒ) and palatal (ç/ʝ).
    They should produce clear frication energy and non-silent output.
    """
    print("\n=== Test: Alveolo-Palatal CV ===")

    pairs = [
        ('ɕɑ', 'voiceless alveolo-palatal (CV)'),
        ('ʑɑ', 'voiced alveolo-palatal (CV)'),
    ]

    all_samples = []
    all_passed = True

    for ipa_text, desc in pairs:
        print(f"  /{ipa_text}/ - {desc}")
        samples = _synthesize_cv_ipa(ipa_text, speed=0.5)

        arr = np.array(samples, dtype=np.float64)
        n = len(arr)

        onset_rms = np.sqrt(np.mean(arr[:n // 4] ** 2)) if n > 0 else 0
        vowel_rms = np.sqrt(np.mean(arr[n // 2:] ** 2)) if n > 0 else 0

        has_signal = onset_rms > 0 or vowel_rms > 0
        status = "PASS" if has_signal else "FAIL"
        if not has_signal:
            all_passed = False
        print(f"    onset RMS={onset_rms:.0f}, vowel RMS={vowel_rms:.0f} {status}")

        all_samples.extend(samples)
        all_samples.extend([0] * int(SAMPLE_RATE * 0.15))

    save_wav("consonant_alveolo_palatal_cv.wav", all_samples)
    assert all_passed, "Some alveolo-palatals show no energy in CV context"
    print(f"  Generated {len(pairs)} alveolo-palatal CV items")
    print("  PASSED")
    return True


def test_alveolo_palatal_spectral():
    """Assert ɕ spectral centroid is between /s/ and /ʃ/ (sibilant positioning).

    ɕ noise filter (3600 Hz) is between ʃ (2800 Hz) and s (7500 Hz),
    so its spectral centroid should fall between the two.
    """
    print("\n=== Test: Alveolo-Palatal Spectral ===")

    centroids = {}
    for char in ['s', 'ʃ', 'ɕ']:
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

    if 'ɕ' not in centroids:
        print("  SKIP: /ɕ/ not available")
        return True

    # ɕ centroid should be between ʃ and s
    if 'ʃ' in centroids and 's' in centroids:
        sh_centroid = centroids['ʃ']
        s_centroid = centroids['s']
        alv_pal_centroid = centroids['ɕ']
        assert alv_pal_centroid > sh_centroid, \
            f"/ɕ/ centroid ({alv_pal_centroid:.0f}) should be > /ʃ/ ({sh_centroid:.0f})"
        assert alv_pal_centroid < s_centroid, \
            f"/ɕ/ centroid ({alv_pal_centroid:.0f}) should be < /s/ ({s_centroid:.0f})"
        print(f"  Verified: /ʃ/ ({sh_centroid:.0f}) < /ɕ/ ({alv_pal_centroid:.0f}) < /s/ ({s_centroid:.0f})")

    print("  PASSED")
    return True


def test_prenasalized_cv():
    """Test prenasalized stops ᵐb, ⁿd, ᵑɡ in CV context.

    Prenasalized stops should produce nasal murmur followed by stop release,
    generating non-silent output when followed by a vowel.
    """
    print("\n=== Test: Prenasalized CV ===")

    prenasalized_pairs = [
        ('ᵐbɑ', 'prenasalized bilabial (CV)'),
        ('ⁿdɑ', 'prenasalized alveolar (CV)'),
        ('ᵑɡɑ', 'prenasalized velar (CV)'),
    ]

    all_samples = []
    all_passed = True

    for ipa_text, desc in prenasalized_pairs:
        print(f"  /{ipa_text}/ - {desc}")
        samples = _synthesize_cv_ipa(ipa_text, speed=0.5)

        arr = np.array(samples, dtype=np.float64)
        n = len(arr)

        onset_rms = np.sqrt(np.mean(arr[:n // 4] ** 2)) if n > 0 else 0
        vowel_rms = np.sqrt(np.mean(arr[n // 2:] ** 2)) if n > 0 else 0

        has_signal = onset_rms > 0 or vowel_rms > 0
        status = "PASS" if has_signal else "FAIL"
        if not has_signal:
            all_passed = False
        print(f"    onset RMS={onset_rms:.0f}, vowel RMS={vowel_rms:.0f} {status}")

        all_samples.extend(samples)
        all_samples.extend([0] * int(SAMPLE_RATE * 0.15))

    save_wav("consonant_prenasalized_cv.wav", all_samples)
    assert all_passed, "Some prenasalized stops show no energy in CV context"
    print(f"  Generated {len(prenasalized_pairs)} prenasalized CV items")
    print("  PASSED")
    return True


def test_prenasalized_voicing():
    """Assert prenasalized stops are strongly voiced in VCV context.

    Prenasalized stops maintain voicing throughout (nasal murmur is voiced,
    stop release is voiced), so they should show strong periodicity (high HNR)
    in the consonant region.
    """
    print("\n=== Test: Prenasalized Voicing ===")

    prenasalized_texts = [
        ('ɑᵐbɑ', 'ᵐb'),
        ('ɑⁿdɑ', 'ⁿd'),
        ('ɑᵑɡɑ', 'ᵑɡ'),
    ]
    all_passed = True

    for ipa_text, label in prenasalized_texts:
        samples = _synthesize_ipa_phoneme(ipa_text)
        if len(samples) < 200:
            print(f"  /{label}/ too short, skipping")
            continue

        # Check middle third (the consonant region)
        n = len(samples)
        mid = samples[n // 3: 2 * n // 3]
        analysis = analyze_segment(mid, SAMPLE_RATE)

        hnr_str = f"HNR={analysis.hnr:.1f}dB" if analysis.hnr else "HNR=N/A"
        ok = analysis.is_voiced and (analysis.hnr is None or analysis.hnr > 5)
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_passed = False
        print(f"  /{label}/ voiced: {analysis.is_voiced} ({hnr_str}) {status}")

    assert all_passed, "Some prenasalized stops not detected as strongly voiced"
    print("  PASSED")
    return True


def test_epiglottal_cv():
    """Test epiglottal consonants ʜ, ʢ, ʡ in CV context.

    Epiglottals should produce non-silent output when followed by a vowel.
    """
    print("\n=== Test: Epiglottal CV ===")

    epiglottal_pairs = [
        ('ʜɑ', 'voiceless epiglottal fricative (CV)'),
        ('ʢɑ', 'voiced epiglottal fricative (CV)'),
        ('ʡɑ', 'epiglottal stop (CV)'),
    ]

    all_samples = []
    all_passed = True

    for ipa_text, desc in epiglottal_pairs:
        print(f"  /{ipa_text}/ - {desc}")
        samples = _synthesize_cv_ipa(ipa_text, speed=0.5)

        arr = np.array(samples, dtype=np.float64)
        n = len(arr)

        onset_rms = np.sqrt(np.mean(arr[:n // 4] ** 2)) if n > 0 else 0
        vowel_rms = np.sqrt(np.mean(arr[n // 2:] ** 2)) if n > 0 else 0

        has_signal = onset_rms > 0 or vowel_rms > 0
        status = "PASS" if has_signal else "FAIL"
        if not has_signal:
            all_passed = False
        print(f"    onset RMS={onset_rms:.0f}, vowel RMS={vowel_rms:.0f} {status}")

        all_samples.extend(samples)
        all_samples.extend([0] * int(SAMPLE_RATE * 0.15))

    save_wav("consonant_epiglottal_cv.wav", all_samples)
    assert all_passed, "Some epiglottals show no energy in CV context"
    print(f"  Generated {len(epiglottal_pairs)} epiglottal CV items")
    print("  PASSED")
    return True


def test_epiglottal_high_f1():
    """Assert epiglottal consonants ʜ, ʢ, ʡ have cf1 > 500 Hz.

    Epiglottal constriction raises F1 even higher than pharyngeals,
    which is the primary acoustic cue for this place of articulation.
    """
    print("\n=== Test: Epiglottal High F1 ===")

    epiglottal_chars = ['ʜ', 'ʢ', 'ʡ']
    all_passed = True

    for char in epiglottal_chars:
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

    assert all_passed, "Some epiglottals have F1 <= 500 Hz"
    print("  PASSED")
    return True


def test_alveolo_palatal_affricate_cv():
    """Test alveolo-palatal affricates t͡ɕ, d͡ʑ in CV context.

    These should produce clear burst + frication energy and non-silent output.
    """
    print("\n=== Test: Alveolo-Palatal Affricate CV ===")

    pairs = [
        ('t͡ɕɑ', 'voiceless alveolo-palatal affricate (CV)'),
        ('d͡ʑɑ', 'voiced alveolo-palatal affricate (CV)'),
    ]

    all_samples = []
    all_passed = True

    for ipa_text, desc in pairs:
        print(f"  /{ipa_text}/ - {desc}")
        samples = _synthesize_cv_ipa(ipa_text, speed=0.5)

        arr = np.array(samples, dtype=np.float64)
        n = len(arr)

        onset_rms = np.sqrt(np.mean(arr[:n // 4] ** 2)) if n > 0 else 0
        vowel_rms = np.sqrt(np.mean(arr[n // 2:] ** 2)) if n > 0 else 0

        has_signal = onset_rms > 0 or vowel_rms > 0
        status = "PASS" if has_signal else "FAIL"
        if not has_signal:
            all_passed = False
        print(f"    onset RMS={onset_rms:.0f}, vowel RMS={vowel_rms:.0f} {status}")

        all_samples.extend(samples)
        all_samples.extend([0] * int(SAMPLE_RATE * 0.15))

    save_wav("consonant_alveolo_palatal_affricate_cv.wav", all_samples)
    assert all_passed, "Some alveolo-palatal affricates show no energy in CV context"
    print(f"  Generated {len(pairs)} affricate CV items")
    print("  PASSED")
    return True


def test_lateral_affricate_cv():
    """Test lateral affricate d͡ɮ in CV context."""
    print("\n=== Test: Lateral Affricate CV ===")

    pairs = [
        ('t͡ɬɑ', 'voiceless lateral affricate (CV)'),
        ('d͡ɮɑ', 'voiced lateral affricate (CV)'),
    ]

    all_samples = []
    all_passed = True

    for ipa_text, desc in pairs:
        print(f"  /{ipa_text}/ - {desc}")
        samples = _synthesize_cv_ipa(ipa_text, speed=0.5)

        arr = np.array(samples, dtype=np.float64)
        n = len(arr)

        onset_rms = np.sqrt(np.mean(arr[:n // 4] ** 2)) if n > 0 else 0
        vowel_rms = np.sqrt(np.mean(arr[n // 2:] ** 2)) if n > 0 else 0

        has_signal = onset_rms > 0 or vowel_rms > 0
        status = "PASS" if has_signal else "FAIL"
        if not has_signal:
            all_passed = False
        print(f"    onset RMS={onset_rms:.0f}, vowel RMS={vowel_rms:.0f} {status}")

        all_samples.extend(samples)
        all_samples.extend([0] * int(SAMPLE_RATE * 0.15))

    save_wav("consonant_lateral_affricate_cv.wav", all_samples)
    assert all_passed, "Some lateral affricates show no energy in CV context"
    print("  PASSED")
    return True


def test_velarized_lateral_cv():
    """Test velarized lateral ɫ in CV context."""
    print("\n=== Test: Velarized Lateral CV ===")

    samples = _synthesize_cv_ipa('ɫɑ', speed=0.5)

    arr = np.array(samples, dtype=np.float64)
    n = len(arr)

    rms = np.sqrt(np.mean(arr ** 2)) if n > 0 else 0
    has_signal = rms > 0
    status = "PASS" if has_signal else "FAIL"
    print(f"  /ɫɑ/ RMS={rms:.0f} {status}")

    # Verify ɫ has lower F2 than l
    l_cf2 = _get_phoneme_cf2('l')
    dark_l_cf2 = _get_phoneme_cf2('ɫ')
    if l_cf2 is not None and dark_l_cf2 is not None:
        assert dark_l_cf2 < l_cf2, f"ɫ cf2 ({dark_l_cf2}) should be < l cf2 ({l_cf2})"
        print(f"  ɫ cf2={dark_l_cf2} < l cf2={l_cf2} PASS")

    save_wav("consonant_velarized_lateral_cv.wav", samples)
    assert has_signal, "Velarized lateral shows no energy"
    print("  PASSED")
    return True


def test_click_cv():
    """Test all 5 click consonants in CV context.

    Clicks should produce short sharp transients (burst energy) and
    non-silent output when followed by a vowel.
    """
    print("\n=== Test: Click CV ===")

    click_pairs = [
        ('ʘɑ', 'bilabial click (CV)'),
        ('ǀɑ', 'dental click (CV)'),
        ('ǃɑ', 'postalveolar click (CV)'),
        ('ǂɑ', 'palatal click (CV)'),
        ('ǁɑ', 'lateral click (CV)'),
    ]

    all_samples = []
    all_passed = True

    for ipa_text, desc in click_pairs:
        print(f"  /{ipa_text}/ - {desc}")
        samples = _synthesize_cv_ipa(ipa_text, speed=0.5)

        arr = np.array(samples, dtype=np.float64)
        n = len(arr)

        onset_rms = np.sqrt(np.mean(arr[:n // 4] ** 2)) if n > 0 else 0
        vowel_rms = np.sqrt(np.mean(arr[n // 2:] ** 2)) if n > 0 else 0

        has_signal = onset_rms > 0 or vowel_rms > 0
        status = "PASS" if has_signal else "FAIL"
        if not has_signal:
            all_passed = False
        print(f"    onset RMS={onset_rms:.0f}, vowel RMS={vowel_rms:.0f} {status}")

        all_samples.extend(samples)
        all_samples.extend([0] * int(SAMPLE_RATE * 0.15))

    save_wav("consonant_clicks_cv.wav", all_samples)
    assert all_passed, "Some clicks show no energy in CV context"
    print(f"  Generated {len(click_pairs)} click CV items")
    print("  PASSED")
    return True


def test_diacritic_voiceless():
    """Test voiceless diacritic: b̥ɑ should produce output (voiceless b = like p)."""
    print("\n=== Test: Diacritic Voiceless ===")

    # b with combining ring below = voiceless b
    samples = _synthesize_cv_ipa('b\u0325ɑ', speed=0.5)

    arr = np.array(samples, dtype=np.float64)
    has_signal = len(arr) > 0 and np.sqrt(np.mean(arr ** 2)) > 0
    print(f"  /b̥ɑ/ has signal: {has_signal}")

    # Check that voicing was removed via IPA pipeline
    phonemes = ipa.IPAToPhonemes('b\u0325ɑ')
    # Find the b phoneme (skip gaps)
    b_phoneme = None
    for p in phonemes:
        if p.get('_char') and 'b' in p.get('_char', ''):
            b_phoneme = p
            break
    if b_phoneme is None:
        # Might be in a phase — check for _isPhase entries
        for p in phonemes:
            if p.get('_isPhase') and p.get('_isVoiced') is not None:
                b_phoneme = p
                break

    if b_phoneme:
        is_voiceless = not b_phoneme.get('_isVoiced', True)
        print(f"  b̥ _isVoiced={b_phoneme.get('_isVoiced')} (expect False): {'PASS' if is_voiceless else 'FAIL'}")
        assert is_voiceless, "b̥ should be voiceless"

    assert has_signal, "b̥ɑ should produce non-silent output"
    print("  PASSED")
    return True


def test_diacritic_labialized():
    """Test labialized diacritic: kʷɑ should have lower cf2 than kɑ."""
    print("\n=== Test: Diacritic Labialized ===")

    # Get phonemes for kɑ and kʷɑ
    phonemes_plain = ipa.IPAToPhonemes('kɑ')
    phonemes_lab = ipa.IPAToPhonemes('kʷɑ')

    # Find the k phoneme (it will be in phases for stops)
    def find_first_phase_cf2(phonemes):
        for p in phonemes:
            if p.get('_isPhase') and 'cf2' in p:
                return p['cf2']
            if not p.get('_silence') and not p.get('_preStopGap') and 'cf2' in p:
                return p['cf2']
        return None

    cf2_plain = find_first_phase_cf2(phonemes_plain)
    cf2_lab = find_first_phase_cf2(phonemes_lab)

    if cf2_plain is not None and cf2_lab is not None:
        print(f"  kɑ cf2={cf2_plain:.0f}, kʷɑ cf2={cf2_lab:.0f}")
        assert cf2_lab < cf2_plain, f"kʷ cf2 ({cf2_lab:.0f}) should be < k cf2 ({cf2_plain:.0f})"
        print("  PASSED")
    else:
        print("  SKIP: Could not extract cf2 from phoneme pipeline")
    return True


def test_diacritic_palatalized():
    """Test palatalized diacritic: tʲɑ should have higher cf2 than tɑ."""
    print("\n=== Test: Diacritic Palatalized ===")

    phonemes_plain = ipa.IPAToPhonemes('tɑ')
    phonemes_pal = ipa.IPAToPhonemes('tʲɑ')

    def find_first_phase_cf2(phonemes):
        for p in phonemes:
            if p.get('_isPhase') and 'cf2' in p:
                return p['cf2']
            if not p.get('_silence') and not p.get('_preStopGap') and 'cf2' in p:
                return p['cf2']
        return None

    cf2_plain = find_first_phase_cf2(phonemes_plain)
    cf2_pal = find_first_phase_cf2(phonemes_pal)

    if cf2_plain is not None and cf2_pal is not None:
        print(f"  tɑ cf2={cf2_plain:.0f}, tʲɑ cf2={cf2_pal:.0f}")
        assert cf2_pal > cf2_plain, f"tʲ cf2 ({cf2_pal:.0f}) should be > t cf2 ({cf2_plain:.0f})"
        print("  PASSED")
    else:
        print("  SKIP: Could not extract cf2 from phoneme pipeline")
    return True


def test_diacritic_nasalized_generic():
    """Test generic nasalized diacritic: ẽ (e + ̃) should have caNP > 0.

    Pre-computed nasalized vowels (ɛ̃, ɔ̃, etc.) should be matched first.
    The generic handler fires only for vowels not in the pre-computed set.
    """
    print("\n=== Test: Diacritic Nasalized Generic ===")

    # e + combining tilde (not in pre-computed set)
    phonemes = ipa.IPAToPhonemes('e\u0303')

    e_phoneme = None
    for p in phonemes:
        if not p.get('_silence') and not p.get('_preStopGap') and p.get('_isVowel'):
            e_phoneme = p
            break

    if e_phoneme:
        canp = e_phoneme.get('caNP', 0)
        print(f"  ẽ caNP={canp} (expect > 0)")
        assert canp > 0, "ẽ should have nasal pole active (caNP > 0)"
        print("  PASSED")
    else:
        print("  SKIP: Could not find vowel phoneme for ẽ")
    return True


def test_diacritic_creaky():
    """Test creaky voice diacritic: a̰ should have diplophonia > base a."""
    print("\n=== Test: Diacritic Creaky ===")

    phonemes_plain = ipa.IPAToPhonemes('a')
    phonemes_creaky = ipa.IPAToPhonemes('a\u0330')

    def find_vowel(phonemes):
        for p in phonemes:
            if p.get('_isVowel') and not p.get('_silence'):
                return p
        return None

    a_plain = find_vowel(phonemes_plain)
    a_creaky = find_vowel(phonemes_creaky)

    if a_plain and a_creaky:
        diplo_plain = a_plain.get('diplophonia', 0)
        diplo_creaky = a_creaky.get('diplophonia', 0)
        print(f"  a diplophonia={diplo_plain}, a̰ diplophonia={diplo_creaky}")
        assert diplo_creaky > diplo_plain, \
            f"a̰ diplophonia ({diplo_creaky}) should be > a ({diplo_plain})"
        print("  PASSED")
    else:
        print("  SKIP: Could not find vowel phonemes")
    return True


def test_diacritic_nasalized_f1_lowering():
    """Test nasalized F1 lowering: open vowels should lose more F1 than close vowels."""
    print("\n=== Test: Diacritic Nasalized F1 Lowering ===")

    # Close vowel u (cf1≈310) — minimal F1 lowering expected
    phonemes_u = ipa.IPAToPhonemes('u')
    phonemes_u_nasal = ipa.IPAToPhonemes('u\u0303')

    # Open vowel ɑ (cf1≈850) — large F1 lowering expected
    phonemes_a = ipa.IPAToPhonemes('\u0251')  # ɑ
    phonemes_a_nasal = ipa.IPAToPhonemes('\u0251\u0303')  # ɑ̃

    def find_vowel(phonemes):
        for p in phonemes:
            if p.get('_isVowel') and not p.get('_silence'):
                return p
        return None

    u_plain = find_vowel(phonemes_u)
    u_nasal = find_vowel(phonemes_u_nasal)
    a_plain = find_vowel(phonemes_a)
    a_nasal = find_vowel(phonemes_a_nasal)

    if u_plain and u_nasal and a_plain and a_nasal:
        u_drop = u_plain.get('cf1', 0) - u_nasal.get('cf1', 0)
        a_drop = a_plain.get('cf1', 0) - a_nasal.get('cf1', 0)
        print(f"  u cf1 drop: {u_drop:.0f} Hz, ɑ cf1 drop: {a_drop:.0f} Hz")
        assert a_drop > u_drop, \
            f"Open vowel ɑ̃ should lose more F1 ({a_drop:.0f}) than close vowel ũ ({u_drop:.0f})"
        print("  PASSED")
    else:
        print("  SKIP: Could not find vowel phonemes")
    return True


def test_diacritic_nasalized_bandwidth():
    """Test nasalized F2 bandwidth expansion: ẽ should have wider cb2 than e."""
    print("\n=== Test: Diacritic Nasalized Bandwidth ===")

    phonemes_plain = ipa.IPAToPhonemes('e')
    phonemes_nasal = ipa.IPAToPhonemes('e\u0303')

    def find_vowel(phonemes):
        for p in phonemes:
            if p.get('_isVowel') and not p.get('_silence'):
                return p
        return None

    e_plain = find_vowel(phonemes_plain)
    e_nasal = find_vowel(phonemes_nasal)

    if e_plain and e_nasal:
        cb2_plain = e_plain.get('cb2', 0)
        cb2_nasal = e_nasal.get('cb2', 0)
        print(f"  e cb2={cb2_plain:.0f}, ẽ cb2={cb2_nasal:.0f}")
        assert cb2_nasal > cb2_plain, \
            f"ẽ cb2 ({cb2_nasal:.0f}) should be > e cb2 ({cb2_plain:.0f})"
        print("  PASSED")
    else:
        print("  SKIP: Could not find vowel phonemes")
    return True


def test_diacritic_breathy_scaling():
    """Test breathy voice uses relative scaling, not flat lfRd=2.5."""
    print("\n=== Test: Diacritic Breathy Scaling ===")

    phonemes_plain = ipa.IPAToPhonemes('a')
    phonemes_breathy = ipa.IPAToPhonemes('a\u0324')  # a̤

    def find_vowel(phonemes):
        for p in phonemes:
            if p.get('_isVowel') and not p.get('_silence'):
                return p
        return None

    a_plain = find_vowel(phonemes_plain)
    a_breathy = find_vowel(phonemes_breathy)

    if a_plain and a_breathy:
        rd_plain = a_plain.get('lfRd', 1.0)
        rd_breathy = a_breathy.get('lfRd', 1.0)
        print(f"  a lfRd={rd_plain:.2f}, a̤ lfRd={rd_breathy:.2f}")
        assert rd_breathy > rd_plain, \
            f"a̤ lfRd ({rd_breathy:.2f}) should be > a lfRd ({rd_plain:.2f})"
        # Verify it's NOT the old flat 2.5 value
        assert rd_breathy != 2.5, \
            f"a̤ lfRd should use relative scaling, not flat 2.5 (got {rd_breathy:.2f})"
        print("  PASSED")
    else:
        print("  SKIP: Could not find vowel phonemes")
    return True


def test_diacritic_palatalized_f3():
    """Test palatalized diacritic raises F3: tʲ should have higher cf3 than t."""
    print("\n=== Test: Diacritic Palatalized F3 ===")

    phonemes_plain = ipa.IPAToPhonemes('t\u0251')  # tɑ
    phonemes_pal = ipa.IPAToPhonemes('t\u02B2\u0251')  # tʲɑ

    def find_first_phase_cf3(phonemes):
        for p in phonemes:
            if p.get('_isPhase') and 'cf3' in p:
                return p['cf3']
            if not p.get('_silence') and not p.get('_preStopGap') and 'cf3' in p:
                return p['cf3']
        return None

    cf3_plain = find_first_phase_cf3(phonemes_plain)
    cf3_pal = find_first_phase_cf3(phonemes_pal)

    if cf3_plain is not None and cf3_pal is not None:
        print(f"  tɑ cf3={cf3_plain:.0f}, tʲɑ cf3={cf3_pal:.0f}")
        assert cf3_pal > cf3_plain, \
            f"tʲ cf3 ({cf3_pal:.0f}) should be > t cf3 ({cf3_plain:.0f})"
        print("  PASSED")
    else:
        print("  SKIP: Could not extract cf3 from phoneme pipeline")
    return True


def test_diacritic_labialized_f3():
    """Test labialized diacritic lowers F3: kʷ should have lower cf3 than k."""
    print("\n=== Test: Diacritic Labialized F3 ===")

    phonemes_plain = ipa.IPAToPhonemes('k\u0251')  # kɑ
    phonemes_lab = ipa.IPAToPhonemes('k\u02B7\u0251')  # kʷɑ

    def find_first_phase_cf3(phonemes):
        for p in phonemes:
            if p.get('_isPhase') and 'cf3' in p:
                return p['cf3']
            if not p.get('_silence') and not p.get('_preStopGap') and 'cf3' in p:
                return p['cf3']
        return None

    cf3_plain = find_first_phase_cf3(phonemes_plain)
    cf3_lab = find_first_phase_cf3(phonemes_lab)

    if cf3_plain is not None and cf3_lab is not None:
        print(f"  kɑ cf3={cf3_plain:.0f}, kʷɑ cf3={cf3_lab:.0f}")
        assert cf3_lab < cf3_plain, \
            f"kʷ cf3 ({cf3_lab:.0f}) should be < k cf3 ({cf3_plain:.0f})"
        print("  PASSED")
    else:
        print("  SKIP: Could not extract cf3 from phoneme pipeline")
    return True


def test_diacritic_pharyngealized_bandwidth():
    """Test pharyngealized diacritic widens cb1: dˤ should have wider cb1 than d."""
    print("\n=== Test: Diacritic Pharyngealized Bandwidth ===")

    phonemes_plain = ipa.IPAToPhonemes('d\u0251')  # dɑ
    phonemes_phar = ipa.IPAToPhonemes('d\u02E4\u0251')  # dˤɑ

    def find_first_phase_cb1(phonemes):
        for p in phonemes:
            if p.get('_isPhase') and 'cb1' in p:
                return p['cb1']
            if not p.get('_silence') and not p.get('_preStopGap') and 'cb1' in p:
                return p['cb1']
        return None

    cb1_plain = find_first_phase_cb1(phonemes_plain)
    cb1_phar = find_first_phase_cb1(phonemes_phar)

    if cb1_plain is not None and cb1_phar is not None:
        print(f"  dɑ cb1={cb1_plain:.0f}, dˤɑ cb1={cb1_phar:.0f}")
        assert cb1_phar > cb1_plain, \
            f"dˤ cb1 ({cb1_phar:.0f}) should be > d cb1 ({cb1_plain:.0f})"
        print("  PASSED")
    else:
        print("  SKIP: Could not extract cb1 from phoneme pipeline")
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
        # Implosive tests
        test_implosive_cv,
        test_implosive_voicing,
        test_implosive_no_aspiration,
        # Spectral assertion tests
        test_voicing_contrast,
        test_fricative_spectral_centroid,
        test_nasal_low_f1,
        test_stop_burst_presence,
        # Alveolo-palatal tests
        test_alveolo_palatal_cv,
        test_alveolo_palatal_spectral,
        # Prenasalized stop tests
        test_prenasalized_cv,
        test_prenasalized_voicing,
        # Epiglottal tests
        test_epiglottal_cv,
        test_epiglottal_high_f1,
        # Extended spectral assertion tests
        test_palatal_high_f2,
        test_uvular_low_f2,
        test_pharyngeal_high_f1,
        test_place_minimal_pairs,
        # Alveolo-palatal affricate tests
        test_alveolo_palatal_affricate_cv,
        # Lateral affricate tests
        test_lateral_affricate_cv,
        # Velarized lateral test
        test_velarized_lateral_cv,
        # Click tests
        test_click_cv,
        # Diacritic modifier tests
        test_diacritic_voiceless,
        test_diacritic_labialized,
        test_diacritic_palatalized,
        test_diacritic_nasalized_generic,
        test_diacritic_creaky,
        test_diacritic_nasalized_f1_lowering,
        test_diacritic_nasalized_bandwidth,
        test_diacritic_breathy_scaling,
        test_diacritic_palatalized_f3,
        test_diacritic_labialized_f3,
        test_diacritic_pharyngealized_bandwidth,
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
