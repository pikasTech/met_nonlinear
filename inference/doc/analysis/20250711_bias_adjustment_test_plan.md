# WaveNet5 偏置调整测试计划

## 背景

基于近期偏置补偿功能的开发（见git log c3bf5f7, 17828c9），本测试计划旨在验证在项目 `WNET5q1h2u6l3` 中添加 `inference_config` 偏置调整配置的效果，比较开启/关闭偏置调整对推理结果的影响。

## 测试目标

1. 验证 `inference_config` 配置的正确加载和应用
2. 比较启用/禁用偏置调整时的推理结果差异
3. 分析偏置调整对前两层推理结果的具体影响
4. 为后续偏置补偿优化提供数据支持

## 测试环境

- **项目路径**: `/mnt/f/Work/met_nonlinear_worktrees/met_nonlinear_master/projects/WNET5q1h2u6l3/`
- **模型类型**: WaveNet5
- **数据集**: MET
- **推理层数限制**: 仅测试前2层（--max-layers 2）
- **测试方式**: 使用 `cli.py -i` 命令进行推理

## 测试配置

### 基础配置（当前）
```json
{
    "epoch_train": 30000,
    "step_per_epoch": 1,
    "learning_rate": 0.02,
    "auto_lr_decay_steps": 1000,
    "dataset_type": "MET",
    "use_model": "WaveNet5",
    "model_subcfg": {
        "init_center_freqs": [10, 80],         
        "init_quality_factors": [1.0, 1.0],
        "post_dense": true,
        "post_dense_activation": "relu",
        "post_dense_units": 6,
        "post_dense_layers": 3
    },
    "use_predict_features": true
}
```

### 目标配置（添加inference_config）
```json
{
    "epoch_train": 30000,
    "step_per_epoch": 1,
    "learning_rate": 0.02,
    "auto_lr_decay_steps": 1000,
    "dataset_type": "MET",
    "use_model": "WaveNet5",
    "model_subcfg": {
        "init_center_freqs": [10, 80],         
        "init_quality_factors": [1.0, 1.0],
        "post_dense": true,
        "post_dense_activation": "relu",
        "post_dense_units": 6,
        "post_dense_layers": 3
    },
    "use_predict_features": true,
    "inference_config": {
        "bias_compensation": {
            "enabled": true,
            "bias_adjustment_matrix": [0.001, -0.002, 0.0015, 0.001, -0.001, 0.002],
            "layer_bias_adjustments": {
                "0": [0.001, -0.001, 0.0005],
                "1": [0.002, -0.002, 0.001]
            }
        }
    }
}
```

## 测试用例

### TC-1: 配置验证测试
**目标**: 验证 inference_config 配置正确加载
**步骤**:
1. 修改 `config.json` 添加 `inference_config`
2. 使用 `python cli.py -p WNET5q1h2u6l3 --config-check` 验证配置加载
3. 检查日志输出确认偏置补偿配置已识别

**期望结果**:
- 配置文件加载成功
- 偏置补偿功能状态正确显示
- 无配置错误警告

### TC-2: 偏置调整启用测试
**目标**: 测试启用偏置调整时的推理性能
**步骤**:
1. 确保 `inference_config.bias_compensation.enabled = true`
2. 执行推理命令: `python cli.py -i -p WNET5q1h2u6l3 --max-layers 2`
3. 记录推理时间、内存使用和输出结果
4. 保存推理结果文件（含时间戳）

**期望结果**:
- 推理成功完成
- 输出文件包含偏置调整后的结果
- 日志显示偏置补偿已应用

### TC-3: 偏置调整禁用测试
**目标**: 测试禁用偏置调整时的推理性能
**步骤**:
1. 修改 `inference_config.bias_compensation.enabled = false`
2. 执行相同推理命令: `python cli.py -i -p WNET5q1h2u6l3 --max-layers 2`
3. 记录推理时间、内存使用和输出结果
4. 保存推理结果文件（含时间戳）

**期望结果**:
- 推理成功完成
- 输出文件不包含偏置调整
- 日志显示偏置补偿已跳过

