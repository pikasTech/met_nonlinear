# 调研报告：STEP1 Round 128 - KAN效率与频域损失文献补充

## 基本信息
- 日期：2026-03-30
- 阶段：STEP1 调研
- 覆盖范围：KAN效率对比、Wiener-KAN混合架构、频域损失函数、MEASUREMENT传感器补偿
- 是否使用子代理：是（并行3方向搜索）

---

## 一、检索路径

### 方向1：KAN vs LSTM/Wiener效率
- 关键词：KAN + LSTM efficiency, Wiener + KAN sensor, LUT KAN inference
- 主要数据库：arXiv, Google Scholar
- 发现：TKAN, GRU-KAN, SOH-KLSTM等混合架构证据

### 方向2：频域损失函数
- 关键词：frequency domain loss time series, FreDF, spectral loss neural network
- 主要数据库：arXiv, IEEE Xplore
- 发现：FreDF公式确认，OLMA/FIRE等频域损失对比

### 方向3：MEASUREMENT传感器非线性
- 关键词：sensor nonlinearity calibration, temperature compensation, electrochemical seismic
- 主要数据库：ScienceDirect, Google Scholar
- 发现：Lin 2020等高相关性论文

---

## 二、新增文献线索

### KAN效率对比文献（P0）

| 文献 | 年份 | 标题 | DOI/链接 | 类型 | 相关度 | 状态 |
|------|------|-------|----------|------|--------|------|
| Genet, Inzirillo | 2024 | TKAN: Temporal Kolmogorov-Arnold Networks | https://arxiv.org/abs/2405.07344 | P0 | 高 | 已验证 |
| Rather et al. | 2025 | GRU-KAN/LSTM-KAN Hybrid | https://doi.org/10.48550/arXiv.2507.13685 | P0 | 高 | 已验证 |
| Jarraya et al. | 2025 | SOH-KLSTM: KAN+LSTM Hybrid | https://doi.org/10.48550/arXiv.2509.10496 | P0 | 高 | 已验证 |
| Makinde | 2026 | T-KAN for Limit Order Book | https://arxiv.org/abs/2601.02310 | P0 | 高 | 已验证 |
| Ali et al. | 2025 | KAN vs LSTM Performance | https://doi.org/10.48550/arXiv.2511.18613 | P0 | 中 | ⚠️冲突 |

### LUT实现效率文献（P0）

| 文献 | 年份 | 标题 | DOI/链接 | 类型 | 相关度 | 状态 |
|------|------|-------|----------|------|--------|------|
| Hoang et al. | 2026 | KANELÉ: ISFPGA 2026, 2700x加速 | https://doi.org/10.48550/arXiv.2512.12850 | P0 | 高 | 已验证 |
| Kuznetsov | 2026 | LUT-KAN: 12x CPU加速 | https://doi.org/10.48550/arXiv.2601.03332 | P0 | 高 | 已验证 |
| Kuznetsov | 2026 | IoT KAN: 5000x加速 | https://doi.org/10.48550/arXiv.2601.08044 | P0 | 高 | 已验证 |
| Errabii et al. | 2026 | KANtize: 低位量化 | https://doi.org/10.48550/arXiv.2603.17230 | P0 | 高 | 已验证 |
| Shen et al. | 2026 | KAN-FIF: 94.8%参数压缩, 68.7%加速 | https://arxiv.org/abs/2602.12117 | P0 | 高 | 已验证 |

### Wiener-KAN混合架构（P0）

| 文献 | 年份 | 标题 | DOI/链接 | 类型 | 相关度 | 状态 |
|------|------|-------|----------|------|--------|------|
| Cruz et al. | 2025 | SS-KAN for Wiener-Hammerstein | https://arxiv.org/abs/2506.16392 | P0 | 高 | 已验证 |
| Bonassi et al. | 2023 | SSM = Deep Wiener | https://arxiv.org/abs/2312.06211 | P0 | 高 | 已验证 |
| Manavalan, Tronarp | 2026 | Barron-Wiener-Laguerre | https://arxiv.org/abs/2602.13098 | P0 | 高 | 已验证 |
| van Meer et al. | 2025 | Hall传感器Wiener自标定, 2.6x改善 | https://arxiv.org/abs/2505.04245 | P0 | 高 | 已验证 |

### 频域损失函数（P0）

| 文献 | 年份 | 标题 | DOI/链接 | 类型 | 相关度 | 状态 |
|------|------|-------|----------|------|--------|------|
| Wang et al. | 2025 | FreDF (ICLR 2025) | https://arxiv.org/abs/2402.02399 | P0 | 高 | 已验证 |
| Shi et al. | 2025 | OLMA: 熵减定理 | https://arxiv.org/abs/2505.11567 | P0 | 高 | 已验证 |
| He et al. | 2025 | FIRE: 统一频域框架 | https://arxiv.org/abs/2510.10145 | P0 | 高 | 已验证 |
| Wu et al. | 2025 | KFS: Parseval定理 | https://arxiv.org/abs/2508.00635 | P0 | 高 | 已验证 |

