# 频率响应补偿前后图生成机制调查报告

> 项目：WNET5q1h2u6l3  （命令：`python cli.py main -e WNET5q1h2u6l3`）  
> 日期：2025-09-27

## 1. 入口命令解析与任务链
命令 `python cli.py main -e WNET5q1h2u6l3` 解析流程：
1. `cli.py` -> 解析子命令 `main`，`-e` 设定 `task_type = EVALUATE`，目标项目名 `WNET5q1h2u6l3`。
2. 进入 `_run_main_commands` -> `core.task_dispatcher.dispatch_task('evaluate', ['WNET5q1h2u6l3'], args)`。
3. `dispatch_task` 中匹配到 `evaluate` -> `_handle_evaluate_task`。
4. `_handle_evaluate_task`：
   - 实例化 `ProjectManager(project_path)`
   - 调用 `ProjectManager.evaluate()`

`ProjectManager.evaluate()` 关键步骤：
- 构造 `ModelEngine`，加载数据与模型：`prepare_dataset_and_model()`
- 可能加载验证最优权重 (`use_best_val_weights = True`)
- 执行 `model_engine.evaluate_loss()`
- 调用 `self.run_prediction(model_engine)` —— 频率响应图生成的核心触发点

`run_prediction()` 中：
```python
if self.config.use_predict_fr:  # 默认 True
    model_engine.predict_FR(self.config.USE_PREDICT_LINEAR)  # 默认 USE_PREDICT_LINEAR=True
```

`ModelEngine.predict_FR()` 针对 `dataset_type == 'MET'`：
调用：
```python
FR_for_comp_real_data(
    self.model_comp,
    self.dataset_test,
    freq_range = config.dataset.freq_range_hz 或 (10,128),
    gain_range=(30,200),
    freq_start_skip=0,
    freq_end_skip=2,
    output_folder=self.checkpoint_dir,  # projects/WNET5q1h2u6l3/data
    use_linear_response=USE_PREDICT_LINEAR
)
```
这一步生成补偿前后频率响应数据与（可视化）线性度散点图，并写出 `projects/WNET5q1h2u6l3/data/linear_response.json`。

## 2. 数据计算与文件产出
核心函数：`visualization/model_analysis.py::FR_for_comp_real_data`

输入：
- 训练/评估阶段模型 `model_comp`（Keras 模型）
- `Dataset_COMP` 数据集对象（包含多震级、多频率的输入 / 原始输出）

主要处理步骤：
1. `dataset.reshape2feature(dataset.output_ori)` 形成批量特征输入；`model.predict()` 得到补偿后预测（补偿结果 = 模型拟合输出）。
2. 对每个震级 sweep：
   - 构造 `TimeSeries` 序列（原始输入、原始输出、补偿后输出）。
   - 通过 `System.fromTimeSeries(... frequencies=dataset.freq_list)` 得到原始与补偿后系统对象（包含频率响应增益）。
3. 收集：
   - `gains_origin` = 每个震级对应的 |H(f)| 列表
   - `gains_comped` = 模型输出对应的 |H(f)| 列表
   - `magnitudes` = 震级列表（来自 `dataset.magn_list`）
   - `frequencies` = 频率列表 `dataset.freq_list`
4. 线性化可视化（若 `use_linear_response=True`）：
   - 对每个频率点 i：绘制散点：横轴震级，纵轴归一化输出值（原始：圆点；补偿：三角）
   - 同时写出 JSON：
```json
{
  "gains_origin": [[...], [...], ...],
  "gains_comped": [[...], [...], ...],
  "magnitudes": [...],
  "frequencies": [...],
  "fit_params_origin": [[A,B,C], ...],
  "fit_params_comped": [[A,B,C], ...]
}
```
文件路径：`projects/WNET5q1h2u6l3/data/linear_response.json`

该 JSON 即为后续“补偿前后”频率响应对比图的直接数据源。

## 3. 补偿前后频率响应图的两类生成方式
### 3.1 评估阶段（当前命令）生成的散点“线性响应”图
- 由 `FR_for_comp_real_data` 内部使用 `matplotlib` 绘制（代码段 约 1~130 行）。
- 图例：`Origin @ <freq> Hz` 与 `Compensated @ <freq> Hz`。
- 这是频率逐点对震级线性度的可视化，而非传统 Bode 曲线。
- 保存路径：使用 `plt.figure(figsize=(12,8))` 后未在函数中显式保存（注意：函数中只保存 JSON；绘图窗口依赖外部 `plt.show()` 或脚本上下文，如果需要保存需补充保存逻辑）。
  当前仓库版本此图不会自动保存静态文件，仅 JSON 数据持久化。

### 3.2 独立频率响应对比图（Bode 视角）
命令使用 `--vis-freq-response-compare` 时触发：
- 入口：`core/task_dispatcher._handle_freq_response_compare_task`
- 数据加载：`visualization/frequency_response_json_comparator.py::LinearResponseDataLoader` 读取 `linear_response.json`。
- 状态区分：
  - `origin` -> `gains_origin`
  - `compensation` -> `gains_comped`
