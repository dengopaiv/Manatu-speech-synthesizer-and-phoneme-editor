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


def _f1_from_parametric_fit(samples, sample_rate, f0_est=None):
    """Estimate F1 by fitting a source+resonance model to harmonic amplitudes.

    Fits: amplitude(f) = source_tilt(f) + resonance(f)
    where source_tilt is -alpha dB/octave and resonance is a Lorentzian peak.
    Uses harmonics H2-H8 (below ~1 kHz) to isolate the F1 region from F2+.
    Solves the harmonic sampling problem by modeling the underlying envelope
    rather than interpolating between sparse harmonic samples.

    Returns (f1_freq, f1_bandwidth) or None if fit fails.
    """
    from scipy.optimize import minimize as sp_minimize

    # Use a centered 100ms analysis frame
    frame_len = min(len(samples), int(sample_rate * 0.100))
    start = (len(samples) - frame_len) // 2
    frame = samples[start:start + frame_len]

    emphasized = _pre_emphasis(frame)
    windowed = emphasized * hamming(len(emphasized))

    nfft = 8192
    spectrum = np.fft.rfft(windowed, nfft)
    log_mag = 20 * np.log10(np.abs(spectrum) + 1e-10)
    freqs = np.fft.rfftfreq(nfft, 1.0 / sample_rate)
    freq_spacing = sample_rate / nfft

    if f0_est is None:
        f0_len = min(len(samples), int(sample_rate * 0.100))
        f0_start = (len(samples) - f0_len) // 2
        f0_est = estimate_f0(samples[f0_start:f0_start + f0_len], sample_rate) or 120.0

    # Extract harmonic amplitudes H2-H8
    h_freqs = []
    h_amps = []
    for n in range(2, 9):
        h_freq = n * f0_est
        if h_freq > sample_rate / 2 - 200:
            break
        idx = int(h_freq / freq_spacing)
        half_win = max(1, int(f0_est / (4 * freq_spacing)))
        lo = max(0, idx - half_win)
        hi = min(len(log_mag) - 1, idx + half_win)
        peak_idx = lo + np.argmax(log_mag[lo:hi + 1])
        h_freqs.append(freqs[peak_idx])
        h_amps.append(log_mag[peak_idx])

    if len(h_freqs) < 4:
        return None

    h_f = np.array(h_freqs)
    h_a = np.array(h_amps)

    # Fit: source_tilt + single_resonance to harmonic amplitudes
    def cost(params):
        s0, alpha, fc, bw = params
        tilt = s0 - alpha * np.log2(h_f / h_f[0])
        resonance = -10 * np.log10((h_f - fc) ** 2 + (bw / 2) ** 2)
        return np.sum((tilt + resonance - h_a) ** 2)

    result = sp_minimize(cost, [120, 6, 400, 100],
                         bounds=[(50, 200), (0, 20), (150, 900), (30, 500)],
                         method='L-BFGS-B')
    if not result.success:
        return None

    fc, bw = result.x[2], result.x[3]
    return (fc, bw)


