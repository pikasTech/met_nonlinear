# WNET5频率响应理论计算计划（EP框架集成）

## 原始需求与背景

### 1. 项目背景
目前已经将 WNET5 的电路做出来了，然后我现在需要对电路进行测试，为了测试电路的设计是否符合预期，我设计了频率响应测试法，即在 SVF 层之前输入扫频信号，然后测量 SVF 层 + Dense 层（第一层）的 RELU 前的波形输出，对 RELU 前的波形 vs 输入波形进行频率响应分析，我目前已经测量了实际电路板的频率响应，我需要再通过仿真来计算出 WNET5 理论上的频率响应，来进行对比。

### 2. 核心任务
**通过仿真来计算出 WNET5 SVF 层 + Dense 层（第一层）的 RELU 前的波形输出 理论上的频率响应**

### 3. 技术路线
按照一个简化的传递函数仿真思路来仿真，因为到RELU之前都是线性系统，所以可以直接提取WNET5的SVF层的每个SVF通道的传递函数，然后通过DENSE层的加权权重，来对SVF的传递函数的每个通道做**传递函数**上的加权计算，得到DENSE的每个输出的权重函数，全程采用频率域分析法，不使用时域波形分析法。

## EP框架集成目标

**主要目标**：将WNET5频率响应理论计算功能集成到EP框架，作为独立的外部项目任务类型进行管理。

**技术路线**：
1. 扩展EP框架，新增`wnet5-circuit-validation`任务类型（专用于WNET5电路验证）
2. 实现基于传递函数的纯频域分析方法
3. 提供标准化的配置模板和自动化执行流程
4. 支持理论与实测数据的对比可视化

## EP框架集成方案

### 1. 任务类型扩展

#### 1.1 添加新任务类型支持
在`core/visualization_path_parser.py`中扩展支持的任务类型：

```python
class VisualizationPathParser:
    """可视化路径解析器"""
    'freq-response-compare',
    'bias-visualization', 
    'waveform-analysis',
    'wnet5-circuit-validation',  # 新增：WNET5电路验证
    'external-circuit-validation'  # 新增：外部电路验证
        'waveform-analysis',
        'wnet5-circuit-validation'  # 新增：WNET5电路验证
    ]
```

#### 1.2 EP命令使用示例
```bash
# 创建WNET5频率响应分析项目
python cli.py ep ep_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3
python cli.py ep projects/WNET5_project/external/wnet5-circuit-validation/svf-dense-analysis

# 支持的路径格式
python cli.py ep projects/WNET5_project/external/wnet5-circuit-validation/svf-dense-analysis
python cli.py ep external/projects/wnet5-circuit-validation/WNET5_theoretical_vs_measured
```

### 2. 配置模板设计

#### 2.1 配置模板结构
在`core/external_cli_handler.py`中添加模板生成器：

```python
def _create_wnet5_circuit_validation_template(ep_path: ExternalPath) -> dict:
    """创建WNET5电路验证配置模板（EP）"""
    return {
        "task_info": {
            "task_type": "wnet5-circuit-validation",
            "description": "WNET5电路频率响应理论验证"
        },
        "model_project_name": ep_path.project_name,
        "frequency_range": {
            "start_freq": 0.1,
            "stop_freq": 1000
        }
    }
```

### 3. 目录结构规范

#### 3.1 项目目录组织
```
ep_projects/{domain}/{task_type}/{task_name}/
├── config.json                    # 任务配置文件
└── data/                          # 输出目录（EP统一）
    ├── numerics/                  # 数值产物（传递函数/频响等JSON/NPZ）
    │   ├── transfer_functions/
    │   │   ├── svf_hp_0.json
    │   │   ├── svf_bp_0.json
    │   │   ├── svf_lp_0.json
    │   │   └── combined_output_0.json
    │   └── frequency_response/
    │       ├── theoretical.json
    │       └── comparison.json
    ├── plots/
    │   ├── bode_plot.png
    │   ├── nyquist_plot.png
    │   └── comparison_plot.png
    ├── reports/
    │   └── analysis_report.md
    └── task_metadata.json
```

