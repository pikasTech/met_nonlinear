# cli.py -a 偏置误差分析增强方案

## 背景

当前的 `cli.py -a` 命令会分析神经网络推理结果与SPICE/NumPy推理结果之间的误差。然而，现有实现存在以下限制：

1. **误差分析粒度不足**：当前实现将所有通道数据展平后计算整体误差指标（mean_error, rms_error等），无法提供每个通道的独立误差分析
2. **缺少偏置误差分析**：对于包含多种频率成分的波形输出，需要专门的偏置（DC偏移）误差计算方法
3. **缺少多层次分析视图**：对于多层网络，需要提供层数×通道数的误差矩阵，以便深入理解误差传播

## 需求分析

### 功能需求
1. 对每个通道的偏置误差进行独立分析
2. 返回与通道数对应的偏置误差列表
3. 对多层网络，返回层数×通道数的偏置误差矩阵
4. 将分析结果写入JSON文件，便于后续处理
5. 考虑输出波形包含多种频率成分的特点，选择最准确的偏置计算方法

### 技术挑战
- 输出波形包含多种频率成分，需要有效分离DC分量
- 不同通道可能有不同的信号特性，需要自适应的分析方法
- 需要处理瞬态响应对偏置计算的影响

## 方案设计

### 方案一：时域平均法（Time-Domain Averaging）

#### 原理
直接计算整个时间序列的平均值作为偏置估计。这是最简单直接的方法。

#### 实现步骤
```python
def calculate_bias_time_average(channel_data):
    """
    通过时域平均计算偏置
    
    参数:
        channel_data: shape (time_steps,) 的单通道数据
    
    返回:
        float: 偏置估计值
    """
    return np.mean(channel_data)
```

#### 优点
- 实现简单，计算快速
- 对于稳态信号效果良好
- 不需要额外的参数调整

#### 缺点
- 对瞬态响应敏感
- 如果信号包含低频振荡，可能导致偏置估计不准确
- 无法区分真实偏置和低频信号成分

#### 适用场景
- 稳态响应分析
- 瞬态响应已经衰减的情况
- 快速初步分析

### 方案二：稳态段提取法（Steady-State Extraction）

#### 原理
识别信号的稳态段（通常是后期部分），仅对稳态段计算平均值，避免瞬态响应的影响。

#### 实现步骤
```python
def calculate_bias_steady_state(channel_data, steady_ratio=0.3):
    """
    通过稳态段提取计算偏置
    
    参数:
        channel_data: shape (time_steps,) 的单通道数据
        steady_ratio: 用于计算偏置的信号末尾部分比例
    
    返回:
        float: 偏置估计值
    """
    n_samples = len(channel_data)
    steady_start = int(n_samples * (1 - steady_ratio))
    steady_data = channel_data[steady_start:]
    
    # 检查稳态段的稳定性
    if np.std(steady_data) > 0.1 * np.abs(np.mean(steady_data)):
        # 如果方差较大，可能还未达到稳态，增加警告
        print("警告：稳态段可能包含振荡成分")
    
    return np.mean(steady_data)
```

#### 优点
- 避免瞬态响应的影响
- 对于具有明显稳态段的信号效果很好
- 可以通过调整 steady_ratio 参数适应不同的信号特性

#### 缺点
- 需要假设信号最终会达到稳态
- 对于持续振荡的信号可能不适用
- steady_ratio 参数需要根据具体情况调整

#### 适用场景
- 阶跃响应分析
- 具有明显瞬态和稳态段的信号
- 系统稳定性验证

### 方案三：频域滤波法（Frequency-Domain Filtering）

#### 原理
通过FFT将信号转换到频域，提取DC分量（0Hz分量），这是最准确的偏置提取方法。

#### 实现步骤
```python
def calculate_bias_frequency_domain(channel_data, sample_rate, dc_bandwidth=1.0):
    """
    通过频域分析提取DC偏置
    
    参数:
        channel_data: shape (time_steps,) 的单通道数据
        sample_rate: 采样率 (Hz)
        dc_bandwidth: DC分量的带宽 (Hz)，用于低通滤波
    
    返回:
        float: 偏置估计值
    """
    # 执行FFT
    n_samples = len(channel_data)
    fft_data = np.fft.fft(channel_data)
    freqs = np.fft.fftfreq(n_samples, 1/sample_rate)
    
    # 创建低通滤波器，只保留接近0Hz的分量
    mask = np.abs(freqs) <= dc_bandwidth
    filtered_fft = fft_data.copy()
    filtered_fft[~mask] = 0
    
    # 逆FFT获取低频分量
    low_freq_signal = np.fft.ifft(filtered_fft).real
    
    # DC分量就是0Hz分量的幅值
    dc_component = fft_data[0].real / n_samples
    
    # 可选：使用低频信号的平均值作为更鲁棒的估计
    robust_dc = np.mean(low_freq_signal)
    
    return dc_component  # 或返回 robust_dc
```

#### 优点
- 理论上最准确，能够精确分离DC分量
- 不受高频噪声影响
- 可以同时分析其他频率成分
- 适用于包含多种频率成分的复杂信号

#### 缺点
- 计算复杂度较高
- 需要足够的数据长度以获得良好的频率分辨率
- 对于非周期信号可能产生频谱泄漏

