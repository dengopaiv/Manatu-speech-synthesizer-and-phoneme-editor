# -*- coding: utf-8 -*-
"""
Spectral analysis module for NVSpeechPlayer phoneme validation.

Pure numpy/scipy implementation (no parselmouth dependency).
Provides LPC-based formant extraction, pitch estimation, HNR,
spectral centroid, and voicing detection.

Usage:
    from tools.spectral_analysis import analyze_segment, extract_formants_lpc

    result = analyze_segment(samples, sample_rate)
    print(result.formants)  # [(freq, bw), ...]
"""

import numpy as np
from scipy.signal.windows import hamming
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class SpectralAnalysisResult:
    """All-in-one analysis result for a segment of audio."""
    formants: List[Tuple[float, float]] = field(default_factory=list)  # [(freq, bandwidth), ...]
    f0: Optional[float] = None  # Fundamental frequency in Hz
    hnr: Optional[float] = None  # Harmonic-to-noise ratio in dB
    spectral_centroid: Optional[float] = None  # Hz
    is_voiced: bool = False
    rms: float = 0.0  # RMS amplitude


def _pre_emphasis(samples, coeff=0.97):
    """Apply pre-emphasis filter to boost high frequencies."""
    return np.append(samples[0], samples[1:] - coeff * samples[:-1])


def _autocorrelation(signal, order):
    """Compute autocorrelation coefficients via numpy correlate."""
    n = len(signal)
    # Pad to avoid circular effects
    padded = np.zeros(2 * n)
    padded[:n] = signal
    # Use FFT-based autocorrelation for efficiency
    fft_sig = np.fft.rfft(padded)
    acf = np.fft.irfft(fft_sig * np.conj(fft_sig))
    return acf[:order + 1] / acf[0] if acf[0] > 0 else np.zeros(order + 1)


def _levinson_durbin(acf, order):
    """Solve for LPC coefficients using Levinson-Durbin recursion.

    Args:
        acf: Autocorrelation values r[0]..r[order]
        order: LPC order

    Returns:
        LPC coefficients [a1, a2, ..., a_order]
    """
    # Initialize
    a = np.zeros(order + 1)
    a[0] = 1.0
    error = acf[0]

    if error <= 0:
        return a[1:]

    for i in range(1, order + 1):
        # Compute reflection coefficient
        reflection = -np.sum(a[:i] * acf[i:0:-1]) / error
        # Update coefficients
        a_new = a.copy()
        for j in range(1, i):
            a_new[j] = a[j] + reflection * a[i - j]
        a_new[i] = reflection
        a = a_new
        error *= (1 - reflection * reflection)
        if error <= 0:
            break

    return a[1:]


def _get_lpc_coefficients(samples, sample_rate, lpc_order=None):
    """Compute LPC coefficients from audio samples.

    Args:
        samples: Normalized audio samples as float64 array
        sample_rate: Sample rate in Hz
        lpc_order: LPC model order

    Returns:
        (poly, lpc_order) where poly is the LPC polynomial [1, a1, a2, ...],
        or (None, 0) on failure.
    """
    if len(samples) < 50:
        return None, 0

    # Normalize
    max_val = np.max(np.abs(samples))
    if max_val > 0:
        samples = samples / max_val

    if lpc_order is None:
        lpc_order = int(sample_rate / 1700)

    # Pre-emphasis
    emphasized = _pre_emphasis(samples)

    # Hamming window
    windowed = emphasized * hamming(len(emphasized))

    # FFT-based autocorrelation
    acf = _autocorrelation(windowed, lpc_order)
    if acf[0] <= 0:
        return None, 0

    # Levinson-Durbin
    lpc_coeffs = _levinson_durbin(acf, lpc_order)

    poly = np.concatenate(([1.0], lpc_coeffs))
    return poly, lpc_order


def _formants_from_roots(poly, sample_rate, num_formants):
    """Extract formants by finding roots of the LPC polynomial.

    Best for well-separated formants. May miss formants that are
    close together (e.g., F1/F2 in back rounded vowels).
    """
    roots = np.roots(poly)

    formant_candidates = []
    for root in roots:
        if np.imag(root) <= 0:
            continue

        mag = np.abs(root)
        if mag >= 1.0 or mag < 0.5:
            continue

        freq = np.arctan2(np.imag(root), np.real(root)) * (sample_rate / (2 * np.pi))
        bw = -1.0 * (sample_rate / (2 * np.pi)) * np.log(mag)

        if 90 < freq < (sample_rate / 2 - 100) and bw > 0 and bw < 3000:
            formant_candidates.append((freq, bw))

    formant_candidates.sort(key=lambda x: x[0])
    return formant_candidates[:num_formants]


