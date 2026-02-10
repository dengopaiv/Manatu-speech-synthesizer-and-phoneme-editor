# -*- coding: utf-8 -*-
"""
Fricative Brightness Auto-Tuner: Measurement-driven spectral shaping.

Synthesizes each fricative, measures FFT-based spectral profile (centroid,
peak frequency, peak prominence, spectral flatness), compares to targets,
and iteratively adjusts noise filter and parallel resonator parameters.

Usage:
    python tools/fricative_autotuner.py              # Full auto-tune with report
    python tools/fricative_autotuner.py --diagnose   # Diagnostic only (no changes)
    python tools/fricative_autotuner.py --fricative s # Tune single fricative
    python tools/fricative_autotuner.py --verbose    # Show per-iteration details
"""

import os
import sys
import io
import argparse
import copy

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

# ── Fricative classification ────────────────────────────────────────

FRICATIVE_CLASS = {
    # Sibilants
    's': 'sibilant',
    'z': 'sibilant',
    'ʃ': 'sibilant',
    'ʒ': 'sibilant',
    # Non-sibilants
    'f': 'non-sibilant',
    'v': 'non-sibilant',
    'θ': 'non-sibilant',
    'ð': 'non-sibilant',
    # Retroflex
    'ʂ': 'retroflex',
    'ʐ': 'retroflex',
    # Skip (aspiration-based or approximant-like)
    'h': 'skip',
    'ʍ': 'skip',
}

# Voicing pairs: voiceless → voiced
VOICING_PAIRS = {
    's': 'z',
    'ʃ': 'ʒ',
    'f': 'v',
    'θ': 'ð',
    'ʂ': 'ʐ',
}

# ── Target spectral profiles ────────────────────────────────────────

# Each target: (centroid_min, centroid_max, peak_min, peak_max, prominence_min, prominence_max)
# prominence_min/max: dB above spectral median
SPECTRAL_TARGETS = {
    's':  {'centroid': (5000, 7000), 'peak': (5000, 8000), 'prominence': (8, None)},
    'ʃ':  {'centroid': (3500, 4500), 'peak': (3000, 5000), 'prominence': (6, None)},
    'f':  {'centroid': (4000, 6000), 'peak': None,          'prominence': (None, 30)},
    'θ':  {'centroid': (4000, 6000), 'peak': None,          'prominence': (None, 30)},
    'ʂ':  {'centroid': (3000, 4000), 'peak': (3000, 4000), 'prominence': (4, None)},
}

# Voiced counterparts share same targets as voiceless
for voiceless, voiced in VOICING_PAIRS.items():
    if voiceless in SPECTRAL_TARGETS:
        SPECTRAL_TARGETS[voiced] = SPECTRAL_TARGETS[voiceless]

# ── Parameter constraints ────────────────────────────────────────────

CONSTRAINTS = {
    'sibilant': {
        'noiseFilterFreq': (2500, 7000),
        'noiseFilterBw': (800, 3000),
        'pa_range': (0.0, 1.0),
        'parallelBypass': (0, 0),  # Sibilants always use resonators
    },
    'non-sibilant': {
        'noiseFilterFreq': (0, 6000),  # Can set freq to shape centroid if needed
        'noiseFilterBw': (1000, 8000),
        'pa_range': (0.0, 1.0),
        'parallelBypass': (0.6, 1.0),
    },
    'retroflex': {
        'noiseFilterFreq': (2500, 5000),
        'noiseFilterBw': (800, 2500),
        'pa_range': (0.0, 1.0),
        'parallelBypass': (0.3, 0.7),
    },
}


# ── Spectral measurement (FFT-based) ────────────────────────────────

