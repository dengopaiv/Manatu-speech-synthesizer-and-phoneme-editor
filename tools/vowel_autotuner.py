# -*- coding: utf-8 -*-
"""
Vowel Auto-Tuner: Measurement-driven F2/F3 parallel reinforcement.

Synthesizes each vowel, measures the LPC spectral envelope at known
formant frequencies, quantifies F2/F3 deficit relative to F1, and
iteratively adjusts pa2/pa3/parallelVoiceMix until deficits reach
target thresholds.

Usage:
    python tools/vowel_autotuner.py              # Full auto-tune with report
    python tools/vowel_autotuner.py --diagnose   # Diagnostic only (no changes)
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
from data import data as phoneme_data, PHONEME_CATEGORIES
from tools.spectral_analysis import _get_lpc_coefficients

SAMPLE_RATE = 44100

# ── Vowel height classification ──────────────────────────────────────

# Map each vowel IPA to its height class for target deficit lookup
VOWEL_HEIGHT = {}

# Close (high) vowels
for v in ['i', 'y', 'ɨ', 'ʉ', 'ɯ', 'u']:
    VOWEL_HEIGHT[v] = 'close'

# Near-close
for v in ['ɪ', 'ʏ', 'ʊ']:
    VOWEL_HEIGHT[v] = 'near-close'

# Close-mid (includes schwa as "mid")
for v in ['e', 'ø', 'ɘ', 'ɵ', 'ɤ', 'o', 'ə']:
    VOWEL_HEIGHT[v] = 'close-mid'

# Open-mid
for v in ['ɛ', 'œ', 'ɜ', 'ɞ', 'ʌ', 'ɔ']:
    VOWEL_HEIGHT[v] = 'open-mid'

# Near-open / Open
for v in ['æ', 'ɐ']:
    VOWEL_HEIGHT[v] = 'open'
for v in ['a', 'ɶ', 'ɑ', 'ɒ']:
    VOWEL_HEIGHT[v] = 'open'

# R-colored (treat as close-mid)
for v in ['ɝ', 'ɚ']:
    VOWEL_HEIGHT[v] = 'close-mid'

# Nasalized vowels
VOWEL_HEIGHT['ã'] = 'open'
VOWEL_HEIGHT['ɛ̃'] = 'open-mid'
VOWEL_HEIGHT['ɔ̃'] = 'open-mid'
VOWEL_HEIGHT['œ̃'] = 'open-mid'


# ── Target deficits (dB below F1 peak) ──────────────────────────────

TARGET_DEFICITS = {
    #                  F2 max deficit, F3 max deficit
    'close':          (8, 15),
    'near-close':     (10, 18),
    'close-mid':      (12, 20),
    'open-mid':       (15, 22),
    'open':           (18, 25),
}

# ── Caps ─────────────────────────────────────────────────────────────

PA2_MAX = 0.8
PA3_MAX = 0.6
PVM_MAX = 0.8
MAX_ITERATIONS = 8


# ── Core functions ───────────────────────────────────────────────────

def synthesize_vowel(ipa_char, duration_ms=400, pitch=120, phoneme_override=None):
    """Synthesize a vowel, optionally with overridden phoneme data.

    Args:
        ipa_char: IPA character
        duration_ms: Duration in ms
        pitch: F0 in Hz
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
    frame.voicePitch = pitch
    frame.endVoicePitch = pitch

    sp.queueFrame(frame, duration_ms, 50)
    # Collect samples
    samples = []
    while True:
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        samples.extend(chunk[i] for i in range(len(chunk)))
    return samples


def measure_formant_levels(samples, cf1, cf2, cf3, sample_rate=SAMPLE_RATE):
    """Measure the LPC spectral envelope level at known formant frequencies.

    Args:
        samples: Audio samples (int16 or float)
        cf1, cf2, cf3: Known formant center frequencies in Hz
        sample_rate: Sample rate

    Returns:
        (F1_dB, F2_dB, F3_dB) envelope levels at the formant frequencies,
        or None on failure.
    """
    samples = np.asarray(samples, dtype=np.float64)

    if len(samples) < 100:
        return None

    # Take middle 50% to skip onset/offset transients
    n = len(samples)
    quarter = n // 4
    middle = samples[quarter:n - quarter]

    if len(middle) < 100:
        return None

    poly, order = _get_lpc_coefficients(middle, sample_rate)
    if poly is None:
        return None

    # Evaluate LPC envelope at specific frequencies
    def envelope_at_freq(freq):
        w = np.exp(-1j * 2 * np.pi * freq / sample_rate)
        response = sum(coeff * (w ** k) for k, coeff in enumerate(poly))
        mag = abs(response)
        if mag < 1e-10:
            mag = 1e-10
        return -20 * np.log10(mag)  # H = 1/A, so negate

    f1_db = envelope_at_freq(cf1)
    f2_db = envelope_at_freq(cf2)
    f3_db = envelope_at_freq(cf3)

    return f1_db, f2_db, f3_db


