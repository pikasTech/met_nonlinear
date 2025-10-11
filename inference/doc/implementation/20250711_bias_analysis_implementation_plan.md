# 偏置误差分析功能实施方案

## 概述

本文档详细说明了在 `cli.py -a` 命令中增加通道级偏置误差分析功能的具体实施方案。根据需求，将实现**稳态段提取法**和**频域滤波法**两种偏置计算方法，并通过pytest进行充分测试后再集成到主程序。

## 实施步骤

### 第一阶段：核心功能实现

#### 1. 新增文件

##### 1.1 `inference/analysis/bias_analyzer.py`
**用途**：实现偏置分析的核心算法
**主要内容**：
- `BiasAnalyzer` 基类，定义偏置分析接口
- `SteadyStateBiasAnalyzer` 类，实现稳态段提取法
- `FrequencyDomainBiasAnalyzer` 类，实现频域滤波法
- `AutoBiasAnalyzer` 类，根据信号特性自动选择方法

##### 1.2 `tests/inference/test_bias_analyzer.py`
**用途**：偏置分析功能的单元测试
**主要内容**：
- 测试稳态段提取法的各种场景
- 测试频域滤波法的各种场景
- 测试边界条件和异常情况
- 使用人造数据验证算法准确性

#### 2. 修改文件

##### 2.1 `inference/management/error_analyzer.py`
**修改点**：
- 导入 `bias_analyzer` 模块
- 在 `ErrorAnalyzer` 类中添加 `_analyze_channel_bias_errors()` 方法
- 在 `analyze_inference_errors()` 方法中调用偏置分析
- 在 `_compute_single_layer_error()` 中收集通道级数据
- 修改返回的分析结果结构，包含偏置误差信息

**具体修改**：
```python
# 在类初始化中添加
self.bias_analyzer = None  # 延迟初始化

# 新增方法
def _analyze_channel_bias_errors(self, ref_data, comp_data, method='auto'):
    """分析通道级偏置误差"""
    pass

# 修改analyze_inference_errors方法
# 在原有分析后添加偏置分析部分
```

##### 2.2 `inference/management/utils.py`
**修改点**：
- 添加 `extract_channel_data()` 函数，从WaveData提取通道数据
- 添加 `format_bias_error_matrix()` 函数，格式化偏置误差矩阵
- 添加 `validate_signal_properties()` 函数，检查信号属性

##### 2.3 `inference/management/report_generator.py`
**修改点**：
- 在 `generate_analysis_report()` 中添加偏置误差报告部分
- 添加 `_generate_bias_error_section()` 方法，生成偏置误差报告
- 添加 `_create_bias_error_heatmap()` 方法，生成偏置误差热力图

##### 2.4 `inference/management/inference_manager.py`
**修改点**：
- 在 `analyze_errors()` 方法中添加偏置分析方法选择参数
- 更新命令行参数处理，支持 `--bias-method` 选项

### 第二阶段：测试开发

#### 1. 测试数据生成策略

##### 1.1 `tests/inference/fixtures/bias_test_signals.py`
**用途**：生成各种测试信号
**包含信号类型**：
- 纯DC信号（用于验证基本功能）
- DC + 正弦波（测试频率分离能力）
- DC + 多频率成分（测试复杂信号）
- 带瞬态响应的信号（测试稳态提取）
- 带噪声的信号（测试鲁棒性）
- 漂移信号（测试时变偏置）

#### 2. 测试用例设计

##### 2.1 稳态段提取法测试
- `test_steady_state_pure_dc()` - 纯DC信号
- `test_steady_state_with_transient()` - 带瞬态响应
- `test_steady_state_oscillating()` - 持续振荡信号
- `test_steady_state_parameter_sensitivity()` - 参数敏感性
- `test_steady_state_edge_cases()` - 边界条件

##### 2.2 频域滤波法测试
- `test_frequency_domain_pure_dc()` - 纯DC信号
- `test_frequency_domain_multi_frequency()` - 多频率信号
- `test_frequency_domain_bandwidth_effect()` - 带宽参数影响
- `test_frequency_domain_sampling_rate()` - 采样率影响
- `test_frequency_domain_spectral_leakage()` - 频谱泄漏处理

##### 2.3 集成测试
- `test_bias_analyzer_integration()` - 完整流程测试
- `test_multilayer_bias_analysis()` - 多层网络测试
- `test_channel_consistency()` - 通道一致性测试
- `test_error_propagation()` - 误差传播测试

### 第三阶段：命令行集成

#### 1. 修改文件

##### 1.1 `cli.py`
**修改点**：
- 添加 `--bias-method` 命令行参数
- 添加 `--bias-params` 命令行参数（JSON格式）
- 在 `analyze_errors()` 调用中传递偏置分析参数

