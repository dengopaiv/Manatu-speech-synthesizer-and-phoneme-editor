"""Keyboard handling for the phoneme editor."""

import time
import wx
import ipa_keyboard


class KeyboardManager:
    """Manages keyboard shortcuts and IPA cycling input."""

    def __init__(self, frame):
        self._frame = frame
        # IPA keyboard cycling state
        self._last_ipa_key = None
        self._last_ipa_time = 0
        self._ipa_press_count = 0
        self._cycle_timeout = 0.5

    def on_key(self, event):
        key = event.GetKeyCode()

        # IPA keyboard in sequence input
        if event.AltDown() and self._frame.sequence_input.HasFocus():
            if self._handle_ipa_key(key):
                return

        # Global shortcuts
        if key == wx.WXK_F5 and not self._frame.audio.is_playing:
            self._frame.on_play(None)
        elif key == wx.WXK_F6 and not self._frame.audio.is_playing:
            self._frame.on_play_sequence(None)
        elif key == wx.WXK_F7:
            self._frame.on_play_reference(None)
        elif key == wx.WXK_F8:
            self._frame.on_toggle_live_preview(None)
        elif key == wx.WXK_F9:
            self._frame.on_loop_sequence(None)
        elif key == wx.WXK_ESCAPE:
            self._frame.on_stop(None)
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
            text = self._frame.sequence_input.GetValue()
            pos = self._frame.sequence_input.GetInsertionPoint()
            if pos > 0 and text[pos-1:pos] == ']':
                bracket_start = text.rfind('[', 0, pos-1)
                if bracket_start >= 0:
                    self._frame.sequence_input.Remove(bracket_start, pos)
        else:
            self._ipa_press_count = 1

        self._last_ipa_key = lookup_key
        self._last_ipa_time = current_time

        result = ipa_keyboard.get_symbol_for_key(lookup_key, self._ipa_press_count)
        if result:
            symbol, description = result
            self._frame.sequence_input.WriteText(f"[{symbol}]")
            self._frame.set_status(f"Inserted: {symbol} ({description})")
            return True
        return False
