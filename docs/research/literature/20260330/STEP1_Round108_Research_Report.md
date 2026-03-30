# 调研报告：STEP1 Round108 (2026-03-30)

## 基本信息
- 日期：2026-03-30
- 阶段：STEP1 调研
- 覆盖范围：P0核心理论（KAN效率、Wiener模型、频域损失）+ GAP2线性度测量范围
- 是否使用子代理：是；并行维度：四个独立搜索方向

## 检索路径

### 方向1：KAN效率与LUT实现（针对GAP9）
- 关键词：KAN + efficiency + LUT, KAN + hardware + acceleration, Kolmogorov-Arnold + spline + implementation
- 主要数据库：arXiv, Google Scholar

### 方向2：Wiener模型最新进展（针对GAP4/GAP5）
- 关键词：Wiener model + nonlinear system identification, Hammerstein-Wiener + deep learning, block-structured nonlinear + sensor
- 主要数据库：arXiv, IEEE Xplore

### 方向3：传感器线性度测量范围（针对GAP2）
- 关键词：sensor linearity + measurement range, electrochemical sensor + linearity + calibration, seismic sensor + amplitude + frequency response
- 主要数据库：Measurement期刊, IEEE Sensors, Google Scholar

### 方向4：频域损失函数（针对GAP10/GAP11）
- 关键词：frequency domain loss + time series, spectral loss + neural network + training, AFMAE + adaptive frequency + loss
- 主要数据库：arXiv, IEEE Xplore, Google Scholar

## 发现结果

### 新增文献线索

#### 1. KAN效率与LUT实现（P0 - GAP9支撑）

| 文献 | 类型 | 相关度 | 入口/链接 |
|-----|------|-------|----------|
| Hoang, Gupta, Harris 2026 - KANELÉ: FPGA LUT实现 | P0 | 高 | DOI: 10.48550/arXiv.2512.12850 |
| Errabii, Sentieys, Traiola 2025 - KAN-SAs: 脉动阵列加速 | P0 | 高 | DOI: 10.48550/arXiv.2512.00055 |
| Kuznetsov 2026 - LUT-Compiled KAN边缘加速 | P0 | 高 | DOI: 10.48550/arXiv.2601.08044 |
| Yu et al. 2025 - PolyKAN: GPU高效实现 | P0 | 高 | DOI: 10.48550/arXiv.2511.14852 |
| Ou et al. 2026 - VIKIN: 可重构加速器 | P0 | 中高 | DOI: 10.48550/arXiv.2603.01165 |

**KAN效率核心发现**：
- KANELÉ: FPGA上2700x加速，与 prior KAN-FPGA方法对比
- KAN-SAs: 100%利用率，50%时钟周期减少（非递归B样条实现）
- LUT-Compiled KAN: 边缘设备5000x加速（batch 1），68x加速（batch 256）
- PolyKAN: GPU上1.2-10x推理加速，1.4-12x训练加速

#### 2. Wiener模型最新进展（P0 - GAP4/GAP5支撑）

| 文献 | 类型 | 相关度 | 入口/链接 |
|-----|------|-------|----------|
| Li et al. 2024 - DLSTM-based Wiener模型 | P0 | 高 | 10.1016/j.ymssp.2024.111386 |
| Li et al. 2024 - Hammerstein-Wiener电池应用 | P1 | 高 | Journal of Energy Storage |
| Voit, Enzner 2024 - 多核神经网络块结构模型 | P0 | 高 | DOI: 10.48550/arXiv.2412.07370 |
| Wang et al. 2024 - 半球谐振陀螺振幅-间隙比漂移建模 | P1 | 高 | Measurement期刊 |
| Xu et al. 2025 - 超低频漂移补偿（自编码器） | P1 | 高 | IEEE TIM |
| Yi et al. 2025 - 谐振陀螺幅-频耦合非线性补偿 | P1 | 高 | MDPI Actuators |

**Wiener模型核心发现**：
- Li et al. 2024: DLSTM替代Wiener结构中的线性滤波器，用于非线性系统辨识
- Wang et al. 2024: 振幅-间隙比和标量因子非线性辨识，直接支撑GAP5
- Yi et al. 2025: 幅-频耦合补偿，支撑震级因素对频漂的影响

#### 3. 传感器线性度测量范围（P2 - GAP2支撑）

| 文献 | 类型 | 相关度 | 入口/链接 |
|-----|------|-------|----------|
| Sundararajan, Naduvil 2023 - 传感器线性化（translinear电路+神经网络） | P2 | 高 | DOI: 10.3934/electsci.2023.0452 |
| Li et al. 2025 - 柔性压力传感器线性度系统性分析 | P2 | 高 | DOI: 10.1088/1361-6439/ad5c2a |
| Jafari et al. 2021 - 宽量程镍基电化学传感器 | P2 | 高 | DOI: 10.1016/j.jelechem.2021.115285 |
| Gao et al. 2025 - 宽线性度范围快速响应触觉传感器 | P2 | 高 | DOI: 10.1002/adv.202411111 |
| Filipiak, Marć 2021 - SAW振动传感器（宽频幅范围） | P2 | 中 | DOI: 10.1016/j.sna.2021.112695 |

