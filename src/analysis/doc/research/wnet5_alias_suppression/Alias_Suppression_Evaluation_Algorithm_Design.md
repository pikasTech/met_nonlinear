# 假频抑制效果评估算法设计方案

## 背景

在WNET5_RealAlias项目中，我们需要评估神经网络模型对电化学系统中假频（aliasing）的抑制效果。根据linear_response.json数据分析，假频主要集中在90-100Hz频段，表现为频响曲线的剧烈波动。

## 数据结构分析

### linear_response.json内容
- **gains_origin**: 原始系统的频响灵敏度值（单位：V/m/s）
- **gains_comped**: 补偿后的频响灵敏度值（单位：V/m/s）
- **frequencies**: 对应的频率点（10Hz-430Hz，90-120Hz区间采样密集）
- **magnitudes**: 测试信号幅度（1.2）
- **fit_params_origin/comped**: 拟合参数（用于多项式拟合）

### 关键观察
1. 在90-100Hz区间，原始信号出现显著波动（最大值：210.17 V/m/s，最小值：196.72 V/m/s）
2. 补偿后信号在同区间波动明显减小（最大值：207.59 V/m/s，最小值：202.43 V/m/s）
3. 频率采样在关键区间更密集（0.25Hz间隔）

## 评估算法设计

### 核心指标：假频抑制率（Alias Suppression Ratio, ASR）

#### 1. 局部波动幅度计算
```
局部波动幅度 = max(gains) - min(gains)  # 在指定频段内
```

#### 2. 假频抑制率计算
```
ASR = (原始波动幅度 - 补偿后波动幅度) / 原始波动幅度 × 100%
```

### 评估指标体系

#### 主要指标
1. **假频区间抑制率（ASR_90_100）**
   - 计算90-100Hz区间的抑制效果
   - 权重：40%

2. **扩展区间抑制率（ASR_85_105）**
   - 计算85-105Hz更宽区间的抑制效果
   - 权重：30%

3. **峰值改善率（Peak Improvement Ratio, PIR）**
   - 计算假频区间内最大偏离的改善程度
   - 权重：20%

4. **平滑度提升（Smoothness Enhancement, SE）**
   - 基于一阶导数的频响曲线平滑度评估
   - 权重：10%

#### 辅助指标
1. **有效带宽保持率**：确保补偿不影响正常频段
2. **相位一致性**：评估补偿后的相位特性（如有相位数据）
3. **稳定性指标**：多次测量的结果一致性

### 算法实现步骤

```python
def evaluate_alias_suppression(linear_response_data):
    """
    评估假频抑制效果
    
    参数:
        linear_response_data: 包含gains_origin, gains_comped, frequencies的字典
    
    返回:
        evaluation_results: 包含各项评估指标的字典
    """
    
    # 1. 提取数据
    gains_origin = linear_response_data['gains_origin'][0]
    gains_comped = linear_response_data['gains_comped'][0]
    frequencies = linear_response_data['frequencies']
    
    # 2. 定义评估频段
    freq_bands = {
        'core': (90, 100),      # 核心假频区间
        'extended': (85, 105),  # 扩展评估区间
        'full': (10, 120)       # 完整低频段
    }
    
    # 3. 计算各频段指标
    results = {}
    for band_name, (f_min, f_max) in freq_bands.items():
        # 获取频段内的数据索引
        indices = [i for i, f in enumerate(frequencies) if f_min <= f <= f_max]
        
        # 提取频段内的增益值
        gains_orig_band = [gains_origin[i] for i in indices]
        gains_comp_band = [gains_comped[i] for i in indices]
        
        # 计算波动幅度（单位：V/m/s）
        ripple_orig = max(gains_orig_band) - min(gains_orig_band)
        ripple_comp = max(gains_comp_band) - min(gains_comp_band)
        
        # 计算抑制率
        suppression_ratio = (ripple_orig - ripple_comp) / ripple_orig * 100
        
        # 存储结果
        results[f'ASR_{band_name}'] = {
            'suppression_ratio': suppression_ratio,
            'original_ripple': ripple_orig,
            'compensated_ripple': ripple_comp,
            'frequency_range': (f_min, f_max)
        }
    
    # 4. 计算平滑度指标
    smoothness_orig = calculate_smoothness(gains_origin, indices)
    smoothness_comp = calculate_smoothness(gains_comped, indices)
    results['smoothness_enhancement'] = (smoothness_comp - smoothness_orig) / smoothness_orig * 100
    
    # 5. 计算综合评分
    weights = {
        'ASR_core': 0.4,
        'ASR_extended': 0.3,
        'PIR': 0.2,
        'SE': 0.1
    }
    
    overall_score = calculate_weighted_score(results, weights)
    results['overall_score'] = overall_score
    
    return results
```

### 评估标准

#### 抑制效果分级
- **优秀（Excellent）**: ASR > 70%
- **良好（Good）**: 50% < ASR ≤ 70%
- **中等（Moderate）**: 30% < ASR ≤ 50%
- **较差（Poor）**: 10% < ASR ≤ 30%
- **无效（Ineffective）**: ASR ≤ 10%

#### 综合评分标准
- **A级**：综合评分 > 80，所有主要指标均为良好以上
- **B级**：综合评分 60-80，核心指标良好
- **C级**：综合评分 40-60，有一定改善效果
- **D级**：综合评分 < 40，改善效果不明显

## 实施建议

### 1. 数据预处理
- 验证数据完整性（频率点连续性、数值合理性）
- 异常值检测和处理
- 必要时进行插值以获得均匀采样

### 2. 可视化支持
- 绘制原始和补偿后的频响曲线对比图
- 标注假频区间和改善程度
- 生成评估报告的可视化摘要

### 3. 批量评估流程
```python
def batch_evaluate_experiments(experiment_list):
    """批量评估多个实验的假频抑制效果"""
    results_summary = []
    
    for exp_name in experiment_list:
        # 加载实验数据
        data_path = f'projects/{exp_name}/data/linear_response.json'
        
        # 执行评估
        evaluation = evaluate_alias_suppression(load_json(data_path))
        
        # 汇总结果
        results_summary.append({
            'experiment': exp_name,
            'ASR_core': evaluation['ASR_core']['suppression_ratio'],
            'overall_score': evaluation['overall_score'],
            'grade': determine_grade(evaluation['overall_score'])
        })
    
    # 生成对比报告
    generate_comparison_report(results_summary)
    
    return results_summary
```

### 4. 集成建议
- 将评估算法集成到`model_analysis.py`模块
- 在训练完成后自动执行评估
- 支持实时监控训练过程中的假频抑制效果

## 预期应用

### 1. 实验效果对比
基于当前基线数据的初步计算：
- 核心区间（90-100Hz）原始波动：约13.45 V/m/s
- 补偿后波动：约5.16 V/m/s
- **预估ASR_core：61.6%**（良好水平）

### 2. 实验优化指导
- 实时评估可帮助调整超参数
- 识别最有效的模型配置
- 指导频率点选择和滤波器设计

### 3. 自动化实验筛选
- 设定最低ASR阈值（如30%）自动筛选有效实验
- 基于综合评分排序实验结果
- 生成最优配置推荐

## 后续优化方向

1. **多维度评估**：考虑相位响应、群延迟等指标
2. **自适应频段**：根据数据自动识别假频区间
3. **统计显著性**：引入多次测量的统计分析
4. **实时评估**：支持训练过程中的动态评估
5. **领域知识集成**：结合电化学系统特性优化评估权重

---

*文档版本: v1.0*  
*创建日期: 2025-01-07*  
*作者: AI Assistant*