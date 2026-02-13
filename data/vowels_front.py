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
		'voiceTurbulenceAmplitude': 0.04,  # Open vowel — strongest HF fill
		'noiseFilterFreq': 0,
		'noiseFilterBw': 1000,
		# Voice quality - optimized for natural sound with smooth transitions
		'spectralTilt': 3,  # Open vowel — cutoff ~4675 Hz (was 4, ~4065 Hz)
		'flutter': 0.15,
		'lfRd': 1.7,  # Slightly lax voice — less DC offset, more HF in source
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 200,  # Scaled ×0.80 (was 250)
		# Cascade formants - frequency-dependent bandwidths (Q=6.25 for F1-F3, Q=3.0 for F4-F6)
		'cf1': 850,  # Standard open front ~730-850 Hz
		'cf2': 1550,  # Fronted: 240 Hz above /ɐ/ (1310), between /œ/ (1500) and /ɶ/ (1600)
		'cf3': 2500,
		'cf4': 3500,
		'cf5': 4500,
		'cf6': 5000,
		'cb1': 136,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb2': 248,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 400,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 875,   # cf4/4.0 = 3500/4.0 (Q=4.0)
		'cb5': 1125,  # cf5/4.0 = 4500/4.0 (Q=4.0)
		'cb6': 1250,  # cf6/4.0 = 5000/4.0 (Q=4.0)
		'cfNP': 250,
		'cfN0': 250,
		'cbNP': 100,
		'cbN0': 100,
		'caNP': 0,
		# Parallel formants - matched to cascade
		'pf1': 850,
		'pf2': 1550,
		'pf3': 2500,
		'pf4': 3500,
		'pf5': 4500,
		'pf6': 5000,
		'pb1': 136,   # Match cb1
		'pb2': 248,   # Match cb2
		'pb3': 400,   # Match cb3
		'pb4': 875,   # Match cb4
		'pb5': 1125,  # Match cb5
		'pb6': 1250,  # Match cb6
		'pa1': 0,
		'pa2': 0.56,   # Auto-tuned F2 reinforcement
		'pa3': 0.56,   # Auto-tuned F3 reinforcement
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'parallelVoiceMix': 0.56,  # Auto-tuned voice mix for parallel F2/F3
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
		'voiceTurbulenceAmplitude': 0.02,  # Close vowel — mild HF noise fill
		# Voice quality - optimized with LF model
		'spectralTilt': 0,  # Low tilt for bright close vowel
		'flutter': 0.12,
		'lfRd': 1.0,  # Modal voice — phonetically correct for close vowels, ~20-30 dB more energy at F2/F3
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
		'cb1': 65,  # Narrowed F1 bandwidth (Q≈4.3) — sharper peak for LPC accuracy at F0=120 Hz
		'cb2': 400,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 512,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 950,   # cf4/4.0 (Q=4.0)
		'cb5': 1039,  # cf5/4.0 (Q=4.0)
		'cb6': 1225,  # cf6/4.0 (Q=4.0)
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
		'pb1': 65,  # Match cb1
		'pb2': 400,  # Match cb2
		'pb3': 512,  # Match cb3
		'pb4': 950,   # Match cb4
		'pb5': 1039,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0.5,   # Auto-tuned F2 reinforcement (capped for F1 LPC accuracy)
		'pa3': 0.4,   # Auto-tuned F3 reinforcement (capped for F1 LPC accuracy)
		'pa4': 0,     # Cascade handles F4
		'pa5': 0,     # Cascade handles F5
		'pa6': 0,     # Cascade handles F6
		'parallelBypass': 0,
		'parallelVoiceMix': 0.5,  # Auto-tuned voice mix for parallel F2/F3
		# Tracheal formants
		'ftpFreq1': 0,
		'ftpBw1': 95,
		'ftzFreq1': 180,  # Tracheal zero below F1 — attenuates F0/sub-F1 energy for LPC accuracy
		'ftzBw1': 80,  # Moderate BW — cuts sub-F1 without touching F1 peak
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
		'voiceTurbulenceAmplitude': 0.02,  # Close-mid vowel — light HF fill
		# Voice quality - optimized with LF model
		'spectralTilt': 1,  # Close-mid — reduce from 2 (was above bypass threshold)
		'flutter': 0.10,
		'lfRd': 1.7,  # Close-mid — moderate modality
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 120,  # Scaled ×0.80 (was 150)
		# Cascade formants - narrower bandwidths for colour
		'cf1': 400,  # Standard close-mid ~390-480 (Hillenbrand: 390)
		'cf2': 2300,  # Standard ~2020-2290
		'cf3': 3000,  # Standard ~2600-2700
		'cf4': 3500,
		'cf5': 5000,
		'cf6': 5400,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 64,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb2': 368,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 480,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 875,   # cf4/4.0 (Q=4.0)
		'cb5': 1250,  # cf5/4.0 (Q=4.0)
		'cb6': 1350,  # cf6/4.0 (Q=4.0)
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
		'pb1': 64,   # Match cb1
		'pb2': 368,  # Match cb2
		'pb3': 480,  # Match cb3
		'pb4': 875,   # Match cb4
		'pb5': 1250,  # Match cb5
		'pb6': 1350,  # Match cb6
		'pa1': 0,
		'pa2': 0.65,   # Auto-tuned F2 reinforcement
		'pa3': 0.34,   # Auto-tuned F3 reinforcement
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'parallelVoiceMix': 0.65,  # Auto-tuned voice mix for parallel F2/F3
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
		'voiceTurbulenceAmplitude': 0.02,  # Close vowel — mild HF noise fill
		# Voice quality - optimized with LF model
		'spectralTilt': 1,  # Reduced HF attenuation for brightness
		'flutter': 0.12,
		'lfRd': 1.3,  # Near-modal — slightly laxer than /i/ (near-close vowel)
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
		'cb1': 64,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb2': 320,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 416,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 825,  # Q=4.0 (was 1100)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
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
		'pb1': 64,   # Match cb1
		'pb2': 320,  # Match cb2
		'pb3': 416,  # Match cb3
		'pb4': 825,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0.8,   # Auto-tuned F2 reinforcement
		'pa3': 0.6,   # Auto-tuned F3 reinforcement
		'pa4': 0,     # Cascade handles F4
		'pa5': 0,     # Cascade handles F5
		'pa6': 0,     # Cascade handles F6
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
	'ɛ': {  # Open-mid front unrounded
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
		'spectralTilt': 3,  # Cutoff ~4675 Hz (was 5)
		'flutter': 0.10,
		'lfRd': 2.3,  # Open-mid — slightly less breathy (was 2.7)
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 160,  # Scaled ×0.80 (was 200)
		# Cascade formants - narrower bandwidths for colour
		'cf1': 550,  # Standard open-mid ~530-580
		'cf2': 1880,  # Standard ~1840-1920
		'cf3': 2530,  # Standard ~2480-2590
		'cf4': 3100,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 88,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb2': 301,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 405,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 775,  # Q=4.0 (was 1033)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
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
		'pb1': 88,   # Match cb1
		'pb2': 301,  # Match cb2
		'pb3': 405,  # Match cb3
		'pb4': 775,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0.35,   # Auto-tuned F2 reinforcement (capped for F1 LPC accuracy)
		'pa3': 0.2,   # Auto-tuned F3 reinforcement
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
	'æ': {  # Near-open front unrounded (TRAP vowel)
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
		'deltaB1': 280,  # Scaled ×0.80 (was 350)
		# Cascade formants - narrower bandwidths for colour
		'cf1': 700,  # Standard near-open ~660-750
		'cf2': 1780,  # Standard ~1720-1850
		'cf3': 2450,  # Standard ~2410-2500
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 112,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb2': 285,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 392,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 825,  # Q=4.0 (was 1100)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
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
		'pb1': 112,   # Match cb1
		'pb2': 285,  # Match cb2
		'pb3': 392,  # Match cb3
		'pb4': 825,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0.27,   # Auto-tuned F2 reinforcement
		'pa3': 0.27,   # Auto-tuned F3 reinforcement
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'parallelVoiceMix': 0.27,  # Auto-tuned voice mix for parallel F2/F3
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
		'voiceTurbulenceAmplitude': 0.01,  # Close vowel — minimal HF fill
		# Voice quality - optimized with LF model
		'spectralTilt': 0,  # Close vowel — brightest
		'flutter': 0.12,
		'lfRd': 1.0,  # Modal voice — close vowel, maximum HF energy for distant F2/F3
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
		'cb1': 80,  # 4th-order F1 needs cb1≥80 for close vowels
		'cb2': 304,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 336,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 675,  # Q=4.0 (was 900)
		'cb5': 1000,  # Q=4.0 (was 1333)
		'cb6': 1225,  # Q=4.0 (was 1633)
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
		'pb1': 80,  # Match cb1
		'pb2': 304,  # Match cb2
		'pb3': 336,  # Match cb3
		'pb4': 675,  # Match cb4
		'pb5': 1000,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0.54,   # Auto-tuned F2 reinforcement
		'pa3': 0.25,  # Reinforce F3 (2100 Hz)
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'parallelVoiceMix': 0.54,  # Auto-tuned voice mix for parallel F2/F3
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
		'voiceTurbulenceAmplitude': 0.01,  # Close vowel — minimal HF fill
		# Voice quality - optimized with LF model
		'spectralTilt': 1,  # Near-close — effectively bypass (< 1.5 threshold)
		'flutter': 0.12,
		'lfRd': 1.3,  # Near-modal — slightly laxer than close vowels
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
		'cb1': 90,   # Widened from 72 — 4th-order F1 needs cb1≥80 for close vowels
		'cb2': 272,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 352,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 850,  # Q=4.0 (was 1133)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
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
		'pb1': 90,   # Match cb1
		'pb2': 272,  # Match cb2
		'pb3': 352,  # Match cb3
		'pb4': 850,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0.78,   # Auto-tuned F2 reinforcement
		'pa3': 0.4,   # Auto-tuned F3 reinforcement
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
		'parallelBypass': 0,
		'parallelVoiceMix': 0.78,  # Auto-tuned voice mix for parallel F2/F3
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
		'cf2': 1600,
		'cf3': 2400,
		'cf4': 3300,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 64,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb2': 256,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 384,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 825,  # Q=4.0 (was 1100)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
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
		'pb1': 64,   # Match cb1
		'pb2': 256,  # Match cb2
		'pb3': 384,  # Match cb3
		'pb4': 825,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0.74,   # Auto-tuned F2 reinforcement
		'pa3': 0.32,   # Auto-tuned F3 reinforcement
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
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
	'œ': {  # Open-mid front rounded
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
		'spectralTilt': 3,  # Cutoff ~4675 Hz (was 5)
		'flutter': 0.10,
		'lfRd': 2.3,  # Open-mid — slightly less breathy (was 2.7)
		'diplophonia': 0,
		'deltaF1': 0,
		'deltaB1': 160,  # Scaled ×0.80 (was 200)
		# Cascade formants - narrower bandwidths for colour
		'cf1': 530,
		'cf2': 1500,
		'cf3': 2500,
		'cf4': 3100,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 85,   # Q=6.24 (narrowed ×0.80 for clarity)
		'cb2': 240,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 400,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 775,  # Q=4.0 (was 1033)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
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
		'pb1': 85,   # Match cb1
		'pb2': 240,  # Match cb2
		'pb3': 400,  # Match cb3
		'pb4': 775,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0.74,   # Auto-tuned F2 reinforcement
		'pa3': 0.35,   # Auto-tuned F3 reinforcement
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
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
	'ɶ': {  # Open front rounded
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
		'deltaB1': 240,  # Scaled ×0.80 (was 300)
		# Cascade formants - narrower bandwidths for colour
		'cf1': 700,
		'cf2': 1600,
		'cf3': 2500,
		'cf4': 3000,
		'cf5': 3750,
		'cf6': 4900,
		'cfNP': 200,
		'cfN0': 250,
		'cb1': 112,   # Q=6.25 (narrowed ×0.80 for clarity)
		'cb2': 256,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb3': 400,  # Q=6.25 (narrowed ×0.80 for clarity)
		'cb4': 750,  # Q=4.0 (was 1000)
		'cb5': 938,  # Q=4.0 (was 1250)
		'cb6': 1225,  # Q=4.0 (was 1633)
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
		'pb1': 112,   # Match cb1
		'pb2': 256,  # Match cb2
		'pb3': 400,  # Match cb3
		'pb4': 750,  # Match cb4
		'pb5': 938,  # Match cb5
		'pb6': 1225,  # Match cb6
		'pa1': 0,
		'pa2': 0.39,   # Auto-tuned F2 reinforcement
		'pa3': 0.39,   # Auto-tuned F3 reinforcement
		'pa4': 0,
		'pa5': 0,
		'pa6': 0,
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
}
