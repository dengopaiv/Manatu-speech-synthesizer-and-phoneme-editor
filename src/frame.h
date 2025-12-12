/*
This file is a part of the NV Speech Player project. 
URL: https://bitbucket.org/nvaccess/speechplayer
Copyright 2014 NV Access Limited.
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2.0, as published by
the Free Software Foundation.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
This license can be found at:
http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
*/

#ifndef SPEECHPLAYER_FRAME_H
#define SPEECHPLAYER_FRAME_H

#include "lock.h"

typedef double speechPlayer_frameParam_t;

typedef struct {
	// voicing and cascaide
	speechPlayer_frameParam_t voicePitch; //  fundermental frequency of voice (phonation) in hz
	speechPlayer_frameParam_t vibratoPitchOffset; // pitch is offset up or down in fraction of a semitone
	speechPlayer_frameParam_t vibratoSpeed; // Speed of vibrato in hz
	speechPlayer_frameParam_t voiceTurbulenceAmplitude; // amplitude of voice breathiness from 0 to 1 
	speechPlayer_frameParam_t glottalOpenQuotient; // fraction between 0 and 1 of a voice cycle that the glottis is open (allows voice turbulance, alters f1...)
	speechPlayer_frameParam_t voiceAmplitude; // amplitude of voice (phonation) source between 0 and 1.
	speechPlayer_frameParam_t sinusoidalVoicingAmplitude; // AVS: pure sine wave at F0 for voicebars/voiced fricatives (0-1)
	speechPlayer_frameParam_t aspirationAmplitude; // amplitude of aspiration (voiceless h, whisper) source between 0 and 1.
	speechPlayer_frameParam_t aspirationFilterFreq; // center freq for aspiration bandpass filter (0=white noise)
	speechPlayer_frameParam_t aspirationFilterBw; // bandwidth of aspiration bandpass filter in Hz
	// KLSYN88 voice quality parameters
	speechPlayer_frameParam_t spectralTilt; // TL: high-frequency attenuation 0-41 dB at 3kHz (0=no tilt, modal voice)
	speechPlayer_frameParam_t flutter; // FL: natural F0 jitter 0-1 (0.25 typical for natural speech)
	speechPlayer_frameParam_t openQuotientShape; // OQ shape: glottal closing curve 0-1 (0=linear, 1=exponential decay)
	speechPlayer_frameParam_t speedQuotient; // SQ: opening/closing time asymmetry 0.5-2.0 (1.0=symmetric)
	speechPlayer_frameParam_t diplophonia; // DI: period alternation for creaky voice 0-1 (0=none)
	speechPlayer_frameParam_t lfRd; // Rd: LF model voice quality 0.3-2.7 (0=use legacy, <1=tense, 1=modal, >1=lax/breathy)
	// Tracheal/subglottal resonances (for breathy voice)
	speechPlayer_frameParam_t ftpFreq1; // FTP1: first tracheal pole frequency in Hz (0=disabled, ~600 typical)
	speechPlayer_frameParam_t ftpBw1; // BTP1: first tracheal pole bandwidth in Hz
	speechPlayer_frameParam_t ftzFreq1; // FTZ1: first tracheal zero frequency in Hz
	speechPlayer_frameParam_t ftzBw1; // BTZ1: first tracheal zero bandwidth in Hz
	speechPlayer_frameParam_t ftpFreq2; // FTP2: second tracheal pole frequency in Hz (~1400 typical)
	speechPlayer_frameParam_t ftpBw2; // BTP2: second tracheal pole bandwidth in Hz
	speechPlayer_frameParam_t ftzFreq2; // FTZ2: second tracheal zero frequency in Hz (0=disabled, ~1500 typical)
	speechPlayer_frameParam_t ftzBw2; // BTZ2: second tracheal zero bandwidth in Hz
	// Glottal-open formant modulation (pitch-synchronous F1 variation)
	speechPlayer_frameParam_t deltaF1; // DF1: F1 frequency increase during glottal open phase (0-100 Hz)
	speechPlayer_frameParam_t deltaB1; // DB1: B1 bandwidth increase during glottal open phase (0-400 Hz)
	// Stop burst envelope
	speechPlayer_frameParam_t burstAmplitude; // AB: stop burst transient amplitude 0-1
	speechPlayer_frameParam_t burstDuration; // DB: burst duration normalized 0-1 (0.25 = 5ms at 20ms max)
	// Cascade formants
	speechPlayer_frameParam_t cf1, cf2, cf3, cf4, cf5, cf6, cfN0, cfNP; // frequencies of standard cascaide formants, nasal (anti) 0 and nasal pole in hz
	speechPlayer_frameParam_t cb1, cb2, cb3, cb4, cb5, cb6, cbN0, cbNP; // bandwidths of standard cascaide formants, nasal (anti) 0 and nasal pole in hz
	speechPlayer_frameParam_t caNP; // amplitude from 0 to 1 of cascade nasal pole formant
	// fricatives and parallel
	speechPlayer_frameParam_t fricationAmplitude; // amplitude of frication noise from 0 to 1.
	speechPlayer_frameParam_t noiseFilterFreq; // center freq for noise bandpass filter (0=white noise, >0=bandpass)
	speechPlayer_frameParam_t noiseFilterBw; // bandwidth of noise bandpass filter in Hz
	speechPlayer_frameParam_t pf1, pf2, pf3, pf4, pf5, pf6; // parallel formants in hz
	speechPlayer_frameParam_t pb1, pb2, pb3, pb4, pb5, pb6; // parallel formant bandwidths in hz
	speechPlayer_frameParam_t pa1, pa2, pa3, pa4, pa5, pa6; // amplitude of parallel formants between 0 and 1
	speechPlayer_frameParam_t parallelBypass; // amount of signal which should bypass parallel resonators from 0 to 1
	speechPlayer_frameParam_t preFormantGain; // amplitude from 0 to 1 of all vocal tract sound (voicing, frication) before entering formant resonators. Useful for stopping/starting speech
	speechPlayer_frameParam_t outputGain; // amplitude from 0 to 1 of final output (master volume)
	speechPlayer_frameParam_t endVoicePitch; //  pitch of voice at the end of the frame length
	speechPlayer_frameParam_t midVoicePitch; // pitch at midpoint for contour tones (0=linear interp, >0=3-point contour)
} speechPlayer_frame_t;

const int speechPlayer_frame_numParams=sizeof(speechPlayer_frame_t)/sizeof(speechPlayer_frameParam_t);

class FrameManager {
	public:
	static FrameManager* create(); //factory function
	virtual void queueFrame(speechPlayer_frame_t* frame, unsigned int minNumSamples, unsigned int numFadeSamples, int userIndex, bool purgeQueue)=0;
	virtual const speechPlayer_frame_t* const getCurrentFrame()=0;
	virtual const int getLastIndex()=0; 
	virtual ~FrameManager()=0 {};
};

#endif
