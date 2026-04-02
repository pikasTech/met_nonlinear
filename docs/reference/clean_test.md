# 清理和测试功能说明

## 清理项目数据

### 基本用法

```bash
# 清理指定项目
python cli.py -c PROJECT_NAME

# 清理所有项目（需确认）
python cli.py -c "*"
```

### 清理内容

清理 `projects/PROJECT_NAME/data/` 目录：

- 训练 checkpoint 文件
- 推理结果
- 临时文件
- 日志文件

### 注意事项

- 清理后模型权重和训练日志无法恢复
- 项目配置文件 `config.json` 不会被删除

---

## 运行单元测试

### 基本用法

```bash
# 运行所有测试
python cli.py --test

# 指定测试路径
python cli.py --test --test-path src/analysis/tests

# 并行测试
python cli.py --test --test-workers 4

# 单测试超时设置
python cli.py --test --test-timeout 60
```

### pytest 直接使用

```bash
# 运行所有测试
pytest

# 运行单个测试文件
pytest src/analysis/tests/test_analysis_comprehensive.py

# 运行单个测试函数
pytest src/analysis/tests/test_analysis_comprehensive.py::TestAliasSuppression::test_module_import

# 关键字匹配
pytest -k "test_module_import"

# 跳过慢速测试
pytest -m "not slow"
```

### 测试标记

| 标记 | 说明 |
|------|------|
| `slow` | 慢速测试 |
| `skip_on_ci` | CI 环境跳过 |
| `requires_gpu` | 需要 GPU |
| `integration` | 集成测试 |

### 测试覆盖范围

- 单元测试 (`src/*/tests/test_*.py`)
- 集成测试
- 后端测试
- 分析模块测试

## 相关配置

测试配置位于 `pytest.ini`：

```ini
[pytest]
testpaths = src/tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
```

## 相关文档

- [分析模块测试](../src/analysis/tests/)
- [推理后端测试](../src/inference/tests/)
