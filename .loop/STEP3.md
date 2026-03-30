## 任务

下载 GAP 引用的文献 PDF 并转换为 Markdown 格式，收集到 `docs/research/literature/pdfs/` 目录。

**关键要求**：GAP 支撑文档（如 `docs/research/gap/GAP{n}_xxx/index.md`）中的文献条目，除了下载链接外，还必须包含对应的本地 PDF 文件路径（如 `docs/research/literature/pdfs/xxx.pdf`），确保可以离线访问原文。

## 核心原则

- **所有 `docs/research/literature/` 和 `docs/research/gap/` 目录下的文档必须使用中文编写**
- 以"支撑论文GAP声称、回应审稿意见"为目标做整理，而不是只做静态归档
- 分类必须服务于论文修订决策，例如理论支撑、对比方法、审稿意见回应
- 对已分析文献优先更新已有清单，而不是反复新建分散文档
- STEP3 只做决策层整理，不重新写分析过程
- `key_references.md` 必须保持短而精，只保留真正能支撑论文声称的核心文献
- STEP3 有推荐权，但没有审核权；只能消费 STEP2 已确认的结果，不能自行补充分析或改判
- STEP3 消费的所有结论都必须能回溯到分析报告或原始文献，禁止引用来源不明的二手结论

## 输入

| 输入文件 | 说明 |
|---------|------|
| `.loop/PRINCIPLE.md` | 包含11个GAP的定义和支撑目标 |
| `docs/IDEA.md` | 论文核心思路 |
| `docs/research/literature/verified_literature.md` | 已验证文献（含GAP支撑标注） |
| `docs/research/literature/excluded_literature.md` | 排除文献 |
| `docs/research/literature/key_references.md` | 核心文献清单 |
| `docs/research/literature/GAP文献缺口.md` | GAP文献缺口分析 |
| `docs/research/gap/GAP_SUMMARY.md` | GAP总体支撑矩阵（如有） |

## 输出

| 输出文件 | 说明 |
|---------|------|
| `docs/research/gap/GAP{n}_xxx/index.md` | 第n个GAP的支撑文档 |
| `docs/research/gap/GAP_SUMMARY.md` | GAP总体支撑矩阵 |
| `docs/research/literature/key_references.md` | 核心文献清单（更新） |
| `docs/research/literature/theory_framework.md` | 理论框架 |
| `docs/research/literature/paper_draft_segments.md` | 论文草稿段落 |
| `docs/research/literature/SUMMARY.md` | 文献调研总览（更新） |

## GAP支撑文档结构

每个GAP支撑文档结构如下：

```
# GAP{n}_{主题}

## GAP定义
[GAP的具体定义，引用PRINCIPLE.md]

## 文献支撑

### 强支撑（直接证明GAP声称）
| 序号 | 文献信息 | 支撑内容 | 下载链接 | 本地PDF地址 |
|-----|---------|---------|---------|------------|
| 1 | [作者, 年份, 标题, 期刊] | [具体支撑内容] | [DOI链接] | [pdfs/xxx.pdf] |

### 弱支撑（提供侧证或背景）
| 序号 | 文献信息 | 支撑内容 | 下载链接 | 本地PDF地址 |
|-----|---------|---------|---------|------------|
| 1 | [作者, 年份, 标题, 期刊] | [具体支撑内容] | [DOI链接] | [pdfs/xxx.pdf] |

## 支撑缺口（如有）
- [缺口描述]
- 缺口等级：高/中/低

## 可引用表述
[可直接写入论文的表述]

## 参考文献
[该GAP支撑涉及的文献列表，格式：作者, 年份. 标题. 期刊. DOI]
```

**注意**：每个入选GAP支撑文档的文献都必须包含下载链接（DOI或可直接访问的PDF链接）和本地PDF文件路径，便于后续离线访问原文核实。

## 流程

### A. 目录整理

- 整理根目录的临时文件和杂乱文件，保持根目录干净，符合根目录白名单

#### 根目录白名单（允许存在的文件/目录）

📄 文件	CLAUDE.md, cli.py, conftest.py, pytest.ini, README.md, README_circuit.md, requirements.txt, waveviewer.bat
📁 目录	.claude/, .git/, .loop/, .playwright-cli/, .vscode/, assets/, cache/, calibration_analyzer/, circuit_design/, docs/, ex_projects/, exam_data/, logs/, paper/, projects/, scripts/, src/, .gitignore

#### 整理规则
- 如发现违规文件，立即移动到对应目录或 `logs/temp/`（临时文件）
- 禁止在根目录创建任何新的文件，禁止污染根目录
- 禁止在根目录生成或保存 .log 文件

### B. GAP支撑文档生成

1. 读取 `docs/research/literature/verified_literature.md` 中所有文献
2. 读取 `docs/research/literature/GAP文献缺口.md` 了解当前缺口
3. 对每个GAP（GAP1-GAP11），检查是否有足够支撑：
   - 有足够支撑 → 生成完整的GAP支撑文档
   - 支撑不足 → 生成含缺口的GAP支撑文档，标记缺口等级
4. 更新 `docs/research/gap/GAP_SUMMARY.md` 总览矩阵

### C. 核心文献清单更新

- 从 `docs/research/literature/verified_literature.md` 中筛选能直接支撑GAP的文献
- 更新 `docs/research/literature/key_references.md`，按GAP分类组织：
  - 每个GAP列出2-3篇核心支撑文献
  - 标注每篇文献的支撑等级（强支撑/弱支撑）
  - **必须包含下载链接**（DOI或PDF链接）和本地PDF地址
- 只能从 `verified_literature.md` 选出候选，禁止从 `raw_literature.md` 直接提拔

### D. 论文素材提炼

从已验证文献中提炼可直接写入论文的内容：

1. **相关工作章节草稿**
   - 按GAP主题组织
   - 每段包含：方法描述、文献引用、局限性说明

2. **理论支撑表述**
   - 精确定义和公式
   - 引用来源

3. **对比方法选择依据**
   - 为什么选择这些方法对比
   - 文献支撑

4. **评估指标来源**
   - 指标的文献出处
   - 行业标准

### E. 审稿意见回应映射

根据 `docs/FRIKAN_REJECT.md` 和第二稿策略，以下审稿意见需要文献支撑：

| 审稿意见 | 需要支撑的内容 | 对应文献类型 |
|---------|--------------|-------------|
| R3-4 对比模型有限 | CNN、Transformer、RNN 在时序中的应用 | 架构对比 |
| R3-5 RVTDCNN 是否最佳 | 功率放大器线性化方法总结 | 补偿方法 |
| R3-6 数据集细节不足 | 数据集构建参考论文 | 数据集 |
| R4-1 激活函数比较 | ReLU、tanh、B-spline 对比研究 | 激活函数 |
| R4-8 计算成本分析 | 效率评估标准方法 | 效率评估 |

**注意**：PIKAN 相关（物理约束、奇对称性、正定性）已废弃，不需要为这些提供文献支撑。

## GAP支撑矩阵

更新 `docs/research/gap/GAP_SUMMARY.md`：

| GAP编号 | GAP主题 | 强支撑数 | 弱支撑数 | 缺口等级 | 核心文献 |
|---------|---------|---------|---------|---------|---------|
| GAP1 | xxx | n | n | 高/中/低 | [文献列表+链接] |
| ... | ... | ... | ... | ... | ... |

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