def measure_spectral_profile(samples, sample_rate=SAMPLE_RATE, highpass_hz=0):
    """Measure FFT-based spectral profile for noise-like signals.

    Args:
        samples: Audio samples (int16 or float)
        sample_rate: Sample rate in Hz
        highpass_hz: High-pass cutoff to exclude voicing energy (for voiced fricatives)

    Returns:
        dict with: centroid, peak_freq, peak_prominence, spectral_flatness
        or None on failure.
    """
    samples = np.asarray(samples, dtype=np.float64)

    if len(samples) < 200:
        return None

    # Take middle 50% to skip onset/offset transients
    n = len(samples)
    quarter = n // 4
    middle = samples[quarter:n - quarter]

    if len(middle) < 200:
        return None

    # Normalize
    max_val = np.max(np.abs(middle))
    if max_val < 1:
        return None
    middle = middle / max_val

    # Windowed FFT
    windowed = middle * hamming(len(middle))
    spectrum = np.abs(np.fft.rfft(windowed))
    freqs = np.fft.rfftfreq(len(windowed), 1.0 / sample_rate)

    # Apply high-pass if requested (for voiced fricatives)
    if highpass_hz > 0:
        hp_mask = freqs >= highpass_hz
        spectrum = spectrum * hp_mask

    # Convert to dB (with floor)
    spectrum_db = 20 * np.log10(np.maximum(spectrum, 1e-10))

    # Only consider frequencies above 500 Hz (skip voicing fundamentals)
    analysis_mask = freqs >= 500
    if not np.any(analysis_mask):
        return None

    analysis_freqs = freqs[analysis_mask]
    analysis_spectrum = spectrum[analysis_mask]
    analysis_db = spectrum_db[analysis_mask]

    # 1. Spectral centroid (weighted by linear magnitude)
    total_energy = np.sum(analysis_spectrum)
    if total_energy <= 0:
        return None
    centroid = np.sum(analysis_freqs * analysis_spectrum) / total_energy

    # 2. Smoothed peak: smooth spectrum then find max
    # Use a moving average to find the broad peak region
    kernel_size = max(5, len(analysis_db) // 50)
    kernel = np.ones(kernel_size) / kernel_size
    smoothed_db = np.convolve(analysis_db, kernel, mode='same')

    peak_idx = np.argmax(smoothed_db)
    peak_freq = analysis_freqs[peak_idx]
    peak_db = smoothed_db[peak_idx]

    # 3. Peak prominence: peak dB above median of smoothed spectrum
    median_db = np.median(smoothed_db)
    peak_prominence = peak_db - median_db

    # 4. Spectral flatness (Wiener entropy): geometric mean / arithmetic mean
    # High flatness = noise-like (white noise = 1.0), low = tonal
    positive_spectrum = analysis_spectrum[analysis_spectrum > 0]
    if len(positive_spectrum) > 0:
        log_mean = np.mean(np.log(positive_spectrum))
        geo_mean = np.exp(log_mean)
        arith_mean = np.mean(positive_spectrum)
        spectral_flatness = geo_mean / arith_mean if arith_mean > 0 else 0
    else:
        spectral_flatness = 0

    return {
        'centroid': centroid,
        'peak_freq': peak_freq,
        'peak_prominence': peak_prominence,
        'spectral_flatness': spectral_flatness,
    }


# ── Synthesis ────────────────────────────────────────────────────────

def synthesize_fricative(ipa_char, duration_ms=400, phoneme_override=None):
    """Synthesize a fricative, optionally with overridden phoneme data.

    Args:
        ipa_char: IPA character
        duration_ms: Duration in ms
        phoneme_override: If provided, use this dict instead of phoneme_data[ipa_char]

    Returns:
        List of int16 sample values.
    """
    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)
    frame = speechPlayer.Frame()

    if phoneme_override is not None:
        ipa.applyPhonemeToFrame(frame, phoneme_override)
    else:
        ipa.applyPhonemeToFrame(frame, phoneme_data[ipa_char])

    frame.preFormantGain = 1.0
    frame.outputGain = 2.0

    # For voiced fricatives, set pitch
    if phoneme_data.get(ipa_char, {}).get('_isVoiced', False):
        frame.voicePitch = 120
        frame.endVoicePitch = 120

    sp.queueFrame(frame, duration_ms, 50)

    samples = []
    while True:
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        samples.extend(chunk[i] for i in range(len(chunk)))
    return samples


# ── Per-class auto-tuners ────────────────────────────────────────────

