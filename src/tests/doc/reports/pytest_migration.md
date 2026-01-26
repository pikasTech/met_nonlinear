# test_framework 到 pytest 迁移记录

## 概述

本文档记录了将项目测试框架从 test_framework 迁移到标准 pytest 的过程。

## 迁移背景

- **原框架**: test_framework (git子模块)
- **新框架**: pytest (标准Python测试框架)
- **迁移日期**: 2025-07-11
- **迁移原因**: 使用标准化的测试框架，减少外部依赖，提高维护性

## 主要变更

### 1. 移除 run_tests.py

完全移除了 run_tests.py 文件，直接使用 pytest 命令行工具：

```bash
# 旧方式
python run_tests.py

# 新方式
pytest
```

### 2. pytest.ini 配置

创建了完整的 pytest 配置文件，包括：
- 测试目录配置
- 测试发现规则
- 标记定义（slow, skip_on_ci, requires_gpu, integration）
- 覆盖率配置
- 超时设置

### 3. 测试执行方式

#### 运行所有测试
```bash
# 直接使用pytest
pytest

# 在正确的Python环境中运行
conda run -n tf26 pytest
```

#### 运行特定测试
```bash
# 指定目录
pytest tests/

# 使用关键字
pytest -k test_kan

# 详细输出
pytest -v

# 运行特定测试类或方法
pytest tests/test_cli.py::TestProjectManager
```

#### 覆盖率报告
```bash
# 终端报告
pytest --cov=. --cov-report=term-missing

# HTML报告
pytest --cov=. --cov-report=html

# 在正确环境中生成覆盖率
conda run -n tf26 pytest --cov=. --cov-report=html
```

## 兼容性说明

1. **unittest 兼容**: pytest 完全兼容 unittest 测试，无需修改现有测试代码
2. **测试发现**: pytest 自动发现所有符合规则的测试文件
3. **环境要求**: 项目需要 Python 3.9 + TensorFlow 2.6 环境

## 后续工作

1. 移除 test_framework git 子模块
2. 更新 CI/CD 配置（如有）
3. 团队培训 pytest 使用方法

## 参考资料

- [pytest 官方文档](https://docs.pytest.org/)
- [pytest-cov 文档](https://pytest-cov.readthedocs.io/)
- 原 test_framework 集成文档：build_test.md, build_test2.md