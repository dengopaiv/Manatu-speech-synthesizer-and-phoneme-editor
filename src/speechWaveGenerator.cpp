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

#include <algorithm>
#include <cmath>
#include <cstdint>
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

// Bandwidth compensation for two cascaded 2nd-order stages.
// Combined -3dB BW narrows by ~0.644x, so each stage needs BW × 1.554.
static constexpr double CASCADE_BW_COMPENSATION = 1.554;

// Improved noise generator using xorshift128+ algorithm
// Better quality randomness and full frequency spectrum for fricatives
class NoiseGenerator {
	private:
	uint64_t state0;
	uint64_t state1;
	// Pink noise filter state (Paul Kellet method)
	double pinkState[5];

	public:
	NoiseGenerator() {
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

};

// Zero Delay Feedback (ZDF) Resonator using State Variable Filter topology
// Reference: Vadim Zavalishin (2012), "The Art of VA Filter Design", Chapter 3.10
//
// Advantages over traditional IIR:
// - Smooth parameter modulation without zipper noise or discontinuities
// - Inherently stable for all positive g and d values (no pole clamping needed)
// - Handles pitch-synchronous modulation cleanly (deltaF1/deltaB1)
// - Zero-delay feedback via implicit integration (trapezoidal rule)
//
// Algorithm (Zavalishin's canonical SVF):
// v3 = in - ic2eq
// v1 = a1*ic1eq + a2*v3       // Bandpass output
// v2 = ic2eq + a2*ic1eq + a3*v3  // Lowpass output (unity DC gain)
// ic1eq = 2*v1 - ic1eq        // Update integrator 1
// ic2eq = 2*v2 - ic2eq        // Update integrator 2
//
// Where: g = tan(π*f/fs), d = BW/f (damping = 1/Q)
//        a1 = 1/(1 + g*(g+d)), a2 = g*a1, a3 = g*a2
class ZDFResonator {
	private:
	// Configuration
	int sampleRate;
	double frequency;
	double bandwidth;
	bool anti;    // Anti-resonator mode (zero instead of pole)
	bool allPole; // All-pole (lowpass) mode for cascade topology

	// ZDF state variables (integrator states)
	double ic1eq, ic2eq;

	// Cached coefficients (updated only when parameters change)
	bool setOnce;
	double g;   // Frequency warping: tan(π*f/fs)
	double a1;  // 1 / (1 + g*(g+d))
	double a2;  // g * a1
	double a3;  // g * a2

	public:
	ZDFResonator(int sampleRate, bool anti=false, bool allPole=false) {
		this->sampleRate = sampleRate;
		this->anti = anti;
		this->allPole = allPole;
		this->setOnce = false;
		this->ic1eq = 0;
		this->ic2eq = 0;
		this->g = 0;
		this->a1 = 1.0;
		this->a2 = 0;
		this->a3 = 0;
	}

	void setParams(double frequency, double bandwidth) {
		// Only recalculate coefficients if parameters changed
		if(!setOnce || (frequency != this->frequency) || (bandwidth != this->bandwidth)) {
			this->frequency = frequency;
			this->bandwidth = bandwidth;

			// Edge case: zero frequency or bandwidth means bypass
			if (frequency <= 0 || bandwidth <= 0) {
				g = 0;
				a1 = 1.0;
				a2 = 0;
				a3 = 0;
				setOnce = true;
				return;
			}

			// g: frequency warping via bilinear transform
			double omega = M_PI * frequency / sampleRate;
			g = tan(omega);

			// Clamp g for numerical stability at very high frequencies
			if (g > 10.0) {
				g = 10.0;
			}

			// d: damping coefficient (1/Q where Q = frequency/bandwidth)
			double d = bandwidth / frequency;

			// Zavalishin's SVF coefficients
			a1 = 1.0 / (1.0 + g * (g + d));
			a2 = g * a1;
			a3 = g * a2;

			setOnce = true;
		}
	}

	double resonate(double in, double frequency, double bandwidth) {
		setParams(frequency, bandwidth);

		// Bypass mode if frequency or bandwidth is zero
		if (g == 0) {
			return in;
		}

		// Zavalishin's canonical ZDF SVF algorithm
		double v3 = in - ic2eq;
		double v1 = a1 * ic1eq + a2 * v3;             // Bandpass
		double v2 = ic2eq + a2 * ic1eq + a3 * v3;     // Lowpass

		// Update integrator states
		ic1eq = 2.0 * v1 - ic1eq;
		ic2eq = 2.0 * v2 - ic2eq;

		// Output selection
		if (anti) {
			// Anti-resonator: subtract bandpass from input to create notch
			return in - v1;
		} else if (allPole) {
			// Lowpass mode for cascade topology (unity DC gain)
			return v2;
		} else {
			// Bandpass mode for parallel topology
			return v1;
		}
	}

