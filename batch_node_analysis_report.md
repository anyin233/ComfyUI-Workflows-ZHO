# ComfyUI 工作流批量节点分析报告

分析时间: 2025-07-08 16:17:08
分析的工作流数量: 17
发现的自定义节点总数: 60

## 📊 节点使用统计

| 节点名称 | 使用次数 | 使用的工作流 |
|---------|---------|-------------|
| `StableCascade_EmptyLatentImage` | 5 | Stable Cascade Canny ControlNet.json, Stable Cascade ImagePrompt Mix.json, Stable Cascade Inpainting ControlNet.json 等5个 |
| `StableCascade_StageB_Conditioning` | 5 | Stable Cascade Canny ControlNet.json, Stable Cascade ImagePrompt Mix.json, Stable Cascade Inpainting ControlNet.json 等5个 |
| `TripleCLIPLoader` | 4 | SD3是否内置文本编码器的对比.json, SD3 BASE 1.0.json, SD3 Medium + Qwen2 .json 等4个 |
| `EmptySD3LatentImage` | 4 | SD3是否内置文本编码器的对比.json, SD3 BASE 1.0.json, SD3 Medium + Qwen2 .json 等4个 |
| `BasicScheduler` | 4 | HUNYUAN VIDEO 1.0 .json, CosXL Edit + ArtGallery 1.0.json, FLUX.1 SCHNELL 1.0.json 等4个 |
| `SamplerCustomAdvanced` | 4 | HUNYUAN VIDEO 1.0 .json, CosXL Edit + ArtGallery 1.0.json, FLUX.1 SCHNELL 1.0.json 等4个 |
| `KSamplerSelect` | 4 | HUNYUAN VIDEO 1.0 .json, CosXL Edit + ArtGallery 1.0.json, FLUX.1 SCHNELL 1.0.json 等4个 |
| `RandomNoise` | 4 | HUNYUAN VIDEO 1.0 .json, CosXL Edit + ArtGallery 1.0.json, FLUX.1 SCHNELL 1.0.json 等4个 |
| `BasicGuider` | 3 | HUNYUAN VIDEO 1.0 .json, FLUX.1 SCHNELL 1.0.json, FLUX.1 DEV 1.0.json |
| `VHS_VideoCombine` | 2 | LivePortrait Animals 1.0.json, HUNYUAN VIDEO 1.0 .json |
| `PrimitiveNode` | 2 | SD3 BASE 1.0.json, CosXL Edit + ArtGallery 1.0.json |
| `ModelSamplingSD3` | 2 | SD3 BASE 1.0.json, HUNYUAN VIDEO 1.0 .json |
| `Reroute` | 2 | CosXL Edit + ArtGallery 1.0.json, Stable Cascade Inpainting ControlNet.json |
| `workflow/FLUX` | 2 | FLUX.1 SCHNELL 1.0.json, FLUX.1 DEV 1.0.json |
| `BRIA_RMBG_Zho` | 2 | CRM Comfy 3D.json, Sketch to 3D.json |
| `BRIA_RMBG_ModelLoader_Zho` | 2 | CRM Comfy 3D.json, Sketch to 3D.json |
| `LivePortraitLoadFaceAlignmentCropper` | 1 | LivePortrait Animals 1.0.json |
| `DownloadAndLoadLivePortraitModels` | 1 | LivePortrait Animals 1.0.json |
| `LivePortraitCropper` | 1 | LivePortrait Animals 1.0.json |
| `LivePortraitComposite` | 1 | LivePortrait Animals 1.0.json |
| `VHS_LoadVideo` | 1 | LivePortrait Animals 1.0.json |
| `LivePortraitProcess` | 1 | LivePortrait Animals 1.0.json |
| `CannyEdgePreprocessor` | 1 | Stable Cascade Canny ControlNet.json |
| `AIO_Preprocessor` | 1 | Stable Cascade Canny ControlNet.json |
| `workflow>HUNYUAN` | 1 | HUNYUAN VIDEO 1.0 .json |
| `EmptyHunyuanLatentVideo` | 1 | HUNYUAN VIDEO 1.0 .json |
| `FluxGuidance` | 1 | HUNYUAN VIDEO 1.0 .json |
| `Any Switch (rgthree)` | 1 | CosXL Edit + ArtGallery 1.0.json |
| `StylesImage_Zho` | 1 | CosXL Edit + ArtGallery 1.0.json |
| `Fast Bypasser (rgthree)` | 1 | CosXL Edit + ArtGallery 1.0.json |
| `ArtistsImage_Zho` | 1 | CosXL Edit + ArtGallery 1.0.json |
| `MovementsImage_Zho` | 1 | CosXL Edit + ArtGallery 1.0.json |
| `DualCFGGuider` | 1 | CosXL Edit + ArtGallery 1.0.json |
| `ConcatText_Zho` | 1 | CosXL Edit + ArtGallery 1.0.json |
| `InstructPixToPixConditioning` | 1 | CosXL Edit + ArtGallery 1.0.json |
| `[Comfy3D] CRM Images MVDiffusion Model` | 1 | CRM Comfy 3D.json |
| `[Comfy3D] Save 3D Mesh` | 1 | CRM Comfy 3D.json |
| `[Comfy3D] Preview 3DMesh` | 1 | CRM Comfy 3D.json |
| `[Comfy3D] Load CRM MVDiffusion Model` | 1 | CRM Comfy 3D.json |
| `[Comfy3D] Load Convolutional Reconstruction Model` | 1 | CRM Comfy 3D.json |
| `SplitImageWithAlpha` | 1 | CRM Comfy 3D.json |
| `[Comfy3D] Convolutional Reconstruction Model` | 1 | CRM Comfy 3D.json |
| `[Comfy3D] CRM CCMs MVDiffusion Model` | 1 | CRM Comfy 3D.json |
| `[Comfy3D] Switch Mesh Axis` | 1 | CRM Comfy 3D.json |
| `ImageCompositeMasked` | 1 | Stable Cascade Inpainting ControlNet.json |
| `GrowMask` | 1 | Stable Cascade Inpainting ControlNet.json |
| `JoinImageWithAlpha` | 1 | Stable Cascade Inpainting ControlNet.json |
| `workflow/StableCascadeInpaintCnet` | 1 | Stable Cascade Inpainting ControlNet.json |
| `InvertMask` | 1 | Stable Cascade Inpainting ControlNet.json |
| `ThresholdMask` | 1 | Stable Cascade Inpainting ControlNet.json |
| `StableCascade_StageC_VAEEncode` | 1 | Stable Cascade Img2Img.json |
| `DisplayText_Zho` | 1 | SD3 Medium + Qwen2 .json |
| `Qwen2_ModelLoader_Zho` | 1 | SD3 Medium + Qwen2 .json |
| `Qwen2_Zho` | 1 | SD3 Medium + Qwen2 .json |
| `PortraitMaster_中文版` | 1 | SD3 Medium + 肖像大师（中文版）.json |
| `TripoSRSampler_Zho` | 1 | Sketch to 3D.json |
| `SaveTripoSR_Zho` | 1 | Sketch to 3D.json |
| `ModelSamplingContinuousEDM` | 1 | Sketch to 3D.json |
| `PainterNode` | 1 | Sketch to 3D.json |
| `TripoSRModelLoader_Zho` | 1 | Sketch to 3D.json |

