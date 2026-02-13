"""Audio playback and live preview management for the phoneme editor."""

import threading
import time
import wave
import struct
import tempfile
import os
import re
from pathlib import Path

import wx
import speechPlayer
import ipa as ipa_module

from editor_events import StatusUpdateEvent, PlayDoneEvent
from phoneme_editor_constants import KLSYN88_DEFAULTS, SEQUENCE_DURATIONS
from data import data as PHONEME_DATA

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


class AudioManager:
    """Manages all audio playback: single frames, diphthongs, sequences, and live preview."""

    def __init__(self, frame, sample_rate=44100):
        self._frame = frame
        self.sample_rate = sample_rate
        self.is_playing = False
        self._is_looping = False
        self.play_thread = None

        # Live preview state
        self.is_live_preview = False
        self._live_sp = None
        self._live_stream = None

    # =========================================================================
    # FRAME CREATION
    # =========================================================================

    def create_frame(self, params):
        """Create a speechPlayer.Frame from a params dict."""
        frame = speechPlayer.Frame()
        for name, value in params.items():
            if hasattr(frame, name):
                setattr(frame, name, value)
        return frame

    @staticmethod
    def apply_formant_scaling(frame, scale_factor):
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

    # =========================================================================
    # SINGLE FRAME PLAYBACK
    # =========================================================================

    def _play_thread(self, frame, duration_ms, formant_scale=1.0):
        try:
            self.apply_formant_scaling(frame, formant_scale)
            scale_info = f", scale={formant_scale:.2f}" if formant_scale != 1.0 else ""
            self._set_status(f"Playing: pitch={frame.voicePitch:.0f}Hz, F1={frame.cf1:.0f}{scale_info}")

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

            self._play_wav(all_samples)
            self._set_status("Done.")
        except Exception as e:
            self._set_status(f"Error: {e}")
        finally:
            wx.PostEvent(self._frame, PlayDoneEvent())

    # =========================================================================
    # DIPHTHONG PLAYBACK
    # =========================================================================

    def _play_diphthong_thread(self, components, duration_ms, formant_scale=1.0):
        """Play diphthong as gliding sequence of component vowels."""
        try:
            component_names = ', '.join(components)
            self._set_status(f"Playing diphthong: {component_names}")

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
                ipa_module.applyPhonemeToFrame(frame, vowel_data)
                self.apply_formant_scaling(frame, formant_scale)
                frames.append(frame)

            if not frames:
                self._set_status("Error: No valid component vowels found")
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

            self._play_wav(all_samples)
            self._set_status("Done.")
        except Exception as e:
            self._set_status(f"Error: {e}")
        finally:
            wx.PostEvent(self._frame, PlayDoneEvent())

    # =========================================================================
    # PLAY / STOP
    # =========================================================================

    def play(self, frame_params, duration_ms, formant_scale, diphthong_components):
        """Start playback. Called by frame's on_play."""
        if self.is_playing:
            return
        if self.is_live_preview:
            self._stop_live_preview()
        self.is_playing = True
        self._update_ui_playing(True)

        if diphthong_components:
            self.play_thread = threading.Thread(
                target=self._play_diphthong_thread,
                args=(diphthong_components, duration_ms, formant_scale),
                daemon=True
            )
        else:
            frame = self.create_frame(frame_params)
            self.play_thread = threading.Thread(
                target=self._play_thread,
                args=(frame, duration_ms, formant_scale),
                daemon=True
            )
        self.play_thread.start()

    def stop(self):
        """Stop current playback or live preview."""
        if self.is_live_preview:
            self._stop_live_preview()
            return
        if self.is_playing:
            self._is_looping = False
            self.is_playing = False
            if HAS_WINSOUND:
                winsound.PlaySound(None, winsound.SND_PURGE)
            self._set_status("Stopped.")
            self._update_ui_playing(False)

    def on_play_done(self):
        """Called when a play thread finishes."""
        self.is_playing = False
        self._frame.header_panel.play_btn.Enable(True)
        self._frame.header_panel.stop_btn.Enable(False)
        self._frame.sequence_panel.play_seq_btn.Enable(True)

    # =========================================================================
    # REFERENCE PLAYBACK
    # =========================================================================

    def play_reference(self, ipa_symbol):
        """Play human-recorded reference sample for an IPA symbol."""
        if not ipa_symbol:
            self._set_status("No IPA symbol to look up")
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
                self._set_status(f"Reference: [{ipa_symbol}]")
                return
            except Exception as e:
                self._set_status(f"winsound error: {e}")

        if ogg_path.exists():
            try:
                import pygame
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                pygame.mixer.music.load(str(ogg_path))
                pygame.mixer.music.play()
                self._set_status(f"Reference: [{ipa_symbol}] (OGG)")
                return
            except ImportError:
                pass
            except Exception as e:
                self._set_status(f"pygame error: {e}")

            try:
                import subprocess
                import sys
                if sys.platform == 'win32':
                    subprocess.Popen(['start', '', str(ogg_path)], shell=True)
                    self._set_status(f"Reference: [{ipa_symbol}] (system player)")
                    return
            except Exception:
                pass

            self._set_status(f"OGG found but can't play. Run: python download_ipa_samples.py --convert")
            return

        self._set_status(f"No reference for [{ipa_symbol}]. Run: python download_ipa_samples.py")

    # =========================================================================
    # LIVE PREVIEW
    # =========================================================================

    def toggle_live_preview(self):
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
        if self.is_playing:
            self.stop()

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
        self._frame.header_panel.play_btn.Enable(False)
        self._frame.header_panel.live_btn.SetLabel("Stop Live")
        self._set_status("Live preview ON — adjust sliders to hear changes")

    def _stop_live_preview(self):
        """Stop the live audio stream and clean up."""
        self.is_live_preview = False
        if self._live_stream is not None:
            self._live_stream.stop()
            self._live_stream.close()
            self._live_stream = None
        self._live_sp = None
        self._frame.header_panel.play_btn.Enable(True)
        self._frame.header_panel.live_btn.SetLabel("Live (F8)")
        self._set_status("Live preview OFF")

    def _queue_live_frame(self):
        """Read current sliders and queue a long frame for continuous playback."""
        if not self.is_live_preview or self._live_sp is None:
            return
        params = self._frame.get_frame_params()
        frame = self.create_frame(params)
        formant_scale = self._frame.header_panel.formant_slider.GetValue() / 100.0
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
    # SEQUENCE PLAYBACK
    # =========================================================================

    def _parse_test_sequence(self, sequence_str, get_current_params_fn, preset_manager):
        phonemes = []
        matches = re.findall(r'\[([^\]]+)\]', sequence_str)
        for phoneme_key in matches:
            if phoneme_key == '*':
                phonemes.append(('*', get_current_params_fn()))
            elif preset_params := preset_manager.find_preset_by_ipa(phoneme_key):
                phonemes.append((phoneme_key, dict(preset_params)))
            elif phoneme_key in PHONEME_DATA:
                phonemes.append((phoneme_key, dict(PHONEME_DATA[phoneme_key])))
            else:
                self._set_status(f"Unknown phoneme: {phoneme_key}")
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
            self._set_status(f"Playing sequence of {len(phoneme_list)} phonemes...")
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

            self._play_wav(all_samples)
            self._set_status("Sequence done.")
        except Exception as e:
            self._set_status(f"Error: {e}")
        finally:
            wx.PostEvent(self._frame, PlayDoneEvent())

    def play_sequence(self, sequence_str, get_current_params_fn, formant_scale, preset_manager):
        """Parse and play a test sequence string."""
        if self.is_playing:
            return
        if self.is_live_preview:
            self._stop_live_preview()
        if not sequence_str:
            self._set_status("No sequence to play.")
            return

        phoneme_list = self._parse_test_sequence(sequence_str, get_current_params_fn, preset_manager)
        if phoneme_list is None:
            return
        if not phoneme_list:
            self._set_status("No valid phonemes in sequence.")
            return

        self.is_playing = True
        self._frame.header_panel.play_btn.Enable(False)
        self._frame.sequence_panel.play_seq_btn.Enable(False)
        self._frame.header_panel.stop_btn.Enable(True)

        self.play_thread = threading.Thread(
            target=self._play_test_sequence_thread,
            args=(phoneme_list, formant_scale),
            daemon=True
        )
        self.play_thread.start()

    # =========================================================================
    # LOOP SEQUENCE PLAYBACK
    # =========================================================================

    def _play_loop_sequence_thread(self, phoneme_list, formant_scale=1.0):
        try:
            iteration = 0
            while self.is_playing and self._is_looping:
                iteration += 1
                self._set_status(f"Loop #{iteration}: {len(phoneme_list)} phonemes...")

                sp = speechPlayer.SpeechPlayer(self.sample_rate)
                for phoneme_key, params in phoneme_list:
                    frame = self._create_frame_from_phoneme(params)
                    self.apply_formant_scaling(frame, formant_scale)
                    duration = SEQUENCE_DURATIONS['vowel'] if params.get('_isVowel') else SEQUENCE_DURATIONS['consonant']
                    fade = min(30, duration // 3)
                    sp.queueFrame(frame, duration, fade)
                sp.queueFrame(None, 50, 20)

                all_samples = []
                while self.is_playing and self._is_looping:
                    samples = sp.synthesize(8192)
                    if samples and hasattr(samples, 'length') and samples.length > 0:
                        all_samples.extend(samples[:samples.length])
                    elif samples:
                        all_samples.extend(samples[:])
                        if len(samples) < 8192:
                            break
                    else:
                        break

                if not self.is_playing or not self._is_looping or not all_samples:
                    break

                self._play_wav(all_samples)

                # Brief pause between iterations
                time.sleep(0.2)

            self._set_status("Loop stopped.")
        except Exception as e:
            self._set_status(f"Error: {e}")
        finally:
            self._is_looping = False
            wx.PostEvent(self._frame, PlayDoneEvent())

    def play_sequence_loop(self, sequence_str, get_current_params_fn, formant_scale, preset_manager):
        """Parse and loop-play a test sequence string."""
        if self.is_playing:
            return
        if self.is_live_preview:
            self._stop_live_preview()
        if not sequence_str:
            self._set_status("No sequence to play.")
            return

        phoneme_list = self._parse_test_sequence(sequence_str, get_current_params_fn, preset_manager)
        if phoneme_list is None:
            return
        if not phoneme_list:
            self._set_status("No valid phonemes in sequence.")
            return

        self._is_looping = True
        self.is_playing = True
        self._frame.header_panel.play_btn.Enable(False)
        self._frame.sequence_panel.play_seq_btn.Enable(False)
        self._frame.header_panel.stop_btn.Enable(True)

        self.play_thread = threading.Thread(
            target=self._play_loop_sequence_thread,
            args=(phoneme_list, formant_scale),
            daemon=True
        )
        self.play_thread.start()

    # =========================================================================
    # SHUTDOWN
    # =========================================================================

    def shutdown(self):
        """Clean up audio resources. Called from frame's on_close."""
        if self.is_live_preview:
            self._stop_live_preview()
        if self.is_playing:
            self._is_looping = False
            self.is_playing = False
            if HAS_WINSOUND:
                winsound.PlaySound(None, winsound.SND_PURGE)

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _set_status(self, message):
        """Thread-safe status update via the frame."""
        self._frame.set_status(message)

    def _update_ui_playing(self, playing):
        """Update play/stop button states."""
        self._frame.header_panel.play_btn.Enable(not playing)
        self._frame.header_panel.stop_btn.Enable(playing)

    def _play_wav(self, all_samples):
        """Write samples to a temp WAV and play with winsound."""
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
