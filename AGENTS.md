# 传感器非线性神经网络学习框架

## 论文撰写

- 构建后的主 Papaer [[main.pdf]] [main.tex](docs\paper\latex\main.tex)
	- 过程文档 [20260327-转投](docs\MDTODO\20260327-转投.md)
- [[文献笔记]] - 用户自己写的文献阅读笔记，不要修改
- 论文 LaTeX 与 MN 投稿稿整理：详见 [docs/reference/paper_latex_submission.md](docs/reference/paper_latex_submission.md)，其中包含 MN AI+sensor 标杆论文（Nano Lett. ML+MEMS 元结构）作为成稿参考。
- 论文核心故事线与引言重构：详见 [docs/reference/paper_storyline_refinement.md](docs/reference/paper_storyline_refinement.md)。
- 论文方法中间稿撰写规范：详见 [docs/reference/paper_method_draft_writing.md](docs/reference/paper_method_draft_writing.md)。
- 论文消融实验方法：详见 [docs/reference/paper_ablation_method.md](docs/reference/paper_ablation_method.md)。
- 论文超参数敏感性分析方法：详见 [docs/reference/paper_hyperparameter_sensitivity_method.md](docs/reference/paper_hyperparameter_sensitivity_method.md)。
- 论文横向对比实验方法：详见 [docs/reference/paper_horizontal_comparison_method.md](docs/reference/paper_horizontal_comparison_method.md)。
- 论文边缘设备推理评估方法：详见 [docs/reference/paper_edge_inference_evaluation_method.md](docs/reference/paper_edge_inference_evaluation_method.md)。
- 论文指标计算方法：详见 [docs/reference/paper_metric_calculation_method.md](docs/reference/paper_metric_calculation_method.md)。
- 论文计算量标定方法：详见 [docs/reference/paper_compute_cost_calibration_method.md](docs/reference/paper_compute_cost_calibration_method.md)。
- 论文 LUT 插值部署评估方法：详见 [docs/reference/paper_lut_interpolation_evaluation_method.md](docs/reference/paper_lut_interpolation_evaluation_method.md)。
- 论文 AI 原理示意图绘制规范：详见 [docs/reference/paper_ai_schematic_figures.md](docs/reference/paper_ai_schematic_figures.md)。
- Paper figure traceability and modification workflow: see [docs/reference/paper_figure_traceability.md](docs/reference/paper_figure_traceability.md).
- Paper figure fine-grained adjusters: see [docs/reference/paper_figure_studio_adjusters.md](docs/reference/paper_figure_studio_adjusters.md).
- 文献索引 [[docs/research/literature/analyze/index|index]]
## 最高原则

- **禁止直接编写配置文件**：创建新项目变体时，禁止直接用 Write 工具编写 config.json，必须先从同类型项目 Copy 已有的 config.json，再用 sed/replace 命令修改所需参数，避免引入幻觉差异。
- **严格按用户指令执行**：当用户说"调整 X，其他不变"时，只改 X，不要自作主张改其他配置。如果认为有更好的方向，应先询问确认。
- **遇到现有脏工作区默认继续**：如果发现与当前任务无关的已有改动或未提交产物，默认按 `Continue as-is` 处理，不要因此停下询问；只需避免覆盖、回滚或误改这些无关内容。
- **前台训练是硬约束**：`python cli.py -t PROJECT_NAME` 只有在当前可见终端、且命令持续附着在当前 Agent 会话时，才算“正在训练”；shell 超时后残留的子进程、仅写日志的隐藏后台任务、`Start-Process`/计划任务等都不算前台训练，发现后必须先停掉并清理状态，再重新以前台方式启动。
- **做消融时先守住语义等价**：像 FRIMLP 这类“只替换局部结构”的消融，必须保留基线的其余关键路径；不能为了省事把前端、fast_model 或系统初始化一并改掉，否则结论无效。
- **禁止自动 sweep 调参**：调参必须逐轮进行；每轮都要先读取上一轮的指标结果，再判断下一轮只改哪个 `learning_rate` 或 `model_subcfg` 方向，禁止预先批量生成一组盲扫项目并自动连续跑完。
  - **案例（2026-04-10）**：用户说"只调整 lr"，但我擅自尝试了更改 epochs、模型结构（INNER_KAN_UNITS/LAYERS、H_UNITS）、use_points、basis_activation、use_auto_lr 等参数，导致多项目 OOM 或指标恶化，且创建了多个不符合要求的项目。正确做法是：只改 lr 这一个参数，其他配置保持原样。
	- **案例（2026-04-11）**：FRIMLP 的正确语义是“保留 FRIKAN 前端，只把 KAN 替换成 MLP”。此前把它实现成独立分支并关闭 `USE_FAST_MODEL`，再加上 `prepare_systems()` 未覆盖 FRIMLP，导致 `h8` 实际退化成 1 路 `SIMOIIR`，训练结论全部失真。正确做法是：复用 FRIKAN 前端与 fast_model 路径，确认 `simoiir` 输出维度与 `H_UNITS` 一致，旧产物清空后再重训。

