#!/usr/bin/env python3
"""
Phoneme Parameter Editor - Comprehensive Klatt Synthesis Parameter GUI

Exposes ALL 47 Klatt synthesis parameters with real-time preview and preset saving.
Designed for creating and testing phoneme definitions for NVSpeechPlayer.

Author: Based on NVSpeechPlayer by NV Access Limited
License: GPL v2
"""

import wx
import wx.lib.scrolledpanel as scrolled
import wx.lib.newevent
import threading
import wave
import struct
import tempfile
import os
import json
import time
from pathlib import Path

# Import synthesis modules
import speechPlayer
import ipa_keyboard

# Load phoneme data from modular data package
from data import data as PHONEME_DATA

# Schwa (ə) defaults for reset - the neutral mid-central vowel
SCHWA_DEFAULTS = PHONEME_DATA.get('ə', {})

# For audio playback
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

# Custom events
StatusUpdateEvent, EVT_STATUS_UPDATE = wx.lib.newevent.NewEvent()
PlayDoneEvent, EVT_PLAY_DONE = wx.lib.newevent.NewEvent()

# Parameter definitions with ranges and descriptions
PARAM_GROUPS = {
    'Pitch & Voicing': [
        ('voicePitch', 25, 300, 100, 'Hz', 'Fundamental frequency'),
        ('endVoicePitch', 25, 300, 100, 'Hz', 'End pitch (for contours)'),
        ('vibratoPitchOffset', 0, 100, 12, '%', 'Vibrato depth (0-100%)'),
        ('vibratoSpeed', 0, 100, 55, 'x0.1Hz', 'Vibrato rate'),
        ('glottalOpenQuotient', 0, 100, 10, '%', 'Glottis open time'),
    ],
    'Amplitudes': [
        ('voiceAmplitude', 0, 100, 100, '%', 'Voiced sound level'),
        ('voiceTurbulenceAmplitude', 0, 100, 0, '%', 'Breathiness'),
        ('aspirationAmplitude', 0, 100, 0, '%', 'Aspiration noise'),
        ('fricationAmplitude', 0, 100, 0, '%', 'Frication noise'),
        ('preFormantGain', 0, 200, 100, '%', 'Pre-resonator gain'),
        ('outputGain', 0, 200, 100, '%', 'Master volume'),
    ],
    'Cascade Formants (F1-F3)': [
        ('cf1', 100, 1000, 500, 'Hz', 'F1 frequency'),
        ('cb1', 30, 300, 60, 'Hz', 'F1 bandwidth'),
        ('cf2', 500, 2500, 1500, 'Hz', 'F2 frequency'),
        ('cb2', 50, 300, 90, 'Hz', 'F2 bandwidth'),
        ('cf3', 1500, 3500, 2500, 'Hz', 'F3 frequency'),
        ('cb3', 50, 400, 150, 'Hz', 'F3 bandwidth'),
    ],
    'Cascade Formants (F4-F6)': [
        ('cf4', 2500, 4500, 3500, 'Hz', 'F4 frequency'),
        ('cb4', 100, 500, 200, 'Hz', 'F4 bandwidth'),
        ('cf5', 3500, 5000, 4500, 'Hz', 'F5 frequency'),
        ('cb5', 100, 500, 200, 'Hz', 'F5 bandwidth'),
        ('cf6', 4000, 6000, 5000, 'Hz', 'F6 frequency'),
        ('cb6', 100, 1500, 500, 'Hz', 'F6 bandwidth'),
    ],
    'Nasal Formants': [
        ('cfN0', 100, 500, 250, 'Hz', 'Nasal zero frequency'),
        ('cbN0', 50, 200, 100, 'Hz', 'Nasal zero bandwidth'),
        ('cfNP', 100, 500, 250, 'Hz', 'Nasal pole frequency'),
        ('cbNP', 50, 200, 100, 'Hz', 'Nasal pole bandwidth'),
        ('caNP', 0, 100, 0, '%', 'Nasal coupling'),
    ],
    'Parallel Formants (F1-F3)': [
        ('pf1', 100, 1000, 500, 'Hz', 'Parallel F1 freq'),
        ('pb1', 30, 300, 60, 'Hz', 'Parallel F1 BW'),
        ('pa1', 0, 100, 0, '%', 'Parallel F1 amp'),
        ('pf2', 500, 2500, 1500, 'Hz', 'Parallel F2 freq'),
        ('pb2', 50, 300, 90, 'Hz', 'Parallel F2 BW'),
        ('pa2', 0, 100, 0, '%', 'Parallel F2 amp'),
        ('pf3', 1500, 3500, 2500, 'Hz', 'Parallel F3 freq'),
        ('pb3', 50, 400, 150, 'Hz', 'Parallel F3 BW'),
        ('pa3', 0, 100, 0, '%', 'Parallel F3 amp'),
    ],
    'Parallel Formants (F4-F6)': [
        ('pf4', 2500, 4500, 3500, 'Hz', 'Parallel F4 freq'),
        ('pb4', 100, 500, 200, 'Hz', 'Parallel F4 BW'),
        ('pa4', 0, 100, 0, '%', 'Parallel F4 amp'),
        ('pf5', 3500, 5000, 4500, 'Hz', 'Parallel F5 freq'),
        ('pb5', 100, 500, 200, 'Hz', 'Parallel F5 BW'),
        ('pa5', 0, 100, 0, '%', 'Parallel F5 amp'),
        ('pf6', 4000, 6000, 5000, 'Hz', 'Parallel F6 freq'),
        ('pb6', 100, 1500, 500, 'Hz', 'Parallel F6 BW'),
        ('pa6', 0, 100, 0, '%', 'Parallel F6 amp'),
    ],
    'Parallel Bypass': [
        ('parallelBypass', 0, 105, 0, '%', 'Unfiltered noise bypass'),
    ],
}

