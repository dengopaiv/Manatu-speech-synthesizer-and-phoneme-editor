"""
Phoneme Editor Panel Classes

Contains all UI panel classes for the phoneme parameter editor:
- AccessibleSlider: Custom slider with enhanced keyboard navigation
- HeaderPanel: Metadata and preview controls
- ParametersPanel: All 47 parameter sliders
- PresetsPanel: Preset browser
- SequenceTestingPanel: Sequence testing interface
- ViewPanel: Read-only parameter views
- FileExportPanel: File operations
"""

import sys
from pathlib import Path

# Add parent directory to path for imports from main package (if not already done)
_EDITOR_DIR = Path(__file__).parent
_ROOT_DIR = _EDITOR_DIR.parent
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

import wx
import wx.lib.scrolledpanel as scrolled

# Import local editor modules
from phoneme_editor_constants import (
    PARAM_GROUPS, PERCENT_PARAMS, GAIN_PARAMS, TENTH_PARAMS,
    KLSYN88_DEFAULTS, IPA_DESCRIPTIONS
)
import voice_profiles

# Import from parent's data package
from data import PHONEME_CATEGORIES, CATEGORY_ORDER


class AccessibleSlider(wx.Slider):
    """Custom slider with enhanced keyboard navigation for accessibility.

    Key bindings:
    - Arrow Up/Down: 0.1% of range
    - Shift + Arrow Up/Down: 1% of range
    - PgUp/PgDown: 5% of range
    - Shift + PgUp/PgDown: 10% of range
    - Home: Jump to minimum
    - End: Jump to maximum
    - F2: Open edit dialog for exact value
    - D: Reset to parameter default
    - Shift+D: Restore to original loaded value
    """

    def __init__(self, parent, param_name, min_val, max_val, default, unit,
                 params_panel, **kwargs):
        super().__init__(parent, **kwargs)
        self.param_name = param_name
        self.min_val = min_val
        self.max_val = max_val
        self.default = default
        self.unit = unit
        self.params_panel = params_panel
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)

    def _on_key_down(self, event):
        # Let Alt/Ctrl combinations propagate to menus and parent handlers
        if event.AltDown() or event.ControlDown():
            event.Skip()
            return

        key = event.GetKeyCode()
        shift = event.ShiftDown()
        range_size = self.max_val - self.min_val
        current = self.GetValue()
        new_value = None

        if key == wx.WXK_UP:
            step = int(range_size * (0.01 if shift else 0.001))
            step = max(1, step)  # At least 1 unit
            new_value = min(self.max_val, current + step)
        elif key == wx.WXK_DOWN:
            step = int(range_size * (0.01 if shift else 0.001))
            step = max(1, step)
            new_value = max(self.min_val, current - step)
        elif key == wx.WXK_PAGEUP:
            step = int(range_size * (0.10 if shift else 0.05))
            step = max(1, step)
            new_value = min(self.max_val, current + step)
        elif key == wx.WXK_PAGEDOWN:
            step = int(range_size * (0.10 if shift else 0.05))
            step = max(1, step)
            new_value = max(self.min_val, current - step)
        elif key == wx.WXK_HOME:
            new_value = self.min_val
        elif key == wx.WXK_END:
            new_value = self.max_val
        elif key == wx.WXK_F2:
            self._open_edit_dialog()
            return
        elif key == ord('D') or key == ord('d'):
            if shift:
                # Restore to original loaded value
                self._restore_original()
            else:
                # Reset to parameter default
                self._restore_default()
            return
        else:
            event.Skip()
            return

        if new_value is not None:
            self.SetValue(new_value)
            self.params_panel._on_slider_change(self.param_name)
            # Trigger scroll event for any listeners
            evt = wx.CommandEvent(wx.wxEVT_SLIDER, self.GetId())
            evt.SetEventObject(self)
            wx.PostEvent(self, evt)

    def _open_edit_dialog(self):
        """Open dialog to enter exact value."""
        current = self.GetValue()
        dlg = wx.TextEntryDialog(
            self.GetParent(),
            f"Enter value for {self.param_name} ({self.min_val}-{self.max_val} {self.unit}):",
            "Set Exact Value",
            str(current)
        )
        if dlg.ShowModal() == wx.ID_OK:
            try:
                new_value = int(float(dlg.GetValue()))
                new_value = max(self.min_val, min(self.max_val, new_value))
                self.SetValue(new_value)
                self.params_panel._on_slider_change(self.param_name)
            except ValueError:
                wx.MessageBox(
                    f"Invalid value. Please enter a number between {self.min_val} and {self.max_val}.",
                    "Invalid Input",
                    wx.OK | wx.ICON_WARNING
                )
        dlg.Destroy()

    def _restore_default(self):
        """Reset to parameter default value."""
        self.SetValue(self.default)
        self.params_panel._on_slider_change(self.param_name)
        self.params_panel._set_status(f"Reset {self.param_name} to default: {self.default}")

    def _restore_original(self):
        """Restore to original loaded value."""
        if self.param_name in self.params_panel._original_values:
            value = self.params_panel._original_values[self.param_name]
            self.SetValue(value)
            self.params_panel._on_slider_change(self.param_name)
            self.params_panel._set_status(f"Restored {self.param_name} to original value: {value}")
        else:
            self.params_panel._set_status(f"No original value for {self.param_name}")


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
        preview_sizer.Add(self.ref_btn, 0, wx.RIGHT, 10)

        # Live preview button
        self.live_btn = wx.Button(self, label="Live (F8)", size=(80, -1))
        self.live_btn.SetName("Toggle Live Preview")
        self.live_btn.SetToolTip("Toggle live audio preview (F8)")
        preview_sizer.Add(self.live_btn, 0)

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
        self.editor.on_param_changed()

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
            if 'endVoicePitch' in params_panel.sliders:
                params_panel.sliders['endVoicePitch'].SetValue(pitch)
                params_panel.value_labels['endVoicePitch'].SetLabel(f"{pitch}")
        self.editor.set_status(f"Preview voice: {preset_name} (pitch={profile.get('basePitch', 100)}Hz)")