## 项目概述

**MET Nonlinear** - 电化学非线性矫正项目。当前核心代码统一收敛在 `src/` 下，重点模块包括 `src/core/`、`src/models/`、`src/inference/`、`src/analysis/`、`src/visualization/`、`src/calibration_analyzer/`。

参考索引：
- UniDesk microservice 集成：D601 `~/met_nonlinear` 固定通过 UniDesk SSH 透传开发 TypeScript 编排后端、Dockerfile 和训练容器；主 server 本地只开发 UniDesk frontend，详见 [docs/reference/unidesk_microservice.md](docs/reference/unidesk_microservice.md)。
- 项目结构与导入路径：详见 [docs/reference/project_structure.md](docs/reference/project_structure.md)。
- 问题定义与建模原则：详见 [docs/reference/modeling_principles.md](docs/reference/modeling_principles.md)。
- 并联 Wiener 模型到 Wiener-KAN 的逆解与补偿推导：详见 [docs/reference/wiener_kan_derivation.md](docs/reference/wiener_kan_derivation.md)。
- 准线性补偿视角下的 Wiener-KAN 结构可行性论证：详见 [docs/reference/quasi_linear_compensation_kan.md](docs/reference/quasi_linear_compensation_kan.md)。
- 模型结构演化与取舍：详见 [docs/reference/model_architecture_selection.md](docs/reference/model_architecture_selection.md)。
- 真实 1DCNN / TCN 卷积时序基线：详见 [docs/reference/conv_sequence_baselines.md](docs/reference/conv_sequence_baselines.md)。
	- 过程文档 [[05_1DCNN_KAN]]
