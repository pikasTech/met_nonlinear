# 调研报告：STEP1 系统性文献线索收集（第三轮）

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研
- 覆盖范围：Wiener模型经典理论、LUT-based KAN实现、KAN-GRU混合架构验证、KANet FLOPs论文、KAN综述论文
- 是否使用子代理：是；并行5方向检索

---

## 检索路径

### 并行子代理任务分配
| 子代理 | 检索方向 | 主要数据库 | 关键词 |
|--------|----------|-----------|--------|
| 子代理1 | LUT-based KAN实现 | arXiv, IEEE Xplore | KAN LUT, KAN lookup table, KAN hardware, KAN efficient inference |
| 子代理2 | Wiener模型经典理论 | IEEE Xplore, ScienceDirect, Google Scholar | Wiener system identification, Wiener-Hammerstein benchmark |
| 子代理3 | KAN-GRU混合架构验证 | arXiv, IEEE Xplore | KAN-GRU, KAN-LSTM hybrid, Rather 2025 |
| 子代理4 | KANet FLOPs论文 | IEEE Xplore, arXiv | KANet, KAN FLOPs, KAN computation cost |
| 子代理5 | KAN时序综述论文 | arXiv, Springer, ACM | KAN survey, KAN review, time series |

---

## 发现结果

### 新增文献线索汇总

#### P0 Wiener模型经典理论

| 作者 | 年份 | 标题 | DOI/URL | 相关性 | 状态 |
|------|------|------|---------|--------|------|
| Schoukens, Ljung | 2009 | Wiener-Hammerstein Benchmark | https://www.diva-portal.org/smash/get/diva2:317004/FULLTEXT01.pdf | **HIGH** | 待核实 |
| Haber, Unbehauen | 1990 | Structure identification of nonlinear dynamic systems—A survey | 10.1016/0005-1098(90)90044-I | **HIGH** | 待核实 |
| Greblicki | 2002 | Nonparametric approach to Wiener system identification | 10.1109/81.983126 | Medium | 待核实 |
| Bai, Giri | 2010 | Introduction to Block-oriented Nonlinear Systems | 10.1007/978-1-84996-513-2_1 | **HIGH** | 待核实 |
| Li et al. | 2024 | LSTM-based Wiener model identification | 10.1016/j.ymssp.2024.111386 | Medium | 待核实 |
| Van Mulders et al. | 2013 | Identification of systems with localised nonlinearity | 10.1016/j.automatica.2013.02.006 | **HIGH** | 待核实 |

#### P0 LUT-based KAN实现

| 作者 | 年份 | 标题 | DOI/URL | 关键发现 | 状态 |
|------|------|------|---------|----------|------|
| Liu et al. | 2024 | KAN: Kolmogorov-Arnold Networks | 10.48550/arXiv.2404.19756 | B-spline on edges = O(1) LUT lookup per activation | 已定位 |
| Qiu et al. | 2024 | PowerMLP: Efficient KAN | 10.48550/arXiv.2412.13571 | KAN 10x slower than MLP; KAN FLOPs >10x PowerMLP | 已核实 |
| Lee et al. | 2024 | HiPPO-KAN | 10.48550/arXiv:2410.14939 | Constant parameter count regardless of window size | 已定位 |

**重要发现：未找到专门的KAN硬件LUT实现论文（FPGA/ASIC）**

#### P0 KAN-GRU混合架构验证 (Rather et al. 2025)

| 作者 | 年份 | 标题 | DOI/URL | 关键发现 | 状态 |
|------|------|------|---------|----------|------|
| Rather et al. | 2025 | Kolmogorov-Arnold Networks-based GRU and LSTM for Loan Default Early Prediction | 10.48550/arXiv.2507.13685 | GRU-KAN和LSTM-KAN混合优于纯LSTM/GRU | **已核实** |

**关键发现：该论文不包含FLOPs或参数量对比，仅关注精度指标**

#### P0 KANet FLOPs论文

| 作者 | 年份 | 标题 | DOI/URL | 关键发现 | 状态 |
|------|------|------|---------|----------|------|
| Pu, Li, Zhou | 2025 | KANet: Memory-Managed Recurrent Kolmogorov-Arnold Network for Indoor Inertial Navigation | 10.1109/TIM.2025.xxxxxx (IEEE TIM) | 声称比LSTM有更低的参数量，包含FLOPs测量 | **待核实** |

