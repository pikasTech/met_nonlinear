# SpiceLib - 电路模拟与神经形态电路库

SpiceLib 是一个集成了 SPICE 仿真与 Python 科学计算的框架，主要用于设计、测试和评估模拟电路和神经形态电路系统。该库特别关注实现神经网络基本构建模块的模拟电路，如 ReLU 激活函数和全连接层（Dense层）。

## 功能特点

* 集成了 NGspice 仿真器和 Python 科学计算环境
* 实现了多种神经网络基本构建模块的模拟电路实现：
  - ReLU 激活函数电路
  - Dense 全连接层的模拟实现（带符号权重加法器）
* 提供了理论模型和 SPICE 电路仿真的对比功能
* 详细的仿真结果可视化
* 支持多通道输入/输出
* 灵活的运放模型配置
* 支持 E96 标准元件值

## 主要模块

### 电路模块

- **`circuit_base.py`**: 所有电路实现的基类
- **`circuit_relu.py`**: ReLU 激活函数电路实现
- **`cicuit_dense.py`**: 密集连接层（全连接层）电路实现
- **`circuit_dense_factory.py`**: 基于工厂模式的密集连接层电路创建工具
- **`circuit_dense_template.py`**: 密集连接层的模板定义

### 仿真模块

- **`simulation.py`**: 主仿真控制器，提供电路仿真和结果分析功能
- **`opamp_models.py`**: 运算放大器模型定义
- **`relu_models.py`**: ReLU 模型定义

### 测试模块

- **`test_relu.py`**: ReLU 电路测试代码
- **`test_dense.py`**: Dense 电路测试代码
- **`test_nrelu.py`**: 负向 ReLU 电路测试
- **`test_model_params.py`**: 模型参数测试

## 电路实现

### ReLU 激活函数电路

ReLU 电路通过二极管和运算放大器实现了模拟的 ReLU 特性：
- 运放同相端接输入信号
- 运放输出和反相端之间接一个二极管，方向从输出到反相端
- 反相端接电阻，然后接地
- 输出信号从运放的反相端输出
- 该电路在输入为负时输出为零，在输入为正时输出与输入成正比

### Dense 层电路

基于差分电流采样的带符号加法器电路：
- 每个输入通道同时连接到正向和负向支路
- 正向通道和负向通道的电流分别通过两个电流采样电阻汇总
- 运放电路放大两路电流的差值，实现带符号相加
- 支持多通道输出，适合实现向量-矩阵乘法（VMM）功能
- 支持每个输出通道添加常量偏置
- 可选支持在每个输出通道后添加 ReLU 激活函数

## 使用示例

### ReLU 电路测试

```python
from simulation import CircuitSimulation
from circuit_relu import PositiveReluCircuit
import numpy as np

# 创建仿真环境
sim = CircuitSimulation(output_folder='./temp')

# 测试参数
t_max = 1e-2  # 10ms
fs = 1e5      # 100kHz采样率

# 创建正向ReLU电路
circuit = PositiveReluCircuit(
    gain=1.0,          # 默认增益为1
    R_value=10e3,      # 10kΩ电阻
    opamp_config = {
        'model': 'OPAx205A',
        'include_file': "spice_models\OPAx205A.LIB",
    },
    use_e96=True
)

# 生成时间向量
t = np.arange(0, t_max, 1/fs)

# 生成正弦波输入信号
freq = 1e3
input_signal = 2.0 * np.sin(2 * np.pi * freq * t)

# 运行仿真
result = sim.run_simulation(t, input_signal, circuit)
```

### Dense 层电路测试

```python
from simulation import CircuitSimulation
from cicuit_dense import DenseCircuit
import numpy as np

# 创建仿真环境
sim = CircuitSimulation(output_folder='./temp')

# 使用直接的带符号增益矩阵创建电路（包含正负增益）
# 形状为 (weights, channels) - 4个权重，2个输出通道
gains = np.array([
    [1.0, -1.0],   # 第一个权重在两个通道中的增益值
    [-1.5, 0.8],   # 第二个权重在两个通道中的增益值
    [2.0, -0.5],   # 第三个权重在两个通道中的增益值
    [-0.8, 1.2]    # 第四个权重在两个通道中的增益值
])

# 运放配置
opamp_config = {
    'model': 'OPAx205A',
    'include_file': "spice_models\OPAx205A.LIB",
}

# 创建带符号加法器电路
circuit = DenseCircuit(
    gains=gains,
    opamp_config=opamp_config,
    use_e96=True,
    use_relu=False  # 是否添加ReLU激活
)

# 生成测试信号
t_max = 1e-1
fs = 2e3
t = np.arange(0, t_max, 1/fs)

# 创建输入信号 - [time_steps, weights] 格式
input_signals = np.zeros((len(t), circuit.n_inputs))
for i in range(circuit.n_inputs):
    freq = 1e1 * (i + 1)
    input_signals[:, i] = 0.5 * np.sin(2 * np.pi * freq * t)

# 运行仿真
result = sim.run_simulation(t, input_signals, circuit)
```

## 依赖库

- NumPy: 用于科学计算
- Matplotlib: 用于数据可视化
- SciPy: 用于信号处理
- NGspice: 用于电路仿真

## 安装

确保您的系统中已安装 NGspice 仿真器，并将其路径正确配置在 `CircuitSimulation` 类初始化参数中。

```bash
# 克隆项目
git clone https://github.com/yourusername/spicelib.git

# 进入项目目录
cd spicelib

# 安装依赖
pip install numpy matplotlib scipy
```

## 许可证

请参阅项目中的 LICENSE 文件获取详细信息。

## 致谢

该项目基于 SpiceLib 框架，感谢所有贡献者的工作。