- 数据集设计与覆盖边界：详见 [docs/reference/dataset_design.md](docs/reference/dataset_design.md)。
- 实验验证与外推边界：详见 [docs/reference/validation_boundaries.md](docs/reference/validation_boundaries.md)。
- 模拟电路实现与 SPICE 验证：详见 [docs/reference/circuit_realization.md](docs/reference/circuit_realization.md)。
- 多后端逐层推理与 wave 桥接：详见 [docs/reference/wave_layered_inference.md](docs/reference/wave_layered_inference.md)。
- WNET5 电路分层验证：详见 [docs/reference/wnet5_circuit_validation.md](docs/reference/wnet5_circuit_validation.md)。
- 器件选型、SPICE 收敛与偏置排查：详见 [docs/reference/spice_device_bias_practices.md](docs/reference/spice_device_bias_practices.md)。
- 时域数据与频响测量：详见 [docs/reference/timeseries_frequency_analysis.md](docs/reference/timeseries_frequency_analysis.md)。
- 仿真系统与非线性基：详见 [docs/reference/nonlinear_basis_simulation.md](docs/reference/nonlinear_basis_simulation.md)。
- RNN ???????????? [docs/reference/rnn_baselines.md](docs/reference/rnn_baselines.md)?
- 损失函数设计：详见 [docs/reference/loss_design.md](docs/reference/loss_design.md)。
- 训练与评估入口：详见 [docs/reference/training.md](docs/reference/training.md)、[docs/reference/evaluation.md](docs/reference/evaluation.md)、[docs/reference/inference.md](docs/reference/inference.md)。其中训练前检查、止损规则和 CNNKAN 调参经验统一收敛在 `training.md`。
- 测试入口与约定：详见 [docs/reference/testing.md](docs/reference/testing.md)。
- 拓展项目与边缘仿真：详见 [docs/reference/ep.md](docs/reference/ep.md)、[docs/reference/edge_device_emulation.md](docs/reference/edge_device_emulation.md)。其中 EP 项目索引、常见路径和 WNET5 电路验证图产物约定统一收敛在 `ep.md`。
- WNET5 分层验证中的 Project 权重加载、E96 量化误差仿真、SVF 拟合误差建模与报告约束：详见 [docs/reference/wnet5_circuit_validation.md](docs/reference/wnet5_circuit_validation.md)。
	- 过程文档 [[02_SVF层误差]]
- WebUI 可视化服务：详见 [docs/reference/webui.md](docs/reference/webui.md)。


## 环境配置

- py 环境：使用名为 `tf26` 的 Conda 环境 Python，而不是硬编码某台机器的绝对路径。
  - 定位规律：先找 `tf26` 这个环境名，再拼接到对应的 Conda 根目录，不要先假设用户名或 Conda 安装目录固定。
  - 常见路径规律：
    - `C:\Users\<用户名>\.conda\envs\tf26\python.exe`
    - `C:\Users\<用户名>\MiniConda3\envs\tf26\python.exe`
    - `C:\Users\<用户名>\miniconda3\envs\tf26\python.exe`
  - 已知主机实例：
    - `C:\Users\liang\.conda\envs\tf26\python.exe`
    - `C:\Users\lyon\MiniConda3\envs\tf26\python.exe`
  - 推荐定位命令：
    - `conda env list`
    - `where conda`
    - `Get-ChildItem "$env:USERPROFILE\\.conda\\envs\\tf26\\python.exe","$env:USERPROFILE\\MiniConda3\\envs\\tf26\\python.exe","$env:USERPROFILE\\miniconda3\\envs\\tf26\\python.exe" -ErrorAction SilentlyContinue`
  - GPU 环境默认行为：native Windows 的 CLI 会在导入 TensorFlow 前主动移除 `TF_GPU_ALLOCATOR=cuda_malloc_async`，并默认启用 `TF_FORCE_GPU_ALLOW_GROWTH=true`；环境边界与排查口径详见 [docs/reference/tf26_environment.md](docs/reference/tf26_environment.md)。
  - 详见 [docs/reference/tf26_environment.md](docs/reference/tf26_environment.md)
- **npm 路径规律**：Windows 环境下 `npm` 可能不在 PATH 中，调用时需使用完整路径 `D:/Program Files/nodejs/npm.cmd` 或通过 `npm.cmd` 调用。npm 相关文件（`package.json`、`node_modules`）只允许存在于 `src/webui/` 目录下，仓库根目录禁止放置。

## AGENTS.md 组织原则

