# CLAUDE.md

本文件为Claude Code (claude.ai/code)在此代码库中工作时提供指导。

## 项目概述

这是**spice_simulator** - 一个集成神经形态电路设计的综合性Python SPICE电路仿真框架。该项目专注于实现神经网络组件的模拟电路等效实现，特别是使用运算放大器和电子元件实现ReLU激活函数和全连接层。


### 测试
```bash
# 运行单个电路测试
python test_relu.py          # 测试ReLU激活电路
python test_dense.py         # 测试全连接层电路
python test_RC.py            # 测试RC滤波器电路
python test_svf.py           # 测试状态变量滤波器电路
python test_nrelu.py         # 测试负向ReLU电路


## 高级架构

### 核心框架结构

**第三方 SpiceLib核心 (`spicelib/`)**
- 这是第三方的库，用于仿真电路，我们使用的是NGspice，不要尝试修改这个库
- 统一的仿真接口和结果处理
- 分布式仿真的客户端-服务器架构

**电路实现 (`circuit_*.py`)**
- `circuit_base.py`：带E96标准电阻值的抽象基类
- `circuit_relu.py`：ReLU激活函数电路（正向/负向）
- `circuit_dense.py`：带符号电流求和的全连接层实现
- `circuit_svf.py`：状态变量滤波器实现
- `circuit_RC.py`：基本RC滤波器电路

**仿真引擎 (`simulation.py`)**
- `CircuitSimulation`：主仿真控制器
- 并行批量仿真支持
- 自动结果插值和比较
- 集成绘图和可视化

### 详细组件分析

#### 1. **仿真引擎 (simulation.py)**

`CircuitSimulation`类是整个框架的核心，提供了完整的电路仿真管道：

**核心功能：**
- **并行处理**：使用`ProcessPoolExecutor`实现多进程并行仿真，默认16个工作进程
- **临时文件管理**：可配置的临时文件清理（.raw, .net, .log文件）
- **信号生成**：内置正弦波、方波等测试信号生成器
- **结果处理**：自动插值对齐、误差统计（最大误差、平均误差、RMSE）

**仿真流程：**
1. 创建包含电路定义的临时网表文件
2. 修改电压源，添加PWL（分段线性）数据
3. 通过`SimRunner`执行NGspice仿真
4. 从.raw文件读取结果并进行后处理
5. 将SPICE结果与理论计算进行比较

**关键方法：**
- `run_simulation_once()`: 单次仿真执行
- `run_batch_simulations()`: 批量并行仿真
- `create_simulation_netlist()`: 动态网表生成
- `_resample_spice_outputs()`: 时间对齐和插值

#### 2. **电路基类架构 (circuit_base.py)**

定义了所有电路必须遵循的接口规范：

```python
class BaseCircuit(ABC):
    # E96标准电阻值（1%容差）
    E96_VALUES = [1.00, 1.02, 1.05, ...]
    
    @abstractmethod
    def get_circuit_netlist() -> str
    @abstractmethod  
    def simulate_numpy() -> np.ndarray
    
    # 标准化的I/O命名
    def get_input_source_names() -> List[str]  # Vin1, Vin2, ...
    def get_output_node_names() -> List[str]   # out1, out2, ...
```

#### 3. **电路实现详解**

**3.1 ReLU激活电路 (circuit_relu.py)**
- **拓扑结构**：运放 + 单二极管反馈
- **工作原理**：
  - 输入为正时：二极管截止，电路为单位增益缓冲器
  - 输入为负时：二极管导通，输出被钳位到0V
- **关键参数**：增益、电阻值、二极管模型

**3.2 全连接层电路 (circuit_dense.py)**
- **创新设计**：差分电流采样的带符号加法器
- **核心思想**：
  - 每个输入分成正负两路
  - 通过电阻矩阵实现权重
  - 电流模式求和实现加法
  - 差分放大器输出带符号结果
- **支持特性**：
  - 多输入多输出（矩阵运算）
  - 可选偏置项
  - 可选ReLU激活

**3.3 状态变量滤波器 (circuit_svf.py)**
- **三运放拓扑**：同时输出高通、带通、低通
- **配置参数**：截止频率、Q因子
- **支持多个SVF单元并行**

#### 4. **模型抽象层**

**4.1 运放模型 (opamp_models.py)**

采用策略模式实现不同精度的运放模型：

```python
# 模型层次结构
OpAmpModel (抽象基类)
├── IdealOpAmpModel      # 理想运放（E元件实现）
└── RealOpAmpModel       # 真实SPICE模型

