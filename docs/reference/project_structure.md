# 项目结构与导入路径

## 功能概述

本仓库的 Python 代码以 `src/` 为唯一主代码根目录；仓库根目录只保留入口脚本、配置、文档、日志和数据目录。长期稳定的目标是：

- `python cli.py ...` 与 `pytest` 都从仓库根目录启动。
- 业务模块统一用包名导入 `core`、`models`、`inference`、`analysis`、`calibration_analyzer` 等。
- project 级训练/评估/推理产物统一收敛到各自项目的 `data/` 目录，而不是散落到仓库根目录。
- 结构化运行日志与手工留存的 stdout/stderr 统一收敛到仓库根目录的 `logs/`，不要把临时 `*.log` 直接落在根目录。

## 目录约定

### 代码与入口

| 路径 | 角色 |
|------|------|
| `cli.py` | 仓库级 CLI 入口，只负责启动、轻量分发和 `src/` 注入 |
| `src/` | 唯一主代码目录 |
| `src/core/` | 训练、评估、CLI 调度、EP/QEMU 子命令等核心逻辑 |
| `src/models/` | 模型定义 |
| `src/inference/` | 推理后端、逐层输出、误差分析与推理可视化 |
| `src/analysis/` | 评估与分析逻辑 |
| `src/visualization/` | 论文图、频响图等可视化逻辑 |
| `src/calibration_analyzer/` | 波形、系统分析与相关桥接结构 |
| `src/tests/` | 主测试目录 |

### 根目录保留内容

根目录原则上不再承载业务 Python 包，只保留以下类型内容：

- `cli.py` 这类仓库级入口。
- `pytest.ini`、`requirements.txt` 等配置文件。
- `docs/`、`projects/`、`ex_projects/`、`data/`、`logs/` 等文档、数据与日志目录。
- 通过 `Tee-Object` / `tee` 额外留存的命令输出，也应默认写到 `logs/` 子目录，而不是在根目录平铺 `train.log`、`pytest.log` 之类的临时文件。

### `board_inference` 子包边界

`src/core/board_inference/` 是当前 `qemu-c-inference` 与 `ep keil-bench` 的稳定生产实现。长期上不应再把已删除的 `src/core/lstm_qemu_ep_task.py` 当作运行时依赖。

当前分工如下：

| 路径 | 角色 |
|------|------|
| `src/core/board_inference/entrypoints.py` | 对外暴露稳定入口，供 `external_cli_handler` / CLI 主流程调用 |
| `src/core/board_inference/registry.py` | 根据 project `config.json` 与权重命名识别模型类型，判断是否已有 native 实现 |
| `src/core/board_inference/models/sequence.py` | `lstm`、`rnn`、`grn`、`lstm_transformer`、`onedcnn`、`tcn`、`wavenet2`、`wavenet3` 的原生实现 |
| `src/core/board_inference/models/frikan.py` | `frikan` 的原生实现 |
| `src/core/board_inference/platforms/benchmark_common.py` | QEMU / Keil 共享的工程生成、构建、串口抓取、summary 写回与比较辅助逻辑 |
| `src/core/board_inference/templates/` | 稳定 C/H 模板目录；固定 scaffold 应放这里，而不是继续塞在 Python 长字符串里 |

长期维护规则：

- `entrypoints.py` 只做请求封装、模型分流和异常边界，不再混入大段模型生成逻辑。
- 模型专属数值导出、结构校验和 `main.c` / `model_data.h` 渲染留在 `models/*.py`。
- 平台共享逻辑优先收敛到 `platforms/benchmark_common.py`，避免在每个模型里复制 Keil/QEMU/串口处理代码。
- 固定模板文本优先放 `templates/`，Python 只保留数值 initializer、拓扑相关声明拼装和少量条件分支。
- 新增 `qemu-c-inference` 模型时，优先扩展 `registry.py` 与对应 `models/*.py`，不要重新引入“单个超长脚本同时承担全部模型和全部平台”的结构。

## project 路径与产物布局

当前 CLI 会把传入的 project 名归一化成仓库相对路径；规范写法是 `projects/...`，Windows 下传入反斜杠也会先归一化为 `/`。

典型 project 目录结构如下：

```text
projects/<PROJECT_NAME>/
├── config.json
└── data/
    ├── best.weights.h5
    ├── best_val.weights.h5
    ├── best.weights.json             # 可选，供离线导出 / board inference 读取
    ├── best_val.weights.json         # 可选，供离线导出 / board inference 读取
    ├── fast_best.weights.h5            # 可选，仅 use_fast_model 时出现
    ├── fast_best_val.weights.h5        # 可选，仅 use_fast_model 时出现
    ├── training_log.jsonl
    ├── training_info.json
    ├── training_state.json
    ├── model_info.json
    ├── linear_response.json            # 评估后生成
    └── scalers/
        ├── combined_scaler.json
        ├── scaler_x.json               # 历史兼容文件，可存在
        └── scaler_y.json               # 历史兼容文件，可存在
```

