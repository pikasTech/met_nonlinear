# 已排除文献

**状态**: STEP2 更新于 2026-03-29（第88轮）
**说明**: R88新增Bruder 2019 Koopman软体机器人排除；R74新增12个条目排除（计算机视觉、物理、医学等领域KANS论文）；R73新增5个条目排除（RepKAN, PAKAN, Nuclear Mass, Geng限流氧传感器, Zheng光学定位）；R72新增3个轻量级时序模型排除（COMET-SG1, Tiny-TSM, NanoHydra）；R70新增CKAN效率冲突证据

## 第88轮排除 (2026-03-29)

**Bruder et al. - Koopman软体机器人 (2019)** arXiv:1810.06637
- 原因: 软体机器人动力学 vs 电化学传感器漂移补偿 - 领域不匹配
- 方法: Koopman算子理论用于软体机器人系统辨识
- 决定: 排除 R88 - 领域不匹配；Iacob 2025 (Schoukens组 Koopman) 已覆盖更相关内容
- 注: Koopman理论与Wiener模型理论虽有联系但应用场景差异大

## 第37轮排除 (2026-03-29)

**Feng et al. - GNIO (2026)** arXiv:2603.15281
- 原因: IMU 惯性导航领域，惯性里程计 vs 电化学传感器漂移补偿
- 方法: 门控神经网络 + Motion Bank + ZUPT 机制
- 决定: 排除 R37 - 领域不匹配；已在 R27 验证门控机制但非电化学应用

**Liu et al. - TLIO (2020)** 10.1109/LRA.2020.3007421
- 原因: IMU 惯性导航，与电化学传感器漂移补偿不相关
- 决定: 排除 R37 - 领域不匹配

**Lu et al. - milliEgo (2020)** arXiv:2006.02266
- 原因: 毫米波雷达辅助里程计，领域不匹配
- 决定: 排除 R37 - 领域不匹配

**Zhang et al. - DIDO (2022)** arXiv:2203.03149
- 原因: 惯性四旋翼动力学，与电化学传感器漂移补偿不相关
- 决定: 排除 R37 - 领域不匹配

**Kausar et al. - Neuromorphic-Bayesian Olfaction (2024)** arXiv:2407.04714
- 原因: 嗅觉传感，神经形态贝叶斯模型，与电化学地震传感器不匹配
- 决定: 排除 R37 - 领域不匹配

**Golroudbari - TE-PINN (2024)** arXiv:2409.16214
- 原因: Transformer 增强的物理信息神经网络，非 KAN 相关
- 决定: 排除 R37 - 非直接相关

**R37 MEASUREMENT 期刊论文（约 35 篇）**
- 原因: 大部分为 MEMS 陀螺仪、加速度计、光纤传感器等领域，领域不匹配
- 典型: 高g加速度计校准、光纤应变传感器、视觉惯性标定等
- 决定: 排除 R37 - 领域不匹配；P2 背景论文已有 85+ 篇覆盖

## 第33轮排除 (2026-03-29)

**Luo et al. - KANLoc: KAN视觉定位 (2026)** arXiv:2602.06968
- 原因: 领域不匹配 - 机器人视觉里程计/行星着陆定位 vs 传感器频率响应漂移补偿
- 方法: 单目视觉定位 + KAN姿态回归；平移误差降低32%，旋转误差降低45%
- 决定: 排除 R33 - 机器人领域与MET电化学传感器漂移补偿无关

## 第32轮排除 (2026-03-28)

## 无法验证 / 未找到

**AFMAE**
- 原始文献未在文献库中找到
- 请改用 Focal Frequency Loss (Jiang et al., 2021)

**FreDF (已纠正的 R8)**
- 论文已在 arXiv:2402.02399 找到 (ICLR 2025)
- 之前被错误标记为"未找到"
- **状态**: 已移至 verified_literature.md - 直接支持 AFMAE 公式

## 超出范围 / 已排除

**Liu et al. - KAN 2.0 (2024)** arXiv:2408.10205
- 原因: 目标不同 - 科学发现导向 vs 通用机器学习
- 注: MultKAN 具有理论价值但应用方向不同
- 决定: 根据 STEP2 分析予以排除

**Tagliabue, How - Airflow-Inertial Odometry (2021)** arXiv:2105.13506
- 原因: 不同领域：机器人学 vs 化学传感

**Feng et al. - Fre-CW (2025)** arXiv:2508.08955
- 原因: 攻击导向优化 vs Wiener-KAN 补偿目标

**Basalaev et al. - CNN Wiener 地震隔离 FFT (2024)** arXiv:2410.14806
- 原因: 高度专业化领域（引力波探测器地震隔离）
- 相关性: 对 MET 非线性论文相关性较低

**Karita et al. - 语音领域 Transformer vs RNN (2019)** arXiv:1909.06317
- 原因: 比较 Transformer vs RNN，与 RNN vs CNN 比较无关
- 相关性: 根据架构范围予以排除

