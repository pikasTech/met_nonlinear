# WNET5假频补偿算法具体实施计划

## 项目概述

本计划基于**首选方案A**（基于现有WNET5架构的直接适配），详细规划WNET5针对假频数据集的TensorFlow算法补偿实施。利用现有成熟的WNET5基础设施，快速实现高效的假频补偿算法。

## 实施时间线

**总工期：3周**
- **第1周**：项目配置和初步训练
- **第2周**：模型优化和效果验证
- **第3周**：性能调优和完整测试

## 详细实施步骤

### 第1周：项目配置和初步训练

#### 1.1 创建项目目录结构（第1天）

**任务**：建立专用的WNET5假频补偿项目

**执行步骤**：
```bash
# 创建项目目录
mkdir -p projects/WNET5_AliasComp/data
mkdir -p projects/WNET5_AliasComp/data/scalers
```

#### 1.2 配置文件创建（第1天）

**目标文件**：`projects/WNET5_AliasComp/config.json`

**具体内容**：
```json
{
    "using_gpu": true,
    "epoch_train": 25000,
    "step_per_epoch": 2,
    "learning_rate": 0.015,
    "use_train_model": true,
    "use_model": "WaveNet5",
    "kernal_units": 6,
    "use_power_loss": true,
    "use_points": 8000,
    "resume_training": true,
    "use_best_val_weights": true,
    "use_auto_lr": true,
    "auto_lr_decay_steps": 800,
    "IIR_TRAINABLE": false,
    "USE_FAST_MODEL": true,
    "IIR_INIT_BY_SYSTEM": true,
    "use_scale": true,
    "use_predict_features": true,
    "use_predict_fr": true,
    "use_cache_features": true,
    "sample_rate": 2000,
    "time_clipped_s": 4.0,
    "activation": "relu",
    "dataset_type": "AliasSimu",
    "feature_range": [-1, 1],
    "target_sweep": 2,
    "model_subcfg": {
        "init_center_freqs": [8, 25, 50, 85, 120, 180],
        "init_quality_factors": [1.5, 2.0, 2.5, 3.0, 4.0, 5.0],
        "post_dense": true,
        "post_dense_activation": "relu",
        "post_dense_units": 8,
        "post_dense_layers": 4,
        "dropout_rate": 0.1,
        "use_dense_bias": true
    }
}
```

**配置说明**：
- **中心频率选择**：覆盖假频敏感频段（8-180Hz）
- **Q因子优化**：渐进式设计，低频宽Q，高频窄Q
- **后处理增强**：4层全连接网络提升补偿精度
- **数据集类型**：使用模拟假频数据集进行训练

#### 1.3 修改配置加载逻辑（第2天）

**目标文件**：`config.py`

**修改位置**：第74行
```python
# 修改前
self.dataset_type = 'MET'

# 修改后
self.dataset_type = 'AliasSimu'  # 默认使用假频模拟数据集
```

**新增配置验证方法**：
```python
def validate_aliasing_config(self):
    """验证假频补偿配置的有效性"""
    if self.dataset_type in ['Alias', 'AliasSimu']:
        if 'WaveNet5' not in self.use_model:
            print("Warning: 推荐使用WaveNet5处理假频数据")
        
        if 'init_center_freqs' in self.model_subcfg:
            freqs = self.model_subcfg['init_center_freqs']
            if min(freqs) < 5 or max(freqs) > 200:
                print("Warning: 假频补偿建议频率范围为5-200Hz")
    
    return True
```

#### 1.4 数据处理优化（第2-3天）

**目标文件**：`data_processing.py`

**修改位置**：`Dataset_COMP_AliasSimu`类（第1099行附近）

**新增假频特征增强**：
```python
def enhance_aliasing_features(self, data, freq):
    """
    针对假频数据的特征增强
    
    Args:
        data: 原始信号数据
        freq: 信号频率
    
    Returns:
        enhanced_data: 增强后的信号数据
    """
    # 假频特征检测和增强
    if freq > 80:  # 高频段假频增强
        # 添加轻微的非线性失真模拟
        aliasing_coeff = 0.02 * (freq - 80) / 120
        enhanced_data = data + aliasing_coeff * np.sign(data) * data**2
    else:
        enhanced_data = data
    
    return enhanced_data
```

