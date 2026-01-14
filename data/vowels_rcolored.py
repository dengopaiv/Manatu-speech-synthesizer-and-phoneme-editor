# -*- coding: utf-8 -*-
"""
Phoneme data: Vowels Rcolored

This file is part of the NV Speech Player project.
Auto-generated from data.py split.

Voice quality is controlled by lfRd parameter (LF model):
- lfRd > 0: Modern LF glottal model (Fant 1995)
- lfRd = 0: No voicing (voiceless consonants only)
"""

VOWELS_RCOLORED = {
	'ɝ': {  # Stressed r-colored schwa (Stevens Table 9.2 - lowered F4)
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'spectralTilt': 4,   # Modal voice naturalness
		'flutter': 0.12,     # Natural F0 jitter
		'cf1': 500,
		'cf2': 1350,
		'cf3': 1650,
		'cf4': 2900,  # Lowered F4 for r-coloring (Stevens)
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 100,
		'cb2': 270,
		'cb3': 330,
		'cb4': 967,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		'pf1': 500,
		'pf2': 1350,
		'pf3': 1650,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 100,
		'pb2': 270,
		'pb3': 330,
		'pb4': 967,
		'pb5': 1250,
		'pb6': 1633,
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'fricationAmplitude': 0,
		# Voice quality
		'lfRd': 2.7,  # Modern LF model (breathy voice, consistent with other vowels)
		'diplophonia': 0,
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 100,
		'ftzFreq1': 0,
		'ftzBw1': 100,
		'ftpFreq2': 0,
		'ftpBw2': 100,
	},
	'ɚ': {  # Unstressed r-colored schwa (Stevens Table 9.2 - lowered F4)
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'spectralTilt': 4,   # Modal voice naturalness
		'flutter': 0.12,     # Natural F0 jitter
		'cf1': 500,
		'cf2': 1400,
		'cf3': 1600,
		'cf4': 2900,  # Lowered F4 for r-coloring (Stevens)
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 100,
		'cb2': 280,
		'cb3': 320,
		'cb4': 967,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		'pf1': 500,
		'pf2': 1400,
		'pf3': 1600,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 100,
		'pb2': 280,
		'pb3': 320,
		'pb4': 967,
		'pb5': 1250,
		'pb6': 1633,
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'fricationAmplitude': 0,
		# Voice quality
		'lfRd': 2.7,  # Modern LF model (breathy voice, consistent with other vowels)
		'diplophonia': 0,
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 100,
		'ftzFreq1': 0,
		'ftzBw1': 100,
		'ftpFreq2': 0,
		'ftpBw2': 100,
	},
}
