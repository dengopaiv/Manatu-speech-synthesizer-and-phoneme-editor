# -*- coding: utf-8 -*-
"""
Phoneme data: Vowels Back

This file is part of the NV Speech Player project.
Auto-generated from data.py split.

Voice quality is controlled by lfRd parameter (LF model):
- lfRd > 0: Modern LF glottal model (Fant 1995)
- lfRd = 0: No voicing (voiceless consonants only)
"""

VOWELS_BACK = {
	'u': {  # Close back rounded
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model
		'spectralTilt': 0,  # Low tilt for bright close vowel
		'flutter': 0.10,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		# Cascade formants - narrower bandwidths for colour
		'cf1': 300,  # Standard close back ~300-340
		'cf2': 870,  # Standard ~870-1020 (Hillenbrand: 870)
		'cf3': 2300,
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 60,   # Narrowed for sharper F1 peak
		'cb2': 174,   # cf2/5.0 = 870/5.0 (Q=5.0)
		'cb3': 460,
		'cb4': 1100,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 300,
		'pf2': 870,
		'pf3': 2300,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 60,   # Match cb1
		'pb2': 174,   # Match cb2
		'pb3': 460,
		'pb4': 1100,
		'pb5': 1250,
		'pb6': 1633,
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 100,
		'ftzFreq1': 0,
		'ftzBw1': 100,
		'ftpFreq2': 0,
		'ftpBw2': 100,
	},
	'ʊ': {  # Near-close back rounded
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model
		'spectralTilt': 2,
		'flutter': 0.12,  # Normalized from 0.25
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		# Cascade formants - narrower bandwidths for colour
		'cf1': 450,  # Standard near-close ~440-470
		'cf2': 1050,  # Standard ~1020-1100
		'cf3': 2300,
		'cf4': 3500,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 90,   # Narrowed for sharper F1 peak
		'cb2': 210,   # Narrowed for sharper F2 peak
		'cb3': 460,
		'cb4': 1167,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 450,
		'pf2': 1050,
		'pf3': 2300,
		'pf4': 3500,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 90,   # Match cb1
		'pb2': 210,   # Match cb2
		'pb3': 460,
		'pb4': 1167,
		'pb5': 1250,
		'pb6': 1633,
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 100,
		'ftzFreq1': 0,
		'ftzBw1': 100,
		'ftpFreq2': 0,
		'ftpBw2': 100,
	},
	'o': {  # Close-mid back rounded
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model
		'spectralTilt': 3,
		'flutter': 0.12,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		# Cascade formants - narrower bandwidths for colour
		'cf1': 400,  # Standard close-mid ~390-500 (Hillenbrand: 390)
		'cf2': 870,  # Standard ~830-920
		'cf3': 2400,  # Standard ~2380-2500
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 80,   # cf1/5.0 = 400/5.0 (Q=5.0)
		'cb2': 218,   # Narrowed for sharper F2 peak
		'cb3': 480,
		'cb4': 1100,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 400,
		'pf2': 870,
		'pf3': 2400,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 80,   # Match cb1
		'pb2': 218,   # Match cb2
		'pb3': 480,
		'pb4': 1100,
		'pb5': 1250,
		'pb6': 1633,
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 100,
		'ftzFreq1': 0,
		'ftzBw1': 100,
		'ftpFreq2': 0,
		'ftpBw2': 100,
	},
	'ɔ': {  # Open-mid back rounded
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model for open vowel
		'spectralTilt': 6,
		'flutter': 0.12,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 300,  # Dynamic F1 bandwidth modulation for natural voice
		# Cascade formants - narrower bandwidths for colour
		'cf1': 600,  # Standard open-mid ~570-640
		'cf2': 880,  # Standard ~840-920
		'cf3': 2550,  # Standard ~2410-2680
		'cf4': 3100,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 120,   # Narrowed for sharper F1 peak
		'cb2': 220,  # Narrowed for sharper F2 peak
		'cb3': 510,
		'cb4': 1033,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 600,
		'pf2': 880,
		'pf3': 2550,
		'pf4': 3100,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 120,   # Match cb1
		'pb2': 220,  # Match cb2
		'pb3': 510,
		'pb4': 1033,
		'pb5': 1250,
		'pb6': 1633,
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 100,
		'ftzFreq1': 0,
		'ftzBw1': 100,
		'ftpFreq2': 0,
		'ftpBw2': 100,
	},
	'ɑ': {  # Open back unrounded
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model for open vowel
		'spectralTilt': 10,  # Higher tilt for open back vowel warmth
		'flutter': 0.12,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 350,  # Dynamic F1 bandwidth modulation for natural voice
		# Cascade formants - narrower bandwidths for colour
		'cf1': 740,  # Standard open back ~710-770
		'cf2': 1150,  # Standard ~1090-1220
		'cf3': 2550,  # Standard ~2440-2640
		'cf4': 3000,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 148,   # Narrowed for sharper F1 peak
		'cb2': 288,  # Narrowed for sharper F2 peak
		'cb3': 510,
		'cb4': 1000,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 740,
		'pf2': 1150,
		'pf3': 2550,
		'pf4': 3000,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 148,   # Match cb1
		'pb2': 288,  # Match cb2
		'pb3': 510,
		'pb4': 1000,
		'pb5': 1250,
		'pb6': 1633,
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 100,
		'ftzFreq1': 0,
		'ftzBw1': 100,
		'ftpFreq2': 0,
		'ftpBw2': 100,
	},
	'ɒ': {  # Open back rounded
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model for open vowel
		'spectralTilt': 8,
		'flutter': 0.12,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 320,  # Dynamic F1 bandwidth modulation for natural voice
		# Cascade formants - narrower bandwidths for colour
		'cf1': 620,
		'cf2': 1100,
		'cf3': 2520,
		'cf4': 3000,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 124,   # Narrowed for sharper F1 peak
		'cb2': 275,  # Narrowed for sharper F2 peak
		'cb3': 504,
		'cb4': 1000,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 620,
		'pf2': 1100,
		'pf3': 2520,
		'pf4': 3000,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 124,   # Match cb1
		'pb2': 275,  # Match cb2
		'pb3': 504,
		'pb4': 1000,
		'pb5': 1250,
		'pb6': 1633,
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 100,
		'ftzFreq1': 0,
		'ftzBw1': 100,
		'ftpFreq2': 0,
		'ftpBw2': 100,
	},
	'ɯ': {  # Close back unrounded
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model
		'spectralTilt': 2,
		'flutter': 0.12,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		# Cascade formants - narrower bandwidths for colour
		'cf1': 300,
		'cf2': 1200,
		'cf3': 2100,
		'cf4': 3500,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 60,   # Narrowed for sharper F1 peak
		'cb2': 240,  # Narrowed for sharper F2 peak
		'cb3': 420,
		'cb4': 1167,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 300,
		'pf2': 1200,
		'pf3': 2100,
		'pf4': 3500,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 60,   # Match cb1
		'pb2': 240,  # Match cb2
		'pb3': 420,
		'pb4': 1167,
		'pb5': 1250,
		'pb6': 1633,
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 100,
		'ftzFreq1': 0,
		'ftzBw1': 100,
		'ftpFreq2': 0,
		'ftpBw2': 100,
	},
	'ɤ': {  # Close-mid back unrounded
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model
		'spectralTilt': 4,
		'flutter': 0.12,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		# Cascade formants - narrower bandwidths for colour
		'cf1': 460,
		'cf2': 1200,
		'cf3': 2550,
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 92,   # Narrowed for sharper F1 peak
		'cb2': 240,  # Narrowed for sharper F2 peak
		'cb3': 510,
		'cb4': 1100,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 460,
		'pf2': 1200,
		'pf3': 2550,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 92,   # Match cb1
		'pb2': 240,  # Match cb2
		'pb3': 510,
		'pb4': 1100,
		'pb5': 1250,
		'pb6': 1633,
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 100,
		'ftzFreq1': 0,
		'ftzBw1': 100,
		'ftpFreq2': 0,
		'ftpBw2': 100,
	},
	'ʌ': {  # Open-mid back unrounded (STRUT vowel)
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model for open vowel
		'spectralTilt': 7,
		'flutter': 0.12,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 280,  # Dynamic F1 bandwidth modulation for natural voice
		# Cascade formants - narrower bandwidths for colour
		'cf1': 620,
		'cf2': 1220,
		'cf3': 2550,
		'cf4': 3100,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 124,   # Narrowed for sharper F1 peak
		'cb2': 244,  # Narrowed for sharper F2 peak
		'cb3': 510,
		'cb4': 1033,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 620,
		'pf2': 1220,
		'pf3': 2550,
		'pf4': 3100,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 124,   # Match cb1
		'pb2': 244,  # Match cb2
		'pb3': 510,
		'pb4': 1033,
		'pb5': 1250,
		'pb6': 1633,
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 100,
		'ftzFreq1': 0,
		'ftzBw1': 100,
		'ftpFreq2': 0,
		'ftpBw2': 100,
	},
}