def compute_target_deficit(ipa_char):
    """Get the target max F2 and F3 deficit for a vowel.

    Returns:
        (f2_target, f3_target) in dB, or None if vowel not classified.
    """
    height = VOWEL_HEIGHT.get(ipa_char)
    if height is None:
        return None
    return TARGET_DEFICITS[height]


def is_back_rounded_close_f1f2(vowel_data):
    """Check if F1 and F2 are close together (back rounded vowels).

    Returns True if F2-F1 gap <= 600 Hz, meaning all parallel reinforcement
    should be skipped to preserve natural back vowel spectrum.
    """
    cf1 = vowel_data.get('cf1', 0)
    cf2 = vowel_data.get('cf2', 0)
    return (cf2 - cf1) <= 600


def autotune_vowel(ipa_char, vowel_data, verbose=False):
    """Auto-tune pa2/pa3/parallelVoiceMix for a single vowel.

    Args:
        ipa_char: IPA character
        vowel_data: Current phoneme dict (will NOT be modified)
        verbose: Print iteration details

    Returns:
        dict with keys:
            'ipa': str
            'cf1', 'cf2', 'cf3': formant freqs
            'f1_db_before', 'f2_db_before', 'f3_db_before': initial levels
            'f2_deficit_before', 'f3_deficit_before': initial deficits
            'f1_db_after', 'f2_db_after', 'f3_db_after': final levels
            'f2_deficit_after', 'f3_deficit_after': final deficits
            'pa2_old', 'pa3_old', 'pvm_old': original values
            'pa2_new', 'pa3_new', 'pvm_new': tuned values
            'iterations': number of iterations used
            'skipped_f2': bool (True if back rounded F1-F2 close)
    """
    cf1 = vowel_data['cf1']
    cf2 = vowel_data['cf2']
    cf3 = vowel_data['cf3']

    pa2_old = vowel_data.get('pa2', 0)
    pa3_old = vowel_data.get('pa3', 0)
    pvm_old = vowel_data.get('parallelVoiceMix', 0)

    skip_f2 = is_back_rounded_close_f1f2(vowel_data)
    targets = compute_target_deficit(ipa_char)
    if targets is None:
        return None
    f2_target, f3_target = targets

    # Measure initial state
    samples = synthesize_vowel(ipa_char)
    levels = measure_formant_levels(samples, cf1, cf2, cf3)
    if levels is None:
        return None

    f1_db_init, f2_db_init, f3_db_init = levels
    f2_deficit_init = f1_db_init - f2_db_init
    f3_deficit_init = f1_db_init - f3_db_init

    result = {
        'ipa': ipa_char,
        'cf1': cf1, 'cf2': cf2, 'cf3': cf3,
        'f1_db_before': f1_db_init,
        'f2_db_before': f2_db_init,
        'f3_db_before': f3_db_init,
        'f2_deficit_before': f2_deficit_init,
        'f3_deficit_before': f3_deficit_init,
        'pa2_old': pa2_old,
        'pa3_old': pa3_old,
        'pvm_old': pvm_old,
        'skipped_f2': skip_f2,
    }

    # Back rounded vowels (close F1-F2) get no parallel reinforcement at all —
    # their naturally weak F3 is what makes them sound "back".
    if skip_f2:
        pa2 = 0
        pa3 = 0
        pvm = 0
        if verbose:
            print(f"  skip_f2=True (F2-F1 gap <= 600 Hz) — zeroing all parallel reinforcement")
    else:
        # Current working values
        pa2 = pa2_old
        pa3 = pa3_old
        pvm = pvm_old

    for iteration in range(MAX_ITERATIONS):
        if skip_f2:
            break  # Nothing to tune

        # Measure current deficit
        trial = copy.deepcopy(vowel_data)
        trial['pa2'] = pa2
        trial['pa3'] = pa3
        trial['parallelVoiceMix'] = pvm

        samples = synthesize_vowel(ipa_char, phoneme_override=trial)
        levels = measure_formant_levels(samples, cf1, cf2, cf3)
        if levels is None:
            break

        f1_db, f2_db, f3_db = levels
        f2_deficit = f1_db - f2_db
        f3_deficit = f1_db - f3_db

        if verbose:
            print(f"  iter {iteration}: F2_def={f2_deficit:.1f} dB (target {f2_target}), "
                  f"F3_def={f3_deficit:.1f} dB (target {f3_target}), "
                  f"pa2={pa2:.3f}, pa3={pa3:.3f}, pVM={pvm:.3f}")

        # Check if within targets
        f2_ok = (f2_deficit <= f2_target)
        f3_ok = (f3_deficit <= f3_target)

        if f2_ok and f3_ok:
            break

        # Adjust pa2 if F2 deficit is too high
        if f2_deficit > f2_target:
            excess = f2_deficit - f2_target
            # Proportional step: ~0.05 per 5 dB excess, min 0.02
            step = max(0.02, min(0.1, excess / 100))
            pa2 = min(pa2 + step, PA2_MAX)

        # Adjust pa3 if F3 deficit is too high
        if f3_deficit > f3_target:
            excess = f3_deficit - f3_target
            step = max(0.02, min(0.08, excess / 120))
            pa3 = min(pa3 + step, PA3_MAX)

        # Enforce pa2 >= pa3
        if pa2 < pa3:
            pa2 = pa3

        # pVM = max(pa2, pa3)
        pvm = min(max(pa2, pa3), PVM_MAX)

    # Final measurement
    trial = copy.deepcopy(vowel_data)
    trial['pa2'] = pa2
    trial['pa3'] = pa3
    trial['parallelVoiceMix'] = pvm
    samples = synthesize_vowel(ipa_char, phoneme_override=trial)
    levels = measure_formant_levels(samples, cf1, cf2, cf3)
    if levels:
        f1_db, f2_db, f3_db = levels
        result['f1_db_after'] = f1_db
        result['f2_db_after'] = f2_db
        result['f3_db_after'] = f3_db
        result['f2_deficit_after'] = f1_db - f2_db
        result['f3_deficit_after'] = f1_db - f3_db
    else:
        result['f2_deficit_after'] = result['f2_deficit_before']
        result['f3_deficit_after'] = result['f3_deficit_before']

    result['pa2_new'] = round(pa2, 3)
    result['pa3_new'] = round(pa3, 3)
    result['pvm_new'] = round(pvm, 3)
    result['iterations'] = iteration + 1 if 'iteration' in dir() else 0

    return result


