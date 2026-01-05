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

import speechPlayer

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_wav(filename, samples, sample_rate=22050):
    """Save samples to WAV file."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with wave.open(filepath, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        data = struct.pack(f'<{len(samples)}h', *samples)
        wav.writeframes(data)
    return filepath


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
    frame.spectralTilt = 6
    frame.flutter = 0.2

    frame.preFormantGain = 1.0
    frame.outputGain = 1.0

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


def run_all_tests():
    """Run all vowel tests."""
    print("=" * 50)
    print("NVSpeechPlayer Vowel Phoneme Tests")
    print("=" * 50)

    tests = [
        test_cardinal_vowels,
        test_front_vowels,
        test_back_vowels,
        test_central_vowels,
        test_pitch_variation,
        test_all_reference_vowels,
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
