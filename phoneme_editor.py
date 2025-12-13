#!/usr/bin/env python3
"""
Phoneme Parameter Editor - Comprehensive Klatt Synthesis Parameter GUI

Exposes ALL 47 Klatt synthesis parameters with real-time preview and preset saving.
Designed for creating and testing phoneme definitions for NVSpeechPlayer.

Tab-based interface with:
- Parameters tab: All 47 parameter sliders
- Presets tab: Browse PHONEME_DATA and presets/ folder with "Load to Current"
- Sequence Testing tab: Test phonemes in context
- View tab: Read-only parameter display (Python dict and table)
- File tab: Export and save operations

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
import re
from pathlib import Path

# Import synthesis modules
import speechPlayer
import ipa_keyboard
import voice_profiles

# Load phoneme data from modular data package
from data import data as PHONEME_DATA, PHONEME_CATEGORIES, CATEGORY_ORDER

# Schwa (ə) defaults for reset - the neutral mid-central vowel
SCHWA_DEFAULTS = PHONEME_DATA.get('ə', {})

# Parameters that should NOT be saved with phoneme presets
# These are prosody/speaker parameters, not phoneme-intrinsic properties
PROSODY_PARAMS = {
    'voicePitch',           # Set by intonation/tone system
    'midVoicePitch',        # Set by tone contour system
    'endVoicePitch',        # Set by intonation/tone system
    'vibratoPitchOffset',   # Speaker characteristic
    'vibratoSpeed',         # Speaker characteristic
    'preFormantGain',       # Output level, not phoneme property
    'outputGain',           # Output level, not phoneme property
}

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
        ('voicePitch', 50, 500, 120, 'Hz', 'Fundamental frequency'),
        ('midVoicePitch', 0, 500, 0, 'Hz', 'Mid pitch (0=linear, >0=contour tone)'),
        ('endVoicePitch', 50, 500, 120, 'Hz', 'End pitch (for contours)'),
        ('vibratoPitchOffset', 0, 100, 12, '%', 'Vibrato depth (0-100%)'),
        ('vibratoSpeed', 0, 100, 55, 'x0.1Hz', 'Vibrato rate'),
        ('glottalOpenQuotient', 10, 99, 50, '%', 'Glottis open time'),
    ],
    'Amplitudes': [
        ('voiceAmplitude', 0, 100, 100, '%', 'Voiced sound level'),
        ('voiceTurbulenceAmplitude', 0, 100, 0, '%', 'Breathiness'),
        ('aspirationAmplitude', 0, 100, 0, '%', 'Aspiration noise'),
        ('aspirationFilterFreq', 0, 6000, 0, 'Hz', 'Aspiration bandpass (0=white)'),
        ('aspirationFilterBw', 100, 4000, 2000, 'Hz', 'Aspiration filter width'),
        ('fricationAmplitude', 0, 100, 0, '%', 'Frication noise'),
        ('noiseFilterFreq', 0, 8000, 0, 'Hz', 'Frication bandpass (0=white)'),
        ('noiseFilterBw', 100, 4000, 1000, 'Hz', 'Frication filter width'),
        ('preFormantGain', 0, 200, 100, '%', 'Pre-resonator gain'),
        ('outputGain', 0, 200, 100, '%', 'Master volume'),
    ],
    'Cascade Formants (F1-F3)': [
        ('cf1', 150, 1000, 500, 'Hz', 'F1 frequency'),
        ('cb1', 40, 500, 60, 'Hz', 'F1 bandwidth'),
        ('cf2', 500, 2800, 1500, 'Hz', 'F2 frequency'),
        ('cb2', 40, 500, 90, 'Hz', 'F2 bandwidth'),
        ('cf3', 1300, 3800, 2500, 'Hz', 'F3 frequency'),
        ('cb3', 40, 500, 150, 'Hz', 'F3 bandwidth'),
    ],
    'Cascade Formants (F4-F6)': [
        ('cf4', 2500, 4800, 3500, 'Hz', 'F4 frequency'),
        ('cb4', 100, 500, 250, 'Hz', 'F4 bandwidth'),
        ('cf5', 3500, 5000, 4500, 'Hz', 'F5 frequency'),
        ('cb5', 150, 700, 200, 'Hz', 'F5 bandwidth'),
        ('cf6', 4000, 5500, 4900, 'Hz', 'F6 frequency'),
        ('cb6', 200, 2000, 1000, 'Hz', 'F6 bandwidth'),
    ],
    'Nasal Formants': [
        ('cfN0', 200, 2500, 450, 'Hz', 'Nasal zero ([m]1000, [n]1400, [ŋ]2000)'),
        ('cbN0', 50, 500, 100, 'Hz', 'Nasal zero bandwidth'),
        ('cfNP', 200, 500, 270, 'Hz', 'Nasal pole frequency'),
        ('cbNP', 50, 500, 100, 'Hz', 'Nasal pole bandwidth'),
        ('caNP', 0, 100, 0, '%', 'Nasal coupling'),
    ],
    'Parallel Formants (F1-F3)': [
        ('pf1', 150, 1000, 500, 'Hz', 'Parallel F1 freq'),
        ('pb1', 40, 500, 60, 'Hz', 'Parallel F1 BW'),
        ('pa1', 0, 100, 0, '%', 'Parallel F1 amp'),
        ('pf2', 500, 2800, 1500, 'Hz', 'Parallel F2 freq'),
        ('pb2', 40, 500, 90, 'Hz', 'Parallel F2 BW'),
        ('pa2', 0, 100, 0, '%', 'Parallel F2 amp'),
        ('pf3', 1300, 3800, 2500, 'Hz', 'Parallel F3 freq'),
        ('pb3', 40, 500, 150, 'Hz', 'Parallel F3 BW'),
        ('pa3', 0, 100, 0, '%', 'Parallel F3 amp'),
    ],
    'Parallel Formants (F4-F6)': [
        ('pf4', 2500, 4800, 3500, 'Hz', 'Parallel F4 freq'),
        ('pb4', 100, 500, 250, 'Hz', 'Parallel F4 BW'),
        ('pa4', 0, 100, 0, '%', 'Parallel F4 amp'),
        ('pf5', 3500, 5000, 4500, 'Hz', 'Parallel F5 freq'),
        ('pb5', 150, 700, 200, 'Hz', 'Parallel F5 BW'),
        ('pa5', 0, 100, 0, '%', 'Parallel F5 amp'),
        ('pf6', 4000, 5500, 4900, 'Hz', 'Parallel F6 freq'),
        ('pb6', 200, 2000, 1000, 'Hz', 'Parallel F6 BW'),
        ('pa6', 0, 100, 0, '%', 'Parallel F6 amp'),
    ],
    'Parallel Bypass': [
        ('parallelBypass', 0, 105, 0, '%', 'Unfiltered noise bypass'),
    ],
    'Voice Quality (KLSYN88)': [
        ('spectralTilt', 0, 41, 0, 'dB', 'High-freq attenuation (breathy)'),
        ('flutter', 0, 100, 25, '%', 'Natural pitch jitter'),
        ('openQuotientShape', 0, 100, 50, '%', 'Glottal closing curve'),
        ('speedQuotient', 50, 200, 100, '%', 'Opening/closing asymmetry'),
        ('diplophonia', 0, 100, 0, '%', 'Period alternation (creaky)'),
        ('lfRd', 0, 27, 0, 'x0.1', 'LF model Rd (0=legacy, 3-27=tense-breathy)'),
    ],
    'Glottal Modulation': [
        ('deltaF1', 0, 100, 0, 'Hz', 'F1 increase during glottal open'),
        ('deltaB1', 0, 400, 0, 'Hz', 'B1 increase during glottal open'),
        ('sinusoidalVoicingAmplitude', 0, 100, 0, '%', 'Pure sine voicing (voicebars)'),
    ],
    'Tracheal Resonances': [
        ('ftpFreq1', 0, 1500, 0, 'Hz', 'Tracheal pole 1 (~600-750 Hz)'),
        ('ftpBw1', 40, 500, 100, 'Hz', 'Tracheal pole 1 bandwidth'),
        ('ftzFreq1', 0, 1500, 0, 'Hz', 'Tracheal zero 1 (0=off)'),
        ('ftzBw1', 40, 500, 100, 'Hz', 'Tracheal zero 1 bandwidth'),
        ('ftpFreq2', 0, 2500, 0, 'Hz', 'Tracheal pole 2 (~1550-1650 Hz)'),
        ('ftpBw2', 40, 500, 100, 'Hz', 'Tracheal pole 2 bandwidth'),
        ('ftzFreq2', 0, 2500, 0, 'Hz', 'Tracheal zero 2 (0=off)'),
        ('ftzBw2', 40, 500, 200, 'Hz', 'Tracheal zero 2 bandwidth'),
    ],
    'Stop Burst': [
        ('burstAmplitude', 0, 100, 0, '%', 'Burst transient intensity'),
        ('burstDuration', 0, 100, 25, '%', 'Burst length (5-20ms)'),
    ],
}

# Parameters that use percentage scaling (0-100 maps to 0.0-1.0)
PERCENT_PARAMS = {
    'voiceAmplitude', 'voiceTurbulenceAmplitude', 'aspirationAmplitude',
    'fricationAmplitude', 'caNP', 'pa1', 'pa2', 'pa3', 'pa4', 'pa5', 'pa6',
    'glottalOpenQuotient', 'vibratoPitchOffset',
    'flutter', 'openQuotientShape', 'speedQuotient', 'diplophonia',
    'burstAmplitude', 'burstDuration', 'sinusoidalVoicingAmplitude',
}

# Parameters that use percentage scaling (0-200 maps to 0.0-2.0)
GAIN_PARAMS = {'preFormantGain', 'outputGain'}

# Parameters that need /10 scaling
TENTH_PARAMS = {'vibratoSpeed', 'parallelBypass', 'lfRd'}

# KLSYN88 default values
KLSYN88_DEFAULTS = {
    'spectralTilt': 0,
    'flutter': 0.25,
    'openQuotientShape': 0.5,
    'speedQuotient': 1.0,
    'diplophonia': 0,
    'lfRd': 0,
    'deltaF1': 0,
    'deltaB1': 0,
    'sinusoidalVoicingAmplitude': 0,
    'ftpFreq1': 0,
    'ftpBw1': 100,
    'ftzFreq1': 0,
    'ftzBw1': 100,
    'ftpFreq2': 0,
    'ftpBw2': 100,
    'ftzFreq2': 0,
    'ftzBw2': 200,
    'burstAmplitude': 0,
    'burstDuration': 0.25,
    'aspirationFilterFreq': 0,
    'aspirationFilterBw': 2000,
    'noiseFilterFreq': 0,
    'noiseFilterBw': 1000,
}

# IPA descriptions
IPA_DESCRIPTIONS = {
    'i': 'close front unrounded', 'y': 'close front rounded',
    'ɨ': 'close central unrounded', 'ʉ': 'close central rounded',
    'ɯ': 'close back unrounded', 'u': 'close back rounded',
    'ɪ': 'near-close front unrounded', 'ʏ': 'near-close front rounded',
    'ʊ': 'near-close back rounded',
    'e': 'close-mid front unrounded', 'ø': 'close-mid front rounded',
    'ɘ': 'close-mid central unrounded', 'ɵ': 'close-mid central rounded',
    'ɤ': 'close-mid back unrounded', 'o': 'close-mid back rounded',
    'ə': 'mid central (schwa)',
    'ɛ': 'open-mid front unrounded', 'œ': 'open-mid front rounded',
    'ɜ': 'open-mid central unrounded', 'ɞ': 'open-mid central rounded',
    'ʌ': 'open-mid back unrounded', 'ɔ': 'open-mid back rounded',
    'æ': 'near-open front unrounded', 'ɐ': 'near-open central',
    'a': 'open front unrounded', 'ɶ': 'open front rounded',
    'ä': 'open central unrounded', 'ɑ': 'open back unrounded', 'ɒ': 'open back rounded',
    'ɝ': 'r-colored mid central', 'ɚ': 'r-colored schwa',
    'p': 'voiceless bilabial plosive', 'b': 'voiced bilabial plosive',
    't': 'voiceless alveolar plosive', 'd': 'voiced alveolar plosive',
    'k': 'voiceless velar plosive', 'g': 'voiced velar plosive',
    'm': 'bilabial nasal', 'n': 'alveolar nasal', 'ŋ': 'velar nasal',
    'f': 'voiceless labiodental fricative', 'v': 'voiced labiodental fricative',
    'θ': 'voiceless dental fricative', 'ð': 'voiced dental fricative',
    's': 'voiceless alveolar fricative', 'z': 'voiced alveolar fricative',
    'ʃ': 'voiceless postalveolar fricative', 'ʒ': 'voiced postalveolar fricative',
    'h': 'voiceless glottal fricative',
    'l': 'alveolar lateral approximant', 'ɹ': 'alveolar approximant',
    'j': 'palatal approximant', 'w': 'labial-velar approximant',
}

# Duration defaults for test sequences
SEQUENCE_DURATIONS = {'vowel': 250, 'consonant': 100, 'default': 150}


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


# =============================================================================
# PANEL CLASSES
# =============================================================================

class HeaderPanel(wx.Panel):
    """Always-visible panel with metadata and preview controls."""

    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor = editor
        self._create_widgets()

    def _create_widgets(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Row 1: Metadata
        meta_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # IPA Symbol
        meta_sizer.Add(wx.StaticText(self, label="IPA:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.ipa_input = wx.TextCtrl(self, size=(60, -1))
        self.ipa_input.SetName("IPA Symbol")
        meta_sizer.Add(self.ipa_input, 0, wx.RIGHT, 15)

        # Category
        meta_sizer.Add(wx.StaticText(self, label="Category:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.category_choice = wx.Choice(self, choices=[
            'vowel', 'fricative', 'stop', 'nasal', 'approximant', 'affricate', 'custom'
        ])
        self.category_choice.SetSelection(0)
        self.category_choice.SetName("Category")
        meta_sizer.Add(self.category_choice, 0, wx.RIGHT, 15)

        # Checkboxes
        self.is_vowel_cb = wx.CheckBox(self, label="Vowel")
        self.is_vowel_cb.SetValue(True)
        meta_sizer.Add(self.is_vowel_cb, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

        self.is_voiced_cb = wx.CheckBox(self, label="Voiced")
        self.is_voiced_cb.SetValue(True)
        meta_sizer.Add(self.is_voiced_cb, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)

        # Description
        meta_sizer.Add(wx.StaticText(self, label="Desc:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.desc_input = wx.TextCtrl(self, size=(200, -1))
        self.desc_input.SetName("Description")
        meta_sizer.Add(self.desc_input, 1, wx.EXPAND)

        main_sizer.Add(meta_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Row 2: Preview controls
        preview_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Voice preset
        preview_sizer.Add(wx.StaticText(self, label="Voice:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.voice_preset_choice = wx.Choice(self, choices=voice_profiles.get_profile_names())
        self.voice_preset_choice.SetSelection(0)
        self.voice_preset_choice.SetName("Preview Voice Type")
        preview_sizer.Add(self.voice_preset_choice, 0, wx.RIGHT, 15)

        # Formant scale
        preview_sizer.Add(wx.StaticText(self, label="Formant:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.formant_slider = wx.Slider(self, value=100, minValue=80, maxValue=150, size=(100, -1))
        self.formant_slider.SetName("Formant Scale")
        preview_sizer.Add(self.formant_slider, 0, wx.RIGHT, 5)
        self.formant_value = wx.StaticText(self, label="1.00", size=(35, -1))
        preview_sizer.Add(self.formant_value, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)

        # Duration
        preview_sizer.Add(wx.StaticText(self, label="Duration:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.duration_slider = wx.Slider(self, value=300, minValue=50, maxValue=1000, size=(100, -1))
        self.duration_slider.SetName("Duration")
        preview_sizer.Add(self.duration_slider, 0, wx.RIGHT, 5)
        self.duration_value = wx.StaticText(self, label="300 ms", size=(50, -1))
        preview_sizer.Add(self.duration_value, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)

        # Play/Stop buttons
        self.play_btn = wx.Button(self, label="Play (F5)", size=(80, -1))
        self.play_btn.SetName("Play")
        preview_sizer.Add(self.play_btn, 0, wx.RIGHT, 5)

        self.stop_btn = wx.Button(self, label="Stop", size=(60, -1))
        self.stop_btn.SetName("Stop")
        self.stop_btn.Enable(False)
        preview_sizer.Add(self.stop_btn, 0, wx.RIGHT, 10)

        # Reference sample button
        self.ref_btn = wx.Button(self, label="Ref (F7)", size=(70, -1))
        self.ref_btn.SetName("Play Reference Sample")
        self.ref_btn.SetToolTip("Play human-recorded reference (F7)")
        preview_sizer.Add(self.ref_btn, 0)

        main_sizer.Add(preview_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(main_sizer)

        # Bind events
        self.formant_slider.Bind(wx.EVT_SLIDER, self._on_formant_change)
        self.duration_slider.Bind(wx.EVT_SLIDER, self._on_duration_change)
        self.voice_preset_choice.Bind(wx.EVT_CHOICE, self._on_voice_preset_change)

    def _on_formant_change(self, event):
        value = self.formant_slider.GetValue() / 100.0
        self.formant_value.SetLabel(f"{value:.2f}")
        # Switch to Custom
        custom_idx = self.voice_preset_choice.FindString('Custom')
        if custom_idx != wx.NOT_FOUND and event:
            self.voice_preset_choice.SetSelection(custom_idx)

    def _on_duration_change(self, event):
        self.duration_value.SetLabel(f"{self.duration_slider.GetValue()} ms")

    def _on_voice_preset_change(self, event):
        preset_name = self.voice_preset_choice.GetStringSelection()
        if preset_name == 'Custom':
            return
        profile = voice_profiles.get_profile(preset_name)
        if profile.get('formantScale') is not None:
            self.formant_slider.SetValue(int(profile['formantScale'] * 100))
            self.formant_value.SetLabel(f"{profile['formantScale']:.2f}")
        # Update pitch slider to use voice profile's base pitch
        if profile.get('basePitch') is not None:
            # Update the voicePitch slider in the parameters panel
            params_panel = self.editor.params_panel
            if 'voicePitch' in params_panel.sliders:
                pitch = int(profile['basePitch'])
                params_panel.sliders['voicePitch'].SetValue(pitch)
                params_panel.value_labels['voicePitch'].SetLabel(f"{pitch}")
                self.editor.params['voicePitch'] = pitch
            if 'endVoicePitch' in params_panel.sliders:
                params_panel.sliders['endVoicePitch'].SetValue(pitch)
                params_panel.value_labels['endVoicePitch'].SetLabel(f"{pitch}")
                self.editor.params['endVoicePitch'] = pitch
        self.editor.set_status(f"Preview voice: {preset_name} (pitch={profile.get('basePitch', 100)}Hz)")


class ParametersPanel(scrolled.ScrolledPanel):
    """Tab panel containing all 47 parameter sliders."""

    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor = editor
        self.sliders = {}
        self.value_labels = {}
        self._create_widgets()
        self.SetupScrolling(scroll_x=False)

    def _create_widgets(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        for group_name, params in PARAM_GROUPS.items():
            group_box = wx.StaticBox(self, label=group_name)
            group_sizer = wx.StaticBoxSizer(group_box, wx.VERTICAL)

            for param_name, min_val, max_val, default, unit, desc in params:
                self._create_slider(group_sizer, param_name, min_val, max_val, default, unit, desc)

            main_sizer.Add(group_sizer, 0, wx.ALL | wx.EXPAND, 5)

        # Reset button at bottom
        self.reset_btn = wx.Button(self, label="&Reset to Defaults")
        self.reset_btn.SetName("Reset to Defaults")
        main_sizer.Add(self.reset_btn, 0, wx.ALL | wx.EXPAND, 10)

        self.SetSizer(main_sizer)

    def _create_slider(self, sizer, name, min_val, max_val, default, unit, desc):
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, label=f"{name}:", size=(180, -1))
        label.SetToolTip(desc)
        row_sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        slider = wx.Slider(self, value=default, minValue=min_val, maxValue=max_val,
                          style=wx.SL_HORIZONTAL, size=(200, -1))
        slider.SetName(f"{name} ({desc})")
        slider.SetToolTip(f"{desc} ({min_val}-{max_val} {unit})")
        row_sizer.Add(slider, 1, wx.EXPAND | wx.RIGHT, 5)

        value_label = wx.StaticText(self, label=f"{default} {unit}", size=(80, -1))
        row_sizer.Add(value_label, 0, wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(row_sizer, 0, wx.ALL | wx.EXPAND, 2)

        self.sliders[name] = (slider, min_val, max_val, default, unit)
        self.value_labels[name] = value_label

        slider.Bind(wx.EVT_SLIDER, lambda e, n=name: self._on_slider_change(n))

    def _on_slider_change(self, name):
        slider, min_val, max_val, default, unit = self.sliders[name]
        self.value_labels[name].SetLabel(f"{slider.GetValue()} {unit}")

    def get_frame_params(self):
        params = {}
        for name, (slider, min_val, max_val, default, unit) in self.sliders.items():
            value = slider.GetValue()
            if name in PERCENT_PARAMS:
                params[name] = value / 100.0
            elif name in GAIN_PARAMS:
                params[name] = value / 100.0
            elif name in TENTH_PARAMS:
                params[name] = value / 10.0
            else:
                params[name] = float(value)
        return params

    def set_frame_params(self, params, apply_klsyn88_defaults=True):
        if apply_klsyn88_defaults:
            all_params = dict(KLSYN88_DEFAULTS)
            all_params.update(params)
        else:
            all_params = params

        for name, value in all_params.items():
            if name not in self.sliders:
                continue
            slider, min_val, max_val, default, unit = self.sliders[name]
            if name in PERCENT_PARAMS:
                slider_val = int(value * 100)
            elif name in GAIN_PARAMS:
                slider_val = int(value * 100)
            elif name in TENTH_PARAMS:
                slider_val = int(value * 10)
            else:
                slider_val = int(value)
            slider_val = max(min_val, min(max_val, slider_val))
            slider.SetValue(slider_val)
            self.value_labels[name].SetLabel(f"{slider_val} {unit}")


class PresetsPanel(wx.Panel):
    """Tab panel for browsing and loading presets."""

    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor = editor
        self._create_widgets()

    def _create_widgets(self):
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left: PHONEME_DATA browser
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(wx.StaticText(self, label="Phoneme Database (PHONEME_DATA):"), 0, wx.ALL, 5)

        self.phoneme_tree = wx.TreeCtrl(self, style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT)
        self.phoneme_tree.SetName("Phoneme Database")
        self._populate_phoneme_tree()
        left_sizer.Add(self.phoneme_tree, 1, wx.EXPAND | wx.ALL, 5)

        # Buttons for PHONEME_DATA
        btn_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.load_full_btn = wx.Button(self, label="Load &Full")
        self.load_full_btn.SetToolTip("Load phoneme with all metadata (IPA, description, category)")
        btn_sizer1.Add(self.load_full_btn, 1, wx.RIGHT, 5)

        self.load_current_btn = wx.Button(self, label="Load to &Current")
        self.load_current_btn.SetToolTip("Load only parameters, preserve current metadata")
        btn_sizer1.Add(self.load_current_btn, 1)
        left_sizer.Add(btn_sizer1, 0, wx.EXPAND | wx.ALL, 5)

        main_sizer.Add(left_sizer, 1, wx.EXPAND | wx.ALL, 5)

        # Right: presets/ folder browser
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(wx.StaticText(self, label="Saved Presets (presets/ folder):"), 0, wx.ALL, 5)

        self.preset_list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.preset_list.SetName("Saved Presets")
        self.preset_list.InsertColumn(0, "IPA", width=50)
        self.preset_list.InsertColumn(1, "Category", width=80)
        self.preset_list.InsertColumn(2, "Description", width=150)
        self._populate_preset_list()
        right_sizer.Add(self.preset_list, 1, wx.EXPAND | wx.ALL, 5)

        # Buttons for presets/
        btn_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.load_preset_full_btn = wx.Button(self, label="Load Full")
        btn_sizer2.Add(self.load_preset_full_btn, 1, wx.RIGHT, 5)

        self.load_preset_current_btn = wx.Button(self, label="Load to Current")
        btn_sizer2.Add(self.load_preset_current_btn, 1, wx.RIGHT, 5)

        self.refresh_btn = wx.Button(self, label="Refresh")
        btn_sizer2.Add(self.refresh_btn, 0)
        right_sizer.Add(btn_sizer2, 0, wx.EXPAND | wx.ALL, 5)

        main_sizer.Add(right_sizer, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(main_sizer)

        # Bind events
        self.load_full_btn.Bind(wx.EVT_BUTTON, self._on_load_full)
        self.load_current_btn.Bind(wx.EVT_BUTTON, self._on_load_current)
        self.load_preset_full_btn.Bind(wx.EVT_BUTTON, self._on_load_preset_full)
        self.load_preset_current_btn.Bind(wx.EVT_BUTTON, self._on_load_preset_current)
        self.refresh_btn.Bind(wx.EVT_BUTTON, self._on_refresh)
        self.phoneme_tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._on_tree_activate)
        self.preset_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_list_activate)

    def _populate_phoneme_tree(self):
        self.phoneme_tree.DeleteAllItems()
        root = self.phoneme_tree.AddRoot("Phonemes")

        # Group vowel categories under a parent node
        vowel_categories = [c for c in CATEGORY_ORDER if c.startswith('Vowels')]
        other_categories = [c for c in CATEGORY_ORDER if not c.startswith('Vowels')]

        # Add Vowels parent with sub-categories
        if vowel_categories:
            vowels_item = self.phoneme_tree.AppendItem(root, "Vowels")
            for cat_name in vowel_categories:
                phonemes = PHONEME_CATEGORIES.get(cat_name, {})
                if not phonemes:
                    continue
                # Remove "Vowels - " prefix for cleaner display
                display_name = cat_name.replace('Vowels - ', '')
                cat_item = self.phoneme_tree.AppendItem(vowels_item, display_name)
                for ipa, params in sorted(phonemes.items(), key=lambda x: x[0]):
                    if not isinstance(params, dict):
                        continue
                    desc = IPA_DESCRIPTIONS.get(ipa, '')
                    label = f"{ipa} - {desc}" if desc else ipa
                    item = self.phoneme_tree.AppendItem(cat_item, label)
                    self.phoneme_tree.SetItemData(item, (ipa, params))

        # Add other categories at root level
        for cat_name in other_categories:
            phonemes = PHONEME_CATEGORIES.get(cat_name, {})
            if not phonemes:
                continue
            cat_item = self.phoneme_tree.AppendItem(root, cat_name)
            for ipa, params in sorted(phonemes.items(), key=lambda x: x[0]):
                if not isinstance(params, dict):
                    continue
                desc = IPA_DESCRIPTIONS.get(ipa, '')
                label = f"{ipa} - {desc}" if desc else ipa
                item = self.phoneme_tree.AppendItem(cat_item, label)
                self.phoneme_tree.SetItemData(item, (ipa, params))

        self.phoneme_tree.ExpandAll()

    def _populate_preset_list(self):
        self.preset_list.DeleteAllItems()
        presets = self.editor.preset_manager.list_presets()
        self._preset_files = []

        for category, preset_list in presets.items():
            for preset in preset_list:
                idx = self.preset_list.InsertItem(self.preset_list.GetItemCount(), preset['ipa'])
                self.preset_list.SetItem(idx, 1, category)
                self.preset_list.SetItem(idx, 2, preset['description'])
                self._preset_files.append(preset['filepath'])

    def _get_selected_phoneme(self):
        item = self.phoneme_tree.GetSelection()
        if item.IsOk():
            data = self.phoneme_tree.GetItemData(item)
            if data:
                return data
        return None

    def _get_selected_preset_file(self):
        idx = self.preset_list.GetFirstSelected()
        if idx >= 0 and idx < len(self._preset_files):
            return self._preset_files[idx]
        return None

    def _on_load_full(self, event):
        data = self._get_selected_phoneme()
        if data:
            ipa, params = data
            self.editor.load_phoneme_full(ipa, params)

    def _on_load_current(self, event):
        data = self._get_selected_phoneme()
        if data:
            ipa, params = data
            self.editor.load_to_current(params)
            self.editor.set_status(f"Loaded parameters from {ipa} (metadata preserved)")

    def _on_load_preset_full(self, event):
        filepath = self._get_selected_preset_file()
        if filepath:
            self.editor.load_preset_file(filepath, update_metadata=True)

    def _on_load_preset_current(self, event):
        filepath = self._get_selected_preset_file()
        if filepath:
            self.editor.load_preset_file(filepath, update_metadata=False)

    def _on_refresh(self, event):
        self._populate_preset_list()
        self.editor.set_status("Preset list refreshed")

    def _on_tree_activate(self, event):
        self._on_load_full(None)

    def _on_list_activate(self, event):
        self._on_load_preset_full(None)


class SequenceTestingPanel(wx.Panel):
    """Tab panel for sequence testing."""

    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor = editor
        self._create_widgets()

    def _create_widgets(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Help text
        help_text = (
            "Test phonemes in sequence. Format: [a][p][a]\n"
            "- [*] = current editor parameters\n"
            "- [ipa] = looks up from presets/ folder, then PHONEME_DATA"
        )
        help_label = wx.StaticText(self, label=help_text)
        main_sizer.Add(help_label, 0, wx.ALL, 10)

        # Sequence input
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        input_sizer.Add(wx.StaticText(self, label="Sequence:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.sequence_input = wx.TextCtrl(self, value="[a][*][a]", size=(300, -1))
        self.sequence_input.SetName("Test Sequence Pattern")
        input_sizer.Add(self.sequence_input, 1, wx.EXPAND)
        main_sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # Quick insert buttons
        quick_sizer = wx.BoxSizer(wx.HORIZONTAL)
        quick_sizer.Add(wx.StaticText(self, label="Quick insert:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

        for symbol in ['a', 'i', 'u', 'e', 'o', 'ə', '*']:
            btn = wx.Button(self, label=f"[{symbol}]", size=(45, -1))
            btn.Bind(wx.EVT_BUTTON, lambda evt, s=symbol: self._insert_phoneme(s))
            quick_sizer.Add(btn, 0, wx.RIGHT, 5)

        # Insert current IPA button
        self.insert_ipa_btn = wx.Button(self, label="[IPA]", size=(50, -1))
        self.insert_ipa_btn.SetToolTip("Insert current IPA symbol from header")
        self.insert_ipa_btn.Bind(wx.EVT_BUTTON, self._on_insert_current_ipa)
        quick_sizer.Add(self.insert_ipa_btn, 0)

        main_sizer.Add(quick_sizer, 0, wx.ALL, 10)

        # Play Sequence button
        self.play_seq_btn = wx.Button(self, label="&Play Sequence (F6)")
        self.play_seq_btn.SetName("Play Sequence")
        main_sizer.Add(self.play_seq_btn, 0, wx.ALL, 10)

        self.SetSizer(main_sizer)

    def _insert_phoneme(self, symbol):
        self.sequence_input.WriteText(f"[{symbol}]")
        self.sequence_input.SetFocus()

    def _on_insert_current_ipa(self, event):
        ipa = self.editor.header_panel.ipa_input.GetValue().strip()
        if ipa:
            self._insert_phoneme(ipa)
            self.editor.set_status(f"Inserted [{ipa}]")
        else:
            self.editor.set_status("No IPA symbol to insert")


class ViewPanel(wx.Panel):
    """Tab panel with read-only parameter views."""

    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor = editor
        self._create_widgets()

    def _create_widgets(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Sub-notebook for different views
        self.sub_notebook = wx.Notebook(self)

        # Python Dict view
        self.dict_panel = wx.Panel(self.sub_notebook)
        dict_sizer = wx.BoxSizer(wx.VERTICAL)
        self.dict_text = wx.TextCtrl(self.dict_panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        font = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.dict_text.SetFont(font)
        dict_sizer.Add(self.dict_text, 1, wx.EXPAND | wx.ALL, 5)
        self.dict_panel.SetSizer(dict_sizer)
        self.sub_notebook.AddPage(self.dict_panel, "Python Dict")

        # Table view
        self.table_panel = wx.Panel(self.sub_notebook)
        table_sizer = wx.BoxSizer(wx.VERTICAL)
        self.table_list = wx.ListCtrl(self.table_panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.table_list.InsertColumn(0, "Parameter", width=150)
        self.table_list.InsertColumn(1, "Value", width=100)
        self.table_list.InsertColumn(2, "Unit", width=60)
        self.table_list.InsertColumn(3, "Group", width=150)
        table_sizer.Add(self.table_list, 1, wx.EXPAND | wx.ALL, 5)
        self.table_panel.SetSizer(table_sizer)
        self.sub_notebook.AddPage(self.table_panel, "Table View")

        main_sizer.Add(self.sub_notebook, 1, wx.EXPAND | wx.ALL, 5)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.refresh_btn = wx.Button(self, label="&Refresh")
        btn_sizer.Add(self.refresh_btn, 0, wx.RIGHT, 10)

        self.copy_btn = wx.Button(self, label="&Copy to Clipboard")
        btn_sizer.Add(self.copy_btn, 0)

        main_sizer.Add(btn_sizer, 0, wx.ALL, 10)

        self.SetSizer(main_sizer)

        # Bind events
        self.refresh_btn.Bind(wx.EVT_BUTTON, self._on_refresh)
        self.copy_btn.Bind(wx.EVT_BUTTON, self._on_copy)

    def _on_refresh(self, event):
        self.refresh_views()
        self.editor.set_status("View refreshed")

    def refresh_views(self):
        # Get current preset data
        preset_data = self.editor.build_preset_data()
        params = preset_data.get('parameters', {})

        # Update dict view
        code = self.editor.preset_manager.export_to_data_py(preset_data)
        self.dict_text.SetValue(code)

        # Update table view
        self.table_list.DeleteAllItems()
        for group_name, group_params in PARAM_GROUPS.items():
            for param_name, min_val, max_val, default, unit, desc in group_params:
                idx = self.table_list.InsertItem(self.table_list.GetItemCount(), param_name)
                value = params.get(param_name, default)
                self.table_list.SetItem(idx, 1, f"{value:.4f}" if isinstance(value, float) else str(value))
                self.table_list.SetItem(idx, 2, unit)
                self.table_list.SetItem(idx, 3, group_name)

    def _on_copy(self, event):
        preset_data = self.editor.build_preset_data()
        code = self.editor.preset_manager.export_to_data_py(preset_data)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(code))
            wx.TheClipboard.Close()
            self.editor.set_status("Copied to clipboard")
        else:
            wx.MessageBox("Could not access clipboard", "Error", wx.OK | wx.ICON_ERROR)


class FileExportPanel(wx.Panel):
    """Tab panel for file operations."""

    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor = editor
        self._create_widgets()

    def _create_widgets(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Save section
        save_box = wx.StaticBox(self, label="Save Preset")
        save_sizer = wx.StaticBoxSizer(save_box, wx.VERTICAL)

        self.save_btn = wx.Button(self, label="&Save to presets/ folder")
        self.save_btn.SetToolTip("Save current preset as JSON to presets/ folder")
        save_sizer.Add(self.save_btn, 0, wx.ALL | wx.EXPAND, 10)

        main_sizer.Add(save_sizer, 0, wx.ALL | wx.EXPAND, 10)

        # Export section
        export_box = wx.StaticBox(self, label="Export")
        export_sizer = wx.StaticBoxSizer(export_box, wx.VERTICAL)

        self.export_dict_btn = wx.Button(self, label="&Export as Python dict (to clipboard)")
        export_sizer.Add(self.export_dict_btn, 0, wx.ALL | wx.EXPAND, 10)

        self.export_json_btn = wx.Button(self, label="Export as &JSON file...")
        export_sizer.Add(self.export_json_btn, 0, wx.ALL | wx.EXPAND, 10)

        main_sizer.Add(export_sizer, 0, wx.ALL | wx.EXPAND, 10)

        # Open section
        open_box = wx.StaticBox(self, label="Open")
        open_sizer = wx.StaticBoxSizer(open_box, wx.VERTICAL)

        self.open_btn = wx.Button(self, label="&Open preset file...")
        open_sizer.Add(self.open_btn, 0, wx.ALL | wx.EXPAND, 10)

        self.new_btn = wx.Button(self, label="&New preset (reset to schwa)")
        new_sizer_add = open_sizer.Add(self.new_btn, 0, wx.ALL | wx.EXPAND, 10)

        main_sizer.Add(open_sizer, 0, wx.ALL | wx.EXPAND, 10)

        self.SetSizer(main_sizer)


# =============================================================================
# MAIN FRAME
# =============================================================================

class PhonemeEditorFrame(wx.Frame):
    """Main application frame with tab-based interface."""

    def __init__(self):
        super().__init__(
            parent=None,
            title="Phoneme Parameter Editor",
            size=(1000, 800)
        )

        self.sample_rate = 44100
        self.is_playing = False
        self.play_thread = None
        self.preset_manager = PresetManager()

        # Diphthong components (if current phoneme is a diphthong)
        self._diphthong_components = None

        # IPA keyboard state
        self._last_ipa_key = None
        self._last_ipa_time = 0
        self._ipa_press_count = 0
        self._cycle_timeout = 0.5

        self._create_menu_bar()
        self._create_main_layout()
        self._bind_events()

        self.Centre()
        self.set_status("Ready. Use tabs to navigate. F5 to play, F6 for sequence.")

    def _create_menu_bar(self):
        menu_bar = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()
        new_item = file_menu.Append(wx.ID_NEW, "&New Preset\tCtrl+N")
        open_item = file_menu.Append(wx.ID_OPEN, "&Open Preset\tCtrl+O")
        save_item = file_menu.Append(wx.ID_SAVE, "&Save Preset\tCtrl+S")
        file_menu.AppendSeparator()
        export_item = file_menu.Append(wx.ID_ANY, "&Export as Python dict\tCtrl+E")
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, "E&xit\tAlt+F4")
        menu_bar.Append(file_menu, "&File")

        # Presets menu
        presets_menu = wx.Menu()
        self._populate_presets_menu(presets_menu)
        menu_bar.Append(presets_menu, "P&resets")

        # Help menu
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "&About")
        menu_bar.Append(help_menu, "&Help")

        self.SetMenuBar(menu_bar)

        # Bind menu events
        self.Bind(wx.EVT_MENU, self.on_new, new_item)
        self.Bind(wx.EVT_MENU, self.on_open, open_item)
        self.Bind(wx.EVT_MENU, self.on_save, save_item)
        self.Bind(wx.EVT_MENU, self.on_export, export_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

    def _populate_presets_menu(self, presets_menu):
        # Helper to add phonemes to a menu
        def add_phonemes_to_menu(menu, phonemes):
            for ipa, params in sorted(phonemes.items(), key=lambda x: x[0]):
                if not isinstance(params, dict):
                    continue
                desc = IPA_DESCRIPTIONS.get(ipa, '')
                label = f"{ipa} - {desc}" if desc else ipa

                # Create submenu with Load Full and Load to Current options
                phoneme_submenu = wx.Menu()
                full_item = phoneme_submenu.Append(wx.ID_ANY, "Load Full")
                current_item = phoneme_submenu.Append(wx.ID_ANY, "Load to Current")

                self.Bind(wx.EVT_MENU, lambda e, i=ipa, p=params: self.load_phoneme_full(i, p), full_item)
                self.Bind(wx.EVT_MENU, lambda e, i=ipa, p=params: self.load_to_current(p), current_item)

                menu.AppendSubMenu(phoneme_submenu, label)

        # Group vowel categories under Vowels menu
        vowel_categories = [c for c in CATEGORY_ORDER if c.startswith('Vowels')]
        other_categories = [c for c in CATEGORY_ORDER if not c.startswith('Vowels')]

        # Add Vowels menu with sub-menus
        if vowel_categories:
            vowels_menu = wx.Menu()
            for cat_name in vowel_categories:
                phonemes = PHONEME_CATEGORIES.get(cat_name, {})
                if not phonemes:
                    continue
                # Remove "Vowels - " prefix for cleaner display
                display_name = cat_name.replace('Vowels - ', '')
                submenu = wx.Menu()
                add_phonemes_to_menu(submenu, phonemes)
                vowels_menu.AppendSubMenu(submenu, f"&{display_name}")
            presets_menu.AppendSubMenu(vowels_menu, "&Vowels")

        # Add other categories at root level
        for cat_name in other_categories:
            phonemes = PHONEME_CATEGORIES.get(cat_name, {})
            if not phonemes:
                continue
            submenu = wx.Menu()
            add_phonemes_to_menu(submenu, phonemes)
            presets_menu.AppendSubMenu(submenu, f"&{cat_name}")

    def _create_main_layout(self):
        main_panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Header panel (always visible)
        self.header_panel = HeaderPanel(main_panel, self)
        main_sizer.Add(self.header_panel, 0, wx.EXPAND | wx.ALL, 5)

        # Separator
        main_sizer.Add(wx.StaticLine(main_panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        # Main notebook for tabs
        self.notebook = wx.Notebook(main_panel)

        # Tab 1: Parameters
        self.params_panel = ParametersPanel(self.notebook, self)
        self.notebook.AddPage(self.params_panel, "&Parameters")

        # Tab 2: Presets
        self.presets_panel = PresetsPanel(self.notebook, self)
        self.notebook.AddPage(self.presets_panel, "P&resets")

        # Tab 3: Sequence Testing
        self.sequence_panel = SequenceTestingPanel(self.notebook, self)
        self.notebook.AddPage(self.sequence_panel, "&Sequence")

        # Tab 4: View
        self.view_panel = ViewPanel(self.notebook, self)
        self.notebook.AddPage(self.view_panel, "&View")

        # Tab 5: File
        self.file_panel = FileExportPanel(self.notebook, self)
        self.notebook.AddPage(self.file_panel, "&File")

        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)

        main_panel.SetSizer(main_sizer)

        # Status bar
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetName("Status")

    def _bind_events(self):
        # Header panel buttons
        self.header_panel.play_btn.Bind(wx.EVT_BUTTON, self.on_play)
        self.header_panel.stop_btn.Bind(wx.EVT_BUTTON, self.on_stop)
        self.header_panel.ref_btn.Bind(wx.EVT_BUTTON, self.on_play_reference)

        # Parameters panel
        self.params_panel.reset_btn.Bind(wx.EVT_BUTTON, self.on_reset)

        # Sequence panel
        self.sequence_panel.play_seq_btn.Bind(wx.EVT_BUTTON, self.on_play_sequence)

        # File panel
        self.file_panel.save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        self.file_panel.export_dict_btn.Bind(wx.EVT_BUTTON, self.on_export)
        self.file_panel.export_json_btn.Bind(wx.EVT_BUTTON, self.on_export_json)
        self.file_panel.open_btn.Bind(wx.EVT_BUTTON, self.on_open)
        self.file_panel.new_btn.Bind(wx.EVT_BUTTON, self.on_new)

        # Keyboard shortcuts
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

        # Custom events
        self.Bind(EVT_STATUS_UPDATE, self.on_status_update)
        self.Bind(EVT_PLAY_DONE, self.on_play_done)

        self.Bind(wx.EVT_CLOSE, self.on_close)

    # =========================================================================
    # PROPERTY ACCESSORS FOR BACKWARD COMPATIBILITY
    # =========================================================================

    @property
    def sliders(self):
        return self.params_panel.sliders

    @property
    def value_labels(self):
        return self.params_panel.value_labels

    @property
    def ipa_input(self):
        return self.header_panel.ipa_input

    @property
    def desc_input(self):
        return self.header_panel.desc_input

    @property
    def category_choice(self):
        return self.header_panel.category_choice

    @property
    def is_vowel_cb(self):
        return self.header_panel.is_vowel_cb

    @property
    def is_voiced_cb(self):
        return self.header_panel.is_voiced_cb

    @property
    def sequence_input(self):
        return self.sequence_panel.sequence_input

    # =========================================================================
    # CORE METHODS
    # =========================================================================

    def get_frame_params(self):
        return self.params_panel.get_frame_params()

    def set_frame_params(self, params, apply_klsyn88_defaults=True):
        self.params_panel.set_frame_params(params, apply_klsyn88_defaults)

    def build_preset_data(self):
        # Get all params then filter out prosody params (pitch, vibrato, gain)
        # These are speaker/intonation properties, not phoneme-intrinsic
        all_params = self.get_frame_params()
        phoneme_params = {k: v for k, v in all_params.items()
                         if k not in PROSODY_PARAMS}
        return {
            'ipa': self.ipa_input.GetValue().strip() or 'x',
            'name': self.ipa_input.GetValue().strip() or 'x',
            'category': self.category_choice.GetStringSelection(),
            'description': self.desc_input.GetValue(),
            'isVowel': self.is_vowel_cb.GetValue(),
            'isVoiced': self.is_voiced_cb.GetValue(),
            'parameters': phoneme_params
        }

    def load_phoneme_full(self, ipa, params):
        """Load phoneme with all metadata.

        Filters out prosody params (pitch, vibrato, gain) - these are
        speaker/intonation properties, not phoneme-intrinsic.
        """
        self.ipa_input.SetValue(ipa)
        self.is_vowel_cb.SetValue(params.get('_isVowel', False))
        self.is_voiced_cb.SetValue(params.get('_isVoiced', False))
        self.desc_input.SetValue(IPA_DESCRIPTIONS.get(ipa, ''))

        # Store diphthong components for glide playback
        self._diphthong_components = params.get('_components')

        # Determine category
        if params.get('_isDiphthong'):
            cat = 'vowel'  # Diphthongs are vowel-like
        elif params.get('_isVowel'):
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

        # Filter internal flags and prosody params
        clean_params = {k: v for k, v in params.items()
                       if not k.startswith('_') and k not in PROSODY_PARAMS}
        self.set_frame_params(clean_params)

        desc = IPA_DESCRIPTIONS.get(ipa, '')
        diph_info = " (diphthong)" if self._diphthong_components else ""
        self.set_status(f"Loaded: {ipa}{diph_info}" + (f" - {desc}" if desc else ""))

    def load_to_current(self, params):
        """Load only parameters, preserve current metadata.

        Filters out:
        - Internal flags (starting with '_')
        - Prosody params (pitch, vibrato, gain) - these are speaker/intonation properties
        """
        # Update diphthong components if present
        self._diphthong_components = params.get('_components')

        clean_params = {k: v for k, v in params.items()
                       if not k.startswith('_') and k not in PROSODY_PARAMS}
        self.set_frame_params(clean_params)
        diph_info = " (diphthong)" if self._diphthong_components else ""
        self.set_status(f"Parameters loaded{diph_info} (metadata preserved)")

    def load_preset_file(self, filepath, update_metadata=True):
        """Load a preset from JSON file.

        Filters out prosody params (pitch, vibrato, gain) from old presets
        that may have incorrectly saved these speaker/intonation properties.
        """
        try:
            data = self.preset_manager.load_preset(filepath)
            if update_metadata:
                self.ipa_input.SetValue(data.get('ipa', ''))
                self.desc_input.SetValue(data.get('description', ''))
                cat = data.get('category', 'vowel')
                idx = self.category_choice.FindString(cat)
                if idx != wx.NOT_FOUND:
                    self.category_choice.SetSelection(idx)
                self.is_vowel_cb.SetValue(data.get('isVowel', False))
                self.is_voiced_cb.SetValue(data.get('isVoiced', False))

            if 'parameters' in data:
                # Filter out prosody params from old presets
                clean_params = {k: v for k, v in data['parameters'].items()
                               if k not in PROSODY_PARAMS}
                self.set_frame_params(clean_params)

            mode = "full" if update_metadata else "parameters only"
            self.set_status(f"Loaded ({mode}): {os.path.basename(str(filepath))}")
        except Exception as e:
            wx.MessageBox(f"Error loading preset: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def set_status(self, message):
        if wx.IsMainThread():
            self.status_bar.SetStatusText(message)
        else:
            wx.PostEvent(self, StatusUpdateEvent(message=message))

    def on_status_update(self, event):
        self.status_bar.SetStatusText(event.message)

    # =========================================================================
    # KEYBOARD HANDLING
    # =========================================================================

    def on_key(self, event):
        key = event.GetKeyCode()

        # IPA keyboard in sequence input
        if event.AltDown() and self.sequence_input.HasFocus():
            if self._handle_ipa_key(key):
                return

        # Global shortcuts
        if key == wx.WXK_F5 and not self.is_playing:
            self.on_play(None)
        elif key == wx.WXK_F6 and not self.is_playing:
            self.on_play_sequence(None)
        elif key == wx.WXK_F7:
            self.on_play_reference(None)
        elif key == wx.WXK_ESCAPE:
            self.on_stop(None)
        else:
            event.Skip()

    def _handle_ipa_key(self, key_code):
        if 65 <= key_code <= 90:
            lookup_key = chr(key_code).lower()
        elif 97 <= key_code <= 122:
            lookup_key = chr(key_code)
        elif 48 <= key_code <= 57:
            lookup_key = chr(key_code)
        else:
            return False

        current_time = time.time()
        if lookup_key == self._last_ipa_key and (current_time - self._last_ipa_time) < self._cycle_timeout:
            self._ipa_press_count += 1
            text = self.sequence_input.GetValue()
            pos = self.sequence_input.GetInsertionPoint()
            if pos > 0 and text[pos-1:pos] == ']':
                bracket_start = text.rfind('[', 0, pos-1)
                if bracket_start >= 0:
                    self.sequence_input.Remove(bracket_start, pos)
        else:
            self._ipa_press_count = 1

        self._last_ipa_key = lookup_key
        self._last_ipa_time = current_time

        result = ipa_keyboard.get_symbol_for_key(lookup_key, self._ipa_press_count)
        if result:
            symbol, description = result
            self.sequence_input.WriteText(f"[{symbol}]")
            self.set_status(f"Inserted: {symbol} ({description})")
            return True
        return False

    # =========================================================================
    # PLAYBACK METHODS
    # =========================================================================

    def create_frame(self):
        frame = speechPlayer.Frame()
        params = self.get_frame_params()
        for name, value in params.items():
            if hasattr(frame, name):
                setattr(frame, name, value)
        return frame

    def apply_formant_scaling(self, frame, scale_factor):
        if scale_factor == 1.0:
            return
        for i in range(1, 7):
            for prefix in ['cf', 'cb', 'pf', 'pb']:
                name = f'{prefix}{i}'
                val = getattr(frame, name, 0)
                if val > 0:
                    setattr(frame, name, val * scale_factor)
        for name in ['cfNP', 'cbNP', 'cfN0', 'cbN0']:
            val = getattr(frame, name, 0)
            if val > 0:
                setattr(frame, name, val * scale_factor)

    def _play_thread(self, frame, duration_ms, formant_scale=1.0):
        try:
            self.apply_formant_scaling(frame, formant_scale)
            scale_info = f", scale={formant_scale:.2f}" if formant_scale != 1.0 else ""
            self.set_status(f"Playing: pitch={frame.voicePitch:.0f}Hz, F1={frame.cf1:.0f}{scale_info}")

            sp = speechPlayer.SpeechPlayer(self.sample_rate)
            if frame.voicePitch < 25:
                frame.voicePitch = 100
            if frame.endVoicePitch < 25:
                frame.endVoicePitch = frame.voicePitch
            if frame.preFormantGain <= 0:
                frame.preFormantGain = 1.0
            if frame.outputGain <= 0:
                frame.outputGain = 1.0

            sp.queueFrame(frame, duration_ms, min(50, duration_ms // 2))
            sp.queueFrame(None, 50, 20)

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
            wx.PostEvent(self, PlayDoneEvent())

    def _play_diphthong_thread(self, components, duration_ms, formant_scale=1.0):
        """Play diphthong as gliding sequence of component vowels."""
        try:
            component_names = ', '.join(components)
            self.set_status(f"Playing diphthong: {component_names}")

            sp = speechPlayer.SpeechPlayer(self.sample_rate)

            # Get formant data for each component vowel
            frames = []
            for vowel_char in components:
                vowel_data = PHONEME_DATA.get(vowel_char, {})
                if not vowel_data:
                    continue
                frame = speechPlayer.Frame()
                frame.preFormantGain = 1.0
                frame.outputGain = 2.0
                frame.voicePitch = 120
                frame.endVoicePitch = 120
                frame.voiceAmplitude = 1.0
                ipa.applyPhonemeToFrame(frame, vowel_data)
                self.apply_formant_scaling(frame, formant_scale)
                frames.append(frame)

            if not frames:
                self.set_status("Error: No valid component vowels found")
                return

            # Calculate timing for glide
            # First component: 40% of duration, 15ms fade
            # Subsequent: remaining time split, with long fade for glide
            first_duration = int(duration_ms * 0.4)
            remaining_duration = duration_ms - first_duration
            subsequent_duration = remaining_duration // max(1, len(frames) - 1) if len(frames) > 1 else remaining_duration

            for i, frame in enumerate(frames):
                if i == 0:
                    # First component: quick onset
                    sp.queueFrame(frame, first_duration, 15)
                else:
                    # Subsequent components: long glide fade
                    glide_fade = min(subsequent_duration - 5, 50)  # Up to 50ms fade
                    sp.queueFrame(frame, subsequent_duration, glide_fade)

            sp.queueFrame(None, 50, 20)  # Fade out

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
            wx.PostEvent(self, PlayDoneEvent())

    def on_play(self, event):
        if self.is_playing:
            return
        self.is_playing = True
        self.header_panel.play_btn.Enable(False)
        self.header_panel.stop_btn.Enable(True)

        duration = self.header_panel.duration_slider.GetValue()
        formant_scale = self.header_panel.formant_slider.GetValue() / 100.0

        # Check if this is a diphthong with components
        if self._diphthong_components:
            self.play_thread = threading.Thread(
                target=self._play_diphthong_thread,
                args=(self._diphthong_components, duration, formant_scale),
                daemon=True
            )
        else:
            frame = self.create_frame()
            self.play_thread = threading.Thread(
                target=self._play_thread,
                args=(frame, duration, formant_scale),
                daemon=True
            )
        self.play_thread.start()

    def on_stop(self, event):
        if self.is_playing:
            self.is_playing = False
            if HAS_WINSOUND:
                winsound.PlaySound(None, winsound.SND_PURGE)
            self.set_status("Stopped.")
            self.header_panel.play_btn.Enable(True)
            self.header_panel.stop_btn.Enable(False)

    def on_play_done(self, event):
        self.is_playing = False
        self.header_panel.play_btn.Enable(True)
        self.header_panel.stop_btn.Enable(False)
        self.sequence_panel.play_seq_btn.Enable(True)

    def on_play_reference(self, event):
        """Play human-recorded reference sample for current IPA symbol."""
        ipa = self.ipa_input.GetValue().strip()
        if not ipa:
            self.set_status("No IPA symbol to look up")
            return

        # Find the sample file
        samples_dir = Path(__file__).parent / "samples"
        if len(ipa) == 1:
            codepoint = f"{ord(ipa):04X}"
        else:
            codepoint = '_'.join(f"{ord(c):04X}" for c in ipa)

        wav_path = samples_dir / f"{codepoint}_{ipa}.wav"
        ogg_path = samples_dir / f"{codepoint}_{ipa}.ogg"

        # Try WAV first (instant playback with winsound)
        if wav_path.exists() and HAS_WINSOUND:
            try:
                winsound.PlaySound(str(wav_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
                self.set_status(f"Reference: [{ipa}]")
                return
            except Exception as e:
                self.set_status(f"winsound error: {e}")

        # Fall back to OGG with pygame
        if ogg_path.exists():
            try:
                import pygame
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(str(ogg_path))
                pygame.mixer.music.play()
                self.set_status(f"Reference: [{ipa}] (OGG)")
                return
            except ImportError:
                pass
            except Exception as e:
                self.set_status(f"pygame error: {e}")

            # Last resort: system player for OGG
            try:
                import subprocess
                import sys
                if sys.platform == 'win32':
                    subprocess.Popen(['start', '', str(ogg_path)], shell=True)
                    self.set_status(f"Reference: [{ipa}] (system player)")
                    return
            except Exception:
                pass

            self.set_status(f"OGG found but can't play. Run: python download_ipa_samples.py --convert")
            return

        # No sample found
        self.set_status(f"No reference for [{ipa}]. Run: python download_ipa_samples.py")

    # =========================================================================
    # SEQUENCE PLAYBACK
    # =========================================================================

    def _parse_test_sequence(self, sequence_str):
        phonemes = []
        matches = re.findall(r'\[([^\]]+)\]', sequence_str)
        for phoneme_key in matches:
            if phoneme_key == '*':
                current_params = self.get_frame_params()
                current_params['_isVowel'] = self.is_vowel_cb.GetValue()
                current_params['_isVoiced'] = self.is_voiced_cb.GetValue()
                category = self.category_choice.GetStringSelection()
                current_params['_isStop'] = (category == 'stop')
                current_params['_isNasal'] = (category == 'nasal')
                phonemes.append(('*', current_params))
            elif preset_params := self.preset_manager.find_preset_by_ipa(phoneme_key):
                phonemes.append((phoneme_key, preset_params))
            elif phoneme_key in PHONEME_DATA:
                phonemes.append((phoneme_key, PHONEME_DATA[phoneme_key]))
            else:
                self.set_status(f"Unknown phoneme: {phoneme_key}")
                return None
        return phonemes

    def _create_frame_from_phoneme(self, params):
        frame = speechPlayer.Frame()
        frame.voicePitch = 100
        frame.midVoicePitch = 0
        frame.endVoicePitch = 100
        frame.preFormantGain = 1.0
        frame.outputGain = 1.0
        for name, value in KLSYN88_DEFAULTS.items():
            if hasattr(frame, name):
                setattr(frame, name, value)
        for name, value in params.items():
            if not name.startswith('_') and hasattr(frame, name):
                setattr(frame, name, value)
        return frame

    def _play_test_sequence_thread(self, phoneme_list, formant_scale=1.0):
        try:
            self.set_status(f"Playing sequence of {len(phoneme_list)} phonemes...")
            sp = speechPlayer.SpeechPlayer(self.sample_rate)

            for phoneme_key, params in phoneme_list:
                frame = self._create_frame_from_phoneme(params)
                self.apply_formant_scaling(frame, formant_scale)
                duration = SEQUENCE_DURATIONS['vowel'] if params.get('_isVowel') else SEQUENCE_DURATIONS['consonant']
                sp.queueFrame(frame, duration, min(30, duration // 3))

            sp.queueFrame(None, 50, 20)

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
            wx.PostEvent(self, PlayDoneEvent())

    def on_play_sequence(self, event):
        if self.is_playing:
            return
        sequence_str = self.sequence_input.GetValue().strip()
        if not sequence_str:
            self.set_status("No sequence to play.")
            return

        phoneme_list = self._parse_test_sequence(sequence_str)
        if phoneme_list is None:
            return
        if not phoneme_list:
            self.set_status("No valid phonemes in sequence.")
            return

        self.is_playing = True
        self.header_panel.play_btn.Enable(False)
        self.sequence_panel.play_seq_btn.Enable(False)
        self.header_panel.stop_btn.Enable(True)

        formant_scale = self.header_panel.formant_slider.GetValue() / 100.0
        self.play_thread = threading.Thread(
            target=self._play_test_sequence_thread,
            args=(phoneme_list, formant_scale),
            daemon=True
        )
        self.play_thread.start()

    # =========================================================================
    # FILE OPERATIONS
    # =========================================================================

    def on_new(self, event):
        self.on_reset(event)
        self._diphthong_components = None  # Clear diphthong state
        self.ipa_input.SetValue('ə')
        self.desc_input.SetValue('mid central (schwa)')
        idx = self.category_choice.FindString('vowel')
        if idx != wx.NOT_FOUND:
            self.category_choice.SetSelection(idx)
        self.is_vowel_cb.SetValue(True)
        self.is_voiced_cb.SetValue(True)
        self.set_status("New preset - reset to schwa (ə)")

    def on_reset(self, event):
        self._diphthong_components = None  # Clear diphthong state
        for name, (slider, min_val, max_val, default, unit) in self.sliders.items():
            value = SCHWA_DEFAULTS.get(name, default)
            value = max(min_val, min(max_val, int(value)))
            slider.SetValue(value)
            self.value_labels[name].SetLabel(f"{value} {unit}")
        self.set_status("Parameters reset to schwa defaults")

    def on_open(self, event):
        with wx.FileDialog(self, "Open Preset",
                          wildcard="JSON files (*.json)|*.json|All files (*.*)|*.*",
                          style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() != wx.ID_CANCEL:
                self.load_preset_file(dlg.GetPath(), update_metadata=True)

    def on_save(self, event):
        ipa = self.ipa_input.GetValue().strip()
        if not ipa:
            wx.MessageBox("Please enter an IPA symbol.", "Missing IPA", wx.OK | wx.ICON_WARNING)
            self.ipa_input.SetFocus()
            return
        try:
            filepath = self.preset_manager.save_preset(self.build_preset_data())
            self.set_status(f"Saved: {filepath.name}")
            # Refresh presets panel
            self.presets_panel._populate_preset_list()
        except Exception as e:
            wx.MessageBox(f"Error saving preset: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def on_export(self, event):
        code = self.preset_manager.export_to_data_py(self.build_preset_data())
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(code))
            wx.TheClipboard.Close()
            self.set_status("Copied to clipboard as Python dict.")
        else:
            wx.MessageBox("Could not access clipboard.", "Error", wx.OK | wx.ICON_ERROR)

    def on_export_json(self, event):
        with wx.FileDialog(self, "Export as JSON",
                          wildcard="JSON files (*.json)|*.json",
                          style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() != wx.ID_CANCEL:
                try:
                    with open(dlg.GetPath(), 'w', encoding='utf-8') as f:
                        json.dump(self.build_preset_data(), f, indent=2, ensure_ascii=False)
                    self.set_status(f"Exported: {os.path.basename(dlg.GetPath())}")
                except Exception as e:
                    wx.MessageBox(f"Error exporting: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def on_about(self, event):
        wx.MessageBox(
            "Phoneme Parameter Editor\n\n"
            "Tab-based Klatt synthesis parameter editor.\n"
            "All 47 parameters exposed for creating phoneme presets.\n\n"
            "Features:\n"
            "- Parameters: Edit all synthesis parameters\n"
            "- Presets: Browse and load from PHONEME_DATA or saved presets\n"
            "- Sequence: Test phonemes in context\n"
            "- View: Read-only parameter display\n"
            "- File: Save/export operations\n\n"
            "Based on NVSpeechPlayer by NV Access Limited\n"
            "License: GPL v2",
            "About",
            wx.OK | wx.ICON_INFORMATION
        )

    def on_exit(self, event):
        self.Close()

    def on_close(self, event):
        if self.is_playing:
            self.is_playing = False
            if HAS_WINSOUND:
                winsound.PlaySound(None, winsound.SND_PURGE)
        event.Skip()


def main():
    app = wx.App()
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