def autotune_sibilant(ipa_char, fric_data, targets, verbose=False):
    """Auto-tune a sibilant fricative (/s/, /z/, /ʃ/, /ʒ/).

    Strategy: Adjust noiseFilterFreq to shift centroid toward target midpoint.
    Adjust dominant pa slot to control peak frequency.
    """
    constraints = CONSTRAINTS['sibilant']
    is_voiced = fric_data.get('_isVoiced', False)
    highpass = 500 if is_voiced else 0

    centroid_target = targets['centroid']
    centroid_mid = (centroid_target[0] + centroid_target[1]) / 2

    # Working copy of adjustable params
    nf_freq = fric_data.get('noiseFilterFreq', 4000)
    nf_bw = fric_data.get('noiseFilterBw', 1500)
    pa1 = fric_data.get('pa1', 0)
    pa2 = fric_data.get('pa2', 0)
    pa3 = fric_data.get('pa3', 0)
    pa4 = fric_data.get('pa4', 0)
    pa5 = fric_data.get('pa5', 0)
    pa6 = fric_data.get('pa6', 0)
    pb = fric_data.get('parallelBypass', 0)

    for iteration in range(8):
        trial = copy.deepcopy(fric_data)
        trial['noiseFilterFreq'] = nf_freq
        trial['noiseFilterBw'] = nf_bw
        trial['pa1'] = pa1
        trial['pa2'] = pa2
        trial['pa3'] = pa3
        trial['pa4'] = pa4
        trial['pa5'] = pa5
        trial['pa6'] = pa6
        trial['parallelBypass'] = pb

        samples = synthesize_fricative(ipa_char, phoneme_override=trial)
        profile = measure_spectral_profile(samples, highpass_hz=highpass)
        if profile is None:
            break

        centroid = profile['centroid']
        peak_freq = profile['peak_freq']
        prominence = profile['peak_prominence']

        if verbose:
            print(f"  iter {iteration}: centroid={centroid:.0f} Hz "
                  f"(target {centroid_target[0]}-{centroid_target[1]}), "
                  f"peak={peak_freq:.0f} Hz, prom={prominence:.1f} dB, "
                  f"nfFreq={nf_freq:.0f}, nfBw={nf_bw:.0f}")

        # Check if centroid is within target range
        in_range = centroid_target[0] <= centroid <= centroid_target[1]

        # Check prominence meets minimum
        prom_ok = True
        if targets['prominence'][0] is not None:
            prom_ok = prominence >= targets['prominence'][0]

        if in_range and prom_ok:
            break

        # Adjust noiseFilterFreq to shift centroid (30% correction)
        centroid_error = centroid_mid - centroid
        nf_freq_adj = centroid_error * 0.30
        nf_freq = np.clip(nf_freq + nf_freq_adj,
                          constraints['noiseFilterFreq'][0],
                          constraints['noiseFilterFreq'][1])

        # If prominence is too low, narrow the bandwidth
        if targets['prominence'][0] is not None and prominence < targets['prominence'][0]:
            prom_deficit = targets['prominence'][0] - prominence
            bw_adj = -prom_deficit * 30  # Narrow by 30 Hz per dB deficit
            nf_bw = np.clip(nf_bw + bw_adj,
                            constraints['noiseFilterBw'][0],
                            constraints['noiseFilterBw'][1])

    return {
        'noiseFilterFreq': round(float(nf_freq)),
        'noiseFilterBw': round(float(nf_bw)),
        'pa1': round(pa1, 3),
        'pa2': round(pa2, 3),
        'pa3': round(pa3, 3),
        'pa4': round(pa4, 3),
        'pa5': round(pa5, 3),
        'pa6': round(pa6, 3),
        'parallelBypass': round(float(pb), 3),
        'iterations': iteration + 1,
    }


