# 训练功能说明

## 功能概述

`python cli.py -t PROJECT_NAME` 用于训练 MET Nonlinear 模型，支持实时进度监控、权重保存和训练日志记录。

## 训练流程

1. **数据集加载** - 根据 `config.json` 中的 `dataset_type` 加载数据集
2. **模型构建** - 初始化模型结构（FRIKAN/WNET5/LSTM等）
3. **训练执行** - 使用 TensorFlow Keras 进行训练，支持实时回调
4. **权重保存** - 自动保存最佳验证权重和最终权重
5. **评估输出** - 输出训练集/验证集的 loss、MAE、AFMAE 指标

## 配置参数

在项目 `config.json` 中配置：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `epoch_train` | 训练轮数 | - |
| `dataset_type` | 数据集类型（如 MET_COMP） | - |
| `use_model` | 模型类型（FRIKAN/WNET5/LSTM） | - |
| `H_UNITS` | 隐藏单元数 | - |
| `use_train_model` | 是否使用训练模式 | true |
| `adjust_weight` | 是否启用交互式权重调整 | false |

## 输出文件

训练完成后在 `projects/PROJECT_NAME/data/` 目录下生成：

- `best_val.weights.h5` - 最佳验证权重
- `best.weights.h5` - 最终权重
- `training_log.jsonl` - 训练日志（loss, val_loss, lr, epoch）
- `training_info.json` - 训练统计摘要
- `model_info.json` - 模型结构信息

## 训练监控

训练过程支持：
- 实时 loss 显示
- 平滑速度估算（指数移动平均）
- 剩余时间预测
- 验证 loss 追踪

## 相关命令

- `python cli.py -e PROJECT_NAME` - 评估已训练模型
- `python cli.py --loss-plot PROJECT_NAME` - 绘制训练 loss 曲线
