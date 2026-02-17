# -*- coding: utf-8 -*-
"""
Shared test utilities for NVSpeechPlayer phoneme tests.

Provides common functions for WAV output, sample collection, and
phoneme frame building using the actual phoneme data as source of truth.
Used by test_vowels.py, test_consonants.py, test_engine.py, etc.
"""

import os
import sys
import wave
import struct

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import speechPlayer
import ipa
from data import data as phoneme_data

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

SAMPLE_RATE = 44100


def save_wav(filename, samples, sample_rate=SAMPLE_RATE):
    """Save samples to WAV file in the test output directory.

    Args:
        filename: WAV filename (saved under tests/output/)
        samples: List of int16 sample values
        sample_rate: Sample rate (default 44100)

    Returns:
        Full filepath of saved WAV.
    """
    filepath = os.path.join(OUTPUT_DIR, filename)
    with wave.open(filepath, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        data = struct.pack(f'<{len(samples)}h', *samples)
        wav.writeframes(data)
    return filepath


def collect_samples(sp):
    """Drain all synthesized samples from a SpeechPlayer instance.

    Args:
        sp: speechPlayer.SpeechPlayer instance

    Returns:
        List of int16 sample values.
    """
    samples = []
    while True:
        chunk = sp.synthesize(4096)
        if not chunk:
            break
        n = chunk.length
        samples.extend(struct.unpack(f'<{n}h', bytes(chunk)[:n * 2]))
    return samples


def build_phoneme_frame(ipa_char, pitch=120):
    """Build a frame from phoneme data (for tests that need frame-level control).

    Uses applyPhonemeToFrame() to read live data from data/*.py,
    then sets pitch and gain defaults suitable for test output.

    Args:
        ipa_char: IPA character key into phoneme_data (e.g. 'a', 's', 'm')
        pitch: F0 in Hz (default 120)

    Returns:
        speechPlayer.Frame configured from phoneme data.
    """
    frame = speechPlayer.Frame()
    ipa.applyPhonemeToFrame(frame, phoneme_data[ipa_char])
    frame.preFormantGain = 1.0
    frame.outputGain = 2.0
    frame.voicePitch = pitch
    frame.endVoicePitch = pitch
    return frame


def synthesize_phoneme(ipa_char, duration_ms=400, pitch=120):
    """Synthesize a phoneme using the full ipa.py pipeline with phoneme data.

    Args:
        ipa_char: IPA character (e.g. 'a', 's', 'm')
        duration_ms: Minimum duration in ms (default 400)
        pitch: F0 in Hz (default 120)

    Returns:
        List of int16 sample values.
    """
    sp = speechPlayer.SpeechPlayer(SAMPLE_RATE)
    for frame, min_dur, fade_dur in ipa.generateSubFramesAndTiming(
        ipa_char, speed=1, basePitch=pitch, inflection=0
    ):
        sp.queueFrame(frame, max(min_dur, duration_ms), fade_dur)
    return collect_samples(sp)