**集成到数据生成流程**：在第1180行附近的数据生成循环中添加：
```python
# 在生成target_response后添加
target_response = self.enhance_aliasing_features(target_response, freq)
```

#### 1.5 模型引擎适配（第3天）

**目标文件**：`model_engine.py`

**修改位置**：第323-331行的WaveNet模型创建部分

**新增假频专用初始化**：
```python
elif 'WaveNet' in self.config.use_model:
    mod_class = eval(self.config.use_model)
    
    # 假频数据集专用配置调整
    if self.config.dataset_type in ['Alias', 'AliasSimu']:
        # 优化假频补偿的特殊配置
        aliasing_optimized_subcfg = self._optimize_for_aliasing(self.config.model_subcfg)
        print("INFO: 应用假频补偿优化配置")
    else:
        aliasing_optimized_subcfg = self.config.model_subcfg
    
    self.model_comp = mod_class(
        fs=self.config.sample_rate,
        checkpoint_dir=self.checkpoint_dir,
        kernel_units=self.config.kernal_units,
        activation=self.config.activation,
        model_subcfg=aliasing_optimized_subcfg,
    )
```

**新增优化方法**：
```python
def _optimize_for_aliasing(self, base_subcfg):
    """针对假频补偿优化模型子配置"""
    optimized_cfg = base_subcfg.copy()
    
    # 假频补偿专用频率分布
    if 'init_center_freqs' not in optimized_cfg:
        optimized_cfg['init_center_freqs'] = [8, 25, 50, 85, 120, 180]
    
    # 假频补偿专用Q因子
    if 'init_quality_factors' not in optimized_cfg:
        optimized_cfg['init_quality_factors'] = [1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
    
    # 假频补偿需要更强的后处理
    optimized_cfg['post_dense'] = True
    optimized_cfg['post_dense_layers'] = max(optimized_cfg.get('post_dense_layers', 1), 4)
    
    return optimized_cfg
```

### 第2周：模型优化和效果验证

#### 2.1 训练监控增强（第4天）

**目标文件**：`training.py`

**修改位置**：训练回调部分

**新增假频补偿专用监控**：
```python
def aliasing_compensation_callback(self, epoch, logs=None):
    """假频补偿训练专用回调"""
    if logs is None:
        logs = {}
    
    # 每100个epoch进行假频补偿效果评估
    if epoch % 100 == 0:
        self._evaluate_aliasing_compensation(epoch, logs)
    
def _evaluate_aliasing_compensation(self, epoch, logs):
    """评估假频补偿效果"""
    print(f"\nEpoch {epoch}: 假频补偿效果评估")
    
    # 生成测试频率点
    test_freqs = [15, 45, 75, 105, 135, 165]
    compensation_scores = []
    
    for freq in test_freqs:
        # 生成测试信号
        test_signal = self._generate_test_signal(freq)
        
        # 模型预测
        prediction = self.model_comp.predict(test_signal)
        
        # 计算补偿效果评分
        score = self._calculate_compensation_score(test_signal, prediction, freq)
        compensation_scores.append(score)
        
        print(f"  频率 {freq}Hz: 补偿评分 {score:.4f}")
    
    avg_score = np.mean(compensation_scores)
    logs['aliasing_compensation_score'] = avg_score
    print(f"  平均补偿评分: {avg_score:.4f}")
```

#### 2.2 评估指标体系建立（第5天）

**目标文件**：新建 `aliasing_evaluation.py`

