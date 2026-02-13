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
		'spectralTilt': 1,  # Close-mid — reduce from 2 (was above bypass threshold)
		'flutter': 0.12,     # Natural F0 jitter
		'cf1': 500,
		'cf2': 1350,
		'cf3': 1650,
		'cf4': 2900,  # Lowered F4 for r-coloring (Stevens)
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 80,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb2': 216,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 264,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 725,  # Q=4.0 (was 967)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		'pf1': 500,
		'pf2': 1350,
		'pf3': 1650,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 80,   # Match cb1
		'pb2': 216,  # Match cb2
		'pb3': 264,  # Match cb3
		'pb4': 725,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0.71,   # Auto-tuned F2 reinforcement
		'pa3': 0.53,   # Auto-tuned F3 reinforcement
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'parallelVoiceMix': 0.71,  # Auto-tuned voice mix for parallel F2/F3
		'fricationAmplitude': 0,
		'voiceTurbulenceAmplitude': 0.03,  # Open-mid vowel — moderate HF fill
		# Voice quality
		'lfRd': 1.7,  # Close-mid — moderate modality
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
		'spectralTilt': 1,  # Close-mid — reduce from 2 (was above bypass threshold)
		'flutter': 0.12,     # Natural F0 jitter
		'cf1': 500,
		'cf2': 1400,
		'cf3': 1600,
		'cf4': 2900,  # Lowered F4 for r-coloring (Stevens)
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 80,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb2': 224,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 256,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 725,  # Q=4.0 (was 967)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		'pf1': 500,
		'pf2': 1400,
		'pf3': 1600,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 80,   # Match cb1
		'pb2': 224,  # Match cb2
		'pb3': 256,  # Match cb3
		'pb4': 725,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0.51,   # Auto-tuned F2 reinforcement
		'pa3': 0.47,   # Auto-tuned F3 reinforcement
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'parallelVoiceMix': 0.51,  # Auto-tuned voice mix for parallel F2/F3
		'fricationAmplitude': 0,
		'voiceTurbulenceAmplitude': 0.03,  # Open-mid vowel — moderate HF fill
		# Voice quality
		'lfRd': 1.7,  # Close-mid — moderate modality
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