#### 3.2 独立可视化项目支持
```
visualization/projects/
└── wnet5-circuit-validation/
    └── {task_name}/                          # 如: WNET5_vs_measured_batch_comparison
        ├── config.json
        └── output/
```

### 4. 可视化引擎实现

#### 4.1 执行器集成
在`core/external_cli_handler.py`中添加执行器：

```python
def _execute_task(ep_path: ExternalPath) -> bool:
    """执行 EP 任务"""
    try:
        # 加载配置
        config = _load_config(ep_path.config_path)
        validated_config = _validate_config(config, ep_path.task_type)
        
        # 根据任务类型选择执行器
        if ep_path.task_type == 'freq-response-compare':
            return _execute_freq_response_task(ep_path, validated_config)
        elif ep_path.task_type == 'wnet5-circuit-validation':  # 新增
            return _execute_transfer_function_task(ep_path, validated_config)
        # ... 其他任务类型
        
    except Exception as e:
        logger.error(f"任务执行失败: {e}")
        return False
```

#### 4.2 传递函数分析执行器
```python
def _execute_transfer_function_task(ep_path: ExternalPath, config: dict) -> bool:
    """执行WNET5电路验证任务（EP）"""
    try:
        # 导入WNET5电路验证分析引擎
        from visualization.wnet5_circuit_validator import WNET5CircuitValidator
        
        # 创建验证器实例
        validator = WNET5CircuitValidator(
            config=config,
            output_dir=ep_path.output_path
        )
        
        # 执行验证流程
        results = validator.execute_validation()
        
        if results['success']:
            logger.info(f"WNET5电路验证完成")
            logger.info(f"生成文件: {results['output_files']}")
            
            # 保存任务元数据
            _save_task_metadata(ep_path, config, results['main_output'])
            return True
        else:
            logger.error(f"验证失败: {results['error']}")
            return False
            
    except ImportError as e:
        logger.error(f"无法导入WNET5电路验证模块: {e}")
        return False
    except Exception as e:
        logger.error(f"WNET5电路验证任务执行失败: {e}")
        return False
```

### 5. WNET5电路验证引擎

#### 5.1 验证引擎架构
创建`visualization/wnet5_circuit_validator.py`（作为 EP 任务执行器之一）：

```python
class WNET5CircuitValidator:
    """WNET5电路验证引擎"""
    
    def __init__(self, config: dict, output_dir: Path):
        self.config = config
        self.output_dir = Path(output_dir)
        self.model_project_name = config['model_project_name']
        self.frequency_range = config['frequency_range']
        
        # 确保输出目录存在
        self._setup_output_directories()
    
    def execute_validation(self) -> dict:
        """执行完整验证流程"""
        try:
            # 1. 加载模型和提取参数
            model = self._load_model()
            svf_params = self._extract_svf_parameters(model)
            dense_weights = self._extract_dense_weights(model)
            
            # 2. 计算传递函数
            svf_tfs = self._calculate_svf_transfer_functions(svf_params)
            combined_tfs = self._calculate_combined_transfer_functions(svf_tfs, dense_weights)
            
            # 3. 计算频率响应
            freq_response = self._calculate_frequency_response(combined_tfs)
            
            # 4. 可视化和报告生成
            plots = self._generate_plots(freq_response)
            report = self._generate_analysis_report(svf_params, dense_weights, freq_response)
            
            # 5. 保存结果（数值存于 data/numerics）
            self._save_results(svf_tfs, combined_tfs, freq_response)
            
            return {
                'success': True,
                'output_files': plots + [report],
                'main_output': plots[0] if plots else report
            }
            
        except Exception as e:
            logger.error(f"验证执行失败: {e}")
            return {'success': False, 'error': str(e)}
```

