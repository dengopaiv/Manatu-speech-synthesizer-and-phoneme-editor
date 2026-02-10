# -*- coding: utf-8 -*-
"""
Consonant Differentiation Diagnostic Tool.

Synthesizes consonants in CV/VCV context, measures spectral profiles,
and reports pairwise differentiation scores for confusable pairs.

Measures:
- Stops: burst centroid, peak frequency, spectral tilt
- Fricatives: centroid, peak prominence, spectral flatness
- Nasals: anti-resonance frequency, band energy ratios, spectral slope (VCV context)

Usage:
    python tools/consonant_diagnostic.py              # Full report
    python tools/consonant_diagnostic.py --category stops   # One category
    python tools/consonant_diagnostic.py --wav         # Also save WAVs
"""

import os
import sys
import io
import argparse
import wave
import struct

# Fix encoding for IPA output on Windows
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import numpy as np
from scipy.signal.windows import hamming

import speechPlayer
import ipa
from data import data as phoneme_data

SAMPLE_RATE = 44100
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'tests', 'output')

# ── Confusable pairs ─────────────────────────────────────────────────

STOP_PAIRS = [
    ('p', 't', 'k'),   # voiceless stops
    ('b', 'd', 'g'),   # voiced stops
]

FRICATIVE_PAIRS = [
    ('f', 'θ'),   # labiodental vs dental
    ('v', 'ð'),   # voiced counterparts
    ('s', 'ʃ'),   # alveolar vs postalveolar sibilant
]

NASAL_PAIRS = [
    ('m', 'n', 'ŋ'),  # bilabial, alveolar, velar
]

# ── Synthesis helpers ─────────────────────────────────────────────────

def _build_frame(ipa_char, pitch=120):
    """Build a frame from phoneme data."""
    frame = speechPlayer.Frame()
    ipa.applyPhonemeToFrame(frame, phoneme_data[ipa_char])
    frame.preFormantGain = 1.0
    frame.outputGain = 2.0
    frame.voicePitch = pitch
    frame.endVoicePitch = pitch
    return frame


def _collect_samples(sp):
    """Drain all samples from a SpeechPlayer."""
    samples = []
    while True:
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        samples.extend(chunk[i] for i in range(len(chunk)))
    return samples


