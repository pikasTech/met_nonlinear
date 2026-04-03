# 误差分析功能说明

## 功能概述

`python cli.py -a PROJECT_NAME --bias-method METHOD` 用于分析模型的误差特性，支持多种偏置分析方法。

## 偏置分析方法

### 自动模式 (auto)

```bash
python cli.py -a PROJECT_NAME --bias-method auto
```

自动选择最佳分析方法。

### 稳态分析 (steady_state)

```bash
python cli.py -a PROJECT_NAME --bias-method steady_state
```

基于稳态值计算偏置误差。

### 频域分析 (frequency_domain)

```bash
python cli.py -a PROJECT_NAME --bias-method frequency_domain
```

基于频域响应计算偏置误差。

## 自定义参数

可以通过 `--bias-params` 传递 JSON 格式的自定义参数：

```bash
python cli.py -a PROJECT_NAME --bias-params '{"threshold": 0.5, "window_size": 100}'
```

## 分析内容

误差分析主要包括：

1. **全局误差统计** - MAE, MSE, AFMAE 等
2. **偏置误差分析** - 输入偏置对输出误差的影响
3. **误差分布可视化** - 误差随时间/频率的分布
4. **改进指标** - 补偿前后的误差改善百分比

## 输出文件

分析完成后在项目目录下生成：

- 误差统计报告
- 误差分布可视化图
- 偏置改善指标

## 相关命令

- `python cli.py -i PROJECT_NAME` - 运行推理
- `python cli.py --bias-viz PROJECT_NAME` - 偏置可视化对比