# Parameters that use percentage scaling (0-100 maps to 0.0-1.0)
PERCENT_PARAMS = {
    'voiceAmplitude', 'voiceTurbulenceAmplitude', 'aspirationAmplitude',
    'fricationAmplitude', 'caNP', 'pa1', 'pa2', 'pa3', 'pa4', 'pa5', 'pa6',
    'glottalOpenQuotient', 'vibratoPitchOffset'
}

# Parameters that use percentage scaling (0-200 maps to 0.0-2.0)
GAIN_PARAMS = {'preFormantGain', 'outputGain'}

# Parameters that need /10 scaling
TENTH_PARAMS = {'vibratoSpeed', 'parallelBypass'}

# IPA descriptions from the International Phonetic Alphabet chart
IPA_DESCRIPTIONS = {
    # Vowels - Close
    'i': 'close front unrounded',
    'y': 'close front rounded',
    'ɨ': 'close central unrounded',
    'ʉ': 'close central rounded',
    'ɯ': 'close back unrounded',
    'u': 'close back rounded',
    # Vowels - Near-close
    'ɪ': 'near-close front unrounded',
    'ʏ': 'near-close front rounded',
    'ʊ': 'near-close back rounded',
    # Vowels - Close-mid
    'e': 'close-mid front unrounded',
    'ø': 'close-mid front rounded',
    'ɘ': 'close-mid central unrounded',
    'ɵ': 'close-mid central rounded',
    'ɤ': 'close-mid back unrounded',
    'o': 'close-mid back rounded',
    # Vowels - Mid
    'ə': 'mid central (schwa)',
    # Vowels - Open-mid
    'ɛ': 'open-mid front unrounded',
    'œ': 'open-mid front rounded',
    'ɜ': 'open-mid central unrounded',
    'ɞ': 'open-mid central rounded',
    'ʌ': 'open-mid back unrounded',
    'ɔ': 'open-mid back rounded',
    # Vowels - Near-open
    'æ': 'near-open front unrounded',
    'ɐ': 'near-open central',
    # Vowels - Open
    'a': 'open front unrounded',
    'ɶ': 'open front rounded',
    'ä': 'open central unrounded',
    'ɑ': 'open back unrounded',
    'ɒ': 'open back rounded',
    # R-colored vowels
    'ɝ': 'r-colored mid central',
    'ɚ': 'r-colored schwa',
    # Nasalized vowels
    'ã': 'nasalized open front',
    'ɛ̃': 'nasalized open-mid front',
    'ɔ̃': 'nasalized open-mid back rounded',
    'œ̃': 'nasalized open-mid front rounded',
    # Consonants - Plosives
    'p': 'voiceless bilabial plosive',
    'b': 'voiced bilabial plosive',
    't': 'voiceless alveolar plosive',
    'd': 'voiced alveolar plosive',
    'ʈ': 'voiceless retroflex plosive',
    'ɖ': 'voiced retroflex plosive',
    'c': 'voiceless palatal plosive',
    'ɟ': 'voiced palatal plosive',
    'k': 'voiceless velar plosive',
    'g': 'voiced velar plosive',
    'q': 'voiceless uvular plosive',
    'ɢ': 'voiced uvular plosive',
    'ʔ': 'glottal stop',
    # Consonants - Nasals
    'm': 'bilabial nasal',
    'ɱ': 'labiodental nasal',
    'n': 'alveolar nasal',
    'ɳ': 'retroflex nasal',
    'ɲ': 'palatal nasal',
    'ŋ': 'velar nasal',
    'ɴ': 'uvular nasal',
    # Consonants - Trills
    'ʙ': 'bilabial trill',
    'r': 'alveolar trill',
    'ʀ': 'uvular trill',
    # Consonants - Taps/Flaps
    'ⱱ': 'labiodental flap',
    'ɾ': 'alveolar tap',
    'ɽ': 'retroflex flap',
    # Consonants - Fricatives
    'ɸ': 'voiceless bilabial fricative',
    'β': 'voiced bilabial fricative',
    'f': 'voiceless labiodental fricative',
    'v': 'voiced labiodental fricative',
    'θ': 'voiceless dental fricative',
    'ð': 'voiced dental fricative',
    's': 'voiceless alveolar fricative',
    'z': 'voiced alveolar fricative',
    'ʃ': 'voiceless postalveolar fricative',
    'ʒ': 'voiced postalveolar fricative',
    'ʂ': 'voiceless retroflex fricative',
    'ʐ': 'voiced retroflex fricative',
    'ç': 'voiceless palatal fricative',
    'ʝ': 'voiced palatal fricative',
    'x': 'voiceless velar fricative',
    'ɣ': 'voiced velar fricative',
    'χ': 'voiceless uvular fricative',
    'ʁ': 'voiced uvular fricative',
    'ħ': 'voiceless pharyngeal fricative',
    'ʕ': 'voiced pharyngeal fricative',
    'h': 'voiceless glottal fricative',
    'ɦ': 'voiced glottal fricative',
    # Consonants - Lateral fricatives
    'ɬ': 'voiceless alveolar lateral fricative',
    'ɮ': 'voiced alveolar lateral fricative',
    # Consonants - Approximants
    'ʋ': 'labiodental approximant',
    'ɹ': 'alveolar approximant',
    'ɻ': 'retroflex approximant',
    'j': 'palatal approximant',
    'ɰ': 'velar approximant',
    'w': 'labial-velar approximant',
    # Consonants - Lateral approximants
    'l': 'alveolar lateral approximant',
    'ɭ': 'retroflex lateral approximant',
    'ʎ': 'palatal lateral approximant',
    'ʟ': 'velar lateral approximant',
    # Additional common symbols
    'I': 'near-close front unrounded (alt)',
    'E': 'open-mid front unrounded (alt)',
    'O': 'open-mid back rounded (alt)',
    'U': 'near-close back rounded (alt)',
}

# Duration defaults for test sequences (milliseconds)
SEQUENCE_DURATIONS = {
    'vowel': 250,
    'consonant': 100,
    'default': 150,
}


