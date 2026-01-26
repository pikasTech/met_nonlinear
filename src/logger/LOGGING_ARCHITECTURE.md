# 日志系统架构说明

## 统一日志架构

本项目实现了一个统一的日志系统，通过 subprocess wrapper 确保不会丢失任何日志信息：

### 1. Print 替换层（print_replacer.py）
- **作用**：自动将 print() 转换为 logger 调用
- **特点**：
  - 基于 AST 的代码转换
  - 智能日志级别检测
  - 处理 f-string 语法限制
  - 已替换 228 个 print 语句

### 2. 进程包装层（cli_wrapper.py）
- **作用**：捕获所有 stdout/stderr 输出
- **特点**：
  - 使用 subprocess 运行原始程序
  - 捕获第三方库输出（如 TensorFlow 警告）
  - 捕获未转换的 print 语句
  - 捕获系统错误和堆栈跟踪
  - 实时显示 + 完整记录

## 日志文件结构

```
logs/
└── WNET5q0.5h2u6l4_inference_20250711_004148.log # 唯一的完整日志（wrapper）
```

## 使用流程

### 开发阶段
1. 使用 `print_checker.py` 查找 print 语句
2. 使用 `print_replacer.py` 替换为 logger
3. 处理 f-string 语法问题

### 运行阶段
1. 使用 `cli_wrapper.py` 运行程序：
   ```bash
   python cli_wrapper.py -i PROJECT_NAME
   ```

2. 或使用便捷脚本：
   ```bash
   ./cli -i PROJECT_NAME        # Linux/macOS
   cli.bat -i PROJECT_NAME      # Windows
   ```

## 日志输出示例

### 终端输出（简洁版）
```
📝 详细日志将写入: logs/WNET5q0.5h2u6l4_inference_20250711_004148.log
🚀 开始执行: python cli.py -i WNET5q0.5h2u6l4
------------------------------------------------------------
   INFO: 详细日志将写入: logs/WNET5q0.5h2u6l4_20250711_004148.log
   INFO: Project path: projects/WNET5q0.5h2u6l4
   INFO: 🔍 推理数据生成项目: WNET5q0.5h2u6l4
❌ ❌ 推理失败
------------------------------------------------------------
✅ 任务成功完成 (耗时: 2.85秒)
📄 完整日志已保存到: logs/WNET5q0.5h2u6l4_inference_20250711_004148.log
```

### 文件输出（详细版）
```
[2025-07-11 00:41:48.453] 命令: python cli.py -i WNET5q0.5h2u6l4
[2025-07-11 00:41:48.453] 工作目录: /path/to/project
[2025-07-11 00:41:48.542] INFO: 详细日志将写入: logs/WNET5q0.5h2u6l4_20250711_004148.log
[2025-07-11 00:41:48.753] WARNING: tensorflow/.../dso_loader.cc:64] Could not load...
[2025-07-11 00:41:50.903] DEBUG: matplotlib data path: /home/ubuntu/...
[2025-07-11 00:41:50.921] ERROR: 未找到推理输入文件: dataset_MET_output_original.wave
```

## 优势

1. **不丢失日志**：wrapper 捕获所有输出
2. **单一日志文件**：避免多个日志文件的混乱
3. **结构化日志**：内部使用标准 logging 模块
4. **智能过滤**：终端只显示重要信息
5. **错误追踪**：完整的堆栈跟踪信息
6. **性能优化**：实时处理，低开销

## 故障排除

### 常见问题

1. **F-string 语法错误**
   ```python
   # 错误
   logger.info(f'{dict['key']}')
   # 正确
   logger.info(f"{dict['key']}")
   ```

2. **缺少 logging 导入**
   ```python
   import logging  # 必须在文件开头
   logger = logging.getLogger(__name__)
   ```

3. **日志文件过大**
   - 定期清理 logs/ 目录
   - 可设置日志轮转（future enhancement）

## 未来改进

1. 日志文件轮转和压缩
2. 日志级别动态配置
3. 分布式日志收集
4. 日志分析和可视化工具