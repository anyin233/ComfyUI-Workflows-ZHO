import json
import argparse
import os
from typing import Dict, Any, List, Optional, Tuple

class ComfyUIToScript:
    def __init__(self):
        self.node_mappings = {
            # Basic loaders
            "CheckpointLoaderSimple": self._convert_checkpoint_loader,
            "DualCLIPLoader": self._convert_dual_clip_loader,
            "VAELoader": self._convert_vae_loader,
            "UNETLoader": self._convert_unet_loader,
            "LoraLoader": self._convert_lora_loader,
            
            # Text encoding
            "CLIPTextEncode": self._convert_clip_text_encode,
            "CLIPTextEncodeFlux": self._convert_clip_text_encode_flux,
            
            # Sampling and generation
            "KSampler": self._convert_ksampler,
            "KSamplerAdvanced": self._convert_ksampler_advanced,
            "SamplerCustomAdvanced": self._convert_sampler_custom_advanced,
            "BasicScheduler": self._convert_basic_scheduler,
            "BasicGuider": self._convert_basic_guider,
            
            # Image processing
            "VAEDecode": self._convert_vae_decode,
            "VAEEncode": self._convert_vae_encode,
            "EmptyLatentImage": self._convert_empty_latent,
            "LatentUpscale": self._convert_latent_upscale,
            
            # Image output
            "SaveImage": self._convert_save_image,
            "PreviewImage": self._convert_preview_image,
            
            # ControlNet and additional features
            "ControlNetLoader": self._convert_controlnet_loader,
            "ControlNetApply": self._convert_controlnet_apply,
            
            # Model Context Protocol and custom nodes
            "PortraitMaster_中文版": self._convert_portrait_master,
            "Sketch to 3D": self._convert_sketch_to_3d,
            "LivePortrait": self._convert_live_portrait,
            
            # Special workflow nodes
            "workflow/FLUX": self._convert_workflow_flux,
            "workflow/SD3": self._convert_workflow_sd3,
            
            # SD3-specific nodes
            "TripleCLIPLoader": self._convert_triple_clip_loader,
            "EmptySD3LatentImage": self._convert_empty_sd3_latent,
            "ModelSamplingSD3": self._convert_model_sampling_sd3,
            "ConditioningSetTimestepRange": self._convert_conditioning_timestep,
            "ConditioningZeroOut": self._convert_conditioning_zero_out,
            "ConditioningCombine": self._convert_conditioning_combine,
            "PrimitiveNode": self._convert_primitive_node,
            
            # Additional nodes that might appear
            "FluxGuidance": self._convert_flux_guidance,
            "RandomNoise": self._convert_random_noise,
            "SamplerCustom": self._convert_sampler_custom,
            "KSamplerSelect": self._convert_ksampler_select,
            "BasicScheduler": self._convert_basic_scheduler,
            "SamplerCustomAdvanced": self._convert_sampler_custom_advanced,
        }
        
        # Keep track of variables for proper code generation
        self.variables = {
            'model': None,
            'clip': None,
            'vae': None,
            'pipe': None,
            'prompt': None,
            'negative_prompt': None,
            'image': None,
            'latent': None,
            'width': 512,
            'height': 512,
        }
        
        # Node replacement strategies for incompatible nodes
        self.node_replacements = {
            # Video/Animation nodes -> Static image generation
            "VHS_VideoCombine": self._replace_video_combine,
            "VHS_LoadVideo": self._replace_video_load,
            "LivePortraitProcess": self._replace_live_portrait,
            "LivePortraitComposite": self._replace_live_portrait_composite,
            "LivePortraitLoadFaceAlignmentCropper": self._replace_face_alignment,
            "DownloadAndLoadLivePortraitModels": self._replace_model_download,
            
            # 3D generation nodes -> 2D alternatives
            "CRM": self._replace_3d_generation,
            "InstantMesh": self._replace_instant_mesh,
            "TripoSR": self._replace_triposr,
            
            # Advanced sampling nodes -> Basic alternatives
            "RandomNoise": self._replace_random_noise,
            "KSamplerSelect": self._replace_ksampler_select,
            "SamplerCustomAdvanced": self._replace_custom_sampler,
            
            # Image processing nodes -> PIL/CV2 alternatives
            "ImageScale": self._replace_image_scale,
            "ImageResize": self._replace_image_resize,
            "ImageCrop": self._replace_image_crop,
            "ImageRotate": self._replace_image_rotate,
            
            # Text processing nodes -> Direct text handling
            "CLIPTextEncodeSDXL": self._replace_sdxl_text_encode,
            "CLIPTextEncodeSD3": self._replace_sd3_text_encode,
            
            # Custom workflow nodes -> Standard equivalents
            "workflow/anything": self._replace_custom_workflow,
            "workflow/SDXL": self._replace_sdxl_workflow,
            
            # ControlNet variants -> Standard ControlNet
            "ControlNetApplyAdvanced": self._replace_controlnet_advanced,
            "MultiControlNetApply": self._replace_multi_controlnet,
            
            # LoRA variants -> Standard LoRA
            "LoraLoaderModelOnly": self._replace_lora_model_only,
            "LoraLoaderTaggedCLIP": self._replace_lora_tagged,
        }
        
    def convert_workflow(self, workflow_path: str, output_path: str):
        """Convert ComfyUI workflow to Python script"""
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow = json.load(f)
        except Exception as e:
            print(f"Error reading workflow file {workflow_path}: {e}")
            return False
        
        print(f"Converting workflow: {os.path.basename(workflow_path)}")
        
        # Reset variables for each workflow
        self.variables = {
            'model': None,
            'clip': None,
            'vae': None,
            'pipe': None,
            'prompt': None,
            'negative_prompt': None,
            'image': None,
            'latent': None,
            'width': 512,
            'height': 512,
        }
        
        script_lines = self._generate_script_header()
        
        # Parse nodes and generate code
        nodes = workflow.get('nodes', []) if 'nodes' in workflow else workflow
        
        # First pass: identify model type and setup
        model_type = self._identify_model_type(nodes)
        print(f"  Detected model type: {model_type}")
        script_lines.extend(self._generate_model_setup(model_type))
        
        # Second pass: process nodes in execution order
        execution_order = self._get_execution_order(nodes)
        print(f"  Processing {len(execution_order)} nodes...")
        
        unsupported_nodes = []
        for node_id in execution_order:
            node = self._find_node_by_id(nodes, node_id)
            if node:
                node_type = node.get('type', '')
                code = self._convert_node(node)
                if code:
                    # Check if this was an unsupported node
                    if any('Unsupported node type' in line for line in code):
                        unsupported_nodes.append(node_type)
                    script_lines.extend(code)
        
        if unsupported_nodes:
            print(f"  Warning: {len(unsupported_nodes)} unsupported node types: {', '.join(set(unsupported_nodes))}")
        
        # Add final generation code if needed
        script_lines.extend(self._generate_final_code(model_type))
        
        # Write output script
        try:
            output_dir = os.path.dirname(output_path)
            if output_dir and output_dir != '.':
                os.makedirs(output_dir, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(script_lines))
            print(f"  ✓ Saved to: {output_path}")
            return True
        except Exception as e:
            print(f"  ✗ Error writing output file {output_path}: {e}")
            return False
    
    def _identify_model_type(self, nodes: List[Dict]) -> str:
        """Identify the type of model being used"""
        for node in nodes:
            if not isinstance(node, dict):
                continue
                
            node_type = node.get('type', '')
            inputs = node.get('inputs', {})
            widgets = node.get('widgets_values', [])
            
            if node_type == 'CheckpointLoaderSimple' and widgets:
                model_name = widgets[0].lower()
                if 'flux' in model_name:
                    return 'flux'
                elif 'sd3' in model_name:
                    return 'sd3'
                elif 'cascade' in model_name:
                    return 'cascade'
                elif 'sdxl' in model_name or 'xl' in model_name:
                    return 'sdxl'
                else:
                    return 'sd'
            elif node_type == 'DualCLIPLoader':
                return 'flux'
            elif 'HUNYUAN' in str(node):
                return 'hunyuan'
            elif '3D' in str(node):
                return '3d'
        
        return 'sd'  # default
    
    def _generate_model_setup(self, model_type: str) -> List[str]:
        """Generate model-specific setup code"""
        setup_code = []
        
        if model_type == 'flux':
            setup_code.extend([
                "# FLUX model setup",
                "from diffusers import FluxPipeline",
                "import torch",
                "",
            ])
        elif model_type == 'sd3':
            setup_code.extend([
                "# Stable Diffusion 3 setup", 
                "from diffusers import StableDiffusion3Pipeline",
                "import torch",
                "",
            ])
        elif model_type == 'cascade':
            setup_code.extend([
                "# Stable Cascade setup",
                "from diffusers import StableCascadePriorPipeline, StableCascadeDecoderPipeline",
                "import torch",
                "",
            ])
        elif model_type == 'sdxl':
            setup_code.extend([
                "# Stable Diffusion XL setup",
                "from diffusers import StableDiffusionXLPipeline",
                "import torch",
                "",
            ])
        elif model_type == '3d':
            setup_code.extend([
                "# 3D generation setup",
                "# Note: 3D workflows require specialized libraries",
                "import torch",
                "",
            ])
        else:
            setup_code.extend([
                "# Standard Stable Diffusion setup",
                "from diffusers import StableDiffusionPipeline",
                "import torch",
                "",
            ])
            
        return setup_code
    
    def _generate_final_code(self, model_type: str) -> List[str]:
        """Generate final execution code"""
        final_code = []
        
        # Only add final generation if image wasn't already generated
        if not self.variables.get('image'):
            final_code.extend([
                "",
                "# Final image generation",
                "if 'pipe' in locals() and pipe is not None:",
                "    print('Starting image generation...')",
                "    with torch.no_grad():",
            ])
            
            # Model-specific generation parameters
            if model_type == 'flux':
                final_code.extend([
                "        result = pipe(",
                "            prompt=prompt if 'prompt' in locals() else 'a beautiful landscape',",
                "            width=width if 'width' in locals() else 1024,",
                "            height=height if 'height' in locals() else 1024,",
                "            num_inference_steps=num_inference_steps if 'num_inference_steps' in locals() else 4,",
                "            guidance_scale=guidance_scale if 'guidance_scale' in locals() else 0.0,",
                "            generator=generator if 'generator' in locals() else None,",
                "        )",
                ])
            elif model_type == 'sd3':
                final_code.extend([
                "        result = pipe(",
                "            prompt=prompt if 'prompt' in locals() else 'a beautiful landscape',",
                "            negative_prompt=negative_prompt if 'negative_prompt' in locals() else None,",
                "            width=width if 'width' in locals() else 1024,",
                "            height=height if 'height' in locals() else 1024,",
                "            num_inference_steps=num_inference_steps if 'num_inference_steps' in locals() else 28,",
                "            guidance_scale=guidance_scale if 'guidance_scale' in locals() else 7.0,",
                "            generator=generator if 'generator' in locals() else None,",
                "        )",
                ])
            else:
                final_code.extend([
                "        result = pipe(",
                "            prompt=prompt if 'prompt' in locals() else 'a beautiful landscape',",
                "            negative_prompt=negative_prompt if 'negative_prompt' in locals() else None,",
                "            num_inference_steps=num_inference_steps if 'num_inference_steps' in locals() else 20,",
                "            guidance_scale=guidance_scale if 'guidance_scale' in locals() else 7.5,",
                "            width=width if 'width' in locals() else 512,",
                "            height=height if 'height' in locals() else 512,",
                "            generator=generator if 'generator' in locals() else None,",
                "        )",
                ])
            
            final_code.extend([
                "",
                "        if hasattr(result, 'images'):",
                "            image = result.images[0]",
                "        else:",
                "            image = result",
                "        ",
                "        # Save the generated image",
                "        output_path = 'generated_image.png'",
                "        image.save(output_path)",
                "        print(f'✓ Image saved as {output_path}')",
                "        ",
                "        # Display image if possible",
                "        try:",
                "            image.show()",
                "        except:",
                "            print('Image display not available in this environment')",
                "",
                "else:",
                "    print('❌ Pipeline not properly initialized')",
                "",
            ])
        else:
            final_code.extend([
                "",
                "# Image was generated in workflow",
                "if 'image' in locals() and image is not None:",
                "    print('✓ Workflow completed successfully')",
                "",
            ])
        
        return final_code
    
    def _generate_script_header(self) -> List[str]:
        """Generate import statements and setup code"""
        return [
            "#!/usr/bin/env python3",
            "\"\"\"",
            "Generated from ComfyUI workflow",
            "This script converts ComfyUI workflow to use diffusers, transformers and other standard libraries",
            "\"\"\"",
            "",
            "import torch",
            "import numpy as np",
            "from PIL import Image",
            "import os",
            "import requests",
            "from typing import Optional, Union, List",
            "",
            "# Check for GPU availability",
            "device = 'cuda' if torch.cuda.is_available() else 'cpu'",
            "dtype = torch.float16 if device == 'cuda' else torch.float32",
            "print(f'Using device: {device} with dtype: {dtype}')",
            "",
        ]
    
    def _get_execution_order(self, nodes: List[Dict]) -> List[str]:
        """Determine execution order based on node connections"""
        # Simple but effective ordering strategy
        node_ids = []
        
        # Define execution priority groups
        priority_groups = [
            # Group 1: Model and component loaders (must be first)
            ['CheckpointLoaderSimple', 'DualCLIPLoader', 'VAELoader', 'UNETLoader'],
            # Group 2: LoRA and additional model components
            ['LoraLoader', 'ControlNetLoader'],
            # Group 3: Input preparation
            ['EmptyLatentImage', 'LoadImage'],
            # Group 4: Text encoding and conditioning
            ['CLIPTextEncode', 'CLIPTextEncodeFlux', 'CLIPTextEncodeSD3'],
            # Group 5: Sampling configuration
            ['BasicScheduler', 'BasicGuider', 'RandomNoise', 'KSamplerSelect'],
            # Group 6: Generation and sampling
            ['KSampler', 'KSamplerAdvanced', 'SamplerCustom', 'SamplerCustomAdvanced'],
            # Group 7: Post-processing
            ['VAEDecode', 'VAEEncode', 'LatentUpscale'],
            # Group 8: Output and workflow
            ['SaveImage', 'PreviewImage', 'workflow/FLUX', 'workflow/SD3'],
        ]
        
        # Add nodes by priority groups
        for group in priority_groups:
            for node in nodes:
                if (isinstance(node, dict) and 
                    node.get('type') in group and 
                    str(node.get('id', '')) not in node_ids):
                    node_ids.append(str(node.get('id', '')))
        
        # Add any remaining nodes
        for node in nodes:
            if isinstance(node, dict):
                node_id = str(node.get('id', ''))
                if node_id and node_id not in node_ids:
                    node_ids.append(node_id)
                    
        return node_ids
    
    def _find_node_by_id(self, nodes: List[Dict], node_id: str) -> Optional[Dict]:
        """Find node by ID"""
        for node in nodes:
            if isinstance(node, dict) and str(node.get('id', '')) == node_id:
                return node
        return None
    
    def _convert_node(self, node: Dict[str, Any]) -> List[str]:
        """Convert a single node to Python code"""
        node_type = node.get('type', '')
        
        # First try direct mapping
        converter = self.node_mappings.get(node_type)
        if converter:
            return converter(node)
        
        # Then try replacement strategy
        replacement = self.node_replacements.get(node_type)
        if replacement:
            return replacement(node)
        
        # If no mapping found, try to find similar nodes
        similar_replacement = self._find_similar_node_replacement(node_type)
        if similar_replacement:
            return similar_replacement(node)
        
        # Last resort: unsupported node with suggestions
        suggestions = self._get_replacement_suggestions(node_type)
        result = [f"# Unsupported node type: {node_type}"]
        if suggestions:
            result.extend(suggestions)
        return result
    
    def _find_similar_node_replacement(self, node_type: str) -> Optional[callable]:
        """Find replacement for similar node types"""
        node_type_lower = node_type.lower()
        
        # Text encoding variants
        if 'cliptext' in node_type_lower and 'encode' in node_type_lower:
            return self._convert_clip_text_encode
        
        # Sampler variants
        if 'sampler' in node_type_lower or 'ksampler' in node_type_lower:
            return self._convert_ksampler
        
        # Loader variants
        if 'loader' in node_type_lower:
            if 'checkpoint' in node_type_lower or 'model' in node_type_lower:
                return self._convert_checkpoint_loader
            elif 'lora' in node_type_lower:
                return self._convert_lora_loader
            elif 'vae' in node_type_lower:
                return self._convert_vae_loader
        
        # Image processing variants
        if 'image' in node_type_lower:
            if 'save' in node_type_lower:
                return self._convert_save_image
            elif 'preview' in node_type_lower:
                return self._convert_preview_image
        
        return None
    
    def _get_replacement_suggestions(self, node_type: str) -> List[str]:
        """Get suggestions for unsupported nodes"""
        node_type_lower = node_type.lower()
        suggestions = []
        
        if 'video' in node_type_lower or 'animate' in node_type_lower:
            suggestions.extend([
                "# Video/Animation nodes are not supported in diffusers",
                "# Consider using: animatediff, stable-video-diffusion, or video generation models",
                "# Alternative: Generate multiple frames and combine with external tools",
            ])
        
        elif '3d' in node_type_lower or 'mesh' in node_type_lower or 'triplane' in node_type_lower:
            suggestions.extend([
                "# 3D generation requires specialized libraries",
                "# Consider using: threestudio, instant3d, or zero123 models",
                "# Alternative: Use 2D generation with depth estimation",
            ])
        
        elif 'controlnet' in node_type_lower:
            suggestions.extend([
                "# ControlNet variants can be replaced with standard ControlNet",
                "from diffusers import StableDiffusionControlNetPipeline, ControlNetModel",
                "# controlnet = ControlNetModel.from_pretrained('lllyasviel/sd-controlnet-canny')",
            ])
        
        elif 'lora' in node_type_lower:
            suggestions.extend([
                "# LoRA variants can be replaced with standard LoRA loading",
                "# pipe.load_lora_weights('path/to/lora')",
                "# pipe.fuse_lora(lora_scale=0.8)",
            ])
        
        elif 'upscale' in node_type_lower or 'super' in node_type_lower:
            suggestions.extend([
                "# Upscaling can be done with dedicated models",
                "# Consider using: Real-ESRGAN, ESRGAN, or SwinIR",
                "from PIL import Image",
                "# image = image.resize((width*2, height*2), Image.LANCZOS)",
            ])
        
        return suggestions
    
    def _convert_checkpoint_loader(self, node: Dict) -> List[str]:
        """Convert CheckpointLoaderSimple to pipeline loading"""
        widgets = node.get('widgets_values', [])
        model_name = widgets[0] if widgets else 'runwayml/stable-diffusion-v1-5'
        
        # Determine pipeline type based on model name
        if 'flux' in model_name.lower():
            pipe_type = 'FluxPipeline'
            repo_id = 'black-forest-labs/FLUX.1-schnell'
        elif 'sd3' in model_name.lower():
            pipe_type = 'StableDiffusion3Pipeline' 
            repo_id = 'stabilityai/stable-diffusion-3-medium-diffusers'
        elif 'cascade' in model_name.lower():
            pipe_type = 'StableCascadePriorPipeline'
            repo_id = 'stabilityai/stable-cascade'
        elif 'xl' in model_name.lower() or 'sdxl' in model_name.lower():
            pipe_type = 'StableDiffusionXLPipeline'
            repo_id = 'stabilityai/stable-diffusion-xl-base-1.0'
        else:
            pipe_type = 'StableDiffusionPipeline'
            repo_id = 'runwayml/stable-diffusion-v1-5'
        
        self.variables['pipe'] = 'pipe'
        
        return [
            f"# Load model checkpoint: {model_name}",
            f"from diffusers import {pipe_type}",
            f"pipe = {pipe_type}.from_pretrained(",
            f"    '{repo_id}',",
            f"    torch_dtype=dtype,",
            f"    safety_checker=None,",
            f"    requires_safety_checker=False",
            f").to(device)",
            f"print('Loaded {pipe_type} from {repo_id}')",
            "",
        ]
    
    def _convert_dual_clip_loader(self, node: Dict) -> List[str]:
        """Convert DualCLIPLoader for FLUX models"""
        widgets = node.get('widgets_values', [])
        
        return [
            f"# FLUX DualCLIP Loader",
            f"# Using integrated CLIP in FLUX pipeline",
            f"# T5 and CLIP-L models are loaded automatically",
            "",
        ]
    
    def _convert_vae_loader(self, node: Dict) -> List[str]:
        """Convert VAELoader"""
        widgets = node.get('widgets_values', [])
        vae_name = widgets[0] if widgets else 'default'
        
        return [
            f"# VAE Loader: {vae_name}",
            f"# VAE is integrated in the pipeline",
            "",
        ]
    
    def _convert_unet_loader(self, node: Dict) -> List[str]:
        """Convert UNETLoader"""
        widgets = node.get('widgets_values', [])
        unet_name = widgets[0] if widgets else 'default'
        weight_dtype = widgets[1] if len(widgets) > 1 else 'default'
        
        # For FLUX models, this is where we actually load the pipeline
        if 'flux' in unet_name.lower():
            self.variables['pipe'] = 'pipe'
            
            # Determine FLUX variant
            if 'dev' in unet_name.lower():
                model_id = 'black-forest-labs/FLUX.1-dev'
                steps = 28  # DEV uses more steps
                guidance = 3.5
            else:
                model_id = 'black-forest-labs/FLUX.1-schnell'
                steps = 4   # SCHNELL uses fewer steps
                guidance = 0.0
            
            return [
                f"# FLUX UNET Loader: {unet_name}",
                f"from diffusers import FluxPipeline",
                f"",
                f"# Load FLUX pipeline",
                f"pipe = FluxPipeline.from_pretrained(",
                f"    '{model_id}',",
                f"    torch_dtype=dtype,",
                f").to(device)",
                f"print('Loaded FLUX pipeline: {model_id}')",
                f"",
                f"# FLUX-specific parameters",
                f"num_inference_steps = {steps}",
                f"guidance_scale = {guidance}",
                "",
            ]
        else:
            return [
                f"# UNET Loader: {unet_name}",
                f"# UNET is integrated in the pipeline",
                "",
            ]
    
    def _convert_clip_text_encode(self, node: Dict) -> List[str]:
        """Convert CLIPTextEncode to prompt encoding"""
        widgets = node.get('widgets_values', [])
        text = widgets[0] if widgets else 'a beautiful landscape'
        
        # Determine if this is positive or negative prompt based on node connections or content
        node_id = str(node.get('id', ''))
        
        # Simple heuristic: if text contains negative words, treat as negative prompt
        negative_indicators = ['bad', 'poor', 'disfigured', 'missing', 'worst', 'ugly', 'blurry']
        is_negative = any(indicator in text.lower() for indicator in negative_indicators)
        
        if is_negative and not self.variables.get('negative_prompt'):
            self.variables['negative_prompt'] = text
            return [
                f"# Negative prompt encoding",
                f"negative_prompt = \"\"\"" + text + "\"\"\"",
                "",
            ]
        else:
            # If we already have a positive prompt, append or replace
            if not self.variables.get('prompt'):
                self.variables['prompt'] = text
                return [
                    f"# Text prompt encoding",
                    f"prompt = \"\"\"" + text + "\"\"\"",
                    "",
                ]
            else:
                # Combine with existing prompt
                return [
                    f"# Additional prompt text",
                    f"# Combining with existing prompt",
                    f"prompt = prompt + ' ' + \"\"\"" + text + "\"\"\"",
                    "",
                ]
    
    def _convert_clip_text_encode_flux(self, node: Dict) -> List[str]:
        """Convert CLIPTextEncodeFlux for FLUX models"""
        widgets = node.get('widgets_values', [])
        text = widgets[0] if widgets else 'a beautiful landscape'
        guidance = widgets[1] if len(widgets) > 1 else 3.5
        
        self.variables['prompt'] = text
        
        return [
            f"# FLUX text prompt encoding",
            f"prompt = \"\"\"" + text + "\"\"\"",
            f"guidance_scale = {guidance}",
            "",
        ]
        
        return [
            f"# FLUX text encoding",
            f"prompt = \"{text}\"",
            f"guidance_scale = {guidance}",
            "",
        ]
    
    def _convert_ksampler(self, node: Dict) -> List[str]:
        """Convert KSampler to diffusion generation"""
        widgets = node.get('widgets_values', [])
        
        # Extract parameters with proper parsing
        seed = widgets[0] if len(widgets) > 0 else 42
        steps_raw = widgets[1] if len(widgets) > 1 else 20
        cfg = widgets[2] if len(widgets) > 2 else 7.5
        sampler = widgets[3] if len(widgets) > 3 else 'euler'
        scheduler = widgets[4] if len(widgets) > 4 else 'normal'
        denoise = widgets[5] if len(widgets) > 5 else 1.0
        
        # Handle special cases for steps
        if steps_raw == "fixed":
            steps = 28  # Default for fixed steps
        else:
            try:
                steps = int(steps_raw)
            except:
                steps = 20
        
        self.variables['image'] = 'image'
        
        return [
            f"# K-Sampler configuration",
            f"torch.manual_seed({seed})",
            f"generator = torch.Generator(device=device).manual_seed({seed})",
            f"",
            f"# Generate image with sampler: {sampler}",
            f"if 'pipe' in locals():",
            f"    with torch.no_grad():",
            f"        result = pipe(",
            f"            prompt=prompt if 'prompt' in locals() else 'a beautiful landscape',",
            f"            negative_prompt=negative_prompt if 'negative_prompt' in locals() else None,",
            f"            num_inference_steps={steps},",
            f"            guidance_scale={cfg},",
            f"            generator=generator,",
            f"            width=width if 'width' in locals() else 512,",
            f"            height=height if 'height' in locals() else 512,",
            f"        )",
            f"        if hasattr(result, 'images'):",
            f"            image = result.images[0]",
            f"        else:",
            f"            image = result",
            f"        ",
            f"        # Save the generated image",
            f"        image.save('generated_image.png')",
            f"        print('✓ Image generated and saved as generated_image.png')",
            "",
        ]
    
    def _convert_ksampler_advanced(self, node: Dict) -> List[str]:
        """Convert KSamplerAdvanced"""
        return self._convert_ksampler(node)
    
    def _convert_sampler_custom_advanced(self, node: Dict) -> List[str]:
        """Convert SamplerCustomAdvanced"""
        widgets = node.get('widgets_values', [])
        
        return [
            f"# Advanced custom sampler",
            f"# Using default pipeline sampling",
            "",
        ]
    
    def _convert_basic_scheduler(self, node: Dict) -> List[str]:
        """Convert BasicScheduler"""
        widgets = node.get('widgets_values', [])
        scheduler_name = widgets[0] if widgets else 'ddim'
        steps = widgets[1] if len(widgets) > 1 else 20
        denoise = widgets[2] if len(widgets) > 2 else 1.0
        
        return [
            f"# Basic scheduler: {scheduler_name}",
            f"# Steps: {steps}, Denoise: {denoise}",
            f"num_inference_steps = {steps}",
            "",
        ]
    
    def _convert_basic_guider(self, node: Dict) -> List[str]:
        """Convert BasicGuider"""
        return [
            f"# Basic guider configuration",
            f"# Integrated in pipeline guidance",
            "",
        ]
    
    def _convert_vae_decode(self, node: Dict) -> List[str]:
        """Convert VAEDecode (usually handled by pipeline)"""
        return [
            "# VAE decode is handled automatically by the pipeline",
            "",
        ]
    
    def _convert_vae_encode(self, node: Dict) -> List[str]:
        """Convert VAEEncode"""
        return [
            "# VAE encode for image-to-image processing",
            "# This would require loading the input image first",
            "",
        ]
    
    def _convert_save_image(self, node: Dict) -> List[str]:
        """Convert SaveImage to PIL save"""
        widgets = node.get('widgets_values', [])
        filename = widgets[0] if widgets else 'generated_image'
        
        return [
            f"# Save generated image",
            f"if 'image' in locals() and image is not None:",
            f"    image.save('{filename}.png')",
            f"    print('Image saved as {filename}.png')",
            f"else:",
            f"    print('No image to save')",
            "",
        ]
    
    def _convert_preview_image(self, node: Dict) -> List[str]:
        """Convert PreviewImage"""
        return [
            f"# Preview image",
            f"if 'image' in locals() and image is not None:",
            f"    image.show()  # Display image",
            "",
        ]
    
    def _convert_empty_latent(self, node: Dict) -> List[str]:
        """Convert EmptyLatentImage to image dimensions"""
        widgets = node.get('widgets_values', [])
        width = widgets[0] if len(widgets) > 0 else 512
        height = widgets[1] if len(widgets) > 1 else 512
        batch_size = widgets[2] if len(widgets) > 2 else 1
        
        self.variables['width'] = width
        self.variables['height'] = height
        
        return [
            f"# Set image dimensions: {width}x{height}",
            f"width = {width}",
            f"height = {height}",
            f"batch_size = {batch_size}",
            "",
        ]
    
    def _convert_latent_upscale(self, node: Dict) -> List[str]:
        """Convert LatentUpscale"""
        widgets = node.get('widgets_values', [])
        upscale_method = widgets[0] if widgets else 'nearest-exact'
        width = widgets[1] if len(widgets) > 1 else 1024
        height = widgets[2] if len(widgets) > 2 else 1024
        
        return [
            f"# Latent upscaling to {width}x{height}",
            f"width = {width}",
            f"height = {height}",
            f"# Method: {upscale_method}",
            "",
        ]
    
    def _convert_lora_loader(self, node: Dict) -> List[str]:
        """Convert LoraLoader to LoRA loading"""
        widgets = node.get('widgets_values', [])
        lora_name = widgets[0] if widgets else ''
        strength_model = widgets[1] if len(widgets) > 1 else 1.0
        strength_clip = widgets[2] if len(widgets) > 2 else 1.0
        
        return [
            f"# Load LoRA adapter: {lora_name}",
            f"# pipe.load_lora_weights('{lora_name}')",
            f"# lora_scale = {strength_model}",
            f"# Note: LoRA loading requires proper adapter setup",
            "",
        ]
    
    def _convert_controlnet_loader(self, node: Dict) -> List[str]:
        """Convert ControlNetLoader"""
        widgets = node.get('widgets_values', [])
        controlnet_name = widgets[0] if widgets else 'canny'
        
        return [
            f"# ControlNet Loader: {controlnet_name}",
            f"from diffusers import ControlNetModel",
            f"# controlnet = ControlNetModel.from_pretrained('lllyasviel/sd-controlnet-{controlnet_name}')",
            "",
        ]
    
    def _convert_controlnet_apply(self, node: Dict) -> List[str]:
        """Convert ControlNetApply"""
        widgets = node.get('widgets_values', [])
        strength = widgets[0] if widgets else 1.0
        
        return [
            f"# Apply ControlNet with strength: {strength}",
            f"# This requires ControlNet pipeline setup",
            "",
        ]
    
    def _convert_portrait_master(self, node: Dict) -> List[str]:
        """Convert PortraitMaster_中文版"""
        widgets = node.get('widgets_values', [])
        
        return [
            f"# Portrait Master (Chinese version)",
            f"# This is a custom node for portrait generation",
            f"# Converting to standard prompting approach",
            f"prompt = \"portrait, professional photography, high quality\"",
            f"negative_prompt = \"blurry, low quality, distorted\"",
            "",
        ]
    
    def _convert_sketch_to_3d(self, node: Dict) -> List[str]:
        """Convert Sketch to 3D"""
        return [
            f"# Sketch to 3D conversion",
            f"# This requires specialized 3D generation models",
            f"# Consider using models like Zero123 or similar",
            f"print('3D generation requires specialized libraries')",
            "",
        ]
    
    def _convert_live_portrait(self, node: Dict) -> List[str]:
        """Convert LivePortrait"""
        return [
            f"# Live Portrait animation",
            f"# This requires specialized animation models",
            f"# Consider using models for portrait animation",
            f"print('Live portrait requires specialized libraries')",
            "",
        ]
    
    def _convert_workflow_flux(self, node: Dict) -> List[str]:
        """Convert workflow/FLUX node"""
        widgets = node.get('widgets_values', [])
        
        # Extract FLUX workflow parameters
        seed = widgets[0] if len(widgets) > 0 else 42
        seed_mode = widgets[1] if len(widgets) > 1 else 'randomize'
        sampler = widgets[2] if len(widgets) > 2 else 'euler'
        scheduler = widgets[3] if len(widgets) > 3 else 'simple'
        steps = widgets[4] if len(widgets) > 4 else 20
        denoise = widgets[5] if len(widgets) > 5 else 1.0
        
        self.variables['image'] = 'image'
        
        return [
            f"# FLUX workflow execution",
            f"torch.manual_seed({seed})",
            f"generator = torch.Generator(device=device).manual_seed({seed})",
            f"",
            f"# FLUX generation parameters",
            f"# Sampler: {sampler}, Scheduler: {scheduler}",
            f"# Steps: {steps}, Denoise: {denoise}",
            f"",
            f"# Generate image with FLUX",
            f"if 'pipe' in locals():",
            f"    with torch.no_grad():",
            f"        result = pipe(",
            f"            prompt=prompt if 'prompt' in locals() else 'a beautiful landscape',",
            f"            width=width if 'width' in locals() else 1024,",
            f"            height=height if 'height' in locals() else 1024,",
            f"            num_inference_steps=num_inference_steps if 'num_inference_steps' in locals() else {steps},",
            f"            guidance_scale=guidance_scale if 'guidance_scale' in locals() else 0.0,",
            f"            generator=generator,",
            f"        )",
            f"        if hasattr(result, 'images'):",
            f"            image = result.images[0]",
            f"        else:",
            f"            image = result",
            f"        print('FLUX generation completed')",
            "",
        ]
    
    def _convert_workflow_sd3(self, node: Dict) -> List[str]:
        """Convert workflow/SD3 node"""
        return [
            f"# SD3 workflow node - custom workflow",
            f"# This represents a Stable Diffusion 3 workflow configuration",
            "",
        ]
    
    def _convert_triple_clip_loader(self, node: Dict) -> List[str]:
        """Convert TripleCLIPLoader for SD3"""
        widgets = node.get('widgets_values', [])
        clip_g = widgets[0] if widgets else 'clip_g.safetensors'
        clip_l = widgets[1] if len(widgets) > 1 else 'clip_l.safetensors' 
        t5xxl = widgets[2] if len(widgets) > 2 else 't5xxl_fp16.safetensors'
        
        return [
            f"# TripleCLIPLoader for SD3: {clip_g}, {clip_l}, {t5xxl}",
            f"# CLIP models are integrated in the SD3 pipeline",
            "",
        ]
    
    def _convert_empty_sd3_latent(self, node: Dict) -> List[str]:
        """Convert EmptySD3LatentImage"""
        widgets = node.get('widgets_values', [])
        width = widgets[0] if widgets else 1024
        height = widgets[1] if len(widgets) > 1 else 1024
        batch_size = widgets[2] if len(widgets) > 2 else 1
        
        self.variables['width'] = width
        self.variables['height'] = height
        
        return [
            f"# SD3 latent image dimensions: {width}x{height}",
            f"width = {width}",
            f"height = {height}",
            f"batch_size = {batch_size}",
            "",
        ]
    
    def _convert_model_sampling_sd3(self, node: Dict) -> List[str]:
        """Convert ModelSamplingSD3"""
        return [
            f"# SD3 model sampling configuration",
            f"# Sampling parameters are handled by the pipeline",
            "",
        ]
    
    def _convert_conditioning_timestep(self, node: Dict) -> List[str]:
        """Convert ConditioningSetTimestepRange"""
        widgets = node.get('widgets_values', [])
        start = widgets[0] if widgets else 0.0
        end = widgets[1] if len(widgets) > 1 else 1.0
        
        return [
            f"# Conditioning timestep range: {start} to {end}",
            f"# Timestep conditioning is handled by pipeline",
            "",
        ]
    
    def _convert_conditioning_zero_out(self, node: Dict) -> List[str]:
        """Convert ConditioningZeroOut"""
        return [
            f"# Conditioning zero out",
            f"# Use empty negative prompt for zero conditioning",
            f"negative_prompt = ''",
            "",
        ]
    
    def _convert_conditioning_combine(self, node: Dict) -> List[str]:
        """Convert ConditioningCombine"""
        return [
            f"# Conditioning combine",
            f"# Multiple conditions are combined in the prompt",
            "",
        ]
    
    def _convert_primitive_node(self, node: Dict) -> List[str]:
        """Convert PrimitiveNode (constant values)"""
        widgets = node.get('widgets_values', [])
        if widgets:
            value = widgets[0]
            return [
                f"# Primitive value: {value}",
                f"primitive_value = {repr(value)}",
                "",
            ]
        return [
            f"# Primitive node (empty)",
            "",
        ]

    def _convert_random_noise(self, node: Dict) -> List[str]:
        """Convert RandomNoise node"""
        widgets = node.get('widgets_values', [])
        seed = widgets[0] if widgets else 42
        
        return [
            f"# Random noise configuration",
            f"torch.manual_seed({seed})",
            f"generator = torch.Generator(device=device).manual_seed({seed})",
            "",
        ]
    
    def _convert_sampler_custom(self, node: Dict) -> List[str]:
        """Convert SamplerCustom node"""
        widgets = node.get('widgets_values', [])
        sampler_name = widgets[0] if widgets else 'euler'
        
        return [
            f"# Custom sampler: {sampler_name}",
            f"sampler_name = '{sampler_name}'",
            "",
        ]

    def _convert_flux_guidance(self, node: Dict) -> List[str]:
        """Convert FluxGuidance node"""
        widgets = node.get('widgets_values', [])
        guidance = widgets[0] if widgets else 3.5
        
        return [
            f"# FLUX guidance configuration",
            f"guidance_scale = {guidance}",
            "",
        ]

    def _convert_ksampler_select(self, node: Dict) -> List[str]:
        """Convert KSamplerSelect node to Python code"""
        widgets = node.get('widgets_values', [])
        
        # Extract sampler settings
        sampler_name = widgets[0] if widgets else 'euler'
        
        return [
            f"# KSamplerSelect: Using {sampler_name} sampler",
            f"sampler_name = '{sampler_name}'",
            f"# Sampler will be used in the generation step",
            "",
        ]
    
    # === Video/Animation Node Replacements ===
    
    def _replace_video_combine(self, node: Dict) -> List[str]:
        """Replace VHS_VideoCombine with static image generation"""
        widgets = node.get('widgets_values', [])
        
        # Handle both list and dict formats
        if isinstance(widgets, list):
            fps = widgets[0] if widgets and len(widgets) > 0 else 24
        elif isinstance(widgets, dict):
            fps = widgets.get(0, 24)
        else:
            fps = 24
        
        return [
            f"# Video combine replaced with static image generation",
            f"# Original FPS: {fps}",
            f"# For video generation, consider using:",
            f"# - stable-video-diffusion pipeline",
            f"# - animatediff models",
            f"# - external tools like FFmpeg for frame combination",
            f"",
            f"# Current: Generate single high-quality frame",
            f"print('Video generation not supported - generating single frame instead')",
            "",
        ]
    
    def _replace_video_load(self, node: Dict) -> List[str]:
        """Replace VHS_LoadVideo with image loading"""
        return [
            f"# Video loading replaced with image loading",
            f"# For video input, extract frames first:",
            f"# import cv2",
            f"# cap = cv2.VideoCapture('video.mp4')",
            f"# ret, frame = cap.read()",
            f"# image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))",
            f"",
            f"# Current: Load single image instead",
            f"# image = Image.open('input_image.jpg')",
            "",
        ]
    
    def _replace_live_portrait(self, node: Dict) -> List[str]:
        """Replace LivePortrait with standard portrait generation"""
        return [
            f"# LivePortrait replaced with enhanced portrait prompts",
            f"# For portrait animation, consider:",
            f"# - DreamTalk, SadTalker, or Wav2Lip models",
            f"# - FaceSwapper or similar face animation tools",
            f"",
            f"# Enhanced portrait generation",
            f"if 'prompt' in locals():",
            f"    prompt = f'portrait photography, {{prompt}}, professional lighting, detailed face'",
            f"else:",
            f"    prompt = 'professional portrait photography, detailed facial features, studio lighting'",
            "",
        ]
    
    def _replace_live_portrait_composite(self, node: Dict) -> List[str]:
        """Replace LivePortraitComposite with image composition"""
        return [
            f"# LivePortrait composite replaced with standard image composition",
            f"# For advanced face compositing, use:",
            f"# from PIL import Image, ImageDraw",
            f"# import cv2  # for advanced blending",
            f"",
            f"# Basic composition example:",
            f"# if 'base_image' in locals() and 'overlay_image' in locals():",
            f"#     base_image.paste(overlay_image, (x, y), overlay_image)",
            "",
        ]
    
    def _replace_face_alignment(self, node: Dict) -> List[str]:
        """Replace face alignment with basic face detection suggestions"""
        return [
            f"# Face alignment replaced with basic preprocessing",
            f"# For face alignment, consider using:",
            f"# - MediaPipe Face Detection",
            f"# - OpenCV face detection",
            f"# - insightface library",
            f"",
            f"# Basic face-focused generation",
            f"if 'prompt' in locals():",
            f"    prompt = f'{{prompt}}, centered face, front view, clear facial features'",
            "",
        ]
    
    def _replace_model_download(self, node: Dict) -> List[str]:
        """Replace model downloading with standard model loading"""
        return [
            f"# Model download replaced with standard diffusers model loading",
            f"# Models are automatically downloaded when needed",
            f"# Ensure you have proper internet connection for first-time use",
            "",
        ]
    
    # === 3D Generation Node Replacements ===
    
    def _replace_3d_generation(self, node: Dict) -> List[str]:
        """Replace 3D generation with 2D alternatives"""
        return [
            f"# 3D generation replaced with enhanced 2D generation",
            f"# For 3D effects, consider using:",
            f"# - depth estimation models",
            f"# - normal map generation",
            f"# - multi-view consistent generation",
            f"",
            f"# Enhanced prompts for 3D-like appearance",
            f"if 'prompt' in locals():",
            f"    prompt = f'{{prompt}}, 3D rendered, volumetric lighting, depth of field'",
            f"else:",
            f"    prompt = '3D rendered object, volumetric lighting, professional 3D visualization'",
            "",
        ]
    
    def _replace_instant_mesh(self, node: Dict) -> List[str]:
        """Replace InstantMesh with multi-view generation"""
        return [
            f"# InstantMesh replaced with multi-view 2D generation",
            f"# For mesh generation, consider external tools:",
            f"# - Blender with AI plugins",
            f"# - Instant3D models",
            f"# - Point-E or Shap-E models",
            f"",
            f"# Generate multiple views",
            f"views = ['front view', 'side view', 'back view', 'top view']",
            f"# Generate each view separately with modified prompts",
            "",
        ]
    
    def _replace_triposr(self, node: Dict) -> List[str]:
        """Replace TripoSR with depth-aware generation"""
        return [
            f"# TripoSR replaced with depth-aware 2D generation",
            f"# For 3D reconstruction, consider:",
            f"# - MVDream models",
            f"# - Wonder3D pipeline",
            f"# - External photogrammetry tools",
            f"",
            f"# Depth-enhanced generation",
            f"if 'prompt' in locals():",
            f"    prompt = f'{{prompt}}, depth perception, 3D structure, detailed geometry'",
            "",
        ]
    
    # === Advanced Sampling Node Replacements ===
    
    def _replace_random_noise(self, node: Dict) -> List[str]:
        """Replace RandomNoise with standard torch noise generation"""
        widgets = node.get('widgets_values', [])
        seed = widgets[0] if widgets else 42
        
        return [
            f"# Random noise generation",
            f"torch.manual_seed({seed})",
            f"generator = torch.Generator(device=device).manual_seed({seed})",
            f"# Noise is handled automatically by diffusers pipeline",
            "",
        ]
    
    def _replace_ksampler_select(self, node: Dict) -> List[str]:
        """Replace KSamplerSelect with scheduler configuration"""
        widgets = node.get('widgets_values', [])
        sampler_name = widgets[0] if widgets else 'euler'
        
        return [
            f"# Sampler selection: {sampler_name}",
            f"# Configure scheduler (handled by pipeline)",
            f"# Available schedulers: DDIM, DPM++, Euler, etc.",
            f"sampler_name = '{sampler_name}'",
            "",
        ]
    
    def _replace_custom_sampler(self, node: Dict) -> List[str]:
        """Replace custom sampler with standard pipeline sampling"""
        return [
            f"# Custom sampler replaced with pipeline default",
            f"# Advanced sampling parameters are approximated",
            f"# For custom sampling, modify pipeline scheduler directly",
            "",
        ]
    
    # === Image Processing Node Replacements ===
    
    def _replace_image_scale(self, node: Dict) -> List[str]:
        """Replace ImageScale with PIL resize"""
        widgets = node.get('widgets_values', [])
        scale_method = widgets[0] if widgets else 'lanczos'
        width = widgets[1] if len(widgets) > 1 else None
        height = widgets[2] if len(widgets) > 2 else None
        
        return [
            f"# Image scaling with PIL",
            f"from PIL import Image",
            f"if 'image' in locals():",
            f"    # Scale method: {scale_method}",
            f"    if {width} and {height}:",
            f"        image = image.resize(({width}, {height}), Image.LANCZOS)",
            f"    print(f'Image scaled to: {{image.size}}')",
            "",
        ]
    
    def _replace_image_resize(self, node: Dict) -> List[str]:
        """Replace ImageResize with PIL resize"""
        return self._replace_image_scale(node)
    
    def _replace_image_crop(self, node: Dict) -> List[str]:
        """Replace ImageCrop with PIL crop"""
        widgets = node.get('widgets_values', [])
        x = widgets[0] if len(widgets) > 0 else 0
        y = widgets[1] if len(widgets) > 1 else 0
        width = widgets[2] if len(widgets) > 2 else 512
        height = widgets[3] if len(widgets) > 3 else 512
        
        return [
            f"# Image cropping with PIL",
            f"if 'image' in locals():",
            f"    image = image.crop(({x}, {y}, {x + width}, {y + height}))",
            f"    print(f'Image cropped to: {{image.size}}')",
            "",
        ]
    
    def _replace_image_rotate(self, node: Dict) -> List[str]:
        """Replace ImageRotate with PIL rotate"""
        widgets = node.get('widgets_values', [])
        angle = widgets[0] if widgets else 0
        
        return [
            f"# Image rotation with PIL",
            f"if 'image' in locals():",
            f"    image = image.rotate({angle}, expand=True)",
            f"    print(f'Image rotated by {angle} degrees')",
            "",
        ]
    
    # === Text Processing Node Replacements ===
    
    def _replace_sdxl_text_encode(self, node: Dict) -> List[str]:
        """Replace SDXL text encoding with standard encoding"""
        widgets = node.get('widgets_values', [])
        text = widgets[0] if widgets else 'a beautiful image'
        
        return [
            f"# SDXL text encoding (simplified)",
            f"prompt = \"{text.replace('\"', '\\\"')}\"",
            f"# SDXL uses dual text encoders (handled by pipeline)",
            "",
        ]
    
    def _replace_sd3_text_encode(self, node: Dict) -> List[str]:
        """Replace SD3 text encoding with standard encoding"""
        widgets = node.get('widgets_values', [])
        text = widgets[0] if widgets else 'a beautiful image'
        
        return [
            f"# SD3 text encoding (simplified)",
            f"prompt = \"{text.replace('\"', '\\\"')}\"",
            f"# SD3 uses T5 and CLIP encoders (handled by pipeline)",
            "",
        ]
    
    # === Custom Workflow Node Replacements ===
    
    def _replace_custom_workflow(self, node: Dict) -> List[str]:
        """Replace custom workflow nodes with standard generation"""
        node_type = node.get('type', 'unknown')
        return [
            f"# Custom workflow node: {node_type}",
            f"# Replaced with standard generation pipeline",
            f"# Custom workflows may require manual adaptation",
            "",
        ]
    
    def _replace_sdxl_workflow(self, node: Dict) -> List[str]:
        """Replace SDXL workflow with SDXL pipeline"""
        return [
            f"# SDXL workflow replaced with SDXL pipeline",
            f"# Ensure SDXL pipeline is loaded above",
            f"# SDXL-specific parameters are handled automatically",
            "",
        ]
    
    # === ControlNet Node Replacements ===
    
    def _replace_controlnet_advanced(self, node: Dict) -> List[str]:
        """Replace advanced ControlNet with standard ControlNet"""
        widgets = node.get('widgets_values', [])
        strength = widgets[0] if widgets else 1.0
        
        return [
            f"# Advanced ControlNet replaced with standard ControlNet",
            f"from diffusers import StableDiffusionControlNetPipeline, ControlNetModel",
            f"# controlnet = ControlNetModel.from_pretrained('controlnet_model')",
            f"# controlnet_strength = {strength}",
            f"# Use StableDiffusionControlNetPipeline for ControlNet features",
            "",
        ]
    
    def _replace_multi_controlnet(self, node: Dict) -> List[str]:
        """Replace MultiControlNet with single ControlNet"""
        return [
            f"# Multi-ControlNet replaced with single ControlNet",
            f"# For multiple ControlNets, use MultiControlNetModel",
            f"# from diffusers import MultiControlNetModel",
            f"# controlnet = MultiControlNetModel([controlnet1, controlnet2])",
            "",
        ]
    
    def _convert_ksampler_select(self, node: Dict) -> List[str]:
        """Convert KSamplerSelect node to Python code"""
        widgets = node.get('widgets_values', [])
        
        # Extract sampler settings
        sampler_name = widgets[0] if widgets else 'euler'
        
        return [
            f"# KSamplerSelect: Using {sampler_name} sampler",
            f"sampler_name = '{sampler_name}'",
            f"# Sampler will be used in the generation step",
            "",
        ]
    
    # === LoRA Node Replacements ===
    
    def _replace_lora_model_only(self, node: Dict) -> List[str]:
        """Replace LoRA model-only with standard LoRA"""
        widgets = node.get('widgets_values', [])
        lora_name = widgets[0] if widgets else 'lora'
        strength = widgets[1] if len(widgets) > 1 else 1.0
        
        return [
            f"# LoRA model-only replaced with standard LoRA loading",
            f"# pipe.load_lora_weights('{lora_name}')",
            f"# lora_scale = {strength}",
            f"# Apply LoRA only to UNet (model), not CLIP",
            "",
        ]
    
    def _replace_lora_tagged(self, node: Dict) -> List[str]:
        """Replace tagged LoRA with standard LoRA"""
        return [
            f"# Tagged LoRA replaced with standard LoRA loading",
            f"# Tags are handled through prompt engineering",
            f"# Use descriptive prompts instead of LoRA tags",
            "",
        ]
    

