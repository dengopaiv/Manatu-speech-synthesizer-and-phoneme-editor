"""
Phoneme Editor Constants

Contains all constant definitions for the phoneme parameter editor:
- Parameter group definitions with ranges
- Scaling parameter sets
- Default values
- IPA descriptions
"""

# Parameters that should NOT be saved with phoneme presets
# These are prosody/speaker parameters, not phoneme-intrinsic properties
PROSODY_PARAMS = {
    'voicePitch',           # Set by intonation/tone system
    'midVoicePitch',        # Set by tone contour system
    'endVoicePitch',        # Set by intonation/tone system
    'vibratoPitchOffset',   # Speaker characteristic
    'vibratoSpeed',         # Speaker characteristic
    'preFormantGain',       # Output level, not phoneme property
    'outputGain',           # Output level, not phoneme property
}

# Parameter definitions with ranges and descriptions
PARAM_GROUPS = {
    'Pitch & Voicing': [
        ('voicePitch', 50, 500, 120, 'Hz', 'Fundamental frequency'),
        ('midVoicePitch', 0, 500, 0, 'Hz', 'Mid pitch (0=linear, >0=contour tone)'),
        ('endVoicePitch', 50, 500, 120, 'Hz', 'End pitch (for contours)'),
        ('vibratoPitchOffset', 0, 100, 12, '%', 'Vibrato depth (0-100%)'),
        ('vibratoSpeed', 0, 100, 55, 'x0.1Hz', 'Vibrato rate'),
        ('glottalOpenQuotient', 10, 99, 50, '%', 'Glottis open time'),
    ],
    'Amplitudes': [
        ('voiceAmplitude', 0, 100, 100, '%', 'Voiced sound level'),
        ('voiceTurbulenceAmplitude', 0, 100, 0, '%', 'Breathiness'),
        ('aspirationAmplitude', 0, 100, 0, '%', 'Aspiration noise'),
        ('aspirationFilterFreq', 0, 6000, 0, 'Hz', 'Aspiration bandpass (0=white)'),
        ('aspirationFilterBw', 100, 4000, 2000, 'Hz', 'Aspiration filter width'),
        ('fricationAmplitude', 0, 100, 0, '%', 'Frication noise'),
        ('noiseFilterFreq', 0, 8000, 0, 'Hz', 'Frication bandpass (0=white)'),
        ('noiseFilterBw', 100, 4000, 1000, 'Hz', 'Frication filter width'),
        ('preFormantGain', 0, 200, 100, '%', 'Pre-resonator gain'),
        ('outputGain', 0, 200, 100, '%', 'Master volume'),
    ],
    'Cascade Formants (F1-F3)': [
        ('cf1', 150, 1000, 500, 'Hz', 'F1 frequency'),
        ('cb1', 40, 500, 60, 'Hz', 'F1 bandwidth'),
        ('cf2', 500, 2800, 1500, 'Hz', 'F2 frequency'),
        ('cb2', 40, 500, 90, 'Hz', 'F2 bandwidth'),
        ('cf3', 1300, 3800, 2500, 'Hz', 'F3 frequency'),
        ('cb3', 40, 500, 150, 'Hz', 'F3 bandwidth'),
    ],
    'Cascade Formants (F4-F6)': [
        ('cf4', 2500, 4800, 3500, 'Hz', 'F4 frequency'),
        ('cb4', 100, 500, 250, 'Hz', 'F4 bandwidth'),
        ('cf5', 3500, 5000, 4500, 'Hz', 'F5 frequency'),
        ('cb5', 150, 700, 200, 'Hz', 'F5 bandwidth'),
        ('cf6', 4000, 5500, 4900, 'Hz', 'F6 frequency'),
        ('cb6', 200, 2000, 1000, 'Hz', 'F6 bandwidth'),
    ],
    'Nasal Formants': [
        ('cfN0', 200, 2500, 450, 'Hz', 'Nasal zero ([m]1000, [n]1400, [ŋ]2000)'),
        ('cbN0', 50, 500, 100, 'Hz', 'Nasal zero bandwidth'),
        ('cfNP', 200, 500, 270, 'Hz', 'Nasal pole frequency'),
        ('cbNP', 50, 500, 100, 'Hz', 'Nasal pole bandwidth'),
        ('caNP', 0, 100, 0, '%', 'Nasal coupling'),
    ],
    'Parallel Formants (F1-F3)': [
        ('pf1', 150, 1000, 500, 'Hz', 'Parallel F1 freq'),
        ('pb1', 40, 500, 60, 'Hz', 'Parallel F1 BW'),
        ('pa1', 0, 100, 0, '%', 'Parallel F1 amp'),
        ('pf2', 500, 2800, 1500, 'Hz', 'Parallel F2 freq'),
        ('pb2', 40, 500, 90, 'Hz', 'Parallel F2 BW'),
        ('pa2', 0, 100, 0, '%', 'Parallel F2 amp'),
        ('pf3', 1300, 3800, 2500, 'Hz', 'Parallel F3 freq'),
        ('pb3', 40, 500, 150, 'Hz', 'Parallel F3 BW'),
        ('pa3', 0, 100, 0, '%', 'Parallel F3 amp'),
    ],
    'Parallel Formants (F4-F6)': [
        ('pf4', 2500, 4800, 3500, 'Hz', 'Parallel F4 freq'),
        ('pb4', 100, 500, 250, 'Hz', 'Parallel F4 BW'),
        ('pa4', 0, 100, 0, '%', 'Parallel F4 amp'),
        ('pf5', 3500, 5000, 4500, 'Hz', 'Parallel F5 freq'),
        ('pb5', 150, 700, 200, 'Hz', 'Parallel F5 BW'),
        ('pa5', 0, 100, 0, '%', 'Parallel F5 amp'),
        ('pf6', 4000, 5500, 4900, 'Hz', 'Parallel F6 freq'),
        ('pb6', 200, 2000, 1000, 'Hz', 'Parallel F6 BW'),
        ('pa6', 0, 100, 0, '%', 'Parallel F6 amp'),
    ],
    'Parallel Bypass': [
        ('parallelBypass', 0, 105, 0, '%', 'Unfiltered noise bypass'),
    ],
    'Voice Quality (KLSYN88)': [
        ('spectralTilt', 0, 41, 0, 'dB', 'High-freq attenuation (breathy)'),
        ('flutter', 0, 100, 25, '%', 'Natural pitch jitter'),
        ('openQuotientShape', 0, 100, 50, '%', 'Glottal closing curve'),
        ('speedQuotient', 50, 200, 100, '%', 'Opening/closing asymmetry'),
        ('diplophonia', 0, 100, 0, '%', 'Period alternation (creaky)'),
        ('lfRd', 0, 27, 0, 'x0.1', 'LF model Rd (0=legacy, 3-27=tense-breathy)'),
    ],
    'Glottal Modulation': [
        ('deltaF1', 0, 100, 0, 'Hz', 'F1 increase during glottal open'),
        ('deltaB1', 0, 400, 0, 'Hz', 'B1 increase during glottal open'),
        ('sinusoidalVoicingAmplitude', 0, 100, 0, '%', 'Pure sine voicing (voicebars)'),
    ],
    'Tracheal Resonances': [
        ('ftpFreq1', 0, 1500, 0, 'Hz', 'Tracheal pole 1 (~600-750 Hz)'),
        ('ftpBw1', 40, 500, 100, 'Hz', 'Tracheal pole 1 bandwidth'),
        ('ftzFreq1', 0, 1500, 0, 'Hz', 'Tracheal zero 1 (0=off)'),
        ('ftzBw1', 40, 500, 100, 'Hz', 'Tracheal zero 1 bandwidth'),
        ('ftpFreq2', 0, 2500, 0, 'Hz', 'Tracheal pole 2 (~1550-1650 Hz)'),
        ('ftpBw2', 40, 500, 100, 'Hz', 'Tracheal pole 2 bandwidth'),
        ('ftzFreq2', 0, 2500, 0, 'Hz', 'Tracheal zero 2 (0=off)'),
        ('ftzBw2', 40, 500, 200, 'Hz', 'Tracheal zero 2 bandwidth'),
    ],
    'Stop Burst': [
        ('burstAmplitude', 0, 100, 0, '%', 'Burst transient intensity'),
        ('burstDuration', 0, 100, 25, '%', 'Burst length (5-20ms)'),
    ],
}

