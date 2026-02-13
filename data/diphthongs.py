# -*- coding: utf-8 -*-
"""
Phoneme data: Diphthongs and Triphthongs

This file is part of the NV Speech Player project.

Diphthongs are defined as sequences of component vowels.
The IPA parser expands these into separate phonemes, allowing
the synthesizer's existing interpolation to create smooth transitions.

Each diphthong entry contains:
- Full formant data from the first component (for editor/preview)
- _components tuple for parser expansion
"""

# Import vowel data to get formant values
from .vowels_front import VOWELS_FRONT
from .vowels_central import VOWELS_CENTRAL
from .vowels_back import VOWELS_BACK

# Merge all vowels for lookup
_ALL_VOWELS = {}
_ALL_VOWELS.update(VOWELS_FRONT)
_ALL_VOWELS.update(VOWELS_CENTRAL)
_ALL_VOWELS.update(VOWELS_BACK)

# Diphthong definitions: maps IPA diphthong to component vowels
DIPHTHONG_COMPONENTS = {
	# ==========================================================================
	# EXISTING DIPHTHONGS (from original data.py)
	# ==========================================================================
	'ɑj': ('ɑ', 'i'),   # Open back unrounded to palatal approximant
	'ɑw': ('ɑ', 'u'),   # Open back unrounded to labiovelar approximant
	'ɔj': ('ɔ', 'i'),   # Low-mid back rounded to palatal approximant

	# ==========================================================================
	# ENGLISH DIPHTHONGS
	# ==========================================================================
	'aɪ': ('a', 'ɪ'),   # PRICE - open front to near-close front (like 'price', 'high')
	'aʊ': ('a', 'ʊ'),   # MOUTH - open front to near-close back (like 'mouth', 'now')
	'eɪ': ('e', 'ɪ'),   # FACE - close-mid front to near-close front (like 'face', 'day')
	'oʊ': ('o', 'ʊ'),   # GOAT - close-mid back to near-close back (like 'goat', 'show')
	'ɔɪ': ('ɔ', 'ɪ'),   # CHOICE - open-mid back to near-close front (like 'choice', 'boy')
	'ɪə': ('ɪ', 'ə'),   # NEAR - near-close front to mid central (like 'near', 'here')
	'eə': ('e', 'ə'),   # SQUARE - close-mid front to mid central (like 'square', 'care')
	'ʊə': ('ʊ', 'ə'),   # CURE - near-close back to mid central (like 'cure', 'tour')

	# ==========================================================================
	# ESTONIAN DIPHTHONGS
	# ==========================================================================
	'aj': ('a', 'i'),   # kai, lai, mai
	'ej': ('e', 'i'),   # hei, lei, vei
	'oj': ('o', 'i'),   # koi, loi, poi
	'uj': ('u', 'i'),   # tui, kui, sui
	'iʊ': ('i', 'ʊ'),   # liu, piu
	'yj': ('y', 'i'),   # tüi, süi
	'ɤj': ('ɤ', 'i'),   # õige, tõi

	# ==========================================================================
	# FINNISH DIPHTHONGS
	# ==========================================================================
	'øy': ('ø', 'y'),   # löyly, pöytä
	'uo': ('u', 'o'),   # suo, tuo, muo
	'yø': ('y', 'ø'),   # syö, lyö, työ

	# ==========================================================================
	# LIVONIAN/FINNIC TRIPHTHONGS
	# ==========================================================================
	'uoi': ('u', 'o', 'i'),   # kuoig (fish)
}

def _build_diphthong_entry(diphthong_ipa, components):
	"""Build a full diphthong entry with formant data from first component."""
	first_vowel = components[0]
	vowel_data = _ALL_VOWELS.get(first_vowel, {})

	# Start with a copy of the first vowel's data
	entry = vowel_data.copy()

	# Override/add diphthong-specific properties
	entry['_isVowel'] = True
	entry['_isVoiced'] = True
	entry['_isDiphthong'] = True
	entry['_components'] = components

	return entry

# Build DIPHTHONGS dict with full formant data
DIPHTHONGS = {
	diphthong: _build_diphthong_entry(diphthong, components)
	for diphthong, components in DIPHTHONG_COMPONENTS.items()
}
