# WNET5 实验数据对比功能实施方案（C05）

## 一、需求背景

### 1.1 原始需求（C05）

在 C04 已实现多层电路验证功能的基础上，现在需要对比实验测量数据和仿真数据的频率响应：

**核心需求**：
1. **对比幅频响应**：上下布局两张图
   - 上图：实际测试的幅频响应（6个通道）
   - 下图：仿真的幅频响应（6个通道）
   
2. **坐标系要求**：使用 **loglog** 坐标系绘制
   - x轴：频率（对数刻度）
   - y轴：幅度，单位 dB（对数刻度）

3. **自测试补偿**：实际测试的幅度需除以自测试频响
   - 自测试文件：`exam_data\SVF-W_DENSE\output_20251103_085135_sweep_selftest_震级1.0.xlsx`
   - 补偿方式：频点一一对应相除

4. **自动识别层和通道**：根据文件名自动识别
   - 示例：`output_20251104_085010_SVF-W_DENSE2_2_震级1.0.xlsx` → 第2层第2通道

5. **集成到现有功能**：在每个层的验证项目中绘制对比图
   - 例如：`ex_projects\inference\wnet5-circuit-validation\WNET5q1h2u6l3_layer1` 绘制第1层对比

### 1.2 实验数据文件结构

**目录**：`exam_data\SVF-W_DENSE\`

**文件命名规则**：
```
output_{时间戳}_SVF-W_DENSE{层号}_{通道号}_震级1.0.xlsx
output_{时间戳}_sweep_selftest_震级1.0.xlsx  # 自测试文件
```

**已有文件示例**：
```
output_20251103_085135_sweep_selftest_震级1.0.xlsx      # 自测试
output_20251103_145209_SVF-W_DENSE1_1_震级1.0.xlsx     # 第1层第1通道
output_20251103_150634_SVF-W_DENSE1_2_震级1.0.xlsx     # 第1层第2通道
...
output_20251104_085010_SVF-W_DENSE2_2_震级1.0.xlsx     # 第2层第2通道
output_20251104_092615_SVF-W_DENSE2_3_震级1.0.xlsx     # 第2层第3通道
...
output_20251104_104211_SVF-W_DENSE3_1_震级1.0.xlsx     # 第3层第1通道
output_20251104_110835_SVF-W_DENSE4_1_震级1.0.xlsx     # 第4层第1通道
...
```

**特殊命名**（注意连字符）：
```
output_20251104_135448_SVF-W_DENSE3-2_震级1.0.xlsx     # 第3层第2通道（使用连字符）
output_20251104_141129_SVF-W_DENSE3-3_震级1.0.xlsx     # 第3层第3通道（使用连字符）
```

**Excel 文件格式**（推测）：
```
列名：F | D{layer}_{channel}_GAIN/B1 | ...
例如：F | D1_1_GAIN/B1 | D1_2_GAIN/B1 | ...
```

---

## 二、当前实现分析

### 2.1 现有实验对比功能

**文件**：`visualization/wnet5_circuit_validator.py`

**已实现的对比功能**（第285-401行）：

```python
def _generate_plots(self, freq_response, dense_weights):
    """生成幅频响应图 (线性增益对数刻度, 支持实验对比)"""
    
    # 1. 理论幅度 (内部存储为 dB, 转线性)
    frequencies = freq_response['frequencies']
    mag_db_list = freq_response['magnitude_db']
    mag_list = [np.clip(np.power(10.0, m/20.0), 1e-20, None) for m in mag_db_list]
    
    # 2. 读取实验数据 (列名形式 D{layer}_[N]_GAIN/B1)
    exp_freq = None
    exp_mags = None
    if self.experiment_path:
        try:
            import pandas as pd, re
            exp_file = Path(self.experiment_path)
            if exp_file.exists():
                df = pd.read_excel(exp_file)
                # 匹配频率列
                freq_cols = [c for c in df.columns if str(c).strip().lower() in ['f','freq','frequency',...]]
                fcol = freq_cols[0] if freq_cols else df.columns[0]
                exp_freq = df[fcol].to_numpy(dtype=float)
                
                # 动态匹配当前分析的层
                pattern = re.compile(rf'^D{analysis_layer}_(\d+)_GAIN/B1$')
                matched = {}
                for c in df.columns:
                    m = pattern.match(str(c).strip())
                    if m:
                        idx = int(m.group(1))
                        arr = df[c].astype(float).to_numpy(dtype=float)
                        matched[idx] = arr
                
                if matched:
                    exp_mags = [matched[ch] for ch in range(1, len(mag_list)+1)]
    
    # 3. 绘制对比图 (上下布局)
    if exp_mags is not None:
        fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(12, 8))
        # 理论数据
        for i, (m, lbl) in enumerate(zip(mag_list, output_labels)):
            ax_top.semilogx(frequencies, m, ...)
        # 实验数据
        for i, (m, lbl) in enumerate(zip(exp_mags, output_labels)):
            ax_bottom.semilogx(exp_freq, m, ...)
