#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to translate all Chinese comments to English across the project
"""

import os
import re
from pathlib import Path

# Translation mappings for common Chinese comments
TRANSLATION_MAP = {
    # Common patterns
    "加载": "load",
    "搜索": "search",
    "分析": "analyze", 
    "生成": "generate",
    "创建": "create",
    "检查": "check",
    "获取": "get",
    "设置": "set",
    "处理": "process",
    "保存": "save",
    "显示": "display",
    "打印": "print",
    "输出": "output",
    "输入": "input",
    "文件": "file",
    "路径": "path",
    "目录": "directory",
    "节点": "node",
    "工作流": "workflow",
    "自定义": "custom",
    "内置": "built-in",
    "仓库": "repository",
    "数据库": "database",
    "报告": "report",
    "结果": "result",
    "信息": "information",
    "配置": "configuration",
    "安装": "installation",
    "命令": "command",
    "参数": "parameter",
    "选项": "option",
    "模式": "mode",
    "类型": "type",
    "名称": "name",
    "描述": "description",
    "链接": "link",
    "下载": "download",
    "失败": "failed",
    "成功": "success",
    "错误": "error",
    "警告": "warning",
    "开始": "start",
    "结束": "end",
    "完成": "complete",
    "跳过": "skip",
    "继续": "continue",
    "停止": "stop",
    "运行": "run",
    "执行": "execute",
    "初始化": "initialize",
    "更新": "update",
    "删除": "delete",
    "添加": "add",
    "修改": "modify",
    "编辑": "edit",
    "查找": "find",
    "替换": "replace",
    "匹配": "match",
    "验证": "validate",
    "测试": "test",
    "调试": "debug",
    "排序": "sort",
    "过滤": "filter",
    "计算": "calculate",
    "统计": "statistics",
    "数量": "count",
    "总共": "total",
    "当前": "current",
    "默认": "default",
    "可选": "optional",
    "必需": "required",
    "有效": "valid",
    "无效": "invalid",
    "空": "empty",
    "存在": "exists",
    "不存在": "does not exist",
    "可用": "available",
    "不可用": "unavailable",
    
    # Specific phrases
    "ComfyUI 工作流自定义节点搜索器": "ComfyUI Workflow Custom Node Searcher",
    "自动搜索工作流中缺失的自定义节点并提供下载链接": "Automatically search for missing custom nodes in workflows and provide download links",
    "ComfyUI 节点搜索器": "ComfyUI Node Searcher",
    "快速入门脚本": "Quick Start Script",
    "简化的命令行界面，适合新用户快速上手": "Simplified command line interface, suitable for new users to get started quickly",
    "节点信息": "Node information",
    "ComfyUI 节点搜索器": "ComfyUI Node Searcher",
    "自动检测 ComfyUI 路径": "Auto-detect ComfyUI path",
    "从本地数据库加载已知节点信息": "Load known node information from local database",
    "ComfyUI Manager 节点数据库 API": "ComfyUI Manager node database API",
    "从 ComfyUI 子模块中加载内置节点列表": "Load built-in node list from ComfyUI submodule",
    "默认的节点列表作为备用": "Default node list as fallback",
    "ComfyUI 新版本的采样器相关节点": "ComfyUI new version sampler-related nodes",
    "尝试从 ComfyUI/nodes.py 中提取 NODE_CLASS_MAPPINGS": "Try to extract NODE_CLASS_MAPPINGS from ComfyUI/nodes.py",
    "从 ComfyUI 子模块加载内置节点": "Loading built-in nodes from ComfyUI submodule",
    "读取文件内容": "Read file content",
    "使用正则表达式提取 NODE_CLASS_MAPPINGS 中的键": "Use regex to extract keys from NODE_CLASS_MAPPINGS",
    "提取每行的节点名称": "Extract node names from each line",
    "从 NODE_CLASS_MAPPINGS 中提取到": "Extracted from NODE_CLASS_MAPPINGS",
    "个内置节点": "built-in nodes",
    "未找到 NODE_CLASS_MAPPINGS，使用默认节点列表": "NODE_CLASS_MAPPINGS not found, using default node list",
    "ComfyUI nodes.py 文件不存在": "ComfyUI nodes.py file does not exist",
    "使用默认内置节点列表": "Using default built-in node list",
    "加载 ComfyUI 内置节点失败": "Failed to load ComfyUI built-in nodes",
    "检查 comfy_extras 目录中的额外节点": "Check for additional nodes in comfy_extras directory",
    "从文件名推导节点类型（这是一个简化的方法）": "Derive node type from filename (simplified method)",
    "这些通常是 API 节点，我们可以将它们标记为内置节点": "These are usually API nodes, we can mark them as built-in nodes",
    "发现额外节点文件": "Found additional node file",
    "检查 comfy_extras 失败": "Failed to check comfy_extras",
    "加载本地节点数据库": "Load local node database",
    "加载本地节点数据库": "Loaded local node database",
    "个已知节点包": "known node packages",
    "本地节点数据库不存在，使用默认配置": "Local node database does not exist, using default configuration",
    "加载本地节点数据库失败": "Failed to load local node database"
}

def translate_chinese_comments(content: str) -> str:
    """Translate Chinese comments in the content"""
    lines = content.split('\n')
    translated_lines = []
    
    for line in lines:
        translated_line = line
        
        # Handle docstrings
        if '"""' in line:
            for chinese, english in TRANSLATION_MAP.items():
                if chinese in line:
                    translated_line = translated_line.replace(chinese, english)
        
        # Handle single line comments
        elif line.strip().startswith('#'):
            for chinese, english in TRANSLATION_MAP.items():
                if chinese in line:
                    translated_line = translated_line.replace(chinese, english)
        
        # Handle inline comments
        elif '#' in line and not line.strip().startswith('"') and not line.strip().startswith("'"):
            comment_start = line.find('#')
            code_part = line[:comment_start]
            comment_part = line[comment_start:]
            
            for chinese, english in TRANSLATION_MAP.items():
                if chinese in comment_part:
                    comment_part = comment_part.replace(chinese, english)
            
            translated_line = code_part + comment_part
        
        # Handle f-strings and print statements with Chinese text
        else:
            for chinese, english in TRANSLATION_MAP.items():
                if chinese in line and ('print(' in line or 'f"' in line or "f'" in line):
                    translated_line = translated_line.replace(chinese, english)
        
        translated_lines.append(translated_line)
    
    return '\n'.join(translated_lines)

def process_file(file_path: Path):
    """Process a single file to translate Chinese comments"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file contains Chinese characters
        if re.search(r'[\u4e00-\u9fff]', content):
            translated_content = translate_chinese_comments(content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            
            print(f"✅ Translated: {file_path}")
        else:
            print(f"⏭️  Skipped: {file_path} (no Chinese content)")
    
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

def main():
    """Main function to process all Python files in the project"""
    project_root = Path(__file__).parent
    
    # Find all Python files (excluding ComfyUI submodule and __pycache__)
    python_files = []
    for file_path in project_root.rglob("*.py"):
        # Skip ComfyUI submodule and cache directories
        if "ComfyUI/" not in str(file_path) and "__pycache__" not in str(file_path):
            python_files.append(file_path)
    
    print(f"Found {len(python_files)} Python files to process")
    print("=" * 50)
    
    for file_path in python_files:
        process_file(file_path)
    
    print("=" * 50)
    print("✅ Translation complete!")

if __name__ == "__main__":
    main()
