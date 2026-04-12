# 时域数据与频响测量

## 功能概述

本项目的时域数据处理、频率响应重建和部分推理后端，共用同一套 TimeSeries 与 System 抽象。

这套能力主要分布在以下位置：

- `src/calibration_analyzer/exam_class.py`：`TimeSeries`、`System`、`load_data_json_to_time_sereis()`、时域法频响测量
- `src/core/data_processing.py`：`_data.json` 预处理、降采样、滤波、裁剪与统一频响构建
- `src/inference/backends/timeseries_backend.py`：基于 `time_response()` 的时序推理后端
- `src/visualization/model_analysis.py`：对神经网络或 Conv1D 层做时域法频响分析的包装调用

## TimeSeries 约定

`TimeSeries` 是仓库里最基础的时域波形对象，长期可依赖的能力包括：

- 采样值 `samples`
- 采样率 `fs`
- 元数据 `params`
- 生成标准激励：`fromSin()`、`fromSquare()`、`fromTriangle()`、`fromSawtooth()`
- 时域预处理：`apply_fade()`、`resample()`、`clip()`、`remove_dc()`、`filter()`、`normalize()`
- 本地二进制存储：单通道 `dumptobinary()` / `loadfrombinary()`，多通道 `dump_multichannel_to_binary()` / `load_multichannel_from_binary()`

### 波形生成规则

- 正弦等标准激励默认支持 `fade_in` 与 `fade_out`
- 当前实现中的 fade 使用 S 型包络，而不是线性 ramp
- 做频响测量或系统仿真时，应优先复用 `TimeSeries.fromSin()`，避免各脚本自己生成激励导致口径漂移

### 多通道时域数据

- 多通道波形允许每个通道携带独立 `params`
- 多通道二进制接口适合本地缓存或可视化中间产物，不应替代项目级训练/评估产物
- 连接多个 `TimeSeries` 时要求采样率一致，否则应先显式重采样

## `_data.json` 到 TimeSeries 的加载口径

历史实验中常见的原始记录格式是单个 `*_data.json` 文件。统一加载入口为 `load_data_json_to_time_sereis()`。

当前长期有效的口径如下：

- 输入序列使用 `dataRecord.ch1_integrate`
- 输出序列使用 `dataRecord.ch2`
- 频率标签读取 `dataRecord.param.params['freq']`
- 采样率使用 `CONF_SAMPLING_RATE`

如果后续新增 JSON 数据格式，应优先扩展统一加载入口，而不是在不同脚本里各自解析一遍。

## 预处理链路

`src/core/data_processing.py` 中的 `pre_process_data()` 已经形成相对稳定的时域预处理顺序。默认流程是：

1. 从 `*_data.json` 加载输入/输出 `TimeSeries` 列表与频率列表
2. 先截取靠后的原始片段，减少起始瞬态影响
3. 按需要降采样到目标 `fs`
4. 施加增益缩放
5. 去除直流分量
6. 进行带通滤波
7. 再裁出用于分析的中间稳态窗口
8. 对最终窗口施加 fade

这条顺序的核心目的不是“把波形处理得更好看”，而是让输入与输出在统一口径下进入稳态分析和频响重建。

### 使用约束

- 频响异常时，先检查预处理顺序是否被改乱，再怀疑模型
- 降采样前后的抗混叠策略要一致，否则不同脚本得到的频响会不一致
- 起始段若存在明显冷启动或窗口不完整，应在预处理阶段裁掉，而不是在后续指标阶段硬算进去

## 从时域序列重建频率响应

仓库的统一入口有两类：

- `System.fromTimeSeries()`：直接从输入/输出 `TimeSeries` 列表构造频响
- `System.frequency_response_from_time_domain()`：给定一个具备 `time_response()` 的系统或模型，通过扫频激励反推出频响

### `System.fromTimeSeries()` 的判定口径

`System.fromTimeSeries()` 会对每个频点调用统一的 `process_frequency_response()`，长期规则包括：

- 输入、输出和频率列表长度必须一一对应
- 输入与输出采样率必须一致
- 计算时优先截取整数周期长度
- 幅值和相位主要基于信号后半段稳态片段计算，而不是整段直接 FFT
- 幅值检测使用选频思路，只取最接近目标频率的频率分量
- 输出结果最终按频率排序

这套规则是为了解决 NOTEBOOK 早期反复出现的几类问题：

- 起始瞬态污染幅值
- 非整周期导致频谱泄漏
- 靠近谐振峰时曲线抖动过大
- 不同脚本对相位和幅值的测量口径不一致

### `System.frequency_response_from_time_domain()` 的适用场景

适用于任何实现了 `time_response()` 的对象，例如：

- 经典时域系统
- `TimeDomainSystem` 串联结构
- 映射非线性系统
- Duffing 等仿真对象
- 包装后的神经网络模型或卷积层

实际做法是：

1. 为每个目标频率生成正弦输入
2. 调用对象的 `time_response()` 获得输出波形
3. 用统一的稳态幅值/相位检测逻辑生成该频点的频响
4. 汇总为 `System`

### 并行与稳定性

- 这两条路径都支持并行，但并行只影响速度，不应改变测量口径
- 如果并行结果和串行结果差异明显，通常是底层对象不可安全并行，而不是频响算法本身有两套口径
- 谐振附近若出现毛刺，优先增加 `time_length` 或检查整数周期截取条件

## 频响测量经验

从 NOTEBOOK 蒸馏后，长期保留的工程经验如下：

- 接近谐振峰时，优先增加观测时长，而不是只增加采样率
- 用带包络的正弦激励能更快进入稳态，减少前段污染
- 测量幅值时应优先按目标频率选频，不要直接拿全带 FFT 峰值替代
- 当时域看起来正常而频响明显异常时，先检查测量方法，再检查模型
- 同一批实验必须固定预处理、窗口、选频和相位计算方法，否则跨项目对比没有意义

## TimeSeries 推理后端

`TimeSeriesBackend` 适用于实现了 `time_response()` 的模型包装类。

长期约束如下：

- 该后端按记录逐条把输入 `WaveRecord` 转成 `TimeSeries`
- 通过模型的 `time_response()` 生成输出 `TimeSeries`
- 再将输出写回 `WaveData`
- 这是时序模型与波形数据结构之间最直接的桥接路径

如果某个模型支持批量 Tensor 输入，但不支持 `time_response()`，它不应勉强塞进这个后端，而应走 batch 或 layered 后端。

## IIR / RNN 前端的关系

本项目中，IIR 到 RNN 的等效并不是孤立理论问题，而是直接影响时域仿真、频响重建和 FRI 前端实现的一致性。

时间步对齐的长期原则以 [modeling_principles.md](modeling_principles.md) 为准；这里不再重复推导，只保留执行要求：

- 改 IIR/RNN 前端时，先做时间步对齐验证
- 再做时域波形验证
- 最后才比较频响和训练指标

## 快速排查

- `*_data.json` 加载后频点不对：先检查 `param.params['freq']` 是否完整
- 频响起始段异常：先检查裁剪窗口和 fade，而不是先调模型
- 谐振附近曲线抖动：先增加 `time_length`，再检查整数周期截取
- 时域正常但频域失真：优先检查是否复用了统一的 `System.fromTimeSeries()` / `frequency_response_from_time_domain()` 路径
- 不同机器结果不一致：同时回看预处理参数、特征缓存和频响测量口径

## 相关文档

- [modeling_principles.md](modeling_principles.md)
- [training.md](training.md)
- [inference.md](inference.md)
- [waveform_visualization.md](waveform_visualization.md)