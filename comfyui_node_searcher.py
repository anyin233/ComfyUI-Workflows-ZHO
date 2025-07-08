#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI Workflow Custom Node Searcher
Automatically searches for missing custom nodes in workflows and provides download links
"""

import json
import re
import requests
from pathlib import Path
import argparse
from typing import Set, Dict, List, Optional
from dataclasses import dataclass
import time
import sys
import os
import importlib.util

@dataclass
class NodeInfo:
    """Node information"""
    name: str
    source_url: str = ""
    github_url: str = ""
    description: str = ""
    install_command: str = ""

class ComfyUINodeSearcher:
    """ComfyUI Node Searcher"""
    
    def __init__(self, comfyui_path: Optional[str] = None):
        # Auto-detect ComfyUI path
        if comfyui_path is None:
            script_dir = Path(__file__).parent
            comfyui_path = script_dir / "ComfyUI"
        
        self.comfyui_path = Path(comfyui_path)
        self.builtin_nodes = self._load_builtin_nodes()
        
        # Load known node information from local database
        self.known_repos = self._load_local_node_database()
        
        # ComfyUI Manager node database API
        self.manager_api_url = "https://raw.githubusercontent.com/ltdrdata/ComfyUI-Manager/main/custom-node-list.json"
        self.node_db = None
    
    def _load_builtin_nodes(self) -> Set[str]:
        """Load built-in node list from ComfyUI submodule"""
        builtin_nodes = set()
        
        # Default node list as fallback
        default_nodes = {
            "LoadImage", "SaveImage", "PreviewImage", 
            "CLIPTextEncode", "CLIPSetLastLayer",
            "CheckpointLoaderSimple", "CheckpointLoader",
            "KSampler", "KSamplerAdvanced", "SamplerCustomAdvanced",
            "VAEDecode", "VAEEncode", "VAELoader", "VAEDecodeTiled", "VAEEncodeTiled",
            "EmptyLatentImage", "LatentUpscale", "LatentUpscaleBy",
            "LatentFromBatch", "RepeatLatentBatch", "LatentComposite", "LatentBlend",
            "LatentRotate", "LatentFlip", "LatentCrop", "SetLatentNoiseMask",
            "ControlNetLoader", "ControlNetApply", "ControlNetApplyAdvanced",
            "DiffControlNetLoader",
            "LoraLoader", "LoraLoaderModelOnly", "CLIPLoader", "UNETLoader", "DualCLIPLoader",
            "StyleModelLoader", "StyleModelApply", "CLIPVisionLoader", "CLIPVisionEncode",
            "GLIGENLoader", "GLIGENTextBoxApply",
            "ImageScale", "ImageScaleBy", "ImageInvert", "ImageBatch", "ImagePadForOutpaint",
            "EmptyImage", "LoadImageMask", "LoadImageOutput",
            "ConditioningAverage", "ConditioningCombine", "ConditioningConcat",
            "ConditioningSetArea", "ConditioningSetAreaPercentage", "ConditioningSetAreaStrength",
            "ConditioningSetMask", "ConditioningZeroOut", "ConditioningSetTimestepRange",
            "unCLIPConditioning", "unCLIPCheckpointLoader",
            "InpaintModelConditioning", "VAEEncodeForInpaint",
            "DiffusersLoader", "LoadLatent", "SaveLatent",
            # ComfyUI new version sampler-related nodes
            "BasicScheduler", "KarrasScheduler", "ExponentialScheduler",
            "KSamplerSelect", "DualCFGGuider", "CFGGuider",
            "RandomNoise", "SamplerCustomAdvanced",
            "UpscaleModelLoader", "ImageUpscaleWithModel",
            "InstructPixToPixConditioning",
            "PrimitiveNode", "Reroute", "Note"
        }
        
        try:
            # Try to extract NODE_CLASS_MAPPINGS from ComfyUI/nodes.py
            nodes_file = self.comfyui_path / "nodes.py"
            if nodes_file.exists():
                print(f"📖 Loading built-in nodes from ComfyUI submodule: {nodes_file}")
                
                # Read file content
                with open(nodes_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Use regex to extract keys from NODE_CLASS_MAPPINGS
                pattern = r'NODE_CLASS_MAPPINGS\s*=\s*\{([^}]+)\}'
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    mappings_content = match.group(1)
                    # Extract node names from each line
                    node_pattern = r'"([^"]+)"\s*:'
                    nodes = re.findall(node_pattern, mappings_content)
                    builtin_nodes.update(nodes)
                    print(f"✅ Extracted {len(nodes)} built-in nodes from NODE_CLASS_MAPPINGS")
                else:
                    print("⚠️ NODE_CLASS_MAPPINGS not found, using default node list")
                    builtin_nodes = default_nodes
            else:
                print(f"⚠️ ComfyUI nodes.py file does not exist: {nodes_file}")
                print("Using default built-in node list")
                builtin_nodes = default_nodes
                
        except Exception as e:
            print(f"⚠️ Failed to load ComfyUI built-in nodes: {e}")
            print("Using default built-in node list")
            builtin_nodes = default_nodes
        
        # Check for additional nodes in comfy_extras directory
        try:
            extras_dir = self.comfyui_path / "comfy_extras"
            if extras_dir.exists():
                for py_file in extras_dir.glob("*.py"):
                    if py_file.name.startswith("nodes_"):
                        # Derive node type from filename (simplified method)
                        node_type = py_file.stem.replace("nodes_", "")
                        # These are usually API nodes, we can mark them as built-in nodes
                        print(f"📝 Found additional node file: {py_file.name}")
        except Exception as e:
            print(f"⚠️ Failed to check comfy_extras: {e}")
        
        return builtin_nodes
    
    def _load_local_node_database(self) -> Dict:
        """Load local node database"""
        try:
            script_dir = Path(__file__).parent
            db_file = script_dir / "node_database.json"
            
            if db_file.exists():
                with open(db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ Loaded local node database: {len(data.get('known_custom_nodes', {}))} known node packages")
                return data.get('known_custom_nodes', {})
            else:
                print("⚠️ Local node database does not exist, using default configuration")
                return self._get_default_repos()
        except Exception as e:
            print(f"⚠️ Failed to load local node database: {e}")
            return self._get_default_repos()
    
    def _get_default_repos(self) -> Dict:
        """Get default repository configuration"""
        return {
            "rgthree-comfy": {
                "title": "rgthree's ComfyUI Nodes",
                "github_url": "https://github.com/rgthree/rgthree-comfy",
                "install_url": "https://github.com/rgthree/rgthree-comfy.git",
                "description": "Contains various utility nodes",
                "nodes": ["Any Switch (rgthree)", "Fast Bypasser (rgthree)"]
            },
            "ComfyUI-ZHO": {
                "title": "ComfyUI ZHO Node Package",
                "github_url": "https://github.com/AIGODLIKE/ComfyUI-ZHO",
                "install_url": "https://github.com/AIGODLIKE/ComfyUI-ZHO.git",
                "description": "ZHO series nodes, including artist, style, movement and other image library nodes",
                "nodes": ["ConcatText_Zho", "ArtistsImage_Zho", "MovementsImage_Zho", "StylesImage_Zho"]
            }
        }
    
    def load_workflow(self, workflow_path: str) -> Dict:
        """Load workflow file"""
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load workflow file: {e}")
            return {}
    
    def extract_node_types(self, workflow: Dict) -> Set[str]:
        """Extract all node types from workflow"""
        node_types = set()
        
        if 'nodes' in workflow:
            for node in workflow['nodes']:
                if 'type' in node:
                    node_types.add(node['type'])
        
        # Check nodes in extra.groupNodes
        if 'extra' in workflow and 'groupNodes' in workflow['extra']:
            for group_name, group_data in workflow['extra']['groupNodes'].items():
                if 'nodes' in group_data:
                    for node in group_data['nodes']:
                        if 'type' in node:
                            node_types.add(node['type'])
        
        return node_types
    
    def identify_custom_nodes(self, node_types: Set[str]) -> Set[str]:
        """Identify custom nodes (non-built-in nodes)"""
        return node_types - self.builtin_nodes
    
    def load_comfyui_manager_db(self) -> bool:
        """Load ComfyUI Manager's node database"""
        try:
            print("📥 Loading ComfyUI Manager node database...")
            response = requests.get(self.manager_api_url, timeout=30)
            response.raise_for_status()
            self.node_db = response.json()
            print(f"✅ Successfully loaded {len(self.node_db['custom_nodes'])} custom node package information")
            return True
        except Exception as e:
            print(f"⚠️ Unable to load ComfyUI Manager database: {e}")
            return False
    
    def search_node_in_db(self, node_name: str) -> List[NodeInfo]:
        """Search for nodes in database"""
        results = []
        
        if not self.node_db:
            return results
        
        for custom_node in self.node_db.get('custom_nodes', []):
            # Check node file list
            files = custom_node.get('files', [])
            for file_path in files:
                # Simple node name matching
                if node_name.lower() in file_path.lower():
                    node_info = NodeInfo(
                        name=node_name,
                        source_url=custom_node.get('reference', ''),
                        github_url=custom_node.get('files', [''])[0] if custom_node.get('files') else '',
                        description=custom_node.get('description', ''),
                        install_command=f"ComfyUI Manager installation: {custom_node.get('title', 'Unknown')}"
                    )
                    results.append(node_info)
                    break
            
            # Check title and description
            title = custom_node.get('title', '').lower()
            description = custom_node.get('description', '').lower()
            if (node_name.lower() in title or 
                node_name.lower() in description or
                any(keyword in node_name.lower() for keyword in title.split())):
                
                node_info = NodeInfo(
                    name=node_name,
                    source_url=custom_node.get('reference', ''),
                    github_url=custom_node.get('files', [''])[0] if custom_node.get('files') else '',
                    description=custom_node.get('description', ''),
                    install_command=f"ComfyUI Manager install: {custom_node.get('title', 'Unknown')}"
                )
                if node_info not in results:
                    results.append(node_info)
        
        return results
    
    def search_in_known_repos(self, node_name: str) -> List[NodeInfo]:
        """Search for nodes in known repositories"""
        results = []
        
        for repo_name, repo_info in self.known_repos.items():
            nodes_list = repo_info.get('nodes', [])
            if node_name in nodes_list:
                node_info = NodeInfo(
                    name=node_name,
                    source_url=repo_info.get('github_url', ''),
                    github_url=repo_info.get('github_url', ''),
                    description=repo_info.get('description', f"From {repo_info.get('title', repo_name)} repository"),
                    install_command=f"git clone {repo_info.get('install_url', repo_info.get('github_url', ''))}"
                )
                results.append(node_info)
        
        return results
    
    def github_search(self, node_name: str) -> List[NodeInfo]:
        """Search for nodes on GitHub"""
        results = []
        
        try:
            # Search ComfyUI-related repositories
            search_query = f"{node_name} ComfyUI custom node"
            api_url = f"https://api.github.com/search/repositories"
            params = {
                'q': search_query,
                'sort': 'stars',
                'order': 'desc'
            }
            
            response = requests.get(api_url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for repo in data.get('items', [])[:3]:  # Only take top 3 results
                    node_info = NodeInfo(
                        name=node_name,
                        source_url=repo['html_url'],
                        github_url=repo['html_url'],
                        description=repo.get('description', ''),
                        install_command=f"git clone {repo['clone_url']}"
                    )
                    results.append(node_info)
        except Exception as e:
            print(f"⚠️ GitHub search failed: {e}")
        
        return results
    
    def search_missing_nodes(self, custom_nodes: Set[str]) -> Dict[str, List[NodeInfo]]:
        """Search for missing custom nodes"""
        results = {}
        
        print(f"🔍 Starting search for {len(custom_nodes)} custom nodes...")
        
        for i, node_name in enumerate(custom_nodes, 1):
            print(f"[{i}/{len(custom_nodes)}] Searching node: {node_name}")
            
            node_results = []
            
            # 1. Search in known repositories
            known_results = self.search_in_known_repos(node_name)
            node_results.extend(known_results)
            
            # 2. Search in ComfyUI Manager database
            if self.node_db:
                db_results = self.search_node_in_db(node_name)
                node_results.extend(db_results)
            
            # 3. If not found, search on GitHub
            if not node_results:
                github_results = self.github_search(node_name)
                node_results.extend(github_results)
            
            results[node_name] = node_results
            
            # Avoid API limits
            if i < len(custom_nodes):
                time.sleep(0.5)
        
        return results
    
    def generate_report(self, missing_nodes: Dict[str, List[NodeInfo]], output_file: Optional[str] = None) -> str:
        """Generate search report"""
        report_lines = []
        report_lines.append("# ComfyUI Custom Node Search Report")
        report_lines.append("")
        report_lines.append(f"Search time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Total nodes searched: {len(missing_nodes)}")
        report_lines.append("")
        
        found_count = sum(1 for results in missing_nodes.values() if results)
        report_lines.append(f"Found nodes: {found_count}")
        report_lines.append(f"Not found nodes: {len(missing_nodes) - found_count}")
        report_lines.append("")
        
        # Found nodes
        if found_count > 0:
            report_lines.append("## 🎯 Found Nodes")
            report_lines.append("")
            
            for node_name, results in missing_nodes.items():
                if results:
                    report_lines.append(f"### {node_name}")
                    report_lines.append("")
                    
                    for i, result in enumerate(results, 1):
                        report_lines.append(f"**Option {i}:**")
                        if result.source_url:
                            report_lines.append(f"- 🔗 Source link: {result.source_url}")
                        if result.description:
                            report_lines.append(f"- 📝 Description: {result.description}")
                        if result.install_command:
                            report_lines.append(f"- 💾 Install command: `{result.install_command}`")
                        report_lines.append("")
                    
                    report_lines.append("---")
                    report_lines.append("")
        
        # Not found nodes
        not_found = [name for name, results in missing_nodes.items() if not results]
        if not_found:
            report_lines.append("## ❓ Not Found Nodes")
            report_lines.append("")
            report_lines.append("The following nodes need manual search:")
            report_lines.append("")
            
            for node_name in not_found:
                report_lines.append(f"- `{node_name}`")
                report_lines.append(f"  - 🔍 Google search: https://www.google.com/search?q={node_name}+ComfyUI+custom+node")
                report_lines.append(f"  - 🔍 GitHub search: https://github.com/search?q={node_name}+ComfyUI")
                report_lines.append("")
        
        # Installation guide
        report_lines.append("## 📦 Installation Guide")
        report_lines.append("")
        report_lines.append("### Method 1: ComfyUI Manager (Recommended)")
        report_lines.append("1. Install ComfyUI Manager")
        report_lines.append("2. Click 'Manager' button in ComfyUI interface")
        report_lines.append("3. Search and install corresponding node packages")
        report_lines.append("")
        
        report_lines.append("### Method 2: Manual Installation")
        report_lines.append("1. Navigate to ComfyUI/custom_nodes directory")
        report_lines.append("2. Run git clone command to clone node repository")
        report_lines.append("3. Restart ComfyUI")
        report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        # Save to file
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                print(f"✅ Report saved to: {output_file}")
            except Exception as e:
                print(f"❌ Failed to save report: {e}")
        
        return report_content
    
    def analyze_workflow(self, workflow_path: str, output_file: Optional[str] = None) -> str:
        """Analyze workflow and generate report"""
        print(f"📄 Analyzing workflow file: {workflow_path}")
        
        # Load workflow
        workflow = self.load_workflow(workflow_path)
        if not workflow:
            return "❌ Unable to load workflow file"
        
        # Extract node types
        all_nodes = self.extract_node_types(workflow)
        print(f"📊 Found {len(all_nodes)} node types")
        
        # Identify custom nodes
        custom_nodes = self.identify_custom_nodes(all_nodes)
        print(f"🔧 Found {len(custom_nodes)} custom nodes:")
        for node in sorted(custom_nodes):
            print(f"  - {node}")
        print()
        
        if not custom_nodes:
            return "✅ This workflow does not use custom nodes"
        
        # Load node database
        self.load_comfyui_manager_db()
        
        # Search missing nodes
        missing_nodes = self.search_missing_nodes(custom_nodes)
        
        # Generate report
        return self.generate_report(missing_nodes, output_file)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="ComfyUI Workflow Custom Node Searcher")
    parser.add_argument("workflow", help="Workflow file path (.json)")
    parser.add_argument("-o", "--output", help="Output report file path (.md)", default="node_search_report.md")
    parser.add_argument("--no-save", action="store_true", help="Do not save report to file")
    parser.add_argument("--comfyui-path", help="ComfyUI installation path (default: ./ComfyUI)")
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.workflow).exists():
        print(f"❌ Workflow file does not exist: {args.workflow}")
        sys.exit(1)
    
    # Create searcher
    searcher = ComfyUINodeSearcher(comfyui_path=args.comfyui_path)
    
    # Display loaded built-in node information
    print(f"🔧 Loaded {len(searcher.builtin_nodes)} built-in nodes")
    print(f"📚 Loaded {len(searcher.known_repos)} known node packages")
    print()
    
    # Analyze workflow
    output_file = None if args.no_save else args.output
    report = searcher.analyze_workflow(args.workflow, output_file)
    
    # Display report
    if args.no_save:
        print("\n" + "="*60)
        print(report)

if __name__ == "__main__":
    main()
