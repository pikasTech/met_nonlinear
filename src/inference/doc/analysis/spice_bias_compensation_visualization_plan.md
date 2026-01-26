# SPICE偏置补偿可视化方案

## 概述

本文档制定了WNET5q1h2u6l3项目中SPICE推理结果的综合可视化方案，用于分析和对比基准配置与偏置补偿配置之间的差异。分析重点是可视化第1-3层偏置补偿带来的改进效果。所有可视化设计遵循学术汇报标准，强调准确性、科学性和严谨性。

## 数据摘要

### 基准配置 (`inference_baseline`)
- **未应用偏置补偿**
- **NN-SPICE偏置误差摘要**：
  - 总体平均偏置：0.00498
  - 总体标准差：0.01327
  - 最大偏置误差：0.06776（第5层，通道0）
  - 受影响最大的层：第2层（均值：0.00558）、第5层（均值：0.06776）

### 补偿配置 (`inference_c123`)
- **对第1、2、3层应用了偏置补偿**
- **NN-SPICE偏置误差摘要**：
  - 总体平均偏置：0.00109（降低78%）
  - 总体标准差：0.00198（降低85%）
  - 最大偏置误差：0.00891（降低87%，第5层，通道0）
  - 改进最大的层：第2层（降低80%）、第3层（降低40%）

### 关键观察
1. **整体偏置指标大幅改善**（降低78-87%）
2. **第1层**：原本偏置已经很低，变化最小
3. **第2-3层**：补偿后显著改善
4. **第4层**：尽管未直接补偿，但有适度改善
5. **第5层**：作为累积效应，大幅改善（降低87%）

## 可视化组件

### 1. 总览分析

#### 1.1 整体偏置误差对比表
- **类型**：标准学术表格
- **内容**：
  - 总体平均偏置（基准 vs 补偿后）
  - 总体标准差（基准 vs 补偿后）
  - 最大偏置误差（基准 vs 补偿后）
  - 改进百分比
- **格式**：LaTeX风格表格，包含标准差和置信区间

#### 1.2 逐层改进条形图
- **类型**：标准条形图
- **数据**：每层的平均偏置误差改进百分比
- **特征**：误差条显示标准差，数值标注在条形上方

### 2. 逐层分析

#### 2.1 偏置误差对比条形图
- **类型**：分组条形图（每层一个）
- **布局**：2×3子图网格显示全部5层
- **特征**：
  - 基准误差（深灰色条）
  - 补偿后误差（浅灰色条）
  - 误差条显示标准差
  - Y轴使用对数刻度（如需要）
  - 精确数值标注

#### 2.2 层间偏置误差传播图
- **类型**：折线图
- **X轴**：层索引（1-5）
- **Y轴**：平均偏置误差
- **线条**：基准（实线）vs 补偿后（虚线）
- **特征**：误差条、图例、网格线

### 3. 通道级分析

#### 3.1 偏置误差热力图
- **类型**：5×6热力图（层×通道）
- **子图**：基准和补偿后并排对比
- **配色**：科学配色方案（viridis或coolwarm）
- **标注**：精确数值显示在每个单元格

#### 3.2 通道偏置误差箱线图
- **类型**：分组箱线图
- **分组**：按层分组，每组显示该层所有通道
- **特征**：
  - 显示中位数、四分位数、异常值
  - 均值用菱形标记
  - 基准和补偿后并排对比

### 4. 误差分布分析

#### 4.1 误差分布直方图
- **类型**：规范化直方图
- **数据**：所有通道的偏置误差
- **特征**：
  - 基准和补偿后使用不同填充模式
  - 添加核密度估计曲线
  - 标注均值和标准差
  - 使用半透明重叠显示

#### 4.2 累积分布函数（CDF）图
- **类型**：CDF曲线
- **用途**：显示误差分布的累积特性
- **特征**：基准vs补偿后对比，标注关键百分位点

### 5. 统计分析

#### 5.1 相关性分析热力图
- **类型**：相关系数矩阵热力图
- **数据**：层间偏置误差相关性
- **标注**：相关系数值显示在单元格中

#### 5.2 改进效果散点图
- **类型**：散点图
- **X轴**：基准偏置误差
- **Y轴**：补偿后偏置误差
- **特征**：
  - 对角线表示无改进
  - 点按层着色
  - 添加线性回归线

### 6. 综合统计表

#### 6.1 详细统计汇总表
- **格式**：学术规范表格
- **内容**：
  - 每层的均值、标准差、最大值、最小值
  - 基准和补偿后对比
  - 改进百分比和p值（如适用）
- **导出**：PNG图表形式，同时生成可直接用于论文的LaTeX代码

## 实现方案

### 文件组织结构
```
inference/
├── doc/
│   └── analysis/
│       └── spice_bias_compensation_visualization_plan.md  # 本文档
├── tools/
│   └── visualization/
│       ├── spice_bias_comparison.py     # 主可视化脚本
│       ├── config.json                  # 默认配置文件
│       ├── utils/
│       │   ├── data_loader.py           # 数据加载工具
│       │   ├── plot_helpers.py          # 绘图辅助函数
│       │   └── statistics.py            # 统计计算工具
│       └── README.md                    # 使用说明
└── results/
    └── bias_comparison/                 # 输出根目录
        ├── figures/                     # PNG图表目录
        │   ├── overview/                # 总览图表
        │   ├── layer_analysis/          # 逐层分析图表
        │   ├── channel_analysis/        # 通道分析图表
        │   ├── distribution/            # 分布分析图表
        │   └── statistics/              # 统计表格
        └── figures/raw/                 # 原始数据目录
            ├── overview/                # 总览图表数据
            ├── layer_analysis/          # 逐层分析数据
            ├── channel_analysis/        # 通道分析数据
            ├── distribution/            # 分布分析数据
            └── statistics/              # 统计表格数据
```