def main():
    parser = argparse.ArgumentParser(description='Convert ComfyUI workflow to Python script')
    parser.add_argument('-i', '--input', help='Input ComfyUI workflow JSON file or directory')
    parser.add_argument('-o', '--output', help='Output directory for Python scripts', 
                       default='converted_scripts')
    parser.add_argument('--all', action='store_true', 
                       help='Convert all workflows in the workflows/zho directory')
    
    args = parser.parse_args()
    
    converter = ComfyUIToScript()
    success_count = 0
    total_count = 0
    
    if args.all:
        # Convert all workflows in the workflows/zho directory
        workflow_dir = 'workflows/zho'
        if os.path.exists(workflow_dir):
            os.makedirs(args.output, exist_ok=True)
            
            json_files = [f for f in os.listdir(workflow_dir) if f.endswith('.json')]
            total_count = len(json_files)
            print(f"Found {total_count} workflow files to convert...")
            
            for filename in json_files:
                input_path = os.path.join(workflow_dir, filename)
                output_filename = filename.replace('.json', '.py')
                output_path = os.path.join(args.output, output_filename)
                
                if converter.convert_workflow(input_path, output_path):
                    success_count += 1
        else:
            print(f"Directory {workflow_dir} not found")
            
    elif args.input:
        if os.path.isdir(args.input):
            # Convert all JSON files in the specified directory
            os.makedirs(args.output, exist_ok=True)
            
            json_files = [f for f in os.listdir(args.input) if f.endswith('.json')]
            total_count = len(json_files)
            print(f"Found {total_count} workflow files to convert...")
            
            for filename in json_files:
                input_path = os.path.join(args.input, filename)
                output_filename = filename.replace('.json', '.py')
                output_path = os.path.join(args.output, output_filename)
                
                if converter.convert_workflow(input_path, output_path):
                    success_count += 1
        else:
            # Convert single file
            total_count = 1
            if not args.output.endswith('.py'):
                args.output = args.output + '.py'
            if converter.convert_workflow(args.input, args.output):
                success_count += 1
    else:
        print("Please specify input file/directory with -i or use --all flag")
        print("Examples:")
        print("  python convert.py --all")
        print("  python convert.py -i workflows/zho")
        print("  python convert.py -i 'workflows/zho/FLUX.1 SCHNELL 1.0.json' -o flux_script.py")
        return
    
    # Print summary
    if total_count > 0:
        print(f"\nConversion completed!")
        print(f"Successfully converted: {success_count}/{total_count} workflows")
        if success_count < total_count:
            print(f"Failed: {total_count - success_count} workflows")
        
        print(f"\nGenerated scripts are ready to run!")
        print(f"Install dependencies with: pip install -r requirements.txt")
        if args.all or os.path.isdir(args.input):
            print(f"Scripts saved in: {args.output}/")
        else:
            print(f"Script saved as: {args.output}")
    else:
        print("No workflow files found to convert.")

if __name__ == "__main__":
    main()