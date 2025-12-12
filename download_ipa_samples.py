#!/usr/bin/env python3
"""
Download IPA reference audio samples from Wikimedia Commons.

Run this script once to populate the samples/ folder with human-recorded
IPA sounds for comparison with synthesized phonemes.

Usage:
    python download_ipa_samples.py          # Download and convert to WAV
    python download_ipa_samples.py --list   # List available samples
    python download_ipa_samples.py --convert # Convert existing .ogg to .wav

Files are downloaded as .ogg and converted to .wav for instant playback.
The phoneme editor uses F7 to play these reference samples.

Source: https://commons.wikimedia.org/wiki/Category:International_Phonetic_Alphabet
License: CC BY-SA 3.0 or Public Domain (varies by file)
"""

import os
import sys
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

# Where to save downloaded samples
SAMPLES_DIR = Path(__file__).parent / "samples"

# Wikimedia Commons base URL for direct file downloads
WIKIMEDIA_REDIRECT = "https://commons.wikimedia.org/wiki/Special:Redirect/file/"

# Mapping: IPA symbol -> Wikimedia Commons filename
# Based on standard IPA vowel and consonant chart naming conventions
IPA_SAMPLES = {
    # === VOWELS - FRONT ===
    'i': 'Close_front_unrounded_vowel.ogg',
    'y': 'Close_front_rounded_vowel.ogg',
    'ɪ': 'Near-close_near-front_unrounded_vowel.ogg',
    'ʏ': 'Near-close_near-front_rounded_vowel.ogg',
    'e': 'Close-mid_front_unrounded_vowel.ogg',
    'ø': 'Close-mid_front_rounded_vowel.ogg',
    'ɛ': 'Open-mid_front_unrounded_vowel.ogg',
    'œ': 'Open-mid_front_rounded_vowel.ogg',
    'æ': 'Near-open_front_unrounded_vowel.ogg',
    'a': 'Open_front_unrounded_vowel.ogg',
    'ɶ': 'Open_front_rounded_vowel.ogg',

    # === VOWELS - CENTRAL ===
    'ɨ': 'Close_central_unrounded_vowel.ogg',
    'ʉ': 'Close_central_rounded_vowel.ogg',
    'ɘ': 'Close-mid_central_unrounded_vowel.ogg',
    'ɵ': 'Close-mid_central_rounded_vowel.ogg',
    'ə': 'Mid_central_vowel.ogg',
    'ɜ': 'Open-mid_central_unrounded_vowel.ogg',
    'ɞ': 'Open-mid_central_rounded_vowel.ogg',
    'ɐ': 'Near-open_central_vowel.ogg',
    'ä': 'Open_central_unrounded_vowel.ogg',

    # === VOWELS - BACK ===
    'ɯ': 'Close_back_unrounded_vowel.ogg',
    'u': 'Close_back_rounded_vowel.ogg',
    'ʊ': 'Near-close_near-back_rounded_vowel.ogg',
    'ɤ': 'Close-mid_back_unrounded_vowel.ogg',
    'o': 'Close-mid_back_rounded_vowel.ogg',
    'ʌ': 'Open-mid_back_unrounded_vowel.ogg',
    'ɔ': 'Open-mid_back_rounded_vowel.ogg',
    'ɑ': 'Open_back_unrounded_vowel.ogg',
    'ɒ': 'Open_back_rounded_vowel.ogg',

    # === VOWELS - R-COLORED ===
    'ɝ': 'En-us-er.ogg',  # American English 'er' sound
    'ɚ': 'En-us-er.ogg',  # Same file, r-colored schwa

    # === STOPS (PLOSIVES) ===
    'p': 'Voiceless_bilabial_plosive.ogg',
    'b': 'Voiced_bilabial_plosive.ogg',
    't': 'Voiceless_alveolar_plosive.ogg',
    'd': 'Voiced_alveolar_plosive.ogg',
    'k': 'Voiceless_velar_plosive.ogg',
    'g': 'Voiced_velar_plosive.ogg',
    'ʔ': 'Glottal_stop.ogg',
    'ʈ': 'Voiceless_retroflex_plosive.ogg',
    'ɖ': 'Voiced_retroflex_plosive.ogg',

    # === FRICATIVES ===
    'f': 'Voiceless_labiodental_fricative.ogg',
    'v': 'Voiced_labiodental_fricative.ogg',
    'θ': 'Voiceless_dental_fricative.ogg',
    'ð': 'Voiced_dental_fricative.ogg',
    's': 'Voiceless_alveolar_sibilant.ogg',
    'z': 'Voiced_alveolar_sibilant.ogg',
    'ʃ': 'Voiceless_palato-alveolar_sibilant.ogg',
    'ʒ': 'Voiced_palato-alveolar_sibilant.ogg',
    'x': 'Voiceless_velar_fricative.ogg',
    'ɣ': 'Voiced_velar_fricative.ogg',
    'h': 'Voiceless_glottal_fricative.ogg',
    'ɦ': 'Voiced_glottal_fricative.ogg',
    'ç': 'Voiceless_palatal_fricative.ogg',
    'ʝ': 'Voiced_palatal_fricative.ogg',

    # === AFFRICATES ===
    'tʃ': 'Voiceless_palato-alveolar_affricate.ogg',
    'dʒ': 'Voiced_palato-alveolar_affricate.ogg',

    # === NASALS ===
    'm': 'Bilabial_nasal.ogg',
    'n': 'Alveolar_nasal.ogg',
    'ŋ': 'Velar_nasal.ogg',
    'ɲ': 'Palatal_nasal.ogg',
    'ɳ': 'Retroflex_nasal.ogg',

    # === LIQUIDS & GLIDES ===
    'l': 'Alveolar_lateral_approximant.ogg',
    'ɹ': 'Alveolar_approximant.ogg',
    'r': 'Alveolar_trill.ogg',
    'ɾ': 'Alveolar_tap.ogg',
    'j': 'Palatal_approximant.ogg',
    'w': 'Voiced_labio-velar_approximant.ogg',
    'ʍ': 'Voiceless_labio-velar_fricative.ogg',
    'ɫ': 'Velarized_alveolar_lateral_approximant.ogg',

    # === SPECIAL ===
    ' ': None,  # Silence - no sample needed
    '_': None,  # Pause - no sample needed
}