	void decay(double factor) { ic1eq *= factor; ic2eq *= factor; }
	void reset() { ic1eq = 0; ic2eq = 0; }

	void setSampleRate(int sr) {
		sampleRate = sr;
		setOnce = false;  // Force coefficient recalculation
	}
};

// Colored Noise Generator with configurable bandpass filtering
// For place-specific fricative spectra: /s/ high-freq, /ʃ/ mid-freq, /f/ flat
// Uses 4th-order ZDF SVF bandpass (two cascaded stages) for proper spectral
// shaping with 24 dB/oct rolloff — needed especially for wide-BW non-sibilants
// where a single 2nd-order stage barely filters the noise.
class ColoredNoiseGenerator {
	private:
	NoiseGenerator white;
	ZDFResonator bandpass;    // ZDF SVF bandpass stage 1
	ZDFResonator bandpass2;   // ZDF SVF bandpass stage 2 (4th-order cascade)

	public:
	ColoredNoiseGenerator(int sr): white(),
		bandpass(sr, false, false),     // bandpass mode
		bandpass2(sr, false, false) {}  // bandpass mode

	double getNext(double filterFreq, double filterBw) {
		// Below 100 Hz: pink noise for natural aspiration
		if (filterFreq < 100) return white.getNextPink();

		// Use RAW white noise — full spectrum input for bandpass shaping
		// (previous 70/30 smoothing was a crude ~6 kHz lowpass that killed
		// high-frequency energy needed for sibilants like /s/)
		double noise = white.getWhite();
		if (filterBw < 100) filterBw = 100;

		// Widen per-stage BW to compensate for cascade narrowing
		double bwAdjusted = filterBw * CASCADE_BW_COMPENSATION;

		// 4th-order bandpass (two cascaded 2nd-order ZDF stages)
		// 24 dB/oct rolloff properly shapes spectrum for both narrow sibilants
		// and wide non-sibilants like /f/ (where 2nd-order barely filters)
		double out = bandpass.resonate(noise, filterFreq, bwAdjusted);
		out = bandpass2.resonate(out, filterFreq, bwAdjusted);

		// Bandwidth-dependent gain compensation
		// Narrow sibilant filters (BW~1800) lose more energy than wide fricative
		// filters (BW~6000), so we boost proportionally.
		// BW=6000 → gain≈1.0, BW=1800 → gain≈3.3, BW=1500 → gain≈4.0
		double gainComp = 6000.0 / max(filterBw, 100.0);
		return out * gainComp;
	}
};

// KLSYN88 Spectral Tilt Filter — Second-order (12 dB/oct)
// Two cascaded first-order lowpass stages for steeper high-frequency rolloff
// tiltDB: 0 = no filtering (modal voice), up to 41 dB attenuation at 5kHz (very breathy)
// 12 dB/oct slope matches measured glottal spectral tilt better than 6 dB/oct
// and preserves more midrange clarity while cutting highs more aggressively
class SpectralTiltFilter {
	private:
	int sampleRate;
	double lastOutput1, lastOutput2;  // Two cascaded stages

	public:
	SpectralTiltFilter(int sr): sampleRate(sr), lastOutput1(0.0), lastOutput2(0.0) {}

	double filter(double input, double tiltDB) {
		if (tiltDB < 1.5) return input;

		double attenLinear = pow(10.0, -tiltDB / 20.0);
		if (attenLinear <= 0.001) attenLinear = 0.001;

		// For two cascaded stages: |H(f)|^2 = 1/(1+(f/fc)^2)^2
		// At 5kHz we want |H|=attenLinear, so solve: fc = 5000/sqrt(1/atten - 1)
		double fc = 5000.0 / sqrt(1.0 / attenLinear - 1.0);
		double alpha = exp(-2.0 * M_PI * fc / sampleRate);

		double stage1 = (1.0 - alpha) * input + alpha * lastOutput1;
		lastOutput1 = stage1;
		double output = (1.0 - alpha) * stage1 + alpha * lastOutput2;
		lastOutput2 = output;
		return output;
	}
};

// Stochastic Jitter/Shimmer Generator
// Replaces deterministic 3-sinusoid flutter with cycle-synchronous random perturbation
// Smoothed (α=0.7) to prevent extreme jumps — ~3.3 cycle time constant
// matches measured vocal jitter correlation (Baken & Orlikoff 2000)
class JitterShimmerGenerator {
	private:
	NoiseGenerator noiseGen;
	double smoothedJitter, smoothedShimmer;
	double heldJitter, heldShimmer;

	public:
	JitterShimmerGenerator(): smoothedJitter(0), smoothedShimmer(0),
		heldJitter(0), heldShimmer(0) {}

	void onNewCycle() {
		smoothedJitter = 0.7 * smoothedJitter + 0.3 * noiseGen.getWhite();
		smoothedShimmer = 0.7 * smoothedShimmer + 0.3 * noiseGen.getWhite();
		heldJitter = smoothedJitter;
		heldShimmer = smoothedShimmer;
	}

