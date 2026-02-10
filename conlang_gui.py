#!python3
"""
Conlang IPA Speech Synthesizer
A desktop GUI for testing constructed languages with Klatt synthesis.

Author: Based on NVSpeechPlayer by NV Access Limited
License: GPL v2
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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

# For audio playback on Windows
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


class ConlangSynthesizer:
    """Main application class for the IPA synthesizer GUI."""

    def __init__(self, root):
        self.root = root
        self.root.title("Conlang IPA Synthesizer")
        self.root.geometry("700x500")
        self.root.minsize(500, 400)

        # Synthesis parameters
        self.sample_rate = 44100
        self.is_speaking = False
        self.speech_thread = None

        # IPA keyboard state for cycling
        self._last_ipa_key = None
        self._last_ipa_time = 0
        self._ipa_press_count = 0
        self._cycle_timeout = 0.5  # 500ms window for cycling

        # Create the UI
        self._create_widgets()
        self._setup_bindings()

        # Status
        self.set_status("Ready. Press F1 for IPA keyboard help. Ctrl+Enter to speak.")

    def _create_widgets(self):
        """Create all UI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Title label
        title_label = ttk.Label(main_frame, text="IPA Text Input", font=("", 12, "bold"))
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        # IPA text input area
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        self.text_input = tk.Text(text_frame, wrap=tk.WORD, font=("Segoe UI", 14), height=10)
        self.text_input.grid(row=0, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        # Scrollbar for text
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_input.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text_input.configure(yscrollcommand=scrollbar.set)

        # Insert sample IPA text with tone examples
        self.text_input.insert("1.0", """hɛˈloʊ wɜːld

Example phonemes:
• Vowels: a e i o u ɑ ɔ ə ɛ ɪ ʊ ʌ æ
• Consonants: p t k b d g f v s z ʃ ʒ θ ð m n ŋ l ɹ j w h

Tone examples (try these):
• High tone: má (ma + acute accent)
• Low tone: mà (ma + grave accent)
• Rising tone: mǎ (ma + caron)
• Falling tone: mâ (ma + circumflex)
• Tone letters: ma˥ ma˩ ma˥˩ (high, low, falling)

Chinese-style tones: mā má mǎ mà""")

        # Controls frame
        controls_frame = ttk.LabelFrame(main_frame, text="Synthesis Controls", padding="10")
        controls_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Speed slider
        ttk.Label(controls_frame, text="Speed:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_slider = ttk.Scale(controls_frame, from_=0.5, to=2.0, variable=self.speed_var, orient="horizontal", length=150)
        self.speed_slider.grid(row=0, column=1, padx=(0, 20))
        self.speed_label = ttk.Label(controls_frame, text="1.0x")
        self.speed_label.grid(row=0, column=2, padx=(0, 30))
        self.speed_var.trace_add("write", lambda *args: self.speed_label.config(text=f"{self.speed_var.get():.1f}x"))

        # Pitch slider
        ttk.Label(controls_frame, text="Pitch:").grid(row=0, column=3, sticky="w", padx=(0, 5))
        self.pitch_var = tk.DoubleVar(value=120.0)
        self.pitch_slider = ttk.Scale(controls_frame, from_=60, to=300, variable=self.pitch_var, orient="horizontal", length=150)
        self.pitch_slider.grid(row=0, column=4, padx=(0, 20))
        self.pitch_label = ttk.Label(controls_frame, text="120 Hz")
        self.pitch_label.grid(row=0, column=5, padx=(0, 30))
        self.pitch_var.trace_add("write", lambda *args: self.pitch_label.config(text=f"{int(self.pitch_var.get())} Hz"))

        # Inflection slider
        ttk.Label(controls_frame, text="Inflection:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(10, 0))
        self.inflection_var = tk.DoubleVar(value=0.5)
        self.inflection_slider = ttk.Scale(controls_frame, from_=0.0, to=1.0, variable=self.inflection_var, orient="horizontal", length=150)
        self.inflection_slider.grid(row=1, column=1, pady=(10, 0))
        self.inflection_label = ttk.Label(controls_frame, text="0.5")
        self.inflection_label.grid(row=1, column=2, pady=(10, 0))
        self.inflection_var.trace_add("write", lambda *args: self.inflection_label.config(text=f"{self.inflection_var.get():.1f}"))

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Speak button
        self.speak_btn = ttk.Button(buttons_frame, text="▶ Speak", command=self.speak, width=15)
        self.speak_btn.grid(row=0, column=0, padx=(0, 10))

        # Stop button
        self.stop_btn = ttk.Button(buttons_frame, text="■ Stop", command=self.stop, width=15, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))

        # Save WAV button
        self.save_btn = ttk.Button(buttons_frame, text="💾 Save WAV", command=self.save_wav, width=15)
        self.save_btn.grid(row=0, column=2, padx=(0, 10))

        # Clear button
        self.clear_btn = ttk.Button(buttons_frame, text="🗑 Clear", command=self.clear_text, width=15)
        self.clear_btn.grid(row=0, column=3)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.grid(row=4, column=0, columnspan=2, sticky="ew")

    def _setup_bindings(self):
        """Set up keyboard bindings."""
        self.root.bind("<Control-Return>", lambda e: self.speak())
        self.root.bind("<Escape>", lambda e: self.stop())
        self.root.bind("<Control-s>", lambda e: self.save_wav())
        self.root.bind("<F1>", lambda e: self.show_help())

        # IPA keyboard bindings (Alt + key)
        # Bind all letters for vowels and consonants
        for char in 'abcdefghijklmnopqrstuvwxyz':
            self.root.bind(f"<Alt-{char}>", self._on_ipa_key)
            self.root.bind(f"<Alt-{char.upper()}>", self._on_ipa_key)

        # Bind number keys for tone marks
        for num in '0123456789':
            self.root.bind(f"<Alt-{num}>", self._on_ipa_key)

        # Bind punctuation keys (need special handling for some)
        self.root.bind("<Alt-apostrophe>", self._on_ipa_key)
        self.root.bind("<Alt-colon>", self._on_ipa_key)
        self.root.bind("<Alt-semicolon>", self._on_ipa_key)  # For colon without shift
        self.root.bind("<Alt-question>", self._on_ipa_key)
        self.root.bind("<Alt-exclam>", self._on_ipa_key)
        self.root.bind("<Alt-period>", self._on_ipa_key)
        self.root.bind("<Alt-minus>", self._on_ipa_key)
        self.root.bind("<Alt-bracketleft>", self._on_ipa_key)
        self.root.bind("<Alt-bracketright>", self._on_ipa_key)
        self.root.bind("<Alt-slash>", self._on_ipa_key)
        self.root.bind("<Alt-asciicircum>", self._on_ipa_key)
        self.root.bind("<Alt-asciitilde>", self._on_ipa_key)

    def _on_ipa_key(self, event):
        """Handle IPA keyboard shortcut."""
        # Get the key pressed
        key = event.keysym.lower()

        # Map keysym names to our lookup keys
        keysym_map = {
            'apostrophe': "'",
            'colon': ':',
            'semicolon': ':',  # Shift+semicolon = colon
            'question': '?',
            'exclam': '!',
            'period': '.',
            'minus': '-',
            'bracketleft': '[',
            'bracketright': ']',
            'slash': '/',
            'asciicircum': '^',
            'asciitilde': '~',
        }

        # Convert keysym to lookup key
        if key in keysym_map:
            lookup_key = keysym_map[key]
        elif len(key) == 1:
            lookup_key = key
        else:
            return  # Unknown key

        # Check if this is the same key pressed within the cycle timeout
        current_time = time.time()
        if lookup_key == self._last_ipa_key and (current_time - self._last_ipa_time) < self._cycle_timeout:
            # Same key, increment press count
            self._ipa_press_count += 1
            # Delete the previously inserted character
            self.text_input.delete("insert-1c", "insert")
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
            self.text_input.insert("insert", symbol)
            # Update status bar with symbol info (for screen reader)
            self.set_status(f"Inserted: {symbol} ({description})")

        return "break"  # Prevent default handling

    def show_help(self):
        """Show help dialog with all keyboard shortcuts."""
        help_text = ipa_keyboard.get_help_text()

        # Create a simple dialog
        help_window = tk.Toplevel(self.root)
        help_window.title("IPA Keyboard Help")
        help_window.geometry("600x500")
        help_window.transient(self.root)

        # Make it modal
        help_window.grab_set()

        # Create text widget with scrollbar
        frame = ttk.Frame(help_window, padding="10")
        frame.pack(fill="both", expand=True)

        text = tk.Text(frame, wrap=tk.WORD, font=("Consolas", 10))
        text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        scrollbar.pack(side="right", fill="y")
        text.configure(yscrollcommand=scrollbar.set)

        # Insert help text
        text.insert("1.0", help_text)
        text.configure(state="disabled")  # Make read-only

        # Close button
        close_btn = ttk.Button(help_window, text="Close (Escape)", command=help_window.destroy)
        close_btn.pack(pady=10)

        # Bind Escape to close
        help_window.bind("<Escape>", lambda e: help_window.destroy())

        # Focus the text for screen reader
        text.focus_set()

    def set_status(self, message):
        """Update status bar."""
        self.status_var.set(message)
        self.root.update_idletasks()

    def get_ipa_text(self):
        """Get the IPA text from the input area."""
        return self.text_input.get("1.0", "end-1c").strip()

    def synthesize_to_samples(self, ipa_text):
        """Synthesize IPA text to audio samples."""
        sp = speechPlayer.SpeechPlayer(self.sample_rate)
        all_samples = []

        speed = self.speed_var.get()
        pitch = self.pitch_var.get()
        inflection = self.inflection_var.get()

        for frame, duration, fade in ipa.generateFramesAndTiming(
            ipa_text,
            speed=speed,
            basePitch=pitch,
            inflection=inflection
        ):
            if not self.is_speaking:
                break

            if frame:
                sp.queueFrame(frame, duration, fade)
            else:
                sp.queueFrame(None, duration, fade)

            chunk_samples = int(duration * (self.sample_rate / 1000.0)) + 100
            samples = sp.synthesize(chunk_samples)
            if samples:
                all_samples.extend(samples[:])

        return all_samples

    def _speak_thread(self, ipa_text):
        """Thread function for speaking."""
        try:
            self.set_status(f"Synthesizing: {len(ipa_text)} characters...")
            samples = self.synthesize_to_samples(ipa_text)

            if not self.is_speaking or not samples:
                return

            # Save to temp file and play
            self.set_status(f"Playing {len(samples)} samples...")

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
            self.root.after(0, self._update_buttons)

    def _update_buttons(self):
        """Update button states."""
        if self.is_speaking:
            self.speak_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
        else:
            self.speak_btn.config(state="normal")
            self.stop_btn.config(state="disabled")

    def speak(self):
        """Start speaking the IPA text."""
        if self.is_speaking:
            return

        ipa_text = self.get_ipa_text()
        if not ipa_text:
            self.set_status("No text to speak.")
            return

        self.is_speaking = True
        self._update_buttons()

        self.speech_thread = threading.Thread(target=self._speak_thread, args=(ipa_text,), daemon=True)
        self.speech_thread.start()

    def stop(self):
        """Stop speaking."""
        if self.is_speaking:
            self.is_speaking = False
            if HAS_WINSOUND:
                winsound.PlaySound(None, winsound.SND_PURGE)
            self.set_status("Stopped.")
            self._update_buttons()

    def save_wav(self):
        """Save the synthesized audio to a WAV file."""
        ipa_text = self.get_ipa_text()
        if not ipa_text:
            self.set_status("No text to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
            title="Save as WAV"
        )

        if not file_path:
            return

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
            messagebox.showerror("Error", f"Could not save file: {e}")

    def clear_text(self):
        """Clear the text input."""
        self.text_input.delete("1.0", "end")
        self.set_status("Text cleared.")


def main():
    """Main entry point."""
    root = tk.Tk()

    # Try to use a nicer theme on Windows
    try:
        root.tk.call("source", "azure.tcl")
        root.tk.call("set_theme", "light")
    except:
        try:
            style = ttk.Style()
            style.theme_use('vista')
        except:
            pass

    app = ConlangSynthesizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
