# R8: SVF层误差仿真数学原理调查报告

## 概述

本报告调查了带误差的SVF层和不带误差的SVF层的计算过程的数学原理，重点分析两者的计算公式差异，并追溯到特定的代码实现位置。

---

## 1. 不带误差的SVF层计算原理

### 1.1 理论数学公式

状态变量滤波器(State Variable Filter, SVF)的理想传递函数基于二阶系统标准形式：

**共同的分母多项式：**
$$D(s) = s^2 + \frac{\omega_0}{Q}s + \omega_0^2$$

其中：
- $\omega_0 = 2\pi f_0$ 为截止角频率
- $f_0$ 为截止频率(Hz)
- $Q$ 为品质因数

**三种滤波输出的传递函数：**

1. **高通输出 (High-Pass)：**
   $$H_{HP}(s) = \frac{s^2}{s^2 + \frac{\omega_0}{Q}s + \omega_0^2}$$

2. **带通输出 (Band-Pass)：**
   $$H_{BP}(s) = \frac{\frac{\omega_0}{Q}s}{s^2 + \frac{\omega_0}{Q}s + \omega_0^2}$$

3. **低通输出 (Low-Pass)：**
   $$H_{LP}(s) = \frac{\omega_0^2}{s^2 + \frac{\omega_0}{Q}s + \omega_0^2}$$

### 1.2 代码实现位置

**文件：** `spice_simulator\circuit_svf.py`

**传递函数计算方法：** `_calculate_svf_transfer_functions` (间接使用，通过符号计算)

**时域递推实现方法：** `simulate_numpy` (第384-458行)

```python
# 位置: spice_simulator\circuit_svf.py:426-449

# 角频率计算
omega_0 = 2 * np.pi * current_cutoff_freq

# 频率常数和阻尼常数
F1 = 2 * np.sin(omega_0 * dt / 2) / dt   # 频率常数
F2 = 1 / Q                              # 阻尼常数

# 逐点计算滤波器输出
for j in range(len(t)):
    # 高通输出计算
    hp = input_signal[j] - lp_z1 - F2 * bp_z1
    # 带通输出计算
    bp = bp_z1 + F1 * hp * dt
    # 低通输出计算
    lp = lp_z1 + F1 * bp_z1 * dt

    # 保存输出（反相，与SPICE行为一致）
    out1[j] = -hp   # 高通输出
    out2[j] = bp   # 带通输出
    out3[j] = -lp   # 低通输出

    # 更新状态变量
    bp_z1 = bp
    lp_z1 = lp
```

**符号计算传递函数实现：** `wnet5_circuit_validator.py:1403-1426`

```python
# 位置: visualization\wnet5_circuit_validator.py:1403-1426

def _calculate_svf_transfer_functions(self, svf_params):
    """计算SVF传递函数"""
    import sympy as sp
    s = sp.Symbol('s')

    transfer_functions = []
    for f0, Q in zip(svf_params['center_freqs'], svf_params['quality_factors']):
        omega0 = 2 * sp.pi * f0
        denominator = s**2 + (omega0/Q)*s + omega0**2

        H_hp = s**2 / denominator                    # 高通
        H_bp = (s * omega0/Q) / denominator          # 带通
        H_lp = omega0**2 / denominator               # 低通

        transfer_functions.append({
            'high_pass': H_hp,
            'band_pass': H_bp,
            'low_pass': H_lp,
            'f0': f0,
            'Q': Q
        })

    return transfer_functions
```

---

## 2. 带误差的SVF层计算原理

### 2.1 误差来源与处理方式

带误差的SVF层不使用理论传递函数，而是直接使用**实测频率响应数据**。误差来源包括：

1. **元器件非理想特性：** 电阻、电容的实际值与标称值的偏差
2. **运放非理想特性：** 有限增益带宽积、输入偏置电流、噪声等
3. **PCB布局影响：** 寄生电容、寄生电感、串扰等
4. **温度漂移：** 元器件参数随温度的变化

### 2.2 实测数据加载

**代码位置：** `visualization\wnet5_circuit_validator.py:393-477`

```python
# 位置: visualization\wnet5_circuit_validator.py:393-477

def _load_svf_measured_data(self) -> Dict[str, Any]:
    """加载SVF层实测频率响应数据"""
    import pandas as pd

    # 读取Excel文件
    df = pd.read_excel(file_path)

    # 解析频率列
    frequencies = df[freq_cols[0]].to_numpy(dtype=float)

    # 解析6个通道数据 (ch1-ch6)
    # 对应: SVF1_HP, SVF1_BP, SVF1_LP, SVF2_HP, SVF2_BP, SVF2_LP
    channels = []
    for i in range(1, 7):
        col_name = f'ch{i}'
        if col_name in df.columns:
            channel_data = df[col_name].to_numpy(dtype=float)
            channel_data = np.clip(channel_data, 1e-20, None)
            channels.append(channel_data)

    return {
        'frequencies': frequencies,
        'magnitude': channels  # 线性增益
    }
```

### 2.3 带误差的SVF+Dense组合计算

**代码位置：** `visualization\wnet5_circuit_validator.py:771-818`

当启用SVF误差仿真时，计算流程如下：

