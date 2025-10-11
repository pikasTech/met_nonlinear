# Wave数据生成功能调研报告

## 1. 现有架构分析

### 1.1 cli.py 命令行参数处理架构

当前 `cli.py` 使用简单的命令行参数解析机制：

```python
# 主要任务类型
task_type = 'train'  # 默认
if '-e' in sys.argv:
    task_type = 'evaluate'
if '-c' in sys.argv:
    task_type = 'clean'
if '-m' in sys.argv:
    task_type = 'model_info'
if '-l' in sys.argv:
    task_type = 'lut'
if '-i' in sys.argv:
    task_type = 'inference'
if '-a' in sys.argv:
    task_type = 'analyze'
```

**架构特点：**
- 使用简单的 `sys.argv` 解析
- 支持项目名称和通配符（如 `FRIKAN*`）
- 支持批量处理（`-all` 参数）
- 支持 force 模式（`-f` 或 `--force`）
- 通过 `ProjectManager` 类管理项目生命周期

### 1.2 数据集类和 export_to_wave 实现

**数据集类层次结构：**
```
Dataset_COMP (基类)
├── Dataset_COMP_MET (MET数据集)
├── Dataset_COMP_PE (PE数据集)
├── Dataset_COMP_Alias (Alias数据集)
└── Dataset_COMP_AliasSimu (AliasSimu数据集)
```

**export_to_wave 实现方式：**
- 位于 `Dataset_COMP` 基类中
- 使用 `calibration_analyzer.waveprocessor` 库
- 支持压缩和元数据
- 生成文件名格式：`dataset_{self.type}_{input|output_original}.wave`

**关键实现代码：**
```python
def export_to_wave(self, output_folder='./wave_output', description=None, author=None, compress=True):
    # 创建 WaveData 和 WaveRecord 对象
    input_wave_data = WaveData(...)
    output_ori_wave_data = WaveData(...)
    
    # 遍历所有震级和频率组合
    for mag_idx in range(self.magn_num):
        for freq_idx in range(self.freq_num):
            # 创建波形记录并添加到波形数据中
            ...
    
    # 保存为 .wave 文件
    processor.save_waveform(input_wave_path, input_wave_data, compress=compress)
    processor.save_waveform(output_ori_wave_path, output_ori_wave_data, compress=compress)
```

### 1.3 项目配置和数据加载流程

**配置系统：**
- `Config` 类管理所有配置参数
- 支持 JSON 序列化和反序列化
- 关键配置：`dataset_type`、`data_path`、`data_base_path`

**数据加载流程：**
1. `ProjectManager.prepare_dataset_and_model()` 调用
2. `ModelEngine.load_dataset(dataset_type)` 根据类型加载数据
3. `ModelEngine.prepare_training_data()` 准备训练数据
4. 在 `prepare_training_data()` 中调用 `export_to_wave()`

**当前调用路径：**
```
cli.py -> ProjectManager.evaluate() -> ModelEngine.prepare_training_data() -> dataset.export_to_wave()
```

### 1.4 测试架构分析

**现有测试结构：**
- 使用 `unittest` 框架
- 测试文件位于 `tests/` 目录
- 支持跳过缺失依赖的测试
- 包含集成测试和单元测试

**测试特点：**
- 使用 `@unittest.skipIf` 装饰器处理依赖
- 创建临时目录进行测试
- 支持模拟项目配置

## 2. 需求分析

### 2.1 功能需求
1. **独立的 wave 数据生成命令**：`cli.py -w PROJECT_NAME`
2. **支持所有数据集类型**：MET、PE、Alias、AliasSimu
3. **可配置输出目录**：支持自定义输出路径
4. **支持 pytest 测试**：完整的测试覆盖
5. **保持代码简洁**：核心实现不在 `cli.py` 中

### 2.2 设计约束
1. **最大限度重用现有代码**：复用数据集类和配置系统
2. **保持架构一致性**：符合现有的 ProjectManager 模式
3. **支持批量处理**：与其他功能一致的批量处理能力
4. **错误处理**：完善的异常处理机制

## 3. 设计方案

### 方案1：委托模式（推荐）

**核心思想：**
在 `ProjectManager` 中添加 `generate_wave_data()` 方法，通过委托模式调用数据集的 `export_to_wave()` 方法。

**实现架构：**
```
cli.py (-w参数)
    ↓
ProjectManager.generate_wave_data()
    ↓
DatasetWaveGenerator (新建辅助类)
    ↓
Dataset_COMP.export_to_wave()
```

**优点：**
- 完全重用现有的数据集加载逻辑
- 保持 `cli.py` 简洁
- 架构一致性好
- 易于测试和维护

**实现文件：**
- `core/wave_generator.py` - 新建辅助类
- `cli.py` - 添加 `-w` 参数支持
- `tests/test_wave_generator.py` - 测试文件

### 方案2：独立工具模式

**核心思想：**
创建独立的 `WaveDataTool` 类，提供完整的 wave 数据生成功能。

**实现架构：**
```
cli.py (-w参数)
    ↓
WaveDataTool (新建工具类)
    ↓
直接使用 Dataset_COMP_* 类
```

**优点：**
- 功能模块化程度高
- 可以独立使用
- 便于扩展更多 wave 相关功能

**缺点：**
- 需要重复部分项目配置逻辑
- 代码复用度相对较低

### 方案3：扩展现有评估模式

