# ComfyUI Workflow Custom Node Searcher

This is a powerful Python toolkit for automatically analyzing custom nodes used in ComfyUI workflow files and providing download links and installation guides.

## 🚀 Main Features

### Single Workflow Analysis
- 📄 **Smart Workflow Parsing**: Supports standard ComfyUI JSON format and complex groupNodes structures
- 🔍 **Automatic Node Recognition**: Dynamically loads the latest built-in node list from ComfyUI submodule
- 🌐 **Multi-source Node Search**: Integrates local database, ComfyUI Manager, and GitHub API
- 📋 **Detailed Installation Guide**: Provides multiple installation methods and specific commands

### Batch Workflow Analysis
- 📁 **Batch Processing**: Analyzes all workflow files in a directory at once
- 📊 **Usage Statistics**: Statistics on usage frequency and distribution of each custom node
- 🔄 **Recursive Search**: Supports searching workflow files in subdirectories
- 📈 **Comprehensive Report**: Generates summary reports containing all workflow information

### Smart Features
- ⚡ **Performance Optimization**: Uses Pixi to manage dependencies, ensuring environment consistency
- 🎯 **Precise Matching**: Intelligently distinguishes between built-in and custom nodes
- 🔄 **Incremental Updates**: Supports maintenance and extension of local node database
- 🌍 **Multi-language Support**: Supports English interface and documentation

## 🛠 Installation and Configuration

### Requirements
- Python 3.8+
- ComfyUI (as submodule)
- Pixi (recommended) or pip

### Quick Start

1. **Clone Repository**:
```bash
git clone <repository-url>
cd ComfyUI-Workflows-ZHO
```

2. **Install Dependencies**:
```bash
# Using Pixi (recommended)
pixi install

# Or using pip
pip install -r requirements.txt
```

3. **Ensure ComfyUI Submodule is Available**:
```bash
git submodule update --init --recursive
```

## 📖 Usage Guide

### Single Workflow Analysis

```bash
# Basic usage
pixi run python comfyui_node_searcher.py "workflows/example.json"

# Custom output file
pixi run python comfyui_node_searcher.py "workflows/example.json" -o "custom_report.md"

# Show results only, don't save file
pixi run python comfyui_node_searcher.py "workflows/example.json" --no-save

# Specify ComfyUI path
pixi run python comfyui_node_searcher.py "workflows/example.json" --comfyui-path "/path/to/ComfyUI"
```

### Batch Workflow Analysis

```bash
# Analyze entire directory
pixi run python batch_node_searcher.py "workflows/"

# Analyze current directory only (non-recursive)
pixi run python batch_node_searcher.py "workflows/" --no-recursive

# Fast analysis (don't search download links)
pixi run python batch_node_searcher.py "workflows/" --no-search

# Custom report output
pixi run python batch_node_searcher.py "workflows/" -o "batch_analysis.md"
```

## 📁 Project Structure

```
ComfyUI-Workflows-ZHO/
├── comfyui_node_searcher.py      # Single workflow analyzer
├── batch_node_searcher.py        # Batch workflow analyzer
├── node_database.json            # Local node database
├── pixi.toml                     # Pixi configuration file
├── requirements.txt              # Python dependencies
├── README_NODE_SEARCHER.md       # Detailed usage documentation
├── ComfyUI/                      # ComfyUI submodule
├── workflows/                    # Example workflow files
│   └── zho/                      # ZHO series workflows
├── converted_scripts/            # Converted scripts
└── docs/                         # Documentation directory
```

## 📊 Analysis Result Examples

### Single Workflow Analysis Result

```markdown
# ComfyUI Custom Node Search Report

📊 Found 16 node types
🔧 Found 4 custom nodes:
  - ConcatText_Zho
  - ArtistsImage_Zho
  - MovementsImage_Zho
  - StylesImage_Zho

## 🎯 Found Nodes

### ConcatText_Zho
- 🔗 Source Link: https://github.com/AIGODLIKE/ComfyUI-ZHO
- 📝 Description: ZHO series nodes, including artist, style, movement and other image library nodes
- 💾 Install Command: `git clone https://github.com/AIGODLIKE/ComfyUI-ZHO.git`
```

### Batch Analysis Result

```markdown
# ComfyUI Workflow Batch Node Analysis Report

Number of workflows analyzed: 17
Total custom nodes found: 60

## 📊 Node Usage Statistics
| Node Name | Usage Count | Used in Workflows |
|-----------|-------------|-------------------|
| `StableCascade_EmptyLatentImage` | 5 | Stable Cascade... |
| `TripleCLIPLoader` | 4 | SD3 series workflows |
| `BasicScheduler` | 4 | FLUX, HUNYUAN etc. |
```

## 🔧 Configuration and Extension

### Node Database Configuration

Edit the `node_database.json` file to add new node information:

```json
{
  "known_custom_nodes": {
    "new-node-pack": {
      "title": "New Node Pack",
      "github_url": "https://github.com/user/repo",
      "install_url": "https://github.com/user/repo.git",
      "description": "Node pack description",
      "nodes": ["NodeType1", "NodeType2"]
    }
  }
}
```

### Supported Search Sources

1. **Local Database**: Known node information maintained in `node_database.json`
2. **ComfyUI Manager**: Official node manager's online database
3. **GitHub API**: Search relevant repositories by keywords

## 🎯 Practical Use Cases

### Workflow Migration
When you need to run existing workflows in a new environment, use this tool to:
- Quickly identify required custom nodes
- Get accurate download links
- Generate installation checklists

### Node Package Management
For node package developers:
- Analyze which nodes are most popular
- Understand node usage patterns
- Optimize node package functionality

### Community Collaboration
- Provide node installation guides when sharing workflows
- Establish standardized node documentation
- Promote ComfyUI ecosystem development

## 💡 Best Practices

1. **Regularly Update Node Database**:
   - Update ComfyUI submodule to get latest built-in nodes
   - Maintain accuracy of local node database

2. **Use Batch Analysis**:
   - Use batch analysis functionality for large projects
   - Generate project-level node dependency reports

3. **Version Control**:
   - Add generated reports to version control
   - Track changes in project dependencies

## 🔍 Troubleshooting

### Common Issues

**Q: What to do if node search results are inaccurate?**
A: Check and update `node_database.json`, or manually verify search results

**Q: Batch analysis too slow?**
A: Use `--no-search` option for fast analysis, or check network connection

**Q: ComfyUI path recognition error?**
A: Use `--comfyui-path` parameter to specify the correct path

### Debugging Tips

1. Use `--no-save` to view real-time output
2. Check if ComfyUI submodule is correctly initialized
3. Verify the correctness of workflow JSON file format

## 🤝 Contribution Guide

Contributions welcome:

1. **Node Database Updates**: Add new node package information
2. **Feature Improvements**: Optimize search algorithms or report formats
3. **Documentation Enhancement**: Improve usage instructions or add examples
4. **Bug Fixes**: Report or fix discovered issues

## 📄 License

This project is open source under the MIT License, see LICENSE file for details.

---

🎨 **Making ComfyUI workflow sharing easier!**
