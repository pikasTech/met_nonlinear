# SPICE/NumPy/NN推理相位统一实施计划（修订版）

## 需求分析

1. **电路仿真结果相位修正**：确保SPICE仿真结果经过post_process处理后与NN一致
2. **NumPy仿真相位统一**：检查并修正NumPy仿真的相位，使其与NN一致  
3. **添加NumPy仿真输出**：在`cli.py -i`时生成numpy_layers目录，格式与nn_layers/spice_layers一致

## 现状分析

### 相位处理现状

1. **NN推理**：
   - 使用IIR滤波器，输出标准的HP/BP/LP响应
   - 不调用post_process方法
   - 所有通道输出应该是正相

2. **SPICE推理**：
   - 电路仿真后调用post_process
   - SVFLayer.post_process对HP(j%3==0)和LP(j%3==2)进行反相
   - 理论上应该与NN一致

3. **NumPy仿真**（circuit_svf.py第421-423行）：
   ```python
   out1[j] = -hp  # 高通输出（已反相）
   out2[j] = bp   # 带通输出  
   out3[j] = -lp  # 低通输出（已反相）
   ```
   - HP和LP已经包含负号，与SPICE电路行为一致
   - 如果再经过post_process，会导致双重反相

## 代码重构：将推理逻辑从cli.py分离

### 新增文件：inference/manager.py

创建InferenceManager类，负责管理推理和误差分析功能：

```python
"""
推理管理器模块

管理项目的推理数据生成和误差分析功能
"""
import os
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .processor import InferenceProcessor
from .data_processing import WaveProcessor
from calibration_analyzer.wavedata import WaveData

class InferenceManager:
    """
    推理管理器
    
    负责：
    - 生成神经网络推理数据
    - 生成SPICE仿真数据
    - 生成NumPy仿真数据
    - 分析推理误差
    - 生成对比报告
    """
    
    def __init__(self, project_manager):
        self.project = project_manager
        self.project_name = project_manager.project_name
        self.checkpoint_dir = project_manager.checkpoint_dir
        self.config = project_manager.config
        self.model = None  # 延迟加载
        
    def run_inference(self):
        """运行推理数据生成（原run_inference）"""
        # 原有逻辑
        
    def analyze_errors(self):
        """运行误差分析（原analyze_errors）"""
        # 原有逻辑
        
    def _generate_inference_data(self, data_dir):
        """生成推理数据（原_generate_inference_data，增加numpy支持）"""
        # 修改后的逻辑，支持numpy
        
    # 其他私有方法...
```

### 修改cli.py

简化ProjectManager类，委托推理功能给InferenceManager：

```python
from inference.manager import InferenceManager

class ProjectManager:
    def __init__(self, project_path):
        # 原有初始化代码...
        self._inference_manager = None  # 延迟创建
    
    @property
    def inference_manager(self):
        """延迟创建推理管理器"""
        if self._inference_manager is None:
            self._inference_manager = InferenceManager(self)
        return self._inference_manager
    
    def run_inference(self):
        """委托给推理管理器"""
        self.inference_manager.run_inference()
    
    def analyze_errors(self):
        """委托给推理管理器"""
        self.inference_manager.analyze_errors()
```

## 实施方案

### 1. 修正NumPy仿真相位（需求2）

**文件：`spice_simulator/circuit_svf.py`**

**修改点：simulate_numpy方法（第420-423行）**

```python
# 原代码
out1[j] = -hp  # 高通输出
out2[j] = bp   # 带通输出
out3[j] = -lp  # 低通输出

# 修改为
out1[j] = hp   # 高通输出（不反相，让post_process统一处理）
out2[j] = bp   # 带通输出
out3[j] = lp   # 低通输出（不反相，让post_process统一处理）
```

**理由**：让NumPy仿真与SPICE电路保持一致的处理流程，相位修正统一由post_process负责。

### 2. 添加NumPy仿真支持（需求3）

#### 2.1 修改SPICEBackend类

**文件：`inference/inference_backends.py`**

**修改点1：添加numpy仿真方法（在simulate_with_spice后添加）**