**主要功能**：
```python
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

class AliasingCompensationEvaluator:
    """假频补偿效果评估器"""
    
    def __init__(self, fs=2000):
        self.fs = fs
        
    def evaluate_compensation_quality(self, original, compensated, target, freq):
        """
        评估假频补偿质量
        
        Args:
            original: 原始带假频信号
            compensated: 补偿后信号
            target: 理想目标信号
            freq: 信号频率
            
        Returns:
            dict: 包含多项评估指标的字典
        """
        metrics = {}
        
        # 1. 信噪比改善
        metrics['snr_improvement'] = self._calculate_snr_improvement(
            original, compensated, target)
        
        # 2. 频域失真度
        metrics['frequency_distortion'] = self._calculate_frequency_distortion(
            compensated, target, freq)
        
        # 3. 时域相关性
        metrics['time_correlation'] = np.corrcoef(compensated.flatten(), 
                                                target.flatten())[0, 1]
        
        # 4. 假频抑制比
        metrics['aliasing_suppression'] = self._calculate_aliasing_suppression(
            original, compensated, freq)
        
        # 5. 综合评分
        metrics['overall_score'] = self._calculate_overall_score(metrics)
        
        return metrics
    
    def _calculate_snr_improvement(self, original, compensated, target):
        """计算信噪比改善"""
        # 原始信号的信噪比
        noise_original = original - target
        snr_original = 20 * np.log10(np.std(target) / np.std(noise_original))
        
        # 补偿后信号的信噪比
        noise_compensated = compensated - target
        snr_compensated = 20 * np.log10(np.std(target) / np.std(noise_compensated))
        
        return snr_compensated - snr_original
    
    def _calculate_frequency_distortion(self, compensated, target, freq):
        """计算频域失真度"""
        # FFT分析
        fft_compensated = np.fft.fft(compensated)
        fft_target = np.fft.fft(target)
        
        # 计算主频段的失真
        freq_bin = int(freq * len(compensated) / self.fs)
        main_freq_distortion = np.abs(fft_compensated[freq_bin] - fft_target[freq_bin]) / np.abs(fft_target[freq_bin])
        
        return main_freq_distortion
    
    def _calculate_aliasing_suppression(self, original, compensated, freq):
        """计算假频抑制比"""
        # 计算假频成分的能量变化
        aliasing_freq = freq + 80  # 假设假频在基频+80Hz附近
        
        fft_original = np.fft.fft(original)
        fft_compensated = np.fft.fft(compensated)
        
        freq_bins = np.fft.fftfreq(len(original), 1/self.fs)
        aliasing_bin = np.argmin(np.abs(freq_bins - aliasing_freq))
        
        aliasing_power_original = np.abs(fft_original[aliasing_bin])**2
        aliasing_power_compensated = np.abs(fft_compensated[aliasing_bin])**2
        
        suppression_ratio = 10 * np.log10(aliasing_power_original / (aliasing_power_compensated + 1e-10))
        
        return suppression_ratio
    
    def _calculate_overall_score(self, metrics):
        """计算综合评分"""
        # 加权平均各项指标
        weights = {
            'snr_improvement': 0.3,
            'frequency_distortion': 0.25,
            'time_correlation': 0.25,
            'aliasing_suppression': 0.2
        }
        
        # 归一化处理
        normalized_metrics = {
            'snr_improvement': np.clip(metrics['snr_improvement'] / 20, 0, 1),
            'frequency_distortion': np.clip(1 - metrics['frequency_distortion'], 0, 1),
            'time_correlation': np.clip(metrics['time_correlation'], 0, 1),
            'aliasing_suppression': np.clip(metrics['aliasing_suppression'] / 30, 0, 1)
        }
        
        overall_score = sum(weights[key] * normalized_metrics[key] 
                          for key in weights.keys())
        
        return overall_score
```

#### 2.3 超参数调优脚本（第6天）

**目标文件**：新建 `hyperparameter_tuning.py`

