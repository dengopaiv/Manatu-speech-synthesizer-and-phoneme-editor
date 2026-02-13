#!/usr/bin/env python3
"""
IPA Keyboard Data for Conlang Synthesizer

Provides Alt+key mappings for typing IPA symbols with full accessibility support.
Each symbol includes a description for screen reader announcements.

Usage:
    Alt + letter = insert IPA symbol
    Multiple rapid presses (within 500ms) cycle through related symbols
"""

# Each entry: (symbol, description)
# Description format: "IPA name (manner/place if consonant, quality if vowel)"

IPA_VOWELS = {
    'a': [
        ('æ', 'ash, near-open front unrounded'),
        ('ɑ', 'script a, open back unrounded'),
        ('ɐ', 'turned a, near-open central'),
        ('a', 'lowercase a, open front unrounded'),
        ('ɒ', 'turned script a, open back rounded'),
    ],
    'e': [
        ('ɛ', 'epsilon, open-mid front unrounded'),
        ('ə', 'schwa, mid central'),
        ('ɜ', 'reversed epsilon, open-mid central unrounded'),
        ('e', 'lowercase e, close-mid front unrounded'),
        ('ɘ', 'reversed e, close-mid central unrounded'),
        ('ɞ', 'closed reversed epsilon, open-mid central rounded'),
    ],
    'i': [
        ('ɪ', 'small capital i, near-close near-front unrounded'),
        ('ɨ', 'barred i, close central unrounded'),
        ('i', 'lowercase i, close front unrounded'),
        ('ɯ', 'turned m, close back unrounded'),
    ],
    'o': [
        ('ɔ', 'open o, open-mid back rounded'),
        ('ɒ', 'turned script a, open back rounded'),
        ('o', 'lowercase o, close-mid back rounded'),
        ('ø', 'slashed o, close-mid front rounded'),
        ('œ', 'o-e ligature, open-mid front rounded'),
        ('ɵ', 'barred o, close-mid central rounded'),
    ],
    'u': [
        ('ʊ', 'upsilon, near-close near-back rounded'),
        ('ʌ', 'turned v, open-mid back unrounded'),
        ('u', 'lowercase u, close back rounded'),
        ('ʉ', 'barred u, close central rounded'),
        ('ɤ', 'rams horns, close-mid back unrounded'),
    ],
    'y': [
        ('y', 'lowercase y, close front rounded'),
        ('ʏ', 'small capital y, near-close near-front rounded'),
    ],
}

