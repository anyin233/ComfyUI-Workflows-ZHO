# ComfyUI 工作流节点搜索器使用指南

## 功能特点

- 🔍 **自动分析工作流**：从 JSON 文件中提取节点信息
- 📚 **智能节点识别**：从 ComfyUI 子模块自动加载内置节点列表
- 🌐 **多源搜索**：集成 ComfyUI Manager 数据库和 GitHub 搜索
- 📝 **详细报告**：生成包含下载链接和安装命令的 Markdown 报告
- 🛠 **Pixi 支持**：使用 pixi 管理 Python 依赖

## 安装依赖

使用 pixi 安装依赖（推荐）：
```bash
pixi install
```

或使用 pip：
```bash
pip install requests
```

## 使用方法

### 基本用法

```bash
# 使用 pixi 运行（推荐）
pixi run python comfyui_node_searcher.py "workflows/zho/CosXL Edit + ArtGallery 1.0.json"

# 或直接使用 python
python3 comfyui_node_searcher.py "workflows/zho/CosXL Edit + ArtGallery 1.0.json"
```

### 命令行选项

```bash
# 显示帮助
python3 comfyui_node_searcher.py --help

# 指定输出文件
python3 comfyui_node_searcher.py "workflow.json" -o "my_report.md"

# 不保存文件，直接显示结果
python3 comfyui_node_searcher.py "workflow.json" --no-save

# 指定 ComfyUI 路径（如果不在默认位置）
python3 comfyui_node_searcher.py "workflow.json" --comfyui-path "/path/to/ComfyUI"
```

## 示例输出

脚本会生成如下格式的报告：

```markdown
# ComfyUI 自定义节点搜索报告

搜索时间: 2024-12-08 16:10:08
总共搜索节点数: 4
找到的节点: 4
未找到的节点: 0

## 🎯 找到的节点

### ConcatText_Zho

**选项 1:**
- 🔗 源码链接: https://github.com/AIGODLIKE/ComfyUI-ZHO
- 📝 描述: ZHO 系列节点，包含艺术家、风格、运动等图片库节点
- 💾 安装命令: `git clone https://github.com/AIGODLIKE/ComfyUI-ZHO.git`

## 📦 安装指南

### 方法1: ComfyUI Manager (推荐)
1. 安装 ComfyUI Manager
2. 在 ComfyUI 界面中点击 'Manager' 按钮
3. 搜索并安装对应的节点包

### 方法2: 手动安装
1. 进入 ComfyUI/custom_nodes 目录
2. 运行 git clone 命令克隆节点仓库
3. 重启 ComfyUI
```

## 工作原理

1. **节点提取**：解析工作流 JSON 文件，提取所有节点类型
2. **内置节点识别**：从 ComfyUI/nodes.py 中自动提取 NODE_CLASS_MAPPINGS
3. **自定义节点识别**：通过对比找出非内置的自定义节点
4. **多源搜索**：
   - 本地数据库搜索（node_database.json）
   - ComfyUI Manager 官方数据库
   - GitHub API 搜索
5. **报告生成**：整理搜索结果并生成 Markdown 报告

## 支持的工作流格式

- ✅ 标准 ComfyUI 工作流 JSON 文件
- ✅ 包含 groupNodes 的复杂工作流
- ✅ 从 ComfyUI 官方界面导出的工作流

## 配置文件

### node_database.json

该文件包含常见自定义节点的信息，可以手动编辑以添加新的节点信息：

```json
{
  "known_custom_nodes": {
    "节点包名": {
      "title": "显示名称",
      "github_url": "GitHub 链接",
      "install_url": "安装链接",
      "description": "描述",
      "nodes": ["节点1", "节点2"]
    }
  }
}
```

## 常见问题

### Q: 为什么某些节点没有找到？
A: 可能的原因：
- 节点名称不匹配
- 节点是非常新的或很少使用的
- 节点可能已经被废弃

### Q: 如何添加新的节点信息？
A: 编辑 `node_database.json` 文件，添加节点信息

### Q: 脚本运行太慢怎么办？
A: 脚本会调用多个 API，可能受网络影响。可以使用 `--no-save` 选项减少文件操作

## 贡献

欢迎提交 PR 来：
- 完善内置节点列表
- 添加更多已知自定义节点信息
- 改进搜索算法
- 优化报告格式
