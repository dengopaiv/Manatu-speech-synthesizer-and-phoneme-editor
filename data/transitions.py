# Coarticulation Module for NVSpeechPlayer
# Implements Klatt locus equations and context-dependent transitions
#
# References:
# - Klatt 1980: Software for a cascade/parallel formant synthesizer
# - Klatt 1987: Review of text-to-speech conversion for English
# - Agrawal & Stevens 1992: KLSYN88 Hindi consonant synthesis

# Vowel classification by articulatory features
# Used for context-dependent locus selection
VOWEL_CLASSES = {
    '+FRONT': ['i', 'ɪ', 'e', 'ɛ', 'æ', 'y', 'ʏ', 'ø', 'œ', 'ɶ'],
    '+ROUND': ['u', 'ʊ', 'o', 'ɔ', 'y', 'ʏ', 'ø', 'œ', 'ɶ'],
    '-FRONT,-ROUND': ['ə', 'ʌ', 'ɑ', 'a', 'ɐ', 'ɨ', 'ʉ', 'ɜ', 'ɘ'],
}

# Transition durations by phoneme class pair (milliseconds)
# Based on acoustic phonetics literature
TRANSITION_DURATIONS = {
    # Consonant -> Vowel (CV)
    ('stop', 'vowel'): 40,       # Rapid release into vowel
    ('fricative', 'vowel'): 50,  # Slower due to constriction release
    ('nasal', 'vowel'): 35,      # Moderate, velic lowering
    ('liquid', 'vowel'): 25,     # Fast, already vowel-like
    ('semivowel', 'vowel'): 30,  # Glide transition

    # Vowel -> Consonant (VC) - generally slower
    ('vowel', 'stop'): 50,       # Closure formation
    ('vowel', 'fricative'): 45,  # Constriction formation
    ('vowel', 'nasal'): 40,      # Velic raising
    ('vowel', 'liquid'): 35,
    ('vowel', 'semivowel'): 40,

    # Vowel -> Vowel (VV)
    ('vowel', 'vowel'): 60,      # Diphthong-like, gradual

    # Consonant clusters
    ('stop', 'liquid'): 20,      # Rapid cluster
    ('fricative', 'liquid'): 25,
    ('nasal', 'stop'): 15,       # Pre-nasalized
    ('liquid', 'stop'): 20,

    # Default fallback
    'default': 20,
}

# F2 locus frequencies by consonant place (Hz)
# These are the "target" F2 values consonants pull vowels toward
# From Klatt 1987 and acoustic phonetics literature
F2_LOCUS = {
    'bilabial': 900,    # p, b, m - low F2 locus
    'labiodental': 1100,  # f, v
    'dental': 1400,     # θ, ð
    'alveolar': 1700,   # t, d, n, s, z, l
    'postalveolar': 2000,  # ʃ, ʒ, tʃ, dʒ
    'retroflex': 1800,  # ʈ, ɖ, ɳ (from Agrawal 1992)
    'palatal': 2300,    # ɲ, ç, j
    'velar': 1500,      # k, g, ŋ - varies with vowel context
    'uvular': 1200,     # q, χ, ʁ
    'pharyngeal': 1000, # ħ, ʕ
    'glottal': None,    # h, ʔ - no locus effect
}

# Map phoneme symbols to place of articulation
PHONEME_PLACE = {
    # Bilabials
    'p': 'bilabial', 'b': 'bilabial', 'm': 'bilabial',
    'ɸ': 'bilabial', 'β': 'bilabial',
    # Labiodentals
    'f': 'labiodental', 'v': 'labiodental', 'ɱ': 'labiodental',
    'ʋ': 'labiodental', 'ⱱ': 'labiodental',
    # Dentals
    'θ': 'dental', 'ð': 'dental',
    # Alveolars
    't': 'alveolar', 'd': 'alveolar', 'n': 'alveolar',
    's': 'alveolar', 'z': 'alveolar', 'l': 'alveolar',
    'ɾ': 'alveolar', 'r': 'alveolar', 'ɹ': 'alveolar',
    'ɬ': 'alveolar', 'ɮ': 'alveolar',
    # Postalveolars
    'ʃ': 'postalveolar', 'ʒ': 'postalveolar',
    'tʃ': 'postalveolar', 'dʒ': 'postalveolar',
    't͡ʃ': 'postalveolar', 'd͡ʒ': 'postalveolar',
    # Retroflexes
    'ʈ': 'retroflex', 'ɖ': 'retroflex', 'ɳ': 'retroflex',
    'ʂ': 'retroflex', 'ʐ': 'retroflex', 'ɭ': 'retroflex',
    'ɻ': 'retroflex', 'ɽ': 'retroflex',
    # Palatals
    'c': 'palatal', 'ɟ': 'palatal', 'ɲ': 'palatal',
    'ç': 'palatal', 'ʝ': 'palatal', 'j': 'palatal',
    'ʎ': 'palatal',
    # Velars
    'k': 'velar', 'g': 'velar', 'ɡ': 'velar', 'ŋ': 'velar',
    'x': 'velar', 'ɣ': 'velar', 'w': 'velar',
    'ʟ': 'velar', 'ɰ': 'velar',
    # Uvulars
    'q': 'uvular', 'ɢ': 'uvular', 'ɴ': 'uvular',
    'χ': 'uvular', 'ʁ': 'uvular',
    # Pharyngeals
    'ħ': 'pharyngeal', 'ʕ': 'pharyngeal',
    # Glottals
    'h': 'glottal', 'ʔ': 'glottal', 'ɦ': 'glottal',
}


