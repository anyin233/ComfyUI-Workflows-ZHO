# ComfyUI 工作流转换器

这个工具可以将 ComfyUI 工作流转换为使用 diffusers、transformers 等标准 Python 库的脚本。

## 功能特性

- 支持多种模型类型：
  - FLUX.1 (SCHNELL/DEV)
  - Stable Diffusion 3
  - Stable Diffusion XL
  - Stable Cascade
  - 标准 Stable Diffusion
- 自动识别工作流类型并生成相应的 diffusers 代码
- 批量转换支持
- 生成可独立运行的 Python 脚本

## 支持的节点类型

### 基础加载器
- `CheckpointLoaderSimple` - 模型检查点加载
- `DualCLIPLoader` - FLUX 双 CLIP 加载器
- `VAELoader` - VAE 加载器
- `UNETLoader` - UNET 加载器
- `LoraLoader` - LoRA 适配器加载

### 文本编码
- `CLIPTextEncode` - 标准文本编码
- `CLIPTextEncodeFlux` - FLUX 文本编码

### 采样和生成
- `KSampler` - K采样器
- `KSamplerAdvanced` - 高级K采样器
- `SamplerCustomAdvanced` - 自定义高级采样器
- `BasicScheduler` - 基础调度器
- `BasicGuider` - 基础引导器

### 图像处理
- `VAEDecode/VAEEncode` - VAE 编解码
- `EmptyLatentImage` - 空潜在图像
- `LatentUpscale` - 潜在空间放大

### 图像输出
- `SaveImage` - 保存图像
- `PreviewImage` - 预览图像

### 特殊节点
- `PortraitMaster_中文版` - 肖像大师
- `workflow/FLUX` - FLUX 工作流节点
- `workflow/SD3` - SD3 工作流节点

## 使用方法

### 转换单个工作流
```bash
python convert.py -i "workflows/zho/FLUX.1 SCHNELL 1.0.json" -o flux_script.py
```

### 转换指定目录中的所有工作流
```bash
python convert.py -i workflows/zho -o converted_scripts
```

### 转换仓库中的所有工作流
```bash
python convert.py --all
```

## 生成的脚本结构

转换后的脚本包含以下部分：

1. **导入和设备配置** - 自动检测 GPU/CPU 并配置数据类型
2. **模型设置** - 根据工作流类型加载相应的 diffusers pipeline
3. **参数配置** - 提取原始工作流中的参数设置
4. **图像生成** - 使用配置的参数生成图像
5. **保存输出** - 保存生成的图像

## 依赖要求

转换后的脚本需要以下依赖：

```bash
pip install torch diffusers transformers PIL numpy requests
```

对于特定模型类型：
- **FLUX**: `pip install diffusers[flux]`
- **SD3**: `pip install diffusers[sd3]`
- **SDXL**: `pip install diffusers[sdxl]`

## 注意事项

1. **模型下载**: 首次运行生成的脚本时，会自动下载相应的模型，可能需要较长时间
2. **GPU内存**: 某些模型（如 FLUX、SD3）需要大量 GPU 内存
3. **未支持节点**: 部分特殊节点（如 3D 生成、视频处理）会被标记为不支持，需要手动处理
4. **自定义节点**: 第三方自定义节点可能无法完全转换

## 扩展开发

要添加对新节点类型的支持：

1. 在 `node_mappings` 字典中添加映射
2. 实现对应的转换方法
3. 按照现有模式处理节点的 `widgets_values` 和 `inputs`

## 示例输出

转换后的 FLUX 脚本示例：

```python
#!/usr/bin/env python3
from diffusers import FluxPipeline
import torch

# Device configuration
device = 'cuda' if torch.cuda.is_available() else 'cpu'
dtype = torch.float16 if device == 'cuda' else torch.float32

# Load FLUX pipeline
pipe = FluxPipeline.from_pretrained(
    'black-forest-labs/FLUX.1-schnell',
    torch_dtype=dtype,
).to(device)

# Set parameters
prompt = "your prompt here"
width = 1024
height = 1024

# Generate image
with torch.no_grad():
    result = pipe(
        prompt=prompt,
        width=width,
        height=height,
        num_inference_steps=20,
        guidance_scale=7.5,
    )
    image = result.images[0]
    image.save('generated_image.png')
```

## 故障排除

如果遇到问题：

1. 检查 JSON 工作流文件格式是否正确
2. 确保有足够的 GPU 内存
3. 检查网络连接（用于模型下载）
4. 查看控制台输出中的错误信息
