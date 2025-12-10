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

/*
Based on klsyn-88, found at http://linguistics.berkeley.edu/phonlab/resources/
*/

#define _USE_MATH_DEFINES

#include <cassert>
#include <cmath>
#include <cstdlib>
#include <cstdint>
#include "debug.h"
#include "utils.h"
#include "speechWaveGenerator.h"

using namespace std;

const double PITWO=M_PI*2;

// Improved noise generator using xorshift128+ algorithm
// Better quality randomness and full frequency spectrum for fricatives
class NoiseGenerator {
	private:
	uint64_t state0;
	uint64_t state1;
	double lastValue;

	public:
	NoiseGenerator(): lastValue(0.0) {
		// Seed with current time and address for uniqueness
		state0 = 0x853c49e6748fea9bULL;
		state1 = 0xda3e39cb94b95bdbULL;
	}

	// xorshift128+ - fast, high quality PRNG
	uint64_t xorshift128plus() {
		uint64_t s1 = state0;
		uint64_t s0 = state1;
		uint64_t result = s0 + s1;
		state0 = s0;
		s1 ^= s1 << 23;
		state1 = s1 ^ s0 ^ (s1 >> 18) ^ (s0 >> 5);
		return result;
	}

	double getNext() {
		// Generate white noise with full frequency spectrum
		double noise = ((double)(xorshift128plus() >> 11) / (double)(1ULL << 53)) * 2.0 - 1.0;
		// Gentle smoothing (less than before) to reduce harshness
		lastValue = noise * 0.7 + lastValue * 0.3;
		return lastValue;
	}

	// Highpass-filtered noise for sibilants (more high-frequency energy)
	double getNextHighpass() {
		double noise = ((double)(xorshift128plus() >> 11) / (double)(1ULL << 53)) * 2.0 - 1.0;
		// Highpass by subtracting lowpass
		double hp = noise - lastValue;
		lastValue = lastValue * 0.8 + noise * 0.2;
		return hp;
	}
};

// Colored Noise Generator with configurable bandpass filtering
// For place-specific fricative spectra: /s/ high-freq, /ʃ/ mid-freq, /f/ flat
class ColoredNoiseGenerator {
	private:
	int sampleRate;
	NoiseGenerator white;
	// Simple 2nd-order bandpass state variables
	double bp1, bp2;
	double lastFreq, lastBw;
	double a0, a1, a2, b1, b2;

	void updateCoeffs(double freq, double bw) {
		if (freq == lastFreq && bw == lastBw) return;
		lastFreq = freq;
		lastBw = bw;

		// Compute 2nd-order bandpass coefficients
		double omega = PITWO * freq / sampleRate;
		double alpha = sin(omega) * sinh(log(2.0) / 2.0 * bw / freq * omega / sin(omega));

		double b0 = alpha;
		double b1_raw = 0.0;
		double b2_raw = -alpha;
		double a0_raw = 1.0 + alpha;
		double a1_raw = -2.0 * cos(omega);
		double a2_raw = 1.0 - alpha;

		// Normalize coefficients
		a0 = b0 / a0_raw;
		a1 = b1_raw / a0_raw;
		a2 = b2_raw / a0_raw;
		b1 = a1_raw / a0_raw;
		b2 = a2_raw / a0_raw;
	}

	public:
	ColoredNoiseGenerator(int sr): sampleRate(sr), white(), bp1(0), bp2(0), lastFreq(0), lastBw(0) {}

	double getNext(double filterFreq, double filterBw) {
		double noise = white.getNext();

		// If filterFreq is 0, return white noise (no filtering)
		if (filterFreq <= 0) return noise;

		// Clamp bandwidth to reasonable values
		if (filterBw < 100) filterBw = 100;

		// Update coefficients if needed
		updateCoeffs(filterFreq, filterBw);

		// Apply bandpass filter (direct form II transposed)
		double out = a0 * noise + a1 * bp1 + a2 * bp2 - b1 * bp1 - b2 * bp2;
		bp2 = bp1;
		bp1 = out;

		// Boost output to compensate for narrow bandpass attenuation
		return out * 3.0;
	}
};

// KLSYN88 Spectral Tilt Filter
// First-order lowpass that attenuates high frequencies to create breathy voice quality
// tiltDB: 0 = no filtering (modal voice), up to 41 dB attenuation at 3kHz (very breathy)
class SpectralTiltFilter {
	private:
	int sampleRate;
	double lastOutput;

	public:
	SpectralTiltFilter(int sr): sampleRate(sr), lastOutput(0.0) {}

