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


def synthesize_vowel_frame(sp, f1=700, f2=1200, f3=2600, duration_ms=200, pitch=120):
    """Queue a vowel frame for CV/VC context."""
    frame = speechPlayer.Frame()
    frame.voicePitch = pitch
    frame.voiceAmplitude = 1.0
    frame.cf1, frame.cb1 = f1, 80
    frame.cf2, frame.cb2 = f2, 90
    frame.cf3, frame.cb3 = f3, 100
    frame.cf4, frame.cb4 = 3300, 150
    frame.preFormantGain = 1.0
    frame.outputGain = 1.0
    sp.queueFrame(frame, duration_ms, 50)


def synthesize_stop_burst(sp, burst_freq, voiced=False):
    """Synthesize a stop consonant burst."""
    frame = speechPlayer.Frame()

    if voiced:
        frame.voicePitch = 120
        frame.voiceAmplitude = 0.3
    else:
        frame.voicePitch = 0
        frame.voiceAmplitude = 0.0

    frame.burstAmplitude = 1.0
    frame.burstDuration = 0.5

    # Set formants based on place
    frame.cf1, frame.cb1 = 400, 80
    frame.cf2, frame.cb2 = burst_freq, 150
    frame.cf3, frame.cb3 = 2500, 100

    frame.preFormantGain = 0.5
    frame.outputGain = 1.0

    sp.queueFrame(frame, 30, 10)


def synthesize_fricative(sp, noise_freq, noise_bw, voiced=False, duration_ms=150):
    """Synthesize a fricative consonant."""
    frame = speechPlayer.Frame()

    if voiced:
        frame.voicePitch = 120
        frame.voiceAmplitude = 0.4

    frame.fricationAmplitude = 1.0
    frame.noiseFilterFreq = noise_freq
    frame.noiseFilterBW = noise_bw

    frame.cf1, frame.cb1 = 400, 80
    frame.cf2, frame.cb2 = 1500, 100
    frame.cf3, frame.cb3 = 2500, 100

    frame.preFormantGain = 0.4
    frame.outputGain = 1.0

    sp.queueFrame(frame, duration_ms, 30)


def synthesize_nasal(sp, f1, f2, f3, duration_ms=150):
    """Synthesize a nasal consonant."""
    frame = speechPlayer.Frame()

    frame.voicePitch = 120
    frame.voiceAmplitude = 1.0

    # Nasal formants with anti-resonance
    frame.cf1, frame.cb1 = f1, 100
    frame.cf2, frame.cb2 = f2, 100
    frame.cf3, frame.cb3 = f3, 100

    # Nasal pole and zero
    frame.cfNP = 480
    frame.cbNP = 60
    frame.cfN0 = 400
    frame.cbN0 = 100

    frame.preFormantGain = 0.8
    frame.outputGain = 1.0

    sp.queueFrame(frame, duration_ms, 40)


# Stop consonant parameters (burst frequencies)
STOPS = {
    'p': {'voiced': False, 'burst': 800, 'desc': 'voiceless bilabial'},
    'b': {'voiced': True, 'burst': 800, 'desc': 'voiced bilabial'},
    't': {'voiced': False, 'burst': 1700, 'desc': 'voiceless alveolar'},
    'd': {'voiced': True, 'burst': 1700, 'desc': 'voiced alveolar'},
    'k': {'voiced': False, 'burst': 1500, 'desc': 'voiceless velar'},
    'g': {'voiced': True, 'burst': 1500, 'desc': 'voiced velar'},
}

# Fricative parameters
FRICATIVES = {
    'f': {'voiced': False, 'freq': 0, 'bw': 2000, 'desc': 'voiceless labiodental'},
    'v': {'voiced': True, 'freq': 0, 'bw': 2000, 'desc': 'voiced labiodental'},
    's': {'voiced': False, 'freq': 5500, 'bw': 2000, 'desc': 'voiceless alveolar'},
    'z': {'voiced': True, 'freq': 5500, 'bw': 2000, 'desc': 'voiced alveolar'},
    'S': {'voiced': False, 'freq': 3500, 'bw': 1500, 'desc': 'voiceless postalveolar (sh)'},
    'Z': {'voiced': True, 'freq': 3500, 'bw': 1500, 'desc': 'voiced postalveolar (zh)'},
    'h': {'voiced': False, 'freq': 0, 'bw': 3000, 'desc': 'voiceless glottal'},
}

# Nasal parameters
NASALS = {
    'm': {'f1': 280, 'f2': 1100, 'f3': 2500, 'desc': 'bilabial'},
    'n': {'f1': 280, 'f2': 1700, 'f3': 2500, 'desc': 'alveolar'},
    'N': {'f1': 280, 'f2': 2000, 'f3': 2500, 'desc': 'velar (ng)'},
}


def collect_samples(sp):
    """Collect all synthesized samples."""
    samples = []
    while True:
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        samples.extend(chunk[i] for i in range(len(chunk)))
    return samples