#### 5.2 核心计算模块
```python
class SVFTransferFunctionExtractor:
    """SVF传递函数提取器"""
    
    @staticmethod
    def extract_from_model(model, config: dict) -> dict:
        """从WNET5模型中提取SVF参数"""
        center_freqs = model.subcfg['init_center_freqs']
        quality_factors = model.subcfg['init_quality_factors']
        
        return {
            'center_freqs': center_freqs,
            'quality_factors': quality_factors,
            'num_svf': len(center_freqs)
        }
    
    @staticmethod
    def calculate_transfer_functions(svf_params: dict) -> list:
        """计算SVF传递函数"""
        import sympy as sp
        s = sp.Symbol('s')
        
        transfer_functions = []
        for f0, Q in zip(svf_params['center_freqs'], svf_params['quality_factors']):
            omega0 = 2 * sp.pi * f0
            denominator = s**2 + (omega0/Q)*s + omega0**2
            
            H_hp = s**2 / denominator
            H_bp = (s * omega0/Q) / denominator  
            H_lp = omega0**2 / denominator
            
            transfer_functions.append({
                'high_pass': H_hp,
                'band_pass': H_bp,
                'low_pass': H_lp,
                'parameters': {'f0': f0, 'Q': Q}
            })
        
        return transfer_functions

class DenseWeightExtractor:
    """Dense层权重提取器"""
    
    @staticmethod
    def extract_from_model(model, config: dict) -> dict:
        """提取Dense层权重矩阵"""
        # 利用现有的UnifiedResistanceCalculator
        from spice_simulator.unified_resistance_calculator import UnifiedResistanceCalculator
        
        calculator = UnifiedResistanceCalculator(model)
        layer_index = config.get('layer_index', 0)
        
        # 获取第一个Dense层
        dense_layer = None
        for i, layer in enumerate(model.layer_to_layer_models):
            if hasattr(layer, 'get_weights'):
                if i == layer_index:
                    dense_layer = layer
                    break
        
        if dense_layer is None:
            raise ValueError(f"未找到索引为{layer_index}的Dense层")
        
        weights = dense_layer.get_weights()
        weight_matrix = weights[0]
        bias_vector = weights[1] if len(weights) > 1 else None
        
        # 处理Conv1D权重形状
        if len(weight_matrix.shape) == 3 and weight_matrix.shape[0] == 1:
            weight_matrix = weight_matrix.squeeze(axis=0)
        
        return {
            'weight_matrix': weight_matrix,
            'bias_vector': bias_vector,
            'shape': weight_matrix.shape,
            'layer_name': dense_layer.name if hasattr(dense_layer, 'name') else f'dense_layer_{layer_index}'
        }
```

### 6. 工作流程

#### 6.1 典型使用流程
```bash
# 1. 创建传递函数分析项目（首次运行）
python cli.py ep WNET5_project/wnet5-circuit-validation/theoretical-analysis

# 系统自动创建配置模板并提示：
# ✅ 配置模板已创建
# 📋 请编辑配置文件后重新运行相同命令
#    配置文件位置: projects/WNET5_project/visualization/wnet5-circuit-validation/theoretical-analysis/config.json

# 2. 编辑配置文件（设置模型路径、分析参数等）

# 3. 执行分析（二次运行）
python cli.py ep WNET5_project/wnet5-circuit-validation/theoretical-analysis

# 系统执行分析并输出：
# 🚀 执行可视化任务...
# ✅ 任务执行完成
#    输出目录: projects/WNET5_project/visualization/wnet5-circuit-validation/theoretical-analysis/output
```

#### 6.2 独立项目模式（可选）
```bash
# 批量对比分析（独立于训练项目）
python cli.py ep visualization/projects/wnet5-circuit-validation/WNET5_batch_comparison
```

### 7. 技术优势

#### 7.1 EP 框架集成优势
- **工程化管理**：利用EP的标准化项目结构和配置管理
- **智能执行**：自动模板生成和智能执行逻辑
- **扩展性强**：模块化设计便于添加新的分析类型
- **向后兼容**：完全兼容现有CLI命令体系