**传感器线性度核心发现**：
- Sundararajan 2023: 分段线性化和神经网络回归扩展有效测量范围
- Li et al. 2025: 从材料和结构角度系统性分析线性度提升方法
- Jafari et al. 2021: 三条线性校准曲线扩展电化学传感器检测范围
- Filipiak 2021: SAW传感器在宽频幅范围内具有平坦幅频响应

#### 4. 频域损失函数（P0 - GAP10/GAP11支撑）

| 文献 | 类型 | 相关度 | 入口/链接 |
|-----|------|-------|----------|
| Wang et al. 2025 - FreDF (ICLR 2025) | P0 | 高 | DOI: 10.48550/arXiv.2402.02399 |
| Shi et al. 2025 - OLMA: 熵减定理 | P0 | 高 | DOI: 10.48550/arXiv.2505.11567 |
| Subich et al. 2025 - 双重惩罚效应 (ICML 2025) | P0 | 高 | DOI: 10.48550/arXiv.2501.19374 |
| He et al. 2025 - FIRE: 统一频域框架 | P1 | 高 | DOI: 10.48550/arXiv.2510.10145 |
| Wu et al. 2025 - KFS: 自适应频选KAN | P0 | 高 | DOI: 10.48550/arXiv.2508.00635 |
| Chakraborty et al. 2025 - BSP Loss | P0 | 高 | DOI: 10.48550/arXiv.2502.00472 |

**频域损失核心发现**：
- FreDF: FFT+L1损失，直接公式匹配AFMAE (L^α = α·|F(Ŷ)-F(Y)|₁ + (1-α)·MSE)
- OLMA: 熵减定理提供最强理论支撑，解释为何频域损失优于纯MAE/MSE
- Subich 2025: MSE双重惩罚效应解释MAE/MSE不足
- AFMAE优势: O(n)直接能量计算 vs 其他频域损失的O(n log n) FFT

## 待核实事项

1. **Li et al. 2024 DLSTM-Wiener**: 需确认是否可作为Wiener-KAN的对比方法引用
2. **Wang et al. 2024 振幅-间隙比**: 需确认DOI完整性和期刊信息
3. **Sundararajan 2023 translinear电路**: 电路实现与本论文神经网络方法的关系需明确
4. **PolyKAN (Yu 2025)**: 确认是否已存在于文献库中

## 排除依据

1. **KAN 2.0 (Liu 2024)**: 已被标记为"不同目标"，不重复收录
2. **CKAN (Livieris 2024)**: 已在文献库中，标记为P0中相关度
3. **TIKZ (论文格式非内容)**: 不相关

## 对文档的影响

- 更新了 `raw_literature.md`：新增约20篇文献线索
- 更新了 `literature_catalog.md`：如需要
- 是否需要更新 GAP文献缺口：否（本次搜索为补充性搜索，GAP9已有强支撑）

## 原始链接

### KAN效率
- DOI: 10.48550/arXiv.2512.12850 (KANELÉ)
- DOI: 10.48550/arXiv.2512.00055 (KAN-SAs)
- DOI: 10.48550/arXiv.2601.08044 (LUT-Compiled KAN)
- DOI: 10.48550/arXiv.2511.14852 (PolyKAN)
- DOI: 10.48550/arXiv.2603.01165 (VIKIN)

### Wiener模型
- DOI: 10.1016/j.ymssp.2024.111386 (Li DLSTM-Wiener)
- DOI: 10.48550/arXiv.2412.07370 (Voit, Enzner)
- Measurement DOI (Wang 2024 - 需补充)

### 传感器线性度
- DOI: 10.3934/electsci.2023.0452 (Sundararajan)
- DOI: 10.1088/1361-6439/ad5c2a (Li 2025)
- DOI: 10.1016/j.jelechem.2021.115285 (Jafari)
- DOI: 10.1002/adv.202411111 (Gao)
- DOI: 10.1016/j.sna.2021.112695 (Filipiak)

### 频域损失
- DOI: 10.48550/arXiv.2402.02399 (FreDF)
- DOI: 10.48550/arXiv.2505.11567 (OLMA)
- DOI: 10.48550/arXiv.2501.19374 (Subich)
- DOI: 10.48550/arXiv.2510.10145 (FIRE)
- DOI: 10.48550/arXiv.2508.00635 (KFS)
- DOI: 10.48550/arXiv.2502.00472 (BSP)
