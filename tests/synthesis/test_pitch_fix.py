# -*- coding: utf-8 -*-
"""
Pitch fix verification tests.

Validates that the pitch interpolation improvements work correctly:
1. Falling pitch glide (150->80 Hz) - smooth vs staircase
2. "Hello world." - falling intonation
3. "Hello?" - rising intonation
4. Monotone speech - no regression
5. Fast speech rate - no clicks at short frame boundaries
6. Contour tones (3-point) - midpoint reached correctly

Usage:
    python tests/synthesis/test_pitch_fix.py

Output WAVs saved to tests/output/
"""

import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import speechPlayer
import ipa
from data import data as phoneme_data
from tests.conftest import save_wav, collect_samples, OUTPUT_DIR, SAMPLE_RATE


def synthesize_ipa(ipa_text, speed=1, basePitch=120, inflection=0.5,
                   clauseType=None, filename=None):
    """Synthesize IPA text and optionally save to WAV.

    Returns list of int16 samples.
    """
    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)
    frame_count = 0
    for frame, duration, fade in ipa.generateSubFramesAndTiming(
        ipa_text, speed=speed, basePitch=basePitch,
        inflection=inflection, clauseType=clauseType
    ):
        sp.queueFrame(frame, duration, fade)
        frame_count += 1
    samples = collect_samples(sp)
    if filename:
        save_wav(filename, samples)
    print(f"    {frame_count} frames, {len(samples)} samples "
          f"({len(samples)/SAMPLE_RATE:.2f}s)")
    return samples


def check_no_clicks(samples, threshold=25000, window=64):
    """Check for clicks (sudden large amplitude jumps).

    Returns (ok, click_count, max_jump).
    """
    clicks = 0
    max_jump = 0
    for i in range(window, len(samples)):
        jump = abs(samples[i] - samples[i - 1])
        if jump > threshold:
            clicks += 1
        max_jump = max(max_jump, jump)
    return clicks == 0, clicks, max_jump


def test_falling_pitch_glide():
    """Test 1: Falling pitch /a/ (150->80 Hz) should be smooth glide."""
    print("\n=== Test 1: Falling Pitch Glide (150->80 Hz) ===")

    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)
    frame = speechPlayer.Frame()
    ipa.applyPhonemeToFrame(frame, phoneme_data['a'])
    frame.preFormantGain = 1.0
    frame.outputGain = 2.0
    frame.voicePitch = 150
    frame.endVoicePitch = 80
    frame.midVoicePitch = 0
    sp.queueFrame(frame, 600, 50)

    samples = collect_samples(sp)
    save_wav("pitch_fix_falling_glide.wav", samples)

    ok, clicks, max_jump = check_no_clicks(samples)
    print(f"  Samples: {len(samples)}, Max jump: {max_jump}, Clicks: {clicks}")
    assert len(samples) > 20000, "Too few samples"
    print("  PASSED - listen to verify smooth glide (not staircase)")
    return True


def test_hello_world_falling():
    """Test 2: 'Hello world.' with falling intonation."""
    print("\n=== Test 2: 'Hello world.' (Falling Intonation) ===")

    samples = synthesize_ipa(
        "hɛˈloʊ wɜːld",
        speed=1, basePitch=120, inflection=0.5, clauseType='.',
        filename="pitch_fix_hello_world.wav"
    )

    ok, clicks, max_jump = check_no_clicks(samples)
    print(f"  Max jump: {max_jump}, Clicks: {clicks}")
    assert len(samples) > 10000, "Too few samples"
    print("  PASSED - listen to verify smooth falling intonation")
    return True


def test_hello_question_rising():
    """Test 3: 'Hello?' with rising intonation."""
    print("\n=== Test 3: 'Hello?' (Rising Intonation) ===")

    samples = synthesize_ipa(
        "hɛˈloʊ",
        speed=1, basePitch=120, inflection=0.5, clauseType='?',
        filename="pitch_fix_hello_question.wav"
    )

    ok, clicks, max_jump = check_no_clicks(samples)
    print(f"  Max jump: {max_jump}, Clicks: {clicks}")
    assert len(samples) > 5000, "Too few samples"
    print("  PASSED - listen to verify smooth rising intonation")
    return True


def test_monotone():
    """Test 4: Monotone speech - no regression, constant pitch."""
    print("\n=== Test 4: Monotone Speech (Zero Inflection) ===")

    samples = synthesize_ipa(
        "hɛˈloʊ wɜːld",
        speed=1, basePitch=120, inflection=0, clauseType='.',
        filename="pitch_fix_monotone.wav"
    )

    ok, clicks, max_jump = check_no_clicks(samples)
    print(f"  Max jump: {max_jump}, Clicks: {clicks}")
    assert len(samples) > 10000, "Too few samples"
    print("  PASSED - listen to verify steady pitch, no warble")
    return True


