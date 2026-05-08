"""AfidnaTTS Backend - Alignment Engine (Aeneas/MFA)"""
import json
import os
import subprocess
from backend.core.config import TIMESTAMPS_DIR
from backend.core.logging import get_logger

logger = get_logger("alignment")

class AlignmentEngine:
    def align(self, task_id: str, audio_path: str, text: str):
        """Generates word-level timestamps."""
        output_json = os.path.join(str(TIMESTAMPS_DIR), f"{task_id}.json")
        
        # Phase 5 Implementation: 
        # For now, we'll implement a 'Smart Estimator' that we can later 
        # swap with a real Aeneas/MFA call.
        
        words = text.split()
        if not words: return
        
        # Placeholder for real alignment logic
        # In a production environment, we'd call aeneas here.
        
        # Simulation of timestamp generation for the UI
        # (Assuming average speaking rate of 150 words per minute)
        duration_per_word = 0.4 # seconds
        timestamps = []
        current_time = 0.0
        
        for word in words:
            start = round(current_time, 3)
            end = round(current_time + duration_per_word, 3)
            timestamps.append({
                "word": word,
                "start": start,
                "end": end
            })
            current_time = end
            
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(timestamps, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Alignment generated for {task_id}")
        return output_json

alignment_engine = AlignmentEngine()