def _formants_from_peaks(poly, sample_rate, num_formants):
    """Extract formants by peak-picking on the LPC spectral envelope.

    More robust than root-finding for close formants (e.g., back rounded
    vowels where F1 and F2 are near each other).
    """
    # Evaluate LPC envelope at high frequency resolution
    nfft = 4096
    freqs = np.linspace(0, sample_rate / 2, nfft // 2 + 1)
    # Compute frequency response: H(z) = 1/A(z)
    w = np.exp(-1j * 2 * np.pi * freqs / sample_rate)
    # Evaluate polynomial A(z) = sum(poly[k] * z^-k)
    response = np.zeros(len(freqs), dtype=complex)
    for k, coeff in enumerate(poly):
        response += coeff * (w ** k)

    # LPC spectral envelope in dB
    magnitude = np.abs(response)
    magnitude[magnitude < 1e-10] = 1e-10
    envelope_db = -20 * np.log10(magnitude)  # Negative because H = 1/A

    # Find local maxima (peaks) in the envelope
    formant_candidates = []
    for i in range(1, len(envelope_db) - 1):
        if envelope_db[i] > envelope_db[i - 1] and envelope_db[i] > envelope_db[i + 1]:
            freq = freqs[i]
            if 90 < freq < (sample_rate / 2 - 100):
                # Estimate bandwidth from the -3dB width of the peak
                peak_level = envelope_db[i]
                threshold = peak_level - 3.0
                # Search left
                left = i
                while left > 0 and envelope_db[left] > threshold:
                    left -= 1
                # Search right
                right = i
                while right < len(envelope_db) - 1 and envelope_db[right] > threshold:
                    right += 1
                bw = freqs[right] - freqs[left] if right > left else 100
                # Prominence: how much this peak stands out above the valley
                left_valley = np.min(envelope_db[max(0, left - 5):left + 1])
                right_valley = np.min(envelope_db[right:min(len(envelope_db), right + 5)])
                prominence = peak_level - max(left_valley, right_valley)

                if prominence > 1.0 and bw < 3000:
                    formant_candidates.append((freq, bw, prominence))

    # Sort by frequency, return top num_formants
    formant_candidates.sort(key=lambda x: x[0])
    return [(f, bw) for f, bw, _ in formant_candidates[:num_formants]]


def extract_formants_lpc(samples, sample_rate, num_formants=4, lpc_order=None):
    """Extract formant frequencies and bandwidths using LPC analysis.

    Uses a combined approach: root-finding for well-separated formants,
    with peak-picking on the LPC envelope as a fallback for close formants
    (common in back rounded vowels).

    Algorithm: normalize -> pre-emphasis -> Hamming window -> FFT-based
    autocorrelation -> Levinson-Durbin -> root finding + peak picking.

    Args:
        samples: Audio samples as numpy array or list (int16 or float)
        sample_rate: Sample rate in Hz
        num_formants: Number of formants to extract (default 4)
        lpc_order: LPC order (default: sample_rate/1700, giving 13@22050 or 26@44100)

    Returns:
        List of (frequency, bandwidth) tuples, sorted by frequency.
        May return fewer than num_formants if extraction fails.
    """
    samples = np.asarray(samples, dtype=np.float64)

    poly, order = _get_lpc_coefficients(samples, sample_rate, lpc_order)
    if poly is None:
        return []

    # Try both methods and pick the better result
    root_formants = _formants_from_roots(poly, sample_rate, num_formants)
    peak_formants = _formants_from_peaks(poly, sample_rate, num_formants)

    # Use peak-picking if it found more formants (common for back rounded
    # vowels where F1/F2 are close together)
    if len(peak_formants) > len(root_formants):
        return peak_formants

    # If both have the same count, prefer root-finding (more precise)
    return root_formants


def extract_formants_lpc_trajectory(samples, sample_rate, frame_ms=25, num_formants=4):
    """Frame-by-frame formant tracking for transition analysis.

    Args:
        samples: Audio samples
        sample_rate: Sample rate in Hz
        frame_ms: Frame size in milliseconds (default 25)
        num_formants: Number of formants to extract per frame

    Returns:
        List of dicts, each with 'time_ms' and 'formants' [(freq, bw), ...].
    """
    samples = np.asarray(samples, dtype=np.float64)
    frame_size = int(sample_rate * frame_ms / 1000)
    hop_size = frame_size // 2  # 50% overlap

    trajectory = []
    offset = 0
    while offset + frame_size <= len(samples):
        frame = samples[offset:offset + frame_size]
        time_ms = (offset + frame_size / 2) * 1000 / sample_rate

        formants = extract_formants_lpc(frame, sample_rate, num_formants)
        trajectory.append({
            'time_ms': time_ms,
            'formants': formants,
        })
        offset += hop_size

    return trajectory


def estimate_f0(samples, sample_rate, min_f0=60, max_f0=500):
    """Estimate fundamental frequency using autocorrelation method.

    Args:
        samples: Audio samples
        sample_rate: Sample rate in Hz
        min_f0: Minimum expected F0 (Hz)
        max_f0: Maximum expected F0 (Hz)

    Returns:
        Estimated F0 in Hz, or None if unvoiced/undetectable.
    """
    samples = np.asarray(samples, dtype=np.float64)

    if len(samples) < sample_rate // min_f0:
        return None

    # Remove DC offset
    samples = samples - np.mean(samples)

    # Normalize
    if np.max(np.abs(samples)) > 0:
        samples = samples / np.max(np.abs(samples))

    # Compute autocorrelation
    n = len(samples)
    acf = np.correlate(samples, samples, mode='full')
    acf = acf[n - 1:]  # Positive lags only

    # Normalize
    if acf[0] > 0:
        acf = acf / acf[0]

    # Search for peak in expected F0 range
    min_lag = int(sample_rate / max_f0)
    max_lag = min(int(sample_rate / min_f0), len(acf) - 1)

    if min_lag >= max_lag or max_lag >= len(acf):
        return None

    search_region = acf[min_lag:max_lag + 1]
    if len(search_region) == 0:
        return None

    peak_idx = np.argmax(search_region) + min_lag
    peak_val = acf[peak_idx]

    # Voicing threshold: autocorrelation peak must be strong enough
    if peak_val < 0.25:
        return None

    # Parabolic interpolation for sub-sample accuracy
    if 0 < peak_idx < len(acf) - 1:
        alpha = acf[peak_idx - 1]
        beta = acf[peak_idx]
        gamma = acf[peak_idx + 1]
        denom = alpha - 2 * beta + gamma
        if abs(denom) > 1e-10:
            offset = 0.5 * (alpha - gamma) / denom
            peak_idx = peak_idx + offset

    f0 = sample_rate / peak_idx
    return f0


def estimate_hnr(samples, sample_rate, min_f0=60, max_f0=500):
    """Estimate Harmonic-to-Noise Ratio.

    Uses autocorrelation method: HNR = 10*log10(r_max / (1 - r_max))
    where r_max is the normalized autocorrelation at the pitch period.

    Args:
        samples: Audio samples
        sample_rate: Sample rate in Hz

    Returns:
        HNR in dB, or None if estimation fails.
    """
    samples = np.asarray(samples, dtype=np.float64)
    samples = samples - np.mean(samples)

    if np.max(np.abs(samples)) == 0:
        return None

    samples = samples / np.max(np.abs(samples))

    # Compute autocorrelation
    n = len(samples)
    acf = np.correlate(samples, samples, mode='full')
    acf = acf[n - 1:]
    if acf[0] <= 0:
        return None
    acf = acf / acf[0]

    # Find pitch period peak
    min_lag = int(sample_rate / max_f0)
    max_lag = min(int(sample_rate / min_f0), len(acf) - 1)

    if min_lag >= max_lag:
        return None

    search_region = acf[min_lag:max_lag + 1]
    if len(search_region) == 0:
        return None

    r_max = np.max(search_region)

    if r_max <= 0 or r_max >= 1:
        return None

    hnr = 10 * np.log10(r_max / (1 - r_max))
    return hnr


def estimate_spectral_centroid(samples, sample_rate):
    """Estimate spectral centroid frequency.

    Useful for discriminating fricative place of articulation.
    /s/ has higher centroid than /ʃ/ which has higher than /f/.

    Args:
        samples: Audio samples
        sample_rate: Sample rate in Hz

    Returns:
        Spectral centroid in Hz.
    """
    samples = np.asarray(samples, dtype=np.float64)

    if len(samples) == 0:
        return 0.0

    # Compute magnitude spectrum
    spectrum = np.abs(np.fft.rfft(samples * hamming(len(samples))))
    freqs = np.fft.rfftfreq(len(samples), 1.0 / sample_rate)

    # Weighted average frequency
    total_energy = np.sum(spectrum)
    if total_energy <= 0:
        return 0.0

    centroid = np.sum(freqs * spectrum) / total_energy
    return centroid


def is_voiced(samples, sample_rate, threshold=0.25):
    """Detect whether a segment is voiced.

    Uses autocorrelation peak strength as indicator.

    Args:
        samples: Audio samples
        sample_rate: Sample rate in Hz
        threshold: Minimum autocorrelation peak (0-1) to consider voiced

    Returns:
        True if voiced, False otherwise.
    """
    f0 = estimate_f0(samples, sample_rate)
    return f0 is not None


def analyze_segment(samples, sample_rate, num_formants=4):
    """All-in-one spectral analysis returning a SpectralAnalysisResult.

    Args:
        samples: Audio samples (numpy array or list of int16 values)
        sample_rate: Sample rate in Hz
        num_formants: Number of formants to extract

    Returns:
        SpectralAnalysisResult dataclass with all analysis results.
    """
    samples = np.asarray(samples, dtype=np.float64)

    result = SpectralAnalysisResult()

    if len(samples) < 50:
        return result

    # RMS amplitude
    result.rms = float(np.sqrt(np.mean(samples ** 2)))

    # Formants via LPC
    result.formants = extract_formants_lpc(samples, sample_rate, num_formants)

    # Pitch
    result.f0 = estimate_f0(samples, sample_rate)

    # Voicing
    result.is_voiced = result.f0 is not None

    # HNR (only meaningful for voiced segments)
    if result.is_voiced:
        result.hnr = estimate_hnr(samples, sample_rate)

    # Spectral centroid
    result.spectral_centroid = estimate_spectral_centroid(samples, sample_rate)

    return result