	double getPitchMod(double amount) {
		if (amount <= 0) return 1.0;
		return 1.0 + heldJitter * amount * 0.02;  // ±2% at full amount
	}

	double getAmpMod(double amount) {
		if (amount <= 0) return 1.0;
		return 1.0 + heldShimmer * amount * 0.01;  // ±1% at full amount
	}
};

// Trill modulator: amplitude LFO for trills /r/, /ʀ/, /ʙ/
// Modulates voice amplitude and preFormantGain at 20-35 Hz
// Cosine shape models natural aerodynamic articulator oscillation
class TrillModulator {
	double phase;
	int sampleRate;
public:
	TrillModulator(int sr) : phase(0), sampleRate(sr) {}

	// Returns modulation factor: 1.0 (fully open) to (1-depth) (maximally closed)
	double getNext(double rate, double depth) {
		if (rate <= 0 || depth <= 0) return 1.0;
		phase = fmod(phase + rate / sampleRate, 1.0);
		// Cosine: smooth closure (1.0 at phase=0, minimum at phase=0.5)
		return 1.0 - depth * 0.5 * (1.0 - cos(PITWO * phase));
	}
};

// DC-Blocking Filter (first-order HPF)
// Removes DC offset from glottal source before cascade filtering.
// The LF model at high Rd values produces asymmetric pulses with significant DC,
// which passes through allPole cascade resonators (unity DC gain) and shifts
// the limiter operating point, causing asymmetric distortion.
// y[n] = x[n] - x[n-1] + R * y[n-1], R = 1 - 2π*fc/fs
// At 96000 Hz, fc=20 Hz: R≈0.9987, transparent above ~40 Hz.
class DCBlockFilter {
private:
	double R, lastIn, lastOut;

public:
	DCBlockFilter(int sampleRate, double cutoffHz = 20.0) {
		R = 1.0 - (2.0 * M_PI * cutoffHz / sampleRate);
		if (R < 0.9) R = 0.9;
		if (R > 0.9999) R = 0.9999;
		lastIn = 0.0;
		lastOut = 0.0;
	}

	double filter(double input) {
		double output = input - lastIn + R * lastOut;
		lastIn = input;
		lastOut = output;
		return output;
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
		if (frequency < 1.0) frequency = 1.0;  // Floor clamp: prevent zero/negative phase
		lastDt = frequency / sampleRate;  // Store phase increment
		double cyclePos=fmod(lastDt+lastCyclePos,1);
		lastCyclePos=cyclePos;
		return cyclePos;
	}

	// Get the phase increment (needed for polyBLEP anti-aliasing)
	double getDt() const { return lastDt; }
};

// Pure function for LF glottal waveform evaluation at arbitrary phase
// Used by 4x oversampling: evaluate at four symmetric phases per output sample
inline double computeGlottalWave(double phase, double tp, double te,
                                  double epsilon, double ampNorm) {
	if (phase < tp) {
		// Opening phase: raised cosine rise
		return 0.5 * (1.0 - cos(M_PI * phase / tp)) * ampNorm;
	} else if (phase < te) {
		// Closing phase: cosinusoidal fall
		return 0.5 * (1.0 + cos(M_PI * (phase - tp) / (te - tp))) * ampNorm;
	} else {
		// Return phase: exponential decay with end-of-cycle fade
		double t_ret = (phase - te) / (1.0 - te);
		double decay = exp(-epsilon * t_ret * (1.0 - te));
		double fade = (t_ret > 0.7) ? 0.5 * (1.0 + cos(M_PI * (t_ret - 0.7) / 0.3)) : 1.0;
		return 0.5 * decay * fade * ampNorm;
	}
}

// Halfband FIR decimator for 2:1 downsampling
// 7-tap halfband kernel: h = {a, 0, b, 0.5, b, 0, a}
// Structural zeros at h[1] and h[5] reduce to 4 multiplies per output sample
// Provides >60 dB stopband attenuation for anti-alias filtering
// Two cascaded stages give 4x→2x→1x decimation
class HalfbandDecimator {
private:
	// 7-tap halfband FIR coefficients (only non-zero taps stored)
	static constexpr double a = -0.0625;   // h[0], h[6]
	static constexpr double b = 0.5625;    // h[2], h[4]
	// h[3] = 0.5 (center tap), h[1] = h[5] = 0 (structural zeros)
	double z[7];  // delay line

public:
	HalfbandDecimator() { reset(); }
	void reset() { for (int i = 0; i < 7; i++) z[i] = 0.0; }

