# R1: WNET5 SVF通道自适应适配调查

## 问题概述

### 现象描述
执行 WNET5 电路验证时，出现通道数不匹配错误：

```
[ERROR 3.34s] WNET5电路验证分析失败: 权重输入通道数 14 与SVF展开通道数 18 不匹配
```

### 期望功能
当 SVF 通道数与权重输入通道数不匹配时：
1. **自动裁剪**: SVF 通道 > 权重通道时，裁剪多余的 SVF 通道
2. **循环拓展**: SVF 通道 < 权重通道时，循环使用已有 SVF 通道数据（如 4→6 变为 1,2,3,4,1,2）
3. **警告提示**: 不匹配发生时，输出警告日志告知用户

---

## 当前代码分析

### 关键代码位置
文件: `visualization/wnet5_circuit_validator.py`

方法: `_calculate_combined_transfer_functions` (第750-773行)

### 当前实现逻辑

```python
def _calculate_combined_transfer_functions(self, svf_tfs, dense_weights):
    """计算SVF+Dense组合传递函数"""
    logger.info("计算组合传递函数...")
    import sympy as sp

    # 展开所有SVF通道 (顺序: 每个滤波器 HP,BP,LP)
    all_svf_channels = []
    for svf in svf_tfs:
        all_svf_channels.extend([svf['high_pass'], svf['band_pass'], svf['low_pass']])

    n_inputs = len(all_svf_channels)
    w = dense_weights['weights']  # (in_ch, out_ch)
    if w.shape[0] != n_inputs:
        raise ValueError(f"权重输入通道数 {w.shape[0]} 与SVF展开通道数 {n_inputs} 不匹配")

    bias_vec = dense_weights['bias']
    out_ch = w.shape[1]
    combined = []
    for o in range(out_ch):
        Hc = bias_vec[o]
        for i, H_svf in enumerate(all_svf_channels):
            Hc += w[i, o] * H_svf
        combined.append(Hc)
    return combined
```

### 通道计算公式
- SVF 滤波器数量 = `len(svf_params['center_freqs'])`
- SVF 展开通道数 = SVF滤波器数量 × 3 (每个滤波器有 HP, BP, LP 三个输出)
- 权重输入通道数 = `dense_weights['weights'].shape[0]`

### 问题场景

| 场景 | SVF滤波器数 | SVF展开通道 | 权重输入通道 | 结果 |
|------|------------|-------------|-------------|------|
| 正常 | 6 | 18 | 18 | 正常 |
| 案例A | 6 | 18 | 14 | **当前报错** |
| 案例B | 4 | 12 | 18 | **当前报错** |

---

## 修改方案设计

### 新增辅助方法

```python
def _adapt_svf_channels(self, all_svf_channels: list, target_channels: int) -> tuple[list, str]:
    """自适应调整SVF通道数以匹配目标通道数

    Args:
        all_svf_channels: 原始SVF通道列表 (SymPy表达式)
        target_channels: 目标通道数 (权重输入通道数)

    Returns:
        tuple: (调整后的通道列表, 操作描述字符串)

    Raises:
        ValueError: 如果目标通道数 <= 0
    """
    current_channels = len(all_svf_channels)

    if current_channels == target_channels:
        return all_svf_channels, "通道数匹配，无需调整"

    if target_channels <= 0:
        raise ValueError(f"目标通道数必须 > 0，实际: {target_channels}")

    adapted_channels = []

    if current_channels > target_channels:
        # 裁剪模式：SVF通道 > 权重通道
        adapted_channels = all_svf_channels[:target_channels]
        operation = "裁剪"
    else:
        # 循环拓展模式：SVF通道 < 权重通道
        for i in range(target_channels):
            adapted_channels.append(all_svf_channels[i % current_channels])
        operation = "循环拓展"

    return adapted_channels, operation
```

### 修改现有方法

