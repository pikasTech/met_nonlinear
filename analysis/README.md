# 假频抑制评估分析模块

本模块用于评估神经网络模型对电化学系统中假频（aliasing）的抑制效果。

## 目录结构

```
analysis/
├── __init__.py              # 模块初始化文件
├── alias_suppression.py     # 核心评估算法
├── visualization.py         # 可视化工具
├── example_usage.py         # 使用示例
├── README.md               # 本文档
├── tests/                  # 测试文件
│   ├── __init__.py
│   ├── conftest.py         # pytest配置
│   ├── test_alias_suppression.py  # 单元测试
│   └── test_data/          # 测试数据
│       └── sample_linear_response.json
└── output/                 # 输出目录（运行时创建）
```

## 主要功能

### 1. 假频抑制评估 (`alias_suppression.py`)

- **evaluate_alias_suppression()**: 评估单个项目的假频抑制效果
- **batch_evaluate_experiments()**: 批量评估多个实验
- **calculate_smoothness()**: 计算频响曲线平滑度
- **calculate_peak_improvement()**: 计算峰值改善率
- **determine_grade()**: 确定评估等级（A/B/C/D）

### 2. 可视化工具 (`visualization.py`)

- **visualize_alias_suppression()**: 可视化单个项目的频响对比
- **visualize_batch_results()**: 可视化批量评估结果对比

## 评估指标

1. **假频抑制率（ASR）**: 核心指标，计算90-100Hz区间内频响波动的减少程度
2. **峰值改善率**: 最大偏离的改善程度
3. **平滑度提升**: 基于一阶导数的频响曲线平滑度改善
4. **综合评分**: 加权综合评价（0-100分）

## 评级标准

- **A级**: 综合评分 ≥ 80（优秀）
- **B级**: 综合评分 60-80（良好）
- **C级**: 综合评分 40-60（中等）
- **D级**: 综合评分 < 40（较差）

## 快速开始

### 1. 评估单个项目

```python
from analysis import evaluate_alias_suppression

# 评估项目
results = evaluate_alias_suppression('projects/WNET5_RealAlias/data/linear_response.json')

# 查看结果
print(f"核心区间抑制率: {results['ASR_core']['suppression_ratio']:.1f}%")
print(f"综合评分: {results['overall_score']:.1f}")
print(f"等级: {results['grade']}")
```

### 2. 批量评估

```python
from analysis import batch_evaluate_experiments

# 批量评估
experiments = ['WNET5_RealAlias', 'WNET5_RealAlias_E01', 'WNET5_RealAlias_E02']
results = batch_evaluate_experiments(experiments, 'evaluation_results.json')
```

### 3. 可视化

```python
from analysis.visualization import visualize_alias_suppression

# 生成可视化图像
visualize_alias_suppression(
    'projects/WNET5_RealAlias/data/linear_response.json',
    save_path='alias_suppression_plot.png'
)
```

## 运行测试

```bash
# 运行所有测试
python -m pytest analysis/tests/ -v

# 运行特定测试
python -m pytest analysis/tests/test_alias_suppression.py::TestAliasSuppression::test_evaluate_alias_suppression_with_dict -v
```

## 运行示例

```bash
# 运行完整示例
python analysis/example_usage.py
```

## 数据格式

输入数据需要包含以下字段（JSON格式）：

```json
{
  "gains_origin": [[...]], // 原始频响增益值 (V/m/s)
  "gains_comped": [[...]], // 补偿后频响增益值 (V/m/s)
  "frequencies": [...],    // 对应的频率点 (Hz)
  "magnitudes": [...],     // 测试信号幅度
  "fit_params_origin": [[...]], // 拟合参数（可选）
  "fit_params_comped": [[...]]  // 拟合参数（可选）
}
```

## 注意事项

1. 确保数据中包含90-100Hz的频率点，这是假频评估的核心区间
2. 增益单位为灵敏度（V/m/s），不是分贝（dB）
3. 评估结果会自动保存为JSON格式，便于后续分析

## 扩展开发

如需添加新的评估指标，可以：

1. 在 `alias_suppression.py` 中添加计算函数
2. 在 `evaluate_alias_suppression()` 中集成新指标
3. 更新权重配置和综合评分计算
4. 添加相应的单元测试