```

**当前实现的问题**：
1. ❌ 使用 **semilogx**（x对数，y线性），而非 **loglog**（x对数，y对数）
2. ❌ 数据单位是**线性增益**，而非 **dB**
3. ❌ 实验数据来自**单一Excel文件**（所有通道在一个文件中），而非多个文件
4. ❌ **没有自测试补偿**功能
5. ✅ 已支持上下布局（理论 vs 实验）

---

## 三、实施方案设计

### 3.1 核心思路

在现有 `_generate_plots()` 函数基础上：

1. **新增功能开关**：通过配置控制使用新的对比模式
2. **自动扫描实验文件**：从目录中匹配对应层的所有通道文件
3. **自测试补偿**：加载自测试文件，对每个通道的幅频响应进行补偿
4. **loglog 坐标系**：x轴和y轴都使用对数刻度，y轴单位为 dB
5. **保持向后兼容**：不影响现有的单文件对比功能

### 3.2 配置文件修改

**文件**：`ex_projects/inference/wnet5-circuit-validation/{project_name}/config.json`

**新增配置项**：

```json
{
  "task_info": {
    "task_type": "wnet5-circuit-validation",
    "description": "WNET5电路频率响应理论验证 - Dense层1"
  },
  "model_project_name": "WNET5q1h2u6l3",
  "analysis_layer": 1,
  "frequency_range": {
    "start_freq": 2,
    "stop_freq": 500
  },
  
  // ⬇️⬇️⬇️ 新增：实验对比配置 ⬇️⬇️⬇️
  "experiment_comparison": {
    "enable": true,                                      // 是否启用实验对比
    "mode": "multi_file",                                // 对比模式：multi_file（多文件）或 single_file（单文件，旧模式）
    "experiment_data_dir": "exam_data/SVF-W_DENSE",     // 实验数据目录
    "selftest_file": "exam_data/SVF-W_DENSE/output_20251103_085135_sweep_selftest_震级1.0.xlsx",  // 自测试文件
    "plot_config": {
      "coordinate_system": "loglog",                     // 坐标系：loglog 或 semilogx
      "y_unit": "dB"                                     // y轴单位：dB 或 linear
    }
  }
  // ⬆️⬆️⬆️ 新增结束 ⬆️⬆️⬆️
}
```

**配置说明**：
- `experiment_comparison.enable`: 是否启用实验对比功能
- `experiment_comparison.mode`: 
  - `"multi_file"`: 新模式，从目录扫描多个实验文件（C05需求）
  - `"single_file"`: 旧模式，使用 `compare_with_experiment` 单文件（向后兼容）
- `experiment_comparison.experiment_data_dir`: 实验数据文件夹路径
- `experiment_comparison.selftest_file`: 自测试频响文件路径
- `plot_config.coordinate_system`: 绘图坐标系
- `plot_config.y_unit`: y轴数据单位

**向后兼容**：
- 如果未配置 `experiment_comparison`，则使用旧的 `compare_with_experiment` 配置
- 如果 `experiment_comparison.enable = false`，则不进行实验对比

---

## 四、代码实现详情

### 4.1 修改点概览

**文件**：`visualization/wnet5_circuit_validator.py`

**修改点清单**：
1. `__init__()` - 新增实验对比配置加载
2. `_load_selftest_data()` - 新增：加载自测试数据
3. `_scan_experiment_files()` - 新增：扫描实验数据文件
4. `_parse_experiment_filename()` - 新增：解析文件名
5. `_load_experiment_channel_data()` - 新增：加载单个通道数据
6. `_compensate_with_selftest()` - 新增：自测试补偿
7. `_generate_plots()` - 重大修改：支持新的对比模式

### 4.2 详细代码修改

#### 修改点1：`__init__()` 函数（第26-38行）

**新增代码**：

```python
def __init__(self, config: Dict[str, Any], output_path: Path):
    self.config = config
    self.output_path = Path(output_path)
    self.model_project_name = config['model_project_name']
    self.frequency_range = config['frequency_range']
    
    # 旧的单文件对比配置（向后兼容）
    self.experiment_path = config.get('compare_with_experiment')
    
    # ⬇️⬇️⬇️ 新增：实验对比配置 ⬇️⬇️⬇️
    self.experiment_comparison = config.get('experiment_comparison', {})
    self.exp_comp_enable = self.experiment_comparison.get('enable', False)
    self.exp_comp_mode = self.experiment_comparison.get('mode', 'single_file')
    self.exp_data_dir = self.experiment_comparison.get('experiment_data_dir')
    self.selftest_file = self.experiment_comparison.get('selftest_file')
    self.plot_config = self.experiment_comparison.get('plot_config', {})
    # ⬆️⬆️⬆️ 新增结束 ⬆️⬆️⬆️
    
    self.analysis_layer = config.get('analysis_layer', 1)
    self._setup_output_directories()
```

#### 修改点2：新增 `_load_selftest_data()` 函数

**位置**：在 `_setup_output_directories()` 之后

```python
def _load_selftest_data(self) -> Dict[str, np.ndarray]:
    """加载自测试频响数据
    
    Returns:
        Dict: {'frequencies': np.ndarray, 'magnitude': np.ndarray}
              magnitude 单位为线性增益
    
    Raises:
        FileNotFoundError: 如果自测试文件不存在
        ValueError: 如果文件格式不正确
    """
    if not self.selftest_file:
        raise ValueError("未配置自测试文件路径 (selftest_file)")
    
    selftest_path = Path(self.selftest_file)
    if not selftest_path.exists():
        raise FileNotFoundError(f"自测试文件不存在: {selftest_path}")
    
    logger.info(f"📂 加载自测试数据: {selftest_path}")
    
    try:
        import pandas as pd
        df = pd.read_excel(selftest_path)
        
        # 查找频率列
        freq_cols = [c for c in df.columns if str(c).strip().lower() in [
            'f', 'freq', 'frequency', 'freq(hz)', 'frequency(hz)', 'hz'
        ]]
        if not freq_cols:
            raise ValueError(f"自测试文件中未找到频率列，列名: {df.columns.tolist()}")
        
        freq_col = freq_cols[0]
        frequencies = df[freq_col].to_numpy(dtype=float)
        
        # 查找增益列（自测试通常只有一个增益列）
        # 可能的列名：GAIN, GAIN/B1, Magnitude, Amplitude
        gain_cols = [c for c in df.columns if c != freq_col and 
                     any(kw in str(c).upper() for kw in ['GAIN', 'MAGNITUDE', 'AMP'])]
        
        if not gain_cols:
            raise ValueError(f"自测试文件中未找到增益列，列名: {df.columns.tolist()}")
        
        gain_col = gain_cols[0]
        magnitude = df[gain_col].to_numpy(dtype=float)
        
        # 检查数据有效性
        if len(frequencies) != len(magnitude):
            raise ValueError(f"频率和增益数据长度不一致: {len(frequencies)} vs {len(magnitude)}")
        
        # 清理无效数据（NaN, Inf）
        valid_mask = np.isfinite(frequencies) & np.isfinite(magnitude)
        frequencies = frequencies[valid_mask]
        magnitude = magnitude[valid_mask]
        
        # 确保增益为正值（避免log运算错误）
        magnitude = np.clip(magnitude, 1e-20, None)
        
        logger.info(f"✅ 自测试数据加载成功: {len(frequencies)} 个频点")
        logger.info(f"   频率范围: {frequencies.min():.2f} - {frequencies.max():.2f} Hz")
        logger.info(f"   增益范围: {magnitude.min():.6f} - {magnitude.max():.6f}")
        
        return {
            'frequencies': frequencies,
            'magnitude': magnitude
        }
        
    except Exception as e:
        logger.error(f"加载自测试数据失败: {e}")
        raise
