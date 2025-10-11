# Alias数据集波形反相功能实施计划

## 实施日期
2025年9月10日

## 问题背景
在 `Dataset_COMP_Alias` 类型的数据集中，由于使用了 `highpass_fit` 生成目标系统，在160-200Hz频率范围内出现相位反向问题。补偿目标的相位与补偿前波形相反，影响训练效果。

## 解决方案概述
通过在配置文件的 `dataset` 部分添加 `inverse_waveform` 选项，在数据预处理阶段对原始波形进行反相处理，解决相位反向问题。

## 深入调查结果

### 1. 现有代码结构分析

#### 1.1 配置系统结构
- **文件**: `config.py`
- **现有dataset配置**: 第92-96行已有 `self.dataset` 字典结构
- **当前内容**: 仅包含 `freq_range_hz` 配置项
- **加载机制**: `load_from_json` 方法支持动态加载配置

#### 1.2 数据流处理链路
```
Config.dataset -> ModelEngine.load_dataset() -> Dataset_COMP_Alias.__init__() 
-> prepare_features_comp() -> pre_process_data_M50() -> pre_process_data() 
-> TimeSeries对象处理
```

#### 1.3 TimeSeries反相功能
- **文件**: `calibration_analyzer/exam_class.py`
- **方法**: `TimeSeries.invert()` (第614-624行)
- **功能**: 执行 `y = -y` 操作，返回新的TimeSeries对象

### 2. 关键调用点分析

#### 2.1 Dataset_COMP_Alias初始化
- **文件**: `core/data_processing.py` 第999-1137行
- **当前参数**: 不接收config参数
- **调用位置**: `core/model_engine.py` 第106-113行

#### 2.2 数据预处理调用链
1. `Dataset_COMP_Alias.__init__()` -> `prepare_features_comp()` (第1074行)
2. `prepare_features_comp()` -> `pre_process_data_M50()` (多处调用)
3. `pre_process_data_M50()` -> `pre_process_data()` (第161行)
4. 另外直接调用 `pre_process_data()` (第1086行)

## 具体实施方案

### 第一阶段：配置结构扩展

#### 修改点1: config.py
**位置**: 第92-96行的dataset配置
**修改内容**:
```python
# 原有代码
self.dataset = {
    # 可选的频率范围配置，Hz单位
    # 缺省时使用传统range(6, n-4)逻辑
    'freq_range_hz': None  # 例如: [10, 128]
}

# 修改后代码
self.dataset = {
    # 可选的频率范围配置，Hz单位
    # 缺省时使用传统range(6, n-4)逻辑
    'freq_range_hz': None,  # 例如: [10, 128]
    # 波形反相配置，用于解决Alias数据集的相位问题
    'inverse_waveform': False  # 默认不反相，保证向后兼容
}
```

### 第二阶段：参数传递链修改

#### 修改点2: core/model_engine.py
**位置**: 第106-113行的Dataset_COMP_Alias实例化
**修改内容**:
```python
# 原有代码
self.dataset_origin = Dataset_COMP_Alias(
    data_info_list,
    self.config.target_sweep,
    sweep_list,
    use_cache=self.config.use_cache_features,
    time_cliped_s=self.config.time_clipped_s,
    fs=self.config.sample_rate
)

# 修改后代码
self.dataset_origin = Dataset_COMP_Alias(
    data_info_list,
    self.config.target_sweep,
    sweep_list,
    use_cache=self.config.use_cache_features,
    time_cliped_s=self.config.time_clipped_s,
    fs=self.config.sample_rate,
    config=self.config  # 传递完整配置对象
)
```

#### 修改点3: core/data_processing.py - Dataset_COMP_Alias类
**位置**: 第1008-1029行的__init__方法签名
**修改内容**:
```python
# 原有方法签名
def __init__(
        self,
        data_info_list: List[exam_process.DataInfo],
        target_sweep,
        sweep_list,
        freq_threshold=80,  # 区分正常频率和假频的频率阈值
        use_cache=True,
        use_debug=False,
        fs=2000,
        time_cliped_s=2.0
):

# 修改后方法签名
def __init__(
        self,
        data_info_list: List[exam_process.DataInfo],
        target_sweep,
        sweep_list,
        freq_threshold=80,  # 区分正常频率和假频的频率阈值
        use_cache=True,
        use_debug=False,
        fs=2000,
        time_cliped_s=2.0,
        config=None  # 新增配置参数
):
```