- 可视化：`FrequencyResponseComparator.compare_sources()`：
  - Overlay：两种状态叠加；marker 分别 `o` 与 `^`。
  - Side_by_side：左右子图分开显示。
- 默认输出目录：`projects/results/`，文件名模式：
  `bode_plot_overlay_<proj1>_<state1>_vs_<proj2>_<state2>.png`

> 若只传一个项目名：自动构造 origin vs compensation 的对比。

## 4. 相关配置与参数影响
| 参数 / 配置 | 位置 | 作用 |
|-------------|------|------|
| `use_predict_fr` | `config.Config` (默认 True) | 是否在评估阶段调用频率响应预测流程 |
| `USE_PREDICT_LINEAR` | `config.Config` | 传入 `predict_FR` 控制是否生成线性响应相关 JSON/图 |
| `dataset.dataset.freq_range_hz` | `config.json` 或运行时 | 若非 None，替代默认 (10,128) 用于系统拟合区间 |
| `freq_start_skip`, `freq_end_skip` | `predict_FR` 固定参数 | 控制跳过首尾频点数量（绘制线性响应时） |
| `Dataset_COMP` | 数据加载模块 | 提供 `magn_list`, `freq_list`, `output_ori` 等源数据 |
| `System.fromTimeSeries` | `calibration_analyzer.exam_class` | 计算每频率点幅值（增益） |

## 5. “补偿”含义来源
“补偿后”(Compensated) 数据 = 模型对原始输出的预测（通过训练拟合实现的频率幅值校正）。流程：
1. 原始输出：物理/仿真采集 `output_ori`。
2. 模型输入：对应激励序列 `inputs`。
3. 模型预测：`pre_features -> pre_samples -> comped_trs`。
4. 对比 `System` 估计出的频域增益差异，显示补偿效果（波动收敛、假频抑制等）。

## 6. 关键调用链总结（文字拓扑）
```
cli.py main -e WNET5q1h2u6l3
 └─ core.task_dispatcher.dispatch_task(evaluate)
     └─ ProjectManager.evaluate()
         ├─ prepare_dataset_and_model()
         ├─ model_engine.evaluate_loss()
         └─ run_prediction()
             └─ if use_predict_fr:
                 └─ ModelEngine.predict_FR()
                     └─ FR_for_comp_real_data()
                         ├─ model.predict() -> 补偿后输出
                         ├─ System.fromTimeSeries() 两次 (origin/comped)
                         ├─ 收集 gains_origin / gains_comped
                         └─ 写出 linear_response.json

后处理（可选命令 --vis-freq-response-compare）
 └─ FrequencyResponseComparator
     ├─ LinearResponseDataLoader 读取 linear_response.json
     └─ 对比绘制 Origin vs Compensation Bode 样式图
```

## 7. 与 WNET5CircuitValidator 的区别（避免混淆）
- `visualization/wnet5_circuit_validator.py` 针对 WaveNet5 的“符号传递函数 + SVF + Dense”推导理论频率响应，与真实实测 Excel 数据对比，输出 `results.json` 及 `plots/frequency_response*.png`。
- 本调查的补偿前后图与其无直接调用关系；评估命令 `-e` 不会触发 Circuit Validator。

## 8. 发现的改进点（可选建议）
1. `FR_for_comp_real_data` 目前未保存线性散点图，若需要固定产物可增加 `plt.savefig(os.path.join(output_folder,'linear_response_plot.png'))`。
2. JSON 未包含单位与说明，可加入 `"meta": {"gain_unit":"V·s/m", "description":"..."}`。
3. 频率跳过参数写死（0,2），可外部配置化。 
4. 评估阶段可自动触发 origin vs compensation 的 Bode 叠加图，减少手动调用。

## 9. 核心代码定位索引
| 功能 | 文件 | 函数 / 位置 |
|------|------|-------------|
| CLI 参数解析 `-e` | `core/cli_parser.py` | 行 220~300 (`--evaluate`) |
| 任务分发 evaluate | `core/task_dispatcher.py` | `_handle_evaluate_task` |
| 运行预测入口 | `core/project_manager.py` | `run_prediction` |
| 调用频响预测 | `core/model_engine.py` | `predict_FR` (行 ~600+) |
| 频响/补偿数据生成 | `visualization/model_analysis.py` | `FR_for_comp_real_data` |
| 对比图（外部可视化） | `visualization/frequency_response_json_comparator.py` | `FrequencyResponseComparator` |

## 10. TL;DR（快速结论）
评估命令 `python cli.py main -e WNET5q1h2u6l3` 会在模型加载并计算评价后，通过一系列调用链最终执行 `FR_for_comp_real_data`，生成 `linear_response.json`，其中包含补偿前 (`gains_origin`) 与补偿后 (`gains_comped`) 的频率响应幅值矩阵。补偿后的数据来自模型对输入信号的预测输出。若需要频率响应的对比图（Bode 风格），需额外执行带 `--vis-freq-response-compare` 的 CLI 以从该 JSON 读取并绘制；当前评估流程默认不保存散点线性响应图，只保存 JSON。

---
（完）