def get_all_vowels():
    """Return list of (ipa_char, vowel_data, category_name) for all vowels."""
    vowels = []
    vowel_cats = [
        ('Vowels - Front', PHONEME_CATEGORIES.get('Vowels - Front', {})),
        ('Vowels - Central', PHONEME_CATEGORIES.get('Vowels - Central', {})),
        ('Vowels - Back', PHONEME_CATEGORIES.get('Vowels - Back', {})),
        ('Vowels - R-colored', PHONEME_CATEGORIES.get('Vowels - R-colored', {})),
        ('Vowels - Nasalized', PHONEME_CATEGORIES.get('Vowels - Nasalized', {})),
    ]
    for cat_name, cat_dict in vowel_cats:
        for ipa_char in sorted(cat_dict.keys()):
            if ipa_char in phoneme_data:
                vowels.append((ipa_char, phoneme_data[ipa_char], cat_name))
    return vowels


def autotune_all(verbose=False):
    """Run auto-tuning on all vowels.

    Returns:
        List of result dicts from autotune_vowel().
    """
    vowels = get_all_vowels()
    results = []

    for ipa_char, vowel_data, cat_name in vowels:
        if verbose:
            print(f"\n{'='*60}")
            print(f"Auto-tuning /{ipa_char}/ ({cat_name})")
            print(f"  cf1={vowel_data['cf1']}, cf2={vowel_data['cf2']}, cf3={vowel_data['cf3']}")
            height = VOWEL_HEIGHT.get(ipa_char, '?')
            targets = compute_target_deficit(ipa_char)
            if targets:
                print(f"  Height: {height}, Targets: F2<={targets[0]} dB, F3<={targets[1]} dB")

        result = autotune_vowel(ipa_char, vowel_data, verbose=verbose)
        if result:
            results.append(result)
        else:
            if verbose:
                print(f"  SKIPPED (no height classification or measurement failed)")

    return results


