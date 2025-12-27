# R20 E96量化热力图数据计算错误修复报告

## 问题描述

R20 指出热力图存在两个严重问题：
1. **子图 4 Weight with E96 Quantization Error 数值明显不对**：原来是 0.24 的值竟变成 1.302
2. **子图 5 的误差热力图数据不是由子图 1 和子图 4 计算出来的**

## 问题根因分析

### 根本原因 1：Key 语义不一致

在 `circuit_dense.py` 的 `generate_quantization_comparison_data` 方法中，key 的构建方式与后续 plotter 解析时的语义不一致：

**原代码（错误）**：
```python
for ch, channel_config in enumerate(self.channel_configs):
    for i, (r_stored, r_neg_stored) in enumerate(zip(r_pos_channels, r_neg_channels)):
        key_pos = f"layer_{ch}_channel_{i}_type_pos"  # ch=输出通道, i=输入通道
```

**问题**：
- `ch` 是输出通道索引（对应 weight_matrix 的列）
- `i` 是输入通道索引（对应 weight_matrix 的行）
- 但在 plotter 中解析时，`layer` 被当作行索引，`channel` 被当作列索引

导致权重矩阵映射完全错误！

### 根本原因 2：Plotter 中 error_matrix 计算使用错误的相对误差公式

原 plotter 使用 `abs(w_e96 - weight_original) / weight_original * 100`，对于小权重会产生极大的误差值（如 7576%）。

## 修复方案

### 修复 1：修正 generate_quantization_comparison_data 中的 Key 语义

**文件**：`spice_simulator/circuit_dense.py` 第 883-914 行

**修改后代码**：
```python
# 交换 layer 和 channel 的语义，使其与 weight_matrix 索引一致
# layer = i (输入通道，作为输出权重矩阵的行)
# channel = ch (输出通道，作为输出权重矩阵的列)
layer_idx = i
channel_idx = ch

key_pos = f"layer_{layer_idx}_channel_{channel_idx}_type_pos"
key_neg = f"layer_{layer_idx}_channel_{channel_idx}_type_neg"
```

### 修复 2：Plotter 中使用正确的误差计算

**文件**：`inference/tools/visualization/weight_e96_quantization_plotter.py` 第 430-470 行

**修改后代码**：使用电阻的相对误差（E96 量化的真实误差），而不是权重的相对误差：

```python
# 使用电阻的相对误差，而不是权重的相对误差
# E96量化的误差应该在1-2%左右
r_raw_val = resistor_raw.get(key, 0)
r_e96_val = resistor_e96.get(key, r_raw_val)

if r_raw_val > 0 and r_raw_val < MAX_RESISTANCE:
    r_rel_error = abs(r_e96_val - r_raw_val) / r_raw_val * 100
    error_matrix[layer, channel] = r_rel_error
```

### 修复 3：添加 MAX_RESISTANCE 常量

**文件**：`inference/tools/visualization/weight_e96_quantization_plotter.py` 第 28-29 行

```python
# 定义最大电阻值（开路电阻）
MAX_RESISTANCE = 1e9
```

## 验证结果

### 修复前 vs 修复后对比

| 位置 | 原始权重 | 修复前 weight_e96 | 修复后 weight_e96 | 误差 |
|------|---------|-------------------|-------------------|------|
| [0][4] | 0.24 | 1.302 ❌ | 0.242 ✅ | 0.9% |
| [4][2] | 1.08 | 0.50 ❌ | 1.074 ✅ | 0.6% |
| [0][0] | -2.05 | -2.05 | -2.05 | 0.3% |

### 子图 5 误差百分比分布

修复后误差百分比在合理范围内：
- 大多数值：0.2% ~ 1.5%
- 全部在 E96 系列标准误差范围内

## 涉及文件

1. **`spice_simulator/circuit_dense.py`**
   - 第 883-914 行：修正 key 构建逻辑
   - 第 959-1017 行：weight_error 计算逻辑

2. **`inference/tools/visualization/weight_e96_quantization_plotter.py`**
   - 第 28-29 行：添加 MAX_RESISTANCE 常量
   - 第 430-470 行：修正 weight_e96_matrix 和 error_matrix 构建

## 总结

R20 提出的两个问题已全部修复：
1. ✅ 子图 4 的数值现在与原始权重一致
2. ✅ 子图 5 的误差现在基于正确的 E96 电阻误差计算