def _save_wav(filename, samples):
    """Save samples as WAV."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with wave.open(filepath, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        data = struct.pack(f'<{len(samples)}h', *samples)
        wav.writeframes(data)
    return filepath


def synthesize_cv(consonant_char, vowel_char='a', pitch=120):
    """Synthesize a CV syllable (consonant + vowel).

    Returns:
        (all_samples, consonant_samples, vowel_samples)
    """
    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)
    c_data = phoneme_data[consonant_char]

    # Consonant frame
    c_frame = _build_frame(consonant_char, pitch)
    if c_data.get('_isStop'):
        sp.queueFrame(c_frame, 30, 10)
    elif c_data.get('_isNasal'):
        sp.queueFrame(c_frame, 120, 40)
    else:
        sp.queueFrame(c_frame, 150, 30)

    # Vowel frame
    v_frame = _build_frame(vowel_char, pitch)
    sp.queueFrame(v_frame, 200, 50)

    all_samples = _collect_samples(sp)

    # Split: consonant region is first ~portion, vowel is rest
    if c_data.get('_isStop'):
        split_point = int(SAMPLE_RATE * 0.030)
    elif c_data.get('_isNasal'):
        split_point = int(SAMPLE_RATE * 0.120)
    else:
        split_point = int(SAMPLE_RATE * 0.150)

    split_point = min(split_point, len(all_samples))
    return all_samples, all_samples[:split_point], all_samples[split_point:]


def synthesize_vcv(consonant_char, vowel_char='a', pitch=120):
    """Synthesize a VCV sequence for nasal analysis.

    Returns:
        (all_samples, consonant_samples)
    """
    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)

    # First vowel
    v_frame = _build_frame(vowel_char, pitch)
    sp.queueFrame(v_frame, 150, 40)

    # Consonant — 200ms for stable steady-state
    c_frame = _build_frame(consonant_char, pitch)
    sp.queueFrame(c_frame, 200, 40)

    # Second vowel
    v_frame2 = _build_frame(vowel_char, pitch)
    sp.queueFrame(v_frame2, 150, 40)

    all_samples = _collect_samples(sp)

    # Consonant region: skip V1 (150ms), take consonant (200ms)
    v1_end = int(SAMPLE_RATE * 0.150)
    c_end = int(SAMPLE_RATE * 0.350)
    v1_end = min(v1_end, len(all_samples))
    c_end = min(c_end, len(all_samples))
    return all_samples, all_samples[v1_end:c_end]


# ── Spectral measurement ─────────────────────────────────────────────

def measure_burst_spectrum(samples, sample_rate=SAMPLE_RATE):
    """Measure spectral properties of a stop burst (first 15-25ms).

    Returns dict with: centroid, peak_freq, spectral_tilt, energy
    """
    samples = np.asarray(samples, dtype=np.float64)

    # Take first 25ms for burst analysis
    burst_len = min(int(sample_rate * 0.025), len(samples))
    if burst_len < 50:
        return None

    burst = samples[:burst_len]

    max_val = np.max(np.abs(burst))
    if max_val < 1:
        return None
    burst = burst / max_val

    # Windowed FFT
    windowed = burst * hamming(len(burst))
    spectrum = np.abs(np.fft.rfft(windowed))
    freqs = np.fft.rfftfreq(len(windowed), 1.0 / sample_rate)

    # Convert to dB
    spectrum_db = 20 * np.log10(np.maximum(spectrum, 1e-10))

    # Only analyze above 200 Hz
    mask = freqs >= 200
    if not np.any(mask):
        return None

    a_freqs = freqs[mask]
    a_spec = spectrum[mask]
    a_db = spectrum_db[mask]

    # Centroid
    total_energy = np.sum(a_spec)
    if total_energy <= 0:
        return None
    centroid = np.sum(a_freqs * a_spec) / total_energy

    # Smoothed peak
    kernel_size = max(3, len(a_db) // 30)
    kernel = np.ones(kernel_size) / kernel_size
    smoothed = np.convolve(a_db, kernel, mode='same')
    peak_idx = np.argmax(smoothed)
    peak_freq = a_freqs[peak_idx]

    # Spectral tilt: regression slope of dB spectrum vs frequency
    # Negative = falling spectrum, positive = rising
    if len(a_freqs) > 2:
        coeffs = np.polyfit(a_freqs / 1000.0, a_db, 1)
        tilt = coeffs[0]  # dB per kHz
    else:
        tilt = 0

    # Total energy (RMS)
    energy = np.sqrt(np.mean(burst ** 2))

    return {
        'centroid': centroid,
        'peak_freq': peak_freq,
        'spectral_tilt': tilt,
        'energy': energy,
    }


def measure_fricative_spectrum(samples, sample_rate=SAMPLE_RATE, highpass_hz=0):
    """Measure spectral properties of a fricative (steady-state).

    Returns dict with: centroid, peak_freq, peak_prominence, spectral_flatness
    """
    samples = np.asarray(samples, dtype=np.float64)
    if len(samples) < 200:
        return None

    # Take middle 50%
    n = len(samples)
    quarter = n // 4
    middle = samples[quarter:n - quarter]
    if len(middle) < 200:
        return None

    max_val = np.max(np.abs(middle))
    if max_val < 1:
        return None
    middle = middle / max_val

    windowed = middle * hamming(len(middle))
    spectrum = np.abs(np.fft.rfft(windowed))
    freqs = np.fft.rfftfreq(len(windowed), 1.0 / sample_rate)

    if highpass_hz > 0:
        spectrum = spectrum * (freqs >= highpass_hz)

    spectrum_db = 20 * np.log10(np.maximum(spectrum, 1e-10))

    mask = freqs >= 500
    if not np.any(mask):
        return None

    a_freqs = freqs[mask]
    a_spec = spectrum[mask]
    a_db = spectrum_db[mask]

    total_energy = np.sum(a_spec)
    if total_energy <= 0:
        return None
    centroid = np.sum(a_freqs * a_spec) / total_energy

    # Smoothed peak
    kernel_size = max(5, len(a_db) // 50)
    kernel = np.ones(kernel_size) / kernel_size
    smoothed = np.convolve(a_db, kernel, mode='same')
    peak_idx = np.argmax(smoothed)
    peak_freq = a_freqs[peak_idx]
    peak_db = smoothed[peak_idx]
    median_db = np.median(smoothed)
    peak_prominence = peak_db - median_db

    # Spectral flatness
    positive = a_spec[a_spec > 0]
    if len(positive) > 0:
        log_mean = np.mean(np.log(positive))
        geo_mean = np.exp(log_mean)
        arith_mean = np.mean(positive)
        flatness = geo_mean / arith_mean if arith_mean > 0 else 0
    else:
        flatness = 0

    return {
        'centroid': centroid,
        'peak_freq': peak_freq,
        'peak_prominence': peak_prominence,
        'spectral_flatness': flatness,
    }


def measure_nasal_spectrum(samples, sample_rate=SAMPLE_RATE):
    """Measure spectral properties of a nasal for place differentiation.

    Key measurements:
    - Spectral centroid: center of gravity in 400-4000 Hz (shifts with place)
    - Band energy ratios: mid/low and high/mid (shift with zero and F2 placement)
    - Spectral slope: dB/kHz from 400-4000 Hz

    Returns dict with: centroid, mid_low_ratio, high_mid_ratio, spectral_slope
    """
    samples = np.asarray(samples, dtype=np.float64)
    if len(samples) < 200:
        return None

    # Take middle 40% — skip transitions on both sides
    n = len(samples)
    start = int(n * 0.3)
    end = int(n * 0.7)
    middle = samples[start:end]
    if len(middle) < 200:
        return None

    max_val = np.max(np.abs(middle))
    if max_val < 1:
        return None
    middle = middle / max_val

    windowed = middle * hamming(len(middle))
    spectrum = np.abs(np.fft.rfft(windowed))
    freqs = np.fft.rfftfreq(len(windowed), 1.0 / sample_rate)
    spectrum_db = 20 * np.log10(np.maximum(spectrum, 1e-10))

    # Spectral centroid in 400-4000 Hz (power-weighted)
    analysis_mask = (freqs >= 400) & (freqs <= 4000)
    if not np.any(analysis_mask):
        return None
    a_freqs = freqs[analysis_mask]
    a_power = spectrum[analysis_mask] ** 2
    total_power = np.sum(a_power)
    if total_power <= 0:
        return None
    centroid = np.sum(a_freqs * a_power) / total_power

    # Band energy ratios (raw spectrum power)
    low_mask = (freqs >= 200) & (freqs < 800)
    mid_mask = (freqs >= 800) & (freqs < 2000)
    high_mask = (freqs >= 2000) & (freqs <= 4000)

    low_energy = np.sum(spectrum[low_mask] ** 2) if np.any(low_mask) else 0
    mid_energy = np.sum(spectrum[mid_mask] ** 2) if np.any(mid_mask) else 0
    high_energy = np.sum(spectrum[high_mask] ** 2) if np.any(high_mask) else 0

    mid_low_ratio = mid_energy / low_energy if low_energy > 0 else 0
    high_mid_ratio = high_energy / mid_energy if mid_energy > 0 else 0

    # Spectral slope: smooth to reduce harmonic noise, then linear regression
    kernel_size = max(5, len(spectrum_db) // 80)
    kernel = np.ones(kernel_size) / kernel_size
    smoothed = np.convolve(spectrum_db, kernel, mode='same')
    slope_db = smoothed[analysis_mask]
    if len(a_freqs) > 2:
        slope_coeffs = np.polyfit(a_freqs / 1000.0, slope_db, 1)
        spectral_slope = slope_coeffs[0]  # dB per kHz
    else:
        spectral_slope = 0

    return {
        'centroid': centroid,
        'mid_low_ratio': mid_low_ratio,
        'high_mid_ratio': high_mid_ratio,
        'spectral_slope': spectral_slope,
    }


# ── Pairwise differentiation scoring ─────────────────────────────────

def differentiation_score(profiles, key):
    """Compute pairwise differentiation score for a group of profiles.

    Score = average absolute difference in the given key between all pairs.
    Higher = better differentiation.
    """
    values = []
    for p in profiles:
        if p is not None and key in p:
            values.append(p[key])

    if len(values) < 2:
        return 0

    # Average pairwise absolute difference
    diffs = []
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            diffs.append(abs(values[i] - values[j]))
    return np.mean(diffs) if diffs else 0


# ── Diagnostic runners ────────────────────────────────────────────────

def diagnose_stops(save_wavs=False):
    """Measure stop burst spectra and report differentiation."""
    print("\n" + "=" * 80)
    print("  STOP BURST ANALYSIS")
    print("=" * 80)

    header = (f"{'Stop':>5} | {'Centroid':>8} | {'Peak':>6} | {'Tilt':>7} | "
              f"{'Energy':>6} | {'Place'}")
    print(header)
    print("-" * 65)

    all_profiles = {}
    all_samples_by_group = {}

    for group in STOP_PAIRS:
        group_samples = []
        for char in group:
            if char not in phoneme_data:
                continue
            all_samp, c_samp, v_samp = synthesize_cv(char, 'a')
            profile = measure_burst_spectrum(c_samp)
            all_profiles[char] = profile

            if save_wavs:
                group_samples.extend(all_samp)
                # Small gap between syllables
                group_samples.extend([0] * int(SAMPLE_RATE * 0.15))

            if profile:
                place = phoneme_data[char].get('cf2', 0)
                tilt_str = f"{profile['spectral_tilt']:+.1f}"
                print(f"  /{char:>2}/ | {profile['centroid']:>7.0f} | "
                      f"{profile['peak_freq']:>5.0f} | {tilt_str:>7} | "
                      f"{profile['energy']:>5.3f} | cf2={place}")
            else:
                print(f"  /{char:>2}/ | {'N/A':>8} | {'N/A':>6} | {'N/A':>7} | {'N/A':>6} |")

        if save_wavs and group_samples:
            voicing = 'voiceless' if not phoneme_data[group[0]].get('_isVoiced') else 'voiced'
            _save_wav(f'diag_stops_{voicing}.wav', group_samples)
            all_samples_by_group[voicing] = group_samples

    # Pairwise differentiation
    print("\n  Pairwise differentiation (centroid Hz | tilt dB/kHz):")
    for group in STOP_PAIRS:
        profiles = [all_profiles.get(c) for c in group]
        cent_score = differentiation_score(profiles, 'centroid')
        tilt_score = differentiation_score(profiles, 'spectral_tilt')
        chars = ','.join(group)
        print(f"    ({chars}): centroid={cent_score:.0f} Hz, tilt={tilt_score:.1f} dB/kHz")

    return all_profiles


def diagnose_fricatives(save_wavs=False):
    """Measure fricative spectra and report differentiation."""
    print("\n" + "=" * 80)
    print("  FRICATIVE SPECTRAL ANALYSIS")
    print("=" * 80)

    header = (f"{'Fric':>5} | {'Centroid':>8} | {'Peak':>6} | {'Prom':>5} | "
              f"{'Flat':>5} | {'nfFreq':>6} | {'nfBw':>6}")
    print(header)
    print("-" * 65)

    all_profiles = {}
    all_chars = []
    for pair in FRICATIVE_PAIRS:
        all_chars.extend(pair)

    group_samples = []
    for char in all_chars:
        if char not in phoneme_data:
            continue

        is_voiced = phoneme_data[char].get('_isVoiced', False)
        highpass = 500 if is_voiced else 0

        all_samp, c_samp, v_samp = synthesize_cv(char, 'a')
        profile = measure_fricative_spectrum(c_samp, highpass_hz=highpass)
        all_profiles[char] = profile

        if save_wavs:
            group_samples.extend(all_samp)
            group_samples.extend([0] * int(SAMPLE_RATE * 0.15))

        nf_freq = phoneme_data[char].get('noiseFilterFreq', 0)
        nf_bw = phoneme_data[char].get('noiseFilterBw', 0)

        if profile:
            print(f"  /{char:>2}/ | {profile['centroid']:>7.0f} | "
                  f"{profile['peak_freq']:>5.0f} | {profile['peak_prominence']:>4.1f} | "
                  f"{profile['spectral_flatness']:>4.3f} | {nf_freq:>5} | {nf_bw:>5}")
        else:
            print(f"  /{char:>2}/ | {'N/A':>8} | {'N/A':>6} | {'N/A':>5} | "
                  f"{'N/A':>5} | {nf_freq:>5} | {nf_bw:>5}")

    if save_wavs and group_samples:
        _save_wav('diag_fricatives.wav', group_samples)

    # Pairwise differentiation
    print("\n  Pairwise differentiation (centroid Hz):")
    for pair in FRICATIVE_PAIRS:
        profiles = [all_profiles.get(c) for c in pair]
        cent_score = differentiation_score(profiles, 'centroid')
        prom_score = differentiation_score(profiles, 'peak_prominence')
        chars = ','.join(pair)
        print(f"    ({chars}): centroid={cent_score:.0f} Hz, prominence={prom_score:.1f} dB")

    return all_profiles


def diagnose_nasals(save_wavs=False):
    """Measure nasal spectra in VCV context and report differentiation."""
    print("\n" + "=" * 80)
    print("  NASAL SPECTRAL ANALYSIS (VCV context)")
    print("=" * 80)

    header = (f"{'Nasal':>5} | {'Centroid':>8} | {'Mid/Low':>7} | "
              f"{'High/Mid':>8} | {'Slope':>7} | {'cfN0':>5} | {'cf2':>5}")
    print(header)
    print("-" * 70)

    all_profiles = {}
    all_chars = []
    for group in NASAL_PAIRS:
        all_chars.extend(group)

    group_samples = []
    for char in all_chars:
        if char not in phoneme_data:
            continue

        all_samp, c_samp = synthesize_vcv(char, 'a')
        profile = measure_nasal_spectrum(c_samp)
        all_profiles[char] = profile

        if save_wavs:
            group_samples.extend(all_samp)
            group_samples.extend([0] * int(SAMPLE_RATE * 0.15))

        cfN0 = phoneme_data[char].get('cfN0', 0)
        cf2 = phoneme_data[char].get('cf2', 0)

        if profile:
            slope_str = f"{profile['spectral_slope']:+.1f}"
            print(f"  /{char:>2}/ | {profile['centroid']:>7.0f} | "
                  f"{profile['mid_low_ratio']:>6.4f} | "
                  f"{profile['high_mid_ratio']:>7.4f} | "
                  f"{slope_str:>7} | {cfN0:>5} | {cf2:>5}")
        else:
            print(f"  /{char:>2}/ | {'N/A':>8} | {'N/A':>7} | "
                  f"{'N/A':>8} | {'N/A':>7} | {cfN0:>5} | {cf2:>5}")

    if save_wavs and group_samples:
        _save_wav('diag_nasals.wav', group_samples)

    # Pairwise differentiation
    print("\n  Pairwise differentiation:")
    for group in NASAL_PAIRS:
        profiles = [all_profiles.get(c) for c in group]
        cent_score = differentiation_score(profiles, 'centroid')
        mid_low_score = differentiation_score(profiles, 'mid_low_ratio')
        high_mid_score = differentiation_score(profiles, 'high_mid_ratio')
        chars = ','.join(group)
        print(f"    ({chars}): centroid={cent_score:.0f} Hz, "
              f"mid/low={mid_low_score:.4f}, high/mid={high_mid_score:.4f}")

    return all_profiles


# ── Main ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Consonant differentiation diagnostic tool')
    parser.add_argument('--category', '-c', type=str, default=None,
                        choices=['stops', 'fricatives', 'nasals'],
                        help='Analyze only one category')
    parser.add_argument('--wav', action='store_true',
                        help='Save WAV files for listening')
    args = parser.parse_args()

    print("Consonant Differentiation Diagnostic")
    print(f"Sample rate: {SAMPLE_RATE} Hz")

    if args.category is None or args.category == 'stops':
        diagnose_stops(save_wavs=args.wav)

    if args.category is None or args.category == 'fricatives':
        diagnose_fricatives(save_wavs=args.wav)

    if args.category is None or args.category == 'nasals':
        diagnose_nasals(save_wavs=args.wav)

    print("\n" + "=" * 80)
    print("  DONE")
    print("=" * 80)


if __name__ == '__main__':
    main()