#### 7.2 传递函数计算优势
- **纯频域分析**：避免复杂的时域SPICE仿真
- **数学精确性**：基于符号计算的严格理论分析
- **计算效率**：1分钟内完成全频段分析
- **结果可重现**：完全确定性的计算过程

#### 7.3 可视化输出优势
- **标准化格式**：统一的JSON数据格式和可视化输出
- **多种图表类型**：Bode图、Nyquist图、阶跃响应等
- **对比分析**：理论与实测数据的直观对比
- **详细报告**：自动生成的分析报告和元数据

### 8. 实施步骤

#### 8.1 阶段一：EP 框架扩展（Week 1）
1. **扩展任务类型支持**
    - 修改`core/external_path_parser.py`
   - 添加`wnet5-circuit-validation`任务类型

2. **添加配置模板生成器**
    - 在`core/external_cli_handler.py`中实现`_create_transfer_function_template()`
   - 集成到`create_visualization_template()`函数

3. **添加任务执行器**
   - 实现`_execute_transfer_function_task()`函数
   - 集成到`_execute_task()`分发器

#### 8.2 阶段二：分析引擎开发（Week 2）
1. **创建分析引擎模块**
   - 实现`visualization/transfer_function_analyzer.py`
   - 实现SVF传递函数提取器
   - 实现Dense权重提取器

2. **核心计算算法**
   - 传递函数组合计算
   - 频率响应计算
   - 数值稳定性处理

#### 8.3 阶段三：可视化和报告（Week 3）
1. **图表生成器**
   - Bode图生成
   - Nyquist图生成  
   - 对比分析图表

2. **报告生成器**
   - Markdown格式分析报告
   - 参数汇总和结果统计
   - 元数据管理

#### 8.4 阶段四：测试和文档（Week 4）
1. **功能测试**
   - 端到端工作流程测试
   - 错误处理和边界情况测试
   - 性能基准测试

2. **文档完善**
   - 用户使用指南
   - 配置参数说明
   - 故障排除指南

### 9. 成功标准

1. **框架集成**：成功集成到EP框架，命令格式统一
2. **配置管理**：自动模板生成和智能执行工作正常
3. **计算精度**：传递函数计算结果数学正确
4. **可视化质量**：生成高质量的分析图表和报告
5. **用户体验**：命令简洁，错误提示清晰，文档完善

## 结论

将WNET5频率响应理论计算功能集成到EP框架中，充分利用了现有的工程化基础设施，实现了标准化的项目管理和自动化执行流程。该方案不仅提供了强大的传递函数分析能力，还保持了与现有工具链的完美兼容性，为后续功能扩展奠定了良好基础。

通过EP框架的智能执行机制，用户只需一个简单的命令即可完成从配置创建到结果生成的全部流程，大大简化了复杂理论分析的操作难度，提高了工作效率。

## 技术方案

### 1. SVF传递函数提取

#### 1.1 从WNET5模型参数获取SVF传递函数
根据`models/wavenet_models.py`中的定义，WNET5的SVF层已有完整的传递函数表达式：

```python
# SVF传递函数（基于center_freqs和quality_factors）
def get_svf_transfer_functions(center_freqs, quality_factors):
    """
    提取SVF各通道传递函数
    
    Returns:
        List[Tuple]: [(H_hp, H_bp, H_lp), ...] 每个SVF的三个传递函数
    """
    import sympy as sp
    s = sp.Symbol('s')
    
    transfer_functions = []
    for f0, Q in zip(center_freqs, quality_factors):
        omega0 = 2 * sp.pi * f0
        
        # 标准SVF传递函数
        denominator = s**2 + (omega0/Q)*s + omega0**2
        
        H_hp = s**2 / denominator                    # 高通
        H_bp = (s * omega0/Q) / denominator          # 带通  
        H_lp = omega0**2 / denominator               # 低通
        
        transfer_functions.append((H_hp, H_bp, H_lp))
    
    return transfer_functions
```

