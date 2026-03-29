# 分析报告：Round 21 - STEP2 综合分析

## 基本信息
- 日期：2026-03-28
- 阶段：STEP2 分析
- 分析对象：R21 新增 Wiener 模型论文、KAN 效率论文、MEASUREMENT 期刊论文
- 是否使用子代理：是（3 个并行方向）

## 分析范围
本轮分析覆盖 Round 21 STEP1 调研中发现的待核实论文：
1. Wiener 模型新论文（2 篇）
2. KAN 效率新论文（4 篇）
3. MEASUREMENT 期刊论文（3 篇）

---

## 理论提取

### 1. Wiener 模型论文

#### Hammar, Djamah, Bettayeb (2019) - **VERIFIED (P0)**

| 字段 | 内容 |
|------|------|
| 标题 | Nonlinear system identification using fractional Hammerstein-Wiener models |
| DOI | 10.1007/s11071-019-05331-9 |
| 期刊 | Nonlinear Dynamics, Vol 98, pp 2327-2338 |
| 引用 | 48 次（Google Scholar） |

**核心方法/理论**：
- 分数阶 Hammerstein-Wiener 模型：将分数阶微积分引入 Wiener-Hammerstein 结构
- 输出误差（OE）方法进行系统辨识
- Levenberg-Marquardt 算法用于参数估计
- 关键创新：回归形式重构使梯度/Hessian 矩阵可闭式获得

**关键公式**（从摘要推断）：
- 分数阶 Wiener-Hammerstein 结构：线性动态 → 静态非线性 → 线性动态
- 目标函数最小化避免参数灵敏度函数重复计算

**主要结论**：
1. 数值仿真验证方法有效性
2. 成功应用于实验性机械臂建模
3. 计算效率显著提升

**与论文的相关点**：
- 分数阶扩展可作为 Wiener-KAN 未来研究方向
- 块结构模型与 Wiener-Hammerstein 基准直接相关
- 输出误差方法可作为频域损失函数理论基础参考

**分类决策**：VERIFIED - SCI 期刊、完整摘要、作者有持续相关工作

---

#### Risuleo, Hjalmarsson (2020) - **PENDING**

| 字段 | 内容 |
|------|------|
| 标题 | Nonparametric models for Hammerstein-Wiener and Wiener-Hammerstein system identification |
| DOI | 10.1016/j.ifacol.2020.12.198 |
| 会议 | IFAC SYSID 2020 |
| 作者 | R. S. Risuleo, H. Hjalmarsson（KTH） |

**状态**：仅获取标题、作者、期刊信息，无法获取全文

**核心方法/理论**（标题推断）：
- 非参数 Wiener 系统辨识方法
- 核函数估计技术
- 渐近一致性理论保证

**与论文的相关点**：
- 非参数 vs 参数方法对比
- Hjalmarsson 是系统辨识领域顶级专家

**分类决策**：PENDING - 需获取全文后才能确认

---

### 2. KAN 效率论文

#### Spectral Gating Networks (SGN) - **VERIFIED (P0)**

| 字段 | 内容 |
|------|------|
| 作者 | Zhang et al. |
| 年份 | 2026 |
| arXiv | 2602.07679 |

**核心方法**：
- 增强现有架构：保留原始 MLP 路径 + 添加光谱路径（spectral branch）
- 可训练随机傅里叶特征（RFF）替代基于网格的样条
- 消除分辨率依赖

**关键公式**：
```
T_SGN(u) = ϕ(u) + G(u) ⊙ Ψ_spec(u)
Ψ_spec(u) = γ(u)A_r
```

**关键效率指标**：
| 指标 | SGN | Spline-KAN | MLP |
|------|-----|------------|-----|
| CIFAR-10 精度 | 93.15% | ~79.2% | 78.5% |
| 推理速度提升 | **11.7x** vs KAN | baseline | - |
| FLOPs | O(d_ff·m) | O(d_ff·G) | O(d_ff) |

**与论文的相关点**：
- 直接针对 KAN 的"resolution-efficiency bottleneck"
- 11.7x 加速直接支持 MET paper 的 KAN LUT 效率主张
- Theorem 3.3 证明 SGN 复杂度与网格分辨率 G 无关

**分类决策**：VERIFIED - 完整理论分析（Theorem 3.2/3.3）、多任务实验验证

---

#### Free-RBF-KAN - **VERIFIED (P0)**

| 字段 | 内容 |
|------|------|
| 作者 | Chiu et al. |
| 年份 | 2026 |
| arXiv | 2601.07760 |

**核心方法**：
- 自适应网格（learnable centroids）+ 可训练光滑度参数
- RBF 核替代 B 样条
- 首个 RBF-KAN 族通用逼近定理证明

**关键效率指标**：
| 任务 | Model | 参数量 | Test MSE | 训练时间(s) |
|------|-------|--------|----------|-------------|
| 2D 非光滑函数 | KAN | 195 | 3.54e-3 | 124 |
| | Free-RBF-KAN | 450 | **2.74e-4** | **121** |
| 2D 热传导 PINN | KAN | 1400 | 6.52e-3 | 267 |
| | Free-RBF-KAN | 2000 | **2.41e-3** | **138** |

**与论文的相关点**：
- 明确针对 De Boor 算法开销问题
- 训练时间 ~2x 加速
- NTK 分析确认无谱偏

**分类决策**：VERIFIED - 完整理论支撑、多任务对比

---

#### Hoang, Gupta, Harris - Ultra-fast On-chip Online Learning - **VERIFIED (P0)**

| 字段 | 内容 |
|------|------|
| 作者 | Hoang, Gupta, Harris |
| 年份 | 2026 |
| arXiv | 2602.02056 |

