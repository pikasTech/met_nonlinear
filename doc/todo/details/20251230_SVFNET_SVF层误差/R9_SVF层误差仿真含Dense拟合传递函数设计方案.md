# R9: SVF层误差仿真拟合传递函数设计方案

## 1. 问题分析

### 1.1 当前实现的问题

根据 R8 的调查结果，当前带误差的 SVF 层计算存在以下问题：

**代码位置：** `visualization\wnet5_circuit_validator.py:771-818`

当前 `_calculate_svf_dense_combined_response` 方法的实现中，`measured_data` 参数**实际上没有被使用**：

```python
def _calculate_svf_dense_combined_response(
    self,
    svf_params: Dict,
    dense_weights: Dict,
    measured_data: Dict[str, Any] = None,  # 参数存在但未使用
    use_measured_svf: bool = True
) -> Dict[str, Any]:
    # 1. 构建传递函数（复用已有方法）- 始终使用理论值！
    svf_tfs = self._calculate_svf_transfer_functions(svf_params)
    combined_tfs = self._calculate_combined_transfer_functions(svf_tfs, dense_weights)

    # 2. 获取频率点 - 仅用于设置频率范围
    if measured_data is not None:
        frequencies = measured_data['frequencies']
        # ... 仅修改频率范围配置

    # 3. 计算频率响应（复用已有方法）- 仍使用理论传递函数
    freq_response = self._calculate_frequency_response(combined_tfs)
    # ...
```

**问题本质：**
- `measured_data` 只被用来设置频率范围
- 传递函数仍然使用理论值 `svf_params` 计算
- `use_measured_svf` 参数完全被忽略

### 1.2 R8 报告中描述的方法

R8 报告中提到的方法是：
$$H_{measured}(j\omega) = G_{measured}(\omega) \times e^{j\theta_{theory}(j\omega)}$$

但这个方法**并未在代码中实现**。

### 1.3 为什么需要替换

直接使用"实测增益 × 理论相位"的方法存在以下问题：

1. **物理意义不明确**：实测增益包含幅度和相位的综合效应，单独使用增益再乘以理论相位无法准确反映实际电路行为

2. **稳定性无法保证**：分离增益和相位后重新组合可能破坏系统的因果性和稳定性

3. **不符合工程惯例**：应该通过参数拟合找到等效的电路参数，然后用这些参数进行仿真

---

## 2. 解决方案：拟合传递函数参数

### 2.1 核心思路

通过**拟合实测数据**得到 SVF 的等效参数（$f_0$, $Q$），然后使用这些拟合参数配合理论仿真代码计算带误差的 SVF 层频率响应。

**优势：**
- 保持理论仿真代码不变，仅替换输入参数
- 拟合得到的参数具有物理意义
- 便于分析和比较不同电路的差异

### 2.2 拟合方法

#### 2.2.1 SVF 传递函数模型

状态变量滤波器的标准传递函数（HP/BP/LP 输出）：

**高通 (HP)：**
$$H_{HP}(s) = \frac{s^2}{s^2 + \frac{\omega_0}{Q}s + \omega_0^2}$$

**带通 (BP)：**
$$H_{BP}(s) = \frac{\frac{\omega_0}{Q}s}{s^2 + \frac{\omega_0}{Q}s + \omega_0^2}$$

**低通 (LP)：**
$$H_{LP}(s) = \frac{\omega_0^2}{s^2 + \frac{\omega_0}{Q}s + \omega_0^2}$$

其中 $\omega_0 = 2\pi f_0$，$f_0$ 为截止频率，$Q$ 为品质因数。

#### 2.2.2 拟合目标函数

对于每个通道（HP/BP/LP），使用**非线性最小二乘拟合**：

$$\min_{f_0, Q} \sum_i \left( G_{measured}(f_i) - G_{theory}(f_i, f_0, Q) \right)^2$$

其中 $G_{theory}$ 是理论传递函数的幅度响应。

#### 2.2.3 幅度响应公式

频率 $f$ 处的幅度响应（线性）：

**高通：**
$$|H_{HP}(f)| = \frac{(2\pi f)^4}{(2\pi f)^4 + (\frac{2\pi f_0}{Q})^2 (2\pi f)^2 + (2\pi f_0)^4}$$

**带通：**
$$|H_{BP}(f)| = \frac{(\frac{2\pi f_0}{Q})^2 (2\pi f)^2}{(2\pi f)^4 + (\frac{2\pi f_0}{Q})^2 (2\pi f)^2 + (2\pi f_0)^4}$$

**低通：**
$$|H_{LP}(f)| = \frac{(2\pi f_0)^4}{(2\pi f)^4 + (\frac{2\pi f_0}{Q})^2 (2\pi f)^2 + (2\pi f_0)^4}$$

---

## 3. 详细设计方案

### 3.1 新增方法

#### 3.1.1 `_fit_svf_parameters` - 拟合 SVF 参数

