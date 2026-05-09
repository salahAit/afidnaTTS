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
            import torch
            
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
                
                # Generate alignment even for cached files if not exists
                combined_text = text # For cache, we use full text
                alignment_engine.align(task_id, target_path, combined_text)
                
                task_manager.update_task(task_id, status="completed", progress=100, output_path=f"/audio/{task_id}.wav")
                return

            # 1. Normalization & Diacritization
            task_manager.update_task(task_id, progress_text="Preparing text...")
            if lang == "ar":
                text = arabic_normalizer.normalize(text)
                from backend.processing.diacritics.engine import diacritics_engine
                text = diacritics_engine.process(text)
                text = arabic_normalizer.clean_arabic(text)
            
            # 2. Chunking
            task_manager.update_task(task_id, progress_text="Chunking text for optimal quality...")
            chunks = chunking_engine.split_text(text)
            
            if not chunks:
                task_manager.update_task(task_id, status="failed", progress_text="No text to process after cleaning.")
                return

            # 3. Engine Selection (Routing)
            engine_name = TTS_ROUTING.get(lang, DEFAULT_ENGINE)
            logger.info(f"Using engine '{engine_name}' for language '{lang}'")

            chunk_files = []
            target_path = os.path.join(str(AUDIO_DIR), f"{task_id}.wav")

            if engine_name == "f5tts":
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{task_id}_chunk_{i}"
                    chunk_path = os.path.join(str(AUDIO_DIR), f"{chunk_id}.wav")
                    task_manager.update_task(task_id, progress=int((i/len(chunks))*100), progress_text=f"Generating chunk {i+1}/{len(chunks)}...")
                    f5_engine.generate(chunk_id, chunk, ref_audio, ref_text, custom_output=chunk_path, lang=lang)
                    if os.path.exists(chunk_path):
                        chunk_files.append(chunk_path)
                    else:
                        raise Exception(f"Chunk {i} generation failed.")
            
            elif engine_name == "kokoro":
                from backend.tts.kokoro.engine import kokoro_engine
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{task_id}_chunk_{i}"
                    chunk_path = os.path.join(str(AUDIO_DIR), f"{chunk_id}.wav")
                    task_manager.update_task(task_id, progress=int((i/len(chunks))*100), progress_text=f"Generating English/French chunk {i+1}/{len(chunks)}...")
                    kokoro_engine.generate(chunk_id, chunk, voice_id, custom_output=chunk_path)
                    if os.path.exists(chunk_path):
                        chunk_files.append(chunk_path)
                    else:
                        raise Exception(f"Kokoro chunk {i} failed.")
            else:
                raise Exception(f"Engine {engine_name} not supported.")

            # 4. Stitching & Post-processing
            if chunk_files:
                task_manager.update_task(task_id, progress_text="Polishing audio...")
                from backend.utils.audio_utils import stitch_audio
                stitch_audio(chunk_files, target_path)
                
                # Cleanup chunks
                for cf in chunk_files:
                    try: os.remove(cf)
                    except: pass

                if os.path.exists(target_path):
                    # Normalization & Silence Removal
                    post_processor.process(target_path)
                    
                    # Cache & Alignment
                    cache_system.save(task_id, text, voice_id, lang)
                    ts_path = alignment_engine.align(task_id, target_path, " ".join(chunks), lang=lang)
                    
                    task_manager.update_task(
                        task_id, 
                        status="completed", 
                        progress=100, 
                        output_path=f"/audio/{task_id}.wav",
                        timestamps_path=ts_path
                    )
            
        except Exception as e:
            logger.error(f"Critical error in orchestration: {str(e)}")
            task_manager.update_task(task_id, status="failed", progress_text=f"Error: {str(e)}")
        
        finally:
            # Task 7: Mandatory GPU Memory Clear
            try:
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    logger.info("VRAM cache cleared successfully")
            except:
                pass

orchestrator = GenerationOrchestrator()

orchestrator = GenerationOrchestrator()
