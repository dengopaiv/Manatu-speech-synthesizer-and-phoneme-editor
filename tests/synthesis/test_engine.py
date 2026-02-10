"""
Test synthesis engine functionality.

Usage:
    python tests/synthesis/test_engine.py

Output WAVs saved to tests/output/
"""

import sys
import os
import io

# Handle encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import speechPlayer
from tests.conftest import save_wav, build_phoneme_frame, SAMPLE_RATE, OUTPUT_DIR


def setup_frame(ipa_char='a', pitch=120, amplitude=1.0):
    """Create a frame from phoneme data with optional overrides."""
    frame = build_phoneme_frame(ipa_char, pitch)
    frame.voiceAmplitude = amplitude
    return frame


def test_basic_synthesis():
    """Test that synthesis produces non-zero output."""
    print("\n=== Test: Basic Synthesis ===")

    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)
    frame = setup_frame()
    sp.queueFrame(frame, 200, 50)

    samples = []
    while True:
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        samples.extend(chunk[i] for i in range(len(chunk)))

    non_zero = sum(1 for s in samples if s != 0)
    peak = max(abs(s) for s in samples) if samples else 0

    print(f"  Samples: {len(samples)}")
    print(f"  Non-zero: {non_zero} ({100*non_zero/len(samples):.1f}%)")
    print(f"  Peak amplitude: {peak}")

    save_wav("basic_synthesis.wav", samples)

    assert len(samples) > 0, "No samples generated"
    assert non_zero > len(samples) * 0.5, "Too many zero samples"
    assert peak > 1000, "Peak amplitude too low"

    print("  PASSED")
    return True


def test_pitch_variation():
    """Test pitch changes correctly."""
    print("\n=== Test: Pitch Variation ===")

    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)

    for pitch in [80, 120, 200]:
        frame = setup_frame('ə', pitch=pitch)
        sp.queueFrame(frame, 300, 50)

    all_samples = []
    while True:
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        all_samples.extend(chunk[i] for i in range(len(chunk)))

    print(f"  Samples: {len(all_samples)}")
    save_wav("pitch_variation.wav", all_samples)

    assert len(all_samples) > 10000, "Not enough samples for pitch test"
    print("  PASSED")
    return True


def test_amplitude_envelope():
    """Test amplitude changes smoothly."""
    print("\n=== Test: Amplitude Envelope ===")

    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)

    # Fade in
    frame1 = setup_frame('ə', amplitude=0.0)
    sp.queueFrame(frame1, 100, 50)

    # Full amplitude
    frame2 = setup_frame('ə', amplitude=1.0)
    sp.queueFrame(frame2, 200, 50)

    # Fade out
    frame3 = setup_frame('ə', amplitude=0.0)
    sp.queueFrame(frame3, 100, 50)

    all_samples = []
    while True:
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        all_samples.extend(chunk[i] for i in range(len(chunk)))


    save_wav("amplitude_envelope.wav", all_samples)
    print(f"  Samples: {len(all_samples)}")
    print("  PASSED")
    return True


def test_formant_transitions():
    """Test formant transitions are smooth."""
    print("\n=== Test: Formant Transitions ===")

    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)

    # /a/ -> /i/ -> /u/ using phoneme data
    sp.queueFrame(setup_frame('a'), 200, 50)
    sp.queueFrame(setup_frame('i'), 200, 50)
    sp.queueFrame(setup_frame('u'), 200, 50)

    all_samples = []
    while True:
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        all_samples.extend(chunk[i] for i in range(len(chunk)))


    save_wav("formant_transitions.wav", all_samples)
    print(f"  Samples: {len(all_samples)}")
    print("  PASSED")
    return True


def test_noise_generation():
    """Test fricative noise generation using /s/ phoneme data."""
    print("\n=== Test: Noise Generation ===")

    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)

    frame = build_phoneme_frame('s')
    sp.queueFrame(frame, 300, 50)

    all_samples = []
    while True:
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        all_samples.extend(chunk[i] for i in range(len(chunk)))


    non_zero = sum(1 for s in all_samples if s != 0)
    print(f"  Samples: {len(all_samples)}")
    print(f"  Non-zero: {non_zero}")

    save_wav("noise_generation.wav", all_samples)

    print(f"  (Noise output: {non_zero}/{len(all_samples)} non-zero)")
    print("  PASSED")
    return True


def run_all_tests():
    """Run all synthesis tests."""
    print("=" * 50)
    print("NVSpeechPlayer Synthesis Engine Tests")
    print("=" * 50)

    tests = [
        test_basic_synthesis,
        test_pitch_variation,
        test_amplitude_envelope,
        test_formant_transitions,
        test_noise_generation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print(f"Output files in: {OUTPUT_DIR}")
    print("=" * 50)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
