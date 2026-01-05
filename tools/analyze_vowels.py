#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Vowel Formant Analysis Tool

Analyzes synthesized vowels and compares against reference values.
Uses parselmouth (Praat Python bindings) for formant extraction.
Designed for accessible text-based output (screen reader friendly).

Install: pip install praat-parselmouth

Usage:
    python analyze_vowels.py --vowel a                    # Analyze vowel with default pitch
    python analyze_vowels.py --vowel ɑ --start-pitch 55 --end-pitch 15  # Falling pitch
    python analyze_vowels.py --wav test.wav               # Analyze existing wav file
    python analyze_vowels.py --all                        # Analyze all reference vowels
    python analyze_vowels.py --wav my.wav --extract-preset  # Extract preset parameters
    python analyze_vowels.py --wav diphthong.wav --trajectory  # Analyze diphthong trajectory
    python analyze_vowels.py --transition ø y             # Show parameter transition
    python analyze_vowels.py --transition ø y --play      # Play transition audio
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
    import numpy as np
    HAS_PARSELMOUTH = True
except ImportError:
    HAS_PARSELMOUTH = False
    print("Warning: parselmouth not installed. Install with: pip install praat-parselmouth")

import json

# For audio playback
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

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


def analyze_stability(wav_path, max_formant_hz=5500):
    """
    Analyze formant stability and voice quality over time.

    Returns metrics for:
    - Formant drift (variation over time)
    - HNR (harmonics-to-noise ratio, indicates distortion)
    - Pitch range
    """
    if not HAS_PARSELMOUTH:
        return None

    sound = parselmouth.Sound(wav_path)
    duration = sound.duration

    results = {
        'duration_ms': round(duration * 1000),
    }

    # Pitch analysis
    pitch = sound.to_pitch(time_step=0.01)
    pitch_values = [f for f in pitch.selected_array['frequency'] if f > 0]
    if pitch_values:
        results['pitch_min'] = round(min(pitch_values))
        results['pitch_max'] = round(max(pitch_values))
        results['pitch_start'] = round(pitch_values[0])
        results['pitch_end'] = round(pitch_values[-1])
        results['pitch_drift'] = round(pitch_values[-1] - pitch_values[0])

    # Formant stability (sample at multiple time points)
    formant = sound.to_formant_burg(time_step=0.02, max_number_of_formants=4,
                                     maximum_formant=max_formant_hz)

    # Sample formants at 5 time points
    times = [duration * t for t in [0.2, 0.35, 0.5, 0.65, 0.8]]
    f1_vals, f2_vals, f3_vals = [], [], []

    for t in times:
        if t < duration:
            f1 = formant.get_value_at_time(1, t)
            f2 = formant.get_value_at_time(2, t)
            f3 = formant.get_value_at_time(3, t)
            if f1 and f1 == f1: f1_vals.append(f1)
            if f2 and f2 == f2: f2_vals.append(f2)
            if f3 and f3 == f3: f3_vals.append(f3)

    # Calculate drift (max - min variation)
    if f1_vals:
        results['F1_avg'] = round(np.mean(f1_vals))
        results['F1_drift'] = round(max(f1_vals) - min(f1_vals))
    if f2_vals:
        results['F2_avg'] = round(np.mean(f2_vals))
        results['F2_drift'] = round(max(f2_vals) - min(f2_vals))
    if f3_vals:
        results['F3_avg'] = round(np.mean(f3_vals))
        results['F3_drift'] = round(max(f3_vals) - min(f3_vals))

    # HNR (Harmonics-to-Noise Ratio) - voice quality/distortion metric
    try:
        hnr = sound.to_harmonicity()
        hnr_values = [h for h in hnr.values.flatten() if h > -200]
        if hnr_values:
            results['HNR_mean'] = round(np.mean(hnr_values), 1)
            results['HNR_min'] = round(min(hnr_values), 1)
    except:
        pass

    return results