**示例命令**：
```bash
# 使用默认（自动）方法
python cli.py -a PROJECT_NAME

# 指定稳态段提取法
python cli.py -a PROJECT_NAME --bias-method steady_state

# 指定频域滤波法with参数
python cli.py -a PROJECT_NAME --bias-method frequency --bias-params '{"dc_bandwidth": 2.0}'
```

##### 1.2 `inference/doc/user_guide/bias_analysis_guide.md`
**新增文档**：用户使用指南
- 偏置分析功能介绍
- 两种方法的适用场景
- 命令行使用示例
- 结果解读指南

### 第四阶段：结果输出增强

#### 1. JSON输出格式

##### 1.1 修改 `error_analysis.json` 结构
```json
{
  "existing_fields": "...",
  "bias_analysis": {
    "method": "frequency_domain",
    "parameters": {
      "dc_bandwidth": 1.0,
      "sample_rate": 100000
    },
    "analysis_timestamp": "2025-07-11 14:30:00",
    "layer_analysis": [
      {
        "layer": 1,
        "channels": 10,
        "bias_errors": [0.001, -0.002, ...],
        "statistics": {
          "mean": 0.0001,
          "std": 0.0005,
          "max_abs": 0.002
        }
      }
    ],
    "bias_error_matrix": [[...]],
    "summary": {
      "worst_case": {
        "layer": 3,
        "channel": 5,
        "error": 0.005
      },
      "average_by_layer": [...],
      "average_by_channel": [...]
    }
  }
}
```

#### 2. 可视化输出

##### 2.1 新增文件 `inference/visualization/bias_plots.py`
**功能**：生成偏置误差可视化图表
- 偏置误差矩阵热力图
- 逐层偏置误差趋势图
- 通道间偏置误差对比图
- 偏置误差分布直方图

## 实施时间表

### 第一周：核心功能开发
- Day 1-2: 实现 `bias_analyzer.py` 核心算法
- Day 3-4: 编写单元测试和测试数据生成
- Day 5: 测试调试，确保算法正确性

### 第二周：集成和测试
- Day 1-2: 集成到 `error_analyzer.py`
- Day 3: 更新报告生成器和工具函数
- Day 4: 命令行参数集成
- Day 5: 集成测试和文档编写

### 第三周：优化和部署
- Day 1-2: 性能优化和边界条件处理
- Day 3: 可视化功能开发
- Day 4: 用户文档和示例
- Day 5: 最终测试和部署

## 风险和缓解措施

### 1. 技术风险
- **风险**：频域方法可能对短信号效果不佳
- **缓解**：实现信号长度检查，自动切换到稳态方法

### 2. 性能风险
- **风险**：大规模数据的FFT计算可能较慢
- **缓解**：实现批处理和并行计算选项

### 3. 兼容性风险
- **风险**：新功能可能影响现有工作流
- **缓解**：保持向后兼容，新功能作为可选项

## 验收标准

1. **功能完整性**
   - 两种偏置计算方法都能正确工作
   - 支持单层和多层分析
   - 结果以JSON格式正确输出

2. **测试覆盖**
   - 单元测试覆盖率 > 90%
   - 所有边界条件都有测试用例
   - 集成测试通过

3. **性能指标**
   - 单层分析时间 < 1秒（1000个样本×10个通道）
   - 内存使用合理，无内存泄漏

4. **文档完善**
   - API文档完整
   - 用户指南清晰
   - 示例代码可运行

## 附录：关键代码结构

### A. BiasAnalyzer 接口设计

```python
class BiasAnalyzer(ABC):
    """偏置分析器基类"""
    
    @abstractmethod
    def calculate_bias(self, channel_data, sample_rate):
        """计算单通道偏置"""
        pass
    
    @abstractmethod
    def get_method_name(self):
        """返回方法名称"""
        pass
    
    def analyze_wavedata(self, wave_data):
        """分析WaveData对象的所有通道"""
        pass
```

### B. 测试数据结构

```python
@pytest.fixture
def bias_test_signals():
    """生成测试信号集合"""
    return {
        'pure_dc': generate_pure_dc_signal(),
        'dc_with_sine': generate_dc_with_sine(),
        'transient': generate_transient_signal(),
        'multi_freq': generate_multi_frequency_signal(),
        'noisy': generate_noisy_signal()
    }
```

### C. 命令行参数扩展

```python
# 在 cli.py 中添加
parser.add_argument('--bias-method', 
                    choices=['auto', 'steady_state', 'frequency'],
                    default='auto',
                    help='偏置分析方法')
parser.add_argument('--bias-params',
                    type=json.loads,
                    default={},
                    help='偏置分析参数（JSON格式）')
```

## 总结

本实施方案提供了完整的偏置误差分析功能开发路线图。通过分阶段实施，先开发核心功能并充分测试，然后逐步集成到主程序，可以确保功能的稳定性和可靠性。重点是先用pytest验证算法的正确性，再进行系统集成，最后优化用户体验。