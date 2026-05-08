"""AfidnaTTS Backend - Generation Orchestrator"""
import threading
import os
from typing import Optional
from backend.core.config import TTS_ROUTING, DEFAULT_ENGINE, AUDIO_DIR
from backend.core.logging import get_logger
from backend.processing.normalization.arabic import arabic_normalizer
from backend.processing.chunking.engine import chunking_engine
from backend.tasks.manager import task_manager
from backend.tts.f5.engine import f5_engine
from backend.utils.cache import cache_system
from backend.alignment.engine import alignment_engine
from backend.processing.post_processing import post_processor
import shutil

logger = get_logger("orchestrator")

class GenerationOrchestrator:
    def start_generation(self, task_id: str, text: str, lang: str = "ar", voice_id: str = None, ref_audio: str = "", ref_text: str = ""):
        # Run in background thread
        thread = threading.Thread(target=self._process, args=(task_id, text, lang, voice_id, ref_audio, ref_text))
        thread.start()

    def _process(self, task_id: str, text: str, lang: str, voice_id: str, ref_audio: str, ref_text: str):
        try:
            # 0. Cache Check
            cached_path = cache_system.check(text, voice_id, lang)
            if cached_path:
                task_manager.update_task(task_id, progress_text="Found in cache, loading...")
                target_path = os.path.join(str(AUDIO_DIR), f"{task_id}.wav")
                shutil.copy(cached_path, target_path)
                post_processor.process(target_path)
                task_manager.update_task(task_id, status="completed", progress=100, output_path=f"/audio/{task_id}.wav")
                # Generate alignment even for cache
                alignment_engine.align(task_id, target_path, text)
                return

            # 1. Normalization
            task_manager.update_task(task_id, progress_text="Normalizing text...")
            if lang == "ar":
                text = arabic_normalizer.normalize(text)
                text = arabic_normalizer.clean_arabic(text)
            
            # 2. Chunking
            task_manager.update_task(task_id, progress_text="Splitting text into chunks...")
            chunks = chunking_engine.split_text(text)
            
            if not chunks:
                task_manager.update_task(task_id, status="failed", progress_text="No text to process after cleaning.")
                return

            # 3. Engine Selection (Routing)
            engine_name = TTS_ROUTING.get(lang, DEFAULT_ENGINE)
            logger.info(f"Using engine '{engine_name}' for language '{lang}'")

            combined_text = " ".join(chunks)
            
            if engine_name == "f5tts":
                f5_engine.generate(task_id, combined_text, ref_audio, ref_text)
                
                # 4. Post-Generation: Cache & Alignment
                target_path = os.path.join(str(AUDIO_DIR), f"{task_id}.wav")
                if os.path.exists(target_path):
                    post_processor.process(target_path)
                    cache_system.save(task_id, text, voice_id, lang)
                    alignment_engine.align(task_id, target_path, combined_text)
            else:
                task_manager.update_task(task_id, status="failed", progress_text=f"Engine {engine_name} not yet implemented.")

        except Exception as e:
            logger.error(f"Critical error in orchestration: {str(e)}")
            task_manager.update_task(task_id, status="failed", progress_text=f"Orchestrator Error: {str(e)}")

orchestrator = GenerationOrchestrator()