**时间序列Transformer论文**
- Informer, Autoformer, FEDformer, Transformers Survey, Attention Is All You Need, Efficient Transformers Survey
- 原因: 对 Wiener-KAN 比较未发现相关性
- 决定: 根据文献范围予以排除

## 冲突与注意事项

**Ali et al. - KAN vs LSTM (2025)** arXiv:2511.18613
- 注: 该论文显示 LSTM 在股票预测中优于 KAN
- 这与 Wiener-KAN 的效率声明相矛盾
- 决定: 保留在 verified_literature.md 中并附警告标识
- 谨慎使用：效率声明应聚焦于 KAN-GRU 混合模型 (Rather 2025)

**Beintema et al. - 深度编码器网络 (2020)** arXiv:2012.07697
- 注: 声称在 Wiener-Hammerstein 基准上具有"已知最低仿真误差"
- 可能与 Cruz SS-KAN 性能声明存在冲突
- 决定: 保留在 verified_literature.md 中并附注意事项标识

**Saha, Samanta - LSTM vs 1D-CNN TinyML (2026)** arXiv:2603.04860
- 注: **冲突** - 1D-CNN 使用少 35% 的 RAM、少 25% 的 Flash，比 LSTM 快 74 倍
- 这与论文中"RNN 参数少于 1D-CNN"的声明相矛盾
- 决定: 无法支持此声明；论文可能需要修改或删除此声明

**Dahal, Murad, Rahimi - CKAN Efficiency Bottlenecks (2025)** arXiv:2501.15757
- 注: **冲突** - CKANs 在小数据集（MoA, MNIST）比 CNN 慢，在大数据集（ImageNet）远不如 CNN
- 原文: "CKANs perform fair yet slower than CNNs in small size dataset...but are not nearly comparable as the dataset gets larger and more complex like the ImageNet"
- 这与"KAN 比 CNN/LSTM 更高效"的笼统声称相矛盾
- 与 Ali 2025 (LSTM > KAN)、Saha 2026 (1D-CNN > LSTM) 形成三重冲突证据链
- 决定: 排除 - 提供负面证据；效率声称必须聚焦于特定场景（边缘LUT加速、参数效率）

**Bian et al. - TinierHAR (2025)** arXiv:2507.07949
- 注: **冲突** - TinierHAR（基于 CNN）比 DeepConvLSTM（基于 RNN）参数少 43.3 倍
- 这与论文中"RNN 参数少于 1D-CNN"的声明相矛盾
- 决定: 无法支持此声明

**Ghosh, Boppu - 基于 FPGA 的 KAN 加速 (2026)** IEEE TCAS
- 注: 无法验证 - arXiv 链接返回 404，IEEE TCAS 需要付费
- 决定: 排除 - 无法获取完整内容

**ChakraVarthy et al. - ML 增强型 ECG 漂移校准 (2026)** DOI: 10.1080/00032719.2026.2618976
- 原因: 无法验证（需付费）；ECG 生物电信号漂移 vs 电化学传感器漂移
- 决定: 排除 R7 - 领域不匹配（ECG vs 电化学）
- 注: 论文声称 ML 增强校准但无法验证完整方法

**Wei, Liu - BP 神经网络用于 MEMS 加速度计漂移 (2024)** RSI 95(11), 115107
- 原因: 无法验证（需付费）；MEMS 加速度计领域
- 决定: 排除 R7 - 领域不匹配（惯性 vs 电化学）
- 注: BP 神经网络 + tent 混沌映射 + 麻雀搜索算法

**Pawase, Futane - ANN 用于 MEMS 地震传感器漂移 (2018)** IJSIS
- 原因: MEMS 地震传感器（地球物理测量），非电化学
- 决定: 排除 R7 - 领域不匹配；ANN（浅层，非深度学习）
- 注: FPAA 硬件实现；频率漂移从 3.68% 降至 0.64%

**Zhou et al. - LSTM 用于 MEMS 海底变形 (2025)** IEEE 11122349
- 原因: MEMS 海底变形监测，非电化学/e-nose
- 决定: 排除 R7 - 领域不匹配；1D-CNN-BiLSTM 混合架构

**Lee et al. - 递归加法网络 (RAN) (2017)** arXiv:1705.07393
- 原因: 不相关 - 分析 LSTM 门函数，非 CNN vs RNN 比较
- 决定: 排除 R7 - 超出架构效率分析范围

**Ang, Khosla, Riviere - 低-g MEMS 加速度计 (2007)** IEEE Sensors
- 原因: 领域不匹配 - MEMS 加速度计 vs 电化学传感器
- 决定: 排除 R8 - 不同传感器领域；方法已被更新文献超越

**Deng et al. - OpenFWI (2022)** arXiv:2111.02926
- 原因: 领域不匹配 - 地震全波形反演 vs MET 测量方法
- 决定: 排除 R8 - 不适用于 MET 传感器特性描述