def estimate_spectral_tilt(wav_path):
    """
    Estimate spectral tilt from WAV file using LTAS (Long-Term Average Spectrum).

    Spectral tilt indicates voice quality:
    - Steep rolloff (high tilt) = breathy voice
    - Flat rolloff (low tilt) = pressed/tense voice

    Returns estimated tilt in dB (0-41 range for NVSpeechPlayer).
    """
    if not HAS_PARSELMOUTH:
        return None

    sound = parselmouth.Sound(wav_path)

    # Create LTAS (Long-Term Average Spectrum)
    ltas = call(sound, "To Ltas", 100)  # 100 Hz bandwidth

    # Measure energy in low (500-1000 Hz) and high (2000-4000 Hz) bands
    try:
        low_energy = call(ltas, "Get mean", 500, 1000, "dB")
        high_energy = call(ltas, "Get mean", 2000, 4000, "dB")

        # Tilt is the difference (positive = more energy in lows)
        raw_tilt = low_energy - high_energy

        # Map to NVSpeechPlayer range (0-41 dB)
        # Typical speech tilt: 5-25 dB
        # Map: 5dB -> 0, 25dB -> 20 (moderate breathy)
        spectral_tilt = max(0, min(41, (raw_tilt - 5) * 1.0))

        return round(spectral_tilt)
    except:
        return None


def analyze_diphthong_trajectory(wav_path, num_points=10, max_formant_hz=5500):
    """
    Analyze formant trajectory over time for diphthong analysis.

    Returns list of dicts with formant values at each time point.
    """
    if not HAS_PARSELMOUTH:
        return None

    sound = parselmouth.Sound(wav_path)
    duration = sound.duration

    # Create formant object
    formant = sound.to_formant_burg(time_step=0.01, max_number_of_formants=5,
                                     maximum_formant=max_formant_hz)

    # Sample at multiple time points (avoid very start/end)
    trajectory = []
    for i in range(num_points):
        # Map 0->(num_points-1) to 0.1->0.9 of duration
        t_ratio = 0.1 + (0.8 * i / max(1, num_points - 1))
        t = duration * t_ratio

        point = {
            'time_pct': round(t_ratio * 100),
            'time_ms': round(t * 1000),
        }

        for fi in range(1, 5):
            try:
                f = formant.get_value_at_time(fi, t)
                b = formant.get_bandwidth_at_time(fi, t)
                point[f'F{fi}'] = round(f) if f and f == f else None
                point[f'B{fi}'] = round(b) if b and b == b else None
            except:
                point[f'F{fi}'] = None
                point[f'B{fi}'] = None

        trajectory.append(point)

    return trajectory


def extract_preset_params(wav_path, max_formant_hz=5500):
    """
    Extract synthesis parameters from WAV file suitable for preset creation.

    Returns dict with cascade and parallel formant parameters plus voice quality estimates.
    """
    if not HAS_PARSELMOUTH:
        return None

    # Get formant analysis at midpoint
    formants = analyze_formants(wav_path, max_formant_hz)
    if not formants:
        return None

    # Get stability analysis for averages
    stability = analyze_stability(wav_path, max_formant_hz)

    # Get spectral tilt estimate
    tilt = estimate_spectral_tilt(wav_path)

    # Build preset parameters
    params = {}

    # Cascade formants (primary synthesis path)
    for i in range(1, 5):
        f_key = f'F{i}'
        b_key = f'B{i}'

        # Use stability average if available, otherwise midpoint
        f_val = stability.get(f'{f_key}_avg') if stability else None
        if f_val is None:
            f_val = formants.get(f_key)

        b_val = formants.get(b_key)

        if f_val:
            params[f'cf{i}'] = f_val
        if b_val:
            params[f'cb{i}'] = b_val

    # Copy cascade to parallel (standard pattern for vowels)
    for i in range(1, 5):
        if f'cf{i}' in params:
            params[f'pf{i}'] = params[f'cf{i}']
        if f'cb{i}' in params:
            params[f'pb{i}'] = params[f'cb{i}']

    # Add higher formants with typical defaults
    if 'cf5' not in params:
        params['cf5'] = 4500
        params['cb5'] = 200
        params['pf5'] = 4500
        params['pb5'] = 200
    if 'cf6' not in params:
        params['cf6'] = 5000
        params['cb6'] = 500
        params['pf6'] = 5000
        params['pb6'] = 500

    # Voice quality estimates
    if tilt is not None:
        params['spectralTilt'] = tilt

    # Estimate glottal open quotient from HNR
    # Higher HNR = cleaner voice = lower open quotient (more closed)
    if stability and 'HNR_mean' in stability:
        hnr = stability['HNR_mean']
        # HNR 5-20 dB maps to OQ 0.6-0.4
        oq = max(0.35, min(0.65, 0.6 - (hnr - 5) * 0.015))
        params['glottalOpenQuotient'] = round(oq, 2)
    else:
        params['glottalOpenQuotient'] = 0.5  # neutral default

    # Standard vowel settings
    params['voiceAmplitude'] = 1.0
    params['_isVowel'] = True
    params['_isVoiced'] = True

    return params


