import os
import json
import re
import requests
import time
from urllib.parse import urlparse

def check_workflow_for_closed_source_models(workflow_path):
    """Check if a ComfyUI workflow uses closed-source models"""
    
    # Known open-source model indicators
    open_source_indicators = [
        'stable-diffusion',
        'sd-',
        'sdxl',
        'flux',
        'controlnet',
        'lora',
        'dreambooth',
        'textual-inversion',
        'embedding',
        'clip',
        'vae',
        'unet',
        'diffusers',
        'huggingface',
        'civitai',
        'runwayml',
        'stabilityai',
        'llava',
        'blip',
        'automatic1111',
        'comfyui',
        'animatediff',
        'ipadapter',
        'instantid',
        'photomaker',
        'facedetailer'
    ]
    
    # Known closed-source model indicators
    closed_source_indicators = [
        'openai',
        'gpt-',
        'claude',
        'anthropic',
        'midjourney',
        'dall-e',
        'dalle',
        'firefly',
        'adobe',
        'gemini',
        'bard',
        'copilot',
        'commercial',
        'proprietary'
    ]
    
    def check_huggingface_model(model_name):
        """Check if a model exists on HuggingFace and is public"""
        try:
            model_name = model_name.strip().replace(' ', '')
            if not model_name:
                return None
                
            api_url = f"https://huggingface.co/api/models/{model_name}"
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                model_info = response.json()
                if model_info.get('private', False):
                    return False  # Private model
                return True  # Public model
            elif response.status_code == 404:
                return None  # Model not found
            else:
                return None  # API error
        except Exception:
            return None
    
    def check_civitai_model(model_id):
        """Check if a model exists on Civitai (public models)"""
        try:
            api_url = f"https://civitai.com/api/v1/models/{model_id}"
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                model_info = response.json()
                # Civitai models are generally public/open-source
                return True
            elif response.status_code == 404:
                return None  # Model not found
            else:
                return None  # API error
        except Exception:
            return None
    
    def check_replicate_model(model_name):
        """Check if a model exists on Replicate"""
        try:
            # Replicate API requires authentication for detailed info
            # So we'll just check if the URL pattern exists
            if '/' in model_name:
                return True  # Assume public if properly formatted
            return None
        except Exception:
            return None
    
    def check_github_model(repo_path):
        """Check if a GitHub repository exists and is public"""
        try:
            api_url = f"https://api.github.com/repos/{repo_path}"
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                repo_info = response.json()
                if repo_info.get('private', False):
                    return False  # Private repo
                return True  # Public repo
            elif response.status_code == 404:
                return None  # Repo not found
            else:
                return None  # API error
        except Exception:
            return None
    
    def extract_model_names(content):
        """Extract potential model names from content"""
        model_names = {'huggingface': set(), 'civitai': set(), 'replicate': set(), 'github': set()}
        
        # HuggingFace patterns
        hf_patterns = [
            r'huggingface\.co/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)',
            r'hf\.co/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)',
            r'"model":\s*"([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)"',
            r'"model_name":\s*"([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)"'
        ]
        
        # Civitai patterns
        civitai_patterns = [
            r'civitai\.com/models/(\d+)',
            r'civitai\.com/api/download/models/(\d+)'
        ]
        
        # Replicate patterns
        replicate_patterns = [
            r'replicate\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)',
            r'r8\.im/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)'
        ]
        
        # GitHub patterns
        github_patterns = [
            r'github\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)',
            r'raw\.githubusercontent\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)'
        ]
        
        # Extract HuggingFace models
        for pattern in hf_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            model_names['huggingface'].update(matches)
        
        # Extract Civitai models
        for pattern in civitai_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            model_names['civitai'].update(matches)
        
        # Extract Replicate models
        for pattern in replicate_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            model_names['replicate'].update(matches)
        
        # Extract GitHub repos
        for pattern in github_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            model_names['github'].update(matches)
            
        return model_names
    
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            content = f.read()
            content_lower = content.lower()
            
        # First check for explicitly closed-source models
        for indicator in closed_source_indicators:
            if indicator in content_lower:
                return True, f"closed-source: {indicator}"
        
        # Extract and check model names from various platforms
        model_names = extract_model_names(content)
        public_models_found = False
        private_models_found = False
        
        # Check HuggingFace models
        for model_name in model_names['huggingface']:
            time.sleep(0.1)  # Rate limiting
            hf_status = check_huggingface_model(model_name)
            
            if hf_status is True:
                public_models_found = True
            elif hf_status is False:
                private_models_found = True
                return True, f"closed-source: private HuggingFace model ({model_name})"
        
        # Check Civitai models (generally open-source)
        for model_id in model_names['civitai']:
            time.sleep(0.1)  # Rate limiting
            civitai_status = check_civitai_model(model_id)
            if civitai_status is True:
                public_models_found = True
        
        # Check Replicate models
        for model_name in model_names['replicate']:
            replicate_status = check_replicate_model(model_name)
            if replicate_status is True:
                public_models_found = True
        
        # Check GitHub repos
        for repo_path in model_names['github']:
            time.sleep(0.1)  # Rate limiting
            github_status = check_github_model(repo_path)
            
            if github_status is True:
                public_models_found = True
            elif github_status is False:
                return True, f"closed-source: private GitHub repo ({repo_path})"
        
        # Check for open-source model indicators
        has_open_source = False
        for indicator in open_source_indicators:
            if indicator in content_lower:
                has_open_source = True
                break
                
        # Parse JSON if it's a workflow file
        if workflow_path.endswith('.json'):
            try:
                workflow_data = json.loads(content)
                # Check nodes for model references
                if isinstance(workflow_data, dict) and 'nodes' in workflow_data:
                    for node in workflow_data['nodes']:
                        if 'inputs' in node:
                            inputs_str = str(node['inputs']).lower()
                            
                            # Check for closed-source in inputs
                            for indicator in closed_source_indicators:
                                if indicator in inputs_str:
                                    return True, f"closed-source: {indicator}"
                            
                            # Check for open-source in inputs
                            for indicator in open_source_indicators:
                                if indicator in inputs_str:
                                    has_open_source = True
                                    
            except json.JSONDecodeError:
                pass
        
        # If we found public models or open-source indicators
        if public_models_found or has_open_source:
            return False, None
            
        # If no clear indicators found, check for generic model patterns
        model_patterns = [
            r'model[_-]?name',
            r'checkpoint',
            r'\.ckpt',
            r'\.safetensors',
            r'api[_-]?key',
            r'endpoint',
            r'service[_-]?url'
        ]
        
        for pattern in model_patterns:
            if re.search(pattern, content_lower):
                return True, "unknown model (potentially closed-source)"
                
    except Exception as e:
        print(f"Error reading {workflow_path}: {e}")
        
    return False, None


def main():
    """Main function to filter workflows"""
    
    workflow_dir = 'workflows'  # Directory containing ComfyUI workflows
    closed_source_workflows = []
    
    for filename in os.listdir(workflow_dir):
        if filename.endswith('.json'):
            workflow_path = os.path.join(workflow_dir, filename)
            is_closed_source, reason = check_workflow_for_closed_source_models(workflow_path)
            
            if is_closed_source:
                closed_source_workflows.append((filename, reason))
    
    # Output results
    if closed_source_workflows:
        print("Closed-source workflows found:")
        for wf, reason in closed_source_workflows:
            print(f"{wf}: {reason}")
    else:
        print("No closed-source workflows found.")

if __name__ == "__main__":
    main()