#### 1.2 SVF参数提取方法
```python
# 从WNET5模型中提取SVF参数
def extract_svf_parameters(model):
    """
    从WaveNet5模型中提取SVF层参数
    
    Returns:
        Tuple: (center_freqs, quality_factors)
    """
    center_freqs = model.subcfg['init_center_freqs']  # [10, 30, 60, 100]
    quality_factors = model.subcfg['init_quality_factors']  # [1.0, 1.0, 1.0, 1.0]
    
    return center_freqs, quality_factors
```

### 2. Dense层权重矩阵获取

#### 2.1 权重提取方法
基于`spice_simulator/unified_resistance_calculator.py`的现有实现：

```python
def extract_dense_weights(model):
    """
    提取Dense层（第一层）的权重矩阵
    
    Returns:
        Tuple: (weight_matrix, bias_vector)
    """
    # 获取第一个Dense层（post_dense_1）
    dense_layer = None
    for layer in model.layer_to_layer_models:
        if isinstance(layer, DenseLayer):
            dense_layer = layer
            break
    
    if dense_layer is None:
        raise ValueError("未找到Dense层")
    
    # 获取权重和偏置
    weights = dense_layer.get_weights()
    weight_matrix = weights[0]  # Shape: (input_channels, output_channels)
    bias_vector = weights[1] if len(weights) > 1 else None
    
    # 处理Conv1D权重形状（kernel_size=1）
    if len(weight_matrix.shape) == 3 and weight_matrix.shape[0] == 1:
        weight_matrix = weight_matrix.squeeze(axis=0)
    
    return weight_matrix, bias_vector
```

### 3. 传递函数组合计算

#### 3.1 加权传递函数计算
```python
def calculate_combined_transfer_function(svf_transfer_functions, weight_matrix):
    """
    计算SVF+Dense组合传递函数
    
    Args:
        svf_transfer_functions: SVF各通道传递函数列表
        weight_matrix: Dense层权重矩阵 (n_inputs, n_outputs)
        
    Returns:
        List: 每个输出通道的组合传递函数
    """
    import sympy as sp
    
    # 展开所有SVF通道的传递函数
    all_svf_channels = []
    for H_hp, H_bp, H_lp in svf_transfer_functions:
        all_svf_channels.extend([H_hp, H_bp, H_lp])
    
    # 对每个输出通道计算加权组合
    output_transfer_functions = []
    for output_idx in range(weight_matrix.shape[1]):
        # 加权求和：H_out = Σ(w_i * H_svf_i)
        H_combined = 0
        for input_idx, H_svf in enumerate(all_svf_channels):
            weight = weight_matrix[input_idx, output_idx]
            H_combined += weight * H_svf
        
        output_transfer_functions.append(H_combined)
    
    return output_transfer_functions
```

#### 3.2 频率响应计算
```python
def calculate_frequency_response(transfer_function, frequencies):
    """
    计算传递函数的频率响应
    
    Args:
        transfer_function: 符号传递函数
        frequencies: 频率点数组 (Hz)
        
    Returns:
        Tuple: (magnitude_db, phase_deg)
    """
    import numpy as np
    import sympy as sp
    
    s = sp.Symbol('s')
    
    # 将频率转换为复数形式 s = jω
    omega = 2 * np.pi * frequencies
    s_vals = 1j * omega
    
    # 将符号传递函数转换为数值函数
    H_func = sp.lambdify(s, transfer_function, 'numpy')
    
    # 计算频率响应
    H_response = H_func(s_vals)
    
    # 计算幅度和相位
    magnitude = np.abs(H_response)
    magnitude_db = 20 * np.log10(magnitude + 1e-12)  # 防止log(0)
    phase_rad = np.angle(H_response)
    phase_deg = np.degrees(phase_rad)
    
    return magnitude_db, phase_deg
```

### 4. 实施步骤