**Magrini et al. - 局部地震检测 (2020)** arXiv:2008.02903
- 原因: 领域不匹配 - 地震事件检测 vs MET 测量方法
- 决定: 排除 R8 - 不同应用领域

**Hsu, Chou, Kuo - WRNN 用于 MEMS 陀螺仪 (2017)** IEEE Inertial
- 原因: 领域不匹配 - MEMS 惯性传感器 vs 电化学传感器；需付费
- 决定: 排除 R9 - 不同传感器领域；更新文献中有相关方法
- 注: Wiener 型 RNN 用于漂移建模但属于惯性领域

**Kumar, Tudu, Ghosh - 伏安传感器电子舌 (2020)** IEEE Sensors
- 原因: IEEE Xplore 需付费；无法验证详细公式
- 决定: 排除 R9 - 无法验证声明；相关性高但无法获取
- 注: 电化学传感器的 Hammerstein-Wiener 结构；若可获取应予引用

**Heng et al. - 半监督对抗域适应 CNN (2025)** Sensors B
- 原因: 无法验证论文存在；在主要学术数据库中未找到记录
- 决定: 排除 R9 - 论文可能不存在或归属错误

**Ren et al. - 电子鼻漂移补偿进展 (2024)** Sensor Review
- 原因: 无法验证论文存在；Emerald Sensor Review 2024 无匹配记录
- 决定: 排除 R9 - 无法验证声明

**Sun et al. - 电化学地震计数值研究 (2017)** IEEE
- 原因: IEEE Xplore 需付费；领域为地震而非通用电化学传感
- 决定: 排除 R9 - 无法验证；领域不匹配

**Zhou et al. - 宽带电化学地震计 (2025)** IEEE TIM
- 原因: IEEE TIM 需付费；领域为地震而非通用电化学传感
- 决定: 排除 R9 - 无法验证；领域不匹配

## 待验证（未排除）

**KAN 2.0 - Liu et al. (2024)** arXiv:2408.10205
- 状态: 已排除 - 目标不同（科学发现）
- 注: MultKAN 具有理论价值但应用方向不同

**KAN 2.0 - MultKAN 组件**
- 可能与模块化结构声明相关
- 待定：如果模块化变得相关则进一步分析

## 无法验证 / 需付费

**Li et al. - FRIKAN (MET 3D 频率响应数据集) (2025)** IEEE TIM TIM-25-06440
- 原因: 未找到 arXiv 预印本；论文已被 IEEE TIM 拒稿
- 决定: **不能作为独立第三方参考文献引用** - 因为这是作者自己的成果
- 注: FRIKAN 方法论应通过其他传感器测量论文引用 (Kumar 2020, Iqbal 2024)

**Zhou et al. - LSTM 用于 MEMS 海底变形 (2025)** IEEE 11122349
- 原因: IEEE Xplore 需付费，无法获取完整内容
- 状态: 已排除 - 无法验证声明

**Kumar, Tudu, Ghosh - 伏安传感器电子舌 (2020)** IEEE Sensors
- 原因: IEEE Xplore 需付费，无法验证详细公式
- 状态: 已排除 - 无法验证声明
- 注: 高相关性 - 电化学传感器的 Hammerstein-Wiener 结构；可能通过馆际互借获取

**Iqbal - 电化学传感器 Volterra 系统分析 (2024)** MIT DSpace
- 原因: 原始链接 (1721.1/155423) 错误 - 返回 SiPM 论文
- 正确链接: handle/1721.1/156552
- 状态: 待纠正 - Volterra 级数分析对 Wiener 模型高相关性

**Hsu, Chou, Kuo - WRNN 用于 MEMS 陀螺仪 (2017)** IEEE Inertial
- 原因: IEEE Xplore 需付费，无法验证详细公式
- 状态: 已排除 - 无法验证声明

**Ang, Khosla, Riviere - 低-g MEMS 加速度计 (2007)** IEEE Sensors
- 原因: 领域不匹配（加速度计 vs 电化学传感器）
- 状态: 已排除 - 相关性低

## 第10轮最终排除 (2026-03-28)

**ChakraVarthy et al. - ML 增强型 ECG 漂移校准 (2026)** DOI: 10.1080/00032719.2026.2618976
- 原因: 领域不匹配 - ECG 生物电信号 vs 电化学传感器漂移
- 决定: 排除 R10 - 无法支持电化学传感器声明

**Wei, Liu - BP 神经网络用于 MEMS 加速度计漂移 (2024)** RSI 95(11), 115107
- 原因: 领域不匹配 - MEMS 加速度计 vs 电化学传感器
- 决定: 排除 R10 - MEMS 惯性领域不适用于 MET 电化学测量

**Pawase, Futane - ANN 用于 MEMS 地震传感器漂移 (2018)** Int J Smart Sensing
- 原因: 领域不匹配 - MEMS 地震传感器 vs 电化学传感器
- 决定: 排除 R10 - 地球物理测量领域不适用

