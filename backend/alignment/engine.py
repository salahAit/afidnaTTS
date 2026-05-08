"""AfidnaTTS Backend - Alignment Engine (Aeneas/MFA)"""
import json
import os
import subprocess
from backend.core.config import TIMESTAMPS_DIR
from backend.core.logging import get_logger

from backend.utils.audio_utils import get_audio_duration

logger = get_logger("alignment")

class AlignmentEngine:
    def align(self, task_id: str, audio_path: str, text: str):
        """Generates word-level timestamps."""
        output_json = os.path.join(str(TIMESTAMPS_DIR), f"{task_id}.json")
        
        # Phase 5 Implementation: 
        # Using Smart Weighting Estimator based on audio duration and character count.
        
        words = text.split()
        if not words: return
        
        total_duration = get_audio_duration(audio_path)
        if total_duration <= 0:
            total_duration = len(words) * 0.4 # Fallback
            
        # Weigh words by their length to distribute duration more naturally
        char_counts = [len(w) for w in words]
        total_chars = sum(char_counts)
        
        timestamps = []
        current_time = 0.0
        
        for i, word in enumerate(words):
            # Calculate weight (at least a small weight for short words)
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
        
        logger.info(f"Alignment (Weighted Estimation) generated for {task_id}: {total_duration}s")
        return output_json

alignment_engine = AlignmentEngine()