**主要功能**：
```python
import itertools
import json
from copy import deepcopy

class WNET5AliasingHyperparameterTuner:
    """WNET5假频补偿超参数调优器"""
    
    def __init__(self, base_config_path):
        with open(base_config_path, 'r') as f:
            self.base_config = json.load(f)
    
    def generate_hyperparameter_combinations(self):
        """生成超参数组合"""
        # 定义搜索空间
        search_space = {
            'learning_rate': [0.01, 0.015, 0.02, 0.025],
            'init_center_freqs': [
                [8, 25, 50, 85, 120, 180],
                [5, 20, 45, 75, 110, 160],
                [10, 30, 55, 90, 130, 190]
            ],
            'init_quality_factors': [
                [1.5, 2.0, 2.5, 3.0, 4.0, 5.0],
                [1.0, 1.5, 2.0, 2.5, 3.0, 4.0],
                [2.0, 2.5, 3.0, 3.5, 4.5, 6.0]
            ],
            'post_dense_units': [6, 8, 10],
            'post_dense_layers': [3, 4, 5],
            'dropout_rate': [0.05, 0.1, 0.15]
        }
        
        # 生成所有组合（限制总数以控制计算成本）
        keys = list(search_space.keys())
        combinations = []
        
        # 使用网格搜索生成前20个最有希望的组合
        for lr in search_space['learning_rate'][:2]:
            for freq_idx in range(len(search_space['init_center_freqs'])):
                for units in search_space['post_dense_units'][:2]:
                    for layers in search_space['post_dense_layers'][:2]:
                        config = deepcopy(self.base_config)
                        config['learning_rate'] = lr
                        config['model_subcfg']['init_center_freqs'] = search_space['init_center_freqs'][freq_idx]
                        config['model_subcfg']['init_quality_factors'] = search_space['init_quality_factors'][freq_idx]
                        config['model_subcfg']['post_dense_units'] = units
                        config['model_subcfg']['post_dense_layers'] = layers
                        config['model_subcfg']['dropout_rate'] = search_space['dropout_rate'][1]  # 使用中等dropout
                        
                        combinations.append(config)
        
        return combinations[:12]  # 限制为12个最优组合
    
    def save_tuning_configs(self, output_dir="tuning_configs"):
        """保存调优配置文件"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        combinations = self.generate_hyperparameter_combinations()
        
        for i, config in enumerate(combinations):
            config_name = f"wnet5_aliasing_tune_{i+1:02d}"
            config_path = os.path.join(output_dir, f"{config_name}.json")
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            print(f"已生成调优配置: {config_path}")
        
        return len(combinations)
```

### 第3周：性能调优和完整测试

#### 3.1 性能优化实施（第7-8天）

**目标文件**：`models/wavenet_models.py`

**修改位置**：WaveNet5类的`build_model`方法

**新增假频优化层**：
```python
def build_aliasing_optimized_model(self, input_shape):
    """构建假频补偿优化的模型"""
    inputs = tf.keras.layers.Input(shape=input_shape, name="Input")
    fast_inputs = tf.keras.layers.Input(shape=input_shape, name="Fast_Input")
    
    # 假频预处理层
    x = self._add_aliasing_preprocessing(inputs)
    fast_x = fast_inputs
    
    # 原有的IIR滤波器层
    x, layer_input = self._build_iir_layers(x)
    fast_x = self._build_fast_layers(fast_x)
    
    # 假频增强的后处理层
    x = self._add_aliasing_postprocessing(x)
    fast_x = self._add_aliasing_postprocessing(fast_x)
    
    return self._finalize_model(inputs, x, fast_inputs, fast_x)

def _add_aliasing_preprocessing(self, x):
    """添加假频预处理层"""
    # 自适应频域滤波
    x = tf.keras.layers.Conv1D(
        filters=4, 
        kernel_size=16, 
        padding='causal',
        activation='tanh',
        name='Aliasing_Prefilter'
    )(x)
    return x

def _add_aliasing_postprocessing(self, x):
    """添加假频后处理优化层"""
    # 残差连接增强
    residual = x
    
    # 多尺度特征提取
    conv_3 = tf.keras.layers.Conv1D(
        filters=x.shape[-1], kernel_size=3, padding='causal', activation='relu')(x)
    conv_5 = tf.keras.layers.Conv1D(
        filters=x.shape[-1], kernel_size=5, padding='causal', activation='relu')(x)
    conv_7 = tf.keras.layers.Conv1D(
        filters=x.shape[-1], kernel_size=7, padding='causal', activation='relu')(x)
    
    # 特征融合
    concat_features = tf.keras.layers.Concatenate()([conv_3, conv_5, conv_7])
    
    # 特征压缩
    compressed = tf.keras.layers.Conv1D(
        filters=x.shape[-1], kernel_size=1, activation='relu')(concat_features)
    
    # 残差连接
    x = tf.keras.layers.Add()([residual, compressed])
    
    return x
```