#### 4.1 阶段一：传递函数提取与验证
1. **SVF传递函数提取**
   ```bash
   python cli.py --project wavenet5_freq_analysis --extract-svf-params
   ```

2. **Dense权重提取**
   ```bash
   python cli.py --project wavenet5_freq_analysis --extract-dense-weights
   ```

#### 4.2 阶段二：传递函数组合计算
1. **组合传递函数计算**
   ```python
   # 核心计算流程
   def main_frequency_analysis():
       # 1. 加载模型
       model = load_wavenet5_model(checkpoint_path)
       
       # 2. 提取SVF参数
       center_freqs, quality_factors = extract_svf_parameters(model)
       
       # 3. 计算SVF传递函数
       svf_tfs = get_svf_transfer_functions(center_freqs, quality_factors)
       
       # 4. 提取Dense权重
       weight_matrix, bias = extract_dense_weights(model)
       
       # 5. 计算组合传递函数
       combined_tfs = calculate_combined_transfer_function(svf_tfs, weight_matrix)
       
       # 6. 计算频率响应
       frequencies = np.logspace(-1, 3, 1000)  # 0.1Hz to 1kHz
       for i, H_combined in enumerate(combined_tfs):
           mag_db, phase_deg = calculate_frequency_response(H_combined, frequencies)
           save_frequency_response(f"output_channel_{i}", frequencies, mag_db, phase_deg)
   ```

#### 4.3 阶段三：结果分析与可视化
1. **Bode图生成**
   ```python
   def plot_frequency_response(frequencies, magnitude_db, phase_deg, title):
       fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
       
       # 幅频响应
       ax1.semilogx(frequencies, magnitude_db)
       ax1.set_ylabel('幅度 (dB)')
       ax1.grid(True)
       ax1.set_title(f'{title} - 幅频响应')
       
       # 相频响应
       ax2.semilogx(frequencies, phase_deg)
       ax2.set_xlabel('频率 (Hz)')
       ax2.set_ylabel('相位 (度)')
       ax2.grid(True)
       ax2.set_title(f'{title} - 相频响应')
       
       plt.tight_layout()
       plt.savefig(f'{title}_bode_plot.png', dpi=300)
   ```

### 5. 集成现有基础设施

#### 5.1 CLI命令扩展
```python
# 在core/cli_parser.py中添加
parser.add_argument('--freq-analysis', action='store_true',
                   help='执行传递函数频率响应分析')
parser.add_argument('--freq-start', type=float, default=0.1,
                   help='分析起始频率')
parser.add_argument('--freq-stop', type=float, default=1000,
                   help='分析结束频率')
parser.add_argument('--freq-points', type=int, default=1000,
                   help='频率点数')
```

#### 5.2 任务分发器集成
```python
# 在core/task_dispatcher.py中添加
if args.freq_analysis:
    freq_config = {
        'start_freq': args.freq_start,
        'stop_freq': args.freq_stop,
        'num_points': args.freq_points
    }
    return project_manager.run_transfer_function_analysis(freq_config)
```

### 6. 输出数据结构

#### 6.1 数据格式设计
```
projects/wavenet5_freq_analysis/data/transfer_function/
├── svf_parameters.json           # SVF参数
├── dense_weights.npz            # Dense层权重
├── transfer_functions/
│   ├── svf_hp_0.json           # SVF高通传递函数
│   ├── svf_bp_0.json           # SVF带通传递函数  
│   ├── svf_lp_0.json           # SVF低通传递函数
│   └── combined_output_0.json   # 组合传递函数
├── frequency_response/
│   ├── output_channel_0.json    # 第一输出通道频率响应
│   └── bode_plots/
│       └── output_channel_0.png  # Bode图
└── analysis_report.md           # 分析报告
```

