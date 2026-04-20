# 模拟电路实现与 SPICE 验证

## 功能概述

本项目的电路实现路线，不是把任意神经网络直接硬搬到模拟电路里，而是优先保留可解释的线性前端，再把剩余可训练部分映射到更容易落地的模拟模块。

这份文档用于收敛长期稳定的工程规则：

- 当前更可行的模拟实现主线是什么
- TF、NumPy、SPICE 之间如何做逐层对应验证
- 电阻映射、激活函数和偏置处理的主要风险点是什么
- 哪些命令、目录和产物构成当前的电路验证闭环

## 当前代码与目录入口

与模拟电路实现直接相关的主路径如下：

- `src/spice_simulator/`：SPICE 网表生成、器件模型、仿真和电阻/BOM 工具
- `src/visualization/wnet5_circuit_validator.py`：WNET5 / SVF 电路验证与频响对比
- `src/inference/`：推理后端，包含 `spice_backend` 在内的多后端入口
- `src/calibration_analyzer/`：时域数据结构、波形分析和频响重建基础能力
- `ex_projects/wnet5-circuit-validation/`：WNET5 分层电路验证模板与产物目录

CLI 侧直接相关的入口主要有：

- `python cli.py -r PROJECT_NAME`：导出电阻表与 BOM 前数据
- `python cli.py -s PROJECT_NAME`：对已有电阻表做标准化系列映射
- `python cli.py -i PROJECT_NAME`：通过不同推理后端做逐层或整模型推理
- `python cli.py ep "ex_projects/wnet5-circuit-validation/layerN"`：生成 WNET5 分层电路验证产物

## project 级模拟配置入口

`projects/<PROJECT>/config.json` 中的 `inference_config`，是当前 project 级模拟实现配置的正式入口；它负责描述模型落到 SPICE / 电路验证时需要遵守的模拟侧约束，而不是训练数据定义或运行产物路径。

当前已经稳定下来的配置族主要包括：

- `power_supply`：电源轨约束，例如 `vcc` / `vee`
- `opamp_config`：运放模型、include 文件与供电脚配置
- `high_pass_config`：高通与工作点补偿网络；它属于可选硬件补偿，不是默认理论基线
- `bias_compensation`：分层 / 分通道偏置修正，长期以 `layer_bias_adjustments` 这类结构化配置表达；历史 `bias_adjustment_matrix` 只作为旧资料名词理解，不再作为正式配置字段
- `bom_config`：与电阻 / BOM 导出直接相关的 project 级选项，当前也归在 `inference_config` 下统一管理

长期边界应这样理解：

- project 的数据定义写在 `dataset` 等训练侧配置里
- project 的模拟实现约束写在 `inference_config` 里
- SPICE 网表、wave 和验证产物仍落在 project 的 `data/` 子树；网表目录的具体落点与推理输出规则，详见 [inference.md](inference.md)

## 当前更可行的实现主线

从 NOTEBOOK_CIRCUIT 的长期收敛看，当前更可行的路线不是“先做 CNN/FIR 到 RNN/IIR 的直接变换”，而是：

- 用固定或半固定的线性前端承担极点与频段特征提取
- 把可训练自由度更多放在零点、加权和非线性部分
- 通过逐层 SPICE 验证保证每一级转换都可解释、可对齐

换句话说，当前优先方向更接近：

- `SVF / SOS / IIR` 作为模拟可实现的线性特征前端
- `Dense / gate / activation` 作为剩余可训练或可调部分

而不是默认尝试：

- 直接训练纯线性 RNN 再硬件化
- 直接把 CNN/FIR 完整转换为 RNN/IIR 并假设相位与增益都能自然保真

## 线性前端的工程判断

### 优先保留固定极点或可解释滤波前端

当目标是把模型迁移到模拟电路时，极点部分优先保留为可解释前端，而不是继续把所有自由度交给统一黑盒训练。

长期原因有三点：

- 线性前端更容易落到 `SVF / SOS / IIR` 一类电路结构
- 极点冻结后，训练与硬件映射问题会明显简化
- 频率响应层面的误差更容易被分层定位

