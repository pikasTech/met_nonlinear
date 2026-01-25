# WNET5_EFF2_A1_PS-5_360-01 项目

## 项目概述

本项目基于 **WNET5_EFF2_A1_PS-5_360** 的轻量化版本，将 **kernal_units 从 6 降至 4**，以减少模型参数量。

## 核心特性

### 1. 轻量化模型架构 (基于EFF2_A1)
- **模型类型**: WaveNet5 (EFF2_A1 最优变种，轻量化版)
- **网络层数**: 4层
- **通道数**: 每层 4 个通道 (原版 6 个)
- **中心频率**: [8, 50, 85, 180] Hz (4频段，原版 6频段)
- **品质因数**: [1.5, 2.5, 3.0, 5.0] (4值，原版 6值)
- **后处理**: 14个隐藏单元，3层密集层
- **密集偏置**: 启用

### 2. 参数量对比

| 指标 | 原版 (6频段) | 轻量化版 (4频段) | 减少比例 |
|------|-------------|-----------------|----------|
| DIAGIIR 参数 | 7,776 | 5,184 | 33.3% |
| 总参数量 | 8,477 | 5,885 | 30.6% |
| 可训练参数 | 701 | 701 | 不变 |

### 3. 偏置补偿
- **启用状态**: 是
- **优化层级**: 4层全覆盖
- **偏置值数量**: 每层 4 个 (原版 6 个)

### 4. 训练参数
- **学习率**: 0.02
- **训练轮次**: 40000
- **学习率衰减**: 每 1000 步自动衰减
- **特征预测**: 启用
- **数据集类型**: Alias
- **数据集路径**: data/ALIA_PS5-360-20250904
- **目标扫描**: 0
- **频率范围**: 160-200Hz
- **目标反相**: 启用

### 5. 硬件配置
- **检波器**: PS-5/360
- **频率范围**: 160-200Hz（专用频段）
- **电源**: ±8V
- **运放**: 理想模型

## 快速开始

### 运行推理
```bash
conda run -n tf26 python cli.py --project projects/WNET5_EFF2_A1_PS-5_360-01/config.json
```

### 查看结果
推理结果将保存在 `inference/results/` 目录中。

## 配置说明

### 轻量化模型配置
```json
"kernal_units": 4,
"model_subcfg": {
  "init_center_freqs": [8, 50, 85, 180],
  "init_quality_factors": [1.5, 2.5, 3.0, 5.0],
  "post_dense": true,
  "post_dense_activation": "relu",
  "post_dense_units": 14,
  "post_dense_layers": 3,
  "use_dense_bias": true
}
```

### 偏置补偿参数
```json
"bias_compensation": {
  "enabled": true,
  "layer_bias_adjustments": {
    "1": [0.005323, 0.002278, 0.005201, 0.014258],
    "2": [0.002181, 0.001301, 0.000932, 0.007533],
    "3": [0.007174, 0.000358, -0.001310, -0.003717],
    "4": [0.000025, 0.002515, 0.000025, 0.000025]
  }
}
```

## 目录结构

```
WNET5_EFF2_A1_PS-5_360-01/
├── config.json              # 项目配置文件
├── README.md                # 项目说明文档
├── data/                    # 数据目录
│   ├── scalers/             # 标准化器
│   ├── best.weights.h5
│   ├── best_val.weights.h5
│   ├── fast_best.weights.h5
│   ├── fast_best_val.weights.h5
│   ├── model_info.json
│   ├── training_info.json
│   ├── training_state.json
│   ├── training_log.jsonl
│   ├── linear_response.json
│   └── initial_iir_channels_frequency_response.png
└── inference/               # 推理目录
    ├── data/                # 推理数据
    └── results/             # 推理结果
```

## 技术细节

### WaveNet5 架构 (轻量化版)
- **输入层**: 频率响应特征 (Alias 数据集)
- **隐藏层**: 4 层 WaveNet 结构，4 个核单元 (原版 6 个)
- **中心频率**: 4 个优化频率点 [8, 50, 85, 180] Hz
- **品质因数**: [1.5, 2.5, 3.0, 5.0]
- **后处理**: 14 个隐藏单元密集层，3 层，ReLU 激活
- **密集偏置**: 启用

### 频段选择策略
| 决策 | 频率 | 说明 |
|------|------|------|
| 保留 | 8 Hz | 检波器响应关键低频 |
| 保留 | 50 Hz | 覆盖原 25+50 Hz 区间 |
| 保留 | 85 Hz | 中高频响应 |
| 保留 | 180 Hz | 高频响应 |
| 移除 | 25 Hz | 与 8 Hz 过近 |
| 移除 | 120 Hz | 与 85 Hz 过近 |

## 版本历史

- **v1.0** (2025-12-26): 轻量化版本，kernal_units 从 6 降至 4，参数量减少 30.6%
  - 修改自 WNET5_EFF2_A1_PS-5_360
  - `kernal_units`: 6 → 4
  - `init_center_freqs`: [8, 25, 50, 85, 120, 180] → [8, 50, 85, 180]
  - `init_quality_factors`: [1.5, 2.0, 2.5, 3.0, 4.0, 5.0] → [1.5, 2.5, 3.0, 5.0]
  - `layer_bias_adjustments`: 每层 6 值 → 4 值

## 相关文档

- [原版项目](../WNET5_EFF2_A1_PS-5_360/README.md) - WNET5_EFF2_A1_PS-5_360
- [config.json](config.json) - 详细配置参数