def print_trajectory(trajectory, vowel_label=None):
    """Print diphthong trajectory in console table format."""
    if not trajectory:
        print("No trajectory data")
        return

    label = f" ({vowel_label})" if vowel_label else ""
    print(f"\nDIPHTHONG TRAJECTORY{label}")
    print("=" * 70)

    # Header
    print(f"{'Time':>6}  {'F1':>6}  {'F2':>6}  {'F3':>6}  {'F4':>6}")
    print("-" * 70)

    # Data rows
    for point in trajectory:
        time_str = f"{point['time_pct']}%"
        f1 = point.get('F1', '-')
        f2 = point.get('F2', '-')
        f3 = point.get('F3', '-')
        f4 = point.get('F4', '-')
        print(f"{time_str:>6}  {f1:>6}  {f2:>6}  {f3:>6}  {f4:>6}")

    # Calculate and show movement
    if len(trajectory) >= 2:
        start = trajectory[0]
        end = trajectory[-1]
        print("-" * 70)
        print("MOVEMENT (start -> end):")
        for i in range(1, 4):
            f_start = start.get(f'F{i}')
            f_end = end.get(f'F{i}')
            if f_start and f_end:
                delta = f_end - f_start
                direction = "up" if delta > 0 else "down" if delta < 0 else "stable"
                print(f"  F{i}: {f_start} -> {f_end} Hz ({delta:+d} Hz, {direction})")


def print_preset_params(params, vowel_label=None):
    """Print extracted preset parameters in both console and JSON format."""
    if not params:
        print("No parameters extracted")
        return

    label = f": {vowel_label}" if vowel_label else ""
    print(f"\nEXTRACTED PRESET PARAMETERS{label}")
    print("=" * 60)

    # Console format
    print("\nFORMANTS:")
    for i in range(1, 5):
        cf = params.get(f'cf{i}')
        cb = params.get(f'cb{i}')
        if cf:
            print(f"  F{i}: {cf} Hz (bandwidth: {cb} Hz)")

    print("\nVOICE QUALITY:")
    if 'spectralTilt' in params:
        print(f"  Spectral tilt: {params['spectralTilt']} dB")
    if 'glottalOpenQuotient' in params:
        print(f"  Glottal open quotient: {params['glottalOpenQuotient']}")

    # JSON format for copy/paste
    print("\nJSON (copy to presets/ folder):")
    print("-" * 60)

    # Create clean dict for JSON output
    json_params = {k: v for k, v in params.items() if not k.startswith('_')}
    print(json.dumps(json_params, indent=2))
    print("-" * 60)


