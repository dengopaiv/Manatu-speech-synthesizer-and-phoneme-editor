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
#include <cfloat>
#include "debug.h"
#include "utils.h"
#include "speechWaveGenerator.h"

// SSE intrinsics for denormal suppression (Windows/MSVC)
#ifdef _MSC_VER
#include <intrin.h>
#endif

using namespace std;

// Enable flush-to-zero and denormals-are-zero modes to prevent CPU stalls
// from subnormal floating-point numbers in resonator feedback paths
inline void enableDenormalSuppression() {
#ifdef _MSC_VER
	// MSVC: Use _controlfp to set FTZ mode
	unsigned int control_word;
	_controlfp_s(&control_word, _DN_FLUSH, _MCW_DN);
#elif defined(__SSE__)
	// GCC/Clang with SSE: Set MXCSR register bits
	_mm_setcsr(_mm_getcsr() | 0x8040);  // FTZ (bit 15) + DAZ (bit 6)
#endif
}

// PolyBLEP (Polynomial Band-Limited Step) anti-aliasing
// Reduces aliasing artifacts at waveform discontinuities
// Reference: Välimäki & Huovilainen 2006
inline double polyBLEP(double t, double dt) {
	// t = phase position (0 to 1), dt = phase increment per sample
	if (dt <= 0) return 0;

	if (t < dt) {
		// Just after discontinuity (start of cycle)
		t = t / dt;
		return t + t - t * t - 1.0;
	} else if (t > 1.0 - dt) {
		// Just before discontinuity (end of cycle)
		t = (t - 1.0) / dt;
		return t * t + t + t + 1.0;
	}
	return 0;
}

const double PITWO=M_PI*2;

// Improved noise generator using xorshift128+ algorithm
// Better quality randomness and full frequency spectrum for fricatives
class NoiseGenerator {
	private:
	uint64_t state0;
	uint64_t state1;
	double lastValue;
	// Pink noise filter state (Voss-McCartney algorithm approximation)
	double pinkState[5];
	int pinkCounter;

