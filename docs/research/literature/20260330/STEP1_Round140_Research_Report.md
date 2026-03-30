# 调研报告：KAN时序网络新文献下载

## 基本信息
- 日期：2026-03-30
- 阶段：STEP1 调研
- 覆盖范围：KAN时间序列网络最新文献（2026年arXiv论文）
- 是否使用子代理：否

## 检索路径
- 关键词：KAN time series 2026, Kolmogorov-Arnold Networks benchmark
- 主要数据库：arXiv
- 新发现数据库：无
- 检索式：KAN time series 2026, KAN vs MLP, conditional time series generation benchmark

## 发现结果
- 新增文献线索：
  | 文献 | 类型 | 相关性 | 入口/链接 |
  |-----|------|-------|----------|
  | Gaonkar et al., 2026, KAN vs MLP | P0 | 高 | https://arxiv.org/abs/2601.10563 |
  | Lan et al., 2026, ConTSG-Bench | P1 | 中 | https://arxiv.org/abs/2603.04767 |
  | Hasan et al., 2026, HaKAN | P0 | 高 | https://arxiv.org/abs/2601.18837（已存在） |

- 入口已定位：
  - KAN vs MLP比较研究（Gaonkar 2026）- 已下载PDF并转换为Markdown
  - ConTSG-Bench条件时间序列生成基准（Lan 2026）- 已下载PDF并转换为Markdown

- 疑似重复：无
- 明确排除：无

## 本轮产出
- 下载PDF文件：
  - `docs/research/literature/pdfs/Hasan_2026_HaKAN.pdf` (580KB)
  - `docs/research/literature/pdfs/Gaonkar_2026_KAN_vs_MLP.pdf` (1.9MB)
  - `docs/research/literature/pdfs/ConTSG_2026_Bench.pdf` (7.3MB)

- 转换Markdown文件：
  - `docs/research/literature/pdfs/Hasan_2026_HaKAN.md` (57KB)
  - `docs/research/literature/pdfs/Gaonkar_2026_KAN_vs_MLP.md` (28KB)
  - `docs/research/literature/pdfs/ConTSG_2026_Bench.md` (158KB)

## 对文档的影响
- 更新了 `docs/research/literature/raw_literature.md`：添加Gaonkar KAN vs MLP和ConTSG-Bench条目
- 更新了 `docs/research/literature/literature_catalog.md`：添加New (R140)类别条目
- 是否需要更新 SUMMARY：否
- 是否需要后续 STEP2 分析：建议后续轮次分析Gaonkar KAN vs MLP论文的理论对比

## 待核实事项
- Gaonkar KAN vs MLP论文中的实验设置和基准是否适合作为论文对比方法
- ConTSG-Bench的评估框架是否可用于 Wiener-KAN 模型的评估参考

## 原始链接
- https://arxiv.org/abs/2601.18837 (HaKAN - 已存在)
- https://arxiv.org/abs/2601.10563 (KAN vs MLP)
- https://arxiv.org/abs/2603.04767 (ConTSG-Bench)