```

#### 修改点3：新增 `_parse_experiment_filename()` 函数

```python
def _parse_experiment_filename(self, filename: str) -> Dict[str, Any]:
    """解析实验数据文件名
    
    支持的命名格式：
    - output_{时间戳}_SVF-W_DENSE{层号}_{通道号}_震级1.0.xlsx
    - output_{时间戳}_SVF-W_DENSE{层号}-{通道号}_震级1.0.xlsx  (连字符格式)
    
    Args:
        filename: 文件名（不含路径）
    
    Returns:
        Dict: {
            'layer': int,        # 层号
            'channel': int,      # 通道号
            'timestamp': str,    # 时间戳
            'magnitude': float   # 震级（默认1.0）
        }
        如果解析失败，返回 None
    
    Examples:
        >>> _parse_experiment_filename('output_20251104_085010_SVF-W_DENSE2_2_震级1.0.xlsx')
        {'layer': 2, 'channel': 2, 'timestamp': '20251104_085010', 'magnitude': 1.0}
        
        >>> _parse_experiment_filename('output_20251104_135448_SVF-W_DENSE3-2_震级1.0.xlsx')
        {'layer': 3, 'channel': 2, 'timestamp': '20251104_135448', 'magnitude': 1.0}
    """
    import re
    
    # 模式1：下划线分隔 SVF-W_DENSE{层号}_{通道号}
    pattern1 = r'output_(\d+_\d+)_SVF-W_DENSE(\d+)_(\d+)_震级([\d.]+)\.xlsx'
    match = re.match(pattern1, filename)
    
    if match:
        timestamp, layer, channel, magnitude = match.groups()
        return {
            'layer': int(layer),
            'channel': int(channel),
            'timestamp': timestamp,
            'magnitude': float(magnitude)
        }
    
    # 模式2：连字符分隔 SVF-W_DENSE{层号}-{通道号}
    pattern2 = r'output_(\d+_\d+)_SVF-W_DENSE(\d+)-(\d+)_震级([\d.]+)\.xlsx'
    match = re.match(pattern2, filename)
    
    if match:
        timestamp, layer, channel, magnitude = match.groups()
        return {
            'layer': int(layer),
            'channel': int(channel),
            'timestamp': timestamp,
            'magnitude': float(magnitude)
        }
    
    # 解析失败
    return None
```

#### 修改点4：新增 `_scan_experiment_files()` 函数

```python
def _scan_experiment_files(self, target_layer: int) -> Dict[int, Path]:
    """扫描实验数据目录，查找指定层的所有通道数据文件
    
    Args:
        target_layer: 目标层号
    
    Returns:
        Dict[int, Path]: {通道号: 文件路径}
        例如: {1: Path('...DENSE1_1...xlsx'), 2: Path('...DENSE1_2...xlsx'), ...}
    
    Raises:
        FileNotFoundError: 如果实验数据目录不存在
    """
    if not self.exp_data_dir:
        raise ValueError("未配置实验数据目录 (experiment_data_dir)")
    
    exp_dir = Path(self.exp_data_dir)
    if not exp_dir.exists():
        raise FileNotFoundError(f"实验数据目录不存在: {exp_dir}")
    
    logger.info(f"🔍 扫描实验数据目录: {exp_dir}")
    logger.info(f"   目标层: {target_layer}")
    
    # 扫描目录中的所有 .xlsx 文件
    channel_files = {}
    
    for file_path in exp_dir.glob('*.xlsx'):
        filename = file_path.name
        
        # 跳过自测试文件
        if 'selftest' in filename.lower():
            continue
        
        # 解析文件名
        parsed = self._parse_experiment_filename(filename)
        
        if parsed is None:
            logger.debug(f"   跳过无法解析的文件: {filename}")
            continue
        
        # 检查是否匹配目标层
        if parsed['layer'] == target_layer:
            channel = parsed['channel']
            
            # 检查重复
            if channel in channel_files:
                logger.warning(
                    f"   ⚠️ 发现重复通道数据: 层{target_layer}通道{channel}\n"
                    f"      已有: {channel_files[channel].name}\n"
                    f"      新文件: {filename}\n"
                    f"      将使用新文件（假设时间戳更新）"
                )
            
            channel_files[channel] = file_path
            logger.info(f"   ✅ 找到: 层{target_layer}通道{channel} - {filename}")
    
    if not channel_files:
        logger.warning(f"⚠️ 未找到层{target_layer}的实验数据文件")
        return {}
    
    logger.info(f"✅ 共找到 {len(channel_files)} 个通道的实验数据")
    
    # 按通道号排序
    sorted_channels = dict(sorted(channel_files.items()))
    return sorted_channels
