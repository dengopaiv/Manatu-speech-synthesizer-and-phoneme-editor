"""File operations for the phoneme editor."""

import os
import json
import wx

from data import data as PHONEME_DATA
from phoneme_editor_constants import IPA_DESCRIPTIONS

# Schwa defaults for reset
SCHWA_DEFAULTS = PHONEME_DATA.get('ə', {})


class FileOperations:
    """Handles file menu operations: new, open, save, export, about."""

    def __init__(self, frame):
        self._frame = frame

    def on_new(self, event):
        self.on_reset(event)
        self._frame._diphthong_components = None
        self._frame.ipa_input.SetValue('ə')
        self._frame.desc_input.SetValue('mid central (schwa)')
        idx = self._frame.category_choice.FindString('vowel')
        if idx != wx.NOT_FOUND:
            self._frame.category_choice.SetSelection(idx)
        self._frame.is_vowel_cb.SetValue(True)
        self._frame.is_voiced_cb.SetValue(True)
        self._frame.set_status("New preset - reset to schwa (ə)")

    def on_reset(self, event):
        self._frame._diphthong_components = None
        for name, slider in self._frame.sliders.items():
            value = SCHWA_DEFAULTS.get(name, slider.default)
            value = max(slider.min_val, min(slider.max_val, int(value)))
            slider.SetValue(value)
            self._frame.value_labels[name].SetLabel(f"{value} {slider.unit}")
        self._frame.set_status("Parameters reset to schwa defaults")

    def on_open(self, event):
        with wx.FileDialog(self._frame, "Open Preset",
                          wildcard="JSON files (*.json)|*.json|All files (*.*)|*.*",
                          style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() != wx.ID_CANCEL:
                self._frame.load_preset_file(dlg.GetPath(), update_metadata=True)

    def on_save(self, event):
        ipa_symbol = self._frame.ipa_input.GetValue().strip()
        if not ipa_symbol:
            wx.MessageBox("Please enter an IPA symbol.", "Missing IPA", wx.OK | wx.ICON_WARNING)
            self._frame.ipa_input.SetFocus()
            return
        try:
            filepath = self._frame.preset_manager.save_preset(self._frame.build_preset_data())
            # Update saved values tracking for D key restore
            self._frame.params_panel.update_saved_values()
            self._frame.set_status(f"Saved: {filepath.name}")
            self._frame.presets_panel._populate_preset_list()
        except Exception as e:
            wx.MessageBox(f"Error saving preset: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def on_export(self, event):
        code = self._frame.preset_manager.export_to_data_py(self._frame.build_preset_data())
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(code))
            wx.TheClipboard.Close()
            self._frame.set_status("Copied to clipboard as Python dict.")
        else:
            wx.MessageBox("Could not access clipboard.", "Error", wx.OK | wx.ICON_ERROR)

    def on_export_json(self, event):
        with wx.FileDialog(self._frame, "Export as JSON",
                          wildcard="JSON files (*.json)|*.json",
                          style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() != wx.ID_CANCEL:
                try:
                    with open(dlg.GetPath(), 'w', encoding='utf-8') as f:
                        json.dump(self._frame.build_preset_data(), f, indent=2, ensure_ascii=False)
                    self._frame.set_status(f"Exported: {os.path.basename(dlg.GetPath())}")
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
        self._frame.Close()
