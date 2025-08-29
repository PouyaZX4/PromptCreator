# core/enhanced_audio.py

import threading
import torch
from faster_whisper import WhisperModel
import noisereduce as nr
import numpy as np
import sounddevice as sd
import librosa
from collections import deque

# --- Configuration ---
TARGET_SR = 16000  # Target sample rate for Whisper
HOP_SECONDS = 0.4  # Process audio in 400ms chunks for responsiveness
MODEL_NAME = "tiny.en" # The Whisper model to use

class EnhancedAudioProcessor:
    """
    Manages Whisper model loading, noise reduction, and PTT audio recording.
    This is a simplified version focusing only on Push-to-Talk functionality.
    """
    def __init__(self):
        self._whisper_model = None
        self._model_lock = threading.Lock()
        self.is_recording = threading.Event() # Event to control the recording loop
        self._audio_buffer = deque()
        print("🎯 EnhancedAudioProcessor initialized for PTT.")

    def load_model(self):
        """Loads the faster-whisper model (thread-safe)."""
        with self._model_lock:
            if self._whisper_model is None:
                print(f"🔄 Loading faster-whisper model: {MODEL_NAME}")
                # Force CPU usage and use int8 for smaller memory footprint
                device = "cpu"
                compute_type = "int8"
                self._whisper_model = WhisperModel(
                    MODEL_NAME,
                    device=device,
                    compute_type=compute_type
                )
                print(f"✅ Faster-whisper model loaded on {device} with {compute_type} compute type.")

    def _apply_noise_reduction(self, audio_data: np.ndarray) -> np.ndarray:
        """Applies noise reduction to an audio chunk."""
        try:
            audio_enhanced = audio_data * 2.0
            reduced_noise = nr.reduce_noise(y=audio_enhanced, sr=TARGET_SR, stationary=False, prop_decrease=0.7)
            return reduced_noise
        except Exception as e:
            print(f"⚠️ Noise reduction failed: {e}")
            return audio_data

    def transcribe_audio(self, audio_data: np.ndarray) -> str:
        """Transcribes a numpy array of audio data."""
        if self._whisper_model is None:
            self.load_model() # Ensure model is loaded if not already
        
        try:
            enhanced_audio = self._apply_noise_reduction(audio_data)
            segments, _ = self._whisper_model.transcribe(
                enhanced_audio, beam_size=5, language="en", without_timestamps=True,
            )
            text = " ".join(s.text for s in segments).strip()
            print(f"🔍 Transcription result: '{text}'")
            return text
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return ""

    def start_ptt_recording(self):
        """Starts the PTT recording process in a new thread, with a brief delay."""
        if self.is_recording.is_set():
            return
        # Small delay to allow initial model warm-up on first use
        delay_seconds = 0.75

        def _begin_recording():
            if self.is_recording.is_set():
                return
            self._audio_buffer.clear()
            self.is_recording.set()
            ptt_thread = threading.Thread(target=self._ptt_record_loop, daemon=True)
            ptt_thread.start()
            print("🔴 PTT Recording thread started.")

        timer = threading.Timer(delay_seconds, _begin_recording)
        timer.daemon = True
        timer.start()
        print(f"⏳ Delaying PTT start by {delay_seconds:.2f}s...")

    def stop_ptt_recording(self) -> np.ndarray | None:
        """Stops PTT recording and returns the full audio data."""
        if not self.is_recording.is_set():
            return None
        self.is_recording.clear()
        print("⏹️ PTT Recording stopped.")
        if not self._audio_buffer:
            return None
        full_audio = np.concatenate(list(self._audio_buffer))
        self._audio_buffer.clear()
        return full_audio

    def _ptt_record_loop(self):
        """The loop that actively records audio while PTT is active."""
        try:
            # --- THE FIX IS HERE ---
            # Query the default INPUT device (microphone), not the output device (speakers).
            device_info = sd.query_devices(kind='input')
            device_sr = int(device_info['default_samplerate'])
            chunk_samples = int(device_sr * HOP_SECONDS)
            with sd.InputStream(samplerate=device_sr, channels=1, dtype=np.float32, blocksize=chunk_samples) as stream:
                while self.is_recording.is_set():
                    raw_chunk, overflowed = stream.read(chunk_samples)
                    if overflowed: print("⚠️ Audio buffer overflowed!")
                    audio_chunk_resampled = librosa.resample(
                        raw_chunk.flatten(), orig_sr=device_sr, target_sr=TARGET_SR
                    )
                    self._audio_buffer.append(audio_chunk_resampled)
        except Exception as e:
            print(f"❌ PTT recording loop error: {e}")
        finally:
            self.is_recording.clear()