```

#### 修改点5：新增 `_load_experiment_channel_data()` 函数

```python
def _load_experiment_channel_data(self, file_path: Path) -> Dict[str, np.ndarray]:
    """加载单个实验通道的数据
    
    Args:
        file_path: 实验数据文件路径
    
    Returns:
        Dict: {'frequencies': np.ndarray, 'magnitude': np.ndarray}
              magnitude 单位为线性增益
    
    Raises:
        ValueError: 如果文件格式不正确
    """
    logger.debug(f"   加载实验数据: {file_path.name}")
    
    try:
        import pandas as pd
        df = pd.read_excel(file_path)
        
        # 查找频率列
        freq_cols = [c for c in df.columns if str(c).strip().lower() in [
            'f', 'freq', 'frequency', 'freq(hz)', 'frequency(hz)', 'hz'
        ]]
        if not freq_cols:
            raise ValueError(f"文件中未找到频率列: {file_path.name}")
        
        freq_col = freq_cols[0]
        frequencies = df[freq_col].to_numpy(dtype=float)
        
        # 查找增益列
        # 可能的列名模式：D{layer}_{channel}_GAIN/B1 或简单的 GAIN
        gain_cols = [c for c in df.columns if c != freq_col and 
                     any(kw in str(c).upper() for kw in ['GAIN', 'MAGNITUDE', 'AMP'])]
        
        if not gain_cols:
            raise ValueError(f"文件中未找到增益列: {file_path.name}")
        
        # 如果有多个增益列，选择第一个
        gain_col = gain_cols[0]
        magnitude = df[gain_col].to_numpy(dtype=float)
        
        # 数据清理
        valid_mask = np.isfinite(frequencies) & np.isfinite(magnitude)
        frequencies = frequencies[valid_mask]
        magnitude = magnitude[valid_mask]
        magnitude = np.clip(magnitude, 1e-20, None)
        
        return {
            'frequencies': frequencies,
            'magnitude': magnitude
        }
        
    except Exception as e:
        logger.error(f"加载实验数据失败 {file_path.name}: {e}")
        raise
```

#### 修改点6：新增 `_compensate_with_selftest()` 函数

```python
def _compensate_with_selftest(
    self, 
    exp_freq: np.ndarray, 
    exp_mag: np.ndarray, 
    selftest_data: Dict[str, np.ndarray]
) -> np.ndarray:
    """使用自测试数据补偿实验数据
    
    补偿方法：exp_compensated = exp_mag / selftest_mag
    通过插值使自测试数据与实验数据的频点对齐
    
    Args:
        exp_freq: 实验数据的频率点
        exp_mag: 实验数据的幅度（线性增益）
        selftest_data: 自测试数据 {'frequencies', 'magnitude'}
    
    Returns:
        np.ndarray: 补偿后的幅度（线性增益）
    """
    from scipy.interpolate import interp1d
    
    selftest_freq = selftest_data['frequencies']
    selftest_mag = selftest_data['magnitude']
    
    # 检查频率范围是否覆盖
    exp_min, exp_max = exp_freq.min(), exp_freq.max()
    self_min, self_max = selftest_freq.min(), selftest_freq.max()
    
    if exp_min < self_min or exp_max > self_max:
        logger.warning(
            f"⚠️ 实验数据频率范围 [{exp_min:.2f}, {exp_max:.2f}] Hz "
            f"超出自测试范围 [{self_min:.2f}, {self_max:.2f}] Hz"
        )
    
    # 使用线性插值（对数空间）
    # 先转换到dB空间进行插值，避免线性空间的数值问题
    selftest_db = 20 * np.log10(selftest_mag + 1e-20)
    
    # 创建插值函数（extrapolate='extrapolate' 允许外推）
    interp_func = interp1d(
        selftest_freq, 
        selftest_db, 
        kind='linear', 
        bounds_error=False,
        fill_value='extrapolate'
    )
    
    # 在实验频点处插值
    selftest_db_interp = interp_func(exp_freq)
    selftest_mag_interp = np.power(10.0, selftest_db_interp / 20.0)
    
    # 执行补偿（相除）
    compensated_mag = exp_mag / (selftest_mag_interp + 1e-20)
    
    return compensated_mag
```

#### 修改点7：重构 `_generate_plots()` 函数（核心修改）

**原函数位置**：第285-401行

**修改策略**：
1. 保留原有的单文件对比逻辑（向后兼容）
2. 新增多文件对比逻辑（C05需求）
3. 根据配置选择使用哪种模式

**新的函数结构**：

```python
def _generate_plots(self, freq_response, dense_weights):
    """生成幅频响应图（支持多种对比模式）
    
    模式1（旧）：单文件对比 (mode='single_file')
    - 从一个Excel文件读取所有通道数据（列名：D{layer}_{ch}_GAIN/B1）
    - 使用 semilogx 或 loglog（根据配置）
    - 数据单位：线性增益或dB（根据配置）
    
    模式2（新）：多文件对比 (mode='multi_file')  ⬅️ C05需求
    - 从多个Excel文件读取各通道数据
    - 使用自测试数据进行补偿
    - 强制使用 loglog 坐标系
    - 数据单位：dB
    """
    logger.info("生成幅频响应图...")
    
    # 决定使用哪种对比模式
    if self.exp_comp_enable and self.exp_comp_mode == 'multi_file':
        # 新模式：多文件对比（C05需求）
        return self._generate_plots_multi_file(freq_response, dense_weights)
    else:
        # 旧模式：单文件对比（保持向后兼容）
        return self._generate_plots_single_file(freq_response, dense_weights)
```

**拆分为两个子函数**：

##### 子函数1：`_generate_plots_single_file()` （保留旧逻辑）

```python
def _generate_plots_single_file(self, freq_response, dense_weights):
    """单文件对比模式（旧逻辑，向后兼容）"""
    logger.info("使用单文件对比模式...")
    
    # 【保留原有的全部逻辑，不做修改】
    # 这里是原 _generate_plots() 函数的全部代码（第285-401行）
    # ...（省略，与原代码完全一致）
    
    return plots