def get_vowel_class(vowel_symbol):
    """
    Classify vowel for context-dependent locus selection.

    Returns: '+FRONT', '+ROUND', or '-FRONT,-ROUND'
    """
    for cls, vowels in VOWEL_CLASSES.items():
        if vowel_symbol in vowels:
            return cls
    return '-FRONT,-ROUND'  # Default for unknown vowels


def get_phoneme_class(phoneme):
    """
    Return phoneme class for transition duration lookup.

    Args:
        phoneme: dict with phoneme properties

    Returns:
        str: 'stop', 'nasal', 'liquid', 'semivowel', 'fricative', 'vowel', or 'other'
    """
    if phoneme.get('_isStop'):
        return 'stop'
    if phoneme.get('_isNasal'):
        return 'nasal'
    if phoneme.get('_isLiquid'):
        return 'liquid'
    if phoneme.get('_isSemivowel'):
        return 'semivowel'
    if phoneme.get('_isVowel'):
        return 'vowel'
    if phoneme.get('_isAfricate'):
        return 'stop'  # Treat affricates like stops for transitions
    # Fricatives don't have a dedicated flag, detect by frication amplitude
    if phoneme.get('fricationAmplitude', 0) > 0:
        return 'fricative'
    return 'other'


def get_consonant_place(phoneme):
    """
    Get place of articulation for a consonant phoneme.

    Args:
        phoneme: dict with '_char' key

    Returns:
        str: place name or None
    """
    symbol = phoneme.get('_char', '')
    if not symbol:
        return None
    return PHONEME_PLACE.get(symbol)


def calculate_formant_onset(consonant, vowel, k=0.75):
    """
    Apply Klatt locus equation to calculate vowel onset formants.

    The locus equation models coarticulation:
        F_onset = F_locus + k * (F_vowel - F_locus)

    Where k is the "extent of undershoot" (typically 0.7-0.8).
    k=0.75 means the vowel formant starts 75% of the way from
    the consonant locus toward the vowel target.

    Args:
        consonant: dict with consonant parameters
        vowel: dict with vowel parameters
        k: undershoot factor (0.0 = at locus, 1.0 = at vowel target)

    Returns:
        dict: onset formant values with '_onset_' prefix
    """
    onset = {}

    # Get consonant place for locus lookup
    place = get_consonant_place(consonant)
    if not place or place == 'glottal':
        # Glottals don't affect formant transitions
        return onset

    # Get F2 locus for this place
    f2_locus = F2_LOCUS.get(place)
    if not f2_locus:
        return onset

    # Calculate F2 onset
    vowel_f2 = vowel.get('cf2', 0)
    if vowel_f2:
        onset_f2 = f2_locus + k * (vowel_f2 - f2_locus)
        onset['_onset_cf2'] = onset_f2

    # F3 is less affected but still shows coarticulation
    # Use consonant's F3 as pseudo-locus
    consonant_f3 = consonant.get('cf3', 0)
    vowel_f3 = vowel.get('cf3', 0)
    if consonant_f3 and vowel_f3:
        # F3 transitions are typically faster (higher k)
        onset_f3 = consonant_f3 + 0.85 * (vowel_f3 - consonant_f3)
        onset['_onset_cf3'] = onset_f3

    return onset


def get_transition_duration(from_phoneme, to_phoneme, speed=1.0):
    """
    Get fade duration based on phoneme class pair.

    Args:
        from_phoneme: previous phoneme dict
        to_phoneme: current phoneme dict
        speed: speech rate multiplier

    Returns:
        float: transition duration in milliseconds (scaled by speed)
    """
    from_class = get_phoneme_class(from_phoneme)
    to_class = get_phoneme_class(to_phoneme)

    key = (from_class, to_class)
    duration = TRANSITION_DURATIONS.get(key, TRANSITION_DURATIONS['default'])

    return duration / speed


def apply_coarticulation(phonemeList, baseSpeed=1.0):
    """
    Apply coarticulation effects to a phoneme sequence.

    This function modifies phonemes in place:
    1. CV transitions: Calculates onset formants using locus equation
    2. Transition durations: Adjusts _fadeDuration based on phoneme classes

    Should be called after calculatePhonemeTimes() and before pitch calculation.

    Args:
        phonemeList: list of phoneme dicts (modified in place)
        baseSpeed: speech rate multiplier
    """
    final_index = len(phonemeList) - 1

    for i, phoneme in enumerate(phonemeList):
        # Skip silence markers
        if phoneme.get('_silence'):
            continue

        prev = phonemeList[i - 1] if i > 0 else None
        # next_ph = phonemeList[i + 1] if i < final_index else None  # For future use

        # Skip if no previous phoneme or previous is silence
        if not prev or prev.get('_silence'):
            continue

        # CV transition: Apply locus equation to vowel onset
        if phoneme.get('_isVowel'):
            # Find the consonant for locus calculation
            # Look past post-stop aspiration to find the actual stop
            consonant = prev
            if prev.get('_postStopAspiration') and i >= 2:
                consonant = phonemeList[i - 2]

            prev_class = get_phoneme_class(consonant)
            # Apply coarticulation for obstruent -> vowel transitions
            if prev_class in ('stop', 'fricative', 'nasal'):
                onset = calculate_formant_onset(consonant, phoneme)
                phoneme.update(onset)

            # Retroflex consonants have SLOWEST F2 transition (Agrawal Table IV)
            consonant_char = consonant.get('_char', '')
            if consonant_char in ['ʈ', 'ɖ', 'ɳ', 'ʂ', 'ʐ', 'ɭ']:
                phoneme['_fadeDuration'] = 60 / baseSpeed
                continue  # Skip normal duration calculation

        # Update transition duration based on phoneme class pair
        duration = get_transition_duration(prev, phoneme, baseSpeed)
        phoneme['_fadeDuration'] = duration
