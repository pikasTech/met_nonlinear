# External Projects (EP) 索引文档

本文档提供了所有外部项目 (External Projects, EP) 的完整索引，按任务类型分组。

## 📊 概览统计

- **总计**: 19 个外部项目
- **任务类型**: 3 种
- **主要类别**: 可视化、推理、电路验证

---

## 🎯 任务类型索引

### 1. freq-response-compare (频率响应对比)
**项目数量**: 10 个

频率响应对比任务主要用于分析和可视化不同配置下的电路频率响应特性，支持补偿前后对比、不同参数配置对比等。

#### 项目列表

| 项目名称 | 配置路径 | 描述 |
|---------|----------|------|
| LSTMu32al_rs300_ex2 | `ex_projects/visualization/freq-response-compare/LSTMu32al_rs300_ex2/config.json` | LSTMu32al 基础对比实验 |
| LSTMu32al_rs300_PS-5 | `ex_projects/visualization/freq-response-compare/LSTMu32al_rs300_PS-5/config.json` | LSTMu32al PS-5 配置对比 |
| LSTMu32al_rs300_PS-5_160-200Hz | `ex_projects/visualization/freq-response-compare/LSTMu32al_rs300_PS-5_160-200Hz/config.json` | 160-200Hz 频率范围对比 |
| LSTMu32al_rs300_PS-5_160-200Hz_inverse | `ex_projects/visualization/freq-response-compare/LSTMu32al_rs300_PS-5_160-200Hz_inverse/config.json` | 160-200Hz 逆目标对比 |
| LSTMu32al_rs300_PS-5_160-200Hz_inverse_ex2 | `ex_projects/visualization/freq-response-compare/LSTMu32al_rs300_PS-5_160-200Hz_inverse_ex2/config.json` | 160-200Hz 逆目标实验2 |
| LSTMu32al_rs300_PS-5_50-300Hz_inverse_ex3 | `ex_projects/visualization/freq-response-compare/LSTMu32al_rs300_PS-5_50-300Hz_inverse_ex3/config.json` | 50-300Hz 逆目标实验3 |
| LSTMu32al_rs300_PS-5_50-300Hz_inverse_ex3_vs_ex4 | `ex_projects/visualization/freq-response-compare/LSTMu32al_rs300_PS-5_50-300Hz_inverse_ex3_vs_ex4/config.json` | 实验3 vs 实验4 对比 |
| LSTMu32al_rs300_PS-5_50-300Hz_inverse_ex4 | `ex_projects/visualization/freq-response-compare/LSTMu32al_rs300_PS-5_50-300Hz_inverse_ex4/config.json` | 50-300Hz 逆目标实验4 |
| PS-5-190_vs_PS-5-360 | `ex_projects/visualization/freq-response-compare/PS-5-190_vs_PS-5-360/config.json` | PS-5-190 与 PS-5-360 对比 |
| WNET5_EFF2_A1_PS-5_360 | `ex_projects/visualization/freq-response-compare/WNET5_EFF2_A1_PS-5_360/config.json` | WNET5 EFF2 A1 PS-5_360 对比 |

#### 使用方法

```bash
# 运行频率响应对比
python cli.py ep "ex_projects/visualization/freq-response-compare/{项目名称}"
```

例如:
```bash
python cli.py ep "ex_projects/visualization/freq-response-compare/WNET5q1h2u6l3_PS-5_360"
```

---

### 2. wnet5-circuit-validation (WNET5 电路验证)
**项目数量**: 8 个

WNET5 电路验证任务主要用于神经网络模型的 SPICE 电路仿真验证，支持分层验证和整体验证。

#### 项目列表

| 项目名称 | 配置路径 | 描述 |
|---------|----------|------|
| WNET5q1h2u6l3 | `ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3/config.json` | WNET5q1h2u6l3 整体验证 |
| WNET5q1h2u6l3_layer1 | `ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1/config.json` | 第1层验证 |
| WNET5q1h2u6l3_layer2 | `ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer2/config.json` | 第2层验证 |
| WNET5q1h2u6l3_layer3 | `ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer3/config.json` | 第3层验证 |
| WNET5q1h2u6l3_layer4 | `ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer4/config.json` | 第4层验证 |
| layer1 | `ex_projects/wnet5-circuit-validation/layer1/config.json` | 通用第1层验证 |
| layer2 | `ex_projects/wnet5-circuit-validation/layer2/config.json` | 通用第2层验证 |
| layer3 | `ex_projects/wnet5-circuit-validation/layer3/config.json` | 通用第3层验证 |

#### 使用方法

```bash
# 运行电路验证
python cli.py ep "ex_projects/inference/wnet5-circuit-validation/{项目名称}"
```

例如:
```bash
python cli.py ep "ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3"
```

---

### 3. freq-response-compensator (频率响应补偿器)
**项目数量**: 1 个

