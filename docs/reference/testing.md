# 测试功能说明

## 功能概述

仓库支持两类测试入口：

- `python cli.py --test`：通过项目 CLI 统一转发到 pytest。
- `pytest`：直接使用 pytest 运行测试。

当前长期约定是：测试应优先保证入口统一、路径一致、超时可控，再逐步补覆盖率；不要把历史过程文档里的阶段性覆盖率目标误写成仓库现状。

## 推荐环境

测试环境统一使用 `tf26`，在 Windows 上优先通过 `conda.bat run --no-capture-output -n tf26` 启动。

```bash
conda.bat run --no-capture-output -n tf26 python cli.py --test
conda.bat run --no-capture-output -n tf26 python -m pytest src/tests -q
conda.bat run --no-capture-output -n tf26 python -m pytest src/tests -q 2>&1 | Tee-Object -FilePath logs/pytest.stdout.log
```

其中 `--no-capture-output` 的长期价值不是“更热闹”，而是避免 Windows 控制台编码与缓冲行为把错误输出吞掉。

如果需要留存测试输出，优先使用 `Tee-Object`（PowerShell）或 `tee`（bash），不要只做 `> pytest.log` 这类完全重定向；否则最容易把“当前会话里的实时错误线索”一并藏掉。

额外留存的 stdout/stderr 默认写到仓库根目录的 `logs/` 子目录，不要把 `pytest.stdout.log` 一类文件直接落在仓库根目录。

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

长期上，`cli.py --test` 应视为仓库级标准入口；只有在需要更细粒度筛选时，才直接调用 `pytest`。

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
pytest src/tests/models/test_models.py -k "predict_accepts_verbose_kwarg" -v
```

其中 `predict_accepts_verbose_kwarg` 这类定向用例适合在修改模型包装类 `predict()` 签名、评估链兼容性或 legacy 项目评估行为后做快速回归。

## WNET5 / SPICE 定向回归

如果本轮修改涉及 WNET5 分层验证、`wnet5_circuit_validator.py`、WaveNet5 SPICE 导出或相关可视化模块，建议优先跑下面几类定向回归：

```bash
pytest src/tests/visualization/test_visualization_modules.py -k "Wnet5CircuitValidator" -v
pytest src/tests/test_wavenet5_spice.py -v
pytest src/tests/test_wavenet5_spice_integration.py -v
```

三者的分工应这样理解：

- `test_visualization_modules.py -k "Wnet5CircuitValidator"`：优先检查 `wnet5_circuit_validator` 模块是否还能被导入，适合改动可视化与验证器入口后做快速冒烟。
- `test_wavenet5_spice.py`：优先检查 WaveNet5 到 SPICE 的导出接口、后端接入和基础对象关系是否被改坏。
- `test_wavenet5_spice_integration.py`：保留一层更接近集成链路的基础对象验证，但其中依赖真实项目文件的场景当前仍是 skip，不应误解为已经覆盖了完整项目级电路验证。

这些自动化回归只能覆盖“代码接口还活着”这一层；WNET5 的通道映射、E96 量化图、SVF 拟合和频响对照仍应按 [wnet5_circuit_validation.md](wnet5_circuit_validation.md) 做人工验收。

### 修改导出契约时的最小验收

如果本轮修改触及下面这些边界之一：

- `src/inference/wavenet5_spice_backend.py`
- `src/models/model_layers.py` 里的 `to_spice()` 契约
- `src/inference/processing/backend_manager.py`
- `src/inference/backends/spice/backend.py` 或相关 SPICE 导出入口

则最少应补做下面几项确认：

- WNET5 的第一层仍然按 `IIR / SVF` 导出，而不是把线性前端跳过
- Dense 层消费的仍是前端展开后的多通道输出，维度契约没有退化回“单输入直接进 Dense”
- project 级 SPICE 网表仍写回 `projects/<PROJECT>/data/spice_netlists/`，没有重新漂回仓库级临时目录

过程文档里曾使用“与某个历史 baseline commit 对比”来定位推理回归；这可以继续作为排障手段，但不应被写成当前仓库的日常必经流程。当前长期口径仍是：自动化测试守接口契约，项目级分层签收按 [wnet5_circuit_validation.md](wnet5_circuit_validation.md) 执行。

## 配置位置

测试的全局配置位于仓库根目录的 `pytest.ini`。

## 适用场景

- 需要走统一项目入口时使用 `python cli.py --test`。
- 需要更灵活地筛选测试时直接使用 `pytest`。

## 开发时的长期约束

### 并行与超时优先保留

当前测试体系默认按“可并行、可超时中断”的方向维护。

长期规则是：

- 新增测试时，优先保持其可在并行 pytest worker 下稳定运行。
- 不要把本可用纯单元测试验证的问题，扩成依赖长时间训练或外部进程的集成测试。
- 若某类测试需要更长时间，应通过路径筛选或 marker 单独执行，而不是拖慢默认入口。

### 卡死判定要和现有机制分开理解

过程文档里曾提出“1 分钟无 console log 视为卡死”的工程要求，但当前仓库长期能依赖的硬约束，仍是 `pytest-timeout` 一类的总超时机制。

因此长期文档里应这样理解：

- 默认超时与并行参数由 CLI / pytest 配置负责。
- “长时间无输出”更适合作为执行任务时的人为排障信号，而不是假定仓库已经内建了输出静默 watchdog。
- 若某条测试经常表现为长时间静默，应优先缩小测试范围、补日志或拆分场景，而不是简单放宽总超时。

### 覆盖率结论必须基于当前报告

测试覆盖率在本仓库是持续建设项。长期规则是：

- 只有在当前 coverage 报告可复现时，才对外声称某个模块或全仓达到特定覆盖率。
- 过程文档中的阶段性数字只代表当时那轮补测结果，不能直接当作长期事实引用。
- 做覆盖率补齐时，优先补 `src/` 主链路模块和导入/缩放/评估兼容性相关测试。

### 成功判定不要停留在“没报错”

对于配置验证、EP 调度、WNET5 验证器和报告生成链路，长期上不应把“命令退出码为 0”直接当成测试通过。

更稳妥的判定方式是：

- 同时检查预期产物是否真的生成，例如报告、JSON、PNG 或波形文件。
- 对配置 / schema 变更，检查关键字段是否真的写入结果，而不是仅仅命令没抛异常。
- 如果代码 silently fallback 到旧逻辑、跳过实验对比或只打印 warning 而缺少核心产物，应视为“礼貌失败”，继续补定位，而不是当作成功签收。

## 相关文档

- [pytest.ini](../../pytest.ini)
- [项目结构与导入路径](project_structure.md)
- [wnet5_circuit_validation.md](wnet5_circuit_validation.md)