```

##### 子函数2：`_generate_plots_multi_file()` （新增，C05需求）

```python
def _generate_plots_multi_file(self, freq_response, dense_weights):
    """多文件对比模式（C05需求）
    
    特性：
    - 从目录扫描对应层的所有通道文件
    - 使用自测试数据进行补偿
    - loglog 坐标系
    - dB 单位
    - 上下布局：上图实验，下图仿真
    """
    logger.info("使用多文件对比模式（C05）...")
    
    analysis_layer = dense_weights.get('analysis_layer', 1)
    
    # ========== 1. 准备理论数据 ==========
    theo_freq = freq_response['frequencies']
    theo_mag_db_list = freq_response['magnitude_db']  # 已经是dB
    n_channels = len(theo_mag_db_list)
    
    output_labels = [f'D{analysis_layer}_{i+1}' for i in range(n_channels)]
    
    logger.info(f"理论数据: {n_channels} 个通道, {len(theo_freq)} 个频点")
    
    # ========== 2. 加载自测试数据 ==========
    try:
        selftest_data = self._load_selftest_data()
    except Exception as e:
        logger.error(f"加载自测试数据失败: {e}")
        logger.warning("将跳过实验对比，仅绘制理论曲线")
        selftest_data = None
    
    # ========== 3. 扫描并加载实验数据 ==========
    exp_data_dict = {}  # {通道号: {'frequencies': [...], 'magnitude_db': [...]}}
    
    if selftest_data is not None:
        try:
            channel_files = self._scan_experiment_files(analysis_layer)
            
            if not channel_files:
                logger.warning(f"未找到层{analysis_layer}的实验数据，将跳过实验对比")
            else:
                # 逐个加载通道数据
                for channel, file_path in channel_files.items():
                    try:
                        # 加载原始数据
                        raw_data = self._load_experiment_channel_data(file_path)
                        
                        # 自测试补偿
                        compensated_mag = self._compensate_with_selftest(
                            raw_data['frequencies'],
                            raw_data['magnitude'],
                            selftest_data
                        )
                        
                        # 转换为dB
                        compensated_db = 20 * np.log10(compensated_mag + 1e-20)
                        
                        exp_data_dict[channel] = {
                            'frequencies': raw_data['frequencies'],
                            'magnitude_db': compensated_db
                        }
                        
                        logger.info(f"   ✅ 通道{channel}: {len(raw_data['frequencies'])} 个频点")
                        
                    except Exception as e:
                        logger.error(f"   ❌ 通道{channel} 加载失败: {e}")
                        continue
                
                logger.info(f"✅ 成功加载 {len(exp_data_dict)} 个通道的实验数据")
        
        except Exception as e:
            logger.error(f"扫描实验数据失败: {e}")
            exp_data_dict = {}
    
    # ========== 4. 绘制对比图 ==========
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    
    # 颜色映射
    cmap = mpl.cm.get_cmap('tab10', n_channels) if n_channels <= 10 else mpl.cm.get_cmap('turbo', n_channels)
    colors = [cmap(i) for i in range(n_channels)]
    
    plots = []
    
    if exp_data_dict:
        # 有实验数据：上下布局
        fig, (ax_exp, ax_theo) = plt.subplots(2, 1, figsize=(12, 10))
        
        # ===== 上图：实验数据 =====
        for channel, data in sorted(exp_data_dict.items()):
            color_idx = channel - 1
            if color_idx >= n_channels:
                color_idx = n_channels - 1
            
            ax_exp.loglog(
                data['frequencies'], 
                np.power(10, data['magnitude_db'] / 20),  # dB转回线性用于loglog
                color=colors[color_idx],
                linewidth=1.5,
                label=f'D{analysis_layer}_{channel}',
                alpha=0.8
            )
        
        ax_exp.set_title(
            f'{self.model_project_name} Dense#{analysis_layer} - 实验测量（补偿后）',
            fontsize=12,
            fontweight='bold'
        )
        ax_exp.set_xlabel('频率 (Hz)', fontsize=10)
        ax_exp.set_ylabel('幅度 (线性, loglog)', fontsize=10)
        ax_exp.grid(True, which='both', alpha=0.3, linestyle='--')
        ax_exp.legend(fontsize=8, ncol=min(3, n_channels), loc='best')
        
        # ===== 下图：理论数据 =====
        for i, (mag_db, lbl) in enumerate(zip(theo_mag_db_list, output_labels)):
            ax_theo.loglog(
                theo_freq,
                np.power(10, mag_db / 20),  # dB转回线性用于loglog
                color=colors[i],
                linewidth=1.5,
                label=lbl,
                alpha=0.8
            )
        
        ax_theo.set_title(
            f'{self.model_project_name} Dense#{analysis_layer} - 理论仿真',
            fontsize=12,
            fontweight='bold'
        )
        ax_theo.set_xlabel('频率 (Hz)', fontsize=10)
        ax_theo.set_ylabel('幅度 (线性, loglog)', fontsize=10)
        ax_theo.grid(True, which='both', alpha=0.3, linestyle='--')
        ax_theo.legend(fontsize=8, ncol=min(3, n_channels), loc='best')
        
        # 统一y轴范围（可选）
        all_exp_mag = np.concatenate([
            np.power(10, d['magnitude_db'] / 20) for d in exp_data_dict.values()
        ])
        all_theo_mag = np.concatenate([
            np.power(10, m / 20) for m in theo_mag_db_list
        ])
        all_mag = np.concatenate([all_exp_mag, all_theo_mag])
        
        y_min = max(1e-6, np.nanmin(all_mag) * 0.5)
        y_max = np.nanmax(all_mag) * 2.0
        
        ax_exp.set_ylim(y_min, y_max)
        ax_theo.set_ylim(y_min, y_max)
        
        plt.tight_layout()
        
        plot_path = self.output_path / 'plots' / 'frequency_response_comparison_multi.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        plots.append(str(plot_path))
        logger.info(f"📊 对比图已保存: {plot_path}")
    
    else:
        # 无实验数据：仅绘制理论曲线
        logger.warning("⚠️ 无实验数据，仅绘制理论曲线")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for i, (mag_db, lbl) in enumerate(zip(theo_mag_db_list, output_labels)):
            ax.loglog(
                theo_freq,
                np.power(10, mag_db / 20),
                color=colors[i],
                linewidth=1.5,
                label=lbl
            )
        
        ax.set_title(f'{self.model_project_name} Dense#{analysis_layer} - 理论仿真', fontsize=12)
        ax.set_xlabel('频率 (Hz)', fontsize=10)
        ax.set_ylabel('幅度 (线性, loglog)', fontsize=10)
        ax.grid(True, which='both', alpha=0.3)
        ax.legend(fontsize=8, ncol=min(3, n_channels))
        
        plt.tight_layout()
        
        plot_path = self.output_path / 'plots' / 'frequency_response.png'
        plt.savefig(plot_path, dpi=300)
        plt.close(fig)
        
        plots.append(str(plot_path))
        logger.info(f"📊 理论图已保存: {plot_path}")
    
    return plots
