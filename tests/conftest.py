# -*- coding: utf-8 -*-
"""
Shared test utilities for NVSpeechPlayer phoneme tests.

Provides common functions for WAV output and sample collection,
used by test_vowels.py, test_consonants.py, and test_coarticulation.py.
"""

import os
import sys
import wave
import struct

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

SAMPLE_RATE = 22050


def save_wav(filename, samples, sample_rate=SAMPLE_RATE):
    """Save samples to WAV file in the test output directory.

    Args:
        filename: WAV filename (saved under tests/output/)
        samples: List of int16 sample values
        sample_rate: Sample rate (default 22050)

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
        chunk = sp.synthesize(1024)
        if not chunk:
            break
        samples.extend(chunk[i] for i in range(len(chunk)))
    return samples