- `AGENTS.md` 只作为项目级顶级索引，用于快速定位命令、入口和文档。
- 其他和 `AGENTS.md` 具有同等作用的文档（例如 `CLAUDE.md`）中只保留一行 `@AGENTS.md` 将其引导到 `AGENTS.md`，避免多种口径互相不一致。
- `AGENTS.md` 的具体功能区只保留四个顶级标题：`主命令`、`ep 子命令`、`projects/ex_projects`、`测试`，不额外拆出新的命令分类标题。
- 每个命令在 `AGENTS.md` 中保留一条主索引，命令下面可以挂多个功能子列表。
- 每个子列表只描述一个功能点，并使用一句话概括，不在此处展开实现细节、参数说明或背景分析。
- 每个子列表应独立对应一个 `docs/reference/` 下的参考文档；如果同一命令包含多个功能，则分别链接到各自文档。
- 所有功能的详细说明统一写入 `docs/reference/` 下的独立 Markdown 文档，并在 `AGENTS.md` 中提供对应链接索引。
- 仓库级使用说明不再维护 `.claude/skills/`；原本的本地技能文档统一并入 `docs/reference/`，由 `AGENTS.md` 负责总索引。
- 当某项功能需要补充说明时，优先更新 `docs/reference/` 的详细文档，再回到 `AGENTS.md` 维护对应子列表的一句话摘要与链接。


## CLI 命令 (cli.py)

### 主命令

- **PROJECT_NAME 路径格式**：主命令（`-t`、`-e`、`-m` 等）传入相对路径，格式为 `projects/项目路径`，如 `projects\01_LR_STUDY\FRIKANh6u6l6_e1k_1` 或 `projects/00_MAE_VS_AFMAE/FRIKANh8u6l6_base`。

- `python cli.py -t PROJECT_NAME`
	- 训练执行：训练模型并输出权重、训练日志与训练统计，详见 [docs/reference/training.md](docs/reference/training.md)。
	- 自动串联：训练完成后会先失效旧评估快照，再自动执行下游 `-e` / `metrics` 对应功能，直接生成当前权重的最新统一指标，详见 [docs/reference/training.md](docs/reference/training.md)。
	- 可见性约定：训练必须以前台可见方式直接执行，只有当前可见会话里持续附着的命令才算“正在训练”；shell 超时后残留的子进程或仅写日志的后台任务一律按异常中断处理，详见 [docs/reference/training.md](docs/reference/training.md)。
	- GPU 环境约定：native Windows 的 `tf26` 默认不使用 `cuda_malloc_async`，并优先采用 allow-growth 方式控制显存占用；遇到 GPU 初始化后无 traceback 退出时优先回看 [docs/reference/tf26_environment.md](docs/reference/tf26_environment.md)。
	- 特征缓存与起始段：如果训练与评估只在特定机器或旧 cache 上复现，优先检查特征缓存键是否覆盖全部特征参数，以及是否错误保留了序列开头的不完整窗口，详见 [docs/reference/training.md](docs/reference/training.md)。
	  - 一次只训练一个项目，避免同时训练多个导致系统资源爆满
	- 项目变体规则：每次调参或结构试验都必须复制成新的 project 路径，禁止在已有项目上直接改配置反复重训，详见 [docs/reference/training.md](docs/reference/training.md)。
	  - FRIMLP/FRIKAND 这类 FRIKAN 消融变体，训练前先确认 `prepare_systems()` 已执行且 `simoiir` 输出维度与 `H_UNITS` 一致，详见 [docs/reference/frimlp_ablation.md](docs/reference/frimlp_ablation.md)。

