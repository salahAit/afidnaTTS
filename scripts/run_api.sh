#!/bin/bash

# Path to f5-tts virtual environment
F5_VENV="/home/msi/f5-tts/venv/bin/activate"

echo "Starting F5-TTS API Server..."
source $F5_VENV
python3 /home/msi/f5-tts/api_server.py
