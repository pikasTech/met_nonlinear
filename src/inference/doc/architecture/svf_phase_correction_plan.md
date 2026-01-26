# SVF层相位一致性修正方案

## 问题根源

经过深入分析，发现SVF层在NN推理和SPICE推理中相位不一致的根本原因：

### 1. 神经网络(NN)推理

- **实现方式**：使用传递函数定义HP、BP、LP滤波器
  ```python
  highpass_expr = s**2 / (s**2 + (omega0/Q)*s + omega0**2)
  bandpass_expr = (s*(omega0/Q))/(s**2 + (omega0/Q)*s + omega0**2)
  lowpass_expr = (omega0**2) / (s**2 + (omega0/Q)*s + omega0**2)
  ```
- **输出相位**：取决于传递函数的定义，理论上应该是标准的SVF输出
- **post_process**：NN推理时**不调用**post_process方法

### 2. SPICE推理

- **电路仿真**（circuit_svf.py的simulate_numpy）：
  ```python
  out1[j] = -hp  # 高通输出（已反相）
  out2[j] = bp   # 带通输出（正相）
  out3[j] = -lp  # 低通输出（已反相）
  ```
- **post_process处理**：
  ```python
  # HP (j%3==0) 和 LP (j%3==2) 会被反相
  if j % 3 == 0 or j % 3 == 2:
      record.data[:, j] = -record.data[:, j]
  ```
- **最终结果**：HP和LP经过双重反相变为正相，BP保持正相

### 3. 相位不一致的原因

**关键发现**：SPICE的numpy仿真中，HP和LP输出已经包含了负号，这可能与NN的传递函数实现不一致。

## 解决方案

### 方案：修改SPICE仿真的输出相位

修改`circuit_svf.py`的`simulate_numpy`方法，去除HP和LP的负号，让post_process统一处理相位：

**修改文件：`spice_simulator/circuit_svf.py`**

**修改位置：simulate_numpy方法（第420-423行）**

原代码：
```python
# 保存输出
out1[j] = -hp  # 高通输出
out2[j] = bp   # 带通输出
out3[j] = -lp  # 低通输出
```

修改为：
```python
# 保存输出（不进行相位反转，让post_process统一处理）
out1[j] = hp   # 高通输出
out2[j] = bp   # 带通输出
out3[j] = lp   # 低通输出
```

### 验证相位一致性

在`cli.py`的`_analyze_inference_errors`中添加相位检测：

```python
# 在第一层分析后添加相位检测
if i == 0:  # 第一层（SVF层）
    # 检查每个通道的相位
    for ch in range(min(6, nn_data.records[0].data.shape[1])):
        nn_ch = nn_data.records[0].data[:, ch]
        spice_ch = spice_data.records[0].data[:, ch]
        
        # 计算相关系数
        corr = np.corrcoef(nn_ch, spice_ch)[0, 1]
        ch_type = ['HP', 'BP', 'LP'][ch % 3]
        ch_num = ch // 3
        
        print(f"  通道{ch} ({ch_type}{ch_num}): 相关系数 = {corr:.3f}")
        
        # 如果相关系数为负，说明相位相反
        if corr < -0.8:
            print(f"    警告：检测到相位反转！")
```

## 实施步骤

1. **备份原文件**：
   ```bash
   cp spice_simulator/circuit_svf.py spice_simulator/circuit_svf.py.backup
   ```

2. **修改circuit_svf.py**：去除HP和LP的负号

3. **测试验证**：
   ```bash
   conda run -n tf26 python cli.py -i WNET5q0.5h2u6l3
   conda run -n tf26 python cli.py -a WNET5q0.5h2u6l3
   ```

4. **检查结果**：
   - 查看相位检测输出
   - 确认所有通道的相关系数都是正的

## 代码修改量

- 修改文件：1个（`spice_simulator/circuit_svf.py`）
- 修改行数：3行
- 风险等级：低（仅影响numpy仿真的输出相位）

## 备选方案

如果上述方案不能解决问题，可以考虑：

### 备选方案1：修改post_process逻辑

在SVFLayer的post_process中添加来源检测：

```python
def post_process(self, output_wave: WaveData):
    # 检查是否来自SPICE仿真
    if output_wave.user_metadata.get('source') == 'spice':
        # SPICE已经处理了相位，不需要再处理
        return output_wave
    
    # 原有的相位处理逻辑...
```

### 备选方案2：统一NN和SPICE的SVF实现

确保NN的传递函数实现与SPICE电路实现产生相同的相位输出。

## 预期结果

修改后，SPICE推理的SVF输出应该与NN推理完全一致：
- 所有通道（HP、BP、LP）都是正相
- 误差分析显示较小的差异
- 相关系数都接近+1

## 注意事项

1. 这个修改会影响所有使用SVF的SPICE仿真
2. 需要验证修改不会破坏其他功能
3. 可能需要调整相关的测试代码