**备注：IEEE TIM付费论文，无法获取完整数据**

#### P0 KAN综述论文

| 作者 | 年份 | 标题 | DOI/URL | 关键发现 | 状态 |
|------|------|------|---------|----------|------|
| Yamak et al. | 2025 | KAN for time series forecasting: a comprehensive review | 10.1007/s10586-025-05574-9 | Springer付费，需要订阅 | **待核实** |
| Somvanshi et al. | 2025 | A Survey on Kolmogorov-Arnold Network | 10.1145/3743128 / arXiv:2411.06078 | ACM Computing Surveys, 208 citations | **待核实** |

#### P1 KAN+RNN混合相关论文

| 作者 | 年份 | 标题 | DOI/URL | 关键发现 | 状态 |
|------|------|------|---------|----------|------|
| Genet, Inzirillo | 2024 | TKAN: Temporal KAN | 10.48550/arXiv.2405.07344 | TKAN > GRU > LSTM | 已定位 |
| Huang et al. | 2025 | TimeKAN | arXiv:2502.06910 | KAN-based frequency decomposition | 已定位 |
| Kui et al. | 2025 | TFKAN: Time-Frequency KAN | arXiv:2506.12696 | Long-term forecasting | 已定位 |
| Livieris | 2024 | C-KAN: Convolutional KAN | MDPI Mathematics | CNN+KAN multistep predictions | 已定位 |

---

## 待核实事项

1. **KANet完整FLOPs数据** - IEEE TIM付费论文，需机构访问权限获取完整数据
2. **Yamak KAN时序综述** - Springer订阅全文
3. **Schoukens & Ljung Wiener-Hammerstein Benchmark** - PDF可直接下载（diva-portal）
4. **Haber & Unbehauen 1990结构识别综述** - 999+引用，经典文献

---

## 排除依据

1. **KAN专用硬件LUT实现** - 搜索未发现FPGA/ASIC相关论文
2. **KANet完整数据** - 付费论文，数据无法获取
3. **AFMAE原始论文** - 仍未找到

---

## 对文档的影响

- 更新文件：
  - `raw_literature.md` - 新增本轮发现的文献线索
  - `literature_catalog.md` - 新增Survey Report Index条目
  - `docs/research/literature/20260328/STEP1_Round3_research_report.md` - 本调研报告
- 是否需要更新SUMMARY：否（STEP1不更新SUMMARY）
- 是否需要后续STEP2分析：是

---

## 原始链接

### Wiener模型经典理论
- https://www.diva-portal.org/smash/get/diva2:317004/FULLTEXT01.pdf (Schoukens & Ljung 2009)
- https://doi.org/10.1016/0005-1098(90)90044-I (Haber & Unbehauen 1990)
- https://doi.org/10.1109/81.983126 (Greblicki 2002)
- https://doi.org/10.1007/978-1-84996-513-2_1 (Bai & Giri 2010)
- https://doi.org/10.1016/j.automatica.2013.02.006 (Van Mulders 2013)
- https://doi.org/10.1016/j.ymssp.2024.111386 (Li et al. 2024)

### LUT-based KAN
- https://doi.org/10.48550/arXiv.2404.19756 (Liu et al. 2024 - KAN original)
- https://doi.org/10.48550/arXiv.2412.13571 (Qiu et al. 2024 - PowerMLP)
- https://doi.org/10.48550/arXiv:2410.14939 (Lee et al. 2024 - HiPPO-KAN)

### KAN-GRU混合架构
- https://doi.org/10.48550/arXiv.2507.13685 (Rather et al. 2025)

### KANet
- https://ieeexplore.ieee.org/abstract/document/10816574/ (Pu, Li, Zhou - IEEE TIM 2025)

### KAN综述
- https://doi.org/10.1007/s10586-025-05574-9 (Yamak et al. 2025 - Springer)
- https://doi.org/10.1145/3743128 (Somvanshi et al. 2025 - ACM)
- https://arxiv.org/abs/2411.06078 (Somvanshi arXiv版本)

### 其他K AN+RNN混合
- https://doi.org/10.48550/arXiv.2405.07344 (Genet & Inzirillo - TKAN)
- https://arxiv.org/abs/2502.06910 (Huang et al. - TimeKAN)
- https://arxiv.org/abs/2506.12696 (Kui et al. - TFKAN)