def show_transition_params(vowel1, vowel2, play_audio=False):
    """
    Show parameter transition between two vowels.
    Optionally play audio preview of the transition.
    """
    try:
        from data import data as phoneme_data
    except ImportError:
        print("Error: Could not import phoneme data")
        return

    p1 = phoneme_data.get(vowel1)
    p2 = phoneme_data.get(vowel2)

    if not p1:
        print(f"Error: Vowel '{vowel1}' not found in phoneme data")
        return
    if not p2:
        print(f"Error: Vowel '{vowel2}' not found in phoneme data")
        return

    print(f"\nTRANSITION: {vowel1} -> {vowel2}")
    print("=" * 75)
    print("(Interpolated over 60ms fade duration)")
    print()

    # Parameters to compare
    formant_params = [
        ('cf1', 'F1 freq'),
        ('cb1', 'F1 bw'),
        ('cf2', 'F2 freq'),
        ('cb2', 'F2 bw'),
        ('cf3', 'F3 freq'),
        ('cb3', 'F3 bw'),
    ]

    voice_params = [
        ('spectralTilt', 'Spec tilt'),
        ('glottalOpenQuotient', 'Glot OQ'),
        ('voiceTurbulenceAmplitude', 'Breathiness'),
    ]

    # Header
    print(f"{'Parameter':<15} {'Start':>8} {'25%':>8} {'50%':>8} {'75%':>8} {'End':>8} {'Jump':>8}  Note")
    print("-" * 85)

    def interpolate(v1, v2, t):
        """Linear interpolation (actual uses Hermite smoothstep)."""
        if v1 is None or v2 is None:
            return None
        return v1 + (v2 - v1) * t

    def format_val(v):
        if v is None:
            return "-"
        if isinstance(v, float) and v < 10:
            return f"{v:.2f}"
        return str(round(v))

    all_params = formant_params + voice_params

    for param, label in all_params:
        v1 = p1.get(param)
        v2 = p2.get(param)

        # Show interpolated values
        v_25 = interpolate(v1, v2, 0.25)
        v_50 = interpolate(v1, v2, 0.50)
        v_75 = interpolate(v1, v2, 0.75)

        # Calculate jump
        if v1 is not None and v2 is not None:
            jump = abs(v2 - v1)
            # Check if large jump (>30% for frequencies, >50% for others)
            is_large = False
            if param.startswith('cf') and v1 > 0:
                is_large = jump / v1 > 0.3
            elif jump > 0.5 and isinstance(v1, float):
                is_large = True
            note = "<-- LARGE" if is_large else ""
        else:
            jump = None
            note = ""

        print(f"{label:<15} {format_val(v1):>8} {format_val(v_25):>8} {format_val(v_50):>8} {format_val(v_75):>8} {format_val(v2):>8} {format_val(jump):>8}  {note}")

    # Play audio if requested
    if play_audio:
        print("\nGenerating transition audio...")
        play_transition(vowel1, vowel2)


def play_transition(vowel1, vowel2, fade_ms=60, duration_ms=300):
    """Generate and play a transition between two vowels."""
    try:
        from data import data as phoneme_data
        import speechPlayer
        import ipa
        import wave
        import struct
        import tempfile
    except ImportError as e:
        print(f"Error importing modules: {e}")
        return

    SAMPLE_RATE = 16000

    p1 = phoneme_data.get(vowel1)
    p2 = phoneme_data.get(vowel2)

    if not p1 or not p2:
        print("Error: Could not load vowel data")
        return

    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)

    # First vowel (sustained)
    frame1 = speechPlayer.Frame()
    frame1.preFormantGain = 1.0
    frame1.outputGain = 2.0
    ipa.applyPhonemeToFrame(frame1, p1)
    frame1.voicePitch = 120
    sp.queueFrame(frame1, duration_ms, 25)  # 25ms fade in

    # Second vowel (transition)
    frame2 = speechPlayer.Frame()
    frame2.preFormantGain = 1.0
    frame2.outputGain = 2.0
    ipa.applyPhonemeToFrame(frame2, p2)
    frame2.voicePitch = 120
    sp.queueFrame(frame2, duration_ms, fade_ms)  # configurable transition fade

    # Silence at end
    sp.queueFrame(None, 100, 50)

    # Synthesize
    all_samples = []
    BATCH_SIZE = 8192
    while True:
        samples = sp.synthesize(BATCH_SIZE)
        if samples:
            all_samples.extend(samples[:])
            if len(samples) < BATCH_SIZE:
                break
        else:
            break

    if not all_samples:
        print("Error: No audio generated")
        return

    # Write to temp file and play
    temp_wav = tempfile.mktemp(suffix='.wav')
    try:
        with wave.open(temp_wav, 'w') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)
            wav.writeframes(struct.pack('<%dh' % len(all_samples), *all_samples))

        if HAS_WINSOUND:
            print(f"Playing: {vowel1} -> {vowel2} (fade: {fade_ms}ms)")
            winsound.PlaySound(temp_wav, winsound.SND_FILENAME)
        else:
            print(f"Audio saved to: {temp_wav}")
            print("(winsound not available for playback)")
    finally:
        if HAS_WINSOUND and os.path.exists(temp_wav):
            os.remove(temp_wav)


