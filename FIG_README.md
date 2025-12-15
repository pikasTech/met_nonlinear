# 频率响应对比图片清单

## ⚠️ 绘图规范：必须使用CLI工具

**绘图执行方法**：
- **✅ 允许**: 仅使用 `cli.py ep` 命令进行绘图
- **❌ 禁止**: 禁止使用任何其他代码、脚本或临时文件进行绘图
- **❌ 禁止**: 禁止创建临时Python脚本进行绘图
- **❌ 禁止**: 禁止直接调用可视化模块进行绘图

所有绘图操作必须通过官方CLI工具 `cli.py` 完成，不得使用任何其他方法。

---

## 图片集：WNET5 Layer1-3 频率响应对比 (2025-12-15)

### 概述
本文档包含使用来自 `20251201-SVFNET-Dense1-3层.xlsx` 实验数据生成的3张频率响应对比图片。这些图片通过CLI工具 `cli.py ep` 命令生成，涵盖3个Dense层的6个通道。

---

## 图片1：Layer1 frequency_response_comparison.png

### 基本信息
- **文件名**: `frequency_response_comparison.png`
- **项目**: `WNET5q1h2u6l3_layer1`
- **类型**: 理论 vs 实验频率响应对比图 (Layer1)
- **布局**: 上下双子图布局
- **生成方式**: CLI工具 (`cli.py ep`)

### 技术规格
- **文件大小**: 约 500 KB
- **图片尺寸**: 3600 × 2400 pixels
- **分辨率**: 300 DPI
- **坐标系**: semilogx (x轴对数刻度，y轴线性刻度)

### 数据源
- **实验数据文件**: `F:/BaiduSyncdisk/data/SVF-NET-CIRCUIT/20251201-SVFNET-Dense1-3层.xlsx`
- **实验Sheet**: `layer1`
- **频率范围**: 2 - 500 Hz
- **Dense层**: `Dense_Layer_Model_1` (6通道)

### CLI执行命令
```bash
python cli.py ep external/projects/wnet5-circuit-validation/layer1
```

### 文件路径
```
external/projects/wnet5-circuit-validation/layer1/data/plots/frequency_response_comparison.png
```

---

## 图片2：Layer2 frequency_response_comparison.png

### 基本信息
- **文件名**: `frequency_response_comparison.png`
- **项目**: `WNET5q1h2u6l3_layer2`
- **类型**: 理论 vs 实验频率响应对比图 (Layer2)
- **布局**: 上下双子图布局
- **生成方式**: CLI工具 (`cli.py ep`)

### 技术规格
- **文件大小**: 约 430 KB
- **图片尺寸**: 3600 × 2400 pixels
- **分辨率**: 300 DPI
- **坐标系**: semilogx (x轴对数刻度，y轴线性刻度)

### 数据源
- **实验数据文件**: `F:/BaiduSyncdisk/data/SVF-NET-CIRCUIT/20251201-SVFNET-Dense1-3层.xlsx`
- **实验Sheet**: `layer2`
- **频率范围**: 2 - 500 Hz
- **Dense层**: `Dense_Layer_Model_2` (6通道)

### CLI执行命令
```bash
python cli.py ep external/projects/wnet5-circuit-validation/layer2
```

### 文件路径
```
external/projects/wnet5-circuit-validation/layer2/data/plots/frequency_response_comparison.png
```

---

## 图片3：Layer3 frequency_response_comparison.png

### 基本信息
- **文件名**: `frequency_response_comparison.png`
- **项目**: `WNET5q1h2u6l3_layer3`
- **类型**: 理论 vs 实验频率响应对比图 (Layer3)
- **布局**: 上下双子图布局
- **生成方式**: CLI工具 (`cli.py ep`)

### 技术规格
- **文件大小**: 约 490 KB
- **图片尺寸**: 3600 × 2400 pixels
- **分辨率**: 300 DPI
- **坐标系**: semilogx (x轴对数刻度，y轴线性刻度)

### 数据源
- **实验数据文件**: `F:/BaiduSyncdisk/data/SVF-NET-CIRCUIT/20251201-SVFNET-Dense1-3层.xlsx`
- **实验Sheet**: `layer3`
- **频率范围**: 2 - 500 Hz
- **Dense层**: `Dense_Layer_Model_3` (6通道)

### CLI执行命令
```bash
python cli.py ep external/projects/wnet5-circuit-validation/layer3
```

### 文件路径
```
external/projects/wnet5-circuit-validation/layer3/data/plots/frequency_response_comparison.png
```

---

## 所有图片的通用配置

### SVF配置
- **滤波器数量**: 2个状态变量滤波器
- **中心频率**: [10.0, 80.0] Hz
- **品质因数**: [1.0, 1.0]