**位置**: 第1030-1050行的配置处理
**修改内容**:
```python
# 在现有初始化代码后添加
# 提取波形反相配置 - 直接访问确保配置存在性验证
inverse_waveform = False
if config and hasattr(config, 'dataset') and isinstance(config.dataset, dict):
    if 'inverse_waveform' in config.dataset:
        inverse_waveform = config.dataset['inverse_waveform']
        print(f"检测到inverse_waveform配置: {inverse_waveform}")
    else:
        print("警告: dataset配置中未找到inverse_waveform，使用默认值False")

# 更新缓存参数以包含新配置
cache_params = {
    'target_sweep': target_sweep,
    'sweep_list': sweep_list,
    'freq_threshold': freq_threshold,
    'fs': fs,
    'time_cliped_s': time_cliped_s,
    'inverse_waveform': inverse_waveform,  # 新增
    'data_paths': [info.data_file_path for info in data_info_list if info.data_file_path]
}
```

### 第三阶段：数据处理函数修改

#### 修改点4: core/data_processing.py - prepare_features_comp函数
**位置**: 第718-739行的函数签名
**修改内容**:
```python
# 原有函数签名
def prepare_features_comp(
        data_info_list: List[exam_process.DataInfo],
        target_sweep,
        sweep_list,
        fs=2000,
        time_cliped_s=2.0,
        use_cache=True,
        use_debug=False,
        build_target_with_comp=True
):

# 修改后函数签名
def prepare_features_comp(
        data_info_list: List[exam_process.DataInfo],
        target_sweep,
        sweep_list,
        fs=2000,
        time_cliped_s=2.0,
        use_cache=True,
        use_debug=False,
        build_target_with_comp=True,
        inverse_waveform=False  # 新增参数
):
```

**位置**: 第740-750行的缓存参数更新
**修改内容**:
```python
# 更新cache_params
cache_params = {
    'target_sweep': target_sweep,
    'sweep_list': sweep_list,
    'fs': fs,
    'time_cliped_s': time_cliped_s,
    'build_target_with_comp': build_target_with_comp,
    'inverse_waveform': inverse_waveform,  # 新增
    'data_info_paths': [info.data_file_path for info in data_info_list if info.data_file_path]
}
```

#### 修改点5: core/data_processing.py - pre_process_data_M50函数
**位置**: 第141-154行的函数签名
**修改内容**:
```python
# 原有函数签名
def pre_process_data_M50(
        data_info_list,
        index,
        amply=0.006,
        use_resample=True,
        fade_in=0.3,
        fade_out=0.0,
        time_cliped_s=2.0,
        filter_bandpass=True,
        filter_bandpass_freq=[10, 500],
        fs=2000,
        use_debug=False
) -> Tuple['System', List['TimeSeries'], List['TimeSeries'], List[float]]:

# 修改后函数签名
def pre_process_data_M50(
        data_info_list,
        index,
        amply=0.006,
        use_resample=True,
        fade_in=0.3,
        fade_out=0.0,
        time_cliped_s=2.0,
        filter_bandpass=True,
        filter_bandpass_freq=[10, 500],
        fs=2000,
        use_debug=False,
        inverse_waveform=False  # 新增参数
) -> Tuple['System', List['TimeSeries'], List['TimeSeries'], List[float]]:
```

#### 修改点6: core/data_processing.py - pre_process_data函数
**位置**: 第19-31行的函数签名
**修改内容**:
```python
# 原有函数签名
def pre_process_data(
        data_path,
        amply=0.006,
        use_resample=True,
        fade_in=0.3,
        fade_out=0.0,
        time_cliped_s=2.0,
        filter_bandpass=True,
        filter_bandpass_freq=[10, 500],
        fs=2000,
        use_debug=False
) -> Tuple['System', List['TimeSeries'], List['TimeSeries'], List[float]]:

# 修改后函数签名
def pre_process_data(
        data_path,
        amply=0.006,
        use_resample=True,
        fade_in=0.3,
        fade_out=0.0,
        time_cliped_s=2.0,
        filter_bandpass=True,
        filter_bandpass_freq=[10, 500],
        fs=2000,
        use_debug=False,
        inverse_waveform=False  # 新增参数
) -> Tuple[List['TimeSeries'], List['TimeSeries'], List[float]]:
```

**位置**: 第135-139行的返回前添加反相处理
**修改内容**:
```python
# 在现有的渐入渐出处理后，return之前添加
# 波形反相处理
if inverse_waveform:
    input_tr_list = [ts.invert() for ts in input_tr_list]
    output_tr_list = [ts.invert() for ts in output_tr_list]
    if use_debug:
        print(f"波形反相处理完成，处理了 {len(input_tr_list)} 个输入和 {len(output_tr_list)} 个输出序列")

logger.info(f'freq_list: {freq_list}')
return input_tr_list, output_tr_list, freq_list
```