def print_stability_analysis(results, vowel=None):
    """Print stability analysis in accessible text format."""
    print("\nVOWEL STABILITY ANALYSIS")
    print("=" * 55)
    print(f"Duration: {results.get('duration_ms', 'N/A')} ms")

    # Pitch info
    print("\nPITCH:")
    if 'pitch_min' in results:
        print(f"  Range: {results['pitch_min']} - {results['pitch_max']} Hz")
        print(f"  Start: {results['pitch_start']} Hz, End: {results['pitch_end']} Hz")
        print(f"  Drift: {results['pitch_drift']:+d} Hz")
    else:
        print("  No pitch detected")

    # Formant stability
    print("\nFORMANT STABILITY (lower drift = more stable):")
    for i in range(1, 4):
        avg = results.get(f'F{i}_avg')
        drift = results.get(f'F{i}_drift')
        if avg and drift:
            stability = "STABLE" if drift < 50 else "UNSTABLE" if drift > 200 else "MODERATE"
            print(f"  F{i}: avg {avg} Hz, drift {drift} Hz ({stability})")

    # Voice quality
    print("\nVOICE QUALITY (HNR - higher = cleaner):")
    hnr_mean = results.get('HNR_mean')
    if hnr_mean is not None:
        if hnr_mean > 15:
            quality = "GOOD"
        elif hnr_mean > 10:
            quality = "ACCEPTABLE"
        elif hnr_mean > 5:
            quality = "ROUGH"
        else:
            quality = "DISTORTED"
        print(f"  HNR mean: {hnr_mean} dB ({quality})")
        print(f"  HNR min: {results.get('HNR_min')} dB")
    else:
        print("  HNR: N/A")

    # Compare to reference if vowel specified
    if vowel and vowel in REFERENCE:
        ref = REFERENCE[vowel]
        print(f"\nCOMPARISON TO TARGET ({vowel} - {ref['desc']}):")
        for i in range(1, 4):
            avg = results.get(f'F{i}_avg')
            ref_key = f'F{i}'
            if avg and ref_key in ref:
                status = check_in_range(avg, ref[ref_key])
                print(f"  F{i}: {status}")


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


