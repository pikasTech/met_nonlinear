# R15 SVF电路元件参数计算调查报告

## 1. 调查目的
调查代码中是否存在根据 SVF 电路的 $f_0$ 和 $Q$ 值计算电路元件参数（电阻、电容）的代码，并总结其计算公式。

## 2. 调查结果
在代码库中，SVF 电路元件参数的计算主要实现在 [spice_simulator/circuit_svf.py](spice_simulator/circuit_svf.py) 文件的 `SVFFilter` 类中的 `_calculate_rc_values` 方法中。

### 2.1 相关代码位置
- 文件路径：[spice_simulator/circuit_svf.py](spice_simulator/circuit_svf.py)
- 方法：`_calculate_rc_values(self, svf_index: int)` (约第 203 行)

### 2.2 电路拓扑结构
该代码实现的是一个标准的三运放状态变量滤波器（State Variable Filter），包含：
- 一个加法器/跟随器（用于 HP 输出和 Q 控制）
- 两个积分器（用于 BP 和 LP 输出）

### 2.3 计算公式总结

根据代码实现，元件参数的计算遵循以下逻辑：

#### 1. 基础电阻设置
设定基准电阻 $R_{base} = 10k\Omega$。
- $R_1 = R_{base} = 10k\Omega$ (输入电阻)
- $R_2 = R_1 = 10k\Omega$ (低通反馈电阻)
- $R_3 = R_1 = 10k\Omega$ (高通反馈电阻)

#### 2. 截止频率 $f_0$ 与积分器参数计算
设定积分器电阻 $R_4 = R_5 = 10k\Omega$。
根据公式 $f_0 = \frac{1}{2\pi RC}$，计算电容值 $C$：
$$C = \frac{1}{2\pi \cdot f_0 \cdot R_4}$$
代码实现：
```python
R_integrator = 10e3
c_value = (1 / (2 * np.pi * current_cutoff_freq * R_integrator))
R4 = R_integrator
R5 = R_integrator
```

#### 3. 品质因数 $Q$ 与反馈电阻计算
设定 $R_7 = R_{base} = 10k\Omega$。
根据 $Q$ 值的定义，计算 $R_6$：
$$R_6 = (3Q - 1) \cdot R_7$$
代码实现：
```python
R7 = R_base
R6 = (3 * current_Q - 1) * R7
```

### 2.4 公式推导验证
在 $R_1 = R_2 = R_3$ 的情况下，该电路的传递函数分母为：
$$D(s) = s^2 + \frac{\omega_0}{Q}s + \omega_0^2$$
其中 $\omega_0 = \frac{1}{R_4 C}$，且 $Q$ 与电阻的关系为：
$$\frac{1}{Q} = \frac{3 R_7}{R_6 + R_7}$$
解得：
$$R_6 = (3Q - 1) R_7$$
这与代码中的实现完全一致。

## 3. 结论
代码中确实存在根据 $f_0$ 和 $Q$ 计算 SVF 电路元件参数的逻辑，主要用于 SPICE 仿真网表的自动生成。计算公式标准且符合经典 SVF 电路设计理论。
