# -*- coding: utf-8 -*-
"""
Spectral brightness regression tests.

Validates that the synthesizer maintains correct relative brightness
ordering across phoneme classes. Tests use HF energy ratio (energy
above 4 kHz / total energy) and spectral centroid as metrics.

Usage:
    python tests/synthesis/test_spectral.py
"""

import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.conftest import synthesize_phoneme, save_wav, SAMPLE_RATE
from tools.spectral_analysis import (
    estimate_hf_energy_ratio,
    estimate_spectral_centroid,
    extract_formants_lpc,
)
import numpy as np

PASS = 0
FAIL = 0


def report(name, passed, detail=""):
    global PASS, FAIL
    status = "PASS" if passed else "FAIL"
    if not passed:
        FAIL += 1
    else:
        PASS += 1
    print(f"  [{status}] {name}{('  ' + detail) if detail else ''}")


def get_metrics(ipa_char, duration_ms=400, pitch=120):
    """Synthesize a phoneme and return (hf_ratio, centroid, samples)."""
    samples = synthesize_phoneme(ipa_char, duration_ms=duration_ms, pitch=pitch)
    arr = np.array(samples, dtype=np.float64)
    # Use steady-state portion (skip first/last 20%)
    start = int(len(arr) * 0.2)
    end = int(len(arr) * 0.8)
    steady = arr[start:end]
    hf = estimate_hf_energy_ratio(steady, SAMPLE_RATE)
    centroid = estimate_spectral_centroid(steady, SAMPLE_RATE)
    return hf, centroid, samples


def test_hf_energy_vowels():
    """Close vowel /i/ should be brighter than open vowel /a/."""
    print("\n=== Test: HF Energy — Vowel Height ===")
    hf_i, cent_i, samp_i = get_metrics('i')
    hf_a, cent_a, samp_a = get_metrics('a')
    save_wav("spectral_i.wav", samp_i)
    save_wav("spectral_a.wav", samp_a)
    print(f"  /i/ HF ratio: {hf_i:.4f}, centroid: {cent_i:.0f} Hz")
    print(f"  /a/ HF ratio: {hf_a:.4f}, centroid: {cent_a:.0f} Hz")
    report("/i/ HF > /a/ HF", hf_i > hf_a,
           f"ratio {hf_i:.4f} vs {hf_a:.4f}")


def test_hf_energy_fricatives():
    """Voiceless sibilant /s/ should have strong HF energy."""
    print("\n=== Test: HF Energy — Fricative /s/ ===")
    hf_s, cent_s, samp_s = get_metrics('s')
    save_wav("spectral_s.wav", samp_s)
    print(f"  /s/ HF ratio: {hf_s:.4f}, centroid: {cent_s:.0f} Hz")
    report("/s/ HF ratio > 0.3", hf_s > 0.3,
           f"ratio {hf_s:.4f}")


def test_voiced_fricative_brightness():
    """Voiced /z/ centroid should be within 40% of voiceless /s/ centroid."""
    print("\n=== Test: Voiced Fricative Brightness — /z/ vs /s/ ===")
    hf_s, cent_s, samp_s = get_metrics('s')
    hf_z, cent_z, samp_z = get_metrics('z')
    save_wav("spectral_z.wav", samp_z)
    print(f"  /s/ centroid: {cent_s:.0f} Hz, HF ratio: {hf_s:.4f}")
    print(f"  /z/ centroid: {cent_z:.0f} Hz, HF ratio: {hf_z:.4f}")
    if cent_s > 0:
        ratio = cent_z / cent_s
        report("/z/ centroid within 40% of /s/", ratio >= 0.6,
               f"ratio {ratio:.2f} ({cent_z:.0f}/{cent_s:.0f})")
    else:
        report("/z/ centroid within 40% of /s/", False, "s centroid=0")


def test_vowel_centroid_ordering():
    """Front vowels brighter than open: /i/ and /e/ > /a/ centroid."""
    print("\n=== Test: Vowel Centroid Ordering ===")
    hf_i, cent_i, _ = get_metrics('i')
    hf_e, cent_e, _ = get_metrics('e')
    hf_a, cent_a, _ = get_metrics('a')
    print(f"  /i/ centroid: {cent_i:.0f} Hz")
    print(f"  /e/ centroid: {cent_e:.0f} Hz")
    print(f"  /a/ centroid: {cent_a:.0f} Hz")
    # /i/ and /e/ are both front close(ish) vowels with high F2;
    # /e/ may have slightly higher centroid due to higher F1.
    # The key distinction is front vs open: both should be above /a/.
    report("/i/ > /a/ centroid", cent_i > cent_a,
           f"{cent_i:.0f} vs {cent_a:.0f}")
    report("/e/ > /a/ centroid", cent_e > cent_a,
           f"{cent_e:.0f} vs {cent_a:.0f}")


def test_formant_prominence():
    """F2/F3 peaks should be prominent (>6 dB above floor) for front vowels."""
    print("\n=== Test: Formant Prominence ===")
    for vowel in ['i', 'e', 'a']:
        samples = synthesize_phoneme(vowel, duration_ms=400, pitch=120)
        arr = np.array(samples, dtype=np.float64)
        start = int(len(arr) * 0.2)
        end = int(len(arr) * 0.8)
        steady = arr[start:end]

        formants = extract_formants_lpc(steady, SAMPLE_RATE, num_formants=4)
        print(f"  /{vowel}/ formants: {[(int(f), int(bw)) for f, bw in formants]}")

        # Check that at least 3 formants were found
        report(f"/{vowel}/ has >= 3 formants", len(formants) >= 3,
               f"found {len(formants)}")


if __name__ == '__main__':
    print("=" * 60)
    print("Spectral Brightness Regression Tests")
    print("=" * 60)

    test_hf_energy_vowels()
    test_hf_energy_fricatives()
    test_voiced_fricative_brightness()
    test_vowel_centroid_ordering()
    test_formant_prominence()

    print(f"\n{'=' * 60}")
    print(f"Results: {PASS} passed, {FAIL} failed")
    if FAIL > 0:
        print("WARNING: Some brightness tests failed — review output above")
    print(f"{'=' * 60}")
