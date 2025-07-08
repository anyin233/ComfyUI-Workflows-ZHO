#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI Workflow Batch Node Searcher
Batch analyze custom nodes in multiple workflow files
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, Set, List
from comfyui_node_searcher import ComfyUINodeSearcher
import time

class BatchNodeSearcher:
    """批量nodesearch器"""
    
    def __init__(self, comfyui_path: str = None):
        self.searcher = ComfyUINodeSearcher(comfyui_path)
        self.all_custom_nodes = set()
        self.workflow_results = {}
    
    def find_workflow_files(self, directory: str, recursive: bool = True) -> List[Path]:
        """finddirectory中的workflowfile"""
        directory = Path(directory)
        
        if recursive:
            pattern = "**/*.json"
        else:
            pattern = "*.json"
        
        workflow_files = []
        for json_file in directory.glob(pattern):
            # 简单check是否为workflowfile
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'nodes' in data or ('extra' in data and 'groupNodes' in data.get('extra', {})):
                        workflow_files.append(json_file)
            except:
                continue
        
        return workflow_files
    
    def analyze_workflow_batch(self, workflow_files: List[Path]) -> Dict:
        """批量analyzeworkflowfile"""
        results = {
            'total_workflows': len(workflow_files),
            'workflows': {},
            'all_custom_nodes': set(),
            'node_usage_count': {},
            'missing_nodes': {}
        }
        
        print(f"🔍 start批量analyze {len(workflow_files)} 个workflowfile...")
        print()
        
        for i, workflow_file in enumerate(workflow_files, 1):
            print(f"[{i}/{len(workflow_files)}] analyze: {workflow_file.name}")
            
            try:
                # loadworkflow
                workflow = self.searcher.load_workflow(str(workflow_file))
                if not workflow:
                    continue
                
                # 提取nodetype
                all_nodes = self.searcher.extract_node_types(workflow)
                custom_nodes = self.searcher.identify_custom_nodes(all_nodes)
                
                # 记录result
                results['workflows'][str(workflow_file)] = {
                    'total_nodes': len(all_nodes),
                    'custom_nodes': list(custom_nodes),
                    'custom_node_count': len(custom_nodes)
                }
                
                # statisticsnode使用次数
                for node in custom_nodes:
                    results['node_usage_count'][node] = results['node_usage_count'].get(node, 0) + 1
                
                # 收集所有customnode
                results['all_custom_nodes'].update(custom_nodes)
                
                print(f"  发现 {len(custom_nodes)} 个customnode")
                
            except Exception as e:
                print(f"  ❌ analyzefailed: {e}")
                continue
        
        # 转换集合为列表以便 JSON 序列化
        results['all_custom_nodes'] = list(results['all_custom_nodes'])
        
        print()
        print(f"✅ 批量analyzecomplete!")
        print(f"📊 total发现 {len(results['all_custom_nodes'])} 个不同的customnode")
        
        return results
    
    def search_all_missing_nodes(self, custom_nodes: Set[str]) -> Dict:
        """search所有缺失的node"""
        if not custom_nodes:
            return {}
        
        print(f"🔍 startsearch {len(custom_nodes)} 个customnode的downloadlink...")
        
        # load ComfyUI Manager database
        self.searcher.load_comfyui_manager_db()
        
        # search缺失的node
        return self.searcher.search_missing_nodes(custom_nodes)
    
    def generate_batch_report(self, results: Dict, missing_nodes: Dict, output_file: str = None) -> str:
        """generate批量analyzereport"""
        report_lines = []
        report_lines.append("# ComfyUI workflow批量nodeanalyzereport")
        report_lines.append("")
        report_lines.append(f"analyze时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"analyze的workflowcount: {results['total_workflows']}")
        report_lines.append(f"发现的customnode总数: {len(results['all_custom_nodes'])}")
        report_lines.append("")
        
        # node使用statistics
        if results['node_usage_count']:
            report_lines.append("## 📊 node使用statistics")
            report_lines.append("")
            report_lines.append("| 节点名称 | 使用次数 | 使用的工作流 |")
            report_lines.append("|---------|---------|-------------|")
            
            # 按使用次数sort
            sorted_nodes = sorted(results['node_usage_count'].items(), key=lambda x: x[1], reverse=True)
            
            for node_name, count in sorted_nodes:
                # 找到使用该node的workflow
                using_workflows = []
                for workflow_path, workflow_info in results['workflows'].items():
                    if node_name in workflow_info['custom_nodes']:
                        using_workflows.append(Path(workflow_path).name)
                
                workflows_text = ", ".join(using_workflows[:3])  # 只display前3个
                if len(using_workflows) > 3:
                    workflows_text += f" 等{len(using_workflows)}个"
                
                report_lines.append(f"| `{node_name}` | {count} | {workflows_text} |")
            
            report_lines.append("")
        
        # 各workflow详情
        report_lines.append("## 📁 workflow详情")
        report_lines.append("")
        
        for workflow_path, workflow_info in results['workflows'].items():
            workflow_name = Path(workflow_path).name
            report_lines.append(f"### {workflow_name}")
            report_lines.append("")
            report_lines.append(f"- 总node数: {workflow_info['total_nodes']}")
            report_lines.append(f"- customnode数: {workflow_info['custom_node_count']}")
            
            if workflow_info['custom_nodes']:
                report_lines.append("- 自定义节点列表:")
                for node in workflow_info['custom_nodes']:
                    report_lines.append(f"  - `{node}`")
            
            report_lines.append("")
        
        # nodesearchresult
        if missing_nodes:
            found_count = sum(1 for results in missing_nodes.values() if results)
            report_lines.append("## 🔍 nodesearchresult")
            report_lines.append("")
            report_lines.append(f"找到downloadlink的node: {found_count}")
            report_lines.append(f"未找到的node: {len(missing_nodes) - found_count}")
            report_lines.append("")
            
            # 找到的node
            if found_count > 0:
                report_lines.append("### 🎯 找到的node")
                report_lines.append("")
                
                for node_name, node_results in missing_nodes.items():
                    if node_results:
                        report_lines.append(f"#### {node_name}")
                        report_lines.append("")
                        
                        for i, result in enumerate(node_results[:3], 1):  # 只display前3个result
                            report_lines.append(f"**option {i}:**")
                            if result.source_url:
                                report_lines.append(f"- 🔗 源码link: {result.source_url}")
                            if result.description:
                                report_lines.append(f"- 📝 description: {result.description}")
                            if result.install_command:
                                report_lines.append(f"- 💾 installationcommand: `{result.install_command}`")
                            report_lines.append("")
                        
                        report_lines.append("---")
                        report_lines.append("")
            
            # 未找到的node
            not_found = [name for name, results in missing_nodes.items() if not results]
            if not_found:
                report_lines.append("### ❓ 未找到的node")
                report_lines.append("")
                
                for node_name in not_found:
                    report_lines.append(f"- `{node_name}`")
                    report_lines.append(f"  - 🔍 Google search: https://www.google.com/search?q={node_name}+ComfyUI+custom+node")
                    report_lines.append(f"  - 🔍 GitHub search: https://github.com/search?q={node_name}+ComfyUI")
                    report_lines.append("")
        
        # installation指南
        report_lines.append("## 📦 installation指南")
        report_lines.append("")
        report_lines.append("### 方法1: ComfyUI Manager (推荐)")
        report_lines.append("1. 安装 ComfyUI Manager")
        report_lines.append("2. 在 ComfyUI 界面中点击 'Manager' 按钮")
        report_lines.append("3. 搜索并安装对应的节点包")
        report_lines.append("")
        
        report_lines.append("### 方法2: 手动installation")
        report_lines.append("1. 进入 ComfyUI/custom_nodes 目录")
        report_lines.append("2. 运行 git clone 命令克隆节点仓库")
        report_lines.append("3. 重启 ComfyUI")
        report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        # save到file
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                print(f"✅ 批量analyzereport已save到: {output_file}")
            except Exception as e:
                print(f"❌ savereportfailed: {e}")
        
        return report_content

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="ComfyUI 工作流批量节点搜索器")
    parser.add_argument("directory", help="包含工作流文件的目录")
    parser.add_argument("-o", "--output", help="输出报告文件路径 (.md)", default="batch_node_analysis_report.md")
    parser.add_argument("--no-save", action="store_true", help="不保存报告到文件")
    parser.add_argument("--no-recursive", action="store_true", help="不递归搜索子目录")
    parser.add_argument("--comfyui-path", help="ComfyUI 安装路径 (默认: ./ComfyUI)")
    parser.add_argument("--no-search", action="store_true", help="不搜索节点下载链接（只分析）")
    
    args = parser.parse_args()
    
    # checkdirectory是否exists
    if not Path(args.directory).exists():
        print(f"❌ directory不exists: {args.directory}")
        return
    
    # create批量search器
    batch_searcher = BatchNodeSearcher(comfyui_path=args.comfyui_path)
    
    # findworkflowfile
    workflow_files = batch_searcher.find_workflow_files(args.directory, not args.no_recursive)
    
    if not workflow_files:
        print(f"❌ 在directory {args.directory} 中未找到workflowfile")
        return
    
    print(f"📁 在directory {args.directory} 中找到 {len(workflow_files)} 个workflowfile")
    print()
    
    # 批量analyze
    results = batch_searcher.analyze_workflow_batch(workflow_files)
    
    # searchnodedownloadlink
    missing_nodes = {}
    if not args.no_search and results['all_custom_nodes']:
        missing_nodes = batch_searcher.search_all_missing_nodes(set(results['all_custom_nodes']))
    
    # generatereport
    output_file = None if args.no_save else args.output
    report = batch_searcher.generate_batch_report(results, missing_nodes, output_file)
    
    # displayreport
    if args.no_save:
        print("\n" + "="*80)
        print(report)

if __name__ == "__main__":
    main()
