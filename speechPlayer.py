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

from ctypes import *
import os

speechPlayer_frameParam_t=c_double

class Frame(Structure):
	_fields_=[(name,speechPlayer_frameParam_t) for name in [
		'voicePitch',
		'vibratoPitchOffset',
		'vibratoSpeed',
		'voiceTurbulenceAmplitude',
		'glottalOpenQuotient',
		'voiceAmplitude',
		'sinusoidalVoicingAmplitude',  # AVS: pure sine at F0 for voicebars (0-1)
		'aspirationAmplitude',
		'aspirationFilterFreq',   # Center freq for aspiration bandpass (0=white)
		'aspirationFilterBw',     # Bandwidth of aspiration bandpass filter
		# KLSYN88 voice quality parameters
		'spectralTilt',      # TL: high-frequency attenuation 0-41 dB
		'flutter',           # FL: natural F0 jitter 0-1
		'openQuotientShape', # OQ shape: glottal closing curve 0-1
		'speedQuotient',     # SQ: opening/closing asymmetry 0.5-2.0
		'diplophonia',       # DI: period alternation 0-1
		'lfRd',              # Rd: LF model voice quality 0.3-2.7 (0=use legacy)
		# Tracheal resonances
		'ftpFreq1',          # FTP1: first tracheal pole Hz
		'ftpBw1',            # BTP1: first tracheal pole bandwidth
		'ftzFreq1',          # FTZ1: first tracheal zero Hz
		'ftzBw1',            # BTZ1: first tracheal zero bandwidth
		'ftpFreq2',          # FTP2: second tracheal pole Hz
		'ftpBw2',            # BTP2: second tracheal pole bandwidth
		'ftzFreq2',          # FTZ2: second tracheal zero Hz
		'ftzBw2',            # BTZ2: second tracheal zero bandwidth
		# Glottal modulation (pitch-synchronous F1 variation)
		'deltaF1',           # DF1: F1 increase during glottal open (0-100 Hz)
		'deltaB1',           # DB1: B1 increase during glottal open (0-400 Hz)
		# Stop burst envelope
		'burstAmplitude',    # AB: burst transient 0-1
		'burstDuration',     # DB: burst duration normalized 0-1
		# Cascade formants
		'cf1','cf2','cf3','cf4','cf5','cf6','cfN0','cfNP',
		'cb1','cb2','cb3','cb4','cb5','cb6','cbN0','cbNP',
		'caNP',
		'fricationAmplitude',
		'noiseFilterFreq',    # Center freq for noise bandpass (0=white, >0=bandpass)
		'noiseFilterBw',      # Bandwidth of noise bandpass filter
		'pf1','pf2','pf3','pf4','pf5','pf6',
		'pb1','pb2','pb3','pb4','pb5','pb6',
		'pa1','pa2','pa3','pa4','pa5','pa6',
		'parallelBypass',
		'parallelVoiceMix',    # Fraction of voice signal routed to parallel bank (0-1)
		'preFormantGain',
		'outputGain',
		'endVoicePitch',
		'midVoicePitch',      # Pitch at midpoint for contour tones (0=linear, >0=3-point)
	]]

dllPath=os.path.join(os.path.dirname(__file__),'speechPlayer.dll')

# Define function prototypes for 64-bit compatibility
def _setupDllFunctions(dll):
	# speechPlayer_handle_t speechPlayer_initialize(int sampleRate)
	dll.speechPlayer_initialize.argtypes = [c_int]
	dll.speechPlayer_initialize.restype = c_void_p

	# void speechPlayer_queueFrame(handle, frame*, minDuration, fadeDuration, userIndex, purgeQueue)
	dll.speechPlayer_queueFrame.argtypes = [c_void_p, POINTER(Frame), c_uint, c_uint, c_int, c_bool]
	dll.speechPlayer_queueFrame.restype = None

	# int speechPlayer_synthesize(handle, sampleCount, sampleBuf)
	dll.speechPlayer_synthesize.argtypes = [c_void_p, c_uint, POINTER(c_short)]
	dll.speechPlayer_synthesize.restype = c_int

	# int speechPlayer_getLastIndex(handle)
	dll.speechPlayer_getLastIndex.argtypes = [c_void_p]
	dll.speechPlayer_getLastIndex.restype = c_int

	# void speechPlayer_terminate(handle)
	dll.speechPlayer_terminate.argtypes = [c_void_p]
	dll.speechPlayer_terminate.restype = None

class SpeechPlayer(object):

	def __init__(self,sampleRate):
		self.sampleRate=sampleRate
		self._dll=cdll.LoadLibrary(dllPath)
		_setupDllFunctions(self._dll)
		self._speechHandle=self._dll.speechPlayer_initialize(sampleRate)

	def queueFrame(self,frame,minFrameDuration,fadeDuration,userIndex=-1,purgeQueue=False):
		frame=byref(frame) if frame else None
		self._dll.speechPlayer_queueFrame(self._speechHandle,frame,int(minFrameDuration*(self.sampleRate/1000.0)),int(fadeDuration*(self.sampleRate/1000.0)),userIndex,purgeQueue)

	def synthesize(self,numSamples):
		buf=(c_short*numSamples)()
		res=self._dll.speechPlayer_synthesize(self._speechHandle,numSamples,buf)
		if res>0:
			buf.length=min(res,len(buf))
			return buf
		else:
			return None

	def getLastIndex(self):
		return self._dll.speechPlayer_getLastIndex(self._speechHandle)

	def __del__(self):
		self._dll.speechPlayer_terminate(self._speechHandle)

class VowelChart(object):

	def __init__(self,fileName):
		self._vowels={}
		with open(fileName,'r') as f:
			for line in f.readlines():
				params=line.split()
				vowel=params.pop(0)
				flag=params.pop(0)
				if flag=='1': continue
				starts=[int(params[x]) for x in range(3)]
				ends=[int(params[x]) for x in range(3,6)]
				self._vowels[vowel]=starts,ends

	def applyVowel(self,frame,vowel,end=False):
		data=self._vowels[vowel][0 if not end else 1]
		frame.cf1=data[0]
		frame.cb1=60
		frame.ca1=1
		frame.cf2=data[1]
		frame.cb2=90
		frame.ca2=1
		frame.cf3=data[2]
		frame.cb3=120
		frame.ca3=1
		frame.ca4=frame.ca5=frame.ca6=frame.caN0=frame.caNP=0
		frame.fricationAmplitude=0
		frame.voiceAmplitude=1
		frame.aspirationAmplitude=0