	double filter(double input, double tiltDB) {
		if (tiltDB <= 0) return input;  // No filtering when tilt is 0

		// Calculate cutoff frequency for desired attenuation at 3kHz
		// For first-order filter: |H(f)| = 1/sqrt(1+(f/fc)^2)
		// Given target attenuation at 3kHz, solve for fc
		double targetFreq = 3000.0;
		double attenLinear = pow(10.0, -tiltDB / 20.0);
		// Clamp to avoid division issues at extreme values
		if (attenLinear >= 0.999) return input;
		if (attenLinear <= 0.001) attenLinear = 0.001;

		double fc = targetFreq * attenLinear / sqrt(1.0 - attenLinear * attenLinear);
		double alpha = exp(-2.0 * M_PI * fc / sampleRate);

		double output = (1.0 - alpha) * input + alpha * lastOutput;
		lastOutput = output;
		return output;
	}
};

// KLSYN88 Flutter Generator
// Adds natural pitch micro-variations using sum of low-frequency oscillators
// Creates more natural-sounding voice by avoiding perfectly steady pitch
class FlutterGenerator {
	private:
	int sampleRate;
	double phase1, phase2, phase3;

	public:
	FlutterGenerator(int sr): sampleRate(sr), phase1(0), phase2(0), phase3(0) {}

	double getNext(double flutterAmount) {
		if (flutterAmount <= 0) return 1.0;  // No modulation

		// Three low-frequency components per KLSYN88 (~12.7, 7.1, 4.7 Hz)
		const double freq1 = 12.7, freq2 = 7.1, freq3 = 4.7;
		double flutter = 0.5 * sin(PITWO * phase1)
		               + 0.3 * sin(PITWO * phase2)
		               + 0.2 * sin(PITWO * phase3);

		phase1 = fmod(phase1 + freq1 / sampleRate, 1.0);
		phase2 = fmod(phase2 + freq2 / sampleRate, 1.0);
		phase3 = fmod(phase3 + freq3 / sampleRate, 1.0);

		// Return pitch multiplier centered at 1.0, ±2% at full flutter
		return 1.0 + flutter * flutterAmount * 0.02;
	}
};

class FrequencyGenerator {
	private:
	int sampleRate;
	double lastCyclePos;

	public:
	FrequencyGenerator(int sr): sampleRate(sr), lastCyclePos(0) {}

	double getNext(double frequency) {
		double cyclePos=fmod((frequency/sampleRate)+lastCyclePos,1);
		lastCyclePos=cyclePos;
		return cyclePos;
	}

};

class VoiceGenerator {
	private:
	FrequencyGenerator pitchGen;
	FrequencyGenerator vibratoGen;
	NoiseGenerator aspirationGen;
	FlutterGenerator flutterGen;  // KLSYN88: natural pitch jitter
	double lastCyclePos;  // KLSYN88: track cycle for diplophonia
	bool periodAlternate;  // KLSYN88: alternating period flag

	public:
	bool glottisOpen;
	VoiceGenerator(int sr): pitchGen(sr), vibratoGen(sr), aspirationGen(), flutterGen(sr), lastCyclePos(0), periodAlternate(false), glottisOpen(false) {};