# Parameters that use percentage scaling (0-100 maps to 0.0-1.0)
PERCENT_PARAMS = {
    'voiceAmplitude', 'voiceTurbulenceAmplitude', 'aspirationAmplitude',
    'fricationAmplitude', 'caNP', 'pa1', 'pa2', 'pa3', 'pa4', 'pa5', 'pa6',
    'glottalOpenQuotient', 'vibratoPitchOffset',
    'flutter', 'openQuotientShape', 'speedQuotient', 'diplophonia',
    'burstAmplitude', 'burstDuration', 'sinusoidalVoicingAmplitude',
}

# Parameters that use percentage scaling (0-200 maps to 0.0-2.0)
GAIN_PARAMS = {'preFormantGain', 'outputGain'}

# Parameters that need /10 scaling
TENTH_PARAMS = {'vibratoSpeed', 'parallelBypass', 'lfRd'}

# KLSYN88 default values
KLSYN88_DEFAULTS = {
    'spectralTilt': 0,
    'flutter': 0.25,
    'openQuotientShape': 0.5,
    'speedQuotient': 1.0,
    'diplophonia': 0,
    'lfRd': 0,
    'deltaF1': 0,
    'deltaB1': 0,
    'sinusoidalVoicingAmplitude': 0,
    'ftpFreq1': 0,
    'ftpBw1': 100,
    'ftzFreq1': 0,
    'ftzBw1': 100,
    'ftpFreq2': 0,
    'ftpBw2': 100,
    'ftzFreq2': 0,
    'ftzBw2': 200,
    'burstAmplitude': 0,
    'burstDuration': 0.25,
    'aspirationFilterFreq': 0,
    'aspirationFilterBw': 2000,
    'noiseFilterFreq': 0,
    'noiseFilterBw': 1000,
}

