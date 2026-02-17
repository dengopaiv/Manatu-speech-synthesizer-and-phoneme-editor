# Phoneme Parameter Files

This directory contains phoneme data definitions for Manatu.

## Voice Quality Parameters

Modern synthesis uses the **LF (Liljencrants-Fant) model** for voice quality control.

### lfRd Parameter

The `lfRd` parameter controls voice quality (glottal pulse shape):

| Value | Voice Quality | Use Case |
|-------|---------------|----------|
| 0 | No voicing | Voiceless consonants only |
| 1.0 | Modal voice | Voiced consonants (natural, balanced) |
| 1.0–1.7 | Modal to slightly breathy | Vowels (height-proportional: close=1.0, open-mid=1.7) |

Valid range: 0.3 to 2.7 (0 = no voicing)

### Other Voice Quality Parameters

- `spectralTilt`: Controls high-frequency rolloff (0-41 dB, typical 0-20)
- `flutter`: F0 jitter for natural voice variation (0.10-0.25)
- `diplophonia`: Irregular voicing for creaky quality (0-0.4)

## File Organization

| File | Contents |
|------|----------|
| `vowels_front.py` | Front vowels (i, e, a, etc.) |
| `vowels_back.py` | Back vowels (u, o, etc.) |
| `vowels_central.py` | Central vowels (schwa, etc.) |
| `vowels_nasalized.py` | Nasalized vowels |
| `vowels_rcolored.py` | R-colored vowels |
| `stops.py` | Stop consonants (p, b, t, d, k, g) |
| `fricatives.py` | Fricative consonants (f, v, s, z, etc.) |
| `nasals.py` | Nasal consonants (m, n, ng) |
| `liquids_glides.py` | Liquids and glides (l, r, w, j) |
| `affricates.py` | Affricate consonants (ch, j) |
| `special.py` | Special/uncategorized phonemes |

## Deprecated Parameters

The following parameters are **deprecated** and no longer used by the synthesizer:

- `glottalOpenQuotient` - Replaced by `lfRd`
- `openQuotientShape` - Replaced by `lfRd`
- `speedQuotient` - Replaced by `lfRd`

These legacy parameters have been removed from all phoneme files.
The modern LF model (`lfRd`) provides superior voice quality control.

## References

- Fant, G. (1995). "The LF-model revisited. Transformations and frequency domain analysis." STL-QPSR 36(2-3).
- Stevens, K.N. (1998). "Acoustic Phonetics." MIT Press.
- Klatt, D.H. (1980). "Software for a cascade/parallel formant synthesizer." JASA 67(3).
