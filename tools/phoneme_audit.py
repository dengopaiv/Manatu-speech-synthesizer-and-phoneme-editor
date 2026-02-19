# -*- coding: utf-8 -*-
"""
Phoneme parameter consistency audit.

Scans all phoneme data and reports consistency issues by phoneme class.
Checks spectralTilt, lfRd, and voicing patterns against expected ranges.

Usage:
    python tools/phoneme_audit.py
"""

import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import data as phoneme_data

# Expected patterns by class
RULES = [
    {
        'name': 'Voiced fricatives: spectralTilt should be <= 5',
        'filter': lambda k, v: v.get('_isVoiced') and not v.get('_isVowel') and not v.get('_isNasal') and not v.get('_isStop') and not v.get('_isLiquid') and v.get('fricationAmplitude', 0) > 0 or (v.get('_isVoiced') and v.get('aspirationAmplitude', 0) > 0 and not v.get('_isVowel') and not v.get('_isNasal') and not v.get('_isStop')),
        'check': lambda k, v: v.get('spectralTilt', 0) <= 5,
        'detail': lambda k, v: f"spectralTilt={v.get('spectralTilt', 0)}",
        'severity': 'CRITICAL',
        'exclude': ['ɦ', 'ɮ'],  # Glottal/lateral fricatives are intentionally different
    },
    {
        'name': 'Open-mid vowels: lfRd should be 1.3-1.7',
        'filter': lambda k, v: v.get('_isVowel') and v.get('lfRd', 0) >= 2.0,
        'check': lambda k, v: v.get('lfRd', 0) <= 1.7,
        'detail': lambda k, v: f"lfRd={v.get('lfRd', 0)}",
        'severity': 'WARNING',
    },
    {
        'name': 'Open/open-mid vowels: spectralTilt should be <= 2',
        'filter': lambda k, v: v.get('_isVowel') and v.get('spectralTilt', 0) == 3,
        'check': lambda k, v: v.get('spectralTilt', 0) <= 2,
        'detail': lambda k, v: f"spectralTilt={v.get('spectralTilt', 0)}, lfRd={v.get('lfRd', 0)}",
        'severity': 'WARNING',
    },
    {
        'name': 'Close vowels: lfRd should be 1.0, spectralTilt 0',
        'filter': lambda k, v: v.get('_isVowel') and v.get('lfRd', 0) == 1.0,
        'check': lambda k, v: v.get('spectralTilt', 0) == 0,
        'detail': lambda k, v: f"lfRd={v.get('lfRd', 0)}, spectralTilt={v.get('spectralTilt', 0)}",
        'severity': 'INFO',
    },
    {
        'name': 'Nasals: spectralTilt=4, lfRd=1.0',
        'filter': lambda k, v: v.get('_isNasal'),
        'check': lambda k, v: v.get('spectralTilt', 0) == 4 and v.get('lfRd', 0) == 1.0,
        'detail': lambda k, v: f"spectralTilt={v.get('spectralTilt', 0)}, lfRd={v.get('lfRd', 0)}",
        'severity': 'INFO',
    },
    {
        'name': 'Voiceless fricatives: lfRd should be 0',
        'filter': lambda k, v: not v.get('_isVoiced') and not v.get('_isVowel') and not v.get('_isNasal') and not v.get('_isStop') and (v.get('fricationAmplitude', 0) > 0 or v.get('aspirationAmplitude', 0) > 0),
        'check': lambda k, v: v.get('lfRd', 0) == 0,
        'detail': lambda k, v: f"lfRd={v.get('lfRd', 0)}",
        'severity': 'WARNING',
    },
]


def run_audit():
    counts = {'CRITICAL': 0, 'WARNING': 0, 'INFO': 0}
    total_issues = 0

    for rule in RULES:
        issues = []
        for k, v in sorted(phoneme_data.items()):
            if not isinstance(v, dict):
                continue
            exclude = rule.get('exclude', [])
            if k in exclude:
                continue
            if rule['filter'](k, v):
                if not rule['check'](k, v):
                    issues.append((k, rule['detail'](k, v)))

        severity = rule['severity']
        if issues:
            counts[severity] += len(issues)
            total_issues += len(issues)
            print(f"\n[{severity}] {rule['name']}")
            for ipa, detail in issues:
                print(f"  /{ipa}/: {detail}")
        else:
            print(f"\n[OK] {rule['name']}")

    # Summary by class
    print("\n" + "=" * 60)
    print("Phoneme Class Summary")
    print("=" * 60)

    classes = {
        'Voiced fricatives': [],
        'Voiceless fricatives': [],
        'Open vowels (lfRd > 1.5)': [],
        'Close vowels (lfRd <= 1.3)': [],
        'Close-mid vowels (lfRd = 1.7)': [],
        'Nasals': [],
        'Liquids/Glides': [],
        'Stops': [],
    }

    for k, v in sorted(phoneme_data.items()):
        if not isinstance(v, dict):
            continue
        if v.get('_isVowel'):
            lfRd = v.get('lfRd', 0)
            if lfRd <= 1.3:
                classes['Close vowels (lfRd <= 1.3)'].append((k, v))
            elif lfRd == 1.7:
                classes['Close-mid vowels (lfRd = 1.7)'].append((k, v))
            else:
                classes['Open vowels (lfRd > 1.5)'].append((k, v))
        elif v.get('_isNasal'):
            classes['Nasals'].append((k, v))
        elif v.get('_isStop'):
            classes['Stops'].append((k, v))
        elif v.get('_isLiquid'):
            classes['Liquids/Glides'].append((k, v))
        elif v.get('_isVoiced') and (v.get('fricationAmplitude', 0) > 0 or v.get('aspirationAmplitude', 0) > 0):
            classes['Voiced fricatives'].append((k, v))
        elif not v.get('_isVoiced') and (v.get('fricationAmplitude', 0) > 0 or v.get('aspirationAmplitude', 0) > 0):
            classes['Voiceless fricatives'].append((k, v))

    for cls_name, members in classes.items():
        if not members:
            continue
        tilts = [v.get('spectralTilt', 0) for _, v in members]
        lfrds = [v.get('lfRd', 0) for _, v in members]
        print(f"\n{cls_name} ({len(members)} phonemes):")
        print(f"  Phonemes: {', '.join(k for k, _ in members)}")
        print(f"  spectralTilt: min={min(tilts)}, max={max(tilts)}, values={sorted(set(tilts))}")
        print(f"  lfRd: min={min(lfrds):.1f}, max={max(lfrds):.1f}, values={sorted(set(lfrds))}")

    print(f"\n{'=' * 60}")
    print(f"Issues: {counts['CRITICAL']} critical, {counts['WARNING']} warning, {counts['INFO']} info")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    print("=" * 60)
    print("Phoneme Parameter Consistency Audit")
    print("=" * 60)
    run_audit()
