"""AfidnaTTS Backend - Cache System"""
import hashlib
import os
import shutil
from backend.core.config import CACHE_DIR, AUDIO_DIR
from backend.core.logging import get_logger

logger = get_logger("cache")

class CacheSystem:
    def get_hash(self, text: str, voice_id: str, lang: str) -> str:
        """Creates a unique hash for the generation parameters."""
        data = f"{text}|{voice_id}|{lang}"
        return hashlib.md5(data.encode()).hexdigest()

    def check(self, text: str, voice_id: str, lang: str) -> Optional[str]:
        """Returns the path to the cached audio if it exists."""
        h = self.get_hash(text, voice_id, lang)
        cache_path = os.path.join(str(CACHE_DIR), f"{h}.wav")
        if os.path.exists(cache_path):
            logger.info(f"Cache hit for hash: {h}")
            return cache_path
        return None

    def save(self, task_id: str, text: str, voice_id: str, lang: str):
        """Saves a generated audio to the cache."""
        h = self.get_hash(text, voice_id, lang)
        src = os.path.join(str(AUDIO_DIR), f"{task_id}.wav")
        dst = os.path.join(str(CACHE_DIR), f"{h}.wav")
        if os.path.exists(src):
            shutil.copy(src, dst)
            logger.info(f"Saved to cache: {h}")

cache_system = CacheSystem()
