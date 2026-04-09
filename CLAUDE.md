# Agentic Coding Guidelines

## 环境配置

- 训练环境：使用名为 `tf26` 的 Conda 环境 Python，而不是硬编码某台机器的绝对路径。
- 常见路径规律：
	- `C:\Users\<用户名>\.conda\envs\tf26\python.exe`
	- `C:\Users\<用户名>\MiniConda3\envs\tf26\python.exe`
	- `C:\Users\<用户名>\miniconda3\envs\tf26\python.exe`
- 当前主机实例：`C:\Users\liang\.conda\envs\tf26\python.exe`
- CLI训练命令：`<TF26_PYTHON> cli.py -t PROJECT_NAME`

> **定位规律**：先找 `tf26` 这个环境名，再拼接到对应的 Conda 根目录，不要先假设用户名或 Conda 安装目录固定。

> **推荐定位命令**：
> - `conda env list`
> - `where conda`
> - `Get-ChildItem "$env:USERPROFILE\.conda\envs\tf26\python.exe","$env:USERPROFILE\MiniConda3\envs\tf26\python.exe","$env:USERPROFILE\miniconda3\envs\tf26\python.exe" -ErrorAction SilentlyContinue`

> **PROJECT_NAME 路径格式**：主命令（`-t`、`-e`、`-m` 等）传入相对路径，格式为 `projects/项目路径`，如 `projects\01_LR_STUDY\FRIKANh6u6l6_e1k_1` 或 `projects/00_MAE_VS_AFMAE/FRIKANh8u6l6_base`。

> **禁止直接编写配置文件**：创建新项目变体时，禁止直接用 Write 工具编写 config.json，必须先从同类型项目 Copy 已有的 config.json，再用 sed/replace 命令修改所需参数，避免引入幻觉差异。

## 项目概述

**MET Nonlinear** - 电化学非线性矫正项目。当前核心代码统一收敛在 `src/` 下，重点模块包括 `src/core/`、`src/models/`、`src/inference/`、`src/analysis/`、`src/visualization/`、`src/calibration_analyzer/`。

参考索引：
- 项目结构与导入路径：详见 [docs/reference/project_structure.md](docs/reference/project_structure.md)。
- 训练与评估入口：详见 [docs/reference/training.md](docs/reference/training.md)、[docs/reference/evaluation.md](docs/reference/evaluation.md)、[docs/reference/inference.md](docs/reference/inference.md)。
- 测试入口与约定：详见 [docs/reference/testing.md](docs/reference/testing.md)。
- 外部项目与边缘仿真：详见 [docs/reference/ep.md](docs/reference/ep.md)、[docs/reference/edge_device_emulation.md](docs/reference/edge_device_emulation.md)。
- WebUI 可视化服务：详见 [docs/reference/webui.md](docs/reference/webui.md)。

---

## CLAUDE.md 组织原则

- `CLAUDE.md` 只作为项目级顶级索引，用于快速定位命令、入口和文档。
- `CLAUDE.md` 的具体功能区只保留四个顶级标题：`主命令`、`ep 子命令`、`projects/ex_projects`、`测试`，不额外拆出新的命令分类标题。
- 每个命令在 `CLAUDE.md` 中保留一条主索引，命令下面可以挂多个功能子列表。
- 每个子列表只描述一个功能点，并使用一句话概括，不在此处展开实现细节、参数说明或背景分析。
- 每个子列表应独立对应一个 `docs/reference/` 下的参考文档；如果同一命令包含多个功能，则分别链接到各自文档。
- 所有功能的详细说明统一写入 `docs/reference/` 下的独立 Markdown 文档，并在 `CLAUDE.md` 中提供对应链接索引。
- 当某项功能需要补充说明时，优先更新 `docs/reference/` 的详细文档，再回到 `CLAUDE.md` 维护对应子列表的一句话摘要与链接。

---

## CLI 命令 (cli.py)

### 主命令

- `python cli.py -t PROJECT_NAME`
	- 训练执行：训练模型并输出权重、训练日志与训练统计，详见 [docs/reference/training.md](docs/reference/training.md)。
	  - 一次只训练一个项目，避免同时训练多个导致系统资源爆满
	  - 在前台训练，不要后台训练

- `python cli.py -e PROJECT_NAME`
	- 评估流程：评估已训练模型并生成推理结果与误差指标，详见 [docs/reference/evaluation.md](docs/reference/evaluation.md)。
	- 计算量估算：导出单步推理计算量与平台加权耗时，详见 [docs/reference/compute_analysis.md](docs/reference/compute_analysis.md)。
- `python cli.py --metrics PROJECT_NAME`
	- 指标提取：从 `-e` 已生成的评估产物提取表格指标并导出 `metrics.json`，详见 [docs/reference/metrics.md](docs/reference/metrics.md)。
