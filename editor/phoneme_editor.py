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
import os
from pathlib import Path

# Add parent directory to path for imports from main package
_EDITOR_DIR = Path(__file__).parent
_ROOT_DIR = _EDITOR_DIR.parent
sys.path.insert(0, str(_ROOT_DIR))

import wx

# Import synthesis modules from parent directory
import ipa

# Import local editor modules
from editor_events import EVT_STATUS_UPDATE, EVT_PLAY_DONE, StatusUpdateEvent
from preset_manager import PresetManager
from audio_manager import AudioManager
from keyboard_manager import KeyboardManager
from file_operations import FileOperations
from phoneme_editor_constants import (
    PROSODY_PARAMS, IPA_DESCRIPTIONS
)
from phoneme_editor_panels import (
    HeaderPanel, ParametersPanel, PresetsPanel,
    SequenceTestingPanel, ViewPanel, FileExportPanel,
    PhonemizeDialog, ID_LOAD_AND_SAVE
)

# Load phoneme data from parent's data package
from data import PHONEME_CATEGORIES, CATEGORY_ORDER


# =============================================================================
# MAIN FRAME
# =============================================================================

class PhonemeEditorFrame(wx.Frame):
    """Main application frame with tab-based interface.

    Acts as a thin facade: owns layout and menus, delegates behavior to managers.
    """

    def __init__(self):
        super().__init__(
            parent=None,
            title="Phoneme Parameter Editor",
            size=(1000, 800)
        )

        # Managers
        self.preset_manager = PresetManager()
        self.audio = AudioManager(self)
        self._keyboard = KeyboardManager(self)
        self._file_ops = FileOperations(self)

        # Diphthong components (if current phoneme is a diphthong)
        self._diphthong_components = None

        self._create_menu_bar()
        self._create_main_layout()
        self._bind_events()

        self.Centre()
        self.set_status("Ready. Use tabs to navigate. F5 to play, F6 for sequence.")

    # =========================================================================
    # MENU BAR
    # =========================================================================

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
        self.Bind(wx.EVT_MENU, self._file_ops.on_new, new_item)
        self.Bind(wx.EVT_MENU, self._file_ops.on_open, open_item)
        self.Bind(wx.EVT_MENU, self._file_ops.on_save, save_item)
        self.Bind(wx.EVT_MENU, self._file_ops.on_export, export_item)
        self.Bind(wx.EVT_MENU, self._file_ops.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self._file_ops.on_about, about_item)

    def _populate_presets_menu(self, presets_menu):
        # Helper to add phonemes to a menu
        def add_phonemes_to_menu(menu, phonemes):
            for ipa_char, params in sorted(phonemes.items(), key=lambda x: x[0]):
                if not isinstance(params, dict):
                    continue
                desc = IPA_DESCRIPTIONS.get(ipa_char, '')
                label = f"{ipa_char} - {desc}" if desc else ipa_char

                # Create submenu with Load Full and Load to Current options
                phoneme_submenu = wx.Menu()
                full_item = phoneme_submenu.Append(wx.ID_ANY, "Load Full")
                current_item = phoneme_submenu.Append(wx.ID_ANY, "Load to Current")

                self.Bind(wx.EVT_MENU, lambda e, i=ipa_char, p=params: self.load_phoneme_full(i, p), full_item)
                self.Bind(wx.EVT_MENU, lambda e, i=ipa_char, p=params: self.load_to_current(p), current_item)

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

    # =========================================================================
    # LAYOUT
    # =========================================================================

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

        self.params_panel = ParametersPanel(self.notebook, self)
        self.notebook.AddPage(self.params_panel, "&Parameters")

        self.presets_panel = PresetsPanel(self.notebook, self)
        self.notebook.AddPage(self.presets_panel, "P&resets")

        self.sequence_panel = SequenceTestingPanel(self.notebook, self)
        self.notebook.AddPage(self.sequence_panel, "&Sequence")

        self.view_panel = ViewPanel(self.notebook, self)
        self.notebook.AddPage(self.view_panel, "&View")

        self.file_panel = FileExportPanel(self.notebook, self)
        self.notebook.AddPage(self.file_panel, "&File")

        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)

        main_panel.SetSizer(main_sizer)

        # Status bar
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetName("Status")

    # =========================================================================
    # EVENT BINDING
    # =========================================================================

    def _bind_events(self):
        # Header panel buttons
        self.header_panel.play_btn.Bind(wx.EVT_BUTTON, self.on_play)
        self.header_panel.stop_btn.Bind(wx.EVT_BUTTON, self.on_stop)
        self.header_panel.ref_btn.Bind(wx.EVT_BUTTON, self.on_play_reference)
        self.header_panel.live_btn.Bind(wx.EVT_BUTTON, self.on_toggle_live_preview)

        # Parameters panel
        self.params_panel.reset_btn.Bind(wx.EVT_BUTTON, self._file_ops.on_reset)

        # Sequence panel
        self.sequence_panel.play_seq_btn.Bind(wx.EVT_BUTTON, self.on_play_sequence)

        # File panel
        self.file_panel.save_btn.Bind(wx.EVT_BUTTON, self._file_ops.on_save)
        self.file_panel.export_dict_btn.Bind(wx.EVT_BUTTON, self._file_ops.on_export)
        self.file_panel.export_json_btn.Bind(wx.EVT_BUTTON, self._file_ops.on_export_json)
        self.file_panel.open_btn.Bind(wx.EVT_BUTTON, self._file_ops.on_open)
        self.file_panel.new_btn.Bind(wx.EVT_BUTTON, self._file_ops.on_new)

        # Keyboard shortcuts
        self.Bind(wx.EVT_CHAR_HOOK, self._keyboard.on_key)

        # Custom events
        self.Bind(EVT_STATUS_UPDATE, self._on_status_update)
        self.Bind(EVT_PLAY_DONE, self._on_play_done)

        self.Bind(wx.EVT_CLOSE, self._on_close)

    # =========================================================================
    # PROPERTY ACCESSORS (facade for panels)
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
    # CORE DATA METHODS
    # =========================================================================

    def get_frame_params(self):
        return self.params_panel.get_frame_params()

    def set_frame_params(self, params, apply_klsyn88_defaults=True):
        self.params_panel.set_frame_params(params, apply_klsyn88_defaults)
        if self.audio.is_live_preview:
            self.audio._queue_live_frame()

    def build_preset_data(self):
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

    def load_phoneme_full(self, ipa_char, params):
        """Load phoneme with all metadata."""
        self.ipa_input.SetValue(ipa_char)
        self.is_vowel_cb.SetValue(params.get('_isVowel', False))
        self.is_voiced_cb.SetValue(params.get('_isVoiced', False))
        self.desc_input.SetValue(IPA_DESCRIPTIONS.get(ipa_char, ''))

        self._diphthong_components = params.get('_components')

        if params.get('_isDiphthong'):
            cat = 'vowel'
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

        clean_params = {k: v for k, v in params.items()
                       if not k.startswith('_') and k not in PROSODY_PARAMS}
        self.set_frame_params(clean_params)

        desc = IPA_DESCRIPTIONS.get(ipa_char, '')
        diph_info = " (diphthong)" if self._diphthong_components else ""
        self.set_status(f"Loaded: {ipa_char}{diph_info}" + (f" - {desc}" if desc else ""))

    def load_to_current(self, params):
        """Load only parameters, preserve current metadata."""
        self._diphthong_components = params.get('_components')
        clean_params = {k: v for k, v in params.items()
                       if not k.startswith('_') and k not in PROSODY_PARAMS}
        self.set_frame_params(clean_params)
        diph_info = " (diphthong)" if self._diphthong_components else ""
        self.set_status(f"Parameters loaded{diph_info} (metadata preserved)")

    def load_preset_file(self, filepath, update_metadata=True):
        """Load a preset from JSON file."""
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
            self._file_ops.on_save(None)
        dlg.Destroy()

    # =========================================================================
    # STATUS
    # =========================================================================

    def set_status(self, message):
        if wx.IsMainThread():
            self.status_bar.SetStatusText(message)
        else:
            wx.PostEvent(self, StatusUpdateEvent(message=message))

    def _on_status_update(self, event):
        self.status_bar.SetStatusText(event.message)

    # =========================================================================
    # THIN EVENT HANDLERS (delegate to managers)
    # =========================================================================

    def on_play(self, event):
        duration = self.header_panel.duration_slider.GetValue()
        formant_scale = self.header_panel.formant_slider.GetValue() / 100.0
        self.audio.play(self.get_frame_params(), duration, formant_scale,
                        self._diphthong_components)

    def on_stop(self, event):
        self.audio.stop()

    def _on_play_done(self, event):
        self.audio.on_play_done()

    def on_play_reference(self, event):
        self.audio.play_reference(self.ipa_input.GetValue().strip())

    def on_toggle_live_preview(self, event):
        self.audio.toggle_live_preview()

    def on_param_changed(self):
        self.audio.on_param_changed()

    def on_play_sequence(self, event):
        sequence_str = self.sequence_input.GetValue().strip()
        formant_scale = self.header_panel.formant_slider.GetValue() / 100.0

        def get_current_params():
            params = self.get_frame_params()
            params['_isVowel'] = self.is_vowel_cb.GetValue()
            params['_isVoiced'] = self.is_voiced_cb.GetValue()
            category = self.category_choice.GetStringSelection()
            params['_isStop'] = (category == 'stop')
            params['_isNasal'] = (category == 'nasal')
            return params

        self.audio.play_sequence(sequence_str, get_current_params,
                                 formant_scale, self.preset_manager)

    def on_loop_sequence(self, event):
        if self.audio._is_looping:
            self.audio.stop()
            return
        sequence_str = self.sequence_input.GetValue().strip()
        formant_scale = self.header_panel.formant_slider.GetValue() / 100.0

        def get_current_params():
            params = self.get_frame_params()
            params['_isVowel'] = self.is_vowel_cb.GetValue()
            params['_isVoiced'] = self.is_voiced_cb.GetValue()
            category = self.category_choice.GetStringSelection()
            params['_isStop'] = (category == 'stop')
            params['_isNasal'] = (category == 'nasal')
            return params

        self.audio.play_sequence_loop(sequence_str, get_current_params,
                                      formant_scale, self.preset_manager)

    def _on_close(self, event):
        self.audio.shutdown()
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