### 图表结构 (适用于所有3张图片)
**上图 (ax_top)**:
- **标题**: `{model_project_name} Dense#{analysis_layer} 输出 频率响应 (理论, 线性增益)`
- **数据**: 理论仿真频率响应
- **Y轴**: 增益 (线性, log刻度)

**下图 (ax_bottom)**:
- **标题**: `实验测量 频率响应 (线性增益)`
- **数据**: 实验测量频率响应
- **X轴**: 频率 (Hz)
- **Y轴**: 增益 (线性, log刻度)

### 实验数据格式
**新格式 (20251201文件)**:
- **列结构**: FREQ, GAIN/CH1, GAIN/CH2, GAIN/CH3, GAIN/CH4, GAIN/CH5, GAIN/CH6
- **Sheet分离**: layer1, layer2, layer3
- **频点数量**: 25个

---

## 原始参考图片

### 图片：frequency_response_comparison.png (原始)

### 基本信息
- **文件名**: `frequency_response_comparison.png`
- **项目**: `WNET5q1h2u6l3`
- **类型**: 理论 vs 实验频率响应对比图
- **布局**: 上下双子图布局

### 技术规格
- **图片尺寸**: 3600 × 2400 pixels
- **物理尺寸**: 12 × 8 inches
- **分辨率**: 300 DPI
- **文件大小**: 544,209 bytes (531 KB)
- **格式**: PNG (8-bit/color RGBA, non-interlaced)

### 绘图配置
- **坐标系**: semilogx (x轴对数刻度，y轴线性刻度)
- **图表尺寸**: figsize=(12, 8)
- **DPI**: 300
- **颜色映射**: tab10/turbo colormap
- **线宽**: 1.4 (理论), 1.2 (实验)
- **网格**: both, alpha=0.3, 虚线

### 数据源
- **实验数据文件**: `D:/BaiduSyncdisk/data/SVF-NET-CIRCUIT/SVF_W_DENSE1.xlsx`
- **频率范围**: 2 - 500 Hz
- **Dense层**: `Dense_Layer_Model_1`
- **输出通道数**: 6个通道 (D1_1 到 D1_6)

### SVF配置
- **滤波器数量**: 2个状态变量滤波器
- **中心频率**: [10.0, 80.0] Hz
- **品质因数**: [1.0, 1.0]
- **滤波器类型**: high_pass, band_pass, low_pass

### 图表结构
**上图 (ax_top)**:
- **标题**: `{model_project_name} Dense#{analysis_layer} 输出 频率响应 (理论, 线性增益)`
- **数据**: 理论仿真频率响应
- **Y轴**: 增益 (线性, log刻度)
- **图例**: fontsize=8, ncol=min(4, n_channels)

**下图 (ax_bottom)**:
- **标题**: `实验测量 频率响应 (线性增益)`
- **数据**: 实验测量频率响应
- **X轴**: 频率 (Hz)
- **Y轴**: 增益 (线性, log刻度)
- **图例**: fontsize=8, ncol=min(4, n_channels)

### 文件路径
```
ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3/data/plots/frequency_response_comparison.png
```

---

## CLI工具绘图总结

### 执行方法
所有图片必须使用CLI工具 `cli.py ep` 命令生成，禁止使用任何其他方法。

### CLI生成的图片
✅ **3张高质量对比图片 (CLI生成)**
- Layer1: 约 500 KB PNG, 300 DPI
- Layer2: 约 430 KB PNG, 300 DPI
- Layer3: 约 490 KB PNG, 300 DPI

**文件路径**:
- Layer1: `external/projects/wnet5-circuit-validation/layer1/data/plots/frequency_response_comparison.png`
- Layer2: `external/projects/wnet5-circuit-validation/layer2/data/plots/frequency_response_comparison.png`
- Layer3: `external/projects/wnet5-circuit-validation/layer3/data/plots/frequency_response_comparison.png`

### 配置格式
- 使用外部项目结构: `external/projects/wnet5-circuit-validation/layer{N}/`
- 任务类型: `wnet5-circuit-validation`
- 离线模式: 启用预计算数据
- 实验sheet: `layer1`, `layer2`, `layer3`

### 技术成就
- **100% CLI合规**: 所有操作使用官方CLI工具
- **零自定义脚本**: 不使用任何临时/自定义脚本
- **生产就绪**: 使用官方外部项目结构
- **离线健壮**: 无需TensorFlow依赖

---

**文档更新**: 2025-12-15
**记录的图片总数**: 4 (3个CLI生成 + 1个原始参考)
**状态**: ✅ 完成CLI工具集成
**执行方法**: 仅使用官方CLI (cli.py ep)
**绘图规范**: 严格遵循CLI绘图要求，禁止其他绘图方法