- `python cli.py --metrics --all-projects --missing-only`
	- 批量补齐指标：递归遍历 `projects/` 下所有项目，只为缺失 `metrics.json` 的项目补生成指标文件，详见 [docs/reference/metrics.md](docs/reference/metrics.md)。
- `python cli.py -m PROJECT_NAME`
	- 模型结构导出：导出模型结构、参数和配置信息，详见 [docs/reference/model_info.md](docs/reference/model_info.md)。
	- 计算量估算：同步生成模型的计算量分析结果，详见 [docs/reference/compute_analysis.md](docs/reference/compute_analysis.md)。
- `python cli.py -l PROJECT_NAME`
	- LUT 导出：生成 LUT 形式的模型表示用于快速验证或部署前分析，详见 [docs/reference/lut.md](docs/reference/lut.md)。
- `python cli.py -i PROJECT_NAME --layers 5`
	- 推理执行：运行模型推理并输出结果目录，详见 [docs/reference/inference.md](docs/reference/inference.md)。
	- 分层调试：支持快速推理和按层推理调试，详见 [docs/reference/inference.md](docs/reference/inference.md)。
- `python cli.py -a PROJECT_NAME --bias-method auto`
	- 误差分析：分析 MAE、AFMAE 等误差指标及分布，详见 [docs/reference/error_analysis.md](docs/reference/error_analysis.md)。
	- 偏置方法：支持自动、稳态和频域三种偏置分析方法，详见 [docs/reference/error_analysis.md](docs/reference/error_analysis.md)。
- `python cli.py -c PROJECT_NAME`
	- 数据清理：清理项目 `data` 目录下的训练和推理产物，详见 [docs/reference/clean.md](docs/reference/clean.md)。
- `python cli.py -w PROJECT_NAME`
	- 波形生成：从项目数据集生成 Origin/Target 波形文件，详见 [docs/reference/wave_generation.md](docs/reference/wave_generation.md)。
- `python cli.py --bias-viz PROJECT_NAME`
	- 偏置对比：对比基线与补偿结果的偏置分布和改善统计，详见 [docs/reference/bias_visualization.md](docs/reference/bias_visualization.md)。
- `python cli.py -r PROJECT_NAME --series E96 E24`
	- 电阻导出：导出电阻表及标准化结果，详见 [docs/reference/export_resistance.md](docs/reference/export_resistance.md)。
	- BOM 与校验：可选生成 BOM 并执行一致性校验，详见 [docs/reference/export_resistance.md](docs/reference/export_resistance.md)。
- `python cli.py -s PROJECT_NAME --series E96 E24`
	- 电阻标准化：对已有电阻 CSV 进行标准化并导出新表，详见 [docs/reference/standardize_resistance.md](docs/reference/standardize_resistance.md)。
- `python cli.py --vis PROJECT_NAME`
	- 波形可视化：生成 Origin/Target 数据集的波形可视化图，详见 [docs/reference/waveform_visualization.md](docs/reference/waveform_visualization.md)。
- `python cli.py --loss-plot PROJECT_NAME`
	- 损失曲线：根据训练日志生成 loss/lr 曲线图，详见 [docs/reference/loss_plot.md](docs/reference/loss_plot.md)。

- `python cli.py --vis-freq-response-compare PROJECT[@STATE] [PROJECT[@STATE]]`
	- 频响直连对比：直接基于 `linear_response.json` 生成频率响应对比图，无需进入 ep 工作流，详见 [docs/reference/freq_response_compare.md](docs/reference/freq_response_compare.md)。
	- 布局模式：支持叠加和左右并排两种布局，详见 [docs/reference/freq_response_compare.md](docs/reference/freq_response_compare.md)。

### ep 子命令 (外部项目)

> **注意**：创建外部项目时，**不要手动创建目录**。直接运行 `python cli.py ep "路径"` 命令，配置不存在时会自动创建模板。

- `python cli.py ep "PROJECT/task-type/task-name"`
	- 模板生成：创建或执行外部项目任务，配置不存在时自动生成模板，详见 [docs/reference/ep.md](docs/reference/ep.md)。
	- 配置驱动执行：配置存在时直接验证并执行外部任务，详见 [docs/reference/ep.md](docs/reference/ep.md)。
- `python cli.py ep "PROJECT/wnet5-circuit-validation/layer2"`
	- 电路验证：执行 WNET5 电路验证类外部任务，详见 [docs/reference/ep.md](docs/reference/ep.md)。