#### 3.2 完整测试脚本（第9天）

**目标文件**：新建 `complete_aliasing_test.py`

**主要功能**：
```python
import numpy as np
import matplotlib.pyplot as plt
from aliasing_evaluation import AliasingCompensationEvaluator
import tensorflow as tf

class CompleteAliasingTest:
    """完整假频补偿测试套件"""
    
    def __init__(self, model_path, config_path):
        self.model_path = model_path
        self.config_path = config_path
        self.evaluator = AliasingCompensationEvaluator()
        
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("=== WNET5假频补偿综合测试 ===")
        
        # 1. 单频测试
        print("\n1. 单频测试")
        single_freq_results = self._test_single_frequencies()
        
        # 2. 多频测试
        print("\n2. 多频测试")
        multi_freq_results = self._test_multiple_frequencies()
        
        # 3. 不同强度假频测试
        print("\n3. 不同强度假频测试")
        intensity_results = self._test_different_intensities()
        
        # 4. 实时性能测试
        print("\n4. 实时性能测试")
        performance_results = self._test_realtime_performance()
        
        # 5. 生成测试报告
        self._generate_test_report({
            'single_freq': single_freq_results,
            'multi_freq': multi_freq_results,
            'intensity': intensity_results,
            'performance': performance_results
        })
        
    def _test_single_frequencies(self):
        """单频测试"""
        test_frequencies = [10, 25, 40, 60, 80, 100, 120, 150, 180]
        results = {}
        
        for freq in test_frequencies:
            print(f"  测试频率: {freq}Hz")
            
            # 生成测试信号
            test_data = self._generate_aliasing_test_signal(freq)
            
            # 模型预测
            prediction = self.model.predict(test_data['input'])
            
            # 评估结果
            metrics = self.evaluator.evaluate_compensation_quality(
                test_data['input'], prediction, test_data['target'], freq
            )
            
            results[freq] = metrics
            print(f"    综合评分: {metrics['overall_score']:.4f}")
            
        return results
    
    def _test_multiple_frequencies(self):
        """多频测试"""
        freq_combinations = [
            [20, 60],
            [30, 90],
            [15, 45, 75],
            [25, 55, 85, 115]
        ]
        
        results = {}
        
        for freqs in freq_combinations:
            print(f"  测试频率组合: {freqs}Hz")
            
            # 生成多频测试信号
            test_data = self._generate_multi_freq_signal(freqs)
            
            # 模型预测
            prediction = self.model.predict(test_data['input'])
            
            # 评估结果
            avg_score = 0
            for freq in freqs:
                metrics = self.evaluator.evaluate_compensation_quality(
                    test_data['input'], prediction, test_data['target'], freq
                )
                avg_score += metrics['overall_score']
            
            avg_score /= len(freqs)
            results[str(freqs)] = avg_score
            print(f"    平均评分: {avg_score:.4f}")
            
        return results
    
    def _test_different_intensities(self):
        """不同强度假频测试"""
        aliasing_strengths = [0.1, 0.3, 0.5, 0.8, 1.0]
        test_freq = 50  # 使用50Hz作为基准频率
        
        results = {}
        
        for strength in aliasing_strengths:
            print(f"  假频强度: {strength}")
            
            # 生成不同强度的假频信号
            test_data = self._generate_variable_intensity_signal(test_freq, strength)
            
            # 模型预测
            prediction = self.model.predict(test_data['input'])
            
            # 评估结果
            metrics = self.evaluator.evaluate_compensation_quality(
                test_data['input'], prediction, test_data['target'], test_freq
            )
            
            results[strength] = metrics['overall_score']
            print(f"    补偿评分: {metrics['overall_score']:.4f}")
            
        return results
    
    def _test_realtime_performance(self):
        """实时性能测试"""
        import time
        
        # 测试不同数据长度的处理时间
        data_lengths = [1000, 2000, 4000, 8000]
        results = {}
        
        for length in data_lengths:
            test_signal = np.random.randn(1, length, 1).astype(np.float32)
            
            # 测试推理时间
            start_time = time.time()
            for _ in range(10):  # 重复10次取平均
                _ = self.model.predict(test_signal, verbose=0)
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 10
            results[length] = avg_time
            
            print(f"  数据长度 {length}: {avg_time*1000:.2f}ms")
            
        return results
    
    def _generate_test_report(self, all_results):
        """生成测试报告"""
        report_path = "wnet5_aliasing_test_report.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# WNET5假频补偿测试报告\n\n")
            f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 单频测试结果
            f.write("## 单频测试结果\n\n")
            f.write("| 频率(Hz) | 综合评分 | SNR改善(dB) | 时域相关性 |\n")
            f.write("|----------|----------|-------------|------------|\n")
            for freq, metrics in all_results['single_freq'].items():
                f.write(f"| {freq} | {metrics['overall_score']:.4f} | "
                       f"{metrics['snr_improvement']:.2f} | {metrics['time_correlation']:.4f} |\n")
            
            # 性能测试结果
            f.write("\n## 实时性能测试\n\n")
            f.write("| 数据长度 | 平均处理时间(ms) |\n")
            f.write("|----------|------------------|\n")
            for length, time_ms in all_results['performance'].items():
                f.write(f"| {length} | {time_ms*1000:.2f} |\n")
            
            f.write(f"\n报告生成完成: {report_path}")
```

