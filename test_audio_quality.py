#!/usr/bin/env python3
"""
Audio Quality Test Script for NVSpeechPlayer

Tests voiced consonants and generates WAV files for analysis.
"""

import wave
import struct
import os
import sys

# Fix Unicode output on Windows
sys.stdout.reconfigure(encoding='utf-8')

import speechPlayer
import ipa

SAMPLE_RATE = 22050

def synthesize_to_wav(ipa_text, filename, speed=1.0, pitch=120, inflection=0.5):
    """Synthesize IPA text to a WAV file.

    Uses batched synthesis pattern like NVDA addon:
    1. Queue ALL frames first (enables proper inter-frame interpolation)
    2. Synthesize in batches of 8192 samples until done
    """
    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)
    all_samples = []

    print(f"Synthesizing: {ipa_text}")

    # Step 1: Queue ALL frames first
    frame_count = 0
    for frame, duration, fade in ipa.generateFramesAndTiming(
        ipa_text,
        speed=speed,
        basePitch=pitch,
        inflection=inflection
    ):
        if frame:
            sp.queueFrame(frame, duration, fade)
        else:
            sp.queueFrame(None, duration, fade)
        frame_count += 1

    if frame_count == 0:
        print(f"  No frames generated!")
        return False

    # Step 2: Synthesize in batches (like NVDA does)
    BATCH_SIZE = 8192
    while True:
        samples = sp.synthesize(BATCH_SIZE)
        if samples and hasattr(samples, 'length') and samples.length > 0:
            all_samples.extend(samples[:samples.length])
        elif samples:
            # Fallback if length attribute not set
            all_samples.extend(samples[:])
            if len(samples) < BATCH_SIZE:
                break
        else:
            break  # No more samples

    if not all_samples:
        print(f"  No samples generated!")
        return False

    # Save to WAV
    with wave.open(filename, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(struct.pack('<%dh' % len(all_samples), *all_samples))

    print(f"  Saved: {filename} ({len(all_samples)} samples, {len(all_samples)/SAMPLE_RATE:.2f}s)")
    return True


def test_voiced_consonants():
    """Test the voiced consonants that broke in eSpeak-ng 1.48-1.49."""
    print("\n=== Testing Voiced Consonants ===")
    print("These broke in eSpeak-ng 1.48-1.49 and killed NVSpeechPlayer\n")

    tests = [
        ("z", "aza", "z - voiced alveolar fricative"),
        ("v", "ava", "v - voiced labiodental fricative"),
        ("ʒ", "aʒa", "ʒ (ezh) - voiced postalveolar fricative"),
        ("j", "aja", "j - palatal approximant"),
        ("g", "aga", "g - voiced velar plosive"),
        ("ð", "aða", "ð (eth) - voiced dental fricative"),
        ("b", "aba", "b - voiced bilabial plosive"),
        ("d", "ada", "d - voiced alveolar plosive"),
    ]

    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)

    for phoneme, test_str, description in tests:
        print(f"\nTesting {description}:")
        filename = os.path.join(output_dir, f"voiced_{phoneme.replace('ʒ', 'ezh').replace('ð', 'eth')}.wav")
        synthesize_to_wav(test_str, filename)


def test_vowel_sequences():
    """Test vowel-to-vowel transitions for smoothness."""
    print("\n=== Testing Vowel Sequences ===")

    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)

    # Simple vowel sequence
    synthesize_to_wav("ieiaeaoouui", os.path.join(output_dir, "vowel_sequence.wav"))

    # With consonant transitions
    synthesize_to_wav("babababa", os.path.join(output_dir, "ba_sequence.wav"))
    synthesize_to_wav("dadadadada", os.path.join(output_dir, "da_sequence.wav"))


def test_mixed_utterances():
    """Test mixed utterances that expose transition issues."""
    print("\n=== Testing Mixed Utterances ===")

    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)

    tests = [
        ("ˈzævəʒə", "zavazha.wav", "Tests z, v, ʒ transitions"),
        ("bædʒə", "badge.wav", "Tests affricate"),
        ("hɛˈloʊ", "hello.wav", "Simple hello"),
        ("ðə kwɪk bɹaʊn fɑks", "quick_brown_fox.wav", "Multiple consonant types"),
    ]

    for ipa_text, filename, description in tests:
        print(f"\n{description}:")
        synthesize_to_wav(ipa_text, os.path.join(output_dir, filename))


def analyze_timing():
    """Print timing information for analysis."""
    print("\n=== Timing Analysis ===")

    test_text = "aba"
    phonemes = ipa.IPAToPhonemes(test_text)
    ipa.correctHPhonemes(phonemes)
    ipa.calculatePhonemeTimes(phonemes, baseSpeed=1.0)

    print(f"\nPhoneme timing for '{test_text}':")
    for p in phonemes:
        char = p.get('_char', '?')
        duration = p.get('_duration', 0)
        fade = p.get('_fadeDuration', 0)
        is_voiced = p.get('_isVoiced', False)
        is_stop = p.get('_isStop', False)
        print(f"  {char}: duration={duration:.1f}ms, fade={fade:.3f}ms, voiced={is_voiced}, stop={is_stop}")


def main():
    print("NVSpeechPlayer Audio Quality Test")
    print("=" * 50)

    analyze_timing()
    test_voiced_consonants()
    test_vowel_sequences()
    test_mixed_utterances()

    print("\n" + "=" * 50)
    print("Tests complete! WAV files saved to test_output/")
    print("Listen to them to identify choppiness issues.")


if __name__ == "__main__":
    main()
