# 调研报告：文献调研第27轮 - 2026年3月新论文核查

## 基本信息
- 日期：2026-03-28
- 阶段：STEP1 调研（第27轮）
- 覆盖范围：2026年3月arXiv新提交论文核查
- 是否使用子代理：是（3个并行子代理）

## 检索路径

### 子代理任务分配
1. **KAN/Wiener 2026年3月论文** - 搜索KAN网络、Wiener模型新论文
2. **频域损失函数论文** - 搜索频率域损失函数新论文
3. **传感器补偿论文** - 搜索传感器非线性/漂移补偿新论文

### 主要数据库
- arXiv (2026年3月提交)
- Google Scholar

## 发现结果

### 1. KAN网络新论文（2026年3月）

| 状态 | 标题 | 作者 | 年份 | 出版物 | 链接 | 相关性 |
|------|------|------|------|--------|------|--------|
| **新增** | KAN-FIF: Spline-Parameterized Lightweight Physics-based Tropical Cyclone Estimation | Shen et al. | 2026 | arXiv | https://arxiv.org/abs/2602.12117v2 | High |

**KAN-FIF核心信息**：
- 集成MLP/CNN与spline参数化KAN层
- 气象卫星传感器建模应用
- **94.8%参数 reduction** (0.99MB vs 19MB)
- **68.7%推理速度提升** (2.3ms vs 7.35ms)
- **32.5%更低的MAE**
- 边缘设备部署，14.41ms/样本延迟
- **更新日期：2026年3月14日**

### 2. 传感器漂移补偿新论文（2026年3月）

| 状态 | 标题 | 作者 | 年份 | 出版物 | 链接 | 相关性 |
|------|------|------|------|--------|------|--------|
| **新增** | GNIO: Gated Neural Inertial Odometry | Feng et al. | 2026 | arXiv | https://arxiv.org/abs/2603.15281 | High |
| **新增** | Intelligent Control of Differential Drive Robots with Unmodeled Dynamics | Alwala et al. | 2026 | arXiv | https://arxiv.org/abs/2603.14940 | Medium-High |
| **新增** | Model-Based and Neural-Aided Approaches for Dog Dead Reckoning | Versano et al. | 2026 | arXiv | https://arxiv.org/abs/2603.07582 | Medium |

**GNIO核心信息**：
- 门控神经网络显式建模运动有效性和上下文
- 解决IMU快速漂移问题
- 引入Motion Bank进行全局运动模式查询
- 门控预测头将位移分解为幅度和方向
- **60.21%轨迹误差降低**
- 直接涉及传感器漂移补偿的神经网络方法

### 3. 地震信号处理新论文（2026年3月）

| 状态 | 标题 | 作者 | 年份 | 出版物 | 链接 | 相关性 |
|------|------|------|------|--------|------|--------|
| **新增** | QC-GAN: Quantum-Classical Synergistic Paradigm for Seismic Data Processing | Yuan et al. | 2026 | arXiv | https://arxiv.org/abs/2603.23984 | High |
| **新增** | Deep Learning-Based 3D Seismic Velocity Inversion | Chen et al. | 2026 | arXiv | https://arxiv.org/abs/2603.17701 | High |
| **新增** | Physics-driven GAN for Seismic Full-Waveform Inversion | Zhang et al. | 2026 | arXiv | https://arxiv.org/abs/2603.14879 | High |
| **新增** | Full Waveform Inversion based on Diffusion Model | Liu et al. | 2026 | arXiv | https://arxiv.org/abs/2603.22307 | Medium-High |

### 4. 频域损失函数新论文（2026年3月）

| 状态 | 标题 | 作者 | 年份 | 出版物 | 链接 | 相关性 |
|------|------|------|------|--------|------|--------|
| 待核实 | Neural Scaling Laws for Weather Emulation through Continual Training | Subramanian et al. | 2026 | arXiv | https://arxiv.org/abs/2603.25687 | Medium |

**说明**：该论文主要关于天气预报中的持续训练神经缩放定律，仅附带提到spectral loss调整，非频域损失函数核心论文。

## 待核实事项

1. **KAN-FIF (2602.12117v2)** - 需确认是否与现有SKANODEs (arXiv:2506.18339)存在重复
2. **GNIO (2603.15281)** - IMU漂移补偿方法与论文MET传感器应用的相关性需评估
3. **地震信号处理论文** - 评估与地震计传感器建模的直接相关性

## 对文档的影响

- 更新文件：`literature_catalog.md`（添加第27轮报告索引）
- 更新文件：`raw_literature.md`（添加新发现论文）
- 本轮发现7篇新论文，优先级排序如下：
  - **高优先级**：KAN-FIF, GNIO, QC-GAN
  - **中优先级**：其他地震/传感器论文

## 原始链接

- KAN-FIF: https://arxiv.org/abs/2602.12117v2
- GNIO: https://arxiv.org/abs/2603.15281
- QC-GAN: https://arxiv.org/abs/2603.23984
- Deep Learning 3D Seismic: https://arxiv.org/abs/2603.17701
- Physics-driven GAN: https://arxiv.org/abs/2603.14879
- Diffusion Model FWI: https://arxiv.org/abs/2603.22307
- Neural Scaling Laws: https://arxiv.org/abs/2603.25687