#### 6.2 传递函数数据格式
```json
{
  "metadata": {
    "type": "transfer_function",
    "svf_index": 0,
    "channel": "high_pass",
    "center_freq": 10.0,
    "quality_factor": 1.0
  },
  "transfer_function": {
    "symbolic": "s**2/(s**2 + 62.83*s + 3947.84)",
    "coefficients": {
      "numerator": [1, 0, 0],
      "denominator": [1, 62.83, 3947.84]
    }
  }
}
```

#### 6.3 频率响应数据格式
```json
{
  "metadata": {
    "channel": "output_0",
    "frequency_range": [0.1, 1000],
    "num_points": 1000,
    "calculation_method": "transfer_function"
  },
  "frequency_response": {
    "frequencies": [0.1, 0.15, 0.2, ...],
    "magnitude_db": [-3.2, -2.8, -2.1, ...], 
    "phase_deg": [15.2, 12.8, 8.9, ...],
    "gain_margin_db": 20.5,
    "phase_margin_deg": 45.2,
    "bandwidth_3db": 850.0
  }
}
```

### 7. 技术优势

#### 7.1 计算效率
- **纯代数计算**：无需数值仿真，计算速度快
- **符号计算精度**：避免数值误差积累
- **频域直接分析**：不需要时域到频域转换

#### 7.2 理论准确性
- **严格的线性系统分析**：基于经典控制理论
- **传递函数级联**：数学上精确的系统组合
- **参数一致性**：直接使用模型训练参数

#### 7.3 可扩展性
- **模块化设计**：SVF和Dense层独立计算
- **多输出支持**：同时分析所有输出通道
- **参数化分析**：可变频率范围和精度

### 8. 验证与对比

#### 8.1 理论vs实测对比指标
- **幅频响应匹配度**：各频点幅度误差统计
- **相频响应一致性**：相位差异分析
- **关键频率参数**：
  - 3dB带宽对比
  - 谐振频率位置
  - 增益裕度和相位裕度

#### 8.2 一致性验证方法
```python
def validate_theory_vs_measurement(theory_data, measurement_data):
    """
    理论与实测数据对比验证
    """
    # 插值到相同频率点
    common_freqs = np.logspace(-1, 3, 500)
    theory_interp = np.interp(common_freqs, theory_data['freqs'], theory_data['mag_db'])
    meas_interp = np.interp(common_freqs, measurement_data['freqs'], measurement_data['mag_db'])
    
    # 计算误差统计
    error_db = np.abs(theory_interp - meas_interp)
    rms_error = np.sqrt(np.mean(error_db**2))
    max_error = np.max(error_db)
    
    return {
        'rms_error_db': rms_error,
        'max_error_db': max_error,
        'correlation': np.corrcoef(theory_interp, meas_interp)[0,1]
    }
```

### 9. 预期挑战与解决方案

#### 9.1 符号计算复杂度
**挑战**：高阶传递函数的符号计算可能很慢
**解决方案**：
- 使用SymPy的简化功能
- 必要时转换为数值计算
- 缓存中间结果

#### 9.2 数值稳定性
**挑战**：传递函数在某些频率点可能不稳定
**解决方案**：
- 添加数值稳定性检查
- 使用合适的数值精度
- 对极值进行特殊处理

### 10. 成功标准

1. **计算完整性**：成功提取所有SVF和Dense层参数
2. **理论准确性**：传递函数数学表达式正确
3. **对比精度**：理论与实测频率响应误差 < 3dB（主要频段）
4. **计算效率**：全频段分析在1分钟内完成
5. **结果可重现**：多次计算结果完全一致

## 实施时间表

1. **Week 1**：传递函数提取算法开发，参数验证
2. **Week 2**：组合计算实现，频率响应分析算法
3. **Week 3**：CLI集成，可视化和报告生成
4. **Week 4**：实测对比，精度验证，文档完善

## 结论

基于传递函数的频域分析方法避免了复杂的时域SPICE仿真，直接从数学层面计算WNET5的理论频率响应。该方案具有计算效率高、理论精度好、实现简洁的优势，能够快速准确地获得频率响应特性，为电路设计验证提供可靠的理论基础。