```python
def simulate_with_numpy(self, 
                       circuit_obj,
                       input_wave_data: WaveData,
                       output_name: str = "numpy_simulation_result") -> WaveData:
    """
    使用NumPy进行电路仿真
    """
    # 检查电路是否支持numpy仿真
    if not hasattr(circuit_obj, 'simulate_numpy'):
        raise ValueError(f"电路对象 {type(circuit_obj).__name__} 不支持NumPy仿真")
    
    # 创建输出WaveData
    output_wave_data = WaveData(
        description=f"NumPy仿真结果 - {output_name}",
        author="NumPy Simulation"
    )
    
    # 对每个输入记录进行仿真
    for record in input_wave_data.records:
        # 获取时间向量和输入信号
        t = record.get_time_axis()
        input_signal = record.data
        
        # 执行numpy仿真
        output_signal = circuit_obj.simulate_numpy(t, input_signal)
        
        # 创建输出记录
        channel_names = []
        for i in range(output_signal.shape[1]):
            ch_type = ['HP', 'BP', 'LP'][i % 3]
            ch_num = i // 3
            channel_names.append(f"{ch_type}{ch_num}")
        
        output_record = WaveRecord(
            data=output_signal,
            sample_rate=record.sample_rate,
            channel_names=channel_names,
            record_id=f"{record.record_id}_numpy",
            user_metadata={**record.user_metadata, "simulation_type": "numpy"}
        )
        output_wave_data.add_record(output_record)
    
    # 应用post_process（如果存在）
    if hasattr(circuit_obj, 'post_process'):
        output_wave_data = circuit_obj.post_process(output_wave_data)
    
    return output_wave_data
```

**修改点2：在infer方法中添加numpy仿真选项（第701-754行）**

在处理多层模型的循环中，同时进行numpy仿真：

```python
# 创建三个结果列表
layer_results_spice = []  # SPICE仿真结果
layer_results_numpy = []  # NumPy仿真结果

for i, spice_obj in enumerate(spice_model):
    # SPICE仿真（原有代码）
    layer_output_spice = self.simulate_with_spice(...)
    
    # NumPy仿真（新增）
    if hasattr(spice_obj, 'simulate_numpy'):
        layer_output_numpy = self.simulate_with_numpy(
            spice_obj, current_input, output_name=f"layer{i+1}")
        layer_results_numpy.append(layer_output_numpy)
    
    # 保存结果...
```

#### 2.2 修改InferenceManager

**文件：`inference/manager.py`（新文件）**

**修改点：_generate_inference_data方法（从cli.py迁移并增强）**

```python
# 创建输出目录
nn_layers_dir = os.path.join(data_dir, 'nn_layers')
spice_layers_dir = os.path.join(data_dir, 'spice_layers')
numpy_layers_dir = os.path.join(data_dir, 'numpy_layers')  # 新增

# SPICE分层推理（修改以支持numpy）
processor.set_backend("spice")
processor.backend_type = "spice"
processor._initialize_backend("spice")

# 修改SPICEBackend以同时返回numpy结果
# 这需要在SPICEBackend.infer中添加return_numpy参数
input_data = processor.load_input_wave(input_wave)
results = processor.backend.infer(input_data, use_scaler=True, 
                                  return_layers=True, 
                                  return_numpy=True)  # 新增参数

# 解析返回结果
if isinstance(results, dict):
    spice_outputs = results['spice']
    numpy_outputs = results.get('numpy', [])
else:
    spice_outputs = results
    numpy_outputs = []

# 保存SPICE输出（原有代码）
os.makedirs(spice_layers_dir, exist_ok=True)
for i, layer_output in enumerate(spice_outputs):
    layer_path = os.path.join(spice_layers_dir, f"layer_{i+1}.wave")
    processor.wave_processor.save_waveform(layer_path, layer_output)

# 保存NumPy输出（新增）
if numpy_outputs:
    os.makedirs(numpy_layers_dir, exist_ok=True)
    for i, layer_output in enumerate(numpy_outputs):
        layer_path = os.path.join(numpy_layers_dir, f"layer_{i+1}.wave")
        processor.wave_processor.save_waveform(layer_path, layer_output)
    print(f"NumPy仿真完成，保存了 {len(numpy_outputs)} 个文件")
```

### 3. 相位验证（需求1）

为确保相位修正正确，在`_analyze_inference_errors`中添加相位检测代码：

**文件：`inference/manager.py`**

**修改点：_analyze_inference_errors方法（从cli.py迁移并添加相位检测）**

