#!python3
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

import sys
from pathlib import Path

# Add parent directory to path for imports from main package
_EDITOR_DIR = Path(__file__).parent
_ROOT_DIR = _EDITOR_DIR.parent
sys.path.insert(0, str(_ROOT_DIR))

import wx
import wx.lib.newevent
import threading
import wave
import struct
import tempfile
import os
import json
import time
import re

# Import synthesis modules from parent directory
import speechPlayer
import ipa

# Import local editor modules
import ipa_keyboard
from phoneme_editor_constants import (
    PROSODY_PARAMS, PARAM_GROUPS, PERCENT_PARAMS, GAIN_PARAMS, TENTH_PARAMS,
    KLSYN88_DEFAULTS, IPA_DESCRIPTIONS, SEQUENCE_DURATIONS
)
from phoneme_editor_panels import (
    HeaderPanel, ParametersPanel, PresetsPanel,
    SequenceTestingPanel, ViewPanel, FileExportPanel,
    PhonemizeDialog, ID_LOAD_AND_SAVE
)

# Load phoneme data from parent's data package
from data import data as PHONEME_DATA, PHONEME_CATEGORIES, CATEGORY_ORDER

# Schwa (ə) defaults for reset - the neutral mid-central vowel
SCHWA_DEFAULTS = PHONEME_DATA.get('ə', {})

# For audio playback
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

# For live preview streaming audio
try:
    import sounddevice as sd
    HAS_SOUNDDEVICE = True
except ImportError:
    HAS_SOUNDDEVICE = False