#### 3.3 部署准备（第10天）

**目标文件**：新建 `deployment_package.py`

**主要功能**：
```python
import os
import shutil
import json

class WNET5AliasingDeployment:
    """WNET5假频补偿部署包准备"""
    
    def __init__(self, project_path, output_path="deployment"):
        self.project_path = project_path
        self.output_path = output_path
        
    def create_deployment_package(self):
        """创建部署包"""
        print("创建WNET5假频补偿部署包...")
        
        # 创建部署目录
        os.makedirs(self.output_path, exist_ok=True)
        
        # 1. 复制模型权重
        self._copy_model_weights()
        
        # 2. 复制配置文件
        self._copy_config_files()
        
        # 3. 复制缩放器
        self._copy_scalers()
        
        # 4. 创建推理接口
        self._create_inference_interface()
        
        # 5. 创建使用文档
        self._create_usage_documentation()
        
        print(f"部署包创建完成: {self.output_path}")
    
    def _create_inference_interface(self):
        """创建推理接口"""
        interface_code = '''
import numpy as np
import tensorflow as tf
import json
from pathlib import Path

class WNET5AliasingCompensator:
    """WNET5假频补偿器 - 生产环境接口"""
    
    def __init__(self, deployment_path):
        self.deployment_path = Path(deployment_path)
        self._load_model()
        self._load_config()
        self._load_scaler()
    
    def compensate(self, signal_data, sample_rate=2000):
        """
        对输入信号进行假频补偿
        
        Args:
            signal_data: numpy数组，形状为 (时间点数,) 或 (批次, 时间点数, 1)
            sample_rate: 采样率，默认2000Hz
            
        Returns:
            compensated_signal: 补偿后的信号
            compensation_quality: 补偿质量评分
        """
        # 预处理
        processed_input = self._preprocess_signal(signal_data)
        
        # 模型推理
        prediction = self.model.predict(processed_input, verbose=0)
        
        # 后处理
        compensated_signal = self._postprocess_signal(prediction)
        
        # 质量评估
        quality_score = self._estimate_quality(signal_data, compensated_signal)
        
        return compensated_signal, quality_score
    
    def batch_compensate(self, signal_batch):
        """批量补偿处理"""
        results = []
        qualities = []
        
        for signal in signal_batch:
            compensated, quality = self.compensate(signal)
            results.append(compensated)
            qualities.append(quality)
            
        return np.array(results), np.array(qualities)
    
    def _preprocess_signal(self, signal):
        """信号预处理"""
        # 确保正确的维度
        if signal.ndim == 1:
            signal = signal.reshape(1, -1, 1)
        elif signal.ndim == 2:
            signal = signal.reshape(signal.shape[0], signal.shape[1], 1)
            
        # 应用缩放器
        if hasattr(self, 'scaler'):
            signal = self.scaler.transform(signal.reshape(-1, 1)).reshape(signal.shape)
            
        return signal.astype(np.float32)
    
    def _postprocess_signal(self, prediction):
        """预测结果后处理"""
        # 逆缩放
        if hasattr(self, 'output_scaler'):
            prediction = self.output_scaler.inverse_transform(
                prediction.reshape(-1, 1)).reshape(prediction.shape)
        
        return prediction.squeeze()
    
    def _estimate_quality(self, original, compensated):
        """估算补偿质量"""
        # 简单的质量评估
        improvement = np.std(original) / (np.std(original - compensated) + 1e-8)
        quality_score = min(improvement / 10.0, 1.0)  # 归一化到0-1
        return quality_score

# 使用示例
if __name__ == "__main__":
    compensator = WNET5AliasingCompensator("./")
    
    # 生成测试信号
    t = np.linspace(0, 2, 4000)
    test_signal = np.sin(2 * np.pi * 50 * t) + 0.3 * np.sin(2 * np.pi * 130 * t)
    
    # 进行补偿
    compensated, quality = compensator.compensate(test_signal)
    
    print(f"补偿完成，质量评分: {quality:.4f}")
'''
        
        with open(os.path.join(self.output_path, "wnet5_compensator.py"), 'w', encoding='utf-8') as f:
            f.write(interface_code)
```

