#!/usr/bin/env python3
"""
Example script showing how to run a converted ComfyUI workflow
This example demonstrates running a FLUX workflow
"""

import torch
from diffusers import FluxPipeline
from PIL import Image
import os

def run_flux_example():
    """Run a simple FLUX generation example"""
    
    # Check device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    dtype = torch.float16 if device == 'cuda' else torch.float32
    print(f'Using device: {device} with dtype: {dtype}')
    
    # Note: For actual usage, you would need to install the model
    # This is just a demonstration of the structure
    
    print("Example: Loading FLUX pipeline...")
    print("pipe = FluxPipeline.from_pretrained('black-forest-labs/FLUX.1-schnell', torch_dtype=dtype).to(device)")
    
    # Example parameters (from converted workflow)
    prompt = "detailed cinematic render of an old dusty CRT monitor on a wooden desk"
    width = 1024
    height = 1024
    num_inference_steps = 4  # FLUX.1-schnell uses fewer steps
    guidance_scale = 0.0      # FLUX.1-schnell doesn't use guidance
    
    print(f"\nExample parameters:")
    print(f"Prompt: {prompt}")
    print(f"Size: {width}x{height}")
    print(f"Steps: {num_inference_steps}")
    print(f"Guidance: {guidance_scale}")
    
    print(f"\nExample generation code:")
    print(f"with torch.no_grad():")
    print(f"    result = pipe(")
    print(f"        prompt='{prompt}',")
    print(f"        width={width},")
    print(f"        height={height},")
    print(f"        num_inference_steps={num_inference_steps},")
    print(f"        guidance_scale={guidance_scale},")
    print(f"    )")
    print(f"    image = result.images[0]")
    print(f"    image.save('generated_image.png')")
    
    print(f"\n💡 To actually run this:")
    print(f"1. Install dependencies: pip install -r requirements.txt")
    print(f"2. Run a converted script: python converted_scripts/FLUX.1\\ SCHNELL\\ 1.0.py")
    print(f"3. Wait for model download (first time only)")
    print(f"4. Generated image will be saved as 'generated_image.png'")

def show_available_scripts():
    """Show available converted scripts"""
    converted_dir = "converted_scripts"
    
    if not os.path.exists(converted_dir):
        print(f"Directory {converted_dir} not found. Run 'python convert.py --all' first.")
        return
    
    scripts = [f for f in os.listdir(converted_dir) if f.endswith('.py')]
    
    print(f"\nAvailable converted scripts ({len(scripts)} total):")
    print("=" * 50)
    
    for script in sorted(scripts):
        print(f"  📄 {script}")
    
    print(f"\nTo run a script:")
    print(f"  python 'converted_scripts/{scripts[0] if scripts else 'script_name.py'}'")

if __name__ == "__main__":
    print("🎨 ComfyUI Workflow Converter - Example Runner")
    print("=" * 60)
    
    run_flux_example()
    show_available_scripts()
    
    print("\n" + "=" * 60)
    print("🚀 Ready to generate amazing images with converted workflows!")