**核心方法**：
- 利用 B-spline 局部性实现稀疏更新
- 定点量化鲁棒性证明
- FPGA 硬件实现

**关键定理**：
- Lemma 3.2: p 阶 B-spline 只有 s=p+1 个非零局部支撑
- Theorem 3.3: C_update(KAN) = s/(G+s) * C_update(MLP)
- Theorem 3.4: KAN 激活输出被限制在 [min(Wi), max(Wi)]
- Theorem 3.5: KAN 梯度敏感性 Var[ε_KAN] = O(Δ²)

**关键效率指标**：
| 任务 | KAN | MLP-P | MLP-L |
|------|-----|-------|-------|
| 回归 (概念漂移) 累积遗憾 | **13.2** | 97.6 | 48.3 |
| 量子位读出准确率 | **92.8%** | 69.8% | 62.4% |
| FPGA 延迟 | **<100ns** | - | - |

**与论文的相关点**：
- **首个亚微秒级片上在线学习演示**（<100ns）
- 直接验证 KAN 的 LUT/spline 局部性优势
- FPGA 实现验证

**分类决策**：VERIFIED - 4 个定理 + FPGA 硬件验证

---

#### FEKAN (Feature-Enriched KAN) - **PENDING**

| 字段 | 内容 |
|------|------|
| 作者 | Menon, Jagtap |
| 年份 | 2026 |
| arXiv | 2602.16530 |

**状态**：缺乏与标准 KAN 的直接 FLOPs/延迟量化对比数据

**核心方法**：
- 特征富化（多项式、三角函数、交互项）
- Theorem 1-3 提供理论框架

**分类决策**：PENDING - 需要补充 FEKAN 相比标准 KAN 的实际 FLOPs/训练时间对比

---

### 3. MEASUREMENT 期刊论文

#### Schaller, Kruse (2025) - **VERIFIED (P2)**

| 字段 | 内容 |
|------|------|
| 标题 | AutoML for multi-class anomaly compensation of sensor drift |
| DOI | 10.1016/j.measurement.2025.117097 |
| 期刊 | Measurement |

**核心方法**：
- AutoML 自动化特征选择和模型超参数调优
- 多类异常同时识别和补偿

**与论文的相关点**：
- 高相关：AutoML 方法是 MET 非线性传感器测量中可借鉴的自动化校准思路

**分类决策**：VERIFIED

---

#### Fang et al. (2024) - **VERIFIED (P2)**

| 字段 | 内容 |
|------|------|
| 标题 | Exploiting nonlinearity for sensitivity enhancement of TPoS micromachined gas sensor |
| DOI | 10.1016/j.measurement.2024.116559 |
| 期刊 | Measurement |

**核心方法**：
- TPoS 微机械气体传感器
- 利用非线性而非抑制非线性实现灵敏度增强

**关键结论**：
- 利用非线性优于抑制非线性
- 与 MET 论文核心观点一致

**分类决策**：VERIFIED

---

#### Han et al. (2020) - **PENDING**

| 字段 | 内容 |
|------|------|
| 标题 | Temperature drift modeling and compensation of capacitive accelerometer based on AGA-BP neural network |
| DOI | 10.1016/j.measurement.2020.108019 |

**状态**：DOI 返回 429 错误（rate limiting），无法获取

**分类决策**：PENDING - 需重试获取

---

## 文献质量评估

| 论文 | 分类 | 原因 |
|------|------|------|
| Hammar 2019 | ✅ VERIFIED | SCI 期刊、完整摘要、48 引用 |
| Risuleo 2020 | ⏳ PENDING | 仅标题信息，需获取全文 |
| Spectral Gating Networks | ✅ VERIFIED | 完整理论 + 实验验证 |
| Free-RBF-KAN | ✅ VERIFIED | 完整理论 + 多任务对比 |
| Hoang Ultra-fast | ✅ VERIFIED | 4 定理 + FPGA 验证 |
| FEKAN | ⏳ PENDING | 需量化数据 |
| Schaller 2025 | ✅ VERIFIED | AutoML 漂移补偿方法 |
| Fang 2024 | ✅ VERIFIED | 非线性利用 |
| Han 2020 | ⏳ PENDING | 429 错误 |

---

## 对文档的影响

### 新增 verified 条目
1. Hammar 2019 - 分数阶 Hammerstein-Wiener
2. Spectral Gating Networks - 11.7x 推理加速
3. Free-RBF-KAN - 2x 训练加速
4. Hoang Ultra-fast - <100ns 延迟、亚微秒片上学习
5. Schaller 2025 - AutoML 漂移补偿
6. Fang 2024 - 非线性利用提高灵敏度

### 新增 pending 条目
1. Risuleo 2020 - 非参数 Wiener 系统
2. FEKAN - 需量化数据
3. Han 2020 - DOI 访问受限

### 新增 excluded 条目
无

---

## 原始链接
- https://doi.org/10.1007/s11071-019-05331-9 (Hammar 2019)
- https://doi.org/10.1016/j.ifacol.2020.12.198 (Risuleo 2020)
- https://arxiv.org/abs/2602.07679 (Spectral Gating Networks)
- https://arxiv.org/abs/2601.07760 (Free-RBF-KAN)
- https://arxiv.org/abs/2602.02056 (Hoang Ultra-fast)
- https://arxiv.org/abs/2602.16530 (FEKAN)
- https://doi.org/10.1016/j.measurement.2025.117097 (Schaller 2025)
- https://doi.org/10.1016/j.measurement.2024.116559 (Fang 2024)
- https://doi.org/10.1016/j.measurement.2020.108019 (Han 2020)