class ParametersPanel(scrolled.ScrolledPanel):
    """Tab panel containing all 47 parameter sliders."""

    def __init__(self, parent, editor):
        super().__init__(parent)
        self.editor = editor
        self.sliders = {}
        self.value_labels = {}
        # Value tracking for D key restore feature
        self._saved_values = {}    # Updated on load AND save
        self._original_values = {} # Only updated on load
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

        slider = AccessibleSlider(
            self, name, min_val, max_val, default, unit, self,
            value=default, minValue=min_val, maxValue=max_val,
            style=wx.SL_HORIZONTAL, size=(200, -1)
        )
        slider.SetName(f"{name} ({desc})")
        slider.SetToolTip(f"{desc} ({min_val}-{max_val} {unit})\nKeys: Arrows=0.1%/1%, PgUp/Dn=5%/10%, Home/End, F2=edit, D=restore")
        row_sizer.Add(slider, 1, wx.EXPAND | wx.RIGHT, 5)

        value_label = wx.StaticText(self, label=f"{default} {unit}", size=(80, -1))
        row_sizer.Add(value_label, 0, wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(row_sizer, 0, wx.ALL | wx.EXPAND, 2)

        self.sliders[name] = slider
        self.value_labels[name] = value_label

        slider.Bind(wx.EVT_SLIDER, lambda e, n=name: self._on_slider_change(n))

    def _on_slider_change(self, name):
        slider = self.sliders[name]
        unit = slider.unit
        self.value_labels[name].SetLabel(f"{slider.GetValue()} {unit}")
        self.editor.on_param_changed()

    def _set_status(self, message):
        """Set status bar message via editor."""
        if hasattr(self.editor, 'set_status'):
            self.editor.set_status(message)

    def get_frame_params(self):
        params = {}
        for name, slider in self.sliders.items():
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

    def set_frame_params(self, params, apply_klsyn88_defaults=True, track_values=True):
        """Set slider values from parameters dict.

        Args:
            params: Dictionary of parameter values
            apply_klsyn88_defaults: Whether to apply KLSYN88 defaults first
            track_values: Whether to update saved/original value tracking
        """
        if apply_klsyn88_defaults:
            all_params = dict(KLSYN88_DEFAULTS)
            all_params.update(params)
        else:
            all_params = params

        for name, value in all_params.items():
            if name not in self.sliders:
                continue
            slider = self.sliders[name]
            if name in PERCENT_PARAMS:
                slider_val = int(value * 100)
            elif name in GAIN_PARAMS:
                slider_val = int(value * 100)
            elif name in TENTH_PARAMS:
                slider_val = int(value * 10)
            else:
                slider_val = int(value)
            slider_val = max(slider.min_val, min(slider.max_val, slider_val))
            slider.SetValue(slider_val)
            self.value_labels[name].SetLabel(f"{slider_val} {slider.unit}")

            # Track values for D key restore
            if track_values:
                self._saved_values[name] = slider_val
                self._original_values[name] = slider_val

    def update_saved_values(self):
        """Update saved values from current slider positions (called on save)."""
        for name, slider in self.sliders.items():
            self._saved_values[name] = slider.GetValue()


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
        open_sizer.Add(self.new_btn, 0, wx.ALL | wx.EXPAND, 10)

        main_sizer.Add(open_sizer, 0, wx.ALL | wx.EXPAND, 10)

        self.SetSizer(main_sizer)
