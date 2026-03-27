# 频率响应绘制机制深度调查报告

## 调查目的

深入分析当前 `-e` 评估任务中频率响应曲线的绘制机制，对比真正的幅频特性曲线与当前实现的差异，为频率响应对比可视化功能的改进提供技术依据。

## 调查范围

- **评估流程**: `-e` 参数触发的评估任务完整数据流
- **绘制函数**: `FR_for_comp_real_data` 函数的具体实现
- **数据结构**: `linear_response.json` 的数据格式和含义
- **绘制逻辑**: 当前实现与标准幅频特性曲线的差异

## 调查时间

**开始时间**: 2025年1月15日  
**完成时间**: 2025年1月15日  
**调查人员**: AI Assistant  

---

## 1. 评估任务数据流分析

### 1.1 调用链路

```
CLI (-e) → dispatch_task() → _handle_evaluate_task() → project.evaluate() → 
model_engine.predict_FR() → FR_for_comp_real_data()
```

### 1.2 关键调用代码

```python
# core/task_dispatcher.py _handle_evaluate_task
def _handle_evaluate_task(project_path, project_names, args):
    project = ProjectManager(project_path)
    project.evaluate()
    if len(project_names) == 1:
        plt.show()

# core/project_manager.py evaluate
def evaluate(self):
    # ... 模型评估逻辑 ...
    self.run_prediction(model_engine)

# core/project_manager.py run_prediction
def run_prediction(self, model_engine: ModelEngine):
    if self.config.use_predict_fr:
        logger.info(f'预测频率响应...')
        model_engine.predict_FR(self.config.USE_PREDICT_LINEAR)

# core/model_engine.py predict_FR
def predict_FR(self, USE_PREDICT_LINEAR=True):
    if self.config.dataset_type == 'MET':
        FR_for_comp_real_data(
            self.model_comp,
            self.dataset_test,
            freq_range=getattr(self.config, 'dataset', {}).get('freq_range_hz', (10, 128)),
            gain_range=(30, 200),
            freq_start_skip=0,
            freq_end_skip=2,
            output_folder=self.checkpoint_dir,
            use_linear_response=USE_PREDICT_LINEAR
        )
```

---

## 2. FR_for_comp_real_data 函数详细分析

### 2.1 函数签名和参数

```python
def FR_for_comp_real_data(
    model,                    # 训练好的补偿模型
    dataset: Dataset_COMP,    # 测试数据集
    freq_range=None,          # 频率范围
    gain_range=None,          # 增益范围
    use_debug=False,          # 调试模式
    freq_start_skip=0,        # 跳过开始的频率点数
    freq_end_skip=0,          # 跳过结束的频率点数
    output_folder='results',  # 输出目录
    use_linear_response=True, # 是否使用线性响应分析
    only_origin=False,        # 是否只显示原始数据
    config=None               # 配置参数
):
```

### 2.2 数据处理流程

#### 步骤1: 模型预测
```python
X_features = dataset.reshape2feature(dataset.output_ori)
pre_features = model.predict(X_features, batch_size=10)
pre_samples = dataset.reshape2sample(pre_features)
```

#### 步骤2: 系统响应计算
```python
for sweep_i in range(dataset.magn_num):
    inputs = dataset.inputs[sweep_i, :, :]      # 输入信号
    output_ori = dataset.output_ori[sweep_i, :, :]  # 原始输出
    output_cmp = pre_samples[sweep_i, :, :]     # 补偿后输出
    
    # 创建TimeSeries对象
    input_trs = [TimeSeries(inputs[freq_i, :], dataset.fs) 
                 for freq_i in range(inputs.shape[0])]
    output_trs = [TimeSeries(output_ori[freq_i, :], dataset.fs) 
                  for freq_i in range(output_ori.shape[0])]
    comped_trs = [TimeSeries(output_cmp[freq_i, :], dataset.fs) 
                  for freq_i in range(output_cmp.shape[0])]
    
    # 使用calibration_analyzer计算系统响应
    system_origin = System.fromTimeSeries(
        input_trs, output_trs, frequencies=dataset.freq_list, use_parallel=False
    )
    system_comped = System.fromTimeSeries(
        input_trs, comped_trs, frequencies=dataset.freq_list, use_parallel=False
    )
```