### CLI接口设计

```bash
# 基本用法
python inference/tools/visualization/spice_bias_comparison.py \
    --baseline projects/WNET5q1h2u6l3/data/inference_baseline \
    --compensated projects/WNET5q1h2u6l3/data/inference_c123 \
    --output inference/results/bias_comparison \
    --config inference/tools/visualization/config.json
```

### 配置文件示例（config.json）
```json
{
  "plots": {
    "overview": true,
    "layer_analysis": true,
    "channel_analysis": true,
    "distribution": true,
    "statistics": true
  },
  "figure": {
    "dpi": 300,
    "figsize": [10, 8],
    "font_size": 12,
    "style": "seaborn-v0_8-paper"
  },
  "colors": {
    "baseline": "#666666",
    "compensated": "#999999",
    "colormap": "viridis"
  },
  "statistics": {
    "confidence_level": 0.95,
    "show_pvalues": true
  },
  "output": {
    "format": "png",
    "raw_data_format": "json",
    "latex_tables": true,
    "save_raw_data": true
  }
}
```

### 命令行参数说明
- `--baseline`：基准推理结果目录（必需）
- `--compensated`：补偿后推理结果目录（必需）
- `--output`：PNG输出目录（默认：`inference/results/bias_comparison`）
- `--config`：配置文件路径（可选，默认使用同目录下的config.json）

## 技术要求

### 依赖项
- `numpy`：数值计算
- `matplotlib`：核心绘图（使用学术风格）
- `seaborn`：统计可视化
- `scipy`：统计检验和相关性分析
- `json`：配置文件和数据导出

### 输出规范

#### PNG图表输出
- **格式**：PNG格式（300 DPI）
- **路径**：`figures/` 子目录
- **命名规则**：
  - 总览：`overview_<analysis_type>.png`
  - 逐层：`layer_<layer_num>_<plot_type>.png`
  - 通道：`channel_<analysis_type>.png`
  - 分布：`distribution_<plot_type>.png`
  - 统计：`statistics_<table_type>.png`

#### 原始数据输出
- **格式**：JSON格式（默认）或CSV格式
- **路径**：`figures/raw/` 对应子目录
- **命名规则**：与PNG文件一一对应，扩展名为`.json`或`.csv`
- **数据结构示例**（JSON）：
```json
{
  "plot_type": "layer_bias_comparison",
  "timestamp": "2025-07-13T10:00:00",
  "data": {
    "x_labels": ["Channel 0", "Channel 1", ...],
    "baseline": [0.00532, 0.00228, ...],
    "compensated": [0.00089, 0.00074, ...],
    "error_bars": {
      "baseline": [0.0012, 0.0008, ...],
      "compensated": [0.0003, 0.0002, ...]
    }
  },
  "metadata": {
    "layer": 2,
    "units": "bias_error",
    "sample_size": 1400000
  }
}

### 绘图规范
- **字体**：Times New Roman或Arial
- **字号**：标题14pt，轴标签12pt，刻度10pt
- **线宽**：1.5pt
- **网格**：浅灰色虚线
- **配色**：灰度为主，必要时使用科学配色
- **图例**：清晰标注，位置不遮挡数据

## 学术规范要求

### 数据呈现
- 所有数值保留适当有效数字（通常3-4位）
- 包含误差条或置信区间
- 明确标注单位
- 使用标准统计符号

### 图表要求
- 清晰的标题描述
- 完整的轴标签和单位
- 适当的刻度范围
- 避免3D效果和装饰性元素
- 黑白打印友好

### 统计严谨性
- 报告样本数量
- 包含统计显著性检验（如适用）
- 明确说明使用的统计方法
- 提供原始数据的获取方式

## 交付物

1. **主可视化脚本**（`spice_bias_comparison.py`）
   - 模块化设计
   - 完善的错误处理
   - 详细的日志输出

2. **配置文件**（`config.json`）
   - 所有可调参数
   - 清晰的注释说明

3. **PNG图表集**（`inference/results/bias_comparison/figures/`）
   - 高质量学术图表
   - 统一的视觉风格
   - 可直接用于论文和报告

4. **原始数据文件**（`inference/results/bias_comparison/figures/raw/`）
   - 每个图表对应的原始数据
   - JSON格式，包含完整元数据
   - 支持数据复现和二次分析

5. **LaTeX表格**（可选输出）
   - 格式化的统计表格
   - 可直接插入论文

## 预期成果

通过这套可视化方案，将提供：
- 偏置补偿效果的定量分析
- 符合学术标准的可视化结果
- 可重现的分析流程
- 为论文和技术报告提供的高质量图表

该方案强调科学严谨性，避免过度设计，专注于准确传达偏置补偿在SPICE电路实现中的改进效果。