def _formants_from_harmonic_interp(samples, sample_rate, num_formants, f0_est=None):
    """Extract formants by interpolating between harmonic amplitudes.

    Measures the amplitude at each harmonic of F0, then fits a cubic spline
    through these samples of the spectral envelope. Peaks of the spline
    give formant frequencies. Directly addresses harmonic sampling bias.
    """
    from scipy.interpolate import CubicSpline

    # Use a centered 100ms analysis frame
    frame_len = min(len(samples), int(sample_rate * 0.100))
    start = (len(samples) - frame_len) // 2
    frame = samples[start:start + frame_len]

    emphasized = _pre_emphasis(frame)
    windowed = emphasized * hamming(len(emphasized))

    nfft = 8192
    spectrum = np.fft.rfft(windowed, nfft)
    log_mag = 20 * np.log10(np.abs(spectrum) + 1e-10)
    freqs = np.fft.rfftfreq(nfft, 1.0 / sample_rate)
    freq_spacing = sample_rate / nfft

    # Estimate F0
    if f0_est is None:
        f0_len = min(len(samples), int(sample_rate * 0.100))
        f0_start = (len(samples) - f0_len) // 2
        f0_est = estimate_f0(samples[f0_start:f0_start + f0_len], sample_rate) or 120.0

    # Extract harmonic amplitudes (peak in ±F0/4 window around each harmonic)
    h_freqs = []
    h_amps = []
    for n in range(2, 50):  # skip fundamental, start at H2
        h_freq = n * f0_est
        if h_freq > sample_rate / 2 - 200:
            break
        idx = int(h_freq / freq_spacing)
        # Search for peak in window around expected harmonic
        half_win = max(1, int(f0_est / (4 * freq_spacing)))
        lo = max(0, idx - half_win)
        hi = min(len(log_mag) - 1, idx + half_win)
        peak_idx = lo + np.argmax(log_mag[lo:hi + 1])
        h_freqs.append(freqs[peak_idx])
        h_amps.append(log_mag[peak_idx])

    if len(h_freqs) < 4:
        return []

    # Fit cubic spline through harmonic amplitude samples
    cs = CubicSpline(h_freqs, h_amps)

    # Evaluate at fine grid and find peaks
    fine_freqs = np.arange(max(200, 1.5 * f0_est), min(5500, sample_rate / 2 - 200), 2.0)
    fine_amps = cs(fine_freqs)

    # Remove spectral tilt
    if len(fine_amps) > 2:
        slope = (fine_amps[-1] - fine_amps[0]) / (len(fine_amps) - 1)
        fine_amps = fine_amps - (fine_amps[0] + slope * np.arange(len(fine_amps)))

    # Peak-pick
    formant_candidates = []
    for i in range(1, len(fine_amps) - 1):
        if fine_amps[i] > fine_amps[i - 1] and fine_amps[i] > fine_amps[i + 1]:
            freq = fine_freqs[i]
            peak_level = fine_amps[i]
            # Estimate bandwidth from -3dB width
            threshold = peak_level - 3.0
            left = i
            while left > 0 and fine_amps[left] > threshold:
                left -= 1
            right = i
            while right < len(fine_amps) - 1 and fine_amps[right] > threshold:
                right += 1
            bw = fine_freqs[right] - fine_freqs[left] if right > left else 100
            # Prominence
            left_valley = np.min(fine_amps[max(0, left - 20):left + 1])
            right_valley = np.min(fine_amps[right:min(len(fine_amps), right + 20)])
            prominence = peak_level - max(left_valley, right_valley)
            if prominence > 1.5 and bw < 3000:
                formant_candidates.append((freq, bw, prominence))

    formant_candidates.sort(key=lambda x: x[0])
    return [(f, bw) for f, bw, _ in formant_candidates[:num_formants]]


