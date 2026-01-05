"""
Voice profile definitions for male/female/child synthesis.

These profiles control pitch (F0), formant scaling, and voice quality
to simulate different voice types. Values are based on acoustic phonetics
research (Peterson & Barney 1952, Hillenbrand et al. 1995).

Formant scaling factors are derived from vocal tract length differences:
- Adult male: ~17.5 cm (reference)
- Adult female: ~14.5 cm (~17% shorter, formants ~17% higher)
- Child (5-10yr): ~12 cm (~30-40% shorter, formants ~35% higher)
"""

VOICE_PROFILES = {
    'male': {
        'name': 'Adult Male',
        'basePitch': 110,          # Hz - typical male F0
        'formantScale': 1.0,       # Reference scale
        'spectralTilt': 0,         # Modal voice (no tilt)
        'voiceTurbulence': 0.0,    # No added breathiness
        'flutter': 0.25,           # Natural jitter
        'description': 'Adult male voice with low pitch and full formants'
    },
    'female': {
        'name': 'Adult Female',
        'basePitch': 200,          # Hz - typical female F0
        'formantScale': 1.17,      # ~17% higher formants
        'spectralTilt': 4,         # Slight breathiness typical of female voice
        'voiceTurbulence': 0.05,   # Slight aspiration
        'flutter': 0.20,           # Slightly less jitter
        'description': 'Adult female voice with higher pitch and scaled formants'
    },
    'child': {
        'name': 'Child',
        'basePitch': 270,          # Hz - child F0
        'formantScale': 1.35,      # ~35% higher formants
        'spectralTilt': 2,         # Minimal breathiness
        'voiceTurbulence': 0.0,    # Children typically not breathy
        'flutter': 0.30,           # Slightly more pitch variation
        'description': 'Child voice with high pitch and compressed vocal tract'
    },
    'custom': {
        'name': 'Custom',
        'basePitch': None,         # Use current slider value
        'formantScale': None,      # Use current slider value
        'spectralTilt': None,      # Use current slider value
        'voiceTurbulence': None,
        'flutter': None,
        'description': 'Custom settings from individual controls'
    }
}


def get_profile(name):
    """Get a voice profile by name (case-insensitive)."""
    key = name.lower().replace(' ', '_').replace('adult_', '')
    return VOICE_PROFILES.get(key, VOICE_PROFILES['male'])


def get_profile_names():
    """Get list of available profile names for UI."""
    return [p['name'] for p in VOICE_PROFILES.values() if p['name'] != 'Custom'] + ['Custom']
