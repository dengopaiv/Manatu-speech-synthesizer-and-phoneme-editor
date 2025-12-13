# -*- coding: utf-8 -*-
"""
Phoneme data: Diphthongs and Triphthongs

This file is part of the NV Speech Player project.

Diphthongs are defined as sequences of component vowels.
The IPA parser expands these into separate phonemes, allowing
the synthesizer's existing interpolation to create smooth transitions.

Format: 'diphthong': ('vowel1', 'vowel2', ...)
"""

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

# For backwards compatibility, also expose as DIPHTHONGS dict
# with basic vowel properties (used by data.py merge)
DIPHTHONGS = {key: {
	'_isVowel': True,
	'_isVoiced': True,
	'_isDiphthong': True,
	'_components': value,
} for key, value in DIPHTHONG_COMPONENTS.items()}