def test_voiceless_stops():
    """Test voiceless stop consonants /p/, /t/, /k/."""
    print("\n=== Test: Voiceless Stops ===")

    sp = speechPlayer.SpeechPlayer(22050)

    for key in ['p', 't', 'k']:
        s = STOPS[key]
        print(f"  /{key}/ - {s['desc']}")

        # Silence
        silence = speechPlayer.Frame()
        silence.voiceAmplitude = 0.0
        sp.queueFrame(silence, 50, 10)

        # Burst
        synthesize_stop_burst(sp, s['burst'], voiced=False)

        # Following vowel /a/
        synthesize_vowel_frame(sp, duration_ms=200)

    samples = collect_samples(sp)
    
    save_wav("consonant_stops_voiceless.wav", samples)
    print("  PASSED")
    return True


def test_voiced_stops():
    """Test voiced stop consonants /b/, /d/, /g/."""
    print("\n=== Test: Voiced Stops ===")

    sp = speechPlayer.SpeechPlayer(22050)

    for key in ['b', 'd', 'g']:
        s = STOPS[key]
        print(f"  /{key}/ - {s['desc']}")

        silence = speechPlayer.Frame()
        silence.voiceAmplitude = 0.0
        sp.queueFrame(silence, 50, 10)

        synthesize_stop_burst(sp, s['burst'], voiced=True)
        synthesize_vowel_frame(sp, duration_ms=200)

    samples = collect_samples(sp)
    
    save_wav("consonant_stops_voiced.wav", samples)
    print("  PASSED")
    return True


def test_fricatives_voiceless():
    """Test voiceless fricatives /f/, /s/, /ʃ/, /h/."""
    print("\n=== Test: Voiceless Fricatives ===")

    sp = speechPlayer.SpeechPlayer(22050)

    for key in ['f', 's', 'S', 'h']:
        f = FRICATIVES[key]
        print(f"  /{key}/ - {f['desc']}")

        synthesize_fricative(sp, f['freq'], f['bw'], voiced=False)
        synthesize_vowel_frame(sp, duration_ms=150)

    samples = collect_samples(sp)
    
    save_wav("consonant_fricatives_voiceless.wav", samples)
    print("  PASSED")
    return True


def test_fricatives_voiced():
    """Test voiced fricatives /v/, /z/, /ʒ/."""
    print("\n=== Test: Voiced Fricatives ===")

    sp = speechPlayer.SpeechPlayer(22050)

    for key in ['v', 'z', 'Z']:
        f = FRICATIVES[key]
        print(f"  /{key}/ - {f['desc']}")

        synthesize_fricative(sp, f['freq'], f['bw'], voiced=True)
        synthesize_vowel_frame(sp, duration_ms=150)

    samples = collect_samples(sp)
    
    save_wav("consonant_fricatives_voiced.wav", samples)
    print("  PASSED")
    return True


def test_nasals():
    """Test nasal consonants /m/, /n/, /ŋ/."""
    print("\n=== Test: Nasals ===")

    sp = speechPlayer.SpeechPlayer(22050)

    for key in ['m', 'n', 'N']:
        n = NASALS[key]
        print(f"  /{key}/ - {n['desc']}")

        synthesize_nasal(sp, n['f1'], n['f2'], n['f3'])
        synthesize_vowel_frame(sp, duration_ms=150)

    samples = collect_samples(sp)
    
    save_wav("consonant_nasals.wav", samples)
    print("  PASSED")
    return True


def test_minimal_pairs():
    """Test minimal pairs to verify voicing contrast."""
    print("\n=== Test: Minimal Pairs ===")

    sp = speechPlayer.SpeechPlayer(22050)

    pairs = [('p', 'b'), ('t', 'd'), ('s', 'z')]

    for vl, vd in pairs:
        print(f"  /{vl}/ vs /{vd}/")

        # Voiceless
        if vl in STOPS:
            synthesize_stop_burst(sp, STOPS[vl]['burst'], voiced=False)
        else:
            synthesize_fricative(sp, FRICATIVES[vl]['freq'], FRICATIVES[vl]['bw'], voiced=False)
        synthesize_vowel_frame(sp, duration_ms=150)

        # Brief pause
        silence = speechPlayer.Frame()
        sp.queueFrame(silence, 100, 10)

        # Voiced
        if vd in STOPS:
            synthesize_stop_burst(sp, STOPS[vd]['burst'], voiced=True)
        else:
            synthesize_fricative(sp, FRICATIVES[vd]['freq'], FRICATIVES[vd]['bw'], voiced=True)
        synthesize_vowel_frame(sp, duration_ms=150)

    samples = collect_samples(sp)
    
    save_wav("consonant_minimal_pairs.wav", samples)
    print("  PASSED")
    return True


def run_all_tests():
    """Run all consonant tests."""
    print("=" * 50)
    print("NVSpeechPlayer Consonant Phoneme Tests")
    print("=" * 50)

    tests = [
        test_voiceless_stops,
        test_voiced_stops,
        test_fricatives_voiceless,
        test_fricatives_voiced,
        test_nasals,
        test_minimal_pairs,
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