def autotune_non_sibilant(ipa_char, fric_data, targets, verbose=False):
    """Auto-tune a non-sibilant fricative (/f/, /v/, /θ/, /ð/).

    Strategy: Adjust noiseFilterFreq to control centroid (freq < 100 → pink noise,
    which is too bright). Adjust noiseFilterBw for fine centroid tuning.
    Verify parallelBypass keeps spectrum flat (prominence ≤ target).
    """
    constraints = CONSTRAINTS['non-sibilant']
    is_voiced = fric_data.get('_isVoiced', False)
    highpass = 500 if is_voiced else 0

    centroid_target = targets['centroid']
    centroid_mid = (centroid_target[0] + centroid_target[1]) / 2

    nf_freq = fric_data.get('noiseFilterFreq', 0)
    nf_bw = fric_data.get('noiseFilterBw', 5000)
    pa1 = fric_data.get('pa1', 0)
    pa2 = fric_data.get('pa2', 0)
    pa3 = fric_data.get('pa3', 0)
    pa4 = fric_data.get('pa4', 0)
    pa5 = fric_data.get('pa5', 0)
    pa6 = fric_data.get('pa6', 0)
    pb = fric_data.get('parallelBypass', 0.8)

    for iteration in range(8):
        trial = copy.deepcopy(fric_data)
        trial['noiseFilterFreq'] = nf_freq
        trial['noiseFilterBw'] = nf_bw
        trial['pa1'] = pa1
        trial['pa2'] = pa2
        trial['pa3'] = pa3
        trial['pa4'] = pa4
        trial['pa5'] = pa5
        trial['pa6'] = pa6
        trial['parallelBypass'] = pb

        samples = synthesize_fricative(ipa_char, phoneme_override=trial)
        profile = measure_spectral_profile(samples, highpass_hz=highpass)
        if profile is None:
            break

        centroid = profile['centroid']
        prominence = profile['peak_prominence']

        if verbose:
            print(f"  iter {iteration}: centroid={centroid:.0f} Hz "
                  f"(target {centroid_target[0]}-{centroid_target[1]}), "
                  f"prom={prominence:.1f} dB, "
                  f"nfFreq={nf_freq:.0f}, nfBw={nf_bw:.0f}, pb={pb:.2f}")

        # Check centroid
        centroid_ok = centroid_target[0] <= centroid <= centroid_target[1]

        # Check prominence is below max (non-sibilants should be relatively flat)
        prom_ok = True
        if targets['prominence'][1] is not None:
            prom_ok = prominence <= targets['prominence'][1]

        if centroid_ok and prom_ok:
            break

        if not centroid_ok:
            centroid_error = centroid_mid - centroid

            # If noiseFilterFreq < 100 (pink noise mode) and centroid too high,
            # switch to bandpass filtered noise centered at target
            if nf_freq < 100 and centroid > centroid_target[1]:
                nf_freq = centroid_mid
                nf_bw = 4000  # Start with wide bandwidth for diffuse character
            else:
                # Adjust noiseFilterFreq to shift centroid (30% correction)
                nf_freq_adj = centroid_error * 0.30
                nf_freq = np.clip(nf_freq + nf_freq_adj,
                                  constraints['noiseFilterFreq'][0],
                                  constraints['noiseFilterFreq'][1])

                # Also adjust bandwidth: wider = more diffuse
                if centroid > centroid_target[1]:
                    # Centroid too high — narrow BW to cut HF
                    nf_bw = max(nf_bw * 0.85, constraints['noiseFilterBw'][0])
                elif centroid < centroid_target[0]:
                    # Centroid too low — widen BW to let in more HF
                    nf_bw = min(nf_bw * 1.15, constraints['noiseFilterBw'][1])

        # If prominence too high, increase parallelBypass (more raw = flatter)
        if not prom_ok and targets['prominence'][1] is not None:
            pb = min(pb + 0.05, constraints['parallelBypass'][1])

    return {
        'noiseFilterFreq': round(float(nf_freq)),
        'noiseFilterBw': round(float(nf_bw)),
        'pa1': round(pa1, 3),
        'pa2': round(pa2, 3),
        'pa3': round(pa3, 3),
        'pa4': round(pa4, 3),
        'pa5': round(pa5, 3),
        'pa6': round(pa6, 3),
        'parallelBypass': round(float(pb), 3),
        'iterations': iteration + 1,
    }