- `python cli.py -e PROJECT_NAME`
	- 评估流程：评估已训练模型并生成推理结果与误差指标，详见 [docs/reference/evaluation.md](docs/reference/evaluation.md)。
	- 自动汇总：评估成功结束后会立即刷新 `metrics.json`，让 WebUI 和统一指标表直接看到最新结果，详见 [docs/reference/evaluation.md](docs/reference/evaluation.md)。
	- 统一指标路径：`-e` 下的 loss、MAE、AFMAE 固定通过预测结果单一路径重算，不依赖训练时 compile 挂了几个 metrics，也绕过部分旧项目在 `model.evaluate()` 层的崩点，详见 [docs/reference/evaluation.md](docs/reference/evaluation.md)。
	- 兼容性约定：自定义模型包装类的 `predict()` 需兼容 Keras `verbose`、`use_scaler` 等参数，评估指标按 `float32` 口径计算以避免 dtype 冲突，详见 [docs/reference/evaluation.md](docs/reference/evaluation.md)。
	- 频响异常排查：如果 MAE/AFMAE 正常但频响三项极差，优先检查模型包装类 `predict()` 是否遗漏缩放/反缩放，以及 `linear_response.json.gains_comped` 是否仍停留在归一化量级，详见 [docs/reference/evaluation.md](docs/reference/evaluation.md)。
	- 写回时机：`training_info.json.evaluation_metrics` 在预测与频响产物生成后才最终写回，只有命令完整结束并出现评估完成日志，才能认为评估指标已落盘；中断后需重跑 `-e`，详见 [docs/reference/evaluation.md](docs/reference/evaluation.md)。
	- 计算量估算：导出单步推理计算量与平台加权耗时，详见 [docs/reference/compute_analysis.md](docs/reference/compute_analysis.md)。
	- 漏算诊断：如果 `compute_analysis.json` 出现 `unsupported_layer_type`、`estimate_status = partial` 或 `unsupported_layers` 非空，当前项目的 compute cost 仍可能被低估；`GRN(GRU)`、`LSTMTransformer` 与 `CNNKAN(Conv1D)` 的旧产物都应重跑新分析确认，详见 [docs/reference/compute_analysis.md](docs/reference/compute_analysis.md)。
- `python cli.py --metrics PROJECT_NAME`
	- 指标提取：统一按消融实验口径计算 `Freq Drift (Hz)`、`Sens Drift (%)` 与默认 `<=128 Hz` in-band 的 `Linearity (%)` 并导出 `metrics.json`，其他模块只读取该文件，详见 [docs/reference/metrics.md](docs/reference/metrics.md)。
	- 显式重算：`-t`、`-e` 和 `-m` 现已自动刷新 `metrics.json`；保留该命令主要用于手动重算、批量补齐和历史项目修复，详见 [docs/reference/metrics.md](docs/reference/metrics.md)。
	- 前置条件：`--metrics` 只汇总现有评估产物，不会自行补算 `evaluation_metrics`；如果项目在评估后又继续训练，或 `-e` 在频率响应阶段被中断，应先完整重跑 `-e`，再执行 `--metrics`，详见 [docs/reference/metrics.md](docs/reference/metrics.md)。
	- 诊断口径：如果 `metrics.json` 里时域误差正常但频响三项异常，先回看 `linear_response.json` 的物理量级，不要直接把问题归因于模型能力，详见 [docs/reference/metrics.md](docs/reference/metrics.md)。
	- 板端汇总：若项目 `config.json` 挂载 `board_inference_ep_path`，`metrics.json` 还会同步汇总 `QEMU-MAE`、`KEIL-MAE`、`KEIL-SPEED (ms/point)`，详见 [docs/reference/metrics.md](docs/reference/metrics.md)。
- `python cli.py --metrics --all-projects`
	- 批量重算指标：递归遍历 `projects/` 下所有项目并全量重算统一指标文件 `metrics.json`，详见 [docs/reference/metrics.md](docs/reference/metrics.md)。
- `python cli.py --metrics --all-projects --missing-only`
	- 缺失补齐：仅为缺失 `metrics.json` 的项目补生成统一指标文件，详见 [docs/reference/metrics.md](docs/reference/metrics.md)。
- `python cli.py -m PROJECT_NAME`
	- 模型结构导出：导出模型结构、参数和配置信息，详见 [docs/reference/model_info.md](docs/reference/model_info.md)。
	- 计算量估算：同步生成模型的计算量分析结果，详见 [docs/reference/compute_analysis.md](docs/reference/compute_analysis.md)。
	- 自动汇总：模型信息导出完成后会同步刷新 `metrics.json`，详见 [docs/reference/model_info.md](docs/reference/model_info.md)。
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

