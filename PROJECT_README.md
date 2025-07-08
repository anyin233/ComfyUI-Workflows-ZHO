# 🎨 ComfyUI Workflow Custom Node Searcher

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-compatible-orange.svg)](https://github.com/comfyanonymous/ComfyUI)

## 📋 Overview

This is an intelligent tool developed specifically for the ComfyUI community that automatically analyzes custom nodes used in workflow files and provides detailed download links and installation guides. Whether you're a ComfyUI beginner or an experienced user, this tool helps you quickly configure your working environment.

### ✨ Core Features

🔍 **Smart Node Recognition** - Dynamically loads the latest built-in node list from ComfyUI submodule, accurately identifying custom nodes

🌐 **Multi-source Node Search** - Integrates local database, ComfyUI Manager official database, and GitHub API

📊 **Batch Workflow Analysis** - Analyzes entire directories at once, generating detailed node usage statistics

📋 **Detailed Installation Guide** - Provides multiple installation methods and specific commands, including ComfyUI Manager and manual installation

⚡ **High-performance Dependency Management** - Uses Pixi to ensure environment consistency and rapid deployment

🎯 **User-friendly Interface** - Supports command-line arguments and interactive operations, suitable for users of different technical levels

## 🚀 Quick Start

### Environment Setup

```bash
# Clone repository (including ComfyUI submodule)
git clone --recursive <repository-url>
cd ComfyUI-Workflows-ZHO

# Install dependencies (Pixi recommended)
pixi install

# Or use traditional method
pip install -r requirements.txt
```

### Basic Usage

```bash
# 🎯 Analyze single workflow (recommended for beginners)
pixi run python quick_start.py "workflows/example.json"

# 📁 Batch analyze workflow directory
pixi run python quick_start.py "workflows/" --batch

# 🔧 Professional command line
pixi run python comfyui_node_searcher.py "workflows/example.json"
pixi run python batch_node_searcher.py "workflows/"
```

## 📖 Use Cases

### 🔄 Workflow Migration
```bash
# Analyze workflows that need migration
python comfyui_node_searcher.py "legacy_workflow.json" -o "migration_guide.md"
```

### 📊 Project Dependency Management
```bash
# Generate node dependency report for all project workflows
python batch_node_searcher.py "project_workflows/" -o "project_dependencies.md"
```

### 🌍 Community Sharing
```bash
# Generate installation guide for shared workflows
python comfyui_node_searcher.py "my_awesome_workflow.json" -o "installation_guide.md"
```

## 📊 Example Output

### Single Workflow Analysis
```
📄 Analyzing workflow file: CosXL Edit + ArtGallery 1.0.json
📊 Found 19 node types
🔧 Found 14 custom nodes:
  - ConcatText_Zho
  - ArtistsImage_Zho
  - Any Switch (rgthree)
  - Fast Bypasser (rgthree)
  
✅ Report saved to: node_search_report.md
```

### Batch Analysis Statistics
```
📁 Found 17 workflow files
📊 Total 60 different custom nodes discovered

| Node Name | Usage Count | Used in Workflows |
|-----------|-------------|-------------------|
| StableCascade_EmptyLatentImage | 5 | Stable Cascade series |
| TripleCLIPLoader | 4 | SD3 series workflows |
| BasicScheduler | 4 | FLUX, HUNYUAN etc. |
```

## 🛠 Advanced Features

### 🎛 Command Line Options

```bash
# Single file analysis
python comfyui_node_searcher.py [file] [options]
  -o, --output          Custom output filename
  --no-save            Don't save report file
  --comfyui-path       Specify ComfyUI path

# Batch analysis
python batch_node_searcher.py [directory] [options]
  --no-recursive       Don't search subdirectories recursively
  --no-search          Fast analysis mode (don't search download links)
  -o, --output         Custom report filename
```

### 📁 Project Structure

```
ComfyUI-Workflows-ZHO/
├── 🐍 comfyui_node_searcher.py      # Single file analyzer
├── 📦 batch_node_searcher.py        # Batch analyzer
├── 🚀 quick_start.py                # Quick start interface
├── 🗄️ node_database.json            # Local node database
├── ⚙️ pixi.toml                     # Pixi configuration
├── 📋 requirements.txt              # Python dependencies
├── 📁 ComfyUI/                      # ComfyUI submodule
├── 📄 workflows/                    # Example workflows
└── 📚 docs/                         # Detailed documentation
```

### 🔧 Node Database Maintenance

Edit `node_database.json` to add new node information:

```json
{
  "known_custom_nodes": {
    "your-awesome-nodes": {
      "title": "Your Awesome Node Pack",
      "github_url": "https://github.com/you/awesome-nodes",
      "install_url": "https://github.com/you/awesome-nodes.git",
      "description": "Node collection with awesome features",
      "nodes": ["AwesomeNode1", "AwesomeNode2"]
    }
  }
}
```

## 📈 Performance Optimization

### ⚡ Fast Mode
```bash
# Skip online search, use local database only
python batch_node_searcher.py "workflows/" --no-search
```

### 🎯 Precise Search
```bash
# Specify ComfyUI path for most accurate built-in node list
python comfyui_node_searcher.py "workflow.json" --comfyui-path "/path/to/ComfyUI"
```

## 🔍 Troubleshooting

### Frequently Asked Questions

**Q: Node recognition inaccurate?**
```bash
# Ensure ComfyUI submodule is up to date
git submodule update --remote
```

**Q: Search too slow?**
```bash
# Use fast mode
python batch_node_searcher.py "workflows/" --no-search
```

**Q: Some nodes not found?**
- Check and update `node_database.json`
- Nodes might be private or deprecated
- Manually verify node name spelling

### 🐛 Debugging Tips

1. **Real-time output**: Use `--no-save` parameter
2. **Check paths**: Confirm ComfyUI submodule path is correct
3. **Verify format**: Ensure workflow JSON format is correct

## 🤝 Community Contributions

We welcome all forms of contributions:

### 📚 Node Database
- Add new node pack information
- Update existing node descriptions and links
- Supplement node usage instructions

### 🔧 Feature Improvements
- Optimize search algorithms
- Improve report formats
- Enhance user interface

### 📖 Documentation
- Improve usage instructions
- Add usage examples
- Translate to other languages

### 🐛 Issue Reports
- Report discovered bugs
- Suggest new features
- Share usage experiences

## 📝 Changelog

### v1.0.0 (Current Version)
- ✅ Complete node search functionality
- ✅ Batch workflow analysis
- ✅ ComfyUI submodule integration
- ✅ Pixi dependency management
- ✅ Multi-language interface support
- ✅ Detailed installation guides

## 📄 License

This project is open source under the MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

Thanks to the following projects and communities:

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - Powerful Stable Diffusion GUI
- [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager) - Node manager
- [ComfyUI Community](https://github.com/comfyanonymous/ComfyUI/discussions) - Active user community

---

### 🌟 If this tool helps you, please give us a Star!

[![GitHub stars](https://img.shields.io/github/stars/your-username/ComfyUI-Workflows-ZHO.svg?style=social&label=Star)](https://github.com/your-username/ComfyUI-Workflows-ZHO)

**Making ComfyUI workflow sharing easier!** 🎨✨