```python
def _calculate_combined_transfer_functions(self, svf_tfs, dense_weights):
    """计算SVF+Dense组合传递函数（支持通道自适应）"""
    logger.info("计算组合传递函数...")
    import sympy as sp

    # 展开所有SVF通道 (顺序: 每个滤波器 HP,BP,LP)
    all_svf_channels = []
    for svf in svf_tfs:
        all_svf_channels.extend([svf['high_pass'], svf['band_pass'], svf['low_pass']])

    n_inputs = len(all_svf_channels)
    w = dense_weights['weights']  # (in_ch, out_ch)
    target_channels = w.shape[0]

    # 通道自适应适配
    if n_inputs != target_channels:
        # 调用自适应方法
        adapted_channels, operation = self._adapt_svf_channels(all_svf_channels, target_channels)
        logger.warning(
            f"⚠️ SVF通道数 ({n_inputs}) 与权重输入通道数 ({target_channels}) 不匹配，"
            f"已{operation}适配"
        )
        logger.warning(f"   原始SVF通道: {n_inputs} -> 适配后: {len(adapted_channels)}")
        all_svf_channels = adapted_channels
        n_inputs = len(all_svf_channels)

    # 验证适配后是否匹配
    if n_inputs != target_channels:
        raise ValueError(
            f"通道适配失败: SVF通道适配后为 {n_inputs}，但权重需要 {target_channels} 通道"
        )

    bias_vec = dense_weights['bias']
    out_ch = w.shape[1]
    combined = []
    for o in range(out_ch):
        Hc = bias_vec[o]
        for i, H_svf in enumerate(all_svf_channels):
            Hc += w[i, o] * H_svf
        combined.append(Hc)
    return combined
```

---

## 修改计划

### 文件修改清单
| 文件 | 修改类型 | 说明 |
|------|----------|------|
| `visualization/wnet5_circuit_validator.py` | 修改 | 新增 `_adapt_svf_channels` 方法，修改 `_calculate_combined_transfer_functions` 方法 |

### 具体步骤

1. **新增 `_adapt_svf_channels` 方法** (约25行)
   - 位置: `_calculate_combined_transfer_functions` 方法之前
   - 功能: 实现通道裁剪和循环拓展逻辑

2. **修改 `_calculate_combined_transfer_functions` 方法** (约15行修改)
   - 添加通道数检查和自适应调用
   - 添加警告日志输出

3. **测试验证**
   - 正常场景: 18 vs 18 (无变化)
   - 裁剪场景: 18 vs 14 (裁剪4通道)
   - 拓展场景: 12 vs 18 (循环拓展)

### 警告日志示例

**裁剪场景 (SVF=18, 权重=14)**:
```
[WARNING] ⚠️ SVF通道数 (18) 与权重输入通道数 (14) 不匹配，已裁剪适配
   原始SVF通道: 18 -> 适配后: 14
```

**循环拓展场景 (SVF=12, 权重=18)**:
```
[WARNING] ⚠️ SVF通道数 (12) 与权重输入通道数 (18) 不匹配，已循环拓展适配
   原始SVF通道: 12 -> 适配后: 18
```

---

## 注意事项

### 1. SymPy表达式拷贝问题
循环拓展时复用同一个 SymPy 表达式对象是安全的，因为组合传递函数只读不修改这些表达式。

### 2. 通道顺序保持
- 裁剪: 保留前 N 个通道 (HP, BP, LP 顺序)
- 循环: 按顺序循环，不改变原始通道的相对顺序

### 3. 向后兼容性
- 正常匹配时行为完全不变
- 仅在不匹配时触发自适应逻辑
- 警告日志明确告知用户发生了适配

---

## 执行检查清单

- [ ] 在 `visualization/wnet5_circuit_validator.py` 中添加 `_adapt_svf_channels` 方法
- [ ] 修改 `_calculate_combined_transfer_functions` 方法，集成通道自适应逻辑
- [ ] 使用示例数据测试裁剪场景 (18→14)
- [ ] 使用示例数据测试循环拓展场景 (12→18)
- [ ] 验证警告日志正确输出
- [ ] 运行完整回归测试确保正常场景不受影响