长期规则：

- `config.json` 位于 project 根目录，长期产物位于同级的 `data/` 目录。
- 权重的主文件名约定为 `best.weights.h5` / `best_val.weights.h5`。
- 对应的 `best.weights.json` / `best_val.weights.json` 若存在，也应视为 canonical 导出产物。
- fast-model 相关权重若存在，命名为 `fast_best.weights.h5` / `fast_best_val.weights.h5`。
- scaler 主文件长期以 `data/scalers/combined_scaler.json` 为准；`scaler_x.json`、`scaler_y.json` 仅作为历史兼容产物看待。
- 推理、评估、模型信息导出都应继续落到该 project 的 `data/` 子树中，不要新开根目录旁路输出。
- 离线分析、QEMU/Keil benchmark、`load_weights()` 一类非训练读路径应把这些 canonical 权重文件当只读输入；若存在命名兼容问题，应修解析逻辑或走显式导出流程，不要在读路径里重命名、重写或覆盖现有权重文件。

## `config.json` 的长期分工

project 根目录的 `config.json` 是“项目定义”，`data/` 是“运行产物”；不要把两者混写。

当前长期分工如下：

- `dataset`：数据集定义、频率范围、反转开关等训练 / 数据侧约束
- `inference_config`：模拟 / 推理实现约束，例如 `power_supply`、`opamp_config`、`high_pass_config`、`bias_compensation`
- `bom_config`：当前也收在 `inference_config` 下，和电阻 / BOM 导出链路一起维护
- `training_info.json`、`model_info.json`、`linear_response.json`、`metrics.json` 等：都属于运行后生成的派生产物，不应反向当作配置源

因此，如果新增的是 project 级模拟实现选项，应优先落在 `inference_config`，而不是再引入新的顶层零散键名。

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

如果离开仓库根目录单独执行脚本或测试，需要自行保证 `src/` 在 `PYTHONPATH` 中；否则 project 相对路径和包导入都可能失效。

## 模块边界与循环导入约束

历史过程文档里曾记录过 `cli.py` 与 `inference.processing.model_loader` 的循环依赖问题；当前长期边界已经收敛为：

1. `cli.py` 只做启动和任务分发，不再承载 `ProjectManager` 的权威实现。
2. 当前 project 上下文实现位于 `src/core/project_manager.py`。
3. `src/inference/processing/model_loader.py` 通过依赖注入接收 `project_manager`，不应再反向导入 `cli.py`。
4. 可复用业务模块应依赖 `core.project_manager`、`core.model_engine` 等稳定模块，而不是把 CLI 入口文件当库接口使用。

推荐的依赖方向是：

```text
cli.py -> core.* -> inference.* / models.* / analysis.*
```

应避免重新引入这种反向依赖：

```text
inference.* -> cli.py
```

测试和一次性脚本如果只是做进程级 smoke test，可以 `import cli`；但新的可复用模块不应以此为常规依赖。

## calibration_analyzer 约定

### 唯一保留路径

`calibration_analyzer` 的真实保留实现为 `src/calibration_analyzer/`。

仓库根目录曾存在一个历史遗留副本（以 gitlink 形式保留）；当前长期口径是只把 `src/calibration_analyzer/` 当运行时与开发时的主包。

### 当前使用方式

- 业务代码统一通过 `from calibration_analyzer ...` 导入。
- `cli.py` 和 `conftest.py` 分别保证 CLI 与 pytest 场景都能解析到 `src/calibration_analyzer/`。
- 新增模块、测试或文档时，不应再引用根目录历史路径。

## 维护规则

1. 新 Python 包默认放入 `src/` 下对应子目录。
2. 新入口脚本若必须放在根目录，应显式处理 `src/` 路径注入，或复用现有 CLI 入口。
3. 文档中提到模块位置时，应优先写 `src/...` 的真实路径，避免沿用迁移前表述。
4. 如果遇到“文件缺失”类问题，先确认是否从仓库根目录运行、project 是否已训练，再怀疑路径逻辑。
5. 新增推理/评估模块时，优先复用 `core.project_manager` 提供的上下文，不要重新把 project 生命周期塞回 `cli.py`。

## 快速验证

```bash
python -c "import cli; import calibration_analyzer.exam_class as m; print(m.__file__)"
pytest src/tests/calibration_analyzer/test_exam_class.py -q
```

第一条命令应输出 `src/calibration_analyzer/...` 下的文件路径，第二条用于验证 `calibration_analyzer` 相关基础测试仍可运行。

## 相关文档

- [training.md](training.md)
- [evaluation.md](evaluation.md)
- [inference.md](inference.md)
- [testing.md](testing.md)
- [historical_process_docs.md](historical_process_docs.md)