def print_report(results, diagnose_only=False):
    """Print a formatted before/after report table."""
    header = "DIAGNOSTIC REPORT" if diagnose_only else "AUTO-TUNE REPORT"
    print(f"\n{'='*100}")
    print(f"  {header}")
    print(f"{'='*100}")

    # Header row
    if diagnose_only:
        print(f"{'Vowel':>6} | {'F2def':>6} | {'F3def':>6} | {'F2tgt':>6} | {'F3tgt':>6} | "
              f"{'pa2':>6} | {'pa3':>6} | {'pVM':>6} | {'Notes'}")
        print(f"{'-'*6}-+-{'-'*6}-+-{'-'*6}-+-{'-'*6}-+-{'-'*6}-+-"
              f"{'-'*6}-+-{'-'*6}-+-{'-'*6}-+-{'-'*20}")
    else:
        print(f"{'Vowel':>6} | {'F2def_b':>7} | {'F2def_a':>7} | {'F3def_b':>7} | {'F3def_a':>7} | "
              f"{'pa2':>12} | {'pa3':>12} | {'pVM':>12} | {'Notes'}")
        print(f"{'-'*6}-+-{'-'*7}-+-{'-'*7}-+-{'-'*7}-+-{'-'*7}-+-"
              f"{'-'*12}-+-{'-'*12}-+-{'-'*12}-+-{'-'*15}")

    for r in results:
        ipa_char = r['ipa']
        targets = compute_target_deficit(ipa_char)
        f2_tgt, f3_tgt = targets if targets else (0, 0)

        notes = []
        if r.get('skipped_f2'):
            notes.append('skip_F2')
        if r.get('f2_deficit_before', 0) > f2_tgt and not r.get('skipped_f2'):
            notes.append('F2!')
        if r.get('f3_deficit_before', 0) > f3_tgt:
            notes.append('F3!')

        if diagnose_only:
            print(f"  /{ipa_char:>3}/ | {r['f2_deficit_before']:>5.1f} | {r['f3_deficit_before']:>5.1f} | "
                  f"{f2_tgt:>5.0f} | {f3_tgt:>5.0f} | "
                  f"{r['pa2_old']:>5.3f} | {r['pa3_old']:>5.3f} | {r['pvm_old']:>5.3f} | "
                  f"{', '.join(notes)}")
        else:
            pa2_str = f"{r['pa2_old']:.2f}->{r['pa2_new']:.2f}"
            pa3_str = f"{r['pa3_old']:.2f}->{r['pa3_new']:.2f}"
            pvm_str = f"{r['pvm_old']:.2f}->{r['pvm_new']:.2f}"
            changed = (r['pa2_new'] != r['pa2_old'] or
                       r['pa3_new'] != r['pa3_old'] or
                       r['pvm_new'] != r['pvm_old'])
            if changed:
                notes.append('CHANGED')

            f2_da = r.get('f2_deficit_after', r['f2_deficit_before'])
            f3_da = r.get('f3_deficit_after', r['f3_deficit_before'])
            print(f"  /{ipa_char:>3}/ | {r['f2_deficit_before']:>6.1f} | {f2_da:>6.1f} | "
                  f"{r['f3_deficit_before']:>6.1f} | {f3_da:>6.1f} | "
                  f"{pa2_str:>12} | {pa3_str:>12} | {pvm_str:>12} | "
                  f"{', '.join(notes)}")

    # Summary
    changed_count = sum(1 for r in results
                        if r.get('pa2_new') != r.get('pa2_old')
                        or r.get('pa3_new') != r.get('pa3_old')
                        or r.get('pvm_new') != r.get('pvm_old'))
    print(f"\n  Total vowels: {len(results)}, Changed: {changed_count}")


def main():
    parser = argparse.ArgumentParser(description='Vowel auto-tuner for F2/F3 parallel reinforcement')
    parser.add_argument('--diagnose', action='store_true',
                        help='Diagnostic only — measure and report, no changes')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show per-iteration details')
    args = parser.parse_args()

    if args.diagnose:
        print("Running diagnostic measurement (no changes)...")
        # For diagnostic, we just measure current state
        vowels = get_all_vowels()
        results = []
        for ipa_char, vowel_data, cat_name in vowels:
            cf1 = vowel_data['cf1']
            cf2 = vowel_data['cf2']
            cf3 = vowel_data['cf3']

            samples = synthesize_vowel(ipa_char)
            levels = measure_formant_levels(samples, cf1, cf2, cf3)
            if levels is None:
                continue

            f1_db, f2_db, f3_db = levels
            results.append({
                'ipa': ipa_char,
                'cf1': cf1, 'cf2': cf2, 'cf3': cf3,
                'f1_db_before': f1_db,
                'f2_db_before': f2_db,
                'f3_db_before': f3_db,
                'f2_deficit_before': f1_db - f2_db,
                'f3_deficit_before': f1_db - f3_db,
                'pa2_old': vowel_data.get('pa2', 0),
                'pa3_old': vowel_data.get('pa3', 0),
                'pvm_old': vowel_data.get('parallelVoiceMix', 0),
                'skipped_f2': is_back_rounded_close_f1f2(vowel_data),
            })

        print_report(results, diagnose_only=True)
    else:
        print("Running auto-tune...")
        results = autotune_all(verbose=args.verbose)
        print_report(results, diagnose_only=False)

        # Print values ready for applying to data files
        print(f"\n{'='*60}")
        print("  VALUES TO APPLY")
        print(f"{'='*60}")
        for r in results:
            if (r['pa2_new'] != r['pa2_old'] or
                    r['pa3_new'] != r['pa3_old'] or
                    r['pvm_new'] != r['pvm_old']):
                print(f"  /{r['ipa']}/: pa2={r['pa2_new']}, pa3={r['pa3_new']}, "
                      f"parallelVoiceMix={r['pvm_new']}")


if __name__ == '__main__':
    main()