IPA_CONSONANTS = {
    'b': [
        ('β', 'beta, voiced bilabial fricative'),
        ('ɓ', 'hooktop b, voiced bilabial implosive'),
        ('ʙ', 'small capital b, bilabial trill'),
        ('b', 'lowercase b, voiced bilabial plosive'),
    ],
    'c': [
        ('ç', 'c cedilla, voiceless palatal fricative'),
        ('ɕ', 'curly-tail c, voiceless alveolo-palatal fricative'),
        ('c', 'lowercase c, voiceless palatal plosive'),
        ('ɟ', 'barred dotless j, voiced palatal plosive'),
    ],
    'd': [
        ('ð', 'eth, voiced dental fricative'),
        ('ɖ', 'right-tail d, voiced retroflex plosive'),
        ('ɗ', 'hooktop d, voiced alveolar implosive'),
        ('d', 'lowercase d, voiced alveolar plosive'),
    ],
    'f': [
        ('ɸ', 'phi, voiceless bilabial fricative'),
        ('f', 'lowercase f, voiceless labiodental fricative'),
    ],
    'g': [
        ('ɡ', 'opentail g, voiced velar plosive'),
        ('ɣ', 'gamma, voiced velar fricative'),
        ('ɢ', 'small capital g, voiced uvular plosive'),
        ('ʛ', 'hooktop small capital g, voiced uvular implosive'),
        ('ɠ', 'hooktop g, voiced velar implosive'),
    ],
    'h': [
        ('ħ', 'barred h, voiceless pharyngeal fricative'),
        ('ɦ', 'hooktop h, voiced glottal fricative'),
        ('ʜ', 'small capital h, voiceless epiglottal fricative'),
        ('ɥ', 'turned h, labial-palatal approximant'),
        ('h', 'lowercase h, voiceless glottal fricative'),
    ],
    'j': [
        ('ʝ', 'curly-tail j, voiced palatal fricative'),
        ('ɟ', 'barred dotless j, voiced palatal plosive'),
        ('ʄ', 'hooktop barred dotless j, voiced palatal implosive'),
        ('j', 'lowercase j, palatal approximant'),
    ],
    'k': [
        ('k', 'lowercase k, voiceless velar plosive'),
        ('q', 'lowercase q, voiceless uvular plosive'),
    ],
    'l': [
        ('ɬ', 'belted l, voiceless alveolar lateral fricative'),
        ('ɮ', 'l-ezh ligature, voiced alveolar lateral fricative'),
        ('ɭ', 'right-tail l, retroflex lateral approximant'),
        ('ʎ', 'turned y, palatal lateral approximant'),
        ('ʟ', 'small capital l, velar lateral approximant'),
        ('l', 'lowercase l, alveolar lateral approximant'),
    ],
    'm': [
        ('ɱ', 'left-tail m, labiodental nasal'),
        ('m', 'lowercase m, bilabial nasal'),
    ],
    'n': [
        ('ŋ', 'eng, velar nasal'),
        ('ɲ', 'left-tail n, palatal nasal'),
        ('ɳ', 'right-tail n, retroflex nasal'),
        ('ɴ', 'small capital n, uvular nasal'),
        ('n', 'lowercase n, alveolar nasal'),
    ],
    'p': [
        ('p', 'lowercase p, voiceless bilabial plosive'),
        ('ɸ', 'phi, voiceless bilabial fricative'),
    ],
    'r': [
        ('ɹ', 'turned r, alveolar approximant'),
        ('ɾ', 'fish-hook r, alveolar tap'),
        ('ʁ', 'inverted small capital r, voiced uvular fricative'),
        ('ʀ', 'small capital r, uvular trill'),
        ('ɻ', 'turned r with right tail, retroflex approximant'),
        ('ɽ', 'right-tail r, retroflex flap'),
        ('r', 'lowercase r, alveolar trill'),
    ],
    's': [
        ('ʃ', 'esh, voiceless postalveolar fricative'),
        ('ʂ', 'right-tail s, voiceless retroflex fricative'),
        ('ɕ', 'curly-tail c, voiceless alveolo-palatal fricative'),
        ('s', 'lowercase s, voiceless alveolar fricative'),
    ],
    't': [
        ('θ', 'theta, voiceless dental fricative'),
        ('ʈ', 'right-tail t, voiceless retroflex plosive'),
        ('t', 'lowercase t, voiceless alveolar plosive'),
    ],
    'v': [
        ('ʋ', 'script v, labiodental approximant'),
        ('v', 'lowercase v, voiced labiodental fricative'),
        ('ⱱ', 'right-hook v, labiodental flap'),
    ],
    'w': [
        ('ʍ', 'turned w, voiceless labial-velar fricative'),
        ('w', 'lowercase w, labial-velar approximant'),
        ('ɰ', 'turned m with leg, velar approximant'),
    ],
    'x': [
        ('χ', 'chi, voiceless uvular fricative'),
        ('x', 'lowercase x, voiceless velar fricative'),
        ('ɧ', 'hooktop heng, voiceless palatal-velar fricative'),
    ],
    'z': [
        ('ʒ', 'ezh, voiced postalveolar fricative'),
        ('ʐ', 'right-tail z, voiced retroflex fricative'),
        ('ʑ', 'curly-tail z, voiced alveolo-palatal fricative'),
        ('z', 'lowercase z, voiced alveolar fricative'),
    ],
}

# Diacritics and suprasegmentals accessible via punctuation keys
IPA_PUNCTUATION = {
    "'": [
        ('ˈ', 'vertical stroke, primary stress'),
        ('ˌ', 'low vertical stroke, secondary stress'),
    ],
    ':': [
        ('ː', 'triangular colon, long'),
        ('ˑ', 'half triangular colon, half-long'),
    ],
    '?': [
        ('ʔ', 'glottal stop'),
        ('ʕ', 'reversed glottal stop, voiced pharyngeal fricative'),
        ('ʡ', 'barred glottal stop, epiglottal plosive'),
        ('ʢ', 'barred reversed glottal stop, voiced epiglottal fricative'),
    ],
    '!': [
        ('ǃ', 'exclamation mark click, postalveolar click'),
        ('ǀ', 'pipe, dental click'),
        ('ǁ', 'double pipe, alveolar lateral click'),
        ('ǂ', 'double-barred pipe, palatal click'),
    ],
}

# Tone marks via number keys
IPA_TONES = {
    '1': [
        ('˥', 'extra high tone letter'),
        ('\u0301', 'combining acute accent, high tone'),  # ́
    ],
    '2': [
        ('˦', 'high tone letter'),
    ],
    '3': [
        ('˧', 'mid tone letter'),
        ('\u0304', 'combining macron, mid tone'),  # ̄
    ],
    '4': [
        ('˨', 'low tone letter'),
    ],
    '5': [
        ('˩', 'extra low tone letter'),
        ('\u0300', 'combining grave accent, low tone'),  # ̀
    ],
    '6': [
        ('\u030C', 'combining caron, rising tone'),  # ̌
        ('˩˥', 'rising contour'),
    ],
    '7': [
        ('\u0302', 'combining circumflex, falling tone'),  # ̂
        ('˥˩', 'falling contour'),
    ],
    '8': [
        ('\u030B', 'combining double acute, extra high tone'),  # ̋
    ],
    '9': [
        ('\u030F', 'combining double grave, extra low tone'),  # ̏
    ],
    '0': [
        ('\u0303', 'combining tilde, nasalization'),  # ̃
        ('\u0330', 'combining tilde below, creaky voice'),  # ̰
    ],
}

