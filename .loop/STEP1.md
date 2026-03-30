## 任务

下载 GAP 引用的文献 PDF 并转换为 Markdown 格式，收集到 `docs/research/literature/pdfs/` 目录。

**关键要求**：GAP 支撑文档（如 `docs/research/gap/GAP{n}_xxx/index.md`）中的文献条目，除了下载链接外，还必须包含对应的本地 PDF 文件路径（如 `docs/research/literature/pdfs/xxx.pdf`），确保可以离线访问原文。

## 核心原则

- **所有 `docs/research/literature/` 目录下的文档必须使用中文编写**
- 每轮都要主动拓展检索渠道，不能只重复浏览同一批关键词
- 收集时优先找原始论文，尽量记录完整引用信息（作者、年份、标题、期刊/会议、DOI）
- 发现疑似重复或高度相似的文献时先标记，交给后续步骤核对
- STEP1 只负责"发现文献线索并结构化落表"，不要在这里写大段文献分析
- 聚合平台（如 Google Scholar、ResearchGate）上的论文先记为"待核实线索"，不能直接升级为有效文献
- STEP1 没有评判权，也没有推荐权；只允许记录事实、来源和待核实方向
- 鼓励使用子代理并行拓展不同方向、不同数据库或不同理论领域的文献检索

## 输入

| 输入文件 | 说明 |
|---------|------|
| `.loop/PRINCIPLE.md` | 包含11个GAP的定义和支撑目标 |
| `docs/IDEA.md` | 论文核心思路 |
| `docs/research/literature/literature_catalog.md` | 已有文献目录（如有） |
| `docs/research/literature/raw_literature.md` | 已有文献线索（如有） |

## 输出

| 输出文件 | 说明 |
|---------|------|
| `docs/research/literature/literature_catalog.md` | 结构化文献目录 |
| `docs/research/literature/raw_literature.md` | 原始文献线索表 |
| `docs/research/literature/{YYYYMMDD}/survey_report.md` | 调研报告 |

## GAP文献需求分析

STEP1需为每个GAP识别所需文献类型，建立GAP→文献需求映射：

| GAP编号 | GAP主题 | 所需文献类型 |
|---------|---------|-------------|
| GAP1 | 电化学地震检波器频响漂移（温度→非线性） | 温度漂移研究、非线性建模 |
| GAP2 | 线性度测量范围偏窄 | 线性度标定方法，已有充分支撑 |
| GAP3 | 频率漂移的震级因素 | 震级/幅值对频响影响研究 |
| GAP4 | 线性模型缺乏非线性建模 | Wiener/Hammerstein非线性系统识别 |
| GAP5 | 温度外未建模震级因素 | 幅值相关频响漂移研究 |
| GAP6 | 力反馈量程限制 | 前馈vs反馈补偿架构对比 |
| GAP7 | 前馈利用非线性提升量程 | 非线性区前馈补偿应用 |
| GAP8 | 频率相关补偿精度优势 | 频率相关vs频率无关补偿方法 |
| GAP9 | 频率相关补偿计算效率 | 频域补偿计算复杂度分析 |
| GAP10 | AFMAE vs 纯MAE | 频域损失vs时域损失对比 |
| GAP11 | AFMAE vs 其他频域损失 | AFMAE vs FreDF/FIRE/OLMA效率对比 |

## 推荐检索方向

### P0 必须覆盖

1. **Wiener 模型理论**
   - 关键词：Wiener system, nonlinear system identification, Hammerstein-Wiener
   - 检索数据库：IEEE Xplore, ScienceDirect, Google Scholar
   - 目标：找到 Wiener 模型的经典论文和最新应用

2. **KAN 网络**
   - 关键词：Kolmogorov-Arnold Networks, KAN, spline networks
   - 检索数据库：arXiv, Google Scholar, ACM Digital Library
   - 目标：找到 KAN 原始论文及在时序/非线性建模中的应用

3. **频域损失函数**
   - 关键词：frequency domain loss, AFMAE, spectral loss, time series prediction
   - 检索数据库：IEEE Xplore, Google Scholar
   - 目标：找到频域损失函数在时间序列中的应用

### P1 必须覆盖

4. **深度学习漂移补偿**
   - 关键词：drift compensation, sensor drift, electrochemical sensor, seismic sensor
   - 检索数据库：IEEE Xplore, ScienceDirect, Google Scholar
   - 目标：找到深度学习方法用于信号漂移补偿的相关工作

