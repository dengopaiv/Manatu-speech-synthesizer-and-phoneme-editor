#!python3
"""
Conlang IPA Speech Synthesizer - Accessible wxPython GUI
A desktop GUI for testing constructed languages with Klatt synthesis.

This version uses wxPython for full screen reader accessibility (NVDA, JAWS, Narrator).

Author: Based on NVSpeechPlayer by NV Access Limited
License: GPL v2
"""

import wx
import wx.adv
import wx.lib.newevent
import threading
import wave
import struct
import tempfile
import os
import time

# Import the synthesis modules
import speechPlayer
import ipa
import ipa_keyboard
import voice_profiles

# For audio playback on Windows
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

# Custom event for thread-safe status updates
StatusUpdateEvent, EVT_STATUS_UPDATE = wx.lib.newevent.NewEvent()
SpeechDoneEvent, EVT_SPEECH_DONE = wx.lib.newevent.NewEvent()


class ConlangSynthesizerFrame(wx.Frame):
    """Main application frame for the IPA synthesizer GUI."""

    def __init__(self):
        super().__init__(
            parent=None,
            title="Conlang IPA Synthesizer",
            size=(700, 650)
        )

        # Synthesis parameters
        self.sample_rate = 44100
        self.is_speaking = False
        self.speech_thread = None

        # IPA keyboard state for cycling
        self._last_ipa_key = None
        self._last_ipa_time = 0
        self._ipa_press_count = 0
        self._cycle_timeout = 0.5  # 500ms window for cycling

        # Create UI
        self._create_menu_bar()
        self._create_widgets()
        self._setup_accelerators()
        self._bind_events()

        # Set minimum size
        self.SetMinSize((500, 400))

        # Center on screen
        self.Centre()

        # Initial status
        self.set_status("Ready. Press F1 for IPA keyboard help. Ctrl+Enter to speak.")

        # Focus the text input
        self.text_input.SetFocus()

    def _create_menu_bar(self):
        """Create accessible menu bar."""
        menu_bar = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()
        save_item = file_menu.Append(wx.ID_SAVE, "&Save as WAV\tCtrl+S", "Save speech to WAV file")
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, "E&xit\tAlt+F4", "Exit the application")
        menu_bar.Append(file_menu, "&File")

        # Edit menu
        edit_menu = wx.Menu()
        clear_item = edit_menu.Append(wx.ID_CLEAR, "&Clear text\tCtrl+Delete", "Clear all text")
        edit_menu.AppendSeparator()
        select_all_item = edit_menu.Append(wx.ID_SELECTALL, "Select &All\tCtrl+A", "Select all text")
        menu_bar.Append(edit_menu, "&Edit")

        # Speech menu
        speech_menu = wx.Menu()
        self.speak_menu_item = speech_menu.Append(wx.ID_ANY, "&Speak\tCtrl+Enter", "Speak the IPA text")
        self.stop_menu_item = speech_menu.Append(wx.ID_STOP, "S&top\tEscape", "Stop speaking")
        self.stop_menu_item.Enable(False)
        menu_bar.Append(speech_menu, "&Speech")

        # Help menu
        help_menu = wx.Menu()
        help_item = help_menu.Append(wx.ID_HELP, "&IPA Keyboard Help\tF1", "Show IPA keyboard shortcuts")
        help_menu.AppendSeparator()
        about_item = help_menu.Append(wx.ID_ABOUT, "&About", "About this application")
        menu_bar.Append(help_menu, "&Help")

        self.SetMenuBar(menu_bar)

        # Bind menu events
        self.Bind(wx.EVT_MENU, self.on_save_wav, save_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_clear, clear_item)
        self.Bind(wx.EVT_MENU, self.on_select_all, select_all_item)
        self.Bind(wx.EVT_MENU, self.on_speak, self.speak_menu_item)
        self.Bind(wx.EVT_MENU, self.on_stop, self.stop_menu_item)
        self.Bind(wx.EVT_MENU, self.on_help, help_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

    def _create_widgets(self):
        """Create all UI widgets with accessibility support."""
        panel = wx.Panel(self)

        # Main vertical sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # IPA Text Input section
        text_label = wx.StaticText(panel, label="&IPA Text Input:")
        text_label.SetName("IPA Text Input label")
        main_sizer.Add(text_label, 0, wx.ALL | wx.EXPAND, 5)

        self.text_input = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.HSCROLL,
            size=(-1, 200)
        )
        self.text_input.SetName("IPA Text Input")
        self.text_input.SetHelpText("Enter IPA phonetic text here. Use Alt+letter for IPA symbols.")

        # Set a readable font
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Segoe UI")
        self.text_input.SetFont(font)

        # Insert sample text with tone examples
        sample_text = """hɛˈloʊ wɜːld

Example phonemes:
Vowels: a e i o u ɑ ɔ ə ɛ ɪ ʊ ʌ æ
Consonants: p t k b d g f v s z ʃ ʒ θ ð m n ŋ l ɹ j w h

Tone examples (try these):
High tone: má (ma + acute accent)
Low tone: mà (ma + grave accent)
Rising tone: mǎ (ma + caron)
Falling tone: mâ (ma + circumflex)
Tone letters: ma˥ ma˩ ma˥˩ (high, low, falling)

Chinese-style tones: mā má mǎ mà"""
        self.text_input.SetValue(sample_text)

        main_sizer.Add(self.text_input, 1, wx.ALL | wx.EXPAND, 5)

        # Synthesis Controls section
        controls_box = wx.StaticBox(panel, label="Synthesis Controls")
        controls_box.SetName("Synthesis Controls")
        controls_sizer = wx.StaticBoxSizer(controls_box, wx.VERTICAL)

        # Create a grid for controls
        grid_sizer = wx.FlexGridSizer(rows=2, cols=6, hgap=10, vgap=10)
        grid_sizer.AddGrowableCol(1)
        grid_sizer.AddGrowableCol(4)

        # Speed control
        speed_label = wx.StaticText(panel, label="&Speed:")
        speed_label.SetName("Speed label")
        grid_sizer.Add(speed_label, 0, wx.ALIGN_CENTER_VERTICAL)

        self.speed_slider = wx.Slider(
            panel,
            value=100,
            minValue=50,
            maxValue=200,
            style=wx.SL_HORIZONTAL
        )
        self.speed_slider.SetName("Speed")
        self.speed_slider.SetHelpText("Adjust speech speed from 0.5x to 2.0x. Current: 1.0x")
        grid_sizer.Add(self.speed_slider, 1, wx.EXPAND)

        self.speed_value_label = wx.StaticText(panel, label="1.0x")
        self.speed_value_label.SetName("Speed value")
        grid_sizer.Add(self.speed_value_label, 0, wx.ALIGN_CENTER_VERTICAL)

        # Pitch control
        pitch_label = wx.StaticText(panel, label="&Pitch:")
        pitch_label.SetName("Pitch label")
        grid_sizer.Add(pitch_label, 0, wx.ALIGN_CENTER_VERTICAL)

        self.pitch_slider = wx.Slider(
            panel,
            value=120,
            minValue=60,
            maxValue=300,
            style=wx.SL_HORIZONTAL
        )
        self.pitch_slider.SetName("Pitch")
        self.pitch_slider.SetHelpText("Adjust base pitch from 60 to 300 Hz. Current: 120 Hz")
        grid_sizer.Add(self.pitch_slider, 1, wx.EXPAND)

        self.pitch_value_label = wx.StaticText(panel, label="120 Hz")
        self.pitch_value_label.SetName("Pitch value")
        grid_sizer.Add(self.pitch_value_label, 0, wx.ALIGN_CENTER_VERTICAL)

        # Inflection control (second row)
        inflection_label = wx.StaticText(panel, label="&Inflection:")
        inflection_label.SetName("Inflection label")
        grid_sizer.Add(inflection_label, 0, wx.ALIGN_CENTER_VERTICAL)

        self.inflection_slider = wx.Slider(
            panel,
            value=50,
            minValue=0,
            maxValue=100,
            style=wx.SL_HORIZONTAL
        )
        self.inflection_slider.SetName("Inflection")
        self.inflection_slider.SetHelpText("Adjust pitch variation from 0.0 to 1.0. Current: 0.5")
        grid_sizer.Add(self.inflection_slider, 1, wx.EXPAND)

        self.inflection_value_label = wx.StaticText(panel, label="0.5")
        self.inflection_value_label.SetName("Inflection value")
        grid_sizer.Add(self.inflection_value_label, 0, wx.ALIGN_CENTER_VERTICAL)

        controls_sizer.Add(grid_sizer, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(controls_sizer, 0, wx.ALL | wx.EXPAND, 5)

        # Voice Type section
        voice_box = wx.StaticBox(panel, label="Voice Type")
        voice_box.SetName("Voice Type")
        voice_sizer = wx.StaticBoxSizer(voice_box, wx.VERTICAL)

        # Voice grid - 2 rows, 6 columns
        voice_grid = wx.FlexGridSizer(rows=2, cols=6, hgap=10, vgap=10)
        voice_grid.AddGrowableCol(1)
        voice_grid.AddGrowableCol(4)

        # Voice preset dropdown
        preset_label = wx.StaticText(panel, label="&Voice Preset:")
        preset_label.SetName("Voice Preset label")
        voice_grid.Add(preset_label, 0, wx.ALIGN_CENTER_VERTICAL)

        self.voice_preset_choice = wx.Choice(panel, choices=voice_profiles.get_profile_names())
        self.voice_preset_choice.SetSelection(0)  # Default to Male
        self.voice_preset_choice.SetName("Voice Preset")
        self.voice_preset_choice.SetHelpText("Select a voice type preset: Male, Female, Child, or Custom")
        voice_grid.Add(self.voice_preset_choice, 1, wx.EXPAND)

        # Empty spacer
        voice_grid.AddStretchSpacer()

        # Formant scale slider
        formant_label = wx.StaticText(panel, label="&Formant Scale:")
        formant_label.SetName("Formant Scale label")
        voice_grid.Add(formant_label, 0, wx.ALIGN_CENTER_VERTICAL)

        self.formant_slider = wx.Slider(
            panel,
            value=100,
            minValue=80,
            maxValue=150,
            style=wx.SL_HORIZONTAL
        )
        self.formant_slider.SetName("Formant Scale")
        self.formant_slider.SetHelpText("Scale formant frequencies. 1.0=male, 1.17=female, 1.35=child. Current: 1.00")
        voice_grid.Add(self.formant_slider, 1, wx.EXPAND)

        self.formant_value_label = wx.StaticText(panel, label="1.00")
        self.formant_value_label.SetName("Formant Scale value")
        voice_grid.Add(self.formant_value_label, 0, wx.ALIGN_CENTER_VERTICAL)

        # Second row: Breathiness slider
        breathiness_label = wx.StaticText(panel, label="&Breathiness:")
        breathiness_label.SetName("Breathiness label")
        voice_grid.Add(breathiness_label, 0, wx.ALIGN_CENTER_VERTICAL)

        self.breathiness_slider = wx.Slider(
            panel,
            value=0,
            minValue=0,
            maxValue=24,
            style=wx.SL_HORIZONTAL
        )
        self.breathiness_slider.SetName("Breathiness")
        self.breathiness_slider.SetHelpText("Spectral tilt in dB. Higher values = breathier voice. Current: 0 dB")
        voice_grid.Add(self.breathiness_slider, 1, wx.EXPAND)

        self.breathiness_value_label = wx.StaticText(panel, label="0 dB")
        self.breathiness_value_label.SetName("Breathiness value")
        voice_grid.Add(self.breathiness_value_label, 0, wx.ALIGN_CENTER_VERTICAL)

        # Empty cells for alignment
        voice_grid.AddStretchSpacer()
        voice_grid.AddStretchSpacer()
        voice_grid.AddStretchSpacer()

        voice_sizer.Add(voice_grid, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(voice_sizer, 0, wx.ALL | wx.EXPAND, 5)

        # Buttons section
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.speak_btn = wx.Button(panel, label="&Speak")
        self.speak_btn.SetName("Speak")
        self.speak_btn.SetHelpText("Press to hear the IPA text spoken aloud. Shortcut: Ctrl+Enter")
        self.speak_btn.SetDefault()
        button_sizer.Add(self.speak_btn, 0, wx.ALL, 5)

        self.stop_btn = wx.Button(panel, label="S&top")
        self.stop_btn.SetName("Stop")
        self.stop_btn.SetHelpText("Stop speaking. Shortcut: Escape")
        self.stop_btn.Enable(False)
        button_sizer.Add(self.stop_btn, 0, wx.ALL, 5)

        self.save_btn = wx.Button(panel, label="Save &WAV")
        self.save_btn.SetName("Save WAV")
        self.save_btn.SetHelpText("Save speech to a WAV audio file. Shortcut: Ctrl+S")
        button_sizer.Add(self.save_btn, 0, wx.ALL, 5)

        self.clear_btn = wx.Button(panel, label="&Clear")
        self.clear_btn.SetName("Clear")
        self.clear_btn.SetHelpText("Clear all text from the input area")
        button_sizer.Add(self.clear_btn, 0, wx.ALL, 5)

        self.help_btn = wx.Button(panel, label="Help (F&1)")
        self.help_btn.SetName("Help")
        self.help_btn.SetHelpText("Show IPA keyboard shortcuts. Shortcut: F1")
        button_sizer.Add(self.help_btn, 0, wx.ALL, 5)

        main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER)

        # Status bar
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetName("Status")

        panel.SetSizer(main_sizer)

    def _setup_accelerators(self):
        """Set up keyboard accelerators including IPA shortcuts."""
        accel_entries = [
            (wx.ACCEL_CTRL, wx.WXK_RETURN, wx.ID_ANY),  # Ctrl+Enter for speak
            (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_STOP),  # Escape for stop
            (wx.ACCEL_CTRL, ord('S'), wx.ID_SAVE),  # Ctrl+S for save
            (wx.ACCEL_NORMAL, wx.WXK_F1, wx.ID_HELP),  # F1 for help
        ]

        # We'll handle IPA shortcuts via key events instead of accelerators
        # because we need the cycling behavior

        accel_table = wx.AcceleratorTable(accel_entries)
        self.SetAcceleratorTable(accel_table)

    def _bind_events(self):
        """Bind all event handlers."""
        # Button events
        self.speak_btn.Bind(wx.EVT_BUTTON, self.on_speak)
        self.stop_btn.Bind(wx.EVT_BUTTON, self.on_stop)
        self.save_btn.Bind(wx.EVT_BUTTON, self.on_save_wav)
        self.clear_btn.Bind(wx.EVT_BUTTON, self.on_clear)
        self.help_btn.Bind(wx.EVT_BUTTON, self.on_help)

        # Slider events
        self.speed_slider.Bind(wx.EVT_SLIDER, self.on_speed_change)
        self.pitch_slider.Bind(wx.EVT_SLIDER, self.on_pitch_change)
        self.inflection_slider.Bind(wx.EVT_SLIDER, self.on_inflection_change)

        # Voice type events
        self.voice_preset_choice.Bind(wx.EVT_CHOICE, self.on_voice_preset_change)
        self.formant_slider.Bind(wx.EVT_SLIDER, self.on_formant_change)
        self.breathiness_slider.Bind(wx.EVT_SLIDER, self.on_breathiness_change)

        # Keyboard events for IPA shortcuts
        self.text_input.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

        # Custom events for thread-safe updates
        self.Bind(EVT_STATUS_UPDATE, self.on_status_update)
        self.Bind(EVT_SPEECH_DONE, self.on_speech_done)

        # Close event
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_key_down(self, event):
        """Handle key events for IPA shortcuts."""
        key_code = event.GetKeyCode()
        modifiers = event.GetModifiers()

        # Check for Ctrl+Enter (speak)
        if modifiers == wx.MOD_CONTROL and key_code == wx.WXK_RETURN:
            self.on_speak(None)
            return

        # Check for Escape (stop)
        if key_code == wx.WXK_ESCAPE:
            self.on_stop(None)
            return

        # Check for Alt+key (IPA shortcuts)
        if modifiers == wx.MOD_ALT:
            # Convert key code to character
            if 65 <= key_code <= 90:  # A-Z
                lookup_key = chr(key_code).lower()
            elif 48 <= key_code <= 57:  # 0-9
                lookup_key = chr(key_code)
            elif key_code == ord("'") or key_code == 222:  # Apostrophe
                lookup_key = "'"
            elif key_code == ord(':') or key_code == 186:  # Colon/semicolon key
                lookup_key = ':'
            elif key_code == ord('?') or key_code == 191:  # Question mark/slash key
                lookup_key = '?'
            elif key_code == ord('!') or key_code == 49:  # Exclamation (Shift+1)
                lookup_key = '!'
            elif key_code == ord('.') or key_code == 190:  # Period
                lookup_key = '.'
            elif key_code == ord('-') or key_code == 189:  # Minus
                lookup_key = '-'
            elif key_code == ord('[') or key_code == 219:  # Left bracket
                lookup_key = '['
            elif key_code == ord(']') or key_code == 221:  # Right bracket
                lookup_key = ']'
            elif key_code == ord('/') or key_code == 191:  # Slash
                lookup_key = '/'
            else:
                event.Skip()
                return

            self._handle_ipa_key(lookup_key)
            return

        event.Skip()

    def _handle_ipa_key(self, lookup_key):
        """Handle IPA keyboard shortcut with cycling support."""
        current_time = time.time()

        # Check if this is the same key pressed within the cycle timeout
        if lookup_key == self._last_ipa_key and (current_time - self._last_ipa_time) < self._cycle_timeout:
            # Same key, increment press count
            self._ipa_press_count += 1
            # Delete the previously inserted character
            pos = self.text_input.GetInsertionPoint()
            if pos > 0:
                self.text_input.Remove(pos - 1, pos)
        else:
            # Different key or timeout expired, reset count
            self._ipa_press_count = 1

        self._last_ipa_key = lookup_key
        self._last_ipa_time = current_time

        # Get the symbol for this key and press count
        result = ipa_keyboard.get_symbol_for_key(lookup_key, self._ipa_press_count)
        if result:
            symbol, description = result
            # Insert the symbol at cursor position
            self.text_input.WriteText(symbol)
            # Update status bar with symbol info (screen reader will announce)
            self.set_status(f"Inserted: {symbol} ({description})")

    def on_speed_change(self, event):
        """Update speed value label."""
        value = self.speed_slider.GetValue() / 100.0
        self.speed_value_label.SetLabel(f"{value:.1f}x")
        self.speed_slider.SetHelpText(f"Adjust speech speed from 0.5x to 2.0x. Current: {value:.1f}x")

    def on_pitch_change(self, event):
        """Update pitch value label."""
        value = self.pitch_slider.GetValue()
        self.pitch_value_label.SetLabel(f"{value} Hz")
        self.pitch_slider.SetHelpText(f"Adjust base pitch from 60 to 300 Hz. Current: {value} Hz")

    def on_inflection_change(self, event):
        """Update inflection value label."""
        value = self.inflection_slider.GetValue() / 100.0
        self.inflection_value_label.SetLabel(f"{value:.1f}")
        self.inflection_slider.SetHelpText(f"Adjust pitch variation from 0.0 to 1.0. Current: {value:.1f}")

    def on_voice_preset_change(self, event):
        """Apply voice preset settings when selection changes."""
        preset_name = self.voice_preset_choice.GetStringSelection()
        profile = voice_profiles.get_profile(preset_name)

        # Skip if Custom is selected (user is adjusting manually)
        if preset_name == 'Custom':
            return

        # Apply preset values to controls
        if profile.get('basePitch') is not None:
            self.pitch_slider.SetValue(int(profile['basePitch']))
            self.on_pitch_change(None)

        if profile.get('formantScale') is not None:
            self.formant_slider.SetValue(int(profile['formantScale'] * 100))
            self.on_formant_change(None, from_preset=True)

        if profile.get('spectralTilt') is not None:
            self.breathiness_slider.SetValue(int(profile['spectralTilt']))
            self.on_breathiness_change(None, from_preset=True)

        self.set_status(f"Voice preset: {preset_name}")

    def on_formant_change(self, event, from_preset=False):
        """Update formant scale value and switch to Custom if manual change."""
        value = self.formant_slider.GetValue() / 100.0
        self.formant_value_label.SetLabel(f"{value:.2f}")
        self.formant_slider.SetHelpText(f"Scale formant frequencies. 1.0=male, 1.17=female, 1.35=child. Current: {value:.2f}")

        # Switch to Custom if user manually changed (not from preset)
        if event and not from_preset:
            self._set_custom_preset()

    def on_breathiness_change(self, event, from_preset=False):
        """Update breathiness value and switch to Custom if manual change."""
        value = self.breathiness_slider.GetValue()
        self.breathiness_value_label.SetLabel(f"{value} dB")
        self.breathiness_slider.SetHelpText(f"Spectral tilt in dB. Higher values = breathier voice. Current: {value} dB")

        # Switch to Custom if user manually changed (not from preset)
        if event and not from_preset:
            self._set_custom_preset()

    def _set_custom_preset(self):
        """Switch the voice preset dropdown to Custom."""
        custom_index = self.voice_preset_choice.FindString('Custom')
        if custom_index != wx.NOT_FOUND:
            self.voice_preset_choice.SetSelection(custom_index)

    def set_status(self, message):
        """Update status bar (thread-safe)."""
        if wx.IsMainThread():
            self.status_bar.SetStatusText(message)
        else:
            evt = StatusUpdateEvent(message=message)
            wx.PostEvent(self, evt)

    def on_status_update(self, event):
        """Handle status update event from thread."""
        self.status_bar.SetStatusText(event.message)

    def get_ipa_text(self):
        """Get the IPA text from the input area."""
        return self.text_input.GetValue().strip()

    def synthesize_to_samples(self, ipa_text):
        """Synthesize IPA text to audio samples.

        Uses batched synthesis pattern like NVDA addon:
        1. Queue ALL frames first (enables proper inter-frame interpolation)
        2. Synthesize in batches of 8192 samples until done
        """
        sp = speechPlayer.SpeechPlayer(self.sample_rate)
        all_samples = []

        speed = self.speed_slider.GetValue() / 100.0
        pitch = self.pitch_slider.GetValue()
        inflection = self.inflection_slider.GetValue() / 100.0
        formant_scale = self.formant_slider.GetValue() / 100.0
        spectral_tilt = self.breathiness_slider.GetValue()

        # Step 1: Queue ALL frames first
        frame_count = 0
        for frame, duration, fade in ipa.generateFramesAndTiming(
            ipa_text,
            speed=speed,
            basePitch=pitch,
            inflection=inflection,
            formantScale=formant_scale,
            spectralTilt=spectral_tilt
        ):
            if not self.is_speaking:
                break

            if frame:
                sp.queueFrame(frame, duration, fade)
            else:
                sp.queueFrame(None, duration, fade)
            frame_count += 1

        if not self.is_speaking or frame_count == 0:
            return []

        # Step 2: Synthesize in batches (like NVDA does)
        BATCH_SIZE = 8192
        while self.is_speaking:
            samples = sp.synthesize(BATCH_SIZE)
            if samples and hasattr(samples, 'length') and samples.length > 0:
                all_samples.extend(samples[:samples.length])
            elif samples:
                # Fallback if length attribute not set
                all_samples.extend(samples[:])
                if len(samples) < BATCH_SIZE:
                    break
            else:
                break  # No more samples

        return all_samples

    def _speak_thread(self, ipa_text):
        """Thread function for speaking."""
        try:
            self.set_status(f"Synthesizing: {len(ipa_text)} characters...")
            samples = self.synthesize_to_samples(ipa_text)

            if not self.is_speaking or not samples:
                return

            self.set_status(f"Playing {len(samples)} samples...")

            # Save to temp file and play
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name

            with wave.open(tmp_path, 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(self.sample_rate)
                wav.writeframes(struct.pack('<%dh' % len(samples), *samples))

            if self.is_speaking and HAS_WINSOUND:
                winsound.PlaySound(tmp_path, winsound.SND_FILENAME)

            # Cleanup
            try:
                os.unlink(tmp_path)
            except:
                pass

            self.set_status("Done.")

        except Exception as e:
            self.set_status(f"Error: {e}")
        finally:
            self.is_speaking = False
            evt = SpeechDoneEvent()
            wx.PostEvent(self, evt)

    def on_speech_done(self, event):
        """Handle speech completion event."""
        self._update_buttons()

    def _update_buttons(self):
        """Update button and menu states."""
        if self.is_speaking:
            self.speak_btn.Enable(False)
            self.stop_btn.Enable(True)
            self.speak_menu_item.Enable(False)
            self.stop_menu_item.Enable(True)
        else:
            self.speak_btn.Enable(True)
            self.stop_btn.Enable(False)
            self.speak_menu_item.Enable(True)
            self.stop_menu_item.Enable(False)

    def on_speak(self, event):
        """Start speaking the IPA text."""
        if self.is_speaking:
            return

        ipa_text = self.get_ipa_text()
        if not ipa_text:
            self.set_status("No text to speak.")
            return

        self.is_speaking = True
        self._update_buttons()

        self.speech_thread = threading.Thread(
            target=self._speak_thread,
            args=(ipa_text,),
            daemon=True
        )
        self.speech_thread.start()

    def on_stop(self, event):
        """Stop speaking."""
        if self.is_speaking:
            self.is_speaking = False
            if HAS_WINSOUND:
                winsound.PlaySound(None, winsound.SND_PURGE)
            self.set_status("Stopped.")
            self._update_buttons()

    def on_save_wav(self, event):
        """Save the synthesized audio to a WAV file."""
        ipa_text = self.get_ipa_text()
        if not ipa_text:
            self.set_status("No text to save.")
            return

        with wx.FileDialog(
            self,
            "Save as WAV",
            wildcard="WAV files (*.wav)|*.wav|All files (*.*)|*.*",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        ) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return

            file_path = dlg.GetPath()

        try:
            self.set_status("Synthesizing for save...")
            self.is_speaking = True  # Use this flag to allow synthesis
            samples = self.synthesize_to_samples(ipa_text)
            self.is_speaking = False

            if not samples:
                self.set_status("No audio generated.")
                return

            with wave.open(file_path, 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(self.sample_rate)
                wav.writeframes(struct.pack('<%dh' % len(samples), *samples))

            self.set_status(f"Saved to {os.path.basename(file_path)}")

        except Exception as e:
            self.set_status(f"Save error: {e}")
            wx.MessageBox(
                f"Could not save file: {e}",
                "Error",
                wx.OK | wx.ICON_ERROR
            )

    def on_clear(self, event):
        """Clear the text input."""
        self.text_input.Clear()
        self.set_status("Text cleared.")
        self.text_input.SetFocus()

    def on_select_all(self, event):
        """Select all text."""
        self.text_input.SetFocus()
        self.text_input.SelectAll()

    def on_help(self, event):
        """Show help dialog with all keyboard shortcuts."""
        help_text = ipa_keyboard.get_help_text()

        dlg = wx.Dialog(
            self,
            title="IPA Keyboard Help",
            size=(650, 500),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Create a read-only text control for the help text
        help_ctrl = wx.TextCtrl(
            dlg,
            value=help_text,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL
        )
        help_ctrl.SetName("IPA Keyboard Help")

        # Use monospace font for better formatting
        font = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        help_ctrl.SetFont(font)

        sizer.Add(help_ctrl, 1, wx.ALL | wx.EXPAND, 10)

        # Close button
        close_btn = wx.Button(dlg, wx.ID_CLOSE, "&Close")
        close_btn.SetDefault()
        sizer.Add(close_btn, 0, wx.ALL | wx.ALIGN_CENTER, 10)

        dlg.SetSizer(sizer)

        close_btn.Bind(wx.EVT_BUTTON, lambda e: dlg.Close())
        dlg.Bind(wx.EVT_CHAR_HOOK, lambda e: dlg.Close() if e.GetKeyCode() == wx.WXK_ESCAPE else e.Skip())

        # Focus the help text for screen reader
        help_ctrl.SetFocus()

        dlg.ShowModal()
        dlg.Destroy()

    def on_about(self, event):
        """Show about dialog."""
        info = wx.adv.AboutDialogInfo()
        info.SetName("Conlang IPA Synthesizer")
        info.SetVersion("1.0")
        info.SetDescription("A tool for testing constructed languages using IPA input with Klatt synthesis.\n\nFully accessible with screen readers (NVDA, JAWS, Narrator).")
        info.SetCopyright("Based on NVSpeechPlayer by NV Access Limited\nLicense: GPL v2")
        info.AddDeveloper("NV Access Limited")

        wx.adv.AboutBox(info)

    def on_exit(self, event):
        """Exit the application."""
        self.Close()

    def on_close(self, event):
        """Handle window close."""
        if self.is_speaking:
            self.is_speaking = False
            if HAS_WINSOUND:
                winsound.PlaySound(None, winsound.SND_PURGE)
        event.Skip()


def main():
    """Main entry point."""
    app = wx.App()

    # Enable high DPI support on Windows
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    frame = ConlangSynthesizerFrame()
    frame.Show()

    app.MainLoop()


if __name__ == "__main__":
    main()