# Special symbols via other keys
IPA_SPECIAL = {
    '.': [
        ('.', 'period, syllable break'),
        ('‿', 'undertie, linking'),
    ],
    '-': [
        ('‿', 'undertie, linking'),
        ('|', 'minor group break'),
        ('‖', 'major group break'),
    ],
    '^': [
        ('↗', 'global rise'),
        ('↘', 'global fall'),
    ],
    '[': [
        ('[', 'left bracket, phonetic transcription'),
    ],
    ']': [
        (']', 'right bracket, phonetic transcription'),
    ],
    '/': [
        ('/', 'slash, phonemic transcription'),
    ],
}

# Combine all mappings
ALL_MAPPINGS = {}
ALL_MAPPINGS.update(IPA_VOWELS)
ALL_MAPPINGS.update(IPA_CONSONANTS)
ALL_MAPPINGS.update(IPA_PUNCTUATION)
ALL_MAPPINGS.update(IPA_TONES)
ALL_MAPPINGS.update(IPA_SPECIAL)


def get_symbol_for_key(key, press_count=1):
    """
    Get the IPA symbol for a given key and press count.

    Args:
        key: The key pressed (lowercase letter or punctuation)
        press_count: How many times the key was pressed in rapid succession

    Returns:
        Tuple of (symbol, description) or None if no mapping exists
    """
    key = key.lower()
    if key not in ALL_MAPPINGS:
        return None

    symbols = ALL_MAPPINGS[key]
    index = (press_count - 1) % len(symbols)
    return symbols[index]


def get_all_symbols_for_key(key):
    """
    Get all IPA symbols mapped to a key.

    Args:
        key: The key to look up

    Returns:
        List of (symbol, description) tuples or empty list
    """
    key = key.lower()
    return ALL_MAPPINGS.get(key, [])


def get_help_text():
    """
    Generate accessible help text for all keyboard shortcuts.

    Returns:
        String with formatted help text
    """
    lines = []
    lines.append("IPA KEYBOARD SHORTCUTS")
    lines.append("=" * 50)
    lines.append("")
    lines.append("Press Alt + key to insert IPA symbols.")
    lines.append("Press the same key multiple times quickly to cycle through related symbols.")
    lines.append("")

    lines.append("VOWELS")
    lines.append("-" * 30)
    for key in sorted(IPA_VOWELS.keys()):
        symbols = IPA_VOWELS[key]
        sym_list = ", ".join(f"{s[0]} ({s[1].split(',')[0]})" for s in symbols)
        lines.append(f"Alt+{key.upper()}: {sym_list}")
    lines.append("")

    lines.append("CONSONANTS")
    lines.append("-" * 30)
    for key in sorted(IPA_CONSONANTS.keys()):
        symbols = IPA_CONSONANTS[key]
        sym_list = ", ".join(f"{s[0]} ({s[1].split(',')[0]})" for s in symbols)
        lines.append(f"Alt+{key.upper()}: {sym_list}")
    lines.append("")

    lines.append("STRESS AND LENGTH")
    lines.append("-" * 30)
    for key in ["'", ":"]:
        if key in IPA_PUNCTUATION:
            symbols = IPA_PUNCTUATION[key]
            sym_list = ", ".join(f"{s[0]} ({s[1]})" for s in symbols)
            lines.append(f"Alt+{key}: {sym_list}")
    lines.append("")

    lines.append("GLOTTALS AND CLICKS")
    lines.append("-" * 30)
    for key in ["?", "!"]:
        if key in IPA_PUNCTUATION:
            symbols = IPA_PUNCTUATION[key]
            sym_list = ", ".join(f"{s[0]} ({s[1].split(',')[0]})" for s in symbols)
            lines.append(f"Alt+{key}: {sym_list}")
    lines.append("")

    lines.append("TONE MARKS (Alt + number)")
    lines.append("-" * 30)
    lines.append("Alt+1: ˥ (extra high), acute accent")
    lines.append("Alt+2: ˦ (high)")
    lines.append("Alt+3: ˧ (mid), macron")
    lines.append("Alt+4: ˨ (low)")
    lines.append("Alt+5: ˩ (extra low), grave accent")
    lines.append("Alt+6: caron (rising tone)")
    lines.append("Alt+7: circumflex (falling tone)")
    lines.append("Alt+8: double acute (extra high)")
    lines.append("Alt+9: double grave (extra low)")
    lines.append("Alt+0: tilde (nasalization)")
    lines.append("")

    lines.append("OTHER SHORTCUTS")
    lines.append("-" * 30)
    lines.append("Ctrl+Enter: Speak text")
    lines.append("Escape: Stop speaking")
    lines.append("Ctrl+S: Save as WAV")
    lines.append("F1: Show this help")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    # Test the module
    print(get_help_text())

    # Test symbol lookup
    print("\nTesting symbol lookup:")
    print(f"Alt+A press 1: {get_symbol_for_key('a', 1)}")
    print(f"Alt+A press 2: {get_symbol_for_key('a', 2)}")
    print(f"Alt+S press 1: {get_symbol_for_key('s', 1)}")
    print(f"Alt+1 press 1: {get_symbol_for_key('1', 1)}")
