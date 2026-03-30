# 调研报告：STEP1 Round 129 - 新增文献补充与GAP最终确认

## 基本信息
- 日期：2026-03-30
- 阶段：STEP1 调研
- 覆盖范围：KAN效率实现、Wiener系统辨识、MEASUREMENT传感器补偿
- 是否使用子代理：是（并行2方向搜索）

---

## 一、检索路径

### 方向1：KAN效率与Wiener系统文献
- 关键词：KAN + Wiener + sensor + LUT + quantization + 2025-2026
- 主要数据库：arXiv, Google Scholar
- 新发现：KAN-SAs, Free-RBF-KAN, Kuang&Lin 2025, WaveNet-Volterra

### 方向2：MEASUREMENT传感器补偿
- 关键词：sensor nonlinearity compensation + temperature drift + measurement journal + 2024-2026
- 主要数据库：ScienceDirect, Google Scholar
- 新发现：Zhao 2024, Chen&Wang 2026, Wang 2026

---

## 二、新增文献线索

### KAN效率实现文献（P0）

| 文献 | 年份 | 标题 | DOI/链接 | 类型 | 相关度 | 状态 |
|------|------|-------|----------|------|--------|------|
| Errabii et al. | 2026 | KAN-SAs: KAN加速器在脉动阵列上 | https://arxiv.org/abs/2512.00055 | P0 | 高 | 新增 |
| Chiu et al. | 2026 | Free-RBF-KAN: 自适应径向基函数KAN | https://arxiv.org/abs/2601.07760 | P0 | 高 | 新增 |

**KAN-SAs核心信息**：
- 脉动阵列硬件加速器
- 100% SA利用率（vs 传统30%）
- 时钟周期减少50%
- 非递归B样条实现

**Free-RBF-KAN核心信息**：
- 首个RBF-KAN通用逼近证明
- 动态对齐激活模式的RBF形状
- 训练/推理比B样条KAN更快

### Wiener系统辨识文献（P0）

| 文献 | 年份 | 标题 | DOI/链接 | 类型 | 相关度 | 状态 |
|------|------|-------|----------|------|--------|------|
| Kuang, Lin | 2025 | 假设密度滤波与神经网络代理模型 | https://arxiv.org/abs/2511.09016 | P0 | 高 | 新增 |
| Bai et al. | 2025 | WaveNet-Volterra主动噪声控制 | https://arxiv.org/abs/2504.04450 | P1 | 高 | 新增 |

**Kuang&Lin 2025核心信息**：
- 非线性动态系统状态估计
- Wiener系统不确定性传播演示
- 神经网络的假设密度滤波/平滑

**WaveNet-Volterra核心信息**：
- 主动噪声控制中的非线性系统辨识
- 与Wiener滤波器基准比较
- 全因果方法用于实时ANC

### MEASUREMENT传感器补偿（新增）

| 文献 | 年份 | 标题 | DOI | 类型 | 相关度 | 状态 |
|------|------|-------|-----|------|--------|------|
| Zhao et al. | 2024 | 非参数非线性辨识与改进EKF | 10.1016/j.measurement.2024.114235 | P1 | 高 | 新增 |
| Chen, Wang | 2026 | DE-LOESS + LSTM-Transformer温补 | 10.1016/j.measurement.2026.120823 | P1 | 高 | 已收录 |
| Wang et al. | 2026 | MEMS陀螺仪相位误差补偿 | 10.1016/j.measurement.2026.121150 | P1 | 高 | 新增 |
| Wang et al. | 2026 | MEMS陀螺仪ZRO漂移多参数融合补偿 | 10.1016/j.measurement.2025.118892 | P1 | 高 | 已收录 |

**Zhao 2024核心信息**：
- 非参数非线性系统辨识方法
- 改进扩展卡尔曼滤波(EKF)
- 传感器非线性补偿新思路

---

## 三、关键发现

### 3.1 KAN硬件加速新进展

**KAN-SAs (Errabii 2026 DATE)**：
- 脉动阵列架构
- 非递归B样条实现
- 50%时钟周期减少
- 与KANELÉ/LUT-KAN互补

**Free-RBF-KAN (Chiu 2026)**：
- RBF替代B样条解决计算开销
- 通用逼近理论保证
- 训练/推理速度显著提升

### 3.2 Wiener系统状态估计

**Kuang & Lin 2025**：
- 将神经网络作为代理模型用于不确定性传播
- 在Wiener系统上演示
- 可用于反馈控制中的状态估计

### 3.3 主动噪声控制基准

**WaveNet-Volterra (Bai 2025)**：
- 与Wiener滤波器直接基准比较
- 因果方法用于实时应用
- 可作为传感器补偿的参考

---

## 四、GAP支撑最终确认

| GAP编号 | 主题 | 支撑状态 | 缺口等级 | 关键文献 |
|--------|------|---------|----------|----------|
| GAP1 | 电化学地震检波器频响漂移 | 已支撑 | 无 | Xu&Wang 2008, Fasmin 2017 |
| GAP2 | 线性度测量范围 | 已支撑 | 无 | MEASUREMENT期刊85+篇 |
| GAP3 | 震级因素 | 已支撑 | 无 | Lin 2020, Bensmann 2010 |
| GAP4 | 非线性建模 | 已支撑 | 无 | Wiener经典理论+Bonassi 2023 |
| GAP5 | 震级频漂建模 | 已支撑 | 无 | van Meer 2025, Fasmin 2017 |
| GAP6 | 前馈vs反馈量程 | 已支撑 | 无 | Elliott&Sutton 2002 |
| GAP7 | 利用非线性提升量程 | 强支撑 | 无 | Fang 2024, KAN-FIF |
| GAP8 | 频率相关补偿精度 | 强支撑 | 无 | FreDF, FIRE |
| GAP9 | 频率相关计算效率 | 强支撑 | 无 | KANELÉ, LUT-KAN, KAN-SAs |
| GAP10 | AFMAE vs MAE | 强支撑 | 无 | FreDF |
| GAP11 | AFMAE vs 其他频域损失 | 强支撑 | 无 | OLMA, FIRE, KFS |

---

## 五、对文档的影响

### 更新的文件
- raw_literature.md：新增Round 129文献线索
- literature_catalog.md：更新调研报告索引

### 文献库状态
- **已完成**：文献库完备，128+轮调研
- **GAP支撑**：11个GAP全部有文献支撑
- **MEASUREMENT**：85+篇（目标50篇）

---

## 六、原始链接

- KAN-SAs: https://arxiv.org/abs/2512.00055
- Free-RBF-KAN: https://arxiv.org/abs/2601.07760
- Kuang&Lin 2025: https://arxiv.org/abs/2511.09016
- WaveNet-Volterra: https://arxiv.org/abs/2504.04450
- Zhao 2024: 10.1016/j.measurement.2024.114235

---

**报告生成时间**：2026-03-30
**调研轮次**：Round 129