**Zhou et al. - LSTM 用于 MEMS 海底变形 (2025)** IEEE 11122349
- 原因: 领域不匹配（MEMS 海底 vs 电化学）+ IEEE 需付费
- 决定: 排除 R10 - 无法验证；领域不匹配

**Sinha et al. - ISFET pH 传感器温度与漂移补偿 (2020)** Microelectronics Journal
- 原因: 需付费 + Journal of Computational Electronics 内容不匹配
- 决定: 排除 R10 - 无法验证；期刊不匹配

**Khatri et al. - 水质传感器漂移补偿 ML (2021)** Springer DOI: 10.1007/s12652-020-02831-0
- 原因: 需付费 - 无法获取完整内容进行验证
- 决定: 排除 R10 - 无法验证声明

**Yamak et al. - KAN 时间序列综述 (2025)** DOI: 10.1007/s10586-025.05574-9
- 原因: DOI 返回 404 错误 - 论文可能尚未正式发表
- 决定: 排除 R10 - 无法验证；DOI 无效

**Livieris - C-KAN: 卷积 KAN (2024)** MDPI Mathematics
- 原因: MDPI 服务器返回 403 错误 - 无法访问论文
- 决定: 排除 R10 - 无法验证；访问被拒绝

**Agafonov et al. - 电化学地震计频率响应 (2015)** ResearchGate
- 原因: ResearchGate 返回 403 错误 - 无法访问
- 决定: 排除 R10 - 无法验证；访问被拒绝

## 第11轮排除 (2026-03-28)

**Gaonkar et al. - KAN vs MLP: 范式转变 (2026)** arXiv:2601.10563
- 原因: 质量存疑 - 本科院校（KLE Technological University），数据集非常小（函数逼近仅 15 行），基础实验缺乏统计严谨性
- 决定: 排除 R11 - 不能作为可靠参考文献支持

**Chen et al. - KAN-We Flow: 用于机器人操作的 KAN (2026)** arXiv:2602.01115
- 原因: 领域不匹配 - 机器人和时序动作预测 vs 传感器频率响应漂移补偿
- 决定: 排除 R11 - 应用领域与 MET 非线性论文无关

**Pérez-Bernal et al. - PINNs vs PIKANs: PINNs 快 1000 倍 (2025)** arXiv:2512.12074
- 原因: 领域不匹配 - PINNs 聚焦 PDE 反问题 vs 传感器漂移补偿；PINNs vs PIKANs 比较无关
- 决定: 排除 R11 - PINNs 聚焦研究不适用于 Wiener-KAN

## 第16轮排除 (2026-03-28)

**Shuai, Li - PIKAN: 用于电力系统的物理信息 KAN (2024)** arXiv:2408.06650
- 原因: PIKAN 在项目文档中明确标记为已停止开发
- 决定: 排除 R16 - PRINCIPLE.md 声明"禁止调研 PIKAN 相关内容（已废弃）"
- 注: PIKAN（本文）与 FRIKAN（作者自己的成果）不同

**Howard et al. - SINDy-KANs: 稀疏非线性动力学识别 (2026)** arXiv:2603.18548
- 原因: 非块结构架构 - 专注于稀疏方程发现，而非 Wiener 的线性动态+静态非线性串联结构
- 决定: 排除 R16 - 不支持 Wiener 线性→非线性架构

**Shen et al. - 基于 Lyapunov 的 KAN 自适应控制 (2025)** arXiv:2512.21437
- 原因: KAN 用于动态系统控制，非 Wiener 的线性动态+静态非线性结构
- 决定: 排除 R16 - 控制应用，非 Wiener 架构

**Zhang, Li - ASSM: 用于传感器异常的自适应状态空间 Mamba (2025)** arXiv:2503.22743
- 原因: **论文已撤回** - 不能被引用
- 决定: 排除 R16 - 撤回的论文不能被参考

**Hsu, Chou, Kuo - WRNN 用于 MEMS 陀螺仪 (2017)** IEEE Inertial
- 原因: 领域不匹配 - MEMS 惯性传感器 vs 电化学传感器；不同的物理和应用背景
- 决定: 排除 R11 - MEMS 惯性领域不适用于 MET 电化学测量

**Ang, Khosla, Riviere - 低-g MEMS 加速度计 (2007)** IEEE Sensors
- 原因: 领域不匹配 - MEMS 加速度计 vs 电化学传感器
- 决定: 排除 R11 - MEMS 惯性领域不适用于 MET 电化学测量

## 背景参考文献（非主要研究）

**Li et al. - 电化学传感器机器学习综述 (2025)** DOI: 10.1016/j.trac.2025.128XXX
- 状态: 综述文章 - 提供电化学传感器机器学习的一般背景
- 注: 不能作为原始研究引用；仅用于一般背景
- 决定: 验证为背景参考文献 R10

## 第17轮排除 (2026-03-28)

**Faroughi et al. - Symbolic-KAN (2026)** arXiv:2603.23854
- 原因: 符号回归/方程发现导向，非传感器漂移补偿
- 决定: 排除 R17 - 与 Wiener-KAN 传感器补偿架构无关