def generate_vowel_wav(vowel, output_path, duration_ms=500, start_pitch=120, end_pitch=None):
    """Generate a vowel WAV file using the NVSpeechPlayer synthesizer.

    Args:
        vowel: IPA vowel character to synthesize
        output_path: Path for output WAV file
        duration_ms: Duration in milliseconds
        start_pitch: Starting pitch in Hz (default 120)
        end_pitch: Ending pitch in Hz (if None, uses start_pitch for steady pitch)
    """
    try:
        from data import data as phoneme_data_dict
        import speechPlayer
        import wave
        import struct

        SAMPLE_RATE = 16000

        if end_pitch is None:
            end_pitch = start_pitch

        # Initialize synthesizer
        sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)

        # Get the phoneme data for the vowel
        phoneme_data = phoneme_data_dict.get(vowel)
        if not phoneme_data:
            print(f"Error: Vowel '{vowel}' not found in phoneme data")
            return False

        # Create frames with custom pitch contour
        # Calculate duration in samples and frames
        target_samples = int(SAMPLE_RATE * duration_ms / 1000)
        frame_duration_ms = 10  # 10ms per frame
        num_frames = max(1, duration_ms // frame_duration_ms)

        # Import the applyPhonemeToFrame function for proper frame setup
        import ipa

        for i in range(num_frames):
            # Interpolate pitch linearly
            t = i / max(1, num_frames - 1)
            current_pitch = start_pitch + (end_pitch - start_pitch) * t

            # Create frame properly (must set preFormantGain and outputGain)
            frame = speechPlayer.Frame()
            frame.preFormantGain = 1.0
            frame.outputGain = 2.0

            # Apply phoneme data (this also applies KLSYN88 defaults)
            ipa.applyPhonemeToFrame(frame, phoneme_data)

            # Set the pitch
            frame.voicePitch = current_pitch

            # Queue the frame
            sp.queueFrame(frame, frame_duration_ms, 0)

        frame_count = num_frames

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
    parser = argparse.ArgumentParser(description='Analyze vowel formants and extract preset parameters')
    parser.add_argument('--wav', help='Path to existing WAV file to analyze')
    parser.add_argument('--vowel', help='Specific vowel to generate and analyze')
    parser.add_argument('--all', action='store_true', help='Analyze all reference vowels')
    parser.add_argument('--max-freq', type=int, default=5500,
                       help='Maximum formant frequency (5500 for male, 5000 for female)')
    parser.add_argument('--start-pitch', type=float, default=120,
                       help='Starting pitch in Hz (default 120)')
    parser.add_argument('--end-pitch', type=float, default=None,
                       help='Ending pitch in Hz (default: same as start-pitch for steady tone)')
    parser.add_argument('--duration', type=int, default=500,
                       help='Duration in milliseconds (default 500)')
    parser.add_argument('--stability', action='store_true',
                       help='Run stability analysis (formant drift, HNR)')

    # New options for preset extraction and diphthong analysis
    parser.add_argument('--extract-preset', action='store_true',
                       help='Extract preset parameters from WAV file (use with --wav)')
    parser.add_argument('--trajectory', action='store_true',
                       help='Analyze diphthong trajectory (formants over time)')
    parser.add_argument('--trajectory-points', type=int, default=10,
                       help='Number of time points for trajectory analysis (default 10)')
    parser.add_argument('--transition', nargs=2, metavar=('VOWEL1', 'VOWEL2'),
                       help='Show parameter transition between two vowels')
    parser.add_argument('--play', action='store_true',
                       help='Play audio preview (use with --transition)')
    parser.add_argument('--output-json', metavar='FILE',
                       help='Write preset parameters to JSON file')

    args = parser.parse_args()

    # --transition doesn't require parselmouth
    if args.transition:
        show_transition_params(args.transition[0], args.transition[1], play_audio=args.play)
        return

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

        # Diphthong trajectory analysis
        if args.trajectory:
            trajectory = analyze_diphthong_trajectory(args.wav, args.trajectory_points, args.max_freq)
            print_trajectory(trajectory, args.vowel)
            return

        # Preset parameter extraction
        if args.extract_preset:
            params = extract_preset_params(args.wav, args.max_freq)
            print_preset_params(params, args.vowel)

            # Optionally write to JSON file
            if args.output_json and params:
                json_params = {k: v for k, v in params.items() if not k.startswith('_')}
                with open(args.output_json, 'w', encoding='utf-8') as f:
                    json.dump(json_params, f, indent=2)
                print(f"\nPreset written to: {args.output_json}")
            return

        # Standard formant analysis
        results = analyze_formants(args.wav, args.max_freq)
        print_analysis(results, args.vowel)

        # Also run stability if requested
        if args.stability:
            stability = analyze_stability(args.wav, args.max_freq)
            if stability:
                print_stability_analysis(stability, args.vowel)

    elif args.vowel:
        # Generate and analyze specific vowel
        temp_wav = f"temp_{ord(args.vowel):04x}.wav"
        end_pitch = args.end_pitch if args.end_pitch else args.start_pitch

        print(f"Generating vowel '{args.vowel}'...")
        print(f"  Pitch: {args.start_pitch} -> {end_pitch} Hz")
        print(f"  Duration: {args.duration} ms")

        if generate_vowel_wav(args.vowel, temp_wav, args.duration, args.start_pitch, args.end_pitch):
            # Standard formant analysis
            results = analyze_formants(temp_wav, args.max_freq)
            print_analysis(results, args.vowel)

            # Stability analysis (always run when pitch varies, or if requested)
            if args.stability or (args.end_pitch and args.end_pitch != args.start_pitch):
                stability = analyze_stability(temp_wav, args.max_freq)
                if stability:
                    print_stability_analysis(stability, args.vowel)

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
        print("  # Basic formant analysis")
        print("  python analyze_vowels.py --wav test.wav")
        print("  python analyze_vowels.py --vowel a")
        print("  python analyze_vowels.py --vowel ɑ --start-pitch 55 --end-pitch 15")
        print("  python analyze_vowels.py --vowel i --stability")
        print("  python analyze_vowels.py --all")
        print()
        print("  # Extract preset parameters from recorded vowel")
        print("  python analyze_vowels.py --wav my_vowel.wav --extract-preset")
        print("  python analyze_vowels.py --wav my_vowel.wav --extract-preset --output-json presets/new.json")
        print()
        print("  # Analyze diphthong trajectory")
        print("  python analyze_vowels.py --wav diphthong.wav --trajectory")
        print("  python analyze_vowels.py --wav diphthong.wav --trajectory --trajectory-points 20")
        print()
        print("  # Show transition between two vowels")
        print("  python analyze_vowels.py --transition ø y")
        print("  python analyze_vowels.py --transition ø y --play")


if __name__ == '__main__':
    main()
