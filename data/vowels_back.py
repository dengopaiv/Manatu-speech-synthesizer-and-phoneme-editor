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
		'voiceTurbulenceAmplitude': 0.01,  # Close vowel — minimal HF fill
		# Voice quality - optimized with LF model
		'spectralTilt': 0,  # Close vowel — brightest
		'flutter': 0.10,
		'lfRd': 1.0,  # Modal voice — close vowel, maximum HF energy
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
		'cb1': 90,   # Widened from 60 — 4th-order F1 needs cb1≥80 for close vowels
		'cb2': 139,   # Q=6.26 (narrowed ×0.80 for clarity)
		'cb3': 368,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 825,  # Q=4.0 (was 1100)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
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
		'pb1': 90,   # Match cb1
		'pb2': 139,   # Match cb2
		'pb3': 368,  # Match cb3
		'pb4': 825,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'parallelVoiceMix': 0,
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
		'voiceTurbulenceAmplitude': 0.01,  # Close vowel — minimal HF fill
		# Voice quality - optimized with LF model
		'spectralTilt': 1,  # Near-close — effectively bypass (< 1.5 threshold)
		'flutter': 0.12,  # Normalized from 0.25
		'lfRd': 1.3,  # Near-modal — slightly laxer than close vowels
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
		'cb1': 80,   # 4th-order F1 needs cb1≥80 for close vowels
		'cb2': 168,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 368,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 875,  # Q=4.0 (was 1167)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
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
		'pb1': 80,   # Match cb1
		'pb2': 168,  # Match cb2
		'pb3': 368,  # Match cb3
		'pb4': 875,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'parallelVoiceMix': 0,
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
		'voiceTurbulenceAmplitude': 0.02,  # Close-mid vowel — light HF fill
		# Voice quality - optimized with LF model
		'spectralTilt': 1,  # Close-mid — reduce from 2 (was above bypass threshold)
		'flutter': 0.12,
		'lfRd': 1.7,  # Close-mid — moderate modality
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 120,  # Scaled ×0.80 (was 150)
		# Cascade formants - narrower bandwidths for colour
		'cf1': 400,  # Standard close-mid ~390-500 (Hillenbrand: 390)
		'cf2': 870,  # Standard ~830-920
		'cf3': 2400,  # Standard ~2380-2500
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 64,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb2': 218,   # Q=4.0 (skip — intentionally wide for back vowel F2)
		'cb3': 384,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 825,  # Q=4.0 (was 1100)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
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
		'pb1': 64,   # Match cb1
		'pb2': 218,   # Match cb2
		'pb3': 384,  # Match cb3
		'pb4': 825,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'parallelVoiceMix': 0,
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
		'voiceTurbulenceAmplitude': 0.03,  # Open-mid vowel — moderate HF fill
		# Voice quality - optimized with LF model for open vowel
		'spectralTilt': 3,  # Cutoff ~4675 Hz (was 4)
		'flutter': 0.12,
		'lfRd': 2.2,  # Semi-open — less breathy for HF presence (was 2.7)
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 240,  # Scaled ×0.80 (was 300)
		# Cascade formants - narrower bandwidths for colour
		'cf1': 600,  # Standard open-mid ~570-640
		'cf2': 880,  # Standard ~840-920
		'cf3': 2550,  # Standard ~2410-2680
		'cf4': 3100,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 96,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb2': 220,  # Q=4.0 (skip — intentionally wide for back vowel F2)
		'cb3': 408,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 775,  # Q=4.0 (was 1033)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
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
		'pb1': 96,   # Match cb1
		'pb2': 220,  # Match cb2
		'pb3': 408,  # Match cb3
		'pb4': 775,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'parallelVoiceMix': 0,
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
		'voiceTurbulenceAmplitude': 0.04,  # Open vowel — strongest HF fill
		# Voice quality - optimized with LF model for open vowel
		'spectralTilt': 3,  # Cutoff ~4675 Hz (was 6)
		'flutter': 0.12,
		'lfRd': 2.0,  # More modal voice for open vowel HF presence (was 2.7)
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 280,  # Scaled ×0.80 (was 350)
		# Cascade formants - narrower bandwidths for colour
		'cf1': 740,  # Standard open back ~710-770
		'cf2': 1150,  # Standard ~1090-1220
		'cf3': 2550,  # Standard ~2440-2640
		'cf4': 3000,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 118,   # Q=6.27 (narrowed ×0.80 for clarity)
		'cb2': 288,  # Q=4.0 (skip — intentionally wide for back vowel F2)
		'cb3': 408,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 750,  # Q=4.0 (was 1000)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
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
		'pb1': 118,   # Match cb1
		'pb2': 288,  # Match cb2
		'pb3': 408,  # Match cb3
		'pb4': 750,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0,
		'pa3': 0.35,   # Auto-tuned F3 reinforcement (capped for F1 LPC accuracy)
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'parallelVoiceMix': 0.35,  # Auto-tuned voice mix for parallel F2/F3
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
		'voiceTurbulenceAmplitude': 0.04,  # Open vowel — strongest HF fill
		# Voice quality - optimized with LF model for open vowel
		'spectralTilt': 3,  # Cutoff ~4675 Hz (was 5)
		'flutter': 0.12,
		'lfRd': 2.0,  # More modal voice for open vowel HF presence (was 2.7)
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 256,  # Scaled ×0.80 (was 320)
		# Cascade formants - narrower bandwidths for colour
		'cf1': 620,
		'cf2': 1100,
		'cf3': 2520,
		'cf4': 3000,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 99,   # Q=6.26 (narrowed ×0.80 for clarity)
		'cb2': 275,  # Q=4.0 (skip — intentionally wide for back vowel F2)
		'cb3': 403,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 750,  # Q=4.0 (was 1000)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
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
		'pb1': 99,   # Match cb1
		'pb2': 275,  # Match cb2
		'pb3': 403,  # Match cb3
		'pb4': 750,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0,
		'pa3': 0,
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'parallelVoiceMix': 0,
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
		'voiceTurbulenceAmplitude': 0.01,  # Close vowel — minimal HF fill
		# Voice quality - optimized with LF model
		'spectralTilt': 0,  # Close vowel — brightest
		'flutter': 0.12,
		'lfRd': 1.0,  # Modal voice — close vowel, maximum HF energy
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
		'cb1': 90,   # Widened from 60 — 4th-order F1 needs cb1≥80 for close vowels
		'cb2': 192,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 336,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 875,  # Q=4.0 (was 1167)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
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
		'pb1': 90,   # Match cb1
		'pb2': 192,  # Match cb2
		'pb3': 336,  # Match cb3
		'pb4': 875,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0.37,   # Halved from 0.73 — back unrounded, moderate reinforcement
		'pa3': 0.18,   # Halved from 0.36
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'parallelVoiceMix': 0.37,  # Halved from 0.73
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
		'voiceTurbulenceAmplitude': 0.02,  # Close-mid vowel — light HF fill
		# Voice quality - optimized with LF model
		'spectralTilt': 1,  # Close-mid — reduce from 2 (was above bypass threshold)
		'flutter': 0.12,
		'lfRd': 1.7,  # Close-mid — moderate modality
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 120,  # Scaled ×0.80 (was 150)
		# Cascade formants - narrower bandwidths for colour
		'cf1': 460,
		'cf2': 1200,
		'cf3': 2550,
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 80,   # 4th-order F1 needs cb1≥80 for close-mid vowels
		'cb2': 192,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 408,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 825,  # Q=4.0 (was 1100)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
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
		'pb1': 80,   # Match cb1
		'pb2': 192,  # Match cb2
		'pb3': 408,  # Match cb3
		'pb4': 825,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0.39,   # Halved from 0.77 — back unrounded, moderate reinforcement
		'pa3': 0.21,   # Halved from 0.41
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'parallelVoiceMix': 0.39,  # Halved from 0.77
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
		'voiceTurbulenceAmplitude': 0.03,  # Open-mid vowel — moderate HF fill
		# Voice quality - optimized with LF model for open vowel
		'spectralTilt': 3,  # Cutoff ~4675 Hz (was 5)
		'flutter': 0.12,
		'lfRd': 2.3,  # Open-mid — slightly less breathy (was 2.7)
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 224,  # Scaled ×0.80 (was 280)
		# Cascade formants - narrower bandwidths for colour
		'cf1': 620,
		'cf2': 1220,
		'cf3': 2550,
		'cf4': 3100,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 99,   # Q=6.26 (narrowed ×0.80 for clarity)
		'cb2': 195,  # Q=6.26 (narrowed ×0.80 for clarity)
		'cb3': 408,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 775,  # Q=4.0 (was 1033)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
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
		'pb1': 99,   # Match cb1
		'pb2': 195,  # Match cb2
		'pb3': 408,  # Match cb3
		'pb4': 775,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0.21,   # Halved from 0.42 — back unrounded, moderate reinforcement
		'pa3': 0.21,   # Halved from 0.42
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'parallelVoiceMix': 0.21,  # Halved from 0.42
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 100,
		'ftzFreq1': 0,
		'ftzBw1': 100,
		'ftpFreq2': 0,
		'ftpBw2': 100,
	},
}