### SVF 是当前 WNET5 路线的核心前端

对当前 WNET5 电路路线，SVF 是最核心的线性实现单元。长期规则是：

- 先验证 SVF 层理论响应与 SPICE 响应是否一致
- 再叠加 Dense 层和激活层
- 不要在 SVF 本身还未对齐时就直接做整网 end-to-end 比较

相关实现已经落在 `src/visualization/wnet5_circuit_validator.py` 与 `ex_projects/wnet5-circuit-validation/`。

### WNET5 的 SPICE 导出必须保留线性前端语义

对当前 WNET5 路线，长期稳定的导出语义是：

- 输入仍是 1 维时序
- 第一层必须先经过 `SVF / IIR` 线性前端展开成多通道特征
- 后续 Dense / activation 电路只消费这组已经展开的前端输出

也就是说，WNET5 的 SPICE 导出必须保留 `输入 1 维 -> SVF/IIR -> 多通道 -> Dense` 这条前端语义，不能为了省事跳过线性前端，直接把单通道输入送进 Dense 电路。否则不仅会破坏维度契约，也会让 TF / NumPy / SPICE 的分层对比失去意义。

更具体的自测试补偿、E96 量化误差、SVF 实测拟合与分层图产物约束，统一以 [wnet5_circuit_validation.md](wnet5_circuit_validation.md) 为权威出处；本页只保留电路实现侧的长期边界。

## 波形与逐层验证规则

更具体的 wave / `WaveData` 与多后端逐层推理约定，详见 [wave_layered_inference.md](wave_layered_inference.md)。

### wave 是 TF / SPICE 之间的桥接载体

当前项目的长期方向，是把统一的波形文件作为不同后端之间的桥接层，而不是让每个后端各自维护一套不兼容的数据格式。

这意味着：

- TF 推理结果可以落成 wave
- SPICE 推理结果也应落成 wave
- 层间对比优先基于 wave 和统一频响/时域分析链路完成

### 输入与输出分离优先于强绑在单文件

对电路逐层验证，长期更推荐把输入波形和输出波形分离保存，而不是把所有层的输入输出强行捆到一个复杂容器里。

这样做的好处是：

- 可以灵活比较任意两层之间的频响关系
- 更容易复用现有频响分析流程
- 减少多层、多震级、多频率情况下的数据结构爆炸

### 必须逐层比对，不要只看最终输出

电路转换验证应按下面顺序推进：

1. 先比对线性前端输出。
2. 再比对 Dense / 加法器输出。
3. 最后再比对激活后与整层输出。

如果直接拿最终输出对比，很多通道顺序、反相、偏置和缩放问题都会被混在一起，无法定位。

## 通道顺序、反相与缩放是第一类排查项

WNET5 / SVF 的更具体验证规则，包括通道映射、自测试补偿和 Q 值口径，详见 [wnet5_circuit_validation.md](wnet5_circuit_validation.md)。

在 WNET5 / SVF 路线下，TF、NumPy、SPICE 三条链路之间最先要排查的，不是 loss，而是：

- 通道顺序是否一致
- 哪些通道天然反相
- 缩放器和量纲是否一致

长期规则是：

- 先确认前端每个输出通道的物理含义和顺序
- 再确认是否需要显式反相或后处理反转
- 最后再比较数值误差

不要在这些基础语义未对齐前，就根据最终波形差异下结论说“SPICE 不对”或“模型不对”。

## Dense 层是当前最大硬件风险点

从电路笔记的长期收敛看，Dense 层权重映射到电阻后的负载效应，是当前最值得优先防守的硬件风险。

长期判断如下：

- 差分电流采样加法器的理论值和实测值必须单独验证
- 电阻网络的负载效应不能被当成二阶小误差忽略
- 进入画板或 BOM 之前，必须先用 SPICE 或等效分析确认加法精度

当前与此直接相关的实现包括：

