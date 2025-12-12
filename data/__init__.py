# -*- coding: utf-8 -*-
"""
Phoneme data module for NV Speech Player.

This module provides the phoneme database split into logical categories.
Import `data` to get the complete merged dictionary.

Categories:
  - vowels_front
  - vowels_central
  - vowels_back
  - vowels_rcolored
  - vowels_nasalized
  - diphthongs
  - stops
  - fricatives
  - affricates
  - nasals
  - liquids_glides
  - special
"""

# Import all category modules
from .vowels_front import VOWELS_FRONT
from .vowels_central import VOWELS_CENTRAL
from .vowels_back import VOWELS_BACK
from .vowels_rcolored import VOWELS_RCOLORED
from .vowels_nasalized import VOWELS_NASALIZED
from .diphthongs import DIPHTHONGS
from .stops import STOPS
from .fricatives import FRICATIVES
from .affricates import AFFRICATES
from .nasals import NASALS
from .liquids_glides import LIQUIDS_GLIDES
from .special import SPECIAL

# Merge all dictionaries into one
data = {}
data.update(VOWELS_FRONT)
data.update(VOWELS_CENTRAL)
data.update(VOWELS_BACK)
data.update(VOWELS_RCOLORED)
data.update(VOWELS_NASALIZED)
data.update(DIPHTHONGS)
data.update(STOPS)
data.update(FRICATIVES)
data.update(AFFRICATES)
data.update(NASALS)
data.update(LIQUIDS_GLIDES)
data.update(SPECIAL)

# Apply automatic parameter calculations for new synthesis features
# This adds deltaF1, deltaB1, ftzFreq2, ftzBw2, sinusoidalVoicingAmplitude,
# aspirationFilterFreq, aspirationFilterBw based on Klatt acoustic formulas
from .calculations import update_all_phonemes
update_all_phonemes(data)

# Category mappings for organized menu display
PHONEME_CATEGORIES = {
    'Vowels - Front': VOWELS_FRONT,
    'Vowels - Central': VOWELS_CENTRAL,
    'Vowels - Back': VOWELS_BACK,
    'Vowels - R-colored': VOWELS_RCOLORED,
    'Vowels - Nasalized': VOWELS_NASALIZED,
    'Diphthongs': DIPHTHONGS,
    'Stops': STOPS,
    'Fricatives': FRICATIVES,
    'Affricates': AFFRICATES,
    'Nasals': NASALS,
    'Liquids & Glides': LIQUIDS_GLIDES,
    'Special': SPECIAL,
}

# Ordered list for menu display
CATEGORY_ORDER = [
    'Vowels - Front',
    'Vowels - Central',
    'Vowels - Back',
    'Vowels - R-colored',
    'Vowels - Nasalized',
    'Diphthongs',
    'Stops',
    'Fricatives',
    'Affricates',
    'Nasals',
    'Liquids & Glides',
    'Special',
]

# For backwards compatibility
__all__ = ["data", "PHONEME_CATEGORIES", "CATEGORY_ORDER"]
