# 日志系统快速使用指南

## 立即开始

### 运行程序（推荐方式）

使用 wrapper 运行，确保捕获所有日志：

```bash
# Linux/macOS
./cli -i WNET5q0.5h2u6l4

# Windows  
cli.bat -i WNET5q0.5h2u6l4

# 或直接使用 Python
conda run -n tf26 python cli_wrapper.py -i WNET5q0.5h2u6l4
```

### 查看日志

日志文件保存在 `logs/` 目录：
```bash
# 查看最新日志
ls -lt logs/ | head -5

# 查看特定日志内容
less logs/WNET5q0.5h2u6l4_inference_20250711_004148.log
```

## 功能一览

### 1. 终端输出（简洁）
- ✅ 成功信息（绿色勾）
- ❌ 错误信息（红色叉）
- ⚠️  警告信息（黄色警告）
- 📝 日志路径提示
- 🚀 执行状态

### 2. 文件输出（详细）
- 完整时间戳 `[2025-07-11 00:41:48.453]`
- 所有日志级别（DEBUG, INFO, WARNING, ERROR）
- 第三方库输出（TensorFlow, matplotlib 等）
- 完整堆栈跟踪

## 常用命令

```bash
# 训练
./cli WNET5q0.5h2u6l4

# 推理
./cli -i WNET5q0.5h2u6l4

# 评估
./cli -e WNET5q0.5h2u6l4

# 生成波形
./cli -w WNET5q0.5h2u6l4

# 批量处理
./cli -e -all
```

## 开发者工具

### 查找 print 语句
```bash
python -m logger.print_checker . --recursive
```

### 替换 print 为 logger
```bash
python -m logger.print_replacer myfile.py
```

### 运行测试
```bash
pytest logger/tests/ -v
```

## 注意事项

1. **首次运行**会创建 `logs/` 目录
2. **日志文件**按时间戳命名，不会覆盖
3. **Ctrl+C** 可以安全中断执行
4. **错误时**会显示日志文件路径供调试

## 示例输出

```
📝 详细日志将写入: logs/WNET5q0.5h2u6l4_inference_20250711_004148.log
🚀 开始执行: python cli.py -i WNET5q0.5h2u6l4
------------------------------------------------------------
   INFO: Project path: projects/WNET5q0.5h2u6l4
   INFO: 🔍 推理数据生成项目: WNET5q0.5h2u6l4
   ...
------------------------------------------------------------
✅ 任务成功完成 (耗时: 2.85秒)
📄 完整日志已保存到: logs/WNET5q0.5h2u6l4_inference_20250711_004148.log
```