# 调研报告：STEP1 Round 32（arXiv最新论文核查）

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研（第32轮）
- 覆盖范围：2026年3月下旬arXiv新论文核查
- 是否使用子代理：是（2个并行子代理）

## 检索路径

### 数据库来源
- arXiv (cs.LG, cs.AR, cs.NE, eess.SP, stat.ME, cs.CV)
- 检索时间窗口：2026-03-23 至 2026-03-28

### 关键词
- KAN, Kolmogorov-Arnold Networks
- Wiener system, Wiener process
- Frequency domain loss, spectral loss
- Sensor drift compensation
- MET measurement, electrochemical sensor

## 发现结果

### 真正新增论文（数据库中无记录）

| 序号 | 论文 | arXiv ID | 主题 | 相关度 | 处理 |
|------|------|----------|------|--------|------|
| 1 | KAN-SAs: Efficient Acceleration of KAN on Systolic Arrays | 2512.00055 | KAN硬件加速 | P2-高 | 新增 |
| 2 | MatrixKAN: Parallelized Kolmogorov-Arnold Network | 2502.07176 | KAN效率优化 | P2-高 | 新增 |
| 3 | Adaptive Active Learning for Online Reliability Prediction | 2603.09058 | Wiener过程 | P2-低 | 排除 |
| 4 | When Sensors Fail: Temporal Sequence Models for Robust PPO under Sensor Drift | 2603.04648 | 传感器漂移 | P1-中 | 新增 |

### 论文详情

#### 1. KAN-SAs (Errabii, Sentieys, Traiola 2026)
- **arXiv**: https://arxiv.org/abs/2512.00055
- **会议**: IEEE/ACM DATE 2026
- **核心**: 在脉动阵列（Systolic Array）上加速KAN推理
- **关键结果**: 100% SA利用率，50%时钟周期减少（28nm FD-SOI工艺）
- **相关性**: 高 - KAN硬件加速证据，支持LUT计算效率声称

#### 2. MatrixKAN (Coffman, Chen 2025)
- **arXiv**: https://arxiv.org/abs/2502.07176
- **核心**: 通过矩阵表示并行化B样条计算，解决KAN训练/推理慢的问题
- **关键结果**: 相比KAN提速约40倍
- **相关性**: 高 - KAN效率改进证据

#### 3. Adaptive Active Learning (Li et al. 2026)
- **arXiv**: https://arxiv.org/abs/2603.09058
- **核心**: 基于Wiener过程的卫星电子可靠性预测
- **相关性**: 低 - 领域不匹配（卫星可靠性 vs 传感器漂移补偿）

#### 4. When Sensors Fail (Vogt-Lowell et al. 2026)
- **arXiv**: https://arxiv.org/abs/2603.04648
- **会议**: ICLR 2026 CAO Workshop
- **核心**: 传感器失效下使用Transformer/SSM进行强化学习
- **相关性**: 中 - 传感器漂移在RL中的应用；提供漂移补偿的另一种思路

### 已排除论文

| 论文 | arXiv ID | 排除原因 |
|------|----------|----------|
| YOLOv10 with KAN | 2603.23037 | 计算机视觉目标检测，领域不匹配 |
| KAN-CFD (Face Forgery) | 2508.03189 | 人脸伪造检测，领域不匹配 |

### 与现有数据库重复（未新增）

以下论文虽在检索范围内，但已在数据库中：
- Symbolic-KAN (已排除 R17)
- FODEs (Guo 2025) - 已在数据库
- KANtize (Errabii 2026) - 已在数据库
- 多篇传感器漂移论文 - 已在数据库

## 待核实事项

无。所有新发现论文已通过arXiv直接获取完整信息。

## 对文档的影响

- 更新文件：
  - `docs/research/literature/20260328/STEP1_Round32_Research_Report.md` - 本报告
  - `docs/research/literature/literature_catalog.md` - 新增KAN-SAs、MatrixKAN、When Sensors Fail
  - `docs/research/literature/raw_literature.md` - 新增4条文献线索
  - `docs/research/literature/excluded_literature.md` - 新增2条排除记录

## 原始链接

- https://arxiv.org/abs/2512.00055 (KAN-SAs)
- https://arxiv.org/abs/2502.07176 (MatrixKAN)
- https://arxiv.org/abs/2603.09058 (Adaptive Active Learning)
- https://arxiv.org/abs/2603.04648 (When Sensors Fail)
- https://arxiv.org/abs/2603.23037 (YOLOv10 with KAN - 排除)
- https://arxiv.org/abs/2508.03189 (KAN-CFD - 排除)

## 调研报告索引

| 日期 | 路径 | 主要内容 |
|------|------|----------|
| 2026-03-28 | STEP1_Round31_Research_Report.md | 第31轮：最终核查轮 |
| 2026-03-28 | **STEP1_Round32_Research_Report.md** | **本报告**：arXiv最新论文 |

---

**本轮新增**: 4条文献线索（2新增/2排除），KAN硬件加速和效率优化方向获得补充。