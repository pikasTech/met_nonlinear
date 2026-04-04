# 测试功能说明

## 功能概述

仓库支持两类测试入口：

- `python cli.py --test`：通过项目 CLI 统一转发到 pytest。
- `pytest`：直接使用 pytest 运行测试。

## CLI 测试入口

### 基本用法

```bash
python cli.py --test
```

### 指定测试路径

```bash
python cli.py --test --test-path src/analysis/tests
```

### 并行与超时

```bash
python cli.py --test --test-workers 4 --test-timeout 300
python cli.py --test --no-parallel
```

CLI 会构造并执行：

```bash
python -m pytest TEST_PATH --timeout SECONDS --workers N
```

默认测试路径为 `src/tests`，默认超时 300 秒，默认并行 worker 为 4。

## 导入路径约定

测试应从仓库根目录启动。根目录 `conftest.py` 会在 pytest 启动时自动将 `src/` 插入 `sys.path`，因此测试代码应直接使用包名导入：

- `from calibration_analyzer.exam_class import System`
- `from analysis.metrics import compute_mae`

不建议写成 `from src.xxx import ...`。当前仓库的真实主代码目录是 `src/`，其中 `calibration_analyzer` 的唯一保留实现为 `src/calibration_analyzer/`。

## 直接使用 pytest

```bash
pytest
pytest src/analysis/tests/test_analysis_comprehensive.py -v
pytest src/analysis/tests/test_analysis_comprehensive.py::TestAliasSuppression::test_module_import -v
pytest -k "test_module_import"
pytest -m "not slow"
```

## 配置位置

测试的全局配置位于仓库根目录的 `pytest.ini`。

## 适用场景

- 需要走统一项目入口时使用 `python cli.py --test`。
- 需要更灵活地筛选测试时直接使用 `pytest`。

## 相关文档

- [pytest.ini](../../pytest.ini)
- [项目结构与导入路径](project_structure.md)