```

---

## 五、测试与验证

### 5.1 单元测试

**测试文件**：`tests/test_wnet5_experiment_comparison.py`

```python
import pytest
import numpy as np
from pathlib import Path
from visualization.wnet5_circuit_validator import WNET5CircuitValidator

def test_parse_experiment_filename_underscore():
    """测试下划线格式的文件名解析"""
    validator = WNET5CircuitValidator({...}, Path('output'))
    
    result = validator._parse_experiment_filename(
        'output_20251104_085010_SVF-W_DENSE2_2_震级1.0.xlsx'
    )
    
    assert result is not None
    assert result['layer'] == 2
    assert result['channel'] == 2
    assert result['timestamp'] == '20251104_085010'
    assert result['magnitude'] == 1.0

def test_parse_experiment_filename_hyphen():
    """测试连字符格式的文件名解析"""
    validator = WNET5CircuitValidator({...}, Path('output'))
    
    result = validator._parse_experiment_filename(
        'output_20251104_135448_SVF-W_DENSE3-2_震级1.0.xlsx'
    )
    
    assert result is not None
    assert result['layer'] == 3
    assert result['channel'] == 2

def test_parse_experiment_filename_invalid():
    """测试无效文件名"""
    validator = WNET5CircuitValidator({...}, Path('output'))
    
    result = validator._parse_experiment_filename('invalid_filename.xlsx')
    assert result is None

def test_compensate_with_selftest():
    """测试自测试补偿"""
    validator = WNET5CircuitValidator({...}, Path('output'))
    
    # 模拟数据
    exp_freq = np.array([10, 20, 50, 100])
    exp_mag = np.array([1.0, 2.0, 3.0, 4.0])
    
    selftest_data = {
        'frequencies': np.array([10, 20, 50, 100]),
        'magnitude': np.array([0.5, 1.0, 1.5, 2.0])
    }
    
    compensated = validator._compensate_with_selftest(exp_freq, exp_mag, selftest_data)
    
    # 验证补偿结果
    expected = exp_mag / selftest_data['magnitude']
    np.testing.assert_array_almost_equal(compensated, expected)
```

### 5.2 集成测试

#### 测试步骤1：准备测试配置

```bash
# 创建测试项目配置
mkdir -p ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1_test

cat > ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1_test/config.json <<EOF
{
  "task_info": {
    "task_type": "wnet5-circuit-validation",
    "description": "WNET5电路验证 - 多文件对比测试"
  },
  "model_project_name": "WNET5q1h2u6l3",
  "analysis_layer": 1,
  "frequency_range": {
    "start_freq": 2,
    "stop_freq": 500
  },
  "experiment_comparison": {
    "enable": true,
    "mode": "multi_file",
    "experiment_data_dir": "exam_data/SVF-W_DENSE",
    "selftest_file": "exam_data/SVF-W_DENSE/output_20251103_085135_sweep_selftest_震级1.0.xlsx",
    "plot_config": {
      "coordinate_system": "loglog",
      "y_unit": "dB"
    }
  }
}
EOF
```

#### 测试步骤2：运行验证

```bash
# 运行第1层验证（C05需求）
python cli.py ep ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1_test

# 检查输出
ls -la ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1_test/data/plots/
# 应该看到: frequency_response_comparison_multi.png

# 查看日志
tail -f logs/metnl.log
```

#### 测试步骤3：验证输出

**预期输出文件**：
```
ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1_test/data/
├── plots/
│   └── frequency_response_comparison_multi.png  ⬅️ 上下对比图
├── reports/
│   └── analysis_report.json
└── results.json
```

**预期日志输出**：
```
[INFO] 生成幅频响应图...
[INFO] 使用多文件对比模式（C05）...
[INFO] 理论数据: 6 个通道, 1000 个频点
[INFO] 📂 加载自测试数据: exam_data/SVF-W_DENSE/output_20251103_085135_sweep_selftest_震级1.0.xlsx
[INFO] ✅ 自测试数据加载成功: 500 个频点
[INFO] 🔍 扫描实验数据目录: exam_data/SVF-W_DENSE
[INFO]    目标层: 1
[INFO]    ✅ 找到: 层1通道1 - output_20251103_145209_SVF-W_DENSE1_1_震级1.0.xlsx
[INFO]    ✅ 找到: 层1通道2 - output_20251103_150634_SVF-W_DENSE1_2_震级1.0.xlsx
[INFO]    ✅ 找到: 层1通道3 - output_20251103_152754_SVF-W_DENSE1_3_震级1.0.xlsx
[INFO]    ✅ 找到: 层1通道4 - output_20251103_155128_SVF-W_DENSE1_4_震级1.0.xlsx
[INFO]    ✅ 找到: 层1通道5 - output_20251103_185204_SVF-W_DENSE1_5_震级1.0.xlsx
[INFO]    ✅ 找到: 层1通道6 - output_20251103_193315_SVF-W_DENSE1_6_震级1.0.xlsx
[INFO] ✅ 共找到 6 个通道的实验数据
[INFO]    ✅ 通道1: 500 个频点
[INFO]    ✅ 通道2: 500 个频点
[INFO]    ✅ 通道3: 500 个频点
[INFO]    ✅ 通道4: 500 个频点
[INFO]    ✅ 通道5: 500 个频点
[INFO]    ✅ 通道6: 500 个频点
[INFO] ✅ 成功加载 6 个通道的实验数据
[INFO] 📊 对比图已保存: .../frequency_response_comparison_multi.png
```

### 5.3 回归测试

**测试向后兼容性**：

```bash
# 测试旧的单文件对比模式（不应受影响）
cat > ex_projects/inference/wnet5-circuit-validation/backward_compat_test/config.json <<EOF
{
  "model_project_name": "WNET5q1h2u6l3",
  "analysis_layer": 1,
  "frequency_range": {"start_freq": 2, "stop_freq": 500},
  "compare_with_experiment": "path/to/single/file.xlsx"
}
EOF

