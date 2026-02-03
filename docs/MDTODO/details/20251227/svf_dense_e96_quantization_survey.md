# SVF-DENSE单层仿真E96量化误差调查报告

**生成日期**: 2025-12-27
**更新**: 2025-12-27 (补充wnet5-circuit-validation仿真方式分析)

---

## 1. 调查概述

### 1.1 关键发现
- **wnet5-circuit-validation** 使用 **NumPy + SymPy 理论计算**，**不使用 SPICE**
- E96量化在 SPICE 电路生成时实现，wnet5-circuit-validation 中没有此功能
- 权重→电阻→E96量化的转换链路：`gain → r_raw = R_base/gain → r_e96 = _convert_to_standard_value(r_raw)`

---

## 2. wnet5-circuit-validation 仿真方式分析

### 2.1 任务入口

| 文件 | 行号 | 功能 |
|------|------|------|
| `core/external_cli_handler.py` | 564-584 | `_execute_wnet5_circuit_validation_task()` |
| `visualization/wnet5_circuit_validator.py` | - | `WNET5CircuitValidator` 核心类 |

### 2.2 使用的技术栈

| 组件 | 使用情况 | 说明 |
|------|----------|------|
| **NumPy** | ✅ 使用 | 数值计算、频率响应计算 |
| **SymPy** | ✅ 使用 | 符号计算传递函数 |
| **SPICE** | ❌ 不使用 | 无网表仿真 |
| **TensorFlow** | ⚠️ 可选 | 仅在线模式用于加载模型权重 |

### 2.3 数据流链路

```
config.json (task_type="wnet5-circuit-validation")
    │
    v
WNET5CircuitValidator.execute_validation()
    │
    ├─> 离线模式 (offline_mode=True)
    │   └── 使用 precomputed_data
    │
    └─> 在线模式 (默认)
        │
        ├─> _load_model()
        │   └── 加载: projects/{model}/data/best.weights.h5 (TensorFlow)
        │
        ├─> _extract_svf_parameters(model)
        │   └── 提取: center_freqs, quality_factors
        │
        ├─> _extract_dense_weights(model, analysis_layer)
        │   └── 提取: kernel (权重矩阵), bias
        │
        ├─> _calculate_svf_transfer_functions()  [SymPy]
        │   └── 计算: HP/BP/LP 传递函数符号表达式
        │
        ├─> _calculate_combined_transfer_functions()  [NumPy + SymPy]
        │   └── 计算: Σ(weight[i] × SVF_channel[i]) + bias
        │
        ├─> _calculate_frequency_response()  [NumPy]
        │   └── 计算: |H(jω)| 幅频响应
        │
        └─> _generate_plots()
            └── 与实验Excel数据对比
```

### 2.4 核心计算代码位置

| 方法 | 文件行号 | 功能 |
|------|----------|------|
| `_calculate_svf_transfer_functions()` | `wnet5_circuit_validator.py:564-587` | SymPy符号计算SVF传递函数 |
| `_calculate_combined_transfer_functions()` | `wnet5_circuit_validator.py:589-612` | 权重×传递函数组合 |
| `_calculate_frequency_response()` | `wnet5_circuit_validator.py:614-645` | NumPy数值计算幅频响应 |

---

## 3. 权重→电阻→E96量化的转换链路

### 3.1 SPICE电路中的转换逻辑 (`circuit_dense.py`)

```python
# circuit_dense.py:301-321
R_base = 1e3  # 输入电阻基准值

for gain in channel_gains:
    # 步骤1: 权重 → 原始电阻值
    if gain > 0:
        r_pos_raw = R_base / gain          # 第305行
        r_neg_raw = MAX_RESISTANCE
    elif gain < 0:
        r_pos_raw = MAX_RESISTANCE
        r_neg_raw = R_base / abs(gain)     # 第310行

    # 步骤2: 原始电阻值 → E96量化值
    r_pos = self._convert_to_standard_value(r_pos_raw) if self.use_e96 else r_pos_raw  # 第318-319行
    r_neg = self._convert_to_standard_value(r_neg_raw) if self.use_e96 else r_neg_raw  # 第320-321行
```

### 3.2 E96量化实现 (`circuit_base.py:23-44`)

```python
E96_VALUES: List[float] = [
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30, 1.33, 1.37, 1.40,
    # ... 共96个标准值
]

def _convert_to_standard_value(self, value: float) -> float:
    """将任意电阻值转换为最接近的E96标准值"""
    if value <= 0:
        return value

    exponent = np.floor(np.log10(value))
    mantissa = value / (10 ** exponent)

    closest_value = min(self.E96_VALUES, key=lambda x: abs(x - mantissa))
    return closest_value * (10 ** exponent)
```

### 3.3 逆向转换：E96电阻 → 等效增益

要在 wnet5-circuit-validation 中模拟量化误差，需要逆向转换：

```python
# 量化后的等效增益
# r_e96 = R_base / gain_quantized
# => gain_quantized = R_base / r_e96

gain_quantized = R_base / r_e96
```

---

## 4. wnet5-circuit-validation 中添加E96量化误差的方案

### 4.1 修改位置

**核心修改**: `visualization/wnet5_circuit_validator.py`

需要修改 `_calculate_combined_transfer_functions()` 方法：
1. 在权重组合前，先将权重转换为E96量化后的等效权重
2. 然后用量化后的等效权重计算组合传递函数

### 4.2 实现伪代码

