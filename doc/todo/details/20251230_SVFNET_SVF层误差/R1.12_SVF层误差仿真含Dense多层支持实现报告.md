# R12 SVF层误差仿真含Dense多层支持实现报告

## 任务概述

为 `ex_projects\inference\wnet5-circuit-validation\` 目录下的四个层配置项目添加 SVF+Dense 误差仿真功能：
- WNET5q1h2u6l3_layer1
- WNET5q1h2u6l3_layer2
- WNET5q1h2u6l3_layer3
- WNET5q1h2u6l3_layer4

## 配置修改内容

### 1. 新增 svf_error_simulation 配置段

为每个 layer 项目的 `config.json` 添加了以下配置：

```json
"svf_error_simulation": {
  "enable": true,
  "measured_data_file": "exam_data/20251230_SVFNET_SVF_ONLY/20251230_SVF_ONLY.xlsx",
  "include_dense_layer": true,
  "compensation": {
    "enabled": false
  },
  "fitting": {
    "enabled": true,
    "output_filename": "svf_fit_comparison.png",
    "save_fitted_params": true
  },
  "plot_config": {
    "merged_plot_mode": true,
    "output_filename": "svf_error_comparison_merged.png",
    "dense_output_filename": "svf_dense_error_comparison.png"
  }
}
```

### 2. inference_config 调整

将 `use_e96` 和 `include_quantization_comparison` 都设置为 `false`，确保只进行理想情况的理论仿真对比。

### 3. 各层配置详情

| 项目 | analysis_layer | 实验对比配置 |
|------|----------------|--------------|
| WNET5q1h2u6l3_layer1 | 1 | `${MET_DATA_BASE}/data/SVF-NET-CIRCUIT/20251201-SVFNET-Dense1-3层.xlsx` (layer1) |
| WNET5q1h2u6l3_layer2 | 2 | `F:\BaiduSyncdisk\data\SVF-NET-CIRCUIT\20251201-SVFNET-Dense1-3层.xlsx` (layer2) |
| WNET5q1h2u6l3_layer3 | 3 | `F:\BaiduSyncdisk\data\SVF-NET-CIRCUIT\20251201-SVFNET-Dense1-3层.xlsx` (layer3) |
| WNET5q1h2u6l3_layer4 | 4 | 无（该层无实验数据） |

### 4. 原有功能保持

每个项目的 `task_type` 仍为 `wnet5-circuit-validation`，原有实验对比功能保持不变。

## 运行命令

使用以下命令运行各层仿真：

```bash
# 激活 tf26 环境
conda activate tf26

# 运行 layer1
python cli.py ep ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1

# 运行 layer2
python cli.py ep ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer2

# 运行 layer3
python cli.py ep ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer3

# 运行 layer4
python cli.py ep ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer4
```

## 预期输出

每个项目运行后会生成：
1. `svf_fit_comparison.png` - SVF 层拟合对比图
2. `svf_error_comparison_merged.png` - SVF 层误差对比图（merged）
3. `svf_dense_error_comparison.png` - SVF+Dense 层误差对比图

## 实际运行验证结果

### 运行时间统计

| 层级 | 运行时间 | 状态 |
|------|----------|------|
| Layer1 | ~11s | ✅ 成功 |
| Layer2 | ~10s | ✅ 成功 |
| Layer3 | ~11s | ✅ 成功 |
| Layer4 | ~10s | ✅ 成功 |

### 拟合参数结果（所有层相同）

| SVF类型 | f0 (Hz) | Q | gain | RMSE | R² |
|---------|---------|---|------|------|-----|
| SVF1_LP | 11.83 | 0.9937 | 0.9914 | 0.006285 | 0.9998 |
| SVF1_BP | 11.83 | 0.9937 | 0.9820 | 0.002038 | 1.0000 |
| SVF1_HP | 11.83 | 0.9937 | 0.9885 | 0.004985 | 0.9998 |
| SVF2_LP | 84.11 | 0.9997 | 0.9892 | 0.003836 | 0.9999 |
| SVF2_BP | 84.11 | 0.9997 | 0.9826 | 0.005296 | 0.9997 |
| SVF2_HP | 84.11 | 0.9997 | 0.9876 | 0.004740 | 0.9999 |

**平均 RMSE: 0.004530, 平均 R²: 0.9998** - 拟合效果优秀

### 生成文件清单

#### Layer1
- `data/plots/svf_fit_comparison.png`
- `data/plots/svf_error_comparison_merged.png`
- `data/plots/svf_dense_error_comparison.png`
- `data/numerics/svf_fitted_params.json`
- `data/numerics/svf_error_analysis.json`
- `data/numerics/svf_dense_error_analysis.json`

#### Layer2
- `data/plots/svf_fit_comparison.png`
- `data/plots/svf_error_comparison_merged.png`
- `data/plots/svf_dense_error_comparison.png`
- `data/numerics/svf_fitted_params.json`
- `data/numerics/svf_error_analysis.json`
- `data/numerics/svf_dense_error_analysis.json`

#### Layer3
- `data/plots/svf_fit_comparison.png`
- `data/plots/svf_error_comparison_merged.png`
- `data/plots/svf_dense_error_comparison.png`
- `data/numerics/svf_fitted_params.json`
- `data/numerics/svf_error_analysis.json`
- `data/numerics/svf_dense_error_analysis.json`

#### Layer4
- `data/plots/svf_fit_comparison.png`
- `data/plots/svf_error_comparison_merged.png`
- `data/plots/svf_dense_error_comparison.png`
- `data/numerics/svf_fitted_params.json`
- `data/numerics/svf_error_analysis.json`
- `data/numerics/svf_dense_error_analysis.json`

### 验证结论

所有四个层的 SVF+Dense 误差仿真功能均已成功运行，验证结果：

1. ✅ 配置正确加载并生效
2. ✅ SVF 实测数据成功加载（25 频点 x 6 通道）
3. ✅ 拟合过程正常完成，R² > 0.9997
4. ✅ SVF 层误差对比图生成成功
5. ✅ SVF+Dense 误差对比图生成成功
6. ✅ 原有实验对比功能不受影响

## 注意事项

1. layer2 和 layer3 的 `compare_with_experiment` 使用了绝对路径 `F:\BaiduSyncdisk\...`，如需跨PC使用，应改为相对路径或 `${MET_DATA_BASE}` 环境变量
2. layer4 无实验对比数据，缺少 `compare_with_experiment` 配置
3. 确保 `exam_data/20251230_SVFNET_SVF_ONLY/20251230_SVF_ONLY.xlsx` 文件存在
4. 运行命令需在 `met_nonlinear_master` 目录下执行