def autotune_retroflex(ipa_char, fric_data, targets, verbose=False):
    """Auto-tune a retroflex fricative (/ʂ/, /ʐ/).

    Strategy: Shift pa2-pa6 weight distribution and parallelBypass
    to control centroid/peak.
    """
    constraints = CONSTRAINTS['retroflex']
    is_voiced = fric_data.get('_isVoiced', False)
    highpass = 500 if is_voiced else 0

    centroid_target = targets['centroid']
    centroid_mid = (centroid_target[0] + centroid_target[1]) / 2

    nf_freq = fric_data.get('noiseFilterFreq', 3500)
    nf_bw = fric_data.get('noiseFilterBw', 1500)
    pa1 = fric_data.get('pa1', 0)
    pa2 = fric_data.get('pa2', 0)
    pa3 = fric_data.get('pa3', 0)
    pa4 = fric_data.get('pa4', 0)
    pa5 = fric_data.get('pa5', 0)
    pa6 = fric_data.get('pa6', 0)
    pb = fric_data.get('parallelBypass', 0.5)

    for iteration in range(6):
        trial = copy.deepcopy(fric_data)
        trial['noiseFilterFreq'] = nf_freq
        trial['noiseFilterBw'] = nf_bw
        trial['pa1'] = pa1
        trial['pa2'] = pa2
        trial['pa3'] = pa3
        trial['pa4'] = pa4
        trial['pa5'] = pa5
        trial['pa6'] = pa6
        trial['parallelBypass'] = pb

        samples = synthesize_fricative(ipa_char, phoneme_override=trial)
        profile = measure_spectral_profile(samples, highpass_hz=highpass)
        if profile is None:
            break

        centroid = profile['centroid']
        peak_freq = profile['peak_freq']
        prominence = profile['peak_prominence']

        if verbose:
            print(f"  iter {iteration}: centroid={centroid:.0f} Hz "
                  f"(target {centroid_target[0]}-{centroid_target[1]}), "
                  f"peak={peak_freq:.0f} Hz, prom={prominence:.1f} dB, "
                  f"nfFreq={nf_freq:.0f}, pb={pb:.2f}")

        centroid_ok = centroid_target[0] <= centroid <= centroid_target[1]

        prom_ok = True
        if targets['prominence'][0] is not None:
            prom_ok = prominence >= targets['prominence'][0]

        if centroid_ok and prom_ok:
            break

        # Adjust noiseFilterFreq to shift centroid (30% correction)
        centroid_error = centroid_mid - centroid
        nf_freq_adj = centroid_error * 0.30
        nf_freq = np.clip(nf_freq + nf_freq_adj,
                          constraints['noiseFilterFreq'][0],
                          constraints['noiseFilterFreq'][1])

        # Adjust parallelBypass to control prominence
        if targets['prominence'][0] is not None and prominence < targets['prominence'][0]:
            # Less bypass = more resonator shaping = higher prominence
            pb = max(pb - 0.05, constraints['parallelBypass'][0])
        elif prominence > 10:
            # Too prominent, add more bypass
            pb = min(pb + 0.03, constraints['parallelBypass'][1])

    return {
        'noiseFilterFreq': round(float(nf_freq)),
        'noiseFilterBw': round(float(nf_bw)),
        'pa1': round(pa1, 3),
        'pa2': round(pa2, 3),
        'pa3': round(pa3, 3),
        'pa4': round(pa4, 3),
        'pa5': round(pa5, 3),
        'pa6': round(pa6, 3),
        'parallelBypass': round(float(pb), 3),
        'iterations': iteration + 1,
    }


# ── Dispatcher ───────────────────────────────────────────────────────

