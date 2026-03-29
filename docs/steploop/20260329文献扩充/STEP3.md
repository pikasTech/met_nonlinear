## 任务

基于已分析的文献进行系统性综合整理，形成可直接支撑论文修订的理论框架和内容素材。

## 核心原则

- **所有 `docs/research/literature/` 目录下的文档必须使用中文编写**
- 以"支撑论文修订声称、回应审稿意见"为目标做整理，而不是只做静态归档
- 分类必须服务于论文修订决策，例如理论支撑、对比方法、审稿意见回应
- 对已分析文献优先更新已有清单，而不是反复新建分散文档
- STEP3 只做决策层整理，不重新写分析过程
- `key_references.md` 必须保持短而精，只保留真正能支撑论文声称的核心文献
- STEP3 有推荐权，但没有审核权；只能消费 STEP2 已确认的结果，不能自行补充分析或改判
- STEP3 消费的所有结论都必须能回溯到分析报告或原始文献，禁止引用来源不明的二手结论

## 输入文件

.loop/PRINCIPLE.md
docs/research/literature/literature_catalog.md
docs/research/literature/raw_literature.md
docs/research/literature/verified_literature.md
docs/research/literature/excluded_literature.md
docs/IDEA.md
docs/FRIKAN_REJECT.md

## 流程

- **编码检查**：在开始任何工作前，检查所有要写入的文档编码是否正确。如发现文件编码错误（如乱码），必须先完整读取文件内容，然后用相同路径完全重写该文件以修复编码问题，然后再继续

### A. 目录整理

- 整理根目录的临时文件和杂乱文件，保持根目录干净，符合根目录白名单

#### 根目录白名单（允许存在的文件/目录）

📄 文件	CLAUDE.md, cli.py, conftest.py, pytest.ini, README.md, README_circuit.md, requirements.txt, waveviewer.bat
📁 目录	.claude/, .git/, .loop/, .playwright-cli/, .vscode/, assets/, cache/, calibration_analyzer/, circuit_design/, docs/, ex_projects/, exam_data/, logs/, paper/, projects/, scripts/, src/, .gitignore

#### 整理规则
- 如发现违规文件，立即移动到对应目录或 `logs/temp/`（临时文件）
- 禁止在根目录创建任何新的文件，禁止污染根目录
- 禁止在根目录生成或保存 .log 文件

### B. 文献整理

- 读取并整理已分析文献，按主题分类：
  - Wiener 模型理论 → 支撑建模模拟声称 + Wiener-KAN 架构联系
  - KAN 网络理论 → 支撑计算效率声称
  - AFMAE 损失函数 → 支撑训练方法声称
  - 深度学习漂移补偿 → 支撑相关工作章节
  - 神经网络架构对比 → 支撑效率对比实验设计
- 针对审稿意见，逐条匹配可支撑的文献和理论：
  - R3-4/R4-7 更多对比方法：找到 CNN、Transformer、RNN 相关文献
  - R3-6/R4-6 数据集描述：找到数据集构建参考
  - R4-8 计算成本分析：找到效率评估方法文献
- 更新核心文献清单 `docs/research/literature/key_references.md`，突出最能支撑论文声称的文献
- 提炼可直接写入论文的内容素材：
  - 相关工作章节的草稿段落
  - 理论支撑的具体表述
  - 对比方法的选择依据
  - 评估指标的参考来源
- 如发现沉淀文档过长或重复严重，要做合并压缩和结构优化，但不得丢失关键信息
- 维护 `docs/research/literature/SUMMARY.md`，确保其简洁反映当前文献调研进展
- 更新 `key_references.md`、`theory_framework.md`、`docs/research/literature/SUMMARY.md` 等综合文档时，必须引用所依据的分析报告路径
- 优先把经验沉淀为：
  - 可直接引用的文献列表
  - 支撑论文声称的理论框架
  - 回应审稿意见的文献依据
  - 论文相关工作章节的草稿大纲
- 只能从 `docs/research/literature/verified_literature.md` 选出 `key_references.md` 的候选，禁止从 `docs/research/literature/raw_literature.md` 直接提拔文献
- 如果发现 `verified_literature.md` 中某文献证据链不足，只能标记"需复核"并等待 STEP2 处理，不能自行改成有效或无效

## 审稿意见回应映射（第二稿重点）

根据 `docs/FRIKAN_REJECT.md` 和第二稿策略，以下审稿意见需要文献支撑：

| 审稿意见 | 需要支撑的内容 | 对应文献类型 |
|---------|--------------|-------------|
| R3-4 对比模型有限 | CNN、Transformer、RNN 在时序中的应用 | 架构对比 |
| R3-5 RVTDCNN 是否最佳 | 功率放大器线性化方法总结 | 补偿方法 |
| R3-6 数据集细节不足 | 数据集构建参考论文 | 数据集 |
| R4-1 激活函数比较 | ReLU、tanh、B-spline 对比研究 | 激活函数 |
| R4-8 计算成本分析 | 效率评估标准方法 | 效率评估 |

**注意**：PIKAN 相关（物理约束、奇对称性、正定性）已废弃，不需要为这些提供文献支撑。

## 输出文件

- `docs/research/literature/key_references.md`
- `docs/research/literature/theory_framework.md`
- `docs/research/literature/paper_draft_segments.md`
- `docs/research/literature/SUMMARY.md`

## 禁止行为

- 禁止调研 PIKAN 相关内容（已废弃）
- 禁止调研 FRIRNN 频响注入相关内容（已废弃）
- 禁止在根目录创建任何新的文件
- 禁止在根目录生成或保存 .log 文件
- 禁止把未核实文献直接列入核心文献清单
- 禁止只做概括总结而不更新具体文献清单
- 禁止修改 `docs/research/literature/raw_literature.md`
- 禁止修改 `docs/research/literature/excluded_literature.md`
- 禁止重新解读或覆盖 STEP2 的分析结论
