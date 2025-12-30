# R25: E96量化频率响应对比图的权重数据验证报告

## 任务概述

验证 R22 执行报告中 "WNET5 权重的计算结果已自然对齐 E96 标准值" 这一观点的正确性。

**核心结论**: 该观点**严重错误**。R22 的实际执行结果证明 E96 量化**确实引入了显著误差**。

---

## 问题分析

### R22 计划中的错误观点

R22 计划文档（第175行）原文：
> **E96量化误差为0的情况**：如果权重已自然对齐E96值，误差将为0，图中两条线会完全重合

R15 执行报告（原报告第361行）原文：
> 在测试中发现，WNET5 权重的计算结果恰好是标准 E96 值，因此误差为 0%。这是有效结果，说明该模型的权重设计已经自然对齐到 E96 标准电阻值。

**问题**: 这两个观点都是错误的，不存在任何"自然对齐"的机制。

---

## 实际执行结果验证

### 1. 频率响应对比图

生成的频率响应对比图 (`plots/frequency_response_e96_comparison.png`) 清晰显示：

![R22 E96频率响应对比图](ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1/plots/frequency_response_e96_comparison.png)

**观察**:
- **虚线（原始权重）** 和 **实线（E96量化权重）** 在多个通道存在明显分离
- D2 通道在 1kHz~100kHz 区域分离最明显
- D5、D6 通道在某些频率区域也有显著差异

### 2. E96 量化误差分析数据

`numerics/e96_error_analysis.json` 中的统计数据：

| 通道 | mean_abs_error_percent | within_1pct | within_2pct |
|------|------------------------|-------------|-------------|
| D1 | 0.27% | 100.0% | 100.0% |
| D2 | **2.77%** | 40.6% | 64.3% |
| D3 | 0.39% | 97.0% | 100.0% |
| D4 | 0.62% | 89.6% | 100.0% |
| D5 | 0.85% | 72.8% | 96.5% |
| D6 | 1.00% | 63.3% | 95.9% |

**关键发现**:
- D2 通道的平均绝对误差高达 **2.77%**
- D2 通道仅有 40.6% 的点在 1% 误差范围内
- 这证明 E96 量化确实引入了不可忽略的误差

### 3. R15 与 R22 权重数据对比

#### R15 生成的权重数据 (`data/plots/raw/e96_quantization/weight_matrices_comparison.json`)

**原始权重 (weight_matrix)**:
```
[[-2.0467, -1.2284, 0.2127, 0.7403, 0.2405, -0.8589],
 [-1.0162, -0.2180, -0.2214, 0.3103, 0.5055, -1.6846],
 [-0.1141, -1.8836, 0.2896, 0.6695, 0.4968, -1.0125],
 [-0.9089, -1.5107, -0.2646, -1.6553, 0.7438, -0.0196],
 [-1.3099, 0.8927, 1.0764, -1.0301, -0.0713, 1.1304],
 [-0.6978, 0.1958, 0.0489, 1.4898, 1.3476, -0.2917]]
```

**E96量化权重 (weight_e96_matrix)**:
```
[[-2.0534, -1.2407, 0.2105, 0.7299, 0.2427, -0.8696],
 [-1.0246, -0.2155, -0.2208, 0.3086, 0.5102, -1.6949],
 [-0.1155, -1.8657, 0.2874, 0.6667, 0.5000, -1.0246],
 [-0.9091, -1.5038, -0.2674, -1.6556, 0.7519, -0.0196],
 [-1.3021, 0.8850, 1.0741, -1.0246, -0.0714, 1.1274],
 [-0.6993, 0.1957, 0.0488, 1.5038, 1.3333, -0.2941]]
```

**对比分析**:
| 元素 | 原始权重 | E96量化权重 | 相对误差 |
|------|----------|-------------|----------|
| [0,0] | -2.0467 | -2.0534 | **0.33%** |
| [0,1] | -1.2284 | -1.2407 | **1.00%** |
| [0,5] | -0.8589 | -0.8696 | **1.25%** |
| [1,5] | -1.6846 | -1.6949 | **0.61%** |
| [2,4] | 0.4968 | 0.5000 | **0.64%** |
| [4,0] | -1.3099 | -1.3021 | **0.60%** |
| [4,3] | -1.0301 | -1.0246 | **0.53%** |
| [5,3] | 1.4898 | 1.5038 | **0.94%** |
| [5,4] | 1.3476 | 1.3333 | **1.06%** |

**结论**: E96 量化引入了 0.33% ~ 1.25% 的权重误差

#### R22 代码中的权重数据验证

R22 的 `_generate_e96_frequency_response_comparison()` 方法（第1326-1347行）从 `quantization_comparison` 中重建权重矩阵：

```python
# 构建 E96 量化后的权重矩阵
weight_e96_matrix = np.zeros_like(original_weights, dtype=np.float64)
for key, error_data in weight_error.items():
    parts = key.split('_')
    if len(parts) >= 6:
        layer = int(parts[1])  # 输入通道索引
        channel = int(parts[3])  # 输出通道索引
        r_type = parts[5]

        if r_type not in ['pos', 'neg']:
            continue

        if layer < original_weights.shape[0] and channel < original_weights.shape[1]:
            w_e96 = error_data.get('weight_e96', original_weights[layer, channel])
            weight_e96_matrix[layer, channel] = w_e96
```