class PresetManager:
    """Manages loading and saving of phoneme presets."""

    def __init__(self, presets_dir='presets'):
        self.presets_dir = Path(presets_dir)
        self.presets_dir.mkdir(exist_ok=True)

    def get_filename(self, ipa_char, category):
        """Generate filename from IPA character."""
        codepoint = f"{ord(ipa_char):04X}" if len(ipa_char) == 1 else "custom"
        return f"{codepoint}_{category}.json"

    def save_preset(self, preset_data):
        """Save a preset to JSON file."""
        ipa = preset_data.get('ipa', 'x')
        category = preset_data.get('category', 'custom')
        filename = self.get_filename(ipa, category)
        filepath = self.presets_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(preset_data, f, indent=2, ensure_ascii=False)

        return filepath

    def load_preset(self, filepath):
        """Load a preset from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_presets(self):
        """List all presets grouped by category."""
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

    def export_to_data_py(self, preset_data):
        """Generate Python dict string for phoneme data format."""
        ipa = preset_data.get('ipa', 'x')
        params = preset_data.get('parameters', {})

        lines = [f"    u'{ipa}':{{"]

        # Add metadata
        if preset_data.get('isVowel'):
            lines.append("        '_isVowel':True,")
        if preset_data.get('isVoiced'):
            lines.append("        '_isVoiced':True,")

        # Add parameters
        for name, value in params.items():
            if name.startswith('_'):
                continue
            lines.append(f"        '{name}':{value},")

        lines.append("    },")
        return '\n'.join(lines)


class PhonemeEditorFrame(wx.Frame):
    """Main application frame for the phoneme parameter editor."""

    def __init__(self):
        super().__init__(
            parent=None,
            title="Phoneme Parameter Editor",
            size=(900, 700)
        )

        self.sample_rate = 22050
        self.is_playing = False
        self.play_thread = None
        self.preset_manager = PresetManager()

        # Parameter sliders dictionary
        self.sliders = {}
        self.value_labels = {}

        # Current preset metadata
        self.current_ipa = ''
        self.current_category = 'vowel'
        self.current_description = ''

        # IPA keyboard state for cycling through symbols
        self._last_ipa_key = None
        self._last_ipa_time = 0
        self._ipa_press_count = 0
        self._cycle_timeout = 0.5  # 500ms timeout for cycling

        self._create_menu_bar()
        self._create_widgets()
        self._bind_events()

        self.Centre()
        self.set_status("Ready. Adjust parameters and click Play to preview.")

    def _create_menu_bar(self):
        """Create menu bar."""
        menu_bar = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()
        new_item = file_menu.Append(wx.ID_NEW, "&New Preset\tCtrl+N", "Reset to defaults")
        open_item = file_menu.Append(wx.ID_OPEN, "&Open Preset\tCtrl+O", "Load preset from file")
        save_item = file_menu.Append(wx.ID_SAVE, "&Save Preset\tCtrl+S", "Save current preset")
        file_menu.AppendSeparator()
        export_item = file_menu.Append(wx.ID_ANY, "&Export as Python dict\tCtrl+E", "Copy as Python dict")
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, "E&xit\tAlt+F4", "Exit")
        menu_bar.Append(file_menu, "&File")

        # Presets menu - populated from phoneme data
        presets_menu = wx.Menu()
        self._populate_presets_menu(presets_menu)
        menu_bar.Append(presets_menu, "P&resets")

        # Help menu
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "&About", "About this application")
        menu_bar.Append(help_menu, "&Help")

        self.SetMenuBar(menu_bar)

        # Bind events
        self.Bind(wx.EVT_MENU, self.on_new, new_item)
        self.Bind(wx.EVT_MENU, self.on_open, open_item)
        self.Bind(wx.EVT_MENU, self.on_save, save_item)
        self.Bind(wx.EVT_MENU, self.on_export, export_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

    def _populate_presets_menu(self, presets_menu):
        """Populate presets menu from phoneme data."""
        # Get the phoneme data dict
        phoneme_data = PHONEME_DATA

        # Categorize phonemes
        categories = {
            'Vowels': [],
            'Stops': [],
            'Fricatives': [],
            'Nasals': [],
            'Liquids': [],
            'Other': []
        }

        for ipa, params in phoneme_data.items():
            if not isinstance(params, dict):
                continue

            if params.get('_isVowel'):
                categories['Vowels'].append((ipa, params))
            elif params.get('_isStop'):
                categories['Stops'].append((ipa, params))
            elif params.get('_isNasal'):
                categories['Nasals'].append((ipa, params))
            elif params.get('_isLiquid'):
                categories['Liquids'].append((ipa, params))
            elif params.get('fricationAmplitude', 0) > 0.5:
                categories['Fricatives'].append((ipa, params))
            else:
                categories['Other'].append((ipa, params))

        # Create submenus
        for category, phonemes in categories.items():
            if not phonemes:
                continue

            submenu = wx.Menu()
            # Sort phonemes alphabetically
            for ipa, params in sorted(phonemes, key=lambda x: x[0]):
                # Add IPA description if available
                desc = IPA_DESCRIPTIONS.get(ipa, '')
                label = f"{ipa} - {desc}" if desc else ipa
                item = submenu.Append(wx.ID_ANY, label, f"Load {ipa}: {desc}" if desc else f"Load {ipa}")
                # Bind with closure to capture ipa and params
                self.Bind(wx.EVT_MENU,
                         lambda evt, i=ipa, p=params: self._load_phoneme(i, p),
                         item)

            presets_menu.AppendSubMenu(submenu, f"&{category}")

    def _load_phoneme(self, ipa, params):
        """Load a phoneme's parameters into the editor."""
        # Set metadata
        self.ipa_input.SetValue(ipa)
        self.is_vowel_cb.SetValue(params.get('_isVowel', False))
        self.is_voiced_cb.SetValue(params.get('_isVoiced', False))

        # Set IPA description from IPA_DESCRIPTIONS dictionary
        desc = IPA_DESCRIPTIONS.get(ipa, '')
        self.desc_input.SetValue(desc)

        # Determine category
        if params.get('_isVowel'):
            cat = 'vowel'
        elif params.get('_isStop'):
            cat = 'stop'
        elif params.get('_isNasal'):
            cat = 'nasal'
        elif params.get('_isLiquid'):
            cat = 'approximant'
        else:
            cat = 'fricative'

        idx = self.category_choice.FindString(cat)
        if idx != wx.NOT_FOUND:
            self.category_choice.SetSelection(idx)

        # Set parameters (filter out metadata keys starting with _)
        clean_params = {k: v for k, v in params.items() if not k.startswith('_')}
        self.set_frame_params(clean_params)

        # Status message with description
        desc = IPA_DESCRIPTIONS.get(ipa, '')
        if desc:
            self.set_status(f"Loaded: {ipa} - {desc}")
        else:
            self.set_status(f"Loaded: {ipa}")

    def _create_widgets(self):
        """Create all UI widgets."""
        main_panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left panel: Controls and play
        left_panel = wx.Panel(main_panel)
        left_sizer = wx.BoxSizer(wx.VERTICAL)

        # Metadata section
        meta_box = wx.StaticBox(left_panel, label="Preset Info")
        meta_sizer = wx.StaticBoxSizer(meta_box, wx.VERTICAL)

        # IPA symbol input
        ipa_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ipa_label = wx.StaticText(left_panel, label="&IPA Symbol:")
        self.ipa_input = wx.TextCtrl(left_panel, size=(80, -1))
        self.ipa_input.SetName("IPA Symbol")
        ipa_sizer.Add(ipa_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        ipa_sizer.Add(self.ipa_input, 0, wx.RIGHT, 10)

        # Category dropdown
        cat_label = wx.StaticText(left_panel, label="&Category:")
        self.category_choice = wx.Choice(left_panel, choices=[
            'vowel', 'fricative', 'stop', 'nasal', 'approximant', 'affricate', 'custom'
        ])
        self.category_choice.SetSelection(0)
        self.category_choice.SetName("Category")
        ipa_sizer.Add(cat_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        ipa_sizer.Add(self.category_choice, 0)

        meta_sizer.Add(ipa_sizer, 0, wx.ALL, 5)

        # Description
        desc_label = wx.StaticText(left_panel, label="&Description:")
        self.desc_input = wx.TextCtrl(left_panel, size=(250, -1))
        self.desc_input.SetName("Description")
        meta_sizer.Add(desc_label, 0, wx.LEFT | wx.TOP, 5)
        meta_sizer.Add(self.desc_input, 0, wx.ALL | wx.EXPAND, 5)

        # Voiced/Vowel checkboxes
        check_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.is_vowel_cb = wx.CheckBox(left_panel, label="Is &Vowel")
        self.is_vowel_cb.SetValue(True)
        self.is_voiced_cb = wx.CheckBox(left_panel, label="Is V&oiced")
        self.is_voiced_cb.SetValue(True)
        check_sizer.Add(self.is_vowel_cb, 0, wx.RIGHT, 20)
        check_sizer.Add(self.is_voiced_cb, 0)
        meta_sizer.Add(check_sizer, 0, wx.ALL, 5)

        left_sizer.Add(meta_sizer, 0, wx.ALL | wx.EXPAND, 5)

        # Play controls
        play_box = wx.StaticBox(left_panel, label="Preview")
        play_sizer = wx.StaticBoxSizer(play_box, wx.VERTICAL)

        # Duration control
        dur_sizer = wx.BoxSizer(wx.HORIZONTAL)
        dur_label = wx.StaticText(left_panel, label="D&uration:")
        self.duration_slider = wx.Slider(left_panel, value=300, minValue=50, maxValue=1000)
        self.duration_slider.SetName("Duration")
        self.duration_value = wx.StaticText(left_panel, label="300 ms")
        dur_sizer.Add(dur_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        dur_sizer.Add(self.duration_slider, 1, wx.EXPAND | wx.RIGHT, 5)
        dur_sizer.Add(self.duration_value, 0, wx.ALIGN_CENTER_VERTICAL)
        play_sizer.Add(dur_sizer, 0, wx.ALL | wx.EXPAND, 5)

        # Play button
        self.play_btn = wx.Button(left_panel, label="&Play (Space)")
        self.play_btn.SetName("Play")
        play_sizer.Add(self.play_btn, 0, wx.ALL | wx.EXPAND, 5)

        # Stop button
        self.stop_btn = wx.Button(left_panel, label="S&top")
        self.stop_btn.SetName("Stop")
        self.stop_btn.Enable(False)
        play_sizer.Add(self.stop_btn, 0, wx.ALL | wx.EXPAND, 5)

        left_sizer.Add(play_sizer, 0, wx.ALL | wx.EXPAND, 5)

        # Test Sequence section
        seq_box = wx.StaticBox(left_panel, label="Test Sequence")
        seq_sizer = wx.StaticBoxSizer(seq_box, wx.VERTICAL)

        # Sequence input
        seq_label = wx.StaticText(left_panel, label="Pattern (e.g. [a][p][a]):")
        seq_sizer.Add(seq_label, 0, wx.LEFT | wx.TOP, 5)

        self.sequence_input = wx.TextCtrl(left_panel, value="[a][p][a]", size=(200, -1))
        self.sequence_input.SetName("Test Sequence Pattern")
        self.sequence_input.SetToolTip(
            "Enter phonemes in brackets, e.g. [a][p][a]\n"
            "Use [*] to play current editor parameters"
        )
        seq_sizer.Add(self.sequence_input, 0, wx.ALL | wx.EXPAND, 5)

        # Quick insert buttons for common vowels
        quick_label = wx.StaticText(left_panel, label="Quick insert:")
        seq_sizer.Add(quick_label, 0, wx.LEFT, 5)

        quick_sizer = wx.BoxSizer(wx.HORIZONTAL)
        for vowel in ['a', 'i', 'u', 'e', 'o', 'ə']:
            btn = wx.Button(left_panel, label=vowel, size=(30, -1))
            btn.SetToolTip(f"Insert [{vowel}]")
            btn.Bind(wx.EVT_BUTTON, lambda evt, v=vowel: self._insert_phoneme(v))
            quick_sizer.Add(btn, 0, wx.ALL, 2)
        seq_sizer.Add(quick_sizer, 0, wx.ALL, 5)

        # Current phoneme buttons row
        current_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # [*] button - insert placeholder for current editor parameters
        star_btn = wx.Button(left_panel, label="[*]", size=(35, -1))
        star_btn.SetToolTip("Insert [*] - plays current editor parameters")
        star_btn.Bind(wx.EVT_BUTTON, lambda evt: self._insert_phoneme('*'))
        current_sizer.Add(star_btn, 0, wx.ALL, 2)

        # Insert IPA button - insert current IPA symbol
        self.insert_ipa_btn = wx.Button(left_panel, label="Insert &IPA", size=(70, -1))
        self.insert_ipa_btn.SetToolTip("Insert current IPA symbol from editor")
        self.insert_ipa_btn.Bind(wx.EVT_BUTTON, self._on_insert_current_ipa)
        current_sizer.Add(self.insert_ipa_btn, 0, wx.ALL, 2)

        seq_sizer.Add(current_sizer, 0, wx.ALL, 5)

        # Play Sequence button
        self.play_seq_btn = wx.Button(left_panel, label="Play Se&quence")
        self.play_seq_btn.SetName("Play Sequence")
        seq_sizer.Add(self.play_seq_btn, 0, wx.ALL | wx.EXPAND, 5)

        left_sizer.Add(seq_sizer, 0, wx.ALL | wx.EXPAND, 5)

        # Action buttons
        action_box = wx.StaticBox(left_panel, label="Actions")
        action_sizer = wx.StaticBoxSizer(action_box, wx.VERTICAL)

        self.save_btn = wx.Button(left_panel, label="&Save Preset")
        self.save_btn.SetName("Save Preset")
        action_sizer.Add(self.save_btn, 0, wx.ALL | wx.EXPAND, 5)

        self.export_btn = wx.Button(left_panel, label="&Export to Clipboard")
        self.export_btn.SetName("Export to Clipboard")
        action_sizer.Add(self.export_btn, 0, wx.ALL | wx.EXPAND, 5)

        self.reset_btn = wx.Button(left_panel, label="&Reset to Defaults")
        self.reset_btn.SetName("Reset to Defaults")
        action_sizer.Add(self.reset_btn, 0, wx.ALL | wx.EXPAND, 5)

        left_sizer.Add(action_sizer, 0, wx.ALL | wx.EXPAND, 5)

        left_panel.SetSizer(left_sizer)
        main_sizer.Add(left_panel, 0, wx.EXPAND | wx.ALL, 5)

        # Right panel: Scrollable parameter sliders
        self.param_panel = scrolled.ScrolledPanel(main_panel)
        self.param_panel.SetupScrolling(scroll_x=False)
        param_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create parameter groups
        for group_name, params in PARAM_GROUPS.items():
            group_box = wx.StaticBox(self.param_panel, label=group_name)
            group_sizer = wx.StaticBoxSizer(group_box, wx.VERTICAL)

            for param_name, min_val, max_val, default, unit, desc in params:
                self._create_slider(self.param_panel, group_sizer,
                                   param_name, min_val, max_val, default, unit, desc)

            param_sizer.Add(group_sizer, 0, wx.ALL | wx.EXPAND, 5)

        self.param_panel.SetSizer(param_sizer)
        main_sizer.Add(self.param_panel, 1, wx.EXPAND | wx.ALL, 5)

        main_panel.SetSizer(main_sizer)

        # Status bar
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetName("Status")

    def _create_slider(self, parent, sizer, name, min_val, max_val, default, unit, desc):
        """Create a labeled slider for a parameter."""
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Label (fixed width for alignment)
        label = wx.StaticText(parent, label=f"{name}:", size=(180, -1))
        label.SetToolTip(desc)
        row_sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        # Slider
        slider = wx.Slider(parent, value=default, minValue=min_val, maxValue=max_val,
                          style=wx.SL_HORIZONTAL, size=(200, -1))
        slider.SetName(f"{name} ({desc})")
        slider.SetToolTip(f"{desc} ({min_val}-{max_val} {unit})")
        row_sizer.Add(slider, 1, wx.EXPAND | wx.RIGHT, 5)

        # Value display
        value_label = wx.StaticText(parent, label=f"{default} {unit}", size=(80, -1))
        row_sizer.Add(value_label, 0, wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(row_sizer, 0, wx.ALL | wx.EXPAND, 2)

        # Store references
        self.sliders[name] = (slider, min_val, max_val, default, unit)
        self.value_labels[name] = value_label

        # Bind slider event
        slider.Bind(wx.EVT_SLIDER, lambda e, n=name: self._on_slider_change(n))

    def _on_slider_change(self, name):
        """Handle slider value change."""
        slider, min_val, max_val, default, unit = self.sliders[name]
        value = slider.GetValue()
        self.value_labels[name].SetLabel(f"{value} {unit}")

    def _bind_events(self):
        """Bind event handlers."""
        self.play_btn.Bind(wx.EVT_BUTTON, self.on_play)
        self.stop_btn.Bind(wx.EVT_BUTTON, self.on_stop)
        self.play_seq_btn.Bind(wx.EVT_BUTTON, self.on_play_sequence)
        self.save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        self.export_btn.Bind(wx.EVT_BUTTON, self.on_export)
        self.reset_btn.Bind(wx.EVT_BUTTON, self.on_reset)
        self.duration_slider.Bind(wx.EVT_SLIDER, self.on_duration_change)

        # Keyboard shortcuts
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

        # Custom events
        self.Bind(EVT_STATUS_UPDATE, self.on_status_update)
        self.Bind(EVT_PLAY_DONE, self.on_play_done)

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_key(self, event):
        """Handle keyboard shortcuts including IPA keyboard for sequence field."""
        key = event.GetKeyCode()

        # Check for Alt+key combination for IPA keyboard input
        if event.AltDown() and self.sequence_input.HasFocus():
            if self._handle_ipa_key(key):
                return  # Handled, don't skip

        # Global playback shortcuts
        if key == wx.WXK_F5 and not self.is_playing:
            self.on_play(None)  # Play current phoneme
        elif key == wx.WXK_F6 and not self.is_playing:
            self.on_play_sequence(None)  # Play sequence
        elif key == wx.WXK_ESCAPE:
            self.on_stop(None)
        else:
            event.Skip()

    def _handle_ipa_key(self, key_code):
        """Handle Alt+key for IPA input in sequence field.

        Returns True if the key was handled, False otherwise.
        """
        # Map key code to lookup key
        if 65 <= key_code <= 90:  # A-Z
            lookup_key = chr(key_code).lower()
        elif 97 <= key_code <= 122:  # a-z (lowercase)
            lookup_key = chr(key_code)
        elif 48 <= key_code <= 57:  # 0-9
            lookup_key = chr(key_code)
        else:
            return False  # Not a valid IPA key

        current_time = time.time()

        # Check for cycling through symbols
        if lookup_key == self._last_ipa_key and (current_time - self._last_ipa_time) < self._cycle_timeout:
            self._ipa_press_count += 1
            # Delete previous [symbol] that was just inserted
            text = self.sequence_input.GetValue()
            pos = self.sequence_input.GetInsertionPoint()
            # Find and delete the previous bracketed symbol
            if pos > 0:
                # Look for ] before cursor
                bracket_end = pos
                if pos > 0 and text[pos-1:pos] == ']':
                    # Find matching [
                    bracket_start = text.rfind('[', 0, pos-1)
                    if bracket_start >= 0:
                        self.sequence_input.Remove(bracket_start, bracket_end)
        else:
            self._ipa_press_count = 1

        self._last_ipa_key = lookup_key
        self._last_ipa_time = current_time

        # Get the IPA symbol for this key press
        result = ipa_keyboard.get_symbol_for_key(lookup_key, self._ipa_press_count)
        if result:
            symbol, description = result
            self.sequence_input.WriteText(f"[{symbol}]")
            self.set_status(f"Inserted: {symbol} ({description})")
            return True

        return False

    def on_duration_change(self, event):
        """Update duration label."""
        value = self.duration_slider.GetValue()
        self.duration_value.SetLabel(f"{value} ms")

    def get_frame_params(self):
        """Get current parameter values as a dictionary."""
        params = {}
        for name, (slider, min_val, max_val, default, unit) in self.sliders.items():
            value = slider.GetValue()

            # Apply scaling based on parameter type
            if name in PERCENT_PARAMS:
                params[name] = value / 100.0
            elif name in GAIN_PARAMS:
                params[name] = value / 100.0
            elif name in TENTH_PARAMS:
                params[name] = value / 10.0
            else:
                params[name] = float(value)

        return params

    def set_frame_params(self, params):
        """Set slider values from a parameter dictionary."""
        for name, value in params.items():
            if name not in self.sliders:
                continue

            slider, min_val, max_val, default, unit = self.sliders[name]

            # Reverse scaling
            if name in PERCENT_PARAMS:
                slider_val = int(value * 100)
            elif name in GAIN_PARAMS:
                slider_val = int(value * 100)
            elif name in TENTH_PARAMS:
                slider_val = int(value * 10)
            else:
                slider_val = int(value)

            # Clamp to range
            slider_val = max(min_val, min(max_val, slider_val))
            slider.SetValue(slider_val)
            self.value_labels[name].SetLabel(f"{slider_val} {unit}")

    def create_frame(self):
        """Create a Frame object from current parameters."""
        frame = speechPlayer.Frame()
        params = self.get_frame_params()

        for name, value in params.items():
            if hasattr(frame, name):
                setattr(frame, name, value)

        return frame

    def set_status(self, message):
        """Update status bar (thread-safe)."""
        if wx.IsMainThread():
            self.status_bar.SetStatusText(message)
        else:
            evt = StatusUpdateEvent(message=message)
            wx.PostEvent(self, evt)

    def on_status_update(self, event):
        """Handle status update event."""
        self.status_bar.SetStatusText(event.message)

    def on_play_done(self, event):
        """Handle play completion."""
        self.is_playing = False
        self.play_btn.Enable(True)
        self.play_seq_btn.Enable(True)
        self.stop_btn.Enable(False)

    def _play_thread(self, frame, duration_ms):
        """Thread function for audio playback."""
        try:
            # Debug: show key parameter values
            self.set_status(f"Playing: pitch={frame.voicePitch:.0f}Hz, voice={frame.voiceAmplitude:.2f}, F1={frame.cf1:.0f}")

            sp = speechPlayer.SpeechPlayer(self.sample_rate)

            # Ensure minimum values for audible output
            if frame.voicePitch < 25:
                frame.voicePitch = 100
            if frame.endVoicePitch < 25:
                frame.endVoicePitch = frame.voicePitch
            if frame.preFormantGain <= 0:
                frame.preFormantGain = 1.0
            if frame.outputGain <= 0:
                frame.outputGain = 1.0

            # Queue the frame
            fade_ms = min(50, duration_ms // 2)
            sp.queueFrame(frame, duration_ms, fade_ms)
            # Queue silence to end
            sp.queueFrame(None, 50, 20)

            # Synthesize
            all_samples = []
            while self.is_playing:
                samples = sp.synthesize(8192)
                if samples and hasattr(samples, 'length') and samples.length > 0:
                    all_samples.extend(samples[:samples.length])
                elif samples:
                    all_samples.extend(samples[:])
                    if len(samples) < 8192:
                        break
                else:
                    break

            if not self.is_playing or not all_samples:
                return

            self.set_status(f"Playing {len(all_samples)} samples...")

            # Save to temp file and play
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name

            with wave.open(tmp_path, 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(self.sample_rate)
                wav.writeframes(struct.pack('<%dh' % len(all_samples), *all_samples))

            if self.is_playing and HAS_WINSOUND:
                winsound.PlaySound(tmp_path, winsound.SND_FILENAME)

            try:
                os.unlink(tmp_path)
            except:
                pass

            self.set_status("Done.")

        except Exception as e:
            self.set_status(f"Error: {e}")
        finally:
            evt = PlayDoneEvent()
            wx.PostEvent(self, evt)

    def on_play(self, event):
        """Play current parameters."""
        if self.is_playing:
            return

        self.is_playing = True
        self.play_btn.Enable(False)
        self.stop_btn.Enable(True)

        frame = self.create_frame()
        duration = self.duration_slider.GetValue()

        self.play_thread = threading.Thread(
            target=self._play_thread,
            args=(frame, duration),
            daemon=True
        )
        self.play_thread.start()

    def on_stop(self, event):
        """Stop playback."""
        if self.is_playing:
            self.is_playing = False
            if HAS_WINSOUND:
                winsound.PlaySound(None, winsound.SND_PURGE)
            self.set_status("Stopped.")
            self.play_btn.Enable(True)
            self.stop_btn.Enable(False)

    def _insert_phoneme(self, phoneme):
        """Insert a phoneme in brackets at cursor position in sequence input."""
        self.sequence_input.WriteText(f"[{phoneme}]")
        self.sequence_input.SetFocus()

    def _on_insert_current_ipa(self, event):
        """Insert the current IPA symbol into the sequence field."""
        ipa = self.ipa_input.GetValue().strip()
        if ipa:
            self._insert_phoneme(ipa)
            self.set_status(f"Inserted [{ipa}] - uses preset values from phoneme data")
        else:
            self.set_status("No IPA symbol to insert. Enter an IPA symbol first.")

    def _parse_test_sequence(self, sequence_str):
        """Parse a test sequence string into list of (phoneme_key, params).

        Args:
            sequence_str: String like "[a][p][a]" or "[a][*][a]" where [*] uses current editor params

        Returns:
            List of (phoneme_key, params_dict) tuples
        """
        import re
        phonemes = []

        # Find all bracketed phonemes
        pattern = r'\[([^\]]+)\]'
        matches = re.findall(pattern, sequence_str)

        for phoneme_key in matches:
            if phoneme_key == '*':
                # Special placeholder: use current editor parameters
                current_params = self.get_frame_params()
                # Add metadata from checkboxes
                current_params['_isVowel'] = self.is_vowel_cb.GetValue()
                current_params['_isVoiced'] = self.is_voiced_cb.GetValue()
                # Determine stop/nasal based on category
                category = self.category_choice.GetStringSelection()
                current_params['_isStop'] = (category == 'stop')
                current_params['_isNasal'] = (category == 'nasal')
                phonemes.append(('*', current_params))
            elif phoneme_key in PHONEME_DATA:
                phonemes.append((phoneme_key, PHONEME_DATA[phoneme_key]))
            else:
                # Unknown phoneme
                self.set_status(f"Unknown phoneme: {phoneme_key}")
                return None

        return phonemes

    def _create_frame_from_phoneme(self, params):
        """Create a Frame object from phoneme parameters."""
        frame = speechPlayer.Frame()

        # Set default pitch values
        frame.voicePitch = 100
        frame.endVoicePitch = 100
        frame.preFormantGain = 1.0
        frame.outputGain = 1.0

        # Apply phoneme parameters
        for name, value in params.items():
            if name.startswith('_'):
                continue  # Skip metadata
            if hasattr(frame, name):
                setattr(frame, name, value)

        return frame

    def _get_phoneme_duration(self, params):
        """Get appropriate duration for a phoneme based on its type."""
        if params.get('_isVowel'):
            return SEQUENCE_DURATIONS['vowel']
        else:
            return SEQUENCE_DURATIONS['consonant']

    def _play_test_sequence_thread(self, phoneme_list):
        """Thread function for playing a sequence of phonemes."""
        try:
            self.set_status(f"Playing sequence of {len(phoneme_list)} phonemes...")

            sp = speechPlayer.SpeechPlayer(self.sample_rate)

            # Queue all frames
            for phoneme_key, params in phoneme_list:
                frame = self._create_frame_from_phoneme(params)
                duration = self._get_phoneme_duration(params)
                fade = min(30, duration // 3)
                sp.queueFrame(frame, duration, fade)

            # Queue silence at end
            sp.queueFrame(None, 50, 20)

            # Synthesize in batches
            all_samples = []
            while self.is_playing:
                samples = sp.synthesize(8192)
                if samples and hasattr(samples, 'length') and samples.length > 0:
                    all_samples.extend(samples[:samples.length])
                elif samples:
                    all_samples.extend(samples[:])
                    if len(samples) < 8192:
                        break
                else:
                    break

            if not self.is_playing or not all_samples:
                return

            self.set_status(f"Playing {len(all_samples)} samples...")

            # Save to temp file and play
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name

            with wave.open(tmp_path, 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(self.sample_rate)
                wav.writeframes(struct.pack('<%dh' % len(all_samples), *all_samples))

            if self.is_playing and HAS_WINSOUND:
                winsound.PlaySound(tmp_path, winsound.SND_FILENAME)

            try:
                os.unlink(tmp_path)
            except:
                pass

            self.set_status("Sequence done.")

        except Exception as e:
            self.set_status(f"Error: {e}")
        finally:
            evt = PlayDoneEvent()
            wx.PostEvent(self, evt)

    def on_play_sequence(self, event):
        """Play the test sequence."""
        if self.is_playing:
            return

        sequence_str = self.sequence_input.GetValue().strip()
        if not sequence_str:
            self.set_status("No sequence to play.")
            return

        # Parse the sequence
        phoneme_list = self._parse_test_sequence(sequence_str)
        if phoneme_list is None:
            return  # Error already shown

        if not phoneme_list:
            self.set_status("No valid phonemes in sequence.")
            return

        self.is_playing = True
        self.play_btn.Enable(False)
        self.play_seq_btn.Enable(False)
        self.stop_btn.Enable(True)

        # Start playback thread
        self.play_thread = threading.Thread(
            target=self._play_test_sequence_thread,
            args=(phoneme_list,),
            daemon=True
        )
        self.play_thread.start()

    def on_new(self, event):
        """Reset to schwa (ə) - the neutral mid-central vowel."""
        self.on_reset(event)
        self.ipa_input.SetValue('ə')
        self.desc_input.SetValue('mid central (schwa)')
        # Set category to vowel
        idx = self.category_choice.FindString('vowel')
        if idx != wx.NOT_FOUND:
            self.category_choice.SetSelection(idx)
        self.is_vowel_cb.SetValue(True)
        self.is_voiced_cb.SetValue(True)
        self.set_status("New preset - parameters reset to schwa (ə) - mid central vowel.")

    def on_reset(self, event):
        """Reset sliders to schwa (ə) defaults - the neutral mid-central vowel."""
        for name, (slider, min_val, max_val, default, unit) in self.sliders.items():
            # Use schwa value if available, otherwise fall back to slider default
            value = SCHWA_DEFAULTS.get(name, default)
            # Ensure value is within slider range
            value = max(min_val, min(max_val, int(value)))
            slider.SetValue(value)
            self.value_labels[name].SetLabel(f"{value} {unit}")
        # Also update metadata to match schwa
        self.ipa_input.SetValue('ə')
        self.desc_input.SetValue('mid central (schwa)')
        idx = self.category_choice.FindString('vowel')
        if idx != wx.NOT_FOUND:
            self.category_choice.SetSelection(idx)
        self.is_vowel_cb.SetValue(True)
        self.is_voiced_cb.SetValue(True)
        self.set_status("Parameters reset to schwa (ə) - mid central vowel.")

    def on_open(self, event):
        """Open a preset file."""
        with wx.FileDialog(
            self,
            "Open Preset",
            wildcard="JSON files (*.json)|*.json|All files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        ) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return

            filepath = dlg.GetPath()

        try:
            data = self.preset_manager.load_preset(filepath)
            self.ipa_input.SetValue(data.get('ipa', ''))
            self.desc_input.SetValue(data.get('description', ''))

            # Set category
            cat = data.get('category', 'vowel')
            idx = self.category_choice.FindString(cat)
            if idx != wx.NOT_FOUND:
                self.category_choice.SetSelection(idx)

            self.is_vowel_cb.SetValue(data.get('isVowel', False))
            self.is_voiced_cb.SetValue(data.get('isVoiced', False))

            # Set parameters
            if 'parameters' in data:
                self.set_frame_params(data['parameters'])

            self.set_status(f"Loaded: {os.path.basename(filepath)}")

        except Exception as e:
            wx.MessageBox(f"Error loading preset: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def on_save(self, event):
        """Save current preset."""
        ipa = self.ipa_input.GetValue().strip()
        if not ipa:
            wx.MessageBox("Please enter an IPA symbol.", "Missing IPA", wx.OK | wx.ICON_WARNING)
            self.ipa_input.SetFocus()
            return

        preset_data = {
            'ipa': ipa,
            'name': ipa,
            'category': self.category_choice.GetStringSelection(),
            'description': self.desc_input.GetValue(),
            'isVowel': self.is_vowel_cb.GetValue(),
            'isVoiced': self.is_voiced_cb.GetValue(),
            'parameters': self.get_frame_params()
        }

        try:
            filepath = self.preset_manager.save_preset(preset_data)
            self.set_status(f"Saved: {filepath.name}")
        except Exception as e:
            wx.MessageBox(f"Error saving preset: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def on_export(self, event):
        """Export to clipboard as Python dict."""
        ipa = self.ipa_input.GetValue().strip() or 'x'

        preset_data = {
            'ipa': ipa,
            'isVowel': self.is_vowel_cb.GetValue(),
            'isVoiced': self.is_voiced_cb.GetValue(),
            'parameters': self.get_frame_params()
        }

        code = self.preset_manager.export_to_data_py(preset_data)

        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(code))
            wx.TheClipboard.Close()
            self.set_status("Copied to clipboard as Python dict.")
        else:
            wx.MessageBox("Could not access clipboard.", "Error", wx.OK | wx.ICON_ERROR)

    def on_about(self, event):
        """Show about dialog."""
        wx.MessageBox(
            "Phoneme Parameter Editor\n\n"
            "Comprehensive Klatt synthesis parameter editor.\n"
            "All 47 parameters exposed for creating phoneme presets.\n\n"
            "Based on NVSpeechPlayer by NV Access Limited\n"
            "License: GPL v2",
            "About",
            wx.OK | wx.ICON_INFORMATION
        )

    def on_exit(self, event):
        """Exit application."""
        self.Close()

    def on_close(self, event):
        """Handle window close."""
        if self.is_playing:
            self.is_playing = False
            if HAS_WINSOUND:
                winsound.PlaySound(None, winsound.SND_PURGE)
        event.Skip()


def main():
    """Main entry point."""
    app = wx.App()

    # High DPI support
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    frame = PhonemeEditorFrame()
    frame.Show()

    app.MainLoop()


if __name__ == "__main__":
    main()
