# -*- coding: utf-8 -*-
"""
Phoneme parameter calculations module.

Automatically derives new synthesis parameters from existing phoneme data
using acoustic formulas from Klatt literature (Klatt 1980, 1990).

New parameters calculated:
- deltaF1, deltaB1: Pitch-synchronous F1/B1 modulation
- ftzFreq2, ftzBw2: Second tracheal zero
- sinusoidalVoicingAmplitude: Pure sine voicing (voicebars)
- aspirationFilterFreq, aspirationFilterBw: Aspiration noise shaping
"""


def calc_deltaF1(phoneme_data):
    """
    Calculate pitch-synchronous F1 frequency increase during glottal open phase.

    Based on Klatt 1990 Table XII: DF1 range 0-100 Hz.
    Subglottal pressure couples to F1 during glottal opening, raising frequency.

    Args:
        phoneme_data: Dictionary with phoneme parameters

    Returns:
        float: deltaF1 in Hz (0-100 range)
    """
    cf1 = phoneme_data.get('cf1', 500)

    if phoneme_data.get('_isNasal'):
        # Nasals: stronger subglottal coupling (5% of F1, max 20 Hz)
        return min(20, cf1 * 0.05)
    elif phoneme_data.get('_isVowel'):
        # Vowels: moderate coupling (2% of F1, max 10 Hz)
        return min(10, cf1 * 0.02)
    elif phoneme_data.get('_isLiquid'):
        # Liquids: similar to vowels (3% of F1, max 12 Hz)
        return min(12, cf1 * 0.03)
    elif phoneme_data.get('_isStop'):
        # Stops: minimal during closure (1% of F1)
        return cf1 * 0.01
    else:
        # Fricatives/other: minimal (1% of F1)
        return cf1 * 0.01


def calc_deltaB1(phoneme_data, deltaF1):
    """
    Calculate pitch-synchronous F1 bandwidth increase during glottal open phase.

    Based on Klatt 1990 Table XII: DB1 range 0-400 Hz.
    Bandwidth effect is typically 3-4x the frequency effect.

    Args:
        phoneme_data: Dictionary with phoneme parameters
        deltaF1: Previously calculated deltaF1 value

    Returns:
        float: deltaB1 in Hz (0-400 range)
    """
    if phoneme_data.get('_isNasal'):
        # Nasals: strongest bandwidth modulation
        return min(400, deltaF1 * 4)
    elif phoneme_data.get('_isVowel'):
        # Vowels: moderate bandwidth modulation
        return min(400, deltaF1 * 3)
    elif phoneme_data.get('_isLiquid'):
        # Liquids: similar to vowels
        return min(400, deltaF1 * 3.5)
    else:
        # Fricatives, stops, other: weaker effect
        return min(400, deltaF1 * 2)


def calc_ftzFreq2(phoneme_data):
    """
    Calculate second tracheal zero frequency.

    Based on Klatt 1990 Table VII: tracheal zeros at ~600, ~1300-1400, ~2100 Hz.
    Only active when second tracheal pole (ftpFreq2) is active.

    Args:
        phoneme_data: Dictionary with phoneme parameters

    Returns:
        float: ftzFreq2 in Hz (0 = disabled)
    """
    ftpFreq2 = phoneme_data.get('ftpFreq2', 0)

    # Only active if second tracheal pole is active
    if ftpFreq2 > 0:
        # Zero slightly below pole frequency (Klatt 1990: ~1300-1400 Hz)
        return max(0, ftpFreq2 - 150)
    return 0


def calc_ftzBw2(phoneme_data):
    """
    Calculate second tracheal zero bandwidth.

    Based on Klatt 1990 Table XII: typical 125-180 Hz.

    Args:
        phoneme_data: Dictionary with phoneme parameters

    Returns:
        float: ftzBw2 in Hz
    """
    ftzFreq2 = calc_ftzFreq2(phoneme_data)
    if ftzFreq2 > 0:
        return 150  # Klatt 1990: 125-180 Hz typical
    return 200  # Default when disabled