**Slote et al. - KANDy: 用于动力系统的 KAN (2026)** arXiv:2602.20413
- 原因: KAN 用于动力系统方程发现，非 Wiener 块结构架构
- 决定: 排除 R17 - 不支持 Wiener 线性→非线性结构

**Mohammed et al. - 用于船舶功率预测的 PI-KAN (2026)** arXiv:2602.22055
- 原因: 使用物理损失函数的物理信息 KAN，非 AFMAE 风格频率损失
- 决定: 排除 R17 - 不同的损失函数方法，与 AFMAE 相关性有限

## 第18轮排除 (2026-03-28)

**Liu et al. - MoFE-Time: 频域专家混合 (2025)** arXiv:2507.06502
- 原因: MoE 架构创新但未使用频域损失函数
- 方法: FTC 模块学习谐波频率，MoE 路由；时域 MSE 损失
- 决定: 排除 R18 - 不支持 AFMAE/频率损失声明

**Gong et al. - SWAN: 地震波数据集 (2026)** arXiv:2603.13645
- 原因: 领域不匹配 - 地震/地球物理数据 vs 传感器动态系统识别
- 决定: 排除 R18 - 应用领域与 MET 电化学测量无关

**Gaonkar et al. - KAN vs MLP: 范式转变 (2026)** arXiv:2601.10563
- 原因: 重复条目（第 125 行已标记为排除 R11）；与 Spotorno 发现存在冲突
- 决定: 排除 R18 - 确认重复；原始排除决定维持

## 第19轮排除 (2026-03-28)

**Ravirajan, Sundararajan - 嗅觉 LLM (2025)** arXiv:2502.07796
- 原因: 无定量漂移补偿结果；领域不匹配（化学电阻/VOC 传感器 vs MET 电化学）；使用反馈补偿架构（非前馈）
- 方法: LLM + 图神经网络 + HMC-FB 用于漂移补偿
- 关键问题: 声称漂移补偿有效但未提供定量数据
- 决定: 排除 R19 - 无法验证声明；领域不匹配

**Rubini et al. - 用于制药生产的进程信息 KAN (2025)** arXiv:2509.20349
- 原因: 与 Wiener-KAN 声明相关性低；无 LUT/量化，无频域损失，无传感器漂移内容
- 方法: 用于冻干温度预测的物理信息 KAN
- 决定: 排除 R19 - 与 MET 非线性项目关注点相关性低

## 第27轮排除 (2026-03-28)

**Alwala et al. - 差分驱动机器人智能控制 (2026)** arXiv:2603.14940
- 原因: 领域不匹配 - 机器人控制与非建模动力学 vs 传感器漂移补偿
- 决定: 排除 R27 - 与 MET 非线性论文无关

**Versano et al. - 狗死 reckon 模型 (2026)** arXiv:2603.07582
- 原因: 领域不匹配 - 动物运动建模 vs 传感器频率响应漂移补偿
- 决定: 排除 R27 - 与 MET 非线性论文无关

**Yuan et al. - QC-GAN 地震数据处理 (2026)** arXiv:2603.23984
- 原因: 领域不匹配 - 地震/地球物理数据处理 vs 传感器动态系统识别
- 决定: 排除 R27 - 应用领域与 MET 电化学测量无关

**Chen et al. - 深度学习3D地震速度反演 (2026)** arXiv:2603.17701
- 原因: 领域不匹配 - 地球物理反演 vs 传感器漂移补偿
- 决定: 排除 R27 - 与 MET 非线性论文无关

**Zhang et al. - 物理驱动GAN地震全波形反演 (2026)** arXiv:2603.14879
- 原因: 领域不匹配 - 地球物理成像 vs 传感器漂移补偿
- 决定: 排除 R27 - 与 MET 非线性论文无关

**Liu et al. - 基于扩散模型的波形反演 (2026)** arXiv:2603.22307
- 原因: 领域不匹配 - 地球物理反演方法 vs 传感器漂移补偿
- 决定: 排除 R27 - 与 MET 非线性论文无关

**Subramanian et al. - 气象预测神经缩放定律 (2026)** arXiv:2603.25687
- 原因: 领域不匹配 - 气象预测 vs 传感器漂移补偿；持续训练方法
- 决定: 排除 R27 - 与 MET 非线性论文无关

## 第32轮排除 (2026-03-28)

**Impraimakis, Vazquez, Zhou - YOLOv10 with KAN (2026)** arXiv:2603.23037
- 原因: 计算机视觉目标检测应用；KAN仅用于可解释性后处理
- 决定: 排除 R32 - 计算机视觉领域与传感器漂移补偿无关

**Zhang et al. - KAN-CFD: 人脸伪造检测 (2025)** arXiv:2508.03189
- 原因: 计算机视觉人脸伪造检测；"漂移补偿"指的是特征漂移，非传感器信号漂移
- 决定: 排除 R32 - 领域不匹配（计算机视觉 vs 传感器漂移补偿）