### 第四阶段：调用链参数传递

#### 修改点7: Dataset_COMP_Alias中的函数调用传递
**位置1**: 第1074-1081行的prepare_features_comp调用
```python
# 修改prepare_features_comp调用
inputs, output_ori, _, sys_target_fit, magn_list, freq_list = prepare_features_comp(
    data_info_list,
    target_sweep,
    sweep_list,
    use_cache=False,
    fs=fs,
    time_cliped_s=time_cliped_s,
    use_debug=False,
    inverse_waveform=inverse_waveform  # 新增参数传递
)
```

**位置2**: 第1086-1087行的pre_process_data调用
```python
# 修改pre_process_data调用
input_tr, output_tr, freq_list = pre_process_data(
    target_file_path, 
    fs=fs, 
    time_cliped_s=time_cliped_s,
    inverse_waveform=inverse_waveform  # 新增参数传递
)
```

#### 修改点8: prepare_features_comp函数内部调用传递
**需要修改的调用点**:
1. 第777-778行的pre_process_data_M50调用（target系统）
2. 第795-796行的pre_process_data_M50调用（每个sweep）

```python
# 修改目标系统的pre_process_data_M50调用
sys_target, tr_input_target, tr_output_target, freq_list = pre_process_data_M50(
    data_info_list, 
    sweep_list[target_sweep], 
    fade_in=fade_in, 
    fade_out=fade_out, 
    fs=fs, 
    time_cliped_s=time_cliped_s,
    inverse_waveform=inverse_waveform  # 新增参数传递
)

# 修改每个sweep的pre_process_data_M50调用
sys_sweep, tr_input, tr_output, freq_list = pre_process_data_M50(
    data_info_list, 
    i, 
    fade_in=fade_in, 
    fade_out=fade_out, 
    fs=fs, 
    time_cliped_s=time_cliped_s,
    inverse_waveform=inverse_waveform  # 新增参数传递
)
```

#### 修改点9: pre_process_data_M50函数内部调用传递
**位置**: 第161-171行的pre_process_data调用
```python
# 修改pre_process_data调用
input_tr, output_tr, freq_list = pre_process_data(
    file_path,
    amply=amply,
    use_resample=use_resample,
    fade_in=fade_in,
    fade_out=fade_out,
    time_cliped_s=time_cliped_s,
    filter_bandpass=filter_bandpass,
    filter_bandpass_freq=filter_bandpass_freq,
    fs=fs,
    use_debug=use_debug,
    inverse_waveform=inverse_waveform  # 新增参数传递
)
```

## 实施风险评估

### 技术风险
1. **缓存失效**: 新参数会导致现有缓存失效，但这是期望行为
2. **参数传递链**: 需要确保所有调用点都正确传递新参数
3. **向后兼容**: 默认值False确保现有项目不受影响

### 测试策略
1. **单元测试**: 验证TimeSeries.invert()功能
2. **集成测试**: 验证完整的参数传递链
3. **配置测试**: 验证配置解析和传递
4. **相位验证**: 验证反相后的相位关系

## 部署计划

### 阶段1: 核心功能实现（1-2天）
1. 修改config.py添加配置项
2. 修改所有函数签名添加reverse_waveform参数
3. 实现波形反相逻辑

### 阶段2: 参数传递链完善（1天）
1. 修改ModelEngine中的Dataset_COMP_Alias实例化
2. 完善所有函数调用的参数传递
3. 更新缓存机制

### 阶段3: 测试验证（1天）
1. 单元测试和集成测试
2. 在测试项目中验证功能
3. 相位问题验证

### 阶段4: 文档和部署（0.5天）
1. 更新相关文档
2. 在目标项目中应用配置

## 验收标准
1. 配置文件正确解析inverse_waveform选项
2. 当inverse_waveform=true时，所有输入和输出波形都被正确反相
3. 当inverse_waveform=false时，行为与修改前完全一致
4. 缓存机制正常工作，不同配置生成不同缓存
5. 相位问题得到解决
6. 配置缺失时能明确提示，不会静默使用默认值

## 总结
这个实施计划通过在配置系统中添加inverse_waveform选项，在数据预处理的最早阶段实现波形反相，能够有效解决Alias数据集的相位反向问题。使用inverse而非reverse更准确地表达数学逆运算的含义。配置检查采用直接访问方式，确保配置生效的可见性。实施过程中需要修改9个主要调用点，确保参数正确传递到最终的数据处理函数。
