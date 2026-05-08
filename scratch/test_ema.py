import torch
import os
import sys

# Add F5-TTS to path if needed
# sys.path.append("/home/msi/f5-tts/venv/lib/python3.12/site-packages")

from f5_tts.model import DiT
from f5_tts.infer.utils_infer import load_model

ckpt_path = "/home/msi/Documents/base.pt"
vocab_file = "backend/storage/arabic_model/vocab.txt"
model_cfg_path = "backend/storage/arabic_model/F5TTS_Base_8_18.yaml"

import yaml
with open(model_cfg_path, 'r') as f:
    model_cfg = yaml.safe_load(f)

device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Testing load_model with use_ema=False...")
try:
    model = load_model(
        DiT,
        model_cfg,
        ckpt_path,
        vocab_file=vocab_file,
        use_ema=False,
        device=device
    )
    print("SUCCESS: Model loaded with use_ema=False!")
except Exception as e:
    print(f"FAILED: {str(e)}")

print("\nTesting load_model with use_ema=True (should fail)...")
try:
    model = load_model(
        DiT,
        model_cfg,
        ckpt_path,
        vocab_file=vocab_file,
        use_ema=True,
        device=device
    )
    print("SUCCESS: Model loaded with use_ema=True (Unexpected!)")
except Exception as e:
    print(f"EXPECTED FAILURE: {str(e)}")
