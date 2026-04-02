# LUT 功能说明

## 功能概述

`python cli.py -l PROJECT_NAME` 用于生成模型的查找表 (LUT) 表示，用于快速推理或硬件部署。

## 基本用法

```bash
python cli.py -l PROJECT_NAME
```

## LUT 生成流程

1. 加载训练好的模型权重
2. 将权重转换为 LUT 格式
3. 使用测试数据验证 LUT 输出
4. 对比 LUT 输出与模型原始输出

## LUT 模型

`ModelKAN_LUT` 类实现 LUT 功能：

- `lut_points` - LUT 采样点数（默认 800）
- `forward()` - LUT 前向推理
- `load_weights_json()` - 从 JSON 加载权重

## 输出

- LUT 模型参数
- LUT vs Model 输出对比图
- 误差统计

## 应用场景

- 快速原型验证
- 嵌入式部署
- 硬件协同仿真

## 相关命令

- `python cli.py -i PROJECT_NAME` - 标准推理
- `python cli.py -m PROJECT_NAME` - 模型信息