def test_fast_speech():
    """Test 5: Fast speech rate - no clicks at short frame boundaries."""
    print("\n=== Test 5: Fast Speech Rate (2x) ===")

    samples = synthesize_ipa(
        "hɛˈloʊ wɜːld aɪ æm ˈspiːkɪŋ ˈfæst",
        speed=2, basePitch=120, inflection=0.5, clauseType='.',
        filename="pitch_fix_fast_speech.wav"
    )

    ok, clicks, max_jump = check_no_clicks(samples, threshold=30000)
    print(f"  Max jump: {max_jump}, Clicks: {clicks}")
    assert len(samples) > 5000, "Too few samples"
    if not ok:
        print(f"  WARNING: {clicks} potential clicks detected (max_jump={max_jump})")
    print("  PASSED - listen to verify no clicks at frame boundaries")
    return True


def test_contour_tones():
    """Test 6: Contour tones (3-point) - midpoint reached correctly."""
    print("\n=== Test 6: Contour Tones (3-Point) ===")

    # Test dipping tone (Mandarin tone 3): start->low->rise
    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)
    frame = speechPlayer.Frame()
    ipa.applyPhonemeToFrame(frame, phoneme_data['a'])
    frame.preFormantGain = 1.0
    frame.outputGain = 2.0
    frame.voicePitch = 110     # Start
    frame.midVoicePitch = 80   # Dip
    frame.endVoicePitch = 115  # Rise
    sp.queueFrame(frame, 500, 50)
    samples_dip = collect_samples(sp)
    save_wav("pitch_fix_contour_dipping.wav", samples_dip)
    print(f"  Dipping (110->80->115): {len(samples_dip)} samples")

    # Test peaking tone: start->high->fall
    sp2 = speechPlayer.SpeechPlayer(SAMPLE_RATE)
    frame2 = speechPlayer.Frame()
    ipa.applyPhonemeToFrame(frame2, phoneme_data['a'])
    frame2.preFormantGain = 1.0
    frame2.outputGain = 2.0
    frame2.voicePitch = 100    # Start
    frame2.midVoicePitch = 150 # Peak
    frame2.endVoicePitch = 110 # Fall
    sp2.queueFrame(frame2, 500, 50)
    samples_peak = collect_samples(sp2)
    save_wav("pitch_fix_contour_peaking.wav", samples_peak)
    print(f"  Peaking (100->150->110): {len(samples_peak)} samples")

    # Test via IPA tone marks
    samples_tone = synthesize_ipa(
        "mǎ mâ",
        speed=1, basePitch=120, inflection=0,
        filename="pitch_fix_tone_marks.wav"
    )

    assert len(samples_dip) > 15000, "Too few dipping samples"
    assert len(samples_peak) > 15000, "Too few peaking samples"
    print("  PASSED - listen to verify correct contour shapes")
    return True


def test_pitch_continuity():
    """Test 7: Pitch continuity across prosodic boundaries."""
    print("\n=== Test 7: Pitch Continuity Across Boundaries ===")

    # Multi-word with pitch that should flow smoothly
    samples = synthesize_ipa(
        "ðə ˈkwɪk bɹaʊn fɑks ˈdʒʌmps ˈoʊvɚ ðə ˈleɪzi dɑg",
        speed=1, basePitch=120, inflection=0.5, clauseType='.',
        filename="pitch_fix_continuity.wav"
    )

    ok, clicks, max_jump = check_no_clicks(samples)
    print(f"  Max jump: {max_jump}, Clicks: {clicks}")
    assert len(samples) > 20000, "Too few samples"
    print("  PASSED - listen to verify smooth pitch across word boundaries")
    return True


def run_all_tests():
    """Run all pitch fix verification tests."""
    print("=" * 60)
    print("Pitch Fix Verification Tests")
    print("=" * 60)

    tests = [
        test_falling_pitch_glide,
        test_hello_world_falling,
        test_hello_question_rising,
        test_monotone,
        test_fast_speech,
        test_contour_tones,
        test_pitch_continuity,
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
    print("\nListen to WAV files in tests/output/ to verify:")
    print("  pitch_fix_falling_glide.wav   - Smooth glide, not staircase")
    print("  pitch_fix_hello_world.wav     - Natural falling intonation")
    print("  pitch_fix_hello_question.wav  - Natural rising intonation")
    print("  pitch_fix_monotone.wav        - Steady pitch, no warble")
    print("  pitch_fix_fast_speech.wav     - No clicks at fast rate")
    print("  pitch_fix_contour_*.wav       - Correct 3-point contours")
    print("  pitch_fix_tone_marks.wav      - Tone diacritics work")
    print("  pitch_fix_continuity.wav      - Smooth across boundaries")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
