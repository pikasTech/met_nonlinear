# Subprocess Wrapper 使用指南

## 概述

`cli_wrapper.py` 是一个 subprocess 包装器，用于捕获 `cli.py` 的所有输出（stdout/stderr）到日志文件，确保不会丢失任何日志信息。

## 特性

1. **完整日志捕获**：捕获所有 stdout 和 stderr 输出
2. **双重输出**：
   - 终端：显示重要信息（简洁版）
   - 文件：保存完整日志（带时间戳）
3. **智能过滤**：自动识别错误、警告和成功信息
4. **实时显示**：实时显示执行进度
5. **中断处理**：优雅处理 Ctrl+C 中断

## 使用方法

### 直接使用 wrapper

```bash
# 训练项目
conda run -n tf26 python cli_wrapper.py WNET5q0.5h2u6l4

# 推理任务
conda run -n tf26 python cli_wrapper.py -i WNET5q0.5h2u6l4

# 评估任务
conda run -n tf26 python cli_wrapper.py -e WNET5q0.5h2u6l4

# 生成波形数据
conda run -n tf26 python cli_wrapper.py -w WNET5q0.5h2u6l4
```

### 使用便捷脚本

Linux/macOS:
```bash
./cli -i WNET5q0.5h2u6l4
```

Windows:
```batch
cli.bat -i WNET5q0.5h2u6l4
```

## 日志文件

日志文件保存在 `logs/` 目录，命名格式：
- `{项目名}_{任务类型}_{时间戳}.log`
- 例如：`WNET5q0.5h2u6l4_inference_20250711_004148.log`

## 终端输出规则

Wrapper 会智能过滤输出，只在终端显示：
- 前 10 行（初始化信息）
- 错误信息（带 ❌ 标记）
- 警告信息（带 ⚠️ 标记）
- 成功信息（带 ✅ 标记）
- 重要进度信息（epoch、loss 等）
- 完成状态和日志路径

## 日志文件格式

```
[2025-07-11 00:41:48.453] 命令: /home/ubuntu/miniconda3/envs/tf26/bin/python cli.py -i WNET5q0.5h2u6l4
[2025-07-11 00:41:48.453] 工作目录: /mnt/f/Work/met_nonlinear_worktrees/met_nonlinear_logging
[2025-07-11 00:41:48.453] Python路径: /home/ubuntu/miniconda3/envs/tf26/bin/python
================================================================================
[2025-07-11 00:41:48.542] INFO: 详细日志将写入: logs/WNET5q0.5h2u6l4_20250711_004148.log
[2025-07-11 00:41:48.753] 2025-07-11 00:41:48.753439: W tensorflow/stream_executor/platform/default/dso_loader.cc:64] Could not load dynamic library 'libcudart.so.11.0'
...
================================================================================
[2025-07-11 00:41:51.299] 执行完成
[2025-07-11 00:41:51.299] 返回码: 0
[2025-07-11 00:41:51.299] 总耗时: 2.85 秒
```

## 高级功能

### 自定义日志目录

修改 `LoggingSubprocessWrapper` 的初始化参数：
```python
wrapper = LoggingSubprocessWrapper(log_dir='custom_logs')
```

### 添加过滤规则

在 `_should_print_to_console()` 方法中添加自定义关键词：
```python
important_keywords = [
    'epoch', 'Project:', '训练', '完成',
    'your_custom_keyword'  # 添加自定义关键词
]
```

## 故障排除

1. **权限问题**：确保脚本有执行权限
   ```bash
   chmod +x cli_wrapper.py
   chmod +x cli
   ```

2. **编码问题**：日志文件使用 UTF-8 编码，确保终端支持 UTF-8

3. **中断处理**：使用 Ctrl+C 可以优雅地终止子进程