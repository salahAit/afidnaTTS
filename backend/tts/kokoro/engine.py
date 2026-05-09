"""AfidnaTTS Backend - Kokoro TTS Engine Wrapper"""
import os
import soundfile as sf
from backend.core.config import AUDIO_DIR, STORAGE_DIR
from backend.core.logging import get_logger

logger = get_logger("kokoro_engine")

class KokoroEngine:
    def __init__(self):
        self.kokoro = None
        self.model_path = str(STORAGE_DIR / "kokoro" / "kokoro-v0_19.onnx")
        self.voices_path = str(STORAGE_DIR / "kokoro" / "voices.bin")
        self._initialized = False

    def _initialize(self):
        if self._initialized: return
        try:
            from kokoro_onnx import Kokoro
            if not os.path.exists(self.model_path):
                logger.error(f"Kokoro model not found at {self.model_path}")
                return
            
            self.kokoro = Kokoro(self.model_path, self.voices_path)
            self._initialized = True
            logger.info("Kokoro TTS Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kokoro: {e}")

    def generate(self, task_id: str, text: str, voice_id: str = "af_bella", custom_output: str = None):
        output_path = custom_output if custom_output else os.path.join(str(AUDIO_DIR), f"{task_id}.wav")
        
        self._initialize()
        if not self._initialized:
            raise Exception("Kokoro engine not initialized")
            
        try:
            # Kokoro voice IDs are like 'af_bella', 'am_adam', etc.
            # Defaulting to af_bella if not provided
            voice = voice_id if voice_id and "_" in voice_id else "af_bella"
            
            samples, sample_rate = self.kokoro.create(text, voice=voice, speed=1.0, lang="en-us")
            sf.write(output_path, samples, sample_rate)
            logger.info(f"Kokoro generation successful: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Kokoro generation failed: {e}")
            raise e

kokoro_engine = KokoroEngine()