**Li et al. - 卫星电子可靠性Wiener过程 (2026)** arXiv:2603.09058
- 原因: Wiener过程用于卫星电子可靠性预测，非传感器动态系统建模
- 决定: 排除 R32 - 领域不匹配（可靠性工程 vs 传感器频率响应）

## 第22轮排除 (2026-03-28)

### R21 遗留条目

**Risuleo, Hjalmarsson - 非参数 Wiener 系统 (2020)** DOI: 10.1016/j.ifacol.2020.12.198
- 原因: 无法获取全文；IFAC 会议论文无公开预印本；尝试多个渠道（arXiv、ScienceDirect、KTH Diva Portal）均无法获取
- 方法: 标题推断为非参数核函数估计方法
- 决定: 排除 R22 - 闭源会议论文无法验证

**FEKAN - 特征富化 KAN (2026)** arXiv:2602.16530
- 原因: 缺乏标准化计算成本度量（FLOPs）；仅报告 "seconds per iteration"（硬件依赖）
- 方法: 特征富化层理论，定理 1-3
- 决定: 排除 R22 - 无法验证 KAN 效率主张；仅提供精度改进证据

**Han et al. - AGA-BP 电容加速度计温度漂移 (2020)** DOI: 10.1016/j.measurement.2020.108019
- 原因: 领域不匹配；研究的是 MEMS 电容式加速度计（地震监测），非电化学传感器
- 方法: AGA-BP 神经网络温度漂移建模
- 决定: 排除 R22 - MEMS 惯性传感器 vs MET 电化学传感器

### 频域损失（非相关）

**Wang et al. - DSAT-HD (2025)** arXiv:2509.24800
- 原因: 非频域损失研究；论文重点是架构设计（dual-stream），Fourier 仅作为预处理
- 方法: Hybrid Decomposition + dual-stream Transformer
- 决定: 排除 R22 - 损失函数为标准 MSE 变体

**Yao et al. - SEPI-TFPNet (2025)** arXiv:2512.11334
- 原因: 非频域损失函数；谱熵用于模型选择，非损失函数组成部分
- 方法: 谱熵先验引导深度特征融合
- 决定: 排除 R22 - 损失函数基于 MAPE

**Zhou et al. - 频域水印 (2025)** arXiv:2511.07802
- 原因: 应用导向（数据水印保护），非时序预测/损失函数研究
- 方法: 频域嵌入水印 + 水印保真度/鲁棒性损失
- 决定: 排除 R22 - 非基础研究

## 分析报告参考
- docs/research/literature/20260328/STEP2_Deep_Analysis.md（第2轮）
- docs/research/literature/20260328/STEP2_Round3_Analysis.md（第3轮）
- docs/research/literature/20260328/RNN_CNN_Efficiency_Conflict.md（第5轮）
- docs/research/literature/20260328/Somvanshi_KAN_Survey_Analysis.md（第5轮）
- docs/research/literature/20260328/Wiener_Sensor_Papers_Analysis.md（第5轮）
- docs/research/literature/20260328/KAN_LUT_Hardware_Analysis.md（第5轮）
- docs/research/literature/20260328/STEP2_Round6_Analysis.md（第6轮）
- docs/research/literature/20260328/KAN_Pending_Analysis_R7.md（第7轮）
- docs/research/literature/20260328/Wiener_Pending_Analysis_R7.md（第7轮）
- docs/research/literature/20260328/Drift_Comp_Pending_Analysis_R7.md（第7轮）
- docs/research/literature/20260328/FreqLoss_Pending_Analysis_R7.md（第7轮）
- docs/research/literature/20260328/ArchEfficiency_Pending_Analysis_R7.md（第7轮）
- docs/research/literature/20260328/STEP2_Round8_Analysis.md（第8轮）- FreDF 已纠正，传感器论文已分析
- docs/research/literature/20260328/STEP2_Round9_Analysis.md（第9轮）- 15 篇已验证，7 篇已排除，Bai TCN 重新分类
- docs/research/literature/20260328/STEP2_Round10_Analysis.md（第10轮）- 最终排除，9 篇论文已排除
- docs/research/literature/20260328/STEP2_Round11_Analysis.md（第11轮）- 9 篇已验证（KANtize, QuantKAN 等），5 篇已排除
- docs/research/literature/20260328/STEP2_Round16_Analysis.md（第16轮）- 8 篇已验证（Wang Spectral Bias, Stochastic Wiener 等），4 篇已排除（PIKAN, SINDy-KANs, Lb-KAN, ASSM 撤回）
- docs/research/literature/20260328/STEP2_Round17_Analysis.md（第17轮）- 6 篇已验证（FreST, Subich ICML, FreDN, Southworth Multilevel, Khodakarami Spectral Bias, Shi PI-GRU），3 篇已排除（Symbolic-KAN, KANDy, PI-KAN Vessel）
- docs/research/literature/20260328/STEP2_Round18_Analysis.md（第18轮）- 7 篇已验证（FIRE, HiPPO-KAN, P-KAN, Free-Knots KAN, KAN-FIF, Learning Koopman, Yin H-W GP），3 篇已排除（MoFE-Time, SWAN, Gaonkar 重复）
- docs/research/literature/20260328/STEP2_Round19_Analysis.md（第19轮）- 5 篇已验证（KAN-HAR, KFS, TSKANMixer, KANFormer, KAN+Crossformer），2 篇已排除（嗅觉 LLM, 进程信息 KAN）
- docs/research/literature/20260328/STEP2_Round21_Analysis.md（第21轮）- 6 篇已验证（SGN 11.7x, Free-RBF-KAN 2x, Hoang <100ns, Schaller AutoML, Fang 非线性利用, Hammar 分数阶 W-H），3 篇待核实
- docs/research/literature/20260328/STEP2_Round22_Analysis.md（第22轮）- 4 篇已验证（SATL, AEFIN, DCAE, Agile RL），6 篇已排除（R21 遗留 3 篇 + R22 频域损失 3 篇）
- docs/research/literature/20260328/STEP2_Round23_Analysis.md（第23轮）- 8 篇已验证（SGN, Free-RBF-KAN, Physical KAN SYNE, 高斯求和滤波器, 最优贝叶斯估计, LFR 学习增强, Taiji-2），0 待核实
- docs/research/literature/20260328/STEP2_Round24_Analysis.md（第24轮）- 7 篇已验证（Lin 电化学地震传感器, Bedon 校准, Poupry 故障诊断, Pietrenko-Dabrowska ML校准, SATL, DCAE, Dualformer）
- docs/research/literature/20260328/STEP2_Round25_Analysis.md（第25轮）- OLMA（AFMAE最强理论支撑），xCPD（频域分解），MEASUREMENT 期刊扩充（85篇目标达成）
- docs/research/literature/20260328/STEP2_Round26_Analysis.md（第26轮）- 最终确认：130+篇已验证，0篇待核实，理论框架完善
- docs/research/literature/20260328/STEP2_Round27_Analysis.md（第27轮）- GNIO 已验证（门控神经网络惯性里程计）

