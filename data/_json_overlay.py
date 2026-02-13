# -*- coding: utf-8 -*-
"""
JSON preset overlay for phoneme data.

When NVSPEECHPLAYER_USE_JSON_PRESETS=1 is set, this module loads
JSON presets from editor/presets/ and overlays them onto the
Python phoneme data dict. This allows the phoneme editor to
feed parameters back into the synthesizer without modifying
Python source files.

The NVDA addon never sets this env var, so it is unaffected.
"""

import os
import json
import glob


# Metadata keys in JSON that map to internal flags
_FLAG_MAP = {
    'isVowel': '_isVowel',
    'isVoiced': '_isVoiced',
}


def load_json_presets_overlay(presets_dir):
    """Load JSON presets and return a dict mapping IPA -> params.

    Args:
        presets_dir: Path to directory containing *.json preset files.

    Returns:
        Dict of {ipa_str: {param_key: value, ...}} with internal flags
        restored from JSON metadata fields.
    """
    result = {}

    for filepath in glob.glob(os.path.join(presets_dir, '*.json')):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                preset = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        ipa = preset.get('ipa')
        if not ipa:
            continue

        params = dict(preset.get('parameters', {}))

        # Restore internal flags from JSON metadata
        for json_key, internal_key in _FLAG_MAP.items():
            if json_key in preset:
                params[internal_key] = preset[json_key]

        # Restore category-based flags
        category = preset.get('category', '')
        if category == 'nasal':
            params['_isNasal'] = True
        if category == 'stop':
            params['_isStop'] = True
        if category == 'liquid':
            params['_isLiquid'] = True

        result[ipa] = params

    return result
