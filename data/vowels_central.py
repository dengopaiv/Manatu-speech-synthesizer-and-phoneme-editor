# -*- coding: utf-8 -*-
"""
Phoneme data: Vowels Central

This file is part of the NV Speech Player project.
Auto-generated from data.py split.

Voice quality is controlled by lfRd parameter (LF model):
- lfRd > 0: Modern LF glottal model (Fant 1995)
- lfRd = 0: No voicing (voiceless consonants only)
"""

VOWELS_CENTRAL = {
	'ə': {  # Mid central (schwa) - most common vowel in English
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
		'cf1': 500,  # Standard mid central ~500-520
		'cf2': 1450,  # Standard ~1400-1500
		'cf3': 2450,  # Standard ~2400-2500
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 100,   # Narrowed for sharper F1 peak
		'cb2': 290,  # Narrowed for sharper F2 peak
		'cb3': 490,
		'cb4': 1100,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 500,
		'pf2': 1450,
		'pf3': 2450,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 100,   # Match cb1
		'pb2': 290,  # Match cb2
		'pb3': 490,
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
	'ɜ': {  # Open-mid central unrounded (NURSE vowel)
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model
		'spectralTilt': 5,
		'flutter': 0.12,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		# Cascade formants - narrower bandwidths for colour
		'cf1': 500,
		'cf2': 1400,
		'cf3': 2300,
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 100,   # Narrowed for sharper F1 peak
		'cb2': 280,  # Narrowed for sharper F2 peak
		'cb3': 460,
		'cb4': 1100,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 500,
		'pf2': 1400,
		'pf3': 2300,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 100,   # Match cb1
		'pb2': 280,  # Match cb2
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
	'ɞ': {  # Open-mid central rounded
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
		'cf1': 500,
		'cf2': 1350,
		'cf3': 2100,
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 100,   # Narrowed for sharper F1 peak
		'cb2': 270,  # Narrowed for sharper F2 peak
		'cb3': 420,
		'cb4': 1100,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 500,
		'pf2': 1350,
		'pf3': 2100,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 100,   # Match cb1
		'pb2': 270,  # Match cb2
		'pb3': 420,
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
	'ɐ': {  # Near-open central
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
		'deltaB1': 280,  # Dynamic F1 bandwidth modulation for natural voice
		# Cascade formants - narrower bandwidths for colour
		'cf1': 650,
		'cf2': 1310,
		'cf3': 2400,
		'cf4': 3000,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 130,   # Narrowed for sharper F1 peak
		'cb2': 262,  # Narrowed for sharper F2 peak
		'cb3': 480,
		'cb4': 1000,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 650,
		'pf2': 1310,
		'pf3': 2400,
		'pf4': 3000,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 130,   # Match cb1
		'pb2': 262,  # Match cb2
		'pb3': 480,
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
	'ɨ': {  # Close central unrounded
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
		'cf1': 300,  # Fixed (standard close central)
		'cf2': 1600,
		'cf3': 2500,
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 60,   # Narrowed for sharper F1 peak
		'cb2': 320,  # Narrowed for sharper F2 peak
		'cb3': 500,
		'cb4': 1100,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 300,
		'pf2': 1600,
		'pf3': 2500,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 60,   # Match cb1
		'pb2': 320,  # Match cb2
		'pb3': 500,
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
	'ʉ': {  # Close central rounded
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
		'cf1': 320,
		'cf2': 1500,
		'cf3': 2300,
		'cf4': 3100,
		'cf5': 3500,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 64,   # Narrowed for sharper F1 peak
		'cb2': 300,  # Narrowed for sharper F2 peak
		'cb3': 460,
		'cb4': 1033,
		'cb5': 1167,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 320,
		'pf2': 1500,
		'pf3': 2300,
		'pf4': 3100,
		'pf5': 3500,
		'pf6': 4900,
		'pb1': 64,   # Match cb1
		'pb2': 300,  # Match cb2
		'pb3': 460,
		'pb4': 1033,
		'pb5': 1167,
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
	'ɘ': {  # Close-mid central unrounded
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
		'cf1': 400,
		'cf2': 1500,
		'cf3': 2400,
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 80,   # Narrowed for sharper F1 peak
		'cb2': 300,  # Narrowed for sharper F2 peak
		'cb3': 480,
		'cb4': 1100,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 400,
		'pf2': 1500,
		'pf3': 2400,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 80,   # Match cb1
		'pb2': 300,  # Match cb2
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
	'ɵ': {  # Close-mid central rounded
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
		'cf1': 400,
		'cf2': 1400,
		'cf3': 2200,
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 80,   # Narrowed for sharper F1 peak
		'cb2': 280,  # Narrowed for sharper F2 peak
		'cb3': 440,
		'cb4': 1100,
		'cb5': 1250,
		'cb6': 1633,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 400,
		'pf2': 1400,
		'pf3': 2200,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 80,   # Match cb1
		'pb2': 280,  # Match cb2
		'pb3': 440,
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
}
