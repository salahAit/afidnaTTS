"""AfidnaTTS Backend - Alignment Engine (Aeneas/MFA)"""
import json
import os
import subprocess
from backend.core.config import TIMESTAMPS_DIR
from backend.core.logging import get_logger

from backend.utils.audio_utils import get_audio_duration

logger = get_logger("alignment")

class AlignmentEngine:
    def align(self, task_id: str, audio_path: str, text: str, lang: str = "ar"):
        """Generates word-level timestamps using Aeneas or Weighted Estimation."""
        output_json = os.path.join(str(TIMESTAMPS_DIR), f"{task_id}.json")
        
        words = text.split()
        if not words: return
        
        # Try Aeneas first
        try:
            # We use a subprocess call to aeneas to avoid C extension issues in the main process
            # Requirement: aeneas must be installed in the venv
            import tempfile
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write("\n".join(words))
                text_file = f.name
                
            cmd = [
                "python", "-m", "aeneas.tools.execute_task",
                audio_path, text_file,
                "task_language=ara|os_task_file_format=json|is_text_type=plain",
                output_json
            ]
            
            # Change language based on input
            if lang != "ar":
                cmd[3] = cmd[3].replace("ara", "eng") # Default to eng for non-arabic

            # For now, we'll check if aeneas is installed
            import aeneas
            subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
            
            if os.path.exists(output_json):
                # Aeneas output needs to be mapped to our word-level format
                with open(output_json, 'r') as f:
                    data = json.load(f)
                
                # Aeneas usually outputs fragments. If we gave it one word per line, 
                # fragments correspond to words.
                formatted = []
                for i, fragment in enumerate(data.get('fragments', [])):
                    formatted.append({
                        "word": words[i] if i < len(words) else "",
                        "start": float(fragment['begin']),
                        "end": float(fragment['end'])
                    })
                
                with open(output_json, 'w', encoding='utf-8') as f:
                    json.dump(formatted, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Aeneas alignment successful for {task_id}")
                return output_json

        except Exception as e:
            logger.warning(f"Aeneas failed or not installed, falling back to weighted estimation: {e}")

        # Fallback: Weighted Estimation
        total_duration = get_audio_duration(audio_path)
        if total_duration <= 0:
            total_duration = len(words) * 0.4
            
        char_counts = [len(w) for w in words]
        total_chars = sum(char_counts)
        
        timestamps = []
        current_time = 0.0
        
        for i, word in enumerate(words):
            word_weight = char_counts[i] / total_chars
            word_duration = total_duration * word_weight
            
            start = round(current_time, 3)
            end = round(current_time + word_duration, 3)
            
            timestamps.append({
                "word": word,
                "start": start,
                "end": end
            })
            current_time = end
            
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(timestamps, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Weighted estimation alignment generated for {task_id}")
        return output_json

alignment_engine = AlignmentEngine()