- `python cli.py server start`
	- 服务启动：启动 WebUI 可视化服务器，详见 [docs/reference/webui.md](docs/reference/webui.md)。
	- 视图约定：WebUI 对比页当前只保留 `Loss Curves` 和 `Table`，其中 `Loss Curves` 基于 `training_log.jsonl` 交互查看 train/val loss，详见 [docs/reference/webui.md](docs/reference/webui.md)。
	- Figure Studio：论文图 Studio 自动扫描 `ex_projects/plot/**/config.json` 并渲染到各 figure ex_project 的 `data/`，详见 [docs/reference/webui.md](docs/reference/webui.md)。
	- 前端构建：修改 `src/webui/src/` 后必须重新执行 `cd src/webui && npm run build`，否则服务仍会提供旧的 `dist` 静态资源，详见 [docs/reference/webui.md](docs/reference/webui.md)。
- `python cli.py server stop`
	- 服务停止：停止 WebUI 可视化服务器，详见 [docs/reference/webui.md](docs/reference/webui.md)。
- `python cli.py server status`
	- 服务状态：查看服务器运行状态和日志路径，详见 [docs/reference/webui.md](docs/reference/webui.md)。
- `python cli.py server logs`
	- 服务日志：查看服务器日志输出，详见 [docs/reference/webui.md](docs/reference/webui.md)。

- `python cli.py --vis-freq-response-compare PROJECT[@STATE] [PROJECT[@STATE]]`
	- 频响直连对比：直接基于 `linear_response.json` 生成频率响应对比图，无需进入 ep 工作流，详见 [docs/reference/freq_response_compare.md](docs/reference/freq_response_compare.md)。
	- 布局模式：支持叠加和左右并排两种布局，详见 [docs/reference/freq_response_compare.md](docs/reference/freq_response_compare.md)。

### ep 子命令 (拓展项目)

- 拓展项目区分于直接的训练项目，常用于横向评估，推理性能分析等基于训练项目产物的二次开发任务。

- **注意**：创建拓展项目时，**不要手动创建目录**。必须先运行 `python cli.py ep create "路径"` 创建模板；直接运行 `python cli.py ep "路径"` 时，如果配置不存在会直接报错退出。

- `python cli.py ep create "PROJECT/task-type/task-name"`
	- 模板生成：显式创建拓展项目模板，若配置已存在则拒绝覆盖，详见 [docs/reference/ep.md](docs/reference/ep.md)。
- `python cli.py ep "PROJECT/task-type/task-name"`
	- 配置驱动执行：仅执行已有配置的外部任务，若配置缺失则直接报错退出，详见 [docs/reference/ep.md](docs/reference/ep.md)。
	- 项目索引：仓库内常见 EP 路径、典型项目名和 WNET5 图产物约定统一维护在 [docs/reference/ep.md](docs/reference/ep.md)。
	- WNET5 长期约束：分层验证的权重来源、E96 量化误差仿真、SVF 拟合与报告产物规则统一维护在 [docs/reference/wnet5_circuit_validation.md](docs/reference/wnet5_circuit_validation.md)。
	- 论文图生成：`ex_projects/plot/**/config.json` 是论文图的标准工程入口，单图和拼图都通过 `python cli.py ep ex_projects/plot/.../<figure_project>` 渲染到自身 `data/`，详见 [docs/reference/paper_data_figure_pipeline.md](docs/reference/paper_data_figure_pipeline.md)。
- `python cli.py ep keil-bench "PROJECT/qemu-c-inference/task-name"`
	- 真机一键基准：对 `qemu-c-inference` EP 自动生成工程、Keil 编译、烧录、抓取串口并解析独立 JSON，详见 [docs/reference/ep.md](docs/reference/ep.md) 与 [docs/reference/edge_device_emulation.md](docs/reference/edge_device_emulation.md)。