## 📁 工作流详情

### SD3是否内置文本编码器的对比.json

- 总节点数: 9
- 自定义节点数: 2
- 自定义节点列表:
  - `TripleCLIPLoader`
  - `EmptySD3LatentImage`

### LivePortrait Animals 1.0.json

- 总节点数: 10
- 自定义节点数: 7
- 自定义节点列表:
  - `LivePortraitLoadFaceAlignmentCropper`
  - `DownloadAndLoadLivePortraitModels`
  - `LivePortraitCropper`
  - `VHS_VideoCombine`
  - `LivePortraitComposite`
  - `VHS_LoadVideo`
  - `LivePortraitProcess`

### SD3 BASE 1.0.json

- 总节点数: 12
- 自定义节点数: 4
- 自定义节点列表:
  - `PrimitiveNode`
  - `TripleCLIPLoader`
  - `ModelSamplingSD3`
  - `EmptySD3LatentImage`

### Stable Cascade Canny ControlNet.json

- 总节点数: 12
- 自定义节点数: 4
- 自定义节点列表:
  - `StableCascade_EmptyLatentImage`
  - `CannyEdgePreprocessor`
  - `StableCascade_StageB_Conditioning`
  - `AIO_Preprocessor`

### Stable Cascade ImagePrompt Mix.json

- 总节点数: 11
- 自定义节点数: 2
- 自定义节点列表:
  - `StableCascade_EmptyLatentImage`
  - `StableCascade_StageB_Conditioning`

### HUNYUAN VIDEO 1.0 .json

- 总节点数: 15
- 自定义节点数: 10
- 自定义节点列表:
  - `VHS_VideoCombine`
  - `BasicScheduler`
  - `workflow>HUNYUAN`
  - `ModelSamplingSD3`
  - `SamplerCustomAdvanced`
  - `EmptyHunyuanLatentVideo`
  - `BasicGuider`
  - `KSamplerSelect`
  - `RandomNoise`
  - `FluxGuidance`

