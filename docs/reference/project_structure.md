# 项目结构与导入路径

## 功能概述

本仓库的 Python 代码以 `src/` 为唯一主代码根目录，仓库根目录仅保留入口脚本、配置和文档。该结构用于同时兼容：

- `python cli.py ...` 形式的统一 CLI 入口。
- `pytest` 直接从仓库根目录运行测试。
- 以包名方式导入 `core`、`models`、`inference`、`calibration_analyzer` 等模块。

## 目录约定

### 代码与入口

| 路径 | 角色 |
|------|------|
| `cli.py` | 仓库级 CLI 入口，负责将 `src/` 注入 `sys.path` |
| `src/` | 唯一主代码目录 |
| `src/core/` | 训练、评估、CLI 调度核心逻辑 |
| `src/models/` | 模型定义 |
| `src/inference/` | 推理后端与数据处理 |
| `src/analysis/` | 评估与分析逻辑 |
| `src/visualization/` | 可视化逻辑 |
| `src/calibration_analyzer/` | 波形解析、校准数据结构与 GUI/分析相关模块 |
| `src/tests/` | 主测试目录 |

### 根目录保留内容

根目录原则上不再承载业务 Python 包，只保留以下类型内容：

- `cli.py` 这类仓库级入口。
- `pytest.ini`、`requirements.txt` 等配置文件。
- `docs/`、`projects/`、`ex_projects/`、`data/` 等文档与数据目录。

## 导入路径解析机制

### CLI 场景

`cli.py` 启动后会优先把 `src/` 插入 `sys.path`，因此运行时应直接使用包名导入，而不是写成带 `src.` 前缀的导入路径。

典型示例：

```python
from calibration_analyzer.exam_class import System, TimeSeries
from core.cli_parser import TaskType
from inference.data_processing import load_wave_data
```

### pytest 场景

仓库根目录的 `conftest.py` 也会在测试启动时将 `src/` 插入 `sys.path`。因此测试文件与业务代码保持同一套导入约定：

- 正确：`from calibration_analyzer.exam_class import System`
- 正确：`from analysis.metrics import compute_mae`
- 不推荐：`from src.calibration_analyzer.exam_class import System`

如果离开仓库根目录单独执行脚本或测试，需要自行保证 `src/` 在 `PYTHONPATH` 中。

## calibration_analyzer 约定

### 唯一保留路径

`calibration_analyzer` 的真实保留实现为 `src/calibration_analyzer/`。

仓库根目录曾存在一个历史遗留的 `calibration_analyzer` 副本（以 gitlink 形式保留），该副本已清理，不再作为运行时或开发时的主包。

### 当前使用方式

- 业务代码统一通过 `from calibration_analyzer ...` 导入。
- `cli.py` 和 `conftest.py` 分别保证 CLI 与 pytest 场景都能解析到 `src/calibration_analyzer/`。
- 新增模块、测试或文档时，不应再引用根目录 `calibration_analyzer/`。

## 维护规则

1. 新 Python 包默认放入 `src/` 下对应子目录。
2. 新入口脚本若必须放在根目录，应显式处理 `src/` 路径注入，或复用现有 CLI 入口。
3. 文档中提到模块位置时，应优先写 `src/...` 的真实路径，避免沿用迁移前表述。
4. 遇到导入冲突或循环导入问题时，先检查是否误用了历史路径或在仓库根目录外执行脚本。

## 快速验证

```bash
python -c "import cli; import calibration_analyzer.exam_class as m; print(m.__file__)"
pytest src/tests/calibration_analyzer/test_exam_class.py -q
```

第一条命令应输出 `src/calibration_analyzer/...` 下的文件路径，第二条用于验证 `calibration_analyzer` 相关基础测试仍可运行。

## 相关文档

- [testing.md](testing.md)
- [training.md](training.md)
- [evaluation.md](evaluation.md)
- [inference.md](inference.md)