### MEASUREMENT传感器补偿（2020-2026）

| 文献 | 年份 | 标题 | DOI | 类型 | 相关度 | 状态 |
|------|------|-------|-----|------|--------|------|
| Lin et al. | 2020 | 电化学地震传感器温度幅度特性 | 10.1016/j.measurement.2020.107518 | P0 | **最高** | 已验证 |
| Han et al. | 2020 | AGA-BP神经网络温度漂移补偿 | 10.1016/j.measurement.2020.108019 | P1 | 高 | 已验证 |
| Fang et al. | 2024 | 利用非线性增强灵敏度(前馈思路) | 10.1016/j.measurement.2024.116559 | P1 | 高 | 已验证 |
| Chen, Wang | 2026 | DE-LOESS + LSTM-Transformer温补 | 10.1016/j.measurement.2026.120823 | P1 | 高 | 已验证 |

---

## 三、关键发现

### 3.1 KAN-RNN混合架构效率证据

**结论**：KAN-GRU/LSTM混合模型优于纯LSTM/GRU
- TKAN (Genet 2024): R²@12-step: TKAN=0.104 > GRU=0.018 > LSTM=-0.473
- Rather 2025 GRU-KAN: 3月预测>92%, 8月>88%
- SOH-KLSTM: KAN+LSTM结合长期依赖与非线性逼近

**⚠️ 注意**：Ali 2025显示纯KAN在股票预测中不如LSTM，说明纯KAN无效率优势，但混合架构有优势

### 3.2 LUT查表实现效率量化

| 实现 | 效率提升 | 来源 |
|------|----------|------|
| KANELÉ (ISFPGA) | 2700x | Hoang 2026 |
| IoT KAN | 5000x | Kuznetsov 2026 |
| LUT-KAN (CPU) | 12x | Kuznetsov 2026 |
| KAN-FIF | 94.8%参数↓, 68.7%速度↑ | Shen 2026 |
| KANtize | 50x BitOps↓ | Errabii 2026 |

### 3.3 Wiener-KAN理论对应

- **Bonassi 2023**: 正式证明SSM ≡ 深度Wiener（线性动力学+静态非线性）
- **Manavalan 2026**: Barron-Wiener-Laguerre完整理论框架
- **van Meer 2025**: Wiener系统用于传感器自标定，2.6x RMS误差改善

### 3.4 AFMAE公式来源

**FreDF (Wang 2025 ICLR)** - 确认公式来源：
```
L^α = α·|F(Ŷ)-F(Y)|₁ + (1-α)·MSE
```
其中F(·)=FFT, |·|₁=L1范数, α典型值0.5

---

## 四、入口已定位

1. **AFMAE公式**：FreDF (Wang 2025, ICLR) - arXiv:2402.02399
2. **Wiener-KAN等价**：Bonassi 2023 (SSM=Deep Wiener) - arXiv:2312.06211
3. **KAN效率**：TKAN, GRU-KAN, SOH-KLSTM混合架构
4. **LUT实现**：KANELÉ, LUT-KAN, KAN-FIF

---

## 五、疑似重复/已排除

| 文献 | 状态 | 原因 |
|------|------|------|
| Ali 2025 KAN vs LSTM | ⚠️冲突 | 纯KAN不如LSTM，与其他证据矛盾 |
| Symbolic-KAN | 已排除 | 与Wiener-KAN架构主张正交 |
| KAN 2.0 | 已排除 | 目标与本项目不同 |

---

## 六、GAP支撑更新

| GAP编号 | 状态 | 新增支撑文献 |
|--------|------|-------------|
| GAP2 (线性度) | 低缺口→已支撑 | Lin 2020, Fang 2024 |
| GAP3 (震级因素) | 低缺口→已支撑 | Lin 2020幅度-频率特性 |
| GAP5 (震级建模) | 低缺口→已支撑 | van Meer 2025 Wiener自标定 |
| GAP7 (利用非线性) | 强支撑 | Fang 2024前馈利用非线性 |

---

## 七、对文档的影响

### 更新的文件
- raw_literature.md：新增Round 128文献线索
- literature_catalog.md：更新调研报告索引
- GAP文献缺口.md：GAP支撑状态更新

### 关键更新
1. KAN-RNN混合架构证据链完整
2. LUT实现效率量化数据齐全
3. MEASUREMENT期刊论文扩充

---

## 八、原始链接

- TKAN: https://arxiv.org/abs/2405.07344
- GRU-KAN: https://doi.org/10.48550/arXiv.2507.13685
- KAN-FIF: https://arxiv.org/abs/2602.12117
- FreDF: https://arxiv.org/abs/2402.02399
- OLMA: https://arxiv.org/abs/2505.11567
- KANELÉ: https://doi.org/10.48550/arXiv.2512.12850
- Lin 2020: 10.1016/j.measurement.2020.107518
- Bonassi 2023: https://arxiv.org/abs/2312.06211

---

**报告生成时间**：2026-03-30
**调研轮次**：Round 128