#### 步骤3: 幅频特性绘制
```python
# 调用calibration_analyzer的System.plot方法
system_origin.plot(
    markersize=0, 
    label=f'{magnitude:.2f}mm/s2 origin', 
    legend=True, 
    disable_phase=True
)

if not only_origin:
    system_comped.plot(
        linestyle='--', marker='x', markersize=4, 
        label=f'{magnitude:.2f}mm/s2 comped', 
        freq_range=freq_range, gain_range=gain_range, 
        legend=True, disable_phase=True
    )
```

### 2.3 真正的幅频特性曲线特征

基于 `calibration_analyzer/exam_class.py` 中 `System.plot()` 方法的分析：

```python
def plot(self, marker='o', markersize=7, ...):
    # 绘制幅度响应 - 这是真正的幅频特性曲线
    System.ax_gain.loglog(
        self.f,           # X轴: 频率 (Hz)
        self.toabs(),     # Y轴: 幅度响应 (线性幅度值)
        marker=marker, markersize=markersize,
        label=system_name, color=instance_color, linestyle=linestyle
    )
    System.ax_gain.set_xlabel("Frequency (Hz)")
    System.ax_gain.set_ylabel("Amplitude")
    System.ax_gain.grid(True, which="both", ls="--")
```

**关键特征**:
- **X轴**: 频率 (Hz) - 对数刻度
- **Y轴**: 幅度响应 - 对数刻度 (loglog plot)
- **数据**: 直接使用 `system.toabs()` 获取的幅度值
- **每条曲线**: 代表一个特定震级下的系统幅频响应

---

## 3. 当前 freq_response 实现分析

### 3.1 线性响应分析绘制

在 `FR_for_comp_real_data` 函数的 `use_linear_response=True` 分支中：

```python
if use_linear_response:
    fig_linear = plt.figure(figsize=(12, 8))
    
    for i in range(freq_start_skip, len(f) - freq_end_skip):
        # 原始响应绘制
        gain_origin = [gains_origin[k][i] for k in range(len(gains_origin))]
        lineraty = [gain / gain_origin[0] for gain in gain_origin]
        outputs_std = [lineraty[k] * magnitudes[k] for k in range(len(gain_origin))]
        
        plt.plot(
            magnitudes, outputs_std,
            label=f'Origin @ {f[i]} Hz', 
            linestyle='', marker='o', markersize=3, color=color
        )
    
    plt.xlabel('Magnitude (m/s^2)')
    plt.ylabel('Amplitude (Normalized)')
    plt.title('Frequency-Dependent Linear Response Analysis')
```

### 3.2 关键差异分析

| 方面 | 真正的幅频特性曲线 | 当前 freq_response 实现 |
|------|-------------------|------------------------|
| **X轴** | 频率 (Hz) | 震级 (m/s²) |
| **Y轴** | 幅度响应 (线性值) | 标准化幅度 |
| **刻度** | 双对数 (loglog) | 线性 |
| **曲线含义** | 每条曲线代表一个震级的幅频响应 | 每条曲线代表一个频率的震级响应 |
| **数据来源** | `system.toabs()` | 自定义标准化计算 |

### 3.3 数据标准化逻辑错误

当前实现中的标准化逻辑存在问题：

```python
# 原始响应的"标准化"
gain_origin = [gains_origin[k][i] for k in range(len(gains_origin))]
lineraty = [gain / gain_origin[0] for gain in gain_origin]  # 相对于第一个震级标准化
outputs_std = [lineraty[k] * magnitudes[k] for k in range(len(gain_origin))]

# 补偿后响应的"标准化" - 逻辑不一致
gain_comped = [gains_comped[k][i] for k in range(len(gains_comped))]
outputs = [gain_comped[k] * magnitudes[k] for k in range(len(gain_comped))]
lineraty = outputs[0] / magnitudes[0]  # 不同的标准化方式
outputs_std = [l / lineraty for l in outputs]
```