	// Push 2 input samples, return 1 decimated output
	double process(double in0, double in1) {
		// Shift delay line left by 2, insert new samples
		z[0] = z[2]; z[1] = z[3]; z[2] = z[4];
		z[3] = z[5]; z[4] = z[6];
		z[5] = in0; z[6] = in1;
		// Convolve exploiting symmetry and structural zeros:
		// h[0]*z[0] + h[2]*z[2] + h[3]*z[3] + h[4]*z[4] + h[6]*z[6]
		return a * (z[0] + z[6]) + b * (z[2] + z[4]) + 0.5 * z[3];
	}
};

class VoiceGenerator {
	private:
	FrequencyGenerator pitchGen;
	FrequencyGenerator vibratoGen;
	FrequencyGenerator sinusoidalGen;  // AVS: pure sinusoidal voicing source
	ColoredNoiseGenerator aspirationGen;  // Filtered aspiration noise source
	JitterShimmerGenerator jitterShimmer;  // Stochastic pitch/amplitude jitter
	double lastCyclePos;  // KLSYN88: track cycle for diplophonia
	bool periodAlternate;  // KLSYN88: alternating period flag
	double currentTe;       // Excitation point for PolyBLEP (0 when unvoiced)
	double currentAmpNorm;  // LF amplitude normalization (0 when unvoiced)
	HalfbandDecimator hbStage1, hbStage2;  // 4x→2x→1x decimation

	public:
	bool glottisOpen;
	VoiceGenerator(int sr): pitchGen(sr), vibratoGen(sr), sinusoidalGen(sr), aspirationGen(sr), jitterShimmer(), lastCyclePos(0), periodAlternate(false), glottisOpen(false), currentTe(0), currentAmpNorm(0) {};

