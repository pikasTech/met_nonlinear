# GAP9: 频率相关补偿（计算效率）

## GAP定义

**核心声称**: 与频率相关的非线性补偿方法做比较，支撑计算效率的提升

**具体描述**: 与其他频率相关的非线性补偿方法相比，本文的 Wiener-KAN 方法在计算效率上有显著提升。KAN 的 LUT 实现和 IIR 的高效计算是主要来源。

## 支撑文献

### 1. PolyKAN (Yu et al. 2025) - GPU加速多项式KAN
- **来源**: arXiv:2511.14852
- **核心**: 首个开源GPU加速KAN运算符库
- **关键结果**: 推理加速1.2-10x，训练加速1.4-12x
- **引文**: "PolyKAN fuses the forward and backward passes of polynomial KAN layers into a concise set of optimized CUDA kernels"
- **支撑内容**: KAN的计算效率优势
- **验证状态**: 已验证 R49

### 2. lmKAN (Pozdnyakov, Schwaller 2025) - 查表多元KAN
- **来源**: arXiv:2509.07103
- **核心**: 通用drop-in替代线性层，通过可训练低维多元函数表达高维映射
- **关键结果**:
  - 推理FLOPs减少高达6.0x
  - H100吞吐量提高10x以上
- **引文**: "lmKANs reduce inference FLOPs by up to 6.0x while matching the flexibility of MLPs"
- **支撑内容**: KAN LUT实现的FLOPs减少证据
- **验证状态**: 已验证 R49

### 3. GRAU (Liu, Ullah, Kumar 2026) - 可重构激活单元
- **来源**: arXiv:2602.22352
- **核心**: 分段线性拟合 + power-of-two斜率近似用于神经网络硬件加速器
- **关键效率**: LUT消耗减少>90%
- **引文**: "GRAU reduces LUT consumption by over 90%"
- **支撑内容**: LUT硬件实现效率
- **验证状态**: 已验证 R83

### 4. BitLogic (Bührer et al. 2026) - FPGA原生LUT神经网络
- **来源**: arXiv:2602.07400
- **核心**: 完全梯度可训练的LUT计算框架
- **关键效率**: <20ns推理延迟，<0.3M逻辑门
- **引文**: "BitLogic replaces multiply-accumulate operations with differentiable LUT nodes"
- **支撑内容**: LUT替代MAC的可行性
- **验证状态**: 已验证 R83

## 文献支撑关系

| 文献 | 支撑角度 | 与GAP9的关联 |
|------|---------|--------------|
| PolyKAN | KAN GPU加速 | 计算效率 |
| lmKAN | KAN FLOPs减少6.0x | 计算效率 |
| GRAU | LUT减少90% | 硬件效率 |
| BitLogic | LUT替代MAC | 硬件效率 |

## GAP支撑评估

**支撑程度**: 较强

**已有支撑**:
- PolyKAN、lmKAN提供KAN计算效率证据
- GRAU、BitLogic提供LUT硬件实现证据

**缺口**:
- 缺乏与其他频率相关补偿方法的直接效率对比

**下一步**:
- 在论文实验中添加计算效率对比