def calc_sinusoidalVoicing(phoneme_data):
    """
    Calculate sinusoidal voicing amplitude (AVS parameter).

    Pure sine wave at F0 frequency for voicebars in voiced obstruents.
    Based on Klatt 1980 Table I: AVS range 0-80 dB.

    Args:
        phoneme_data: Dictionary with phoneme parameters

    Returns:
        float: sinusoidalVoicingAmplitude (0-1 normalized)
    """
    is_voiced = phoneme_data.get('_isVoiced', False)

    if not is_voiced:
        return 0.0

    # Voiced fricatives: strong voicebar component
    frication = phoneme_data.get('fricationAmplitude', 0)
    if frication > 0.5:
        return 0.35  # Prominent voicebar for /v/, /z/, /ʒ/, etc.

    # Voiced stops during closure: mild voicebar
    if phoneme_data.get('_isStop'):
        return 0.25  # Voice bar visible in spectrogram

    # Vowels, nasals, liquids: use complex LF glottal model instead
    return 0.0


def calc_aspirationFilterFreq(phoneme_data):
    """
    Calculate aspiration bandpass filter center frequency.

    Shapes aspiration noise spectrum for more natural quality.
    Based on Stevens Acoustic Phonetics Ch.8 and Klatt 1990.

    Args:
        phoneme_data: Dictionary with phoneme parameters

    Returns:
        float: aspirationFilterFreq in Hz (0 = white noise)
    """
    aspiration = phoneme_data.get('aspirationAmplitude', 0)

    if aspiration <= 0:
        return 0  # No aspiration = no filter needed

    # Voiceless stops: use white noise (unfiltered)
    if phoneme_data.get('_isStop') and not phoneme_data.get('_isVoiced'):
        return 0

    # High aspiration (/h/, breathy voice): mid-frequency emphasis
    if aspiration > 0.3:
        return 1500  # Glottal aspiration spectral peak

    return 0  # Default: white noise


def calc_aspirationFilterBw(phoneme_data):
    """
    Calculate aspiration bandpass filter bandwidth.

    Args:
        phoneme_data: Dictionary with phoneme parameters

    Returns:
        float: aspirationFilterBw in Hz
    """
    freq = calc_aspirationFilterFreq(phoneme_data)
    if freq > 0:
        return 2000  # Broad filter for natural aspiration
    return 2000  # Default bandwidth


def update_phoneme_with_new_params(phoneme_data):
    """
    Add all new synthesis parameters to a phoneme dictionary.

    Calculates and adds:
    - deltaF1, deltaB1 (pitch-synchronous F1 modulation)
    - ftzFreq2, ftzBw2 (second tracheal zero)
    - sinusoidalVoicingAmplitude (voicebar component)
    - aspirationFilterFreq, aspirationFilterBw (aspiration shaping)

    Args:
        phoneme_data: Dictionary with existing phoneme parameters

    Returns:
        dict: Updated phoneme_data with new parameters added
    """
    # Calculate deltaF1 first (deltaB1 depends on it)
    deltaF1 = calc_deltaF1(phoneme_data)

    # Add all new parameters
    phoneme_data['deltaF1'] = deltaF1
    phoneme_data['deltaB1'] = calc_deltaB1(phoneme_data, deltaF1)
    phoneme_data['ftzFreq2'] = calc_ftzFreq2(phoneme_data)
    phoneme_data['ftzBw2'] = calc_ftzBw2(phoneme_data)
    phoneme_data['sinusoidalVoicingAmplitude'] = calc_sinusoidalVoicing(phoneme_data)
    phoneme_data['aspirationFilterFreq'] = calc_aspirationFilterFreq(phoneme_data)
    phoneme_data['aspirationFilterBw'] = calc_aspirationFilterBw(phoneme_data)

    return phoneme_data


def update_all_phonemes(phoneme_dict):
    """
    Update all phonemes in a dictionary with new parameters.

    Args:
        phoneme_dict: Dictionary mapping IPA symbols to parameter dicts

    Returns:
        dict: Updated dictionary with new parameters for all phonemes
    """
    for ipa, params in phoneme_dict.items():
        if isinstance(params, dict):
            update_phoneme_with_new_params(params)
    return phoneme_dict