```python
def _fit_svf_parameters(
    self,
    frequencies: np.ndarray,
    magnitudes: List[np.ndarray],
    svf_params: Dict
) -> Dict[str, Any]:
    """拟合SVF参数以匹配实测数据

    Args:
        frequencies: 频率数组 (Hz)
        magnitudes: 实测幅度数据列表，每个元素对应一个通道
        svf_params: 初始 SVF 参数（包含 center_freqs, quality_factors）

    Returns:
        Dict: {
            'fitted_params': {
                'center_freqs': [...],  # 拟合后的截止频率
                'quality_factors': [...]  # 拟合后的 Q 值
            },
            'fitted_channels': [
                {'channel': str, 'f0': float, 'Q': float, 'rmse': float, 'r2': float}
            ],
            'fit_quality': {
                'overall_rmse': float,
                'overall_r2': float
            }
        }
    """
```

**实现要点：**
- 使用 `scipy.optimize.curve_fit` 进行拟合
- 初始猜测值使用理论 $f_0$ 和 $Q$
- 设置参数边界：$f_0 \in [0.5f_{theory}, 2f_{theory}]$, $Q \in [0.1, 20]$
- 计算拟合优度指标：RMSE, R²

#### 3.1.2 `_generate_fit_comparison_plot` - 拟合结果对比图

```python
def _generate_fit_comparison_plot(
    self,
    frequencies: np.ndarray,
    measured_mags: List[np.ndarray],
    fitted_mags: List[np.ndarray],
    channel_labels: List[str]
) -> str:
    """生成拟合结果对比图

    对比实测数据与拟合曲线的吻合程度

    Args:
        frequencies: 频率数组
        measured_mags: 实测幅度数据
        fitted_mags: 拟合得到的幅度数据
        channel_labels: 通道标签

    Returns:
        str: 生成的图片路径
    """
```

**图示风格：**
- 继承 `frequency_response_comparison_merged.png` 的风格
- 实测数据用实线
- 拟合曲线用虚线
- 包含 RMSE 和 R² 标注

#### 3.1.3 修改 `_calculate_svf_dense_combined_response`

```python
def _calculate_svf_dense_combined_response(
    self,
    svf_params: Dict,
    dense_weights: Dict,
    measured_data: Dict[str, Any] = None,
    use_measured_svf: bool = True,
    fitted_params: Dict = None  # 新增：拟合参数
) -> Dict[str, Any]:
    """计算 SVF + Dense 组合频率响应

    Args:
        svf_params: 原始 SVF 参数
        dense_weights: Dense 权重
        measured_data: SVF 实测数据
        use_measured_svf: 是否使用实测/拟合数据
        fitted_params: 拟合后的 SVF 参数（优先使用）

    Returns:
        Dict: 频率响应数据
    """
    # 选择使用的参数
    params_to_use = fitted_params if (use_measured_svf and fitted_params) else svf_params

    # 构建传递函数（使用拟合参数或原始参数）
    svf_tfs = self._calculate_svf_transfer_functions(params_to_use)
    combined_tfs = self._calculate_combined_transfer_functions(svf_tfs, dense_weights)

    # ... 其余逻辑不变
```

### 3.2 配置项扩展

在 `config.json` 中新增拟合相关配置：

```json
{
  "svf_error_simulation": {
    "enable": true,
    "measured_data_file": "exam_data/20251230_SVFNET_SVF_ONLY/20251230_SVF_ONLY.xlsx",
    "include_dense_layer": true,
    "fitting": {
      "enabled": true,
      "output_filename": "svf_fit_comparison.png",
      "save_fitted_params": true
    },
    "plot_config": {
      "merged_plot_mode": true,
      "output_filename": "svf_error_comparison.png",
      "dense_output_filename": "svf_dense_error_comparison.png"
    }
  }
}
```

### 3.3 输出数据

#### 3.3.1 拟合参数文件

保存拟合结果到 `numerics/svf_fitted_params.json`：

```json
{
  "fitted_params": {
    "center_freqs": [12.5, 80.2],  # 拟合后的截止频率 (Hz)
    "quality_factors": [0.72, 0.68]  # 拟合后的 Q 值
  },
  "fitted_channels": [
    {"channel": "SVF1_HP", "f0": 12.3, "Q": 0.71, "rmse": 0.015, "r2": 0.998},
    {"channel": "SVF1_BP", "f0": 12.7, "Q": 0.73, "rmse": 0.012, "r2": 0.999},
    {"channel": "SVF1_LP", "f0": 12.5, "Q": 0.72, "rmse": 0.018, "r2": 0.997},
    {"channel": "SVF2_HP", "f0": 80.5, "Q": 0.66, "rmse": 0.022, "r2": 0.995},
    {"channel": "SVF2_BP", "f0": 79.8, "Q": 0.69, "rmse": 0.019, "r2": 0.996},
    {"channel": "SVF2_LP", "f0": 80.2, "Q": 0.68, "rmse": 0.021, "r2": 0.995}
  ],
  "fit_quality": {
    "overall_rmse": 0.0178,
    "overall_r2": 0.996
  }
}
```

