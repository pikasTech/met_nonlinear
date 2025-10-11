# SPICE偏置补偿可视化工具

## 概述

本工具用于对比分析SPICE推理的基准结果和偏置补偿后的结果，生成学术风格的可视化图表。

## 安装要求

```bash
pip install numpy matplotlib seaborn scipy
```

## 基本使用

```bash
python spice_bias_comparison.py \
    --baseline <基准推理目录> \
    --compensated <补偿后推理目录> \
    --output <输出目录>
```

### 示例

```bash
python inference\tools\visualization\spice_bias_comparison.py --baseline "F:\Work\met_nonlinear_worktrees\met_nonlinear_master\projects\WNET5q1h2u6l3\data\inference_baseline" --compensated "F:\Work\met_nonlinear_worktrees\met_nonlinear_master\projects\WNET5q1h2u6l3\data\inference_c123"
```

## 配置文件

可以通过`--config`参数指定配置文件，否则使用默认的`config.json`：

```json
{
  "plots": {
    "overview": true,        // 生成总览图表
    "layer_analysis": true,  // 生成逐层分析图表
    "channel_analysis": true,// 生成通道分析图表
    "distribution": true,    // 生成分布分析图表
    "statistics": true       // 生成统计表格
  },
  "figure": {
    "dpi": 300,             // PNG分辨率
    "figsize": [10, 8],     // 图表尺寸
    "font_size": 12         // 字体大小
  },
  "output": {
    "format": "png",
    "raw_data_format": "json",
    "latex_tables": true,    // 生成LaTeX表格
    "save_raw_data": true    // 保存原始数据
  }
}
```

## 输出结构

```
<output_dir>/
├── figures/                    # PNG图表
│   ├── overview/              # 总览分析
│   ├── layer_analysis/        # 逐层分析
│   ├── channel_analysis/      # 通道分析
│   ├── distribution/          # 分布分析
│   └── statistics/            # 统计表格
├── figures/raw/               # 原始数据（JSON格式）
│   └── [与figures相同的子目录结构]
└── visualization_report.json  # 可视化报告
```

## 生成的图表

1. **总览分析**
   - `overview_global_improvement.png` - 全局改进条形图
   - `overview_layer_improvement_trend.png` - 逐层改进趋势图

2. **逐层分析**
   - `layer_N_bias_comparison.png` - 第N层偏置误差对比

3. **通道分析**
   - `channel_bias_error_heatmap.png` - 偏置误差热力图

4. **分布分析**
   - `distribution_error_histogram.png` - 误差分布直方图

5. **统计表格**
   - `statistics_summary_table.png` - 统计汇总表
   - `statistics_summary_table.tex` - LaTeX格式表格

## 原始数据格式

每个图表都有对应的JSON数据文件，包含：
- `timestamp` - 生成时间戳
- `plot_type` - 图表类型
- `data` - 绘图数据
- `metadata` - 元数据（单位、样本数等）

## 注意事项

1. 输入目录必须包含`error_analysis.json`文件
2. 中文标签可能需要安装中文字体支持
3. 所有图表采用学术出版标准设计

## 故障排除

如果遇到中文显示问题，可以：
1. 安装中文字体包
2. 或修改`plot_helpers.py`中的字体设置

## 开发者信息

- 主脚本：`spice_bias_comparison.py`
- 数据加载：`utils/data_loader.py`
- 绘图函数：`utils/plot_helpers.py`
- 统计计算：`utils/statistics.py`