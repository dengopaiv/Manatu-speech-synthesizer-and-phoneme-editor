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
except ImportError:
	import speechPlayer
	from data import data

def iterPhonemes(**kwargs):
	for k,v in data.items():
		if all(v[x]==y for x,y in kwargs.items()):
			yield k

def setFrame(frame,phoneme):
	values=data[phoneme]
	for k,v in values.items():
		setattr(frame,k,v)

def applyPhonemeToFrame(frame,phoneme):
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
TONE_PITCH_MULTIPLIERS = {
	'extra_high': 1.4,
	'high': 1.2,
	'mid': 1.0,
	'low': 0.85,
	'extra_low': 0.7,
	'rising': (0.85, 1.2),   # start low, end high
	'falling': (1.2, 0.85),  # start high, end low
}

def _parseToneLetters(text, index):
	"""Parse a sequence of tone letters starting at index. Returns (tone_value, chars_consumed)."""
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
	# Convert tone sequence to a value (e.g., ˥˩ = falling from 5 to 1)
	if len(tones) == 1:
		level = tones[0]
		if level >= 4:
			return 'high', consumed
		elif level == 3:
			return 'mid', consumed
		else:
			return 'low', consumed
	else:
		# Contour tone
		if tones[-1] > tones[0]:
			return 'rising', consumed
		else:
			return 'falling', consumed

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
		isLengthened=(text[index+1:index+2]=='ː')
		isTiedTo=(text[index+1:index+2]=='͡')
		isTiedFrom=(text[index-1:index]=='͡') if index>0 else False
		phoneme=None
		if isTiedTo:
			phoneme=data.get(text[index:index+3])
			offset+=2 if phoneme else 1
		elif isLengthened:
			phoneme=data.get(text[index:index+2])
			offset+=1
		if not phoneme:
			phoneme=data.get(char)
		if not phoneme:
			yield char,None
			continue
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
		phoneme['_char']=char
		lastPhonemeRef[0] = phoneme  # Track last phoneme for tone diacritics
		yield char,phoneme

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
			if lastPhoneme and lastPhoneme.get('_isStop') and not lastPhoneme.get('_isVoiced') and phoneme and phoneme.get('_isVoiced') and not phoneme.get('_isStop') and not phoneme.get('_isAfricate'): 
				psa=data['h'].copy()
				psa['_postStopAspiration']=True
				psa['_char']=None
				phonemeList.append(psa)
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
			phonemeList.append(phoneme)
			lastPhoneme=phoneme
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
			phonemeDuration=min(6.0/speed,6.0)
			phonemeFadeDuration=3.0/speed  # Was 0.001 - caused clicks
		elif phoneme.get('_isAfricate'):
			phonemeDuration=24.0/speed
			phonemeFadeDuration=5.0/speed  # Was 0.001 - caused clicks
		elif not phoneme.get('_isVoiced'):
			phonemeDuration=45.0/speed
		else: # is voiced
			if phoneme.get('_isVowel'):
				if lastPhoneme and (lastPhoneme.get('_isLiquid') or lastPhoneme.get('_isSemivowel')): 
					phonemeFadeDuration=25.0/speed
				if phoneme.get('_tiedTo'):
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

def applyToneMarks(phonemeList, basePitch):
	"""Apply tone-based pitch modifications to phonemes that have tone marks."""
	for phoneme in phonemeList:
		tone = phoneme.get('_tone')
		if not tone:
			continue

		multiplier = TONE_PITCH_MULTIPLIERS.get(tone)
		if not multiplier:
			continue

		currentPitch = phoneme.get('voicePitch', basePitch)
		currentEndPitch = phoneme.get('endVoicePitch', currentPitch)

		if isinstance(multiplier, tuple):
			# Contour tone (rising or falling)
			startMult, endMult = multiplier
			phoneme['voicePitch'] = basePitch * startMult
			phoneme['endVoicePitch'] = basePitch * endMult
		else:
			# Level tone
			newPitch = basePitch * multiplier
			phoneme['voicePitch'] = newPitch
			phoneme['endVoicePitch'] = newPitch

def generateFramesAndTiming(ipaText,speed=1,basePitch=100,inflection=0.5,clauseType=None):
	phonemeList=IPAToPhonemes(ipaText)
	if len(phonemeList)==0:
		return
	correctHPhonemes(phonemeList)
	calculatePhonemeTimes(phonemeList,speed)
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
			frame.outputGain=2.0
			applyPhonemeToFrame(frame,phoneme)
			yield frame,frameDuration,fadeDuration
