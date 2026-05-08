import torch
import sys

ckpt_path = "/home/msi/Documents/base.pt"
try:
    ckpt = torch.load(ckpt_path, map_location="cpu")
    print(f"Type: {type(ckpt)}")
    if isinstance(ckpt, dict):
        print(f"Keys: {ckpt.keys()}")
        if "model_state_dict" in ckpt:
            sd = ckpt["model_state_dict"]
        else:
            sd = ckpt
        
        # Print first 20 keys to identify architecture
        print("\nFirst 20 keys:")
        for i, k in enumerate(list(sd.keys())[:20]):
            print(f"{i}: {k} - {sd[k].shape}")
except Exception as e:
    print(f"Error: {e}")
