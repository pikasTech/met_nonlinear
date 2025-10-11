# Python 日志系统实现

这是一个基于 Python 标准库的模块化日志系统，用于替代项目中的 print 语句。

## 功能特性

- 🔍 **Print 检查器**: 扫描代码中的所有 print() 语句
- 🔄 **自动替换**: 将 print 语句智能转换为适当级别的日志调用
- 📝 **分级日志**: 支持 DEBUG, INFO, WARNING, ERROR, CRITICAL 级别
- 🎯 **模块化设计**: 支持分层的模块化日志管理
- ⚙️ **灵活配置**: 支持 YAML/JSON 配置文件
- 🎨 **彩色输出**: 在终端中显示带颜色的日志（可选）

## 快速开始

### 1. 检查 print 使用情况

```bash
# 扫描目录
python print_checker.py /path/to/project

# 扫描单个文件
python print_checker.py script.py

# 输出 JSON 格式
python print_checker.py /path/to/project --json

# 排除特定目录
python print_checker.py /path/to/project --exclude tests build
```

### 2. 替换 print 语句

```python
from print_replacer import replace_prints_in_file

# 替换文件中的 print
result = replace_prints_in_file('original.py')
if result['success']:
    print(f"成功替换 {result['count']} 个 print 语句")
```

### 3. 使用日志系统

```python
from logging_setup import setup_logging, get_module_logger

# 初始化日志系统
setup_logging()

# 获取模块 logger
logger = get_module_logger('core.training')

# 记录日志
logger.info("开始训练")
logger.debug("详细信息")
logger.warning("警告信息")
logger.error("错误信息")
```

## 目录结构

```
logger/
├── print_checker.py      # Print 语句扫描器
├── print_replacer.py     # Print 自动替换器
├── logging_setup.py      # 日志系统配置
├── logging_config.yaml   # 示例配置文件
├── demo.py              # 使用演示
└── tests/               # 测试文件
    ├── test_print_checker.py
    ├── test_print_replacer.py
    ├── test_logging_setup.py
    └── test_integration.py
```

## Print 替换规则

替换器会根据 print 内容智能选择日志级别：

- 包含 "critical", "fatal", "严重" → `logger.critical()`
- 包含 "error", "fail", "错误", "失败" → `logger.error()`
- 包含 "warn", "warning", "警告" → `logger.warning()`
- 包含 "debug", "调试" → `logger.debug()`
- 其他情况 → `logger.info()`

特殊处理：
- `print(..., file=sys.stderr)` → `logger.error()`
- 多参数 print → 格式化字符串
- 空 print() → `logger.info("")`

## 配置文件示例

```yaml
version: 1
disable_existing_loggers: false

formatters:
  console_simple:
    format: '%(levelname)s: %(message)s'
  file_detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: console_simple
    
  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: file_detailed
    filename: logs/app.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

loggers:
  myapp:
    level: DEBUG
    handlers: [console, file]
```

## 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行特定测试
python -m pytest tests/test_print_checker.py -v

# 查看测试覆盖率
python -m pytest --cov=. --cov-report=html
```

## 使用建议

1. **渐进式迁移**: 先使用 print_checker 了解现状，再逐步替换
2. **备份原文件**: replace_prints_in_file 默认会创建 .bak 备份
3. **检查替换结果**: 替换后务必检查代码是否正常运行
4. **配置优先**: 使用配置文件管理日志行为，避免硬编码

## 注意事项

- 需要 Python 3.6+
- 替换后的代码会自动添加 `logging.basicConfig()` 以确保日志输出
- 建议在版本控制中提交前仔细检查替换结果
- 复杂的 print 语句可能需要手动调整

## 许可证

MIT License