def check_ffmpeg():
    """Check if ffmpeg is available."""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_codepoint(ipa_char):
    """Get the codepoint string for an IPA character."""
    if len(ipa_char) == 1:
        return f"{ord(ipa_char):04X}"
    else:
        # Multi-character (e.g., affricates)
        return '_'.join(f"{ord(c):04X}" for c in ipa_char)


def get_sample_path(ipa_char, extension='wav'):
    """Get the local file path for an IPA sample."""
    codepoint = get_codepoint(ipa_char)
    return SAMPLES_DIR / f"{codepoint}_{ipa_char}.{extension}"


def convert_ogg_to_wav(ogg_path, wav_path):
    """Convert .ogg to .wav using ffmpeg."""
    try:
        result = subprocess.run([
            'ffmpeg', '-y', '-i', str(ogg_path),
            '-ar', '44100', '-ac', '1',
            '-loglevel', 'error',
            str(wav_path)
        ], capture_output=True, timeout=30)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False


def download_sample(ipa_char, filename, convert=True):
    """Download a single sample from Wikimedia Commons."""
    if filename is None:
        return True  # Skip intentionally empty entries

    wav_path = get_sample_path(ipa_char, 'wav')
    ogg_path = get_sample_path(ipa_char, 'ogg')

    # Check if WAV already exists
    if wav_path.exists():
        print(f"  [{ipa_char}] Already exists: {wav_path.name}")
        return True

    # Check if OGG exists (needs conversion)
    if ogg_path.exists() and convert:
        print(f"  [{ipa_char}] Converting {ogg_path.name}...", end=" ", flush=True)
        if convert_ogg_to_wav(ogg_path, wav_path):
            ogg_path.unlink()  # Remove .ogg after successful conversion
            print("OK")
            return True
        else:
            print("FAILED")
            return False

    # Download from Wikimedia
    url = WIKIMEDIA_REDIRECT + urllib.request.quote(filename)

    try:
        print(f"  [{ipa_char}] Downloading {filename}...", end=" ", flush=True)

        request = urllib.request.Request(
            url,
            headers={'User-Agent': 'NVSpeechPlayer/1.0 (IPA sample downloader)'}
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
            ogg_path.write_bytes(data)
            print(f"OK ({len(data)} bytes)", end="")

        # Convert to WAV if ffmpeg is available
        if convert:
            print(" -> Converting...", end=" ", flush=True)
            if convert_ogg_to_wav(ogg_path, wav_path):
                ogg_path.unlink()  # Remove .ogg after successful conversion
                print("OK")
            else:
                print("FAILED (keeping .ogg)")
        else:
            print()

        return True

    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def download_all():
    """Download all IPA samples."""
    print("IPA Reference Sample Downloader")
    print("=" * 50)
    print(f"Source: Wikimedia Commons")
    print(f"License: CC BY-SA 3.0 / Public Domain")
    print(f"Output: {SAMPLES_DIR}")
    print()

    # Check for ffmpeg
    has_ffmpeg = check_ffmpeg()
    if has_ffmpeg:
        print("ffmpeg found - will convert to WAV for instant playback")
    else:
        print("WARNING: ffmpeg not found - samples will be .ogg format")
        print("         Install ffmpeg for WAV conversion (faster playback)")
        print("         https://ffmpeg.org/download.html")
    print()

    # Create samples directory
    SAMPLES_DIR.mkdir(exist_ok=True)

    # Track results
    success = 0
    skipped = 0
    failed = 0
    failed_list = []

    print("Downloading samples...")
    print()

    for ipa_char, filename in IPA_SAMPLES.items():
        if filename is None:
            skipped += 1
            continue

        if download_sample(ipa_char, filename, convert=has_ffmpeg):
            success += 1
        else:
            failed += 1
            failed_list.append((ipa_char, filename))

    print()
    print("=" * 50)
    print(f"Results: {success} downloaded, {skipped} skipped, {failed} failed")

    if failed_list:
        print()
        print("Failed downloads:")
        for ipa, filename in failed_list:
            print(f"  [{ipa}] {filename}")
        print()
        print("Some files may have different names on Wikimedia Commons.")
        print("You can manually download them from:")
        print("  https://commons.wikimedia.org/wiki/Category:International_Phonetic_Alphabet")

    return failed == 0


def convert_existing():
    """Convert any existing .ogg files to .wav."""
    if not check_ffmpeg():
        print("ERROR: ffmpeg is required for conversion")
        print("       Install ffmpeg: https://ffmpeg.org/download.html")
        return False

    print("Converting existing .ogg files to .wav...")
    print()

    if not SAMPLES_DIR.exists():
        print("No samples folder found.")
        return True

    converted = 0
    failed = 0

    for ogg_path in SAMPLES_DIR.glob("*.ogg"):
        wav_path = ogg_path.with_suffix('.wav')
        if wav_path.exists():
            print(f"  {ogg_path.name} -> already converted")
            continue

        print(f"  {ogg_path.name} -> ", end="", flush=True)
        if convert_ogg_to_wav(ogg_path, wav_path):
            ogg_path.unlink()
            print("OK")
            converted += 1
        else:
            print("FAILED")
            failed += 1

    print()
    print(f"Converted: {converted}, Failed: {failed}")
    return failed == 0


def list_available():
    """List which samples are available locally."""
    print(f"Available IPA samples in {SAMPLES_DIR}:")
    print()

    if not SAMPLES_DIR.exists():
        print("  (samples folder not found - run download first)")
        return

    wav_count = 0
    ogg_count = 0
    missing = 0

    for ipa_char, filename in IPA_SAMPLES.items():
        if filename is None:
            continue

        wav_path = get_sample_path(ipa_char, 'wav')
        ogg_path = get_sample_path(ipa_char, 'ogg')

        if wav_path.exists():
            print(f"  [{ipa_char}] {wav_path.name} (WAV)")
            wav_count += 1
        elif ogg_path.exists():
            print(f"  [{ipa_char}] {ogg_path.name} (OGG - needs conversion)")
            ogg_count += 1
        else:
            missing += 1

    print()
    print(f"WAV: {wav_count}, OGG: {ogg_count}, Missing: {missing}")
    if ogg_count > 0:
        print("Run with --convert to convert OGG files to WAV")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            list_available()
        elif sys.argv[1] == '--convert':
            success = convert_existing()
            sys.exit(0 if success else 1)
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Usage: python download_ipa_samples.py [--list|--convert]")
            sys.exit(1)
    else:
        success = download_all()
        sys.exit(0 if success else 1)
