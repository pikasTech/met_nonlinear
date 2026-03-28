## 任务

系统性搜索和收集与转投论文主题相关的文献，形成结构化的文献线索库。

## 核心原则

- 每轮都要主动拓展检索渠道，不能只重复浏览同一批关键词
- 收集时优先找原始论文，尽量记录完整引用信息（作者、年份、标题、期刊/会议、DOI）
- 发现疑似重复或高度相似的文献时先标记，交给后续步骤核对
- STEP1 只负责"发现文献线索并结构化落表"，不要在这里写大段文献分析
- 聚合平台（如 Google Scholar、ResearchGate）上的论文先记为"待核实线索"，不能直接升级为有效文献
- STEP1 没有评判权，也没有推荐权；只允许记录事实、来源和待核实方向
- 鼓励使用子代理并行拓展不同方向、不同数据库或不同理论领域的文献检索

## 输入文件

.loop/PRINCIPLE.md
docs/research/literature/
docs/IDEA.md

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

## 流程

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

## 输出文件

- `docs/research/literature/literature_catalog.md`
- `docs/research/literature/raw_literature.md`
- `docs/research/literature/{YYYYMMDD}/` 下的调研报告

## 禁止行为

- 禁止只贴标题不做说明
- 禁止把无法判断来源真伪的信息直接写成"已确认有效"
- 禁止在 `raw_literature.md` 为同一文献新增多个语义重复条目
- 禁止修改 `docs/research/literature/verified_literature.md`
- 禁止给文献下最终评价结论或引用建议
