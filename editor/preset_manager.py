"""Preset management for the phoneme editor."""

import json
from pathlib import Path


class PresetManager:
    """Manages loading and saving of phoneme presets."""

    def __init__(self, presets_dir='presets'):
        self.presets_dir = Path(presets_dir)
        self.presets_dir.mkdir(exist_ok=True)

    def get_filename(self, ipa_char, category):
        codepoint = f"{ord(ipa_char):04X}" if len(ipa_char) == 1 else "custom"
        return f"{codepoint}_{category}.json"

    def save_preset(self, preset_data):
        ipa = preset_data.get('ipa', 'x')
        category = preset_data.get('category', 'custom')
        filename = self.get_filename(ipa, category)
        filepath = self.presets_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(preset_data, f, indent=2, ensure_ascii=False)
        return filepath

    def load_preset(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_presets(self):
        presets = {}
        for filepath in self.presets_dir.glob('*.json'):
            try:
                data = self.load_preset(filepath)
                category = data.get('category', 'custom')
                if category not in presets:
                    presets[category] = []
                presets[category].append({
                    'filepath': filepath,
                    'ipa': data.get('ipa', '?'),
                    'name': data.get('name', filepath.stem),
                    'description': data.get('description', '')
                })
            except Exception:
                pass
        return presets

    def find_preset_by_ipa(self, ipa_char):
        for filepath in self.presets_dir.glob('*.json'):
            try:
                data = self.load_preset(filepath)
                if data.get('ipa') == ipa_char:
                    params = dict(data.get('parameters', {}))
                    params['_isVowel'] = data.get('isVowel', False)
                    params['_isVoiced'] = data.get('isVoiced', False)
                    params['_isStop'] = (data.get('category') == 'stop')
                    params['_isNasal'] = (data.get('category') == 'nasal')
                    return params
            except Exception:
                pass
        return None

    def export_to_data_py(self, preset_data):
        ipa = preset_data.get('ipa', 'x')
        params = preset_data.get('parameters', {})
        lines = [f"    u'{ipa}':{{"]
        if preset_data.get('isVowel'):
            lines.append("        '_isVowel':True,")
        if preset_data.get('isVoiced'):
            lines.append("        '_isVoiced':True,")
        for name, value in params.items():
            if not name.startswith('_'):
                lines.append(f"        '{name}':{value},")
        lines.append("    },")
        return '\n'.join(lines)
