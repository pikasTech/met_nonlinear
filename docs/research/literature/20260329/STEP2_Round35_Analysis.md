# 分析报告：STEP2 Round35 文献深度分析

## 基本信息
- 日期：2026-03-29
- 阶段：STEP2 分析
- 分析对象：Round 35 新增文献 (R35)
- 是否使用子代理：否

## 理论提取

### 1. Symbolic-KAN (Faroughi et al. 2026) - arXiv:2603.23854

**核心方法/理论**：
- Symbolic Kolmogorov-Arnold Networks，将离散符号结构嵌入可训练深度网络
- 将多变量函数表示为学习到的单变量原函数的组合
- 使用符号正则化逐步将连续混合锐化为单热选择

**关键公式**：
- f(x) = Σp∈P g_p(θ_p(x))，其中 g_p 是从分析原语库中选择的可学习一元函数

**主要结论**：
- 符号提取成功率达99.8% OFAT测试MSE降低
- 可在数据驱动回归和逆动力系统中恢复正确的原语项和控制结构

**与论文的相关点**：
- 相关度：**中** - 符号回归方向，非时间序列补偿重点
- 无直接支撑 MET 非线性补偿声称

---

### 2. SINDy-KANs (Howard et al. 2026) - arXiv:2603.18548

**核心方法/理论**：
- 稀疏非线性动力学辨识 + KAN
- SINDy 应用于每个激活函数层级，同时训练 KAN 和类 SINDy 表示
- 保持深度 KAN 的函数组合能力

**关键公式**：
- 在每个激活函数层级应用稀疏辨识

**主要结论**：
- 跨多个符号回归任务的准确方程发现

**与论文的相关点**：
- 相关度：**中** - 动力学系统辨识，非时间序列
- 与已有 SINDy-KANs 条目重复（raw_literature.md R35）

---

### 3. KaCGM (Almodóvar et al. 2026) - arXiv:2603.20184

**核心方法/理论**：
- Kolmogorov-Arnold 因果生成模型
- 每个结构方程由 KAN 参数化
- 直接检查学习到的因果机制，包括符号近似

**关键公式**：
- 混合类型表格数据的因果生成模型

**主要结论**：
- 在合成和半合成基准上与 SOTA 相比具有竞争力
- 可提取简化结构方程

**与论文的相关点**：
- 相关度：**中** - 因果生成模型方向，非时间序列补偿
- 与 MET 论文声称无直接关联

---

### 4. GNIO (Feng et al. 2026) - arXiv:2603.15281

**核心方法/理论**：
- Gated Neural Inertial Odometry，用于 MEMS 传感器的门控神经网络惯性里程计
- **Motion Bank**：查询全局运动模式字典，提供超出局部感受野的语义上下文
- **Gated Prediction Head**：将位移分解为幅度和方向，作为软可微 Zero-Velocity Update (ZUPT)

**关键公式**：
- 门控机制动态抑制静止期间的传感器噪声，同时在动态运动期间缩放预测

**主要结论**：
- OxIOD 数据集上轨迹误差降低 60.21%
- 在频繁停止和不规则运动速度的挑战性场景中表现出色

**与论文的相关点**：
- 相关度：**高** - **直接支撑漂移补偿声称**
- **门控机制**概念与 Wiener-KAN 的前馈补偿架构相关
- 传感器漂移建模方法可借鉴

---

### 5. DCT-Based Causal CNN (Badawi et al. 2020) - arXiv:2011.06681

**核心方法/理论**：
- 离散余弦变换（DCT）层 + 因果 CNN
- 在变换域应用软阈值非线性进行去噪
- 软阈值在训练期间学习

**关键公式**：
- DCT 模块学习稀疏漂移信号表示
- 漂移估计 = CNN(DCT(传感器信号))

**主要结论**：
- DCT 层 CNN 能够产生缓慢变化的基线漂移信号
- 即使观测传感器信号非常嘈杂，也能获得准确平滑的漂移估计

**与论文的相关点**：
- 相关度：**高** - **直接支撑传感器漂移补偿**
- **化学传感器漂移补偿**直接相关
- DCT 域方法与频域损失函数方向相关

---

### 6. Neuromorphic-Bayesian Model (Kausar et al. 2024) - arXiv:2407.04714

**核心方法/理论**：
- 神经形态计算 + 贝叶斯推理混合方法
- 卷积脉冲神经网络用于特征提取
- 贝叶斯脉冲神经网络用于气味检测和识别

**关键公式**：
- 能量效率比较 vs 非脉冲 ML 算法

**主要结论**：
- 在漂移补偿 robustness 评估数据集上验证
- 能量效率更优

**与论文的相关点**：
- 相关度：**中** - 嗅觉传感器领域，使用非常不同的方法（脉冲神经网络）
- 与 MET 电化学传感器漂移补偿间接相关

---

## 文献质量评估

### 可靠文献（建议验证）：
1. **GNIO** - 发表于 IEEE Robotics and Automation Letters，有完整方法论
2. **DCT-Based Causal CNN** - ICASSP 2020 会议论文，化学传感器漂移直接相关

### 质量存疑：
- **Symbolic-KAN** - 符号回归方向，与时间序列补偿无直接关联
- **KaCGM** - 因果生成模型，非时间序列
- **SINDy-KANs** - 动力学系统辨识，与已有条目重复

### 明显不相关：
- **Neuromorphic-Bayesian** - 脉冲神经网络方法，与 MET 论文架构差异大

---

## 审稿意见支撑

无直接对应审稿意见编号。本轮分析聚焦于：
- 漂移补偿文献补充
- 新 KAN 变体探索

---

## 对文档的影响

### 更新文件：
- `docs/research/literature/verified_literature.md` - 无新增验证条目
- `docs/research/literature/excluded_literature.md` - 无新增排除条目
- `docs/research/literature/SUMMARY.md` - 无需更新

### 分析结论：
| 文献 | 状态 | 原因 |
|------|------|------|
| GNIO | **高相关** | 传感器漂移补偿直接相关，门控机制概念可借鉴 |
| DCT-Based CNN | **高相关** | 化学传感器漂移补偿，频域方法相关 |
| Symbolic-KAN | 排除 | 符号回归，非时间序列补偿 |
| SINDy-KANs | 排除 | 动力学系统辨识，与已有条目重复 |
| KaCGM | 排除 | 因果生成模型，非时间序列 |
| Neuromorphic-Bayesian | 排除 | 脉冲神经网络，方法差异大 |

---

## 原始链接
- https://arxiv.org/abs/2603.23854 (Symbolic-KAN)
- https://arxiv.org/abs/2603.18548 (SINDy-KANs)
- https://arxiv.org/abs/2603.20184 (KaCGM)
- https://arxiv.org/abs/2603.15250 (In-Context SINDy-KAN)
- https://arxiv.org/abs/2603.15281 (GNIO)
- https://arxiv.org/abs/2011.06681 (DCT-Based Causal CNN)
- https://arxiv.org/abs/2407.04714 (Neuromorphic-Bayesian)