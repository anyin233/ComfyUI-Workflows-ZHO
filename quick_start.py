#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI Node Searcher - Quick Start Script
Simplified command line interface, suitable for new users to get started quickly
"""

import sys
import argparse
from pathlib import Path
from comfyui_node_searcher import ComfyUINodeSearcher
from batch_node_searcher import BatchNodeSearcher

def print_banner():
    """Print welcome information"""
    print("=" * 60)
    print("🎨 ComfyUI Workflow Custom Node Searcher")
    print("   Automatically search for missing nodes in workflows and provide download links")
    print("=" * 60)
    print()

def analyze_single_workflow():
    """Analyze single workflow file"""
    print("📄 Single workflow analysis mode")
    print()
    
    # Get workflow file path
    workflow_path = input("Please enter workflow file path: ").strip()
    
    if not Path(workflow_path).exists():
        print(f"❌ file不exists: {workflow_path}")
        return
    
    print(f"🔍 analyzeworkflow: {workflow_path}")
    print()
    
    # createsearch器并analyze
    searcher = ComfyUINodeSearcher()
    report = searcher.analyze_workflow(workflow_path, "single_analysis_report.md")
    
    print("\n✅ analyzecomplete！report已save到: single_analysis_report.md")
    
    # 询问是否查看report
    view_report = input("\n是否在终端中查看报告? (y/n): ").lower()
    if view_report == 'y':
        print("\n" + "="*60)
        print(report)

def analyze_batch_workflows():
    """批量analyzeworkflowfile"""
    print("📁 批量workflowanalyzemode")
    print()
    
    # getdirectorypath
    directory = input("请输入包含工作流的目录路径: ").strip()
    
    if not Path(directory).exists():
        print(f"❌ directory不exists: {directory}")
        return
    
    # 询问是否递归search
    recursive = input("是否搜索子目录? (y/n): ").lower() == 'y'
    
    # 询问是否searchdownloadlink
    search_links = input("是否搜索节点下载链接? (y/n): ").lower() == 'y'
    
    print(f"🔍 批量analyzedirectory: {directory}")
    if recursive:
        print("📂 包含子directory")
    if search_links:
        print("🌐 将searchdownloadlink")
    print()
    
    # create批量search器
    batch_searcher = BatchNodeSearcher()
    
    # findworkflowfile
    workflow_files = batch_searcher.find_workflow_files(directory, recursive)
    
    if not workflow_files:
        print(f"❌ 在directory {directory} 中未找到workflowfile")
        return
    
    print(f"📄 找到 {len(workflow_files)} 个workflowfile")
    
    # 确认continue
    confirm = input("是否继续分析? (y/n): ").lower()
    if confirm != 'y':
        print("❌ analyze已取消")
        return
    
    # execute批量analyze
    results = batch_searcher.analyze_workflow_batch(workflow_files)
    
    # searchnodedownloadlink
    missing_nodes = {}
    if search_links and results['all_custom_nodes']:
        missing_nodes = batch_searcher.search_all_missing_nodes(set(results['all_custom_nodes']))
    
    # generatereport
    report = batch_searcher.generate_batch_report(results, missing_nodes, "batch_analysis_report.md")
    
    print("\n✅ 批量analyzecomplete！report已save到: batch_analysis_report.md")
    
    # display简要statistics
    print(f"\n📊 analyze摘要:")
    print(f"   - workflowcount: {results['total_workflows']}")
    print(f"   - customnode数: {len(results['all_custom_nodes'])}")
    if missing_nodes:
        found_count = sum(1 for results in missing_nodes.values() if results)
        print(f"   - 找到downloadlink: {found_count}")

def main():
    """主函数"""
    print_banner()
    
    # 如果有command行parameter，直接process
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="ComfyUI 节点搜索器快速入门")
        parser.add_argument("file_or_dir", help="工作流文件或目录路径")
        parser.add_argument("--batch", action="store_true", help="批量分析模式")
        parser.add_argument("--no-search", action="store_true", help="不搜索下载链接")
        
        args = parser.parse_args()
        
        if args.batch or Path(args.file_or_dir).is_dir():
            # 批量mode
            batch_searcher = BatchNodeSearcher()
            workflow_files = batch_searcher.find_workflow_files(args.file_or_dir)
            
            if not workflow_files:
                print(f"❌ 在 {args.file_or_dir} 中未找到workflowfile")
                return
            
            results = batch_searcher.analyze_workflow_batch(workflow_files)
            
            missing_nodes = {}
            if not args.no_search and results['all_custom_nodes']:
                missing_nodes = batch_searcher.search_all_missing_nodes(set(results['all_custom_nodes']))
            
            batch_searcher.generate_batch_report(results, missing_nodes, "batch_analysis_report.md")
            print("✅ 批量analyzecomplete！")
        else:
            # 单filemode
            searcher = ComfyUINodeSearcher()
            searcher.analyze_workflow(args.file_or_dir, "single_analysis_report.md")
            print("✅ 单fileanalyzecomplete！")
        
        return
    
    # 交互式mode
    print("请选择analyzemode:")
    print("1. analyze单个workflowfile")
    print("2. 批量analyzeworkflowdirectory")
    print("3. 退出")
    print()
    
    while True:
        choice = input("请输入选择 (1-3): ").strip()
        
        if choice == '1':
            analyze_single_workflow()
            break
        elif choice == '2':
            analyze_batch_workflows()
            break
        elif choice == '3':
            print("👋 再见！")
            break
        else:
            print("❌ invalid选择，请input 1、2 或 3")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作，再见！")
    except Exception as e:
        print(f"\n❌ 发生error: {e}")
        print("请checkinput或联系开发者get帮助")