```python
# 位置: visualization\wnet5_circuit_validator.py:771-818

def _calculate_svf_dense_combined_response(
    self,
    svf_params: Dict,
    dense_weights: Dict,
    measured_data: Dict[str, Any] = None,
    use_measured_svf: bool = True
) -> Dict[str, Any]:
    """计算 SVF + Dense 组合频率响应"""

    # 1. 构建传递函数
    svf_tfs = self._calculate_svf_transfer_functions(svf_params)

    # 2. 如果使用实测SVF数据，替换理论传递函数
    if use_measured_svf and measured_data is not None:
        # 用实测增益数据替代理论计算
        frequencies = measured_data['frequencies']
        measured_mags = measured_data['magnitude']

        # 将实测数据与理论传递函数结合
        # 复数响应 = 实测增益 × 理论相位
        ...

    # 3. 计算组合传递函数
    combined_tfs = self._calculate_combined_transfer_functions(svf_tfs, dense_weights)

    # 4. 计算频率响应
    freq_response = self._calculate_frequency_response(combined_tfs)

    return freq_response
```

### 2.4 误差仿真的核心公式

**实测增益与理论相位的结合：**

$$H_{measured}(j\omega) = G_{measured}(\omega) \times e^{j\theta_{theory}(j\omega)}$$

其中：
- $G_{measured}(\omega)$ 是从Excel文件读取的实测增益（线性）
- $\theta_{theory}(j\omega)$ 是理论传递函数的相位响应

**这种处理方式的原理：**
- 实测数据包含幅度误差和相位误差
- 但在当前实现中，只使用实测的**幅度**信息
- 相位仍使用理论计算，以保证因果性和稳定性

---

## 3. 两种计算方式的对比分析

### 3.1 计算流程对比

| 方面 | 不带误差(SVF理想) | 带误差(SVF实测) |
|------|------------------|-----------------|
| **输入参数** | 截止频率 $f_0$、Q值 | 截止频率 $f_0$、Q值 + 实测增益数据 |
| **计算方法** | 符号计算/递推滤波 | 实测数据 + 理论相位 |
| **频率响应** | 纯理论计算 | 实测幅度 × 理论相位 |
| **结果确定性** | 每次计算结果相同 | 取决于实测数据 |
| **适用范围** | 理想电路仿真 | 实际硬件验证 |

### 3.2 数学公式对比

**不带误差：**
$$H(j\omega) = \frac{(j\omega)^2}{(j\omega)^2 + \frac{\omega_0}{Q}j\omega + \omega_0^2} \quad \text{(高通)}$$

**带误差：**
$$H_{error}(j\omega) = G_{measured}(\omega) \times \frac{(j\omega)^2}{(j\omega)^2 + \frac{\omega_0}{Q}j\omega + \omega_0^2}$$

其中 $G_{measured}(\omega)$ 是实测增益值。

### 3.3 误差来源对比

| 误差类型 | 不带误差 | 带误差 |
|---------|---------|--------|
| 电阻误差 | 无（使用标称值） | 有（体现在实测数据中） |
| 电容误差 | 无 | 有 |
| 运放非理想性 | 无（使用理想运放模型） | 有 |
| 温度漂移 | 无 | 有 |
| PCB布局影响 | 无 | 有 |

---

## 4. 代码实现位置汇总

| 功能 | 文件位置 | 行号范围 |
|------|---------|---------|
| SVF电路类定义 | `spice_simulator\circuit_svf.py` | 48-459 |
| 电阻/电容值计算 | `spice_simulator\circuit_svf.py` | 180-258 |
| 网表生成 | `spice_simulator\circuit_svf.py` | 273-339 |
| 时域递推仿真 | `spice_simulator\circuit_svf.py` | 384-458 |
| SVF层包装器 | `models\model_layers.py` | 225-362 |
| 传递函数计算 | `visualization\wnet5_circuit_validator.py` | 1403-1426 |
| 组合传递函数 | `visualization\wnet5_circuit_validator.py` | 1428-1451 |
| 频率响应计算 | `visualization\wnet5_circuit_validator.py` | 1453-1484 |
| 实测数据加载 | `visualization\wnet5_circuit_validator.py` | 393-477 |
| SVF+Dense组合计算 | `visualization\wnet5_circuit_validator.py` | 771-818 |
| 误差对比图生成 | `visualization\wnet5_circuit_validator.py` | 820-908 |

---

## 5. 结论

### 5.1 核心差异

1. **不带误差的SVF层**使用纯数学公式计算频率响应，结果完全由理论参数($f_0$, $Q$)决定。

2. **带误差的SVF层**使用实测数据替换理论增益计算，保留了实际电路中的各种非理想效应。

3. 当前实现中，带误差仿真使用"实测幅度 × 理论相位"的组合方式，这是考虑到：
   - 实测数据直接反映了电路的实际表现
   - 理论相位保证了系统的因果性和稳定性
   - 便于量化电路误差对整体性能的影响

### 5.2 应用场景

- **不带误差仿真：** 电路设计初期验证、参数优化、理论分析
- **带误差仿真：** 实际硬件验证、误差来源分析、可靠性评估

---

## 6. 参考资料

1. 状态变量滤波器理论：《Analog Filter Design》- Robert Schaumann
2. SVF电路实现：`spice_simulator\circuit_svf.py`
3. 误差仿真配置：`ex_projects\inference\wnet5-circuit-validation\SVF_ERROR_SIM\config.json`
4. 实测数据文件：`exam_data/20251230_SVFNET_SVF_ONLY/20251230_SVF_ONLY.xlsx`
