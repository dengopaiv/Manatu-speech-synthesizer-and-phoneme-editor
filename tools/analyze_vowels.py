#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Vowel Formant Analysis Tool

Analyzes synthesized vowels and compares against reference values.
Uses parselmouth (Praat Python bindings) for formant extraction.

Install: pip install praat-parselmouth

Usage:
    python analyze_vowels.py              # Analyze all vowels
    python analyze_vowels.py --vowel a    # Analyze specific vowel
    python analyze_vowels.py --wav test.wav  # Analyze existing wav file
"""

import os
import sys
import argparse

# Fix Unicode output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import parselmouth
    from parselmouth.praat import call
    HAS_PARSELMOUTH = True
except ImportError:
    HAS_PARSELMOUTH = False
    print("Warning: parselmouth not installed. Install with: pip install praat-parselmouth")

# Reference formant values (Adult Male, Hz) from Peterson & Barney / Hillenbrand
REFERENCE = {
    'i': {'F1': (270, 310), 'F2': (2290, 2790), 'F3': (3010, 3310), 'desc': 'close front unrounded'},
    'ɪ': {'F1': (390, 400), 'F2': (1990, 2100), 'F3': (2550, 2650), 'desc': 'near-close front'},
    'e': {'F1': (400, 480), 'F2': (2020, 2290), 'F3': (2600, 2700), 'desc': 'close-mid front'},
    'ɛ': {'F1': (530, 580), 'F2': (1840, 1920), 'F3': (2480, 2590), 'desc': 'open-mid front'},
    'æ': {'F1': (660, 750), 'F2': (1720, 1850), 'F3': (2410, 2500), 'desc': 'near-open front'},
    'a': {'F1': (730, 850), 'F2': (1090, 1350), 'F3': (2440, 2600), 'desc': 'open front'},
    'ɑ': {'F1': (710, 770), 'F2': (1090, 1220), 'F3': (2440, 2640), 'desc': 'open back unrounded'},
    'ɔ': {'F1': (570, 640), 'F2': (840, 920), 'F3': (2410, 2680), 'desc': 'open-mid back rounded'},
    'o': {'F1': (450, 500), 'F2': (830, 920), 'F3': (2380, 2500), 'desc': 'close-mid back rounded'},
    'ʊ': {'F1': (440, 470), 'F2': (1020, 1100), 'F3': (2240, 2380), 'desc': 'near-close back rounded'},
    'u': {'F1': (300, 340), 'F2': (870, 1020), 'F3': (2240, 2380), 'desc': 'close back rounded'},
    'ə': {'F1': (500, 520), 'F2': (1400, 1500), 'F3': (2400, 2500), 'desc': 'mid central (schwa)'},
}


def analyze_formants(wav_path, max_formant_hz=5500):
    """
    Analyze formants from a WAV file using Praat/parselmouth.

    Args:
        wav_path: Path to WAV file
        max_formant_hz: Maximum formant frequency (5500 for male, 5000 for female)

    Returns:
        dict with F1, F2, F3, F4 and their bandwidths
    """
    if not HAS_PARSELMOUTH:
        return None

    sound = parselmouth.Sound(wav_path)

    # Use Burg method for formant extraction (most reliable)
    # Parameters: time_step=0 (auto), max_formants=5, max_freq, window_length, pre_emphasis
    formant = call(sound, "To Formant (burg)", 0, 5, max_formant_hz, 0.025, 50)

    # Get values at midpoint (most stable region of sustained vowel)
    midpoint = sound.duration / 2

    results = {
        'duration_ms': round(sound.duration * 1000),
    }

    for i in range(1, 5):
        try:
            f = call(formant, "Get value at time", i, midpoint, "hertz", "Linear")
            b = call(formant, "Get bandwidth at time", i, midpoint, "hertz", "Linear")
            results[f'F{i}'] = round(f) if f == f else None  # NaN check
            results[f'B{i}'] = round(b) if b == b else None
        except:
            results[f'F{i}'] = None
            results[f'B{i}'] = None

    return results


def check_in_range(value, range_tuple):
    """Check if value is within range and return status string."""
    if value is None:
        return "N/A"
    low, high = range_tuple
    if value < low:
        return f"LOW ({value} < {low})"
    elif value > high:
        return f"HIGH ({value} > {high})"
    else:
        return f"OK ({low}-{high})"


def print_analysis(results, vowel=None):
    """Print analysis results in screen-reader friendly format."""
    print("\nFORMANT ANALYSIS RESULTS")
    print("=" * 50)
    print(f"Duration: {results.get('duration_ms', 'N/A')} ms")
    print()
    print("MEASURED FORMANTS:")
    for i in range(1, 5):
        f = results.get(f'F{i}')
        b = results.get(f'B{i}')
        f_str = str(f) if f else "N/A"
        b_str = str(b) if b else "N/A"
        print(f"  F{i}: {f_str} Hz (bandwidth: {b_str} Hz)")

    if vowel and vowel in REFERENCE:
        ref = REFERENCE[vowel]
        print()
        print(f"COMPARISON FOR VOWEL '{vowel}' ({ref['desc']}):")
        for i in range(1, 4):
            f = results.get(f'F{i}')
            ref_key = f'F{i}'
            if ref_key in ref:
                status = check_in_range(f, ref[ref_key])
                print(f"  F{i}: {status}")


def generate_vowel_wav(vowel, output_path, duration_ms=500):
    """Generate a vowel WAV file using the NVSpeechPlayer synthesizer."""
    try:
        import ipa
        import speechPlayer
        import wave
        import struct

        SAMPLE_RATE = 16000

        # Initialize synthesizer
        sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)

        # Queue frames for the vowel
        frame_count = 0
        for frame, duration, fade in ipa.generateFramesAndTiming(
            vowel,
            speed=0.5,  # Slower for sustained vowel
            basePitch=120,
            inflection=0
        ):
            if frame:
                sp.queueFrame(frame, duration, fade)
            else:
                sp.queueFrame(None, duration, fade)
            frame_count += 1

        if frame_count == 0:
            print(f"Error: No frames generated for vowel '{vowel}'")
            return False

        # Synthesize in batches
        all_samples = []
        BATCH_SIZE = 8192
        while True:
            samples = sp.synthesize(BATCH_SIZE)
            if samples and hasattr(samples, 'length') and samples.length > 0:
                all_samples.extend(samples[:samples.length])
            elif samples:
                all_samples.extend(samples[:])
                if len(samples) < BATCH_SIZE:
                    break
            else:
                break

        if not all_samples:
            print(f"Error: No samples generated for vowel '{vowel}'")
            return False

        # Write WAV file
        with wave.open(output_path, 'w') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)
            wav.writeframes(struct.pack('<%dh' % len(all_samples), *all_samples))

        return True
    except Exception as e:
        print(f"Error generating vowel: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='Analyze vowel formants')
    parser.add_argument('--wav', help='Path to existing WAV file to analyze')
    parser.add_argument('--vowel', help='Specific vowel to generate and analyze')
    parser.add_argument('--all', action='store_true', help='Analyze all reference vowels')
    parser.add_argument('--max-freq', type=int, default=5500,
                       help='Maximum formant frequency (5500 for male, 5000 for female)')
    args = parser.parse_args()

    if not HAS_PARSELMOUTH:
        print("ERROR: parselmouth is required for formant analysis.")
        print("Install with: pip install praat-parselmouth")
        print()
        print("Alternatively, use Praat directly:")
        print("  praat --run tools/analyze_formants.praat your_file.wav")
        sys.exit(1)

    if args.wav:
        # Analyze existing WAV file
        if not os.path.exists(args.wav):
            print(f"Error: File not found: {args.wav}")
            sys.exit(1)

        results = analyze_formants(args.wav, args.max_freq)
        print_analysis(results, args.vowel)

    elif args.vowel:
        # Generate and analyze specific vowel
        temp_wav = f"temp_{args.vowel}.wav"
        print(f"Generating vowel '{args.vowel}'...")

        if generate_vowel_wav(args.vowel, temp_wav):
            results = analyze_formants(temp_wav, args.max_freq)
            print_analysis(results, args.vowel)
            os.remove(temp_wav)
        else:
            print("Failed to generate vowel")

    elif args.all:
        # Analyze all reference vowels
        print("ANALYZING ALL REFERENCE VOWELS")
        print("=" * 60)

        for vowel in REFERENCE.keys():
            temp_wav = f"temp_{ord(vowel):04x}.wav"
            print(f"\n--- Vowel: {vowel} ({REFERENCE[vowel]['desc']}) ---")

            if generate_vowel_wav(vowel, temp_wav):
                results = analyze_formants(temp_wav, args.max_freq)
                if results:
                    print(f"  F1: {results.get('F1')} Hz (B1: {results.get('B1')} Hz)")
                    print(f"  F2: {results.get('F2')} Hz (B2: {results.get('B2')} Hz)")
                    print(f"  F3: {results.get('F3')} Hz (B3: {results.get('B3')} Hz)")

                    # Compare to reference
                    ref = REFERENCE[vowel]
                    for i in range(1, 4):
                        f = results.get(f'F{i}')
                        if f and f'F{i}' in ref:
                            status = check_in_range(f, ref[f'F{i}'])
                            if 'OK' not in status:
                                print(f"    -> F{i} {status}")

                os.remove(temp_wav)
            else:
                print("  (Failed to generate)")

    else:
        parser.print_help()
        print()
        print("Examples:")
        print("  python analyze_vowels.py --wav test.wav")
        print("  python analyze_vowels.py --vowel a")
        print("  python analyze_vowels.py --all")


if __name__ == '__main__':
    main()