- `python cli.py ep "compare/mae_vs_afmae"`
	- 损失函数消融对比：配置驱动读取多个 project 的 `metrics.json` 做统一横向比较，详见 [docs/reference/mae_vs_afmae.md](docs/reference/mae_vs_afmae.md)。
	- 板端列展示：若 compare 配置启用 `metrics.board_inference.enabled`，综合表可追加 `QEMU-MAE`、`KEIL-MAE`、`KEIL-SPEED (ms/point)`，详见 [docs/reference/mae_vs_afmae.md](docs/reference/mae_vs_afmae.md)。
- `python cli.py ep "ex_projects/compare/wiener_parallel_modeling"`
	- 并联 Wiener 建模：复现幅值依赖频响漂移的三支路并联 Wiener 等效模型，并输出拟合图与摘要指标，详见 [docs/reference/parallel_wiener_modeling.md](docs/reference/parallel_wiener_modeling.md)。
- `python cli.py ep "compare/compute_cost_calibration"`
	- 计算量参数标定：基于 STM32F405 真机时延反标 `add:multiply:MAP` 权重，并输出搜索报告与可视化，详见 [docs/reference/paper_compute_cost_calibration_method.md](docs/reference/paper_compute_cost_calibration_method.md)。
- `python cli.py ep "PROJECT/wnet5-circuit-validation/layer2"`
	- 电路验证：执行 WNET5 电路验证类外部任务，详见 [docs/reference/ep.md](docs/reference/ep.md)。
	- 电路验证规则：通道映射、环境变量路径、E96 热力图和频响对照口径详见 [docs/reference/wnet5_circuit_validation.md](docs/reference/wnet5_circuit_validation.md)。
- `python cli.py ep "PROJECT/freq-response-compensator/test"`
	- 频响补偿任务：执行频率响应补偿器外部任务，详见 [docs/reference/ep.md](docs/reference/ep.md)。
	- 路径格式：支持拓展项目、训练项目和简化格式，详见 [docs/reference/ep.md](docs/reference/ep.md)。

### projects/ex_projects

