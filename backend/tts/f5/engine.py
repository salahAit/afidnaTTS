"""AfidnaTTS Backend - F5-TTS Engine Wrapper"""
import subprocess
import os
import sys
from backend.core.config import F5_PYTHON, AUDIO_DIR, CLEAR_VRAM_AFTER_GENERATION
from backend.core.logging import get_logger
from backend.tasks.manager import task_manager

logger = get_logger("f5_engine")

class F5Engine:
    def generate(self, task_id: str, text: str, ref_audio: str = "", ref_text: str = ""):
        output_filename = f"{task_id}.wav"
        output_path = os.path.join(str(AUDIO_DIR), output_filename)
        
        task_manager.update_task(task_id, status="running", progress_text="Initializing F5-TTS...")
        
        cmd = [
            F5_PYTHON, "-m", "f5_tts.infer.infer_cli",
            "--gen_text", text,
            "--output_dir", str(AUDIO_DIR),
            "--output_file", output_filename
        ]
        
        if ref_audio:
            cmd.extend(["--ref_audio", ref_audio])
        if ref_text:
            cmd.extend(["--ref_text", ref_text])

        try:
            logger.info(f"Starting F5 generation for task {task_id}")
            process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
            
            for line in process.stderr:
                line = line.strip()
                if not line: continue
                
                # Extract progress percentage if available
                if "%" in line:
                    try:
                        # Simple extraction for tqdm style: " 50%|███"
                        percent = int(line.split("%")[0].split()[-1])
                        task_manager.update_task(task_id, progress=percent, progress_text=line)
                    except:
                        task_manager.update_task(task_id, progress_text=line)
                else:
                    task_manager.update_task(task_id, progress_text=line)

            process.wait()

            if process.returncode == 0 and os.path.exists(output_path):
                task_manager.update_task(task_id, status="completed", progress=100, output_path=f"/audio/{output_filename}")
                logger.info(f"F5 generation successful: {task_id}")
            else:
                task_manager.update_task(task_id, status="failed", progress_text="CLI process failed.")
                logger.error(f"F5 generation failed for {task_id}")

        except Exception as e:
            logger.error(f"Error in F5Engine: {str(e)}")
            task_manager.update_task(task_id, status="failed", progress_text=str(e))
        
        finally:
            if CLEAR_VRAM_AFTER_GENERATION:
                logger.info("Triggering VRAM cleanup (if applicable)")
                # In a real environment, we'd import torch and call empty_cache() here if running in-process
                # But since we use subprocess, VRAM is freed when the process ends.

f5_engine = F5Engine()
