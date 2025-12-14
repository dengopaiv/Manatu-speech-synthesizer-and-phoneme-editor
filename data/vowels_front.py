# -*- coding: utf-8 -*-
"""
Phoneme data: Vowels Front

This file is part of the NV Speech Player project.
Auto-generated from data.py split.
"""

VOWELS_FRONT = {
	'a': {  # Open front unrounded
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		'voiceTurbulenceAmplitude': 0,
		'noiseFilterFreq': 0,
		'noiseFilterBw': 1000,
		# Voice quality - optimized for natural sound with smooth transitions
		'glottalOpenQuotient': 0.45,  # Higher for open vowel
		'openQuotientShape': 0.5,
		'speedQuotient': 1.0,
		'spectralTilt': 10,  # Higher spectral tilt for open vowel warmth
		'flutter': 0.15,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 400,  # Dynamic F1 bandwidth modulation for natural voice
		# Cascade formants - narrower bandwidths for "colour/bass"
		'cf1': 850,  # Standard open front ~730-850 Hz
		'cf2': 1350,  # Standard ~1090-1350 Hz
		'cf3': 2500,
		'cf4': 3500,
		'cf5': 4500,
		'cf6': 5000,
		'cb1': 90,   # Narrowed from 219 for sharper F1 peak (more bass)
		'cb2': 110,  # Narrowed from 300 for sharper F2 peak (more colour)
		'cb3': 150,
		'cb4': 200,
		'cb5': 200,
		'cb6': 500,
		'cfNP': 250,
		'cfN0': 250,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 850,
		'pf2': 1350,
		'pf3': 2500,
		'pf4': 3500,
		'pf5': 4500,
		'pf6': 5000,
		'pb1': 90,   # Match cb1
		'pb2': 110,  # Match cb2
		'pb3': 150,
		'pb4': 200,
		'pb5': 200,
		'pb6': 500,
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
		'ftzBw1': 125,
		'ftpFreq2': 0,
		'ftpBw2': 125,
		# Burst
		'burstAmplitude': 0,
		'burstDuration': 0.25,
	},
	'i': {  # High front unrounded (tense) - FLEECE vowel
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model
		'glottalOpenQuotient': 0.12,
		'openQuotientShape': 0.5,
		'speedQuotient': 0.5,
		'spectralTilt': 0,  # Low tilt for bright close vowel
		'flutter': 0.12,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		# Cascade formants - narrower bandwidths for colour
		'cf1': 280,  # Standard close front ~270-310
		'cf2': 2500,  # Standard ~2290-2790
		'cf3': 3200,  # Standard ~3010-3310
		'cf4': 3800,
		'cf5': 4156,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 50,   # Narrowed for sharper F1 peak
		'cb2': 100,  # Narrowed for sharper F2 peak
		'cb3': 150,
		'cb4': 200,
		'cb5': 150,
		'cb6': 400,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 280,
		'pf2': 2500,
		'pf3': 3200,
		'pf4': 3800,
		'pf5': 4156,
		'pf6': 4900,
		'pb1': 50,   # Match cb1
		'pb2': 100,  # Match cb2
		'pb3': 150,
		'pb4': 200,
		'pb5': 150,
		'pb6': 400,
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 95,
		'ftzFreq1': 0,
		'ftzBw1': 100,
		'ftpFreq2': 0,
		'ftpBw2': 200,
	},
	'e': {  # Mid front unrounded (close-mid)
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model
		'glottalOpenQuotient': 0.12,
		'openQuotientShape': 0.5,
		'speedQuotient': 0.5,
		'spectralTilt': 4,
		'flutter': 0.10,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		# Cascade formants - narrower bandwidths for colour
		'cf1': 530,  # Standard close-mid ~400-480
		'cf2': 2300,  # Standard ~2020-2290
		'cf3': 3000,  # Standard ~2600-2700
		'cf4': 3500,
		'cf5': 5000,
		'cf6': 5400,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 60,   # Narrowed for sharper F1 peak
		'cb2': 100,  # Narrowed for sharper F2 peak
		'cb3': 150,
		'cb4': 200,
		'cb5': 590,
		'cb6': 380,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 530,
		'pf2': 2300,
		'pf3': 3000,
		'pf4': 3500,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 60,   # Match cb1
		'pb2': 100,  # Match cb2
		'pb3': 150,
		'pb4': 200,
		'pb5': 200,
		'pb6': 1000,
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
	'ɪ': {  # Near-close front unrounded (lax) - KIT vowel
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model
		'glottalOpenQuotient': 0.12,
		'openQuotientShape': 0.5,
		'speedQuotient': 0.5,
		'spectralTilt': 2,
		'flutter': 0.12,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		# Cascade formants - narrower bandwidths for colour
		'cf1': 400,  # Standard near-close ~390-400
		'cf2': 2000,  # Standard ~1990-2100 - important for diphthongs
		'cf3': 2600,  # Standard ~2550-2650
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 60,   # Narrowed for sharper F1 peak
		'cb2': 100,  # Narrowed for sharper F2 peak
		'cb3': 150,
		'cb4': 180,
		'cb5': 150,
		'cb6': 400,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 400,
		'pf2': 2000,
		'pf3': 2600,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 60,   # Match cb1
		'pb2': 100,  # Match cb2
		'pb3': 150,
		'pb4': 180,
		'pb5': 150,
		'pb6': 400,
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
	'ɛ': {  # Open-mid front unrounded
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model
		'glottalOpenQuotient': 0.20,  # Slightly higher for more open vowel
		'openQuotientShape': 0.5,
		'speedQuotient': 0.5,
		'spectralTilt': 5,
		'flutter': 0.10,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		# Cascade formants - narrower bandwidths for colour
		'cf1': 550,  # Standard open-mid ~530-580
		'cf2': 1880,  # Standard ~1840-1920
		'cf3': 2530,  # Standard ~2480-2590
		'cf4': 3100,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 70,   # Narrowed for sharper F1 peak
		'cb2': 100,  # Narrowed for sharper F2 peak
		'cb3': 150,
		'cb4': 180,
		'cb5': 150,
		'cb6': 400,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 550,
		'pf2': 1880,
		'pf3': 2530,
		'pf4': 3100,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 70,   # Match cb1
		'pb2': 100,  # Match cb2
		'pb3': 150,
		'pb4': 180,
		'pb5': 150,
		'pb6': 400,
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
	'æ': {  # Near-open front unrounded (TRAP vowel)
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model for open vowel
		'glottalOpenQuotient': 0.35,  # Higher for open vowel
		'openQuotientShape': 0.5,
		'speedQuotient': 0.7,
		'spectralTilt': 8,  # Moderate tilt for warmth
		'flutter': 0.12,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 350,  # Dynamic F1 bandwidth modulation for natural voice
		# Cascade formants - narrower bandwidths for colour
		'cf1': 700,  # Standard near-open ~660-750
		'cf2': 1780,  # Standard ~1720-1850
		'cf3': 2450,  # Standard ~2410-2500
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 80,   # Narrowed for sharper F1 peak
		'cb2': 110,  # Narrowed for sharper F2 peak
		'cb3': 150,
		'cb4': 180,
		'cb5': 150,
		'cb6': 400,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 700,
		'pf2': 1780,
		'pf3': 2450,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 80,   # Match cb1
		'pb2': 110,  # Match cb2
		'pb3': 150,
		'pb4': 180,
		'pb5': 150,
		'pb6': 400,
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
	'y': {  # Close front rounded
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model
		'glottalOpenQuotient': 0.15,
		'openQuotientShape': 0.5,  # Normalized from 0.12
		'speedQuotient': 0.5,
		'spectralTilt': 2,
		'flutter': 0.12,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		# Cascade formants - narrower bandwidths for colour
		'cf1': 280,  # Close front ~280
		'cf2': 1900,
		'cf3': 2100,
		'cf4': 2700,
		'cf5': 4000,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 50,   # Narrowed for sharper F1 peak
		'cb2': 100,  # Narrowed for sharper F2 peak
		'cb3': 120,
		'cb4': 100,
		'cb5': 200,
		'cb6': 400,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 280,
		'pf2': 1900,
		'pf3': 2100,
		'pf4': 2700,
		'pf5': 4000,
		'pf6': 4900,
		'pb1': 50,   # Match cb1
		'pb2': 100,  # Match cb2
		'pb3': 120,
		'pb4': 100,
		'pb5': 200,
		'pb6': 400,
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
	'ʏ': {  # Near-close front rounded
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model
		'glottalOpenQuotient': 0.12,
		'openQuotientShape': 0.5,
		'speedQuotient': 0.5,
		'spectralTilt': 2,
		'flutter': 0.12,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		# Cascade formants - narrower bandwidths for colour
		'cf1': 360,
		'cf2': 1700,
		'cf3': 2200,
		'cf4': 3400,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 55,   # Narrowed for sharper F1 peak
		'cb2': 100,  # Narrowed for sharper F2 peak
		'cb3': 140,
		'cb4': 180,
		'cb5': 150,
		'cb6': 400,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 360,
		'pf2': 1700,
		'pf3': 2200,
		'pf4': 3400,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 55,   # Match cb1
		'pb2': 100,  # Match cb2
		'pb3': 140,
		'pb4': 180,
		'pb5': 150,
		'pb6': 400,
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
	'ø': {  # Close-mid front rounded
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model
		'glottalOpenQuotient': 0.12,
		'openQuotientShape': 0.5,
		'speedQuotient': 0.5,
		'spectralTilt': 3,
		'flutter': 0.12,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		# Cascade formants - narrower bandwidths for colour
		'cf1': 400,
		'cf2': 1600,
		'cf3': 2400,
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 60,   # Narrowed for sharper F1 peak
		'cb2': 100,  # Narrowed for sharper F2 peak
		'cb3': 150,
		'cb4': 180,
		'cb5': 150,
		'cb6': 400,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 400,
		'pf2': 1600,
		'pf3': 2400,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 60,   # Match cb1
		'pb2': 100,  # Match cb2
		'pb3': 150,
		'pb4': 180,
		'pb5': 150,
		'pb6': 400,
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
	'œ': {  # Open-mid front rounded
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model
		'glottalOpenQuotient': 0.18,  # Slightly higher for more open vowel
		'openQuotientShape': 0.5,
		'speedQuotient': 0.5,
		'spectralTilt': 5,
		'flutter': 0.10,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		# Cascade formants - narrower bandwidths for colour
		'cf1': 530,
		'cf2': 1500,
		'cf3': 2500,
		'cf4': 3100,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 70,   # Narrowed for sharper F1 peak
		'cb2': 100,  # Narrowed for sharper F2 peak
		'cb3': 150,
		'cb4': 180,
		'cb5': 150,
		'cb6': 400,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 530,
		'pf2': 1500,
		'pf3': 2500,
		'pf4': 3100,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 70,   # Match cb1
		'pb2': 100,  # Match cb2
		'pb3': 150,
		'pb4': 180,
		'pb5': 150,
		'pb6': 400,
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
	'ɶ': {  # Open front rounded
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - optimized with LF model for open vowel
		'glottalOpenQuotient': 0.35,  # Higher for open vowel
		'openQuotientShape': 0.5,
		'speedQuotient': 0.5,
		'spectralTilt': 8,  # Moderate tilt for warmth
		'flutter': 0.12,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 300,  # Dynamic F1 bandwidth modulation for natural voice
		# Cascade formants - narrower bandwidths for colour
		'cf1': 700,
		'cf2': 1600,
		'cf3': 2500,
		'cf4': 3000,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 80,   # Narrowed for sharper F1 peak
		'cb2': 100,  # Narrowed for sharper F2 peak
		'cb3': 150,
		'cb4': 180,
		'cb5': 150,
		'cb6': 400,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 700,
		'pf2': 1600,
		'pf3': 2500,
		'pf4': 3000,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 80,   # Match cb1
		'pb2': 100,  # Match cb2
		'pb3': 150,
		'pb4': 180,
		'pb5': 150,
		'pb6': 400,
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