## 关键修改文件汇总

### 必须修改的文件

| 文件路径 | 修改类型 | 主要内容 |
|----------|----------|----------|
| `config.py` | 🔧 配置增强 | 添加假频配置验证和默认值 |
| `data_processing.py` | 🚀 功能增强 | 假频特征增强算法 |
| `model_engine.py` | ⚙️ 逻辑修改 | 假频专用模型初始化 |
| `training.py` | 📊 监控增强 | 假频补偿训练回调 |

### 新建文件

| 文件路径 | 文件类型 | 主要功能 |
|----------|----------|----------|
| `projects/WNET5_AliasComp/config.json` | 📋 配置文件 | 项目专用配置 |
| `aliasing_evaluation.py` | 🧪 评估模块 | 补偿效果评估 |
| `hyperparameter_tuning.py` | 🎛️ 调优工具 | 超参数自动优化 |
| `complete_aliasing_test.py` | 🔍 测试套件 | 综合功能测试 |
| `deployment_package.py` | 📦 部署工具 | 生产环境准备 |

## 验收标准

### 功能验收
- ✅ WNET5成功加载假频数据集并开始训练
- ✅ 训练过程稳定，loss正常下降
- ✅ 假频补偿评分在0.7以上
- ✅ 单频测试覆盖5-200Hz范围
- ✅ 实时处理延迟小于50ms（4000点数据）

### 性能验收
- ✅ GPU利用率达到80%以上
- ✅ 训练收敛时间不超过8小时
- ✅ 模型文件大小控制在100MB以内
- ✅ 内存使用峰值不超过8GB

### 质量验收
- ✅ 假频抑制比达到20dB以上
- ✅ 信噪比改善10dB以上
- ✅ 时域相关性0.9以上
- ✅ 综合评分0.8以上

## 总结

本实施计划基于现有成熟的WNET5基础设施，通过**最小化修改**实现**最大化效果**。重点在于：

1. **配置驱动**：通过配置文件控制假频补偿模式
2. **渐进增强**：在现有框架基础上逐步添加假频专用功能
3. **完整测试**：建立全面的评估和验证体系
4. **生产就绪**：提供完整的部署和使用接口

预期在3周内完成高质量的WNET5假频补偿算法实施，为后续优化迭代奠定坚实基础。