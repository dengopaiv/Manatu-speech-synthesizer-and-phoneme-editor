###
#This file is a part of the NV Speech Player project. 
#URL: https://bitbucket.org/nvaccess/speechplayer
#Copyright 2014 NV Access Limited.
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License version 2.0, as published by
#the Free Software Foundation.
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#This license can be found at:
#http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
###

import os
import itertools
import codecs
try:
	from . import speechPlayer
	from .data import data
	from .data import transitions
except ImportError:
	import speechPlayer
	from data import data
	from data import transitions

def iterPhonemes(**kwargs):
	for k,v in data.items():
		if all(v[x]==y for x,y in kwargs.items()):
			yield k

def setFrame(frame,phoneme):
	values=data[phoneme]
	for k,v in values.items():
		setattr(frame,k,v)

# KLSYN88 voice quality parameter defaults (neutral/modal voice)
# These ensure backward compatibility - existing phoneme data works unchanged
# Note: Additional derived params (deltaF1, deltaB1, ftzFreq2, ftzBw2,
# sinusoidalVoicingAmplitude, aspirationFilterFreq/Bw) are computed
# dynamically by calculations.py based on phoneme context and voice quality.
# Formant frequencies/bandwidths come from phoneme data files (data/*.py).
KLSYN88_DEFAULTS = {
	'lfRd': 1.0,              # Modal voice (LF model enabled)
	'spectralTilt': 0,        # No tilt (modal voice)
	'flutter': 0.25,          # Slight natural jitter
	'diplophonia': 0,         # No period alternation
	'ftpFreq1': 0,            # Tracheal disabled by default
	'ftpBw1': 100,
	'ftzFreq1': 0,
	'ftzBw1': 100,
	'ftpFreq2': 0,
	'ftpBw2': 100,
	'burstAmplitude': 0,      # No burst by default
	'burstDuration': 0.25,    # 5ms at 20ms max
	'trillRate': 0,           # No trill by default
	'trillDepth': 0,          # No trill by default
	'burstFilterFreq': 0,     # Unfiltered burst by default
	'burstFilterBw': 2000,    # Default bandwidth if filter enabled
	'burstNoiseColor': 0,    # White noise (flat spectrum) by default
	'noiseFilterFreq': 0,     # Unfiltered frication by default
	'noiseFilterBw': 1000,    # Default bandwidth if filter enabled
}

def applyPhonemeToFrame(frame,phoneme):
	# Apply KLSYN88 defaults first for backward compatibility
	for k,v in KLSYN88_DEFAULTS.items():
		setattr(frame,k,v)
	# Then apply phoneme-specific values (override defaults)
	for k,v in phoneme.items():
		if not k.startswith('_'):
			setattr(frame,k,v)

# Tone diacritics (combining characters)
TONE_DIACRITICS = {
	'\u0301': 'high',      # combining acute accent (á)
	'\u0300': 'low',       # combining grave accent (à)
	'\u0304': 'mid',       # combining macron (ā)
	'\u030C': 'rising',    # combining caron (ǎ)
	'\u0302': 'falling',   # combining circumflex (â)
	'\u030B': 'extra_high', # combining double acute (a̋)
	'\u030F': 'extra_low',  # combining double grave (ȁ)
}

# IPA tone letters (placed after syllable)
TONE_LETTERS = {
	'˥': 5,  # extra high
	'˦': 4,  # high
	'˧': 3,  # mid
	'˨': 2,  # low
	'˩': 1,  # extra low
}

# Map tone names to pitch multipliers (relative to base pitch)
# Level tones: single float
# 2-point contours: (start, end) tuple
# 3-point contours: (start, mid, end) tuple - uses midVoicePitch
TONE_PITCH_MULTIPLIERS = {
	# Level tones
	'extra_high': 1.4,
	'high': 1.2,
	'mid': 1.0,
	'low': 0.85,
	'extra_low': 0.7,
	# 2-point contours
	'rising': (0.85, 1.2),   # start low, end high
	'falling': (1.2, 0.85),  # start high, end low
	# 3-point contours (for complex tones like Mandarin tone 3)
	'dipping': (0.9, 0.7, 0.95),     # ˨˩˦ Mandarin tone 3: mid-low→extra-low→mid
	'peaking': (0.85, 1.2, 0.9),    # Low→high→mid (rise-fall)
	'low_rising': (0.7, 0.8, 1.0),  # ˨˧ Cantonese tone 5: low→mid→high
	'high_falling': (1.3, 1.0, 0.7), # ˥˧˩ High→mid→low (gradual fall)
}