## STEP1调研报告索引

- docs/research/literature/20260328/STEP1_Round32_Research_Report.md（第32轮）- arXiv最新论文：4条线索（2新增/2排除）
- docs/research/literature/20260329/STEP2_Round33_Analysis.md（第33轮）- 3篇Round 33论文分析：Luo KANLoc已排除
- docs/research/literature/20260329/STEP2_Round35_Analysis.md（第35轮）- DCT-Based Causal CNN化学传感器漂移验证；Symbolic-KAN/SINDy-KANs/KaCGM排除
- docs/research/literature/20260329/STEP2_Round36_Analysis.md（第36轮）- 文献库完整性最终确认
- docs/research/literature/20260329/STEP2_Round37_Analysis.md（第37轮）- R37新增论文分析：IMU惯性导航论文排除（GNIO已验证但领域不匹配）
- docs/research/literature/20260329/STEP1_Round38_Research_Report.md（第38轮）- arXiv新论文核查：无新高相关性文献
- docs/research/literature/20260329/STEP2_Round38_Analysis.md（第38轮）- 分析确认：文献库完备

## 第72轮排除 (2026-03-29)

**Gogoi - COMET-SG1 (2026)** arXiv:2601.20772
- 原因: 非 KAN 相关 - 轻量级自回归回归器，与 Wiener-KAN 架构无直接关系
- 方法: 轻量级时序基础模型
- 决定: 排除 R72 - 低相关度

**Birkel - Tiny-TSM (2025)** arXiv:2511.19272
- 原因: 非 KAN 相关 - 轻量级时序基础模型，与 Wiener-KAN 架构无直接关系
- 方法: TinyML 时序模型
- 决定: 排除 R72 - 低相关度

**Cioflan et al. - NanoHydra (2025)** arXiv:2510.20038
- 原因: 非 KAN 相关 - 能量高效时序模型，与 Wiener-KAN 架构无直接关系
- 方法: 能量高效时序模型
- 决定: 排除 R72 - 低相关度

## 第73轮排除 (2026-03-29)

**Cheon - RepKAN: Demystifying KAN for Vision Tasks (2026)** arXiv:2603.06002
- 原因: 计算机视觉任务（图像分类），与传感器频率响应漂移补偿无关
- 方法: KAN 用于视觉任务的可解释性分析
- 决定: 排除 R73 - 应用领域与 MET 电化学传感器漂移补偿无关

**Zhang, Chen, Zhong, Deng - PAKAN: Pixel Adaptive KAN for Pansharpening (2026)** arXiv:2603.15109
- 原因: 全色锐化（图像融合）应用，与传感器漂移补偿无关
- 方法: 像素自适应 KAN 模块用于遥感图像融合
- 决定: 排除 R73 - 图像融合领域与传感器漂移补偿无关

