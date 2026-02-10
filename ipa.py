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
KLSYN88_DEFAULTS = {
	'lfRd': 1.0,              # Modal voice (LF model enabled)
	'spectralTilt': 0,        # No tilt (modal voice)
	'flutter': 0.25,          # Slight natural jitter
	'openQuotientShape': 0.5, # Moderate exponential
	'speedQuotient': 1.0,     # Symmetric opening/closing
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
	'ʰ': 'aspiration',     # U+02B0 — modifier letter small h
	# Future:
	# 'ʷ': 'labialization',  # U+02B7
	# 'ʲ': 'palatalization',  # U+02B2
	# 'ⁿ': 'prenasalization', # U+207F
}

# Characters that should not be included in multi-char phoneme lookups
_SKIP_IN_MULTICHAR = set('ˈˌː͡ ') | set(TONE_DIACRITICS.keys()) | set(TONE_LETTERS.keys()) | set(CONSONANT_MODIFIERS.keys())

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
		# Check for consonant modifier diacritics (e.g. ʰ for aspiration)
		elif char in CONSONANT_MODIFIERS:
			modifier = CONSONANT_MODIFIERS[char]
			if lastPhonemeRef[0] is not None:
				if modifier == 'aspiration':
					lastPhonemeRef[0]['_hasExplicitAspiration'] = True
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
		elif phoneme:
			stress=phoneme.pop('_stress',0)
			if lastPhoneme and not lastPhoneme.get('_isVowel') and phoneme and phoneme.get('_isVowel'):
				lastPhoneme['_syllableStart']=True
				syllableStartPhoneme=lastPhoneme
			elif stress==1 and lastPhoneme and lastPhoneme.get('_isVowel'):
				phoneme['_syllableStart']=True
				syllableStartPhoneme=phoneme
			# Auto-aspiration: voiceless stop before voiced sound (suppressed if explicit ʰ)
			if lastPhoneme and lastPhoneme.get('_isStop') and not lastPhoneme.get('_isVoiced') and phoneme and phoneme.get('_isVoiced') and not phoneme.get('_isStop') and not phoneme.get('_isAfricate') and not lastPhoneme.get('_hasExplicitAspiration'):
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
				# Add fade-out frame before gap to avoid clicks
				if lastPhoneme and lastPhoneme.get('_isVoiced'):
					fadeOut = lastPhoneme.copy()
					fadeOut['_fadeOutToSilence'] = True
					fadeOut['_char'] = None
					phonemeList.append(fadeOut)
				# Then add the silence gap
				gap=dict(_silence=True,_preStopGap=True)
				phonemeList.append(gap)
			# Phase expansion for affricates with _phases
			phases = phoneme.get('_phases')
			if phases:
				for i, phase in enumerate(phases):
					phaseFrame = {k: v for k, v in phoneme.items() if k != '_phases'}
					phaseFrame.update(phase)
					phaseFrame['_isAffricatePhase'] = True
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
		if phoneme.get('_fadeOutToSilence'):
			# Fade-out frame before gap - smooth transition to silence
			phonemeDuration=10.0/speed
			phonemeFadeDuration=10.0/speed
		elif phoneme.get('_preStopGap'):
			phonemeDuration=20.0/speed  # Was 41ms - reduced to minimize click window
		elif phoneme.get('_postStopAspiration'):
			phonemeDuration=20.0/speed
		elif phoneme.get('_isStop'):
			phonemeDuration=min(10.0/speed,10.0)  # 10ms lets burst resonators develop spectral character
			phonemeFadeDuration=5.0/speed
		elif phoneme.get('_isAffricatePhase'):
			phonemeDuration=phoneme.get('_phaseDuration', 30) / speed
			phonemeFadeDuration=phoneme.get('_phaseFade', 5) / speed
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
		voice_params = ['glottalOpenQuotient', 'spectralTilt', 'speedQuotient',
		                'flutter', 'openQuotientShape', 'lfRd']

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
		if phoneme.get('_silence'):
			yield None,frameDuration,fadeDuration
		else:
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
