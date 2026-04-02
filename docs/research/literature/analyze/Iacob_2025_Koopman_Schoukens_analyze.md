# Iacob_2025_Koopman_Schoukens 分析

## 论文基本信息

- **标题**: Learning Koopman Models From Data Under General Noise Conditions
- **作者**: Lucian Cristian Iacob, Máté Szécsi, Gerben Izaak Beintema, Maarten Schoukens, Roland Tóth (Eindhoven Technical University, Hungary)
- **发表时间**: 2025年
- **会议/期刊**: arXiv (submitted to editors)
- **GitHub**: https://github.com/MaartenSchoukens/deepSI

## 核心内容摘要

本文提出了一种在一般噪声条件下从输入-输出数据学习具有控制输入的非线性系统Koopman模型的新识别方法。核心贡献包括：(1) 基于状态可重构性概念的深度状态空间编码器；(2) 预测误差平方损失的有效多步射击公式；(3) 包含创新噪声项的Koopman模型结构以处理过程和测量噪声；(4) 证明了估计器的统计一致性和计算效率。实验在Wiener-Hammerstein系统、Bouc-Wen迟滞benchmark和Crazyflie 2.1纳米四旋翼飞行器上验证了方法的有效性。

## GAP 关联分析

### GAP6/GAP7: 前馈补偿利用非线性区

**批判性支持**：

- **论文做了什么**：Koopman框架通过可观测函数将非线性系统提升到高维空间，在提升空间中系统动力学是线性的。这本质上是一种"利用"非线性的方法——通过提升而非排除来处理非线性。
- **论文没有做什么**：未讨论传感器频率响应漂移补偿问题，未涉及前馈vs反馈架构对量程的限制

**方法论参考**：

- Koopman模型将非线性系统表示为"线性提升状态+非线性可观测量"的组合，这与Wiener模型"线性部分+非线性部分"的结构有概念上的相似性
- 第150-151行公式(2.6)展示提升状态 z_{k+1} = A z_k，表明提升后的动力学是线性的

### GAP8/GAP9: 频率相关补偿

**无直接支撑**：

- 论文专注于时域系统识别，使用预测误差的l2损失
- 未涉及频率域分析或频域损失函数
- FFT/IFFT仅用于数学推导，未作为计算工具

### GAP10/GAP11: AFMAE vs 其他频域损失函数

**无支撑**：

- 论文使用l2损失函数进行预测误差最小化
- 未涉及频域损失函数设计

## 关键原文摘录

> "The Koopman framework uses observable functions φ ∈ F to lift the system to a higher dimensional space with linear dynamics."（第91行）

> "the Koopman operator K : F → F associated with (2.1) is defined through: Kφ = φ ○ f"（第98行）

> "The main challenge of the Koopman framework is the selection of the observables, including their number, to obtain a suitable approximation in terms of an appropriate norm (or an exact embedding) of the nonlinear system."（第153行）

> "a linear system whose dynamics are governed by the Koopman matrix A is only equivalent in terms of behavior... if explicit nonlinear constraints are imposed on the initial condition of the lifted state"（第153行）

> "multiple-shooting formulation where, on subsections of the data, multi-step prediction errors can be calculated in parallel. This allows for efficient batch optimization of the network parameters"（第9行，摘要）

## GAP支撑结论

**GAP6/GAP7支撑评估**: 弱相关/方法论参考

**支撑内容**:
1. Koopman框架展示了通过提升函数"利用"非线性而非排除的方法论
2. 提升状态空间中的线性动力学与Wiener模型的"线性部分"概念相似
3. 非线性可观测量与Wiener模型的"非线性部分"概念相似

**局限性**:
- 领域差异：系统识别 vs 传感器频率漂移补偿
- 未涉及前馈架构设计
- 未涉及频率域处理
- 使用l2时域损失而非频域损失

**总体评估**: 可作为非线性系统提升表示的方法论参考，但与GAP6-11的直接关联较弱