python cli.py ep ex_projects/inference/wnet5-circuit-validation/backward_compat_test
# 应该使用旧的单文件对比逻辑，不报错
```

---

## 六、实施计划

### 6.1 开发阶段（预计4-5小时）

#### 阶段1：新增辅助函数（1.5小时）
- [x] `_load_selftest_data()` - 加载自测试数据
- [x] `_parse_experiment_filename()` - 解析文件名
- [x] `_scan_experiment_files()` - 扫描实验文件
- [x] `_load_experiment_channel_data()` - 加载通道数据
- [x] `_compensate_with_selftest()` - 自测试补偿
- [x] 编写单元测试

#### 阶段2：重构绘图函数（1.5小时）
- [x] 将 `_generate_plots()` 拆分为两个子函数
- [x] `_generate_plots_single_file()` - 保留旧逻辑
- [x] `_generate_plots_multi_file()` - 新增C05逻辑
- [x] 修改 `__init__()` 加载配置

#### 阶段3：集成测试（1小时）
- [x] 创建测试配置文件
- [x] 运行第1层验证
- [x] 验证输出图表和日志
- [x] 测试向后兼容性

#### 阶段4：文档更新（0.5小时）
- [x] 更新 `doc/summary.md`
- [x] 更新使用说明

### 6.2 验证阶段（预计1小时）

- [ ] 测试第2层（`analysis_layer: 2`）
- [ ] 测试第3层（`analysis_layer: 3`）
- [ ] 测试第4层（`analysis_layer: 4`）
- [ ] 验证不同层的对比图
- [ ] 检查自测试补偿是否正确

**总计**：约5-6小时

---

## 七、风险评估与应对

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|---------|
| Excel文件格式不一致 | 高 | 中 | 增强列名匹配逻辑，支持多种列名格式 |
| 自测试数据频率范围不足 | 中 | 中 | 使用外推插值，并记录警告日志 |
| 实验文件命名不规范 | 中 | 低 | 支持多种命名模式，提供详细解析失败日志 |
| 频点不对齐导致插值误差 | 低 | 中 | 使用对数空间插值，减少误差 |
| 向后兼容性破坏 | 高 | 极低 | 保持旧逻辑完全不变，新增独立分支 |

---

## 八、关键技术要点

### 8.1 loglog 坐标系实现

**matplotlib 调用**：
```python
ax.loglog(x, y)  # x轴和y轴都使用对数刻度
```

**注意事项**：
- 数据必须为正值（否则无法取对数）
- 建议先在线性空间计算，再用 `np.clip()` 确保正值
- dB 转线性：`linear = 10^(dB/20)`

### 8.2 自测试补偿算法

**补偿公式**：
```
compensated_mag[f] = measured_mag[f] / selftest_mag[f]
```

**实现要点**：
1. **频点对齐**：使用插值使自测试数据与测量数据的频点一致
2. **插值方法**：在 dB 空间进行线性插值（减少误差）
3. **边界处理**：允许外推（`fill_value='extrapolate'`），但记录警告

**代码示例**：
```python
from scipy.interpolate import interp1d

# 转dB空间
selftest_db = 20 * np.log10(selftest_mag + 1e-20)

# 创建插值函数
interp_func = interp1d(
    selftest_freq, 
    selftest_db, 
    kind='linear',
    fill_value='extrapolate'
)

# 插值到实验频点
selftest_db_interp = interp_func(exp_freq)
selftest_mag_interp = 10 ** (selftest_db_interp / 20)

# 执行补偿
compensated = exp_mag / selftest_mag_interp
```

### 8.3 文件名解析正则表达式

**支持的格式**：
1. `output_{时间戳}_SVF-W_DENSE{层号}_{通道号}_震级1.0.xlsx`
2. `output_{时间戳}_SVF-W_DENSE{层号}-{通道号}_震级1.0.xlsx`

**正则表达式**：
```python
# 格式1：下划线
pattern1 = r'output_(\d+_\d+)_SVF-W_DENSE(\d+)_(\d+)_震级([\d.]+)\.xlsx'