**Lu, Shang, Du, Li, Liang - Correcting Nuclear Mass Models with Interpretable ML (2026)** arXiv:2603.15203
- 原因: 核物理领域，与传感器漂移补偿无关
- 方法: 可解释机器学习校正核质量模型
- 决定: 排除 R73 - 应用领域与传感器漂移补偿无关

**Geng, Chen, Xie, Ni - Limiting Current Calculation for Limiting Current Oxygen Sensor (2025)** DOI: 10.1016/j.measurement.2025.116665
- 原因: 传感器理论模型研究，非漂移补偿或深度学习方法
- 方法: 限流氧传感器的极限电流计算理论模型
- 决定: 排除 R73 - 纯理论研究，非漂移补偿方法

**Zheng, Mei, Yang - Sub-pixel Shift Compensation for Temperature-Induced Drift in NIR Optical Positioning (2026)** DOI: 10.1016/j.measurement.2025.119097
- 原因: 光学定位系统漂移补偿，与电化学传感器漂移补偿无关
- 方法: 温度引起的漂移的亚像素移位补偿
- 决定: 排除 R73 - 光学定位领域与电化学传感器漂移补偿无关

## 第74轮排除 (2026-03-29)

**Impraimakis, Vazquez, Zhou - YOLOv10 with KAN for Interpretable Object Detection (2026)** arXiv:2603.23037
- 原因: 计算机视觉目标检测应用，KAN仅用于可解释性后处理
- 方法: YOLOv10目标检测 + KAN可解释性分析
- 决定: 排除 R74 - 计算机视觉领域与传感器漂移补偿无关

**Dai, Yi, Wei, Zhang - Many-body Mobility Edges with KAN (2026)** arXiv:2603.21807
- 原因: 凝聚态物理领域，系统边缘态研究
- 方法: KAN用于多体系统边缘态分析
- 决定: 排除 R74 - 物理领域与传感器漂移补偿无关

**Yuan - HMAR: Hierarchical Modality-Aware Expert KAN for Medical Image Retrieval (2026)** arXiv:2603.16679
- 原因: 医学图像检索领域
- 方法: 层级模态感知专家KAN
- 决定: 排除 R74 - 医学领域与传感器漂移补偿无关

**Boledi, Bosbach, Poonoosamy - KAN Surrogate Model for Chemical Equilibria (2026)** arXiv:2603.15307
- 原因: 化学平衡领域
- 方法: KAN替代化学平衡计算
- 决定: 排除 R74 - 化学工程领域与传感器漂移补偿无关

**Sovrano et al. - In-Context Symbolic Regression for Robustness-Improved KAN (2026)** arXiv:2603.15250
- 原因: 符号回归领域，方程发现导向
- 方法: 上下文符号回归增强KAN鲁棒性
- 决定: 排除 R74 - 符号回归与Wiener-KAN架构无关

**Lu, Shang, Du, Li, Liang - Correcting Nuclear Mass Models with Interpretable ML (2026)** arXiv:2603.15203
- 原因: 核物理领域
- 方法: 可解释机器学习校正核质量模型
- 决定: 排除 R74 - 核物理领域与传感器漂移补偿无关

**Zhang, Chen, Zhong, Deng - PAKAN: Pixel Adaptive KAN Modules for Pansharpening (2026)** arXiv:2603.15109
- 原因: 遥感图像融合领域
- 方法: 像素自适应KAN模块用于全色锐化
- 决定: 排除 R74 - 图像融合领域与传感器漂移补偿无关

**Moreau et al. - Faithful Multimodal Concept Bottleneck Models with KAN (2026)** arXiv:2603.13163
- 原因: 医学领域，多模态概念瓶颈模型
- 方法: KAN用于多模态医学图像
- 决定: 排除 R74 - 医学领域与传感器漂移补偿无关

**Alikhani - DKD-KAN: Knowledge-Distilled KAN for Intrusion Detection (2026)** arXiv:2603.03486
- 原因: 网络安全入侵检测领域
- 方法: 知识蒸馏KAN用于入侵检测
- 决定: 排除 R74 - 网络安全领域与传感器漂移补偿无关

**Wakaura - Merged Amplitude Encoding for Quantum KAN (2026)** arXiv:2603.02818
- 原因: 量子计算领域
- 方法: 量子KAN振幅编码
- 决定: 排除 R74 - 量子计算领域与传感器漂移补偿无关

**Jiang et al. - TokenCom: VLM with KAN for Multimodal Token Communications (2026)** arXiv:2603.00482
- 原因: 多模态通信领域
- 方法: VLM与KAN用于多模态token通信
- 决定: 排除 R74 - 通信领域与传感器漂移补偿无关

**Self-Calibrating Neural Network for Sensor Drift Correction (2025)** N/A (IAJSE)
- 原因: 无法验证论文存在，无有效DOI或链接
- 方法: 自校准神经网络传感器漂移校正
- 决定: 排除 R74 - 无法验证

（文件结束）