def _formants_from_smoothed_spectrum(samples, sample_rate, num_formants, f0_est=None):
    """Extract formants via cepstral smoothing of the spectral envelope.

    Uses cepstral liftering to cleanly separate the spectral envelope
    (formant structure) from harmonic fine structure (F0 and overtones).
    More robust than LPC or boxcar smoothing for BLIT harmonic sources.
    """
    # Use a centered 100ms analysis frame (needs ≥3 pitch periods for
    # good spectral resolution; 100ms gives 12 periods at F0=120 Hz)
    frame_len = min(len(samples), int(sample_rate * 0.100))
    start = (len(samples) - frame_len) // 2
    frame = samples[start:start + frame_len]

    emphasized = _pre_emphasis(frame)
    windowed = emphasized * hamming(len(emphasized))

    nfft = 8192

    # Estimate F0 for adaptive liftering cutoff
    if f0_est is None:
        f0_len = min(len(samples), int(sample_rate * 0.100))
        f0_start = (len(samples) - f0_len) // 2
        f0_seg = samples[f0_start:f0_start + f0_len]
        f0_est = estimate_f0(f0_seg, sample_rate) or 120.0

    # Cepstral smoothing: log-spectrum → cepstrum → lifter → smooth envelope
    full_spec = np.fft.fft(windowed, nfft)
    log_mag = np.log(np.abs(full_spec) + 1e-10)
    cepstrum = np.fft.ifft(log_mag).real

    # Lifter cutoff at quefrency = 1/(3*F0) — well below the first harmonic
    # peak in the cepstrum (at 1/F0), keeping only the broad spectral envelope
    lifter_cutoff = int(sample_rate / (3.0 * f0_est))
    cepstrum[lifter_cutoff + 1:nfft - lifter_cutoff] = 0

    # Back to smoothed spectral envelope (positive frequencies, in dB)
    smooth_env = np.fft.fft(cepstrum).real[:nfft // 2 + 1]
    smooth_db = smooth_env * (20.0 / np.log(10))
    freqs = np.fft.rfftfreq(nfft, 1.0 / sample_rate)

    # Remove spectral tilt (linear trend) to reduce low-frequency bias
    # in peak positions — formant peaks are relative to the envelope slope
    if len(smooth_db) > 2:
        slope = (smooth_db[-1] - smooth_db[0]) / (len(smooth_db) - 1)
        smooth_db = smooth_db - (smooth_db[0] + slope * np.arange(len(smooth_db)))

    # Peak-pick formants from smoothed envelope
    formant_candidates = []
    for i in range(1, len(smooth_db) - 1):
        if smooth_db[i] > smooth_db[i - 1] and smooth_db[i] > smooth_db[i + 1]:
            freq = freqs[i]
            # Skip below 1.5*F0 to avoid picking up the fundamental
            min_freq = max(200, 1.5 * f0_est)
            if min_freq < freq < (sample_rate / 2 - 100):
                peak_level = smooth_db[i]
                threshold = peak_level - 3.0
                left = i
                while left > 0 and smooth_db[left] > threshold:
                    left -= 1
                right = i
                while right < len(smooth_db) - 1 and smooth_db[right] > threshold:
                    right += 1
                bw = freqs[right] - freqs[left] if right > left else 100
                left_valley = np.min(smooth_db[max(0, left - 5):left + 1])
                right_valley = np.min(smooth_db[right:min(len(smooth_db), right + 5)])
                prominence = peak_level - max(left_valley, right_valley)
                if prominence > 2.0 and bw < 3000:
                    formant_candidates.append((freq, bw, prominence))

    formant_candidates.sort(key=lambda x: x[0])
    return [(f, bw) for f, bw, _ in formant_candidates[:num_formants]]


def extract_formants_lpc(samples, sample_rate, num_formants=4, lpc_order=None):
    """Extract formant frequencies and bandwidths using spectral smoothing + LPC.

    Runs two complementary methods and merges results:
    - Cepstral smoothing: robust to BLIT harmonics, best for open vowels
      where F1 is well above F0
    - LPC (root-finding + peak-picking): best for close vowels where F1/F2
      are well-separated

    Both methods tend to underestimate F1 (cepstral blurs F1 toward F0,
    LPC over-resolves harmonics). Using the higher F1 from either method
    corrects this systematically.

    Args:
        samples: Audio samples as numpy array or list (int16 or float)
        sample_rate: Sample rate in Hz
        num_formants: Number of formants to extract (default 4)
        lpc_order: LPC order (default: sample_rate/1700)

    Returns:
        List of (frequency, bandwidth) tuples, sorted by frequency.
        May return fewer than num_formants if extraction fails.
    """
    samples = np.asarray(samples, dtype=np.float64)

    # Method 1: Cepstral envelope (robust to BLIT harmonics)
    smooth_formants = _formants_from_smoothed_spectrum(samples, sample_rate, num_formants)

    # Method 1b: Harmonic interpolation (handles harmonic sampling bias)
    interp_formants = _formants_from_harmonic_interp(samples, sample_rate, num_formants)

    # Method 1c: Parametric F1 fit (source tilt + resonance model)
    param_f1 = _f1_from_parametric_fit(samples, sample_rate)
    param_formants = [param_f1] if param_f1 is not None else []

    # Method 2: LPC root-finding + peak-picking at full sample rate
    poly, order = _get_lpc_coefficients(samples, sample_rate, lpc_order)
    lpc_formants = []
    if poly is not None:
        root_formants = _formants_from_roots(poly, sample_rate, num_formants)
        peak_formants = _formants_from_peaks(poly, sample_rate, num_formants)
        lpc_formants = peak_formants if len(peak_formants) > len(root_formants) else root_formants

    # Method 3: Downsampled LPC (better harmonic averaging at lower rate)
    ds_formants = []
    if sample_rate > 24000 and len(samples) > 200:
        from scipy.signal import decimate
        factor = sample_rate // 22050
        if factor >= 2:
            ds_samples = decimate(samples, factor, ftype='iir', zero_phase=True)
            ds_rate = sample_rate / factor
            ds_poly, _ = _get_lpc_coefficients(ds_samples, ds_rate, lpc_order)
            if ds_poly is not None:
                ds_roots = _formants_from_roots(ds_poly, ds_rate, num_formants)
                ds_peaks = _formants_from_peaks(ds_poly, ds_rate, num_formants)
                ds_formants = ds_peaks if len(ds_peaks) > len(ds_roots) else ds_roots

    # Collect all methods that found at least 1 formant
    all_methods = [(f, m) for f, m in [
        (smooth_formants, 'cep'), (interp_formants, 'interp'),
        (param_formants, 'param'), (lpc_formants, 'lpc'), (ds_formants, 'ds')
    ] if f]

    if not all_methods:
        return []
    if len(all_methods) == 1:
        return all_methods[0][0]

    # Pick the best F1 across methods — corrects systematic underestimation.
    # Cap at 1000 Hz to avoid selecting a method that misidentified F2 as F1.
    f1_ceiling = 1000
    eligible = [(f, m) for f, m in all_methods if f[0][0] <= f1_ceiling]
    if not eligible:
        eligible = all_methods
    best_f1_entry = max(eligible, key=lambda x: x[0][0][0])
    best_f1 = best_f1_entry[0][0]  # (freq, bw) tuple

    # Pick the method with the most formants for F2, F3, etc.
    most_complete = max(all_methods, key=lambda x: len(x[0]))
    base_formants = most_complete[0]

    # If the best-F1 method already has enough formants, use it directly
    if len(best_f1_entry[0]) >= num_formants:
        return best_f1_entry[0][:num_formants]

    # Construct: best F1 + higher formants from most-complete method
    result = [best_f1]
    for f, bw in base_formants:
        if f > best_f1[0] * 1.05 and len(result) < num_formants:
            result.append((f, bw))

    if len(result) >= num_formants:
        return result[:num_formants]

    # Fallback: return whichever method found the most formants
    return base_formants[:num_formants]


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


def estimate_hf_energy_ratio(samples, sample_rate, cutoff_hz=4000):
    """Estimate the ratio of energy above a cutoff frequency to total energy.

    Uses FFT with Hamming window. A higher ratio means a brighter sound.

    Args:
        samples: Audio samples
        sample_rate: Sample rate in Hz
        cutoff_hz: Frequency cutoff in Hz (default 4000)

    Returns:
        Ratio of HF energy to total energy (0.0-1.0, higher = brighter).
    """
    samples = np.asarray(samples, dtype=np.float64)

    if len(samples) < 50:
        return 0.0

    # Remove DC offset
    samples = samples - np.mean(samples)

    # Apply Hamming window
    windowed = samples * hamming(len(samples))

    # Compute power spectrum
    spectrum = np.abs(np.fft.rfft(windowed)) ** 2
    freqs = np.fft.rfftfreq(len(windowed), 1.0 / sample_rate)

    total_energy = np.sum(spectrum)
    if total_energy <= 0:
        return 0.0

    hf_mask = freqs >= cutoff_hz
    hf_energy = np.sum(spectrum[hf_mask])

    return float(hf_energy / total_energy)


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
