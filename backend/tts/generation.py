"""AfidnaTTS Backend - Generation Orchestrator"""
import threading
import os
from typing import Optional
from backend.core.config import TTS_ROUTING, DEFAULT_ENGINE, AUDIO_DIR, VOICES_DIR
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
        thread = threading.Thread(target=self._process, args=(task_id, text, lang, voice_id, ref_audio, ref_text))
        thread.start()

    def _process(self, task_id: str, text: str, lang: str, voice_id: str, ref_audio: str, ref_text: str):
        try:
            # Default Arabic reference voice (from IbrahimSalah/Arabic-F5-TTS-v2)
            if lang == "ar" and not ref_audio:
                ref_audio = str(VOICES_DIR / "arabic_ref.wav")
                if not ref_text:
                    ref_text = "لا يمر يوم إلا وأستقبل عدة رسائل تتضمن أسئلة ملحة"

            # 0. Cache Check
            cached_path = cache_system.check(text, voice_id, lang)
            if cached_path:
                task_manager.update_task(task_id, progress_text="Found in cache, loading...")
                target_path = os.path.join(str(AUDIO_DIR), f"{task_id}.wav")
                shutil.copy(cached_path, target_path)
                post_processor.process(target_path)
                task_manager.update_task(task_id, status="completed", progress=100, output_path=f"/audio/{task_id}.wav")
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

            if engine_name == "f5tts":
                chunk_files = []
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{task_id}_chunk_{i}"
                    chunk_path = os.path.join(str(AUDIO_DIR), f"{chunk_id}.wav")
                    task_manager.update_task(task_id, progress_text=f"Generating chunk {i+1}/{len(chunks)}...")
                    f5_engine.generate(chunk_id, chunk, ref_audio, ref_text, custom_output=chunk_path, lang=lang)
                    if os.path.exists(chunk_path):
                        chunk_files.append(chunk_path)
                    else:
                        raise Exception(f"Chunk {i} generation failed.")
                
                # 4. Stitching
                task_manager.update_task(task_id, progress_text="Stitching audio chunks...")
                target_path = os.path.join(str(AUDIO_DIR), f"{task_id}.wav")
                from backend.utils.audio_utils import stitch_audio
                stitch_audio(chunk_files, target_path)
                
                # Cleanup chunks
                for cf in chunk_files:
                    try: os.remove(cf)
                    except: pass

                # 5. Post-Generation: Cache & Alignment
                if os.path.exists(target_path):
                    post_processor.process(target_path)
                    cache_system.save(task_id, text, voice_id, lang)
                    combined_text = " ".join(chunks)
                    alignment_engine.align(task_id, target_path, combined_text)
                    
                    task_manager.update_task(task_id, status="completed", progress=100, output_path=f"/audio/{task_id}.wav")
            else:
                task_manager.update_task(task_id, status="failed", progress_text=f"Engine {engine_name} not yet implemented.")

        except Exception as e:
            logger.error(f"Critical error in orchestration: {str(e)}")
            task_manager.update_task(task_id, status="failed", progress_text=f"Orchestrator Error: {str(e)}")

orchestrator = GenerationOrchestrator()