**核心思想：**
扩展现有的 `evaluate()` 方法，添加仅生成 wave 数据的选项。

**实现架构：**
```
cli.py (-w参数)
    ↓
ProjectManager.evaluate(wave_only=True)
    ↓
简化的数据准备和 export_to_wave()
```

**优点：**
- 代码改动最小
- 完全重用现有逻辑

**缺点：**
- 耦合度较高
- 职责不够清晰

## 4. 推荐方案详细设计

### 4.1 方案1 - 委托模式详细设计

**核心类设计：**

```python
# core/wave_generator.py
class DatasetWaveGenerator:
    \"\"\"数据集波形生成器\"\"\"
    
    def __init__(self, project_manager):
        self.project_manager = project_manager
        self.config = project_manager.config
    
    def generate_wave_data(self, output_folder=None, dataset_filter=None):
        \"\"\"
        生成波形数据
        
        Args:
            output_folder: 输出目录，默认为项目目录下的 wave_output
            dataset_filter: 数据集过滤器，可选择生成哪些数据集
        \"\"\"
        # 1. 加载数据集
        # 2. 准备数据
        # 3. 调用 export_to_wave
        # 4. 返回生成的文件路径
    
    def _load_and_prepare_dataset(self):
        \"\"\"加载和准备数据集\"\"\"
        # 重用 ModelEngine 的逻辑
    
    def _validate_output_folder(self, output_folder):
        \"\"\"验证输出目录\"\"\"
        # 创建目录、权限检查等
```

**命令行参数扩展：**

```python
# cli.py 中添加
elif task_type == 'wave':
    try:
        project = ProjectManager(project_path)
        project.generate_wave_data(force=force_mode)
        print(f"Wave data generated for project '{project_name}'")
    except Exception as e:
        print(f"Error occurred while generating wave data for project '{project_name}': {e}")
        traceback.print_exc()
        continue
```

**ProjectManager 扩展：**

```python
# cli.py 中的 ProjectManager 类
def generate_wave_data(self, force=False, output_folder=None):
    \"\"\"生成波形数据\"\"\"
    from core.wave_generator import DatasetWaveGenerator
    
    generator = DatasetWaveGenerator(self)
    return generator.generate_wave_data(
        output_folder=output_folder,
        force=force
    )
```

### 4.2 测试设计

**测试文件结构：**
```
tests/
├── test_wave_generator.py           # 主要测试文件
├── test_wave_integration.py         # 集成测试
└── wave_test_data/                  # 测试数据目录
    ├── mock_project/
    │   ├── config.json
    │   └── data/
    └── expected_outputs/
```

**测试用例设计：**
```python
# tests/test_wave_generator.py
class TestDatasetWaveGenerator(unittest.TestCase):
    
    def test_generate_wave_data_met(self):
        \"\"\"测试 MET 数据集的波形生成\"\"\"
    
    def test_generate_wave_data_pe(self):
        \"\"\"测试 PE 数据集的波形生成\"\"\"
    
    def test_generate_wave_data_alias(self):
        \"\"\"测试 Alias 数据集的波形生成\"\"\"
    
    def test_generate_wave_data_aliassimu(self):
        \"\"\"测试 AliasSimu 数据集的波形生成\"\"\"
    
    def test_output_folder_validation(self):
        \"\"\"测试输出目录验证\"\"\"
    
    def test_error_handling(self):
        \"\"\"测试错误处理\"\"\"
```

### 4.3 文档位置

**文档结构：**
```
documentation/
├── wave_data_generation_research_report.md    # 本报告
├── wave_data_generation_implementation_guide.md  # 实现指南
└── api/
    └── wave_generator_api.md                   # API 文档
```

## 5. 实现计划

### 5.1 实现步骤

1. **第一阶段：核心实现**
   - 创建 `core/wave_generator.py`
   - 实现 `DatasetWaveGenerator` 类
   - 在 `ProjectManager` 中添加 `generate_wave_data()` 方法

2. **第二阶段：命令行集成**
   - 在 `cli.py` 中添加 `-w` 参数支持
   - 实现参数解析和错误处理
   - 添加批量处理支持

3. **第三阶段：测试实现**
   - 创建测试文件和测试数据
   - 实现单元测试和集成测试
   - 配置 pytest 运行环境

4. **第四阶段：文档完善**
   - 编写 API 文档
   - 创建使用示例
   - 更新项目文档

### 5.2 风险评估

**技术风险：**
- **低风险**：数据集加载逻辑已经成熟
- **中风险**：新的命令行参数可能与现有参数冲突
- **低风险**：测试环境配置

**兼容性风险：**
- **低风险**：不影响现有功能
- **低风险**：使用现有的数据集接口

### 5.3 性能考虑

**优化点：**
1. **数据集缓存**：重用现有的缓存机制
2. **批量处理**：支持多项目并行生成
3. **内存管理**：大数据集的分批处理
4. **文件 I/O**：优化波形文件写入

## 6. 结论

推荐采用**方案1 - 委托模式**，因为它：

1. **最大限度重用现有代码**：完全复用数据集加载和处理逻辑
2. **保持架构一致性**：符合现有的 ProjectManager 模式
3. **易于测试和维护**：清晰的职责分离
4. **扩展性好**：便于未来添加更多 wave 相关功能

该方案能够满足所有需求，同时保持代码的简洁性和可维护性，是最优的实现选择。