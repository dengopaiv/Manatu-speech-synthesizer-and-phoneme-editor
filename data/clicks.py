# -*- coding: utf-8 -*-
"""
Phoneme data: Click consonants

The 5 IPA click consonants (velaric ingressive airstream mechanism).
True velaric suction cannot be synthesized by the current engine, so
these are approximated using the burst generator with short, sharp
transients — recognizable if not perfect.

Each click is a 2-phase stop:
  Phase 1: Click burst — very short (3-5ms), high-amplitude, characteristic spectrum
  Phase 2: Velar release — short (5-8ms), lower burst mimicking the velar back-release
"""

# Shared base parameters for all clicks
_CLICK_BASE = {
	'_isNasal': False,
	'_isStop': True,
	'_isLiquid': False,
	'_isVowel': False,
	'_isVoiced': False,
	'voiceAmplitude': 0,
	'aspirationAmplitude': 0.3,
	'lfRd': 0,
	'caNP': 0,
	# Neutral (schwa-like) formants — burst dominates perception
	'cf1': 500,
	'cf2': 1500,
	'cf3': 2500,
	'cf4': 3300,
	'cf5': 3750,
	'cf6': 4900,
	'cfNP': 200,
	'cfN0': 250,
	'cb1': 100,
	'cb2': 100,
	'cb3': 150,
	'cb4': 250,
	'cb5': 200,
	'cb6': 1000,
	'cbNP': 100,
	'cbN0': 100,
	'pf1': 500,
	'pf2': 1500,
	'pf3': 2500,
	'pf4': 3300,
	'pf5': 3750,
	'pf6': 4900,
	'pb1': 100,
	'pb2': 100,
	'pb3': 150,
	'pb4': 250,
	'pb5': 200,
	'pb6': 1000,
	'pa1': 0,
	'pa2': 0,
	'pa3': 0,
	'pa4': 0,
	'pa5': 0,
	'pa6': 0,
	'parallelBypass': 0,
	'fricationAmplitude': 0,
	'spectralTilt': 0,
	'flutter': 0,
	'diplophonia': 0,
	'ftpFreq1': 0,
	'ftpBw1': 100,
	'ftzFreq1': 0,
	'ftzBw1': 100,
	'ftpFreq2': 0,
	'ftpBw2': 100,
}


def _make_click(burst_freq, burst_bw):
	"""Create a click phoneme with characteristic burst frequency."""
	entry = dict(_CLICK_BASE)
	entry['_phases'] = [
		{   # Phase 1: Click burst — sharp, short transient
			'_phaseDuration': 4,
			'_phaseFade': 1,
			'burstAmplitude': 1.0,
			'burstDuration': 0.15,
			'burstFilterFreq': burst_freq,
			'burstFilterBw': burst_bw,
			'burstNoiseColor': 0.1,  # White-ish for sharp transient
		},
		{   # Phase 2: Velar back-release
			'_phaseDuration': 6,
			'_phaseFade': 2,
			'burstAmplitude': 0.4,
			'burstDuration': 0.1,
			'burstFilterFreq': 2000,
			'burstFilterBw': 1500,
		},
	]
	return entry


CLICKS = {
	# Bilabial click — diffuse pop, like lip smack
	'ʘ': _make_click(burst_freq=600, burst_bw=800),
	# Dental click — sharp "tsk"
	'ǀ': _make_click(burst_freq=4000, burst_bw=2500),
	# Postalveolar click — loud "cluck"
	'ǃ': _make_click(burst_freq=2500, burst_bw=2000),
	# Palatal click — softer "clop"
	'ǂ': _make_click(burst_freq=3500, burst_bw=1800),
	# Lateral click — lateral "tchk"
	'ǁ': _make_click(burst_freq=5000, burst_bw=3000),
}
