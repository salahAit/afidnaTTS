"""AfidnaTTS Backend - Audio Utilities"""
import subprocess
import os
import shutil
from typing import List
from backend.core.logging import get_logger

logger = get_logger("audio_utils")

def stitch_audio(input_paths: List[str], output_path: str):
    """Stitches multiple audio files into one using FFmpeg concat demuxer."""
    if not input_paths:
        logger.warning("No input paths provided for stitching.")
        return
    
    if len(input_paths) == 1:
        logger.info(f"Only one chunk, copying to {output_path}")
        shutil.copy(input_paths[0], output_path)
        return

    # Create a temporary file list for FFmpeg
    list_file = output_path + ".list.txt"
    try:
        with open(list_file, 'w', encoding='utf-8') as f:
            for path in input_paths:
                # FFmpeg concat demuxer requires absolute paths or relative to list file
                abs_path = os.path.abspath(path)
                f.write(f"file '{abs_path}'\n")
        
        logger.info(f"Stitching {len(input_paths)} chunks into {output_path}")
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", list_file, "-c", "copy", output_path
        ]
        result = subprocess.run(cmd, check=True, stderr=subprocess.PIPE, text=True)
        logger.info(f"Stitching successful: {output_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg stitching failed: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Error during stitching: {str(e)}")
        raise
    finally:
        if os.path.exists(list_file):
            os.remove(list_file)

def get_audio_duration(audio_path: str) -> float:
    """Gets audio duration using ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", audio_path
        ]
        output = subprocess.check_output(cmd).decode().strip()
        return float(output)
    except Exception as e:
        logger.error(f"Failed to get duration for {audio_path}: {str(e)}")
        return 0.0