# 工厂模式创建
OpAmpModelFactory.create_model({
    'model': 'OPAx205A',
    'include_file': 'spice_models/OPAx205A.LIB',
    'power_pins': True
})
```

**预定义模型库：**
- OPAx205A：精密运放
- AD8622：低噪声双运放
- OPA1611：音频运放

**4.2 ReLU模型 (relu_models.py)**

三种ReLU实现策略：

```python
ReluModel (抽象基类)
├── NoReluModel         # 直接连接（无激活）
├── OpAmpReluModel      # 运放实现（精确）
└── DiodeClampReluModel # 二极管钳位（简单）
```

**关键特性：**
- 可配置钳位电压（不仅限于0V）
- 支持增益调整
- 理论与实际模型对比

### 电路设计模式

**神经形态电路实现**
- ReLU电路使用二极管-运放配置进行整流
- 全连接层实现带符号权重的差分电流求和
- 支持偏置添加和级联ReLU激活
- 使用E96标准元件值进行实际实现

**仿真工作流程**
1. 通过继承`BaseCircuit`定义电路
2. 使用元件模型生成网表
3. 通过`CircuitSimulation`执行仿真
4. 理论模型与SPICE模型结果比较
5. 可视化和分析

**模型集成**
- 运放模型：支持各种运放SPICE模型（OPA1611、OPAx205A等）
- 元件库：带容差建模的标准无源元件
- 工艺变化：制造变化的统计分析

### NGspice集成

**第三方依赖: 本地NGspice**
- `Spice64/`目录中的捆绑NGspice安装
- 预配置OSDI设备模型
- 包含示例电路和模型

**仿真执行**
- 自动网表生成和仿真
- 原始文件解析和数据提取
- 错误处理和仿真调试

## 常见工作流程

### 实现新的电路类型
1. 从`circuit_base.py`中的`BaseCircuit`继承
2. 实现`get_circuit_netlist()`方法
3. 定义元件值和连接
4. 添加用于比较的理论模型
5. 按照`test_*.py`模式创建测试文件

### 运行电路分析
```python
from simulation import CircuitSimulation
from circuit_relu import PositiveReluCircuit

# 创建仿真环境
sim = CircuitSimulation(output_folder='./temp')

# 定义电路
circuit = PositiveReluCircuit(gain=1.0, R_value=10e3)

# 使用输入信号运行仿真
result = sim.run_simulation(t, input_signal, circuit)
```

### 批量仿真示例
```python
# 并行运行多个仿真
results = sim.run_batch_simulations(
    input_signals_list,  # 输入信号列表
    circuits_list,       # 电路列表
    truncate_lengths=True  # 自动截断到最短长度
)

# 结果包含每个仿真的详细信息
for idx, result in results.items():
    print(f"仿真 {idx}: 最大误差 = {result['max_diff']}")
```

### 使用不同的运放模型
```python
# 理想运放
circuit = PositiveReluCircuit(
    opamp_config={'model': 'ideal'}
)

# 真实运放模型
circuit = PositiveReluCircuit(
    opamp_config={
        'model': 'OPAx205A',
        'include_file': 'spice_models/OPAx205A.LIB'
    }
)
```

### 创建自定义全连接层
```python
from circuit_dense import DenseCircuit
import numpy as np

# 定义权重矩阵 (输入数 × 输出数)
weights = np.array([
    [1.0, -0.5],   # 第一个输入的权重
    [-0.8, 1.2]    # 第二个输入的权重
])

# 创建带ReLU的全连接层
circuit = DenseCircuit(
    gains=weights,
    use_relu=True,
    use_e96=True  # 使用标准电阻值
)
```

## 扩展框架

### 添加新的运放模型
1. 在`OpAmpModelFactory.MODEL_CONFIGS`中添加配置
2. 提供SPICE模型文件路径
3. 指定是否需要电源引脚

### 实现新的激活函数
1. 继承`ReluModel`基类
2. 实现`get_netlist_text()`和`modify_output_signals()`
3. 在`ReluModelFactory`中注册新类型