- `python cli.py ep "PROJECT/freq-response-compensator/test"`
	- 频响补偿任务：执行频率响应补偿器外部任务，详见 [docs/reference/ep.md](docs/reference/ep.md)。
	- 路径格式：支持外部项目、训练项目和简化格式，详见 [docs/reference/ep.md](docs/reference/ep.md)。

### server 子命令 (WebUI 可视化服务)

- `python cli.py server start`
	- 服务启动：启动 WebUI 可视化服务器，详见 [docs/reference/webui.md](docs/reference/webui.md)。
- `python cli.py server stop`
	- 服务停止：停止 WebUI 可视化服务器，详见 [docs/reference/webui.md](docs/reference/webui.md)。
- `python cli.py server status`
	- 服务状态：查看服务器运行状态和日志路径，详见 [docs/reference/webui.md](docs/reference/webui.md)。
- `python cli.py server logs`
	- 服务日志：查看服务器日志输出，详见 [docs/reference/webui.md](docs/reference/webui.md)。

### projects/ex_projects

- `projects\01_LR_STUDY\` 系列 - `固定 LR vs 余弦衰减`：固定学习率尝试达到或优于余弦衰减效果，最优固定 LR 约 0.0005，还未达到。详见 [docs/reference/lr_tuning_fixed_vs_cosine.md](docs/reference/lr_tuning_fixed_vs_cosine.md)。
- `projects\01_LR_STUDY\CNNKANh8u6l6_e1k_lr14e5_stable` - CNNKAN 替换消融稳定版：在默认旧 batch-size 行为下可跑满 1000 epoch，并保留旧项目复现约束。详见 [docs/reference/cnnkan_ablation.md](docs/reference/cnnkan_ablation.md)。
- `ex_projects/compare/mae_vs_afmae` - MAE vs AFMAE 消融对比：执行 MAE/AFMAE 损失函数消融实验并生成对比报告，详见 [docs/reference/mae_vs_afmae.md](docs/reference/mae_vs_afmae.md)。
- `ex_projects/compare/lr_test_1k_epoch` - LR 消融对比：对比 1k epoch 训练中不同学习率（0.01/0.002/0.001）的训练效果，详见 [docs/reference/lr_test_1k_epoch.md](docs/reference/lr_test_1k_epoch.md)。


### 测试命令

- `python cli.py --test`
	- CLI 测试入口：通过 CLI 入口运行测试集，详见 [docs/reference/testing.md](docs/reference/testing.md)。
- `python cli.py --test --test-path src/logger/tests`
	- 路径筛选：指定测试目录，详见 [docs/reference/testing.md](docs/reference/testing.md)。
- `python cli.py --test --test-workers 4 --test-timeout 300`
	- 并行与超时：配置并行数和超时时间，详见 [docs/reference/testing.md](docs/reference/testing.md)。

- `pytest`
	- 默认测试集：直接运行仓库默认测试集，详见 [docs/reference/testing.md](docs/reference/testing.md)。
- `pytest src/analysis/tests/test_analysis_comprehensive.py::TestAliasSuppression::test_module_import -v`
	- 单测定位：运行单个测试文件或函数，详见 [docs/reference/testing.md](docs/reference/testing.md)。
- `pytest -k "test_module_import"`
	- 关键字筛选：按关键字筛选测试，详见 [docs/reference/testing.md](docs/reference/testing.md)。

- `python cli.py qemu list`
	- QEMU 工程扫描：列出仓库中可直接编译运行的 QEMU 工程目录，详见 [docs/reference/edge_device_emulation.md](docs/reference/edge_device_emulation.md)。
- `python cli.py qemu build src/tests/qemu/stm32f405_hello`
	- QEMU 编译：对指定工程目录自动解析源文件和链接脚本并生成 ELF，详见 [docs/reference/edge_device_emulation.md](docs/reference/edge_device_emulation.md)。
- `python cli.py qemu run src/tests/qemu/stm32f405_hello --timeout 5`
	- QEMU 运行：运行指定工程 ELF，默认超时后自动结束并回显串口输出，详见 [docs/reference/edge_device_emulation.md](docs/reference/edge_device_emulation.md)。
- `python cli.py qemu build-run src/tests/qemu/stm32f405_hello --timeout 5`
	- QEMU 冒烟验证：一条命令完成编译与运行，适合快速验证 `Hello World!`，详见 [docs/reference/edge_device_emulation.md](docs/reference/edge_device_emulation.md)。

- `qemu-system-arm.exe -M olimex-stm32-h405 -kernel src/tests/qemu/stm32f405_hello/hello.elf -nographic`
	- 边缘设备仿真：使用 QEMU 模拟 Cortex-M4，在 PC 上近似评估算法在 STM32F405 等边缘设备上的推理性能，详见 [docs/reference/edge_device_emulation.md](docs/reference/edge_device_emulation.md)。