```python
# 在分析第一层时检测相位
if i == 0:  # SVF层
    print("  检测SVF层各通道相位...")
    for ch in range(min(6, nn_data.records[0].data.shape[1])):
        nn_ch = nn_data.records[0].data[:1000, ch]  # 取前1000个样本
        spice_ch = spice_data.records[0].data[:1000, ch]
        
        # 计算相关系数
        if len(nn_ch) > 0 and len(spice_ch) > 0:
            corr = np.corrcoef(nn_ch, spice_ch)[0, 1]
            ch_type = ['HP', 'BP', 'LP'][ch % 3]
            ch_num = ch // 3
            print(f"    通道{ch} ({ch_type}{ch_num}): 相关系数 = {corr:.3f}")
```

## 文件修改清单（修订版）

### 新增文件

1. **inference/manager.py**（新增约500行）
   - 创建InferenceManager类
   - 从cli.py迁移所有推理相关方法
   - 增强_generate_inference_data支持numpy输出
   - 增强_analyze_inference_errors添加相位检测

### 修改文件

1. **spice_simulator/circuit_svf.py**
   - 修改simulate_numpy方法，去除HP/LP的负号（3行）

2. **inference/inference_backends.py**
   - 添加simulate_with_numpy方法（约40行）
   - 修改infer方法支持numpy仿真（约20行修改）
   - 添加return_numpy参数处理（约10行）

3. **cli.py**
   - 删除所有推理相关方法（减少约300行）
   - 添加inference_manager属性（约10行）
   - 修改run_inference和analyze_errors委托调用（约10行）

4. **inference/__init__.py**
   - 添加InferenceManager导出（1行）

## 实施步骤（修订版）

1. **第一步**：创建inference/manager.py，迁移推理逻辑
2. **第二步**：修改cli.py，使用InferenceManager
3. **第三步**：修改circuit_svf.py的simulate_numpy方法
4. **第四步**：在SPICEBackend中添加numpy仿真支持
5. **第五步**：在InferenceManager中支持numpy输出
6. **第六步**：测试验证相位一致性

## InferenceManager的详细设计

### 方法迁移对应关系

从cli.py迁移到inference/manager.py的方法：

| 原方法名 | 新位置 | 修改内容 |
|---------|--------|----------|
| run_inference | InferenceManager.run_inference | 保持不变 |
| analyze_errors | InferenceManager.analyze_errors | 保持不变 |
| _validate_inference_prerequisites | InferenceManager._validate_inference_prerequisites | 保持不变 |
| _check_existing_inference_data | InferenceManager._check_existing_inference_data | 增加numpy_layers检查 |
| _find_input_file | InferenceManager._find_input_file | 保持不变 |
| _generate_inference_data | InferenceManager._generate_inference_data | 增加numpy仿真支持 |
| _analyze_inference_errors | InferenceManager._analyze_inference_errors | 增加相位检测，支持numpy |
| _generate_analysis_report | InferenceManager._generate_analysis_report | 保持不变 |
| _generate_visualization | InferenceManager._generate_visualization | 保持不变 |
| _combine_layer_outputs | InferenceManager._combine_layer_outputs | 保持不变 |
| _get_timestamp | InferenceManager._get_timestamp | 保持不变 |

### 依赖处理

InferenceManager需要访问：
- `self.project.model` - 模型对象
- `self.project.state_manager` - 状态管理器
- `self.project.checkpoint_dir` - 检查点目录
- `self.project.config` - 配置对象

## 预期结果

执行`python cli.py -i`后，输出目录结构：

```
projects/WNET5q0.5h2u6l3/data/inference/
├── nn_layers/
│   └── layer_1.wave ... layer_5.wave
├── spice_layers/
│   └── layer_1.wave ... layer_5.wave
├── numpy_layers/        # 新增
│   └── layer_1.wave ... layer_5.wave
├── input.wave
└── inference_metadata.json
```

所有三种推理方式的输出相位应该完全一致。

## 代码修改量统计（修订版）

- 新增文件：1个（inference/manager.py，约500行）
- 修改文件：4个
- 净增代码量：约300行（新增500行，删除200行）
- 风险等级：中低（主要是代码重构和功能增强）

## 优势

1. **代码组织更清晰**：推理逻辑独立于项目管理
2. **可扩展性更好**：便于添加新的推理后端
3. **测试更容易**：InferenceManager可以独立测试
4. **符合项目架构**：与ModelEngine等核心类的设计保持一致

## 注意事项

1. NumPy仿真只适用于支持simulate_numpy方法的电路（如SVFFilter）
2. Dense层等其他电路可能需要单独实现simulate_numpy方法
3. 需要确保post_process在所有仿真路径中都被正确调用