# 格式2：连字符
pattern2 = r'output_(\d+_\d+)_SVF-W_DENSE(\d+)-(\d+)_震级([\d.]+)\.xlsx'
```

---

## 九、配置示例

### 9.1 第1层验证配置

```json
{
  "task_info": {
    "task_type": "wnet5-circuit-validation",
    "description": "WNET5电路验证 - Dense层1"
  },
  "model_project_name": "WNET5q1h2u6l3",
  "analysis_layer": 1,
  "frequency_range": {
    "start_freq": 2,
    "stop_freq": 500
  },
  "experiment_comparison": {
    "enable": true,
    "mode": "multi_file",
    "experiment_data_dir": "exam_data/SVF-W_DENSE",
    "selftest_file": "exam_data/SVF-W_DENSE/output_20251103_085135_sweep_selftest_震级1.0.xlsx",
    "plot_config": {
      "coordinate_system": "loglog",
      "y_unit": "dB"
    }
  }
}
```

### 9.2 第2层验证配置

```json
{
  "task_info": {
    "task_type": "wnet5-circuit-validation",
    "description": "WNET5电路验证 - Dense层2"
  },
  "model_project_name": "WNET5q1h2u6l3",
  "analysis_layer": 2,
  "frequency_range": {
    "start_freq": 2,
    "stop_freq": 500
  },
  "experiment_comparison": {
    "enable": true,
    "mode": "multi_file",
    "experiment_data_dir": "exam_data/SVF-W_DENSE",
    "selftest_file": "exam_data/SVF-W_DENSE/output_20251103_085135_sweep_selftest_震级1.0.xlsx",
    "plot_config": {
      "coordinate_system": "loglog",
      "y_unit": "dB"
    }
  }
}
```

### 9.3 向后兼容配置（旧模式）

```json
{
  "model_project_name": "WNET5q1h2u6l3",
  "analysis_layer": 1,
  "frequency_range": {
    "start_freq": 2,
    "stop_freq": 500
  },
  "compare_with_experiment": "path/to/experiment_data.xlsx"
}
```

---

## 十、输出结果示例

### 10.1 文件结构

```
ex_projects/inference/wnet5-circuit-validation/WNET5q1h2u6l3_layer1/
├── config.json                                    # 配置文件
└── data/
    ├── plots/
    │   └── frequency_response_comparison_multi.png  # ⬅️ 新增：上下对比图
    ├── numerics/
    │   └── frequency_response.json                # 频率响应数据
    ├── reports/
    │   └── analysis_report.json                   # 分析报告
    └── results.json                                # 汇总结果
```

### 10.2 对比图说明

**frequency_response_comparison_multi.png**：

```
┌────────────────────────────────────────────────────┐
│  WNET5q1h2u6l3 Dense#1 - 实验测量（补偿后）        │
│  ┌──────────────────────────────────────────────┐  │
│  │  • 上图：实验数据（6条曲线）                 │  │
│  │  • 坐标系：loglog                            │  │
│  │  • 已除以自测试频响                          │  │
│  │  • 单位：线性增益（对数刻度显示）            │  │
│  └──────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────┤
│  WNET5q1h2u6l3 Dense#1 - 理论仿真                  │
│  ┌──────────────────────────────────────────────┐  │
│  │  • 下图：仿真数据（6条曲线）                 │  │
│  │  • 坐标系：loglog                            │  │
│  │  • 传递函数理论计算                          │  │
│  │  • 单位：线性增益（对数刻度显示）            │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

**图表特性**：
- **上下布局**：上图实验，下图仿真
- **统一范围**：两图的x轴和y轴范围一致，便于对比
- **颜色对应**：相同通道使用相同颜色
- **清晰标注**：每条曲线都有标签（D1_1, D1_2, ...）

---

## 十一、依赖库要求

### 11.1 Python 库

```python
# 核心依赖（已有）
numpy>=1.20.0
matplotlib>=3.3.0
pandas>=1.2.0

# 新增依赖
scipy>=1.6.0           # 用于插值（interp1d）
openpyxl>=3.0.0        # 用于读取 Excel 文件
```

### 11.2 安装命令

```bash
pip install scipy openpyxl
```

---

## 十二、FAQ

### Q1：如果某一层缺少部分通道的实验数据怎么办？

**A**：系统会自动跳过缺失的通道，仅绘制有数据的通道。日志会记录：
```
[INFO] ✅ 共找到 4 个通道的实验数据  # 6个通道只找到4个
[WARNING] ⚠️ 通道5和6的实验数据缺失，将不在实验图中显示
```

### Q2：自测试文件的频率范围不足怎么办？

**A**：系统会使用外推插值（`fill_value='extrapolate'`），并记录警告：
```
[WARNING] ⚠️ 实验数据频率范围 [2.0, 500.0] Hz 超出自测试范围 [10.0, 400.0] Hz
```
建议确保自测试文件覆盖所需的完整频率范围。

### Q3：如何切换回旧的单文件对比模式？

**A**：有两种方式：
1. **不配置 experiment_comparison**（自动使用旧模式）
2. **设置 mode='single_file'**：
   ```json
   "experiment_comparison": {
     "enable": true,
     "mode": "single_file"
   },
   "compare_with_experiment": "path/to/file.xlsx"
   ```

### Q4：loglog 坐标系显示异常怎么办？

**A**：检查数据是否包含零值或负值：
```python
# 确保数据为正值
magnitude = np.clip(magnitude, 1e-20, None)
```

### Q5：如何验证自测试补偿是否正确？

**A**：可以在日志中查看补偿前后的数值范围：
```
[INFO] 补偿前: 0.1 - 10.0
[INFO] 补偿后: 0.5 - 5.0
```
或手动计算几个频点验证。

---

## 十三、总结

### 13.1 实现的功能

✅ **自动扫描实验数据**：根据层号自动匹配所有通道文件  
✅ **自测试补偿**：除以自测试频响，得到补偿后的幅频响应  
✅ **loglog 坐标系**：x轴和y轴都使用对数刻度  
✅ **上下对比布局**：上图实验，下图仿真，便于对比  
✅ **向后兼容**：不影响现有的单文件对比功能  
✅ **健壮的错误处理**：文件缺失、格式错误等情况都有友好提示

### 13.2 方案优势

1. **最小侵入**：在现有代码基础上扩展，不破坏原有逻辑
2. **灵活配置**：通过配置文件控制对比模式和参数
3. **清晰日志**：详细记录数据加载、补偿、绘图过程
4. **易于维护**：功能模块化，每个函数职责单一
5. **可扩展**：未来可以轻松添加新的对比模式或补偿算法

### 13.3 下一步工作

1. 实施代码修改（按照第四节的详细方案）
2. 编写单元测试
3. 运行集成测试（第1/2/3/4层）
4. 更新文档（doc/summary.md）
5. 与实验团队确认对比结果

---

**文档创建日期**：2025年11月4日  
**对应需求**：C05  
**相关文档**：
- `doc/plan/20251104/wnet5_multilayer_circuit_validation_implementation_plan.md`（C04）
- `doc/guide/user_command.md`（原始需求）
