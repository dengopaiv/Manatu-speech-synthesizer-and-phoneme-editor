# -*- coding: utf-8 -*-
"""
Phoneme data: Vowels Nasalized

This file is part of the NV Speech Player project.
Auto-generated from data.py split.

Voice quality is controlled by lfRd parameter (LF model):
- lfRd > 0: Modern LF glottal model (Fant 1995)
- lfRd = 0: No voicing (voiceless consonants only)
"""

VOWELS_NASALIZED = {
	'ã': {  # Nasalized low central
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'spectralTilt': 2,   # Open vowel — fc ~6260 Hz (brighter; was 3)
		'flutter': 0.12,     # Natural F0 jitter
		'cf1': 650,
		'cf2': 1430,
		'cf3': 2500,
		'cf4': 3000,  # Lower F4 for low vowels
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 270,
		'cfN0': 250,
		'cb1': 130,
		'cb2': 286,
		'cb3': 500,
		'cb4': 600,   # Q=5.0 (cf4/5.0 = 3000/5.0) (was 750)
		'cb5': 750,   # Q=5.0 (cf5/5.0 = 3750/5.0) (was 938)
		'cb6': 980,   # Q=5.0 (cf6/5.0 = 4900/5.0) (was 1225)
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0.5,
		'pf1': 650,
		'pf2': 1430,
		'pf3': 2500,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 130,
		'pb2': 286,
		'pb3': 500,
		'pb4': 600,   # Match cb4
		'pb5': 750,   # Match cb5
		'pb6': 980,   # Match cb6
		'pa1': 0,
		'pa2': 0.53,   # Auto-tuned F2 reinforcement
		'pa3': 0.37,   # Auto-tuned F3 reinforcement
		'pa4': 0.5,  # Parallel F4 primary HF source
		'pa5': 0.4,  # Parallel F5 primary HF source
		'pa6': 0.25,  # Parallel F6 primary HF source
		'parallelBypass': 0,
		'parallelVoiceMix': 0.53,  # Auto-tuned voice mix for parallel F2/F3
		'fricationAmplitude': 0,
		# Voice quality
		'lfRd': 1.5,  # Open vowel — less breathy (was 2.0)
		'diplophonia': 0,
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 100,
		'ftzFreq1': 0,
		'ftzBw1': 100,
		'ftpFreq2': 0,
		'ftpBw2': 100,
	},
	'ɛ̃': {  # Nasalized low-mid front
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'spectralTilt': 2,   # Open-mid — fc ~6260 Hz (brighter; was 3)
		'flutter': 0.12,     # Natural F0 jitter
		'cf1': 530,
		'cf2': 1680,
		'cf3': 2500,
		'cf4': 3100,  # Lower F4 for low vowels
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 270,
		'cfN0': 250,
		'cb1': 106,
		'cb2': 336,
		'cb3': 500,
		'cb4': 620,   # Q=5.0 (cf4/5.0 = 3100/5.0) (was 775)
		'cb5': 750,   # Q=5.0 (cf5/5.0 = 3750/5.0) (was 938)
		'cb6': 980,   # Q=5.0 (cf6/5.0 = 4900/5.0) (was 1225)
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0.5,
		'pf1': 530,
		'pf2': 1680,
		'pf3': 2500,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 106,
		'pb2': 336,
		'pb3': 500,
		'pb4': 620,   # Match cb4
		'pb5': 750,   # Match cb5
		'pb6': 980,   # Match cb6
		'pa1': 0,
		'pa2': 0.54,   # Auto-tuned F2 reinforcement
		'pa3': 0.24,   # Auto-tuned F3 reinforcement
		'pa4': 0.5,  # Parallel F4 primary HF source
		'pa5': 0.4,  # Parallel F5 primary HF source
		'pa6': 0.25,  # Parallel F6 primary HF source
		'parallelBypass': 0,
		'parallelVoiceMix': 0.54,  # Auto-tuned voice mix for parallel F2/F3
		'fricationAmplitude': 0,
		# Voice quality
		'lfRd': 1.7,  # Open-mid — less breathy (was 2.3)
		'diplophonia': 0,
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 100,
		'ftzFreq1': 0,
		'ftzBw1': 100,
		'ftpFreq2': 0,
		'ftpBw2': 100,
	},
	'ɔ̃': {  # Nasalized low-mid back
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'spectralTilt': 2,   # Open-mid — fc ~6260 Hz (brighter; was 3)
		'flutter': 0.12,     # Natural F0 jitter
		'cf1': 450,
		'cf2': 870,
		'cf3': 2570,
		'cf4': 3100,  # Lower F4 for low vowels
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 270,
		'cfN0': 250,
		'cb1': 90,
		'cb2': 218,
		'cb3': 514,
		'cb4': 620,   # Q=5.0 (cf4/5.0 = 3100/5.0) (was 775)
		'cb5': 750,   # Q=5.0 (cf5/5.0 = 3750/5.0) (was 938)
		'cb6': 980,   # Q=5.0 (cf6/5.0 = 4900/5.0) (was 1225)
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0.5,
		'pf1': 450,
		'pf2': 870,
		'pf3': 2570,
		'pf4': 3100,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 90,
		'pb2': 218,
		'pb3': 514,
		'pb4': 620,   # Match cb4
		'pb5': 750,   # Match cb5
		'pb6': 980,   # Match cb6
		'pa1': 0,
		'pa2': 0,
		'pa3': 0.41,   # Auto-tuned F3 reinforcement
		'pa4': 0.5,  # Parallel F4 primary HF source
		'pa5': 0.4,  # Parallel F5 primary HF source
		'pa6': 0.25,  # Parallel F6 primary HF source
		'parallelBypass': 0,
		'parallelVoiceMix': 0.41,  # Auto-tuned voice mix for parallel F2/F3
		'fricationAmplitude': 0,
		# Voice quality
		'lfRd': 1.6,  # Open-mid — less breathy (was 2.0)
		'diplophonia': 0,
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 100,
		'ftzFreq1': 0,
		'ftzBw1': 100,
		'ftpFreq2': 0,
		'ftpBw2': 100,
	},
	'œ̃': {  # Nasalized low-mid front rounded
		'_isNasal': False,
		'_isStop': False,
		'_isLiquid': False,
		'_isVowel': True,
		'_isVoiced': True,
		'voiceAmplitude': 1,
		'aspirationAmplitude': 0,
		'spectralTilt': 2,   # Open-mid — fc ~6260 Hz (brighter; was 3)
		'flutter': 0.12,     # Natural F0 jitter
		'cf1': 530,
		'cf2': 1500,
		'cf3': 2500,
		'cf4': 3100,  # Lower F4 for low vowels
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 270,
		'cfN0': 250,
		'cb1': 106,
		'cb2': 300,
		'cb3': 500,
		'cb4': 620,   # Q=5.0 (cf4/5.0 = 3100/5.0) (was 775)
		'cb5': 750,   # Q=5.0 (cf5/5.0 = 3750/5.0) (was 938)
		'cb6': 980,   # Q=5.0 (cf6/5.0 = 4900/5.0) (was 1225)
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0.5,
		'pf1': 530,
		'pf2': 1500,
		'pf3': 2500,
		'pf4': 3300,
		'pf5': 3750,
		'pf6': 4900,
		'pb1': 106,
		'pb2': 300,
		'pb3': 500,
		'pb4': 620,   # Match cb4
		'pb5': 750,   # Match cb5
		'pb6': 980,   # Match cb6
		'pa1': 0,
		'pa2': 0.6,   # Auto-tuned F2 reinforcement
		'pa3': 0.27,   # Auto-tuned F3 reinforcement
		'pa4': 0.5,  # Parallel F4 primary HF source
		'pa5': 0.4,  # Parallel F5 primary HF source
		'pa6': 0.25,  # Parallel F6 primary HF source
		'parallelBypass': 0,
		'parallelVoiceMix': 0.6,  # Auto-tuned voice mix for parallel F2/F3
		'fricationAmplitude': 0,
		# Voice quality
		'lfRd': 1.7,  # Open-mid — less breathy (was 2.3)
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