# Custom events
StatusUpdateEvent, EVT_STATUS_UPDATE = wx.lib.newevent.NewEvent()
PlayDoneEvent, EVT_PLAY_DONE = wx.lib.newevent.NewEvent()


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

        # Live preview state
        self.is_live_preview = False
        self._live_sp = None       # SpeechPlayer instance for live preview
        self._live_stream = None   # sounddevice.OutputStream

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
        self.header_panel.live_btn.Bind(wx.EVT_BUTTON, self.on_toggle_live_preview)

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
        if self.is_live_preview:
            self._queue_live_frame()

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

    def on_phonemize(self):
        """Resolve IPA text through diacritic pipeline and show results."""
        ipa_text = self.ipa_input.GetValue().strip()
        if not ipa_text:
            self.set_status("Enter IPA text to phonemize")
            return

        results = ipa.resolve_ipa_phoneme(ipa_text)
        if not results:
            self.set_status(f"Could not resolve: {ipa_text}")
            return

        dlg = PhonemizeDialog(self, ipa_text, results)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            selected = dlg.get_selected()
            self.load_phoneme_full(selected['char'], selected['params'])
        elif result == ID_LOAD_AND_SAVE:
            selected = dlg.get_selected()
            self.load_phoneme_full(selected['char'], selected['params'])
            self.on_save(None)
        dlg.Destroy()

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
        elif key == wx.WXK_F8:
            self.on_toggle_live_preview(None)
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
    # LIVE PREVIEW
    # =========================================================================

    def on_toggle_live_preview(self, event):
        """Toggle live audio preview on/off (F8)."""
        if not HAS_SOUNDDEVICE:
            wx.MessageBox(
                "Live preview requires the sounddevice package.\n\n"
                "Install it with: pip install sounddevice",
                "Missing dependency",
                wx.OK | wx.ICON_INFORMATION
            )
            return
        if self.is_live_preview:
            self._stop_live_preview()
        else:
            self._start_live_preview()

    def _start_live_preview(self):
        """Start streaming live audio from the current slider parameters."""
        # Stop batch playback first if active
        if self.is_playing:
            self.on_stop(None)

        self._live_sp = speechPlayer.SpeechPlayer(self.sample_rate)
        self._queue_live_frame()

        def audio_callback(outdata, frames, time_info, status):
            samples = self._live_sp.synthesize(frames)
            if samples and hasattr(samples, 'length') and samples.length > 0:
                count = min(samples.length, frames)
                for i in range(count):
                    outdata[i][0] = samples[i]
                for i in range(count, frames):
                    outdata[i][0] = 0
            elif samples:
                count = min(len(samples), frames)
                for i in range(count):
                    outdata[i][0] = samples[i]
                for i in range(count, frames):
                    outdata[i][0] = 0
            else:
                # No samples — output silence and re-queue frame
                for i in range(frames):
                    outdata[i][0] = 0
                wx.CallAfter(self._queue_live_frame)

        self._live_stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='int16',
            blocksize=1024,
            callback=audio_callback,
        )
        self._live_stream.start()

        self.is_live_preview = True
        self.header_panel.play_btn.Enable(False)
        self.header_panel.live_btn.SetLabel("Stop Live")
        self.set_status("Live preview ON — adjust sliders to hear changes")

    def _stop_live_preview(self):
        """Stop the live audio stream and clean up."""
        self.is_live_preview = False
        if self._live_stream is not None:
            self._live_stream.stop()
            self._live_stream.close()
            self._live_stream = None
        self._live_sp = None
        self.header_panel.play_btn.Enable(True)
        self.header_panel.live_btn.SetLabel("Live (F8)")
        self.set_status("Live preview OFF")

    def _queue_live_frame(self):
        """Read current sliders and queue a long frame for continuous playback."""
        if not self.is_live_preview or self._live_sp is None:
            return
        frame = self.create_frame()
        formant_scale = self.header_panel.formant_slider.GetValue() / 100.0
        self.apply_formant_scaling(frame, formant_scale)
        # Safety defaults for continuous playback
        if frame.voicePitch < 25:
            frame.voicePitch = 100
        if frame.endVoicePitch < 25:
            frame.endVoicePitch = frame.voicePitch
        if frame.preFormantGain <= 0:
            frame.preFormantGain = 1.0
        if frame.outputGain <= 0:
            frame.outputGain = 1.0
        self._live_sp.queueFrame(frame, 10000, 50, purgeQueue=True)

    def on_param_changed(self):
        """Called by panels when a parameter slider or formant scale changes."""
        if self.is_live_preview:
            self._queue_live_frame()

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
            first_duration = int(duration_ms * 0.4)
            remaining_duration = duration_ms - first_duration
            subsequent_duration = remaining_duration // max(1, len(frames) - 1) if len(frames) > 1 else remaining_duration

            for i, frame in enumerate(frames):
                if i == 0:
                    sp.queueFrame(frame, first_duration, 15)
                else:
                    glide_fade = min(subsequent_duration - 5, 50)
                    sp.queueFrame(frame, subsequent_duration, glide_fade)

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

    def on_play(self, event):
        if self.is_playing:
            return
        if self.is_live_preview:
            self._stop_live_preview()
        self.is_playing = True
        self.header_panel.play_btn.Enable(False)
        self.header_panel.stop_btn.Enable(True)

        duration = self.header_panel.duration_slider.GetValue()
        formant_scale = self.header_panel.formant_slider.GetValue() / 100.0

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
        if self.is_live_preview:
            self._stop_live_preview()
            return
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
        ipa_symbol = self.ipa_input.GetValue().strip()
        if not ipa_symbol:
            self.set_status("No IPA symbol to look up")
            return

        samples_dir = Path(__file__).parent / "samples"
        if len(ipa_symbol) == 1:
            codepoint = f"{ord(ipa_symbol):04X}"
        else:
            codepoint = '_'.join(f"{ord(c):04X}" for c in ipa_symbol)

        wav_path = samples_dir / f"{codepoint}_{ipa_symbol}.wav"
        ogg_path = samples_dir / f"{codepoint}_{ipa_symbol}.ogg"

        if wav_path.exists() and HAS_WINSOUND:
            try:
                winsound.PlaySound(str(wav_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
                self.set_status(f"Reference: [{ipa_symbol}]")
                return
            except Exception as e:
                self.set_status(f"winsound error: {e}")

        if ogg_path.exists():
            try:
                import pygame
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(str(ogg_path))
                pygame.mixer.music.play()
                self.set_status(f"Reference: [{ipa_symbol}] (OGG)")
                return
            except ImportError:
                pass
            except Exception as e:
                self.set_status(f"pygame error: {e}")

            try:
                import subprocess
                import sys
                if sys.platform == 'win32':
                    subprocess.Popen(['start', '', str(ogg_path)], shell=True)
                    self.set_status(f"Reference: [{ipa_symbol}] (system player)")
                    return
            except Exception:
                pass

            self.set_status(f"OGG found but can't play. Run: python download_ipa_samples.py --convert")
            return

        self.set_status(f"No reference for [{ipa_symbol}]. Run: python download_ipa_samples.py")

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
                phonemes.append((phoneme_key, dict(preset_params)))
            elif phoneme_key in PHONEME_DATA:
                phonemes.append((phoneme_key, dict(PHONEME_DATA[phoneme_key])))
            else:
                self.set_status(f"Unknown phoneme: {phoneme_key}")
                return None

        # Process _copyAdjacent phonemes
        for i, (key, params) in enumerate(phonemes):
            if params.get('_copyAdjacent'):
                adjacent = None
                if i + 1 < len(phonemes):
                    adjacent = phonemes[i + 1][1]
                elif i > 0:
                    adjacent = phonemes[i - 1][1]

                if adjacent:
                    for k, v in adjacent.items():
                        if not k.startswith('_') and k not in params:
                            params[k] = v

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

            for i, (phoneme_key, params) in enumerate(phoneme_list):
                frame = self._create_frame_from_phoneme(params)
                self.apply_formant_scaling(frame, formant_scale)
                duration = SEQUENCE_DURATIONS['vowel'] if params.get('_isVowel') else SEQUENCE_DURATIONS['consonant']
                fade = min(30, duration // 3)
                sp.queueFrame(frame, duration, fade)

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
            self.set_status("Sequence done.")
        except Exception as e:
            self.set_status(f"Error: {e}")
        finally:
            wx.PostEvent(self, PlayDoneEvent())

    def on_play_sequence(self, event):
        if self.is_playing:
            return
        if self.is_live_preview:
            self._stop_live_preview()
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
        self._diphthong_components = None
        self.ipa_input.SetValue('ə')
        self.desc_input.SetValue('mid central (schwa)')
        idx = self.category_choice.FindString('vowel')
        if idx != wx.NOT_FOUND:
            self.category_choice.SetSelection(idx)
        self.is_vowel_cb.SetValue(True)
        self.is_voiced_cb.SetValue(True)
        self.set_status("New preset - reset to schwa (ə)")

    def on_reset(self, event):
        self._diphthong_components = None
        for name, slider in self.sliders.items():
            value = SCHWA_DEFAULTS.get(name, slider.default)
            value = max(slider.min_val, min(slider.max_val, int(value)))
            slider.SetValue(value)
            self.value_labels[name].SetLabel(f"{value} {slider.unit}")
        self.set_status("Parameters reset to schwa defaults")

    def on_open(self, event):
        with wx.FileDialog(self, "Open Preset",
                          wildcard="JSON files (*.json)|*.json|All files (*.*)|*.*",
                          style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() != wx.ID_CANCEL:
                self.load_preset_file(dlg.GetPath(), update_metadata=True)

    def on_save(self, event):
        ipa_symbol = self.ipa_input.GetValue().strip()
        if not ipa_symbol:
            wx.MessageBox("Please enter an IPA symbol.", "Missing IPA", wx.OK | wx.ICON_WARNING)
            self.ipa_input.SetFocus()
            return
        try:
            filepath = self.preset_manager.save_preset(self.build_preset_data())
            # Update saved values tracking for D key restore
            self.params_panel.update_saved_values()
            self.set_status(f"Saved: {filepath.name}")
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
            "Slider shortcuts:\n"
            "- Arrows: 0.1%/1% (with Shift)\n"
            "- PgUp/PgDn: 5%/10% (with Shift)\n"
            "- Home/End: Min/Max\n"
            "- F2: Edit exact value\n"
            "- D: Restore saved | Shift+D: Restore original\n\n"
            "- F8: Toggle live preview (requires sounddevice)\n\n"
            "Based on NVSpeechPlayer by NV Access Limited\n"
            "License: GPL v2",
            "About",
            wx.OK | wx.ICON_INFORMATION
        )

    def on_exit(self, event):
        self.Close()

    def on_close(self, event):
        if self.is_live_preview:
            self._stop_live_preview()
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