```python
# 在 wnet5_circuit_validator.py 中添加

class WNET5CircuitValidator:
    E96_VALUES: List[float] = [...]  # 从 circuit_base.py 复制

    def _convert_to_e96(self, value: float) -> float:
        """将电阻值转换为E96标准值 (复制自 circuit_base.py)"""
        if value <= 0:
            return value
        exponent = np.floor(np.log10(value))
        mantissa = value / (10 ** exponent)
        closest_value = min(self.E96_VALUES, key=lambda x: abs(x - mantissa))
        return closest_value * (10 ** exponent)

    def _weight_to_quantized_weight(self, weight: float, R_base: float = 1e3) -> float:
        """将神经网络权重转换为E96量化后的等效权重

        转换链路: weight → r_raw = R_base/|weight| → r_e96 → gain_e96 = R_base/r_e96
        """
        if abs(weight) < 1e-10:
            return 0.0

        # 步骤1: 权重 → 原始电阻值
        r_raw = R_base / abs(weight)

        # 步骤2: 原始电阻值 → E96量化值
        r_e96 = self._convert_to_e96(r_raw)

        # 步骤3: E96量化电阻 → 等效权重
        gain_e96 = R_base / r_e96 * np.sign(weight)

        return gain_e96

    def _calculate_combined_transfer_functions(self, svf_tfs, dense_weights, use_e96=False):
        """计算SVF+Dense组合传递函数 (支持E96量化)"""
        # ... 原有代码 ...

        w = dense_weights['weights']  # (in_ch, out_ch)

        # 如果启用E96量化，转换权重
        if use_e96:
            R_base = 1e3  # 与 circuit_dense.py 保持一致
            w_quantized = np.zeros_like(w)
            for i in range(w.shape[0]):
                for o in range(w.shape[1]):
                    w_quantized[i, o] = self._weight_to_quantized_weight(w[i, o], R_base)
            w = w_quantized

        # ... 其余代码不变 ...
```

### 4.3 配置项添加

在 `config.json` 中添加：

```json
{
  "task_type": "wnet5-circuit-validation",
  "model_project_name": "WNET5q1h2u6l3",
  "analysis_layer": 1,
  "use_e96_quantization": true,  // 新增：启用E96量化误差仿真
  "frequency_range": {
    "start_freq": 2,
    "stop_freq": 500
  }
}
```

### 4.4 配置解析

在 `WNET5CircuitValidator.__init__()` 中解析：

```python
self.use_e96_quantization = config.get('use_e96_quantization', False)
```

---

## 5. 两种仿真方式的对比

| 方面 | wnet5-circuit-validation | SPICE推理 |
|------|--------------------------|-----------|
| **计算方式** | NumPy + SymPy 传递函数 | SPICE网表仿真 |
| **E96量化位置** | 需要额外实现 | 已实现 (use_e96参数) |
| **仿真精度** | 理论值 (理想器件) | 可模拟实际器件特性 |
| **计算速度** | 快 (纯数学计算) | 慢 (需要求解电路方程) |
| **与实测对比** | 适合频率响应验证 | 适合时域瞬态仿真 |

---

## 6. 实现路径建议

### 6.1 最小修改方案 (方案A)

**仅修改 `wnet5_circuit_validator.py`**：

1. 复制 `_convert_to_standard_value()` 方法
2. 添加 `_weight_to_quantized_weight()` 方法
3. 修改 `_calculate_combined_transfer_functions()` 支持 `use_e96` 参数
4. 在 `__init__()` 中解析配置

**优点**: 不影响现有SPICE推理代码
**缺点**: 需要重新实现量化逻辑

### 6.2 复用方案 (方案B)

**复用 `circuit_base.py` 的E96量化逻辑**：

1. 在 `wnet5_circuit_validator.py` 中导入 `from spice_simulator.circuit_base import BaseCircuit`
2. 实例化一个临时电路对象来使用 `_convert_to_standard_value()`
3. 或者将E96量化函数提取为独立工具函数

**优点**: 代码复用，避免重复实现
**缺点**: 引入额外依赖

### 6.3 完整方案 (方案C)

**创建统一量化工具模块**：

```python
# spice_simulator/resistance_quantizer.py (新建)
class ResistanceQuantizer:
    E96_VALUES = [...]  # 从 circuit_base.py 移动到此

    @staticmethod
    def to_e96(value: float) -> float: ...

    @staticmethod
    def weight_to_quantized_weight(weight: float, R_base: float = 1e3) -> float: ...
```

**优点**: 统一管理，易于维护
**缺点**: 需要新建文件

---

## 7. 结论

### 7.1 当前状态总结

| 任务类型 | 仿真方式 | E96量化支持 |
|----------|----------|-------------|
| wnet5-circuit-validation | NumPy + SymPy 理论计算 | ❌ 不支持 |
| SPICE推理 | SPICE网表仿真 | ✅ 支持 (use_e96参数) |

### 7.2 wnet5-circuit-validation 添加E96量化的要点

1. **核心挑战**: 该任务使用纯数学计算，不经过SPICE电路，所以需要"手动"模拟量化过程
2. **关键转换**: `weight → r_raw = R_base/|weight| → r_e96 → gain_e96 = R_base/r_e96`
3. **最小修改**: 在 `_calculate_combined_transfer_functions()` 中添加权重量化转换
4. **配置添加**: 在config.json中添加 `use_e96_quantization` 选项

### 7.3 推荐方案

**推荐方案A (最小修改)**，因为：
- 修改范围小，易于测试和验证
- 不影响现有SPICE推理代码
- 便于对比理想/量化两种模式的差异

---

**报告生成**: Claude Code
**调查日期**: 2025-12-27
