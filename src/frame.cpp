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

#include <queue>
#include "utils.h"
#include "frame.h"

using namespace std;

struct frameRequest_t {
	unsigned int minNumSamples;
	unsigned int numFadeSamples;
	bool NULLFrame;
	speechPlayer_frame_t frame;
	double voicePitchInc;      // pitch increment for first half (or full frame if no midpoint)
	double voicePitchInc2;     // pitch increment for second half (contour tones)
	bool hasContour;           // true if using 3-point pitch contour
	int userIndex;
};

class FrameManagerImpl: public FrameManager {
	private:
	LockableObject frameLock;
	queue<frameRequest_t*> frameRequestQueue;
	frameRequest_t* oldFrameRequest;
	frameRequest_t* newFrameRequest;
	speechPlayer_frame_t curFrame;
	bool curFrameIsNULL;
	unsigned int sampleCounter;
	int lastUserIndex;

	void updateCurrentFrame() {
		sampleCounter++;
		if(newFrameRequest) {
			if(sampleCounter>(newFrameRequest->numFadeSamples)) {
				delete oldFrameRequest;
				oldFrameRequest=newFrameRequest;
				newFrameRequest=NULL;
			} else {
				double curFadeRatio=(double)sampleCounter/(newFrameRequest->numFadeSamples);
				for(int i=0;i<speechPlayer_frame_numParams;++i) {
					// These parameters step instantly (no smoothstep interpolation)
					// to avoid audible filter sweeps and ensure correct onset timing
					if (i == FRAME_INDEX(burstAmplitude) || i == FRAME_INDEX(burstDuration)
					    || i == FRAME_INDEX(fricationAmplitude) || i == FRAME_INDEX(noiseFilterFreq)
					    || i == FRAME_INDEX(noiseFilterBw) || i == FRAME_INDEX(parallelAntiFreq)
					    || i == FRAME_INDEX(trillRate) || i == FRAME_INDEX(trillDepth)
					    || i == FRAME_INDEX(burstFilterFreq) || i == FRAME_INDEX(burstFilterBw)
					    || i == FRAME_INDEX(burstNoiseColor)) {
						// Use target value immediately
						((speechPlayer_frameParam_t*)&curFrame)[i] = ((speechPlayer_frameParam_t*)&(newFrameRequest->frame))[i];
					} else {
						((speechPlayer_frameParam_t*)&curFrame)[i]=calculateValueAtFadePosition(((speechPlayer_frameParam_t*)&(oldFrameRequest->frame))[i],((speechPlayer_frameParam_t*)&(newFrameRequest->frame))[i],curFadeRatio);
					}
				}
			}
		} else if(sampleCounter>(oldFrameRequest->minNumSamples)) {
			if(!frameRequestQueue.empty()) {
				curFrameIsNULL=false;
				newFrameRequest=frameRequestQueue.front();
				frameRequestQueue.pop();
				if(newFrameRequest->NULLFrame) {
					memcpy(&(newFrameRequest->frame),&(oldFrameRequest->frame),sizeof(speechPlayer_frame_t));
					newFrameRequest->frame.preFormantGain=0;
					newFrameRequest->frame.voicePitch=curFrame.voicePitch;
					newFrameRequest->voicePitchInc=0;
				} else if(oldFrameRequest->NULLFrame) {
					memcpy(&(oldFrameRequest->frame),&(newFrameRequest->frame),sizeof(speechPlayer_frame_t));
					oldFrameRequest->frame.preFormantGain=0;
				}
				if(newFrameRequest) {
					if(newFrameRequest->userIndex!=-1) lastUserIndex=newFrameRequest->userIndex;
					sampleCounter=0;
					newFrameRequest->frame.voicePitch+=(newFrameRequest->voicePitchInc*newFrameRequest->numFadeSamples);
				}
			} else {
				curFrameIsNULL=true;
			}
		} else {
			// Apply pitch increment - handle 3-point contour tones
			if (oldFrameRequest->hasContour && sampleCounter > oldFrameRequest->minNumSamples / 2) {
				// Second half of frame: use voicePitchInc2
				curFrame.voicePitch += oldFrameRequest->voicePitchInc2;
			} else {
				// First half (or linear): use voicePitchInc
				curFrame.voicePitch += oldFrameRequest->voicePitchInc;
			}
			oldFrameRequest->frame.voicePitch = curFrame.voicePitch;
		}
	}


	public:

	FrameManagerImpl(): curFrame(), curFrameIsNULL(true), sampleCounter(0), newFrameRequest(NULL), lastUserIndex(-1)  {
		oldFrameRequest=new frameRequest_t();
		oldFrameRequest->NULLFrame=true;
	}

	void queueFrame(speechPlayer_frame_t* frame, unsigned int minNumSamples, unsigned int numFadeSamples, int userIndex, bool purgeQueue) {
		frameLock.acquire();
		frameRequest_t* frameRequest=new frameRequest_t;
		frameRequest->minNumSamples=max(minNumSamples,(unsigned int)1);
		frameRequest->numFadeSamples=max(numFadeSamples,(unsigned int)1);
		if(frame) {
			frameRequest->NULLFrame=false;
			memcpy(&(frameRequest->frame),frame,sizeof(speechPlayer_frame_t));
			// Check for 3-point contour tone (midVoicePitch > 0)
			if (frame->midVoicePitch > 0) {
				// Contour tone: split into two halves
				frameRequest->hasContour = true;
				unsigned int halfSamples = frameRequest->minNumSamples / 2;
				if (halfSamples > 0) {
					frameRequest->voicePitchInc = (frame->midVoicePitch - frame->voicePitch) / halfSamples;
					frameRequest->voicePitchInc2 = (frame->endVoicePitch - frame->midVoicePitch) / (frameRequest->minNumSamples - halfSamples);
				} else {
					frameRequest->voicePitchInc = 0;
					frameRequest->voicePitchInc2 = 0;
				}
			} else {
				// Linear interpolation (original behavior)
				frameRequest->hasContour = false;
				frameRequest->voicePitchInc = (frame->endVoicePitch - frame->voicePitch) / frameRequest->minNumSamples;
				frameRequest->voicePitchInc2 = 0;
			}
		} else {
			frameRequest->NULLFrame=true;
			frameRequest->hasContour = false;
		}
		frameRequest->userIndex=userIndex;
		if(purgeQueue) {
			for(;!frameRequestQueue.empty();frameRequestQueue.pop()) delete frameRequestQueue.front();
			sampleCounter=oldFrameRequest->minNumSamples;
			if(newFrameRequest) {
				oldFrameRequest->NULLFrame=newFrameRequest->NULLFrame;
				memcpy(&(oldFrameRequest->frame),&curFrame,sizeof(speechPlayer_frame_t));
				delete newFrameRequest;
				newFrameRequest=NULL;
			}
		}
		frameRequestQueue.push(frameRequest);
		frameLock.release();
	}

	const int getLastIndex() {
		return lastUserIndex;
	}

	const speechPlayer_frame_t* const getCurrentFrame() {
		frameLock.acquire();
		updateCurrentFrame();
		frameLock.release();
		return curFrameIsNULL?NULL:&curFrame;
	}

	~FrameManagerImpl() {
		for(;!frameRequestQueue.empty();frameRequestQueue.pop()) delete frameRequestQueue.front();
		if(oldFrameRequest) delete oldFrameRequest;
		if(newFrameRequest) delete newFrameRequest;
	}

};

FrameManager* FrameManager::create() { return new FrameManagerImpl(); }