**问题**:
1. 原始响应和补偿后响应使用不同的标准化方法
2. 标准化后的物理意义不明确
3. 不是真正的幅频特性曲线

---

## 4. linear_response.json 数据结构分析

### 4.1 数据格式

```json
{
    "gains_origin": [     // 补偿前增益数据 [震级][频率]
        [freq1_mag1, freq2_mag1, ...],  // 震级1的各频率增益
        [freq1_mag2, freq2_mag2, ...],  // 震级2的各频率增益
        ...
    ],
    "gains_comped": [     // 补偿后增益数据 [震级][频率]
        [freq1_mag1, freq2_mag1, ...],
        [freq1_mag2, freq2_mag2, ...],
        ...
    ],
    "magnitudes": [1.2, 2.4, 3.6, 4.8, 6.0],  // 震级列表
    "frequencies": [160.0, 160.25, ...],       // 频率列表
    "fit_params_origin": [...],     // 拟合参数（补偿前）
    "fit_params_comped": [...]      // 拟合参数（补偿后）
}
```

### 4.2 数据含义

- **gains_origin/gains_comped**: 通过 `system.toabs()` 获取的真实幅度响应
- **数据维度**: `[len(magnitudes), len(frequencies)]`
- **物理意义**: 每个 `gains_origin[i][j]` 表示第i个震级、第j个频率的系统幅度响应

### 4.3 正确的幅频特性曲线绘制

基于JSON数据的正确绘制方式应该是：

```python
for mag_idx, magnitude in enumerate(magnitudes):
    # 提取该震级下所有频率的幅度响应
    amplitudes_origin = gains_origin[mag_idx]
    amplitudes_comped = gains_comped[mag_idx]
    
    # 绘制幅频特性曲线
    plt.loglog(frequencies, amplitudes_origin, 
               label=f'Origin {magnitude} m/s²', marker='o')
    plt.loglog(frequencies, amplitudes_comped, 
               label=f'Compensated {magnitude} m/s²', marker='^')

plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.title('Frequency Response (Bode Plot)')
```

---

## 5. 问题总结与建议

### 5.1 主要问题

1. **概念混淆**: 当前 `freq_response` 绘制的不是幅频特性曲线，而是"线性度分析图"
2. **坐标轴错误**: X轴应该是频率，Y轴应该是幅度响应
3. **刻度错误**: 应该使用对数刻度 (loglog)
4. **数据处理错误**: 不应该进行非物理意义的标准化

### 5.2 正确的幅频特性曲线特征

**标准的幅频特性曲线 (Bode Plot) 应该具备**:
- X轴: 频率 (Hz) - 对数刻度
- Y轴: 幅度响应 - 对数刻度
- 每条曲线: 代表不同震级下的系统频率响应
- 数据: 直接使用幅度值，无需标准化

### 5.3 改进建议

1. **重新实现频率响应对比功能**
   - 使用 `gains_origin` 和 `gains_comped` 数据
   - 正确的 loglog 绘制
   - 合理的曲线标签和图例

2. **保留线性度分析功能**
   - 将当前实现重命名为 "线性度分析"
   - 作为独立的分析功能保留

3. **提供多种可视化选项**
   - 标准幅频特性曲线
   - 线性度分析图
   - 相位响应曲线

### 5.4 技术实现路径

基于已有的 JSON 数据，可以快速实现正确的幅频特性曲线绘制，无需重新训练模型或修改数据生成逻辑。

---

## 6. 结论

当前的 `freq_response` 实现**并不是真正的幅频特性曲线**，而是一种线性度分析图。真正的幅频特性曲线应该以频率为X轴、幅度响应为Y轴，使用对数刻度绘制。

基于 `linear_response.json` 中已有的完整数据，可以轻松实现正确的幅频特性曲线绘制，为用户提供标准的频域分析工具。

---

**调查完成时间**: 2025年1月15日  
**文档版本**: v1.0  
**后续行动**: 基于本调查结果改进频率响应对比可视化功能