	public:
	NoiseGenerator(): lastValue(0.0), pinkCounter(0) {
		// Seed with current time and address for uniqueness
		state0 = 0x853c49e6748fea9bULL;
		state1 = 0xda3e39cb94b95bdbULL;
		// Initialize pink noise state
		for (int i = 0; i < 5; i++) pinkState[i] = 0;
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

	// Raw white noise (no filtering)
	double getWhite() {
		return ((double)(xorshift128plus() >> 11) / (double)(1ULL << 53)) * 2.0 - 1.0;
	}

	double getNext() {
		// Generate white noise with full frequency spectrum
		double noise = getWhite();
		// Gentle smoothing (less than before) to reduce harshness
		lastValue = noise * 0.7 + lastValue * 0.3;
		return lastValue;
	}

	// Pink noise (1/f spectrum) for natural aspiration
	// Uses Paul Kellet's refined method - cascaded 1-pole filters
	// Better spectral match for breathy voice than white noise
	double getNextPink() {
		double white = getWhite();

		// 5 cascaded 1-pole lowpass filters with different cutoffs
		// Approximates 1/f spectrum from 20Hz to Nyquist
		pinkState[0] = 0.99886 * pinkState[0] + white * 0.0555179;
		pinkState[1] = 0.99332 * pinkState[1] + white * 0.0750759;
		pinkState[2] = 0.96900 * pinkState[2] + white * 0.1538520;
		pinkState[3] = 0.86650 * pinkState[3] + white * 0.3104856;
		pinkState[4] = 0.55000 * pinkState[4] + white * 0.5329522;

		double pink = pinkState[0] + pinkState[1] + pinkState[2]
		            + pinkState[3] + pinkState[4] + white * 0.5362;

		// Normalize (sum of coefficients is ~1.5)
		return pink * 0.11;
	}

	// Highpass-filtered noise for sibilants (more high-frequency energy)
	double getNextHighpass() {
		double noise = getWhite();
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
		// If filterFreq is too low, return pink noise for natural aspiration
		// Pink (1/f) spectrum better matches natural breathiness
		// Threshold of 100 Hz prevents numerical instability from sinh() overflow
		// during parameter interpolation when transitioning to/from filtered noise
		if (filterFreq < 100) return white.getNextPink();

		double noise = white.getNext();

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
// tiltDB: 0 = no filtering (modal voice), up to 41 dB attenuation at 5kHz (very breathy)
// Target raised from 3kHz to 5kHz to preserve brightness in 3-5kHz speech range
class SpectralTiltFilter {
	private:
	int sampleRate;
	double lastOutput;

	public:
	SpectralTiltFilter(int sr): sampleRate(sr), lastOutput(0.0) {}

	double filter(double input, double tiltDB) {
		// Bypass for small values - avoids unnecessary filtering
		if (tiltDB < 1.5) return input;

		// Calculate cutoff frequency for desired attenuation at 5kHz
		// For first-order filter: |H(f)| = 1/sqrt(1+(f/fc)^2)
		// Given target attenuation at 5kHz, solve for fc
		// Raised from 3kHz to preserve brightness in critical 3-5kHz region
		double targetFreq = 5000.0;
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
	double lastDt;  // Phase increment for polyBLEP

	public:
	FrequencyGenerator(int sr): sampleRate(sr), lastCyclePos(0), lastDt(0) {}

	double getNext(double frequency) {
		lastDt = frequency / sampleRate;  // Store phase increment
		double cyclePos=fmod(lastDt+lastCyclePos,1);
		lastCyclePos=cyclePos;
		return cyclePos;
	}

	// Get the phase increment (needed for polyBLEP anti-aliasing)
	double getDt() const { return lastDt; }
};

class VoiceGenerator {
	private:
	FrequencyGenerator pitchGen;
	FrequencyGenerator vibratoGen;
	FrequencyGenerator sinusoidalGen;  // AVS: pure sinusoidal voicing source
	ColoredNoiseGenerator aspirationGen;  // Filtered aspiration noise source
	FlutterGenerator flutterGen;  // KLSYN88: natural pitch jitter
	double lastCyclePos;  // KLSYN88: track cycle for diplophonia
	bool periodAlternate;  // KLSYN88: alternating period flag

	public:
	bool glottisOpen;
	VoiceGenerator(int sr): pitchGen(sr), vibratoGen(sr), sinusoidalGen(sr), aspirationGen(sr), flutterGen(sr), lastCyclePos(0), periodAlternate(false), glottisOpen(false) {};

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

		// Aspiration noise with optional bandpass filtering
		double aspiration;
		if (frame->aspirationFilterFreq > 0) {
			aspiration = aspirationGen.getNext(frame->aspirationFilterFreq, frame->aspirationFilterBw) * 0.2;
		} else {
			aspiration = aspirationGen.getNext(0, 1000) * 0.2;  // White noise fallback
		}
		double turbulence=aspiration*frame->voiceTurbulenceAmplitude;

		double glottalWave;

		// Check if using LF model (Rd > 0) or legacy model
		if (frame->lfRd > 0) {
			// Improved Liljencrants-Fant (LF) glottal model
			// Based on Fant 1995 and Degottex et al. 2011 refinements
			// Rd parameter controls voice quality: 0.3=tense, 1.0=modal, 2.7=breathy
			double Rd = max(0.3, min(2.7, frame->lfRd));

			// Improved Rd-to-parameter mapping (Fant 1995 / Degottex 2011)
			// These provide better spectral envelope matching than Fant 1985
			double Rap = (-1.0 + 4.8 * Rd) / 100.0;           // Return phase quotient
			double Rkp = (22.4 + 11.8 * Rd) / 100.0;          // Open quotient shape
			double Rgp = 1.0 / (4.0 * ((0.11 * Rd / (0.5 + 1.2 * Rkp)) - Rap)); // Rise time

			// Clamp parameters to valid ranges
			if (Rap < 0.01) Rap = 0.01;
			if (Rap > 0.20) Rap = 0.20;
			if (Rkp < 0.20) Rkp = 0.20;
			if (Rkp > 0.80) Rkp = 0.80;
			if (Rgp < 0.50) Rgp = 0.50;
			if (Rgp > 3.00) Rgp = 3.00;

			// Derived timing parameters (normalized to T0 = 1)
			double tp = 1.0 / (2.0 * Rgp);           // Time of peak flow
			double te = tp * (1.0 + Rkp);            // Time of excitation (max negative derivative)
			double ta = Rap;                          // Return phase time constant

			// Ensure valid timing
			if (tp > 0.45) tp = 0.45;
			if (te > 0.98) te = 0.98;
			if (te < tp + 0.05) te = tp + 0.05;

			// Calculate epsilon for return phase (ensures smooth decay to zero)
			// Solve: exp(-epsilon * (1-te)) = threshold (very small)
			double epsilon = 1.0 / (ta * (1.0 - te) + 0.001);

			// Amplitude normalization factor for consistent output level
			// Compensates for Rd-dependent waveform shape changes
			double ampNorm = 1.0 / (0.5 + 0.3 * Rd);

			glottisOpen = voice < te;

			if (voice < tp) {
				// Opening phase: smooth sinusoidal rise to peak
				// Uses raised cosine for C1 continuity at boundaries
				double phase = M_PI * voice / tp;
				glottalWave = 0.5 * (1.0 - cos(phase)) * ampNorm;
			} else if (voice < te) {
				// Closing phase: smooth cosinusoidal fall
				// Derivative is negative (excitation phase)
				double phase = M_PI * (voice - tp) / (te - tp);
				glottalWave = 0.5 * (1.0 + cos(phase)) * ampNorm;
			} else {
				// Return phase: exponential decay modeling incomplete closure
				// This phase adds the "breathy" component to the voice
				double t_return = (voice - te) / (1.0 - te);
				double decay = exp(-epsilon * t_return * (1.0 - te));

				// Apply smooth fade at end of cycle for C0 continuity
				double fade = 1.0;
				if (t_return > 0.7) {
					// Raised cosine fade from t_return=0.7 to t_return=1.0
					fade = 0.5 * (1.0 + cos(M_PI * (t_return - 0.7) / 0.3));
				}

				glottalWave = 0.5 * decay * fade * ampNorm;
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

		// Apply polyBLEP anti-aliasing to reduce aliasing at cycle discontinuity
		// The glottal waveform has a discontinuity when it resets at cycle boundary
		double dt = pitchGen.getDt();
		double cyclePos = lastCyclePos;  // Current position in cycle
		// Apply polyBLEP at start of cycle (discontinuity from end of return phase)
		voice -= polyBLEP(cyclePos, dt) * 0.5;  // Attenuated to match waveform jump size

		if(!glottisOpen) {
			turbulence*=0.01;
		}
		voice+=turbulence;
		voice*=frame->voiceAmplitude;

		// AVS: Sinusoidal voicing - pure sine wave at F0 for voicebars and voiced fricatives
		// This bypasses the complex glottal model for simpler periodic energy
		if (frame->sinusoidalVoicingAmplitude > 0) {
			double sinPhase = sinusoidalGen.getNext(frame->voicePitch * vibrato);
			double sinVoice = sin(sinPhase * PITWO) * frame->sinusoidalVoicingAmplitude;
			voice += sinVoice;
		}

		aspiration*=frame->aspirationAmplitude;
		return aspiration+voice;
	}

};

// ============================================================================
// LEGACY IIR RESONATORS (REPLACED BY ZDF - PRESERVED FOR REFERENCE)
// ============================================================================
// These traditional IIR resonators have been replaced by ZDF implementations
// (see ZDFResonator and ZDFResonator4thOrder below). The old code is preserved
// for reference and potential A/B testing. All formant generators now use ZDF.
// ============================================================================
/*
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

			// Soft saturation: smooth compression near critical zone
			// Prevents discontinuity at hard clamp boundary
			if (r >= 0.995) {
				// Map r from [0.995, 1.0] → [0.995, 0.9999] using tanh curve
				double excess = r - 0.995;
				double maxExcess = 0.005;  // Range to compress
				double compressed = tanh(excess / maxExcess * 3.0) * 0.0049 + 0.995;
				r = compressed;
			}

			// Safety clamp (should rarely trigger now)
			if (r >= 0.9999) r = 0.9999;
			if (r < 0) r = 0;

			c=-(r*r);
			b=r*cos(PITWO/sampleRate*-frequency)*2.0;
			a=1.0-b-c;
			if(anti&&frequency!=0) {
				a=1.0/a;
				c*=-a;
				b*=-a;
			}

			// NaN/Inf safety check - reset to bypass if coefficients are invalid
			if (isnan(a) || isnan(b) || isnan(c) || isinf(a) || isinf(b) || isinf(c)) {
				a = 1.0; b = 0.0; c = 0.0;  // Pass-through
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
		// Using 0.80 factor for improved F1 stability (relaxed from 0.72)
		double bwAdjusted = bandwidth * 0.80;

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
*/
// ============================================================================
// END LEGACY CODE
// ============================================================================

// Zero Delay Feedback (ZDF) Resonator using State Variable Filter topology
// Based on Vadim Zavalishin (2012): "The Art of VA Filter Design"
//
// Advantages over traditional IIR:
// - Smooth parameter modulation without zipper noise or discontinuities
// - Inherently stable for all positive g and R values (no pole clamping needed)
// - Handles pitch-synchronous modulation cleanly (deltaF1/deltaB1)
// - Zero-delay feedback via implicit integration (trapezoidal rule)
//
// Mathematical foundation:
// Analog prototype: H(s) = (g*s) / (s² + 2*R*g*s + g²)
// Where: g = tan(π*f/fs), R = 1/(2*Q), Q = f/BW
//
// Trapezoidal integration (zero-delay feedback):
// v0 = k1 * (in - 2*R*s1 - s2)  // Bandpass output (implicit)
// v1 = s1 + g*v0                 // Lowpass state
// v2 = s2 + g*v1                 // Lowpass output
// s1 = v1 + g*v0                 // Update integrator 1
// s2 = v2 + g*v1                 // Update integrator 2
// k1 = 1 / (1 + 2*R*g + g*g)     // Normalization
class ZDFResonator {
	private:
	// Configuration
	int sampleRate;
	double frequency;
	double bandwidth;
	bool anti;  // Anti-resonator mode (zero instead of pole)

	// ZDF state variables (integrator states)
	double s1, s2;

	// Cached coefficients (updated only when parameters change)
	bool setOnce;
	double g;   // Frequency warping: tan(π*f/fs)
	double R;   // Damping coefficient: 1/(2*Q)
	double k1;  // Normalization: 1 / (1 + 2*R*g + g*g)

	public:
	ZDFResonator(int sampleRate, bool anti=false) {
		this->sampleRate = sampleRate;
		this->anti = anti;
		this->setOnce = false;
		this->s1 = 0;
		this->s2 = 0;
		this->g = 0;
		this->R = 0;
		this->k1 = 1.0;
	}

	void setParams(double frequency, double bandwidth) {
		// Only recalculate coefficients if parameters changed
		if(!setOnce || (frequency != this->frequency) || (bandwidth != this->bandwidth)) {
			this->frequency = frequency;
			this->bandwidth = bandwidth;

			// Edge case: zero frequency or bandwidth means bypass
			if (frequency <= 0 || bandwidth <= 0) {
				g = 0;
				R = 0;
				k1 = 1.0;
				setOnce = true;
				return;
			}

			// Calculate ZDF coefficients
			// g: frequency warping via bilinear transform
			double omega = M_PI * frequency / sampleRate;
			g = tan(omega);

			// Clamp g for numerical stability at very high frequencies
			// (approaching Nyquist, tan(π/2) → ∞)
			if (g > 10.0) {
				g = 10.0;  // Roughly 0.46 * sampleRate
			}

			// R: damping coefficient from quality factor
			// Q = frequency / bandwidth
			double Q = frequency / bandwidth;
			R = 1.0 / (2.0 * Q);

			// k1: normalization coefficient for unity gain at resonance
			k1 = 1.0 / (1.0 + 2.0 * R * g + g * g);

			setOnce = true;
		}
	}

	double resonate(double in, double frequency, double bandwidth) {
		setParams(frequency, bandwidth);

		// Bypass mode if frequency or bandwidth is zero
		if (g == 0) {
			return in;
		}

		// ZDF State Variable Filter algorithm (trapezoidal integration)
		// This computes the implicit solution with zero-delay feedback

		// Bandpass output (implicit feedback equation)
		double v0 = k1 * (in - 2.0 * R * s1 - s2);

		// State updates (integrate forward)
		double v1 = s1 + g * v0;
		double v2 = s2 + g * v1;

		// Update integrator states with zero-delay sample
		s1 = v1 + g * v0;
		s2 = v2 + g * v1;

		// Output selection
		if (anti) {
			// Anti-resonator mode (notch filter / zero)
			// Subtract bandpass from input to create notch
			return in - v0;
		} else {
			// Normal resonator mode (bandpass filter / pole)
			return v0;
		}
	}

	void setSampleRate(int sr) {
		sampleRate = sr;
		setOnce = false;  // Force coefficient recalculation
	}
};

// 4th-order ZDF resonator (cascade of two 2nd-order ZDF sections)
// Provides sharper formants with 24 dB/octave rolloff vs 12 dB/octave for 2nd-order
// Better vowel clarity and more focused formant peaks
class ZDFResonator4thOrder {
	private:
	int sampleRate;
	ZDFResonator stage1, stage2;

	public:
	ZDFResonator4thOrder(int sr): sampleRate(sr), stage1(sr), stage2(sr) {}

	double resonate(double in, double frequency, double bandwidth) {
		if (frequency <= 0) return in;  // Bypass if frequency is 0

		// Adjust bandwidth for equivalent Q when cascading
		// Using 0.80 factor (same as original IIR implementation)
		double bwAdjusted = bandwidth * 0.80;

		// Cascade two 2nd-order ZDF sections at same frequency
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
	ZDFResonator pole1, zero1, pole2, zero2;  // Two pole-zero pairs for tracheal coupling (using ZDF)

	public:
	TrachealResonator(int sr): sampleRate(sr), pole1(sr), zero1(sr, true), pole2(sr), zero2(sr, true) {}

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

		// Second tracheal zero (anti-resonator around 1500 Hz typical)
		if (frame->ftzFreq2 > 0) {
			output = zero2.resonate(output, frame->ftzFreq2, frame->ftzBw2);
		}

		return output;
	}
};

class CascadeFormantGenerator {
	private:
	int sampleRate;
	// F1-F3: 4th-order ZDF resonators for sharper, more focused formants
	ZDFResonator4thOrder r1, r2, r3;
	// F4-F6: 2nd-order ZDF resonators (wider bandwidths, less benefit from 4th-order)
	ZDFResonator r4, r5, r6, rN0, rNP;

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
		// Adaptive cascading: F2-F3 use 0.75 effective factor (pre-scale to compensate for 0.80 internal)
		output=r3.resonate(output, frame->cf3, frame->cb3 * 0.9375);  // 0.9375 = 0.75/0.80
		output=r2.resonate(output, frame->cf2, frame->cb2 * 0.9375);  // Effective: 0.75
		// Pitch-synchronous F1 modulation: during glottal open phase,
		// F1 rises and B1 widens due to subglottal coupling (Klatt 1990)
		double f1 = frame->cf1;
		double b1 = frame->cb1;
		if (glottisOpen) {
			f1 += frame->deltaF1;
			b1 += frame->deltaB1;
		}
		output=r1.resonate(output, f1, b1);
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
		// Note: burstAmplitude is NOT interpolated during frame fade (handled in frame.cpp)
		// so this triggers immediately at full amplitude
		if (lastBurstAmp <= 0 && burstAmplitude > 0) {
			burstPhase = 0;  // Reset burst to start
		}
		lastBurstAmp = burstAmplitude;

		if (burstPhase >= 1.0) {
			return 0;  // Burst complete
		}

		// Calculate envelope: quadratic decay from 1 to 0 over burst duration
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
	ZDFResonator r1, r2, r3, r4, r5, r6;  // Using ZDF resonators for smooth modulation

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
		// Enable denormal suppression to prevent CPU stalls from subnormal floats
		enableDenormalSuppression();
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
				// Soft limiting using tanh for smoother clipping
				double scaled = out * 2500;  // Reduced from 4000 to prevent clipping
				double limited = tanh(scaled / 32000.0) * 32000.0;  // Soft limit
				// Use rounding instead of truncation to reduce quantization distortion
				sampleBuf[i].value = (short)lrint(limited);
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