5. **神经网络架构对比**
   - 关键词：LSTM vs CNN vs Transformer, computational efficiency, time series
   - 检索数据库：IEEE Xplore, arXiv, Google Scholar
   - 目标：找到不同架构在计算效率方面的对比研究

6. **神经网络架构效率对比**
   - 关键词：RNN vs CNN, computational efficiency, parameter count, FLOPs
   - 检索数据库：IEEE Xplore, arXiv, Google Scholar
   - 目标：找到 RNN 相对于 1D-CNN 计算效率的对比研究

### P2 可选扩展

7. **电化学/地震信号数据集**
   - 关键词：electrochemical dataset, seismic signal dataset, benchmark

8. **LUT 实现相关**
   - 关键词：look-up table, LUT implementation, neural network acceleration

### P2 可选扩展 - MEASUREMENT 与传感器非线性补偿

9. **MEASUREMENT 实验测量方法**
   - 关键词：MET measurement, experimental measurement methodology, sensor characterization, frequency response measurement, nonlinear calibration
   - 检索数据库：IEEE Xplore, ScienceDirect, **Measurement 期刊**, Google Scholar
   - **目标：找到 50 篇和当前传感器非线性问题研究相关的 MEASUREMENT 期刊论文，其中至少 40 篇是 2020 年后的**
   - **当前进度**：已找到 2 篇（Xu&Wang 2008, Dutta 2018），需继续扩充

10. **传感器非线性补偿**
    - 关键词：sensor nonlinearity compensation, nonlinear calibration, temperature compensation, drift correction, electrochemical sensor, seismic sensor
    - 检索数据库：IEEE Xplore, ScienceDirect, Google Scholar, MDPI Sensors
    - 目标：找到传感器非线性建模与补偿的传统方法和深度学习方法

11. **数据集构建与发布标准**
    - 关键词：dataset publication, data acquisition methodology, sensor data standard, benchmark dataset release
    - 检索数据库：IEEE Xplore, Google Scholar, Zenodo, Figshare
    - 目标：找到数据集发布的参考论文，特别是电化学/地震信号领域

## 流程

- **编码检查**：在开始任何工作前，检查所有要写入的文档编码是否正确。如发现文件编码错误（如乱码），必须先完整读取文件内容，然后用相同路径完全重写该文件以修复编码问题，然后再继续
- 先读取 `.loop/PRINCIPLE.md` 和 `docs/IDEA.md` 理解当前研究重点
- 检查 `docs/research/literature/` 目录下的已有文献列表，避免重复收集同一批信息
- 联网检索文献，优先寻找与当前研究重点直接相关的论文
- 将本轮原始调研过程和发现写入 `docs/research/literature/{YYYYMMDD}/` 下的调研报告，至少记录：检索范围、数据库、关键词、发现结果、待核实事项、排除依据、产出文件
- 调研报告优先按 `.loop/REPORT_TEMPLATE.md` 中"调研报告模板"编写，保证不同轮次结构一致
- 更新 `docs/research/literature/literature_catalog.md`，优先补充新文献而非重复描述旧文献
- 将新增文献线索写入 `docs/research/literature/raw_literature.md` 的统一表格或统一字段列表，每条至少包含：
  - 作者
  - 年份
  - 标题
  - 期刊/会议
  - DOI/链接
  - 主题分类（P0/P1/P2）
  - 与论文的相关性（高/中/低）
  - 核实状态（待核实/已获取/疑似重复）
  - 备注
- 若同一文献已存在，只更新该条目，不新增冗余长段落
- 对信息不全或疑似转载的条目，只记录"下一步核对方向"
- 允许记录"文献已定位"，但不允许写"重要文献""核心引用"之类结论
- 若本轮还更新了 `literature_catalog.md`、`raw_literature.md` 等汇总文档，必须在文档中补充对应调研报告路径引用

## GAP文献缺口识别

在完成文献收集后，需识别每个GAP的文献支撑缺口：

1. 读取 `docs/research/literature/verified_literature.md` 中已有文献
2. 对照GAP文献需求表，检查每个GAP是否有足够文献支撑
3. 将缺口记录到 `docs/research/literature/GAP文献缺口.md`
4. 将缺口文献作为下一轮STEP1检索的重点方向

## 禁止行为

- 禁止只贴标题不做说明
- 禁止把无法判断来源真伪的信息直接写成"已确认有效"
- 禁止在 `raw_literature.md` 为同一文献新增多个语义重复条目
- 禁止修改 `docs/research/literature/verified_literature.md`
- 禁止给文献下最终评价结论或引用建议
