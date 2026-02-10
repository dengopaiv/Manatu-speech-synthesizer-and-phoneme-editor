# -*- coding: utf-8 -*-
"""
Sync JSON editor presets from Python phoneme data.

Generates/updates JSON preset files in editor/presets/ from the
canonical phoneme data in data/*.py.

Usage:
    python tools/sync_presets.py              # Update all presets
    python tools/sync_presets.py --dry-run    # Show what would change
    python tools/sync_presets.py --diff       # Show parameter differences
"""

import sys
import os
import io
import json
import argparse

# Handle encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import data as phoneme_data, PHONEME_CATEGORIES

# Prosody params that shouldn't be stored in presets
PROSODY_PARAMS = {
    'voicePitch', 'midVoicePitch', 'endVoicePitch',
    'vibratoPitchOffset', 'vibratoSpeed',
    'preFormantGain', 'outputGain',
}

# Map from PHONEME_CATEGORIES keys to JSON category names
_CATEGORY_MAP = {
    'Vowels - Front': 'vowel',
    'Vowels - Central': 'vowel',
    'Vowels - Back': 'vowel',
    'Vowels - R-colored': 'vowel',
    'Vowels - Nasalized': 'vowel',
    'Diphthongs': 'diphthong',
    'Stops': 'stop',
    'Fricatives': 'fricative',
    'Affricates': 'affricate',
    'Nasals': 'nasal',
    'Liquids & Glides': 'liquid',
    'Special': 'special',
}

# Description overrides for known vowels (from IPA charts)
_VOWEL_DESCRIPTIONS = {
    'a': 'open front unrounded',
    'i': 'close front unrounded',
    'e': 'close-mid front unrounded',
    'ɛ': 'open-mid front unrounded',
    'æ': 'near-open front unrounded',
    'y': 'close front rounded',
    'ø': 'close-mid front rounded',
    'œ': 'open-mid front rounded',
    'ɶ': 'open front rounded',
    'ɨ': 'close central unrounded',
    'ʉ': 'close central rounded',
    'ɘ': 'close-mid central unrounded',
    'ɵ': 'close-mid central rounded',
    'ə': 'mid central (schwa)',
    'ɜ': 'open-mid central unrounded',
    'ɞ': 'open-mid central rounded',
    'ɐ': 'near-open central',
    'ɯ': 'close back unrounded',
    'u': 'close back rounded',
    'ɤ': 'close-mid back unrounded',
    'o': 'close-mid back rounded',
    'ʌ': 'open-mid back unrounded',
    'ɔ': 'open-mid back rounded',
    'ɑ': 'open back unrounded',
    'ɒ': 'open back rounded',
    'ɪ': 'near-close front unrounded',
    'ʏ': 'near-close front rounded',
    'ʊ': 'near-close back rounded',
    'ɚ': 'r-colored schwa',
    'ɝ': 'r-colored open-mid central',
}


def _ipa_to_filename(ipa_str, category):
    """Convert IPA string to preset filename.

    Format: {CODEPOINT}_{category}.json
    Multi-character IPA uses underscore-separated codepoints.
    """
    codepoints = '_'.join(f'{ord(c):04X}' for c in ipa_str)
    return f"{codepoints}_{category}.json"


def _detect_category(ipa_char):
    """Detect category for a phoneme by checking PHONEME_CATEGORIES."""
    for cat_name, cat_dict in PHONEME_CATEGORIES.items():
        if ipa_char in cat_dict:
            return _CATEGORY_MAP.get(cat_name, 'special')
    return 'special'


def _filter_params(params):
    """Filter out internal flags and prosody params."""
    return {k: float(v) if isinstance(v, (int, float)) else v
            for k, v in params.items()
            if not k.startswith('_') and k not in PROSODY_PARAMS}


def _build_preset(ipa_char, params):
    """Build a JSON preset dict from phoneme data."""
    category = _detect_category(ipa_char)
    description = _VOWEL_DESCRIPTIONS.get(ipa_char, '')

    return {
        'ipa': ipa_char,
        'name': ipa_char,
        'category': category,
        'description': description,
        'isVowel': bool(params.get('_isVowel', False)),
        'isVoiced': bool(params.get('_isVoiced', False)),
        'parameters': _filter_params(params),
    }


def sync_presets(presets_dir, dry_run=False, show_diff=False):
    """Sync all phoneme data to JSON presets.

    Args:
        presets_dir: Path to editor/presets/ directory
        dry_run: If True, don't write files
        show_diff: If True, show parameter differences

    Returns:
        (created, updated, unchanged) counts
    """
    os.makedirs(presets_dir, exist_ok=True)

    created = 0
    updated = 0
    unchanged = 0

    for ipa_char, params in sorted(phoneme_data.items()):
        category = _detect_category(ipa_char)
        filename = _ipa_to_filename(ipa_char, category)
        filepath = os.path.join(presets_dir, filename)

        new_preset = _build_preset(ipa_char, params)
        new_json = json.dumps(new_preset, indent=2, ensure_ascii=False) + '\n'

        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_content = f.read()

            if existing_content.strip() == new_json.strip():
                unchanged += 1
                continue

            if show_diff:
                try:
                    existing = json.loads(existing_content)
                    _print_diff(ipa_char, existing.get('parameters', {}),
                                new_preset['parameters'])
                except json.JSONDecodeError:
                    print(f"  /{ipa_char}/: existing JSON is malformed")

            if dry_run:
                print(f"  Would update: {filename} (/{ipa_char}/)")
                updated += 1
                continue

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_json)
            print(f"  Updated: {filename} (/{ipa_char}/)")
            updated += 1
        else:
            if dry_run:
                print(f"  Would create: {filename} (/{ipa_char}/)")
                created += 1
                continue

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_json)
            print(f"  Created: {filename} (/{ipa_char}/)")
            created += 1

    return created, updated, unchanged


def _print_diff(ipa_char, old_params, new_params):
    """Print parameter differences between existing and new presets."""
    all_keys = sorted(set(old_params) | set(new_params))
    diffs = []
    for key in all_keys:
        old_val = old_params.get(key)
        new_val = new_params.get(key)
        if old_val != new_val:
            diffs.append(f"    {key}: {old_val} -> {new_val}")

    if diffs:
        print(f"  /{ipa_char}/ differences:")
        for d in diffs:
            print(d)


def main():
    parser = argparse.ArgumentParser(
        description='Sync JSON editor presets from Python phoneme data')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print what would change without writing files')
    parser.add_argument('--diff', action='store_true',
                        help='Show parameter differences between current JSON and Python data')
    args = parser.parse_args()

    presets_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'editor', 'presets')

    print(f"Syncing presets to: {presets_dir}")
    if args.dry_run:
        print("(dry run - no files will be written)")
    print()

    created, updated, unchanged = sync_presets(
        presets_dir, dry_run=args.dry_run, show_diff=args.diff)

    print(f"\nSummary: {created} created, {updated} updated, {unchanged} unchanged")
    print(f"Total phonemes in data: {len(phoneme_data)}")


if __name__ == '__main__':
    main()
