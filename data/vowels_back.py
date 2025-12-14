# -*- coding: utf-8 -*-
"""
Phoneme data: Vowels Back

This file is part of the NV Speech Player project.
Auto-generated from data.py split.
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
		'glottalOpenQuotient': 0.22,  # Increased for brighter upper formants
		'openQuotientShape': 0.5,
		'speedQuotient': 1.0,
		'spectralTilt': 0,  # Low tilt for bright close vowel
		'flutter': 0.10,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		# Cascade formants - narrower bandwidths for colour
		'cf1': 300,  # Standard close back ~300-340
		'cf2': 750,  # Standard ~870-1020
		'cf3': 2300,
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 50,   # Narrowed for sharper F1 peak
		'cb2': 80,   # Narrowed for sharper F2 peak
		'cb3': 150,
		'cb4': 200,
		'cb5': 150,
		'cb6': 400,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 300,
		'pf2': 750,
		'pf3': 2300,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 50,   # Match cb1
		'pb2': 80,   # Match cb2
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
		'glottalOpenQuotient': 0.22,  # Increased for brighter upper formants
		'openQuotientShape': 0.5,
		'speedQuotient': 0.7,
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
		'cb1': 55,   # Narrowed for sharper F1 peak
		'cb2': 90,   # Narrowed for sharper F2 peak
		'cb3': 150,
		'cb4': 180,
		'cb5': 150,
		'cb6': 400,
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
		'pb1': 55,   # Match cb1
		'pb2': 90,   # Match cb2
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
		'glottalOpenQuotient': 0.22,  # Increased for brighter upper formants
		'openQuotientShape': 0.5,
		'speedQuotient': 0.7,
		'spectralTilt': 3,
		'flutter': 0.12,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		# Cascade formants - narrower bandwidths for colour
		'cf1': 470,  # Standard close-mid ~450-500
		'cf2': 870,  # Standard ~830-920
		'cf3': 2400,  # Standard ~2380-2500
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 60,   # Narrowed for sharper F1 peak
		'cb2': 90,   # Narrowed for sharper F2 peak
		'cb3': 150,
		'cb4': 180,
		'cb5': 150,
		'cb6': 400,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 470,
		'pf2': 870,
		'pf3': 2400,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 60,   # Match cb1
		'pb2': 90,   # Match cb2
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
		'glottalOpenQuotient': 0.38,  # Increased for brighter upper formants
		'openQuotientShape': 0.5,
		'speedQuotient': 0.8,  # Increased from 0.5 to reduce distortion
		'spectralTilt': 8,  # Increased from 6 to smooth harshness
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
		'cb1': 85,   # Widened from 75 to reduce ringing/distortion
		'cb2': 100,  # Narrowed for sharper F2 peak
		'cb3': 150,
		'cb4': 180,
		'cb5': 150,
		'cb6': 400,
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
		'pb1': 85,   # Match cb1
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
	'ɑ': {  # Open back unrounded
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'fricationAmplitude': 0,
		# Voice quality - tuned to reduce distortion at low pitch
		'glottalOpenQuotient': 0.40,  # Higher for open vowel
		'openQuotientShape': 0.5,
		'speedQuotient': 0.7,
		'spectralTilt': 0,  # No tilt - brighter, matches user tuning
		'flutter': 0.12,
		'lfRd': 2.7,  # Enable LF model for natural glottal pulses
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 240,  # Matched to user preset
		'sinusoidalVoicingAmplitude': 0.3,  # Voicebar for richer low end
		# Cascade formants - wider bandwidths to reduce distortion/ringing
		'cf1': 740,  # Standard open back ~710-770
		'cf2': 1150,  # Standard ~1090-1220
		'cf3': 2550,  # Standard ~2440-2640
		'cf4': 3000,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 131,  # Wider per user tuning - reduces resonance distortion
		'cb2': 192,  # Wider per user tuning
		'cb3': 150,
		'cb4': 180,
		'cb5': 200,
		'cb6': 400,
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
		'pb1': 85,
		'pb2': 100,
		'pb3': 150,
		'pb4': 180,
		'pb5': 200,
		'pb6': 400,
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		# Tracheal formants - adds subglottal coupling for natural resonance
		'ftpFreq1': 1050,  # Tracheal pole - user tuned
		'ftpBw1': 100,
		'ftzFreq1': 600,   # Tracheal zero - user tuned
		'ftzBw1': 360,
		'ftpFreq2': 448,
		'ftpBw2': 408,
		'ftzFreq2': 1000,
		'ftzBw2': 178,
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
		'glottalOpenQuotient': 0.38,  # Increased for brighter upper formants
		'openQuotientShape': 0.5,
		'speedQuotient': 0.6,
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
		'pf1': 620,
		'pf2': 1100,
		'pf3': 2520,
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
		'glottalOpenQuotient': 0.22,  # Increased for brighter upper formants
		'openQuotientShape': 0.5,
		'speedQuotient': 0.7,
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
		'cb1': 50,   # Narrowed for sharper F1 peak
		'cb2': 100,  # Narrowed for sharper F2 peak
		'cb3': 150,
		'cb4': 180,
		'cb5': 200,
		'cb6': 400,
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
		'pb1': 50,   # Match cb1
		'pb2': 100,  # Match cb2
		'pb3': 150,
		'pb4': 180,
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
		'glottalOpenQuotient': 0.22,  # Increased for brighter upper formants
		'openQuotientShape': 0.5,
		'speedQuotient': 0.7,
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
		'pf1': 460,
		'pf2': 1200,
		'pf3': 2550,
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
		'glottalOpenQuotient': 0.38,  # Increased for brighter upper formants
		'openQuotientShape': 0.5,
		'speedQuotient': 0.5,
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
		'cb1': 75,   # Narrowed for sharper F1 peak
		'cb2': 100,  # Narrowed for sharper F2 peak
		'cb3': 150,
		'cb4': 180,
		'cb5': 150,
		'cb6': 400,
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
		'pb1': 75,   # Match cb1
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