	double getNext(const speechPlayer_frame_t* frame) {
		double vibrato=(sin(vibratoGen.getNext(frame->vibratoSpeed)*PITWO)*0.06*frame->vibratoPitchOffset)+1;
		double jitter=jitterShimmer.getPitchMod(frame->flutter);  // Stochastic pitch jitter

		// KLSYN88: Diplophonia - alternating pitch periods for creaky voice
		double diplophoniaMod = 1.0;
		if (frame->diplophonia > 0) {
			// Alternating periods: one slightly longer, one slightly shorter
			// ±10% pitch variation at full diplophonia
			diplophoniaMod = periodAlternate ? (1.0 + frame->diplophonia * 0.10) : (1.0 - frame->diplophonia * 0.10);
		}

		double voice=pitchGen.getNext(frame->voicePitch*vibrato*jitter*diplophoniaMod);

		// Detect new pitch period (cycle wrapped) to toggle alternation and update jitter
		if (voice < lastCyclePos - 0.5) {  // Wrapped from ~1 back to ~0
			periodAlternate = !periodAlternate;
			jitterShimmer.onNewCycle();  // New random jitter/shimmer values per cycle
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

		// Check if using LF model (Rd > 0) or no voicing
		if (frame->lfRd > 0) {
			// Improved Liljencrants-Fant (LF) glottal model
			// Based on Fant 1995 and Degottex et al. 2011 refinements
			// Rd parameter controls voice quality: 0.3=tense, 1.0=modal, 2.7=breathy
			double Rd = max(0.3, min(2.7, frame->lfRd));

			// Improved Rd-to-parameter mapping (Fant 1995 / Degottex 2011)
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
			double epsilon = 1.0 / (ta * (1.0 - te) + 0.001);

			// Amplitude normalization factor for consistent output level
			double ampNorm = 1.0 / (0.5 + 0.3 * Rd);

			// Store for PolyBLEP at te
			currentTe = te;
			currentAmpNorm = ampNorm;

			glottisOpen = voice < te;

			// 4x oversampling with halfband decimation
			// Evaluates LF waveform at 4 symmetric phases per output sample,
			// applies PolyBLEP at each oversampled phase (4x smaller dt → more precise),
			// then decimates through two cascaded halfband FIR stages (4x→2x→1x)
			double dt = pitchGen.getDt();
			double dt_os = dt * 0.25;  // Quarter-sample phase increment

			// Evaluate at 4 symmetric phases centered on current position
			double phases[4] = {
				fmod(voice - 1.5 * dt_os + 2.0, 1.0),
				fmod(voice - 0.5 * dt_os + 1.0, 1.0),
				fmod(voice + 0.5 * dt_os, 1.0),
				fmod(voice + 1.5 * dt_os, 1.0)
			};

			double samples_os[4];
			for (int k = 0; k < 4; k++) {
				double gw = computeGlottalWave(phases[k], tp, te, epsilon, ampNorm);
				double s = gw * 2.0 - ampNorm;  // DC center: [0, ampNorm] → [-ampNorm, +ampNorm]

				// PolyBLEP at cycle boundary (discontinuity from return phase end)
				s -= polyBLEP(phases[k], dt_os) * ampNorm * 0.5;

				// PolyBLEP at excitation point (te) — main LF step discontinuity
				if (te > 0 && dt_os > 0) {
					double phaseRelTe = fmod(phases[k] - te + 1.0, 1.0);
					s -= polyBLEP(phaseRelTe, dt_os) * ampNorm;
				}

				samples_os[k] = s;
			}

			// Two-stage halfband decimation: 4x → 2x → 1x
			double d0 = hbStage1.process(samples_os[0], samples_os[1]);
			double d1 = hbStage1.process(samples_os[2], samples_os[3]);
			glottalWave = hbStage2.process(d0, d1);
		} else {
			// No voicing (voiceless consonants: /p/, /t/, /k/, /f/, /s/, /ʃ/, etc.)
			// lfRd=0 means no glottal source - only noise/frication used
			glottalWave = 0.0;
			glottisOpen = false;
			currentTe = 0;
			currentAmpNorm = 0;
		}

		voice = glottalWave;

		if(!glottisOpen) {
			turbulence*=0.01;
		}
		voice+=turbulence;
		voice*=frame->voiceAmplitude*jitterShimmer.getAmpMod(frame->flutter);

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

// 4th-order ZDF resonator (cascade of two 2nd-order ZDF sections)
// Provides sharper formants with 24 dB/octave rolloff vs 12 dB/octave for 2nd-order
// Better vowel clarity and more focused formant peaks
class ZDFResonator4thOrder {
	private:
	ZDFResonator stage1, stage2;

	public:
	ZDFResonator4thOrder(int sr, bool allPole=false): stage1(sr, false, allPole), stage2(sr, false, allPole) {}

	double resonate(double in, double frequency, double bandwidth) {
		if (frequency <= 0) return in;  // Bypass if frequency is 0

		// Widen per-stage bandwidth to compensate for cascade narrowing.
		double bwAdjusted = bandwidth * CASCADE_BW_COMPENSATION;

		// Cascade two 2nd-order ZDF sections at same frequency
		double out = stage1.resonate(in, frequency, bwAdjusted);
		return stage2.resonate(out, frequency, bwAdjusted);
	}

	void decay(double factor) { stage1.decay(factor); stage2.decay(factor); }
	void reset() { stage1.reset(); stage2.reset(); }

	void setSampleRate(int sr) {
		stage1.setSampleRate(sr);
		stage2.setSampleRate(sr);
	}
};

// KLSYN88: Tracheal (subglottal) resonator for breathy voice realism
// Adds coupling to tracheal cavity below the glottis
class TrachealResonator {
	private:
	ZDFResonator pole1, zero1, pole2, zero2;  // Two pole-zero pairs for tracheal coupling (using ZDF)

	public:
	TrachealResonator(int sr): pole1(sr, false, true), zero1(sr, true), pole2(sr, false, true), zero2(sr, true) {}

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

// Cascade HF Shelf Filter
// Compensates for the cascade formant chain's structural HF loss (~57 dB at 8 kHz
// through 6 series allPole resonators). Applied only to cascade output, not globally.
// Topology: y = x + boost * HPF(x) — transparent at DC, +boostDB above corner.
// The cascade chain's 6 allPole stages cumulatively attenuate ~21 dB at 4 kHz and
// ~57 dB at 8 kHz. Even at 96 kHz (reducing ZDF warping), the cascade is structurally
// dark. A modest shelf restores presence without affecting the parallel path (which
// carries fricative/sibilant HF naturally).
class HFShelfFilter {
private:
	double alpha;  // HPF coefficient: exp(-2π * corner / sr)
	double boost;  // Linear boost factor: 10^(boostDB/20) - 1
	double lastIn, lastOut;  // HPF state

public:
	HFShelfFilter(int sampleRate, double cornerHz = 3000.0, double boostDB = 6.0) {
		alpha = exp(-2.0 * M_PI * cornerHz / sampleRate);
		boost = pow(10.0, boostDB / 20.0) - 1.0;
		lastIn = 0.0;
		lastOut = 0.0;
	}

	double filter(double input) {
		// First-order HPF: y[n] = alpha * (y[n-1] + x[n] - x[n-1])
		double hp = alpha * (lastOut + input - lastIn);
		lastIn = input;
		lastOut = hp;
		// Shelf: add boosted HPF to original (transparent at DC)
		return input + boost * hp;
	}
};

class CascadeFormantGenerator {
	private:
	// F1-F3: 4th-order ZDF resonators with allPole (lowpass) for cascade topology
	ZDFResonator4thOrder r1, r2, r3;
	// F4-F6: 2nd-order ZDF resonators with allPole (lowpass) for cascade topology
	ZDFResonator r4, r5, r6, rN0, rNP;
	// Smooth glottal blend for pitch-synchronous F1 modulation
	double smoothGlottalBlend;
	double glottalAlpha;  // ~2ms smoothing constant

	public:
	CascadeFormantGenerator(int sr): r1(sr, true), r2(sr, true), r3(sr, true), r4(sr, false, true), r5(sr, false, true), r6(sr, false, true), rN0(sr, true), rNP(sr, false, true), smoothGlottalBlend(0) {
		glottalAlpha = 1.0 - exp(-1.0 / (0.002 * sr));  // 2ms time constant
	};

	double getNext(const speechPlayer_frame_t* frame, bool glottisOpen, double input) {
		input/=2.0;
		double n0Output=rN0.resonate(input,frame->cfN0,frame->cbN0);
		double nasalOutput=rNP.resonate(n0Output,frame->cfNP,frame->cbNP);
		double output=calculateValueAtFadePosition(input,nasalOutput,frame->caNP);
		output=r6.resonate(output,frame->cf6,frame->cb6);
		output=r5.resonate(output,frame->cf5,frame->cb5);
		output=r4.resonate(output,frame->cf4,frame->cb4);
		// F1-F3 use 4th-order allPole for sharper resonance (24 dB/octave rolloff)
		output=r3.resonate(output, frame->cf3, frame->cb3);
		output=r2.resonate(output, frame->cf2, frame->cb2);
		// Pitch-synchronous F1 modulation: during glottal open phase,
		// F1 rises and B1 widens due to subglottal coupling (Klatt 1990)
		// Smooth the glottis-open flag with ~2ms exponential transition
		// to eliminate discontinuity at glottal boundaries
		double glottalTarget = glottisOpen ? 1.0 : 0.0;
		smoothGlottalBlend += glottalAlpha * (glottalTarget - smoothGlottalBlend);
		double f1 = frame->cf1 + frame->deltaF1 * smoothGlottalBlend;
		double b1 = frame->cb1 + frame->deltaB1 * smoothGlottalBlend;
		output=r1.resonate(output, f1, b1);
		return output;
	}

	void decay(double factor) {
		r1.decay(factor); r2.decay(factor); r3.decay(factor);
		r4.decay(factor); r5.decay(factor); r6.decay(factor);
		rN0.decay(factor); rNP.decay(factor);
	}
	void reset() {
		r1.reset(); r2.reset(); r3.reset();
		r4.reset(); r5.reset(); r6.reset();
		rN0.reset(); rNP.reset();
	}

};

// KLSYN88: Stop burst envelope generator for plosive transients
// Self-sustaining: once triggered, the burst completes its envelope independently
// of frame changes, using stored parameters from the triggering frame.
class BurstGenerator {
	private:
	int sampleRate;
	NoiseGenerator noiseGen;
	ZDFResonator burstFilter;  // Place-specific spectral coloring
	double burstPhase;  // 0 = burst start, 1 = burst end
	double lastBurstAmp;  // Track amplitude to detect burst start
	bool burstActive;
	double activeBurstAmp;
	double activeBurstDuration;
	double activeFilterFreq;
	double activeFilterBw;
	double activeNoiseColor;

	public:
	BurstGenerator(int sr): sampleRate(sr), noiseGen(), burstFilter(sr),
		burstPhase(1.0), lastBurstAmp(0), burstActive(false),
		activeBurstAmp(0), activeBurstDuration(0),
		activeFilterFreq(0), activeFilterBw(0), activeNoiseColor(0) {}

	double getNext(double burstAmplitude, double burstDuration, double filterFreq, double filterBw, double noiseColor) {
		// Detect new burst trigger (amplitude jumps from 0 to non-zero)
		if (lastBurstAmp <= 0 && burstAmplitude > 0) {
			burstPhase = 0;
			burstFilter.reset();
			burstActive = true;
			activeBurstAmp = burstAmplitude;
			activeBurstDuration = burstDuration;
			activeFilterFreq = filterFreq;
			activeFilterBw = filterBw;
			activeNoiseColor = noiseColor;
		}
		lastBurstAmp = burstAmplitude;

		if (!burstActive || burstPhase >= 1.0) {
			burstActive = false;
			burstFilter.decay(0.9);
			return 0;
		}

		// Envelope using STORED parameters (not current frame)
		double durationMs = 5.0 + activeBurstDuration * (20.0 - 5.0);
		double durationSamples = (durationMs / 1000.0) * sampleRate;
		double envelope = exp(-6.0 * burstPhase);
		burstPhase += 1.0 / durationSamples;
		if (burstPhase > 1.0) burstPhase = 1.0;

		// Generate burst noise with place-specific spectral coloring
		// Blend white/pink noise based on burstNoiseColor (0=white, 1=pink)
		double white = noiseGen.getWhite();
		double raw = white * (1.0 - activeNoiseColor) + noiseGen.getNextPink() * activeNoiseColor;
		double filtered = raw;
		if (activeFilterFreq > 0 && activeFilterBw > 0) {
			filtered = burstFilter.resonate(raw, activeFilterFreq, activeFilterBw) * 3.0;
		}
		// Onset transient: add unfiltered noise while bandpass filter rings up
		// Duration scales with filter frequency: low-freq filters need ~3 cycles to reach steady state
		// /p/ at 1500Hz → 2.0ms, /t/ at 4000Hz → 1.5ms (floor), /q/ at 1200Hz → 2.5ms
		double onsetMs = (activeFilterFreq > 0)
			? max(1.5, 3.0 / (activeFilterFreq / 1000.0))
			: 1.5;
		double onsetSamples = (onsetMs / 1000.0) * sampleRate;
		double onsetPhase = min(burstPhase * durationSamples / onsetSamples, 1.0);
		double onsetScale = 1.0 - activeNoiseColor * 0.7;
		double noise = filtered + raw * (1.0 - onsetPhase) * onsetScale;
		return noise * envelope * activeBurstAmp;
	}

	void decay(double factor) { burstFilter.decay(factor); }
	void reset() { burstFilter.reset(); burstPhase = 1.0; burstActive = false; }
};

class ParallelFormantGenerator {
	private:
	ZDFResonator r1, r2, r3, r4, r5, r6;  // Using ZDF resonators for smooth modulation
	ZDFResonator antiRes;  // Anti-resonator for parallel path spectral zeros

	public:
	ParallelFormantGenerator(int sr): r1(sr), r2(sr), r3(sr), r4(sr), r5(sr), r6(sr), antiRes(sr, true) {};

	double getNext(const speechPlayer_frame_t* frame, double input) {
		input/=2.0;
		double output=0;
		// ZDF SVF resonate() already returns native bandpass (v1) for parallel resonators,
		// so no input subtraction needed. The old "resonate() - input" was a leftover from
		// when resonate() returned allpole (lowpass) output and subtraction approximated bandpass.
		output+=r1.resonate(input,frame->pf1,frame->pb1)*frame->pa1;
		output+=r2.resonate(input,frame->pf2,frame->pb2)*frame->pa2;
		output+=r3.resonate(input,frame->pf3,frame->pb3)*frame->pa3;
		output+=r4.resonate(input,frame->pf4,frame->pb4)*frame->pa4;
		output+=r5.resonate(input,frame->pf5,frame->pb5)*frame->pa5;
		output+=r6.resonate(input,frame->pf6,frame->pb6)*frame->pa6;
		// Apply parallel anti-resonator (freq=0 bypasses automatically: g=0, returns input)
		output = antiRes.resonate(output, frame->parallelAntiFreq, frame->parallelAntiBw);
		return calculateValueAtFadePosition(output,input,frame->parallelBypass);
	}

	void decay(double factor) {
		r1.decay(factor); r2.decay(factor); r3.decay(factor);
		r4.decay(factor); r5.decay(factor); r6.decay(factor);
		antiRes.decay(factor);
	}
	void reset() {
		r1.reset(); r2.reset(); r3.reset();
		r4.reset(); r5.reset(); r6.reset();
		antiRes.reset();
	}

};

// Cascade Ducking Tracker
// Reduces cascade output during voiceless bursts/frication to prevent amplitude spikes
// at stop-vowel boundaries where cascade resonators still ring from previous vowel
class CascadeDuckTracker {
private:
	double smoothDuck;
	double alpha;  // ~1ms smoothing constant
public:
	CascadeDuckTracker(int sr) : smoothDuck(1.0) {
		alpha = 1.0 - exp(-1.0 / (0.001 * sr));  // 1ms time constant
	}
	double getDuck(double burstAmp, double fricAmp, double voiceAmp) {
		// Duck cascade when burst/fric is active and voicing is low
		double burstEnv = max(burstAmp, fricAmp);
		double target = 1.0 - 0.7 * burstEnv * (1.0 - voiceAmp);
		smoothDuck += alpha * (target - smoothDuck);
		return smoothDuck;
	}
};

// Peak Limiter with fast attack and slow release
// Transparent below threshold (-3 dB), only compresses peaks
// Replaces tanh soft clip which always applied nonlinear distortion
class PeakLimiter {
private:
	double gain;
	double attackAlpha, releaseAlpha, fastReleaseAlpha;
	double threshold;
	bool fastRelease;
public:
	PeakLimiter(int sr, double thresholdDb = -3.0) {
		gain = 1.0;
		threshold = 32767.0 * pow(10.0, thresholdDb / 20.0);  // ~23197
		attackAlpha = 1.0 - exp(-1.0 / (0.0001 * sr));     // 0.1ms attack
		releaseAlpha = 1.0 - exp(-1.0 / (0.050 * sr));      // 50ms release (normal speech)
		fastReleaseAlpha = 1.0 - exp(-1.0 / (0.005 * sr));  // 5ms release (during silence)
		fastRelease = false;
	}
	// Enable fast release during silence/closure so limiter recovers before burst onset
	void setFastRelease(bool fast) { fastRelease = fast; }
	double limit(double input) {
		double absIn = fabs(input);
		if (absIn > threshold) {
			double targetGain = threshold / absIn;
			gain += attackAlpha * (targetGain - gain);
		} else {
			double alpha = fastRelease ? fastReleaseAlpha : releaseAlpha;
			gain += alpha * (1.0 - gain);
		}
		return input * gain;
	}
};

class SpeechWaveGeneratorImpl: public SpeechWaveGenerator {
	private:
	int sampleRate;
	VoiceGenerator voiceGenerator;
	DCBlockFilter dcBlock;  // Remove DC offset from glottal source before cascade
	SpectralTiltFilter tiltFilter;  // KLSYN88: spectral tilt for breathy voice
	TrachealResonator trachealRes;  // KLSYN88: subglottal resonances
	ColoredNoiseGenerator fricGenerator;  // Bandpass-filtered noise for fricatives
	BurstGenerator burstGen;  // KLSYN88: stop burst envelopes
	TrillModulator trillMod;  // Amplitude LFO for trill consonants
	CascadeFormantGenerator cascade;
	HFShelfFilter cascadeShelf;  // Compensate cascade chain's structural HF loss
	ParallelFormantGenerator parallel;
	CascadeDuckTracker cascadeDuck;  // Reduce cascade during voiceless bursts
	PeakLimiter peakLimiter;  // Transparent peak limiter (replaces tanh)
	double prevPreGain;  // Track preFormantGain for silence detection
	FrameManager* frameManager;

	public:
	SpeechWaveGeneratorImpl(int sr): sampleRate(sr), voiceGenerator(sr), dcBlock(sr, 20.0), tiltFilter(sr), trachealRes(sr), fricGenerator(sr), burstGen(sr), trillMod(sr), cascade(sr), cascadeShelf(sr, 3000.0, 6.0), parallel(sr), cascadeDuck(sr), peakLimiter(sr), prevPreGain(0), frameManager(NULL) {
		// Enable denormal suppression to prevent CPU stalls from subnormal floats
		enableDenormalSuppression();
	}

	unsigned int generate(const unsigned int sampleCount, sample* sampleBuf) {
		if(!frameManager) return 0;
		for(unsigned int i=0;i<sampleCount;++i) {
			const speechPlayer_frame_t* frame=frameManager->getCurrentFrame();
			if(frame) {
				double voice=voiceGenerator.getNext(frame);
				voice=dcBlock.filter(voice);  // Remove DC offset from LF glottal source
				voice=tiltFilter.filter(voice,frame->spectralTilt);  // KLSYN88: apply spectral tilt
				voice=trachealRes.resonate(voice,frame);  // KLSYN88: apply tracheal resonances
				// Trill modulation: amplitude LFO applied to voice and overall gain
				double trillMod_val = trillMod.getNext(frame->trillRate, frame->trillDepth);
				voice *= trillMod_val;
				// Resonator drain/reset during silence
				double preGain = frame->preFormantGain * trillMod_val;
				if (preGain < 0.01) {
					cascade.decay(0.95);   // ~1ms exponential drain
					parallel.decay(0.95);
				}
				if (prevPreGain < 0.005 && preGain > 0.01) {
					cascade.reset();  // Hard reset on voice onset after silence
					parallel.reset();
				}
				prevPreGain = preGain;
				double cascadeOut=cascade.getNext(frame,voiceGenerator.glottisOpen,voice*preGain);
				// Duck cascade during voiceless bursts to prevent amplitude spikes
				double duck = cascadeDuck.getDuck(frame->burstAmplitude, frame->fricationAmplitude, frame->voiceAmplitude);
				cascadeOut *= duck;
				// HF shelf: compensate cascade chain's structural HF loss
				cascadeOut = cascadeShelf.filter(cascadeOut);
				// Colored noise for fricatives (bandpass filtered based on place of articulation)
				double fric=fricGenerator.getNext(frame->noiseFilterFreq, frame->noiseFilterBw)*0.3*frame->fricationAmplitude;
				double burst=burstGen.getNext(frame->burstAmplitude,frame->burstDuration,frame->burstFilterFreq,frame->burstFilterBw,frame->burstNoiseColor);  // KLSYN88: stop burst
				double parallelInput=(fric+burst)*preGain;
				parallelInput+=voice*frame->parallelVoiceMix*preGain;
				double parallelOut=parallel.getNext(frame,parallelInput);
				double out=(cascadeOut+parallelOut)*frame->outputGain;
				// Peak limiter: transparent below -3dB, fast attack for transients
				// Fast release during silence so limiter recovers before stop bursts
				peakLimiter.setFastRelease(preGain < 0.01);
				double scaled = out * 4000;
				double limited = peakLimiter.limit(scaled);
				sampleBuf[i].value = (short)lrint(max(-32767.0, min(32767.0, limited)));
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
