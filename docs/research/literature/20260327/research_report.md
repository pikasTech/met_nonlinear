# 调研报告：Wiener-KAN 模型文献

日期：2026-03-27
阶段：STEP1 调研

## 搜索覆盖范围
- P0：KAN 网络、Wiener 模型、频域损失
- P1：漂移补偿、架构效率
- 使用 5 个并行子代理进行搜索

## 关键发现

### KAN 论文（arXiv 已验证 ID）
1. 原始 KAN：Liu et al. - 2404.19756 (ICLR 2025)
2. TKAN：Genet and Inzirillo - 2405.07344
3. 用于时间序列的 KAN：Vaca-Rubio et al. - 2405.08790
4. PowerMLP（效率）：Qiu et al. - 2412.13571 (AAAI 2025)
5. 用于 Wiener 的状态空间 KAN：Cruz et al. - 2506.16392 (IEEE) **关键**
6. KAN 2.0：Liu et al. - 2408.10205

### Wiener 模型论文
1. 用于 Wiener-Hammerstein 的状态空间 KAN：2506.16392
2. Barron-Wiener-Laguerre：Manavalan and Tronarp - 2602.13098
3. Wiener-Hammerstein 的核设计：Xu et al. - 2505.20747

### 频域损失
1. Focal Frequency Loss：Jiang et al. - 2012.12821 (ICCV 2021)
2. TimeCF 与 SAMFre：Wang et al. - 2505.17532
3. Fre-CW：Feng et al. - 2508.08955

### 漂移补偿
1. TDACNN（气体传感器）：Zhang et al. - 2110.07509
2. 知识蒸馏 E-nose：Lin and Zhan - 2507.17071
3. 气流-惯性里程计：Tagliabue and How - 2105.13506

### 架构效率
1. CNN vs RNN NLP：Yin et al. - 1702.01923
2. 深度滤波：Xie and Zhang - 2112.12616
3. 稳定 RNN：Miller and Hardt - 1805.10369 (ICLR 2019)

## 待验证
1. AFMAE 来源（可能是自定义术语）
2. FreDF 原始论文（SAMFre 引用）
3. 用于 Wiener 的状态空间 KAN（2506.16392）- 关键论文

## 输出文件
- docs/research/literature/literature_catalog.md
- docs/research/literature/raw_literature.md
- docs/research/literature/20260327/research_report.md
