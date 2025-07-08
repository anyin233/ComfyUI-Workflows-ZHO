#!/usr/bin/env python3
"""
Advanced ComfyUI Node Analyzer
Analyzes workflows to identify incompatible nodes and suggest replacements
"""

import json
import os
from collections import Counter
from typing import Dict, List, Set

class NodeAnalyzer:
    def __init__(self):
        self.supported_nodes = {
            # Basic loaders
            "CheckpointLoaderSimple", "DualCLIPLoader", "VAELoader", "UNETLoader", "LoraLoader",
            
            # Text encoding
            "CLIPTextEncode", "CLIPTextEncodeFlux",
            
            # Sampling and generation
            "KSampler", "KSamplerAdvanced", "SamplerCustomAdvanced", "BasicScheduler", "BasicGuider",
            "RandomNoise", "KSamplerSelect",
            
            # Image processing
            "VAEDecode", "VAEEncode", "EmptyLatentImage", "LatentUpscale",
            
            # Image output
            "SaveImage", "PreviewImage",
            
            # ControlNet
            "ControlNetLoader", "ControlNetApply",
            
            # Special nodes
            "PortraitMaster_中文版", "workflow/FLUX", "workflow/SD3",
        }
        
        self.replaceable_nodes = {
            # Video/Animation -> Static alternatives
            "VHS_VideoCombine": "Static image generation",
            "VHS_LoadVideo": "Image loading from video frames",
            "LivePortraitProcess": "Enhanced portrait generation",
            "LivePortraitComposite": "Standard image composition",
            
            # 3D -> 2D alternatives
            "CRM": "Enhanced 2D with 3D-like prompts",
            "InstantMesh": "Multi-view 2D generation",
            "TripoSR": "Depth-aware 2D generation",
            
            # Advanced sampling -> Standard alternatives
            "RandomNoise": "Standard torch noise generation",
            "KSamplerSelect": "Scheduler configuration",
            "SamplerCustomAdvanced": "Pipeline default sampling",
            
            # Image processing -> PIL/CV2
            "ImageScale": "PIL resize",
            "ImageResize": "PIL resize",
            "ImageCrop": "PIL crop",
            "ImageRotate": "PIL rotate",
        }
        
        self.critical_nodes = {
            # Nodes that significantly change workflow behavior
            "VHS_VideoCombine", "VHS_LoadVideo", "LivePortraitProcess",
            "CRM", "InstantMesh", "TripoSR",
            "workflow/VIDEO", "workflow/ANIMATE"
        }
    
    def analyze_workflow(self, workflow_path: str) -> Dict:
        """Analyze a single workflow file"""
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow = json.load(f)
        except Exception as e:
            return {"error": f"Failed to read workflow: {e}"}
        
        nodes = workflow.get('nodes', [])
        node_types = [node.get('type', '') for node in nodes if isinstance(node, dict)]
        
        analysis = {
            "file": os.path.basename(workflow_path),
            "total_nodes": len(node_types),
            "unique_node_types": len(set(node_types)),
            "supported_nodes": [],
            "replaceable_nodes": [],
            "unsupported_nodes": [],
            "critical_issues": [],
            "conversion_difficulty": "Easy"
        }
        
        for node_type in set(node_types):
            if node_type in self.supported_nodes:
                analysis["supported_nodes"].append(node_type)
            elif node_type in self.replaceable_nodes:
                analysis["replaceable_nodes"].append({
                    "node": node_type,
                    "replacement": self.replaceable_nodes[node_type]
                })
            else:
                analysis["unsupported_nodes"].append(node_type)
            
            if node_type in self.critical_nodes:
                analysis["critical_issues"].append(node_type)
        
        # Determine conversion difficulty
        if analysis["critical_issues"]:
            analysis["conversion_difficulty"] = "Hard"
        elif analysis["unsupported_nodes"]:
            analysis["conversion_difficulty"] = "Medium"
        
        return analysis
    
    def analyze_all_workflows(self, workflow_dir: str) -> Dict:
        """Analyze all workflows in a directory"""
        if not os.path.exists(workflow_dir):
            return {"error": f"Directory {workflow_dir} not found"}
        
        results = {
            "summary": {
                "total_workflows": 0,
                "easy_conversion": 0,
                "medium_conversion": 0,
                "hard_conversion": 0,
                "most_common_unsupported": [],
                "most_common_replaceable": []
            },
            "workflows": []
        }
        
        all_unsupported = []
        all_replaceable = []
        
        for filename in os.listdir(workflow_dir):
            if filename.endswith('.json'):
                workflow_path = os.path.join(workflow_dir, filename)
                analysis = self.analyze_workflow(workflow_path)
                
                if "error" not in analysis:
                    results["workflows"].append(analysis)
                    results["summary"]["total_workflows"] += 1
                    
                    # Count by difficulty
                    if analysis["conversion_difficulty"] == "Easy":
                        results["summary"]["easy_conversion"] += 1
                    elif analysis["conversion_difficulty"] == "Medium":
                        results["summary"]["medium_conversion"] += 1
                    else:
                        results["summary"]["hard_conversion"] += 1
                    
                    # Collect node statistics
                    all_unsupported.extend(analysis["unsupported_nodes"])
                    all_replaceable.extend([r["node"] for r in analysis["replaceable_nodes"]])
        
        # Calculate most common issues
        if all_unsupported:
            unsupported_counter = Counter(all_unsupported)
            results["summary"]["most_common_unsupported"] = unsupported_counter.most_common(10)
        
        if all_replaceable:
            replaceable_counter = Counter(all_replaceable)
            results["summary"]["most_common_replaceable"] = replaceable_counter.most_common(10)
        
        return results
    
    def generate_report(self, analysis: Dict) -> str:
        """Generate a detailed analysis report"""
        if "error" in analysis:
            return f"Error: {analysis['error']}"
        
        if "workflows" in analysis:  # Multiple workflows
            return self._generate_summary_report(analysis)
        else:  # Single workflow
            return self._generate_single_report(analysis)
    
    def _generate_summary_report(self, analysis: Dict) -> str:
        """Generate summary report for multiple workflows"""
        summary = analysis["summary"]
        report = []
        
        report.append("🔍 ComfyUI Workflow Analysis Report")
        report.append("=" * 50)
        report.append("")
        
        report.append(f"📊 Summary Statistics:")
        report.append(f"  Total workflows analyzed: {summary['total_workflows']}")
        report.append(f"  Easy conversion: {summary['easy_conversion']} ({summary['easy_conversion']/summary['total_workflows']*100:.1f}%)")
        report.append(f"  Medium conversion: {summary['medium_conversion']} ({summary['medium_conversion']/summary['total_workflows']*100:.1f}%)")
        report.append(f"  Hard conversion: {summary['hard_conversion']} ({summary['hard_conversion']/summary['total_workflows']*100:.1f}%)")
        report.append("")
        
        if summary["most_common_unsupported"]:
            report.append("⚠️  Most Common Unsupported Nodes:")
            for node, count in summary["most_common_unsupported"]:
                report.append(f"  {node}: {count} workflows")
            report.append("")
        
        if summary["most_common_replaceable"]:
            report.append("🔄 Most Common Replaceable Nodes:")
            for node, count in summary["most_common_replaceable"]:
                replacement = self.replaceable_nodes.get(node, "See documentation")
                report.append(f"  {node}: {count} workflows -> {replacement}")
            report.append("")
        
        # Individual workflow details
        report.append("📝 Individual Workflow Analysis:")
        report.append("-" * 30)
        
        for workflow in analysis["workflows"]:
            difficulty_emoji = {"Easy": "✅", "Medium": "⚠️", "Hard": "❌"}
            emoji = difficulty_emoji.get(workflow["conversion_difficulty"], "❓")
            
            report.append(f"{emoji} {workflow['file']} ({workflow['conversion_difficulty']})")
            report.append(f"   Nodes: {workflow['total_nodes']} total, {workflow['unique_node_types']} unique types")
            
            if workflow["critical_issues"]:
                report.append(f"   Critical issues: {', '.join(workflow['critical_issues'])}")
            
            if workflow["unsupported_nodes"]:
                report.append(f"   Unsupported: {', '.join(workflow['unsupported_nodes'][:3])}{'...' if len(workflow['unsupported_nodes']) > 3 else ''}")
            
            report.append("")
        
        return "\n".join(report)
    
    def _generate_single_report(self, analysis: Dict) -> str:
        """Generate detailed report for a single workflow"""
        report = []
        
        report.append(f"🔍 Analysis: {analysis['file']}")
        report.append("=" * 50)
        report.append("")
        
        difficulty_emoji = {"Easy": "✅", "Medium": "⚠️", "Hard": "❌"}
        emoji = difficulty_emoji.get(analysis["conversion_difficulty"], "❓")
        
        report.append(f"Conversion Difficulty: {emoji} {analysis['conversion_difficulty']}")
        report.append(f"Total Nodes: {analysis['total_nodes']}")
        report.append(f"Unique Node Types: {analysis['unique_node_types']}")
        report.append("")
        
        if analysis["supported_nodes"]:
            report.append("✅ Supported Nodes:")
            for node in sorted(analysis["supported_nodes"]):
                report.append(f"   {node}")
            report.append("")
        
        if analysis["replaceable_nodes"]:
            report.append("🔄 Replaceable Nodes:")
            for item in analysis["replaceable_nodes"]:
                report.append(f"   {item['node']} -> {item['replacement']}")
            report.append("")
        
        if analysis["unsupported_nodes"]:
            report.append("❌ Unsupported Nodes:")
            for node in sorted(analysis["unsupported_nodes"]):
                report.append(f"   {node}")
            report.append("")
        
        if analysis["critical_issues"]:
            report.append("🚨 Critical Issues:")
            for issue in analysis["critical_issues"]:
                report.append(f"   {issue} - Requires manual handling")
            report.append("")
        
        return "\n".join(report)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze ComfyUI workflows for conversion compatibility')
    parser.add_argument('-i', '--input', help='Input workflow file or directory', default='workflows/zho')
    parser.add_argument('-o', '--output', help='Output report file (optional)')
    parser.add_argument('--summary', action='store_true', help='Show only summary for directory analysis')
    
    args = parser.parse_args()
    
    analyzer = NodeAnalyzer()
    
    if os.path.isfile(args.input):
        # Analyze single file
        analysis = analyzer.analyze_workflow(args.input)
    else:
        # Analyze directory
        analysis = analyzer.analyze_all_workflows(args.input)
    
    report = analyzer.generate_report(analysis)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to: {args.output}")
    else:
        print(report)

if __name__ == "__main__":
    main()