- `projects\01_LR_STUDY\` 系列 - `固定 LR vs 余弦衰减`：固定学习率尝试达到或优于余弦衰减效果，最优固定 LR 约 0.0005，还未达到。详见 [docs/reference/lr_tuning_fixed_vs_cosine.md](docs/reference/lr_tuning_fixed_vs_cosine.md)。
- `projects\01_LR_STUDY\CNNKANh8u6l6_e1k_lr14e5_stable` - CNNKAN 替换消融稳定版：在默认旧 batch-size 行为下可跑满 1000 epoch，并保留旧项目复现约束。详见 [docs/reference/cnnkan_ablation.md](docs/reference/cnnkan_ablation.md)。
- `projects\05_1DCNN\1DCNNc4u8k20l8_e1k_lr18e3_pd8l8_true` - 真实 1DCNN 卷积时序基线：当前仓库保留的 canonical `1DCNN` 对照项目。详见 [docs/reference/conv_sequence_baselines.md](docs/reference/conv_sequence_baselines.md)。
- `projects\06_TCN\TCNc4d1248k3_nopd_true_e1k_lr2e3` - 真实 TCN 卷积时序基线：当前仓库保留的 canonical `TCN` 对照项目。详见 [docs/reference/conv_sequence_baselines.md](docs/reference/conv_sequence_baselines.md)。
- `projects\07_RNN\RNNu16_e1k_puremae_r15` - 真实 RNN 时序基线：当前仓库保留的 canonical `RNN` 对照项目。详见 [docs/reference/rnn_baselines.md](docs/reference/rnn_baselines.md)
- `projects\04_FRIMLP\FRIMLPh8u6l6_e1k_lr7e4_mlp20l6_tanh_d00` - FRIMLP 真消融达标案例：修复前端与 fast_model 接线后，1000 epoch 达到 `Freq Drift = 5.8179 Hz`。详见 [docs/reference/frimlp_ablation.md](docs/reference/frimlp_ablation.md)。
- `ex_projects/compare/mae_vs_afmae` - MAE vs AFMAE 消融对比：执行 MAE/AFMAE 损失函数消融实验并生成对比报告，详见 [docs/reference/mae_vs_afmae.md](docs/reference/mae_vs_afmae.md)。
- `ex_projects/compare/wiener_parallel_modeling` - 并联 Wiener 等效建模：复现 MET 大信号幅频耦合漂移并输出报告、图像与摘要 JSON，详见 [docs/reference/parallel_wiener_modeling.md](docs/reference/parallel_wiener_modeling.md)。
- `ex_projects/compare/compute_cost_calibration` - Compute Cost 标定：用 STM32F405 真机时延标定 `add:multiply:MAP` 权重，详见 [docs/reference/paper_compute_cost_calibration_method.md](docs/reference/paper_compute_cost_calibration_method.md)。
- `ex_projects/compare/lr_test_1k_epoch` - LR 消融对比：对比 1k epoch 训练中不同学习率（0.01/0.002/0.001）的训练效果，详见 [docs/reference/lr_test_1k_epoch.md](docs/reference/lr_test_1k_epoch.md)。


### 测试命令
- 过程文档 [[03_单元测试]]

- `python cli.py --test`
	- CLI 测试入口：通过 CLI 入口运行测试集，详见 [docs/reference/testing.md](docs/reference/testing.md)。
	- 环境约定：Windows 下优先通过 `conda.bat run --no-capture-output -n tf26` 启动，详见 [docs/reference/testing.md](docs/reference/testing.md)。
- `python cli.py --test --test-path src/logger/tests`
	- 路径筛选：指定测试目录，详见 [docs/reference/testing.md](docs/reference/testing.md)。
- `python cli.py --test --test-workers 4 --test-timeout 300`
	- 并行与超时：配置并行数和超时时间，详见 [docs/reference/testing.md](docs/reference/testing.md)。
	- 卡死边界：`1` 分钟无输出更适合作为排障信号，长期硬约束仍以 pytest timeout 为准，详见 [docs/reference/testing.md](docs/reference/testing.md)。

- `pytest`
	- 默认测试集：直接运行仓库默认测试集，详见 [docs/reference/testing.md](docs/reference/testing.md)。
- `pytest src/analysis/tests/test_analysis_comprehensive.py::TestAliasSuppression::test_module_import -v`
	- 单测定位：运行单个测试文件或函数，详见 [docs/reference/testing.md](docs/reference/testing.md)。
- `pytest -k "test_module_import"`
	- 关键字筛选：按关键字筛选测试，详见 [docs/reference/testing.md](docs/reference/testing.md)。

- `py -3 C:\Users\lyon\.agents\skills\keil\keil-cli.py program --wait -p src/tests/keil_projects/met_keil_405/MDK-ARM/Electrochemical geophone.uvprojx -m daplink --program-backend <keil|pyocd> -u <probe_uid> -t MET405`
	- STM32F405 真机烧录：`met_keil_405` 在单 probe 隔离后可复用 Keil backend，无法隔离时改走 pyOCD，并以串口启动日志作为最终签收，详见 [docs/reference/keil_stm32f405_programming.md](docs/reference/keil_stm32f405_programming.md)。
- `py -3 C:\Users\lyon\.agents\skills\keil\keil-cli.py detect -u <probe_uid> -p src/tests/keil_projects/met_keil_405/MDK-ARM/Electrochemical geophone.uvprojx -t MET405`
	- STM32F405 target-aware 探测：让 DAP-Link detect 直接复用工程 `Device` 推导 pyOCD target override，避免只拿到 generic `CoreSightTarget`，详见 [docs/reference/keil_stm32f405_programming.md](docs/reference/keil_stm32f405_programming.md)。

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