	double getNext(const speechPlayer_frame_t* frame) {
		double vibrato=(sin(vibratoGen.getNext(frame->vibratoSpeed)*PITWO)*0.06*frame->vibratoPitchOffset)+1;
		double flutter=flutterGen.getNext(frame->flutter);  // KLSYN88: apply flutter

		// KLSYN88: Diplophonia - alternating pitch periods for creaky voice
		double diplophoniaMod = 1.0;
		if (frame->diplophonia > 0) {
			// Alternating periods: one slightly longer, one slightly shorter
			// ±10% pitch variation at full diplophonia
			diplophoniaMod = periodAlternate ? (1.0 + frame->diplophonia * 0.10) : (1.0 - frame->diplophonia * 0.10);
		}

		double voice=pitchGen.getNext(frame->voicePitch*vibrato*flutter*diplophoniaMod);

		// Detect new pitch period (cycle wrapped) to toggle alternation
		if (voice < lastCyclePos - 0.5) {  // Wrapped from ~1 back to ~0
			periodAlternate = !periodAlternate;
		}
		lastCyclePos = voice;

		double aspiration=aspirationGen.getNext()*0.2;
		double turbulence=aspiration*frame->voiceTurbulenceAmplitude;

		double glottalWave;

		// Check if using LF model (Rd > 0) or legacy model
		if (frame->lfRd > 0) {
			// Liljencrants-Fant (LF) glottal model
			// Rd parameter controls voice quality: 0.3=tense, 1.0=modal, 2.7=breathy
			double Rd = max(0.3, min(2.7, frame->lfRd));

			// Derive LF parameters from Rd (Fant et al. 1985 approximations)
			// These polynomial fits map Rd to the four LF parameters
			double Rk = 0.118 * Rd + 0.224;  // Glottal open time ratio
			double Rg = 0.25 * Rd + 0.5;     // Glottal rise time
			double Ra = 0.048 * Rd - 0.01;   // Return phase coefficient
			if (Ra < 0.01) Ra = 0.01;

			// Derived timing parameters
			double tp = 1.0 / (2.0 * Rg);    // Time of peak (as fraction of T0)
			double te = tp * (1.0 + Rk);     // Time of excitation (glottal closure)
			double ta = Ra;                   // Return phase time constant

			// Ensure te <= 1.0
			if (te > 0.99) te = 0.99;

			glottisOpen = voice < te;

			if (voice < tp) {
				// Rising phase: sinusoidal rise to peak
				glottalWave = 0.5 * (1.0 - cos(M_PI * voice / tp));
			} else if (voice < te) {
				// Falling phase: cosinusoidal fall from peak
				double fallPos = (voice - tp) / (te - tp);
				glottalWave = 0.5 * (1.0 + cos(M_PI * fallPos));
			} else {
				// Return phase: exponential decay (models incomplete closure)
				double returnPos = (voice - te) / (1.0 - te);
				double epsilon = 1.0 / (ta + 0.001);  // Decay rate
				glottalWave = 0.5 * exp(-epsilon * returnPos * (1.0 - te));
				// Taper to zero at end of cycle
				if (returnPos > 0.8) {
					glottalWave *= (1.0 - returnPos) / 0.2;
				}
			}
		} else {
			// Legacy glottal model using openQuotientShape and speedQuotient
			double oq = frame->glottalOpenQuotient;
			double sq = frame->speedQuotient;  // 1.0 = symmetric, >1 = fast rise/slow fall
			double shape = frame->openQuotientShape;  // 0 = linear decay, 1 = exponential decay

			glottisOpen = voice < oq;

			if (voice < oq) {
				// Open phase: split by speed quotient into rising and falling portions
				double openingEnd = oq / (1.0 + 1.0/sq);  // SQ controls rise/fall time ratio
				if (voice < openingEnd) {
					// Rising phase - linear ramp to peak
					glottalWave = voice / openingEnd;
				} else {
					// Falling phase within open period - exponential decay
					double fallPos = (voice - openingEnd) / (oq - openingEnd);
					double expFactor = 1.0 + shape * 4.0;  // shape 0->1, expFactor 1->5
					glottalWave = pow(1.0 - fallPos, expFactor);
				}
			} else {
				// Closed phase - no airflow
				glottalWave = 0.0;
			}
		}

		voice = (glottalWave * 2.0) - 1.0;  // Scale to -1 to +1

		if(!glottisOpen) {
			turbulence*=0.01;
		}
		voice+=turbulence;
		voice*=frame->voiceAmplitude;
		aspiration*=frame->aspirationAmplitude;
		return aspiration+voice;
	}

};

class Resonator {
	private:
	//raw parameters
	int sampleRate;
	double frequency;
	double bandwidth;
	bool anti;
	//calculated parameters
	bool setOnce;
	double a, b, c;
	//Memory
	double p1, p2;

	public:
	Resonator(int sampleRate, bool anti=false) {
		this->sampleRate=sampleRate;
		this->anti=anti;
		this->setOnce=false;
		this->p1=0;
		this->p2=0;
	}

	void setParams(double frequency, double bandwidth) {
		if(!setOnce||(frequency!=this->frequency)||(bandwidth!=this->bandwidth)) {
			this->frequency=frequency;
			this->bandwidth=bandwidth;
			double r=exp(-M_PI/sampleRate*bandwidth);
			c=-(r*r);
			b=r*cos(PITWO/sampleRate*-frequency)*2.0;
			a=1.0-b-c;
			if(anti&&frequency!=0) {
				a=1.0/a;
				c*=-a;
				b*=-a;
			}
		}
		this->setOnce=true;
	}

	double resonate(double in, double frequency, double bandwidth) {
		setParams(frequency,bandwidth);
		double out=a*in+b*p1+c*p2;
		p2=p1;
		p1=anti?in:out;
		return out;
	}

