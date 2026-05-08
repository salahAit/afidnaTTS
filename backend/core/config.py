"""AfidnaTTS Backend - Core Configuration"""
import os
from pathlib import Path

# ──────────────────────────── Paths ────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
AUDIO_DIR = STORAGE_DIR / "audio"
CACHE_DIR = STORAGE_DIR / "cache"
VOICES_DIR = STORAGE_DIR / "voices"
TIMESTAMPS_DIR = STORAGE_DIR / "timestamps"

for d in [AUDIO_DIR, CACHE_DIR, VOICES_DIR, TIMESTAMPS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ──────────────────────────── TTS Engines ──────────────────────
TTS_ROUTING = {
    "ar": "f5tts",
    "en": "kokoro",
    "fr": "f5tts",
    "zh": "f5tts",
}

DEFAULT_ENGINE = "f5tts"

# ──────────────────────────── F5-TTS Settings ──────────────────
F5_PYTHON = os.environ.get("F5_PYTHON", "/home/msi/f5-tts/venv/bin/python")
F5_OUTPUT_DIR = str(AUDIO_DIR)

# ──────────────────────────── Chunking ─────────────────────────
MIN_CHUNK_SECONDS = 5
MAX_CHUNK_SECONDS = 25
MAX_CHUNK_CHARS = 300  # Safety limit per chunk

# ──────────────────────────── Diacritics ───────────────────────
DIACRITICS_LEVEL_LIGHT = "light"
DIACRITICS_LEVEL_MEDIUM = "medium"
DIACRITICS_LEVEL_FULL = "full"
DEFAULT_DIACRITICS_LEVEL = DIACRITICS_LEVEL_MEDIUM

# ──────────────────────────── Server ───────────────────────────
HOST = "0.0.0.0"
PORT = 8000
CORS_ORIGINS = ["*"]

# ──────────────────────────── GPU ──────────────────────────────
CLEAR_VRAM_AFTER_GENERATION = True