### CosXL Edit + ArtGallery 1.0.json

- 总节点数: 19
- 自定义节点数: 14
- 自定义节点列表:
  - `Any Switch (rgthree)`
  - `Reroute`
  - `StylesImage_Zho`
  - `BasicScheduler`
  - `Fast Bypasser (rgthree)`
  - `ArtistsImage_Zho`
  - `MovementsImage_Zho`
  - `SamplerCustomAdvanced`
  - `DualCFGGuider`
  - `PrimitiveNode`
  - `KSamplerSelect`
  - `ConcatText_Zho`
  - `InstructPixToPixConditioning`
  - `RandomNoise`

### FLUX.1 SCHNELL 1.0.json

- 总节点数: 13
- 自定义节点数: 6
- 自定义节点列表:
  - `BasicScheduler`
  - `workflow/FLUX`
  - `SamplerCustomAdvanced`
  - `BasicGuider`
  - `KSamplerSelect`
  - `RandomNoise`

### CRM Comfy 3D.json

- 总节点数: 13
- 自定义节点数: 11
- 自定义节点列表:
  - `BRIA_RMBG_Zho`
  - `[Comfy3D] CRM Images MVDiffusion Model`
  - `[Comfy3D] Save 3D Mesh`
  - `[Comfy3D] Preview 3DMesh`
  - `[Comfy3D] Load CRM MVDiffusion Model`
  - `[Comfy3D] Load Convolutional Reconstruction Model`
  - `SplitImageWithAlpha`
  - `[Comfy3D] Convolutional Reconstruction Model`
  - `BRIA_RMBG_ModelLoader_Zho`
  - `[Comfy3D] CRM CCMs MVDiffusion Model`
  - `[Comfy3D] Switch Mesh Axis`

### FLUX.1 DEV 1.0.json

- 总节点数: 13
- 自定义节点数: 6
- 自定义节点列表:
  - `BasicScheduler`
  - `workflow/FLUX`
  - `SamplerCustomAdvanced`
  - `BasicGuider`
  - `KSamplerSelect`
  - `RandomNoise`

### Stable Cascade Inpainting ControlNet.json

- 总节点数: 18
- 自定义节点数: 9
- 自定义节点列表:
  - `Reroute`
  - `ImageCompositeMasked`
  - `GrowMask`
  - `JoinImageWithAlpha`
  - `StableCascade_StageB_Conditioning`
  - `workflow/StableCascadeInpaintCnet`
  - `InvertMask`
  - `ThresholdMask`
  - `StableCascade_EmptyLatentImage`

### Stable Cascade Img2Img.json

- 总节点数: 9
- 自定义节点数: 3
- 自定义节点列表:
  - `StableCascade_EmptyLatentImage`
  - `StableCascade_StageC_VAEEncode`
  - `StableCascade_StageB_Conditioning`

### SD3 Medium + Qwen2 .json

- 总节点数: 12
- 自定义节点数: 5
- 自定义节点列表:
  - `TripleCLIPLoader`
  - `EmptySD3LatentImage`
  - `DisplayText_Zho`
  - `Qwen2_ModelLoader_Zho`
  - `Qwen2_Zho`

### Stable Cascade ImagePrompt Standard.json

- 总节点数: 11
- 自定义节点数: 2
- 自定义节点列表:
  - `StableCascade_EmptyLatentImage`
  - `StableCascade_StageB_Conditioning`

### SD3 Medium + 肖像大师（中文版）.json

- 总节点数: 8
- 自定义节点数: 3
- 自定义节点列表:
  - `TripleCLIPLoader`
  - `EmptySD3LatentImage`
  - `PortraitMaster_中文版`

### Sketch to 3D.json

- 总节点数: 15
- 自定义节点数: 7
- 自定义节点列表:
  - `BRIA_RMBG_Zho`
  - `TripoSRSampler_Zho`
  - `SaveTripoSR_Zho`
  - `ModelSamplingContinuousEDM`
  - `PainterNode`
  - `BRIA_RMBG_ModelLoader_Zho`
  - `TripoSRModelLoader_Zho`

### SDXS-512-0.9.json

- 总节点数: 8
- 自定义节点数: 0

## 📦 安装指南

### 方法1: ComfyUI Manager (推荐)
1. 安装 ComfyUI Manager
2. 在 ComfyUI 界面中点击 'Manager' 按钮
3. 搜索并安装对应的节点包

### 方法2: 手动安装
1. 进入 ComfyUI/custom_nodes 目录
2. 运行 git clone 命令克隆节点仓库
3. 重启 ComfyUI
