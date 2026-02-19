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
		'voiceTurbulenceAmplitude': 0.02,  # Close-mid vowel — light HF fill
		# Voice quality - optimized with LF model
		'spectralTilt': 1,  # Close-mid — reduce from 2 (was above bypass threshold)
		'flutter': 0.12,
		'lfRd': 1.7,  # Close-mid — moderate modality
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 144,  # Scaled ×0.80 (was 180)
		# Cascade formants - narrower bandwidths for colour
		'cf1': 500,  # Standard mid central ~500-520
		'cf2': 1450,  # Standard ~1400-1500
		'cf3': 2450,  # Standard ~2400-2500
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 80,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb2': 232,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 392,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 660,   # Q=5.0 (cf4/5.0 = 3300/5.0)
		'cb5': 750,   # Q=5.0 (cf5/5.0 = 3750/5.0)
		'cb6': 980,   # Q=5.0 (cf6/5.0 = 4900/5.0)
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
		'pb1': 80,   # Match cb1
		'pb2': 232,  # Match cb2
		'pb3': 392,  # Match cb3
		'pb4': 660,   # Match cb4 Q=5.0
		'pb5': 750,   # Match cb5 Q=5.0
		'pb6': 980,   # Match cb6 Q=5.0
		'pa1': 0,
		'pa2': 0.8,   # Auto-tuned F2 reinforcement
		'pa3': 0.37,   # Auto-tuned F3 reinforcement
		'pa4': 0.7,  # Parallel F4 primary HF source
		'pa5': 0.5,  # Parallel F5 primary HF source
		'pa6': 0.3,  # Parallel F6 primary HF source
		'parallelBypass': 0,
		'parallelVoiceMix': 0.8,  # Auto-tuned voice mix for parallel F2/F3
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
		'voiceTurbulenceAmplitude': 0.03,  # Open-mid vowel — moderate HF fill
		# Voice quality - optimized with LF model
		'spectralTilt': 2,  # Open-mid — fc ~6260 Hz (brighter; was 3, ~4675 Hz)
		'flutter': 0.12,
		'lfRd': 1.5,  # Open-mid — less breathy (was 2.0)
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 144,  # Scaled ×0.80 (was 180)
		# Cascade formants - narrower bandwidths for colour
		'cf1': 500,
		'cf2': 1400,
		'cf3': 2300,
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 80,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb2': 224,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 368,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 660,   # Q=5.0 (cf4/5.0 = 3300/5.0)
		'cb5': 750,   # Q=5.0 (cf5/5.0 = 3750/5.0)
		'cb6': 980,   # Q=5.0 (cf6/5.0 = 4900/5.0)
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
		'pb1': 80,   # Match cb1
		'pb2': 224,  # Match cb2
		'pb3': 368,  # Match cb3
		'pb4': 660,   # Match cb4 Q=5.0
		'pb5': 750,   # Match cb5 Q=5.0
		'pb6': 980,   # Match cb6 Q=5.0
		'pa1': 0,
		'pa2': 0.77,   # Auto-tuned F2 reinforcement
		'pa3': 0.37,   # Auto-tuned F3 reinforcement
		'pa4': 0.5,  # Parallel F4 primary HF source
		'pa5': 0.4,  # Parallel F5 primary HF source
		'pa6': 0.25,  # Parallel F6 primary HF source
		'parallelBypass': 0,
		'parallelVoiceMix': 0.77,  # Auto-tuned voice mix for parallel F2/F3
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
		'voiceTurbulenceAmplitude': 0.03,  # Open-mid vowel — moderate HF fill
		# Voice quality - optimized with LF model
		'spectralTilt': 2,  # Open-mid — fc ~6260 Hz (brighter; was 3, ~4675 Hz)
		'flutter': 0.12,
		'lfRd': 1.5,  # Open-mid — less breathy (was 2.0)
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 144,  # Scaled ×0.80 (was 180)
		# Cascade formants - narrower bandwidths for colour
		'cf1': 500,
		'cf2': 1350,
		'cf3': 2100,
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 80,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb2': 216,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 336,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 660,   # Q=5.0 (cf4/5.0 = 3300/5.0)
		'cb5': 750,   # Q=5.0 (cf5/5.0 = 3750/5.0)
		'cb6': 980,   # Q=5.0 (cf6/5.0 = 4900/5.0)
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
		'pb1': 80,   # Match cb1
		'pb2': 216,  # Match cb2
		'pb3': 336,  # Match cb3
		'pb4': 660,   # Match cb4 Q=5.0
		'pb5': 750,   # Match cb5 Q=5.0
		'pb6': 980,   # Match cb6 Q=5.0
		'pa1': 0,
		'pa2': 0.68,   # Auto-tuned F2 reinforcement
		'pa3': 0.4,   # Auto-tuned F3 reinforcement
		'pa4': 0.5,  # Parallel F4 primary HF source
		'pa5': 0.4,  # Parallel F5 primary HF source
		'pa6': 0.25,  # Parallel F6 primary HF source
		'parallelBypass': 0,
		'parallelVoiceMix': 0.68,  # Auto-tuned voice mix for parallel F2/F3
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
		'voiceTurbulenceAmplitude': 0.04,  # Open vowel — strongest HF fill
		# Voice quality - optimized with LF model for open vowel
		'spectralTilt': 2,  # Near-open — fc ~6260 Hz (brighter; was 3, ~4675 Hz)
		'flutter': 0.12,
		'lfRd': 1.5,  # Near-open — less breathy (was 2.0)
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 224,  # Scaled ×0.80 (was 280)
		# Cascade formants - narrower bandwidths for colour
		'cf1': 650,
		'cf2': 1310,
		'cf3': 2400,
		'cf4': 3000,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 104,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb2': 210,  # Q=6.24 (narrowed ×0.80 for clarity)
		'cb3': 384,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 600,   # Q=5.0 (cf4/5.0 = 3000/5.0)
		'cb5': 750,   # Q=5.0 (cf5/5.0 = 3750/5.0)
		'cb6': 980,   # Q=5.0 (cf6/5.0 = 4900/5.0)
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
		'pb1': 104,   # Match cb1
		'pb2': 210,  # Match cb2
		'pb3': 384,  # Match cb3
		'pb4': 600,   # Match cb4 Q=5.0
		'pb5': 750,   # Match cb5 Q=5.0
		'pb6': 980,   # Match cb6 Q=5.0
		'pa1': 0,
		'pa2': 0.39,   # Auto-tuned F2 reinforcement
		'pa3': 0.39,   # Auto-tuned F3 reinforcement
		'pa4': 0.5,  # Parallel F4 primary HF source
		'pa5': 0.4,  # Parallel F5 primary HF source
		'pa6': 0.25,  # Parallel F6 primary HF source
		'parallelBypass': 0,
		'parallelVoiceMix': 0.39,  # Auto-tuned voice mix for parallel F2/F3
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
		'voiceTurbulenceAmplitude': 0.01,  # Close vowel — minimal HF fill
		# Voice quality - optimized with LF model
		'spectralTilt': 0,  # Close vowel — brightest
		'flutter': 0.12,
		'lfRd': 1.0,  # Modal voice — close vowel, maximum HF energy for distant F2/F3
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
		'cb1': 90,   # Widened from 60 — 4th-order F1 needs cb1≥80 for close vowels
		'cb2': 256,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 400,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 660,   # Q=5.0 (cf4/5.0 = 3300/5.0)
		'cb5': 750,   # Q=5.0 (cf5/5.0 = 3750/5.0)
		'cb6': 980,   # Q=5.0 (cf6/5.0 = 4900/5.0)
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
		'pb1': 90,   # Match cb1
		'pb2': 256,  # Match cb2
		'pb3': 400,  # Match cb3
		'pb4': 660,   # Match cb4 Q=5.0
		'pb5': 750,   # Match cb5 Q=5.0
		'pb6': 980,   # Match cb6 Q=5.0
		'pa1': 0,
		'pa2': 0.6,   # Auto-tuned F2 reinforcement
		'pa3': 0.35,   # Auto-tuned F3 reinforcement
		'pa4': 0.8,  # Parallel F4 primary HF source
		'pa5': 0.6,  # Parallel F5 primary HF source
		'pa6': 0.4,  # Parallel F6 primary HF source
		'parallelBypass': 0,
		'parallelVoiceMix': 0.6,  # Auto-tuned voice mix for parallel F2/F3
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
		'voiceTurbulenceAmplitude': 0.01,  # Close vowel — minimal HF fill
		# Voice quality - optimized with LF model
		'spectralTilt': 0,  # Close vowel — brightest
		'flutter': 0.12,
		'lfRd': 1.0,  # Modal voice — close vowel, maximum HF energy for distant F2/F3
		'diplophonia': 0,
		# Cascade formants - Swedish reference tuning (F2≈1700-1800, F3≈2400-2500)
		'cf1': 320,
		'cf2': 1750,
		'cf3': 2450,
		'cf4': 3100,
		'cf5': 3500,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 90,   # Widened from 64 — 4th-order F1 needs cb1≥80 for close vowels
		'cb2': 280,  # Q=6.25 (1750/6.25)
		'cb3': 392,  # Q=6.25 (2450/6.25)
		'cb4': 620,   # Q=5.0 (cf4/5.0 = 3100/5.0)
		'cb5': 700,   # Q=5.0 (cf5/5.0 = 3500/5.0)
		'cb6': 980,   # Q=5.0 (cf6/5.0 = 4900/5.0)
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 320,
		'pf2': 1750,
		'pf3': 2450,
		'pf4': 3100,
		'pf5': 3500,
		'pf6': 4900,
		'pb1': 90,   # Match cb1
		'pb2': 280,  # Match cb2
		'pb3': 392,  # Match cb3
		'pb4': 620,   # Match cb4 Q=5.0
		'pb5': 700,   # Match cb5 Q=5.0
		'pb6': 980,   # Match cb6 Q=5.0
		'pa1': 0,
		'pa2': 0.7,   # Auto-tuned F2 reinforcement
		'pa3': 0.38,   # Auto-tuned F3 reinforcement
		'pa4': 0.8,  # Parallel F4 primary HF source
		'pa5': 0.6,  # Parallel F5 primary HF source
		'pa6': 0.4,  # Parallel F6 primary HF source
		'parallelBypass': 0,
		'parallelVoiceMix': 0.7,  # Auto-tuned voice mix for parallel F2/F3
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
		'voiceTurbulenceAmplitude': 0.02,  # Close-mid vowel — light HF fill
		# Voice quality - optimized with LF model
		'spectralTilt': 1,  # Close-mid — reduce from 2 (was above bypass threshold)
		'flutter': 0.12,
		'lfRd': 1.7,  # Close-mid — moderate modality
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 120,  # Scaled ×0.80 (was 150)
		# Cascade formants - narrower bandwidths for colour
		'cf1': 400,
		'cf2': 1500,
		'cf3': 2400,
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 64,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb2': 240,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 384,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 660,   # Q=5.0 (cf4/5.0 = 3300/5.0)
		'cb5': 750,   # Q=5.0 (cf5/5.0 = 3750/5.0)
		'cb6': 980,   # Q=5.0 (cf6/5.0 = 4900/5.0)
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
		'pb1': 64,   # Match cb1
		'pb2': 240,  # Match cb2
		'pb3': 384,  # Match cb3
		'pb4': 660,   # Match cb4 Q=5.0
		'pb5': 750,   # Match cb5 Q=5.0
		'pb6': 980,   # Match cb6 Q=5.0
		'pa1': 0,
		'pa2': 0.74,   # Auto-tuned F2 reinforcement
		'pa3': 0.33,   # Auto-tuned F3 reinforcement
		'pa4': 0.7,  # Parallel F4 primary HF source
		'pa5': 0.5,  # Parallel F5 primary HF source
		'pa6': 0.3,  # Parallel F6 primary HF source
		'parallelBypass': 0,
		'parallelVoiceMix': 0.74,  # Auto-tuned voice mix for parallel F2/F3
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
		'voiceTurbulenceAmplitude': 0.02,  # Close-mid vowel — light HF fill
		# Voice quality - optimized with LF model
		'spectralTilt': 1,  # Close-mid — reduce from 2 (was above bypass threshold)
		'flutter': 0.12,
		'lfRd': 1.7,  # Close-mid — moderate modality
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 120,  # Scaled ×0.80 (was 150)
		# Cascade formants - narrower bandwidths for colour
		'cf1': 400,
		'cf2': 1400,
		'cf3': 2200,
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 64,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb2': 224,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 352,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 660,   # Q=5.0 (cf4/5.0 = 3300/5.0)
		'cb5': 750,   # Q=5.0 (cf5/5.0 = 3750/5.0)
		'cb6': 980,   # Q=5.0 (cf6/5.0 = 4900/5.0)
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
		'pb1': 64,   # Match cb1
		'pb2': 224,  # Match cb2
		'pb3': 352,  # Match cb3
		'pb4': 660,   # Match cb4 Q=5.0
		'pb5': 750,   # Match cb5 Q=5.0
		'pb6': 980,   # Match cb6 Q=5.0
		'pa1': 0,
		'pa2': 0.75,   # Auto-tuned F2 reinforcement
		'pa3': 0.34,   # Auto-tuned F3 reinforcement
		'pa4': 0.7,  # Parallel F4 primary HF source
		'pa5': 0.5,  # Parallel F5 primary HF source
		'pa6': 0.3,  # Parallel F6 primary HF source
		'parallelBypass': 0,
		'parallelVoiceMix': 0.75,  # Auto-tuned voice mix for parallel F2/F3
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 100,
		'ftzFreq1': 0,
		'ftzBw1': 100,
		'ftpFreq2': 0,
		'ftpBw2': 100,
	},
}