频率响应补偿器任务用于生成补偿器的频率响应可视化。

#### 项目列表

| 项目名称 | 配置路径 | 描述 |
|---------|----------|------|
| WNET5q1h2u6l3 | `ex_projects/visualization/freq-response-compensator/WNET5q1h2u6l3/config.json` | WNET5q1h2u6l3 补偿器可视化 |

#### 使用方法

```bash
# 运行补偿器可视化
python cli.py ep "ex_projects/visualization/freq-response-compensator/WNET5q1h2u6l3"
```

---

## 📁 目录结构

```
ex_projects/
├── inference/
│   └── wnet5-circuit-validation/          # 推理验证类 EP
│       ├── WNET5q1h2u6l3/
│       ├── WNET5q1h2u6l3_layer1/
│       ├── WNET5q1h2u6l3_layer2/
│       ├── WNET5q1h2u6l3_layer3/
│       └── WNET5q1h2u6l3_layer4/
├── visualization/
│   ├── freq-response-compare/             # 频率响应对比 EP
│   │   ├── LSTMu32al_rs300_ex2/
│   │   ├── LSTMu32al_rs300_PS-5/
│   │   ├── LSTMu32al_rs300_PS-5_160-200Hz/
│   │   ├── LSTMu32al_rs300_PS-5_160-200Hz_inverse/
│   │   ├── LSTMu32al_rs300_PS-5_160-200Hz_inverse_ex2/
│   │   ├── LSTMu32al_rs300_PS-5_50-300Hz_inverse_ex3/
│   │   ├── LSTMu32al_rs300_PS-5_50-300Hz_inverse_ex3_vs_ex4/
│   │   ├── LSTMu32al_rs300_PS-5_50-300Hz_inverse_ex4/
│   │   ├── PS-5-190_vs_PS-5-360/
│   │   ├── WNET5_EFF2_A1_PS-5_360/
│   │   └── WNET5q1h2u6l3_PS-5_360/
│   └── freq-response-compensator/         # 补偿器 EP
│       └── WNET5q1h2u6l3/
└── wnet5-circuit-validation/              # 通用电路验证 EP
    ├── layer1/
    ├── layer2/
    └── layer3/
```

---

## 🔧 通用运行命令

所有 EP 项目都可以使用以下命令格式运行：

```bash
python cli.py ep "{EP项目路径}"
```

### 路径格式说明

- **完整路径格式**: `category/task-type/project-name`
- **简化路径格式**: `project-name` (当任务类型明确时)

### 示例

```bash
# 频率响应对比
python cli.py ep "ex_projects/visualization/freq-response-compare/WNET5q1h2u6l3_PS-5_360"

# 电路验证
python cli.py ep "ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3"

# 补偿器
python cli.py ep "ex_projects/visualization/freq-response-compensator/WNET5q1h2u6l3"
```

---

## 📝 配置文件说明

每个 EP 项目包含以下文件：

- `config.json`: 主要配置文件，包含任务类型和参数
- `data/`: 输出数据目录
  - `task_metadata.json`: 任务元数据
  - `*.png`: 生成的图表文件

### 配置文件结构示例

```json
{
  "task_info": {
    "task_type": "freq-response-compare"
  },
  "visualization_config": {
    "layout": "side_by_side",
    "freq_range": [160, 200],
    "output_format": "png",
    "dpi": 300,
    "figsize": [12, 8],
    "title": "项目标题"
  },
  "data_sources": [
    {
      "project": "项目名",
      "state": "origin|compensation",
      "label": "显示标签"
    }
  ]
}
```

---

## 🎯 任务类型详细说明

### freq-response-compare
- **用途**: 对比不同配置下的频率响应
- **输入**: 线性响应 JSON 数据
- **输出**: 频率响应对比图 (Bode 图)
- **参数**: 频率范围、布局方式、图表尺寸等

### wnet5-circuit-validation
- **用途**: 验证神经网络模型的 SPICE 电路实现
- **输入**: 训练好的模型权重
- **输出**: 电路仿真结果和验证报告
- **参数**: 层配置、验证模式等

### freq-response-compensator
- **用途**: 生成补偿器的频率响应可视化
- **输入**: 补偿器参数配置
- **输出**: 补偿器频率响应图
- **参数**: 补偿器类型、频率范围等

---

## 📅 更新日志

- **2025-12-15**: 创建 EP_README.md 索引文档
- **总计**: 维护 19 个外部项目配置

---

## 🚀 快速开始

1. **选择项目**: 根据需求选择合适的任务类型和项目
2. **运行命令**: 使用 `python cli.py ep` 命令运行
3. **查看结果**: 在 `data/` 目录中查看生成的文件
4. **查看日志**: 检查 `logs/` 目录中的执行日志

---

## 📞 支持

如需添加新的外部项目或修改现有配置，请参考本文档的结构和格式。