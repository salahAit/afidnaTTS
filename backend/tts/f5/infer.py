import os
import sys
import torch
import torchaudio
import argparse
from pathlib import Path
from omegaconf import OmegaConf

# Add current directory to sys.path to find backend modules if needed
sys.path.append(os.getcwd())

from f5_tts.model import DiT
from hydra.utils import get_class
from f5_tts.infer.utils_infer import (
    load_model, 
    load_vocoder, 
    preprocess_ref_audio_text, 
    infer_process,
    remove_silence_for_generated_wav
)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gen_text", type=str, required=True)
    parser.add_argument("--ref_audio", type=str, default="")
    parser.add_argument("--ref_text", type=str, default="")
    parser.add_argument("--output_dir", type=str, default="output")
    parser.add_argument("--output_file", type=str, default="out.wav")
    parser.add_argument("--ckpt_file", type=str, required=True)
    parser.add_argument("--vocab_file", type=str, required=True)
    parser.add_argument("--model_cfg", type=str, required=True)
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--use_ema", action="store_true", default=False)
    
    args = parser.parse_args()
    
    print(f"Loading model from {args.ckpt_file}...")
    
    # Load config
    model_cfg = OmegaConf.load(args.model_cfg)
    model_cls = get_class(f"f5_tts.model.{model_cfg.model.backbone}")
    model_arc = model_cfg.model.arch
    
    # Load model
    model_obj = load_model(
        model_cls, 
        model_arc, 
        args.ckpt_file, 
        vocab_file=args.vocab_file, 
        device=args.device, 
        use_ema=args.use_ema
    )
    
    # Load vocoder
    vocoder = load_vocoder(device=args.device)
    
    # Prepare output
    out_path = Path(args.output_dir) / args.output_file
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Preprocess reference
    ref_audio = args.ref_audio
    ref_text = args.ref_text
    
    if not ref_audio:
        # If no ref audio, we might need a default one or handle it
        # For now, F5 needs a ref. We can use a silent one or a placeholder if allowed.
        # But usually we expect a ref_audio.
        pass
    
    if ref_audio:
        ref_audio, ref_text = preprocess_ref_audio_text(ref_audio, ref_text)
    
    print(f"Generating: {args.gen_text[:50]}...")
    
    # Generate
    audio, sr, _ = infer_process(
        ref_audio,
        ref_text,
        args.gen_text,
        model_obj,
        vocoder,
        device=args.device
    )
    
    # Save
    if audio is not None:
        torchaudio.save(str(out_path), torch.from_numpy(audio).unsqueeze(0), sr)
        print(f"Saved to {out_path}")
        
        # Post-process
        # remove_silence_for_generated_wav(str(out_path))
    else:
        print("Generation failed: audio is None")
        sys.exit(1)

if __name__ == "__main__":
    main()