#### 适用场景
- 复杂的多频率成分信号
- 需要高精度偏置估计的场合
- 同时需要频谱分析的应用

## 推荐实现方案

考虑到输出波形包含多种频率成分的特点，**推荐采用组合方案**：

1. **主方法**：使用频域滤波法（方案三）作为主要的偏置计算方法
2. **验证方法**：使用稳态段提取法（方案二）作为验证
3. **快速方法**：提供时域平均法（方案一）作为快速预览选项

### 实现架构

```python
class ChannelBiasAnalyzer:
    """通道偏置误差分析器"""
    
    def __init__(self, method='frequency', **kwargs):
        """
        初始化分析器
        
        参数:
            method: 分析方法 ('frequency', 'steady_state', 'time_average', 'auto')
            kwargs: 方法特定参数
        """
        self.method = method
        self.params = kwargs
    
    def analyze_bias_errors(self, ref_data, comp_data, layer_info=None):
        """
        分析偏置误差
        
        参数:
            ref_data: 参考数据 (time_steps, channels)
            comp_data: 对比数据 (time_steps, channels)
            layer_info: 层信息（可选）
        
        返回:
            dict: 包含偏置误差分析结果
        """
        n_channels = ref_data.shape[1]
        bias_errors = []
        
        for ch in range(n_channels):
            ref_bias = self._calculate_bias(ref_data[:, ch])
            comp_bias = self._calculate_bias(comp_data[:, ch])
            bias_error = ref_bias - comp_bias
            
            bias_errors.append({
                'channel': ch,
                'ref_bias': float(ref_bias),
                'comp_bias': float(comp_bias),
                'bias_error': float(bias_error),
                'relative_error': float(bias_error / ref_bias) if ref_bias != 0 else None
            })
        
        return {
            'layer_info': layer_info,
            'channel_count': n_channels,
            'bias_errors': bias_errors,
            'summary': {
                'mean_bias_error': np.mean([e['bias_error'] for e in bias_errors]),
                'max_bias_error': np.max(np.abs([e['bias_error'] for e in bias_errors])),
                'method': self.method,
                'parameters': self.params
            }
        }
    
    def analyze_multilayer_bias(self, layer_data_pairs):
        """
        分析多层网络的偏置误差
        
        参数:
            layer_data_pairs: [(ref_data, comp_data, layer_info), ...]
        
        返回:
            dict: 包含多层偏置误差矩阵
        """
        results = []
        bias_matrix = []
        
        for ref_data, comp_data, layer_info in layer_data_pairs:
            layer_result = self.analyze_bias_errors(ref_data, comp_data, layer_info)
            results.append(layer_result)
            
            # 提取偏置误差向量
            bias_vector = [e['bias_error'] for e in layer_result['bias_errors']]
            bias_matrix.append(bias_vector)
        
        return {
            'layer_results': results,
            'bias_error_matrix': np.array(bias_matrix),  # shape: (n_layers, n_channels)
            'matrix_shape': {
                'n_layers': len(layer_data_pairs),
                'n_channels': len(bias_matrix[0]) if bias_matrix else 0
            }
        }
```

### 输出格式

增强后的分析结果将包含以下结构：

```json
{
    "project_name": "PROJECT_NAME",
    "timestamp": "2025-07-11 10:00:00",
    "bias_analysis": {
        "method": "frequency",
        "parameters": {
            "dc_bandwidth": 1.0,
            "sample_rate": 100000
        },
        "layer_bias_errors": [
            {
                "layer": 1,
                "channel_bias_errors": [
                    {
                        "channel": 0,
                        "ref_bias": 0.0123,
                        "comp_bias": 0.0125,
                        "bias_error": -0.0002,
                        "relative_error": -0.0163
                    },
                    ...
                ]
            },
            ...
        ],
        "bias_error_matrix": [
            [-0.0002, 0.0001, ...],  // Layer 1
            [0.0003, -0.0001, ...],  // Layer 2
            ...
        ],
        "summary_statistics": {
            "per_channel_mean_bias": [-0.0001, 0.0002, ...],
            "per_layer_mean_bias": [0.0001, -0.0002, ...],
            "overall_mean_bias": 0.0001,
            "worst_channel": {
                "layer": 3,
                "channel": 2,
                "bias_error": 0.005
            }
        }
    },
    "existing_analysis": {
        // 保留现有的整体误差分析结果
    }
}
```

## 实施计划

1. **第一阶段**：实现基础的通道偏置分析功能
   - 在 `ErrorAnalyzer` 类中添加 `ChannelBiasAnalyzer`
   - 实现三种偏置计算方法
   - 修改 `analyze_errors` 命令以包含偏置分析

2. **第二阶段**：完善多层分析和可视化
   - 实现偏置误差矩阵计算
   - 添加可视化功能（热力图显示偏置误差矩阵）
   - 优化性能，支持大规模数据

3. **第三阶段**：高级功能
   - 自动方法选择（根据信号特性）
   - 偏置漂移分析（时间序列分析）
   - 与其他误差指标的相关性分析

## 结论

通过实现上述方案，`cli.py -a` 命令将能够提供详细的通道级偏置误差分析，帮助用户更好地理解模型在不同通道上的表现差异。频域滤波法作为主要方法能够准确处理包含多种频率成分的复杂波形，而组合方案的设计确保了分析的鲁棒性和灵活性。