def autotune_fricative(ipa_char, fric_data, verbose=False):
    """Auto-tune a single fricative, dispatching to class-specific tuner.

    Args:
        ipa_char: IPA character
        fric_data: Current phoneme dict (NOT modified)
        verbose: Print iteration details

    Returns:
        dict with tuned parameters and metadata, or None if skipped.
    """
    fclass = FRICATIVE_CLASS.get(ipa_char, 'skip')
    if fclass == 'skip':
        return None

    targets = SPECTRAL_TARGETS.get(ipa_char)
    if targets is None:
        return None

    is_voiced = fric_data.get('_isVoiced', False)
    highpass = 500 if is_voiced else 0

    # Measure initial state
    samples = synthesize_fricative(ipa_char)
    profile_before = measure_spectral_profile(samples, highpass_hz=highpass)
    if profile_before is None:
        return None

    # Store before values
    result = {
        'ipa': ipa_char,
        'class': fclass,
        'is_voiced': is_voiced,
        'centroid_before': profile_before['centroid'],
        'peak_freq_before': profile_before['peak_freq'],
        'prominence_before': profile_before['peak_prominence'],
        'flatness_before': profile_before['spectral_flatness'],
        # Original params
        'nf_freq_old': fric_data.get('noiseFilterFreq', 0),
        'nf_bw_old': fric_data.get('noiseFilterBw', 0),
        'pa6_old': fric_data.get('pa6', 0),
        'pb_old': fric_data.get('parallelBypass', 0),
    }

    # Dispatch to class-specific tuner
    if fclass == 'sibilant':
        tuned = autotune_sibilant(ipa_char, fric_data, targets, verbose)
    elif fclass == 'non-sibilant':
        tuned = autotune_non_sibilant(ipa_char, fric_data, targets, verbose)
    elif fclass == 'retroflex':
        tuned = autotune_retroflex(ipa_char, fric_data, targets, verbose)
    else:
        return None

    result['tuned'] = tuned

    # Measure final state
    trial = copy.deepcopy(fric_data)
    for k, v in tuned.items():
        if k != 'iterations':
            trial[k] = v
    samples = synthesize_fricative(ipa_char, phoneme_override=trial)
    profile_after = measure_spectral_profile(samples, highpass_hz=highpass)
    if profile_after:
        result['centroid_after'] = profile_after['centroid']
        result['peak_freq_after'] = profile_after['peak_freq']
        result['prominence_after'] = profile_after['peak_prominence']
        result['flatness_after'] = profile_after['spectral_flatness']
    else:
        result['centroid_after'] = result['centroid_before']
        result['peak_freq_after'] = result['peak_freq_before']
        result['prominence_after'] = result['prominence_before']
        result['flatness_after'] = result['flatness_before']

    result['iterations'] = tuned.get('iterations', 0)
    return result


# ── Voicing pair consistency ─────────────────────────────────────────

def enforce_voicing_pairs(results):
    """Copy spectral shape params from voiceless to voiced counterpart.

    Modifies results in-place. The voiced result's tuned params are
    overwritten with the voiceless result's tuned params (noise shaping only).
    """
    # Build lookup by IPA
    by_ipa = {r['ipa']: r for r in results}

    spectral_params = ['noiseFilterFreq', 'noiseFilterBw',
                       'pa1', 'pa2', 'pa3', 'pa4', 'pa5', 'pa6',
                       'parallelBypass']

    for voiceless, voiced in VOICING_PAIRS.items():
        if voiceless in by_ipa and voiced in by_ipa:
            vl_tuned = by_ipa[voiceless].get('tuned', {})
            vd_tuned = by_ipa[voiced].get('tuned', {})
            for param in spectral_params:
                if param in vl_tuned:
                    vd_tuned[param] = vl_tuned[param]
            by_ipa[voiced]['pair_synced'] = True


# ── Report ───────────────────────────────────────────────────────────

def get_all_fricatives():
    """Return list of (ipa_char, fric_data) for all tunable fricatives."""
    fricatives = []
    # Process voiceless first, then voiced (for pair consistency)
    voiceless_order = ['s', 'ʃ', 'f', 'θ', 'ʂ']
    voiced_order = ['z', 'ʒ', 'v', 'ð', 'ʐ']

    for ipa_char in voiceless_order + voiced_order:
        if ipa_char in phoneme_data and FRICATIVE_CLASS.get(ipa_char) != 'skip':
            fricatives.append((ipa_char, phoneme_data[ipa_char]))
    return fricatives