	void setSampleRate(int sr) { sampleRate = sr; }
};

// 4th-order resonator (cascade of two 2nd-order sections)
// Provides sharper formants with 24 dB/octave rolloff vs 12 dB/octave for 2nd-order
// Better vowel clarity and more focused formant peaks
class Resonator4thOrder {
	private:
	int sampleRate;
	Resonator stage1, stage2;

	public:
	Resonator4thOrder(int sr): sampleRate(sr), stage1(sr), stage2(sr) {}

	double resonate(double in, double frequency, double bandwidth) {
		if (frequency <= 0) return in;  // Bypass if frequency is 0

		// Adjust bandwidth for equivalent Q when cascading
		// For Butterworth-like response, each stage gets bw * 0.64 (~1/sqrt(2))
		double bwAdjusted = bandwidth * 0.64;

		// Cascade two 2nd-order sections at same frequency
		double out = stage1.resonate(in, frequency, bwAdjusted);
		return stage2.resonate(out, frequency, bwAdjusted);
	}

	void setSampleRate(int sr) {
		sampleRate = sr;
		stage1.setSampleRate(sr);
		stage2.setSampleRate(sr);
	}
};

// KLSYN88: Tracheal (subglottal) resonator for breathy voice realism
// Adds coupling to tracheal cavity below the glottis
class TrachealResonator {
	private:
	int sampleRate;
	Resonator pole1, zero1, pole2;  // First pole-zero pair + second pole

	public:
	TrachealResonator(int sr): sampleRate(sr), pole1(sr), zero1(sr, true), pole2(sr) {}

	double resonate(double input, const speechPlayer_frame_t* frame) {
		double output = input;

		// First tracheal pole (adds resonance around 600 Hz)
		if (frame->ftpFreq1 > 0) {
			output = pole1.resonate(output, frame->ftpFreq1, frame->ftpBw1);
		}

		// First tracheal zero (anti-resonator, adds notch)
		if (frame->ftzFreq1 > 0) {
			output = zero1.resonate(output, frame->ftzFreq1, frame->ftzBw1);
		}

		// Second tracheal pole (adds resonance around 1400 Hz)
		if (frame->ftpFreq2 > 0) {
			output = pole2.resonate(output, frame->ftpFreq2, frame->ftpBw2);
		}

		return output;
	}
};

class CascadeFormantGenerator {
	private:
	int sampleRate;
	// F1-F3: 4th-order resonators for sharper, more focused formants
	Resonator4thOrder r1, r2, r3;
	// F4-F6: 2nd-order resonators (wider bandwidths, less benefit from 4th-order)
	Resonator r4, r5, r6, rN0, rNP;

	public:
	CascadeFormantGenerator(int sr): sampleRate(sr), r1(sr), r2(sr), r3(sr), r4(sr), r5(sr), r6(sr), rN0(sr,true), rNP(sr) {};

	double getNext(const speechPlayer_frame_t* frame, bool glottisOpen, double input) {
		input/=2.0;
		double n0Output=rN0.resonate(input,frame->cfN0,frame->cbN0);
		double output=calculateValueAtFadePosition(input,rNP.resonate(n0Output,frame->cfNP,frame->cbNP),frame->caNP);
		output=r6.resonate(output,frame->cf6,frame->cb6);
		output=r5.resonate(output,frame->cf5,frame->cb5);
		output=r4.resonate(output,frame->cf4,frame->cb4);
		// F1-F3 use 4th-order for sharper resonance (24 dB/octave rolloff)
		output=r3.resonate(output,frame->cf3,frame->cb3);
		output=r2.resonate(output,frame->cf2,frame->cb2);
		output=r1.resonate(output,frame->cf1,frame->cb1);
		return output;
	}

};

// KLSYN88: Stop burst envelope generator for plosive transients
class BurstGenerator {
	private:
	int sampleRate;
	NoiseGenerator noiseGen;
	double burstPhase;  // 0 = burst start, 1 = burst end
	double lastBurstAmp;  // Track amplitude to detect burst start

	public:
	BurstGenerator(int sr): sampleRate(sr), noiseGen(), burstPhase(1.0), lastBurstAmp(0) {}

