# -*- coding: utf-8 -*-
"""
Sub-frame architecture tests.

Validates the sub-frame generator (generateSubFramesAndTiming) for correct
pitch interpolation, coarticulation, cross-phoneme blending, and performance.

Usage:
    python tests/synthesis/test_subframes.py

Output WAVs saved to tests/output/
"""

import sys
import os
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import speechPlayer
import ipa
from tests.conftest import save_wav, collect_samples, OUTPUT_DIR, SAMPLE_RATE


def synthesize(ipa_text, filename=None, **kwargs):
    """Synthesize IPA text using sub-frame generator.

    Returns (samples, frame_count, elapsed_ms).
    """
    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)
    frame_count = 0
    t0 = time.perf_counter()
    for frame, duration, fade in ipa.generateSubFramesAndTiming(ipa_text, **kwargs):
        sp.queueFrame(frame, duration, fade)
        frame_count += 1
    elapsed = (time.perf_counter() - t0) * 1000
    samples = collect_samples(sp)
    if filename:
        save_wav(filename, samples)
    return samples, frame_count, elapsed


def test_basic_vowel():
    """Test sub-frame generation for a simple vowel."""
    print("\n=== Test: Basic Vowel /a/ ===")

    samples, frames, elapsed = synthesize(
        "a", filename="subframe_basic_vowel.wav",
        speed=1, basePitch=120, inflection=0
    )

    print(f"  Frames: {frames}, Samples: {len(samples)} ({len(samples)/SAMPLE_RATE:.2f}s)")
    print(f"  Generation time: {elapsed:.1f}ms")
    assert len(samples) > 1000, "Too few samples"
    assert frames > 1, "Expected multiple sub-frames"
    print("  PASSED")
    return True


def test_pitch_contour():
    """Test pitch interpolation in sub-frames."""
    print("\n=== Test: Pitch Contour (Falling) ===")

    synthesize("a", filename="subframe_falling_pitch.wav",
               speed=1, basePitch=150, inflection=0.5, clauseType='.')

    print("  PASSED - listen to WAV for pitch smoothness")
    return True


def test_coarticulation():
    """Test formant coarticulation trajectories in sub-frames."""
    print("\n=== Test: Coarticulation (CV/VC) ===")

    # /ba/ has bilabial onset coarticulation on F2
    synthesize("ba", filename="subframe_coarticulation_ba.wav",
               speed=1, basePitch=120, inflection=0)

    # /da/ has alveolar onset coarticulation
    synthesize("da", filename="subframe_coarticulation_da.wav",
               speed=1, basePitch=120, inflection=0)

    # /gab/ has velar onset + bilabial offset
    synthesize("gab", filename="subframe_coarticulation_gab.wav",
               speed=1, basePitch=120, inflection=0)

    print("  PASSED - listen to WAVs for formant transition quality")
    return True


def test_contour_tones():
    """Test 3-point contour tones with sub-frames."""
    print("\n=== Test: Contour Tones ===")

    synthesize("mǎ", filename="subframe_tone_rising.wav",
               speed=1, basePitch=120, inflection=0)

    synthesize("mâ", filename="subframe_tone_falling.wav",
               speed=1, basePitch=120, inflection=0)

    print("  PASSED - listen to WAVs for tone contour accuracy")
    return True


def test_fast_speech():
    """Test fast speech rate with sub-frames."""
    print("\n=== Test: Fast Speech (2x) ===")

    synthesize("hɛˈloʊ wɜːld aɪ æm ˈspiːkɪŋ",
               filename="subframe_fast_speech.wav",
               speed=2, basePitch=120, inflection=0.5, clauseType='.')

    print("  PASSED - listen to WAV for click-free fast speech")
    return True


def test_subframe_count():
    """Verify sub-frame count matches expected density."""
    print("\n=== Test: Sub-Frame Density ===")

    # A simple vowel at speed 1 should have ~12 sub-frames (60ms / 5ms)
    _, frame_count, _ = synthesize("a", speed=1, basePitch=120, inflection=0)

    print(f"  /a/ at speed=1: {frame_count} sub-frames")
    assert frame_count >= 5, f"Expected at least 5 sub-frames for /a/, got {frame_count}"

    # Longer text should produce many more
    _, frame_count2, _ = synthesize(
        "hɛˈloʊ wɜːld", speed=1, basePitch=120, inflection=0.5, clauseType='.'
    )

    print(f"  'hello world' at speed=1: {frame_count2} sub-frames")
    assert frame_count2 > 50, f"Expected >50 sub-frames for sentence, got {frame_count2}"
    print("  PASSED")
    return True


def test_performance():
    """Test generation performance on a long sentence."""
    print("\n=== Test: Performance ===")

    text = "ðə ˈkwɪk bɹaʊn fɑks ˈdʒʌmps ˈoʊvɚ ðə ˈleɪzi dɑg"
    samples, frames, elapsed = synthesize(
        text, filename="subframe_long_sentence.wav",
        speed=1, basePitch=120, inflection=0.5, clauseType='.'
    )

    print(f"  Frames: {frames}, Samples: {len(samples)} ({len(samples)/SAMPLE_RATE:.2f}s)")
    print(f"  Generation time: {elapsed:.1f}ms")
    print("  PASSED")
    return True


def run_all_tests():
    """Run all sub-frame architecture tests."""
    print("=" * 60)
    print("Sub-Frame Architecture Tests")
    print("=" * 60)

    tests = [
        test_basic_vowel,
        test_pitch_contour,
        test_coarticulation,
        test_contour_tones,
        test_fast_speech,
        test_subframe_count,
        test_performance,
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

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print(f"Output files in: {OUTPUT_DIR}")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