- `src/spice_simulator/weight_resistor_bom_generator.py`
- `src/spice_simulator/unified_resistance_calculator.py`
- `python cli.py -r PROJECT_NAME`
- `python cli.py -s PROJECT_NAME`

## 偏置调零的长期放置原则

更具体的器件选型、SPICE 收敛参数使用边界和偏置来源排查，详见 [spice_device_bias_practices.md](spice_device_bias_practices.md)。

对当前 Dense + activation 路线，偏置调零更适合放在 Dense 级，而不是放在权重板一侧。

这样做的长期理由是：

- 权重板可以保持更简单、可复用
- Dense 级更接近真正叠加偏置和误差传播的位置
- 运放与激活级联后的偏置更容易在 Dense 级统一修正

## 激活函数的工程判断

### ReLU 在模拟电路中不是默认优先项

当前笔记收敛出的长期判断是：在模拟电路里，ReLU 不应被当成默认最稳妥的激活函数。

原因不是它不能做，而是：

- 它往往依赖偏置来产生非线性
- 二极管和运放的非理想性会把小偏置不断累积
- 中间层 offset 很容易演化成非预期非线性

因此，当 ReLU 路线表现不稳时，应先把问题理解为“偏置与器件非理想的工程问题”，而不是简单归因于仿真器误差。更具体的偏置来源与调零实践，详见 [spice_device_bias_practices.md](spice_device_bias_practices.md)。

### tanh / 中心对称非线性更适合低偏置场景

当前更有潜力的方向，是不依赖显式 bias 的中心对称非线性，例如 tanh 路线。

长期理由是：

- 对 offset 更不敏感
- 更接近“零中心”处理
- 在层间累积误差较大时更容易保持行为稳定

这不意味着 tanh 一定是最终答案，但它在当前模拟实现约束下，比偏置驱动型 ReLU 更值得优先验证。

### 精密整流器件优先看漏电，而不是只看压降

若走精密整流 / ReLU 近似路线，长期器件判断应优先关注低频高精度下的反向漏电流，而不是只盯着二极管的正向压降。

因此，对低频精密整流场景，像 `BAS116` 这类低漏电器件比 `1N4148` 更适合作为默认候选；但最终仍要通过 SPICE 和整层误差验证，不应只凭器件手册下结论。器件筛选与漏电主导的长期解释，详见 [spice_device_bias_practices.md](spice_device_bias_practices.md)。

## SPICE 仿真结果的解释原则

收敛报错、跨仿真器复核和器件模型取舍的更具体规则，详见 [spice_device_bias_practices.md](spice_device_bias_practices.md)。

- 先区分是电路原理错误、网表接线错误，还是仿真收敛问题。
- 理想运放能跑通，不代表真实器件模型就一定正确。
- 一旦真实器件模型和理想模型差异很大，优先检查偏置、漏电、输入极性、负载和静态工作点。
- LTSpice、ngspice、Multisim 等结果不一致时，先核对电路连接和器件模型，再讨论谁更可信。

## 推荐工作流

1. 先在算法侧收敛到“线性前端 + 剩余可训练部分”的可解释结构。
2. 用 TF / NumPy 验证逐层输出语义，再落到 SPICE。
3. 先验证 SVF / SOS / IIR 线性前端，再验证 Dense。
4. 对电阻映射和加法器单独做负载效应验证。
5. 对激活函数优先验证偏置与器件非理想的影响，再决定是否继续走 ReLU。
6. 进入 BOM 或画板前，先跑 `-r` / `-s` 和分层 EP 验证。

## 相关文档

- [ep.md](ep.md)
- [export_resistance.md](export_resistance.md)
- [standardize_resistance.md](standardize_resistance.md)
- [timeseries_frequency_analysis.md](timeseries_frequency_analysis.md)
- [model_architecture_selection.md](model_architecture_selection.md)
- [wave_layered_inference.md](wave_layered_inference.md)
- [wnet5_circuit_validation.md](wnet5_circuit_validation.md)
- [spice_device_bias_practices.md](spice_device_bias_practices.md)