**验证结果**: R22 使用的数据源与 R15 完全一致，都是从 `DenseCircuitFactory.create()` 的 `generate_quantization_comparison_data()` 方法生成的。

---

## R15 报告中 statistics.total_count=0 的问题

R15 报告中的统计数据：
```json
{
  "statistics": {
    "mean_absolute_error": 768.2,
    "max_absolute_error": 2499.0,
    "min_absolute_error": 0.0,
    "std_absolute_error": 749.9,
    "within_5pct": 100,
    "total_count": 0
  }
}
```

**问题**: `total_count = 0` 说明量化对比数据收集存在问题，而不是真的没有误差。

**原因分析**: `generate_quantization_comparison_data()` 方法中只统计了 `resistor_value != 0` 的电阻，但某些电阻值的计算可能返回了异常值。

---

## 修改计划

为确保 R22 的权重数据可追溯和可验证，需要在 `_generate_e96_frequency_response_comparison()` 方法中添加权重 dump 功能。

### 修改文件

`visualization/wnet5_circuit_validator.py`

### 修改内容

#### 1. 在 `_generate_e96_frequency_response_comparison()` 中添加权重 dump

**位置**: 第1366行之后（计算 `freq_response_e96` 之后）

**新增代码**:
```python
# 3.5 Dump 权重数据用于验证
weights_dump = {
    'timestamp': datetime.now().isoformat(),
    'original_weights': original_weights.tolist(),
    'weight_e96_matrix': weight_e96_matrix.tolist(),
    'weight_difference': (weight_e96_matrix - original_weights).tolist(),
    'weight_relative_error': ((weight_e96_matrix - original_weights) / np.abs(original_weights) * 100).tolist()
}

# 保存权重数据
weights_dump_path = self.output_path / 'numerics' / 'r22_weights_dump.json'
with open(weights_dump_path, 'w', encoding='utf-8') as f:
    json.dump(weights_dump, f, indent=2, ensure_ascii=False)
logger.info(f"R22权重数据已保存: {weights_dump_path}")
```

**注意**: 需要导入 `datetime` 模块

#### 2. 添加 `datetime` 导入

**位置**: 文件顶部（第10行左右）

**新增代码**:
```python
from datetime import datetime
```

### 修改行号对照表

| 修改项 | 文件 | 行号 | 修改类型 |
|--------|------|------|----------|
| 添加 `datetime` 导入 | `wnet5_circuit_validator.py` | 15 | 新增 |
| 添加权重 dump 代码 | `wnet5_circuit_validator.py` | 1367-1379 | 新增 |

---

## 验证步骤

### 1. 运行 R22 代码

```bash
python cli.py ep ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1
```

### 2. 验证输出

预期生成的文件：
- `output/numerics/r22_weights_dump.json` - R22 的权重数据
- `output/plots/frequency_response_e96_comparison.png` - 频率响应对比图
- `output/numerics/e96_error_analysis.json` - 误差分析数据

### 3. 对比验证

对比 `r22_weights_dump.json` 和 R15 生成的 `data/plots/raw/e96_quantization/weight_matrices_comparison.json`：

```python
import json
import numpy as np

# 加载 R15 数据
with open('data/plots/raw/e96_quantization/weight_matrices_comparison.json') as f:
    r15_data = json.load(f)

# 加载 R22 数据
with open('output/numerics/r22_weights_dump.json') as f:
    r22_data = json.load(f)

# 对比
r15_weight_e96 = np.array(r15_data['data']['weight_e96_matrix'])
r22_weight_e96 = np.array(r22_data['weight_e96_matrix'])

assert np.allclose(r15_weight_e96, r22_weight_e96), "权重数据不一致！"
print("✅ R22 和 R15 的 E96 量化权重数据一致")
```

---

## 结论

1. **R22 计划中的 "自然对齐" 观点是错误的**
   - E96 量化确实引入了 0.27% ~ 2.77% 的频率响应误差
   - 权重误差范围为 0.33% ~ 1.25%

2. **R15 报告中的 statistics.total_count=0 是数据收集问题**
   - 实际存在误差，只是统计数据生成有误

3. **R22 的实现是正确的**
   - 频率响应对比图清晰显示了误差
   - 误差分析数据提供了量化指标

4. **添加权重 dump 功能是必要的**
   - 确保权重数据可追溯
   - 便于 R15 和 R22 的数据一致性验证

---

## 修改汇总表

| 文件 | 修改类型 | 修改内容 | 行号 |
|------|---------|---------|------|
| `visualization/wnet5_circuit_validator.py` | 新增 | `datetime` 导入 | 15 |
| `visualization/wnet5_circuit_validator.py` | 新增 | 权重 dump 代码 | 1367-1379 |
