# Wave误差分析改进实施方案

## 问题背景

当前的误差分析只计算了数值误差，并生成了JSON报告和可视化图表。但缺少误差波形文件的生成，不利于深入分析误差的时域特征。需要生成误差wave文件，保持与原始wave相同的结构。

## 需求分析

1. **核心需求**：
   - 两个wave文件做差运算，生成误差wave文件
   - 误差wave保存到`error_layers/`目录，与`spice_layers/`具有相同的目录结构
   - 保持原始wave的元数据（采样率、通道名、记录结构等）

2. **技术要求**：
   - 最小化代码修改
   - 充分利用现有wave基础设施
   - 保持与现有系统的兼容性

## 现状分析

### Wave基础设施能力评估

1. **已有功能**：
   - WaveData类支持乘法运算（`__mul__`）
   - 完整的文件读写功能（save/load）
   - 灵活的元数据系统
   - 记录级别的数据管理

2. **缺失功能**：
   - 不支持wave间的减法运算（`__sub__`）
   - 没有wave间的算术运算框架

3. **当前误差计算实现**（cli.py:536）：
   ```python
   error = nn_output - spice_output  # 仅numpy数组运算
   ```

## 实施方案

### 方案一：扩展WaveData类，添加减法运算支持（推荐）

**实现思路**：
1. 在`WaveData`类中添加`__sub__`方法，支持两个wave对象相减
2. 在误差分析时直接使用wave对象的减法运算
3. 保存误差wave到`error_layers/`目录

**优点**：
- 符合面向对象设计原则
- 代码复用性高，未来可扩展其他运算
- 使用方式直观：`error_wave = nn_wave - spice_wave`
- 保持wave完整的元数据结构

**实现要点**：
```python
# WaveData类新增方法
def __sub__(self, other: 'WaveData') -> 'WaveData':
    """实现两个WaveData对象的减法运算"""
    # 1. 验证两个wave的兼容性（记录数、采样率等）
    # 2. 逐记录进行减法运算
    # 3. 创建新的WaveData对象，保留元数据
    # 4. 返回误差wave对象
```

**使用方式**：
```python
# 在cli.py的误差分析中
error_wave = nn_wave - spice_wave
error_path = os.path.join(error_layers_dir, f"layer_{i+1}.wave")
wave_processor.save_waveform(error_path, error_wave)
```

### 方案二：在误差分析函数中直接实现

**实现思路**：
1. 在`_analyze_inference_errors`中，计算误差后直接构建WaveData对象
2. 复制原始wave的元数据，替换数据为误差数据
3. 保存到`error_layers/`目录

**优点**：
- 不需要修改wave基础设施
- 实现快速，改动范围小
- 对现有系统影响最小

**缺点**：
- 代码复用性差
- 不符合OOP设计原则
- 未来扩展性有限

**实现要点**：
```python
# 在误差计算后创建误差wave
error_wave = WaveData(
    description=f"Error between NN and SPICE (Layer {i+1})",
    version=nn_data.version,
    # ... 其他元数据
)

# 为每个记录创建误差记录
for j, (nn_rec, spice_rec) in enumerate(zip(nn_data.records, spice_data.records)):
    error_data = nn_rec.data - spice_rec.data
    error_record = WaveRecord(
        data=error_data,
        sample_rate=nn_rec.sample_rate,
        channel_names=nn_rec.channel_names,
        # ... 其他属性
    )
    error_wave.add_record(error_record)
```

### 方案三：创建WaveArithmetic工具类

**实现思路**：
1. 创建独立的`WaveArithmetic`工具类
2. 提供静态方法处理wave间的各种运算
3. 在误差分析中调用该工具类

**优点**：
- 模块化设计，职责分离
- 易于扩展更多运算类型
- 不影响核心WaveData类

**缺点**：
- 增加了系统复杂度
- 使用方式不如运算符重载直观

**实现要点**：
```python
class WaveArithmetic:
    @staticmethod
    def subtract(wave1: WaveData, wave2: WaveData) -> WaveData:
        """计算两个wave的差"""
        # 实现逻辑
    
    @staticmethod
    def add(wave1: WaveData, wave2: WaveData) -> WaveData:
        """计算两个wave的和"""
        # 实现逻辑
```

## 推荐方案

**推荐采用方案一**，原因如下：

1. **设计合理性**：扩展WaveData类符合面向对象设计原则，运算符重载是Python的惯用方式
2. **使用便利性**：`wave1 - wave2`的语法直观易懂
3. **长期价值**：为wave基础设施增加了有价值的功能，未来可能需要其他运算
4. **代码优雅性**：避免在业务代码中处理底层数据操作

## 实施步骤

1. **第一步**：在`calibration_analyzer/wavedata.py`中为`WaveData`类添加`__sub__`方法
2. **第二步**：修改`cli.py`的`_analyze_inference_errors`方法，使用wave减法运算
3. **第三步**：创建`error_layers/`目录并保存误差wave文件
4. **第四步**：更新误差分析报告，添加误差wave文件路径信息
5. **第五步**：测试验证新功能的正确性

## 注意事项

1. **兼容性检查**：减法运算前需验证两个wave的兼容性（记录数、采样率、通道数等）
2. **错误处理**：妥善处理不兼容的wave相减情况
3. **元数据更新**：误差wave需要适当的描述和元数据
4. **性能考虑**：对于大型wave文件，需要考虑内存使用

## 预期成果

实施后的目录结构：
```
projects/WNET5q0.5h2u6l3/data/inference/
├── nn_layers/
│   └── layer_1.wave ... layer_5.wave
├── spice_layers/
│   └── layer_1.wave ... layer_5.wave
├── error_layers/        # 新增
│   └── layer_1.wave ... layer_5.wave
├── input.wave
├── error_analysis.json
└── inference_comparison.png
```

每个误差wave文件包含：
- 对应层的误差数据（nn - spice）
- 原始wave的采样率和通道信息
- 适当的描述和元数据
- 与原始wave相同的记录结构