#### 3.3.2 生成的图片

1. **拟合结果对比图**：`plots/svf_fit_comparison.png`
   - 对比 SVF 层的实测原始数据 vs 拟合曲线
   - 验证拟合质量

2. **SVF+Dense 对比图**：`plots/svf_dense_error_comparison.png`
   - 虚线：理想 SVF + Dense
   - 实线：拟合 SVF + Dense

---

## 4. 实现步骤

### Step 1: 实现拟合方法

**文件：** `visualization\wnet5_circuit_validator.py`

新增方法：
- `_get_svf_magnitude_response(f, f0, Q, filter_type)` - 计算指定类型滤波器的幅度响应
- `_fit_svf_parameters()` - 拟合 SVF 参数
- `_generate_fit_comparison_plot()` - 生成拟合对比图

### Step 2: 修改执行流程

在 `execute_validation` 方法的 SVF 误差仿真分支中：

```python
if self.svf_error_enable:
    # 加载实测数据
    measured_data = self._load_svf_measured_data()

    # 拟合 SVF 参数（新增）
    if self.svf_error_config.get('fitting', {}).get('enabled', False):
        fitted_params = self._fit_svf_parameters(
            measured_data['frequencies'],
            measured_data['magnitude'],
            svf_params
        )
        # 保存拟合参数
        self._save_fitted_params(fitted_params)

        # 生成拟合对比图（新增）
        fit_plot = self._generate_fit_comparison_plot(
            measured_data['frequencies'],
            measured_data['magnitude'],
            self._calculate_fitted_magnitudes(measured_data['frequencies'], fitted_params),
            channel_labels
        )
        plots.append(fit_plot)
    else:
        fitted_params = None

    # 使用拟合参数计算 SVF+Dense 响应
    if include_dense:
        # 计算 baseline: 理想 SVF + Dense
        baseline_response = self._calculate_svf_dense_combined_response(
            svf_params, dense_weights,
            measured_data=None, use_measured_svf=False
        )

        # 计算 target: 拟合 SVF + Dense
        target_response = self._calculate_svf_dense_combined_response(
            svf_params, dense_weights,
            measured_data=measured_data, use_measured_svf=True,
            fitted_params=fitted_params  # 传递拟合参数
        )

        # 生成对比图
        dense_plot = self._generate_svf_dense_error_comparison_plot(
            baseline_response, target_response, dense_weights
        )
        plots.append(dense_plot)
```

### Step 3: 删除旧代码

删除 R8 中描述的"实测增益 + 理论相位"相关代码（如果存在）：

```python
# 删除以下代码：
# if use_measured_svf and measured_data is not None:
#     # 用实测增益数据替代理论计算
#     frequencies = measured_data['frequencies']
#     measured_mags = measured_data['magnitude']
#     # 将实测数据与理论传递函数结合
#     # 复数响应 = 实测增益 × 理论相位
```

### Step 4: 测试验证

1. 运行 `ep ex_projects/inference/wnet5-circuit-validation/SVF_ERROR_SIM`
2. 检查拟合对比图：实测数据与拟合曲线应高度吻合（R² > 0.99）
3. 检查 SVF+Dense 对比图：理想曲线与拟合曲线的差异应合理
4. 验证拟合参数文件正确生成

---

## 5. 代码位置汇总

| 功能 | 文件位置 | 新增/修改 |
|------|---------|---------|
| 拟合 SVF 参数 | `visualization\wnet5_circuit_validator.py` | 新增 `_fit_svf_parameters` |
| 拟合对比图 | `visualization\wnet5_circuit_validator.py` | 新增 `_generate_fit_comparison_plot` |
| 修改组合响应计算 | `visualization\wnet5_circuit_validator.py` | 修改 `_calculate_svf_dense_combined_response` |
| 修改执行流程 | `visualization\wnet5_circuit_validator.py` | 修改 `execute_validation` |
| 配置文件 | `ex_projects/inference/wnet5-circuit-validation/SVF_ERROR_SIM/config.json` | 新增 fitting 配置 |
| 拟合参数输出 | `numerics/svf_fitted_params.json` | 新增输出 |

---

## 6. 预期效果

1. **拟合结果对比图**：清晰展示实测数据与拟合曲线的吻合程度
2. **拟合参数文件**：包含物理意义的 $f_0$ 和 $Q$ 参数，便于分析电路误差来源
3. **SVF+Dense 对比图**：使用拟合参数计算，更准确地反映实际电路行为
4. **代码简化**：删除不合理的"实测增益 + 理论相位"方法，统一使用拟合参数

---

## 7. 参考资料

1. 状态变量滤波器理论：《Analog Filter Design》- Robert Schaumann
2. 非线性最小二乘拟合：`scipy.optimize.curve_fit`
3. 拟合优度评估：`sklearn.metrics.r2_score`
4. 现有 SVF 层代码：`spice_simulator\circuit_svf.py`
5. 现有可视化代码：`visualization\wnet5_circuit_validator.py`