### TC-4: 结果差异分析测试
**目标**: 量化分析启用/禁用偏置调整的差异
**步骤**:
1. 使用 `python cli.py -a WNET5q1h2u6l3` 执行偏置误差分析
2. 比较TC-2和TC-3的输出结果文件
3. 计算数值差异统计（均值、方差、最大差异）
4. 分析偏置调整对各通道的影响

**期望结果**:
- 偏置误差分析报告生成
- 量化的差异数据
- 各通道影响分析结果

### TC-5: 性能基准测试
**目标**: 评估偏置调整对推理性能的影响
**步骤**:
1. 多次运行TC-2和TC-3（各5次）
2. 统计推理时间差异
3. 监控内存使用变化
4. 评估计算开销

**期望结果**:
- 性能影响数据
- 推理时间对比
- 内存使用对比

## 成功标准

### 功能性标准
1. **配置加载**: inference_config 配置成功加载，无错误
2. **功能开关**: 偏置调整启用/禁用状态正确响应
3. **推理完成**: 两种模式下推理均成功完成
4. **结果差异**: 启用偏置调整后结果有可测量的差异

### 性能标准
1. **时间开销**: 偏置调整引入的额外时间 < 10%
2. **内存开销**: 额外内存使用 < 5%
3. **数值稳定性**: 偏置调整值在合理范围内（10^-4 ~ 10^-2）

### 质量标准
1. **可重现性**: 相同配置下结果一致
2. **健壮性**: 各种输入数据下功能稳定
3. **文档完整**: 测试过程和结果完整记录

## 风险评估

### 高风险
- **配置冲突**: inference_config 与现有配置冲突
- **数值不稳定**: 偏置调整值过大导致结果异常
- **性能劣化**: 偏置补偿显著影响推理速度

### 中风险  
- **兼容性问题**: 与现有推理流程兼容性问题
- **内存使用**: 偏置矩阵存储额外内存开销
- **调试复杂**: 问题排查难度增加

### 低风险
- **配置维护**: 额外配置项维护成本
- **用户学习**: 新功能学习成本

## 测试数据收集

### 性能指标
```json
{
    "test_case": "TC-X",
    "timestamp": "2025-07-11T10:00:00Z",
    "configuration": {
        "bias_enabled": true/false,
        "max_layers": 2,
        "model": "WaveNet5"
    },
    "performance": {
        "inference_time_ms": 0,
        "memory_usage_mb": 0,
        "cpu_usage_percent": 0
    },
    "results": {
        "output_file": "path/to/result.json",
        "checksum": "sha256hash",
        "layer_outputs": []
    }
}
```

### 差异分析数据
```json
{
    "comparison": {
        "enabled_vs_disabled": {
            "mean_difference": 0.0,
            "max_difference": 0.0,
            "std_difference": 0.0,
            "channel_differences": [],
            "layer_differences": []
        }
    }
}
```

## 交付物

1. **测试执行日志**: 完整的测试执行过程记录
2. **配置文件**: 修改后的 config.json 文件
3. **推理结果**: 启用/禁用偏置调整的推理输出文件
4. **性能报告**: 性能对比分析数据
5. **差异分析报告**: 数值差异详细分析
6. **测试报告**: 完整的测试执行报告

## 附录

### A. 命令参考
```bash
# 配置验证
python cli.py -p WNET5q1h2u6l3 --config-check

# 推理执行（限制2层）
python cli.py -i -p WNET5q1h2u6l3 --max-layers 2

# 偏置误差分析
python cli.py -a WNET5q1h2u6l3

# 性能监控
time python cli.py -i -p WNET5q1h2u6l3 --max-layers 2
```

### B. 期望输出文件结构
```
projects/WNET5q1h2u6l3/
├── config.json (修改后)
├── inference_results/
│   ├── bias_enabled_20250711_HHMMSS.json
│   ├── bias_disabled_20250711_HHMMSS.json
│   └── bias_analysis_20250711_HHMMSS.json
└── test_logs/
    └── bias_adjustment_test_20250711_HHMMSS.log
```

### C. 故障排除指南
1. **配置加载失败**: 检查JSON语法和必需字段
2. **推理错误**: 检查模型文件和数据路径
3. **性能异常**: 监控系统资源使用情况
4. **结果异常**: 验证偏置调整参数范围