def autotune_all(verbose=False):
    """Run auto-tuning on all fricatives (voiceless first, then enforce pairs).

    Returns:
        List of result dicts from autotune_fricative().
    """
    fricatives = get_all_fricatives()
    results = []

    for ipa_char, fric_data in fricatives:
        if verbose:
            fclass = FRICATIVE_CLASS.get(ipa_char, '?')
            targets = SPECTRAL_TARGETS.get(ipa_char, {})
            print(f"\n{'='*60}")
            print(f"Auto-tuning /{ipa_char}/ ({fclass})")
            if 'centroid' in targets:
                print(f"  Target centroid: {targets['centroid'][0]}-{targets['centroid'][1]} Hz")

        result = autotune_fricative(ipa_char, fric_data, verbose=verbose)
        if result:
            results.append(result)
        elif verbose:
            print(f"  SKIPPED")

    enforce_voicing_pairs(results)
    return results


def print_report(results, diagnose_only=False):
    """Print a formatted before/after report table."""
    header = "DIAGNOSTIC REPORT" if diagnose_only else "AUTO-TUNE REPORT"
    print(f"\n{'='*110}")
    print(f"  FRICATIVE {header}")
    print(f"{'='*110}")

    if diagnose_only:
        print(f"{'Fric':>5} | {'Class':>11} | {'Centroid':>8} | {'Peak':>6} | {'Prom':>5} | "
              f"{'Flat':>5} | {'nfFreq':>6} | {'nfBw':>6} | {'pa6':>5} | {'pBP':>5} | {'Status'}")
        print(f"{'-'*5}-+-{'-'*11}-+-{'-'*8}-+-{'-'*6}-+-{'-'*5}-+-"
              f"{'-'*5}-+-{'-'*6}-+-{'-'*6}-+-{'-'*5}-+-{'-'*5}-+-{'-'*15}")
    else:
        print(f"{'Fric':>5} | {'Class':>11} | {'Cent_b':>7} | {'Cent_a':>7} | {'Prom_b':>6} | {'Prom_a':>6} | "
              f"{'nfFreq':>12} | {'nfBw':>12} | {'pBP':>10} | {'Notes'}")
        print(f"{'-'*5}-+-{'-'*11}-+-{'-'*7}-+-{'-'*7}-+-{'-'*6}-+-{'-'*6}-+-"
              f"{'-'*12}-+-{'-'*12}-+-{'-'*10}-+-{'-'*15}")

    for r in results:
        ipa_char = r['ipa']
        fclass = r['class']
        targets = SPECTRAL_TARGETS.get(ipa_char, {})

        if diagnose_only:
            # Check status
            notes = []
            ct = targets.get('centroid')
            if ct:
                c = r['centroid_before']
                if c < ct[0]:
                    notes.append('LOW')
                elif c > ct[1]:
                    notes.append('HIGH')
                else:
                    notes.append('OK')

            pt = targets.get('prominence', (None, None))
            p = r['prominence_before']
            if pt[0] is not None and p < pt[0]:
                notes.append('weak')
            elif pt[1] is not None and p > pt[1]:
                notes.append('sharp')

            print(f"  /{ipa_char:>2}/ | {fclass:>11} | {r['centroid_before']:>7.0f} | "
                  f"{r['peak_freq_before']:>5.0f} | {r['prominence_before']:>4.1f} | "
                  f"{r['flatness_before']:>4.3f} | {r['nf_freq_old']:>5} | {r['nf_bw_old']:>5} | "
                  f"{r['pa6_old']:>4.2f} | {r['pb_old']:>4.2f} | {', '.join(notes)}")
        else:
            tuned = r.get('tuned', {})
            nf_freq_new = tuned.get('noiseFilterFreq', r['nf_freq_old'])
            nf_bw_new = tuned.get('noiseFilterBw', r['nf_bw_old'])
            pb_new = tuned.get('parallelBypass', r['pb_old'])

            nf_freq_str = f"{r['nf_freq_old']}->{nf_freq_new}"
            nf_bw_str = f"{r['nf_bw_old']}->{nf_bw_new}"
            pb_str = f"{r['pb_old']:.2f}->{pb_new:.2f}"

            notes = []
            if r.get('pair_synced'):
                notes.append('SYNCED')
            if (nf_freq_new != r['nf_freq_old'] or
                    nf_bw_new != r['nf_bw_old'] or
                    pb_new != r['pb_old']):
                notes.append('CHANGED')

            print(f"  /{ipa_char:>2}/ | {fclass:>11} | {r['centroid_before']:>6.0f} | "
                  f"{r['centroid_after']:>6.0f} | {r['prominence_before']:>5.1f} | "
                  f"{r['prominence_after']:>5.1f} | "
                  f"{nf_freq_str:>12} | {nf_bw_str:>12} | {pb_str:>10} | "
                  f"{', '.join(notes)}")

    # Summary
    changed = sum(1 for r in results
                  if r.get('tuned', {}).get('noiseFilterFreq', r['nf_freq_old']) != r['nf_freq_old']
                  or r.get('tuned', {}).get('noiseFilterBw', r['nf_bw_old']) != r['nf_bw_old']
                  or r.get('tuned', {}).get('parallelBypass', r['pb_old']) != r['pb_old'])
    print(f"\n  Total fricatives: {len(results)}, Changed: {changed}")


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Fricative brightness auto-tuner for spectral shaping')
    parser.add_argument('--diagnose', action='store_true',
                        help='Diagnostic only — measure and report, no changes')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show per-iteration details')
    parser.add_argument('--fricative', '-f', type=str, default=None,
                        help='Tune a single fricative (IPA character)')
    args = parser.parse_args()

    if args.diagnose:
        print("Running diagnostic measurement (no changes)...")
        fricatives = get_all_fricatives()
        results = []

        for ipa_char, fric_data in fricatives:
            if args.fricative and ipa_char != args.fricative:
                continue

            fclass = FRICATIVE_CLASS.get(ipa_char, 'skip')
            is_voiced = fric_data.get('_isVoiced', False)
            highpass = 500 if is_voiced else 0

            samples = synthesize_fricative(ipa_char)
            profile = measure_spectral_profile(samples, highpass_hz=highpass)
            if profile is None:
                continue

            results.append({
                'ipa': ipa_char,
                'class': fclass,
                'is_voiced': is_voiced,
                'centroid_before': profile['centroid'],
                'peak_freq_before': profile['peak_freq'],
                'prominence_before': profile['peak_prominence'],
                'flatness_before': profile['spectral_flatness'],
                'nf_freq_old': fric_data.get('noiseFilterFreq', 0),
                'nf_bw_old': fric_data.get('noiseFilterBw', 0),
                'pa6_old': fric_data.get('pa6', 0),
                'pb_old': fric_data.get('parallelBypass', 0),
            })

        print_report(results, diagnose_only=True)
    else:
        print("Running fricative auto-tune...")
        if args.fricative:
            # Single fricative mode
            ipa_char = args.fricative
            if ipa_char not in phoneme_data:
                print(f"  ERROR: /{ipa_char}/ not found in phoneme data")
                return
            result = autotune_fricative(ipa_char, phoneme_data[ipa_char],
                                        verbose=args.verbose)
            results = [result] if result else []
        else:
            results = autotune_all(verbose=args.verbose)

        print_report(results, diagnose_only=False)

        # Print values ready for applying to data files
        print(f"\n{'='*60}")
        print("  VALUES TO APPLY")
        print(f"{'='*60}")
        for r in results:
            tuned = r.get('tuned', {})
            if not tuned:
                continue
            changed_params = []
            for param in ['noiseFilterFreq', 'noiseFilterBw', 'pa1', 'pa2', 'pa3',
                          'pa4', 'pa5', 'pa6', 'parallelBypass']:
                old_key = {
                    'noiseFilterFreq': 'nf_freq_old',
                    'noiseFilterBw': 'nf_bw_old',
                    'pa6': 'pa6_old',
                    'parallelBypass': 'pb_old',
                }.get(param)
                new_val = tuned.get(param)
                if new_val is not None:
                    changed_params.append(f"{param}={new_val}")
            if changed_params:
                print(f"  /{r['ipa']}/: {', '.join(changed_params)}")


if __name__ == '__main__':
    main()