def _parseToneLetters(text, index):
	"""Parse a sequence of tone letters starting at index. Returns (tone_value, chars_consumed).

	Handles:
	- Single level tones: ˥ (high), ˧ (mid), ˩ (low)
	- 2-point contours: ˧˥ (rising), ˥˩ (falling)
	- 3-point contours: ˨˩˦ (dipping), ˧˥˧ (peaking)
	"""
	tones = []
	consumed = 0
	while index + consumed < len(text):
		char = text[index + consumed]
		if char in TONE_LETTERS:
			tones.append(TONE_LETTERS[char])
			consumed += 1
		else:
			break
	if not tones:
		return None, 0

	# Single level tone
	if len(tones) == 1:
		level = tones[0]
		if level == 5:
			return 'extra_high', consumed
		elif level >= 4:
			return 'high', consumed
		elif level == 3:
			return 'mid', consumed
		elif level == 2:
			return 'low', consumed
		else:
			return 'extra_low', consumed

	# 2-point contour tone
	elif len(tones) == 2:
		if tones[1] > tones[0]:
			return 'rising', consumed
		else:
			return 'falling', consumed

	# 3+ point contour tone - detect shape
	else:
		start, mid, end = tones[0], tones[len(tones)//2], tones[-1]
		# Dipping: starts mid/low, dips lower, rises (e.g., ˨˩˦)
		if mid < start and end > mid:
			return 'dipping', consumed
		# Peaking: starts lower, rises to peak, falls (e.g., ˧˥˧)
		elif mid > start and mid > end:
			return 'peaking', consumed
		# Low rising: gradual rise from low (e.g., ˨˧˥)
		elif start < mid < end:
			return 'low_rising', consumed
		# High falling: gradual fall from high (e.g., ˥˧˩)
		elif start > mid > end:
			return 'high_falling', consumed
		# Fallback to simple rising/falling based on endpoints
		elif end > start:
			return 'rising', consumed
		else:
			return 'falling', consumed

# Consonant modifier diacritics (superscript letters following a consonant)
CONSONANT_MODIFIERS = {
	'ʰ': 'aspiration',         # U+02B0 — modifier letter small h
	'ʼ': 'ejective',           # U+02BC — modifier letter apostrophe (ejective diacritic)
	'ʷ': 'labialization',      # U+02B7
	'ʲ': 'palatalization',     # U+02B2
	'ˠ': 'velarization',       # U+02E0
	'ˤ': 'pharyngealization',  # U+02E4
}

# Combining diacritics (attached to base character in Unicode)
COMBINING_DIACRITICS = {
	'\u0325': 'voiceless',      # ̥  (combining ring below)
	'\u030A': 'voiceless',      # ̊  (combining ring above — alternate)
	'\u0324': 'breathy',        # ̤  (combining diaeresis below)
	'\u0330': 'creaky',         # ̰  (combining tilde below)
	'\u0303': 'nasalized',      # ̃  (combining tilde)
	'\u0329': 'syllabic',       # ̩  (combining vertical line below)
	'\u032F': 'non_syllabic',   # ̯  (combining inverted breve below)
}

# Characters that should not be included in multi-char phoneme lookups
# Exclude ʼ from skip set so _findLongestPhoneme can match ejective entries (e.g. "pʼ")
_SKIP_IN_MULTICHAR = set('ˈˌː͡ ') | set(TONE_DIACRITICS.keys()) | set(TONE_LETTERS.keys()) | (set(CONSONANT_MODIFIERS.keys()) - {'ʼ'}) | set(COMBINING_DIACRITICS.keys())

def _findLongestPhoneme(text, index, maxLen=4):
	"""Try to match the longest phoneme starting at index.

	This enables diphthongs (2 chars) and triphthongs (3 chars) to be
	looked up directly without requiring tie-bars.

	Args:
		text: The IPA text string
		index: Starting position in text
		maxLen: Maximum phoneme length to try (default 4 for triphthongs + length mark)

	Returns:
		tuple: (matched_string, phoneme_data, length) or (None, None, 0) if no match
	"""
	remaining = len(text) - index
	for length in range(min(maxLen, remaining), 1, -1):  # Try longest first, down to 2
		candidate = text[index:index + length]
		# Skip if candidate contains special characters
		if any(c in _SKIP_IN_MULTICHAR for c in candidate):
			continue
		phoneme = data.get(candidate)
		if phoneme:
			return candidate, phoneme, length
	return None, None, 0

def _applySecondaryArticulation(phoneme, modifier):
	"""Apply a secondary articulation modifier (ʷ ʲ ˠ ˤ) to a phoneme dict."""
	if modifier == 'labialization':
		# Lower F2 toward lip rounding (~700 Hz)
		for key in ('cf2', 'pf2'):
			if key in phoneme:
				phoneme[key] = phoneme[key] * 0.75 + 700 * 0.25
		# Lower F3 toward 2200 Hz (lip rounding lowers F3)
		for key in ('cf3', 'pf3'):
			if key in phoneme:
				phoneme[key] = phoneme[key] * 0.85 + 2200 * 0.15
		# Narrower F2 bandwidth from rounding
		if 'cb2' in phoneme:
			phoneme['cb2'] *= 0.90
	elif modifier == 'palatalization':
		# Raise F2 toward palatal (~2300 Hz)
		for key in ('cf2', 'pf2'):
			if key in phoneme:
				phoneme[key] = phoneme[key] * 0.7 + 2300 * 0.3
		# Raise F3 toward 3200 Hz (tongue body toward palate)
		for key in ('cf3', 'pf3'):
			if key in phoneme:
				phoneme[key] = phoneme[key] * 0.80 + 3200 * 0.20
		# Lower F1 (tongue body rises), floor at 250 Hz
		for key in ('cf1', 'pf1'):
			if key in phoneme:
				phoneme[key] = max(250, phoneme[key] * 0.92)
		# Narrower F2 bandwidth from constriction
		if 'cb2' in phoneme:
			phoneme['cb2'] *= 0.85
	elif modifier == 'velarization':
		# Lower F2 toward velar (~1200 Hz)
		for key in ('cf2', 'pf2'):
			if key in phoneme:
				phoneme[key] = phoneme[key] * 0.75 + 1200 * 0.25
		# Lower F3 toward 2400 Hz
		for key in ('cf3', 'pf3'):
			if key in phoneme:
				phoneme[key] = phoneme[key] * 0.90 + 2400 * 0.10
		# Wider F2 bandwidth from velar backing
		if 'cb2' in phoneme:
			phoneme['cb2'] *= 1.10
	elif modifier == 'pharyngealization':
		# Raise F1 toward ~700 Hz, lower F2 toward ~1000 Hz
		for key in ('cf1', 'pf1'):
			if key in phoneme:
				phoneme[key] = phoneme[key] * 0.7 + 700 * 0.3
		for key in ('cf2', 'pf2'):
			if key in phoneme:
				phoneme[key] = phoneme[key] * 0.75 + 1000 * 0.25
		# Lower F3 toward 2200 Hz
		for key in ('cf3', 'pf3'):
			if key in phoneme:
				phoneme[key] = phoneme[key] * 0.90 + 2200 * 0.10
		# Wider bandwidths from pharyngeal constriction
		if 'cb1' in phoneme:
			phoneme['cb1'] *= 1.20
		if 'cb2' in phoneme:
			phoneme['cb2'] *= 1.15
		# Slight breathiness from pharyngeal constriction
		if phoneme.get('lfRd', 0) > 0:
			phoneme['lfRd'] = min(2.7, phoneme.get('lfRd', 1.0) * 1.15)


def _applyCombiningDiacritic(phoneme, diacritic):
	"""Apply a combining diacritic (̥ ̤ ̰ ̃ ̩ ̯) to a phoneme dict."""
	if diacritic == 'voiceless':
		phoneme['voiceAmplitude'] = 0
		phoneme['lfRd'] = 0
		phoneme['_isVoiced'] = False
	elif diacritic == 'breathy':
		# Relative scaling: blend 60% toward max breathy (2.7)
		currentRd = phoneme.get('lfRd', 1.0)
		if currentRd > 0:
			phoneme['lfRd'] = currentRd + 0.60 * (2.7 - currentRd)
		else:
			phoneme['lfRd'] = 2.5
			phoneme['voiceAmplitude'] = phoneme.get('voiceAmplitude', 0) or 1
		# Spectral tilt: blend toward target of 10 dB
		currentTilt = phoneme.get('spectralTilt', 0)
		phoneme['spectralTilt'] = currentTilt + 0.60 * (10 - currentTilt)
		# Aspiration noise from glottal turbulence
		phoneme['aspirationAmplitude'] = max(phoneme.get('aspirationAmplitude', 0), 0.15)
		# F1 bandwidth expansion from increased airflow
		if 'cb1' in phoneme:
			phoneme['cb1'] *= 1.25
	elif diacritic == 'creaky':
		# Relative scaling: blend 60% toward tight closure (0.3)
		currentRd = phoneme.get('lfRd', 1.0)
		if currentRd > 0:
			phoneme['lfRd'] = currentRd + 0.60 * (0.3 - currentRd)
		else:
			phoneme['lfRd'] = 0.5
			phoneme['voiceAmplitude'] = phoneme.get('voiceAmplitude', 0) or 1
		# Diplophonia: period alternation
		phoneme['diplophonia'] = min(0.5, phoneme.get('diplophonia', 0) + 0.25)
		# More HF energy from tight closure
		phoneme['spectralTilt'] = phoneme.get('spectralTilt', 0) - 2
		# F0 irregularity
		phoneme['flutter'] = min(0.5, phoneme.get('flutter', 0.25) + 0.15)
		# Tighter closure = sharper F1
		if 'cb1' in phoneme:
			phoneme['cb1'] *= 0.85
	elif diacritic == 'nasalized':
		# Nasal pole and zero (vowels and consonants)
		phoneme['caNP'] = 0.5
		phoneme['cfNP'] = 270
		phoneme['cbNP'] = 100
		phoneme['cfN0'] = 250
		phoneme['cbN0'] = 100
		# Vowel-specific modifications: F1 lowering, F2 shifts, bandwidth
		if phoneme.get('_isVowel'):
			cf1 = phoneme.get('cf1', 500)
			# F1 lowering proportional to openness (open vowels lose more)
			lowering = max(0, min(200, (cf1 - 500) * 0.50))
			for key in ('cf1', 'pf1'):
				if key in phoneme:
					phoneme[key] = max(250, phoneme[key] - lowering)
			# F2 lowering ~7%
			for key in ('cf2', 'pf2'):
				if key in phoneme:
					phoneme[key] -= phoneme[key] * 0.07
			# F2 bandwidth expansion ~15% from nasal impedance coupling
			if 'cb2' in phoneme:
				phoneme['cb2'] *= 1.15
			# Voice quality toward modal: blend lfRd 25% toward 2.0
			currentRd = phoneme.get('lfRd', 1.0)
			if currentRd > 0:
				phoneme['lfRd'] = currentRd + 0.25 * (2.0 - currentRd)
	elif diacritic == 'syllabic':
		phoneme['_isSyllabic'] = True
	elif diacritic == 'non_syllabic':
		phoneme['_isNonSyllabic'] = True


def _IPAToPhonemesHelper(text):
	textLen=len(text)
	index=0
	offset=0
	curStress=0
	lastPhonemeRef = [None]  # Use list to allow modification in nested scope
	for index in range(textLen):
		index=index+offset
		if index>=textLen:
			break
		char=text[index]
		if char=='ˈ':
			curStress=1
			continue
		elif char=='ˌ':
			curStress=2
			continue
		# Check for tone diacritics (combining characters following a letter)
		# These apply to the PREVIOUS phoneme since they come after the vowel
		elif char in TONE_DIACRITICS:
			if lastPhonemeRef[0] is not None:
				lastPhonemeRef[0]['_tone'] = TONE_DIACRITICS[char]
			continue
		# Check for tone letters (these also apply to previous syllable)
		elif char in TONE_LETTERS:
			tone, consumed = _parseToneLetters(text, index)
			if tone and lastPhonemeRef[0] is not None:
				lastPhonemeRef[0]['_tone'] = tone
			offset += consumed - 1  # -1 because the loop will advance by 1
			continue
		# Check for combining diacritics (̥ ̤ ̰ ̃ ̩ ̯) — apply to previous phoneme
		elif char in COMBINING_DIACRITICS:
			diacritic = COMBINING_DIACRITICS[char]
			if lastPhonemeRef[0] is not None:
				_applyCombiningDiacritic(lastPhonemeRef[0], diacritic)
			continue
		# Check for consonant modifier diacritics (e.g. ʰ for aspiration, ʷ ʲ ˠ ˤ)
		elif char in CONSONANT_MODIFIERS:
			modifier = CONSONANT_MODIFIERS[char]
			if lastPhonemeRef[0] is not None:
				if modifier == 'aspiration':
					lastPhonemeRef[0]['_hasExplicitAspiration'] = True
				elif modifier == 'ejective':
					if not lastPhonemeRef[0].get('_isEjective'):
						# No explicit ejective entry — yield marker for fallback transformation
						yield 'ʼ', {'_applyEjective': True}
				elif modifier in ('labialization', 'palatalization', 'velarization', 'pharyngealization'):
					_applySecondaryArticulation(lastPhonemeRef[0], modifier)
			continue
		isLengthened=(text[index+1:index+2]=='ː')
		isTiedTo=(text[index+1:index+2]=='͡')
		isTiedFrom=(text[index-1:index]=='͡') if index>0 else False
		phoneme=None
		matchedChars=char  # Track what was actually matched for _char field

		# Try longest-match first for diphthongs/triphthongs
		if not isTiedTo and not isLengthened:
			matchedStr, phoneme, matchLen = _findLongestPhoneme(text, index)
			if phoneme:
				matchedChars = matchedStr
				offset += matchLen - 1  # -1 because loop advances by 1

		# Fall back to tie-bar handling
		if not phoneme and isTiedTo:
			# Try ejective affricate first (base + tie-bar + second + ʼ)
			if index + 3 < textLen and text[index + 3] == 'ʼ':
				phoneme=data.get(text[index:index+4])
				if phoneme:
					matchedChars = text[index:index+4]
					offset+=3
			if not phoneme:
				phoneme=data.get(text[index:index+3])
				if phoneme:
					matchedChars = text[index:index+3]
				offset+=2 if phoneme else 1

		# Fall back to lengthened vowel
		if not phoneme and isLengthened:
			phoneme=data.get(text[index:index+2])
			if phoneme:
				matchedChars = text[index:index+2]
			offset+=1

		# Fall back to single character
		if not phoneme:
			phoneme=data.get(char)
		if not phoneme:
			yield char,None
			continue

		# Look ahead for trailing combining diacritics and secondary articulation modifiers.
		# Apply these BEFORE yielding so stops/affricates get the modifications in their
		# phase expansion (IPAToPhonemes copies the phoneme dict when expanding phases).
		nextPos = index + offset + 1
		pendingModifiers = []
		while nextPos < textLen:
			nextChar = text[nextPos]
			if nextChar in COMBINING_DIACRITICS:
				pendingModifiers.append(('combining', COMBINING_DIACRITICS[nextChar]))
				offset += 1
				nextPos += 1
			elif nextChar in CONSONANT_MODIFIERS:
				mod = CONSONANT_MODIFIERS[nextChar]
				if mod in ('labialization', 'palatalization', 'velarization', 'pharyngealization'):
					pendingModifiers.append(('secondary', mod))
					offset += 1
					nextPos += 1
				else:
					break  # aspiration/ejective handled by the main loop
			else:
				break

		# Check if this is a diphthong/triphthong that needs expansion
		components = phoneme.get('_components')
		if components:
			# Expand diphthong into component vowels
			for i, component_char in enumerate(components):
				component_phoneme = data.get(component_char)
				if not component_phoneme:
					continue
				component_phoneme = component_phoneme.copy()
				# Apply stress only to first component
				if i == 0 and curStress:
					component_phoneme['_stress'] = curStress
					curStress = 0
				# Apply pending modifiers to each component
				for modType, modValue in pendingModifiers:
					if modType == 'combining':
						_applyCombiningDiacritic(component_phoneme, modValue)
					elif modType == 'secondary':
						_applySecondaryArticulation(component_phoneme, modValue)
				# Mark as part of diphthong for potential special handling
				component_phoneme['_inDiphthong'] = True
				component_phoneme['_diphthongChar'] = matchedChars
				component_phoneme['_char'] = component_char
				lastPhonemeRef[0] = component_phoneme
				yield component_char, component_phoneme
		else:
			# Regular phoneme (not a diphthong)
			phoneme=phoneme.copy()
			if curStress:
				phoneme['_stress']=curStress
				curStress=0
			if isTiedFrom:
				phoneme['_tiedFrom']=True
			elif isTiedTo:
				phoneme['_tiedTo']=True
			if isLengthened:
				phoneme['_lengthened']=True
			# Apply pending modifiers BEFORE yielding
			for modType, modValue in pendingModifiers:
				if modType == 'combining':
					_applyCombiningDiacritic(phoneme, modValue)
				elif modType == 'secondary':
					_applySecondaryArticulation(phoneme, modValue)
			phoneme['_char']=matchedChars  # Use matched string (may be diphthong/triphthong)
			lastPhonemeRef[0] = phoneme  # Track last phoneme for tone diacritics
			yield matchedChars,phoneme

def IPAToPhonemes(ipaText):
	phonemeList=[]
	textLength=len(ipaText)
	# Collect phoneme info for each IPA character, assigning diacritics (lengthened, stress) to the last real phoneme
	newWord=True
	lastPhoneme=None
	syllableStartPhoneme=None
	for char,phoneme in _IPAToPhonemesHelper(ipaText):
		if char==' ':
			newWord=True
		elif phoneme and phoneme.get('_applyEjective'):
			# Retroactively apply ejective transformation to last stop/affricate phases
			for i in range(len(phonemeList) - 1, -1, -1):
				entry = phonemeList[i]
				if entry.get('_preStopGap'):
					entry['_closureDuration'] = 18
					break
				if entry.get('_isPhase'):
					entry['aspirationAmplitude'] = 0
					entry['fricationAmplitude'] = 0
					entry['diplophonia'] = 0.15
					entry['burstAmplitude'] = min(entry.get('burstAmplitude', 0) + 0.05, 1.0)
					entry['_isEjective'] = True
		elif phoneme:
			stress=phoneme.pop('_stress',0)
			if lastPhoneme and not lastPhoneme.get('_isVowel') and phoneme and phoneme.get('_isVowel'):
				lastPhoneme['_syllableStart']=True
				syllableStartPhoneme=lastPhoneme
			elif stress==1 and lastPhoneme and lastPhoneme.get('_isVowel'):
				phoneme['_syllableStart']=True
				syllableStartPhoneme=phoneme
			# Auto-aspiration: voiceless stop before voiced sound (suppressed if explicit ʰ or ejective)
			if lastPhoneme and lastPhoneme.get('_isStop') and not lastPhoneme.get('_isVoiced') and not lastPhoneme.get('_isEjective') and phoneme and phoneme.get('_isVoiced') and not phoneme.get('_isStop') and not phoneme.get('_isAfricate') and not lastPhoneme.get('_hasExplicitAspiration'):
				psa=data['h'].copy()
				psa['_postStopAspiration']=True
				psa['_char']=None
				phonemeList.append(psa)
				lastPhoneme=psa
			# Explicit ʰ: insert aspiration after the stop, regardless of what follows
			if lastPhoneme and lastPhoneme.get('_hasExplicitAspiration'):
				psa=data['h'].copy()
				psa['_postStopAspiration']=True
				psa['_char']=None
				phonemeList.append(psa)
				lastPhoneme.pop('_hasExplicitAspiration')
				lastPhoneme=psa
			if newWord:
				newWord=False
				phoneme['_wordStart']=True
				phoneme['_syllableStart']=True
				syllableStartPhoneme=phoneme
			if stress:
				syllableStartPhoneme['_stress']=stress
			elif phoneme.get('_isStop') or phoneme.get('_isAfricate'):
				# Pre-stop closure frame: stop's formant targets with all sound silenced.
				# Formants interpolate toward stop values during closure, so they're
				# at target by burst onset (matches natural articulatory behavior).
				gap = {k: v for k, v in phoneme.items() if not k.startswith('_')}
				gap['_silence'] = True          # Keep: coarticulation skips _silence phonemes
				gap['_preStopGap'] = True       # Keep: calculatePhonemeTimes uses this for 20ms duration
				gap['preFormantGain'] = 0       # No sound output during closure
				gap['burstAmplitude'] = 0       # No burst during closure
				gap['fricationAmplitude'] = 0   # No frication
				gap['voiceAmplitude'] = 0       # No voicing
				gap['aspirationAmplitude'] = 0  # No aspiration
				gap['voiceTurbulenceAmplitude'] = 0
				gap['sinusoidalVoicingAmplitude'] = 0
				if phoneme.get('_isImplosive'):
					# Implosives: maintain voicebar through closure
					gap['voiceAmplitude'] = 0.5
					gap['preFormantGain'] = 0.2
				if phoneme.get('_closureDuration'):
					gap['_closureDuration'] = phoneme['_closureDuration']
				phonemeList.append(gap)
			# Phase expansion for phonemes with _phases (stops, affricates, ejectives)
			phases = phoneme.get('_phases')
			if phases:
				for i, phase in enumerate(phases):
					phaseFrame = {k: v for k, v in phoneme.items() if k != '_phases'}
					phaseFrame.update(phase)
					phaseFrame['_isPhase'] = True
					phaseFrame['_phaseIndex'] = i
					phaseFrame['_phaseCount'] = len(phases)
					phonemeList.append(phaseFrame)
				lastPhoneme = phonemeList[-1]
			else:
				phonemeList.append(phoneme)
				lastPhoneme=phoneme
	# Handle trailing explicit aspiration (word-final tʰ)
	if lastPhoneme and lastPhoneme.get('_hasExplicitAspiration'):
		psa=data['h'].copy()
		psa['_postStopAspiration']=True
		psa['_char']=None
		phonemeList.append(psa)
		lastPhoneme.pop('_hasExplicitAspiration')
	return phonemeList

def resolve_ipa_phoneme(ipa_text):
	"""Resolve an IPA string into phoneme parameters with diacritic tracking.

	Returns list of dicts, each with:
	  - 'char': the matched IPA string
	  - 'params': full parameter dict (with diacritics applied, pre-phase-expansion)
	  - 'base_char': the base phoneme character (without diacritics)
	  - 'base_params': the unmodified base phoneme params (for diff display)
	"""
	modifier_chars = set(CONSONANT_MODIFIERS.keys()) | set(COMBINING_DIACRITICS.keys()) | set(TONE_DIACRITICS.keys())

	results = []
	for char, phoneme in _IPAToPhonemesHelper(ipa_text):
		if phoneme is None:
			continue
		if phoneme.get('_applyEjective'):
			# Retroactively mark the previous result as ejective
			if results:
				prev = results[-1]
				params = prev['params']
				# Apply ejective transformation to the params
				params['_isEjective'] = True
				prev['char'] = prev['char'] + 'ʼ'
			continue
		# Determine the base character by stripping modifier/diacritic chars
		matched = phoneme.get('_char', char)
		base_char = ''.join(c for c in matched if c not in modifier_chars)
		if not base_char:
			base_char = matched
		# Look up unmodified base params
		base_params = data.get(base_char, {}).copy()
		results.append({
			'char': char,
			'params': phoneme,
			'base_char': base_char,
			'base_params': base_params,
		})
	return results

def correctHPhonemes(phonemeList):
	finalPhonemeIndex=len(phonemeList)-1
	# Correct all h phonemes (including inserted aspirations) so that their formants match the next phoneme, or the previous if there is no next
	for index in range(len(phonemeList)):
		prevPhoneme=phonemeList[index-1] if index>0 else None
		curPhoneme=phonemeList[index]
		nextPhoneme=phonemeList[index+1] if index<finalPhonemeIndex else None
		if curPhoneme.get('_copyAdjacent'):
			adjacent=nextPhoneme if nextPhoneme and not nextPhoneme.get('_silence') else prevPhoneme 
			if adjacent:
				for k,v in adjacent.items():
					if not k.startswith('_') and k not in curPhoneme:
						curPhoneme[k]=v

def calculatePhonemeTimes(phonemeList,baseSpeed):
	lastPhoneme=None
	syllableStress=0
	speed=baseSpeed
	for index,phoneme in enumerate(phonemeList):
		nextPhoneme=phonemeList[index+1] if len(phonemeList)>index+1 else None
		syllableStart=phoneme.get('_syllableStart')
		if syllableStart:
			syllableStress=phoneme.get('_stress')
			if syllableStress:
				speed=baseSpeed/1.4 if syllableStress==1 else baseSpeed/1.1
			else:
				speed=baseSpeed
		phonemeDuration=60.0/speed
		phonemeFadeDuration=10.0/speed
		if phoneme.get('_preStopGap'):
			phonemeDuration=phoneme.get('_closureDuration', 12.0) / speed
		elif phoneme.get('_postStopAspiration'):
			phonemeDuration=15.0/speed
		elif phoneme.get('_isPhase'):
			phonemeDuration=phoneme.get('_phaseDuration', 30) / speed
			phonemeFadeDuration=phoneme.get('_phaseFade', 5) / speed
		elif phoneme.get('_isStop'):
			phonemeDuration=10.0/speed
			phonemeFadeDuration=3.0/speed
		elif phoneme.get('_isAfricate'):
			phonemeDuration=24.0/speed
			phonemeFadeDuration=5.0/speed  # Was 0.001 - caused clicks
		elif not phoneme.get('_isVoiced'):
			phonemeDuration=45.0/speed
		else: # is voiced
			if phoneme.get('_isVowel'):
				if lastPhoneme and (lastPhoneme.get('_isLiquid') or lastPhoneme.get('_isSemivowel')):
					phonemeFadeDuration=25.0/speed
				# Special handling for diphthong/triphthong components
				if phoneme.get('_inDiphthong'):
					# Check if this is first component or subsequent
					if lastPhoneme and lastPhoneme.get('_inDiphthong') and lastPhoneme.get('_diphthongChar') == phoneme.get('_diphthongChar'):
						# Subsequent component: longer glide fade for smooth transitions
						phonemeDuration=40.0/speed  # Increased from 30
						phonemeFadeDuration=60.0/speed  # Increased from 45 for smoother KLSYN param glide
					else:
						# First component of diphthong
						phonemeDuration=50.0/speed  # Increased from 40
						phonemeFadeDuration=25.0/speed  # Increased from 15
				elif phoneme.get('_tiedTo'):
					phonemeDuration=40.0/speed
				elif phoneme.get('_tiedFrom'):
					phonemeDuration=20.0/speed
					phonemeFadeDuration=20.0/speed
				elif not syllableStress and not syllableStart and nextPhoneme and not nextPhoneme.get('_wordStart') and (nextPhoneme.get('_isLiquid') or nextPhoneme.get('_isNasal')):
					if nextPhoneme.get('_isLiquid'):
						phonemeDuration=30.0/speed
					else:
						phonemeDuration=40.0/speed
			else: # not a vowel
				phonemeDuration=30.0/speed
				if phoneme.get('_isLiquid') or phoneme.get('_isSemivowel'):
					phonemeFadeDuration=20.0/speed
		if phoneme.get('_lengthened'):
			phonemeDuration*=1.05
		phoneme['_duration']=phonemeDuration
		phoneme['_fadeDuration']=phonemeFadeDuration
		lastPhoneme=phoneme

def applyPitchPath(phonemeList,startIndex,endIndex,basePitch,inflection,startPitchPercent,endPitchPercent):
	startPitch=basePitch*(2**(((startPitchPercent-50)/50.0)*inflection))
	endPitch=basePitch*(2**(((endPitchPercent-50)/50.0)*inflection))
	voicedDuration=0
	for index in range(startIndex,endIndex):
		phoneme=phonemeList[index]
		if phoneme.get('_isVoiced'):
			voicedDuration+=phoneme['_duration']
	curDuration=0
	pitchDelta=endPitch-startPitch
	curPitch=startPitch
	syllableStress=False
	for index in range(startIndex,endIndex):
		phoneme=phonemeList[index]
		phoneme['voicePitch']=curPitch
		if phoneme.get('_isVoiced'):
			curDuration+=phoneme['_duration']
			pitchRatio=curDuration/float(voicedDuration)
			curPitch=startPitch+(pitchDelta*pitchRatio)
		phoneme['endVoicePitch']=curPitch

intonationParamTable={
	'.':{
		'preHeadStart':46,
		'preHeadEnd':57,
		'headExtendFrom':4,
		'headStart':80,
		'headEnd':50,
		'headSteps':[100,75,50,25,0,63,38,13,0],
		'headStressEndDelta':-16,
		'headUnstressedRunStartDelta':-8,
		'headUnstressedRunEndDelta':-5,
		'nucleus0Start':64,
		'nucleus0End':8,
		'nucleusStart':70,
		'nucleusEnd':18,
		'tailStart':24,
		'tailEnd':8,
	},
	',':{
		'preHeadStart':46,
		'preHeadEnd':57,
		'headExtendFrom':4,
		'headStart':80,
		'headEnd':60,
		'headSteps':[100,75,50,25,0,63,38,13,0],
		'headStressEndDelta':-16,
		'headUnstressedRunStartDelta':-8,
		'headUnstressedRunEndDelta':-5,
		'nucleus0Start':34,
		'nucleus0End':52,
		'nucleusStart':78,
		'nucleusEnd':34,
		'tailStart':34,
		'tailEnd':52,
	},
	'?':{
		'preHeadStart':45,
		'preHeadEnd':56,
		'headExtendFrom':3,
		'headStart':75,
		'headEnd':43,
		'headSteps':[100,75,50,20,60,35,11,0],
		'headStressEndDelta':-16,
		'headUnstressedRunStartDelta':-7,
		'headUnstressedRunEndDelta':0,
		'nucleus0Start':34,
		'nucleus0End':68,
		'nucleusStart':86,
		'nucleusEnd':21,
		'tailStart':34,
		'tailEnd':68,
	},
	'!':{
		'preHeadStart':46,
		'preHeadEnd':57,
		'headExtendFrom':3,
		'headStart':90,
		'headEnd':50,
		'headSteps':[100,75,50,16,82,50,32,16],
		'headStressEndDelta':-16,
		'headUnstressedRunStartDelta':-9,
		'headUnstressedRunEndDelta':0,
		'nucleus0Start':92,
		'nucleus0End':4,
		'nucleusStart':92,
		'nucleusEnd':80,
		'tailStart':76,
		'tailEnd':4,
	}
}

def calculatePhonemePitches(phonemeList,speed,basePitch,inflection,clauseType):
	intonationParams=intonationParamTable[clauseType or '.']
	preHeadStart=0
	preHeadEnd=len(phonemeList)
	for index,phoneme in enumerate(phonemeList):
		if phoneme.get('_syllableStart'):
			syllableStress=phoneme.get('_stress')==1
			if syllableStress:
				preHeadEnd=index
				break
	if (preHeadEnd-preHeadStart)>0:
		applyPitchPath(phonemeList,preHeadStart,preHeadEnd,basePitch,inflection,intonationParams['preHeadStart'],intonationParams['preHeadEnd'])
	nucleusStart=nucleusEnd=tailStart=tailEnd=len(phonemeList)
	for index in range(nucleusEnd-1,preHeadEnd-1,-1):
		phoneme=phonemeList[index]
		if phoneme.get('_syllableStart'):
			syllableStress=phoneme.get('_stress')==1
			if syllableStress :
				nucleusStart=index
				break
			else:
				nucleusEnd=tailStart=index
	hasTail=(tailEnd-tailStart)>0
	if hasTail:
		applyPitchPath(phonemeList,tailStart,tailEnd,basePitch,inflection,intonationParams['tailStart'],intonationParams['tailEnd'])
	if (nucleusEnd-nucleusStart)>0:
		if hasTail:
			applyPitchPath(phonemeList,nucleusStart,nucleusEnd,basePitch,inflection,intonationParams['nucleusStart'],intonationParams['nucleusEnd'])
		else:
			applyPitchPath(phonemeList,nucleusStart,nucleusEnd,basePitch,inflection,intonationParams['nucleus0Start'],intonationParams['nucleus0End'])
	if preHeadEnd<nucleusStart:
		headStartPitch=intonationParams['headStart']
		headEndPitch=intonationParams['headEnd']
		lastHeadStressStart=None
		lastHeadUnstressedRunStart=None
		stressEndPitch=None
		steps=intonationParams['headSteps']
		extendFrom=intonationParams['headExtendFrom']
		stressStartPercentageGen=itertools.chain(steps,itertools.cycle(steps[extendFrom:]))
		for index in range(preHeadEnd,nucleusStart+1):
			phoneme=phonemeList[index]
			syllableStress=phoneme.get('_stress')==1
			if phoneme.get('_syllableStart'):
				if lastHeadStressStart is not None:
					stressStartPitch=headEndPitch+(((headStartPitch-headEndPitch)/100.0)*next(stressStartPercentageGen))
					stressEndPitch=stressStartPitch+intonationParams['headStressEndDelta']
					applyPitchPath(phonemeList,lastHeadStressStart,index,basePitch,inflection,stressStartPitch,stressEndPitch)
					lastHeadStressStart=None
				if syllableStress :
					if lastHeadUnstressedRunStart is not None:
						unstressedRunStartPitch=stressEndPitch+intonationParams['headUnstressedRunStartDelta']
						unstressedRunEndPitch=stressEndPitch+intonationParams['headUnstressedRunEndDelta']
						applyPitchPath(phonemeList,lastHeadUnstressedRunStart,index,basePitch,inflection,unstressedRunStartPitch,unstressedRunEndPitch)
						lastHeadUnstressedRunStart=None
					lastHeadStressStart=index
				elif lastHeadUnstressedRunStart is None: 
					lastHeadUnstressedRunStart=index

def _blend_diphthong_voice_quality(phonemeList):
	"""Blend voice quality parameters between diphthong components for smoother glides.

	Since the C++ synthesizer interpolates ALL parameters during fade (including
	voice quality params like spectralTilt, glottalOpenQuotient, etc.), large
	differences between diphthong components can cause audible voice quality changes.

	This function averages key voice quality parameters across diphthong components
	so the interpolation results in smoother, more natural glides.
	"""
	# Track which diphthongs we've already processed
	processed_diphthongs = set()

	for phoneme in phonemeList:
		if not phoneme.get('_inDiphthong'):
			continue

		diphthong_char = phoneme.get('_diphthongChar')
		if diphthong_char in processed_diphthongs:
			continue

		# Find all components of this diphthong
		components = [p for p in phonemeList
		              if p.get('_diphthongChar') == diphthong_char and p.get('_inDiphthong')]

		if len(components) < 2:
			continue

		processed_diphthongs.add(diphthong_char)

		# Voice quality parameters to blend
		voice_params = ['spectralTilt', 'flutter', 'lfRd']

		for param in voice_params:
			values = [c.get(param) for c in components if param in c and c.get(param) is not None]
			if len(values) >= 2:
				# Use weighted average: first component gets more weight (60/40 split)
				# This preserves more of the starting vowel's character
				if len(values) == 2:
					avg = values[0] * 0.6 + values[1] * 0.4
				else:
					avg = sum(values) / len(values)
				for c in components:
					c[param] = avg

def applyFormantScaling(frame, scale_factor):
	"""
	Scale all formant frequencies and bandwidths by a factor.

	Used for voice type modification (male/female/child).
	Female voices typically use scale ~1.17, children ~1.35.

	Args:
		frame: speechPlayer.Frame object
		scale_factor: float, 1.0 = no change, >1 = higher formants (smaller vocal tract)
	"""
	if scale_factor == 1.0:
		return  # No scaling needed

	# Scale cascade formant frequencies and bandwidths (cf1-cf6, cb1-cb6)
	for i in range(1, 7):
		cf_name = f'cf{i}'
		cb_name = f'cb{i}'
		current_freq = getattr(frame, cf_name, 0)
		if current_freq > 0:
			setattr(frame, cf_name, current_freq * scale_factor)
		current_bw = getattr(frame, cb_name, 0)
		if current_bw > 0:
			setattr(frame, cb_name, current_bw * scale_factor)

	# Scale nasal formants
	if getattr(frame, 'cfNP', 0) > 0:
		frame.cfNP *= scale_factor
		frame.cbNP *= scale_factor
	if getattr(frame, 'cfN0', 0) > 0:
		frame.cfN0 *= scale_factor
		frame.cbN0 *= scale_factor

	# Scale parallel formant frequencies and bandwidths (pf1-pf6, pb1-pb6)
	for i in range(1, 7):
		pf_name = f'pf{i}'
		pb_name = f'pb{i}'
		current_freq = getattr(frame, pf_name, 0)
		if current_freq > 0:
			setattr(frame, pf_name, current_freq * scale_factor)
		current_bw = getattr(frame, pb_name, 0)
		if current_bw > 0:
			setattr(frame, pb_name, current_bw * scale_factor)


def applyToneMarks(phonemeList, basePitch):
	"""Apply tone-based pitch modifications to phonemes that have tone marks.

	Handles:
	- Level tones: single multiplier → constant pitch
	- 2-point contours: (start, end) → linear interpolation (midVoicePitch=0)
	- 3-point contours: (start, mid, end) → two-phase interpolation via midVoicePitch
	"""
	for phoneme in phonemeList:
		tone = phoneme.get('_tone')
		if not tone:
			continue

		multiplier = TONE_PITCH_MULTIPLIERS.get(tone)
		if not multiplier:
			continue

		if isinstance(multiplier, tuple):
			if len(multiplier) == 3:
				# 3-point contour tone (e.g., dipping, peaking)
				# Uses midVoicePitch for proper contour shape
				startMult, midMult, endMult = multiplier
				phoneme['voicePitch'] = basePitch * startMult
				phoneme['midVoicePitch'] = basePitch * midMult
				phoneme['endVoicePitch'] = basePitch * endMult
			else:
				# 2-point contour tone (rising or falling)
				# Linear interpolation between start and end
				startMult, endMult = multiplier
				phoneme['voicePitch'] = basePitch * startMult
				phoneme['midVoicePitch'] = 0  # Signal linear interpolation
				phoneme['endVoicePitch'] = basePitch * endMult
		else:
			# Level tone - constant pitch throughout
			newPitch = basePitch * multiplier
			phoneme['voicePitch'] = newPitch
			phoneme['midVoicePitch'] = 0
			phoneme['endVoicePitch'] = newPitch

def generateFramesAndTiming(ipaText, speed=1, basePitch=100, inflection=0.5, clauseType=None,
                           formantScale=1.0, spectralTilt=None, voiceTurbulence=None, flutter=None):
	"""
	Generate synthesis frames from IPA text.

	Args:
		ipaText: IPA string to synthesize
		speed: Speech rate multiplier (default 1.0)
		basePitch: Fundamental frequency in Hz (default 100)
		inflection: Pitch variation amount 0-1 (default 0.5)
		clauseType: Punctuation for intonation ('.', ',', '?', '!')
		formantScale: Factor to multiply formant frequencies (1.0=male, 1.17=female, 1.35=child)
		spectralTilt: Override spectral tilt in dB (higher=breathier)
		voiceTurbulence: Override voice turbulence amplitude 0-1
		flutter: Override flutter amount for pitch jitter
	"""
	phonemeList=IPAToPhonemes(ipaText)
	if len(phonemeList)==0:
		return
	correctHPhonemes(phonemeList)
	calculatePhonemeTimes(phonemeList,speed)
	transitions.apply_coarticulation(phonemeList, speed)  # Apply CV coarticulation
	_blend_diphthong_voice_quality(phonemeList)  # Blend voice quality for smoother diphthong glides
	calculatePhonemePitches(phonemeList,speed,basePitch,inflection,clauseType)
	applyToneMarks(phonemeList, basePitch)  # Apply tone marks after standard intonation
	for phoneme in phonemeList:
		frameDuration=phoneme.pop('_duration')
		fadeDuration=phoneme.pop('_fadeDuration')
		if phoneme.get('_silence') and not phoneme.get('_preStopGap'):
			yield None,frameDuration,fadeDuration
		else:
			# Extract onset/offset values (pop removes them so applyPhonemeToFrame won't see them)
			onset_cf2 = phoneme.pop('_onset_cf2', None)
			onset_cf3 = phoneme.pop('_onset_cf3', None)
			offset_cf2 = phoneme.pop('_offset_cf2', None)
			offset_cf3 = phoneme.pop('_offset_cf3', None)

			if onset_cf2 is not None:
				# Create onset waypoint frame (copy of vowel with locus-derived formants)
				onset_frame = speechPlayer.Frame()
				onset_frame.preFormantGain = 1.0
				onset_frame.outputGain = 1.0
				applyPhonemeToFrame(onset_frame, phoneme)
				applyFormantScaling(onset_frame, formantScale)
				if spectralTilt is not None:
					onset_frame.spectralTilt = spectralTilt
				if voiceTurbulence is not None:
					onset_frame.voiceTurbulenceAmplitude = voiceTurbulence
				if flutter is not None:
					onset_frame.flutter = flutter
				# Override formants with locus-derived onset values (scaled for voice type)
				onset_frame.cf2 = onset_cf2 * formantScale
				if onset_cf3 is not None:
					onset_frame.cf3 = onset_cf3 * formantScale
				# Yield onset waypoint: 1ms duration, 70% of original fade
				yield onset_frame, 1.0, fadeDuration * 0.7
				# Remaining 30% for onset->target
				fadeDuration = fadeDuration * 0.3

			frame=speechPlayer.Frame()
			frame.preFormantGain=1.0
			frame.outputGain=1.0
			applyPhonemeToFrame(frame,phoneme)

			# Apply voice type modifications
			applyFormantScaling(frame, formantScale)

			# Override voice quality parameters if specified
			if spectralTilt is not None:
				frame.spectralTilt = spectralTilt
			if voiceTurbulence is not None:
				frame.voiceTurbulenceAmplitude = voiceTurbulence
			if flutter is not None:
				frame.flutter = flutter

			yield frame,frameDuration,fadeDuration

			if offset_cf2 is not None:
				# Create offset waypoint frame (copy of vowel with locus-derived formants)
				offset_frame = speechPlayer.Frame()
				offset_frame.preFormantGain = 1.0
				offset_frame.outputGain = 1.0
				applyPhonemeToFrame(offset_frame, phoneme)
				applyFormantScaling(offset_frame, formantScale)
				if spectralTilt is not None:
					offset_frame.spectralTilt = spectralTilt
				if voiceTurbulence is not None:
					offset_frame.voiceTurbulenceAmplitude = voiceTurbulence
				if flutter is not None:
					offset_frame.flutter = flutter
				# Override formants with locus-derived offset values
				offset_frame.cf2 = offset_cf2 * formantScale
				if offset_cf3 is not None:
					offset_frame.cf3 = offset_cf3 * formantScale
				# Yield offset waypoint: 1ms hold, 30ms fade (VC transition)
				yield offset_frame, 1.0, 30.0
