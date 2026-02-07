# -*- coding: utf-8 -*-
"""
Phoneme data: Vowels Front

This file is part of the NV Speech Player project.
Auto-generated from data.py split.

Voice quality is controlled by lfRd parameter (LF model):
- lfRd > 0: Modern LF glottal model (Fant 1995)
- lfRd = 0: No voicing (voiceless consonants only)
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
		'spectralTilt': 10,  # Higher spectral tilt for open vowel warmth
		'flutter': 0.15,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 400,  # Dynamic F1 bandwidth modulation for natural voice
		# Cascade formants - frequency-dependent bandwidths (Q=5.0 for F1-F3, Q=3.0 for F4-F6)
		'cf1': 850,  # Standard open front ~730-850 Hz
		'cf2': 1350,  # Standard ~1090-1350 Hz
		'cf3': 2500,
		'cf4': 3500,
		'cf5': 4500,
		'cf6': 5000,
		'cb1': 170,   # cf1/5.0 = 850/5.0 (Q=5.0)
		'cb2': 338,   # cf2/5.0 = 1350/5.0 (Q=5.0)
		'cb3': 500,   # cf3/5.0 = 2500/5.0 (Q=5.0)
		'cb4': 1167,  # cf4/3.0 = 3500/3.0 (Q=3.0)
		'cb5': 1500,  # cf5/3.0 = 4500/3.0 (Q=3.0)
		'cb6': 1667,  # cf6/3.0 = 5000/3.0 (Q=3.0)
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
		'pb1': 170,   # Match cb1
		'pb2': 338,   # Match cb2
		'pb3': 500,   # Match cb3
		'pb4': 1167,  # Match cb4
		'pb5': 1500,  # Match cb5
		'pb6': 1667,  # Match cb6
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
		'cb1': 56,   # Narrowed for sharper F1 peak
		'cb2': 500,  # Narrowed for sharper F2 peak
		'cb3': 640,
		'cb4': 1267,
		'cb5': 1385,
		'cb6': 1633,
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
		'pb1': 56,   # Match cb1
		'pb2': 500,  # Match cb2
		'pb3': 640,
		'pb4': 1267,
		'pb5': 1385,
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
		'spectralTilt': 4,
		'flutter': 0.10,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		# Cascade formants - narrower bandwidths for colour
		'cf1': 400,  # Standard close-mid ~390-480 (Hillenbrand: 390)
		'cf2': 2300,  # Standard ~2020-2290
		'cf3': 3000,  # Standard ~2600-2700
		'cf4': 3500,
		'cf5': 5000,
		'cf6': 5400,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 80,   # cf1/5.0 = 400/5.0 (Q=5.0)
		'cb2': 460,  # Narrowed for sharper F2 peak
		'cb3': 600,
		'cb4': 1167,
		'cb5': 1667,
		'cb6': 1800,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 400,
		'pf2': 2300,
		'pf3': 3000,
		'pf4': 3500,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 80,   # Match cb1
		'pb2': 460,  # Match cb2
		'pb3': 600,
		'pb4': 1167,
		'pb5': 1667,
		'pb6': 1800,
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
		'cb1': 80,   # Narrowed for sharper F1 peak
		'cb2': 400,  # Narrowed for sharper F2 peak
		'cb3': 520,
		'cb4': 1100,
		'cb5': 1250,
		'cb6': 1633,
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
		'pb1': 80,   # Match cb1
		'pb2': 400,  # Match cb2
		'pb3': 520,
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
		'cb1': 110,   # Narrowed for sharper F1 peak
		'cb2': 376,  # Narrowed for sharper F2 peak
		'cb3': 506,
		'cb4': 1033,
		'cb5': 1250,
		'cb6': 1633,
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
		'pb1': 110,   # Match cb1
		'pb2': 376,  # Match cb2
		'pb3': 506,
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
		'cb1': 140,   # Narrowed for sharper F1 peak
		'cb2': 356,  # Narrowed for sharper F2 peak
		'cb3': 490,
		'cb4': 1100,
		'cb5': 1250,
		'cb6': 1633,
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
		'pb1': 140,   # Match cb1
		'pb2': 356,  # Match cb2
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
		'cb1': 56,   # Narrowed for sharper F1 peak
		'cb2': 380,  # Narrowed for sharper F2 peak
		'cb3': 420,
		'cb4': 900,
		'cb5': 1333,
		'cb6': 1633,
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
		'pb1': 56,   # Match cb1
		'pb2': 380,  # Match cb2
		'pb3': 420,
		'pb4': 900,
		'pb5': 1333,
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
		'cb1': 72,   # Narrowed for sharper F1 peak
		'cb2': 340,  # Narrowed for sharper F2 peak
		'cb3': 440,
		'cb4': 1133,
		'cb5': 1250,
		'cb6': 1633,
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
		'pb1': 72,   # Match cb1
		'pb2': 340,  # Match cb2
		'pb3': 440,
		'pb4': 1133,
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
		'cb1': 80,   # Narrowed for sharper F1 peak
		'cb2': 320,  # Narrowed for sharper F2 peak
		'cb3': 480,
		'cb4': 1100,
		'cb5': 1250,
		'cb6': 1633,
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
		'pb1': 80,   # Match cb1
		'pb2': 320,  # Match cb2
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
		'cb1': 106,   # Narrowed for sharper F1 peak
		'cb2': 300,  # Narrowed for sharper F2 peak
		'cb3': 500,
		'cb4': 1033,
		'cb5': 1250,
		'cb6': 1633,
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
		'pb1': 106,   # Match cb1
		'pb2': 300,  # Match cb2
		'pb3': 500,
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
		'cb1': 140,   # Narrowed for sharper F1 peak
		'cb2': 320,  # Narrowed for sharper F2 peak
		'cb3': 500,
		'cb4': 1000,
		'cb5': 1250,
		'cb6': 1633,
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
		'pb1': 140,   # Match cb1
		'pb2': 320,  # Match cb2
		'pb3': 500,
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
}