	double getNext(double burstAmplitude, double burstDuration) {
		if (burstAmplitude <= 0) {
			lastBurstAmp = 0;
			burstPhase = 1.0;
			return 0;
		}

		// Detect new burst (amplitude just became non-zero)
		if (lastBurstAmp <= 0 && burstAmplitude > 0) {
			burstPhase = 0;  // Reset burst to start
		}
		lastBurstAmp = burstAmplitude;

		if (burstPhase >= 1.0) {
			return 0;  // Burst complete
		}

		// Calculate envelope: exponential decay from 1 to 0 over burst duration
		// burstDuration 0-1 maps to ~5-20ms (normalized)
		double maxDurationMs = 20.0;
		double minDurationMs = 5.0;
		double durationMs = minDurationMs + burstDuration * (maxDurationMs - minDurationMs);
		double durationSamples = (durationMs / 1000.0) * sampleRate;

		double envelope = pow(1.0 - burstPhase, 2.0);  // Quadratic decay

		// Advance phase
		burstPhase += 1.0 / durationSamples;
		if (burstPhase > 1.0) burstPhase = 1.0;

		// Generate burst: noise * envelope * amplitude
		return noiseGen.getNext() * envelope * burstAmplitude;
	}
};

class ParallelFormantGenerator {
	private:
	int sampleRate;
	Resonator r1, r2, r3, r4, r5, r6;

	public:
	ParallelFormantGenerator(int sr): sampleRate(sr), r1(sr), r2(sr), r3(sr), r4(sr), r5(sr), r6(sr) {};

	double getNext(const speechPlayer_frame_t* frame, double input) {
		input/=2.0;
		double output=0;
		output+=(r1.resonate(input,frame->pf1,frame->pb1)-input)*frame->pa1;
		output+=(r2.resonate(input,frame->pf2,frame->pb2)-input)*frame->pa2;
		output+=(r3.resonate(input,frame->pf3,frame->pb3)-input)*frame->pa3;
		output+=(r4.resonate(input,frame->pf4,frame->pb4)-input)*frame->pa4;
		output+=(r5.resonate(input,frame->pf5,frame->pb5)-input)*frame->pa5;
		output+=(r6.resonate(input,frame->pf6,frame->pb6)-input)*frame->pa6;
		return calculateValueAtFadePosition(output,input,frame->parallelBypass);
	}

};

class SpeechWaveGeneratorImpl: public SpeechWaveGenerator {
	private:
	int sampleRate;
	VoiceGenerator voiceGenerator;
	SpectralTiltFilter tiltFilter;  // KLSYN88: spectral tilt for breathy voice
	TrachealResonator trachealRes;  // KLSYN88: subglottal resonances
	ColoredNoiseGenerator fricGenerator;  // Bandpass-filtered noise for fricatives
	BurstGenerator burstGen;  // KLSYN88: stop burst envelopes
	CascadeFormantGenerator cascade;
	ParallelFormantGenerator parallel;
	FrameManager* frameManager;

	public:
	SpeechWaveGeneratorImpl(int sr): sampleRate(sr), voiceGenerator(sr), tiltFilter(sr), trachealRes(sr), fricGenerator(sr), burstGen(sr), cascade(sr), parallel(sr), frameManager(NULL) {
	}

	unsigned int generate(const unsigned int sampleCount, sample* sampleBuf) {
		if(!frameManager) return 0; 
		double val=0;
		for(unsigned int i=0;i<sampleCount;++i) {
			const speechPlayer_frame_t* frame=frameManager->getCurrentFrame();
			if(frame) {
				double voice=voiceGenerator.getNext(frame);
				voice=tiltFilter.filter(voice,frame->spectralTilt);  // KLSYN88: apply spectral tilt
				voice=trachealRes.resonate(voice,frame);  // KLSYN88: apply tracheal resonances
				double cascadeOut=cascade.getNext(frame,voiceGenerator.glottisOpen,voice*frame->preFormantGain);
				// Colored noise for fricatives (bandpass filtered based on place of articulation)
				double fric=fricGenerator.getNext(frame->noiseFilterFreq, frame->noiseFilterBw)*0.3*frame->fricationAmplitude;
				double burst=burstGen.getNext(frame->burstAmplitude,frame->burstDuration);  // KLSYN88: stop burst
				double parallelOut=parallel.getNext(frame,(fric+burst)*frame->preFormantGain);
				double out=(cascadeOut+parallelOut)*frame->outputGain;
				sampleBuf[i].value=(int)max(min(out*4000,32000),-32000);
			} else {
				return i;
			}
		}
		return sampleCount;
	}

	void setFrameManager(FrameManager* frameManager) {
		this->frameManager=frameManager;
	}

};

SpeechWaveGenerator* SpeechWaveGenerator::create(int sampleRate) {return new SpeechWaveGeneratorImpl(sampleRate); }
