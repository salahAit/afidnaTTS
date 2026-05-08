"""AfidnaTTS Backend - Audio Post-Processing"""
import subprocess
import os
from backend.core.logging import get_logger

logger = get_logger("post_processing")

class PostProcessor:
    def process(self, audio_path: str):
        """Applies normalization and trimming to the audio file."""
        if not os.path.exists(audio_path):
            return
            
        temp_path = audio_path + ".tmp.wav"
        
        # FFmpeg command:
        # - af loudnorm: Normalizes volume to -14 LUFS (streaming standard)
        # - silenceremove: Removes silence from start and end
        cmd = [
            "ffmpeg", "-y", "-i", audio_path,
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11, silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB:stop_periods=-1:stop_silence=0.1:stop_threshold=-50dB",
            temp_path
        ]
        
        try:
            subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
            os.replace(temp_path, audio_path)
            logger.info(f"Post-processing applied to: {audio_path}")
        except Exception as e:
            logger.error(f"Post-processing failed: {str(e)}")
            if os.path.exists(temp_path): os.remove(temp_path)

post_processor = PostProcessor()