# IPA descriptions
IPA_DESCRIPTIONS = {
    'i': 'close front unrounded', 'y': 'close front rounded',
    'ɨ': 'close central unrounded', 'ʉ': 'close central rounded',
    'ɯ': 'close back unrounded', 'u': 'close back rounded',
    'ɪ': 'near-close front unrounded', 'ʏ': 'near-close front rounded',
    'ʊ': 'near-close back rounded',
    'e': 'close-mid front unrounded', 'ø': 'close-mid front rounded',
    'ɘ': 'close-mid central unrounded', 'ɵ': 'close-mid central rounded',
    'ɤ': 'close-mid back unrounded', 'o': 'close-mid back rounded',
    'ə': 'mid central (schwa)',
    'ɛ': 'open-mid front unrounded', 'œ': 'open-mid front rounded',
    'ɜ': 'open-mid central unrounded', 'ɞ': 'open-mid central rounded',
    'ʌ': 'open-mid back unrounded', 'ɔ': 'open-mid back rounded',
    'æ': 'near-open front unrounded', 'ɐ': 'near-open central',
    'a': 'open front unrounded', 'ɶ': 'open front rounded',
    'ä': 'open central unrounded', 'ɑ': 'open back unrounded', 'ɒ': 'open back rounded',
    'ɝ': 'r-colored mid central', 'ɚ': 'r-colored schwa',
    'p': 'voiceless bilabial plosive', 'b': 'voiced bilabial plosive',
    't': 'voiceless alveolar plosive', 'd': 'voiced alveolar plosive',
    'k': 'voiceless velar plosive', 'g': 'voiced velar plosive',
    'm': 'bilabial nasal', 'n': 'alveolar nasal', 'ŋ': 'velar nasal',
    'f': 'voiceless labiodental fricative', 'v': 'voiced labiodental fricative',
    'θ': 'voiceless dental fricative', 'ð': 'voiced dental fricative',
    's': 'voiceless alveolar fricative', 'z': 'voiced alveolar fricative',
    'ʃ': 'voiceless postalveolar fricative', 'ʒ': 'voiced postalveolar fricative',
    'h': 'voiceless glottal fricative',
    'l': 'alveolar lateral approximant', 'ɹ': 'alveolar approximant',
    'j': 'palatal approximant', 'w': 'labial-velar approximant',
}

# Duration defaults for test sequences
SEQUENCE_DURATIONS = {'vowel': 250, 'consonant': 100, 'default': 150}
